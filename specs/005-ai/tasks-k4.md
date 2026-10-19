# Tasks — spec 005, delivery K4 (clean-up)

**Plan**: [plan-k4.md](plan-k4.md) (approved by the owner, 2026-10-19). FR-040 is `[CHANGE]`.

## Found while implementing

- `SYSTEM_AI_PROVIDER` has been unread since K1 (the key's prefix decides). It leaves the settings
  with `AI_KEY_STUDENT_ANALYSIS`. Both stay harmless if a host still sets them, because the
  settings ignore unknown variables. `docs/transfer.md` § 3 asks to remove them from the host.
- The legacy endpoint had no schema of its own; its rate limit (`rate_limit_review`) is the one
  `/student/procedure/analyze` uses, so it stays.
- `scripts/audit_production_readiness.py` no longer sets `AI_KEY_STUDENT_ANALYSIS`.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/api/test_spec005_k4_cleanup.py`: the legacy review endpoint answers 404 and is
  not in the API; no setting for a student analysis or a provider — FR-040

## Phase 2 — Implementation

- [x] T002 `api/routers/ai.py`: `POST /ai/review-procedure` removed
- [x] T003 `api/config.py`: `ai_key_student_analysis` and `system_ai_provider` removed
- [x] T004 `AGENTS.md` § AI integration rewritten from spec 005, covering:
  - the key's prefix and the models;
  - KatIA's guardrail and record;
  - the Groq-only review.

  `README.md` and `docs/transfer.md` § 3 updated. The R7 line on V1 keys stays until F-10.

## Phase 3 — Close

- [x] T005 Traceability: FR-040 filled; K4 `closed`. Checks: the full suite on both engines,
  black, flake8 and `check_traceability.py`.
