"""
Spec 001 FR-028n (tasks T090, T097; docs/sdd/f1-semillero-survey.md § 4.2–4.3, AGENTS R8): the
migration reads the `courses.block` CHECK and never rewrites it.

- It accepts the four blocks the code writes → no DDL, extra values kept; two migrations leave
  it as it was (PostgreSQL: the same constraint oid).
- It lacks one of them (an old database) → the migration stops with an error naming the missing
  value, before touching the constraint or the table; `scripts/migrate.py` exits 1.

Each case runs on a throwaway database of each engine, seeded with the constraint under test
before the repository bootstraps.
"""

import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import uuid
from urllib.parse import urlsplit, urlunsplit

import pytest

FOUR = ("Universidad", "Colegio", "Concursos", "Semillero")
PRODUCTION = FOUR + ("Semillero 11°",)  # what `main` leaves on PostgreSQL
OLD = ("Universidad", "Colegio", "Concursos")

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")
_SSLMODE = os.environ.get("DATABASE_SSLMODE", "disable")
_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _courses_ddl(values):
    allowed = ", ".join(f"'{v}'" for v in values)
    return (
        "CREATE TABLE courses (id TEXT PRIMARY KEY, name TEXT NOT NULL,"
        f" block TEXT NOT NULL CHECK (block IN ({allowed})), description TEXT DEFAULT '')"
    )


class _SQLite:
    engine = "sqlite"

    def __init__(self, path):
        self.path = path

    def create_courses(self, values):
        conn = sqlite3.connect(self.path)
        conn.execute(_courses_ddl(values))
        conn.commit()
        conn.close()

    def bootstrap(self):
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

        SQLiteRepository(db_name=self.path)

    def state(self):
        """The courses table's DDL."""
        conn = sqlite3.connect(self.path)
        try:
            return conn.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'courses'"
            ).fetchone()[0]
        finally:
            conn.close()

    def foreign_key_targets(self):
        """Every table a foreign key points at."""
        conn = sqlite3.connect(self.path)
        try:
            tables = [
                r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            ]
            return {fk[2] for t in tables for fk in conn.execute(f'PRAGMA foreign_key_list("{t}")')}
        finally:
            conn.close()

    def accepts(self, block):
        conn = sqlite3.connect(self.path)
        try:
            conn.execute(
                "INSERT INTO courses (id, name, block) VALUES (?, 'probe', ?)",
                ("probe_" + uuid.uuid4().hex[:8], block),
            )
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.rollback()
            conn.close()

    def allowed(self):
        return set(re.findall(r"'([^']*)'", re.search(r"block IN \(([^)]*)\)", self.state())[1]))


class _Postgres:
    engine = "postgres"

    def __init__(self, url):
        self.url = url

    def _connect(self):
        import psycopg2

        return psycopg2.connect(self.url, sslmode=_SSLMODE)

    def create_courses(self, values):
        conn = self._connect()
        with conn, conn.cursor() as cur:
            cur.execute(_courses_ddl(values))
        conn.close()

    def bootstrap(self):
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        PostgresRepository()._pool.closeall()

    def state(self):
        """(oid, definition) of every CHECK constraint on courses."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT oid, pg_get_constraintdef(oid) FROM pg_constraint"
                    " WHERE conrelid = 'courses'::regclass AND contype = 'c' ORDER BY oid"
                )
                return cur.fetchall()
        finally:
            conn.close()

    def accepts(self, block):
        import psycopg2

        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO courses (id, name, block) VALUES (%s, 'probe', %s)",
                    ("probe_" + uuid.uuid4().hex[:8], block),
                )
            return True
        except psycopg2.errors.CheckViolation:
            return False
        finally:
            conn.rollback()
            conn.close()

    def allowed(self):
        (definition,) = [d for _, d in self.state()]
        return set(re.findall(r"'([^']*)'", definition))


def _throwaway_postgres(monkeypatch):
    """A new, empty PostgreSQL database the repository reads through DATABASE_URL."""
    if not _PG_URL:
        pytest.skip("Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.")
    import psycopg2

    name = "f1_block_" + uuid.uuid4().hex[:12]
    admin = psycopg2.connect(_PG_URL, sslmode=_SSLMODE)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f'CREATE DATABASE "{name}"')
    url = urlunsplit(urlsplit(_PG_URL)._replace(path="/" + name))
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_SSLMODE", _SSLMODE)
    try:
        yield _Postgres(url)
    finally:
        with admin.cursor() as cur:
            # A repository whose bootstrap raised leaves its pool open; FORCE ends it.
            cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.close()


@pytest.fixture(autouse=True)
def _bootstrap_env(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD") or "f1-admin")
    monkeypatch.setenv("RUN_MIGRATIONS", "1")


@pytest.fixture(params=["sqlite", "postgres"])
def database(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        yield _SQLite(str(tmp_path / "f1_block.db"))
    else:
        yield from _throwaway_postgres(monkeypatch)


@pytest.fixture
def postgres_database(monkeypatch):
    yield from _throwaway_postgres(monkeypatch)


def test_spec001_new_database_accepts_exactly_the_four_blocks(database):
    """FR-028n: a new database on either engine allows the same four blocks; a second
    migration issues no DDL on the constraint."""
    database.bootstrap()
    first = database.state()
    database.bootstrap()

    assert database.state() == first
    assert database.allowed() == set(FOUR)
    assert all(database.accepts(block) for block in FOUR)
    assert not database.accepts("Semillero 6°")


def test_spec001_constraint_with_extra_values_is_left_as_it_is(database):
    """FR-028n, survey § 4.2: the production constraint (the four plus 'Semillero 11°') is kept
    with its extra value; two migrations leave it untouched — on PostgreSQL the same oid (today
    it is dropped and re-added on every run)."""
    database.create_courses(PRODUCTION)
    before = database.state()

    database.bootstrap()
    database.bootstrap()

    assert database.state() == before
    assert database.allowed() == set(PRODUCTION)
    assert not database.accepts("Semillero 6°")


def test_spec001_old_database_stops_the_migration(database):
    """FR-028n, survey § 4.3: a constraint without 'Semillero' stops the migration with an error
    that names it; the constraint, the table and the other tables' foreign keys stay as they
    were (today SQLite rebuilds the table and PostgreSQL drops and re-adds the constraint)."""
    database.create_courses(OLD)
    before = database.state()

    with pytest.raises(Exception) as stopped:
        database.bootstrap()

    assert "'Semillero'" in str(stopped.value)
    assert "f1-semillero-survey.md § 4.3" in str(stopped.value)
    assert database.state() == before
    if database.engine == "sqlite":
        # The old rebuild renamed courses first, leaving foreign keys on "_courses_old".
        assert "courses" in database.foreign_key_targets()
        assert "_courses_old" not in database.foreign_key_targets()
    assert not database.accepts("Semillero")


def test_spec001_migrate_py_exits_1_on_an_old_database(postgres_database):
    """FR-028n, AGENTS R17: `scripts/migrate.py && uvicorn` never starts the web process on a
    database whose constraint lacks a block (scripts/migrate.py migrates PostgreSQL only)."""
    database = postgres_database
    database.create_courses(OLD)
    before = database.state()
    env = dict(os.environ, MIGRATION_DATABASE_URL=database.url, DATABASE_SSLMODE=_SSLMODE)

    run = subprocess.run(
        [sys.executable, "scripts/migrate.py"],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert run.returncode == 1, run.stdout[-2000:] + run.stderr[-2000:]
    assert "'Semillero'" in run.stdout + run.stderr
    assert "Migraciones completadas." not in run.stdout
    assert database.state() == before
