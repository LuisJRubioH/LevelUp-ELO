# Oulad Constitution

## Core Principles

### I. The Spec Is the Contract

Behaviour is defined by `specs/NNN-*/spec.md`, not by code comments, chat history or memory.

- Every user-visible or data-affecting behaviour MUST trace to a functional requirement, and every
  functional requirement MUST trace to at least one automated test (spec § Traceability).
- Code that disagrees with its spec is a defect, whichever side is wrong. The fix is to decide
  (via `/speckit-clarify`) and then align the other side in the same PR.
- A behaviour change MUST arrive as a `[CHANGE]` requirement before the code that implements it.
- Areas without a spec yet are governed by this constitution and `AGENTS.md`; they get a spec
  the first time a feature touches them.

Rationale: the project already paid for drift — documentation described a dynamic K factor,
a `zdp.py` module and skill files that did not exist.

### II. One Source of Truth per Fact

Every piece of state and every rule has exactly one owner; everything else derives from it.

- A student's rating lives only in `student_course_topic_elo`, one row per student, course and
  topic. Course and overall ratings are derived from it and never stored; `student_topic_elo` and
  `users.current_elo` are legacy and not written. `attempts` is a log and MUST NOT be used to
  reconstruct a rating.
- Each rating writer (diagnostic baseline, valid answer, teacher-validated procedure, finished
  PvP match) MUST apply its effect exactly once, guarded by persisted state, and all writers
  MUST use the same canonical rating key for the same practice context (key defined in spec 001).
- Shared constants (rating formulas, rank tables, thresholds) MUST be defined once in `domain/`
  and consumed, not copied, by other layers. A frontend preview MUST use the backend's numbers.
- Each rule has one **normative owner** that holds its full detail; other documents MAY summarise
  it in a sentence and MUST link to the owner instead of restating its detail:

  | Topic | Normative owner |
  |---|---|
  | Principles, non-negotiables, governance | this constitution |
  | Behaviour of a specced area | `specs/NNN-*/spec.md` |
  | Operational how-to (commands, patterns, file locations) | `AGENTS.md` |
  | Rationale and history of decisions | `docs/arquitectura.md` |

  If a summary and its owner disagree, the owner wins and the summary is corrected.

### III. Layered Architecture, Enforced by Tests

```
src/domain/          pure rules and arithmetic. No I/O, no third-party libraries, no upper layers.
src/application/     use cases. Imports domain/. NEVER infrastructure/.
src/infrastructure/  repositories, storage, AI clients, ML calibrator.
src/interface/, api/ composition layer: the only places that wire infrastructure into services.
```

- `tests/unit/test_architecture_layers.py` MUST pass; a new forbidden import is a build failure.
- New business logic goes to `domain/`; new use cases to `application/services/`. No SQL in
  `domain/`, no rating arithmetic in `infrastructure/` or in routers.
- Services receive their dependencies; they MUST NOT look them up.
- The system stays a modular monolith. Splitting services requires a spec with a measured reason.

### IV. Dual-Database Parity

SQLite (local, tests) and PostgreSQL (Supabase in a deployment) expose an identical public API.

- A change to one repository MUST be mirrored in the other in the same commit, and
  `python scripts/db_sync_check.py` MUST pass before any commit that touches a repository.
- Behavioural equivalence is proven by tests parametrised over both engines, not by the text diff.
- Migrations are additive only — new columns, tables and indexes; never `DROP`, never a type
  change — and idempotent on both engines: PostgreSQL uses `ADD COLUMN IF NOT EXISTS`; SQLite
  checks `PRAGMA table_info` first (`_add_column_if_not_exists`), since it lacks that clause.
- In deployed environments the schema bootstrap runs outside the HTTP process
  (`scripts/migrate.py`, web process with `RUN_MIGRATIONS=0`). In local development and tests the
  in-process bootstrap (default `RUN_MIGRATIONS=1`) is allowed.
- PostgreSQL rows are read by name (`row["col"]`); pooled connections are returned with
  `put_connection`, never closed; one repository instance per process.

### V. Integrity of Learning Measurement

The rating is the product. It MUST be correct under concurrency, retries and hostile clients.

- Answering is one unit of work: lock, read, compute, persist in a single transaction
  (PostgreSQL `FOR UPDATE` users→items in that fixed order; SQLite `BEGIN IMMEDIATE`). The domain
  computation passed into that transaction MUST NOT perform I/O.
