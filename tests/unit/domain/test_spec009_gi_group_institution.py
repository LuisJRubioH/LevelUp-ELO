"""
Spec 009 delivery GI — a group's institution and grade, the rules without I/O (plan-gi.md § The
rules; tasks T003, T004): the institution as stored, the grade's range and the key two institutions
compare by (spec 004's comparison of names, the one spec 007 O-G6 uses).

[CHANGE] tests: the base has no edit of a group's institution, so each fails there (missing
function) before its implementation.
"""

from src.domain.identity import comparable_key
from src.domain.student_import import group_institution_problem, stored_institution


def test_spec009_gi_a_group_institution_is_stored_as_typed_and_checked():
    """FR-019, US4-AS3, O-GI6 (a): outer spaces removed and inner spaces collapsed, case and
    accents kept; an empty or blank institution, one over 200 characters and a grade outside
    6 … 11 are refused, each with its reason."""
    assert stored_institution("  Colegio   San José ") == "Colegio San José"
    assert stored_institution("Liceo\tPiñas\n") == "Liceo Piñas"
    assert stored_institution("I.E. ÑANDÚ") == "I.E. ÑANDÚ"

    assert group_institution_problem("Colegio San José", 6) is None
    assert group_institution_problem("Colegio San José", 11) is None
    assert group_institution_problem("Colegio San José", None) is None
    assert group_institution_problem("  " + "a" * 200 + "  ", 9) is None

    for empty in ("", "   ", None):
        assert group_institution_problem(empty, 9) == "Escribe la institución."
    assert group_institution_problem(42, 9) == "Escribe la institución."
    assert (
        group_institution_problem("a" * 201, 9) == "La institución tiene más de 200 caracteres."
    )
    # Collapsing comes first: 200 characters once inner spaces are one are accepted.
    assert group_institution_problem("a" * 100 + "     " + "a" * 99, 9) is None

    for grade in (5, 12, 0, -1, True, False, "9", 9.0):
        assert (
            group_institution_problem("Colegio San José", grade)
            == "El grado del grupo va de 6.º a 11.º."
        ), grade


_SAME_KEY = (
    ("Colegio  San José", "colegio san jose", True),
    ("  COLEGIO SAN JOSÉ ", "Colegio San Jose", True),
    ("Piñas", "Pinas", False),
    ("Liceo Piñas", "liceo PIÑAS", True),
    ("Colegio San José", "Colegio San Josefa", False),
)


def test_spec009_gi_institutions_compare_by_spec004_key():
    """FR-024 (spec 007 O-G6): inner spaces collapsed, case and accents folded, the ñ kept; an
    empty or missing institution has no key."""
    for a, b, same in _SAME_KEY:
        assert comparable_key(a) is not None
        assert (comparable_key(a) == comparable_key(b)) is same, (a, b)
    for blank in (None, "", "   ", "\t\n", 7):
        assert comparable_key(blank) is None
