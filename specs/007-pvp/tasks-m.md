# Tasks — spec 007, delivery M (fair matches)

**Plan**: [plan-m.md](plan-m.md) (approved; owner decisions O-M1 … O-M11 answered 2026-10-21). FR-030, FR-031,
FR-032 and FR-033 are `[CHANGE]`; delivery M touches the lobby, the match's items, the expectation
and the close pinned by delivery A (FR-002, FR-004, FR-005, FR-007, FR-008, FR-011) and the close
retries of delivery H (FR-061).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[US3]**: User Story 3 — Matches are even

---

## Phase 0: Owner decisions (Blocking)

- [x] T000 The owner answers O-M1 … O-M11 (plan-m § Decisions); record each answer in plan-m and
  set its status to approved. Done 2026-10-21: every recommended option was approved, so the
  numbers in the tests below (±150, +50 every 20 s, ±450, 3 per day, 05:00 UTC, ±200 / +100)
  stand, and there is no schema change (O-M5).

---

## Phase 1: Setup

- [x] T001 Add the settings `pvp_window_start` (150), `pvp_window_step` (50), `pvp_window_every_s`
  (20), `pvp_window_max` (450), `pvp_daily_pair_cap` (3), `pvp_seen_days` (7), `pvp_item_band`
  (200), `pvp_item_band_step` (100) to `api/config.py` with their environment names, and create
  the empty modules `src/domain/pvp/matchmaking.py`, `src/domain/pvp/match_items.py` (beside F's
  `outcome.py`, or with the package `__init__.py` if F has not landed); no behaviour yet.

---

## Phase 2: Pin Current Behaviour (Blocking)

- [x] T002 Run against the unchanged code and record the green run here; they must stay green
  through every task below:
  - delivery A: `tests/integration/test_pvp_enrolment.py` (FR-002), `test_pvp_answer_integrity.py`
    (FR-003, FR-004), `test_pvp_waiting_player.py` (FR-005, FR-006), `test_pvp_repository.py`
    (FR-007, FR-010, FR-012), `tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once`,
    `tests/integration/test_spec001_concurrent_rating_writers.py`,
    `tests/unit/application/test_spec001_service.py::test_spec001_pvp_lobby_rating_is_the_course_rating_read_outside_the_lock`
    and `::test_spec001_pvp_shows_pending_never_the_1000_fallback` (FR-008),
    `tests/unit/application/test_pvp_display.py` and `tests/integration/test_pvp_history_display.py`
    (FR-011), `tests/unit/infrastructure/test_pvp_logic.py`, `tests/api/test_pvp*.py`;
  - delivery L: `tests/integration/test_pvp_limits.py`, `tests/unit/api/test_pvp_limits.py`;
  - delivery H: `tests/integration/test_spec007_h_history.py` (an unrated close goes through the
    same retries and `not_saved`);
  - delivery F, if merged first: `tests/integration/test_spec007_f_match_flow.py` (the lobby
    resume, O-F1 b);
  - `frontend/e2e/league.spec.ts`.
  Check that every integration fixture pairs fresh students (both at 1000) and plays at most one
  match per pair; record it here. If one does not, that test sets the window or the cap through
  settings, citing FR-030/FR-031 — never an edited assertion.
  **Recorded 2026-10-22, unchanged code (`redesign` at af9ab31, F merged):** the files above —
  delivery A, L, H and F's pins, plus `tests/integration/test_spec004_e2_display_names.py` —
  **171 passed** on both engines (SQLite + PostgreSQL), and `frontend/e2e/league.spec.ts`
  **14 passed**. Fixture check: every integration fixture that plays through the lobby creates
  fresh students, both rated 1000 in the course or unrated (expected at 1000), and plays one
  match per pair, with a fresh course per test; no fixture needed a window or cap setting.

**Checkpoint**: the lobby, the match and the close pinned — M can change them.

---

## Phase 3: User Story 3 — Matches are even (Priority: P2)

**Goal**: two students meet only within a window that widens while they wait; a pair's fourth and
later matches of the day are played unrated, announced before the start; the items are near the
mean of both ratings, unseen for a week, with images and without difficulty; the expectation is read
when the match is formed.

**Independent Test**: `tests/integration/test_spec007_m_fair_matches.py` (uvicorn, both engines;
`pvp_window_every_s` shortened with `monkeypatch`).

### Tests for User Story 3 (written first; each must FAIL before its implementation task)

- [x] T010 [P] [US3] `[CHANGE]` `test_spec007_window_starts_at_150_and_widens_each_step`,
  `test_spec007_window_stops_at_its_ceiling`, `test_spec007_the_close_pair_is_picked`,
  `test_spec007_a_lone_waiter_is_eligible_wider_the_longer_they_wait` for FR-030, US3-AS1 (O-M1 …
  O-M3) in `tests/unit/domain/test_spec007_m_matchmaking.py` — **fail** before T020
  Failed first (2026-10-22): collection `ImportError` — `WindowRule`, `window`, `eligible`,
  `pick_opponent` did not exist in the empty `matchmaking.py` (T001).
