# Plan — spec 006, delivery RS: resuming a started template

**Spec**: [spec.md](spec.md) § Deliveries, RS (US6-AS1 … US6-AS4; FR-025 … FR-027) ·
**Branch**: `claude/dazzling-mendel-uta2jw` · **Date**: 2026-11-25 · **Status**: for the owner's
approval (Clarifications, session 2026-11-25: resume; a run-out attempt is used)

## Summary

A template is graded once (FR-021), but `POST /exam/start` created a new session on every call
until the student submitted. A student could open a template, read its items, leave and start it
again with the whole time. The 2027 municipal olympiad takes its two virtual phases as templates
from home, so that gap decides who qualifies.

## Constitution Check (1.2.0)

| Principle | RS |
|---|---|
| Dual database (IV, R1) | one new read (`get_open_template_session`) and one sweep condition on both engines; `db_sync_check.py` |
| No schema change | no column, table or index: `SCHEMA_VERSION` and its digest stay as they are |
| Ratings (R15) | untouched: an exam still moves no rating (FR-004) |
| Tests first (VII) | the five integration tests and the three browser tests fail on the unchanged code |
| Secrets (V2-R9) | a resumed session carries the items as the first start did: no correct option |

## Design

- **Resume (FR-025).** For a template, after the FR-021 check and before the window check,
  `get_open_template_session(user, template, course)` returns the student's earliest unsubmitted
  session of that template in that course. With time left — the stored deadline minus the
  30-second grace, in whole seconds — the router answers with that session: its items read one by
  one in the stored order (an item removed from the bank keeps its place, so the submission still
  names every item and FR-024 reports it), `time_limit_seconds` = the seconds left and
  `resumed: true`. No session is created, and the window is not checked again: a student who
  started inside it finishes.
- **A run-out attempt is used (FR-026).** With no time left, the start is refused with 409 and a
  reason. `GET /exam/templates` and `GET /exam/pending` drop such templates with the same rule
  (`_attempt_used`), in the router, so the 30-second grace never shows a template that cannot
  start. The SQL of both listings is unchanged.
- **The sweep keeps the record (FR-027).** `expire_stale_exam_sessions` deletes as before, except
  an unsubmitted template session: it is the only trace that the attempt was used. One row per
  student and template at most, so the table stays small.
- **The screen.** `Exam.tsx` reads `resumed`: it says the exam resumed and that the clock kept
  running, counts down from the server's seconds left, and, when this device's draft belongs to
  the same session, brings its answers back. A 409 on start shows the server's reason instead of
  the generic error. Standard exams are unchanged (US6-AS4).

## Out of scope

- Saving answers on the server before the submission: the screen's draft and the grace already
  deliver a submission sent at the limit; a run-out attempt has nothing to grade.
- Two starts racing each other could still create two sessions; the earliest is the one resumed
  and FR-021 grades only one submission.
