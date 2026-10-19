# Tasks — spec 003, delivery L3 (a node completes on right answers)

**Plan**: [plan-l3.md](plan-l3.md) (approved by the owner, 2026-10-19). FR-030 is `[CHANGE]`; N1
(B01 on view) and N2 (B13 on answers right or wrong) apply here.

## Found while writing the tests

- Every required interaction of the catalogue has an expected answer, so «right» is defined for
  all of them.
- B02 (the trigger question) is not an eleven-block node: its first question takes one answer and
  the second has no right one. FR-030 covers eleven-block nodes only, so B02 keeps «answered».
- B13 has no interactions: «answered» completes it at once, as today.
- The eleven-block renderer already enables «Terminar» only when every practice and closing item is
  right on the client; L3 makes the server enforce it and lets the screen show the server's
  refusal.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/unit/domain/test_spec003_l3_completion.py`: the four rules on fabricated data;
  every eleven-block node uses `correct`; no diagnostic, bridge or post-diagnostic item is a gap
  (V2-R11) — FR-030
- [x] T002 `tests/integration/test_spec003_l3_completion.py` (both engines): a wrong answer is
  refused by name; the refusal lists every missing item in order; all right completes and opens
  the next node; wrong then right completes; B01 on view, B13 on answers; a node completed before
  L3 stays completed — US3-AS1 … AS3, FR-030, N1, N2

## Phase 2 — Implementation

- [x] T003 `src/domain/learning/path.py`: `completion_rule`, `completion_gaps`,
  `completion_refused`; `missing_interactions` retired (the hub repair uses `completion_gaps`)
- [x] T004 `prealgebra.py`: `completion` on every node — `cards` (hubs), `correct` (eleven-block),
  `view` (B01), `answered` (B02, B13)
- [x] T005 `api/routers/student.py`: `node_completed` checks only a node not yet completed; the 409
  carries `completion_refused`
- [x] T006 Frontend: `Lesson.tsx` catches the 409 and `ElevenBlockLesson` shows its text under
  «Terminar»

## Phase 3 — Close

- [x] T007 Traceability: US3-AS1 … AS3, FR-030 filled; L3 `closed`; full suite on both engines,
  black, flake8, `check_traceability.py`, `pnpm run build`
