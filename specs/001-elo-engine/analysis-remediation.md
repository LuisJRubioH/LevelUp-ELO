# Spec 001 — Remediation proposal for the `/speckit-analyze` findings

Status: **applied** (2026-10-06). Approved by the owner after expert review, with Option A for
groups and these refinements: basis precedence requested (validated, authorized) → group course →
overall, shown in the response/UI, no substitution for unrated participants; one explicit tie rule
with positions taken from the same ordered list; architecture guards supplementary to behavioural
tests. Second `/speckit-analyze` run: 0 CRITICAL; follow-ups I6, G1, L1 applied. Kept as the record
of what changed and why.

Order of application if approved: C1 → T1 → I1 → the rest. C1 and T1 rewrite the same tasks.

---

## C1 — CRITICAL — rating arithmetic would land in repositories and routers

**Finding.** Constitution III: "no rating arithmetic in `infrastructure/` or in routers". T062 puts
the V1 ranking aggregation inside both repositories; T061 orders the group ranking "in the
application layer" without naming a use case while routers call the repository directly; T060
reroutes `get_teacher_dashboard_stats` / `get_student_elo_summary`, which average inside the
repository today.

**Proposal.** Split every ranking and summary into *participation* (SQL filter, infrastructure) and
*rating* (domain aggregation, called from one application service).

1. **New application module** `src/application/services/rating_read_service.py`:

   | Function | Contract |
   |---|---|
   | `ratings_view(user_id)` | moved here from `StudentService` (same contract) |
   | `ratings_view_bulk(user_ids)` | same, for many students in one repository round-trip |
   | `ranking_view(scope, *, group_id=None, course_id=None, education_level=None, grade=None, limit=None)` | `scope ∈ {"group","global","course","weekly"}`; returns `[{user_id, username, rating, rank_label, status, position, attempts_in_window}]` ordered by derived rating, `status="pending_diagnostic"` rows last |
   | `ranking_position(user_id, scope, **same_args)` | the user's `position` in exactly the list `ranking_view` returns for the same arguments, or `None` if not a participant |

   `StudentService` and `TeacherService` delegate to it; V2 routers and V1 views call it.

2. **Repository contract** (both engines, contracts/domain.md) — replace the ranking/summary
   methods' rating columns with plain data:

   | Method | Returns | Arithmetic? |
   |---|---|---|
   | `get_ranking_participants(scope, group_id=None, course_id=None, education_level=None, grade=None, window_days=7)` | `[{user_id, username, attempts_in_window}]` — who appears | none (filter + count) |
   | `get_course_topic_ratings_bulk(user_ids, course_id=None)` | raw `(user_id, course_id, topic, elo, rd, origin, approximate)` rows | none |
   | `get_current_context_course_ids_bulk(user_ids)` | `{user_id: [course_id, …]}` | none |
   | `get_teacher_dashboard_stats(teacher_id)` | unchanged **minus** `global_elo` (attempts, accuracy, last activity stay) | none on ratings |

   Removed from repositories: `get_student_elo_summary` (its rating part moves to
   `ratings_view`; its attempt counts become a plain query if still needed),
   `get_group_ranking`, `get_global_ranking`, `get_course_ranking`, `get_weekly_ranking`,
   `get_student_rank` as rating producers. `save_weekly_ranking(group_id, rows)` keeps storing
   snapshots, but receives the rows computed by `ranking_view(scope="weekly")`.

3. **Accepted persistence pattern (records finding U5).** Adding a delta that the domain already
   computed (`current_elo = MAX(0, current_elo + :delta)`) inside a write transaction is
   persistence, not arithmetic — it is what keeps procedure and PvP effects atomic and
   exactly-once (AGENTS R15/R19). Note this explicitly in research R3 so C1's rule is not
   over-applied.

4. **Guard test.** `tests/unit/test_architecture_layers.py::test_spec001_no_rating_aggregation_in_repositories_or_routers`
   — fails if a repository or router file contains `AVG(` over `current_elo`/`elo_after`, or
   imports `src.domain.elo.aggregation`/`ranks`. Cheap, and stops the drift from coming back.

