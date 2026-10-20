# Plan — spec 008, delivery T: topics and subtopics (B19)

**Spec**: [spec.md](spec.md) § Deliveries, T (US5; FR-040 … FR-043) · **Branch**: `008-t`, from
`redesign` · **Date**: 2026-10-20 · **Status**: approved; merge rule A (owner, 2026-10-20)

## Summary

DIAN and EPA8 carry one topic per item, so a topic's rating rests on one answer, the course rating
weighs areas by how many labels they have, and the teacher reads hundreds of one-answer rows. T
makes the coarse label the `topic` (it carries the rating) and keeps the fine label as an optional
`subtopic` (study only). It lands before delivery V commits the id manifest, which then forbids
topic changes (FR-011).

## Constitution Check (1.2.0)

| Principle | T |
|---|---|
| Tests first (I) | every FR and US5 scenario gets a failing test before the change (tasks-t.md Phase 1) |
| Ratings (I, R15) | ratings stay keyed by (course, topic); `subtopic` never keys one; nothing is rebuilt from attempts; the merge of stored fine-topic ratings is a repair script, not a start-up step (spec 002 FR-018) |
| Layers (II, R2) | the subtopic report is read through the application layer; the repositories return raw counts, no rating aggregation (guard `test_spec001_no_rating_aggregation_in_repositories_or_routers`) |
| Dual database (IV, R1, R8) | additive `items.subtopic` on both engines; `SCHEMA_VERSION` + `MIGRATION_SOURCES_DIGEST` raised; `db_sync_check.py` and `test_spec002_d3_parity.py` |
| Production (VI) | no migration or repair is run against production by an agent; the repair counts by default and writes only with `--apply`, run by the owner |

## The regrouping (FR-041)

Rule: `topic` = the text before « — » (EPA8) or « - » (DIAN); `subtopic` = the rest. An item with
no separator keeps its topic and gets no subtopic. Measured on the current bank:

**EPA8** (`items/bank/evaluar_para_avanzar_8.json`): 60 items, **59 topics → 5**.

| Topic | Items |
|---|---:|
| Pensamiento aleatorio | 21 |
| Pensamiento variacional | 12 |
| Pensamiento espacial | 11 |
| Pensamiento métrico | 9 |
| Pensamiento numérico | 7 |

**DIAN** (`items/bank/DIAN.json`): 293 items, **209 topics → 34** by the mechanical rule. 103
items have no separator and already carry a coarse topic. Fifteen topics have 6–22 items
(Constitución Política 22, MIPG 22, Régimen Tributario 21, Gerencia de Proyectos (PMI) 21, Derecho
Administrativo (CPACA) 21, Aprendizaje Continuo 21, Orientación al Ciudadano 21, Trabajo en Equipo
21, Ética 21, Comportamiento Ético 20, PQRSF 19, Régimen Aduanero 14, Gestión Documental 12, Ley de
Transparencia 10, Régimen Cambiario 6). **Nineteen are left with 1–3 items**, mostly variants of
a larger topic:

| Small topic (items) | Proposed coarse topic |
|---|---|
| CPACA (3) | Derecho Administrativo (CPACA) |
| Sistema PQRSF (1), PQRSF y MIPG (1) | PQRSF |
| Comportamiento Ético (Nivel 4) (1) | Comportamiento Ético |
| Régimen Aduanero/Cambiario (1) | Régimen Aduanero |
| Trabajo en Equipo / Transferencia de Conocimiento (1), Trabajo en Equipo / Liderazgo (1), Mejora Continua / Trabajo en Equipo (1) | Trabajo en Equipo |
| Aprendizaje Continuo / Planeación (1) | Aprendizaje Continuo |
| Código de Integridad (1) | Ética |
| Formulación de Proyectos (1), Metodología de Marco Lógico (MML) (1), Gestión de Riesgos (1) | Gerencia de Proyectos (PMI) |
| Derecho Disciplinario (1), Mecanismos de Protección (1) | Constitución Política |
| Compromiso / Toma de Decisiones (1), Responsabilidad / Gestión del Tiempo (1), Gestión del Talento Humano (1), Sistemas de Gestión SG-SST (1) | stay as they are (FR-043 warns) |

With this table DIAN ends with **19 topics**, four of them small (warned, not blocked). The small
topic's old label becomes the item's `subtopic`. **The table is a content proposal**: the owner
may edit it in this plan's review; it is applied as a one-time bank edit (no code reads it).

## Design

- **Bank and validator (FR-040, FR-041, FR-043).** `subtopic` is an optional bank field, non-empty
  text when present (`scripts/validate_bank.py`, checked like `topic`). The validator warns, naming
  the topic, for a course topic with fewer than 5 items (warning, exit 0). The regrouping is a
  one-time edit of `DIAN.json` and `evaluar_para_avanzar_8.json`; `scripts/build_epa8_bank.py` is
  updated to emit `topic`/`subtopic` so its output matches (delivery V will check it in CI, D6).
