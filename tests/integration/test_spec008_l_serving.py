"""
Spec 008 delivery L (US4; FR-030, plan-l.md O-IL1 … O-IL3): what the serving paths do with a
retired item.

New practice, new exams, the diagnostic and PvP never serve it; a template that holds it cannot
start and cannot be written; what was served before the retirement is honoured (a started exam is
graded, an answer in flight counts). Both engines, through the app's real endpoints.
"""

import json
import socket as _socket
import threading
import time

import pytest

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    set_rating,
    sql,
)
from tests.integration.test_spec008_l_item_life import LifeBank


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _student(repo, bank):
    student = make_student(repo)
    enroll(repo, student, bank.course)
    return student, headers_for(repo, student)


def _start(client, headers, course, n=3, template=None):
    body = {"course_id": course, "n_questions": n, "time_limit_minutes": 10}
    if template is not None:
        body["template_id"] = template
    return client.post("/api/student/exam/start", headers=headers, json=body)


def _retire(repo, bank, item_id):
    bank.item(item_id)["retired"] = True
    bank.sync(repo)


# ── Phase 1: pins that hold on the unchanged code ───────────────────────────


def test_spec008_l_a_started_exam_grades_an_item_retired_since(repo, client, tmp_path, monkeypatch):
    """Spec § Edge Cases: an exam started before the retirement grades the item as served."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.sync(repo)
    _, headers = _student(repo, bank)
    exam = _start(client, headers, bank.course).json()
    retired = exam["items"][0]["id"]
    _retire(repo, bank, retired)

    response = client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
        },
    )

    assert response.status_code == 200, response.text
    by_id = {r["item_id"]: r for r in response.json()["results"]}
    assert by_id[retired]["graded"] is True
    assert response.json()["total_questions"] == 3


def test_spec008_l_an_answer_to_an_item_retired_after_serving_is_accepted(
    repo, client, tmp_path, monkeypatch
):
    """O-IL2: an item served before its retirement is answered as any other — 200, and the
    rating moves."""
    bank = LifeBank(tmp_path, monkeypatch, n=1)
    bank.sync(repo)
    student, headers = _student(repo, bank)
    served = client.post(
        "/api/student/next-question", headers=headers, json={"course_id": bank.course}
    )
    assert served.status_code == 200, served.text
    item_id = served.json()["item"]["id"]
    _retire(repo, bank, item_id)

    response = client.post(
        "/api/student/answer",
        headers=headers,
        json={"item_id": item_id, "selected_option": "A", "time_taken": 20},
    )

    assert response.status_code == 200, response.text
    assert rating_of(repo, student, bank.course, "Vida") is not None
    assert sql(
        repo, "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND elo_valid = 1", (student,)
    ) == [(1,)]


# ── Phase 2: [CHANGE] — new exams, the diagnostic, templates and PvP (FR-030) ─


def test_spec008_l_new_exams_and_the_diagnostic_skip_a_retired_item(
    repo, client, tmp_path, monkeypatch
):
    """FR-030, US4-AS1, SC-001: a standard exam and the diagnostic asked for more items than the
    course holds draw every item in circulation and never the retired one."""
    bank = LifeBank(tmp_path, monkeypatch, n=4)
    retired = bank.ids[0]
    _retire(repo, bank, retired)
    _, headers = _student(repo, bank)

    exam = _start(client, headers, bank.course, n=4)
    diagnostic = client.get(f"/api/student/diagnostic/{bank.course}", headers=headers)

    assert exam.status_code == 200, exam.text
    assert {i["id"] for i in exam.json()["items"]} == set(bank.ids[1:])
    assert diagnostic.status_code == 200, diagnostic.text
    assert {q["id"] for q in diagnostic.json()["questions"]} == set(bank.ids[1:])


def _teacher_class(repo, client, bank):
    """The course's teacher and group, an enrolled student of the group, and a template of every
    item assigned to the group."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, bank.course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, bank.course, group)
    teacher_headers = headers_for(repo, teacher)
    created = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={"course_id": bank.course, "title": "L", "time_limit_min": 10, "item_ids": bank.ids},
    )
    assert created.status_code == 201, created.text
    template = created.json()["id"]
    assigned = client.post(
        f"/api/teacher/exam-templates/{template}/assignments",
        headers=teacher_headers,
        json={"group_ids": [group], "starts_at": None, "ends_at": None},
    )
    assert assigned.status_code in (200, 201), assigned.text
    return template, teacher_headers, headers_for(repo, student)


