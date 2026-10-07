# Research: ELO Engine (spec 001)

Phase 0 of `/speckit-plan`. Every decision cites the requirement it serves. No open
`NEEDS CLARIFICATION` remains.

## Facts established (2026-10-06)

| Fact | Evidence | Consequence |
|---|---|---|
| 23 of 403 topic labels are shared by several courses ("Geometría" in 5, "Lógica" in 6) | `items/bank/**.json` scan | ratings must be keyed by course **and** topic (FR-029) |
| ≥ 10 course names equal a topic label of the same course ("Álgebra Básica", "Geometría", …) | `courses.name` ∩ `items.topic`, local DB | a single-name key cannot tell a V1 course row from a topic row → the whole old store is legacy (FR-033–036) |
| `student_topic_elo` PK is `(user_id, topic)` | both repositories | adding `course_id` to the PK is not an additive migration (Principle IV) |
| `users.current_elo` is `NOT NULL DEFAULT 1000` | both repositories | it cannot express "pending diagnostic" (FR-028b) |
| V2 overall readers: `aggregate_global_elo` (stats, ai, teacher student view), ad-hoc `AVG(student_topic_elo)` in `get_teacher_dashboard_stats` | grep | all must route through one derivation (FR-028a) |
| Rankings (`get_global_ranking`, `get_course_ranking`, `get_weekly_ranking`) replay `attempts.elo_after` | `sqlite_repository.py:1880-1975` | violates Principle II, but only **V1** calls them (frozen) → Known Deviation proposal, see plan § Complexity Tracking |
| Validity window lives in `_tiempo_valido` in both repositories | `sqlite_repository.py:1294` | a domain rule in infrastructure; FR-009 needs it before the result is reported |
| Course catalogue per level/grade exists: `get_available_courses_by_level(level, grade)` + `enrollments` | repositories | "current level and grade" (FR-028a) is computable without new data |

## Decisions

### R1 — New rating store; old table becomes the legacy store (FR-029, FR-033–036)
- **Decision**: new table `student_course_topic_elo`, PK `(user_id, course_id, topic)`, with
  provenance columns. All writers move to it. `student_topic_elo` is no longer written and is read
  only by reconciliation.
- **Rationale**: the only additive way to change the key; removes label ambiguity at once
  (every old row is legacy by definition, no row classification needed).
- **Alternatives**: add `course_id` to `student_topic_elo` (PK change → not additive; and old
  rows would still be ambiguous); keep one table and prefix keys `course::topic` (encodes identity
  in a string, breaks every existing reader silently).

### R2 — Stable identity (FR-029)
- **Decision**: course identity = `courses.id` (file slug); topic identity = the topic label
  **within** its course. The pair `(course_id, topic)` is the key. Labels are never compared across
  courses and never compared with course names.
- **Assumption recorded**: renaming a topic label in the bank creates a new topic (old rating stays
  under the old label). Topic ids are out of scope (spec 008).

### R3 — Derived ratings are pure domain functions (FR-028a, FR-029a)
- **Decision**: `src/domain/elo/aggregation.py` with `course_rating(topic_ratings) -> float | None`
  and `overall_rating(course_ratings) -> float | None` (`None` = pending diagnostic), plus
  `rank_competition` for every ranking. **`src/application/services/rating_read_service.py`** is the
  only orchestration point: it loads raw rows and participants from the repository and calls the
  domain functions (`ratings_view`, `ratings_view_bulk`, `course_rating_of`, `group_basis`,
  `ranking_view`, `ranking_rank`). Every rating reader in `api/` and in V1 views goes through it.
- **Layer split (owner, 2026-10-06)**: calculations in `domain/`; orchestration in the read
  service; participant selection and raw-row access in repositories. Repositories never average or
  order by a rating. **Permitted persistence pattern**: adding a delta the domain already computed,
  atomically inside a write transaction (`current_elo = MAX(0, current_elo + :delta)`) — that is
  what keeps procedure and PvP effects exactly-once (AGENTS R15/R19); it is not rating arithmetic.
