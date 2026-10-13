# Feature Specification: Identity & Access — School Accounts

**Feature Branch**: `004-identity` (one branch per delivery once implementation starts)

**Created**: 2026-10-13

**Status**: Draft for review — all approved decisions of blocks 4 and 8 and of the rate-limit
store (owner, 2026-10-13) are specified. E1 and E6 are implemented and closed (their pull
requests); E2 … E5 are `planned`.

**Input**: The owner's approved orders of 2026-10-13: block 4 (enrolment through Google Forms,
account creation and access limits) with its clarifications P1–P15 and supplementary precisions,
block 8 (Safari-compatible session renewal) and the decision on LuisJRubioH/LevelUp-ELO#59
(continuity of the limits when Redis fails). Background: the as-is survey
`docs/sdd/identity-survey.md` (LuisJRubioH/LevelUp-ELO#37), cited as I1 … I19, and the read-only
research of 2026-10-13 cited with `file:line` on `redesign @ 1d6fcf6`.

**Outcome served** (constitution VIII): the school, not the public, decides who has an account. A
student gets a working account without signing up or inventing a password, keeps it until the last
day the school sets, is shown to classmates by a name and never by identification number, and can
keep a session open on any supported browser — Safari included — for as long as the account and
its credentials are valid. Teachers trust that the students they see are theirs.

## Code Scope *(mandatory)*

The code whose behaviour this spec defines. A path shared with another spec belongs to both.

- `api/routers/auth.py` — login, public registration, refresh, logout, password change
- `api/schemas/auth.py`
- `api/rate_limit.py` — the limits and their store
- `api/config.py` — the settings of limits, registration and sessions
- `api/dependencies.py` — the per-request account check
- `api/main.py` — `/api/health`
- `api/routers/admin.py` — administrative creation, import, reset, expiration
- `api/routers/student.py` — names in rankings and PvP history; the student's own identification
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
| **E2** | Display name everywhere classmates look; who sees the identification; password change; security version that revokes tokens, renewals and persistent connections; admin password reset; teachers created by the admin | Before any real student is created (decision 5). Teachers created by the admin need its forced password change (N3). | planned |
| **E3** | Temporary student accounts created one by one: identification as username and initial password, existing group, level and grade, display name, last day of access; expiration enforced, also on open sessions and PvP; the admin changes, extends or reactivates | Not merged before E2 is in production. | planned |
| **E4** | Import of a Google Forms export (`.xlsx`, `.csv`): mapping, preview, confirmation, re-import without changes, linking, audit, own limits | After E3, whose creation rules it reuses. | planned |
| **E5** | Session renewal without third-party cookies (block 8): same-origin proxy, cookie scope, CSRF, no caching, revocation and expiry respected; Safari verified | After E2 (revocation). E3's tests include renewal of an expired account. | planned |
| **E6** | Rate-limit store continuity (constitution 1.1.0): temporary memory fallback, timeouts, controlled recovery, no new allowance, health state | After LuisJRubioH/LevelUp-ELO#63; replaces the code of LuisJRubioH/LevelUp-ELO#59. Same file as E1: one after the other. | closed |

## Clarifications

### Session 2026-10-13 (owner orders and clarifications, approved)

Recorded as given; the delivery that turns each into requirements is in brackets.

**Block 4 — enrolment, account creation and access limits**

- Q: How do students enrol? → A: through a Google Form; the admin downloads the responses and
  imports the `.xlsx` or `.csv` from the admin panel, mapping the file's columns to the
  application's fields and choosing the group and the expiration. Every account of this flow is a
  student. [E4]
- Q: What are a temporary student's credentials? → A: by the product owner's decision, the
  identification number is both the username and the initial password, with no change required at
  first access; the student may change it later. The password is stored only with the existing
  secure hash, never readable in the database, logs or import reports. [E3, E4; change: E2]
- Q: How is the identification read? → A: as text of digits, keeping leading zeros; only outer
  spaces are removed; other formats are flagged for correction; ambiguous values or values altered
  by Excel are rejected, never rebuilt. It never appears in rankings or classmates' views. [E3, E4]
- Q: What happens before saving an import? → A: a preview of new accounts, existing accounts,
  duplicates and errors per row; nothing is saved until the admin confirms. Existing students are
  detected by an identification already linked; re-importing never duplicates accounts, resets
  passwords, changes groups, extends expirations or overwrites progress — updates of existing
  accounts need an explicit administrative action. The result is shown and recorded: who, when,
  how many accounts were created or skipped. [E4]
- Q: How long is an account valid? → A: temporary accounts require an expiration, set per batch and
  changeable per account by the admin, shown in Colombian time. Once expired, sign-in and
  authenticated access stop, even from an open session; academic data is kept; the admin can
  extend or reactivate. [E3]
- Q: Is public registration open? → A: closed by default by a server-side control; it can be
  enabled explicitly if needed. Individual creation and import stay available with registration
  closed, through the application's validations and services — no manual inserts. [E1; creation:
  E3, E4]
