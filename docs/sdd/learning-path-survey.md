# Learning path — as-is survey (spec 003 input)

Read-only survey of `redesign @ 1d6fcf6`, 2026-10-09. Input for `specs/003-learning-path/spec.md`
(roadmap M3: course map, 11-block nodes, unlock chain, misconception tags, diagnostic gating;
AGENTS.md V2-R11 … V2-R18 are "owned by spec 003 once it exists").

Each finding cites code at that commit (`S` = `api/routers/student.py`,
`L` = `src/domain/learning/prealgebra.py`, `N/` = `src/domain/learning/nodes/`,
`FE/` = `frontend/src/pages/Student/`). **Verified** = read in the code and, where marked, checked
by importing the catalogue; **Inferred** = reasoned from the code, not run. Nothing here was run
against production.

## 1. Where things live

| Concern | File |
|---|---|
| Lesson catalogue, sequences, unlock data, map rows, interaction grading | `L` (2,360 lines with the hubs) |
| Node content (52 eleven-block modules) | `N/*.py`, listed in `N/__init__.py:64-121` (`NODE_MODULES`) |
| Hubs | E00, M00, C00 in `L`; A00 and S00 in `N/a00_hub.py`, `N/s00_hub_bagdad.py` |
| API | `S:1110-1210` (progress, hub auto-complete, special cases), `S:1215` lesson, `S:1230` events, `S:1286` interactions, `S:1340` pre-algebra summary, `S:1394` map |
| Progress tables | `lesson_progress`, `lesson_interactions` (both repositories) |
| Renderers | `FE/Lesson.tsx` (dispatch), `FE/lessons/blocks/ElevenBlockLesson.tsx` + `LessonBlocks.tsx` (generic), `FE/lessons/LevelTwo/Three/FourLesson.tsx` (hubs), `FE/CourseMap.tsx` |
| Math rendering | `frontend/src/components/Math/MathContent.tsx` |
| Tests | `tests/unit/domain/test_prealgebra_lessons.py` (47 functions, 211 cases), `tests/api/test_student.py:633-1112` (10), `tests/integration/test_sqlite_repository.py:56-115` |

## 2. Actual behaviour

**One course.** Only `algebra_basica` has a path (`L:13`); the lesson endpoints answer 404 for
any other course (`S:1221`). The catalogue holds **60 nodes**: pre-algebra N1 13, N2 7, N3 6,
N4 7; algebra N1 17, N2 5, N3 5. 52 are `eleven_block_node`; the other 8 are hubs and the N1
specials (B01 welcome, B02 trigger question, B13 closing diagnostic).

**Unlock data.** Node modules hold only content (`NODE_ID`, `CONCEPT_SLUG`, `CONTENT`). Position
comes from the "fichas" in `L`: hand-written for N1, sequence tuples
`(id, node_type, topic, i18n_prefix, unlock_after)` for the other levels (`L:908, 1142, 1502,
1613, 1740, 1788`). The result is a **tree**, not a chain: one root (B01), no dangling
`unlock_after`, B08 has two children and E00 six (verified by importing the catalogue).

**Progress.** `lesson_progress` stores `viewed`/`completed` per (student, course, node) and only
moves forward; `blocked`/`current` are derived. `lesson_interactions` keeps one answer per
interaction (last write wins). Answers are graded on the server (`evaluate_interaction`,
`L:2206-2341`) and the result drives feedback and the summary's misconception tags. **Nothing in
the path moves a rating** (`affects_elo: False` everywhere; tested at `test_student.py:735-921`).

**Gating on the server.** A node whose `unlock_after` is not completed answers 403 on read and
write (`S:1160-1164`). `node_completed` answers 409 until every required interaction **has an
answer** (`S:1247-1278`); for eleven-block nodes the required set is the practice items plus the
closing item (`L:1953-1959`). Hard-coded cases: the N3 hub and machines need all six N2 nodes
(`S:1156-1158`); B09 (complex numbers) is hidden and 403 for the "básico" presentation
(`S:1174-1178`); the N2 and N3 hubs auto-complete when their cards are opened (`S:1113-1140`).

