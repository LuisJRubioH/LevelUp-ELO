"""
Spec 007 delivery L (US5; FR-050, FR-051): the League cannot be flooded.

- One live League socket per student: a second one, in any course and any phase, is closed with
  4409 before it reaches the lobby; the first is untouched (FR-050, US5-AS1).
- A frame over 4 KB, or beyond 5 messages per second, is dropped unparsed and gets no reply; ten
  dropped frames within ten seconds close the socket with 4429 (FR-051, US5-AS2).

Both engines, through the app's real WebSocket endpoint on uvicorn (see test_pvp_enrolment.py).
"""

import json
import time

import pytest

from tests.integration.conftest import enroll, make_course, make_student
from tests.integration.test_pvp_enrolment import (  # noqa: F401 — live_api is a fixture
    _course,
    _token,
    _until,
    live_api,
)

SILENCE_S = 1.0  # how long "no reply" is waited for


@pytest.fixture
def clock(monkeypatch):
    """The sockets' limits read a clock the test moves (spec 007 FR-051).

    The bucket refills while the server works through a burst, so with the real clock a server
    slower than one answer per 1/rate seconds refills a token before it reads the last frame of
    the burst. Here time passes only when the test says so: `clock[0] += seconds`.
    """
    from api.config import settings
    from api.websocket import pvp
    from api.websocket.limits import SocketLimits

    now = [0.0]
    monkeypatch.setattr(
        pvp,
        "_socket_limits",
        lambda: SocketLimits(
            max_frame_bytes=settings.pvp_max_frame_bytes,
            per_second=settings.pvp_max_messages_per_second,
            abuse_limit=settings.pvp_abuse_limit,
            clock=lambda: now[0],
        ),
    )
    return now


def _match(repo, live_api, connect):
    """Two enrolled students in one ten-item match: (waiting socket, joining socket, items)."""
    course_id, _ = make_course(repo, ["Fracciones", "Decimales"], items_per_topic=5)
    first, second = make_student(repo), make_student(repo)
    enroll(repo, first, course_id)
    enroll(repo, second, course_id)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    waiting, joining = connect(url), connect(url)
    waiting.send(json.dumps({"token": _token(repo, first)}))
    _until(waiting, "waiting")
    joining.send(json.dumps({"token": _token(repo, second)}))
    _until(waiting, "game_start")
    items = _until(joining, "game_start")["items"]
    return waiting, joining, items


def _answer(item, **extra):
    return json.dumps({"type": "answer", "item_id": item["id"], "selected": "A", **extra})


def _silent(socket):
    """True when nothing arrives within SILENCE_S."""
    try:
        socket.recv(timeout=SILENCE_S)
    except TimeoutError:
        return True
    return False


def _close_code(socket):
    from websockets.exceptions import ConnectionClosed

    with pytest.raises(ConnectionClosed) as closed:
        for _ in range(50):
            socket.recv(timeout=5)
    return closed.value.rcvd.code if closed.value.rcvd else None


def test_spec007_a_second_league_socket_is_refused(repo, live_api):
    """FR-050, US5-AS1: the same student's second League socket — another course too — is closed
    with 4409; the first stays in the lobby, is matched and plays."""
    from websockets.sync.client import connect

    course_id, other_course = _course(repo), _course(repo)
    student, rival = make_student(repo), make_student(repo)
    for course in (course_id, other_course):
        enroll(repo, student, course)
    enroll(repo, rival, course_id)

    with connect(f"{live_api}/api/ws/pvp/{course_id}") as first:
        first.send(json.dumps({"token": _token(repo, student)}))
        _until(first, "waiting")

        for course in (course_id, other_course):
            with connect(f"{live_api}/api/ws/pvp/{course}") as second:
                second.send(json.dumps({"token": _token(repo, student)}))
                assert _close_code(second) == 4409

        with connect(f"{live_api}/api/ws/pvp/{course_id}") as joining:
            joining.send(json.dumps({"token": _token(repo, rival)}))
            item = _until(first, "game_start")["items"][0]
            _until(joining, "game_start")
            first.send(_answer(item))
            assert _until(first, "answer_result")["item_id"] == item["id"]


def test_spec007_a_closed_league_socket_frees_the_student(repo, live_api):
    """FR-050: the limit is on live sockets — once the first one closes, the student can enter
    again."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    student = make_student(repo)
    enroll(repo, student, course_id)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with connect(url) as first:
        first.send(json.dumps({"token": _token(repo, student)}))
        _until(first, "waiting")
    time.sleep(0.3)

    with connect(url) as again:
        again.send(json.dumps({"token": _token(repo, student)}))
        assert _until(again, "waiting") == {"type": "waiting"}


def test_spec007_an_oversized_frame_is_dropped(repo, live_api):
    """FR-051, US5-AS2: a frame over 4 KB gets no reply, even a valid answer; the next answer
    is judged."""
    from websockets.sync.client import connect

    waiting, joining, items = _match(repo, live_api, connect)
    with waiting, joining:
        joining.send(_answer(items[0], pad="x" * 5000))
        assert _silent(joining)

        joining.send(_answer(items[1]))
        assert _until(joining, "answer_result")["item_id"] == items[1]["id"]


def test_spec007_a_burst_beyond_the_rate_is_dropped(repo, live_api, clock):
    """FR-051, US5-AS2: of six answers sent at once, five are judged and the sixth gets no reply;
    a second later answers are judged again. No time passes during the burst (`clock`), however
    long the server takes to judge it."""
    from websockets.sync.client import connect

    waiting, joining, items = _match(repo, live_api, connect)
    with waiting, joining:
        clock[0] += 1.1  # a full bucket: the token frame was spent at sign-in
        for item in items[:6]:
            joining.send(_answer(item))

        judged = [_until(joining, "answer_result")["item_id"] for _ in range(5)]
        assert judged == [item["id"] for item in items[:5]]
        assert _silent(joining)

        clock[0] += 1.1
        joining.send(_answer(items[6]))
        assert _until(joining, "answer_result")["item_id"] == items[6]["id"]


def test_spec007_persisting_abuse_closes_the_socket(repo, live_api):
    """FR-051, US5-AS2: ten dropped frames within ten seconds close the socket with 4429."""
    from websockets.sync.client import connect

    waiting, joining, items = _match(repo, live_api, connect)
    with waiting, joining:
        for _ in range(10):
            joining.send(_answer(items[0], pad="x" * 5000))

        assert _close_code(joining) == 4429


def test_spec007_an_oversized_sign_in_frame_is_dropped(repo, live_api):
    """FR-051: the limits apply from the first frame — an oversized token frame is dropped, and
    a proper one still signs the student in."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    student = make_student(repo)
    enroll(repo, student, course_id)

    with connect(f"{live_api}/api/ws/pvp/{course_id}") as socket:
        socket.send(json.dumps({"token": _token(repo, student), "pad": "x" * 5000}))
        assert _silent(socket)
        socket.send(json.dumps({"token": _token(repo, student)}))
        assert _until(socket, "waiting") == {"type": "waiting"}
