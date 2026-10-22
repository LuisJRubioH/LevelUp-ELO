# AI integration — as-is survey (spec 005 input)

Read-only survey of `redesign @ ec96508`, 2026-10-19. Input for `specs/005-ai/spec.md` (roadmap
M5: provider detection, key precedence, KatIA's Socratic guardrails, procedure review; AGENTS.md §
AI integration and R7).

Each finding cites code at that commit (`AI` = `src/infrastructure/external_api/ai_client.py`,
`R` = `api/routers/ai.py`, `S` = `api/routers/student.py`, `T` = `api/routers/teacher.py`,
`MR` = `src/infrastructure/external_api/model_router.py`, `PR` =
`src/infrastructure/external_api/math_procedure_review.py`, `FE/` = `frontend/src/`).
**Verified** = read in the code; **Inferred** = reasoned from the code, not run. No provider was
called and nothing was run against production.

## 1. Where things live

| Concern | File |
|---|---|
| Key settings and precedence | `api/config.py:39-63` (`get_ai_key`); rate limits `:66-67` |
| KatIA chat | `R:39-161` (`POST /api/ai/socratic`) |
| Legacy procedure review, unused by the frontend | `R:167-202` (`POST /api/ai/review-procedure`) |
| Procedure analysis, the path the frontend uses | `S:631-747` (`POST /api/student/procedure/analyze`); `/ai-status` `S:607-617`; signed score `api/dependencies.py:92-104` |
| Teacher analysis | `T:398-434`; `src/application/services/teacher_service.py:118-181` |
| Providers, prefix detection, calls, prompts, vision | `AI` (1,374 lines) |
| Groq Llama-4-Scout review | `PR` |
| Model router, Socratic validator, `SOCRATIC_MAX_TOKENS` | `MR:36-354` |
| KatIA messages (procedure comment, streak) | `src/domain/katia/katia_messages.py` — V1 only |
| Chat storage | `katia_interactions` (`sqlite_repository.py:870-890, 2000-2075`; `postgres_repository.py:1133-1151, 2427-2480`) |
| V1 | `src/interface/streamlit/views/student_view.py` (KatIA 1130-1200, procedures 1295-1583), `teacher_view.py:84-125` |
| Frontend | `FE/components/KatIA/SocraticChat.tsx`; key and provider store `FE/stores/settingsStore.ts:22-63`; provider pickers in `FE/pages/Layout.tsx:263-300`, `Student/StudentLayout.tsx:120-150`, `Teacher/TeacherLayout.tsx:100-145`; procedure UI `components/Procedure/ProcedureSection.tsx`, `pages/Student/ProcedureUpload.tsx` |

## 2. Actual behaviour

**Provider detection.** One implementation, in the backend: `AI:101-108`, first match wins —
`sk-ant-` Anthropic, `gsk_` Groq, `AIzaSy` Gemini, `hf_` HuggingFace, `sk-proj-` and `sk-`
OpenAI. An empty or unknown key gives `None` (`AI:121-128`). V2 has no path to a local model
(Ollama / LM Studio): every V2 endpoint answers 422 without a key, and only V1 configures a local
URL (`student_view.py:333+`).

**Key precedence.** `get_ai_key(function, user_key)`: the user's key, else the function's key
(`AI_KEY_KATIA`, `AI_KEY_PROCEDURE`, `AI_KEY_TEACHER_ANALYSIS`), else `SYSTEM_AI_API_KEY`
(`api/config.py:50-63`). A user key travels in the request body (JSON or multipart), is kept in
the browser's localStorage (`settingsStore.ts:34-38`) and is never stored or echoed by the server
(Verified). `AI_KEY_STUDENT_ANALYSIS` is read by nothing in V2.

**Which provider is called.** KatIA and teacher analysis use the `provider` the client sends,
default `"groq"` (`api/schemas/student.py:376`, `api/schemas/teacher.py:72`); detection by prefix
runs only when the client sends an empty provider. Procedure analysis ignores the client and uses
the prefix (`S:657`). The model the user picks in the frontend is stored but never sent.

