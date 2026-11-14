# Plan — spec 003, delivery L6: honest feedback and withheld steps

**Spec**: [spec.md](spec.md) § Deliveries, L6 (US7, US8; FR-060 … FR-065; SC-004, SC-005; N12,
N13) · **Branch**: `003-learning-path-l6`, from `main` · **Date**: 2026-11-12 · **Status**:
proposed — the spec amendment is approved (owner, 2026-11-12); this plan awaits approval in the
docs PR

## Summary

Two things a tester met in the first QA round (`docs/qa/2026-11-ronda-1.md`, Q2 and Q4):

| What the student meets today | Where it comes from | L6 |
|---|---|---|
| One right option of two marked → «Todavía no. Revisa el procedimiento…» | Of the 92 multiple-answer interactions, 84 go through `_register_mixed_interactions`, where `feedback_missing`, `feedback_incorrect` and `feedback_trap` default to `"default"`: the 52 abstraction questions and 31 practice questions define none of them, and the C00 icebreaker only the first. «Incomplete» and «holds a wrong option» both get the node's `feedback.default` | Two shared messages; grade and tag untouched |
| «Complétalo tú» with nothing to complete | `WorkedExample` renders a withheld step as a text, with no control (`LessonBlocks.tsx`); the self-explanation prompt and the solution show regardless | Think, then reveal |

## Constitution Check (1.2.0)

| Principle | L6 |
|---|---|
| The spec is the contract (I) | Both behaviours arrive as `[CHANGE]` requirements (FR-060, FR-061, FR-064) before any code; what must not move is pinned first (FR-062, FR-063, FR-065) |
| Layers (III, R2) | The messages and the rule that picks one live in `src/domain/learning/`; the router and the renderer are not told about them |
| Dual DB (R1) | No repository, table or migration is touched |
| Brownfield safety (rule 6) | A pin over every multiple-answer selection passes on the unchanged code and must pass unchanged after |
| Simplicity (VII) | One rule and two texts for 84 interactions; one branch in one component for 104 worked examples |
| Content rules (V2-R11 … V2-R18) | Unchanged. An author may still give an interaction its own message; it wins |

## Design

### Feedback (FR-060 … FR-062)

- **What does not change.** `evaluate_interaction` keeps deciding `is_expected` and
  `misconception_tag` exactly as today, branch by branch (trap → missing → incorrect).
- **Do not reorder the branches.** Putting «holds a wrong option» before «misses a right one»
  looks like the natural fix and is wrong: measured over the 84 interactions and their 5 412
  possible selections, it changes the stored misconception tag of 3 969 of them. The teacher's
  record (FR-040, N11) must not move.
- **What changes: only the message, chosen apart.** When the branch's own feedback key is the
  fallback `"default"` — the interaction defined none for that case — the key becomes:
  - `selection_incomplete` if the selection holds right options only;
  - `selection_has_wrong` if it holds any option that is not right (a trap option included).

  An interaction that defines its own key for the case keeps it (US7-AS4): the eight with
  `error_rules` and the C00 icebreaker's `feedback_missing`.
- **One place for the two texts.** A constant in `src/domain/learning/` maps the two keys to their
  text. At catalogue load, every node that has a multiple-answer interaction gets both entries in
  its `content["feedback"]` unless it declares them. `feedback` is already an opaque, public field
  (`public_content.OPAQUE_PATHS`), and the renderer already resolves any key
  (`feedbackText` in `ElevenBlockLesson.tsx`): **no frontend change for FR-060 and FR-061**.
- **Texts** (D1, approved; the second was made neutral so it also reads right on a practice
  question, which has no «cases above»):
  - `selection_incomplete`: «Vas bien: lo que marcaste es correcto, pero falta al menos una
    opción más.»
  - `selection_has_wrong`: «Al menos una de las opciones que marcaste no es correcta. Revísalas
    una por una.»

### Withheld steps (FR-063 … FR-065)

`WorkedExample` already reveals one step per click («Ver el siguiente paso (n / 5)») and already
counts the last `faded` steps as withheld. L6 changes what a withheld step is:

