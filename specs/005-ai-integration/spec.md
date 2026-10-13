# Feature Specification: AI Integration — KatIA guides without giving the answer

**Feature Branch**: `005-ai-integration` (work carried on `claude/festive-hopper-qh6qpb`)

**Created**: 2026-10-13

**Status**: Implemented on this branch — specify + clarify (`914e8b8`), plan (`f5cc732`) and
tasks (`11e59a0`) were committed before any code; every requirement and scenario below has its
tests in § Traceability. The model evaluation (§ Model evaluation) is the owner's step.

**Input**: The owner's block 6 decisions of 2026-10-13 (points 1–9, § Clarifications) and the
review of KatIA on `redesign @ 1d6fcf6` with LuisJRubioH/LevelUp-ELO#56 and
LuisJRubioH/LevelUp-ELO#57 merged (§ Appendix — As-is evidence).

**Outcome served** (constitution VIII): a student who is stuck gets help to think the exercise
through — concepts, questions, an intermediate step — and still has to reach the answer
themselves, before and after answering. Practice ratings then keep measuring what the student
can do (constitution V), teachers can trust them, and the cost of the tutor stays bounded.

This is the first time a feature touches the AI area, so under the roadmap's lean scope this
spec covers only what block 6 changes: KatIA's chat in V2. The rest of the roadmap's spec 005
area (procedure review, student and teacher analyses) enters by amendment (§ Out of Scope).

## Code Scope *(mandatory)*

The code whose behaviour this spec defines. A pull request that changes any of these paths, or a
test file cited in § Traceability, is a code change for this spec whatever its branch. An entry
ending in `/` covers everything below it. Paths shared with spec 001 belong to both.

- `api/routers/ai.py` — `/ai/socratic` (the procedure review in the same file is out of scope)
- `api/schemas/student.py` — the chat request
- `api/config.py` — KatIA's provider and limits
- `api/rate_limit.py` — the chat's request limit
- `api/routers/student.py` — `next-question` records the serving KatIA binds to
- `src/application/interfaces/repositories.py`
- `src/infrastructure/persistence/` — servings, open exams and KatIA turns in both repositories
- `src/domain/katia/` — checks, instructions, reviewed messages, limits
- `src/application/interfaces/tutor.py`
- `src/application/services/katia_service.py` — the use case
- `src/infrastructure/external_api/katia_tutor.py` — provider routing and the model client
- `frontend/src/components/KatIA/SocraticChat.tsx`
- `frontend/src/pages/Student/Practice.tsx`
- `frontend/src/components/Course/CourseRail.tsx`

## Delivery *(read first)*

