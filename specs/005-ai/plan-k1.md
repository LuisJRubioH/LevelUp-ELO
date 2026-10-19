# Plan — spec 005, delivery K1: one key, the right provider

**Spec**: [spec.md](spec.md) § Deliveries, K1 (US2, US4; FR-010 … FR-016) · **Branch**:
`005-ai-k1`, from `redesign` after A · **Date**: 2026-10-19 · **Status**: draft for the owner's
approval

## Summary

Today the browser chooses the provider (default `groq`) for KatIA and the teacher analysis, while
procedure analysis decides by the key's prefix; the browser offers `google` where the server knows
`gemini`; the chosen model is never sent; no provider call has a timeout; a non-Groq review gets an
empty model; the teacher analysis is told the student uploaded no procedure; and exception text
reaches responses. K1 makes the key decide the provider, the server decide the model, and every
failure a fixed message.

## Constitution Check (1.2.0)

| Principle | K1 |
|---|---|
| Security (VI, R7) | Keys still never stored or returned (FR-005 pinned in A); no exception text in responses |
| Layers (III) | Provider choice and models stay in infrastructure (`ai_client.py`) and settings; routers only ask for a function's client |
| Simplicity (VII) | One rule for the provider (the prefix), one setting per model; the picker and its three copies go |

## Design

- **Provider (FR-010):** one function, `provider_for(key) -> str`, built on
  `detect_provider_from_key`. A key with no known prefix answers 422 «Clave no reconocida: usa una
  de Groq (gsk_), Anthropic (sk-ant-), OpenAI (sk-), Gemini (AIzaSy) o HuggingFace (hf_)». Every
  endpoint calls it; `body.provider` is no longer read.
- **Client (FR-011):** `provider` leaves `SocraticRequest` and `StudentAIAnalysisRequest` (pydantic
  ignores an unknown field, so an old browser still works). The provider picker leaves `Layout.tsx`,
  `StudentLayout.tsx` and `TeacherLayout.tsx`; the key field stays. `settingsStore` drops `provider`
  and `model`, with a persisted-state migration that discards them.
- **Models (FR-012):** settings `ai_model_katia`, `ai_model_vision`, `ai_model_analysis` (env
  `AI_MODEL_*`), defaults `llama-3.1-8b-instant`, `meta-llama/llama-4-scout-17b-16e-instruct`,
  `llama-3.3-70b-versatile`. They apply to Groq keys; for another provider the function uses that
  provider's entry in `PROVIDERS` (`model_cog` / `model_analysis`), as today.
- **Timeouts (FR-013):** `timeout=30` on KatIA's client, `90` on the review's and the analysis's
  (`OpenAI(...)`, `Anthropic(...)`, the Gemini client, `requests`); a timeout maps to 503 «La IA no
  respondió a tiempo».
- **Review (FR-014):** a key whose provider is not Groq answers 422 «La revisión con IA usa Groq»
  before the image is processed. `/ai-status` keeps `provider`; `ProcedureSection.tsx` shows the
  same sentence and hides «Analizar» when the student's own key, or the system's, is not Groq's. The
  generic vision branch (`analyze_procedure_image` with `model_name=""`) is no longer reached.
- **Teacher analysis (FR-015):** `student_ai_analysis` passes
  `repo.get_procedure_stats_by_course(student_id)` and the analysis model to
  `generate_ai_analysis`.
- **Errors (FR-016):** every `detail=f"…{exc}"` in `api/routers/ai.py` and `api/routers/student.py`
  becomes a fixed message (the exception is logged server-side without the key); a provider error
  string (`ERROR_…`, `❌ …`) from the analysis becomes 502 instead of 200; `analyze_procedure_image`'s
  error strings are not reached (FR-014).

## Tests (written first; each fails on today's code)

| Test | Proves |
|---|---|
| `tests/api/test_spec005_k1_providers.py::test_the_key_prefix_picks_the_provider_for_every_feature` (a provider double records the base URL and model; Groq, Anthropic, OpenAI, Gemini keys; KatIA, teacher analysis) | US2-AS1, FR-010, FR-012 |
| `…::test_a_key_with_no_known_prefix_is_refused_naming_the_providers` | FR-010 |
| `…::test_the_browser_cannot_choose_provider_or_model` (send `provider="openai"` with a Groq key → Groq) | FR-011 |
| `…::test_models_come_from_settings` (`AI_MODEL_KATIA` set → that model) | FR-012 |
| `…::test_a_provider_that_does_not_answer_in_time_is_503` (clients built with the timeout; a double that raises the SDK's timeout) | FR-013, US2-AS3 |
| `…::test_review_with_a_non_groq_key_is_refused_before_processing` | US2-AS2, FR-014 |
| `…::test_teacher_analysis_receives_procedure_stats_and_the_analysis_model` | US4-AS1, FR-015 |
| `…::test_no_response_carries_exception_text` (every AI endpoint × the double's failures) | US2-AS3, FR-016, SC-003 |
| `frontend/e2e/spec005-k1-keys.spec.ts`: no provider picker; «La revisión con IA usa Groq» shown with an Anthropic key | FR-011, FR-014 |

## Order

K1 goes first: K2 and K3 build on one provider client per function.
