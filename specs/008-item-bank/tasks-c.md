# Tasks — spec 008, delivery C (one course catalogue)

**Plan**: [plan-c.md](plan-c.md) · **Status**: approved (owner decisions O-C1 …
O-C9 answered 2026-10-21, each as recommended). FR-020 and FR-021 are `[CHANGE]`; US3-AS1 and US3-AS2 are their scenarios. C has no
`[AS-IS]` requirement of its own, but it rewires code that delivery A pinned (FR-001 validator,
FR-003 failed sync, FR-004 duplicate ids, FR-005 map change resyncs), so Phase 1 runs those pins and
a new course-rows pin on the unchanged code before anything changes.

## Phase 0 — Owner decisions and order (blocking)

- [x] T000 The owner decides O-C1 … O-C9 (plan-c.md § Owner decisions) and the plan's status
  becomes approved. A decision that differs from the recommendation is written into plan-c.md first
  and the affected tasks are adjusted in the same commit (e.g. O-C2 «curated names» turns T002's
  literal table into the new names and adds the rename to the transfer flag; O-C5 «fallback» turns
  T006's third test into a logged-fallback assertion; O-C7 «file bytes» changes T009's cases).
  **No task below starts before this.** Done 2026-10-21: every recommended option was approved, so
  the tasks below stand as written.
- [x] T000a Delivery V is merged into `redesign` (it creates `src/domain/bank/` and changes
  `scripts/validate_bank.py`); branch `008-c` starts from that `redesign`. **No task below starts
  before this.** (V's plan is merged, #144; V's code is not yet.) Satisfied by **stacking**:
  `008-c` starts from V's code branch `origin/008-v` @ `c18bf5c` (open PR #151), which already
  contains `redesign` @ `809731e`. C's pull request targets `008-v` and merges **after #151**.

## Phase 1 — Pins green on the unchanged code (blocking)

- [x] T001 Run, on `redesign` after V and unchanged by C, and record the green run in the PR:
  `tests/unit/scripts/test_validate_bank.py`, `tests/unit/infrastructure/test_bank_content.py`,
  `tests/integration/test_spec002_d1_startup.py::test_spec002_d1_a_changed_course_map_resyncs_the_bank`,
  `tests/integration/test_sqlite_bank_sync_failure.py`, `tests/integration/test_bank_duplicate_id.py`,
  `tests/integration/test_spec002_d3_parity.py`, `tests/integration/test_spec001_catalogue.py`,
  `tests/integration/test_spec008_t_topics.py`, `tests/unit/scripts/test_spec002_d3_db_sync_check.py`;
  `python scripts/validate_bank.py` (exit 0) and `python scripts/db_sync_check.py` (exit 0)
  (FR-001, FR-003, FR-004, FR-005 stay green through C).
  **Recorded 2026-10-27** on `008-v` @ `c18bf5c`: 114 passed, 0 skipped (SQLite and PostgreSQL);
  `validate_bank.py` exit 0; `db_sync_check.py` exit 0.
- [x] T002 [P] [US3] New pin, both engines, passes on unchanged code:
  `tests/integration/test_spec008_c_courses.py::test_spec008_c_synced_courses_keep_their_block_and_name`
  — a bootstrap from the real bank stores exactly the 49 `(id, name, block)` rows of plan-c.md
  § Measured facts (the 10 first-topic names, DIAN, SENA, EPA8 and the 36 `«<label> Semillero <g>°»`)
  (FR-020; O-C2: no stored row changes).
  **Recorded**: passes on the unchanged code on both engines (2 passed). A fresh SQLite bootstrap
  stores 49 courses, 2,031 items, bank fingerprint `3ea461a8…bddd`.

**Checkpoint**: T001–T002 green on unchanged code.

## Phase 2 — `[CHANGE]` tests first (each fails on the unchanged code, for the stated reason)

- [x] T003 [P] [US3] The catalogue module (depends on T001):
  `tests/unit/domain/test_spec008_c_catalogue.py`
  - `::test_spec008_c_every_bank_course_has_a_block_and_a_name` — every file under `items/bank/`
    resolves to a block in `COURSE_BLOCKS` and a non-empty name (FR-020, US3-AS1);
  - `::test_spec008_c_a_semillero_file_gives_block_grade_and_name` — 6 subjects × grades 6–11:
    «Semillero», *g*, `«<label> Semillero <g>°»` (FR-021, US3-AS2; O-C3);
  - `::test_spec008_c_a_semillero_name_outside_the_rule_is_refused` — grade 5 and 12, an unknown
    subject, a top-level `logica_semillero_6.json` (FR-021; O-C4);
  - `::test_spec008_c_the_catalogue_imports_only_the_standard_library` (FR-020; the bank job
    installs nothing).
  Fail today: module absent.
