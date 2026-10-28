"""
Spec 008 delivery C (FR-020, SC-003; plan-c.md O-C7): one copy of the course catalogue. Neither
repository holds its own course map, both read `src.domain.bank.catalogue`, and the bank
fingerprint hashes the catalogue's view of the bank's courses, so a change to a bank course's block
or name resyncs (FR-005) and an edit that changes none of them does not.
"""

import ast
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_PERSISTENCE = ROOT / "src" / "infrastructure" / "persistence"
_MAPS = {"_COURSE_BLOCK_MAP", "_COURSE_NAME_MAP"}


def _assigned_names(tree):
    names = set()
    for node in ast.walk(tree):
        targets = node.targets if isinstance(node, ast.Assign) else []
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
        names |= {t.id for t in targets if isinstance(t, ast.Name)}
    return names


def _imports_catalogue(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "src.domain.bank.catalogue":
            return True
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "src.domain.bank"
            and any(a.name == "catalogue" for a in node.names)
        ):
            return True
    return False


def test_spec008_c_neither_repository_holds_a_course_map():
    """FR-020, SC-003: one place writes a course's block and name."""
    for name in ("sqlite_repository.py", "postgres_repository.py"):
        source = (_PERSISTENCE / name).read_text(encoding="utf-8")
        tree = ast.parse(source)

        assert not (_assigned_names(tree) & _MAPS), name
        assert not any(m in source for m in _MAPS), name
        assert _imports_catalogue(tree), name


def _bank(tmp_path, course):
    bank = tmp_path / "bank"
    bank.mkdir()
    item = {
        "id": f"{course}_1",
        "content": "¿Cuánto es $2+2$?",
        "difficulty": 900,
        "topic": "Tema C",
        "options": ["3", "4"],
        "correct_option": "4",
    }
    (bank / f"{course}.json").write_text(json.dumps([item]), encoding="utf-8")
    return bank


def _fingerprints(db):
    conn = sqlite3.connect(db)
    try:
        return [r[0] for r in conn.execute("SELECT fingerprint FROM bank_syncs ORDER BY id")]
    finally:
        conn.close()


def test_spec008_c_the_fingerprint_hashes_the_catalogue(tmp_path, monkeypatch):
    """FR-020 with FR-005 (O-C7): each start of the repository records the bank fingerprint when
    it changed. A bank course's block or name changed in the catalogue → a new fingerprint (the
    bank resyncs); a catalogue entry for a course outside this bank → the same fingerprint."""
    from src.domain.bank import catalogue
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    course = "c008_fp"
    bank = _bank(tmp_path, course)
    db = str(tmp_path / "fp.db")
    monkeypatch.setattr(SQLiteRepository, "BANK_DIR", str(bank))
    courses = dict(catalogue.COURSES)
    courses[course] = ("Colegio", "Curso C")
    monkeypatch.setattr(catalogue, "COURSES", courses)

    SQLiteRepository(db_name=db)
    first = _fingerprints(db)
    assert len(first) == 1

    monkeypatch.setattr(catalogue, "COURSES", {**courses, "c008_otro": ("Colegio", "Otro")})
    SQLiteRepository(db_name=db)
    assert _fingerprints(db) == first  # no course of this bank changed

    monkeypatch.setattr(catalogue, "COURSES", {**courses, course: ("Colegio", "Curso C bis")})
    SQLiteRepository(db_name=db)
    renamed = _fingerprints(db)
    assert len(renamed) == 2 and renamed[1] != first[0]

    monkeypatch.setattr(catalogue, "COURSES", {**courses, course: ("Universidad", "Curso C bis")})
    SQLiteRepository(db_name=db)
    moved = _fingerprints(db)
    assert len(moved) == 3 and moved[2] not in moved[:2]
