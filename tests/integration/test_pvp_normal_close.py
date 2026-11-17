"""QA Q15 / spec 007 FR-002: a terminal game_end is followed by a normal socket close.

Use real uvicorn and WebSocket clients: an ASGI handler returning without a close frame is
observable as 1006 here, whereas a fake socket or TestClient can hide the transport failure.
"""

import json

import pytest

from tests.integration.conftest import enroll, give_institution, make_student
from tests.integration.test_pvp_enrolment import (
    _answer_all,
    _course,
    _token,
    _until,
    live_api,  # noqa: F401 -- shared real-server fixture
)


@pytest.mark.parametrize("last", [0, 1], ids=["waiting-last", "joining-last"])
def test_spec007_finished_match_closes_both_sockets_normally(repo, client, live_api, last):
    """FR-002, US1-AS1: either player may finish last; both get their result before code 1000.

    Prepare ratings through the diagnostic endpoint, then verify the stored result agrees with
    each player's terminal frame. Closing a completed game must not create a forfeit.
    """
    from websockets.exceptions import ConnectionClosedOK
    from websockets.sync.client import connect

    course_id = _course(repo)
    students = [make_student(repo), make_student(repo)]
    items = repo.get_items_from_db(course_id=course_id)
    for student in students:
        enroll(repo, student, course_id)
        give_institution(repo, student)
        diagnostic = client.post(
            f"/api/student/diagnostic/{course_id}/submit",
            headers={"Authorization": f"Bearer {_token(repo, student)}"},
            json={"answers": [{"item_id": items[0]["id"], "selected_option": "A"}]},
        )
        assert diagnostic.status_code == 200

    url = f"{live_api}/api/ws/pvp/{course_id}"
    with connect(url) as first, connect(url) as second:
        sockets = [first, second]
        first.send(json.dumps({"token": _token(repo, students[0])}))
        _until(first, "waiting")
        second.send(json.dumps({"token": _token(repo, students[1])}))
        starts = [_until(socket, "game_start") for socket in sockets]
        assert starts[0]["match_id"] == starts[1]["match_id"]
        for index in (1 - last, last):
            _answer_all(sockets[index], starts[index]["items"])
        ends = [_until(socket, "game_end") for socket in sockets]

        # Read the last responder first: Q15 returned an abnormal close immediately there;
        # the other player's coroutine could otherwise remain waiting for another answer.
        for index in (last, 1 - last):
            with pytest.raises(ConnectionClosedOK) as closed:
                sockets[index].recv(timeout=3)
            assert closed.value.rcvd.code == 1000

    for student, end in zip(students, ends):
        assert (end["your_score"], end["opp_score"]) == (5, 5)
        assert not end["forfeit"]
        history = repo.get_pvp_history(student)
        assert len(history) == 1
        assert history[0]["status"] == "finished"
        assert history[0]["my_score"] == end["your_score"]
        assert history[0]["opp_score"] == end["opp_score"]
        assert history[0]["elo_delta"] == end["elo_delta"]