The docs steps (`914e8b8`, `f5cc732`, `11e59a0`) wrote the requirements with plain IDs, like
spec 004, so that a docs-only pull request would block no other pull request touching the files
above (LuisJRubioH/LevelUp-ELO#55 and #57 touch `api/routers/ai.py`). The implementing commits on
the same branch made every ID bold and filled § Traceability; the IDs did not change.

Found while doing so: a spec with no bold requirement fails
`tests/unit/scripts/test_check_traceability.py::test_the_repository_specs_pass_the_static_checks`
(it requires every spec to define at least one checked requirement), so a plain-ID docs PR is red
in the unit job — spec 004's draft (#58) included.

## Clarifications

### Session 2026-10-13 (owner decisions on block 6, recorded before `/speckit-specify`)

- Q: What may KatIA do? → A: guide without giving the answer, before and after the student
  answers: explain concepts, ask questions, suggest intermediate steps. She may not give the
  result, point to or confirm the correct option, solve the exercise completely, or reveal the
  solution by successive elimination (point 1; FR-001 … FR-005).
- Q: What happens to today's prompt rules that congratulate a correct proposal and explain why
  an option is a distractor? → A: removed. The student's free message travels as a turn of its
  own, apart from the tutor's instructions (point 1; FR-001, FR-002).
- Q: Does KatIA receive the correct option? → A: not before the student answers: she gets the
  statement and the options without the key. After an answer the server verified for the
  corresponding attempt, she may get it as an internal reference, which does not authorise
  revealing it. Having answered the same item in the past does not unlock it in a new attempt
  (point 2; FR-006 … FR-008).
- Q: How are replies checked? → A: on the server, before the student sees them. A literal search
  for `correct_option` is a complement, not a guarantee: indirect confirmations, equivalent
  expressions, identification by position, elimination and revelation accumulated over several
  turns are also evaluated. A rejected reply becomes a revised conceptual help, preferring
  reviewed hints where they exist (point 3; FR-009 … FR-017).
- Q: Can prompts and filters guarantee that no solution is ever revealed? → A: no. The limits of
  free generation are documented (§ Known limits) and the guarantee is never declared met because
  some examples pass (point 3; SC-005).
- Q: Where does the exercise come from? → A: the browser sends the exercise's id, the student's
  message and the minimum context; the server checks the student's access to the exercise and
  reads the academic data from the official store. Text the browser sends is never used as the
  statement. The message and the history admitted are limited (point 4; FR-018 … FR-024).
- Q: KatIA during exams? → A: hidden in the exam screen and refused by the server for any item of
  the student's open exam, whatever screen or direct call asks, from the server's exam state —
  never a flag from the browser (point 5; FR-025, FR-026).
- Q: Who chooses the provider? → A: with the system key, the server, from its validated
  configuration; the browser cannot change the provider or the destination of that key. A
  student's own key, if any, keeps a separate flow. Keys never appear in logs, responses or error
  messages (point 6; FR-027 … FR-030).
- Q: Consumption limits? → A: V2 applies the configured Socratic limit, documented as 120 output
  tokens, instead of the fixed 4096; changing it needs pedagogical examples and an explicit
  agreement. The request limit already in `redesign` is kept and tested. The message and history
  limits are configurable. Errors and cut-off replies are handled so the student understands them
  (point 7; FR-031 … FR-037).
- Q: A larger model? → A: not approved. The current model is compared with an alternative on
  representative bank items — mathematical accuracy, compliance with the no-reveal rule, latency,
  estimated cost — and the results are presented before any decision. A larger model does not
  replace the pedagogical controls (point 8; § Model evaluation).
- Q: Tests? → A: direct requests for the solution, successive proposed options, malicious
  instructions inside the message, requests for a complete resolution and multi-turn
  conversations, in every supported language (es, en); plus access, statement from the server,
  exam block, provider selection and consumption limits. Backend-control tests are kept apart
  from evaluations with real model replies. Documentation that attributes V1-only validation to
  V2 is corrected (point 9; § Traceability, § Model evaluation).

### Decisions this spec takes where block 6 leaves room (recommended; the owner may change them)

| ID | Decision | Why | Requirement |
|---|---|---|---|
| K1 | "Access to the exercise" = the item exists, the student is enrolled in its course (spec 001 FR-037) **and the item was served to that student** by `next-question` (practice or course map). Otherwise 409. | Point 2 needs a server record of the attempt the help belongs to; the same record stops KatIA being used on arbitrary bank items (point 4, "consumption outside KatIA's purpose"). Both KatIA entry points get their item from `next-question`. | FR-019, FR-020, FR-022 |
| K2 | Defaults: message ≤ 500 characters; ≤ 4 previous turns as context; ≤ 12 turns per serving; after 3 flagged turns in a serving, only reviewed hints. All configurable. | Bounded cost per item; repeated extraction attempts stop reaching the model. | FR-023, FR-024, FR-016, FR-034 |
| K3 | A proposed option or a request for the answer is answered with a reviewed redirect **without calling the model**, identical whichever option is correct. | Closes the enumeration oracle deterministically (Appendix A1); "explain how you got there" is itself a Socratic reply. | FR-003 … FR-005 |
| K4 | The validator is strict: a false positive costs a reviewed hint instead of the model's reply. Each turn stores its outcome so the rejection rate can be measured. | Point 3 forbids declaring the guarantee from examples; the stored outcomes are the evidence. | FR-009, FR-037 |
| K5 | No bank item has reviewed hints today (2031 items, no hint field). The reviewed help is a fixed, human-written set per language; per-item hints are a follow-up for spec 008. | "Prefer reviewed hints where they exist." | FR-017 |
| K6 | The history the model sees is the server's record of this serving's accepted turns; the API accepts no history from the client. | Point 4 limits the history admitted; a client-supplied history could hide accumulated revelation. | FR-023 |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - KatIA helps me think, and never hands me the answer (Priority: P1)

A student working on a practice item asks KatIA for help. She explains, asks questions and
suggests an intermediate step. Asked for the answer, offered options one by one, told to ignore
her rules or to solve everything, she redirects the student to their own reasoning; a reply of
the model that gives the answer away never reaches the student.

**Why this priority**: today the prompt itself tells the model to congratulate a correct proposal
and to explain why a wrong one is a distractor, so typing each option reveals the key
(Appendix A1). Ratings earned that way measure nothing.

**Independent Test**: with a fake model on the API, send each kind of message in Spanish and in
English and inspect what the model received, what the student received and what was stored.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** an item served to the student and not yet answered, **When** they ask
   KatIA a question, **Then** the model receives the bank's statement and options, the student's
   message as a separate turn after the instructions, and nothing that tells which option is
   correct (the request is identical whichever option is the key).
2. **US1-AS2** — **Given** that item, **When** the student proposes options one after another, by
   letter, by position or by their content, in Spanish or English, **Then** every reply is a
   reviewed redirect that does not depend on which option is correct, and the model is not called.
3. **US1-AS3** — **Given** that item, **When** the student asks for the answer, for the correct option
   or for the complete solution, in Spanish or English, **Then** the reply is a reviewed redirect
   and the model is not called.
4. **US1-AS4** — **Given** that item, **When** the student's message tells KatIA to ignore or change
   her instructions, in Spanish or English, **Then** the reply is a reviewed redirect and the model
   is not called.
5. **US1-AS5** — **Given** a model reply that states the correct option, an equal value, an option by
   letter or position, a verdict on a proposal, an eliminated option or a worked solution, **When**
   the server checks it, **Then** the student receives a reviewed conceptual hint instead, and the
   rejected text is neither shown nor stored.
6. **US1-AS6** — **Given** a conversation on one serving where KatIA's accepted replies already carry
   intermediate equations, **When** a new reply would complete a worked solution across turns,
   **Then** it is rejected like a single-turn solution; and **Given** three flagged turns in a
   serving, **When** the student writes again, **Then** KatIA answers with a reviewed hint without
   calling the model.

---

### User Story 2 - After I answer, KatIA can use the solution, still without revealing it (Priority: P1)

Once the server has recorded the student's answer to the item they are looking at, KatIA may
know the correct option to guide precisely; the reply rules do not change. A new serving of the
same item starts locked again.

**Why this priority**: block 6 point 2 — precise help after answering without opening a way to
the key on a later attempt.

**Independent Test**: serve an item, ask KatIA, answer through `/answer`, ask again; serve the
same item again and ask before answering; compare what the model received each time.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** the student answered the serving they are looking at, **When** they ask
   KatIA, **Then** the model's instructions carry the correct option as an internal reference
   marked not to be revealed.
2. **US2-AS2** — **Given** the student answered an earlier serving of the same item and the item is
   served again, **When** they ask before answering the new serving, **Then** the model receives
   no key.
3. **US2-AS3** — **Given** the student answered, **When** the model's reply states the correct option,
   **Then** it is rejected and replaced as in US1-AS5.

---

### User Story 3 - KatIA works on my exercise, with the server's data (Priority: P1)

KatIA answers only about an exercise the student was served in a course they are enrolled in,
with the statement and options from the bank, a bounded message and a bounded history kept by
the server.

**Why this priority**: today the statement is whatever the browser sends and any item id works,
so KatIA is a free general-purpose model on the system key (Appendix A3).

**Independent Test**: on the API, ask about an item with a different `item_content`, about a
course the student is not enrolled in, about an item never served, about an unknown id, with an
over-long message and after several turns; check statuses, the model's input and storage.

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** a served item, **When** the request carries some other text as the
   statement, **Then** the model receives the bank's statement and never the client's text.
2. **US3-AS2** — **Given** a student not enrolled in the item's course, **When** they ask KatIA about
   it, **Then** the request is refused as forbidden, the model is not called and nothing is stored.
3. **US3-AS3** — **Given** an item of an enrolled course never served to the student, **When** they ask
   about it, **Then** the request is refused as a conflict and the model is not called.
4. **US3-AS4** — **Given** an unknown item id, **When** the student asks about it, **Then** not found.
5. **US3-AS5** — **Given** a message longer than the configured limit, **When** it is sent, **Then** it
   is refused with a clear reason and the model is not called.
6. **US3-AS6** — **Given** a serving with more accepted turns than the configured history, **When** the
   student asks again, **Then** the model receives only the latest configured number of turns of
   that serving, from the server's record.

---

### User Story 4 - No KatIA on exam questions (Priority: P1)

KatIA is absent from the exam screen, and the server refuses her for any item of the student's
open exam, from any screen or a direct call.

**Why this priority**: the exam is evaluative (spec 001 FR-032); help there falsifies it.

**Independent Test**: start an exam, serve one of its items in practice too, ask KatIA about it;
submit the exam, ask again; let another exam expire, ask again.

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** an open exam of the student containing an item, **When** they ask KatIA
   about that item — even served in practice, even with any client flag — **Then** it is refused as
   forbidden, the model is not called and nothing is stored.
2. **US4-AS2** — **Given** that exam submitted, or expired, **When** they ask about the item served in
   practice, **Then** KatIA answers.
3. **US4-AS3** — **Given** the exam screen, **Then** it offers no KatIA.

---

### User Story 5 - The server decides where the system's key goes (Priority: P2)

With the system key, provider and model come from the server's configuration; a browser cannot
redirect the key. A student's own key goes only to the provider it belongs to. No key ever
appears in a log, a response or an error.

**Why this priority**: today the browser's `provider` picks the destination of the system key,
including `localhost` providers (Appendix A4).

**Independent Test**: on the API with a fake transport, vary `SYSTEM_AI_PROVIDER`, the system key,
the student's key and the requested provider; record the destination; make the provider fail with
the key in its error text.

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** the system key, **When** the request names another provider, **Then** the
   key goes to the configured provider (or, when none is configured, to the provider its prefix
   identifies) with that provider's default model.
2. **US5-AS2** — **Given** a configured provider that is not a supported cloud provider or contradicts
   the system key's prefix, **When** the student asks, **Then** KatIA is unavailable and the key is
   sent nowhere.
3. **US5-AS3** — **Given** the student's own key, **When** they ask, **Then** it goes only to the cloud
   provider its prefix identifies — or, for an unrecognised prefix, to the cloud provider named in
   the request — and never to a local provider.
4. **US5-AS4** — **Given** a provider failure whose text contains the key, **When** the student asks,
   **Then** the chat shows a plain message and neither the response, the server log nor the stored
   history contains the key.

---

### User Story 6 - Bounded consumption and understandable errors (Priority: P2)

Each reply is short and bounded; a burst of requests, an exhausted serving or a cut-off reply is
handled so the student knows what happened.

**Why this priority**: the system key's cost and the student's experience (block 6 point 7).

**Independent Test**: inspect the model's token limit; return a cut-off reply; send eleven
requests in a minute; exhaust a serving's turns; trigger each refusal in the chat in both
languages.

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** any accepted request, **Then** the model is asked for at most the configured
   number of output tokens (120 by default).
2. **US6-AS2** — **Given** a reply cut off by that limit, **Then** the student receives its complete
   sentences, or a reviewed hint when none is complete.
3. **US6-AS3** — **Given** ten KatIA requests in a minute from one session, **When** an eleventh
   arrives, **Then** it is refused as too many requests and the chat says to wait.
4. **US6-AS4** — **Given** a serving that reached the configured number of turns, **When** the student
   writes again, **Then** KatIA answers with a fixed closing message without calling the model.
5. **US6-AS5** — **Given** each refusal (not enrolled, open exam, not served, message too long, too
   many requests, KatIA unavailable), **Then** the chat shows a translated message (es, en), never a
   raw status or an internal detail.

### Edge Cases

- **Text of the statement in a reply.** A value or option that already appears in the statement
  does not count as a mention: KatIA may quote the statement. If the correct option itself is
  written in the statement, a literal check cannot see it (§ Known limits).
- **Short options** (`4`, `x`, `Sí`). A distractor of one or two characters is a mention only next
  to a verdict or an elimination ("no es 4"); the correct option is a mention anywhere outside the
  statement. Longer options are mentions anywhere.
- **The student proposes an option inside a genuine question** ("¿por qué no puede ser $2x$?"). It
  is a proposal (US1-AS2): KatIA asks for the student's reasoning instead.
- **An answer submitted outside the response-time window** (spec 001 FR-008) is still a submitted
  answer for the serving: the attempt is recorded by the server, so US2-AS1 applies.
- **An idempotent retry of `/answer`** creates no second attempt; the serving stays answered.
- **Two tabs.** A serving belongs to the student and the item, not to a tab: both see the same
  conversation record and the same answered state.
- **Items served before this change** have no serving record: KatIA refuses them (409) until the
  student asks for the next question. The chat says to continue practising.
- **The model provider is down**: no turn is stored and no rating changes (#57 behaviour kept,
  FR-035).
- **V1 (Streamlit)** keeps its own KatIA path (§ Out of Scope).

## Requirements *(mandatory)*

### Functional Requirements

**The pedagogical rule (US1)**

- **FR-001** [CHANGE]: The system shall instruct the tutor model, on every request, that it may
  explain concepts, ask questions and suggest an intermediate step, and that it must not give the
  result, say or hint which option is correct or incorrect, name an option by letter or position,
  eliminate options or solve the exercise completely; the instructions shall contain no rule that
  rewards a correct proposal or analyses a distractor.
- **FR-002** [CHANGE]: The system shall send the student's message to the tutor model as a separate
  user turn after the tutor's instructions, never inside them.
- **FR-003** [CHANGE]: If a student's message asks for the answer, the correct option or a complete
  solution, then the system shall reply with a reviewed redirect in the conversation's language
  without calling the tutor model.
- **FR-004** [CHANGE]: If a student's message proposes an option — by letter, by position or by its
  content — then the system shall reply with a reviewed redirect that does not depend on which
  option is correct, without calling the tutor model.
- **FR-005** [CHANGE]: If a student's message tries to change or reveal the tutor's instructions, then
  the system shall reply with a reviewed redirect without calling the tutor model.

**What KatIA receives (US2)**

- **FR-006** [CHANGE]: While the current serving of an item has no answer from the student, the system
  shall give the tutor model the item's statement and options without indicating the correct one.
- **FR-007** [CHANGE]: When the student has an answer recorded by the server for the current serving
  of the item, the system shall add the correct option to the tutor's instructions as an internal
  reference that must not be revealed or confirmed.
- **FR-008** [CHANGE]: The system shall treat an answer to an earlier serving of the same item as no
  answer for the current serving.

**Checking the reply (US1)**

- **FR-009** [CHANGE]: The system shall check every reply of the tutor model on the server before it is
  shown or stored; a rejected reply is never shown nor stored.
- **FR-010** [CHANGE]: If a reply contains the correct option's text, after normalising LaTeX and
  spacing, or a number equal to the correct option's value, and that text or number is not part of
  the statement, then the system shall reject it.
- **FR-011** [CHANGE]: If a reply refers to an option by letter or by position, then the system shall
  reject it.
- **FR-012** [CHANGE]: If a reply mentions another option's text of three or more characters not
  present in the statement, or negates or discards any option, then the system shall reject it.
- **FR-013** [CHANGE]: If a reply passes a verdict on a proposal — a confirmation or a rejection such as
  "correcto", "así es", "vas bien", "no es esa", "that's right", "not quite" — then the system shall
  reject it.
- **FR-014** [CHANGE]: If a reply presents a worked solution — step labels, "la respuesta es" / "the
  answer is", or three or more equations not taken from the statement — then the system shall
  reject it.
- **FR-015** [CHANGE]: If the equations not taken from the statement across the serving's accepted
  replies and the new reply reach four, then the system shall reject the new reply.
- **FR-016** [CHANGE]: While a serving has the configured number of flagged turns (redirected messages
  or rejected replies; 3 by default), the system shall answer with reviewed hints without calling
  the tutor model.
- **FR-017** [CHANGE]: When a reply is rejected, the system shall show a reviewed conceptual hint in the
  conversation's language instead.

**The exercise comes from the server (US3)**

- **FR-018** [CHANGE]: The system shall read the statement, options, topic and course of the item from
  the item store and ignore any statement or history text the client sends.
- **FR-019** [CHANGE]: If the student is not enrolled in the item's course, then the system shall refuse
  the request as forbidden, without calling the tutor model or storing anything.
- **FR-020** [CHANGE]: If the item was never served to the student, then the system shall refuse the
  request as a conflict, without calling the tutor model or storing anything.
- **FR-021** [AS-IS]: If the item does not exist, then the system shall refuse the request as not found.
- **FR-022** [CHANGE]: When `next-question` serves an item, the system shall record the serving: the
  student, the item, its course and the student's latest recorded attempt at that moment.
- **FR-023** [CHANGE]: The system shall give the tutor model at most the configured number of previous
  accepted turns of the current serving (4 by default), read from its own record.
- **FR-024** [CHANGE]: If the student's message is longer than the configured limit (500 characters by
  default), then the system shall refuse it with a reason, without calling the tutor model.

