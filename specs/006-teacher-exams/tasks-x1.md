# Tasks — spec 006, delivery X1 (exam access and attempts)

**Plan**: [plan-x1.md](plan-x1.md) (approved by the owner, 2026-10-19). FR-020 … FR-024 are
`[CHANGE]`.

## Found while implementing

- **Enrolment is checked again at submission.** Losing an enrolment between the start and the
  submit is a 403. A student with no session of their own still gets 404 for an unknown session.
- **Existing tests updated for FR-020:**
  - `test_exam_submit_deadline.py` and `test_exam_assignment_window.py` used students with no
    enrolment; they now enrol them.
  - `test_student.py::TestExamMode::test_exam_start_nonexistent_course` now expects 403: a course
    that does not exist is one the student is not enrolled in.
  - FR-005's 404 for an enrolled course with no items moved to
    `test_spec006_x1_exams.py::test_a_course_without_items_is_404`.
- **One attempt.** It is checked at the start and again at the submit, which closes the case of
  two sessions started before the first submission. No unique index is added: existing data may
  hold repeated sessions, and the migration would stop on them.
- **A submitted template** leaves both the student's template list and their pending exams. The
  pending list is shown on the exam screen («Exámenes asignados»); one click selects the course and
  the template.
- **Course name.** The course name stored with the history is the one of the student's enrolment;
  the request's `course_name` is ignored.
- **Start limit.** Exam starts: `RATE_LIMIT_EXAM_START`, 10 a minute by default.
- **Stale sessions.** Active sessions 24 hours past their deadline are deleted at bootstrap and at
  each start.
- **Removed item.** A removed item comes back with `graded: false` and is left out of
  `total_questions` and the score. If no item remains, the submit is a 409.
- **Still to come.** Templates with no assignment are still visible to the course until X2 (N2).

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/integration/test_spec006_x1_exams.py` (both engines) — US2-AS1 … AS3,
  FR-020 … FR-024:
  - who may take an exam;
  - a student no longer enrolled;
  - an empty course;
  - one attempt;
  - pending exams;
  - the course name;
  - the start limit;
  - stale sessions;
  - a removed item;
  - an enrolled course with no items.
- [x] T002 `frontend/e2e/spec006-x1-pending.spec.ts` — FR-022, FR-024:
  - assigned exams listed and chosen;
  - a removed item shown as not graded.

## Phase 2 — Implementation

- [x] T003 Exam routes:
  - students only (`require_role("student")`);
  - enrolment on templates, start and submit;
  - a 422 for an empty course on `/exam/templates`.
- [x] T004 Repositories, on both engines:
  - `has_submitted_template` and `expire_stale_exam_sessions`;
  - the template and pending queries drop submitted templates;
  - bootstrap sweep.
- [x] T005 Submit:
  - one attempt;
  - the course name from the enrolment;
  - removed items reported (`graded`).
- [x] T006 Start:
  - one attempt (409 «Ya presentaste este examen.»);
  - the sweep;
  - `@limiter.limit(settings.rate_limit_exam_start)`.
- [x] T007 Frontend:
  - «Exámenes asignados» on the exam screen;
  - not-graded items in the results (es, en).

## Phase 3 — Close

- [x] T008 Traceability: US2-AS1 … AS3 and FR-020 … FR-024 filled; X1 `closed`. Full suite on both
  engines, Playwright, black, flake8, `db_sync_check.py`, `check_traceability.py`,
  `pnpm run build`.