- Q: Which limits? → A: separate limits for login, public registration and import. Login: per
  normalised account and a configurable global ceiling, initially 10 per account and 300 overall
  per minute, to be verified against the expected concurrency; blocks are temporary. Public
  registration, when enabled, has its own per-address limit. The import has its own administrative
  controls able to load a whole class. [E1, E4]
- Q: What must tests prove? → A: 30 students sign in from one address within one minute; repeated
  attempts against one account are limited; re-importing a file duplicates no student and changes
  no credential or progress; closed registration is enforced on the server while administrative
  creation goes on; an expired account loses access, also from an open session; identifications
  keep their leading zeros. Parity between SQLite and PostgreSQL; the storage of the limits
  documented for the final repository; no deployment. [all]

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

**P4 — origin of the display name** [E2, E3, E4]: mandatory for new accounts and imports, taken
from a form column and reviewable by the admin; never the identification, not even as a fallback.
Existing accounts without one use, for now, a neutral alias not derived from their identification.
Repeated display names are allowed.

**P5 — changing the display name** [E2]: reserved to the admin and recorded; independent of the
username used to sign in.

**P6 — password reset** [E2]: the admin resets with a random temporary password that must be
changed at first access; every earlier session is invalidated; the operation is recorded —
responsible, account, time — never the password. Tests prove earlier tokens stop working, public
names never expose the identification, and only authorised roles change names or reset access.

**P7 — expiration and message** [E3]: the admin gives the last day of access, inclusive, in
Colombian time. From the start of the next day authenticated access is blocked and the student
sees «El período de acceso de tu cuenta terminó. Tu progreso está guardado. Contacta al
administrador si necesitas ampliar el acceso.» Extending never deletes data.

**P8 — group** [E3, E4]: an existing group is required for every new temporary student, created
individually or imported. No group is created automatically from errors or variations in a file.

**P9 — level and grade** [E3, E4]: from mapped columns or from values chosen explicitly for the
batch; shown in the preview; combinations validated; «No aplica» admitted where it applies; never
deduced silently from the group's name.

**P10 — identification format** [E3, E4]: text of digits, leading zeros kept; only outer spaces
removed; other formats flagged for correction; ambiguous or Excel-altered values rejected without
rebuilding them.

**P11 — students with an existing account** [E4]: existing accounts and their progress are kept;
matches by an identification already linked; explicit administrative linking where it is missing;
never merged by name; credentials never reset by an import; changing the group or the expiration
of an existing account needs a specific confirmation.

**P12 — administrative limits** [E3, E4]: separate from public registration and login. Initially:
30 individual creations per minute per admin; files up to 500 students and 5 MB; one import
running per admin. A full load is verified and retries never duplicate accounts. Configurable. If
the server cannot process 500 students reliably, the result is reported before lowering the limit
or changing the processing.

