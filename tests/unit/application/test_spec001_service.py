"""
Spec 001 behaviour changes in StudentService (fake repository).

[CHANGE] tests: each was written before its implementation task and failed first.
"""

import logging

import pytest

from src.application.services.student_service import StudentService

_ITEM = {"id": "spec001_item", "topic": "Fracciones", "correct_option": "A"}


class _AnswerRepo:
    def __init__(self, badges_fail=False):
        self.badges_fail = badges_fail
        self.written = None

    def save_answer_transaction(self, *, compute, **_kwargs):
        self.written = compute(
            {"elo": 1000.0, "rd": 350.0, "item_difficulty": 1000.0, "item_rd": 350.0}
        )
        return True

    def award_achievement(self, *_args):
        if self.badges_fail:
            raise RuntimeError("badge store down")
        return False

    def get_study_streak(self, _user_id):
        return 0

    def get_total_attempts_count(self, _user_id):
        return 0


# ── T036: FR-015 — a badge failure is logged, the answer still returns ──────


def test_spec001_badge_failure_is_logged_and_the_answer_returns(caplog):
    repo = _AnswerRepo(badges_fail=True)

    with caplog.at_level(logging.ERROR):
        is_correct, result = StudentService(repository=repo).process_answer(1, _ITEM, "A", "", 20.0)

    assert is_correct is True
    assert result["elo_after"] == pytest.approx(1016.0)
    assert any(
        r.levelno >= logging.ERROR and "badge store down" in r.getMessage() + str(r.exc_info)
        for r in caplog.records
    )


# ── T039 contract: the result reports validity; an invalid attempt moves nothing ──


@pytest.mark.parametrize("seconds,valid", [(20.0, True), (2.0, False), (0, False), (None, True)])
def test_spec001_process_answer_reports_validity(seconds, valid):
    repo = _AnswerRepo()

    _, result = StudentService(repository=repo).process_answer(1, _ITEM, "A", "", seconds)

    attempt, item_difficulty, _ = repo.written
    assert result["elo_valid"] is valid and attempt["elo_valid"] is valid
    if valid:
        assert (result["elo_after"], item_difficulty) == (
            pytest.approx(1016.0),
            pytest.approx(984.0),
        )
    else:
        assert (result["elo_after"], result["rd_after"], item_difficulty) == (1000.0, 350.0, 1000.0)
        assert attempt["elo_after"] == attempt["elo_before"] == 1000.0
