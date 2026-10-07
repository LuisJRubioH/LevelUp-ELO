---

description: "Tasks for spec 001 — ELO engine"
---

# Tasks: ELO Engine

**Input**: `specs/001-elo-engine/` — spec.md, plan.md, research.md (R1–R18), data-model.md,
contracts/api.md, contracts/domain.md, quickstart.md

**Tests are MANDATORY** (constitution Principle I; spec § Traceability). Every FR and acceptance
scenario maps to a test task below — reused (assertions checked) or new.

| Tag | Test kind | Before implementation | After |
|---|---|---|---|
| `[AS-IS]` | characterization (Phase 2) | **PASS on unchanged code** | still pass |
| `[CHANGE]` | behaviour change (story phases) | **FAIL** | pass |

Pinned tests that a `[CHANGE]` deliberately alters are listed as **flip** tasks next to the change
that causes them; they cite the FR. Never edit a pinned assertion silently.

**Test naming**: every new test function name contains `spec001`, so
`pytest -k spec001` selects them (quickstart §1). Repository tests use the two-engine `repo`
fixture (SQLite + PostgreSQL) and must give identical results (constitution IV).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: different files, no dependency on an unfinished task
- **[USn]**: user story from spec.md
- Requirement IDs are named in every test task

## Path Conventions (Oulad)

`src/domain/`, `src/application/`, `src/infrastructure/persistence/{sqlite,postgres}_repository.py`,
`api/`, `frontend/src/`, V1 (frozen) `src/interface/streamlit/`. Tests: `tests/unit/<layer>/`,
`tests/integration/` (both engines), `tests/api/`, `frontend/e2e/`.

---

## Phase 1: Setup

- [ ] T001 Move the two-engine `repo` fixture, `_postgres_repo` dependency and the `student`/`_sql` helpers from `tests/integration/test_elo_single_source.py` into `tests/integration/conftest.py` (behaviour unchanged; `test_elo_single_source.py` imports nothing new) and add seeding helpers `make_course(repo, course_id, name, block, topics=[...])`, `enroll(repo, user_id, course_id)`, `answer(repo, user_id, item_id, correct, seconds)` used by every spec001 integration test, and a single read helper `rating_of(repo, user_id, course_id, topic)` that every pin uses instead of querying a rating table directly (today it reads `student_topic_elo` by the key the code writes)
- [ ] T002 [P] Confirm the SQLite reconciliation command in `specs/001-elo-engine/quickstart.md` §3 (`DB_PATH=... python -c "...SQLiteRepository..."`) runs against a copy of `data/elo_database.db`; correct the quickstart if not

---

## Phase 2: Pin Current Behaviour (Blocking)

**Purpose**: characterize every `[AS-IS]` requirement the refactor touches. **Every task here must
pass against the unchanged code** (record the green run in T020). A pin that fails on today's code
is a finding for `/speckit-clarify`, not something to fix here.

### Reused tests (verify assertions prove the FR; strengthen in place if partial)

