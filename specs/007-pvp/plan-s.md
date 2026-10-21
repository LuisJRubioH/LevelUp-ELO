# Plan — spec 007, delivery S: the League's answers in the statistics

**Spec**: [spec.md](spec.md) § Deliveries, S (US7; FR-070) · **Branch**: `007-s`, from `redesign`
· **Date**: 2026-10-21 · **Status**: approved (owner, 2026-10-21: O-S1 … O-S8 as recommended)

## Summary

Every League answer is judged on the server and written to `pvp_answers` (`match_id`, `user_id`,
`item_id`, `is_correct`, `answered_at`), and nothing reads it (survey V23): the student's
statistics (`/api/student/stats`, `Stats.tsx`), the teacher's student panel
(`/api/teacher/student/{id}`, `Dashboard.tsx`) and the export (`/api/teacher/export/xlsx`) are
built from `attempts` only. A student who misses an item ten times in the League shows nothing of
it, and the teacher cannot see which items the League exposes. Delivery S reads `pvp_answers` and
shows it, counted per topic and per item, **as League answers** — beside the practice figures, not
inside them — to the student and to their teacher. The match score keeps being computed in
memory (owner, V23); no rating is read from or rebuilt with these answers.

Scope confirmed from spec.md: delivery S = **FR-070** [CHANGE] and **US7-AS1**; no `[AS-IS]`
requirement of the spec is changed, but S must not move the figures pinned by spec 001 (ratings,
`total_attempts`, streak, the ranking's "≥ 1 attempt in the last 7 days"), spec 006 C1 (the
dashboard's attempts and accuracy, the «attention» list, the metrics, the export's existing
sheets) and spec 008 T (the subtopic report) — they are `attempts` figures.

## Constitution Check (1.2.0)

| Principle | S |
|---|---|
| The spec is the contract (I) | FR-070 and US7-AS1 each get a test written first; every point the spec leaves open — where the answers show, which matches count, what per item means, the export, the teacher's courses and window, the endpoints, the schema, a failed write — is an owner decision below (O-S1 … O-S8), not a choice of this plan |
| One source of truth (II) | `pvp_answers` is the only record of a League answer; it is never copied into `attempts`. The counts and shares are computed once, by a domain function, and the screens render them as given |
| Layers (III, R2) | the counting rules (per topic, per item, most missed first, the share) are pure functions with no I/O in a new `src/domain/pvp/answer_stats.py`, beside F's `outcome.py` (O-F9) and M's `matchmaking.py` / `match_items.py`; the application service calls the repository and the domain; the routers only compose; the code PR adds the file to spec 007 § Code Scope |
| Raw rows (R15) | the new reads return one raw row per answer (`match_id`, `course_id`, `item_id`, `topic`, `is_correct`, `answered_at`, and `user_id` on the teacher's read); no `COUNT`, average, rounding or order by result in SQL — the domain counts. No rating value is read or written |
| Dual database (IV, R1) | each new read lands in both repositories with an identical signature and `@_read_only` (R4); `db_sync_check.py`; integration tests on both engines; the D2 read-only list and `HOT_READS` gain them |
| Schema (R8) | **no schema change** under O-S7: `pvp_answers` already holds what S counts, and the reads reach it through `pvp_matches` (`idx_pvp_matches_players`) and `idx_pvp_answers_match (match_id, user_id)`. |
| Integrity of measurement (V; R15, R16, R19) | League answers never enter `attempts`, so they never reach a rating, the item-difficulty update, the selector's history, the ranking's eligibility or the streak; the close still applies the delta from the in-memory score (FR-007); nothing is rebuilt from `attempts` or `pvp_answers` |
| Security (VI, V2-R9) | a student reads only their own answers, never the opponent's; a teacher reads only their students (spec 006 FR-040, `_require_teacher_student`) and, under O-S5, only in the courses that link them; no `correct_option`, no item `difficulty` (FR-032's rule) and no opponent identity reach either screen |
| Async (R17) | the reads are REST endpoints (`def`, threadpool); nothing is added to the socket path, `_lock` or the close |
| Single process (R18) | unaffected: S reads stored rows only |
| Simplicity (VII) | no new dependency, no new table, no change to the match; one domain module, two repository reads, two endpoints, one export sheet, one screen component reused by the student and the teacher |

## Design

### What already exists

