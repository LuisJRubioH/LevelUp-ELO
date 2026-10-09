# Persistence — as-is survey (spec 002 input)

Read-only survey of `redesign @ 7c2d388`, 2026-10-09. Input for `specs/002-persistence/spec.md`
(roadmap M2: repository contract, SQLite/PostgreSQL parity, additive migrations, pool, locks,
storage paths; follow-up F-3).

Each finding cites code at that commit (`S` = `src/infrastructure/persistence/sqlite_repository.py`,
`P` = `src/infrastructure/persistence/postgres_repository.py`). **Verified** = read in the code and,
where marked, reproduced on a local PostgreSQL 16 or an in-memory SQLite. **Inferred** = reasoned
from the code, not reproduced. Nothing here was run against production.

## 1. Where things live

| Concern | File |
|---|---|
| Repository contract (5 `Protocol`s, 27 methods) | `src/application/interfaces/repositories.py` |
| Contract check (names and parameter names, both ways) | `tests/unit/application/test_repository_contracts.py` |
| Engines (125 / 126 public methods) | `S` (4,830 lines), `P` (5,580 lines) |
| Engine choice and one instance per process | `api/dependencies.py:30-54` (V2), `src/interface/streamlit/app.py:50-76` (V1) |
| Schema bootstrap | `_bootstrap_schema` (S:39, P:231) → `init_db` → `_migrate_db` → seeds → backfill → item sync → reconciliation → stale PvP expiry |
| Deployed migration step | `scripts/migrate.py` (forces `RUN_MIGRATIONS=1`, exits 1 if a locked step was skipped) |
| Block CHECK guard (read-only, FR-028n) | `src/infrastructure/persistence/course_blocks.py` |
| Test-student seed | `src/infrastructure/persistence/seed_test_students.py` (SQLite) and `P:3488-3624` |
| Textual parity check (CI job "Paridad DB") | `scripts/db_sync_check.py` |
| Two-engine test fixture | `tests/integration/conftest.py:51-72` (`repo`, params `sqlite`/`postgres`) |
| File storage | `src/infrastructure/storage/supabase_storage.py`, `P:4319-4421` (procedure upload) |
| Bucket backup / restore | `scripts/backup_storage_bucket.py`, `scripts/restore_storage_bucket.py` |

## 2. Actual behaviour

**Engine choice.** `DATABASE_URL` set → `PostgresRepository`, else `SQLiteRepository`. SQLite is
the local and test engine; production runs PostgreSQL (Supabase). The two classes have the same
public method names and argument lists; the only differences are `__init__(db_name=None)` vs
`__init__()` and P's extra `put_connection` (P:311).

**Contract.** `repositories.py` declares 27 methods in five protocols (student, teacher, rating
read, admin, and their union). The contract test checks that each exists on both classes with the
same *parameter names* and that every `self.repository.X` call in the three services is declared.
Routers call the repository directly, so **98 public methods are in no interface**.

**Bootstrap** (same order on both engines; S:36-58, P:226-265). The whole bootstrap is gated by
`RUN_MIGRATIONS` (default on); with it off the constructor writes nothing. `_seed_demo_data` and
`_seed_test_students` are skipped when `ENVIRONMENT=production`; `_seed_admin` runs everywhere
when `ADMIN_PASSWORD` is set. There is **no schema version**: every start re-runs every step
idempotently — about 95 DDL statements on PostgreSQL in one transaction (`ADD COLUMN IF NOT
EXISTS`, `CREATE … IF NOT EXISTS`), then an item sync that issues one `UPDATE` per bank item
(2,031 today; P:3452-3467), then the legacy reconciliation's scans. Render runs `migrate.py` on
every cold start.

**Bootstrap locks** (PostgreSQL only). `pg_try_advisory_lock` 12345 (`_migrate_db`), 12346
(admin seed), 12347 (demo seed), 12348 (item sync), 12349 (test students); the reconciliation
takes `pg_try_advisory_xact_lock(12345)`. A step whose lock is held is skipped and reported by
`bootstrap_skipped_steps()` (P:267). No blocking advisory lock remains. SQLite has no equivalent:
two processes would both run every step.

