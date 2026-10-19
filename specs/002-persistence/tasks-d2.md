# Tasks — spec 002, delivery D2 (connections and the event loop)

**Plan**: [plan-d2.md](plan-d2.md) (approved by the owner, 2026-10-19, N1 = 2 idle connections,
N2 = the hot paths' reads first). Every D2 requirement is `[CHANGE]`: its test fails on the
unchanged code first. The A pins (FR-020, FR-021, FR-026) and D1's startup tests stay green.

## Hot reads (N2), measured

Calling `/next-question`, `/stats`, the course map, the lesson, the group ranking and the course
list on PostgreSQL, with every repository method wrapped, gives these 18 reads:
`get_answered_item_ids`, `get_course_topic_ratings`, `get_course_topic_ratings_bulk`,
`get_items_from_db`, `get_user_by_id` (every authenticated request), `get_user_enrollments`,
`get_courses`, `get_current_context_course_ids_bulk`, `get_study_streak`,
`get_total_attempts_count`, `get_diagnostic`, `get_lesson_states`, `get_lesson_progress`,
`get_lesson_interactions`, `get_ranking_participants`, `get_available_courses_by_level`,
`get_completed_diagnostic_course_ids`, `get_education_level`. Before D2 each costs `BEGIN`, its
`SELECT` and `ROLLBACK` (counted by the proxy).

## Deviation from the plan, decided while writing the tests

- A read marked `@_read_only` also **retries once** on a fresh connection when the first attempt
  fails with `OperationalError`/`InterfaceError` (reads are idempotent). The probe of FR-023 covers
  a connection idle past `DB_POOL_PROBE_AFTER_S`; the retry covers one the server closed sooner,
  at no cost for the hot connections.

## Phase 1 — Setup

- [x] T001 `tests/integration/pg_message_proxy.py`: TCP proxy counting the client's `Q` messages

## Phase 2 — Tests first (`tests/integration/test_spec002_d2_connections.py`; all fail today)

- [x] T002 [P] US5-AS1, FR-025, SC-003: each hot read sends only its own statements
- [x] T003 [P] FR-025: `@_read_only` is on exactly the hot reads, on both engines, none writes
- [x] T004 [P] US5-AS2, FR-023: after the server closes the pooled connections, a read and a write
  succeed
- [x] T005 [P] US5-AS3, FR-020, FR-022: after a burst of 5, 2 idle connections stay; a sixth is
  refused
- [x] T006 [P] US4-AS1, FR-024, SC-004: KatIA's chat waiting 2 s on the repository does not delay
  `/api/health` (both engines)
- [x] T007 [P] US4-AS2: an exhausted pool waited on by an async handler does not delay
  `/api/health`
- [x] T008 [P] FR-024: AST guard — no repository call in an `async def` under `api/`

## Phase 3 — Implementation

- [ ] T009 Both repositories: `_read_only` decorator (PostgreSQL: autocommit for the checkout and
  one retry; SQLite: marker only) on the 18 hot reads (T002, T003)
- [ ] T010 PostgreSQL pool: `minconn = DB_POOL_MIN_IDLE` (default 2, clamped 1…5), the liveness
  probe for connections idle past `DB_POOL_PROBE_AFTER_S` (default 30), `put_connection` resets
  autocommit (T004, T005)
- [ ] T011 `api/routers/ai.py::socratic` and `api/websocket/notifications.py`: repository calls via
  `asyncio.to_thread` (T006 … T008)
- [ ] T012 `docs/transfer.md` § 3 and AGENTS.md R4/R17: the two variables, the read decorator

## Phase 4 — Close

- [ ] T013 Traceability: every D2 row filled; D2 `closed`; full suite on both engines,
  `db_sync_check.py`, black, flake8, `check_traceability.py`; before/after numbers in the PR
