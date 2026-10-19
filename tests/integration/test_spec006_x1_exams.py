"""
Spec 006 delivery X1 (US2; FR-020 … FR-024): exam access and attempts.

Only a student enrolled in the course lists, starts and submits its exams; a template is graded
once, and a submitted one leaves the student's pending exams; the course name comes from the
course; exam starts are limited per account; sessions 24 hours past their deadline are deleted;
an item removed from the bank after the start is reported, not a 409 forever. Both engines.
"""

import pytest

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


def _class(repo, client, course_name=None):
    """A course with three items, its teacher's group, an enrolled student and a template
    assigned to the group."""
    course, items = make_course(repo, ["x1_a", "x1_b", "x1_c"], name=course_name)
    item_ids = [ids[0] for ids in items.values()]
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, course, group)
    teacher_headers = headers_for(repo, teacher)
    created = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={"course_id": course, "title": "X1", "time_limit_min": 10, "item_ids": item_ids},
    )
    assert created.status_code == 201, created.text
    template = created.json()["id"]
    assigned = client.post(
        f"/api/teacher/exam-templates/{template}/assignments",
        headers=teacher_headers,
        json={"group_ids": [group], "starts_at": None, "ends_at": None},
    )
    assert assigned.status_code in (200, 201), assigned.text
    return {
        "course": course,
        "items": item_ids,
        "template": template,
        "student": student,
        "headers": headers_for(repo, student),
        "teacher_headers": teacher_headers,
    }


def _start(client, headers, course, template=None):
    body = {"course_id": course, "n_questions": 3, "time_limit_minutes": 10}
    if template is not None:
        body["template_id"] = template
    return client.post("/api/student/exam/start", headers=headers, json=body)


def _submit(client, headers, exam, course_name=""):
    return client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": exam["session_id"],
            "course_name": course_name,
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
        },
    )


def _sessions(repo, user_id):
    return sql(repo, "SELECT COUNT(*) FROM active_exam_sessions WHERE user_id = ?", (user_id,))[0][
        0
    ]


# ── FR-020: who may take an exam ─────────────────────────────────────────────


@pytest.mark.parametrize("who", ["not-enrolled", "teacher", "admin"])
def test_only_enrolled_students_reach_exams(repo, client, who):
    """US2-AS1, FR-020: 403 before any session; teachers and admins included."""
    c = _class(repo, client)
    if who == "teacher":
        user, headers = None, c["teacher_headers"]
    else:
        user = make_student(repo)
        if who == "admin":
            sql(repo, "UPDATE users SET role = 'admin' WHERE id = ?", (user,))
        headers = headers_for(repo, user)

    listed = client.get(f"/api/student/exam/templates?course_id={c['course']}", headers=headers)
    standard = _start(client, headers, c["course"])
    templated = _start(client, headers, c["course"], c["template"])
    submitted = client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={"session_id": "x1-none", "answers": []},
    )

    # A student never enrolled has no session of their own: 404, nothing to grade.
    expected_submit = 404 if who == "not-enrolled" else 403
    assert [r.status_code for r in (listed, standard, templated)] == [403] * 3
    assert submitted.status_code == expected_submit
    if user is not None:
        assert _sessions(repo, user) == 0
    if who != "not-enrolled":
        assert client.get("/api/student/exam/pending", headers=headers).status_code == 403


def test_a_student_no_longer_enrolled_cannot_submit(repo, client):
    """FR-020: the course is checked again at submission."""
    c = _class(repo, client)
    exam = _start(client, c["headers"], c["course"]).json()
    sql(
        repo,
        "DELETE FROM enrollments WHERE user_id = ? AND course_id = ?",
        (c["student"], c["course"]),
    )

    assert _submit(client, c["headers"], exam).status_code == 403


def test_a_course_without_items_is_404(repo, client):
    """FR-005 (spec 006 A): an enrolled course with no items has no exam to build."""
    course, _ = make_course(repo, [], name="Curso X1 vacío")
    student = make_student(repo)
    enroll(repo, student, course)

    response = _start(client, headers_for(repo, student), course)

    assert response.status_code == 404, response.text