- [ ] T003 [P] Reuse for FR-001: `tests/unit/domain/test_elo_model.py::TestExpectedScore` (all 5) — confirm they assert the exact formula; record in § Traceability
- [ ] T004 [P] Reuse for FR-017, FR-018: `tests/unit/domain/test_item_selector.py` (`TestZDPSelection`, `TestFisherInformation`, `TestZDPPreFiltering`, `TestControlledVariety`); add `test_spec001_band_widens_by_005_up_to_10_steps_then_whole_pool` there if widening count is not asserted (US2-AS2)
- [ ] T005 [P] Reuse for FR-016, FR-019 edge "topic with no items": `tests/unit/application/test_student_service.py::TestGetNextQuestion::test_variety_preserves_unseen_priority_and_session_exclusions`, `::TestTopicFilter::test_unknown_topic_filter_falls_back_to_full_pool`, `::TestGetNextQuestion::test_preserves_selected_identity_when_difficulties_match` (edge: equal difficulty)
- [ ] T006 [P] Reuse for FR-007, FR-008, FR-010, FR-021, FR-022 (once), FR-028, US1-AS3, US1-AS6, US3-AS3, US4-AS2: `tests/integration/test_elo_single_source.py` (`test_an_invalid_attempt_does_not_move_the_rating`, `test_concurrent_answers_on_the_same_item_compose_serially`, `test_diagnostic_baseline_survives_until_the_first_practice`, `test_a_validated_procedure_delta_is_applied_exactly_once`, `test_global_elo_stays_the_average_of_the_canonical_topics` — FR-028: aggregate derived from stored ratings, not attempts)
- [ ] T007 [P] Reuse for FR-025 (once), FR-027, US5-AS2, US5-AS3: `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess` (`test_closing_a_match_twice_applies_the_delta_once`, `test_matches_orphaned_by_a_restart_are_closed`, `test_a_live_match_is_left_alone`)
- [ ] T008 [P] Reuse for FR-023 (ownership), US4-AS4: `tests/api/test_procedure_grading.py::test_other_teacher_cannot_grade_or_view_submission`, `::test_reassignment_between_lookup_and_update_prevents_grading`
- [ ] T009 [P] Reuse for FR-011, US1-AS7, edge "diagnostic duplicate/foreign item": `tests/api/test_student.py::test_invalid_answer_context_has_no_side_effects`, `::test_answer_without_legacy_item_data`, `::test_diagnostic_rejects_noncanonical_payload`
- [ ] T010 [P] Reuse for FR-012 (PostgreSQL): `tests/integration/test_postgres_production_guards.py` idempotency test (lines ~250–290); its SQLite twin is created in T013

### New characterization tests (must PASS on unchanged code)

- [ ] T011 [P] `[AS-IS]` FR-002, FR-003, FR-004, US1-AS1, US1-AS2, edge "RD floor 30" in `tests/unit/domain/test_spec001_engine_pins.py`: `VectorRating().update` from defaults with D=1000 gives 1016.00 / 984.00 and RD 332.5; RD at 30 stays 30 and moves 32·30/350·0.5 = 1.371…
- [ ] T012 [P] `[AS-IS]` FR-005, FR-006, FR-015-today (failure swallowed — pinned only to be flipped in T034) in `tests/unit/application/test_spec001_service_pins.py`: drive `StudentService.process_answer` with a fake repository whose `save_answer_transaction` runs `compute` on a fixed state; assert item difficulty 984/1016 for US1-AS1/AS2 and that the returned `item_rd` equals the input
- [ ] T013 [P] `[AS-IS]` FR-012, FR-013, FR-014, FR-032, US1-AS4, US1-AS5, US6-AS4, edge "retry key empty or > 128 chars" in `tests/api/test_spec001_answer_pins.py`: replay with same key returns stored result and attempt count stays 1; same key + other option → 409; neither `/answer` nor `/exam/submit` responses contain `correct_option`; `/exam/submit` leaves every rating unchanged; key `""` and 129 chars → 400
- [ ] T014 [P] `[AS-IS]` FR-016 (cooldown ≥ 3), FR-019, US2-AS3, US2-AS4, US2-AS5 in `tests/unit/application/test_spec001_service_pins.py`: failed item eligible only when `session_questions_count − failed_at ≥ 3`; correct-in-session never offered; exhausted pool at rating 1800 → `(None, "mastery")`, at 1799 → pool offered again
- [ ] T015 [P] `[AS-IS]` FR-017 worked example US2-AS1 in `tests/unit/domain/test_spec001_engine_pins.py`: rating 1000, items 600/950/1100/1600 → always 950 over 50 seeded draws
- [ ] T016 [P] `[AS-IS]` FR-020, FR-031a, US3-AS1, US3-AS2, US3-AS4 in `tests/api/test_spec001_answer_pins.py`: diagnostic with one correct item at difficulty 1200 → topic baseline 1022; all wrong at difficulty < 1100 → floor 760; skipped answer changes nothing; response carries a league label from Bronce/Plata/Oro/Diamante
- [ ] T017 [P] `[AS-IS]` FR-022, FR-023 (grade range), FR-024, US4-AS1, US4-AS3, US4-AS5, edge "grade 50" in `tests/integration/test_spec001_repository_pins.py` (both engines): grade 80 → +6.0 on the item's topic; grade 50 → 0 and `elo_applied = 1`; grade 101 → `ValueError`, nothing changes; storing an `ai_proposed_score` changes no rating
- [ ] T018 [P] `[AS-IS]` FR-025 (formula), US5-AS1, US5-AS4 in `tests/integration/test_spec001_repository_pins.py` and `tests/unit/domain/test_spec001_engine_pins.py`: `api.websocket.pvp._elo_deltas(1000, 1000)` = (12.0, −12.0), draw = (0.0, 0.0); after `finish_pvp_match` the next practice answer starts from the post-match rating
- [ ] T019 [P] `[AS-IS]` FR-007, FR-008 boundaries, FR-028e, FR-028g, edges "exactly 3 s / 600 s valid", "missing time = 30 s" in `tests/integration/test_spec001_repository_pins.py` (both engines): 3.0 and 600.0 move the rating, 2.99 and 600.01 do not; `time_taken=None` moves it; `get_latest_attempts`/`get_student_attempts_detail` return one row per attempt with its `elo_after`; a saved `weekly_rankings` row is returned unchanged by `get_ranking_history`
- [ ] T020 Run `pytest tests/ --ignore=tests/e2e -q -k "spec001 or elo_single_source or pvp_repository or item_selector or elo_model or student_service or procedure_grading"` on the **unchanged code**; paste the green summary into this task; stop if anything is red