- **Write path (unchanged):** `api/websocket/pvp.py` judges each answer in memory
  (`_judge_answer`), updates the score, then `asyncio.to_thread(repo.save_pvp_answer, …)`; a
  failed insert is logged and the answer still scores (V23). An answer after the end, outside the
  match or repeated is not judged and not written (FR-003). `pvp_answers` has no chosen option, no
  answer time and no course: the course is `pvp_matches.course_id`, the topic is the item's.
- **Reads today:** `/api/student/stats` → `RatingReadService.ratings_view`,
  `get_total_attempts_count`, `get_study_streak`, `StudyReportService.subtopic_report`
  (`attempts` with a subtopic, spec 008 FR-042). `/api/teacher/student/{id}` →
  `TeacherService.get_student_dashboard` (ratings, `attempts`, procedures, subtopics); the
  student's KatIA record has its own endpoint (`/student/{id}/katia-history`, spec 005 FR-033).
  `/api/teacher/export/xlsx` → four sheets «Intentos», «Matrículas», «Procedimientos», «KatIA»,
  every one over spec 006 FR-040's student set (`_teacher_links_cte`, `_linked_course`).

### Composition with F, M and H (approved plans)

- **F (forfeit, `elapsed`, resume).** A player's answers before a drop are already written; after
  a resume, answers on the new socket are written the same way. F's `elapsed` and the speed
  tiebreak stay in memory (V23): S stores and shows **no answer time**. A forfeit is a finished
  match; its answers count like any other (O-S2).
- **M (`daily_cap`, "seen").** An over-cap match is `finished` with deltas 0 and reason
  `daily_cap`: its answers are study evidence and count (O-S2). M's "seen" (O-M9) reads
  `pvp_matches.item_ids` — items **served** — and S does not change it; S counts items
  **answered**. An item served and left unanswered is "seen" for M and absent from S's counts.
  M's `game_start` drops `difficulty`; S never shows it either.
- **H and E3 (`not_saved`, `orphaned`, `account_expired`).** These matches end `abandoned` with no
  rating change, but the answers given before the close are in `pvp_answers`; O-S2 decides
  whether they count.
- Under every option S reads only `pvp_answers` joined to `pvp_matches` and `items`; it reads no
  `elo_*` column, so a match's rating outcome never changes what S counts unless O-S2 (b) filters
  by status.

### FR-070 — the League's answers in the statistics (US7-AS1)

**Repositories (both, R1, `@_read_only`).**

- `get_league_answers(user_id)` — the student's own answers: one raw row per `pvp_answers` row of
  that `user_id`, joined to `pvp_matches` (for `course_id`, `status`), `items` (for `topic`) and
  `courses` (for the name). The match is found by `player1_id = ? OR player2_id = ?`, then the
  answers by `(match_id, user_id)` — both indexed (no schema change). Only closed matches
  (`status <> 'active'`): a live match's answers appear once it closes, so a student cannot read
  their running result through the statistics. An answer whose item is no longer in `items` is
  left out, as the subtopic report does.
- `get_teacher_league_answers(teacher_id, student_id=None)` — the same rows with `user_id`, for
  the teacher's student set (`_teacher_links_cte`, spec 006 FR-040) and, under O-S5 (a), only in
  the courses that link each student to the teacher (`_linked_course("a.user_id",
  "m.course_id")`); `student_id` narrows it to one student for the panel. It **reuses** spec 006's
  helpers and changes neither.
- Rows are raw: no `COUNT`, no `GROUP BY`, no order by result (R15 guard style). Volume is
  bounded: ≤ 10 answers per match.

**Domain** (`src/domain/pvp/answer_stats.py`, pure):

- `league_summary(rows, top_items=5) -> {"topics": [...], "items": [...], "answers": n,
  "correct": n}`:
  - per `(course_id, topic)`: `answers`, `correct`, `share_correct` (0.0 with no answers),
    weakest first, then the most answered — the order of spec 008's subtopic report, so both read
    the same way;
  - per item: `item_id`, `course_id`, `topic`, `answers`, `missed`, `last_answered_at`; only items
    missed at least once; most missed first, then the most recent; the first `top_items` (O-S3);
  - every row carries `"source": "league"` — the spec's "marked as League answers".
- `league_export_rows(rows, names)` — one row per student × course × topic × item with
  `answers` and `correct` (O-S4 (a)).

