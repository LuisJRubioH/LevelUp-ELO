# Tasks — spec 005, delivery K2 (KatIA's guardrails and access)

**Plan**: [plan-k2.md](plan-k2.md) (approved by the owner, 2026-10-19). FR-020 … FR-023 are
`[CHANGE]`.

## Found while writing the tests

- The prompt lists the item's options, so the correct option's text appears there once, as one
  option among the rest. The test pins that it appears exactly as often as the options show it and
  that no «RESPUESTA CORRECTA» marker exists outside the statement and options.
- Six existing tests asked KatIA or the review about `q47` (`calculo_integral`), a course the
  test student is not enrolled in. With FR-021 that is a 403, so they now use `q21`
  (`calculo_diferencial`, where the student is enrolled): `test_ai_calls_off_event_loop.py`,
  `test_ai_errors_and_scores.py`, `test_spec005_a_pins.py`, `test_spec005_k1_providers.py`.
- A procedure analysed for a free exercise (an id that is not in the bank) has no course to check:
  it requires the student to be enrolled in at least one course.
- V1 keeps its own validator (`model_router.validate_socratic_response`, 5 sentences): V1 is
  frozen. The 13 phrases are copied, not moved, into `src/domain/katia/guardrail.py`.
- The instructions still travel as a «SISTEMA:» prefix of one message, as today; K3's multi-turn
  conversation sends real system and history messages.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/api/test_spec005_k2_katia.py`: no correct answer in the prompt; the statement
  from the item; a revealing reply replaced and not stored; a guiding reply stored; 120 tokens;
  403 for not enrolled, teacher and admin on KatIA and on the analysis (provider never called);
  no read on the event loop — US1-AS1 … AS3, FR-020 … FR-023
- [x] T002 `tests/unit/domain/test_spec005_guardrail.py`: sentences, phrases, the option's text
  after normalising, a short option does not refuse every reply — FR-022
- [x] T003 `frontend/e2e/katia-chat.spec.ts`: the chat sends the option the student marked — FR-020

## Phase 2 — Implementation

- [x] T004 `src/domain/katia/guardrail.py`: `check_reply`, `GUIDING_QUESTION`, `MAX_SENTENCES`
- [x] T005 `ai_client.get_socratic_guidance`: no correct answer; the option marked and the message
  apart; `max_tokens=120`
- [x] T006 `api/ai_target.require_enrolled_in_item`; `/ai/socratic` and `/procedure/analyze` for
  students only, enrolled in the item's course, before any provider call; statement and options
  from the item; reads and the provider call through `asyncio.to_thread`; a refused reply becomes
  the guiding question and is not stored
- [x] T007 `SocraticRequest.selected_option` (ignored unless it is one of the item's options);
  `SocraticChat` sends it from practice

## Phase 3 — Close

- [x] T008 Traceability: US1-AS1 … AS3, FR-020 … FR-023 filled; K2 `closed`; full suite on both
  engines, Playwright, black, flake8, `check_traceability.py`, `pnpm run build`
