"""
Spec 007 delivery M (US3; FR-030, FR-031): who meets whom, and which matches of a pair count.

Pure rules of `src/domain/pvp/matchmaking.py`, with the owner's numbers (plan-m, O-M1 … O-M5):
a window of ±150 at entry, +50 every 20 s, at most ±450; two waiters meet within the larger of
their two windows; the nearest rating wins, ties by the longest wait; a pair's day is the calendar
day in Colombia (fixed UTC−5); after 3 rated matches of the pair that day the next is unrated.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.domain.pvp.matchmaking import (
    WindowRule,
    eligible,
    pair_day_start,
    pair_match_is_rated,
    pick_opponent,
    window,
)

RULE = WindowRule(start=150, step=50, every_s=20, ceiling=450)


@dataclass(eq=False)
class Waiter:
    rating: float
    joined_at: float


# ── FR-030: the window ──────────────────────────────────────────────────────


def test_spec007_window_starts_at_150_and_widens_each_step():
    """FR-030 (O-M1): ±150 at entry, +50 at each full 20 s waited."""
    widths = [window(s, 150, 50, 20, 450) for s in (0, 19.9, 20, 39.9, 40, 60)]
    assert widths == [150, 150, 200, 200, 250, 300]
    assert RULE.width(45) == 250


def test_spec007_window_stops_at_its_ceiling():
    """FR-030 (O-M1): ±450 is reached at 120 s and never passed."""
    assert window(120, 150, 50, 20, 450) == 450
    assert window(119.9, 150, 50, 20, 450) == 400
    assert window(300, 150, 50, 20, 450) == 450
    assert RULE.width(10_000) == 450


def test_spec007_the_close_pair_is_picked():
    """US3-AS1 (O-M2, O-M3): A 1000 and B 1400 wait; C 1100 arrives → C meets A, not B. Among
    two eligible at the same gap, the one who waited longer."""
    now = 100.0
    a, b = Waiter(1000, now - 5), Waiter(1400, now - 5)
    c = Waiter(1100, now)
    assert pick_opponent(c, [a, b, c], now, RULE) is a
    assert pick_opponent(Waiter(1250, now), [a, b], now, RULE) is b  # 150 from B, 250 from A
    assert pick_opponent(Waiter(1200, now), [a, b], now, RULE) is None  # 200 from both

    early, late = Waiter(1050, now - 30), Waiter(1150, now - 10)
    assert pick_opponent(Waiter(1100, now), [late, early], now, RULE) is early


def test_spec007_a_lone_waiter_is_eligible_wider_the_longer_they_wait():
    """FR-030, US3-AS1 (O-M2): a newcomer 250 away is refused by a fresh waiter and admitted by
    one who waited 40 s — the larger of the two windows decides."""
    assert not eligible(1000, 0, 1250, 0, RULE)
    assert not eligible(1000, 39, 1250, 0, RULE)
    assert eligible(1000, 40, 1250, 0, RULE)
    assert eligible(1250, 0, 1000, 40, RULE)  # symmetric
    assert not eligible(1000, 10_000, 1451, 10_000, RULE)  # never beyond the ceiling

    now = 1000.0
    lone = Waiter(1000, now - 40)
    assert pick_opponent(Waiter(1250, now), [lone], now, RULE) is lone
    assert pick_opponent(Waiter(1250, now), [Waiter(1000, now - 39)], now, RULE) is None


# ── FR-031: the pair's day and the cap ──────────────────────────────────────


def test_spec007_the_pair_day_starts_at_midnight_in_colombia():
    """FR-031 (O-M4): the day runs from 00:00 in Bogotá, i.e. from 05:00 UTC."""
    utc = timezone.utc
    assert pair_day_start(datetime(2026, 10, 22, 5, 0, tzinfo=utc)) == datetime(
        2026, 10, 22, 5, 0, tzinfo=utc
    )
    assert pair_day_start(datetime(2026, 10, 22, 4, 59, tzinfo=utc)) == datetime(
        2026, 10, 21, 5, 0, tzinfo=utc
    )
    assert pair_day_start(datetime(2026, 10, 22, 23, 30, tzinfo=utc)) == datetime(
        2026, 10, 22, 5, 0, tzinfo=utc
    )
    bogota = timezone(timedelta(hours=-5))
    assert pair_day_start(datetime(2026, 10, 21, 23, 59, tzinfo=bogota)) == datetime(
        2026, 10, 21, 5, 0, tzinfo=utc
    )


def _row(status="finished", reason=None):
    return {"id": 1, "status": status, "elo_reason_p1": reason, "elo_reason_p2": reason}


def test_spec007_the_fourth_match_of_a_pair_in_a_day_is_not_rated():
    """FR-031 (O-M5): three finished rated rows → the next is unrated; a forfeit counts (it moved
    a rating); a `daily_cap` row and an abandoned row do not."""
    assert pair_match_is_rated([], 3)
    assert pair_match_is_rated([_row(), _row()], 3)
    assert not pair_match_is_rated([_row(), _row(), _row()], 3)
    assert not pair_match_is_rated([_row(), _row(), _row("finished", "forfeit")], 3)
    assert not pair_match_is_rated([_row(), _row(), _row(reason="no_rated_topics")], 3)
    assert pair_match_is_rated([_row(), _row(), _row(reason="daily_cap")], 3)
    assert pair_match_is_rated([_row(), _row(), _row("abandoned", "not_saved")], 3)
    assert pair_match_is_rated([_row(), _row(), _row("abandoned", "orphaned")], 3)
