# Plan — spec 009, delivery GI: a group's institution and grade

**Spec**: [spec.md](spec.md) § Deliveries, GI (US4; FR-019 … FR-024; N28) · **Branch**: docs
`009-plan-gi`, from `009-student-import-i1` (LuisJRubioH/LevelUp-ELO#158, unmerged), because GI
edits the columns I1 adds and its Code Scope names files only I1 creates; code `009-gi`, from
`redesign` once #158 is merged · **Date**: 2026-10-27

**Status**: approved by the owner (2026-10-27): O-GI1 … O-GI6 as recommended — option (a) of
each. The spec text is written under those options.

**Why now.** Spec 007's plan G (`origin/007-plan-g`, O-G5, approved 2026-10-27) refuses with 4414
a real student whose main group has no `groups.institution`. I1 sets the institution only on the
groups the admin creates through it; every group created before I1 — by a teacher or by the admin —
keeps NULL, so G2 would refuse every current student. The owner ordered an admin edit in the panel,
not a one-off repair script, because the institution is data kept over time (spec 007 plan-g
§ O-G5; spec N28). **GI must reach `main` before G2.**

## Constitution Check (1.2.0)

| Principle | GI |
|---|---|
| Dual database (R1) | One new repository method, `set_group_institution`, in both repositories with the same signature; one read, `get_recorded_institutions`, `@_read_only` in both; `db_sync_check.py`; repository and API tests parametrised over both engines |
| Additive migrations (R8) | **No schema change under O-GI1 (a)**: GI writes I1's `groups.institution` and `groups.grade` (schema 8) and audits in spec 004's `audit_account_events`. Under O-GI1 (b) one new table, the next free schema version (10: I1 takes 8, spec 008 L plans 9), with its digest, backup and rehearsal |
| Layers (R2) | The rules — the institution as stored, the grade's range, the comparison key — are pure functions in `src/domain/` (`student_import.py`, `identity.py`); the repository applies them inside its transaction; HTTP in `api/routers/admin.py` |
| One source of truth (II) | The comparison key is spec 004's (`identity._comparable` plus collapsed spaces), the same spec 007 G uses (O-G6), computed on the server; the screen never folds text itself |
| Accounts untouched (FR-021) | The method's only `UPDATE` is on `groups` (institution, grade); a test snapshots every student's row, enrolments and ratings before and after |
| Secrets and personal data (VI) | An institution is a school's name, not personal data; the audit holds IDs and the institution and grade, never a student's data |
| Single process (R18), no blocking I/O (R17) | Plain `def` endpoints; nothing in memory |

## Design

### The rules, without I/O (FR-019, FR-024)

- `src/domain/student_import.py::group_institution_problem(institution, grade) -> str | None`:
  the institution is a non-empty text of at most 200 characters once outer spaces are removed and
  inner spaces collapsed (O-GI6 (a)); the grade is None or in `GROUP_GRADES` (6 … 11), the range
  I1's `group_for_teacher_problem` already applies to a new group. A bool is not a grade. The
  reasons are the Spanish messages of I1's (`"El grado del grupo va de 6.º a 11.º."`) plus
  `"Escribe la institución."` and `"La institución tiene más de 200 caracteres."`.
- `stored_institution(text) -> str`: outer spaces removed, inner spaces collapsed, case and accents
  kept — exactly what I1's `create_group_for_teacher` does inline today; I1's creation is switched
  to call it, with no change of behaviour (its tests stay green).
- `src/domain/identity.py::comparable_key(text) -> str | None`: spec 004's `_comparable` over the
  collapsed text (case and accents folded, ñ kept), None when empty. **Shared with spec 007 G**,
  whose plan says G exposes the same rule from this file: whichever delivery lands first adds it and
  the other uses it; the name is agreed in the PR that lands first. GI uses it only to compare;
  nothing stores the key.

### The edit (FR-019, FR-020, FR-021, FR-023)

`set_group_institution(admin_id, group_id, institution, grade, confirm_same=False)` in both
repositories → `(ok, code, result)`:

1. `group_institution_problem` → `(False, "invalid", reason)`, before any connection.
2. One transaction: the admin must be active (`_is_active_admin`) → `"forbidden"`; the group is read
   — PostgreSQL `SELECT … FROM groups WHERE id = %s FOR UPDATE`, SQLite `BEGIN IMMEDIATE` — →
   `"not_found"` when missing.
3. Unchanged institution (as stored) and grade → `(True, "unchanged", …)`; nothing written, no audit
   row (FR-020).
4. Other groups whose `comparable_key(institution)` equals the new one and whose grade is the same
   (read in the same transaction; the keys are computed in Python, never in SQL) → while
   `confirm_same` is false, `(False, "same_institution_and_grade", [{id, name, teacher}])` and
   nothing written (O-GI5 (a)).
5. `UPDATE groups SET institution = ?, grade = ? WHERE id = ?` — the only write to `groups`, no
   other column — and the audit row of O-GI1 in the same transaction; commit.
6. Returns the stored values and, under O-GI2 (a), `students_with_other_grade`: the active
   non-test students of the group whose own `users.grade` (text, spec 004) differs from the group's
   new grade — a raw count, nothing changed.

R4 holds: `put_connection`, never `close`, on PostgreSQL; the read of step 4 and the update share
the transaction, so two admins editing at once serialise on the group's lock.

### The audit (FR-020) — O-GI1

**(a) recommended, no schema.** A row of spec 004's `audit_account_events`: `actor_id` the admin,
`user_id` the group's teacher (the column is `NOT NULL` and points to `users`; the teacher is the
account the group belongs to), `action = 'group_institution_changed'`, `detail` a JSON text
`{"group_id": …, "before": {"institution": …, "grade": …}, "after": {…}}`. `GET
/api/admin/account-audit` already returns it; `Audit.tsx` gains its label («Institución del
grupo») and shows the group and the values from `detail`.

