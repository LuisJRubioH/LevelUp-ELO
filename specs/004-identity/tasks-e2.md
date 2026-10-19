# Tasks — spec 004, delivery E2 (passwords, sessions and display names)

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

## Part 2 — display names (US3, FR-020 … FR-025, FR-033)

`[CHANGE]`: the base branch has no display name. Each test below was run on the unchanged code
first and failed (missing column, method or field), then passed with the implementation.

- [x] T011 Name filter and public name, no I/O — `tests/unit/domain/test_spec004_display_names.py`
  (FR-020, FR-021, FR-022)
- [x] T012 Both engines: normalised name at registration, who may change it and its audit, the
  public name in the rows behind rankings, PvP history and the teacher's dashboard —
  `tests/integration/test_spec004_e2_display_names.py`
- [x] T013 API on both engines: classmates and teachers see the name and no username of a named
  student (ranking, PvP history and live match, dashboard, procedures, a student's ranking, CSV
  export); the admin sees both and changes any student's name; a student changes their own; a
  teacher or another student is refused; registration asks students for an allowed name
  (US3-AS1 … AS8, FR-023 … FR-025, FR-033, SC-005)
- [x] T014 Screens — `frontend/e2e/spec004-display-names.spec.ts`: ranking, league rival, teacher
  dashboard and procedures by name; registration field; `/mi-nombre`; the admin's list and
  correction
- [x] T015 `users.display_name` and `set_display_name` in both repositories (R1, R8); protocol
- [x] T016 Public name in the repository rows; `name`/`student_name` in the API; PvP rival by name
- [x] T017 Endpoints: registration, `PUT /api/student/display-name`, `PUT
  /api/admin/users/{id}/display-name`; `display_name` in `/me` and the session
- [x] T018 Screens: registration, `/mi-nombre`, menus, rankings, league, teacher views, admin list
- [x] T019 Earlier tests updated to the new contract: students register with a name; rankings,
  dashboard, procedures, PvP and exports read `name`
- [x] T020 Traceability: every E2 row filled, E2 `closed`
