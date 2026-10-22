# PROMPT — Enrich the 5 remaining N4 Divisibility nodes (C02–C06)

> Student-facing content stays in Spanish (es-CO); this prompt only governs structure, rules and checks.

## Goal

**C01 Divisibility** is already the reference node (pilot), complete and verified end to
end: rich content + `LevelFourLesson.tsx`/`.css` + routing + map wiring + tests. The other
5 concepts (**C02 Multiples, C03 Primes, C04 Prime factorization, C05 GCD, C06 LCM**) currently have
minimum viable content (`"validation_status": "F4_TODO_stub"` in `prealgebra.py`) — curricularly
correct but without C01's richness (fewer examples, less practice, no variety of contexts).
This document is the template for bringing them to the same level, replicating C01 node by node.

## What is ALREADY built — DO NOT redo (reuse as-is)

- **Backend evaluation engine**: `evaluate_interaction()` in `src/domain/learning/prealgebra.py`
  already supports the 3 types N4 needs (`numeric`, `single_select`, `multi_select`) — **do not touch
  that function**.
- **Mixed interaction registrar**: `_register_mixed_interactions(node_id, concept_slug,
  items)` (defined right before `_N4_CARDS` in `prealgebra.py`). It walks a list of items
  `{"id", "kind", ...}` and generates both `_LESSONS[node_id]["interactions"]` and
  `_INTERACTION_RULES[...]`. It is already used for the hub icebreaker and for each concept's
  `practice` — reuse it, do not rewrite it.
- **Frontend renderer**: `frontend/src/pages/Student/lessons/LevelFourLesson.tsx` +
  `LevelFourLesson.css`. It detects `content.kind === "level_hub_port"` (hub) vs any other value
  (concept) and automatically renders: `KatiaStorySlot` → `[discovery | formal definition]`
  (`.set-story`/`.set-formal`) → worked examples in 2 columns + wide trap
  (`.n2-examples-2col`/`.n2-example-wide`, reused from N2) → formalization box
  (`.n4-formalization`) → mixed practice (`PracticeItem`, switch on `item.kind`) → closing → footer.
  **The work for C02–C06 is ONLY content**: edit
  `_N4_CONCEPT_CONTENT[<NODE_ID>]` in `prealgebra.py`, copying the EXACT shape of
  `N4_DIVISIBILITY_NODE_ID` (C01) as the template.
- **Routing and map**: `N4_IDS` in `Lesson.tsx`, sequential insertion into `course_map`
  (`api/routers/student.py`) — the 7 nodes are already wired. There is no need to touch them when
  enriching content (only if a new node is added, which does not apply here).

## Structure to put in each dict (same as C01)

```python
N4_XXX_NODE_ID: {
    "kind": "divisibility_concept",
    "concept_id": "C0N",
    "concept_slug": "...",                      # used in default_misconception: error_<slug>
    "title": "...",
    "story_contract": {"type": "guided_discovery_formalization",
                        "practice_position": "after_definition_plus_examples", "is_integrated": True},
    "katia": {"eyebrow", "title", "body", "question"},       # opening + problem-posing question
    "discovery": {"eyebrow", "title", "body"},                # guided discovery
    "definition": "...", "definition_title": "...", "definition_katex": r"...",
    "worked_examples": [ ...N normal..., {"trap": True, ...} ],  # 2-3 normal + 1 trap
    "formalization": {"title", "intro", "items": [{"label", "rule", "latex"?}, ...]},
    "practice": [                                              # 6-9 items, MIXED types
        {"id": "Q1", "kind": "numeric", "prompt": "...", "expr": r"...", "answer": "..."},
        {"id": "Q2", "kind": "single_select", "prompt": "...",
         "options": [{"id": "a", "text": "..."}, ...], "expected": "a",
         "feedback_by_option": {"a": "correct", "b": "fb_xxx_q2_b", ...},
         "misconception_by_option": {"b": "..."}},
        {"id": "Q3", "kind": "multi_select", "prompt": "...",
         "valid_options": ["...", ...], "expected": ["...", ...], "trap_options": ["...", ...],
         "feedback_correct": "correct", "feedback_trap": "fb_xxx_q3_trap",
         "misconception_trap": "...", "feedback_missing": "fb_xxx_q3_missing",
         "misconception_missing": "...", "feedback_incorrect": "default",
         "misconception_incorrect": "error_<slug>"},
    ],
    "feedback": {"correct": "...", "default": "...", "fb_xxx_qN_x": "...", ...},  # EVERY key used above
    "closing": "...",
    "validation_status": "F4_C0N_pilot",   # change from F4_TODO_stub when done
}
```

**IMPORTANT — bug already fixed, do not reintroduce**: `valid_options`/`expected`/`trap_options` in
`multi_select` must be **lists** (`[...]`), NEVER sets (`{...}`) — they live inside `content`,
which travels to the frontend as JSON, and a Python `set` does not serialize deterministically.
`_register_mixed_interactions` already converts the list to a `set()` internally for the backend
rules; the frontend only needs the list.

## NON-negotiable rules

1. **Setting = the Port of the Polis, but only as a backdrop.** KatIA is the port's
   official/herald (docks, ships, amphorae, routes to Athens/Corinth/Delos/
   Miletus/Rhodes/Sparta) — use it in each node's opening (`katia`), but **DO NOT force every
   example and every practice item to be "ships and amphorae"**. That was the user's explicit
   correction on N3 ("as if nothing else existed in ancient Greece").