**Checkpoint**: current behaviour pinned (depends on T001–T019).

---

## Phase 3: Foundational (Blocking for all stories)

**Purpose**: domain functions, the new store and the single reader. No behaviour change yet:
Phase 2 pins stay green after each task.

- [ ] T021 [P] `[CHANGE]` tests first in `tests/unit/domain/test_spec001_domain.py` for contracts/domain.md: `rating_delta`, `next_rd`, `item_difficulty_delta`, `is_valid_response_time` (None→30, 3 and 600 inclusive), `pvp_deltas`, `diagnostic_tier`, `diagnostic_baseline` (floor 760), `course_rating` (empty → None), `overall_rating` (None values skipped; all None → None; US6-AS1 → 1100), `rank_for` (None → None; 16 labels ascending), `RANKS`. Must FAIL (functions absent)
- [ ] T022 Implement in `src/domain/elo/model.py`: `rating_delta`, `next_rd`, `item_difficulty_delta`, `is_valid_response_time`, `pvp_deltas`, `diagnostic_tier`, `diagnostic_baseline`; make `RatingModel.update` and `VectorRating.update` delegate to them; remove `impact_modifier` from `VectorRating.update` (T021 passes for these; Phase 2 pins green)
- [ ] T023 [P] Create `src/domain/elo/aggregation.py` (`course_rating`, `overall_rating`) and `src/domain/elo/ranks.py` (`RANKS` copied verbatim from `api/routers/student.py::_RANK_THRESHOLDS`, `rank_for`); `tests/unit/test_architecture_layers.py` stays green
- [ ] T024 Remove dead code (research R15): `calculate_dynamic_k`, `update_elo`, `StudentELO` from `src/domain/elo/model.py`; unused import in `src/interface/streamlit/views/student_view.py:21`; `get_user_history_elo` from both repositories. **Flip** (delete, citing constitution VII): `tests/unit/domain/test_elo_model.py::TestDynamicKFactor`, `::TestUpdateElo`, `tests/unit/domain/test_vector_elo.py::TestVectorRatingUpdate::test_zero_impact_modifier_gives_no_rating_change`, `tests/unit/application/test_student_service.py::TestProcessAnswer::test_cognitive_modifier_is_1_when_disabled`
- [ ] T025 Point callers at the domain: `api/routers/student.py` uses `diagnostic_tier`/`diagnostic_baseline` and `rank_for` (delete `_diff_tier`, `_RANK_THRESHOLDS`, `_elo_to_rank`); `api/websocket/pvp.py` uses `pvp_deltas` (delete `_elo_deltas`, `K`); update T016/T018 pins to import from the new location **without changing their asserted numbers**
- [ ] T026 Add table `student_course_topic_elo` to `init_db`/`_migrate_db` in **both** `src/infrastructure/persistence/sqlite_repository.py` and `postgres_repository.py` exactly per data-model.md: PK `(user_id, course_id, topic)`; `current_elo REAL NOT NULL` "≥ 0"; `rd REAL NOT NULL DEFAULT 350` "30 ≤ rd ≤ 350"; `origin TEXT NOT NULL` one of `practice · diagnostic · legacy_topic_row · legacy_course_row · procedure`; `approximate` "NOT NULL DEFAULT false"; `legacy_source_key TEXT NULL`; `reconciled_at TIMESTAMP NULL`; `created_at`, `updated_at`; index `(user_id, course_id)`. Additive only (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`)
- [ ] T027 Add `pvp_matches.elo_reason_p1`, `elo_reason_p2` `TEXT NULL` in both repositories (PostgreSQL `ADD COLUMN IF NOT EXISTS`; SQLite `_add_column_if_not_exists`)
- [ ] T028 [P] `[CHANGE]` tests first in `tests/integration/test_spec001_course_topic_store.py` (both engines): `get_course_topic_ratings(user, course_id=None)` returns only new-table rows with `origin`/`approximate`; `get_current_context_course_ids(user)` = enrollments ∩ catalogue for level+grade (semillero grade 6 student enrolled in grade 6 and 7 courses → only grade 6). Must FAIL
- [ ] T029 Implement `get_course_topic_ratings` and `get_current_context_course_ids` in both repositories; declare them in `src/application/interfaces/repositories.py`; update `tests/unit/application/test_repository_contracts.py`; run `python scripts/db_sync_check.py` (T028 passes)
- [ ] T030 [P] `[CHANGE]` tests first in `tests/unit/application/test_spec001_service.py`: `StudentService.ratings_view(user)` with a fake repo returns `{overall, overall_status, rank_label, courses:[{course_id, rating, rank_label, current_context, topics}]}`; US6-AS1 numbers; no current-context rated course → `overall=None`, `overall_status="pending_diagnostic"`, `rank_label=None`. Must FAIL
- [ ] T031 Implement `StudentService.ratings_view` in `src/application/services/student_service.py` using `aggregation` and `ranks` (T030 passes)

**Checkpoint**: domain, store and reader exist; all Phase 2 pins green.

---

## Phase 4: User Story 1 — A practice answer updates my rating correctly (P1) 🎯 MVP

**Independent test**: answers on one item move the item's course-topic rating per FR-001…006 and
report honestly (quickstart §4 step 5).

### Tests for US1 (`[CHANGE]` — must FAIL first)

- [ ] T032 [P] [US1] `[CHANGE]` FR-029, US1-AS1, US1-AS2 in `tests/integration/test_spec001_course_topic_store.py` (both engines): an answer on an item of course C, topic T writes only `student_course_topic_elo(user, C, T)` with `origin='practice'` (1016.00/984.00), writes nothing to `student_topic_elo` or `users.current_elo`, and the same topic label in course C' is untouched
- [ ] T033 [P] [US1] `[CHANGE]` FR-009, FR-008 in `tests/api/test_spec001_api.py`: answer with `time_taken=2` → `delta_elo == 0`, `elo_after == elo_before`, `elo_valid == false`; stored attempt has `elo_after == elo_before`. Must FAIL on the code before this story's implementation
- [ ] T034 [P] [US1] `[CHANGE]` FR-015 in `tests/unit/application/test_spec001_service.py`: when `award_achievement` raises, `process_answer` returns its result and `caplog` contains an ERROR record. **Flip** the T012 "swallowed" assertion (FR-015). Must FAIL on the code before this story's implementation

### Implementation for US1

- [ ] T035 [US1] Change `save_answer_transaction(user_id, item_id, compute, request_id=None, request_fingerprint=None)` in **both** repositories: lock users→items (unchanged order), read the item's `course_id`, `topic`, `difficulty`, `rating_deviation` and the row `(user, course_id, topic)` (default 1000/350), call `compute`, insert the attempt with the item's topic, write rating + item only if `attempt_data["elo_valid"]`; delete `_tiempo_valido`, `_set_topic_elo`, `_refresh_global_elo` (contracts/domain.md); re-point the T001 helper `rating_of` to `student_course_topic_elo(user, course_id, topic)` — this is not an assertion change, the pinned numbers stay
- [ ] T036 [US1] Rewrite `StudentService.process_answer` (`vector_rating`, `elo_topic` removed): `compute` uses `rating_delta`, `next_rd`, `item_difficulty_delta`, `is_valid_response_time`; invalid → before = after; return `elo_before`, `elo_after`, `rd_after`, `elo_valid`; badge failure → `logger.exception` (T034)
- [ ] T037 [US1] Update `/student/answer` in `api/routers/student.py` and `AnswerResponse` in `api/schemas/student.py`: accept and ignore `elo_topic` (mark deprecated in the Field), add `elo_valid`, keep idempotency and 400/409 behaviour, drop `impact_modifier` from `cog_data` (contracts/api.md)
- [ ] T038 [US1] **Flip** with FR-029 cited: `tests/unit/application/test_student_service.py::TestProcessAnswer::test_elo_topic_overrides_item_topic` (delete: the key is always the item's course+topic), `::test_save_answer_transaction_called_once` and `::test_cog_data_contains_expected_fields` (new signature/fields); `tests/integration/test_elo_single_source.py` tests that read `student_topic_elo`/`users.current_elo` now read `student_course_topic_elo` — same asserted numbers
- [ ] T039 [US1] `python scripts/db_sync_check.py`; Phase 2 pins + T032–T034 green

**Checkpoint**: US1 complete and independently testable.

---

## Phase 5: User Story 2 — The next item fits my level (P1)

**Independent test**: with a fixed pool and seed, the selection rating is the topic rating (topic
practice) or the derived course rating (course practice).

- [ ] T040 [P] [US2] `[CHANGE]` FR-029a (selection), FR-004 in `tests/unit/application/test_spec001_service.py`: `get_next_question` with `topic_filter=T` uses the (C,T) rating; without filter uses `course_rating` of C (1000 when no rated topic); a diagnostic course average is no longer used as a seed. Must FAIL
- [ ] T041 [US2] Implement the selection rating in `StudentService.get_next_question` (signature per contracts/domain.md) and in `/student/next-question` (`api/routers/student.py`); remove the diagnostic course seed from `api/dependencies.py::build_vector_rating` (delete the function if no caller remains)
- [ ] T042 [US2] **Flip** with FR-004 cited: `tests/api/test_student.py::test_first_practice_uses_diagnostic_rating` — the first practice now starts from the diagnostic's **topic** baselines, not a course seed

**Checkpoint**: US1 + US2 work.

---

## Phase 6: User Story 3 — The diagnostic sets my starting point (P2)

- [ ] T043 [P] [US3] `[CHANGE]` FR-029, FR-021 in `tests/integration/test_spec001_course_topic_store.py` (both engines): diagnostic for course C writes `(user, C, T)` rows with `origin='diagnostic'`; a topic with practice in C is not overwritten; the same label in another course is unaffected. Must FAIL
- [ ] T044 [US3] Add `set_topic_rating_baseline(user_id, course_id, topic, elo, rd=350)` and `has_practice_attempts(user_id, course_id, topic)` to both repositories (replace `set_topic_elo_baseline` and the old `has_practice_attempts` signature); update `/student/diagnostic/{course_id}/submit` to use them and `diagnostic_baseline`; update interface + contract test; `db_sync_check`

---

## Phase 7: User Story 4 — A teacher's grade adjusts my rating once (P2)

- [ ] T045 [P] [US4] `[CHANGE]` FR-029, US4-AS1 in `tests/integration/test_spec001_course_topic_store.py` (both engines): grading 80 adds +6.0 to `(student, item.course_id, item.topic)`; absent row created at 1006.0 with `origin='procedure'`; floor 0; once only. Must FAIL
- [ ] T046 [US4] Change the bump in `validate_procedure_submission` (both repositories) to the new table; remove `_bump_topic_elo` writes to `student_topic_elo`; `db_sync_check`

---

## Phase 8: User Story 5 — A finished PvP match adjusts my rating once (P3)

- [ ] T047 [P] [US5] `[CHANGE]` FR-029b, FR-029c, US5-AS5 in `tests/integration/test_spec001_course_topic_store.py` (both engines): delta +12 adds +12 to **every** rated topic of the course and the course rating moves by exactly 12; player with no rated topic → ratings unchanged, `elo_delta_pX = 0`, `elo_reason_pX = 'no_rated_topics'`, opponent applied; second close changes nothing; return value carries applied deltas. Must FAIL
- [ ] T048 [P] [US5] `[CHANGE]` FR-026 in `tests/unit/application/test_spec001_service.py` (or `tests/api/test_spec001_api.py` via the lobby helper): the lobby rating for a course is `course_rating` of that course, not an all-course average. Must FAIL
- [ ] T049 [US5] Implement `finish_pvp_match` (both repositories) per contracts/domain.md; `api/websocket/pvp.py`: lobby rating from `ratings_view`/course rating, `game_end` sends applied `elo_delta` and `elo_reason` (`"not_applied"` with 0 when persistence fails); `frontend/src/hooks/usePvpMatch.ts` type gains `elo_reason`
- [ ] T050 [US5] **Flip** with FR-029/029b cited: `tests/integration/test_pvp_repository.py::TestPvpMatchLifecycle::test_finish_updates_current_elo`, `::test_elo_never_negative`, `::TestPvpStateSurvivesTheProcess::test_result_moves_the_canonical_rating_not_just_the_average` now assert on `student_course_topic_elo`

---

## Phase 9: User Story 6 — My rating reads the same everywhere (P3)

### Tests for US6 (`[CHANGE]` — must FAIL first)

- [ ] T051 [P] [US6] `[CHANGE]` FR-028a, FR-028b, FR-028c, US6-AS1, US6-AS5, US6-AS6 in `tests/api/test_spec001_api.py`: `/student/stats` returns `global_elo` 1100 for the US6-AS1 fixture; a promoted student with no rated new-grade course gets `global_elo: null`, `overall_status: "pending_diagnostic"`, `rank_label: null`; earlier-grade course listed with `current_context: false` and unchanged rating; no response field reports a difference between overall ratings. Must FAIL on the code before this story's implementation
- [ ] T052 [P] [US6] `[CHANGE]` FR-028, SC-005 "canonical reads" in `tests/integration/test_spec001_course_topic_store.py` (both engines) + `tests/api/test_spec001_api.py`: one fixture student; stats, teacher dashboard, teacher student report, exam snapshot, AI context builder and rankings all report the same overall/course rating as `ratings_view`; editing `student_topic_elo` and `users.current_elo` by hand changes none of them (FR-036). Must FAIL on the code before this story's implementation
- [ ] T053 [P] [US6] `[CHANGE]` FR-028d in `tests/integration/test_spec001_course_topic_store.py` (both engines): `get_group_ranking(group, course_id=C)` ignores ratings and attempts of other courses (**fails on today's code: the filter does not filter**); orders by derived rating; unrated students last and marked pending
- [ ] T054 [P] [US6] `[CHANGE]` FR-028f in `tests/integration/test_spec001_course_topic_store.py` (both engines): global/course/weekly rankings rank by derived rating; a student active this week with a lower rating appears, an inactive one with a higher rating does not; `get_student_rank` equals the student's index in the corresponding list under the same participation rule. Must FAIL on the code before this story's implementation
- [ ] T055 [P] [US6] `[CHANGE]` FR-031, US6-AS3 in `tests/api/test_spec001_api.py`: `GET /api/meta/ranks` (no auth) returns the 16 labels ascending; for one student `rank_label` is identical in `/student/stats`, `/teacher/dashboard`, `/teacher/student/{id}`, `/student/group-ranking`. Must FAIL on the code before this story's implementation
- [ ] T056 [P] [US6] `[CHANGE]` FR-030, US6-AS2 (SC-006) in `tests/api/test_spec001_api.py`: `/student/next-question` returns `preview`; answering that item correctly in 20 s returns `delta_elo == preview.on_correct` (±0.1); incorrectly → `preview.on_wrong`. Must FAIL on the code before this story's implementation
- [ ] T057 [P] [US6] `[CHANGE]` FR-033, FR-034, FR-034a, FR-034b, FR-035, FR-036, SC-008 in `tests/integration/test_spec001_reconciliation.py` (both engines), fixtures built from the real ambiguity (course name == topic label; topic shared by two courses): existing new-table rows untouched; source (a) topic-label row used only with attempts under that key on that course or that course's diagnostic; source (b) course row chosen by most recent `updated_at`, course-id on tie, never summed; reconciled rows `approximate=true` with `legacy_source_key`; legacy row with no eligible context creates nothing; legacy rows unchanged; second run creates 0 rows. Must FAIL on the code before this story's implementation
- [ ] T058 [P] [US6] Playwright (mocked API, verifies frontend flows only) `frontend/e2e/spec001-ratings.spec.ts`: Practice shows the API `preview` (US6-AS2); Stats shows "pending diagnostic" when `overall_status` is pending and lists history courses (US6-AS5/AS6); teacher Dashboard and Groups render the API `rank_label` (US6-AS3); Home lists ranks from `/api/meta/ranks`

### Implementation for US6

- [ ] T059 [US6] Implement `_reconcile_legacy_ratings()` in both repositories per research R10 and call it from `_bootstrap_schema` after existing backfills (PostgreSQL under the existing advisory lock); `db_sync_check` (T057 passes)
- [ ] T060 [US6] Route every V2/shared reader of research R18 through `ratings_view` / `get_course_topic_ratings`: `/student/stats` (remove the twin-dedupe hack), `/student/map/{course_id}`, `/student/exam/submit` snapshot, `/ai/socratic` context (`api/routers/ai.py`), `teacher_service.get_student_dashboard`, `teacher_service.generate_ai_analysis`, `get_teacher_dashboard_stats`, `get_student_elo_summary`; delete `get_latest_elo_by_topic`, `get_topic_elo_map`, `aggregate_global_elo` once unused; update interface + contract test
- [ ] T061 [US6] Rewrite `get_group_ranking` (both repositories) to return eligible user ids + course-topic rows; order in the application layer by `course_rating`/`overall_rating`; fix the course filter (T053 passes)
- [ ] T062 [US6] Migrate V1-only rankings in both repositories — `get_global_ranking`, `get_course_ranking`, `get_weekly_ranking`, `get_student_rank` — participation from `attempts` (unchanged windows), rating from `student_course_topic_elo` via the domain aggregation; `save_weekly_ranking` stores the migrated values; `get_ranking_history` untouched (FR-028g) (T054 passes)
- [ ] T063 [US6] API schemas and routes per contracts/api.md: `StudentStatsResponse` (`global_elo: float | None`, `overall_status`, `course_ratings`), teacher `StudentSummary`/`StudentReportResponse` (`global_elo: float | None`, `rank_label`, `overall_status`), `NextQuestionResponse.preview`, new `GET /api/meta/ranks` (public router, rate-limited like other public routes)
- [ ] T064 [US6] Frontend: `Practice.tsx` uses `preview` (delete `estimateEloDelta`); `Stats.tsx` shows "pending diagnostic" and history courses; `Teacher/Dashboard.tsx`, `Teacher/Groups.tsx` use API `rank_label` (delete `RANKS`, `rankFor`); `Home.tsx` fetches `/api/meta/ranks` (delete `RANKS`); `RankBadge.tsx` keeps the only colour map keyed by the 16 labels; i18n keys in `frontend/src/i18n/locales/es.ts` and `en.ts`; `frontend/src/api/{student,teacher}.ts` types; `pnpm run build` green (T058 passes)

**Checkpoint**: all six stories work; T051–T058 green.

---

## Phase 10: V1 compatibility (frozen interface, shared-layer changes)

- [ ] T065 `[CHANGE]` regression test first in `tests/unit/interface/test_spec001_v1_compat.py`: reproduce `student_view.handle_answer_topic`'s call into `StudentService.process_answer` (new signature) against a SQLite repo and assert the rating lands on the item's `(course_id, topic)`; import `src.interface.streamlit.app` dependencies and construct `StudentService`/`TeacherService` as `app.py` does (smoke). Must FAIL before T066
- [ ] T066 Adapt V1 call sites only: `src/interface/streamlit/views/student_view.py:73, 385-393, 1787, 1816, 1839, 1935, 1945` and `teacher_view.py:656, 960` to the new service/reader signatures; V1 rank labels and preview untouched (research R16) (T065 passes)

---

## Phase N: Traceability & Verification

- [ ] T067 Fill spec.md § Traceability: every FR (incl. lettered) and every scenario → collected pytest node id or Playwright title from the tasks above; no `PENDING`
- [ ] T068 Review assertion adequacy row by row; strengthen any test that proves only part of its FR (record which)
- [ ] T069 Full verification (AGENTS.md § Verify): `pytest tests/ --ignore=tests/e2e -q`, `python scripts/db_sync_check.py`, `python scripts/validate_bank.py`, `cd frontend && pnpm run build`, `pnpm run test:e2e -- spec001`; paste results
- [ ] T070 Capacity guard: `python scripts/measure_capacity.py` within 10 % of 26 CPU-ms/request; record the number
- [ ] T071 Reconciliation dry run on a copy of `data/elo_database.db` twice (quickstart §3); record rows created on run 1 and 0 on run 2
- [ ] T072 [P] Update operational docs (new/modified text in English): `AGENTS.md` R15, R16, R19, V2-R3, architecture map and database table; `docs/arquitectura.md` § El motor ELO (the paragraphs this spec makes false)
- [ ] T073 Remove resolved Known Deviations D-1, D-2, D-3 via `/speckit-constitution` on its own branch (PATCH bump) — after this spec's code PR merges

---

## Dependencies & Execution Order

```
Phase 1 (T001–T002)
  → Phase 2 pins (T003–T019) → T020 green on unchanged code       ← BLOCKS everything below
  → Phase 3 foundational (T021–T031)                               ← BLOCKS all stories
  → US1 (T032–T039)
  → US2 (T040–T042)          needs US1's new answer path
  → US3 (T043–T044), US4 (T045–T046), US5 (T047–T050)   parallel after US1
  → US6 (T051–T064)          needs US1–US5 writers on the new store
  → V1 (T065–T066)           after T036 and T060
  → Phase N (T067–T073)
```

Within each story: `[CHANGE]` test tasks (must FAIL) → implementation → flips → story checkpoint.
Every task touching a repository changes **both** engines and ends with `db_sync_check` (R1).

## Parallel Opportunities

- Phase 2: T003–T019 are all [P] (different files or independent test functions).
- Phase 3: T021, T023, T028, T030 test/creation tasks in parallel.
- After US1: US3, US4, US5 phases in parallel.
- US6 test tasks T051–T058 in parallel; implementation T059–T064 sequential where they share files.

## Implementation Strategy

MVP = Phases 1–4 (pins, foundation, US1): ratings stored per course+topic, honest invalid
attempts, badge failures logged. Each later story is an independent increment; the code PR goes in
only after Phase N (constitution agent rule 7).

## Notes

- Commits follow the approved commit policy in AGENTS.md § Required sequence and constitution
  § AI Agent Behaviour, rule 7.
- `[AS-IS]` tests: green before and after. `[CHANGE]` tests: red before, green after. Flips cite
  their FR.
- A-1 (Playwright in CI) and A-2 (traceability check in CI) are separate roadmap tasks on their own
  branches.
