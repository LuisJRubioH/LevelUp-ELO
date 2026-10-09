"""
Spec 001 FR-028k (task T085): the catalogue rule `in_catalogue`, over every level and, for
semillero, every grade. One domain rule decides both the courses offered and the courses that
count as current for the overall rating.
"""

import pytest

from src.domain.entities import SEMILLERO_GRADES, in_catalogue, valid_semillero_grade

GRADES = ["6", "7", "8", "9", "10", "11"]


@pytest.mark.parametrize("grade", GRADES)
def test_spec001_semillero_catalogue_is_the_courses_of_the_grade(grade):
    other = "7" if grade != "7" else "8"
    assert in_catalogue("semillero", grade, f"algebra_semillero_{grade}", "Semillero")
    assert in_catalogue("semillero", int(grade), f"geometria_semillero_{grade}", "Semillero")
    assert not in_catalogue("semillero", grade, f"algebra_semillero_{other}", "Semillero")
    assert not in_catalogue("semillero", grade, "algebra_basica", "Colegio")
    # A suffix that only ends like the grade is another grade: 1 vs 11.
    assert not in_catalogue("semillero", "1", "algebra_semillero_11", "Semillero")


@pytest.mark.parametrize("grade", [None, ""])
def test_spec001_semillero_without_a_grade_has_no_course(grade):
    """Today every semillero course matched; now none does (FR-028k)."""
    for g in GRADES:
        assert not in_catalogue("semillero", grade, f"algebra_semillero_{g}", "Semillero")


@pytest.mark.parametrize(
    "level, block, other_block",
    [
        ("universidad", "Universidad", "Colegio"),
        ("colegio", "Colegio", "Universidad"),
        ("concursos", "Concursos", "Semillero"),
    ],
)
def test_spec001_other_levels_are_their_block(level, block, other_block):
    assert in_catalogue(level, None, "any_course", block)
    assert in_catalogue(level.upper(), "9", "any_course", block)  # grade is ignored
    assert not in_catalogue(level, None, "any_course", other_block)


def test_spec001_unknown_level_falls_back_to_universidad():
    assert in_catalogue(None, None, "calculo_diferencial", "Universidad")
    assert in_catalogue("doctorado", None, "calculo_diferencial", "Universidad")
    assert not in_catalogue(None, None, "algebra_basica", "Colegio")


def test_spec001_valid_semillero_grades_are_6_to_11():
    assert SEMILLERO_GRADES == frozenset(GRADES)
    for grade in GRADES + [6, 11]:
        assert valid_semillero_grade(grade)
    for grade in [None, "", "5", "12", "6°", " 7", 5]:
        assert not valid_semillero_grade(grade)
