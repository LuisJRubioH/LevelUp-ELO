# Tasks — spec 006, delivery P1 (the procedures queue)

**Plan**: [plan-p1.md](plan-p1.md) (approved by the owner, 2026-10-19). FR-050 and FR-051 are
`[CHANGE]`.

## Found while implementing

- **Who reviews a procedure.** One rule, `_procedure_reaches_teacher` over C1's `teacher_links`
  (both engines): the student is active, not a test user, and linked to the teacher through the
  item's course — by an enrolment in one of the teacher's groups, or by a main group of that
  course (or of a group with no course). An id with no bank item follows the main group, as
  before. The queue, its count, the grading transaction, the grading history and the recent
  copies all use it (`_procedure_for_teacher` for one procedure), so a teacher grades exactly
  what the queue shows. The V1 per-group branch (`group_id`) is unchanged (V1 is frozen).
- **Resubmission.** It clears `ai_proposed_score` and `ai_feedback` and puts the procedure back
  as `pending`; a new AI review sets them again.
- **The grade.** `Procedures.tsx` starts with no grade («—», «Elige una calificación»), «Guardar
  calificación» disabled until the teacher picks one, and empty again for a new review round. The
  AI score and its feedback (`ai_feedback`, now in `PendingProcedure`) are shown beside it.
  `spec001-b7-procedures.spec.ts` › the resubmission test now picks the grade again for the new
  round.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/integration/test_spec006_p1_queue.py` (both engines): the queue follows the
  item's course (no main group; a main group of another course) and only that teacher grades it;
  inactive and test students out of the queue and its count; a resubmission clears the AI score
  and feedback (US5-AS1, US5-AS2, FR-050, FR-051).
- [x] T002 `frontend/e2e/spec006-p1-grade.spec.ts`: empty grade, AI score and feedback beside it,
  nothing saved until a grade is picked (US5-AS2, FR-051).

## Phase 2 — Implementation

- [x] T003 Repositories (both engines): `_procedure_reaches_teacher`, `_procedure_for_teacher`;
  the queue, the count, `grade_procedure_transaction`, `get_procedure_gradings`,
  `get_recent_procedure_copies_for_teacher`; `submit_procedure` clears the AI score.
- [x] T004 API: `ai_feedback` in `PendingProcedure`.
- [x] T005 Frontend: `Procedures.tsx` and `TeacherConsole.css`.

## Phase 3 — Close

- [x] T006 Traceability: US5-AS1, US5-AS2, FR-050, FR-051 filled; P1 `closed` — spec 006 has no
  `PENDING` row. Checks run: the full suite on both engines, Playwright, black and flake8,
  `db_sync_check.py`, `check_traceability.py`, `pnpm run build`.
