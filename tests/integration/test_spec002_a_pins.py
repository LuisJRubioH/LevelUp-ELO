"""
Spec 002 delivery A: as-is pins (FR-001, FR-002, FR-012, FR-013, FR-020, FR-021).

What persistence already guarantees, each tied to a test that passes on the unchanged code: the
engine follows `DATABASE_URL`; one repository per process; production seeds no demo or test
account; the schema only grows, idempotently; at most 5 PostgreSQL connections; every connection
goes back to the pool.
"""

import ast
import inspect
import re

import pytest

from src.infrastructure.persistence.schema_version import _MIGRATION_METHODS
from tests.integration.conftest import is_postgres, sql

# ── FR-001, FR-002: the engine and the instance ─────────────────────────────


@pytest.fixture
def fresh_dependency(monkeypatch):
    import api.dependencies as dependencies

    monkeypatch.setattr(dependencies, "_repo_instance", None)
    return dependencies


@pytest.mark.parametrize("database_url", [None, "postgresql://u:p@db.example:5432/x"])
def test_spec002_engine_follows_database_url(fresh_dependency, monkeypatch, database_url):
    """FR-001: `DATABASE_URL` set → PostgreSQL; absent → SQLite."""
    from src.infrastructure.persistence import postgres_repository, sqlite_repository

    built = []
    monkeypatch.setattr(postgres_repository, "PostgresRepository", lambda: built.append("pg"))
    monkeypatch.setattr(sqlite_repository, "SQLiteRepository", lambda: built.append("sqlite"))
    if database_url:
        monkeypatch.setenv("DATABASE_URL", database_url)
    else:
        monkeypatch.delenv("DATABASE_URL", raising=False)

    fresh_dependency.get_repository()

    assert built == (["pg"] if database_url else ["sqlite"])


def test_spec002_one_repository_per_process(fresh_dependency, monkeypatch):
    """FR-002 (R12): V2 builds the repository once; frozen V1 keeps its locked singleton."""
    from src.infrastructure.persistence import sqlite_repository

    built = []
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(
        sqlite_repository, "SQLiteRepository", lambda: built.append(object()) or built[-1]
    )

    first = fresh_dependency.get_repository()
    assert fresh_dependency.get_repository() is first
    assert len(built) == 1

    v1 = open("src/interface/streamlit/app.py", encoding="utf-8").read()
    assert "_REPO_SINGLETON" in v1 and "threading.Lock()" in v1


# ── FR-012: production seeds no demo or test account ────────────────────────


@pytest.mark.parametrize("environment", ["production", "development"])
def test_spec002_production_seeds_no_demo_or_test_accounts(repo, monkeypatch, environment):
    """FR-012, both engines: the start skips both seeds in production and runs them elsewhere
    (the second case keeps the pin from passing vacuously)."""
    called = []
    cls = type(repo)
    monkeypatch.setattr(cls, "_seed_demo_data", lambda self: called.append("demo"))
    monkeypatch.setattr(cls, "_seed_test_students", lambda self: called.append("test"))
    monkeypatch.setenv("ENVIRONMENT", environment)

    repo._bootstrap_schema()

    assert called == ([] if environment == "production" else ["demo", "test"])


# ── FR-013: the schema only grows, idempotently ─────────────────────────────

_FORBIDDEN = {
    "a table created without IF NOT EXISTS": r"CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)",
    "an index created without IF NOT EXISTS": r"CREATE\s+(UNIQUE\s+)?INDEX\s+(?!IF\s+NOT\s+EXISTS)",
    "a DROP": r"\bDROP\s+(?!NOT\s+NULL)",
    "a type change": r"ALTER\s+COLUMN\s+\w+\s+(SET\s+DATA\s+)?TYPE",
    "a rename": r"\bRENAME\b",
}


