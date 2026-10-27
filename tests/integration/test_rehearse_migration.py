"""
docs/transfer.md § 4–5: `scripts/rehearse_migration.py` on a copy already past the first switch.

Production has carried the redesign since 2026-10-22, so every later block reaches it as an
upgrade (schema 6 → 8 next, roadmap 2026-10-27): its copy already holds reconciled baselines and
exams with their overall rating. A migration that moves none of them must rehearse green.

Needs POSTGRES_TEST_DATABASE_URL (a local disposable server whose role may create databases) and
`pg_dump`/`pg_restore` on the PATH; skipped otherwise.
"""

import os
import shutil
import subprocess
import sys
import uuid
from urllib.parse import urlsplit, urlunsplit

import psycopg2
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not _PG_URL or not shutil.which("pg_dump") or not shutil.which("pg_restore"),
    reason="Requiere POSTGRES_TEST_DATABASE_URL y pg_dump/pg_restore.",
)


def _url_for(database: str) -> str:
    parts = urlsplit(_PG_URL)
    return urlunsplit(parts._replace(path=f"/{database}"))


def _execute(url: str, statement: str, params=()):
    conn = psycopg2.connect(url, sslmode="disable")
    try:
        with conn.cursor() as cur:
            cur.execute(statement, params)
            row = cur.fetchone() if cur.description else None
        conn.commit()
        return row
    finally:
        conn.close()


@pytest.fixture
def databases():
    """A source and an empty scratch database, both dropped afterwards."""
    names = [f"rehearse_{kind}_{uuid.uuid4().hex[:8]}" for kind in ("source", "scratch")]
    admin = psycopg2.connect(_PG_URL, sslmode="disable")
    admin.autocommit = True
    try:
        with admin.cursor() as cur:
            for name in names:
                cur.execute(f'CREATE DATABASE "{name}"')
        yield [_url_for(name) for name in names]
    finally:
        with admin.cursor() as cur:
            for name in names:
                cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.close()


def _migrate(url: str) -> None:
    env = dict(
        os.environ,
        DATABASE_URL=url,
        MIGRATION_DATABASE_URL=url,
        DATABASE_SSLMODE="disable",
        ENVIRONMENT="development",
        RUN_MIGRATIONS="1",
    )
    proc = subprocess.run(
        [sys.executable, "scripts/migrate.py"], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert proc.returncode == 0, (proc.stdout + proc.stderr)[-2000:]


def test_rehearsal_passes_on_a_copy_already_past_the_first_switch(databases, tmp_path):
    source, scratch = databases
    _migrate(source)
    # What production holds since the switch: a baseline reconciled from a legacy row (both kept)
    # and an exam submitted afterwards with its overall rating.
    student = _execute(source, "SELECT id FROM users WHERE role = 'student' ORDER BY id LIMIT 1")[0]
    course, topic = _execute(source, "SELECT course_id, topic FROM items ORDER BY id LIMIT 1")
    _execute(
        source,
        "INSERT INTO student_topic_elo (user_id, topic, current_elo, rd)"
        " VALUES (%s, %s, 1123, 140)",
        (student, topic),
    )
    _execute(
        source,
        "INSERT INTO student_course_topic_elo (user_id, course_id, topic, current_elo, rd, origin,"
        " approximate, legacy_source_key, reconciled_at)"
        " VALUES (%s, %s, %s, 1123, 140, 'legacy_topic_row', TRUE, %s, NOW())",
        (student, course, topic, topic),
    )
    _execute(
        source,
        "INSERT INTO exam_sessions (user_id, course_id, n_questions, correct_count, score_pct,"
        " global_elo_after, global_elo_status) VALUES (%s, %s, 5, 4, 80, 1123, 'rated')",
        (student, course),
    )

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/rehearse_migration.py",
            "--source-url",
            source,
            "--source-sslmode",
            "disable",
            "--dump",
            str(tmp_path / "source.dump"),
            "--scratch-url",
            scratch,
            "--scratch-sslmode",
            "disable",
        ],
        cwd=ROOT,
        env={
            k: v
            for k, v in os.environ.items()
            if k not in ("DATABASE_URL", "MIGRATION_DATABASE_URL")
        },
        capture_output=True,
        text=True,
    )

    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out[-3000:]
    assert "RESULT: PASS" in out
    assert "[FAIL]" not in out
