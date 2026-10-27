"""
Spec 007 delivery G1 (US2; FR-020, FR-021, FR-023, FR-024): who may enter the League.

- FR-020 (O-G2, O-G3): a student with no rating in the subject is refused at entry with 4413 and
  never queued; a rating that cannot be read is a server error (4500), never "no rating".
- FR-021 (O-G7): a test user meets only test users, on entry and on every window step.
- FR-023 (O-G8): a student with a match still in memory — away in the grace, or gone after
  answering every item — cannot enter another queue: 4412, and the match is left as it was.
- FR-024 (O-G4): each refusal has its own close code — 4001 session, 4002 not a student, 4004 not
  enrolled, 4500 server error.

Both engines, through the app's real WebSocket endpoint (uvicorn where two players must share one
event loop; see test_pvp_enrolment.py). The server runs in this process: the window step, the
match and the grace are shortened with `monkeypatch`, and the lobby is read in memory.
"""

import json
import time

import pytest
from starlette.websockets import WebSocketDisconnect

from tests.integration.conftest import (
    enroll,
    league_player,
    make_course,
    make_student,
    make_teacher,
    sql,
)
from tests.integration.test_pvp_enrolment import (  # noqa: F401 — live_api is a fixture
    _token,
    _until,
    live_api,
)
from tests.integration.test_pvp_limits import _close_code
from tests.integration.test_spec007_f_match_flow import _answer, _none_of, timing  # noqa: F401

TOPIC = "Fracciones"
WRONG = "B"


def _course(repo):
    course_id, _ = make_course(repo, [TOPIC], items_per_topic=5)
    return course_id


def _enter(repo, connect, url, student):
    socket = connect(url)
    socket.send(json.dumps({"token": _token(repo, student)}))
    return socket


def _first_close(socket):
    """The close code of a socket refused at entry, asserting it sent nothing first."""
    from websockets.exceptions import ConnectionClosed

    with pytest.raises(ConnectionClosed) as closed:
        message = socket.recv(timeout=10)
        raise AssertionError(f"sent {message} before closing")
    return closed.value.rcvd.code if closed.value.rcvd else None


def _refused(client, course_id, token):
    """The close code of a TestClient socket refused at entry."""
    with client.websocket_connect(f"/api/ws/pvp/{course_id}") as socket:
        socket.send_json({"token": token})
        with pytest.raises(WebSocketDisconnect) as closed:
            socket.receive_json()
    return closed.value.code


def _in_play(user_id):
    from api.websocket import pvp

    return user_id in pvp.players_in_play()


def _until_free(user_id, within=5.0):
    """Wait until the student holds no slot and no match in memory (a closed match leaves
    `_matches` right after its `game_end` is sent)."""
    deadline = time.monotonic() + within
    while _in_play(user_id):
        assert time.monotonic() < deadline, f"user {user_id} still in play"
        time.sleep(0.05)


@pytest.fixture
def step(monkeypatch):
    """Shorten the window's step period (spec 007 FR-030): `step(seconds)`."""
    from api.config import settings

    def set_(seconds):
        monkeypatch.setattr(settings, "pvp_window_every_s", seconds)

    return set_


# ── FR-020, US2-AS1: a rating in the subject ─────────────────────────────────


def test_spec007_a_student_without_rating_is_not_queued(repo, live_api):
    """FR-020, US2-AS1: an enrolled student with no rating in the subject is closed with 4413
    before any `waiting`; no slot of theirs is left, so a rated student who joins next waits
    alone instead of meeting them."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    unrated = make_student(repo)
    enroll(repo, unrated, course_id)
    rated = league_player(repo, course_id)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, unrated) as refused:
        assert _first_close(refused) == 4413
    assert not _in_play(unrated)

    with _enter(repo, connect, url, rated) as alone:
        assert _until(alone, "waiting")["type"] == "waiting"
        assert _none_of(alone, "game_start", 1.0)


def test_spec007_a_failed_rating_read_is_a_server_error(repo, client, monkeypatch):
    """FR-024 (O-G3): when the rating cannot be read the entry is a server error, 4500 — not
    "no rating" (4413), and not a queue place at the internal 1000."""
    from src.application.services.rating_read_service import RatingReadService

    course_id = _course(repo)
    student = league_player(repo, course_id)

    def broken(self, user_id, course):
        raise RuntimeError("database down")

    monkeypatch.setattr(RatingReadService, "course_rating_of", broken)

    assert _refused(client, course_id, _token(repo, student)) == 4500
    assert not _in_play(student)


# ── FR-021, US2-AS2: test users only with test users ─────────────────────────


def test_spec007_a_test_user_and_a_real_student_never_meet(repo, live_api, step):
    """FR-021, US2-AS2: a test user and a real student with the same rating wait in the same
    subject and never meet — neither at entry nor as their windows widen; a second real student
    who joins meets the real one, and the test user keeps waiting."""
    from websockets.sync.client import connect

    step(0.3)
    course_id = _course(repo)
    tester = league_player(repo, course_id, test_user=True)
    real, other_real = league_player(repo, course_id), league_player(repo, course_id)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, tester) as test_socket:
        _until(test_socket, "waiting")
        with _enter(repo, connect, url, real) as real_socket:
            _until(real_socket, "waiting")
            # Several window steps pass: both look for a partner again, and find none.
            assert _none_of(real_socket, "game_start", 1.2)
            assert _none_of(test_socket, "game_start", 0.1)

            with _enter(repo, connect, url, other_real) as joining:
                start = _until(joining, "game_start")
                assert _until(real_socket, "game_start")["match_id"] == start["match_id"]
            assert _none_of(test_socket, "game_start", 0.5)

    players = sql(
        repo, "SELECT player1_id, player2_id FROM pvp_matches WHERE course_id = ?", (course_id,)
    )
    assert [set(row) for row in players] == [{real, other_real}]


def test_spec007_two_test_users_meet(repo, live_api):
    """FR-021 (O-G7): two test users rated in the subject meet each other."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    first = league_player(repo, course_id, test_user=True)
    second = league_player(repo, course_id, test_user=True)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, first) as waiting:
        _until(waiting, "waiting")
        with _enter(repo, connect, url, second) as joining:
            start = _until(joining, "game_start")
            assert _until(waiting, "game_start")["match_id"] == start["match_id"]


