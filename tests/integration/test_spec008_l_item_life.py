"""
Spec 008 delivery L (US4; FR-030, FR-031, FR-033): an item's life in the bank sync.

- `"retired": true` stamps `items.retired_at`; the row, its attempts and the ratings stay; the
  reads that serve items skip it; removing the mark (or `false`) serves it again.
- A bank difficulty edited since the last sync wins over the calibrated one (recorded in
  `item_difficulty_changes`, source `sync`); an untouched one keeps the calibration.
- No item row is ever deleted.

Both engines. Each test syncs its own temporary bank, whose course it registers in the catalogue.
"""

import json
import pathlib
import re
import uuid

from tests.integration.conftest import (
    answer,
    enroll,
    make_student,
    register_course,
    sql,
)
from tests.integration.test_spec002_d1_startup import (  # noqa: F401  (`database`: a fixture)
    _count,
    _repair as repair,
    database,
)

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_REPOSITORIES = [
    _ROOT / "src" / "infrastructure" / "persistence" / "sqlite_repository.py",
    _ROOT / "src" / "infrastructure" / "persistence" / "postgres_repository.py",
]


class LifeBank:
    """A temporary bank of one course whose items a test edits and syncs."""

    def __init__(self, tmp_path, monkeypatch, n=3, difficulty=900, topic="Vida", block=""):
        self.course = f"spec008l_{uuid.uuid4().hex[:10]}"
        register_course(monkeypatch, self.course)
        self.dir = tmp_path / f"bank_{self.course}"
        self.dir.mkdir()
        self.items = []
        for k in range(n):
            item = {
                "id": f"{self.course}_{k}",
                "content": f"¿Cuánto es ${k}+1$?",
                "difficulty": difficulty,
                "topic": topic,
                "options": ["A", "B", "C", "D"],
                "correct_option": "A",
            }
            if block:
                item["block"] = block
            self.items.append(item)

    @property
    def ids(self):
        return [item["id"] for item in self.items]

    def item(self, item_id):
        return next(item for item in self.items if item["id"] == item_id)

    def sync(self, repo):
        (self.dir / f"{self.course}.json").write_text(json.dumps(self.items), encoding="utf-8")
        repo.sync_items_from_bank_folder(str(self.dir))


def stored(repo, item_id, column):
    return sql(repo, f"SELECT {column} FROM items WHERE id = ?", (item_id,))[0][0]


def rating_rows(repo, user_id):
    return sorted(
        (r[0], r[1], float(r[2]), float(r[3]))
        for r in sql(
            repo,
            "SELECT course_id, topic, current_elo, rd FROM student_course_topic_elo"
            " WHERE user_id = ?",
            (user_id,),
        )
    )


def attempt_rows(repo, user_id):
    return [
        tuple(r)
        for r in sql(
            repo,
            "SELECT a.id, a.item_id, i.course_id, a.elo_before, a.elo_after FROM attempts a"
            " JOIN items i ON i.id = a.item_id WHERE a.user_id = ? ORDER BY a.id",
            (user_id,),
        )
    ]


def answered(repo, bank, item_id):
    """An enrolled student who answered `item_id` once, validly."""
    student = make_student(repo)
    enroll(repo, student, bank.course)
    answer(repo, student, item_id, correct=True)
    return student


# ── Phase 1: pins that hold on the unchanged code ───────────────────────────


def test_spec008_l_an_untouched_bank_difficulty_keeps_the_calibration(repo, tmp_path, monkeypatch):
    """FR-031, US4-AS2 (second half): an item calibrated by use keeps its difficulty while the
    bank value stays the one synced."""
    bank = LifeBank(tmp_path, monkeypatch, n=1)
    bank.sync(repo)
    item_id = bank.ids[0]
    answered(repo, bank, item_id)
    calibrated = float(stored(repo, item_id, "difficulty"))
    assert calibrated != 900.0  # the valid answer moved the item

    bank.sync(repo)

    assert float(stored(repo, item_id, "difficulty")) == calibrated


