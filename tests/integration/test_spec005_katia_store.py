"""
Spec 005 (block 6): what KatIA's use case reads and writes, on SQLite and PostgreSQL.

Servings and their answered state (FR-008, FR-022), open exams (FR-025), and turns by serving
with their outcome (FR-037). Each test runs on both engines (constitution IV).
"""

import uuid
from datetime import datetime, timedelta, timezone

from tests.integration.conftest import answer, enroll, make_course, make_student, sql


def _course_with_two_items(repo, student):
    course, items = make_course(repo, ["t"], items_per_topic=2)
    enroll(repo, student, course)
    return course, items["t"]


def test_spec005_a_serving_is_answered_only_by_a_later_attempt(repo, student):
    """FR-022, FR-007, FR-008: the watermark separates this serving from earlier answers."""
    course, (item, other) = _course_with_two_items(repo, student)
    assert repo.get_latest_item_serve(student, item) is None

    first = repo.record_item_serve(student, item, course)
    serve = repo.get_latest_item_serve(student, item)
    assert serve == {"id": first, "attempt_watermark": 0}
    assert repo.has_attempt_after(student, item, serve["attempt_watermark"]) is False

    answer(repo, student, other)
    classmate = make_student(repo)
    enroll(repo, classmate, course)
    answer(repo, classmate, item)
    assert repo.has_attempt_after(student, item, serve["attempt_watermark"]) is False

    answer(repo, student, item, correct=False)
    assert repo.has_attempt_after(student, item, serve["attempt_watermark"]) is True

    second = repo.record_item_serve(student, item, course)
    again = repo.get_latest_item_serve(student, item)
    assert again["id"] == second and second > first
    assert again["attempt_watermark"] > serve["attempt_watermark"]
    assert repo.has_attempt_after(student, item, again["attempt_watermark"]) is False


def _exam(repo, student, course, item_ids, minutes):
    session_id = f"spec005_{uuid.uuid4().hex}"
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    repo.create_active_exam_session(
        session_id, student, course, None, item_ids, expires.isoformat()
    )
    return session_id


def test_spec005_open_exam_items_are_those_neither_submitted_nor_expired(repo, student):
    """FR-025: the server's exam state, whatever the client says."""
    course, (item, other) = _course_with_two_items(repo, student)
    _exam(repo, student, course, [item, "spec005-open-b"], minutes=10)
    _exam(repo, student, course, ["spec005-expired"], minutes=-10)
    submitted = _exam(repo, student, course, [other], minutes=10)
    sql(
        repo,
        "UPDATE active_exam_sessions SET submitted_at = CURRENT_TIMESTAMP WHERE id = ?",
        (submitted,),
    )
    classmate = make_student(repo)
    _exam(repo, classmate, course, ["spec005-classmate"], minutes=10)

    assert sorted(repo.get_open_exam_item_ids(student)) == sorted([item, "spec005-open-b"])
    assert repo.get_open_exam_item_ids(make_student(repo)) == []


def test_spec005_turns_are_read_by_serving_with_their_outcome(repo, student):
    """FR-037: each turn keeps its serving and outcome; V1's call without them still works."""
    course, (item, _) = _course_with_two_items(repo, student)
    s1 = repo.record_item_serve(student, item, course)
    s2 = repo.record_item_serve(student, item, course)
    repo.save_katia_interaction(
        student, course, item, "t", "m1", "r1", serve_id=s1, guard_outcome="accepted"
    )
    repo.save_katia_interaction(
        student, course, item, "t", "m2", "r2", serve_id=s1, guard_outcome="rejected:verdict"
    )
    repo.save_katia_interaction(
        student, course, item, "t", "m3", "r3", serve_id=s2, guard_outcome="accepted"
    )
    repo.save_katia_interaction(
        user_id=student,
        course_id=course,
        item_id=item,
        item_topic="t",
        student_message="v1",
        katia_response="sin serving",
    )

    assert repo.get_katia_turns(s1) == [
        {"student_message": "m1", "katia_response": "r1", "guard_outcome": "accepted"},
        {"student_message": "m2", "katia_response": "r2", "guard_outcome": "rejected:verdict"},
    ]
    assert [t["student_message"] for t in repo.get_katia_turns(s2)] == ["m3"]
    rows = sql(
        repo,
        "SELECT serve_id, guard_outcome FROM katia_interactions WHERE student_message = 'v1'"
        " AND user_id = ?",
        (student,),
    )
    assert [tuple(r) for r in rows] == [(None, None)]


def test_spec005_the_migration_is_idempotent(repo):
    """Data model: running the migration again changes nothing and keeps every row."""
    student = make_student(repo)
    course, (item, _) = _course_with_two_items(repo, student)
    serve = repo.record_item_serve(student, item, course)

    repo._migrate_db()

    assert repo.get_latest_item_serve(student, item)["id"] == serve
    assert sql(repo, "SELECT COUNT(*) FROM item_serves WHERE user_id = ?", (student,))[0][0] == 1
