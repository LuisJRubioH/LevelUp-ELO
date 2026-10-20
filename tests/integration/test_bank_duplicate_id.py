"""
Survey 008 B22 (`docs/sdd/item-bank-survey.md` § 7): an id present in two bank files resolved
differently per engine. SQLite kept the last file's item; PostgreSQL kept the last one for an
item already in the database but the FIRST for a new one (`ON CONFLICT DO NOTHING` dropped the
second insert). R1: the same bank gives the same items on both engines — the last file read wins,
as it always did on SQLite. `validate_bank.py` rejects duplicates, so this needs a bank that
bypassed CI; the sync must still agree with itself.
"""

import json
import uuid

from tests.integration.conftest import sql


def _item(item_id, topic):
    return {
        "id": item_id,
        "content": f"¿Cuánto es $1+1$? ({topic})",
        "difficulty": 900,
        "topic": topic,
        "options": ["$1$", "$2$"],
        "correct_option": "$2$",
    }


def _bank(tmp_path, item_id, tag):
    """Two files, read in this order, that both carry `item_id`."""
    bank = tmp_path / "bank"
    bank.mkdir()
    first, second = f"b22a_{tag}", f"b22b_{tag}"
    (bank / f"{first}.json").write_text(json.dumps([_item(item_id, "Primero")]), encoding="utf-8")
    (bank / f"{second}.json").write_text(json.dumps([_item(item_id, "Segundo")]), encoding="utf-8")
    return bank, second


def _stored(repo, item_id):
    return tuple(sql(repo, "SELECT course_id, topic FROM items WHERE id = ?", (item_id,))[0])


def test_a_new_duplicate_id_keeps_the_last_files_item(repo, tmp_path):
    tag = uuid.uuid4().hex[:8]
    item_id = f"b22_{tag}"
    bank, last_course = _bank(tmp_path, item_id, tag)

    repo.sync_items_from_bank_folder(str(bank))

    assert _stored(repo, item_id) == (last_course, "Segundo")


def test_an_existing_duplicate_id_keeps_the_last_files_item(repo, tmp_path):
    tag = uuid.uuid4().hex[:8]
    item_id = f"b22_{tag}"
    bank, last_course = _bank(tmp_path, item_id, tag)
    repo.sync_items_from_bank_folder(str(bank))
    for path in bank.iterdir():  # an edit to both copies: the item now exists
        data = json.loads(path.read_text(encoding="utf-8"))
        data[0]["content"] += " (editado)"
        path.write_text(json.dumps(data), encoding="utf-8")

    repo.sync_items_from_bank_folder(str(bank))

    assert _stored(repo, item_id) == (last_course, "Segundo")