def test_spec008_l_history_keeps_a_retired_item(repo, client, tmp_path, monkeypatch):
    """US4-AS1 («its row and its attempts stay, its rating history is unchanged»): every read of
    history keeps a retired item."""
    from tests.integration.conftest import headers_for

    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.sync(repo)
    item_id = bank.ids[0]
    student = answered(repo, bank, item_id)
    headers = headers_for(repo, student)
    exam = client.post(
        "/api/student/exam/start",
        headers=headers,
        json={"course_id": bank.course, "n_questions": 3, "time_limit_minutes": 10},
    ).json()
    submitted = client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
        },
    )
    assert submitted.status_code == 200, submitted.text
    ratings, attempts = rating_rows(repo, student), attempt_rows(repo, student)
    responses = sql(
        repo,
        "SELECT r.item_id, i.topic FROM exam_responses r JOIN items i ON i.id = r.item_id"
        " WHERE r.item_id = ?",
        (item_id,),
    )

    bank.item(item_id)["retired"] = True
    bank.sync(repo)

    assert repo.get_item_by_id(item_id)["id"] == item_id
    assert attempt_rows(repo, student) == attempts and attempts
    assert rating_rows(repo, student) == ratings and ratings
    assert [tuple(r) for r in responses] == [(item_id, "Vida")]
    assert sql(
        repo,
        "SELECT r.item_id, i.topic FROM exam_responses r JOIN items i ON i.id = r.item_id"
        " WHERE r.item_id = ?",
        (item_id,),
    ) == list(responses)
    latest = client.get("/api/student/history", headers=headers).json()["attempts"]
    assert len(latest) == 1  # the one practice answer, on the retired item
    assert client.get("/api/student/exam/history", headers=headers).json()


def test_spec008_l_no_item_row_is_ever_deleted(repo, tmp_path, monkeypatch):
    """FR-030 («never delete an item row»): no repository deletes from `items`, and an id that
    leaves the bank file keeps its row."""
    for path in _REPOSITORIES:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"DELETE\s+FROM\s+items\b", text, re.IGNORECASE), path.name
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.sync(repo)
    gone = bank.items.pop()

    bank.sync(repo)

    assert repo.get_item_by_id(gone["id"])["id"] == gone["id"]


# ── Phase 2: [CHANGE] — retirement in the sync (FR-030, FR-033) ─────────────


def _moment(value):
    """A stored timestamp as text, to the second, on either engine."""
    return None if value is None else str(value)[:19]


def test_spec008_l_a_retired_item_is_stamped_and_kept(repo, tmp_path, monkeypatch):
    """FR-030, US4-AS1: the mark stamps `retired_at` and keeps the row; a resync keeps the first
    stamp; the attempts and the ratings do not move; a new id that arrives retired is inserted
    retired (O-IL13)."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.sync(repo)
    item_id = bank.ids[0]
    student = answered(repo, bank, item_id)
    ratings, attempts = rating_rows(repo, student), attempt_rows(repo, student)

    bank.item(item_id)["retired"] = True
    bank.sync(repo)

    assert stored(repo, item_id, "retired_at") is not None
    assert repo.get_item_by_id(item_id)["id"] == item_id
    assert attempt_rows(repo, student) == attempts and attempts
    assert rating_rows(repo, student) == ratings and ratings
    assert [stored(repo, i, "retired_at") for i in bank.ids[1:]] == [None, None]

    sql(repo, "UPDATE items SET retired_at = '2026-01-02 03:04:05' WHERE id = ?", (item_id,))
    bank.sync(repo)
    assert _moment(stored(repo, item_id, "retired_at")) == "2026-01-02 03:04:05"

    arriving = {**bank.items[1], "id": f"{bank.course}_new", "retired": True}
    bank.items.append(arriving)
    bank.sync(repo)
    assert stored(repo, arriving["id"], "retired_at") is not None
    assert repo.get_item_by_id(arriving["id"])["id"] == arriving["id"]


def test_spec008_l_removing_the_mark_serves_it_again(repo, tmp_path, monkeypatch):
    """FR-033: the mark removed, or set to `false`, clears the retirement and serves the item."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    removed, falsified = bank.ids[0], bank.ids[1]
    for item_id in (removed, falsified):
        bank.item(item_id)["retired"] = True
    bank.sync(repo)
    served = {i["id"] for i in repo.get_items_from_db(course_id=bank.course)}
    assert served == {bank.ids[2]}

    del bank.item(removed)["retired"]
    bank.item(falsified)["retired"] = False
    bank.sync(repo)

    assert [stored(repo, i, "retired_at") for i in (removed, falsified)] == [None, None]
    served = {i["id"] for i in repo.get_items_from_db(course_id=bank.course)}
    assert served == set(bank.ids)


