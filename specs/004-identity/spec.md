# Feature Specification: Identity & Access — School Accounts

**Feature Branch**: `004-identity`

**Created**: 2026-10-13

**Status**: Draft — `/speckit-specify` + owner decisions of 2026-10-13, for review. Requirements
of delivery E1 only; nothing implemented yet.

**Input**: The owner's block 4 (students enrolled through Google Forms and imported by the admin,
temporary accounts, credentials, expiration, access limits) and the owner's decisions of
2026-10-13; the review of block 4 against `redesign @ 1d6fcf6` (2026-10-12); the as-is survey
`docs/sdd/identity-survey.md` (LuisJRubioH/LevelUp-ELO#37), whose findings are cited as I1 … I19.

**Outcome served** (constitution VIII): the school, not the public, decides who has an account. A
student receives a working account without signing up or inventing a password, keeps it only
until the date the school sets, and is shown to classmates by a name, never by identification
number. Teachers can trust that the students they see are their students.

This is the first time a feature touches identity, so under the roadmap's lean scope this spec
covers only block 4. The rest of the roadmap's spec 004 area (§ Out of Scope) enters by amendment
when a feature needs it.

## Code Scope *(mandatory)*

The code whose behaviour this spec defines **so far** (delivery E1). A pull request that changes
any of these paths, or a test file cited in § Traceability, is a code change for this spec
whatever its branch. Each later delivery's amendment adds the files it changes (§ Deliveries).

- `api/routers/auth.py` — login and self-registration
- `api/rate_limit.py` — login limits
- `api/config.py` — the limit settings
- `frontend/src/pages/Login.tsx`
- `frontend/src/api/auth.ts`

## Deliveries *(mandatory for this spec)*

Block 4 is delivered in four steps. Every step follows the project's rules unchanged: its
requirements and scenarios enter this spec as checked IDs (bold, each with a § Traceability row)
in a docs pull request, where rows may say `PENDING`; its code pull request then replaces every
`PENDING` row with tests that exist and pass. Only **E1** has requirements in this version. The
owner decisions behind E2–E4 are recorded now in § Clarifications; their requirements are written
in each step's amendment, after its pending decisions (§ Pending Owner Decisions) are settled.

| Step | Content | Decisions it implements | Order rule |
|---|---|---|---|
| **E1** | Self-registration closed on the server; login limits per account and global | 6 | Needed for the switch (LuisJRubioH/LevelUp-ELO#3). Creates no account. |
| **E2** | Display name in every view between students; password change; a password change or reset ends the account's other sessions | 2 (change), 5 | Must be in production before any real student is created (decision 5). |
| **E3** | Temporary student accounts: individual creation by the admin (identification as username and initial password, mandatory expiration); expiration enforced; admin changes or extends it | 2, 4 | Not merged before E2 is in production. |
| **E4** | Import from a Google Forms export (`.xlsx`, `.csv`): column mapping, destination group and expiration, preview, confirmation, re-import without changes, audit | 1, 3 | After E3, whose creation rules it reuses. |

**One amendment in flight at a time.** The traceability check rejects every `PENDING` row of this
spec on any pull request that changes its Code Scope (AGENTS.md § Spec-driven development). E1's
scope is identity files only, so while E1 is in flight it blocks only identity work, which should
merge first (LuisJRubioH/LevelUp-ELO#33, LuisJRubioH/LevelUp-ELO#35, LuisJRubioH/LevelUp-ELO#38,
LuisJRubioH/LevelUp-ELO#24 touch these files). E3 and E4 must add both repositories to the Code
Scope; while either is in flight, every pull request that touches a repository would fail, whatever
its spec. How to avoid blocking unrelated work then is decision P13.

## Clarifications

### Session 2026-10-13 (owner decisions on block 4)

Recorded as given; the step that turns each into requirements is in brackets.

1. **Enrolment and data.**
   - Q: How do students enrol? → A: through a Google Form; the admin imports its responses from
     Excel (`.xlsx`) or CSV in the admin panel. [E4]
   - Q: Which fields does the form have? → A: only the identification number is confirmed. The
     import lets the admin map columns to fields; which other columns exist is still to be
     confirmed, and none is assumed. [E4]
   - Q: What does the admin choose during an import? → A: the destination group and the
     expiration. [E4]
   - Q: How is the identification read? → A: as text, keeping leading zeros; duplicates are
     detected within the file and against existing accounts. [E3, E4]
2. **Credentials and their reach.**
   - Q: What are a temporary student's credentials? → A: the identification is the username and
     the initial password, with no forced change at first sign-in; the student can change it
     later. An explicit decision of the product owner. [E3, E4; the change: E2]
   - Q: How is the password stored? → A: only with the existing secure hash; never readable in the
     database, logs or reports. [E3, E4]
   - Q: Whom does it cover? → A: individual creation and import of **students** only. Credentials
     based on the identification never apply to teachers or administrators. The admin creating
     teachers was not part of the approved scope. [E3, E4]
3. **Import and audit.**
   - Q: What happens before saving? → A: a preview of new accounts, existing accounts, duplicates
     and errors, row by row; nothing is saved without the admin's confirmation. [E4]
   - Q: What does a re-import do? → A: it never duplicates accounts and never changes the
     password, groups, expiration or progress of an existing account; those changes need an
     explicit administrative action. [E4]
   - Q: What is audited? → A: the admin responsible, date and time, an operation identifier, the
     affected accounts by internal ID and each row's result; never passwords or the whole file.
     [E4]
4. **Expiration.**
   - Q: Who sets it? → A: the admin, mandatorily, when creating a temporary account or importing
     a batch; the admin can change it per account and extend it. It is shown in Colombian time.
     [E3, E4]
   - Q: What does it block? → A: new sign-ins, session renewals and authenticated access from
     sessions already open. Academic data is kept. [E3]
   - Q: Does a PvP match in progress finish? → A: no exception: the connection is closed and the
     match is treated by the existing disconnection or abandonment rules, with no new rating
     effect; any case those rules leave open is documented (§ Edge Cases). [E3]
5. **Display name and sessions.**
   - Q: Where may the identification appear? → A: never in rankings, PvP or any other view of
     classmates. That protection is in place before real students are created: E2 ships before
     E3 (or creation stays unavailable until it does). Where the display name comes from is still
     to be confirmed. [E2]
   - Q: What does a password change or reset do to other sessions? → A: it ends them, including
     their ability to renew. How this reaches access tokens still within their lifetime is to be
     specified (P3). [E2]
6. **Registration and limits.**
   - Q: Is public registration open? → A: closed by default and blocked on the server.
     Administrative creation stays available, with its own permissions and limits. [E1; creation:
     E3]
   - Q: Which login limits? → A: 10 sign-in attempts per account per minute and a global ceiling
     of 300 per minute, both configurable. The per-account counter was not defined as counting
     only failed attempts. [E1]
   - Q: What is the minimum check? → A: 30 different students sign in from the same IP address
     within one minute and none is blocked for sharing the network. [E1]
   - Q: And the import? → A: a class import has its own controls, independent of the login
     limits. [E4]
7. **Delivery.** Steps are allowed, without formatting tricks to get around traceability; any
   change to the checker is proposed explicitly with its scope (P13).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nobody creates an account by themselves (Priority: P1) — E1

Neither the login screen nor the API lets anyone create an account. Accounts that already exist
keep working as today.

**Why this priority**: once the redesign is in production, anyone who finds the sign-up can create
a student, or a teacher pending approval (`api/routers/auth.py:79-92`).

**Independent Test**: a self-registration request creates nothing; existing accounts sign in.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** any caller, signed in or not, **When** they send a self-registration
   request to the API, **Then** it is refused and no account is created.
2. **US1-AS2** — **Given** the login screen, **When** it loads, **Then** it offers no way to create
   an account.
3. **US1-AS3** — **Given** a teacher who registered before the closure and is pending approval,
   **When** the admin approves them, **Then** they can sign in, as today.

---

### User Story 2 - Login limits protect each account without blocking a class (Priority: P1) — E1

Repeated sign-in attempts against one account are stopped wherever they come from, a flood of
attempts against the service is capped, and a class signing in together from the school's single
address is not stopped.

**Why this priority**: with the identification as initial password (E3) the account is the unit to
protect. Today the only login limit counts per address (20 per minute, `api/config.py:63`): the
21st student of a class signing in within one minute from the school's address is refused, and
behind the hosting proxy every user may share one address (§ Edge Cases).

**Independent Test**: the 11th attempt in a minute against one account is refused while another
account signs in; 30 students from one address sign in; the 301st attempt in a minute is refused.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** an account, **When** its 11th sign-in attempt within one minute arrives,
   right password or not, from any address, **Then** it is refused, and another account still
   signs in.
2. **US2-AS2** — **Given** an identifier that matches no account, **When** its 11th attempt within
   one minute arrives, **Then** the refusal is identical to the one of US2-AS1.
3. **US2-AS3** — **Given** 30 different students on one IP address, **When** each signs in once with
   the right password within one minute, **Then** all 30 succeed.
4. **US2-AS4** — **Given** 300 sign-in attempts within one minute, from any accounts and addresses,
   **When** the 301st arrives, **Then** it is refused.
5. **US2-AS5** — **Given** other values in the settings, **When** the API starts, **Then** both
   limits follow them.
6. **US2-AS6** — **Given** a production configuration whose limit counters live in process memory,
   **When** the API starts, **Then** it refuses to start, as today.

---

### Edge Cases

- **The hosting proxy hides the client's address.** Reproduced locally with uvicorn 0.53 (the
  version `requirements-api.txt` installs): behind a proxy that is not on loopback, every request
  is counted under the proxy's address; trusting every proxy (`FORWARDED_ALLOW_IPS='*'`) counts the
  left-most `X-Forwarded-For` entry, which a client can write. E1 keeps no per-address login limit
  (FR-006), so neither case affects sign-in; no header is trusted for it.
- **An account with an email** can sign in with its username or its email: both count toward the
  same account's limit (FR-004).
- **Attempts above the limit with the right password** are refused too, until the minute ends; the
  agreed counter counts every attempt (decision 6). No change to that is proposed.
- **A teacher who needs an account after the closure** has no way to get one: self-registration
  was the only way to create teachers, and the admin creating teachers is outside the approved
  scope. Decision P1.
- **V1's own sign-up form** (`src/interface/streamlit/views/auth_view.py`) writes to the same
  database and is not closed by this spec; V1 is disconnected during the switch
  (`docs/transfer.md` § 3.1). If V1 is ever reconnected, its sign-up must be closed first.

## Requirements *(mandatory)*

### Functional Requirements

**E1 — self-registration closed (US1)**

- **FR-001** [CHANGE]: If anyone sends a self-registration request, then the system shall refuse
  it and create no account. *(Today `POST /api/auth/register` creates a student, or a teacher
  pending approval, for any caller — `api/routers/auth.py:79-92`.)* Whether a server setting may
  reopen it is decision P2; by default it is closed.
- **FR-002** [CHANGE]: The login screen shall offer no way to create an account. *(Today it has a
  «Crear cuenta» tab — `frontend/src/pages/Login.tsx:328`.)*
- **FR-003** [AS-IS]: While a teacher account is pending approval, the system shall let the admin
  approve or reject it (`api/routers/admin.py:40-61`).

**E1 — login limits (US2)**

- **FR-004** [CHANGE]: When an account receives more sign-in attempts within one minute than the
  per-account limit (default 10), counting every attempt — right or wrong password, by username or
  by email, from any address — the system shall refuse the extra attempts without checking the
  password until the minute ends.
- **FR-005** [CHANGE]: When the service receives more sign-in attempts within one minute than the
  global limit (default 300), across all accounts and addresses, the system shall refuse the extra
  attempts without checking the password until the minute ends.
- **FR-006** [CHANGE]: The system shall not refuse a sign-in because other users share its address:
  no per-address limit applies to sign-in. *(Today 20 per minute per address,
  `api/config.py:63`.)*
- **FR-007** [CHANGE]: The system shall take both limits of FR-004 and FR-005 from settings, with
  defaults 10 and 300 per minute.
- **FR-008** [CHANGE]: The system shall answer an attempt refused by FR-004 identically whether or
  not an account with that identifier exists.
- **FR-009** [CHANGE]: The system shall not keep an identifier or email in readable form in the
  limit counters, nor write it to the logs when a limit refuses an attempt.
- **FR-010** [AS-IS]: Where the API runs in production, the system shall refuse to start while its
  limit counters are kept in process memory (`api/config.py:93`).

### Key Entities

- **Sign-in attempt counter**: attempts per account per minute, and all attempts per minute, kept
  in the shared limit store in production (FR-004, FR-005, FR-010). Holds no readable identifier
  (FR-009).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 100 % of E1's acceptance scenarios, an automated check reproduces the outcome.
- **SC-002**: After E1, 0 accounts can be created through self-registration.
- **SC-003**: 30 students sign in from one address within one minute with 0 refusals, while 100 %
  of attempts beyond the 10th per account and the 300th overall within a minute are refused.

## Assumptions

- **Defaults chosen in this draft, open to review**: a limited attempt does not reveal whether an
  account exists (FR-008); the limit store and the logs hold no readable identifier (FR-009).
- Existing accounts keep their username and password; E1 changes no stored data.
- Test data uses invented identifications only. The repository is public: no real
  identification, name or form export appears in tests, fixtures, logs or CI artifacts.
- E1's code pull request moves the tests that create accounts through self-registration (8 calls,
  in `tests/api/test_auth.py`, `tests/api/test_student.py`,
  `tests/integration/test_spec001_catalogue.py`,
  `tests/integration/test_postgres_production_guards.py`) to the repository, and turns the
  registration form test of `frontend/e2e/auth.spec.ts` into US1-AS2.

### Risks (recorded, not decided here)

- **Password = identification** (decision 2). Anyone who knows a classmate's identification can
  sign in as them until the password is changed; the per-account limit does not stop someone who
  knows the password. Mitigations beyond E2's password change are not specified.
- **Minors' personal data (Colombian Law 1581 of 2012).** Collecting minors' identifications
  through a form requires the guardians' authorisation and a privacy notice; that is the school's
  process, outside this software. Deleting the responses file from the form's storage after the
  import is the school's step.

## Pending Owner Decisions

Each needs the owner's answer before the step named. A recommendation is not a decision.

| # | Step | Question | Recommendation |
|---|---|---|---|
| P1 | E1 | How is a new teacher's account created once self-registration closes? | A script the owner runs on the server, like the admin password reset of LuisJRubioH/LevelUp-ELO#15, until a teacher-creation feature is approved. |
| P2 | E1 | "Closed by default": may a server setting reopen self-registration, or is it removed for good? | No setting: reopening becomes a reviewed code change (constitution VII). |
| P3 | E2 | How does ending other sessions reach access tokens still within their 15 minutes? | Every request already re-reads the account (`api/dependencies.py:134-148`): tokens carry the account's credential version, and a token older than the account's current version is refused at its next use — access and refresh alike. The session that made the change gets a new pair. Open realtime connections of the account close within 30 s. |
| P4 | E2, E4 | Where does the display name come from? | At individual creation the admin types it; at import, a mapped column that the form must include (the import refuses a mapping without it). |
| P5 | E2 | May the display name be changed later, and by whom? | By the admin only. |
| P6 | E2, E3 | Is the admin's password reset of a student in scope, and to what value? | Yes, back to the identification, ending other sessions (decision 5). |
| P7 | E3 | Does the admin choose a date (valid until 23:59:59 that day, Colombian time) or a date and time? What does an expired account see on signing in? | A date. The «cuenta vencida» message only after the right password, so it does not reveal which accounts exist. |
| P8 | E3 | Does individual creation also place the student in a group, and does joining it work like an invitation code (main group and enrolment in the group's course, spec 001 FR-028l)? | Yes to both, same as the import. |
| P9 | E3, E4 | Where do a created student's level and grade come from (needed for the catalogue, and the grade mandatory for semillero — spec 001 FR-028m)? | From the destination group's course where it fixes them; otherwise chosen by the admin for the batch. |
| P10 | E3, E4 | Beyond text with leading zeros: which characters and lengths are valid; are thousands separators removed; what happens to an Excel numeric cell, whose leading zeros are already lost? | Letters and digits, 6–15 characters; remove dots and spaces; reject scientific notation and decimals; a numeric cell is an error asking for the column as text. |
| P11 | E4 | What happens to a student who already has a self-created account (its username is not the identification)? | Shown as «posible existente» when username or email match; linked only by an explicit admin action. |
| P12 | E3, E4 | Limits of administrative creation and of the import: rate per admin, rows per file, synchronous or in the background? | 200 rows per file, processed in the background; one import at a time per admin. |
| P13 | E3, E4 | While E3's or E4's amendment is in flight, every pull request touching a repository fails, whatever its spec. Accept that window (merge the docs and code PRs back to back, or as one PR as with spec 001's block 5), or correct the checker? | Correct the checker, explicitly: a Code Scope entry marked `(shared)` does not by itself make a pull request a code change for the spec; the spec's own entries, its cited tests and its directory still do. Scope: `scripts/check_traceability.py` rule 3a, its tests, the template comment and AGENTS.md § Spec-driven development. |
| P14 | E3 | Who else sees the identification: the student's teachers and the admin? | Yes; other students never (decision 5). |
| P15 | E3 | The rating of an expired account can still change once, when a match it left is closed by the timer with the existing rules (see below the table). Accept it? | Accept: it is the existing rule for any disconnection and adds no new rating effect. |

**What the existing PvP rules do when E3 closes an expired player's connection** (`api/websocket/
pvp.py` on `redesign`, unchanged by LuisJRubioH/LevelUp-ELO#46): waiting in the lobby → removed, no
match; in a match → the match continues on its timer and closes after 180 s with the scores so far,
applying the normal result to both players (the one who left keeps their score and usually loses);
a server restart before that → the match is closed as abandoned with no rating change. Cases these
rules leave open: the opponent waits up to 180 s against nobody; the expired player's rating
changes once after expiry (P15); the player cannot rejoin the match.

## Out of Scope *(mandatory)*

- The requirements of E2, E3 and E4, until their amendments (§ Deliveries).
- Creating teachers or administrators from the admin panel, and credentials based on the
  identification for them (decision 2).
- Forcing a password change at first sign-in (decision 2).
- **Block 5** (the diagnostic result) — spec 001, LuisJRubioH/LevelUp-ELO#62.
- **Blocks 6, 7 and 8** of the owner's plan — under discussion.
- The rest of the roadmap's spec 004 area, until a feature needs it (survey § 5): username and
  email normalisation (I1, I2), password recovery by the student, admin powers (I4–I6), group
  membership (I7, I8), auditing other actions (I9), the student-route role boundary (I11), test and
  demo accounts (I12, I13), changing a student's level or grade (I14), session lifetime, and
  hashing cost (I17).
- Rating effects of any account action — spec 001. Persistence mechanics — spec 002. AI keys and
  limits — spec 005. Teacher console — spec 006. The PvP match lifecycle — spec 007.
- V1, beyond the edge case above.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario. Reuse adequate existing tests; create or strengthen tests where coverage is missing.**

| Requirement / Scenario | Test |
|---|---|
| US1-AS1 | `PENDING` |
| US1-AS2 | `PENDING` |
| US1-AS3 | `PENDING` |
| US2-AS1 | `PENDING` |
| US2-AS2 | `PENDING` |
| US2-AS3 | `PENDING` |
| US2-AS4 | `PENDING` |
| US2-AS5 | `PENDING` |
| US2-AS6 | `PENDING` |
| FR-001 | `PENDING` |
| FR-002 | `PENDING` |
| FR-003 | `PENDING` |
| FR-004 | `PENDING` |
| FR-005 | `PENDING` |
| FR-006 | `PENDING` |
| FR-007 | `PENDING` |
| FR-008 | `PENDING` |
| FR-009 | `PENDING` |
| FR-010 | `PENDING` |
