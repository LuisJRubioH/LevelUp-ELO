# Tasks — spec 004, delivery E2 (part 1: passwords and sessions)

**Plan**: [plan-e2.md](plan-e2.md). FR-026 … FR-032 are `[CHANGE]`: the base branch has no
password change, reset, teacher creation or security version, so every test below fails there.
Written with the code (the owner asked the agent to continue without them), so the tasks are done.

## Tests

- [x] T001 Change, keep this session, refuse a wrong or short password, count attempts against the
  account limit; tokens from before E2 keep working until the version advances —
  `tests/api/test_spec004_e2_passwords.py` (US4-AS1 … AS3, FR-026 … FR-028)
- [x] T002 Another session's access token, renewal and open WebSocket end at once (US4-AS2)
- [x] T003 Admin reset for a student and a teacher: temporary password, every session ends, only
  the change is allowed until done; teacher creation; duplicate username; audit without the
  password; non-admins refused (US5-AS1 … AS4, FR-029 … FR-032)
- [x] T004 Repository on both engines: version, hash, reset, creation, audit, additive migration —
  `tests/integration/test_spec004_e2_accounts.py`
- [x] T005 Screens: forced change after sign-in, the API's 403 sends to the change, voluntary change
  from the menu, admin reset and teacher creation showing the temporary password once —
  `frontend/e2e/spec004-passwords.spec.ts`

## Implementation

- [x] T006 Columns, audit table and account methods in both repositories; protocols
- [x] T007 Security version in tokens and checks; forced-change gate; `POST /api/auth/password`
- [x] T008 Admin endpoints: reset, create teacher, account audit, students and teachers listed
- [x] T009 WebSocket registry closing an account's sockets on revocation
- [x] T010 Screens: `/cambiar-contrasena`, route gate, menu links, admin users and audit

## Still open in E2

- [ ] US3, FR-020 … FR-025 and the display-name part of FR-033 — waiting on the owner
