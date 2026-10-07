# API Contract Changes: ELO Engine (spec 001)

Base path `/api`. Only fields that change are listed; everything else in each payload is unchanged.
Compatibility rule: no field is removed or renamed in this spec — existing clients keep working;
new clients use the new fields. One exception: the always-1.0 `impact_modifier` key inside the
free-form `cog_data` dict of `/student/answer`. `[FR]` = requirement served.

## `POST /student/next-question` — `NextQuestionResponse`

| Field | Change | Type | Meaning |
|---|---|---|---|
| `preview` | **new** | `{on_correct: float, on_wrong: float} \| null` | change the engine will apply to the item's topic rating for each outcome, computed by the same domain function as the update; `null` when no item [FR-030] |

Selection uses the topic rating when `topic` is sent, otherwise the derived course rating
[FR-016–019, FR-029a].

## `POST /student/answer` — `AnswerRequest` / `AnswerResponse`

| Field | Change | Meaning |
|---|---|---|
| request `elo_topic` | **deprecated, ignored** | still accepted (no 400 for old clients); the rating key is always the item's course and topic [FR-029] |
| response `elo_before`, `elo_after`, `rd_after` | semantics | values of the item's **topic rating in its course** [FR-029] |
| response `delta_elo` | semantics | `0` and `elo_after == elo_before` when the response time is outside 3–600 s [FR-009] |
| response `elo_valid` | **new** `bool` | whether this attempt moved any rating [FR-008, FR-009] |
| response `cog_data.impact_modifier` | **removed key** inside a free-form dict | dead value, always 1.0 [R15] |

Unchanged: `Idempotency-Key` replay (200, stored result) and conflict (409) [FR-012, FR-013];
400 for an option not in the item [FR-011]; no `correct_option` [FR-014].

## `GET /student/stats` — `StudentStatsResponse`

| Field | Change | Type | Meaning |
|---|---|---|---|
| `global_elo` | type widened | `float \| null` | overall rating per FR-028a; `null` when pending [FR-028b] |
| `overall_status` | **new** | `"rated" \| "pending_diagnostic"` | [FR-028b] |
| `rank_label` | semantics | `str \| null` | from the single rank scale; `null` when pending [FR-031] |
| `course_ratings` | **new** | `list[{course_id, course_name, rating: float \| null, rank_label, current_context: bool, topics: list[TopicELO]}]` | per-course view; `current_context=false` = earlier level/grade, shown as history [FR-028c] |
| `topic_elos` | semantics | `list[TopicELO]` | topics of current-context courses only; the old cross-course dedupe hack is removed |

No field anywhere reports a difference between two overall ratings [FR-028c].

## `GET /student/map/{course_id}`
Node states read the student's topic ratings **for that course** [FR-029]. Thresholds unchanged
(spec 003).

## `POST /student/diagnostic/{course_id}/submit`
Baselines written per `(course_id, topic)` [FR-020, FR-021, FR-029]. Response unchanged; the
league label stays a placement [FR-031a].

## `GET /teacher/dashboard` — `StudentSummary` · `GET /teacher/student/{id}` — `StudentReportResponse`

| Field | Change | Type | Meaning |
|---|---|---|---|
| `global_elo` | type widened | `float \| null` | same derivation as the student's overall rating [FR-028a] |
| `rank_label` | **new** | `str \| null` | single scale [FR-031]; the frontend stops computing ranks |
| `overall_status` | **new** | `"rated" \| "pending_diagnostic"` | [FR-028b] |

## `GET /student/group-ranking?course_id=` · `GET /teacher/student/{id}/ranking`

| Field | Change | Type | Meaning |
|---|---|---|---|
| `basis` | **new** | `{kind: "course" \| "overall", course_id: str \| null, course_name: str \| null, source: "requested" \| "group" \| "overall"}` | the single basis used for every participant [FR-028d] |
| `ranking[]` | semantics | `{user_id, username, rating: float \| null, rank_label: str \| null, status: "rated" \| "pending_diagnostic", position}` | ordered per FR-028h; pending last; `global_elo`/`rank_pos` kept as aliases of `rating`/`position` for old clients |
| `my_rank` | semantics | `int \| null` | equals that student's `position` in `ranking` [FR-028h] |

Errors: `course_id` that does not exist → **400**; a student requesting a course they are not
enrolled in → **403**. The teacher endpoint takes no `course_id` (basis = group course, else
overall); the existing group-ownership check stays.

## `GET /meta/ranks` — **new, public** (`api/routers/meta.py`)
`200 → [{label: str, min: float}]` ordered ascending; the 16-level scale. Used by the home page
[FR-031]. No authentication; rate-limited like other public routes; cacheable.

## WebSocket `/ws/pvp/...` — `game_end` message

| Field | Change | Meaning |
|---|---|---|
| `elo_delta` | semantics | the **applied** delta (0 when not applied) [FR-029c] |
| `elo_reason` | **new** `string \| null` | `"no_rated_topics"` when the delta was not applied [FR-029c] |

If persisting the match fails, `elo_delta` is `0` and `elo_reason` is `"not_applied"` — the message
never reports a change that was not stored.