**Application.** `StudyReportService` (spec 008 T) gains `league_report(user_id)` and
`teacher_league_report(teacher_id, student_id)` — it is already the "for study, never a rating"
service; the alternative of a new `LeagueStatsService` is noted in § Risks. The item statements
for the most-missed items (O-S3, at most 5) are read with the existing `get_item_by_id` and passed
on as `content`, `options` and `image_url` only — never `correct_option` or `difficulty`.

**Endpoints (O-S6 (a)).**

- `GET /api/student/league/stats` → `{"answers", "correct", "topics": [...], "items": [...]}`, the
  student's own; items carry `content` and `options` as shown in the match (so the screen can
  render the statement with `MathContent`), never the key or the difficulty.
- `GET /api/teacher/student/{student_id}/league` → the same shape for one student, after
  `_require_teacher_student` (404 otherwise, as the KatIA history); 403 for a non-teacher
  (spec 006 FR-042).
- The export gains a fifth sheet **«Liga»** (O-S4) from `get_teacher_league_answers(teacher_id)`;
  the CSV export («Intentos» only) is unchanged.

**Screens.**

- **Student** (`Stats.tsx`): a card «En la Liga», after the subtopic report: one sentence that it
  does not change the ELO (as `subtopics.hint` says), the per-topic bars (the same visual as
  `SubtopicReport`, a new `components/Study/LeagueReport.tsx`, D1: its own accent, the League's
  token) and «Lo que más fallas en la Liga»: the most-missed items' statements through
  `MathContent` (D5), «falló n de m». No card when the student has no League answer. Copy in
  i18n `league.stats.*` (es source, en).
- **Teacher** (`Dashboard.tsx`, student panel): a section «En la Liga», after «Conversaciones con
  KatIA», with the same component (topic, answers, correct; the most-missed items with id and
  topic and the statement on hover/expand). It does not touch the dashboard table, the summary,
  the «attention» list or the metrics (O-S1).
- **Export** (`Export.tsx`): the sheet list gains «Liga» and «4 hojas» becomes «5 hojas».

**What does not change (O-S1 (a)).** `total_attempts`, the study streak, the activity heatmap,
achievements, the ELO chart, the subtopic report, the dashboard's attempts and accuracy and their
7/30/all window (spec 006 FR-043), the «attention» list and the summary (FR-041), the metrics, the
«Intentos» sheet and the CSV, the ranking's eligibility (spec 001 FR-028d), the selector's
history and the AI analysis's inputs (spec 005 FR-015). A test pins that a League match leaves all
of them as they were.

### Repositories (both, R1)

| Method | Change | Returns |
|---|---|---|
| `get_league_answers(user_id)` | new, `@_read_only` | raw answer rows of the student's closed matches |
| `get_teacher_league_answers(teacher_id, student_id=None)` | new, `@_read_only` | raw answer rows of the teacher's set in the linked courses |
| `save_pvp_answer` | unchanged under O-S8 (a) | — |

`src/application/interfaces/repositories.py` gains both reads (an application service calls them;
`test_repository_contracts.py` checks both ways). `tests/integration/test_spec002_d2_connections.py`
gains them in `HOT_READS` and the read-only list. No table, column or index under O-S7 (a);
`python scripts/db_sync_check.py` after the change.

## Shared files the code PR will touch (warning for parallel sessions)

