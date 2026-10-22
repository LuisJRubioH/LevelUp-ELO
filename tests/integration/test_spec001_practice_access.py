"""
Spec 001, follow-up F-4 (FR-037, FR-037a, User Story 8; tasks T101–T106): practice items,
answers and diagnostics only in courses the student is enrolled in — from their level's courses
or through an invitation. Everything else is refused with 403 before an item is served or any
rating, attempt, item difficulty, retry record or diagnostic is touched.

Both engines, through the API (`client` runs the app on this test's repository).
"""

import uuid

import pytest

from src.application.services.student_service import StudentService
from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    sql,
)

TOPIC = "Probabilidad"


def _course(repo, block="Universidad", items=3):
    course_id, by_topic = make_course(repo, [TOPIC], block=block, items_per_topic=items)
    return course_id, by_topic[TOPIC]


def _next(client, headers, course_id):
    return client.post("/api/student/next-question", headers=headers, json={"course_id": course_id})


def _answer(client, headers, item_id, key=None):
    if key is not None:
        headers = {**headers, "Idempotency-Key": key}
    return client.post(
        "/api/student/answer",
        headers=headers,
        json={"item_id": item_id, "selected_option": "A", "time_taken": 20},
    )


def _diagnostic_answers(item_ids):
    return {"answers": [{"item_id": i, "selected_option": "A"} for i in item_ids]}


def _state(repo, user_id, course_id, item_ids):
    """Everything a refused request must leave as it was."""
    attempts = sql(
        repo,
        "SELECT item_id, elo_before, elo_after, request_id FROM attempts WHERE user_id = ?"
        " ORDER BY id",
        (user_id,),
    )
    ratings = sql(
        repo,
        "SELECT course_id, topic, current_elo, rd FROM student_course_topic_elo"
        " WHERE user_id = ? ORDER BY course_id, topic",
        (user_id,),
    )
    difficulties = [repo.get_item_by_id(i)["difficulty"] for i in item_ids]
    return (
        [tuple(r) for r in attempts],
        [tuple(r) for r in ratings],
        difficulties,
        repo.get_diagnostic(user_id, course_id),
    )


# ── Denied (FR-037, FR-037a) ─────────────────────────────────────────────────


def test_spec001_next_question_outside_enrolment_is_forbidden(repo, client):
    """US8-AS1: a colegio student not enrolled in a universidad course gets no item from it; a
    course that does not exist is refused the same way."""
    student = make_student(repo, "colegio")
    course_id, _ = _course(repo)
    headers = headers_for(repo, student)

    for requested in (course_id, "no_such_course_" + uuid.uuid4().hex[:8]):
        response = _next(client, headers, requested)
        assert response.status_code == 403, response.text
        assert "item" not in response.json()


@pytest.mark.parametrize("with_key", [False, True], ids=["no-key", "retry-key"])
def test_spec001_answer_outside_enrolment_changes_nothing(repo, client, with_key):
    """US8-AS2: the answer is refused and no attempt, rating, item difficulty or retry record
    changes — with or without a retry key."""
    student = make_student(repo, "colegio")
    course_id, items = _course(repo)
    headers = headers_for(repo, student)
    key = "f4-" + uuid.uuid4().hex if with_key else None
    before = _state(repo, student, course_id, items)

    response = _answer(client, headers, items[0], key)

    assert response.status_code == 403, response.text
    assert _state(repo, student, course_id, items) == before
    assert rating_of(repo, student, course_id, TOPIC) is None
    if key:
        assert repo.get_answer_by_request_id(student, key) is None


def test_spec001_diagnostic_outside_enrolment_is_forbidden(repo, client):
    """US8-AS3: the diagnostic serves no question and its submission stores no baseline and no
    result."""
    student = make_student(repo, "colegio")
    course_id, items = _course(repo)
    headers = headers_for(repo, student)
    before = _state(repo, student, course_id, items)

    status = client.get(f"/api/student/diagnostic/{course_id}", headers=headers)
    submit = client.post(
        f"/api/student/diagnostic/{course_id}/submit",
        headers=headers,
        json=_diagnostic_answers(items),
    )

    assert status.status_code == 403, status.text
    assert "questions" not in status.json()
    assert submit.status_code == 403, submit.text
    assert _state(repo, student, course_id, items) == before
    assert repo.get_diagnostic(student, course_id) is None


