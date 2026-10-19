# Plan — spec 003, delivery L2: answer keys stay on the server

**Spec**: [spec.md](spec.md) § Deliveries, L2 (US2; FR-020; N5) · **Branch**:
`003-learning-path-l2`, from `redesign` · **Date**: 2026-10-19 · **Status**: approved by the owner (2026-10-19)

## Summary

`GET /lessons/{course}/{node}` returns the node's whole `content`, grading keys included. All
grading already happens on the server (`evaluate_interaction`, FR-003). The browser therefore
receives keys it does not need, and anyone can read them in the network tab.

L2 strips those keys from the response. It first needed a field-by-field reading of what the
content holds; this was measured over the 60 nodes of the catalogue on 2026-10-19.

| Field (path in `content`) | Occurrences | What it is | L2 |
|---|---|---|---|
| `practice[].expected`, `diagnostic.items[].expected`, `post_diagnostic.items[].expected`, `icebreaker.items[].expected` | 411 | the right answer | **removed** |
| `…[].answer` (practice, diagnostic, post, icebreaker) | 280 | the right answer (typed items) | **removed** |
| `practice[].accepted` | 4 | accepted alternatives | **removed** |
| `bridge.items[].blanks[].answer` | 212 | the right value of each blank | **removed** (the client uses only `id` and `label`) |
| `closing_item.answer` | 52 | the closing item's answer | **removed** |
| `…[].misconception_by_option` | 384 | the error each option reveals: marks the wrong ones | **removed** (the server returns the tag with the grade) |
| `…[].feedback_by_option` | 197 | the feedback text per option | **removed**; the server's grade already carries `feedback_key` |
| `…[].trap_options` | 32 | which options are traps | **removed** |
| `…[].valid_options` | 32 | **the list of choices** of a multiple-answer item — `PracticeItem` renders it | **kept** (N7) |
| `worked_examples[].solution` | 156 | the worked example's solution, shown in steps as teaching | **kept** (N8) |
| `worked_examples[].correct_version` | 52 | the trap card's right version, shown after the student commits | **kept** (N8) |
| `abstraction_question.options[].correct` | 199 | a closing question **graded in the browser** | N9 |
| `feedback.correct` | 57 | the text shown on a right answer, not a key | kept |

## Constitution Check (1.2.0)

| Principle | L2 |
|---|---|
| Security (VI) | An allow-list projection: a field reaches the browser only when the projection names it, so a key added later is left out by default |
| Layers (III) | `public_content(content)` is pure domain, in `src/domain/learning/`; the router applies it |
| Content rules | Node modules are unchanged; the server keeps every key for grading |

## Design

- **`public_content(content) -> dict`**, an allow-list per block kind. It copies the fields the
  renderer reads and nothing else. Which fields those are is read from `LessonBlocks.tsx` and
  `ElevenBlockLesson.tsx` and fixed in the function's test.
- **`lesson_detail` and `lesson_event`** return `public_content(...)`.
- **N5:** the three unreachable renderers (`LevelTwoOperation`, `LevelThreeMachine`,
  `LevelFourConcept`) are removed. They are the only code that shows «Resultado esperado:
  {answer}». The TypeScript types lose `answer` and `expected` (`LessonBlocks.tsx:51-54`).
- **The response to a graded answer** stays as it is (`is_expected`, `misconception_tag`,
  `feedback_key`), so the student sees the same feedback (US2-AS2).

## Tests (written first; each fails on today's code)

| Test | Proves |
|---|---|
| `tests/integration/test_spec003_l2_keys.py::test_no_lesson_response_holds_a_grading_key` (every node of the catalogue, both engines; recursive search for every removed field name) | US2-AS1, FR-020, SC-002 |
| `…::test_feedback_is_unchanged_after_the_keys_leave` (a right and a wrong answer per item kind give the same response as before) | US2-AS2 |
| `tests/unit/domain/test_spec003_l2_public_content.py::test_projection_keeps_what_the_renderer_reads` | no rendering regression |
| `frontend/e2e/spec003-l2-lesson.spec.ts`: an eleven-block lesson is walked end to end with the stripped content | the student's path still works |
| `pnpm run build` | the removed renderers and types compile away |

## Owner decisions (2026-10-19)

- **N7 — `valid_options` is the list of choices, not a key.** **Approved** — **keep it** and amend
  US2-AS1, which names it among the keys, to drop it. Removing it would leave multiple-answer items
  with nothing to choose from.
- **N8 — worked-example `solution` and `correct_version`.** They are teaching content: an example
  the student reads, and the right version the trap card shows after the student commits. They are
  not keys of a graded interaction. **Approved** — **keep them in the content** (FR-020 covers
  grading keys). The alternative is to serve them from the server after the attempt, which is more
  work for content the student is meant to see.
- **N9 — the abstraction question is graded in the browser** (`options[].correct`; 199 options in
  52 nodes). **Approved** — **make it a server-graded interaction with `required=False`**, so it never
  gates completion and its key leaves the content like the others. The alternative is to drop the
  right/wrong colouring and keep it as an ungraded question.
