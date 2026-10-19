# Plan — spec 002, delivery D3: parity checks and documented differences

**Spec**: [spec.md](spec.md) § Deliveries, D3 (US7; FR-040, FR-041; decision N1) · **Branch**:
`002-persistence-d3`, from `redesign` · **Date**: 2026-10-19 · **Status**: approved by the owner (2026-10-19), with N7 and N8 as recommended

## Summary

`scripts/db_sync_check.py` passes, but it checks less than it says:

- **Its DDL comparison is blind since D1.** It compares the lines of `_migrate_db` that contain
  DDL keywords. D1 moved the DDL into `_run_migration` and `init_db`, so it now compares
  **0 statements with 0** on each engine. Before D1 it already missed
  `_add_column_if_not_exists` calls, unique indexes, column types and `init_db` (survey P13).
- **A difference is only a warning**, and it is reported only when the counts differ.

D3 replaces that comparison with two checks that fail:

1. a static one, in the "Paridad DB" job, that reads every migration method of both
   repositories;
2. a runtime one, in "Guardas PostgreSQL", that builds both schemas and compares what the
   databases report.

Every accepted difference is listed, with its reason, in one file. D3 also applies decision N1:
the item sync updates course name and block on PostgreSQL too, and SQLite gets the index it
lacks.

## What the engines differ in today (measured 2026-10-19)