**Exams (US4)**

- **FR-025** [CHANGE]: While an item belongs to an exam session of the student that is neither
  submitted nor expired, the system shall refuse KatIA requests about that item as forbidden,
  without calling the tutor model or storing anything.
- **FR-026** [AS-IS]: The exam screen shall offer no KatIA.

**Provider and keys (US5)**

- **FR-027** [CHANGE]: While a request uses the system key, the system shall send it to the provider
  set in `SYSTEM_AI_PROVIDER`, or, when that is empty, to the provider the key's prefix identifies,
  with that provider's default model, and shall ignore the provider the client names.
- **FR-028** [CHANGE]: If the system key's provider is not a supported cloud provider or contradicts the
  key's prefix, then the system shall report KatIA as unavailable without sending the key.
- **FR-029** [CHANGE]: Where the student supplies their own key, the system shall send it only to the
  cloud provider its prefix identifies, or, for an unrecognised prefix, to the cloud provider the
  client names, and never to a local provider.
- **FR-030** [CHANGE]: The system shall keep API keys out of logs, responses, error messages and stored
  turns.

**Consumption and errors (US6)**

- **FR-031** [CHANGE]: The system shall ask the tutor model for at most the configured number of output
  tokens per reply (120 by default, the documented Socratic limit).
- **FR-032** [CHANGE]: If a reply is cut off by the token limit, then the system shall keep only its
  complete sentences, and show a reviewed hint when none remains.
