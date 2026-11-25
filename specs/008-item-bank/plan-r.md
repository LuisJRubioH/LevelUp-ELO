# Plan — spec 008, delivery R: items reserved for templates

**Spec**: [spec.md](spec.md) § Deliveries, R (US6-AS1 … US6-AS3; FR-035, FR-036) · **Branch**:
`claude/dazzling-mendel-uta2jw` · **Date**: 2026-11-25 · **Status**: for the owner's approval (the
decision is the user's, 2026-11-25: the olympiad's tests use unseen questions)

## Summary

Every bank item is served everywhere: practice, the diagnostic, standard exams, PvP. The 2027
municipal olympiad needs unseen questions for its tests, kept in the same bank (one validator, one
manifest, one sync) but reachable only through a teacher's template.

## Constitution Check (1.2.0)

| Principle | R |
|---|---|
| Migrations additive (R8) | one nullable column, `items.reserved_at`, by `_add_item_reserved` on both engines; `SCHEMA_VERSION` 10 with its digest recorded |
| Dual database (R1) | the column, the sync and the item read change on both engines; `db_sync_check.py`, `test_spec002_d3_parity.py` |
| Bank fingerprint | `BANK_SYNC_FORMAT` 3: every database resyncs once after the deploy and stamps the marks |
| One serving read | `get_items_from_db` stays the read every serving path shares; reserved items are left out unless `include_reserved=True`, which only the template paths pass |
| Tests first (VII) | the stamping, practice, exam and diagnostic tests and the validator's fail on the unchanged code; the template test pins what R must keep working |

## Design

- **Mark.** `"reserved": true` in a bank item, a JSON boolean (validator). Like `retired`, the sync
  stamps `reserved_at` the first time and clears it when the mark goes or turns `false`.
- **Serving.** `get_items_from_db(topic, course_id, block, include_reserved=False)` adds
  `AND reserved_at IS NULL` unless asked; `get_course_blocks` always leaves reserved items out.
  Practice, the diagnostic, standard exams, PvP, the map and V1 call it without the flag.
- **Templates.** The teacher's item catalogue, template creation and edit, and
  `_items_from_template` (a student's start) pass `include_reserved=True`.
- **Validator.** `reserved` must be a boolean; a reserved item does not count for a topic's
  small-topic warning, since nobody practises it.

## Out of scope

- Who may see reserved items: today any teacher can build a template from any course. The
  read-only accounts the user chose for the other institutions' teachers (adjustment 7) close that.
- The olympiad's courses and their bank content (adjustment 4).
