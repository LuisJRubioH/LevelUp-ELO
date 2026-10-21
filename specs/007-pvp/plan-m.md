# Plan — spec 007, delivery M: fair matches

**Spec**: [spec.md](spec.md) § Deliveries, M (US3; FR-030, FR-031, FR-032, FR-033) · **Branch**:
`007-m`, from `redesign` · **Date**: 2026-10-21 · **Status**: draft for the owner's approval
(decisions O-M1 … O-M11 open)

## Summary

Today the lobby is one slot per course: whoever waits meets whoever comes next, whatever their
ratings (survey V5). Nothing limits how often the same two students play rated matches. The ten
items are `random.sample` over the whole course — any difficulty, possibly items one of the players
practised minutes ago — sent with their `difficulty` and without their `image_url` (V13, V19). The
expectation of `pvp_deltas` uses the ratings read when each player entered the lobby, up to ~8
minutes old at the close (V24). Delivery M replaces the slot with a queue per course in which two
students meet only within a rating window that widens while they wait; plays a pair's fourth and
later matches of the day without rating, telling both before the start; chooses the items near the
mean of the two ratings, unseen by either player for a week, with their images and without their
difficulty; and reads both ratings again when the match is formed.

## Constitution Check (1.2.0)

| Principle | M |
|---|---|
| The spec is the contract (I) | FR-030 … FR-033 and US3-AS1 … AS3 each get a test written first; every number and rule the spec leaves open is an owner decision below (O-M1 … O-M11), not a choice of this plan |
| One source of truth (II) | the window, the cap and the item band are settings read in one place (`api/config.py`) and passed to the domain; the screen shows the server's `rated` flag and reason as given and estimates nothing |
| Layers (III, R2) | the business rules are pure functions with no I/O in a new `src/domain/pvp/matchmaking.py` (window, opponent choice, the Colombian day, the cap) and `src/domain/pvp/match_items.py` (item choice, a seeded `random.Random` passed in); the lobby, the timer and the I/O stay in `api/websocket/pvp.py`; the code PR adds both files to spec 007's § Code Scope, beside F's `src/domain/pvp/outcome.py` (O-F9) |
| Raw rows (R15) | the two new repository reads return raw rows — the pair's matches since a time, the item ids a player saw since a time — and the domain counts, filters and chooses; no repository averages, rounds or orders by rating |
| Dual database (IV, R1) | every new or changed repository method lands in both repositories with an identical signature; `db_sync_check.py`; integration tests on both engines (`live_api`) |
| Schema (R8) | **no schema change** under the recommended O-M5: an unrated match is a `finished` row with both deltas 0 and reason `daily_cap` in the existing `elo_reason_p1/p2`, as H's `not_saved` and F's `forfeit` are; "seen" reads existing tables and indexes (`idx_attempts_user_id`, `idx_pvp_matches_players`). The alternative under O-M5 is SCHEMA_VERSION **8** (E3 in #73 holds 7) |
| Integrity of measurement (V; R15, R19) | an over-cap match changes no rating row; a rated one still goes through `finish_pvp_match` (atomic, floor 0, idempotent) and H's retries; the expectation is the course rating read when the match is formed (FR-033); nothing is rebuilt from attempts |
| Security (VI, V2-R9) | `game_start` loses `difficulty` and keeps leaving out `correct_option`; the window and the opponent's exact rating are never sent (the opponent keeps seeing `shown_elo`, FR-008) |
| Async (R17) | the pairing decision under `_lock` is pure and does no I/O; the rating re-read, the pair count, the "seen" read and the item read run in threads after the pair has left the queue, never under `_lock` |
| Single process (R18) | the queue and its wait times live in process memory, as the slot does today; a restart empties the queue (the waiting players reconnect, F's resume token or a new entry) |
| Simplicity (VII) | no new dependency, no new table; the daily boundary uses a fixed UTC−5 offset (Colombia has no daylight saving), not `zoneinfo`, which needs the `tzdata` package on the maintainer's Windows machine |

## Design

### FR-030 — a rating window that widens while waiting (US3-AS1)

**The queue.** `_lobby: dict[str, LobbySlot]` becomes `dict[str, list[LobbySlot]]` — every student
waiting in a course, in arrival order. A `LobbySlot` gains `rating` (the course rating read at
lobby entry, as today, for the window only) and `joined_at` (`loop.time()` at entry).

**The window (O-M1).** A pure function `window(waited_s, start, step, every_s, ceiling)`:
`min(ceiling, start + step × floor(waited_s / every_s))`. Recommended: **±150** at entry, **+50
every 20 s**, ceiling **±450** (reached after 120 s). The lobby's 300 s wait limit is unchanged.

**Who may meet (O-M2).** Two slots are eligible when `|R_a − R_b| ≤ max(window_a, window_b)`: the
longer waiter's widened window admits a newcomer, which is what makes "a lone student is matched
wider the longer they wait" true. Delivery G adds its conditions (rating present, test users,
institution) to the same pure predicate; M does not anticipate them.

**Which one (O-M3).** `pick_opponent(me, waiting, now)` returns, among the eligible slots of the
course other than the student's own, the one with the **smallest rating gap**, ties broken by the
**longest wait**; None when none is eligible. US3-AS1: A (1000) and B (1400) wait; C (1100) arrives
→ C meets A; B keeps waiting.

**When the lobby looks.** Twice:
- **on entry**, under `_lock`, as today: the newcomer runs `pick_opponent`; if it finds a slot, it
  removes it from the queue and becomes the creator (p2); otherwise it appends its own slot;
- **while waiting**, every `every_s` (20 s): the waiting coroutine's loop already wakes on a
  deadline; it now also wakes each step, and under `_lock` — if its slot is still queued — runs
  `pick_opponent` for itself. If it finds a partner, it removes both slots and becomes the creator,
  waking the partner through its `matched` event, exactly as a newcomer does. Without this, two
  waiters whose windows have grown to cover each other would never meet until a third student
  arrived.
- The ghost-slot rule stays: a slot whose socket is no longer connected is dropped when seen.
- The match-forming code (re-read, items, `create_pvp_match`, wake) moves out of `_play` into one
  `_form_match(creator, partner, course_id, repo)` called from both paths.

**Composition with F (O-F1 b; O-M11).** F's resume token, issued with `waiting`, lets the same tab
replace its own stale lobby slot. With the queue, the replacement swaps the `ws` of the existing
slot in place — same position, same `joined_at` — so a resumed waiter keeps the window they had
earned (recommended O-M11). F's `game_resume` carries the match's items: it sends the same safe
items as `game_start` (below), never `difficulty`.

**Unrated players before G (O-M10).** G keeps unrated students out (FR-020), but G waits for spec
009. If M ships first, an unrated player's window and the items' mean use the same 1000 that drives
their expectation today (FR-008, spec 001 FR-029a) — never shown.

### FR-031 — at most 3 rated matches per pair per day (US3-AS2)

**The day (O-M4).** Recommended: the calendar day in Colombia — from 00:00 to 24:00 in Bogotá,
i.e. from 05:00 UTC. A pure `pair_day_start(now_utc)` returns that instant in UTC with a fixed
offset of −5 h. The repository compares it with `finished_at` (UTC in both engines: SQLite
`CURRENT_TIMESTAMP`, PostgreSQL `NOW()` on Supabase's UTC sessions); the code passes it as a
parameter, never as SQL date arithmetic.

**What counts (O-M5).** After the pair has left the queue, the creator reads, in a thread,
`get_pvp_pair_matches_since(a, b, since)` (both repositories, `@_read_only`): raw rows (`id`,
`status`, `elo_reason_p1`, `elo_reason_p2`, `finished_at`) of the matches between the two, in either
order, finished since `since` (index `idx_pvp_matches_players`). The pure
`pair_match_is_rated(rows, cap=3)` counts the **finished** rows whose reasons are not `daily_cap`
(a forfeit counts — it moved a rating; abandoned rows do not — they moved nothing) and returns
False when the count has reached the cap. The match being formed is not yet a row; one student
holds at most one League socket (L), so two matches of the same pair cannot be formed at once.

**Does the cap change who meets whom (O-M7).** Recommended: no. The pairing under `_lock` cannot
read the database, and the spec says the over-cap match is played, not refused. The alternative
keeps an in-memory count per pair and day and prefers another eligible opponent.

**An unrated match.** `ActiveMatch` gains `rated: bool`. When False:
- `game_start` carries `rated: false` and `unrated_reason: "daily_cap"` to both players (how the
  screen tells them: O-M6);
- the close computes no delta: `finish_pvp_match(…, rated=False, reason="daily_cap")` (both
  repositories) writes `status='finished'`, the winner and the scores, both deltas 0 and both
  reasons `daily_cap`, and touches no `student_course_topic_elo` row; idempotent on
  `status='active'` as today; H's retries and `not_saved` apply unchanged;
- `game_end` carries `elo_delta: 0`, `elo_delta_display: 0`, `elo_reason: "daily_cap"`; the screen
  explains it (FR-011 already explains a delta not applied) and the history shows the reason;
- F's forfeit and speed tiebreak still decide the winner of an unrated match; they move no rating.

**F's `reason` argument.** F adds `finish_pvp_match(…, reason=None)`. M adds `rated: bool = True`
next to it, same signature in both repositories; whichever lands second keeps one signature. If M
lands first, M adds `reason` with F's semantics.

### FR-032 — the items (US3-AS3)

**Seen (O-M9).** Recommended: an item is seen by a player when, in the last 7 × 24 h, the player
answered it in practice (`attempts.timestamp`), answered it in an exam
(`exam_responses.created_at`), or was served it in a League match (`pvp_matches.item_ids`, the
player in `player1_id`/`player2_id`, `started_at`). One raw read per match,
`get_item_ids_seen_since(user_ids, course_id, since)` (both repositories, `@_read_only`), returns
the item ids (raw, unordered; the domain makes the set). Lessons hold no bank items and are not read.

**The choice (O-M8).** A pure `choose_match_items(items, mean, seen, n=10, rng)`:
1. candidates = unseen items with `|difficulty − mean| ≤ 200`; widened by 100 at a time (up to the
   whole course) until there are at least `n`;
2. `n` drawn at random from the candidates (the `rng` passed in; tests seed it);
3. **"when enough remain"**: if the whole course has fewer than `n` unseen items, all unseen ones
   are taken and the rest is filled with seen items, nearest difficulty to the mean first;
4. the same items in the same order for both players, as today.

`mean` = the mean of the two course ratings re-read for FR-033. The item read itself is today's
`get_items_from_db(course_id=…)`.

**What reaches the browser.** `game_start` (and F's `game_resume`) items become
`{id, content, options, topic, image_url}`: `image_url` added (the same path practice sends,
served by `api/main.py`'s items mount), `difficulty` removed, `correct_option` still absent
(V2-R9). The screen renders the image with the existing `components/Question/QuestionImage`, as
Practice and Exam do (D5: math still through `MathContent`).

### FR-033 — the expectation read when the match is formed

- `_form_match` reads both players' course ratings again, in threads, after the pair has left the
  queue and before the items are chosen: `RatingReadService(repo).course_rating_of` (FR-008's
  path), never under `_lock`.
- `ActiveMatch` gains `expect_p1` / `expect_p2` (the re-read value, 1000 when unrated) and the
  close uses them in `pvp_deltas`; `LobbySlot.elo` remains only for the window. `shown_elo` in
  `game_start` uses the re-read value too (recommended; it is the same read).
- FR-008's pin (`test_spec001_pvp_lobby_rating_is_the_course_rating_read_outside_the_lock`) stays
  green: the lobby still reads through `_course_rating`, outside the lock.

### Repositories (both, R1)

| Method | Change | Returns |
|---|---|---|
| `get_pvp_pair_matches_since(user_a, user_b, since)` | new, `@_read_only` | raw rows of the pair's matches finished since `since` |
| `get_item_ids_seen_since(user_ids, course_id, since)` | new, `@_read_only` | item ids from `attempts`, `exam_responses`, `pvp_matches.item_ids` |
| `finish_pvp_match(…, reason=None, rated=True)` | `rated=False`: no rating row touched, deltas 0, reason for both | as today |

No new table, column or index under the recommended options; `python scripts/db_sync_check.py`
after the change. `src/application/interfaces/repositories.py` gains the two reads only if an
application service calls them (the plan calls them from `api/websocket/pvp.py`, as the other PvP
methods are).

### Settings and constants

`api/config.py`: `pvp_window_start=150`, `pvp_window_step=50`, `pvp_window_every_s=20`,
`pvp_window_max=450`, `pvp_daily_pair_cap=3`, `pvp_seen_days=7`, `pvp_item_band=200`,
`pvp_item_band_step=100` — the owner's numbers once O-M1, O-M8 are answered, tunable without a code
change. Tests shorten `pvp_window_every_s` with `monkeypatch` (the `live_api` server runs in the
test's process). `render.yaml` needs no change: the defaults are the production values.

### Frontend

- `usePvpMatch.ts`: the item type drops `difficulty`, gains `image_url?`; `game_start` stores
  `rated` and `unrated_reason`.
- `League.tsx`: the item renders `QuestionImage`; an unrated match shows the notice (O-M6) from
  `league.unrated.dailyCap`; `game_end` and the history show `league.historyReasons.daily_cap`.
- i18n `es` and `en` (`frontend/src/i18n/locales/`); colours from tokens.

## Shared files the code PR will touch (warning for parallel sessions)

- `src/infrastructure/persistence/sqlite_repository.py`, `postgres_repository.py` — two new reads
  and `finish_pvp_match`'s signature (**also changed by F**: `reason=`; and by G, E3).
- `api/websocket/pvp.py` — the lobby becomes a queue, `_form_match`, `ActiveMatch` fields,
  `game_start` items (**also changed by F**: `ends_at`, `game_resume`, the resume token on the lobby
  slot; and by G).
- `api/config.py` — eight settings (F adds `pvp_reconnect_grace_s`).
- `frontend/src/i18n/locales/es.ts`, `en.ts` — `league.unrated.*`, `league.historyReasons.daily_cap`
  (F adds `forfeit`, 4410/4411; G adds refusal notices).
- `frontend/src/hooks/usePvpMatch.ts`, `frontend/src/pages/Student/League.tsx` (F changes both).
- `specs/007-pvp/spec.md` — § Code Scope gains `src/domain/pvp/matchmaking.py` and
  `match_items.py`; § Traceability rows of M; delivery M → `closed`.
- `AGENTS.md` — R19 (the expectation is read when the match is formed; an over-cap match is
  `daily_cap`, no rating change) and the Architecture map (`domain/pvp/`).
- `docs/sdd/roadmap.md` — only the M7 progress note, if the owner tracks deliveries there.
- `render.yaml` — **no change** under the recommended options.
- `src/infrastructure/persistence/schema_version.py` — **only** under O-M5's alternative
  (SCHEMA_VERSION 8 and a new `MIGRATION_SOURCES_DIGEST`).
- Not touched: `docs/transfer.md`, any `ops/*` branch.

## Tests (written first; each `[CHANGE]` test fails on today's code)

| Test | Proves | Where |
|---|---|---|
| `test_spec007_window_starts_at_150_and_widens_each_step`, `test_spec007_window_stops_at_its_ceiling` | FR-030 (O-M1) | `tests/unit/domain/test_spec007_m_matchmaking.py` |
| `test_spec007_the_close_pair_is_picked`, `test_spec007_a_lone_waiter_is_eligible_wider_the_longer_they_wait` | FR-030, US3-AS1 (O-M2, O-M3) on the pure predicate | same file |
| `test_spec007_the_pair_day_starts_at_midnight_in_colombia` | FR-031 (O-M4): 04:59 UTC belongs to the previous day, 05:00 UTC starts a new one | same file |
| `test_spec007_the_fourth_match_of_a_pair_in_a_day_is_not_rated` | FR-031 (O-M5): 3 finished rated rows → False; a `daily_cap` row or an abandoned row does not count | same file |
| `test_spec007_match_items_are_near_the_mean`, `test_spec007_match_items_skip_items_seen_this_week`, `test_spec007_match_items_fill_with_seen_items_when_too_few_remain` | FR-032 (O-M8) | `tests/unit/domain/test_spec007_m_match_items.py` |
| `test_spec007_the_close_pair_meets_and_the_far_one_waits` | US3-AS1, FR-030: A 1000 and B 1400 wait, C 1100 joins → C plays A; B still `waiting` | `tests/integration/test_spec007_m_fair_matches.py` (uvicorn, both engines) |
| `test_spec007_a_lone_waiter_meets_a_farther_rival_after_waiting` | US3-AS1, FR-030: with `pvp_window_every_s` shortened, a 1000 waiter meets a 1250 newcomer only after two steps | same file |
| `test_spec007_two_waiters_meet_when_their_windows_grow` | FR-030: no newcomer; the waiters 250 apart meet on a step | same file |
| `test_spec007_a_pairs_fourth_match_of_the_day_is_unrated_and_announced` | US3-AS2, FR-031: three rated rows seeded today → `game_start` has `rated: false` for both; `game_end` 0 with `daily_cap`; no rating row changed; history shows the reason | same file |
| `test_spec007_yesterdays_matches_do_not_count` | FR-031 (O-M4): three rows finished before today's 05:00 UTC → the match is rated | same file |
| `test_spec007_match_items_are_near_the_mean_unseen_with_images_and_no_difficulty` | US3-AS3, FR-032: a course with items at several difficulties, some practised by one player this week and one with an image → the items lie in the band, none practised, `image_url` present, no `difficulty` key | same file |
| `test_spec007_the_expectation_is_read_when_the_match_is_formed` | FR-033: a waiter's rating changes while they wait; the applied delta equals `pvp_deltas` on the new rating | same file |
| `test_spec007_pair_matches_since_returns_raw_rows`, `test_spec007_items_seen_since_reads_practice_exams_and_league`, `test_spec007_finish_unrated_moves_no_rating` | the repository reads and `rated=False` (FR-031, FR-032) | `tests/integration/test_pvp_repository.py` (both engines) |
| e2e «una partida fuera del cupo diario avisa que no cuenta» and «el ítem de la Liga muestra su imagen» | US3-AS2, US3-AS3 on screen (mocked socket) | `frontend/e2e/league.spec.ts` |

Delivery A's, L's and H's pins stay green. The integration fixtures create fresh, unrated students
per test (both expected at 1000, within any window) and play at most one match per pair, so neither
the window nor the cap changes what they assert; if one did, the task sets the window or the cap
through settings for that test and says so — it never edits a pinned assertion.

**Traceability rows to fill:** FR-030, FR-031, FR-032, FR-033, US3-AS1, US3-AS2, US3-AS3
(delivery M → closed).

## Risks

- **Small institutions, wide gaps.** With G's same-institution rule, a student far from everyone
  waits until the ceiling and may time out at 300 s with no rival; O-M1's ceiling trades fairness
  for waiting. The numbers are settings.
- **Few unseen items.** A small course or a heavy practiser exhausts the unseen items near the
  mean; step 3 of the choice fills with seen ones rather than refusing a match.
- **Wake-ups.** One wake per waiting student every 20 s, all on the event loop with no I/O under
  `_lock`; negligible at the expected numbers.
- **Merge with F and G** on `pvp.py`'s lobby, `game_start` and `finish_pvp_match`: the same
  functions; whichever lands second merges (above).
- **Before G, unrated players** still play, expected and placed at 1000 (O-M10).

## Decisions (owner) — open

Each has a recommended option; none is decided by this plan.

- **O-M1 — the window's numbers.** Recommended: ±150 at entry, +50 every 20 s, ceiling ±450 (at
  120 s); the 300 s lobby limit unchanged. Alternatives: (b) no ceiling — +50 every 20 s until the
  300 s limit (±850); (c) a finer step, +25 every 10 s, same ceiling.
- **O-M2 — whose window.** Recommended: eligible when the gap is within the **larger** of the two
  windows (the long waiter admits a newcomer). Alternative: within the **smaller** (both must
  accept) — a lone waiter then only meets another long waiter.
- **O-M3 — which eligible opponent.** Recommended: the smallest rating gap, ties by the longest
  wait. Alternative: the longest wait among the eligible (first come, first served inside the
  window).
- **O-M4 — "a day".** Recommended: the calendar day in Colombia (00:00–24:00 Bogotá = from 05:00
  UTC, fixed UTC−5). Alternative: a rolling 24 h before the match.
- **O-M5 — how an over-cap match is recorded.** Recommended, no schema change: `finished`, deltas 0,
  reason `daily_cap` for both; the cap counts finished rows without that reason (forfeits count,
  abandoned rows do not). Alternative: SCHEMA_VERSION 8 adds `pvp_matches.rated BOOLEAN NOT NULL
  DEFAULT TRUE` (both repositories, R8, new digest) and the cap counts `rated` rows — clearer
  queries, at the cost of a migration and a rehearsal before production.
- **O-M6 — how both are told before the start.** Recommended: `game_start` carries `rated: false`
  and `unrated_reason: "daily_cap"`; the screen shows «Esta partida no cuenta para tu ELO: ya
  jugaron 3 partidas hoy» above the first item and keeps it in the match header — both see it before
  any answer. Alternative: a `match_found {rated, unrated_reason}` frame and a 3 s pre-start screen
  with the notice, the match clock (F's `ends_at`) starting after it.
- **O-M7 — does the cap change pairing.** Recommended: no; the pair meets and plays unrated.
  Alternative: an in-memory count per pair and day, and the lobby prefers another eligible opponent.
- **O-M8 — the item band.** Recommended: unseen items within ±200 of the mean, widened by 100 until
  10, then 10 at random; fewer than 10 unseen in the course → fill with seen ones, nearest first.
  Alternative: `AdaptiveItemSelector` ten times on the mean rating (P ∈ [0.40, 0.75] — skewed below
  the mean: D from R−191 to R+70).
- **O-M9 — "seen in the last week".** Recommended: answered in practice or in an exam, or served in
  a League match, by either player in the last 7 × 24 h. Alternative: answered only (`attempts`,
  `exam_responses`, `pvp_answers`) — an item shown in a League match but not answered stays
  eligible.
- **O-M10 — before G ships.** Recommended: M does not wait for G; an unrated player is placed and
  expected at 1000, never shown, until G keeps them out. Alternative: M waits for G (and spec 009).
- **O-M11 — a resumed waiter (with F).** Recommended: F's lobby resume keeps the slot's position and
  `joined_at`, so the earned window is kept. Alternative: a resume restarts the wait at ±150.
