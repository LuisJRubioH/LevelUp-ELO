"""
Spec 001 characterization pins through the HTTP API (tasks T014, T017). SQLite (tests/api).

[AS-IS]: these hold on the code before the spec 001 refactor. Each test seeds its own course
and student, so nothing depends on the bank's items or on other tests' answers.
"""

import uuid

import pytest

from tests.integration.conftest import make_course, rating_of, sql

TOPIC = "Fracciones"
LEAGUES = {"Bronce", "Plata", "Oro", "Diamante"}


def _student(api_client):
    """A fresh student and its headers; the token is minted directly (no auth rate limit)."""
    from api.dependencies import create_access_token, get_repository

    repo = get_repository()
    username = f"spec001_{uuid.uuid4().hex[:10]}"
    ok, msg = repo.register_user(username, "password123", "student", education_level="colegio")
    assert ok, msg
    user_id = sql(repo, "SELECT id FROM users WHERE username = ?", (username,))[0][0]
    token = create_access_token(user_id, username, "student")
    return repo, user_id, {"Authorization": "Bearer " + token}


def _item(repo, **kwargs):
    course_id, items = make_course(repo, [TOPIC], **kwargs)
    return course_id, [repo.get_item_by_id(i) for i in items[TOPIC]]


def _answer(api_client, headers, item, option="A", key=None):
    if key is not None:
        headers = {**headers, "Idempotency-Key": key}
    return api_client.post(
        "/api/student/answer",
        headers=headers,
        json={"item_id": item["id"], "selected_option": option, "time_taken": 20},
    )


def _attempts(repo, user_id):
    return sql(repo, "SELECT COUNT(*) FROM attempts WHERE user_id = ?", (user_id,))[0][0]


def _state(repo, user_id, items):
    difficulties = [repo.get_item_by_id(i["id"])["difficulty"] for i in items]
    return repo.get_course_topic_ratings(user_id), difficulties


# ── T014: FR-012, FR-013, FR-014, FR-032, US1-AS4, US1-AS5, US6-AS4 ─────────


def test_spec001_retry_with_the_same_key_returns_the_stored_result(api_client):
    """US1-AS4: same key, same answer → the stored result, one attempt, nothing moves again."""
    repo, user_id, headers = _student(api_client)
    _, (item,) = _item(repo)
    key = "spec001-" + uuid.uuid4().hex

    first = _answer(api_client, headers, item, key=key)
    after_first = _state(repo, user_id, [item])
    replay = _answer(api_client, headers, item, key=key)

    assert (first.status_code, replay.status_code) == (200, 200)
    fields = ("is_correct", "elo_before", "elo_after", "delta_elo")
    assert {f: replay.json()[f] for f in fields} == {f: first.json()[f] for f in fields}
    assert replay.json()["cog_data"] == {"idempotent_replay": True}
    assert _attempts(repo, user_id) == 1
    assert _state(repo, user_id, [item]) == after_first


def test_spec001_same_key_for_another_answer_is_a_conflict(api_client):
    """US1-AS5: the key belongs to option A; option B under it → 409, nothing recorded."""
    repo, user_id, headers = _student(api_client)
    _, (item,) = _item(repo)
    key = "spec001-" + uuid.uuid4().hex
    assert _answer(api_client, headers, item, "A", key=key).status_code == 200
    after_first = _state(repo, user_id, [item])

    conflict = _answer(api_client, headers, item, "B", key=key)

    assert conflict.status_code == 409
    assert _attempts(repo, user_id) == 1
    assert _state(repo, user_id, [item]) == after_first


@pytest.mark.parametrize("key,status", [("", 400), ("k" * 129, 400), ("k" * 128, 200)])
def test_spec001_retry_key_length_is_1_to_128(api_client, key, status):
    """Edge "retry key empty or > 128 chars": rejected before anything is recorded."""
    repo, user_id, headers = _student(api_client)
    _, (item,) = _item(repo)

    response = _answer(api_client, headers, item, key=key)

    assert response.status_code == status
    assert _attempts(repo, user_id) == (1 if status == 200 else 0)


def test_spec001_no_response_carries_the_correct_option(api_client):
    """FR-014: neither /answer nor the exam endpoints send the correct option."""
    repo, _, headers = _student(api_client)
    course_id, items = _item(repo, items_per_topic=3)

    answered = _answer(api_client, headers, items[0])
    start = api_client.post(
        "/api/student/exam/start", headers=headers, json={"course_id": course_id, "n_questions": 3}
    )
    submit = api_client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": start.json()["session_id"],
            "answers": [
                {"item_id": i["id"], "selected_option": "A"} for i in start.json()["items"]
            ],
        },
    )

    assert [r.status_code for r in (answered, start, submit)] == [200, 200, 200]
    for response in (answered, start, submit):
        assert "correct_option" not in response.text


def test_spec001_exam_submission_changes_no_rating(api_client):
    """FR-032, US6-AS4 (API half): an all-correct exam leaves ratings and difficulties as is."""
    repo, user_id, headers = _student(api_client)
    course_id, items = _item(repo, items_per_topic=3)
    assert _answer(api_client, headers, items[0]).status_code == 200
    before = _state(repo, user_id, items)

    start = api_client.post(
        "/api/student/exam/start", headers=headers, json={"course_id": course_id, "n_questions": 3}
    ).json()
    submit = api_client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": start["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in start["items"]],
        },
    )

    assert submit.status_code == 200
    assert submit.json()["correct_count"] == len(start["items"])
    assert all(r["elo_delta"] == 0.0 for r in submit.json()["results"])
    assert _state(repo, user_id, items) == before


# ── T017: FR-020, FR-031a, US3-AS1, US3-AS2, US3-AS4 ────────────────────────


def _diagnostic(api_client, headers, course_id, answers):
    return api_client.post(
        f"/api/student/diagnostic/{course_id}/submit",
        headers=headers,
        json={"answers": [{"item_id": i, "selected_option": o} for i, o in answers]},
    )


def test_spec001_diagnostic_correct_at_1200_and_a_skipped_answer(api_client):
    """US3-AS1 + US3-AS4: one correct at difficulty 1200 → 1000 + 22; the skip adds nothing."""
    repo, user_id, headers = _student(api_client)
    course_id, (solved, skipped) = _item(repo, difficulty=1200.0, items_per_topic=2)

    response = _diagnostic(
        api_client, headers, course_id, [(solved["id"], "A"), (skipped["id"], "")]
    )

    assert response.status_code == 200
    body = response.json()
    assert body["initial_elo"] == 1022.0
    assert body["answered"] == 1
    assert [(t["topic"], t["correct"], t["total"], t["elo"]) for t in body["themes"]] == [
        (TOPIC, 1, 2, 1022.0)
    ]
    assert rating_of(repo, user_id, course_id, TOPIC) == 1022.0
    assert body["league"]["name"] == "Bronce" and body["league"]["name"] in LEAGUES


def test_spec001_diagnostic_floor_is_760(api_client):
    """US3-AS2: thirteen wrong answers below 1100 → 1000 − 260 = 740, floored at 760."""
    repo, user_id, headers = _student(api_client)
    course_id, items = _item(repo, difficulty=1000.0, items_per_topic=13)

    response = _diagnostic(api_client, headers, course_id, [(i["id"], "B") for i in items])

    assert response.status_code == 200
    assert response.json()["initial_elo"] == 760.0
    assert rating_of(repo, user_id, course_id, TOPIC) == 760.0
    assert response.json()["league"]["name"] in LEAGUES
