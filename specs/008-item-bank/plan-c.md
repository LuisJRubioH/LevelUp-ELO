# Plan — spec 008, delivery C: one course catalogue (D5)

**Spec**: [spec.md](spec.md) § Deliveries, C (US3; FR-020, FR-021) · **Branch**: `008-c`, from
`redesign` **after V is merged** · **Date**: 2026-10-21 · **Status**: draft for the owner's approval
(decisions O-C1 … O-C9 open)

## Summary

The block and display name of every course are written twice — `_COURSE_BLOCK_MAP` and
`_COURSE_NAME_MAP` as class attributes of **both** repositories — and the validator reads the block
map by parsing the repositories' source with `ast`. Ten courses have no name in the map and take
the `topic` of their first item, so reordering a file renames its course (survey B14). C puts block
and name in **one catalogue module**, read by both repositories, the validator and the bank
fingerprint; semillero courses get their block and grade from the file name
(`items/bank/semillero/<subject>_semillero_<g>.json`) instead of 36 map entries; and the validator
fails on a course without an explicit name.

Recommended outcome: **no schema change, no stored course row changes** (every course keeps today's
block and name), and **one resync** of the bank at the first start after the deploy, because the
fingerprint's input changes shape (§ Bank fingerprint).

## Constitution Check (1.2.0)

| Principle | C |
|---|---|
| Spec is the contract (I) | FR-020, FR-021 are `[CHANGE]`; each and US3-AS1, US3-AS2 get tests that fail on today's code (tasks-c.md Phase 2). C rewires code that delivery A pinned (FR-001, FR-003, FR-004, FR-005): those pins run green on the unchanged code first (Phase 1) and only their fixtures change |
| One source of truth (II) | this delivery **is** principle II for courses: one module holds block and name (SC-003); the repositories, the validator, `db_sync_check.py` and the fingerprint read it; the semillero grade rule lives in one function (O-C8) |
| Layers (III, R2) | the catalogue is data plus pure functions over a course id and a relative path — no file reads, no SQL. Recommended home `src/domain/bank/catalogue.py`, beside V's `src/domain/bank/rules.py` (O-V2), standard library only, under the existing guard `tests/unit/test_architecture_layers.py::test_domain_stays_free_of_io_and_ml_dependencies` (O-C1). The repositories import it (infrastructure → domain is allowed); the validator imports it as it will import V's rules |
| Dual database (IV, R1, R8) | the course upsert of `sync_items_from_bank_folder` changes identically on both engines (both read the catalogue); public signatures do not change; no migration, no `SCHEMA_VERSION` change, `MIGRATION_SOURCES_DIGEST` untouched (none of `_MIGRATION_METHODS` changes); `db_sync_check.py` section 2 is rewritten to check the new rule (O-C9) |
| Learning measurement (V, R15) | ratings are keyed by (course, topic); C changes no course id and no topic, so no rating row moves. Block and name are display and catalogue data |
| Simplicity (VII) | no new dependency; the «Banco de preguntas» CI job still installs nothing (the catalogue is standard library) |
| Production (VI) | nothing runs against a database; the one resync happens at the owner's deploy; the transfer is flagged, not touched (§ The transfer) |

## Measured facts (`redesign @ 9177907`, 2026-10-21)

**The two maps.** `_COURSE_BLOCK_MAP` (S:4211-4268, P:152-207) has **50 entries**;
`_COURSE_NAME_MAP` (S:4270-4310, P:209-249) has **39**. Both are **identical between the
repositories**, keys and values and order (compared as Python objects). Every name-map key is in
the block map. `db_sync_check.py` (`check_course_map`, lines 240-259) compares only the block maps,
by regex; nothing compares the name maps (they agree today by care, not by check).

**Courses.** 49 bank files (13 top-level, 36 in `semillero/`) → 49 courses: Semillero 36,
Universidad 6, Colegio 5, Concursos 2. Every file has a block entry. **One block entry has no
file**: `aritmetica` (Colegio) — the survey's B14; no database built from the bank has an
`aritmetica` course row, since the sync creates courses only from files.

**Names.** 39 courses are named in the map: DIAN, SENA, `evaluar_para_avanzar_8` and the 36
semillero courses. **10 take their first item's `topic`**:

