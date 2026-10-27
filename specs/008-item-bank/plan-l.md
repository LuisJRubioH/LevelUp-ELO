# Plan — spec 008, delivery L: an item's life (D2, D3)

**Spec**: [spec.md](spec.md) § Deliveries, L (US4; FR-030 … FR-033) · **Branch**: `008-l`, from
`redesign` **after V's and C's code are merged** · **Date**: 2026-10-22 · **Status**: approved
(owner, 2026-10-27: O-IL1 … O-IL13 as recommended)

Decision names: spec 007's delivery L already used «O-L1 … O-L3» (`specs/007-pvp/plan-l.md`), so
the decisions of this delivery are **O-IL1, O-IL2, …** («Item Life») to keep every decision name
unique across the repository.

## Summary

Two things a bank author cannot do today, and one tool:

- **D2 (FR-030, FR-033) — retiring an item.** `"retired": true` on a bank item makes the sync stamp
  an additive `items.retired_at`; the reads that **serve** items (practice, new exams, the
  diagnostic, PvP, the teacher's catalogue) skip it; every read of **history** (attempts, exams,
  procedures, KatIA records, ratings) keeps seeing the row. No item row is ever deleted. Removing
  the mark (or `false`) clears `retired_at` and serves the item again; V's manifest keeps it bound
  to its course and topic.
- **D3 (FR-031) — a bank edit wins, an untouched value keeps the calibration.** An additive
  `items.bank_difficulty` stores the bank value last synced. When the bank value differs from it,
  the sync sets `difficulty` to the bank value; when it is equal, the calibrated `difficulty` stays.
- **D3, N2 (FR-032) — an audited recalibration script.** `scripts/recalibrate_items.py` prints
  counts by default, writes only with `--apply`, and records every change (item, previous and new
  difficulty, source, time) in an additive table `item_difficulty_changes` on both engines.

L is a schema change: two additive columns, one additive table and one index on both engines, the
next free `SCHEMA_VERSION` (§ Schema) and a new `MIGRATION_SOURCES_DIGEST`. It lands **after V and
C** (spec order) and closes V's open end: O-V6's «a manifest id missing from the bank is an error
until L» becomes «… is an error: mark it `"retired": true` instead» (O-IL5).

## Constitution Check (1.2.0)

