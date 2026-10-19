"""
Spec 006 delivery X2 (US3; FR-030 … FR-033): templates and results.

A template is a draft until it is assigned; its items lock once a student has started it (the
teacher duplicates it to change them); an assignment names groups of the template's course only
and commits all of them or none; the results count the teacher's own students on their first
submission, per student and per item, with the option each chose. Both engines.
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


def _teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher, headers_for(repo, teacher)


def _student_in(repo, course, group):
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, course, group)
    return student, headers_for(repo, student)


def _template(client, headers, course, items, title="X2"):
    created = client.post(
        "/api/teacher/exam-templates",
        headers=headers,
        json={"course_id": course, "title": title, "time_limit_min": 10, "item_ids": items},
    )
    assert created.status_code == 201, created.text
    return created.json()


def _assign(client, headers, template, groups):
    return client.post(
        f"/api/teacher/exam-templates/{template}/assignments",
        headers=headers,
        json={"group_ids": groups, "starts_at": None, "ends_at": None},
    )


def _class(repo, client):
    course, items = make_course(repo, ["x2_a", "x2_b"])
    item_ids = [ids[0] for ids in items.values()]
    teacher, headers = _teacher(repo)
    group = make_group(repo, teacher, course)
    template = _template(client, headers, course, item_ids)
    return {
        "course": course,
        "items": item_ids,
        "teacher": teacher,
        "headers": headers,
        "group": group,
        "template": template["id"],
    }


def _listed(client, headers, course):
    rows = client.get(f"/api/student/exam/templates?course_id={course}", headers=headers).json()
    return [r["id"] for r in rows]


# ── FR-030: a draft until assigned ───────────────────────────────────────────


def test_an_unassigned_template_is_a_draft(repo, client):
    """US3-AS3, FR-030: no student sees it; the teacher sees it as unassigned."""
    c = _class(repo, client)
    _, student = _student_in(repo, c["course"], c["group"])

    assert c["template"] not in _listed(client, student, c["course"])
    pending = client.get("/api/student/exam/pending", headers=student).json()
    assert c["template"] not in [p["template_id"] for p in pending]
    mine = client.get("/api/teacher/exam-templates", headers=c["headers"]).json()
    assert [t["assigned"] for t in mine if t["id"] == c["template"]] == [False]

    assert _assign(client, c["headers"], c["template"], [c["group"]]).status_code == 201

    assert c["template"] in _listed(client, student, c["course"])
    mine = client.get("/api/teacher/exam-templates", headers=c["headers"]).json()
    assert [t["assigned"] for t in mine if t["id"] == c["template"]] == [True]


# ── FR-031: locked once started ──────────────────────────────────────────────


def test_a_started_template_cannot_change_its_items(repo, client):
    """US3-AS2, FR-031: items locked once started; title editable; a duplicate is free."""
    c = _class(repo, client)
    _assign(client, c["headers"], c["template"], [c["group"]])
    _, student = _student_in(repo, c["course"], c["group"])
    started = client.post(
        "/api/student/exam/start",
        headers=student,
        json={"course_id": c["course"], "template_id": c["template"]},
    )
    assert started.status_code == 200, started.text
    url = f"/api/teacher/exam-templates/{c['template']}"

    items = client.patch(url, headers=c["headers"], json={"item_ids": c["items"][:1]})
    title = client.patch(url, headers=c["headers"], json={"title": "X2 renombrado"})
    copy = client.post(f"{url}/duplicate", headers=c["headers"])

    assert items.status_code == 409, items.text
    assert "Duplica" in items.json()["detail"]
    assert title.status_code == 200 and title.json()["title"] == "X2 renombrado"
    assert copy.status_code == 201, copy.text
    duplicate = copy.json()
    assert duplicate["id"] != c["template"] and duplicate["item_ids"] == c["items"]
    assert duplicate["title"] == "X2 renombrado (copia)"
    changed = client.patch(
        f"/api/teacher/exam-templates/{duplicate['id']}",
        headers=c["headers"],
        json={"item_ids": c["items"][:1]},
    )
    assert changed.status_code == 200, changed.text
    mine = {
        t["id"]: t for t in client.get("/api/teacher/exam-templates", headers=c["headers"]).json()
    }
    assert mine[c["template"]]["locked"] is True and mine[duplicate["id"]]["locked"] is False


# ── FR-032: one course, all groups or none ───────────────────────────────────


def test_an_assignment_is_one_course_and_all_or_nothing(repo, client):
    """FR-032: a group of another course refuses the whole assignment."""
    c = _class(repo, client)
    other_course, _ = make_course(repo, ["x2_otro"])
    other_group = make_group(repo, c["teacher"], other_course)

    response = _assign(client, c["headers"], c["template"], [c["group"], other_group])

    assert response.status_code == 422, response.text
    listed = client.get(
        f"/api/teacher/exam-templates/{c['template']}/assignments", headers=c["headers"]
    )
    assert listed.json() == []


# ── FR-033: results ──────────────────────────────────────────────────────────


def _stored_session(repo, user, template, course, answers, at):
    """A submission as an older database may hold it (a retake, or another teacher's student)."""
    sql(
        repo,
        "INSERT INTO exam_sessions (user_id, course_id, course_name, n_questions, correct_count,"
        " score_pct, global_elo_after, exam_template_id, created_at)"
        " VALUES (?, ?, '', ?, ?, ?, 0, ?, ?)",
        (
            user,
            course,
            len(answers),
            sum(1 for _, ok, _ in answers if ok),
            100.0 * sum(1 for _, ok, _ in answers if ok) / len(answers),
            template,
            at,
        ),
    )
    session = sql(
        repo,
        "SELECT MAX(id) FROM exam_sessions WHERE user_id = ? AND exam_template_id = ?",
        (user, template),
    )[0][0]
    for item, ok, option in answers:
        sql(
            repo,
            "INSERT INTO exam_responses (session_id, template_id, user_id, item_id, topic,"
            " is_correct, selected_option) VALUES (?, ?, ?, ?, 'x2', ?, ?)",
            (session, template, user, item, 1 if ok else 0, option),
        )


def test_results_count_my_students_first_submission(repo, client):
    """US3-AS1, FR-033: my students only, first submission, per student and item, options kept."""
    c = _class(repo, client)
    _assign(client, c["headers"], c["template"], [c["group"]])
    mine, student = _student_in(repo, c["course"], c["group"])
    exam = client.post(
        "/api/student/exam/start",
        headers=student,
        json={"course_id": c["course"], "template_id": c["template"]},
    ).json()
    submitted = client.post(
        "/api/student/exam/submit",
        headers=student,
        json={
            "session_id": exam["session_id"],
            "answers": [
                {"item_id": exam["items"][0]["id"], "selected_option": "A"},
                {"item_id": exam["items"][1]["id"], "selected_option": "B"},
            ],
        },
    )
    assert submitted.status_code == 200, submitted.text
    # A later retake (older data) and another teacher's student: neither counts.
    _stored_session(
        repo,
        mine,
        c["template"],
        c["course"],
        [(i["id"], True, "A") for i in exam["items"]],
        "2099-01-01 00:00:00",
    )
    other_teacher, _ = _teacher(repo)
    stranger, _ = _student_in(repo, c["course"], make_group(repo, other_teacher, c["course"]))
    _stored_session(
        repo,
        stranger,
        c["template"],
        c["course"],
        [(i["id"], True, "A") for i in exam["items"]],
        "2026-01-01 00:00:00",
    )

    results = client.get(
        f"/api/teacher/exam-templates/{c['template']}/results", headers=c["headers"]
    ).json()

    assert (results["n_students"], results["n_sessions"], results["avg_score"]) == (1, 1, 50.0)
    [row] = results["students"]
    assert row["user_id"] == mine and row["score_pct"] == 50.0
    assert [(a["item_id"], a["selected_option"]) for a in row["answers"]] == [
        (exam["items"][0]["id"], "A"),
        (exam["items"][1]["id"], "B"),
    ]
    by_item = {q["item_id"]: q for q in results["questions"]}
    assert by_item[exam["items"][1]["id"]]["choices"] == {"B": 1}
