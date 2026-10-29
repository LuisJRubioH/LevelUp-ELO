# Feature Specification: PvP League

**Feature Branch**: `007-pvp` (one branch per delivery once implementation starts)

**Created**: 2026-10-20

**Status**: Draft for the owner's approval. Written from the as-is survey
(`docs/sdd/pvp-survey.md`, LuisJRubioH/LevelUp-ELO#47), re-verified on 2026-10-19 (its § 7), and
the owner's decisions of 2026-10-20 (its § 8, D1 … D11). Delivery A pins what already holds,
including the fixes delivered in #46, #106, #107, #112, #115, #119 and #120.

**Input**: Roadmap M7 (`docs/sdd/roadmap.md`): the 1-vs-1 League — fair, bounded and honest about
what it did to a rating.

**Outcome served** (constitution VIII): two students of the same institution who both have a
rating in a subject play a short race of items near their level; the result moves their course
rating once, by an amount the server computed and shows as it computed it; nobody can farm
rating, flood the server or lose a match because a tab slept.

## Code Scope *(mandatory)*

- `api/websocket/pvp.py` — lobby, match, close, the orphan sweep
- `api/main.py` — starts and stops the orphan sweep (shared)
- `api/routers/student.py` — `/api/student/pvp/history` (shared with specs 001, 003, 005, 006)
- `src/application/services/rating_read_service.py` — the history's shown delta (shared with spec
  001)
- `src/infrastructure/persistence/sqlite_repository.py`,
  `src/infrastructure/persistence/postgres_repository.py` — PvP storage: create, answers, close,
  history, orphan expiry (shared)
- `frontend/src/pages/Student/League.tsx`, `frontend/src/pages/Student/League.css`
- `frontend/src/hooks/usePvpMatch.ts`
- `src/domain/pvp/outcome.py` — the winner rule: score, then total answer time (delivery F,
  O-F9)
- `src/domain/pvp/matchmaking.py` — the rating window, the opponent, the pair's day and its cap
  (delivery M, FR-030, FR-031)
- `src/domain/pvp/match_items.py` — the match's items: near the mean, unseen for a week (delivery
  M, FR-032)
- `src/domain/pvp/admission.py` — who may enter (a rating in the subject; for a real student, an
  institution) and who may meet whom (test users only with test users, real students only of one
  institution) (deliveries G1 and G2, FR-020 … FR-022)
- `src/domain/pvp/answer_stats.py` — the League's answers counted per topic and per item for
  study (delivery S)
- `src/application/services/study_report_service.py` — the League report and the «Liga» sheet
  (delivery S; shared with spec 008 T)
- `api/routers/teacher.py` — `/api/teacher/student/{id}/league` and the «Liga» sheet of the
  workbook (delivery S; shared with spec 006)
- `frontend/src/components/Study/LeagueReport.tsx`, `frontend/src/pages/Student/Stats.tsx`,
  `frontend/src/pages/Teacher/Dashboard.tsx`, `frontend/src/pages/Teacher/Export.tsx` — the
  League's answers on the student's statistics, the teacher's student panel and the export
  (delivery S; shared with specs 001, 006 and 008)

## Deliveries *(this spec is delivered in steps)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it closed and fills all its rows.

| Delivery | Content | State |
|---|---|---|
| **A** | As-is pins: who may play, what an answer and a close may do, the waiting player, a malformed frame, the rating effect, the shown delta, the orphan sweep — each tied to a test that exists today | closed |
| **G1** | Who may enter, part 1: a rating in the subject (D1), test users only with test users (D2), one queue or match per student (D6), a distinct reason for every refusal (V24) | closed |
| **G2** | Who may enter, part 2: the same institution (D3), after spec 009 I1 and once the groups of League players carry their institution (owner, 2026-10-27, O-G1) | closed |
| **M** | Fair matches: a rating window that widens while waiting and a daily cap per pair (D5); items near both ratings, unseen for a week, with images, without their difficulty (D7); the expectation read when the match is formed (V24) | closed |
| **F** | The match flow: the server's clock and a speed tiebreak (D8); a 20 s grace to come back, then a forfeit (D4) | closed |
| **L** | Socket and process limits: one live socket per student, a frame size and a message rate (D9); one worker in production by any route (V17) | closed |
| **H** | History: every match with its outcome reason and subject, as many as the screen shows (D10); a close that fails is retried, then recorded as not saved (V11) | closed |
| **S** | Statistics: the League's answers feed the student's and the teacher's statistics (V23) | closed |

## Clarifications

### Session 2026-10-20 (owner decisions, survey § 8)

- Q: Unrated player (V6)? → A: cannot enter the League for that subject; the screen asks for the
  subject's diagnostic first (D1).
- Q: Test users (V21)? → A: they play only each other (D2).
- Q: Who meets whom (V16)? → A: the same institution only (D3).
- Q: Disconnects (V9)? → A: a 20 s grace to come back and resume, then a forfeit (D4).
- Q: Fair matching (V5)? → A: a rating window (±150, widening while waiting) and at most 3 rated
  matches per day against the same opponent (D5).