| Course | Block | Name today (first item's topic) | Items |
|---|---|---|---:|
| `algebra_basica` | Colegio | Álgebra Básica | 103 |
| `aritmetica_basica` | Colegio | Aritmética Básica | 103 |
| `geometria` | Colegio | Geometría | 3 |
| `trigonometria` | Colegio | Trigonometría | 103 |
| `algebra_lineal` | Universidad | Álgebra Lineal | 120 |
| `calculo_diferencial` | Universidad | Cálculo Diferencial | 120 |
| `calculo_integral` | Universidad | Cálculo Integral | 120 |
| `calculo_varias_variables` | Universidad | Cálculo de Varias Variables | 120 |
| `ecuaciones_diferenciales` | Universidad | Ecuaciones Diferenciales Ordinarias | 100 |
| `probabilidad` | Universidad | Probabilidad | 100 |

A fresh local SQLite bootstrap stores exactly these 49 `(id, name, block)` rows.

**Semillero.** All 36 files match `<subject>_semillero_<g>` with **6 subjects** (`algebra`,
`aritmetica`, `conteo_combinatoria`, `geometria`, `logica`, `probabilidad`) × **grades 6–11**, six
per grade. Every one of the 36 names is `«<Subject> Semillero <g>°»` with one label per subject
(Álgebra, Aritmética, Conteo y Combinatoria, Geometría, Lógica, Probabilidad) — so the 36 entries of
each map are derivable from a 6-entry subject table with **no change of any name**.

**Where the grade lives.** The grade is **not stored**: the `courses` table has `id`, `name`,
`block` (CHECK over the four blocks) and `description` (`"Curso de {name}"`) on both engines
(S:740, P:1008). The grade is read from the id suffix in three places: the domain rule
`src/domain/entities.py::in_catalogue` (`course_id.endswith(f"_semillero_{grade}")`, spec 001
FR-028k) and the SQL `c.id LIKE '%semillero_{grade}'` in `get_teachers_with_groups_and_courses`
(S:3345, P:3853). The frontend parses no course id (`Teacher/Groups.tsx:467` ranks blocks by a
`Semillero N` pattern no stored block has; harmless, out of scope).

**The sync.** Both engines resolve a course as
`name = _COURSE_NAME_MAP.get(id) or items[0]["topic"]`, `block = _COURSE_BLOCK_MAP.get(id,
"Universidad")` (S:4365-4368, P:4855-4858), insert a new course and rename or move an existing one
whose name or block differs (spec 002 N1). **Nothing deletes a course.**

**The bank fingerprint.** `bank_fingerprint(BANK_DIR, {"block": _COURSE_BLOCK_MAP, "name":
_COURSE_NAME_MAP})` (S:100-102, P:362-364; `schema_version.py:86-99`) hashes the two maps as JSON
(sorted keys) and then every bank file. Today: `3ea461a8…bddd`. Any change to what is hashed — even
an equivalent catalogue that drops `aritmetica` and names the ten courses with their current names —
gives another value (measured: `e200735b…5d5c`), so **the next start resyncs once**. That resync
rewrites no course row when the catalogue keeps today's names and blocks (the upsert compares
`(name, block)`), PostgreSQL updates no item (it updates only rows whose static columns changed),
SQLite rewrites each item with the same values, and `bank_syncs` gains one row.

**The validator.** `scripts/validate_bank.py::course_block_maps` (lines 98-111) parses both
repositories' source with `ast` and requires each file's course in both block maps (lines 284-292);
it checks no name. The CI bank job installs only pytest, which is why it parses instead of
importing; `src/__init__.py`, `src/domain/__init__.py` are empty, so importing a standard-library
module under `src/domain/` works there.

**Tests that reach into the maps** (fixtures only, see tasks-c.md T011):
`tests/integration/test_spec002_d1_startup.py::test_spec002_d1_a_changed_course_map_resyncs_the_bank`
(FR-005 pin) and `tests/integration/test_spec002_d3_parity.py` monkeypatch the repositories' maps;
`tests/integration/test_sqlite_bank_sync_failure.py` (FR-003 pin) puts a typo block in the map;
`tests/unit/scripts/test_validate_bank.py::test_a_course_missing_from_the_course_map_is_an_error`
(US1-AS1, FR-001) asserts the text `_COURSE_BLOCK_MAP`, and `::test_the_course_map_is_read_from_both_repositories`
(FR-001) reads the repositories' maps. Four integration files sync temporary banks whose course is
in no map and rely on the «Universidad» fallback: `test_spec002_d3_parity.py`,
`test_sqlite_bank_sync_failure.py`, `test_bank_duplicate_id.py` (FR-004 pin),
`test_spec008_t_topics.py`. `tests/unit/scripts/test_spec002_d3_db_sync_check.py::test_the_repositories_pass`
runs the whole `db_sync_check.py`, whose section 2 requires the maps to exist.

