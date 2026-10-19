# Feature Specification: Learning Path

**Feature Branch**: `003-learning-path` (one branch per delivery once implementation starts)

**Created**: 2026-10-18

**Status**: Approved by the owner, with the recommendations of N1 … N6 (2026-10-18). Written from the as-is survey
(`docs/sdd/learning-path-survey.md`, LuisJRubioH/LevelUp-ELO#13) and the owner's decisions of
2026-10-18 (its § 7). Nothing in deliveries L1 … L5 is implemented.

**Input**: Roadmap M3 (`docs/sdd/roadmap.md`): the course map, the eleven-block nodes, the unlock
chain, misconception tags and diagnostic gating. AGENTS V2-R11 … V2-R18 stay the authoring rules
for content (decision 7); this spec owns the engine.

**Outcome served** (constitution VIII): a student walks the path only in the courses they are
enrolled in, finishes a node by understanding it — right answers, not any answer — and their
teacher sees what they learned, while the answers stay on the server and nothing a minor writes
freely is stored.

## Code Scope *(mandatory)*

- `src/domain/learning/prealgebra.py` — catalogue, unlock data, map rows, interaction grading
- `api/routers/student.py` — the lesson, event, interaction, summary and map endpoints (shared
  with spec 001)
- `api/schemas/student.py` — what the lesson endpoints send (shared with spec 001)
- `frontend/src/pages/Student/Lesson.tsx`
- `frontend/src/pages/Student/CourseMap.tsx` (shared with spec 001)
- `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx`
- `frontend/src/pages/Student/lessons/blocks/LessonBlocks.tsx`

## Deliveries *(this spec is delivered in steps)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it closed and fills all its rows.

| Delivery | Content | State |
|---|---|---|
| **A** | As-is pins: what the path already guarantees, each requirement tied to a test | in progress |
| **L1** | Access: lessons and the map only for enrolled students; a teacher previews the courses of their groups, read only | planned |
| **L2** | Answer keys stay on the server | planned |
| **L3** | A node completes on right answers | planned |
| **L4** | What the teacher sees: the post-diagnostic outcome and an answer history, no free text | planned |
| **L5** | Unlock rules from data only; the map and the API share them | planned |

## Clarifications

### Session 2026-10-18 (owner decisions on the survey, § 7)

- Q: Who may open lessons and the map (L1)? → A: only students enrolled in the course, as
  spec 001 FR-037 does for practice. A teacher may preview the courses of their groups, read only,
  saving no progress.
- Q: Answer keys (L2)? → A: the grading keys leave what is sent to the browser; the server grades.
- Q: What completes a node (L3)? → A: right answers, not answers present; B01, B13 and the hubs get
  explicit rules (N1 … N3 below).
- Q: What learning data is kept (L4, L8)? → A: no free text — the students are minors. The
  post-diagnostic outcome and an answer history, right or wrong with its misconception tag, are kept
  for the teacher.
- Q: Unlock rules (L5, L6)? → A: `unlock_after` (data) is the only source; the rule "all six N2
  nodes" before N3 and the B09 rule move into data, and the map and the API read the same data.
- Q: D5 (L11)? → A: the rule names `MathContent` (KaTeX) as the way to render math; amended in
  AGENTS.md with this spec.
- Q: Scope? → A: the engine — access, map, unlock, progress, completion, and what the server sends
  and stores. Content authoring stays in AGENTS V2-R11 … V2-R18 with their existing tests.

### State of the survey's findings on 2026-10-18

The survey read `redesign @ 1d6fcf6` (2026-10-09). Since then the map never offers a node the API
refuses (LuisJRubioH/LevelUp-ELO#53, part of L5: the API's special case stays in code), progress
is read in one query (LuisJRubioH/LevelUp-ELO#22), and a multiple-answer item sends the whole
selection. Verified still present on 2026-10-18: L1 (no enrolment check on the lesson endpoints or
the map), L2 (the whole `CONTENT` is sent), L3 (completion checks presence), L4/L8 (last answer
wins, nothing else kept), L6 (hard-coded node ids, the 409 text «Responde las dos preguntas
primero» for every node), L10 (the summary endpoint has no response model).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - I walk only the paths of my courses (Priority: P1) — L1

**Why this priority**: today any signed-in user, of any role, reads and writes the progress of any
course with a path (survey L1, reproduced).

**Independent Test**: one student enrolled in the path's course and one not; each opens a lesson,
records an event and opens the map.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a student not enrolled in the course, **When** they open a lesson,
   record an event or an answer, read the summary or open the map, **Then** each is refused with
   403 «No estás inscrito en este curso.» and nothing is stored.
2. **US1-AS2** — **Given** a student enrolled in the course, **When** they do the same, **Then** it
   works as today.
3. **US1-AS3** — **Given** a teacher with a group in the course, **When** they open its lessons or
   map, **Then** they read them with every node available and no progress, and any event or answer
   they send is refused without storing anything.
4. **US1-AS4** — **Given** a teacher with no group in the course, **When** they open a lesson,
   **Then** it is refused.

### User Story 2 - The answers stay on the server (Priority: P1) — L2

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** any node, **When** a student opens it, **Then** the response holds no
   answer key: no `answer`, `expected`, `accepted`, `trap_options`,
   `misconception_by_option`, closing answer or bridge blank (`valid_options`, the list of choices,
   stays: N7).
2. **US2-AS2** — **Given** an answer sent, **When** the server grades it, **Then** the student
   still gets the same feedback as today.

### User Story 3 - A node completes when I get it right (Priority: P1) — L3

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** a node whose required items are all answered and one is wrong, **When**
   the student marks it completed, **Then** it is refused with a message naming what is missing,
   and the node stays open.
2. **US3-AS2** — **Given** every required item's latest answer right, **When** the student marks it
   completed, **Then** it completes and the next node opens.
3. **US3-AS3** — **Given** a wrong answer, **When** the student answers again right, **Then** the
   node can be completed.

### User Story 4 - My teacher sees what I learned (Priority: P2) — L4

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** a student who answered an item wrong and then right, **When** their
   teacher reads the summary, **Then** both answers appear in order, each right or wrong with its
   misconception tag.
2. **US4-AS2** — **Given** a node's post-diagnostic, **When** the student finishes it, **Then** its
   outcome is stored and the teacher sees it.
3. **US4-AS3** — **Given** any answer, **When** it is stored, **Then** it holds no free text written
   by the student.

### User Story 5 - The map and the lesson agree because they read the same rules (Priority: P2) — L5

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** the catalogue, **When** it is loaded, **Then** it has one root, no
   unlock reference to a missing node and no cycle.
2. **US5-AS2** — **Given** any progress, **When** the map shows a node available, **Then** the API
   opens it; and every node the API refuses is shown blocked.
3. **US5-AS3** — **Given** the N3 hub and the B09 rule, **When** they are evaluated, **Then** they
   come from the catalogue's data, not from node ids in code.

### User Story 6 - What already holds keeps holding (Priority: P1) — A

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** a lesson event or answer, **When** it is stored, **Then** no rating
   changes.
2. **US6-AS2** — **Given** a node whose predecessor is not completed, **When** it is opened,
   **Then** the API refuses it.
3. **US6-AS3** — **Given** every node the map offers, **When** the student opens it, **Then** it
   opens.

### Edge Cases

- **A node completed before L3** (on answers present): it stays completed; L3 applies to nodes not
  yet completed.
- **A student enrolled through an invitation** in a course outside their level (spec 001 FR-028l):
  enrolled is enrolled; the path opens.
- **A student who leaves the course**: like practice (spec 001 FR-037a), the path closes; their
  progress is kept.

## Requirements *(mandatory)*

### Functional Requirements

**As-is (A)**

- **FR-001** [AS-IS]: The system shall change no rating because of any lesson event or answer.
- **FR-002** [AS-IS]: If a node's predecessor in the unlock data is not completed, then the system
  shall refuse to open it or store anything for it.
- **FR-003** [AS-IS]: The system shall grade every interaction on the server.
- **FR-004** [AS-IS]: The system shall store a node's progress as viewed or completed and never move
  it back.
- **FR-005** [AS-IS]: The system shall show on the map, as available, only nodes the API opens.
- **FR-006** [AS-IS]: The system shall store no free-text field of an answer.

**Access (L1)**

- **FR-010** [CHANGE]: If a student who is not enrolled in the course opens a lesson, records an
  event or an answer, reads the summary or opens the map, then the system shall refuse with 403
  and store nothing.
- **FR-011** [CHANGE]: Where a teacher has a group in the course, the system shall let them read its
  lessons and map with every node available, store nothing they send, and refuse any other
  teacher.

**Answer keys (L2)**

- **FR-020** [CHANGE]: When the system sends a node's content, it shall leave out every grading key
  of its interactions.

**Completion (L3)**

- **FR-030** [CHANGE]: When a student marks an eleven-block node completed, the system shall accept
  it only if the latest answer of every required interaction is right, and otherwise refuse naming
  the items still missing. *(Today any answer present is enough, and the refusal always reads
  «Responde las dos preguntas primero».)*

**Learning record (L4)**

- **FR-040** [CHANGE]: The system shall keep every answer to an interaction, in order, with whether
  it was right and its misconception tag, instead of keeping only the last.
- **FR-041** [CHANGE]: When a student finishes a node's post-diagnostic, the system shall store its
  outcome.
- **FR-042** [CHANGE]: When a teacher reads a student's path summary for a course of their group,
  the system shall show the answer history and the post-diagnostic outcomes.

**Unlock rules (L5)**

- **FR-050** [CHANGE]: The system shall decide whether a node is open only from the catalogue's
  unlock data, and the map and the API shall use the same function.
- **FR-051** [CHANGE]: The system shall reject at load a catalogue with more than one root, an
  unlock reference to a missing node, or a cycle.

### Key Entities

- **Node**: one lesson of the path — its unlock data, its interactions and which of them are
  required to complete it.
- **Progress**: per student, course and node — viewed or completed; never moves back.
- **Answer**: per interaction, kept in order — right or wrong and its misconception tag; never free
  text.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 lesson or map responses reach a user not enrolled in the course (or not the
  teacher of a group in it), checked for every endpoint.
- **SC-002**: 0 grading keys in any lesson response, checked over every node of the catalogue.
- **SC-003**: 100 % of the nodes the map offers open, and 100 % of those it shows blocked are
  refused, over every node and a set of progress states.

## Assumptions

- One course has a path today (`algebra_basica`); the rules are written for any course that gets
  one.
- Lessons never move a rating (FR-001); ratings belong to spec 001.

## New Decisions and Contradictions

| # | Point | Recommendation |
|---|---|---|
| N1 | B01 (welcome) completes on view today. | **Approved** (owner, 2026-10-18): Keep it: it has no question. |
| N2 | B13 (closing diagnostic) has no completion check today. | **Approved** (owner, 2026-10-18): It completes when every item has an answer, right or not: a diagnostic measures, it does not gate. |
| N3 | The hubs (N2, N3, N4, A00, S00) complete when their cards are opened, some on the client only. | **Approved** (owner, 2026-10-18): One rule on the server: a hub completes when the student has opened every card. |
| N4 | L9: the map shows practice-topic nodes blocked until B08, but practice ignores the path. | **Approved** (owner, 2026-10-18): Keep practice independent of the path (spec 001) and drop the block from the map. |
| N5 | L7: three renderers are unreachable (`LevelTwoOperation`, `LevelThreeMachine`, `LevelFourConcept`), the only place showing «Resultado esperado: {answer}». | **Approved** (owner, 2026-10-18): Remove them with L2. |
| N6 | L10: the summary endpoint has no response model and does not check the course. | **Approved** (owner, 2026-10-18): Give it one and validate the course with L1. |
| N7 | `valid_options` is the list of choices a multiple-answer item shows, not a key (plan-l2). | **Approved** (owner, 2026-10-19): Keep it; US2-AS1 amended. |
| N8 | Worked-example `solution` and `correct_version` are teaching content the student is meant to see. | **Approved** (owner, 2026-10-19): Keep them in the content; FR-020 covers grading keys. |
| N9 | The abstraction question is graded in the browser (`options[].correct`, 52 nodes). | **Approved** (owner, 2026-10-19): A server-graded interaction with `required=False`; its key leaves the content. |
| N10 | Admins and the path (L1). | **Approved** (owner, 2026-10-19): An admin previews every course like a teacher, read only. |
| N11 | What the teacher sees of an answer (L4). | **Approved** (owner, 2026-10-19): Right or wrong and the misconception tag, never the chosen value. |

## Out of Scope *(mandatory)*

- Content authoring — AGENTS V2-R11 … V2-R18 and their tests (owner, decision 7).
- Ratings and practice item selection — spec 001; persistence mechanics — spec 002; the item
  bank — spec 008.
- Visual design beyond AGENTS D1 … D5.

## Traceability *(mandatory)*

Rows of delivery A cite the tests that already pin the behaviour; the rest are filled by the pull
request that closes their delivery.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | L1 | `PENDING` |
| US1-AS2 | L1 | `PENDING` |
| US1-AS3 | L1 | `PENDING` |
| US1-AS4 | L1 | `PENDING` |
| US2-AS1 | L2 | `PENDING` |
| US2-AS2 | L2 | `PENDING` |
| US3-AS1 | L3 | `PENDING` |
| US3-AS2 | L3 | `PENDING` |
| US3-AS3 | L3 | `PENDING` |
| US4-AS1 | L4 | `PENDING` |
| US4-AS2 | L4 | `PENDING` |
| US4-AS3 | L4 | `PENDING` |
| US5-AS1 | L5 | `PENDING` |
| US5-AS2 | L5 | `PENDING` |
| US5-AS3 | L5 | `PENDING` |
| US6-AS1 | A | `tests/integration/test_sqlite_repository.py::TestLessonProgress::test_lesson_events_are_idempotent_and_do_not_change_elo` |
| US6-AS2 | A | `tests/api/test_student.py::test_level_two_map_and_hub_are_locked_until_level_one_is_completed` |
| US6-AS3 | A | `tests/integration/test_map_matches_lesson_access.py::test_every_lesson_the_map_offers_opens` |
| FR-001 | A | `tests/integration/test_sqlite_repository.py::TestLessonProgress::test_lesson_events_are_idempotent_and_do_not_change_elo` |
| FR-002 | A | `tests/api/test_student.py::test_level_two_map_and_hub_are_locked_until_level_one_is_completed` |
| FR-003 | A | `tests/unit/domain/test_prealgebra_lessons.py::test_trigger_question_feedback_is_evaluated_in_domain`<br>`tests/unit/domain/test_prealgebra_lessons.py::test_typed_answers_are_validated_before_being_compared` |
| FR-004 | A | `tests/api/test_student.py::test_welcome_lesson_progress_flow` |
| FR-005 | A | `tests/integration/test_map_matches_lesson_access.py::test_every_lesson_the_map_offers_opens`<br>`tests/unit/domain/test_prealgebra_lessons.py::test_map_states_come_from_unlock_after` |
| FR-006 | A | `tests/integration/test_sqlite_repository.py::TestLessonProgress::test_structured_lesson_response_roundtrip_has_no_free_text_field` |
| FR-010 | L1 | `PENDING` |
| FR-011 | L1 | `PENDING` |
| FR-020 | L2 | `PENDING` |
| FR-030 | L3 | `PENDING` |
| FR-040 | L4 | `PENDING` |
| FR-041 | L4 | `PENDING` |
| FR-042 | L4 | `PENDING` |
| FR-050 | L5 | `PENDING` |
| FR-051 | L5 | `PENDING` |
