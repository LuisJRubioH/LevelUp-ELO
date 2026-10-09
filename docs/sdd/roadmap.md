# SDD adoption roadmap — Oulad (brownfield)

Goal: replace "docs that drift" with specs that are checked by tests, by reverse-engineering
the existing code into a constitution + one spec per bounded area, then refactoring each area
to its spec.

Cadence assumed: **5 sessions/week, 1 session ≈ half a working day** (same as the redesign
roadmap). Colombian holidays skipped (Oct 12, Nov 2, Nov 16, Dec 8). Start **Mon 2026-10-05**.

---

## 1. How we work (every spec repeats this loop)

| Step | Command | Output | Who decides | Gate |
|---|---|---|---|---|
| 0. Survey | — (read-only) | `docs/sdd/<area>-survey.md` | Claude drafts | you read it |
| 1. Specify | `/speckit-specify` | `specs/NNN-<area>/spec.md` — **as-is** behaviour, EARS requirements, out-of-scope | Claude drafts from code | you approve |
| 2. Clarify | `/speckit-clarify` | answers encoded in spec.md | **you** decide each drift: keep, fix, or drop | you approve |
| 3. Checklist | `/speckit-checklist` | requirement-quality checklist | Claude | all items pass |
| 4. Plan | `/speckit-plan` | plan.md, research.md, data-model.md, contracts/, quickstart.md, constitution check | Claude | you approve |
| 5. Tasks | `/speckit-tasks` + `/speckit-analyze` | tasks.md (`[P]`, `[USn]`), consistency report | Claude | analyze has no CRITICAL |
| 6. Pin | (first tasks) | **characterization tests**: one test per acceptance scenario, written against today's code, green before any refactor | Claude | tests green on old code |
| 7. Implement | `/speckit-implement` | refactor to the contract; pinned tests stay green, changed behaviour gets its test flipped explicitly | Claude | full suite + `db_sync_check` green |
| 8. Converge | `/speckit-converge` | gaps appended to tasks.md → loop to 7 until empty | Claude | no gaps |

**Branches & PRs:** one branch per spec (`NNN-<area>`, created by `/speckit-specify`), **one commit
per step after your approval**, and **two PRs to `main` per spec**:
- **Docs PR** after step 5 (spec + plan + tasks, no code) — cheap to review, no deploy risk.
- **Code PR** after step 8 (tests + refactor) — this one deploys; you merge it.

Strict "branch per command" is possible (≈7 PRs per spec); say so if your course requires it.

**Changing a requirement later:** `/speckit-clarify` on that spec → re-run plan → tasks →
analyze → implement. If it contradicts a principle, `/speckit-constitution` first (version bump).

---

## 2. Phase 0 — foundation (once)

| # | Work | Sessions |
|---|---|---|
| 0.1 | Template edits: EARS requirement patterns + "Out of scope" section in `spec-template.md` | 0.5 |
| 0.2 | Constitution (`/speckit-constitution`), English, from CLAUDE.md corrected by the code | 1.5 |
| 0.3 | Slim CLAUDE.md to quickstart + commands + pointer to constitution; translate dev text to English | 1 |

## 3. Specs (bounded areas, in risk order)

| Spec | Area | Covers | Sessions |
|---|---|---|---|
| **001** | ELO engine | rating/RD update, item update, selector, answer transaction, all rating writers (diagnostic, procedure, PvP delta), global average, ranks | 8 |
| **002** | Persistence | repository contract, SQLite/Postgres parity, migrations (additive), pool, locks, storage paths | 6 |
| **003** | Learning path | course map, 11-block nodes, unlock chain, misconception tags, diagnostic gating | 6 |
| 004 | Identity & access | JWT/refresh, roles, teacher approval, groups, admin, test users; changing a student's grade (promotion); takes over spec 001 FR-028m (registration and enrolment rules) | 4 |
| 005 | AI integration | provider detection, key precedence, KatIA socratic guardrails, procedure review | 4 |
| 006 | Teacher console & exams | dashboard metrics, exports, exam mode, procedure grading flow | 5 |
| 007 | PvP leagues | lobby, match lifecycle, single-process constraint (ELO effect lives in 001) | 4 |
| 008 | Item bank | JSON schema, validation, course→block map, calibration | 4 |

Not specs (covered by the constitution): frontend design system, code style, CI.

**V1 (Streamlit): frozen** (2026-10-05) — no specs of its own; changed only for crashes, data
corruption, or to keep working after shared-layer changes. See constitution § Stack.

### Automation tasks

