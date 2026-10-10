# Identity & access — as-is survey (spec 004 input)

Read-only survey of `redesign @ 1d6fcf6`, 2026-10-10. Input for `specs/004-identity/spec.md`
(roadmap: JWT/refresh, roles, teacher approval, groups, admin, test users, changing a student's
grade; it takes over spec 001 FR-028m, the registration and enrolment rules). Under the roadmap's
lean scope, spec 004 is written the first time a feature touches the area. This survey is meant
to be ready for that moment. The likely first touch is giving a grade to grade-less semillero
accounts (F-1) or promoting a student.

Each finding cites code at that commit (`S` = `src/infrastructure/persistence/sqlite_repository.py`,
`P` = `src/infrastructure/persistence/postgres_repository.py`, `FE/` = `frontend/src/`).

How each finding was checked:
- **Verified**: read in the code.
- **Reproduced**: run against a throwaway local API (SQLite, through the test client or `uvicorn`)
  or a local PostgreSQL 16.
- **Inferred**: reasoned from the code, not run.

Nothing here was run against production. Security-sensitive details are shared with the owner
directly, not in this repository.

## 1. Where things live

| Concern | File |
|---|---|
| Login, registration, refresh, logout, profile | `api/routers/auth.py` |
| Tokens, current user, role check | `api/dependencies.py:63-165` |
| Request schemas | `api/schemas/auth.py` |
| Rate limits | `api/rate_limit.py`, `api/config.py:60-65` |
| Production start guard | `api/config.py:78-102` (`validate_runtime`) |
| Password hashing | `src/infrastructure/security/hashing_service.py` |
| Accounts | `register_user` P:1461 S:1114 · `login_user` P:1540 S:1194 · `get_user_by_id` P:1513 S:1170 |
| Admin API | `api/routers/admin.py` (whole router requires `admin`, :26) |
| Admin repository methods | deactivate / reactivate / approve / reject: P:2449-2488, S:2053-2081 · students list P:2510 S:2096 · audit P:1924 S:1591 |
| Groups and invitations | `api/routers/teacher.py:96-146` · `create_group` P:2541 S:2118 · `generate_group_invite_code` P:2663 S:2236 · `get_group_by_invite_code` P:2684 S:2254 · `delete_group` P:2736 S:2298 · `change_student_group` P:3235 S:2770 |
| Enrolment | `api/routers/student.py:317-376` · `student_service.py:304-337` · `enroll_user` P:3721 S:3131 |
| Teacher's access to a student | `api/routers/teacher.py:57-69` (`_require_teacher_group`, `_require_teacher_student`) |
| Seeds | `_seed_admin` P:1284 S:968 · `_seed_demo_data` P:1325 S:995 · `_seed_test_students` P:3485, `src/infrastructure/persistence/seed_test_students.py` |
| WebSocket authentication | `api/websocket/notifications.py:63-103`, `api/websocket/pvp.py:180-195` |
| Session in the browser | `FE/stores/authStore.ts`, `FE/api/client.ts:39-141`, `FE/App.tsx:110-153`, `FE/pages/Login.tsx` |
| Admin screens | `FE/pages/Admin/{Users,Groups,Reports,Audit}.tsx`; client in `FE/api/teacher.ts:311-339` |
| V1 (frozen) | `src/interface/streamlit/views/{auth_view,admin_view}.py`, `state.py`; sessions P:4230-4278 S:3617-3647 |

## 2. Actual behaviour

**Accounts.** There are three roles: `student`, `teacher` and `admin`. Registration through the API
accepts:
- a username of 3–50 characters, with no other rule;
- a password of at least 6 characters after trimming (the untrimmed value is hashed);
- the role `student` (default) or `teacher`;
- an optional level from the four;
- a grade, required for semillero (FR-028m);
- an optional email of up to 254 characters, which is trimmed, checked against a simple regex and
  must be unique.

What a new account looks like:
- Teachers start with `approved = 0`; students start approved.
- Nobody joins a group at registration. The sign-up screen logs the new student in and, if a class
  code was typed, tries `enroll-by-code` and ignores any error (`FE/pages/Login.tsx:229-237`).