- Academic data (difficulty, topic, options, correct answer) is always read from the server's
  store. The client supplies only identity, choice and telemetry.
- The correct option MUST NEVER be sent to the frontend, in any response.
- Retried requests with the same `Idempotency-Key` MUST NOT move the rating twice.
- Exam mode, AI-proposed procedure scores, and attempts outside the valid response-time window
  MUST NOT move the rating.

### VI. Security and Secrets

- AI and service keys live only in backend environment variables (or, for a user's own key, in
  client-side storage). Never in the database, never in logs, never in the frontend bundle.
- Passwords use Argon2id. Tokens are never logged. Refresh tokens are HttpOnly cookies.
- Uploaded procedures are stored in a private bucket by relative path and served as bytes,
  never by public URL.
- Users flagged `is_test_user` are protected and the flag is never removed.
- Production startup MUST refuse to run with an unsafe configuration (see Validation).

### VII. Simplicity and Evidence

- Prefer deleting code to adding it. Dead code, unused parameters and speculative abstractions
  are defects to remove when their area is touched.
- Optimisation requires a measurement first (`scripts/measure_capacity.py` or equivalent) and a
  target. Current target: 20–30 concurrent students on one process.
- Known limits (single process, free-tier instance) are declared and enforced, not hidden.

### VIII. Pedagogy Is a Requirement

Oulad exists to make students learn mathematics, not to maximise engagement.

- Every spec MUST state the learner or teacher outcome it serves. A feature with no stated
  pedagogical or operational outcome is out of scope.
- Learning content (nodes, items, feedback) follows the 11-block node architecture and the
  item-bank schema; their invariants are owned by spec 003 and spec 008.
- KatIA guides; she MUST NOT reveal answers.

## Project Nature & Technology Stack

**What it is.** Oulad is the redesign of LevelUp-ELO: an adaptive mathematics practice
platform for Colombian school, university and olympiad ("semillero", contest) students and their
teachers. A per-topic Elo rating with uncertainty (RD) drives item selection toward a target
success probability; teachers review handwritten procedures; an AI tutor (KatIA) gives Socratic
hints. Production of the original product lives in `LuisJRubioH/LevelUp-ELO`. This repository is
a development copy and is **not deployed**: the owner transfers finished work to the final
deployment repository by hand (`docs/transfer.md`).

**Users.** student · teacher (requires approval) · admin.

**Stack.**

| Layer | Technology |
|---|---|
| Backend API | Python 3.11, FastAPI, uvicorn, single process (`WEB_CONCURRENCY=1`) |
| Frontend | React 19, TypeScript, Vite, Tailwind v4, Zustand, TanStack Query, react-katex, Framer Motion; pnpm |
| Legacy UI (V1) | Streamlit — **frozen** (see below) |
| Data | PostgreSQL on Supabase (deployment target), SQLite (local/tests), Supabase Storage (private bucket) |
| Realtime | FastAPI WebSockets (PvP, notifications), in-process state |
| AI | Multi-provider client selected by key prefix; degrades gracefully without a key |
| Deploy | None from this repository; manual transfer by the owner (`docs/transfer.md`). Inert templates: `render.yaml` (backend), `frontend/vercel.json` (frontend) |
| Quality | pytest, Playwright (e2e), black (100 cols), flake8, GitHub Actions |

**V1 is frozen** (decided 2026-10-05). `src/interface/streamlit/` receives no features and no
specs of its own. It is changed only to (a) fix a crash or data corruption, or (b) keep it
working after a change in a shared layer (`src/domain`, `src/application`,
`src/infrastructure`, `items/`). Frozen means no new features, not no verification:

- A shared-layer change that does not alter a signature or behaviour V1 calls needs only a
  **startup smoke check**: V1's modules import and its services construct.
- A shared-layer change that alters a signature, return shape or behaviour V1 calls, and every
  fix made inside V1, needs a **regression test** that reproduces the V1 call path and fails
  without the change.

## Domain Rules

These are the invariants every spec inherits. Exact formulas and parameters are owned by the
spec named in brackets; changing them requires a `[CHANGE]` requirement in that spec.

- **Rating model** [spec 001]: expected score `P = 1/(1+10^((D−R)/400))`; per-topic rating with
  RD that shrinks with evidence; item difficulty moves symmetrically with each valid answer.
