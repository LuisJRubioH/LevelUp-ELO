# Plan — spec 006, delivery X2: templates and results

**Spec**: [spec.md](spec.md) § Deliveries, X2 (US3; FR-030 … FR-033) · **Branch**: `006-x2`, from
`redesign` after X1 · **Date**: 2026-10-19 · **Status**: draft for the owner (depends on N2, N4,
N5)

## Summary

A template is public to the whole course the moment it exists, edits change items already
answered, an assignment can mix courses and half-commit, and results count everybody's every
attempt with no per-student view. X2 makes templates drafts until assigned, locks them once
started, and computes results over the teacher's students' first submissions.

## Constitution Check (1.2.0)

| Principle | X2 |
|---|---|
| Additive migrations (R8), dual database (IV, R1) | `exam_responses.selected_option` (TEXT, NULL for rows before X2) on both engines; `SCHEMA_VERSION` + 1 with its digest; `docs/transfer.md` § 5 updated |
| Layers (III) | the «first submission» rule and the results arithmetic in the domain; the repository returns rows |

## Design

- **Draft (FR-030):** the visibility query (both engines) drops the «no assignment → whole course»
  branch; the teacher screen marks unassigned templates «Borrador».
- **Lock (FR-031):** `PATCH` changing `item_ids` answers 409 when any `active_exam_sessions` or
  `exam_sessions` row names the template; the title and time limit stay editable; a «Duplicar»
  action creates a copy.
- **Assignment (FR-032):** the group's course must equal the template's (422 otherwise); all groups
  in one transaction (`assign_template_to_groups`, both engines).
- **Results (FR-033):** a domain function over rows of the teacher's student set (spec 006 C1's
  rule, or today's dashboard set until C1), first `exam_sessions` row per student; per item:
  right, wrong, chosen option; per student: score. The chosen option is stored at submit.

## Tests (written first)

| Test (both engines) | Proves |
|---|---|
| `tests/integration/test_spec006_x2_templates.py::test_an_unassigned_template_is_a_draft` | US3-AS3, FR-030 |
| `…::test_a_started_template_cannot_change_its_items` | US3-AS2, FR-031 |
| `…::test_an_assignment_is_one_course_and_all_or_nothing` | FR-032 |
| `…::test_results_count_my_students_first_submission` (other teacher's student, a retake, a teacher's session) | US3-AS1, FR-033 |
| `tests/unit/domain/test_spec006_exam_results.py` | FR-033 |
| D1's digest test and D3's parity tests | the column on both engines |
