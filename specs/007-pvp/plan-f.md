# Plan — spec 007, delivery F: the server's clock, a speed tiebreak and a 20 s grace

**Spec**: [spec.md](spec.md) § Deliveries, F (US4; FR-040, FR-041, FR-042) · **Branch**: `007-f`,
from `redesign` · **Date**: 2026-10-21 · **Status**: draft for the owner's approval (decisions
O-F1 … O-F9 open)

## Summary

Today the match clock lives in two places: the server closes the match 180 s after `game_start`
(`_timer`), while the screen counts `setInterval` ticks from `duration_seconds`, which a background
tab slows (survey V20). Equal scores are always a draw. A player whose socket drops is not replaced
and cannot come back: the match runs to 180 s, the opponent is not told, and reconnecting joins the
lobby as a new player (V9) — or, since delivery L, is refused with 4409 for up to ~40 s while the
server still holds the half-open socket (plan-l § FR-050, "Reconnect"). Delivery F sends the
server's end time and counts down to it, breaks equal scores by total answer time, and keeps a
dropped player's place for 20 s: a reconnect in that window resumes the match, otherwise the match
ends at once as that player's loss by abandonment.

## Constitution Check (1.2.0)

| Principle | F |
|---|---|
| The spec is the contract (I) | FR-040 … FR-042 and US4-AS1 … AS3 each get a test written first; every point the spec leaves open is an owner decision below (O-F1 … O-F9), not a choice of this plan |
| One source of truth (II) | the end time, the answer times, the grace and the winner are the server's; the screen renders `ends_at` and `game_end` as given and estimates nothing (V2-R3 spirit) |
| Layers (III) | the winner rule (score, then time to the second) is a pure function with no I/O (where it lives: O-F9); the socket, the grace timer and the resume path stay in `api/websocket/pvp.py`; repositories return raw rows |
| Dual database (IV, R1) | one optional argument on `finish_pvp_match` in both repositories (O-F3), `db_sync_check.py`; integration tests on both engines through `live_api` |
| Schema (R8) | **no schema change** under the recommended O-F3: the forfeit reason uses the existing `elo_reason_p1/p2` columns, as H's `not_saved` and the sweep's `orphaned` do |
| Integrity of measurement (V; R15, R19) | a forfeit moves the course rating once, through `finish_pvp_match` (atomic, floor 0, idempotent on `status='active'`) and H's retry; a match both players leave changes no rating; nothing is rebuilt from attempts |
| Security (VI) | the resume token is a per-match random secret held in memory, compared in constant time, bound to the authenticated user; a reconnect re-authenticates with the JWT and the enrolment check; no new field reveals the opponent's answers or an item's key (V2-R9) |
| Async (R17) | grace bookkeeping is under `_lock` with no I/O; the forfeit close runs outside it, through `_finish_match`, as every other close |
| Single process (R18) | the grace and the tokens live in process memory; a restart during a grace ends the match as abandoned by the sweep (A, spec § Edge Cases) |
| Simplicity (VII) | no new dependency, no new table; one in-memory token per player, one grace task per away player |

## Design

### FR-040 — the server's end time (US4-AS1)

- When the match is formed, the creator's coroutine fixes, once:
  `started = loop.time()`, `ends_at_loop = started + MATCH_DURATION`, and the wall-clock
  `ends_at` (UTC, ISO 8601 with milliseconds). They live on `ActiveMatch`.
- `game_start` keeps `duration_seconds` and adds `ends_at` and `server_now` (UTC ISO). The
  `game_resume` frame (FR-042) carries the same two fields.
- **The server alone decides the end:** `_timer` sleeps until `ends_at_loop`, not a fresh 180 s;
  `_judge_answer` ignores an answer read at or after `ends_at_loop` even if the timer coroutine has
  not run yet (today only `match.finished` stops it). An answer the server ignored gets no reply, as
  today (FR-003).
