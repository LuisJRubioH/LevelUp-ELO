# Plan — spec 005, delivery K2: KatIA's guardrails and access

**Spec**: [spec.md](spec.md) § Deliveries, K2 (US1; FR-020 … FR-023) · **Branch**: `005-ai-k2`,
from `redesign` after K1 · **Date**: 2026-10-19 · **Status**: approved by the owner (2026-10-19)

## Summary

KatIA's prompt holds the correct answer and the statement the browser sends; nothing checks the
reply; any role may call it, for any item; the provider is asked for 4,096 tokens; the rating read
blocks the event loop. K2 takes the answer out, reads the statement from the item, checks every
reply on the server and lets only enrolled students in.

## Constitution Check (1.2.0)

| Principle | K2 |
|---|---|
| Minors (VI) | No answer leaks to a student practising alone; access as practice (spec 001 FR-037) |
| Layers (III) | The reply check is pure domain (`src/domain/katia/guardrail.py`); the router calls it |
| Async (R17) | Every repository read of the endpoint through `asyncio.to_thread` |

## Design

- **Prompt (FR-020):** `get_socratic_guidance` loses its `correct_answer` parameter. The statement
  and options come from `repo.get_item_by_id` (the item's `content` and `options`), not from
  `body.item_content`; `SocraticRequest` gains an optional `selected_option` (must be one of the
  item's options, else ignored) so the student's message stops being passed as «the option they
  chose». The prompt becomes a real system message where the provider supports it.
- **Access (FR-021):** `require_role("student")` on `/ai/socratic` and `/procedure/analyze`; the
  item's course is the course checked by `StudentService.ensure_enrolled` (the check practice
  uses). 403 «No estás inscrito en este curso.» before any provider call.
- **Reply check (FR-022):** `check_reply(reply, correct_option_text) -> bool` in
  `src/domain/katia/guardrail.py`: at most 3 sentences (N1), none of the revealing phrases (today's
  13 in `model_router.py`, moved here), and not the correct option's text, compared after
  normalising case, spaces and LaTeX delimiters. The provider is asked for `max_tokens=120`. A
  refused reply is replaced by «¿Qué parte del enunciado te genera más dudas? ¿Qué intentaste
  hasta ahora?» and the conversation stores no KatIA reply for that turn. The correct option is read
  on the server only to check the reply; it never enters the prompt.
- **Off the loop (FR-023):** `RatingReadService(...).ratings_view` and the item read through
  `asyncio.to_thread`; `asyncio.get_event_loop()` replaced by `asyncio.to_thread` for the provider
  call.

## Tests (written first; each fails on today's code)

| Test | Proves |
|---|---|
| `tests/api/test_spec005_k2_katia.py::test_the_prompt_never_holds_the_correct_answer` (a provider double records the prompt; items of each block; SC-001) | US1-AS1, FR-020 |
| `…::test_the_statement_comes_from_the_item_not_the_client` | FR-020 |
| `…::test_a_reply_that_gives_the_answer_is_replaced_and_not_stored` (the option's text; a revealing phrase; 4 sentences; SC-002) | US1-AS2, FR-022 |
| `…::test_katia_asks_for_at_most_120_tokens` | FR-022 |
| `…::test_only_enrolled_students_reach_katia_or_the_review` (not enrolled, teacher, admin → 403, the double never called) | US1-AS3, FR-021 |
| `tests/unit/domain/test_spec005_guardrail.py` (sentence count, phrases, normalised option text, a reply that only asks questions passes) | FR-022 |
| `tests/integration/test_spec002_d2_connections.py` extended: a slow rating read in KatIA does not block `GET /` | FR-023 |