| Principle | L |
|---|---|
| Spec is the contract (I) | FR-030 … FR-033 are `[CHANGE]`; each and US4-AS1 … AS3 get tests that fail on today's code (tasks-l.md Phase 2). The halves that hold today — an untouched bank value keeps the calibration (US4-AS2, second half), a started exam grades what it served, history reads join `items` with no filter — are pinned green first (Phase 1) |
| One source of truth (II) | «is this item in circulation» is decided in **one place per engine**: the item read every serving path already shares (`get_items_from_db`, O-IL1), plus the block counts. History reads never filter. The bank is the source of `retired` and of the bank difficulty; the database keeps only what the bank cannot know (the calibration and the audit trail) |
| Layers (III, R2) | the recalibration arithmetic (D\* inversion, plan of changes) is pure domain code — `src/domain/elo/model.py::dstar` beside `expected_score`, and `src/domain/bank/recalibration.py::plan_recalibration` beside V's `rules.py` and C's `catalogue.py`; the repositories return raw attempt rows and apply the changes (no averages in SQL: guard `test_spec001_no_rating_aggregation_in_repositories_or_routers`); the script is a composition point, as the repair scripts are |
| Dual database (IV, R1, R8) | `retired_at`, `bank_difficulty`, `item_difficulty_changes` and its index on both engines, same type family (no `engine_differences.py` entry needed, § Schema); the sync's change identical on both; two new public methods on both repositories with identical signatures; `db_sync_check.py` and `test_spec002_d3_parity.py` |
| Learning measurement (V, R15) | ratings are not touched: retiring changes no `student_course_topic_elo` row and no attempt; a difficulty change moves only `items.difficulty` (the item's side), never a student rating; nothing is rebuilt from attempts. FR-007's two exclusive item-difficulty writers become three (§ Spec notes) |
| Security (VI) | the script prints counts per course and source, never student rows; it runs with `RUN_MIGRATIONS=0` (`scripts/repairs/_repair.py::_repository`, survey B16), so it migrates and syncs nothing; an agent never runs it against production |
| Simplicity (VII) | no new dependency; the D\* inversion is a bisection over `expected_score` (standard library); one column per fact |
| Production (VI, AGENTS § Deploy) | the migration is additive; the first sync after it fills `bank_difficulty` without discarding a calibration (O-IL6); every write to production data beyond that is an owner-run script, count first |

## Measured facts (`redesign @ af9ab31`, 2026-10-22)

**Bank.** 49 files, **2,031 items**, every difficulty a JSON integer (V). **0 items carry a
`retired` key** (keys in use: `block`, `content`, `correct_option`, `difficulty`, `id`,
`image_path`, `image_url`, `options`, `subtopic`, `tags`, `topic`).

**How difficulty is written today (B9, holds).** Exactly two writers of `items.difficulty`:
- the bank sync **inserts** a new id with the bank `difficulty` and `rating_deviation` 350
  (`sync_items_from_bank_folder`, S:4313, P:4755); for an existing id it updates content, options,
  key, topic, course, image, tags, block and subtopic and **never** `difficulty` or
  `rating_deviation` (S:4410-4428; P:4815-4870 compares a static tuple that leaves both out);
- the answer transaction, only for an `elo_valid` attempt: `UPDATE items SET difficulty = ?,
  rating_deviation = ?` (S:2012, P:2438), with `difficulty + item_difficulty_delta(...)` computed in
  `StudentService` (`student_service.py:183`) and the item's RD passed through unchanged (`:208`).
So **an item whose `difficulty` differs from its bank value has either been answered validly or had
its bank value edited after it was inserted** — the two cases D3 separates.

**Column types.** `items.difficulty` is `REAL` on **both** engines (S:211, P:584 and P:948) — on
PostgreSQL that is single precision (float4): exact for every integer bank value, ~7 significant
digits for a calibrated one. `rating_deviation` is `REAL` on both. L does not change either type
(R8).

**What calibration does.** Nothing to `items`: `src/infrastructure/ml/calibration.py` is the
display-only isotonic calibrator of `expected_score`/`prob_failure` (FR-006, B15) and never touches
an item. **No recalibration script exists**: `scripts/monthly_metrics.py:96-103` only lists items
at 0 % success with ≥ 10 attempts and prints «Recalibrar o retirar»; AGENTS § Item bank gives the
manual formula `D*(R, P*) = R + 400 × log10((1 − P*) / P*)` (the inverse of `expected_score`,
`src/domain/elo/model.py:88`).

**Calibrated difficulties differing from the bank.** A fresh local SQLite bootstrap (schema 6,
2,031 items) has **0** attempts and **0** items whose difficulty differs from the bank. Production
is not measured by an agent; what can be measured is the bank it was loaded from. Comparing
`origin/main`'s bank (what production synced: 1,971 items, 48 courses) with `redesign`'s:
- **454 ids differ in difficulty, all in two courses: every DIAN item (293/293) is +281 on
  `redesign`, every SENA item (161/161) +200.** Under today's code these edits never reach
  production (B9); under L they reach it only as O-IL6 decides.
- `main`'s own history changed the difficulty of **38 ids** (e.g. `q81` 600 → 720 on 2026-03-09);
  a production row inserted before such an edit kept the older value.
- **25 ids left `main`'s bank and are in no bank file today** (`albS1` … `albS25`, the old
  `algebra_semillero` course — survey B8): any database that loaded them still serves them.
- `redesign` adds 60 ids (EPA8); no id changed course between the two banks.

**Where a retired item would leak — every read that serves items goes through one method.**
`get_items_from_db(topic, course_id, block)` (S:4672, P:5374; filters by course/block/topic only):