# ── Allowed (FR-037) ─────────────────────────────────────────────────────────


def _invited_student(repo, course_id):
    """A colegio student enrolled through a teacher's group in a course of another level — what
    `enroll-by-code` stores (an enrolment carrying the group)."""
    teacher = make_teacher(repo)
    group_id = make_group(repo, teacher, course_id)
    student = make_student(repo, "colegio")
    enroll(repo, student, course_id, group_id)
    return student


@pytest.mark.parametrize("how", ["own-level", "invitation"])
def test_spec001_enrolled_students_practise_as_before(repo, client, how):
    """US8-AS4 [AS-IS]: enrolled from their level's courses or through an invitation, a student
    takes the diagnostic, gets the next item and answers it; the rating moves."""
    if how == "own-level":
        course_id, items = _course(repo, block="Colegio")
        student = make_student(repo, "colegio")
        enroll(repo, student, course_id)
    else:
        course_id, items = _course(repo, block="Universidad")
        student = _invited_student(repo, course_id)
    headers = headers_for(repo, student)

    status = client.get(f"/api/student/diagnostic/{course_id}", headers=headers)
    assert status.status_code == 200, status.text
    asked = [q["id"] for q in status.json()["questions"]]
    assert asked and set(asked) <= set(items)
    submit = client.post(
        f"/api/student/diagnostic/{course_id}/submit",
        headers=headers,
        json=_diagnostic_answers(asked),
    )
    assert submit.status_code == 200, submit.text
    baseline = rating_of(repo, student, course_id, TOPIC)
    assert baseline is not None

    served = _next(client, headers, course_id)
    assert served.status_code == 200, served.text
    item = served.json()["item"]
    assert item and item["id"] in items

    answered = _answer(client, headers, item["id"])
    assert answered.status_code == 200, answered.text
    assert rating_of(repo, student, course_id, TOPIC) != baseline


def test_spec001_leaving_a_course_closes_it(repo, client):
    """US8-AS5: after leaving a course the student gets no item from it and cannot answer its
    items — a retry of an accepted answer included; their stored ratings in it stay as they
    were."""
    student = make_student(repo, "colegio")
    course_id, items = _course(repo, block="Colegio")
    enroll(repo, student, course_id)
    headers = headers_for(repo, student)
    key = "f4-" + uuid.uuid4().hex
    assert _answer(client, headers, items[0], key).status_code == 200
    assert client.delete(f"/api/student/enroll/{course_id}", headers=headers).status_code == 204
    before = _state(repo, student, course_id, items)
    assert before[1], "the accepted answer stored a rating"

    assert _next(client, headers, course_id).status_code == 403
    assert _answer(client, headers, items[1]).status_code == 403
    assert _answer(client, headers, items[0], key).status_code == 403
    assert _state(repo, student, course_id, items) == before


# ── The service rule both engines answer (FR-037, FR-037a, SC-001) ───────────


def test_spec001_ensure_enrolled(repo):
    """`StudentService.ensure_enrolled` passes for an ordinary enrolment and for one made
    through an invitation, and raises PermissionError otherwise."""
    service = StudentService(repository=repo)
    own_course, _ = _course(repo, block="Colegio", items=1)
    invited_course, _ = _course(repo, block="Universidad", items=1)
    student = make_student(repo, "colegio")
    enroll(repo, student, own_course)
    invited = _invited_student(repo, invited_course)

    service.ensure_enrolled(student, own_course)
    service.ensure_enrolled(invited, invited_course)
    for user_id, course_id in (
        (student, invited_course),
        (invited, own_course),
        (student, "no_such_course_" + uuid.uuid4().hex[:8]),
    ):
        with pytest.raises(PermissionError):
            service.ensure_enrolled(user_id, course_id)

    repo.unenroll_user(student, own_course)
    with pytest.raises(PermissionError):
        service.ensure_enrolled(student, own_course)