# ── FR-023, US2-AS4: one queue or match per student ──────────────────────────


def _start(repo, connect, url, a, b):
    first, second = _enter(repo, connect, url, a), None
    _until(first, "waiting")
    second = _enter(repo, connect, url, b)
    return first, second, _until(first, "game_start"), _until(second, "game_start")


def test_spec007_a_student_away_in_a_match_cannot_queue_elsewhere(repo, live_api, timing):
    """FR-023, US2-AS4: a player's match socket drops and the grace runs. A new socket of theirs
    without the resume token — in that subject or another — is closed with 4412; the opponent
    is told nothing new, and the grace ends in a forfeit as delivery F says. Afterwards the
    student queues normally."""
    from websockets.sync.client import connect

    timing(duration=60, grace=3)
    course_id, other_course = _course(repo), _course(repo)
    a = league_player(repo, course_id, other_course)
    b = league_player(repo, course_id)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    first, second, start, _ = _start(repo, connect, url, a, b)
    with second:
        first.close()
        _until(second, "opponent_away")

        for course in (course_id, other_course):
            with _enter(repo, connect, f"{live_api}/api/ws/pvp/{course}", a) as again:
                assert _first_close(again) == 4412

        seen = []
        while not seen or seen[-1]["type"] != "game_end":
            seen.append(json.loads(second.recv(timeout=10)))
        assert "opponent_back" not in [m["type"] for m in seen]
        assert (seen[-1]["won"], seen[-1]["forfeit"]) == (True, True)

    _until_free(a)
    with _enter(repo, connect, f"{live_api}/api/ws/pvp/{other_course}", a) as fresh:
        assert _until(fresh, "waiting")["type"] == "waiting"


def test_spec007_a_student_who_finished_and_left_cannot_queue_until_the_match_ends(
    repo, live_api, timing
):
    """FR-023 (O-G8, O-F4): a player who answered every item and left has no grace, but the
    match still runs until the opponent finishes; until then a new socket of theirs is 4412.
    When the match ends they may queue again."""
    from websockets.sync.client import connect

    timing(duration=60, grace=1)
    course_id = _course(repo)
    a, b = league_player(repo, course_id), league_player(repo, course_id)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    first, second, start, _ = _start(repo, connect, url, a, b)
    with second:
        with first:
            for item in start["items"]:
                _answer(first, item)

        with _enter(repo, connect, url, a) as again:
            assert _first_close(again) == 4412

        for item in start["items"]:
            _answer(second, item, WRONG)
        end = _until(second, "game_end")
        assert (end["won"], end["forfeit"], end["opp_score"]) == (False, False, 5)

    _until_free(a)
    with _enter(repo, connect, url, a) as fresh:
        assert _until(fresh, "waiting")["type"] == "waiting"


# ── FR-024, US2-AS5: a code per refusal ──────────────────────────────────────


def test_spec007_each_refusal_has_its_own_code(repo, client, monkeypatch):
    """FR-024, US2-AS5 (O-G4): a bad token is 4001 (session), a teacher 4002 (not a student), a
    student not enrolled 4004, and a failed enrolment read 4500 (server error) — four distinct
    codes where there was one."""
    course_id, other_course = _course(repo), _course(repo)
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    stranger = league_player(repo, other_course)
    student = league_player(repo, course_id)

    codes = {
        "session": _refused(client, course_id, "not-a-token"),
        "teacher": _refused(client, course_id, _token(repo, teacher)),
        "not_enrolled": _refused(client, course_id, _token(repo, stranger)),
    }

    def broken(user_id):
        raise RuntimeError("database down")

    monkeypatch.setattr(repo, "get_user_enrollments", broken)
    codes["server_error"] = _refused(client, course_id, _token(repo, student))

    assert codes == {
        "session": 4001,
        "teacher": 4002,
        "not_enrolled": 4004,
        "server_error": 4500,
    }
