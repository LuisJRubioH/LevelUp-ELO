"""
Spec 007 delivery M (US3; FR-030 … FR-033): matches are even.

- FR-030: two students meet only within a rating window — ±150 at entry, +50 every
  `pvp_window_every_s` waited (20 s; shortened here), at most ±450 — the larger of the two
  waiters' windows; the nearest rating first (O-M1 … O-M3).
- FR-031: a pair's fourth and later matches of the Colombian day are played without rating; both
  are told in `game_start`; the close is `daily_cap` with 0 (O-M4 … O-M7).
- FR-032: the items are near the mean of both ratings, unseen by either player this week, with
  their image and without their difficulty (O-M8, O-M9).
- FR-033: the expectation uses the ratings read when the match is formed.

Both engines, through the app's real WebSocket endpoint on uvicorn (see test_pvp_enrolment.py).
"""

import json
import time
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.elo.model import pvp_deltas
from tests.integration.conftest import (
    enroll,
    is_postgres,
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
from tests.integration.test_spec007_f_match_flow import _none_of

TOPIC = "Fracciones"
RIGHT, WRONG = "A", "B"  # make_course's items all have "A" as the key


@pytest.fixture
def step(monkeypatch):
    """Shorten the window's step period: `step(seconds)` (the server runs in this process)."""
    from api.config import settings

    def set_(seconds):
        monkeypatch.setattr(settings, "pvp_window_every_s", seconds)

    return set_


def _player(repo, course_id, elo):
    student = make_student(repo)
    enroll(repo, student, course_id)
    set_rating(repo, student, course_id, TOPIC, float(elo))
    return student


def _course(repo, items=5):
    course_id, _ = make_course(repo, [TOPIC], items_per_topic=items)
    return course_id


def _enter(repo, connect, url, student):
    socket = connect(url)
    socket.send(json.dumps({"token": _token(repo, student)}))
    return socket


def _first(socket):
    return json.loads(socket.recv(timeout=15))


def _play(socket, items, selected):
    for item in items:
        time.sleep(ANSWER_PACE_S)
        socket.send(json.dumps({"type": "answer", "item_id": item["id"], "selected": selected}))
        _until(socket, "answer_result")


def _players_of(repo, match_id):
    row = sql(repo, "SELECT player1_id, player2_id FROM pvp_matches WHERE id = ?", (match_id,))
    return set(row[0])


def _db_time(repo, moment):
    return moment if is_postgres(repo) else moment.strftime("%Y-%m-%d %H:%M:%S")


def _seed_pair_matches(repo, course_id, a, b, count, finished_at=None):
    """`count` finished, rated matches of the pair (delta 0 so the ratings stay at 1000)."""
    for n in range(count):
        p1, p2 = (a, b) if n % 2 == 0 else (b, a)
        match_id = repo.create_pvp_match(course_id, p1, p2, ["x"])
        repo.finish_pvp_match(
            match_id=match_id, winner_id=p1, score_p1=2, score_p2=1,
            elo_delta_p1=0.0, elo_delta_p2=0.0, p1_id=p1, p2_id=p2,
        )  # fmt: skip
        if finished_at is not None:
            sql(
                repo,
                "UPDATE pvp_matches SET finished_at = ? WHERE id = ?",
                (_db_time(repo, finished_at), match_id),
            )


# ── FR-030, US3-AS1: the window ─────────────────────────────────────────────


def test_spec007_the_close_pair_meets_and_the_far_one_waits(repo, live_api):
    """US3-AS1, FR-030: A 1000 and B 1400 wait; C 1100 joins → C plays A; B is still waiting."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    a, b, c = (_player(repo, course_id, elo) for elo in (1000, 1400, 1100))
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        assert _first(sa)["type"] == "waiting"
        with _enter(repo, connect, url, b) as sb:
            assert _first(sb)["type"] == "waiting"  # 400 from A: no match
            with _enter(repo, connect, url, c) as sc:
                start_c, start_a = _until(sc, "game_start"), _until(sa, "game_start")
                assert start_c["match_id"] == start_a["match_id"]
                assert start_c["opponent"]["elo"] == 1000
                assert _players_of(repo, start_c["match_id"]) == {a, c}
                assert _none_of(sb, "game_start", 1.5)  # B keeps waiting


def test_spec007_a_lone_waiter_meets_a_farther_rival_after_waiting(repo, live_api, step):
    """US3-AS1, FR-030 (O-M2): with a 1 s step, a 1250 newcomer is refused by a 1000 waiter who
    just entered, and admitted on entry once the waiter's window reached ±250 (two steps)."""
    from websockets.sync.client import connect

    step(1.0)
    course_id = _course(repo)
    a = _player(repo, course_id, 1000)
    early, late = _player(repo, course_id, 1250), _player(repo, course_id, 1250)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        entered = time.monotonic()
        assert _first(sa)["type"] == "waiting"
        with _enter(repo, connect, url, early) as se:
            assert _first(se)["type"] == "waiting"  # 250 > ±150: not yet
        time.sleep(max(0.0, entered + 2.4 - time.monotonic()))
        with _enter(repo, connect, url, late) as sl:
            start = _first(sl)
            assert start["type"] == "game_start"  # admitted at once, by A's window
            assert _until(sa, "game_start")["match_id"] == start["match_id"]
            assert _players_of(repo, start["match_id"]) == {a, late}


def test_spec007_two_waiters_meet_when_their_windows_grow(repo, live_api, step):
    """FR-030: no newcomer — two waiters 250 apart meet on a step, once a window covers the gap
    (two 1 s steps), not before."""
    from websockets.sync.client import connect

    step(1.0)
    course_id = _course(repo)
    a, b = _player(repo, course_id, 1000), _player(repo, course_id, 1250)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        entered = time.monotonic()
        assert _first(sa)["type"] == "waiting"
        with _enter(repo, connect, url, b) as sb:
            assert _first(sb)["type"] == "waiting"
            start_a, start_b = _until(sa, "game_start"), _until(sb, "game_start")
            waited = time.monotonic() - entered
            assert start_a["match_id"] == start_b["match_id"]
            assert 1.9 <= waited <= 8.0


# ── FR-031, US3-AS2: the daily cap of a pair ────────────────────────────────


def _colombian_midnight_utc():
    bogota = datetime.now(timezone.utc) - timedelta(hours=5)
    midnight = bogota.replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight + timedelta(hours=5)).replace(tzinfo=timezone.utc)


