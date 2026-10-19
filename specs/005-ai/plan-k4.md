# Plan — spec 005, delivery K4: clean-up

**Spec**: [spec.md](spec.md) § Deliveries, K4 (FR-040) · **Branch**: `005-ai-k4`, from `redesign`
after K3 · **Date**: 2026-10-19 · **Status**: draft for the owner's approval

## Design

- Remove `POST /api/ai/review-procedure` (unused by the frontend; always Groq, no PDF conversion,
  a synchronous call inside `async def`) and its schema.
- Remove the `ai_key_student_analysis` setting (`AI_KEY_STUDENT_ANALYSIS` is read by nothing in V2).
- AGENTS.md § AI integration rewritten from spec 005: the prefix decides the provider; the
  `AI_MODEL_*` settings; KatIA's guardrail and record; Groq-only review; the R7 line on V1 keys goes
  with V1 (F-10).
- What V1 still imports (streaming functions, `AIClient`, local providers, the second vision list,
  `katia_messages.py`) stays until F-10 removes V1.

## Tests

| Test | Proves |
|---|---|
| `tests/api/test_spec005_k4_cleanup.py::test_the_legacy_review_endpoint_is_gone` (404) | FR-040 |
| `…::test_no_setting_for_student_analysis` | FR-040 |
