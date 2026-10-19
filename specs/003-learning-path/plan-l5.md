# Plan — spec 003, delivery L5: unlock rules from data only

**Spec**: [spec.md](spec.md) § Deliveries, L5 (US5; FR-050, FR-051; N3, N4) · **Branch**:
`003-learning-path-l5`, from `redesign` after L1 · **Date**: 2026-10-19 · **Status**: approved by the owner (2026-10-19)

## Summary

The map and the API decide «is this node open?» in two places. They agree today only because
LuisJRubioH/LevelUp-ELO#53 made the map copy the API's special case. The rules live partly in data
and partly in code:

| Rule | Where it lives today | API | Map |
|---|---|---|---|
| a node opens when its `unlock_after` is completed | data (`unlock_after`) | `_lesson_with_progress` | `curriculum_map_rows` |
| N3 needs every N2 operation node | **code** (`N3_HUB_NODE_ID`, `N3_MACHINE_NODE_IDS`, `N2_OPERATION_NODE_IDS`) | hard-coded `if` | `LEVEL_GATES` |
| B09 only for the intermediate and advanced bands | **code** (`COMPLEX_NODE_ID`) | hard-coded `if` | `complex_visible` |
| a hub completes when every card is opened | **code**, two repair functions for N2 and N3 hubs; N4/A00/S00 on the client | partly | — |
| practice topics blocked on the map until B08 | **code** (`REALS_NODE_ID`) | — (practice ignores it) | `curriculum_completed` |

L5 makes one domain function the only judge, reading only node data, and validates the catalogue
when it loads.

## Constitution Check (1.2.0)

| Principle | L5 |
|---|---|
| Layers (III) | The rule moves into `src/domain/learning/` (pure, no I/O); the router and the map call it |
| Simplicity (VII) | One function and three node fields replace five special cases |
| Content rules (V2-R11 … V2-R18) | Unchanged: authors add `unlock_after`, `gates` or `requires_band` in the node module, nothing else |

## Design

- **Node data** (in each node module, read through `_LESSONS`):
  - `unlock_after` — as today;
  - `gates: [node_id, …]` — extra prerequisites. The N3 hub and its machines get the six N2
    operation nodes; this replaces `LEVEL_GATES`;
  - `requires_band: ["intermedio", "avanzado"]` — B09;
  - `completion: "cards"` on the hubs (N3: one server rule for every hub).
- **`node_access(node_id, state_of, band) -> Access(open: bool, reason: str | None)`** in
  `src/domain/learning/path.py`. It is the only function both callers use (FR-050):
  - `_lesson_with_progress` raises 403 with `reason`;
  - `curriculum_map_rows` marks the node `blocked` when it is closed;
  - the B09 visibility on the map follows the same `requires_band`.
- **Hubs (N3):** after any card interaction is recorded, `hub_completed(node, answers)` completes
  the hub when every card's interaction exists. The two repair functions
  (`_ensure_n2_hub…`, `_ensure_n3_hub…`) become one generic call for every node with
  `completion: "cards"`, so a student who opened every card before L5 is completed on their next
  read, as today.
- **Practice on the map (N4):** the topic rows stop being `blocked` until B08; the map shows them
  `available`, with `current` on the first one not mastered, as it already does after B08.
- **Catalogue validation (FR-051):** at import, `validate_catalogue(_LESSONS)` raises if any of
  these holds:
  - there is not exactly one node without `unlock_after`;
  - an `unlock_after` or `gates` entry names a missing node;
  - the graph has a cycle.

  A unit test proves each case on a fabricated catalogue, and the real catalogue loads.
- Node ids leave `api/routers/student.py`: no `N2_*`, `N3_*` or `COMPLEX_NODE_ID` there.
  `REALS_NODE_ID` leaves the map.

## Tests (written first; each fails on today's code)

| Test | Proves |
|---|---|
| `tests/unit/domain/test_spec003_l5_path.py::test_catalogue_has_one_root_no_dangling_reference_no_cycle` + three fabricated broken catalogues | US5-AS1, FR-051 |
| `…::test_gates_and_bands_come_from_node_data` (a fabricated node with `gates` / `requires_band`, no id in code) | US5-AS3 |
| `tests/unit/test_architecture_layers.py::test_spec003_router_names_no_path_node` (AST: no `*_NODE_ID` of the path in `api/routers/student.py`) | US5-AS3, FR-050 |
| `tests/integration/test_spec003_l5_map_api.py::test_map_and_api_agree_over_every_node_and_progress_set` (both engines; every node × a set of progress states and bands: map `blocked` ⇔ API 403) | US5-AS2, FR-050, SC-003 |
| `…::test_every_hub_completes_when_its_cards_are_opened` (N2, N3, N4, A00, S00) | N3 |
| `…::test_practice_topics_are_not_blocked_by_the_path` | N4 |

## Order

L5 goes after L1, which puts access in front of the endpoints, and before L3, which extends the
completion rules L5 centralises.
