---

description: "Tasks for spec 001 — ELO engine"
---

# Tasks: ELO Engine

**Input**: `specs/001-elo-engine/` — spec.md, plan.md, research.md (R1–R19), data-model.md,
contracts/api.md, contracts/domain.md, quickstart.md

**Tests are MANDATORY** (constitution Principle I; spec § Traceability). Every FR and acceptance
scenario maps to a test task below — reused (assertions checked) or new.

| Tag | Test kind | Before implementation | After |
|---|---|---|---|
| `[AS-IS]` | characterization (Phase 2) | **PASS on unchanged code** | still pass |
| `[CHANGE]` | behaviour change (story phases) | **FAIL** | pass |

Pinned tests that a `[CHANGE]` deliberately alters are listed as **flip** tasks next to the change
that causes them; they cite the FR. Never edit a pinned assertion silently.

**Test naming**: every new test function name contains `spec001`. Repository tests use the
two-engine `repo` fixture (SQLite + PostgreSQL) and must give identical results (constitution IV;
SC-001). Architecture guards are supplementary; behavioural tests prove the FRs.

**Layer split (constitution III, research R3)**: calculations in `src/domain/`; orchestration in
`src/application/services/rating_read_service.py`; participant selection and raw-row access in
repositories. The only rating write pattern allowed in SQL is adding a domain-computed delta
atomically.

**V1 is never left broken**: a task that changes a shared signature or deletes a shared reader
adapts its V1 call sites in the same task; the V1 smoke pin (T021) stays green at every checkpoint.

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

- [X] T001 Move the two-engine `repo` fixture, `_postgres_repo` dependency and the `student`/`_sql` helpers from `tests/integration/test_elo_single_source.py` into `tests/integration/conftest.py` (behaviour unchanged) and add helpers `make_course(repo, course_id, name, block, topics=[...])`, `make_group(repo, teacher_id, course_id=None)`, `enroll(repo, user_id, course_id, group_id=None)`, `answer(repo, user_id, item_id, correct, seconds)` and one read helper `rating_of(repo, user_id, course_id, topic)` that every pin uses instead of querying a rating table directly (today it reads `student_topic_elo` by the key the code writes)
- [X] T002 [P] Confirm the SQLite reconciliation command in `specs/001-elo-engine/quickstart.md` §3 (`DB_PATH=... python -c "...SQLiteRepository..."`) runs against a copy of `data/elo_database.db`; correct the quickstart if not
- [X] T003 Extend the CI job `test-postgres` in `.github/workflows/ci.yml` to run every two-engine test of this spec on PostgreSQL — the job lists files by name, so add `tests/integration/test_spec001_repository_pins.py`, `test_spec001_course_topic_store.py`, `test_spec001_reconciliation.py` (and `test_pvp_repository.py` once T050 makes PvP two-engine); keep the existing two files. *(Done as: the job runs the whole `tests/integration/` folder with `-rs` — a file list would fail on not-yet-created files and go stale.)* Without this, the PostgreSQL branch of the new tests never runs anywhere (today the 11 local skips are exactly that branch)

---

## Phase 2: Pin Current Behaviour (Blocking)

**Purpose**: characterize every `[AS-IS]` requirement the refactor touches. **Every task here must
pass against the unchanged code** (green run recorded in T022). A pin that fails on today's code is
a finding for `/speckit-clarify`, not something to fix here.

### Reused tests (verify assertions prove the FR; strengthen in place if partial)

- [X] T004 [P] Reuse for FR-001: `tests/unit/domain/test_elo_model.py::TestExpectedScore` (all 5) — confirm they assert the exact formula *(Done: the 5 assert the formula only at P = 0.5 and one 400-point gap; `test_spec001_fr001_both_engine_paths_use_the_same_expected_success` in `test_spec001_engine_pins.py` adds non-trivial points for both `expected_score` and `RatingModel.expected_score`, the path the rating update actually uses.)*
- [X] T005 [P] Reuse for FR-017, FR-018: `tests/unit/domain/test_item_selector.py` (`TestZDPSelection`, `TestFisherInformation`, `TestZDPPreFiltering`, `TestControlledVariety`); add `test_spec001_band_widens_by_005_up_to_10_steps_then_whole_pool` there if the widening count is not asserted (US2-AS2) *(Done: widening was not asserted; test added. The 10-step cap itself is unobservable — the band reaches its [0.01, 0.99] clamp after 8 steps.)*
- [X] T006 [P] Reuse for FR-016, edge "topic with no items", edge "equal difficulty": `tests/unit/application/test_student_service.py::TestGetNextQuestion::test_variety_preserves_unseen_priority_and_session_exclusions`, `::TestTopicFilter::test_unknown_topic_filter_falls_back_to_full_pool`, `::TestGetNextQuestion::test_preserves_selected_identity_when_difficulties_match`
- [X] T007 [P] Reuse for FR-007, FR-008, FR-010, FR-021, FR-022 (once), FR-028, US1-AS3, US1-AS6, US3-AS3, US4-AS2: `tests/integration/test_elo_single_source.py` (`test_an_invalid_attempt_does_not_move_the_rating`, `test_concurrent_answers_on_the_same_item_compose_serially`, `test_diagnostic_baseline_survives_until_the_first_practice`, `test_a_validated_procedure_delta_is_applied_exactly_once`, `test_global_elo_stays_the_average_of_the_canonical_topics` — FR-028: aggregate derived from stored ratings) *(Done: these five do not exercise FR-021; its proof is `tests/api/test_student.py::test_first_practice_uses_diagnostic_rating` (re-done diagnostic leaves the practised rating, SQLite) and `tests/integration/test_postgres_production_guards.py::test_postgres_permissions_diagnostic_and_canonical_answer` (same on PostgreSQL). T069 cites those.)*
- [X] T008 [P] Reuse for FR-025 (once), FR-027, US5-AS2, US5-AS3 (**SQLite only** — this file has no PostgreSQL branch today; the two-engine check is T050): `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess` (`test_closing_a_match_twice_applies_the_delta_once`, `test_matches_orphaned_by_a_restart_are_closed`, `test_a_live_match_is_left_alone`)
- [X] T009 [P] Reuse for FR-023 (ownership), US4-AS4: `tests/api/test_procedure_grading.py::test_other_teacher_cannot_grade_or_view_submission`, `::test_reassignment_between_lookup_and_update_prevents_grading` *(Done: both asserted the submission unchanged, not the rating; strengthened in place with `get_latest_elo_by_topic` before/after.)*
- [X] T010 [P] Reuse for FR-011, US1-AS7, edge "diagnostic duplicate/foreign item": `tests/api/test_student.py::test_invalid_answer_context_has_no_side_effects`, `::test_answer_without_legacy_item_data`, `::test_diagnostic_rejects_noncanonical_payload` *(Done: also `tests/api/test_student.py::TestAnswer::test_ignores_tampered_item_data` — the direct proof that difficulty, topic and options come from the store.)*
- [X] T011 [P] Reuse for FR-012 (PostgreSQL): idempotency test in `tests/integration/test_postgres_production_guards.py` (~lines 250–290); its SQLite twin is T014

### New characterization tests (must PASS on unchanged code)

