"""
Spec 007 delivery F (US4; FR-040, FR-041, FR-042): the match is decided on the server.

- FR-040: `game_start` carries the server's end time (`ends_at`, `server_now`) and the server
  alone ends the match at it.
- FR-041: on equal correct answers the lower total answer time wins (whole seconds; O3, O-F7).
- FR-042: a player whose socket drops keeps their place for the grace; a reconnect carrying their
  `resume` token resumes the same match (O-F1), otherwise the match ends at once as their loss by
  abandonment (O-F2, O-F3). A player who finished every item does not forfeit (O-F4); both away
  abandons the match with no rating change (O-F5); the grace never extends the match (O-F6).

Both engines, through the app's real WebSocket endpoint on uvicorn (see test_pvp_enrolment.py).
`MATCH_DURATION` and the grace are shortened with `monkeypatch`: the server runs in this process.
"""

import json
import time
from datetime import datetime, timezone

import pytest

from tests.integration.conftest import (
    enroll,
    give_institution,
    make_course,
    make_student,
    rating_of,
    set_rating,
    sql,
)
from tests.integration.test_pvp_enrolment import (  # noqa: F401 — live_api is a fixture
    ANSWER_PACE_S,
    _token,
    _until,
    live_api,
)
from tests.integration.test_pvp_limits import _close_code

TOPIC = "Fracciones"
RIGHT, WRONG = "A", "B"  # make_course's items all have "A" as the key


@pytest.fixture
def timing(monkeypatch):
    """Shorten the match and the grace: `timing(duration=…, grace=…)`."""
    from api.config import settings
    from api.websocket import pvp

    def set_(duration=60, grace=20):
        monkeypatch.setattr(pvp, "MATCH_DURATION", duration)
        monkeypatch.setattr(settings, "pvp_reconnect_grace_s", grace)

    return set_


def _players(repo):
    """A course with five items and two enrolled students rated 1000 in it, of one institution
    (spec 007 FR-022)."""
    course_id, _ = make_course(repo, [TOPIC], items_per_topic=5)
    a, b = make_student(repo), make_student(repo)
    for student in (a, b):
        enroll(repo, student, course_id)
        set_rating(repo, student, course_id, TOPIC, 1000.0)
        give_institution(repo, student)
    return course_id, a, b


def _start(repo, url, connect, a, b):
    """`a` waits, `b` joins: (a's socket, b's socket, a's game_start, b's game_start)."""
    first, second = connect(url), connect(url)
    first.send(json.dumps({"token": _token(repo, a)}))
    _until(first, "waiting")
    second.send(json.dumps({"token": _token(repo, b)}))
    return first, second, _until(first, "game_start"), _until(second, "game_start")


def _answer(socket, item, selected=RIGHT):
    time.sleep(ANSWER_PACE_S)
    socket.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": selected}))
    return _until(socket, "answer_result")


def _resume(repo, url, connect, student, resume):
    socket = connect(url)
    socket.send(json.dumps({"token": _token(repo, student), "resume": resume}))
    return socket