**Connections.** PostgreSQL: `ThreadedConnectionPool(1, 5)` (P:207-209), `sslmode` from
`DATABASE_SSLMODE` (default `require`), `statement_timeout=60s`, no keepalives or connect timeout.
`get_connection` retries an exhausted pool for up to 30 s with `time.sleep` (P:271-294); every
method returns its connection in `finally` (R4 holds: no `conn.close()` in P). SQLite: a new
`sqlite3.connect(timeout=30)` per call (S:64-65), no pragmas (no WAL, no `foreign_keys`).

**Transactions.** `save_answer_transaction` locks `users` then `items` `FOR UPDATE`, reads the
`(course, topic)` rating **without a lock** and writes an absolute value (P:1683-1700, 1632-1645).
The other rating writers — validated procedure (`_bump_course_topic_rating`, P:1656) and finished
PvP match (P:4042) — apply `GREATEST(0, current_elo + delta)` without locking `users`. Those are
the only `FOR UPDATE` statements in P. SQLite serialises the answer with `BEGIN IMMEDIATE`
(S:1327-1332).

**Storage.** Procedure images go to the private bucket `procedimientos` under
`{student_id}/{item_id}/{hash}.{ext}`; the row stores the relative path in `storage_url` (R9).
BYTEA `image_data` is **always** written as well (P:4353-4355), and a failed upload also writes a
local file under `data/uploads/procedures`. SQLite has no Storage and no `storage_url` column: it
keeps the file and a BLOB.