- **Item selection** [spec 001]: target success probability band with progressive widening,
  preferring informative items (`P(1−P)`), unseen before failed-with-cooldown before historical.
- **Teacher authority** [spec 006]: a teacher's procedure score is the only procedure signal
  that moves the rating; the AI score is advisory.
- **Learning path** [spec 003]: nodes unlock in a declared order; each node declares its focal
  misconception; misconception tags are `<symptom>_<operation>` and unique per node.
- **Item bank** [spec 008]: items live in `items/bank/**.json`; `correct_option` matches one
  `options` entry exactly; LaTeX backslashes are doubled in JSON.

## Code Style & Structure

- **Language.** All development text — identifiers, comments, docstrings, specs, docs, commit
  messages — is written in English. Learner-facing content stays in Spanish (es-CO) through
  i18n or content modules. Only new or modified development text must be English; untouched
  Spanish text in the same file is left as is. Bulk translation happens only as its own task.
- **Python.** black at 100 columns; flake8 `E9,F63,F7,F82` clean. Imports inside backfill
  functions stay local.
- **TypeScript.** Strict build passes (`pnpm run build`). Direct `fetch()` uses the
  `VITE_API_URL` prefix. Colours come from CSS tokens, never hard-coded.
- **Frontend design.** Student views mobile-first (375 px); teacher views desktop-first
  (1280 px); math always rendered with KaTeX; motion only where it carries meaning.
- **Tests.** Unit tests next to the layer they test (`tests/unit/<layer>/`); cross-engine
  behaviour in `tests/integration/`; HTTP contracts in `tests/api/`.
- **Commits.** One logical change per commit; never commit `.claude/`, `CLAUDE.md`, secrets or
  generated databases.

## Validation & Error Management

- **Trust boundaries validate.** Every API input is validated (pydantic) and checked against
  canonical data; invalid input returns 4xx with a reason, never a silent default.
- **Fail loudly at startup.** `validate_runtime()` MUST reject production start on missing
  `DATABASE_URL`, weak `JWT_SECRET_KEY`, localhost CORS, in-memory rate limiting, or
  `WEB_CONCURRENCY > 1`. A failed migration stops the service.
- **Readiness, not liveness.** `/api/health` checks the database and returns 503 when it is down.
- **No silent swallowing.** `except Exception: pass` is forbidden. A failure in a non-critical
  side effect (badges, notifications) MAY be tolerated only if it is logged and the primary
  operation's result is unaffected.
- **Transactions roll back** on any exception and re-raise; partial writes are never committed.
- **Graceful degradation** applies to optional integrations only (AI, calibrator, storage
  upload falls back to DB bytes) and MUST be visible in logs.

## AI Agent Behaviour (SDD Rules)

Rules for any AI agent (Claude Code, Codex) working in this repository. Each rule closes one of
the five prompt gaps.

1. **Bounded reach** (gap: unlimited reach). An agent's scope is the **authorized objective** (the
   task, or the user's request) plus its **necessary dependencies**: the code that must change for
   the objective to work, the changes this constitution makes mandatory (the mirrored repository,
   tests, docs the change makes stale), and nothing else. The user need not list files. Problems
   found outside that scope are reported or filed as a follow-up, not fixed in passing. No push
   to `main`; no deploy; no destructive git operation.
2. **Measurable acceptance** (gap: subjectiveness). Every acceptance criterion is a test or a
   number. Words like "clean", "better", "robust" are not criteria. Done means the listed tests
   and checks pass — and the agent reports their actual output.
3. **What, not how, in specs** (gap: micromanagement). Specs state behaviour and constraints;
   plans choose the implementation; the agent may pick any implementation within the plan and
   this constitution, and records non-obvious choices in `research.md`.
4. **Outcome traceability** (gap: business disconnection). Every task traces to a user story,
   every user story to a learner or teacher outcome. A task with no trace is removed or questioned.
5. **Humans decide, agents evidence** (gap: delegating critical thinking). A decision already
   recorded — in this constitution, a spec, `AGENTS.md`, or an accepted Known Deviation — is
   applied without asking. A **new** pedagogical, product or data-semantics decision, or one that
   conflicts with a recorded one, belongs to the owner: the agent marks it
   `[NEEDS CLARIFICATION]`, recommends an option with its consequences, and continues with any
   work that does not depend on it. Claims about current behaviour cite code (`file:line`) or a
   test.
