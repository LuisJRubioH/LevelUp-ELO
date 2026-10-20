# Plan — spec 007, delivery H: the match history and a close that fails

**Spec**: [spec.md](spec.md) § Deliveries, H (US6; FR-060, FR-061) · **Branch**: `007-h`, from
`redesign` · **Date**: 2026-10-20 · **Status**: draft for the owner's approval

## Summary

Today the history lists only matches with `status = 'finished'`, up to 20 rows, while the screen
shows 5; an abandoned match (orphan sweep, and soon E3's expired account) never appears, and a
match whose close fails to persist stays `active` until the sweep closes it ten minutes later as a
plain `abandoned` row, still invisible. Delivery H lists every closed match with its subject and
reason, sends only the rows the screen shows, and retries a failing close before recording it as
`not_saved`.

## Constitution Check (1.2.0)

| Principle | H |
|---|---|
| Security (VI) | the history stays the student's own; no new field reveals the opponent's rating or an item |
| One source of truth (II) | the row count is one server constant; the screen shows what it gets |
| Layers (III) | the reason is a stored value read by the repository; the shown delta stays in `RatingReadService` |
| Dual database (IV, R1) | both repositories change together; `db_sync_check.py`; tests on both engines |
| Schema (R8) | **no schema change**: the reason uses the existing `elo_reason_p1/p2` columns, as E3 (#73) already does for an expired account |
| Ratings (R15, R19) | a `not_saved` or orphaned match changes no rating; nothing is rebuilt from attempts |
| Async (R17) | the retries run in threads with `asyncio.sleep` between them, never under `_lock` |

## Design

### FR-060 — every closed match, with subject and reason (US6-AS1)

- `get_pvp_history(user_id, limit)` (both repositories) returns `status IN ('finished',
  'abandoned')` — `active` stays out — newest first by `finished_at`, joined to `courses` for the
  subject's name. Each row adds `status`, `course_name` and `reason`: the student's own
  `elo_reason_p1/p2` (`no_rated_topics`, `not_saved`, `orphaned`, E3's `account_expired`; NULL for
  an ordinary finished match or an abandoned row from before H).
- **Rows sent = rows shown**: `PVP_HISTORY_ROWS = 5`, used by the endpoint; the screen stops
  slicing and renders what it receives.
- The orphan sweep (`expire_stale_pvp_matches`, both repositories) now also writes
  `elo_delta_* = 0` and `elo_reason_* = 'orphaned'`, so its rows say why.
- **Screen** (`League.tsx` `HistoryPanel`): each row shows the subject; an abandoned row shows a
  neutral tag and its reason from i18n (`league.historyReasons.*`, with a fallback for a NULL
  reason) instead of won/lost; the delta keeps the server's `elo_delta_display` («—» when none).

### FR-061 — a close that fails (US6-AS2)

- `_close_match` calls `repo.finish_pvp_match` up to **4 times: the first try and 3 retries**,
  waiting 0.5 s, 1 s and 2 s between them (3.5 s in all — "within a few seconds"). The delays are
  a module constant so tests can shorten them.
- If every try fails: `repo.abandon_pvp_match(match_id, "not_saved")` (both repositories) closes
  the row as `abandoned` with `elo_delta_* = 0` and the reason, only while it is still `active`
  (idempotent, as `finish_pvp_match`), and changes no rating. **E3 (#73) adds the same method with
  the same signature** for an expired account; whichever lands second keeps one copy.
- If even that write fails (the database is down), the row stays `active` and the sweep closes it
  later as `orphaned` — no rating moves either way.
- `game_end` keeps reporting `elo_reason = "not_applied"` with 0, as spec 001 FR-029c pins
  (`test_spec001_game_end_reports_not_applied_when_persistence_fails`): it describes what happened
  to the rating at that moment; the history then names the stored reason.

## Tests (written first; each fails on today's code)

| Test | Proves | Where |
|---|---|---|
| `test_spec007_history_lists_finished_abandoned_and_not_saved` | FR-060, US6-AS1: three closed matches appear with subject and reason; an active one does not | `tests/integration/test_spec007_h_history.py` (both engines) |
| `test_spec007_history_sends_only_the_rows_shown` | FR-060: seven closed matches → the newest 5 | same file |
| `test_spec007_the_sweep_records_why` | FR-060: an orphan closed by the sweep carries `orphaned` and 0 | same file |
| `test_spec007_a_failing_close_is_retried_then_recorded_not_saved` | FR-061, US6-AS2: `finish_pvp_match` fails every time → 4 tries, row `abandoned`/`not_saved`, no rating changes, in both players' history | same file (uvicorn, a real match) |
| `test_spec007_a_close_that_succeeds_on_retry_finishes_normally` | FR-061: fails once, then succeeds → `finished` with the applied deltas | same file |
| `test_spec007_abandon_is_idempotent_and_skips_a_finished_match` | FR-061 | same file |
| `/api/student/pvp/history` returns at most 5 rows with `status`, `course_name`, `reason` | FR-060 | `tests/api/test_pvp.py` |
| e2e «el historial muestra partidas abandonadas y no guardadas con su materia» | US6-AS1 on screen | `frontend/e2e/league.spec.ts` |

Delivery A's pins stay green, including spec 001's `not_applied` test. **Traceability rows to
fill:** FR-060, FR-061, US6-AS1, US6-AS2 (delivery H → closed).

## Risks

- **A slow close**: the worst case adds 3.5 s before `game_end` reaches the players; the screen
  already waits for it.
- **Old abandoned rows** (before H) have no reason: shown with the fallback text.
- **Conflict with E3 (#73)** on `abandon_pvp_match` and on the history's abandoned rows: same
  storage pattern, resolved at merge.

## Decisions for the owner

- **O-H1 — rows shown: 5?** The screen shows 5 today. **Recommended: 5**, the server sends exactly
  those.
- **O-H2 — retry timing: 0.5 s, 1 s, 2 s?** Three retries within 3.5 s. **Recommended: yes.**
- **O-H3 — `game_end` keeps `not_applied`** (spec 001's pinned wording) while the history shows
  `not_saved`. **Recommended: yes** — renaming it would amend spec 001 for no visible gain.
