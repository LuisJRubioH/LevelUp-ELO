"""
Spec 008 delivery L (US4-AS3; FR-032, plan-l.md O-IL9, O-IL10): `scripts/recalibrate_items.py`.

The script prints counts by default and writes nothing; with `--apply` it writes each planned
difficulty and records every change — item, previous and new difficulty, source and time — in
`item_difficulty_changes`. An item an answer moved since the plan is skipped. It runs with
RUN_MIGRATIONS=0: it migrates and syncs nothing. Both engines, the script run as a subprocess
against the test's database.
"""

import os
import pathlib
import subprocess
import sys
import uuid

from tests.integration.conftest import is_postgres, make_student, sql
from tests.integration.test_spec002_d1_startup import database  # noqa: F401  (a fixture)

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")


def _course(repo, difficulties, bank=None):
    """A course with one item per difficulty (`bank_difficulty` = `bank` or the difficulty)."""
    course_id = f"spec008l_recal_{uuid.uuid4().hex[:10]}"
    sql(
        repo,
        "INSERT INTO courses (id, name, block, description) VALUES (?, ?, 'Colegio', '')",
        (course_id, course_id),
    )
    ids = []
    for n, difficulty in enumerate(difficulties):
        item_id = f"{course_id}_{n}"
        sql(
            repo,
            "INSERT INTO items (id, topic, content, options, correct_option, difficulty,"
            " rating_deviation, course_id, bank_difficulty)"
            " VALUES (?, 'Vida', 'Pregunta L', '[\"A\", \"B\"]', 'A', ?, 350, ?, ?)",
            (item_id, float(difficulty), course_id, bank if bank is not None else difficulty),
        )
        ids.append(item_id)
    return course_id, ids


def _attempts(repo, item_id, n, successes, rating=1000.0):
    """`n` valid attempts on `item_id` by one student at `rating`, `successes` of them right."""
    student = make_student(repo)
    for k in range(n):
        sql(
            repo,
            "INSERT INTO attempts (user_id, item_id, is_correct, elo_before, elo_after,"
            " elo_valid, topic) VALUES (?, ?, ?, ?, ?, 1, 'Vida')",
            (student, item_id, k < successes, rating, rating),
        )


def _run(repo, *args):
    env = dict(os.environ)
    env["RUN_MIGRATIONS"] = "0"
    if is_postgres(repo):
        env["DATABASE_URL"] = _PG_URL
        env.pop("MIGRATION_DATABASE_URL", None)
    else:
        env.pop("DATABASE_URL", None)
        env.pop("MIGRATION_DATABASE_URL", None)
        env["DB_PATH"] = repo.db_name
    proc = subprocess.run(
        [sys.executable, "scripts/recalibrate_items.py", *args],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout


def _difficulties(repo, ids):
    return [float(sql(repo, "SELECT difficulty FROM items WHERE id = ?", (i,))[0][0]) for i in ids]


def _changes(repo, ids):
    rows = []
    for item_id in ids:
        rows += [
            (r[0], float(r[1]), float(r[2]), r[3], r[4], r[5] is not None)
            for r in sql(
                repo,
                "SELECT item_id, previous_difficulty, new_difficulty, source, detail, changed_at"
                " FROM item_difficulty_changes WHERE item_id = ? ORDER BY id",
                (item_id,),
            )
        ]
    return rows


def test_spec008_l_a_dry_run_counts_and_writes_nothing(repo):
    """FR-032, US4-AS3 (first half): without `--apply` the script prints counts and writes
    nothing."""
    course, ids = _course(repo, [1000, 1000])
    _attempts(repo, ids[0], 20, 0)  # far too easy at 1000: D* is higher
    _attempts(repo, ids[1], 20, 10)  # right where it is

    output = _run(repo, "--course", course)

    assert "1 planned" in output and "dry run" in output
    assert course in output
    assert _difficulties(repo, ids) == [1000.0, 1000.0]
    assert _changes(repo, ids) == []


def test_spec008_l_apply_records_every_change(repo):
    """FR-032, US4-AS3 (second half): `--apply` writes each planned difficulty and records the
    item, the previous and new difficulty, the source (`dstar`, or `bank` with `--method bank`)
    and the time."""
    course, ids = _course(repo, [1000, 1000])
    _attempts(repo, ids[0], 20, 0)
    _attempts(repo, ids[1], 20, 10)

    output = _run(repo, "--course", course, "--apply")

    [new] = _difficulties(repo, ids[:1])
    assert new == 1645.0  # smoothed share 0.5/21: 1000 + 400·log10(41), rounded
    assert _difficulties(repo, ids[1:]) == [1000.0]
    assert _changes(repo, ids) == [
        (ids[0], 1000.0, 1645.0, "dstar", "20 attempts, 0 successes", True)
    ]
    assert "1 applied" in output

    banked_course, banked = _course(repo, [719, 900], bank=1000)
    _run(repo, "--method", "bank", "--course", banked_course, "--apply")

    assert _difficulties(repo, banked) == [1000.0, 1000.0]
    assert [(c[1], c[2], c[3]) for c in _changes(repo, banked)] == [
        (719.0, 1000.0, "bank"),
        (900.0, 1000.0, "bank"),
    ]


def test_spec008_l_an_item_moved_since_the_plan_is_skipped(repo):
    """FR-032: an answer that moved the item between the plan and the write wins — the change is
    skipped and counted, nothing recorded."""
    course, ids = _course(repo, [1000, 1000])
    sql(repo, "UPDATE items SET difficulty = 1016.5 WHERE id = ?", (ids[0],))  # an answer since

    result = repo.apply_item_difficulty_changes(
        [
            {"item_id": ids[0], "previous": 1000.0, "new": 1500, "detail": None},
            {"item_id": ids[1], "previous": 1000.0, "new": 1400, "detail": None},
        ],
        "dstar",
    )

    assert result == {"applied": 1, "skipped_moved": 1}
    assert _difficulties(repo, ids) == [1016.5, 1400.0]
    assert [c[0] for c in _changes(repo, ids)] == [ids[1]]


def test_spec008_l_the_script_migrates_nothing(database, monkeypatch):  # noqa: F811
    """FR-032, constitution VI (survey B16): against a database at the previous schema version,
    with a bank it has not synced, the script changes neither `schema_versions` nor
    `bank_syncs`."""
    monkeypatch.setenv("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD") or "l-admin")
    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    monkeypatch.setenv("ENVIRONMENT", "development")
    database.build()
    top = database.sql("SELECT MAX(version) FROM schema_versions")[0][0]
    database.sql("DELETE FROM schema_versions WHERE version = ?", (top,))
    database.sql("INSERT INTO bank_syncs (fingerprint) VALUES ('stale')")
    versions = database.sql("SELECT version FROM schema_versions ORDER BY version")
    syncs = database.sql("SELECT id, fingerprint FROM bank_syncs ORDER BY id")

    env = dict(os.environ)
    env.update(database.env)
    env["RUN_MIGRATIONS"] = "0"
    env.pop("MIGRATION_DATABASE_URL", None)
    if database.engine == "sqlite":
        env.pop("DATABASE_URL", None)
    proc = subprocess.run(
        [sys.executable, "scripts/recalibrate_items.py"],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert database.sql("SELECT version FROM schema_versions ORDER BY version") == versions
    assert database.sql("SELECT id, fingerprint FROM bank_syncs ORDER BY id") == syncs