| Surface | Caller | Effect of filtering there |
|---|---|---|
| Practice | `StudentService.get_next_question` (`student_service.py:77`), V1 and V2 | the selector's pool (then `AdaptiveItemSelector`) has no retired item |
| Standard exam, diagnostic | `api/routers/student.py::_build_standard_exam` (:869; diagnostic at :1200) | not drawn |
| Template exam start | `_items_from_template` (:902); the start answers **409 «La plantilla contiene preguntas que ya no están disponibles»** when an item is missing (:988-992) | O-IL3 |
| Teacher's template create / edit | `api/routers/teacher.py:672, 709` («Items no encontrados en el curso») | a retired id cannot enter a template |
| Teacher's item catalogue | `teacher.py:911` | not listed |
| Course map topics | `student.py:1568` | a topic with only retired items is not drawn (its rating row stays, R15) |
| PvP | `api/websocket/pvp.py:672` (`_form_match`); spec 007 M keeps this read (plan-m.md O-M8: «the item read itself is today's `get_items_from_db`») | not drawn, nor used as M's fill |

Also `get_course_blocks` (S:4719, P:5423) counts items per thematic block for the concursos block
picker; it is a serving read (a block of only retired items would offer an empty practice).

**Reads that must keep a retired item (history).** `get_item_by_id` (S:4910, P:5634) — the answer
endpoint (:237), exam grading (:1083; spec 006 FR-024 handles a *missing* item), the diagnostic
submit (:1233), the procedure review (:726) and KatIA (`api/routers/ai.py:76`); and every join of
`attempts`, `exam_responses`, `procedure_submissions` or `pvp_matches` with `items` (history,
stats, teacher reports, exports, reconciliation `SELECT DISTINCT course_id, topic FROM items`,
`get_enrolled_topics`, `has_practice_attempts`). None filters by anything but ids, so a kept row
keeps rendering; L adds no filter to any of them (guard, tasks-l.md T008).

**The bank fingerprint.** `bank_fingerprint` hashes the bank files and the course maps
(`schema_version.py:86-99`; C replaces the maps by the catalogue's view). Adding `"retired": true`
or editing a difficulty changes a bank file, so the next start resyncs (spec 002 FR-016). **The
migration alone changes no bank file**: without O-IL7, the first start after L's deploy would skip
the sync and `bank_difficulty` would stay NULL until the next bank edit.

**Schema version.** `SCHEMA_VERSION = 6` on `redesign` (spec 008 T). Spec 004 E3 (PR #73, branch
`004-identity-e3`, open) raises it to **7** (`users.access_until`).
*Update 2026-10-27:* E3 is merged (version 7) and spec 009 I1 (PR #158) takes **8**; L takes the
next free version when its code PR lands — **9** if I1 lands first. The owner groups the rehearsals:
one backup and rehearsal for 6 → 8 (E3 + I1), and a later one for L.

**Tests that pin today's behaviour L keeps.** FR-003 (`test_sqlite_bank_sync_failure.py`), FR-004
(`test_bank_duplicate_id.py`), FR-005 (`test_spec002_d1_startup.py::…_a_changed_course_map_resyncs_the_bank`),
FR-007 (`test_repository_contracts.py::test_retired_methods_stay_gone`), spec 006 FR-024
(`test_spec006_x1_exams.py::test_a_removed_item_is_reported_not_blocking`), the parity test and the
schema-version test. No existing test asserts that the sync leaves `difficulty` alone, so none is
flipped silently; L's own pin (tasks-l.md T002) records that half before it changes.

## Design

### The bank and the validator (FR-030, FR-033)

- `retired` is an optional bank field: a JSON boolean (`true` or `false`); anything else is a
  validator error naming the item (O-IL12). A retired item is still validated in full — it can
  return (FR-033) and history renders it.
- FR-043's small-topic warning counts only items not retired (O-IL12).
- **V's O-V6 transition (O-IL5).** A manifest id missing from the bank **stays an error** after L;
  the message changes from «… until delivery L» to «`<id>` está en `items/id_manifest.json` pero no
  en el banco: no borres un ítem, márcalo `"retired": true`». An item leaves circulation only by
  the mark, never by deletion from the JSON — the bank keeps the content history needs and the
  un-retire path needs.
- EPA8: `build_epa8_bank.py`'s `CAMPOS_BANCO` passes `retired` through from
  `items/source/epa8/*.json`, so a retired EPA8 item is marked in the source and V's `--check`
  stays byte-exact.

### Schema (both engines; R8)

One migration method, `_add_item_life(cursor)`, called from `_run_migration` on both repositories
and listed in `_MIGRATION_METHODS`:

| Object | SQLite | PostgreSQL | Default / backfill |
|---|---|---|---|
| `items.retired_at` | `_add_column_if_not_exists(cursor, "items", "retired_at", "TIMESTAMP")` | `ALTER TABLE items ADD COLUMN IF NOT EXISTS retired_at TIMESTAMP` | NULL = in circulation; no backfill (0 items carry the mark) |
| `items.bank_difficulty` | `_add_column_if_not_exists(cursor, "items", "bank_difficulty", "INTEGER")` | `ALTER TABLE items ADD COLUMN IF NOT EXISTS bank_difficulty INTEGER` | NULL until the first sync after the migration fills it (O-IL6); the migration reads no bank file |
| `item_difficulty_changes` | `id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT NOT NULL, previous_difficulty REAL NOT NULL, new_difficulty REAL NOT NULL, source TEXT NOT NULL CHECK (source IN ('sync','bank','dstar')), detail TEXT, changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | `id SERIAL PRIMARY KEY`, the same columns with `DOUBLE PRECISION` for the two difficulties | new, empty |
| index | `CREATE INDEX IF NOT EXISTS idx_item_difficulty_changes_item ON item_difficulty_changes(item_id)` | same | — |

- `bank_difficulty` is `INTEGER` on both (V makes every bank difficulty a JSON integer, FR-010).
  `TIMESTAMP`, `INTEGER`, `REAL`/`DOUBLE PRECISION` fall in the same family on both engines
  (`engine_differences.py::type_family`), so **no `engine_differences.py` entry** is needed; if
  review chooses a type of another family (e.g. a boolean `retired` instead of `retired_at`), it
  becomes an entry with its reason, as `student_course_topic_elo.approximate` is.
- No foreign key from `item_difficulty_changes.item_id` to `items` (items are never deleted, and
  SQLite does not enforce foreign keys here); no index on `retired_at` (2,031 rows, read by course).
- `SCHEMA_VERSION` = **the next free version on `redesign` when the code PR is rebased for merge**:
  **8 if spec 004 E3 (PR #73) has merged by then** (it holds 7), **7 if it has not** (E3 then
  rebases to 8). The code PR reads `SCHEMA_VERSION` on `redesign`, adds 1, extends the comment
  line («N: spec 008 L (items.retired_at, items.bank_difficulty, item_difficulty_changes)»),
  records the new `MIGRATION_SOURCES_DIGEST` (`test_spec002_schema_version.py` fails otherwise),
  and, if another bump lands while it is open, rebases and takes the next number again. Never two
  PRs with the same number on `redesign`.

### The sync (FR-030, FR-031, FR-033; both engines, identical behaviour)

Per bank item, in the sync's existing transaction:

1. **New id** → inserted with `difficulty = bank_difficulty = <bank value>`, RD 350,
   `retired_at = CURRENT_TIMESTAMP` if `retired` is true, else NULL (O-IL13).
2. **Existing id, retirement**: `retired` true and `retired_at` NULL → `retired_at =
   CURRENT_TIMESTAMP`; true and already set → kept (the first retirement time); absent or `false`
   and set → NULL (FR-033).
3. **Existing id, difficulty**:
   - `bank_difficulty` equals the bank value → `difficulty` untouched (the calibration stays);
   - it differs (not NULL) → `difficulty = bank_difficulty = <bank value>`, and a row
     `('sync', previous, new)` in `item_difficulty_changes` (O-IL8); RD untouched (O-IL11); an edit
     equal to the stored difficulty records nothing (spec § Edge Cases);
   - it is NULL (first sync after the migration) → per O-IL6 (recommended: `bank_difficulty =
     <bank value>`, `difficulty` untouched, nothing recorded).
4. Static columns as today. On PostgreSQL the «unchanged bank writes no row» comparison extends to
   `retired` (as a flag) and `bank_difficulty`, so an unchanged item is still not rewritten.

The first sync after the migration is forced by O-IL7 (recommended: a constant
`BANK_SYNC_FORMAT = 2` in `schema_version.py`, hashed into `bank_fingerprint`, so every database
resyncs exactly once after L's deploy; a later bump is the same tool for any future sync change).

### Serving reads (FR-030, O-IL1)

`get_items_from_db` adds `AND retired_at IS NULL` to its four queries, on both engines; its
signature and its return shape do not change, so no caller and no protocol changes.
`get_course_blocks` adds the same condition. **Nothing else filters**: `get_item_by_id`, every
history join and every report keep retired rows (O-IL2). A text guard (tasks-l.md T008) fails if `retired_at
IS NULL` appears in any other repository method, so a history read cannot start hiding retired
items by accident.

Consequences, by surface:
- **Practice**: never selected; an answer to an item served before its retirement (the sync runs
  at deploy, so seconds of overlap) is accepted as served (O-IL2).
- **New exam** (standard, diagnostic): never drawn. **Template exam** containing a retired item:
  start refused with today's 409 (O-IL3); the teacher duplicates the template without it (spec 006
  N5); a retired id is refused when creating or editing a template (today's 400).
- **Started exam**: graded as served — `get_item_by_id` still returns the item (spec § Edge Cases;
  FR-024 is untouched and still covers an item that no longer exists).
- **PvP**: never drawn into a new match, nor used by M's «fill with seen items»; a match in progress
  keeps its items (they live in the match).
- **KatIA, procedures, history, stats, exports, teacher views**: unchanged; a retired item renders
  as before (its row, attempts and ratings stay — US4-AS1).

### The recalibration script (FR-032, N2)

`scripts/recalibrate_items.py` (O-IL10), built on `scripts/repairs/_repair.py::_repository()`
(`RUN_MIGRATIONS=0`, MIGRATION_DATABASE_URL/DATABASE_URL or local SQLite):

- `--method dstar` (default): for every item **not retired** with at least 10 valid attempts
  (`monthly_metrics.py`'s threshold), the domain computes the difficulty that makes the expected
  score match the observed one (O-IL9), clamped to 400–2000 (FR-010) and rounded to an integer; a
  change is planned when it differs from the stored difficulty by ≥ 25.
- `--method bank`: for every item whose stored difficulty differs from its `bank_difficulty`, plans
  the bank value (the tool O-IL6 relies on for DIAN/SENA).
- `--course <id>` (repeatable) narrows both. Default run: prints counts — items examined, planned
  changes per course, mean and largest |Δ| — and writes nothing. `--apply`: writes.
- **Apply**, in one transaction per item batch: lock the item (PostgreSQL `SELECT … FOR UPDATE`;
  SQLite `BEGIN IMMEDIATE`), re-read `difficulty`; if an answer moved it since the plan, skip it
  and count it; else `UPDATE items SET difficulty = ?` and insert `(item_id, previous, new, source,
  detail)` with `source` `dstar` or `bank` and `detail` the attempts and successes used (dstar).
  Prints counts only.
- Repository methods (both engines, identical signatures, `@_read_only` on the read only):
  `get_item_calibration_rows(course_ids=None) -> list[dict]` — raw rows of valid attempts
  (`item_id, course_id, difficulty, bank_difficulty, retired_at, elo_before, is_correct`), no
  aggregation in SQL; `apply_item_difficulty_changes(changes, source) -> dict` — the locked write
  and audit above, returning `{"applied": n, "skipped_moved": m}`.
- Domain: `src/domain/elo/model.py::dstar(ratings, successes) -> float` — the D with
  `Σ expected_score(r, D) = successes` (bisection over D ∈ [400, 2000]; for one rating R and a
  success share P\* it equals AGENTS' `R + 400·log10((1 − P*)/P*)`) — and
  `src/domain/bank/recalibration.py::plan_recalibration(rows, method, min_attempts=10, min_change=25)`,
  which smooths the success count toward ½ (`successes + ½` of `n + 1`) so 0 % and 100 % stay
  finite, clamps, rounds and skips retired items.

### Tests (written first; Phase 2 of tasks-l.md)

All integration tests run on both engines (`tests/integration/conftest.py::repo`). New files:
`tests/integration/test_spec008_l_item_life.py`, `tests/integration/test_spec008_l_recalibration.py`,
`tests/api/test_spec008_l_serving.py`, `tests/unit/domain/test_spec008_l_recalibration.py`.

| Test | Proves | Before L |
|---|---|---|
| `test_spec008_l_item_life.py::test_spec008_l_a_retired_item_is_stamped_and_kept` (sync a bank with the mark: row present, `retired_at` set, kept on a resync; attempts and rating rows unchanged) | FR-030, US4-AS1 | fails (no column) |
| `…::test_spec008_l_practice_never_serves_a_retired_item` (`get_items_from_db` and `get_next_question` over a course with one retired item) | FR-030, US4-AS1 | fails |
| `…::test_spec008_l_block_counts_skip_retired_items` | FR-030 | fails |
| `…::test_spec008_l_history_keeps_a_retired_item` (`get_item_by_id`, attempts joined with items, exam history) | US4-AS1 | passes (pin, Phase 1) |
| `…::test_spec008_l_removing_the_mark_serves_it_again` (mark removed; mark `false`) | FR-033 | fails |
| `…::test_spec008_l_an_edited_bank_difficulty_wins` (900 inserted, answered to 1234, bank 700 → 700; one `sync` change recorded) | FR-031, US4-AS2 | fails |
| `…::test_spec008_l_an_untouched_bank_difficulty_keeps_the_calibration` (bank 900 unchanged, 1234 stays after a forced resync) | FR-031, US4-AS2 | passes (pin, Phase 1) |
| `…::test_spec008_l_an_edit_equal_to_the_stored_difficulty_changes_nothing` (no difficulty change, no audit row) | FR-031 (edge) | fails (no audit table) |
| `…::test_spec008_l_the_first_sync_after_the_migration_keeps_every_difficulty` (NULL `bank_difficulty`, per O-IL6) | FR-031 | fails |
| `…::test_spec008_l_the_upgrade_forces_one_sync` (per O-IL7) | FR-031 | fails |
| `…::test_spec008_l_no_item_row_is_ever_deleted` (no `DELETE FROM items` in either repository; a bank without an id leaves its row) | FR-030 | passes (pin) |
| `test_spec008_l_serving.py::test_spec008_l_new_exams_and_the_diagnostic_skip_a_retired_item` | FR-030, US4-AS1 | fails |
| `…::test_spec008_l_a_template_with_a_retired_item_is_refused` (start 409; create/patch 400) | FR-030 (O-IL3) | fails |
| `…::test_spec008_l_a_started_exam_grades_an_item_retired_since` | FR-030 (edge) | passes (pin) |
| `…::test_spec008_l_pvp_never_draws_a_retired_item` (a course with 11 items, one retired: the match's 10 exclude it) | FR-030, US4-AS1 | fails |
| `…::test_spec008_l_an_answer_to_an_item_retired_after_serving_is_accepted` (O-IL2) | FR-030 (edge) | passes (pin) |
| `tests/unit/test_architecture_layers.py::test_spec008_l_only_serving_reads_filter_retired_items` | FR-030, II | fails (no filter anywhere) |
| `test_spec008_l_recalibration.py::test_spec008_l_a_dry_run_counts_and_writes_nothing` | FR-032, US4-AS3 | fails (no script) |
| `…::test_spec008_l_apply_records_every_change` (item, previous, new, source, time) | FR-032, US4-AS3 | fails |
| `…::test_spec008_l_an_item_moved_since_the_plan_is_skipped` | FR-032 | fails |
| `…::test_spec008_l_the_script_migrates_nothing` (`RUN_MIGRATIONS=0`; no bank sync) | FR-032, VI | fails |
| `tests/unit/domain/test_spec008_l_recalibration.py::test_spec008_l_dstar_inverts_the_expected_score` (and AGENTS' examples: P\*=0.25 → R+191, 0.10 → R+382 for one rating) | FR-032 | fails |
| `…::test_spec008_l_the_plan_skips_retired_few_attempts_and_small_changes` (and clamps to 400–2000) | FR-032 | fails |
| `tests/unit/scripts/test_validate_bank.py::test_spec008_l_retired_must_be_a_boolean` | FR-030 | fails |
| `…::test_spec008_l_retired_items_do_not_count_for_a_small_topic` | FR-030 (O-IL12) | fails |
| `…::test_spec008_l_a_manifest_id_missing_from_the_bank_names_the_retired_mark` | FR-030 (O-IL5) | fails (V's message) |
| `…::test_spec008_l_an_unretired_item_keeps_its_manifest_binding` (un-retired with another topic fails) | FR-033 | passes once V is merged (pin) |
| `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_l_the_generator_carries_the_retired_mark` | FR-030 | fails |
| `tests/unit/infrastructure/test_spec002_schema_version.py` (existing: new version and digest) | schema | fails until the migration lands |

## Owner decisions (owner, 2026-10-27: the recommended option of each)

With O-IL4 the owner approves the proposed FR-034 (§ Spec notes); the PR that closes L adds it with
its Traceability row and amends FR-007 (a third, audited writer), and records O-IL6 in the spec's
Edge Cases.

**DIAN and SENA after L (owner, 2026-10-27):** once L is in production, the 454 bank values
production never received (DIAN +281, SENA +200) are applied with `recalibrate_items.py --method
bank --course DIAN --course SENA`: counted first, reviewed, then `--apply` (audited).

| # | Question | Decided (owner, 2026-10-27) | Alternatives (rejected) |
|---|---|---|---|
| **O-IL1** | Where is «not retired» enforced? | In `get_items_from_db` (and `get_course_blocks`), both engines: the one read every serving path already shares — practice, standard exam, diagnostic, template start, teacher catalogue and template checks, course map, PvP (today and after spec 007 M). No signature change | A parameter `include_retired=False` on `get_items_from_db` (teacher catalogue could show retired items marked); or a filter in each caller (seven places, one forgotten = a leak) |
| **O-IL2** | An item retired after it was served (practice answer in flight, KatIA conversation open, procedure upload, started exam) | **Accepted as served**: `get_item_by_id` is unchanged, so the answer counts and moves ratings as any other; the overlap is the seconds of a deploy | Practice `/answer` refuses a retired item with 409 (the student loses an answer they gave in good faith; the exam half stays «graded as served», spec § Edge Cases) |
| **O-IL3** | A teacher's template that contains a retired item | **Start refused with today's 409** («La plantilla contiene preguntas que ya no están disponibles»); the teacher duplicates it without the item (spec 006 N5). No new code | Start with the remaining items (the teacher's exam changes silently, and two students may get different exams); or mark retired items in the teacher's template view (frontend work, a later delivery) |
| **O-IL4** | **Orphan rows** — items in a database but in no bank file: the 25 `albS*` and the `algebra_semillero` course in databases loaded from older banks (survey B8, second half) | A repair `scripts/repairs/retire_orphan_items.py` (counts by default, `--apply` stamps `retired_at`, prints counts), run by the owner after L's deploy, as T's merge was; the start never retires anything on its own (spec 002 FR-018). **Needs a spec line** (§ Spec notes) | The sync retires every row absent from a fully parsed bank (an unparsable file would retire its whole course at the next start); or leave orphans served (B8 stays half open) |
| **O-IL5** | V's O-V6 after L: a manifest id missing from the bank | **Stays an error**; the message points to `"retired": true`. Leaving the JSON is not a way out of circulation | Removal allowed and read as an implicit retirement by the sync (needs the sync to read the manifest; content needed to un-retire would be gone) |
| **O-IL6** | The first sync after the migration (`bank_difficulty` NULL): what happens to `difficulty`? | **Record, keep**: `bank_difficulty = <bank value>`, `difficulty` untouched on every item (no calibration discarded at start). The 454 DIAN/SENA values that `main`'s production never received are applied, if the owner wants them, by `recalibrate_items.py --method bank --course DIAN --course SENA` (count first, then `--apply`, audited) | **Bank wins once** (every item takes the bank value: applies DIAN +281 and SENA +200, discards every usage calibration); **only unanswered items take the bank value** (no valid attempt ⇒ never calibrated ⇒ the difference is a lost edit; answered DIAN items would stay ~281 below their siblings); a committed baseline of `main`'s values as the «last synced» value (faithful to D3 for production, one more file to keep) |
| **O-IL7** | How the first sync after the migration is forced (the migration changes no bank file) | `BANK_SYNC_FORMAT = 2` in `schema_version.py`, hashed into `bank_fingerprint`: every database resyncs exactly once | Sync whenever an item in circulation has `bank_difficulty` NULL (one query per start; an orphan row would resync forever unless O-IL4 retires it) |
| **O-IL8** | Does the sync's «bank wins» also go into `item_difficulty_changes`? | **Yes**, source `sync`: one table explains every difficulty change that is not an answer (answers are in `attempts`) | Only the script's changes (FR-032's literal scope); a bank edit is then visible only in git |
| **O-IL9** | How `dstar` recalibrates | Maximum likelihood: the D with `Σ expected_score(elo_before_i, D)` equal to the successes smoothed toward ½ (bisection, D ∈ [400, 2000]), items not retired with ≥ 10 valid attempts, rounded, changed when \|Δ\| ≥ 25 | AGENTS' closed form `R̄ + 400·log10((1 − s)/s)` with R̄ the mean `elo_before` and s the smoothed success rate (simpler; biased when ratings are spread); or a manual list (`--from-file id,difficulty`) only |
| **O-IL10** | Script home and output | `scripts/recalibrate_items.py` (it is a tool, not a one-off repair), reusing `_repair._repository()`; counts per course and source, no student data; `--method {dstar,bank}`, `--course` | Under `scripts/repairs/` with the other count-first tools; or a teacher/admin endpoint (out of scope: needs auth and UI) |
| **O-IL11** | Item RD when a bank edit or a recalibration sets the difficulty | **Unchanged** (it is 350 for every item today: nothing moves it, survey B9) | Reset to 350 (no effect today; matters only if item RD ever moves) |
| **O-IL12** | `retired` in the validator | A JSON boolean, else an error; a retired item is validated in full; FR-043's small-topic count excludes retired items (a topic of 5 where 3 are retired rests on 2) | Count retired items too (warning blind to retirements); or forbid `"retired": false` (FR-033 allows it) |
| **O-IL13** | A **new** id that arrives already retired; the retirement time on later syncs | Inserted with `retired_at` set (one rule for every id in the bank); the first `retired_at` is kept while the mark stays | Not inserted until un-retired (then `retired_at` would not record a retirement that never served) |

Not an open decision (recorded): never a `DELETE` of an item (D2); the bank edit wins (D3); the audit
is a database table on both engines (N2); un-retiring is allowed (N3); a moved item is a new id and
a retired old one (D4).

## Bank data and the transfer (flag for the session that owns the transfer)

- **L needs no bank edit.** 0 items carry the mark today. But the deploy **changes the bank
  fingerprint** (O-IL7), so every database resyncs once at the first start after L.
- **`SCHEMA_VERSION` changes (7 or 8).** `docs/transfer.md` § 5 (lines 384-387) requires the backup
  and the rehearsal (`scripts/rehearse_migration.py`) to be repeated on the commit being switched
  whenever `SCHEMA_VERSION` changed since the last rehearsal, and its version table (line 382) needs
  L's row. **L's code PR does not touch `docs/transfer.md`**; the transfer session adds the row and
  repeats the rehearsal if L lands before the production switch.
- **Production difficulties.** Production was synced from `main`, whose DIAN items are 281 and SENA
  items 200 below `redesign`'s. With O-IL6 recommended, the switch keeps `main`'s (calibrated)
  values and records `redesign`'s as `bank_difficulty`; the rescale reaches production only by the
  owner's `recalibrate_items.py --method bank` run. With O-IL6 «bank wins once», the switch
  overwrites every calibrated difficulty in production. Either way this is a transfer-visible change
  the transfer session should know before it rehearses.
- **Orphans.** The 25 `albS*` items (and the `algebra_semillero` course) are in production's
  database if it loaded them; O-IL4's repair is the owner's post-deploy step, after its count-only
  run on the rehearsal copy.

## Files the code PR touches (shared)

| File | Change | Shared with |
|---|---|---|
| `src/infrastructure/persistence/sqlite_repository.py`, `postgres_repository.py` | `_add_item_life`; `_run_migration` calls it; the sync (retired, bank difficulty, audit); `get_items_from_db`, `get_course_blocks` filter; `get_item_calibration_rows`, `apply_item_difficulty_changes` | every spec (R1); C rewrites the same sync's course lines first |
| `src/infrastructure/persistence/schema_version.py` | `SCHEMA_VERSION` next free (9 if I1 lands first), comment, `MIGRATION_SOURCES_DIGEST`, `_MIGRATION_METHODS` + `_add_item_life`, `BANK_SYNC_FORMAT` in `bank_fingerprint` (O-IL7) | spec 002 (mechanics), spec 004 E3 (version 7), C (fingerprint input) |
| `src/infrastructure/persistence/engine_differences.py` | **nothing** with the recommended types; an entry only if review picks types of different families | spec 002 |
| `src/application/interfaces/repositories.py` | nothing (`get_items_from_db` unchanged; the script's methods are not a service's) | — |
| `src/domain/elo/model.py` | `dstar` | spec 001 |
| `src/domain/bank/recalibration.py` | new (beside V's `rules.py`, C's `catalogue.py`) | V, C |
| `scripts/recalibrate_items.py`; `scripts/repairs/retire_orphan_items.py` (O-IL4) | new | — |
| `scripts/validate_bank.py` | `retired` boolean, FR-043 count, O-V6 message | V, C |
| `scripts/build_epa8_bank.py` | `CAMPOS_BANCO` + `retired` | V (`--check`) |
| `src/domain/selector/item_selector.py` | **nothing**: its pool comes from `get_items_from_db` | spec 001 |
| `api/routers/student.py`, `api/routers/teacher.py`, `api/websocket/pvp.py` | **nothing** with O-IL1/O-IL2/O-IL3 as recommended (they read `get_items_from_db`) | specs 001, 006, 007 (M changes `_form_match`'s choice, not its read) |
| `tests/…` (four new files, additions to `test_validate_bank.py`, `test_build_epa8_bank.py`, `test_architecture_layers.py`; `test_spec002_schema_version.py` digest) | new tests | deliveries A, T, V |
| `AGENTS.md` | § Item bank: `retired`, «never delete an item from the JSON», the bank-wins rule, `recalibrate_items.py` replacing «recalibrate or retire»; § Database: `items.retired_at`, `bank_difficulty`, `item_difficulty_changes` rows; R15's writer table is unaffected (ratings), the item-difficulty writers sentence gains the sync and the script | every session |
| `scripts/monthly_metrics.py` | its «Recalibrar o retirar» line names the script and the mark | — |
| `docs/sdd/roadmap.md` | M8 status line | every session |
| `specs/008-item-bank/spec.md` | § Traceability L rows, L `closed`; Code Scope entries for the new script(s) and module | — |

**Not touched**: `docs/transfer.md`, `scripts/migrate.py`, `scripts/rehearse_migration.py`,
`render.yaml`, `frontend/` — the transfer is flagged above, not edited.

## Spec notes for the owner (no change made here)

- **FR-007 vs FR-032.** FR-007 [AS-IS] says the repositories offer no item-difficulty update
  besides the bank sync and the answer transaction; FR-032's `--apply` is a third writer
  (`apply_item_difficulty_changes`). FR-007 needs «… and the audited recalibration (FR-032)» in the
  PR that closes L (the pinned test checks only two retired names, so it stays green either way).
- **FR-031 does not say what the first sync does** when no bank value was ever recorded (every
  existing row). O-IL6 decides it; the spec could record the decision in its Edge Cases.
- **Orphans (O-IL4).** US4's «Why» names «dropping it from the JSON leaves it served», but FR-030
  only covers the mark. Retiring rows that are in no bank file needs a requirement (proposed
  **FR-034** [CHANGE]: «The system shall offer a repair that counts, and with `--apply` retires,
  the items stored in the database that no bank file carries») and a Traceability row; without it,
  the repair is out of the spec and B8's second half stays open.
- **«Practice, new exams and PvP»** (FR-030, SC-001) does not name the diagnostic, the teacher's
  catalogue and templates, the course map or the block counts; O-IL1 covers them all through one
  read. No text change is needed if the owner reads «exams» to include the diagnostic.
- **Code Scope** lacks `scripts/recalibrate_items.py`, `src/domain/bank/recalibration.py`,
  `src/domain/elo/model.py` (dstar) and the PvP/exam routers L relies on (read only, no change). The
  code PR adds the files it creates once they exist.

## Risks and rollout

- **Order.** V (manifest; O-V6) and C (catalogue; the sync's course lines) merge first; L rebases on
  both. Spec 004 E3 decides L's version number (§ Schema).
- **One resync** at the first start after the deploy (O-IL7). On PostgreSQL it rewrites every item
  once (to fill `bank_difficulty`); afterwards an unchanged bank writes nothing, as today.
- **No calibration lost at start** with O-IL6 recommended; the price is that a bank edit made
  before L (the DIAN/SENA rescale) reaches an existing database only through the owner's audited
  script.
- **A topic whose items are all retired** keeps its rating row, which keeps counting in the course
  rating (R15), as D4's moved items do; nothing can move it again. Review watches for it; the
  validator's small-topic warning (O-IL12) names such a topic.
- **No deploy by an agent; no script run against production by an agent.**
