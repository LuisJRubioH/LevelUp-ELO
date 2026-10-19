# Specification Quality Checklist: Teacher Console & Exams

**Purpose**: Validate specification completeness and quality before planning (step 3)
**Created**: 2026-10-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details beyond what the brownfield needs — requirements name behaviour (who
  may start an exam, what the results count, which students a screen lists, where a rank is
  computed); file names appear only in the Code Scope and the plans
- [x] Focused on value — "Outcome served" stated
- [x] Written so the owner can decide — each decision N1 … N11 names the survey finding and a
  recommendation
- [x] All mandatory sections completed (Code Scope, Deliveries, Out of Scope, Traceability)

## Requirement Completeness

- [x] Every decision is decided — N1 … N11 approved by the owner on 2026-10-19 as recommended,
  except the range buttons, which stay and work (FR-043)
- [x] Requirements are testable — each FR names an observable outcome (a 403 with no session, a 409
  on a second attempt, results over the first submissions, the same students in every sheet, a
  rank shared by a tie)
- [x] Success criteria are measurable (0 sessions by non-enrolled users, the same student set in
  five places, 0 ranks computed in the browser, 0 procedures without a teacher)
- [x] All acceptance scenarios are defined — 16 scenarios over 5 stories
- [x] Edge cases are identified — a moved student, a mixed-course assignment, the grace period,
  standard exams
- [x] Scope is clearly bounded — ratings (001), membership and roles (004), AI (005), storage
  (002), V1 (F-10)
- [x] Dependencies and assumptions identified; one finding (survey T10) is handed to spec 001

## Feature Readiness

- [x] Every functional requirement has an acceptance scenario or a test row of its own
- [x] Each delivery stands on its own (X1, X2, C1, P1); X2's results need X1's one-attempt rule
  only for «first submission», which is defined without it
- [x] Traceability: one row per FR and scenario; delivery A cites tests that exist and pass on both
  engines (43 pytest, 10 Playwright, run 2026-10-19); open deliveries are `PENDING`

## Notes

- 2026-10-19: the owner approved the spec and the plans, with the range buttons kept (FR-043).