- Q: One queue (V8)? → A: one lobby slot or match per student across all subjects; a second tab is
  refused with a notice (D6).
- Q: Items (V13, V19)? → A: near both ratings, none seen in the last week, images included, no
  difficulty sent to the browser (D7).
- Q: The clock (V20)? → A: the client counts down to the server's end time; equal scores are broken
  by speed (D8).
- Q: Socket limits (V7)? → A: one live socket per student, frames up to 4 KB, at most 5 messages
  per second (D9).
- Q: History (V25)? → A: every match — finished, abandoned, not saved — with its reason and
  subject, and only as many as shown (D10).
- Q: Orphans (V22)? → A: a periodic sweep; nothing is closed at shutdown (D11, delivered in #119).

### Session 2026-10-20, second round (owner decisions on the draft)

- Q: The institution (O1)? → A: a first-class concept, designed now: the owner will run olympiads in
  which students first classify within their institution and the final keeps one student per
  grade per institution. Every student has an institution and a grade (owned by spec 009, owner
  decision N21 «por institución y grado»), and the League's «same institution» reads the
  student's institution. No interim boundary (the main group's teacher is not used).
- Q: The numbers (O2)? → A: ±150, the widening step, 3 per day, 20 s, 4 KB and 5 per second are
  accepted as starting values; the plans may tune them with the owner.
- Q: Speed tiebreak (O3)? → A: on equal correct answers, the lower total time between
  `game_start` and each counted answer wins; a draw remains only on equal time to the second.
- Q: Spec 001 amendment for D1? → A: approved; it ships with delivery G1 (see § Dependencies).
- Q: A close that fails to persist (V11)? → A: retried 3 times within a few seconds, then the match
  is closed as abandoned with reason `not_saved`, visible in the history.
- Q: More than one worker (V17)? → A: in production the API refuses to start with more than one
  worker by any route (`--workers`, `WEB_CONCURRENCY`); the deployment is documented as one
  instance.
- Q: `pvp_answers` (V23)? → A: it feeds the student's and the teacher's statistics (which items
  are missed in the League); the score stays in memory.
- Q: Refusals and the expectation (V24)? → A: each refusal gets its own close code and message
  (session expired, not enrolled, no access, server error…), and the expectation rating is read
  again when the match is formed, not at lobby entry.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - What already holds keeps holding (Priority: P1) — A

**Why this priority**: the integrity of answers, the close, the waiting player and the rating
effect were fixed in the last weeks; they stay fixed while the rest changes.

**Independent Test**: the existing integration, API, unit and browser tests named in
§ Traceability, on both engines.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** two enrolled students, **When** they meet in the lobby and answer,
   **Then** each answer gets its own verdict, the waiting player's first answer included, and both
   receive `game_end`.
2. **US1-AS2** — **Given** a match, **When** a player sends an item outside the match, an answer
   after the end, or a frame that is not JSON, **Then** nothing scores and the player's match goes
   on.
3. **US1-AS3** — **Given** a finished match, **When** it closes — twice at once, or while one
   player's answer is being saved — **Then** each player's delta reaches every rated topic of the
   course exactly once, floor 0, and the screen shows the server's rounded number.
4. **US1-AS4** — **Given** a match left active by a restart, **When** more than 600 s have passed,
   **Then** the sweep or the next start closes it as abandoned without moving any rating, and a
   live match is never touched.

### User Story 2 - Only fair opponents can meet (Priority: P1) — G1, G2

**Why this priority**: today an unrated account, a test account or a stranger from another school
can move a real student's rating, and one student can play in several subjects at once.

**Independent Test**: students with and without a rating, test and real, of two institutions,
connect to the lobby.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** a student with no rating in the subject, **When** they open the League
   for it, **Then** they are not queued and the screen offers the subject's diagnostic.
2. **US2-AS2** — **Given** a test user and a real student waiting in the same subject, **When**
   the lobby matches, **Then** they never meet each other.
3. **US2-AS3** — **Given** two students of different institutions in the same subject, **When**
   the lobby matches, **Then** they never meet.
4. **US2-AS4** — **Given** a student already waiting or playing in any subject, **When** a second
   tab connects, **Then** it is refused with a notice and the first stays as it was.
5. **US2-AS5** — **Given** a connection refused for an expired session, for not being enrolled or
   for a server error, **When** the screen receives the close, **Then** each shows its own reason.

### User Story 3 - Matches are even (Priority: P2) — M

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** two waiting students 400 points apart and a third 100 points from the
   first, **When** the lobby matches, **Then** the close pair meets; a lone student is matched
   wider the longer they wait.
2. **US3-AS2** — **Given** two students who already played 3 rated matches today, **When** they
   meet again, **Then** the match is not rated and both are told before it starts.
3. **US3-AS3** — **Given** a match, **When** it starts, **Then** its items are near the mean of the
   two ratings, none was seen by either player in the last week, each carries its image, and no
   item's difficulty reaches the browser.

### User Story 4 - The match is decided on the server (Priority: P2) — F

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** a match, **When** a tab sleeps in the background, **Then** its countdown
   still ends at the server's end time, and the server decides the end.
