# PvP leagues — as-is survey (spec 007 input)

Read-only survey of `redesign @ 1d6fcf6`, 2026-10-11. Input for `specs/007-pvp/spec.md` (roadmap
M7: lobby, match lifecycle, single-process constraint). PvP is new in the redesign: production
`main` has none. Under the roadmap's lean scope, spec 007 is written the first time a feature
touches the area. Some findings below are fixed in their own PRs. The rest wait for that spec or
for an owner decision.

Each finding cites code at that commit:

| Abbreviation | File |
|---|---|
| `W` | `api/websocket/pvp.py` |
| `P` | `src/infrastructure/persistence/postgres_repository.py` |
| `S` | `src/infrastructure/persistence/sqlite_repository.py` |
| `M` | `src/domain/elo/model.py` |
| `H` | `frontend/src/hooks/usePvpMatch.ts` |
| `L` | `frontend/src/pages/Student/League.tsx` |

How each finding was checked:
- **Verified**: read in the code.
- **Reproduced**: run against the app on a local uvicorn server (SQLite, or a local PostgreSQL
  16), or in a unit test with fake sockets.
- **Inferred**: reasoned from the code, not run.

Nothing here was run against production. Abuse cases are described only as far as a decision needs
them. The rating effect of a match (K = 24, floor 0, `no_rated_topics`, idempotent close) belongs
to spec 001 (FR-025 to FR-029c, AGENTS R19). Enrolment and roles belong to spec 004.

## 1. Where things live

| Concern | File |
|---|---|
| Endpoint, lobby, match, timer | `W` (route `/api/ws/pvp/{course_id}`, mounted at `api/main.py:116`). State: `_lobby`, `_matches`, `_lock` (W:70-72) |
| Rating formula | `pvp_deltas` M:88-91, `K_PVP = 24` M:9 |
| Storage | Tables P:1161-1203, S:868-912. Methods: `create_pvp_match` P:3976 S:3379 · `save_pvp_answer` P:3992 S:3393 · `finish_pvp_match` P:4004 S:3403 · `expire_stale_pvp_matches` P:4060 S:3459 · `get_pvp_history` P:4087 S:3484 |
| History API | `GET /api/student/pvp/history` (`api/routers/student.py:311-314`) |
| Screens | `H`, `L`; route `/student/league` (`frontend/src/App.tsx:205-208`) |
| Single process | `settings.validate_runtime()` (`api/config.py:95-102`, AGENTS R18); `render.yaml` sets `WEB_CONCURRENCY=1` |

## 2. Actual behaviour

**Joining.**
- The socket is accepted, then the token must arrive in the first message within 10 s.
- The user must be an active student enrolled in the course.
- Any failure closes the socket with 4001.
- The course rating is read in a thread, outside `_lock` (R17). An unrated player is expected at
  1000 but shown as pending (FR-029a).

**Matching.**
- There is one waiting slot per course, first come first served, with no rating window
  (W:217-230).
- A waiting socket that is no longer connected is skipped.
- A second join by the same student replaces their own slot.
- Nothing stops a student from waiting or playing in several courses at once.
- A player who waits 300 s is disconnected with no message.

**Starting a match.** The second player's connection creates the match:
- It loads the course bank and samples 10 items (fewer if the course has fewer). Both players get
  the same items in the same order. Difficulty is not considered.
- Items are sent with id, statement, options, topic and difficulty. There is no `correct_option`
  (V2-R9) and no image.
- It records a `pvp_matches` row with status `active`.
- Both players get `game_start`, with the opponent's username and shown rating.
- A single 180 s timer runs in the creator's coroutine.

**Answering.**
- Each answer is judged on the server against the item's key and stored in `pvp_answers`.
- The sender gets `answer_result`; the opponent gets `opponent_update`.
- Each item counts once per player.
- The match ends when both players have answered every item, or at 180 s.

**Closing.**
- The higher score wins; equal scores are a draw.
- `pvp_deltas` computes the deltas from the two expectation ratings.
- `finish_pvp_match` applies them in one transaction to every rated topic of the course, with a
  floor of 0 (R19). It is idempotent through `AND status='active'`.
- A player with no rated topic gets 0, with `no_rated_topics`.
- `game_end` reports the applied delta and its reason, or 0 with `not_applied` if persisting
  failed.

**Disconnects.**
- A player who drops during a match is not replaced, and the opponent is not told.
- The match runs to 180 s; the absent player is scored on what they had answered.
- There is no reconnect. Reconnecting joins the lobby as a new player.

**Orphans.**
- A match left `active` by a restart is closed as `abandoned`, with no rating change, by
  `expire_stale_pvp_matches(600)`.
- This runs only at schema bootstrap: once per deploy, in `scripts/migrate.py`.

