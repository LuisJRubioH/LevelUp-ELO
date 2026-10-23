# Feature Specification: Initial Student Import from Google Forms

**Feature Branch**: `009-student-import`

**Created**: 2026-10-14

**Status**: Approved by the owner, spec and plan (2026-10-18). The owner's approved decisions on the
initial import, moved from spec 004 on 2026-10-14, night, so that spec 004 holds only rules for
every account. Plan and tasks: [plan-i1.md](plan-i1.md), [tasks-i1.md](tasks-i1.md) (2026-10-15).
The form's columns arrived on 2026-10-18 (N1, session below). **I1 implemented** (branch
`009-student-import-i1`, 2026-10-23), with schema version 8; the 500-student measurement (SC-002,
P12) goes to the owner with its pull request.

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
- `src/infrastructure/persistence/schema_version.py` — schema version 8, the import's tables and
  columns
- `frontend/src/pages/Admin/Users.tsx`
- `src/domain/student_import.py` — the import's rules without I/O: identification, grade, name,
  digest
- `src/infrastructure/importing/spreadsheet_reader.py` — reading the Forms export
- `api/routers/admin_import.py` — columns, preview, confirmation and its worker, state, linking,
  unlinking, the groups the admin creates for a teacher
- `api/schemas/auth.py` — the account's own identification and locked name in `/me`
- `frontend/src/pages/Admin/Import.tsx` — «Importar estudiantes»
- `frontend/src/pages/DisplayName.tsx` — the student's own identification and locked name
- `scripts/measure_import.py` — the 500-student measurement (SC-002)

## Deliveries *(mandatory for this spec)*

| Delivery | Content | Order rule | State |
|---|---|---|---|
| **I1** | The whole import: mapping, preview, confirmation, credentials, re-import, linking, who sees the identification, the name of an imported account, audit and limits | After spec 004's E3, whose creation and expiry rules it reuses; once the owner sends the form's columns (N1). | closed |

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

### Session 2026-10-18, later (owner answers)

- N18, N19, N20, N22 and N23 are approved as recommended; N21 is approved with the owner's
  classification: by institution and grade. A first phase is played among classmates of one
  institution and grade, and only finalists meet the best of other institutions (an olympiad
  feature after the refactor, roadmap § 6). Everything stays closed: each teacher reviews the
  results of their own students.
- Accounts need an e-mail for account and password recovery (N24, open).
- The teacher who accompanies each student is collected by a separate form — name, institution,
  grades accompanied, contact data — so that the teacher sees their students' progress (N25, open).
- Later the same day the owner approved the recommendations of N24 and N25: a recovery e-mail per
  account, read by the import (FR-016, FR-018), with self-service recovery as a later spec 004
  delivery; and teachers and their groups created by the admin before the import.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The admin imports a class from a Forms export (Priority: P1) — I1

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a `.xlsx` or `.csv` up to 5 MB and 500 students, **When** the admin
   uploads it, maps its columns (the display name from one or two columns, and each institution
   and grade to an existing group), chooses the last day of access and, unless mapped, level and
   grade, **Then** a preview lists each row as new, existing, duplicate or error, with its level,
   grade and group, and nothing is saved.
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
  the system shall list its columns and let the admin map the identification; the display name
  from one or two columns, joined with one space in the order the admin chooses (N19);
  optionally, level and grade; and the institution and grade of each row to an existing group,
  one group per institution and grade (N21). It shall let the admin choose the last day of access
  and the batch's level and grade where not mapped (N20).
- **FR-002** [CHANGE]: Before saving, the system shall show each row as new, existing, duplicate (in
  the file) or error with its reason, with the level, grade and group it would get. A row without a
  display name, with one spec 004's name filter refuses (spec 004 FR-020), or whose institution and
  grade map to no group, is an error.
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
- **FR-016** [CHANGE]: The system shall read from the file only the identification, the
  display-name columns, level and grade, the institution and the recovery e-mail, and shall store
  nothing else of it (N23, N24).
- **FR-017** [CHANGE]: When the admin removes the link between an identification and an account
  made by mistake, the system shall record who removed it and when, and shall change neither the
  account's username nor its credentials (N18).