- **FR-033** [AS-IS]: The system shall accept at most the configured number of KatIA requests per
  signed-in session and minute (10 by default) and refuse the rest as too many requests.
- **FR-034** [CHANGE]: If a serving has reached the configured number of turns (12 by default), then the
  system shall answer with a fixed closing message without calling the tutor model.
- **FR-035** [AS-IS]: If the tutor model fails, then the system shall send the chat an error event with
  a plain message and store nothing.
- **FR-036** [CHANGE]: The chat shall show a translated message (es, en) for each refusal — not
  enrolled, open exam, not served, message too long, too many requests, unavailable — never a raw
  status or internal detail.
- **FR-037** [CHANGE]: The system shall store, with each turn, the serving it belongs to and its
  outcome: accepted, redirected (with its reason), rejected (with its reasons), cut off, or closed.

### Key Entities

- **Serving**: one delivery of an item to a student by `next-question`: student, item, course, and
  the student's latest attempt at that moment. The current serving of an item is the latest one;
  it is answered when the student has an attempt on the item after that mark.
- **KatIA turn** (`katia_interactions`): the student's message, the text the student was shown,
  the serving and the outcome. Teachers read and export these turns.
- **Open exam**: an exam session of the student neither submitted nor expired
  (`active_exam_sessions`).
