"""
src/domain/pvp/admission.py
===========================
Spec 007 delivery G (FR-020, FR-021, FR-022; owner decisions O-G2, O-G5, O-G6, O-G7, O-G10).
Pure — no I/O: the caller reads the facts and passes them in.

- Who may enter (FR-020, O-G2): a student with a rating in the subject — any origin, read as
  `RatingReadService.course_rating_of(...) is not None`. A test user needs one too (O-G7).
- Who may enter (FR-022, O-G5): a real student also needs an institution — their main group's —
  with a key; a test user does not (O-G7).
- Who may meet (FR-021, FR-022, O-G7): a test user only a test user, whatever the institutions;
  a real student only a real student with the same institution key.
- How two institutions compare (O-G6): spec 009's `comparable_key` — inner spaces collapsed, ends
  trimmed, case and accents folded, the ñ kept.
"""

from typing import Protocol

from src.domain.identity import comparable_key

NO_RATING = "no_rating"
NO_INSTITUTION = "no_institution"


def institution_key(institution) -> str | None:
    """O-G6: the key two institutions compare by (spec 009 FR-024's `comparable_key`), or None
    when there is no institution or nothing is left of it."""
    return comparable_key(institution)


def entry_refusal(*, rated: bool, is_test_user: bool, institution_key: str | None) -> str | None:
    """Why a student may not enter a subject's League — `NO_RATING` first, then
    `NO_INSTITUTION` for a real student without an institution key — or None when they may."""
    if not rated:
        return NO_RATING
    if institution_key is None and not is_test_user:
        return NO_INSTITUTION
    return None


class Entrant(Protocol):
    is_test_user: bool
    institution: str | None  # the folded key (`institution_key`)


def may_meet(a: Entrant, b: Entrant) -> bool:
    """FR-021, FR-022: two test users always meet; two real students meet when both have the
    same institution key; a test user and a real student never do."""
    if bool(a.is_test_user) != bool(b.is_test_user):
        return False
    if a.is_test_user:
        return True
    return a.institution is not None and a.institution == b.institution
