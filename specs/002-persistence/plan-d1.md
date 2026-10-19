# Plan — spec 002, delivery D1: startup

**Spec**: [spec.md](spec.md) § Deliveries, D1 (US1 … US3; FR-014 … FR-018) · **Branch**:
`002-persistence-d1`, from `redesign` · **Date**: 2026-10-18 · **Status**: for the owner's approval

## Summary

Each start of the API (Render runs `scripts/migrate.py` before uvicorn on every cold start) re-runs
about 95 DDL statements, the item sync (one `UPDATE` per bank item, 2,031 today), the startup
repairs and the legacy reconciliation's scans. D1 records a **schema version** and an **item-bank
fingerprint**: a start that finds both current does only what has work to do (the orphaned PvP
matches). The data repairs leave the start and become scripts; the one non-additive statement runs
only when needed; and a failing migration commits nothing.

## Constitution Check (1.2.0)

| Principle | D1 |
|---|---|
| Dual database (IV, R1) | The same version table, version constant, fingerprint and repair scripts on both engines; every test parametrised over SQLite and PostgreSQL; `db_sync_check.py` |
| Additive migrations (R8) | One new table (`schema_versions`). The `DROP NOT NULL` becomes the one recorded exception, run only while needed (FR-014) |
| Layers (III) | Infrastructure and scripts only; no domain or rating code changes |
| Simplicity and evidence (VII) | One integer version and one fingerprint, no migration framework; the start's cost measured before and after on the rehearsal database (SC-002) |
| Validation and errors | A failed migration stops the start with the step's name (FR-017); nothing is swallowed |
| Security (VI) | The repair scripts print counts only, never rows |

## Design

### Schema version (FR-015, FR-016)

- New table, both engines, created first by `init_db`:
  `schema_versions(version INTEGER PRIMARY KEY, applied_at TIMESTAMP, bank_fingerprint TEXT)`.
  One row per applied version; never updated or removed (append-only).
- A module `src/infrastructure/persistence/schema_version.py` holds `SCHEMA_VERSION` (an integer,
  starting at 1) and `MIGRATION_SOURCES_DIGEST`, the SHA-256 of the source of every function that
  issues DDL (`init_db`, `_migrate_db` and the helpers they call, on both repositories).
- **Keeping the number honest.** A unit test recomputes the digest from the source; if migration
  code changed and `SCHEMA_VERSION` was not raised with a new digest, the test fails with
  «raise SCHEMA_VERSION and record the new digest». So no pull request can change the schema
  without changing the version.
- **Bootstrap**, under the existing migration lock (12345 on PostgreSQL; `BEGIN IMMEDIATE` on
  SQLite):
  1. read `MAX(version)`;
  2. if it equals `SCHEMA_VERSION`, skip `init_db`, `_migrate_db`, the backfills and the seeds that
     already ran (admin, demo, test students only insert what is missing — see § Seeds);
  3. otherwise run `init_db` and `_migrate_db` as today, then insert the new version row **in the
     same transaction** as the DDL (PostgreSQL DDL is transactional; on SQLite the migration runs
     inside one explicit transaction).
- A database with no `schema_versions` table (every existing one) is "version 0": it runs the full
  migration once, exactly as today, and records version 1. No data is read to guess a version.

### Item bank fingerprint (FR-016)

- The fingerprint is the SHA-256 of the sorted list of `(path, file digest)` under `items/bank/`.
- `sync_items_from_bank_folder` runs only when the fingerprint differs from the last row's; after
  a sync, the fingerprint is recorded with a new row (same version), so a bank edited without a
  schema change re-syncs the bank and nothing else (spec § Edge Cases).

### Seeds, reconciliation and orphaned matches

- `_seed_admin`, `_seed_demo_data`, `_seed_test_students` already insert only what is missing; with
  the version current they still run a read to confirm, and write nothing (SC-001 counts writes,
  not reads).
- `_reconcile_legacy_ratings` inserts only rows that are missing; after its first run it writes
  nothing. It stays on every start (cheap scans) until spec 001 retires the legacy rows.
- `expire_stale_pvp_matches` stays on every start: a restart loses the in-memory timers, so closing
  the orphaned matches is real work (spec 001 FR-027). It writes only when such matches exist.

### Repairs become scripts (FR-018)

