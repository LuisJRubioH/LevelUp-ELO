# Plan — spec 007, delivery G: who may enter the League

**Spec**: [spec.md](spec.md) § Deliveries, G (US2; FR-020, FR-021, FR-022, FR-023, FR-024) ·
**Branch**: `007-g` (or `007-g1` / `007-g2` under O-G1 (a)), from `redesign` · **Date**: 2026-10-23
· **Status**: approved (owner, 2026-10-27: O-G1 … O-G11 as recommended; G split into G1 and G2)

## Summary

Today any active student enrolled in a subject may enter its League (survey 007 V6, V16, V21):
an unrated student is expected at 1000 and gets 0 applied (`no_rated_topics`), a test account can
move a real student's rating, and two students of different schools meet. Every refusal — a bad
token, a teacher, a student not enrolled, a database error — closes with the same 4001 «Auth
failed» (V24). Delivery L already refuses a second **live** League socket of a student, in any
subject, with 4409; but a student whose match socket dropped — away during F's 20 s grace, or gone
after answering every item (O-F4) — holds no live socket, so a new tab without the resume token
enters a lobby, in that subject or another, while the first match still runs (V8, measured on the
code below).

Delivery G refuses, at entry and before the queue, a student with no rating in the subject (and
the screen sends them to its diagnostic), a student already in a queue or a match, and — under
O-G5 — a student without an institution; it makes the lobby pair a test user only with a test user
and a student only with one of the same institution; and it gives every refusal its own close code
and message.

## Measured facts (redesign `e629a6c`; M at `origin/007-pvp-m` `2099432`)

