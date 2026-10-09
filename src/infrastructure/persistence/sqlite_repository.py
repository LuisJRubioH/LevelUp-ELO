import json
import os
import sqlite3
import logging
from src.infrastructure.security.hashing_service import HashingService

logger = logging.getLogger(__name__)


# TODO: reemplazar SQLite por DB externa (PostgreSQL, etc.) en producción
def _migrations_enabled() -> bool:
    """Indica si este proceso debe crear esquema, seeds y backfills.

    Por defecto sí, para que desarrollo local y tests no cambien. En
    despliegue se pone RUN_MIGRATIONS=0 en el proceso web y el esquema lo
    aplica un paso previo (scripts/migrate.py): ver _bootstrap_schema().
    """
    return os.environ.get("RUN_MIGRATIONS", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


class SQLiteRepository:
    # Ruta fija — garantiza que todos los datos persistan entre ejecuciones.
    _DEFAULT_DB_PATH = os.path.join("data", "elo_database.db")

    def __init__(self, db_name=None):
        self.db_name = db_name or os.environ.get("DB_PATH", self._DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        self.hashing = HashingService()
        # Parity with PostgresRepository: SQLite has no advisory locks and serialises writers,
        # so no bootstrap step is ever skipped and this stays empty.
        self._skipped_locked_steps: list[str] = []
        if _migrations_enabled():
            self._bootstrap_schema()

    def _bootstrap_schema(self):
        """Esquema, seeds y backfills: un solo paso, fuera del arranque HTTP.

        Sobre el pooler de transacciones de Supabase (puerto 6543) la sesión
        no sobrevive al commit, así que el pg_try_advisory_lock que toma
        _migrate_db() puede terminar liberándose desde otra sesión física.
        Por eso esto corre una sola vez y por conexión directa o pooler de
        sesión — ver scripts/migrate.py y el startCommand de render.yaml.
        """
        self.init_db()
        self._migrate_db()
        self._seed_admin()
        if os.environ.get("ENVIRONMENT", "development").lower() != "production":
            self._seed_demo_data()
        self._backfill_prob_failure()
        self.sync_items_from_bank_folder()
        if os.environ.get("ENVIRONMENT", "development").lower() != "production":
            self._seed_test_students()
        self._reconcile_legacy_ratings()
        self.expire_stale_pvp_matches()

    def bootstrap_skipped_steps(self) -> list[str]:
        """Bootstrap steps skipped because another session held their advisory lock (R17)."""
        return list(self._skipped_locked_steps)

    def get_connection(self, timeout: float = 30.0):
        return sqlite3.connect(self.db_name, timeout=timeout)

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

    def get_student_procedure_submissions(self, student_id, limit: int = 50):
        """Lista los últimos procedimientos enviados por el estudiante con
        estado, score docente, comentario y delta ELO. Usado por la vista
        de Feedback. NUNCA expone respuestas correctas (no aplica a procedimientos)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, item_id, item_content, status, ai_proposed_score,
                   teacher_score, final_score, teacher_feedback, elo_delta,
                   submitted_at, reviewed_at
            FROM procedure_submissions
            WHERE student_id = ?
            ORDER BY submitted_at DESC
            LIMIT ?
            """,
            (student_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "submission_id": r[0],
                "item_id": r[1],
                "item_content": r[2],
                "status": r[3],
                "ai_proposed_score": r[4],
                "teacher_score": r[5],
                "final_score": r[6],
                "teacher_feedback": r[7],
                "elo_delta": r[8],
                "submitted_at": r[9],
                "reviewed_at": r[10],
            }
            for r in rows
        ]

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
        try:
            # First, before any change: an old courses.block CHECK stops the migration.
            self._check_courses_block_constraint(cursor)
        except Exception:
            conn.close()
            raise

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
        # ELO actual del estudiante — se actualiza al responder y al validar procedimientos
        self._add_column_if_not_exists(cursor, "users", "current_elo", "REAL DEFAULT 1000.0")
        # Correo electrónico — NULL para usuarios existentes, UNIQUE parcial (solo no-NULL)
        self._add_column_if_not_exists(cursor, "users", "email", "TEXT")
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email
            ON users(email) WHERE email IS NOT NULL
        """
        )

        # Asegurar índices si no existen
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_teacher ON groups(teacher_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_group ON users(group_id)")
        # Índice compuesto para consultas de intentos por (user_id, topic) y timestamp
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_attempts_user_topic_ts "
            "ON attempts(user_id, topic, timestamp DESC)"
        )

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
        # 1 = intento con tiempo válido (3-600s) → actualiza ELO
        # 0 = adivinanza (<3s) o sesión abandonada (>600s) → no actualiza ELO
        self._add_column_if_not_exists(cursor, "attempts", "elo_valid", "INTEGER DEFAULT 1")
        self._add_column_if_not_exists(cursor, "attempts", "elo_before", "REAL")
        self._add_column_if_not_exists(cursor, "attempts", "request_id", "TEXT")
        self._add_column_if_not_exists(cursor, "attempts", "request_fingerprint", "TEXT")
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_attempts_user_request_id "
            "ON attempts(user_id, request_id) WHERE request_id IS NOT NULL"
        )

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
        # v4b — marca de que elo_delta ya se aplicó al rating canónico
        self._add_column_if_not_exists(
            cursor, "procedure_submissions", "elo_applied", "INTEGER DEFAULT 0"
        )
        # v5 — retroalimentación textual generada por la IA (evaluacion_global del modelo)
        self._add_column_if_not_exists(cursor, "procedure_submissions", "ai_feedback", "TEXT")
        # v6 — hash SHA-256 del archivo subido para detección anti-plagio (T7)
        self._add_column_if_not_exists(cursor, "procedure_submissions", "file_hash", "TEXT")
        # v7b — PostgreSQL runs ALTER TABLE procedure_submissions … DROP NOT NULL on image_data
        # (NULL when the file lives in Storage); SQLite always keeps the bytes: no step here.

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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_procedure_submissions_student_id "
            "ON procedure_submissions(student_id)"
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
        # Bloque temático dentro del curso (p.ej. "Constitución Política" en DIAN)
        self._add_column_if_not_exists(cursor, "items", "block", "TEXT DEFAULT ''")

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

        # ── Tabla achievements (logros/badges del estudiante) ─────────────
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, badge_id)
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_achievements_user
            ON achievements(user_id)
        """
        )

        # ── Tabla student_topic_elo (ELO actual por materia, consultable) ──
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS student_topic_elo (
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                current_elo REAL NOT NULL DEFAULT 1000.0,
                rd REAL NOT NULL DEFAULT 350.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, topic),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_student_topic_elo_topic
            ON student_topic_elo(topic)
        """
        )

        # ── student_course_topic_elo: the only rating state (spec 001, FR-029) ──
        # One row per student × course × topic. REAL is an 8-byte float in SQLite
        # (FR-028i, research R20). origin/approximate record how the row started.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS student_course_topic_elo (
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                current_elo REAL NOT NULL CHECK (current_elo >= 0),
                rd REAL NOT NULL DEFAULT 350 CHECK (rd >= 30 AND rd <= 350),
                origin TEXT NOT NULL CHECK (origin IN ('practice', 'diagnostic',
                    'legacy_topic_row', 'legacy_course_row', 'procedure')),
                approximate INTEGER NOT NULL DEFAULT 0,
                legacy_source_key TEXT,
                reconciled_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, course_id, topic),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_student_course_topic_elo_user_course
            ON student_course_topic_elo(user_id, course_id)
        """
        )

        # ── Tabla exam_sessions (historial de exámenes del estudiante) ────────
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                course_name TEXT NOT NULL DEFAULT '',
                n_questions INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                score_pct REAL NOT NULL,
                global_elo_after REAL NOT NULL DEFAULT 0,
                exam_template_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS active_exam_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                exam_template_id INTEGER,
                item_ids TEXT NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                submitted_at DATETIME,
                result_json TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_active_exam_sessions_user "
            "ON active_exam_sessions(user_id, submitted_at)"
        )

        # ── Tabla exam_templates (plantillas de examen del docente) ──────────
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exam_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                title TEXT NOT NULL,
                time_limit_min INTEGER NOT NULL DEFAULT 20,
                item_ids TEXT NOT NULL DEFAULT '[]',
                archived INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_exam_templates_course "
            "ON exam_templates(course_id, archived)"
        )

        # v7 — Sprint C: examen manual del docente (vincula sessions con templates).
        self._add_column_if_not_exists(cursor, "exam_sessions", "exam_template_id", "INTEGER")
        # Spec 001 (FR-028b): the overall rating's state at submission — 'rated' or 'pending'.
        # NULL = recorded before this column: unknown, never backfilled (see contracts/api.md).
        self._add_column_if_not_exists(
            cursor,
            "exam_sessions",
            "global_elo_status",
            "TEXT CHECK (global_elo_status IN ('rated', 'pending'))",
        )

        # ── Tabla exam_assignments (asignaciones a grupos + ventana de tiempo) ──
        # Sin filas para un template => visible a todos los inscritos al curso
        # (backward-compat con plantillas creadas antes de esta tabla).
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exam_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                starts_at TEXT,
                ends_at TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (template_id, group_id),
                FOREIGN KEY (template_id) REFERENCES exam_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_exam_assignments_template "
            "ON exam_assignments(template_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_exam_assignments_group " "ON exam_assignments(group_id)"
        )

        # ── Tabla exam_responses (respuesta por pregunta de cada examen) ──────
        # Permite el análisis de resultados del docente (pregunta más acertada/
        # fallada, tema a reforzar). El examen sigue siendo evaluativo: estas
        # filas NO afectan el ELO ni la dificultad del ítem.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exam_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                template_id INTEGER,
                user_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                topic TEXT,
                is_correct INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_exam_responses_template "
            "ON exam_responses(template_id)"
        )

        # ── Tabla diagnostics (examen diagnóstico de inicio de materia) ───────
        # Gating: una fila por (estudiante, materia). Marca que ya hizo el
        # diagnóstico, fija el ELO inicial y guarda el desglose por tema.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                initial_elo REAL NOT NULL,
                score_pct REAL NOT NULL,
                result_json TEXT NOT NULL DEFAULT '{}',
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, course_id)
            )
            """
        )

        # Progreso curricular independiente del ELO (nodos de contenido).
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS lesson_progress (
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'available',
                objectives_viewed INTEGER NOT NULL DEFAULT 0,
                math_convention_viewed INTEGER NOT NULL DEFAULT 0,
                viewed_at DATETIME,
                completed_at DATETIME,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, course_id, node_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Respuestas cerradas de lecciones; por diseño no admite texto libre.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS lesson_interactions (
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                interaction_id TEXT NOT NULL,
                selected_option TEXT NOT NULL,
                is_expected INTEGER,
                misconception_tag TEXT,
                answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, course_id, node_id, interaction_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # ── Tablas PvP (ligas en tiempo real) ────────────────────────────────
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pvp_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT NOT NULL,
                player1_id INTEGER NOT NULL,
                player2_id INTEGER NOT NULL,
                item_ids TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'active',
                winner_id INTEGER,
                score_p1 INTEGER NOT NULL DEFAULT 0,
                score_p2 INTEGER NOT NULL DEFAULT 0,
                elo_delta_p1 REAL,
                elo_delta_p2 REAL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                finished_at DATETIME,
                FOREIGN KEY(player1_id) REFERENCES users(id),
                FOREIGN KEY(player2_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pvp_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                is_correct INTEGER NOT NULL DEFAULT 0,
                answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(match_id) REFERENCES pvp_matches(id)
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pvp_matches_players "
            "ON pvp_matches(player1_id, player2_id)"
        )
        # NULL = applied normally; 'no_rated_topics' = applied 0 (spec 001, FR-029c).
        self._add_column_if_not_exists(cursor, "pvp_matches", "elo_reason_p1", "TEXT")
        self._add_column_if_not_exists(cursor, "pvp_matches", "elo_reason_p2", "TEXT")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pvp_answers_match " "ON pvp_answers(match_id, user_id)"
        )

        conn.commit()
        conn.close()

    def _check_courses_block_constraint(self, cursor):
        """Read-only: the courses.block CHECK must accept the four blocks (spec 001 FR-028n).

        No DDL either way. Widening it would mean rebuilding the table — not additive (AGENTS
        R8), and the old rename-based rebuild left other tables' foreign keys on a dropped
        table — so a constraint that lacks a block stops the migration instead.
        """
        from src.infrastructure.persistence.course_blocks import require_course_blocks

        row = cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'courses'"
        ).fetchone()
        # A new database has no courses table yet: this migration creates it below.
        require_course_blocks(row[0] if row else "")

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
        - Concursante: concursante1 / demo1234 (DIAN — preparación concurso público)

        Se crean grupos vinculados a cursos reales con cada estudiante
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
            ("Grupo Demo - DIAN", "DIAN"),
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
            ("concursante1", "concursos", "DIAN"),
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
        self,
        username,
        password,
        role="student",
        group_id=None,
        education_level=None,
        grade=None,
        email=None,
    ):
        """Registra un nuevo usuario.

        Para estudiantes, `group_id` es opcional en el momento del registro:
        el estudiante elige grupo al matricularse en un curso (catálogo).
        `education_level` determina qué catálogo de cursos podrá ver.
        `grade` solo aplica cuando education_level = 'semillero' ('6'–'11').
        `email` opcional — si se provee, se valida formato y unicidad.
        """
        # Validación backend de contraseña (no confiar solo en la UI)
        if not password or not password.strip():
            return False, "La contraseña es obligatoria."
        if len(password.strip()) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres."
        # Semillero sin grado 6–11 no tiene catálogo: no se registra (spec 001 FR-028m).
        from src.domain.entities import valid_semillero_grade

        if education_level == "semillero" and not valid_semillero_grade(grade):
            return False, "Semillero requiere un grado de 6.º a 11.º."
        # Validar email si se provee
        if email is not None:
            email = email.strip() or None
        if email is not None:
            if not self._valid_email_format(email):
                return False, "Formato de correo inválido."
            if self.email_exists(email):
                return False, "Este correo ya está registrado."
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hashing.hash_password(password)
            # Teachers necesitan aprobación; students y admin se aprueban solos
            approved = 0 if role == "teacher" else 1
            _grade = str(grade) if education_level == "semillero" else None
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved, group_id, "
                "rating_deviation, education_level, grade, email) "
                "VALUES (?, ?, ?, ?, ?, 350.0, ?, ?, ?)",
                (username, password_hash, role, approved, group_id, education_level, _grade, email),
            )
            conn.commit()
            return True, "Registro exitoso."
        except sqlite3.IntegrityError:
            return False, "Error: El nombre de usuario ya existe."
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> dict | None:
        """Retorna datos básicos de un usuario por su ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, group_id, education_level, current_elo, active, approved "
            "FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "role": row[2],
            "group_id": row[3],
            "education_level": row[4],
            "current_elo": row[5],
            "active": bool(row[6]),
            "approved": bool(row[7]),
        }

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Buscar por username O email
        cursor.execute(
            "SELECT id, username, role, approved, password_hash "
            "FROM users WHERE (username = ? OR (email = ? AND email IS NOT NULL)) AND active = 1 "
            "LIMIT 1",
            (username, username),
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

    # ── Email helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _valid_email_format(email: str) -> bool:
        import re

        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    def get_user_by_login(self, login: str):
        """Busca usuario por username O email. Retorna misma tupla que login_user (sin verificar password)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, approved, password_hash "
            "FROM users WHERE (username = ? OR (email = ? AND email IS NOT NULL)) AND active = 1 "
            "LIMIT 1",
            (login, login),
        )
        row = cursor.fetchone()
        conn.close()
        return row  # (id, username, role, approved, password_hash) | None

    def email_exists(self, email: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE email = ? AND email IS NOT NULL",
            (email,),
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def update_user_email(self, user_id: int, email: str) -> None:
        if not self._valid_email_format(email):
            raise ValueError("Formato de correo inválido")
        if self.email_exists(email):
            raise ValueError("Este correo ya está registrado")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        conn.commit()
        conn.close()

    def _set_course_topic_rating(self, cursor, user_id, course_id, topic, elo, rd, origin):
        """Write one (course, topic) rating; `origin` is kept from the row's first writer."""
        cursor.execute(
            """
            INSERT INTO student_course_topic_elo
                (user_id, course_id, topic, current_elo, rd, origin, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, course_id, topic) DO UPDATE
                SET current_elo = excluded.current_elo,
                    rd = excluded.rd,
                    updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, course_id, topic, float(elo), float(rd), origin),
        )

    def _bump_course_topic_rating(self, cursor, user_id, course_id, topic, delta, origin):
        """Add a domain-computed delta atomically, floor 0 (research R3: persistence, not
        arithmetic). An absent row starts from 1000 + delta with this `origin`."""
        cursor.execute(
            """
            INSERT INTO student_course_topic_elo
                (user_id, course_id, topic, current_elo, rd, origin, updated_at)
            VALUES (?, ?, ?, ?, 350.0, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, course_id, topic) DO UPDATE
                SET current_elo = MAX(0, student_course_topic_elo.current_elo + ?),
                    updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, course_id, topic, max(0.0, 1000.0 + float(delta)), origin, float(delta)),
        )

    def save_answer_transaction(
        self,
        user_id: int,
        item_id: str,
        compute,
        request_id: str | None = None,
        request_fingerprint: str | None = None,
    ) -> bool:
        """Unit of work of one answer: lock, read, compute, persist (spec 001, FR-010, FR-029).

        The rating is the item's own (course, topic) row. `compute` is the domain calculation:

            compute({"elo", "rd", "item_difficulty", "item_rd", "course_id", "topic"})
                -> (attempt_data, item_difficulty_new, item_rd_new)

        It runs on the locked state and must not do I/O. The attempt is always stored; the
        rating and the item move only when `attempt_data["elo_valid"]` (FR-008, FR-008a).
        Returns False when `request_id` was already recorded (a client retry).
        """
        conn = self.get_connection()
        # Transacción explícita gestionada aquí, no por el autocommit de sqlite3.
        conn.isolation_level = None
        cursor = conn.cursor()
        try:
            # BEGIN IMMEDIATE bloquea la escritura ANTES de leer, así que el
            # ciclo leer→calcular→escribir queda serializado entre respuestas.
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(
                "SELECT difficulty, rating_deviation, course_id, topic FROM items WHERE id = ?",
                (item_id,),
            )
            item = cursor.fetchone()
            if item is None:
                raise ValueError("Ítem '%s' no encontrado." % item_id)
            difficulty, item_rd, course_id, topic = item
            cursor.execute(
                "SELECT current_elo, rd FROM student_course_topic_elo"
                " WHERE user_id = ? AND course_id = ? AND topic = ?",
                (user_id, course_id, topic),
            )
            rating = cursor.fetchone()

            attempt_data, item_difficulty_new, item_rd_new = compute(
                {
                    "elo": float(rating[0]) if rating else 1000.0,
                    "rd": float(rating[1]) if rating else 350.0,
                    "item_difficulty": float(difficulty),
                    "item_rd": float(item_rd or 350.0),
                    "course_id": course_id,
                    "topic": topic,
                }
            )
            elo_valid = bool(attempt_data["elo_valid"])

            # Siempre registrar el intento
            cursor.execute(
                """INSERT INTO attempts
                   (user_id, item_id, is_correct, difficulty, topic, elo_after,
                    prob_failure, expected_score, time_taken, confidence_score,
                    error_type, rating_deviation, elo_valid, elo_before,
                    request_id, request_fingerprint)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, request_id) WHERE request_id IS NOT NULL DO NOTHING""",
                (
                    user_id,
                    item_id,
                    1 if attempt_data["is_correct"] else 0,
                    attempt_data.get("difficulty"),
                    topic,
                    attempt_data["elo_after"],
                    attempt_data.get("prob_failure"),
                    attempt_data.get("expected_score"),
                    attempt_data.get("time_taken"),
                    attempt_data.get("confidence_score"),
                    attempt_data.get("error_type"),
                    attempt_data.get("rating_deviation"),
                    1 if elo_valid else 0,
                    attempt_data.get("elo_before"),
                    request_id,
                    request_fingerprint,
                ),
            )
            inserted = cursor.rowcount == 1
            if inserted and elo_valid:
                cursor.execute(
                    "UPDATE items SET difficulty = ?, rating_deviation = ? WHERE id = ?",
                    (item_difficulty_new, item_rd_new, item_id),
                )
                self._set_course_topic_rating(
                    cursor,
                    user_id,
                    course_id,
                    topic,
                    attempt_data["elo_after"],
                    attempt_data["rating_deviation"],
                    "practice",
                )
            conn.commit()
            return inserted
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_answer_by_request_id(self, user_id: int, request_id: str) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT item_id, is_correct, elo_before, elo_after, rating_deviation, "
            "request_fingerprint, elo_valid FROM attempts WHERE user_id=? AND request_id=?",
            (user_id, request_id),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "item_id": row[0],
            "is_correct": bool(row[1]),
            "elo_before": row[2],
            "elo_after": row[3],
            "rating_deviation": row[4],
            "request_fingerprint": row[5],
            "elo_valid": bool(row[6]),
        }

    def get_all_attempts_for_calibration(
        self,
        education_level: str = None,
        exclude_test_users: bool = True,
    ) -> list:
        """Retorna intentos filtrados para calibración ML.

        Filtra elo_valid=1 y opcionalmente is_test_user=0.
        luisito-s y torieg (is_test_user=1) siempre excluidos en análisis.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            params = []
            where = ["a.elo_valid = 1"]
            if exclude_test_users:
                where.append("COALESCE(u.is_test_user, 0) = 0")
            if education_level:
                where.append("u.education_level = ?")
                params.append(education_level)
            cursor.execute(
                f"""SELECT a.id, a.user_id, a.item_id, a.is_correct,
                           a.expected_score, a.elo_valid, a.time_taken,
                           u.education_level
                    FROM attempts a
                    JOIN users u ON a.user_id = u.id
                    WHERE {' AND '.join(where)}
                    ORDER BY a.timestamp""",
                params,
            )
            return [dict(row) for row in cursor.fetchall()]
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

    def get_activity_heatmap(self, user_id: int, days: int = 70) -> dict:
        """Retorna {date: count} con el número de intentos por día (últimos N días)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DATE(timestamp) AS d, COUNT(*) AS cnt
            FROM attempts
            WHERE user_id = ? AND timestamp >= DATE('now', ? || ' days')
            GROUP BY d
        """,
            (user_id, f"-{days}"),
        )
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

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

    def get_audit_group_changes(self, limit: int = 100) -> list:
        """Devuelve las reasignaciones de grupo auditadas, más recientes primero."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.student_id, s.username AS student_username,
                   a.old_group_id, og.name AS old_group_name,
                   a.new_group_id, ng.name AS new_group_name,
                   a.admin_id, ad.username AS admin_username,
                   a.timestamp
            FROM audit_group_changes a
            LEFT JOIN users s ON s.id = a.student_id
            LEFT JOIN users ad ON ad.id = a.admin_id
            LEFT JOIN groups og ON og.id = a.old_group_id
            LEFT JOIN groups ng ON ng.id = a.new_group_id
            ORDER BY a.timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

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
            WHERE g.teacher_id = ?
              AND COALESCE(u.is_test_user, 0) = 0
              {_filter}
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

    def save_weekly_ranking(self, group_id, rows):
        """Store `rows` (RatingReadService.ranking_view(scope="weekly") entries) as this week's
        snapshot (FR-028g). `rank` is the competition rank; pending rows (no rank) are not stored.
        Idempotent per week + group + user."""
        from datetime import date, timedelta

        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # lunes
        week_end = week_start + timedelta(days=6)  # domingo
        conn = self.get_connection()
        try:
            for r in rows:
                if r["rank"] is None:
                    continue
                conn.execute(
                    """INSERT OR IGNORE INTO weekly_rankings
                       (week_start, week_end, group_id, rank, user_id, username, global_elo,
                        attempts_count)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        str(week_start),
                        str(week_end),
                        group_id,
                        r["rank"],
                        r["user_id"],
                        r["username"],
                        r["rating"],
                        r["attempts_in_window"],
                    ),
                )
            conn.commit()
        finally:
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

    def get_total_attempts_count(self, user_id):
        """Retorna el número total de intentos de un estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attempts WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_latest_attempts(self, user_id, limit=20):
        """Retorna los últimos N intentos con el resultado real, esperado, ELO y timestamp."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT is_correct, expected_score, prob_failure, elo_after, timestamp
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
        for is_correct, expected, prob_fail, elo_after, timestamp in rows:
            actual = 1.0 if is_correct else 0.0
            # Si expected_score es NULL (intentos viejos), lo derivamos de prob_failure
            if expected is None and prob_fail is not None:
                expected = 1.0 - prob_fail
            elif expected is None:
                expected = 0.5  # Valor neutro por defecto si no hay datos

            results.append(
                {
                    "actual": actual,
                    "expected": expected,
                    "elo_after": elo_after,
                    "timestamp": str(timestamp)[:10] if timestamp else None,
                }
            )
        return results

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

    # ── Spec 001: raw rating rows and ranking participants ───────────────────
    # Raw rows only: no averaging, rounding or ordering by rating (constitution III).

    def get_course_topic_ratings(self, user_id, course_id=None):
        """Rows of student_course_topic_elo for one student (never the legacy store)."""
        rows = self.get_course_topic_ratings_bulk([user_id], course_id)
        return [{k: v for k, v in r.items() if k != "user_id"} for r in rows]

    def get_course_topic_ratings_bulk(self, user_ids, course_id=None):
        if not user_ids:
            return []
        marks = ", ".join("?" for _ in user_ids)
        query = (
            "SELECT user_id, course_id, topic, current_elo, rd, origin, approximate"
            f" FROM student_course_topic_elo WHERE user_id IN ({marks})"
        )
        params = list(user_ids)
        if course_id is not None:
            query += " AND course_id = ?"
            params.append(course_id)
        conn = self.get_connection()
        try:
            rows = conn.execute(query + " ORDER BY user_id, course_id, topic", params).fetchall()
        finally:
            conn.close()
        return [
            {
                "user_id": r[0],
                "course_id": r[1],
                "topic": r[2],
                "elo": float(r[3]),
                "rd": float(r[4]),
                "origin": r[5],
                "approximate": bool(r[6]),
            }
            for r in rows
        ]

    def get_current_context_course_ids(self, user_id):
        """Enrolled courses in the catalogue of the student's current level and grade."""
        return self.get_current_context_course_ids_bulk([user_id])[user_id]

    def get_current_context_course_ids_bulk(self, user_ids):
        from src.domain.entities import in_catalogue

        result = {user_id: [] for user_id in user_ids}
        if not user_ids:
            return result
        marks = ", ".join("?" for _ in user_ids)
        conn = self.get_connection()
        try:
            rows = conn.execute(
                "SELECT e.user_id, e.course_id, c.block, u.education_level, u.grade"
                " FROM enrollments e JOIN courses c ON c.id = e.course_id"
                " JOIN users u ON u.id = e.user_id"
                f" WHERE e.user_id IN ({marks}) ORDER BY e.user_id, e.course_id",
                list(user_ids),
            ).fetchall()
        finally:
            conn.close()
        for user_id, course_id, block, level, grade in rows:
            if in_catalogue(level, grade, course_id, block):
                result[user_id].append(course_id)
        return result

    def get_ranking_participants(
        self,
        scope,
        group_id=None,
        course_id=None,
        education_level=None,
        grade=None,
        window_days=7,
    ):
        """Who appears in a ranking (FR-028f) — never what they are ranked by."""
        conn = self.get_connection()
        try:
            if scope == "group":
                rows = conn.execute(
                    "SELECT id, username FROM users"
                    " WHERE group_id = ? AND role = 'student' AND active = 1 ORDER BY id",
                    (group_id,),
                ).fetchall()
                return [{"user_id": r[0], "username": r[1], "attempts_in_window": 0} for r in rows]
            where = ["u.role = 'student'", "a.timestamp >= datetime('now', ?)"]
            params = ["-%d days" % int(window_days)]
            if scope == "weekly":
                where.append("u.group_id = ?")
                params.append(group_id)
            elif scope == "global":
                if education_level:
                    where.append("u.education_level = ?")
                    params.append(education_level)
                if grade:
                    where.append("u.grade = ?")
                    params.append(grade)
            elif scope != "course" or course_id is None:
                raise ValueError(f"Unknown ranking scope {scope!r} or missing course_id.")
            join = ""
            if course_id is not None and scope in ("course", "weekly"):
                join = " JOIN items i ON i.id = a.item_id"
                where.append("i.course_id = ?")
                params.append(course_id)
            rows = conn.execute(
                "SELECT u.id, u.username, COUNT(a.id) FROM attempts a"
                f" JOIN users u ON u.id = a.user_id{join} WHERE {' AND '.join(where)}"
                " GROUP BY u.id, u.username ORDER BY u.id",
                params,
            ).fetchall()
        finally:
            conn.close()
        return [{"user_id": r[0], "username": r[1], "attempts_in_window": r[2]} for r in rows]

    def get_group_course_id(self, group_id):
        conn = self.get_connection()
        try:
            row = conn.execute("SELECT course_id FROM groups WHERE id = ?", (group_id,)).fetchone()
        finally:
            conn.close()
        return row[0] if row else None

    def _reconcile_legacy_ratings(self) -> int:
        """One-time, idempotent: approximate baselines from legacy rows (spec 001, research R10).

        Reads raw rows, lets the domain plan which (course, topic) ratings to create, inserts
        them with ON CONFLICT DO NOTHING. Legacy rows are never changed. Returns rows created.
        """
        from src.domain.elo.reconciliation import plan_reconciliation

        conn = self.get_connection()
        try:
            legacy, attempts, diagnostics, topics, names, existing = (
                conn.execute(query).fetchall()
                for query in (
                    "SELECT user_id, topic, current_elo, rd, updated_at FROM student_topic_elo",
                    "SELECT DISTINCT a.user_id, i.course_id, i.topic, a.topic AS rating_key FROM attempts a"
                    " JOIN items i ON i.id = a.item_id WHERE a.topic IS NOT NULL",
                    "SELECT user_id, course_id FROM diagnostics",
                    "SELECT DISTINCT course_id, topic FROM items WHERE course_id IS NOT NULL",
                    "SELECT id, name FROM courses",
                    "SELECT user_id, course_id, topic FROM student_course_topic_elo",
                )
            )
            rows = plan_reconciliation(legacy, attempts, diagnostics, topics, dict(names), existing)
            created = 0
            for r in rows:
                cursor = conn.execute(
                    """INSERT INTO student_course_topic_elo
                       (user_id, course_id, topic, current_elo, rd, origin, approximate,
                        legacy_source_key, reconciled_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                       ON CONFLICT (user_id, course_id, topic) DO NOTHING""",
                    (
                        r["user_id"],
                        r["course_id"],
                        r["topic"],
                        r["elo"],
                        r["rd"],
                        r["origin"],
                        r["legacy_source_key"],
                    ),
                )
                created += cursor.rowcount
            conn.commit()
            return created
        finally:
            conn.close()

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

        Returns (True, msg, group_id) si fue creado, (False, msg, None) si hay error.
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
            return True, f"Grupo '{name}' creado exitosamente.", cursor.lastrowid
        except sqlite3.IntegrityError:
            return False, "Ya existe un grupo con ese nombre.", None
        finally:
            conn.close()

    def get_groups_by_teacher(self, teacher_id):
        """Lista grupos de un profesor con el nombre y bloque del curso vinculado (JOIN)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT g.id AS group_id, g.name, g.course_id, COALESCE(c.name, '—') AS course_name,
                   g.created_at, COALESCE(c.block, 'Universidad') AS block, g.invite_code,
                   (SELECT COUNT(*) FROM users u2
                    WHERE u2.group_id = g.id AND u2.active = 1 AND u2.role = 'student'
                      AND COALESCE(u2.is_test_user, 0) = 0) AS student_count
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
                "group_id": r[0],
                "name": r[1],
                "course_id": r[2],
                "course_name": r[3],
                "created_at": r[4],
                "block": r[5],
                "invite_code": r[6],
                "student_count": r[7],
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
                       (SELECT COUNT(DISTINCT e.user_id) FROM enrollments e WHERE e.group_id = g.id) AS student_count
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
                       (SELECT COUNT(DISTINCT e.user_id) FROM enrollments e WHERE e.group_id = g.id) AS student_count
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

    def get_teacher_dashboard_stats(self, teacher_id):
        """Retorna estadísticas consolidadas por estudiante para el dashboard docente.

        Un estudiante aparece UNA sola vez, sin importar cuántos cursos
        tenga matriculados. Se usa su grupo primario (users.group_id).
        Incluye ELO actual, intentos totales, acierto promedio y última actividad.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            WITH teacher_student_ids AS (
                SELECT DISTINCT u.id AS user_id
                FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = ? AND u.active = 1 AND u.role = 'student'
                  AND COALESCE(u.is_test_user, 0) = 0

                UNION

                SELECT DISTINCT e.user_id
                FROM enrollments e
                JOIN groups g ON e.group_id = g.id
                JOIN users u ON e.user_id = u.id
                WHERE g.teacher_id = ? AND u.active = 1 AND u.role = 'student'
                  AND COALESCE(u.is_test_user, 0) = 0
            )
            SELECT u.id AS user_id, u.username, u.education_level,
                   u.group_id, COALESCE(g.name, 'Sin grupo') AS group_name,
                   COUNT(a.id) AS total_attempts,
                   CASE WHEN COUNT(a.id) > 0
                        THEN CAST(SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS REAL) / COUNT(a.id)
                        ELSE 0.0 END AS accuracy,
                   MAX(a.timestamp) AS last_activity
            FROM teacher_student_ids ts
            JOIN users u ON u.id = ts.user_id
            LEFT JOIN groups g ON u.group_id = g.id
            LEFT JOIN attempts a ON a.user_id = ts.user_id
            GROUP BY u.id, u.username, u.education_level, u.group_id, g.name
            ORDER BY u.username ASC
        """,
            (teacher_id, teacher_id),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "user_id": r[0],
                "username": r[1],
                "education_level": r[2],
                "group_id": r[3],
                "group_name": r[4],
                "total_attempts": int(r[5]),
                "accuracy": float(r[6]),
                "last_activity": str(r[7])[:10] if r[7] else None,
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

    def get_teacher_metrics(self, teacher_id):
        """Métricas de uso del grupo del docente: tiempo promedio, abandono, temas, actividad diaria."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cte = """
            WITH teacher_students AS (
                SELECT DISTINCT u.id AS user_id
                FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = ? AND u.active = 1 AND u.role = 'student'
                  AND COALESCE(u.is_test_user, 0) = 0
                UNION
                SELECT DISTINCT e.user_id
                FROM enrollments e
                JOIN groups g ON e.group_id = g.id
                JOIN users u ON e.user_id = u.id
                WHERE g.teacher_id = ? AND u.active = 1 AND u.role = 'student'
                  AND COALESCE(u.is_test_user, 0) = 0
            )
        """
        cursor.execute(
            cte
            + """
            SELECT
                COUNT(*) AS total_attempts,
                AVG(CASE WHEN a.time_taken BETWEEN 3 AND 600 THEN a.time_taken END) AS avg_time,
                CAST(SUM(CASE WHEN a.time_taken IS NOT NULL
                              AND (a.time_taken < 3 OR a.time_taken > 600) THEN 1 ELSE 0 END)
                     AS REAL) / NULLIF(COUNT(*), 0) AS abandonment_rate
            FROM attempts a
            JOIN teacher_students ts ON a.user_id = ts.user_id
        """,
            (teacher_id, teacher_id),
        )
        row = cursor.fetchone()
        totals = {
            "total_attempts": int(row[0] or 0),
            "avg_time_seconds": round(float(row[1] or 0), 1),
            "abandonment_rate": round(float(row[2] or 0), 4),
        }

        cursor.execute(
            cte
            + """
            SELECT a.topic,
                   COUNT(*) AS attempts,
                   CAST(SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS REAL) / COUNT(*) AS accuracy,
                   AVG(CASE WHEN a.time_taken BETWEEN 3 AND 600 THEN a.time_taken END) AS avg_time
            FROM attempts a
            JOIN teacher_students ts ON a.user_id = ts.user_id
            WHERE a.topic IS NOT NULL AND a.topic != ''
            GROUP BY a.topic
            ORDER BY attempts DESC
            LIMIT 10
        """,
            (teacher_id, teacher_id),
        )
        topic_stats = [
            {
                "topic": r[0],
                "attempts": int(r[1]),
                "accuracy": round(float(r[2] or 0), 3),
                "avg_time": round(float(r[3] or 0), 1),
            }
            for r in cursor.fetchall()
        ]

        cursor.execute(
            cte
            + """
            SELECT strftime('%Y-%m-%d', a.timestamp) AS date, COUNT(*) AS count
            FROM attempts a
            JOIN teacher_students ts ON a.user_id = ts.user_id
            WHERE a.timestamp >= date('now', '-30 days')
            GROUP BY date
            ORDER BY date ASC
        """,
            (teacher_id, teacher_id),
        )
        daily_attempts = [{"date": r[0], "count": int(r[1])} for r in cursor.fetchall()]

        cursor.execute(
            cte
            + """
            SELECT CAST(strftime('%H', a.timestamp) AS INTEGER) AS hour, COUNT(*) AS count
            FROM attempts a
            JOIN teacher_students ts ON a.user_id = ts.user_id
            GROUP BY hour
            ORDER BY hour ASC
        """,
            (teacher_id, teacher_id),
        )
        hourly = {r[0]: int(r[1]) for r in cursor.fetchall()}
        hourly_distribution = [{"hour": h, "count": hourly.get(h, 0)} for h in range(24)]

        conn.close()
        return {
            **totals,
            "topic_stats": topic_stats,
            "daily_attempts": daily_attempts,
            "hourly_distribution": hourly_distribution,
        }

    def export_teacher_student_data(self, teacher_id, group_id=None):
        """Exporta datos de intentos de los estudiantes del profesor para análisis externo.

        Cada intento aparece UNA sola vez. Incluye columna 'cursos_matriculados'
        con la lista de cursos del estudiante (separados por coma).
        Si group_id se proporciona, filtra solo ese grupo.
        """
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        _gf1 = "AND g.id = ?" if group_id else ""
        _gf2 = "AND g2.id = ?" if group_id else ""
        _params = [teacher_id]
        if group_id:
            _params.append(group_id)
        _params.append(teacher_id)
        if group_id:
            _params.append(group_id)

        cursor.execute(
            f"""
            WITH teacher_student_ids AS (
                SELECT DISTINCT u.id AS user_id
                FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE g.teacher_id = ? AND u.active = 1 AND u.role = 'student'
                  AND COALESCE(u.is_test_user, 0) = 0
                  {_gf1}

                UNION

                SELECT DISTINCT e.user_id
                FROM enrollments e
                JOIN groups g ON e.group_id = g.id
                JOIN users u ON e.user_id = u.id
                WHERE g.teacher_id = ? AND u.active = 1 AND u.role = 'student'
                  AND COALESCE(u.is_test_user, 0) = 0
                  {_gf2}
            )
            SELECT
                u.id AS student_id,
                u.username,
                u.education_level,
                u.grade,
                COALESCE(pg.name, 'Sin grupo') AS group_name,
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
                i.tags AS item_tags,
                COALESCE(
                    (SELECT GROUP_CONCAT(DISTINCT c2.name)
                     FROM enrollments e2
                     LEFT JOIN courses c2 ON e2.course_id = c2.id
                     WHERE e2.user_id = u.id),
                    ''
                ) AS cursos_matriculados
            FROM teacher_student_ids ts
            JOIN users u ON u.id = ts.user_id
            LEFT JOIN groups pg ON u.group_id = pg.id
            JOIN attempts a ON a.user_id = ts.user_id
            JOIN items i ON a.item_id = i.id
            LEFT JOIN courses c ON i.course_id = c.id
            ORDER BY u.username ASC, a.timestamp ASC
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
              AND COALESCE(u.is_test_user, 0) = 0
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
              AND COALESCE(u.is_test_user, 0) = 0
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
        "evaluar_para_avanzar_8": "Colegio",
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
        "evaluar_para_avanzar_8": "Evaluar para Avanzar — Matemáticas 8.°",
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
                            (id, topic, content, options, correct_option, difficulty, rating_deviation, course_id, image_url, tags, block)
                        VALUES (?, ?, ?, ?, ?, ?, 350.0, ?, ?, ?, ?)
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
                            item.get("block", ""),
                        ),
                    )
                else:
                    # Actualizar contenido/metadatos sin tocar el rating ELO
                    cursor.execute(
                        """
                        UPDATE items
                        SET content = ?, options = ?, correct_option = ?, topic = ?, course_id = ?, image_url = ?, tags = ?, block = ?
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
                            item.get("block", ""),
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
        """The catalogue of a level — for semillero, of the grade (spec 001 FR-028k).

        The courses of the level's block, kept by the domain rule `in_catalogue`: a semillero
        grade *g* gives the `*_semillero_g` courses, and no grade gives none. An unknown level
        falls back to universidad.
        """
        from src.domain.entities import LEVEL_TO_BLOCK, LEVEL_UNIVERSIDAD, in_catalogue

        level = (level or LEVEL_UNIVERSIDAD).lower()
        block = LEVEL_TO_BLOCK.get(level, LEVEL_TO_BLOCK[LEVEL_UNIVERSIDAD])
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, block, description FROM courses WHERE block = ? ORDER BY name ASC",
            (block,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {"id": r[0], "name": r[1], "block": r[2], "description": r[3]}
            for r in rows
            if in_catalogue(level, grade, r[0], r[2])
        ]

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

    def get_items_from_db(self, topic=None, course_id=None, block=None):
        """Obtiene ítems desde la base de datos.
        Prioridad de filtro: course_id [+ block] > topic > sin filtro."""
        conn = self.get_connection()
        cursor = conn.cursor()
        import json

        if course_id and block:
            cursor.execute(
                "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url, tags FROM items WHERE course_id = ? AND block = ?",
                (course_id, block),
            )
        elif course_id:
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

    def get_course_blocks(self, course_id: str) -> list[dict]:
        """Retorna los bloques temáticos de un curso con su conteo de ítems."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT block, COUNT(*) FROM items WHERE course_id = ? AND block != '' GROUP BY block ORDER BY block ASC",
            (course_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"block": r[0], "item_count": r[1]} for r in rows]

    # ── PvP ──────────────────────────────────────────────────────────────────

    def create_pvp_match(self, course_id: str, p1: int, p2: int, item_ids: list[str]) -> int:
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pvp_matches (course_id, player1_id, player2_id, item_ids) VALUES (?,?,?,?)",
            (course_id, p1, p2, json.dumps(item_ids)),
        )
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return match_id

    def save_pvp_answer(self, match_id: int, user_id: int, item_id: str, is_correct: bool) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pvp_answers (match_id, user_id, item_id, is_correct) VALUES (?,?,?,?)",
            (match_id, user_id, item_id, int(is_correct)),
        )
        conn.commit()
        conn.close()

    def finish_pvp_match(
        self,
        match_id: int,
        winner_id: int | None,
        score_p1: int,
        score_p2: int,
        elo_delta_p1: float,
        elo_delta_p2: float,
        p1_id: int,
        p2_id: int,
    ) -> dict | None:
        """Close an active match once and apply each player's delta (FR-025, FR-029b, FR-029c).

        The delta goes to every rated topic of the match's course (atomic addition, floor 0).
        A player with no rated topic there gets 0 with reason 'no_rated_topics'. Returns
        {"p1": (applied, reason), "p2": (applied, reason)}, or None when the match was not
        active (closed already: nothing changes).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # La guarda de status hace el cierre idempotente: si el timer y el
            # último jugador disparan a la vez, el ELO se aplica una sola vez.
            cursor.execute(
                """UPDATE pvp_matches SET status='finished', winner_id=?, score_p1=?, score_p2=?,
                   finished_at=CURRENT_TIMESTAMP
                   WHERE id=? AND status='active'
                   RETURNING course_id""",
                (winner_id, score_p1, score_p2, match_id),
            )
            row = cursor.fetchone()
            if row is None:
                conn.commit()
                return None
            applied = {}
            for key, player, delta in (("p1", p1_id, elo_delta_p1), ("p2", p2_id, elo_delta_p2)):
                cursor.execute(
                    """UPDATE student_course_topic_elo
                       SET current_elo = MAX(0, current_elo + ?), updated_at = CURRENT_TIMESTAMP
                       WHERE user_id = ? AND course_id = ?""",
                    (float(delta), player, row[0]),
                )
                applied[key] = (float(delta), None) if cursor.rowcount else (0.0, "no_rated_topics")
            cursor.execute(
                """UPDATE pvp_matches SET elo_delta_p1=?, elo_reason_p1=?,
                   elo_delta_p2=?, elo_reason_p2=? WHERE id=?""",
                (*applied["p1"], *applied["p2"], match_id),
            )
            conn.commit()
            return applied
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def expire_stale_pvp_matches(self, max_age_seconds: int = 600) -> int:
        """Cierra partidas que quedaron 'active' sin que nadie las terminara.

        Una partida dura 180s y su cronómetro vive en el proceso que la creó:
        un reinicio lo pierde y la fila se queda activa para siempre, invisible
        en el historial (que filtra status='finished'). Se marcan 'abandoned'
        y no tocan ELO — nadie ganó. Devuelve cuántas se cerraron.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pvp_matches SET status='abandoned', finished_at=CURRENT_TIMESTAMP
            WHERE status='active'
              AND started_at < datetime('now', ?)
            """,
            ("-%d seconds" % max_age_seconds,),
        )
        closed = cursor.rowcount
        conn.commit()
        conn.close()
        if closed:
            logger.info("Partidas PvP huérfanas cerradas: %d", closed)
        return closed

    def get_pvp_history(self, user_id: int, limit: int = 20) -> list[dict]:
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.id, m.course_id, m.winner_id, m.score_p1, m.score_p2,
                   m.elo_delta_p1, m.elo_delta_p2, m.started_at, m.finished_at,
                   m.player1_id, m.player2_id,
                   u1.username as p1_name, u2.username as p2_name
            FROM pvp_matches m
            JOIN users u1 ON u1.id = m.player1_id
            JOIN users u2 ON u2.id = m.player2_id
            WHERE (m.player1_id = ? OR m.player2_id = ?) AND m.status = 'finished'
            ORDER BY m.finished_at DESC LIMIT ?
            """,
            (user_id, user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        results = []
        for r in rows:
            is_p1 = r[9] == user_id
            results.append(
                {
                    "match_id": r[0],
                    "course_id": r[1],
                    "won": r[2] == user_id,
                    "draw": r[2] is None,
                    "my_score": r[3] if is_p1 else r[4],
                    "opp_score": r[4] if is_p1 else r[3],
                    "elo_delta": r[5] if is_p1 else r[6],
                    "opponent": r[12] if is_p1 else r[11],
                    "finished_at": r[8],
                }
            )
        return results

    def get_item_by_id(self, item_id: str) -> dict | None:
        """Retorna el ítem completo (incluido correct_option) por su ID."""
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, topic, content, options, correct_option, difficulty, rating_deviation, image_url, tags, course_id "
            "FROM items WHERE id = ?",
            (item_id,),
        )
        r = cursor.fetchone()
        conn.close()
        if not r:
            return None
        return {
            "id": r[0],
            "topic": r[1],
            "content": r[2],
            "options": json.loads(r[3]),
            "correct_option": r[4],
            "difficulty": r[5],
            "rating_deviation": r[6],
            "image_url": r[7],
            "tags": json.loads(r[8]) if r[8] else [],
            "course_id": r[9],
        }

    # ── Achievements / Logros ─────────────────────────────────────────────────

    def get_achievements(self, user_id: int) -> list[dict]:
        """Retorna todos los logros desbloqueados por el usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT badge_id, earned_at FROM achievements WHERE user_id = ? ORDER BY earned_at",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"badge_id": r[0], "earned_at": str(r[1])} for r in rows]

    def award_achievement(self, user_id: int, badge_id: str) -> bool:
        """
        Otorga un logro al usuario si no lo tiene ya.
        Retorna True si fue otorgado por primera vez, False si ya lo tenía.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO achievements (user_id, badge_id) VALUES (?, ?)",
                (user_id, badge_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

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

        ext = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "application/pdf": "pdf",
        }.get(mime_type, "bin")
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
            submission_id = existing[0]
        else:
            cursor.execute(
                """
                INSERT INTO procedure_submissions
                    (student_id, item_id, item_content, image_data, mime_type, procedure_image_path, file_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (student_id, item_id, item_content, image_data, mime_type, img_path, file_hash),
            )
            submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return submission_id

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
                   ai_proposed_score, ai_feedback, teacher_score, final_score
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
                "ai_feedback",
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

    def validate_procedure_submission(
        self,
        submission_id: int,
        teacher_score: float,
        feedback: str = "",
        teacher_id: int | None = None,
    ) -> bool:
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
        from src.domain.elo.model import procedure_elo_delta

        elo_delta = procedure_elo_delta(teacher_score)

        conn = self.get_connection()
        cursor = conn.cursor()
        ownership = ""
        params = [teacher_score, teacher_score, feedback or None, elo_delta, submission_id]
        if teacher_id is not None:
            ownership = """
                AND EXISTS (
                    SELECT 1 FROM users u
                    JOIN groups g ON g.id = u.group_id
                    WHERE u.id = procedure_submissions.student_id
                      AND g.teacher_id = ?
                )
            """
            params.append(teacher_id)
        cursor.execute(
            f"""
            UPDATE procedure_submissions
            SET teacher_score    = ?,
                final_score      = ?,
                teacher_feedback = ?,
                elo_delta        = ?,
                elo_applied      = 1,
                status           = 'VALIDATED_BY_TEACHER',
                reviewed_at      = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status IN ('pending', 'PENDING_TEACHER_VALIDATION')
              {ownership}
        """,
            tuple(params),
        )
        updated = cursor.rowcount == 1
        # El delta se aplica aquí una sola vez; la guarda de status impide
        # revalidar la misma entrega.
        if updated:
            cursor.execute(
                """SELECT ps.student_id, i.course_id, i.topic
                   FROM procedure_submissions ps
                   JOIN items i ON ps.item_id = i.id
                   WHERE ps.id = ?""",
                (submission_id,),
            )
            row = cursor.fetchone()
            if row:
                self._bump_course_topic_rating(
                    cursor, row[0], row[1], row[2], elo_delta, "procedure"
                )
        conn.commit()
        conn.close()
        return updated

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

    def save_exam_session(
        self,
        user_id: int,
        course_id: str,
        course_name: str,
        n_questions: int,
        correct_count: int,
        score_pct: float,
        global_elo_after: float | None,
        template_id: int | None = None,
        responses: list[dict] | None = None,
    ) -> int:
        """Persiste la sesión de examen (agregado) y, si se pasan, las
        respuestas por pregunta en exam_responses (para análisis del docente).
        `responses`: lista de dicts {item_id, topic, is_correct}."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO exam_sessions
               (user_id, course_id, course_name, n_questions, correct_count, score_pct,
                global_elo_after, global_elo_status, exam_template_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                course_id,
                course_name,
                n_questions,
                correct_count,
                score_pct,
                global_elo_after or 0,
                "pending" if global_elo_after is None else "rated",
                template_id,
            ),
        )
        row_id = cursor.lastrowid
        if responses:
            cursor.executemany(
                """INSERT INTO exam_responses
                   (session_id, template_id, user_id, item_id, topic, is_correct)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (
                        row_id,
                        template_id,
                        user_id,
                        r["item_id"],
                        r.get("topic"),
                        1 if r.get("is_correct") else 0,
                    )
                    for r in responses
                ],
            )
        conn.commit()
        conn.close()
        return row_id

    def create_active_exam_session(
        self,
        session_id: str,
        user_id: int,
        course_id: str,
        template_id: int | None,
        item_ids: list[str],
        expires_at: str,
    ) -> None:
        conn = self.get_connection()
        conn.execute(
            """INSERT INTO active_exam_sessions
               (id, user_id, course_id, exam_template_id, item_ids, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, user_id, course_id, template_id, json.dumps(item_ids), expires_at),
        )
        conn.commit()
        conn.close()

    def get_active_exam_session(self, session_id: str, user_id: int) -> dict | None:
        conn = self.get_connection()
        row = conn.execute(
            """SELECT id, course_id, exam_template_id, item_ids, expires_at,
                      submitted_at, result_json
               FROM active_exam_sessions WHERE id=? AND user_id=?""",
            (session_id, user_id),
        ).fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "course_id": row[1],
            "template_id": row[2],
            "item_ids": json.loads(row[3]),
            "expires_at": str(row[4]),
            "submitted_at": row[5],
            "result": json.loads(row[6]) if row[6] else None,
        }

    def complete_active_exam_session(
        self,
        session_id: str,
        user_id: int,
        course_name: str,
        result: dict,
        responses: list[dict],
    ) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE active_exam_sessions SET submitted_at=CURRENT_TIMESTAMP, result_json=?
                   WHERE id=? AND user_id=? AND submitted_at IS NULL
                     AND datetime(expires_at) >= datetime('now')""",
                (json.dumps(result), session_id, user_id),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            run = cursor.execute(
                "SELECT course_id, exam_template_id FROM active_exam_sessions WHERE id=?",
                (session_id,),
            ).fetchone()
            cursor.execute(
                """INSERT INTO exam_sessions
                   (user_id, course_id, course_name, n_questions, correct_count, score_pct,
                    global_elo_after, global_elo_status, exam_template_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    run[0],
                    course_name,
                    result["total_questions"],
                    result["correct_count"],
                    result["score_pct"],
                    # Pending: the column stays NOT NULL (AGENTS R8); the status says pending.
                    result["global_elo_after"] or 0,
                    "pending" if result["global_elo_after"] is None else "rated",
                    run[1],
                ),
            )
            history_id = cursor.lastrowid
            if responses:
                cursor.executemany(
                    """INSERT INTO exam_responses
                       (session_id, template_id, user_id, item_id, topic, is_correct)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    [
                        (
                            history_id,
                            run[1],
                            user_id,
                            r["item_id"],
                            r.get("topic"),
                            1 if r.get("is_correct") else 0,
                        )
                        for r in responses
                    ],
                )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_diagnostic(self, user_id: int, course_id: str) -> dict | None:
        """Devuelve el diagnóstico de un estudiante en una materia, o None."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT initial_elo, score_pct, result_json,
                      strftime('%Y-%m-%d %H:%M', completed_at) AS completed_at
               FROM diagnostics WHERE user_id = ? AND course_id = ?""",
            (user_id, course_id),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        import json as _json

        return {
            "initial_elo": row[0],
            "score_pct": row[1],
            "result": _json.loads(row[2] or "{}"),
            "completed_at": row[3],
        }

    def get_completed_diagnostic_course_ids(self, user_id: int) -> list:
        """course_ids con diagnóstico completado por el estudiante."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_id FROM diagnostics WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def save_diagnostic(
        self, user_id: int, course_id: str, initial_elo: float, score_pct: float, result_json: str
    ) -> None:
        """Persiste (upsert) el diagnóstico completado de una materia."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO diagnostics
               (id, user_id, course_id, initial_elo, score_pct, result_json, completed_at)
               VALUES (
                   (SELECT id FROM diagnostics WHERE user_id = ? AND course_id = ?),
                   ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
               )""",
            (user_id, course_id, user_id, course_id, initial_elo, score_pct, result_json),
        )
        conn.commit()
        conn.close()

    def get_lesson_progress(self, user_id: int, course_id: str, node_id: str) -> dict:
        """Progreso de un nodo no evaluativo; nunca consulta ni modifica ELO."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT state, objectives_viewed, math_convention_viewed,
                      viewed_at, completed_at
               FROM lesson_progress
               WHERE user_id = ? AND course_id = ? AND node_id = ?""",
            (user_id, course_id, node_id),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {
                "state": "available",
                "objectives_viewed": False,
                "math_convention_viewed": False,
                "viewed_at": None,
                "completed_at": None,
            }
        return {
            "state": row[0],
            "objectives_viewed": bool(row[1]),
            "math_convention_viewed": bool(row[2]),
            "viewed_at": str(row[3]) if row[3] else None,
            "completed_at": str(row[4]) if row[4] else None,
        }

    def record_lesson_event(self, user_id: int, course_id: str, node_id: str, event: str) -> dict:
        """Registra un hito curricular idempotente sin afectar ELO."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO lesson_progress
               (user_id, course_id, node_id, state, objectives_viewed,
                math_convention_viewed, viewed_at, completed_at, updated_at)
               VALUES (
                   ?, ?, ?,
                   CASE WHEN ? = 'node_completed' THEN 'completed' ELSE 'viewed' END,
                   CASE WHEN ? = 'objectives_viewed' THEN 1 ELSE 0 END,
                   CASE WHEN ? = 'math_convention_viewed' THEN 1 ELSE 0 END,
                   CURRENT_TIMESTAMP,
                   CASE WHEN ? = 'node_completed' THEN CURRENT_TIMESTAMP ELSE NULL END,
                   CURRENT_TIMESTAMP
               )
               ON CONFLICT(user_id, course_id, node_id) DO UPDATE SET
                   state = CASE WHEN excluded.state = 'completed' THEN 'completed'
                                ELSE lesson_progress.state END,
                   objectives_viewed = MAX(lesson_progress.objectives_viewed,
                                           excluded.objectives_viewed),
                   math_convention_viewed = MAX(lesson_progress.math_convention_viewed,
                                                excluded.math_convention_viewed),
                   viewed_at = COALESCE(lesson_progress.viewed_at, excluded.viewed_at),
                   completed_at = COALESCE(lesson_progress.completed_at, excluded.completed_at),
                   updated_at = CURRENT_TIMESTAMP""",
            (user_id, course_id, node_id, event, event, event, event),
        )
        conn.commit()
        conn.close()
        return self.get_lesson_progress(user_id, course_id, node_id)

    def get_lesson_interactions(self, user_id: int, course_id: str, node_id: str) -> dict:
        """Selecciones estructuradas del nodo, indexadas por interacción."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT interaction_id, selected_option, is_expected, misconception_tag
               FROM lesson_interactions
               WHERE user_id = ? AND course_id = ? AND node_id = ?""",
            (user_id, course_id, node_id),
        )
        rows = cursor.fetchall()
        conn.close()
        return {
            row[0]: {
                "interaction_id": row[0],
                "selected_option": row[1],
                "is_expected": None if row[2] is None else bool(row[2]),
                "misconception_tag": row[3],
            }
            for row in rows
        }

    def save_lesson_interaction(
        self,
        user_id: int,
        course_id: str,
        node_id: str,
        interaction_id: str,
        selected_option: str,
        is_expected: bool | None,
        misconception_tag: str | None,
    ) -> None:
        """Guarda una opción cerrada; nunca recibe contenido de texto libre."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO lesson_interactions
               (user_id, course_id, node_id, interaction_id, selected_option,
                is_expected, misconception_tag, answered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(user_id, course_id, node_id, interaction_id) DO UPDATE SET
                   selected_option = excluded.selected_option,
                   is_expected = excluded.is_expected,
                   misconception_tag = excluded.misconception_tag,
                   answered_at = CURRENT_TIMESTAMP""",
            (
                user_id,
                course_id,
                node_id,
                interaction_id,
                selected_option,
                None if is_expected is None else int(is_expected),
                misconception_tag,
            ),
        )
        conn.commit()
        conn.close()

    def set_topic_rating_baseline(
        self, user_id: int, course_id: str, topic: str, elo: float, rd: float = 350.0
    ) -> None:
        """Diagnostic writer: the starting rating of one (course, topic) (FR-020, FR-029).

        No attempt is created. The caller skips topics already practised (FR-021).
        """
        conn = self.get_connection()
        try:
            self._set_course_topic_rating(
                conn.cursor(), user_id, course_id, topic, elo, rd, "diagnostic"
            )
            conn.commit()
        finally:
            conn.close()

    def has_practice_attempts(self, user_id: int, course_id: str, topic: str) -> bool:
        """Whether the student answered items of this course and topic (FR-021)."""
        conn = self.get_connection()
        try:
            found = conn.execute(
                "SELECT 1 FROM attempts a JOIN items i ON i.id = a.item_id"
                " WHERE a.user_id = ? AND i.course_id = ? AND i.topic = ? LIMIT 1",
                (user_id, course_id, topic),
            ).fetchone()
        finally:
            conn.close()
        return found is not None

    def get_exam_template_results(self, template_id: int) -> dict:
        """Análisis agregado de resultados de una plantilla de examen.

        Devuelve métricas por pregunta y por tópico para que el docente
        identifique la pregunta más acertada, la más fallada y el tema a
        reforzar. Solo lee exam_responses (no afecta ELO)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        # resumen de sesiones
        cursor.execute(
            """SELECT COUNT(*) AS n_sessions,
                      COUNT(DISTINCT user_id) AS n_students,
                      COALESCE(AVG(score_pct), 0) AS avg_score
               FROM exam_sessions WHERE exam_template_id = ?""",
            (template_id,),
        )
        s = cursor.fetchone()
        summary = {
            "n_sessions": s[0] or 0,
            "n_students": s[1] or 0,
            "avg_score": round(s[2] or 0, 1),
        }
        # por pregunta
        cursor.execute(
            """SELECT er.item_id,
                      COALESCE(i.content, er.item_id) AS content,
                      er.topic,
                      COUNT(*) AS total,
                      SUM(er.is_correct) AS correct
               FROM exam_responses er
               LEFT JOIN items i ON i.id = er.item_id
               WHERE er.template_id = ?
               GROUP BY er.item_id, i.content, er.topic
               ORDER BY total DESC""",
            (template_id,),
        )
        questions = []
        for r in cursor.fetchall():
            total = r[3] or 0
            correct = r[4] or 0
            questions.append(
                {
                    "item_id": r[0],
                    "content": r[1],
                    "topic": r[2],
                    "total": total,
                    "correct": correct,
                    "accuracy": round(correct / total * 100, 1) if total else 0.0,
                }
            )
        # por tópico
        cursor.execute(
            """SELECT COALESCE(topic, 'Sin tópico') AS topic,
                      COUNT(*) AS total, SUM(is_correct) AS correct
               FROM exam_responses WHERE template_id = ?
               GROUP BY topic ORDER BY total DESC""",
            (template_id,),
        )
        topics = []
        for r in cursor.fetchall():
            total = r[1] or 0
            correct = r[2] or 0
            topics.append(
                {
                    "topic": r[0],
                    "total": total,
                    "correct": correct,
                    "accuracy": round(correct / total * 100, 1) if total else 0.0,
                }
            )
        conn.close()

        ranked = [q for q in questions if q["total"] > 0]
        best = max(ranked, key=lambda q: q["accuracy"], default=None)
        worst = min(ranked, key=lambda q: q["accuracy"], default=None)
        reinforce = min(topics, key=lambda t: t["accuracy"], default=None) if topics else None
        return {
            **summary,
            "questions": questions,
            "topics": topics,
            "best_question": best,
            "worst_question": worst,
            "reinforce_topic": reinforce,
        }

    def get_exam_history(self, user_id: int, limit: int = 20) -> list[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, course_id, course_name, n_questions, correct_count,
                      score_pct,
                      CASE WHEN global_elo_status = 'rated' THEN global_elo_after END
                          AS global_elo_after,
                      COALESCE(global_elo_status, 'unknown') AS global_elo_status,
                      strftime('%Y-%m-%d %H:%M', created_at) AS created_at
               FROM exam_sessions
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "course_id": r[1],
                "course_name": r[2],
                "n_questions": r[3],
                "correct_count": r[4],
                "score_pct": r[5],
                "global_elo_after": r[6],
                "global_elo_status": r[7],
                "created_at": r[8],
            }
            for r in rows
        ]

    # ── Sprint C: plantillas de examen del docente ────────────────────────────

    def create_exam_template(
        self,
        teacher_id: int,
        course_id: str,
        title: str,
        time_limit_min: int,
        item_ids: list[str],
    ) -> int:
        """Crea una plantilla de examen manual y devuelve el id generado."""
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO exam_templates (teacher_id, course_id, title, time_limit_min, item_ids)
               VALUES (?, ?, ?, ?, ?)""",
            (teacher_id, course_id, title, time_limit_min, json.dumps(item_ids)),
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id

    def get_exam_template(self, template_id: int) -> dict | None:
        """Obtiene una plantilla por id (incluye archivadas)."""
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, teacher_id, course_id, title, time_limit_min, item_ids,
                      archived, strftime('%Y-%m-%d %H:%M', created_at) AS created_at
               FROM exam_templates WHERE id = ?""",
            (template_id,),
        )
        r = cursor.fetchone()
        conn.close()
        if not r:
            return None
        return {
            "id": r[0],
            "teacher_id": r[1],
            "course_id": r[2],
            "title": r[3],
            "time_limit_min": r[4],
            "item_ids": json.loads(r[5]) if r[5] else [],
            "archived": bool(r[6]),
            "created_at": r[7],
        }

    def list_exam_templates(
        self,
        course_id: str | None = None,
        teacher_id: int | None = None,
        include_archived: bool = False,
    ) -> list[dict]:
        """Lista plantillas filtrando por curso, docente o estado archivado."""
        import json

        conn = self.get_connection()
        cursor = conn.cursor()
        clauses = []
        params: list = []
        if course_id is not None:
            clauses.append("course_id = ?")
            params.append(course_id)
        if teacher_id is not None:
            clauses.append("teacher_id = ?")
            params.append(teacher_id)
        if not include_archived:
            clauses.append("archived = 0")
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        cursor.execute(
            f"""SELECT id, teacher_id, course_id, title, time_limit_min, item_ids,
                       archived, strftime('%Y-%m-%d %H:%M', created_at) AS created_at
                FROM exam_templates {where}
                ORDER BY created_at DESC""",
            tuple(params),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "teacher_id": r[1],
                "course_id": r[2],
                "title": r[3],
                "time_limit_min": r[4],
                "item_ids": json.loads(r[5]) if r[5] else [],
                "archived": bool(r[6]),
                "created_at": r[7],
            }
            for r in rows
        ]

    def update_exam_template(
        self,
        template_id: int,
        title: str | None = None,
        time_limit_min: int | None = None,
        item_ids: list[str] | None = None,
    ) -> bool:
        """Actualiza campos puntuales. Retorna True si afectó una fila."""
        import json

        sets = []
        params: list = []
        if title is not None:
            sets.append("title = ?")
            params.append(title)
        if time_limit_min is not None:
            sets.append("time_limit_min = ?")
            params.append(time_limit_min)
        if item_ids is not None:
            sets.append("item_ids = ?")
            params.append(json.dumps(item_ids))
        if not sets:
            return False
        params.append(template_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE exam_templates SET {', '.join(sets)} WHERE id = ?",
            tuple(params),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def archive_exam_template(self, template_id: int) -> bool:
        """Marca la plantilla como archivada (soft delete)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE exam_templates SET archived = 1 WHERE id = ?",
            (template_id,),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    # ── Asignación de plantillas a grupos + ventana de tiempo ────────────────

    def create_exam_assignment(
        self,
        template_id: int,
        group_id: int,
        starts_at: str | None = None,
        ends_at: str | None = None,
    ) -> int:
        """Asigna una plantilla a un grupo. ISO strings o None."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO exam_assignments (template_id, group_id, starts_at, ends_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(template_id, group_id) DO UPDATE
              SET starts_at = excluded.starts_at,
                  ends_at = excluded.ends_at
            """,
            (template_id, group_id, starts_at, ends_at),
        )
        cursor.execute(
            "SELECT id FROM exam_assignments WHERE template_id=? AND group_id=?",
            (template_id, group_id),
        )
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        return int(row[0])

    def delete_exam_assignment(self, assignment_id: int, template_id: int | None = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        if template_id is None:
            cursor.execute("DELETE FROM exam_assignments WHERE id = ?", (assignment_id,))
        else:
            cursor.execute(
                "DELETE FROM exam_assignments WHERE id = ? AND template_id = ?",
                (assignment_id, template_id),
            )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def list_assignments_for_template(self, template_id: int) -> list[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ea.id, ea.template_id, ea.group_id, g.name,
                   ea.starts_at, ea.ends_at, ea.created_at
            FROM exam_assignments ea
            JOIN groups g ON g.id = ea.group_id
            WHERE ea.template_id = ?
            ORDER BY ea.created_at DESC
            """,
            (template_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "template_id": r[1],
                "group_id": r[2],
                "group_name": r[3],
                "starts_at": r[4],
                "ends_at": r[5],
                "created_at": r[6],
            }
            for r in rows
        ]

    def list_active_templates_for_student(
        self,
        user_id: int,
        course_id: str,
    ) -> list[dict]:
        """Plantillas activas visibles a un estudiante en un curso (SQLite)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT et.id, et.title, et.course_id, et.item_ids,
                   et.time_limit_min, et.created_at,
                   MAX(ea.ends_at) AS window_ends_at
            FROM exam_templates et
            LEFT JOIN exam_assignments ea
                ON ea.template_id = et.id
               AND ea.group_id = (SELECT group_id FROM users WHERE id = ?)
               AND (ea.starts_at IS NULL OR ea.starts_at <= datetime('now'))
               AND (ea.ends_at IS NULL OR ea.ends_at >= datetime('now'))
            WHERE et.archived = 0
              AND et.course_id = ?
              AND (
                NOT EXISTS (SELECT 1 FROM exam_assignments WHERE template_id = et.id)
                OR ea.id IS NOT NULL
              )
            GROUP BY et.id
            ORDER BY et.created_at DESC
            """,
            (user_id, course_id),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "title": r[1],
                "course_id": r[2],
                "item_ids": json.loads(r[3]) if r[3] else [],
                "time_limit_min": r[4],
                "created_at": r[5],
                "window_ends_at": r[6],
            }
            for r in rows
        ]

    def list_pending_exams_for_student(self, user_id: int) -> list[dict]:
        """Resumen de plantillas pendientes en todos los cursos inscritos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT et.id, et.title, et.course_id, c.name, et.time_limit_min
            FROM exam_templates et
            JOIN enrollments en
                ON en.course_id = et.course_id AND en.user_id = ?
            JOIN courses c ON c.id = et.course_id
            LEFT JOIN exam_assignments ea
                ON ea.template_id = et.id
               AND ea.group_id = (SELECT group_id FROM users WHERE id = ?)
               AND (ea.starts_at IS NULL OR ea.starts_at <= datetime('now'))
               AND (ea.ends_at IS NULL OR ea.ends_at >= datetime('now'))
            WHERE et.archived = 0
              AND (
                NOT EXISTS (SELECT 1 FROM exam_assignments WHERE template_id = et.id)
                OR ea.id IS NOT NULL
              )
            ORDER BY et.created_at DESC
            """,
            (user_id, user_id),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "template_id": r[0],
                "title": r[1],
                "course_id": r[2],
                "course_name": r[3],
                "time_limit_min": r[4],
            }
            for r in rows
        ]