## Design

### The catalogue module (FR-020, FR-021)

`src/domain/bank/catalogue.py` (O-C1), standard library only:

- `COURSES: dict[str, tuple[str, str]]` — course id → (block, name), **one explicit entry per
  non-semillero course** (13 today: the 10 of the table above with today's names per O-C2, plus
  DIAN, SENA, `evaluar_para_avanzar_8`). `aritmetica` is not carried over (O-C6).
- `SEMILLERO_SUBJECTS: dict[str, str]` — subject → label (6 entries), and `SEMILLERO_GRADES` reused
  from `src/domain/entities.py` (6–11).
- `semillero_grade(course_id) -> str | None` — the grade of a `<subject>_semillero_<g>` id with a
  known subject and a grade in 6–11, else `None`.
- `course_entry(course_id, relative_path) -> CourseEntry | None` — `(block, name, grade)`:
  for a file under `semillero/`, block «Semillero», grade *g*, name `«<label> Semillero <g>°»`
  (O-C3, O-C4); otherwise the `COURSES` entry with `grade=None`; `None` when the course is unknown.
- `catalogue_problems(bank_paths) -> list[str]` — for the validator: a file whose course has no
  entry or no explicit name, a semillero file whose name gives no subject or grade, a top-level file
  named like a semillero course (O-C4), and a catalogue entry with no file (O-C6). Each message
  names the file or course and `src/domain/bank/catalogue.py`.
- `fingerprint_view(course_ids) -> dict` — `{course_id: [block, name]}` for the courses of the bank,
  what the fingerprint hashes (O-C7).

The four values of `block` stay `COURSE_BLOCKS` (`src/domain/entities.py`); a test checks every
catalogue block is one of them, so a typo fails in CI instead of at the `courses` CHECK.

### Both repositories (FR-020, R1)

- Delete `_COURSE_BLOCK_MAP` and `_COURSE_NAME_MAP` from both classes.
- `sync_items_from_bank_folder` (both): `entry = course_entry(course_id, relpath)`; name and block
  come from it; the first item's `topic` is **never** a course name again. An unknown course
  (`entry is None`, a bank that bypassed CI) is handled per O-C5 (recommended: skipped with an error
  log naming the file, as an unparsable file is). The upsert itself (insert, or update when name or
  block differ) is unchanged.
- `_sync_bank_if_changed` (both): `bank_fingerprint(BANK_DIR, fingerprint_view(...))` (O-C7).
- No other method changes; public signatures stay the same (`db_sync_check.py` section 1).

### The validator (FR-020, FR-021)

`course_block_maps()` and its `ast` parsing are removed; `main()` calls `catalogue_problems` with
every bank file's path relative to `items/bank/` and reports each as an error. It composes with V:
V's `src/domain/bank/rules.py` and manifest check stay as they are; both modules are imported the
same way.

### The semillero grade (FR-021, O-C8)

Recommended: `in_catalogue` asks `semillero_grade(course_id) == str(grade)` instead of its own
`endswith`, so one function owns the rule. The two `LIKE '%semillero_{grade}'` queries stay (they
read stored rows; replacing them is a separate change).

### `db_sync_check.py` (O-C9)

Section 2 becomes «Un solo catálogo de cursos»: neither repository source defines
`_COURSE_BLOCK_MAP` or `_COURSE_NAME_MAP`, and both import `src.domain.bank.catalogue`.
`engine_differences.py` needs no entry (no schema difference).

## Bank fingerprint and the resync

