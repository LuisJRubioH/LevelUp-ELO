# Tasks — spec 003, delivery L1 (access)

**Plan**: [plan-l1.md](plan-l1.md) (approved by the owner, 2026-10-19; N10: an admin previews
every course like a teacher). FR-010 and FR-011 are `[CHANGE]`: their tests fail on the unchanged
code first; the delivery A pins stay green.

## Phase 1 — Tests first (`tests/integration/test_spec003_l1_access.py`, both engines)

- [x] T001 US1-AS1, FR-010, SC-001: a student not enrolled → 403 on lesson, event, answer,
  summary and map; nothing stored
- [x] T002 US1-AS2: an enrolled student walks the path as before; a locked node stays locked
- [x] T003 US1-AS3, FR-011, N10: a teacher of the course, and an admin, read every node and the
  map as `available`, `preview: true`; events, answers and the summary 403; nothing stored
- [x] T004 US1-AS4, FR-011: a teacher with no group in the course → 403 everywhere
- [x] T005 N6: the summary has a response model; a course without a path → 404

## Phase 2 — Implementation

- [ ] T006 `api/routers/student.py`: `_path_access` (student: `ensure_enrolled`; teacher: a group in
  the course; admin: preview; else 403) in front of the five endpoints; writes in preview 403; reads
  in preview skip the unlock rules and the hub repairs, which write
- [ ] T007 `api/schemas/student.py`: `preview` on the lesson and map responses;
  `PathSummaryResponse`
- [ ] T008 Frontend: the map and lesson routes admit teachers; a preview banner; a «Ver ruta» link
  for groups whose course has a path
- [ ] T009 Delivery A pins re-run; any pin that signed in a student not enrolled gets an
  `enroll(...)` line (listed in the PR)

## Phase 3 — Close

- [ ] T010 Traceability: US1-AS1 … AS4, FR-010, FR-011 filled; L1 `closed`; full suite on both
  engines, black, flake8, `check_traceability.py`, `pnpm run build`
