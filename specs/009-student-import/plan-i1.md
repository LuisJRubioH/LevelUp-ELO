# Plan — spec 009, delivery I1: the initial student import

**Spec**: [spec.md](spec.md) § Deliveries, I1 (US1 … US3; FR-001 … FR-018) · **Branch**:
`009-student-import-i1`, from spec 004's E3 (`004-identity-e3`, LuisJRubioH/LevelUp-ELO#73), whose
creation and expiry rules it reuses · **Date**: 2026-10-15

Written before the Google Form's columns were known (N1). The admin maps the file's columns, so
almost nothing below depends on them; what does is listed in § Waiting on the form and marked
`[N1]` in [tasks-i1.md](tasks-i1.md). **Approved by the owner on 2026-10-18.** The columns arrived
the same day (spec § Clarifications, 2026-10-18): the grade's values are «Sexto» … «Undécimo»
(6.º … 11.º); the display-name, level and group mapping wait on N19 … N21.

**Amended 2026-10-23** for the owner's answers N19 … N25 (2026-10-18), which the spec already
carries in FR-001, FR-002 and FR-016 … FR-018: see § The form's answers. Two points those answers
left open, N26 and N27 (spec § New Decisions), were approved by the owner as recommended on
2026-10-23: the institution lives on the group (N26 (a)), and an existing account's different
recovery e-mail is a change confirmed one by one (N27).

## Constitution Check (1.2.0)

| Principle | I1 |
|---|---|
| Dual database (R1) | Two new tables and the same methods in both repositories; `db_sync_check.py`; repository and API tests on both engines |
| Additive migrations (R8) | New tables (`student_identifications`, `student_imports`, `student_import_rows`) and, since N24, one nullable column `users.recovery_email`; under N26 (a) two nullable columns on `groups`. `SCHEMA_VERSION` takes the next free number with its digest, so I1 needs its own backup and rehearsal before production. Existing accounts get no link |
| Layers (R2) | Reading an identification, a row's level and grade, and the classification of a preview in `src/domain/student_import.py`, no I/O; reading the file in `src/infrastructure/importing/`; persistence in the repositories; HTTP in `api/` |
| Secrets and personal data (R7, VI) | The initial password is the identification, stored only as its Argon2id hash. No identification, display name or file in logs, audit rows or error messages meant for logs; the audit keeps internal IDs and reason codes. Tests use invented identifications only (the repository is public) |
| Single process (R18) | One import at a time per admin is enforced in the database, not in memory, so it holds across restarts |
| No blocking I/O in async code (R17) | The confirmation runs in a worker thread; the endpoints are `def` |

## Design

### Reading the file (FR-001, FR-004, P12)

- `.csv` (UTF-8 with or without BOM; `,` or `;`, sniffed) or `.xlsx` (openpyxl, read-only,
  values not formulas; the first sheet). At most 5 MB — refused from `Content-Length` and again
  while reading — and 500 data rows; the first non-empty row is the header.
- Cells keep their type: text stays text. An `.xlsx` numeric cell holding a whole number of up to 15
  digits is read as its digits (N16); a decimal, a value of more than 15 digits or one in
  scientific notation is flagged as altered by the spreadsheet and never rebuilt.
- `normalize_identification(raw)`: outer spaces removed; only digits accepted. Anything else —
  dots, dashes, spaces inside, letters, `1,2E+09` — is an error with its reason, never corrected.

### Mapping and batch choices (FR-001, P8, P9)

- The admin maps one column to the identification and one or two to the display name (N19), and
  optionally columns to level, grade, institution and recovery e-mail. Unmapped level and grade
  come from values chosen for the batch (N20).
