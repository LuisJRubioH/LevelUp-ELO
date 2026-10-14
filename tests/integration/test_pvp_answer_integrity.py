"""
A PvP score counts only the match's own items, answered once while the match is live, and a match
needs items to start. Both engines, on the app's real WebSocket endpoint served by uvicorn (a
match needs both players on one event loop; see test_pvp_enrolment.py).
"""

import json

import pytest
from websockets.exceptions import ConnectionClosed

from api.websocket import pvp
from tests.integration.conftest import enroll, make_course, make_student, sql
from tests.integration.test_pvp_enrolment import _course, _token, _until, live_api  # noqa: F401


def _matched(repo, live_api, course_id):  # noqa: F811
    """Two students enrolled in the course: the endpoint's URL and their two tokens."""
    first, second = make_student(repo), make_student(repo)
    enroll(repo, first, course_id)
    enroll(repo, second, course_id)
    return f"{live_api}/api/ws/pvp/{course_id}", _token(repo, first), _token(repo, second)


def _answers_of(repo, match_id):
    return sql(repo, "SELECT COUNT(*) FROM pvp_answers WHERE match_id = ?", (match_id,))[0][0]


def test_an_answer_outside_the_match_scores_nothing(repo, live_api):  # noqa: F811
    """An item that is not one of the match's, an item id that is not text and a choice that is
    not text are ignored: no point, no answer_result, nothing stored. The match then ends on the
    real answers alone."""
    from websockets.sync.client import connect

    url, first, second = _matched(repo, live_api, _course(repo))
    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": first}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": second}))
        start = _until(waiting, "game_start")
        _until(joining, "game_start")
        items = start["items"]

        for stray in (
            {"item_id": "not-an-item-of-this-match", "selected": None},
            {"item_id": ["a", "list"], "selected": None},
            {"item_id": items[0]["id"], "selected": None},
        ):
            waiting.send(json.dumps({"type": "answer", **stray}))
        for socket in (waiting, joining):
            for item in items:
                socket.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": "B"}))
                result = _until(socket, "answer_result")
                assert (result["item_id"], result["is_correct"]) == (item["id"], False)
        ends = [_until(socket, "game_end") for socket in (waiting, joining)]

    assert [(e["your_score"], e["opp_score"]) for e in ends] == [(0, 0), (0, 0)]
    assert _answers_of(repo, start["match_id"]) == 2 * len(items)


def test_an_answer_after_the_match_ended_is_ignored(repo, live_api, monkeypatch):  # noqa: F811
    """Once the timer has closed the match, a correct answer neither scores nor is stored."""
    from websockets.sync.client import connect

    monkeypatch.setattr(pvp, "MATCH_DURATION", 1)
    url, first, second = _matched(repo, live_api, _course(repo))
    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": first}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": second}))
        start = _until(waiting, "game_start")
        assert [_until(s, "game_end")["your_score"] for s in (waiting, joining)] == [0, 0]

        waiting.send(
            json.dumps({"type": "answer", "item_id": start["items"][0]["id"], "selected": "A"})
        )
        with pytest.raises(TimeoutError):
            waiting.recv(timeout=1.5)

    assert _answers_of(repo, start["match_id"]) == 0


def test_a_course_without_items_starts_no_match(repo, live_api):  # noqa: F811
    """With nothing to play, both players are told (close 4404) and no match is recorded: a 0-0
    draw would still move ratings whenever the expectations differ."""
    from websockets.sync.client import connect

    course_id, _ = make_course(repo, ["Fracciones"], items_per_topic=0)
    url, first, second = _matched(repo, live_api, course_id)
    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": first}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": second}))
        for socket in (waiting, joining):
            with pytest.raises(ConnectionClosed) as closed:
                _until(socket, "game_start")
            assert closed.value.rcvd.code == 4404

    matches = sql(repo, "SELECT COUNT(*) FROM pvp_matches WHERE course_id = ?", (course_id,))
    assert matches[0][0] == 0