### Listing (FR-022)

- `GET /api/admin/groups` already returns `institution` and `grade` (I1). GI adds the query
  `?without_institution=true`: only groups whose institution is NULL or blank, and the response's
  `count`. The filter runs in the router over the repository's raw rows (R15's spirit: no new SQL
  for a view).
- `GET /api/admin/institutions` → the recorded institutions, one per `comparable_key`, each with the
  spelling of its oldest group and how many groups carry it. A new read, `get_recorded_institutions`
  (`@_read_only`, both engines), returns the raw `(id, institution)` pairs; the router groups them
  by key with the domain function.

### API

| Endpoint | Purpose |
|---|---|
| `PUT /api/admin/groups/{group_id}/institution` | `{institution, grade, confirm_same}` → 200 `{group_id, institution, grade, unchanged, students_with_other_grade}`; 400 with the reason (FR-019); 404 unknown group; 409 `{code: "same_institution_and_grade", groups: [...]}` (O-GI5); 403 for anyone but the admin (FR-023) |
| `GET /api/admin/groups?without_institution=true` | Only the groups without institution, with `count` (FR-022) |
| `GET /api/admin/institutions` | The recorded institutions, one per key, for the form's suggestions (FR-024) |

All under `require_role("admin")`, in `api/routers/admin.py` beside the existing group endpoints.

### Screen — `frontend/src/pages/Admin/Groups.tsx`

- Two new columns, «Institución» and «Grado» («—» when empty), and a toggle «Solo grupos sin
  institución (N)» that reads the filtered endpoint; the count is visible without the toggle so the
  admin knows what is left before G2 ships.
- «Editar institución» on each row opens an inline form: the institution with a `datalist` of
  `GET /api/admin/institutions` (typing «Colegio San José» picks the recorded spelling instead of a
  new variant, which would split one school into two League keys), and the grade as a select
  («No aplica», 6.º … 11.º).
- A 409 shows the groups that share institution and grade, with «Guardar de todos modos», which
  resends with `confirm_same: true`. A 200 with `students_with_other_grade > 0` shows «N
  estudiantes de este grupo tienen otro grado; no se cambia el suyo.»
- D1: the empty institution cell is drawn in the warning token (`#F59E0B`), so the groups still to
  fix stand out; D3 holds (data first). Strings in `i18n/locales/es.ts` and `en.ts`; `adminApi` in
  `frontend/src/api/teacher.ts` gains `setGroupInstitution` and `institutions`, and `AdminGroup`
  is unchanged (I1 already has the fields).

### What GI does not touch

- Students: group, level, grade, enrolments, last day, credentials, ratings (FR-021). The League
  reads the new institution at the student's next entry (spec 007 G reads it at entry).
- I1's import: a pairing suggested from an edited institution changes the preview's digest, so a
  confirmation prepared before the edit is refused and a new preview is asked (FR-003; spec § Edge
  Cases). I1's `suggest_pairing` folds with `_folded`, which drops the tilde of ñ, while spec 004
  and spec 007 O-G6 keep it; GI leaves I1's suggestion as it is and records the difference here for
  the owner (a later alignment would be one function and its test).
- The teacher's own group creation still takes no institution (I1 unchanged).

## Owner decisions (open)

