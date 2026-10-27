"""
Survey 007 V10 and V12 (`docs/sdd/pvp-survey.md` § 7): the player who waits in the PvP lobby,
and a malformed frame during a match.

While a player waits, a task reads their socket to notice a closed tab. Two things went wrong:
- an answer the client sent right after `game_start`, read by that task before the waiting
  coroutine resumed, was thrown away — no `answer_result` ever came back. Under load this made
  `test_pvp_enrolment.py::test_pvp_matches_and_finishes_a_game_between_enrolled_students`
  intermittent;
- any message sent while waiting ended the wait as if the tab had been closed.

Both engines, through the app's real WebSocket endpoint on uvicorn (see test_pvp_enrolment.py).
"""

import asyncio
import json
import types

from tests.integration.conftest import league_player
from tests.integration.test_pvp_enrolment import (  # noqa: F401 — live_api is a fixture
    _course,
    _token,
    _until,
    live_api,
)


def _slow_wake_up(monkeypatch):
    """A loaded event loop: the waiting coroutine resumes 0.5 s after it is matched, so the
    client's first answer reaches the socket before it does."""
    import api.websocket.pvp as pvp

    real_wait = asyncio.wait

    async def slow_wait(*args, **kwargs):
        result = await real_wait(*args, **kwargs)
        await asyncio.sleep(0.5)
        return result

    names = {n: getattr(asyncio, n) for n in dir(asyncio) if not n.startswith("__")}
    monkeypatch.setattr(pvp, "asyncio", types.SimpleNamespace(**{**names, "wait": slow_wait}))


def _two_students(repo):
    course_id = _course(repo)
    first, second = league_player(repo, course_id), league_player(repo, course_id)  # G1: rated
    return course_id, first, second


def test_the_waiting_players_first_answer_is_never_lost(repo, live_api, monkeypatch):
    """An answer sent right after `game_start` is judged even when the waiting player's
    coroutine resumes late."""
    from websockets.sync.client import connect

    _slow_wake_up(monkeypatch)
    course_id, first, second = _two_students(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": _token(repo, first)}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": _token(repo, second)}))
        item = _until(waiting, "game_start")["items"][0]
        waiting.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": "A"}))

        assert _until(waiting, "answer_result")["item_id"] == item["id"]


def test_a_message_while_waiting_does_not_leave_the_lobby(repo, live_api):
    """Only a closed socket leaves the lobby: a stray message while waiting is ignored, and the
    player is still matched."""
    from websockets.sync.client import connect

    course_id, first, second = _two_students(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": _token(repo, first)}))
        _until(waiting, "waiting")
        waiting.send(json.dumps({"type": "ping"}))
        joining.send(json.dumps({"token": _token(repo, second)}))

        starts = [_until(socket, "game_start") for socket in (waiting, joining)]

    assert starts[0]["match_id"] == starts[1]["match_id"]


def test_a_malformed_message_does_not_end_the_players_match(repo, live_api):
    """Survey 007 V12: a frame that is not JSON is ignored; the player keeps answering."""
    from websockets.sync.client import connect

    course_id, first, second = _two_students(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": _token(repo, first)}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": _token(repo, second)}))
        _until(waiting, "game_start")
        item = _until(joining, "game_start")["items"][0]

        joining.send("{not json")
        joining.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": "A"}))

        assert _until(joining, "answer_result")["item_id"] == item["id"]
