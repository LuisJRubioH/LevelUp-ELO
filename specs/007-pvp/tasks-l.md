# Tasks — spec 007, delivery L (socket and process limits)

**Plan**: [plan-l.md](plan-l.md) (approved by the owner, 2026-10-20). FR-050, FR-051 and FR-052
are `[CHANGE]`; delivery L touches no `[AS-IS]` requirement's code path except the League receive
loop, pinned by delivery A's tests.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[US5]**: User Story 5 — The server cannot be flooded

---

## Phase 1: Setup

- [x] T001 Add the settings `pvp_max_frame_bytes` (4096), `pvp_max_messages_per_second` (5),
  `pvp_abuse_limit` (10), `pvp_single_process_lock` (`/tmp/oulad-api.lock`) to `api/config.py`
  with their environment names; no behaviour yet.

---

## Phase 2: Pin Current Behaviour (Blocking)

- [x] T002 Run delivery A's PvP tests (`tests/integration/test_pvp_waiting_player.py`,
  `test_pvp_enrolment.py`, `test_pvp_answer_integrity.py`, `tests/api/test_pvp_orphan_sweep.py`,
  `frontend/e2e/league.spec.ts`) against the unchanged code and record the green run here. They
  must stay green through every task below. Green in the full suite after every change (2026-10-20).

**Checkpoint**: normal play pinned — limits can be added.

---

## Phase 3: User Story 5 — The server cannot be flooded (Priority: P3)

**Goal**: one League socket per student; frames over 4 KB and beyond 5/s dropped, persisting abuse
closed; one worker in production by any route.

**Independent Test**: `tests/integration/test_pvp_limits.py` and `tests/api/test_single_worker.py`.

### Tests for User Story 5 (written first; each must FAIL before its implementation task)

- [x] T010 [P] [US5] `[CHANGE]` `test_spec007_a_second_league_socket_is_refused` for FR-050,
  US5-AS1 in `tests/integration/test_pvp_limits.py` (uvicorn, both engines) — **fails** before T020
- [x] T011 [P] [US5] `[CHANGE]` `test_spec007_an_oversized_frame_is_dropped`,
  `test_spec007_a_burst_beyond_the_rate_is_dropped`,
  `test_spec007_persisting_abuse_closes_the_socket` for FR-051, US5-AS2 in the same file —
  **fail** before T021–T022
- [x] T012 [P] [US5] `[CHANGE]` unit tests `test_spec007_socket_limits_*` for the token bucket and
  the abuse window (fake clock) in `tests/unit/api/test_pvp_limits.py` — **fail** before T021
- [x] T013 [P] [US5] `[CHANGE]` `test_spec007_a_second_worker_refuses_to_start` and
  `test_spec007_web_concurrency_is_still_refused` for FR-052 in `tests/api/test_single_worker.py`
  (two subprocesses, production settings, same lock path) — the first **fails** before T023
- [x] T014 [P] [US5] `[CHANGE]` e2e «una segunda pestaña dice por qué» (mocked close 4409) in
  `frontend/e2e/league.spec.ts` — **fails** before T024

### Implementation for User Story 5

- [x] T020 [US5] FR-050: per-student League socket registry in `api/websocket/pvp.py`, set after
  authentication, cleared in `finally`; a second socket closed 4409 before the lobby (T010 green)
- [x] T021 [US5] FR-051: `api/websocket/limits.py::SocketLimits` (token bucket + abuse window),
  pure (T012 green)
- [x] T022 [US5] FR-051: apply `SocketLimits` to every frame of the League socket — the token frame,
  the waiting loop and the answer loop; persisting abuse closes 4429 (T011 green)
- [x] T023 [US5] FR-052: exclusive non-blocking `fcntl.flock` on `pvp_single_process_lock` in the
  lifespan, production only, held for the process's life; the R18 message on failure (T013 green)
- [x] T024 [US5] Frontend: 4409 and 4429 in `usePvpMatch.ts`; every close notice moved to
  `league.closeNotices.*` in `es` and `en` (T014 green)
- [x] T025 [US5] If the owner approves O-L1: `--ws-max-size 65536` in `render.yaml`'s
  `startCommand`
- [x] T026 [US5] Docs: AGENTS.md R18 and `docs/arquitectura.md` § Límites conocidos name the lock
  and the limits

**Checkpoint**: US5 functional; T010–T014 green; delivery A's tests still green.

---

## Phase N: Traceability & Verification

- [x] T090 Fill § Traceability rows FR-050, FR-051, FR-052, US5-AS1, US5-AS2 with the tests above;
  mark delivery L `closed`
- [x] T091 Review assertion adequacy: each test proves its FR/scenario (refusal *and* the first
  socket unaffected; drop *and* recovery after a second)
- [x] T092 Verification (AGENTS.md § Verify): full suite on both engines, `pnpm run build`,
  Playwright `league.spec.ts`, `check_traceability.py`, black, flake8
- [x] T093 V1 check: no shared layer changes (`api/` and `frontend/` only) — none needed

---

## Dependencies & Execution Order

- T001 → T002 (pins green) → T010–T014 written and failing → T020–T026 → T090–T093.
- T020 depends on T010; T021 on T012; T022 on T011 and T021; T023 on T013; T024 on T014.
- T025 only after the owner's answer to O-L1.

### Parallel Opportunities

T010–T014 are independent files; T021 and T023 can proceed in parallel.

## Notes

- Overlap with delivery G (FR-023): L builds the registry and code 4409; G cites T010 for FR-023.
- Reconnect within the 20 s grace belongs to delivery F; under L alone a half-open socket can
  delay a reconnect by up to ~40 s.
- Two delivery A tests (`test_pvp_enrolment.py::test_pvp_matches_and_finishes_a_game_between_enrolled_students`,
  `test_pvp_answer_integrity.py::test_an_answer_outside_the_match_scores_nothing`) sent ten answers
  in a few milliseconds, faster than FR-051 allows; their client now answers at a person's pace
  (`ANSWER_PACE_S` = 0.25 s). What they assert is unchanged.
