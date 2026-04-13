"""
tests/api/test_health.py
=========================
Tests del health check de la API.
No requiere autenticación.
"""


class TestHealthEndpoints:
    def test_root_returns_ok(self, api_client):
        """GET / → 200 con status=ok."""
        r = api_client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_api_health_returns_ok(self, api_client):
        """GET /api/health → 200 con DB conectada."""
        r = api_client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["db"] == "ok"

    def test_docs_accessible(self, api_client):
        """GET /api/docs → 200 (Swagger UI disponible)."""
        r = api_client.get("/api/docs")
        assert r.status_code == 200

    def test_openapi_schema_accessible(self, api_client):
        """GET /api/openapi.json → 200 con schema válido."""
        r = api_client.get("/api/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert "components" in schema
