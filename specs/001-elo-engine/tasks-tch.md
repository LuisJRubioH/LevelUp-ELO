# Tasks — spec 001, delivery TCH (no enrolment without a teacher)

**Plan**: [plan-tch.md](plan-tch.md). FR-028v and FR-028w are `[CHANGE]`: today the catalogue
enrols any student with no group and the course list says nothing about it, so every test below
must fail on the unchanged code first (wrong status, missing group, missing field or screen text),
then pass with the implementation.

## Tests

- [ ] T001 The rule, no I/O: no group; a teacher not approved or not active; a group with no
  course; a group with the course; a group with another course (FR-028v) —
  `tests/unit/domain/test_spec001_catalogue.py::test_spec001_catalogue_enrolment_needs_the_groups_teacher`
- [ ] T002 Both engines, through the API: a student whose group has no course enrols with the
  group, keeps the same group, and a procedure in that course is in the teacher's queue (US11-AS1,
  FR-028v) — `tests/integration/test_spec001_enrolment_teacher.py`
- [ ] T003 Both engines: refused with «Pide a tu docente una invitación para este curso.» (403)
  and nothing enrolled for no group, a group with another course, a deactivated teacher and a
  teacher not approved; the group's own course enrols with the group (US11-AS2, FR-028v)
- [ ] T004 Both engines: a group named in the request is ignored; a course already enrolled through
  an invitation keeps that invitation's group (FR-028v, spec § Edge Cases) — the first rewrites
  `tests/integration/test_enrol_joins_no_group.py::test_catalogue_enrolment_ignores_a_group_id`
- [ ] T005 Both engines: `GET /api/student/courses` marks `enrollable` per course — true only for a
  catalogue course the rule accepts (FR-028w)
- [ ] T006 Screen — `frontend/e2e/spec001-enrolment-teacher.spec.ts` (mocked API): «Inscribirme»
  only where `enrollable`; «Con invitación de tu docente» and its button to the «Código» tab
  otherwise; a refused enrolment shows the server's message (US11-AS3, FR-028w)
- [ ] T007 Earlier tests moved to the rule, coverage kept: `tests/integration/test_spec001_catalogue.py`
  (the catalogue enrolment of US7-AS3 has a group), `tests/api/test_student.py` (catalogue
  enrolments of its fixtures)

## Implementation

- [ ] T008 `catalogue_enrolment_group` in `src/domain/entities.py`
- [ ] T009 `get_student_group(user_id)` in both repositories and `IStudentRepository` (R1);
  `python scripts/db_sync_check.py`
- [ ] T010 `StudentService.enroll_from_catalogue` (already enrolled → no write; the rule;
  `NoTeacherForCourse`) and `catalogue_enrolment_allowed`
- [ ] T011 `POST /enroll` refusal message; `CourseResponse.enrollable`; `EnrollRequest` docstring
- [ ] T012 `Courses.tsx`, `frontend/src/api/student.ts`, i18n `es`/`en`; `pnpm run build`
- [ ] T013 `scripts/verify_deployment.py` enrols only where `enrollable`; a local dress rehearsal
  (`migrate.py` → API with production settings → `verify_deployment.py`) passes

## Close

- [ ] T014 Traceability: FR-028v, FR-028w, US11-AS1 … AS3 filled; TCH `closed`;
  `python scripts/check_traceability.py --run`