2. **US4-AS2** — **Given** equal correct answers, **When** the match ends, **Then** the faster
   player wins.
3. **US4-AS3** — **Given** a player whose connection drops, **When** they come back within 20 s,
   **Then** they resume the same match; otherwise they lose by abandonment and the opponent wins
   at once, told why.

### User Story 5 - The server cannot be flooded (Priority: P3) — L

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** a student with a live League socket, **When** a second socket of theirs
   opens, **Then** it is refused.
2. **US5-AS2** — **Given** a socket, **When** it sends a frame over 4 KB or more than 5 messages in
   a second, **Then** the excess is not processed and a persisting abuse closes the socket.

### User Story 6 - The history tells what happened (Priority: P3) — H

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** a finished, an abandoned and an unsaved match, **When** the student
   opens the history, **Then** all three appear with their subject and reason, and only as many
   rows as the screen shows are sent.
2. **US6-AS2** — **Given** a match whose result cannot be saved, **When** the retries fail,
   **Then** it is closed as abandoned with reason `not_saved`, no rating changes, and it appears
   in both players' history with that reason.

### User Story 7 - The League's answers count for study (Priority: P3) — S

**Why this priority**: every League answer is written and never read; it is evidence of what a
student misses, lost to the student and the teacher.

**Independent Test**: a student plays a match and misses an item; their statistics and their
teacher's view count that miss.

**Acceptance Scenarios**:

1. **US7-AS1** — **Given** a finished match, **When** the student or their teacher opens the
   statistics, **Then** the League's answers are counted per item and topic, marked as League
   answers.

### Edge Cases

- **A player rated in the subject whose topics are all floored at 0** still enters (they have a
  rating); the floor rule of spec 001 applies to the delta.
- **Equal time to the second** with equal scores is a draw (O3).
- **A player who comes back after the grace** finds the match lost; they may queue again.
- **The daily cap** counts rated matches; a match played over the cap is played but not rated.
- **A restart during a match** still ends as abandoned with no rating change (A); the grace (F)
  cannot outlive the process (AGENTS.md R18).

## Requirements *(mandatory)*

### Functional Requirements

**What already holds (A)**

- **FR-001** [AS-IS]: The system shall admit to a subject's League only an authenticated student
  enrolled in it, and close any other socket with the code of its reason (FR-024). *(Amended
  2026-10-27 with delivery G1: it said «with 4001».)*
- **FR-002** [AS-IS]: When two enrolled students meet in the lobby, the system shall start one
  match with the same items for both and end it with `game_end` for each.
- **FR-003** [AS-IS]: The system shall score an answer only for an item of the match, once, while
  the match runs.
- **FR-004** [AS-IS]: If a subject has no items, then the system shall close the socket with 4404
  and record no match.
- **FR-005** [AS-IS]: While a player waits, the system shall keep them queued whatever they send,
  and shall judge an answer sent right after `game_start` even if the waiting coroutine resumes
  late.
- **FR-006** [AS-IS]: If a frame is not JSON, then the system shall ignore it and keep the player's
  match running.
- **FR-007** [AS-IS]: When a match closes, the system shall add each player's applied delta to
  every rated topic of the course, floor 0, exactly once even if the close runs twice or an answer
  is saved at the same time (AGENTS.md R19; spec 001 FR-029b).
- **FR-008** [AS-IS]: The system shall compute the expectation from each player's course rating,
  read outside the lobby lock, and show the opponent a pending rating, never the internal 1000.
- **FR-009** [AS-IS]: The system shall name the opponent by their display name, in the match and
  in the history (spec 004 FR-021).
- **FR-010** [AS-IS]: The system shall close as abandoned, without changing any rating, every match
  active for more than 600 s — at start and, while the API runs, every 5 minutes — and shall close
  no match at shutdown.
- **FR-011** [AS-IS]: The system shall send, with each applied delta, the number to show — half up
  on the value (spec 001 FR-028j) — in `game_end` and in the history; the screen shall render it as
  given, explain a delta not applied, colour each answer with that answer's verdict, and keep its
  copy in `i18n` and its colours in tokens.
- **FR-012** [AS-IS]: The system shall list a student's finished matches from their own side: their
  score, the opponent's, the result and their delta.

**Who may enter (G1; FR-022: G2)**

- **FR-020** [CHANGE]: If a student has no rating in the subject, then the system shall not queue
  them, and the screen shall send them to the subject's diagnostic (D1).
- **FR-021** [CHANGE]: The system shall match a test user only with a test user (D2).
- **FR-022** [CHANGE]: The system shall match only students of the same institution, read from the
  student's institution as recorded by spec 009 (D3, O1).
- **FR-023** [CHANGE]: While a student is waiting or playing in any subject, the system shall refuse
  another League socket of theirs with a notice and leave the first unchanged (D6).
- **FR-024** [CHANGE]: When the system refuses a League connection, it shall close it with a code
  and message that name the reason — session expired, not enrolled, no access to the subject,
  server error — instead of one code for every refusal (V24).

**Fair matches (M)**

