"""Recalibrates item difficulties, audited (spec 008 FR-032; plan-l.md O-IL9, O-IL10).

    python scripts/recalibrate_items.py                       # dstar, every course: counts only
    python scripts/recalibrate_items.py --course DIAN --apply
    python scripts/recalibrate_items.py --method bank --course DIAN --course SENA

- `--method dstar` (default): for every item in circulation with at least 10 valid attempts, the
  difficulty at which the students who answered it would be expected to get as many right as they
  did (success count smoothed toward ½), clamped to 400–2000 and rounded; planned when it moves
  by 25 or more.
- `--method bank`: every item whose difficulty differs from the bank value last synced takes it
  (e.g. the DIAN and SENA values a database synced before delivery L never received, O-IL6).

By default it prints counts — items examined, planned changes per course, mean and largest |Δ| —
and writes nothing. `--apply` writes, recording every change in `item_difficulty_changes` (item,
previous and new difficulty, source, detail, time); an item an answer moved since the plan is
skipped. It prints counts only, never student data (constitution VI).

Engine as the repair scripts: PostgreSQL through MIGRATION_DATABASE_URL or DATABASE_URL, else the
local SQLite of DB_PATH; built with RUN_MIGRATIONS=0, so it migrates and syncs nothing.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "repairs"))

from _repair import _repository  # noqa: E402

from src.domain.bank.recalibration import plan_recalibration  # noqa: E402


def _report(plan: list[dict], examined: int, method: str) -> None:
    print(f"method {method} · {examined} items examined · {len(plan)} planned")
    by_course: dict[str, list[float]] = {}
    for change in plan:
        by_course.setdefault(change["course_id"], []).append(
            abs(change["new"] - change["previous"])
        )
    for course, deltas in sorted(by_course.items()):
        print(
            f"  {course}: {len(deltas)} planned, mean |Δ| {sum(deltas) / len(deltas):.0f},"
            f" largest |Δ| {max(deltas):.0f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--method", choices=("dstar", "bank"), default="dstar")
    parser.add_argument("--course", action="append", help="limit to a course (repeatable)")
    parser.add_argument("--apply", action="store_true", help="write the changes (default: count)")
    args = parser.parse_args()

    repo = _repository()
    rows = repo.get_item_calibration_rows(args.course)
    plan = plan_recalibration(rows, args.method)
    _report(plan, len({r["item_id"] for r in rows}), args.method)
    if not args.apply:
        print("dry run: nothing written; --apply to write")
        return 0
    result = repo.apply_item_difficulty_changes(plan, args.method)
    print(
        f"{result['applied']} applied, {result['skipped_moved']} skipped"
        " (moved by an answer since the plan)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
