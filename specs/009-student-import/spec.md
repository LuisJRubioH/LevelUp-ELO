# Feature Specification: Initial Student Import from Google Forms

**Feature Branch**: `009-student-import`

**Created**: 2026-10-14

**Status**: Approved by the owner, spec and plan (2026-10-18). The owner's approved decisions on the
initial import, moved from spec 004 on 2026-10-14, night, so that spec 004 holds only rules for
every account. Nothing is implemented. Plan and tasks: [plan-i1.md](plan-i1.md),
[tasks-i1.md](tasks-i1.md) (2026-10-15). The form's columns arrived on 2026-10-18 (N1, session
below); the questions they raise, N19 … N23, wait on the owner before FR-001 and FR-002 change.

**Input**: The owner's orders of 2026-10-13 on block 4 (enrolment through Google Forms) and the
answers of 2026-10-14 (N4, N12, N14, N16 and the night session), first recorded in spec 004
(LuisJRubioH/LevelUp-ELO#58). Background: the as-is survey `docs/sdd/identity-survey.md`
(LuisJRubioH/LevelUp-ELO#37).

**Outcome served** (constitution VIII): the students of the owner's first load from Google Forms
get a working account without signing up or inventing a password, and keep it until the last day
set for their batch. Their identification never reaches classmates or teachers. The import creates
accounts through spec 004's validations and changes none of its rules; it adds two that reach other
paths — the student of an imported account does not rename themselves (FR-014), and a username that
is an identification linked to another account is refused (FR-015).

**Depends on**: spec 004 — display names and the name filter (spec 004 FR-020 to spec 004 FR-025),
the creation of a student by the admin (spec 004 FR-040 and spec 004 FR-043 to spec 004 FR-045) and
the last day of access (spec 004 FR-046 to spec 004 FR-052). Not delivered before spec 004's E3.

## Code Scope *(mandatory)*

The code whose behaviour this spec defines. A path shared with another spec belongs to both.

- `api/routers/admin.py` — upload, preview, confirmation, linking, the import's audit
- `api/routers/auth.py` — the student's own identification in `/me`
- `src/application/interfaces/repositories.py`
- `src/infrastructure/persistence/sqlite_repository.py` — the identification link and the import's
  records
- `src/infrastructure/persistence/postgres_repository.py` — the same, mirrored (R1)
- `frontend/src/pages/Admin/Users.tsx`

## Deliveries *(mandatory for this spec)*

| Delivery | Content | Order rule | State |
|---|---|---|---|
| **I1** | The whole import: mapping, preview, confirmation, credentials, re-import, linking, who sees the identification, the name of an imported account, audit and limits | After spec 004's E3, whose creation and expiry rules it reuses; once the owner sends the form's columns (N1). | planned |

## Clarifications

### Recorded in spec 004, 2026-10-13 (owner orders, approved)

Moved here as given on 2026-10-14; the scope notes of 2026-10-14 are kept.

- Q: How do students enrol? → A: through a Google Form; the admin downloads the responses and
  imports the `.xlsx` or `.csv` from the admin panel, mapping the file's columns to the
  application's fields and choosing the group and the expiration. Every account of this flow is a
  student.
- Q: What are a temporary student's credentials? → A: by the product owner's decision, the
  identification number is both the username and the initial password, with no change required at
  first access; the student may change it later. The password is stored only with the existing
  secure hash, never readable in the database, logs or import reports. *(Scope, 2026-10-14: the
  initial import only; students created one by one get their own credentials, spec 004 N13.)*
- Q: How is the identification read? → A: as text of digits, keeping leading zeros; only outer
  spaces are removed; other formats are flagged for correction; ambiguous values or values altered
  by Excel are rejected, never rebuilt. It never appears in rankings or classmates' views.
  *(2026-10-14: leading zeros withdrawn — the identifications have none; the format is the initial
  import's, never a rule for usernames.)*
- Q: What happens before saving an import? → A: a preview of new accounts, existing accounts,
  duplicates and errors per row; nothing is saved until the admin confirms. Existing students are
  detected by an identification already linked; re-importing never duplicates accounts, resets
  passwords, changes groups, extends expirations or overwrites progress — updates of existing
  accounts need an explicit administrative action. The result is shown and recorded: who, when,
  how many accounts were created or skipped.

**P4 — origin of the display name** (the import's part): taken from a form column and reviewable
by the admin; never the identification, not even as a fallback.

**P5 / N14 — changing the display name** (the import's part): only the admin changes the display
name of an account of the initial import, and the change is recorded.

**P8 — group** (the import's part): an existing group is chosen for the batch; no group is created
automatically from errors or variations in a file.

**P9 — level and grade** (the import's part): from mapped columns or from values chosen explicitly
for the batch; shown in the preview; combinations validated as in spec 004.

**P10 — identification format**: text of digits, leading zeros kept; only outer spaces removed;
other formats flagged for correction; ambiguous or Excel-altered values rejected without rebuilding
them. *(2026-10-14: leading zeros withdrawn; the initial import's format, not a general validation;
no rule about documents not requested — N4 withdrawn.)*

**P11 — students with an existing account**: existing accounts and their progress are kept; matches
by an identification already linked; explicit administrative linking where it is missing; never
merged by name; credentials never reset by an import; changing the group or the expiration of an
existing account needs a specific confirmation.

**P12 — administrative limits** (the import's part): files up to 500 students and 5 MB; one import
running per admin. A full load is verified and retries never duplicate accounts. Configurable. If
the server cannot process 500 students reliably, the result is reported before lowering the limit
or changing the processing.

**P14 — who sees the identification**: each student their own; the admin for management; teachers
use the display name and the group; never other students, nor any response meant for public or
shared views.

### Recorded in spec 004, 2026-10-14 (owner answers, approved)

- N12: an imported account without a name yet appears by a neutral alias. *(Withdrawn the same
  night: see below.)*
- N16: numeric `.xlsx` cells are accepted — a whole number of up to 15 digits is read as its
  digits.

### Session 2026-10-14, night (owner answers, approved)

- The initial import is specified apart, in this spec, so that spec 004 holds only rules for every
  account; the decisions approved for it keep their content.
- A row without a display name is an error the admin corrects before confirming: every imported
  account has a name, and no alias exists.
- The group is required when the admin creates a student, the import included (spec 004 N15).

### Session 2026-10-18 (owner: approval and the form's columns)

- The spec and plan-i1 are approved.
- N1 is answered by the form's script (`crearFormulario`, «Inscripción – Olimpiadas Municipales de
  Matemáticas de Chigorodó 2027»). Its questions, in order: «Nombres», «Apellidos», «Tipo de
  documento» (Tarjeta de identidad, Cédula de ciudadanía, Registro civil, PPT, Otro), «Número de
  documento» (the form accepts `^[0-9]{5,12}$`), «Institución educativa» (a list plus «Otro»),
  «Sede» (optional), «Grado que cursas en 2027» (Sexto, Séptimo, Octavo, Noveno, Décimo, Undécimo),
  «Correo electrónico de contacto», «Nombre completo del acudiente», «Celular del acudiente» and the
  data-treatment authorization.
- Read against this spec: the identification is «Número de documento» (P10 holds: the form already
  takes digits only); the grade is «Grado que cursas en 2027», whose six values are grades 6.º to
  11.º; there is no level column and no single display-name column. N19 … N23 record what follows.
- The owner noticed the form lacks the legal representative's authorization for the treatment of
  the participants' personal data and for the use of their image. That is the school's form, not
  this system (§ Assumptions); a revised script was handed to the owner on 2026-10-18.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The admin imports a class from a Forms export (Priority: P1) — I1

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a `.xlsx` or `.csv` up to 5 MB and 500 students, **When** the admin
   uploads it, maps its columns, chooses an existing group, the last day of access and, unless
   mapped, level and grade, **Then** a preview lists each row as new, existing, duplicate or error,
   with its level and grade, and nothing is saved.
2. **US1-AS2** — **Given** a preview, **When** the admin confirms, **Then** exactly the new rows
   become temporary students with the identification as username and initial password, and the
   result shows how many were created and skipped.
3. **US1-AS3** — **Given** the same file imported again, **When** it is confirmed, **Then** no
   account is duplicated and no password, group, last day or progress changes.
4. **US1-AS4** — **Given** identifications in a CSV or in an `.xlsx`, **When** they are imported,
   **Then** each is read as written, with no conversion by the spreadsheet, and a value the
   spreadsheet already altered (for example, in scientific notation) is flagged for correction and
   never rebuilt (numeric cells: N16).
5. **US1-AS5** — **Given** a student with an account but no linked identification, **When** the
   admin links it explicitly, **Then** later imports find it; nothing is ever merged by name.
6. **US1-AS6** — **Given** an existing account whose group or last day differs in the file, **When**
   the admin confirms that change specifically, **Then** only that change is applied.
7. **US1-AS7** — **Given** a confirmed import, **When** the audit is read, **Then** it names the
   admin, the time, the operation and each row's result with internal account IDs, and holds no
   password and not the file.
8. **US1-AS8** — **Given** an import running, **When** the same admin starts another or retries the
   confirmation, **Then** it is refused or returns the first result, and nothing is duplicated.
9. **US1-AS9** — **Given** a student or a teacher, **When** they reach the import, **Then** they are
   refused.
10. **US1-AS10** — **Given** a row without a display name, or with one spec 004's name filter
    refuses, **When** the preview is shown, **Then** the row is an error and confirming creates no
    account for it.

### User Story 2 - Nobody else sees my identification (Priority: P1) — I1

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** a student with a linked identification, **When** they open their profile,
   **Then** they see it; the admin sees it for management.
2. **US2-AS2** — **Given** imported students in a group, **When** a classmate opens a ranking or a
   PvP match, or their teacher opens any view of the group, **Then** no response or message holds
   another student's identification.

### User Story 3 - Only the admin renames an imported account (Priority: P2) — I1

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** an account of the initial import, **When** the admin changes its display
   name, **Then** it changes and the change is recorded.
2. **US3-AS2** — **Given** an account of the initial import, **When** its student tries to change
   their own display name, **Then** it is refused and nothing changes.

### Edge Cases

- **An identification that is already another account's username** (an account not linked to it):
  the row is an error; nothing is merged and no username changes (FR-007).
- **A username the admin types for a student created one by one that is an identification linked
  to another account**: refused (FR-015), so that one person's identification never signs in to
  another's account.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** [CHANGE]: When the admin uploads a `.xlsx` or `.csv` of at most 5 MB and 500 students,
  the system shall list its columns and let the admin map the identification, the display name
  and, optionally, level and grade, and choose an existing group, the last day of access and the
  batch's level and grade where not mapped. *(Which columns the form has is to be confirmed: N1.)*
- **FR-002** [CHANGE]: Before saving, the system shall show each row as new, existing, duplicate (in
  the file) or error with its reason, with the level and grade it would get. A row without a
  display name, or with one spec 004's name filter refuses (spec 004 FR-020), is an error.
- **FR-003** [CHANGE]: The system shall save nothing until the admin confirms the preview, and then
  create exactly the rows shown as new through the validations of spec 004 FR-040, spec 004 FR-043
  and spec 004 FR-044, with the credentials of FR-005 instead of a temporary password.
- **FR-004** [CHANGE]: The system shall read an identification as text of digits, remove only outer
  spaces, and refuse for correction any other format, ambiguous value or value altered by a
  spreadsheet, without rebuilding it. A whole number in a numeric cell of up to 15 digits is read
  as its digits (N16). This format is no condition on usernames or on accounts without an
  identification.
- **FR-005** [CHANGE]: When the import creates a student, the system shall set the identification as
  username and as initial password, link it to the account, and not require a change at first
  access. A student created one by one never gets these credentials (spec 004, N13).
- **FR-006** [CHANGE]: When a file is imported again, the system shall create no duplicate and change
  no password, group, last day of access or progress of an existing account.
- **FR-007** [CHANGE]: The system shall match existing students only by an identification already
  linked; let the admin link one explicitly; and never merge accounts by name. A row whose
  identification is the username of an account not linked to it is an error.
- **FR-008** [CHANGE]: If the file gives an existing account another group or last day, then the
  system shall apply it only after the admin confirms that change specifically.
- **FR-009** [CHANGE]: When an import is confirmed, the system shall record the admin, the date and
  time, an operation identifier, and each row's result with the internal ID of the account
  affected — never passwords and never the file.
- **FR-010** [CHANGE]: The system shall run at most one import per admin at a time, return the first
  result to a retried confirmation, and keep the import's controls separate from the login and
  registration limits.
- **FR-011** [CHANGE]: The system shall keep no uploaded file after its import is confirmed or
  abandoned, and write no identification or display name to the application logs.
- **FR-012** [CHANGE]: If anyone other than the admin uses the import, then the system shall refuse.
- **FR-013** [CHANGE]: The system shall show a linked identification only to its own student and to
  the admin; no response or message addressed to another student or to a teacher shall carry it.
- **FR-014** [CHANGE]: While an account was created by the import, the system shall let only the admin
  change its display name, record the change, and refuse the student's own change (N14).
- **FR-015** [CHANGE]: If the admin creates a student one by one with a username that is an
  identification linked to another account, then the system shall refuse the creation and change
  nothing.

### Key Entities

- **Identification link**: an account's identification, text of digits as given, unique among
  linked accounts; only the import's accounts and accounts the admin links explicitly have one. It
  lives apart from the account's general fields, so that no rule for every account depends on it.
- **Import**: one confirmed file's operation; the file itself is not kept.
- **Import audit record**: who, when, operation identifier, affected accounts by internal ID,
  result per row; never passwords or files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Re-importing a confirmed file creates 0 accounts and changes 0 credentials, groups,
  last days or progress records.
- **SC-002**: A file of 500 students is imported completely and reliably, or the measured result is
  reported before the limit or the processing changes (P12).
- **SC-003**: 0 responses addressed to a student or a teacher contain another student's linked
  identification.
- **SC-004**: Every scenario is reproduced by automated checks; those that depend on stored data run
  on SQLite and PostgreSQL with identical results.

## Assumptions

- Test data uses invented identifications only; the repository is public.
- Linking an identification only lets the import recognise an account (P11) and is never required.
  No account outside the import gets the import's group, last day or credentials unless the admin
  confirms that change specifically (FR-008).
- Collecting minors' identifications requires the guardians' authorisation and a privacy notice
  (Colombian Law 1581 of 2012) — the school's process; deleting the form's responses file after the
  import is the school's step.

## New Decisions and Contradictions (not assumed approved)

| # | Point | Recommendation |
|---|---|---|
| N1 | The columns of the Google Form: which hold the identification, the display name, level and grade. | Waiting on the owner, who sends them when available. |
| N4 | (Spec 004, 2026-10-13.) P10 admits digits only, so identifications with letters (passport, PPT, some foreign documents) cannot be imported. | **Withdrawn** (owner, 2026-10-14): no condition about documents nobody asked for; the import keeps P10. |
| N14 | (Spec 004, question D.) Changing the display name of an imported account. | **Decided** (owner, 2026-10-14): only the admin. |
| N16 | (Spec 004.) Without leading zeros, an `.xlsx` cell typed as a number that holds a whole number loses nothing when read as its digits. The 2026-10-13 text flagged every numeric cell. | **Decided** (owner, 2026-10-14): accepted — a whole number of up to 15 digits is read as its digits; only values the spreadsheet already altered (scientific notation, decimals, more digits than it keeps) are flagged. |
| N18 | (Plan, 2026-10-15.) The admin links an identification to an existing account (FR-007), but the spec gives no way to remove or correct a link made by mistake. | Let the admin remove a link, recorded; the account's username and credentials never change. |
| N19 | (Form, 2026-10-18.) The display name is split into «Nombres» and «Apellidos»; FR-001 maps one column. | Let the admin map one or two columns for the display name, joined with one space in the order chosen («Nombres Apellidos»); spec 004's filter and limits apply to the result. |
| N20 | (Form.) There is no level column; every participant is in grades 6.º to 11.º. | The batch's level is chosen once by the admin; for this olympiad, semillero, so the grade column decides each student's six courses (spec 001 FR-028k). |
| N21 | (Form.) Each row names an institution («Institución educativa», or «Otro» with free text); FR-001 takes one existing group per batch. | Let the admin map the institution column to existing groups, one per institution, created beforehand; a row whose institution maps to no group («Otro» included) is an error to correct before confirming. «Sede» is not read. |
| N22 | (Form.) Its texts promise what the system does not do: «Te enviaremos al correo las instrucciones» (the system sends no email; FR-005 makes the identification the username and initial password) and «Las respuestas de las pruebas se califican identificadas con un código, sin el nombre del estudiante» (teachers and classmates see the display name, spec 004 FR-020). | Change the form's texts to what the platform does (done in the revised script); sending the access instructions is the school's step. |
| N23 | (Form.) It also collects the document type, e-mail, the guardian's name and mobile number and «Sede». | The import reads only the identification, the names, the grade and the institution; nothing else is stored (data minimisation, Law 1581 of 2012). The responses sheet stays the school's, as § Assumptions says. |

## Out of Scope *(mandatory)*

- Every rule for all accounts — display names and their filter, passwords, sessions, creation one
  by one, the last day of access, Safari, the limits' store: spec 004.
- Forcing students created with their identification to change it at first access (decision).
- Identity documents other than the import's identifications, such as passports or PPT: not
  requested, so no rule is written for them (owner, 2026-10-14; N4 withdrawn).
- Imports from sources other than the Google Form's export.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario.** Nothing is implemented yet.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | I1 | `PENDING` |
| US1-AS2 | I1 | `PENDING` |
| US1-AS3 | I1 | `PENDING` |
| US1-AS4 | I1 | `PENDING` |
| US1-AS5 | I1 | `PENDING` |
| US1-AS6 | I1 | `PENDING` |
| US1-AS7 | I1 | `PENDING` |
| US1-AS8 | I1 | `PENDING` |
| US1-AS9 | I1 | `PENDING` |
| US1-AS10 | I1 | `PENDING` |
| US2-AS1 | I1 | `PENDING` |
| US2-AS2 | I1 | `PENDING` |
| US3-AS1 | I1 | `PENDING` |
| US3-AS2 | I1 | `PENDING` |
| FR-001 | I1 | `PENDING` |
| FR-002 | I1 | `PENDING` |
| FR-003 | I1 | `PENDING` |
| FR-004 | I1 | `PENDING` |
| FR-005 | I1 | `PENDING` |
| FR-006 | I1 | `PENDING` |
| FR-007 | I1 | `PENDING` |
| FR-008 | I1 | `PENDING` |
| FR-009 | I1 | `PENDING` |
| FR-010 | I1 | `PENDING` |
| FR-011 | I1 | `PENDING` |
| FR-012 | I1 | `PENDING` |
| FR-013 | I1 | `PENDING` |
| FR-014 | I1 | `PENDING` |
| FR-015 | I1 | `PENDING` |
