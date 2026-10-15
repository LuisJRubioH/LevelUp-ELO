# Feature Specification: Identity & Access — School Accounts

**Feature Branch**: `004-identity` (one branch per delivery once implementation starts)

**Created**: 2026-10-13

**Status**: Approved by the owner (2026-10-15). The approved decisions of blocks 4 and 8 that apply to every account,
and those of the rate-limit store (owner, 2026-10-13 and 2026-10-14), are specified; the initial
import's decisions live in spec 009 (owner, 2026-10-14). E1 is implemented and closed (its pull
request); E2, E3, E5 and E6 are `planned`.

**Input**: The owner's approved orders of 2026-10-13: block 4 (enrolment through Google Forms,
account creation and access limits) with its clarifications P1–P15 and supplementary precisions,
block 8 (Safari-compatible session renewal) and the decision on LuisJRubioH/LevelUp-ELO#59
(continuity of the limits when Redis fails); the owner's corrections of 2026-10-14 on the scope of
the initial import's decisions. Background: the as-is survey
`docs/sdd/identity-survey.md` (LuisJRubioH/LevelUp-ELO#37), cited as I1 … I19, and the read-only
research of 2026-10-13 cited with `file:line` on `redesign @ 1d6fcf6`. The initial import from
Google Forms is specified apart, in spec 009 (owner, 2026-10-14): this spec holds the rules every
account follows, which the import reuses and never changes.

**Outcome served** (constitution VIII): the school, not the public, decides who has an account.
Accounts with their own credentials remain possible, and every existing account keeps its
credentials and its progress. Classmates and teachers see each student by name. Every user can keep a session open on any supported browser — Safari included — for as long as the
account and its credentials are valid. Teachers trust that the students they see are theirs.

## Code Scope *(mandatory)*

The code whose behaviour this spec defines. A path shared with another spec belongs to both.

- `api/routers/auth.py` — login, public registration, refresh, logout, password change
- `api/schemas/auth.py`
- `api/rate_limit.py` — the limits and their store
- `api/config.py` — the settings of limits, registration and sessions
- `api/dependencies.py` — the per-request account check
- `api/main.py` — `/api/health`
- `api/routers/admin.py` — administrative creation, reset, expiration, display names
- `api/routers/student.py` — names in rankings and PvP history; the student's own display name
- `api/routers/teacher.py` — names in teacher views
- `api/websocket/pvp.py` — rival's name; closing on revocation or expiry
- `api/websocket/notifications.py` — closing on revocation or expiry
- `src/application/interfaces/repositories.py`
- `src/infrastructure/persistence/` — accounts, history and audit in both repositories
- `src/infrastructure/security/hashing_service.py`
- `frontend/src/api/auth.ts`
- `frontend/src/api/client.ts` — renewal through the same origin
- `frontend/src/stores/authStore.ts`
- `frontend/src/pages/Login.tsx`
- `frontend/src/pages/Admin/Users.tsx`
- `frontend/src/pages/Student/Stats.tsx`
- `frontend/src/pages/Student/League.tsx`
- `frontend/src/hooks/usePvpMatch.ts`
- `frontend/vercel.json` — the same-origin proxy (prepared, not deployed)
- `render.yaml`

## Deliveries *(mandatory for this spec)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it `closed` and fills all its rows.

| Delivery | Content | Order rule | State |
|---|---|---|---|
| **E1** | Public registration closed by default (one server setting, refused on the server, reflected by the screen); login limits per normalised account and global | Needed for the switch (LuisJRubioH/LevelUp-ELO#3). Built on LuisJRubioH/LevelUp-ELO#33, whose login-by-address limit it replaces. | closed |
| **E2** | Display name everywhere classmates and teachers look; password change; security version that revokes tokens, renewals and persistent connections; admin password reset; teachers created by the admin | Before any real student is created (decision 5). Teachers created by the admin need its forced password change (N3). | planned |
| **E3** | Students created one by one by the admin: own username, temporary password changed at first access, display name, existing group, optional last day (N13, N15); the expiry of any account that has a last day of access, also on open sessions and PvP, while an account without one never expires; the admin changes, extends or reactivates | Not merged before E2 is in production. | planned |
| **E5** | Session renewal without third-party cookies (block 8): same-origin proxy, cookie scope, CSRF, no caching, revocation and expiry respected; Safari verified | After E2 (revocation). E3's tests include renewal of an expired account. | planned |
| **E6** | Rate-limit store continuity (constitution 1.1.0): temporary memory fallback, timeouts, controlled recovery, no new allowance, health state | After LuisJRubioH/LevelUp-ELO#63; replaces the code of LuisJRubioH/LevelUp-ELO#59. Same file as E1: one after the other. | planned |

The initial import of a Google Forms export, once delivery E4 here, is spec 009 (owner,
2026-10-14); the other deliveries keep their names.

## Clarifications

### Session 2026-10-13 (owner orders and clarifications, approved)

Recorded as given; the delivery that turns each into requirements is in brackets.

**Block 4 — enrolment, account creation and access limits**

- The questions on enrolment through a Google Form, the credentials of its students, how their
  identification is read and what happens before saving an import are recorded in spec 009, with
  the initial import (owner, 2026-10-14).
- Q: How long is an account valid? → A: temporary accounts require an expiration, set per batch and
  changeable per account by the admin, shown in Colombian time. Once expired, sign-in and
  authenticated access stop, even from an open session; academic data is kept; the admin can
  extend or reactivate. [E3] *(Scope, 2026-10-14: the expiry applies to any account that has a
  last day; the import's batch gives one only to its own accounts; an account without one never
  expires.)*
- Q: Is public registration open? → A: closed by default by a server-side control; it can be
  enabled explicitly if needed. Individual creation and import stay available with registration
  closed, through the application's validations and services — no manual inserts. [E1; creation:
  E3; the import: spec 009]
- Q: Which limits? → A: separate limits for login, public registration and import. Login: per
  normalised account and a configurable global ceiling, initially 10 per account and 300 overall
  per minute, to be verified against the expected concurrency; blocks are temporary. Public
  registration, when enabled, has its own per-address limit. The import has its own administrative
  controls able to load a whole class. [E1; the import's controls: spec 009]
- Q: What must tests prove? → A: 30 students sign in from one address within one minute; repeated
  attempts against one account are limited; re-importing a file duplicates no student and changes
  no credential or progress; closed registration is enforced on the server while administrative
  creation goes on; an expired account loses access, also from an open session; identifications
  keep their leading zeros. Parity between SQLite and PostgreSQL; the storage of the limits
  documented for the final repository; no deployment. [all] *(2026-10-14: the leading-zero test
  is withdrawn; the import's tests are spec 009's.)*

**P1 — creating teachers** [E2, see N3]: from the admin panel, by the admin only; created teachers
are approved, receive a random temporary password and must change it at first access; credentials
based on the identification never apply to teachers or admins; who created the account is
recorded.

**P2 — reopening public registration** [E1]: one server configuration variable, closed by default.
The server refuses public sign-ups while closed and the screen reflects the state. Administrative
creation stays available. Opening it removes neither the limits nor the approval of publicly
registered teachers.

**P3 — revoking tokens and sessions** [E2]: a per-account security version checked by the server. A
password change invalidates the earlier tokens; the session that made the change may receive new
credentials. An administrative reset invalidates every session. Revocation applies to renewals and
to persistent authenticated connections.

**P4 — origin of the display name** [E2, E3; the import's column: spec 009]: mandatory for new
accounts and imports, taken from a form column and reviewable by the admin; never the
identification, not even as a fallback. Existing accounts without one use, for now, a neutral alias
not derived from their identification. Repeated display names are allowed. *(Scope, 2026-10-14:
every new student account, N11; an account without one shows its username, N5; an import row without
one is an error, spec 009 — no alias.)*

**P5 — changing the display name** [E2]: reserved to the admin and recorded; independent of the
username used to sign in. *(Scope: N14 — the admin alone for the import's accounts, spec 009;
the owner of any other account changes their own.)*

**P6 — password reset** [E2]: the admin resets with a random temporary password that must be
changed at first access; every earlier session is invalidated; the operation is recorded —
responsible, account, time — never the password. Tests prove earlier tokens stop working, public
names never expose the identification, and only authorised roles change names or reset access.

**P7 — expiration and message** [E3]: the admin gives the last day of access, inclusive, in
Colombian time. From the start of the next day authenticated access is blocked and the student
sees «El período de acceso de tu cuenta terminó. Tu progreso está guardado. Contacta al
administrador si necesitas ampliar el acceso.» Extending never deletes data.

**P8 — group** [E3; the import: spec 009]: an existing group is required for every new temporary
student, created individually or imported. No group is created automatically from errors or
variations in a file. *(Scope, 2026-10-14: every student the admin creates, one by one or by the
import, semillero included — N15, at creation; public registration, existing accounts, deleting a
group and reassigning a student keep today's behaviour.)*

**P9 — level and grade** [E3; the import's columns and batch: spec 009]: from mapped columns or from
values chosen explicitly for the batch; shown in the preview; combinations validated; «No aplica»
admitted where it applies; never deduced silently from the group's name.

**P12 — administrative limits** [E3; files and imports: spec 009]: separate from public registration
and login. Initially: 30 individual creations per minute per admin; files up to 500 students and 5
MB; one import running per admin. A full load is verified and retries never duplicate accounts.
Configurable. If the server cannot process 500 students reliably, the result is reported before
lowering the limit or changing the processing.

**P13 — traceability checker** [done: LuisJRubioH/LevelUp-ELO#64]: requirements recognised
whatever their formatting; deliveries explicit; nothing exigible in a delivery may stay `PENDING`
when it closes.

**P15 — expiration during a PvP match** [E3]: a match still active when an account expires is
closed as abandoned, with no rating effect for either participant; results validly saved before
the expiry are kept; closing and expiring are atomic and idempotent, with concurrency tests and
clear messages for both players.

**Audit** [E2, E3; the import: spec 009]: the admin responsible, date and time, an operation
identifier, the affected accounts by internal ID and each row's result; never passwords or the whole
file.

**Block 8 — session renewal compatible with Safari** [E5]: the authentication flow must not depend
on third-party cookies: the API is reached from the application's own origin through a proxy to
the backend, and sending, receiving and deleting the cookie are verified on login, renewal and
logout. The renewal cookie stays `HttpOnly` and `Secure`, with its scope and `SameSite` set for the
chosen flow. Protections against unauthorised requests are kept and authentication responses are
not cached. The access token keeps its 15 minutes. Renewal lets work continue without intervention
while session and account are valid, respects revocation by password change or reset and account
expiry at once, and never bypasses them. Verified on Safari for iPhone/iPad and desktop and on the
other supported browsers — token expiry, reload, logout, revoked credentials, expired accounts —
distinguishing automated tests from checks on real devices. PvP WebSockets are reviewed
separately. Code, configuration and the transfer guide are prepared; no deployment.

**Rate-limit store (#59)** [E6]: a temporary in-memory fallback of the counters when Redis fails
while the server runs, keeping the configured limits and the single-process rule; startup still
refuses a missing Redis configuration; formalised first in the rules (constitution 1.1.0,
LuisJRubioH/LevelUp-ELO#63); never presented as a permanent substitute. Configurable connect and
operation timeouts; no request waits on Redis during a sustained outage; recovery checked in a
controlled way; return to the shared store without granting a new allowance. `/api/health`
reports normal or degraded without internal addresses or credentials; 200 while the database and
the fallback serve, 503 if the database fails or the limits cannot be applied; monitors read the
body state too. Entering and leaving the degraded mode is logged once each. Tests: failure,
recovery, limits during the fallback, transition between stores, both mechanisms failing.
Documented: a restart loses the local counters.

### Session 2026-10-14 (owner corrections on scope, approved)

- The decisions on the identification as username and password belong only to the owner's first
  load of students from Google Forms (the initial import). They are no universal requirement of
  identity or authentication.
- Accounts with their own credentials and no identification linked remain possible; the
  restrictions of the initial file never become general validations.
- The identifications have no leading zeros: that case leaves the acceptance requirements.
- Excel must not alter the values, but no condition is added about documents nobody asked for.
- Each decision is classified by its scope (below).
- The last day, the group and the credentials of this load are not imposed on other accounts.
- Existing accounts keep their credentials and their progress, and none has to link an
  identification to keep working.
- New general restrictions drawn from this first group's examples or needs are asked, never assumed
  approved (N11 … N16).

### Session 2026-10-14, later (owner answers to N11 … N16, approved)

- N11: the display name is **not optional**: every new student account has one — created by the
  admin, imported, or registered by the student while registration is open. A student who
  registers chooses it, and names that mock or offend are refused (the filter: N17).
- N12: classmates and teachers — PvP, rankings, the teacher's views — see the display name, never
  an identification. An imported account without a name yet appears by a neutral alias.
  *(Withdrawn 2026-10-14, night: an import row without a name is an error, spec 009.)*
- N13: a student created one by one by the admin gets their own credentials: a username of letters
  and digits and a random temporary password changed at first access. The import stays available
  with its own credentials (the identification; spec 009).
- N14: only the admin changes the display name of an account of the initial import (spec 009);
  the owner of any other account may change their own, under the same filter.
- N15: an existing group is mandatory for every student account — created one by one, imported or
  semillero. *(Scope, 2026-10-14, night: at creation by the admin.)*
- N16: numeric `.xlsx` cells are accepted (spec 009).
- Still open: the columns of the Google Form (the owner sends them when available); what an
  existing account without a name shows (N5); the details of the name filter (N17).

### Session 2026-10-14, evening (owner answers, approved)

- N5: the existing accounts are test accounts; one without a display name shows its username.
- N17: names may be long and use hyphens — names that are not Spanish — and offensive words in
  English are refused as well as in Spanish.
- N1, N2, N3, N6, N9 and N10 are approved (N4 was withdrawn and now lives in spec 009; N8 is the owner's operational step).
- Still open: N7 (when the expiry message is shown); the columns of the Google Form.

### Session 2026-10-14, night (owner answers, approved)

- N7 is approved: an expired account sees P7's message only after the right password; with a wrong
  one, the usual refusal.
- The initial import from Google Forms is specified apart, in spec 009, so that this spec holds only
  rules for every account. The decisions approved for the import keep their content and move with
  it.
- An import row without a display name is an error the admin corrects before confirming (spec
  009). No neutral alias is needed: every account shows its display name, or its username while it
  has none (N5).
- N15 applies when the admin creates a student — one by one or by the import, semillero included.
  Public registration, existing accounts, deleting a group and reassigning a student keep today's
  behaviour.

### Session 2026-10-15 (owner answers, approved)

- Block 8 is approved: session renewal through the application's own origin (delivery E5).
  Turning it on — the two Vercel variables and Render's cookie setting — and the checks on real
  Safari devices remain the owner's operational steps.
- E3 is approved as delivered (LuisJRubioH/LevelUp-ELO#73), with the choices its plan makes:
  - a last day already past is refused when the admin creates a student, while an existing
    account's last day may be set in the past, which ends its access at once;
  - a student the admin creates joins the group's course at any level, as with an invitation
    (spec 001 FR-028l);
  - the per-admin creation limit counts refused attempts too;
  - V1 does not check the last day; it is disconnected at the switch.

### Scope of each decision (2026-10-14)

**General product rule** — every account:
- Public registration is opened or closed by one server setting and refused on the server while
  closed (P2).
- Login is limited per normalised account and by a global ceiling, with no per-address limit
  (FR-006 … FR-011).
- Passwords are stored only as an Argon2id hash (FR-032).
- The security version: a password change ends the other sessions, an administrative reset ends all
  of them and forces a change of the temporary password (P3, P6).
- Teachers are created by the admin, approved, with a temporary password changed at first access;
  credentials based on an identification never apply to teachers or admins (P1).
- Administrative operations are audited without passwords or files.
- An account that has a last day of access stops at its end, also in open sessions and PvP, keeps
  its data, and the admin can extend it (P7, P15). An account without a last day never expires.
- Classmates and teachers see a student by display name — by username while an existing account
  has none (N12, N5) — and never by an identification.
- Every new student account has a display name (N11); a student the admin creates has an existing
  group (N15).
- A student created one by one gets their own username and a temporary password (N13).
- Session renewal through the application's own origin (block 8) and the continuity of the limits
  when Redis fails (#59).

**Configuration of the first version** — values a setting can change:
- Public registration closed by default (P2).
- Login: 10 per account and 300 in total per minute; public registration: 20 per address per minute
  (N2).
- Administrative limits: 30 individual creations per minute per admin (P12); the import's limits
  are spec 009's.

**Behaviour of the initial import** — spec 009 (owner, 2026-10-14): its credentials, the
identification's format, the display name's column, the batch's group, level, grade and last day,
mapping, preview, confirmation, re-import, linking and who sees the identification. It reuses this
spec's rules for every account and adds two that reach other paths, both stated there: the student
of an imported account does not rename themselves, and the admin cannot give a new account a
username that is an identification linked to another.

**Waiting on the owner**: nothing in this spec. The columns of the Google Form wait in spec 009.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nobody creates an account by themselves unless the server allows it (Priority: P1) — E1

**Why this priority**: with the redesign in production, anyone who finds the sign-up can create a
student or a pending teacher (`api/routers/auth.py:79-92`).

**Independent Test**: with the setting at its default, a sign-up request creates nothing and the
screen offers none; with it enabled, sign-up works within its own limit.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** the default configuration, **When** anyone sends a public sign-up
   request, **Then** it is refused on the server and no account is created.
2. **US1-AS2** — **Given** the default configuration, **When** the login screen loads, **Then** it
   offers no way to sign up.
3. **US1-AS3** — **Given** public registration enabled by its setting, **When** someone signs up,
   **Then** the account is created as today (a teacher pending approval), and the screen offers it.
4. **US1-AS4** — **Given** public registration enabled, **When** one address exceeds the
   registration limit within a minute, **Then** the extra sign-ups are refused, and login is not
   affected.
5. **US1-AS5** — **Given** a teacher pending approval, **When** the admin approves them, **Then**
   they can sign in, as today.

### User Story 2 - Login limits protect each account without blocking a class (Priority: P1) — E1

**Why this priority**: for the initial import's accounts the identification is the initial password
(spec 009), so the account is the unit to protect; today the only login limit counts 20 per minute per address (`api/config.py:63`), so a
class of 21 on one school address is refused.

**Independent Test**: 30 students from one address sign in; the 11th attempt against one account
in a minute is refused; the 301st attempt in a minute is refused.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** 30 different students on one address, **When** each signs in once with
   the right password within one minute, **Then** all 30 succeed.
2. **US2-AS2** — **Given** an account, **When** its 11th attempt within a minute arrives — right
   password or not, by its username or its email, from any address — **Then** it is refused until
   the block ends, and another account still signs in.
3. **US2-AS3** — **Given** 300 attempts within a minute from any accounts, **When** the 301st
   arrives, **Then** it is refused.
4. **US2-AS4** — **Given** an identifier that matches no account, **When** its 11th attempt arrives,
   **Then** the refusal is identical to that of an existing account.
5. **US2-AS5** — **Given** other values in the settings, **When** the API starts, **Then** both
   limits follow them.

### User Story 3 - Classmates and teachers see my name (Priority: P1) — E2

*Scope (2026-10-14)*: classmates and teachers see a student by display name (N12); every new student
account has one (N11); an existing account without one shows its username (N5). The admin changes
any student's name, and a student changes their own (N14); spec 009 reserves to the admin the names
of the import's accounts.

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** a group ranking, **When** a student opens it, **Then** each classmate
   appears by display name — or by username while they have none (FR-022) — and the response holds
   no username of a classmate who has a display name.
2. **US3-AS2** — **Given** a PvP match or history, **When** a student sees the rival, **Then** it is
   the rival's display name, or their username while they have none, and no message carries the
   username of a rival who has a display name.
3. **US3-AS3** — **Given** an existing account without a display name, **When** a classmate or a
   teacher sees it, **Then** it appears by its username (N5).
4. **US3-AS4** — **Given** a teacher's views of their students — dashboard, groups, procedures, exam
   results, exports — **When** they load, **Then** each student appears by display name (or the
   username of FR-022) and group, and no username of a student who has a display name appears.
5. **US3-AS5** — **Given** the admin's list of users, **When** it loads, **Then** each student shows
   their username and their display name, so that the admin can find and correct a name.
6. **US3-AS6** — **Given** a student account, **When** the admin changes its display name, **Then**
   it changes and the change is recorded; when a teacher or another student tries, it is refused and
   nothing changes.
7. **US3-AS7** — **Given** a student, **When** they change their own display name, **Then** an
   allowed name is saved and recorded, and a name the filter refuses changes nothing.
8. **US3-AS8** — **Given** public registration enabled, **When** a student registers, **Then** a
   display name is required, and a name the filter refuses is refused.

### User Story 4 - I change my password and my other sessions end (Priority: P1) — E2

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** a signed-in user, **When** they give their current password and a valid
   new one, **Then** the new one signs in, the old one does not, and their session continues.
2. **US4-AS2** — **Given** two open sessions of one account, **When** one changes the password,
   **Then** the other's access token, renewal and persistent connections stop working at once.
3. **US4-AS3** — **Given** a wrong current password or a new one too short, **When** the change is
   asked, **Then** it is refused and nothing changes.

### User Story 5 - The admin resets access and creates teachers (Priority: P2) — E2

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** a student or teacher, **When** the admin resets their password, **Then**
   a random temporary password is issued, every earlier session stops working, and at the next
   sign-in they must change it before anything else.
2. **US5-AS2** — **Given** the admin, **When** they create a teacher, **Then** the teacher is
   approved, receives a random temporary password and must change it at first access; the
   creation is recorded with who made it.
3. **US5-AS3** — **Given** a reset or a creation, **When** the audit is read, **Then** it names the
   admin, the account and the time, and holds no password.
4. **US5-AS4** — **Given** a student or a teacher, **When** they try to reset access or create a
   teacher, **Then** it is refused.

### User Story 6 - The admin creates a student one by one (Priority: P1) — E3

*Scope (2026-10-14)*: a student created one by one gets their own credentials (N13) and an
existing group (N15); credentials based on the identification belong to the initial import only
(spec 009).

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** a username `ana.perez7`, a display name, an existing group and a valid
   level and grade, **When** the admin creates the student, **Then** the account is created with a
   random temporary password shown once to the admin, and at the first sign-in the student must
   change it before anything else.
2. **US6-AS2** — **Given** a username the account rules refuse, or a display name the name filter
   refuses, **When** the admin creates the student, **Then** it is refused and nothing is created.
3. **US6-AS3** — **Given** no group, a group that does not exist, a missing display name, or an
   invalid level and grade combination, **When** the admin creates the student, **Then** it is
   refused and nothing is created.
4. **US6-AS4** — **Given** a username already in use, **When** the admin creates the student,
   **Then** it is refused and nothing changes.
5. **US6-AS5** — **Given** an admin who already created 30 students in the last minute, **When** they
   create one more, **Then** it is refused for the rest of the minute.

### User Story 7 - An account stops working after its last day (Priority: P1) — E3

**Acceptance Scenarios**:

1. **US7-AS1** — **Given** a last day of access, **When** that day ends in Colombian time, **Then**
   sign-in is refused with «El período de acceso de tu cuenta terminó. Tu progreso está guardado.
   Contacta al administrador si necesitas ampliar el acceso.»
2. **US7-AS2** — **Given** an open session, **When** its account expires, **Then** its next request,
   renewal or persistent connection is refused.
3. **US7-AS3** — **Given** an expired account, **When** its data is read, **Then** its ratings,
   attempts, enrolments and submissions are unchanged.
4. **US7-AS4** — **Given** an expired account, **When** the admin extends its last day, **Then** it
   signs in again with all its data.
5. **US7-AS5** — **Given** a PvP match in progress, **When** one player's account expires, **Then**
   the match is closed as abandoned, neither player's rating changes, results saved before stay,
   and both players see why.
6. **US7-AS6** — **Given** the expiry and the normal close of a match at the same moment, **When**
   both run, **Then** the match ends once, in one state, with one effect.
7. **US7-AS7** — **Given** an account without a last day of access — any existing account, or one
   with its own credentials — **When** any day ends, **Then** it keeps signing in and its sessions
   keep working.

The initial import's user story is spec 009's; the stories keep their numbers.

### User Story 9 - My session renews on any browser, Safari included (Priority: P1) — E5

**Acceptance Scenarios**:

1. **US9-AS1** — **Given** a signed-in user whose access token expired, **When** they keep working,
   **Then** the session renews without intervention, through the application's own origin.
2. **US9-AS2** — **Given** a reload of the page, **When** the session is valid, **Then** the user
   stays signed in.
3. **US9-AS3** — **Given** a logout, **When** it completes, **Then** the renewal cookie is deleted
   and no renewal works.
4. **US9-AS4** — **Given** credentials revoked by a password change or reset, or an expired account,
   **When** a renewal is attempted, **Then** it is refused at once.
5. **US9-AS5** — **Given** Safari on iPhone, iPad and desktop and the other supported browsers,
   **When** US9-AS1 … AS4 are run, **Then** they hold on each.

### User Story 10 - Limits keep working when Redis fails (Priority: P2) — E6

**Acceptance Scenarios**:

1. **US10-AS1** — **Given** Redis failing while the API runs, **When** requests arrive, **Then** the
   configured limits keep applying from memory, no request waits on Redis beyond its timeout once
   the failure is known, and `/api/health` answers 200 with a degraded state.
2. **US10-AS2** — **Given** Redis back, **When** recovery is detected, **Then** the shared store is
   used again and no counter restarts from zero for a key counted during the outage.
3. **US10-AS3** — **Given** Redis and the fallback both failing, **When** a limited request or a
   health check arrives, **Then** the limited request is refused and `/api/health` answers 503.
4. **US10-AS4** — **Given** a production configuration without Redis, **When** the API starts,
   **Then** it refuses to start, as today.
5. **US10-AS5** — **Given** an outage of many requests, **When** the logs are read, **Then** they
   hold one entry for entering and one for leaving the degraded mode.

### Edge Cases

- **The hosting proxy hides the client's address** (reproduced locally with uvicorn 0.53): login
  keeps no per-address limit (FR-008), so it does not matter there; public registration's
  per-address limit may then count every client as one — no header is trusted for it (N2).
- **An account with an email** signs in with its username or its email: both count toward the same
  account's login limit (FR-006).
- **A variant of a username** (other letter case, outer spaces) names no account — sign-in matches
  exactly — so it cannot sign in, and it is counted under itself, normalised (FR-006).
- **Attempts above the limit with the right password** are refused too until the block ends; the
  agreed counter counts every attempt, not only failed ones. No change is proposed.
- **V1's own sign-up form** writes to the same database and is not closed by this spec; V1 is
  disconnected during the switch (`docs/transfer.md` § 3.1); if it is reconnected, its sign-up
  must be closed first.
- **Expiry while a request is in flight**: the request already authorised completes; the next one
  is refused (FR-047).

## Requirements *(mandatory)*

### Functional Requirements

**E1 — public registration (US1)**

- **FR-001** [CHANGE]: While public registration is disabled — its default — the system shall
  refuse every public sign-up on the server and create no account. *(Today `POST
  /api/auth/register` creates a student, or a teacher pending approval, for any caller —
  `api/routers/auth.py:79-92`.)*
- **FR-002** [CHANGE]: The system shall enable public registration only through one server
  configuration setting, disabled by default.
- **FR-003** [CHANGE]: The login screen shall offer sign-up only while public registration is
  enabled, reading that state from the server. *(Today it always has a «Crear cuenta» tab —
  `frontend/src/pages/Login.tsx:328`.)*
- **FR-004** [CHANGE]: While public registration is enabled, the system shall limit sign-ups per
  address with a limit of their own, separate from the login limits.
- **FR-005** [AS-IS]: While a teacher account registered publicly is pending approval, the system
  shall let the admin approve or reject it (`api/routers/admin.py:40-61`).

**E1 — login limits (US2)**

- **FR-006** [CHANGE]: When an account receives more sign-in attempts within one minute than the
  per-account limit (default 10) — counting every attempt, right or wrong, that names it by its
  username or its email, from any address — the system shall refuse the extra attempts without
  checking the password until the minute ends. An identifier that names no account is counted the
  same way under itself, after trimming outer spaces and ignoring letter case.
- **FR-007** [CHANGE]: When the service receives more sign-in attempts within one minute than the
  global limit (default 300), the system shall refuse the extra attempts until the minute ends.
- **FR-008** [CHANGE]: The system shall not refuse a sign-in because other users share its address:
  no per-address limit applies to login. *(Today 20 per minute per address, `api/config.py:63`.)*
- **FR-009** [CHANGE]: The system shall take the login limits from settings, defaults 10 and 300 per
  minute, independent of the registration and administrative limits.
- **FR-010** [CHANGE]: The system shall answer an attempt refused by FR-006 identically whether or not
  an account with that identifier exists.
- **FR-011** [CHANGE]: The system shall keep no identifier or email in readable form in the limit
  counters, and write none to the logs when a limit refuses an attempt.
- **FR-012** [AS-IS]: Where the API runs in production, the system shall refuse to start while its
  limit counters are kept in process memory (`api/config.py:93`).

**E2 — display names (US3)**

- **FR-020** [CHANGE]: The system shall give every new student account a display name,
  independent of the username, which may repeat across accounts: the admin sets it when creating
  the account, a student who registers chooses it, and the initial import takes it from a column
  (spec 009). The name filter accepts 2 to 80 letters of any language, spaces, apostrophes and
  hyphens, and refuses a name that holds an offensive or mocking word in Spanish or English,
  compared without accents or letter case (N17). Existing accounts keep working without one.
- **FR-021** [CHANGE]: When the system shows a student to another student — rankings, PvP rival and
  history, any classmates' view — it shall show the display name, or the username of FR-022 while
  the account has none, and no response or message addressed to a student shall carry the username
  of another student who has a display name. *(Today: `frontend/src/pages/Student/Stats.tsx:257`,
  `League.tsx:142,171,243`, `api/websocket/pvp.py:331,335`.)*
- **FR-022** [CHANGE]: While an account has no display name — only accounts created before this
  delivery — the system shall show its username (N5).
- **FR-023** [CHANGE]: When a teacher's views show a student — dashboard, groups, procedures, exam
  results, exports — the system shall show the display name (or the username of FR-022) and group,
  and no username of a student who has a display name.
- **FR-024** [CHANGE]: The system shall show the admin each student's username and display name.
- **FR-025** [CHANGE]: The system shall let the admin change any student's display name and a
  student change their own, both under the name filter, record every change — who, which account,
  when — and refuse it to anyone else.

**E2 — passwords and sessions (US4, US5)**

- **FR-026** [CHANGE]: When a signed-in user gives their current password and a valid new one
  (6 characters or more after trimming, the account rule today), the system shall replace the
  password; otherwise it shall refuse and keep it.
- **FR-027** [CHANGE]: The system shall keep a security version per account, check it on every
  authenticated request, renewal and persistent connection, and refuse credentials issued under
  an earlier version.
- **FR-028** [CHANGE]: When a user changes their password, the system shall advance the security
  version and give the session that made the change new credentials; every other session's access
  token, renewal and persistent connection stops working.
- **FR-029** [CHANGE]: When the admin resets an account's password, the system shall issue a random
  temporary password, advance the security version so that every session ends, and record the
  admin, the account and the time — never the password.
- **FR-030** [CHANGE]: While an account must change its temporary password, the system shall allow
  only the password change.
- **FR-031** [CHANGE]: When the admin creates a teacher, the system shall create it approved, with a
  random temporary password that must be changed at first access, and record who created it.
- **FR-032** [CHANGE]: The system shall store every password — initial, temporary or chosen — only as
  an Argon2id hash, and write no password to the database in readable form, to logs or to reports.
- **FR-033** [CHANGE]: If anyone other than the admin tries to reset access, create a teacher or
  change a display name, then the system shall refuse it and change nothing.

**E3 — temporary students (US6)**

- **FR-040** [CHANGE]: When the admin creates a student one by one, the system shall require a
  username, a display name, an existing group, and a level and a grade (or «No aplica» where it
  applies, combinations validated); the last day of access is optional. It shall issue a random
  temporary password that must be changed at first access (FR-030), shown once to the admin, and
  create the account through the application's services and validations, never by a direct insert.
- **FR-043** [CHANGE]: If the username is already in use, then the system shall refuse the creation
  and change nothing.
- **FR-044** [CHANGE]: When the admin creates a student — one by one, or by the import of spec 009,
  semillero included — the system shall require an existing group (N15); the new student joins it,
  and no group is created by a creation. Public registration, existing accounts, deleting a group
  and reassigning a student keep today's behaviour.
- **FR-045** [CHANGE]: When an admin exceeds 30 individual creations per minute (configurable), the
  system shall refuse the extra creations until the minute ends.

**E3 — expiration (US7)**

- **FR-046** [CHANGE]: The system shall store an account's optional last day of access, inclusive,
  interpreted and shown in Colombian time; only an explicit action of the admin — or the initial
  import's batch, spec 009 — sets it.
- **FR-047** [CHANGE]: From the start of the day after an account's last day, the system shall
  refuse the account's sign-in, renewals, authenticated requests and persistent connections. An
  account without a last day of access never expires.
- **FR-048** [CHANGE]: When an expired account signs in with the right password, the system shall
  answer «El período de acceso de tu cuenta terminó. Tu progreso está guardado. Contacta al
  administrador si necesitas ampliar el acceso.» With a wrong password it shall give the usual
  refusal, the same as for any account, so that the message never tells a stranger that an account
  exists or has expired (N7).
- **FR-049** [CHANGE]: When an account expires, the system shall keep its account and academic data
  unchanged.
- **FR-050** [CHANGE]: The system shall let the admin change an account's last day of access and
  extend it, reactivating an expired account without deleting data, and record the change.
- **FR-051** [CHANGE]: When an account expires during an active PvP match, the system shall close the
  match as abandoned, with no rating change for either player, keep the answers saved before, and
  tell both players why.
- **FR-052** [CHANGE]: The system shall close a match and apply an expiry atomically and idempotently,
  so that a match ends once, in one state, whatever arrives first.

The initial import's requirements are spec 009's; the numbers they left are not reused.

**E5 — session renewal (US9)**

- **FR-080** [CHANGE]: The system shall serve authentication — login, renewal, logout — from the
  application's own origin through a proxy to the backend, so that no step depends on a
  third-party cookie.
- **FR-081** [CHANGE]: The system shall keep the renewal cookie `HttpOnly` and `Secure`, scoped to the
  authentication paths, with the `SameSite` policy of the same-origin flow, and delete it on logout
  with the same attributes. *(Today it is `SameSite=None` for a cross-origin flow and logout
  deletes it without `Secure`/`SameSite` — `api/routers/auth.py:60-68,146`.)*
- **FR-082** [CHANGE]: The system shall refuse authentication requests from other origins and mark
  every authentication response as not cacheable. *(Today there is no origin check and no
  `Cache-Control` on them.)*
- **FR-083** [AS-IS]: The access token shall last 15 minutes (`api/config.py:19`).
- **FR-084** [CHANGE]: When a renewal is attempted with revoked credentials or for an expired or
  inactive account, the system shall refuse it at once.
- **FR-085** [CHANGE]: The system shall keep WebSocket connections authenticated by their first
  message, checked against the security version and the account's state, independent of the HTTP
  proxy.

**E6 — rate-limit store continuity (US10)**

- **FR-090** [CHANGE]: If the shared rate-limit store fails while the API runs, then the system shall
  count the limits in process memory with the same configured values, only while one process
  serves.
- **FR-091** [CHANGE]: The system shall call the store with configurable connect and operation
  timeouts, stop calling it on every request once a failure is known, and probe its recovery at a
  controlled interval.
- **FR-092** [CHANGE]: When the store recovers, the system shall return to it carrying over what was
  counted in memory, so that no key gets a new allowance.
- **FR-093** [CHANGE]: The system shall log entering and leaving the degraded mode once each.
- **FR-094** [CHANGE]: `/api/health` shall report the limits as normal or degraded, without internal
  addresses or credentials, answering 200 while the database and the limits work, and 503 when the
  database fails or the limits cannot be applied.
- **FR-095** [CHANGE]: If neither the store nor the fallback can apply a limit, then the system shall
  refuse the limited request.
- **FR-096** [AS-IS]: Where the API runs in production, the system shall refuse to start without the
  shared store's configuration (`api/config.py:93`).

### Key Entities

- **Account**: username, password hash, role, approved, active; new: security version,
  must-change-password flag and display name — required for every new student account (N11),
  possibly empty on existing accounts, which keep working. New and optional, never needed for an
  account to work: the last day of access. The import's identification is spec 009's.
- **Audit record**: who, when, operation identifier, affected accounts by internal ID, result per
  row; never passwords or files.
- **Limit counters**: per normalised account and global (login), per address (public sign-up), per
  admin (creations); shared store with a temporary memory fallback.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % of each delivery's scenarios are reproduced by automated checks; those that
  depend on stored data run on SQLite and PostgreSQL with identical results.
- **SC-002**: 30 students sign in from one address within one minute with 0 refusals; 100 % of
  attempts beyond the 10th per account and the 300th overall within a minute are refused.
- **SC-004**: After expiry, revocation or reset, 0 earlier credentials work — access token,
  renewal or persistent connection.
- **SC-005**: 0 responses addressed to a student or a teacher carry the username of another student
  who has a display name.
- **SC-007**: Session renewal works on Safari (iPhone, iPad, desktop) and the other supported
  browsers, each check labelled automated or real device.

The import's criteria, once SC-003 and SC-006 here, are spec 009's.

## Assumptions

- Test data uses invented identifications only; the repository is public.
- Existing accounts keep username, password, data and progress, and keep working without a display
  name or a last day of access; one without a display name shows its username (N5). They are test
  accounts (owner, 2026-10-14).

## New Decisions and Contradictions (not assumed approved)

| # | Delivery | Point | Recommendation |
|---|---|---|---|
| N1 | E1 | "Per normalised account", as E1 implements it: username and email of one account count together; an identifier naming no account is counted under itself after trimming outer spaces and ignoring letter case (FR-006). | **Approved** (owner, 2026-10-14). |
| N2 | E1 | Public registration's own per-address limit had no value; E1 uses 20 per minute (`RATE_LIMIT_REGISTER`), the previous one. Behind the hosting proxy it may count every client as one address (LuisJRubioH/LevelUp-ELO#60); no forwarded header is trusted. | **Approved** (owner, 2026-10-14): 20 per minute, no forwarded header trusted. |
| N3 | E1/E2 | P1 was approved for E1, but a created teacher must change a temporary password at first access, which is E2's mechanism (FR-030). | **Approved** (owner, 2026-10-14): teachers are created in E2. |
| N5 | E2 | With N12 decided, an existing account without a display name still has to be shown somehow: by its own username (never an identification for these accounts) or by a neutral alias. | **Decided** (owner, 2026-10-14): its username; the existing accounts are test accounts. |
| N6 | E5 | The hosting proxy for the same origin (Vercel rewrites) does not carry WebSockets, so PvP and notifications keep connecting to the API's origin (token in the first message, no cookie); streaming answers (KatIA) must be checked through the proxy. | **Approved** (owner, 2026-10-14). |
| N7 | E3 | When does an expired account see P7's message («El período de acceso de tu cuenta terminó…»)? Shown for any password, anyone who types a username learns that the account exists and has expired — and for the import's accounts the username is an identification number. | **Approved** (owner, 2026-10-14): only after the right password; with a wrong one, the usual «usuario o contraseña incorrectos». |
| N8 | E6 | Render's health check reads only the status code, so a degraded 200 alerts nobody; "monitors read the body" needs an external monitor. | Operational step for the owner, listed apart. |
| N11 | E2 | (Question A, 2026-10-14.) The display name outside the initial import — public registration, teachers created by the admin, students created one by one: optional or mandatory? | **Decided** (owner, 2026-10-14): not optional — every new student account has one; a student who registers chooses it under the name filter (N17). |
| N12 | E2 | (Question B.) Accounts without a linked identification — the existing ones and those with their own credentials: what do classmates and teachers see? | **Decided**: the display name, never an identification; an imported account without one shows a neutral alias. Existing accounts without one: N5. **Amended** (owner, 2026-10-14, night): no alias — an import row without a name is an error (spec 009). |
| N13 | E3 | (Question C.) Students created one by one by the admin, outside the import: (1) own credentials — the admin picks the username, a temporary password with a forced change, group and last day optional; (2) also credentials based on the identification when the admin chooses; (3) in the first version only the import creates students. | **Decided**: (1); the import keeps its own credentials. |
| N14 | E2 | (Question D.) P5: is changing the display name reserved to the admin for every account, or only for the initial import's? | **Decided**: only for the initial import's accounts (spec 009); the owner of any other account changes their own, under the filter. |
| N15 | E3 | (Question E.) P8: is an existing group mandatory for students created one by one too? | **Decided**: mandatory for every student — created one by one, imported or semillero. **Scope** (owner, 2026-10-14, night): at creation by the admin; public registration, existing accounts, deleting a group and reassigning a student keep today's behaviour. |
| N17 | E2 | The name filter («censuras lógicas»): what it refuses. | **Decided** (owner, 2026-10-14): long names with hyphens are allowed (names that are not Spanish); offensive and mocking words in Spanish and English are refused, compared without accents or letter case; the admin can always correct a name. Recommended limits, not set by the owner: 2 to 80 characters of letters of any language, spaces, apostrophes and hyphens. |

## Out of Scope *(mandatory)*

- The initial import from Google Forms: spec 009 (owner, 2026-10-14).
- Credentials based on an identification for teachers or admins.
- Requiring an existing account, or any account outside the initial import, to link an
  identification or to receive a last day of access, a group or credentials based on the
  identification (owner, 2026-10-14).
- Requiring a group of publicly registered students or of existing accounts, or changing how a
  group is deleted or a student reassigned (N15, owner 2026-10-14).
- A display name for teachers or admins: not decided; N11 covers student accounts.
- Blocks 5 and 7 (spec 001: LuisJRubioH/LevelUp-ELO#62, LuisJRubioH/LevelUp-ELO#65) and block 6
  (KatIA, spec 005).
- The rest of the roadmap's spec 004 area until a feature needs it: password recovery by the
  student, group membership (I7, I8), the student-route role boundary (I11), test and demo
  accounts (I12, I13), changing a student's level or grade (I14), hashing cost (I17).
- Rating effects of any account action — spec 001. Persistence mechanics — spec 002. The PvP match
  lifecycle beyond FR-051/FR-052 — spec 007.
- Deployment: code, configuration and guides are prepared; the owner deploys.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario. Reuse adequate existing tests; create or strengthen tests where coverage is missing.**
Nothing new is implemented yet; `[AS-IS]` rows cite the existing tests that pin them.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | E1 | `tests/integration/test_spec004_e1_registration.py::test_spec004_public_registration_is_closed_by_default` |
| US1-AS2 | E1 | `frontend/e2e/auth.spec.ts › con el registro público cerrado, login no ofrece crear cuenta (spec 004 US1-AS2, FR-003)` |
| US1-AS3 | E1 | `tests/integration/test_spec004_e1_registration.py::test_spec004_registration_opens_only_through_its_setting`<br>`frontend/e2e/auth.spec.ts › con el registro público abierto, el formulario está accesible desde login (spec 004 US1-AS3)` |
| US1-AS4 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_registration_has_its_own_per_address_limit` |
| US1-AS5 | E1 | `tests/api/test_admin.py::TestPendingTeachers::test_approve_teacher` |
| US2-AS1 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_thirty_students_on_one_address_sign_in` |
| US2-AS2 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_the_eleventh_attempt_on_one_account_is_refused` |
| US2-AS3 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_the_global_ceiling_refuses_every_extra_attempt` |
| US2-AS4 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_a_refusal_does_not_reveal_whether_the_account_exists` |
| US2-AS5 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_login_limits_follow_their_settings` |
| US3-AS1 | E2 | `PENDING` |
| US3-AS2 | E2 | `PENDING` |
| US3-AS3 | E2 | `PENDING` |
| US3-AS4 | E2 | `PENDING` |
| US3-AS5 | E2 | `PENDING` |
| US3-AS6 | E2 | `PENDING` |
| US3-AS7 | E2 | `PENDING` |
| US3-AS8 | E2 | `PENDING` |
| US4-AS1 | E2 | `PENDING` |
| US4-AS2 | E2 | `PENDING` |
| US4-AS3 | E2 | `PENDING` |
| US5-AS1 | E2 | `PENDING` |
| US5-AS2 | E2 | `PENDING` |
| US5-AS3 | E2 | `PENDING` |
| US5-AS4 | E2 | `PENDING` |
| US6-AS1 | E3 | `PENDING` |
| US6-AS2 | E3 | `PENDING` |
| US6-AS3 | E3 | `PENDING` |
| US6-AS4 | E3 | `PENDING` |
| US6-AS5 | E3 | `PENDING` |
| US7-AS1 | E3 | `PENDING` |
| US7-AS2 | E3 | `PENDING` |
| US7-AS3 | E3 | `PENDING` |
| US7-AS4 | E3 | `PENDING` |
| US7-AS5 | E3 | `PENDING` |
| US7-AS6 | E3 | `PENDING` |
| US7-AS7 | E3 | `PENDING` |
| US9-AS1 | E5 | `PENDING` |
| US9-AS2 | E5 | `PENDING` |
| US9-AS3 | E5 | `PENDING` |
| US9-AS4 | E5 | `PENDING` |
| US9-AS5 | E5 | `PENDING` |
| US10-AS1 | E6 | `PENDING` |
| US10-AS2 | E6 | `PENDING` |
| US10-AS3 | E6 | `PENDING` |
| US10-AS4 | E6 | `tests/api/test_production_config.py::test_insecure_production_configuration_is_rejected` |
| US10-AS5 | E6 | `PENDING` |
| FR-001 | E1 | `tests/integration/test_spec004_e1_registration.py::test_spec004_public_registration_is_closed_by_default` |
| FR-002 | E1 | `tests/integration/test_spec004_e1_registration.py::test_spec004_registration_opens_only_through_its_setting` |
| FR-003 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_registration_state_is_public`<br>`frontend/e2e/auth.spec.ts › con el registro público cerrado, login no ofrece crear cuenta (spec 004 US1-AS2, FR-003)`<br>`frontend/e2e/auth.spec.ts › con el registro público abierto, el formulario está accesible desde login (spec 004 US1-AS3)` |
| FR-004 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_registration_has_its_own_per_address_limit` |
| FR-005 | E1 | `tests/api/test_admin.py::TestPendingTeachers::test_approve_teacher`<br>`tests/integration/test_spec004_e1_registration.py::test_spec004_registration_opens_only_through_its_setting` |
| FR-006 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_the_eleventh_attempt_on_one_account_is_refused`<br>`tests/integration/test_spec004_e1_registration.py::test_spec004_login_account_id_names_one_active_account` |
| FR-007 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_the_global_ceiling_refuses_every_extra_attempt` |
| FR-008 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_thirty_students_on_one_address_sign_in` |
| FR-009 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_login_limits_follow_their_settings`<br>`tests/api/test_spec004_e1_login_limits.py::test_spec004_the_global_ceiling_refuses_every_extra_attempt` |
| FR-010 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_a_refusal_does_not_reveal_whether_the_account_exists` |
| FR-011 | E1 | `tests/api/test_spec004_e1_login_limits.py::test_spec004_limits_keep_no_readable_identifier` |
| FR-012 | E1 | `tests/api/test_production_config.py::test_insecure_production_configuration_is_rejected` |
| FR-020 | E2 | `PENDING` |
| FR-021 | E2 | `PENDING` |
| FR-022 | E2 | `PENDING` |
| FR-023 | E2 | `PENDING` |
| FR-024 | E2 | `PENDING` |
| FR-025 | E2 | `PENDING` |
| FR-026 | E2 | `PENDING` |
| FR-027 | E2 | `PENDING` |
| FR-028 | E2 | `PENDING` |
| FR-029 | E2 | `PENDING` |
| FR-030 | E2 | `PENDING` |
| FR-031 | E2 | `PENDING` |
| FR-032 | E2 | `PENDING` |
| FR-033 | E2 | `PENDING` |
| FR-040 | E3 | `PENDING` |
| FR-043 | E3 | `PENDING` |
| FR-044 | E3 | `PENDING` |
| FR-045 | E3 | `PENDING` |
| FR-046 | E3 | `PENDING` |
| FR-047 | E3 | `PENDING` |
| FR-048 | E3 | `PENDING` |
| FR-049 | E3 | `PENDING` |
| FR-050 | E3 | `PENDING` |
| FR-051 | E3 | `PENDING` |
| FR-052 | E3 | `PENDING` |
| FR-080 | E5 | `PENDING` |
| FR-081 | E5 | `PENDING` |
| FR-082 | E5 | `PENDING` |
| FR-083 | E5 | `PENDING` |
| FR-084 | E5 | `PENDING` |
| FR-085 | E5 | `PENDING` |
| FR-090 | E6 | `PENDING` |
| FR-091 | E6 | `PENDING` |
| FR-092 | E6 | `PENDING` |
| FR-093 | E6 | `PENDING` |
| FR-094 | E6 | `PENDING` |
| FR-095 | E6 | `PENDING` |
| FR-096 | E6 | `tests/api/test_production_config.py::test_insecure_production_configuration_is_rejected` |
