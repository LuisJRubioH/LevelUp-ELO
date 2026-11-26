# Tasks — spec 006, deliveries AB1 … AB3 (the open question)

**Plan**: [plan-ab.md](plan-ab.md). FR-060 … FR-065 are `[CHANGE]`. The RS, AL, X1 and X2 pins stay
green throughout.

## Phase 1 — Tests first (AB1, AB2; each fails on the unchanged code)

- [x] T001 [FR-060] `tests/integration/test_spec006_ab_open.py::test_the_teacher_writes_open_questions`,
  `…::test_an_unstarted_templates_open_questions_can_change` (both engines).
- [x] T002 [US8-AS1, FR-061] `…::test_a_student_gets_the_statements_never_the_reference`.
- [x] T003 [US8-AS2, FR-062] `…::test_typed_answers_are_kept_under_a_code_and_move_no_rating`,
  `…::test_an_answer_to_a_question_not_in_the_template_is_refused`,
  `…::test_an_answer_longer_than_the_limit_is_refused`.
- [x] T004 [US8-AS3, FR-060] `…::test_a_started_templates_open_questions_are_locked`.
- [x] T005 [US8-AS4, FR-063] `…::test_the_ai_proposes_four_levels_with_the_code_and_no_name`,
  `…::test_an_unreadable_reply_leaves_the_answer_to_the_teacher`,
  `…::test_without_a_key_the_answer_waits_for_the_teacher` (provider stub).
- [x] T006 [FR-063] `tests/unit/domain/test_spec006_open_answers.py`: the prompt, the reading, the
  scores, the teacher's levels.
- [x] T007 [US8-AS1, US8-AS2, FR-061, FR-062] `frontend/e2e/spec006-ab-open.spec.ts`.
- [x] T008 [FR-060] `frontend/e2e/spec006-ab-teacher.spec.ts`.

## Phase 2 — Implementation (AB1, AB2)

- [x] T009 Both repositories: `_create_exam_open_questions`; `SCHEMA_VERSION` 11 and its digest.
- [x] T010 Both repositories: `set_template_open_questions`, `get_template_open_questions`,
  `get_session_open_answers`, `set_open_answer_proposal`; `complete_active_exam_session(...,
  open_answers)`; `db_sync_check.py`.
- [x] T011 `src/domain/exams/open_answers.py`: rubric, code, prompt, reading.
- [x] T012 `api/schemas/teacher.py`, `api/routers/teacher.py`: create, edit (locked), duplicate,
  the response's `open_questions`.
- [x] T013 `api/schemas/student.py`, `api/routers/student.py`: start and resume carry the
  statements; the submission keeps the answers and schedules the proposal.
- [x] T014 `api/open_answer_review.py`: `propose_for_session`.
- [x] T015 `frontend/src/pages/Student/Exam.tsx` and the `es`/`en` messages;
  `frontend/src/pages/Teacher/Exams.tsx`, `frontend/src/api/teacher.ts`, `TeacherConsole.css`.

## Phase 3 — Close AB1 and AB2

- [x] T016 Traceability: US8-AS1 … US8-AS4 and FR-060 … FR-063 filled; AB1 and AB2 `closed`;
  `AGENTS.md`. Checks: the suite on both engines, `db_sync_check.py`, `check_traceability.py`,
  `pnpm run build`, black (CI's version) and flake8.

## AB3 — planned

- [ ] T017 [US8-AS5, FR-064] Tests: the queue by code, the teacher's levels recorded with who and
  when, the AI's kept; only the template's teacher.
- [ ] T018 [FR-065] Tests: results and export count a decided open answer.
- [ ] T019 Implementation: repository reads and writes (both engines), `GET` and `PUT` routes, the
  queue screen in `Teacher/Exams.tsx`.
