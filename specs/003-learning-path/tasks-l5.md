# Tasks — spec 003, delivery L5 (unlock rules from data only)

**Plan**: [plan-l5.md](plan-l5.md) (approved by the owner, 2026-10-19). FR-050 and FR-051 are
`[CHANGE]`; N3 (hubs) and N4 (practice not blocked by the path) apply here.

## Found while writing the tests

- The map/API agreement over every node, four progress sets and two bands already holds
  (LuisJRubioH/LevelUp-ELO#53 made the map copy the API's special case): the test is a guard for
  this refactor, not a failing `[CHANGE]` test.
- The N2 and N3 hubs complete on the server when every card is opened; the N4, A00 and S00 hubs do
  not (their completion is the browser's) — N3 closes that.
- The completion check in `lesson_event` is one rule written five times: every node requires all
  its registered interactions answered (B02, B03, the eleven-block nodes, the N2 and N3 nodes);
  B01 and B13 have none. L5 writes it once, over node data; L3 then changes «answered» to «right».

## Phase 1 — Tests first

- [x] T001 `tests/unit/domain/test_spec003_l5_path.py`: catalogue validation (one root, no
  dangling `unlock_after`/`gates`, no cycle); `node_access` from fabricated data; the old special
  cases are catalogue data (US5-AS1, US5-AS3, FR-051, N3)
- [x] T002 `tests/unit/test_architecture_layers.py::test_spec003_router_names_no_path_node`
  (FR-050, US5-AS3)
- [x] T003 `tests/integration/test_spec003_l5_map_api.py`: map ⇔ API over every node × progress ×
  band (US5-AS2, SC-003, guard); every hub completes on its cards (N3); practice topics never
  blocked (N4)

## Phase 2 — Implementation

- [ ] T004 `src/domain/learning/path.py`: `node_access`, `missing_interactions`,
  `validate_catalogue` (run at import), `CatalogueError`
- [ ] T005 Catalogue data in `prealgebra.py`: `gates` on the N3 nodes (replaces `LEVEL_GATES`),
  `requires_band` on B09, `completion: "cards"` on the five hubs; `curriculum_map_rows` and the
  summary read them
- [ ] T006 `api/routers/student.py`: every rule through the domain; no path node id left; hubs
  complete generically; practice topics not blocked
- [ ] T007 Existing pins re-run unchanged

## Phase 3 — Close

- [ ] T008 Traceability: US5-AS1 … AS3, FR-050, FR-051 filled; L5 `closed`; full suite on both
  engines, black, flake8, `check_traceability.py`
