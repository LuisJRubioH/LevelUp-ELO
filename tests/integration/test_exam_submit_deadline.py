"""An exam submitted shortly after its time limit is still graded: the answer travels after the
student's clock reaches zero. Both engines."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.integration.conftest import headers_for, make_student, sql

COURSE = "algebra_basica"
LIMIT_SECONDS = 5 * 60


def _start(client, headers):
    response = client.post(
        "/api/student/exam/start",
        headers=headers,
        json={"course_id": COURSE, "n_questions": 1, "time_limit_minutes": 5},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _as_if_started_ago(repo, session_id, seconds):
    """Move the session's stored deadline back as if the exam had started `seconds` ago."""
    deadline = sql(repo, "SELECT expires_at FROM active_exam_sessions WHERE id = ?", (session_id,))
    deadline = deadline[0][0]
    if isinstance(deadline, str):
        deadline = datetime.fromisoformat(deadline)
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    moved = deadline - timedelta(seconds=seconds)
    value = moved.replace(tzinfo=None) if hasattr(repo, "put_connection") else moved.isoformat()
    sql(repo, "UPDATE active_exam_sessions SET expires_at = ? WHERE id = ?", (value, session_id))


def _submit(client, headers, exam):
    return client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": exam["session_id"],
            "course_id": COURSE,
            "course_name": "Álgebra",
            "answers": [
                {"item_id": item["id"], "selected_option": "", "time_taken": 10}
                for item in exam["items"]
            ],
            "total_time_taken": LIMIT_SECONDS,
        },
    )


@pytest.mark.parametrize("late", [5, 20])
def test_a_submission_just_after_the_limit_is_graded(repo, client, late):
    student = make_student(repo, "colegio")
    headers = headers_for(repo, student)
    exam = _start(client, headers)
    _as_if_started_ago(repo, exam["session_id"], LIMIT_SECONDS + late)

    response = _submit(client, headers, exam)

    assert response.status_code == 200, response.text
    assert response.json()["total_questions"] == len(exam["items"])


def test_a_submission_long_after_the_limit_is_refused(repo, client):
    student = make_student(repo, "colegio")
    headers = headers_for(repo, student)
    exam = _start(client, headers)
    _as_if_started_ago(repo, exam["session_id"], LIMIT_SECONDS + 120)

    response = _submit(client, headers, exam)

    assert response.status_code == 409, response.text
