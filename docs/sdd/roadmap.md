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
| 004 | Identity & access | JWT/refresh, roles, teacher approval, groups, admin, test users | 4 |
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
| A-1 | **Playwright in CI** — run the existing Chromium suite (`frontend/e2e/`) on PRs | deterministic fixtures, no flaky retries hiding failures; traces + screenshots kept as artifacts on failure; README note that these tests mock the API and verify frontend flows, not backend integration | during M1 | 1 |
| A-2 | **Traceability check in CI** — script over `specs/*/spec.md` | unique FR / scenario IDs; every FR and scenario has a row; each reference resolves to a collected test (`pytest --collect-only`, Playwright `--list`); `PENDING` allowed on spec branches before the code PR, rejected on the code PR; referenced tests pass and are not skipped. Assertion adequacy stays a review item | with spec 001 code PR (needs its first traceability table) | 1 |

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