Both repositories were bootstrapped from empty and their catalogues compared (`redesign` after
LuisJRubioH/LevelUp-ELO#82).

| Kind | Difference | D3 |
|---|---|---|
| Tables | none — 32 on each engine | — |
| Column | `procedure_submissions.storage_url` only on PostgreSQL | documented (N1: SQLite has no Storage) |
| Index | `attempts(user_id)` only on PostgreSQL | **added to SQLite** (N1) |
| Index | PostgreSQL has `groups(teacher_id)` twice (`idx_groups_teacher_id`, `idx_groups_teacher`) | documented (N7) |
| Type | `active_exam_sessions.expires_at`, `exam_assignments.starts_at`, `ends_at`: `TEXT` on SQLite, `TIMESTAMP` on PostgreSQL | documented (spec clarification: timestamps come back as `str` on SQLite) |
| Type | `exam_templates.archived`, `student_course_topic_elo.approximate`: `INTEGER` on SQLite, `BOOLEAN` on PostgreSQL | documented (SQLite has no boolean type) |
| Behaviour | the item sync updates an existing course's name and block on SQLite only | **fixed on PostgreSQL** (N1) |
| Seed | test students: 8 students, 7 groups, 41 enrolments on SQLite; 7, 6 and 39 on PostgreSQL (local data only; never in production) | N8 |
| Signatures | none: 146 public methods with the same parameters, names, kinds and defaults (`put_connection` is PostgreSQL's pool) | kept exact (FR-041) |

## Constitution Check (1.2.0)

| Principle | D3 |
|---|---|
| Dual database (IV, R1) | This *is* R1's check: it now fails on what it misses today |
| Additive migrations (R8) | One new SQLite index; nothing dropped (the duplicate PostgreSQL index stays, N7) |
| Simplicity and evidence (VII) | Catalogue introspection, the database's own answer, instead of more text heuristics; one list of accepted differences |
| Layers (III) | Infrastructure, scripts and tests only |

## Design

### Accepted differences, in one place

- `src/infrastructure/persistence/engine_differences.py` holds a list of entries. Each entry has:
  - `kind` (`column`, `index`, `type`, `method`);
  - the object it names;
  - `engines` (where it exists);
  - `reason` (one sentence, with the decision that accepts it).
- Both checks read this file and **fail** in two cases:
  - an undocumented difference;
  - a documented difference that no longer exists, so the list never goes stale.

### Static check: `db_sync_check.py` (FR-040, FR-041; no database needed)

- **Section 3, rewritten.** It parses (`ast`) every method listed in
  `schema_version._MIGRATION_METHODS` on both repositories and collects three things:
  1. each `_add_column_if_not_exists(cursor, table, column, …)` as `table.column`;
  2. each `CREATE TABLE [IF NOT EXISTS] name`;
  3. each `CREATE [UNIQUE] INDEX [IF NOT EXISTS] name ON table(cols)`, as table, columns and
     uniqueness.

  The two sets must match, apart from the accepted differences. A mismatch is an **error** that
  names the object.
- **Section 1, signatures.** The regex over `def …(…)` is replaced by `inspect.signature` on
  both imported classes: parameter names, kinds and defaults. The regex stops at the first `)`,
  so it cannot read a default such as `fields=("a", "b")` and misses everything after it.
- The script takes `--sqlite PATH --postgres PATH`, so a test can run it on edited copies.
- The "Paridad DB" job already installs `requirements.txt`, so importing both classes needs no
  new dependency (verified: psycopg2 is in it).

### Runtime check (FR-040, the ground truth; PostgreSQL)

- `tests/integration/test_spec002_d3_parity.py` bootstraps a throwaway SQLite file and a
  throwaway PostgreSQL database (D1's pattern).
- It reads each catalogue:
  - SQLite: `sqlite_master`, `PRAGMA table_info` and `PRAGMA index_list`/`index_info`;
  - PostgreSQL: `information_schema.columns` and `pg_index`.
- It compares tables, columns, column type families (int, float, text, time, bool, bytes) and
  non-primary indexes (columns, uniqueness). The result must equal the accepted differences
  exactly.
- It runs in "Guardas PostgreSQL", which already runs every integration test against a real
  PostgreSQL.

### N1, applied

- **SQLite: `CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON attempts(user_id)`.** This changes
  migration code, so D1's digest test requires `SCHEMA_VERSION = 2` and the new digest.
  - Every database migrates once more on its next start; the migration is cumulative and
    idempotent, so on PostgreSQL it adds nothing.
  - Then version 2 is recorded.
- **PostgreSQL item sync.** Today a course's row gets `ON CONFLICT (id) DO NOTHING`. It becomes an
  update of `name` and `block` when either changed, as SQLite does, so a renamed course or one
  moved to another block in the bank reaches production. It is written only when something
  changed, so D1's "an unchanged bank writes nothing" still holds: the sync does not run at all
  then.

## Tests (written first; each [CHANGE] test fails on today's code)

| Test | Proves |
|---|---|
| `tests/unit/scripts/test_spec002_d3_db_sync_check.py::test_a_column_added_to_one_engine_fails` — `db_sync_check.py` on copies where one repository gains `_add_column_if_not_exists(cursor, "users", "d3_probe", "TEXT")`: exit 1 naming `users.d3_probe` | US7-AS1, FR-040 |
| `…::test_an_index_or_unique_index_on_one_engine_fails` (parametrised: index, unique index) | US7-AS1, FR-040 |
| `…::test_a_parameter_after_a_tuple_default_differs_fails` — a renamed parameter after a `("a", "b")` default, which the regex misses | US7-AS2, FR-041 |
| `…::test_the_repositories_pass` and `…::test_a_stale_accepted_difference_fails` | the list stays exact |
| `tests/integration/test_spec002_d3_parity.py::test_both_engines_build_the_same_schema` (PostgreSQL) | FR-040 at runtime; the SQLite index of N1 |
| `tests/integration/test_spec002_d3_parity.py::test_item_sync_updates_course_name_and_block` (both engines) | N1 |
| D1's `test_migration_code_changes_raise_the_version` | the version raised to 2 |

## Rollout

- `SCHEMA_VERSION` goes from 1 to 2. The first start after deploy runs the cumulative migration
  once, then records version 2.
- On PostgreSQL the only effect is the course sync: names and blocks from the bank overwrite those
  in the database. Today they already match, so no row changes until the bank changes.

## Owner decisions (2026-10-19)

- **N7 — the duplicate PostgreSQL index on `groups(teacher_id)`.** **Approved: keep it and
  document it**. Dropping it is not additive (R8). It costs a little write time on a small table.
  The alternative is one `DROP INDEX` as a second recorded exception to R8, the way FR-014 is
  recorded.
- **N8 — the test-student seed differs** (8 against 7 students on a fresh database, local data
  only). **Approved: align PostgreSQL to SQLite in D3**, with the parity test comparing the seed
  counts. The alternative is to document it as accepted.