# ── Phase 2: [CHANGE] — practice and blocks never serve a retired item (FR-030) ─


def test_spec008_l_practice_never_serves_a_retired_item(repo, tmp_path, monkeypatch):
    """FR-030, US4-AS1, SC-001: the item read every serving path shares skips a retired item,
    by course, by block and by topic; adaptive practice never draws it."""
    from src.application.services.student_service import StudentService

    bank = LifeBank(tmp_path, monkeypatch, n=3, block="Bloque L")
    retired = bank.ids[0]
    bank.item(retired)["retired"] = True
    bank.sync(repo)

    reads = [
        repo.get_items_from_db(course_id=bank.course),
        repo.get_items_from_db(course_id=bank.course, block="Bloque L"),
        repo.get_items_from_db(topic="Vida"),
    ]
    assert [{i["id"] for i in r} & set(bank.ids) for r in reads] == [set(bank.ids[1:])] * 3

    student = make_student(repo)
    enroll(repo, student, bank.course)
    service = StudentService(repository=repo)
    drawn = set()
    for _ in range(30):
        item, _status = service.get_next_question(
            student_id=student, course_id=bank.course, session_correct_ids=set()
        )
        drawn.add(item["id"])
    assert retired not in drawn and drawn <= set(bank.ids[1:])


def test_spec008_l_block_counts_skip_retired_items(repo, tmp_path, monkeypatch):
    """FR-030: the block picker counts only the items in circulation."""
    bank = LifeBank(tmp_path, monkeypatch, n=3, block="Bloque L")
    bank.item(bank.ids[0])["retired"] = True
    bank.sync(repo)

    assert repo.get_course_blocks(bank.course) == [{"block": "Bloque L", "item_count": 2}]


# ── Phase 2: [CHANGE] — the bank difficulty (FR-031) ─────────────────────────


def changes_of(repo, item_id):
    return [
        (r[0], float(r[1]), float(r[2]), r[3] is not None)
        for r in sql(
            repo,
            "SELECT source, previous_difficulty, new_difficulty, changed_at"
            " FROM item_difficulty_changes WHERE item_id = ? ORDER BY id",
            (item_id,),
        )
    ]


def test_spec008_l_an_edited_bank_difficulty_wins(repo, tmp_path, monkeypatch):
    """FR-031, US4-AS2 (first half): calibrated by use, then edited in the bank from 900 to 700
    → 700; the RD is untouched (O-IL11) and the change is recorded with source `sync` (O-IL8)."""
    bank = LifeBank(tmp_path, monkeypatch, n=1)
    bank.sync(repo)
    item_id = bank.ids[0]
    answered(repo, bank, item_id)
    calibrated = float(stored(repo, item_id, "difficulty"))
    rd = float(stored(repo, item_id, "rating_deviation"))
    assert calibrated != 900.0

    bank.item(item_id)["difficulty"] = 700
    bank.sync(repo)

    assert float(stored(repo, item_id, "difficulty")) == 700.0
    assert stored(repo, item_id, "bank_difficulty") == 700
    assert float(stored(repo, item_id, "rating_deviation")) == rd
    [(source, previous, new, timed)] = changes_of(repo, item_id)
    assert (source, new, timed) == ("sync", 700.0, True)
    assert abs(previous - calibrated) < 1e-3


def test_spec008_l_an_edit_equal_to_the_stored_difficulty_changes_nothing(
    repo, tmp_path, monkeypatch
):
    """FR-031 (spec § Edge Cases): a bank edit to the value the item already has changes nothing
    and records nothing."""
    bank = LifeBank(tmp_path, monkeypatch, n=1)
    bank.sync(repo)
    item_id = bank.ids[0]
    sql(repo, "UPDATE items SET difficulty = 700 WHERE id = ?", (item_id,))

    bank.item(item_id)["difficulty"] = 700
    bank.sync(repo)

    assert float(stored(repo, item_id, "difficulty")) == 700.0
    assert changes_of(repo, item_id) == []


