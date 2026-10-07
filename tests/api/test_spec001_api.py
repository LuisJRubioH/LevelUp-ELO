"""
Spec 001 behaviour changes through the HTTP API (SQLite, tests/api).

[CHANGE] tests: each was written before its implementation task and failed first.
"""

from tests.api.test_spec001_answer_pins import _answer, _item, _student
from tests.integration.conftest import sql

# ── T035: FR-009, FR-008 — an invalid attempt reports no change ─────────────


def test_spec001_invalid_time_reports_and_records_no_change(api_client):
    repo, user_id, headers = _student(api_client)
    _, (item,) = _item(repo)

    response = api_client.post(
        "/api/student/answer",
        headers=headers,
        json={"item_id": item["id"], "selected_option": "A", "time_taken": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["elo_valid"] is False
    assert body["delta_elo"] == 0
    assert body["elo_after"] == body["elo_before"]
    stored = sql(repo, "SELECT elo_before, elo_after FROM attempts WHERE user_id = ?", (user_id,))
    assert [(float(b), float(a)) for b, a in stored] == [(body["elo_before"], body["elo_before"])]


def test_spec001_valid_answer_reports_elo_valid(api_client):
    repo, _, headers = _student(api_client)
    _, (item,) = _item(repo)

    body = _answer(api_client, headers, item).json()

    assert body["elo_valid"] is True
    assert body["elo_after"] == 1016.0
