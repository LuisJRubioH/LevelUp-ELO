# ELO engine — as-is survey (reverse engineering input)

Read-only survey of `main @ cf88c55`, 2026-10-04. Input for `specs/001-elo-engine/spec.md`.
Each finding cites code; "Drift" = code and docs (CLAUDE.md) disagree.

## 1. Where things live

| Concern | File |
|---|---|
| Expected score, procedure delta, (unused) dynamic K | `src/domain/elo/model.py` |
| Rating + RD update | `src/domain/elo/uncertainty.py` (`RatingModel`) |
| Per-topic vector, global average | `src/domain/elo/vector_elo.py` |
| Item selection (ZDP + Fisher) | `src/domain/selector/item_selector.py` |
| Answer use case, item priority, item ELO update, badges | `src/application/services/student_service.py` |
| Atomic persistence, time validity, global refresh | `sqlite_repository.py` / `postgres_repository.py` (`save_answer_transaction`, `_set_topic_elo`, `_bump_topic_elo`) |
| Diagnostic baseline | `api/routers/student.py` ~L1030 → `set_topic_elo_baseline` |
| PvP deltas | `api/websocket/pvp.py` (`K = 24`) → `finish_pvp_match` |
| Teacher procedure delta | `procedure_elo_delta()` → `validate_procedure_submission` |
| Calibrator (display only) | `src/infrastructure/ml/calibration.py` |

## 2. Actual behaviour

**Student rating update** (per answer):
- `P = 1 / (1 + 10^((D − R)/400))`
- `ΔR = 32 × (RD/350) × (result − P)` — K is a fixed 32 scaled by RD.
- `RD' = max(30, RD × 0.95)`
- Defaults: R = 1000, RD = 350.

**Item update**: `D' = D + 32 × ((1 − result) − (1 − P))`. Item RD is read but never changed.

**Validity**: the attempt is always stored; rating and item difficulty move only if `3 s ≤ time_taken ≤ 600 s`.

**Single source of truth**: `student_topic_elo(user_id, topic)` holds the rating. `users.current_elo` = rounded average of the user's topic rows, refreshed on every write. `attempts` is a log.

**Writers of `student_topic_elo`**: answer (set), diagnostic baseline (set, only if no practice yet, floor 760), teacher procedure validation (bump `(score−50)×0.2`, once), PvP finish (bump, once per match, floor 0).

**Idempotency**: `request_id` unique per user; a replay returns without moving anything.

**Concurrency**: one transaction; `BEGIN IMMEDIATE` (SQLite) / `FOR UPDATE` users→items (Postgres).

**Selector**: priority unseen → failed-in-session with ≥3-question cooldown → historical; correct-in-session excluded. Pre-filter `D ∈ [R−250, R+250]`, then `P ∈ [0.40, 0.75]` expanded ±0.05 up to 10 steps, then random pick among candidates with ≥95 % of max `P(1−P)`. Pool empty and R ≥ 1800 → "mastery".

## 3. Findings

| # | Kind | Finding | Evidence |
|---|---|---|---|
| F1 | **Bug risk** | **The rating key is not consistent across writers.** V1 writes under the course *name*; V2 under item `topic` or `course_id`; procedure under item `topic`; PvP under `course_id`. One student can end up with several rows for the same course, and the global average counts all of them. `/stats` already carries a dedupe hack ("bug #7 QA mayo 2026"). | `student_view.py:385`, `student.py:166,252`, `finish_pvp_match`, `validate_procedure_submission` |
| F2 | Drift | Dynamic K (40/32/16/24) documented in CLAUDE.md is **not used** for students. `calculate_dynamic_k` and `update_elo` are dead (only an unused import in V1). | `model.py`, `student_view.py:21` |
| F3 | Inconsistency | Three different K values: answers 32×RD/350, PvP 24, frontend preview 32/24 by R<1400. The preview shows a delta the engine will not apply. | `uncertainty.py`, `pvp.py:28`, `Practice.tsx:27` |
| F4 | Inconsistency | PvP matchmaking and expected score use the **global** average, but the delta goes to the **course** topic. | `pvp.py:191`, `finish_pvp_match` |
| F5 | Data honesty | An invalid-time attempt stores `elo_after` as if the rating moved, and the API response reports that delta, but nothing changed. | `save_answer_transaction`, `student.py:227` |
| F6 | Dead param | `impact_modifier` survives in `VectorRating.update` and `cog_data`, always 1.0. | `vector_elo.py`, `student_service.py:138` |
| F7 | Drift | `elo/zdp.py` is documented but does not exist; the ±250 rating pre-filter is undocumented. | CLAUDE.md, `item_selector.py` |
| F8 | Duplication | Rank tables (16 levels) defined in ≥4 places. | `student_view.py`, `student.py`, `RankBadge.tsx`, `Stats.tsx` |
| F9 | Smell | `item_rd` round-trips but is never updated; item RD is effectively constant. | `student_service.py` compute |
| F10 | Smell | Badge errors are swallowed with bare `except Exception: pass`. | `student_service.py` |

## 4. Existing evidence (characterization tests)

46 tests across `tests/integration/test_elo_single_source.py`, `tests/unit/domain/test_elo_model.py`, `test_vector_elo.py`, `test_item_selector.py`; plus `test_repository_contracts.py`, `test_architecture_layers.py`. Not covered yet: F1 key consistency, F3 preview vs engine, F4 PvP rating source.
