"""A teacher opens the students their dashboard lists: those whose main group is theirs and those
enrolled through one of their groups. Both engines."""

from tests.integration.conftest import headers_for, make_student, make_teacher, sql

COURSE_A = "algebra_basica"
COURSE_B = "geometria"


def _teacher_with_code(repo, client, course_id):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    headers = headers_for(repo, teacher)
    created = client.post(
        "/api/teacher/groups",
        headers=headers,
        json={"course_id": course_id, "group_name": f"Grupo {teacher}"},
    )
    assert created.status_code == 201, created.text
    group = created.json()["group_id"]
    code = client.post(f"/api/teacher/groups/{group}/invite-code", headers=headers)
    return headers, group, code.json()["invite_code"]


def test_a_student_who_joined_a_second_group_stays_open_to_the_first_teacher(repo, client):
    first, first_group, first_code = _teacher_with_code(repo, client, COURSE_A)
    second, _, second_code = _teacher_with_code(repo, client, COURSE_B)
    stranger, _, _ = _teacher_with_code(repo, client, COURSE_A)
    student = make_student(repo, "colegio")
    for code in (first_code, second_code):
        joined = client.post(
            "/api/student/enroll-by-code",
            headers=headers_for(repo, student),
            json={"invite_code": code},
        )
        assert joined.status_code == 201, joined.text

    listed = client.get("/api/teacher/dashboard", headers=first).json()["students"]
    assert student in {s["user_id"] for s in listed}
    for path in ("", "/elo-history", "/katia-history"):
        assert client.get(f"/api/teacher/student/{student}{path}", headers=first).status_code == 200
        assert (
            client.get(f"/api/teacher/student/{student}{path}", headers=second).status_code == 200
        )
        assert (
            client.get(f"/api/teacher/student/{student}{path}", headers=stranger).status_code == 404
        )

    # The ranking shown is the first teacher's group, on its course. Who takes part in a group
    # ranking (the main group only, today) is left as it is.
    ranking = client.get(f"/api/teacher/student/{student}/ranking", headers=first)
    assert ranking.status_code == 200
    assert ranking.json()["basis"]["course_id"] == COURSE_A
