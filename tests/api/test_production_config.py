"""La configuración de producción debe fallar cerrada."""

import pytest

from api.config import Settings


def production_settings(**overrides):
    values = {
        "environment": "production",
        "database_url": "postgresql://db.example/levelup",
        "jwt_secret_key": "x" * 40,
        "cors_origins": ["https://app.example"],
        "rate_limit_storage_uri": "redis://cache.example:6379/0",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_valid_production_configuration_passes():
    production_settings().validate_runtime()


@pytest.mark.parametrize(
    "override",
    [
        {"database_url": ""},
        {"jwt_secret_key": "short"},
        {"jwt_secret_key": "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"},
        {"cors_origins": ["http://localhost:5173", "https://app.example"]},
        {"rate_limit_storage_uri": "memory://"},
    ],
)
def test_insecure_production_configuration_is_rejected(override):
    with pytest.raises(RuntimeError):
        production_settings(**override).validate_runtime()


def test_production_database_does_not_seed_demo_or_test_accounts(tmp_path, monkeypatch):
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    repo = SQLiteRepository(str(tmp_path / "production.db"))
    conn = repo.get_connection()
    try:
        usernames = {
            row[0]
            for row in conn.execute(
                "SELECT username FROM users WHERE username IN "
                "('profesor1', 'estudiante1', 'estudiante_colegio_1')"
            ).fetchall()
        }
    finally:
        conn.close()
    assert usernames == set()


def test_web_process_can_skip_schema_bootstrap(tmp_path, monkeypatch):
    """RUN_MIGRATIONS=0 deja el esquema al paso previo del despliegue.

    Sobre el pooler de transacciones el advisory lock de sesión de _migrate_db()
    no protege nada, así que migrar en el arranque HTTP no es seguro.
    """
    import sqlite3

    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    monkeypatch.setenv("RUN_MIGRATIONS", "0")
    db_path = str(tmp_path / "sin_bootstrap.db")
    SQLiteRepository(db_path)

    conn = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    finally:
        conn.close()
    assert tables == set(), "El proceso web no debe crear el esquema."

    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    SQLiteRepository(db_path)
    conn = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    finally:
        conn.close()
    assert "users" in tables and "attempts" in tables


def test_production_rejects_more_than_one_worker():
    """Con varios workers el lobby de PvP se parte en dos y nadie se entera.

    `_lobby`, `_matches` y `_rooms` viven en memoria del proceso: dos jugadores
    en workers distintos no se emparejan y los eventos llegan a medias, sin
    error visible. Mejor no arrancar que arrancar roto (AGENTS.md R18).
    """
    with pytest.raises(RuntimeError, match="WEB_CONCURRENCY"):
        production_settings(web_concurrency=4).validate_runtime()


def test_production_accepts_a_single_worker():
    production_settings(web_concurrency=1).validate_runtime()
