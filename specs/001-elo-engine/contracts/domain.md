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
| `diagnostic_tier(difficulty) -> (win, loss)` | +14/−20 · +22/−12 · +34/−6 (moved from the router) | 020 |
| `diagnostic_baseline(answers) -> float` | `max(760, 1000 + Σ tier deltas)` | 020 |

Removed: `calculate_dynamic_k`, `update_elo`, `StudentELO`, `impact_modifier` parameter.
`VectorRating.update` keeps its signature minus `impact_modifier` and delegates to the functions above.

## Repository (both engines, identical signatures — R1)

| Method | Contract | FR |
|---|---|---|
| `save_answer_transaction(user_id, item_id, compute, request_id=None, request_fingerprint=None) -> bool` | lock users→items; read item `(course_id, topic, difficulty, rd)` and rating row `(user, course_id, topic)`; call `compute(state)`; persist attempt always; persist rating + item only if `attempt_data["elo_valid"]`; `False` on idempotent replay. **`topic` parameter removed.** | 007–010, 012, 029 |
| `get_course_topic_ratings(user_id, course_id=None) -> list[{course_id, topic, elo, rd, origin, approximate}]` | new-table rows only; never legacy | 028, 029 |
| `get_current_context_course_ids(user_id) -> list[str]` | enrollments ∩ catalogue for the user's level and grade | 028a |
| `set_topic_rating_baseline(user_id, course_id, topic, elo, rd=350)` | diagnostic writer; replaces `set_topic_elo_baseline` | 020 |
| `has_practice_attempts(user_id, course_id, topic) -> bool` | attempts on items of that course and topic | 021 |
| `validate_procedure_submission(...)` | unchanged signature; bump on `(student, item.course_id, item.topic)` | 022–024 |
| `finish_pvp_match(...) -> {p1: (applied, reason), p2: (applied, reason)}` | returns applied deltas; bump every row of `(player, course)`; none → `(0, "no_rated_topics")`; idempotent | 025, 029b, 029c |
| `expire_stale_pvp_matches(max_age_seconds=600) -> int` | unchanged | 027 |
| `_reconcile_legacy_ratings() -> int` | bootstrap step; returns rows created; idempotent | 033–036, 034a, 034b |

Removed from the public API: `get_latest_elo_by_topic` (replaced by `get_course_topic_ratings`),
`get_topic_elo_map` (map reads `get_course_topic_ratings(user, course_id)`),
`set_topic_elo_baseline`, `_refresh_global_elo`, `_tiempo_valido`.
`src/application/interfaces/repositories.py` and `tests/unit/application/test_repository_contracts.py`
are updated with the same list.

## Application — `StudentService`

| Method | Contract |
|---|---|
| `process_answer(user_id, item_data, selected_option, reasoning, time_taken, request_id=None, request_fingerprint=None)` | `vector_rating` and `elo_topic` parameters removed; returns `(is_correct, result)` with `elo_before`, `elo_after`, `rd_after`, `elo_valid` |
| `get_next_question(student_id, course_id, topic_filter=None, session…)` | selection rating per FR-016–019; returns item + `preview` |
| `ratings_view(user_id) -> {overall, overall_status, rank_label, courses: [...]}` | the single reader for every overall/course rating in `api/` |
