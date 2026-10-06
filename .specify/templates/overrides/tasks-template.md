---

description: "Oulad task list template (project override of the Spec Kit core tasks-template)"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`

**Prerequisites**: plan.md (required), spec.md (required for user stories and § Traceability),
research.md, data-model.md, contracts/

**Tests are MANDATORY** (constitution Principle I). Every functional requirement and every
acceptance scenario in spec.md § Traceability is an explicit test request, so test tasks are
always generated — this overrides the core template's "tests are optional" default. For each
FR / scenario:

- **Reuse** an existing test when its assertions already prove the requirement; the task is to
  record it in § Traceability (and strengthen the assertion if it proves only part).
- **Create** a test when none exists or the existing one is inadequate.

**Two kinds of test, two different sequences** (brownfield, constitution agent rule 6):

| Requirement tag | Test kind | Must be, before implementation | After implementation |
|---|---|---|---|
| `[AS-IS]` | characterization | **PASSING against the unchanged code** — it pins today's behaviour | still passing |
| `[CHANGE]` | behaviour change | **FAILING** — the intended behaviour does not exist yet | passing |

A `[CHANGE]` that alters something an `[AS-IS]` test pinned flips that test explicitly in the
same task, citing the FR. Never edit a pinned assertion silently.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested
independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **Requirement IDs**: every test task names the FR / scenario IDs it covers (e.g. `FR-003, US1-AS2`)
- Include exact file paths in descriptions

## Path Conventions (Oulad)

- Domain / application / infrastructure: `src/domain/`, `src/application/`, `src/infrastructure/`
- API: `api/`; frontend: `frontend/src/`; V1 (frozen): `src/interface/streamlit/`
- Unit tests: `tests/unit/<layer>/`; cross-engine behaviour: `tests/integration/` (parametrised
  over SQLite and PostgreSQL); HTTP contracts: `tests/api/`; browser flows: `frontend/e2e/`

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit-tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Requirements and their [AS-IS] / [CHANGE] tags from spec.md
  - spec.md § Traceability (every row gets a test task, reused or new)
  - Feature requirements from plan.md, entities from data-model.md, endpoints from contracts/

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup

**Purpose**: Anything the work needs that does not exist yet (often nothing in a brownfield area)

- [ ] T001 [Setup task, e.g. "Create tests/integration/test_[area].py with engine fixture"]

---

## Phase 2: Pin Current Behaviour (Blocking)

**Purpose**: Characterization tests for every `[AS-IS]` requirement this feature's refactor will
touch, so the refactor cannot change behaviour unnoticed. Omit this phase only if the spec has no
`[AS-IS]` requirement touched by the work; likewise generate `[CHANGE]` test tasks only for
`[CHANGE]` requirements.

**⚠️ CRITICAL**: No implementation task may start until every test in this phase **passes against
the unchanged code**. A characterization test that fails on today's code is wrong (or has found a
bug): stop and raise it in `/speckit-clarify`, do not "fix" the code here.

- [ ] T002 [P] Reuse `tests/...::test_...` for FR-001 — verify its assertions prove FR-001; record in § Traceability
- [ ] T003 [P] Characterization test for FR-002, US1-AS1 in tests/integration/test_[name].py — passes on unchanged code
- [ ] T004 Run the phase's tests against the unchanged code and record the green run in the task

**Checkpoint**: Current behaviour pinned — refactor and change work can begin

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1

- [ ] T010 [P] [US1] `[CHANGE]` test for FR-004, US1-AS2 in tests/unit/domain/test_[name].py — **fails** before T012
- [ ] T011 [P] [US1] `[AS-IS]` FR-005: reuse/characterize in tests/api/test_[name].py — passes before and after

### Implementation for User Story 1

- [ ] T012 [US1] Implement FR-004 in src/domain/[module].py (makes T010 pass; T011 stays green)
- [ ] T013 [US1] Mirror repository change in sqlite_repository.py and postgres_repository.py (R1)
- [ ] T014 [US1] Flip pinned test `tests/...::test_...` for FR-004 (behaviour intentionally changed)

**Checkpoint**: User Story 1 functional; its tests green; § Traceability rows for US1 filled

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2

- [ ] T020 [P] [US2] `[CHANGE]` / `[AS-IS]` test for FR-…, US2-AS… in tests/...

### Implementation for User Story 2

- [ ] T021 [US2] Implement … in src/...

**Checkpoint**: User Stories 1 and 2 both work independently

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Traceability & Verification

**Purpose**: Close every gap before the code PR (constitution § Governance)

- [ ] TXXX Update spec.md § Traceability: no `PENDING` rows; every reference resolves to a collected test
- [ ] TXXX Review assertion adequacy: each mapped test proves its FR / scenario, not just part of it
- [ ] TXXX Run verification (AGENTS.md § Verify before saying "done"): full test suite;
  `db_sync_check.py` if a repository changed; `validate_bank.py` if `items/` changed;
  `pnpm run build` if `frontend/` changed
- [ ] TXXX V1 check if a shared layer changed (constitution § Stack: smoke check or regression test)
- [ ] TXXX Remove resolved Known Deviations from the constitution (via `/speckit-constitution`)

---

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Pin Current Behaviour (Phase 2)** → user stories → **Traceability &
  Verification (Phase N)**.
- Phase 2 BLOCKS all user stories: no refactor before the pins are green on unchanged code.
- Within each story: `[CHANGE]` tests written and FAILING → implementation → `[CHANGE]` tests
  passing, `[AS-IS]` tests still passing.
- Repository changes always in both engines in the same task (R1).

### Parallel Opportunities

- Phase 2 tasks marked [P] can run in parallel
- Test tasks within a story marked [P] can run in parallel
- Different user stories can proceed in parallel once Phase 2 is green

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label + requirement IDs map each task to spec.md for traceability
- `[AS-IS]` tests: green before and after. `[CHANGE]` tests: red before, green after.
- Commits follow the approved commit policy in AGENTS.md § Required sequence (one commit per
  approved Spec Kit step) and constitution § AI Agent Behaviour, rule 7
- Avoid: vague tasks, same-file conflicts, test tasks without requirement IDs
