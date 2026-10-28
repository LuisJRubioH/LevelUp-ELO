# Feature Specification: Item Bank

**Feature Branch**: `008-item-bank` (one branch per delivery once implementation starts)

**Created**: 2026-10-20

**Status**: Draft for the owner's approval. Written from the as-is survey
(`docs/sdd/item-bank-survey.md`, LuisJRubioH/LevelUp-ELO#50), re-verified on 2026-10-19 (its § 7),
with the owner's decisions of 2026-10-20 (its § 8, D1 … D6). Delivery A pins what already holds:
the fixes B7, B13, B15, B20, B21 and B22 merged on 2026-10-20 (#108, #110, #111, #113, #116,
#117, #118). B19 (topics too fine) was decided in a third round: a coarse topic carries the
rating, the fine label becomes a subtopic.

**Input**: Roadmap M8 (`docs/sdd/roadmap.md`): the item bank — its validation, its sync into both
databases, the course catalogue, and the life of an item.

**Outcome served** (constitution VIII): a student is served only items that are well formed, of a
difficulty that means what the bank says, in the course and topic their rating is kept for — and a
wrong item can be taken out of circulation without losing anyone's history.

## Code Scope *(mandatory)*

- `scripts/validate_bank.py` — the bank validator CI runs
- `scripts/build_epa8_bank.py` — the EPA8 bank generator and its `--check`
- `scripts/update_id_manifest.py` — appends new ids to the id manifest (delivery V)
- `src/domain/bank/rules.py` — the bank's rules, read by the validator and the EPA8 generator
  (delivery V)
- `items/id_manifest.json` — each id's course and topic (delivery V; outside the bank fingerprint)
- `items/bank/` — the bank files (content is data; their rules are this spec's)
- `src/domain/bank/catalogue.py` — the course catalogue: block and name of every course, the
  semillero rule (delivery C)
- `src/domain/entities.py` — `in_catalogue` reads the catalogue's semillero grade (delivery C;
  shared with spec 001)
- `scripts/db_sync_check.py` — section 2: neither repository holds a course map (delivery C;
  shared with spec 002)
- `src/infrastructure/persistence/sqlite_repository.py`,
  `src/infrastructure/persistence/postgres_repository.py` — the bank sync, which reads the course
  catalogue, item reads (shared with specs 001, 002, 006)
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
| **T** | Topics and subtopics (B19): the coarse topic carries the rating, the fine label becomes `subtopic` (additive `items.subtopic` column, both engines, `SCHEMA_VERSION` bump); DIAN and EPA8 regrouped once; a warning for a topic with fewer than 5 items. Lands **before** V commits the id manifest | closed |
| **V** | Validator rules: an integer difficulty in 400–2000 (D1), no existing id changing course or topic against a committed id manifest (D4), the EPA8 bank checked against its generator in CI (D6) | closed |
| **C** | One course catalogue: block and name of every course in one module that both repositories and the validator read; semillero block and grade from the file name (D5) | closed |
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
- Q: Topics too fine (B19)? → A: deferred at first; decided in the third round below.

### Session 2026-10-20, second round (owner decisions on the draft)

- Q: Where does the id manifest live (N1)? → A: `items/id_manifest.json`, outside `items/bank/`,
  so the sync never reads it as a course (FR-011).
- Q: What does «audited» mean (N2)? → A: every recalibration change is recorded in an additive
  database table on both engines, not a log file, so the record survives deploys (FR-032).
- Q: Can a retired item come back (N3)? → A: yes, by removing the mark; it stays bound to its
  course and topic through the manifest (FR-033).

### Session 2026-10-20, third round (B19)

- Q: DIAN has 293 items in 209 topics and EPA8 60 in 59, so most topics carry one item and a
  rating that one answer sets. What carries the rating? → A: the coarse topic (EPA8: the five
  «Pensamiento …» areas; DIAN: «Constitución Política» and its peers); the fine label is kept as a
  subtopic for study reports — «it was a writing problem» (owner). FR-040 … FR-043.
- Q: What happens to ratings already stored on the old fine topics? → **To confirm in the plan**
  (Assumptions): recommended, each student's fine-topic ratings of one coarse topic are combined
  into it as their mean, marked `approximate` with provenance, never rebuilt from attempts.

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

### User Story 5 - The rating counts a topic, the study report sees the subtopic (Priority: P1) — T

**Why this priority**: with one item per topic, one lucky answer fixes a topic's rating for good,
the course rating weighs areas by how many fine labels they have, and the teacher reads 59 rows of
one answer each. The fine label is still wanted, for study.

**Independent Test**: both engines sync the regrouped EPA8 bank; practice, ratings and the study
report are checked.

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** EPA8 item P01, today «Pensamiento aleatorio — porcentaje sobre un
   total», **When** the regrouped bank is synced, **Then** its `topic` is «Pensamiento aleatorio»
   and its `subtopic` is «porcentaje sobre un total», and EPA8 has five topics.
2. **US5-AS2** — **Given** a student who answers P01 and P05 (both «Pensamiento aleatorio»),
   **When** the ratings are read, **Then** both answers move the one rating of «Pensamiento
   aleatorio», and no rating is keyed by a subtopic.
3. **US5-AS3** — **Given** a student's answers on items of subtopic «porcentaje sobre un total»,
   **When** the study report is read, **Then** it shows the results per subtopic, across courses.
4. **US5-AS4** — **Given** a topic with fewer than 5 items, **When** the validator runs, **Then**
   it warns, naming the topic, and does not fail.

### Edge Cases

- **An exam already started with an item retired since**: the item is graded as it was served;
  only new exams and new practice skip it (spec 006 FR-024 covers an item that no longer exists).
- **A retired item un-retired** (`"retired"` removed or `false`): it returns to circulation; the
  manifest still forbids changing its course or topic.
- **An edited difficulty equal to the calibrated value**: nothing changes.
- **A moved item** (D4): the old id is retired, the new id is added to the manifest; ratings on the
  old (course, topic) stay where they are (spec 001 R15).
- **Regrouping topics (B19)** happens once, in delivery T, before V commits the id manifest;
  after that the manifest forbids topic changes (FR-011).
- **An item with no subtopic**: allowed; it simply does not appear in the per-subtopic report.

## Requirements *(mandatory)*

### Functional Requirements

**What already holds (A)**

- **FR-001** [AS-IS]: When CI validates the bank, the system shall fail on a missing required
  field, a key outside the options, fewer than two options, a duplicate id across files, prose
  between two `$`, a control character from a single-backslash LaTeX command (AGENTS R5), a
  newline that cuts a formula, an empty or non-text topic, an id that is not non-empty text, tags
  that are not a list of non-empty text, an image that does not exist, or a file whose course is
  missing from the course catalogue (amended by delivery C: the repositories' course maps became
  the catalogue, FR-020).
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

**Topics and subtopics (T)**

- **FR-040** [CHANGE]: The system shall key ratings by an item's `topic` only; an item may carry an
  optional `subtopic` (text), stored in an additive `items.subtopic` column on both engines, which
  shall never key a rating (B19).
- **FR-041** [CHANGE]: The DIAN and EPA8 banks shall be regrouped once so that `topic` is the coarse
  topic — the text before « — » (EPA8) or « - » (DIAN) — and `subtopic` the rest; the regrouping
  shall land before the id manifest is committed (FR-011) (B19).
- **FR-042** [CHANGE]: The system shall offer a study report of a student's results per subtopic,
  across courses (B19).
- **FR-043** [CHANGE]: When a topic has fewer than 5 items, the validator shall warn, naming the
  topic, without failing (B19).

**Validator rules (V)**

- **FR-010** [CHANGE]: If an item's difficulty is not an integer between 400 and 2000 inclusive,
  then the validator shall fail; AGENTS § Item bank shall state that range (D1).
- **FR-011** [CHANGE]: If an id in the committed id manifest (`items/id_manifest.json`, outside
  `items/bank/`) appears in the bank with another course or topic, then the validator shall fail
  naming the id and both values; a new id shall be added to the manifest by a script, never by
  hand (D4, N1).
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
  difficulty, the source and the time in an additive database table on both engines, not a log
  file (D3, N2).
- **FR-033** [CHANGE]: When a retired item's mark is removed (or set to `false`), the sync shall
  clear its retirement and serve it again; the manifest keeps it bound to its course and topic
  (D2, N3).

### Key Entities

- **Bank item**: one entry of `items/bank/**.json`; its course is its file name.
- **Course catalogue**: block and display name per course (C).
- **Id manifest**: the committed record of each id's course and topic (V).
- **Retired item**: a row kept for history and no longer served; it can return by removing the mark
  (L).
- **Subtopic**: the fine label of an item, for study reports only (T).
- **Difficulty change record**: one row per recalibration change — item, previous and new
  difficulty, source, time (L).

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
- **To confirm in the plan of delivery T** (B19): ratings already stored on the old fine topics.
  Recommended: each student's ratings on the fine topics of one coarse topic are combined into the
  coarse topic as their mean, marked `approximate` with their provenance — as spec 001's legacy
  reconciliation does — and never rebuilt from attempts (AGENTS R15). The owner confirms this before
  T is implemented.

## New Decisions and Contradictions

Decided by the owner on 2026-10-20 (second round); see § Clarifications.

| # | Point | Decision |
|---|---|---|
| N1 | Where the id manifest lives | `items/id_manifest.json`, outside `items/bank/` so the sync never reads it as a course (FR-011). |
| N2 | What «audited» means for the recalibration script | An additive table of difficulty changes on both engines, not a log file, so the record survives deploys (FR-032). |
| N3 | Un-retiring an item | Allowed by removing the mark; the manifest keeps it pinned to its course and topic (FR-033). |
| B19 | Topics too fine | The coarse topic carries the rating; the fine label becomes `subtopic`, for study reports (FR-040 … FR-043). Migration of stored fine-topic ratings: to confirm in the plan. |

## Out of Scope *(mandatory)*

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
| US5-AS1 | T | `tests/unit/infrastructure/test_bank_content.py::test_dian_and_epa8_are_regrouped`<br>`tests/integration/test_spec008_t_topics.py::test_spec008_the_sync_stores_the_subtopic` |
| US5-AS2 | T | `tests/integration/test_spec008_t_topics.py::test_spec008_two_answers_in_one_coarse_topic_move_one_rating` |
| US5-AS3 | T | `tests/integration/test_spec008_t_topics.py::test_spec008_the_subtopic_report_counts_across_courses`<br>`tests/integration/test_spec008_t_topics.py::test_spec008_stats_and_teacher_view_carry_the_report`<br>`frontend/e2e/stats.spec.ts › muestra el reporte por subtema, del más débil al más firme (spec 008 US5-AS3)` |
| US5-AS4 | T | `tests/unit/scripts/test_validate_bank.py::test_a_small_topic_warns_and_passes` |
| US2-AS1 | V | `tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_difficulty_outside_400_2000_or_not_an_integer_fails`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_integer_difficulty_in_400_2000_passes` |
| US2-AS2 | V | `tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_id_whose_course_changed_fails_naming_both_values`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_id_whose_topic_changed_fails_naming_both_values`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_new_id_fails_until_the_script_adds_it`<br>`tests/unit/scripts/test_id_manifest.py::test_spec008_v_the_script_only_appends` |
| US2-AS3 | V | `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_a_hand_edited_epa8_bank_fails_the_check`<br>`tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_the_committed_epa8_bank_passes_the_check` |
| US3-AS1 | C | `tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_every_bank_course_has_a_block_and_a_name`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_the_validator_reads_the_catalogue`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_a_course_with_no_explicit_name_fails`<br>`tests/integration/test_spec008_c_courses.py::test_spec008_c_both_engines_sync_the_catalogues_block_and_name` |
| US3-AS2 | C | `tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_a_semillero_file_gives_block_grade_and_name`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_a_semillero_file_name_must_give_a_grade`<br>`tests/integration/test_spec008_c_courses.py::test_spec008_c_a_semillero_file_syncs_as_its_grade_without_an_entry` |
| US4-AS1 | L | PENDING |
| US4-AS2 | L | PENDING |
| US4-AS3 | L | PENDING |
| FR-001 | A | `tests/unit/scripts/test_validate_bank.py::test_two_amounts_in_one_sentence_are_flagged`<br>`tests/unit/scripts/test_validate_bank.py::test_the_bank_has_no_prose_read_as_math`<br>`tests/unit/scripts/test_validate_bank.py::test_an_unescaped_backslash_in_latex_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_a_newline_that_cuts_a_formula_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_an_empty_or_non_text_topic_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_an_id_that_is_not_text_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_tags_must_be_a_list_of_text`<br>`tests/unit/scripts/test_validate_bank.py::test_an_image_that_does_not_exist_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_a_course_missing_from_the_course_map_is_an_error`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_the_validator_reads_the_catalogue` |
| FR-002 | A | `tests/unit/infrastructure/test_bank_content.py::test_no_item_offers_the_same_answer_twice`<br>`tests/unit/infrastructure/test_bank_content.py::test_copies_of_a_question_share_the_key` |
| FR-003 | A | `tests/integration/test_sqlite_bank_sync_failure.py::test_a_failed_bank_sync_releases_the_database` |
| FR-004 | A | `tests/integration/test_bank_duplicate_id.py::test_a_new_duplicate_id_keeps_the_last_files_item`<br>`tests/integration/test_bank_duplicate_id.py::test_an_existing_duplicate_id_keeps_the_last_files_item` |
| FR-005 | A | `tests/integration/test_spec002_d1_startup.py::test_spec002_d1_a_changed_course_map_resyncs_the_bank` |
| FR-006 | A | `tests/api/test_calibrator_once.py::test_the_calibrator_is_loaded_once_per_process`<br>`tests/api/test_calibrator_once.py::test_without_a_model_the_shared_calibrator_returns_the_raw_value` |
| FR-007 | A | `tests/unit/application/test_repository_contracts.py::test_retired_methods_stay_gone` |
| FR-040 | T | `tests/unit/scripts/test_validate_bank.py::test_subtopic_must_be_text`<br>`tests/integration/test_spec008_t_topics.py::test_spec008_the_sync_stores_the_subtopic`<br>`tests/integration/test_spec008_t_topics.py::test_spec008_two_answers_in_one_coarse_topic_move_one_rating` |
| FR-041 | T | `tests/unit/infrastructure/test_bank_content.py::test_dian_and_epa8_are_regrouped`<br>`tests/integration/test_spec008_t_merge.py::test_spec008_the_repair_script_reads_the_committed_regrouping` |
| FR-042 | T | `tests/integration/test_spec008_t_topics.py::test_spec008_the_subtopic_report_counts_across_courses`<br>`tests/integration/test_spec008_t_topics.py::test_spec008_stats_and_teacher_view_carry_the_report` |
| FR-043 | T | `tests/unit/scripts/test_validate_bank.py::test_a_small_topic_warns_and_passes` |
| FR-010 | V | `tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_difficulty_outside_400_2000_or_not_an_integer_fails`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_integer_difficulty_in_400_2000_passes`<br>`tests/unit/domain/test_spec008_v_bank_rules.py::test_spec008_v_difficulty_rule`<br>`tests/unit/infrastructure/test_bank_validator.py::TestValidateItem::test_spec008_v_out_of_range_difficulty_is_an_error`<br>`tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_the_generator_applies_the_bank_difficulty_rule`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_agents_states_the_validators_difficulty_range`<br>`tests/unit/infrastructure/test_bank_content.py::test_spec008_v_every_bank_difficulty_is_an_integer_in_400_2000` |
| FR-011 | V | `tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_id_whose_course_changed_fails_naming_both_values`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_id_whose_topic_changed_fails_naming_both_values`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_new_id_fails_until_the_script_adds_it`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_manifest_id_missing_from_the_bank_fails`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_missing_manifest_fails`<br>`tests/unit/domain/test_spec008_v_bank_rules.py::test_spec008_v_manifest_rules`<br>`tests/unit/scripts/test_id_manifest.py::test_spec008_v_the_script_only_appends`<br>`tests/unit/scripts/test_id_manifest.py::test_spec008_v_a_changed_or_removed_entry_against_the_base_fails`<br>`tests/unit/scripts/test_id_manifest.py::test_spec008_v_the_bank_job_checks_the_manifest_against_the_base`<br>`tests/unit/infrastructure/test_bank_content.py::test_spec008_v_the_committed_manifest_matches_the_bank` |
| FR-012 | V | `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_a_hand_edited_epa8_bank_fails_the_check`<br>`tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_the_committed_epa8_bank_passes_the_check`<br>`tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_the_bank_job_runs_the_epa8_check` |
| FR-020 | C | `tests/integration/test_spec008_c_courses.py::test_spec008_c_synced_courses_keep_their_block_and_name`<br>`tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_every_bank_course_has_a_block_and_a_name`<br>`tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_the_catalogue_imports_only_the_standard_library`<br>`tests/unit/infrastructure/test_spec008_c_one_catalogue.py::test_spec008_c_neither_repository_holds_a_course_map`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_the_validator_reads_the_catalogue`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_a_catalogue_course_with_no_file_fails`<br>`tests/integration/test_spec008_c_courses.py::test_spec008_c_both_engines_sync_the_catalogues_block_and_name`<br>`tests/integration/test_spec008_c_courses.py::test_spec008_c_an_unknown_course_is_not_synced`<br>`tests/unit/infrastructure/test_spec008_c_one_catalogue.py::test_spec008_c_the_fingerprint_hashes_the_catalogue`<br>`tests/unit/scripts/test_spec002_d3_db_sync_check.py::test_spec008_c_a_course_map_in_a_repository_fails` |
| FR-021 | C | `tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_a_semillero_file_gives_block_grade_and_name`<br>`tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_a_semillero_name_outside_the_rule_is_refused`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_a_course_with_no_explicit_name_fails`<br>`tests/unit/scripts/test_validate_bank.py::test_spec008_c_a_semillero_file_name_must_give_a_grade`<br>`tests/integration/test_spec008_c_courses.py::test_spec008_c_a_semillero_file_syncs_as_its_grade_without_an_entry` |
| FR-030 | L | PENDING |
| FR-031 | L | PENDING |
| FR-032 | L | PENDING |
| FR-033 | L | PENDING |