- [X] T012 [P] `[AS-IS]` FR-002, FR-003, FR-004, US1-AS1, US1-AS2, edge "RD floor 30" in `tests/unit/domain/test_spec001_engine_pins.py`: `VectorRating().update` from defaults with D=1000 gives 1016.00 / 984.00 and RD 332.5; at RD 30 stays 30 and moves 32·30/350·0.5
- [X] T013 [P] `[AS-IS]` FR-005, FR-006, and FR-015-today (failure swallowed — pinned only to be flipped in T036) in `tests/unit/application/test_spec001_service_pins.py`: `StudentService.process_answer` with a fake repository whose `save_answer_transaction` runs `compute` on a fixed state; item difficulty 984/1016 for US1-AS1/AS2; returned `item_rd` equals the input
- [X] T014 [P] `[AS-IS]` FR-012, FR-013, FR-014, FR-032, US1-AS4, US1-AS5, US6-AS4, edge "retry key empty or > 128 chars" in `tests/api/test_spec001_answer_pins.py`: replay with same key returns the stored result and attempt count stays 1; same key + other option → 409; no `correct_option` in `/answer` or `/exam/submit`; `/exam/submit` leaves every rating unchanged; key `""` and 129 chars → 400
- [X] T015 [P] `[AS-IS]` FR-016 (cooldown ≥ 3), FR-019, US2-AS3, US2-AS4, US2-AS5 in `tests/unit/application/test_spec001_service_pins.py`: failed item eligible only when `session_questions_count − failed_at ≥ 3`; correct-in-session never offered; exhausted pool at rating 1800 → `(None, "mastery")`, at 1799 → pool offered again
- [X] T016 [P] `[AS-IS]` FR-017, US2-AS1 in `tests/unit/domain/test_spec001_engine_pins.py`: rating 1000, items 600/950/1100/1600 → always 950 over 50 seeded draws
- [X] T017 [P] `[AS-IS]` FR-020, FR-031a, US3-AS1, US3-AS2, US3-AS4 in `tests/api/test_spec001_answer_pins.py`: one correct item at difficulty 1200 → topic baseline 1022; all wrong below 1100 → floor 760; skipped answer changes nothing; response carries a league label from Bronce/Plata/Oro/Diamante
- [X] T018 [P] `[AS-IS]` FR-022, FR-023 (grade range), FR-024, US4-AS1, US4-AS3, US4-AS5, edge "grade 50" in `tests/integration/test_spec001_repository_pins.py` (both engines): grade 80 → +6.0 on the item's topic; grade 50 → 0 and `elo_applied = 1`; grade 101 → `ValueError`, nothing changes; an `ai_proposed_score` changes no rating
- [X] T019 [P] `[AS-IS]` FR-025 (formula), US5-AS1, US5-AS4 in `tests/integration/test_spec001_repository_pins.py` and `tests/unit/domain/test_spec001_engine_pins.py`: `api.websocket.pvp._elo_deltas(1000, 1000)` = (12.0, −12.0), draw = (0.0, 0.0); after `finish_pvp_match` the next practice answer starts from the post-match rating
- [X] T020 [P] `[AS-IS]` FR-007, FR-008 boundaries, FR-028e, FR-028g, edges "exactly 3 s / 600 s valid", "missing time = 30 s" in `tests/integration/test_spec001_repository_pins.py` (both engines): 3.0 and 600.0 move the rating, 2.99 and 600.01 do not; `time_taken=None` moves it; `get_latest_attempts`/`get_student_attempts_detail` return one row per attempt with its `elo_after`; a saved `weekly_rankings` row is returned unchanged by `get_ranking_history`; FR-032, US6-AS4 (storage half): saving and completing an exam session (`save_exam_session`, `complete_active_exam_session`) writes no rating row
- [X] T021 [P] `[AS-IS]` V1 smoke (constitution § Stack) in `tests/unit/interface/test_spec001_v1_smoke.py`: V1 view modules import, and `StudentService`/`TeacherService` construct exactly as `src/interface/streamlit/app.py` does (no Streamlit runtime). Stays green at **every** later checkpoint *(Done: needs the V1 stack from `requirements.txt` (CI `test-unit` installs it); without Streamlit the module is skipped, never silently passed.)*
- [X] T022 Pin gate **on both engines**: run `pytest tests/ --ignore=tests/e2e -q -rs -k "spec001 or elo_single_source or pvp_repository or item_selector or elo_model or student_service or procedure_grading"` (same selection as quickstart §1) on the **unchanged code** with `POSTGRES_TEST_DATABASE_URL` pointing at a disposable PostgreSQL (local: start Docker Desktop, then `docker run -d --rm --name spec001-pg -p 5433:5432 -e POSTGRES_PASSWORD=spec001 postgres:16-alpine` and `POSTGRES_TEST_DATABASE_URL=postgresql://postgres:spec001@localhost:5433/postgres`), or record the green `test-postgres` CI run of the same commit. The gate is **not passed** if any PostgreSQL-branch test is reported SKIPPED; paste the summary including the `-rs` skip list; stop if anything is red
  **Gate record (2026-10-07, commit d31c744 + the Phase 2 test files, unchanged application code):**
  the whole suite was run instead of the `-k` selection, because that selection misses two
  reused files (`tests/api/test_student.py` — T010, FR-021 — and
  `tests/integration/test_postgres_production_guards.py` — T011). Local disposable PostgreSQL 16
  (`spec001-pg` on 127.0.0.1:5433), Python 3.13.5:
  `POSTGRES_TEST_DATABASE_URL=postgresql://postgres:spec001@localhost:5433/postgres python -m pytest tests/ --ignore=tests/e2e -q -rs`
  → **756 passed in 80.99 s; 0 skipped, 0 failed** (no `-rs` skip list printed). Before Phase 2:
  688 passed, 11 skipped (the PostgreSQL branch).

**Checkpoint**: current behaviour pinned (depends on T001–T021).

---

## Phase 3: Foundational (Blocking for all stories)

**Purpose**: domain functions, the new store, raw-row/participant reads and the read service. No
behaviour change yet: Phase 2 pins (incl. T021) stay green after each task.

