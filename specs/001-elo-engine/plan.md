# Implementation Plan: ELO Engine

**Branch**: `001-elo-engine` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-elo-engine/spec.md`

## Summary

Pin the current rating engine with characterization tests, then move the rating to a single,
unambiguous key — **student × course × topic** — in a new table, derive every course and overall
rating from it with pure domain functions, and route every writer (answer, diagnostic, procedure,
PvP) and every V2 reader through that one definition. Legacy rows from the old single-name store
are reconciled once into approximate baselines with provenance. Alongside: honest reporting of
invalid attempts, a preview computed by the engine, one rank scale, logged badge failures, and
removal of dead rating code. Design decisions: [research.md](research.md) (R1–R17).

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5 / React 19 (frontend)
**Primary Dependencies**: FastAPI, pydantic, psycopg2 (PostgreSQL), sqlite3; Vite, Zustand,
TanStack Query, react-i18next
**Storage**: PostgreSQL (Supabase) in deploy, SQLite locally and in tests — dual repository (R1)
**Testing**: pytest (unit, integration over both engines, API); Playwright exists, not in CI
**Target Platform**: Linux web service on Render (single process) + SPA on Vercel
**Project Type**: web application (API + SPA), legacy Streamlit UI frozen
**Performance Goals**: no regression beyond 10 % of the measured 26 CPU-ms per request
**Constraints**: additive-only migrations; one process (`WEB_CONCURRENCY=1`); answer transaction
lock order users → items; correct option never leaves the backend
**Scale/Scope**: 20–30 concurrent students; 49 courses, 403 topic labels, ≈ 4.6 k items;
≤ a few hundred rating rows per student

## Constitution Check

*Gate before Phase 0 and re-checked after Phase 1 design.*

| Principle | Status | How this plan complies |
|---|---|---|
| I. Spec is the contract | ✅ | every change traces to an FR; `[AS-IS]` pinned before refactor, `[CHANGE]` tests fail first (tasks phase 2) |
| II. One source of truth | ✅ | `student_course_topic_elo` is the only rating state; course/overall/rank derived by one domain definition; `users.current_elo` and the old table stop being sources; preview uses the engine formula; one rank table (resolves D-1, D-2) |
| III. Layers | ✅ | formulas, validity window, PvP deltas, diagnostic tiers, aggregation, ranks and ranking order move **into** `domain/`; orchestration only in `rating_read_service.py`; repositories return participants and raw rows; atomic addition of a domain-computed delta is the one permitted write pattern (research R3) |
| IV. Dual DB | ✅ | new table/columns in both engines; idempotent additive migration; integration tests parametrised over both |
| V. Measurement integrity | ✅ | answer stays one transaction; invalid attempts report no change; PvP reports applied delta; idempotency unchanged |
| VI. Security | ✅ | no new secret; `/meta/ranks` exposes only public scale data; `correct_option` still never sent |
| VII. Simplicity | ✅ | dead code removed (R15); no cache tables; capacity re-measured |
| VIII. Pedagogy | ✅ | promotion is a new-context baseline, never a loss; approximate baselines labelled as such |
| Validation & errors | ✅ | badge failure logged (resolves D-3); PvP persistence failure reported as not applied |
| V1 frozen | ✅ | freeze = Streamlit interface + code used only by it (R18). Shared readers comply; V1 call sites adapted; V1-only current-rating readers migrated to the derived ratings (FR-028f); history readers untouched; V1 regression test (constitution § Stack) |

Post-design re-check: unchanged — no principle violated by data-model or contracts.

## Project Structure

### Documentation (this feature)

```text
specs/001-elo-engine/
├── spec.md
├── plan.md              # this file
├── research.md          # R1–R17
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.md
│   └── domain.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (touched by this feature)

```text
src/domain/elo/
├── model.py             # expected_score, rating_delta, next_rd, item_difficulty_delta,
│                        # is_valid_response_time, procedure_elo_delta, pvp_deltas,
│                        # diagnostic_tier/baseline  (dead code removed)
├── vector_elo.py        # VectorRating without impact_modifier, delegates to model.py
├── uncertainty.py       # RatingModel delegates to model.py (or is folded into it)
├── aggregation.py       # NEW: course_rating, overall_rating
└── ranks.py             # NEW: RANKS, rank_for
src/domain/selector/item_selector.py      # unchanged
src/application/services/rating_read_service.py  # NEW: ratings_view(_bulk), course_rating_of,
                                                 # group_basis, ranking_view, ranking_rank
src/application/services/student_service.py  # process_answer, get_next_question
src/application/services/teacher_service.py  # reads through RatingReadService
src/application/interfaces/repositories.py   # contract list updated
src/infrastructure/persistence/
├── sqlite_repository.py    # new table, writers, reconciliation  ┐ mirrored (R1)
└── postgres_repository.py  # same                                 ┘
src/interface/streamlit/    # V1: adapt calls only (frozen)
api/routers/student.py      # next-question preview, answer, stats, diagnostic, map
api/routers/teacher.py      # dashboard, student report
api/routers/meta.py         # NEW: GET /meta/ranks (registered in api/main.py under /api)
api/schemas/{student,teacher}.py
api/websocket/pvp.py        # course rating for lobby, applied deltas in game_end
frontend/src/pages/Student/Practice.tsx, Stats.tsx
frontend/src/pages/Teacher/Dashboard.tsx, Groups.tsx
frontend/src/pages/Home.tsx
frontend/src/components/ELO/RankBadge.tsx
frontend/src/i18n/locales/{es,en}.ts
tests/unit/domain/  tests/unit/application/  tests/integration/  tests/api/
```

