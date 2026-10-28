# Tasks — spec 009, delivery GI (a group's institution and grade)

**Plan**: [plan-gi.md](plan-gi.md). **Status**: approved by the owner (2026-10-27; O-GI1 …
O-GI6 as recommended). Every GI requirement is `[CHANGE]`: the base has no edit of a group's institution, no
filter of groups without one and no list of recorded institutions, so each test is written first
and must fail on the base (missing function, method, endpoint, query or control) before its
implementation. There are no `[AS-IS]` requirements, so there is no characterization phase; I1's
own tests are the guard for the one I1 function GI refactors (T015). `[O-GIn]` marks a task whose
content follows the recommended option of that decision; another option changes it as the plan's
row says. `[P]` marks tasks that can run in parallel with the others of their phase.

**Depends on**: spec 009 I1 merged into `redesign` (LuisJRubioH/LevelUp-ELO#158: `groups.institution`
and `groups.grade`, schema 8, `create_group_for_teacher`). GI's code must reach `main` before spec
007's G2 (spec 007 O-G5).

## Phase 0 — Owner decisions

- [ ] T001 The owner answers O-GI1 … O-GI6 (plan-gi § Owner decisions); spec.md N28 and this file
  are updated with the answers. Under O-GI1 (b) add T019; under O-GI2 (b) T007 gains the refusal of
  a grade on a group with students; under O-GI3 (b) or O-GI4 (b) a new task each; under O-GI5 (b)
  T010 expects a refusal; under O-GI6 (b) T003 and T007 accept a cleared institution after
  confirmation

## Phase 1 — Setup

- [ ] T002 After #158 is merged, branch `009-gi` from `redesign`; spec 009's Code Scope gains each
  new file as it is created (the checker accepts only tracked files)

## Phase 2 — Tests first (each must fail on the base)

### Domain, no I/O — `tests/unit/domain/test_spec009_gi_group_institution.py`

- [ ] T003 [P] `test_spec009_gi_a_group_institution_is_stored_as_typed_and_checked`: outer spaces
  removed and inner spaces collapsed, case and accents kept («  Colegio   San José » → «Colegio San
  José»); empty or blank refused `[O-GI6]`; more than 200 characters refused; grade None or 6 … 11,
  5, 12, `True` and a text refused, each with its reason (FR-019, US4-AS3)
- [ ] T004 [P] `test_spec009_gi_institutions_compare_by_spec004_key`: «Colegio  San José» and
  «colegio san jose» share a key; «Piñas» and «Pinas» do not (ñ kept); blank → None (FR-024; spec
  007 O-G6)

### Both engines — `tests/integration/test_spec009_gi_group_institution.py`

(Repository and API on SQLite and PostgreSQL, the `repo` fixture parametrised as in I1's
`test_spec009_import_store.py`.)

- [ ] T005 `test_spec009_gi_the_admin_sets_a_groups_institution_and_grade`: a group created by a
  teacher (no institution) → `PUT /api/admin/groups/{id}/institution` → 200; `GET /api/admin/groups`
  shows them; one audit entry with the admin, the group, the time, before (none) and after
  `[O-GI1]` (US4-AS1, FR-019, FR-020)
- [ ] T006 `test_spec009_gi_an_unchanged_save_records_nothing`: saving the same values → 200
  `unchanged`, no new audit entry (FR-020)
- [ ] T007 `test_spec009_gi_an_edit_changes_no_account`: a group with three students (one with
  another grade, one test user), each enrolled and rated; snapshot of `users` rows, enrolments,
  `student_course_topic_elo` and the group's name, teacher and course; edit institution and grade;
  the snapshot is identical, and `students_with_other_grade` counts the active non-test student
  with another grade `[O-GI2]` (US4-AS2, FR-021)
- [ ] T008 `test_spec009_gi_an_invalid_edit_changes_nothing`: empty institution `[O-GI6]`, 201
  characters, grade 12 → 400 with the reason; unknown group → 404; the group and the audit
  unchanged (US4-AS3, FR-019, FR-023)