def test_an_empty_course_is_refused_when_listing(repo, client):
    """FR-020: an empty course id selects no course."""
    c = _class(repo, client)
    response = client.get("/api/student/exam/templates?course_id=", headers=c["headers"])
    assert response.status_code == 422, response.text


# ── FR-021, FR-022: one attempt per template; pending exams ──────────────────


def test_a_template_is_graded_once(repo, client):
    """US2-AS2, FR-021: a second start of a submitted template is a 409; standard exams are
    unlimited."""
    c = _class(repo, client)
    first = _start(client, c["headers"], c["course"], c["template"])
    assert first.status_code == 200, first.text
    assert _submit(client, c["headers"], first.json()).status_code == 200

    again = _start(client, c["headers"], c["course"], c["template"])

    assert again.status_code == 409, again.text
    assert "Ya presentaste" in again.json()["detail"]
    for _ in range(2):
        standard = _start(client, c["headers"], c["course"])
        assert standard.status_code == 200, standard.text
        assert _submit(client, c["headers"], standard.json()).status_code == 200


def test_pending_drops_a_submitted_template(repo, client):
    """US2-AS2, FR-022: an assigned template is pending until submitted, then leaves both
    lists."""
    c = _class(repo, client)

    def pending():
        rows = client.get("/api/student/exam/pending", headers=c["headers"]).json()
        return [r["template_id"] for r in rows]

    def listed():
        rows = client.get(
            f"/api/student/exam/templates?course_id={c['course']}", headers=c["headers"]
        ).json()
        return [r["id"] for r in rows]

    assert c["template"] in pending() and c["template"] in listed()
    exam = _start(client, c["headers"], c["course"], c["template"]).json()
    assert c["template"] in pending()  # started, not submitted
    _submit(client, c["headers"], exam)

    assert c["template"] not in pending()
    assert c["template"] not in listed()


# ── FR-023: the course name, a limit, stale sessions ─────────────────────────


def test_the_course_name_comes_from_the_course(repo, client):
    """FR-023: the history keeps the course's name, not what the request says."""
    c = _class(repo, client, course_name="Curso X1 real")
    exam = _start(client, c["headers"], c["course"]).json()

    assert _submit(client, c["headers"], exam, course_name="Inventado").status_code == 200

    names = sql(repo, "SELECT course_name FROM exam_sessions WHERE user_id = ?", (c["student"],))
    assert [n[0] for n in names] == ["Curso X1 real"]


def test_exam_starts_are_limited(repo, client):
    """FR-023: starts are limited per account (10 a minute by default)."""
    c = _class(repo, client)
    codes = [_start(client, c["headers"], c["course"]).status_code for _ in range(11)]
    assert codes[:10] == [200] * 10
    assert codes[10] == 429


def test_stale_sessions_are_deleted(repo, client):
    """FR-023: sessions 24 hours past their deadline go, at the next start; fresh ones stay."""
    c = _class(repo, client)
    old = _start(client, c["headers"], c["course"]).json()["session_id"]
    fresh = _start(client, c["headers"], c["course"]).json()["session_id"]
    sql(
        repo,
        "UPDATE active_exam_sessions SET expires_at = ? WHERE id = ?",
        ("2000-01-01 00:00:00", old),
    )

    assert _start(client, c["headers"], c["course"]).status_code == 200

    ids = [r[0] for r in sql(repo, "SELECT id FROM active_exam_sessions", ())]
    assert old not in ids and fresh in ids


# ── FR-024: an item removed after the start ──────────────────────────────────


def test_a_removed_item_is_reported_not_blocking(repo, client):
    """US2-AS3, FR-024: the remaining items are graded; the removed one is not counted."""
    c = _class(repo, client)
    exam = _start(client, c["headers"], c["course"]).json()
    removed = exam["items"][0]["id"]
    sql(repo, "DELETE FROM items WHERE id = ?", (removed,))

    response = _submit(client, c["headers"], exam)

    assert response.status_code == 200, response.text
    body = response.json()
    by_id = {r["item_id"]: r for r in body["results"]}
    assert by_id[removed]["graded"] is False
    assert all(r["graded"] for i, r in by_id.items() if i != removed)
    assert body["total_questions"] == len(exam["items"]) - 1
