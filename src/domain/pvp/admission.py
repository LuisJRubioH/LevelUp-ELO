"""
src/domain/pvp/admission.py
===========================
Spec 007 delivery G1 (FR-020, FR-021; owner decisions O-G2, O-G7, O-G10). Pure — no I/O: the
caller reads the facts and passes them in.

- Who may enter (FR-020, O-G2): a student with a rating in the subject — any origin, read as
  `RatingReadService.course_rating_of(...) is not None`. A test user needs one too (O-G7).
- Who may meet (FR-021, O-G7): a test user only a test user; a real student only a real student.

Delivery G2 adds the institution (FR-022): its key, its refusal and its comparison here.
"""

from typing import Protocol

NO_RATING = "no_rating"


def entry_refusal(*, rated: bool, is_test_user: bool) -> str | None:
    """Why a student may not enter a subject's League — `NO_RATING` — or None when they may.

    `is_test_user` changes nothing in G1: a test user, like anyone, needs a rating (O-G7). G2
    reads it with the institution, which a test user does not need."""
    return None if rated else NO_RATING


class Entrant(Protocol):
    is_test_user: bool


def may_meet(a: Entrant, b: Entrant) -> bool:
    """FR-021: two waiters may meet only when both are test users or neither is."""
    return bool(a.is_test_user) == bool(b.is_test_user)
