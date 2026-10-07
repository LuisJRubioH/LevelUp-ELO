# Domain & Repository Contracts: ELO Engine (spec 001)

Internal interfaces the tests pin. Pure functions live in `src/domain/` (no I/O, R2).

## Domain — `src/domain/elo/`

| Function | Contract | FR |
|---|---|---|
| `expected_score(rating, difficulty) -> float` | `1 / (1 + 10^((difficulty − rating)/400))` (unchanged) | 001 |
| `rating_delta(rating, rd, difficulty, result) -> float` | `32 × (rd/350) × (result − expected_score)`; the only formula used by both the update and the preview | 002, 030 |
| `next_rd(rd) -> float` | `max(30, rd × 0.95)` | 003 |
| `item_difficulty_delta(rating, difficulty, result) -> float` | `32 × ((1 − result) − (1 − expected_score))` | 005 |
| `is_valid_response_time(seconds \| None) -> bool` | `None → 30 s`; valid iff `3 ≤ s ≤ 600` | 008, 009 |
| `procedure_elo_delta(grade) -> float` | `(grade − 50) × 0.2`; `ValueError` outside [0, 100] (unchanged) | 022, 023 |
| `pvp_deltas(rating_a, rating_b, outcome_a) -> (float, float)` | `K=24`, outcome 1 / 0.5 / 0 (moved from `api/websocket/pvp.py`) | 025 |
| `course_rating(topic_ratings: list[float]) -> float \| None` | arithmetic mean; `None` if empty | 029a |
| `overall_rating(course_ratings: list[float \| None]) -> float \| None` | mean of non-`None` values, equal weight; `None` if none | 028a, 028b |
| `rank_for(rating: float \| None) -> str \| None` | 16-level table, `None` → `None` | 031 |
| `RANKS: tuple[(min, label), ...]` | the single scale, served by `/meta/ranks` | 031 |
| `RANKING_DISPLAY_DECIMALS: int` | the one precision used both to compare ratings in rankings and to return them for display (value per FR-028h decision) | 028h |
| `rank_competition(entries) -> list[entry]` | entries `{user_id, rating: float \| None, …}`; rounds each rating to `RANKING_DISPLAY_DECIMALS` and returns it rounded; rated entries by rounded rating desc, then `user_id` asc **for display only**; `rank` = 1 + number of entries with a strictly higher rounded rating (1, 2, 2, 4); pending (`rating=None`) last by `user_id` asc with `rank=None`; other fields (e.g. `attempts_in_window`) are carried through and never used to order | 028d, 028f, 028h |
| `diagnostic_tier(difficulty) -> (win, loss)` | +14/−20 · +22/−12 · +34/−6 (moved from the router) | 020 |
| `diagnostic_baseline(answers) -> float` | `max(760, 1000 + Σ tier deltas)` | 020 |

Removed: `calculate_dynamic_k`, `update_elo`, `StudentELO`, `impact_modifier` parameter.
`VectorRating.update` keeps its signature minus `impact_modifier` and delegates to the functions above.

## Repository (both engines, identical signatures — R1)

| Method | Contract | FR |
|---|---|---|
Repositories select participants and return raw rows. They never average, order by, or otherwise
compute a rating (constitution III). The one permitted rating write pattern is adding a
domain-computed delta atomically inside a transaction (`current_elo = MAX(0, current_elo + :delta)`)
— persistence, not arithmetic (research R3).