- The last day of access is chosen for the batch (spec 004 FR-046); a last day already past is
  refused, as in spec 004's creation. The group is no longer one per batch: each row's
  (institution, grade) pair is paired with an existing group (N21; § The form's answers).
- Level and grade are checked with spec 004's `student_level_problem`: semillero takes a grade from
  6.º to 11.º, the other levels «No aplica». A mapped value that does not match a known one is an
  error for that row, never guessed; the form's grade values are listed in § The form's answers.

### Preview (FR-002, FR-007, US1-AS10)

`classify_rows` is pure: it receives the parsed rows, the mapping, the batch choices and two lookups
read from the database — the linked identifications and the usernames in use. Each row gets one
status and its reasons:

| Status | When |
|---|---|
| `new` | A valid identification not linked to any account and not a username in use; a display name the filter accepts; a valid level and grade |
| `existing` | The identification is linked to an account. Its group or last day may differ from the batch's: the preview shows each difference as a change to confirm (FR-008) |
| `duplicate` | The identification appears earlier in the file; only the first occurrence counts |
| `error` | Any problem: identification format, no display name or a refused one (spec 004 FR-020), level and grade, or an identification that is the username of an account not linked to it (FR-007) |

Nothing is saved by the preview.

### Confirmation without keeping the file (FR-003, FR-006, FR-010, FR-011)

- The preview stores nothing. It returns a `preview_digest`: the SHA-256 of the file's bytes, the
  mapping, the batch choices and every row's status. To confirm, the admin's browser sends the same
  file and choices again (it keeps the `File` in memory, so the admin does not pick it again) with
  the digest and the changes to existing accounts it confirms.
- The server reads the file again, recomputes the preview and its digest. If they differ — another
  file or choices, or a row whose status changed since the preview because someone created or
  linked an account meanwhile — it refuses and asks for a new preview. The admin confirms exactly
  what they saw.
- Then it opens an import record: `student_imports` with the admin, the time, an operation
  identifier (`import_id`, also the idempotency key) and the state `running`. A partial unique
  index allows one `running` import per admin; a second confirmation while one runs is refused,
  and a retry of the same confirmation (same digest, same admin) returns that import (FR-010).
- No file is written anywhere; the bytes live in the request and the worker's memory until the
  import ends.

### Running the import (FR-003, FR-005, FR-008, SC-002)

- Hashing a password costs about 100 ms and 64 MiB (`hashing_service.py`, at most two hashes per
  process at once). 500 students take about a minute of one of those two slots. So the confirmation
  answers `202` with the `import_id` and a worker thread does the work; the screen polls the
  import's state. Logins keep the other slot throughout.
- Rows are created in chunks of 25, each chunk one transaction, through a repository method that
  applies spec 004's creation (`create_student_account`'s checks: admin, group, name filter, level
  and grade, last day) with the import's credentials: username and initial password are the
  identification, no forced change (FR-005), the identification linked with origin `import`.
- Each row is re-checked inside its transaction: an identification linked or a username taken
  since the confirmation makes that row `skipped` with its reason — never a duplicate (FR-006).
  Re-importing the same file therefore creates nothing and changes nothing.
- Confirmed changes to existing accounts (FR-008) go through the existing operations: the group
  through the admin's group change (audited) and the last day through `set_access_until`
  (spec 004 FR-050). Nothing else of an existing account is touched: no password, no progress.
- A worker that dies (a restart) leaves the import `running`; after 10 minutes without progress it
  is marked `interrupted`. Confirming the same file again finishes it: the rows already created
  are `existing`.
- Measured before the delivery closes: 500 students on SQLite and PostgreSQL locally, and the
  time reported to the owner with the processing used (P12, SC-002). Nothing changes without that
  report.

### Linking an existing account (FR-007, US1-AS5)