**History.**
- The API returns the caller's last 20 finished matches across courses, without `elo_reason`.
- The screen shows the last 5.

**Screens.**
- States are idle → connecting → waiting → playing → finished. There is no error state: any close
  before `finished` returns to idle with no message (H:119-127).
- The countdown is client-side and for display only.

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| V1 | **Integrity** | **An answer could score for an item outside the match.** The key was looked up without checking that the item belonged to the match. A crafted message could add points and count toward finishing. | W:349-358, 383 | **Reproduced** (both engines, real uvicorn). Fixed in #46 |
| V2 | **Integrity** | **Answers counted after the match ended,** whether by the timer or by `game_end`. They were stored and sent to the opponent, so `pvp_answers` disagreed with the final score. | W:341-390 | **Reproduced**. Fixed in #46 |
| V3 | **Bug** | **Timer race.** If both players finished just as the timer was closing the match, the timer was cancelled mid-close. Neither player got `game_end`, the match stayed in memory, and the rating change still committed. Separately, whoever closed second returned at once, so its socket could close before `game_end` arrived. | W:109-112, 158-163, 386-389 | **Reproduced** (unit test, fake sockets). Fixed in #46 |
| V4 | **Bug** | **A course with no items started a 0-item match.** This also happened when the bank failed to load. The screen showed «Cargando preguntas…» for 180 s, and the 0-0 draw still moved ratings when the expectations differed. | W:233-241; L:212-214; M:88-91 | **Reproduced**. Fixed in #46 (close 4404, no match recorded) |
| V5 | **Fair play** | **Nothing limits repeated matches between the same two accounts.** Matching is a single first-come slot with no rating window, no repeat-opponent limit and no daily cap, and a match can end in seconds. With V6, two cooperating accounts can keep moving one account's rating. Registration and catalogue enrolment are self-service, and teachers cannot see PvP. | W:217-230, 386-390; P:4046 S:3445 | Inferred. Decision 1 |
| V6 | **Rating (spec 001)** | **A match is not zero-sum.** An unrated player is expected at 1000 but gets 0 applied (`no_rated_topics`). The floor at 0 clamps a topic without changing the reported delta, so R19's "the course rating moves by exactly the delta" fails near 0. | P:4040-4046 S:3439-3445; W:94-98 | Verified. Decision 2 |
| V7 | **Load** | **No limits on the socket.** Sockets are accepted before authentication (up to 10 s). There is no cap per user or address. Frames can reach the server default (16 MiB), and item ids have no length limit. Before #46, every answer message was a database insert against a pool of 5. #46 bounds stored answers to the match's items, but messages are still parsed without limit. | W:172-176, 341-365; P:206-208 | Inferred. Decision 3 |
| V8 | **Exclusivity** | **A student can be in several queues or matches at once.** They can wait or play in several courses together. A second tab in the same course silently replaces the first, which then waits 300 s for nothing. | W:223-230 | Verified. Decision 4 |
| V9 | **Disconnects** | **A dropped player cannot come back.** There is no reconnect or resume, and the opponent is not told. The dropped player's screen goes back to the lobby and can join a second match while the first runs on. A waiting player who leaves while the match is being created is still matched, and loses at 180 s. | W:226, 234-255, 392-396; H:119-127 | Inferred (the window during creation). Decision 5 |
| V10 | **Bug** | Any message from the client while waiting is treated as a disconnect. Today's client sends none. | W:287, 308-317 | Verified |
| V11 | **Persistence** | **A failed close is not retried.** If `finish_pvp_match` fails, the row stays `active` until the next deploy's bootstrap. "Already closed" and "failed" both reach the players as `not_applied`. Errors are logged without a traceback. | W:125-139; P:265 S:58; `render.yaml:23` | Verified |
| V12 | **Lifecycle** | After `game_end`, a player whose answer did not end the match keeps an open socket, and the match stays referenced, until their client closes. A malformed frame ends that player's loop silently, without closing the socket. | W:390, 397-398 | Verified |
| V13 | **Content** | **Match items lose their image.** 41 EPA8 items would show without their figure. (#45 serves those figures elsewhere; the PvP payload still omits `image_url`.) | W:244-249 | Verified. Decision 7 |
| V14 | **Screens** | **The league screen hides reasons and mis-colours feedback.** `elo_reason` is never shown, so a +0 has no explanation. Close codes are ignored. The first answer is coloured with the previous answer's correctness, so it is red on the first item. Feedback lands after the index has moved on. The countdown at 0 does not stop answers. `JSON.parse` is unguarded. History shows raw decimals, a bare «+» for a delta not applied, and no course; it uses index keys and is not refreshed after a match. | L:51-56, 145-148, 181-193, 224-252; H:83, 119-127 | Verified |
| V15 | **Drift** | **The two engines' PvP storage differs.** PostgreSQL has no foreign keys on the PvP tables; SQLite does. Neither has a `UNIQUE (match_id, user_id, item_id)` on answers or a `CHECK` on status. History's `finished_at` format differs. Some SQLite PvP methods have no `try/finally`. The PvP repository tests run on SQLite only. | P:1164-1192; S:885-899; P:4118 S:3518; `tests/integration/test_pvp_repository.py:16-19` | Verified |
| V16 | **Privacy** | **Strangers see each other.** Any enrolled student of a course is shown the opponent's username and rounded course rating. That reaches across schools and groups, and can include minors. | W:329-336 | Verified. Decision 6 |
| V17 | **Guard** | R18's check reads only `WEB_CONCURRENCY`; starting uvicorn with `--workers N` would bypass it. | `api/config.py:95-102` | Verified (low) |
| V18 | **Traceability** | **FR-026's test exercises unused code.** `_lobby_rating` is not used by the endpoint, which calls `_course_rating`. The test cited for spec 001 FR-026 exercises `_lobby_rating`. | W:101-104, 203; `tests/unit/application/test_spec001_service.py:138-168` | Verified |

## 4. Existing evidence

- **Domain:**
  - `tests/unit/domain/test_spec001_domain.py` and `test_spec001_engine_pins.py`: `pvp_deltas`
    values.
- **Match logic:**
  - `tests/unit/infrastructure/test_pvp_logic.py`: winner and delta signs; `game_end` from each
    player's side; draws; the double-close guard; the applied delta and reason; `not_applied`
    when persisting fails.
  - New in #46: the second close waits; finishing early leaves a closing timer alone; answer
    judging.
- **Lobby rating:**
  - `tests/unit/application/test_spec001_service.py`: `_lobby_rating`, `_slot_ratings` (see V18).
- **Storage:**
  - `tests/integration/test_spec001_course_topic_store.py` (both engines): the delta reaches every
    rated topic once; `no_rated_topics`.
  - `tests/integration/test_spec001_repository_pins.py`: practice after PvP starts from the
    post-match rating.
  - `tests/integration/test_pvp_repository.py` (SQLite only): lifecycle, history, floor, apply
    once, expiry at 600 s.
- **Endpoint:**
  - `tests/integration/test_pvp_enrolment.py` (both engines, real uvicorn): an enrolled student
    waits and leaves cleanly; a full match to `game_end`; 4001 for a student not enrolled.
  - `tests/api/test_websocket_authorization.py`.
  - New in #46: `tests/integration/test_pvp_answer_integrity.py`.
- **History API:** `tests/api/test_pvp.py` (200 and 401).
- **Not covered:**
  - the 180 s timer end to end;
  - disconnects while waiting or during a match;
  - two tabs, or one student in two courses;
  - teacher and refresh tokens on the socket;
  - a malformed first message;
  - the 300 s wait;
  - the 4500 path;
  - the PostgreSQL branch of expiry, history and the floor;
  - the screens (no hook, page or e2e test);
  - limits.

## 5. Decisions for the owner (input for `/speckit-clarify`)

None blocks the transfer (PR #3).

1. **Fair play (V5).** Which limits apply to rated matches?
   - a rating window between players;
   - a cap on rated matches against the same opponent per day;
   - a daily cap on rated matches;
   - a minimum time or number of answers before a result counts.
2. **Unrated players and the floor (V6).** Choose one, as a spec 001 amendment:
   - keep today's rule;
   - rate a match only when both players have a rated topic in the course;
   - keep PvP closed until the course diagnostic is done.
3. **Socket limits (V7).** Set limits on sockets per student, joins per minute, frame size and
   messages per second.
4. **One queue at a time (V8).** Should a student be limited to one queue or match at a time,
   across all courses? Should a second tab take over or be refused?
5. **Disconnects (V9).**
   - Should a player who drops forfeit after a set number of seconds?
   - Should the opponent be told?
   - Should a reconnect within the match resume it?
6. **Who can meet whom (V16).** Any enrolled student of the course, or only students of the same
   group or institution? Show the username, or an alias?
7. **Items in a match (V13).** Include images, or leave items with images out of PvP? Choose items
   by the players' ratings, or at random from the whole course as today?
8. **Teacher view.** Should teachers see their students' PvP matches?

## 6. Proposed scope for spec 007 (draft)

- **In:**
  - the lobby and matching;
  - the match lifecycle: items, answering, timer, close, disconnects, orphans;
  - the socket protocol and its limits;
  - the single-process constraint (R18);
  - the league screen and history.
- **Out:**
  - rating arithmetic and the PvP rating writer (spec 001; V6's rule is an amendment there);
  - enrolment and roles (spec 004);
  - item content and images (spec 008).
