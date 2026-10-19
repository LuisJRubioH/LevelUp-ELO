"""An exam assignment's window: dates are checked, stored in UTC, read back with their zone, and
a window open now lets the group's students see the exam. Both engines."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    sql,
)

COURSE = "algebra_basica"


def _template_for_a_group(repo, client):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, COURSE)
    headers = headers_for(repo, teacher)
    items = [item["id"] for item in repo.get_items_from_db(course_id=COURSE)[:2]]
    created = client.post(
        "/api/teacher/exam-templates",
        headers=headers,
        json={"course_id": COURSE, "title": "Ventana", "time_limit_min": 10, "item_ids": items},
    )
    assert created.status_code == 201, created.text
    return headers, group, created.json()["id"]


def _assign(client, headers, template, group, starts_at, ends_at):
    return client.post(
        f"/api/teacher/exam-templates/{template}/assignments",
        headers=headers,
        json={"group_ids": [group], "starts_at": starts_at, "ends_at": ends_at},
    )


@pytest.mark.parametrize(
    "starts_at, ends_at",
    [
        ("mañana", None),
        (None, "2026-13-45T25:00:00Z"),
        ("2026-10-12T10:00:00Z", "2026-10-11T10:00:00Z"),
    ],
)
def test_an_invalid_window_is_refused(repo, client, starts_at, ends_at):
    headers, group, template = _template_for_a_group(repo, client)

    response = _assign(client, headers, template, group, starts_at, ends_at)

    assert response.status_code == 422, response.text
    listed = client.get(f"/api/teacher/exam-templates/{template}/assignments", headers=headers)
    assert listed.json() == []


def test_a_window_is_read_back_in_utc(repo, client):
    headers, group, template = _template_for_a_group(repo, client)

    response = _assign(
        client, headers, template, group, "2026-10-12T08:00:00-05:00", "2026-10-12T10:30:00-05:00"
    )

    assert response.status_code == 201, response.text
    [assignment] = response.json()
    assert assignment["starts_at"] == "2026-10-12T13:00:00Z"
    assert assignment["ends_at"] == "2026-10-12T15:30:00Z"


def test_a_window_open_now_shows_the_exam_to_the_group(repo, client):
    headers, group, template = _template_for_a_group(repo, client)
    student = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, COURSE, group)  # exams are for enrolled students (spec 006 FR-020)
    now = datetime.now(timezone.utc)
    starts_at = (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    ends_at = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    assert _assign(client, headers, template, group, starts_at, ends_at).status_code == 201

    visible = client.get(
        "/api/student/exam/templates",
        headers=headers_for(repo, student),
        params={"course_id": COURSE},
    )

    assert visible.status_code == 200, visible.text
    assert template in {t["id"] for t in visible.json()}