- Admins cannot register. One admin is created from `ADMIN_USER` / `ADMIN_PASSWORD` when missing;
  an existing admin is never updated (`_seed_admin`).

**Login.** The login field matches the username or the email exactly, among active accounts.
- Passwords are Argon2id (passlib: 64 MiB, `t = 2`, `p = 4`). A legacy SHA-256 hash is accepted once
  and rewritten to Argon2id.
- A wrong password and an inactive account both answer 401 with the same message.
- An unapproved teacher gets 403 «pendiente de aprobación».
- Login and registration are limited to `RATE_LIMIT_AUTH` (20/minute) per origin.

**Tokens.**
- **Access token:** an HS256 JWT valid 15 minutes, carrying `sub`, `username`, `role` and
  `type = access`. It is returned in the body and kept by the SPA in localStorage (`levelup-auth`)
  together with the user and their role.
- **Refresh token:** a JWT valid 7 days, carrying `sub`, `type = refresh` and `jti`. It travels in
  an HttpOnly, Secure, `SameSite=None` cookie on path `/api/auth`. `/refresh` also accepts it in the
  body. Each refresh issues a new pair.
- **Logout** deletes the cookie.
- **Every authenticated request** re-reads the account (`dependencies.py:134-148`):
  - inactive → 401;
  - unapproved teacher → 403.

  WebSockets do the same with the token sent in their first message.
- **Production** refuses to start with the default or a short `JWT_SECRET_KEY`, and also with
  localhost CORS, in-memory rate limiting or more than one worker.

