# Tasks — spec 009, delivery I1 (the initial student import)

**Plan**: [plan-i1.md](plan-i1.md). Every requirement of spec 009 is `[CHANGE]`: the base branch
has no import, so each test is written first and must fail there (missing module, table, method,
endpoint or screen) before its implementation. There are no `[AS-IS]` requirements, so there is no
characterization phase. Tests use invented identifications only.

`[N1]` marked what waited on the Google Form's columns; they arrived on 2026-10-18, so those tasks
are no longer blocked (amendment of 2026-10-23, plan § The form's answers). `[N26]` and `[N27]` mark
what waits on the two open decisions of that amendment. `[P]` marks tasks that can run in parallel
with the others of their phase.

## Phase 1 — Setup

- [ ] T001 Branch `009-student-import-i1` from `004-identity-e3`; spec 009's Code Scope gains the
  new files as they are created (the checker accepts only tracked files)

## Phase 2 — Tests first (each must fail on the base branch)

### Domain, no I/O — `tests/unit/domain/test_spec009_import_rules.py`

- [ ] T002 [P] Identification: outer spaces removed; digits only; dots, dashes, inner spaces,
  letters, empty → error with its reason; a whole number of up to 15 digits from a numeric cell
  read as its digits; a decimal, more than 15 digits or scientific notation → «altered by the
  spreadsheet», never rebuilt (FR-004, US1-AS4, N16)
- [ ] T003 [P] Classification: `new`, `existing` (with the group and last-day differences),
  `duplicate` (the second occurrence in the file), `error` for a missing or refused name, a bad
  identification, a level and grade that do not match, and an identification that is another
  account's username (FR-002, FR-007, US1-AS1, US1-AS10)
- [ ] T004 [P] The digest changes with the file, the mapping, the batch choices or any row's
  status, and only with them (FR-003)
- [ ] T005 [P] Level and grade: the batch's level (N20) and the form's grades «Sexto» … «Undécimo»
  read as 6 … 11 without case, accents or outer spaces; an unknown value is an error, never guessed
  (FR-001, P9)
- [ ] T035 [P] Display name from one or two columns, in the order chosen, joined with one space; the
  filter judges the joined name; an empty result is an error (FR-001, N19, US1-AS10)
- [ ] T036 [P] Group by institution and grade: each row's pair takes the group paired with it; a
  pair with no group, «Otro» included, is an error; «Sede» is never read (FR-001, FR-002, N21)
- [ ] T037 [P] Recovery e-mail: optional column; a value that is not an e-mail address is an error;
  the same address on several rows is allowed (FR-018, N24)

### File reading — `tests/unit/infrastructure/test_spec009_spreadsheet_reader.py`

- [ ] T006 [P] CSV with and without BOM, `,` and `;`; `.xlsx` with text and numeric cells; the header
  and the rows as typed; over 5 MB or 500 rows refused before reading everything; an empty file or
  one without a header refused (FR-001, US1-AS4)
- [ ] T038 [P] Only the mapped columns leave the reader: a file with the form's other columns
  (document type, guardian, «Sede», authorisation) yields rows without them, and neither the
  preview response nor any stored record holds their values; only the mapping step's example rows
  show them to the admin (FR-016, N23)

### Both engines, repository — `tests/integration/test_spec009_import_store.py`

- [ ] T007 Import creation in chunks: identification as username and initial password, no forced
  change, linked with origin `import`, enrolled in the group's course, last day set; a row whose
  identification was linked meanwhile is `skipped`, never duplicated (FR-003, FR-005, FR-006)
- [ ] T008 One `running` import per admin; a retry of the same confirmation returns the same
  import; an import idle for 10 minutes becomes `interrupted` (FR-010, US1-AS8)
- [ ] T009 Audit rows hold the admin, times, the operation identifier, row numbers, results,
  internal IDs and reason codes — and no identification, name, password or file (FR-009, US1-AS7)
- [ ] T010 Explicit link: only an admin, only a student account without one, never an
  identification linked elsewhere; recorded; the username does not change (FR-007, US1-AS5)
- [ ] T011 Imported account: the student's own name change refused, the admin's accepted and
  recorded (FR-014, US3-AS1, US3-AS2); a one-by-one creation with a username that is a linked
  identification refused (FR-015)
- [ ] T039 Removing a link: admin only, recorded with who and when; the username and credentials
  do not change; a later import no longer matches it, and a row with it is an error while it is
  still that account's username (FR-017, FR-007, N18)
- [ ] T040 The migration: `users.recovery_email` (and, under `[N26]` (a), `groups.institution` and
  `groups.grade`) additive on both engines; `SCHEMA_VERSION` and its digest; the D3 parity test;
  a new account gets the row's recovery e-mail and keeps `users.email` empty; sign-in never reads
  the recovery e-mail (FR-018, R8)
- [ ] T041 `[N27]` An existing account's different recovery e-mail is a change applied only when
  confirmed for that account (FR-018, FR-008)
- [ ] T042 `[N26]` The admin creates a group for a teacher, with name, course and (under (a)) the
  institution and grade; the teacher sees it as their own (N25)

### Both engines, API — `tests/api/test_spec009_import.py`

- [ ] T012 Columns → preview → confirm → state, end to end with an invented file of 30 students;
  the result counts created and skipped; nothing saved by the preview (US1-AS1, US1-AS2)
- [ ] T013 The same file again creates nothing and changes no password, group, last day or rating
  (US1-AS3, FR-006, SC-001)
- [ ] T014 Changes to existing accounts applied only when confirmed one by one (US1-AS6, FR-008)
- [ ] T015 A confirmation whose file, choices or row statuses changed since the preview is refused
  (FR-003)
- [ ] T016 A student or a teacher is refused on every import endpoint (US1-AS9, FR-012)
- [ ] T017 Who sees the identification: `/me` shows a student their own; the admin's list shows
  it; every student and teacher endpoint, the PvP messages and the teacher's exports hold no other
  student's identification (US2-AS1, US2-AS2, FR-013, SC-003)
- [ ] T018 No identification or name in the application logs during an import, with logging
  captured (FR-011)
- [ ] T019 Load: 500 invented students on both engines, timed; the result goes in the PR and to the
  owner before the delivery closes (SC-002, P12)

### Screens — `frontend/e2e/spec009-import.spec.ts`

- [ ] T020 Upload, map, choose batch, preview with each status and its reasons, confirm, progress,
  result (US1-AS1, US1-AS2, US1-AS10)
- [ ] T021 A changed preview asks for a new one; existing-account changes need their own check box
  (FR-003, US1-AS6)
- [ ] T022 «Vincular identificación» from the users list (US1-AS5)
- [ ] T023 The student sees their identification and, for an imported account, a read-only name
  (US2-AS1, US3-AS2)
- [ ] T024 The mapping suggests the form's columns by their header («Número de documento»,
  «Nombres», «Apellidos», «Grado que cursas en 2027», «Institución educativa», «Correo electrónico
  de contacto») and the admin can change each suggestion