- **FR-018** [CHANGE]: When the admin maps an e-mail column, the system shall store each row's
  address as the account's recovery e-mail — one per account, which may repeat across accounts
  (siblings, a shared family address) and never serves to sign in — and shall leave the account's
  sign-in e-mail unchanged. A value that is not an e-mail address is an error for that row (N24).

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
| N18 | (Plan, 2026-10-15.) The admin links an identification to an existing account (FR-007), but the spec gives no way to remove or correct a link made by mistake. | **Approved** (owner, 2026-10-18): the admin removes a link, recorded; the account's username and credentials never change (FR-017). |
| N19 | (Form, 2026-10-18.) The display name is split into «Nombres» and «Apellidos»; FR-001 maps one column. | **Approved** (owner, 2026-10-18): Let the admin map one or two columns for the display name, joined with one space in the order chosen («Nombres Apellidos»); spec 004's filter and limits apply to the result. |
| N20 | (Form.) There is no level column; every participant is in grades 6.º to 11.º. | **Approved** (owner, 2026-10-18): The batch's level is chosen once by the admin; for this olympiad, semillero, so the grade column decides each student's six courses (spec 001 FR-028k). |
| N21 | (Form.) Each row names an institution («Institución educativa», or «Otro» with free text); FR-001 took one existing group per batch. | **Approved, amended** (owner, 2026-10-18): students are classified by institution **and grade**: one group per institution and grade, whose teacher is the one who accompanies those grades at that institution (N25). In a first phase each student competes with classmates of the same institution and grade; only finalists meet the best of other institutions (roadmap § 6, olympiad). A row whose institution and grade map to no group («Otro» included) is an error to correct before confirming; «Sede» is not read (FR-001, FR-002). |
| N22 | (Form.) Its texts promise what the system does not do: «Te enviaremos al correo las instrucciones» (the system sends no email; FR-005 makes the identification the username and initial password) and «Las respuestas de las pruebas se califican identificadas con un código, sin el nombre del estudiante» (teachers and classmates see the display name, spec 004 FR-020). | **Approved** (owner, 2026-10-18): Change the form's texts to what the platform does (done in the revised script); sending the access instructions is the school's step. |
| N23 | (Form.) It also collects the document type, e-mail, the guardian's name and mobile number and «Sede». | **Approved** (owner, 2026-10-18): The import reads only the identification, the names, the grade and the institution; nothing else is stored (data minimisation, Law 1581 of 2012). The responses sheet stays the school's, as § Assumptions says. |
| N24 | (Owner, 2026-10-18.) Accounts need an e-mail for account and password recovery. The form's «Correo electrónico de contacto» can be the student's or the guardian's. Two facts block using it as the account's `users.email`: that column is unique and is also a sign-in identifier (spec 004 FR-006), so siblings or a family sharing one address could not both have it; and the system sends no e-mail today, so self-service recovery does not exist (spec 004 § Out of Scope). | **Approved** (owner, 2026-10-18): A separate recovery e-mail per account, not unique and never a sign-in identifier, filled by the import from that column (additive column, AGENTS R8); FR-016 would then also read that column. Self-service recovery by e-mail as a new spec 004 delivery, which needs an e-mail-sending service (owner's choice of provider and its cost); until then the admin resets passwords (spec 004 E2). |
| N25 | (Owner, 2026-10-18.) Each student's teacher comes from a separate form: name, institution, grades accompanied and contact data, so that the teacher sees the progress of their students. | **Approved** (owner, 2026-10-18): The admin creates each teacher (spec 004 E2) and one group per institution and grade owned by that teacher, before importing students; the teacher sees only their groups (spec 004, the teacher's scope). The teachers' form is the school's, like the students'. |

## Out of Scope *(mandatory)*

- Every rule for all accounts — display names and their filter, passwords, sessions, creation one
  by one, the last day of access, Safari, the limits' store: spec 004.
- Forcing students created with their identification to change it at first access (decision).
- Identity documents other than the import's identifications, such as passports or PPT: not
  requested, so no rule is written for them (owner, 2026-10-14; N4 withdrawn).