- [ ] T009 `test_spec009_gi_only_an_active_admin_edits`: a teacher (the group's own included) and a
  student → 403 on the edit, the filter and the institutions list; a deactivated admin's call to
  the repository method → refused; nothing changes (US4-AS4, FR-023)
- [ ] T010 `test_spec009_gi_the_same_institution_and_grade_asks_for_confirmation`: another group
  with «colegio san jose», grade 6 → saving «Colegio San José», 6 → 409 naming that group, nothing
  written; again with `confirm_same: true` → 200, stored as typed; same institution with another
  grade → 200 at once `[O-GI5]` (US4-AS6, FR-024)
- [ ] T011 `test_spec009_gi_the_groups_without_institution_are_listed_with_their_count`:
  `?without_institution=true` returns exactly the groups whose institution is NULL or blank, with
  `count`, teacher and number of students; after T005's edit the group leaves it (US4-AS5, FR-022)
- [ ] T012 `test_spec009_gi_recorded_institutions_one_per_key`: three groups «Colegio San José»
  (oldest), «colegio san jose», «Liceo Piñas» → two entries, the first with the oldest spelling and
  2 groups (FR-024)

### Screen — `frontend/e2e/spec009-gi-groups.spec.ts`

- [ ] T013 `editar la institución y el grado de un grupo sin institución (US4-AS1, US4-AS5)`: the
  admin sees «Solo grupos sin institución (N)», opens one, picks a suggested institution and a
  grade, saves; the row shows them and N drops by one (US4-AS1, US4-AS5, FR-022)
- [ ] T014 `la misma institución y grado pide confirmación (US4-AS6)`: the warning names the other
  group; «Guardar de todos modos» saves (US4-AS6, FR-024)

## Phase 3 — Implementation

- [ ] T015 `src/domain/student_import.py`: `group_institution_problem`, `stored_institution`; I1's
  `create_group_for_teacher` (both repositories) calls `stored_institution` instead of its inline
  expression, with I1's tests green; `src/domain/identity.py`: `comparable_key` (or spec 007 G's
  name if G1 has landed) (makes T003, T004 pass)
- [ ] T016 `set_group_institution` and `get_recorded_institutions` (`@_read_only`) in both
  repositories and in `src/application/interfaces/repositories.py`; the lock, the same-key read,
  the single `UPDATE groups`, the audit row `[O-GI1]` in one transaction (R1, R4, R16's lock order
  untouched); `python scripts/db_sync_check.py` (T005 … T010, T012 at the repository level)
- [ ] T017 `api/routers/admin.py`: `PUT /groups/{id}/institution`, `?without_institution=true` on
  `GET /groups`, `GET /institutions` (T005 … T012)
- [ ] T018 `frontend/src/pages/Admin/Groups.tsx` (columns, the toggle and its count, the inline
  form with the datalist, the 409 warning, the other-grade notice), `Audit.tsx` (the action's
  label and detail), `frontend/src/api/teacher.ts` (`adminApi.setGroupInstitution`,
  `adminApi.institutions`), strings in `frontend/src/i18n/locales/es.ts` and `en.ts` (T013, T014)
- [ ] T019 *(only under O-GI1 (b))* the `audit_group_edits` table in both repositories, additive
  (R8); `SCHEMA_VERSION` 10 and `MIGRATION_SOURCES_DIGEST`; the D3 parity test; `docs/transfer.md`
  (backup and rehearsal for the new version)

## Phase 4 — Close

- [ ] T020 Traceability: every GI row of spec 009 filled with T003 … T014's tests and GI `closed`;
  AGENTS.md (the `group_institution_changed` audit action, under O-GI1 (a)); `check_traceability.py
  --run`, the full suite on both engines, Playwright, `db_sync_check.py`, black, flake8 and
  `pnpm run build`
- [ ] T021 In the code PR, the count of groups without institution in production, read by the
  owner from the admin panel after the merge, is the input to spec 007 G2's gate (plan-g § D3)

## Traceability map

| Spec ID | Test task(s) |
|---|---|
| US4-AS1 | T005, T013 |
| US4-AS2 | T007 |
| US4-AS3 | T003, T008 |
| US4-AS4 | T009 |
| US4-AS5 | T011, T013 |
| US4-AS6 | T010, T014 |
| FR-019 | T003, T005, T008 |
| FR-020 | T005, T006 |
| FR-021 | T007 |
| FR-022 | T011, T013 |
| FR-023 | T008, T009 |
| FR-024 | T004, T010, T012, T014 |
