"""
PostgreSQL startup and many-row writes cost few round trips, whatever the bank's size.

psycopg2's `executemany` sends one statement per row. Every start ran the bank sync, which
rewrote each of the ~2,000 items: through a proxy adding a 10 ms database round trip,
`scripts/migrate.py` took 24.6 s (22.9 s in the sync) instead of 1.5 s, on every cold start of
the free plan. Now a start whose bank did not change writes no item, a changed item costs one
batched statement, and an exam stores its responses in a few batched statements.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from psycopg2.extras import RealDictCursor

from src.infrastructure.persistence import postgres_repository
from tests.integration.conftest import make_student, sql


class _CountingCursor(RealDictCursor):
    """Counts the statements sent to the server: one per execute, one per executemany row."""

    sent = 0

    def execute(self, query, vars=None):
        _CountingCursor.sent += 1
        return super().execute(query, vars)

    def executemany(self, query, vars_list):
        vars_list = list(vars_list)
        _CountingCursor.sent += len(vars_list)
        return super().executemany(query, vars_list)


@pytest.fixture
def counting(monkeypatch):
    monkeypatch.setattr(postgres_repository, "RealDictCursor", _CountingCursor)
    _CountingCursor.sent = 0
    return _CountingCursor


def _sync(repo, counting) -> int:
    """Run the bank sync; fail if its lock was busy (a skipped sync proves nothing)."""
    skipped_before = repo.bootstrap_skipped_steps().count("sync_items_from_bank_folder")
    counting.sent = 0
    repo.sync_items_from_bank_folder()
    skipped_after = repo.bootstrap_skipped_steps().count("sync_items_from_bank_folder")
    assert skipped_after == skipped_before, "the sync was skipped: its advisory lock was busy"
    return counting.sent


def test_a_start_whose_bank_did_not_change_writes_no_item(_postgres_repo, counting):
    repo = _postgres_repo
    _sync(repo, counting)  # whatever this database held, it now matches the bank
    xmin_before = sql(repo, "SELECT id, xmin::text FROM items ORDER BY id")

    sent = _sync(repo, counting)

    assert sql(repo, "SELECT id, xmin::text FROM items ORDER BY id") == xmin_before
    assert sent <= 5, f"{sent} statements for a sync with nothing to do"


def test_the_bank_sync_restores_a_changed_item_in_one_more_statement(_postgres_repo, counting):
    repo = _postgres_repo
    unchanged = _sync(repo, counting)
    item_id, content = sql(repo, "SELECT id, content FROM items ORDER BY id LIMIT 1")[0]
    try:
        sql(repo, "UPDATE items SET content = 'stale' WHERE id = ?", (item_id,))
        restoring = _sync(repo, counting)
        assert sql(repo, "SELECT content FROM items WHERE id = ?", (item_id,))[0][0] == content
    finally:
        sql(repo, "UPDATE items SET content = ? WHERE id = ?", (content, item_id))
    assert restoring <= unchanged + 1, f"{restoring} statements to restore one item"


def _responses(repo, n):
    item_ids = [row[0] for row in sql(repo, "SELECT id FROM items ORDER BY id LIMIT ?", (n,))]
    return [
        {"item_id": item_id, "topic": "t", "is_correct": k % 2 == 0}
        for k, item_id in enumerate(item_ids)
    ]


def _stored(repo, history_id):
    return sql(
        repo,
        "SELECT item_id, is_correct FROM exam_responses WHERE session_id = ? ORDER BY item_id",
        (history_id,),
    )


def test_an_exam_inserts_its_responses_in_a_few_statements(_postgres_repo, counting):
    repo = _postgres_repo
    user = make_student(repo)
    responses = _responses(repo, 30)
    counting.sent = 0

    history_id = repo.save_exam_session(
        user, "algebra_basica", "Álgebra", len(responses), 15, 50.0, None, responses=responses
    )

    assert _stored(repo, history_id) == sorted(
        (r["item_id"], 1 if r["is_correct"] else 0) for r in responses
    )
    assert counting.sent <= 10, f"{counting.sent} statements for one exam"


def test_an_active_exam_submission_inserts_its_responses_in_a_few_statements(
    _postgres_repo, counting
):
    repo = _postgres_repo
    user = make_student(repo)
    responses = _responses(repo, 30)
    session_id = uuid.uuid4().hex
    expires = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    repo.create_active_exam_session(
        session_id, user, "algebra_basica", None, [r["item_id"] for r in responses], expires
    )
    result = {
        "total_questions": 30,
        "correct_count": 15,
        "score_pct": 50.0,
        "global_elo_after": None,
    }
    counting.sent = 0

    assert repo.complete_active_exam_session(session_id, user, "Álgebra", result, responses)

    sent = counting.sent
    history_id = sql(
        repo, "SELECT id FROM exam_sessions WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user,)
    )[0][0]
    assert _stored(repo, history_id) == sorted(
        (r["item_id"], 1 if r["is_correct"] else 0) for r in responses
    )
    assert sent <= 10, f"{sent} statements for one exam submission"
