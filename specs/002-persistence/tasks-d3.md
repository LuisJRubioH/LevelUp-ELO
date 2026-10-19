# Tasks — spec 002, delivery D3 (parity checks and documented differences)

**Plan**: [plan-d3.md](plan-d3.md) (approved by the owner, 2026-10-19, N7 = keep and document the
duplicate PostgreSQL index, N8 = align the PostgreSQL test-student seed to SQLite). FR-040 and
FR-041 are `[CHANGE]`: their tests fail on the unchanged code first.

## Found while writing the tests

- The PostgreSQL seed lacks `estudiante_concursos_1` and its group: it keeps its own copy of the
  student list, which `seed_test_students.py` (SQLite) extended. N8 makes PostgreSQL read the same
  list.

- The static check counts indexes by name: PostgreSQL issues
  `CREATE INDEX IF NOT EXISTS idx_attempts_user_topic_ts` in both `init_db` and `_run_migration`,
  which makes one index, not two.
- Rollout: the plan said production course rows already match the bank; that was not verified,
  and the plan now says so.

## Phase 1 — Tests first (all fail on the unchanged code)

- [x] T001 [P] `tests/unit/scripts/test_spec002_d3_db_sync_check.py`: a column, an index, a unique
  index on one engine, a parameter after a tuple default, a stale accepted difference → exit 1
  naming it; the repositories as they are → exit 0 (US7-AS1, US7-AS2, FR-040, FR-041)
- [x] T002 [P] `tests/integration/test_spec002_d3_parity.py::test_both_engines_build_the_same_schema`:
  catalogues and seed counts equal apart from the accepted differences (FR-040, N1, N7, N8)
- [x] T003 [P] `…::test_item_sync_updates_course_name_and_block`, both engines (N1)

## Phase 2 — Implementation

- [x] T004 `src/infrastructure/persistence/engine_differences.py`: the accepted differences, the
  `Catalogue` model and `unexplained()` (static and runtime)
- [x] T005 `scripts/db_sync_check.py`: `--sqlite/--postgres`; section 1 by `inspect.signature`;
  section 3 by `ast` over `_MIGRATION_METHODS`, failing as errors (T001)
- [x] T006 SQLite `idx_attempts_user_id`; `SCHEMA_VERSION = 2` and the new digest (T002)
- [x] T007 PostgreSQL course sync updates name and block when they changed (T003)
- [x] T008 PostgreSQL `_seed_test_students` reads the shared student list, concursos included (T002)
- [x] T009 AGENTS.md R1: what the check covers and where accepted differences live

## Phase 3 — Close

- [x] T010 Traceability: US7-AS1, US7-AS2, FR-040, FR-041 filled; D3 `closed`; full suite on both
  engines, `db_sync_check.py`, black, flake8, `check_traceability.py`
