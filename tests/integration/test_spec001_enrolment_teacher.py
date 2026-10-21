"""
Spec 001 delivery TCH (User Story 11; FR-028v, FR-028w): no enrolment without a teacher.

From the catalogue a student enrols only in a course the teacher of their group reviews — a group
with no course, or the group's own course, whose teacher is approved and active — and the
enrolment is recorded with that group, so the course's procedures reach that teacher (spec 006
FR-050). Any other course is reached through an invitation. Both engines, through the API.
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

REFUSAL = "Pide a tu docente una invitación para este curso."


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _teacher(repo, approved=True, active=True):
    teacher = make_teacher(repo)
    sql(
        repo,
        "UPDATE users SET approved = ?, active = ? WHERE id = ?",
        (int(approved), int(active), teacher),
    )
    return teacher


def _student(repo, group_id=None):
    student = make_student(repo, "colegio")
    if group_id is not None:
        sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group_id, student))
    return student


def _enrolments(repo, student):
    rows = sql(
        repo,
        "SELECT course_id, group_id FROM enrollments WHERE user_id = ? ORDER BY course_id",
        (student,),
    )
    return [tuple(row) for row in rows]


def _group_of(repo, student):
    return sql(repo, "SELECT group_id FROM users WHERE id = ?", (student,))[0][0]


def _enrol(client, repo, student, course_id, **extra):
    return client.post(
        "/api/student/enroll",
        headers=headers_for(repo, student),
        json={"course_id": course_id, **extra},
    )


def _png() -> bytes:
    meta = PngInfo()
    meta.add_text("tch", uuid.uuid4().hex)
    output = io.BytesIO()
    Image.new("RGB", (2, 2), (30, 90, 150)).save(output, format="PNG", pnginfo=meta)
    return output.getvalue()


def test_spec001_a_group_without_a_course_enrols_with_its_teacher(repo, client):
    """US11-AS1: enrolled with the group, the student's group unchanged, and a procedure in that
    course is in the teacher's queue."""
    course, items = make_course(repo, ["tch_a"])
    teacher = _teacher(repo)
    group = make_group(repo, teacher)
    student = _student(repo, group)

    response = _enrol(client, repo, student, course)

    assert response.status_code == 201, response.text
    assert _enrolments(repo, student) == [(course, group)]
    assert _group_of(repo, student) == group
    upload = client.post(
        "/api/student/procedure",
        headers=headers_for(repo, student),
        data={"item_id": items["tch_a"][0]},
        files={"file": ("work.png", _png(), "image/png")},
    )
    assert upload.status_code in (200, 201), upload.text
    queue = client.get("/api/teacher/procedures", headers=headers_for(repo, teacher))
    assert queue.status_code == 200, queue.text
    assert [p["item_id"] for p in queue.json()] == [items["tch_a"][0]]


@pytest.mark.parametrize(
    "case",
    ["no group", "a group with another course", "teacher deactivated", "teacher not approved"],
)
def test_spec001_enrolment_without_the_groups_teacher_is_refused(repo, client, case):
    """US11-AS2: refused with the invitation message, nothing enrolled, the group unchanged."""
    course, _ = make_course(repo, ["tch_b"])
    other, _ = make_course(repo, ["tch_c"])
    group = None
    if case == "a group with another course":
        group = make_group(repo, _teacher(repo), other)
    elif case == "teacher deactivated":
        group = make_group(repo, _teacher(repo, active=False))
    elif case == "teacher not approved":
        group = make_group(repo, _teacher(repo, approved=False))
    student = _student(repo, group)

    response = _enrol(client, repo, student, course)

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == REFUSAL
    assert _enrolments(repo, student) == []
    assert _group_of(repo, student) == group


def test_spec001_the_groups_own_course_enrols_from_the_catalogue(repo, client):
    """US11-AS2: a student whose group has the course as its own enrols in it with the group."""
    course, _ = make_course(repo, ["tch_d"])
    group = make_group(repo, _teacher(repo), course)
    student = _student(repo, group)

    response = _enrol(client, repo, student, course)

    assert response.status_code == 201, response.text
    assert _enrolments(repo, student) == [(course, group)]


def test_spec001_a_course_already_enrolled_keeps_its_group(repo, client):
    """FR-028v: a course enrolled through an invitation's group keeps that group when the student
    asks for it from the catalogue again."""
    course, _ = make_course(repo, ["tch_e"])
    own = make_group(repo, _teacher(repo))
    invited = make_group(repo, _teacher(repo), course)
    student = _student(repo, own)
    enroll(repo, student, course, invited)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (own, student))

    response = _enrol(client, repo, student, course)

    assert response.status_code == 201, response.text
    assert _enrolments(repo, student) == [(course, invited)]
    assert _group_of(repo, student) == own


def test_spec001_the_course_list_says_which_courses_enrol(repo, client):
    """FR-028w: `enrollable` is true only for a catalogue course the rule accepts."""
    own_course, _ = make_course(repo, ["tch_f"])
    other_course, _ = make_course(repo, ["tch_g"])
    teacher = _teacher(repo)
    with_course = _student(repo, make_group(repo, teacher, own_course))
    without_course = _student(repo, make_group(repo, teacher))
    without_group = _student(repo)

    def enrollable(student):
        body = client.get("/api/student/courses", headers=headers_for(repo, student)).json()
        return {c["id"]: c["enrollable"] for c in body if c["id"] in (own_course, other_course)}

    assert enrollable(with_course) == {own_course: True, other_course: False}
    assert enrollable(without_course) == {own_course: True, other_course: True}
    assert enrollable(without_group) == {own_course: False, other_course: False}