**KatIA.** `POST /api/ai/socratic`, any authenticated role, 10 requests/minute per account
(`api/config.py:66`). One blocking call, `get_socratic_guidance`, runs in an executor; its full
reply is then split into SSE tokens (`R:103-131`), so the streaming is simulated. The prompt is
sent as a single user message, not a system message (`AI:184-185`). It holds the statement, the
options, the student's rating and **the correct answer** (`AI:465`), with a rule not to reveal it.
`max_tokens=4096` (`AI:199, 230, 269`). The reply is stored in `katia_interactions` with the
student's own message as free text; the teacher reads it and exports it with the student's name.
Nothing deletes those rows.

**Procedure review.** `POST /api/student/procedure/analyze`, 3 requests/minute. Uploads are checked
(type, 10 MB, 25 Mpx, magic bytes, PDF of 1–20 pages; a PDF becomes its first page at 200 dpi).
With a Groq key it calls `meta-llama/llama-4-scout-17b-16e-instruct` (`PR:12`), temperature 0.1,
asks for strict JSON with a 0–100 score, retries once on bad JSON, forces 0 when the image does
not answer the question, and the server clamps the score to 0–100 (`S:596-604`). The result is
signed into a 30-minute token; on submission only `ai_proposed_score` is stored. The rating moves
only through the teacher's grade, `(score − 50) × 0.2` (spec 001; pinned by
`test_spec001_repository_pins.py:91`).

