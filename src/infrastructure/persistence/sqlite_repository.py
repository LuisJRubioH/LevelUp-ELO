import os
from src.infrastructure.security.hashing_service import HashingService

# TODO: reemplazar SQLite por DB externa (PostgreSQL, etc.) en producción
class SQLiteRepository:
    def __init__(self, db_name=None):
        self.db_name = db_name or os.environ.get('DB_PATH', 'elo_project.db')
        self.hashing = HashingService()
        self.init_db()
        self._migrate_db()
        self._seed_demo_data()
        self._backfill_prob_failure()
        self.sync_items_from_bank_folder()

    def get_connection(self):
        import sqlite3
        return sqlite3.connect(self.db_name, timeout=10.0)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de grupos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
                approved INTEGER DEFAULT 1,
                active INTEGER DEFAULT 1,
                group_id INTEGER,
                rating_deviation REAL DEFAULT 350.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE SET NULL
            )
        ''')

        # Tabla de intentos/progreso
        cursor.execute('''
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
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_student_procedure_scores(self, student_id):
        """Retorna lista de notas de procedimientos evaluados por el docente para el estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT procedure_score, submitted_at
            FROM procedure_submissions
            WHERE student_id = ? AND procedure_score IS NOT NULL
            ORDER BY submitted_at DESC
        ''', (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'score': row[0], 'submitted_at': row[1]} for row in rows]

    def get_procedure_stats_by_course(self, student_id):
        """Retorna dict {course_id: {'course_name', 'avg_score', 'count'}} con el
        promedio de notas de procedimiento agrupadas por curso del estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.course_id, c.name, AVG(ps.procedure_score), COUNT(ps.id)
            FROM procedure_submissions ps
            JOIN items i ON ps.item_id = i.id
            LEFT JOIN courses c ON i.course_id = c.id
            WHERE ps.student_id = ? AND ps.procedure_score IS NOT NULL
            GROUP BY i.course_id
        ''', (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return {
            row[0]: {
                'course_name': row[1] or row[0],
                'avg_score': round(row[2], 2),
                'count': row[3]
            }
            for row in rows if row[0]
        }

    def get_students_procedure_summary_table(self, teacher_id):
        """Para el panel docente: lista de dicts con promedio de procedimiento
        por estudiante y curso, filtrado por los grupos del profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
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
        ''', (teacher_id,))
        cols = ['student_id', 'student', 'course_id', 'course_name', 'avg_score', 'count']
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        for row in rows:
            row['avg_score'] = round(row['avg_score'], 2)
        return rows


    def _migrate_db(self):
        """Agrega columnas nuevas de forma segura si no existen (migración)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Obtener columnas actuales de users
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [row[1] for row in cursor.fetchall()]
        if 'role' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
        if 'approved' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN approved INTEGER DEFAULT 1")
        if 'active' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN active INTEGER DEFAULT 1")
        if 'group_id' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN group_id INTEGER")
        if 'rating_deviation' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN rating_deviation REAL DEFAULT 350.0")
        if 'education_level' not in user_cols:
            # Sin DEFAULT: los usuarios existentes quedan NULL → pasan por onboarding la primera vez
            cursor.execute("ALTER TABLE users ADD COLUMN education_level TEXT")

        # Asegurar índices si no existen
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_teacher ON groups(teacher_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_group ON users(group_id)")

        # Asegurar tabla de auditoría
        cursor.execute('''
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
        ''')

        # Obtener columnas actuales de attempts
        cursor.execute("PRAGMA table_info(attempts)")
        attempt_cols = [row[1] for row in cursor.fetchall()]
        if 'prob_failure' not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN prob_failure REAL")
        if 'expected_score' not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN expected_score REAL")
        if 'time_taken' not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN time_taken REAL")
        if 'confidence_score' not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN confidence_score REAL")
        if 'error_type' not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN error_type TEXT")
        if 'rating_deviation' not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN rating_deviation REAL")

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

        # Migración de procedure_submissions: columnas añadidas en v2
        cursor.execute("PRAGMA table_info(procedure_submissions)")
        _proc_cols = [row[1] for row in cursor.fetchall()]
        if 'procedure_score' not in _proc_cols:
            cursor.execute("ALTER TABLE procedure_submissions ADD COLUMN procedure_score REAL")
        if 'procedure_image_path' not in _proc_cols:
            cursor.execute("ALTER TABLE procedure_submissions ADD COLUMN procedure_image_path TEXT")
        if 'feedback_image_path' not in _proc_cols:
            cursor.execute("ALTER TABLE procedure_submissions ADD COLUMN feedback_image_path TEXT")

        # Tabla de procedimientos enviados por estudiantes para revisión del docente
        cursor.execute('''
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
        ''')

        # ── LMS: Cursos y Matrículas ─────────────────────────────────────────────

        # Catálogo de cursos (uno por archivo JSON en items/bank/)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                block TEXT NOT NULL CHECK (block IN ('Universidad', 'Colegio')),
                description TEXT DEFAULT ''
            )
        ''')

        # Matrículas: relación N-N entre estudiantes y cursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, course_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        ''')

        # Vincular ítems a su curso (migración aditiva)
        cursor.execute("PRAGMA table_info(items)")
        item_cols = [row[1] for row in cursor.fetchall()]
        if 'course_id' not in item_cols:
            cursor.execute("ALTER TABLE items ADD COLUMN course_id TEXT REFERENCES courses(id)")

        conn.commit()
        conn.close()

    def _backfill_prob_failure(self):
        """Rellena prob_failure para intentos históricos que tienen NULL.
        Reconstruye el ELO por tópico en orden cronológico para cada estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Obtener todos los estudiantes con intentos sin prob_failure
        cursor.execute(
            "SELECT DISTINCT user_id FROM attempts WHERE prob_failure IS NULL"
        )
        user_ids = [row[0] for row in cursor.fetchall()]

        for user_id in user_ids:
            # Traer TODOS los intentos del usuario en orden cronológico
            cursor.execute(
                "SELECT id, topic, difficulty, elo_after FROM attempts "
                "WHERE user_id = ? ORDER BY timestamp ASC, id ASC",
                (user_id,)
            )
            attempts = cursor.fetchall()

            elo_by_topic = {}  # ELO reconstruido antes de cada intento
            for attempt_id, topic, difficulty, elo_after in attempts:
                elo_before = elo_by_topic.get(topic, 1000.0)
                p_success = expected_score(elo_before, difficulty)
                prob_failure = 1.0 - p_success

                cursor.execute(
                    "UPDATE attempts SET prob_failure = ? WHERE id = ?",
                    (prob_failure, attempt_id)
                )
                # Avanzar ELO reconstruido
                elo_by_topic[topic] = elo_after

        conn.commit()
        conn.close()

    def _seed_demo_data(self):
        """Crea usuarios y grupo demo si no existen (idempotente)."""
        # Pre-computar hashes ANTES de abrir la conexión:
        # Argon2 es lento por diseño; calcularlos con la DB abierta provoca "database is locked".
        admin_hash = self.hashing.hash_password("admin1234")
        demo_hash = self.hashing.hash_password("demo1234")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Admin
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, 'admin', 1)",
                ("admin", admin_hash)
            )

        # Profesor demo
        cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, 'teacher', 1)",
                ("profesor1", demo_hash)
            )

        conn.commit()

        # Grupo Demo (necesita el id del profesor)
        cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
        profesor_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM groups WHERE name = 'Grupo Demo' AND teacher_id = ?", (profesor_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO groups (name, teacher_id) VALUES (?, ?)",
                ("Grupo Demo", profesor_id)
            )
            conn.commit()

        cursor.execute("SELECT id FROM groups WHERE name = 'Grupo Demo' AND teacher_id = ?", (profesor_id,))
        group_id = cursor.fetchone()[0]

        # Estudiantes demo
        for username in ("estudiante1", "estudiante2"):
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, approved, group_id) VALUES (?, ?, 'student', 1, ?)",
                    (username, demo_hash, group_id)
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

    def register_user(self, username, password, role='student', group_id=None):
        """Registra un nuevo usuario. Valida group_id para estudiantes."""
        if role == 'student' and group_id is None:
            return False, "Error: Los estudiantes deben pertenecer a un grupo."

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hashing.hash_password(password)
            # Teachers necesitan aprobación; students y admin se aprueban solos
            approved = 0 if role == 'teacher' else 1
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved, group_id, rating_deviation) VALUES (?, ?, ?, ?, ?, 350.0)",
                (username, password_hash, role, approved, group_id)
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
            (username,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            user_id, uname, role, approved, stored_hash = row
            
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

    def save_attempt(self, user_id, item_id, is_correct, difficulty, topic, elo_after, prob_failure=None, expected_score=None, time_taken=None, confidence_score=None, error_type=None, rating_deviation=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attempts (user_id, item_id, is_correct, difficulty, topic, elo_after, prob_failure, expected_score, time_taken, confidence_score, error_type, rating_deviation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, item_id, is_correct, difficulty, topic, elo_after, prob_failure, expected_score, time_taken, confidence_score, error_type, rating_deviation))
        conn.commit()
        conn.close()

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
        cursor.execute('''
            SELECT is_correct, expected_score, prob_failure
            FROM attempts
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for is_correct, expected, prob_fail in rows:
            actual = 1.0 if is_correct else 0.0
            # Si expected_score es NULL (intentos viejos), lo derivamos de prob_failure
            if expected is None and prob_fail is not None:
                expected = 1.0 - prob_fail
            elif expected is None:
                expected = 0.5 # Valor neutro por defecto si no hay datos
            
            results.append({"actual": actual, "expected": expected})
        return results

    def get_user_history_elo(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT elo_after FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows] if rows else [1000]

    def get_latest_elo(self, user_id):
        history = self.get_user_history_elo(user_id)
        return history[-1]

    def get_attempts_for_ai(self, user_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT topic, difficulty, is_correct, timestamp
            FROM attempts
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
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
        """Devuelve un diccionario {topic: (elo_actual, rd_actual)} para el usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT topic, elo_after, rating_deviation FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        elo_map = {}
        for topic, elo, rd in rows:
            # Si rd es NULL (intentos viejos), usamos el valor por defecto 350.0
            elo_map[topic] = (elo, rd if rd is not None else 350.0)
        return elo_map

    def get_user_history_full(self, user_id):
        """Devuelve historial completo para gráficas: [{'timestamp':..., 'topic':..., 'elo':...}]"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, topic, elo_after FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'timestamp': r[0], 'topic': r[1], 'elo': r[2]} for r in rows]

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
        return [{'id': r[0], 'username': r[1], 'created_at': r[2]} for r in rows]

    def get_approved_teachers(self):
        """Retorna lista de teachers aprobados y activos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, created_at FROM users WHERE role = 'teacher' AND approved = 1 AND active = 1 ORDER BY username ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'username': r[1], 'created_at': r[2]} for r in rows]

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
        return [{'id': r[0], 'username': r[1], 'created_at': r[2]} for r in rows]

    def get_all_students_admin(self):
        """Retorna TODOS los estudiantes (activos e inactivos) con su grupo para el panel admin."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.active, u.created_at, g.name as group_name 
            FROM users u
            LEFT JOIN groups g ON u.group_id = g.id
            WHERE u.role = 'student' 
            ORDER BY u.username ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'username': r[1], 'active': r[2], 'created_at': r[3], 'group_name': r[4]} for r in rows]

    # ─── Gestión de GRUPOS ────────────────────────────────────────────────────────

    def create_group(self, name, teacher_id):
        """Crea un nuevo grupo para un profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO groups (name, teacher_id) VALUES (?, ?)", (name, teacher_id))
        conn.commit()
        conn.close()

    def get_groups_by_teacher(self, teacher_id):
        """Lista grupos que pertenecen a un profesor específico (Seguridad)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at FROM groups WHERE teacher_id = ? ORDER BY name ASC", (teacher_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'created_at': r[2]} for r in rows]

    def get_all_groups(self):
        """Lista todos los grupos disponibles (para el registro de estudiantes)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, u.username as teacher_name 
            FROM groups g
            JOIN users u ON g.teacher_id = u.id
            ORDER BY g.name ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'teacher_name': r[2]} for r in rows]

    def get_students_by_teacher(self, teacher_id):
        """Retorna estudiantes que pertenecen a CUALQUIER grupo del profesor (Seguridad)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.created_at, g.name as group_name, g.id as group_id
            FROM users u
            JOIN groups g ON u.group_id = g.id
            WHERE g.teacher_id = ? AND u.active = 1
            ORDER BY u.username ASC
        ''', (teacher_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'username': r[1], 'created_at': r[2], 'group_name': r[3], 'group_id': r[4]} for r in rows]

    def get_students_by_group(self, group_id, teacher_id):
        """Retorna estudiantes de un grupo específico, validando que sea del profesor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.created_at
            FROM users u
            JOIN groups g ON u.group_id = g.id
            WHERE u.group_id = ? AND g.teacher_id = ? AND u.active = 1
            ORDER BY u.username ASC
        ''', (group_id, teacher_id))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'username': r[1], 'created_at': r[2]} for r in rows]

    def get_student_attempts_detail(self, student_id):
        """Historial detallado de intentos de un estudiante (para el teacher)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, topic, difficulty, is_correct, elo_after, rating_deviation, prob_failure, timestamp
            FROM attempts
            WHERE user_id = ?
            ORDER BY timestamp ASC
        ''', (student_id,))
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
            if not res or res[0] != 'admin':
                return False, "Error de seguridad: Solo un administrador puede realizar esta acción."

            # 2. Validar que el objetivo sea ESTUDIANTE y obtener su grupo actual
            cursor.execute("SELECT role, group_id FROM users WHERE id = ? AND active = 1", (student_id,))
            res = cursor.fetchone()
            if not res:
                return False, "Error: El estudiante no existe o está inactivo."
            
            target_role, old_group_id = res
            if target_role != 'student':
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
            
            cursor.execute('''
                INSERT INTO audit_group_changes (student_id, old_group_id, new_group_id, admin_id)
                VALUES (?, ?, ?, ?)
            ''', (student_id, old_group_id, new_group_id, admin_id))
            
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
        'algebra_lineal':          'Universidad',
        'calculo_diferencial':     'Universidad',
        'calculo_integral':        'Universidad',
        'calculo_varias_variables':'Universidad',
        'ecuaciones_diferenciales':'Universidad',
        # ── Bloque Colegio ────────────────────────────────────────────────────
        'algebra_basica':          'Colegio',
        'aritmetica':              'Colegio',
        'aritmetica_basica':       'Colegio',
        'trigonometria':           'Colegio',
        'geometria':               'Colegio',
    }

    def sync_items_from_bank_folder(self, bank_dir='items/bank'):
        """Escanea items/bank/*.json, registra cada archivo como curso y sincroniza
        sus ítems sin sobreescribir ratings ELO ya calculados."""
        import json
        import glob as _glob

        if not os.path.isdir(bank_dir):
            return

        json_files = sorted(_glob.glob(os.path.join(bank_dir, '*.json')))
        if not json_files:
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        for filepath in json_files:
            # course_id = nombre del archivo sin extensión (ej: 'algebra_lineal')
            course_id = os.path.splitext(os.path.basename(filepath))[0]

            with open(filepath, 'r', encoding='utf-8') as f:
                items_list = json.load(f)

            if not items_list:
                continue

            # Nombre legible tomado del campo 'topic' del primer ítem
            course_name = items_list[0].get('topic', course_id)
            block = self._COURSE_BLOCK_MAP.get(course_id, 'Universidad')

            # Upsert del curso (nunca sobreescribe si ya existe)
            cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO courses (id, name, block, description) VALUES (?, ?, ?, ?)",
                    (course_id, course_name, block, f"Curso de {course_name}")
                )

            # Sincronizar cada ítem vinculándolo al curso
            for item in items_list:
                cursor.execute("SELECT id FROM items WHERE id = ?", (item['id'],))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO items
                            (id, topic, content, options, correct_option, difficulty, rating_deviation, course_id)
                        VALUES (?, ?, ?, ?, ?, ?, 350.0, ?)
                    ''', (
                        item['id'],
                        item['topic'],
                        item['content'],
                        json.dumps(item['options']),
                        item['correct_option'],
                        item['difficulty'],
                        course_id,
                    ))
                else:
                    # Actualizar contenido/metadatos sin tocar el rating ELO
                    cursor.execute('''
                        UPDATE items
                        SET content = ?, options = ?, correct_option = ?, topic = ?, course_id = ?
                        WHERE id = ?
                    ''', (
                        item['content'],
                        json.dumps(item['options']),
                        item['correct_option'],
                        item['topic'],
                        course_id,
                        item['id'],
                    ))

        conn.commit()
        conn.close()

    def get_courses(self, block=None):
        """Devuelve todos los cursos, opcionalmente filtrados por bloque."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if block:
            cursor.execute(
                "SELECT id, name, block, description FROM courses WHERE block = ? ORDER BY name ASC",
                (block,)
            )
        else:
            cursor.execute("SELECT id, name, block, description FROM courses ORDER BY block ASC, name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'block': r[2], 'description': r[3]} for r in rows]

    def enroll_user(self, user_id, course_id):
        """Matricula a un usuario en un curso. Idempotente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO enrollments (user_id, course_id) VALUES (?, ?)",
            (user_id, course_id)
        )
        conn.commit()
        conn.close()

    def unenroll_user(self, user_id, course_id):
        """Elimina la matrícula de un usuario en un curso."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM enrollments WHERE user_id = ? AND course_id = ?",
            (user_id, course_id)
        )
        conn.commit()
        conn.close()

    def get_user_enrollments(self, user_id):
        """Devuelve los cursos en los que está matriculado el usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.block, c.description
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.user_id = ?
            ORDER BY c.name ASC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'block': r[2], 'description': r[3]} for r in rows]

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

    # ─── Gestión de ÍTEMS (ELO Dinámico) ────────────────────────────────────────

    def sync_items_from_json(self, items_list):
        """Sincroniza el banco de preguntas JSON con la DB. No sobreescribe ratings actuales."""
        conn = self.get_connection()
        cursor = conn.cursor()
        import json
        
        for item in items_list:
            cursor.execute("SELECT id FROM items WHERE id = ?", (item['id'],))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO items (id, topic, content, options, correct_option, difficulty, rating_deviation)
                    VALUES (?, ?, ?, ?, ?, ?, 350.0)
                ''', (
                    item['id'], 
                    item['topic'], 
                    item['content'], 
                    json.dumps(item['options']), 
                    item['correct_option'], 
                    item['difficulty']
                ))
            else:
                # Actualizar contenido y opciones para refrescar LaTeX sin perder el rating
                cursor.execute('''
                    UPDATE items 
                    SET content = ?, options = ?, correct_option = ?, topic = ?
                    WHERE id = ?
                ''', (
                    item['content'], 
                    json.dumps(item['options']), 
                    item['correct_option'], 
                    item['topic'],
                    item['id']
                ))
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
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation FROM items WHERE course_id = ?",
                (course_id,)
            )
        elif topic and topic != "Todos":
            cursor.execute(
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation FROM items WHERE topic = ?",
                (topic,)
            )
        else:
            cursor.execute(
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation FROM items"
            )

        rows = cursor.fetchall()
        conn.close()

        items = []
        for r in rows:
            items.append({
                'id': r[0],
                'topic': r[1],
                'content': r[2],
                'options': json.loads(r[3]),
                'correct_option': r[4],
                'difficulty': r[5],
                'rating_deviation': r[6],
            })
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
                (token, user_id, expires_at.isoformat())
            )
            conn.commit()
        return token

    def validate_session(self, token):
        from datetime import datetime, timezone
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id, expires_at FROM sessions WHERE token = ?",
                (token,)
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

    def save_procedure_submission(self, student_id, item_id, item_content, image_data, mime_type='image/jpeg'):
        """Guarda o reemplaza el procedimiento enviado por el estudiante.
        La imagen se persiste en data/uploads/procedures/ y la ruta se almacena en la DB.
        """
        import time as _time
        ext = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}.get(mime_type, 'jpg')
        os.makedirs(os.path.join('data', 'uploads', 'procedures'), exist_ok=True)
        img_filename = f"{student_id}_{item_id}_{int(_time.time())}.{ext}"
        img_path = os.path.join('data', 'uploads', 'procedures', img_filename)
        with open(img_path, 'wb') as _f:
            _f.write(image_data)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id FROM procedure_submissions WHERE student_id=? AND item_id=?',
            (student_id, item_id),
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute('''
                UPDATE procedure_submissions
                SET image_data=?, mime_type=?, procedure_image_path=?,
                    status='pending', teacher_feedback=NULL,
                    feedback_image=NULL, feedback_image_path=NULL,
                    procedure_score=NULL,
                    submitted_at=CURRENT_TIMESTAMP, reviewed_at=NULL
                WHERE student_id=? AND item_id=?
            ''', (image_data, mime_type, img_path, student_id, item_id))
        else:
            cursor.execute('''
                INSERT INTO procedure_submissions
                    (student_id, item_id, item_content, image_data, mime_type, procedure_image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, item_id, item_content, image_data, mime_type, img_path))
        conn.commit()
        conn.close()

    def get_student_submission(self, student_id, item_id):
        """Retorna la entrega del estudiante para una pregunta, o None."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, status, teacher_feedback, feedback_image,
                   feedback_mime_type, submitted_at, reviewed_at,
                   procedure_score, feedback_image_path
            FROM procedure_submissions
            WHERE student_id=? AND item_id=?
        ''', (student_id, item_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            cols = ['id', 'status', 'teacher_feedback', 'feedback_image',
                    'feedback_mime_type', 'submitted_at', 'reviewed_at',
                    'procedure_score', 'feedback_image_path']
            return dict(zip(cols, row))
        return None

    def get_pending_submissions_count(self, teacher_id):
        """Cuenta las entregas pendientes de revisión del docente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM procedure_submissions ps
            JOIN users u ON ps.student_id = u.id
            JOIN groups g ON u.group_id = g.id
            WHERE g.teacher_id = ? AND ps.status = 'pending'
        ''', (teacher_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_pending_submissions_for_teacher(self, teacher_id):
        """Retorna todas las entregas pendientes de los estudiantes del docente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ps.id, ps.student_id, u.username AS student_name,
                   ps.item_id, ps.item_content, ps.image_data, ps.mime_type,
                   ps.submitted_at, ps.procedure_image_path
            FROM procedure_submissions ps
            JOIN users u ON ps.student_id = u.id
            JOIN groups g ON u.group_id = g.id
            WHERE g.teacher_id = ? AND ps.status = 'pending'
            ORDER BY ps.submitted_at DESC
        ''', (teacher_id,))
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        conn.close()
        return rows

    def save_teacher_feedback(self, submission_id, feedback_text,
                              feedback_image=None, feedback_mime_type=None,
                              procedure_score=None):
        """Guarda la retroalimentación del docente y marca la entrega como revisada.
        Si se adjunta imagen de corrección, se persiste en data/uploads/feedback/.
        """
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
        conn.execute('''
            UPDATE procedure_submissions
            SET teacher_feedback=?, feedback_image=?, feedback_mime_type=?,
                procedure_score=?, feedback_image_path=?,
                status='reviewed', reviewed_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (feedback_text, feedback_image, feedback_mime_type,
              procedure_score, feedback_image_path, submission_id))
        conn.commit()
        conn.close()

