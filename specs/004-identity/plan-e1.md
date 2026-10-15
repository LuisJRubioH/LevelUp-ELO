# Plan — spec 004, delivery E1: closed registration and login limits

**Spec**: [spec.md](spec.md) § Deliveries, E1 (US1, US2; FR-001 … FR-012) · **Branch**:
`004-identity-e1` · **Date**: 2026-10-13

This plan arrives with the code instead of in a docs pull request before it: the owner asked the
agent to continue without them ("sigue sin mi"). Its decisions are listed so they can be reviewed
before the merge; none changes the spec.

## Constitution Check (1.1.0)

| Principle | E1 |
|---|---|
| Layers (R2) | Limits and the setting live in `api/`; the repositories add one read (`login_account_id`). No rule in `domain/`, nothing in `application/` |
| Dual database (R1) | `login_account_id` in both repositories, same signature and query; `db_sync_check.py` passes; tested on both engines |
| Additive migrations (R8) | No schema change |
| Secrets (R7) | No key or identifier in the limit store: an identifier that names no account is kept as a SHA-256 digest (FR-011) |
| Single process (R18) | Counters live in the limit store (`RATE_LIMIT_STORAGE_URI`), shared like the existing ones |
| Tests before done | Every E1 row of § Traceability names a passing test; `PENDING` remains only in E2–E6 |

## Design

- **Registration setting** (FR-001 … FR-003). `PUBLIC_REGISTRATION_ENABLED` (`api/config.py`,
  default `false`). `POST /api/auth/register` answers 403 while it is off, before the repository is
  called. `GET /api/auth/registration` returns `{"enabled": …}`; the login screen shows the
  sign-up tab and switch only when it is `true`, and treats an error as closed.
- **Registration limit** (FR-004). Its own per-address limit, `RATE_LIMIT_REGISTER` = 20/minute
  (decision N2, the value `RATE_LIMIT_AUTH` had). Read at each request (slowapi accepts a
  callable), so a test or a restart with another value takes effect.
- **Login limits** (FR-006 … FR-011). No per-address limit on login any more: the slowapi
  decorator from LuisJRubioH/LevelUp-ELO#33 is removed. Each attempt is counted twice in the same
  store, with the fixed-window strategy slowapi already uses (a block ends with its minute):
  - globally, under `login/all`, against `RATE_LIMIT_LOGIN_GLOBAL` (300/minute);
  - for the account, under `login/account:<id>` when the identifier is exactly the username or the
    email of an active account (`login_account_id`, the same match as `login_user`), otherwise under
    `login/identifier:<sha256 of the trimmed, case-folded identifier>`; against
    `RATE_LIMIT_LOGIN_ACCOUNT` (10/minute). Decision N1.
  The check runs before the password is verified, so the 11th attempt is refused with the right
  password too. Both limits answer the same 429, `Retry-After: 60`, whether the account exists
  (FR-010).
- **Removed setting**. `RATE_LIMIT_AUTH` no longer exists; `docs/transfer.md` § 3 lists the new
  variables and warns that production's open sign-up closes with the merge.

## Not in E1

- Teachers created by the administrator (P1): their forced password change is E2's mechanism
  (decision N3). Until then a teacher signs up while the setting is on and is approved, as today.
- The limit store's fallback when Redis fails: E6.

## Merge order

After LuisJRubioH/LevelUp-ELO#63 (constitution 1.1.0), LuisJRubioH/LevelUp-ELO#64 (checker with
deliveries) and LuisJRubioH/LevelUp-ELO#58 (spec 004). It contains LuisJRubioH/LevelUp-ELO#33,
whose AI limits it keeps and whose login-per-address limit it replaces. If
LuisJRubioH/LevelUp-ELO#60 lands first, its § 3.2 still describes `RATE_LIMIT_AUTH` for login;
E6 or a follow-up updates that paragraph.
