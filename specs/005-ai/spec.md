# Feature Specification: AI Integration

**Feature Branch**: `005-ai` (one branch per delivery once implementation starts)

**Created**: 2026-10-19

**Status**: Draft for the owner's approval. Written from the as-is survey
(`docs/sdd/ai-survey.md`, LuisJRubioH/LevelUp-ELO#92) and the owner's decisions of 2026-10-19 (its
§ 7). Nothing in deliveries K1 … K4 is implemented.

**Input**: Roadmap M5 (`docs/sdd/roadmap.md`): provider detection, key precedence, KatIA's Socratic
guardrails, procedure review. AGENTS.md § AI integration and R7 describe this area today; this
spec owns it and the section is rewritten with K4.

**Outcome served** (constitution VIII): KatIA helps a student reach the answer without giving it,
the key a school provides reaches the provider it belongs to, the teacher learns where each
student got with the assistant — not what they wrote — and no AI output moves a rating.

## Code Scope *(mandatory)*

- `api/routers/ai.py` — KatIA's chat and the legacy review endpoint
- `api/config.py` — key and model settings
- `api/routers/student.py` — procedure analysis and `/ai-status` (shared with specs 001 and 003)
- `api/routers/teacher.py` — the teacher's AI analysis and KatIA history (shared)
- `api/schemas/student.py`, `api/schemas/teacher.py` — the AI request bodies (shared)
- `src/infrastructure/external_api/ai_client.py`
- `src/infrastructure/external_api/math_procedure_review.py`
- `src/infrastructure/external_api/model_router.py`
- `src/application/services/teacher_service.py` (shared)
- `src/infrastructure/persistence/sqlite_repository.py`,
  `src/infrastructure/persistence/postgres_repository.py` — KatIA's storage (shared)
- `frontend/src/components/KatIA/SocraticChat.tsx`
- `frontend/src/stores/settingsStore.ts`
- `frontend/src/pages/Layout.tsx`, `frontend/src/pages/Student/StudentLayout.tsx`,
  `frontend/src/pages/Teacher/TeacherLayout.tsx` — the key and provider picker (shared)
- `frontend/src/components/Procedure/ProcedureSection.tsx`

## Deliveries *(this spec is delivered in steps)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it closed and fills all its rows.

| Delivery | Content | State |
|---|---|---|
| **A** | As-is pins: what the AI features already guarantee, each requirement tied to a test | closed |
| **K1** | One key, the right provider: the provider from the key's prefix, one model per function from settings, timeouts, Groq-only review said in the interface, the teacher analysis's real inputs, no exception text to the client | planned |
| **K2** | KatIA's guardrails and access: no correct answer in the prompt, every reply checked, the statement read from the item, only enrolled students | planned |
| **K3** | KatIA's record: multi-turn conversations, a summary per conversation for the teacher, no message text kept after it ends | planned |
| **K4** | Clean-up: V2-only dead code removed, AGENTS.md § AI integration rewritten | planned |

## Clarifications

### Session 2026-10-19 (owner decisions on the survey, § 7)

- Q: KatIA's guardrail (A1, A2)? → A: the correct answer leaves the prompt, and the server checks
  every reply anyway: at most 120 tokens and 3 sentences, none of the revealing phrases, never the
  correct option's text; a refused reply is replaced by a guiding question and not stored.
- Q: Which provider (A4)? → A: the key's prefix decides, everywhere; the provider picker goes; the
  server chooses the model per function.
- Q: Procedure review with other providers (A5)? → A: Groq only for now, said in the interface.
  KatIA, the review and the analyses each keep their own Groq model.
- Q: What KatIA stores (A9)? → A: no message text after a conversation ends; a summary per
  conversation — topic, item, whether the student then solved it, did not, or left, and the kind of
  difficulty.
- Q: Access (A8)? → A: only students enrolled in the item's course (spec 001 FR-037).
- Q: Dead code (A11)? → A: V2-only dead code goes here (K4). V1 retires for good after the switch
  (roadmap F-10); its code is out of this spec.
- Q: Model ids (A12)? → A: in settings, one per function, today's models as defaults; explicit
  timeouts.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - KatIA helps me without giving me the answer (Priority: P1) — K2

**Why this priority**: today KatIA's prompt holds the correct answer and nothing checks the reply;
one leak turns a formative chat into an answer key, for a minor practising alone.