**Teacher analysis.** `POST /api/teacher/student/{id}/ai-analysis`, teacher or admin, the student
in the teacher's groups. Sends ratings, accuracy, topics and response times — no name or id
(Verified). Fewer than 3 attempts returns a fixed message.

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| A1 | **Guardrail missing** | **V2's KatIA has no post-validation and no token cap.** AGENTS.md says V2 uses `SOCRATIC_MAX_TOKENS=120` and rejects replies that reveal the answer or exceed 3 sentences. The endpoint never calls `validate_socratic_response` and asks for 4,096 tokens. The validator exists only in V1; it allows 5 sentences (`MR:320`) and matches 13 phrases ("la respuesta es", "paso 1:" …), not the correct option itself. | `R` (no call); `AI:199`; `MR:303-344`; `AGENTS.md` § AI integration | Verified |
| A2 | **Answer in the prompt** | The correct answer is in KatIA's prompt, guarded only by an instruction to the model; nothing checks the reply for it. | `AI:465`; `R:69-77` | Verified (code); leak not reproduced |
| A3 | **Client-controlled prompt** | The statement in the prompt is `body.item_content`, sent by the client with no length limit, not the item's stored text; the student's chat message is passed as the "option the student chose". | `R:110-111`; `api/schemas/student.py:369`; `AI:429, 464-472` | Verified |
| A4 | **Provider routing** | The frontend offers `google`, the backend knows `gemini`: a Gemini key goes to Groq's configuration. With the default `"groq"`, an Anthropic, OpenAI or Gemini key (the user's or the system's) is sent to Groq unless the user picks the matching provider. Procedure analysis decides by prefix instead: two rules for one key. | `Layout.tsx:272`; `settingsStore.ts:26, 59`; `AI:71`; `R:91-96`; `S:657` | Verified (routing); failure Inferred |
| A5 | **Non-Groq procedure review** | Other providers get `model_name=""`: OpenAI and HuggingFace answer 422 «no soporta visión»; Anthropic and Gemini receive an empty model and the SDK error text comes back as HTTP 200 feedback, signed into the token. | `S:717`; `AI:1069-1083, 1209, 1242, 1230, 1265` | Verified (code); SDK error Inferred |
| A6 | **Teacher analysis input** | `procedure_stats` is never passed, so every analysis tells the model the student uploaded no procedure (with a «critical warning»); the model is always `llama-3.1-8b-instant`, whatever the provider. | `T:425-430`; `AI:730, 765-771` | Verified |
| A7 | **Errors to the client** | Raw exception text reaches HTTP details (`R:201`; `S:675, 692-696, 722`) and the review feedback (`AI:1230, 1265`); provider error strings come back as 200 from teacher analysis. An SDK 401 message can carry a masked fragment of the key. | as cited | Verified (sites); key fragment Inferred |
| A8 | **Access** | `/ai/socratic` and `/procedure/analyze` accept any role, and KatIA does not check that the student is enrolled in the course or that the item belongs to it. | `R:39-60`; `S:631-640` | Verified |
| A9 | **Minors' free text** | `katia_interactions.student_message` keeps what students type, indefinitely, exported with their name; nothing purges it. Compare spec 003, which stores no free text from lessons (FR-006). | repositories as cited; `T:390-395, 531` | Verified |
| A10 | **Blocking calls** | Still synchronous inside `async def`: the rating read for KatIA (`R:88`) and the whole legacy review (`R:196`). `asyncio.get_event_loop()` in a coroutine (`R:103`). | as cited | Verified |
| A11 | **Dead and duplicated code** | Unused in V2: `/api/ai/review-procedure`, `get_socratic_guidance_stream`, `get_katia_chat_stream`, `SOCRATIC_CORRECTION_PROMPT`, `apply_procedure_elo_adjustment`, `AIClient`, `AI_KEY_STUDENT_ANALYSIS`. Two vision keyword lists (`AI:998-1043`, `MR:92-119`), three KatIA prompts (`AI:447, 494, 552`), three copies of the key and provider picker in the frontend. | as cited | Verified (grep) |
| A12 | **Model ids** | Hard-coded per provider (`AI:52-81`; frontend list `settingsStore.ts:44-63`), several likely retired or superseded (`gemini-2.0-flash`, `gemini-2.0-flash-exp`, `gemini-1.5-pro`, the legacy HuggingFace inference URL). No explicit timeout on any SDK client. | as cited | Ids Verified; retirement Inferred |
| A13 | **Doc drift** | AGENTS.md: «no prefix → local» holds only in V1; the KatIA guardrail (A1). R7 says V1 keeps keys only in `st.session_state`, but V1 also reads `GROQ_API_KEY` from the environment (`student_view.py:287`, `teacher_view.py:86`). The KatIA assets bullet matches the code (`get_procedure_comment` ≥ 91 / ≥ 60 / below; `get_streak_message` 5/10/20), but both are V1 only. | as cited | Verified |
| A14 | **Test gaps** | Untested: prefix detection, key precedence, the Socratic validator, the review's JSON parsing and retry, provider/key mismatch, the prompt holding the answer, `/api/ai/review-procedure`, the `google` provider value, teacher analysis returning provider errors as 200. | `tests/` (grep) | Verified |

## 4. Existing evidence

- **KatIA:** a provider failure is neither streamed as KatIA's reply nor saved; an unexpected
  failure shows no internal detail; a reply is streamed and saved
  (`tests/api/test_ai_errors_and_scores.py:78-117`); the socratic limit is per account
  (`tests/api/test_rate_limit.py`); 401 without a session (`test_protected_routes.py:91`); the
  canonical rating reaches the prompt (`test_spec001_api.py:256-290`); a slow item read does not
  block the loop (`test_spec002_d2_connections.py:196-270`).
- **Procedure review:** the AI score stays on 0–100 (`test_ai_errors_and_scores.py:120`); a forged
  score is ignored and a signed token accepted (`test_procedure_upload_security.py:26`); analysis
  runs off the event loop (`test_ai_calls_off_event_loop.py:47`); the AI score moves no rating
  (`test_spec001_repository_pins.py:91`).
