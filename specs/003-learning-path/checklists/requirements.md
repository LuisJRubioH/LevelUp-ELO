# Specification Quality Checklist: Learning Path

**Purpose**: Validate specification completeness and quality before planning (step 3)
**Created**: 2026-10-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details beyond what the brownfield needs — the requirements name behaviour
  (refusals, what a response holds, what completes a node, what is kept); file names appear only in
  the Code Scope and the "Today" notes (constitution agent rule 5)
- [x] Focused on value — "Outcome served" stated: the path only in one's courses, completion by
  understanding, the teacher sees what was learned, answers stay on the server, no free text kept
- [x] Written so the owner can decide — each change carries what happens today
- [x] All mandatory sections completed (Code Scope, Deliveries, Out of Scope, Traceability)

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — the survey's decisions and N1 … N6 were approved
  by the owner on 2026-10-18
- [x] Requirements are testable — each FR names an observable outcome (a 403 and nothing stored,
  keys absent from a response, a 409 naming items, rows kept in order, one function for map and API)
- [x] Success criteria are measurable (0 responses, 0 keys over every node, 100 % map/API agreement)
- [x] All acceptance scenarios are defined — 18 scenarios over 6 stories
- [x] Edge cases are identified — a node completed before L3, an enrolment outside the level, a
  student who leaves the course
- [x] Scope is clearly bounded — Out of Scope names content authoring (V2-R11 … V2-R18), specs 001,
  002, 008
- [x] Dependencies and assumptions identified (one course has a path today; lessons never move a
  rating)

## Feature Readiness

- [x] Every functional requirement has an acceptance scenario or a test row of its own
- [x] Each delivery stands on its own (L1 … L5), in the order the plans give
- [x] Traceability: one row per FR and scenario; delivery A cites existing tests; open deliveries
  are `PENDING`

## Notes

- 2026-10-19, while planning L2: the field list of US2-AS1 names `valid_options`, which is the list
  of choices a multiple-answer item shows, not a key; and the content holds teaching material that
  shows a right answer after an attempt (`solution`, `correct_version`) and one question graded in
  the browser (`abstraction_question.options[].correct`). Put to the owner as N7 … N9 in plan-l2.md;
  the spec is amended only after their decision.

## Amendment L6 (2026-11-12)

Checked on the L6 additions only (US7, US8, FR-060 … FR-065, SC-004, SC-005, N12, N13).

- [x] No implementation detail — the requirements name what the student is told and what is shown
  when; file names stay in the plan
- [x] Each change says what happens today (FR-060, FR-064)
- [x] No [NEEDS CLARIFICATION] marker — D1 and D2 were approved by the owner on 2026-11-12
  (§ Clarifications, session 2026-11-12)
- [x] Testable — each FR names something observable: which message an answer gets, that it names
  no option, the grade and tag of a selection, which steps are withheld, what is on screen before
  and after a step is revealed, that no request leaves
- [x] Measurable success criteria (SC-004 over every multiple-answer interaction and selection;
  SC-005 over the two presentations that withhold steps)
- [x] Every FR has a scenario or a row of its own: FR-060 ↔ US7-AS1; FR-061 ↔ US7-AS2; FR-062 ↔
  US7-AS3; FR-063 ↔ US8-AS5 and its own row; FR-064 ↔ US8-AS1 … AS3; FR-065 ↔ US8-AS4
- [x] Edge cases named — one right option, an interaction with messages of its own, a reload
- [x] Scope bounded — the default message, the node codes in texts and the presentation cut-offs
  are named as outside L6
- [x] `[AS-IS]` and `[CHANGE]` are told apart: FR-062, FR-063 and FR-065 write down what holds
  today and are pinned before any change
- [x] Traceability: 15 rows, all `PENDING` in a delivery that is `planned`
