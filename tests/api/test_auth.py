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
