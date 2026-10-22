"""Enrolling from the catalogue joins no other group — it is recorded with the student's own group
(spec 001 FR-028v, delivery TCH); a group is joined only through one of its invitations (delivery
INV). Both engines."""

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
    """A group id sent with a catalogue enrolment is not joined: the student is enrolled with
    their own group (spec 001 FR-028v, delivery TCH), stays out of the named group's ranking and
    out of its teacher's students; a student with no group is refused, whatever group they name."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, COURSE)
    member = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, member))
    own_teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (own_teacher,))
    own = make_group(repo, own_teacher)
    student = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (own, student))
    headers = headers_for(repo, student)

    response = client.post(
        "/api/student/enroll", headers=headers, json={"course_id": COURSE, "group_id": group}
    )

    assert response.status_code == 201, response.text
    assert _group_columns(repo, student) == (own, own)
    ranking = client.get("/api/student/group-ranking", headers=headers).json()
    assert member not in {s["user_id"] for s in ranking["ranking"]}
    assert student not in {s["id"] for s in repo.get_students_by_teacher(teacher)}

    alone = make_student(repo, "colegio")
    refused = client.post(
        "/api/student/enroll",
        headers=headers_for(repo, alone),
        json={"course_id": COURSE, "group_id": group},
    )
    assert refused.status_code == 403, refused.text
    assert sql(repo, "SELECT COUNT(*) FROM enrollments WHERE user_id = ?", (alone,))[0][0] == 0


def test_an_invitation_still_joins_the_group(repo, client):
    """A single-use invitation remains the way into a group."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, COURSE)
    (code,) = repo.create_group_invitations(teacher, group, 1, 30)
    student = make_student(repo, "colegio")

    response = client.post(
        "/api/student/enroll-by-code",
        headers=headers_for(repo, student),
        json={"invite_code": code},
    )

    assert response.status_code == 201, response.text
    assert _group_columns(repo, student) == (group, group)
