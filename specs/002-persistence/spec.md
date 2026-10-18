# Feature Specification: Persistence

**Feature Branch**: `002-persistence` (one branch per delivery once implementation starts)

**Created**: 2026-10-18

**Status**: Approved by the owner, with the recommendations of N1 … N6 (2026-10-18). Written from the as-is survey
(`docs/sdd/persistence-survey.md`, LuisJRubioH/LevelUp-ELO#12) and the owner's decisions of
2026-10-18 (its § 7). Nothing in deliveries D1 … D3 is implemented.

**Input**: Roadmap M2 (`docs/sdd/roadmap.md`): the repository contract, the parity of the two
engines, additive migrations, the pool, locks and Storage paths; follow-up F-3.

**Outcome served** (constitution VIII): the application starts fast, never loses or rewrites data
behind anyone's back, and keeps answering while the database is slow; the engine used in
development behaves like production's under the same tests.

## Code Scope *(mandatory)*

- `src/infrastructure/persistence/` — both repositories: schema, migrations, bootstrap, pool,
  transactions (shared with spec 001, which owns the rating writers' arithmetic)
- `src/infrastructure/storage/` — Supabase Storage client and safe paths
- `src/application/interfaces/repositories.py` — the repository contract
- `scripts/migrate.py` — the deployed migration step
- `scripts/db_sync_check.py` — the textual parity check
- `api/dependencies.py` — engine choice and one instance per process
- `api/routers/ai.py` — repository calls from asynchronous handlers
- `api/websocket/notifications.py` — repository calls from the notification socket

## Deliveries *(this spec is delivered in steps)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it closed and fills all its rows.

| Delivery | Content | State |
|---|---|---|
| **A** | As-is pins: what persistence already guarantees, each requirement tied to a test | in progress |
| **D1** | Startup: a schema version so a start with nothing to do does nothing; repairs as scripts; the one R8 exception guarded; a failed migration commits nothing | planned |
| **D2** | Connections and the event loop: warm idle connections, a real liveness check, no repository call blocking an asynchronous handler, one round trip per read | planned |
| **D3** | Parity checks and documented differences between the engines | planned |

## Clarifications

### Session 2026-10-18 (owner decisions on the survey, § 7)

- Q: Which engine is the contract? → A: PostgreSQL, production's engine, is the reference. SQLite is
  a development engine that must pass the same tests. Parity is proven by the tests that run on
  both engines (the `repo` and `client` fixtures), not by identical internals.
- Q: Precision (survey P2, P3 = roadmap F-3)? → A: accepted and documented. PostgreSQL `REAL`
  columns keep about 7 significant digits — a drift of about 0.001 points after 10,000 updates,
  far below the whole-number display — and `attempts.difficulty` is an integer column on both
  engines, so PostgreSQL rounds the history's difficulty (up to 0.5 points). No new columns.
- Q: Foreign keys (P4)? → A: relations stay enforced by code, and this is documented. Before any
  foreign key is declared, a read-only count of orphans in production.
- Q: The `DROP NOT NULL` that runs on every start (P5)? → A: it runs only while the column is still
  `NOT NULL`, and is recorded as the one accepted exception to AGENTS R8 (FR-014).
- Q: Startup repairs and versioning (P6, P7, cold starts)? → A: an additive schema-version table so
  a start with nothing to do does nothing; one-off data repairs move to scripts (FR-015 … FR-018).
- Q: The lost rating update (P1)? → A: fixed as a spec 001 follow-up (LuisJRubioH/LevelUp-ELO#79):
  every rating writer locks its students first. This spec pins it (FR-026).
- Q: Pool, asynchronous boundary and round trips (P8, P9, P20)? → A: inside this spec, with
  measurements (delivery D2).

### State of the survey's findings on 2026-10-18

The survey read `redesign @ 7c2d388` (2026-10-09). Since then: P1 fixed (LuisJRubioH/LevelUp-ELO#79);
P10 fixed (the teacher's image falls back to the row, roadmap F-8); P12 fixed (semillero test
students enrolled, roadmap F-6); the path part of P21 fixed (roadmap F-7); the procedure upload and
analysis no longer block the event loop (`asyncio.to_thread`), part of P9; P18's duplicate
procedures are prevented by spec 001's block 7. Still present and verified on 2026-10-18: P5 (the
`DROP NOT NULL`), P6 (startup repairs), P7 (a `rollback` inside `_migrate_db` after a failed
`UPDATE groups`), P8 (`minconn=1`, the probe `conn.isolation_level`), P9 in `api/routers/ai.py`
(`get_item_by_id` inside `async def socratic`) and `api/websocket/notifications.py`
(`get_user_by_id`, `get_groups_by_teacher`), P18's URL pattern, P20 and P21's log line.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A restart with nothing to migrate is quick and writes nothing (Priority: P1) — D1

Render restarts the API on every cold start. Today each start re-runs about 95 DDL statements, one
update per bank item and the startup repairs. With a schema version, a start that finds the schema
current does nothing but check it.

**Why this priority**: every cold start pays it, and every needless write is a chance to change
data nobody asked to change.

**Independent Test**: bootstrap a database, then start again on both engines and count the DDL and
data statements issued.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a database already at the current schema version, an unchanged item bank
   and no PvP match left active, **When** the migration step runs, **Then** it issues no DDL and
   writes no data, and the web process starts.
2. **US1-AS2** — **Given** a database at an older version, **When** the migration step runs,
   **Then** it applies the missing steps once, records the new version, and a second run changes
   nothing.
3. **US1-AS3** — **Given** a migration whose statement fails, **When** the migration step runs,
   **Then** nothing of that migration is committed, the error names the step, and the web process
   does not start.

### User Story 2 - Data is repaired only on purpose (Priority: P2) — D1

Today each start deactivates users with an empty password hash, renames duplicate groups, fills
`groups.name_normalized` and rewrites `prob_failure` for every attempt of a user who has one empty.
Repairs become scripts the owner runs knowingly, each reporting what it changed.

**Why this priority**: a repair that runs on every start can undo an administrator's decision (for
example, a user reactivated on purpose).

**Independent Test**: start twice over data that a repair would change; then run the repair script
twice.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** a user with an empty password hash whom the admin reactivated, **When**
   the API starts, **Then** the user stays active.
2. **US2-AS2** — **Given** data a repair applies to, **When** its script runs, **Then** it reports
   the rows it changed; a second run reports 0.
3. **US2-AS3** — **Given** a migration that needs data only a repair produces (duplicate group
   names before their unique index), **When** the migration step runs, **Then** it stops with an
   error naming the repair script and changes nothing.

### User Story 3 - The schema only grows (Priority: P2) — D1

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** `procedure_submissions.image_data` already nullable, **When** the
   migration step runs, **Then** no `ALTER … DROP NOT NULL` is issued.
2. **US3-AS2** — **Given** an old database where `image_data` is still `NOT NULL`, **When** the
   migration step runs, **Then** the column becomes nullable once and the change is recorded with
   the schema version.

### User Story 4 - A slow database does not freeze other requests (Priority: P2) — D2

**Why this priority**: the API is one process (AGENTS R18); a synchronous database call inside an
asynchronous handler stops every other request and socket while it waits.

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** a repository call that takes seconds, **When** KatIA's chat or the
   notification socket makes it, **Then** other requests are answered meanwhile.
2. **US4-AS2** — **Given** an exhausted pool, **When** an asynchronous handler waits for a
   connection, **Then** the event loop is not blocked while it waits.

### User Story 5 - Reads are cheap and connections stay healthy (Priority: P3) — D2

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** a repository method that only reads, **When** it runs on PostgreSQL,
   **Then** it costs one round trip to the database (no `BEGIN` and `ROLLBACK` around it).
2. **US5-AS2** — **Given** a pooled connection the server has closed, **When** a request takes it,
   **Then** the system replaces it and the request succeeds.
3. **US5-AS3** — **Given** a burst of concurrent requests, **When** they finish, **Then** idle
   connections up to the configured minimum stay open for the next ones, and never more than 5
   are open.

### User Story 6 - What already holds keeps holding (Priority: P1) — A

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** an answer between its read and its write, **When** a procedure is graded
   or a PvP match finishes for the same student, **Then** both effects remain (spec 001 R15).
2. **US6-AS2** — **Given** another session holding a bootstrap lock, **When** `scripts/migrate.py`
   runs, **Then** it exits 1 naming the skipped step and the web process does not start.
3. **US6-AS3** — **Given** `RUN_MIGRATIONS=0`, **When** a repository is built, **Then** it writes
   nothing.
4. **US6-AS4** — **Given** Storage fails on download, **When** the teacher opens a procedure,
   **Then** the image is served from the row.

### User Story 7 - The parity check catches what it claims (Priority: P3) — D3

**Acceptance Scenarios**:

1. **US7-AS1** — **Given** a column, index or unique index added to one engine's migration only,
   **When** `db_sync_check.py` runs, **Then** it fails naming it.
2. **US7-AS2** — **Given** a public method whose parameters differ between the engines, **When**
   the check runs, **Then** it fails naming it.

### Edge Cases

- **Two instances start at once** (a deploy overlapping the old process): the bootstrap locks keep
  today's behaviour — the one without the lock skips and reports (FR-011); the schema version is
  written inside the same transaction as the steps it records.
- **A version recorded but a step missing** (a database changed by hand): the migration step trusts
  the version; `scripts/rehearse_migration.py` and the repair scripts are the way to check, not the
  start.
- **SQLite with two processes** (local development): no advisory locks exist; the schema version
  makes the second start a no-op instead of a second full run.
- **The item bank changed but not the schema** (new or edited items): the start syncs the bank and
  records its new fingerprint; nothing else runs.

## Requirements *(mandatory)*

### Functional Requirements

**Engine and contract (A)**

- **FR-001** [AS-IS]: Where `DATABASE_URL` is set, the system shall use PostgreSQL; otherwise it
  shall use SQLite.
- **FR-002** [AS-IS]: The system shall build one repository instance per process (AGENTS R12).
- **FR-003** [AS-IS]: The system shall offer every repository method the services call, with the
  same parameter names, on both engines.

**Bootstrap and migrations (A, D1)**

- **FR-010** [AS-IS]: While `RUN_MIGRATIONS` is `0`, the system shall write nothing when it builds a
  repository.
- **FR-011** [AS-IS]: If another session holds a bootstrap step's lock, then the system shall skip
  that step and report it, and `scripts/migrate.py` shall exit 1 so the web process does not start.
- **FR-012** [AS-IS]: Where `ENVIRONMENT` is `production`, the system shall seed neither demo data
  nor test students.
- **FR-013** [AS-IS]: The system shall change the schema only by adding tables, columns and indexes,
  idempotently, on both engines (AGENTS R8), with the single exception of FR-014.
- **FR-014** [CHANGE]: When the schema is migrated, the system shall make
  `procedure_submissions.image_data` nullable only while it is still `NOT NULL`, and record that
  change with the schema version. *(Today the `ALTER … DROP NOT NULL` runs on every start.)*
- **FR-015** [CHANGE]: The system shall record the schema version a database is at, in an additive
  table, on both engines.
- **FR-016** [CHANGE]: When the migration step finds the database at the current schema version and
  the item bank unchanged since its last sync, the system shall issue no DDL and write no data,
  except closing the PvP matches a restart left active (spec 001 FR-027). *(Today every start
  re-runs every step, the item sync and the repairs.)*
- **FR-017** [CHANGE]: If any statement of a migration fails, then the system shall commit nothing
  of that migration, stop with an error naming the step, and not start the web process. *(Today a
  failed `UPDATE groups` is rolled back inside `_migrate_db`, which also discards the DDL issued
  before it, and the rest is committed.)*
- **FR-018** [CHANGE]: The system shall run no data repair at start: deactivating users with an
  empty password hash, renaming duplicate groups, filling `groups.name_normalized` and rewriting
  `prob_failure` become scripts that report the rows they change and change nothing on a second
  run. If a migration needs data a repair produces, then the migration shall stop with an error
  naming that script.

**Connections and the event loop (A, D2)**

- **FR-020** [AS-IS]: The system shall keep at most 5 PostgreSQL connections open per process
  (AGENTS R4).
- **FR-021** [AS-IS]: The system shall return every PostgreSQL connection to the pool after use,
  never close it from a repository method (AGENTS R4).
- **FR-022** [CHANGE]: The system shall keep idle connections open up to a configured minimum
  between requests, never exceeding FR-020's limit. *(Today `minconn=1`: every concurrent checkout
  beyond the first opens a new TLS connection.)*
- **FR-023** [CHANGE]: If a pooled connection is no longer usable, then the system shall replace it
  before handing it to a caller. *(Today the probe reads a client-side attribute that does not
  detect a closed connection.)*
- **FR-024** [CHANGE]: The system shall make no repository or Storage call synchronously from an
  asynchronous request or socket handler; such calls run in a worker thread (AGENTS R17). *(Today:
  `api/routers/ai.py`, KatIA's chat; `api/websocket/notifications.py`, the room check.)*
- **FR-025** [CHANGE]: When a repository method only reads, the system shall run it on PostgreSQL in
  one round trip, without opening and closing a transaction around it. *(Today each read costs
  about three: `BEGIN`, the query and the pool's `ROLLBACK`.)*
- **FR-026** [AS-IS]: Every rating writer shall lock its students' rows, in id order, before it
  reads or writes a rating, so that no writer overwrites another's effect (spec 001 R15).

**Storage (A)**

- **FR-030** [AS-IS]: The system shall store a procedure file's Storage location as a relative path
  inside the student's folder, never a URL (AGENTS R9).
- **FR-031** [AS-IS]: If downloading a procedure's file from Storage fails, then the system shall
  serve the bytes kept in its row.
- **FR-032** [AS-IS]: If uploading a procedure's file to Storage fails, then the system shall keep
  its bytes in the row and a local copy inside `data/uploads/procedures`.

**Parity checks (D3)**

- **FR-040** [CHANGE]: The system's parity check shall fail when a table, column, index or unique
  index is migrated on one engine only. *(Today it compares line counts and misses
  `_add_column_if_not_exists` calls and unique indexes.)*
- **FR-041** [CHANGE]: The system's parity check shall fail when a public repository method's
  parameters differ between the engines.

### Key Entities

- **Schema version**: the version a database's schema is at and when each step was applied; one
  row per applied version, never updated or removed.
- **Repair script**: a one-off data change run on purpose, with a count of the rows it changes and
  no effect on a second run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A start against a database at the current version issues 0 DDL statements and 0 data
  writes, counted on both engines.
- **SC-002**: A start against a current PostgreSQL database takes at most a tenth of today's
  migration time, measured on the rehearsal database before and after D1.
- **SC-003**: A read-only repository method costs 1 round trip on PostgreSQL, measured through a
  counting proxy as in the survey (P20).
- **SC-004**: While a repository call in an asynchronous handler takes 2 s, another request is
  answered within its normal time.
- **SC-005**: Every test of this spec that runs on both engines passes on both.

## Assumptions

- PostgreSQL is production's engine (Supabase, free tier: at most 5 connections per process).
- SQLite is for development and tests; nothing in production depends on it.
- Measurements of D2 use a local PostgreSQL with a delaying proxy, as the survey did; production
  numbers are not measured from agents (constitution: agents never touch production).
- The orphan count before any foreign key (clarification P4) is an operational step for the owner,
  read-only, like the counts of spec 001 block 7.

## New Decisions and Contradictions

| # | Finding | Recommendation |
|---|---|---|
| N1 | P11: engine differences beyond types — `storage_url` only on PostgreSQL; SQLite's item sync updates a course's name and block, PostgreSQL's only inserts; extra indexes on PostgreSQL. | **Approved** (owner, 2026-10-18): Make the item sync update name and block on PostgreSQL too (the bank is the source); keep `storage_url` PostgreSQL-only and documented (SQLite has no Storage); add the missing indexes to SQLite. |
| N2 | P14: the contract declares 27 methods; routers call 98 more directly. | **Approved** (owner, 2026-10-18): Leave the contract as is in this spec; each spec that touches a router adds the methods it uses. |
| N3 | P15: database errors read as user errors — a failed password re-hash as «invalid credentials», any integrity error on registration as «username exists», a profile read error as 401/404; advisory-unlock failures swallowed. | **Approved** (owner, 2026-10-18): Answer a database error as a server error (500, logged without user data); keep the user messages for the user's mistakes only. |
| N4 | P16: on SQLite, an exception leaks its connection until garbage collection. | **Approved** (owner, 2026-10-18): Close every SQLite connection in `finally` (development only, low priority). |
| N5 | P18: a `DATABASE_URL` with `?query` parses into the database name. | **Approved** (owner, 2026-10-18): Refuse to start with an error naming the problem. |
| N6 | P21: the procedure upload logs the exercise id as typed. | **Approved** (owner, 2026-10-18): Log no user-typed text; log ids only. |

## Out of Scope *(mandatory)*

- Rating arithmetic and which writer moves which rating — spec 001.
- Identity and access rules — spec 004; the PvP match lifecycle — spec 007; the item bank's format
  and calibration — spec 008.
- New columns for precision (decided: accepted and documented) and declaring foreign keys before
  the orphan count.
- Raising the pool above 5 connections or running more than one process (AGENTS R18).
- V1 (Streamlit) beyond keeping it working: frozen.

## Traceability *(mandatory)*

Rows of delivery A cite the tests that already pin the behaviour; the rest are filled by the
pull request that closes their delivery.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | D1 | `PENDING` |
| US1-AS2 | D1 | `PENDING` |
| US1-AS3 | D1 | `PENDING` |
| US2-AS1 | D1 | `PENDING` |
| US2-AS2 | D1 | `PENDING` |
| US2-AS3 | D1 | `PENDING` |
| US3-AS1 | D1 | `PENDING` |
| US3-AS2 | D1 | `PENDING` |
| US4-AS1 | D2 | `PENDING` |
| US4-AS2 | D2 | `PENDING` |
| US5-AS1 | D2 | `PENDING` |
| US5-AS2 | D2 | `PENDING` |
| US5-AS3 | D2 | `PENDING` |
| US6-AS1 | A | `tests/integration/test_spec001_concurrent_rating_writers.py::test_spec001_a_procedure_graded_during_an_answer_keeps_its_delta`<br>`tests/integration/test_spec001_concurrent_rating_writers.py::test_spec001_a_pvp_result_applied_during_an_answer_keeps_its_delta` |
| US6-AS2 | A | `tests/integration/test_migrate_lock.py::test_migrate_fails_and_blocks_the_web_process_when_a_lock_is_held` |
| US6-AS3 | A | `tests/integration/test_v1_run_migrations.py::test_v1_with_run_migrations_0_creates_nothing` |
| US6-AS4 | A | `tests/integration/test_teacher_image_fallback.py::test_image_falls_back_to_the_row_when_storage_fails` |
| US7-AS1 | D3 | `PENDING` |
| US7-AS2 | D3 | `PENDING` |
| FR-001 | A | `PENDING` |
| FR-002 | A | `PENDING` |
| FR-003 | A | `tests/unit/application/test_repository_contracts.py::test_every_declared_method_exists_in_both_engines`<br>`tests/unit/application/test_repository_contracts.py::test_declared_signatures_match_the_implementation`<br>`tests/unit/application/test_repository_contracts.py::test_everything_the_service_calls_is_declared` |
| FR-010 | A | `tests/integration/test_v1_run_migrations.py::test_v1_with_run_migrations_0_creates_nothing` |
| FR-011 | A | `tests/integration/test_migrate_lock.py::test_migrate_fails_and_blocks_the_web_process_when_a_lock_is_held`<br>`tests/integration/test_migrate_lock.py::test_migrate_succeeds_and_starts_the_web_process_without_contention` |
| FR-012 | A | `PENDING` |
| FR-013 | A | `PENDING` |
| FR-014 | D1 | `PENDING` |
| FR-015 | D1 | `PENDING` |
| FR-016 | D1 | `PENDING` |
| FR-017 | D1 | `PENDING` |
| FR-018 | D1 | `PENDING` |
| FR-020 | A | `PENDING` |
| FR-021 | A | `PENDING` |
| FR-022 | D2 | `PENDING` |
| FR-023 | D2 | `PENDING` |
| FR-024 | D2 | `PENDING` |
| FR-025 | D2 | `PENDING` |
| FR-026 | A | `tests/integration/test_spec001_concurrent_rating_writers.py::test_spec001_a_procedure_graded_during_an_answer_keeps_its_delta`<br>`tests/integration/test_spec001_concurrent_rating_writers.py::test_spec001_a_pvp_result_applied_during_an_answer_keeps_its_delta`<br>`tests/integration/test_elo_single_source.py::test_concurrent_answers_on_the_same_item_compose_serially` |
| FR-030 | A | `tests/integration/test_procedure_upload_paths.py::test_storage_key_stays_in_the_students_folder`<br>`tests/unit/infrastructure/test_storage_paths.py::test_no_separator_or_dot_survives` |
| FR-031 | A | `tests/integration/test_teacher_image_fallback.py::test_image_falls_back_to_the_row_when_storage_fails` |
| FR-032 | A | `tests/integration/test_procedure_upload_paths.py::test_local_fallback_file_stays_in_the_uploads_folder` |
| FR-040 | D3 | `PENDING` |
| FR-041 | D3 | `PENDING` |