6. **Brownfield safety.** Before refactoring an area, characterization tests pin its current
   behaviour and pass against the unchanged code. A refactor that changes a pinned behaviour
   MUST be backed by a `[CHANGE]` requirement and flip the test explicitly.
7. **Workflow gates.** One branch per spec, one commit per approved Spec Kit step, a docs PR after
   `/speckit-tasks` + `/speckit-analyze`, and a code PR after `/speckit-converge` reports no gaps.
   The owner merges.
8. **Verification before "done".** For any change: the relevant tests, `db_sync_check.py` if a
   repository changed, `validate_bank.py` if `items/` changed, and `pnpm run build` if `frontend/`
   changed.

## Known Deviations

Places where the code or another document currently contradicts this constitution. Each has an
owner spec and a deadline (roadmap milestone, `docs/sdd/roadmap.md`). Until fixed, the deviation
is tolerated but MUST NOT spread to new code.

| ID | Deviation | Contradicts | Fixed by | Deadline |
|---|---|---|---|---|

None open. D-1 (rating writers used different keys), D-2 (frontend preview with its own K) and
D-3 (swallowed badge errors) were resolved by spec 001, merged 2026-10-08, and removed in 1.0.1.

Not a deviation: existing Spanish development text is permitted by the language policy and is
tracked as **documentation debt** (`AGENTS.md` is translated in step 0.3). Only new or modified
development text written in Spanish is noncompliance.

## Governance

- **Precedence.** This constitution > spec of the area > `AGENTS.md` (operational rules) >
  `docs/arquitectura.md` (rationale) > `CLAUDE.md` (local, unversioned pointer only). A lower
  document that contradicts a higher one is wrong: it is corrected, or listed in Known
  Deviations until it is.
- **Non-negotiable principles.** I (the spec is the contract), II (single source of truth,
  exactly-once effects), IV (dual-database parity), V (integrity of learning measurement) and VI
  (security and secrets) cannot be waived by a plan. Departing from them requires an amendment.
  No exception accepted under any other section (Code Style, Validation, Stack, …) may weaken an
  obligation that one of these principles protects, wherever that obligation is written.
  Working in an area that has no spec yet is not an exception to I: Principle I itself allows it.
- **Other deviations** (III, VII, VIII, Code Style, Validation) MAY be accepted per plan, in its
  Complexity Tracking table, only if (a) the owner approves it in the PR, (b) it names a deadline
  milestone, and (c) it is added to Known Deviations. An unapproved or expired deviation is a
  defect.
- **Amendments** go through `/speckit-constitution` on their own branch and PR, with a Sync Impact
  Report naming the affected specs.
- **Versioning** is semantic: MAJOR removes or redefines a principle; MINOR adds a principle or
  section or materially expands one; PATCH clarifies wording.
- **Compliance — enforced today by CI** (`.github/workflows/ci.yml`): item-bank validation, black +
  flake8, unit tests (including architecture layers and repository contracts) with a **coverage
  floor of 70 % over `src/domain` + `src/application`** (`--cov-fail-under=70`, unit job), integration
  tests, `db_sync_check.py`, ELO tests against a real PostgreSQL, API tests, frontend build. The
  floor may rise, never fall, without an amendment.
- **Coverage and traceability are complementary.** Coverage shows code was executed;
  traceability shows each requirement has a test. Neither proves the assertions are adequate: a
  mapped test may assert only part of its requirement. Every FR and acceptance scenario MUST map
  to relevant executable tests, and review MUST check that their assertions prove the stated
  behaviour.
- **Compliance — not yet automated** (enforced by review until its task lands, see
  `docs/sdd/roadmap.md` § Automation tasks): Playwright e2e (exists in `frontend/e2e/`, not run in
  CI; its tests mock the API, so they verify frontend flows, not backend integration); FR → test
  traceability; the Spec Kit gates after clarify, analyze and converge
  (`.specify/workflows/speckit/workflow.yml` only gates after specify and plan); V1 startup smoke
  check.
- **Review.** The constitution and its Known Deviations are reviewed at the end of each roadmap
  milestone.

**Version**: 1.0.1 | **Ratified**: 2026-10-05 | **Last Amended**: 2026-10-08