- `src/infrastructure/persistence/sqlite_repository.py`, `postgres_repository.py` — two new reads
  (**also changed by F, M, G and E3 (#73)**: `finish_pvp_match`, the lobby reads; S adds reads
  only and changes no existing method). They reuse spec 006's `_teacher_links_cte` and
  `_linked_course` unchanged.
- `src/application/interfaces/repositories.py` — two signatures.
- `src/application/services/study_report_service.py` — two methods (**owned by spec 008 T**;
  only additions).
- `api/routers/student.py` — one endpoint (shared with specs 001, 003, 005, 006; F, M and H touch
  only `/pvp/history`).
- `api/routers/teacher.py`, `api/schemas/teacher.py`, `api/schemas/student.py` — **spec 006
  Code Scope**: one endpoint, the «Liga» sheet in `export_xlsx`, the response models.
- `frontend/src/pages/Teacher/Dashboard.tsx`, `frontend/src/pages/Teacher/Export.tsx`,
  `frontend/src/api/teacher.ts` — **spec 006 Code Scope**: the panel section, `SHEETS` and the
  «4 hojas» copy, one client call.
- `frontend/src/pages/Student/Stats.tsx`, `frontend/src/api/student.ts`, new
  `frontend/src/components/Study/LeagueReport.tsx` (+ `.css`) — Stats is shared with specs 001
  and 008 T (the subtopic card).
- `frontend/src/i18n/locales/es.ts`, `en.ts` — `league.stats.*` (F adds `league.tiebreak*`,
  4410/4411; M adds `league.unrated.*`, `historyReasons.daily_cap`; G adds refusal notices).
- `tests/integration/test_spec002_d2_connections.py` — `HOT_READS` and the read-only list (spec
  002).
- `specs/007-pvp/spec.md` — § Code Scope gains `src/domain/pvp/answer_stats.py`,
  `study_report_service.py`, `api/routers/teacher.py`, `Stats.tsx`, `Dashboard.tsx`,
  `Export.tsx`, `LeagueReport.tsx`; § Traceability rows FR-070, US7-AS1; delivery S → `closed`.
- `AGENTS.md` — § Database: a `pvp_answers` row («every judged League answer; read only by the
  statistics (spec 007 S), never by a rating»); § Architecture map: `domain/pvp/answer_stats.py`;
  R15's sentence "`attempts` is a log" gains "League answers live in `pvp_answers`, never in
  `attempts`".
- `docs/sdd/roadmap.md` — only the M7 progress note, if the owner tracks deliveries there.
- `render.yaml` — **no change**. SCHEMA_VERSION / `MIGRATION_SOURCES_DIGEST` — **no change**
  under O-S7 (a); 8 under (b) or (c).
- Not touched: `docs/transfer.md`, any `ops/*` branch, `api/websocket/pvp.py` (under O-S8 (a)).

**Overlap with spec 006 (another session owns its defects).** S adds to five files in spec 006's
Code Scope (`teacher.py`, the teacher schemas, `Dashboard.tsx`, `Export.tsx`, `api/teacher.ts`)
and reads its student set (FR-040) without changing it. It must not change what C1 pins
(FR-040 … FR-043: one student set, the summary, ranks and «attention», the window) nor X2's
results. Any defect fix in those files lands first or is rebased under S; S's additions are
appended (a new endpoint, a new sheet at the end, a new panel section at the end) to keep the
merge mechanical. Spec 007's Out of Scope says «A teacher view of PvP»: S shows the teacher the
student's League **answers** (study evidence), not the matches, opponents or results — see the
report note on spec.md below.

## Tests (written first; each `[CHANGE]` test fails on today's code)

| Test | Proves | Where |
|---|---|---|
| `test_spec007_league_summary_counts_per_topic_and_item` | FR-070 (pure): answers, correct, share per (course, topic); weakest first; per item only missed ones, most missed first, top 5; every row `source: "league"`; no answers → empty | `tests/unit/domain/test_spec007_s_answer_stats.py` |
| `test_spec007_league_export_rows_one_per_student_topic_item` | FR-070, O-S4 | same file |
| `test_spec007_league_answers_are_raw_rows_of_closed_matches` | FR-070, R15: one row per answer, own answers only, the opponent's absent, an active match's absent, the course from the match and the topic from the item | `tests/integration/test_spec007_s_league_stats.py` (both engines) |
| `test_spec007_teacher_league_answers_follow_the_student_set` | FR-070, spec 006 FR-040, O-S5: another teacher's student and a course that does not link the student are absent; a test student is absent | same file |
| `test_spec007_a_league_miss_reaches_the_students_statistics` | **US7-AS1**, FR-070: two students play a real match (`live_api`), one misses an item → `/api/student/league/stats` counts it under its topic and in the most-missed items, marked `source: "league"`, with no `correct_option` and no `difficulty` | same file (uvicorn) |
| `test_spec007_a_league_miss_reaches_the_teachers_view` | **US7-AS1**, FR-070: the same miss in `/api/teacher/student/{id}/league` for the student's teacher; 404 for another teacher; 403 for a student | same file |
| `test_spec007_the_export_has_a_league_sheet` | FR-070, O-S4: the workbook has «Liga» after «KatIA» with the miss; the four existing sheets keep their headers | same file |
| `test_spec007_answers_of_every_closed_match_count` | FR-070, O-S2 (a): answers of a `daily_cap`, a `forfeit` and an `abandoned` (`not_saved` / `orphaned`) match count; (b) would flip it to finished only | same file (seeded rows) |
| `test_spec007_league_answers_leave_the_practice_figures_unchanged` | FR-070 «marked as League answers», O-S1 (a), R15: after a League match, `total_attempts`, the streak, the subtopic report, the dashboard's attempts and accuracy, the metrics and the «Intentos» sheet are equal to before, `attempts` has no new row and no rating row changed | same file — **passes on today's code** (a guard, Phase 2) and stays green |
| `/api/student/league/stats` and `/api/teacher/student/{id}/league` require a token; shapes | FR-070 | `tests/api/test_pvp.py` |
| `test_spec002_d2_read_only_methods_write_nothing` with the two reads listed | R4 | `tests/integration/test_spec002_d2_connections.py` |
| e2e «la Liga aparece en mis estadísticas, aparte de la práctica» | US7-AS1 on the student's screen (mocked API) | `frontend/e2e/league-stats.spec.ts` |
| e2e «el docente ve lo que el estudiante falla en la Liga» and «el libro trae la hoja Liga» | US7-AS1 on the teacher's screen (mocked API) | same file (new, so spec 006's `spec006-c1-console.spec.ts` is not edited) |