5. **Task edits.**
   - New `[CHANGE]` test task (US6, before T060): `tests/unit/application/test_spec001_rating_read_service.py` —
     `ranking_view` per scope with a fake repository; `ranking_position` equals the index in the
     list for the same arguments; pending rows last. Must FAIL.
   - **T060** → "Create `rating_read_service.py` (`ratings_view`, `ratings_view_bulk`); route
     stats, map, exam snapshot, `/ai/socratic`, teacher dashboard and student report through it;
     remove `global_elo` from `get_teacher_dashboard_stats` and delete `get_student_elo_summary`'s
     rating computation; adapt the V1 call sites of each reader removed (see T1)".
   - **T061** → "Add `get_ranking_participants` and `get_course_topic_ratings_bulk` to both
     repositories (participation for scope `group` honours `course_id`: only attempts on items
     of that course); implement `ranking_view`/`ranking_position`; `/student/group-ranking` and
     `/teacher/student/{id}/ranking` call `ranking_view(scope="group", …)`".
   - **T062** → "V1 rankings: `student_view.py` and `teacher_view.py` call `ranking_view` /
     `ranking_position` for global, course and weekly; `save_weekly_ranking` stores rows from
     `ranking_view(scope="weekly")`; delete the old repository ranking methods; history
     (`get_ranking_history`) untouched".
   - Research R18 "Ranking implementation note" and contracts/domain.md updated to match.

**Cost.** About +0.5 session. It also removes the need to write each ranking twice (SQLite and
PostgreSQL) — aggregation exists once.

---

## T1 — MEDIUM — V1 stays broken from Phase 3 until Phase 10

**Proposal.** Keep V1 working at every step instead of repairing it at the end.

- Move the **smoke** half of T065 into Phase 2 as an `[AS-IS]` pin (it passes today):
  `tests/unit/interface/test_spec001_v1_smoke.py` — V1 modules import, `StudentService` and
  `TeacherService` construct exactly as `src/interface/streamlit/app.py` does. Every later
  checkpoint runs it.
- Move the **regression** half of T065 into US1 as a `[CHANGE]` test written before T035/T036:
  `tests/unit/interface/test_spec001_v1_compat.py` — V1's answer call path lands on the item's
  `(course_id, topic)`.
- Fold T066 into the tasks that break V1: T036 adapts `student_view.py:385-393`; T060 adapts
  `student_view.py:73, 1787, 1816, 1839, 1935, 1945` and `teacher_view.py:656, 960`; T062 adapts
  the ranking views. Delete T066; Phase 10 disappears.
- Dependencies section: "every task that changes a shared signature or deletes a shared reader
  adapts its V1 call sites in the same task; the V1 smoke pin stays green at every checkpoint".

---

## I1 — HIGH — SC-001 asks for both databases on scenarios that never touch one

**Proposal.** Replace SC-001 with:

> **SC-001**: For 100 % of the acceptance scenarios above, an automated check reproduces the
> stated numbers. Every scenario whose outcome depends on stored data runs against both supported
> databases with identical results; scenarios that exercise only domain rules or response shapes
> run once.

Optional, **not** in this spec: a CI job running `tests/api/` against PostgreSQL (roadmap
candidate next to A-1/A-2).

---

## A1 — MEDIUM — FR-028f says "e.g." for the participation rule — **DECISION**

Verified in code: global and course rankings use a 7-day activity window; the global ranking also
filters by level/grade when given; the weekly ranking uses the group's 7-day activity.

**Proposed text** (replaces the "keeping each ranking's participation rule separate …" sentence):

| Ranking | Who appears (participation) | Ranked by |
|---|---|---|
| Global | students (of the requested level and grade, when given) with ≥ 1 attempt in the last 7 days | overall rating (FR-028a) |
| Course | students with ≥ 1 attempt on that course's items in the last 7 days | that course's rating (FR-029a) |
| Weekly (group) | students of the group with ≥ 1 attempt in the last 7 days | **see decision** |
| Group (V2, FR-028d) | students of the group | **see decision** |
| Student position | same rule and value as the list it refers to | — |

**DECISION — what ranks a group?** A group may be tied to a course (`groups.course_id` is
nullable). Options:

