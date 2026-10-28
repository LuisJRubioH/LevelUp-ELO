"""
Spec 008 delivery C (FR-020, FR-021; US3-AS1, US3-AS2): both engines take every course's block and
name from the course catalogue (`src/domain/bank/catalogue.py`), a semillero file its block, grade
and name from its file name, and a course the catalogue does not know is not synced (plan-c.md
O-C5). The first test pins the 49 course rows a bootstrap from the real bank stores today: C moves
none of them (O-C2).
"""

import json
import logging
import uuid

from tests.integration.conftest import is_postgres, register_course, sql

SEMILLERO_LABELS = {
    "algebra": "Álgebra",
    "aritmetica": "Aritmética",
    "conteo_combinatoria": "Conteo y Combinatoria",
    "geometria": "Geometría",
    "logica": "Lógica",
    "probabilidad": "Probabilidad",
}
# plan-c.md § Measured facts: the 49 (id, name, block) rows of a fresh bootstrap, before C.
COURSE_ROWS = {
    "algebra_basica": ("Álgebra Básica", "Colegio"),
    "aritmetica_basica": ("Aritmética Básica", "Colegio"),
    "geometria": ("Geometría", "Colegio"),
    "trigonometria": ("Trigonometría", "Colegio"),
    "evaluar_para_avanzar_8": ("Evaluar para Avanzar — Matemáticas 8.°", "Colegio"),
    "algebra_lineal": ("Álgebra Lineal", "Universidad"),
    "calculo_diferencial": ("Cálculo Diferencial", "Universidad"),
    "calculo_integral": ("Cálculo Integral", "Universidad"),
    "calculo_varias_variables": ("Cálculo de Varias Variables", "Universidad"),
    "ecuaciones_diferenciales": ("Ecuaciones Diferenciales Ordinarias", "Universidad"),
    "probabilidad": ("Probabilidad", "Universidad"),
    "DIAN": ("Concurso DIAN — Gestor I", "Concursos"),
    "SENA": ("Concurso SENA — Profesional 10", "Concursos"),
    **{
        f"{subject}_semillero_{grade}": (f"{label} Semillero {grade}°", "Semillero")
        for subject, label in SEMILLERO_LABELS.items()
        for grade in range(6, 12)
    },
}


def _course_row(repo, course_id):
    rows = sql(repo, "SELECT name, block FROM courses WHERE id = ?", (course_id,))
    return tuple(rows[0]) if rows else None


def _item(item_id, topic):
    return {
        "id": item_id,
        "content": f"¿Cuánto es $2+2$? ({topic})",
        "difficulty": 900,
        "topic": topic,
        "options": ["3", "4"],
        "correct_option": "4",
    }


def _write(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


def test_spec008_c_synced_courses_keep_their_block_and_name(repo):
    """FR-020 (O-C2): a sync of the real bank stores exactly the 49 course rows it stored before
    C — the ten courses once named by their first item's topic keep that name."""
    if is_postgres(repo):  # the shared database's bootstrap may predate this code: sync now
        repo.sync_items_from_bank_folder(repo.BANK_DIR)
        rows = {
            r[0]: (r[1], r[2])
            for r in sql(repo, "SELECT id, name, block FROM courses")
            if r[0] in COURSE_ROWS
        }
    else:
        rows = {r[0]: (r[1], r[2]) for r in sql(repo, "SELECT id, name, block FROM courses")}

    assert len(COURSE_ROWS) == 49
    assert rows == COURSE_ROWS


def test_spec008_c_both_engines_sync_the_catalogues_block_and_name(repo, tmp_path, monkeypatch):
    """FR-020, US3-AS1: the next start stores the catalogue's block and name; reordering the
    course's items does not rename it (its name is never its first item's topic)."""
    course = f"c008_{uuid.uuid4().hex[:8]}"
    bank = tmp_path / "bank"
    _write(bank / f"{course}.json", [_item(f"{course}_1", "Primero"), _item(f"{course}_2", "Otro")])
    monkeypatch.setattr(type(repo), "BANK_DIR", str(bank))
    register_course(monkeypatch, course, "Colegio", "Curso C")

    repo._sync_bank_if_changed()
    assert _course_row(repo, course) == ("Curso C", "Colegio")

    register_course(monkeypatch, course, "Universidad", "Curso C renombrado")
    repo._sync_bank_if_changed()
    assert _course_row(repo, course) == ("Curso C renombrado", "Universidad")

    _write(bank / f"{course}.json", [_item(f"{course}_2", "Otro"), _item(f"{course}_1", "Primero")])
    repo._sync_bank_if_changed()
    assert _course_row(repo, course) == ("Curso C renombrado", "Universidad")


def test_spec008_c_a_semillero_file_syncs_as_its_grade_without_an_entry(
    repo, tmp_path, monkeypatch
):
    """FR-021, US3-AS2: `semillero/probabilidad_semillero_9.json`, with no entry in the catalogue,
    is synced as block «Semillero», name «Probabilidad Semillero 9°», and is in the grade-9
    catalogue and not in grade 8's. The course row is first spoiled so the sync must write it."""
    from src.domain.bank import catalogue

    course = "probabilidad_semillero_9"
    assert course not in catalogue.COURSES
    item_id = f"c008_sem_{uuid.uuid4().hex[:8]}"
    bank = tmp_path / "bank"
    _write(bank / "semillero" / f"{course}.json", [_item(item_id, "Tema C semillero")])
    sql(repo, "UPDATE courses SET name = 'C antes', block = 'Colegio' WHERE id = ?", (course,))
    try:
        repo.sync_items_from_bank_folder(str(bank))

        assert _course_row(repo, course) == ("Probabilidad Semillero 9°", "Semillero")
        stored = sql(repo, "SELECT course_id FROM items WHERE id = ?", (item_id,))
        assert [tuple(r) for r in stored] == [(course,)]
        grade_9 = {c["id"] for c in repo.get_available_courses_by_level("semillero", grade="9")}
        grade_8 = {c["id"] for c in repo.get_available_courses_by_level("semillero", grade="8")}
        assert course in grade_9 and course not in grade_8
    finally:
        sql(repo, "DELETE FROM items WHERE id = ?", (item_id,))
        sql(
            repo,
            "UPDATE courses SET name = ?, block = 'Semillero', description = ? WHERE id = ?",
            ("Probabilidad Semillero 9°", "Curso de Probabilidad Semillero 9°", course),
        )


def test_spec008_c_an_unknown_course_is_not_synced(repo, tmp_path, caplog):
    """FR-020 (O-C5, survey B14): a bank file whose course the catalogue does not know (a bank
    that bypassed CI) is skipped with an error naming it — never stored in «Universidad»."""
    course = f"c008_unknown_{uuid.uuid4().hex[:8]}"
    item_id = f"{course}_1"
    bank = tmp_path / "bank"
    _write(bank / f"{course}.json", [_item(item_id, "Tema desconocido")])

    with caplog.at_level(logging.ERROR):
        repo.sync_items_from_bank_folder(str(bank))

    assert _course_row(repo, course) is None
    assert sql(repo, "SELECT id FROM items WHERE id = ?", (item_id,)) == []
    assert any(
        r.levelno == logging.ERROR and f"{course}.json" in r.getMessage() for r in caplog.records
    )