- **Screen** (`usePvpMatch.ts`): on `game_start` / `game_resume` it stores
  `offset = server_now − Date.now()` and `endsAt`; every tick (and on `visibilitychange`) it sets
  `timeLeft = max(0, ceil((endsAt − (Date.now() + offset)) / 1000))`. A tab that slept shows the
  right time on its first tick back; the screen never closes the match itself — at 0 it disables the
  options and waits for `game_end`.

### FR-041 — the speed tiebreak (US4-AS2)

- For each player the server keeps `elapsed[user_id]`: the sum, over the player's **counted
  answers** (definition: O-F7), of `answer_read_time − started`, measured on the loop's monotonic
  clock. Kept in memory with the score (owner, V23: "the score stays in memory"); `pvp_answers`
  is unchanged.
- At close, the winner rule is: higher score wins; on equal scores, the lower
  `floor(elapsed)` (whole seconds, O3: "a draw remains only on equal time to the second") wins;
  equal whole seconds is a draw. A tiebreak win is a full win: `pvp_deltas(…, 1.0 / 0.0)`, `won`
  true / false in `game_end`, `winner_id` stored.
- `game_end` adds `tiebreak: true` when the time decided it, so the result screen can say «ganaste
  por velocidad» / «perdiste por velocidad» (i18n `league.tiebreak*`). The history needs nothing new:
  it shows won / lost as today.
- 0–0 with no counted answers has `elapsed = 0` for both → a draw, as today.

### FR-042 — a 20 s grace, then a forfeit (US4-AS3)

**Recognising a reconnect (O-F1).** Server-side, a reconnect and a second tab look the same: a new
authenticated socket of a student who already has one. Recommended: each player receives a random
`resume` token (`secrets.token_urlsafe(16)`), with `waiting` and with `game_start`; the client keeps
it in `sessionStorage` (per tab, survives a reload). The first frame of a reconnect is
`{token, resume}`. A valid `resume` for the student's own match (or lobby slot) **takes over**: the
old socket, if the server still holds it, is closed with **4411** «Tu partida siguió en otra
conexión.» and the new one is bound to the slot. A socket without a valid `resume` meets L's rule
unchanged: refused 4409 while another live League socket exists (US5-AS1 keeps holding).

**The drop.** When a player's answer loop ends with `WebSocketDisconnect` (or 4429 — a socket closed
for abuse is a drop like any other) while the match is not finished:
- under `_lock`, the player is marked away until `loop.time() + PVP_RECONNECT_GRACE_S`
  (setting, default **20**, O2) and one grace task is scheduled; no I/O under the lock;
- the opponent receives `opponent_away {grace_seconds}` (the screen shows «Tu rival se desconectó;
  tiene 20 s para volver»);
- frames to an away player are not sent (they would only fail and log).
- A player who drops after answering every item (`done`) is a special case: O-F4.

**The resume.** A reconnect with a valid `resume` token for a match still in `_matches`:
- under `_lock`: the slot's `ws` is replaced (the `LobbySlot` is shared, so the opponent's
  `opponent.ws` sends reach the new socket), the away mark is cleared, the grace task cancelled,
  `_league_sockets[user_id]` points to the new socket;
- the player receives `game_resume {match_id, items, answered: [item ids], your_score, opp_score,
  opponent, ends_at, server_now}` and the answer loop continues on the new socket; the opponent
  receives `opponent_back`;
