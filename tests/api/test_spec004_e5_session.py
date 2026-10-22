"""
Spec 004, delivery E5 — session renewal without third-party cookies (US9, FR-080 … FR-085): the
renewal cookie's scope and SameSite, its deletion with the same attributes, no caching of
authentication responses, refusal of authentication requests and WebSockets from other origins,
and the same-origin proxy the frontend is prepared to use.

Through the API on SQLite. Safari on real devices (US9-AS5) is the owner's check.

[CHANGE] tests: they fail on the base branch (SameSite fixed to None, a logout that deletes the
cookie without Secure/SameSite, no Cache-Control, no origin check, no proxy).
"""

import json
import pathlib
import time
import uuid

import jwt
import pytest
from starlette.websockets import WebSocketDisconnect

from api.config import settings
from api.dependencies import get_repository

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_FOREIGN = "https://evil.example"
_HASH = {}


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()
    yield
    limiter.reset()


def _account():
    repo = get_repository()
    if "hash" not in _HASH:
        _HASH["hash"] = repo.hashing.hash_password("password123")
    name = "e5_" + uuid.uuid4().hex[:10]
    conn = repo.get_connection()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, role, approved, active, education_level)"
        " VALUES (?, ?, 'student', 1, 1, 'colegio')",
        (name, _HASH["hash"]),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id, name


def _login(client, name, headers=None):
    return client.post(
        "/api/auth/login", json={"username": name, "password": "password123"}, headers=headers
    )


def _cookie_header(response) -> str:
    cookies = [v for k, v in response.headers.multi_items() if k.lower() == "set-cookie"]
    refresh = [c for c in cookies if c.startswith("levelup_refresh=")]
    assert len(refresh) == 1, cookies
    return refresh[0]


@pytest.mark.parametrize("same_site", ["none", "lax"])
def test_spec004_renewal_cookie_is_http_only_secure_and_scoped(api_client, monkeypatch, same_site):
    """FR-081: HttpOnly, Secure, only for the authentication paths, SameSite from its setting —
    "none" for today's cross-origin flow, "lax" for the same-origin one."""
    monkeypatch.setattr(settings, "auth_cookie_samesite", same_site)
    _, name = _account()

    cookie = _cookie_header(_login(api_client, name)).lower()

    assert "httponly" in cookie and "secure" in cookie
    assert "path=/api/auth" in cookie
    assert f"samesite={same_site}" in cookie


def test_spec004_samesite_setting_accepts_only_known_values():
    """FR-081: a mistyped policy stops the start instead of producing a cookie browsers drop."""
    from api.config import Settings

    assert Settings(_env_file=None, auth_cookie_samesite=" Lax ").auth_cookie_samesite == "lax"
    with pytest.raises(ValueError):
        Settings(_env_file=None, auth_cookie_samesite="laxx")


@pytest.mark.parametrize("same_site", ["none", "lax"])
def test_spec004_logout_deletes_the_cookie_with_the_same_attributes(
    api_client, monkeypatch, same_site
):
    """US9-AS3, FR-081: the deletion carries the same Secure, HttpOnly, SameSite and path; without
    them a browser keeps a cross-site cookie."""
    monkeypatch.setattr(settings, "auth_cookie_samesite", same_site)

    cookie = _cookie_header(api_client.post("/api/auth/logout")).lower()

    assert "max-age=0" in cookie or "expires=thu, 01 jan 1970" in cookie
    assert "httponly" in cookie and "secure" in cookie
    assert "path=/api/auth" in cookie and f"samesite={same_site}" in cookie


def test_spec004_authentication_responses_are_never_cached(api_client):
    """FR-082: every authentication response, success or refusal, is marked not cacheable."""
    _, name = _account()
    ok = _login(api_client, name)
    token = ok.json()["access_token"]
    responses = {
        "login": ok,
        "login-refused": api_client.post(
            "/api/auth/login", json={"username": name, "password": "wrong"}
        ),
        "refresh-refused": api_client.post("/api/auth/refresh", json={"refresh_token": "x"}),
        "me": api_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}),
        "registration": api_client.get("/api/auth/registration"),
        "logout": api_client.post("/api/auth/logout"),
    }

    for label, response in responses.items():
        assert response.headers.get("cache-control") == "no-store", label
        assert response.headers.get("pragma") == "no-cache", label


