import os
import re
import time
import functools
import psycopg2
import psycopg2.errors
import psycopg2.extras
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from src.infrastructure.security.hashing_service import HashingService
from src.infrastructure.storage.supabase_storage import SupabaseStorage
from src.domain.elo.model import expected_score


def _timing(func):
    """Decorator que mide y reporta el tiempo de ejecución de cada método."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start) * 1000
        print(f"[TIMING] {func.__name__}: {elapsed_ms:.0f}ms")
        return result
    return wrapper


class PostgresRepository:

    _COURSE_BLOCK_MAP = {
        # ── Bloque Universidad ────────────────────────────────────────────────
        'algebra_lineal':          'Universidad',
        'calculo_diferencial':     'Universidad',
        'calculo_integral':        'Universidad',
        'calculo_varias_variables':'Universidad',
        'ecuaciones_diferenciales':'Universidad',
        'probabilidad':            'Universidad',
        # ── Bloque Colegio ────────────────────────────────────────────────────
        'algebra_basica':          'Colegio',
        'aritmetica':              'Colegio',
        'aritmetica_basica':       'Colegio',
        'trigonometria':           'Colegio',
        'geometria':               'Colegio',
        # ── Bloque Concursos (preparación para concursos públicos) ────────────
        'DIAN':                    'Concursos',
        'SENA':                    'Concursos',
    }

    _COURSE_NAME_MAP = {
        'DIAN': 'Concurso DIAN — Gestor I',
        'SENA': 'Concurso SENA — Profesional 10',
    }

    _URL_RE = re.compile(
        r'^(?:postgresql|postgres)://([^:]+):(.+)@([^:]+):(\d+)/(.+)$'
    )

    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not defined. "
                "Set it to a PostgreSQL connection string, e.g. "
                "'postgresql://user:pass@host:5432/dbname'"
            )

        # Parsear URL una sola vez y crear pool de conexiones
        m = self._URL_RE.match(self.database_url)
        if not m:
            raise RuntimeError(f"Cannot parse DATABASE_URL: {self.database_url[:20]}…")
        user, password, host, port, dbname = m.groups()
        self._conn_kwargs = dict(
            host=host,
            port=int(port),
            dbname=dbname,
            user=user,
            password=password,
            sslmode='require',
            options='-c statement_timeout=60000',
        )
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1, maxconn=5, **self._conn_kwargs
            )
        except psycopg2.OperationalError as exc:
            raise RuntimeError(
                f"No se pudo conectar a PostgreSQL. Verifica que DATABASE_URL "
                f"use el pooler de Supabase (puerto 6543, no 5432). Error: {exc}"
            ) from exc

        self.hashing = HashingService()
        self._storage = SupabaseStorage()
        print("Iniciando init_db...")
        self.init_db()
        print("init_db OK")
        print("Iniciando _migrate_db...")
        self._migrate_db()
        print("_migrate_db OK")
        print("Iniciando _seed_admin...")
        self._seed_admin()
        print("_seed_admin OK")
        print("Iniciando _seed_demo_data...")
        self._seed_demo_data()
        print("_seed_demo_data OK")
        print("Iniciando _backfill_prob_failure...")
        self._backfill_prob_failure()
        print("_backfill_prob_failure OK")
        print("Iniciando sync_items_from_bank_folder...")
        self.sync_items_from_bank_folder()
        print("sync_items_from_bank_folder OK")
        print("Iniciando _seed_test_students...")
        self._seed_test_students()
        print("_seed_test_students OK")

    def get_connection(self):
        """Obtiene una conexión del pool. Caller debe devolverla con put_connection()."""
        conn = self._pool.getconn()
        try:
            # Verificar que la conexión siga viva; si no, el pool la reemplaza
            conn.isolation_level
        except psycopg2.OperationalError:
            self._pool.putconn(conn, close=True)
            conn = self._pool.getconn()
        return conn

    def resolve_storage_image(self, storage_url: str) -> bytes | None:
        """Download procedure image bytes from Supabase Storage.

        Handles both legacy public URLs and plain storage paths stored in
        ``procedure_submissions.storage_url``.  Returns raw bytes suitable
        for ``st.image()``, or None if unavailable.
        """
        print(f"[RESOLVE_IMG] Intentando descargar: {storage_url}")
        if not storage_url:
            print("[RESOLVE_IMG] storage_url es None/vacío")
            return None
        result = self._storage.get_file('procedimientos', storage_url)
        print(f"[RESOLVE_IMG] Resultado: {'bytes:'+str(len(result)) if result else 'None'}")
        return result

    def put_connection(self, conn):
        """Devuelve una conexión al pool para reutilización."""
        self._pool.putconn(conn)

    @_timing
    def init_db(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Tabla de grupos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    course_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
                    approved INTEGER DEFAULT 1,
                    active INTEGER DEFAULT 1,
                    group_id INTEGER,
                    rating_deviation REAL DEFAULT 350.0,
                    education_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de intentos/progreso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attempts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    item_id TEXT,
                    is_correct BOOLEAN,
                    difficulty INTEGER,
                    topic TEXT,
                    elo_after REAL,
                    prob_failure REAL,
                    expected_score REAL,
                    time_taken REAL,
                    confidence_score REAL,
                    error_type TEXT,
                    rating_deviation REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de ítems (preguntas con rating propio)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    options TEXT NOT NULL,
                    correct_option TEXT NOT NULL,
                    difficulty REAL NOT NULL,
                    rating_deviation REAL DEFAULT 350.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')

            # ── Índices para acelerar JOINs y filtros frecuentes ─────────
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON attempts(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_groups_teacher_id ON groups(teacher_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_procedure_submissions_student_id ON procedure_submissions(student_id)')

            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def get_student_procedure_scores(self, student_id):
        """Retorna notas de procedimientos validados, normalizadas a escala 0-100."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT
                    CASE
                        WHEN final_score IS NOT NULL THEN final_score
                        ELSE procedure_score * 20.0
                    END AS score,
                    submitted_at
                FROM procedure_submissions
                WHERE student_id = %s
                  AND (final_score IS NOT NULL OR procedure_score IS NOT NULL)
                ORDER BY submitted_at DESC
            ''', (student_id,))
            rows = cursor.fetchall()
            return [{'score': row['score'], 'submitted_at': row['submitted_at']} for row in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_procedure_stats_by_course(self, student_id):
        """Retorna dict {course_id: {'course_name', 'avg_score', 'count'}} con el
        promedio de notas de procedimiento agrupadas por curso del estudiante."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT i.course_id, c.name AS course_name,
                       AVG(CASE
                           WHEN ps.final_score IS NOT NULL THEN ps.final_score
                           ELSE ps.procedure_score * 20.0
                       END) AS avg_score,
                       COUNT(ps.id) AS cnt
                FROM procedure_submissions ps
                JOIN items i ON ps.item_id = i.id
                LEFT JOIN courses c ON i.course_id = c.id
                WHERE ps.student_id = %s
                  AND (ps.final_score IS NOT NULL OR ps.procedure_score IS NOT NULL)
                GROUP BY i.course_id, c.name
            ''', (student_id,))
            rows = cursor.fetchall()
            return {
                row['course_id']: {
                    'course_name': row['course_name'] or row['course_id'],
                    'avg_score': round(row['avg_score'], 2),
                    'count': row['cnt']
                }
                for row in rows if row['course_id']
            }
        finally:
            self.put_connection(conn)

    @_timing
    def get_students_procedure_summary_table(self, teacher_id):
        """Para el panel docente: lista de dicts con promedio de procedimiento
        por estudiante y curso, filtrado por los grupos del profesor."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT u.id AS student_id, u.username AS student, i.course_id,
                       c.name AS course_name,
                       AVG(ps.procedure_score) AS avg_score, COUNT(ps.id) AS count
                FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                JOIN items i ON ps.item_id = i.id
                LEFT JOIN courses c ON i.course_id = c.id
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = %s AND ps.procedure_score IS NOT NULL
                GROUP BY u.id, u.username, i.course_id, c.name
                ORDER BY u.username, i.course_id
            ''', (teacher_id,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    'student_id': row['student_id'],
                    'student': row['student'],
                    'course_id': row['course_id'],
                    'course_name': row['course_name'],
                    'avg_score': round(row['avg_score'], 2),
                    'count': row['count'],
                })
            return result
        finally:
            self.put_connection(conn)

    def _column_exists(self, cursor, table: str, column: str) -> bool:
        """Devuelve True si `column` ya existe en `table`."""
        cursor.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
            (table, column)
        )
        return cursor.fetchone() is not None

    def _add_column_if_not_exists(self, cursor, table: str, column: str, definition: str) -> None:
        """Ejecuta ALTER TABLE ADD COLUMN sólo si la columna no existe todavía."""
        if not self._column_exists(cursor, table, column):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _migrate_db(self):
        """Agrega columnas nuevas de forma segura si no existen (migración).

        Usa un advisory lock para que solo una instancia ejecute las
        migraciones a la vez (evita deadlocks en arranque paralelo de
        Streamlit).  Reintenta hasta 3 veces ante DeadlockDetected o
        QueryCanceled.
        """
        for attempt in range(3):
            conn = self.get_connection()
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # ── Advisory lock: solo una instancia migra a la vez ───────────
                cursor.execute("SELECT pg_advisory_lock(12345)")
                try:

                    # ── Timeout de 30s por statement para evitar bloqueos ──────
                    cursor.execute("SET statement_timeout = '30s'")

                    # users
                    self._add_column_if_not_exists(cursor, 'users', 'role', "TEXT DEFAULT 'student'")
                    self._add_column_if_not_exists(cursor, 'users', 'approved', "INTEGER DEFAULT 1")
                    self._add_column_if_not_exists(cursor, 'users', 'active', "INTEGER DEFAULT 1")
                    self._add_column_if_not_exists(cursor, 'users', 'group_id', "INTEGER")
                    self._add_column_if_not_exists(cursor, 'users', 'rating_deviation', "REAL DEFAULT 350.0")
                    self._add_column_if_not_exists(cursor, 'users', 'education_level', "TEXT")
                    self._add_column_if_not_exists(cursor, 'users', 'is_test_user', "INTEGER DEFAULT 0")

                    # Asegurar índices si no existen
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_teacher ON groups(teacher_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_group ON users(group_id)")

                    # Migración: vincular grupos a un curso del catálogo (course_id nullable)
                    self._add_column_if_not_exists(cursor, 'groups', 'course_id', "TEXT")

                    # Asegurar tabla de auditoría
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS audit_group_changes (
                            id SERIAL PRIMARY KEY,
                            student_id INTEGER NOT NULL,
                            old_group_id INTEGER,
                            new_group_id INTEGER,
                            admin_id INTEGER NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    # attempts
                    self._add_column_if_not_exists(cursor, 'attempts', 'prob_failure', "REAL")
                    self._add_column_if_not_exists(cursor, 'attempts', 'expected_score', "REAL")
                    self._add_column_if_not_exists(cursor, 'attempts', 'time_taken', "REAL")
                    self._add_column_if_not_exists(cursor, 'attempts', 'confidence_score', "REAL")
                    self._add_column_if_not_exists(cursor, 'attempts', 'error_type', "TEXT")
                    self._add_column_if_not_exists(cursor, 'attempts', 'rating_deviation', "REAL")

                    # Asegurar tabla items
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS items (
                            id TEXT PRIMARY KEY,
                            topic TEXT NOT NULL,
                            content TEXT NOT NULL,
                            options TEXT NOT NULL,
                            correct_option TEXT NOT NULL,
                            difficulty REAL NOT NULL,
                            rating_deviation REAL DEFAULT 350.0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    # Tabla de procedimientos enviados por estudiantes para revisión del docente
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS procedure_submissions (
                            id SERIAL PRIMARY KEY,
                            student_id INTEGER NOT NULL,
                            item_id TEXT NOT NULL,
                            item_content TEXT NOT NULL,
                            image_data BYTEA,
                            mime_type TEXT DEFAULT 'image/jpeg',
                            status TEXT DEFAULT 'pending',
                            teacher_feedback TEXT,
                            feedback_image BYTEA,
                            feedback_mime_type TEXT,
                            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            reviewed_at TIMESTAMP
                        )
                    ''')

                    # Migración de procedure_submissions: columnas añadidas en v2
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'procedure_score', "REAL")
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'procedure_image_path', "TEXT")
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'feedback_image_path', "TEXT")
                    # v3 — flujo formal de validación docente
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'ai_proposed_score', "REAL")
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'teacher_score', "REAL")
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'final_score', "REAL")
                    # v4 — delta ELO calculado al momento de la validación docente
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'elo_delta', "REAL")
                    # v5 — retroalimentación textual generada por la IA
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'ai_feedback', "TEXT")
                    # v6 — hash SHA-256 del archivo subido para detección anti-plagio
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'file_hash', "TEXT")
                    # v7 — URL de Supabase Storage (reemplaza BYTEA para nuevos registros)
                    self._add_column_if_not_exists(cursor, 'procedure_submissions', 'storage_url', "TEXT")
                    # v7b — image_data ya no es obligatorio (NULL cuando se usa Storage)
                    cursor.execute('''
                        ALTER TABLE procedure_submissions
                        ALTER COLUMN image_data DROP NOT NULL
                    ''')

                    # ── LMS: Cursos y Matrículas ─────────────────────────────────────

                    # Catálogo de cursos (uno por archivo JSON en items/bank/)
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS courses (
                            id TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            block TEXT NOT NULL CHECK (block IN ('Universidad', 'Colegio', 'Concursos')),
                            description TEXT DEFAULT ''
                        )
                    ''')

                    # Matrículas: relación N-N entre estudiantes y cursos
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS enrollments (
                            user_id INTEGER NOT NULL,
                            course_id TEXT NOT NULL,
                            group_id INTEGER,
                            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (user_id, course_id)
                        )
                    ''')

                    # Migración: asociar matrícula a un grupo (nullable)
                    self._add_column_if_not_exists(cursor, 'enrollments', 'group_id', "INTEGER")

                    # Vincular ítems a su curso (migración aditiva)
                    self._add_column_if_not_exists(cursor, 'items', 'course_id', "TEXT")
                    # T14: campo opcional para imagen/diagrama asociado a la pregunta
                    self._add_column_if_not_exists(cursor, 'items', 'image_url', "TEXT")

                    # ── Migración: ampliar CHECK constraint de courses.block ──────
                    self._migrate_courses_block_check(cursor)

                    # ── Unicidad de nombre de grupo por profesor (case-insensitive) ─
                    self._add_column_if_not_exists(cursor, 'groups', 'name_normalized', "TEXT")
                    # Rellenar valores existentes que estén NULL
                    try:
                        cursor.execute("""
                            UPDATE groups SET name_normalized = LOWER(TRIM(name))
                            WHERE name_normalized IS NULL
                        """)
                    except Exception:
                        conn.rollback()
                        # Otra instancia ya lo hizo, continuar
                    # Resolver duplicados existentes antes de crear el índice único:
                    # renombrar grupos con sufijo -DUP-{id} para desambiguar
                    cursor.execute("""
                        SELECT id, name, teacher_id, name_normalized
                        FROM groups
                        WHERE (teacher_id, name_normalized) IN (
                            SELECT teacher_id, name_normalized
                            FROM groups
                            GROUP BY teacher_id, name_normalized
                            HAVING COUNT(*) > 1
                        )
                        ORDER BY teacher_id, name_normalized, id
                    """)
                    dup_rows = cursor.fetchall()
                    # Agrupar por (teacher_id, name_normalized); conservar el primero, renombrar el resto
                    seen = set()
                    for row in dup_rows:
                        row_id = row['id']
                        row_name = row['name']
                        row_teacher = row['teacher_id']
                        row_norm = row['name_normalized']
                        key = (row_teacher, row_norm)
                        if key not in seen:
                            seen.add(key)  # el primero se conserva intacto
                            continue
                        new_name = f"{row_name}-DUP-{row_id}"
                        new_norm = new_name.strip().lower()
                        cursor.execute(
                            "UPDATE groups SET name = %s, name_normalized = %s WHERE id = %s",
                            (new_name, new_norm, row_id)
                        )
                    # Índice único: (teacher_id, nombre normalizado)
                    cursor.execute("""
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_groups_teacher_name_unique
                        ON groups(teacher_id, name_normalized)
                    """)

                    # ── Desactivar usuarios con contraseña vacía o nula ────────────
                    cursor.execute("""
                        UPDATE users SET active = 0
                        WHERE (password_hash IS NULL OR TRIM(password_hash) = '')
                          AND active = 1
                    """)

                    # ── Tabla weekly_rankings ─────────────────────────────────
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS weekly_rankings (
                            id SERIAL PRIMARY KEY,
                            week_start DATE NOT NULL,
                            week_end DATE NOT NULL,
                            group_id INTEGER NOT NULL,
                            rank INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            username TEXT NOT NULL,
                            global_elo REAL NOT NULL,
                            attempts_count INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')
                    cursor.execute('''
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_weekly_rankings_unique
                        ON weekly_rankings(week_start, group_id, user_id)
                    ''')
                    cursor.execute('''
                        CREATE INDEX IF NOT EXISTS idx_weekly_rankings_week_group
                        ON weekly_rankings(week_start, group_id)
                    ''')

                    conn.commit()

                finally:
                    cursor.execute("SELECT pg_advisory_unlock(12345)")

                return  # Migración exitosa, salir del loop de reintentos

            except (psycopg2.errors.DeadlockDetected, psycopg2.errors.QueryCanceled):
                conn.rollback()
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise
            finally:
                self.put_connection(conn)

    def _migrate_courses_block_check(self, cursor):
        """Actualiza el CHECK constraint de courses.block para incluir 'Concursos'.

        PostgreSQL soporta DROP CONSTRAINT IF EXISTS + ADD CONSTRAINT,
        así que no necesitamos el truco rename-recreate de SQLite.
        """
        cursor.execute("""
            ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_block_check
        """)
        cursor.execute("""
            ALTER TABLE courses ADD CONSTRAINT courses_block_check
            CHECK (block IN ('Universidad', 'Colegio', 'Concursos'))
        """)

    def _backfill_prob_failure(self):
        """Rellena prob_failure para intentos históricos que tienen NULL.
        Reconstruye el ELO por tópico en orden cronológico para cada estudiante."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Obtener todos los estudiantes con intentos sin prob_failure
            cursor.execute(
                "SELECT DISTINCT user_id FROM attempts WHERE prob_failure IS NULL"
            )
            user_ids = [row['user_id'] for row in cursor.fetchall()]

            for user_id in user_ids:
                # Traer TODOS los intentos del usuario en orden cronológico
                cursor.execute(
                    "SELECT id, topic, difficulty, elo_after FROM attempts "
                    "WHERE user_id = %s ORDER BY timestamp ASC, id ASC",
                    (user_id,)
                )
                attempts = cursor.fetchall()

                elo_by_topic = {}  # ELO reconstruido antes de cada intento
                for attempt in attempts:
                    attempt_id = attempt['id']
                    topic = attempt['topic']
                    difficulty = attempt['difficulty']
                    elo_after = attempt['elo_after']

                    elo_before = elo_by_topic.get(topic, 1000.0)
                    p_success = expected_score(elo_before, difficulty)
                    prob_failure = 1.0 - p_success

                    cursor.execute(
                        "UPDATE attempts SET prob_failure = %s WHERE id = %s",
                        (prob_failure, attempt_id)
                    )
                    # Avanzar ELO reconstruido
                    elo_by_topic[topic] = elo_after

            conn.commit()
        finally:
            self.put_connection(conn)

    def _seed_admin(self):
        """Crea el usuario admin desde variables de entorno si no existe."""
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            return

        admin_user = os.getenv("ADMIN_USER", "admin")
        admin_hash = self.hashing.hash_password(admin_password)

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT pg_advisory_lock(12346)")
            try:
                cursor.execute("SELECT id FROM users WHERE username = %s", (admin_user,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, role, approved) VALUES (%s, %s, 'admin', 1)",
                        (admin_user, admin_hash)
                    )
                    conn.commit()
            finally:
                cursor.execute("SELECT pg_advisory_unlock(12346)")
        finally:
            self.put_connection(conn)

    def _seed_demo_data(self):
        """Crea usuarios, grupos y matrículas demo si no existen (idempotente)."""
        demo_hash = self.hashing.hash_password("demo1234")

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT pg_advisory_lock(12347)")
            try:

                # Profesor demo
                cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, role, approved) VALUES (%s, %s, 'teacher', 1)",
                        ("profesor1", demo_hash)
                    )

                conn.commit()

                # ID del profesor para crear grupos
                cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
                profesor_id = cursor.fetchone()['id']

                # Grupos demo vinculados a cursos del catálogo
                _demo_groups = [
                    ("Grupo Demo - Cálculo", "calculo_diferencial"),
                    ("Grupo Demo - Álgebra", "algebra_basica"),
                ]
                group_ids = {}
                for g_name, g_course in _demo_groups:
                    g_norm = g_name.strip().lower()
                    cursor.execute(
                        "SELECT id FROM groups WHERE name_normalized = %s AND teacher_id = %s",
                        (g_norm, profesor_id)
                    )
                    row = cursor.fetchone()
                    if not row:
                        cursor.execute(
                            "INSERT INTO groups (name, teacher_id, course_id, name_normalized) VALUES (%s, %s, %s, %s) RETURNING id",
                            (g_name, profesor_id, g_course, g_norm)
                        )
                        conn.commit()
                        group_ids[g_course] = cursor.fetchone()['id']
                    else:
                        group_ids[g_course] = row['id']
                        # Asegurar que el grupo tenga course_id (migra grupos legacy sin curso)
                        cursor.execute(
                            "UPDATE groups SET course_id = %s WHERE id = %s AND course_id IS NULL",
                            (g_course, row['id'])
                        )

                conn.commit()

                # Estudiantes demo: cada uno en su nivel y grupo correspondiente
                _demo_students = [
                    ("estudiante1", "universidad", "calculo_diferencial"),
                    ("estudiante2", "colegio", "algebra_basica"),
                ]
                for username, edu_level, primary_course in _demo_students:
                    primary_gid = group_ids.get(primary_course)
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    row = cursor.fetchone()
                    if not row:
                        cursor.execute(
                            "INSERT INTO users (username, password_hash, role, approved, group_id, rating_deviation, education_level) "
                            "VALUES (%s, %s, 'student', 1, %s, 350.0, %s)",
                            (username, demo_hash, primary_gid, edu_level)
                        )
                    else:
                        # Asegurar que el estudiante tenga grupo y nivel asignados
                        cursor.execute(
                            "UPDATE users SET group_id = COALESCE(group_id, %s), "
                            "education_level = COALESCE(education_level, %s) "
                            "WHERE id = %s",
                            (primary_gid, edu_level, row['id'])
                        )

                conn.commit()

                # Matrículas demo: cada estudiante se inscribe en su grupo principal
                for username, _edu, primary_course in _demo_students:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    student_id = cursor.fetchone()['id']
                    g_id = group_ids.get(primary_course)
                    cursor.execute(
                        "SELECT 1 FROM enrollments WHERE user_id = %s AND course_id = %s AND group_id = %s",
                        (student_id, primary_course, g_id)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO enrollments (user_id, course_id, group_id) VALUES (%s, %s, %s)",
                            (student_id, primary_course, g_id)
                        )

                conn.commit()
            finally:
                cursor.execute("SELECT pg_advisory_unlock(12347)")
        finally:
            self.put_connection(conn)

    def _update_password_hash(self, user_id, password):
        """Actualiza el hash de un usuario al nuevo estándar Argon2id."""
        new_hash = self.hashing.hash_password(password)
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def register_user(self, username, password, role='student', group_id=None, education_level=None):
        """Registra un nuevo usuario."""
        if not password or not password.strip():
            return False, "La contraseña es obligatoria."
        if len(password.strip()) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres."
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            password_hash = self.hashing.hash_password(password)
            approved = 0 if role == 'teacher' else 1
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved, group_id, rating_deviation, education_level) "
                "VALUES (%s, %s, %s, %s, %s, 350.0, %s)",
                (username, password_hash, role, approved, group_id, education_level)
            )
            conn.commit()
            return True, "Registro exitoso."
        except psycopg2.IntegrityError:
            conn.rollback()
            return False, "Error: El nombre de usuario ya existe."
        finally:
            self.put_connection(conn)

    @_timing
    def login_user(self, username, password):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, username, role, approved, password_hash FROM users WHERE username = %s AND active = 1",
                (username,)
            )
            row = cursor.fetchone()
        finally:
            self.put_connection(conn)

        if row:
            user_id = row['id']
            uname = row['username']
            role = row['role']
            approved = row['approved']
            stored_hash = row['password_hash']

            # Rechazar cuentas con contraseña vacía o nula
            if not stored_hash or not stored_hash.strip():
                return None

            # 1. Intentar verificación con Argon2
            if stored_hash.startswith("$argon2id$"):
                try:
                    verified, new_hash = self.hashing.verify_and_update(password, stored_hash)
                    if verified:
                        if new_hash:
                            self._update_password_hash(user_id, password)
                        return (user_id, uname, role, approved)
                except Exception:
                    pass

            # 2. Si no es Argon2 o falló, intentar legado
            if self.hashing.verify_legacy_sha256(password, stored_hash):
                self._update_password_hash(user_id, password)
                return (user_id, uname, role, approved)

        return None  # Credenciales inválidas o usuario inactivo

    @_timing
    def save_attempt(self, user_id, item_id, is_correct, difficulty, topic, elo_after,
                     prob_failure=None, expected_score=None, time_taken=None,
                     confidence_score=None, error_type=None, rating_deviation=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                INSERT INTO attempts (user_id, item_id, is_correct, difficulty, topic, elo_after,
                                      prob_failure, expected_score, time_taken, confidence_score,
                                      error_type, rating_deviation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, item_id, is_correct, difficulty, topic, elo_after,
                  prob_failure, expected_score, time_taken, confidence_score,
                  error_type, rating_deviation))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def get_study_streak(self, user_id):
        """Calcula la racha de días consecutivos de estudio del estudiante."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT DISTINCT DATE(timestamp) AS d FROM attempts WHERE user_id = %s
                UNION
                SELECT DISTINCT DATE(submitted_at) AS d FROM procedure_submissions WHERE student_id = %s
                ORDER BY d DESC
            ''', (user_id, user_id))
            dates = [str(row['d']) for row in cursor.fetchall()]
        finally:
            self.put_connection(conn)

        if not dates:
            return 0

        from datetime import date, timedelta
        today = date.today()
        streak = 0
        expected = today if dates[0] == str(today) else today - timedelta(days=1)
        for d_str in dates:
            if d_str == str(expected):
                streak += 1
                expected -= timedelta(days=1)
            elif d_str < str(expected):
                break  # hueco en la racha
        return streak

    def get_weekly_ranking(self, group_id, limit=5):
        """Top estudiantes del grupo por ELO promedio, con actividad en los últimos 7 días."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                WITH active_users AS (
                    SELECT DISTINCT a.user_id
                    FROM attempts a
                    JOIN users u ON a.user_id = u.id
                    WHERE u.group_id = %s AND u.role = 'student'
                      AND a.timestamp >= NOW() - INTERVAL '7 days'
                ),
                latest_elo AS (
                    SELECT a.user_id, a.item_id, a.elo_after,
                           ROW_NUMBER() OVER (
                               PARTITION BY a.user_id, i.course_id
                               ORDER BY a.timestamp DESC
                           ) AS rn
                    FROM attempts a
                    JOIN items i ON a.item_id = i.id
                    WHERE a.user_id IN (SELECT user_id FROM active_users)
                ),
                user_elo AS (
                    SELECT le.user_id,
                           ROUND(AVG(le.elo_after)::numeric, 0) AS global_elo
                    FROM latest_elo le
                    WHERE le.rn = 1
                    GROUP BY le.user_id
                ),
                week_attempts AS (
                    SELECT a.user_id, COUNT(*) AS attempts_this_week
                    FROM attempts a
                    WHERE a.user_id IN (SELECT user_id FROM active_users)
                      AND a.timestamp >= NOW() - INTERVAL '7 days'
                    GROUP BY a.user_id
                )
                SELECT ue.user_id, u.username, ue.global_elo, wa.attempts_this_week
                FROM user_elo ue
                JOIN users u ON ue.user_id = u.id
                JOIN week_attempts wa ON ue.user_id = wa.user_id
                ORDER BY ue.global_elo DESC
                LIMIT %s
            ''', (group_id, limit))
            rows = cursor.fetchall()
            return [
                {'user_id': row['user_id'], 'username': row['username'],
                 'global_elo': float(row['global_elo']),
                 'rank': idx + 1, 'attempts_this_week': row['attempts_this_week']}
                for idx, row in enumerate(rows)
            ]
        finally:
            self.put_connection(conn)

    def save_weekly_ranking(self, group_id):
        """Guarda el top 5 actual en weekly_rankings. Idempotente por semana+grupo+user."""
        from datetime import date, timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # lunes
        week_end = week_start + timedelta(days=6)             # domingo
        ranking = self.get_weekly_ranking(group_id, 5)
        if not ranking:
            return
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            for r in ranking:
                cursor.execute('''
                    INSERT INTO weekly_rankings
                        (week_start, week_end, group_id, rank, user_id, username, global_elo, attempts_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (week_start, group_id, user_id) DO NOTHING
                ''', (str(week_start), str(week_end), group_id, r['rank'],
                      r['user_id'], r['username'], r['global_elo'], r['attempts_this_week']))
            conn.commit()
        finally:
            self.put_connection(conn)

    def get_ranking_history(self, group_id, weeks=4):
        """Historial de rankings de las últimas N semanas."""
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(weeks=weeks)
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT week_start, week_end, rank, username, global_elo, attempts_count
                FROM weekly_rankings
                WHERE group_id = %s AND week_start >= %s
                ORDER BY week_start DESC, rank ASC
            ''', (group_id, str(cutoff)))
            rows = cursor.fetchall()
            return [
                {'week_start': str(row['week_start']), 'week_end': str(row['week_end']),
                 'rank': row['rank'], 'username': row['username'],
                 'global_elo': float(row['global_elo']), 'attempts_count': row['attempts_count']}
                for row in rows
            ]
        finally:
            self.put_connection(conn)

    @_timing
    def get_total_attempts_count(self, user_id):
        """Retorna el número total de intentos de un estudiante."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT COUNT(*) AS cnt FROM attempts WHERE user_id = %s", (user_id,))
            count = cursor.fetchone()['cnt']
            return count
        finally:
            self.put_connection(conn)

    @_timing
    def get_latest_attempts(self, user_id, limit=20):
        """Retorna los últimos N intentos con el resultado real y el esperado."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT is_correct, expected_score, prob_failure
                FROM attempts
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            ''', (user_id, limit))
            rows = cursor.fetchall()
        finally:
            self.put_connection(conn)

        results = []
        for row in rows:
            is_correct = row['is_correct']
            expected = row['expected_score']
            prob_fail = row['prob_failure']
            actual = 1.0 if is_correct else 0.0
            if expected is None and prob_fail is not None:
                expected = 1.0 - prob_fail
            elif expected is None:
                expected = 0.5
            results.append({"actual": actual, "expected": expected})
        return results

    @_timing
    def get_user_history_elo(self, user_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT elo_after FROM attempts WHERE user_id = %s ORDER BY timestamp ASC", (user_id,))
            rows = cursor.fetchall()
            return [r['elo_after'] for r in rows] if rows else [1000]
        finally:
            self.put_connection(conn)

    @_timing
    def get_latest_elo(self, user_id):
        history = self.get_user_history_elo(user_id)
        return history[-1]

    @_timing
    def get_attempts_for_ai(self, user_id, limit=20):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT topic, difficulty, is_correct, timestamp
                FROM attempts
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            ''', (user_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_answered_item_ids(self, user_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT DISTINCT item_id FROM attempts WHERE user_id = %s", (user_id,))
            rows = cursor.fetchall()
            return [r['item_id'] for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_latest_elo_by_topic(self, user_id):
        """Devuelve {topic: (elo_actual, rd_actual)} incluyendo ajustes de procedimientos."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 1. ELO base desde los intentos de preguntas
            cursor.execute(
                "SELECT topic, elo_after, rating_deviation "
                "FROM attempts WHERE user_id = %s ORDER BY timestamp ASC",
                (user_id,)
            )
            elo_map = {}
            for row in cursor.fetchall():
                topic = row['topic']
                elo = row['elo_after']
                rd = row['rating_deviation']
                elo_map[topic] = (elo, rd if rd is not None else 350.0)

            # 2. Sumar deltas ELO de procedimientos validados por el docente
            cursor.execute('''
                SELECT i.topic, SUM(ps.elo_delta) AS total_delta
                FROM procedure_submissions ps
                JOIN items i ON ps.item_id = i.id
                WHERE ps.student_id = %s
                  AND ps.status = 'VALIDATED_BY_TEACHER'
                  AND ps.elo_delta IS NOT NULL
                GROUP BY i.topic
            ''', (user_id,))
            for row in cursor.fetchall():
                topic = row['topic']
                total_delta = row['total_delta']
                if topic in elo_map:
                    base_elo, rd = elo_map[topic]
                    elo_map[topic] = (round(base_elo + total_delta, 2), rd)
                else:
                    elo_map[topic] = (round(1000.0 + total_delta, 2), 350.0)

            return elo_map
        finally:
            self.put_connection(conn)

    @_timing
    def get_user_history_full(self, user_id):
        """Devuelve historial completo para gráficas."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT timestamp, topic, elo_after FROM attempts WHERE user_id = %s ORDER BY timestamp ASC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [{'timestamp': r['timestamp'], 'topic': r['topic'], 'elo': r['elo_after']} for r in rows]
        finally:
            self.put_connection(conn)

    # ─── Métodos para ADMIN ─────────────────────────────────────────────────────

    @_timing
    def get_pending_teachers(self):
        """Retorna lista de teachers pendientes de aprobación."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, username, created_at FROM users WHERE role = 'teacher' AND approved = 0 ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            return [{'id': r['id'], 'username': r['username'], 'created_at': r['created_at']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_approved_teachers(self):
        """Retorna lista de teachers aprobados y activos."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, username, created_at FROM users WHERE role = 'teacher' AND approved = 1 AND active = 1 ORDER BY username ASC"
            )
            rows = cursor.fetchall()
            return [{'id': r['id'], 'username': r['username'], 'created_at': r['created_at']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def deactivate_user(self, user_id):
        """Da de baja (desactiva) a un usuario por id."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("UPDATE users SET active = 0 WHERE id = %s", (user_id,))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def reactivate_user(self, user_id):
        """Reactiva un usuario dado de baja, conservando todo su progreso."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("UPDATE users SET active = 1 WHERE id = %s", (user_id,))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def approve_teacher(self, user_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("UPDATE users SET approved = 1 WHERE id = %s", (user_id,))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def reject_teacher(self, user_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("DELETE FROM users WHERE id = %s AND role = 'teacher'", (user_id,))
            conn.commit()
        finally:
            self.put_connection(conn)

    # ─── Métodos para TEACHER ────────────────────────────────────────────────────

    @_timing
    def get_all_students(self):
        """Retorna lista de todos los estudiantes activos."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, username, created_at FROM users WHERE role = 'student' AND active = 1 ORDER BY username ASC"
            )
            rows = cursor.fetchall()
            return [{'id': r['id'], 'username': r['username'], 'created_at': r['created_at']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_all_students_admin(self):
        """Retorna TODOS los estudiantes (activos e inactivos) con su grupo para el panel admin."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT u.id, u.username, u.active, u.created_at, g.name as group_name
                FROM users u
                LEFT JOIN groups g ON u.group_id = g.id
                WHERE u.role = 'student'
                ORDER BY u.username ASC
            ''')
            rows = cursor.fetchall()
            return [{'id': r['id'], 'username': r['username'], 'active': r['active'],
                     'created_at': r['created_at'], 'group_name': r['group_name']} for r in rows]
        finally:
            self.put_connection(conn)

    # ─── Gestión de GRUPOS ────────────────────────────────────────────────────────

    @_timing
    def create_group(self, name, teacher_id, course_id=None):
        """Crea un nuevo grupo para un profesor, opcionalmente vinculado a un curso."""
        name_normalized = name.strip().lower()
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "INSERT INTO groups (name, teacher_id, course_id, name_normalized) VALUES (%s, %s, %s, %s)",
                (name, teacher_id, course_id, name_normalized)
            )
            conn.commit()
            return True, f"Grupo '{name}' creado exitosamente."
        except psycopg2.IntegrityError:
            conn.rollback()
            return False, "Ya existe un grupo con ese nombre."
        finally:
            self.put_connection(conn)

    @_timing
    def get_groups_by_teacher(self, teacher_id):
        """Lista grupos de un profesor con el nombre del curso vinculado (JOIN)."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT g.id, g.name, g.course_id, COALESCE(c.name, '—') AS course_name, g.created_at
                FROM groups g
                LEFT JOIN courses c ON g.course_id = c.id
                WHERE g.teacher_id = %s
                ORDER BY g.name ASC
            ''', (teacher_id,))
            rows = cursor.fetchall()
            return [
                {'id': r['id'], 'name': r['name'], 'course_id': r['course_id'],
                 'course_name': r['course_name'], 'created_at': r['created_at']}
                for r in rows
            ]
        finally:
            self.put_connection(conn)

    @_timing
    def get_all_groups(self):
        """Lista todos los grupos disponibles (para el registro de estudiantes)."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT g.id, g.name, u.username as teacher_name
                FROM groups g
                JOIN users u ON g.teacher_id = u.id
                ORDER BY g.name ASC
            ''')
            rows = cursor.fetchall()
            return [{'id': r['id'], 'name': r['name'], 'teacher_name': r['teacher_name']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def delete_group(self, group_id, admin_id):
        """Elimina un grupo (solo admin). Desvincula estudiantes y matrículas del grupo."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Validar que el ejecutor sea admin
            cursor.execute("SELECT role FROM users WHERE id = %s AND active = 1", (admin_id,))
            res = cursor.fetchone()
            if not res or res['role'] != 'admin':
                return False, "Error de seguridad: Solo un administrador puede eliminar grupos."

            # Verificar que el grupo existe
            cursor.execute("SELECT name FROM groups WHERE id = %s", (group_id,))
            grp = cursor.fetchone()
            if not grp:
                return False, "El grupo no existe."

            group_name = grp['name']

            # Desvincular estudiantes del grupo (conservar sus datos)
            cursor.execute("UPDATE users SET group_id = NULL WHERE group_id = %s", (group_id,))

            # Desvincular matrículas del grupo
            cursor.execute("UPDATE enrollments SET group_id = NULL WHERE group_id = %s", (group_id,))

            # Eliminar el grupo
            cursor.execute("DELETE FROM groups WHERE id = %s", (group_id,))

            conn.commit()
            return True, f"Grupo '{group_name}' eliminado. Los estudiantes fueron desvinculados."
        except Exception as e:
            conn.rollback()
            return False, f"Error al eliminar grupo: {e}"
        finally:
            self.put_connection(conn)

    @_timing
    def get_students_by_teacher(self, teacher_id):
        """Retorna estudiantes vinculados al profesor vía grupo primario O matrículas."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT u.id, u.username, u.created_at, g.name AS group_name, g.id AS group_id,
                       g.course_id, COALESCE(c.name, '—') AS course_name,
                       COALESCE(c.block, '—') AS course_block
                FROM users u
                JOIN groups g ON u.group_id = g.id
                LEFT JOIN courses c ON g.course_id = c.id
                WHERE g.teacher_id = %s AND u.active = 1

                UNION

                SELECT u.id, u.username, u.created_at, g.name AS group_name, g.id AS group_id,
                       g.course_id, COALESCE(c.name, '—') AS course_name,
                       COALESCE(c.block, '—') AS course_block
                FROM enrollments e
                JOIN users u ON e.user_id = u.id
                JOIN groups g ON e.group_id = g.id
                LEFT JOIN courses c ON g.course_id = c.id
                WHERE g.teacher_id = %s AND u.active = 1

                ORDER BY username ASC
            ''', (teacher_id, teacher_id))
            rows = cursor.fetchall()
            return [{
                'id': r['id'], 'username': r['username'], 'created_at': r['created_at'],
                'group_name': r['group_name'], 'group_id': r['group_id'],
                'course_id': r['course_id'], 'course_name': r['course_name'],
                'course_block': r['course_block']
            } for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_students_by_group(self, group_id, teacher_id):
        """Retorna estudiantes de un grupo específico, validando que sea del profesor."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT u.id, u.username, u.created_at
                FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE u.group_id = %s AND g.teacher_id = %s AND u.active = 1
                ORDER BY u.username ASC
            ''', (group_id, teacher_id))
            rows = cursor.fetchall()
            return [{'id': r['id'], 'username': r['username'], 'created_at': r['created_at']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_student_attempts_detail(self, student_id):
        """Historial detallado de intentos de un estudiante (para el teacher)."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT id, topic, difficulty, is_correct, elo_after, rating_deviation,
                       prob_failure, timestamp, time_taken
                FROM attempts
                WHERE user_id = %s
                ORDER BY timestamp ASC
            ''', (student_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self.put_connection(conn)

    # ─── Gestión de SEGURIDAD (Admin) ───────────────────────────────────────────

    @_timing
    def change_student_group(self, student_id, new_group_id, admin_id, allow_null=False):
        """Reasigna a un estudiante a un nuevo grupo con validaciones y auditoría."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 1. Validar que el ejecutor sea ADMIN
            cursor.execute("SELECT role FROM users WHERE id = %s AND active = 1", (admin_id,))
            res = cursor.fetchone()
            if not res or res['role'] != 'admin':
                return False, "Error de seguridad: Solo un administrador puede realizar esta acción."

            # 2. Validar que el objetivo sea ESTUDIANTE y obtener su grupo actual
            cursor.execute("SELECT role, group_id FROM users WHERE id = %s AND active = 1", (student_id,))
            res = cursor.fetchone()
            if not res:
                return False, "Error: El estudiante no existe o está inactivo."

            target_role = res['role']
            old_group_id = res['group_id']
            if target_role != 'student':
                return False, f"Error: No se puede cambiar el grupo de un {target_role}."

            # 3. Validar redundancia
            if old_group_id == new_group_id:
                return False, "Información: El estudiante ya pertenece al grupo seleccionado."

            # 4. Validar existencia del nuevo grupo
            if new_group_id is not None:
                cursor.execute("SELECT id FROM groups WHERE id = %s", (new_group_id,))
                if not cursor.fetchone():
                    return False, "Error: El grupo destino no existe."
            elif not allow_null:
                return False, "Error: No se permite dejar al estudiante sin grupo."

            # 5. Ejecutar cambio y auditoría en una transacción
            cursor.execute("UPDATE users SET group_id = %s WHERE id = %s", (new_group_id, student_id))

            cursor.execute('''
                INSERT INTO audit_group_changes (student_id, old_group_id, new_group_id, admin_id)
                VALUES (%s, %s, %s, %s)
            ''', (student_id, old_group_id, new_group_id, admin_id))

            conn.commit()
            return True, "Reasignación completada y auditada correctamente."

        except Exception as e:
            conn.rollback()
            return False, f"Error crítico en la base de datos: {str(e)}"
        finally:
            self.put_connection(conn)

    # ─── Gestión de CURSOS y MATRÍCULAS ─────────────────────────────────────────

    @_timing
    def sync_items_from_bank_folder(self, bank_dir='items/bank'):
        """Escanea items/bank/*.json, registra cada archivo como curso y sincroniza
        sus ítems sin sobreescribir ratings ELO ya calculados.

        Optimización: máximo 2 SELECTs + 2 INSERTs en total.
        Carga IDs existentes en un set, filtra localmente y hace
        un solo executemany() para courses y otro para items.
        """
        import json
        import glob as _glob

        if not os.path.isdir(bank_dir):
            return

        json_files = sorted(_glob.glob(os.path.join(bank_dir, '*.json')))
        if not json_files:
            return

        # Cargar todos los JSONs en memoria
        courses_data = []
        for filepath in json_files:
            course_id = os.path.splitext(os.path.basename(filepath))[0]
            with open(filepath, 'r', encoding='utf-8') as f:
                items_list = json.load(f)
            if items_list:
                courses_data.append((course_id, items_list))

        if not courses_data:
            return

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT pg_advisory_lock(12348)")
            try:

                # 1. Obtener todos los IDs existentes en una sola query
                cursor.execute("SELECT id FROM items")
                existing_item_ids = {row['id'] for row in cursor.fetchall()}

                cursor.execute("SELECT id FROM courses")
                existing_course_ids = {row['id'] for row in cursor.fetchall()}

                # 2. Construir listas de courses e items nuevos
                new_courses_params = []
                new_items_params = []

                for course_id, items_list in courses_data:
                    course_name = self._COURSE_NAME_MAP.get(course_id) or items_list[0].get('topic', course_id)
                    block = self._COURSE_BLOCK_MAP.get(course_id, 'Universidad')

                    if course_id not in existing_course_ids:
                        new_courses_params.append(
                            (course_id, course_name, block, f"Curso de {course_name}")
                        )

                    for item in items_list:
                        if item['id'] not in existing_item_ids:
                            new_items_params.append((
                                item['id'],
                                item['topic'],
                                item['content'],
                                json.dumps(item['options']),
                                item['correct_option'],
                                item['difficulty'],
                                course_id,
                                item.get('image_url') or item.get('image_path'),
                            ))

                # 3. Si no hay nada nuevo, salir
                if not new_courses_params and not new_items_params:
                    return  # finally blocks devuelven conexión y liberan lock

                # 4. Insertar todo de una sola vez
                if new_courses_params:
                    cursor.executemany(
                        "INSERT INTO courses (id, name, block, description) "
                        "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                        new_courses_params
                    )

                if new_items_params:
                    cursor.executemany('''
                        INSERT INTO items
                            (id, topic, content, options, correct_option, difficulty, rating_deviation, course_id, image_url)
                        VALUES (%s, %s, %s, %s, %s, %s, 350.0, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    ''', new_items_params)

                conn.commit()
            finally:
                cursor.execute("SELECT pg_advisory_unlock(12348)")
        finally:
            self.put_connection(conn)

    def _seed_test_students(self):
        """Crea estudiantes de prueba permanentes (inline PostgreSQL version)."""
        from src.domain.entities import LEVEL_COLEGIO, LEVEL_UNIVERSIDAD, LEVEL_TO_BLOCK

        _TEST_PASSWORD = "test1234"
        _TEST_STUDENTS = [
            ("estudiante_colegio_1", LEVEL_COLEGIO),
            ("estudiante_colegio_2", LEVEL_COLEGIO),
            ("estudiante_colegio_3", LEVEL_COLEGIO),
            ("estudiante_universidad_1", LEVEL_UNIVERSIDAD),
            ("estudiante_universidad_2", LEVEL_UNIVERSIDAD),
        ]

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT pg_advisory_lock(12349)")
            try:

                # ── Salida rápida: si los 5 ya existen, no hay nada que hacer ────
                placeholders = ','.join(['%s'] * len(_TEST_STUDENTS))
                cursor.execute(
                    "SELECT username FROM users WHERE username IN ({})".format(placeholders),
                    [s[0] for s in _TEST_STUDENTS],
                )
                existing = {row['username'] for row in cursor.fetchall()}
                students_to_create = [(u, l) for u, l in _TEST_STUDENTS if u not in existing]

                if not students_to_create:
                    return  # Todos existen — finally blocks liberan lock y conexión

                # Solo computar hash si hay estudiantes nuevos
                password_hash = self.hashing.hash_password(_TEST_PASSWORD)

                # Necesitamos un profesor para crear grupos; usar profesor1
                cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
                row = cursor.fetchone()
                if not row:
                    return  # Sin profesor demo no podemos crear grupos
                profesor_id = row['id']

                # Grupos de prueba por nivel
                _level_groups = {
                    LEVEL_COLEGIO: ("Grupo Prueba - Colegio", None),
                    LEVEL_UNIVERSIDAD: ("Grupo Prueba - Universidad", None),
                }
                for level, (g_name, _) in list(_level_groups.items()):
                    g_norm = g_name.strip().lower()
                    cursor.execute(
                        "SELECT id FROM groups WHERE name_normalized = %s AND teacher_id = %s",
                        (g_norm, profesor_id),
                    )
                    row = cursor.fetchone()
                    if not row:
                        block = LEVEL_TO_BLOCK[level]
                        cursor.execute(
                            "SELECT id FROM courses WHERE block = %s ORDER BY name ASC LIMIT 1",
                            (block,),
                        )
                        first_course = cursor.fetchone()
                        course_id = first_course['id'] if first_course else None
                        cursor.execute(
                            "INSERT INTO groups (name, teacher_id, course_id, name_normalized) VALUES (%s, %s, %s, %s) RETURNING id",
                            (g_name, profesor_id, course_id, g_norm),
                        )
                        conn.commit()
                        new_row = cursor.fetchone()
                        _level_groups[level] = (g_name, new_row['id'])
                    else:
                        _level_groups[level] = (g_name, row['id'])

                # Crear SOLO estudiantes que no existen
                for username, edu_level in students_to_create:
                    group_id = _level_groups[edu_level][1]
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, role, approved, group_id, "
                        "rating_deviation, education_level, is_test_user) "
                        "VALUES (%s, %s, 'student', 1, %s, 350.0, %s, 1)",
                        (username, password_hash, group_id, edu_level),
                    )
                conn.commit()

                # Matricular estudiantes nuevos en TODOS los cursos de su nivel
                for username, edu_level in students_to_create:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    student_id = cursor.fetchone()['id']
                    block = LEVEL_TO_BLOCK[edu_level]
                    group_id = _level_groups[edu_level][1]

                    cursor.execute(
                        "SELECT id FROM courses WHERE block = %s",
                        (block,),
                    )
                    courses = cursor.fetchall()
                    for course_row in courses:
                        cursor.execute(
                            "INSERT INTO enrollments (user_id, course_id, group_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                            (student_id, course_row['id'], group_id),
                        )

                conn.commit()
            finally:
                cursor.execute("SELECT pg_advisory_unlock(12349)")
        finally:
            self.put_connection(conn)

    @_timing
    def get_available_courses_by_level(self, level: str):
        """Retorna los cursos disponibles filtrados ESTRICTAMENTE por nivel educativo."""
        from src.domain.entities import LEVEL_TO_BLOCK, LEVEL_UNIVERSIDAD
        _block = LEVEL_TO_BLOCK.get(level.lower(), LEVEL_TO_BLOCK[LEVEL_UNIVERSIDAD])
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, name, block, description FROM courses WHERE block = %s ORDER BY name ASC",
                (_block,)
            )
            rows = cursor.fetchall()
            return [{'id': r['id'], 'name': r['name'], 'block': r['block'], 'description': r['description']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_courses(self, block=None):
        """Devuelve todos los cursos, opcionalmente filtrados por bloque."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            if block:
                cursor.execute(
                    "SELECT id, name, block, description FROM courses WHERE block = %s ORDER BY name ASC",
                    (block,)
                )
            else:
                cursor.execute("SELECT id, name, block, description FROM courses ORDER BY block ASC, name ASC")
            rows = cursor.fetchall()
            return [{'id': r['id'], 'name': r['name'], 'block': r['block'], 'description': r['description']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_available_groups_for_course(self, course_id):
        """Retorna los grupos activos vinculados a un curso específico."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT g.id, g.name, u.username AS teacher_name
                FROM groups g
                JOIN users u ON g.teacher_id = u.id
                WHERE g.course_id = %s AND u.active = 1 AND u.approved = 1
                ORDER BY g.name ASC
            ''', (course_id,))
            rows = cursor.fetchall()
            return [{'id': r['id'], 'name': r['name'], 'teacher_name': r['teacher_name']} for r in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def enroll_user(self, user_id, course_id, group_id=None):
        """Matricula a un usuario en un curso. Idempotente."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "INSERT INTO enrollments (user_id, course_id, group_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (user_id, course_id, group_id)
            )
            if group_id is not None:
                cursor.execute(
                    "UPDATE enrollments SET group_id = %s WHERE user_id = %s AND course_id = %s",
                    (group_id, user_id, course_id)
                )
                cursor.execute(
                    "UPDATE users SET group_id = %s WHERE id = %s",
                    (group_id, user_id)
                )
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def unenroll_user(self, user_id, course_id):
        """Elimina la matrícula de un usuario en un curso."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "DELETE FROM enrollments WHERE user_id = %s AND course_id = %s",
                (user_id, course_id)
            )
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def get_user_enrollments(self, user_id):
        """Devuelve los cursos en los que está matriculado el usuario."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT c.id, c.name, c.block, c.description,
                       e.group_id, COALESCE(g.name, '') AS group_name
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN groups g ON e.group_id = g.id
                WHERE e.user_id = %s
                ORDER BY c.name ASC
            ''', (user_id,))
            rows = cursor.fetchall()
            return [
                {'id': r['id'], 'name': r['name'], 'block': r['block'], 'description': r['description'],
                 'group_id': r['group_id'], 'group_name': r['group_name']}
                for r in rows
            ]
        finally:
            self.put_connection(conn)

    @_timing
    def get_enrolled_topics(self, user_id):
        """Retorna el conjunto de tópicos relevantes para el filtrado de la tabla ELO."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            # Fuente 1: cursos matriculados → tópicos de sus ítems
            cursor.execute('''
                SELECT DISTINCT i.topic
                FROM enrollments e
                JOIN items i ON i.course_id = e.course_id
                WHERE e.user_id = %s AND i.topic IS NOT NULL
            ''', (user_id,))
            topics = {row['topic'] for row in cursor.fetchall()}
            # Fuente 2: tópicos de ítems con procedimientos enviados
            cursor.execute('''
                SELECT DISTINCT i.topic
                FROM procedure_submissions ps
                JOIN items i ON ps.item_id = i.id
                WHERE ps.student_id = %s AND i.topic IS NOT NULL
            ''', (user_id,))
            topics |= {row['topic'] for row in cursor.fetchall()}
            return topics
        finally:
            self.put_connection(conn)

    @_timing
    def set_education_level(self, user_id, level):
        """Guarda el nivel educativo del usuario."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("UPDATE users SET education_level = %s WHERE id = %s", (level, user_id))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def get_education_level(self, user_id):
        """Retorna el education_level del usuario, o None si no existe."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT education_level FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            return row['education_level'] if row else None
        finally:
            self.put_connection(conn)

    # ─── Gestión de ÍTEMS (ELO Dinámico) ────────────────────────────────────────

    @_timing
    def sync_items_from_json(self, items_list):
        """Sincroniza el banco de preguntas JSON con la DB. No sobreescribe ratings actuales."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            import json

            for item in items_list:
                cursor.execute("SELECT id FROM items WHERE id = %s", (item['id'],))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO items (id, topic, content, options, correct_option, difficulty, rating_deviation)
                        VALUES (%s, %s, %s, %s, %s, %s, 350.0)
                    ''', (
                        item['id'],
                        item['topic'],
                        item['content'],
                        json.dumps(item['options']),
                        item['correct_option'],
                        item['difficulty']
                    ))
                else:
                    cursor.execute('''
                        UPDATE items
                        SET content = %s, options = %s, correct_option = %s, topic = %s
                        WHERE id = %s
                    ''', (
                        item['content'],
                        json.dumps(item['options']),
                        item['correct_option'],
                        item['topic'],
                        item['id']
                    ))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def get_items_from_db(self, topic=None, course_id=None):
        """Obtiene ítems desde la base de datos."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            import json

            if course_id:
                cursor.execute(
                    "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url FROM items WHERE course_id = %s",
                    (course_id,)
                )
            elif topic and topic != "Todos":
                cursor.execute(
                    "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url FROM items WHERE topic = %s",
                    (topic,)
                )
            else:
                cursor.execute(
                    "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url FROM items"
                )

            rows = cursor.fetchall()

            items = []
            for r in rows:
                items.append({
                    'id': r['id'],
                    'topic': r['topic'],
                    'content': r['content'],
                    'options': json.loads(r['options']),
                    'correct_option': r['correct_option'],
                    'difficulty': r['difficulty'],
                    'rating_deviation': r['rating_deviation'],
                    'image_url': r['image_url'],
                })
            return items
        finally:
            self.put_connection(conn)

    @_timing
    def update_item_rating(self, item_id, student_rating, actual_score, k_item=32.0):
        """Actualiza la dificultad (rating) del ítem de forma simétrica."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT difficulty, rating_deviation FROM items WHERE id = %s", (item_id,))
            res = cursor.fetchone()
            if not res:
                return

            current_diff = res['difficulty']
            current_rd = res['rating_deviation']

            # Lógica ELO inversa para el ítem
            item_score = 1.0 - actual_score

            p_student_wins = expected_score(student_rating, current_diff)
            p_item_wins = 1.0 - p_student_wins

            delta = k_item * (item_score - p_item_wins)
            new_diff = current_diff + delta

            cursor.execute("UPDATE items SET difficulty = %s WHERE id = %s", (new_diff, item_id))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def create_session(self, user_id):
        import secrets
        from datetime import datetime, timedelta, timezone
        token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
                (token, user_id, expires_at.isoformat())
            )
            conn.commit()
        finally:
            self.put_connection(conn)
        return token

    @_timing
    def validate_session(self, token):
        from datetime import datetime, timezone
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT user_id, expires_at FROM sessions WHERE token = %s",
                (token,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            user_id = row['user_id']
            expires_at = row['expires_at']
            # Handle both string and datetime objects
            if isinstance(expires_at, str):
                exp_dt = datetime.fromisoformat(expires_at)
            else:
                exp_dt = expires_at
            # Ensure timezone-aware comparison
            if exp_dt.tzinfo is None:
                from datetime import timezone as tz
                exp_dt = exp_dt.replace(tzinfo=tz.utc)
            if exp_dt < datetime.now(timezone.utc):
                cursor.execute("DELETE FROM sessions WHERE token = %s", (token,))
                conn.commit()
                return None
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
        finally:
            self.put_connection(conn)

    @_timing
    def delete_session(self, token):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("DELETE FROM sessions WHERE token = %s", (token,))
            conn.commit()
        finally:
            self.put_connection(conn)

    # ── Procedimientos para revisión del docente ──────────────────────────────

    @_timing
    def check_file_hash_duplicate(self, item_id, student_id, file_hash):
        """Verifica si el hash SHA-256 de un archivo ya fue registrado por OTRO estudiante
        para la misma pregunta."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 1 FROM procedure_submissions
                WHERE item_id = %s AND file_hash = %s AND student_id != %s
                LIMIT 1
            ''', (item_id, file_hash, student_id))
            found = cursor.fetchone() is not None
            return found
        finally:
            self.put_connection(conn)

    @_timing
    def save_procedure_submission(self, student_id, item_id, item_content, image_data,
                                  mime_type='image/jpeg', file_hash=None):
        """Guarda o reemplaza el procedimiento enviado por el estudiante.

        Si Supabase Storage está disponible, sube el archivo al bucket
        'procedimientos' y almacena la URL.  image_data se guarda como NULL
        en la BD para nuevos registros (ahorra ~200 KB de BYTEA por fila).
        Fallback: disco local + BYTEA si Storage no está disponible.
        """
        import time as _time
        print(f"[SAVE_PROC] Recibido: student_id={student_id}, item_id={item_id}, "
              f"image_data={'bytes:'+str(len(image_data)) if image_data else 'None'}, mime_type={mime_type}")
        ext = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}.get(mime_type, 'jpg')

        # ── Intentar subir a Supabase Storage ────────────────────────────
        storage_path = f"{student_id}/{item_id}/{file_hash or int(_time.time())}.{ext}"
        if self._storage.available:
            print(f"[STORAGE] Subiendo archivo a Supabase Storage...")
        else:
            print("[STORAGE] WARNING: SUPABASE_URL/KEY no definidas, usando BYTEA fallback")
        storage_url = self._storage.upload_file(
            'procedimientos', storage_path, image_data, mime_type,
        )
        print(f"[SAVE_PROC] storage_url resultado={storage_url}")

        # ── BYTEA backup + disco local fallback ────────────────────────
        img_path = None
        bytea_value = None
        if image_data:
            # Always keep BYTEA as backup regardless of storage_url
            bytea_value = psycopg2.Binary(image_data)
        if not storage_url:
            if image_data:
                os.makedirs(os.path.join('data', 'uploads', 'procedures'), exist_ok=True)
                img_filename = f"{student_id}_{item_id}_{int(_time.time())}.{ext}"
                img_path = os.path.join('data', 'uploads', 'procedures', img_filename)
                with open(img_path, 'wb') as _f:
                    _f.write(image_data)
            else:
                print("[SAVE_PROC] ERROR: storage_url=None AND image_data=None, no hay datos para guardar")

        print(f"[SAVE_PROC] Guardando en DB: storage_url={storage_url}, "
              f"image_data={'bytes:'+str(len(image_data)) if image_data else 'None'}")

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                'SELECT id FROM procedure_submissions WHERE student_id=%s AND item_id=%s',
                (student_id, item_id),
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute('''
                    UPDATE procedure_submissions
                    SET image_data=%s, mime_type=%s, procedure_image_path=%s, file_hash=%s,
                        storage_url=%s,
                        status=CASE
                            WHEN ai_proposed_score IS NOT NULL THEN 'PENDING_TEACHER_VALIDATION'
                            ELSE 'pending'
                        END,
                        teacher_feedback=NULL,
                        feedback_image=NULL, feedback_image_path=NULL,
                        procedure_score=NULL, teacher_score=NULL, final_score=NULL,
                        submitted_at=CURRENT_TIMESTAMP, reviewed_at=NULL
                    WHERE student_id=%s AND item_id=%s
                ''', (bytea_value, mime_type, img_path, file_hash, storage_url,
                      student_id, item_id))
            else:
                cursor.execute('''
                    INSERT INTO procedure_submissions
                        (student_id, item_id, item_content, image_data, mime_type,
                         procedure_image_path, file_hash, storage_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (student_id, item_id, item_content, bytea_value,
                      mime_type, img_path, file_hash, storage_url))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def save_ai_proposed_score(self, student_id: int, item_id: str, ai_score: float,
                               ai_feedback: str = None):
        """Guarda la puntuación propuesta por la IA y actualiza el status."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                UPDATE procedure_submissions
                SET ai_proposed_score = %s,
                    ai_feedback = %s,
                    status = 'PENDING_TEACHER_VALIDATION'
                WHERE student_id = %s AND item_id = %s
            ''', (ai_score, ai_feedback, student_id, item_id))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def get_student_submission(self, student_id, item_id):
        """Retorna la entrega del estudiante para una pregunta, o None."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT id, status, teacher_feedback, feedback_image,
                       feedback_mime_type, submitted_at, reviewed_at,
                       procedure_score, feedback_image_path,
                       ai_proposed_score, teacher_score, final_score,
                       storage_url
                FROM procedure_submissions
                WHERE student_id=%s AND item_id=%s
            ''', (student_id, item_id))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            self.put_connection(conn)

    @_timing
    def get_reviewed_submission_ids(self, student_id):
        """Retorna los IDs de entregas que ya tienen retroalimentación."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT id FROM procedure_submissions
                WHERE student_id = %s AND reviewed_at IS NOT NULL
            ''', (student_id,))
            ids = {row['id'] for row in cursor.fetchall()}
            return ids
        finally:
            self.put_connection(conn)

    @_timing
    def get_student_feedback_history(self, student_id):
        """Historial completo de entregas del estudiante para el Centro de Feedback."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT ps.id, ps.item_id,
                       SUBSTR(ps.item_content, 1, 80) AS item_short,
                       ps.ai_proposed_score, ps.ai_feedback,
                       ps.final_score, ps.teacher_score,
                       ps.procedure_score,
                       ps.teacher_feedback,
                       ps.status, ps.submitted_at, ps.reviewed_at,
                       ps.procedure_image_path, ps.feedback_image_path,
                       ps.storage_url
                FROM procedure_submissions ps
                WHERE ps.student_id = %s
                ORDER BY ps.submitted_at DESC
            ''', (student_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_pending_submissions_count(self, teacher_id):
        """Cuenta las entregas pendientes de revisión del docente."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT COUNT(*) AS cnt FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = %s
                  AND ps.status IN ('pending', 'PENDING_TEACHER_VALIDATION')
            ''', (teacher_id,))
            count = cursor.fetchone()['cnt']
            return count
        finally:
            self.put_connection(conn)

    @_timing
    def get_pending_submissions_for_teacher(self, teacher_id):
        """Retorna todas las entregas pendientes de los estudiantes del docente."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT ps.id, ps.student_id, u.username AS student_name,
                       ps.item_id, ps.item_content, ps.mime_type,
                       ps.submitted_at, ps.procedure_image_path,
                       ps.status, ps.ai_proposed_score, ps.ai_feedback,
                       ps.storage_url,
                       CASE WHEN ps.storage_url IS NULL THEN ps.image_data
                            ELSE NULL END AS image_data
                FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = %s
                  AND ps.status IN ('pending', 'PENDING_TEACHER_VALIDATION')
                ORDER BY ps.submitted_at DESC
            ''', (teacher_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self.put_connection(conn)

    @_timing
    def get_student_elo_summary(self, student_id):
        """ELO actual por tópico, ELO global, total de intentos y precisión reciente."""
        elo_by_topic = self.get_latest_elo_by_topic(student_id)
        global_elo = (
            sum(e for e, _ in elo_by_topic.values()) / len(elo_by_topic)
            if elo_by_topic else 1000.0
        )
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT COUNT(*) AS cnt FROM attempts WHERE user_id = %s", (student_id,))
            total = cursor.fetchone()['cnt']
            cursor.execute(
                "SELECT is_correct FROM attempts WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10",
                (student_id,)
            )
            recent = cursor.fetchall()
        finally:
            self.put_connection(conn)
        recent_acc = sum(1 for r in recent if r['is_correct']) / len(recent) if recent else 0.0
        return {
            'elo_by_topic': elo_by_topic,
            'global_elo': round(global_elo, 1),
            'attempts_count': total,
            'recent_accuracy': recent_acc,
        }

    @_timing
    def validate_procedure_submission(self, submission_id: int,
                                      teacher_score: float, feedback: str = ""):
        """Valida la calificación de un procedimiento y establece la nota final oficial."""
        elo_delta = round((teacher_score - 50.0) * 0.2, 4)

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                UPDATE procedure_submissions
                SET teacher_score    = %s,
                    final_score      = %s,
                    teacher_feedback = %s,
                    elo_delta        = %s,
                    status           = 'VALIDATED_BY_TEACHER',
                    reviewed_at      = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (teacher_score, teacher_score, feedback or None, elo_delta, submission_id))
            conn.commit()
        finally:
            self.put_connection(conn)

    @_timing
    def save_teacher_feedback(self, submission_id, feedback_text,
                              feedback_image=None, feedback_mime_type=None,
                              procedure_score=None):
        """Guarda la retroalimentación del docente y marca la entrega como revisada."""
        feedback_image_path = None
        if feedback_image:
            import time as _time
            ext = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}.get(feedback_mime_type, 'jpg')
            os.makedirs(os.path.join('data', 'uploads', 'feedback'), exist_ok=True)
            fb_filename = f"feedback_{submission_id}_{int(_time.time())}.{ext}"
            feedback_image_path = os.path.join('data', 'uploads', 'feedback', fb_filename)
            with open(feedback_image_path, 'wb') as _f:
                _f.write(feedback_image)

        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                UPDATE procedure_submissions
                SET teacher_feedback=%s, feedback_image=%s, feedback_mime_type=%s,
                    procedure_score=%s, feedback_image_path=%s,
                    status='reviewed', reviewed_at=CURRENT_TIMESTAMP
                WHERE id=%s
            ''', (feedback_text, psycopg2.Binary(feedback_image) if feedback_image else None,
                  feedback_mime_type, procedure_score, feedback_image_path, submission_id))
            conn.commit()
        finally:
            self.put_connection(conn)
