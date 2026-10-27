"""
src/domain/pvp/matchmaking.py
=============================
Spec 007 delivery M (FR-030, FR-031; owner decisions O-M1 … O-M5, O-M7). Pure — no clock, no I/O:
the caller passes the times and the numbers (`api/config.py`).

- The window (FR-030, O-M1): ±`start` at entry, + `step` for every full `every_s` waited, at most
  ±`ceiling`.
- Who may meet (O-M2): two waiters whose rating gap is within the larger of their two windows, so
  a long waiter admits a newcomer the newcomer's own window would refuse.
- Which one (O-M3): the smallest gap among the eligible, ties broken by the longest wait.
- The pair's day (O-M4): the calendar day in Colombia, a fixed UTC−5 (no daylight saving there).
- The cap (O-M5): a pair's match is rated while fewer than `cap` of the pair's matches that day
  moved a rating — finished rows not closed as `daily_cap`; a forfeit counts, an abandoned row
  does not. The cap never changes who meets whom (O-M7): an over-cap match is played unrated.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Mapping, Protocol, Sequence, TypeVar

# Colombia keeps UTC−5 all year: its day starts at 05:00 UTC.
COLOMBIA = timezone(timedelta(hours=-5))
DAILY_CAP_REASON = "daily_cap"


def window(waited_s: float, start: float, step: float, every_s: float, ceiling: float) -> float:
    """The half-width of a waiter's rating window after `waited_s` seconds in the queue."""
    steps = math.floor(max(0.0, waited_s) / every_s) if every_s > 0 else 0
    return min(ceiling, start + step * steps)


@dataclass(frozen=True)
class WindowRule:
    """The window's numbers (O-M1), read once from the settings and passed in."""

    start: float = 150
    step: float = 50
    every_s: float = 20
    ceiling: float = 450

    def width(self, waited_s: float) -> float:
        return window(waited_s, self.start, self.step, self.every_s, self.ceiling)


def eligible(
    rating_a: float, waited_a: float, rating_b: float, waited_b: float, rule: WindowRule
) -> bool:
    """O-M2: the gap is within the larger of the two windows."""
    return abs(rating_a - rating_b) <= max(rule.width(waited_a), rule.width(waited_b))


class Waiting(Protocol):
    rating: float  # the rating the window uses (1000 for an unrated player, O-M10)
    joined_at: float  # when they entered the queue, on the caller's clock


W = TypeVar("W", bound=Waiting)


def pick_opponent(me: W, waiting: Sequence[W], now: float, rule: WindowRule) -> W | None:
    """O-M3: among the eligible waiters other than `me`, the nearest rating, then the longest
    wait; None when nobody is eligible."""
    my_wait = now - me.joined_at
    best: W | None = None
    best_key: tuple[float, float] | None = None
    for other in waiting:
        if other is me:
            continue
        if not eligible(me.rating, my_wait, other.rating, now - other.joined_at, rule):
            continue
        key = (abs(me.rating - other.rating), other.joined_at)
        if best_key is None or key < best_key:
            best, best_key = other, key
    return best


def pair_day_start(now: datetime) -> datetime:
    """O-M4: the start, in UTC, of the Colombian calendar day that contains `now` (aware)."""
    local = now.astimezone(COLOMBIA)
    midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(timezone.utc)


def _moved_a_rating(row: Mapping) -> bool:
    return (
        row.get("status") == "finished"
        and row.get("elo_reason_p1") != DAILY_CAP_REASON
        and row.get("elo_reason_p2") != DAILY_CAP_REASON
    )


def pair_match_is_rated(rows: Iterable[Mapping], cap: int) -> bool:
    """O-M5: True while the pair's rows of the day hold fewer than `cap` rated matches."""
    return sum(1 for row in rows if _moved_a_rating(row)) < cap
