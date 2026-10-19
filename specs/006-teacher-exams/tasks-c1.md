# Tasks — spec 006, delivery C1 (the console from the server)

**Plan**: [plan-c1.md](plan-c1.md) (approved by the owner, 2026-10-19, with the range buttons kept
and working). FR-040 … FR-043 are `[CHANGE]`.

## Found while implementing

- **One set.** `teacher_links(user_id, group_id, course_id)` is a CTE shared by every teacher query
  on both engines (`_teacher_links_cte`): active, non-test students whose main group or enrolment
  group is the teacher's, with the course that links each one. Course-bound rows (attempts,
  procedures, KatIA, enrolments) are kept only for a linked course (`_linked_course`). A student
  listed by two of the teacher's groups shows the lower group id on the dashboard row and counts
  in both groups' figures.
- **Summary.** It travels with `GET /teacher/dashboard` (`summary`, and `summary.groups` per group)
  instead of a separate `/teacher/groups/{id}/summary`: one request serves the dashboard and the
  groups screen. Computed by `RatingReadService.console_summary` → `src/domain/elo/console.py`.
- **Attention.** Rated below 1100, or accuracy below 60 % over attempts in the window. A student
  with no attempts in the window has no accuracy: not flagged for it, and left out of the mean
  accuracy (the screen used to count it as 0 %).
- **Podium.** Places 1–3 only, ties share a medal; a pending student is never on it and shows «—».
- **Windows.** `?days=7|30|all` (default 30, anything else 422) on `/teacher/dashboard` and
  `/teacher/metrics`; the daily activity follows the window (it was fixed at 30 days). The query
  key carries the window. The groups screen uses the default window.
- **Teachers only.** The router requires the teacher role; the admin branches in template checks
  went with it. Unused client calls `studentReport` and `studentEloHistory` removed (the routes
  stay). `TeacherService.get_dashboard_data` is kept for the frozen V1.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/integration/test_spec006_c1_console.py` (both engines): one set everywhere, the
  moved student, the server summary, test students out of the group ranking, 403 for an admin,
  the 7 / 30 / all windows (US4-AS1 … AS4, FR-040 … FR-043).
- [x] T002 `frontend/e2e/spec006-c1-console.spec.ts`: the server's ranks, mean and «attention»;
  each button asks for its window (FR-041, FR-043).

## Phase 2 — Implementation

- [x] T003 Repositories (both engines): `_teacher_links_cte`, `_linked_course`, `_since`,
  `get_teacher_student_groups`; `get_teacher_dashboard_stats(days)`, `get_teacher_metrics(days)`,
  the four export sheets, the group counts and the group ranking on the one set.
- [x] T004 Domain `console_summary` and `tests/unit/domain/test_spec006_console.py` (FR-041).
- [x] T005 Router: `require_role("teacher")`, `days`, `summary`; the discarded students query gone.
- [x] T006 Frontend: `Dashboard.tsx` and `Groups.tsx` render the summary; 7d / 30d / Todo send
  `days`; existing e2e mocks match the URL with its query.

## Phase 3 — Close

- [x] T007 Traceability: US4-AS1 … AS4 and FR-040 … FR-043 filled; C1 `closed`. Checks run: the
  full suite on both engines, Playwright, black and flake8, `db_sync_check.py`,
  `check_traceability.py`, `pnpm run build`.