def test_spec007_a_pairs_fourth_match_of_the_day_is_unrated_and_announced(repo, live_api):
    """US3-AS2, FR-031: three rated matches today → the fourth is played; `game_start` tells
    both it is not rated (`daily_cap`); `game_end` applies 0 with that reason; no rating moves;
    the history says why."""
    from websockets.sync.client import connect

    from src.application.services.rating_read_service import RatingReadService

    course_id = _course(repo)
    a, b = _player(repo, course_id, 1000), _player(repo, course_id, 1000)
    _seed_pair_matches(repo, course_id, a, b, 3)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        _until(sa, "waiting")
        with _enter(repo, connect, url, b) as sb:
            starts = [_until(s, "game_start") for s in (sa, sb)]
            for start in starts:
                assert (start["rated"], start["unrated_reason"]) == (False, "daily_cap")
            _play(sa, starts[0]["items"], RIGHT)
            _play(sb, starts[1]["items"], WRONG)
            ends = [_until(s, "game_end") for s in (sa, sb)]

    assert ends[0]["won"] is True
    for end in ends:
        assert (end["elo_delta"], end["elo_delta_display"], end["elo_reason"]) == (
            0.0, 0, "daily_cap",
        )  # fmt: skip
    assert rating_of(repo, a, course_id, TOPIC) == 1000.0
    assert rating_of(repo, b, course_id, TOPIC) == 1000.0
    row = RatingReadService(repo).pvp_history(a)["matches"][0]
    assert (row["match_id"], row["status"], row["reason"], row["elo_delta_display"]) == (
        starts[0]["match_id"], "finished", "daily_cap", 0,
    )  # fmt: skip