- **FR-030** [CHANGE]: The system shall match two students only within a rating window of ±150 of
  their course ratings, widened by a fixed step for every period waited (D5, O2).
- **FR-031** [CHANGE]: When two students have played 3 rated matches today against each other, the
  system shall play their next matches that day without rating and tell both before the start
  (D5, O2).
- **FR-032** [CHANGE]: The system shall choose a match's items near the mean of the two ratings,
  none seen by either player in the last 7 days when enough remain, each with its image, and shall
  send no item difficulty to the browser (D7).
- **FR-033** [CHANGE]: When a match is formed, the system shall read both players' course ratings
  again for the expectation, not reuse the ratings read when they entered the lobby (V24).

**The match flow (F)**

- **FR-040** [CHANGE]: The system shall send the match's end time with `game_start`, the screen
  shall count down to it, and the server alone shall decide the end (D8).
- **FR-041** [CHANGE]: When the correct answers are equal, the system shall declare the player with
  the lower total answer time the winner (D8, O3).
- **FR-042** [CHANGE]: If a player's socket drops, then the system shall keep their place for 20 s
  and resume the match if they reconnect; otherwise it shall end the match as their loss by
  abandonment and tell the opponent at once (D4, O2).

**Socket limits (L)**

- **FR-050** [CHANGE]: The system shall keep at most one live League socket per student (D9).
- **FR-051** [CHANGE]: The system shall not process a frame over 4 KB nor more than 5 messages per
  second from a socket, and shall close a socket that persists (D9, O2).
- **FR-052** [CHANGE]: If the API is started in production with more than one worker by any route
  (`--workers`, `WEB_CONCURRENCY`), then it shall refuse to start (V17; AGENTS.md R18).

**History (H)**

- **FR-060** [CHANGE]: The system shall list a student's matches whatever their outcome — finished,
  abandoned, not saved — each with its subject and reason, and send only as many as the screen
  shows (D10).
- **FR-061** [CHANGE]: If persisting a finished match fails, then the system shall retry it 3 times
  within a few seconds and, if it still fails, close the match as abandoned with reason
  `not_saved`, changing no rating (V11).

**Statistics (S)**

- **FR-070** [CHANGE]: The system shall count the League's answers (`pvp_answers`) in the student's
  and the teacher's statistics per item and topic, marked as League answers; the match score keeps
  being computed in memory (V23).

### Key Entities

- **Lobby slot**: a student waiting in one subject; at most one per student (G1).
- **Match**: two players, a subject, items, a server end time, scores and answer times; its close
  applies each player's delta once.
- **Pair count**: rated matches per pair of students per day (M).
- **Institution and grade**: every student's institution and grade, owned by spec 009; the League
  reads the institution (G2), and a future olympiad reads both. A student's institution is their
  main group's (`users.group_id` → `groups.institution`, spec 009 N26 (a)); a student without a
  main group, or whose group records none, has none (O-G5).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 rated matches with an unrated player, a test user against a real student, or two
  institutions.
- **SC-002**: 0 pairs with more than 3 rated matches in a day.
- **SC-003**: 0 matches decided by the browser's clock; 0 deltas rounded in the browser.
- **SC-004**: 0 matches left active more than 15 minutes while the API runs.

## Assumptions

- The rating formulas (`pvp_deltas`, the floor, the display rounding) belong to spec 001.
- The backend stays a single process (AGENTS.md R18): the lobby, the grace (F) and the limits (L)
  live in memory.

## Dependencies

- **Spec 001 amendment (approved by the owner, 2026-10-20).** Today an unrated player may play, is
  expected at 1000 and gets 0 applied with `no_rated_topics` (spec 001 FR-029c; AGENTS.md R19).
  FR-020 keeps unrated players out of the League. The pull request of delivery G1 amends
  spec 001 FR-029c to say: «A student with no rating in the subject does not enter the League (spec 007
  FR-020); `no_rated_topics` remains only for a player whose rated topics disappear during a
  match». This spec does not edit spec 001 on its own.
- **Institution and grade (spec 009, owner decision N21).** Every student has an institution and a
  grade, stable over a season. They must exist before delivery G2 ships; FR-022 has no fallback.
- **Olympiads (future spec, roadmap).** Students classify first within their institution and the
  final keeps one per grade per institution. That feature is not part of this spec, but its needs —
  institution and grade per student, stable over a season — constrain FR-022 and the data it reads.

## Out of Scope *(mandatory)*

- The rating formulas and their display rule — spec 001.
- Enrolment, roles, display names and the name filter — spec 004.
- The item bank's contents and difficulty calibration — spec 008.
- The olympiad itself (phases by institution and grade, finalists) — a separate future spec.
- Creating institutions and assigning students to them — spec 009.
- Running more than one backend process (AGENTS.md R18).
- A teacher view of the League's matches (results, opponents). The League's answers reach the
  teacher as study evidence through FR-070 (owner, 2026-10-21, plan-s O-S1).

## Traceability *(mandatory)*