- [x] T011 [P] [US3] `[CHANGE]` `test_spec007_the_pair_day_starts_at_midnight_in_colombia`,
  `test_spec007_the_fourth_match_of_a_pair_in_a_day_is_not_rated` for FR-031 (O-M4, O-M5) in the
  same file — **fail** before T021
  Failed first: the same `ImportError` (`pair_day_start`, `pair_match_is_rated` absent).
- [x] T012 [P] [US3] `[CHANGE]` `test_spec007_match_items_are_near_the_mean`,
  `test_spec007_match_items_skip_items_seen_this_week`,
  `test_spec007_match_items_fill_with_seen_items_when_too_few_remain` for FR-032 (O-M8) in
  `tests/unit/domain/test_spec007_m_match_items.py` (seeded `random.Random`) — **fail** before T022
  Failed first: `ImportError` — `choose_match_items` absent from the empty `match_items.py`.
- [x] T013 [P] [US3] `[CHANGE]` `test_spec007_pair_matches_since_returns_raw_rows`,
  `test_spec007_items_seen_since_reads_practice_exams_and_league`,
  `test_spec007_finish_unrated_moves_no_rating` for FR-031, FR-032 (O-M5, O-M9) in
  `tests/integration/test_pvp_repository.py` (both engines) — **fail** before T023
  Failed first, both engines: `AttributeError` (no `get_pvp_pair_matches_since`, no
  `get_item_ids_seen_since`) and `TypeError` (`finish_pvp_match` took no `rated`).
- [x] T014 [P] [US3] `[CHANGE]` `test_spec007_the_close_pair_meets_and_the_far_one_waits`,
  `test_spec007_a_lone_waiter_meets_a_farther_rival_after_waiting`,
  `test_spec007_two_waiters_meet_when_their_windows_grow` for FR-030, US3-AS1 in
  `tests/integration/test_spec007_m_fair_matches.py` — **fail** before T024
  Failed first, both engines: the second student got `game_start` instead of `waiting` — the
  one-slot lobby paired whoever came next, whatever the gap.
- [x] T015 [P] [US3] `[CHANGE]` `test_spec007_a_pairs_fourth_match_of_the_day_is_unrated_and_announced`,
  `test_spec007_yesterdays_matches_do_not_count` for FR-031, US3-AS2 in the same file — **fail**
  before T025
  Failed first, both engines: `KeyError: 'rated'` — `game_start` carried no rated flag.
- [x] T016 [P] [US3] `[CHANGE]` `test_spec007_match_items_are_near_the_mean_unseen_with_images_and_no_difficulty`
  for FR-032, US3-AS3 in the same file — **fails** before T027
  Failed first, both engines: the 10 items were a random sample of the whole course (far and
  practised items included), with `difficulty` and without `image_url`.
- [x] T017 [P] [US3] `[CHANGE]` `test_spec007_the_expectation_is_read_when_the_match_is_formed` for
  FR-033 in the same file — **fails** before T028
  Failed first, both engines: B saw A at 1000 (the entry read) and the delta was 12, computed on
  the ratings read at lobby entry.
- [x] T018 [P] [US3] `[CHANGE]` e2e «una partida fuera del cupo diario avisa que no cuenta»
  (US3-AS2) and «el ítem de la Liga muestra su imagen» (US3-AS3) in `frontend/e2e/league.spec.ts`
  (mocked socket; the fixture items drop `difficulty`) — **fail** before T029
  Failed first: «…fuera del cupo diario avisa…», «el historial dice que una partida fuera del
  cupo no contó» and «…muestra su imagen» — no notice, the history showed no reason, no `img`.
  A guard, «una partida que cuenta no muestra el aviso», passes before and after (it pins that
  the notice is not shown for a rated match).

### Implementation for User Story 3

- [x] T020 [US3] FR-030: `window`, `eligible`, `pick_opponent` in `src/domain/pvp/matchmaking.py`,
  pure, numbers passed in (T010 green)
- [x] T021 [US3] FR-031: `pair_day_start` (fixed UTC−5) and `pair_match_is_rated` in the same
  module (T011 green)
- [x] T022 [US3] FR-032: `choose_match_items(items, mean, seen, n, rng, band, band_step)` in
  `src/domain/pvp/match_items.py` (T012 green)
- [x] T023 [US3] FR-031, FR-032: `get_pvp_pair_matches_since`, `get_item_ids_seen_since`
  (`@_read_only`, raw rows) and `finish_pvp_match(…, reason=None, rated=True)` in **both**
  repositories; reconcile with F's `reason=` if F landed first (T013 green)
  F had landed: `reason=` kept, `rated: bool = True` added beside it (one signature, both
  repositories). Both new reads carry `@_read_only`, so they join the list in
  `tests/integration/test_spec002_d2_connections.py::HOT_READS` (the decorator guard and the
  one-round-trip check), as spec 003 L4 and spec 008 T did for theirs.
