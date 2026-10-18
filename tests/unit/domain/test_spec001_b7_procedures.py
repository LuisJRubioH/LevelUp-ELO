"""
Spec 001, delivery B7: the arithmetic of a regrade and the classification of an upload.
Pure domain functions, no I/O. [CHANGE] tests (tasks-b7.md T004–T006), written first.
"""

import pytest

from src.domain.elo.model import ProcedureGrading, procedure_elo_delta, procedure_grading
from src.domain.procedures import (
    ACCEPT,
    COPY,
    REFUSE_OTHER_ITEM,
    REFUSE_SAME_ITEM,
    classify_upload,
)

# ── T004: one current contribution per procedure (FR-024b, FR-024d) ─────────


def _regrade(first, second, rating=1000.0):
    """Grade a fresh procedure `first`, then regrade it `second`; return both gradings."""
    one = procedure_grading(first, 0.0, rating)
    two = procedure_grading(second, one.contribution_after, rating + one.applied)
    return one, two


def test_spec001_b7_first_grading_is_todays_delta():
    """FR-022 unchanged: with no previous contribution the correction is the full delta."""
    for grade in (0.0, 30.0, 50.0, 80.0, 100.0):
        result = procedure_grading(grade, 0.0, 1000.0)
        assert result.computed_delta == procedure_elo_delta(grade)
        assert result.correction == result.applied == procedure_elo_delta(grade)
        assert result.contribution_after == procedure_elo_delta(grade)


def test_spec001_b7_same_grade_again_moves_nothing():
    """US9-AS1: 80 (+6), then 80 → correction 0, contribution stays +6."""
    one, two = _regrade(80.0, 80.0)
    assert one.applied == 6.0
    assert (two.correction, two.applied, two.contribution_after) == (0.0, 0.0, 6.0)


def test_spec001_b7_higher_regrade_adds_the_difference():
    """US9-AS2: 60 (+2), then 90 (+8) → +6, contribution +8."""
    _, two = _regrade(60.0, 90.0)
    assert (two.computed_delta, two.correction, two.applied) == (8.0, 6.0, 6.0)
    assert two.contribution_after == 8.0


def test_spec001_b7_lower_regrade_takes_back_the_difference():
    """US9-AS3: 80 (+6), then 30 (−4) → −10, contribution −4."""
    _, two = _regrade(80.0, 30.0)
    assert (two.computed_delta, two.correction, two.applied) == (-4.0, -10.0, -10.0)
    assert two.contribution_after == -4.0


def test_spec001_b7_the_floor_is_respected_and_the_applied_amount_counts():
    """US9-AS7: rating 3, grade 0 → −3 applied; resubmitted, 80 at rating 0 → +9, rating 9."""
    one = procedure_grading(0.0, 0.0, 3.0)
    assert (one.computed_delta, one.correction, one.applied) == (-10.0, -10.0, -3.0)
    assert one.contribution_after == -3.0

    two = procedure_grading(80.0, one.contribution_after, 0.0)
    assert (two.correction, two.applied, two.contribution_after) == (9.0, 9.0, 6.0)


def test_spec001_b7_the_same_grade_after_a_floored_penalty_applies_the_remainder():
    """B7-P2: rating 3, grade 0 (−3 applied); regraded 0 at rating 20 → the remaining −7."""
    one = procedure_grading(0.0, 0.0, 3.0)
    two = procedure_grading(0.0, one.contribution_after, 20.0)
    assert (two.correction, two.applied, two.contribution_after) == (-7.0, -7.0, -10.0)


def test_spec001_b7_a_regrade_below_zero_is_floored_again():
    """Edge case: a correction larger than the rating stops at 0; the contribution follows."""
    two = procedure_grading(0.0, 6.0, 12.0)  # asks −16 with only 12 to give
    assert (two.correction, two.applied, two.contribution_after) == (-16.0, -12.0, -6.0)


def test_spec001_b7_amounts_carry_no_float_noise():
    """0.2 × an integer grade has binary noise; stored amounts are rounded like the delta."""
    _, two = _regrade(70.0, 90.0)  # 4.000000000000001 and 8.000000000000002 unrounded
    assert (two.correction, two.applied, two.contribution_after) == (4.0, 4.0, 8.0)


def test_spec001_b7_grade_out_of_range_is_refused():
    """FR-023 unchanged: the grade must lie in 0–100."""
    with pytest.raises(ValueError):
        procedure_grading(101.0, 0.0, 1000.0)


# ── T005: a contribution nobody can know (FR-024h, B7-P1) ───────────────────


def test_spec001_b7_unknown_contribution_applies_nothing_and_stays_unknown():
    result = procedure_grading(90.0, None, 1000.0)
    assert result == ProcedureGrading(
        computed_delta=8.0, correction=None, applied=0.0, contribution_after=None
    )
    assert result.contribution_unknown


# ── T006: what an upload is (FR-024i, FR-024j, FR-024k) ─────────────────────


def test_spec001_b7_own_file_for_the_same_item_is_refused():
    """FR-024k: the student already uploaded this file for this item."""
    assert classify_upload(7, "item-a", own_upload_item="item-a", first_owner=7) == REFUSE_SAME_ITEM


def test_spec001_b7_own_file_for_another_item_is_refused():
    """FR-024j: the student already uploaded this file for another item."""
    assert (
        classify_upload(7, "item-b", own_upload_item="item-a", first_owner=7) == REFUSE_OTHER_ITEM
    )


def test_spec001_b7_another_students_file_is_a_copy_for_any_item():
    """FR-024i: another student sent it first — for this item or for another one."""
    assert classify_upload(7, "item-a", own_upload_item=None, first_owner=9) == COPY
    assert classify_upload(7, "item-z", own_upload_item=None, first_owner=9) == COPY


def test_spec001_b7_reuploading_an_own_copy_is_refused_not_graded_again():
    """Rule 1 before rule 2: a copy already recorded is never a second 0."""
    assert classify_upload(7, "item-a", own_upload_item="item-a", first_owner=9) == REFUSE_SAME_ITEM
    assert (
        classify_upload(7, "item-b", own_upload_item="item-a", first_owner=9) == REFUSE_OTHER_ITEM
    )


def test_spec001_b7_a_new_file_is_accepted():
    assert classify_upload(7, "item-a", own_upload_item=None, first_owner=None) == ACCEPT
    assert classify_upload(7, "item-a", own_upload_item=None, first_owner=7) == ACCEPT
