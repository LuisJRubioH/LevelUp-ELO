"""
Spec 007 delivery G (US2; FR-020, FR-021, FR-022): who may enter the League and who may meet whom.

Pure rules of `src/domain/pvp/admission.py` (plan-g, O-G2, O-G5, O-G6, O-G7, O-G10): a student
enters a subject's League only with a rating in it — a test user too — and a real student only
with an institution; a test user meets only test users, and a real student only one of the same
institution, compared by a folded key.
"""

from dataclasses import dataclass

from src.domain.pvp.admission import (
    NO_INSTITUTION,
    NO_RATING,
    entry_refusal,
    institution_key,
    may_meet,
)

SCHOOL = institution_key("Colegio de la Liga")


@dataclass(frozen=True)
class Player:
    is_test_user: bool
    institution: str | None = SCHOOL  # the folded key, as the lobby keeps it


def test_spec007_entry_refusal_reasons():
    """FR-020 (O-G2, O-G7): no rating in the subject → `no_rating`, for a real student and for
    a test user alike, and before any other reason; a rated student of either kind enters.
    FR-022 (O-G5): a rated real student with no institution key → `no_institution`; a test user
    needs none (O-G7)."""
    assert NO_RATING == "no_rating"
    assert NO_INSTITUTION == "no_institution"
    assert entry_refusal(rated=False, is_test_user=False, institution_key=SCHOOL) == NO_RATING
    assert entry_refusal(rated=False, is_test_user=True, institution_key=SCHOOL) == NO_RATING
    assert entry_refusal(rated=True, is_test_user=False, institution_key=SCHOOL) is None
    assert entry_refusal(rated=True, is_test_user=True, institution_key=SCHOOL) is None
    assert entry_refusal(rated=True, is_test_user=False, institution_key=None) == NO_INSTITUTION
    assert entry_refusal(rated=False, is_test_user=False, institution_key=None) == NO_RATING
    assert entry_refusal(rated=True, is_test_user=True, institution_key=None) is None


def test_spec007_test_users_meet_only_test_users():
    """FR-021 (O-G7): a real student and a test user never meet, in either order, even of the
    same institution; two test users meet whatever their institutions, and so do two real
    students of one institution."""
    real, test = Player(is_test_user=False), Player(is_test_user=True)
    assert may_meet(real, test) is False
    assert may_meet(test, real) is False
    assert may_meet(test, Player(is_test_user=True)) is True
    assert may_meet(test, Player(is_test_user=True, institution=institution_key("Otro"))) is True
    assert may_meet(test, Player(is_test_user=True, institution=None)) is True
    assert may_meet(real, Player(is_test_user=False)) is True


def test_spec007_students_of_different_institutions_never_meet():
    """FR-022: two real students meet only when their institution keys are equal; a real
    student without a key meets nobody (the entry refuses them before, O-G5)."""
    here = Player(is_test_user=False, institution=institution_key("Colegio San José"))
    there = Player(is_test_user=False, institution=institution_key("Instituto Técnico"))
    same = Player(is_test_user=False, institution=institution_key("colegio  san jose"))
    nowhere = Player(is_test_user=False, institution=None)
    assert may_meet(here, there) is False
    assert may_meet(there, here) is False
    assert may_meet(here, same) is True
    assert may_meet(here, nowhere) is False
    assert may_meet(nowhere, Player(is_test_user=False, institution=None)) is False


def test_spec007_institutions_compare_folded():
    """O-G6: the key is spec 009's `comparable_key` — inner spaces collapsed, ends trimmed, case
    and accents folded, the ñ kept; blank or missing has no key."""
    assert institution_key("Colegio  San José") == institution_key("colegio san jose")
    assert institution_key("  COLEGIO San José ") == institution_key("colegio san josé")
    assert institution_key("Piñas") != institution_key("Pinas")
    assert institution_key("   ") is None
    assert institution_key("") is None
    assert institution_key(None) is None
