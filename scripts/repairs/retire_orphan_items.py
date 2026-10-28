"""Retires the items stored in the database that no bank file carries (spec 008 FR-034, O-IL4):
ids an older bank loaded and the current one no longer has (survey B8: `albS1` … `albS25`). It
stamps `items.retired_at`, so practice, exams and PvP stop serving them while their attempts and
ratings stay; it never deletes a row. The start never does this on its own (spec 002 FR-018).

Run after the deploy that carries delivery L: `python scripts/repairs/retire_orphan_items.py`
(counts), then with `--apply`.
"""

from _repair import run

if __name__ == "__main__":
    run(
        "retire_orphan_items",
        "items in no bank file, retired (retired_at stamped)",
        __doc__,
    )
