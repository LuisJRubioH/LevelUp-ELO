# Tasks — spec 006, delivery RS (resuming a started template)

**Plan**: [plan-rs.md](plan-rs.md). FR-025, FR-026 and FR-027 are `[CHANGE]`; there is no
`[AS-IS]` requirement in RS. The X1 and X2 pins already in § Traceability stay green throughout.

## Found while implementing

- **The grace.** A first version filtered the listings in SQL against the stored deadline, which
  includes the 30-second grace: for those 30 seconds a template was listed whose start was
  already refused. The listings now use the router's rule, the same as the start.

## Phase 1 — Tests first (each fails on the unchanged code)

- [x] T001 [US6-AS1, FR-025] `tests/integration/test_spec006_rs_resume.py::test_a_started_template_resumes_with_the_time_left`
  (both engines): same session, items in order, 100–120 seconds left, one session, graded.
- [x] T002 [US6-AS2, FR-025] `…::test_resuming_does_not_need_the_window_open` (both engines).
- [x] T003 [US6-AS3, FR-026] `…::test_an_attempt_whose_time_ran_out_is_used` (both engines): 409
  with a reason; not in the exams or pending lists.
- [x] T004 [US6-AS3, FR-027] `…::test_the_sweep_keeps_an_unsubmitted_template_attempt` (both
  engines): the template session stays a day past its deadline; a standard one goes.
- [x] T005 [US6-AS4] `…::test_standard_exams_start_fresh` (both engines).
- [x] T006 [US6-AS1, US6-AS3, FR-025, FR-026] `frontend/e2e/spec006-rs-resume.spec.ts`: the
  resumed notice and the server's seconds left; the saved answers of the same session; the
  server's reason on a run-out attempt.

## Phase 2 — Implementation (after Phase 1 fails)

- [x] T007 [FR-025, FR-026] Both repositories: `get_open_template_session(user_id, template_id,
  course_id)`; `python scripts/db_sync_check.py`.
- [x] T008 [FR-027] Both repositories: `expire_stale_exam_sessions` keeps an unsubmitted template
  session.
- [x] T009 [FR-025, FR-026] `api/routers/student.py`: resume or refuse before the window check;
  `_attempt_used` filters `GET /exam/templates` and `GET /exam/pending`;
  `ExamStartResponse.resumed`.
- [x] T010 [FR-025, FR-026] `frontend/src/pages/Student/Exam.tsx` and the `es`/`en` messages.

## Phase 3 — Close

- [x] T011 Traceability: US6-AS1 … US6-AS4, FR-025 … FR-027 filled; RS `closed`. Checks: the
  suite, `db_sync_check.py`, `check_traceability.py`, `pnpm run build`, black and flake8.