| Fact | Evidence |
|---|---|
| Every refusal at entry is 4001 «Auth failed»: invalid or expired token, revoked session, pending password change, non-student role, not enrolled, and any database error while checking | `api/websocket/pvp.py` (`pvp_ws`, the `except Exception` after `authenticate_access_token` and `get_user_enrollments`); same on M's branch |
| Close codes in use on the League socket: 4001 (any refusal), 4003 (origin not allowed, spec 004 FR-085), 4404 (no items, A), 4409 (second live socket, L), 4410 / 4411 (F), 4429 (L), 4500 (database error creating the match). Spec 004 E3 (#73, unmerged) adds 4403 for an account whose access ended (`connections.EXPIRED_CODE`), at entry and by its sweep | `pvp.py`; `frontend/src/hooks/usePvpMatch.ts` `CLOSE_NOTICES`; `origin/004-identity-e3:api/websocket/pvp.py`, `api/websocket/expiry.py` |
| "Has a rating in the subject" is already one call: `RatingReadService.course_rating_of(user, course)` is `None` exactly when the student has no row in `student_course_topic_elo` for that course (any origin: diagnostic, practice, reconciled approximate baseline) | `src/application/services/rating_read_service.py:81-84` |
| The lobby already reads it at entry, outside `_lock`, and maps `None` (and, on M's branch, a **failed read**) to 1000 for the window and the expectation, never shown (O-M10) | `pvp.py` `_play` / `_slot_ratings`; plan-m O-M10 |
| `users.is_test_user` exists (INTEGER DEFAULT 0) but no repository read used by the socket returns it: `get_user_by_id` and `authenticate_access_token` do not | `postgres_repository.py:855, 2186-2206`; `api/dependencies.py:160-193` |
| **No institution exists anywhere today**: no column on `users` or `groups`, no table, no code | `grep -ri institution src api` → nothing; `groups` = `id, name, teacher_id, course_id, created_at, name_normalized` |
| Spec 009 I1's plan (PR #157, unmerged) puts the institution **on the group**: `groups.institution` (text) and `groups.grade`, both nullable, set when the admin creates a group per institution and grade; a student's institution is their **main group's** (`users.group_id`). Owner approved N26 (a) on 2026-10-23. I1 takes schema 8 or 9, after E3 (7). It sets the institution only on groups it creates: **existing groups keep NULL** and I1 has no way to set it on them | `origin/009-plan-i1-forms:specs/009-student-import/plan-i1.md` § Where the institution lives, § Merge order; spec 009 N26 |
| L's one-socket rule is per student across subjects (`_league_sockets[user_id]`), checked only while the old socket is `CONNECTED`. When a match socket ends, `pvp_ws`'s `finally` frees `_league_sockets` while the match stays in `_matches` (grace, or O-F4) | `pvp.py` `pvp_ws`; `tests/integration/test_pvp_limits.py::test_spec007_a_second_league_socket_is_refused` (already covers "another course too" for a live socket) |
| On M, the pairing is one function under `_lock`: `_pick_partner(slot, queue)` → `matchmaking.pick_opponent`, used both on entry and on each window step (`_pair_on_step`); `LobbySlot` has `user_id, name, elo, ws, shown_elo, course_id, resume, joined_at` | `origin/007-pvp-m:api/websocket/pvp.py` |
| Every PvP socket test today plays **unrated students with no group** (`make_student` + `enroll`); M's tests set a rating (`set_rating`) but no group | `tests/integration/conftest.py:79-85`; `test_pvp_enrolment.py`, `test_pvp_limits.py`, `test_spec007_f_match_flow.py`, `test_spec007_h_history.py`, `origin/007-pvp-m:tests/integration/test_spec007_m_fair_matches.py` |
| The screen has a per-course diagnostic entry at `/student/course/:courseId` (`CourseEntry.tsx`); `GET /api/student/courses` carries `diagnostic_done`, not the rating status | `frontend/src/App.tsx`; `frontend/src/api/student.ts` `Course` |
| Production runs `redesign` (PR #3), so the League and its 4001 are live | owner's context, AGENTS § Deploy |

## Constitution Check (1.2.0)

| Principle | G |
|---|---|
| The spec is the contract (I) | FR-020 … FR-024 and US2-AS1 … AS5 each get a test written first; every point the spec leaves open is an owner decision below (O-G1 … O-G11), not a choice of this plan |
| One source of truth (II) | "rated in the subject" is `RatingReadService.course_rating_of` (spec 001 FR-029a), never re-derived; the institution is spec 009's (`groups.institution` of the main group, N26 (a)); the refusal reason is the server's and the screen shows it by code, estimating nothing |
| Layers (III, R2) | the rules — who may enter, who may meet, how two institutions compare — are pure functions in a new `src/domain/pvp/admission.py`; the socket, the codes and the reads stay in `api/websocket/pvp.py`; the repository returns a raw row |
| Raw rows (R15) | the new read returns `is_test_user` and the main group's institution as stored; no rating is computed in a repository or the router |
| Dual database (IV, R1) | one new `@_read_only` method in both repositories, identical signature; `db_sync_check.py`; integration tests on both engines (`live_api`) |
| Schema (R8) | **no schema change in G.** G reads `groups.institution`, which spec 009 I1 adds (N26 (a)); `SCHEMA_VERSION` and `MIGRATION_SOURCES_DIGEST` are untouched by G |
| Integrity of measurement (V; R15, R19) | no unrated player reaches a rated match (SC-001); a test account never moves a real student's rating; nothing is rebuilt from attempts. `no_rated_topics` remains only for a rating that disappears between entry and close (spec 001 FR-029c as amended, § Dependencies) |
| Security and privacy (VI) | students of different institutions never see each other's name or rating (survey V16); refusal messages name the reason but never another student, a rating or an institution; the institution is never sent to the browser |
| Async (R17) | the entry reads (rating, profile) run in threads after the one-socket claim and outside `_lock`; the pairing predicate under `_lock` is pure; the busy check reads only in-memory dicts with no `await` between check and claim |
| Single process (R18) | the busy check reads `_lobby` / `_matches` in process memory, as L's rule does |
| Simplicity (VII) | no new dependency, table, column or setting; one domain module, one repository read, a handful of close codes |

## Design

### Order of the checks at entry

`pvp_ws` after this delivery (M's and F's code as merged; E3's 4403 if #73 is in):

1. origin → 4003 (spec 004, unchanged);
2. accept; first frame within 10 s, under L's limits (unchanged);
3. **token and account** → `authenticate_access_token`: an `HTTPException` 401/403 → **4001**
   (session); E3's `ACCESS_EXPIRED_MESSAGE` → **4403** (E3); any other exception → **4500**;
4. **role** ≠ student → **4002**;
5. **enrolment** → not enrolled → **4004**; a failed read → **4500**;
6. F's resume path (a valid `resume` takes its place back, 4410 for an ended match) —
   **unchanged, and G's checks 7–9 do not apply to it**: the place was admitted when it was taken
   (O-G3);
7. L's live-socket rule → **4409** (unchanged), and in the same synchronous step, with no `await`,
   **G's busy rule** (FR-023) → **4412**, then the claim of `_league_sockets`;
8. in threads, outside `_lock`: the course rating (the read the lobby already does) and the entry
   profile (`is_test_user`, institution). A failed read → **4500**, never "no rating" (O-G3);
9. `admission.entry_refusal(...)`: no rating → **4413** (FR-020); no institution, not a test user →
   **4414** (O-G5, FR-022);
10. the queue: M's `_pick_partner` with G's `may_meet` filter (FR-021, FR-022).

Steps 7–10 run inside the existing `try/finally` that frees `_league_sockets`, so a refused socket
never holds the student's place.

### FR-020 — a rating in the subject (US2-AS1)

- Rated means `course_rating_of(user, course) is not None` (O-G2). The lobby already makes this
  read at entry; G uses it to decide entry before the slot is built. M's fallback "a failed read is
  unrated → 1000" becomes "a failed read is 4500" (O-G3); the 1000 that `_slot_ratings` maps to
  remains only for M's re-read at formation, where a rating can in principle vanish (a spec 008 T
  merge between entry and formation) — the case spec 001 FR-029c keeps `no_rated_topics` for.
- Close **4413** «Para jugar esta materia en la Liga primero haz su diagnóstico.»; the screen shows
  that notice with a button «Hacer el diagnóstico» to `/student/course/{courseId}` (O-G9). The
  student is never queued: no slot, no `waiting`.
- Plan-m's O-M10 ("an unrated player is placed at 1000 until G keeps them out") is retired by this
  delivery: no unrated player reaches the window.

### FR-021 — test users only with test users (US2-AS2)

- `LobbySlot` gains `is_test_user: bool` and `institution: str | None` (the folded key, O-G6),
  filled from the entry profile.
- `admission.may_meet(a, b)`: `a.is_test_user == b.is_test_user` and, for two real students, the
  same institution key (FR-022); two test users meet whatever their institutions (O-G7).
- M's `_pick_partner` filters `others` through `may_meet` before `pick_opponent`. It is the only
  pairing point — on entry and on every window step (`_pair_on_step`) — so both paths obey it.
  Pure, under `_lock`, no I/O. A test user who finds no test user waits and times out at 300 s
  like anyone without a rival (`noRival` notice).

### FR-022 — the same institution (US2-AS3)

- The institution is the student's main group's `groups.institution` (spec 009 N26 (a)), read with
  `is_test_user` in one new raw read (§ Repositories), at entry, in a thread.
- Two institutions compare by a folded key (O-G6): inner spaces collapsed, ends trimmed, case and
  accents folded (ñ kept) — the rule spec 004 already uses to compare names
  (`src/domain/identity.py::_comparable`), exposed for reuse. An empty or missing institution has
  no key.
- A real student with no key — no main group, or a group without institution — is refused 4414
  (O-G5) rather than placed in a "no institution" bucket that would let strangers of different
  schools meet. This depends on spec 009 having set the institution of the groups the League's
  players belong to (§ Dependencies, § Production impact).
- The institution never reaches the browser; `game_start` is unchanged.

### FR-023 — one queue or match per student (US2-AS4)

- **Busy** means: the student has a slot in any course's queue, or is a player of a match still in
  `_matches` (running, away during the grace, or gone after answering every item, O-F4) (O-G8).
- At step 7, a new entry (no valid `resume`) of a busy student is closed **4412** «Ya tienes una
  búsqueda o una partida en curso en la Liga. Termínala o vuelve a esa pestaña.»; their slot or
  match is untouched (the grace keeps running, the opponent sees nothing).
- A live socket elsewhere keeps L's **4409** (US5-AS1 unchanged): 4409 means "another tab is open",
  4412 "a match of yours is still running without a tab". The tab that owns the match comes back
  through F's `resume`, which runs before both checks.
- Check and claim happen with no `await` between them, so two new sockets of one student cannot
  both pass.

### FR-024 — a code and a message per refusal (US2-AS5)

Recommended table (O-G4). The close reason (≤ 123 bytes) carries the Spanish sentence for logs and
tools; the screen shows `league.closeNotices.<key>` from i18n by code, as today.

| Code | Reason | Screen key → text (es) | Owner |
|---|---|---|---|
| 4001 | session: token invalid, expired or revoked; temporary password still pending | `sessionExpired` → «Tu sesión expiró. Vuelve a iniciar sesión.» | A, reworded |
| 4002 | the account is not a student | `notStudent` → «La Liga es solo para estudiantes.» | G |
| 4003 | origin not allowed | (no notice: not a browser of the app) | spec 004 |
| 4004 | not enrolled in the subject | `notEnrolled` → «No estás inscrito en esta materia.» | G |
| 4403 | the account's access ended | E3's notice | spec 004 E3 |
| 4404 | the subject has no items | `noItems` (unchanged) | A |
| 4409 | another League tab is open | `secondTab` (unchanged) | L |
| 4410 / 4411 | match over / resumed elsewhere | unchanged | F |
| 4412 | already queued or in a match | `busyElsewhere` → text above | G |
| 4413 | no rating in the subject | `noRating` → text above + «Hacer el diagnóstico» | G |
| 4414 | no institution recorded | `noInstitution` → «Tu cuenta aún no tiene institución registrada. Pídele a tu docente que la registre para jugar la Liga.» | G (O-G5) |
| 4429 | too many messages | unchanged | L |
| 4500 | server error (at entry or creating the match) | `serverError` (unchanged) | A, widened |

- 4001 keeps its number so F's "refresh the token once on 4001 during a reconnect" keeps working;
  its text no longer mentions enrolment. Its old catch-all text is retired.
- The two A pins that assert 4001 for a student **not enrolled** flip to 4004 explicitly (tasks
  T012), citing FR-024; spec 007 FR-001's "close any other socket with 4001" must be amended in
  the same PR (§ Spec changes).

### Domain: `src/domain/pvp/admission.py` (new)

Pure, no I/O, no clock:
- `institution_key(text) -> str | None` — the folded key, None when empty (O-G6);
- `entry_refusal(rated: bool, is_test_user: bool, institution_key: str | None) -> str | None` —
  `"no_rating"`, `"no_institution"` or None (O-G5, O-G7);
- `may_meet(a, b) -> bool` — over a `Protocol` with `is_test_user` and `institution` (FR-021,
  FR-022).

The code PR adds the file to spec 007's § Code Scope beside M's `matchmaking.py` and
`match_items.py` and F's `outcome.py`.

### Repositories (both, R1)

| Method | Change | Returns |
|---|---|---|
| `get_league_entry_profile(user_id)` | new, `@_read_only` | raw `{"is_test_user": int, "institution": str \| None}` — `users LEFT JOIN groups ON groups.id = users.group_id`; None when the user does not exist |

Under O-G1 (a), G1 ships the method returning `institution: None` (the column does not exist yet)
and G2 adds the join once I1's `groups.institution` exists. `python scripts/db_sync_check.py`;
`tests/integration/test_spec002_d2_connections.py` gains the method in its read-only list (as M
did for its two reads). `src/application/interfaces/repositories.py` is not touched: only
`api/websocket/pvp.py` calls it, like the other PvP methods.

### Frontend

- `usePvpMatch.ts`: `CLOSE_NOTICES` gains 4002 `notStudent`, 4004 `notEnrolled`, 4412
  `busyElsewhere`, 4413 `noRating`, 4414 `noInstitution`; 4001 maps to `sessionExpired`. None of
  them is a drop: no reconnect (F's `isDrop` already treats 4xxx as final).
- `League.tsx`: the 4413 notice carries a button to `/student/course/{courseId}` (D5/D1: copy in
  i18n, colours from tokens).
- i18n `es` and `en`: `league.closeNotices.{sessionExpired, notStudent, notEnrolled,
  busyElsewhere, noRating, noInstitution}`, `league.goToDiagnostic`; `authFailed` removed.

## Shared files the code PR will touch (warning for parallel sessions)

- `api/websocket/pvp.py` — `pvp_ws` entry, `_play`, `LobbySlot`, `_pick_partner` (**changed by M**,
  PR #152, and by **E3**, PR #73: the 4403 branch and `abandon_matches_of`).
- `src/infrastructure/persistence/sqlite_repository.py`, `postgres_repository.py` — one read
  (**also changed by M, S #155, E3 #73, I1 #157**).
- `src/domain/identity.py` — exposes the folding rule (spec 004's file).
- `src/domain/pvp/admission.py` — new.
- `frontend/src/hooks/usePvpMatch.ts`, `frontend/src/pages/Student/League.tsx`,
  `frontend/src/i18n/locales/es.ts`, `en.ts` (**M and E3 change all four**).
- `tests/integration/conftest.py` — a `league_player` helper; every PvP socket test's fixture
  (A, F, L, H, M, S, spec 004 E2 names) moves to it (§ Tests).
- `tests/integration/test_spec002_d2_connections.py` — the read-only list.
- `specs/007-pvp/spec.md` — § Traceability rows of G, FR-001's wording, § Code Scope, delivery G →
  `closed`; `specs/001-elo-engine/spec.md` — FR-029c amended (approved), FR-029a per O-G11.
- `AGENTS.md` — R19 ("1000 drives the expectation of an unrated player" no longer happens in the
  League) and R18 (the League's close codes next to 4409 / 4429).
- `docs/sdd/roadmap.md` — the M7 progress note only.
- **Not touched:** `render.yaml` (no setting, no start command change), `docs/transfer.md`, the
  schema (`schema_version.py`), any `ops/*` branch.

### Production impact (production runs `redesign`)

- **D1/D2/D6/V24 (no institution needed):** unrated students, and real-vs-test pairs, stop playing
  rated matches at once; refusal notices change. No migration, backup or rehearsal is needed: no
  schema, no setting. A browser holding the old SPA during the deploy shows the generic notice for
  the new codes (`closeNotice`'s fallback) until it reloads.
- **D3 (the institution):** under O-G5 (a), **every real student whose main group has no
  institution is refused 4414** — today, every student, because no group has one, and I1 sets it
  only on the groups it creates. Before the code that reads the institution reaches `main`, the
  groups of every League player need their institution set: a tool spec 009 does not plan today
  (an admin edit of a group's institution, or a `scripts/repairs/` script that counts by default
  and writes with `--apply`). That is the reason for O-G1's split.

## Tests (written first; each `[CHANGE]` test fails on today's code)

| Test | Proves | Where |
|---|---|---|
| `test_spec007_entry_refusal_reasons` | FR-020, FR-022 (O-G5, O-G7): unrated → `no_rating` first; real without key → `no_institution`; test user without key → None | `tests/unit/domain/test_spec007_g_admission.py` |
| `test_spec007_test_users_meet_only_test_users` | FR-021: real–test never; test–test always, across institutions (O-G7) | same file |
| `test_spec007_students_of_different_institutions_never_meet` | FR-022: real students meet only with equal keys | same file |
| `test_spec007_institutions_compare_folded` | O-G6: «Colegio  San José» = «colegio san jose»; «Piñas» ≠ «Pinas»; blank → None | same file |
| `test_spec007_a_student_without_rating_is_not_queued` | FR-020, US2-AS1: unrated enrolled student → 4413, no `waiting`, no slot left; a rated rival who then joins is not matched with them | `tests/integration/test_spec007_g_admission.py` (uvicorn, both engines) |
| `test_spec007_a_failed_rating_read_is_a_server_error` | FR-024 (O-G3): the rating read raises → 4500, not 4413 | same file |
| `test_spec007_a_test_user_and_a_real_student_never_meet` | FR-021, US2-AS2: a test user and a real student, same rating and institution, wait; a window step passes (`pvp_window_every_s` shortened) and they stay waiting; a second real student joins and meets the real one | same file |
| `test_spec007_two_test_users_meet` | FR-021 (O-G7): two test users of different institutions meet | same file |
| `test_spec007_students_of_two_institutions_never_meet` | FR-022, US2-AS3: two real students of different institutions, same rating, never meet (entry and a window step); a third of the first's institution meets the first | same file |
| `test_spec007_a_student_without_institution_is_refused` | FR-022 (O-G5): main group without institution → 4414; no group → 4414 | same file |
| `test_spec007_a_student_away_in_a_match_cannot_queue_elsewhere` | FR-023, US2-AS4: a player drops (grace running); a new socket without `resume`, same and other subject → 4412; the opponent sees no `opponent_back`; the grace ends in a forfeit as F says; afterwards the student queues normally | same file |
| `test_spec007_a_student_who_finished_and_left_cannot_queue_until_the_match_ends` | FR-023 (O-G8, O-F4) | same file |
| `test_spec007_each_refusal_has_its_own_code` | FR-024, US2-AS5: bad token 4001, teacher 4002, not enrolled 4004, enrolment read raising 4500 | same file |
| `test_spec007_league_entry_profile_returns_raw_fields` | the new read, both engines: `is_test_user` as stored; the main group's institution or None | `tests/integration/test_pvp_repository.py` |
| e2e «sin diagnóstico la Liga ofrece el diagnóstico (spec 007 US2-AS1)» | US2-AS1 on screen: close 4413 → notice + button to the course page | `frontend/e2e/league.spec.ts` |
| e2e «una partida en curso impide otra búsqueda y dice por qué (spec 007 US2-AS4)» | US2-AS4 on screen: 4412 notice | same file |
| e2e «cada rechazo muestra su motivo (spec 007 US2-AS5)» | US2-AS5 on screen: 4001, 4004, 4500 each show their own text | same file |

**Pins kept, and the fixture move.** Every PvP socket test of A, F, L, H, M and S, and spec 004 E2's
names test, plays students that G would refuse (no rating; no institution). Their fixtures move to
a `league_player(repo, course_id, *, elo=1000.0, institution=…, test_user=False)` helper (rated,
in a group with an institution, enrolled) **without changing any assertion**; under O-G1 (a), G1's
helper sets only the rating, G2 adds the group. If a pinned assertion depended on an unrated
player, the task flips it explicitly citing FR-020 — none was found (`no_rated_topics` is asserted
only by repository-level tests that call `finish_pvp_match` directly, which stay as they are).
The two A tests that assert 4001 for a student not enrolled flip to 4004 citing FR-024.

**Traceability rows to fill:** FR-020, FR-021, FR-022, FR-023, FR-024, US2-AS1 … US2-AS5 (delivery
G → closed), and FR-001's row keeps its tests with the flipped code.

## Spec changes the code PR carries (not made here)

- **Spec 007 FR-001** [AS-IS] says «close any other socket with 4001»; FR-024 contradicts it.
  Proposed: «…and close any other socket with the code of its reason (FR-024)».
- **Spec 001 FR-029c** — approved text (spec 007 § Dependencies): «A student with no rating in the
  subject does not enter the League (spec 007 FR-020); `no_rated_topics` remains only for a player
  whose rated topics disappear during a match».
- **Spec 001 FR-029a** still says the PvP expectation uses 1000 with no rated topic (O-G11).
- **Spec 007 § Deliveries / § Traceability** — only under O-G1 (a): G becomes G1 and G2, and the
  Delivery column of FR-022 and US2-AS3 says G2.
- **Spec 007 § Key Entities** «every student's institution and grade, owned by spec 009» — under
  N26 (a) they are the main group's; a student whose group has none has none (O-G5).
- **Spec 007 § Code Scope** gains `src/domain/pvp/admission.py`.

## Risks

- **Longer waits, more `noRival`.** Three filters now stack — window (M), test users, institution —
  in small institutions; more students reach 300 s alone. The numbers are M's settings; G adds
  none.
- **Locking out production** if the institution check ships before groups carry one (O-G1, O-G5).
- **Merge order on `pvp.py`** with M (#152) and E3 (#73): G is written on M's code; if E3 lands
  after G, E3 adds its 4403 branch to the table above; if before, G keeps it.
- **A rating that vanishes** between entry and formation (a spec 008 T merge run while students
  wait) still plays with `no_rated_topics`, as amended FR-029c says.

## Decisions (owner, 2026-10-27)

The owner approved the recommended option of each decision. The split of O-G1 is in spec 007
§ Deliveries (G1, G2) and its Traceability column, amended in this docs PR.

- **O-G1 — (a) split:** **G1** = FR-020, FR-021, FR-023, FR-024 (branch `007-g1`, after M's code
  is merged); **G2** = FR-022 (branch `007-g2`, after spec 009 I1's code is merged and the groups
  of League players carry their institution).
- **O-G2 — a rating in the subject** = `course_rating_of(user, course) is not None`, any origin.
- **O-G3 — at entry,** after authentication and enrolment, before the queue, a close with its own
  code; F's resume skips G's entry checks; a failed read is 4500, never 4413.
- **O-G4 — the codes** of § FR-024: 4001 kept for the session; new 4002, 4004, 4412, 4413, 4414;
  4500 widened to entry.
- **O-G5 — (a)** a real student without institution is refused with 4414 (G2). The tool that sets
  the institution of existing groups must exist before G2 ships: **a spec 009 amendment** — the
  admin edits a group's institution and grade from the admin panel (owner, 2026-10-27; not a
  one-off repair script, since the institution is data kept over time).
- **O-G6 — the folded key** (spaces, case, accents; ñ kept), spec 004's rule.
- **O-G7 — test users** meet only test users, need no institution, and still need a rating.
- **O-G8 — busy** = a queue slot or a match still in memory (running, away in the grace, or
  finished-and-left) → 4412.
- **O-G9 — on 4413,** the notice with a button to `/student/course/{courseId}`.
- **O-G10 — the rules** in `src/domain/pvp/admission.py` (pure), applied inside M's
  `_pick_partner`.
- **O-G11 — spec 001 FR-029a** is amended with FR-029c in G1's PR.
