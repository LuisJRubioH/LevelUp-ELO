# Tasks — spec 007, delivery F (the server's clock, a speed tiebreak and a 20 s grace)

**Plan**: [plan-f.md](plan-f.md) (approved; owner decisions O-F1 … O-F9 answered 2026-10-21). FR-040, FR-041 and
FR-042 are `[CHANGE]`; delivery F touches the match loop, the timer and the close pinned by delivery
A (FR-002, FR-003, FR-005, FR-007), the one-socket rule of delivery L (FR-050) and the close retries
of delivery H (FR-061).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[US4]**: User Story 4 — The match is decided on the server

---

## Phase 0: Owner decisions (Blocking)

- [x] T000 The owner answers O-F1 … O-F9 (plan-f § Decisions); record each answer in plan-f and
  set its status to approved. Tests T014–T017 and T019 are written to the decided option; a test
  for an option the owner rejects is dropped or rewritten before Phase 3.

---

## Phase 1: Setup

- [ ] T001 Add the setting `pvp_reconnect_grace_s` (20, `PVP_RECONNECT_GRACE_S`) to `api/config.py`
  and the constants `MATCH_ENDED_CODE = 4410`, `RESUMED_ELSEWHERE_CODE = 4411` to
  `api/websocket/pvp.py`; no behaviour yet.

---

## Phase 2: Pin Current Behaviour (Blocking)

- [ ] T002 Run against the unchanged code and record the green run here; they must stay green
  through every task below:
  - delivery A: `tests/unit/infrastructure/test_pvp_logic.py` (incl. `TestFinishMatch::test_draw_marks_both_draw_true`,
    `test_double_finish_is_guarded`, `test_finishing_early_leaves_a_timer_that_is_already_closing`,
    `test_no_answer_counts_once_the_match_is_over`), `tests/integration/test_pvp_enrolment.py`,
    `test_pvp_waiting_player.py`, `test_pvp_answer_integrity.py`, `test_pvp_repository.py`,
    `tests/integration/test_spec001_concurrent_rating_writers.py`, `tests/api/test_pvp_orphan_sweep.py`;
  - delivery L: `tests/integration/test_pvp_limits.py` (US5-AS1 — a socket without `resume` is
    still refused 4409), `tests/unit/api/test_pvp_limits.py`;
  - delivery H: `tests/integration/test_spec007_h_history.py` (a forfeit close goes through the
    same retries and `not_saved`);
  - spec 001: `test_spec001_game_end_reports_not_applied_when_persistence_fails`;
  - `frontend/e2e/league.spec.ts`.

- [ ] T003 If spec 004 E3 (#73) is in `redesign` when F starts: add its PvP tests to T002's pins
  (`tests/integration/test_spec004_e3_accounts.py`, the abandon and 4403 cases;
  `frontend/e2e/spec004-e3-accounts.spec.ts`, «una partida cerrada por un vencimiento…») and write
  `test_spec007_an_expired_account_mid_match_abandons_without_forfeit` in
  `tests/integration/test_spec007_f_match_flow.py`: an account that expires mid-match closes it as
  `abandoned` / `account_expired` with no rating change and 4403, and no grace or forfeit follows.
  It passes on E3's code before T025 and must stay green after it (plan-f § An expired account
  mid-match). If #73 lands after F, the PR that lands second adds this test.

**Checkpoint**: the match loop, the close and the one-socket rule pinned — F can change them.

---

## Phase 3: User Story 4 — The match is decided on the server (Priority: P2)

**Goal**: the screen counts down to the server's end time and the server alone ends the match;
equal scores are broken by speed; a dropped player has 20 s to resume, then loses by abandonment
and the opponent is told at once.

**Independent Test**: `tests/integration/test_spec007_f_match_flow.py` (uvicorn, both engines; the
grace and `MATCH_DURATION` shortened with `monkeypatch`).

### Tests for User Story 4 (written first; each must FAIL before its implementation task)

- [ ] T010 [P] [US4] `[CHANGE]` `test_spec007_game_start_carries_the_servers_end_time`,
  `test_spec007_the_server_closes_at_its_end_time_whatever_the_client_does` for FR-040, US4-AS1 in
  `tests/integration/test_spec007_f_match_flow.py` — the first **fails** before T020 (no `ends_at`)
