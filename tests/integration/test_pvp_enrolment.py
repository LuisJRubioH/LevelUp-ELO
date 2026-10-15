"""
Roadmap follow-up F-5: the PvP lobby admits students enrolled in the match's course.

`api/websocket/pvp.py` checks enrolment before a student joins the lobby (AGENTS § Security). It
read the course id under a key the repositories do not return, so every enrolled student was
closed with 4001 like a stranger. Both engines, through the app's real WebSocket endpoint.

A match needs two players on ONE event loop, as under uvicorn in production: the lobby hands the
waiting player's socket and asyncio.Event to the second player's coroutine. Starlette's TestClient
runs each WebSocket on its own loop, so the match test runs the app on a real uvicorn server.
"""

import gc
import json
import socket as _socket
import threading
import time

import pytest
from starlette.websockets import WebSocketDisconnect

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
)


def _token(repo, user_id):
    return headers_for(repo, user_id)["Authorization"].removeprefix("Bearer ")


def _course(repo):
    course_id, _ = make_course(repo, ["Fracciones"], items_per_topic=5)
    return course_id


def test_pvp_admits_an_enrolled_student(repo, client, caplog):
    """An enrolled student passes authentication and waits in the lobby; leaving the lobby is
    a clean disconnect, not an asyncio "Task exception was never retrieved" error."""
    course_id = _course(repo)
    student = make_student(repo)
    enroll(repo, student, course_id)

    with client.websocket_connect(f"/api/ws/pvp/{course_id}") as socket:
        socket.send_json({"token": _token(repo, student)})
        assert socket.receive_json() == {"type": "waiting"}
    gc.collect()

    assert not [r for r in caplog.records if "never retrieved" in r.getMessage()]


@pytest.fixture
def live_api(repo):
    """The app on this test's repository, served by uvicorn on a free local port."""
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
    """Read the socket until a message of `kind`; return it."""
    for _ in range(limit):
        message = json.loads(socket.recv(timeout=15))
        if message["type"] == kind:
            return message
    raise AssertionError(f"no {kind} in {limit} messages")


def _answer_all(socket, items):
    for item in items:
        socket.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": "A"}))
        assert _until(socket, "answer_result")["item_id"] == item["id"]


def test_pvp_matches_and_finishes_a_game_between_enrolled_students(repo, live_api):
    """Two students enrolled in the course — one of them through a teacher's group, as an
    invitation enrols — are matched, play every item and both get the result. The second to
    arrive (who owns the match timer) answers last, so finishing the game also stops it."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    first, second = make_student(repo), make_student(repo)
    enroll(repo, first, course_id)
    enroll(repo, second, course_id, make_group(repo, make_teacher(repo), course_id))
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": _token(repo, first)}))
        assert _until(waiting, "waiting") == {"type": "waiting"}
        joining.send(json.dumps({"token": _token(repo, second)}))
        starts = [_until(socket, "game_start") for socket in (waiting, joining)]
        assert starts[0]["match_id"] == starts[1]["match_id"]
        items = starts[0]["items"]
        assert len(items) == 5
        assert all("correct_option" not in item for item in items)  # V2-R9

        _answer_all(waiting, items)
        _answer_all(joining, items)
        ends = [_until(socket, "game_end") for socket in (waiting, joining)]

    assert [(e["your_score"], e["opp_score"]) for e in ends] == [(5, 5), (5, 5)]


def test_pvp_still_refuses_a_student_not_enrolled(repo, client):
    """Enrolment in another course does not open this one."""
    course_id, other = _course(repo), _course(repo)
    student = make_student(repo)
    enroll(repo, student, other)

    with client.websocket_connect(f"/api/ws/pvp/{course_id}") as socket:
        socket.send_json({"token": _token(repo, student)})
        with pytest.raises(WebSocketDisconnect) as closed:
            socket.receive_json()
        assert closed.value.code == 4001