| # | Point | Recommended | Alternatives |
|---|---|---|---|
| **O-GI1** | Where the edit's audit lives (FR-020) | **(a)** spec 004's `audit_account_events` (`user_id` the group's teacher, `action = 'group_institution_changed'`, the group and the values in `detail`): **no schema change**, shown in the existing account audit | **(b)** a new `audit_group_edits` table (group, admin, before and after, time): **schema version 10** (I1 8, spec 008 L 9), both repositories, digest, D3 parity, its own backup and rehearsal before production. **(c)** `audit_group_changes`: rejected — its `student_id` is `NOT NULL` and it records reassignments |
| **O-GI2** | The grade of a group that already has students | **(a)** editable; the response and the screen say how many of its students have another grade; theirs never changes (FR-021) | **(b)** the grade is locked while the group has active students (only the institution is editable) — FR-019 gains a refusal. **(c)** also change the students' grade: rejected, it changes accounts and their courses (spec 001 FR-028k) |
| **O-GI3** | A bulk file (CSV) of group, institution and grade | **(a)** no: one group at a time; groups are few (one per institution and grade, N25) | **(b)** a CSV with preview and confirmation reusing I1's reader, as a later delivery if the count of groups to fix makes it worth it |
| **O-GI4** | Notifying the group's teacher | **(a)** no notice; the audit records it and the teacher's view does not change | **(b)** a notice to the teacher through the notifications socket (`api/websocket/notifications.py`), a new message type |
| **O-GI5** | Another group with the same institution (by key) and grade (US4-AS6, FR-024) | **(a)** allowed after the admin confirms it (two groups of one grade at one school are normal: 6.º A and 6.º B) | **(b)** refused — one group per institution and grade, as N21 first described. **(c)** allowed silently |
| **O-GI6** | Clearing a group's institution | **(a)** refused: an empty institution is invalid (FR-019), since it would put the group's students out of the League (spec 007 O-G5) | **(b)** allowed, after a confirmation that names how many students lose the League |

## Tests (one per FR and scenario; tasks-gi.md)

| Test | Covers | File |
|---|---|---|
| `test_spec009_gi_a_group_institution_is_stored_as_typed_and_checked` | FR-019, US4-AS3 | `tests/unit/domain/test_spec009_gi_group_institution.py` |
| `test_spec009_gi_institutions_compare_by_spec004_key` | FR-024 | same file |
| `test_spec009_gi_the_admin_sets_a_groups_institution_and_grade` | US4-AS1, FR-019, FR-020 | `tests/integration/test_spec009_gi_group_institution.py` |
| `test_spec009_gi_an_unchanged_save_records_nothing` | FR-020 | same file |
| `test_spec009_gi_an_edit_changes_no_account` | US4-AS2, FR-021 | same file |
| `test_spec009_gi_an_invalid_edit_changes_nothing` | US4-AS3, FR-019 | same file |
| `test_spec009_gi_only_an_active_admin_edits` | US4-AS4, FR-023 | same file |
| `test_spec009_gi_the_groups_without_institution_are_listed_with_their_count` | US4-AS5, FR-022 | same file |
| `test_spec009_gi_the_same_institution_and_grade_asks_for_confirmation` | US4-AS6, FR-024 | same file |
| `test_spec009_gi_recorded_institutions_one_per_key` | FR-024 | same file |
| `editar la institución y el grado de un grupo sin institución (US4-AS1, US4-AS5)` | US4-AS1, US4-AS5, FR-022 | `frontend/e2e/spec009-gi-groups.spec.ts` |
| `la misma institución y grado pide confirmación (US4-AS6)` | US4-AS6, FR-024 | same file |

The integration file runs on both engines (`repo` fixture parametrised, as I1's
`test_spec009_import_store.py`).

## Merge order

1. This docs PR, after #158 (I1) in merge order: it is based on I1's branch.
2. GI's code PR from `redesign` after #158 is merged; no schema change under O-GI1 (a), so no
   backup or rehearsal of its own beyond I1's schema 8.
3. Then the admin sets the institution of every group that holds League players, in production.
4. Then spec 007 G2 (FR-022), whose PR checks that the count of groups without institution among
   League players is zero (spec 007 plan-g § D3).

## Files the code PR touches

- `src/domain/student_import.py` — `group_institution_problem`, `stored_institution` (I1's creation
  calls it)
- `src/domain/identity.py` — `comparable_key` (shared with spec 007 G)
- `src/application/interfaces/repositories.py` — the two methods
- `src/infrastructure/persistence/sqlite_repository.py`, `postgres_repository.py` — the same
  methods (R1); under O-GI1 (b) also the table, `schema_version.py` and `engine_differences.py` if
  needed
- `api/routers/admin.py` — the three endpoints
- `frontend/src/pages/Admin/Groups.tsx`, `frontend/src/pages/Admin/Audit.tsx`,
  `frontend/src/api/teacher.ts`, `frontend/src/i18n/locales/` (es, en)
- Tests: `tests/unit/domain/test_spec009_gi_group_institution.py`,
  `tests/integration/test_spec009_gi_group_institution.py`, `frontend/e2e/spec009-gi-groups.spec.ts`
- `specs/009-student-import/spec.md` (Traceability rows, GI `closed`), `AGENTS.md` (the audit
  action, under O-GI1 (a))
