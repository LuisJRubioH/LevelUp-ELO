"""Enrolling from the catalogue joins no group; a group is joined only through its invitation
code. Both engines."""

from tests.integration.conftest import headers_for, make_group, make_student, make_teacher, sql

COURSE = "algebra_basica"


def _group_columns(repo, student):
    user_group = sql(repo, "SELECT group_id FROM users WHERE id = ?", (student,))[0][0]
    enrolment_group = sql(
        repo,
        "SELECT group_id FROM enrollments WHERE user_id = ? AND course_id = ?",
        (student, COURSE),
    )[0][0]
    return user_group, enrolment_group


def test_catalogue_enrolment_ignores_a_group_id(repo, client):
    """A group id sent with a catalogue enrolment is not joined: the student is enrolled in the
    course, stays out of that group's ranking and out of its teacher's students."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, COURSE)
    member = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, member))
    student = make_student(repo, "colegio")
    headers = headers_for(repo, student)

    response = client.post(
        "/api/student/enroll", headers=headers, json={"course_id": COURSE, "group_id": group}
    )

    assert response.status_code == 201, response.text
    assert _group_columns(repo, student) == (None, None)
    ranking = client.get("/api/student/group-ranking", headers=headers).json()
    assert ranking["ranking"] == []
    assert student not in {s["id"] for s in repo.get_students_by_teacher(teacher)}


def test_invitation_code_still_joins_the_group(repo, client):
    """The invitation code remains the way into a group."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, COURSE)
    code = repo.generate_group_invite_code(group)
    student = make_student(repo, "colegio")

    response = client.post(
        "/api/student/enroll-by-code",
        headers=headers_for(repo, student),
        json={"invite_code": code},
    )

    assert response.status_code == 201, response.text
    assert _group_columns(repo, student) == (group, group)