def test_spec004_authentication_requests_from_other_origins_are_refused(api_client):
    """FR-082: a state-changing authentication request whose `Origin` is not one the API serves
    is refused before anything happens; the frontend's origin and requests without `Origin`
    (other programs) work."""
    user_id, name = _account()
    foreign = {"Origin": _FOREIGN}
    own = {"Origin": settings.cors_origins[0]}
    token = _login(api_client, name).json()["access_token"]
    bearer = {"Authorization": f"Bearer {token}"}

    refused = [
        _login(api_client, name, headers=foreign),
        api_client.post("/api/auth/refresh", json={"refresh_token": "x"}, headers=foreign),
        api_client.post("/api/auth/logout", headers=foreign),
        api_client.post(
            "/api/auth/password",
            json={"current_password": "password123", "new_password": "nueva-123"},
            headers={**bearer, **foreign},
        ),
    ]

    assert [r.status_code for r in refused] == [403] * 4
    assert get_repository().verify_user_password(user_id, "password123")
    assert _login(api_client, name, headers=own).status_code == 200
    assert _login(api_client, name).status_code == 200
    assert api_client.get("/api/auth/me", headers={**bearer, **foreign}).status_code == 200


def test_spec004_websockets_from_other_origins_are_refused(api_client):
    """FR-085 with decision N6: WebSockets keep connecting straight to the API, authenticated by
    their first message; a browser socket from another origin is refused at the handshake."""
    user_id, name = _account()
    token = _login(api_client, name).json()["access_token"]
    room = f"/api/ws/notifications/student_{user_id}"

    with pytest.raises(WebSocketDisconnect):
        with api_client.websocket_connect(room, headers={"origin": _FOREIGN}) as socket:
            socket.receive_json()
    with api_client.websocket_connect(room, headers={"origin": settings.cors_origins[0]}) as socket:
        socket.send_json({"token": token})
        assert socket.receive_json()["type"] == "connected"


def test_spec004_renewal_is_refused_at_once_for_revoked_or_inactive_accounts(api_client):
    """FR-084 (revocation and deactivation; expiry arrives with E3): a renewal issued before a
    password change, or for an account deactivated since, is refused at once."""
    revoked_id, revoked = _account()
    inactive_id, inactive = _account()
    revoked_login, inactive_login = _login(api_client, revoked), _login(api_client, inactive)

    get_repository().set_user_password(revoked_id, "otra-clave-1")
    conn = get_repository().get_connection()
    conn.execute("UPDATE users SET active = 0 WHERE id = ?", (inactive_id,))
    conn.commit()
    conn.close()

    for login in (revoked_login, inactive_login):
        renewal = api_client.post(
            "/api/auth/refresh", json={"refresh_token": login.cookies.get("levelup_refresh")}
        )
        assert renewal.status_code == 401


def test_spec004_access_token_lasts_fifteen_minutes(api_client):
    """FR-083 [AS-IS]: the access token keeps its 15 minutes."""
    _, name = _account()

    token = _login(api_client, name).json()["access_token"]
    payload = jwt.decode(token, options={"verify_signature": False})

    assert settings.access_token_expire_minutes == 15
    assert 14 * 60 <= payload["exp"] - time.time() <= 15 * 60 + 5


def test_spec004_the_frontend_can_reach_the_api_through_its_own_origin():
    """FR-080: the frontend's host forwards /api/* to the API before the single-page fallback,
    the HTTP client uses the page's own origin when VITE_API_URL is empty, and WebSockets keep
    their own base (VITE_WS_URL), since the proxy carries HTTP only (N6)."""
    config = json.loads((_ROOT / "frontend" / "vercel.json").read_text(encoding="utf-8"))
    rewrites = config["rewrites"]
    api_rule = next(i for i, r in enumerate(rewrites) if r["source"] == "/api/:path*")
    spa_rule = next(i for i, r in enumerate(rewrites) if r["destination"] == "/index.html")
    client = (_ROOT / "frontend" / "src" / "api" / "client.ts").read_text(encoding="utf-8")
    ws_base = (_ROOT / "frontend" / "src" / "api" / "wsBase.ts").read_text(encoding="utf-8")

    assert api_rule < spa_rule
    assert rewrites[api_rule]["destination"].startswith("https://")
    assert rewrites[api_rule]["destination"].endswith("/api/:path*")
    assert 'import.meta.env.VITE_API_URL ?? ""' in client
    assert "VITE_WS_URL" in ws_base