- **Guards**: an architecture test (no rating aggregation or ordering in repositories/routers) is a
  supplementary check; the behavioural tests are what prove FR-028–028h.
- **Rationale**: Principle II (one definition), Principle III (arithmetic in domain).
- **Alternatives**: SQL views per engine (duplicated logic in two dialects, harder to test);
  keeping `users.current_elo` as a cache (can't be `NULL`; second place to keep consistent).

### R4 — `users.current_elo` becomes legacy (FR-028)
- **Decision**: stop writing and reading it. Column stays (no `DROP`). `_refresh_global_elo` is
  removed; PvP stops reading it (R8).
- **Rationale**: a stored average is a second source; it cannot represent "pending".

### R5 — Validity is a domain rule (FR-008, FR-009)
- **Decision**: `is_valid_response_time(seconds)` in `src/domain/elo/model.py`; `compute()` in
  `StudentService.process_answer` uses it, so for an invalid attempt `elo_after = elo_before`,
  `rd_after = rd_before`, item difficulty unchanged, `elo_valid = False` — and the API reports
  `delta_elo = 0`. Repositories persist what `compute` returns and no longer decide validity.
- **Alternatives**: keep the check in the repository and patch the response (two places decide).

### R6 — Answer transaction on the new key (FR-010, FR-029)
- **Decision**: `save_answer_transaction(user_id, item_id, compute, ...)` — `topic` parameter
  removed; the repository reads the item's `course_id` and `topic` under the lock and the rating
  row `(user_id, course_id, topic)`. Lock order unchanged: users → items (PostgreSQL `FOR UPDATE`;
  SQLite `BEGIN IMMEDIATE`). `attempts.topic` stores the item's topic from now on.
- **API**: `AnswerRequest.elo_topic` stays accepted for client compatibility, is ignored, and is
  marked deprecated (no validation error for old clients).

### R7 — Selection rating (FR-016–019, FR-029a)
- **Decision**: `get_next_question` receives the selection rating explicitly: the topic rating when
  `topic_filter` is set, otherwise `course_rating` of the course (1000 when `None`).
  `build_vector_rating` loses the diagnostic course seed (FR-004 note).

### R8 — PvP (FR-025, FR-026, FR-029b, FR-029c)
- **Decision**: lobby slot rating = course rating of the match course (via R3; 1000 if none).
  `finish_pvp_match` adds the delta to every `(user, course_id, *)` row in one transaction; with no
  rows it persists applied delta 0 and reason `no_rated_topics`. Additive columns
  `pvp_matches.elo_reason_p1`, `elo_reason_p2`. The method returns the **applied** deltas; the
  WebSocket result message sends those. Idempotency guard `AND status='active'` unchanged.

### R9 — Procedure and diagnostic writers (FR-020–024, FR-029)
- **Decision**: procedure bump targets `(student, item.course_id, item.topic)`, floor 0, creates
  the row at `1000 + delta` when absent (current edge behaviour). Diagnostic baseline writes
  `(student, course_id, topic)` with provenance `diagnostic`, skipping topics with practice in
  that course.

### R10 — Reconciliation (FR-033–036, FR-034a/b)
- **Decision**: `_reconcile_legacy_ratings()` in both repositories, called by the schema bootstrap
  after existing backfills (so `scripts/migrate.py` runs it at deploy; local/tests in-process),
  under the existing advisory lock on PostgreSQL. Algorithm, per student:
  1. Eligible contexts = `(course_id, topic)` pairs with a practice attempt on an item of that
     course and topic, plus every topic of a course whose diagnostic the student took.
  2. Skip pairs that already have a row in the new table (FR-033).
  3. Source (a): legacy row keyed by the topic label, if the student has attempts **recorded under
     that key** on items of that course, or took that course's diagnostic.
     Source (b): the course's legacy row — candidates keyed by `course_id` and by course name;
     most recent `updated_at` wins, `course_id` on tie (FR-035) — only if the student practised
     that topic in that course.
  4. Insert with `INSERT … ON CONFLICT DO NOTHING`, provenance `legacy_topic_row` or
     `legacy_course_row`, `approximate = TRUE`, `legacy_source_key`, `reconciled_at`.
  5. Legacy rows never selected stay untouched (FR-034b).
- **Idempotency**: step 2 + `ON CONFLICT DO NOTHING` make a second run a no-op (SC-008).
- **Alternatives**: replay attempts (forbidden by FR-036 and Principle II).

### R11 — One rank scale (FR-031, FR-031a)
- **Decision**: `src/domain/elo/ranks.py` holds the 16-level table (moved from
  `api/routers/student.py::_RANK_THRESHOLDS`) and `rank_for(rating) -> str | None`. Every API
  response that carries a rating carries `rank_label`. Public `GET /api/meta/ranks` returns the
  scale for the home page. Frontend `RANKS` arrays in `Home.tsx`, `Teacher/Dashboard.tsx`,
  `Teacher/Groups.tsx` are deleted; colours stay presentation in one map keyed by label
  (`RankBadge.tsx`). Diagnostic leagues (`_DIAG_LEAGUES`) stay as placement.

### R12 — Preview from the engine (FR-030)
- **Decision**: domain `rating_delta(rating, rd, difficulty, result)` is the single formula used by
  `VectorRating.update` and by the preview. `NextQuestionResponse` gains
  `preview: {on_correct, on_wrong}` for the selected item and the student's topic rating.
  `estimateEloDelta()` in `Practice.tsx` is deleted.

### R13 — Pending diagnostic and promotion (FR-028b, FR-028c)
- **Decision**: `StudentStatsResponse.global_elo: float | None`, new `overall_status:
  "rated" | "pending_diagnostic"`, `rank_label: None` when pending; per-course list with
  `current_context: bool` so earlier-grade courses render as history. No endpoint returns a delta
  between overall ratings; the only deltas are per answer, per procedure and per match, all
  within one course (FR-028c holds by construction). i18n keys es/en for "pending diagnostic".

### R14 — Badges failure (FR-015)
- **Decision**: `logger.exception(...)` replaces `except Exception: pass`; result unchanged.

### R15 — Dead code removed (constitution VII)
- `calculate_dynamic_k`, `update_elo`, `StudentELO`, `impact_modifier` (parameter and `cog_data`
  key), `_tiempo_valido` (moved, R5), `_refresh_global_elo` (R4), `_RANK_THRESHOLDS` (moved, R11).
  Tests that only exercised dead code are deleted with it.

### R16 — V1 (frozen) compatibility
- **Decision**: V1's `process_answer(..., elo_topic=course name)` call drops `elo_topic` (shared
  service change → regression test through V1's call path, constitution § Stack). V1 screens keep
  their own rank labels and preview (FR-030/031 not required for V1), but every V1 current-rating
  read goes through the derived ratings: shared readers by adapted call sites, V1-only rankings by
  migration (R18, FR-028f). History displays are untouched.

### R17 — Performance
- **Decision**: index `(user_id, course_id)` on the new table. Derived reads aggregate at most a
  few hundred rows per student. Verify with `scripts/measure_capacity.py` before/after: the
  26 CPU-ms/request baseline must not regress by more than 10 %.

### R18 — Rating reader inventory, classified by **caller**, not by origin (FR-028, FR-028a)

Classification rule (owner, 2026-10-06): the V1 freeze covers `src/interface/streamlit/` and code
used **only** by it. Anything reachable from `api/` — directly or through a shared service — is V2
or shared and **must** follow the new rating model.

Two kinds of reads are distinguished:
- **Rating reconstruction** — derives a current rating from rows (forbidden from `attempts`,
  Principle II).
- **Log display** — shows past `attempts.elo_after` values as history; allowed, it is what a log is
  for. After this spec those values are per course-topic.

| Reader | What it computes today | V1 callers | V2 callers | Class | Action |
|---|---|---|---|---|---|
| `get_latest_elo_by_topic` | current rows of old table | `student_view.py:73, 1839`; `teacher_view.py:656` | `api/dependencies.py:180` (`build_vector_rating` → next-question, answer, stats, exam submit, `/ai/socratic` `ai.py:76`, teacher ai-analysis `teacher.py:310`); `teacher_service.py:113` (`generate_ai_analysis` ← `teacher.py:313`, V1 `teacher_view.py:960`); `get_student_elo_summary` | **shared** | replace by `get_course_topic_ratings` + `ratings_view`; adapt V1 call sites |
| `get_student_elo_summary` | mean of old rows, 1000 fallback | `student_view.py:1816, 1945`; via `get_student_dashboard` ← `teacher_view.py:712` | `teacher_service.get_student_dashboard` ← `teacher.py:272` | **shared** | through `ratings_view` |
| `get_teacher_dashboard_stats` | `AVG(student_topic_elo)` else `users.current_elo` | via `get_dashboard_data` ← `teacher_view.py:592, 607` | `teacher.py:78` | **shared** | overall per FR-028a + `rank_label` |
| `aggregate_global_elo` (domain) | plain mean of vector | `student_view.py:1787, 1935` | stats `student.py:247`; exam submit snapshot `student.py:924`; `ai.py:77`; `teacher.py:311` | **shared** | replaced by `overall_rating` |
| `get_topic_elo_map` | old rows by label | — | `/student/map` `student.py:1392` | V2 | course-scoped topic ratings |
| `get_user_by_id().current_elo` | stored average | — | PvP lobby `pvp.py:190-191` | V2 | course rating (R8) |
| **`get_group_ranking`** | **`AVG(attempts.elo_after)` over all history** — reconstruction; and the `course_id` filter does not filter (LEFT JOIN on items only) | — | `/student/group-ranking` `student.py:410`; `/teacher/student/{id}/ranking` `teacher.py:335` | **V2 — non-compliant** | rank via `ranking_view(scope="group")` on the group basis of FR-028d (requested → group course → overall; R19) |
| `get_diagnostic().initial_elo` as course seed | stored course average | — | `api/dependencies.py:202` | V2 | removed (FR-004) |
| exam `global_elo_after` snapshot | written from `aggregate_global_elo` | — | written `student.py:924`, read `/exam/history` `student.py:946` | V2 | snapshot written from `ratings_view` overall (`null` when pending) |
| `get_latest_attempts` | per-attempt `elo_after` | — | `/student/history` `student.py:383`; `/teacher/student/{id}/elo-history` `teacher.py:279` | V2 — log display | keep; label as history; no current rating derived from it |
| `get_student_attempts_detail` | per-attempt `elo_after` | via `teacher_service` (V1 views) | via `teacher_service` ← `teacher.py:272, 313` | shared — log display | keep |
| `export_teacher_student_data` | per-attempt `elo_after` | `teacher_view.py:1003` | `/teacher/export/csv` `teacher.py:349`, `/xlsx` `teacher.py:384` | shared — log display | keep; add current course rating column from `ratings_view` |
| `get_answer_by_request_id` | stored attempt | — | `/student/answer` replay `student.py:197, 220` | V2 — log | keep |
| `get_global_ranking` | latest `elo_after` per topic from attempts — reconstruction | `student_view.py:610`; `teacher_view.py:465` | — | **V1-only** | migrate: participation = activity in last 7 days (kept); rating = overall (FR-028f) |
| `get_course_ranking` | same, per course | `student_view.py:729`; `teacher_view.py:495` | — | **V1-only** | migrate: participation = activity in that course in last 7 days (kept); rating = course rating (FR-028f) |
| `get_weekly_ranking` | same, group + week | `teacher_view.py:528` | — | **V1-only** | migrate: participation = ≥ 1 attempt this week in the group (kept); rating = the group basis of FR-028d; `attempts_this_week` stays a participation metric (FR-028f) |
| `save_weekly_ranking`, `get_ranking_history` | snapshot table `weekly_rankings` | `teacher_view.py:550, 556` | — | V1-only — history | keep: snapshots are history (FR-028g); new snapshots take their values from the migrated `get_weekly_ranking` |
| `get_student_rank` | from attempts | `student_view.py:538, 634, 757` | — | **V1-only** | migrate: same rating and participation rule as the list it positions in (FR-028f) |
| `get_user_history_full` | attempts history | `student_view.py:1769` | — | V1-only — log display | none |
| `get_user_history_elo` | attempts history | — | — | **dead** | delete (VII) |
| Rank tables | 16 levels (`student.py:1497`); 7 (`Teacher/Dashboard.tsx:20`, `Groups.tsx:14`); 8 (`Home.tsx:36`); V1 `state.py:31` | `state.py:31` | the other four | V2 + V1 | V2 → `domain/elo/ranks.py`; V1 keeps its own (frozen screen) |

**Result**: every current-rating reader — V2, shared and V1-only — moves onto `ratings_view` /
`get_course_topic_ratings` in this spec (owner decision 2026-10-06, option B). History readers
(per-attempt logs and weekly snapshots) stay as history. The newly found non-compliant V2 reader is
`get_group_ranking` (attempt replay plus a course filter that does not filter, in both engines).
No constitutional deviation remains.

Ranking implementation (superseded by R19 for details): `get_ranking_participants` returns who
appears (SQL filter + attempt count); `get_course_topic_ratings_bulk` returns raw rows;
`RatingReadService.ranking_view` derives the rating on the list's single basis and orders it with
`rank_competition`. The old repository ranking methods are deleted, so aggregation and ordering exist
once — not once per engine.

### R19 — Ranking basis, ties and authorization (FR-028d, FR-028f, FR-028h)

- **Basis precedence** (owner decision, option A): explicitly requested course (must exist → else
  400; must be visible to the requester → else 403: a student must be enrolled; the teacher
  endpoint takes no course) → the group's course (`groups.course_id`, nullable) → overall rating.
  One basis per list, applied to every participant, returned as `basis` and shown in the UI.
- **No substitution**: a participant without a rating on the basis is `pending_diagnostic` and
  listed last; their overall or another course's rating is never used instead.
- **Competition ranking** (FR-028h, owner decision 2026-10-06, supersedes the first tie rule):
  compare ratings rounded to `RANKING_DISPLAY_DECIMALS`, the precision every ranking surface
  displays; equal rounded ratings share a rank, the next distinct one skips (1, 2, 2, 4). Attempt
  count is not a tie-breaker. User id orders display within a tie only — stable and identical in
  both engines (database order is not). Pending participants come last with no numeric rank.
- **Why compare at display precision**: comparing finer than what is shown would give two students
  who both read "1200" different ranks. The API therefore returns ranking ratings already rounded,
  and clients do not re-round.
- **Precision = whole numbers** (owner, 2026-10-06): matches every screen today; one answer moves a
  rating by up to ~16 points, so decimals carry no information.
- **Rounding rule** (FR-028i): `round_for_ranking` = half up on the decimal representation
  (`Decimal(repr(x)).quantize(Decimal(1), ROUND_HALF_UP)`). Python's built-in `round` is
  half-to-even (`round(1200.5) == 1200`, `round(2.5) == 2`) and would disagree with the UI's old
  `Math.round`; `repr` avoids binary artefacts. Ratings are ≥ 0, so half up = half away from zero.
- **Round once, at the end**: storage, updates and the topic → course → overall averages stay full
  precision. Rounding earlier changes results: topics 1200.4, 1200.4, 1201.4 → course 1201 (late)
  vs 1200 (early).
- **A student's rank** = the `rank` of their entry in the unlimited list; `limit` only shortens the
  displayed list, so a top-N cut through a tie keeps the shared rank.
- **Weekly snapshots**: `save_weekly_ranking(group_id, rows)` stores the rows `ranking_view`
  produced; stored snapshots are never recomputed (FR-028g).
