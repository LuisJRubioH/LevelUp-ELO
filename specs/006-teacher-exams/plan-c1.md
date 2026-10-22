# Plan — spec 006, delivery C1: the console from the server

**Spec**: [spec.md](spec.md) § Deliveries, C1 (US4; FR-040 … FR-043) · **Branch**: `006-c1`, from
`redesign` · **Date**: 2026-10-19 · **Status**: approved by the owner (2026-10-19), with the range
buttons kept and working (FR-043)

## Summary

Each teacher screen, metric and export sheet builds its own student set (survey T13, T14), the
browser computes the group mean, the ranking and the «attention» list (T17, against R15), and an
admin passes the teacher check (T20). C1 gives the console one student set, one ranking source and
teacher-only routes.

## Constitution Check (1.2.0)

| Principle | C1 |
|---|---|
| Ratings read once (R15) | ranking, summary and attention from `RatingReadService`; the guard test `test_spec001_no_rating_aggregation_in_repositories_or_routers` stays green |
| Dual database (IV, R1) | one repository method for the set, on both engines |
| Design (D3) | data first; the group view shows the server's numbers |

## Design

- **One set (FR-040):** `teacher_student_ids(teacher_id)` (both engines): role student, active,
  not a test user, main group or enrolment group of the teacher's groups, with the courses that
  link each student to the teacher. The dashboard, metrics (`get_teacher_metrics`), group counts
  and the four export sheets filter by it, and course-bound data (attempts, procedures, KatIA,
  enrolments) by those courses (N7).
- **From the server (FR-041):** `GET /teacher/dashboard` carries a `summary`
  (`RatingReadService.console_summary` → `src/domain/elo/console.py`): the mean, the histogram
  buckets, the ranking (competition ranks, pending last; test students are not in the set) and
  the «attention» list (rated below 1100, or accuracy below 60 % over attempts in the window — a
  student with no attempts has no accuracy to judge), for the whole set and per group under
  `summary.groups` (a student in two of the teacher's groups counts in both). The group ranking
  route (`/teacher/student/{id}/ranking`) leaves test students out. `Dashboard.tsx` and
  `Groups.tsx` render it. *Implemented this way instead of a separate
  `/teacher/groups/{id}/summary`: one request serves both screens.*
- **Teachers only (FR-042):** the teacher router gets `require_role("teacher")`; the discarded
  `get_students_by_teacher` call and the unused client functions go.
- **Range views (FR-043):** `GET /teacher/dashboard?days=7|30|all` and
  `GET /teacher/metrics?days=7|30|all` (default 30, as the screen today); the repositories filter
  attempts by `timestamp >= now − days` (no filter for `all`, which starts at each student's
  registration); ratings, ranks and the group summary are not windowed. The 7d / 30d / Todo
  buttons send it and the query key carries it.

## Tests (written first)

| Test | Proves |
|---|---|
| `tests/integration/test_spec006_c1_console.py::test_every_place_lists_the_same_students` (both engines) | US4-AS2, FR-040 |
| `…::test_a_moved_student_shows_only_the_shared_course` | FR-040 (N7) |
| `…::test_the_summary_comes_from_the_server` and `…::test_the_group_ranking_leaves_out_test_students` | US4-AS1, FR-041 |
| `tests/unit/domain/test_spec006_console.py` | FR-041 (ranks, mean, attention, histogram, per group) |
| `…::test_an_admin_gets_403_on_teacher_routes` | US4-AS3, FR-042 |
| `…::test_the_dashboard_counts_the_chosen_window` (attempts 3, 20, 90 days old; 7, 30, all; both engines) | US4-AS4, FR-043 |
| `frontend/e2e/spec006-c1-console.spec.ts` › the server's ranking, mean and «attention» | US4-AS1, FR-041 |
| `frontend/e2e/spec006-c1-console.spec.ts` › each button asks for its window | US4-AS4, FR-043 |
