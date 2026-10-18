# Tasks — spec 004, delivery E1

**Plan**: [plan-e1.md](plan-e1.md). E1's requirements are `[CHANGE]` except FR-005 and FR-012,
`[AS-IS]` and pinned by tests that already pass on the base branch (`test_approve_teacher`,
`test_insecure_production_configuration_is_rejected`). On the base branch
(registration open, login limited per address) the tests of the closed default, the registration
setting and the account limits fail; the open-registration cases pin what stays as today. Written
with the code (see plan-e1.md), so every task is already done.

## Phase 1 — Tests that fail first

- [x] T001 [US1] Registration closed by default, refused on the server, no account created —
  `tests/integration/test_spec004_e1_registration.py::test_spec004_public_registration_is_closed_by_default`
  (US1-AS1, FR-001; both engines)
- [x] T002 [US1] Registration opens only through its setting; a teacher stays pending —
  `…::test_spec004_registration_opens_only_through_its_setting` (US1-AS3, FR-002, FR-005)
- [x] T003 [US1] The registration state is public; its own per-address limit leaves login alone —
  `tests/api/test_spec004_e1_login_limits.py::test_spec004_registration_state_is_public`,
  `…::test_spec004_registration_has_its_own_per_address_limit` (FR-003, FR-004, US1-AS4)
- [x] T004 [US1] The login screen offers sign-up only while it is open —
  `frontend/e2e/auth.spec.ts`, two cases (US1-AS2, US1-AS3, FR-003)
- [x] T005 [US2] 30 students on one address sign in; the 11th attempt on one account is refused by
  username or email; 301st overall refused —
  `…::test_spec004_thirty_students_on_one_address_sign_in`,
  `…::test_spec004_the_eleventh_attempt_on_one_account_is_refused`,
  `…::test_spec004_the_global_ceiling_refuses_every_extra_attempt` (US2-AS1 … AS3, FR-006 … FR-008)
- [x] T006 [US2] Identical refusal for an unknown identifier; settings drive both limits; no
  readable identifier in the store or the logs —
  `…::test_spec004_a_refusal_does_not_reveal_whether_the_account_exists`,
  `…::test_spec004_login_limits_follow_their_settings`,
  `…::test_spec004_limits_keep_no_readable_identifier` (US2-AS4, US2-AS5, FR-009 … FR-011)
- [x] T007 [US2] `login_account_id` on both engines: username, email, inactive, unknown —
  `tests/integration/test_spec004_e1_registration.py::test_spec004_login_account_id_names_one_active_account`
  (FR-006)

## Phase 2 — Implementation

- [x] T008 Settings `PUBLIC_REGISTRATION_ENABLED`, `RATE_LIMIT_LOGIN_ACCOUNT`,
  `RATE_LIMIT_LOGIN_GLOBAL`, `RATE_LIMIT_REGISTER`; remove `RATE_LIMIT_AUTH` (`api/config.py`)
- [x] T009 `login_account_id` in both repositories; `python scripts/db_sync_check.py`
- [x] T010 `login_limit_key`, `login_allowed` (`api/rate_limit.py`); login and register in
  `api/routers/auth.py`; `GET /api/auth/registration`
- [x] T011 Login screen (`frontend/src/pages/Login.tsx`, `frontend/src/api/auth.ts`); default mock
  of `/api/auth/registration` in `frontend/e2e/fixtures.ts`
- [x] T012 Existing tests that relied on open registration or on the per-address login limit:
  `tests/api/test_auth.py`, `tests/api/test_student.py`, `tests/api/test_rate_limit.py`,
  `tests/integration/test_postgres_production_guards.py`

## Phase 3 — Traceability and documents

- [x] T013 Fill E1's rows in spec.md § Traceability and mark E1 `closed`;
  `python scripts/check_traceability.py --run`
- [x] T014 `docs/transfer.md` § 3, `.env.example`, `docs/checklist-apertura.md`: new variables, and
  that production's open sign-up closes with the merge
