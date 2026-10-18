# Tasks — spec 004, delivery E6

**Plan**: [plan-e6.md](plan-e6.md). FR-090 … FR-095 are `[CHANGE]`: on the base branch a store
failure makes every limited route answer 500 and `/api/health` does not look at the limits, so
their tests fail there. FR-096 and US10-AS4 are `[AS-IS]`, pinned by
`test_insecure_production_configuration_is_rejected`. Written with the code (see plan-e6.md), so
every task is already done.

## Phase 1 — Tests (`tests/api/test_spec004_e6_limit_store.py`)

- [x] T001 [US10] Limits apply from memory with the same values once the store fails; the API's
  login limit and a degraded 200 health during an outage, with no address or password in it
  (FR-090, US10-AS1)
- [x] T002 [US10] No call reaches the store once its failure is known; one probe per interval;
  a real Redis client against a silent socket ends after one timeout and the next calls do not
  wait (FR-091, US10-AS1)
- [x] T003 [US10] Recovery carries memory counts over without a new allowance, including a key
  counted only during the outage; a failed probe keeps the fallback (FR-092, US10-AS2)
- [x] T004 [US10] One warning in, one out, for an outage of many requests, without the store's
  address (FR-093, US10-AS5)
- [x] T005 [US10] Health normal → degraded → normal (FR-094)
- [x] T006 [US10] Memory disabled (more than one process) or full: limited request 503 and health
  503 (FR-095, US10-AS3)
- [x] T007 The API's limiter sits behind the failover with the configured timeouts when a shared
  store is configured — guards the slowapi attributes it replaces (FR-090, FR-091)

## Phase 2 — Implementation

- [x] T008 Settings `RATE_LIMIT_STORAGE_CONNECT_TIMEOUT`, `RATE_LIMIT_STORAGE_TIMEOUT`,
  `RATE_LIMIT_STORAGE_PROBE_INTERVAL`, `RATE_LIMIT_FALLBACK_MAX_KEYS` (`api/config.py`)
- [x] T009 `FailoverStorage`, `LimitsUnavailable`, `use_failover_storage`, `limits_state`
  (`api/rate_limit.py`)
- [x] T010 `/api/health` limits state and the 503 handler (`api/main.py`)
- [x] T011 Real Redis check, by hand (plan-e6.md § Design)

## Phase 3 — Traceability and documents

- [x] T012 Fill E6's rows in spec.md § Traceability and mark E6 `closed`; decisions N9, N10
- [x] T013 `docs/transfer.md` § 3 and § 3.2 (from LuisJRubioH/LevelUp-ELO#60), `docs/arquitectura.md`
  § Observabilidad, `scripts/verify_deployment.py` (limits must be `normal` after the switch)