Rows of delivery A cite tests that exist today; the rest are filled by the pull request that
closes their delivery.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | A | `tests/integration/test_pvp_enrolment.py::test_pvp_matches_and_finishes_a_game_between_enrolled_students`<br>`tests/integration/test_pvp_waiting_player.py::test_the_waiting_players_first_answer_is_never_lost` |
| US1-AS2 | A | `tests/integration/test_pvp_answer_integrity.py::test_an_answer_outside_the_match_scores_nothing`<br>`tests/integration/test_pvp_answer_integrity.py::test_an_answer_after_the_match_ended_is_ignored`<br>`tests/integration/test_pvp_waiting_player.py::test_a_malformed_message_does_not_end_the_players_match` |
| US1-AS3 | A | `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_closing_a_match_twice_applies_the_delta_once`<br>`tests/integration/test_spec001_concurrent_rating_writers.py::test_spec001_a_pvp_result_applied_during_an_answer_keeps_its_delta`<br>`tests/integration/test_pvp_history_display.py::test_the_history_sends_the_shown_delta` |
| US1-AS4 | A | `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_matches_orphaned_by_a_restart_are_closed`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_a_live_match_is_left_alone`<br>`tests/api/test_pvp_orphan_sweep.py::test_the_sweep_runs_periodically_off_the_event_loop` |
| US2-AS1 | G1 | `tests/integration/test_spec007_g_admission.py::test_spec007_a_student_without_rating_is_not_queued`<br>`frontend/e2e/league.spec.ts › sin diagnóstico la Liga ofrece el diagnóstico (spec 007 US2-AS1)` |
| US2-AS2 | G1 | `tests/integration/test_spec007_g_admission.py::test_spec007_a_test_user_and_a_real_student_never_meet` |
| US2-AS3 | G2 | `tests/integration/test_spec007_g_admission.py::test_spec007_students_of_two_institutions_never_meet` |
| US2-AS4 | G1 | `tests/integration/test_spec007_g_admission.py::test_spec007_a_student_away_in_a_match_cannot_queue_elsewhere`<br>`tests/integration/test_pvp_limits.py::test_spec007_a_second_league_socket_is_refused`<br>`frontend/e2e/league.spec.ts › una partida en curso impide otra búsqueda y dice por qué (spec 007 US2-AS4)` |
| US2-AS5 | G1 | `tests/integration/test_spec007_g_admission.py::test_spec007_each_refusal_has_its_own_code`<br>`frontend/e2e/league.spec.ts › cada rechazo muestra su motivo (spec 007 US2-AS5)` |
| US3-AS1 | M | `tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_the_close_pair_is_picked`<br>`tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_a_lone_waiter_is_eligible_wider_the_longer_they_wait`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_the_close_pair_meets_and_the_far_one_waits`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_a_lone_waiter_meets_a_farther_rival_after_waiting` |
| US3-AS2 | M | `tests/integration/test_spec007_m_fair_matches.py::test_spec007_a_pairs_fourth_match_of_the_day_is_unrated_and_announced`<br>`frontend/e2e/league.spec.ts › una partida fuera del cupo diario avisa que no cuenta (spec 007 US3-AS2)`<br>`frontend/e2e/league.spec.ts › el historial dice que una partida fuera del cupo no contó (spec 007 US3-AS2)` |
| US3-AS3 | M | `tests/integration/test_spec007_m_fair_matches.py::test_spec007_match_items_are_near_the_mean_unseen_with_images_and_no_difficulty`<br>`frontend/e2e/league.spec.ts › el ítem de la Liga muestra su imagen (spec 007 US3-AS3)` |
| US4-AS1 | F | `tests/integration/test_spec007_f_match_flow.py::test_spec007_the_server_closes_at_its_end_time_whatever_the_client_does`<br>`frontend/e2e/league.spec.ts › la cuenta atrás sigue la hora del servidor aunque la pestaña duerma (spec 007 US4-AS1)` |
| US4-AS2 | F | `tests/unit/domain/test_spec007_f_outcome.py::test_spec007_equal_scores_the_faster_player_wins`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_tied_match_is_won_by_speed`<br>`frontend/e2e/league.spec.ts › un empate se decide por velocidad (spec 007 US4-AS2)` |
| US4-AS3 | F | `tests/integration/test_spec007_f_match_flow.py::test_spec007_a_player_who_returns_within_the_grace_resumes_the_match`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_player_who_does_not_return_loses_by_abandonment`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_reconnect_after_the_grace_finds_the_match_over`<br>`frontend/e2e/league.spec.ts › una caída reconecta y retoma la partida (spec 007 US4-AS3)`<br>`frontend/e2e/league.spec.ts › el rival abandona y ganas al instante (spec 007 US4-AS3)`<br>`frontend/e2e/league.spec.ts › volver tarde dice que la partida terminó (spec 007 US4-AS3)` |
| US5-AS1 | L | `tests/integration/test_pvp_limits.py::test_spec007_a_second_league_socket_is_refused`<br>`tests/integration/test_pvp_limits.py::test_spec007_a_closed_league_socket_frees_the_student`<br>`frontend/e2e/league.spec.ts › una segunda pestaña dice por qué (spec 007 US5-AS1)` |
| US5-AS2 | L | `tests/integration/test_pvp_limits.py::test_spec007_an_oversized_frame_is_dropped`<br>`tests/integration/test_pvp_limits.py::test_spec007_a_burst_beyond_the_rate_is_dropped`<br>`tests/integration/test_pvp_limits.py::test_spec007_persisting_abuse_closes_the_socket`<br>`frontend/e2e/league.spec.ts › demasiados mensajes cierran la conexión con su motivo (spec 007 US5-AS2)` |
| US6-AS1 | H | `tests/integration/test_spec007_h_history.py::test_spec007_history_lists_finished_abandoned_and_not_saved`<br>`tests/integration/test_spec007_h_history.py::test_spec007_history_pages_of_five_reach_every_match`<br>`frontend/e2e/league.spec.ts › el historial muestra partidas abandonadas y no guardadas con su materia (spec 007 US6-AS1)` |
| US6-AS2 | H | `tests/integration/test_spec007_h_history.py::test_spec007_a_failing_close_is_retried_then_recorded_not_saved` |
| US7-AS1 | S | `tests/integration/test_spec007_s_league_stats.py::test_spec007_a_league_miss_reaches_the_students_statistics`<br>`tests/integration/test_spec007_s_league_stats.py::test_spec007_a_league_miss_reaches_the_teachers_view`<br>`frontend/e2e/league-stats.spec.ts › la Liga aparece en mis estadísticas, aparte de la práctica (spec 007 US7-AS1)`<br>`frontend/e2e/league-stats.spec.ts › el docente ve lo que el estudiante falla en la Liga (spec 007 US7-AS1)` |
| FR-001 | A | `tests/integration/test_pvp_enrolment.py::test_pvp_admits_an_enrolled_student`<br>`tests/integration/test_pvp_enrolment.py::test_pvp_still_refuses_a_student_not_enrolled` |
| FR-002 | A | `tests/integration/test_pvp_enrolment.py::test_pvp_matches_and_finishes_a_game_between_enrolled_students`<br>`tests/integration/test_pvp_repository.py::TestPvpMatchLifecycle::test_create_returns_match_id` |
| FR-003 | A | `tests/integration/test_pvp_answer_integrity.py::test_an_answer_outside_the_match_scores_nothing`<br>`tests/integration/test_pvp_answer_integrity.py::test_an_answer_after_the_match_ended_is_ignored` |
| FR-004 | A | `tests/integration/test_pvp_answer_integrity.py::test_a_course_without_items_starts_no_match` |
| FR-005 | A | `tests/integration/test_pvp_waiting_player.py::test_the_waiting_players_first_answer_is_never_lost`<br>`tests/integration/test_pvp_waiting_player.py::test_a_message_while_waiting_does_not_leave_the_lobby` |
| FR-006 | A | `tests/integration/test_pvp_waiting_player.py::test_a_malformed_message_does_not_end_the_players_match` |
| FR-007 | A | `tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once`<br>`tests/integration/test_pvp_repository.py::TestPvpMatchLifecycle::test_elo_never_negative`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_result_moves_the_canonical_rating_not_just_the_average`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_closing_a_match_twice_applies_the_delta_once`<br>`tests/integration/test_spec001_concurrent_rating_writers.py::test_spec001_a_pvp_result_applied_during_an_answer_keeps_its_delta` |
| FR-008 | A | `tests/unit/application/test_spec001_service.py::test_spec001_pvp_lobby_rating_is_the_course_rating_read_outside_the_lock`<br>`tests/unit/application/test_spec001_service.py::test_spec001_pvp_shows_pending_never_the_1000_fallback` |
| FR-009 | A | `tests/integration/test_spec004_e2_display_names.py::test_spec004_pvp_rival_is_named_in_the_match`<br>`tests/integration/test_spec004_e2_display_names.py::test_spec004_pvp_history_shows_the_rival_by_name` |
| FR-010 | A | `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_matches_orphaned_by_a_restart_are_closed`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_a_live_match_is_left_alone`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_spec001_abandonment_starts_after_600_seconds`<br>`tests/api/test_pvp_orphan_sweep.py::test_the_sweep_runs_periodically_off_the_event_loop`<br>`tests/api/test_pvp_orphan_sweep.py::test_a_failed_pass_does_not_stop_the_sweep`<br>`tests/api/test_pvp_orphan_sweep.py::test_the_api_runs_the_sweep_and_stopping_it_closes_no_match` |
| FR-011 | A | `tests/unit/application/test_pvp_display.py::test_game_end_carries_the_shown_delta`<br>`tests/unit/application/test_pvp_display.py::test_pvp_history_carries_the_shown_delta`<br>`tests/integration/test_pvp_history_display.py::test_the_history_sends_the_shown_delta`<br>`frontend/e2e/league.spec.ts › la respuesta se colorea con su propio resultado`<br>`frontend/e2e/league.spec.ts › un ELO sin cambio dice por qué`<br>`frontend/e2e/league.spec.ts › el historial muestra el número del servidor, sin redondear en el navegador` |
| FR-012 | A | `tests/integration/test_pvp_repository.py::TestPvpMatchLifecycle::test_full_match_recorded_in_history`<br>`tests/integration/test_pvp_repository.py::TestPvpMatchLifecycle::test_history_perspective_is_per_user`<br>`tests/api/test_pvp.py::TestPvpHistory::test_history_requires_auth` |
| FR-020 | G1 | `tests/unit/domain/test_spec007_g_admission.py::test_spec007_entry_refusal_reasons`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_a_student_without_rating_is_not_queued`<br>`frontend/e2e/league.spec.ts › sin diagnóstico la Liga ofrece el diagnóstico (spec 007 US2-AS1)` |
| FR-021 | G1 | `tests/unit/domain/test_spec007_g_admission.py::test_spec007_test_users_meet_only_test_users`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_a_test_user_and_a_real_student_never_meet`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_two_test_users_meet`<br>`tests/integration/test_pvp_repository.py::test_spec007_league_entry_profile_returns_raw_fields` |
| FR-022 | G2 | `tests/unit/domain/test_spec007_g_admission.py::test_spec007_entry_refusal_reasons`<br>`tests/unit/domain/test_spec007_g_admission.py::test_spec007_students_of_different_institutions_never_meet`<br>`tests/unit/domain/test_spec007_g_admission.py::test_spec007_institutions_compare_folded`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_students_of_two_institutions_never_meet`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_a_student_without_institution_is_refused`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_two_test_users_meet`<br>`tests/integration/test_pvp_repository.py::test_spec007_league_entry_profile_returns_raw_fields`<br>`frontend/e2e/league.spec.ts › sin institución la Liga dice qué falta (spec 007 FR-022)` |
| FR-023 | G1 | `tests/integration/test_spec007_g_admission.py::test_spec007_a_student_away_in_a_match_cannot_queue_elsewhere`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_a_student_who_finished_and_left_cannot_queue_until_the_match_ends`<br>`tests/integration/test_pvp_limits.py::test_spec007_a_second_league_socket_is_refused`<br>`frontend/e2e/league.spec.ts › una partida en curso impide otra búsqueda y dice por qué (spec 007 US2-AS4)` |
| FR-024 | G1 | `tests/integration/test_spec007_g_admission.py::test_spec007_each_refusal_has_its_own_code`<br>`tests/integration/test_spec007_g_admission.py::test_spec007_a_failed_rating_read_is_a_server_error`<br>`tests/integration/test_pvp_enrolment.py::test_pvp_still_refuses_a_student_not_enrolled`<br>`tests/api/test_websocket_authorization.py::test_pvp_rejects_course_without_enrollment`<br>`frontend/e2e/league.spec.ts › cada rechazo muestra su motivo (spec 007 US2-AS5)` |
| FR-030 | M | `tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_window_starts_at_150_and_widens_each_step`<br>`tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_window_stops_at_its_ceiling`<br>`tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_the_close_pair_is_picked`<br>`tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_a_lone_waiter_is_eligible_wider_the_longer_they_wait`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_the_close_pair_meets_and_the_far_one_waits`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_a_lone_waiter_meets_a_farther_rival_after_waiting`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_two_waiters_meet_when_their_windows_grow` |
| FR-031 | M | `tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_the_pair_day_starts_at_midnight_in_colombia`<br>`tests/unit/domain/test_spec007_m_matchmaking.py::test_spec007_the_fourth_match_of_a_pair_in_a_day_is_not_rated`<br>`tests/integration/test_pvp_repository.py::test_spec007_pair_matches_since_returns_raw_rows`<br>`tests/integration/test_pvp_repository.py::test_spec007_finish_unrated_moves_no_rating`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_a_pairs_fourth_match_of_the_day_is_unrated_and_announced`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_yesterdays_matches_do_not_count`<br>`frontend/e2e/league.spec.ts › una partida fuera del cupo diario avisa que no cuenta (spec 007 US3-AS2)`<br>`frontend/e2e/league.spec.ts › una partida que cuenta no muestra el aviso (spec 007 US3-AS2)` |
| FR-032 | M | `tests/unit/domain/test_spec007_m_match_items.py::test_spec007_match_items_are_near_the_mean`<br>`tests/unit/domain/test_spec007_m_match_items.py::test_spec007_match_items_skip_items_seen_this_week`<br>`tests/unit/domain/test_spec007_m_match_items.py::test_spec007_match_items_fill_with_seen_items_when_too_few_remain`<br>`tests/integration/test_pvp_repository.py::test_spec007_items_seen_since_reads_practice_exams_and_league`<br>`tests/integration/test_spec007_m_fair_matches.py::test_spec007_match_items_are_near_the_mean_unseen_with_images_and_no_difficulty`<br>`frontend/e2e/league.spec.ts › el ítem de la Liga muestra su imagen (spec 007 US3-AS3)` |
| FR-033 | M | `tests/integration/test_spec007_m_fair_matches.py::test_spec007_the_expectation_is_read_when_the_match_is_formed` |
| FR-040 | F | `tests/integration/test_spec007_f_match_flow.py::test_spec007_game_start_carries_the_servers_end_time`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_the_server_closes_at_its_end_time_whatever_the_client_does`<br>`tests/unit/infrastructure/test_pvp_logic.py::test_spec007_an_answer_read_after_the_end_time_is_not_judged`<br>`frontend/e2e/league.spec.ts › la cuenta atrás sigue la hora del servidor aunque la pestaña duerma (spec 007 US4-AS1)` |
| FR-041 | F | `tests/unit/domain/test_spec007_f_outcome.py::test_spec007_equal_scores_the_faster_player_wins`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_tied_match_is_won_by_speed`<br>`frontend/e2e/league.spec.ts › un empate se decide por velocidad (spec 007 US4-AS2)` |
| FR-042 | F | `tests/integration/test_spec007_f_match_flow.py::test_spec007_a_player_who_returns_within_the_grace_resumes_the_match`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_player_who_does_not_return_loses_by_abandonment`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_reconnect_after_the_grace_finds_the_match_over`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_reconnect_takes_over_a_half_open_socket`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_waiting_player_reconnects_without_waiting_for_the_ping`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_a_player_who_finished_and_leaves_does_not_forfeit`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_both_players_away_abandons_without_rating`<br>`tests/integration/test_spec007_f_match_flow.py::test_spec007_the_grace_does_not_extend_the_match`<br>`tests/integration/test_pvp_repository.py::test_spec007_finish_with_a_reason_keeps_no_rated_topics`<br>`frontend/e2e/league.spec.ts › una partida perdida por abandono lo dice en el historial (spec 007 FR-042)` |
| FR-050 | L | `tests/integration/test_pvp_limits.py::test_spec007_a_second_league_socket_is_refused`<br>`tests/integration/test_pvp_limits.py::test_spec007_a_closed_league_socket_frees_the_student` |
| FR-051 | L | `tests/integration/test_pvp_limits.py::test_spec007_an_oversized_frame_is_dropped`<br>`tests/integration/test_pvp_limits.py::test_spec007_a_burst_beyond_the_rate_is_dropped`<br>`tests/integration/test_pvp_limits.py::test_spec007_persisting_abuse_closes_the_socket`<br>`tests/integration/test_pvp_limits.py::test_spec007_an_oversized_sign_in_frame_is_dropped`<br>`tests/unit/api/test_pvp_limits.py::test_spec007_socket_limits_accept_up_to_the_rate_then_drop`<br>`tests/unit/api/test_pvp_limits.py::test_spec007_socket_limits_abuse_is_ten_drops_within_ten_seconds` |
| FR-052 | L | `tests/api/test_single_worker.py::test_spec007_a_second_worker_refuses_to_start`<br>`tests/api/test_single_worker.py::test_spec007_a_single_worker_starts_and_a_restart_is_not_blocked`<br>`tests/api/test_single_worker.py::test_spec007_web_concurrency_is_still_refused` |
| FR-060 | H | `tests/integration/test_spec007_h_history.py::test_spec007_history_lists_finished_abandoned_and_not_saved`<br>`tests/integration/test_spec007_h_history.py::test_spec007_history_pages_of_five_reach_every_match`<br>`tests/integration/test_spec007_h_history.py::test_spec007_the_sweep_records_why`<br>`frontend/e2e/league.spec.ts › ver más carga la página siguiente del historial (spec 007 FR-060)` |
| FR-061 | H | `tests/integration/test_spec007_h_history.py::test_spec007_a_failing_close_is_retried_then_recorded_not_saved`<br>`tests/integration/test_spec007_h_history.py::test_spec007_a_close_that_succeeds_on_retry_finishes_normally`<br>`tests/integration/test_spec007_h_history.py::test_spec007_abandon_is_idempotent_and_skips_a_finished_match` |
| FR-070 | S | `tests/unit/domain/test_spec007_s_answer_stats.py::test_spec007_league_summary_counts_per_topic_and_item`<br>`tests/unit/domain/test_spec007_s_answer_stats.py::test_spec007_league_summary_of_no_answers_is_empty`<br>`tests/unit/domain/test_spec007_s_answer_stats.py::test_spec007_league_export_rows_one_per_student_topic_item`<br>`tests/integration/test_spec007_s_league_stats.py::test_spec007_league_answers_are_raw_rows_of_closed_matches`<br>`tests/integration/test_spec007_s_league_stats.py::test_spec007_answers_of_every_closed_match_count`<br>`tests/integration/test_spec007_s_league_stats.py::test_spec007_teacher_league_answers_follow_the_student_set`<br>`tests/integration/test_spec007_s_league_stats.py::test_spec007_the_export_has_a_league_sheet`<br>`tests/integration/test_spec007_s_league_stats.py::test_spec007_league_answers_leave_the_practice_figures_unchanged`<br>`tests/api/test_pvp.py::TestLeagueStats::test_the_students_league_stats_have_their_shape`<br>`tests/api/test_pvp.py::TestLeagueStats::test_the_teachers_view_is_for_teachers`<br>`frontend/e2e/league-stats.spec.ts › sin respuestas en la Liga no hay tarjeta de la Liga (spec 007 FR-070)`<br>`frontend/e2e/league-stats.spec.ts › el libro trae la hoja Liga (spec 007 FR-070)` |
