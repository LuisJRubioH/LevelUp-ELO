"""The admin user list carries each student's role and education level, on both engines.

The admin table has «Rol» and «Nivel» columns; the repositories did not select either, so both
were empty for every row.
"""

from tests.integration.conftest import make_student


def test_admin_user_list_carries_role_and_education_level(repo):
    student_id = make_student(repo, education_level="universidad")

    row = next(r for r in repo.get_all_students_admin() if r["id"] == student_id)

    assert row["role"] == "student"
    assert row["education_level"] == "universidad"
    assert {"username", "active", "created_at", "group_name"} <= set(row)
