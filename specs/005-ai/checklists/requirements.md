# Specification Quality Checklist: AI Integration

**Purpose**: Validate specification completeness and quality before planning (step 3)
**Created**: 2026-10-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details beyond what the brownfield needs — the requirements name behaviour
  (which provider is called, what a prompt holds, what a reply may say, what is kept); file names
  appear only in the Code Scope and the "Today" notes (constitution agent rule 5)
- [x] Focused on value — "Outcome served" stated: KatIA guides without giving the answer, a key
  reaches its provider, the teacher learns where a student got, no AI output moves a rating
- [x] Written so the owner can decide — each change carries what happens today
- [x] All mandatory sections completed (Code Scope, Deliveries, Out of Scope, Traceability)

## Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain, and every "Proposed" decision is decided — **N1 … N4
  wait for the owner** (sentence limit, the kinds of difficulty, the old `katia_interactions`
  texts, a student's own key)
- [x] Requirements are testable — each FR names an observable outcome (the provider and model a
  provider double receives, a prompt without the answer, a replaced reply not stored, a 403 with no
  provider call, no text left after closing)
- [x] Success criteria are measurable (0 prompts with the answer, 0 leaked replies, 0 responses with
  exception text, 0 texts older than 24 h)
- [x] All acceptance scenarios are defined — 13 scenarios over 5 stories
- [x] Edge cases are identified — unknown prefix, a second conversation on an answered item, an
  unclassifiable difficulty, conversations from before K3
- [x] Scope is clearly bounded — Out of Scope names ratings (001), uploads (001 block 7), grading
  (006), V1's AI code (F-10), other vision providers
- [x] Dependencies and assumptions identified (Groq in production; V1 retired; no AI output moves a
  rating)

## Feature Readiness

- [x] Every functional requirement has an acceptance scenario or a test row of its own
- [x] Each delivery stands on its own (K1 … K4), in the order the plans give
- [x] Traceability: one row per FR and scenario; delivery A cites existing tests; open deliveries
  are `PENDING`

## Notes

- The one open item is the owner's decision on N1 … N4; the plans assume the proposals and say
  where each one lands.
