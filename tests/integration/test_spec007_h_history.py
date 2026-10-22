"""
Spec 007 delivery H (US6; FR-060, FR-061): every match leaves a trace.

- The history lists finished and abandoned matches — orphaned, not saved — each with its subject
  and the student's own reason, newest first, five at a time; «Ver más» asks for the five after
  the last one shown (`before`). An active match is not in it.
- A close that fails to persist is retried (the first try and 3 retries); if every try fails the
  match is closed as abandoned with reason `not_saved`, and no rating moves.

Both engines.
"""

import asyncio
import types

import pytest

from tests.integration.conftest import make_course, make_student, rating_of, set_rating, sql

TOPIC = "Fracciones"


def _players(repo):
    course_id, _ = make_course(repo, [TOPIC], name="Aritmética H")
    a, b = make_student(repo), make_student(repo)
    set_rating(repo, a, course_id, TOPIC, 1000.0)
    set_rating(repo, b, course_id, TOPIC, 1000.0)
    return course_id, a, b


def _finish(repo, match_id, a, b):
    repo.finish_pvp_match(
        match_id=match_id, winner_id=a, score_p1=3, score_p2=1,
        elo_delta_p1=8.0, elo_delta_p2=-8.0, p1_id=a, p2_id=b,
    )  # fmt: skip


def _orphan(repo, match_id):
    """Make `match_id` look abandoned by a dead process, then sweep."""
    sql(
        repo,
        "UPDATE pvp_matches SET started_at = ? WHERE id = ?",
        ("2000-01-01 00:00:00", match_id),
    )
    repo.expire_stale_pvp_matches()


def test_spec007_history_lists_finished_abandoned_and_not_saved(repo):
    """FR-060, US6-AS1: a finished, an orphaned and an unsaved match appear with their subject
    and reason; an active one does not."""
    from src.application.services.rating_read_service import RatingReadService

    course_id, a, b = _players(repo)
    finished = repo.create_pvp_match(course_id, a, b, ["i1"])
    _finish(repo, finished, a, b)
    orphan = repo.create_pvp_match(course_id, a, b, ["i1"])
    _orphan(repo, orphan)
    unsaved = repo.create_pvp_match(course_id, a, b, ["i1"])
    assert repo.abandon_pvp_match(unsaved, "not_saved") is True
    repo.create_pvp_match(course_id, a, b, ["i1"])  # still active

    page = RatingReadService(repo).pvp_history(a)

    rows = {row["match_id"]: row for row in page["matches"]}
    assert set(rows) == {finished, orphan, unsaved}
    assert {r["course_name"] for r in rows.values()} == {"Aritmética H"}
    assert rows[finished]["status"] == "finished"
    assert (rows[orphan]["status"], rows[orphan]["reason"]) == ("abandoned", "orphaned")
    assert (rows[unsaved]["status"], rows[unsaved]["reason"]) == ("abandoned", "not_saved")
    assert page["has_more"] is False


def test_spec007_history_pages_of_five_reach_every_match(repo):
    """FR-060: seven matches — the newest five with `has_more`, then the two after the fifth."""
    from src.application.services.rating_read_service import RatingReadService

    course_id, a, b = _players(repo)
    ids = []
    for _ in range(7):
        ids.append(repo.create_pvp_match(course_id, a, b, ["i1"]))
        _finish(repo, ids[-1], a, b)
    service = RatingReadService(repo)

    first = service.pvp_history(a)
    second = service.pvp_history(a, before=first["matches"][-1]["match_id"])

    assert [r["match_id"] for r in first["matches"]] == ids[::-1][:5]
    assert first["has_more"] is True
    assert [r["match_id"] for r in second["matches"]] == ids[::-1][5:]
    assert second["has_more"] is False


def test_spec007_the_sweep_records_why(repo):
    """FR-060: an orphan closed by the sweep says `orphaned` for both players, with 0."""
    course_id, a, b = _players(repo)
    match_id = repo.create_pvp_match(course_id, a, b, ["i1"])

    _orphan(repo, match_id)

    row = sql(
        repo,
        "SELECT status, elo_delta_p1, elo_reason_p1, elo_delta_p2, elo_reason_p2"
        " FROM pvp_matches WHERE id = ?",
        (match_id,),
    )[0]
    assert (row[0], float(row[1]), row[2], float(row[3]), row[4]) == (
        "abandoned", 0.0, "orphaned", 0.0, "orphaned",
    )  # fmt: skip


