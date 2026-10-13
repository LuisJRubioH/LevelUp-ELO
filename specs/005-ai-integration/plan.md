# Implementation Plan: KatIA guides without giving the answer

**Branch**: `005-ai-integration` (carried on `claude/festive-hopper-qh6qpb`) | **Date**: 2026-10-13 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-ai-integration/spec.md`

## Summary

Move KatIA's V2 chat from "a prompt that asks the model to behave" to a use case the server
controls. The server records each item it serves; KatIA answers only about a served item of an
enrolled course outside an open exam, with the bank's statement and options, and receives the
correct option only after the server recorded an answer to that serving. The student's message
travels as its own turn; messages that ask for the answer, propose an option or try to override
the rules get a reviewed redirect without calling the model; every model reply passes
deterministic checks before the student sees it, and a rejected one becomes a reviewed hint. The
server chooses where the system key goes, asks for 120 output tokens and bounds message,
history and turns. Design decisions: [research.md](research.md) (R1–R13).

## Technical Context

**Language/Version**: Python 3.11 (backend; local runs on 3.13), TypeScript 5 / React 19
**Primary Dependencies**: FastAPI, pydantic-settings, slowapi, openai and anthropic SDKs,
psycopg2, sqlite3; Vite, Zustand, react-i18next
**Storage**: PostgreSQL (Supabase) and SQLite through the dual repository — one new table
(`item_serves`) and two new columns (`katia_interactions.serve_id`, `.guard_outcome`)
**Testing**: pytest (unit for domain/application, integration over both engines, API on
SQLite), Playwright with a mocked API
**Target Platform**: Render (one process) + Vercel SPA
**Project Type**: web application (API + SPA); V1 Streamlit frozen
**Performance Goals**: no extra model call; refused requests make none; one indexed read per
check (serving, attempts above the watermark, open exams, turns of the serving)
**Constraints**: additive migrations only; the correct option never reaches the browser; keys
never logged; blocking I/O off the event loop (AGENTS R17)
**Scale/Scope**: 20–30 concurrent students; ≤ 12 turns per serving; ≤ 10 requests/min/session

## Constitution Check

*Gate before Phase 0 and re-checked after Phase 1 design.*

| Principle | Status | How this plan complies |
|---|---|---|
| I. Spec is the contract | ✅ | every FR gets a test; `[CHANGE]` tests fail on the base first; plain IDs until their tests land (spec § Delivery) |
| II. One source of truth | ✅ | the token limit moves to `domain/katia/limits.py` and V1/V2/config consume it (R11); the conversation and the serving have one store each (R1, R2) |
| III. Layers | ✅ | checks, prompt and reviewed messages in `domain/katia/` (pure); the use case in `application/services/katia_service.py` with `IKatiaRepository` and `ITutor` injected; SDKs and routing in `infrastructure/external_api/katia_tutor.py`; composition in `api/routers/ai.py` |
| IV. Dual DB | ✅ | `item_serves` and the two columns in both engines, idempotent; repository behaviour tested over both (`tests/integration/test_spec005_katia_store.py`); `db_sync_check.py` |
| V. Measurement integrity | ✅ | the key never travels before an answer; exams refused from server state; the correct option still never reaches the frontend |
| VI. Security | ✅ | the system key's destination is server-only; local providers refused; keys out of logs/responses/stored turns (R6, R7); no SymPy `eval` on model output (R3) |
| VII. Simplicity | ✅ | two dead prompt functions removed (R10); no new dependency; limits are five settings with domain defaults |
| VIII. Pedagogy | ✅ | the rule is the owner's (block 6); limits of the guarantee stated, not hidden (spec § Known limits) |
| Validation & errors | ✅ | every refusal is a 4xx/503 with a code before streaming; a model failure keeps #57's SSE contract; a failed serving record is logged and does not break practice |
| V1 frozen | ✅ | V1 changes only by deleting an unused alias and by importing the moved constant (R10, R11) |

Post-design re-check: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/005-ai-integration/
├── spec.md
├── plan.md              # this file
├── research.md          # R1–R13
├── data-model.md
├── contracts/api.md
└── tasks.md
```

### Source Code (repository root)

```text
src/domain/katia/
├── guardrails.py          # NEW — normalisation, message and reply checks, trimming
├── tutor_prompt.py        # NEW — instructions (es/en) and message list
├── reviewed_messages.py   # NEW — reviewed redirects and hints (es/en)
└── limits.py              # NEW — KatiaLimits, SOCRATIC_MAX_TOKENS
src/application/interfaces/
├── repositories.py        # + IKatiaRepository
└── tutor.py               # NEW — ITutor, TutorCompletion, TutorUnavailable
src/application/services/katia_service.py        # NEW — the use case
src/infrastructure/external_api/katia_tutor.py   # NEW — resolve_route, ProviderTutor
src/infrastructure/external_api/ai_client.py     # − get_socratic_guidance(_stream)
src/infrastructure/external_api/model_router.py  # SOCRATIC_MAX_TOKENS from domain
src/infrastructure/persistence/{sqlite,postgres}_repository.py  # item_serves, turns, open exams
src/interface/streamlit/views/student_view.py    # − unused alias (V1)
api/config.py              # KatIA limits
api/schemas/student.py     # SocraticRequest
api/routers/ai.py          # /ai/socratic composition
api/routers/student.py     # next-question records the serving
frontend/src/components/KatIA/SocraticChat.tsx   # no statement sent; coded errors
frontend/src/pages/Student/Practice.tsx, frontend/src/components/Course/CourseRail.tsx
frontend/src/i18n/locales/{es,en}.ts
scripts/evaluate_katia_models.py                 # NEW — § Model evaluation (not CI)
docs/sdd/katia-model-evaluation.md               # NEW — protocol and results (pending)
```

Tests:

```text
tests/unit/domain/test_spec005_guardrails.py          # FR-003…FR-005, FR-009…FR-015, FR-032
tests/unit/domain/test_spec005_tutor_prompt.py        # FR-001, FR-002, FR-006, FR-007
tests/unit/application/test_spec005_katia_service.py  # flow with fake repo and tutor
tests/unit/infrastructure/test_spec005_katia_tutor.py # routing, truncation, failures
tests/integration/test_spec005_katia_store.py         # both engines
tests/api/test_spec005_katia_api.py                   # end to end with a fake tutor
tests/api/test_ai_errors_and_scores.py, tests/api/test_rate_limit.py,
tests/api/test_spec001_api.py                         # adapted to the new seam
tests/unit/scripts/test_evaluate_katia_models.py      # harness scoring
frontend/e2e/katia-chat.spec.ts                       # FR-026, FR-036, request shape
```

## Complexity Tracking

None: no principle is waived.
