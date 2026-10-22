# Plan — spec 006, delivery RV: review fixes before the switch

**Spec**: [spec.md](spec.md) § Deliveries, RV (US2-AS4, US4-AS5; FR-022a, FR-041a … FR-041c) ·
**Branch**: `006-rv`, from `redesign` · **Date**: 2026-10-21 · **Status**: for the owner's approval
(the decisions are the owner's, 2026-10-21: fixed before the switch; «Todos» by the mean of each
student's courses with the teacher; templates without an assignment documented and counted)

## Summary

The review of 2026-10-20 found three things in X2 and C1:

1. **Exams follow the main group only.** `list_active_templates_for_student` and
   `list_pending_exams_for_student` (both engines) look for an assignment to
   `users.group_id`. Joining a second teacher's group sets that column to the new group
   (`_enrol`), while the enrolment in the first course keeps its group. The student keeps the
   course and the first teacher keeps the student (FR-040), but the first group's exams vanish.
2. **The console ranks every set on the overall rating.** `RatingReadService.console_summary`
   uses `views[uid]["overall"]` for the whole set and for each group. A group of course X is
   therefore ranked on a mean that counts other courses — other teachers' courses included — while
   the student's own group ranking uses course X (spec 001 FR-028d). The screens show the overall
   number beside the place.
3. **Templates without an assignment.** On `main` they were shown to every enrolled student; from
   the switch they are drafts (FR-030). Production holds only demo accounts; the owner chose to
   document and count them.

## Constitution Check (1.2.0)

| Principle | RV |
|---|---|
| Ratings read once (R15) | every rating the console shows comes from `RatingReadService`; the rule for «Todos» is a pure domain function; the guard `test_spec001_no_rating_aggregation_in_repositories_or_routers` stays green |
| Dual database (IV, R1) | the two exam queries and the new links read change on both engines; `db_sync_check.py` |
| No schema change | no migration, so `SCHEMA_VERSION` (6) and the rehearsal already run stay valid |
| Tests first (VII) | each `[CHANGE]` test fails on the unchanged code |
| Design (D3) | data first: the ranking names its basis; no new decoration |

## Design

- **Exams of every linked group (FR-022a).** Both queries match an assignment whose group is the
  student's main group **or the group of their enrolment in the template's course**:
  `ea.group_id IN (SELECT group_id FROM users WHERE id = ? UNION SELECT group_id FROM enrollments
  WHERE user_id = ? AND course_id = et.course_id)`. Starting an exam already goes through
  `list_active_templates_for_student`, so it follows. A same-course move replaces the enrolment's
  group (`_enrol`), so the old group's exams drop out (N7). The stale docstrings («sin
  asignaciones → visible a todos») in both repositories and in `GET /exam/templates` are
  corrected. The same sentence in the `exam_assignments` DDL comment stays: it is inside the
  migration methods that `MIGRATION_SOURCES_DIGEST` covers, and changing it would raise
  `SCHEMA_VERSION` and ask for another rehearsal; it is corrected with the next migration change.
- **The links, with their course.** `get_teacher_student_groups` (used only by the dashboard)
  becomes `get_teacher_student_links(teacher_id)` on both engines: the distinct
  `(user_id, group_id, course_id)` rows of `teacher_links` (the CTE C1 already shares).
- **One rule for a set's rating (FR-041a, FR-041b).** Domain, `src/domain/elo/console.py`:
  `linked_rating(course_ratings, courses, overall)` — the overall rating when one link names no
  course; otherwise the equal-weight mean of the rated linked courses (`overall_rating` over them,
  so an unrated course does not count and none rated is pending).
  `RatingReadService.console_summary(students, links, group_courses)`:
  - «Todos»: each student's courses are those of all their links → `linked_rating`.
  - A group with a course C: the student's course C rating (spec 001 FR-028d).
  - A group without a course: the courses of the student's links through that group →
    `linked_rating` (a main-group link names no course → overall, as FR-028d; an enrolment link
    names its course → that course, N7).
  The domain `console_summary(entries, basis, group_bases)` keeps the C1 figures; each entry
  carries its «Todos» rating and its rating per group, each set carries its `basis`
  (`{"kind": "course", "course_id", "course_name"}` or `{"kind": "linked_courses"}`), and each
  ranking entry its `display_rating` and `rank_label` (FR-041c).
- **What the dashboard sends (FR-041c).** `GET /teacher/dashboard`: each student row carries the
  «Todos» `display_rating` and `rank_label` from the summary; `global_elo` and `overall_status`
  (the overall rating) are no longer sent. The student report and the AI analysis are outside RV.
- **Screens.** `Dashboard.tsx`: the rows shown in the students list, the ranking, the metrics and
  the drawer take their rating from the figures of the chosen set (all or one group); the ranking
  heading names the basis («Por ELO de Álgebra 7°» or «Por la media de sus cursos contigo») and the
  drawer says which rating it shows. `Groups.tsx`: each group's members show the group's rating.
  Nothing is computed in the browser (SC-003).
- **Templates without an assignment (owner: document and count).** `docs/transfer.md` § 6 «Before
  the switch» explains it and gives the read-only count; the `precheck` job of `transfer-ops.yml`
  (on the ops branches, outside this pull request) prints the same count, numbers only.

## Tests (written first)

| Test | Proves | Fails today because |
|---|---|---|
| `tests/integration/test_spec006_x1_exams.py::test_a_second_group_keeps_the_first_groups_exams` (both engines) | US2-AS4, FR-022a | the second group replaces the first in the query |
| `tests/integration/test_spec006_c1_console.py::test_a_group_ranks_on_its_course` (both engines) | US4-AS5, FR-041a | the group is ranked on the overall rating |
| `tests/integration/test_spec006_c1_console.py::test_all_groups_rank_on_the_courses_linked_to_the_teacher` (both engines) | US4-AS5, FR-041b, FR-041c | «Todos» uses the overall; the rows send `global_elo` |
| `tests/unit/domain/test_spec006_console.py::test_each_set_ranks_on_its_basis` | FR-041a, FR-041c | no basis, no rating on ranking entries |
| `tests/unit/domain/test_spec006_console.py::test_the_linked_rating` | FR-041b | `linked_rating` does not exist |
| `frontend/e2e/spec006-c1-console.spec.ts` › each group by its course, «Todos» by the courses with the teacher | US4-AS5, FR-041c | the screen shows the overall number |

The C1 tests keep their names; their fixtures gain the basis (unit) and they must stay green.
Spec 001's `test_spec001_number_and_label_agree_on_every_surface` reads the dashboard row of a
student with one course and must stay green unchanged.

## Risks and rollout

- **Behaviour change at the switch:** none beyond C1's — the console is new with the redesign.
- **No schema change.** The backup and rehearsal runs already prepared (on `45a7157`) stay valid;
  only the precheck gains a count, so its run is dispatched again for the owner to approve.
- **#73 (E3)** touches the same repositories; it is brought up to date after RV lands.