def _sql_strings(function) -> list[str]:
    """The string literals a method's code holds (f-string parts included), docstring excluded."""
    tree = ast.parse(inspect.cleandoc("\n" + inspect.getsource(function)))
    body = tree.body[0].body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    return [
        node.value
        for stmt in body
        for node in ast.walk(stmt)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


@pytest.mark.parametrize("engine", ["sqlite", "postgres"])
def test_spec002_migration_code_only_adds(engine):
    """FR-013 (R8): no DROP, type change or rename; every table and index IF NOT EXISTS; a
    PostgreSQL column only ADD COLUMN IF NOT EXISTS; the one DROP NOT NULL is FR-014's."""
    if engine == "sqlite":
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository as cls
    else:
        from src.infrastructure.persistence.postgres_repository import PostgresRepository as cls

    found = []
    for name in _MIGRATION_METHODS:
        text = "\n".join(_sql_strings(getattr(cls, name)))
        for what, pattern in _FORBIDDEN.items():
            if re.search(pattern, text, re.IGNORECASE):
                found.append((name, what))
        if re.search(r"DROP\s+NOT\s+NULL", text, re.IGNORECASE) and name != (
            "_make_image_data_nullable"
        ):
            found.append((name, "a DROP NOT NULL outside FR-014"))
        if engine == "postgres" and re.search(
            r"ADD\s+COLUMN\s+(?!IF\s+NOT\s+EXISTS)", text, re.IGNORECASE
        ):
            found.append((name, "a column added without IF NOT EXISTS"))
    assert found == []


def _schema(repo) -> set:
    if is_postgres(repo):
        rows = sql(
            repo,
            "SELECT table_name, column_name FROM information_schema.columns"
            " WHERE table_schema = 'public'",
        )
    else:
        tables = [r[0] for r in sql(repo, "SELECT name FROM sqlite_master WHERE type = 'table'")]
        rows = [(t, c[1]) for t in tables for c in sql(repo, f"PRAGMA table_info({t})")]
    return {tuple(r) for r in rows}


def test_spec002_migration_runs_twice_without_change(repo):
    """FR-013, both engines: the whole migration run again on a migrated database changes no
    table or column (the version gate is lowered so every step actually runs)."""
    before = _schema(repo)
    for _ in range(2):
        sql(repo, "DELETE FROM schema_versions")
        assert repo._migrate_db()
    assert _schema(repo) == before


# ── FR-020, FR-021: the PostgreSQL pool ─────────────────────────────────────


def test_spec002_at_most_five_postgresql_connections(monkeypatch):
    """FR-020 (R4): the pool's maximum is 5, and the idle minimum cannot be raised past it."""
    from src.infrastructure.persistence.postgres_repository import PostgresRepository, _env_number

    source = inspect.getsource(PostgresRepository.__init__)
    assert re.search(r"maxconn\s*=\s*5\b", source)
    assert re.search(r'_env_number\("DB_POOL_MIN_IDLE",\s*2,\s*1,\s*5\)', source)
    monkeypatch.setenv("DB_POOL_MIN_IDLE", "50")
    assert _env_number("DB_POOL_MIN_IDLE", 2, 1, 5) == 5


def test_spec002_every_postgresql_connection_goes_back_to_the_pool():
    """FR-021 (R4): no repository method closes a connection; every method that takes one
    returns it with put_connection in a finally block."""
    from src.infrastructure.persistence import postgres_repository

    tree = ast.parse(inspect.getsource(postgres_repository))
    unreturned, closes = [], []
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for fn in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
            calls = [
                n.func.attr
                for n in ast.walk(fn)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            ]
            if "close" in calls:
                closes.append(fn.name)
            if "get_connection" not in calls:
                continue
            returned = any(
                isinstance(c, ast.Call)
                and isinstance(c.func, ast.Attribute)
                and c.func.attr == "put_connection"
                for t in ast.walk(fn)
                if isinstance(t, ast.Try)
                for s in t.finalbody
                for c in ast.walk(s)
            )
            if not returned:
                unreturned.append(fn.name)
    assert unreturned == [] and closes == []