| `save_answer_transaction(user_id, item_id, compute, request_id=None, request_fingerprint=None) -> bool` | lock users→items; read item `(course_id, topic, difficulty, rd)` and rating row `(user, course_id, topic)`; call `compute(state)`; persist attempt always; persist rating + item only if `attempt_data["elo_valid"]`; `False` on idempotent replay. **`topic` parameter removed.** | 007–010, 012, 029 |
| `get_course_topic_ratings(user_id, course_id=None) -> list[{course_id, topic, elo, rd, origin, approximate}]` | new-table rows only; never legacy | 028, 029 |
| `get_current_context_course_ids(user_id) -> list[str]` | enrollments ∩ catalogue for the user's level and grade (semillero by grade; colegio, universidad, concursos by level) | 028a |
| `get_course_topic_ratings_bulk(user_ids, course_id=None) -> list[{user_id, course_id, topic, elo, rd, origin, approximate}]` | raw rows for many students, one query | 028a, 028d, 028f |
| `get_current_context_course_ids_bulk(user_ids) -> {user_id: [course_id]}` | same rule as above, many students | 028a |
| `get_ranking_participants(scope, group_id=None, course_id=None, education_level=None, grade=None, window_days=7) -> list[{user_id, username, attempts_in_window}]` | **who appears**, per FR-028f table; `scope ∈ {"group","global","course","weekly"}`; for `"group"` `attempts_in_window = 0`; never returns a rating | 028d, 028f |
| `get_group_course_id(group_id) -> str \| None` | the group's course, if any | 028d |
| `save_weekly_ranking(group_id, rows)` | stores the rows computed by `ranking_view(scope="weekly")` as a snapshot | 028g |
| `get_teacher_dashboard_stats(teacher_id)` | per student: attempts, accuracy, last activity — **no rating** | 028a |
| `set_topic_rating_baseline(user_id, course_id, topic, elo, rd=350)` | diagnostic writer; replaces `set_topic_elo_baseline` | 020 |
| `has_practice_attempts(user_id, course_id, topic) -> bool` | attempts on items of that course and topic | 021 |
| `validate_procedure_submission(...)` | unchanged signature; bump on `(student, item.course_id, item.topic)` | 022–024 |
| `finish_pvp_match(...) -> {p1: (applied, reason), p2: (applied, reason)}` | returns applied deltas; bump every row of `(player, course)`; none → `(0, "no_rated_topics")`; idempotent | 025, 029b, 029c |
| `expire_stale_pvp_matches(max_age_seconds=600) -> int` | unchanged | 027 |
| `_reconcile_legacy_ratings() -> int` | bootstrap step; returns rows created; idempotent | 033–036, 034a, 034b |

Removed from the public API: `get_latest_elo_by_topic` (replaced by `get_course_topic_ratings`),
`get_topic_elo_map` (map reads `get_course_topic_ratings(user, course_id)`),
`set_topic_elo_baseline`, `_refresh_global_elo`, `_tiempo_valido`, `get_student_elo_summary`
(rating part → `ratings_view`), `get_group_ranking`, `get_global_ranking`, `get_course_ranking`,
`get_weekly_ranking`, `get_student_rank` (→ `get_ranking_participants` + `ranking_view`),
`get_user_history_elo` (dead).
`src/application/interfaces/repositories.py` and `tests/unit/application/test_repository_contracts.py`
are updated with the same list.

## Application

### `src/application/services/rating_read_service.py` — `RatingReadService(repository)`

The only place that turns stored rows into course ratings, overall ratings, ranks and rankings
(orchestration; the arithmetic is the domain functions above). V2 routers, `StudentService`,
`TeacherService` and V1 views call it.

| Method | Contract | FR |
|---|---|---|
| `ratings_view(user_id) -> {overall, overall_status, rank_label, courses: [{course_id, course_name, rating, rank_label, current_context, topics}]}` | `overall=None` ⇒ `overall_status="pending_diagnostic"`, `rank_label=None` | 028a–c, 029a, 031 |
| `ratings_view_bulk(user_ids) -> {user_id: ratings_view}` | same, one repository round-trip | 028a |
| `course_rating_of(user_id, course_id) -> float \| None` | selection / PvP expectation use `1000` when `None` (caller decides) | 029a, 026 |
| `group_basis(group_id, requested_course_id=None, requester=None) -> {kind: "course" \| "overall", course_id: str \| None, source: "requested" \| "group" \| "overall"}` | precedence of FR-028d; unknown course → `ValueError` (400); not visible to requester → `PermissionError` (403) | 028d |
| `ranking_view(scope, *, group_id=None, course_id=None, education_level=None, grade=None, limit=None, requester=None) -> {basis, entries: [{user_id, username, rating, rank_label, status: "rated" \| "pending_diagnostic", attempts_in_window, rank: int \| None}]}` | participants from `get_ranking_participants`; rating on the single basis; `rank_competition`; `rating` returned already rounded to `RANKING_DISPLAY_DECIMALS`; `limit` cuts the display list **after** ranking and never changes a `rank` | 028d, 028f, 028h |
| `ranking_rank(user_id, scope, **same_args) -> int \| None` | the `rank` of `user_id`'s entry in `ranking_view(scope, **same_args)` (unlimited list); `None` if pending or not a participant | 028f, 028h |

### `StudentService`

| Method | Contract |
|---|---|
| `process_answer(user_id, item_data, selected_option, reasoning, time_taken, request_id=None, request_fingerprint=None)` | `vector_rating` and `elo_topic` parameters removed; returns `(is_correct, result)` with `elo_before`, `elo_after`, `rd_after`, `elo_valid` |
| `get_next_question(student_id, course_id, topic_filter=None, session…)` | selection rating per FR-016–019 via `RatingReadService`; returns item + `preview` |
