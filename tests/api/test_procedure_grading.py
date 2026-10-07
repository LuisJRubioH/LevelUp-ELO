"""Calificación real en la SQLite temporal: propiedad, persistencia y cierre."""

import uuid

import pytest


@pytest.fixture
def submission(api_client, teacher_token):
    from api.dependencies import create_access_token, decode_token, get_repository

    repo = get_repository()
    teacher_id = int(decode_token(teacher_token)["sub"])
    group_id = repo.get_groups_by_teacher(teacher_id)[0]["group_id"]
    item = repo.get_items_from_db(course_id="calculo_diferencial")[0]
    suffix = uuid.uuid4().hex[:10]
    conn = repo.get_connection()
    try:
        student_id = conn.execute(
            "INSERT INTO users (username, password_hash, role, group_id) VALUES (?, ?, ?, ?)",
            (f"grading_student_{suffix}", "unused-test-hash", "student", group_id),
        ).lastrowid
        other_id = conn.execute(
            "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, 1)",
            (f"grading_teacher_{suffix}", "unused-test-hash", "teacher"),
        ).lastrowid
        submission_id = conn.execute(
            "INSERT INTO procedure_submissions "
            "(student_id, item_id, item_content, image_data, status, ai_proposed_score) "
            "VALUES (?, ?, ?, ?, 'PENDING_TEACHER_VALIDATION', 99)",
            (student_id, item["id"], item["content"], b"local test fixture"),
        ).lastrowid
        conn.commit()
    finally:
        conn.close()
    token = create_access_token(other_id, f"grading_teacher_{suffix}", "teacher")
    return {
        "id": submission_id,
        "student_id": student_id,
        "item_id": item["id"],
        "repo": repo,
        "other_headers": {"Authorization": "Bearer " + token},
    }


@pytest.mark.parametrize("score,delta", [(0, -10), (80, 6), (100, 10)])
def test_teacher_can_grade_own_pending_submission(
    api_client, teacher_headers, submission, score, delta
):
    response = api_client.post(
        "/api/teacher/procedures/grade",
        headers=teacher_headers,
        json={
            "submission_id": submission["id"],
            "teacher_score": score,
            "teacher_feedback": "Revisado",
        },
    )
    assert response.status_code == 200
    assert response.json()["elo_delta"] == delta
    repo = submission["repo"]
    saved = repo.get_student_submission(submission["student_id"], submission["item_id"])
    assert saved["teacher_score"] == score
    assert saved["final_score"] == score
    assert saved["ai_proposed_score"] == 99
    assert saved["teacher_feedback"] == "Revisado"
    assert saved["status"] == "VALIDATED_BY_TEACHER"
    history = repo.get_student_procedure_submissions(submission["student_id"])
    assert history[0]["elo_delta"] == delta

    # Una segunda petición no reabre ni altera una revisión cerrada.
    repeat = api_client.post(
        "/api/teacher/procedures/grade",
        headers=teacher_headers,
        json={"submission_id": submission["id"], "teacher_score": 50},
    )
    assert repeat.status_code == 404
    assert repo.get_student_submission(submission["student_id"], submission["item_id"]) == saved


def test_other_teacher_cannot_grade_or_view_submission(api_client, submission):
    repo = submission["repo"]
    before = repo.get_student_submission(submission["student_id"], submission["item_id"])
    ratings = repo.get_latest_elo_by_topic(submission["student_id"])
    response = api_client.post(
        "/api/teacher/procedures/grade",
        headers=submission["other_headers"],
        json={"submission_id": submission["id"], "teacher_score": 0},
    )
    assert response.status_code == 404
    image = api_client.get(
        f"/api/teacher/procedures/{submission['id']}/image", headers=submission["other_headers"]
    )
    assert image.status_code == 404
    assert repo.get_student_submission(submission["student_id"], submission["item_id"]) == before
    # FR-023 (spec 001, T009): a refused grade changes no rating.
    assert repo.get_latest_elo_by_topic(submission["student_id"]) == ratings


def test_nonexistent_submission_returns_404(api_client, teacher_headers):
    response = api_client.post(
        "/api/teacher/procedures/grade",
        headers=teacher_headers,
        json={"submission_id": 99999999, "teacher_score": 80},
    )
    assert response.status_code == 404


def test_reassignment_between_lookup_and_update_prevents_grading(
    api_client, teacher_headers, submission, monkeypatch
):
    repo = submission["repo"]
    ratings = repo.get_latest_elo_by_topic(submission["student_id"])
    original = repo.validate_procedure_submission

    def reassign_then_validate(*args, **kwargs):
        conn = repo.get_connection()
        try:
            conn.execute("UPDATE users SET group_id=NULL WHERE id=?", (submission["student_id"],))
            conn.commit()
        finally:
            conn.close()
        return original(*args, **kwargs)

    monkeypatch.setattr(repo, "validate_procedure_submission", reassign_then_validate)
    response = api_client.post(
        "/api/teacher/procedures/grade",
        headers=teacher_headers,
        json={"submission_id": submission["id"], "teacher_score": 80},
    )
    assert response.status_code == 404
    saved = repo.get_student_submission(submission["student_id"], submission["item_id"])
    assert saved["status"] == "PENDING_TEACHER_VALIDATION"
    assert saved["teacher_score"] is None
    assert repo.get_latest_elo_by_topic(submission["student_id"]) == ratings
