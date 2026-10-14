"""
The test-student seed (local and test data only; skipped when ENVIRONMENT=production).

Every seeded student is enrolled in exactly the catalogue of their level and grade — the domain
rule `in_catalogue` (spec 001 FR-028k) — and the semillero test group points at a semillero
course. Found by the persistence survey (docs/sdd/persistence-survey.md, P12): the seed looked
for blocks `Semillero 9°` / `Semillero %`, which the `courses.block` CHECK does not allow, so the
semillero test students had no enrolment and their group no course.

`estudiante_concursos_1` is seeded on SQLite only (survey P11, left to spec 002). PostgreSQL keeps
its rows between tests and other tests add courses after the seed ran, so the catalogue that must
be enrolled is the one the item bank defines; no enrolment may fall outside the catalogue.
"""

from pathlib import Path

import pytest

from src.domain.entities import LEVEL_TO_BLOCK, in_catalogue
from tests.integration.conftest import sql

_BANK = Path(__file__).resolve().parents[2] / "items" / "bank"
BANK_COURSES = {p.stem for p in _BANK.glob("*.json")} | {
    p.stem for p in (_BANK / "semillero").glob("*.json")
}

SEEDED_ON_BOTH_ENGINES = [
    ("estudiante_colegio_1", "colegio", None),
    ("estudiante_colegio_2", "colegio", None),
    ("estudiante_colegio_3", "colegio", None),
    ("estudiante_universidad_1", "universidad", None),
    ("estudiante_universidad_2", "universidad", None),
    ("estudiante_semillero_1", "semillero", "9"),
    ("estudiante_semillero_2", "semillero", "11"),
]


def _catalogue(repo, level, grade) -> set:
    rows = sql(repo, "SELECT id, block FROM courses WHERE block = ?", (LEVEL_TO_BLOCK[level],))
    return {course_id for course_id, block in rows if in_catalogue(level, grade, course_id, block)}


@pytest.mark.parametrize("username,level,grade", SEEDED_ON_BOTH_ENGINES)
def test_seeded_students_are_enrolled_in_their_catalogue(repo, username, level, grade):
    rows = sql(repo, "SELECT id, education_level, grade FROM users WHERE username = ?", (username,))
    assert rows, f"{username} was not seeded"
    user_id, stored_level, stored_grade = rows[0]
    assert (stored_level, stored_grade) == (level, grade)

    enrolled = {
        row[0]
        for row in sql(repo, "SELECT course_id FROM enrollments WHERE user_id = ?", (user_id,))
    }
    catalogue = _catalogue(repo, level, grade)
    from_bank = catalogue & BANK_COURSES
    assert from_bank, f"the item bank has no course for {level} {grade or ''}"
    assert enrolled <= catalogue, "enrolled outside the catalogue"
    assert from_bank <= enrolled, "catalogue courses missing"


def test_seeded_semillero_group_points_at_a_semillero_course(repo):
    rows = sql(
        repo,
        "SELECT c.block FROM groups g LEFT JOIN courses c ON c.id = g.course_id"
        " WHERE g.name = 'Grupo Prueba - Semillero'",
    )
    assert rows, "the semillero test group was not seeded"
    assert rows[0][0] == LEVEL_TO_BLOCK["semillero"]
