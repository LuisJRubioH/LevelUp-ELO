"""
tests/api/test_auth.py
=======================
Tests de autenticación:
  POST /api/login       → JWT tokens
  POST /api/register    → registro de usuario
  POST /api/refresh     → renovación de token
  GET  /api/me          → perfil del usuario autenticado
  POST /api/logout      → cierre de sesión
"""


class TestLogin:
    def test_login_valid_student(self, api_client):
        """Login con credenciales correctas → 200 + access_token."""
        r = api_client.post(
            "/api/auth/login", json={"username": "estudiante1", "password": "demo1234"}
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        # refresh_token va en HttpOnly cookie, no en el body JSON
        assert data["role"] == "student"
        cookie = next(c for c in api_client.cookies.jar if c.name == "levelup_refresh")
        assert cookie.path == "/api/auth"
        assert cookie.secure is True

    def test_login_valid_teacher(self, api_client):
        """Login del docente pre-aprobado."""
        r = api_client.post(
            "/api/auth/login", json={"username": "profesor1", "password": "demo1234"}
        )
        assert r.status_code == 200
        data = r.json()
        assert data["role"] == "teacher"

    def test_login_valid_admin(self, api_client):
        """Login del administrador (seeded si ADMIN_PASSWORD está en env)."""
        r = api_client.post(
            "/api/auth/login", json={"username": "admin", "password": "testadmin123"}
        )
        assert r.status_code == 200
        data = r.json()
        assert data["role"] == "admin"

    def test_login_wrong_password(self, api_client):
        """Login con contraseña incorrecta → 401."""
        r = api_client.post(
            "/api/auth/login", json={"username": "estudiante1", "password": "incorrecto"}
        )
        assert r.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        """Login con usuario inexistente → 401."""
        r = api_client.post(
            "/api/auth/login", json={"username": "no_existe_xyz", "password": "demo1234"}
        )
        assert r.status_code == 401

    def test_login_missing_fields(self, api_client):
        """Login sin campos requeridos → 422 (Pydantic validation)."""
        r = api_client.post("/api/auth/login", json={"username": "estudiante1"})
        assert r.status_code == 422


class TestRegister:
    def test_register_student(self, api_client):
        """Registro de un estudiante nuevo → 201."""
        r = api_client.post(
            "/api/auth/register",
            json={
                "username": "nuevo_estudiante_api_test",
                "password": "password123",
                "role": "student",
                "education_level": "colegio",
            },
        )
        assert r.status_code == 201

    def test_register_teacher(self, api_client):
        """Registro de un docente → 201 (queda pendiente de aprobación)."""
        r = api_client.post(
            "/api/auth/register",
            json={
                "username": "nuevo_docente_api_test",
                "password": "password123",
                "role": "teacher",
            },
        )
        assert r.status_code == 201

    def test_register_duplicate_username(self, api_client):
        """Registro con nombre de usuario ya existente → 409."""
        r = api_client.post(
            "/api/auth/register",
            json={
                "username": "estudiante1",
                "password": "password123",
                "role": "student",
                "education_level": "colegio",
            },
        )
        assert r.status_code == 400

    def test_register_short_password(self, api_client):
        """Contraseña demasiado corta → 422 (Pydantic)."""
        r = api_client.post(
            "/api/auth/register",
            json={"username": "usuario_pw_corta", "password": "ab", "role": "student"},
        )
        assert r.status_code == 422


class TestMe:
    def test_me_authenticated(self, api_client, student_headers):
        """GET /api/me con token válido → 200 con perfil del usuario."""
        r = api_client.get("/api/auth/me", headers=student_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "estudiante1"
        assert data["role"] == "student"
        assert "user_id" in data

    def test_me_without_token(self, api_client):
        """GET /api/me sin token → 401."""
        r = api_client.get("/api/auth/me")
        assert r.status_code == 401

    def test_me_with_invalid_token(self, api_client):
        """GET /api/me con token malformado → 401."""
        r = api_client.get("/api/auth/me", headers={"Authorization": "Bearer token_invalido"})
        assert r.status_code == 401


class TestLogout:
    def test_logout(self, api_client, student_headers):
        """POST /api/logout → 204 No Content."""
        r = api_client.post("/api/auth/logout", headers=student_headers)
        assert r.status_code == 204


class TestRefreshAndRevocation:
    def test_refresh_uses_http_only_cookie_without_json_body(self, api_client):
        login = api_client.post(
            "/api/auth/login", json={"username": "estudiante1", "password": "demo1234"}
        )
        assert login.status_code == 200
        previous = api_client.cookies.get("levelup_refresh")
        refreshed = api_client.post("https://testserver/api/auth/refresh")
        assert refreshed.status_code == 200
        assert refreshed.json()["access_token"]
        assert api_client.cookies.get("levelup_refresh")
        assert api_client.cookies.get("levelup_refresh") != previous

    def test_refresh_without_cookie_or_body_is_rejected(self, api_client):
        api_client.cookies.delete("levelup_refresh")
        assert api_client.post("https://testserver/api/auth/refresh").status_code == 401

    def test_disabled_user_loses_access_and_cannot_refresh(self, api_client):
        from api.dependencies import get_repository

        username = "revoked_session_test"
        api_client.post(
            "/api/auth/register",
            json={"username": username, "password": "password123", "role": "student"},
        )
        login = api_client.post(
            "/api/auth/login", json={"username": username, "password": "password123"}
        )
        assert login.status_code == 200
        headers = {"Authorization": "Bearer " + login.json()["access_token"]}
        repo = get_repository()
        conn = repo.get_connection()
        try:
            conn.execute("UPDATE users SET active=0 WHERE id=?", (login.json()["user_id"],))
            conn.commit()
        finally:
            conn.close()
        assert api_client.get("/api/student/courses", headers=headers).status_code == 401
        assert api_client.post("https://testserver/api/auth/refresh").status_code == 401