- [x] T004 [P] [US3] One copy (depends on T001):
  `tests/unit/infrastructure/test_spec008_c_one_catalogue.py::test_spec008_c_neither_repository_holds_a_course_map`
  — neither repository's source defines `_COURSE_BLOCK_MAP` or `_COURSE_NAME_MAP`, and both import
  `src.domain.bank.catalogue` (FR-020, SC-003). Fails today: both define both maps.
- [x] T005 [P] [US3] The validator (depends on T001), each on a temporary bank as CI runs it
  (V's `_run`, which also writes the manifest):
  - `tests/unit/scripts/test_validate_bank.py::test_spec008_c_the_validator_reads_the_catalogue`
    — a course added to the catalogue (monkeypatched module) passes; absent, it fails naming the
    file and `src/domain/bank/catalogue.py` (FR-020, US3-AS1);
  - `::test_spec008_c_a_course_with_no_explicit_name_fails` — an entry with an empty name fails
    naming the course (FR-021, US3-AS1);
  - `::test_spec008_c_a_semillero_file_name_must_give_a_grade` — `semillero/logica_semillero_12.json`
    and `semillero/logica.json` fail; `semillero/logica_semillero_6.json` passes with no entry
    (FR-021, US3-AS2);
  - `::test_spec008_c_a_catalogue_course_with_no_file_fails` (per O-C6; FR-020).
  Fail today: the validator parses the repositories and checks no name.
- [x] T006 [US3] Both engines sync from the catalogue (depends on T002):
  `tests/integration/test_spec008_c_courses.py`
  - `::test_spec008_c_both_engines_sync_the_catalogues_block_and_name` — a catalogue entry changed
    (block and name) is stored on both engines after the next start; reordering a course's items
    does not rename it (FR-020, US3-AS1);
  - `::test_spec008_c_a_semillero_file_syncs_as_its_grade_without_an_entry` — a temporary bank with
    `semillero/probabilidad_semillero_9.json` and no catalogue entry for it: block «Semillero», name
    «Probabilidad Semillero 9°», listed by `get_available_courses_by_level("semillero", grade="9")`
    and not for grade 8 (FR-021, US3-AS2);
  - `::test_spec008_c_an_unknown_course_is_not_synced` (per O-C5; FR-020).
  Fail today: the catalogue does not exist.
- [x] T007 [P] The fingerprint (depends on T001):
  `tests/unit/infrastructure/test_spec008_c_one_catalogue.py::test_spec008_c_the_fingerprint_hashes_the_catalogue`
  — per O-C7: changing a bank course's block or name in the catalogue changes the fingerprint; a
  catalogue edit that changes no bank course's block or name does not (FR-020 with FR-005). Fails
  today.
- [x] T008 [P] `db_sync_check.py` (depends on T001):
  `tests/unit/scripts/test_spec002_d3_db_sync_check.py::test_spec008_c_a_course_map_in_a_repository_fails`
  — a copy of a repository source with a `_COURSE_BLOCK_MAP` makes the check fail (O-C9; FR-020).
  Fails today: section 2 requires the maps.

**Checkpoint**: T003–T008 collected and failing for the reasons stated; T001–T002 still green.
**Recorded 2026-10-27** (commit «tests first»): 62 failed, 61 passed over the five files touched.
- T003: 43 failed — `ModuleNotFoundError: No module named 'src.domain.bank.catalogue'` (the stdlib
  test: the probe subprocess exits 1 on the same import).
- T004: `AssertionError: sqlite_repository.py` — both repositories assign both maps.
- T005: 9 failed — the validator subprocess cannot import `src.domain.bank.catalogue` (the
  validator still parses the repositories' maps and checks no name).
- T006: 6 failed (both engines) — `cannot import name 'catalogue' from 'src.domain.bank'` for the
  first two; the third stores `('Tema desconocido', 'Universidad')` (the silent fallback).
- T007: `cannot import name 'catalogue'`.
- T008: `_COURSE_NAME_MAP` in one copy → exit 0 (section 2 ignores the name map);
  `_COURSE_BLOCK_MAP` → exit 1 on «Mismas claves» without naming `src.domain.bank.catalogue`.
- T001–T002 still green (61 passed, none skipped).

## Phase 3 — Implementation (after Phase 2 fails for the right reason)

- [ ] T009 [US3] `src/domain/bank/catalogue.py` (O-C1): `COURSES` (13 explicit entries, today's
  names per O-C2, no `aritmetica` per O-C6), `SEMILLERO_SUBJECTS`, `semillero_grade`, `course_entry`,
  `catalogue_problems`, `fingerprint_view` (depends on T003).
- [ ] T010 [US3] Both repositories, together (R1): delete both maps; `sync_items_from_bank_folder`
  resolves each course through `course_entry` and handles an unknown course per O-C5;
  `_sync_bank_if_changed` passes `fingerprint_view` to `bank_fingerprint` (O-C7). Run
  `python scripts/db_sync_check.py` (depends on T004, T006, T007, T009).
- [ ] T011 Fixtures only, no assertion changes (depends on T010): a shared fixture registers a
  temporary course in the catalogue (monkeypatch of `COURSES`) and replaces every monkeypatch of the
  repositories' maps — `test_spec002_d1_startup.py::test_spec002_d1_a_changed_course_map_resyncs_the_bank`
  (FR-005), `test_spec002_d3_parity.py`, `test_sqlite_bank_sync_failure.py` (FR-003; the typo block
  goes in the catalogue entry) — and is used by the files that sync unmapped temporary courses
  (`test_bank_duplicate_id.py` FR-004, `test_spec002_d3_parity.py`, `test_spec008_t_topics.py`) when
  O-C5 skips unknown courses.
- [ ] T012 [US3] Validator: remove `course_block_maps` and the `ast` import; call
  `catalogue_problems` (depends on T005, T009). **Flip** the pinned
  `tests/unit/scripts/test_validate_bank.py::test_a_course_missing_from_the_course_map_is_an_error`:
  it asserts the catalogue's path instead of `_COURSE_BLOCK_MAP`, docstring citing FR-020.
  **Replace** `::test_the_course_map_is_read_from_both_repositories` (it reads the removed maps) by
  T005's `test_spec008_c_the_validator_reads_the_catalogue`, recorded in T016's spec amendment.
- [ ] T013 [US3] `src/domain/entities.py::in_catalogue` uses `semillero_grade` (O-C8); T001's
  `test_spec001_catalogue.py` stays green (depends on T009).
- [ ] T014 `scripts/db_sync_check.py` section 2 per O-C9; `engine_differences.py` unchanged
  (depends on T008, T010).
- [ ] T015 Docs: `AGENTS.md` R1 checklist (one catalogue, no copy per repository), § Database
  («both course maps» → the course catalogue), § Item bank «New course» (add the entry to the
  catalogue; a semillero file needs none); `README.md` «Nuevo curso»; the CI bank job's pytest line
  gains `tests/unit/domain/test_spec008_c_catalogue.py` (depends on T012).

## Phase 4 — Traceability and verification

- [ ] T016 `specs/008-item-bank/spec.md`: fill the C rows — FR-020 (T002, T003 first and fourth,
  T004, T005 first and fourth, T006 first and third, T007, T008), FR-021 (T003 second and third,
  T005 second and third, T006 second), US3-AS1 (T003 first, T005 first and second, T006 first),
  US3-AS2 (T003 second, T005 third, T006 second); mark C `closed`; Code Scope gains
  `src/domain/bank/catalogue.py`, `src/domain/entities.py`, `scripts/db_sync_check.py`. **Spec
  amendment for the owner**: FR-001 «missing from the course catalogue» and its row cites
  `test_spec008_c_the_validator_reads_the_catalogue` instead of the replaced test (plan-c.md § Spec
  notes). `docs/sdd/roadmap.md` M8 status line.
- [ ] T017 Review assertion adequacy: US3-AS1's three parts (sync, validator, unnamed course) and
  US3-AS2's «without a map entry» each have a test that would fail without the change.
- [ ] T018 Verification: `ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q`
  on both engines; `python scripts/db_sync_check.py` (mandatory, repositories changed);
  `python scripts/validate_bank.py`; `python scripts/build_epa8_bank.py --check`;
  `python scripts/check_traceability.py --run`; black and flake8. Record in the PR: the fingerprint
  before and after (one resync expected, O-C7), T002 green (no course row changed), `SCHEMA_VERSION`
  and `MIGRATION_SOURCES_DIGEST` unchanged. V1 starts (shared repositories, same behaviour). No
  `frontend/` change. Note for the session that owns the transfer: plan-c.md § The transfer.

## Dependencies

T000, T000a → T001 → T002 → (T003 ∥ T004 ∥ T005 ∥ T007 ∥ T008), T006 (after T002) → T009 (after
T003) → T010 (after T004, T006, T007, T009) → T011 → T012 (after T005) → T013 → T014 (after T008)
→ T015 → T016 → T017 → T018.
No implementation task starts before its Phase 2 test fails for the stated reason.
