"""Merges the ratings stored on the old fine topics of DIAN and EPA8 into their coarse topic
(spec 008 delivery T, the owner's rule A — specs/008-item-bank/plan-t.md § Decision).

Per student and course: the mean rating and mean RD (within 30–350) of the fine rows become the
coarse row, marked approximate with the fine keys as provenance; a coarse row the student already
has is never touched. Every fine row is archived in `student_course_topic_elo_archive` and removed
from the live store. Attempts are never touched. The regrouping is the one recorded when the banks
were edited (`topic_regrouping_008t.json`).

Run after the deploy that carries T: `python scripts/repairs/merge_fine_topic_ratings.py`
(counts), then with `--apply`.
"""

import argparse
import json
import os

from _repair import _repository

HERE = os.path.dirname(os.path.abspath(__file__))
REGROUPING = os.path.join(HERE, "topic_regrouping_008t.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the changes (default: count)")
    args = parser.parse_args()
    with open(REGROUPING, encoding="utf-8") as handle:
        regrouping = json.load(handle)
    rows = _repository().merge_fine_topic_ratings(regrouping, apply=args.apply)
    if args.apply:
        print(f"{rows} fine-topic ratings merged and archived")
    else:
        print(f"{rows} fine-topic ratings would be merged and archived (dry run; --apply to write)")
