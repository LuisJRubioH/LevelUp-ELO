"""
V1's entry point honours RUN_MIGRATIONS=0 on both engines (AGENTS.md R17).

V1 (src/interface/streamlit/app.py) builds its repository on the first session and, by default,
bootstraps the schema in-process. On Streamlit Cloud that would migrate and seed the production
database from a web session, over the transaction pooler. Reconnecting V1 after the transfer is
only safe if RUN_MIGRATIONS=0 stops all of it, so this runs the real entry point headless
(Streamlit AppTest) against a fresh, empty database: with RUN_MIGRATIONS=0 nothing may be created;
without it the schema appears, which proves the check can see a migration.
"""

import os
import pathlib
import sqlite3
import uuid
from urllib.parse import urlsplit, urlunsplit

import pytest

pytest.importorskip("streamlit", reason="V1 stack (requirements.txt) not installed")
from streamlit.testing.v1 import AppTest  # noqa: E402

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")
_SSLMODE = os.environ.get("DATABASE_SSLMODE", "disable")
_APP = str(pathlib.Path(__file__).resolve().parents[2] / "src/interface/streamlit/app.py")


def _run_v1_landing():
    at = AppTest.from_file(_APP, default_timeout=300)
    at.run()
    return at


@pytest.fixture(params=["sqlite", "postgres"])
def empty_database(request, tmp_path, monkeypatch):
    """(engine, function listing the database's tables) for a new, empty database."""
    monkeypatch.setenv("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD") or "v1-gate-admin")
    if request.param == "sqlite":
        path = str(tmp_path / "v1_gate.db")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("DB_PATH", path)

        def tables():
            if not os.path.exists(path):
                return set()
            conn = sqlite3.connect(path)
            try:
                return {r[0] for r in conn.execute("SELECT name FROM sqlite_master")}
            finally:
                conn.close()

        yield "sqlite", tables
        return

    if not _PG_URL:
        pytest.skip("Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.")
    import psycopg2

    name = "v1_gate_" + uuid.uuid4().hex[:12]
    admin = psycopg2.connect(_PG_URL, sslmode=_SSLMODE)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f'CREATE DATABASE "{name}"')
    url = urlunsplit(urlsplit(_PG_URL)._replace(path="/" + name))
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_SSLMODE", _SSLMODE)

    def tables():
        conn = psycopg2.connect(url, sslmode=_SSLMODE)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT table_name FROM information_schema.tables"
                    " WHERE table_schema = 'public'"
                )
                return {r[0] for r in cur.fetchall()}
        finally:
            conn.close()

    try:
        yield "postgres", tables
    finally:
        with admin.cursor() as cur:
            # V1 keeps its pool open for the life of the process; FORCE ends those sessions.
            cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.close()


def test_v1_with_run_migrations_0_creates_nothing(empty_database, monkeypatch):
    _, tables = empty_database
    monkeypatch.setenv("RUN_MIGRATIONS", "0")

    at = _run_v1_landing()

    assert "db" in at.session_state, "V1 never built its repository; the check proves nothing"
    assert tables() == set(), "V1 created schema with RUN_MIGRATIONS=0"


def test_v1_without_run_migrations_bootstraps_the_schema(empty_database, monkeypatch):
    """Contrast: the same run without the variable migrates, so the check above is meaningful."""
    _, tables = empty_database
    monkeypatch.delenv("RUN_MIGRATIONS", raising=False)

    at = _run_v1_landing()

    assert not at.exception, [e.value for e in at.exception]
    assert {"users", "student_course_topic_elo"} <= tables()
