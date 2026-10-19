# Plan — spec 003, delivery L4: what the teacher sees

**Spec**: [spec.md](spec.md) § Deliveries, L4 (US4; FR-040 … FR-042) · **Branch**:
`003-learning-path-l4`, from `redesign` after L1 and L3 · **Date**: 2026-10-19 · **Status**: for
the owner's approval

## Summary

Today `lesson_interactions` keeps **one row per interaction**: a new answer overwrites the last
one, so a wrong-then-right history is lost. The post-diagnostic outcome («avance» / «sin evidencia
de avance») is computed in the browser and never stored. No teacher screen shows any of it. L4:

- keeps every answer in order;
- stores the post-diagnostic outcome on the server;
- gives the teacher a read-only path view of each student of their groups.

## Constitution Check (1.2.0)

| Principle | L4 |
|---|---|
| Additive migrations (R8) | Two new tables; `lesson_interactions` stays as the current-answer table the completion rule (L3) reads |
| Dual database (IV, R1) | Both repositories, the D3 parity check, tests on both engines |
| Schema version (spec 002 D1) | The migration code changes, so `SCHEMA_VERSION` + 1 and a new digest |
| Minors' data (VI) | No free text: the stored value is the server-normalised choice (`selected_option`, already constrained by FR-006: option ids, or numbers and short expressions matching the item's regex) |
| Layers (III) | The outcome is computed in the domain; the repository stores rows only (R15's pattern) |

## Design

- **`lesson_answers`** (append-only):
  - columns: `id`, `user_id`, `course_id`, `node_id`, `interaction_id`, `selected_option`,
    `is_expected`, `misconception_tag`, `answered_at`;
  - one index on `(user_id, course_id, node_id)`;
  - `save_lesson_interaction` writes it in the same transaction as the current-answer row.
- **History before L4:** each existing `lesson_interactions` row is copied once, as the first
  history entry, by the migration that creates the table (its first value, as D1 did for
  `name_normalized`). History therefore starts with the last answer known before L4.
- **`lesson_outcomes`** (one row per student, course and node):
  - columns: `diagnostic_correct`, `post_correct`, `items`, `outcome` (`gain` / `flat`),
    `recorded_at`;
  - written when the last post-diagnostic item is answered;
  - `outcome` uses the domain rule the browser applies today: `gain` when post > diagnostic,
    otherwise `flat`, never «worse».
  - The browser shows the server's outcome instead of computing it.
- **Teacher endpoint:** `GET /teacher/students/{id}/path/{course}`, guarded by
  `_require_teacher_student` (the student must be in one of the teacher's groups). For each node it
  returns:
  - the state;
  - the answers in order: interaction label, right or wrong, misconception tag, time;
  - the outcome.

  It has a response model and never returns `selected_option`. The teacher sees right or wrong and
  the tag, which is what they act on (N11).
- **Teacher screen:** on the student's panel in `Dashboard.tsx`, a «Ruta de aprendizaje» section
  with one row per node and the answer history unfolded on demand. Data first, per AGENTS D3.
- The student's own summary (`/prealgebra-summary`) reads the history too: a misconception
  corrected later still shows as reviewed.

## Tests (written first; each fails on today's code)

| Test (both engines) | Proves |
|---|---|
| `tests/integration/test_spec003_l4_record.py::test_wrong_then_right_are_both_kept_in_order` | US4-AS1, FR-040 |
| `…::test_post_diagnostic_outcome_is_stored_and_shown_to_the_teacher` | US4-AS2, FR-041, FR-042 |
| `…::test_no_answer_row_holds_free_text` (every stored value is an option id or matches the item's regex) | US4-AS3, FR-006 |
| `…::test_only_the_students_teacher_reads_the_path` (another teacher 403; a student 403) | FR-042 |
| `…::test_the_migration_copies_each_last_answer_once` | history before L4 |
| D3's parity tests and D1's digest test | the schema change is on both engines and versioned |

## Owner decisions (open)

- **N11 — the teacher sees right/wrong and the tag, not the chosen value.** Recommended: **as
  stated**. The value adds little for a teacher, and it is the closest thing to the student's own
  writing. The alternative is to show the chosen option's text.
