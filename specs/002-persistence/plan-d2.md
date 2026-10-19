# Plan — spec 002, delivery D2: connections and the event loop

**Spec**: [spec.md](spec.md) § Deliveries, D2 (US4, US5; FR-022 … FR-025; SC-003, SC-004) ·
**Branch**: `002-persistence-d2`, from `redesign` after D1 (LuisJRubioH/LevelUp-ELO#81) ·
**Date**: 2026-10-19 · **Status**: for the owner's approval

## Summary

The API is one process (AGENTS R18). Three things slow it down:

- Each PostgreSQL read pays about three round trips: `BEGIN`, the query, and the pool's
  `ROLLBACK` (survey P20).
- Concurrent requests beyond the first open a new TLS connection to Supabase, because the pool
  keeps one idle connection (P8).
- Two asynchronous handlers call the repository synchronously, which stops every request and
  socket while they wait (P9).

D2 fixes all three. It also adds a liveness check that detects a connection the server closed.

## Constitution Check (1.2.0)

| Principle | D2 |
|---|---|
| Dual database (IV, R1) | The read decorator and the pool settings exist on both repositories (no-ops on SQLite); every behaviour test runs on both engines where it applies; `db_sync_check.py` |
| Pool limits (R4) | `maxconn` stays 5; the minimum idle is configurable and never above it |
| Async boundary (R17) | Every repository or Storage call from `async def` goes through `asyncio.to_thread`; a guard test reads `api/` and fails on a direct call |
| Simplicity and evidence (VII) | No new dependency (no asyncpg, no new pool); before/after round trips measured through a counting proxy, as the survey did |
| Security (VI) | No change to what is logged; the proxy and the measurements run locally only |

## Design

### Idle connections (FR-022, US5-AS3)

- psycopg2's `ThreadedConnectionPool` keeps at most `minconn` idle connections and closes the rest
  when they are returned. `minconn` becomes `DB_POOL_MIN_IDLE`:
  - default **2**;
  - clamped to the range 1 … 5;
  - `maxconn` stays 5.
- The pool opens `minconn` connections at start-up. That is one more connection to Supabase than
  today, well under the free tier's limit; the dashboard keeps the final say.
- `docs/transfer.md` § 3 lists the variable.

### A real liveness check (FR-023, US5-AS2)

- Today's probe, `conn.isolation_level`, reads a client-side attribute and never fails for a
  connection the server closed.
- New check, run on checkout:
  1. a connection with `conn.closed` set is discarded;
  2. a connection idle for more than `DB_POOL_PROBE_AFTER_S` (default 30 s; Supabase's pooler and
     Render's network close idle sockets) is probed with `SELECT 1` in autocommit; on
     `OperationalError` or `InterfaceError` it is discarded and replaced.
- The last-return time is kept per connection (a dict keyed by `id(conn)`). Hot connections
  therefore pay nothing, which keeps FR-025's single round trip.

### One round trip per read (FR-025, US5-AS1, SC-003)

- A decorator `@_read_only` on the repository's read methods sets `conn.autocommit = True` for
  that checkout. psycopg2 then sends no `BEGIN`, and `put_connection` skips the `ROLLBACK`
  (nothing is open) and resets `autocommit = False` before returning the connection.
- Applied method by method. Applied only where the method issues no write; a test checks this
  with D1's statement recorder over every decorated method.
- Same decorator name on SQLite, as a no-op: SQLite has no round trips, and the parity check stays
  textual.
- Writers and the transactions of spec 001 (`save_answer_transaction`, the procedure grading,
  `finish_pvp_match`) are **not** touched: they need their transaction.

### No blocking call on the event loop (FR-024, US4-AS1, US4-AS2, SC-004)

| Handler | Today | D2 |
|---|---|---|
| `api/routers/ai.py::socratic` | `repo.get_item_by_id` in `async def` | `await asyncio.to_thread(...)` |
| `api/routers/ai.py::socratic` (saving the interaction) | already `run_in_executor` | unchanged |
| `api/routers/ai.py::review_procedure` | no repository call | unchanged |
| `api/websocket/notifications.py` | `authenticate_access_token`, `get_user_by_id`, `get_groups_by_teacher` in `async def` | one `to_thread` for the room check |
| `api/routers/student.py::submit_procedure`, `analyze_procedure` | already `to_thread` | unchanged |

- With these calls in a worker thread, `get_connection`'s `time.sleep` (pool exhausted) also runs
  off the loop (US4-AS2).
- A guard test reads every `async def` under `api/` (AST) and fails on a call to `repo.*`,
  `get_repository()` or a Storage method that is not inside `asyncio.to_thread`. It is the same
  kind of guard as `test_architecture_layers.py`.

## Tests (written first; each [CHANGE] test must fail on today's code)

| Test | Engines | Proves |
|---|---|---|
| `test_spec002_d2_a_read_costs_one_round_trip`: a counting TCP proxy in front of the local PostgreSQL counts client→server messages for a sample of read methods | PostgreSQL | US5-AS1, FR-025, SC-003 |
| `test_spec002_d2_read_only_methods_write_nothing`: every `@_read_only` method run under the statement recorder | both | FR-025 (safety of the decorator) |
| `test_spec002_d2_a_closed_connection_is_replaced`: the server terminates a pooled backend (`pg_terminate_backend`); the next request succeeds | PostgreSQL | US5-AS2, FR-023 |
| `test_spec002_d2_idle_connections_survive_a_burst`: 5 concurrent checkouts, then the idle count equals `DB_POOL_MIN_IDLE`; never more than 5 open | PostgreSQL | US5-AS3, FR-020, FR-022 |
| `test_spec002_d2_a_slow_repository_call_does_not_block_other_requests`: a repository method slowed to 2 s behind KatIA's chat; `/api/health` answers within its normal time meanwhile (httpx `AsyncClient` + ASGI) | both | US4-AS1, FR-024, SC-004 |
| `test_spec002_d2_waiting_for_the_pool_does_not_block_the_loop`: pool exhausted; an async handler waits; `/api/health` still answers | PostgreSQL | US4-AS2 |
| `test_spec002_d2_no_repository_call_in_async_code`: AST guard over `api/` | — | FR-024 |
| The A pins (FR-020, FR-021, FR-026) and D1's startup tests | both | unchanged behaviour |

## Measurement (SC-003, SC-004)

- Before and after, through the counting proxy with a 10 ms delay per message:
  - messages per read on `/stats`, the course map and `/next-question`;
  - p50 of `/api/health` while a 2 s repository call runs in KatIA's chat.
- The numbers go into this plan's PR. Production is not measured (agents never touch it).

## Rollout

- No schema change: `SCHEMA_VERSION` stays where D1 left it, and the digest test stays green.
- One optional environment variable on Render, `DB_POOL_MIN_IDLE`, which defaults to 2.

## Open points for the owner

- **N1 — `DB_POOL_MIN_IDLE` default.** Recommended **2**: one more idle connection than today. 3
  helps bursts more but holds 3 of Supabase's connections all day.
- **N2 — Scope of `@_read_only`.** Recommended: the reads behind the student's hot paths first
  (`/next-question`, `/stats`, map, lesson, ranking), then the rest in the same PR only if the
  write-guard test covers them. The alternative is every read at once.