Two separate tasks that move checks from "review-only" to CI (constitution § Governance).
Each gets its own branch and PR.

| ID | Task | Acceptance | When | Sessions |
|---|---|---|---|---|
| A-1 | **Playwright in CI** — run the existing Chromium suite (`frontend/e2e/`) on PRs | deterministic fixtures, no flaky retries hiding failures; traces + screenshots kept as artifacts on failure; README note that these tests mock the API and verify frontend flows, not backend integration | during M1 — **Done 2026-10-09** (PR #4, merged into `redesign`) | 1 |
| A-2 | **Traceability check in CI** — script over `specs/*/spec.md` | unique FR / scenario IDs; every FR and scenario has a row; each reference resolves to a collected test (`pytest --collect-only`, Playwright `--list`); `PENDING` allowed on spec branches before the code PR, rejected on the code PR; referenced tests pass and are not skipped. Assertion adequacy stays a review item | with spec 001 code PR (needs its first traceability table) — **Done 2026-10-09** (PR #5, merged into `redesign`; branch-independent, by Code Scope) | 1 |

### Follow-ups found while implementing specs

Defects outside the running spec's scope. Each is fixed in its own branch and PR, test first.

| ID | Finding | Reproduction | Acceptance | When |
|---|---|---|---|---|
| F-1 | **Semillero catalogue is empty for students with a grade** (found in spec 001, 2026-10-07). `get_available_courses_by_level` (both repositories) looks for block `Semillero {grade}°`, which no course has: all 36 semillero courses have block `Semillero` and carry the grade as id suffix `_semillero_N`. The SQLite CHECK on `courses.block` allows only `Semillero`; the PostgreSQL CHECK list is garbled (`'Semillero'` repeated, then `'Semillero 11°'`) | fresh SQLite API (`DB_PATH` temp, bootstrap): register a student `education_level=semillero, grade="6"`, `GET /api/student/courses` → 200 with **0** courses; the same student with `grade=None` → 36 courses (all grades 6–11) | **Decided 2026-10-08** (spec 001 FR-028k–o, User Story 7; plan `docs/sdd/f1-semillero-survey.md`; tasks T084–T100): semillero requires a grade 6–11 and sees exactly the six courses of that grade; the API rejects registration without a grade; `/enroll` checks the catalogue on every level; invitations stay cross-level but need a grade, never change level or grade, never count toward the overall rating, and are listed among the student's enrolments; grade-less accounts are never given a grade automatically (documented procedure first) and see «Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu docente o al administrador.» with their enrolments still open; the block CHECK issues no DDL when it already accepts the four blocks, extra values kept; an old database lacking one stops the migration with a clear error — the automatic widenings are removed and any manual repair is reviewed separately (R8). Tests first, two-engine where storage is involved; `db_sync_check` in sync; V1 changed only through the shared fix | **Decided 2026-10-09: included before the production switch** (PR #3 merge); docs PR (spec + tasks) first, then the code PR; deploy after the owner's read-only checks (T084, `docs/transfer.md` § 6); merge order with F-4: survey § 7 |
| F-3 | **`attempts.difficulty` is `INTEGER` on PostgreSQL, `REAL` on SQLite** (found in spec 001, 2026-10-07): attempt history on PostgreSQL rounds the item difficulty to a whole number (598.3854 → 598); item difficulties are fractional after any answer | on PostgreSQL, answer an item whose difficulty is fractional; `SELECT difficulty FROM attempts` returns the rounded integer; SQLite keeps the value | owner decision: accept and document, or an additive fix (new column, AGENTS R8) — never a retype; parity test over both engines; `test_postgres_permissions_diagnostic_and_canonical_answer` updated accordingly | spec 002 (persistence parity) |
| F-2 | **CI lint already fails on `main`**: black 24.3.0 would reformat 79 files untouched by spec 001 | `black --check --line-length=100 src/ tests/ scripts/` on `main` | one formatting-only commit; `black --check` and the CI flake8 selection pass; full suite unchanged | **Done 2026-10-08** on branch `ci/test-job-deps` (75 files remained after spec 001), together with the CI dependency fix that unblocks the unit, integration, parity, PostgreSQL and API jobs |
| F-4 | **Practice is not limited to the student's courses** (found in the F-1 survey, 2026-10-08). `POST /api/student/next-question` serves items of any course, enrolled or not; `/answer` then stores a rating for that course, and `/diagnostic/{course}` also works on it | fresh SQLite API: a colegio student with no enrolment asks `next-question` for `probabilidad` (universidad) → 200 with an item; answering it stores a `probabilidad` rating (1018); `GET /api/student/diagnostic/probabilidad` → 200 | **Decided 2026-10-08** (spec 001 FR-037, FR-037a, User Story 8; tasks T101–T108): `next-question`, `/answer` and the diagnostic (status and submit) check enrolment — from the student's level or through an invitation — and refuse anything else with 403 before serving an item or touching a rating, attempt, item difficulty, retry record or diagnostic; tests for allowed and denied access, the denied side with no side effect; V2 only | **pending before the production switch** (PR #3 merge); docs PR, then the code PR, both before F-1's docs PR: once the traceability check (A-2) is merged, every PR that changes spec 001's code fails while spec 001 has `PENDING` rows on its base |
| F-5 | **PvP rejects every enrolled student** (found while specifying F-4, 2026-10-08). `api/websocket/pvp.py` builds the enrolment set from `row["course_id"]`, but `get_user_enrollments` (both repositories) returns the course under `id`; the `KeyError` is caught as an authentication failure. Only the refusal path is tested (`tests/api/test_websocket_authorization.py::test_pvp_rejects_course_without_enrollment`). PvP is new in the redesign (`main` has none), so the switch would ship it unusable | SQLite API: `estudiante1` enrolled in a course connects to `/api/ws/pvp/{course}` and sends a valid token → closed with 4001, log `PvP auth failed: 'course_id'` | **Decided 2026-10-08: included before the switch.** Tests written first (both engines, `tests/integration/test_pvp_enrolment.py`): an enrolled student waits in the lobby and leaves cleanly; two students — one enrolled through a group — play a whole match to `game_end` on a real uvicorn server; a student enrolled only elsewhere still gets 4001. The check reads `row["id"]`; the lobby also reads the exception of its finished wait task, which otherwise logged "Task exception was never retrieved" whenever a waiting player left | **pending before the production switch** (PR #3 merge); branch `fix/f5-pvp-enrolment` |
| F-6 | **Semillero test students are seeded without enrolments** (found by the persistence survey, 2026-10-09, P12). The test-student seed (both engines) looks for the blocks `Semillero {grade}°` and `Semillero %`, which the `courses.block` CHECK does not allow: `estudiante_semillero_1`/`_2` get no enrolment and the semillero test group no course. Local and test data only — the seed is skipped with `ENVIRONMENT=production` | fresh SQLite or PostgreSQL bootstrap: `estudiante_semillero_1` has 0 rows in `enrollments`; `Grupo Prueba - Semillero` has `course_id` NULL | test first, both engines (`tests/integration/test_seed_test_students.py`): every seeded student is enrolled in exactly the catalogue `in_catalogue(level, grade)` (spec 001 FR-028k) and the semillero group points at a `Semillero` course; the seed still only inserts for students it creates, so an existing local database keeps its rows | branch `fix/seed-semillero-enrolments`; no production effect, so not needed before the switch |

## 4. Calendar

| Milestone | Sessions | Done by |
|---|---|---|
| M0 Foundation (constitution, templates, CLAUDE.md / AGENTS.md) | S1–S3 | **Wed 2026-10-07** |
| M1 Spec 001 ELO engine + A-1 Playwright CI + A-2 traceability CI | S4–S13 | **Thu 2026-10-22** |
| M2 Spec 002 Persistence | S14–S19 | **Fri 2026-10-30** |
| M3 Spec 003 Learning path | S20–S25 | **Tue 2026-11-10** |
| — *Lean scope ends here* — | 25 sessions | **Tue 2026-11-10** |
| M4 Spec 004 Identity & access | S26–S29 | Tue 2026-11-17 |
| M5 Spec 005 AI integration | S30–S33 | Mon 2026-11-23 |
| M6 Spec 006 Teacher & exams | S34–S38 | Mon 2026-11-30 |
| M7 Spec 007 PvP | S39–S42 | Fri 2026-12-04 |
| M8 Spec 008 Item bank | S43–S46 | **Fri 2026-12-11** (full scope) |

**Lean scope (recommended):** M0–M3. The three riskiest areas get specs now; 004–008 get their
spec the first time a feature touches them ("spec on touch"), so no area is specced twice.

## 5. Definition of done

- Constitution ratified; CLAUDE.md points to it and no longer duplicates rules.
- Every in-scope area has spec/plan/tasks merged to `main`.
- Every acceptance scenario maps to a passing test (FR → test table in each spec).
- `/speckit-converge` reports no gaps for every in-scope spec.
- Drift found in surveys is either fixed or recorded as an accepted decision in the spec.
- From then on, new features run the full cycle starting at `/speckit-specify`.