- **Reviewed message**: a fixed, human-written redirect or hint per language, versioned in code.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every item and both languages, the request the model receives before an answer
  is byte-identical whichever option is marked correct.
- **SC-002**: Every scripted extraction attempt in § Traceability (direct request, successive
  options, malicious instruction, complete resolution, multi-turn) ends with no reply that the
  server's checks identify as revealing, in es and en.
- **SC-003**: Zero calls to the model for requests refused by access, exam, serving, length,
  turn-cap or rate limits.
- **SC-004**: The model's output limit is 120 tokens in every V2 KatIA request, against 4096 today.
- **SC-005**: No document in the repository claims that KatIA can never reveal a solution; the
  limits in § Known limits are stated wherever the guardrails are described.

## Known limits of free generation *(normative for every document that describes KatIA)*

Neither the instructions nor the checks guarantee that KatIA never reveals a solution:

- Algebraically equivalent forms that differ from the option after normalisation (factored vs
  expanded, rewritten identities) are not detected. Symbolic algebra is not run on model output:
  the available parser evaluates code and the output is influenced by the student.
- A hint can make the answer obvious without naming it; tone can differ between proposals the
  model sees in paraphrase. Proposals that name an option never reach the model (FR-004), but a
  paraphrase that matches no option's text does.
- Wording outside the listed verdicts and markers passes; a value written in the statement cannot
  be told apart from the answer. In the bank of 2026-10-13, **125 of 2031 items (6 %)** write
  their key's text inside the statement: for them the literal check is blind, and a proposal of
  the key is recognised only with a cue ("¿es …?", "da …").
- Before an answer the model does not get the key, but it can solve the exercise itself.

What reduces the risk is measured, not assumed: each turn stores its outcome (FR-037) and the
model evaluation (§ Model evaluation) reports leak rates on real replies. Passing tests prove the
controls behave as written; they do not prove the guarantee.

Measured over every bank item (pinned by
`tests/unit/domain/test_spec005_guardrails.py::test_spec005_the_checks_hold_over_every_bank_item`):
neutral Socratic replies in es and en and a verbatim quote of the statement pass, two genuine
questions are never redirected, "¿Es <key>?" is always recognised and "La respuesta es <key>"
always rejected. The first run of that probe rejected **every** neutral reply (adverbs such as
"exactly" read as verdicts; prose options compared without spaces, so "en un caso" contained
"Nunca") — the reason strictness is measured on the whole bank and not on hand-picked examples.

## Model evaluation *(block 6 point 8; not a system behaviour)*

No change of model is approved. Before one is proposed, the current model (Groq
`llama-3.1-8b-instant`) is compared with an alternative on representative bank items, through
the same prompt and checks as production:

- mathematical accuracy: the model chooses the correct option when asked to solve the item;
- no-reveal compliance: share of raw replies the checks reject, by reason, under the scripted
  extraction attempts in es and en, plus a sample of accepted replies for human review;
- latency: p50 and p95 per reply;
- estimated cost: input and output tokens per reply times the provider's price at the date of
  the run.

These evaluations call real models and are kept apart from the backend tests: they never run in
CI, need a key, and their report is presented to the owner before any decision. The harness is
`scripts/evaluate_katia_models.py` (its arithmetic is unit-tested with a fake model); protocol,
command and the place for results: `docs/sdd/katia-model-evaluation.md`.

## Assumptions

- Both KatIA entry points in V2 (practice and the course map) obtain their item from
  `next-question` (Appendix A5).
- The current model and providers stay as configured; only how they are chosen changes.
- `es` and `en` are the supported languages (`frontend/src/i18n`).

## Out of Scope *(mandatory)*

