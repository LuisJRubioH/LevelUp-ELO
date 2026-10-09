"""
PostgreSQL writes of many rows go out in batches, not one round trip per row.

psycopg2's `executemany` sends one statement per row. Every start runs the bank sync, which
re-synchronises each of the ~2,000 items: through a proxy adding a 10 ms database round trip,
`scripts/migrate.py` took 24.6 s (22.9 s in the sync) instead of 1.5 s, on every cold start of
the free plan. An exam submission inserted its responses one by one the same way.
"""

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


def test_the_bank_sync_restores_items_in_a_few_statements(_postgres_repo, counting):
    repo = _postgres_repo
    item_id, content = sql(repo, "SELECT id, content FROM items ORDER BY id LIMIT 1")[0]
    sql(repo, "UPDATE items SET content = 'stale' WHERE id = ?", (item_id,))
    counting.sent = 0

    repo.sync_items_from_bank_folder()

    assert sql(repo, "SELECT content FROM items WHERE id = ?", (item_id,))[0][0] == content
    assert counting.sent <= 50, f"{counting.sent} statements for one bank sync"


def test_an_exam_inserts_its_responses_in_a_few_statements(_postgres_repo, counting):
    repo = _postgres_repo
    user = make_student(repo)
    item_ids = [row[0] for row in sql(repo, "SELECT id FROM items ORDER BY id LIMIT 30")]
    responses = [
        {"item_id": item_id, "topic": "t", "is_correct": n % 2 == 0}
        for n, item_id in enumerate(item_ids)
    ]
    counting.sent = 0

    session_id = repo.save_exam_session(
        user, "algebra_basica", "Álgebra", len(responses), 15, 50.0, None, responses=responses
    )

    stored = sql(
        repo,
        "SELECT item_id, is_correct FROM exam_responses WHERE session_id = ? ORDER BY item_id",
        (session_id,),
    )
    assert stored == sorted((r["item_id"], 1 if r["is_correct"] else 0) for r in responses)
    assert counting.sent <= 10, f"{counting.sent} statements for one exam"