Moving the maps into one module **necessarily** changes what the fingerprint hashes (the name data
gains 10 entries and loses `aritmetica` under the spec's «every course named explicitly»), so every
database **resyncs the bank once** at the first start of C. With O-C2 as recommended that resync
changes **no course row and no item value**; it costs one bank pass (seconds) and one `bank_syncs`
row. FR-005 (a catalogue-only change resyncs) keeps holding: its pin changes only how it edits the
catalogue. The alternative that keeps today's hash (O-C7, last option) is listed but not recommended.

## The transfer (owned by another session — flagged, not touched)

- **No `SCHEMA_VERSION` change**, so C does not invalidate a rehearsal's schema coverage
  (`docs/transfer.md` § 5 ties re-rehearsal to `SCHEMA_VERSION`).
- **The fingerprint changes.** A production database from `main` has no `bank_syncs` and syncs at
  its first migration anyway, so C **before** the switch adds nothing to that sync; C **after** the
  switch costs one resync at its own deploy. Either way, with O-C2 as recommended, no course is
  renamed or moved for users.
- **If the owner picks new names (O-C2 alternative)**, the first start after C renames up to 10
  courses on every database, production included; the session that owns the transfer should know
  before the rehearsal, since the rehearsal's course table would differ from one made before C.
- **Unmeasured in production** (agents do not read it): whether production holds course rows with
  no bank file (e.g. `aritmetica`, the old `algebra_semillero`). C never deletes a course, so such
  rows stay as they are.
- `docs/transfer.md`, `ops/*`, `scripts/migrate.py` and `scripts/rehearse_migration.py` are **not
  touched** by C.

## Owner decisions (open)

| # | Question | Recommended | Alternatives |
|---|---|---|---|
| **O-C1** | Where does the catalogue live? | `src/domain/bank/catalogue.py`: pure data and functions, standard library, beside V's `rules.py`; the domain already owns `COURSE_BLOCKS`, `SEMILLERO_GRADES` and `in_catalogue`; the CI bank job imports it with nothing installed | (a) `src/infrastructure/persistence/course_catalogue.py`, beside `course_blocks.py` — the validator would import infrastructure, and `in_catalogue` (domain) could not use its grade rule; (b) a data file `items/courses.json` read by a small loader — editable without Python, but it is I/O (cannot sit in the domain), needs its own schema check, and must be hashed into the fingerprint as a file |
| **O-C2** | The names of the 10 courses that take their first item's topic | Freeze **today's names** (table above) as explicit entries: no stored row changes on any database, no user-visible rename | Curated names chosen by the owner now (e.g. «Ecuaciones Diferenciales» instead of «… Ordinarias»): the first start renames those courses everywhere, production included (flag to the transfer) |
| **O-C3** | A semillero course's name | Derived: `«<label> Semillero <g>°»` from a 6-entry subject table — identical to all 36 names today; «named explicitly» is satisfied per subject, and a new grade or a new file of a known subject needs no entry (US3-AS2) | (a) An explicit name per semillero course (36 entries) — contradicts US3-AS2's «without a map entry»; (b) derived label from the subject slug (`conteo_combinatoria` → «Conteo Combinatoria») — no table, but loses accents and «y» |
| **O-C4** | What makes a file a semillero course | Both its place and its name: a file in `semillero/` must be `<subject>_semillero_<g>` with a known subject and *g* in 6–11, else a validator error; a top-level file named like that is also an error (no ambiguity) | By name only (`*_semillero_<g>` anywhere is semillero); or by folder only (any file in `semillero/`, grade parsed from the suffix) |
| **O-C5** | A course unknown to the catalogue at sync time (a bank that bypassed CI) | **Skip the file** with an error log naming it, as an unparsable file is skipped; never «Universidad» silently. Test fixtures that sync temporary courses register them in the catalogue (tasks T011) | (a) Keep today's fallback («Universidad», name = file stem instead of first topic) with an error log; (b) fail the whole sync and the start |
| **O-C6** | `aritmetica`, in the map with no file | Not carried into the catalogue; the validator fails on a catalogue entry with no bank file, so the catalogue cannot drift from the bank again | Keep it (harmless, unused); or a warning instead of an error for an entry with no file |
| **O-C7** | What the fingerprint hashes | `{course_id: [block, name]}` of the bank's courses, resolved through the catalogue: one resync at C's first start, then a resync exactly when a bank course's block or name changes | (a) The bytes of `catalogue.py` — any edit, even a comment, resyncs; (b) a legacy-compatible projection that rebuilds today's `{"block": …, "name": …}` shape (including `aritmetica` and only the 39 old names) so the hash does not move — avoids one harmless resync at the price of code that exists only for that |
| **O-C8** | Who owns the semillero grade rule | `in_catalogue` (domain) calls `semillero_grade`; the SQL `LIKE` in `get_teachers_with_groups_and_courses` stays | (a) Leave `in_catalogue` as it is (the suffix rule stays in two places); (b) also replace the `LIKE` queries on both engines with catalogue filtering in Python |
| **O-C9** | `db_sync_check.py` section 2 | Rewritten: neither repository defines a course map and both import the catalogue | Remove the section and rely on the unit test of T006 alone |

Not open (recorded): the catalogue holds block and name only — the grade is derived, never stored;
no course row is ever deleted; ratings and course ids do not change.

## Schema

**None.** No column, table or index; `SCHEMA_VERSION` stays (6 on `redesign`; 7 if E3, PR #73,
lands first) and `MIGRATION_SOURCES_DIGEST` is unchanged (no method of `_MIGRATION_METHODS` is
touched). Storing a course's grade or a catalogue table in the database is not proposed; if review
asks for it, it takes the next free version — **8 at the earliest** — under AGENTS § Database.

## Tests (written first)

| Test | Proves | Before C |
|---|---|---|
| `tests/integration/test_spec008_c_courses.py::test_spec008_c_synced_courses_keep_their_block_and_name` (both engines: the 49 `(id, name, block)` rows of the measured table) | FR-020 (no stored row changes; O-C2) | passes (pin) |
| `tests/unit/domain/test_spec008_c_catalogue.py::test_spec008_c_every_bank_course_has_a_block_and_a_name` (real bank; blocks in `COURSE_BLOCKS`) | FR-020, US3-AS1 | fails (module absent) |
| `…::test_spec008_c_a_semillero_file_gives_block_grade_and_name` (6 subjects × 6 grades) | FR-021, US3-AS2 | fails |
| `…::test_spec008_c_a_semillero_name_outside_the_rule_is_refused` (grade 5, 12, unknown subject, top-level `*_semillero_6`) | FR-021 (O-C4) | fails |
| `…::test_spec008_c_the_catalogue_imports_only_the_standard_library` | FR-020 (the bank job installs nothing) | fails |
| `tests/unit/infrastructure/test_spec008_c_one_catalogue.py::test_spec008_c_neither_repository_holds_a_course_map` (both sources: no `_COURSE_BLOCK_MAP` / `_COURSE_NAME_MAP`, both import the catalogue) | FR-020, SC-003 | fails |
| `tests/integration/test_spec008_c_courses.py::test_spec008_c_both_engines_sync_the_catalogues_block_and_name` (a catalogue entry changed → both engines store it; a reordered file does not rename its course) | FR-020, US3-AS1 | fails |
| `…::test_spec008_c_a_semillero_file_syncs_as_its_grade_without_an_entry` (a temporary bank with `semillero/probabilidad_semillero_9.json`, no catalogue entry for it: block «Semillero», name «Probabilidad Semillero 9°», in the grade-9 catalogue and not in grade 8's) | FR-021, US3-AS2 | fails |
| `…::test_spec008_c_an_unknown_course_is_not_synced` (per O-C5) | FR-020 (B14) | fails |
| `tests/unit/scripts/test_validate_bank.py::test_spec008_c_the_validator_reads_the_catalogue` | FR-020, US3-AS1 | fails |
| `…::test_spec008_c_a_course_with_no_explicit_name_fails` | FR-021, US3-AS1 | fails |
| `…::test_spec008_c_a_semillero_file_name_must_give_a_grade` | FR-021, US3-AS2 | fails |
| `…::test_spec008_c_a_catalogue_course_with_no_file_fails` (per O-C6) | FR-020 | fails |
| `tests/unit/infrastructure/test_spec008_c_one_catalogue.py::test_spec008_c_the_fingerprint_hashes_the_catalogue` (per O-C7: a catalogue change for a bank course changes it; an unrelated edit does not) | FR-020 with FR-005 | fails |
| `tests/unit/scripts/test_spec002_d3_db_sync_check.py::test_spec008_c_a_course_map_in_a_repository_fails` (O-C9) | FR-020 | fails |

## Files the code PR touches (shared)

| File | Change | Shared with |
|---|---|---|
| `src/domain/bank/catalogue.py` | new (O-C1) | V (`rules.py`, `__init__.py` beside it) |
| `src/infrastructure/persistence/sqlite_repository.py`, `postgres_repository.py` | maps removed; course upsert and fingerprint read the catalogue (R1, both) | every spec (shared files); L next changes the same sync |
| `src/domain/entities.py` | `in_catalogue` uses `semillero_grade` (O-C8) | spec 001 |
| `scripts/validate_bank.py` | `course_block_maps` removed; `catalogue_problems` | V (manifest, difficulty), L (`retired`) |
| `scripts/db_sync_check.py` | section 2 (O-C9) | spec 002 |
| `src/infrastructure/persistence/engine_differences.py` | nothing expected (no schema difference) | spec 002 |
| `tests/integration/test_spec002_d1_startup.py`, `test_spec002_d3_parity.py`, `test_sqlite_bank_sync_failure.py`, `test_bank_duplicate_id.py`, `test_spec008_t_topics.py`; `tests/unit/scripts/test_validate_bank.py`, `test_spec002_d3_db_sync_check.py` | fixtures edit the catalogue instead of the maps; one assertion text flipped citing FR-020; one test replaced (tasks T011, T012) | spec 002, delivery A and T rows |
| `AGENTS.md` | R1 checklist («Changed `_COURSE_BLOCK_MAP`?» → the catalogue, one place); § Database bootstrap note («both course maps» → the course catalogue); § Item bank «New course» steps | every session |
| `README.md` (line 271, «Nuevo curso») | same steps | — |
| `docs/sdd/roadmap.md` | M8 status line | every session |
| `specs/008-item-bank/spec.md` | C rows, C `closed`, Code Scope, FR-001 wording (§ Spec notes) | — |
| `.github/workflows/ci.yml` | bank job pytest line gains `tests/unit/domain/test_spec008_c_catalogue.py` | every job |

**Not touched**: `docs/transfer.md`, `ops/*`, `scripts/migrate.py`, `scripts/rehearse_migration.py`,
`schema_version.py` (its `bank_fingerprint` signature already takes the course data as an argument),
the frontend, V1's `app.py`. `Implementacion/MAPA_NODOS_ALGEBRA8.md:40` still says «add to
`_COURSE_BLOCK_MAP` of both»; it is a planning note, corrected only if the owner wants.

## Spec notes for the owner (no change made here)

- **FR-001 is an `[AS-IS]` requirement C makes stale.** It says the validator fails on «a file whose
  course is missing from either repository's course map», and its § Traceability row cites
  `test_validate_bank.py::test_the_course_map_is_read_from_both_repositories`, which reads the maps
  FR-020 removes. The code PR needs a spec amendment: FR-001 reads «missing from the course
  catalogue» and that row cites `test_spec008_c_the_validator_reads_the_catalogue`. US1-AS1 («a
  course outside the map») reads correctly either way.
- **FR-021 «every course named explicitly» (D5) vs US3-AS2 «without a map entry».** A semillero
  course cannot have both an explicit entry and none. This plan reads them together as O-C3: each
  subject is named explicitly, each semillero course's name is derived. The owner confirms or
  amends.
- **«for grade *g*» (US3-AS2).** The grade is not stored anywhere; it is derived from the id when a
  catalogue is read. The test checks it through the grade's catalogue (`get_available_courses_by_level`).
- **FR-005 says «a course map».** After C it is the catalogue; the meaning holds and the pin keeps
  its assertions. A wording touch is optional.
- **Code Scope** does not list the catalogue module, `src/domain/entities.py` or
  `scripts/db_sync_check.py`; the code PR adds those it changes (the checker needs each entry to name
  a tracked file, so the module is added once it exists).

## Risks and rollout

- **Order.** V first (it changes `validate_bank.py` and creates `src/domain/bank/`); C rebases on
  it. L after C (both change the sync).
- **One resync** on each database at the first start of C (§ Bank fingerprint); harmless with O-C2
  as recommended.
- **A course that bypassed CI** stops appearing (O-C5 recommended) instead of landing in
  «Universidad»; CI already refuses it, so only a hand-deployed bank is affected.
- **No deploy-visible change** with the recommended options: same courses, same blocks, same
  names, same catalogues per level and grade.
