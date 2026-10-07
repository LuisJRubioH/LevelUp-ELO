"""
Spec 001 characterization pins on both engines (tasks T018, T019, T020).

[AS-IS]: every test runs on SQLite and PostgreSQL (`repo` fixture) and holds on the code before
the spec 001 refactor. Ratings are read only through `rating_of`; answers go only through
`answer` (tests/integration/conftest.py), so the store can move without touching a number here.
"""

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest

from tests.integration.conftest import (
    answer,
    make_course,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    sql,
)
from src.domain.elo.vector_elo import VectorRating

TOPIC = "Fracciones"


def _course(repo, items_per_topic=1):
    course_id, items = make_course(repo, [TOPIC], items_per_topic=items_per_topic)
    return course_id, items[TOPIC]


def _difficulty(repo, item_id):
    return float(repo.get_item_by_id(item_id)["difficulty"])


def _rating_state(repo, user_id):
    rows = sql(
        repo,
        "SELECT topic, current_elo, rd FROM student_topic_elo WHERE user_id = ? ORDER BY topic",
        (user_id,),
    )
    current = sql(repo, "SELECT current_elo FROM users WHERE id = ?", (user_id,))[0][0]
    return [tuple(r) for r in rows], current


# ── T018: FR-022, FR-023 (grade range), FR-024, US4-AS1, US4-AS3, US4-AS5 ─────


def _pending_submission(repo, student, item_id):
    return sql(
        repo,
        """INSERT INTO procedure_submissions
           (student_id, item_id, item_content, image_data, status)
           VALUES (?, ?, ?, ?, 'pending') RETURNING id""",
        (student, item_id, "spec001 procedure", b"spec001 image"),
    )[0][0]


@pytest.mark.parametrize("grade,expected", [(80.0, 1106.0), (50.0, 1100.0)])
def test_spec001_validated_grade_adds_grade_minus_50_times_02(repo, student, grade, expected):
    """US4-AS1: grade 80 → +6.0 on the item's topic; edge "grade 50" → +0, still applied."""
    course_id, (item_id,) = _course(repo)
    repo.set_topic_elo_baseline(student, TOPIC, 1100.0)
    submission = _pending_submission(repo, student, item_id)

    assert repo.validate_procedure_submission(submission, teacher_score=grade)

    assert rating_of(repo, student, course_id, TOPIC) == expected
    applied, delta = sql(
        repo, "SELECT elo_applied, elo_delta FROM procedure_submissions WHERE id = ?", (submission,)
    )[0]
    assert (int(applied), float(delta)) == (1, expected - 1100.0)


def test_spec001_grade_out_of_range_changes_nothing(repo, student):
    """US4-AS3: grade 101 → ValueError; the rating and the submission stay as they were."""
    course_id, (item_id,) = _course(repo)
    repo.set_topic_elo_baseline(student, TOPIC, 1100.0)
    submission = _pending_submission(repo, student, item_id)

    with pytest.raises(ValueError):
        repo.validate_procedure_submission(submission, teacher_score=101.0)

    assert rating_of(repo, student, course_id, TOPIC) == 1100.0
    status = sql(repo, "SELECT status FROM procedure_submissions WHERE id = ?", (submission,))
    assert status[0][0] == "pending"


def test_spec001_ai_proposed_score_changes_no_rating(repo, student):
    """US4-AS5: an AI-proposed score moves the submission to review, never a rating."""
    course_id, (item_id,) = _course(repo)
    repo.set_topic_elo_baseline(student, TOPIC, 1100.0)
    _pending_submission(repo, student, item_id)
    before = _rating_state(repo, student)

    repo.save_ai_proposed_score(student, item_id, 100.0, "spec001 ai feedback")

    assert _rating_state(repo, student) == before
    assert rating_of(repo, student, course_id, TOPIC) == 1100.0


# ── T019: FR-025, US5-AS4 ────────────────────────────────────────────────────


def test_spec001_practice_after_pvp_starts_from_the_post_match_rating(repo):
    """US5-AS4: the next course-mode practice answer reads the rating the match left."""
    a, b = make_student(repo), make_student(repo)
    course_id, (item_id,) = _course(repo)
    match_id = repo.create_pvp_match(course_id, a, b, [item_id])

    repo.finish_pvp_match(
        match_id=match_id,
        winner_id=a,
        score_p1=3,
        score_p2=0,
        elo_delta_p1=12.0,
        elo_delta_p2=-12.0,
        p1_id=a,
        p2_id=b,
    )
    _, cog = answer(repo, a, item_id, correct=True, elo_topic=course_id)

    assert cog["elo_before"] == 1012.0