def test_spec008_l_the_first_sync_after_the_migration_keeps_every_difficulty(
    repo, tmp_path, monkeypatch
):
    """FR-031, O-IL6: a row from before L (no bank value recorded) keeps its calibrated
    difficulty; the sync records the bank value and no change."""
    bank = LifeBank(tmp_path, monkeypatch, n=2)
    bank.sync(repo)
    calibrated, untouched = bank.ids
    sql(
        repo,
        "UPDATE items SET bank_difficulty = NULL, difficulty = 1234 WHERE id = ?",
        (calibrated,),
    )
    sql(repo, "UPDATE items SET bank_difficulty = NULL WHERE id = ?", (untouched,))

    bank.sync(repo)

    assert float(stored(repo, calibrated, "difficulty")) == 1234.0
    assert float(stored(repo, untouched, "difficulty")) == 900.0
    assert [stored(repo, i, "bank_difficulty") for i in bank.ids] == [900, 900]
    assert changes_of(repo, calibrated) == [] and changes_of(repo, untouched) == []


def _pre_l_fingerprint(bank_dir):
    """The bank fingerprint as delivery C computed it, before L's BANK_SYNC_FORMAT."""
    import hashlib
    import os

    from src.domain.bank.catalogue import fingerprint_view
    from src.infrastructure.persistence.schema_version import bank_files

    files = bank_files(bank_dir)
    view = fingerprint_view([os.path.relpath(p, bank_dir) for p in files])
    digest = hashlib.sha256()
    if view:
        digest.update(json.dumps(view, sort_keys=True, ensure_ascii=False).encode() + b"\0")
    for path in files:
        digest.update(os.path.relpath(path, bank_dir).replace(os.sep, "/").encode() + b"\0")
        with open(path, "rb") as handle:
            digest.update(hashlib.sha256(handle.read()).digest())
    return digest.hexdigest()


def test_spec008_l_the_upgrade_forces_one_sync(database, monkeypatch):
    """FR-031, O-IL7: a database whose last sync recorded the pre-L fingerprint resyncs once at
    the next start (filling every bank value), and not at the start after."""
    monkeypatch.setenv("ADMIN_PASSWORD", "l-admin")
    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    monkeypatch.setenv("ENVIRONMENT", "development")
    database.build()
    database.sql(
        "INSERT INTO bank_syncs (fingerprint) VALUES (?)",
        (_pre_l_fingerprint(database.repository_class.BANK_DIR),),
    )
    before = database.sql("SELECT COUNT(*) FROM bank_syncs")[0][0]

    database.build()
    after_upgrade = database.sql("SELECT COUNT(*) FROM bank_syncs")[0][0]
    database.build()

    assert after_upgrade == before + 1
    assert database.sql("SELECT COUNT(*) FROM bank_syncs")[0][0] == after_upgrade
    assert database.sql("SELECT COUNT(*) FROM items WHERE bank_difficulty IS NULL") == [(0,)]


# ── Phase 2: [CHANGE] — the orphan repair (FR-034, O-IL4) ────────────────────


def test_spec008_l_the_orphan_repair_counts_then_retires(database, monkeypatch):
    """FR-034: an item stored in the database that no bank file carries is counted by the
    count-only run, which writes nothing; `--apply` retires it; a second run changes nothing; a
    bank item is never touched."""
    monkeypatch.setenv("ADMIN_PASSWORD", "l-admin")
    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    monkeypatch.setenv("ENVIRONMENT", "development")
    database.build()
    orphan = f"albS_l_{uuid.uuid4().hex[:8]}"
    database.sql(
        "INSERT INTO items (id, topic, content, options, correct_option, difficulty,"
        " rating_deviation, course_id) VALUES (?, 'Vida', 'Pregunta L', '[\"A\", \"B\"]', 'A', 900, 350,"
        " 'algebra_basica')",
        (orphan,),
    )
    in_circulation = database.sql("SELECT COUNT(*) FROM items WHERE retired_at IS NULL")[0][0]

    counted = repair(database, "retire_orphan_items.py")
    assert _count(counted) == 1
    assert database.sql("SELECT retired_at FROM items WHERE id = ?", (orphan,)) == [(None,)]

    applied = repair(database, "retire_orphan_items.py", "--apply")
    assert _count(applied) == 1
    assert database.sql("SELECT retired_at IS NOT NULL FROM items WHERE id = ?", (orphan,)) in (
        [(1,)],
        [(True,)],
    )
    assert database.sql("SELECT COUNT(*) FROM items WHERE retired_at IS NULL")[0][0] == (
        in_circulation - 1
    )

    assert _count(repair(database, "retire_orphan_items.py", "--apply")) == 0
