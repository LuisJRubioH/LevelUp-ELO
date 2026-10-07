"""
Spec 001, FR-012a: a retry key returns the persisted attempt values, the first time too (T035b).

[CHANGE]: written before the fix. On PostgreSQL `attempts.elo_after` is a 4-byte REAL, so these
fixed values reproduce the old mismatch deterministically: the full-precision result
1189.3449518… rounds to 1189.34, while PostgreSQL sends its stored 4-byte value as the text
1189.345, which rounds to 1189.35. The seed is an integer so no store's rounding moves it.
The stored rating must keep the full-precision value, applied once (research R21).
"""

import uuid

import pytest

from src.domain.elo.model import rating_delta
from tests.integration.conftest import headers_for, make_course, rating_of, set_rating, sql

TOPIC = "Fracciones"
START = 1181.0
FULL_PRECISION_AFTER = START + rating_delta(START, 350.0, 1000.0, 1.0)


def test_spec001_boundary_values_are_a_real_boundary():
    assert round(FULL_PRECISION_AFTER, 2) == 1189.34
    assert FULL_PRECISION_AFTER == pytest.approx(1189.3449518674986, abs=1e-9)
    assert round(float("1189.345"), 2) == 1189.35  # what a 4-byte PostgreSQL value reads back as


def test_spec001_retry_returns_the_persisted_attempt_and_applies_once(repo, student, client):
    course, items = make_course(repo, [TOPIC], difficulty=1000.0)
    item_id = items[TOPIC][0]
    set_rating(repo, student, course, TOPIC, START)
    headers = {**headers_for(repo, student), "Idempotency-Key": "spec001-" + uuid.uuid4().hex}
    body = {"item_id": item_id, "selected_option": "A", "time_taken": 20}

    first = client.post("/api/student/answer", headers=headers, json=body)
    retry = client.post("/api/student/answer", headers=headers, json=body)

    assert (first.status_code, retry.status_code) == (200, 200)
    fields = ("is_correct", "elo_before", "elo_after", "rd_after", "delta_elo")
    assert {f: first.json()[f] for f in fields} == {f: retry.json()[f] for f in fields}
    persisted = sql(
        repo,
        "SELECT elo_before, elo_after, rating_deviation FROM attempts"
        " WHERE user_id = ? AND request_id = ?",
        (student, headers["Idempotency-Key"]),
    )
    assert len(persisted) == 1  # one attempt: the rating effect happened once
    before, after, rd = (float(v) for v in persisted[0])
    assert (first.json()["elo_before"], first.json()["elo_after"], first.json()["rd_after"]) == (
        round(before, 2),
        round(after, 2),
        round(rd, 2),
    )
    # Full precision in the rating state, applied once — never the persisted attempt value.
    assert rating_of(repo, student, course, TOPIC) == FULL_PRECISION_AFTER
