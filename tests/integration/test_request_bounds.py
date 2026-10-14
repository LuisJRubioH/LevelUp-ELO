"""Requests outside their bounds are refused before they reach the database. Both engines."""

from tests.integration.conftest import headers_for, make_group, make_student, make_teacher, sql


def test_an_exam_needs_a_course(repo, client):
    """An empty course id used to build a standard exam from every course's items."""
    student = make_student(repo, "colegio")

    response = client.post(
        "/api/student/exam/start",
        headers=headers_for(repo, student),
        json={"course_id": "", "n_questions": 5, "time_limit_minutes": 10},
    )

    assert response.status_code == 422, response.text


def test_the_rating_history_limit_is_bounded(repo, client):
    """A negative limit was a 500 on PostgreSQL and returned everything on SQLite."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, "algebra_basica")
    student = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    headers = headers_for(repo, teacher)

    for limit in (-1, 0, 10_000):
        response = client.get(
            f"/api/teacher/student/{student}/elo-history", headers=headers, params={"limit": limit}
        )
        assert response.status_code == 422, (limit, response.text)
    assert (
        client.get(f"/api/teacher/student/{student}/elo-history", headers=headers).status_code
        == 200
    )
