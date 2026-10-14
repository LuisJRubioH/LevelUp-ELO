"""Edges found by the spec 004 survey (docs/sdd/identity-survey.md I1, I4, I10). Both engines."""

import uuid

from tests.integration.conftest import (
    headers_for,
    make_group,
    make_student,
    make_teacher,
    sql,
)


def _admin(repo):
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1 WHERE id = ?", (admin,))
    return admin


def test_login_with_an_email_as_long_as_registration_accepts(repo, client):
    """I1: registration accepts emails up to 254 characters; login accepts the same."""
    email = f"{uuid.uuid4().hex}{'a' * 40}@example.com"
    username = f"edge_{uuid.uuid4().hex[:8]}"
    registered = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "secret12",
            "education_level": "colegio",
            "email": email,
        },
    )
    assert registered.status_code == 201, registered.text
    assert len(email) > 50

    response = client.post("/api/auth/login", json={"username": email, "password": "secret12"})

    assert response.status_code == 200, response.text
    assert response.json()["username"] == username


def test_moving_a_student_to_a_missing_group_is_refused(repo, client):
    """I4: the repository's refusal reaches the admin as 400, and nothing is audited."""
    admin = _admin(repo)
    student = make_student(repo, "colegio")
    before = sql(repo, "SELECT COUNT(*) FROM audit_group_changes")[0][0]

    response = client.patch(
        "/api/admin/students/group",
        headers=headers_for(repo, admin),
        json={"student_id": student, "new_group_id": 987654321},
    )

    assert response.status_code == 400, response.text
    assert "no existe" in response.json()["detail"]
    assert sql(repo, "SELECT COUNT(*) FROM audit_group_changes")[0][0] == before


def test_a_group_move_is_listed_in_the_audit(repo, client):
    """I10: the audit lists a move on both engines (SQLite answered 500 once a row existed)."""
    admin = _admin(repo)
    teacher = make_teacher(repo)
    group = make_group(repo, teacher, "algebra_basica")
    student = make_student(repo, "colegio")
    headers = headers_for(repo, admin)

    moved = client.patch(
        "/api/admin/students/group",
        headers=headers,
        json={"student_id": student, "new_group_id": group},
    )
    assert moved.status_code == 204, moved.text

    response = client.get("/api/admin/audit", headers=headers)

    assert response.status_code == 200, response.text
    entry = next(e for e in response.json()["entries"] if e["student_id"] == student)
    assert entry["new_group_id"] == group
    assert entry["admin_id"] == admin
    assert entry["old_group_id"] is None
