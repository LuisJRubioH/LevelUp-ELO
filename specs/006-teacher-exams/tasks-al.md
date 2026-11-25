# Tasks — spec 006, delivery AL (a template in an order of its own)

**Plan**: [plan-al.md](plan-al.md). FR-028 is `[CHANGE]`. US7-AS2 … US7-AS4 describe what must not
change around it (resume, grading, standard exams): their tests pass on the unchanged code and
stay green.

## Phase 1 — Tests first

- [x] T001 [US7-AS1, FR-028] `tests/integration/test_spec006_al_order.py::test_each_session_draws_its_own_order`
  (both engines): three students; every item once; not every session in the saved order; options
  shuffled. Fails on the unchanged code.
- [x] T002 [US7-AS1, FR-028] `…::test_an_option_that_refers_to_the_others_stays_last` (both
  engines). Fails on the unchanged code.
- [x] T003 [US7-AS2, US7-AS3, US7-AS4] `…::test_a_resumed_session_keeps_its_order`,
  `…::test_the_order_changes_no_result`, `…::test_standard_exams_keep_their_order` (both
  engines). Pass on the unchanged code; they guard what AL must not break.
- [x] T004 [FR-028] `tests/unit/domain/test_spec006_exam_order.py`: permutation, fixed per session
  and item, different across sessions, the anchored option last, what counts as one.

## Phase 2 — Implementation

- [x] T005 [FR-028] `src/domain/exams/order.py`: `item_order`, `option_order`,
  `refers_to_the_others`.
- [x] T006 [FR-028] `api/routers/student.py`: a template's items drawn before the session is
  stored; `_exam_item` orders a template session's options, at start and on resume.

## Phase 3 — Close

- [x] T007 Traceability: US7-AS1 … US7-AS4 and FR-028 filled; AL `closed`. Checks: the suite,
  `check_traceability.py`, black (CI's version) and flake8.
