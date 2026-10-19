# Plan — spec 003, delivery L3: a node completes on right answers

**Spec**: [spec.md](spec.md) § Deliveries, L3 (US3; FR-030; N1, N2) · **Branch**:
`003-learning-path-l3`, from `redesign` after L5 · **Date**: 2026-10-19 · **Status**: for the
owner's approval

## Summary

Today `node_completed` is accepted when every required interaction has an answer, right or wrong.
The check is spread over four branches of `lesson_event`, two of them with hard-coded node ids, and
the refusal always reads «Responde las dos preguntas primero». L3 adds one domain rule beside L5's
`node_access`, and the refusal names what is missing:

| Node | Completes when | Decision |
|---|---|---|
| B01 (welcome) | it is viewed | N1 (as today) |
| B13 (closing diagnostic) | every item has an answer, right or wrong | N2 |
| hubs | every card is opened | N3, L5 |
| every other node | the **latest** answer of every required interaction is right | FR-030 |

Required interactions are those in the node's `interactions` list, as today. Under V2-R11 the
mini-diagnostic, the bridge and the post-diagnostic are registered `required=False`, so a
diagnostic never gates.

## Constitution Check (1.2.0)

| Principle | L3 |
|---|---|
| Layers (III) | `completion_gaps(node, answers) -> list[str]` is pure domain; the router only reads answers and calls it |
| Validation and errors | A 409 whose `detail` names the items still missing, in the order the student sees them |
| No rating change (FR-001) | Unchanged: completion writes `lesson_progress` only |

## Design

- **`completion_gaps(lesson, latest_answers) -> list[Gap]`** in `src/domain/learning/path.py`.
  - The rule depends on `lesson["completion"]`, a node field with four values: `view` (B01),
    `answered` (B13), `cards` (hubs, from L5) and `correct`, the default.
  - A `Gap` carries the interaction id and a label for the student, built from the item's place in
    the content: «Práctica 2», «Cierre», «Pregunta 1». No `prompt` text is copied.
- **`lesson_event`:** its four `if` branches become one call. When there are gaps, the response is:

  ```
  409 {"detail": "Te falta acertar: Práctica 2 y Cierre.", "missing": ["…-E2", "…-C1"]}
  ```

  B13's message is «Te falta responder: …».
- **The frontend:** `ElevenBlockLesson` already asks for completion only when `allResolved` holds;
  it now shows the 409's `detail` instead of a generic message. Retrying an item is already
  possible (`can_retry`), and the latest answer counts (US3-AS3).
- **Nodes completed before L3:** they stay completed. `lesson_progress` never moves back (FR-004),
  and L3 only gates the `node_completed` event.

## Tests (written first; each fails on today's code)

| Test (both engines) | Proves |
|---|---|
| `tests/integration/test_spec003_l3_completion.py::test_one_wrong_required_answer_refuses_naming_it` | US3-AS1, FR-030 |
| `…::test_all_latest_answers_right_completes_and_opens_the_next` | US3-AS2 |
| `…::test_a_wrong_answer_corrected_lets_the_node_complete` | US3-AS3 |
| `…::test_welcome_completes_on_view_and_closing_on_answers_right_or_wrong` | N1, N2 |
| `…::test_a_node_completed_before_l3_stays_completed` | spec edge case |
| `tests/unit/domain/test_spec003_l3_completion.py::test_diagnostic_items_never_gate` (over every eleven-block node: no `required=False` interaction is in a gap) | V2-R11 kept |
