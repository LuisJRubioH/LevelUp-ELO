"""The admin's groups page, on both engines.

`GET /api/admin/groups` carried only id, name and teacher_name, while the page read
`teacher_username`, `teacher_id` and `student_count`: the teacher column showed «ID undefined» and
the count «—». `DELETE /api/admin/groups/{id}` answered 204 even when the repository refused.
"""

from tests.integration.conftest import (
    headers_for,
    make_student,
    make_teacher,
    make_group,
    sql,
)


def _admin(repo) -> int:
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    return admin


def _join(repo, student_id, group_id) -> None:
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group_id, student_id))


def test_admin_groups_list_names_the_teacher_and_counts_the_students(repo, client):
    """Each group carries its teacher's id and name and the count the teacher's own page shows:
    active students whose group it is, test accounts left out."""
    teacher = make_teacher(repo)
    group = make_group(repo, teacher)
    for _ in range(2):
        _join(repo, make_student(repo), group)
    inactive = make_student(repo)
    _join(repo, inactive, group)
    sql(repo, "UPDATE users SET active = 0 WHERE id = ?", (inactive,))
    test_user = make_student(repo)
    _join(repo, test_user, group)
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (test_user,))

    r = client.get("/api/admin/groups", headers=headers_for(repo, _admin(repo)))

    assert r.status_code == 200
    row = next(g for g in r.json()["groups"] if g["id"] == group)
    teacher_name = sql(repo, "SELECT username FROM users WHERE id = ?", (teacher,))[0][0]
    assert row["teacher_id"] == teacher
    assert row["teacher_name"] == teacher_name
    assert row["student_count"] == 2
    own_page = next(g for g in repo.get_groups_by_teacher(teacher) if g["id"] == group)
    assert row["student_count"] == own_page["student_count"]


def test_deleting_an_unknown_group_is_refused(repo, client):
    """The repository's refusal reaches the admin instead of a 204."""
    r = client.delete("/api/admin/groups/987654321", headers=headers_for(repo, _admin(repo)))

    assert r.status_code == 404
    assert r.json()["detail"] == "El grupo no existe."


def test_deleting_a_group_unlinks_its_students(repo, client):
    teacher = make_teacher(repo)
    group = make_group(repo, teacher)
    student = make_student(repo)
    _join(repo, student, group)

    r = client.delete(f"/api/admin/groups/{group}", headers=headers_for(repo, _admin(repo)))

    assert r.status_code == 204
    assert sql(repo, "SELECT id FROM groups WHERE id = ?", (group,)) == []
    assert sql(repo, "SELECT group_id FROM users WHERE id = ?", (student,))[0][0] is None


def test_a_database_error_while_deleting_stays_out_of_the_response(repo, client, monkeypatch):
    monkeypatch.setattr(
        type(repo),
        "delete_group",
        lambda self, group_id, admin_id: (False, "Error al eliminar grupo: secret detail"),
    )

    r = client.delete("/api/admin/groups/1", headers=headers_for(repo, _admin(repo)))

    assert r.status_code == 500
    assert "secret detail" not in r.text
