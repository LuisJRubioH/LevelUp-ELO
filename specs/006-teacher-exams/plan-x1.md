# Plan — spec 006, delivery X1: exam access and attempts

**Spec**: [spec.md](spec.md) § Deliveries, X1 (US2; FR-020 … FR-024) · **Branch**: `006-x1`, from
`redesign` · **Date**: 2026-10-19 · **Status**: draft for the owner (depends on N1, N3, N11)

## Summary

Exams check nothing about who asks: any token lists, starts and submits any course's exams, as
many times as it likes. X1 lets in only enrolled students, allows one graded attempt per
template, shows pending exams, and removes the smells of survey T8.

## Constitution Check (1.2.0)

| Principle | X1 |
|---|---|
| Minors (VI) | access as practice (spec 001 FR-037): only enrolled students |
| Ratings (I) | exams still move no rating (FR-004 stays pinned) |
| Dual database (IV, R1) | one additive change on both engines (below); `db_sync_check` |
| Async (R17) | the exam endpoints are `def`; no change |

## Design

- **Access (FR-020):** `require_role("student")` on `/exam/templates`, `/exam/pending`,
  `/exam/start`, `/exam/submit`, `/exam/history`; the course checked with
  `StudentService.ensure_enrolled` (the check practice uses), before any session is created. An
  empty `course_id` on `/exam/templates` becomes a 422 like `/exam/start`.
- **One attempt (FR-021):** `/exam/start` with a `template_id` the student already submitted (an
  `exam_sessions` row for the user and template) answers 409 «Ya presentaste este examen.».
  Standard exams keep no limit.
- **Pending (FR-022):** `list_pending_exams_for_student` (both engines) drops submitted templates;
  the student's exam screen lists them (today only the admin layout fetches them).
- **Smells (FR-023):** `course_name` read from `courses`; `@limiter.limit` on `/exam/start` (a new
  `rate_limit_exam_start`, 10/minute); `expire_stale_exam_sessions()` deletes
  `active_exam_sessions` 24 h past their deadline, at bootstrap and on each start.
- **Removed item (FR-024):** submit grades the items that still exist; a removed one comes back
  with `graded: false` and does not count in the score.
- No schema change.

## Tests (written first; each fails on today's code)

| Test (both engines) | Proves |
|---|---|
| `tests/integration/test_spec006_x1_exams.py::test_only_enrolled_students_reach_exams` (not enrolled, teacher, admin → 403, no session) | US2-AS1, FR-020 |
| `…::test_a_template_is_graded_once` and `…::test_pending_drops_a_submitted_template` | US2-AS2, FR-021, FR-022 |
| `…::test_the_course_name_comes_from_the_course`, `…::test_exam_starts_are_limited`, `…::test_stale_sessions_are_deleted` | FR-023 |
| `…::test_a_removed_item_is_reported_not_blocking` | US2-AS3, FR-024 |
| `frontend/e2e/spec006-x1-pending.spec.ts` | FR-022 |