def _when(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _now():
    return datetime.now(timezone.utc)


def _row(repo, match_id):
    return sql(
        repo,
        "SELECT status, winner_id, elo_reason_p1, elo_reason_p2 FROM pvp_matches WHERE id = ?",
        (match_id,),
    )[0]


def _row_becomes(repo, match_id, status, within=10.0):
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        row = _row(repo, match_id)
        if row[0] == status:
            return row
        time.sleep(0.1)
    raise AssertionError(f"match {match_id} still {_row(repo, match_id)[0]}, not {status}")


def _none_of(socket, kind, seconds):
    """True when no message of `kind` arrives within `seconds`."""
    deadline = time.monotonic() + seconds
    while (left := deadline - time.monotonic()) > 0:
        try:
            message = json.loads(socket.recv(timeout=left))
        except TimeoutError:
            return True
        if message["type"] == kind:
            return False
    return True


# ── FR-040: the server's end time ───────────────────────────────────────────


def test_spec007_game_start_carries_the_servers_end_time(repo, live_api):
    """FR-040: both players get the same `ends_at`, MATCH_DURATION after the server's now."""
    from websockets.sync.client import connect

    course_id, a, b = _players(repo)
    first, second, start_a, start_b = _start(
        repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b
    )
    with first, second:
        assert start_a["ends_at"] == start_b["ends_at"]
        left = (_when(start_a["ends_at"]) - _when(start_a["server_now"])).total_seconds()
        assert 178 <= left <= 180
        assert start_a["duration_seconds"] == 180


def test_spec007_the_server_closes_at_its_end_time_whatever_the_client_does(repo, live_api, timing):
    """FR-040, US4-AS1: with a 2 s match and clients that send nothing, both get `game_end` at
    the server's `ends_at`."""
    from websockets.sync.client import connect

    timing(duration=2)
    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    with first, second:
        ends_at = _when(start["ends_at"])
        for socket in (first, second):
            _until(socket, "game_end")
            assert abs((_now() - ends_at).total_seconds()) < 1.0


# ── FR-041: the speed tiebreak ──────────────────────────────────────────────


def test_spec007_a_tied_match_is_won_by_speed(repo, live_api):
    """FR-041, US4-AS2: both answer every item right; the second answers each 2 s later and
    loses by speed — a full win, stored and applied."""
    from websockets.sync.client import connect

    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    with first, second:
        for item in start["items"]:
            _answer(first, item)
        time.sleep(2.0)
        for item in start["items"]:
            _answer(second, item)
        fast, slow = _until(first, "game_end"), _until(second, "game_end")

    assert (fast["your_score"], fast["opp_score"]) == (5, 5)
    assert (fast["won"], fast["draw"], fast["tiebreak"]) == (True, False, True)
    assert (slow["won"], slow["draw"], slow["tiebreak"]) == (False, False, True)
    assert _row(repo, start["match_id"])[:2] == ("finished", a)
    assert rating_of(repo, a, course_id, TOPIC) == pytest.approx(1012.0)
    assert rating_of(repo, b, course_id, TOPIC) == pytest.approx(988.0)


# ── FR-042: the grace, the resume and the forfeit ───────────────────────────


def test_spec007_a_player_who_returns_within_the_grace_resumes_the_match(repo, live_api, timing):
    """FR-042, US4-AS3: a player drops and comes back with their resume token: the same match
    goes on — its answered items and scores — and the opponent is told both ways."""
    from websockets.sync.client import connect

    timing(duration=60, grace=5)
    course_id, a, b = _players(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    first, second, start, _ = _start(repo, url, connect, a, b)
    items = start["items"]
    with second:
        with first:
            _answer(first, items[0])
        assert _until(second, "opponent_away")["grace_seconds"] == 5

        with _resume(repo, url, connect, a, start["resume"]) as again:
            resumed = _until(again, "game_resume")
            assert resumed["match_id"] == start["match_id"]
            assert resumed["answered"] == [items[0]["id"]]
            assert (resumed["your_score"], resumed["opp_score"]) == (1, 0)
            assert resumed["ends_at"] == start["ends_at"]
            assert _until(second, "opponent_back")["type"] == "opponent_back"

            assert _answer(again, items[1])["your_score"] == 2
            for item in items[2:]:
                _answer(again, item)
            for item in items:
                _answer(second, item, WRONG)
            ends = [_until(socket, "game_end") for socket in (again, second)]

    assert [(e["your_score"], e["won"], e["forfeit"]) for e in ends] == [
        (5, True, False),
        (0, False, False),
    ]
    assert _row(repo, start["match_id"]) == ("finished", a, None, None)


def test_spec007_a_player_who_does_not_return_loses_by_abandonment(repo, live_api, timing):
    """FR-042, US4-AS3 (O-F2, O-F3): the player who left loses even when ahead; the opponent is
    told at once after the grace, long before the end time; the delta is applied once."""
    from websockets.sync.client import connect

    timing(duration=60, grace=1)
    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    with second:
        with first:
            _answer(first, start["items"][0])
            _answer(first, start["items"][1])
        _until(second, "opponent_away")
        end = _until(second, "game_end")
        assert (_when(start["ends_at"]) - _now()).total_seconds() > 30

        assert (end["won"], end["draw"], end["forfeit"]) == (True, False, True)
        assert (end["your_score"], end["opp_score"]) == (0, 2)
        time.sleep(0.5)

    assert _row(repo, start["match_id"]) == ("finished", b, "forfeit", "forfeit")
    assert rating_of(repo, b, course_id, TOPIC) == pytest.approx(1012.0)
    assert rating_of(repo, a, course_id, TOPIC) == pytest.approx(988.0)


def test_spec007_a_reconnect_after_the_grace_finds_the_match_over(repo, live_api, timing):
    """FR-042, spec § Edge Cases: a resume for a match already lost is closed with 4410; the
    student may then queue again."""
    from websockets.sync.client import connect

    timing(duration=60, grace=1)
    course_id, a, b = _players(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    first, second, start, _ = _start(repo, url, connect, a, b)
    with second:
        first.close()
        assert _until(second, "game_end")["forfeit"] is True

    with _resume(repo, url, connect, a, start["resume"]) as late:
        assert _close_code(late) == 4410
    with connect(url) as fresh:
        fresh.send(json.dumps({"token": _token(repo, a)}))
        assert _until(fresh, "waiting")["type"] == "waiting"


def test_spec007_a_reconnect_takes_over_a_half_open_socket(repo, live_api):
    """FR-042 with FR-050 (O-F1): the old socket is still open on the server. A socket with the
    resume token is admitted at once and the old one is closed with 4411; one without the token
    is still refused with 4409."""
    from websockets.sync.client import connect

    course_id, a, b = _players(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    first, second, start, _ = _start(repo, url, connect, a, b)
    with first, second:
        _answer(first, start["items"][0])

        with _resume(repo, url, connect, a, start["resume"]) as again:
            resumed = _until(again, "game_resume")
            assert (resumed["match_id"], resumed["your_score"]) == (start["match_id"], 1)
            assert _close_code(first) == 4411

            with connect(url) as third:
                third.send(json.dumps({"token": _token(repo, a)}))
                assert _close_code(third) == 4409

            assert _answer(again, start["items"][1])["your_score"] == 2


def test_spec007_a_waiting_player_reconnects_without_waiting_for_the_ping(repo, live_api):
    """O-F1 (b): the resume token comes with `waiting`; the same tab's reconnect replaces its
    half-open lobby socket at once, and the lobby still holds one slot for the student."""
    from websockets.sync.client import connect

    course_id, a, b = _players(repo)
    url = f"{live_api}/api/ws/pvp/{course_id}"
    with connect(url) as stale:
        stale.send(json.dumps({"token": _token(repo, a)}))
        resume = _until(stale, "waiting")["resume"]

        with _resume(repo, url, connect, a, resume) as again:
            assert _until(again, "waiting")["type"] == "waiting"
            assert _close_code(stale) == 4411

            with connect(url) as rival:
                rival.send(json.dumps({"token": _token(repo, b)}))
                start = _until(rival, "game_start")
                assert _until(again, "game_start")["match_id"] == start["match_id"]
                assert _answer(again, start["items"][0])["your_score"] == 1


def test_spec007_a_player_who_finished_and_leaves_does_not_forfeit(repo, live_api, timing):
    """O-F4: a player who answered every item and then leaves does not forfeit: the match ends
    when the opponent finishes, by score and time."""
    from websockets.sync.client import connect

    timing(duration=60, grace=1)
    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    with second:
        with first:
            for item in start["items"]:
                _answer(first, item)
        assert _none_of(second, "game_end", 2.5)

        _answer(second, start["items"][0])
        for item in start["items"][1:]:
            _answer(second, item, WRONG)
        end = _until(second, "game_end")

    assert (end["won"], end["forfeit"], end["your_score"], end["opp_score"]) == (False, False, 1, 5)
    assert _row(repo, start["match_id"]) == ("finished", a, None, None)


def test_spec007_both_players_away_abandons_without_rating(repo, live_api, timing):
    """O-F5: both players leave and neither comes back: the match is abandoned `both_left`
    and no rating moves."""
    from websockets.sync.client import connect

    timing(duration=60, grace=1)
    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    with first, second:
        _answer(first, start["items"][0])
    row = _row_becomes(repo, start["match_id"], "abandoned")

    assert row == ("abandoned", None, "both_left", "both_left")
    assert rating_of(repo, a, course_id, TOPIC) == 1000.0
    assert rating_of(repo, b, course_id, TOPIC) == 1000.0


def test_spec007_the_grace_does_not_extend_the_match(repo, live_api, timing):
    """O-F6: a player who drops a second before the end is not waited for: the match closes at
    the server's end time, by score."""
    from websockets.sync.client import connect

    timing(duration=3, grace=5)
    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    ends_at = _when(start["ends_at"])
    with second:
        with first:
            _answer(first, start["items"][0])
            time.sleep(max(0.0, (ends_at - _now()).total_seconds() - 1.0))
        end = _until(second, "game_end")
        assert abs((_now() - ends_at).total_seconds()) < 1.0

    assert (end["won"], end["forfeit"], end["opp_score"]) == (False, False, 1)
    assert _row(repo, start["match_id"])[:2] == ("finished", a)


# ── With spec 004 E3: an account that expires mid-match (plan-f T003) ──────────────────────


def test_spec007_an_expired_account_mid_match_abandons_without_forfeit(
    repo, live_api, timing, monkeypatch
):
    """plan-f § An expired account mid-match (spec 004 FR-051, FR-052): E3's expiry sweep closes
    the match as abandoned / `account_expired` with no rating change and closes the socket with
    4403. It is not a forfeit — even for the player who was ahead — and no grace starts after it."""
    import asyncio

    from websockets.sync.client import connect

    from api.websocket import connections, expiry
    from tests.integration.test_spec004_e3_accounts import _expire

    loops = []
    register = connections.register

    def _register(user_id, websocket):  # runs on the server's loop: remember it for the sweep
        loops.append(asyncio.get_running_loop())
        register(user_id, websocket)

    monkeypatch.setattr(connections, "register", _register)
    timing(duration=60, grace=1)
    course_id, a, b = _players(repo)
    first, second, start, _ = _start(repo, f"{live_api}/api/ws/pvp/{course_id}", connect, a, b)
    with first, second:
        _answer(first, start["items"][0])
        _answer(first, start["items"][1])  # a is ahead 2–0: a forfeit would be b's win
        _expire(repo, a)
        swept = asyncio.run_coroutine_threadsafe(
            expiry.sweep_expired_accounts(repo), loops[-1]
        ).result(timeout=15)

        assert swept == [a]
        assert _close_code(first) == expiry.EXPIRED_CODE
        end = _until(second, "game_end")
        assert end["abandoned"] is True and end["reason"] == "account_expired"
        assert end["elo_delta"] == 0 and not end.get("forfeit")
        # No grace follows: b is never told the rival is away, and no second result arrives.
        assert _none_of(second, "opponent_away", 2.0)

    status, winner, reason_p1, reason_p2 = _row(repo, start["match_id"])
    assert (status, winner) == ("abandoned", None)
    assert reason_p1 == reason_p2 == "account_expired"
    assert rating_of(repo, a, course_id, TOPIC) == pytest.approx(1000.0)
    assert rating_of(repo, b, course_id, TOPIC) == pytest.approx(1000.0)
