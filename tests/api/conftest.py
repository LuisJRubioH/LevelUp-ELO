"""
tests/api/conftest.py
======================
Fixtures compartidos para los tests de integración de la API FastAPI.

Estrategia:
- Se usa SQLiteRepository con un archivo temporal para evitar dependencias
  externas (PostgreSQL, Supabase).
- El cliente es session-scoped: init_db() corre una sola vez por sesión
  (sincroniza el banco de preguntas — puede tardar ~5 s).
- Los tokens de cada rol son también session-scoped para reutilizar autenticación.
"""

import os

import pytest
from starlette.testclient import TestClient

# ── Configurar env vars ANTES de importar la app ──────────────────────────────
# DATABASE_URL ausente → SQLiteRepository
os.environ.pop("DATABASE_URL", None)
os.environ["ADMIN_PASSWORD"] = "testadmin123"
os.environ["ADMIN_USER"] = "admin"


def _headers(token: str) -> dict:
    """Encabezado Authorization listo para usar en peticiones."""
    return {"Authorization": f"Bearer {token}"}


# ── Cliente TestClient (session-scoped) ───────────────────────────────────────


@pytest.fixture(scope="session")
def api_client(tmp_path_factory):
    """
    TestClient de FastAPI apuntando a un SQLite temporal.
    Corre el lifespan completo (init_db + seed + sync items bank).
    """
    db_path = str(tmp_path_factory.mktemp("api_db") / "test.db")
    os.environ["DB_PATH"] = db_path

    # Resetear el singleton del repositorio para que use el DB temporal
    import api.dependencies as deps

    deps._repo_instance = None

    from api.main import app

    # student_service.py importa ai_client.py que llama load_dotenv() al importarse,
    # lo que re-inyecta DATABASE_URL desde .env en os.environ.
    # Hay que volver a eliminarlo DESPUÉS de que todos los imports ocurran.
    os.environ.pop("DATABASE_URL", None)

    with TestClient(app) as client:
        yield client

    # Limpiar singleton al finalizar la sesión
    deps._repo_instance = None


# ── Tokens de autenticación por rol ──────────────────────────────────────────


@pytest.fixture(scope="session")
def student_token(api_client):
    """Token JWT del estudiante de demo (estudiante1 / demo1234)."""
    res = api_client.post(
        "/api/auth/login", json={"username": "estudiante1", "password": "demo1234"}
    )
    assert res.status_code == 200, f"Login estudiante falló: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def teacher_token(api_client):
    """Token JWT del docente de demo (profesor1 / demo1234, pre-aprobado)."""
    res = api_client.post("/api/auth/login", json={"username": "profesor1", "password": "demo1234"})
    assert res.status_code == 200, f"Login profesor falló: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token(api_client):
    """Token JWT del administrador (admin / testadmin123)."""
    res = api_client.post("/api/auth/login", json={"username": "admin", "password": "testadmin123"})
    assert res.status_code == 200, f"Login admin falló: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def student_headers(student_token):
    return _headers(student_token)


@pytest.fixture(scope="session")
def teacher_headers(teacher_token):
    return _headers(teacher_token)


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return _headers(admin_token)
