# Plan — spec 004, delivery E3: students created one by one, and the last day of access

**Spec**: [spec.md](spec.md) § Deliveries, E3 (US6, US7; FR-040, FR-043 … FR-052) · **Branch**:
`004-identity-e3` · **Date**: 2026-10-15

E3 is `closed`. It builds on E2 (forced password change, security version, socket registry,
display names) and follows the owner's decisions N7, N13 and N15 (2026-10-14). Nothing in it knows
about identifications or the initial import (spec 009): the import will reuse the creation and the
last day of access.

## Constitution Check (1.1.0)

| Principle | E3 |
|---|---|
| Dual database (R1) | Same methods, signatures and DDL in both repositories; `db_sync_check.py` passes; repository and API tests run on both engines |
| Additive migrations (R8) | One nullable column, `users.access_until` (`DATE` on PostgreSQL, `TEXT` `YYYY-MM-DD` on SQLite). Every existing account gets NULL: it never expires (US7-AS7) |
| Layers (R2) | Level and grade, the Colombian day and the expiry rule in `src/domain/identity.py`, no I/O; persistence in the repositories; HTTP, sockets and the sweep in `api/` |
| Secrets (R7, VI) | The temporary password is shown once in the admin's response; never stored readable, never in the audit or the logs |
| Single process (R18) | The sweep reads the in-process socket registry and PvP state, like revocation; it calls the repository through `asyncio.to_thread` and never under the PvP `_lock` (R17) |
| PvP close (R19) | An expiry closes a match through the same `match.finished` guard and the same `status='active'` condition as the normal close |

## Design

- **Creation** (FR-040, FR-043, FR-044, N13, N15). `POST /api/admin/students` — admin only — with
  username (the account rule of E2: 3 to 50 letters, digits, `. _ - @`), display name (E2's
  filter), an existing group, level and grade, and an optional last day. `create_student_account`
  checks it all and, in one transaction, creates the approved student with a random 12-character
  temporary password and a forced change (FR-030), `created_by`, the group (`users.group_id`) and
  the enrolment in the group's course when it has one, and the audit row `student_created`. Joining
  the group works like an invitation code (spec 001 FR-028l): any level, never a group created by
  the creation. A refusal creates nothing. Level and grade: semillero needs a grade from 6.º to
  11.º; the other levels take none («No aplica») — `student_level_problem`, never guessed. A last
  day already past is refused: the student could never sign in.
- **Limit** (FR-045, P12). `rate_limit_admin_creations = "30/minute"`, per admin (the limiter's key
  is the verified account), checked after the role: a teacher's refused attempt never counts.
- **Last day** (FR-046, FR-050). `users.access_until`, inclusive, read in Colombian time (UTC−5
  all year, `colombia_today`). `PUT /api/admin/users/{id}/access-until` sets, changes, extends or
  removes it for a student or a teacher (admins have none); each change adds `access_until_changed`
  to the audit with the new day. A day already past closes the account's open sockets at once.
  The admin's users list shows the day and whether it has passed.
- **Expiry** (FR-047, FR-048, N7). From 00:00 of the next Colombian day (`access_expired`):
  - Sign-in with the right password answers 403 with the owner's message (P7); with a wrong
    password, the usual 401 — the message never tells a stranger the account exists.
  - Every authenticated request and WebSocket (`authenticate_access_token`) and every renewal
    answers 401 with the message. A socket refused this way closes with code 4403.
  - An open socket that authenticated before is closed by a sweep every 60 s
    (`api/websocket/expiry.py`, started with the app): it reads the last day of every connected
    account and of every PvP player in one query, abandons their matches, then closes their
    sockets with 4403.
- **Data kept** (FR-049). Expiry changes nothing in the account or its academic data; extending
  the day restores access with all of it. Nothing is deleted.
- **PvP** (FR-051, FR-052, P15). `abandon_matches_of(user)` takes each of the player's matches
  under the same guard as `_finish_match`: whoever sets `match.finished` first decides. An abandon
  marks the row `abandoned` with zero deltas and reason `account_expired` (`abandon_pvp_match`,
  `WHERE status='active'`), keeps the saved answers and sends both players `game_end` with
  `abandoned: true`, `reason: "account_expired"`, `elo_delta: 0`. A match whose normal close
  started first keeps its result; the sweep waits until both players have it before closing the
  socket.
- **Screens**.
  - The admin's users page gets a «Crear estudiante» form: username, display name, group, level,
    grade only for semillero («No aplica» otherwise) and an optional last day. The temporary
    password is shown once, as for teachers. A «Último día» column shows the day (dd/mm/aaaa),
    «vencida» when it passed and «sin límite» when there is none, with an inline change and
    «Quitar límite».
  - Sign-in shows the message from the server. When an open session ends because the renewal
    refuses an expired account, or a notifications socket closes with 4403, the login screen shows
    it.
  - The league shows «Partida cancelada» with the reason and +0.

## Merge order

After E2 (LuisJRubioH/LevelUp-ELO#68), which it contains, and not before E2 is in production
(§ Deliveries). E5's same-origin renewal will carry the expiry check unchanged: it reuses the
refresh endpoint.