**Parity checks.** `db_sync_check.py` compares method names and raw parameter text, counts lines
in `_migrate_db` matching `ALTER TABLE|ADD COLUMN|CREATE TABLE|CREATE INDEX` (only a different
*count* fails), checks `?`/`%s` placeholders, `row[<digit>]` and connection get/put counts.
Behaviour is checked by the integration tests parametrised over both engines: 88 cases run on
each engine, 19 only on SQLite, 13 only on PostgreSQL (CI job "Guardas PostgreSQL").

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| P1 | **Bug risk** | **A rating delta can be lost.** The answer transaction reads the topic rating without a lock and overwrites it with an absolute value; a validated procedure or a finished PvP match that commits its `+delta` on the same row between that read and that write is erased. Breaks R15 ("each writer applies its effect exactly once"). Narrow window, but silent. | P:1683-1700, 1632-1645, 1656, 4042 | **Reproduced** on local PostgreSQL 16 (§ 4.1) |
| P2 | **Data precision** | **PostgreSQL `REAL` is 4-byte float**: `items.difficulty`/`rating_deviation`, every `attempts` rating column, `users.current_elo`, procedure and PvP deltas, exam and diagnostic scores keep ~7 significant digits (1189.34495 → 1189.345). Only `student_course_topic_elo` is `DOUBLE PRECISION` (P:974-975). SQLite `REAL` is 8-byte. | P:355, 372-378, 393-394; S:115-121, 137-138 | Verified on PG 16. **Measured impact: negligible** — the rounding error is ≤ 3·10⁻⁵ to 1.2·10⁻⁴ points per write between 300 and 2,500; 10,000 simulated item-difficulty updates drift 0.001 points from 8-byte arithmetic; screens round to whole numbers |
| P3 | **Parity (F-3)** | **`attempts.difficulty` is declared `INTEGER` on both engines**, not REAL on SQLite as the roadmap says. SQLite's integer affinity keeps 598.3854 as a real value; PostgreSQL rounds it to 598. | S:113, P:370 | Verified (PG 16, SQLite) |
| P4 | **Parity** | **Foreign keys differ by engine.** SQLite never enables `PRAGMA foreign_keys`, so none of its declared FKs is enforced; PostgreSQL declares only five FKs, so most relations (attempts, enrollments, procedure submissions, PvP, lessons, items → courses) are enforced on neither engine. | S:64-65 (no pragma); FK lists in both `_migrate_db` | Verified |
| P5 | **R8** | **One non-additive DDL runs on every start:** PostgreSQL `ALTER TABLE procedure_submissions ALTER COLUMN image_data DROP NOT NULL`. Idempotent in effect, but it is the "never DROP" the rule forbids, and it is the line `db_sync_check` balances with a comment (S:436). | P:733-738 | Verified |
| P6 | **Startup data rewrites** | Every start also runs data repairs: deactivates users with an empty password hash (would re-deactivate one reactivated without a password), renames duplicate groups `-DUP-{id}`, backfills `groups.name_normalized`, and `_backfill_prob_failure` rewrites the value for **all** attempts of a user who has any NULL. | S:493-554, 932-961; P:792-859, 1242-1282 | Verified (code) |
| P7 | **Bug risk** | `_migrate_db` on PostgreSQL catches a failed `UPDATE groups` with `conn.rollback()` and carries on: that discards every DDL issued earlier in the same transaction, then commits the rest. | P:792-801 | Code verified; effect inferred |
| P8 | **Pool** | **psycopg2 keeps at most `minconn` idle connections** (`_putconn` closes the rest; psycopg2 2.9.13 `pool.py:105-116`). With `minconn=1`, every concurrent checkout beyond the first opens a new TLS connection to Supabase. The liveness probe `conn.isolation_level` (P:290) does not detect a dead connection. | P:207-209, 271-294 | Pool behaviour verified in the installed psycopg2; probe inferred |
| P9 | **R17** | **Blocking calls inside `async def`:** `submit_procedure` writes the submission and uploads to Supabase synchronously (student.py:461, 477-512); `ai.py:56, 75` and `notifications.py:80-91` read the repository directly. With the pool exhausted, `time.sleep` in `get_connection` would freeze the event loop for up to 30 s. PvP does it right (`asyncio.to_thread`). | `api/routers/student.py:461`, `api/routers/ai.py:56,75`, `api/websocket/notifications.py:80-91` | Code verified; stall inferred |
| P10 | **Storage** | **The teacher queue cannot fall back to BYTEA:** `get_pending_submissions_for_teacher` returns `image_data` only when `storage_url IS NULL`, so a failed Storage download gives 404 although the bytes are in the row. Also: BYTEA is always stored (contrary to P:4319-4320), and a resubmission with a new hash leaves the old object in the bucket. | P:4568-4573, 4353-4355; `api/routers/teacher.py:204-212` | Code verified |
| P11 | **Parity gaps** | `storage_url` exists only on PostgreSQL; SQLite's item sync updates an existing course's name and block, PostgreSQL only inserts (`ON CONFLICT DO NOTHING`); the test-student seed creates 8 students and 4 groups on SQLite, 7 and 3 on PostgreSQL; PostgreSQL has two indexes on `groups(teacher_id)` and one on `attempts(user_id)` that SQLite lacks; `TIMESTAMP` columns come back as `str` on SQLite and `datetime` on PostgreSQL, and three of them are `TEXT` on SQLite (compared as strings). | S:3000-3005 vs P:3388-3391; `seed_test_students.py:26-36` vs P:3495-3504; P:411-418, 625; S:721, 773-774 | Verified |
| P12 | **Bug (F-1 residue)** | **Semillero test students get no enrolments:** the seed looks for block `Semillero {grade}°` / `LIKE 'Semillero %'`, which the CHECK does not allow (blocks are `Semillero`). Local and test data only (skipped in production). | `seed_test_students.py:92, 134`; P:3556, 3596 | Verified |
| P13 | **Check blind spots** | `db_sync_check.py` does not see `_add_column_if_not_exists` calls (no keyword on the line), column types, `CREATE UNIQUE INDEX`, `init_db`, or `__init__`; it counts comments; text differences are reported only when the counts differ, and only as warnings. P2–P5 and P11 all pass it. | `scripts/db_sync_check.py:65, 85-100, 171-193` | Verified (reading; the check passes today) |
| P14 | **Contract** | The contract checks names only; 98 public methods are in no interface; `IAdminRepository` has no consumer check; the runtime `isinstance` test runs on a synthetic fake. Routers depend on the concrete repositories. | `repositories.py`; `test_repository_contracts.py:50-123` | Verified |
| P15 | **Swallowed errors** | A failed password-rehash write is hidden as "invalid credentials" (P:1574-1575); any `IntegrityError` on registration reads "username exists" (P:1507-1509); `_get_profile_row` turns a database error into 401/404 (`api/routers/auth.py:189-190`); advisory-unlock failures are swallowed (P:1219-1220 and four more), which could leave a session lock on a pooled connection; Storage errors become `None` with a print. | as cited | Code verified |
| P16 | **Connection hygiene (SQLite)** | 106 of 126 methods close their connection in straight-line code, so an exception leaks it until garbage collection; the session methods use `with conn:`, which commits but never closes. | e.g. S:3618-3630, 3697-3735 | Verified (sample read) |
| P17 | **R12 (V1)** | V1's `_REPO_SINGLETON` lives in the main script, which Streamlit re-executes on every rerun, so it is likely rebuilt per browser session (one pool each) — only `session_state` keeps it. V1 is frozen and disconnected during the transfer; this matters only if it is reconnected. V2's singleton has no lock but is built once at startup. | `app.py:50-76`; `api/dependencies.py:30-54`; `api/main.py:63` | Inferred |
| P18 | **Smell** | `save_procedure_submission` does SELECT-then-INSERT with no UNIQUE `(student_id, item_id)`: concurrent submissions can duplicate rows. `_retry_on_deadlock` says it rolls back but does not, and wraps two read-only methods. `DATABASE_URL` is parsed with a regex whose last group would swallow a `?query` suffix into the database name. | P:4376-4421, 34-57, 175 | Code verified; the regex was run: `…:5432/postgres?sslmode=require` parses to the database name `postgres?sslmode=require`; other effects inferred |
| P19 | **Drift** | AGENTS.md § Database lists the bootstrap without `_reconcile_legacy_ratings` and `expire_stale_pvp_matches`; the roadmap's F-3 wording (P3); `docs/arquitectura.md` § Persistencia says parity is proven by `test_elo_single_source.py` (now 88 two-engine cases across many files). | `AGENTS.md:556-557`; `docs/sdd/roadmap.md` F-3 | Verified |
| P20 | **Latency** | **Every PostgreSQL repository call pays about three network round trips.** psycopg2 sends `BEGIN` before the first statement, then the statement; a read's transaction is closed by the pool's `ROLLBACK` when the connection is returned, a write's by its `COMMIT`. Endpoints that read once per element multiply this. The course map made 59 reads: 2.0 s at a simulated 10 ms round trip, 5.6 s at 30 ms (fixed separately in PR #22). `/stats` makes 6 reads, about 0.2 s at 10 ms. Reads in autocommit would take one round trip each. | P:271-294 (pool); `api/routers/student.py` (map) | **Measured** on local PostgreSQL 16 through a proxy: a read is 3 client→server messages, `record_lesson_event` 6; times with a proxy that delays every message |
| P21 | **Smell** | A procedure's exercise id is free text (`Form(...)`, no length limit) and is stored as typed; the PostgreSQL repository also prints it raw in a log line (`[SAVE_PROC] Recibido`). Path use is fixed separately (F-7, PR #17); a length limit and logging without user text belong to the persistence contract. Present on `main` too. | `api/routers/student.py:464`; P:4326 | Verified (code read) |