**Independent Test**: a student enrolled in the item's course chats with KatIA through a provider
double that records the prompt and returns chosen replies.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** any item, **When** KatIA is asked about it, **Then** the prompt sent to
   the provider holds the item's statement and options as stored, the option the student chose and
   their message, and not the correct answer.
2. **US1-AS2** — **Given** a provider reply that names the correct option, uses a revealing phrase
   («la respuesta es», «paso 1:» …) or has more than 3 sentences, **When** it comes back, **Then**
   the student sees a guiding question instead and the reply is not recorded as KatIA's.
3. **US1-AS3** — **Given** a student not enrolled in the item's course, or a user who is not a
   student, **When** they call KatIA or procedure analysis, **Then** the server refuses with 403 and
   calls no provider.

### User Story 2 - One key reaches its provider (Priority: P1) — K1

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** a key with a known prefix (system, function or the user's), **When** any
   AI feature runs, **Then** it calls that prefix's provider with the model the settings name for
   that function, whatever the browser sends.
2. **US2-AS2** — **Given** a key that is not Groq's, **When** a student asks for a procedure
   review, **Then** the server answers 422 «La revisión con IA usa Groq» and the interface says so
   before the upload.
3. **US2-AS3** — **Given** a provider that fails or does not answer in time, **When** any AI feature
   runs, **Then** the response is 502 or 503 with a fixed message, never 200, and carries no
   exception text.

### User Story 3 - My teacher sees where I got with KatIA (Priority: P2) — K3

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** a conversation about an item, **When** the student then answers the item
   right (or wrong), **Then** the conversation closes with the outcome «superado» (or «no
   superado»), its number of turns and the kind of difficulty, and the teacher sees it.
2. **US3-AS2** — **Given** a conversation, **When** the student asks for another item, ends the
   session or sends nothing more for 24 hours without answering, **Then** it closes as
   «abandonado».
3. **US3-AS3** — **Given** a closed conversation, **When** anything reads the database or the
   export, **Then** no message text of it remains.

### User Story 4 - The teacher's analysis reads the real data (Priority: P2) — K1

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** a student with graded procedures, **When** the teacher asks for an
   analysis, **Then** the prompt holds their procedure statistics and the analysis model runs.

### User Story 5 - What already holds keeps holding (Priority: P1) — A

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** an AI score for a procedure, **When** it is stored, **Then** no rating
   moves; only the teacher's grade does.
2. **US5-AS2** — **Given** a provider failure, **When** KatIA answers, **Then** the failure is
   neither shown nor stored as KatIA's reply.
3. **US5-AS3** — **Given** many AI requests from one account, **When** they pass the limit,
   **Then** the server refuses them, whatever token the account uses.

### Edge Cases

- **A key with no known prefix** (a local server's, a typo): refused with a message that names the
  accepted providers; V2 has no local model.
- **KatIA after the student already answered the item**: a new conversation; its outcome is the
  next answer to that item, or «abandonado».
- **The provider cannot classify the difficulty**: the summary records «sin clasificar»; the
  outcome still comes from the answer.
- **Conversations stored before K3**: the existing `katia_interactions` rows (N3).

## Requirements *(mandatory)*

### Functional Requirements

**As-is (A)**

- **FR-001** [AS-IS]: The system shall move no rating because of an AI output; only the teacher's
  grade of a procedure moves one (spec 001).
- **FR-002** [AS-IS]: The system shall accept an AI score for a procedure only inside a review
  token it signed for the same student, item and file, and keep it within 0–100.
- **FR-003** [AS-IS]: If a provider fails, then the system shall neither show nor store the failure
  as KatIA's reply.
- **FR-004** [AS-IS]: The system shall limit AI requests per account.
- **FR-005** [AS-IS]: The system shall store no API key and return none in any response.
- **FR-006** [AS-IS]: The system shall use the user's key when given, else the function's key,
  else the general key.
- **FR-007** [AS-IS]: If no key is available, then the system shall answer 422 naming the setting
  to configure.

**Providers and models (K1)**

- **FR-010** [CHANGE]: The system shall choose the provider of every AI feature from the key's
  prefix (`sk-ant-` Anthropic, `gsk_` Groq, `AIzaSy` Gemini, `hf_` HuggingFace, `sk-proj-`/`sk-`
  OpenAI), and refuse a key with no known prefix naming the accepted providers. *(Today KatIA and
  the teacher analysis use the provider the browser sends, default `groq`.)*
- **FR-011** [CHANGE]: The system shall take no provider and no model from the client; the
  interface shall offer no provider picker.
- **FR-012** [CHANGE]: The system shall use, for each function, the model its setting names
  (`AI_MODEL_KATIA`, `AI_MODEL_VISION`, `AI_MODEL_ANALYSIS`), defaulting to today's Groq models
  (`llama-3.1-8b-instant`, `meta-llama/llama-4-scout-17b-16e-instruct`,
  `llama-3.3-70b-versatile`).
- **FR-013** [CHANGE]: The system shall give every provider call an explicit timeout — 30 s for
  KatIA, 90 s for a review or an analysis — and answer 503 when it runs out.
- **FR-014** [CHANGE]: Where the key is not Groq's, the system shall refuse a procedure review with
  422 «La revisión con IA usa Groq», and the interface shall say so before the upload.
- **FR-015** [CHANGE]: When a teacher asks for a student's analysis, the system shall send the
  student's procedure statistics with it. *(Today the prompt always says no procedure was
  uploaded.)*
- **FR-016** [CHANGE]: The system shall return no exception text or provider error string in any
  response, review feedback or analysis; a provider error is a 502 or 503 with a fixed message.

**KatIA's guardrails and access (K2)**

- **FR-020** [CHANGE]: The system shall build KatIA's prompt from the item's statement and options
  as stored, the option the student chose and their message, and shall never include the correct
  answer. *(Today it holds the correct answer and the client-sent statement.)*
- **FR-021** [CHANGE]: The system shall let only a student enrolled in the item's course use KatIA
  and procedure analysis, and refuse anyone else with 403 before calling a provider.
- **FR-022** [CHANGE]: The system shall cap KatIA's reply at 120 tokens and replace with a fixed
  guiding question any reply that has more than 3 sentences, a revealing phrase or the correct
  option's text; a replaced reply shall not be recorded as KatIA's.
- **FR-023** [CHANGE]: The system shall run KatIA's provider call and its database reads off the
  event loop.

**KatIA's record (K3)**

- **FR-030** [CHANGE]: The system shall treat one student's messages about one item, with KatIA's
  replies, as one conversation, sending the open conversation's earlier turns as context.
- **FR-031** [CHANGE]: When a conversation closes, the system shall store its summary: course,
  topic, item, number of turns, outcome — «superado» when the student's next answer to the item is
  right, «no superado» when wrong, «abandonado» when they ask for another item, end the session or
  send nothing for 24 hours — the kind of difficulty from a fixed list (N2), and the misconception
  tag of the option the student had chosen, if any.
- **FR-032** [CHANGE]: The system shall keep a conversation's message text only while it is open
  and delete it when it closes, at most 24 hours after its last message.
- **FR-033** [CHANGE]: The system shall show a teacher the conversation summaries of the students
  of their groups, and export counts per topic and outcome, never message text.

**Clean-up (K4)**

- **FR-040** [CHANGE]: The system shall offer no `/api/ai/review-procedure` endpoint and read no
  `AI_KEY_STUDENT_ANALYSIS` setting; AGENTS.md § AI integration shall describe the behaviour of this
  spec.

### Key Entities

- **Key**: the user's, the function's or the general one; its prefix names the provider.
- **Function**: KatIA, procedure review, teacher analysis — each with its model and timeout.
- **Conversation**: one student and one item, open until the next answer to it; its text lives
  only while it is open.
- **Conversation summary**: course, topic, item, turns, outcome, kind of difficulty, misconception
  tag; no text.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 KatIA prompts hold the correct answer, checked over a sample of items of every
  course block.
- **SC-002**: 0 KatIA replies that name the correct option reach the student, checked with a
  provider double that returns it.
- **SC-003**: 0 responses of the AI endpoints carry exception text, checked for each failure the
  provider double can raise.
- **SC-004**: 0 conversation texts older than 24 hours in the database.

## Assumptions

- Groq is the production provider (owner, 2026-10-19); the other prefixes stay detected so a school
  may bring its own key for KatIA and the analyses.
- No AI output moves a rating (FR-001); ratings belong to spec 001.
- V1 is disconnected at the switch and retired (roadmap F-10): its AI code is not specified here.

## New Decisions and Contradictions

| # | Point | Recommendation |
|---|---|---|
| N1 | AGENTS.md says V2 caps KatIA at 120 tokens and rejects replies beyond 3 sentences; the V1 validator allows 5. | **Proposed**: 3, as documented (FR-022). |
| N2 | The kinds of difficulty for the summary. | **Proposed**: «enunciado» (did not understand the statement), «concepto», «procedimiento», «cálculo», «opciones» (misread the options), plus «sin clasificar»; the model picks one when the conversation closes, never free text. |
| N3 | `katia_interactions` holds every message typed before K3, with no expiry. | **Proposed**: K3 adds the summary table and stops writing text there; a repair script (`scripts/repairs/`, spec 002 FR-018) deletes the old texts, run by the owner after the switch. No summary can be rebuilt from them (no outcome). |
| N4 | Whether a student with their own key may still use it. | **Proposed**: yes — the key keeps its precedence (FR-006); only the provider picker goes. |

## Out of Scope *(mandatory)*

- Ratings — spec 001: only the teacher's grade moves one. Uploads, storage and anti-plagiarism —
  spec 001 block 7. The teacher's grading flow — spec 006.
- V1's AI code (streaming, `AIClient`, local providers, OCR, the symbolic verifier, KatIA's
  predefined messages): retired with V1 (roadmap F-10).