**Client.** `Lesson.tsx` dispatches by `content.kind` first (eleven-block → generic renderer),
then by node type or by hard-coded id lists (N2/N3/N4/ALG hubs, B02, B13; `FE/Lesson.tsx:21-50,
127-203`). The generic renderer shows the server's `is_expected`/`feedback_key`
(`LessonBlocks.tsx:80-85`). The map comes from `GET /map/{course}` with states computed on the
server; the client only blocks clicks on `blocked` nodes.

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| L1 | **Access** | **No enrolment check on any learning-path endpoint.** Lesson, events, interactions, summary and map accept any authenticated user, any role, in any course the student is not enrolled in. Spec 001 FR-037 left the map and lessons out of its scope on purpose. | `S:101-108` called only at `S:118, 173, 990, 1022` | Verified |
| L2 | **Answer keys on the client** | `LessonDetailResponse.content` is the node's whole `CONTENT`, including the keys of the items that gate completion: `answer`, `expected`, `accepted`, `valid_options`, `trap_options`, `misconception_by_option`, `closing_item.answer`, bridge blanks (e.g. `N/b06_racionales.py:47, 58, 79, 285`). The endpoint's docstring says "sin exponer respuestas". The renderer does not display them, but a student can read them in the browser. | `api/schemas/student.py:313-331`; `S:1219` | Verified |
| L3 | **Completion** | `node_completed` checks that answers **exist**, not that they are right; B01, B13, the N4 hub, A00 and S00 have no check at all, so a client can complete them directly. | `S:1261-1278` | Presence check verified; list of unchecked nodes from code reading |
| L4 | **Unsent learning data** | The genuine attempt, self-explanations, trap confidence and explanation, hints used, the abstraction answer and the B02 challenge are **never sent**; mastery and the post-diagnostic outcome are computed in the browser and lost. The repository test pins that responses carry no free-text field, which may be deliberate (privacy). | `LessonBlocks.tsx:340-341, 422, 596-597, 771, 798`; `ElevenBlockLesson.tsx:168-187`; `test_sqlite_repository.py:56-115` | Code verified |
| L5 | **Unlock rules in two places** | The map follows `unlock_after` only, where the N3 hub follows E06; the API also requires all six N2 nodes. A student who finished E06 first sees the N3 hub available on the map and gets 403 on opening it. Nothing tests that the tree has one root, no dangling reference and no cycle. | `L:1148`, `S:1156-1158`; `test_prealgebra_lessons.py:606-611` | Mismatch inferred; tree checked by import |
| L6 | **Hard-coded node ids** | Server: hub auto-completion, the B09 rule, a dead `STAIRCASE` entry (B03 is now eleven-block), the 409 text "Responde las dos preguntas" for every node. Client: id lists for N2/N3/N4/ALG hubs, B02, B13, the B01 fallback screen. V2-R16 says `Lesson.tsx` no longer whitelists ids. | `S:1113-1178, 1250, 1264`; `FE/Lesson.tsx:21-50, 205-305` | Verified |
| L7 | **Dead renderers** | Every non-hub node is eleven-block, so `LevelTwoOperation`, `LevelThreeMachine` and `LevelFourConcept` are unreachable; the "Resultado esperado: {answer}" fallback lives only there. | `FE/Lesson.tsx:127-169`; `FE/lessons/LevelTwoLesson.tsx:226`, `LevelThreeLesson.tsx:284` | Inferred (grep of `kind`) |
| L8 | **Overwritten history** | Re-answering an interaction, even after completion, replaces the earlier answer and its misconception tag; there is no event history, so the teacher summary sees only the last answer. | repositories `save_lesson_interaction` (upsert) | Code verified |
| L9 | **Map vs practice** | The map shows practice-topic nodes `blocked` until B08 is completed, but `/next-question` ignores lesson progress: the block is display only. | `S:1471, 1488-1490`; `S:114-127` | Code verified |
| L10 | **Summary endpoint** | `/prealgebra-summary/{course}` has no response model, does not validate the course and has no test. | `S:1340-1391` | Verified |
| L11 | **Design-rule drift** | D5 says react-katex; math goes through `katex.renderToString` + `dangerouslySetInnerHTML` (react-katex is installed but unused). Some hub math is plain text (`a^n`, `×→`, practice prompts in `PracticeItem.tsx`). `CourseMap.css` defines its own accent `#8b5cf6` (token: `#6C63FF`); several raw CSS transitions where D2 asks for Framer Motion. | `components/Math/MathContent.tsx:2, 50, 88`; `FE/lessons/LevelTwoLesson.tsx:150`; `FE/CourseMap.css:8-11, 52` | Verified (MathContent); others from code reading |
| L12 | **Test gaps** | No e2e test opens a lesson; the map's only e2e test relies on the development padding of the map (`CourseMap.tsx:86-102`). Untested: enrolment (L1), the summary, the PostgreSQL lesson methods, the B09 403, writes to a locked node, overwrite on re-answer, and several V2-R11…R17 invariants (§ 4). | `frontend/e2e/`; `spec001-ratings.spec.ts:83-102` | Verified |
| L13 | **Doc drift** | V2-R13 cites `_N3_MACHINE_CONTENT` and `LevelThreeLesson.tsx` for the machines: the symbol no longer exists and M01–M05 are eleven-block (LevelThree renders only the M00 hub). V2-R18 calls the known-debt list "nine inherited pre-algebra tags", but `confunde_la_operacion_dictada` is algebra. ALG-N1 F01 uses i18n prefix `algebra.n1.b03` (copy-paste); `ALG_*_NODE_ID` constants are defined twice; comments at `L:1587, 1839, 1938-1940` are stale (the last says the blocks "siembran ELO"). | `AGENTS.md` V2-R13, V2-R18; `L:1596-1603, 1675` | Verified |

