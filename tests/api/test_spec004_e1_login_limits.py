"""
Spec 004, delivery E1 (US1-AS4, US2, FR-003 … FR-011): login limits per account and global, no
per-address login limit, public registration's own per-address limit, and the registration state
the login screen reads. The counters live in the limiter's store (memory in tests), so these run
through the API on one engine; the account lookup they use is pinned on both engines in
tests/integration/test_spec004_e1_registration.py.

[CHANGE] tests: written before the code they test.
"""

import logging
import uuid

import pytest

from api.dependencies import get_repository

_HASH_CACHE = {}


def _login(client, username, password="password123"):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def _students(n, email=False):
    """n active students sharing one password hash (hashing 30 passwords would take seconds)."""
    repo = get_repository()
    if "hash" not in _HASH_CACHE:
        _HASH_CACHE["hash"] = repo.hashing.hash_password("password123")
    names = []
    conn = repo.get_connection()
    cursor = conn.cursor()
    for _ in range(n):
        name = "e1_" + uuid.uuid4().hex[:12]
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, approved, active, education_level,"
            " email) VALUES (?, ?, 'student', 1, 1, 'colegio', ?)",
            (name, _HASH_CACHE["hash"], f"{name}@example.test" if email else None),
        )
        names.append(name)
    conn.commit()
    conn.close()
    return names


def test_spec004_thirty_students_on_one_address_sign_in(api_client):
    """US2-AS1, FR-008: 30 students from the same address within one minute, default limits —
    none refused for sharing the network."""
    responses = [_login(api_client, name) for name in _students(30)]
    assert [r.status_code for r in responses] == [200] * 30


def test_spec004_the_eleventh_attempt_on_one_account_is_refused(api_client):
    """US2-AS2, FR-006: the 11th attempt in a minute — right password or not, by username or by
    email — is refused even with the right password; another account still signs in."""
    name, other = _students(2, email=True)
    attempts = [_login(api_client, name, "wrong") for _ in range(5)]
    attempts += [_login(api_client, f"{name}@example.test", "wrong") for _ in range(5)]
    assert [r.status_code for r in attempts] == [401] * 10

    eleventh = _login(api_client, name)

    assert eleventh.status_code == 429
    assert _login(api_client, other).status_code == 200


def test_spec004_a_refusal_does_not_reveal_whether_the_account_exists(api_client):
    """US2-AS4, FR-010: the limit refuses an unknown identifier exactly as an existing account."""
    (name,) = _students(1)
    missing = "e1_missing_" + uuid.uuid4().hex[:8]
    for who in (name, missing):
        for _ in range(10):
            _login(api_client, who, "wrong")
    known, unknown = _login(api_client, name, "wrong"), _login(api_client, missing, "wrong")

    assert known.status_code == unknown.status_code == 429
    assert known.json() == unknown.json()
    assert known.headers.get("retry-after") == unknown.headers.get("retry-after")


def test_spec004_the_global_ceiling_refuses_every_extra_attempt(api_client, monkeypatch):
    """US2-AS3, FR-007, FR-009: above the global limit any sign-in is refused, a valid one too.
    The limit comes from its setting (5 here instead of 300)."""
    from api.config import settings

    monkeypatch.setattr(settings, "rate_limit_login_global", "5/minute")
    (name,) = _students(1)
    for _ in range(5):
        assert _login(api_client, "e1_missing_" + uuid.uuid4().hex, "x").status_code == 401

    assert _login(api_client, name).status_code == 429


def test_spec004_login_limits_follow_their_settings(api_client, monkeypatch):
    """US2-AS5, FR-009: defaults 10 per account and 300 overall per minute; another value for
    the account limit takes effect."""
    from api.config import Settings, settings

    defaults = Settings()
    assert defaults.rate_limit_login_account == "10/minute"
    assert defaults.rate_limit_login_global == "300/minute"
    monkeypatch.setattr(settings, "rate_limit_login_account", "2/minute")
    (name,) = _students(1)

    statuses = [_login(api_client, name).status_code for _ in range(3)]

    assert statuses == [200, 200, 429]


def test_spec004_limits_keep_no_readable_identifier(api_client, caplog):
    """FR-011: neither the counters' keys nor the logs hold the identifier typed."""
    from api.rate_limit import limiter

    secret = "e1_identifier_" + uuid.uuid4().hex[:8]
    with caplog.at_level(logging.DEBUG):
        for _ in range(12):
            _login(api_client, secret, "wrong")
    keys = " ".join(str(k) for k in limiter._storage.storage.keys())

    assert secret not in keys and secret.casefold() not in keys
    assert secret not in caplog.text


def test_spec004_registration_state_is_public(api_client, monkeypatch):
    """FR-003 (API side): the login screen reads whether public registration is open."""
    from api.config import settings

    assert api_client.get("/api/auth/registration").json() == {"enabled": False}
    monkeypatch.setattr(settings, "public_registration_enabled", True)
    assert api_client.get("/api/auth/registration").json() == {"enabled": True}


def test_spec004_registration_has_its_own_per_address_limit(api_client, monkeypatch):
    """US1-AS4, FR-004: with registration open, one address is limited (3 here); login is not
    affected by it."""
    from api.config import settings

    monkeypatch.setattr(settings, "public_registration_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_register", "3/minute")
    statuses = [
        api_client.post(
            "/api/auth/register",
            json={
                "username": "e1_" + uuid.uuid4().hex[:10],
                "password": "password123",
                "display_name": "Ana Ruiz",
            },
        ).status_code
        for _ in range(4)
    ]
    (name,) = _students(1)

    assert statuses == [201, 201, 201, 429]
    assert _login(api_client, name).status_code == 200


@pytest.fixture(autouse=True)
def _fresh_counters():
    from api.rate_limit import limiter

    limiter.reset()
    yield
    limiter.reset()
