# Tasks — spec 002, delivery D1 (startup)

**Plan**: [plan-d1.md](plan-d1.md) (approved by the owner, 2026-10-18). Every D1 requirement is
`[CHANGE]`: its test is written first and must fail on the unchanged code, then pass with its
implementation. The `[AS-IS]` pins of delivery A that the startup touches (FR-010, FR-011) must stay
green throughout.

`[P]` marks tasks that can run in parallel with the others of their phase.

## Deviations from the plan, decided while writing the tasks

- The bank fingerprint lives in its own append-only table, `bank_syncs (id, fingerprint,
  synced_at)`, not as a column of `schema_versions`: a bank synced twice under one schema version
  needs two rows, and `schema_versions` has one row per version.
- `_migrate_db` stays cumulative: a database behind the current version re-runs the whole
  (idempotent) migration and records the new version, so an index skipped once (spec 001
  FR-024a's, while duplicates exist) is retried with the next version.

## Phase 1 — Setup

- [x] T001 `tests/integration/statement_recorder.py`: a helper that wraps a repository's
  connections (both engines) and records each statement with its row count, so a test can count the
  DDL and the rows written by a start

## Phase 2 — Pin current behaviour (blocking)

- [x] T002 Re-run the delivery A pins of the bootstrap on the unchanged code and record the green
  run here: `test_migrate_lock.py`, `test_v1_run_migrations.py`,
  `test_spec001_course_block_constraint.py`, `test_seed_test_students.py` — 35 passed on both
  engines (2026-10-18), on a database already migrated; see the T002 note above for a fresh one

## Phase 3 — Tests first (each must fail on the unchanged code)

All in `tests/integration/test_spec002_d1_startup.py`, both engines, unless noted.

- [x] T003 [P] [US1] A second start against a current database issues no DDL and writes no row
  (US1-AS1, FR-016)
- [x] T004 [P] [US1] A database without `schema_versions` migrates once and records version 1; the
  next start issues no DDL (US1-AS2, FR-015)
- [x] T005 [P] [US1] A migration step forced to fail commits nothing — no new column, no version
  row — and raises naming the step; `scripts/migrate.py` exits 1 (US1-AS3, FR-017)
- [x] T006 [P] [US2] A user without a password hash whom the admin reactivated stays active after a
  start (US2-AS1, FR-018)
- [x] T007 [P] [US2] Each repair script reports a count in a dry run, changes rows with `--apply`,
  and reports 0 on a second `--apply` (US2-AS2, FR-018)
- [x] T008 [P] [US2] Duplicate group names, or names without their normalised form, stop the
  migration with an error naming `scripts/repairs/rename_duplicate_groups.py`; nothing is committed
  (US2-AS3, FR-017, FR-018)
- [x] T009 [P] [US3] PostgreSQL only: the `DROP NOT NULL` is issued only while `image_data` is
  `NOT NULL` (US3-AS1, US3-AS2, FR-014)
- [x] T010 [P] An edited bank re-syncs the bank and records its fingerprint, and nothing else runs;
  an unchanged bank is not re-synced (spec § Edge Cases, FR-016)
- [x] T011 [P] `tests/unit/infrastructure/test_spec002_schema_version.py`: the digest of the
  migration code matches the one recorded with `SCHEMA_VERSION` (FR-015)

## Phase 4 — Implementation

- [x] T012 `src/infrastructure/persistence/schema_version.py`: `SCHEMA_VERSION`,
  `MIGRATION_SOURCES_DIGEST`, `migration_sources_digest()`, `bank_fingerprint(bank_dir)` (T011)
- [x] T013 Both repositories: `schema_versions` and `bank_syncs` (additive, R8); `_bootstrap_schema`
  reads the version and skips `init_db` and `_migrate_db` when current; `_migrate_db` records the
  version in its own transaction; the bank is synced only when its fingerprint changed (T003, T004,
  T010)
- [x] T014 Both repositories: `_migrate_db` all or nothing — PostgreSQL drops the inner
  `rollback`; SQLite runs it in one explicit transaction (T005)
- [x] T015 Both repositories: the startup repairs leave `_migrate_db` and the bootstrap
  (`_backfill_prob_failure` included) and become `repair_*` methods; the migration stops with
  `MigrationNeedsRepair` naming the script when groups need it; `scripts/repairs/*.py` (T006 … T008)
- [x] T016 PostgreSQL: the `DROP NOT NULL` behind `information_schema.columns.is_nullable` (T009)
- [x] T017 `docs/transfer.md` and AGENTS.md § Database: the bootstrap order, the version, the repair
  scripts

## Phase 5 — Close

- [x] T018 Traceability: every D1 row filled; D1 `closed`; `check_traceability.py`, the full suite
  on both engines, `db_sync_check.py`, black and flake8
