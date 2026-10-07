"""
Spec 001 characterization pins for StudentService (tasks T013, T015).

[AS-IS]: these hold on the code before the spec 001 refactor. The FR-015 pin records today's
swallowed badge failure only so that T036 can flip it deliberately.
"""

import pytest

from src.application.services.student_service import StudentService
from src.domain.elo.vector_elo import VectorRating


class _AnswerRepo:
    """Runs `compute` on a fixed locked state, as the real unit of work does."""

    def __init__(self, item_rd=123.0, badges_fail=False):
        self.item_rd = item_rd
        self.badges_fail = badges_fail
        self.written = None

    def save_answer_transaction(self, *, compute, **_kwargs):
        self.written = compute(
            {"elo": 1000.0, "rd": 350.0, "item_difficulty": 1000.0, "item_rd": self.item_rd}
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


_ITEM = {"id": "spec001_item", "topic": "Fracciones", "correct_option": "A"}


# ── T013: FR-005, FR-006, US1-AS1, US1-AS2 ──────────────────────────────────


@pytest.mark.parametrize("option,rating,difficulty", [("A", 1016.0, 984.0), ("B", 984.0, 1016.0)])
def test_spec001_answer_moves_rating_and_item_symmetrically(option, rating, difficulty):
    """D=1000, R=1000: correct → 1016 / item 984; wrong → 984 / item 1016; item RD kept."""
    repo = _AnswerRepo(item_rd=123.0)

    StudentService(repository=repo).process_answer(1, _ITEM, option, "", 20.0, VectorRating())

    attempt, item_difficulty, item_rd = repo.written
    assert attempt["elo_after"] == pytest.approx(rating, abs=1e-9)
    assert item_difficulty == pytest.approx(difficulty, abs=1e-9)
    assert item_rd == 123.0


def test_spec001_fr015_today_a_badge_failure_is_swallowed():
    """FR-015 today (Known Deviation D-3): the answer returns, the failure leaves no trace.

    Pinned to be flipped by T036 (log the failure, still return the result).
    """
    repo = _AnswerRepo(badges_fail=True)

    is_correct, cog = StudentService(repository=repo).process_answer(
        1, _ITEM, "A", "", 20.0, VectorRating()
    )

    assert is_correct is True
    assert cog["elo_after"] == pytest.approx(1016.0)
    assert "new_badges" not in cog


# ── T015: FR-016 (cooldown), FR-019, US2-AS3, US2-AS4, US2-AS5 ─────────────


class _PoolRepo:
    def __init__(self, items, answered=()):
        self.items = items
        self.answered = list(answered)

    def get_items_from_db(self, *_args, **_kwargs):
        return list(self.items)

    def get_answered_item_ids(self, _user_id):
        return self.answered


def _item(item_id):
    return {"id": item_id, "difficulty": 1000.0, "topic": "Fracciones"}


def _vector(rating):
    vector = VectorRating()
    vector.ratings["Fracciones"] = (rating, 100.0)
    return vector


@pytest.mark.parametrize("questions_so_far,expected", [(7, "historic"), (8, "failed")])
def test_spec001_failed_item_returns_after_three_questions(questions_so_far, expected):
    """US2-AS3: an item failed at question 5 is eligible only once count − 5 ≥ 3."""
    repo = _PoolRepo([_item("failed"), _item("historic")], answered=["failed", "historic"])

    item, status = StudentService(repository=repo).get_next_question(
        1,
        "Fracciones",
        _vector(1000.0),
        session_wrong_timestamps={"failed": 5},
        session_questions_count=questions_so_far,
    )

    assert (item["id"], status) == (expected, "ok")


def test_spec001_item_correct_this_session_is_never_offered():
    """US2-AS4: while another item is eligible, a correct-this-session item never comes back."""
    repo = _PoolRepo([_item("done"), _item("other")])
    service = StudentService(repository=repo)

    picks = {
        service.get_next_question(1, "Fracciones", _vector(1000.0), session_correct_ids={"done"})[
            0
        ]["id"]
        for _ in range(30)
    }

    assert picks == {"other"}


@pytest.mark.parametrize("rating,expected", [(1800.0, (None, "mastery")), (1799.0, ("a", "ok"))])
def test_spec001_exhausted_pool_mastery_threshold(rating, expected):
    """US2-AS5: nothing eligible → mastery at ≥ 1800, the pool again below."""
    repo = _PoolRepo([_item("a")])

    item, status = StudentService(repository=repo).get_next_question(
        1, "Fracciones", _vector(rating), session_correct_ids={"a"}
    )

    assert ((item or {}).get("id"), status) == expected
