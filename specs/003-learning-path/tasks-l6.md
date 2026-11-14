# Tasks — spec 003, delivery L6 (honest feedback and withheld steps)

**Plan**: [plan-l6.md](plan-l6.md) (proposed, 2026-11-12; awaits approval in the docs PR).
FR-060, FR-061 and FR-064 are `[CHANGE]`; FR-062, FR-063 and FR-065 are `[AS-IS]`; N12 and N13
apply here.

**Two sequences** (constitution agent rule 6): an `[AS-IS]` test is written first and **passes on
the unchanged code**; a `[CHANGE]` test is written before its implementation task and **fails**
until it. No task of Phase 2 or 3 starts before Phase 1 is green on the unchanged code.

## Found while planning

- Reordering the multiple-answer branches of `evaluate_interaction` would change the stored
  misconception tag of 3 969 of the 5 412 possible selections. L6 does not reorder: it picks the
  feedback key apart (plan § Design).
- The renderer already resolves any feedback key from the node's `content.feedback`, so FR-060
  and FR-061 need no frontend change.
- No existing test pins the key `"default"` on a multiple-answer answer.
- All 104 worked examples have five steps; the self-explanation hangs from a withheld step in 9 of
  them in «intermedio» and in 29 in «avanzado».

## Phase 1 — Pin current behaviour (blocking; every test passes on the unchanged code)

- [x] T001 [P] `tests/unit/domain/test_spec003_l6_feedback.py`:
  `test_grade_and_tag_of_every_multiple_answer_selection_are_unchanged` — a digest of
  `(interaction, selection) → (is_expected, misconception_tag)` over the 92 multiple-answer
  interactions and every selection each admits, recorded from the unchanged code (FR-062, US7-AS3)
- [x] T002 [P] same file: `test_an_interaction_with_its_own_message_keeps_it` — the C00
  icebreaker's `feedback_missing` and one `error_rules` interaction answer the keys they answer
  today (US7-AS4)
- [x] T003 [P] `frontend/e2e/spec003-l6-worked-example.spec.ts`: «básico no retiene ningún paso»;
  «intermedio retiene los dos últimos pasos y avanzado los tres últimos» (stepping with «Ver el
  siguiente paso» alone never shows them); «mostrar un paso no envía nada al servidor» (FR-063,
  FR-065, US8-AS4, US8-AS5)

**Checkpoint**: T001 … T003 green on the unchanged code; the digest of T001 is committed.

## Phase 2 — User Story 7: the lesson tells the truth about a partial answer

### Tests (each fails before T007)

- [x] T004 `tests/unit/domain/test_spec003_l6_feedback.py`:
  `test_right_options_only_but_not_all_is_told_so`,
  `test_a_selection_with_a_wrong_option_is_told_so` (one right and one wrong; one trap option)
  (FR-060, FR-061, US7-AS1, US7-AS2)
- [x] T005 same file: `test_no_right_only_selection_gets_the_message_of_a_wrong_answer` (every
  interaction × every selection), `test_every_key_a_multiple_answer_interaction_answers_has_a_text_in_its_node`,
  `test_the_shared_texts_name_no_option` (SC-004, FR-060, FR-061)
- [x] T006 `tests/integration/test_spec003_l6_feedback.py` (both engines):
  `test_the_lesson_response_carries_the_text_of_the_key_the_server_answers` (US7-AS1, US7-AS2)

### Implementation

- [x] T007 `src/domain/learning/`: the two keys and their texts in one constant; in the
  multiple-answer branch of `evaluate_interaction`, where the chosen feedback key is the fallback
  `"default"`, answer `selection_incomplete` or `selection_has_wrong`; at catalogue load, every
  node with a multiple-answer interaction carries both texts in `content["feedback"]` unless it
  declares them. `is_expected` and `misconception_tag` are not touched: T001 stays green with its
  digest unchanged

**Checkpoint**: T001, T002, T004 … T006 green.

## Phase 3 — User Story 8: think a step through before seeing it

### Tests (each fails before T009)

- [x] T008 `frontend/e2e/spec003-l6-worked-example.spec.ts`: «un paso retenido invita a pensarlo
  y se revela con su control» (in «intermedio» and in «avanzado», and no request leaves when the
  control is pressed); «la autoexplicación aparece con su paso, no antes»; «la solución espera a
  que todos los pasos estén a la vista» (FR-064, US8-AS1 … AS4, SC-005)

### Implementation

- [x] T009 `frontend/src/pages/Student/lessons/blocks/LessonBlocks.tsx` (`WorkedExample`): a
  revealed step always renders in full; when the next step is withheld, the invitation and
  «Comparar con el paso» take the place of «Ver el siguiente paso». `FADED_STEPS` is not touched.
  Style in `lessonBlocks.css` (a rule that ends in `span` names it: the guard of PR 182)
- [ ] T010 `scripts/qa/lib.js` (if PR 182 is merged): `faded-no-input` accepts the reveal control;
  `lesson_sweep.js` over the 60 nodes in «intermedio» and «avanzado» reports none
  — **open**: on 2026-11-13 PR 182 is not merged, so `scripts/qa/lib.js` is not on `main`. The
  invitation keeps the class `block-step-faded` and the control carries `data-reveal-step`, so the
  check becomes `li?.querySelector("input, textarea, select, [data-reveal-step]")`; the pull
  request that lands second makes that change

**Checkpoint**: T003 still green, unchanged; T008 green.

## Phase 4 — Traceability and verification

- [x] T011 Fill the 15 rows of § Traceability (US7-AS1 … AS4, US8-AS1 … AS5, FR-060 … FR-065)
  and mark L6 `closed`
- [x] T012 Verification: the full suite on both engines, `frontend/e2e`, `pnpm run build`,
  black, flake8, `python scripts/check_traceability.py --run`. `db_sync_check.py` and
  `validate_bank.py` do not apply: no repository and no item changes

## Dependencies

- Phase 1 blocks Phases 2 and 3.
- Phases 2 and 3 share no file and may run in parallel.
- T007 after T004 … T006; T009 after T008.

## Requirement → test task

| Requirement / scenario | Tag | Test task |
|---|---|---|
| FR-060, US7-AS1 | CHANGE | T004, T005, T006 |
| FR-061, US7-AS2 | CHANGE | T004, T005, T006 |
| FR-062, US7-AS3 | AS-IS | T001 |
| US7-AS4 | AS-IS | T002 |
| FR-063, US8-AS5 | AS-IS | T003 |
| FR-064, US8-AS1 … AS3 | CHANGE | T008 |
| FR-065, US8-AS4 | AS-IS | T003 (a plain step), T008 (a withheld step) |
| SC-004 | — | T005 |
| SC-005 | — | T008 |
