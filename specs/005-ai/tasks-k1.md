# Tasks — spec 005, delivery K1 (one key, the right provider)

**Plan**: [plan-k1.md](plan-k1.md) (approved by the owner, 2026-10-19). FR-010 … FR-016 are
`[CHANGE]`.

## Found while writing the tests

- KatIA's provider call ran inside the event stream, so a failure was a 200 with an `error` event.
  US2-AS3 asks for a 502/503: the call now runs before the stream starts (the provider answers in
  one piece anyway). Two existing tests pinned the old event form and now pin the status
  (`test_ai_errors_and_scores.py`); the teacher's 503 test pins the fixed messages.
- The repositories keep procedure scores on 0–100, but the analysis prompt labelled them on 0–5:
  any score read «Excelente». The labels now use 0–100 (60 / 80), for V2 and V1 alike.
- The generic vision review (non-Groq) is gone, so the off-the-loop test's «vision-review» case
  became a KatIA case.
- `SYSTEM_AI_PROVIDER` is no longer read (the prefix decides); the setting goes with K4.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/api/test_spec005_k1_providers.py` (20 cases): provider by prefix for each
  provider; browser's provider and model ignored; models from settings; unknown prefix refused
  (KatIA, review, analysis); timeouts 30/90; timeout → 503; Groq-only review; the analysis's
  procedure statistics, model and timeout; no exception text — US2, US4, FR-010 … FR-016
- [x] T002 `frontend/e2e/spec005-k1-keys.spec.ts`: no picker; «La revisión con IA usa Groq» with an
  Anthropic key; the review offered with the system's Groq key — FR-011, FR-014

## Phase 2 — Implementation

- [x] T003 `api/config.py`: `ai_model_katia`, `ai_model_vision`, `ai_model_analysis`
- [x] T004 `api/ai_target.py`: `ai_target(function, key)`, `UNKNOWN_KEY`, `TIMED_OUT`,
  `UNAVAILABLE`, `GROQ_ONLY`, timeouts
- [x] T005 `ai_client.py`: `timeout` through `_call_ai_api`, `get_socratic_guidance`,
  `get_pedagogical_analysis`; Anthropic timeouts raise `TimeoutError`; quality labels on 0–100.
  `math_procedure_review.py`: `model` and `timeout`; errors without the SDK's text
- [x] T006 Routers: KatIA (provider before the stream, fixed 502/503), procedure analysis (Groq
  only, fixed messages, no generic vision branch), `/ai-status` by prefix, teacher analysis
  (statistics, model, timeout, 502 on a provider error string), legacy review's fixed message;
  `provider` leaves the request schemas
- [x] T007 Frontend: the picker leaves the three layouts; `settingsStore` keeps only the key
  (persisted version 1 drops `provider`/`model`); KatIA and the analysis send no provider; the
  procedure screens show «La revisión con IA usa Groq» and hide «Analizar» for a non-Groq key

## Phase 3 — Close

- [x] T008 Traceability: US2-AS1 … AS3, US4-AS1, FR-010 … FR-016 filled; K1 `closed`; full suite
  on both engines, Playwright, black, flake8, `check_traceability.py`, `pnpm run build`