## Phase 3 — Implementation

- [ ] T025 `src/domain/student_import.py`: identification, row level and grade, classification,
  digest (makes T002–T004 pass)
- [ ] T026 The form's level and grade values, the two-column name, the group pairing and the
  recovery e-mail in `src/domain/student_import.py` (T005, T035 … T037)
- [ ] T027 `src/infrastructure/importing/spreadsheet_reader.py`, keeping only the mapped columns
  (T006, T038)
- [ ] T028 Tables `student_identifications`, `student_imports`, `student_import_rows` and the
  columns of T040, additive, in both repositories (R1, R8); import, link, unlink and audit methods;
  protocols; `SCHEMA_VERSION`; `db_sync_check.py` (T007–T010, T039, T040)
- [ ] T029 Spec 004 methods extended: `set_display_name` (FR-014), `create_student_account`
  (FR-015) (T011)
- [ ] T030 `api/routers/admin_import.py` and its schemas: columns, preview, confirmation with the
  worker thread, state, list, link; `/me` with the own identification (T012–T018)
- [ ] T031 Measure T019 and write the result in the PR (SC-002)
- [ ] T032 Screens: «Importar estudiantes», the users list's link and identification, the student's
  account page (T020–T023)
- [ ] T033 Header suggestions in the mapping (T024)
- [ ] T043 `[N27]` The confirmed recovery-e-mail change of an existing account (T041)
- [ ] T044 `[N26]` `POST /api/admin/teachers/{id}/groups` and «Crear grupo» in the admin's teachers
  list (T042)

## Phase 4 — Close

- [ ] T034 Traceability: every row of spec 009 filled with its tests; I1 `closed`; AGENTS.md
  (tables, `users.recovery_email`, the import's rule on usernames); `docs/transfer.md` (the new
  schema version and its rehearsal); `check_traceability.py`, the full suite on both engines,
  Playwright, `db_sync_check.py`, black, flake8 and the build