Delivery A's, L's and H's pins stay green (the socket path is not touched), and so do spec 006
C1's console tests, spec 008 T's subtopic tests (`test_spec008_stats_and_teacher_view_carry_the_report`),
spec 005 K3's export test (the «KatIA» sheet) and `tests/api/test_spec001_api.py`'s `/stats`.

**Traceability rows to fill:** FR-070, US7-AS1 (delivery S → closed).

## Risks

- **Undercount.** A failed `save_pvp_answer` still scores (V23); that answer is missing from the
  statistics, never from the match. Rare; O-S8 decides whether to retry.
- **Topic drift.** The topic is the item's current one (as the subtopic report), so spec 008 T's
  topic merge moves old League answers with it; an item removed from `items` drops out.
- **Read cost without an index on `pvp_answers.user_id`.** The reads go through the player's
  matches; at ≤ 10 answers per match and the expected volume this is small. If it is not, O-S7
  (b) adds the index (SCHEMA_VERSION 8, after E3's 7).
- **Merge with spec 006's defect work** on `teacher.py`, `Dashboard.tsx`, `Export.tsx` (above),
  and with F / M on the repositories and i18n: S only adds, so whichever lands second rebases.
- **Service placement.** Putting the League report in `StudyReportService` touches a spec 008
  file; a separate `LeagueStatsService` avoids it at the cost of one more class. Either keeps the
  domain function as the single rule.
- **Before F / M land**, S works on today's matches (finished or abandoned): it reads no column
  F or M add.

## Decisions (owner, 2026-10-21)

The owner approved the recommended option of each decision.

- **O-S1 — their own section:** the student's Stats card «En la Liga», the teacher's student panel
  section and an export sheet, and nowhere else; every `attempts` figure (attempts, accuracy,
  streak, activity, achievements, subtopic report, dashboard, «attention», metrics, ranking
  eligibility, AI analysis) stays as it is.
- **O-S2 — every closed match:** every stored answer of a closed match counts, whatever its outcome
  — finished, forfeit (F), `daily_cap` (M), abandoned (`not_saved`, `orphaned`, `account_expired`).
  Active matches are never read.
- **O-S3 — per topic and the 5 most-missed items:** per topic (answers, correct, share) plus the 5
  most-missed items — the statement rendered with `MathContent`, «falló n de m» — on both screens;
  never the key, never the difficulty.
- **O-S4 — a fifth XLSX sheet «Liga»:** one row per student × course × topic × item with answers and
  correct (the student named as in «Intentos»); the CSV unchanged.
- **O-S5 — the linking courses, whole history:** only matches in the courses that link the student
  to the teacher (spec 006 FR-040), over the whole history.
- **O-S6 — two new read endpoints:** `GET /api/student/league/stats` and
  `GET /api/teacher/student/{id}/league`; `StudentStatsResponse` and `get_student_dashboard` stay
  untouched.
- **O-S7 — no schema change:** read through `pvp_matches` and the existing `(match_id, user_id)`
  index.
- **O-S8 — a failed answer write stays as today:** logged, the answer still scores, and it is
  missing from the statistics.
