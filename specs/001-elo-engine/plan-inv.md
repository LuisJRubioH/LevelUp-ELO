# Plan — spec 001, delivery INV: single-use invitations

**Spec**: [spec.md](spec.md) § Deliveries, INV (User Story 10; FR-028l, FR-028p … FR-028u) ·
**Branch**: `001-single-use-invitations` · **Date**: 2026-10-15

INV is `closed`. The owner decided on 2026-10-15 that an invitation serves one student, that the
teacher generates them, that unused ones expire and that today's reusable group codes stop working
(spec § Clarifications, Session 2026-10-15). The expiry period was not given: 30 days, as a server
setting, is the recommended default.

## Constitution Check (1.2.0)

| Principle | INV |
|---|---|
| Dual database (R1, IV) | Same four methods, signatures and DDL in both repositories; `db_sync_check.py` passes; every repository behaviour runs on both engines (`tests/integration/test_spec001_invitations.py`) |
| Additive migrations (R8) | New table `group_invitations` and its index, `CREATE … IF NOT EXISTS` on both engines. `groups.invite_code` is kept; V2 stops reading and writing it |
| Layers (R2, III) | Token alphabet, shape, normalisation, states and the order of refusals in `src/domain/invitations.py` (no I/O); the transaction in the repositories; the semillero-grade rule in `StudentService.enroll_by_invitation`; HTTP in `api/` |
| Concurrency (V) | Redemption is one transaction: PostgreSQL locks the student, then the invitation (`FOR UPDATE`), and consumes it with a conditional `UPDATE … RETURNING`; SQLite `BEGIN IMMEDIATE`. Two redemptions of one invitation: exactly one succeeds |
| Security (VI) | Tokens drawn with `secrets`; a teacher or admin outside the group gets 404, so the group is not revealed; a used invitation shows only the student's public name (spec 004 FR-023) |
| V1 frozen | V1 keeps `generate_group_invite_code`, `get_group_by_invite_code` and `invite_code` in `get_groups_by_teacher`, which it calls; `enroll_user` keeps its signature and behaviour (its writes moved to a helper the redemption shares). V1 startup: `tests/unit/interface/test_spec001_v1_smoke.py` |

## Design

- **Table** `group_invitations`: `id`, `group_id` (→ `groups`, `ON DELETE CASCADE`), `token` (`TEXT
  UNIQUE NOT NULL`, stored without the hyphen), `created_by`, `created_at`, `expires_at`,
  `used_by`, `used_at`, `revoked_at`; index on `group_id`. Timestamps as the files already store
  them (`TIMESTAMP`, written by the database clock: `NOW()` / `datetime('now')`), so expiry is
  always compared on the same clock.
- **Token** (FR-028p): 10 characters of `ABCDEFGHJKMNPQRSTUVWXYZ23456789` from `secrets.choice`
  (31¹⁰ ≈ 8 × 10¹⁴ tokens), shown `XXXXX-XXXXX`. A collision is drawn again (`INSERT OR IGNORE` /
  `ON CONFLICT (token) DO NOTHING`).
- **Repository** (both engines):
  `create_group_invitations(teacher_id, group_id, count, ttl_days)` → tokens, or None when the
  group is not this active, approved teacher's; `get_group_invitations(teacher_id, group_id)` →
  rows with `status`, `expires_at`, `used_at`, `used_by_name` = `COALESCE(display_name, username)`,
  or None; `revoke_group_invitation(teacher_id, invitation_id)` → `revoked` / `not_found` /
  `not_revocable`; `redeem_group_invitation(user_id, token)` → `{"status", "course_id",
  "group_id"}` with `ok`, `invalid`, `used`, `expired`, `no_course` or `already_member`. Only `ok`
  writes. Only the redemption is called by a service, so only it joins `IStudentRepository`.
- **Order of refusals** (`redemption_refusal`): what the invitation is (unknown or revoked or its
  teacher inactive → invalid; used; expired), then whether its group has a course, then whether the
  student is already in it. The semillero grade is checked by the service before the repository
  is called, so a refused student never consumes an invitation.
- **API**. Teacher: `POST /api/teacher/groups/{id}/invitations` `{count}` (1–50) → `{tokens,
  ttl_days}`; `GET /api/teacher/groups/{id}/invitations` → `{ttl_days, invitations}`; `DELETE
  /api/teacher/invitations/{id}` → 204 / 404 / 409. `POST …/invite-code` is removed and no group
  response carries `invite_code` (the dashboard drops it from the repository rows V1 still uses).
  Student: `POST /api/student/enroll-by-code` keeps its body `{invite_code}`; 404 invalid, 409 used,
  410 expired, 409 already a member, 400 no course, 403 no grade or not a student.
- **Setting**: `invitation_ttl_days: int = 30` in `api/config.py` (`INVITATION_TTL_DAYS`).
- **Screens**. Teacher → Grupos: the card's code chip becomes a pointer to the group's drawer,
  whose «Invitaciones» panel has a count (1–50), «Generar invitaciones», the hint «Cada código
  sirve para un solo estudiante y vence a los {ttl} días si nadie lo usa.» (TTL from the API) and
  the list — token, «Sin usar · vence dd/mm/aaaa» / «Usada por …» / «Vencida» / «Anulada», «Copiar»
  and «Anular» on unused ones. Each row marks its state with a token-coloured rule; new rows spring
  in (Framer Motion). Student → Cursos → Código de acceso: accepts the code with or without the
  hyphen and shows the API's message.

## Doubts recorded for the owner

- V1 (frozen) still generates and accepts reusable codes until it is disconnected; spec § Out of
  Scope.
- A non-student account redeeming an invitation is refused (403) so it cannot consume a token
  meant for a student — not in the owner's words, added to protect "single use".

## Merge order

After LuisJRubioH/LevelUp-ELO#68 (spec 004 E2, display names) and LuisJRubioH/LevelUp-ELO#65
(spec 001 deliveries), which this branch contains.
