# Tasks — spec 003, delivery L4 (what the teacher sees)

**Plan**: [plan-l4.md](plan-l4.md) (approved by the owner, 2026-10-19). FR-040 … FR-042 are
`[CHANGE]`; FR-006 (no free text) is kept; N11 (the teacher sees right or wrong and the tag, not
the chosen value) applies here.

## Found while writing the tests

- The teacher's per-student endpoints live under `/teacher/student/{id}/…` and answer **404** to a
  teacher whose groups do not hold the student (`_require_teacher_student`). The path endpoint
  follows them: `GET /teacher/student/{id}/path/{course}` — another teacher 404, a student 403
  (the router's role guard), a course without a path 404.
- `path_summary` read only the latest answer, so a misconception corrected later disappeared from
  the student's review; it now reads the history.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/integration/test_spec003_l4_record.py` (both engines): wrong then right kept in
  order; outcome stored and shown; never «worse»; no free text; only the student's teacher; the
  migration copies each last answer once — US4-AS1 … AS3, FR-040 … FR-042
- [x] T002 `tests/unit/domain/test_spec003_l4_record.py`: the outcome rule; every interaction of
  the catalogue has a label that is not its id — FR-041, N11
- [x] T003 `frontend/e2e/spec003-l4-teacher-path.spec.ts`: the student panel lists the nodes with
  activity, the history in order on demand, the outcome

## Phase 2 — Implementation

- [x] T004 Both repositories: `_create_lesson_history` (tables `lesson_answers` + index,
  `lesson_outcomes`; copies each `lesson_interactions` row once); `save_lesson_interaction` writes
  the history in the same transaction; `get_lesson_answers`, `save_lesson_outcome`,
  `get_lesson_outcomes`; `SCHEMA_VERSION` 3 and the new digest
- [x] T005 Domain (`path.py`): `interaction_label` (also the L3 refusal's labels),
  `is_post_diagnostic`, `post_diagnostic_outcome`; `prealgebra.path_record`; `path_summary` reads
  the history
- [x] T006 Routers: the last post-diagnostic answer stores the outcome and returns it; the lesson's
  `progress.outcome`; `GET /teacher/student/{id}/path/{course}` with `StudentPathResponse`
- [x] T007 Frontend: `ElevenBlockLesson` shows the server's outcome; the teacher's student panel
  gets «Ruta de aprendizaje» before the AI analysis (AGENTS D3)

## Phase 3 — Close

- [x] T008 Traceability: US4-AS1 … AS3, FR-040 … FR-042 filled; L4 `closed`; full suite on both
  engines, Playwright, black, flake8, `db_sync_check.py`, `check_traceability.py`, `pnpm run build`
