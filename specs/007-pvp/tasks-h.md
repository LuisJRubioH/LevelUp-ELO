# Tasks — spec 007, delivery H (the match history and a close that fails)

**Plan**: [plan-h.md](plan-h.md) (approved by the owner, 2026-10-20). FR-060 and FR-061 are
`[CHANGE]`; delivery H touches the close path pinned by delivery A and spec 001 FR-029c.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[US6]**: User Story 6 — Every match leaves a trace

---

## Phase 1: Setup

- [ ] T001 `PVP_HISTORY_PAGE = 5` and the retry delays (0.5, 1, 2 s) as module constants in
  `api/websocket/pvp.py` / `api/routers/student.py`; no behaviour yet.

---

## Phase 2: Pin Current Behaviour (Blocking)

- [ ] T002 Run delivery A's PvP tests and spec 001's PvP pins
  (`tests/unit/infrastructure/test_pvp_logic.py`, `tests/integration/test_pvp_*.py`,
  `tests/api/test_pvp*.py`, `frontend/e2e/league.spec.ts`) against the unchanged code and record
  the green run here. They must stay green through every task below.

**Checkpoint**: the close path pinned — H can change it.

---

## Phase 3: User Story 6 — Every match leaves a trace (Priority: P3)

**Goal**: the history lists finished, abandoned and unsaved matches with subject and reason, the
rows the screen shows; a failing close is retried, then recorded as `not_saved`.

**Independent Test**: `tests/integration/test_spec007_h_history.py`.

### Tests for User Story 6 (written first; each must FAIL before its implementation task)

- [ ] T010 [P] [US6] `[CHANGE]` `test_spec007_history_lists_finished_abandoned_and_not_saved`,
  `test_spec007_history_pages_of_five_reach_every_match`, `test_spec007_the_sweep_records_why` for
  FR-060, US6-AS1 in `tests/integration/test_spec007_h_history.py` (both engines) — **fail**
  before T020–T021
- [ ] T011 [P] [US6] `[CHANGE]` `test_spec007_a_failing_close_is_retried_then_recorded_not_saved`,
  `test_spec007_a_close_that_succeeds_on_retry_finishes_normally`,
  `test_spec007_abandon_is_idempotent_and_skips_a_finished_match` for FR-061, US6-AS2 in the same
  file — **fail** before T022–T023
- [ ] T012 [P] [US6] `[CHANGE]` `/api/student/pvp/history` returns `{matches, has_more}`, at most 5 rows
  with `status`, `course_name`, `reason`, and honours `before` in `tests/api/test_pvp.py` — **fails** before T021
- [ ] T013 [P] [US6] `[CHANGE]` e2e «el historial muestra partidas abandonadas y no guardadas con
  su materia» and «ver más carga la página siguiente» in
  `frontend/e2e/league.spec.ts` — **fails** before T024

### Implementation for User Story 6

- [ ] T020 [US6] FR-060: the sweep writes `elo_delta_* = 0`, `elo_reason_* = 'orphaned'` (both
  repositories) (T010 sweep test green)
- [ ] T021 [US6] FR-060: `get_pvp_history` returns finished and abandoned rows with `status`,
  `course_name`, `reason`, one page after `before`; the endpoint returns `{matches, has_more}`
  (both repositories; T010, T012 green)
- [ ] T022 [US6] FR-061: `abandon_pvp_match(match_id, reason)` in both repositories, only while
  `active`, no rating change (T011 idempotence test green)
- [ ] T023 [US6] FR-061: `_close_match` retries `finish_pvp_match` (first try + 3 retries), then
  `abandon_pvp_match(…, "not_saved")`; `game_end` keeps `not_applied` (T011 green; spec 001 pin
  green)
- [ ] T024 [US6] Frontend: `HistoryPanel` renders every row it receives and «Ver más» while
  `has_more`, the subject, and an abandoned row's reason from `league.historyReasons.*` (es, en) with a fallback (T013 green)
- [ ] T025 [US6] `python scripts/db_sync_check.py` — both repositories in step

**Checkpoint**: US6 functional; T010–T013 green; delivery A's and spec 001's pins still green.

---

## Phase N: Traceability & Verification

- [ ] T090 Fill § Traceability rows FR-060, FR-061, US6-AS1, US6-AS2; mark delivery H `closed`
- [ ] T091 Review assertion adequacy: the not-saved test checks no rating moved *and* both
  players see the row; the pages test checks the newest five first and that the two pages together hold every match once
- [ ] T092 Verification (AGENTS.md § Verify): full suite on both engines, `db_sync_check.py`,
  `pnpm run build`, Playwright `league.spec.ts`, `check_traceability.py`, black, flake8
- [ ] T093 V1 check: the repositories are shared with V1; V1 does not read the PvP history

---

## Dependencies & Execution Order

- T001 → T002 (pins green) → T010–T013 written and failing → T020–T025 → T090–T093.
- T020 and T021 depend on T010; T022 and T023 on T011; T024 on T013; T023 on T022.

## Notes

- E3 (#73) adds `abandon_pvp_match` with the same signature and reason storage; whichever PR lands
  second keeps one copy and both reasons in `league.historyReasons`.
