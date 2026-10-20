# Feature Specification: Item Bank

**Feature Branch**: `008-item-bank` (one branch per delivery once implementation starts)

**Created**: 2026-10-20

**Status**: Draft for the owner's approval. Written from the as-is survey
(`docs/sdd/item-bank-survey.md`, LuisJRubioH/LevelUp-ELO#50), re-verified on 2026-10-19 (its § 7),
with the owner's decisions of 2026-10-20 (its § 8, D1 … D6). Delivery A pins what already holds:
the fixes B7, B13, B15, B20, B21 and B22 merged on 2026-10-20 (#108, #110, #111, #113, #116,
#117, #118). B19 is deferred by the owner.

**Input**: Roadmap M8 (`docs/sdd/roadmap.md`): the item bank — its validation, its sync into both
databases, the course catalogue, and the life of an item.

**Outcome served** (constitution VIII): a student is served only items that are well formed, of a
difficulty that means what the bank says, in the course and topic their rating is kept for — and a
wrong item can be taken out of circulation without losing anyone's history.

## Code Scope *(mandatory)*

- `scripts/validate_bank.py` — the bank validator CI runs
- `scripts/build_epa8_bank.py` — the EPA8 bank generator and its `--check`
- `items/bank/` — the bank files (content is data; their rules are this spec's)
- `src/infrastructure/persistence/sqlite_repository.py`,
  `src/infrastructure/persistence/postgres_repository.py` — the bank sync, the course maps, item
  reads (shared with specs 001, 002, 006)
- `src/infrastructure/persistence/schema_version.py` — the bank fingerprint (shared with spec 002)
- `src/infrastructure/ml/calibration.py` — the display calibrator
- `src/domain/selector/item_selector.py` — which items practice can serve (shared with spec 001)
- `.github/workflows/ci.yml` — the «Banco de preguntas» job (shared)

## Deliveries *(this spec is delivered in steps)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it closed and fills all its rows.

| Delivery | Content | State |
|---|---|---|
| **A** | As-is pins: the validator's checks, the bank content tests, a failed sync releasing the database, duplicate ids resolved alike on both engines, a map change resyncing, the calibrator loaded once, the retired repository methods staying gone | closed |
| **V** | Validator rules: an integer difficulty in 400–2000 (D1), no existing id changing course or topic against a committed id manifest (D4), the EPA8 bank checked against its generator in CI (D6) | planned |
| **C** | One course catalogue: block and name of every course in one module that both repositories and the validator read; semillero block and grade from the file name (D5) | planned |
| **L** | An item's life: `"retired": true` takes an item out of practice, exams and PvP without deleting it (D2); a difficulty edited in the bank wins over the calibrated one, an untouched one keeps it, and an audited recalibration script (D3). Additive migrations on both engines and a `SCHEMA_VERSION` bump (AGENTS § Database) | planned |

## Clarifications

### Session 2026-10-20 (owner decisions, survey § 8)

- Q: Difficulty range (B6)? → A: an integer in 400–2000, as an error; AGENTS corrected; the 32 easy
  semillero items are not re-rated (D1).
- Q: Retiring an item (B8)? → A: `"retired": true` in the bank JSON; never a DELETE (D2).
- Q: A difficulty edited in the bank (B9)? → A: the edit wins; an untouched value keeps the
  calibration; an audited D\* recalibration script (D3).
- Q: Moving an item to another course or topic (B10)? → A: forbidden; a moved item gets a new id
  and the old one is retired (D4).
- Q: The course maps (B14)? → A: one shared catalogue module; every course named explicitly (D5).
- Q: EPA8 (B23)? → A: `build_epa8_bank.py --check` in the bank job (D6).
- Q: Topics too fine (B19)? → A: deferred by the owner, to be discussed (Out of Scope).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - What already holds keeps holding (Priority: P1) — A

**Why this priority**: the validator, the sync and the calibrator were fixed on 2026-10-20; they
stay fixed while the rest changes.

**Independent Test**: the existing unit, API and integration tests named in § Traceability.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a bank item with a LaTeX command written with one backslash, an empty
   topic, a numeric id, malformed tags, a missing image or a course outside the map, **When** CI
   validates the bank, **Then** the validator fails naming the item; a well-formed item passes.
2. **US1-AS2** — **Given** a bank sync that fails on SQLite, **When** another writer opens the
   database, **Then** it is not locked.
3. **US1-AS3** — **Given** an id present in two bank files, **When** either engine syncs, **Then**
   both keep the last file's item.

### User Story 2 - The validator catches what would mislead a student (Priority: P1) — V

**Why this priority**: a fractional or out-of-range difficulty, an item silently moved to another
topic, or an EPA8 file edited by hand all reach students today without CI noticing.

**Independent Test**: the validator run on temporary banks, as CI runs it.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** an item whose difficulty is 350, 2100, 900.5 or `true`, **When** CI
   validates the bank, **Then** it fails; an integer in 400–2000 passes.
2. **US2-AS2** — **Given** an id in the committed manifest whose course or topic changed in the
   bank, **When** CI validates the bank, **Then** it fails naming the id and both values; a new id
   passes once added to the manifest.
3. **US2-AS3** — **Given** an EPA8 bank file that differs from what `build_epa8_bank.py` generates,
   **When** the bank job runs, **Then** it fails.

### User Story 3 - One catalogue of courses (Priority: P2) — C

**Why this priority**: the block and name of each course are copied in both repositories and the
validator reads them by parsing source; ten courses take their name from their first item's topic.

**Independent Test**: the catalogue module, both repositories and the validator on the real bank.

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** the catalogue module, **When** either repository syncs or the validator
   runs, **Then** each uses the catalogue's block and name for every course, and a course without
   an explicit name fails validation.
2. **US3-AS2** — **Given** a file `items/bank/semillero/<subject>_semillero_<g>.json`, **When** it
   is synced, **Then** its course is in block «Semillero» for grade *g* without a map entry.

### User Story 4 - A wrong item leaves circulation; an edited difficulty takes effect (Priority: P2) — L

**Why this priority**: today a wrong item cannot be removed — dropping it from the JSON leaves it
served — and a corrected difficulty in the bank is ignored.

**Independent Test**: both engines sync a bank with a retired item and an edited difficulty; the
practice, exam and PvP item reads are checked.

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** an item marked `"retired": true`, **When** it is synced, **Then** it is
   no longer offered in practice, in a new exam or in a PvP match, its row and its attempts stay,
   and its rating history is unchanged.
2. **US4-AS2** — **Given** an item calibrated by use to 1234 whose bank difficulty changes from
   900 to 700, **When** it is synced, **Then** its difficulty is 700; **Given** the bank value
   untouched, **Then** it stays 1234.
3. **US4-AS3** — **Given** the recalibration script run without `--apply`, **When** it finishes,
   **Then** it prints counts and writes nothing; with `--apply`, every change is recorded with the
   item, the previous and new difficulty, the source and the time.

### Edge Cases

- **An exam already started with an item retired since**: the item is graded as it was served;
  only new exams and new practice skip it (spec 006 FR-024 covers an item that no longer exists).
- **A retired item un-retired** (`"retired"` removed or `false`): it returns to circulation; the
  manifest still forbids changing its course or topic.
- **An edited difficulty equal to the calibrated value**: nothing changes.
- **A moved item** (D4): the old id is retired, the new id is added to the manifest; ratings on the
  old (course, topic) stay where they are (spec 001 R15).
- **Regrouping topics (B19)** must happen before the manifest freezes topics (D4), or as a
  one-time, reviewed manifest update.

## Requirements *(mandatory)*

### Functional Requirements

**What already holds (A)**

- **FR-001** [AS-IS]: When CI validates the bank, the system shall fail on a missing required
  field, a key outside the options, fewer than two options, a duplicate id across files, prose
  between two `$`, a control character from a single-backslash LaTeX command (AGENTS R5), a
  newline that cuts a formula, an empty or non-text topic, an id that is not non-empty text, tags
  that are not a list of non-empty text, an image that does not exist, or a file whose course is
  missing from either repository's course map.
- **FR-002** [AS-IS]: The bank shall offer no item the same answer twice, and copies of one
  question shall share the key.
- **FR-003** [AS-IS]: If a bank sync fails on SQLite, then the system shall roll it back and release
  the database.
- **FR-004** [AS-IS]: When an id appears in two bank files, both engines shall keep the item of the
  last file read.
- **FR-005** [AS-IS]: When only a course map changes, the next start shall resync the bank, as
  spec 002 FR-016 defines.
- **FR-006** [AS-IS]: The system shall load the display calibrator once per process and return the
  raw probability when no model exists.
- **FR-007** [AS-IS]: The repositories shall offer no item loader or item-difficulty update besides
  the bank sync and the answer transaction.

**Validator rules (V)**

- **FR-010** [CHANGE]: If an item's difficulty is not an integer between 400 and 2000 inclusive,
  then the validator shall fail; AGENTS § Item bank shall state that range (D1).
- **FR-011** [CHANGE]: If an id in the committed id manifest appears in the bank with another course
  or topic, then the validator shall fail naming the id and both values; a new id shall be added to
  the manifest by a script, never by hand (D4).
- **FR-012** [CHANGE]: The «Banco de preguntas» CI job shall run `build_epa8_bank.py --check` and
  fail when the EPA8 bank differs from its generator's output (D6).

**One catalogue (C)**

- **FR-020** [CHANGE]: The system shall keep the block and name of every course in one catalogue
  module, read by both repositories and the validator; neither repository shall hold its own copy
  (D5).
- **FR-021** [CHANGE]: The system shall derive a semillero course's block and grade from its file
  name, and the validator shall fail on a course with no explicit name (D5).

**An item's life (L)**

- **FR-030** [CHANGE]: When a bank item carries `"retired": true`, the sync shall record when it was
  retired in an additive column, and practice, new exams and PvP shall not serve it; the system
  shall never delete an item row (D2).
- **FR-031** [CHANGE]: When an item's difficulty in the bank differs from the bank value last
  synced, the sync shall set the item's difficulty to the bank value; while the bank value is
  unchanged, the sync shall keep the calibrated difficulty (D3).
- **FR-032** [CHANGE]: The system shall offer a recalibration script that prints counts by default,
  writes only with `--apply`, and records every change with the item, the previous and new
  difficulty, the source and the time (D3).

### Key Entities

- **Bank item**: one entry of `items/bank/**.json`; its course is its file name.
- **Course catalogue**: block and display name per course (C).
- **Id manifest**: the committed record of each id's course and topic (V).
- **Retired item**: a row kept for history and no longer served (L).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 items served in practice, exams or PvP that are marked retired.
- **SC-002**: 0 bank items with a non-integer difficulty or one outside 400–2000.
- **SC-003**: 1 place where a course's block and name are written.
- **SC-004**: 0 ids whose course or topic changed after entering the manifest.

## Assumptions

- Ratings are keyed by (course, topic) and never rebuilt from attempts (spec 001, AGENTS R15).
- The sync runs only when the bank fingerprint changes (spec 002 FR-016).
- The item bank's content (statements, keys, distractors) is authored outside this spec; this spec
  sets its rules.

## New Decisions and Contradictions

| # | Point | Recommendation |
|---|---|---|
| N1 | Where the id manifest lives | `items/id_manifest.json`, outside `items/bank/` so the sync never reads it as a course. |
| N2 | What «audited» means for the recalibration script (FR-032) | An additive table of difficulty changes on both engines, not a log file, so the record survives deploys. |
| N3 | Un-retiring an item | Allowed by removing the mark; the manifest keeps it pinned to its course and topic. |

## Out of Scope *(mandatory)*

- **B19 — topics too fine** (DIAN 293 items in 209 topics, EPA8 60 in 59): deferred by the owner,
  to be discussed. Any regrouping must come before the id manifest freezes topics (FR-011), or as
  a one-time, reviewed manifest update.
- The rating arithmetic and the item-difficulty update after an answer — spec 001.
- The schema-version mechanics and the bank fingerprint itself — spec 002.
- Exams and the teacher's templates — spec 006, beyond not serving a retired item.
- `items/source/` and the textbook extraction, except the EPA8 generator check (survey § 8).
- V1 beyond keeping it working until it is retired (roadmap F-10).

## Traceability *(mandatory)*

Rows of delivery A cite tests that exist today; the rest are filled by the pull request that
closes their delivery.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | A | `tests/unit/scripts/test_validate_bank.py::test_an_unescaped_backslash_in_latex_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_an_empty_or_non_text_topic_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_an_id_that_is_not_text_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_tags_must_be_a_list_of_text`<br>`tests/unit/scripts/test_validate_bank.py::test_an_image_that_does_not_exist_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_a_course_missing_from_the_course_map_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_a_well_formed_item_passes` |
| US1-AS2 | A | `tests/integration/test_sqlite_bank_sync_failure.py::test_a_failed_bank_sync_releases_the_database` |
| US1-AS3 | A | `tests/integration/test_bank_duplicate_id.py::test_a_new_duplicate_id_keeps_the_last_files_item`<br>`tests/integration/test_bank_duplicate_id.py::test_an_existing_duplicate_id_keeps_the_last_files_item` |
| US2-AS1 | V | PENDING |
| US2-AS2 | V | PENDING |
| US2-AS3 | V | PENDING |
| US3-AS1 | C | PENDING |
| US3-AS2 | C | PENDING |
| US4-AS1 | L | PENDING |
| US4-AS2 | L | PENDING |
| US4-AS3 | L | PENDING |
| FR-001 | A | `tests/unit/scripts/test_validate_bank.py::test_two_amounts_in_one_sentence_are_flagged`<br>`tests/unit/scripts/test_validate_bank.py::test_the_bank_has_no_prose_read_as_math`<br>`tests/unit/scripts/test_validate_bank.py::test_an_unescaped_backslash_in_latex_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_a_newline_that_cuts_a_formula_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_an_empty_or_non_text_topic_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_an_id_that_is_not_text_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_tags_must_be_a_list_of_text`<br>`tests/unit/scripts/test_validate_bank.py::test_an_image_that_does_not_exist_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_a_course_missing_from_the_course_map_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_the_course_map_is_read_from_both_repositories` |
| FR-002 | A | `tests/unit/infrastructure/test_bank_content.py::test_no_item_offers_the_same_answer_twice`<br>`tests/unit/infrastructure/test_bank_content.py::test_copies_of_a_question_share_the_key` |
| FR-003 | A | `tests/integration/test_sqlite_bank_sync_failure.py::test_a_failed_bank_sync_releases_the_database` |
| FR-004 | A | `tests/integration/test_bank_duplicate_id.py::test_a_new_duplicate_id_keeps_the_last_files_item`<br>`tests/integration/test_bank_duplicate_id.py::test_an_existing_duplicate_id_keeps_the_last_files_item` |
| FR-005 | A | `tests/integration/test_spec002_d1_startup.py::test_spec002_d1_a_changed_course_map_resyncs_the_bank` |
| FR-006 | A | `tests/api/test_calibrator_once.py::test_the_calibrator_is_loaded_once_per_process`<br>`tests/api/test_calibrator_once.py::test_without_a_model_the_shared_calibrator_returns_the_raw_value` |
| FR-007 | A | `tests/unit/application/test_repository_contracts.py::test_retired_methods_stay_gone` |
| FR-010 | V | PENDING |
| FR-011 | V | PENDING |
| FR-012 | V | PENDING |
| FR-020 | C | PENDING |
| FR-021 | C | PENDING |
| FR-030 | L | PENDING |
| FR-031 | L | PENDING |
| FR-032 | L | PENDING |
