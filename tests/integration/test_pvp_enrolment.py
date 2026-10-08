"""
Roadmap follow-up F-5: the PvP lobby admits students enrolled in the match's course.

`api/websocket/pvp.py` checks enrolment before a student joins the lobby (AGENTS § Security). It
read the course id under a key the repositories do not return, so every enrolled student was
closed with 4001 like a stranger. Both engines, through the app's real WebSocket endpoint.
"""

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


def test_pvp_admits_an_enrolled_student(repo, client):
    """An enrolled student passes authentication and waits in the lobby."""
    course_id = _course(repo)
    student = make_student(repo)
    enroll(repo, student, course_id)

    with client.websocket_connect(f"/api/ws/pvp/{course_id}") as socket:
        socket.send_json({"token": _token(repo, student)})
        assert socket.receive_json() == {"type": "waiting"}


def test_pvp_matches_two_enrolled_students(repo, client):
    """Two students enrolled in the course — one of them through a teacher's group, as an
    invitation enrols — are matched and both get the start of the game."""
    course_id = _course(repo)
    first, second = make_student(repo), make_student(repo)
    enroll(repo, first, course_id)
    enroll(repo, second, course_id, make_group(repo, make_teacher(repo), course_id))

    with client.websocket_connect(f"/api/ws/pvp/{course_id}") as waiting:
        waiting.send_json({"token": _token(repo, first)})
        assert waiting.receive_json() == {"type": "waiting"}
        with client.websocket_connect(f"/api/ws/pvp/{course_id}") as joining:
            joining.send_json({"token": _token(repo, second)})
            for socket in (waiting, joining):
                start = socket.receive_json()
                assert start["type"] == "game_start", start
                assert start["match_id"]


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
