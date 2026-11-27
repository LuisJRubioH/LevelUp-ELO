# Tasks — spec 006, deliveries AB1 … AB3 (the open question)

**Plan**: [plan-ab.md](plan-ab.md). FR-060 … FR-067 are `[CHANGE]`. The RS, AL, X1 and X2 pins stay
green throughout.

## Found while implementing

- **Two kinds** (user, 2026-11-27). The first AB1 and AB2 (commit `0661c79`) sent every typed
  answer to the AI. Rewritten: short answers graded on submission, procedures as photos read by the
  vision model. The unmerged version-11 migration was redefined in place.

## Phase 1 — Tests first (AB1, AB2; each fails on the code before them)

- [x] T001 [FR-060] `tests/integration/test_spec006_ab_open.py::test_the_teacher_writes_both_kinds`,
  `…::test_a_short_question_needs_an_accepted_answer`,
  `…::test_an_unstarted_templates_open_questions_can_change` (both engines).
- [x] T002 [US8-AS4, FR-060] `…::test_a_started_templates_open_questions_are_locked`.
- [x] T003 [US8-AS1, FR-061] `…::test_a_student_gets_statements_and_kinds_never_the_answers`.
- [x] T004 [US8-AS2, FR-062] `…::test_short_answers_are_graded_with_equivalents` (five forms),
  `…::test_a_typed_answer_to_a_procedure_is_refused`.
- [x] T005 [US8-AS3, FR-063] `…::test_a_procedure_photo_is_kept_and_replaced`,
  `…::test_a_photo_upload_is_refused_when_it_should_be`,
  `…::test_a_procedure_without_a_photo_is_blank`.
- [x] T006 [US8-AS5, FR-064] `…::test_the_ai_proposes_levels_for_a_photo_with_the_code_and_no_name`,
  `…::test_an_unreadable_reply_leaves_the_photo_to_the_teacher`,
  `…::test_without_a_key_the_photo_waits_for_the_teacher` (vision stub).
- [x] T007 [FR-062, FR-064] `tests/unit/domain/test_spec006_open_answers.py`: equivalences, the
  prompt, the reading, the scores, the teacher's levels.
- [x] T008 [US8-AS1 … AS3, FR-061 … FR-063] `frontend/e2e/spec006-ab-open.spec.ts`.
- [x] T009 [FR-060] `frontend/e2e/spec006-ab-teacher.spec.ts`.

## Phase 2 — Implementation (AB1, AB2)

- [x] T010 Both repositories: `_create_exam_open_questions` (three tables); `SCHEMA_VERSION` 11 and
  its digest.
- [x] T011 Both repositories: `set_template_open_questions`, `get_template_open_questions`,
  `save_open_photo`, `get_session_open_photos`, `get_session_open_answers`,
  `set_open_answer_proposal`; `complete_active_exam_session(..., open_answers)` upserts;
  `db_sync_check.py`.
- [x] T012 `src/domain/exams/open_answers.py`: kinds, equivalences, rubric, code, prompt, reading.
- [x] T013 `api/schemas/teacher.py`, `api/routers/teacher.py`: kinds, create, edit (locked),
  duplicate.
- [x] T014 `api/schemas/student.py`, `api/routers/student.py`: statements and kinds on start and
  resume; `POST /exam/open-photo`; the submission grades short answers and schedules the proposal.
- [x] T015 `src/infrastructure/external_api/math_procedure_review.py`: `rubric_from_image`;
  `api/open_answer_review.py`: `propose_for_session`.
- [x] T016 `frontend/src/pages/Student/Exam.tsx` and the `es`/`en` messages;
  `frontend/src/pages/Teacher/Exams.tsx`, `frontend/src/api/teacher.ts`.

## Phase 3 — Close AB1 and AB2

- [x] T017 Traceability: US8-AS1 … US8-AS5 and FR-060 … FR-064 filled; AB1 and AB2 `closed`;
  `AGENTS.md`. Checks: the suite on both engines, `db_sync_check.py`, `check_traceability.py`,
  `pnpm run build`, black (CI's version) and flake8.

## AB3 — planned

- [ ] T018 [US8-AS6, FR-065] Tests: the queue by code — a procedure with its photo and proposal, a
  short answer with its automatic grade; only the template's teacher.
- [ ] T019 [US8-AS7, FR-066] Tests: a manual grade without a reason is refused; with one it is
  recorded (who, when, before, after, reason); the student's result and the institution's report
  show it.
- [ ] T020 [FR-067] Tests: results and export count a short answer on submission and a procedure
  once decided, with whether it was changed by hand.
- [ ] T021 Implementation: repository reads and writes (both engines), routes, the queue screen.