- Procedure review, student and teacher AI analyses — the rest of the roadmap's spec 005 area.
- V1 (Streamlit) KatIA: frozen (roadmap); it keeps its own prompt with the key and its V1-only
  check (Appendix A6). Retiring V1 is in the pre-opening checklist.
- Changing the model or the 120-token limit (§ Model evaluation; block 6 points 7–8).
- Per-item reviewed hints in the bank (K5) — a schema change for spec 008.
- Blocking practice itself during an exam (only KatIA is refused here).
- Lessons' scripted KatIA messages (spec 003): no model is involved.
- Blocks 4, 5, 7 and 8 of the owner's brief.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario. Reuse adequate existing tests; create or strengthen tests where coverage is missing.**

Backend-control tests use a fake model and run in CI; Playwright tests mock the API and verify
the chat's behaviour. Evaluations with real model replies live in § Model evaluation and are
never cited here. Each `[CHANGE]` test failed on the base before its implementation; the
`[AS-IS]` pins (FR-021, FR-026, FR-033, FR-035) passed on it.

| Requirement / Scenario | Test |
|---|---|
| FR-001 | `tests/unit/domain/test_spec005_tutor_prompt.py::test_spec005_instructions_state_what_katia_may_and_may_not_do`<br>`tests/unit/domain/test_spec005_tutor_prompt.py::test_spec005_instructions_reward_no_proposal_and_analyse_no_distractor` |
| FR-002 | `tests/unit/domain/test_spec005_tutor_prompt.py::test_spec005_the_message_is_its_own_last_turn`<br>`tests/api/test_spec005_katia_api.py::test_spec005_the_model_gets_the_stores_exercise_and_no_key` |
| FR-003 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_requests_for_the_answer_are_redirected`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_flagged_messages_get_a_reviewed_redirect`<br>`tests/api/test_spec005_katia_api.py::test_spec005_requests_for_the_answer_and_overrides_never_reach_the_model` |
| FR-004 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_proposed_options_are_recognised`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_short_numeric_proposals_are_recognised`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_short_word_proposals_need_a_cue`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_genuine_questions_are_not_flagged`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_a_number_from_the_statement_is_not_a_proposal`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_proposing_each_option_gets_the_same_reply_whichever_is_correct`<br>`tests/api/test_spec005_katia_api.py::test_spec005_successive_options_get_the_same_redirect_whichever_is_correct` |
| FR-005 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_instruction_overrides_are_recognised`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_flagged_messages_get_a_reviewed_redirect`<br>`tests/api/test_spec005_katia_api.py::test_spec005_requests_for_the_answer_and_overrides_never_reach_the_model` |
| FR-006 | `tests/unit/domain/test_spec005_tutor_prompt.py::test_spec005_before_an_answer_the_request_is_the_same_whichever_option_is_correct`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_before_an_answer_the_model_gets_no_key`<br>`tests/api/test_spec005_katia_api.py::test_spec005_before_an_answer_the_request_does_not_depend_on_the_key` |
| FR-007 | `tests/unit/domain/test_spec005_tutor_prompt.py::test_spec005_after_an_answer_the_key_is_an_internal_reference`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_after_an_answer_to_this_serving_the_key_is_a_reference`<br>`tests/api/test_spec005_katia_api.py::test_spec005_after_answering_this_serving_the_key_is_a_reference` |
| FR-008 | `tests/integration/test_spec005_katia_store.py::test_spec005_a_serving_is_answered_only_by_a_later_attempt`<br>`tests/api/test_spec005_katia_api.py::test_spec005_an_answer_to_an_earlier_serving_unlocks_nothing` |
| FR-009 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_a_revealing_reply_is_replaced_and_never_stored`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_revealing_reply_is_replaced_before_anyone_sees_it` |
| FR-010 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_the_correct_option_text_is_rejected`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_a_value_equal_to_the_key_is_rejected`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_values_of_the_statement_and_exponents_are_not_the_key`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_a_short_word_key_counts_only_with_a_cue`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_the_checks_hold_over_every_bank_item` |
| FR-011 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_options_named_by_position_are_rejected` |
| FR-012 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_another_options_text_is_rejected`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_eliminations_are_rejected` |
| FR-013 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_verdicts_are_rejected`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_socratic_replies_pass`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_the_checks_hold_over_every_bank_item` |
| FR-014 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_worked_solutions_are_rejected` |
| FR-015 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_equations_accumulated_over_the_serving_are_rejected`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_equations_accumulated_in_the_serving_reject_the_reply`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_multi_turn_conversation_cannot_assemble_the_solution` |
| FR-016 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_after_three_flagged_turns_only_reviewed_hints`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_multi_turn_conversation_cannot_assemble_the_solution` |
| FR-017 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_a_revealing_reply_is_replaced_and_never_stored`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_revealing_reply_is_replaced_before_anyone_sees_it` |
| FR-018 | `tests/api/test_spec005_katia_api.py::test_spec005_the_model_gets_the_stores_exercise_and_no_key`<br>`tests/api/test_spec005_katia_api.py::test_spec005_the_model_sees_at_most_the_configured_history`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › la petición lleva el ejercicio, el mensaje y el idioma; nunca el enunciado` |
| FR-019 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_refusals_call_no_model_and_store_nothing`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_course_the_student_is_not_enrolled_in_is_forbidden` |
| FR-020 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_refusals_call_no_model_and_store_nothing`<br>`tests/api/test_spec005_katia_api.py::test_spec005_an_item_never_served_is_a_conflict` |
| FR-021 | `tests/api/test_spec005_katia_api.py::test_spec005_unknown_item_is_not_found`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_refusals_call_no_model_and_store_nothing` |
| FR-022 | `tests/api/test_spec005_katia_api.py::test_spec005_the_model_gets_the_stores_exercise_and_no_key`<br>`tests/integration/test_spec005_katia_store.py::test_spec005_a_serving_is_answered_only_by_a_later_attempt`<br>`tests/integration/test_spec005_katia_store.py::test_spec005_the_migration_is_idempotent` |
| FR-023 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_history_is_the_servings_latest_accepted_turns`<br>`tests/api/test_spec005_katia_api.py::test_spec005_the_model_sees_at_most_the_configured_history` |
| FR-024 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_refusals_call_no_model_and_store_nothing`<br>`tests/api/test_spec005_katia_api.py::test_spec005_an_over_long_message_is_refused` |
| FR-025 | `tests/integration/test_spec005_katia_store.py::test_spec005_open_exam_items_are_those_neither_submitted_nor_expired`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_refusals_call_no_model_and_store_nothing`<br>`tests/api/test_spec005_katia_api.py::test_spec005_an_open_exams_item_is_refused_from_any_screen`<br>`tests/api/test_spec005_katia_api.py::test_spec005_after_the_exam_katia_answers_again` |
| FR-026 | `frontend/e2e/katia-chat.spec.ts › KatIA › el examen no ofrece KatIA` |
| FR-027 | `tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_system_key_goes_where_the_server_says`<br>`tests/api/test_spec005_katia_api.py::test_spec005_the_system_key_goes_where_the_server_says` |
| FR-028 | `tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_an_invalid_system_configuration_sends_the_key_nowhere`<br>`tests/api/test_spec005_katia_api.py::test_spec005_an_invalid_system_provider_disables_katia` |
| FR-029 | `tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_students_key_goes_only_to_its_provider`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_students_unrecognised_key_needs_a_cloud_provider`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_students_key_goes_only_to_its_provider`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › en el mapa usa la key y el proveedor del estudiante` |
| FR-030 | `tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_failure_carries_a_code_and_never_the_key`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_provider_failure_never_shows_the_key`<br>`tests/api/test_spec005_katia_api.py::test_spec005_an_invalid_system_provider_disables_katia` |
| FR-031 | `tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_the_model_is_asked_for_the_configured_output_limit`<br>`tests/api/test_spec005_katia_api.py::test_spec005_the_model_is_asked_for_120_output_tokens` |
| FR-032 | `tests/unit/domain/test_spec005_guardrails.py::test_spec005_cut_off_reply_keeps_complete_sentences`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_a_period_inside_math_does_not_end_a_sentence`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_reply_cut_by_the_limit_is_flagged`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_anthropic_replies_report_truncation`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_a_cut_off_reply_keeps_its_complete_sentences`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_a_cut_off_reply_with_no_complete_sentence_becomes_a_hint`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_cut_off_reply_shows_its_complete_sentences` |
| FR-033 | `tests/api/test_rate_limit.py::test_socratic_rate_limit_is_enforced_per_access_token` |
| FR-034 | `tests/unit/application/test_spec005_katia_service.py::test_spec005_a_serving_closes_after_its_turns`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_english_conversations_get_english_reviewed_texts`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_serving_closes_after_twelve_turns` |
| FR-035 | `tests/api/test_ai_errors_and_scores.py::test_a_provider_failure_is_not_katias_reply`<br>`tests/api/test_ai_errors_and_scores.py::test_an_unexpected_failure_shows_no_internal_detail`<br>`tests/api/test_ai_errors_and_scores.py::test_a_reply_is_streamed_and_saved`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_a_model_failure_stores_nothing`<br>`tests/api/test_spec005_katia_api.py::test_spec005_a_model_failure_is_an_error_event_and_stores_nothing` |
| FR-036 | `frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: exam_active`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: not_served`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: not_enrolled`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: message_too_long`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: 429`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › en inglés, el rechazo del examen se explica en inglés` |
| FR-037 | `tests/integration/test_spec005_katia_store.py::test_spec005_turns_are_read_by_serving_with_their_outcome`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_flagged_messages_get_a_reviewed_redirect`<br>`tests/api/test_spec005_katia_api.py::test_spec005_the_model_gets_the_stores_exercise_and_no_key` |
| US1-AS1 | `tests/api/test_spec005_katia_api.py::test_spec005_the_model_gets_the_stores_exercise_and_no_key`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_before_an_answer_the_model_gets_no_key` |
| US1-AS2 | `tests/api/test_spec005_katia_api.py::test_spec005_successive_options_get_the_same_redirect_whichever_is_correct`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_proposing_each_option_gets_the_same_reply_whichever_is_correct` |
| US1-AS3 | `tests/api/test_spec005_katia_api.py::test_spec005_requests_for_the_answer_and_overrides_never_reach_the_model`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_requests_for_the_answer_are_redirected` |
| US1-AS4 | `tests/api/test_spec005_katia_api.py::test_spec005_requests_for_the_answer_and_overrides_never_reach_the_model`<br>`tests/unit/domain/test_spec005_guardrails.py::test_spec005_instruction_overrides_are_recognised` |
| US1-AS5 | `tests/api/test_spec005_katia_api.py::test_spec005_a_revealing_reply_is_replaced_before_anyone_sees_it`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_a_revealing_reply_is_replaced_and_never_stored` |
| US1-AS6 | `tests/api/test_spec005_katia_api.py::test_spec005_a_multi_turn_conversation_cannot_assemble_the_solution`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_equations_accumulated_in_the_serving_reject_the_reply`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_after_three_flagged_turns_only_reviewed_hints` |
| US2-AS1 | `tests/api/test_spec005_katia_api.py::test_spec005_after_answering_this_serving_the_key_is_a_reference` |
| US2-AS2 | `tests/api/test_spec005_katia_api.py::test_spec005_an_answer_to_an_earlier_serving_unlocks_nothing`<br>`tests/integration/test_spec005_katia_store.py::test_spec005_a_serving_is_answered_only_by_a_later_attempt` |
| US2-AS3 | `tests/api/test_spec005_katia_api.py::test_spec005_after_answering_a_revealing_reply_is_still_replaced` |
| US3-AS1 | `tests/api/test_spec005_katia_api.py::test_spec005_the_model_gets_the_stores_exercise_and_no_key` |
| US3-AS2 | `tests/api/test_spec005_katia_api.py::test_spec005_a_course_the_student_is_not_enrolled_in_is_forbidden` |
| US3-AS3 | `tests/api/test_spec005_katia_api.py::test_spec005_an_item_never_served_is_a_conflict` |
| US3-AS4 | `tests/api/test_spec005_katia_api.py::test_spec005_unknown_item_is_not_found` |
| US3-AS5 | `tests/api/test_spec005_katia_api.py::test_spec005_an_over_long_message_is_refused` |
| US3-AS6 | `tests/api/test_spec005_katia_api.py::test_spec005_the_model_sees_at_most_the_configured_history`<br>`tests/unit/application/test_spec005_katia_service.py::test_spec005_history_is_the_servings_latest_accepted_turns` |
| US4-AS1 | `tests/api/test_spec005_katia_api.py::test_spec005_an_open_exams_item_is_refused_from_any_screen`<br>`tests/integration/test_spec005_katia_store.py::test_spec005_open_exam_items_are_those_neither_submitted_nor_expired` |
| US4-AS2 | `tests/api/test_spec005_katia_api.py::test_spec005_after_the_exam_katia_answers_again` |
| US4-AS3 | `frontend/e2e/katia-chat.spec.ts › KatIA › el examen no ofrece KatIA` |
| US5-AS1 | `tests/api/test_spec005_katia_api.py::test_spec005_the_system_key_goes_where_the_server_says`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_system_key_goes_where_the_server_says` |
| US5-AS2 | `tests/api/test_spec005_katia_api.py::test_spec005_an_invalid_system_provider_disables_katia`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_an_invalid_system_configuration_sends_the_key_nowhere` |
| US5-AS3 | `tests/api/test_spec005_katia_api.py::test_spec005_a_students_key_goes_only_to_its_provider`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_students_key_goes_only_to_its_provider`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_students_unrecognised_key_needs_a_cloud_provider` |
| US5-AS4 | `tests/api/test_spec005_katia_api.py::test_spec005_a_provider_failure_never_shows_the_key`<br>`tests/unit/infrastructure/test_spec005_katia_tutor.py::test_spec005_a_failure_carries_a_code_and_never_the_key` |
| US6-AS1 | `tests/api/test_spec005_katia_api.py::test_spec005_the_model_is_asked_for_120_output_tokens` |
| US6-AS2 | `tests/api/test_spec005_katia_api.py::test_spec005_a_cut_off_reply_shows_its_complete_sentences` |
| US6-AS3 | `tests/api/test_rate_limit.py::test_socratic_rate_limit_is_enforced_per_access_token`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: 429` |
| US6-AS4 | `tests/api/test_spec005_katia_api.py::test_spec005_a_serving_closes_after_twelve_turns` |
| US6-AS5 | `frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: exam_active`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: not_served`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: not_enrolled`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: message_too_long`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › un rechazo se explica en el chat: 429`<br>`frontend/e2e/katia-chat.spec.ts › KatIA › en inglés, el rechazo del examen se explica en inglés` |

## Appendix — As-is evidence

Cited at `redesign @ 1d6fcf6` with #56 and #57 merged.

- **A1** The student's free message fills the slot "Opción que el estudiante TIENE SELECCIONADA"
  (`src/infrastructure/external_api/ai_client.py:464`) and rule 2 says "Si … es la correcta,
  felicita sutilmente su intuición" (`:469`), rule 3 explains a distractor: proposing each option
  reveals the key. The message is interpolated into the prompt text (`:447-477`).
- **A2** `/ai/socratic` reads `correct_option` and sends it on every request
  (`api/routers/ai.py:74`, `:104-117`); `validate_socratic_response` is called only by V1
  (`src/interface/streamlit/views/student_view.py:1168`), although `AGENTS.md:609-610` and
  `README.md:95-97` attribute it to V2.
- **A3** The statement is `body.item_content` (`api/routers/ai.py:108`), unbounded
  (`api/schemas/student.py:339`); any existing item id is accepted (`api/routers/ai.py:67`).
- **A4** The provider is `body.provider` (`api/routers/ai.py:89`), default `"groq"` in the schema and
  the store, so the key's prefix is never consulted; `PROVIDERS` includes `lmstudio` and `ollama` at
  `localhost` (`src/infrastructure/external_api/ai_client.py:49`).
- **A5** Practice and the course map's rail both take their item from `next-question`
  (`frontend/src/pages/Student/Practice.tsx`, `frontend/src/components/Course/CourseRail.tsx:107`);
  `next-question` records nothing about the serving (`api/routers/student.py:114-147`). The exam
  screen has no KatIA (`frontend/src/pages/Student/Exam.tsx:5`) but `/ai/socratic` does not check
  exams.
- **A6** V2 asks for `max_tokens=4096` (`ai_client.py:199`, `:230`) although `SOCRATIC_MAX_TOKENS=120`
  (`src/infrastructure/external_api/model_router.py:354`) is documented; the rate limit
  `10/minute` is applied (`api/routers/ai.py:39`, `tests/api/test_rate_limit.py`).