- **Schema (FR-040).** Additive `items.subtopic TEXT` on both engines (`_run_migration`;
  PostgreSQL `ADD COLUMN IF NOT EXISTS`, SQLite `_add_column_if_not_exists`), the next
  `SCHEMA_VERSION` (5 today; 6 if spec 004 E3, #73, lands first — whichever is next at
  implementation) and a new `MIGRATION_SOURCES_DIGEST`; `docs/transfer.md` version table.
- **Sync (FR-040).** `sync_items_from_bank_folder` writes `subtopic` on both engines (insert and
  the static-columns update). The bank fingerprint changes, so every database resyncs once
  (spec 002 FR-016). Ratings keep reading `items.topic` only (`save_answer_transaction`,
  `RatingReadService`); nothing reads `subtopic` for a rating.
- **Study report (FR-042).** A repository method on both engines returns raw rows: per subtopic
  (and its course), attempts and correct attempts of one student (`attempts` ⋈ `items`, only
  `elo_valid` attempts, only items with a subtopic). An application service computes the share
  correct and orders it; no rating arithmetic. Exposed in the student's stats
  (`GET /api/student/stats` gains `subtopics`) and the teacher's view of a student
  (`GET /api/teacher/student/{id}` gains the same), with the teacher scope rules spec 006 already
  applies. The screens list subtopics with attempts and share correct, weakest first.

## Decision (owner, 2026-10-20): ratings stored on the old fine topics — rule A

After the regrouping, `student_course_topic_elo` rows keyed by an old fine topic (e.g. «Pensamiento
aleatorio — porcentaje sobre un total») no longer match any item, and — since a course rating is
the mean of its stored topic rows (`src/domain/elo/aggregation.py::course_rating`) — they would
keep counting in the course rating forever.

**Measured locally:** the seeded database has **0** such rows (no seeded student has a DIAN or
EPA8 rating). Production is not measured by an agent: the repair script's default (count-only)
run gives the owner the real numbers before anything is written.

**Approved (A), owner 2026-10-20:** a repair script `scripts/repairs/merge_fine_topic_ratings.py` (counts by
default, writes with `--apply`, prints counts only — spec 002 FR-018, `scripts/repairs/_repair.py`):
- per student and course, the ratings of the fine topics of one coarse topic are combined into the
  coarse topic as their **mean**, with RD the **mean of their RDs** (never below 30), `origin =
  'merged'`, `approximate = 1` and the old keys recorded as provenance (`legacy_source_key`,
  `reconciled_at`), as spec 001's legacy reconciliation records it;
- a coarse topic the student already has a row for is **never touched** (as reconciliation's
  FR-033);
- the old fine rows are copied to an additive archive table and then removed from the live store,
  so each coarse topic counts once in the course rating;
- `attempts` and every history row stay as they are; nothing is rebuilt from attempts (R15).

Note: spec 001's legacy reconciliation chooses one source row and **never averages** (its
FR-035), because there the rows were alternative records of the same thing. Here they are records
of different, smaller parts of one topic, so a mean is the faithful summary; the owner confirms
this departure (approved with A).

**Not chosen (B):** archive and remove the fine rows without merging: the coarse topic starts
unrated («diagnóstico pendiente») and is set by the student's next diagnostic or answers.

## Tests (written first)

| Test (both engines unless noted) | Proves |
|---|---|
| `tests/unit/scripts/test_validate_bank.py::test_subtopic_must_be_text` and `::test_a_small_topic_warns_and_passes` | FR-040, FR-043, US5-AS4 |
| `tests/unit/infrastructure/test_bank_content.py::test_dian_and_epa8_are_regrouped` (EPA8 five topics; P01 topic and subtopic; DIAN as the table) | FR-041, US5-AS1 |
| `tests/integration/test_spec008_t_topics.py::test_the_sync_stores_the_subtopic` | FR-040, US5-AS1 |
| `…::test_two_answers_in_one_coarse_topic_move_one_rating` (P01, P05) | FR-040, US5-AS2 |
| `…::test_the_subtopic_report_counts_across_courses` and `tests/api/…` for both endpoints | FR-042, US5-AS3 |
| `tests/integration/test_spec008_t_merge.py` (count-only run writes nothing; `--apply` merges per rule A, leaves existing coarse rows and attempts untouched, archives the fine rows; idempotent) | the confirmed rule |
| `tests/unit/infrastructure/test_spec002_schema_version.py` (version and digest raised) | schema |

§ Traceability rows FR-040 … FR-043 and US5-AS1 … AS4 are filled with these tests in the PR that
closes T.

## Risks and rollout

- **One resync** on every database at the first start after deploy (fingerprint change): it only
  reapplies the bank.
- **Order**: T before V (the id manifest freezes topics). The repair runs **after** the deploy that
  carries T, as an owner-approved step: first the count-only run, then `--apply`.
- **Until the repair runs**, an existing student's course rating on DIAN/EPA8 still includes the
  old fine rows; new answers already go to the coarse topics.
