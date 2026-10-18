"""
Spec 004, delivery E1 (US1, FR-001 … FR-002): public registration is closed by default, refused on
the server, and opens only through its setting — on both engines. Also the account lookup the login
limit uses (FR-006): exact username or email of an active account, nothing else.

[CHANGE] tests: written before the code they test.
"""

import uuid

import pytest

from tests.integration.conftest import sql


def _body(role="student"):
    return {
        "username": "e1_" + uuid.uuid4().hex[:10],
        "password": "password123",
        "role": role,
        "education_level": "colegio",
        "display_name": "Ana Ruiz",  # spec 004 FR-020: students register with a name
    }


def _count(repo, username):
    return sql(repo, "SELECT COUNT(*) FROM users WHERE username = ?", (username,))[0][0]


def test_spec004_public_registration_is_closed_by_default(repo, client):
    """US1-AS1, FR-001: with the default setting a valid sign-up is refused and creates nothing."""
    from api.config import Settings, settings

    assert Settings().public_registration_enabled is False
    assert settings.public_registration_enabled is False
    body = _body()

    response = client.post("/api/auth/register", json=body)

    assert response.status_code == 403, response.text
    assert _count(repo, body["username"]) == 0


@pytest.mark.parametrize("role, approved", [("student", 1), ("teacher", 0)])
def test_spec004_registration_opens_only_through_its_setting(
    repo, client, monkeypatch, role, approved
):
    """US1-AS3, FR-002: enabled by its setting, sign-up works as before — a teacher waits for
    approval."""
    from api.config import settings

    monkeypatch.setattr(settings, "public_registration_enabled", True)
    body = _body(role)

    response = client.post("/api/auth/register", json=body)

    assert response.status_code == 201, response.text
    rows = sql(repo, "SELECT role, approved FROM users WHERE username = ?", (body["username"],))
    assert [tuple(r) for r in rows] == [(role, approved)]


def test_spec004_login_account_id_names_one_active_account(repo):
    """FR-006: username and email of one account name the same id; anything else names none."""
    username = "e1_" + uuid.uuid4().hex[:10]
    email = username + "@example.test"
    ok, _ = repo.register_user(username, "password123", role="student", email=email)
    assert ok
    account = repo.login_account_id(username)

    assert isinstance(account, int)
    assert repo.login_account_id(email) == account
    assert repo.login_account_id(username.upper()) is None
    assert repo.login_account_id(" " + username) is None
    assert repo.login_account_id("e1_missing_" + uuid.uuid4().hex) is None
    sql(repo, "UPDATE users SET active = 0 WHERE id = ?", (account,))
    assert repo.login_account_id(username) is None