- [ ] T011 [P] [US4] `[CHANGE]` `test_spec007_an_answer_read_after_the_end_time_is_not_judged` for
  FR-040 in `tests/unit/infrastructure/test_pvp_logic.py` — **fails** before T020
- [ ] T012 [P] [US4] `[CHANGE]` e2e «la cuenta atrás sigue la hora del servidor aunque la pestaña
  duerma» for US4-AS1 in `frontend/e2e/league.spec.ts` (`page.clock` jump without firing timers;
  the mocked `game_start` carries `ends_at`, `server_now`) — **fails** before T021
- [ ] T013 [P] [US4] `[CHANGE]` `test_spec007_equal_scores_the_faster_player_wins` for FR-041,
  US4-AS2 (unit, in the file O-F9 decides; cases: lower time wins, equal whole seconds → draw,
  0–0 → draw, a higher score wins whatever the time) and
  `test_spec007_a_tied_match_is_won_by_speed` for FR-041, US4-AS2 in
  `tests/integration/test_spec007_f_match_flow.py` — **fail** before T022
- [ ] T014 [P] [US4] `[CHANGE]` `test_spec007_a_player_who_returns_within_the_grace_resumes_the_match`,
  `test_spec007_a_player_who_does_not_return_loses_by_abandonment`,
  `test_spec007_a_reconnect_after_the_grace_finds_the_match_over` for FR-042, US4-AS3 in
  `tests/integration/test_spec007_f_match_flow.py` — **fail** before T024–T026
