# Tasks — spec 008, delivery L (an item's life)

**Plan**: [plan-l.md](plan-l.md) · **Status**: approved (owner decisions O-IL1 …
O-IL13 answered 2026-10-27, each as recommended; named «O-IL», not «O-L», because spec 007's delivery L already used O-L1 … O-L3).
FR-030, FR-031, FR-032 and FR-033 are `[CHANGE]`; US4-AS1 … AS3 are their scenarios. L has no
`[AS-IS]` requirement of its own, but it rewrites the bank sync delivery A pinned (FR-003, FR-004,
FR-005) and the item read every serving path shares, so Phase 1 re-runs those pins and pins the
halves of US4 that already hold, on the unchanged code, before anything changes.

**Starts after** V's and C's code are merged on `redesign` (`validate_bank.py`, the manifest and
O-V6; the catalogue and the sync's course lines). Branch `008-l` from `redesign` at that point.

## Phase 0 — Owner decisions (blocking)

- [x] T000 The owner decides O-IL1 … O-IL13 (plan-l.md § Owner decisions) and the plan's status
  becomes approved; the owner also answers the § Spec notes (FR-007's wording; the proposed FR-034
  for orphans, O-IL4). **No task below starts before this.** A decision that differs from the
  recommendation is written into plan-l.md first and the affected tasks are adjusted in the same
  commit, e.g.: O-IL1 «parameter» changes T006's calls, T017's signature and the protocol;
  O-IL2 «409» turns T003's second pin into a `[CHANGE]` test and adds a router change to T017;
  O-IL3 «serve the rest» turns T007's 409 assertion into «started with the remaining items» and
  adds a router change to T017; O-IL4 «not retired» drops T013 and T019; O-IL6 «bank wins once» or
  «unanswered items» rewrites T009's first-sync assertion; O-IL7 «NULL check» rewrites T009's
  upgrade test; O-IL8 «script only» removes the `sync` audit assertions from T009; O-IL9 «closed
  form» changes T010. Done 2026-10-27: every recommended option was approved, with the proposed
  FR-034 (O-IL4); the tasks below stand as written.

## Phase 1 — Pins green on the unchanged code (blocking)

- [ ] T001 Run, on `redesign` unchanged, and record the green run in the PR: delivery A's sync pins
  (`tests/integration/test_sqlite_bank_sync_failure.py`, `tests/integration/test_bank_duplicate_id.py`,
  `tests/integration/test_spec002_d1_startup.py::test_spec002_d1_a_changed_course_map_resyncs_the_bank`),
  `tests/unit/application/test_repository_contracts.py`, T's `tests/integration/test_spec008_t_topics.py`,
  V's and C's validator and catalogue tests, `tests/integration/test_spec006_x1_exams.py::test_a_removed_item_is_reported_not_blocking`,
  `tests/integration/test_spec002_d3_parity.py`, `tests/unit/infrastructure/test_spec002_schema_version.py`,
  `python scripts/validate_bank.py` and `python scripts/db_sync_check.py` (FR-003, FR-004, FR-005,
  FR-007, spec 006 FR-024 stay green through L).
- [ ] T002 [P] [US4] `tests/integration/test_spec008_l_item_life.py` (both engines), pins that pass
  on unchanged code:
  - `::test_spec008_l_an_untouched_bank_difficulty_keeps_the_calibration` — item inserted at 900,
    `difficulty` set to 1234 by valid answers (through `conftest.answer`), the bank left at 900,
    `sync_items_from_bank_folder` run again → 1234 (FR-031, US4-AS2 second half).
  - `::test_spec008_l_history_keeps_a_retired_item` — an item answered, then synced with
    `"retired": true` (ignored today): `get_item_by_id` returns it; the attempt, its join with
    `items` and the exam history still carry it; the student's rating rows are unchanged
    (US4-AS1, «its row and its attempts stay»).
  - `::test_spec008_l_no_item_row_is_ever_deleted` — no `DELETE FROM items` in either repository
    (text check); a bank without an id leaves its row (FR-030, «never delete»).
- [ ] T003 [P] [US4] `tests/api/test_spec008_l_serving.py`, pins that pass on unchanged code:
  - `::test_spec008_l_a_started_exam_grades_an_item_retired_since` — exam started, item marked and
    synced, submit → the item is graded (spec § Edge Cases).
  - `::test_spec008_l_an_answer_to_an_item_retired_after_serving_is_accepted` — `/next-question`
    serves it, the mark is synced, `/answer` → 200 and the rating moves (O-IL2).
- [ ] T004 [P] [US4] `tests/unit/scripts/test_validate_bank.py::test_spec008_l_an_unretired_item_keeps_its_manifest_binding`
  — an item with `"retired": false` and another topic than its manifest entry fails naming both
  topics (passes on V's merged code: the manifest binds every bank id) (FR-033, «the manifest keeps
  it bound»).

**Checkpoint**: T001–T004 green on unchanged code.

## Phase 2 — `[CHANGE]` tests first (each fails on the unchanged code, for the stated reason)

- [ ] T005 [P] [US4] Retirement in the sync (depends on T001), `tests/integration/test_spec008_l_item_life.py`:
  - `::test_spec008_l_a_retired_item_is_stamped_and_kept` — `"retired": true` → the row stays,
    `retired_at` is set, a second sync keeps the first `retired_at`, attempts and
    `student_course_topic_elo` rows unchanged; a new id arriving retired is inserted retired
    (O-IL13). Fails: no `retired_at` column.
  - `::test_spec008_l_removing_the_mark_serves_it_again` — mark removed, and separately set to
    `false` → `retired_at` NULL and the item back in `get_items_from_db`. Fails: no column.
  (FR-030, FR-033, US4-AS1)
- [ ] T006 [P] [US4] Practice and blocks (depends on T001), same file:
  - `::test_spec008_l_practice_never_serves_a_retired_item` — a course of three items, one retired:
    `get_items_from_db(course_id=…)` (and with `block=`, `topic=`) excludes it; `StudentService.get_next_question`
    over many draws never returns it. Fails: served.
  - `::test_spec008_l_block_counts_skip_retired_items` — `get_course_blocks` counts only items in
    circulation. Fails: counted.
  (FR-030, US4-AS1, SC-001)
- [ ] T007 [P] [US4] Exams, diagnostic, templates, PvP (depends on T001), `tests/api/test_spec008_l_serving.py`:
  - `::test_spec008_l_new_exams_and_the_diagnostic_skip_a_retired_item` — standard exam start and
    `GET /api/student/diagnostic/{course}` over a course whose every other item is drawn: the retired
    one never appears. Fails: drawn.
  - `::test_spec008_l_a_template_with_a_retired_item_is_refused` — start → 409 «ya no están
    disponibles»; `POST /api/teacher/exam-templates` and `PATCH` with the retired id → 400
    (O-IL3). Fails: start succeeds, create accepts.
  - `::test_spec008_l_pvp_never_draws_a_retired_item` — a course of 11 items, one retired; a formed
    match's 10 items exclude it (WebSocket test client as `tests/api/test_pvp.py`). Fails: may
    draw it (seeded `random`).
  (FR-030, US4-AS1, SC-001)
- [ ] T008 [P] Guard (depends on T001): `tests/unit/test_architecture_layers.py::test_spec008_l_only_serving_reads_filter_retired_items`
  — in both repositories, `retired_at IS NULL` appears exactly in `get_items_from_db` and
  `get_course_blocks` (and the O-IL4 repair's own method), nowhere else. Fails: appears nowhere.
  (FR-030; constitution II)
- [ ] T009 [P] [US4] The bank difficulty (depends on T002), `tests/integration/test_spec008_l_item_life.py`:
  - `::test_spec008_l_an_edited_bank_difficulty_wins` — inserted at 900, answered to 1234, bank
    edited to 700, synced → `difficulty` 700, `bank_difficulty` 700, RD unchanged (O-IL11), one
    `item_difficulty_changes` row `('sync', 1234, 700)` (O-IL8). Fails: stays 1234.
  - `::test_spec008_l_an_edit_equal_to_the_stored_difficulty_changes_nothing` — stored 700, bank
    edited to 700 → no change, no audit row. Fails: no audit table.
  - `::test_spec008_l_the_first_sync_after_the_migration_keeps_every_difficulty` — rows with
    `bank_difficulty` NULL and a calibrated `difficulty` ≠ bank: the sync fills `bank_difficulty`
    with the bank value, keeps `difficulty`, records nothing (O-IL6). Fails: no column.
  - `::test_spec008_l_the_upgrade_forces_one_sync` — a database whose last `bank_syncs` row is the
    pre-L fingerprint resyncs once at the next start and not at the one after (O-IL7). Fails: the
    fingerprint is unchanged, no sync.
  (FR-031, US4-AS2)
- [ ] T010 [P] [US4] Recalibration, domain (depends on T001),
  `tests/unit/domain/test_spec008_l_recalibration.py`:
  - `::test_spec008_l_dstar_inverts_the_expected_score` — for one rating R and share P\*, `dstar`
    equals `R + 400·log10((1 − P*)/P*)` (AGENTS: P\*=0.25 → R+191, P\*=0.10 → R+382); for mixed
    ratings, `Σ expected_score(r, dstar) = successes`. Fails: absent.
  - `::test_spec008_l_the_plan_skips_retired_few_attempts_and_small_changes` — < 10 attempts,
    retired, |Δ| < 25 skipped; 0 % and 100 % finite; clamped to 400–2000; integers; `--method bank`
    plans `bank_difficulty` where it differs. Fails: absent.
  (FR-032, O-IL9)
- [ ] T011 [P] [US4] Recalibration, script (depends on T001), `tests/integration/test_spec008_l_recalibration.py`
  (both engines; the script run as a subprocess against a temporary database):
  - `::test_spec008_l_a_dry_run_counts_and_writes_nothing` — prints counts; `items` and
    `item_difficulty_changes` unchanged. Fails: no script.
  - `::test_spec008_l_apply_records_every_change` — `--apply` writes each planned difficulty and one
    row per change with item, previous, new, source (`dstar`; `bank` with `--method bank`) and a
    time. Fails: no script.
  - `::test_spec008_l_an_item_moved_since_the_plan_is_skipped` — an answer moves the item between
    plan and write (`apply_item_difficulty_changes` called with a stale previous value) → skipped
    and counted, nothing recorded. Fails: no method.
  - `::test_spec008_l_the_script_migrates_nothing` — run against a database at the previous schema
    version: `schema_versions` and `bank_syncs` unchanged (`RUN_MIGRATIONS=0`, survey B16). Fails:
    no script.
  (FR-032, US4-AS3)
- [ ] T012 [P] [US4] Validator and generator (depends on T001):
  - `tests/unit/scripts/test_validate_bank.py::test_spec008_l_retired_must_be_a_boolean` — `"yes"`,
    `1`, `null` fail naming the item; `true`, `false` pass. Fails: unknown keys are ignored.
  - `…::test_spec008_l_retired_items_do_not_count_for_a_small_topic` — a topic of 5 with 1 retired
    warns. Fails: counted.
  - `…::test_spec008_l_a_manifest_id_missing_from_the_bank_names_the_retired_mark` — the O-V6 error
    names `"retired": true` (O-IL5). Fails: V's message.
  - `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_l_the_generator_carries_the_retired_mark`
    — a source item with `"retired": true` is projected with it. Fails: dropped by `CAMPOS_BANCO`.
  (FR-030, FR-033)
- [ ] T013 [P] Orphans, if O-IL4 is approved with its FR-034 (depends on T001),
  `tests/integration/test_spec008_l_item_life.py::test_spec008_l_the_orphan_repair_counts_then_retires`
  — a row in no bank file: the count-only run writes nothing; `--apply` stamps `retired_at`; a
  second run changes nothing; a bank item is never touched. Fails: no repair.
- [ ] T014 Schema test (depends on T001): `tests/unit/infrastructure/test_spec002_schema_version.py`
  fails once `_add_item_life` exists until `SCHEMA_VERSION` and the digest are raised (it is the
  existing guard; no new test).

**Checkpoint**: T005–T013 collected and failing for the reasons stated; T001–T004 still green.

## Phase 3 — Implementation (after Phase 2 fails for the right reason)

- [ ] T015 Migration, both engines (R1, R8): `_add_item_life` — `items.retired_at TIMESTAMP`,
  `items.bank_difficulty INTEGER`, `item_difficulty_changes` (plan § Schema) and
  `idx_item_difficulty_changes_item`; called from `_run_migration`; listed in `_MIGRATION_METHODS`.
  `SCHEMA_VERSION` = the next free on `redesign` at rebase (8 if spec 004 E3, PR #73, has merged;
  else 7), its comment line, the new `MIGRATION_SOURCES_DIGEST`. `python scripts/db_sync_check.py`
  passes with **no** `engine_differences.py` entry (same type families) (depends on T005, T009, T014).
- [ ] T016 Sync, both engines: retirement (stamp, keep, clear; new retired id inserted), bank
  difficulty (wins when it differs from `bank_difficulty`, `sync` audit row, RD untouched; NULL
  per O-IL6), PostgreSQL's unchanged-row comparison extended; `BANK_SYNC_FORMAT` hashed into
  `bank_fingerprint` (O-IL7) (depends on T015).
- [ ] T017 Serving reads, both engines: `AND retired_at IS NULL` in the four queries of
  `get_items_from_db` and in `get_course_blocks`; nothing else filters (depends on T006, T007,
  T008, T016).
- [ ] T018 Recalibration: `dstar` in `src/domain/elo/model.py`; `src/domain/bank/recalibration.py`;
  `get_item_calibration_rows` (`@_read_only`) and `apply_item_difficulty_changes` on both
  repositories (identical signatures; PostgreSQL `FOR UPDATE` on `items`, SQLite `BEGIN
  IMMEDIATE`; `put_connection` on PostgreSQL, R4); `scripts/recalibrate_items.py` on
  `_repair._repository()` (depends on T010, T011, T015).
- [ ] T019 If O-IL4 is approved: `scripts/repairs/retire_orphan_items.py` and its repository method
  `retire_orphan_items(apply=False)` on both engines (reads the bank ids the sync reads; counts by
  default) (depends on T013, T015).
- [ ] T020 Validator and generator: `retired` boolean; FR-043 count excludes retired; O-V6 message;
  `CAMPOS_BANCO` + `retired` (depends on T012).
- [ ] T021 `AGENTS.md`: § Item bank — `retired` (never delete an item from the JSON; un-retire by
  removing the mark), the bank-wins rule, `recalibrate_items.py` (and the orphan repair) in place
  of «recalibrate or retire»; § Database — `items.retired_at`, `items.bank_difficulty`,
  `item_difficulty_changes` in the table list; the bootstrap note that L's deploy resyncs once.
  `scripts/monthly_metrics.py`'s advice line names the script and the mark (depends on T016–T020).

## Phase 4 — Traceability and verification

- [ ] T022 `specs/008-item-bank/spec.md`: fill the L rows — FR-030 (T002 third, T005, T006, T007,
  T008, T012 first and third), FR-031 (T002 first, T009), FR-032 (T010, T011), FR-033 (T004, T005
  second), US4-AS1 (T002 second, T005 first, T006 first, T007), US4-AS2 (T002 first, T009 first),
  US4-AS3 (T011 first and second); FR-007's wording per the owner's answer to plan-l.md § Spec notes;
  FR-034 and its row if O-IL4 was approved; § Code Scope gains the new script(s) and
  `src/domain/bank/recalibration.py`; mark L `closed`. `docs/sdd/roadmap.md` M8 status line.
- [ ] T023 Review assertion adequacy: US4-AS1 asserts practice, new exam and PvP **and** the row,
  the attempts and the rating rows; US4-AS2 both halves; US4-AS3 both halves and every audited
  field (item, previous, new, source, time).
- [ ] T024 Verification: `ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q`
  (with `POSTGRES_TEST_DATABASE_URL` set to a local PostgreSQL, so the parametrised tests run on
  both engines); `python scripts/db_sync_check.py` (mandatory: both repositories changed);
  `python scripts/validate_bank.py`; `python scripts/build_epa8_bank.py --check`;
  `python scripts/check_traceability.py --run`; black and flake8. No `frontend/` change. V1: start
  `streamlit run src/interface/streamlit/app.py` locally once (shared repository code changed).
- [ ] T025 Hand-off note in the PR for the session that owns the transfer (no edit of
  `docs/transfer.md` here): the new `SCHEMA_VERSION` and its row for the version table, «repeat
  the backup and the rehearsal», the one resync after deploy, the DIAN +281 / SENA +200 values
  production never received and how O-IL6 treats them, and the orphan repair's count-only run on
  the rehearsal copy.

## Dependencies

T000 → T001 → (T002 ∥ T003 ∥ T004) and (T005 ∥ T006 ∥ T007 ∥ T008 ∥ T010 ∥ T011 ∥ T012 ∥ T013;
T009 after T002) → T014 → T015 → T016 → T017; T018 (after T010, T011, T015); T019 (after T013,
T015); T020 (after T012) → T021 → T022 → T023 → T024 → T025.
No implementation task starts before its Phase 2 test fails for the stated reason.
