"""
scripts/migrate.py must not report success when a bootstrap step was skipped (AGENTS.md R17).

Every bootstrap step that writes shared state takes a non-blocking PostgreSQL advisory lock and,
in-process, simply skips when another instance holds it. For the dedicated migration step that
skip used to be silent: migrate.py printed "Migraciones completadas." and the start command
(`python scripts/migrate.py && uvicorn ...`) launched the web process on a schema that might not
be migrated. These tests hold each lock from another session, run the real start-command shape
and require a failure that names the skipped step, with no web process.

PostgreSQL only: SQLite has no advisory locks and serialises writers, so its bootstrap never skips
a step; the two-engine test pins that both repositories report the skipped steps the same way.
"""

import os
import pathlib
import subprocess
import sys

import psycopg2
import pytest

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")
_ROOT = pathlib.Path(__file__).resolve().parents[2]
_WEB = "WEB-PROCESS-STARTED"

# (advisory lock id, bootstrap steps that must be reported when another session holds it)
_LOCKS = [
    (12345, ["migrate_db", "reconcile_legacy_ratings"]),
    (12346, ["seed_admin"]),
    (12347, ["seed_demo_data"]),
    (12348, ["sync_items_from_bank_folder"]),
    (12349, ["seed_test_students"]),
]


def _start_command():
    """`python scripts/migrate.py && <web process>`, as render.yaml's startCommand."""
    env = dict(os.environ)
    env.update(
        {
            "MIGRATION_DATABASE_URL": _PG_URL,
            "DATABASE_SSLMODE": os.environ.get("DATABASE_SSLMODE", "disable"),
            "ADMIN_PASSWORD": os.environ.get("ADMIN_PASSWORD") or "postgres-audit-admin",
            "ENVIRONMENT": "development",  # every seed runs, so every lock is exercised
        }
    )
    proc = subprocess.run(
        ["bash", "-c", f'"{sys.executable}" scripts/migrate.py && echo {_WEB}'],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return proc.returncode, proc.stdout + proc.stderr


@pytest.fixture
def postgres_only():
    if not _PG_URL:
        pytest.skip("Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.")


@pytest.mark.parametrize("lock_id, steps", _LOCKS, ids=[str(lock) for lock, _ in _LOCKS])
def test_migrate_fails_and_blocks_the_web_process_when_a_lock_is_held(
    postgres_only, lock_id, steps
):
    holder = psycopg2.connect(_PG_URL, sslmode=os.environ.get("DATABASE_SSLMODE", "disable"))
    holder.autocommit = True
    try:
        with holder.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", (lock_id,))
            assert cursor.fetchone()[0], f"lock {lock_id} already held before the test"
        code, output = _start_command()
    finally:
        holder.close()  # ends the session, releasing the lock

    assert code != 0, output
    assert "Migraciones completadas." not in output
    assert _WEB not in output, "the web process started on an unverified schema"
    for step in steps:
        assert step in output, f"{step} not named in:\n{output}"


def test_migrate_succeeds_and_starts_the_web_process_without_contention(postgres_only):
    code, output = _start_command()

    assert code == 0, output
    assert "Migraciones completadas." in output
    assert _WEB in output


def test_bootstrap_reports_no_skipped_step_without_contention(repo):
    """Both engines expose the skipped steps; an uncontended bootstrap skips none."""
    assert repo.bootstrap_skipped_steps() == []
