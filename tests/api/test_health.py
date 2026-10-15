"""Readiness debe comprobar la base y fallar con un estado útil al orquestador."""


def test_health_executes_database_probe(api_client):
    response = api_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["db"] == "ok"


def test_health_returns_503_without_exposing_database_error(api_client, monkeypatch):
    import api.dependencies as dependencies

    def unavailable():
        raise RuntimeError("postgresql://secret-user:secret-password@private-host/db")

    monkeypatch.setattr(dependencies, "get_repository", unavailable)
    response = api_client.get("/api/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Base de datos no disponible."}
    assert "secret-password" not in response.text