New directory `scripts/repairs/`, each script read-only by default (`--apply` to write), printing
the count it would change or changed, idempotent:

| Script | Moves out of the start | Today |
|---|---|---|
| `deactivate_users_without_password.py` | deactivating users whose password hash is empty | P:943; S equivalent |
| `rename_duplicate_groups.py` | renaming duplicate `(teacher, name)` groups `-DUP-{id}` and filling `groups.name_normalized` | P:856-895; S equivalent |
| `backfill_prob_failure.py` | `_backfill_prob_failure` | P:1462; S:1141 |

- `groups.name_normalized` and its unique index are part of version 1's migration. On a database
  that still has duplicates, the unique index cannot be created: the migration stops with
  «run scripts/repairs/rename_duplicate_groups.py» and commits nothing (FR-017, FR-018, US2-AS3) —
  the same pattern as spec 001's block CHECK guard (`course_blocks.py`).

### The one R8 exception (FR-014)

- Before the `ALTER TABLE procedure_submissions ALTER COLUMN image_data DROP NOT NULL`, read
  `information_schema.columns.is_nullable` and run it only when it is `NO`. The fact is recorded by
  the version row that applies it. SQLite has no equivalent statement (its column is already
  nullable); `db_sync_check.py`'s balancing comment stays.

### All or nothing (FR-017)

- PostgreSQL: remove the inner `try/except: conn.rollback()` around `UPDATE groups SET
  name_normalized` (P:858-866, the P7 defect); any exception in `_migrate_db` rolls the whole
  transaction back and is raised, so `scripts/migrate.py` exits 1 with the traceback's step name and
  uvicorn does not start (`migrate.py && uvicorn`).
- SQLite: `_migrate_db` opens one explicit transaction (`isolation_level = None` + `BEGIN`), as the
  answer transaction does, and rolls it back on error.

## Tests (written first; each must fail on today's code except the pins)

| Test (both engines unless noted) | Proves |
|---|---|
| `test_spec002_d1_a_current_database_starts_without_ddl_or_writes` — a statement-recording cursor counts DDL and `INSERT/UPDATE/DELETE` on the second start | US1-AS1, FR-016, SC-001 |
| `test_spec002_d1_an_old_database_migrates_once_and_records_the_version` — a database without the table; two starts; one version row; the second start issues no DDL | US1-AS2, FR-015 |
| `test_spec002_d1_a_failing_migration_commits_nothing` — a step forced to fail midway; no new column, no version row; `migrate.py` exits 1 naming it | US1-AS3, FR-017 |
| `test_spec002_d1_a_reactivated_user_without_password_stays_active` | US2-AS1, FR-018 |
| `test_spec002_d1_repair_scripts_report_and_are_idempotent` — each script, dry run then `--apply` twice | US2-AS2, FR-018 |
| `test_spec002_d1_duplicate_groups_stop_the_migration_naming_the_script` | US2-AS3, FR-017, FR-018 |
| `test_spec002_d1_drop_not_null_runs_only_while_needed` (PostgreSQL) — recorded statements | US3-AS1, US3-AS2, FR-014 |
| `test_spec002_d1_a_changed_bank_only_resyncs_the_bank` | spec § Edge Cases, FR-016 |
| `tests/unit/infrastructure/test_spec002_schema_version.py::test_migration_code_changes_raise_the_version` | FR-015 (the version stays honest) |
| Existing `test_migrate_lock.py`, `test_v1_run_migrations.py`, `test_spec001_course_block_constraint.py`, `scripts/rehearse_migration.py` | unchanged behaviour (pins) |

## Measurement (SC-002)

`scripts/rehearse_migration.py` already restores a copy and migrates it twice; it gains a timing
line for each run. Before D1 the second run costs a full migration; after D1 it must cost at most a
tenth. Measured locally on the simulated production database; the owner's `ops/transfer-backup`
rehearsal reports the same lines.

## Rollout

- Deploys with the switch or after it; the first start on production applies version 1 (the full
  migration it applies today) and records it. Nothing to run by hand.
- The repair scripts are the owner's, read-only by default; `docs/transfer.md` lists them for the
  case a migration stops naming one.

## Open points for the owner

None blocking. `SCHEMA_VERSION` starts at 1 and every later schema change raises it by one.