- [x] T024 [US3] FR-030: `_lobby` becomes a queue per course; `LobbySlot.rating`, `joined_at`;
  pairing on entry and on each waiting step under `_lock` with no I/O; `_form_match` shared by both
  paths; F's lobby resume swaps the slot's `ws` in place (O-M11) (T014 green; FR-005 pins green)
  The waiting coroutine wakes at each widening of its own window and pairs under `_lock`
  (`_pair_on_step`); `LobbySlot` keeps `elo` (the entry read, for the window) with a `rating`
  alias and gains `joined_at`; `LobbySlot` compares by identity (`eq=False`).
- [x] T025 [US3] FR-031: `_form_match` reads the pair's rows in a thread and sets
  `ActiveMatch.rated`; `game_start` carries `rated` / `unrated_reason`; the close of an unrated match
  calls `finish_pvp_match(…, rated=False, reason="daily_cap")` and `game_end` reports 0 with
  `daily_cap` (T015 green; H's pins green)
  A failed read of the pair's rows plays the match rated (the cap is not known to be reached),
  logged; `game_resume` carries `rated` / `unrated_reason` too.
- [x] T027 [US3] FR-032: `_form_match` reads the seen ids in a thread and chooses with
  `choose_match_items`; the safe items are `{id, content, options, topic, image_url}` in
  `game_start` (and F's `game_resume`) (T016 green; FR-002, FR-004 pins green)
  A failed "seen" read chooses as if nothing was seen; the item read is still
  `get_items_from_db(course_id=…)`.
- [x] T028 [US3] FR-033: `_form_match` re-reads both course ratings in threads (not under `_lock`);
  `ActiveMatch.expect_p1/p2` drive `pvp_deltas`; `shown_elo` from the same read (T017 green; FR-007,
  FR-008 pins green)
  A failed re-read keeps the rating read at lobby entry for that player.
- [x] T029 [US3] Frontend: `usePvpMatch.ts` item type (no `difficulty`, `image_url?`), `rated` /
  `unrated_reason`; `League.tsx` renders `QuestionImage` and the unrated notice (O-M6); i18n
  `league.unrated.dailyCap` and `league.historyReasons.daily_cap` in `es` and `en` (T018 green)
- [x] T030 [US3] `python scripts/db_sync_check.py` — both repositories in step — `✓ REPOS EN SYNC`.
- [x] T031 [US3] Docs: AGENTS.md R19 (the expectation read when the match is formed; `daily_cap`)
  and the Architecture map (`domain/pvp/`); spec.md § Code Scope gains the two domain modules

**Checkpoint**: US3 functional; T010–T018 green; delivery A's, L's and H's pins still green.

---

## Phase N: Traceability & Verification

- [x] T090 Fill § Traceability rows FR-030, FR-031, FR-032, FR-033, US3-AS1, US3-AS2, US3-AS3 with
  the tests above; mark delivery M `closed`
- [x] T091 Review assertion adequacy: US3-AS1 checks *both* who met and that the far student still
  waits; US3-AS2 checks the notice to both players *and* that no rating row moved; US3-AS3 checks
  band, unseen, image *and* the absence of `difficulty`; FR-033 checks the applied delta, not only
  the read
  Checked: US3-AS1 asserts who met (`pvp_matches` players) *and* that B gets no `game_start`;
  US3-AS2 asserts `rated: false` to both, 0 / `daily_cap` in `game_end`, both ratings at 1000
  and the history reason; US3-AS3 asserts the exact unseen in-band set, no practised item, the
  image path and the exact key set (no `difficulty`, no `correct_option`); FR-033 asserts the
  applied delta and both ratings, not only the shown 1100.
- [x] T092 Verification (AGENTS.md § Verify): full suite on both engines, `db_sync_check.py`,
  `pnpm run build`, Playwright `league.spec.ts`, `check_traceability.py`, black, flake8
  Recorded 2026-10-22: `pytest tests/ --ignore=tests/e2e` **2303 passed** (SQLite + PostgreSQL,
  none skipped); `db_sync_check.py` in sync; `pnpm run build` ok; Playwright **131 passed**
  (`league.spec.ts` 18); `check_traceability.py --run` PASS (1328 pytest cases, 96 Playwright);
  black 24.3.0 and flake8 clean.
- [x] T093 V1 check: the repositories and `src/domain/` are shared with V1; V1 has no League and
  calls none of the changed methods
  `src/interface/` (V1) calls no PvP method and imports nothing from `src/domain/pvp/`.

---

## Dependencies & Execution Order

- T000 → T001 → T002 (pins green) → T010–T018 written and failing → T020–T031 → T090–T093.
- T020 depends on T010; T021 on T011; T022 on T012; T023 on T013; T024 on T014 and T020; T025 on
  T015, T021 and T023; T027 on T016, T022 and T023;
  T028 on T017 and T024; T029 on T018; T030 after T023.

### Parallel Opportunities

T010–T018 are independent files or independent tests; T020–T023 can proceed in parallel.

## Notes

- Composition with F (approved, not merged): F's resume token on the lobby slot, `game_resume`'s
  items and `finish_pvp_match(…, reason=)` meet M's queue, safe items and `rated=`; whichever PR lands
  second merges them and keeps one signature.
- Delivery G adds its conditions to M's `eligible` predicate; until G, unrated players are placed at
  1000 (O-M10).
