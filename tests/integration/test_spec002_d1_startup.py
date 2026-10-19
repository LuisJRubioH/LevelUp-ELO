"""
Spec 002 delivery D1 (tasks T003–T010): a start with nothing to do does nothing.

- A database at the current schema version, with the item bank unchanged, starts without DDL or
  data writes (FR-016, SC-001); an older one migrates once and records the version (FR-015).
- A failing migration commits nothing and names its step (FR-017).
- Data repairs leave the start and become scripts (FR-018); a migration that needs one stops
  naming it.
- PostgreSQL's one non-additive statement runs only while needed (FR-014).

Each test runs on a throwaway database of each engine, built by the real bootstrap. "Older"
databases are made by removing `schema_versions` from a migrated one: that is exactly what every
database deployed before D1 looks like.
"""

import json
import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import uuid
from urllib.parse import urlsplit, urlunsplit

import pytest

from tests.integration.statement_recorder import record_statements

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")
_SSLMODE = os.environ.get("DATABASE_SSLMODE", "disable")
_ROOT = pathlib.Path(__file__).resolve().parents[2]


class _SQLite:
    engine = "sqlite"

    def __init__(self, path):
        self.path = path
        self.env = {"DB_PATH": path}

    @property
    def repository_class(self):
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

        return SQLiteRepository

    def build(self):
        return self.repository_class(db_name=self.path)

    def sql(self, statement, params=()):
        conn = sqlite3.connect(self.path)
        try:
            cursor = conn.execute(statement, params)
            rows = cursor.fetchall() if cursor.description else []
            conn.commit()
            return rows
        finally:
            conn.close()

    def has_table(self, table):
        return bool(self.sql("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)))

    def has_column(self, table, column):
        return any(r[1] == column for r in self.sql(f'PRAGMA table_info("{table}")'))


class _Postgres:
    engine = "postgres"

    def __init__(self, url):
        self.url = url
        self.env = {"DATABASE_URL": url, "DATABASE_SSLMODE": _SSLMODE}

    @property
    def repository_class(self):
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        return PostgresRepository

    def build(self):
        repo = self.repository_class()
        repo._pool.closeall()
        return repo

    def sql(self, statement, params=()):
        import psycopg2

        conn = psycopg2.connect(self.url, sslmode=_SSLMODE)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(statement.replace("?", "%s"), params)
                return cur.fetchall() if cur.description else []
        finally:
            conn.close()

    def has_table(self, table):
        return self.sql("SELECT to_regclass(?) IS NOT NULL", (table,))[0][0]

    def has_column(self, table, column):
        return bool(
            self.sql(
                "SELECT 1 FROM information_schema.columns WHERE table_name = ? AND column_name = ?",
                (table, column),
            )
        )


def _throwaway_postgres(monkeypatch):
    if not _PG_URL:
        pytest.skip("Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.")
    import psycopg2

    name = "spec002_d1_" + uuid.uuid4().hex[:12]
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
            cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.close()


@pytest.fixture(autouse=True)
def _bootstrap_env(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD") or "d1-admin")
    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    monkeypatch.setenv("ENVIRONMENT", "development")  # every seed runs


@pytest.fixture(params=["sqlite", "postgres"])
def database(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        yield _SQLite(str(tmp_path / "d1.db"))
    else:
        yield from _throwaway_postgres(monkeypatch)


@pytest.fixture
def postgres_database(monkeypatch):
    yield from _throwaway_postgres(monkeypatch)


def _make_old(database):
    """A database as every one deployed before D1: migrated, without a recorded version."""
    database.sql("DROP TABLE IF EXISTS schema_versions")


def _versions(database):
    if not database.has_table("schema_versions"):
        return []
    return [r[0] for r in database.sql("SELECT version FROM schema_versions ORDER BY version")]


def _repair(database, script, *args):
    env = dict(os.environ)
    env.update(database.env)
    env["RUN_MIGRATIONS"] = "0"
    if database.engine == "sqlite":
        env.pop("DATABASE_URL", None)
    proc = subprocess.run(
        [sys.executable, f"scripts/repairs/{script}", *args],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout


def _count(output):
    """The number a repair script reports: its last line is «<n> rows …»."""
    return int(output.strip().splitlines()[-1].split()[0])


# ── US1: a start with nothing to do does nothing ────────────────────────────


def test_spec002_d1_a_current_database_starts_without_ddl_or_writes(database, monkeypatch):
    """US1-AS1, FR-016, SC-001: the second start issues no DDL and changes no row."""
    database.build()
    recorded = record_statements(monkeypatch, database.repository_class)

    database.build()

    assert recorded.ddl() == []
    assert recorded.writes() == []


def test_spec002_d1_an_old_database_migrates_once_and_records_the_version(database, monkeypatch):
    """US1-AS2, FR-015: a database without a version migrates, records it once; the next start
    issues no DDL."""
    from src.infrastructure.persistence.schema_version import SCHEMA_VERSION

    database.build()
    _make_old(database)
    recorded = record_statements(monkeypatch, database.repository_class)

    database.build()
    assert recorded.ddl(), "an old database must be migrated"
    assert _versions(database) == [SCHEMA_VERSION]

    recorded.statements.clear()
    database.build()
    assert recorded.ddl() == []
    assert _versions(database) == [SCHEMA_VERSION]


def test_spec002_d1_a_failing_migration_commits_nothing(database, monkeypatch):
    """US1-AS3, FR-017: a step that fails after DDL leaves no column and no version, and the
    error names the step."""
    from src.infrastructure.persistence.schema_version import MigrationFailed

    database.build()
    _make_old(database)
    cls = database.repository_class

    def failing_step(self, cursor=None):
        cursor.execute("ALTER TABLE users ADD COLUMN d1_probe TEXT")
        raise RuntimeError("d1 probe failure")

    monkeypatch.setattr(cls, "_ensure_procedure_pair_index", failing_step)

    with pytest.raises(MigrationFailed, match="migrate_db"):
        database.build()

    assert not database.has_column("users", "d1_probe")
    assert _versions(database) == []


def test_spec002_d1_a_fresh_database_with_the_lock_held_stops_naming_the_step(postgres_database):
    """FR-011 with FR-017: on a database never migrated, another session's migration lock stops
    the start before any step reads the schema the migration would create (tasks-d1 T002)."""
    import psycopg2

    holder = psycopg2.connect(postgres_database.url, sslmode=_SSLMODE)
    holder.autocommit = True
    try:
        with holder.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(12345)")
        env = dict(os.environ)
        env.update({"MIGRATION_DATABASE_URL": postgres_database.url, "DATABASE_SSLMODE": _SSLMODE})
        proc = subprocess.run(
            [sys.executable, "scripts/migrate.py"],
            cwd=_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
    finally:
        holder.close()
    output = proc.stdout + proc.stderr

    assert proc.returncode != 0, output
    assert "migrate_db" in output
    assert "Traceback" not in output, output


# ── US2: data is repaired only on purpose ───────────────────────────────────


def _user_without_password(database, active=1):
    name = "d1_nopass_" + uuid.uuid4().hex[:8]
    database.sql(
        "INSERT INTO users (username, password_hash, role, active) VALUES (?, '', 'student', ?)",
        (name, active),
    )
    return name


def _active(database, username):
    return database.sql("SELECT active FROM users WHERE username = ?", (username,))[0][0]


def test_spec002_d1_a_reactivated_user_without_password_stays_active(database):
    """US2-AS1, FR-018: neither a start nor a full migration deactivates a user the admin
    reactivated."""
    database.build()
    username = _user_without_password(database, active=1)

    database.build()
    assert _active(database, username) == 1

    _make_old(database)
    database.build()
    assert _active(database, username) == 1


def _duplicate_groups(database):
    """Two groups of one teacher whose names differ only in case and spaces, and one without
    its normalised name — what the unique index forbids, as an old database may hold."""
    teacher = database.sql("SELECT id FROM users WHERE username = 'profesor1'")[0][0]
    database.sql("DROP INDEX IF EXISTS idx_groups_teacher_name_unique")
    name = "D1 Grupo " + uuid.uuid4().hex[:6]
    for variant, normalised in ((name, name.lower()), (f" {name.upper()} ", name.lower())):
        database.sql(
            "INSERT INTO groups (name, teacher_id, name_normalized) VALUES (?, ?, ?)",
            (variant, teacher, normalised),
        )
    database.sql(
        "INSERT INTO groups (name, teacher_id, name_normalized) VALUES (?, ?, NULL)",
        ("D1 Sin Normalizar " + uuid.uuid4().hex[:6], teacher),
    )
    return name


def _attempt_without_prob_failure(database):
    user = database.sql("SELECT id FROM users WHERE username = 'estudiante1'")[0][0]
    database.sql(
        "INSERT INTO attempts (user_id, item_id, is_correct, difficulty, topic, elo_after,"
        " prob_failure) VALUES (?, 'd1_item', ?, 1000, 'd1_topic', 1010.0, NULL)",
        (user, True),
    )


def _katia_text(database):
    """Spec 005 N3: a message typed before K3, kept with no expiry."""
    user = database.sql("SELECT id FROM users WHERE username = 'estudiante1'")[0][0]
    database.sql(
        "INSERT INTO katia_interactions (user_id, course_id, item_id, item_topic,"
        " student_message, katia_response) VALUES (?, 'k3', 'k3_item', 'k3', 'hola', 'Mira el signo.')",
        (user,),
    )


@pytest.mark.parametrize(
    "script, prepare, expected",
    [
        ("deactivate_users_without_password.py", _user_without_password, 1),
        ("rename_duplicate_groups.py", _duplicate_groups, 2),  # one renamed, one filled
        ("backfill_prob_failure.py", _attempt_without_prob_failure, 1),
        ("delete_katia_texts.py", _katia_text, 1),  # spec 005 N3
    ],
    ids=["users", "groups", "prob_failure", "katia_texts"],
)
def test_spec002_d1_repair_scripts_report_and_are_idempotent(database, script, prepare, expected):
    """US2-AS2, FR-018: a dry run reports and changes nothing; --apply changes and reports the
    rows; a second --apply reports 0."""
    database.build()
    prepare(database)

    assert _count(_repair(database, script)) == expected
    assert _count(_repair(database, script)) == expected, "a dry run must change nothing"
    assert _count(_repair(database, script, "--apply")) == expected
    assert _count(_repair(database, script, "--apply")) == 0


def test_spec002_d1_duplicate_groups_stop_the_migration_naming_the_script(database):
    """US2-AS3, FR-017, FR-018: duplicates before the unique index stop the migration with the
    repair script's name; nothing is renamed or recorded. After the repair, it migrates."""
    from src.infrastructure.persistence.schema_version import MigrationNeedsRepair

    database.build()
    name = _duplicate_groups(database)
    _make_old(database)

    with pytest.raises(MigrationNeedsRepair, match="rename_duplicate_groups.py"):
        database.build()

    assert not database.sql("SELECT 1 FROM groups WHERE name LIKE ?", ("%-DUP-%",))
    assert database.sql("SELECT COUNT(*) FROM groups WHERE name_normalized IS NULL")[0][0] == 1
    assert _versions(database) == []
    assert len(database.sql("SELECT 1 FROM groups WHERE LOWER(TRIM(name)) = ?", (name.lower(),)))

    _repair(database, "rename_duplicate_groups.py", "--apply")
    database.build()
    assert _versions(database)


# ── US3: the schema only grows ──────────────────────────────────────────────


def test_spec002_d1_drop_not_null_runs_only_while_needed(postgres_database, monkeypatch):
    """US3-AS1, US3-AS2, FR-014 (PostgreSQL only: SQLite's column is nullable from the start)."""
    from src.infrastructure.persistence.schema_version import SCHEMA_VERSION

    database = postgres_database
    database.build()
    recorded = record_statements(monkeypatch, database.repository_class)

    _make_old(database)
    database.build()
    assert recorded.matching(r"DROP\s+NOT\s+NULL") == []

    recorded.statements.clear()
    database.sql("ALTER TABLE procedure_submissions ALTER COLUMN image_data SET NOT NULL")
    _make_old(database)
    database.build()
    assert len(recorded.matching(r"DROP\s+NOT\s+NULL")) == 1
    nullable = database.sql(
        "SELECT is_nullable FROM information_schema.columns"
        " WHERE table_name = 'procedure_submissions' AND column_name = 'image_data'"
    )[0][0]
    assert nullable == "YES"
    assert _versions(database) == [SCHEMA_VERSION]


# ── Edge case: the bank changed, not the schema ─────────────────────────────


def test_spec002_d1_a_changed_bank_only_resyncs_the_bank(database, tmp_path, monkeypatch):
    """Spec § Edge Cases, FR-016: an edited bank is synced and its fingerprint recorded, with no
    DDL and no other write; an unchanged bank is not synced again."""
    bank = tmp_path / "bank"
    shutil.copytree(_ROOT / "items" / "bank", bank)
    monkeypatch.setattr(database.repository_class, "BANK_DIR", str(bank), raising=False)
    database.build()
    recorded = record_statements(monkeypatch, database.repository_class)

    edited = bank / "geometria.json"
    items = json.loads(edited.read_text(encoding="utf-8"))
    items[0]["content"] = items[0]["content"] + " (D1)"
    edited.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    database.build()

    assert recorded.ddl() == []
    for statement, _ in recorded.writes():
        assert any(t in statement for t in ("items", "courses", "bank_syncs")), statement
    stored = database.sql("SELECT content FROM items WHERE id = ?", (items[0]["id"],))[0][0]
    assert stored == items[0]["content"]

    recorded.statements.clear()
    database.build()
    assert recorded.writes() == []
    assert recorded.matching(r"^\s*UPDATE\s+items") == []