def test_spec008_l_a_template_with_a_retired_item_is_refused(repo, client, tmp_path, monkeypatch):
    """FR-030, O-IL3: a template holding a retired item does not start (today's 409); a retired
    id cannot enter a template, created or edited (today's 400)."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.sync(repo)
    template, teacher_headers, student_headers = _teacher_class(repo, client, bank)
    draft = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={
            "course_id": bank.course,
            "title": "L draft",
            "time_limit_min": 10,
            "item_ids": bank.ids[1:],
        },
    ).json()["id"]
    retired = bank.ids[0]
    _retire(repo, bank, retired)

    started = _start(client, student_headers, bank.course, template=template)
    created = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={"course_id": bank.course, "title": "L2", "time_limit_min": 10, "item_ids": [retired]},
    )
    edited = client.patch(
        f"/api/teacher/exam-templates/{draft}",
        headers=teacher_headers,
        json={"item_ids": bank.ids},
    )

    assert started.status_code == 409, started.text
    assert "ya no están disponibles" in started.json()["detail"]
    assert created.status_code == 400, created.text
    assert edited.status_code == 400, edited.text
    assert retired in created.json()["detail"] and retired in edited.json()["detail"]


@pytest.fixture
def live_api(repo):
    """The app on this test's repository, served by uvicorn on a free local port (a match needs
    both players on one event loop: tests/integration/test_pvp_enrolment.py)."""
    import uvicorn

    import api.dependencies as deps
    from api.main import app

    with _socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, lifespan="off", log_level="warning")
    )
    previous, deps._repo_instance = deps._repo_instance, repo
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 15
    while not server.started:
        assert time.monotonic() < deadline, "uvicorn did not start"
        time.sleep(0.05)
    try:
        yield f"ws://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(15)
        deps._repo_instance = previous


def _until(socket, kind, limit=40):
    for _ in range(limit):
        message = json.loads(socket.recv(timeout=15))
        if message["type"] == kind:
            return message
    raise AssertionError(f"no {kind} in {limit} messages")


def _answer_all(socket, items):
    for item in items:
        time.sleep(0.25)  # the League takes at most 5 messages per second (spec 007 FR-051)
        socket.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": "A"}))
        assert _until(socket, "answer_result")["item_id"] == item["id"]


def test_spec008_l_pvp_never_draws_a_retired_item(repo, live_api, tmp_path, monkeypatch):
    """FR-030, US4-AS1, SC-001: a course of ten items, one retired — a match asks for ten, so
    before L it took every item; now it takes the nine in circulation."""
    from websockets.sync.client import connect

    bank = LifeBank(tmp_path, monkeypatch, n=10)
    retired = bank.ids[0]
    _retire(repo, bank, retired)
    first, second = make_student(repo), make_student(repo)
    for student in (first, second):
        enroll(repo, student, bank.course)
        set_rating(repo, student, bank.course, "Vida", 1000.0)  # spec 007 G: a rated subject
    url = f"{live_api}/api/ws/pvp/{bank.course}"

    def token(user_id):
        return headers_for(repo, user_id)["Authorization"].removeprefix("Bearer ")

    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": token(first)}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": token(second)}))
        items = _until(waiting, "game_start")["items"]
        assert _until(joining, "game_start")["items"] == items
        _answer_all(waiting, items)
        _answer_all(joining, items)
        for socket in (waiting, joining):
            _until(socket, "game_end")

    assert {i["id"] for i in items} == set(bank.ids[1:])
