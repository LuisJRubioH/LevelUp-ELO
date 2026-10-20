"""
Spec 006 delivery P1 (US5; FR-050, FR-051): the procedures queue.

A pending procedure reaches the teachers of the groups that link the student to the item's
course — by enrolment or by main group — for active, non-test students only, so none is left
without a teacher; the same teachers grade it. A resubmission clears the AI score and feedback
of the earlier round. Both engines.
"""

import io
import uuid

import pytest
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    sql,
)


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _png() -> bytes:
    meta = PngInfo()
    meta.add_text("p1", uuid.uuid4().hex)
    output = io.BytesIO()
    Image.new("RGB", (2, 2), (90, 30, 150)).save(output, format="PNG", pnginfo=meta)
    return output.getvalue()


def _teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _upload(client, repo, student, item_id):
    response = client.post(
        "/api/student/procedure",
        headers=headers_for(repo, student),
        data={"item_id": item_id},
        files={"file": ("work.png", _png(), "image/png")},
    )
    assert response.status_code in (200, 201), response.text
    return sql(
        repo,
        "SELECT id FROM procedure_submissions WHERE student_id = ? AND item_id = ?",
        (student, item_id),
    )[0][0]


def _queue(client, repo, teacher):
    response = client.get("/api/teacher/procedures", headers=headers_for(repo, teacher))
    assert response.status_code == 200, response.text
    return {p["submission_id"]: p for p in response.json()}


def _world(repo):
    """Teacher A: group GA in course A. Teacher B: group GB in course B."""
    course_a, items_a = make_course(repo, ["p1_a"], items_per_topic=2)
    course_b, items_b = make_course(repo, ["p1_b"], items_per_topic=2)
    teacher_a, teacher_b = _teacher(repo), _teacher(repo)
    return {
        "course_a": course_a,
        "course_b": course_b,
        "item_a": items_a["p1_a"][0],
        "item_b": items_b["p1_b"][0],
        "teacher_a": teacher_a,
        "teacher_b": teacher_b,
        "group_a": make_group(repo, teacher_a, course_a),
        "group_b": make_group(repo, teacher_b, course_b),
    }


# ── FR-050: the queue follows the item's course ──────────────────────────────


def test_the_queue_follows_the_items_course(repo, client):
    """US5-AS1, FR-050: a student with no main group and one whose main group is another
    course's reach the teacher of the item's course — and only that teacher grades them."""
    w = _world(repo)
    no_group = make_student(repo)
    enroll(repo, no_group, w["course_b"], w["group_b"])
    elsewhere = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (w["group_a"], elsewhere))
    enroll(repo, elsewhere, w["course_a"], w["group_a"])
    enroll(repo, elsewhere, w["course_b"], w["group_b"])

    lone = _upload(client, repo, no_group, w["item_b"])
    moved = _upload(client, repo, elsewhere, w["item_b"])
    own = _upload(client, repo, elsewhere, w["item_a"])

    queue_a, queue_b = _queue(client, repo, w["teacher_a"]), _queue(client, repo, w["teacher_b"])
    assert set(queue_b) >= {lone, moved} and own not in queue_b
    assert own in queue_a and lone not in queue_a and moved not in queue_a

    graded = client.post(
        "/api/teacher/procedures/grade",
        headers=headers_for(repo, w["teacher_b"]),
        json={"submission_id": moved, "teacher_score": 80, "review_round": 1},
    )
    refused = client.post(
        "/api/teacher/procedures/grade",
        headers=headers_for(repo, w["teacher_a"]),
        json={"submission_id": lone, "teacher_score": 80, "review_round": 1},
    )
    assert graded.status_code == 200, graded.text
    assert refused.status_code == 404, refused.text


def test_inactive_and_test_students_are_not_queued(repo, client):
    """US5-AS1, FR-050: only active, non-test students' procedures are in the queue."""
    w = _world(repo)
    students = []
    for _ in range(3):
        student = make_student(repo)
        sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (w["group_a"], student))
        enroll(repo, student, w["course_a"], w["group_a"])
        students.append((student, _upload(client, repo, student, w["item_a"])))
    (_, active), (inactive, gone), (tester, hidden) = students
    sql(repo, "UPDATE users SET active = 0 WHERE id = ?", (inactive,))
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (tester,))

    queue = _queue(client, repo, w["teacher_a"])

    assert active in queue and gone not in queue and hidden not in queue
    assert repo.get_pending_submissions_count(w["teacher_a"]) == 1


# ── FR-051: the AI score of an earlier round ─────────────────────────────────


def test_a_resubmission_clears_the_ai_score(repo, client):
    """US5-AS2, FR-051: the queue shows the AI score and feedback; a resubmission clears both."""
    w = _world(repo)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (w["group_a"], student))
    enroll(repo, student, w["course_a"], w["group_a"])
    submission = _upload(client, repo, student, w["item_a"])
    repo.save_ai_proposed_score(student, w["item_a"], 72.0, "Falta justificar el paso 2.")

    before = _queue(client, repo, w["teacher_a"])[submission]
    assert (before["ai_score"], before["ai_feedback"]) == (72.0, "Falta justificar el paso 2.")

    assert _upload(client, repo, student, w["item_a"]) == submission
    after = _queue(client, repo, w["teacher_a"])[submission]

    assert (after["ai_score"], after["ai_feedback"], after["review_round"]) == (None, None, 2)