def test_spec007_abandon_is_idempotent_and_skips_a_finished_match(repo):
    """FR-061: abandoning closes an active match once; a finished match is left as it is."""
    course_id, a, b = _players(repo)
    active = repo.create_pvp_match(course_id, a, b, ["i1"])
    finished = repo.create_pvp_match(course_id, a, b, ["i1"])
    _finish(repo, finished, a, b)

    assert repo.abandon_pvp_match(active, "not_saved") is True
    assert repo.abandon_pvp_match(active, "not_saved") is False
    assert repo.abandon_pvp_match(finished, "not_saved") is False
    status = sql(repo, "SELECT status FROM pvp_matches WHERE id = ?", (finished,))[0][0]
    assert status == "finished"


class _Socket:
    def __init__(self):
        self.sent = []

    async def send_json(self, message):
        self.sent.append(message)


def _active_match(repo, course_id, a, b):
    import api.websocket.pvp as pvp

    match_id = repo.create_pvp_match(course_id, a, b, ["i1"])
    p1 = pvp.LobbySlot(user_id=a, name="a", elo=1000.0, ws=_Socket())
    p2 = pvp.LobbySlot(user_id=b, name="b", elo=1000.0, ws=_Socket())
    return pvp.ActiveMatch(
        match_id=match_id, course_id=course_id, p1=p1, p2=p2,
        items=[], correct={}, score={a: 2, b: 1},
    )  # fmt: skip


def _failing(repo, failures):
    """`repo` whose finish_pvp_match raises `failures` times, then works; counts the tries."""
    tries = []

    def finish(**kwargs):
        tries.append(1)
        if len(tries) <= failures:
            raise RuntimeError("database unavailable")
        return repo.finish_pvp_match(**kwargs)

    proxy = types.SimpleNamespace(finish_pvp_match=finish, abandon_pvp_match=repo.abandon_pvp_match)
    return proxy, tries


@pytest.fixture
def no_wait(monkeypatch):
    import api.websocket.pvp as pvp

    monkeypatch.setattr(pvp, "CLOSE_RETRY_DELAYS", (0.0, 0.0, 0.0))


def test_spec007_a_failing_close_is_retried_then_recorded_not_saved(repo, no_wait):
    """FR-061, US6-AS2: four tries fail → abandoned `not_saved`, no rating moves, both players
    see it in their history; `game_end` says `not_applied` (spec 001 FR-029c)."""
    import api.websocket.pvp as pvp
    from src.application.services.rating_read_service import RatingReadService

    course_id, a, b = _players(repo)
    match = _active_match(repo, course_id, a, b)
    proxy, tries = _failing(repo, failures=99)

    asyncio.run(pvp._close_match(match, proxy))

    assert len(tries) == 4
    assert rating_of(repo, a, course_id, TOPIC) == 1000.0
    assert rating_of(repo, b, course_id, TOPIC) == 1000.0
    for player in (a, b):
        row = RatingReadService(repo).pvp_history(player)["matches"][0]
        assert (row["match_id"], row["status"], row["reason"]) == (
            match.match_id, "abandoned", "not_saved",
        )  # fmt: skip
    end = match.p1.ws.sent[-1]
    assert (end["type"], end["elo_delta"], end["elo_reason"]) == ("game_end", 0.0, "not_applied")


def test_spec007_a_close_that_succeeds_on_retry_finishes_normally(repo, no_wait):
    """FR-061: one failure, then the close persists — finished, with the applied deltas."""
    import api.websocket.pvp as pvp

    course_id, a, b = _players(repo)
    match = _active_match(repo, course_id, a, b)
    proxy, tries = _failing(repo, failures=1)

    asyncio.run(pvp._close_match(match, proxy))

    assert len(tries) == 2
    status = sql(repo, "SELECT status FROM pvp_matches WHERE id = ?", (match.match_id,))[0][0]
    assert status == "finished"
    assert rating_of(repo, a, course_id, TOPIC) > 1000.0
    assert match.p1.ws.sent[-1]["elo_reason"] is None