- **Teacher analysis:** scope (`test_teacher_resource_access.py:45-72`), 422 without a key naming
  `SYSTEM_AI_API_KEY` (`:151`), 503 on connection errors (`:165`), fewer than 3 attempts
  (`test_teacher_service.py:132-151`).
- **Frontend:** `e2e/katia-chat.spec.ts` (token refresh; the student's key and provider are sent),
  `e2e/spec001-b7-procedures.spec.ts`, `e2e/teacher-procedure-view.spec.ts`.

## 5. Decisions for the owner (input for `/speckit-clarify`)

None blocks the transfer (PR #3): no AI output moves a rating.

1. **KatIA's guardrail (A1, A2).** Port a post-validation to V2 and cap the tokens, and decide what
   it checks: the 13 phrases, also the correct option's text, and the sentence limit (3 as
   documented, or the 5 the code allows). Or keep the correct answer out of the prompt altogether,
   so the model cannot leak it (KatIA would then guide without knowing the answer).
2. **Which provider (A4).** Decide by the key's prefix everywhere (the provider picker becomes
   redundant), or by the user's choice everywhere and refuse a key that does not match it.
3. **Non-Groq procedure review (A5).** Give each vision provider a real model, or support only Groq
   for review and say so in the interface.
4. **What KatIA stores (A9).** Keep students' messages (the teacher reads them), keep them for a
   limited time, or store no free text as spec 003 decided for lessons.
5. **Access (A8).** Only students enrolled in the item's course may use KatIA and procedure
   analysis, as spec 001 FR-037 does for practice?
6. **Dead code (A11).** Remove what V2 does not use (it would stay in V1 while V1 is frozen?), or
   leave it until V1 is retired.
7. **Model ids (A12).** Keep them in code and review them in each spec, or move them to settings.

## 6. Proposed scope for spec 005 (draft)

- **In:** provider detection and key precedence; how a provider and model are chosen; KatIA's
  prompt, guardrails, limits and what it stores; procedure analysis (providers, parsing, the
  advisory score and its token); teacher analysis (inputs, outputs, errors); error handling and
  degradation without a key; the async boundary for AI calls; the related AGENTS.md text.
- **Out:** rating effects (spec 001: only the teacher's grade moves a rating); upload storage and
  anti-plagiarism (spec 001 block 7); the teacher's grading flow (spec 006); V1 beyond what V2
  shares (V1 is frozen).

## 7. Owner decisions (2026-10-19)

The owner read this survey and approved the recommendations; they are the input for
`/speckit-specify`.

1. **KatIA's guardrail (A1, A2):** the correct answer leaves KatIA's prompt, and the server still
   checks every reply: at most 120 tokens and 3 sentences, none of the revealing phrases, never the
   correct option's text. A refused reply is replaced by a guiding question and not stored.
2. **Which provider (A4):** decided by the key's prefix everywhere; the provider picker goes. The
   server chooses the model per function.
3. **Procedure review (A5):** Groq only (the vision model, `llama-4-scout`), said in the interface;
   other providers may come in a later delivery. KatIA and the analyses keep their own Groq models:
   one provider, one model per function.
4. **What KatIA stores (A9):** no message text after a conversation ends. A short record per
   conversation instead: the topic and item, whether the student then solved it, did not, or left
   without finishing, and the kind of difficulty from a fixed list. Where the student got with the
   assistant, not what was said.
5. **Access (A8):** only students enrolled in the item's course, as spec 001 FR-037 does for
   practice; the statement is read from the item, not from the client.
6. **Dead code (A11):** V2-only dead code goes with spec 005. V1 retires for good: disconnected at
   the switch (PR #3, `docs/transfer.md` § 3.1) and never reconnected; its code is removed about two
   weeks after V2 runs stable in production (roadmap F-10).
7. **Model ids (A12):** in settings, one per function, with today's models as defaults; every
   provider call gets an explicit timeout.

Not a decision: the teacher analysis gets the student's procedure statistics (A6) and no response
carries exception text (A7) — both are defects.
