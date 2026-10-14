"""
Spec 004, delivery E2 — passwords and sessions (US4, US5; FR-026 … FR-033): a user changes their
password and every other session ends; the security version revokes access tokens, renewals and
open WebSockets; the admin resets access with a temporary password that must be changed first, and
creates approved teachers the same way; both operations are audited without the password.

Through the API on SQLite; the repository side is pinned on both engines in
tests/integration/test_spec004_e2_accounts.py.

[CHANGE] tests: they fail on the base branch, which has no password change, reset, teacher
creation or security version.
"""

import logging
import uuid

import pytest
from starlette.websockets import WebSocketDisconnect

from api.dependencies import PASSWORD_CHANGE_REQUIRED, SESSION_REVOKED, get_repository

_HASH = {}


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()
    yield
    limiter.reset()


def _account(role="student", password="password123"):
    """A new active account with `password` (hash cached: Argon2 is slow on purpose)."""
    repo = get_repository()
    if password not in _HASH:
        _HASH[password] = repo.hashing.hash_password(password)
    name = f"e2_{role[0]}_" + uuid.uuid4().hex[:10]
    conn = repo.get_connection()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, role, approved, active, education_level)"
        " VALUES (?, ?, ?, 1, 1, 'colegio')",
        (name, _HASH[password], role),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id, name


def _row(user_id, columns="password_hash, security_version, must_change_password"):
    conn = get_repository().get_connection()
    try:
        return conn.execute(f"SELECT {columns} FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()


def _login(client, username, password="password123"):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _change(client, token, current, new):
    return client.post(
        "/api/auth/password",
        json={"current_password": current, "new_password": new},
        headers=_auth(token),
    )


def _refresh(client, login_response):
    """Renew with the refresh token the login set (sent in the body: the test client is http)."""
    return client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_response.cookies.get("levelup_refresh")},
    )


# ── US4: the user changes their password ─────────────────────────────────────


def test_spec004_password_change_replaces_it_and_keeps_this_session(api_client):
    """US4-AS1, FR-026, FR-028: with the current password and a valid new one, the new one signs
    in, the old one does not, and the session that changed it continues with new credentials."""
    user_id, name = _account()
    session = _login(api_client, name)

    changed = _change(api_client, session.json()["access_token"], "password123", "nueva-clave-1")

    assert changed.status_code == 200, changed.text
    new_token = changed.json()["access_token"]
    assert api_client.get("/api/auth/me", headers=_auth(new_token)).status_code == 200
    assert api_client.get("/api/student/stats", headers=_auth(new_token)).status_code == 200
    assert _login(api_client, name, "password123").status_code == 401
    assert _login(api_client, name, "nueva-clave-1").status_code == 200
    assert _row(user_id)[1] == 1  # security version advanced once


def test_spec004_other_sessions_end_on_password_change(api_client):
    """US4-AS2, FR-027, FR-028: another session's access token, renewal and open WebSocket stop
    working at once; the token the change returned keeps working."""
    user_id, name = _account()
    session_a = _login(api_client, name)
    session_b = _login(api_client, name)
    token_b = session_b.json()["access_token"]

    with api_client.websocket_connect(f"/api/ws/notifications/student_{user_id}") as socket:
        socket.send_json({"token": token_b})
        assert socket.receive_json()["type"] == "connected"

        changed = _change(api_client, session_a.json()["access_token"], "password123", "otra-12")
        assert changed.status_code == 200, changed.text

        with pytest.raises(WebSocketDisconnect) as closed:
            socket.receive_json()
    assert closed.value.code == 4401

    refused = api_client.get("/api/auth/me", headers=_auth(token_b))
    assert refused.status_code == 401
    assert refused.json()["detail"] == SESSION_REVOKED
    assert _refresh(api_client, session_b).status_code == 401
    assert (
        api_client.get("/api/auth/me", headers=_auth(session_a.json()["access_token"])).status_code
        == 401
    )
    assert (
        api_client.get("/api/auth/me", headers=_auth(changed.json()["access_token"])).status_code
        == 200
    )


