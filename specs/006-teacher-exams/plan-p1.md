# Plan — spec 006, delivery P1: the procedures queue

**Spec**: [spec.md](spec.md) § Deliveries, P1 (US5; FR-050, FR-051) · **Branch**: `006-p1`, from
`redesign` · **Date**: 2026-10-19 · **Status**: approved by the owner (2026-10-19)

## Summary

The queue follows the student's main group, so a procedure of a student with no group, or whose
group belongs to another course, never reaches a teacher; it mixes inactive and test students; the
AI score starts the grade and stays stale after a resubmission; the AI feedback is never shown.

## Constitution Check (1.2.0)

| Principle | P1 |
|---|---|
| Ratings (I) | the grade's effect stays spec 001 block 7's; P1 changes who sees the procedure, not what a grade applies |
| Dual database (IV, R1) | the queue query on both engines; no schema change |

## Design

- **Who sees it (FR-050):** a pending procedure goes to the teachers of the groups enrolled in the
  item's course (enrolments of the student in that course), for active, non-test students; the
  grading transaction checks the same relation instead of `users.group_id`. Free exercise ids
  (no bank item) keep today's rule (the student's main group).
- **The slider (FR-051):** `Procedures.tsx` starts with no grade (the «Validar» button disabled
  until one is chosen); the AI score and `ai_feedback` (added to `PendingProcedure`) are shown
  beside it; `submit_procedure`'s resubmission clears `ai_proposed_score` and `ai_feedback`.

## Tests (written first)

| Test | Proves |
|---|---|
| `tests/integration/test_spec006_p1_queue.py::test_the_queue_follows_the_items_course` (both engines; a student with no group, one in another course's group) | US5-AS1, FR-050 |
| `…::test_inactive_and_test_students_are_not_queued` | FR-050 |
| `…::test_a_resubmission_clears_the_ai_score` | FR-051 |
| `frontend/e2e/spec006-p1-grade.spec.ts` (empty slider, AI score and feedback shown) | US5-AS2, FR-051 |