# ── T020: FR-007, FR-008 boundaries, FR-028e, FR-028g, FR-032 (storage) ───────


@pytest.mark.parametrize(
    "seconds,moves",
    [(3.0, True), (600.0, True), (None, True), (2.99, False), (600.01, False)],
)
def test_spec001_response_time_window_is_inclusive(repo, student, seconds, moves):
    """Edges "exactly 3 s / 600 s valid", "missing time = 30 s": the window is [3, 600].

    Outside it the attempt is recorded (FR-007) and nothing moves (FR-008).
    """
    course_id, (item_id,) = _course(repo)

    answer(repo, student, item_id, correct=True, seconds=seconds)

    if moves:
        assert rating_of(repo, student, course_id, TOPIC) == 1016.0
        assert _difficulty(repo, item_id) == 984.0
    else:
        assert rating_of(repo, student, course_id, TOPIC) is None
        assert _difficulty(repo, item_id) == 1000.0
    recorded = sql(
        repo, "SELECT elo_valid FROM attempts WHERE user_id = ? AND item_id = ?", (student, item_id)
    )
    assert [int(r[0]) for r in recorded] == [1 if moves else 0]


def test_spec001_attempt_history_keeps_each_attempts_rating(repo, student):
    """FR-028e: student and teacher history return one row per attempt with its elo_after."""
    _, (first, second) = _course(repo, items_per_topic=2)
    vector = VectorRating()
    expected = [vector.update(TOPIC, 1000.0, 1.0)[0]]

    answer(repo, student, first, correct=True)
    expected.append(vector.update(TOPIC, 1000.0, 0.0)[0])
    answer(repo, student, second, correct=False)

    latest = sorted(a["elo_after"] for a in repo.get_latest_attempts(student))
    detail = sorted(a["elo_after"] for a in repo.get_student_attempts_detail(student))
    assert latest == pytest.approx(sorted(expected), abs=1e-2)
    assert detail == pytest.approx(sorted(expected), abs=1e-2)


def test_spec001_weekly_snapshot_is_returned_unchanged(repo, student):
    """FR-028g: a saved weekly ranking row is history; later rating changes do not touch it."""
    group_id = make_group(repo, make_teacher(repo))
    week_start = date.today()
    sql(
        repo,
        """INSERT INTO weekly_rankings
           (week_start, week_end, group_id, rank, user_id, username, global_elo, attempts_count)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            str(week_start),
            str(week_start + timedelta(days=6)),
            group_id,
            1,
            student,
            "spec001_snapshot",
            1234.5,
            3,
        ),
    )
    _, (item_id,) = _course(repo)
    answer(repo, student, item_id, correct=True)

    history = repo.get_ranking_history(group_id)

    assert [
        (str(h["week_start"]), h["rank"], h["username"], h["global_elo"], h["attempts_count"])
        for h in history
    ] == [(str(week_start), 1, "spec001_snapshot", 1234.5, 3)]


def test_spec001_exam_storage_writes_no_rating(repo, student):
    """FR-032, US6-AS4 (storage half): saving and completing an exam leaves every rating as is."""
    course_id, (item_id,) = _course(repo)
    repo.set_topic_elo_baseline(student, TOPIC, 1100.0)
    before = _rating_state(repo, student)
    result = {
        "results": [],
        "correct_count": 1,
        "total_questions": 1,
        "score_pct": 100.0,
        "global_elo_after": 1100.0,
    }

    repo.save_exam_session(student, course_id, "spec001 exam", 1, 1, 100.0, 1100.0)
    session_id = uuid.uuid4().hex
    repo.create_active_exam_session(
        session_id=session_id,
        user_id=student,
        course_id=course_id,
        template_id=None,
        item_ids=[item_id],
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
    )
    completed = repo.complete_active_exam_session(
        session_id,
        student,
        "spec001 exam",
        result,
        [{"item_id": item_id, "topic": TOPIC, "is_correct": True}],
    )

    assert completed is True
    assert _rating_state(repo, student) == before
    assert _difficulty(repo, item_id) == 1000.0
