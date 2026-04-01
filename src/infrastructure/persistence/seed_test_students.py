"""Seed de estudiantes de prueba con persistencia permanente.

Crea 5 estudiantes de prueba (3 colegio, 2 universidad) matriculados en TODOS
los cursos de su nivel. Es idempotente: si ya existen no sobrescribe progreso.

Estudiantes:
  - estudiante_colegio_1, _2, _3  (nivel colegio, contraseña: test1234)
  - estudiante_universidad_1, _2   (nivel universidad, contraseña: test1234)

Uso:
  seed_test_students(repository)  # llamado desde SQLiteRepository.__init__
"""

from src.domain.entities import LEVEL_COLEGIO, LEVEL_UNIVERSIDAD, LEVEL_SEMILLERO, LEVEL_TO_BLOCK

_TEST_PASSWORD = "test1234"

_TEST_STUDENTS = [
    # (username, education_level, grade)
    ("estudiante_colegio_1",      LEVEL_COLEGIO,     None),
    ("estudiante_colegio_2",      LEVEL_COLEGIO,     None),
    ("estudiante_colegio_3",      LEVEL_COLEGIO,     None),
    ("estudiante_universidad_1",  LEVEL_UNIVERSIDAD, None),
    ("estudiante_universidad_2",  LEVEL_UNIVERSIDAD, None),
    ("estudiante_semillero_1",    LEVEL_SEMILLERO,   "9"),
    ("estudiante_semillero_2",    LEVEL_SEMILLERO,   "11"),
]


def seed_test_students(repo):
    """Crea estudiantes de prueba y los matricula en todos los cursos de su nivel.

    - Estrictamente idempotente: si el usuario ya existe, no lo toca.
    - Solo INSERT, nunca UPDATE sobre usuarios existentes.
    - Marca is_test_user=1 para protección contra eliminación.
    - Crea un grupo demo por nivel si no existe (vinculado a profesor1).
    """
    conn = repo.get_connection()
    cursor = conn.cursor()

    # ── Salida rápida: si todos ya existen, no hay nada que hacer ────────
    cursor.execute(
        "SELECT username FROM users WHERE username IN ({})".format(
            ','.join('?' * len(_TEST_STUDENTS))
        ),
        [s[0] for s in _TEST_STUDENTS],
    )
    existing = {row[0] for row in cursor.fetchall()}
    students_to_create = [(u, l, g) for u, l, g in _TEST_STUDENTS if u not in existing]

    if not students_to_create:
        conn.close()
        return  # Todos existen — no tocar nada

    # Solo computar hash si hay estudiantes nuevos (Argon2 es lento por diseño)
    password_hash = repo.hashing.hash_password(_TEST_PASSWORD)

    # Necesitamos un profesor para crear grupos; usar profesor1 (creado por _seed_demo_data)
    cursor.execute("SELECT id FROM users WHERE username = 'profesor1'")
    row = cursor.fetchone()
    if not row:
        conn.close()
        return  # Sin profesor demo no podemos crear grupos; se reintentará en próximo inicio
    profesor_id = row[0]

    # Grupos de prueba por nivel (uno por bloque educativo)
    _level_groups = {
        LEVEL_COLEGIO:     ("Grupo Prueba - Colegio",     None),
        LEVEL_UNIVERSIDAD: ("Grupo Prueba - Universidad", None),
        LEVEL_SEMILLERO:   ("Grupo Prueba - Semillero",   None),
    }
    for level, (g_name, _) in _level_groups.items():
        g_norm = g_name.strip().lower()
        cursor.execute(
            "SELECT id FROM groups WHERE name_normalized = ? AND teacher_id = ?",
            (g_norm, profesor_id),
        )
        row = cursor.fetchone()
        if not row:
            block = LEVEL_TO_BLOCK[level]
            cursor.execute(
                "SELECT id FROM courses WHERE block = ? ORDER BY name ASC LIMIT 1",
                (block,),
            )
            first_course = cursor.fetchone()
            course_id = first_course[0] if first_course else None
            cursor.execute(
                "INSERT INTO groups (name, teacher_id, course_id, name_normalized) VALUES (?, ?, ?, ?)",
                (g_name, profesor_id, course_id, g_norm),
            )
            conn.commit()
            _level_groups[level] = (g_name, cursor.lastrowid)
        else:
            _level_groups[level] = (g_name, row[0])

    # Crear SOLO estudiantes que no existen — nunca modificar los existentes
    for username, edu_level, student_grade in students_to_create:
        group_id = _level_groups[edu_level][1]
        _grade = student_grade if edu_level == LEVEL_SEMILLERO else None
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, approved, group_id, "
            "rating_deviation, education_level, is_test_user, grade) "
            "VALUES (?, ?, 'student', 1, ?, 350.0, ?, 1, ?)",
            (username, password_hash, group_id, edu_level, _grade),
        )
    conn.commit()

    # Matricular estudiantes nuevos en TODOS los cursos de su nivel
    for username, edu_level, _grade in students_to_create:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        student_id = cursor.fetchone()[0]
        block = LEVEL_TO_BLOCK[edu_level]
        group_id = _level_groups[edu_level][1]

        cursor.execute(
            "SELECT id FROM courses WHERE block = ?",
            (block,),
        )
        courses = cursor.fetchall()
        for (course_id,) in courses:
            cursor.execute(
                "INSERT OR IGNORE INTO enrollments (user_id, course_id, group_id) VALUES (?, ?, ?)",
                (student_id, course_id, group_id),
            )

    conn.commit()
    conn.close()