2. **Varied context bank — no object repeats more than 2 times across the WHOLE level** (7
   nodes, counting C01 too). Contexts already used in C01: candies, marbles, fair tickets,
   wheat sacks, oars, oil amphorae. For C02–C06 use new variety: orchards/rows of trees, farm
   animals, musical instruments, coins/fair tickets (if not repeated from C01), school
   supplies, distances/runners, towers/blocks. Before writing an example, check which objects
   already appeared in the previous nodes.
3. **Specific, actionable feedback, never a bare "correct/incorrect".** Each incorrect option
   of a `single_select`/`multi_select` needs its own entry in `feedback_by_option` /
   `feedback_trap`/`feedback_missing` explaining **why** it is wrong (see C01's `fb_c01_qN_x`
   as an example).
4. **The trap (`trap: True`) is a real conceptual error**, not a slip — in C01 it was "even ⇏
   divisible by 4"; follow the same criterion (a counterexample that refutes a hasty
   generalization).
5. **Explicit LaTeX that compiles in KaTeX**: `\dfrac`, `\sqrt`, `\times`, `\div`, `\mathbb{}`,
   es-CO decimal comma wrapped in braces (`2{,}5`) where applicable. Check for 0 `.katex-error`
   in the real render.
6. **Practice with typeable numeric answers**: the backend validates `numeric` with the regex
   `-?\d{1,6}(,\d{1,4})?` — only integers or decimals with ≤4 decimal digits, never repeating
   decimals.

## Mapping from the source document to each node

| Node | Page in the original `.md` | Content to expand |
|---|---|---|
| **C02 Multiples** | Page 3 · CONCEPTO 2 | Already has 1 example (tower of blocks) + 1 trap + 1 multi_select practice item. Add: the full "runner" example (2, 3, 4, 6 and 9 hours) as extra numeric situations, more practice (min. 6-8 items); the formalization already has the doc's 4 properties — check that they are complete. |
| **C03 Primes** | Page 4 · CONCEPTO 3 | Already has 1 example + trap (the number 1) + 1 multi_select. Add: the doc's "count the divisors" activity for several numbers (7, 12, 1, 11) as numeric practice, more examples with varied primes/composites (not only the doc's), formalization with the fundamental theorem already present. |
| **C04 Prime factorization** | Page 5 · CONCEPTO 5 (doc) | Already has 1 example (84) + 1 trap (36). Add: model the doc's "successive division" (64, 81, 125, 630, 72, 1200) as **one numeric interaction per step** (see note below), plus "ways to break it down" practice as multi_select (36, 90 and 128 from the doc already have their correct/incorrect options ready). |
| **C05 GCD** | Page 6 · CONCEPTO 5 (doc, misnumbered as 5 again) | Already has 1 example (225, 180) + trap. Add: the doc's table of pairs (24-36, 45-60, 28-42, 54-72, 120-180, 144-216) as `single_select` practice (pick the correct GCD from options) or `numeric`, plus the Euclidean algorithm as an explicit method in the formalization (already listed). |
| **C06 LCM** | Page 7 · CONCEPTO 6 | Already has 1 example (20, 30) + trap. Add: the doc's table of pairs (16-24, 21-35, 28-40, 36-54, 132-180, 154-231) as practice, plus the relation GCD×LCM=a×b as an application question. |

**Successive decomposition (C04/C05/C06) — how to model it without a new widget**: each
division step (e.g. `630÷2=315`, `315÷3=105`, ...) is **an independent `numeric` interaction**
inside `practice`, with its own `id` (Q1, Q2, Q3...) and a `prompt` saying which step it is.
They are shown as a normal vertical list (reuse `.n4-practice-item`, no tree component).
There is no need to show every step in a single interactive card — the worked example
(`worked_examples`) already shows the full sequence with `steps`; the practice can ask for 1-2
individual steps or the final result.

## Verification (required per node, same as was done for C01)

1. `python -c "import src.domain.learning.prealgebra"` — loads without errors.
2. `python -c "import json; from src.domain.learning.prealgebra import get_lesson, N4_XXX_NODE_ID; json.dumps(get_lesson(N4_XXX_NODE_ID)['content'])"` — confirms no `set()` slipped into `content`.
3. `python -m pytest tests/unit/domain/test_prealgebra_lessons.py -q` — must not break anything that exists (add a case analogous to `test_n4_divisibility_mixed_interactions` per node if new interaction types are added).
4. `cd frontend && ./node_modules/.bin/tsc --noEmit` — no errors (types should not change at all, only content).
5. Restart the backend **without** `--reload` to load the new content.
6. Manual walk-through via the API (as was done with C01): login → `GET /api/student/lessons/algebra_basica/<NODE_ID>` → `POST .../interactions` for each `practice` item → `POST .../events {"event":"node_completed"}` → confirm that the next node becomes `"available"` in `GET /api/student/map/algebra_basica`. Afterwards, clean up the test rows in `lesson_progress`/`lesson_interactions` if a shared demo account was used.
7. Change `"validation_status"` from `"F4_TODO_stub"` to `"F4_C0N_pilot"` (or similar) when each node is done.

## Suggested order

C02 Multiples → C03 Primes → C04 Prime factorization → C05 GCD → C06 LCM.

Reason: Multiples and Primes are the closest in shape to C01 (criteria/simple definition);
Factorization, GCD and LCM share the "successive decomposition" pattern and are best done
together at the end, once the pattern of sequential numeric steps is refined.