**Roles at the API.**
- `/admin/*` requires `admin`.
- `/teacher/*` requires `teacher` or `admin`; an admin acts as a teacher with their own groups.
- `/student/*`, `/ai/*` and `/auth/me` require authentication only.
- PvP requires the `student` role and enrolment in the course.
- Notification rooms are authorised per role and user.
- A teacher sees a student (report, history, KatIA log, AI analysis, ranking) only when the
  student's main group is one of the teacher's groups. The dashboard lists more (§ 3, I7; fixed in
  #36).

**Session in the browser.**
- The role comes from the persisted store. `/api/auth/me` is called only at login.
- A refresh replaces the token, not the stored user, so a change of role or approval shows up at
  the next login.
- A 401 triggers one shared refresh, then one retry. A failed refresh clears the store, and the
  route guard sends the user to `/login`.
- Route guards:
  - `/student` and `/teacher` require that role, or `admin`.
  - `/admin` requires a session only (`FE/App.tsx:147-153`). A student or teacher who opens it gets
    the admin page with empty data, because the API answers 403.

**Teacher approval.** The admin's Users page polls the pending teachers every 30 s and approves or
rejects each one, with no confirmation step. Rejecting deletes the account (`reject_teacher`).

**Groups.**
- **Creation:** a teacher creates a group for a course. The name must be unique per teacher,
  ignoring case and surrounding spaces. A group has no code until the teacher generates one.
- **Invitation code:** generating again replaces the old code at once; codes do not expire.
- **Joining:** a student joins with the code from any level (FR-028l). That enrols them in the
  group's course with the group, and replaces the student's main group (`users.group_id`).
- **Catalogue enrolment** (`/enroll`) joins no group since #34.
- **Teachers** cannot rename or delete a group, or remove a student.
- **The admin** can delete a group: its students are unlinked, `enrollments.group_id` becomes
  NULL, and the enrolments stay.
- **Moving a student** (admin API, audited) changes `users.group_id` only. No screen calls it.

**Two kinds of membership.** `users.group_id` is the student's one main group.
`enrollments.group_id` is the group of each course enrolment. Each feature reads them differently:

| Feature | Reads |
|---|---|
| Teacher dashboard and student list | both (union) |
| Teacher's access to one student | the main group (I7) |
| Group ranking (student and teacher) | the main group |
| Admin move | writes the main group only |
| Invitation join | writes both |
| `unenroll` | deletes the enrolment and leaves the main group |

**Admin.**
- The Users list holds **students only** (`get_all_students_admin`, `role = 'student'`).
- Approved teachers appear nowhere, so the V2 screens cannot deactivate one. V1 could.
- Deactivate and reactivate accept any id.
- Problem reports can be listed and resolved.
- The audit log lists group moves only.

**Test and demo accounts.**
- The four demo accounts and seven or eight `estudiante_*` test accounts are created, with
  published passwords, unless the process has `ENVIRONMENT=production`.
- That same variable turns on `validate_runtime()`.
- Seeds never delete or update a password.
- `is_test_user = 1` hides an account from teacher dashboards, metrics and exports, and from rating
  calibration.

**Level and grade.**
- Set at registration only. No API, screen or script changes them later: `set_grade` has no
  caller, and `set_education_level` is called only by V1 onboarding, which offers no semillero.
- Grade-less semillero accounts are fixed by hand in SQL (`docs/sdd/f1-semillero-survey.md` § 3).
- What a later change does to ratings is spec 001 FR-028c.

**Self-service.** No password change, no recovery (the login link says «próximamente»), no username
change and no account deletion. An email change exists only in the shared `Layout`, which only
`/admin` uses now (`FE/pages/Layout.tsx:87-110`). The student and teacher layouts have none.

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| I1 | **Bug** | **An email longer than 50 characters cannot be used to log in.** Registration accepts emails up to 254 characters, but `LoginRequest.username` stops at 50: the API answers 422 before checking anything. The username still works. | `api/schemas/auth.py:11, 23` | **Reproduced** (45-character local part: register 201, login with the email 422, with the username 200) |
| I2 | **Identity** | **Usernames are not normalised.** Case and surrounding spaces are kept, and uniqueness is exact on both engines: `Estudiante1` and ` estudiante1 ` register next to `estudiante1`. Emails are trimmed but not lower-cased; their partial unique index is case-sensitive. V1's caption promises «solo letras, números y guion bajo», which nothing enforces. | P:349, 619; S:91, 324; `api/schemas/auth.py:16`; `auth_view.py:165-168` | **Reproduced** (both registered, 201) |
| I3 | **Registration** | A student can register through the API without a level (201); the catalogue then falls back to universidad. The screen always sends one. | `api/schemas/auth.py:19-21`; `student_service.py:346-348` | **Reproduced** |
| I4 | **Admin** | **Failures are reported as success.** Moving a student to a group that does not exist answers 204: the repository's `(ok, message)` is discarded. Deactivate, reactivate, delete group and resolve report answer 204 for unknown ids. Approve has no role filter. | `api/routers/admin.py:47-119`; P:3235-3295 | **Reproduced** (move to a missing group, deactivate an unknown id) |
| I5 | **Admin** | **«Reject» deletes any teacher, approved ones included.** It is the only path that deletes a user. Their groups are left behind: PostgreSQL has no foreign key on `groups.teacher_id`, and SQLite's are not enforced. The groups vanish from `/admin/groups` (inner join), their codes stop resolving, and students keep a `group_id` that points at nothing. | P:2481-2488 S:2076-2081; `admin.py:47-61`; P:2715-2733 | **Reproduced** (approved `profesor1` rejected by id: 200, row gone) |
| I6 | **Admin** | **An admin can deactivate any account, including their own.** Self-deactivation locks out the only admin: the next call and the next login answer 401. Neither `_seed_admin` nor the #15 reset script reactivates an account, so recovery is SQL. The V2 Users list shows students only, so approved teachers cannot be deactivated from V2 screens. | `admin.py:64-73`; P:2449-2468, 2510-2536 | **Reproduced** (self-deactivation) |
| I7 | **Groups** | **The dashboard and per-student access disagreed.** The dashboard lists students by main group or by enrolment group. The report, histories, AI analysis and ranking accepted only the main group. Joining a second group by code replaces the main group, so the first teacher kept the student on the dashboard and got 404 when opening them. | `teacher.py:57-69`; P:2776-2851 | **Reproduced**; access fixed in #36. Who takes part in a group ranking (main group only) is decision 3 |
| I8 | **Groups** | **Membership is written inconsistently.** An invitation join silently replaces the main group, with no audit. The admin move writes only the main group, so the enrolment still names the old one. `unenroll` leaves the main group, so the student stays in that group's ranking and dashboard. A group deletion is not audited. On SQLite its exam assignments stay, because the cascade is declared but not enforced. | P:3721-3738, 3741-3752, 2736-2773, 3276-3286 | Code verified; effects inferred |
| I9 | **Audit** | Only admin group moves are audited. Approvals, rejections (deletions), (de)activations, group deletions and invitation joins leave no trace. | `audit_group_changes` P:639-647 | Verified |
| I10 | **Bug (SQLite)** | **`/admin/audit` answers 500 on SQLite once any audit row exists**: `dict(row)` on a plain tuple. Local development and tests only; PostgreSQL is fine. | S:1612 | **Reproduced** |
| I11 | **Role boundary** | `/student/*` checks authentication, not role. An approved teacher or the admin can enrol, practise, join a group by code and appear as a student wherever rankings do not filter by role. | `api/routers/student.py:89` | Verified |
| I12 | **Test accounts (R6)** | `is_test_user` means «hidden from teacher views, exports and calibration», not «protected». Rankings include test students, and deactivation and rejection do not check the flag. AGENTS R6 and the constitution say «protected, never remove». | P:610, 1765-1781, 2024, 2576, 2841, 2921, 3066, 3180, 3220; P:2264-2318 | Verified |
| I13 | **Seeds** | Demo and test accounts with published passwords exist in any process without `ENVIRONMENT=production`, and the same unset variable skips `validate_runtime()`. Seeds never remove accounts, so setting it later does not undo them. SQLite seeds one more test student than PostgreSQL (`estudiante_concursos_1`). `docs/transfer.md` already requires the variable on both hosts. | P:249, 259; S:51, 55; `seed_test_students.py:35`; `api/config.py:80-81` | Verified |
| I14 | **Promotion** | Nothing changes a student's level or grade after registration: `set_grade` has no caller, and `set_education_level` is reachable only from V1 onboarding without semillero. Grade-less semillero accounts depend on the manual SQL of the F-1 survey. | P:3820-3851; `student_view.py:136-154` | Verified |
| I15 | **Self-service** | No password change or recovery, no username change, no account deletion or data request. The email change is reachable only from the admin pages. The «Recordarme» checkbox does nothing. | `FE/pages/Login.tsx:408-426`; `FE/pages/Layout.tsx:87-110` | Verified |
| I16 | **Browser session** | The stored role is trusted until the next login. A refresh does not re-read the profile. `/admin` has no role guard: non-admins see the admin page shell with empty data. The login page shows even with a valid session. 401, 403 and 429 show the backend's text. | `FE/App.tsx:110-153`; `FE/stores/authStore.ts:43`; `FE/api/client.ts:127-141` | Verified |
| I17 | **Capacity** | **Each password check holds 64 MiB.** With the API's thread pool, 30 simultaneous logins peaked at 1,097 MB on a 144 MB process, more than a 512 MB instance (`render.yaml` declares the free plan). One check costs 0.24 s of CPU. | `hashing_service.py:12-18` | **Reproduced** (real server, 30 logins). Bounded to two checks at a time in #35 (peak 219 MB); the parameters themselves are decision 9 |
| I18 | **Rate limits** | Login and registration were keyed by any bearer header, valid or not, and the AI limits by token instead of account. | `api/rate_limit.py` | **Reproduced**; fixed in #33 |
| I19 | **Drift** | AGENTS.md § Roles says «student — group required»; in V2 registration and catalogue enrolment join no group. It says «admin — reassigns students (audited)»; V2 has the API but no screen. R6, see I12. The `/admin/users` docstring says «all users», but it returns students only. | `AGENTS.md` § Roles, R6; `admin.py:33-37` | Verified |

## 4. Existing evidence

- **API:**
  - `tests/api/test_auth.py` (17): login per role, wrong password, registration, duplicate,
    short password, `/me`, logout, refresh by cookie, a deactivated user losing access and refresh.
  - `test_protected_routes.py` (20): anonymous and wrong-role access to student, teacher, admin and
    AI routes; malformed headers.
  - `test_admin.py` (11): admin-only listing, approve, deactivate/reactivate, groups, reports.
  - `test_jwt_compatibility.py` (3).
  - `test_teacher_resource_access.py` (3).
  - `test_websocket_authorization.py` (4).
  - `test_production_config.py` (6).
  - `test_rate_limit.py` (2; 5 with #33).
- **Registration and enrolment (spec 001 FR-028k–o, both engines):**
  `tests/integration/test_spec001_catalogue.py`; `tests/integration/test_enrol_joins_no_group.py`
  (#34).
- **Teacher scope:** `tests/integration/test_teacher_student_scope.py` (#36).
- **Browser:** `frontend/e2e/auth.spec.ts` (5) and `protected-routes.spec.ts` (12) — redirects
  for anonymous users and wrong roles, login per role, a wrong password, and the registration form.
- **Not covered:**
  - admin failure paths and unknown ids (I4);
  - rejecting an approved teacher (I5);
  - self-deactivation (I6);
  - membership writes (I8);
  - the audit on SQLite (I10);
  - non-student callers of `/student/*` (I11);
  - username and email normalisation (I1, I2);
  - the invitation code's lifecycle (regenerate, deleted teacher);
  - `/admin` opened by a non-admin in the browser (I16).

## 5. Decisions for the owner (input for `/speckit-clarify`)

None blocks the transfer (PR #3).

1. **Usernames and emails (I1, I2).** Normalise usernames (trim; case-insensitive uniqueness) and
   lower-case emails? Existing accounts may collide: a read-only count first. Keep login by
   username *or* email?
2. **Admin powers (I4–I6).**
   - Reject only pending teachers, and deactivate instead of delete?
   - Refuse self-deactivation and deactivating the last active admin?
   - List teachers (and admins) in the Users screen so they can be deactivated?
   - Add a screen for the existing move-student API?
3. **Group membership (I7, I8).** One source of truth for «this teacher's student», for rankings
   and for the dashboard: the main group, the enrolment groups, or both. What does joining a
   second group do to the first? Should `unenroll` leave the course's group?
4. **Audit scope (I9).** Which admin and teacher actions are recorded?
5. **Test accounts (I12, I13).** Does `is_test_user` mean «hidden from teachers» (today) or
   «protected» (R6)? Should test students appear in rankings? How are demo accounts handled in
   production (see the owner's checklist)?
6. **Promotion (I14).** Who changes a student's level or grade (admin screen, teacher, script),
   with what audit, and how FR-028c's «history, not a loss» is shown.
7. **Self-service (I15).** Password change, and a recovery path that does not need email (most
   accounts have none): a teacher or admin reset, or recovery by email for those who gave one.
   Should students change their own email? Account deletion and data requests for minors.
8. **Session lifetime and revocation.** Already raised with the owner separately.
9. **Hashing cost (I17).** Keep Argon2 at 64 MiB with the concurrency bound of #35, or lower the
   parameters (for example m = 19 MiB, t = 2, p = 1: 0.05 s of CPU instead of 0.24 s). Stored
   hashes are re-hashed at each user's next login. This depends on the Render plan actually in use.
10. **Role boundary (I11, I16).** Restrict `/student/*` to students, or allow admins and teachers
    (for example to preview)? Add the `/admin` role guard to the browser.

## 6. Proposed scope for spec 004 (draft)

- **In:**
  - registration and its rules, including FR-028m moved from spec 001;
  - login identifiers and normalisation;
  - password storage and its cost;
  - tokens, sessions, refresh, logout and revocation;
  - role boundaries per router, WebSocket and screen;
  - teacher approval;
  - groups, invitation codes and membership;
  - enrolment by catalogue and by invitation (the rule; the catalogue itself stays in spec 001);
  - admin actions and their audit;
  - test and demo accounts;
  - level and grade changes;
  - self-service account actions;
  - rate limits on authentication.
- **Out:**
  - rating effects of any of these (spec 001, including FR-028c);
  - persistence mechanics: pool, migrations, parity (spec 002);
  - AI keys and providers (spec 005);
  - dashboard metrics, exports and exams (spec 006);
  - the PvP match lifecycle (spec 007);
  - V1 beyond keeping it working (frozen, disconnected at the switch).
