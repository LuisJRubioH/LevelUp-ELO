import os
import sqlite3
import logging
from src.infrastructure.security.hashing_service import HashingService

logger = logging.getLogger(__name__)


# TODO: reemplazar SQLite por DB externa (PostgreSQL, etc.) en producción
class SQLiteRepository:
    # Ruta fija — garantiza que todos los datos persistan entre ejecuciones.
    _DEFAULT_DB_PATH = os.path.join("data", "elo_database.db")

    def __init__(self, db_name=None):
        self.db_name = db_name or os.environ.get("DB_PATH", self._DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        self.hashing = HashingService()
        self.init_db()
        self._migrate_db()
        self._seed_admin()
        self._seed_demo_data()
        self._backfill_prob_failure()
        self.sync_items_from_bank_folder()
        self._seed_test_students()

    def get_connection(self):
        return sqlite3.connect(self.db_name, timeout=10.0)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de grupos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                course_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        """
        )

        # Tabla de usuarios
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
                approved INTEGER DEFAULT 1,
                active INTEGER DEFAULT 1,
                group_id INTEGER,
                rating_deviation REAL DEFAULT 350.0,
                education_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE SET NULL
            )
        """
        )

        # Tabla de intentos/progreso
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
        )

        # Tabla de ítems (preguntas con rating propio)
        cursor.execute(
            """
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
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
        )

        conn.commit()
        conn.close()

    def get_student_procedure_scores(self, student_id):
        """Retorna notas de procedimientos validados, normalizadas a escala 0-100.

        Reglas de normalización (retrocompatibilidad):
          - final_score (0-100)   → usado directamente.
          - procedure_score (0-5) → multiplicado × 20 para equiparar escala.
          - ai_proposed_score     → NUNCA incluido (no es nota oficial).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                CASE
                    WHEN final_score IS NOT NULL THEN final_score
                    ELSE procedure_score * 20.0
                END AS score,
                submitted_at
            FROM procedure_submissions
            WHERE student_id = ?
              AND (final_score IS NOT NULL OR procedure_score IS NOT NULL)
            ORDER BY submitted_at DESC
        """,
            (student_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"score": row[0], "submitted_at": row[1]} for row in rows]

    def get_procedure_stats_by_course(self, student_id):
        """Retorna dict {course_id: {'course_name', 'avg_score', 'count'}} con el
        promedio de notas de procedimiento agrupadas por curso del estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.course_id, c.name,
                   AVG(CASE
                       WHEN ps.final_score IS NOT NULL THEN ps.final_score
                       ELSE ps.procedure_score * 20.0
                   END),
                   COUNT(ps.id)
            FROM procedure_submissions ps
            JOIN items i ON ps.item_id = i.id
            LEFT JOIN courses c ON i.course_id = c.id
            WHERE ps.student_id = ?
              AND (ps.final_score IS NOT NULL OR ps.procedure_score IS NOT NULL)
            GROUP BY i.course_id
        """,
            (student_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return {
            row[0]: {
                "course_name": row[1] or row[0],
                "avg_score": round(row[2], 2),
                "count": row[3],
            }
            for row in rows
            if row[0]
        }

    def get_students_procedure_summary_table(self, teacher_id):
        """Para el panel docente: lista de dicts con promedio de procedimiento
        por estudiante y curso, filtrado por los grupos del profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.username, i.course_id, c.name,
                   AVG(ps.procedure_score), COUNT(ps.id)
            FROM procedure_submissions ps
            JOIN users u ON ps.student_id = u.id
            JOIN items i ON ps.item_id = i.id
            LEFT JOIN courses c ON i.course_id = c.id
            JOIN groups g ON u.group_id = g.id
            WHERE g.teacher_id = ? AND ps.procedure_score IS NOT NULL
            GROUP BY u.id, i.course_id
            ORDER BY u.username, i.course_id
        """,
            (teacher_id,),
        )
        cols = ["student_id", "student", "course_id", "course_name", "avg_score", "count"]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        for row in rows:
            row["avg_score"] = round(row["avg_score"], 2)
        return rows

    def _column_exists(self, cursor, table: str, column: str) -> bool:
        """Devuelve True si `column` ya existe en `table`."""
        cursor.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cursor.fetchall())

    def _add_column_if_not_exists(self, cursor, table: str, column: str, definition: str) -> None:
        """Ejecuta ALTER TABLE ADD COLUMN sólo si la columna no existe todavía."""
        if not self._column_exists(cursor, table, column):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _migrate_db(self):
        """Agrega columnas nuevas de forma segura si no existen (migración)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # users
        self._add_column_if_not_exists(cursor, "users", "role", "TEXT DEFAULT 'student'")
        self._add_column_if_not_exists(cursor, "users", "approved", "INTEGER DEFAULT 1")
        self._add_column_if_not_exists(cursor, "users", "active", "INTEGER DEFAULT 1")
        self._add_column_if_not_exists(cursor, "users", "group_id", "INTEGER")
        self._add_column_if_not_exists(cursor, "users", "rating_deviation", "REAL DEFAULT 350.0")
        # Sin DEFAULT: los usuarios existentes quedan NULL → pasan por onboarding la primera vez
        self._add_column_if_not_exists(cursor, "users", "education_level", "TEXT")
        # Flag para estudiantes de prueba (protección contra eliminación accidental)
        self._add_column_if_not_exists(cursor, "users", "is_test_user", "INTEGER DEFAULT 0")
        # Grado escolar (solo para education_level = 'semillero'; valores '6'–'11')
        self._add_column_if_not_exists(cursor, "users", "grade", "TEXT")

        # Asegurar índices si no existen
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_teacher ON groups(teacher_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_group ON users(group_id)")

        # Migración: vincular grupos a un curso del catálogo (course_id nullable)
        self._add_column_if_not_exists(cursor, "groups", "course_id", "TEXT REFERENCES courses(id)")

        # Asegurar tabla de auditoría
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_group_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                old_group_id INTEGER,
                new_group_id INTEGER,
                admin_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(admin_id) REFERENCES users(id)
            )
        """
        )

        # attempts
        self._add_column_if_not_exists(cursor, "attempts", "prob_failure", "REAL")
        self._add_column_if_not_exists(cursor, "attempts", "expected_score", "REAL")
        self._add_column_if_not_exists(cursor, "attempts", "time_taken", "REAL")
        self._add_column_if_not_exists(cursor, "attempts", "confidence_score", "REAL")
        self._add_column_if_not_exists(cursor, "attempts", "error_type", "TEXT")
        self._add_column_if_not_exists(cursor, "attempts", "rating_deviation", "REAL")

        # Asegurar tabla items
        cursor.execute(
            """
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
        """
        )

        # Tabla de procedimientos enviados por estudiantes para revisión del docente
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS procedure_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                item_content TEXT NOT NULL,
                image_data BLOB NOT NULL,
                mime_type TEXT DEFAULT 'image/jpeg',
                status TEXT DEFAULT 'pending',
                teacher_feedback TEXT,
                feedback_image BLOB,
                feedback_mime_type TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES users(id)
            )
        """
        )

        # Migración de procedure_submissions: columnas añadidas en v2
        self._add_column_if_not_exists(cursor, "procedure_submissions", "procedure_score", "REAL")
        self._add_column_if_not_exists(
            cursor, "procedure_submissions", "procedure_image_path", "TEXT"
        )
        self._add_column_if_not_exists(
            cursor, "procedure_submissions", "feedback_image_path", "TEXT"
        )
        # v3 — flujo formal de validación docente (Task 3)
        # INVARIANTE: ai_proposed_score NUNCA toca ELO; solo final_score puede hacerlo.
        self._add_column_if_not_exists(cursor, "procedure_submissions", "ai_proposed_score", "REAL")
        self._add_column_if_not_exists(cursor, "procedure_submissions", "teacher_score", "REAL")
        self._add_column_if_not_exists(cursor, "procedure_submissions", "final_score", "REAL")
        # v4 — delta ELO calculado al momento de la validación docente (Task 5)
        # Formula: elo_delta = (final_score - 50) * 0.2  (nunca desde ai_proposed_score)
        self._add_column_if_not_exists(cursor, "procedure_submissions", "elo_delta", "REAL")
        # v5 — retroalimentación textual generada por la IA (evaluacion_global del modelo)
        self._add_column_if_not_exists(cursor, "procedure_submissions", "ai_feedback", "TEXT")
        # v6 — hash SHA-256 del archivo subido para detección anti-plagio (T7)
        self._add_column_if_not_exists(cursor, "procedure_submissions", "file_hash", "TEXT")

        # ── LMS: Cursos y Matrículas ─────────────────────────────────────────────

        # Catálogo de cursos (uno por archivo JSON en items/bank/)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                block TEXT NOT NULL CHECK (block IN ('Universidad', 'Colegio', 'Concursos', 'Semillero')),
                description TEXT DEFAULT ''
            )
        """
        )

        # Matrículas: relación N-N entre estudiantes y cursos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                group_id INTEGER,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, course_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE SET NULL
            )
        """
        )

        # Migración: asociar matrícula a un grupo (nullable — inscripciones previas
        # quedan con group_id = NULL, el sistema las tolera sin riesgo).
        self._add_column_if_not_exists(
            cursor, "enrollments", "group_id", "INTEGER REFERENCES groups(id) ON DELETE SET NULL"
        )

        # Vincular ítems a su curso (migración aditiva)
        self._add_column_if_not_exists(cursor, "items", "course_id", "TEXT REFERENCES courses(id)")
        # T14: campo opcional para imagen/diagrama asociado a la pregunta
        self._add_column_if_not_exists(cursor, "items", "image_url", "TEXT")
        # Tags de taxonomía (JSON array): dimensión cognitiva, general y específica
        self._add_column_if_not_exists(cursor, "items", "tags", "TEXT")

        # ── Migración: ampliar CHECK constraint de courses.block ──────────────
        # SQLite no soporta ALTER TABLE para modificar constraints; hay que
        # recrear la tabla. Solo se ejecuta si el CHECK actual no permite
        # 'Concursos' (detección: intentar INSERT + ROLLBACK).
        self._migrate_courses_block_check(cursor)

        # ── Unicidad de nombre de grupo por profesor (case-insensitive) ────
        # Columna auxiliar para el índice único normalizado
        self._add_column_if_not_exists(cursor, "groups", "name_normalized", "TEXT")
        # Rellenar valores existentes que estén NULL
        cursor.execute(
            """
            UPDATE groups SET name_normalized = LOWER(TRIM(name))
            WHERE name_normalized IS NULL
        """
        )
        # Resolver duplicados existentes antes de crear el índice único:
        # renombrar grupos con sufijo -DUP-{id} para desambiguar
        cursor.execute(
            """
            SELECT id, name, teacher_id, name_normalized
            FROM groups
            WHERE (teacher_id, name_normalized) IN (
                SELECT teacher_id, name_normalized
                FROM groups
                GROUP BY teacher_id, name_normalized
                HAVING COUNT(*) > 1
            )
            ORDER BY teacher_id, name_normalized, id
        """
        )
        dup_rows = cursor.fetchall()
        # Agrupar por (teacher_id, name_normalized); conservar el primero, renombrar el resto
        seen = set()
        for row_id, row_name, row_teacher, row_norm in dup_rows:
            key = (row_teacher, row_norm)
            if key not in seen:
                seen.add(key)  # el primero se conserva intacto
                continue
            new_name = f"{row_name}-DUP-{row_id}"
            new_norm = new_name.strip().lower()
            cursor.execute(
                "UPDATE groups SET name = ?, name_normalized = ? WHERE id = ?",
                (new_name, new_norm, row_id),
            )
        # Índice único: (teacher_id, nombre normalizado)
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_groups_teacher_name_unique
            ON groups(teacher_id, name_normalized)
        """
        )

        # Código de invitación por grupo (opcional, generado por el docente)
        self._add_column_if_not_exists(cursor, "groups", "invite_code", "TEXT")
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_groups_invite_code
            ON groups(invite_code) WHERE invite_code IS NOT NULL
        """
        )

        # ── Desactivar usuarios con contraseña vacía o nula ────────────────
        # Conserva sus datos históricos pero impide login hasta que un admin
        # los reactive y se les asigne una contraseña válida.
        cursor.execute(
            """
            UPDATE users SET active = 0
            WHERE (password_hash IS NULL OR TRIM(password_hash) = '')
              AND active = 1
        """
        )

        # ── Tabla problem_reports (reportes técnicos de usuarios) ────
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS problem_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
        )

        # ── Tabla weekly_rankings ─────────────────────────────────────
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weekly_rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start DATE NOT NULL,
                week_end DATE NOT NULL,
                group_id INTEGER NOT NULL,
                rank INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                global_elo REAL NOT NULL,
                attempts_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_weekly_rankings_unique
            ON weekly_rankings(week_start, group_id, user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_weekly_rankings_week_group
            ON weekly_rankings(week_start, group_id)
        """
        )

        # ── Tabla katia_interactions (registro de interacciones con KatIA) ──
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS katia_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id TEXT,
                item_id TEXT,
                item_topic TEXT,
                student_message TEXT NOT NULL,
                katia_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_katia_interactions_user
            ON katia_interactions(user_id)
        """
        )

        conn.commit()
        conn.close()

    def _migrate_courses_block_check(self, cursor):
        """Recrea la tabla courses si el CHECK constraint no incluye todos los bloques.

        SQLite no permite ALTER CHECK, así que se usa rename-recreate-copy.
        Es idempotente: si el CHECK ya es correcto, no hace nada.
        """
        # Detectar si 'Semillero' ya es aceptado (implica que el CHECK está actualizado)
        try:
            cursor.execute(
                "INSERT INTO courses (id, name, block, description) "
                "VALUES ('__check_probe__', '__probe__', 'Semillero', '')"
            )
            # Si llegó aquí, el INSERT fue aceptado → CHECK ya lo permite
            cursor.execute("DELETE FROM courses WHERE id = '__check_probe__'")
            return  # No hace falta migrar
        except Exception:
            # CHECK constraint rechazó 'Semillero' → necesitamos migrar
            pass

        # 1. Renombrar tabla actual
        cursor.execute("ALTER TABLE courses RENAME TO _courses_old")

        # 2. Crear tabla nueva con CHECK ampliado (incluye Semillero)
        cursor.execute(
            """
            CREATE TABLE courses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                block TEXT NOT NULL CHECK (block IN ('Universidad', 'Colegio', 'Concursos', 'Semillero')),
                description TEXT DEFAULT ''
            )
        """
        )

        # 3. Copiar datos existentes
        cursor.execute(
            """
            INSERT INTO courses (id, name, block, description)
            SELECT id, name, block, description FROM _courses_old
        """
        )

        # 4. Eliminar tabla antigua
        cursor.execute("DROP TABLE _courses_old")

    def _backfill_prob_failure(self):
        """Rellena prob_failure para intentos históricos que tienen NULL.
        Reconstruye el ELO por tópico en orden cronológico para cada estudiante."""
        from src.domain.elo.model import expected_score

        conn = self.get_connection()
        cursor = conn.cursor()

        # Obtener todos los estudiantes con intentos sin prob_failure
        cursor.execute("SELECT DISTINCT user_id FROM attempts WHERE prob_failure IS NULL")
        user_ids = [row[0] for row in cursor.fetchall()]

        for user_id in user_ids:
            # Traer TODOS los intentos del usuario en orden cronológico
            cursor.execute(
                "SELECT id, topic, difficulty, elo_after FROM attempts "
                "WHERE user_id = ? ORDER BY timestamp ASC, id ASC",
                (user_id,),
            )
            attempts = cursor.fetchall()

            elo_by_topic = {}  # ELO reconstruido antes de cada intento
            for attempt_id, topic, difficulty, elo_after in attempts:
                elo_before = elo_by_topic.get(topic, 1000.0)
                p_success = expected_score(elo_before, difficulty)
                prob_failure = 1.0 - p_success

                cursor.execute(
                    "UPDATE attempts SET prob_failure = ? WHERE id = ?", (prob_failure, attempt_id)
                )
                # Avanzar ELO reconstruido
                elo_by_topic[topic] = elo_after

        conn.commit()
        conn.close()

    def _seed_admin(self):
        """Crea el usuario admin desde variables de entorno si no existe.

        Requiere ADMIN_PASSWORD definida en el entorno; si no existe, no se crea
        ningún admin por defecto. El nombre de usuario se toma de ADMIN_USER
        (por defecto 'admin').
        """
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            return

        admin_user = os.getenv("ADMIN_USER", "admin")
        # Argon2 es lento por diseño; calcular el hash antes de abrir la conexión
        # evita "database is locked" en entornos con alta concurrencia.
        admin_hash = self.hashing.hash_password(admin_password)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (admin_user,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, 'admin', 1)",
                (admin_user, admin_hash),
            )
            conn.commit()
        conn.close()

    def _seed_demo_data(self):
        """Crea usuarios, grupos y matrículas demo si no existen (idempotente).

        Credenciales de prueba:
        - Profesor: profesor1 / demo1234
        - Estudiante universidad: estudiante1 / demo1234 (Cálculo Diferencial)
        - Estudiante colegio: estudiante2 / demo1234 (Álgebra Básica)

        Se crean dos grupos vinculados a cursos reales con cada estudiante
        matriculado en el grupo de su nivel para iniciar estudio inmediatamente.
        """
        # Pre-computar hashes ANTES de abrir la conexión:
        # Argon2 es lento por diseño; calcularlos con la DB abierta provoca "database is locked".
        demo_hash = self.hashing.hash_password("demo1234")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Profesor demo
        cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, 'teacher', 1)",
                ("profesor1", demo_hash),
            )

        conn.commit()

        # ID del profesor para crear grupos
        cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
        profesor_id = cursor.fetchone()[0]

        # Grupos demo vinculados a cursos del catálogo
        _demo_groups = [
            ("Grupo Demo - Cálculo", "calculo_diferencial"),
            ("Grupo Demo - Álgebra", "algebra_basica"),
        ]
        group_ids = {}
        for g_name, g_course in _demo_groups:
            g_norm = g_name.strip().lower()
            cursor.execute(
                "SELECT id FROM groups WHERE name_normalized = ? AND teacher_id = ?",
                (g_norm, profesor_id),
            )
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO groups (name, teacher_id, course_id, name_normalized) VALUES (?, ?, ?, ?)",
                    (g_name, profesor_id, g_course, g_norm),
                )
                conn.commit()
                group_ids[g_course] = cursor.lastrowid
            else:
                group_ids[g_course] = row[0]
                # Asegurar que el grupo tenga course_id (migra grupos legacy sin curso)
                cursor.execute(
                    "UPDATE groups SET course_id = ? WHERE id = ? AND course_id IS NULL",
                    (g_course, row[0]),
                )

        conn.commit()

        # Estudiantes demo: cada uno en su nivel y grupo correspondiente
        _demo_students = [
            # (username, nivel_educativo, course_id del grupo principal)
            ("estudiante1", "universidad", "calculo_diferencial"),
            ("estudiante2", "colegio", "algebra_basica"),
        ]
        for username, edu_level, primary_course in _demo_students:
            primary_gid = group_ids.get(primary_course)
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, approved, group_id, rating_deviation, education_level) "
                    "VALUES (?, ?, 'student', 1, ?, 350.0, ?)",
                    (username, demo_hash, primary_gid, edu_level),
                )
            else:
                # Asegurar que el estudiante tenga grupo y nivel asignados
                cursor.execute(
                    "UPDATE users SET group_id = COALESCE(group_id, ?), "
                    "education_level = COALESCE(education_level, ?) "
                    "WHERE id = ?",
                    (primary_gid, edu_level, row[0]),
                )

        conn.commit()

        # Matrículas demo: cada estudiante se inscribe en su grupo principal
        for username, _edu, primary_course in _demo_students:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            student_id = cursor.fetchone()[0]
            g_id = group_ids.get(primary_course)
            cursor.execute(
                "SELECT 1 FROM enrollments WHERE user_id = ? AND course_id = ? AND group_id = ?",
                (student_id, primary_course, g_id),
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO enrollments (user_id, course_id, group_id) VALUES (?, ?, ?)",
                    (student_id, primary_course, g_id),
                )

        conn.commit()
        conn.close()

    def _update_password_hash(self, user_id, password):
        """Actualiza el hash de un usuario al nuevo estándar Argon2id."""
        new_hash = self.hashing.hash_password(password)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        conn.commit()
        conn.close()

    def register_user(
        self, username, password, role="student", group_id=None, education_level=None, grade=None
    ):
        """Registra un nuevo usuario.

        Para estudiantes, `group_id` es opcional en el momento del registro:
        el estudiante elige grupo al matricularse en un curso (catálogo).
        `education_level` determina qué catálogo de cursos podrá ver.
        `grade` solo aplica cuando education_level = 'semillero' ('6'–'11').
        """
        # Validación backend de contraseña (no confiar solo en la UI)
        if not password or not password.strip():
            return False, "La contraseña es obligatoria."
        if len(password.strip()) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres."
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hashing.hash_password(password)
            # Teachers necesitan aprobación; students y admin se aprueban solos
            approved = 0 if role == "teacher" else 1
            _grade = grade if education_level == "semillero" else None
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved, group_id, rating_deviation, education_level, grade) "
                "VALUES (?, ?, ?, ?, ?, 350.0, ?, ?)",
                (username, password_hash, role, approved, group_id, education_level, _grade),
            )
            conn.commit()
            return True, "Registro exitoso."
        except sqlite3.IntegrityError:
            return False, "Error: El nombre de usuario ya existe."
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Buscamos al usuario por nombre para verificar su hash
        cursor.execute(
            "SELECT id, username, role, approved, password_hash FROM users WHERE username = ? AND active = 1",
            (username,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            user_id, uname, role, approved, stored_hash = row

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

    def save_attempt(
        self,
        user_id,
        item_id,
        is_correct,
        difficulty,
        topic,
        elo_after,
        prob_failure=None,
        expected_score=None,
        time_taken=None,
        confidence_score=None,
        error_type=None,
        rating_deviation=None,
    ):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attempts (user_id, item_id, is_correct, difficulty, topic, elo_after, prob_failure, expected_score, time_taken, confidence_score, error_type, rating_deviation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                item_id,
                is_correct,
                difficulty,
                topic,
                elo_after,
                prob_failure,
                expected_score,
                time_taken,
                confidence_score,
                error_type,
                rating_deviation,
            ),
        )
        conn.commit()
        conn.close()

    def save_answer_transaction(
        self,
        user_id: int,
        item_id: str,
        item_difficulty_new: float,
        item_rd_new: float,
        attempt_data: dict,
    ) -> None:
        """
        Persiste el resultado de una respuesta de forma atómica.
        Actualiza la dificultad del ítem y registra el intento en una
        sola transacción: ambas operaciones ocurren o ninguna.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE items SET difficulty = ?, rating_deviation = ? WHERE id = ?",
                (item_difficulty_new, item_rd_new, item_id),
            )
            cursor.execute(
                """INSERT INTO attempts
                   (user_id, item_id, is_correct, difficulty, topic, elo_after,
                    prob_failure, expected_score, time_taken, confidence_score,
                    error_type, rating_deviation)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    item_id,
                    1 if attempt_data["is_correct"] else 0,
                    attempt_data.get("difficulty"),
                    attempt_data.get("topic"),
                    attempt_data["elo_after"],
                    attempt_data.get("prob_failure"),
                    attempt_data.get("expected_score"),
                    attempt_data.get("time_taken"),
                    attempt_data.get("confidence_score"),
                    attempt_data.get("error_type"),
                    attempt_data.get("rating_deviation"),
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_study_streak(self, user_id, course_id=None):
        """Calcula la racha de días consecutivos de estudio del estudiante.

        Si course_id se proporciona, solo cuenta los días con actividad en ese
        curso específico (racha independiente por materia). Sin course_id,
        cuenta cualquier actividad (racha global).
        Retorna el número de días consecutivos (0 si no hay actividad reciente).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        if course_id:
            cursor.execute(
                """
                SELECT DISTINCT DATE(a.timestamp) AS d
                FROM attempts a
                JOIN items i ON i.id = a.item_id
                WHERE a.user_id = ? AND i.course_id = ?
                ORDER BY d DESC
            """,
                (user_id, course_id),
            )
        else:
            cursor.execute(
                """
                SELECT DISTINCT DATE(timestamp) AS d FROM attempts WHERE user_id = ?
                UNION
                SELECT DISTINCT DATE(submitted_at) AS d FROM procedure_submissions WHERE student_id = ?
                ORDER BY d DESC
            """,
                (user_id, user_id),
            )
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()

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
                break
        return streak

    def save_problem_report(self, user_id: int, description: str) -> None:
        """Guarda un reporte de problema técnico enviado por un usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO problem_reports (user_id, description) VALUES (?, ?)",
            (user_id, description),
        )
        conn.commit()
        conn.close()

    def get_problem_reports(self, status: str = None) -> list:
        """Devuelve reportes de problemas. Con status='pending' solo los pendientes."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute(
                """
                SELECT pr.id, pr.user_id, u.username, pr.description, pr.status, pr.created_at
                FROM problem_reports pr
                JOIN users u ON u.id = pr.user_id
                WHERE pr.status = ?
                ORDER BY pr.created_at DESC
            """,
                (status,),
            )
        else:
            cursor.execute(
                """
                SELECT pr.id, pr.user_id, u.username, pr.description, pr.status, pr.created_at
                FROM problem_reports pr
                JOIN users u ON u.id = pr.user_id
                ORDER BY pr.created_at DESC
            """
            )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "user_id": r[1],
                "username": r[2],
                "description": r[3],
                "status": r[4],
                "created_at": r[5],
            }
            for r in rows
        ]

    def mark_problem_resolved(self, report_id: int) -> None:
        """Marca un reporte de problema como resuelto."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE problem_reports SET status = 'resolved' WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()

    # ── KatIA interactions ──────────────────────────────────────────────

    def save_katia_interaction(
        self,
        user_id: int,
        course_id: str,
        item_id: str,
        item_topic: str,
        student_message: str,
        katia_response: str = None,
    ) -> None:
        """Registra una interacción del estudiante con el chat socrático de KatIA."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO katia_interactions (user_id, course_id, item_id, item_topic, "
            "student_message, katia_response) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, course_id, item_id, item_topic, student_message, katia_response),
        )
        conn.commit()
        conn.close()

    def get_katia_interactions(self, user_id: int, limit: int = 200) -> list:
        """Retorna las interacciones de un estudiante con KatIA."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ki.id, ki.course_id, c.name AS course_name,
                   ki.item_id, ki.item_topic, ki.student_message,
                   ki.katia_response, ki.created_at
            FROM katia_interactions ki
            LEFT JOIN courses c ON c.id = ki.course_id
            WHERE ki.user_id = ?
            ORDER BY ki.created_at DESC
            LIMIT ?
        """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "course_id": r[1],
                "course_name": r[2],
                "item_id": r[3],
                "item_topic": r[4],
                "student_message": r[5],
                "katia_response": r[6],
                "created_at": r[7],
            }
            for r in rows
        ]

    def export_teacher_katia_interactions(self, teacher_id: int, group_id: int = None) -> list:
        """Exporta interacciones de KatIA de los estudiantes del docente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        _filter = ""
        _params = [teacher_id]
        if group_id:
            _filter = "AND u.group_id = ?"
            _params.append(group_id)
        cursor.execute(
            f"""
            SELECT u.id AS student_id, u.username, g.name AS group_name,
                   ki.course_id, c.name AS course_name,
                   ki.item_topic, ki.student_message,
                   ki.katia_response, ki.created_at
            FROM katia_interactions ki
            JOIN users u ON u.id = ki.user_id
            JOIN groups g ON g.id = u.group_id
            LEFT JOIN courses c ON c.id = ki.course_id
            WHERE g.teacher_id = ? {_filter}
            ORDER BY ki.created_at DESC
        """,
            _params,
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "student_id": r[0],
                "username": r[1],
                "group_name": r[2],
                "course_id": r[3],
                "course_name": r[4],
                "item_topic": r[5],
                "student_message": r[6],
                "katia_response": r[7],
                "created_at": r[8],
            }
            for r in rows
        ]

    def get_weekly_ranking(self, group_id, limit=5):
        """Top estudiantes del grupo por ELO promedio, con actividad en los últimos 7 días."""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Subconsulta: último elo_after por (usuario, tópico) para usuarios del grupo
        # con al menos 1 intento en los últimos 7 días.
        cursor.execute(
            """
            WITH active_users AS (
                SELECT DISTINCT a.user_id
                FROM attempts a
                JOIN users u ON a.user_id = u.id
                WHERE u.group_id = ? AND u.role = 'student'
                  AND a.timestamp >= datetime('now', '-7 days')
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
                       ROUND(AVG(le.elo_after), 0) AS global_elo
                FROM latest_elo le
                WHERE le.rn = 1
                GROUP BY le.user_id
            ),
            week_attempts AS (
                SELECT a.user_id, COUNT(*) AS attempts_this_week
                FROM attempts a
                WHERE a.user_id IN (SELECT user_id FROM active_users)
                  AND a.timestamp >= datetime('now', '-7 days')
                GROUP BY a.user_id
            )
            SELECT ue.user_id, u.username, ue.global_elo, wa.attempts_this_week
            FROM user_elo ue
            JOIN users u ON ue.user_id = u.id
            JOIN week_attempts wa ON ue.user_id = wa.user_id
            ORDER BY ue.global_elo DESC
            LIMIT ?
        """,
            (group_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "user_id": row[0],
                "username": row[1],
                "global_elo": row[2],
                "rank": idx + 1,
                "attempts_this_week": row[3],
            }
            for idx, row in enumerate(rows)
        ]

    def save_weekly_ranking(self, group_id):
        """Guarda el top 5 actual en weekly_rankings. Idempotente por semana+grupo+user."""
        from datetime import date, timedelta

        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # lunes
        week_end = week_start + timedelta(days=6)  # domingo
        ranking = self.get_weekly_ranking(group_id, 5)
        if not ranking:
            return
        conn = self.get_connection()
        cursor = conn.cursor()
        for r in ranking:
            cursor.execute(
                """
                INSERT OR IGNORE INTO weekly_rankings
                    (week_start, week_end, group_id, rank, user_id, username, global_elo, attempts_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(week_start),
                    str(week_end),
                    group_id,
                    r["rank"],
                    r["user_id"],
                    r["username"],
                    r["global_elo"],
                    r["attempts_this_week"],
                ),
            )
        conn.commit()
        conn.close()

    def get_ranking_history(self, group_id, weeks=4):
        """Historial de rankings de las últimas N semanas."""
        from datetime import date, timedelta

        cutoff = date.today() - timedelta(weeks=weeks)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT week_start, week_end, rank, username, global_elo, attempts_count
            FROM weekly_rankings
            WHERE group_id = ? AND week_start >= ?
            ORDER BY week_start DESC, rank ASC
        """,
            (group_id, str(cutoff)),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "week_start": row[0],
                "week_end": row[1],
                "rank": row[2],
                "username": row[3],
                "global_elo": row[4],
                "attempts_count": row[5],
            }
            for row in rows
        ]

    def get_global_ranking(self, limit=5, education_level=None, grade=None):
        """Top estudiantes globales por ELO promedio, con actividad en los últimos 7 días."""
        conn = self.get_connection()
        cursor = conn.cursor()
        _level_filter = ""
        _params = []
        if education_level:
            _level_filter += "AND u.education_level = ?"
            _params.append(education_level)
        if grade:
            _level_filter += " AND u.grade = ?"
            _params.append(grade)
        cursor.execute(
            f"""
            WITH active_users AS (
                SELECT DISTINCT a.user_id
                FROM attempts a
                JOIN users u ON a.user_id = u.id
                WHERE u.role = 'student'
                  AND a.timestamp >= datetime('now', '-7 days')
                  {_level_filter}
            ),
            latest_elo AS (
                SELECT a.user_id, a.elo_after,
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
                       ROUND(AVG(le.elo_after), 0) AS global_elo
                FROM latest_elo le
                WHERE le.rn = 1
                GROUP BY le.user_id
            ),
            week_attempts AS (
                SELECT a.user_id, COUNT(*) AS attempts_this_week
                FROM attempts a
                WHERE a.user_id IN (SELECT user_id FROM active_users)
                  AND a.timestamp >= datetime('now', '-7 days')
                GROUP BY a.user_id
            )
            SELECT ue.user_id, u.username, ue.global_elo, wa.attempts_this_week
            FROM user_elo ue
            JOIN users u ON ue.user_id = u.id
            JOIN week_attempts wa ON ue.user_id = wa.user_id
            ORDER BY ue.global_elo DESC
            LIMIT ?
        """,
            (*_params, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "user_id": row[0],
                "username": row[1],
                "global_elo": row[2],
                "rank": idx + 1,
                "attempts_this_week": row[3],
            }
            for idx, row in enumerate(rows)
        ]

    def get_course_ranking(self, course_id, limit=5):
        """Top estudiantes en un curso específico por ELO promedio, últimos 7 días."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            WITH active_users AS (
                SELECT DISTINCT a.user_id
                FROM attempts a
                JOIN users u ON a.user_id = u.id
                JOIN items i ON a.item_id = i.id
                WHERE u.role = 'student'
                  AND i.course_id = ?
                  AND a.timestamp >= datetime('now', '-7 days')
            ),
            latest_elo AS (
                SELECT a.user_id, a.elo_after,
                       ROW_NUMBER() OVER (
                           PARTITION BY a.user_id, i.topic
                           ORDER BY a.timestamp DESC
                       ) AS rn
                FROM attempts a
                JOIN items i ON a.item_id = i.id
                WHERE a.user_id IN (SELECT user_id FROM active_users)
                  AND i.course_id = ?
            ),
            user_elo AS (
                SELECT le.user_id,
                       ROUND(AVG(le.elo_after), 0) AS course_elo
                FROM latest_elo le
                WHERE le.rn = 1
                GROUP BY le.user_id
            ),
            week_attempts AS (
                SELECT a.user_id, COUNT(*) AS attempts_this_week
                FROM attempts a
                JOIN items i ON a.item_id = i.id
                WHERE a.user_id IN (SELECT user_id FROM active_users)
                  AND i.course_id = ?
                  AND a.timestamp >= datetime('now', '-7 days')
                GROUP BY a.user_id
            )
            SELECT ue.user_id, u.username, ue.course_elo, wa.attempts_this_week
            FROM user_elo ue
            JOIN users u ON ue.user_id = u.id
            JOIN week_attempts wa ON ue.user_id = wa.user_id
            ORDER BY ue.course_elo DESC
            LIMIT ?
        """,
            (course_id, course_id, course_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "user_id": row[0],
                "username": row[1],
                "course_elo": row[2],
                "rank": idx + 1,
                "attempts_this_week": row[3],
            }
            for idx, row in enumerate(rows)
        ]

    def get_student_rank(self, user_id, course_id=None, education_level=None, grade=None):
        """Posición del estudiante en el ranking (global o por curso)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if course_id is not None:
            # Ranking por curso (ignora education_level)
            cursor.execute(
                """
                WITH active_users AS (
                    SELECT DISTINCT a.user_id
                    FROM attempts a
                    JOIN users u ON a.user_id = u.id
                    JOIN items i ON a.item_id = i.id
                    WHERE u.role = 'student'
                      AND i.course_id = ?
                      AND a.timestamp >= datetime('now', '-7 days')
                ),
                latest_elo AS (
                    SELECT a.user_id, a.elo_after,
                           ROW_NUMBER() OVER (
                               PARTITION BY a.user_id, i.topic
                               ORDER BY a.timestamp DESC
                           ) AS rn
                    FROM attempts a
                    JOIN items i ON a.item_id = i.id
                    WHERE a.user_id IN (SELECT user_id FROM active_users)
                      AND i.course_id = ?
                ),
                user_elo AS (
                    SELECT le.user_id,
                           ROUND(AVG(le.elo_after), 0) AS course_elo
                    FROM latest_elo le
                    WHERE le.rn = 1
                    GROUP BY le.user_id
                ),
                ranked AS (
                    SELECT user_id, course_elo AS global_elo,
                           ROW_NUMBER() OVER (ORDER BY course_elo DESC) AS rank
                    FROM user_elo
                )
                SELECT rank, (SELECT COUNT(*) FROM user_elo) AS total, global_elo
                FROM ranked WHERE user_id = ?
            """,
                (course_id, course_id, user_id),
            )
        else:
            # Ranking global, opcionalmente filtrado por nivel educativo y grado
            _level_filter = ""
            _params = []
            if education_level:
                _level_filter += "AND u.education_level = ?"
                _params.append(education_level)
            if grade:
                _level_filter += " AND u.grade = ?"
                _params.append(grade)
            _params.append(user_id)
            cursor.execute(
                f"""
                WITH active_users AS (
                    SELECT DISTINCT a.user_id
                    FROM attempts a
                    JOIN users u ON a.user_id = u.id
                    WHERE u.role = 'student'
                      AND a.timestamp >= datetime('now', '-7 days')
                      {_level_filter}
                ),
                latest_elo AS (
                    SELECT a.user_id, a.elo_after,
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
                           ROUND(AVG(le.elo_after), 0) AS global_elo
                    FROM latest_elo le
                    WHERE le.rn = 1
                    GROUP BY le.user_id
                ),
                ranked AS (
                    SELECT user_id, global_elo,
                           ROW_NUMBER() OVER (ORDER BY global_elo DESC) AS rank
                    FROM user_elo
                )
                SELECT rank, (SELECT COUNT(*) FROM user_elo) AS total, global_elo
                FROM ranked WHERE user_id = ?
            """,
                tuple(_params),
            )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"rank": row[0], "total_students": row[1], "global_elo": row[2]}
        return None

    def get_total_attempts_count(self, user_id):
        """Retorna el número total de intentos de un estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attempts WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_latest_attempts(self, user_id, limit=20):
        """Retorna los últimos N intentos con el resultado real y el esperado."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT is_correct, expected_score, prob_failure
            FROM attempts
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()

        results = []
        for is_correct, expected, prob_fail in rows:
            actual = 1.0 if is_correct else 0.0
            # Si expected_score es NULL (intentos viejos), lo derivamos de prob_failure
            if expected is None and prob_fail is not None:
                expected = 1.0 - prob_fail
            elif expected is None:
                expected = 0.5  # Valor neutro por defecto si no hay datos

            results.append({"actual": actual, "expected": expected})
        return results

    def get_user_history_elo(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT elo_after FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows] if rows else [1000]

    def get_latest_elo(self, user_id):
        history = self.get_user_history_elo(user_id)
        return history[-1]

    def get_attempts_for_ai(self, user_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT topic, difficulty, is_correct, timestamp
            FROM attempts
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (user_id, limit),
        )
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_answered_item_ids(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT item_id FROM attempts WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_latest_elo_by_topic(self, user_id):
        """Devuelve {topic: (elo_actual, rd_actual)} incluyendo ajustes de procedimientos.

        Fuentes de ELO (en orden de aplicación):
          1. Intentos de preguntas (tabla `attempts`) — base cronológica.
          2. Procedimientos validados por docente (elo_delta de procedure_submissions).
             INVARIANTE: solo elo_delta de status='VALIDATED_BY_TEACHER' se aplica aquí.
             ai_proposed_score NUNCA afecta este cálculo.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. ELO base desde los intentos de preguntas
        cursor.execute(
            "SELECT topic, elo_after, rating_deviation "
            "FROM attempts WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,),
        )
        elo_map = {}
        for topic, elo, rd in cursor.fetchall():
            elo_map[topic] = (elo, rd if rd is not None else 350.0)

        # 2. Sumar deltas ELO de procedimientos validados por el docente (agrupados por tópico)
        cursor.execute(
            """
            SELECT i.topic, SUM(ps.elo_delta)
            FROM procedure_submissions ps
            JOIN items i ON ps.item_id = i.id
            WHERE ps.student_id = ?
              AND ps.status = 'VALIDATED_BY_TEACHER'
              AND ps.elo_delta IS NOT NULL
            GROUP BY i.topic
        """,
            (user_id,),
        )
        for topic, total_delta in cursor.fetchall():
            if topic in elo_map:
                base_elo, rd = elo_map[topic]
                elo_map[topic] = (round(base_elo + total_delta, 2), rd)
            else:
                # Tópico solo en procedimientos (sin intentos de preguntas aún)
                elo_map[topic] = (round(1000.0 + total_delta, 2), 350.0)

        conn.close()
        return elo_map

    def get_user_history_full(self, user_id):
        """Devuelve historial completo para gráficas: [{'timestamp':..., 'topic':..., 'elo':..., 'time_taken':...}]"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, topic, elo_after, time_taken FROM attempts WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"timestamp": r[0], "topic": r[1], "elo": r[2], "time_taken": r[3]} for r in rows]

    # ─── Métodos para ADMIN ─────────────────────────────────────────────────────

    def get_pending_teachers(self):
        """Retorna lista de teachers pendientes de aprobación."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, created_at FROM users WHERE role = 'teacher' AND approved = 0 ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "username": r[1], "created_at": r[2]} for r in rows]

    def get_approved_teachers(self):
        """Retorna lista de teachers aprobados y activos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, created_at FROM users WHERE role = 'teacher' AND approved = 1 AND active = 1 ORDER BY username ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "username": r[1], "created_at": r[2]} for r in rows]

    def deactivate_user(self, user_id):
        """Da de baja (desactiva) a un usuario por id."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def reactivate_user(self, user_id):
        """Reactiva un usuario dado de baja, conservando todo su progreso."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET active = 1 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def approve_teacher(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET approved = 1 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def reject_teacher(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ? AND role = 'teacher'", (user_id,))
        conn.commit()
        conn.close()

    # ─── Métodos para TEACHER ────────────────────────────────────────────────────

    def get_all_students(self):
        """Retorna lista de todos los estudiantes activos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, created_at FROM users WHERE role = 'student' AND active = 1 ORDER BY username ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "username": r[1], "created_at": r[2]} for r in rows]

    def get_all_students_admin(self):
        """Retorna TODOS los estudiantes (activos e inactivos) con su grupo para el panel admin."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.username, u.active, u.created_at, g.name as group_name
            FROM users u
            LEFT JOIN groups g ON u.group_id = g.id
            WHERE u.role = 'student'
            ORDER BY u.username ASC
        """
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {"id": r[0], "username": r[1], "active": r[2], "created_at": r[3], "group_name": r[4]}
            for r in rows
        ]

    # ─── Gestión de GRUPOS ────────────────────────────────────────────────────────

    def create_group(self, name, teacher_id, course_id=None):
        """Crea un nuevo grupo para un profesor, opcionalmente vinculado a un curso.

        Returns (True, msg) si fue creado, (False, msg) si hay duplicado u otro error.
        """
        name_normalized = name.strip().lower()
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO groups (name, teacher_id, course_id, name_normalized) VALUES (?, ?, ?, ?)",
                (name, teacher_id, course_id, name_normalized),
            )
            conn.commit()
            return True, f"Grupo '{name}' creado exitosamente."
        except sqlite3.IntegrityError:
            return False, "Ya existe un grupo con ese nombre."
        finally:
            conn.close()

    def get_groups_by_teacher(self, teacher_id):
        """Lista grupos de un profesor con el nombre y bloque del curso vinculado (JOIN)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT g.id, g.name, g.course_id, COALESCE(c.name, '—') AS course_name, g.created_at,
                   COALESCE(c.block, 'Universidad') AS block, g.invite_code
            FROM groups g
            LEFT JOIN courses c ON g.course_id = c.id
            WHERE g.teacher_id = ?
            ORDER BY g.name ASC
        """,
            (teacher_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "name": r[1],
                "course_id": r[2],
                "course_name": r[3],
                "created_at": r[4],
                "block": r[5],
                "invite_code": r[6],
            }
            for r in rows
        ]

    def get_teachers_with_groups_and_courses(self, education_level: str, grade: str = None) -> list:
        """Devuelve lista de profesores con sus grupos y cursos para un nivel educativo.

        Filtra por bloque del nivel del estudiante. Si grade se proporciona (Semillero),
        filtra también por grado dentro del bloque.
        """
        _LEVEL_TO_BLOCK = {
            "universidad": "Universidad",
            "colegio": "Colegio",
            "concursos": "Concursos",
            "semillero": "Semillero",
        }
        block = _LEVEL_TO_BLOCK.get((education_level or "universidad").lower(), "Universidad")
        conn = self.get_connection()
        cursor = conn.cursor()
        if grade and block == "Semillero":
            cursor.execute(
                """
                SELECT g.id, g.name, g.course_id, c.name AS course_name,
                       u.id AS teacher_id, u.username AS teacher_name,
                       (SELECT COUNT(*) FROM enrollments e WHERE e.group_id = g.id) AS student_count
                FROM groups g
                JOIN users u ON g.teacher_id = u.id
                JOIN courses c ON g.course_id = c.id
                WHERE u.active = 1 AND u.approved = 1
                  AND c.block = ? AND c.id LIKE ?
                ORDER BY u.username ASC, c.name ASC
            """,
                (block, f"%semillero_{grade}"),
            )
        else:
            cursor.execute(
                """
                SELECT g.id, g.name, g.course_id, c.name AS course_name,
                       u.id AS teacher_id, u.username AS teacher_name,
                       (SELECT COUNT(*) FROM enrollments e WHERE e.group_id = g.id) AS student_count
                FROM groups g
                JOIN users u ON g.teacher_id = u.id
                JOIN courses c ON g.course_id = c.id
                WHERE u.active = 1 AND u.approved = 1
                  AND c.block = ?
                ORDER BY u.username ASC, c.name ASC
            """,
                (block,),
            )
        rows = cursor.fetchall()
        conn.close()
        teachers: dict = {}
        for r in rows:
            tid = r[4]
            if tid not in teachers:
                teachers[tid] = {"teacher_id": tid, "teacher_name": r[5], "groups": []}
            teachers[tid]["groups"].append(
                {
                    "group_id": r[0],
                    "group_name": r[1],
                    "course_id": r[2],
                    "course_name": r[3],
                    "student_count": r[6] or 0,
                }
            )
        return list(teachers.values())

    def generate_group_invite_code(self, group_id: int) -> str:
        """Genera o regenera el código de invitación de 6 chars para un grupo."""
        import random, string

        conn = self.get_connection()
        cursor = conn.cursor()
        for _ in range(10):
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            try:
                cursor.execute("UPDATE groups SET invite_code = ? WHERE id = ?", (code, group_id))
                conn.commit()
                conn.close()
                return code
            except Exception:
                conn.rollback()
        conn.close()
        raise RuntimeError("No se pudo generar un código único. Intenta de nuevo.")

    def get_group_by_invite_code(self, code: str) -> dict | None:
        """Busca un grupo por su código de invitación. Retorna dict o None."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT g.id, g.name, g.course_id, c.name AS course_name, u.username AS teacher_name,
                   c.block
            FROM groups g
            JOIN courses c ON g.course_id = c.id
            JOIN users u ON g.teacher_id = u.id
            WHERE g.invite_code = ? AND u.active = 1 AND u.approved = 1
        """,
            (code.upper().strip(),),
        )
        r = cursor.fetchone()
        conn.close()
        if not r:
            return None
        return {
            "group_id": r[0],
            "group_name": r[1],
            "course_id": r[2],
            "course_name": r[3],
            "teacher_name": r[4],
            "block": r[5],
        }

    def get_all_groups(self):
        """Lista todos los grupos disponibles (para el registro de estudiantes)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT g.id, g.name, u.username as teacher_name
            FROM groups g
            JOIN users u ON g.teacher_id = u.id
            ORDER BY g.name ASC
        """
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "teacher_name": r[2]} for r in rows]

    def delete_group(self, group_id, admin_id):
        """Elimina un grupo (solo admin). Desvincula estudiantes y matrículas del grupo.

        Returns (True, msg) o (False, msg).
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Validar que el ejecutor sea admin
            cursor.execute("SELECT role FROM users WHERE id = ? AND active = 1", (admin_id,))
            res = cursor.fetchone()
            if not res or res[0] != "admin":
                return False, "Error de seguridad: Solo un administrador puede eliminar grupos."

            # Verificar que el grupo existe
            cursor.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
            grp = cursor.fetchone()
            if not grp:
                return False, "El grupo no existe."

            group_name = grp[0]

            # Desvincular estudiantes del grupo (conservar sus datos)
            cursor.execute("UPDATE users SET group_id = NULL WHERE group_id = ?", (group_id,))

            # Desvincular matrículas del grupo
            cursor.execute("UPDATE enrollments SET group_id = NULL WHERE group_id = ?", (group_id,))

            # Eliminar el grupo
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))

            conn.commit()
            return True, f"Grupo '{group_name}' eliminado. Los estudiantes fueron desvinculados."
        except Exception as e:
            conn.rollback()
            return False, f"Error al eliminar grupo: {e}"
        finally:
            conn.close()

    def get_students_by_teacher(self, teacher_id):
        """Retorna estudiantes vinculados al profesor vía grupo primario O matrículas.

        Un estudiante puede aparecer varias veces si está matriculado en
        múltiples grupos del profesor — una fila por (estudiante, grupo).
        Esto permite que los filtros de grupo/nivel/materia funcionen
        correctamente mostrando al estudiante en cada contexto.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        # Unión de dos fuentes: grupo primario (users.group_id) y matrículas
        # (enrollments.group_id). UNION elimina duplicados exactos.
        cursor.execute(
            """
            SELECT u.id, u.username, u.created_at, g.name AS group_name, g.id AS group_id,
                   g.course_id, COALESCE(c.name, '—') AS course_name,
                   COALESCE(c.block, '—') AS course_block
            FROM users u
            JOIN groups g ON u.group_id = g.id
            LEFT JOIN courses c ON g.course_id = c.id
            WHERE g.teacher_id = ? AND u.active = 1

            UNION

            SELECT u.id, u.username, u.created_at, g.name AS group_name, g.id AS group_id,
                   g.course_id, COALESCE(c.name, '—') AS course_name,
                   COALESCE(c.block, '—') AS course_block
            FROM enrollments e
            JOIN users u ON e.user_id = u.id
            JOIN groups g ON e.group_id = g.id
            LEFT JOIN courses c ON g.course_id = c.id
            WHERE g.teacher_id = ? AND u.active = 1

            ORDER BY 2 ASC
        """,
            (teacher_id, teacher_id),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "username": r[1],
                "created_at": r[2],
                "group_name": r[3],
                "group_id": r[4],
                "course_id": r[5],
                "course_name": r[6],
                "course_block": r[7],
            }
            for r in rows
        ]

    def get_students_by_group(self, group_id, teacher_id):
        """Retorna estudiantes de un grupo específico, validando que sea del profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.username, u.created_at
            FROM users u
            JOIN groups g ON u.group_id = g.id
            WHERE u.group_id = ? AND g.teacher_id = ? AND u.active = 1
            ORDER BY u.username ASC
        """,
            (group_id, teacher_id),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "username": r[1], "created_at": r[2]} for r in rows]

    def get_student_attempts_detail(self, student_id):
        """Historial detallado de intentos de un estudiante (para el teacher)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, topic, difficulty, is_correct, elo_after, rating_deviation, prob_failure, timestamp, time_taken
            FROM attempts
            WHERE user_id = ?
            ORDER BY timestamp ASC
        """,
            (student_id,),
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    def export_teacher_student_data(self, teacher_id, group_id=None):
        """Exporta TODOS los datos de estudiantes del profesor para análisis externo.

        Retorna una lista de dicts con: datos del estudiante, intento, ítem,
        curso, matrícula, tiempo, RD, probabilidad, etc.
        Si group_id se proporciona, filtra solo ese grupo.
        """
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        _group_filter = "AND g.id = ?" if group_id else ""
        _params = [teacher_id, teacher_id]
        if group_id:
            _params.extend([group_id, group_id])

        cursor.execute(
            f"""
            SELECT
                u.id AS student_id,
                u.username,
                u.education_level,
                u.grade,
                g.name AS group_name,
                c.name AS course_name,
                c.block AS course_block,
                a.id AS attempt_id,
                a.item_id,
                i.topic,
                i.content AS item_content,
                a.difficulty AS item_difficulty,
                a.is_correct,
                a.elo_after,
                a.rating_deviation AS attempt_rd,
                a.prob_failure,
                a.expected_score,
                a.time_taken,
                a.confidence_score,
                a.error_type,
                a.timestamp AS attempt_timestamp,
                i.tags AS item_tags
            FROM attempts a
            JOIN users u ON a.user_id = u.id
            JOIN items i ON a.item_id = i.id
            LEFT JOIN courses c ON i.course_id = c.id
            LEFT JOIN groups g ON u.group_id = g.id
            WHERE u.active = 1
              AND g.teacher_id = ?
              {_group_filter.replace('?', '?') if group_id else ''}

            UNION ALL

            SELECT
                u.id AS student_id,
                u.username,
                u.education_level,
                u.grade,
                g.name AS group_name,
                c.name AS course_name,
                c.block AS course_block,
                a.id AS attempt_id,
                a.item_id,
                i.topic,
                i.content AS item_content,
                a.difficulty AS item_difficulty,
                a.is_correct,
                a.elo_after,
                a.rating_deviation AS attempt_rd,
                a.prob_failure,
                a.expected_score,
                a.time_taken,
                a.confidence_score,
                a.error_type,
                a.timestamp AS attempt_timestamp,
                i.tags AS item_tags
            FROM attempts a
            JOIN users u ON a.user_id = u.id
            JOIN items i ON a.item_id = i.id
            LEFT JOIN courses c ON i.course_id = c.id
            JOIN enrollments e ON e.user_id = u.id
            JOIN groups g ON e.group_id = g.id
            WHERE u.active = 1
              AND g.teacher_id = ?
              {_group_filter.replace('?', '?') if group_id else ''}

            ORDER BY username ASC, attempt_timestamp ASC
        """,
            tuple(_params),
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        result = [dict(zip(columns, row)) for row in rows]
        for row in result:
            try:
                tags = json.loads(row.pop("item_tags") or "[]")
            except Exception:
                tags = []
            row["item_area"] = next(
                (t.split(":", 1)[1].rstrip("]").strip() for t in tags if t.startswith("[General:")),
                "Sin registro",
            )
            row["item_enfoque"] = next(
                (t.split(":", 1)[1].rstrip("]").strip() for t in tags if t.startswith("[Enfoque:")),
                "Sin registro",
            )
            row["item_componente"] = next(
                (
                    t.split(":", 1)[1].rstrip("]").strip()
                    for t in tags
                    if t.startswith("[Específica:")
                ),
                "Sin registro",
            )
        return result

    def export_teacher_enrollments(self, teacher_id, group_id=None):
        """Exporta matrículas de los estudiantes del profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        _gf = "AND g.id = ?" if group_id else ""
        _params = (teacher_id, group_id) if group_id else (teacher_id,)
        cursor.execute(
            f"""
            SELECT
                u.id AS student_id,
                u.username,
                u.education_level,
                u.grade,
                g.name AS group_name,
                c.id AS course_id,
                c.name AS course_name,
                c.block AS course_block,
                e.enrolled_at
            FROM enrollments e
            JOIN users u ON e.user_id = u.id
            JOIN groups g ON e.group_id = g.id
            LEFT JOIN courses c ON e.course_id = c.id
            WHERE u.active = 1
              AND g.teacher_id = ?
              {_gf}
            ORDER BY u.username ASC, c.name ASC
        """,
            _params,
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    def export_teacher_procedures(self, teacher_id, group_id=None):
        """Exporta datos de procedimientos de los estudiantes del profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        _gf = "AND g.id = ?" if group_id else ""
        _params = (teacher_id, group_id) if group_id else (teacher_id,)
        cursor.execute(
            f"""
            SELECT
                u.id AS student_id,
                u.username,
                g.name AS group_name,
                ps.item_id,
                ps.item_content,
                ps.status,
                ps.ai_proposed_score,
                ps.teacher_score,
                ps.final_score,
                ps.elo_delta,
                ps.submitted_at,
                ps.reviewed_at
            FROM procedure_submissions ps
            JOIN users u ON ps.student_id = u.id
            LEFT JOIN groups g ON u.group_id = g.id
            WHERE u.active = 1
              AND g.teacher_id = ?
              {_gf}
            ORDER BY u.username ASC, ps.submitted_at ASC
        """,
            _params,
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    # ─── Gestión de SEGURIDAD (Admin) ───────────────────────────────────────────

    def change_student_group(self, student_id, new_group_id, admin_id, allow_null=False):
        """
        Reasigna a un estudiante a un nuevo grupo con validaciones y auditoría.
        Usa transacciones para asegurar la integridad de los datos.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # 1. Validar que el ejecutor sea ADMIN
            cursor.execute("SELECT role FROM users WHERE id = ? AND active = 1", (admin_id,))
            res = cursor.fetchone()
            if not res or res[0] != "admin":
                return (
                    False,
                    "Error de seguridad: Solo un administrador puede realizar esta acción.",
                )

            # 2. Validar que el objetivo sea ESTUDIANTE y obtener su grupo actual
            cursor.execute(
                "SELECT role, group_id FROM users WHERE id = ? AND active = 1", (student_id,)
            )
            res = cursor.fetchone()
            if not res:
                return False, "Error: El estudiante no existe o está inactivo."

            target_role, old_group_id = res
            if target_role != "student":
                return False, f"Error: No se puede cambiar el grupo de un {target_role}."

            # 3. Validar redundancia
            if old_group_id == new_group_id:
                return False, "Información: El estudiante ya pertenece al grupo seleccionado."

            # 4. Validar existencia del nuevo grupo
            if new_group_id is not None:
                cursor.execute("SELECT id FROM groups WHERE id = ?", (new_group_id,))
                if not cursor.fetchone():
                    return False, "Error: El grupo destino no existe."
            elif not allow_null:
                return False, "Error: No se permite dejar al estudiante sin grupo."

            # 5. Ejecutar cambio y auditoría en una transacción
            cursor.execute("UPDATE users SET group_id = ? WHERE id = ?", (new_group_id, student_id))

            cursor.execute(
                """
                INSERT INTO audit_group_changes (student_id, old_group_id, new_group_id, admin_id)
                VALUES (?, ?, ?, ?)
            """,
                (student_id, old_group_id, new_group_id, admin_id),
            )

            conn.commit()
            return True, "Reasignación completada y auditada correctamente."

        except Exception as e:
            conn.rollback()
            return False, f"Error crítico en la base de datos: {str(e)}"
        finally:
            conn.close()

    # ─── Gestión de CURSOS y MATRÍCULAS ─────────────────────────────────────────

    # Bloque al que pertenece cada curso (por slug del archivo).
    # Ampliar aquí cuando se agreguen cursos de Colegio.
    _COURSE_BLOCK_MAP = {
        # ── Bloque Universidad ────────────────────────────────────────────────
        "algebra_lineal": "Universidad",
        "calculo_diferencial": "Universidad",
        "calculo_integral": "Universidad",
        "calculo_varias_variables": "Universidad",
        "ecuaciones_diferenciales": "Universidad",
        "probabilidad": "Universidad",
        # ── Bloque Colegio ────────────────────────────────────────────────────
        "algebra_basica": "Colegio",
        "aritmetica": "Colegio",
        "aritmetica_basica": "Colegio",
        "trigonometria": "Colegio",
        "geometria": "Colegio",
        # ── Bloque Concursos (preparación para concursos públicos) ────────────
        "DIAN": "Concursos",
        "SENA": "Concursos",
        # ── Bloque Semillero (Olimpiadas Matemáticas UdeA, grados 6–11) ───────
        "logica_semillero_6": "Semillero",
        "algebra_semillero_6": "Semillero",
        "geometria_semillero_6": "Semillero",
        "conteo_combinatoria_semillero_6": "Semillero",
        "probabilidad_semillero_6": "Semillero",
        "aritmetica_semillero_6": "Semillero",
        "logica_semillero_7": "Semillero",
        "algebra_semillero_7": "Semillero",
        "geometria_semillero_7": "Semillero",
        "conteo_combinatoria_semillero_7": "Semillero",
        "probabilidad_semillero_7": "Semillero",
        "aritmetica_semillero_7": "Semillero",
        "logica_semillero_8": "Semillero",
        "algebra_semillero_8": "Semillero",
        "geometria_semillero_8": "Semillero",
        "conteo_combinatoria_semillero_8": "Semillero",
        "probabilidad_semillero_8": "Semillero",
        "aritmetica_semillero_8": "Semillero",
        "aritmetica_semillero_9": "Semillero",
        "logica_semillero_9": "Semillero",
        "algebra_semillero_9": "Semillero",
        "geometria_semillero_9": "Semillero",
        "conteo_combinatoria_semillero_9": "Semillero",
        "probabilidad_semillero_9": "Semillero",
        "logica_semillero_10": "Semillero",
        "algebra_semillero_10": "Semillero",
        "geometria_semillero_10": "Semillero",
        "conteo_combinatoria_semillero_10": "Semillero",
        "probabilidad_semillero_10": "Semillero",
        "aritmetica_semillero_10": "Semillero",
        "logica_semillero_11": "Semillero",
        "algebra_semillero_11": "Semillero",
        "geometria_semillero_11": "Semillero",
        "conteo_combinatoria_semillero_11": "Semillero",
        "probabilidad_semillero_11": "Semillero",
        "aritmetica_semillero_11": "Semillero",
    }

    # Nombre legible del curso cuando el topic del primer ítem no es representativo.
    # Solo se necesita para cursos con múltiples subtemas heterogéneos.
    _COURSE_NAME_MAP = {
        "DIAN": "Concurso DIAN — Gestor I",
        "SENA": "Concurso SENA — Profesional 10",
        "logica_semillero_6": "Lógica Semillero 6°",
        "algebra_semillero_6": "Álgebra Semillero 6°",
        "geometria_semillero_6": "Geometría Semillero 6°",
        "conteo_combinatoria_semillero_6": "Conteo y Combinatoria Semillero 6°",
        "probabilidad_semillero_6": "Probabilidad Semillero 6°",
        "aritmetica_semillero_6": "Aritmética Semillero 6°",
        "logica_semillero_7": "Lógica Semillero 7°",
        "algebra_semillero_7": "Álgebra Semillero 7°",
        "geometria_semillero_7": "Geometría Semillero 7°",
        "conteo_combinatoria_semillero_7": "Conteo y Combinatoria Semillero 7°",
        "probabilidad_semillero_7": "Probabilidad Semillero 7°",
        "aritmetica_semillero_7": "Aritmética Semillero 7°",
        "logica_semillero_8": "Lógica Semillero 8°",
        "algebra_semillero_8": "Álgebra Semillero 8°",
        "geometria_semillero_8": "Geometría Semillero 8°",
        "conteo_combinatoria_semillero_8": "Conteo y Combinatoria Semillero 8°",
        "probabilidad_semillero_8": "Probabilidad Semillero 8°",
        "aritmetica_semillero_8": "Aritmética Semillero 8°",
        "aritmetica_semillero_9": "Aritmética Semillero 9°",
        "logica_semillero_9": "Lógica Semillero 9°",
        "algebra_semillero_9": "Álgebra Semillero 9°",
        "geometria_semillero_9": "Geometría Semillero 9°",
        "conteo_combinatoria_semillero_9": "Conteo y Combinatoria Semillero 9°",
        "probabilidad_semillero_9": "Probabilidad Semillero 9°",
        "logica_semillero_10": "Lógica Semillero 10°",
        "algebra_semillero_10": "Álgebra Semillero 10°",
        "geometria_semillero_10": "Geometría Semillero 10°",
        "conteo_combinatoria_semillero_10": "Conteo y Combinatoria Semillero 10°",
        "probabilidad_semillero_10": "Probabilidad Semillero 10°",
        "aritmetica_semillero_10": "Aritmética Semillero 10°",
        "logica_semillero_11": "Lógica Semillero 11°",
        "algebra_semillero_11": "Álgebra Semillero 11°",
        "geometria_semillero_11": "Geometría Semillero 11°",
        "conteo_combinatoria_semillero_11": "Conteo y Combinatoria Semillero 11°",
        "probabilidad_semillero_11": "Probabilidad Semillero 11°",
        "aritmetica_semillero_11": "Aritmética Semillero 11°",
    }

    def sync_items_from_bank_folder(self, bank_dir="items/bank"):
        """Escanea items/bank/*.json, registra cada archivo como curso y sincroniza
        sus ítems sin sobreescribir ratings ELO ya calculados."""
        import json
        import glob as _glob

        if not os.path.isdir(bank_dir):
            return

        json_files = sorted(_glob.glob(os.path.join(bank_dir, "*.json")))
        # También escanear el subdirectorio semillero/
        json_files += sorted(_glob.glob(os.path.join(bank_dir, "semillero", "*.json")))
        if not json_files:
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        for filepath in json_files:
            # course_id = nombre del archivo sin extensión (ej: 'algebra_lineal')
            course_id = os.path.splitext(os.path.basename(filepath))[0]
            _fname = os.path.basename(filepath)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    items_list = json.load(f)
            except UnicodeDecodeError as e:
                logger.error(
                    "Error de encoding en '%s': %s. "
                    "Asegúrate de que el archivo sea UTF-8 sin BOM. "
                    "Ejecuta: python scripts/validate_bank.py",
                    _fname,
                    e,
                )
                continue
            except json.JSONDecodeError as e:
                logger.error(
                    "JSON inválido en '%s': %s. " "Verifica la sintaxis con un linter JSON.",
                    _fname,
                    e,
                )
                continue
            except FileNotFoundError:
                logger.warning("Archivo no encontrado: '%s'. Ignorando.", filepath)
                continue

            if not items_list:
                continue

            # Nombre legible: usar mapa explícito o el topic del primer ítem
            course_name = self._COURSE_NAME_MAP.get(course_id) or items_list[0].get(
                "topic", course_id
            )
            block = self._COURSE_BLOCK_MAP.get(course_id, "Universidad")

            # Upsert del curso: insertar si no existe, actualizar nombre/bloque si cambiaron
            cursor.execute("SELECT id, name, block FROM courses WHERE id = ?", (course_id,))
            _existing = cursor.fetchone()
            if not _existing:
                cursor.execute(
                    "INSERT INTO courses (id, name, block, description) VALUES (?, ?, ?, ?)",
                    (course_id, course_name, block, f"Curso de {course_name}"),
                )
            elif _existing[1] != course_name or _existing[2] != block:
                # Actualizar si el nombre o bloque cambiaron (por reconfiguración)
                cursor.execute(
                    "UPDATE courses SET name = ?, block = ?, description = ? WHERE id = ?",
                    (course_name, block, f"Curso de {course_name}", course_id),
                )

            # Sincronizar cada ítem vinculándolo al curso
            for item in items_list:
                cursor.execute("SELECT id FROM items WHERE id = ?", (item["id"],))
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        INSERT INTO items
                            (id, topic, content, options, correct_option, difficulty, rating_deviation, course_id, image_url, tags)
                        VALUES (?, ?, ?, ?, ?, ?, 350.0, ?, ?, ?)
                    """,
                        (
                            item["id"],
                            item["topic"],
                            item["content"],
                            json.dumps(item["options"]),
                            item["correct_option"],
                            item["difficulty"],
                            course_id,
                            item.get("image_url") or item.get("image_path"),
                            json.dumps(item.get("tags") or []),
                        ),
                    )
                else:
                    # Actualizar contenido/metadatos sin tocar el rating ELO
                    cursor.execute(
                        """
                        UPDATE items
                        SET content = ?, options = ?, correct_option = ?, topic = ?, course_id = ?, image_url = ?, tags = ?
                        WHERE id = ?
                    """,
                        (
                            item["content"],
                            json.dumps(item["options"]),
                            item["correct_option"],
                            item["topic"],
                            course_id,
                            item.get("image_url") or item.get("image_path"),
                            json.dumps(item.get("tags") or []),
                            item["id"],
                        ),
                    )

        conn.commit()
        conn.close()

    def _seed_test_students(self):
        """Crea estudiantes de prueba permanentes (delegado a módulo externo)."""
        from src.infrastructure.persistence.seed_test_students import seed_test_students

        seed_test_students(self)

    def get_available_courses_by_level(self, level: str, grade=None):
        """Retorna los cursos disponibles filtrados ESTRICTAMENTE por nivel educativo.

        Parámetro level: 'universidad' | 'colegio' | 'concursos' | 'semillero' (case-insensitive).
        Para semillero, usar grade ('6'–'11') para filtrar por bloque específico de grado.
        La consulta usa WHERE block = ? sin fallback a todos los cursos;
        si el nivel no existe en la tabla, devuelve lista vacía.
        """
        from src.domain.entities import LEVEL_TO_BLOCK, LEVEL_UNIVERSIDAD

        if level.lower() == "semillero" and grade:
            _block = f"Semillero {grade}°"
        else:
            _block = LEVEL_TO_BLOCK.get(level.lower(), LEVEL_TO_BLOCK[LEVEL_UNIVERSIDAD])
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, block, description FROM courses WHERE block = ? ORDER BY name ASC",
            (_block,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "block": r[2], "description": r[3]} for r in rows]

    def get_courses(self, block=None):
        """Devuelve todos los cursos, opcionalmente filtrados por bloque."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if block:
            cursor.execute(
                "SELECT id, name, block, description FROM courses WHERE block = ? ORDER BY name ASC",
                (block,),
            )
        else:
            cursor.execute(
                "SELECT id, name, block, description FROM courses ORDER BY block ASC, name ASC"
            )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "block": r[2], "description": r[3]} for r in rows]

    def get_available_groups_for_course(self, course_id):
        """Retorna los grupos activos disponibles para un curso.

        Busca grupos por bloque del curso (no por course_id exacto) para que
        un único grupo "Semillero" o "Universidad" aparezca en todos los cursos
        de ese bloque. El JOIN con users expone el nombre del profesor.
        Solo retorna grupos cuyo teacher esté activo y aprobado.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT g.id, g.name, u.username AS teacher_name
            FROM groups g
            JOIN users u ON g.teacher_id = u.id
            WHERE g.course_id IN (
                SELECT id FROM courses WHERE block = (
                    SELECT block FROM courses WHERE id = ?
                )
            )
            AND u.active = 1 AND u.approved = 1
            ORDER BY g.name ASC
        """,
            (course_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "teacher_name": r[2]} for r in rows]

    def enroll_user(self, user_id, course_id, group_id=None):
        """Matricula a un usuario en un curso. Idempotente.

        Si se proporciona group_id:
          - Se registra en enrollments.group_id para rastrear la asociación curso→grupo.
          - Se actualiza users.group_id para mantener compatibilidad con el dashboard
            docente (que filtra estudiantes por grupo del profesor).
        Las matrículas existentes sin grupo quedan con group_id = NULL — no se rompen.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO enrollments (user_id, course_id, group_id) VALUES (?, ?, ?)",
            (user_id, course_id, group_id),
        )
        if group_id is not None:
            # Actualizar group_id aunque la matrícula ya existiera
            cursor.execute(
                "UPDATE enrollments SET group_id = ? WHERE user_id = ? AND course_id = ?",
                (group_id, user_id, course_id),
            )
            # Mantener users.group_id sincronizado (dashboard docente)
            cursor.execute("UPDATE users SET group_id = ? WHERE id = ?", (group_id, user_id))
        conn.commit()
        conn.close()

    def unenroll_user(self, user_id, course_id):
        """Elimina la matrícula de un usuario en un curso."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM enrollments WHERE user_id = ? AND course_id = ?", (user_id, course_id)
        )
        conn.commit()
        conn.close()

    def get_user_enrollments(self, user_id):
        """Devuelve los cursos en los que está matriculado el usuario.

        Incluye el nombre del grupo asociado a cada matrícula (puede ser None para
        inscripciones previas que no tenían grupo).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.name, c.block, c.description,
                   e.group_id, COALESCE(g.name, '') AS group_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            LEFT JOIN groups g ON e.group_id = g.id
            WHERE e.user_id = ?
            ORDER BY c.name ASC
        """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "name": r[1],
                "block": r[2],
                "description": r[3],
                "group_id": r[4],
                "group_name": r[5],
            }
            for r in rows
        ]

    def get_enrolled_topics(self, user_id):
        """Retorna el conjunto de tópicos relevantes para el filtrado de la tabla ELO.

        Fuentes incluidas (OR lógico):
          1. Tópicos de ítems pertenecientes a cursos en los que el estudiante
             está actualmente matriculado (enrollments → items.course_id → items.topic).
          2. Tópicos de ítems donde el estudiante tiene procedimientos enviados
             (independientemente de matrícula, para no ocultar actividad real).

        Retorna set vacío si el estudiante no tiene matrículas ni procedimientos;
        en ese caso, el llamador debe usar el elo_map completo como fallback.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        # Fuente 1: cursos matriculados → tópicos de sus ítems
        cursor.execute(
            """
            SELECT DISTINCT i.topic
            FROM enrollments e
            JOIN items i ON i.course_id = e.course_id
            WHERE e.user_id = ? AND i.topic IS NOT NULL
        """,
            (user_id,),
        )
        topics = {row[0] for row in cursor.fetchall()}
        # Fuente 2: tópicos de ítems con procedimientos enviados
        cursor.execute(
            """
            SELECT DISTINCT i.topic
            FROM procedure_submissions ps
            JOIN items i ON ps.item_id = i.id
            WHERE ps.student_id = ? AND i.topic IS NOT NULL
        """,
            (user_id,),
        )
        topics |= {row[0] for row in cursor.fetchall()}
        conn.close()
        return topics

    def set_education_level(self, user_id, level):
        """Guarda el nivel educativo del usuario ('universidad' | 'colegio')."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET education_level = ? WHERE id = ?", (level, user_id))
        conn.commit()
        conn.close()

    def get_education_level(self, user_id):
        """Retorna el education_level del usuario, o None si no existe."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT education_level FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def set_grade(self, user_id, grade):
        """Guarda el grado escolar del usuario (solo válido para nivel semillero)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET grade = ? WHERE id = ?", (grade, user_id))
        conn.commit()
        conn.close()

    def get_grade(self, user_id):
        """Retorna el grado del usuario, o None si no aplica."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT grade FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    # ─── Gestión de ÍTEMS (ELO Dinámico) ────────────────────────────────────────

    def sync_items_from_json(self, items_list):
        """Sincroniza el banco de preguntas JSON con la DB. No sobreescribe ratings actuales."""
        conn = self.get_connection()
        cursor = conn.cursor()
        import json

        for item in items_list:
            cursor.execute("SELECT id FROM items WHERE id = ?", (item["id"],))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO items (id, topic, content, options, correct_option, difficulty, rating_deviation)
                    VALUES (?, ?, ?, ?, ?, ?, 350.0)
                """,
                    (
                        item["id"],
                        item["topic"],
                        item["content"],
                        json.dumps(item["options"]),
                        item["correct_option"],
                        item["difficulty"],
                    ),
                )
            else:
                # Actualizar contenido y opciones para refrescar LaTeX sin perder el rating
                cursor.execute(
                    """
                    UPDATE items
                    SET content = ?, options = ?, correct_option = ?, topic = ?
                    WHERE id = ?
                """,
                    (
                        item["content"],
                        json.dumps(item["options"]),
                        item["correct_option"],
                        item["topic"],
                        item["id"],
                    ),
                )
        conn.commit()
        conn.close()

    def get_items_from_db(self, topic=None, course_id=None):
        """Obtiene ítems desde la base de datos.
        Prioridad de filtro: course_id > topic > sin filtro."""
        conn = self.get_connection()
        cursor = conn.cursor()
        import json

        if course_id:
            cursor.execute(
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url, tags FROM items WHERE course_id = ?",
                (course_id,),
            )
        elif topic and topic != "Todos":
            cursor.execute(
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url, tags FROM items WHERE topic = ?",
                (topic,),
            )
        else:
            cursor.execute(
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url, tags FROM items"
            )

        rows = cursor.fetchall()
        conn.close()

        items = []
        for r in rows:
            items.append(
                {
                    "id": r[0],
                    "topic": r[1],
                    "content": r[2],
                    "options": json.loads(r[3]),
                    "correct_option": r[4],
                    "difficulty": r[5],
                    "rating_deviation": r[6],
                    "image_url": r[7],
                    "tags": json.loads(r[8]) if r[8] else [],
                }
            )
        return items

    def update_item_rating(self, item_id, student_rating, actual_score, k_item=32.0):
        """
        Actualiza la dificultad (rating) del ítem de forma simétrica.
        Si el alumno gana (acierta), el ítem pierde (baja dificultad).
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT difficulty, rating_deviation FROM items WHERE id = ?", (item_id,))
        res = cursor.fetchone()
        if not res:
            conn.close()
            return

        current_diff, current_rd = res

        # Lógica ELO inversa para el ítem
        # El resultado para el ítem es (1 - actual_score)
        item_score = 1.0 - actual_score

        # Probabilidad de que el ítem 'gane' (que el alumno falle)
        # expected_score(rating_estudiante, rating_item) es prob acierto alumno
        # prob fallo alumno = 1 - prob acierto
        from src.domain.elo.model import expected_score

        p_student_wins = expected_score(student_rating, current_diff)
        p_item_wins = 1.0 - p_student_wins

        delta = k_item * (item_score - p_item_wins)
        new_diff = current_diff + delta

        cursor.execute("UPDATE items SET difficulty = ? WHERE id = ?", (new_diff, item_id))
        conn.commit()
        conn.close()

    def create_session(self, user_id):
        import secrets
        from datetime import datetime, timedelta, timezone

        token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
                (token, user_id, expires_at.isoformat()),
            )
            conn.commit()
        return token

    def validate_session(self, token):
        from datetime import datetime, timezone

        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id, expires_at FROM sessions WHERE token = ?", (token,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            user_id, expires_at = row
            if datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
                conn.commit()
                return None
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()

    def delete_session(self, token):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()

    # ── Procedimientos para revisión del docente ──────────────────────────────

    def check_file_hash_duplicate(self, item_id, student_id, file_hash):
        """Verifica si el hash SHA-256 de un archivo ya fue registrado por OTRO estudiante
        para la misma pregunta. Previene plagio de procedimientos entre alumnos.

        Retorna True si hay duplicado (otro estudiante subió el mismo archivo), False si es limpio.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM procedure_submissions
            WHERE item_id = ? AND file_hash = ? AND student_id != ?
            LIMIT 1
        """,
            (item_id, file_hash, student_id),
        )
        found = cursor.fetchone() is not None
        conn.close()
        return found

    def save_procedure_submission(
        self, student_id, item_id, item_content, image_data, mime_type="image/jpeg", file_hash=None
    ):
        """Guarda o reemplaza el procedimiento enviado por el estudiante.
        La imagen se persiste en data/uploads/procedures/ y la ruta se almacena en la DB.
        file_hash: SHA-256 del archivo para detección anti-plagio.
        """
        import time as _time

        ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime_type, "jpg")
        os.makedirs(os.path.join("data", "uploads", "procedures"), exist_ok=True)
        img_filename = f"{student_id}_{item_id}_{int(_time.time())}.{ext}"
        img_path = os.path.join("data", "uploads", "procedures", img_filename)
        with open(img_path, "wb") as _f:
            _f.write(image_data)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM procedure_submissions WHERE student_id=? AND item_id=?",
            (student_id, item_id),
        )
        existing = cursor.fetchone()
        if existing:
            # Preserva ai_proposed_score si ya fue analizado por IA.
            # Resetea solo campos de revisión del docente (nueva entrega anula feedback anterior).
            cursor.execute(
                """
                UPDATE procedure_submissions
                SET image_data=?, mime_type=?, procedure_image_path=?, file_hash=?,
                    status=CASE
                        WHEN ai_proposed_score IS NOT NULL THEN 'PENDING_TEACHER_VALIDATION'
                        ELSE 'pending'
                    END,
                    teacher_feedback=NULL,
                    feedback_image=NULL, feedback_image_path=NULL,
                    procedure_score=NULL, teacher_score=NULL, final_score=NULL,
                    submitted_at=CURRENT_TIMESTAMP, reviewed_at=NULL
                WHERE student_id=? AND item_id=?
            """,
                (image_data, mime_type, img_path, file_hash, student_id, item_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO procedure_submissions
                    (student_id, item_id, item_content, image_data, mime_type, procedure_image_path, file_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (student_id, item_id, item_content, image_data, mime_type, img_path, file_hash),
            )
        conn.commit()
        conn.close()

    def save_ai_proposed_score(
        self, student_id: int, item_id: str, ai_score: float, ai_feedback: str = None
    ):
        """Guarda la puntuación propuesta por la IA y actualiza el status a PENDING_TEACHER_VALIDATION.

        INVARIANTE CRÍTICA: ai_proposed_score NUNCA modifica el ELO del estudiante.
        Solo final_score (validado por el docente vía Task 4) puede afectar analytics.

        Si no existe registro previo para student_id+item_id, no hace nada (la imagen
        debe guardarse primero con save_procedure_submission).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE procedure_submissions
            SET ai_proposed_score = ?,
                ai_feedback = ?,
                status = 'PENDING_TEACHER_VALIDATION'
            WHERE student_id = ? AND item_id = ?
        """,
            (ai_score, ai_feedback, student_id, item_id),
        )
        conn.commit()
        conn.close()

    def resolve_storage_image(self, storage_url: str):
        """Stub — SQLite backend does not use Supabase Storage."""
        return None

    def get_student_submission(self, student_id, item_id):
        """Retorna la entrega del estudiante para una pregunta, o None.
        Incluye ai_proposed_score, teacher_score y final_score del flujo de validación.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, status, teacher_feedback, feedback_image,
                   feedback_mime_type, submitted_at, reviewed_at,
                   procedure_score, feedback_image_path,
                   ai_proposed_score, teacher_score, final_score
            FROM procedure_submissions
            WHERE student_id=? AND item_id=?
        """,
            (student_id, item_id),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            cols = [
                "id",
                "status",
                "teacher_feedback",
                "feedback_image",
                "feedback_mime_type",
                "submitted_at",
                "reviewed_at",
                "procedure_score",
                "feedback_image_path",
                "ai_proposed_score",
                "teacher_score",
                "final_score",
            ]
            return dict(zip(cols, row))
        return None

    def get_reviewed_submission_ids(self, student_id):
        """Retorna los IDs de entregas que ya tienen retroalimentación (reviewed_at no nulo).

        Se usa junto con st.session_state para determinar cuáles son nuevas
        (el estudiante aún no las ha visto en el Centro de Feedback).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id FROM procedure_submissions
            WHERE student_id = ? AND reviewed_at IS NOT NULL
        """,
            (student_id,),
        )
        ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        return ids

    def get_student_feedback_history(self, student_id):
        """Historial completo de entregas del estudiante para el Centro de Feedback.

        Retorna todas las procedure_submissions del estudiante con datos de la
        pregunta asociada, ordenadas por fecha descendente (más reciente primero).
        Solo lectura — no dispara recálculo de ELO ni puntuación.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ps.id, ps.item_id,
                   SUBSTR(ps.item_content, 1, 80) AS item_short,
                   ps.ai_proposed_score, ps.ai_feedback,
                   ps.final_score, ps.teacher_score,
                   ps.procedure_score,
                   ps.teacher_feedback,
                   ps.status, ps.submitted_at, ps.reviewed_at,
                   ps.procedure_image_path, ps.feedback_image_path
            FROM procedure_submissions ps
            WHERE ps.student_id = ?
            ORDER BY ps.submitted_at DESC
        """,
            (student_id,),
        )
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_pending_submissions_count(self, teacher_id, group_id=None):
        """Cuenta las entregas pendientes de revisión del docente.
        Si se pasa group_id, restringe al grupo indicado.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        if group_id:
            cursor.execute(
                """
                SELECT COUNT(*) FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                WHERE u.group_id = ?
                  AND ps.status IN ('pending', 'PENDING_TEACHER_VALIDATION')
            """,
                (group_id,),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = ?
                  AND ps.status IN ('pending', 'PENDING_TEACHER_VALIDATION')
            """,
                (teacher_id,),
            )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_pending_submissions_for_teacher(self, teacher_id, group_id=None):
        """Retorna las entregas pendientes del docente.
        Si se pasa group_id, restringe al grupo indicado.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        if group_id:
            cursor.execute(
                """
                SELECT ps.id, ps.student_id, u.username AS student_name,
                       ps.item_id, ps.item_content, ps.image_data, ps.mime_type,
                       ps.submitted_at, ps.procedure_image_path,
                       ps.status, ps.ai_proposed_score, ps.ai_feedback
                FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                WHERE u.group_id = ?
                  AND ps.status IN ('pending', 'PENDING_TEACHER_VALIDATION')
                ORDER BY ps.submitted_at DESC
            """,
                (group_id,),
            )
        else:
            cursor.execute(
                """
                SELECT ps.id, ps.student_id, u.username AS student_name,
                       ps.item_id, ps.item_content, ps.image_data, ps.mime_type,
                       ps.submitted_at, ps.procedure_image_path,
                       ps.status, ps.ai_proposed_score, ps.ai_feedback
                FROM procedure_submissions ps
                JOIN users u ON ps.student_id = u.id
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = ?
                  AND ps.status IN ('pending', 'PENDING_TEACHER_VALIDATION')
                ORDER BY ps.submitted_at DESC
            """,
                (teacher_id,),
            )
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_student_elo_summary(self, student_id):
        """ELO actual por tópico, ELO global, total de intentos y precisión reciente.
        Devuelve dict con claves: elo_by_topic, global_elo, attempts_count, recent_accuracy.
        """
        elo_by_topic = self.get_latest_elo_by_topic(student_id)
        global_elo = (
            sum(e for e, _ in elo_by_topic.values()) / len(elo_by_topic) if elo_by_topic else 1000.0
        )
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attempts WHERE user_id = ?", (student_id,))
        total = cursor.fetchone()[0]
        cursor.execute(
            "SELECT is_correct FROM attempts WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10",
            (student_id,),
        )
        recent = cursor.fetchall()
        conn.close()
        recent_acc = sum(1 for r in recent if r[0]) / len(recent) if recent else 0.0
        return {
            "elo_by_topic": elo_by_topic,
            "global_elo": round(global_elo, 1),
            "attempts_count": total,
            "recent_accuracy": recent_acc,
        }

    def validate_procedure_submission(
        self, submission_id: int, teacher_score: float, feedback: str = ""
    ):
        """Valida la calificación de un procedimiento y establece la nota final oficial.

        Reglas de negocio:
          - teacher_score y final_score se fijan al mismo valor (el docente es la autoridad).
          - final_score es el único campo que puede afectar ELO y analytics (Task 5).
          - Una vez en 'VALIDATED_BY_TEACHER', la entrega desaparece de la cola pendiente.

        Args:
            submission_id: PK de procedure_submissions.
            teacher_score: Calificación oficial (0.0 – 100.0).
            feedback:      Comentario opcional del docente.
        """
        # ELO delta: independiente del ELO base del estudiante (es un ajuste aditivo)
        # Formula idéntica a apply_procedure_elo_adjustment: (score - 50) * 0.2
        elo_delta = round((teacher_score - 50.0) * 0.2, 4)

        conn = self.get_connection()
        conn.execute(
            """
            UPDATE procedure_submissions
            SET teacher_score    = ?,
                final_score      = ?,
                teacher_feedback = ?,
                elo_delta        = ?,
                status           = 'VALIDATED_BY_TEACHER',
                reviewed_at      = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (teacher_score, teacher_score, feedback or None, elo_delta, submission_id),
        )
        conn.commit()
        conn.close()

    def save_teacher_feedback(
        self,
        submission_id,
        feedback_text,
        feedback_image=None,
        feedback_mime_type=None,
        procedure_score=None,
    ):
        """Guarda la retroalimentación del docente y marca la entrega como revisada.
        Si se adjunta imagen de corrección, se persiste en data/uploads/feedback/.
        """
        feedback_image_path = None
        if feedback_image:
            import time as _time

            ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(
                feedback_mime_type, "jpg"
            )
            os.makedirs(os.path.join("data", "uploads", "feedback"), exist_ok=True)
            fb_filename = f"feedback_{submission_id}_{int(_time.time())}.{ext}"
            feedback_image_path = os.path.join("data", "uploads", "feedback", fb_filename)
            with open(feedback_image_path, "wb") as _f:
                _f.write(feedback_image)

        conn = self.get_connection()
        conn.execute(
            """
            UPDATE procedure_submissions
            SET teacher_feedback=?, feedback_image=?, feedback_mime_type=?,
                procedure_score=?, feedback_image_path=?,
                status='reviewed', reviewed_at=CURRENT_TIMESTAMP
            WHERE id=?
        """,
            (
                feedback_text,
                feedback_image,
                feedback_mime_type,
                procedure_score,
                feedback_image_path,
                submission_id,
            ),
        )
        conn.commit()
        conn.close()