@pytest.mark.parametrize(
    "current, new",
    [("incorrecta", "valida-123"), ("password123", "  abc  "), ("password123", "")],
    ids=["wrong-current", "short-new", "empty-new"],
)
def test_spec004_a_refused_change_changes_nothing(api_client, current, new):
    """US4-AS3, FR-026: a wrong current password, or a new one shorter than 6 characters after
    trimming, is refused; the password, the version and the session stay as they were. The
    refusal never echoes the passwords."""
    user_id, name = _account()
    session = _login(api_client, name)
    token = session.json()["access_token"]
    before = _row(user_id)

    refused = _change(api_client, token, current, new)

    assert refused.status_code == 400
    assert current not in refused.text and (not new.strip() or new.strip() not in refused.text)
    assert _row(user_id) == before
    assert api_client.get("/api/auth/me", headers=_auth(token)).status_code == 200
    assert _login(api_client, name).status_code == 200


def test_spec004_password_change_attempts_count_against_the_account_limit(api_client):
    """FR-026 with FR-006: guessing the current password through a stolen session is limited
    like the login screen — 10 attempts per account and minute."""
    _, name = _account()
    token = _login(api_client, name).json()["access_token"]  # 1st attempt on the account

    statuses = [
        _change(api_client, token, f"guess-{i}", "nueva-123").status_code for i in range(10)
    ]

    assert statuses == [400] * 9 + [429]