## 4. Existing evidence

- **Contract:** `tests/unit/application/test_repository_contracts.py` (4 tests),
  `tests/unit/test_architecture_layers.py` (layers; no rating aggregation in repositories).
- **Behavioural parity:** the `repo` fixture (`tests/integration/conftest.py:64-72`) runs 88 cases
  on each engine (spec 001 pins, answer retries, course-topic store, catalogue, practice access,
  reconciliation, PvP enrolment). SQLite-only: `test_sqlite_repository.py` (6),
  `test_pvp_repository.py` (13). PostgreSQL-only: `test_postgres_production_guards.py` (6),
  `test_migrate_lock.py` (6 cases), the `migrate.py` case of `test_spec001_course_block_constraint.py`.
- **Bootstrap:** `test_migrate_lock.py` (every advisory lock held by another session; the real
  start command), `test_v1_run_migrations.py` (V1 honours `RUN_MIGRATIONS=0`),
  `test_spec001_course_block_constraint.py` (FR-028n).
- **Rehearsal:** `scripts/rehearse_migration.py` (restore, migrate twice, compare) — PASS on the
  legacy simulation.
### 4.1 Reproduction of P1 (2026-10-09)

On a throwaway local PostgreSQL 16 database bootstrapped by the repository itself, through its
public methods only: a student's `(course, topic)` rating set to 1000; a procedure submission for
an item of that topic; then `save_answer_transaction` with a `compute` that, between the
transaction's read and its write, calls `validate_procedure_submission(score=100)` (+10, committed
on another pooled connection) and returns an answer worth +5. Read 1000 → after the procedure
1010 → final **1005**, not 1015: the procedure's +10 is gone while the submission says
`elo_applied = 1`. The PvP finish uses the same `GREATEST(0, current_elo + delta)` update, so it is
exposed the same way. SQLite is not: `BEGIN IMMEDIATE` holds the database's write lock for the
whole answer.