- [ ] T015 [P] [US4] `[CHANGE]` `test_spec007_a_reconnect_takes_over_a_half_open_socket` for FR-042
  with FR-050 (L's open ~40 s block; O-F1) in the same file, asserting both halves: with `resume`
  admitted at once and the old socket closed 4411; without `resume` still 4409 — **fails** before
  T024; under O-F1 (b), also `test_spec007_a_waiting_player_reconnects_without_waiting_for_the_ping`
- [ ] T016 [P] [US4] `[CHANGE]` the decided edge cases for FR-042 in the same file:
  `test_spec007_a_player_who_finished_and_leaves_does_not_forfeit` (O-F4),
  `test_spec007_both_players_away_abandons_without_rating` (O-F5),
  `test_spec007_the_grace_does_not_extend_the_match` (O-F6) — each **fails** before T025 (today a
  drop is never a forfeit nor an abandonment, so each fails on its observable `game_end` / row)
- [ ] T017 [P] [US4] `[CHANGE]` `test_spec007_finish_with_a_reason_keeps_no_rated_topics` for
  FR-042 / O-F3 in `tests/integration/test_pvp_repository.py` (both engines) — **fails** before T023
- [ ] T018 [P] [US4] `[CHANGE]` e2e «una caída reconecta y retoma la partida», «el rival abandona y
  ganas al instante», «volver tarde dice que la partida terminó» for US4-AS3 in
  `frontend/e2e/league.spec.ts` (mocked socket) — **fail** before T027
- [ ] T019 [P] [US4] `[CHANGE]` e2e «un empate se decide por velocidad» for US4-AS2 on screen
  (`game_end` with `tiebreak: true`) in `frontend/e2e/league.spec.ts` — **fails** before T027

### Implementation for User Story 4

- [ ] T020 [US4] FR-040: `ActiveMatch` gets `started`, `ends_at_loop`, `ends_at`; `game_start`
  carries `ends_at`, `server_now`; `_timer` sleeps to `ends_at_loop`; `_judge_answer` ignores an
  answer at or after it (T010, T011 green; A's answer-integrity pins green)
- [ ] T021 [US4] FR-040 frontend: `usePvpMatch.ts` derives `timeLeft` from `endsAt` and the server
  offset on every tick and on `visibilitychange`; at 0 the options are disabled and the screen waits
  for `game_end` (T012 green)
- [ ] T022 [US4] FR-041: `elapsed[user_id]` per O-F7 kept in the answer loop; the winner rule as a
  pure function where O-F9 decides; `_close_match` uses it; `game_end` adds `tiebreak`
  (T013 green; `test_draw_marks_both_draw_true` green unchanged, or flipped in this task citing
  FR-041 if its fixture must carry times)
- [ ] T023 [US4] FR-042 / O-F3: `finish_pvp_match(…, reason=None)` in both repositories, identical
  signature; `python scripts/db_sync_check.py` (T017 green; A's close pins green)
- [ ] T024 [US4] FR-042 / O-F1: the `resume` token per player (with `game_start`, and with
  `waiting`, O-F1 (b)); a first frame `{token, resume}` that matches takes over the slot — old
  socket closed 4411, `_league_sockets` rebound — before L's 4409 check; `game_resume` sent;
  `opponent_back` to the opponent; the timer task and early finish move onto `ActiveMatch`
  (T014 resume test, T015 green; US5-AS1 pin green)
- [ ] T025 [US4] FR-042: on a drop in a running match, mark the player away under `_lock` (no I/O),
  send `opponent_away`, schedule the grace task; on expiry close through `_finish_match` as the
  away player's forfeit (O-F2) with reason `forfeit`, or `abandon_pvp_match(…, "both_left")` (O-F5);
  apply O-F4 and O-F6 (T014 forfeit test, T016 green; H's retry pins green)
- [ ] T026 [US4] FR-042: a `resume` for a match no longer in `_matches` → close 4410 (T014
  after-the-grace test green)
- [ ] T027 [US4] Frontend: phase `reconnecting` with automatic retries for up to the grace (token
  refreshed first if expired); `game_resume` restores items, index, scores and `endsAt`;
  `opponent_away` / `opponent_back` notice; `game_end` `forfeit` / `tiebreak` result copy;
  `CLOSE_NOTICES` 4410, 4411; `league.historyReasons.forfeit` shown on a finished row; every string
  in `es` and `en`; `resume` kept in `sessionStorage` (T018, T019 green; `pnpm run build`)
- [ ] T028 [US4] O-F8 (approved): `--ws-ping-interval 10 --ws-ping-timeout 10` in
  `render.yaml`'s `startCommand`
- [ ] T029 [US4] Docs: AGENTS.md R18 names the grace as in-memory state lost on restart, and the
  4410 / 4411 codes next to 4409 / 4429; `docs/arquitectura.md` § Límites conocidos likewise

**Checkpoint**: US4 functional; T010–T019 green; delivery A's, L's and H's pins and spec 001's PvP
pins still green.

---

## Phase N: Traceability & Verification

- [ ] T090 Fill § Traceability rows FR-040, FR-041, FR-042, US4-AS1, US4-AS2, US4-AS3 with the
  tests above; mark delivery F `closed`; add `src/domain/pvp/outcome.py` (O-F9) to the
  spec's § Code Scope in the same PR
- [ ] T091 Review assertion adequacy: the resume test checks the *same* match continues (match id,
  answered items, scores) *and* the opponent was told both ways; the forfeit test checks the
  opponent's `game_end` arrives before `ends_at` *and* the rating moved once; the half-open test
  checks both the takeover *and* that a tab without `resume` is still refused; the tiebreak test
  checks `winner_id` stored, not only the frame
- [ ] T092 Verification (AGENTS.md § Verify): full suite on both engines, `db_sync_check.py`,
  `pnpm run build`, Playwright `league.spec.ts`, `check_traceability.py`, black, flake8
- [ ] T093 V1 check: the repositories are shared with V1; V1 does not call `finish_pvp_match`
  (PvP is V2 only) — the new optional argument changes nothing there

---

## Dependencies & Execution Order

- T000 (owner decisions) → T001 → T002, T003 (pins green) → T010–T019 written and failing → T020–T029 →
  T090–T093.
- T020 depends on T010, T011; T021 on T012 and T020; T022 on T013; T023 on T017; T024 on T014
  (resume) and T015; T025 on T014 (forfeit), T016, T023, T024 and T003; T026 on T024; T027 on T018,
  T019 and T020–T026; T028 per O-F8.

### Parallel Opportunities

T010–T019 are independent; T021 and T022 can proceed in parallel after T020; T023 is independent of
T020–T022.

## Notes

- **L's open issue (the ~40 s 4409 block on reconnect).** Resolved by T024 / T015 under O-F1: a
  reconnect carrying its `resume` token replaces the half-open socket at once. Under O-F1 (a) it is
  resolved in a match only; under O-F1 (c) without a token, US5-AS1 would have to be amended.
- Overlap with M (`game_start` payload) and G (FR-024's codes table gains 4410 / 4411): whichever PR
  lands second merges the frame and the table.
- A forfeit's close goes through H's `_persist_close`, so a database failure still ends as
  `not_saved` with `not_applied` in `game_end` (spec 001 FR-029c).
