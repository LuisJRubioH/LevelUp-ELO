# Tasks — spec 007, delivery G (who may enter the League)

**Plan**: [plan-g.md](plan-g.md) (approved; owner decisions O-G1 … O-G11 answered 2026-10-27, each as recommended). FR-020, FR-021,
FR-022, FR-023 and FR-024 are `[CHANGE]`; delivery G touches the entry and the lobby pinned by
delivery A (FR-001, FR-002, FR-005, FR-008), the one-socket rule of delivery L (FR-050), F's resume
path (FR-042) and M's queue (FR-030).

**Order.** G's code starts only after **M's code (PR #152) is merged** into `redesign`: G is
written on M's queue (`_pick_partner`, `_pair_on_step`, `LobbySlot`). F, L and H are merged. Under
O-G1 (a), G1 needs nothing else; **G2 (FR-022) also waits for spec 009 I1's code** (PR #157's
plan; `groups.institution`, N26 (a)), which itself follows spec 004 E3 (#73), and for the
institution of the League players' groups to be set (O-G5). Under O-G1 (b), all of G waits for
both.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[US2]**: User Story 2 — Only fair opponents can meet

---

## Phase 0: Owner decisions (Blocking)

- [x] T000 The owner answers O-G1 … O-G11 (plan-g § Decisions); record each answer in plan-g and
  set its status to approved. If O-G1 (a) is chosen, the owner also approves the spec amendment
  that splits delivery G into G1 and G2 (§ Deliveries, and the Delivery column of FR-022 and
  US2-AS3), in its own docs PR before any code; the tasks below then carry G1 or G2 as marked.
  Tests T010, T011, T013, T015 and T016 are written to the decided options; a test for a rejected option
  is dropped or rewritten before Phase 3. Done 2026-10-27: every recommended option was approved;
  the G1 / G2 split is amended in spec 007 by the same docs PR (#159), so the tasks below carry G1
  or G2 as marked. O-G5's tool is a spec 009 amendment (the admin edits a group's institution and
  grade; owner, 2026-10-27); G2 starts after it ships.

---

## Phase 1: Setup

- [x] T001 Confirm M (#152) is in `redesign` (and record whether E3 #73 and I1 are); branch `007-g`
  (or `007-g1` / `007-g2`) from it. Done 2026-10-27 for G1: M (#152) and this plan (#159) were
  not merged yet, so `007-g1` stacks on `origin/007-pvp-m` (which carries `redesign` with E3 #73
  and S #155 merged) plus `origin/007-plan-g`; I1 is not merged (G2's concern only).
- [x] T002 Create the empty module `src/domain/pvp/admission.py` and the constants
  `NOT_STUDENT_CODE = 4002`, `NOT_ENROLLED_CODE = 4004`, `BUSY_ELSEWHERE_CODE = 4412`,
  `NO_RATING_CODE = 4413`, `NO_INSTITUTION_CODE = 4414`, `SERVER_ERROR_CODE = 4500` in
  `api/websocket/pvp.py` (numbers per O-G4); no behaviour yet. G1: done with T020/T021 (the
  module was created by the implementation commit, after the failing tests); `NO_INSTITUTION_CODE`
  is G2's and is not defined in G1.
- [x] T003 Add `league_player(repo, course_id, *, elo=1000.0, institution=…, test_user=False)` to
  `tests/integration/conftest.py`: a student, enrolled, with a rating in one topic of the course
  (`set_rating`), and — G2 only — in a group whose institution is set. Move every PvP socket test's
  players to it **without changing any assertion**: `test_pvp_enrolment.py`,
  `test_pvp_waiting_player.py`, `test_pvp_answer_integrity.py`, `test_pvp_limits.py`,
  `test_pvp_history_display.py`, `test_spec007_f_match_flow.py`, `test_spec007_h_history.py`,
  `test_spec007_m_fair_matches.py` (keeps its own ratings), `test_spec007_s_league_stats.py` (if
  S is merged), `test_spec004_e2_display_names.py`, and E3's PvP cases if #73 is merged. Run them
  on the unchanged code: all green (they pass whether or not G exists).
  Done 2026-10-27 (G1): `league_player(repo, course_id, *more_courses, elo=1000.0, test_user=False,
  group_id=None)` — `more_courses` for L's two-course test, `group_id` for enrolment through a
  teacher's group. Moved: `test_pvp_enrolment.py`, `test_pvp_waiting_player.py`,
  `test_pvp_answer_integrity.py`, `test_pvp_limits.py`, `test_spec007_s_league_stats.py`,
  `test_spec004_e2_display_names.py`. F's `_players` and M's `_player` already seed a rating and
  were left as they are; `test_pvp_history_display.py`, `test_spec007_h_history.py` and E3's PvP
  cases open no League socket. One S test,
  `test_spec007_league_answers_leave_the_practice_figures_unchanged`, relied on an unrated pair
  to move no rating: its players are now rated and the pair is seeded past its daily cap
  (FR-031), so the match is still unrated and no assertion changed. Run on the unchanged code:
  66 passed (both engines).

---

## Phase 2: Pin Current Behaviour (Blocking)

- [x] T004 Run against the unchanged code (after T003) and record the green run here; they must
  stay green through every task below except the two flips of T012:
  - delivery A: `tests/integration/test_pvp_enrolment.py` (FR-001, FR-002),
    `test_pvp_waiting_player.py` (FR-005), `test_pvp_answer_integrity.py` (FR-003, FR-004),
    `test_pvp_repository.py`, `tests/unit/application/test_spec001_service.py` (FR-008 — the
    lobby's course rating read outside the lock; pending, never 1000),
    `tests/api/test_websocket_authorization.py`, `tests/unit/infrastructure/test_pvp_logic.py`;
  - delivery L: `tests/integration/test_pvp_limits.py` — in particular
    `test_spec007_a_second_league_socket_is_refused` (a **live** second socket, same or other
    course, is 4409: the live half of US2-AS4 already holds and must keep holding);
  - delivery F: `tests/integration/test_spec007_f_match_flow.py` (a `resume` still takes its place
    back before any G check; 4001 still triggers the screen's token refresh);
  - delivery H: `tests/integration/test_spec007_h_history.py`;
  - delivery M: `tests/unit/domain/test_spec007_m_matchmaking.py`,
    `tests/integration/test_spec007_m_fair_matches.py`;
  - spec 001: `test_spec001_course_topic_store.py::test_spec001_pvp_player_without_rated_topics_gets_zero`
    and the `test_pvp_logic.py` FR-029c pins (the residual `no_rated_topics` stays);
  - `frontend/e2e/league.spec.ts`.

  Recorded 2026-10-27 on the unchanged code (`6f86761`), both engines: the backend pins above
  plus S's and spec 004 E2/E3's PvP files, 317 passed; after T003's fixture move, the moved files
  66 passed.

**Checkpoint**: the entry, the lobby and the one-socket rule pinned — G can change them.

---

## Phase 3: User Story 2 — Only fair opponents can meet (Priority: P1)

**Goal**: an unrated student is sent to the subject's diagnostic instead of the queue; a test user
meets only test users; students meet only within their institution; a student already in a queue
or a match cannot enter another; every refusal says why.

**Independent Test**: `tests/integration/test_spec007_g_admission.py` (uvicorn, both engines;
students with and without a rating, test and real, of two institutions; M's window step shortened
with `monkeypatch`).

### Tests for User Story 2 (written first; each must FAIL before its implementation task)

- [x] T010 [P] [US2] `[CHANGE]` `test_spec007_entry_refusal_reasons` for FR-020, FR-022 (O-G5,
  O-G7) in `tests/unit/domain/test_spec007_g_admission.py` — **fails** before T020 (no function)
  — G1 (the `no_institution` cases: G2)
- [ ] T011 [P] [US2] `[CHANGE]` `test_spec007_test_users_meet_only_test_users` for FR-021 and
  `test_spec007_students_of_different_institutions_never_meet`,
  `test_spec007_institutions_compare_folded` for FR-022 (O-G6) in the same file — **fail** before
  T020 — FR-021: G1; FR-022: G2
- [x] T012 [P] [US2] `[CHANGE]` `test_spec007_each_refusal_has_its_own_code` for FR-024, US2-AS5 in
  `tests/integration/test_spec007_g_admission.py` (bad token 4001, teacher 4002, not enrolled
  4004, `get_user_enrollments` raising 4500) — **fails** before T021 (4001 for all). In the same
  task, **flip explicitly, citing FR-024** (and FR-001 as amended, T091):
  `tests/integration/test_pvp_enrolment.py::test_pvp_still_refuses_a_student_not_enrolled` and
  `tests/api/test_websocket_authorization.py::test_pvp_rejects_course_without_enrollment`, from
  4001 to 4004 — G1
- [x] T013 [P] [US2] `[CHANGE]` `test_spec007_a_student_without_rating_is_not_queued` for FR-020,
  US2-AS1 and `test_spec007_a_failed_rating_read_is_a_server_error` for FR-024 (O-G3) in the same
  file — **fail** before T022 (today: `waiting`, then a match; a failed read plays at 1000) — G1
- [x] T014 [P] [US2] `[CHANGE]` `test_spec007_a_test_user_and_a_real_student_never_meet` for
  FR-021, US2-AS2 and `test_spec007_two_test_users_meet` for FR-021 (O-G7) in the same file — the
  first **fails** before T023 (today they meet) — G1
- [ ] T015 [P] [US2] `[CHANGE]` `test_spec007_students_of_two_institutions_never_meet` for FR-022,
  US2-AS3 and `test_spec007_a_student_without_institution_is_refused` for FR-022 (O-G5) in the same
  file — **fail** before T024 — G2
- [x] T016 [P] [US2] `[CHANGE]` `test_spec007_a_student_away_in_a_match_cannot_queue_elsewhere`
  for FR-023, US2-AS4 and
  `test_spec007_a_student_who_finished_and_left_cannot_queue_until_the_match_ends` for FR-023
  (O-G8) in the same file — **fail** before T025 (today the new socket gets `waiting`) — G1
- [x] T017 [P] [US2] `[CHANGE]` `test_spec007_league_entry_profile_returns_raw_fields` for FR-021,
  FR-022 in `tests/integration/test_pvp_repository.py` (both engines) — **fails** before T026 (no
  method) — G1 (`is_test_user`), G2 (the institution)
- [x] T018 [P] [US2] `[CHANGE]` e2e «sin diagnóstico la Liga ofrece el diagnóstico (spec 007
  US2-AS1)», «una partida en curso impide otra búsqueda y dice por qué (spec 007 US2-AS4)» and
  «cada rechazo muestra su motivo (spec 007 US2-AS5)» in `frontend/e2e/league.spec.ts` (mocked
  socket closing with 4413, 4412, and 4001 / 4004 / 4500) — **fail** before T027 (unknown codes
  show the generic notice; 4001 shows the old catch-all text) — G1

Record here, per task, the failure seen on the unchanged code.

Recorded 2026-10-27 (G1), each run on the unchanged code (`6f86761`), both engines:
- T010, T011 (FR-021 part — `test_spec007_test_users_meet_only_test_users` written; the FR-022
  tests are G2's, so T011 stays open): `ModuleNotFoundError: src.domain.pvp.admission`.
- T012: `test_spec007_each_refusal_has_its_own_code` — teacher, not enrolled and a failing
  enrolment read all closed 4001 (`{'teacher': 4001, 'not_enrolled': 4001, 'server_error':
  4001}`); the two flipped pins got 4001 where they now expect 4004.
- T013: `test_spec007_a_student_without_rating_is_not_queued` — the unrated student got
  `waiting`; `test_spec007_a_failed_rating_read_is_a_server_error` — the socket was queued
  (`DID NOT RAISE WebSocketDisconnect`).
- T014: `test_spec007_a_test_user_and_a_real_student_never_meet` — the real student met the test
  user at entry (no `waiting`, timed out); `test_spec007_two_test_users_meet` passes on the
  unchanged code, as expected (it pins O-G7's allowed pair, not a change).
- T016: both tests — the new socket without `resume` got `waiting` instead of 4412.
- T017: `AttributeError: … has no attribute 'get_league_entry_profile'`.
- T018: the three e2e tests showed the generic «No pudimos conectar con la arena» for 4413 and
  4412, and the old catch-all text for 4001.

### Implementation for User Story 2

- [x] T020 [US2] `src/domain/pvp/admission.py`: `institution_key` (spec 004's folding rule, exposed
  from `src/domain/identity.py` without changing its behaviour), `entry_refusal`, `may_meet`
  (T010, T011 green; `tests/unit/test_architecture_layers.py` green)
- [x] T021 [US2] FR-024: `pvp_ws` maps each refusal to its code — `HTTPException` from
  `authenticate_access_token` → 4001 (E3's expiry → 4403 if #73 is in), role → 4002, not enrolled →
  4004, any other exception → 4500 (T012 green, including the two flipped pins)
- [x] T022 [US2] FR-020: in `_play`, the course rating read decides entry before the slot is
  built — None → 4413; a failed read → 4500 (replacing M's fallback to 1000 at entry); the read is
  the one the lobby already makes, outside `_lock` (T013 green; FR-008 pins green)
- [x] T023 [US2] FR-021: `LobbySlot.is_test_user` from the entry profile; `_pick_partner` filters
  through `admission.may_meet` before `pick_opponent` — the one pairing point, on entry and on
  each window step (T014 green; M's pins green)
- [ ] T024 [US2] FR-022 (G2): `LobbySlot.institution` (the folded key); `may_meet` compares it for
  real students; a real student with no key → 4414 (T015 green)
- [x] T025 [US2] FR-023: in `pvp_ws`, after F's resume path and with L's 4409 check, with no `await`
  between check and claim: a student with a slot in any queue or a player of a match in
  `_matches` → 4412 (T016 green; L's and F's pins green)
- [x] T026 [US2] `get_league_entry_profile(user_id)` in both repositories, identical signature,
  `@_read_only` (G1: `is_test_user`, institution None; G2: the main group's institution);
  `tests/integration/test_spec002_d2_connections.py` lists it; `python scripts/db_sync_check.py`
  (T017 green)
- [x] T027 [US2] Frontend: `CLOSE_NOTICES` 4001 → `sessionExpired`, 4002, 4004, 4412, 4413, 4414;
  on 4413 a button to `/student/course/{courseId}`; i18n `es` and `en`
  (`league.closeNotices.*`, `league.goToDiagnostic`; `authFailed` removed); colours from tokens
  (T018 green; `pnpm run build`)
- [x] T028 [US2] Docs: AGENTS.md R19 (an unrated student does not enter the League; the 1000 no
  longer drives a League expectation at entry) and R18 (the League's close codes beside 4409 /
  4429); retire plan-m's O-M10 note in AGENTS if it was copied there

G1 notes (2026-10-27): T020 delivers `entry_refusal(rated=, is_test_user=)` and `may_meet` on
`is_test_user` only; `institution_key` and the `no_institution` refusal are G2's (T024).
T021: a first frame that is late, not JSON or not an object keeps 4001 as before (no session was
presented); a teacher still pending approval is refused by `authenticate_access_token` and so gets
4001. T025 reuses `players_in_play()` (spec 004 E3), which already reads every lobby queue and every
match in memory. T027: the way to the diagnostic is a link styled as an outlined action
(`.pv-diagnostic`), since it navigates. Tests: `live_api` now clears the League's in-memory state
when its server stops — on SQLite each test's database reuses the same user ids, so a match left in
its grace by one test made a later test's student busy (4412).

**Checkpoint**: US2 functional; T010–T018 green; delivery A's (with the two flips), L's, F's, H's,
M's and spec 001's PvP pins still green.

---

## Phase N: Traceability & Verification

- [x] T090 Fill § Traceability rows FR-020, FR-021, FR-022, FR-023, FR-024, US2-AS1 … US2-AS5 with
  the tests above (FR-023 and US2-AS4 also cite L's
  `test_spec007_a_second_league_socket_is_refused` for the live-socket half); mark delivery G (or
  G1 / G2) `closed`; add `src/domain/pvp/admission.py` to § Code Scope — G1 done 2026-10-27:
  FR-020, FR-021, FR-023, FR-024, US2-AS1, AS2, AS4, AS5 filled; G1 `closed`; G2 `planned` with
  FR-022 and US2-AS3 `PENDING`
- [x] T091 In the same PR, the approved spec amendments: spec 007 FR-001 («…close any other socket
  with the code of its reason (FR-024)»); spec 001 FR-029c (the text approved in spec 007
  § Dependencies); spec 001 FR-029a per O-G11; spec 007 § Key Entities (the institution is the main
  group's, N26 (a)) — G1 done 2026-10-27: FR-001, spec 001 FR-029a and FR-029c (and its Out of
  Scope follow-up, resolved); § Key Entities (the institution) is left for G2, which reads it
- [x] T092 Review assertion adequacy: the no-rating test checks that no slot remains (a rated
  student who joins after is not matched with them), not only the code; the test-user and
  institution tests check both pairing paths (entry and a window step) and that the eligible pair
  does meet; the busy test checks the first match's grace and forfeit are untouched; the refusal
  test checks four distinct codes, and the e2e test three distinct texts — G1 done: the no-rating
  test asserts nothing is sent before 4413, the student is not in play, and a rated student who
  joins waits alone; the test-user test passes several window steps and checks the stored match is
  the real pair's; the busy tests check no `opponent_back`, the forfeit, and a normal queue after;
  the refusal tests check four codes, the e2e test four distinct texts
- [x] T093 Verification (AGENTS.md § Verify): full suite on both engines, `db_sync_check.py`,
  `pnpm run build`, Playwright `league.spec.ts`, `check_traceability.py`, black, flake8 — G1:
  see the PR's verification (full suite both engines, full Playwright)
- [x] T094 V1 check: the new repository read is unused by V1 (PvP is V2 only); nothing else shared
  with V1 changes — G1: `get_league_entry_profile` is called only by `api/websocket/pvp.py`
- [ ] T095 Production note in the PR description (plan-g § Production impact): no schema, no
  setting, no `render.yaml` change; for G2 (or G under O-G1 (b)), the institutions of the League
  players' groups are set before merge, or those students are refused 4414

---

## Dependencies & Execution Order

- M's code merged (#152) → T000 → T001–T003 → T004 (pins green) → T010–T018 written and failing →
  T020–T028 → T090–T095.
- T020 depends on T010, T011; T021 on T012; T022 on T013 and T026; T023 on T014, T020 and T026;
  T024 on T015, T020, T026 and (G2) I1 merged; T025 on T016; T026 on T017; T027 on T018 and
  T021–T025; T091 on T000.
- Under O-G1 (a), G1 = T010 (minus `no_institution`), T011 (FR-021), T012–T014, T016–T018,
  T020–T023, T025–T028; G2 = the FR-022 parts of T003, T010, T011, T017, T020, T026 and T015,
  T024, each with its own Phase N.

### Parallel Opportunities

T010–T018 are independent; T021 and T026 can proceed in parallel; T027 waits for the codes.

## Notes

- **L's live-socket rule already holds for a second tab in any subject** (US5-AS1, "another
  course too"); G adds only the case L cannot see: a match of the student still running with no
  live socket (F's grace, O-F4).
- **F's resume is not re-admitted.** A valid `resume` takes its place back before every G check;
  rating, institution and busy are checked only for a new entry.
- **E3 (#73)**: if merged first, its 4403 at entry stays; if merged after, the PR that lands second
  keeps both 4403 and G's codes in `pvp_ws` and `CLOSE_NOTICES`.
- **S (#155)** touches the repositories and `test_spec002_d2_connections.py`, not `pvp.py`;
  whichever lands second merges the read-only list.
