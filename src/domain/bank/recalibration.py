"""Spec 008 delivery L: how an item's difficulty changes outside an answer (FR-031, FR-032).

Pure functions, standard library only; the repositories and `scripts/recalibrate_items.py` read
and write.

- `sync_difficulty` (FR-031, O-IL6): what the bank sync does with an item's difficulty — a bank
  value edited since the last sync wins, an untouched one keeps the calibration, and the first
  sync after the migration records the bank value without changing anything.
- `plan_recalibration` (FR-032, O-IL9): the changes the recalibration script proposes, from raw
  rows of valid attempts (`dstar`) or from the bank values (`bank`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.domain.bank.rules import DIFFICULTY_RANGE
from src.domain.elo.model import dstar

MIN_ATTEMPTS = 10  # scripts/monthly_metrics.py's threshold for «recalibrate or retire»
MIN_CHANGE = 25


@dataclass(frozen=True)
class SyncDifficulty:
    """What the sync writes: `difficulty` None leaves it; `audit` records (previous, new)."""

    bank_difficulty: int
    difficulty: float | None = None
    audit: tuple[float, float] | None = None


def sync_difficulty(
    stored_difficulty: float, stored_bank: int | None, bank_value: int
) -> SyncDifficulty | None:
    """None when nothing changes. The bank value differing from the one last synced sets the
    difficulty (recorded, source `sync`, O-IL8) unless the item already has it (spec § Edge
    Cases); no bank value recorded yet (O-IL6) records it and keeps the difficulty."""
    if stored_bank is not None and int(stored_bank) == bank_value:
        return None
    if stored_bank is None or float(stored_difficulty) == float(bank_value):
        return SyncDifficulty(bank_difficulty=bank_value)
    return SyncDifficulty(
        bank_difficulty=bank_value,
        difficulty=float(bank_value),
        audit=(float(stored_difficulty), float(bank_value)),
    )


def plan_recalibration(
    rows: Iterable[dict],
    method: str,
    min_attempts: int = MIN_ATTEMPTS,
    min_change: float = MIN_CHANGE,
) -> list[dict]:
    """The changes to write, one dict per item: `item_id`, `course_id`, `previous`, `new` (an
    integer in 400–2000) and `detail`.

    `rows` are raw rows, one per valid attempt (`elo_before` None for an item never answered):
    `item_id, course_id, difficulty, bank_difficulty, retired_at, elo_before, is_correct`.

    - `dstar`: items in circulation with at least `min_attempts` valid attempts; the success
      count is smoothed toward ½ — share (s + ½)/(n + 1) — so 0 % and 100 % stay finite; the
      difficulty that expects that many successes is clamped, rounded, and planned when it moves
      by at least `min_change`.
    - `bank`: every item whose difficulty differs from its recorded bank value takes it.
    """
    if method not in ("dstar", "bank"):
        raise ValueError(f"unknown method {method!r}: dstar or bank")
    items: dict[str, dict] = {}
    for row in rows:
        item = items.setdefault(row["item_id"], {**row, "ratings": [], "successes": 0})
        if row["elo_before"] is not None:
            item["ratings"].append(float(row["elo_before"]))
            item["successes"] += 1 if row["is_correct"] else 0

    low, high = DIFFICULTY_RANGE
    plan = []
    for item_id, item in sorted(items.items()):
        previous = float(item["difficulty"])
        if method == "bank":
            bank = item["bank_difficulty"]
            if bank is None or float(bank) == previous:
                continue
            new, detail = int(bank), None
        else:
            n, s = len(item["ratings"]), item["successes"]
            if item["retired_at"] is not None or n < min_attempts:
                continue
            target = (s + 0.5) / (n + 1) * n
            new = int(round(min(high, max(low, dstar(item["ratings"], target, low, high)))))
            if abs(new - previous) < min_change:
                continue
            detail = f"{n} attempts, {s} successes"
        plan.append(
            {
                "item_id": item_id,
                "course_id": item["course_id"],
                "previous": previous,
                "new": new,
                "detail": detail,
            }
        )
    return plan
