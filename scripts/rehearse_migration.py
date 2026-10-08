"""
scripts/rehearse_migration.py — rehearse the transfer migration on a restored copy.

Implements docs/transfer.md § 4–6 as one command, so the owner's rehearsal on the real backup
runs the same checks as any earlier rehearsal:

  1. backup     pg_dump of the source database (read-only), unless --dump already exists
  2. readable   pg_restore --list on the dump
  3. restore    into an EMPTY scratch database (local by default)
  4. baseline   legacy state: row counts and content checksums
  5. migrate    scripts/migrate.py against the scratch copy — run 1
  6. verify     reconciliation: approximate baselines with provenance, each equal to exactly one
                legacy row; legacy tables, attempts, exams and item calibration untouched
  7. migrate    run 2 — must change nothing (schema and every table identical to run 1)
  8. smoke      the API on the migrated copy with RUN_MIGRATIONS=0: /api/health, /api/meta/ranks

Usage:
    # dump the source (direct connection, port 5432) and rehearse on a local scratch database
    python scripts/rehearse_migration.py --source-url "$MIGRATION_DATABASE_URL" \\
        --dump pre-transfer-YYYYMMDD.dump --scratch-url postgresql://u:p@localhost:5432/scratch

    # rehearse from a dump taken earlier
    python scripts/rehearse_migration.py --dump pre-transfer-YYYYMMDD.dump \\
        --scratch-url postgresql://u:p@localhost:5432/scratch

Never writes to the source. The scratch database must be empty, must not be the source, and must
be on localhost unless --allow-remote-scratch is given. Needs pg_dump/pg_restore at least as new
as the source server. The dump holds student data: keep it out of the repository.
Exit code 0 only if every check passes.
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from urllib.parse import urlsplit

import psycopg2
from psycopg2.extras import RealDictCursor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
# Pre-existing data the migration must leave exactly as it was (spec 001: legacy rows are read,
# never written; attempts are a log).
UNCHANGED_TABLES = (
    "student_topic_elo",
    "attempts",
    "exam_sessions",
    "procedure_submissions",
    "enrollments",
)
LEGACY_COUNTS = {
    "users": "SELECT COUNT(*) FROM users",
    "users_with_current_elo": "SELECT COUNT(*) FROM users WHERE current_elo IS NOT NULL",
    "attempts": "SELECT COUNT(*) FROM attempts",
    "exam_sessions": "SELECT COUNT(*) FROM exam_sessions",
    "student_topic_elo": "SELECT COUNT(*) FROM student_topic_elo",
}


class Rehearsal:
    def __init__(self):
        self.failures = []
        self.lines = []

    def log(self, msg=""):
        print(msg, flush=True)
        self.lines.append(msg)

    def check(self, ok, label, detail=""):
        self.log(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
        if not ok:
            self.failures.append(label)
        return ok


def _target(url):
    parts = urlsplit(url)
    return (parts.hostname or "", parts.port or 5432, parts.path.lstrip("/"))


def _connect(url, sslmode):
    host, port, db = _target(url)
    parts = urlsplit(url)
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=db,
        user=parts.username,
        password=parts.password,
        sslmode=sslmode,
        cursor_factory=RealDictCursor,
    )


def _scalar(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    return None if row is None else list(row.values())[0]


def _tables(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables"
            " WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY 1"
        )
        return [row["table_name"] for row in cur.fetchall()]


def _checksum(conn, table, columns="t"):
    # Order-independent content fingerprint of a whole table (or of selected columns).
    return _scalar(
        conn,
        f"SELECT md5(COALESCE(string_agg(x, '|' ORDER BY x), '')) FROM"
        f" (SELECT ({columns})::text AS x FROM {table} t) s",
    )


def _columns(conn, table):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns"
            " WHERE table_schema = 'public' AND table_name = %s ORDER BY ordinal_position",
            (table,),
        )
        return [row["column_name"] for row in cur.fetchall()]


def _legacy_checksum(conn, table, cols):
    # Checksum over the columns that existed before migrating: added columns do not count.
    return _checksum(conn, table, ", ".join(f't."{c}"' for c in cols))


def _rows_by_id(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return {row["id"]: tuple(row.values())[1:] for row in cur.fetchall()}


def _snapshot(conn):
    return {
        table: (_scalar(conn, f"SELECT COUNT(*) FROM {table}"), _checksum(conn, table))
        for table in _tables(conn)
    }


def _schema_fingerprint(url):
    out = subprocess.run(
        ["pg_dump", "--schema-only", "--no-owner", "--no-privileges", f"--dbname={url}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    body = [
        ln
        for ln in out.splitlines()
        if ln.strip()
        and not ln.startswith("--")
        and not ln.startswith("\\restrict")
        and not ln.startswith("\\unrestrict")
    ]
    return hashlib.sha256("\n".join(body).encode()).hexdigest()


def _run_migrate(r, scratch_url, sslmode, environment):
    env = dict(os.environ)
    env.update(
        {
            "MIGRATION_DATABASE_URL": scratch_url,
            "DATABASE_URL": scratch_url,
            "DATABASE_SSLMODE": sslmode,
            "ENVIRONMENT": environment,
            "RUN_MIGRATIONS": "1",
        }
    )
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "migrate.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    m = re.search(r"_reconcile_legacy_ratings OK: (\d+) filas", out)
    created = int(m.group(1)) if m else None
    ok = proc.returncode == 0 and "Migraciones completadas." in out
    if not ok:
        r.log(out[-4000:])
    return ok, created


def _smoke(scratch_url, sslmode):
    code = (
        "from fastapi.testclient import TestClient\n"
        "from api.main import app\n"
        "with TestClient(app) as c:\n"
        "    h = c.get('/api/health'); m = c.get('/api/meta/ranks')\n"
        "    ranks = m.json() if m.status_code == 200 else []\n"
        "    ranks = ranks.get('ranks', ranks) if isinstance(ranks, dict) else ranks\n"
        "    print('SMOKE', h.status_code, m.status_code, len(ranks),"
        " m.headers.get('cache-control', ''))\n"
    )
    env = dict(os.environ)
    env.update(
        {
            "DATABASE_URL": scratch_url,
            "DATABASE_SSLMODE": sslmode,
            "RUN_MIGRATIONS": "0",
            "ENVIRONMENT": "development",
        }
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True
    )
    m = re.search(r"SMOKE (\d+) (\d+) (\d+) (.*)", proc.stdout)
    return (m.groups() if m else None), (proc.stdout + proc.stderr)[-2000:]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dump", required=True, help="dump file to create (with --source-url) or use")
    ap.add_argument("--source-url", help="database to back up (read-only; direct port 5432)")
    ap.add_argument("--scratch-url", required=True, help="EMPTY throwaway database to restore into")
    ap.add_argument("--schema", default="public", help="schema to dump (default: public)")
    ap.add_argument("--source-sslmode", default=os.environ.get("DATABASE_SSLMODE", "require"))
    ap.add_argument("--scratch-sslmode", default="prefer")
    ap.add_argument(
        "--environment",
        default="production",
        help="ENVIRONMENT for the migration run (production skips demo seeds)",
    )
    ap.add_argument("--allow-remote-scratch", action="store_true")
    ap.add_argument("--report", help="write the transcript to this file")
    args = ap.parse_args()
    r = Rehearsal()

    scratch = _target(args.scratch_url)
    if args.source_url and _target(args.source_url) == scratch:
        sys.exit("Refusing: the scratch database is the source database.")
    if scratch[0] not in LOCAL_HOSTS and not args.allow_remote_scratch:
        sys.exit(
            f"Refusing: scratch host {scratch[0]!r} is not local (use --allow-remote-scratch)."
        )

    r.log("== 1. Backup")
    if args.source_url:
        if os.path.exists(args.dump):
            sys.exit(f"Refusing to overwrite {args.dump}.")
        src = _connect(args.source_url, args.source_sslmode)
        try:
            server = _scalar(src, "SHOW server_version")
        finally:
            src.close()
        client = subprocess.run(["pg_dump", "--version"], capture_output=True, text=True).stdout
        r.log(f"  source server {server}; {client.strip()}")
        env = dict(os.environ, PGSSLMODE=args.source_sslmode)
        proc = subprocess.run(
            [
                "pg_dump",
                "--format=custom",
                "--no-owner",
                "--no-privileges",
                f"--schema={args.schema}",
                f"--file={args.dump}",
                f"--dbname={args.source_url}",
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        if not r.check(proc.returncode == 0, "pg_dump of the source", proc.stderr.strip()[-500:]):
            return finish(r, args)
    r.check(os.path.exists(args.dump), f"dump file exists ({args.dump})")
    if r.failures:
        return finish(r, args)
    r.log(
        f"  size {os.path.getsize(args.dump):,} bytes; sha256"
        f" {hashlib.sha256(open(args.dump, 'rb').read()).hexdigest()}"
    )

    r.log("== 2. Dump is readable")
    listing = subprocess.run(["pg_restore", "--list", args.dump], capture_output=True, text=True)
    entries = [ln for ln in listing.stdout.splitlines() if ln and not ln.startswith(";")]
    r.check(listing.returncode == 0 and entries, "pg_restore --list", f"{len(entries)} entries")

    r.log("== 3. Restore into the scratch database")
    conn = _connect(args.scratch_url, args.scratch_sslmode)
    try:
        existing = _tables(conn)
    finally:
        conn.close()
    if not r.check(not existing, "scratch database is empty", ", ".join(existing[:5])):
        return finish(r, args)
    env = dict(os.environ, PGSSLMODE=args.scratch_sslmode)
    proc = subprocess.run(
        ["pg_restore", "--no-owner", "--no-privileges", f"--dbname={args.scratch_url}", args.dump],
        env=env,
        capture_output=True,
        text=True,
    )
    errors = [ln for ln in proc.stderr.splitlines() if "error:" in ln.lower()]
    benign = [ln for ln in errors if 'schema "public" already exists' in ln]
    r.check(
        len(errors) == len(benign),
        "pg_restore without errors",
        "; ".join(e for e in errors if e not in benign)[:500] or f"{len(benign)} benign",
    )

    conn = _connect(args.scratch_url, args.scratch_sslmode)
    conn.autocommit = True
    r.log("== 4. Legacy state before migrating")
    before_counts = {k: _scalar(conn, sql) for k, sql in LEGACY_COUNTS.items()}
    for k, v in before_counts.items():
        r.log(f"  {k}: {v}")
    before_cols = {t: _columns(conn, t) for t in _tables(conn)}
    before = {t: _legacy_checksum(conn, t, cols) for t, cols in before_cols.items()}
    users_before = _rows_by_id(conn, "SELECT id, current_elo, rating_deviation FROM users")
    calibration = _rows_by_id(conn, "SELECT id, difficulty, rating_deviation FROM items")
    exam_ids = _scalar(conn, "SELECT COALESCE(MAX(id), 0) FROM exam_sessions")

    r.log("== 5. Migration, run 1")
    ok, created1 = _run_migrate(r, args.scratch_url, args.scratch_sslmode, args.environment)
    r.check(ok, "scripts/migrate.py exits 0 and prints 'Migraciones completadas.'")
    if not ok:
        return finish(r, args)
    r.log(f"  reconciliation created {created1} rows")

    r.log("== 6. Verify reconciliation")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT origin, approximate, COUNT(*) AS n FROM student_course_topic_elo"
            " GROUP BY 1, 2 ORDER BY 1, 2"
        )
        for row in cur.fetchall():
            r.log(f"  origin={row['origin']} approximate={row['approximate']}: {row['n']}")
    reconciled = _scalar(
        conn, "SELECT COUNT(*) FROM student_course_topic_elo" " WHERE origin LIKE 'legacy\\_%'"
    )
    r.check(
        reconciled == created1,
        "reconciled rows equal the rows the run reported",
        f"{reconciled} vs {created1}",
    )
    r.check(
        _scalar(
            conn,
            "SELECT COUNT(*) FROM student_course_topic_elo WHERE origin LIKE"
            " 'legacy\\_%' AND (approximate IS NOT TRUE OR legacy_source_key IS NULL"
            " OR reconciled_at IS NULL)",
        )
        == 0,
        "every reconciled row is approximate, with legacy_source_key and reconciled_at",
    )
    mismatched = _scalar(
        conn,
        """
        SELECT COUNT(*) FROM student_course_topic_elo n
        LEFT JOIN student_topic_elo l ON l.user_id = n.user_id AND l.topic = n.legacy_source_key
        WHERE n.origin LIKE 'legacy\\_%' AND (l.user_id IS NULL
           OR n.current_elo::real <> GREATEST(l.current_elo, 0)::real
           OR n.rd::real <> LEAST(350, GREATEST(30, COALESCE(l.rd, 350)))::real)""",
    )
    # Compared at the legacy column's precision (REAL): the value is carried over as the
    # legacy row shows it, then stored in 8 bytes (research R20).
    r.check(
        mismatched == 0,
        "each baseline equals exactly one legacy row (never summed)",
        f"{mismatched} mismatched",
    )
    for table in UNCHANGED_TABLES:
        if table in before_cols:
            r.check(
                _legacy_checksum(conn, table, before_cols[table]) == before[table],
                f"{table} unchanged (pre-existing columns)",
            )
    users_after = _rows_by_id(conn, "SELECT id, current_elo, rating_deviation FROM users")
    r.check(
        all(users_after.get(i) == v for i, v in users_before.items()),
        "existing users keep current_elo and rating_deviation",
        f"{len(users_after) - len(users_before)} users added",
    )
    changed = sorted(
        t
        for t, cols in before_cols.items()
        if t not in UNCHANGED_TABLES and _legacy_checksum(conn, t, cols) != before[t]
    )
    r.log(f"  other tables whose pre-existing data changed (bank sync, seeds): {changed or 'none'}")
    r.check(
        _scalar(
            conn,
            "SELECT COUNT(*) FROM exam_sessions WHERE id <= %s AND"
            " global_elo_status IS NOT NULL",
            (exam_ids,),
        )
        == 0,
        "pre-existing exam_sessions keep global_elo_status NULL (reported as unknown)",
    )
    after = _rows_by_id(conn, "SELECT id, difficulty, rating_deviation FROM items")
    moved = [i for i, v in calibration.items() if after.get(i) != v]
    r.check(
        not moved,
        "existing items keep difficulty and rating_deviation (calibration)",
        f"{len(moved)} changed; {len(after) - len(calibration)} items added",
    )
    without = _scalar(
        conn,
        """
        SELECT COUNT(DISTINCT l.user_id) FROM student_topic_elo l
        WHERE NOT EXISTS (SELECT 1 FROM student_course_topic_elo n WHERE n.user_id = l.user_id)""",
    )
    r.log(
        f"  students with legacy ratings but no baseline (they will see 'pending diagnostic'):"
        f" {without}"
    )

    r.log("== 7. Migration, run 2 (idempotency)")
    schema1 = _schema_fingerprint(args.scratch_url)
    snap1 = _snapshot(conn)
    ok, created2 = _run_migrate(r, args.scratch_url, args.scratch_sslmode, args.environment)
    r.check(ok, "second run exits 0")
    r.check(created2 == 0, "second run reconciles 0 rows", f"{created2}")
    r.check(_schema_fingerprint(args.scratch_url) == schema1, "schema identical after run 2")
    snap2 = _snapshot(conn)
    changed = sorted(t for t in snap1 if snap1[t] != snap2.get(t))
    r.check(not changed, "every table identical after run 2", ", ".join(changed))

    r.log("== 8. Smoke test on the migrated copy (RUN_MIGRATIONS=0)")
    result, out = _smoke(args.scratch_url, args.scratch_sslmode)
    if result is None:
        r.check(False, "API starts on the migrated copy", out)
    else:
        health, ranks, n, cache = result
        r.check(health == "200", "GET /api/health → 200", health)
        r.check(
            ranks == "200" and n == "16",
            "GET /api/meta/ranks → 200 with 16 ranks",
            f"{ranks}, {n} ranks, Cache-Control: {cache}",
        )
    conn.close()
    return finish(r, args)


def finish(r, args):
    r.log("")
    r.log("RESULT: " + ("PASS" if not r.failures else f"FAIL ({len(r.failures)} checks)"))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write("\n".join(r.lines) + "\n")
    return 0 if not r.failures else 1


if __name__ == "__main__":
    sys.exit(main())
