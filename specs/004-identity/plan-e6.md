# Plan — spec 004, delivery E6: rate-limit store continuity

**Spec**: [spec.md](spec.md) § Deliveries, E6 (US10; FR-090 … FR-096) · **Branch**:
`004-identity-e6` · **Date**: 2026-10-13 · **Replaces**: the code of LuisJRubioH/LevelUp-ELO#59

Like E1's, this plan arrives with the code: the owner asked the agent to continue without them.
Values the spec left open are decisions N9 and N10, applied as recommendations.

## Constitution Check (1.1.0)

| Principle | E6 |
|---|---|
| Rate-limit store fallback (§ Validation) | Memory only after the shared store fails at runtime, same limits, only with `WEB_CONCURRENCY=1`; startup still refuses production without the shared store (FR-096, unchanged); timeouts configurable; no request waits during a sustained outage; recovery probed in a controlled way; no new allowance on return; one log line in, one out; a restart loses the memory counters (documented in `docs/transfer.md` § 3.2) |
| Readiness, not liveness | `/api/health`: 503 if the database fails or the limits cannot be applied; 200 with `limits` `normal`/`degraded`; no address or credential in the body or the logs |
| No silent swallowing | Every store failure either switches to memory (logged once) or, during recovery, keeps the fallback and is logged at debug level; nothing is dropped silently |
| Layers (R2) | All in `api/`; no repository, domain or schema change |
| Single process (R18) | The fallback is refused (requests 503) if more than one process serves |

## Design

`FailoverStorage` (`api/rate_limit.py`) is a `limits` storage placed in front of the shared one
when `RATE_LIMIT_STORAGE_URI` is not `memory://`. slowapi accepts only a URI, so after building
the `Limiter` its storage and fixed-window strategy are replaced (`use_failover_storage`); a test
guards those private attributes.

- **Normal**: every call goes to the shared store. Its client has
  `RATE_LIMIT_STORAGE_CONNECT_TIMEOUT` and `RATE_LIMIT_STORAGE_TIMEOUT` (0.5 s each) and no
  retries, so a failing call ends after one timeout (`redis://`, `rediss://` and their Valkey
  equivalents; another scheme keeps its client's defaults).
- **Entering degraded** (FR-090, FR-093): the first failure flips the state under a lock, logs one
  warning with the exception's class only (a Redis error can carry its address) and serves that
  call from memory.
- **Degraded** (FR-090, FR-091): counters in a dict `key → [count, expiry]` on a monotonic clock,
  same windows, at most `RATE_LIMIT_FALLBACK_MAX_KEYS` (50 000) live keys. No call reaches the
  store. A limited request or a health check whose turn comes, at most once per
  `RATE_LIMIT_STORAGE_PROBE_INTERVAL` (10 s), starts a daemon thread that probes the store, so no
  request waits on it.
- **Recovery** (FR-092, FR-093): if the probe's `check()` answers, under the same lock each live
  memory counter is added to the store with its remaining window (`INCRBY`, expiry set only if the
  key is new) and removed from memory; then the state flips back and one warning is logged. A
  failure halfway keeps the fallback; counters already carried are not carried twice. Requests
  arriving during the transfer wait on the lock, then go to the store.
- **Unavailable** (FR-095): memory full, or more than one process → `LimitsUnavailable`, answered
  503 with `Retry-After: 60` by an exception handler; `/api/health` answers 503.
- **Health** (FR-094): in normal state it pings the store (bounded by the timeouts); a failed ping
  enters the degraded state like a failed call. Body: `status` `ok`/`degraded`, `db`, `limits`,
  `version`. `scripts/verify_deployment.py` now requires `limits: normal` after the switch.

Checked against a real Redis (local `redis-server`, not in CI): stopped with the API running —
four logins took 0.01 s, health 200 `degraded`, one warning; restarted — one probe, four counters
carried over, health back to `normal`, and the account's next six attempts passed and the
seventh and eighth were refused (10 in all).

## Not in E6

- An external monitor that reads the health body (decision N8): the owner's operational step.
- Counting across processes during an outage: the fallback refuses instead (R18).

## Merge order

After E1 (LuisJRubioH/LevelUp-ELO#66), which it contains: same file, `api/rate_limit.py`. It also
contains LuisJRubioH/LevelUp-ELO#60 and rewrites its § 3.2 of `docs/transfer.md` for the code
after E1 and E6 (per-account sign-in, the fallback, the health body); merge #60 first or let this
pull request carry it.