- Imports from sources other than the Google Form's export.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario.** Every row is I1's (closed): the tests that store data run on SQLite and PostgreSQL
(SC-004).

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows`<br>`frontend/e2e/spec009-import.spec.ts › subir, mapear, ver la vista previa, confirmar y ver el resultado (US1-AS1, US1-AS2, US1-AS10)` |
| US1-AS2 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows`<br>`tests/integration/test_spec009_import_store.py::test_spec009_an_import_creates_students_with_the_identification_as_credentials`<br>`frontend/e2e/spec009-import.spec.ts › subir, mapear, ver la vista previa, confirmar y ver el resultado (US1-AS1, US1-AS2, US1-AS10)` |
| US1-AS3 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_the_same_file_again_creates_and_changes_nothing`<br>`tests/integration/test_spec009_import_store.py::test_spec009_a_row_linked_or_taken_meanwhile_is_skipped_never_duplicated` |
| US1-AS4 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_an_identification_is_read_as_its_digits`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_any_other_identification_is_refused_and_never_rebuilt`<br>`tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_a_csv_is_read_with_its_header_and_rows_as_typed`<br>`tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_an_xlsx_keeps_text_and_numeric_cells_as_typed` |
| US1-AS5 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_the_admin_links_an_identification_explicitly`<br>`tests/integration/test_spec009_import_api.py::test_spec009_the_admin_links_and_unlinks_an_identification`<br>`frontend/e2e/spec009-import.spec.ts › vincular y quitar una identificación desde la lista de usuarios (US1-AS5, FR-017)` |
| US1-AS6 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_changes_to_existing_accounts_apply_only_when_confirmed`<br>`frontend/e2e/spec009-import.spec.ts › una vista previa que cambió pide generarla de nuevo, y sin marcar no se confirma ningún cambio (FR-003, US1-AS6)` |
| US1-AS7 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_the_audit_holds_ids_and_codes_never_the_data`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows` |
| US1-AS8 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_one_running_import_per_admin_and_a_retry_returns_it`<br>`tests/integration/test_spec009_import_api.py::test_spec009_a_retried_confirmation_returns_the_first_import` |
| US1-AS9 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_a_student_or_a_teacher_is_refused_on_every_import_endpoint` |
| US1-AS10 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_a_row_with_a_problem_is_an_error_with_its_reason`<br>`tests/integration/test_spec009_import_store.py::test_spec009_a_chunk_applies_spec004_creation_rules`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows`<br>`frontend/e2e/spec009-import.spec.ts › subir, mapear, ver la vista previa, confirmar y ver el resultado (US1-AS1, US1-AS2, US1-AS10)` |
| US2-AS1 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_an_imported_student_sees_the_identification_and_cannot_rename`<br>`tests/integration/test_spec009_import_api.py::test_spec009_the_admin_links_and_unlinks_an_identification`<br>`frontend/e2e/spec009-import.spec.ts › el estudiante importado ve su identificación y su nombre solo de lectura (US2-AS1, US3-AS2)` |
| US2-AS2 | I1 | `tests/integration/test_spec009_identification_visibility.py::test_spec009_no_classmate_or_teacher_response_holds_an_identification` |
| US3-AS1 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_only_the_admin_renames_an_imported_account`<br>`tests/integration/test_spec009_import_api.py::test_spec009_an_imported_student_sees_the_identification_and_cannot_rename` |
| US3-AS2 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_only_the_admin_renames_an_imported_account`<br>`tests/integration/test_spec009_import_api.py::test_spec009_an_imported_student_sees_the_identification_and_cannot_rename`<br>`frontend/e2e/spec009-import.spec.ts › el estudiante importado ve su identificación y su nombre solo de lectura (US2-AS1, US3-AS2)` |
| FR-001 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_two_name_columns_join_with_one_space_in_the_order_chosen`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_forms_grade_words_read_as_six_to_eleven`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_group_comes_from_the_rows_institution_and_grade`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_a_pair_is_suggested_the_group_with_that_institution_and_grade`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_forms_headers_suggest_the_mapping`<br>`tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_a_file_over_the_size_limit_is_refused_before_it_is_parsed`<br>`tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_a_file_over_the_row_limit_is_refused`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows`<br>`tests/integration/test_spec009_import_api.py::test_spec009_an_unusable_file_or_choice_is_refused_with_its_reason`<br>`tests/integration/test_spec009_import_api.py::test_spec009_the_admin_creates_a_group_for_a_teacher_and_it_pairs`<br>`tests/integration/test_spec009_import_store.py::test_spec009_the_admin_creates_a_group_for_a_teacher`<br>`frontend/e2e/spec009-import.spec.ts › el admin cambia una columna sugerida (T024)`<br>`frontend/e2e/spec009-import.spec.ts › el admin crea un grupo para un docente con su institución y grado (N25, N26)` |
| FR-002 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_a_valid_unknown_row_is_new_with_its_level_grade_and_group`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_a_linked_identification_is_existing_with_the_differences_to_confirm`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_second_occurrence_of_an_identification_is_a_duplicate`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_a_row_with_a_problem_is_an_error_with_its_reason`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_group_comes_from_the_rows_institution_and_grade`<br>`tests/integration/test_spec009_import_store.py::test_spec009_the_lookups_give_what_the_preview_compares`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows` |
| FR-003 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_digest_changes_with_the_file_mapping_batch_or_any_status`<br>`tests/integration/test_spec009_import_store.py::test_spec009_an_import_creates_students_with_the_identification_as_credentials`<br>`tests/integration/test_spec009_import_store.py::test_spec009_a_chunk_applies_spec004_creation_rules`<br>`tests/integration/test_spec009_import_api.py::test_spec009_a_confirmation_whose_preview_changed_is_refused`<br>`frontend/e2e/spec009-import.spec.ts › una vista previa que cambió pide generarla de nuevo, y sin marcar no se confirma ningún cambio (FR-003, US1-AS6)` |
| FR-004 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_an_identification_is_read_as_its_digits`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_any_other_identification_is_refused_and_never_rebuilt`<br>`tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_an_xlsx_keeps_text_and_numeric_cells_as_typed` |
| FR-005 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_an_import_creates_students_with_the_identification_as_credentials`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows` |
| FR-006 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_a_row_linked_or_taken_meanwhile_is_skipped_never_duplicated`<br>`tests/integration/test_spec009_import_api.py::test_spec009_the_same_file_again_creates_and_changes_nothing` |
| FR-007 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_an_identification_that_is_another_accounts_username_is_an_error`<br>`tests/integration/test_spec009_import_store.py::test_spec009_the_admin_links_an_identification_explicitly`<br>`tests/integration/test_spec009_import_store.py::test_spec009_the_lookups_give_what_the_preview_compares`<br>`tests/integration/test_spec009_import_store.py::test_spec009_removing_a_link_keeps_the_account_as_it_is` |
| FR-008 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_a_linked_identification_is_existing_with_the_differences_to_confirm`<br>`tests/integration/test_spec009_import_api.py::test_spec009_changes_to_existing_accounts_apply_only_when_confirmed`<br>`tests/integration/test_spec009_import_api.py::test_spec009_a_confirmed_change_the_preview_did_not_show_is_refused` |
| FR-009 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_the_audit_holds_ids_and_codes_never_the_data` |
| FR-010 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_one_running_import_per_admin_and_a_retry_returns_it`<br>`tests/integration/test_spec009_import_store.py::test_spec009_an_idle_import_becomes_interrupted`<br>`tests/integration/test_spec009_import_api.py::test_spec009_a_retried_confirmation_returns_the_first_import` |
| FR-011 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_the_import_writes_no_identification_or_name_to_the_logs`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows` |
| FR-012 | I1 | `tests/integration/test_spec009_import_api.py::test_spec009_a_student_or_a_teacher_is_refused_on_every_import_endpoint` |
| FR-013 | I1 | `tests/integration/test_spec009_identification_visibility.py::test_spec009_no_classmate_or_teacher_response_holds_an_identification`<br>`tests/integration/test_spec009_import_api.py::test_spec009_the_admin_links_and_unlinks_an_identification`<br>`tests/integration/test_spec009_import_api.py::test_spec009_an_imported_student_sees_the_identification_and_cannot_rename` |
| FR-014 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_only_the_admin_renames_an_imported_account`<br>`tests/integration/test_spec009_import_api.py::test_spec009_an_imported_student_sees_the_identification_and_cannot_rename` |
| FR-015 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_a_one_by_one_username_that_is_a_linked_identification_is_refused` |
| FR-016 | I1 | `tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_only_the_mapped_columns_leave_the_reader`<br>`tests/unit/infrastructure/test_spec009_spreadsheet_reader.py::test_spec009_a_mapped_column_missing_from_the_file_is_refused`<br>`tests/integration/test_spec009_import_api.py::test_spec009_columns_then_preview_then_confirm_creates_the_new_rows` |
| FR-017 | I1 | `tests/integration/test_spec009_import_store.py::test_spec009_removing_a_link_keeps_the_account_as_it_is`<br>`tests/integration/test_spec009_import_api.py::test_spec009_the_admin_links_and_unlinks_an_identification`<br>`frontend/e2e/spec009-import.spec.ts › vincular y quitar una identificación desde la lista de usuarios (US1-AS5, FR-017)` |
| FR-018 | I1 | `tests/unit/domain/test_spec009_import_rules.py::test_spec009_the_same_recovery_email_on_several_rows_is_allowed`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_an_unmapped_recovery_email_leaves_it_empty`<br>`tests/unit/domain/test_spec009_import_rules.py::test_spec009_an_existing_accounts_different_recovery_email_is_a_change_to_confirm`<br>`tests/integration/test_spec009_import_store.py::test_spec009_the_migration_adds_the_import_tables_and_columns`<br>`tests/integration/test_spec009_import_store.py::test_spec009_an_import_creates_students_with_the_identification_as_credentials`<br>`tests/integration/test_spec009_import_store.py::test_spec009_a_recovery_email_change_is_applied_only_by_the_admin`<br>`tests/integration/test_spec009_import_api.py::test_spec009_changes_to_existing_accounts_apply_only_when_confirmed` |