`PUT /api/admin/users/{id}/identification` links an identification to a student account that has
none, if no other account has it linked; recorded. Its username does not change and the account
keeps its own credentials: the link only lets later imports recognise it. Nothing is ever matched
or merged by name. Removing a link made by mistake is FR-017 (N18; § The form's answers).

### Who sees the identification (FR-013, US2, SC-003)

- The link lives in `student_identifications`, apart from `users`. Only two readers return it:
  `/api/auth/me` for the account itself and the admin's users list and import screens.
- An imported student's username is their identification, so every response other people see
  must show the display name, not the username. Spec 004 E2 already does this (its public name).
  I1 adds a test that walks every student and teacher endpoint, the PvP messages and the teacher's
  exports with two imported students in one group, and asserts that neither body holds the other's
  identification.

### The name of an imported account (FR-014, FR-015)

- `set_display_name` refuses the student's own change when the account's link has origin `import`;
  the admin still changes it, recorded (spec 004 FR-025 otherwise unchanged).
- `create_student_account` (spec 004) refuses a username that is an identification linked to
  another account (FR-015).

### Audit (FR-009, US1-AS7)

`student_imports` (admin, times, `import_id`, state, counts) and `student_import_rows` (row number,
result, internal account ID or none, reason code). No identification, name, password or file.
`GET /api/admin/imports` and `/api/admin/imports/{id}` read them. Group and last-day changes and
links also land in `audit_account_events`.

### Access (FR-012)

Every endpoint is under `/api/admin` and requires the admin role; the upload size and row limits
are checked before reading the whole file.

### API

| Endpoint | Purpose |
|---|---|
| `POST /api/admin/imports/columns` | Upload → the header and five example rows, to map (multipart) |
| `POST /api/admin/imports/preview` | File + mapping + batch → rows with status and reasons, and the digest |
| `POST /api/admin/imports` | File + mapping + batch + digest + confirmed changes → `202 {import_id}` |
| `GET /api/admin/imports/{import_id}` | State, counts, row results |
| `GET /api/admin/imports` | The admin's imports, most recent first |
| `PUT /api/admin/users/{id}/identification` | Explicit link |
| `DELETE /api/admin/users/{id}/identification` | Remove a link made by mistake (FR-017) |
| `POST /api/admin/teachers/{id}/groups` | A group for an institution and grade, owned by that teacher (N25) |

### Screens

- Admin → «Importar estudiantes» (`frontend/src/pages/Admin/Import.tsx`), four steps:
  1. upload;
  2. map the columns, with the example rows;
  3. the last day; level and grade where not mapped; each (institution, grade) pair of the file
     paired with a group (N21);
  4. the preview — counts per status, each row with its reasons, filters, and a check box for each
     change to an existing account — then «Confirmar», progress and result.
- The admin's users list shows the identification of linked accounts and offers «Vincular
  identificación» and, on a linked one, «Quitar vínculo» (FR-017).
- The admin's teachers list offers «Crear grupo» for a teacher (N25).
- The student's account page (`/mi-nombre`) shows their identification. For an imported account it
  shows the name read-only, with «Tu nombre lo cambia el administrador».

## The form's answers (N1, N19 … N25; amendment of 2026-10-23)

The form's columns arrived on 2026-10-18 and the owner answered N19 … N25 the same day. What they
change in the design above:

- **Display name (N19, FR-001).** The admin maps one or two columns and their order; the two values
  are joined with one space («Nombres Apellidos») after removing outer spaces, and spec 004's filter
  and limits judge the joined name. An empty result is an error (US1-AS10).
- **Level and grade (N20, P9).** The batch's level is chosen once (for this olympiad, semillero);
  the grade comes from the grade column. The form's six values «Sexto», «Séptimo», «Octavo»,
  «Noveno», «Décimo», «Undécimo» read as 6 … 11, compared without case, accents or outer spaces;
  any other value is an error for the row, never guessed. `student_level_problem` still checks the
  pair.
- **Group by institution and grade (N21, N25, FR-001, FR-002).** There is no batch group any more.
  The admin creates the teachers and one group per institution and grade before importing (N25).
  In the import, every distinct (institution, grade) pair found in the file is paired with an
  existing group — by the admin in step 3, or suggested under N26 (a) — and a row whose pair has no
  group, «Otro» included, is an error. «Sede» is not read.
- **Only the needed columns (N23, FR-016).** The reader hands the preview and the import only the
  mapped columns; every other column of the file (document type, guardian, «Sede»,
  authorisation…) is dropped while reading and never reaches the preview, a stored record or a log.
  The mapping step alone shows the admin the header and up to five example rows, to choose the
  columns; nothing of it is stored.
- **Recovery e-mail (N24, FR-018).** An optional mapped column fills the new `users.recovery_email`
  (nullable, not unique, never read by sign-in; `users.email` stays the sign-in e-mail and is not
  touched). A value that is not an e-mail address is an error for that row; the same address on
  several rows is allowed. For an existing account see N27.
- **Removing a link (N18, FR-017).** `DELETE /api/admin/users/{id}/identification`, admin only,
  recorded in `audit_account_events`; the account's username and credentials do not change. A later
  import treats that identification as unlinked: a row with it is an error while it is still that
  account's username (FR-007).
- **Groups for an institution and grade (N25).** Today only a teacher creates groups. The admin
  needs to create the per-institution-and-grade groups owned by a teacher:
  `POST /api/admin/teachers/{id}/groups` with the name and course (and, under N26 (a), the
  institution and grade), through the same repository method and checks as the teacher's own.

### Where the institution lives (N26, approved 2026-10-23: (a))

Spec 007 FR-022 matches League players «of the same institution, read from the student's
institution as recorded by spec 009», but spec 009 reads the institution only to pick a group. Under
the recommendation the group records it:

- **(a) recommended — on the group.** `groups.institution` (text) and `groups.grade` (6 … 11), both
  nullable, set when the admin creates the group. The import pairs each (institution, grade) with
  the group that has those values (the admin can change the pairing before the preview); a
  student's institution is their main group's. Students created one by one or enrolled by
  invitation get one too, through their group; a group without an institution gives none, and
  spec 007 G decides what that means.
- **(b) on the student.** A per-student institution written by the import. Accounts not imported
  have none, so spec 007 G needs a fallback for them.
- **(c) nowhere.** The pairing lives only in the import request; spec 007 FR-022 then has no source
  and needs its own decision.

### An existing account's recovery e-mail (N27, approved 2026-10-23)

FR-018 fills the recovery e-mail of the accounts the import creates. For an account that already
exists, re-importing changes nothing (FR-006), and FR-008 asks a specific confirmation only for the
group and the last day. **Recommended:** treat a different recovery e-mail like those two — shown as
a difference in the preview and applied only when the admin confirms it for that account. The
alternatives are to fill it only when the account has none, or never to touch it on an existing
account.

### Headers for the mapping (T024)

The form's headers suggest the mapping: «Número de documento» → identification, «Nombres» and
«Apellidos» → display name in that order, «Grado que cursas en 2027» → grade, «Institución
educativa» → institution, «Correo electrónico de contacto» → recovery e-mail. The admin can change
every suggestion.

## Merge order

After spec 004's E3 (LuisJRubioH/LevelUp-ELO#73). E2 is in production since 2026-10-22, so E3 can
merge after its own backup and rehearsal (schema version 7). I1 takes the next free schema version
(8, or 9 if spec 008 L takes 8 first) and needs its own backup and rehearsal too.
