# Tasks — spec 006, delivery X2 (templates and results)

**Plan**: [plan-x2.md](plan-x2.md) (approved by the owner, 2026-10-19). FR-030 … FR-033 are
`[CHANGE]`.

## Found while implementing

- **Students' rule.** «The teacher's students» is the dashboard's set (`get_teacher_dashboard_stats`
  of the template's author) until C1 builds one set for the whole console. Names are the visible
  name (spec 004).
- **First submission.** The earliest stored session of each student, by date, then by id. Older
  databases may hold retakes from before X1.
- **Locked items.** Only a change of items is refused (409). Sending the same list is accepted, and
  the title and time limit stay editable. «Duplicar» makes an unassigned, unlocked copy named
  «… (copia)».
- **Assignment.** Groups must be the template author's (400 otherwise, as before) and of the
  template's course (422). All groups are written in one transaction (`assign_template_to_groups`);
  `create_exam_assignment` stays for the frozen V1.
- **Results.** The repository returns raw rows (`get_exam_template_responses`); the domain computes
  them (`src/domain/exams/results.py`). `get_exam_template_results` is gone. Each item counts the
  wrong options chosen (`choices`).
- **Schema.** `exam_responses.selected_option` (TEXT): `SCHEMA_VERSION` 5 with its digest.
  Rows stored before X2 have NULL there. `docs/transfer.md` § 5 and § 6 now say 5.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/integration/test_spec006_x2_templates.py` (both engines), covering US3-AS1 … AS3
  and FR-030 … FR-033:
  - the draft;
  - the lock and the duplicate;
  - the one-course, all-or-nothing assignment;
  - the results of my students' first submission.
- [x] T002 `tests/unit/domain/test_spec006_exam_results.py` — FR-033
- [x] T003 `frontend/e2e/spec006-x2-templates.spec.ts`:
  - «Borrador» and «Ya presentado» badges;
  - «Duplicar»;
  - results per student with the option chosen.

## Phase 2 — Implementation

- [x] T004 Migration `_add_exam_selected_option`, applied on both engines. The answer stores the
  chosen option.
- [x] T005 Visibility: a template with no assignment is shown to no student, in both the template
  query and the pending query.
- [x] T006 Repository: `template_has_sessions`, `assign_template_to_groups`,
  `get_exam_template_responses`.
- [x] T007 Teacher routes:
  - `assigned` and `locked` on each template;
  - 409 on locked items;
  - `POST /exam-templates/{id}/duplicate`;
  - course check and atomic assignment;
  - results from the domain.
- [x] T008 Frontend `Exams.tsx`:
  - the badges;
  - «Duplicar»;
  - the template marked assigned after an assignment;
  - «Por estudiante» in the results.

## Phase 3 — Close

- [x] T009 Traceability: US3-AS1 … AS3 and FR-030 … FR-033 filled; X2 `closed`. Checks run:
  - the full suite on both engines;
  - Playwright;
  - black and flake8;
  - `db_sync_check.py` and `check_traceability.py`;
  - `pnpm run build`.
