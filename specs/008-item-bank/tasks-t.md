# Tasks — spec 008, delivery T (topics and subtopics)

**Plan**: [plan-t.md](plan-t.md) (merge rule A approved by the owner, 2026-10-20).
FR-040 … FR-043 are `[CHANGE]`; there is no `[AS-IS]` requirement in T, so no characterization
phase. Delivery A's pins (validator, bank content, sync) must stay green throughout.

## Phase 1 — Tests first (fail on the unchanged code)

- [ ] T001 [P] [US5] `tests/unit/scripts/test_validate_bank.py`: `subtopic` must be non-empty text
  when present; a topic with fewer than 5 items warns, naming it, and exits 0 (FR-040, FR-043,
  US5-AS4).
- [ ] T002 [P] [US5] `tests/unit/infrastructure/test_bank_content.py::test_dian_and_epa8_are_regrouped`:
  EPA8 has the five «Pensamiento …» topics; P01 has topic «Pensamiento aleatorio» and subtopic
  «porcentaje sobre un total»; DIAN's topics are the approved table's (FR-041, US5-AS1).
- [ ] T003 [US5] `tests/integration/test_spec008_t_topics.py` (both engines): the sync stores
  `subtopic`; two answers on P01 and P05 move the one «Pensamiento aleatorio» rating and no
  rating is keyed by a subtopic (FR-040, US5-AS1, US5-AS2).
- [ ] T004 [US5] same file + `tests/api/test_spec008_t_report.py`: the per-subtopic report of a
  student, across courses, in `GET /api/student/stats` and `GET /api/teacher/student/{id}`
  (teacher scope as spec 006) (FR-042, US5-AS3).
- [ ] T005 `tests/integration/test_spec008_t_merge.py` (both engines): the repair's count-only run
  writes nothing; `--apply` applies the rule the owner confirmed (plan § The decision), leaves an
  existing coarse row and every attempt untouched, archives the fine rows; a second run changes
  nothing.
- [ ] T006 `tests/unit/infrastructure/test_spec002_schema_version.py`: the next `SCHEMA_VERSION`
  and its digest (fails until the migration changes).

## Phase 2 — Implementation (after Phase 1 fails for the right reason)

- [ ] T007 Bank: the one-time regrouping of `items/bank/DIAN.json` and
  `items/bank/evaluar_para_avanzar_8.json` (plan table); `scripts/build_epa8_bank.py` emits
  `topic`/`subtopic` (depends on T002).
- [ ] T008 Validator: `subtopic` check and the small-topic warning in `scripts/validate_bank.py`
  (depends on T001).
- [ ] T009 Schema and sync, both repositories: additive `items.subtopic`; `sync_items_from_bank_folder`
  writes it; `SCHEMA_VERSION`, `MIGRATION_SOURCES_DIGEST`, `docs/transfer.md` (depends on T003,
  T006). `db_sync_check.py`.
- [ ] T010 Report: repository method (raw counts, both engines), application service, the two
  endpoints and their screens (`frontend/src/pages/Student/`, teacher student view; i18n es/en)
  (depends on T004).
- [ ] T011 Repair: `scripts/repairs/merge_fine_topic_ratings.py` per the confirmed rule; the
  additive archive table on both engines if the rule archives (depends on T005).

## Phase 3 — Close

- [ ] T012 Traceability: FR-040 … FR-043 and US5-AS1 … AS4 filled; T `closed`. Checks: the full
  suite on both engines, `validate_bank.py`, `db_sync_check.py`, `check_traceability.py`, black
  and flake8, `pnpm run build`, Playwright for the report screens.
- [ ] T013 Rollout note in the PR: one resync at the first start; the owner runs the repair's
  count-only mode on production, then `--apply`.