def test_spec007_yesterdays_matches_do_not_count(repo, live_api):
    """FR-031 (O-M4): three matches finished before today's 00:00 in Bogotá (05:00 UTC) do not
    count: the match is rated and the win moves the ratings."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    a, b = _player(repo, course_id, 1000), _player(repo, course_id, 1000)
    _seed_pair_matches(
        repo, course_id, a, b, 3, finished_at=_colombian_midnight_utc() - timedelta(minutes=1)
    )
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        _until(sa, "waiting")
        with _enter(repo, connect, url, b) as sb:
            starts = [_until(s, "game_start") for s in (sa, sb)]
            for start in starts:
                assert (start["rated"], start["unrated_reason"]) == (True, None)
            _play(sa, starts[0]["items"], RIGHT)
            _play(sb, starts[1]["items"], WRONG)
            end = _until(sa, "game_end")

    assert (end["elo_delta"], end["elo_reason"]) == (12.0, None)
    assert rating_of(repo, a, course_id, TOPIC) == pytest.approx(1012.0)
    assert rating_of(repo, b, course_id, TOPIC) == pytest.approx(988.0)


# ── FR-032, US3-AS3: the items ──────────────────────────────────────────────


def test_spec007_match_items_are_near_the_mean_unseen_with_images_and_no_difficulty(repo, live_api):
    """US3-AS3, FR-032: players at 1000 and 1100 (mean 1050). The course holds 12 items within
    ±200 — two practised by A this week — and 6 far away; one near item has an image. The match
    gets exactly the 10 near unseen items, the same for both, the image's path included, and no
    item carries its difficulty (nor its key)."""
    from websockets.sync.client import connect

    course_id, _ = make_course(repo, [TOPIC], items_per_topic=0)
    near, far = [], []
    bank = [1000, 1050, 1100, 1150, 1200, 1250] * 2 + [600, 700, 1500, 1600, 1700, 1800]
    for n, difficulty in enumerate(bank):
        item_id = f"m_{course_id}_{n}"
        sql(
            repo,
            "INSERT INTO items (id, topic, content, options, correct_option, difficulty,"
            " rating_deviation, course_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (item_id, TOPIC, f"x{n}", json.dumps(["A", "B"]), "A", float(difficulty), 350.0,
             course_id),
        )  # fmt: skip
        (near if abs(difficulty - 1050) <= 200 else far).append(item_id)
    assert (len(near), len(far)) == (12, 6)
    a, b = _player(repo, course_id, 1000), _player(repo, course_id, 1100)
    practised = near[:2]
    for item_id in practised:
        sql(
            repo,
            "INSERT INTO attempts (user_id, item_id, is_correct) VALUES (?, ?, ?)",
            (a, item_id, True if is_postgres(repo) else 1),
        )
    pictured = near[5]
    sql(repo, "UPDATE items SET image_url = ? WHERE id = ?", ("items/images/m.png", pictured))
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        _until(sa, "waiting")
        with _enter(repo, connect, url, b) as sb:
            start_a, start_b = _until(sa, "game_start"), _until(sb, "game_start")

    items = start_a["items"]
    assert items == start_b["items"]
    assert {i["id"] for i in items} == set(near[2:])
    assert not {i["id"] for i in items} & set(practised)
    assert all("difficulty" not in i and "correct_option" not in i for i in items)
    by_id = {i["id"]: i for i in items}
    assert by_id[pictured]["image_url"] == "items/images/m.png"
    assert all(set(i) == {"id", "content", "options", "topic", "image_url"} for i in items)


# ── FR-033: the expectation read when the match is formed ───────────────────


def test_spec007_the_expectation_is_read_when_the_match_is_formed(repo, live_api):
    """FR-033: A enters the lobby at 1000; while A waits, A's rating becomes 1100. B (1000) joins
    and wins: the applied deltas are `pvp_deltas` on 1100, not on the 1000 read at entry, and B
    sees A at 1100."""
    from websockets.sync.client import connect

    course_id = _course(repo)
    a, b = _player(repo, course_id, 1000), _player(repo, course_id, 1000)
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with _enter(repo, connect, url, a) as sa:
        _until(sa, "waiting")
        sql(
            repo,
            "UPDATE student_course_topic_elo SET current_elo = ? WHERE user_id = ?",
            (1100.0, a),
        )
        with _enter(repo, connect, url, b) as sb:
            start_a, start_b = _until(sa, "game_start"), _until(sb, "game_start")
            assert start_b["opponent"]["elo"] == 1100
            _play(sb, start_b["items"], RIGHT)
            _play(sa, start_a["items"], WRONG)
            end_b = _until(sb, "game_end")

    d_a, d_b = pvp_deltas(1100.0, 1000.0, 0.0)  # A is p1 (waited), B p2; B won
    assert end_b["elo_delta"] == pytest.approx(d_b)
    assert d_b != pytest.approx(12.0)
    assert rating_of(repo, b, course_id, TOPIC) == pytest.approx(1000.0 + d_b)
    assert rating_of(repo, a, course_id, TOPIC) == pytest.approx(1100.0 + d_a)
