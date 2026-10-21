# Tasks — spec 007, delivery S (the League's answers in the statistics)

**Plan**: [plan-s.md](plan-s.md) (draft for the owner's approval; decisions O-S1 … O-S8 open).
FR-070 is `[CHANGE]`; delivery S changes no `[AS-IS]` requirement of spec 007 and does not touch
the socket path pinned by delivery A, but it must leave the `attempts` figures of spec 001, spec
006 C1 and spec 008 T as they are.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[US7]**: User Story 7 — The League's answers count for study

---

## Phase 0: Owner decisions (Blocking)

- [ ] T000 The owner answers O-S1 … O-S8 (plan-s § Decisions); record each answer in plan-s and
  set its status to approved. The tests below are written for the recommended options; an answer
  that differs changes the named tests before they are written (O-S2 (b) flips
  `test_spec007_answers_of_every_closed_match_count`; O-S3/O-S4/O-S5/O-S6 change the shapes, the
  sheet and the endpoints; O-S7 (b)/(c) adds T005 and SCHEMA_VERSION 8 after E3's 7; O-S8 (b)
  adds a socket-path task and a delivery A re-run).

---

## Phase 1: Setup

- [ ] T001 Create the empty module `src/domain/pvp/answer_stats.py` (with the package
  `__init__.py` if neither F nor M has landed) and the empty test files
  `tests/unit/domain/test_spec007_s_answer_stats.py`,
  `tests/integration/test_spec007_s_league_stats.py` (engine fixture and `live_api` as in
  `tests/integration/test_pvp_enrolment.py`) and `frontend/e2e/league-stats.spec.ts`; no
  behaviour yet.

---

## Phase 2: Pin Current Behaviour (Blocking)

- [ ] T002 Run against the unchanged code and record the green run here; they must stay green
  through every task below:
  - delivery A, L, H: `tests/integration/test_pvp_*.py`, `tests/integration/test_spec007_h_history.py`,
    `tests/unit/infrastructure/test_pvp_logic.py`, `tests/api/test_pvp*.py`,
    `frontend/e2e/league.spec.ts` (S does not touch the socket path; they prove it);
  - spec 001: `tests/api/test_spec001_api.py` (`/stats`), the PvP pins
    `tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once`;
  - spec 006 C1: `tests/integration/test_spec006_c1_console.py`,
    `frontend/e2e/spec006-c1-console.spec.ts`;
  - spec 008 T: `tests/integration/test_spec008_t_topics.py` (the subtopic report in `/stats` and
    the teacher's panel);
  - spec 005 K3: `tests/integration/test_spec005_k3_record.py` (the «KatIA» sheet);
  - spec 002 D2: `tests/integration/test_spec002_d2_connections.py`;
  - `frontend/e2e/stats.spec.ts`.
- [ ] T003 [P] Guard for FR-070 («marked as League answers», O-S1 (a), R15):
  `test_spec007_league_answers_leave_the_practice_figures_unchanged` in
  `tests/integration/test_spec007_s_league_stats.py` (both engines, `live_api`): after a real
  League match, `total_attempts`, the study streak, the subtopic report, the teacher dashboard's
  attempts and accuracy, the metrics and the «Intentos» sheet equal their values before the
  match, `attempts` has no new row and no `student_course_topic_elo` row changed beyond the
  match's own delta — **passes on the unchanged code** and stays green after every task.

**Checkpoint**: the practice figures and the match pinned — S can add the League's.

---

## Phase 3: User Story 7 — The League's answers count for study (Priority: P3)

**Goal**: the student and their teacher see the League's answers counted per topic and per item,
marked as League answers, beside the practice figures; nothing in the match or the ratings changes.

**Independent Test**: `tests/integration/test_spec007_s_league_stats.py` — a student plays a
match and misses an item; their statistics and their teacher's view count that miss.

### Tests for User Story 7 (written first; each must FAIL before its implementation task)

- [ ] T010 [P] [US7] `[CHANGE]` `test_spec007_league_summary_counts_per_topic_and_item` and
  `test_spec007_league_export_rows_one_per_student_topic_item` for FR-070 (O-S3, O-S4) in
  `tests/unit/domain/test_spec007_s_answer_stats.py` — **fail** before T020
- [ ] T011 [P] [US7] `[CHANGE]` `test_spec007_league_answers_are_raw_rows_of_closed_matches`,
  `test_spec007_teacher_league_answers_follow_the_student_set` and
  `test_spec007_answers_of_every_closed_match_count` for FR-070 (R15, spec 006 FR-040, O-S2,
  O-S5) in `tests/integration/test_spec007_s_league_stats.py` (both engines; seeded matches:
  finished, `daily_cap`, `forfeit`, `not_saved`, `orphaned`, one active; an opponent's answers;
  another teacher's student; an unlinked course; a test student) — **fail** before T021
- [ ] T012 [P] [US7] `[CHANGE]` `test_spec007_a_league_miss_reaches_the_students_statistics` and
  `test_spec007_a_league_miss_reaches_the_teachers_view` for **US7-AS1**, FR-070 in the same file
  (uvicorn, a real match through `live_api`: the miss counted under its topic and in the
  most-missed items, `source: "league"`, no `correct_option`, no `difficulty`; 404 for another
  teacher, 403 for a student) — **fail** before T023
- [ ] T013 [P] [US7] `[CHANGE]` `test_spec007_the_export_has_a_league_sheet` for FR-070 (O-S4) in
  the same file: «Liga» after «KatIA» with the miss; the four existing sheets keep their headers —
  **fails** before T024
- [ ] T014 [P] [US7] `[CHANGE]` `/api/student/league/stats` and
  `/api/teacher/student/{id}/league` require a token and return the documented shape, for FR-070
  in `tests/api/test_pvp.py` — **fail** before T023
- [ ] T015 [P] [US7] `[CHANGE]` the two new reads in `HOT_READS` and the read-only list of
  `tests/integration/test_spec002_d2_connections.py` (R4) — **fail** before T021
- [ ] T016 [P] [US7] `[CHANGE]` e2e «la Liga aparece en mis estadísticas, aparte de la práctica»,
  «el docente ve lo que el estudiante falla en la Liga» and «el libro trae la hoja Liga» for
  US7-AS1, FR-070 in `frontend/e2e/league-stats.spec.ts` (mocked API) — **fail** before T025

### Implementation for User Story 7

- [ ] T020 [US7] FR-070: `league_summary` and `league_export_rows` in
  `src/domain/pvp/answer_stats.py` — pure, no I/O (T010 green;
  `tests/unit/test_architecture_layers.py` green)
- [ ] T021 [US7] FR-070: `get_league_answers(user_id)` and
  `get_teacher_league_answers(teacher_id, student_id=None)` in **both** repositories, raw rows,
  `@_read_only`, reusing `_teacher_links_cte` / `_linked_course` unchanged; both signatures in
  `src/application/interfaces/repositories.py` (T011, T015 green;
  `tests/unit/application/test_repository_contracts.py` and
  `test_spec001_no_rating_aggregation_in_repositories_or_routers` green)
- [ ] T022 [US7] `python scripts/db_sync_check.py` — both repositories in step, no schema
  difference (O-S7 (a))
- [ ] T023 [US7] FR-070: `StudyReportService.league_report` / `teacher_league_report` (the
  most-missed items' statements through `get_item_by_id`, without key or difficulty); the
  endpoints `GET /api/student/league/stats` in `api/routers/student.py` and
  `GET /api/teacher/student/{student_id}/league` in `api/routers/teacher.py` (after
  `_require_teacher_student`), with their response models in `api/schemas/` (T012, T014 green)
- [ ] T024 [US7] FR-070: the «Liga» sheet appended to `export_xlsx` in `api/routers/teacher.py`,
  through `_append_xlsx_row` (CSV injection guard) (T013 green; the «KatIA» and C1 export tests
  green)
- [ ] T025 [US7] Frontend: `components/Study/LeagueReport.tsx` (+ `.css`, tokens only, D1, D5:
  statements through `MathContent`); the «En la Liga» card in `pages/Student/Stats.tsx`; the
  «En la Liga» section in the student panel of `pages/Teacher/Dashboard.tsx`; «Liga» in
  `pages/Teacher/Export.tsx`'s `SHEETS` and «5 hojas»; `studentApi.leagueStats`,
  `teacherApi.studentLeague`; copy in `league.stats.*` (es, en) (T016 green;
  `frontend/e2e/stats.spec.ts`, `spec006-c1-console.spec.ts` green)

**Checkpoint**: US7 functional; T010–T016 green; T003 and every Phase 2 pin still green.

---

## Phase N: Traceability & Verification

- [ ] T090 Fill § Traceability rows FR-070 and US7-AS1; add `src/domain/pvp/answer_stats.py`,
  `src/application/services/study_report_service.py`, `api/routers/teacher.py`,
  `frontend/src/pages/Student/Stats.tsx`, `frontend/src/pages/Teacher/Dashboard.tsx`,
  `frontend/src/pages/Teacher/Export.tsx`, `frontend/src/components/Study/LeagueReport.tsx` to
  § Code Scope; mark delivery S `closed`
- [ ] T091 Review assertion adequacy: the US7-AS1 tests check the miss on **both** screens'
  endpoints from a real match, the `source` mark, and that neither the key nor the opponent's
  answers appear; T003 checks every practice figure, not a sample
- [ ] T092 AGENTS.md: § Database gains `pvp_answers`; § Architecture map gains
  `domain/pvp/answer_stats.py`; R15 notes that League answers live in `pvp_answers`, never in
  `attempts`. `docs/sdd/roadmap.md`: the M7 note, if the owner tracks deliveries there
- [ ] T093 Verification (AGENTS.md § Verify): full suite on both engines, `db_sync_check.py`,
  `pnpm run build`, Playwright `league-stats.spec.ts`, `stats.spec.ts`,
  `spec006-c1-console.spec.ts`, `league.spec.ts`, `check_traceability.py`, black, flake8
- [ ] T094 V1 check: the repositories are shared with V1; V1 neither reads `pvp_answers` nor
  calls the new methods (smoke import of `src/interface/streamlit/app.py`)

---

## Dependencies & Execution Order

- T000 (owner decisions) → T001 → T002–T003 (pins green on unchanged code) → T010–T016 written and
  failing → T020–T025 → T090–T094.
- T020 depends on T010; T021 on T011 and T015; T022 on T021; T023 on T012, T014, T020 and T021;
  T024 on T013, T020 and T021; T025 on T016 and T023–T024.
- Under O-S7 (b)/(c), a T005 (the migration in both repositories, SCHEMA_VERSION 8, the new
  `MIGRATION_SOURCES_DIGEST`, `test_spec002_schema_version.py`) runs after E3 (#73) has landed and
  before T021.

## Notes

- S touches five files of spec 006's Code Scope (`api/routers/teacher.py`, `api/schemas/teacher.py`,
  `frontend/src/pages/Teacher/Dashboard.tsx`, `frontend/src/pages/Teacher/Export.tsx`,
  `frontend/src/api/teacher.ts`); the session that owns spec 006's defects is told before T023 —
  S only appends (an endpoint, a sheet at the end, a panel section at the end).
- F and M change the repositories and i18n in parallel; S adds reads only and changes no existing
  method, so whichever lands second rebases.
