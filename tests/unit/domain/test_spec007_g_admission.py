"""
Spec 007 delivery G1 (US2; FR-020, FR-021): who may enter the League and who may meet whom.

Pure rules of `src/domain/pvp/admission.py` (plan-g, O-G2, O-G7, O-G10): a student enters a
subject's League only with a rating in it — a test user too; a test user meets only test users.
Delivery G2 adds the institution (FR-022).
"""

from dataclasses import dataclass

from src.domain.pvp.admission import NO_RATING, entry_refusal, may_meet


@dataclass(frozen=True)
class Player:
    is_test_user: bool


def test_spec007_entry_refusal_reasons():
    """FR-020 (O-G2, O-G7): no rating in the subject → `no_rating`, for a real student and for
    a test user alike; a rated student of either kind enters."""
    assert NO_RATING == "no_rating"
    assert entry_refusal(rated=False, is_test_user=False) == NO_RATING
    assert entry_refusal(rated=False, is_test_user=True) == NO_RATING
    assert entry_refusal(rated=True, is_test_user=False) is None
    assert entry_refusal(rated=True, is_test_user=True) is None


def test_spec007_test_users_meet_only_test_users():
    """FR-021 (O-G7): a real student and a test user never meet, in either order; two test
    users meet, and so do two real students."""
    real, test = Player(is_test_user=False), Player(is_test_user=True)
    assert may_meet(real, test) is False
    assert may_meet(test, real) is False
    assert may_meet(test, Player(is_test_user=True)) is True
    assert may_meet(real, Player(is_test_user=False)) is True
