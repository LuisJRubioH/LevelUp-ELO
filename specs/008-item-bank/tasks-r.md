# Tasks — spec 008, delivery R (items reserved for templates)

**Plan**: [plan-r.md](plan-r.md). FR-035 and FR-036 are `[CHANGE]`. The L pins (retired items)
stay green throughout.

## Phase 1 — Tests first

- [x] T001 [US6-AS3, FR-035] `tests/integration/test_spec008_r_reserved.py::test_spec008_r_a_reserved_item_is_stamped_and_released`
  (both engines). Fails on the unchanged code.
- [x] T002 [US6-AS1, FR-035] `…::test_spec008_r_practice_never_serves_a_reserved_item`: the item
  read by course, block and topic, the block counts and adaptive practice. Fails on the unchanged
  code.
- [x] T003 [US6-AS1, FR-035] `…::test_spec008_r_exams_and_the_diagnostic_skip_a_reserved_item`.
  Fails on the unchanged code.
- [x] T004 [US6-AS2, FR-035] `…::test_spec008_r_a_template_serves_a_reserved_item`: the
  catalogue, creation, edit and a student's start. Passes on the unchanged code; guards that R
  leaves templates working.
- [x] T005 [FR-036] `tests/unit/scripts/test_validate_bank.py::test_spec008_r_reserved_must_be_a_boolean`
  and `…::test_spec008_r_reserved_items_do_not_count_for_a_small_topic`. Fail on the unchanged
  code.

## Phase 2 — Implementation

- [x] T006 [FR-035] Both repositories: `_add_item_reserved` (additive `items.reserved_at`);
  `SCHEMA_VERSION` 10 and `MIGRATION_SOURCES_DIGEST`; `BANK_SYNC_FORMAT` 3.
- [x] T007 [FR-035] Both repositories: the sync stamps and clears `reserved_at`;
  `get_items_from_db(..., include_reserved=False)`; `get_course_blocks` leaves reserved items out;
  the interface's signature.
- [x] T008 [FR-035] The template paths pass `include_reserved=True` (`api/routers/teacher.py`,
  `_items_from_template`).
- [x] T009 [FR-036] `scripts/validate_bank.py`.
- [x] T010 `AGENTS.md`: the items table and «Reserving» under the item's life.

## Phase 3 — Close

- [x] T011 Traceability: US6-AS1 … US6-AS3, FR-035 and FR-036 filled; R `closed`. Checks: the
  suite on both engines, `db_sync_check.py`, `validate_bank.py`, `build_epa8_bank.py --check`,
  `check_traceability.py`, black (CI's version) and flake8.
