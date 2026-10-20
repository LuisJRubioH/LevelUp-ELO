# Specification Quality Checklist: PvP League

**Purpose**: Validate specification completeness and quality before planning (step 3)
**Created**: 2026-10-20
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details beyond what the brownfield needs — requirements name behaviour (who
  may enter, who meets whom, what an answer or a close may do, what the screen shows); file names
  appear only in the Code Scope and the plans
- [x] Focused on value — "Outcome served" stated
- [x] Written so the owner can decide — each change cites the owner's decision (D1 … D11) and its
  survey finding
- [x] All mandatory sections completed (Code Scope, Deliveries, Out of Scope, Traceability)

## Requirement Completeness

- [x] Every survey decision is decided — D1 … D11 taken by the owner on 2026-10-20 (survey § 8)
- [x] Open points resolved — O1 (the institution is a first-class concept owned by spec 009), O2
  (the starting numbers) and O3 (the speed tiebreak) decided by the owner on 2026-10-20; V11, V17,
  V23 and V24 decided the same day (FR-061, FR-052, FR-070, FR-024/FR-033)
- [x] Requirements are testable — each FR names an observable outcome (a socket refused, two
  students never matched, a match played unrated, a countdown to the server's end time, a forfeit
  after 20 s, a frame not processed)
- [x] Success criteria are measurable (0 rated matches across the access rules, 0 pairs over the
  cap, 0 deltas rounded in the browser, 0 orphans older than 15 minutes)
- [x] All acceptance scenarios are defined — 20 scenarios over 7 stories
- [x] Edge cases are identified — a floored rating, a tie on time, a late return, the daily cap, a
  restart during the grace
- [x] Scope is clearly bounded — rating formulas (001), identity (004), item contents (008),
  institutions (009), the olympiad itself (a future spec)
- [x] Dependencies and assumptions identified — the spec 001 amendment for D1 (approved) ships
  with delivery G; institution and grade come from spec 009 and must exist before G

## Feature Readiness

- [x] Every functional requirement has an acceptance scenario or a test row of its own
- [x] Each delivery stands on its own (G, M, F, L, H, S); M's window and F's tiebreak need no other
  open delivery; G waits on spec 009's institution
- [x] Traceability: one row per FR and scenario; delivery A cites tests that exist and pass on both
  engines (159 pytest and 4 Playwright, run 2026-10-20); open deliveries are `PENDING`

## Notes

- 2026-10-20: drafted from the owner's decisions; awaits the owner's approval and O1 … O3.
- 2026-10-20 (second round): O1 … O3, the spec 001 amendment and V11, V17, V23, V24 decided by the
  owner; delivery S added.
