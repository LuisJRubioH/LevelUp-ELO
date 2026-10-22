# Tasks — spec 006, delivery RV (review fixes before the switch)

**Plan**: [plan-rv.md](plan-rv.md). FR-022a, FR-041a, FR-041b and FR-041c are `[CHANGE]`; there
is no `[AS-IS]` requirement in RV. The C1 and X1 pins already in § Traceability stay green
throughout.

## Found while implementing

- **Links.** `get_teacher_student_links` replaced `get_teacher_student_groups`, whose only caller
  was the dashboard; it returns the distinct `(user_id, group_id, course_id)` rows of
  `teacher_links`. The group's own course comes from `get_groups_by_teacher`, which the
  dashboard already read.
- **One rule.** `linked_rating` decides every set without a course of its own; a group with a
  course asks it for that one course. The service reads the course ratings from
  `ratings_view_bulk`, the same rows and current courses a student's overall rating uses.
- **Rows.** The dashboard rows copy the «Todos» rating and label from the summary's ranking; the
  screens overlay the chosen set's ratings from its ranking, so the students list, the ranking,
  «attention» and the drawer show one number per student and set.
- **Labels.** The ranking heading was «Ranking global · Por ELO global»; it is «Ranking» with the
  basis. The group card showed its mean with no label; it now names the basis, as the group
  detail and the drawer do.
- **Not RV.** A React warning about list keys in `frontend/e2e/spec004-display-names.spec.ts`
  (the teacher dashboard with that spec's mock) is there on the unchanged code too.

## Phase 1 — Tests first (each fails on the unchanged code)

- [x] T001 [US2-AS4, FR-022a] `tests/integration/test_spec006_x1_exams.py::test_a_second_group_keeps_the_first_groups_exams`
  (both engines): an exam assigned to the student's first group in course X; the student joins a
  second teacher's group for course Y; the exam is still listed for X, among the pending exams,
  and starts; after joining another group for X it is no longer listed.
- [x] T002 [US4-AS5, FR-041a] `tests/integration/test_spec006_c1_console.py::test_a_group_ranks_on_its_course`
  (both engines): two students of a course-X group, ordered one way on X and the other way on the
  overall rating; the group's ranking, mean and ranking entries follow X.
- [x] T003 [US4-AS5, FR-041b, FR-041c] `tests/integration/test_spec006_c1_console.py::test_all_groups_rank_on_the_courses_linked_to_the_teacher`
  (both engines): «Todos» ranks a student linked only through course X on X, and one linked
  through a group without a course on the overall rating; the dashboard rows carry those
  ratings and no `global_elo` or `overall_status`.
- [x] T004 [FR-041a, FR-041b, FR-041c] `tests/unit/domain/test_spec006_console.py::test_each_set_ranks_on_its_basis`
  and `…::test_the_linked_rating`.
- [x] T005 [US4-AS5, FR-041c] `frontend/e2e/spec006-c1-console.spec.ts` › each group by its course
  and «Todos» by the courses with the teacher: the numbers beside the places and the basis named.

## Phase 2 — Implementation (after Phase 1 fails)

- [x] T006 [FR-022a] Both repositories: the assignment's group is the main group or the
  enrolment's group in the template's course, in `list_active_templates_for_student` and
  `list_pending_exams_for_student`; docstrings corrected (also `GET /exam/templates`).
- [x] T007 [FR-041a, FR-041b] Both repositories: `get_teacher_student_links` replaces
  `get_teacher_student_groups`; `python scripts/db_sync_check.py`.
- [x] T008 [FR-041a … c] Domain `linked_rating` and `console_summary(entries, basis, group_bases)`;
  `RatingReadService.console_summary(students, links, group_courses)`; the C1 unit fixtures gain
  the basis.
- [x] T009 [FR-041c] Router `GET /teacher/dashboard`: the rows carry the «Todos» rating from the
  summary; `global_elo` and `overall_status` are no longer sent.
- [x] T010 [FR-041c] `frontend/src/api/teacher.ts`, `Dashboard.tsx`, `Groups.tsx`: ratings from the
  chosen set's figures, the basis named; the C1 e2e mocks gain the ranking entries' ratings.

## Phase 3 — Close

- [x] T011 Traceability: US2-AS4, US4-AS5, FR-022a, FR-041a … c filled; RV `closed`. Checks: the
  full suite on both engines, Playwright, black and flake8, `db_sync_check.py`,
  `check_traceability.py`, `pnpm run build`.
- [x] T012 Outside the pull request: the read-only count of templates without an assignment in the
  `precheck` job (ops branches, `85deb6b`), and the owner told which run to approve.
