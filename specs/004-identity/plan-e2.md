# Plan — spec 004, delivery E2: passwords, sessions and display names

**Spec**: [spec.md](spec.md) § Deliveries, E2 (US4, US5; FR-026 … FR-032) · **Branch**:
`004-identity-e2` · **Date**: 2026-10-14

E2 is `closed`. Part 1 covers the rules the owner approved as general product rules (P1, P3,
P6): password change, the security version that revokes sessions, the administrative reset and
teachers created by the admin. Part 2 covers display names (US3, FR-020 … FR-025, FR-033's
display-name part), built after the owner's answers of 2026-10-14 (N5, N11, N12, N14, N17) and
the split of the initial import into spec 009: nothing in E2 knows about identifications or about
where an account came from.

## Constitution Check (1.1.0)

| Principle | E2 part 1 |
|---|---|
| Dual database (R1) | Same methods, signatures and DDL in both repositories; `db_sync_check.py` passes; repository tests run on both engines |
| Additive migrations (R8) | Columns `security_version`, `must_change_password` (both `NOT NULL DEFAULT 0`), `created_by`, `display_name` (nullable); table `audit_account_events`. Existing accounts keep version 0, no forced change and no display name |
| Layers (R2) | The password rule, the name filter and the public name in `src/domain/identity.py`; persistence in the repositories; HTTP and WebSockets in `api/` |
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

## Design — part 2: display names

- **Name and filter** (FR-020, N17). `users.display_name`, stored trimmed with its spaces
  collapsed. The filter (`display_name_problem`) accepts 2 to 80 letters of any language, spaces,
  apostrophes and hyphens, and refuses whole words of a Spanish and English list of offensive or
  mocking words — and a few well-known mocking full names — compared without accents or letter
  case (ñ kept), also with repeated letters collapsed or the letters run together. Words that are
  also real names or surnames stay out of the list; the admin corrects what it misses. Its message
  never repeats the name.
- **Public name** (FR-021, FR-022, N5). The display name, else the username. The repositories
  select it as `COALESCE(display_name, username)` in the rows behind rankings, PvP history, the
  teacher's dashboard and procedure queue, and the teacher's exports, so the API never holds the
  username of a named student there. Ranking rows keep `username` for V1 (frozen, disconnected at
  the switch); the API drops it.
- **Who changes it** (FR-025, FR-033). `set_display_name(actor, account, name)` in both
  repositories: the student their own, an active admin any student's; the filter applies; a row
  `display_name_changed` is recorded in `audit_account_events` without the name. `PUT
  /api/student/display-name` and `PUT /api/admin/users/{id}/display-name`. Teachers and admins have
  no display name (not decided).
- **Registration** (FR-020, N11). With public registration open, a student needs an allowed name;
  a teacher registers as before.
- **What the API sends**. Rankings and the teacher's views carry `name`; the PvP rival is
  `{name, elo}`; the procedure queue carries `student_name`; the admin's users list carries
  `username` and `display_name`; `/me` and the session carry the account's own `display_name`.
- **Screens**. Registration asks students «Tu nombre»; `/mi-nombre` (student menu «Mi nombre»);
  rankings, league, teacher dashboard, groups and procedures show the name; the menus show the
  own name; the admin's users list shows both and corrects a student's name in place.

## Merge order

After E6 (LuisJRubioH/LevelUp-ELO#67), which it contains, and after LuisJRubioH/LevelUp-ELO#58
(LuisJRubioH/LevelUp-ELO#63 and LuisJRubioH/LevelUp-ELO#64 are merged).