**P13 — traceability checker** [done: LuisJRubioH/LevelUp-ELO#64]: requirements recognised
whatever their formatting; deliveries explicit; nothing exigible in a delivery may stay `PENDING`
when it closes.

**P14 — who sees the identification** [E2]: each student their own; the admin for management;
teachers use the display name and the group; never other students, nor any response meant for
public or shared views.

**P15 — expiration during a PvP match** [E3]: a match still active when an account expires is
closed as abandoned, with no rating effect for either participant; results validly saved before
the expiry are kept; closing and expiring are atomic and idempotent, with concurrency tests and
clear messages for both players.

**Audit** [E2, E3, E4]: the admin responsible, date and time, an operation identifier, the
affected accounts by internal ID and each row's result; never passwords or the whole file.

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

**Why this priority**: the identification is the initial password (E3), so the account is the unit
to protect; today the only login limit counts 20 per minute per address (`api/config.py:63`), so a
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

### User Story 3 - Classmates see my name, never my identification (Priority: P1) — E2

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** a group ranking, **When** a student opens it, **Then** each classmate
   appears by display name and the response holds no other student's username or identification.
2. **US3-AS2** — **Given** a PvP match or history, **When** a student sees the rival, **Then** it is
   the rival's display name, and no message carries their username or identification.
3. **US3-AS3** — **Given** an existing account without a display name, **When** a classmate sees
   it, **Then** it appears by a neutral alias not derived from its identification.
4. **US3-AS4** — **Given** a teacher's views of their students, **When** they load, **Then** each
   student appears by display name and group, without identification.
5. **US3-AS5** — **Given** a student, **When** they open their profile, **Then** they see their own
   identification; the admin sees it for management.
6. **US3-AS6** — **Given** the admin, **When** they change a display name, **Then** it changes and the
   change is recorded; a student or teacher who tries is refused.

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

### User Story 6 - The admin creates a temporary student (Priority: P1) — E3

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** an identification `0012345678`, an existing group, level and grade, a
   display name and a last day of access, **When** the admin creates the student, **Then** the
   student signs in with `0012345678` as username and password, with no forced change, and the
   leading zeros are kept.
2. **US6-AS2** — **Given** an identification with inner spaces, dots, letters or an Excel-altered
   form, **When** the admin creates the student, **Then** it is refused for correction and nothing
   is created.
3. **US6-AS3** — **Given** no group, a group that does not exist, a missing display name, a missing
   last day, or an invalid level and grade combination, **When** the admin creates the student,
   **Then** it is refused and nothing is created.
4. **US6-AS4** — **Given** an identification already used as a username or linked to an account,
   **When** the admin creates the student, **Then** it is refused and nothing changes.
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

### User Story 8 - The admin imports a class from a Forms export (Priority: P1) — E4

**Acceptance Scenarios**:

1. **US8-AS1** — **Given** a `.xlsx` or `.csv` up to 5 MB and 500 students, **When** the admin
   uploads it, maps its columns, chooses an existing group, the last day of access and, unless
   mapped, level and grade, **Then** a preview lists each row as new, existing, duplicate or error,
   with its level and grade, and nothing is saved.
2. **US8-AS2** — **Given** a preview, **When** the admin confirms, **Then** exactly the new rows
   become temporary students with the identification as username and initial password, and the
   result shows how many were created and skipped.
3. **US8-AS3** — **Given** the same file imported again, **When** it is confirmed, **Then** no
   account is duplicated and no password, group, last day or progress changes.
4. **US8-AS4** — **Given** identifications with leading zeros, **When** they are imported from a CSV
   or from text cells of an `.xlsx`, **Then** the zeros are kept; a numeric cell is flagged.
5. **US8-AS5** — **Given** a student with an account but no linked identification, **When** the
   admin links it explicitly, **Then** later imports find it; nothing is ever merged by name.
6. **US8-AS6** — **Given** an existing account whose group or last day differs in the file, **When**
   the admin confirms that change specifically, **Then** only that change is applied.
7. **US8-AS7** — **Given** a confirmed import, **When** the audit is read, **Then** it names the
   admin, the time, the operation and each row's result with internal account IDs, and holds no
   password and not the file.
8. **US8-AS8** — **Given** an import running, **When** the same admin starts another or retries the
   confirmation, **Then** it is refused or returns the first result, and nothing is duplicated.
9. **US8-AS9** — **Given** a student or a teacher, **When** they reach the import, **Then** they are
   refused.

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

**E2 — display name and identification (US3)**

- **FR-020** [CHANGE]: The system shall give every account a display name, independent of the
  username, which may repeat across accounts.
- **FR-021** [CHANGE]: When the system shows a student to another student — rankings, PvP rival and
  history, any classmates' view — it shall show the display name, and no response or message
  addressed to a student shall carry another student's username or identification.
  *(Today: `frontend/src/pages/Student/Stats.tsx:257`, `League.tsx:142,171,243`,
  `api/websocket/pvp.py:331,335`.)*
- **FR-022** [CHANGE]: While an existing account has no display name, the system shall show a
  neutral alias not derived from its identification.
- **FR-023** [CHANGE]: When a teacher's views show a student, the system shall show the display name
  and group, without identification.
- **FR-024** [CHANGE]: The system shall show a student their own identification and the admin any
  student's, and no one else.
- **FR-025** [CHANGE]: When the admin changes a display name, the system shall apply and record it;
  if anyone else tries, it shall refuse.

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

- **FR-040** [CHANGE]: When the admin creates a temporary student, the system shall require an
  identification, a display name, an existing group, a level and a grade (or «No aplica» where it
  applies, combinations validated) and a last day of access, and shall create the account through
  the application's services and validations, never by a direct insert.
- **FR-041** [CHANGE]: The system shall read an identification as text of digits, keep its leading
  zeros, remove only outer spaces, and refuse for correction any other format, ambiguous value or
  value altered by a spreadsheet, without rebuilding it.
- **FR-042** [CHANGE]: When a temporary student is created, the system shall set the identification
  as username and as initial password, link it to the account, and not require a change at first
  access.
- **FR-043** [CHANGE]: If the identification is already a username or linked to an account, then the
  system shall refuse the creation and change nothing.
- **FR-044** [CHANGE]: The new student shall join the chosen group; no group is created by a
  creation or an import.
- **FR-045** [CHANGE]: When an admin exceeds 30 individual creations per minute (configurable), the
  system shall refuse the extra creations until the minute ends.

**E3 — expiration (US7)**

- **FR-046** [CHANGE]: The system shall store a temporary account's last day of access, inclusive,
  interpreted and shown in Colombian time.
- **FR-047** [CHANGE]: From the start of the day after the last day, the system shall refuse the
  account's sign-in, renewals, authenticated requests and persistent connections.
- **FR-048** [CHANGE]: When an expired account signs in with the right password, the system shall
  answer «El período de acceso de tu cuenta terminó. Tu progreso está guardado. Contacta al
  administrador si necesitas ampliar el acceso.» [NEEDS CLARIFICATION: N7]
- **FR-049** [CHANGE]: When an account expires, the system shall keep its account and academic data
  unchanged.
- **FR-050** [CHANGE]: The system shall let the admin change an account's last day of access and
  extend it, reactivating an expired account without deleting data, and record the change.
- **FR-051** [CHANGE]: When an account expires during an active PvP match, the system shall close the
  match as abandoned, with no rating change for either player, keep the answers saved before, and
  tell both players why.
- **FR-052** [CHANGE]: The system shall close a match and apply an expiry atomically and idempotently,
  so that a match ends once, in one state, whatever arrives first.

**E4 — import (US8)**

- **FR-060** [CHANGE]: When the admin uploads a `.xlsx` or `.csv` of at most 5 MB and 500 students,
  the system shall list its columns and let the admin map the identification, the display name
  and, optionally, level and grade, and choose an existing group, the last day of access and the
  batch's level and grade where not mapped. *(Which columns the form has is to be confirmed.)*
- **FR-061** [CHANGE]: Before saving, the system shall show each row as new, existing, duplicate (in
  the file) or error with its reason, with the level and grade it would get.
- **FR-062** [CHANGE]: The system shall save nothing until the admin confirms the preview, and then
  create exactly the rows shown as new through the same rules as FR-040 … FR-044.
- **FR-063** [CHANGE]: When a file is imported again, the system shall create no duplicate and change
  no password, group, last day of access or progress of an existing account.
- **FR-064** [CHANGE]: The system shall match existing students only by an identification already
  linked; let the admin link one explicitly; and never merge accounts by name.
- **FR-065** [CHANGE]: If the file gives an existing account another group or last day, then the
  system shall apply it only after the admin confirms that change specifically.
- **FR-066** [CHANGE]: When an import is confirmed, the system shall record the admin, the date and
  time, an operation identifier, and each row's result with the internal ID of the account
  affected — never passwords and never the file.
- **FR-067** [CHANGE]: The system shall run at most one import per admin at a time, return the first
  result to a retried confirmation, and keep the import's controls separate from the login and
  registration limits.
- **FR-068** [CHANGE]: The system shall keep no uploaded file after its import is confirmed or
  abandoned, and write no identification or display name to the application logs.
- **FR-069** [CHANGE]: If anyone other than the admin uses the import, then the system shall refuse.

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

- **Account**: username, password hash, role, approved, active; new: display name, linked
  identification, security version, must-change-password flag, last day of access.
- **Identification**: text of digits kept as given (leading zeros), unique among linked accounts.
- **Audit record**: who, when, operation identifier, affected accounts by internal ID, result per
  row; never passwords or files.
- **Import**: one confirmed file's operation; the file itself is not kept.
- **Limit counters**: per normalised account and global (login), per address (public sign-up), per
  admin (creations, imports); shared store with a temporary memory fallback.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % of each delivery's scenarios are reproduced by automated checks; those that
  depend on stored data run on SQLite and PostgreSQL with identical results.
- **SC-002**: 30 students sign in from one address within one minute with 0 refusals; 100 % of
  attempts beyond the 10th per account and the 300th overall within a minute are refused.
- **SC-003**: Re-importing a confirmed file creates 0 accounts and changes 0 credentials, groups,
  last days or progress records.
- **SC-004**: After expiry, revocation or reset, 0 earlier credentials work — access token,
  renewal or persistent connection.
- **SC-005**: 0 responses addressed to a student contain another student's identification or
  username.
- **SC-006**: A file of 500 students is imported completely and reliably, or the measured result is
  reported before the limit or the processing changes (P12).
- **SC-007**: Session renewal works on Safari (iPhone, iPad, desktop) and the other supported
  browsers, each check labelled automated or real device.

## Assumptions

- Test data uses invented identifications only; the repository is public.
- Existing accounts keep username, password and data; E2 gives them a neutral alias until the
  admin sets a display name; E3 gives no existing account an expiration.
- Collecting minors' identifications requires the guardians' authorisation and a privacy notice
  (Colombian Law 1581 of 2012) — the school's process; deleting the form's responses file after the
  import is the school's step.

## New Decisions and Contradictions (not assumed approved)

| # | Delivery | Point | Recommendation |
|---|---|---|---|
| N1 | E1 | "Per normalised account", as E1 implements it: username and email of one account count together; an identifier naming no account is counted under itself after trimming outer spaces and ignoring letter case (FR-006). | Confirm. |
| N2 | E1 | Public registration's own per-address limit had no value; E1 uses 20 per minute (`RATE_LIMIT_REGISTER`), the previous one. Behind the hosting proxy it may count every client as one address (LuisJRubioH/LevelUp-ELO#60); no forwarded header is trusted. | Confirm the value. |
| N3 | E1/E2 | P1 was approved for E1, but a created teacher must change a temporary password at first access, which is E2's mechanism (FR-030). | Create teachers in E2. Until then a new teacher signs up while the server setting opens registration (P2) and is approved, as today. |
| N4 | E3/E4 | P10 admits digits only, so identifications with letters (passport, PPT, some foreign documents) cannot be created or imported. | Confirm, or allow the admin to type such a username by hand for those students. |
| N5 | E2 | P4's neutral alias also replaces the self-chosen usernames classmates see today for existing accounts. | Confirm; a format such as «Estudiante 4821», from the internal ID, not the identification. |
| N6 | E5 | The hosting proxy for the same origin (Vercel rewrites) does not carry WebSockets, so PvP and notifications keep connecting to the API's origin (token in the first message, no cookie); streaming answers (KatIA) must be checked through the proxy. | Keep WebSockets direct and add an origin check to them (FR-085); verify KatIA's stream through the proxy. |
| N7 | E3 | Showing the expiry message only after the right password avoids revealing which accounts exist; with a wrong password the answer is the usual one. | Confirm. |
| N8 | E6 | Render's health check reads only the status code, so a degraded 200 alerts nobody; "monitors read the body" needs an external monitor. | Operational step for the owner, listed apart. |
| N9 | E6 | FR-091 asked for configurable timeouts and a controlled probe without values. E6 uses 0.5 s to connect and 0.5 s per operation, no client retries, a background probe at most every 10 s and at most 50 000 counters in memory (`RATE_LIMIT_STORAGE_*`, `RATE_LIMIT_FALLBACK_MAX_KEYS`). | Confirm the values. |
| N10 | E6 | During an outage the store cannot be read, so a key counted just before it starts from zero in memory (up to one more window's allowance while Redis is down); FR-092 holds on return. | Confirm; reading the store's counts is impossible while it is down. |

## Out of Scope *(mandatory)*

- Forcing students created with their identification to change it at first access (decision).
- Credentials based on the identification for teachers or admins.
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
| US8-AS1 | E4 | `PENDING` |
| US8-AS2 | E4 | `PENDING` |
| US8-AS3 | E4 | `PENDING` |
| US8-AS4 | E4 | `PENDING` |
| US8-AS5 | E4 | `PENDING` |
| US8-AS6 | E4 | `PENDING` |
| US8-AS7 | E4 | `PENDING` |
| US8-AS8 | E4 | `PENDING` |
| US8-AS9 | E4 | `PENDING` |
| US9-AS1 | E5 | `PENDING` |
| US9-AS2 | E5 | `PENDING` |
| US9-AS3 | E5 | `PENDING` |
| US9-AS4 | E5 | `PENDING` |
| US9-AS5 | E5 | `PENDING` |
| US10-AS1 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_api_limits_and_health_during_an_outage`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_store_calls_are_bounded_by_their_timeouts` |
| US10-AS2 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_recovery_carries_memory_counts_over_to_the_store` |
| US10-AS3 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_without_store_or_fallback_limited_requests_are_refused` |
| US10-AS4 | E6 | `tests/api/test_production_config.py::test_insecure_production_configuration_is_rejected` |
| US10-AS5 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_entering_and_leaving_are_logged_once_each` |
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
| FR-041 | E3 | `PENDING` |
| FR-042 | E3 | `PENDING` |
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
| FR-060 | E4 | `PENDING` |
| FR-061 | E4 | `PENDING` |
| FR-062 | E4 | `PENDING` |
| FR-063 | E4 | `PENDING` |
| FR-064 | E4 | `PENDING` |
| FR-065 | E4 | `PENDING` |
| FR-066 | E4 | `PENDING` |
| FR-067 | E4 | `PENDING` |
| FR-068 | E4 | `PENDING` |
| FR-069 | E4 | `PENDING` |
| FR-080 | E5 | `PENDING` |
| FR-081 | E5 | `PENDING` |
| FR-082 | E5 | `PENDING` |
| FR-083 | E5 | `PENDING` |
| FR-084 | E5 | `PENDING` |
| FR-085 | E5 | `PENDING` |
| FR-090 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_limits_keep_applying_from_memory_when_the_store_fails`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_memory_fallback_needs_a_single_process`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_the_api_limiter_uses_the_failover_with_a_shared_store` |
| FR-091 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_no_request_calls_the_store_once_its_failure_is_known`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_store_calls_are_bounded_by_their_timeouts`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_a_failed_probe_keeps_the_fallback` |
| FR-092 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_recovery_carries_memory_counts_over_to_the_store`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_a_failed_probe_keeps_the_fallback` |
| FR-093 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_entering_and_leaving_are_logged_once_each` |
| FR-094 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_health_reports_the_limits_state`<br>`tests/api/test_spec004_e6_limit_store.py::test_spec004_api_limits_and_health_during_an_outage`<br>`tests/api/test_health.py::test_health_returns_503_without_exposing_database_error` |
| FR-095 | E6 | `tests/api/test_spec004_e6_limit_store.py::test_spec004_without_store_or_fallback_limited_requests_are_refused` |
| FR-096 | E6 | `tests/api/test_production_config.py::test_insecure_production_configuration_is_rejected` |