- **Not covered:** numeric precision and types across engines (P2, P3), FK enforcement (P4),
  the lost update (P1), pool reuse (P8), the async boundary (P9), the Storage read fallback
  (P10), startup data rewrites (P6, P7).

## 5. Decisions for the owner (input for `/speckit-clarify`)

Each is a real choice; none blocks the transfer (PR #3).

1. **Which engine is the contract?** Production is PostgreSQL. Should spec 002 require identical
   behaviour on both engines (today's R1), or make PostgreSQL the reference and SQLite a
   development engine that must pass the same tests?
2. **Precision (P2, P3 = F-3).** R8 forbids changing a column's type. Options: accept and document
   the 4-byte precision and the integer `attempts.difficulty`; or add `DOUBLE PRECISION` columns,
   write both, read the new one (additive, more code). The measured drift (P2) is about 0.001
   points after 10,000 updates, far below the whole-number display; `attempts.difficulty` loses up
   to 0.5 points of history on PostgreSQL.
3. **Foreign keys (P4).** Enable `PRAGMA foreign_keys` on SQLite (existing local databases may hold
   orphans), declare the missing FKs on PostgreSQL (an additive `ADD CONSTRAINT … NOT VALID` is
   possible, but production data must be checked first), or document that relations are enforced
   by code.
4. **The `DROP NOT NULL` (P5).** Run it only while the column is still `NOT NULL` (read
   `information_schema` first) and record it as the one accepted R8 exception, or leave it.
5. **Startup repairs and versioning (P6, P7, cold starts).** Keep re-running everything
   idempotently, add an additive schema-version table so a start with nothing to do does nothing,
   or move the one-off data repairs to scripts.
6. **Lost update (P1).** It is a rating-writer defect (spec 001's R15 rule). Fix it as a spec 001
   follow-up (test first, own PR) or inside spec 002 ("locks")?
7. **Async boundary (P9), pool (P8) and round trips per read (P20).** In spec 002's scope, or a
   separate follow-up? Raising `minconn` keeps warm connections without raising `maxconn` (R4); the
   Supabase free tier limits apply to both. Reads in autocommit, or several reads on one checkout,
   cut the round trips per request; where Render and Supabase run decides how much that matters.

## 6. Proposed scope for spec 002 (draft)

- **In:** the repository contract (what services and routers may call), engine parity (types,
  constraints, seeds, item sync), additive and idempotent migrations and what a start may write,
  bootstrap locks and their reporting, connection and pool lifecycle, transaction and lock order
  across writers, the async boundary to the repositories, Storage paths and fallbacks, what
  `db_sync_check.py` must catch, F-3.
- **Out:** rating arithmetic and which writer moves which rating (spec 001); identity and access
  rules (spec 004); PvP match lifecycle (spec 007); item bank format and calibration (spec 008);
  V1 beyond keeping it working (frozen).
