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


# ── T043: FR-029a (selection), FR-004 — the selection rating ────────────────


class _SelectionRepo:
    """Items of course C; stored ratings (C, T) = 1800 and (C, U) = 1000 → course 1400."""

    def __init__(self, rows=(("T", 1800.0), ("U", 1000.0)), diagnostic_elo=None):
        self.rows = [
            {
                "course_id": "C",
                "topic": t,
                "elo": e,
                "rd": 100.0,
                "origin": "practice",
                "approximate": False,
            }
            for t, e in rows
        ]
        self.diagnostic_elo = diagnostic_elo

    def get_items_from_db(self, topic=None, course_id=None, block=None):
        return [
            {"id": "t1", "difficulty": 1000.0, "topic": "T"},
            {"id": "u1", "difficulty": 1000.0, "topic": "U"},
        ]

    def get_answered_item_ids(self, _user_id):
        return []

    def get_course_topic_ratings(self, user_id, course_id=None):
        return [r for r in self.rows if course_id in (None, r["course_id"])]

    def get_diagnostic(self, _user_id, _course_id):  # must never seed the selection rating
        return None if self.diagnostic_elo is None else {"initial_elo": self.diagnostic_elo}


@pytest.mark.parametrize("topic_filter,expected", [("T", "mastery"), (None, "ok")])
def test_spec001_selection_rating_is_topic_or_course(topic_filter, expected):
    """Pool exhausted: the topic rating (1800) reaches mastery; the course rating (1400) does not."""
    service = StudentService(repository=_SelectionRepo())

    item, status = service.get_next_question(
        1, "C", topic_filter=topic_filter, session_correct_ids={"t1", "u1"}
    )

    assert status == expected  # "ok": the pool again (either item; equal difficulty is a draw)
    assert (item is None) == (expected == "mastery")


def test_spec001_unrated_course_selects_at_1000_and_ignores_the_diagnostic_average():
    service = StudentService(repository=_SelectionRepo(rows=(), diagnostic_elo=1900.0))

    assert service.ratings.selection_rating(1, "C") == 1000.0
    assert service.ratings.selection_rating(1, "C", "T") == 1000.0
    item, status = service.get_next_question(1, "C", session_correct_ids={"t1", "u1"})
    assert status == "ok"  # 1000 < 1800: the pool again, never mastery from a 1900 seed


# ── T051: FR-026 — the PvP expectation uses the course rating, read outside _lock ──


def test_spec001_pvp_lobby_rating_is_the_course_rating_read_outside_the_lock():
    import asyncio

    from api.websocket import pvp

    class Repo:
        lock_seen = []

        def get_course_topic_ratings(self, user_id, course_id=None):
            self.lock_seen.append(pvp._lock.locked())
            rows = [("C", "a", 1200.0), ("C", "b", 1000.0), ("D", "a", 2000.0)]
            return [
                {
                    "course_id": c,
                    "topic": t,
                    "elo": e,
                    "rd": 350.0,
                    "origin": "practice",
                    "approximate": False,
                }
                for c, t, e in rows
                if course_id in (None, c)
            ]

        def get_user_by_id(self, _user_id):  # the old all-course average: never used
            return {"current_elo": 1500.0}

    repo = Repo()

    assert asyncio.run(pvp._lobby_rating(repo, 1, "C")) == 1100.0
    assert asyncio.run(pvp._lobby_rating(repo, 1, "E")) == 1000.0
    assert repo.lock_seen == [False, False]
