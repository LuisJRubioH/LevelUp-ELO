"""
Survey 008 B13 (`docs/sdd/item-bank-survey.md` § 7): a failed bank sync on SQLite left its
connection open, holding the write lock, so the next writer in the same process got «database is
locked». A failure must roll back and release the database. SQLite only: PostgreSQL's sync already
returns its connection to the pool in a `finally`.
"""

import json
import sqlite3
import uuid

import pytest


def test_a_failed_bank_sync_releases_the_database(tmp_path, monkeypatch):
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    db = str(tmp_path / "sync.db")
    repo = SQLiteRepository(db_name=db)
    bank = tmp_path / "bank"
    bank.mkdir()
    course = "b13_" + uuid.uuid4().hex[:6]
    item = {
        "id": f"{course}_1",
        "content": "¿Cuánto es $2+2$?",
        "difficulty": 900,
        "topic": "Tema B13",
        "options": ["3", "4"],
        "correct_option": "4",
    }
    (bank / f"{course}.json").write_text(json.dumps([item]), encoding="utf-8")
    # A block the courses CHECK refuses (a typo in the map): the sync fails.
    monkeypatch.setitem(SQLiteRepository._COURSE_BLOCK_MAP, course, "colegio")

    with pytest.raises(sqlite3.IntegrityError):
        repo.sync_items_from_bank_folder(str(bank))

    other = sqlite3.connect(db, timeout=0.5)
    try:
        other.execute("BEGIN IMMEDIATE")  # «database is locked» while the failed sync holds it
        other.rollback()
        assert other.execute("SELECT COUNT(*) FROM courses WHERE id = ?", (course,)).fetchone() == (
            0,
        )
    finally:
        other.close()
