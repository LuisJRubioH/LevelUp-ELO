# Tasks — spec 003, delivery L2 (answer keys stay on the server)

**Plan**: [plan-l2.md](plan-l2.md) (approved by the owner, 2026-10-19). FR-020 is `[CHANGE]`; N5
(remove the unreachable renderers), N7 (`valid_options` stays), N8 (`solution`, `correct_version`
stay) and N9 (the abstraction question graded on the server) apply here.

## Found while writing the tests

- Beyond the fields in the plan's table, the hub icebreakers carry `feedback_correct`,
  `feedback_incorrect`, `feedback_missing`, `feedback_trap`, `misconception_incorrect` and
  `misconception_missing`: grading data, left out too.
- Seven fields no renderer reads stay on the server as internal: `concept_slug`, `misconception`,
  `house`, `guide`, `validation_status`, `post_diagnostic.compara_con`,
  `post_diagnostic.trigger_refuerzo`.
- Grading through the API already matched the domain for every item kind (US2-AS2 holds before
  and after: a guard).

## Phase 1 — Tests first

- [x] T001 `tests/unit/domain/test_spec003_l2_public_content.py`: every content field of the
  catalogue is classified (public, grading key, internal); the projection keeps every public field,
  no key and no internal field; the catalogue keeps its keys — FR-020, N7, N8
- [x] T002 `tests/integration/test_spec003_l2_keys.py` (both engines): no lesson response, over
  every node, holds a key; grading unchanged per item kind; the abstraction question graded by the
  server, `required=False` — US2-AS1, US2-AS2, N9
- [x] T003 `frontend/e2e/spec003-l2-lesson.spec.ts`: an eleven-block lesson with stripped content,
  the abstraction question sent to the server, retried, and «Terminar» not blocked by it

## Phase 2 — Implementation

- [x] T004 `src/domain/learning/public_content.py`: `PUBLIC_PATHS` (233 paths), `OPAQUE_PATHS`
  (`.feedback`), `GRADING_KEYS`, `INTERNAL_PATHS`, `public_content`
- [x] T005 `api/routers/student.py`: `_lesson_with_progress` projects the content for every lesson
  response (detail, event, preview)
- [x] T006 `prealgebra.py`: `<node>-ABSTRACCION` registered as a `multi_select` interaction,
  `required=False`, on every node with an abstraction question (N9)
- [x] T007 Frontend: `AbstractionQuestion` submits through the lesson engine; `answer` and
  `expected` leave the item types; `LevelTwoOperation`, `LevelThreeMachine`, `LevelFourConcept`
  removed with their unused types (N5)

## Phase 3 — Close

- [x] T008 Traceability: US2-AS1, US2-AS2, FR-020 filled; L2 `closed`; full suite on both engines,
  Playwright, black, flake8, `check_traceability.py`, `pnpm run build`
