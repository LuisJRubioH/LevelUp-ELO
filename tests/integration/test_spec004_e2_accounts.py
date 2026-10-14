"""
Spec 004, delivery E2 — passwords and sessions on both engines (FR-026 … FR-033): the repository
methods behind the password change, the administrative reset and teacher creation, and the
revocation they cause through the API.

[CHANGE] tests: they fail on the base branch, which has none of these methods.
"""

import uuid

from tests.integration.conftest import make_student, make_teacher, sql


def _admin(repo) -> int:
    """An active admin of the test's own: the seeded one exists only when ADMIN_PASSWORD is set."""
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    return admin


def _state(repo, user_id):
    row = sql(
        repo,
        "SELECT password_hash, security_version, must_change_password FROM users WHERE id = ?",
        (user_id,),
    )[0]
    return tuple(row)


def test_spec004_set_user_password_advances_the_security_version(repo, student):
    """FR-028, FR-032: the new password is stored as Argon2id, the old one stops verifying, the
    version advances by one per change, and the forced change is set or cleared as asked."""
    assert repo.verify_user_password(student, "password123")
    _, before, _ = _state(repo, student)

    version = repo.set_user_password(student, "temporal-1", must_change=True)
    stored, after, must_change = _state(repo, student)

    assert version == after == before + 1
    assert stored.startswith("$argon2id$") and "temporal-1" not in stored
    assert must_change == 1
    assert repo.verify_user_password(student, "temporal-1")
    assert not repo.verify_user_password(student, "password123")

    assert repo.set_user_password(student, "propia-12") == before + 2
    assert _state(repo, student)[2] == 0
    assert repo.get_user_by_id(student)["security_version"] == before + 2
    assert repo.set_user_password(10**9, "x-123456") is None


def test_spec004_reset_is_admin_only_and_audited_without_the_password(repo, student):
    """FR-029, FR-033: only an active admin resets, only a student's or teacher's access; the
    reset forces a change, advances the version and records admin, account and time."""
    admin = _admin(repo)
    other = make_student(repo)
    before = _state(repo, student)

    refused = repo.reset_user_password(other, student, "Temporal1234")
    refused_admin_target = repo.reset_user_password(admin, admin, "Temporal1234")

    assert refused[0] is False and refused_admin_target[0] is False
    assert _state(repo, student) == before

    ok, _ = repo.reset_user_password(admin, student, "Temporal1234")

    stored, version, must_change = _state(repo, student)
    assert ok and must_change == 1 and version == before[1] + 1
    assert repo.verify_user_password(student, "Temporal1234")
    events = [e for e in repo.get_account_audit(limit=50) if e["user_id"] == student]
    assert [(e["action"], e["actor_id"]) for e in events] == [("password_reset", admin)]
    assert events[0]["created_at"] and "Temporal1234" not in str(events[0])


def test_spec004_teacher_creation_is_admin_only_approved_and_audited(repo):
    """FR-031, FR-033: an approved teacher that must change its temporary password, with who
    created it; a duplicate username or a non-admin actor creates nothing."""
    admin = _admin(repo)
    username = "e2_teacher_" + uuid.uuid4().hex[:8]

    assert repo.create_teacher_account(make_student(repo), username, "Temporal1234")[0] is False
    ok, _, teacher_id = repo.create_teacher_account(admin, username, "Temporal1234")
    duplicate = repo.create_teacher_account(admin, username, "Otra12345678")

    assert ok and duplicate[0] is False
    row = sql(
        repo,
        "SELECT role, approved, active, must_change_password, created_by FROM users"
        " WHERE username = ?",
        (username,),
    )
    assert [tuple(r) for r in row] == [("teacher", 1, 1, 1, admin)]
    assert repo.verify_user_password(teacher_id, "Temporal1234")
    events = [e for e in repo.get_account_audit(limit=50) if e["user_id"] == teacher_id]
    assert [(e["action"], e["actor_id"]) for e in events] == [("teacher_created", admin)]
    accounts = {a["id"]: a for a in repo.get_accounts_admin()}
    assert accounts[teacher_id]["role"] == "teacher"
    assert admin not in accounts


def test_spec004_a_password_change_revokes_earlier_tokens(repo, client, student):
    """FR-027, FR-028 on both engines: after the change, the earlier access token and renewal are
    refused and the returned token works."""
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (student,))[0][0]
    login = client.post("/api/auth/login", json={"username": username, "password": "password123"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    refresh = login.cookies.get("levelup_refresh")

    changed = client.post(
        "/api/auth/password",
        json={"current_password": "password123", "new_password": "nueva-123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert changed.status_code == 200, changed.text
    old = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    new = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {changed.json()['access_token']}"}
    )
    client.cookies.clear()
    renewal = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert (old.status_code, new.status_code, renewal.status_code) == (401, 200, 401)


def test_spec004_account_columns_and_audit_table_are_additive(repo):
    """R8, FR-027: the new columns default to version 0 and no forced change, so existing accounts
    and their sessions keep working after the migration; running it again changes nothing."""
    student = make_student(repo)
    assert _state(repo, student)[1:] == (0, 0)

    repo._migrate_db()

    assert _state(repo, student)[1:] == (0, 0)
    audited = sql(repo, "SELECT COUNT(*) FROM audit_account_events WHERE user_id = ?", (student,))
    assert audited[0][0] == 0
