# Tasks — spec 001, delivery INV (single-use invitations)

**Plan**: [plan-inv.md](plan-inv.md). FR-028l (amended) and FR-028p … FR-028u are `[CHANGE]`: the
base branch has one reusable code per group, so every test below was run on the unchanged code
first and failed (missing module, table, method, endpoint or screen), then passed with the
implementation.

## Tests

- [x] T001 Token alphabet, length, shape, normalisation, count bounds, states and order of refusals,
  no I/O — `tests/unit/domain/test_spec001_invitations.py` (FR-028p … FR-028t)
- [x] T002 Both engines, through the API: generation, expiry from the setting, count bounds,
  collision redrawn (US10-AS1, FR-028p) — `tests/integration/test_spec001_invitations.py`
- [x] T003 Both engines: redemption enrols with the group and outside the catalogue; used, expired,
  revoked and the old group code refused; nothing consumed for a gradeless semillero, a member, a
  group without course or a non-student; the teacher sees the public name (US10-AS2 … AS6, AS8,
  AS9, FR-028l, FR-028q … FR-028u)
- [x] T004 Both engines: two students at the same moment → exactly one enrolment; one student with
  two invitations at once → one used (US10-AS7, FR-028q)
- [x] T005 Both engines and API: only the group's teacher creates, lists and revokes; another
  teacher and an admin get 404, a student 403 (US10-AS10, FR-028p, FR-028t)
- [x] T006 Additive migration on both engines; `groups.invite_code` kept (FR-028u)
- [x] T007 Screens — `frontend/e2e/spec001-invitations.spec.ts`: the teacher generates, sees every
  state, copies and revokes; a student redeems with or without the hyphen and sees «Este código ya
  fue usado…»; `frontend/e2e/teacher-load-errors.spec.ts`: a failed generation or list is said
- [x] T008 Earlier tests moved to the new flow, coverage kept: `test_spec001_catalogue.py`,
  `test_enrol_joins_no_group.py`, `test_teacher_student_scope.py`,
  `test_postgres_production_guards.py`, `tests/api/test_teacher.py`,
  `tests/api/test_teacher_resource_access.py`; `scripts/audit_production_readiness.py` probes the
  new endpoints

## Implementation

- [x] T009 `src/domain/invitations.py`
- [x] T010 `group_invitations` and the four methods in both repositories (R1, R8); `enroll_user`
  shares its writes with the redemption; `redeem_group_invitation` in `IStudentRepository`
- [x] T011 `StudentService.enroll_by_invitation(user_id, code)`: grade first, then the repository
- [x] T012 `invitation_ttl_days` setting; teacher endpoints; `enroll-by-code` statuses; no
  `invite_code` in group responses; `POST …/invite-code` removed
- [x] T013 Screens: the «Invitaciones» panel in the group drawer; the student's code input
- [x] T014 Traceability: every INV row filled, INV `closed`; AGENTS.md § Database row
