"""
Spec 006 delivery AL (US7; FR-028): a template's items and options in an order drawn per session.

Each student who starts a template gets its items in an order of their own and each item's options
shuffled for their session; a resumed session keeps both orders; an option that refers to the
others stays last; grading compares the chosen text, so the order changes no result. Standard
exams keep their order. Both engines.
"""

import json

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

BANK_OPTIONS = ["A", "B", "C", "D"]


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _class(repo, client, students=1, n_items=8):
    """A course with `n_items` items (options A–D, A correct), a group, enrolled students and a
    template with every item, assigned to the group."""
    course, items = make_course(repo, [f"al_{n}" for n in range(n_items)])
    item_ids = [ids[0] for ids in items.values()]
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, course)
    headers = []
    for _ in range(students):
        student = make_student(repo)
        sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
        enroll(repo, student, course, group)
        headers.append(headers_for(repo, student))
    teacher_headers = headers_for(repo, teacher)
    created = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={"course_id": course, "title": "AL", "time_limit_min": 10, "item_ids": item_ids},
    )
    assert created.status_code == 201, created.text
    template = created.json()["id"]
    assigned = client.post(
        f"/api/teacher/exam-templates/{template}/assignments",
        headers=teacher_headers,
        json={"group_ids": [group], "starts_at": None, "ends_at": None},
    )
    assert assigned.status_code in (200, 201), assigned.text
    return {"course": course, "items": item_ids, "template": template, "headers": headers}


def _start(client, headers, course, template=None):
    body = {"course_id": course, "n_questions": 8, "time_limit_minutes": 10}
    if template is not None:
        body["template_id"] = template
    response = client.post("/api/student/exam/start", headers=headers, json=body)
    assert response.status_code == 200, response.text
    return response.json()


def _orders(exam):
    return [i["id"] for i in exam["items"]], [tuple(i["options"]) for i in exam["items"]]


def test_each_session_draws_its_own_order(repo, client):
    """US7-AS1, FR-028: every item, once, in an order of each session; the options shuffled."""
    c = _class(repo, client, students=3)
    exams = [_start(client, h, c["course"], c["template"]) for h in c["headers"]]

    item_orders = [_orders(e)[0] for e in exams]
    option_orders = [o for e in exams for o in _orders(e)[1]]
    assert all(sorted(order) == sorted(c["items"]) for order in item_orders)
    assert any(order != c["items"] for order in item_orders)
    assert all(sorted(o) == BANK_OPTIONS for o in option_orders)
    assert any(list(o) != BANK_OPTIONS for o in option_orders)


def test_a_resumed_session_keeps_its_order(repo, client):
    """US7-AS2, FR-028: resuming (FR-025) shows the same items and options in the same order."""
    c = _class(repo, client)
    first = _start(client, c["headers"][0], c["course"], c["template"])
    again = _start(client, c["headers"][0], c["course"], c["template"])

    assert again["resumed"] is True
    assert _orders(again) == _orders(first)


def test_the_order_changes_no_result(repo, client):
    """US7-AS3, FR-028: grading compares the chosen text; all correct is 100 %, wherever the
    correct option was shown."""
    c = _class(repo, client)
    exam = _start(client, c["headers"][0], c["course"], c["template"])

    submitted = client.post(
        "/api/student/exam/submit",
        headers=c["headers"][0],
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
        },
    )

    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["score_pct"] == 100.0
    assert submitted.json()["correct_count"] == len(c["items"])


def test_an_option_that_refers_to_the_others_stays_last(repo, client):
    """US7-AS1, FR-028: «Ninguna de las anteriores» is still the last option."""
    c = _class(repo, client, students=3)
    anchored = c["items"][0]
    sql(
        repo,
        "UPDATE items SET options = ? WHERE id = ?",
        (json.dumps(["Ninguna de las anteriores", "A", "B", "C"]), anchored),
    )

    for headers in c["headers"]:
        exam = _start(client, headers, c["course"], c["template"])
        options = next(i["options"] for i in exam["items"] if i["id"] == anchored)
        assert options[-1] == "Ninguna de las anteriores"


def test_standard_exams_keep_their_order(repo, client):
    """US7-AS4: a standard exam shows each item's options as the bank has them."""
    c = _class(repo, client)
    exam = _start(client, c["headers"][0], c["course"])

    assert all(i["options"] == BANK_OPTIONS for i in exam["items"])
