# Plan — spec 004, delivery E2 (part 1): passwords and sessions

**Spec**: [spec.md](spec.md) § Deliveries, E2 (US4, US5; FR-026 … FR-032) · **Branch**:
`004-identity-e2` · **Date**: 2026-10-14

E2 stays `in progress`. This part covers the rules the owner approved as general product rules
(P1, P3, P6): password change, the security version that revokes sessions, the administrative
reset and teachers created by the admin. Display names and who sees an identification (US3,
FR-020 … FR-025, FR-033's display-name part) wait on the owner's answers about which decisions
belong only to the initial import (2026-10-14, questions A–E); nothing here assumes them.

## Constitution Check (1.1.0)

| Principle | E2 part 1 |
|---|---|
| Dual database (R1) | Same methods, signatures and DDL in both repositories; `db_sync_check.py` passes; repository tests run on both engines |
| Additive migrations (R8) | Columns `security_version`, `must_change_password` (both `NOT NULL DEFAULT 0`), `created_by`; table `audit_account_events`. Existing accounts keep version 0 and no forced change |
| Layers (R2) | The password rule in `src/domain/identity.py`; persistence in the repositories; HTTP and WebSockets in `api/` |
| Secrets (R7, VI) | Passwords only as Argon2id hashes; the temporary password appears once in the admin's response, never in the database, the audit or the logs |
| Single process (R18) | Open WebSockets are closed from an in-process registry, like the rooms and the lobby |

## Design

- **Security version** (FR-027). Access and refresh tokens carry `sv`. Every authenticated request
  (`authenticate_access_token`, shared by REST and WebSockets) and every renewal compares it with
  the account's version and answers 401 when it differs. A token without `sv` was issued before E2
  and counts as version 0, so existing sessions survive the deployment.
- **Password change** (FR-026, FR-028). `POST /api/auth/password` with the current password and
  a new one of 6 characters or more after trimming. It counts against the account's sign-in limit
  (FR-006), replaces the hash, advances the version, closes the account's open WebSockets and
  returns new credentials for this session. No length rule in the request schema: a 422 would
  echo the password back.
- **Forced change** (FR-030). `must_change_password` is set by a reset or a teacher creation.
  While it is set, every endpoint and WebSocket answers 403 except `/api/auth/me` and
  `/api/auth/password`; the screen sends the user to `/cambiar-contrasena`.
- **Admin reset** (FR-029). `POST /api/admin/users/{id}/reset-password`, students and teachers
  only: a 12-character random temporary password (no look-alike characters), forced change, new
  version, open sockets closed, audit row `password_reset`. Shown once on the admin's screen.
- **Teachers created by the admin** (FR-031, P1). `POST /api/admin/teachers` with a username and an
  optional email: approved, temporary password, forced change, `created_by`, audit row
  `teacher_created`. No display name is asked for (question A is open).
- **Audit** (FR-029, FR-031). `GET /api/admin/account-audit`: operation, account, admin, time; no
  password column exists.
- **Screens**. `/cambiar-contrasena` (forced or voluntary, reachable from each panel's menu); the
  admin's users list shows students and teachers with «Restablecer contraseña» and a «Crear
  docente» form; the audit page lists account operations.

## Not in this part

US3 and FR-020 … FR-025 (display names, alias, who sees the identification), and the display-name
part of FR-033: they wait on the owner (2026-10-14).

## Merge order

After E6 (LuisJRubioH/LevelUp-ELO#67), which it contains, and after LuisJRubioH/LevelUp-ELO#63,
LuisJRubioH/LevelUp-ELO#64 and LuisJRubioH/LevelUp-ELO#58.
