# Feature Specification: Identity & Access — School Accounts

**Feature Branch**: `004-identity`

**Created**: 2026-10-13

**Status**: Draft — `/speckit-specify` of the approved part of the owner's block 4, for review.
Nothing here is implemented yet.

**Input**: The owner's block 4 (import of students from a Google Forms export in Excel or CSV,
temporary accounts, credentials, expiration and access limits — brief §1–§7) with the owner's
decisions; the review of that brief against `redesign @ 1d6fcf6` (2026-10-12); and the as-is
survey `docs/sdd/identity-survey.md` (LuisJRubioH/LevelUp-ELO#37), whose findings are cited as
I1 … I19.

**Outcome served** (constitution VIII): the school, not the public, decides who has an account.
A student receives a working account without having to sign up or invent a password, keeps it
only for as long as the school intends, and is shown to classmates by name, never by
identification number. Teachers can then trust that the students they see are their students.

This is the first time a feature touches identity, so under the roadmap's lean scope this spec
covers only what block 4 changes. The rest of the roadmap's spec 004 area (§ Out of Scope) enters
by amendment when a feature needs it.

## Code Scope *(mandatory)*

The code whose behaviour this spec defines. A pull request that changes any of these paths, or a
test file cited in § Traceability, is a code change for this spec whatever its branch. An entry
ending in `/` covers everything below it. Paths shared with spec 001 belong to both.

- `api/routers/auth.py` — login, self-registration, password change
- `api/schemas/auth.py`
- `api/rate_limit.py` — login limits
- `api/dependencies.py` — the per-request account check that expiration relies on
- `api/routers/admin.py` — account creation and import
- `api/routers/student.py` — names in the group ranking and the PvP history
- `api/websocket/pvp.py` — the rival's name
- `src/application/interfaces/repositories.py`
- `src/infrastructure/persistence/` — accounts in both repositories
- `frontend/src/api/auth.ts`
- `frontend/src/pages/Login.tsx`
- `frontend/src/pages/Admin/Users.tsx`
- `frontend/src/pages/Student/Stats.tsx`
- `frontend/src/pages/Student/League.tsx`
- `frontend/src/hooks/usePvpMatch.ts`

Each part adds the files it creates (§ Delivery).

## Delivery in four parts *(read first)*

The traceability check rejects **all** of a spec's `PENDING` rows on every code pull request for
that spec (AGENTS.md § Spec-driven development: "the check is per spec, not per row"). A spec with
four parts written as checked requirements would therefore block part A's code until part D's
tests existed, and would block every other pull request that touches the shared files above.

So this spec states every approved requirement now, for one review, but each part's requirements
and scenarios become **checked** — bold ID and a § Traceability row — in the pull request that
implements that part, together with its tests. Until then they are written with plain IDs
(`FR-001`, `US1-AS1`), which the check does not read. The IDs are final: activating a part only
makes them bold and adds their rows.

| Part | Content | Brief | Requirements | State |
|---|---|---|---|---|
| A | Self-registration closed; accounts created by the admin; login limits per account | §5, §6 | US1, US2 · FR-001 … FR-014 | planned |
| B | Account expiration | §4 | US3 · FR-015 … FR-019 | planned |
| C | Display name between students; password change | — | US4, US5 · FR-020 … FR-026 | planned |
| D | Import from a Google Forms export: column mapping, preview, confirmation, audit | §1–§3 | US6 · FR-027 … FR-036 | planned |

Part A is what the switch to the redesign needs (LuisJRubioH/LevelUp-ELO#3): with the redesign in
production, today's public sign-up is open to anyone. Each part's tests run on SQLite and
PostgreSQL (brief §7, SC-001).

**Order constraint.** Until part C is in production, a student created with the identification as
username appears by that username in rankings and PvP. Real students are therefore created —
individually or by import — only once part C is in production, or parts A and C ship together;
until then, part A's individual creation serves teachers and test accounts.

## Clarifications

### Session 2026-10-12/13 (owner decisions on block 4, recorded before `/speckit-specify`)

- Q: Who creates accounts? → A: the school. Public self-registration is closed on the server
  (brief §5); students are created by import (part D) or individually by the admin, who can also
  create teachers, since self-registration was the only way to create one (part A).
- Q: What are a student's credentials? → A: the username is the student's identification number,
  and the initial password is that same identification. The student can change it (part C).
- Q: How do classmates see each other? → A: by a display name, which accounts do not have today;
  every view between students shows it instead of the username (part C).
- Q: Are accounts permanent? → A: no; an account can expire (brief §4, part B).
- Q: Which limits apply? → A: login limits per account (brief §6, part A).

Five further questions from the same review are **not decided** and are not specified here
(§ Out of Scope, D1 … D5). Where a requirement depends on one, it says so.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Only the school creates accounts (Priority: P1) — part A

Nobody can create an account from the login screen or the API. The admin creates students one by
one (and teachers), with the identification as username and initial password.

**Why this priority**: once the redesign is in production, anyone who finds the sign-up can create
a student or a pending teacher account (`api/routers/auth.py:79-92`). Closing it is needed on the
day of the switch, and closing it requires another way to create accounts.

**Independent Test**: a sign-up request creates nothing; an account created by the admin signs in.

**Acceptance Scenarios**:

1. US1-AS1 **Given** any caller, signed in or not, **When** they send a self-registration request
   to the API, **Then** it is refused and no account is created.
2. US1-AS2 **Given** the login screen, **When** it loads, **Then** it offers no way to create an
   account.
3. US1-AS3 **Given** the admin, **When** they create a student with an identification, a level and,
   for semillero, a grade, **Then** the student signs in with the identification as both username
   and password.
4. US1-AS4 **Given** the admin, **When** they create a teacher, **Then** the teacher signs in
   without a separate approval step.
5. US1-AS5 **Given** the admin, **When** they create a semillero student without a grade from 6 to
   11, or an account whose username already exists, **Then** it is refused and nothing changes.
6. US1-AS6 **Given** a student or a teacher, **When** they request an account creation, **Then** it
   is refused and nothing is created.
7. US1-AS7 **Given** a teacher who registered before the closure and is pending approval, **When**
   the admin approves them, **Then** they can sign in, as today.

---

### User Story 2 - Guessing a password is limited per account (Priority: P1) — part A

Repeated failed logins against one account are stopped, wherever they come from, and a class
signing in together from the school's single address is not stopped.

**Why this priority**: with the identification as initial password (US1), the account is the unit
to protect. Today the only login limit counts per address (20 per minute, `api/config.py:63`), and
behind the hosting proxy every client may share one address (§ Edge Cases).

**Independent Test**: failed logins against one account are refused after the limit while another
account still signs in; a class-sized burst of correct logins from one address all succeed.

**Acceptance Scenarios**:

1. US2-AS1 **Given** an account, **When** its failed logins reach the limit within the window, from
   any addresses, **Then** further logins for it are refused until the window ends, even with the
   right password, and other accounts are unaffected.
2. US2-AS2 **Given** an identifier that matches no account, **When** its failed logins reach the
   limit, **Then** the refusal looks the same as for an existing account.
3. US2-AS3 **Given** a class of students signing in from one address within one minute, **When**
   each enters the right password once, **Then** none is refused by a limit.
4. US2-AS4 **Given** a production configuration whose limit counters are kept in process memory,
   **When** the API starts, **Then** it refuses to start, as today.

---

### User Story 3 - An account stops working when it expires (Priority: P2) — part B

A temporary account works until its expiration date and then neither signs in nor keeps a session
open. Nothing it did is lost.

**Why this priority**: block 4 creates accounts for a course or a period; the school needs them to
end without deleting anyone's work.

**Independent Test**: an account past its expiration date is refused at login and on its next
request; its ratings and attempts are unchanged.

**Acceptance Scenarios**:

1. US3-AS1 **Given** an account whose expiration has passed, **When** it signs in with the right
   password, **Then** it is refused.
2. US3-AS2 **Given** a signed-in account that expires, **When** its next request, session refresh
   or realtime connection arrives after the expiration, **Then** it is refused.
3. US3-AS3 **Given** an expired account, **When** its data is read, **Then** its ratings, attempts,
   enrolments and submissions are unchanged.
4. US3-AS4 **Given** an account without an expiration date (every account that exists today),
   **When** it signs in, **Then** it works as today.

---

### User Story 4 - Classmates see my name, not my identification (Priority: P1) — part C

Rankings and PvP show each student by a display name. A student's identification never reaches
another student's screen or browser.

**Why this priority**: once the username is the identification (US1), every place that shows a
username to other students would publish identification numbers of minors: the group ranking
(`frontend/src/pages/Student/Stats.tsx:257`), the PvP rival (`League.tsx:142,171`,
`api/websocket/pvp.py:331,335`) and the PvP history (`League.tsx:243`,
`postgres_repository.py:4096`, `sqlite_repository.py:3494`).

**Independent Test**: the ranking and PvP responses a student receives contain other students'
display names and no other student's username.

**Acceptance Scenarios**:

1. US4-AS1 **Given** a group ranking, **When** a student opens it, **Then** every other student
   appears by display name, and the response contains no other student's username.
2. US4-AS2 **Given** a PvP match, **When** two students are paired, **Then** each sees the other's
   display name, and no message carries the rival's username.
3. US4-AS3 **Given** a PvP history, **When** a student opens it, **Then** each rival appears by
   display name.
4. US4-AS4 **Given** an account without a display name (every account created before part C),
   **When** another student sees it, **Then** it appears by its username, as today.

---

### User Story 5 - I can change my password (Priority: P1) — part C

A student (or teacher) replaces the initial password with one only they know.

**Why this priority**: the initial password is the identification, which classmates may know from
class lists or ID cards. Today no endpoint or screen changes a password (I15).

**Independent Test**: after a change, the new password signs in and the old one does not.

**Acceptance Scenarios**:

1. US5-AS1 **Given** a signed-in user, **When** they give their current password and a valid new
   one, **Then** the new one signs in and the old one is refused.
2. US5-AS2 **Given** a signed-in user, **When** the current password they give is wrong, **Then**
   the change is refused and the password is unchanged.
3. US5-AS3 **Given** a signed-in user, **When** the new password is shorter than the account rule
   allows, **Then** the change is refused and the password is unchanged.
4. US5-AS4 **Given** a student or a teacher, **When** they open their screens, **Then** they find
   where to change their password.

---

### User Story 6 - The admin creates a class from a Forms export (Priority: P2) — part D

The admin uploads the responses of the school's Google Form, exported as Excel or CSV, says which
column holds each field, reviews what will be created and confirms.

**Why this priority**: it is how a whole class gets accounts at once; individual creation (US1)
covers the day of the switch and the exceptions.

**Independent Test**: a file with valid and invalid rows previews each row's outcome, creates
nothing until confirmed, then creates exactly the valid rows and records the import.

**Acceptance Scenarios**:

1. US6-AS1 **Given** a Forms export as `.xlsx` or `.csv`, **When** the admin uploads it, **Then**
   its columns are listed and the admin maps each account field to one of them.
2. US6-AS2 **Given** a mapped file, **When** the preview is shown, **Then** each row says whether
   its account will be created or why it will not, and no account exists yet.
3. US6-AS3 **Given** a preview, **When** the admin confirms it, **Then** exactly the rows shown as
   creatable become accounts with the identification as username and initial password and the
   mapped display name, and the admin sees how many were created and refused.
4. US6-AS4 **Given** a row whose identification is already a username, or repeats an earlier row of
   the file, **When** the preview is shown, **Then** that row is shown as refused and is never
   created.
5. US6-AS5 **Given** a confirmed import, **When** the audit is read, **Then** it records who
   imported, when, and how many rows were created and refused.
6. US6-AS6 **Given** the preview is abandoned, **When** nothing is confirmed, **Then** no account is
   created and the file is not kept.
7. US6-AS7 **Given** a student or a teacher, **When** they upload a file to the import, **Then** it
   is refused.

---

### Edge Cases

- **A class signs in at once from the school's one public address.** Today 20 logins per minute
  per address are allowed (`api/config.py:63`); the 21st student of the minute is refused (US2-AS3).
- **Behind the hosting proxy, the API may not see the client's address.** Reproduced locally with
  uvicorn 0.53 (the version installed by `requirements-api.txt`): a request arriving from a
  non-loopback proxy is keyed by the proxy's address whatever `X-Forwarded-For` says; trusting
  every proxy instead (`FORWARDED_ALLOW_IPS='*'`) keys it by the left-most `X-Forwarded-For` entry,
  which a client can write. Render's start command (`render.yaml:23`) sets neither. A limit keyed
  only by address is therefore either shared by every user or avoidable; the per-account limit
  (FR-011) does not depend on it. Which address the limits see in production is for the plan to
  establish.
- **An expiration passes during a session.** The next request, refresh or new realtime connection
  is refused (FR-016). Whether an already open PvP match is cut at that instant is not specified
  here. [NEEDS CLARIFICATION: open realtime connection at expiry — recommendation: let the match in
  progress finish; every later request is refused]
- **A password change while another session is open** (for example, a classmate who signed in with
  the identification). Today a session lives up to 7 days through its refresh token and nothing
  ends it early (survey § 2). [NEEDS CLARIFICATION: does a password change end the account's other
  sessions? — recommendation: yes, since it is the remedy for the risk of US5]
- **Between preview and confirmation another account takes a row's username.** That row is refused
  at confirmation and reported with the others (FR-031).
- **Leading zeros, thousands separators or scientific notation in the identification column of a
  spreadsheet.** How identifications are read and normalised is decision D2.
- **A student who already signed up alone appears in the file.** Their old account has no
  identification; what the import does with them is decision D1.

## Requirements *(mandatory)*

### Functional Requirements

Plain IDs: planned, checked when their part is implemented (§ Delivery).

**Part A — accounts are created by the school (US1)**

- FR-001 [CHANGE]: If anyone sends a self-registration request, then the system shall refuse it and
  create no account. *(Today `POST /api/auth/register` creates a student, or a teacher pending
  approval, for any caller — `api/routers/auth.py:79-92`.)*
- FR-002 [CHANGE]: The login screen shall offer no way to create an account. *(Today it has a
  «Crear cuenta» tab — `frontend/src/pages/Login.tsx:328`.)*
- FR-003 [CHANGE]: When the admin creates a student account, the system shall set its username to
  the student's identification and its initial password to that same identification.
  [NEEDS CLARIFICATION: D2 — accepted identification formats and their normalisation]
- FR-004 [CHANGE]: When the admin creates an account, the system shall let them choose the role
  student or teacher, and for a student the level and, for semillero, the grade.
  [NEEDS CLARIFICATION: brief — whether a teacher's username and initial password follow FR-003]
- FR-005 [CHANGE]: When the admin creates a teacher account, the system shall create it approved.
- FR-006 [CHANGE]: If the admin creates a semillero student without a grade from 6 to 11, then the
  system shall refuse it. *(Spec 001 FR-028m states this rule for registration and says it moves
  to spec 004; part A moves it.)*
- FR-007 [CHANGE]: If an account creation would use a username that already exists, then the
  system shall refuse it and change nothing.
- FR-008 [CHANGE]: If a user other than the admin requests an account creation, then the system
  shall refuse it and create nothing.
- FR-009 [AS-IS]: While a teacher account is pending approval, the system shall let the admin
  approve or reject it (`api/routers/admin.py:40-61`).
- FR-010 [AS-IS]: The system shall store every password, including an initial one, as an Argon2id
  hash (`src/infrastructure/security/hashing_service.py:13-16`; constitution VI).

**Part A — login limits (US2)**

- FR-011 [CHANGE]: When the failed logins for one account identifier reach the limit within the
  window, the system shall refuse further logins for that identifier until the window ends,
  whatever address they come from and without checking the password.
  [NEEDS CLARIFICATION: brief §6 — the limit and the window]
- FR-012 [CHANGE]: The system shall answer a login refused by FR-011 identically whether or not an
  account with that identifier exists.
- FR-013 [CHANGE]: While the students of one class sign in from a single address, the system shall
  not refuse a correct login because of a per-address limit, for a class of up to [NEEDS
  CLARIFICATION: brief §6 — class size] students signing in within one minute. *(Today 20 per
  minute per address, `api/config.py:63`.)*
- FR-014 [AS-IS]: Where the API runs in production, the system shall refuse to start while its
  limit counters are kept in process memory (`api/config.py:93`).

**Part B — expiration (US3)**

- FR-015 [CHANGE]: The system shall let an account carry an expiration date.
  [NEEDS CLARIFICATION: brief §4 — who sets it, when (individual creation, import, later), and
  whether the admin can change it]
- FR-016 [CHANGE]: While an account is past its expiration, the system shall refuse its login, its
  session refresh, each of its authenticated requests and each new realtime connection.
  [NEEDS CLARIFICATION: D3 — the instant an expiration date ends and what the refusal says]
  *(The API already re-reads the account on every authenticated request and realtime
  authentication — `api/dependencies.py:134-148`.)*
- FR-017 [CHANGE]: When an account expires, the system shall keep the account and all its data
  unchanged.
- FR-018 [AS-IS]: While an account has no expiration date, the system shall treat it as it does
  today; no existing account receives an expiration date from this spec.
- FR-019 [AS-IS]: If an inactive account signs in, then the system shall refuse it with the same
  answer as a wrong password (`api/routers/auth.py:43-47`).

**Part C — display name (US4)**

- FR-020 [CHANGE]: When the school creates a student account, individually or by import, the
  system shall require a display name and store it with the account.
- FR-021 [CHANGE]: When the system shows a student to another student — in a group ranking, as a
  PvP rival or in a PvP history — it shall show the display name.
- FR-022 [CHANGE]: The system shall not send another student's username in any response or message
  addressed to a student about rankings or PvP.
- FR-023 [CHANGE]: While an account has no display name (one created before part C), the system
  shall show its username in its place.

**Part C — password change (US5)**

- FR-024 [CHANGE]: When a signed-in user gives their current password and a new one, the system
  shall replace the password, so that only the new one signs in.
- FR-025 [CHANGE]: If the current password given is wrong, or the new one is shorter than 6
  characters after trimming (the account rule today, `postgres_repository.py:1476-1478`), then
  the system shall refuse the change and keep the password.
- FR-026 [CHANGE]: The student and teacher screens shall offer the password change. *(Today only
  the admin layout offers any account setting — I15.)*

**Part D — import (US6)**

- FR-027 [CHANGE]: When the admin uploads a Google Forms export as `.xlsx` or `.csv`, the system
  shall list its columns and let the admin map each account field to one of them: identification,
  display name, level, grade [NEEDS CLARIFICATION: brief §1 — the full list of fields the form
  collects and which are required].
- FR-028 [CHANGE]: Before creating anything, the system shall show a preview that gives each row's
  outcome: created, or refused with its reason.
- FR-029 [CHANGE]: The system shall create no account from a file until the admin confirms its
  preview.
- FR-030 [CHANGE]: When the admin confirms a preview, the system shall create exactly the rows it
  showed as creatable, each with the credentials of FR-003 and its mapped display name, and shall
  report how many rows were created and refused.
- FR-031 [CHANGE]: If a row's identification is already a username, or repeats an earlier row of
  the file, then the system shall show it as refused and not create it; a username taken between
  preview and confirmation is refused at confirmation and reported.
- FR-032 [CHANGE]: If a row breaks a rule of individual creation (FR-003, FR-006), then the system
  shall show it as refused with that rule as its reason.
- FR-033 [CHANGE]: When an import is confirmed, the system shall record who imported, when, and
  how many rows were created and refused. [NEEDS CLARIFICATION: brief §3 — anything else the audit
  keeps]
- FR-034 [CHANGE]: The system shall not keep the uploaded file once its import is confirmed or
  abandoned.
- FR-035 [CHANGE]: If a user other than the admin uploads a file to the import, then the system
  shall refuse it.
- FR-036 [CHANGE]: The system shall not write a row's identification or display name to the
  application logs.

### Key Entities

- **Account**: username (the identification for accounts the school creates), password hash, role,
  level, grade, active, approved; new here: display name and expiration date.
- **Identification**: the student's identity document number as the school records it; the
  username of a school-created student. Its accepted formats are decision D2.
- **Display name**: what other students see (part C).
- **Import**: one confirmed file — who, when, counts of rows created and refused (part D). The
  uploaded file itself is not an entity: it is not kept (FR-034).
- **Login limit counter**: failed logins per identifier within a window, kept in the shared limit
  store in production (FR-011, FR-014).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 100 % of each part's acceptance scenarios, an automated check reproduces the
  outcome; every scenario that depends on stored data runs on SQLite and PostgreSQL with identical
  results (brief §7).
- **SC-002**: After part A, 0 accounts can be created by anyone other than the admin.
- **SC-003**: A class of the size fixed for FR-013 signs in within one minute from one address with
  0 refusals, while 100 % of logins against one account beyond the FR-011 limit are refused.
- **SC-004**: After an account's expiration, 0 of its requests, refreshes or new realtime
  connections succeed, and 0 of its rows change.
- **SC-005**: 0 responses or messages addressed to a student about rankings or PvP contain another
  student's username.
- **SC-006**: An import whose preview shows K creatable rows creates 0 accounts before
  confirmation and exactly K after it.

## Assumptions

- **Defaults chosen in this draft, open to `/speckit-clarify`**: a teacher created by the admin is
  approved (FR-005); a limited login does not reveal whether an account exists (FR-012);
  expiration deletes nothing (FR-017); the uploaded file is not kept (FR-034); an account without
  a display name shows its username (FR-023).
- **Existing data is kept**: no existing account changes username, password, expiration or
  display name because of this spec (FR-018, FR-023).
- **V1** is frozen and is disconnected during the switch (`docs/transfer.md` § 3.1). Its own
  sign-up form (`src/interface/streamlit/views/auth_view.py`) writes to the same database and is
  not closed by this spec. If V1 is ever reconnected, its sign-up must be closed or V1 kept
  without it — decided then.
- **Test data uses invented identifications only.** The repository is public: no real
  identification, name or form export appears in tests, fixtures, logs or CI artifacts.
- The import's cost is bounded by the password hashing of FR-010 (64 MiB and about 0.24 s of CPU
  per new password, at most two at a time since LuisJRubioH/LevelUp-ELO#35; survey I17). The file
  size it accepts is decision D5.

### Risks (recorded, not decided here)

- **Password = identification.** Anyone who knows a classmate's identification (class lists, ID
  cards) can sign in as them until the password is changed; the per-account limit does not stop
  someone who knows the password. Mitigations (for example a notice while the initial password is
  unchanged) are not specified.
- **Minors' personal data (Colombian Law 1581 of 2012).** Collecting minors' identifications
  through a form requires the guardians' authorisation and a privacy notice; that is the school's
  process, outside this software. The software side is FR-034 and FR-036; deleting the responses
  file from the form's storage after the import is the school's step.

## Out of Scope *(mandatory)*

- **Decisions D1 … D5 of the 2026-10-12 review, until the owner decides them**: D1 students who
  already have a self-created account; D2 identification formats and normalisation; D3 the
  expiration instant and message; D4 who else (teachers, admin) sees the identification; D5 the
  import's size limit or background processing. Each enters by amendment.
- **Block 5** (showing the current rating after the diagnostic) — spec 001, its own amendment.
- **Blocks 6, 7 and 8** of the owner's plan — under discussion.
- The rest of the roadmap's spec 004 area, until a feature needs it (survey § 5): username and
  email normalisation (I1, I2), password recovery, admin powers (I4–I6), group membership
  (I7, I8), auditing other actions (I9), the student-route role boundary (I11), test and demo
  accounts (I12, I13), changing a student's level or grade (I14), session lifetime and revocation
  beyond the edge case above, and hashing cost (I17).
- What teachers' and the admin's screens show — decision D4.
- Rating effects of any account action — spec 001. Persistence mechanics — spec 002. AI keys and
  limits — spec 005. Teacher console — spec 006. The PvP match lifecycle — spec 007 (only the
  rival's name is here).
- V1, beyond the assumption above.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario. Reuse adequate existing tests; create or strengthen tests where coverage is missing.**

Rows are added when each part is activated (§ Delivery), with tests that exist and pass in that
part's pull request. No requirement is checked yet.

| Requirement / Scenario | Test |
|---|---|