def test_spec004_tokens_from_before_the_security_version_still_work(api_client):
    """FR-027: tokens issued before E2 carry no version and count as version 0, so existing
    sessions survive the deployment; they stop once the version advances."""
    import jwt

    from api.config import settings

    user_id, name = _account()
    legacy = jwt.encode(
        {"sub": str(user_id), "username": name, "role": "student", "type": "access"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    assert api_client.get("/api/auth/me", headers=_auth(legacy)).status_code == 200

    get_repository().set_user_password(user_id, "nueva-clave-9")

    assert api_client.get("/api/auth/me", headers=_auth(legacy)).status_code == 401


# ── US5: the admin resets access and creates teachers ────────────────────────


@pytest.mark.parametrize("role", ["student", "teacher"])
def test_spec004_admin_reset_gives_a_temporary_password_that_must_be_changed(
    api_client, admin_headers, role
):
    """US5-AS1, FR-029, FR-030: a random temporary password; every earlier session ends; at the
    next sign-in only the password change (and the profile) is allowed until it is changed."""
    user_id, name = _account(role)
    earlier = _login(api_client, name)

    reset = api_client.post(f"/api/admin/users/{user_id}/reset-password", headers=admin_headers)

    assert reset.status_code == 200, reset.text
    temporary = reset.json()["temporary_password"]
    assert len(temporary) >= 12 and temporary != "password123"
    assert (
        api_client.get("/api/auth/me", headers=_auth(earlier.json()["access_token"])).status_code
        == 401
    )
    assert _refresh(api_client, earlier).status_code == 401
    assert _login(api_client, name, "password123").status_code == 401

    signed_in = _login(api_client, name, temporary)
    assert signed_in.status_code == 200
    assert signed_in.json()["must_change_password"] is True
    token = signed_in.json()["access_token"]
    elsewhere = "/api/student/stats" if role == "student" else "/api/teacher/dashboard"
    blocked = api_client.get(elsewhere, headers=_auth(token))
    assert blocked.status_code == 403
    assert blocked.json()["detail"] == PASSWORD_CHANGE_REQUIRED
    me = api_client.get("/api/auth/me", headers=_auth(token))
    assert me.status_code == 200 and me.json()["must_change_password"] is True
    with api_client.websocket_connect(f"/api/ws/notifications/{role}_{user_id}") as socket:
        socket.send_json({"token": token})
        with pytest.raises(WebSocketDisconnect):
            socket.receive_json()

    changed = _change(api_client, token, temporary, "propia-123")
    assert changed.status_code == 200, changed.text
    assert changed.json()["must_change_password"] is False
    assert (
        api_client.get(elsewhere, headers=_auth(changed.json()["access_token"])).status_code == 200
    )


def test_spec004_admin_creates_an_approved_teacher_with_a_temporary_password(
    api_client, admin_headers
):
    """US5-AS2, FR-031: the teacher is approved, gets a random temporary password, must change it
    at first access, and the account records who created it."""
    username = "e2_docente_" + uuid.uuid4().hex[:8]

    created = api_client.post(
        "/api/admin/teachers", json={"username": username}, headers=admin_headers
    )

    assert created.status_code == 201, created.text
    body = created.json()
    teacher_id, temporary = body["user_id"], body["temporary_password"]
    approved, must_change, created_by, role = _row(
        teacher_id, "approved, must_change_password, created_by, role"
    )
    admin_id = api_client.get("/api/auth/me", headers=admin_headers).json()["user_id"]
    assert (role, approved, must_change, created_by) == ("teacher", 1, 1, admin_id)

    signed_in = _login(api_client, username, temporary)
    assert signed_in.status_code == 200 and signed_in.json()["must_change_password"] is True
    token = signed_in.json()["access_token"]
    assert api_client.get("/api/teacher/dashboard", headers=_auth(token)).status_code == 403
    changed = _change(api_client, token, temporary, "docente-123")
    assert changed.status_code == 200
    assert (
        api_client.get(
            "/api/teacher/dashboard", headers=_auth(changed.json()["access_token"])
        ).status_code
        == 200
    )


def test_spec004_a_teacher_username_already_taken_is_refused(api_client, admin_headers):
    """FR-031: creating a teacher never overwrites an existing account."""
    _, name = _account("student")

    refused = api_client.post("/api/admin/teachers", json={"username": name}, headers=admin_headers)

    assert refused.status_code == 400
    assert _login(api_client, name).status_code == 200


def test_spec004_account_audit_names_admin_account_and_time_never_the_password(
    api_client, admin_headers, caplog
):
    """US5-AS3, FR-029, FR-031, FR-032: the audit names the admin, the account and the time;
    neither it, the database nor the logs hold a temporary password, and every stored password
    is an Argon2id hash."""
    user_id, _ = _account()
    with caplog.at_level(logging.DEBUG):
        reset = api_client.post(f"/api/admin/users/{user_id}/reset-password", headers=admin_headers)
        created = api_client.post(
            "/api/admin/teachers",
            json={"username": "e2_audit_" + uuid.uuid4().hex[:8]},
            headers=admin_headers,
        )
    temporaries = [reset.json()["temporary_password"], created.json()["temporary_password"]]
    teacher_id = created.json()["user_id"]

    audit = api_client.get("/api/admin/account-audit", headers=admin_headers)

    assert audit.status_code == 200
    events = {(e["action"], e["user_id"]): e for e in audit.json()["events"]}
    for key in (("password_reset", user_id), ("teacher_created", teacher_id)):
        event = events[key]
        assert event["admin_username"] == "admin"
        assert event["created_at"]
    for temporary in temporaries:
        assert temporary not in audit.text
        assert temporary not in caplog.text
    for account in (user_id, teacher_id):
        assert _row(account, "password_hash")[0].startswith("$argon2id$")
    conn = get_repository().get_connection()
    try:
        stored = " ".join(str(r) for r in conn.execute("SELECT * FROM audit_account_events"))
    finally:
        conn.close()
    assert not any(temporary in stored for temporary in temporaries)


@pytest.mark.parametrize("who", ["student_headers", "teacher_headers"])
def test_spec004_only_the_admin_resets_access_or_creates_teachers(api_client, request, who):
    """US5-AS4, FR-033: a student or a teacher is refused and nothing changes."""
    headers = request.getfixturevalue(who)
    user_id, name = _account()
    before = _row(user_id)
    username = "e2_nope_" + uuid.uuid4().hex[:8]

    reset = api_client.post(f"/api/admin/users/{user_id}/reset-password", headers=headers)
    create = api_client.post("/api/admin/teachers", json={"username": username}, headers=headers)
    audit = api_client.get("/api/admin/account-audit", headers=headers)

    assert (reset.status_code, create.status_code, audit.status_code) == (403, 403, 403)
    assert _row(user_id) == before
    assert _login(api_client, username, "x").status_code == 401
    assert _login(api_client, name).status_code == 200