- Vision providers other than Groq for the review: a later delivery if the owner asks.

## Traceability *(mandatory)*

Rows of delivery A cite the tests that already pin the behaviour; the rest are filled by the pull
request that closes their delivery.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | K2 | `PENDING` |
| US1-AS2 | K2 | `PENDING` |
| US1-AS3 | K2 | `PENDING` |
| US2-AS1 | K1 | `PENDING` |
| US2-AS2 | K1 | `PENDING` |
| US2-AS3 | K1 | `PENDING` |
| US3-AS1 | K3 | `PENDING` |
| US3-AS2 | K3 | `PENDING` |
| US3-AS3 | K3 | `PENDING` |
| US4-AS1 | K1 | `PENDING` |
| US5-AS1 | A | `tests/integration/test_spec001_repository_pins.py::test_spec001_ai_proposed_score_changes_no_rating` |
| US5-AS2 | A | `tests/api/test_ai_errors_and_scores.py::test_a_provider_failure_is_not_katias_reply` |
| US5-AS3 | A | `tests/api/test_rate_limit.py::test_ai_rate_limit_follows_the_account_across_new_tokens` |
| FR-001 | A | `tests/integration/test_spec001_repository_pins.py::test_spec001_ai_proposed_score_changes_no_rating` |
| FR-002 | A | `tests/api/test_procedure_upload_security.py::test_client_cannot_forge_ai_score_but_signed_review_is_accepted`<br>`tests/api/test_ai_errors_and_scores.py::test_the_ai_score_stays_on_its_0_to_100_scale` |
| FR-003 | A | `tests/api/test_ai_errors_and_scores.py::test_a_provider_failure_is_not_katias_reply`<br>`tests/api/test_ai_errors_and_scores.py::test_an_unexpected_failure_shows_no_internal_detail` |
| FR-004 | A | `tests/api/test_rate_limit.py::test_socratic_rate_limit_is_enforced_per_access_token`<br>`tests/api/test_rate_limit.py::test_ai_rate_limit_is_not_shared_between_accounts` |
| FR-005 | A | `tests/api/test_spec005_a_pins.py::test_spec005_no_table_has_a_key_column`<br>`tests/api/test_spec005_a_pins.py::test_spec005_a_users_key_is_neither_stored_nor_returned`<br>`tests/api/test_spec005_a_pins.py::test_spec005_the_system_key_is_never_returned` |
| FR-006 | A | `tests/api/test_spec005_a_pins.py::test_spec005_user_key_then_function_key_then_general_key` |
| FR-007 | A | `tests/api/test_teacher_resource_access.py::test_ai_analysis_without_a_key_says_so` |
| FR-010 | K1 | `PENDING` |
| FR-011 | K1 | `PENDING` |
| FR-012 | K1 | `PENDING` |
| FR-013 | K1 | `PENDING` |
| FR-014 | K1 | `PENDING` |
| FR-015 | K1 | `PENDING` |
| FR-016 | K1 | `PENDING` |
| FR-020 | K2 | `PENDING` |
| FR-021 | K2 | `PENDING` |
| FR-022 | K2 | `PENDING` |
| FR-023 | K2 | `PENDING` |
| FR-030 | K3 | `PENDING` |
| FR-031 | K3 | `PENDING` |
| FR-032 | K3 | `PENDING` |
| FR-033 | K3 | `PENDING` |
| FR-040 | K4 | `PENDING` |
