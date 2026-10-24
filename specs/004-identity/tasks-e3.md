# Tasks — spec 004, delivery E3 (students created one by one, and the last day of access)

**Plan**: [plan-e3.md](plan-e3.md). FR-040, FR-043 … FR-052 are `[CHANGE]`: the base branch has no
student creation by the admin and no last day of access. Each test below was run on the unchanged
code first and failed — missing functions, method, column, endpoint or screen — then passed with
the implementation. One exception, noted at T005: the login screen already showed the server's
refusal, so its expiry message is new on the server, not on the screen.

## Tests

- [x] T001 Level and grade of a new student; the Colombian day; the inclusive last day; no last
  day never expires; a last day read only as a calendar date; the owner's message —
  `tests/unit/domain/test_spec004_e3_rules.py` (FR-040, FR-046 … FR-048, US7-AS1, US7-AS7)
- [x] T002 Both engines, repository: creation with group, course, level, grade, last day, forced
  change and audit; every refusal creates nothing; last day set, extended, removed and recorded,
  by the admin only; an abandoned match closes once without rating —
  `tests/integration/test_spec004_e3_accounts.py` (US6-AS1 … AS4, FR-040, FR-043, FR-044,
  FR-046, FR-050 … FR-052)
- [x] T003 Both engines, API: creation and first sign-in with the forced change; refusals; username
  in use; admin only; 30 per minute (3 in the test) — (US6-AS1 … AS5, FR-040, FR-043 … FR-045)
- [x] T004 Both engines, API: the last day itself signs in, the next day refuses with the message
  for the right password and the usual refusal for a wrong one; an open session's request,
  renewal and new socket are refused; data unchanged and access restored by extending; admin
  only; an account without a last day keeps working (US7-AS1 … AS4, US7-AS7, FR-046 … FR-050)
- [x] T005 Both engines, sockets and PvP: the sweep closes an expired account's socket with 4403,
  abandons its match and tells both players, an account in date keeps its socket; expiry and
  normal close at once end the match once (US7-AS2, US7-AS5, US7-AS6, FR-047, FR-051, FR-052)
- [x] T006 Screens — `frontend/e2e/spec004-e3-accounts.spec.ts`: the admin creates a student and
  sees the temporary password once; a refusal shows its reason; the admin sees, extends and
  removes a last day; sign-in shows the expiry message (passes on the unchanged screen: the
  change is the server's, T004); an open session that expires lands on the login with the
  message; a match closed by an expiry says so with +0

## Implementation

- [x] T007 `student_level_problem`, `colombia_today`, `parse_last_day`, `access_expired`,
  `ACCESS_EXPIRED_MESSAGE` in `src/domain/identity.py`
- [x] T008 `users.access_until`; `create_student_account`, `set_access_until`,
  `get_access_until_bulk`, `abandon_pvp_match` and `access_until` in the account rows, in both
  repositories (R1, R8); protocols
- [x] T009 Expiry in `authenticate_access_token`, sign-in (after the password, N7) and renewal
- [x] T010 `POST /api/admin/students` with its limit setting; `PUT
  /api/admin/users/{id}/access-until`; `access_until` and `access_expired` in the users list
- [x] T011 Close code 4403 for refused and swept sockets; `players_in_play`,
  `abandon_matches_of`; the 60 s sweep started and stopped with the app
- [x] T012 Screens: «Crear estudiante», «Último día» column, the login notice, the notifications
  socket ending the session, the league's cancelled match
- [x] T013 Earlier admin screen tests answer the new groups request (the creation form lists
  groups)
- [x] T014 Traceability: every E3 row filled, E3 `closed`; AGENTS.md R18, R19 and the `users` row