| Option | Rule |
|---|---|
| A (recommended) | If the group has a course, rank by that course's rating; otherwise by overall rating. An explicit `course_id` in the request still wins. |
| B | Always overall rating unless `course_id` is passed (today's FR-028d wording). |

Recommendation A: a group created for "Álgebra Básica" should rank its members on Álgebra Básica,
not on unrelated courses they also take. If chosen, FR-028d gets the same rule.

---

## I2 — MEDIUM — edge case contradicts FR-029a

Replace "Course with no rated topics → its derived rating is 1000." with:

> Course with no rated topics → selection and PvP expectation use 1000; every display shows
> "pending diagnostic" (FR-029a).

## I3 — MEDIUM — SC-005 vs V1

Replace "on every screen that shows them" with "on every V2 screen that shows them (V1 keeps its
own labels — research R16)".

## I4 — MEDIUM — quickstart §1 misses reused pins

Replace the quickstart §1 command with T020's selection, so both run the same set:

```bash
pytest tests/ --ignore=tests/e2e -q -k "spec001 or elo_single_source or pvp_repository or item_selector or elo_model or student_service or procedure_grading"
```

(Alternative: register a `spec001` pytest marker and mark the reused tests — more edits, same
result.)

## U1 — MEDIUM — T063 has no file for `/meta/ranks`

T063: "new `api/routers/meta.py` with `GET /meta/ranks`, registered in `api/main.py` under
`/api`, no authentication, using the existing rate limiter like other public routes".

## U2 — MEDIUM — PvP lobby read inside `async def`

- T049 adds: "the lobby rating is read with `await asyncio.to_thread(...)`, never while holding
  `_lock` (AGENTS R17)".
- T048 adds an assertion: a fake repository records `pvp._lock.locked()` at call time; it must be
  `False`.

## U3 — MEDIUM — current context only tested for semillero

T028 adds: a colegio student (`grade = None`) enrolled in a colegio course and a universidad
course → only the colegio course is current; same check for universidad and concursos.

## U4 — MEDIUM — T052 says "rankings" without naming them

T052: replace "rankings" with "`ranking_view` for scopes group (with and without course),
global, course and weekly, and `ranking_position`" (depends on C1).

## D1 — LOW — FR-028 and FR-028e overlap

FR-028 becomes: "The system shall hold each rating in exactly one place and derive every
aggregate from stored ratings (history rule: FR-028e)." The "never by replaying attempts" clause
lives only in FR-028e.

## A2 — LOW — T048 offers two files

T048 uses `tests/unit/application/test_spec001_service.py` (the lock assertion from U2 needs a
fake repository, which unit tests already have).

## I5 — LOW — "no field removed" vs `impact_modifier`

contracts/api.md compatibility rule: "No field is removed or renamed, except the always-1.0
`impact_modifier` key inside the free-form `cog_data` dict."

## U5 — LOW — atomic delta in SQL

Covered by C1 point 3.

---

## Net effect if all are approved

- Tasks: T065/T066 dissolved into earlier tasks; +2 test tasks (rating read service, guard test);
  T060–T062 rewritten. Roughly 74 tasks.
- Spec: SC-001, SC-005, FR-028, FR-028d (if decision A), FR-028f, one edge case.
- Plan/contracts/research: `rating_read_service.py`, repository contract for participants and
  bulk rows, accepted persistence pattern.
- Calendar: +0.5 session inside M1 (deadline 2026-10-22 unchanged).
- After applying: re-run `/speckit-analyze`; expected 0 CRITICAL, then the docs PR.

---

## Adjustment after approval (2026-10-06) — competition ranking

Owner decision replacing the first FR-028h tie rule: equal ratings share a competition rank
(1, 2, 2, 4); ratings are compared at the precision the UI displays; attempt count is never a
tie-breaker; user id only orders display within a tie; pending-diagnostic students come last with
no numeric rank. Applied to spec (FR-028d, FR-028f, FR-028h, US6-AS8, edge cases), contracts
(`rank_competition`, `RANKING_DISPLAY_DECIMALS`, `ranking_rank`, API `rank`), research R19, plan
and tasks T022, T024, T031, T055, T056, T061, T065, T067.

Open: the display precision itself — the UI shows ratings as whole numbers today while the API
returns 2 decimals (see spec § Clarifications).