- The steps already revealed are always rendered in full; «Complétalo tú» disappears.
- When the next step is withheld, the place of «Ver el siguiente paso» is taken by an invitation
  — «Tu turno: piensa este paso antes de verlo.» — and a control «Comparar con el paso».
  Pressing it reveals that step.
- The self-explanation prompt renders with its step, so it cannot precede it; the solution keeps
  its condition (every step shown), which is now reachable honestly.
- Local state only, as today: no request, nothing stored (FR-065, FR-006).
- `FADED_STEPS` (0, 2, 3) is not touched (FR-063).

All 104 worked examples have five steps, so a withheld step always follows at least two shown.

## Tests

`[AS-IS]` — written first; they pass on the unchanged code and must still pass, unchanged, at the
end:

| Test | Proves |
|---|---|
| `tests/unit/domain/test_spec003_l6_feedback.py::test_grade_and_tag_of_every_multiple_answer_selection_are_unchanged` — a digest of `(interaction, selection) → (is_expected, misconception_tag)` over every multiple-answer interaction and every selection, recorded from the unchanged code | FR-062, US7-AS3 |
| `…::test_an_interaction_with_its_own_message_keeps_it` (the C00 icebreaker, one `error_rules` interaction) | US7-AS4 |
| `frontend/e2e/spec003-l6-worked-example.spec.ts › básico no retiene ningún paso` | FR-063, US8-AS5 |
| `… › intermedio retiene los dos últimos pasos y avanzado los tres últimos` (stepping with «Ver el siguiente paso» alone never shows them) | FR-063 |
| `… › mostrar un paso no envía nada al servidor` | FR-065, US8-AS4 |

`[CHANGE]` — each fails on the unchanged code:

| Test | Proves |
|---|---|
| `tests/unit/domain/test_spec003_l6_feedback.py::test_right_options_only_but_not_all_is_told_so` (B04's abstraction question, one right option → `selection_incomplete`) | FR-060, US7-AS1 |
| `…::test_a_selection_with_a_wrong_option_is_told_so` (one right and one wrong; one trap option) | FR-061, US7-AS2 |
| `…::test_no_right_only_selection_gets_the_message_of_a_wrong_answer` (every interaction × every selection: right-only and incomplete never resolves to the node's `default` text) | SC-004 |
| `…::test_every_key_a_multiple_answer_interaction_answers_has_a_text_in_its_node` and `…::test_the_shared_texts_name_no_option` | FR-060, FR-061 |
| `tests/integration/test_spec003_l6_feedback.py::test_the_lesson_response_carries_the_text_of_the_key_the_server_answers` (both engines: answer through `/interactions`, read the text from the lesson's `content.feedback`) | US7-AS1, US7-AS2 |
| `frontend/e2e/spec003-l6-worked-example.spec.ts › un paso retenido invita a pensarlo y se revela con su control` | FR-064, US8-AS1, SC-005 |
| `… › la autoexplicación aparece con su paso, no antes` | FR-064, US8-AS2 |
| `… › la solución espera a que todos los pasos estén a la vista` | FR-064, US8-AS3 |

`scripts/qa/lesson_sweep.js` (PR 182) reports `faded-no-input` in all 52 eleven-block nodes today;
its check is updated to accept the reveal control and must report none after L6. It is a QA tool,
not a traceability row.

## Risks and what was checked

- **No existing test pins `"default"` on a multiple-answer answer** (searched `tests/`); the
  e2e fixtures answer `"default"` from a mocked API and keep working.
- **`test_feedback_is_unchanged_after_the_keys_leave`** (US2-AS2) compares the API with the
  domain, not with a fixed key: it holds.
- **The teacher's history** shows right or wrong and the tag, never a feedback key: unchanged.
- **Depends on PR 182 only for the sweep check**; the code of L6 does not need it.

## Order

1. This docs PR (spec + plan + tasks).
2. Code PR: the pins, then feedback (domain only), then the worked example (frontend only). The
   two halves share no file and may be done in either order after the pins.
