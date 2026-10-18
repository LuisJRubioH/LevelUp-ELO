"""
Spec 001, delivery B7, over HTTP on both engines: what the grading response, the notification and
the student's list report; retries; the copy and the two refusals; the history (tasks-b7.md
T015–T018). [CHANGE] tests, written before the routes changed.
"""

import io
import uuid

import pytest
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from tests.integration.conftest import (
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    set_rating,
    sql,
)

TOPIC = "Procedimientos"


def _png() -> bytes:
    """A real PNG nobody uploaded before (PostgreSQL keeps earlier runs' files)."""
    meta = PngInfo()
    meta.add_text("b7", uuid.uuid4().hex)
    output = io.BytesIO()
    Image.new("RGB", (2, 2), (30, 90, 150)).save(output, format="PNG", pnginfo=meta)
    return output.getvalue()


def _teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _classroom(repo, rating=1000.0):
    teacher = _teacher(repo)
    course, items = make_course(repo, [TOPIC], items_per_topic=2)
    group = make_group(repo, teacher, course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    set_rating(repo, student, course, TOPIC, rating)
    return {"teacher": teacher, "course": course, "items": items[TOPIC], "student": student}


def _upload(client, repo, student, item_id, image):
    return client.post(
        "/api/student/procedure",
        headers=headers_for(repo, student),
        data={"item_id": item_id},
        files={"file": ("work.png", image, "image/png")},
    )


def _queue_round(client, repo, teacher, submission_id):
    queue = client.get("/api/teacher/procedures", headers=headers_for(repo, teacher)).json()
    return next(p["review_round"] for p in queue if p["submission_id"] == submission_id)


def _grade(client, repo, teacher, submission_id, score, review_round):
    return client.post(
        "/api/teacher/procedures/grade",
        headers=headers_for(repo, teacher),
        json={"submission_id": submission_id, "teacher_score": score, "review_round": review_round},
    )


@pytest.fixture
def notifications(monkeypatch):
    import api.websocket.notifications as module

    sent = []
    monkeypatch.setattr(module, "notify_sync", lambda **kw: sent.append(kw))
    return sent


# ── T015: the rating effect shown is the amount applied (US9-AS9; FR-024f) ──


def test_spec001_b7_response_notification_and_list_report_the_amount_applied(
    repo, client, notifications
):
    room = _classroom(repo)
    item = room["items"][0]
    submission = _upload(client, repo, room["student"], item, _png()).json()["submission_id"]
    first = _grade(client, repo, room["teacher"], submission, 80, 1).json()
    assert (first["elo_delta"], first["computed_delta"], first["contribution"]) == (6, 6, 6)

    assert _upload(client, repo, room["student"], item, _png()).status_code == 200
    review_round = _queue_round(client, repo, room["teacher"], submission)
    assert review_round == 2
    second = _grade(client, repo, room["teacher"], submission, 30, review_round).json()

    assert (second["elo_delta"], second["computed_delta"], second["contribution"]) == (-10, -4, -4)
    assert [n["data"]["elo_delta"] for n in notifications] == [6, -10]
    assert notifications[-1]["data"]["computed_delta"] == -4
    listed = client.get("/api/student/procedures", headers=headers_for(repo, room["student"]))
    row = next(r for r in listed.json()["submissions"] if r["submission_id"] == submission)
    assert (row["elo_delta"], row["computed_delta"], row["contribution"]) == (-10, -4, -4)
    assert rating_of(repo, room["student"], room["course"], TOPIC) == 996.0


def test_spec001_b7_a_floored_grade_reports_what_the_floor_let_through(repo, client):
    room = _classroom(repo, rating=3.0)
    submission = _upload(client, repo, room["student"], room["items"][0], _png()).json()
    graded = _grade(client, repo, room["teacher"], submission["submission_id"], 0, 1).json()

    assert (graded["elo_delta"], graded["computed_delta"]) == (-3, -10)
    listed = client.get("/api/student/procedures", headers=headers_for(repo, room["student"]))
    assert listed.json()["submissions"][0]["elo_delta"] == -3


# ── T016: retries (US9-AS5; FR-024g) ────────────────────────────────────────


def test_spec001_b7_a_retried_grading_request_returns_the_same_body(repo, client, notifications):
    room = _classroom(repo)
    submission = _upload(client, repo, room["student"], room["items"][0], _png()).json()
    sid = submission["submission_id"]

    first = _grade(client, repo, room["teacher"], sid, 80, 1)
    retry = _grade(client, repo, room["teacher"], sid, 80, 1)

    assert first.status_code == retry.status_code == 200
    assert retry.json() == first.json()
    assert len(notifications) == 1
    assert rating_of(repo, room["student"], room["course"], TOPIC) == 1006.0
    # A round that is neither the current one nor already graded is refused.
    assert _grade(client, repo, room["teacher"], sid, 80, 7).status_code == 404


# ── T017: the copy and the two refusals (US9-AS10 … AS12; FR-024i … FR-024k) ──


def test_spec001_b7_upload_answers_copy_and_refusals(repo, client):
    room = _classroom(repo)
    copier = make_student(repo)
    set_rating(repo, copier, room["course"], TOPIC, 1000.0)
    first_item, second_item = room["items"]
    image = _png()
    assert _upload(client, repo, room["student"], first_item, image).status_code == 200

    copy = _upload(client, repo, copier, first_item, image)
    same_item = _upload(client, repo, room["student"], first_item, image)
    other_item = _upload(client, repo, room["student"], second_item, image)

    assert copy.status_code == 200
    body = copy.json()
    assert (body["status"], body["is_copy"], body["teacher_score"], body["elo_delta"]) == (
        "graded",
        True,
        0,
        -10,
    )
    assert rating_of(repo, copier, room["course"], TOPIC) == 990.0
    assert (same_item.status_code, same_item.json()["detail"]) == (
        409,
        "Ya subiste este archivo para este ejercicio.",
    )
    assert (other_item.status_code, other_item.json()["detail"]) == (
        409,
        "Este archivo pertenece a otro ejercicio.",
    )


# ── T018: the history and the copies list (FR-024e, FR-024i, FR-023) ────────


def test_spec001_b7_history_and_copies_are_for_the_groups_teacher_only(repo, client):
    room = _classroom(repo)
    outsider = _teacher(repo)
    item = room["items"][0]
    sid = _upload(client, repo, room["student"], item, _png()).json()["submission_id"]
    _grade(client, repo, room["teacher"], sid, 80, 1)
    _upload(client, repo, room["student"], item, _png())
    _grade(client, repo, room["teacher"], sid, 30, 2)

    history = client.get(
        f"/api/teacher/procedures/{sid}/gradings", headers=headers_for(repo, room["teacher"])
    )
    assert history.status_code == 200
    assert [(h["review_round"], h["grade"], h["applied"]) for h in history.json()] == [
        (1, 80, 6),
        (2, 30, -10),
    ]
    assert all(h["grader_name"] and h["reason"] == "teacher" for h in history.json())
    assert (
        client.get(
            f"/api/teacher/procedures/{sid}/gradings", headers=headers_for(repo, outsider)
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/api/teacher/procedures/{sid}/gradings", headers=headers_for(repo, room["student"])
        ).status_code
        == 403
    )

    # A copy in the teacher's group appears in their list, without the first sender.
    sender = make_student(repo)
    image = _png()
    _upload(client, repo, sender, room["items"][1], image)
    copier = make_student(repo)
    sql(
        repo,
        "UPDATE users SET group_id = (SELECT group_id FROM users WHERE id = ?) WHERE id = ?",
        (room["student"], copier),
    )
    _upload(client, repo, copier, room["items"][1], image)

    copies = client.get(
        "/api/teacher/procedures/copies", headers=headers_for(repo, room["teacher"])
    )
    assert [c["student_id"] for c in copies.json()] == [copier]
    assert "sender" not in str(copies.json()) and str(sender) not in {
        str(c["student_id"]) for c in copies.json()
    }
    outsider_copies = client.get(
        "/api/teacher/procedures/copies", headers=headers_for(repo, outsider)
    )
    assert outsider_copies.json() == []