- [X] T023 [P] `[CHANGE]` tests first in `tests/unit/domain/test_spec001_domain.py` for contracts/domain.md: `rating_delta`, `next_rd`, `item_difficulty_delta`, `is_valid_response_time` (None→30; explicit 0 → invalid, FR-008a; 3 and 600 inclusive), `pvp_deltas`, `diagnostic_tier`, `diagnostic_baseline` (floor 760), `course_rating` (empty → None), `overall_rating` (None skipped; all None → None; US6-AS1 → 1100), `rank_for` (None → None; 16 labels ascending), `RANKS`, `RATING_DISPLAY_DECIMALS == 0`, `round_for_display` (FR-028i: 1199.5→1200, 1200.5→1201, 1200.49→1200, 1200.4999999→1200, 0.5→1, 2.5→3 — i.e. **not** Python's half-to-even), `rating_display` (FR-028j, US6-AS9 boundary: 999.6→(1000, "Plata I"), 999.5→(1000, "Plata I"), 999.4→(999, "Plata II"), None→(None, None)), `course_rating`/`overall_rating` keep full precision (topics 1200.4, 1200.4, 1201.4 → course 1200.7333…, ranked as 1201), `rank_competition` (FR-028h, US6-AS8: rounded ratings 1250/1200/1200/1150 + pending → ranks 1, 2, 2, 4, None; ties displayed by user id asc with the same rank; entries with different `attempts_in_window` but equal rounded rating still share a rank; ratings differing only below the display precision tie; returned ratings are rounded). Must FAIL (functions absent)
- [X] T024 Implement in `src/domain/elo/model.py`: `rating_delta`, `next_rd`, `item_difficulty_delta`, `is_valid_response_time`, `pvp_deltas`, `diagnostic_tier`, `diagnostic_baseline`; `RatingModel.update` and `VectorRating.update` delegate to them; remove `impact_modifier` from `VectorRating.update`
- [X] T025 [P] Create `src/domain/elo/aggregation.py` (`course_rating`, `overall_rating`, full precision) and `src/domain/elo/ranks.py` (`RANKS` copied verbatim from `api/routers/student.py::_RANK_THRESHOLDS`, `rank_for`, `RATING_DISPLAY_DECIMALS = 0`, `round_for_display`, `rank_competition`); `tests/unit/test_architecture_layers.py` green (T023 passes)
- [X] T026 Remove dead code (research R15): `calculate_dynamic_k`, `update_elo`, `StudentELO` from `src/domain/elo/model.py`; the unused import at `src/interface/streamlit/views/student_view.py:21` (V1 call site of a deleted symbol); `get_user_history_elo` from both repositories. **Flip** (delete, citing constitution VII): `tests/unit/domain/test_elo_model.py::TestDynamicKFactor`, `::TestUpdateElo`, `tests/unit/domain/test_vector_elo.py::TestVectorRatingUpdate::test_zero_impact_modifier_gives_no_rating_change`, `tests/unit/application/test_student_service.py::TestProcessAnswer::test_cognitive_modifier_is_1_when_disabled` *(Done: also removed `get_latest_elo` from both repositories — the only caller of `get_user_history_elo`, itself without callers.)*
- [X] T027 Point callers at the domain: `api/routers/student.py` uses `diagnostic_tier`/`diagnostic_baseline` and `rank_for` (delete `_diff_tier`, `_RANK_THRESHOLDS`, `_elo_to_rank`); `api/websocket/pvp.py` uses `pvp_deltas` (delete `_elo_deltas`, `K`); update T017/T019 imports **without changing their asserted numbers** *(Done: `tests/unit/infrastructure/test_pvp_logic.py` keeps its assertions through a local wrapper over `pvp_deltas`. PvP deltas are no longer rounded to 2 decimals before persisting (FR-028i).)*
- [X] T028 Add table `student_course_topic_elo` in `init_db`/`_migrate_db` of **both** `src/infrastructure/persistence/sqlite_repository.py` and `postgres_repository.py` exactly per data-model.md: PK `(user_id, course_id, topic)`; `current_elo` `DOUBLE PRECISION` (PostgreSQL) / `REAL` (SQLite, 8-byte) `NOT NULL` "≥ 0"; `rd` same types `NOT NULL DEFAULT 350` "30 ≤ rd ≤ 350" — never PostgreSQL `REAL`, which is 4-byte (research R20, FR-028i); `origin TEXT NOT NULL` one of `practice · diagnostic · legacy_topic_row · legacy_course_row · procedure`; `approximate` "NOT NULL DEFAULT false"; `legacy_source_key TEXT NULL`; `reconciled_at TIMESTAMP NULL`; `created_at`, `updated_at`; index `(user_id, course_id)`. Additive only *(Done: the data-model rules are CHECK constraints in both engines; `course_id` references `courses(id)`.)*
- [X] T029 Add `pvp_matches.elo_reason_p1`, `elo_reason_p2` `TEXT NULL` in both repositories (PostgreSQL `ADD COLUMN IF NOT EXISTS`; SQLite `_add_column_if_not_exists`)
- [X] T030 [P] `[CHANGE]` tests first in `tests/integration/test_spec001_course_topic_store.py` (both engines) for the raw-row and participant reads of contracts/domain.md: `get_course_topic_ratings` (+ `_bulk`) return only new-table rows with `origin`/`approximate`; `get_current_context_course_ids` (+ `_bulk`) = enrollments ∩ catalogue — semillero grade 6 enrolled in grade 6 and 7 courses → only grade 6; colegio student (`grade=None`) enrolled in a colegio and a universidad course → only colegio; same check for universidad and concursos; `get_ranking_participants` for each scope per the FR-028f table (group course filter counts only attempts on that course's items), returning no rating field; `get_group_course_id`. Must FAIL
- [X] T030a [P] `[CHANGE]` FR-028i, FR-028j storage precision (owner 2026-10-07, research R20) in `tests/integration/test_spec001_course_topic_store.py` (both engines): rows of 999.4999999 and 999.6 in `student_course_topic_elo` read back unchanged through `get_course_topic_ratings`, and `RatingReadService.ratings_view` shows 999 "Plata II" and 1000 "Plata I" for them on SQLite and PostgreSQL alike. Must FAIL (table absent); also confirm it fails when the PostgreSQL column is `REAL` *(Done: passes on both engines; with the PostgreSQL column altered to `REAL` it fails with `[999.5] == [999.4999999]`, then restored.)*
- [X] T031 Implement those reads in both repositories; declare them in `src/application/interfaces/repositories.py`; update `tests/unit/application/test_repository_contracts.py`; `python scripts/db_sync_check.py` (T030 passes) *(Done: protocol `IRatingReadRepository` in `src/application/interfaces/repositories.py`, checked by the contract test. Current context uses the catalogue rule as the data stores it — every semillero course has block 'Semillero' and its grade is the id suffix `_semillero_N` — via domain `in_catalogue`. Separate pre-existing bug, not fixed here: `get_available_courses_by_level` looks for a block 'Semillero N°' that no course can have.)*
- [X] T032 [P] `[CHANGE]` tests first in `tests/unit/application/test_spec001_rating_read_service.py` with a fake repository: `ratings_view` (US6-AS1 numbers; pending → `overall=None`, `overall_status="pending_diagnostic"`, `rank_label=None`), `ratings_view_bulk`, `course_rating_of`, `group_basis` precedence (requested → group course → overall; unknown course → `ValueError`; not enrolled → `PermissionError`), `ranking_view` (single basis for every participant, no substitution, ratings returned as integers via `round_for_display` with `rank_label` derived from that integer; `ratings_view` returns full-precision `overall`/`rating` plus `display_rating` and `rank_label` from `rating_display` (FR-028j: a 999.6 overall gives display 1000, "Plata I"), averages computed in full precision before the single rounding (FR-028i), competition ranks, pending last with `rank=None`, `limit` cuts the list without changing any rank), `ranking_rank` = the rank of the student's entry in the unlimited list for the same arguments (`None` when pending). Must FAIL
- [X] T033 Implement `src/application/services/rating_read_service.py` (`RatingReadService`) per contracts/domain.md; inject it where `StudentService`/`TeacherService` are composed (`api/routers/student.py::_make_service`, `api/routers/teacher.py::_svc`, `src/interface/streamlit/app.py`); T032 and T030a pass, T021 green *(Done: `StudentService` and `TeacherService` take `ratings=None` and default to `RatingReadService(repository)`, so the API and V1 composition roots get it without a call-site change.)*

**Checkpoint**: domain, store, raw reads and read service exist; all Phase 2 pins green.

---

## Phase 4: User Story 1 — A practice answer updates my rating correctly (P1) 🎯 MVP

**Independent test**: answers on one item move the item's course-topic rating per FR-001…006 and
report honestly (quickstart §4 step 5).

### Tests for US1 (`[CHANGE]` — must FAIL first)

- [X] T034 [P] [US1] `[CHANGE]` FR-029, US1-AS1, US1-AS2 in `tests/integration/test_spec001_course_topic_store.py` (both engines): an answer on an item of course C, topic T writes only `student_course_topic_elo(user, C, T)` with `origin='practice'` (1016.00/984.00), nothing to `student_topic_elo` or `users.current_elo`, and the same topic label in course C' is untouched. Must FAIL on the code before this story's implementation
- [X] T035 [P] [US1] `[CHANGE]` FR-009, FR-008 in `tests/api/test_spec001_api.py`: answer with `time_taken=2` → `delta_elo == 0`, `elo_after == elo_before`, `elo_valid == false`; stored attempt has `elo_after == elo_before`. Must FAIL on the code before this story's implementation
- [X] T035a [P] [US1] `[CHANGE]` FR-008a in `tests/integration/test_spec001_course_topic_store.py` (both engines): an answer with an explicit `time_taken=0` is recorded with `elo_valid = 0` and leaves the rating, RD and item difficulty unchanged, while `time_taken=None` still moves the rating (30 s). Must FAIL on the code before this story's implementation (today 0 is read as absent)
- [X] T035b [P] [US1] `[CHANGE]` FR-012, FR-012a (owner 2026-10-07, research R21) in `tests/integration/test_spec001_answer_retry.py` (both engines through the API; deterministic on PostgreSQL): fixed boundary values — rating 1181 (an integer, so no store's rounding moves it), difficulty 1000, RD 350, correct answer — give a full-precision 1189.344952 (rounds to 1189.34) whose 4-byte stored attempt PostgreSQL returns as 1189.345 (rounds to 1189.35); the first response and a retry with the same key return identical values equal to the persisted attempt's, one attempt is recorded, and the stored rating equals the full-precision value (applied once, never the attempt's). Seeds through a `set_rating` helper re-pointed in T038 with `rating_of`. Must FAIL on today's code on PostgreSQL
- [X] T036 [P] [US1] `[CHANGE]` FR-015 in `tests/unit/application/test_spec001_service.py`: when `award_achievement` raises, `process_answer` returns its result and `caplog` holds an ERROR record. **Flip** the T013 "swallowed" assertion (FR-015). Must FAIL on the code before this story's implementation
- [X] T037 [P] [US1] `[CHANGE]` FR-029 V1 regression in `tests/unit/interface/test_spec001_v1_compat.py`: reproduce `student_view.handle_answer_topic`'s call into `StudentService.process_answer` (new signature) against a SQLite repo; the rating lands on the item's `(course_id, topic)`. Must FAIL on the code before this story's implementation

### Implementation for US1

- [X] T038 [US1] Change `save_answer_transaction(user_id, item_id, compute, request_id=None, request_fingerprint=None)` in **both** repositories: lock users→items (unchanged order), read the item's `course_id`, `topic`, `difficulty`, `rating_deviation` and the row `(user, course_id, topic)` (default 1000/350), call `compute`, insert the attempt with the item's topic, write rating + item only if `attempt_data["elo_valid"]`; delete `_tiempo_valido`, `_set_topic_elo`, `_refresh_global_elo`; re-point the T001 helper `rating_of` to `student_course_topic_elo(user, course_id, topic)` — not an assertion change *(Done: dead `save_attempt` (an old-store writer without callers) and `_set_topic_elo` removed too; `_bump_topic_elo`/`_refresh_global_elo` stay only for the legacy backfill `_backfill_current_elo` until T063 decides it.)*
- [X] T039 [US1] Rewrite `StudentService.process_answer` (`vector_rating`, `elo_topic` removed): `compute` uses `rating_delta`, `next_rd`, `item_difficulty_delta`, `is_valid_response_time`; invalid (incl. explicit 0, FR-008a) → before = after; return `elo_before`, `elo_after`, `rd_after`, `elo_valid`; badge failure → `logger.exception`. **Adapt V1 in this task**: `src/interface/streamlit/views/student_view.py:385-393` (T037 passes, T021 green) *(Done: V1 `handle_answer_topic` sends `None` when it has no start time — it used 0.0 for "missing", which FR-008a makes invalid.)*
- [X] T040 [US1] `/student/answer` in `api/routers/student.py` and `AnswerResponse` in `api/schemas/student.py`: accept and ignore `elo_topic` (deprecated Field), add `elo_valid`, keep idempotency and 400/409, drop `impact_modifier` from `cog_data` (contracts/api.md); with an `Idempotency-Key` build the response numbers from the persisted attempt on the first response as on a retry (FR-012a, research R21) *(Done: the fingerprint uses the item's topic where the client's `elo_topic` was, so retries of clients that sent none still match.)*
- [X] T041 [US1] **Flip** citing FR-029: `tests/unit/application/test_student_service.py::TestProcessAnswer::test_elo_topic_overrides_item_topic` (delete), `::test_save_answer_transaction_called_once`, `::test_cog_data_contains_expected_fields` (new signature/fields); `tests/integration/test_elo_single_source.py` reads through `rating_of` — same asserted numbers *(Done, flips citing FR-029/R6: `test_student.py::TestAnswer::test_invalid_answer_context_has_no_side_effects` loses its two `elo_topic` cases (ignored now, so no 400); `tests/integration/test_sqlite_repository.py::TestAtomicTransaction` uses the new signature; `test_elo_single_source.py::test_global_elo_stays_the_average_of_the_canonical_topics` removed (users.current_elo is legacy, FR-028/R4).)*
- [X] T042 [US1] `python scripts/db_sync_check.py`; Phase 2 pins (incl. T021) + T034–T037, T035a and T035b green; rerun the **whole suite on both engines** (the Phase 3 checkpoint failed on `test_postgres_concurrent_answer_retry_has_one_effect`; isolated passes do not close it)
  **Checkpoint record (2026-10-07) — Phases 4–8 run as one write-side checkpoint.** Every
  rating writer and the selection reader share `student_course_topic_elo`; moving the answer path
  alone left the diagnostic, procedure, PvP and selection tests on the old store (32 failures),
  so US1–US5's write side (T034–T053) was implemented before one checkpoint. Readers of US6
  (stats, dashboards, rankings) still read the old store until Phase 9.
  Whole suite, SQLite + disposable local PostgreSQL 16:
  `POSTGRES_TEST_DATABASE_URL=postgresql://postgres:spec001@localhost:5433/postgres python -m pytest tests/ --ignore=tests/e2e -q -rs`
  → **850 passed, 0 failed, 0 skipped**; it includes
  `test_postgres_concurrent_answer_retry_has_one_effect`, which failed at the Phase 3 checkpoint.
  `python scripts/db_sync_check.py` → in sync; frontend `tsc -b --noEmit` → 0 errors.

**Checkpoint**: US1 complete and independently testable.

---

## Phase 5: User Story 2 — The next item fits my level (P1)

- [X] T043 [P] [US2] `[CHANGE]` FR-029a (selection), FR-004 in `tests/unit/application/test_spec001_service.py`: `get_next_question` with `topic_filter=T` uses the (C,T) rating; without a filter uses `RatingReadService.course_rating_of(user, C)` (1000 when None); the diagnostic course average is no longer a seed. Must FAIL
- [X] T044 [US2] Implement the selection rating in `StudentService.get_next_question` (contracts/domain.md) and `/student/next-question`; remove the diagnostic course seed and `build_vector_rating` from `api/dependencies.py` when unused. **Adapt in this task**: V1 `student_view.py:868` and `scripts/audit_production_readiness.py:253-254` (T021 green) *(Done: `RatingReadService.selection_rating(user_id, course_id, topic=None)` is the single place for the selection rating; `get_next_question(student_id, course_id, topic_filter=None, ...)`. The PostgreSQL guard `test_postgres_permissions_diagnostic_and_canonical_answer` reads the new store; its attempt-difficulty assertion states the pre-existing INTEGER column (roadmap F-3).)*
- [X] T045 [US2] **Flip** citing FR-004: `tests/api/test_student.py::test_first_practice_uses_diagnostic_rating` — the first practice starts from the diagnostic's **topic** baselines, not a course seed

---

## Phase 6: User Story 3 — The diagnostic sets my starting point (P2)

- [X] T046 [P] [US3] `[CHANGE]` FR-029, FR-021 in `tests/integration/test_spec001_course_topic_store.py` (both engines): diagnostic for course C writes `(user, C, T)` rows with `origin='diagnostic'`; a topic with practice in C is not overwritten; the same label in another course is unaffected. Must FAIL
- [X] T047 [US3] Add `set_topic_rating_baseline(user_id, course_id, topic, elo, rd=350)` and `has_practice_attempts(user_id, course_id, topic)` to both repositories (replacing `set_topic_elo_baseline` and the old signature); update `/student/diagnostic/{course_id}/submit`; **adapt** `scripts/audit_production_readiness.py:252`; interface + contract test; `db_sync_check`

---

## Phase 7: User Story 4 — A teacher's grade adjusts my rating once (P2)

- [X] T048 [P] [US4] `[CHANGE]` FR-029, US4-AS1 in `tests/integration/test_spec001_course_topic_store.py` (both engines): grade 80 adds +6.0 to `(student, item.course_id, item.topic)`; absent row created at 1006.0 with `origin='procedure'`; floor 0; once only. Must FAIL
- [X] T049 [US4] Change the bump in `validate_procedure_submission` (both repositories) to the new table — atomic addition of the domain-computed delta (permitted persistence pattern); no write to `student_topic_elo`; `db_sync_check` *(Done: `_bump_course_topic_rating` — atomic addition, floor 0, origin 'procedure' for an absent row.)*

---

## Phase 8: User Story 5 — A finished PvP match adjusts my rating once (P3)

- [X] T050 [P] [US5] `[CHANGE]` FR-029b, FR-029c, US5-AS5 in `tests/integration/test_spec001_course_topic_store.py` (both engines): delta +12 adds +12 to **every** rated topic of the course and the course rating moves by exactly 12; player with no rated topic → ratings unchanged, `elo_delta_pX = 0`, `elo_reason_pX = 'no_rated_topics'`, opponent applied; a second close changes nothing; return value carries applied deltas. Must FAIL
- [X] T051 [P] [US5] `[CHANGE]` FR-026 in `tests/unit/application/test_spec001_service.py`: the lobby rating for a course equals `course_rating_of(user, course)`, not an all-course average; a fake repository records `api.websocket.pvp._lock.locked()` at read time and it is `False` (AGENTS R17). Must FAIL
- [X] T052 [US5] Implement `finish_pvp_match` (both repositories, contracts/domain.md); `api/websocket/pvp.py`: lobby rating via `await asyncio.to_thread(rating_read_service.course_rating_of, ...)`, **never while holding `_lock`**; `game_end` sends applied `elo_delta` and `elo_reason` (`"not_applied"` with 0 when persistence fails); `frontend/src/hooks/usePvpMatch.ts` type gains `elo_reason` *(Done: `finish_pvp_match` returns `None` when the match was not active (a second close changes nothing). `game_end` tests added to `tests/unit/infrastructure/test_pvp_logic.py` first. PostgreSQL methods of this spec read rows by column name (`db_sync_check` § 5).)*
- [X] T053 [US5] **Flip** citing FR-029/029b: `tests/integration/test_pvp_repository.py::TestPvpMatchLifecycle::test_finish_updates_current_elo`, `::test_elo_never_negative`, `::TestPvpStateSurvivesTheProcess::test_result_moves_the_canonical_rating_not_just_the_average` assert through `rating_of` *(Done: `test_pvp_repository.py` players start with one rated topic of the course; `test_spec001_repository_pins.py` T019 pin likewise — same asserted numbers.)*

---

## Phase 9: User Story 6 — My rating reads the same everywhere (P3)

### Tests for US6 (`[CHANGE]` — must FAIL first)

- [X] T054 [P] [US6] `[CHANGE]` FR-028a, FR-028b, FR-028c, US6-AS1, US6-AS5, US6-AS6 in `tests/api/test_spec001_api.py`: `/student/stats` returns `global_elo` 1100 for the US6-AS1 fixture; a promoted student with no rated new-grade course gets `global_elo: null`, `overall_status: "pending_diagnostic"`, `rank_label: null`; the earlier-grade course listed with `current_context: false`, rating unchanged; no field reports a difference between overall ratings. Must FAIL on the code before this story's implementation
- [X] T055 [P] [US6] `[CHANGE]` FR-028, FR-036, SC-005 "canonical reads" in `tests/integration/test_spec001_course_topic_store.py` (both engines) + `tests/api/test_spec001_api.py`: one fixture student; stats, teacher dashboard, teacher student report, exam snapshot, `/ai/socratic` context, and `ranking_view` for scopes group (with and without course), global, course and weekly, plus `ranking_rank`, all report the rating `ratings_view` gives; editing `student_topic_elo` and `users.current_elo` by hand changes none of them. Must FAIL on the code before this story's implementation *(Done: the API half failed first. The two-engine half (`test_spec001_every_ranking_reads_the_canonical_rating`) passed on its first run: RatingReadService and the participant reads it exercises were built test-first in Phase 3 (T030–T033); it stands as their two-engine proof.)*
- [X] T056 [P] [US6] `[CHANGE]` FR-028d, US6-AS7 in `tests/integration/test_spec001_course_topic_store.py` (both engines) and `tests/api/test_spec001_api.py`: group ranking with `course_id=C` ignores ratings and attempts of other courses (**fails on today's code: the filter does not filter**); basis precedence requested → group course → overall, returned as `basis` with `source`; unknown course → 400; course the student is not enrolled in → 403; the teacher endpoint uses the group course; a participant without a rating on the basis is `pending_diagnostic`, listed last with `rank: null` (and `my_rank: null` for that student), never ranked on another rating. Must FAIL on the code before this story's implementation *(Done: the API half failed first; the two-engine half passed on first run for the same reason as T055.)*
- [X] T057 [P] [US6] `[CHANGE]` FR-028f, FR-028h, US6-AS8 in `tests/integration/test_spec001_course_topic_store.py` (both engines): global/course/weekly rankings follow the FR-028f table — a student active this week with a lower rating appears, an inactive one with a higher rating does not; weekly uses the group basis; US6-AS8 competition ranking with identical results on both engines — equal rounded ratings share a rank and the next rank skips (1, 2, 2, 4), tied students with **different** attempts-in-window still share the rank, display order within the tie by user id, pending last with no rank; `ranking_rank` equals the rank of the student's entry; `limit=2` cutting through the tie keeps rank 2 on the shown entry. Must FAIL on the code before this story's implementation *(Done: two-engine; passed on first run — the logic was built test-first in T030–T033. Participation evidence is inserted as attempt rows so no rating moves.)*
- [X] T058 [P] [US6] `[CHANGE]` FR-031, FR-028j, US6-AS3, US6-AS9 in `tests/api/test_spec001_api.py`: `GET /api/meta/ranks` (no auth) returns the 16 labels ascending; for one student `rank_label` and the displayed number (`display_rating`, or the ranking entry's integer `rating`) are identical in `/student/stats`, `/teacher/dashboard`, `/teacher/student/{id}` and `/student/group-ranking`; boundary fixture with a full-precision overall of 999.6 → every endpoint returns 1000 with "Plata I", and 999.4 → 999 with "Plata II", while the stored rating stays 999.6 / 999.4. Must FAIL on the code before this story's implementation
- [X] T059 [P] [US6] `[CHANGE]` FR-030, US6-AS2 (SC-006) in `tests/api/test_spec001_api.py`: `/student/next-question` returns `preview`; answering that item correctly in 20 s returns `delta_elo == preview.on_correct` (±0.1); incorrectly → `preview.on_wrong`. Must FAIL on the code before this story's implementation
- [X] T060 [P] [US6] `[CHANGE]` FR-033, FR-034, FR-034a, FR-034b, FR-035, FR-036, SC-008 in `tests/integration/test_spec001_reconciliation.py` (both engines), fixtures built from the real ambiguity (course name == topic label; topic shared by two courses): existing new-table rows untouched; source (a) only with attempts under that key on that course or that course's diagnostic; source (b) by most recent `updated_at`, course-id on tie, never summed; reconciled rows `approximate=true` with `legacy_source_key`; a legacy row with no eligible context creates nothing; legacy rows unchanged; a second run creates 0 rows. Must FAIL on the code before this story's implementation
- [X] T061 [P] [US6] `[CHANGE]` supplementary architecture guard `tests/unit/test_architecture_layers.py::test_spec001_no_rating_aggregation_in_repositories_or_routers` (constitution III): no repository or router contains `AVG(`/`ORDER BY` over `current_elo` or `elo_after`, or imports `src.domain.elo.aggregation`/`ranks`. Must FAIL on today's code (rankings average `elo_after`)
- [X] T062 [P] [US6] Playwright (mocked API — verifies frontend flows only) `frontend/e2e/spec001-ratings.spec.ts`: Practice shows the API `preview` (US6-AS2); Stats shows "pending diagnostic" and history courses (US6-AS5/AS6) and the group ranking with its basis label and pending rows last (US6-AS7); teacher Dashboard and Groups render the API `rank_label` (US6-AS3); Home lists ranks from `/api/meta/ranks`; a mocked `display_rating: 1000` with `rank_label: "Plata I"` renders exactly "1000" and "Plata I" in Stats, RankBadge and the teacher Dashboard (US6-AS9, FR-028j); group ranking shows tied students with the same rank number, the API rating exactly as returned (no re-rounding — e.g. a mocked `1201` renders as `1201`), and pending rows without a rank (US6-AS8, FR-028i) *(Done: the realistic US6-AS9 case already passed on the old frontend (`Math.round(999.6)` is 1000), so a deliberately inconsistent mock (display_rating 1201 vs global_elo 1180.2) proves the screens render the API value as given. Run locally with `PLAYWRIGHT_CHANNEL=chrome`: the installed Playwright Chromium build is older than the package.)*

### Implementation for US6

- [X] T063 [US6] Implement `_reconcile_legacy_ratings()` in both repositories per research R10; call it from `_bootstrap_schema` after existing backfills (PostgreSQL under the existing advisory lock); `db_sync_check` (T060 passes) *(Done: the decision rules are one pure function, `src/domain/elo/reconciliation.py::plan_reconciliation`; repositories read raw rows and insert. Legacy values outside the store's invariants are clamped (rating ≥ 0, 30 ≤ RD ≤ 350). The bootstrap's `_backfill_current_elo` and its helpers `_bump_topic_elo`/`_refresh_global_elo` were deleted — they wrote the legacy store and `users.current_elo`, which nothing writes after this spec (FR-036, research R4); reconciliation runs in their place.)*
- [X] T064 [US6] Route every V2/shared reader of research R18 through `RatingReadService`: `/student/stats` (remove the twin-dedupe hack), `/student/map/{course_id}`, `/student/exam/submit` snapshot, `/ai/socratic` (`api/routers/ai.py`), `TeacherService.get_student_dashboard` and `generate_ai_analysis`, `/teacher/dashboard` (remove `global_elo` from `get_teacher_dashboard_stats`; fill it from `ratings_view_bulk`). Delete `get_latest_elo_by_topic`, `get_topic_elo_map`, `get_student_elo_summary`, `aggregate_global_elo`. **Adapt V1 in this task**: `student_view.py:73, 1787, 1816, 1839, 1935, 1945`, `teacher_view.py:656, 712, 960`. Interface + contract test; `db_sync_check`; T021 green *(Done: no screen or response shows the internal 1000 fallback — pending reads "Diagnóstico pendiente" / null in stats, course map and rail (`MapNode.elo` nullable), PvP opponent (`game_start.opponent.elo` = shown value or null), practice header, V1 course cards, practice header and overall metrics, teacher views, and AI prompts ("pendiente de diagnóstico"). The exam snapshot returns null while pending; `exam_sessions.global_elo_after` is NOT NULL DEFAULT 0, so storage keeps 0 (AGENTS R8 forbids relaxing it; no screen displays it). Flipped citing FR-028b: `tests/api/test_student.py::TestStats::test_stats_initial_elo`; citing FR-028a: `tests/unit/domain/test_vector_elo.py::TestAggregateGlobalElo` (removed with `aggregate_global_elo`).)*
- [X] T065 [US6] Group ranking: `/student/group-ranking` and `/teacher/student/{id}/ranking` call `RatingReadService.ranking_view(scope="group", …)` with `group_basis` (400/403 mapping per contracts/api.md); delete `get_group_ranking` from both repositories (T056 passes)
- [X] T066 [US6] V1 rankings: `student_view.py:538, 610, 634, 729, 757` and `teacher_view.py:465, 495, 528, 550` call `ranking_view`/`ranking_rank`; `save_weekly_ranking(group_id, rows)` (the snapshot's `rank` column stores the competition rank) stores rows from `ranking_view(scope="weekly")`; delete `get_global_ranking`, `get_course_ranking`, `get_weekly_ranking`, `get_student_rank` from both repositories; `get_ranking_history` untouched (FR-028g); T057 and T061 pass, T021 green *(Done: V1 rankings go through `src/interface/streamlit/rankings.py` (V1 row shape over `ranking_view`).)*
- [X] T067 [US6] API schemas and routes per contracts/api.md: `StudentStatsResponse` (`global_elo: float | None`, `overall_status`, `course_ratings`), teacher `StudentSummary`/`StudentReportResponse` (`global_elo: float | None`, `display_rating`, `rank_label`, `overall_status`), `display_rating` on stats overall and each `course_ratings` entry (FR-028j), `NextQuestionResponse.preview`, group-ranking `basis` and entry fields (with `global_elo`/`rank_pos` aliases), new `api/routers/meta.py` with `GET /meta/ranks` registered in `api/main.py` under `/api`, no auth, rate-limited like other public routes (T054, T058, T059 pass) *(Done: plus `RatingReadService.answer_preview` (FR-030) and `rank_scale()` for `/api/meta/ranks`, which stays free of domain imports in routers (T061).)*
- [X] T068 [US6] Frontend: `Practice.tsx` uses `preview` (delete `estimateEloDelta`); `Stats.tsx` shows "pending diagnostic", history courses, and the group ranking's basis label with the API `rank` (shared on ties), the API `rating` rendered as returned (remove `Math.round` from ranking ratings, `Stats.tsx:229`; FR-028i), and pending rows last without a rank; `Teacher/Dashboard.tsx`, `Teacher/Groups.tsx` use API `display_rating` + `rank_label` (delete `RANKS`, `rankFor`); `Stats.tsx:142` and `RankBadge.tsx:52` render `display_rating` instead of `Math.round(...)` (FR-028j); `Home.tsx` fetches `/api/meta/ranks` (delete `RANKS`); `RankBadge.tsx` keeps the only colour map keyed by the 16 labels; i18n keys in `frontend/src/i18n/locales/es.ts` and `en.ts`; types in `frontend/src/api/{student,teacher}.ts`; `pnpm run build` green (T062 passes) *(Done: plus `Teacher/Groups.tsx` group average = mean of rated members' display values, shown without an invented rank label; `CourseRail.tsx`, `League.tsx`, `Exam.tsx` types. The shared e2e mock gained the spec 001 stats fields. Lint: the changed files keep their 13 pre-existing problems, none added.)*

**Checkpoint**: all six stories work; T054–T062 green; T021 green.

---

## Phase N: Traceability & Verification

- [X] T069 Fill spec.md § Traceability: every FR (incl. lettered) and every scenario → collected pytest node id or Playwright title; no `PENDING`. For each scenario tested through the API on one engine whose outcome depends on stored data, also cite the two-engine test of its storage behaviour (SC-001) *(Done 2026-10-07: 89 rows, no `PENDING`; every pytest reference checked against `pytest --collect-only` node ids and every Playwright title against the spec file.)*
- [X] T070 Review assertion adequacy row by row; strengthen any test that proves only part of its FR (record which) *(Done: three gaps closed with new tests — FR-027 boundary (`test_pvp_repository.py::...::test_spec001_abandonment_starts_after_600_seconds`, 590 s vs 610 s); FR-028f/g snapshot from the shown ranking (`test_spec001_course_topic_store.py::test_spec001_weekly_snapshot_stores_the_ranking_as_shown`, both engines — the new `save_weekly_ranking(group_id, rows)` had no test); FR-029a map pending (`tests/api/test_spec001_api.py::test_spec001_course_map_shows_unrated_topics_as_pending`). Precision assertions kept: T030a and T035b assert the stored rating equals the full-precision value on both engines; F-3 (`attempts.difficulty` INTEGER) concerns attempt history only.)*
- [X] T071 Full verification (AGENTS.md § Verify): `pytest tests/ --ignore=tests/e2e -q` (includes the V1 smoke), `python scripts/db_sync_check.py`, `python scripts/validate_bank.py`, `cd frontend && pnpm run build`, `pnpm run test:e2e -- spec001`; paste results *(Done 2026-10-07: `pytest tests/ --ignore=tests/e2e -q -rs` with the local disposable PostgreSQL → **883 passed, 0 skipped, 0 failed**; `db_sync_check` in sync; `validate_bank` OK; `pnpm run build` green; Playwright **35 passed** (spec001: 7/7) with `PLAYWRIGHT_CHANNEL=chrome`; flake8 CI selection 0.)*
- [X] T072 Capacity guard: `python scripts/measure_capacity.py` within 10 % of 26 CPU-ms/request; record the number *(Done 2026-10-07: the recorded 26 CPU-ms was not reproducible on today's loaded machine for either version, so the guard compared both on the same machine, alternating runs (`--students 30 --rounds 6`): this branch 93.1 / 87.9 / 101.7 / 79.4 (mean 90.5); `main` before spec 001 73.8 / 86.2 / 85.0 / 91.8 / 88.5 (mean 85.1) → **+6.4 %**, within 10 %; run-to-run noise ±12 %.)*
- [X] T073 Reconciliation dry run on a copy of `data/elo_database.db` twice (quickstart §3); record rows created on run 1 and 0 on run 2 *(Done 2026-10-07 on a copy of `data/elo_database.db` (deleted afterwards): 11 legacy rows of 5 students → run 1 created **13** approximate baselines (9 `legacy_topic_row`, 4 `legacy_course_row`), run 2 created **0**, an explicit third call returned **0**; every row has `approximate=1` and `legacy_source_key`; each equals exactly one legacy row (never summed); legacy rows unchanged.)*
- [X] T074 [P] Update operational docs (new/modified text in English): `AGENTS.md` R15, R16, R19, V2-R3, architecture map and database table; `docs/arquitectura.md` § El motor ELO (the paragraphs this spec makes false) *(Done: AGENTS.md R15, R16, R19, V2-R3, architecture map, table list and the advisory-lock note (`pg_try_advisory_xact_lock`); `docs/arquitectura.md` § El motor ELO — new text in English.)*
- [X] T075 Remove resolved Known Deviations D-1, D-2, D-3 via `/speckit-constitution` on its own branch (PATCH bump) — after this spec's code PR merges *(Done 2026-10-08 after PR #3 merged: constitution 1.0.0 → 1.0.1 (PATCH) removes D-1, D-2, D-3 and the D-2 pointer in Principle II, names the rating store `student_course_topic_elo`, and records that this repository is a development copy and is not deployed.)*

---

## Dependencies & Execution Order

```
Phase 1 (T001–T003)
  → Phase 2 pins (T004–T021) → T022 green on unchanged code       ← BLOCKS everything below
  → Phase 3 foundational (T023–T033)                               ← BLOCKS all stories
  → US1 (T034–T042)
  → US2 (T043–T045)          needs US1's answer path
  → US3 (T046–T047), US4 (T048–T049), US5 (T050–T053)   parallel after US1
  → US6 (T054–T068)          needs US1–US5 writers on the new store
  → Phase N (T069–T075)
```

- Within each story: `[CHANGE]` tests (must FAIL) → implementation → flips → checkpoint.
- Every task touching a repository changes **both** engines and ends with `db_sync_check` (R1).
- Every task that changes a shared signature or deletes a shared reader adapts its V1 call sites
  in the same task; T021 (V1 smoke) stays green at every checkpoint.

## Parallel Opportunities

- Phase 2: T004–T021 are all [P].
- Phase 3: T023, T025, T030, T032 in parallel.
- After US1: US3, US4, US5 in parallel.
- US6 tests T054–T062 in parallel; implementation T063–T068 sequential where they share files.

## Implementation Strategy

MVP = Phases 1–4 (pins, foundation, US1): ratings stored per course+topic, honest invalid
attempts, badge failures logged, V1 still answering. Each later story is an independent increment;
the code PR goes in only after Phase N (constitution agent rule 7).

## Notes

- Commits follow the approved commit policy in AGENTS.md § Required sequence and constitution
  § AI Agent Behaviour, rule 7.
- `[AS-IS]` tests: green before and after. `[CHANGE]` tests: red before, green after. Flips cite
  their FR.
- A-1 (Playwright in CI) and A-2 (traceability check in CI) are separate roadmap tasks on their own
  branches.

---

## Phase 10: Convergence

- [X] T076 Make V1's stakes preview in `src/interface/streamlit/views/student_view.py` ("Stakes preview") show `RatingReadService.answer_preview(user, course_id, item)` — the change the engine applies to the item's (course, topic) — with one decimal, instead of recomputing `32×(RD/350)×…` from the course rating and RD; add a V1 test that the shown values equal the applied change within 0.1 per FR-030, SC-006, Constitution II (contradicts) *(Done 2026-10-07: `student_view._stakes(ratings, user_id, course_id, item)` renders `RatingReadService.answer_preview` with one decimal; the inline `32×(RD/350)` recomputation and its now-unused imports are gone. Test first: `tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_stakes_preview_is_the_applied_change` (course rating 1100/RD 225 vs topic 1300/RD 100, both outcomes) failed, then passed.)*
- [X] T077 Label approximate baselines: carry `approximate` (and `origin`) on the topics of `/student/stats` `course_ratings` (and keep them in the teacher report), mark them as approximate in `Stats.tsx` (i18n es/en), with an API test and a Playwright check per FR-034a, plan: Constitution check VIII (partial) *(Done: `TopicELO.approximate`/`origin` on `/student/stats` (`course_ratings[].topics` and `topic_elos`); `Stats.tsx` marks a course with a reconciled topic "aproximado" (hint in es/en) and the topic bar with ≈. The teacher report (`TeacherService.get_student_dashboard().course_ratings`) already carried both fields — now asserted in T081; V1's teacher topic table (`teacher_view._topic_rows`) adds Curso and Aproximado columns. Tests first: `tests/api/test_spec001_api.py::test_spec001_stats_marks_approximate_baselines`, `tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_teacher_topic_table_marks_approximate_baselines`; the Playwright check (`Estadísticas marcan las líneas base aproximadas…`) was written after the UI and confirmed failing with `Stats.tsx` reverted.)*
- [X] T078 Owner decision, then implement: `/student/exam/history` returns the stored `global_elo_after` raw, and a snapshot taken while the diagnostic was pending is stored as the column default 0 (`NOT NULL`, AGENTS R8) — return `null` for it, or record an R8 exception to relax the constraint; test that no response reports 0 as a rating per FR-028b, Constitution V (partial) *(Owner decision 2026-10-07: A — `null` for a pending snapshot, recorded explicitly rather than inferred from 0 or from the current status. Additive column `exam_sessions.global_elo_status` (`'rated'`/`'pending'`, CHECK) on both engines, written by `save_exam_session` and `complete_active_exam_session` from the value at submission (`None` → pending); `global_elo_after` stays NOT NULL DEFAULT 0 (AGENTS R8). `/exam/history` returns the stored value only when `rated` (a genuine 0 stays 0), plus `global_elo_status`; rows recorded before the column report `"unknown"` with `null` — kept as stored, never backfilled, because the previous engine stored its 1000 default and this branch stored 0 for a student with no rating (contracts/api.md, data-model.md). Two-engine tests first, through the API: `tests/integration/test_spec001_course_topic_store.py::test_spec001_pending_exam_snapshot_is_null_not_zero`, `::test_spec001_genuine_zero_snapshot_is_reported_as_zero`, `::test_spec001_diagnostic_after_the_exam_keeps_the_pending_snapshot`, `::test_spec001_snapshot_recorded_before_the_status_is_unknown` (0 and 1000).)*
- [X] T079 Add `Cache-Control: public, max-age=…` to `GET /api/meta/ranks` with a test per contracts/api.md ("cacheable") (partial) *(Done: `Cache-Control: public, max-age=3600`; test first: `tests/api/test_spec001_api.py::test_spec001_meta_ranks_is_cacheable`.)*
- [X] T080 Align contracts/domain.md § StudentService (`get_next_question` "returns item + preview") with the implementation — the router adds the preview through `RatingReadService.answer_preview` — or move the preview into the service per plan: contracts (partial) *(Done: the contract now matches the implementation — `get_next_question` returns `(item, status)`; `/next-question` and V1's stakes line take the preview from `RatingReadService.answer_preview`.)*
- [X] T081 Update `tests/unit/application/test_teacher_service.py`: drop the stale `get_student_elo_summary` mock and assert `get_student_dashboard`'s RatingReadService fields (`global_elo`, `display_rating`, `rank_label`, `overall_status`, including the pending case) per FR-028a, FR-028b, Constitution I (partial) *(Done: the stale `get_student_elo_summary`/`get_latest_elo_by_topic` mocks are replaced by the raw rating reads; `TestGetStudentDashboard` asserts the rated (999.6 → 1000 "Plata I", approximate kept) and pending cases. Test-only task: both tests passed on first run against the existing service.)*

## Phase 11: Convergence

- [X] T082 Make V1 show one display value with its V1 rank: wherever `student_view.py` (course cards, practice header, "Nivel Global") and `teacher_view.py` (students table, student-detail header) show a current rating next to `get_rank(...)`, round once half up with `round_for_display` and derive both the number and the label from that value, with a V1 test at the 999.6 boundary per FR-028j (contradicts) *(Done 2026-10-07: `src/interface/streamlit/rankings.py::v1_rated(value)` rounds once with `round_for_display` and returns the shown number, V1 rank and colour of that value (pending text when `None`); used by the student course cards, practice header and "Nivel Global", and by the teacher students table (`ELO Global` now the display value) and student-detail header. Tests first: `tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_number_and_rank_come_from_one_display_value` (999.6 → "1000" 🔰 Iniciado, 999.4 → "999" 🌱 Punto de Partida, pending) and `::test_spec001_v1_views_rank_only_through_the_display_value` (no `get_rank(` left in V1 views). Also fixed here: T077's V1 helper `_topic_rows` was shadowed by a local of the same name in `render_teacher` (flake8 F823, an UnboundLocalError at runtime) — renamed `_rating_topic_rows`.)*
- [X] T083 Mark approximate topic ratings on the course map: add `approximate` to `MapNode` (`/student/map/{course_id}`) and show it on `CourseMap.tsx` nodes and `CourseRail.tsx`, with an API test and a Playwright check per FR-034a, plan: Constitution check VIII (partial) *(Done: `MapNode.approximate` from the topic row; `CourseMap.tsx` (trail and practice cards, with the hint as title) and `CourseRail.tsx` show ≈. Tests first: `tests/api/test_spec001_api.py::test_spec001_course_map_marks_approximate_topics` and the Playwright check `Mapa y riel del curso marcan los temas con línea base aproximada (FR-034a)`, each failing before the change.)*

## Phase 12: Follow-up F-1 — catalogue by level and grade (owner decisions 2026-10-08)

Spec: FR-028k … FR-028o, User Story 7 (Clarifications 2026-10-08). Survey and plan:
`docs/sdd/f1-semillero-survey.md`. Docs on `fix/f1-semillero-catalogue`; tests first — each
`[CHANGE]` test fails on the code before its implementation task. Development and tests are local;
nothing here touches production.

**Before deploying (owner, read-only on production — not part of the code PR)**

- [ ] T084 Count and list semillero students without a grade (survey § 3 step 1) and read `courses_block_check` (survey § 4.3 step 1); record the counts and whether the four blocks are accepted (no data changed). Grade-less accounts get their grade by the documented procedure, or the owner accepts the ones left; a constraint lacking a block means the migration will stop (FR-028n) and needs the separately reviewed repair first

**Tests first**

- [ ] T085 [CHANGE] Domain test: `in_catalogue` over level × grade 6–11 × own-grade, other-grade and other-level courses, and semillero without a grade → no course, per FR-028k (fails today for the grade-less case)
- [ ] T086 [CHANGE] Two-engine repository test: a grade-*g* semillero catalogue is exactly the six `*_semillero_g` courses for *g* = 6–11, a grade-less one is empty, other levels unchanged, per FR-028k, US7-AS1, US7-AS5
- [ ] T087 [CHANGE] API + two-engine test: registration as semillero without a grade, or with a grade outside 6–11, is rejected and creates no account; `GET /api/student/courses` for grade 7 returns the six grade-7 courses, per FR-028m, US7-AS1, US7-AS2
- [ ] T088 [CHANGE] API test: `/enroll` outside the catalogue (colegio → universidad course; grade 6 → grade-7 course) is rejected with nothing enrolled; inside the catalogue it enrols, per FR-028m, US7-AS3
- [ ] T089 [CHANGE] API + two-engine test, through `POST /api/student/enroll-by-code`: an invitation enrols a grade-6 student in a colegio group's course, they can practise it, their level and grade are unchanged, the course is not current and the overall rating is unchanged; a semillero account without a grade is refused a new invitation, reads "pending diagnostic", and keeps its existing enrolments, per FR-028l, US7-AS4, US7-AS5
- [ ] T090 Two-engine test: the block constraint accepts the four blocks and rejects `'Semillero 6°'`; an extra allowed value is kept; two migrations issue no DDL on it (PostgreSQL: the constraint's oid is unchanged — fails today: dropped and re-added on every run), per FR-028n, survey § 4.2, AGENTS R8
- [ ] T097 [CHANGE] Two-engine test: on a database whose block constraint lacks `'Semillero'`, the migration stops with an error naming the missing value, the constraint and the `courses` table are unchanged (PostgreSQL: same oid and definition; SQLite: same `CREATE TABLE` text, foreign keys of the other tables untouched), and `scripts/migrate.py` exits 1 without starting the web process, per FR-028n, survey § 4.3 (fails today: PostgreSQL re-adds it, SQLite rebuilds the table)
- [ ] T098 [CHANGE] API test: `GET /api/student/courses` for a colegio student enrolled by invitation in a universidad course lists the catalogue with `in_catalogue: true` and the invited course with `enrolled: true, in_catalogue: false`; for a grade-less semillero student it lists only the courses they are enrolled in, per FR-028l, FR-028o, US7-AS5, US7-AS6
- [ ] T099 [CHANGE] Playwright test (`frontend/e2e/`, mocked API): a grade-less semillero student sees the notice «Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu docente o al administrador.» and no catalogue course, while an enrolled course stays listed with its practice button; an invited course appears under *Mis matrículas* only, per FR-028o, US7-AS5, US7-AS6

**Implementation**

- [ ] T091 Both repositories' catalogue (`get_available_courses_by_level`) filter with the domain rule `in_catalogue`, which returns no course for semillero without a grade; `db_sync_check.py` in sync (FR-028k; depends on T085, T086)
- [ ] T092 Reject semillero without a grade 6–11 in the API schema and in `register_user` on both engines (FR-028m; depends on T087)
- [ ] T093 `/enroll` checks the catalogue through the service; `enroll-by-code` reads the group the repositories return (today a 500 for every valid code), requires a grade from a semillero student and never changes level or grade (FR-028m, FR-028l; depends on T088, T089)
- [ ] T094 Block-constraint guard: read-only check on both engines that the four blocks are accepted, no DDL when they are; new databases get exactly the four blocks on both engines (FR-028n, survey § 4.2; depends on T090)
- [ ] T095 Old-database path of the block constraint (approved 2026-10-08): remove both automatic widenings; stop with the error naming the missing values; `scripts/migrate.py` exits 1 (FR-028n, survey § 4.3; depends on T097). The manual repair DDL is not part of this task and is not run
- [ ] T100 `GET /api/student/courses` returns the catalogue plus the courses the student is enrolled in outside it, with `in_catalogue`; the courses screen shows the FR-028o notice for a grade-less semillero student, keeps *Explorar* to catalogue courses and lists every enrolment under *Mis matrículas*; `es` and `en` strings (FR-028l, FR-028o; depends on T098, T099)

**Close**

- [ ] T096 Replace the `PENDING` rows of FR-028k … FR-028o and US7-AS1 … AS6 with the tests above; `python scripts/check_traceability.py --run` (once A-2 is merged) and the full suite on PostgreSQL pass; rehearse the migration twice on the legacy-data simulation (no DDL on the second run)

V1 stays frozen: it receives the shared repository and service changes only (its own
`Semillero {grade}°` enrolment filter in `student_view.py` is left as is).

## Phase 13: Follow-up F-4 — practice only in enrolled courses (owner decisions 2026-10-08)

Spec: FR-037, FR-037a, User Story 8 (Clarifications 2026-10-08, follow-up F-4). Phase 12 is
follow-up F-1, in its own docs PR. Docs on `fix/f4-practice-access`; tests first — each
`[CHANGE]` test fails on the code before its implementation task. V2 only: V1 offers practice
only in the student's enrolments and is frozen.

**Tests first**

- [ ] T101 [CHANGE] API test: `next-question` for a course the student is not enrolled in (colegio student, `probabilidad`) and for a course that does not exist → 403, no item, per FR-037, US8-AS1 (fails today: 200 with an item)
- [ ] T102 [CHANGE] API test: `/answer` to an item of a course the student is not enrolled in, with and without `Idempotency-Key` → 403; the student's attempts, `student_course_topic_elo` rows, the item's difficulty and the retry record are unchanged, per FR-037a, US8-AS2 (fails today: 200 and a stored rating)
- [ ] T103 [CHANGE] API test: `GET /diagnostic/{course}` and `POST /diagnostic/{course}/submit` for a course the student is not enrolled in → 403; no question served, no diagnostic and no baseline stored, per FR-037, FR-037a, US8-AS3 (fails today: 200)
- [ ] T104 [AS-IS] API test: a student enrolled from their level's courses and one enrolled through an invitation code in a course of another level both get the next item, answer it (the rating moves) and take the diagnostic as today, per FR-037, US8-AS4 (passes on unchanged code)
- [ ] T105 [CHANGE] API test: after practising a course and leaving it (`DELETE /enroll/{course}`), `next-question` and `/answer` for it → 403, a retry of the accepted answer → 403 with the stored attempt unchanged, and the stored ratings in it are unchanged, per FR-037, FR-037a, US8-AS5
- [ ] T106 [CHANGE] Two-engine test: `StudentService.ensure_enrolled(user_id, course_id)` passes for an ordinary enrolment and for one made through an invitation (`enroll_user` with the group), and raises `PermissionError` for no enrolment, after unenrolment and for an unknown course, per FR-037, FR-037a, SC-001

**Implementation**

- [ ] T107 `StudentService.ensure_enrolled` (application layer, reads `get_user_enrollments`); `api/routers/student.py` calls it first in `next_question`, `diagnostic_status` and `diagnostic_submit`, and in `answer` right after the item lookup (404 for an unknown item stays) and before option validation and the retry replay, answering 403 «No estás inscrito en este curso.»; existing API tests that practised without enrolling enrol first (FR-037, FR-037a; depends on T101–T106)

**Close**

- [ ] T108 Replace the `PENDING` rows of FR-037, FR-037a and US8-AS1 … AS5 with the tests above; `python scripts/check_traceability.py --run` (once A-2 is merged), the full suite on PostgreSQL and Playwright pass