**Structure Decision**: existing layered layout (constitution III); two new domain modules,
one new router file at most; no new top-level directories.

## Delivery order (input for `/speckit-tasks`)

1. **Pin** — characterization tests for every `[AS-IS]` FR touched, green on unchanged code.
   Includes the current behaviour of every reader in research R18 that this spec changes.
2. **Domain** — move formulas/validity/tiers/ranks into `domain/`; aggregation; remove dead code.
   Pins stay green (pure moves).
3. **Store** — new table + `pvp_matches` columns in both engines; repository contract updated.
4. **Writers** — answer transaction, diagnostic, procedure, PvP on the new key (`[CHANGE]` tests
   for FR-029, 029b, 029c, 009 written failing first).
5. **Readers** — `RatingReadService`; every V2 or shared reader in research R18 goes through it:
   stats, teacher dashboard and student report, map, `/ai/socratic` and teacher AI analysis,
   exam snapshot, PvP lobby, **group ranking with its basis** (FR-028a–e, 029a, 026). The V1-only
   rankings and a student's own rank use `ranking_view`/`ranking_rank` with their participation rules
   kept separate from the rating basis and one tie rule (FR-028f, 028h); weekly snapshots stay
   history (FR-028g).
   **V1 is never left broken**: every task that changes a shared signature or deletes a shared
   reader adapts its V1 call sites in the same task; a V1 smoke pin stays green at every
   checkpoint.
6. **Reconciliation** — FR-033–036, 034a/b; idempotency test on both engines.
7. **Contracts** — API fields, `/meta/ranks`, `game_end` message.
8. **Frontend** — preview from API, single rank source, "pending diagnostic", history view.
9. **V1** — no separate phase: smoke pin from Phase 2, regression test in US1, call sites adapted
   inside the tasks that change them.
10. **Verify** — full suite, `db_sync_check`, frontend build, capacity, traceability table,
    remove D-1/D-2/D-3 from the constitution's Known Deviations.

## Focused regression checks (required in tasks, both engines where a repository is involved)

| Check | Proves | FR |
|---|---|---|
| Group ranking with `course_id` excludes attempts and ratings of other courses (fails on today's code) | course filter works | 028d |
| Group ranking basis: requested → group course → overall; 400 unknown course, 403 not enrolled; basis returned; no substitution for unrated students | basis precedence | 028d |
| Group ranking orders by derived rating, unrated students last as pending | canonical source | 028d, 028b |
| Number and label agree: 999.6 → 1000 "Plata I", 999.5 → 1000 "Plata I", 999.4 → 999 "Plata II" on stats, teacher dashboard, teacher report and rankings; stored value unchanged | display label | 028j |
| Rounding: `round_for_display` half up (1199.5→1200, 1200.5→1201, 1200.4999→1200, 0.5→1); averages kept full precision (topics 1200.4/1200.4/1201.4 → 1201); API returns ranking ratings as integers; clients do not round | rounding rule | 028i |
| Competition ranking: equal ratings at display precision share a rank (1, 2, 2, 4); attempts never break ties; user id orders display within a tie only; pending last with no rank; identical on both engines; a student's own rank = their entry's rank; `limit` never changes a rank | competition ranking | 028h |
| Every rating reader in R18 returns values equal to `ratings_view` for the same student (single fixture, all readers) | canonical reads | 028, 028a, 029a |
| Legacy rows and `users.current_elo` changed by hand do not change any read | legacy excluded | 036, 028 |
| Student in a grade with no rated course: stats, teacher dashboard, rankings show pending, no number, no rank | pending diagnostic | 028b |
| Promotion fixture: no endpoint reports a negative overall delta; old-grade courses still readable | promotion | 028c |
| A student's own rank equals the rank of their entry in the corresponding list, same participation rule | rank consistency | 028f, 028h |
| Weekly ranking: a student active this week appears; a student inactive this week with a higher rating does not; ordering by derived rating | participation ≠ rating source | 028f |
| Stored weekly snapshots unchanged after migration and after new answers | history preserved | 028g |
| V1 answer path (`student_view.handle_answer_topic` call shape) persists to the item's course+topic; V1 modules import and services construct — smoke green at every checkpoint | V1 compatibility | 029, constitution § Stack |
| Explicit `time_taken = 0` is invalid: attempt recorded, rating, RD and item difficulty unchanged; an absent time still counts as 30 s (fails on today's code) | zero is not missing | 008a |
| Retry key, fixed boundary values (rating 1181, difficulty 1000, RD 350, correct): the first response and the retry return the same persisted attempt values; the rating is applied once and stored at full precision (fails on today's code on PostgreSQL) | retry consistency | 012, 012a |
| Storage precision on both engines: a stored 999.4999999 reads back unchanged and displays 999 "Plata II" on SQLite and PostgreSQL (fails with a PostgreSQL `REAL` column) | precision parity | 028i, 028j |
| Architecture guard: no rating aggregation/ordering in repositories or routers (supplementary to the behavioural tests above) | layer split | constitution III |
| Each repository test above runs parametrised on SQLite and PostgreSQL with identical results | engine parity | IV |

## Complexity Tracking

| Deviation | Why needed | Simpler alternative rejected because | Approval / deadline |
|---|---|---|---|
| — | No deviation: every current-rating reader, including the V1-only rankings, is migrated (research R18, FR-028f) | — | — |
