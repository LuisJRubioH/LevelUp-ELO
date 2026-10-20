# Specification Quality Checklist: Item Bank

**Purpose**: Validate specification completeness and quality before planning (step 3)
**Created**: 2026-10-20
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details beyond what the brownfield needs — requirements name behaviour
  (what the validator rejects, which items are served, which difficulty wins); file names appear
  only in the Code Scope, the manifest's location (N1) and the plans
- [x] Focused on value — "Outcome served" stated
- [x] Written so the owner can decide — D1 … D6 come from the owner (survey § 8); N1 … N3 each
  carry a recommendation
- [x] All mandatory sections completed (Code Scope, Deliveries, Out of Scope, Traceability)

## Requirement Completeness

- [x] The survey's decisions are decided — D1 … D6 by the owner on 2026-10-20; B19 explicitly
  deferred and out of scope
- [ ] N1 … N3 approved by the owner (manifest location, audit table, un-retiring)
- [x] Requirements are testable — each FR names an observable outcome (a failing validator run, an
  item not served, a difficulty value after a sync, counts without writes)
- [x] Success criteria are measurable (0 retired items served, 0 out-of-range difficulties, 1
  catalogue, 0 moved ids)
- [x] All acceptance scenarios are defined — 11 scenarios over 4 stories
- [x] Edge cases are identified — an exam started before a retirement, un-retiring, an edit equal
  to the calibration, a moved item, regrouping topics before the manifest
- [x] Scope is clearly bounded — ratings (001), persistence mechanics (002), exams (006),
  `items/source/` (survey § 8), B19 (deferred)
- [x] Dependencies and assumptions identified — spec 002 FR-016 owns the fingerprint; L needs
  additive migrations and a `SCHEMA_VERSION` bump

## Feature Readiness

- [x] Every functional requirement has an acceptance scenario or a test row of its own
- [x] Each delivery stands on its own (V, C, L); V's manifest needs no catalogue, L's retirement
  needs no manifest
- [x] Traceability: one row per FR and scenario; delivery A cites tests that exist and pass (run
  2026-10-20); open deliveries are `PENDING`

## Notes

- 2026-10-20: drafted for the owner's approval; N1 … N3 open.
