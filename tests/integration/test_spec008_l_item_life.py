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