## 4. Existing evidence

- **Content invariants** (`test_prealgebra_lessons.py`, 211 cases): the eleven blocks, one focal
  self-explanation, the trap card, hints n1–n3, only practice and closing gate, answers reachable
  (V2-R11); building / station / destination / room names match their hubs and focal
  misconceptions are distinct (V2-R12–R15); six-set ladders and decimal commas (V2-R12); mixed
  practice and list-typed options (V2-R14); no shared room names (V2-R16); misconception routing,
  no orphan tag, and "a content error emitted by 3+ nodes needs a teaching node" with 9 known-debt
  tags (V2-R18).
- **Not tested** (stated only in AGENTS.md): the mini-diagnostic does not grade; the renderer
  knows no node id; E06's 𝕀 `partial` row; KatIA as a Greek cat and interior scenes; no repeated
  concrete case; the context bank of N4; that hub cards point to each house's first room; the
  closure axes; the chain S00 ← R04, G01 ← P04. Prose rules (vocabulary lanes, historical claims)
  can only be reviewed.
- **API** (`test_student.py:633-1112`): welcome completion, 409 until answered, `is_expected`
  stored without touching ratings, N2/N3 hub gating, ALG map order. **Repository**
  (`test_sqlite_repository.py:56-115`): idempotent events, no rating change, no free-text field.

## 5. Decisions for the owner (input for `/speckit-clarify`)

None blocks the transfer (PR #3); lessons never move a rating.

1. **Who may open lessons and the map (L1)?** Only students enrolled in the course (as FR-037 does
   for practice), any student, and may teachers preview?
2. **Answer keys (L2).** Accept them on the client (lessons are formative and the server already
   grades), or strip the grading keys from `content` so only the server holds them.
3. **What completes a node (L3).** Answers present (today), answers right, or a mastery rule; and
   what B01, B13 and the hubs must require.
4. **What learning data is kept (L4, L8).** Today self-explanations and other free text are not
   stored and each answer overwrites the previous one. Keep that (privacy, minors), or store some
   of it — e.g. the post-diagnostic outcome or an answer history for the teacher.
5. **Unlock rules (L5, L6).** Make `unlock_after` (data) the only source, moving the "all six N2
   nodes" rule and the B09 rule into data, or keep code special cases.
6. **D5 (L11).** Amend the rule to name `MathContent` (KaTeX) as the way to render math, or move
   to react-katex.
7. **Scope of the content rules.** Should spec 003 turn V2-R11 … V2-R18 into requirements with
   tests (and keep prose rules as review items), or own only the engine (map, unlock, progress,
   completion) and leave content authoring to the AGENTS rules?

## 6. Proposed scope for spec 003 (draft)

- **In:** the lesson catalogue and unlock tree; access to lessons and the map; progress states
  and what completes a node; what the server sends and stores (grading, answer keys, history);
  hub behaviour; the map's states; the generic renderer's contract with the API; the content
  invariants the owner chooses to keep as requirements (decision 7).
- **Out:** ratings (spec 001 — lessons never move them); practice item selection (spec 001);
  persistence mechanics (spec 002); the item bank (spec 008); visual design beyond D1–D5.
