# Tasks — spec 006, delivery RV (review fixes before the switch)

**Plan**: [plan-rv.md](plan-rv.md). FR-022a, FR-041a, FR-041b and FR-041c are `[CHANGE]`; there
is no `[AS-IS]` requirement in RV. The C1 and X1 pins already in § Traceability stay green
throughout.

## Phase 1 — Tests first (each fails on the unchanged code)

- [ ] T001 [US2-AS4, FR-022a] `tests/integration/test_spec006_x1_exams.py::test_a_second_group_keeps_the_first_groups_exams`
  (both engines): an exam assigned to the student's first group in course X; the student joins a
  second teacher's group for course Y; the exam is still listed for X, among the pending exams,
  and starts; after joining another group for X it is no longer listed.
- [ ] T002 [US4-AS5, FR-041a] `tests/integration/test_spec006_c1_console.py::test_a_group_ranks_on_its_course`
  (both engines): two students of a course-X group, ordered one way on X and the other way on the
  overall rating; the group's ranking, mean and ranking entries follow X.
- [ ] T003 [US4-AS5, FR-041b, FR-041c] `tests/integration/test_spec006_c1_console.py::test_all_groups_rank_on_the_courses_linked_to_the_teacher`
  (both engines): «Todos» ranks a student linked only through course X on X, and one linked
  through a group without a course on the overall rating; the dashboard rows carry those
  ratings and no `global_elo` or `overall_status`.
- [ ] T004 [FR-041a, FR-041b, FR-041c] `tests/unit/domain/test_spec006_console.py::test_each_set_ranks_on_its_basis`
  and `…::test_the_linked_rating`.
- [ ] T005 [US4-AS5, FR-041c] `frontend/e2e/spec006-c1-console.spec.ts` › each group by its course
  and «Todos» by the courses with the teacher: the numbers beside the places and the basis named.

## Phase 2 — Implementation (after Phase 1 fails)

- [ ] T006 [FR-022a] Both repositories: the assignment's group is the main group or the
  enrolment's group in the template's course, in `list_active_templates_for_student` and
  `list_pending_exams_for_student`; docstrings corrected (also `GET /exam/templates`).
- [ ] T007 [FR-041a, FR-041b] Both repositories: `get_teacher_student_links` replaces
  `get_teacher_student_groups`; `python scripts/db_sync_check.py`.
- [ ] T008 [FR-041a … c] Domain `linked_rating` and `console_summary(entries, basis, group_bases)`;
  `RatingReadService.console_summary(students, links, group_courses)`; the C1 unit fixtures gain
  the basis.
- [ ] T009 [FR-041c] Router `GET /teacher/dashboard`: the rows carry the «Todos» rating from the
  summary; `global_elo` and `overall_status` are no longer sent.
- [ ] T010 [FR-041c] `frontend/src/api/teacher.ts`, `Dashboard.tsx`, `Groups.tsx`: ratings from the
  chosen set's figures, the basis named; the C1 e2e mocks gain the ranking entries' ratings.

## Phase 3 — Close

- [ ] T011 Traceability: US2-AS4, US4-AS5, FR-022a, FR-041a … c filled; RV `closed`. Checks: the
  full suite on both engines, Playwright, black and flake8, `db_sync_check.py`,
  `check_traceability.py`, `pnpm run build`.
- [ ] T012 Outside the pull request: the read-only count of templates without an assignment in the
  `precheck` job (ops branches), and the owner told which run to approve.