- the clock keeps running during the grace and the grace never extends the match (O-F6).
- The timer task and `_finish_early` move onto `ActiveMatch` (today `timer_task` is a local of the
  creator's coroutine), so whichever coroutine sees `all_done()` — original or resumed — can finish
  early.

**The forfeit.** If the grace task wakes and the player is still away and the match not finished:
- the match closes through `_finish_match` (so H's retries and `not_saved` apply) with the away
  player as loser — outcome 0 / 1 in `pvp_deltas`, whatever the scores (O-F2) — and the reason
  `forfeit` recorded for both players (O-F3);
- the opponent receives `game_end` at once with `won: true`, `forfeit: true`; the result screen
  says «Tu rival abandonó la partida»;
- if both players are away when a grace ends, O-F5 applies.

**After the grace.** A reconnect whose `resume` names a match no longer in `_matches` is closed with
**4410** «La partida ya terminó.»; the screen shows it, invalidates the history (which now shows the
loss «por abandono») and returns to the lobby, where the student may queue again (spec § Edge
Cases). A reconnect with no `resume` after the grace is an ordinary new entry.

**Drop detection (O-F8).** The grace starts when the server *detects* the drop. A closed tab or a
network change usually ends the socket at once; a half-open connection is detected only by uvicorn's
ping (today 20 s interval + 20 s timeout). Under O-F1 the reconnect itself replaces the stale socket,
so the returning student is never blocked; O-F8 decides how long a player who vanished silently
takes to forfeit.

**Screen** (`usePvpMatch.ts`, `League.tsx`):
- a new phase `reconnecting`: an abnormal close (not a 4xxx code, not after `game_end`) during
  `playing` reconnects automatically — at once, then every 2 s — sending `{token, resume}`, for up to
  the grace; the screen shows «Reconectando… (n s)» with the countdown still running to `endsAt`;
- `game_resume` restores items, the current index (the first item not in `answered`), the scores and
  `endsAt`, and returns to `playing`;
- `opponent_away` / `opponent_back` show and clear a notice in the match header;
- `CLOSE_NOTICES` gains 4410 (`matchOver`) and 4411 (`resumedElsewhere`); `league.historyReasons`
  gains `forfeit`, shown on a finished row whose reason is `forfeit` (today only abandoned rows show
  a reason); every string in `es` and `en`.
- An expired access token during the reconnect is refreshed through the store's existing refresh
  before the retry (the match lasts 180 s, a token 15 min; rare, but a 4001 must not lose a match
  that a refresh would save).

### The waiting player and the lobby (L's open issue)

A waiting student whose socket went half-open still occupies `_league_sockets` and the lobby slot.
Under O-F1 (b) the `resume` token is also issued with `waiting`, so the same tab reconnecting replaces
its own stale lobby slot instead of being refused 4409 for up to ~40 s. The grace does **not** apply
in the lobby: a waiting player who drops leaves the queue as today (FR-005 pins it). A player whose
`game_start` cannot be sent is treated as having dropped at the start: the grace applies from
`started`.

### Repositories

- `finish_pvp_match(…, reason: str | None = None)` (both repositories, identical signature): when
  given, `reason` is written to each player's `elo_reason_*` where the delta was applied normally;
  `no_rated_topics` keeps precedence for a player with no rated topic. Default `None` keeps every
  current call unchanged.
- Both players away (recommended O-F5): the existing `abandon_pvp_match(match_id, "both_left")`; no
  new method.
- `python scripts/db_sync_check.py` after the change.

### Settings and constants

`api/config.py`: `pvp_reconnect_grace_s = 20` (`PVP_RECONNECT_GRACE_S`). `api/websocket/pvp.py`:
`MATCH_ENDED_CODE = 4410`, `RESUMED_ELSEWHERE_CODE = 4411`, and the reconnect retry interval of the
screen (2 s) in `usePvpMatch.ts`. Tests shorten the grace and `MATCH_DURATION` with `monkeypatch`
(the `live_api` server runs in the test's process).

## Tests (written first; each `[CHANGE]` test fails on today's code)

| Test | Proves | Where |
|---|---|---|
| `test_spec007_game_start_carries_the_servers_end_time` | FR-040: `game_start` has `ends_at`, `server_now`; `ends_at − started ≈ MATCH_DURATION` | `tests/integration/test_spec007_f_match_flow.py` (uvicorn, both engines) |
| `test_spec007_the_server_closes_at_its_end_time_whatever_the_client_does` | FR-040, US4-AS1: with a 2 s match and a client that sends nothing, both receive `game_end` at `ends_at` (± tolerance) | same file |
| `test_spec007_an_answer_read_after_the_end_time_is_not_judged` | FR-040: `_judge_answer` with the loop clock past `ends_at_loop` → ignored, even with `finished` still false | `tests/unit/infrastructure/test_pvp_logic.py` |
| e2e «la cuenta atrás sigue la hora del servidor aunque la pestaña duerma» | US4-AS1 on screen: Playwright `page.clock` jumps 60 s without firing timers; on the next tick the countdown shows `ends_at − now`, not 60 s too much | `frontend/e2e/league.spec.ts` |
| `test_spec007_equal_scores_the_faster_player_wins` | FR-041, US4-AS2: the winner rule on (score, elapsed) pairs, including equal whole seconds → draw and 0–0 → draw | unit, where O-F9 places the rule |
| `test_spec007_a_tied_match_is_won_by_speed` | FR-041, US4-AS2: two real players, same correct answers, one answers ~2 s later per item → the faster gets `won: true, tiebreak: true`, `winner_id` stored, deltas applied | `tests/integration/test_spec007_f_match_flow.py` |
| `test_spec007_a_player_who_returns_within_the_grace_resumes_the_match` | FR-042, US4-AS3: drop, reconnect with `resume` → `game_resume` with the same match, answered items and scores; the opponent gets `opponent_away` then `opponent_back`; the next answer is judged; the match ends normally | same file |
| `test_spec007_a_player_who_does_not_return_loses_by_abandonment` | FR-042, US4-AS3: no reconnect → the opponent gets `game_end {won: true, forfeit: true}` right after the grace, well before `ends_at`; the row is `finished`, winner the opponent, reason `forfeit`, deltas applied once | same file |
| `test_spec007_a_reconnect_after_the_grace_finds_the_match_over` | FR-042, spec § Edge Cases: `resume` for a closed match → close 4410; a new entry then queues normally | same file |
| `test_spec007_a_reconnect_takes_over_a_half_open_socket` | FR-042 with FR-050 (L's open issue): the old socket left open server-side, a new one with `resume` → admitted at once, the old one closed 4411; a new one **without** `resume` → still 4409 | same file |
| `test_spec007_a_waiting_player_reconnects_without_waiting_for_the_ping` | O-F1 (b): a half-open waiting socket replaced by the same tab's reconnect; the lobby keeps one slot | same file (only if O-F1 (b) is approved) |
| `test_spec007_a_player_who_finished_and_leaves_does_not_forfeit` | O-F4 (as decided) | same file |
| `test_spec007_both_players_away_abandons_without_rating` | O-F5 (as decided): no rating moves; history reason `both_left` | same file |
| `test_spec007_the_grace_does_not_extend_the_match` | O-F6 (as decided): a drop 1 s before `ends_at` → the match closes at `ends_at` by score | same file |
| `test_spec007_finish_with_a_reason_keeps_no_rated_topics` | O-F3: `finish_pvp_match(…, reason="forfeit")` writes `forfeit` where applied, `no_rated_topics` where not; idempotent | `tests/integration/test_pvp_repository.py` (both engines) |
| e2e «una caída reconecta y retoma la partida», «el rival abandona y ganas al instante», «volver tarde dice que la partida terminó» | US4-AS3 on screen (mocked socket) | `frontend/e2e/league.spec.ts` |

Delivery A's, L's and H's pins stay green. In particular: `test_draw_marks_both_draw_true` builds a
5–5 match with no answer times (equal `elapsed = 0`) and stays a draw; if its fixture had to change
to carry times, the task flips it explicitly citing FR-041. `test_spec007_a_second_league_socket_is_refused`
(US5-AS1) keeps passing: a socket without `resume` is still refused.

**Traceability rows to fill:** FR-040, FR-041, FR-042, US4-AS1, US4-AS2, US4-AS3 (delivery F →
closed).

## Risks

- **Clock skew.** A client clock far off is corrected by `server_now`; the network delay of one frame
  (≤ ~0.5 s) remains in the display, never in the decision.
- **Duplicated tab.** Browsers copy `sessionStorage` into a duplicated tab, so it carries the same
  `resume`; it would take the match over and the first tab is told 4411. Acceptable: one live socket
  remains (FR-050).
- **A player who vanishes silently** forfeits only after detection + 20 s (O-F8).
- **Restart during a grace** ends as `abandoned`/`orphaned` by the sweep, no rating change (A; R18).
- **Overlap with M** (`game_start` loses `difficulty`, adds images) and **G** (FR-024 codes table
  gains 4410 / 4411): both touch the same frame and table; whichever lands second merges.
- **H's retries** add up to 3.5 s before a forfeit's `game_end` reaches the opponent when the
  database fails; the test allows it.

## Decisions (open — for the owner)

- **O-F1 — How a reconnect is told apart from a second tab.**
  *Recommended:* a per-player `resume` token sent with `waiting` (b) and `game_start`, kept in the
  tab's `sessionStorage`; a socket presenting it takes over and the old one is closed with 4411; a
  socket without it meets L's 4409 as today. Ends the ~40 s block in the match and in the lobby.
  *Alternatives:* (a) the token only with `game_start` — the block ends in a match but remains in
  the lobby; (c) no token: the newest socket of a student who is in a match always takes over —
  simpler, but a second tab would steal a running match, contradicting US5-AS1 as written.
- **O-F2 — Does a forfeit move the rating?**
  *Recommended:* yes, as a full loss for the player who left and a full win for the opponent
  (`pvp_deltas` with outcome 0 / 1), whatever the score at that moment — otherwise leaving would be
  a free way to avoid a losing match. *Alternative:* close it as `abandoned` with no rating change
  (then a losing player can always escape; the opponent's «wins at once» would be in name only).
- **O-F3 — Where the forfeit is recorded.**
  *Recommended:* no schema change — `status='finished'`, `winner_id` = the opponent, and
  `elo_reason_*` = `forfeit` for both through `finish_pvp_match(…, reason=)`; `no_rated_topics`
  keeps precedence; the history shows «por abandono». *Alternative:* a new additive column
  `pvp_matches.end_reason` (`time`, `all_answered`, `forfeit`, …), which separates *why the match
  ended* from *what happened to the rating*, at the cost of a migration and a `SCHEMA_VERSION` bump.
- **O-F4 — A player who answered every item, then drops.**
  *Recommended:* no forfeit — they have nothing left to do; the match ends when the opponent
  finishes or at `ends_at`, by score and time, and their `game_end` is waiting for them if they
  resume. *Alternative:* the same grace and forfeit as any other drop (simpler rule, but punishes a
  student who finished and closed the tab).
- **O-F5 — Both players away.**
  *Recommended:* if, when a grace ends, the other player is also away, the match closes as
  `abandoned` with reason `both_left` and no rating change (nobody stayed to win).
  *Alternative:* the first whose grace ends loses (a rated result between two absent players).
- **O-F6 — The clock during a grace.**
  *Recommended:* it keeps running and the grace never extends `ends_at`; if `ends_at` comes during a
  grace, the match closes normally by score and time. *Alternative:* pause the match clock while a
  player is away (fairer to the one who dropped, but lets a player stall a match they are losing).
- **O-F7 — What «total answer time» counts** (FR-041; O3 says "each counted answer").
  *Recommended:* the correct answers only — the time it took to earn the score that tied — summed
  from `game_start`, compared in whole seconds. *Alternatives:* (a) every judged answer, right or
  wrong (a player who answered fewer items would win by answering less); (b) the time of the last
  correct answer (one number, the moment the player reached their score).
- **O-F8 — Faster drop detection.**
  *Recommended:* start uvicorn with `--ws-ping-interval 10 --ws-ping-timeout 10` in `render.yaml`, so
  a silently vanished player forfeits within ~40 s instead of ~60 s; it applies to every socket
  (notifications too) and costs one small ping every 10 s per socket. *Alternative:* keep uvicorn's
  20 s / 20 s; the returning player is not affected under O-F1, only the forfeit is later.
- **O-F9 — Where the winner rule lives.**
  *Recommended:* a pure function `match_outcome(score_p1, score_p2, elapsed_p1, elapsed_p2)` in a new
  `src/domain/pvp/outcome.py` (constitution III: business logic in `domain/`), with the code PR adding
  that file to spec 007's § Code Scope. *Alternative:* a private pure helper in
  `api/websocket/pvp.py`, next to `_judge_answer` (no Code Scope change; the rule stays in the
  composition layer, as the answer judgement does today).
