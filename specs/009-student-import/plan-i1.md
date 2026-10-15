# Plan — spec 009, delivery I1: the initial student import

**Spec**: [spec.md](spec.md) § Deliveries, I1 (US1 … US3; FR-001 … FR-015) · **Branch**:
`009-student-import-i1`, from spec 004's E3 (`004-identity-e3`, LuisJRubioH/LevelUp-ELO#73), whose
creation and expiry rules it reuses · **Date**: 2026-10-15

Written before the Google Form's columns are known (N1). The admin maps the file's columns, so
almost nothing below depends on them; what does is listed in § Waiting on the form and marked
`[N1]` in [tasks-i1.md](tasks-i1.md).

## Constitution Check (1.2.0)

| Principle | I1 |
|---|---|
| Dual database (R1) | Two new tables and the same methods in both repositories; `db_sync_check.py`; repository and API tests on both engines |
| Additive migrations (R8) | New tables only (`student_identifications`, `student_imports`, `student_import_rows`); no column of `users` changes. Existing accounts get no link |
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

- The admin maps one column to the identification and one to the display name, and optionally
  columns to level and grade. Unmapped level and grade come from values chosen for the batch.
- An existing group and the last day of access are chosen for the batch (spec 004 FR-044,
  FR-046). A last day already past is refused, as in spec 004's creation.
- Level and grade are checked with spec 004's `student_level_problem`: semillero takes a grade from
  6.º to 11.º, the other levels «No aplica». A mapped value that does not match a known one is an
  error for that row, never guessed. **[N1]** Which values the form's answers use.

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
or merged by name. Removing or correcting a link is not in the spec (**N18**).

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

### Screens

- Admin → «Importar estudiantes» (`frontend/src/pages/Admin/Import.tsx`), four steps:
  1. upload;
  2. map the columns, with the example rows;
  3. group, last day, and level and grade where not mapped;
  4. the preview — counts per status, each row with its reasons, filters, and a check box for each
     change to an existing account — then «Confirmar», progress and result.
- The admin's users list shows the identification of linked accounts and offers «Vincular
  identificación».
- The student's account page (`/mi-nombre`) shows their identification. For an imported account it
  shows the name read-only, with «Tu nombre lo cambia el administrador».

## Waiting on the form (N1)

- Which columns hold the identification, the name (one column, or first and last names apart) and,
  if any, level and grade — for default mapping suggestions and the realistic test file.
- The values the form's answers use for level and grade, to read them without guessing.
- Whether any other column matters to the import (for example, the guardians' authorisation).

The design does not change with the answers. If the name comes in two columns, the mapping joins
first and last names with one space.

## Merge order

After spec 004's E3 (LuisJRubioH/LevelUp-ELO#73), which is merged only once E2 is in production, and
after the owner sends the columns (N1). Not part of the switch to `main` (LuisJRubioH/LevelUp-ELO#3).
