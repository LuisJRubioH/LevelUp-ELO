"""
Spec 002 D3 (FR-040; decisions N1, N7, N8): both engines build the same schema and seed, apart
from the differences accepted in src/infrastructure/persistence/engine_differences.py.

The runtime half of the parity check: each engine is bootstrapped from empty and its catalogue
read back (SQLite: sqlite_master and PRAGMAs; PostgreSQL: information_schema and pg_index), so
what is compared is what the databases report, not what the code looks like.
"""

import json
import os
import shutil
import sqlite3
import uuid
from urllib.parse import urlsplit, urlunsplit

import pytest

from tests.integration.conftest import register_course

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")
_SSLMODE = os.environ.get("DATABASE_SSLMODE", "disable")


@pytest.fixture(autouse=True)
def _bootstrap_env(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD") or "d3-admin")
    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    monkeypatch.setenv("ENVIRONMENT", "development")  # the seeds run (N8)


@pytest.fixture
def postgres_url(monkeypatch):
    if not _PG_URL:
        pytest.skip("Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.")
    import psycopg2

    name = "spec002_d3_" + uuid.uuid4().hex[:12]
    admin = psycopg2.connect(_PG_URL, sslmode=_SSLMODE)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f'CREATE DATABASE "{name}"')
    url = urlunsplit(urlsplit(_PG_URL)._replace(path="/" + name))
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_SSLMODE", _SSLMODE)
    try:
        yield url
    finally:
        with admin.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.close()


def _sqlite_catalogue(path):
    from src.infrastructure.persistence.engine_differences import Catalogue

    conn = sqlite3.connect(path)
    try:
        catalogue = Catalogue()
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        ]
        for table in tables:
            for _, column, declared, *_ in conn.execute(f'PRAGMA table_info("{table}")'):
                catalogue.add_column(table, column, declared)
            for _, index, unique, origin, _partial in conn.execute(f'PRAGMA index_list("{table}")'):
                if origin == "pk":
                    continue
                columns = [r[2] for r in conn.execute(f'PRAGMA index_info("{index}")')]
                catalogue.add_index(table, columns, bool(unique))
        return catalogue
    finally:
        conn.close()


def _postgres_catalogue(conn):
    from src.infrastructure.persistence.engine_differences import Catalogue

    catalogue = Catalogue()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name, column_name, data_type FROM information_schema.columns"
            " WHERE table_schema = 'public'"
        )
        for table, column, declared in cur.fetchall():
            catalogue.add_column(table, column, declared)
        cur.execute(
            """
            SELECT t.relname, array_agg(a.attname ORDER BY k.ord), ix.indisunique
              FROM pg_index ix
              JOIN pg_class t ON t.oid = ix.indrelid
              JOIN pg_namespace n ON n.oid = t.relnamespace
             CROSS JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY k(attnum, ord)
              JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
             WHERE n.nspname = 'public' AND NOT ix.indisprimary
             GROUP BY t.relname, ix.indexrelid, ix.indisunique
        """
        )
        for table, columns, unique in cur.fetchall():
            catalogue.add_index(table, list(columns), unique)
    return catalogue


def _seed_counts(run):
    return {
        "test students": run("SELECT COUNT(*) FROM users WHERE is_test_user = 1"),
        "groups": run("SELECT COUNT(*) FROM groups"),
        "test enrolments": run(
            "SELECT COUNT(*) FROM enrollments e JOIN users u ON u.id = e.user_id"
            " WHERE u.is_test_user = 1"
        ),
    }


def test_both_engines_build_the_same_schema(tmp_path, postgres_url):
    """FR-040 at runtime, N1, N7, N8: tables, columns, column types (by family) and indexes,
    and the local seed, are the same on both engines apart from the accepted differences."""
    import psycopg2

    from src.infrastructure.persistence.engine_differences import unexplained
    from src.infrastructure.persistence.postgres_repository import PostgresRepository
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    sqlite_path = str(tmp_path / "d3.db")
    SQLiteRepository(db_name=sqlite_path)
    PostgresRepository()._pool.closeall()

    conn = psycopg2.connect(postgres_url, sslmode=_SSLMODE)
    try:
        problems = unexplained(
            _sqlite_catalogue(sqlite_path), _postgres_catalogue(conn), runtime=True
        )

        def pg(query):
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchone()[0]

        pg_seed = _seed_counts(pg)
    finally:
        conn.close()

    lite = sqlite3.connect(sqlite_path)
    try:
        sqlite_seed = _seed_counts(lambda q: lite.execute(q).fetchone()[0])
    finally:
        lite.close()

    assert problems == []
    assert sqlite_seed == pg_seed


@pytest.mark.parametrize("engine", ["sqlite", "postgres"])
def test_item_sync_updates_course_name_and_block(engine, tmp_path, monkeypatch, request):
    """N1: the bank is the source — a course renamed or moved to another block in the bank is
    renamed or moved in the database too, on both engines."""
    bank = tmp_path / "bank"
    bank.mkdir()
    course = "d3_curso_" + uuid.uuid4().hex[:6]
    items = [
        {
            "id": f"{course}_1",
            "content": "¿Cuánto es $2+2$?",
            "difficulty": 900,
            "topic": "Tema D3",
            "options": ["3", "4"],
            "correct_option": "4",
        }
    ]
    (bank / f"{course}.json").write_text(json.dumps(items), encoding="utf-8")
    # Spec 008 C: a bank course is in the course catalogue (no «Universidad» fallback, O-C5).
    register_course(monkeypatch, course, "Universidad", "Tema D3")

    if engine == "sqlite":
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

        repo = SQLiteRepository(db_name=str(tmp_path / "sync.db"))

        def course_row():
            conn = sqlite3.connect(str(tmp_path / "sync.db"))
            try:
                return conn.execute(
                    "SELECT name, block FROM courses WHERE id = ?", (course,)
                ).fetchone()
            finally:
                conn.close()

    else:
        request.getfixturevalue("postgres_url")
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        repo = PostgresRepository()

        def course_row():
            conn = repo.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, block FROM courses WHERE id = %s", (course,))
                    row = cur.fetchone()
                    return (row["name"], row["block"]) if isinstance(row, dict) else row
            finally:
                repo.put_connection(conn)

    try:
        repo.sync_items_from_bank_folder(str(bank))
        assert course_row() == ("Tema D3", "Universidad")

        register_course(monkeypatch, course, "Colegio", "Curso D3 renombrado")
        repo.sync_items_from_bank_folder(str(bank))
        assert course_row() == ("Curso D3 renombrado", "Colegio")
    finally:
        if engine == "postgres":
            repo._pool.closeall()
