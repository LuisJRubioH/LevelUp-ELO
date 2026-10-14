"""
The bank's answer keys are consistent: no item offers the same answer twice, and two copies of a
question never disagree on its key. Read from items/bank/ and items/bank/semillero/, the folders
the sync loads.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BANK = ROOT / "items" / "bank"


def _items():
    for path in sorted([*BANK.glob("*.json"), *(BANK / "semillero").glob("*.json")]):
        for item in json.loads(path.read_text(encoding="utf-8")):
            yield path.name, item


def _same(text):
    """Text as the student reads it: spacing, TeX spacing commands included, does not count."""
    return re.sub(r"\s+|\\[,;:! ]", "", str(text))


def test_no_item_offers_the_same_answer_twice():
    """Two options that read the same make the item unanswerable: only one of them is the key."""
    repeated = []
    for name, item in _items():
        seen = defaultdict(list)
        for option in item["options"]:
            seen[_same(option)].append(option)
        repeated += [(name, item["id"], same) for same in seen.values() if len(same) > 1]
    assert repeated == []


def test_copies_of_a_question_share_the_key():
    """The same statement with the same options, in two courses, has one right answer."""
    copies = defaultdict(list)
    for name, item in _items():
        question = (_same(item["content"]), tuple(sorted(_same(o) for o in item["options"])))
        copies[question].append((name, item["id"], _same(item["correct_option"])))
    disagreeing = [group for group in copies.values() if len({key for *_, key in group}) > 1]
    assert disagreeing == []
