# Plan — spec 001, delivery TCH: no enrolment without a teacher

**Spec**: [spec.md](spec.md) § Deliveries, TCH (User Story 11; FR-028v, FR-028w) · **Branch**:
`001-tch`, from `redesign` · **Date**: 2026-10-21 · **Status**: decided by the owner on
2026-10-21; goes in before the production switch

## Summary

A course enrolled from the catalogue has no group (delivery INV). Spec 006 FR-050 sends a procedure
to the teacher whose group links the student to the item's course, so a procedure in a course other
than the group's own reaches no teacher. `main` shows every procedure of a group's student to its
teacher, so the switch would open the gap. The owner decided that no student enrols in a course
without a teacher (spec § Clarifications, Session 2026-10-21): the catalogue enrols only in a
course the teacher of the student's group reviews, and records the enrolment with that group.

## Constitution Check (1.2.0)

| Principle | TCH |
|---|---|
| Tests first (I) | every FR and US11 scenario gets a test that fails on today's code before the change (tasks-tch.md) |
| Layers (R2, III) | the rule — which group, if any, a catalogue enrolment is recorded with — is a pure function in `src/domain/entities.py`, next to the catalogue rule; the repositories return the student's group as a raw row; `StudentService` decides; HTTP and messages in `api/` |
| Dual database (R1, IV) | one new read method with the same signature and SQL shape on both engines; `db_sync_check.py`; behaviour proven on both engines |
| Additive migrations (R8) | no schema change: `enrollments.group_id` already exists |
| Ratings (R15) | none moves; the rule decides only who reviews a procedure |
| Production (VI) | no repair: the enrolments without a group that exist are kept (owner: production holds only demo accounts) |
| V1 frozen | V1 calls `enroll_user` directly, whose signature and behaviour stay; V1 is disconnected at the switch |

## Design

- **Domain** (`src/domain/entities.py`): `catalogue_enrolment_group(group, course_id) -> int |
  None`. `group` is the student's group as `{"group_id", "course_id", "teacher_ok"}`, or `None`
  for a student with no group. It returns the group's id when `teacher_ok` is true and the group
  has no course or has `course_id`; otherwise `None`. No I/O.
- **Repository** (both engines, in `IStudentRepository`): `get_student_group(user_id) -> dict |
  None` — the student's group (`users.group_id`) with its `course_id` and `teacher_ok` (its
  teacher has role `teacher`, `active = 1` and `approved = 1`, as the invitation's check in
  `redeem_group_invitation`), or `None` when the student has no group or it no longer exists. Raw
  row, no decision.
- **Service** (`StudentService`):
  - `enroll_from_catalogue(user_id, course_id)`: the catalogue check stays first (FR-028m,
    `PermissionError`); a course the student is already enrolled in returns without writing, so an
    enrolment made through an invitation keeps its group; then the domain rule; `None` raises
    `NoTeacherForCourse` (a `PermissionError`); otherwise `enroll_user(user_id, course_id,
    group_id=…)`. The group is the student's own, so `enroll_user`'s update of `users.group_id`
    writes the value already there.
  - `catalogue_enrolment_allowed(user_id) -> set[str]`: the catalogue courses the rule accepts,
    reading the student's group once.
- **API** (`api/routers/student.py`, `api/schemas/student.py`): `POST /enroll` answers 403
  «Pide a tu docente una invitación para este curso.» for `NoTeacherForCourse` and keeps «Ese curso
  no está en tu catálogo.» for a course outside the catalogue. `CourseResponse` gains `enrollable:
  bool` (default `False`) — true for a catalogue course the student may enrol in now (FR-028w).
  `EnrollRequest`'s docstring says a group sent is still ignored.
- **Screen** (`frontend/src/pages/Student/Courses.tsx`, `frontend/src/api/student.ts`, i18n `es`
  and `en`): in «Explorar», a course not enrolled shows «Matricularme» when `enrollable`, otherwise
  «Con invitación de tu docente» and a button that opens the «Código» tab; a refused enrolment
  shows the server's message (today the mutation has no `onError`).
- **Deployment check** (`scripts/verify_deployment.py`): the diagnostic step enrols only in a
  course the list marks `enrollable`; the lesson step enrols in `algebra_basica` only when
  `enrollable` and otherwise reports, as a warning, that the verification student needs it through
  their group or an invitation. Not in the spec's Code Scope; it follows the API.

## Who is affected

- Students whose group has no course: unchanged, except that the enrolment now carries the group
  (their teacher already reviewed every course, FR-050).
- Students whose group has a course: from the catalogue, only that course; any other through an
  invitation. The seeded test students (`_seed_test_students`) are in such groups.
- Students with no group — public registration (`PUBLIC_REGISTRATION_ENABLED`, roadmap § Account
  registration) and accounts whose group was deleted: only invitations.
- Teachers: a procedure in a course enrolled from the catalogue reaches the teacher of the group
  it was enrolled with; a student who moves later keeps that teacher for that course (spec 006 N7).

## Tests (written first)

| Test | Proves |
|---|---|
| `tests/unit/domain/test_spec001_catalogue.py::test_spec001_catalogue_enrolment_needs_the_groups_teacher` | FR-028v: the rule's cases, no I/O |
| `tests/integration/test_spec001_enrolment_teacher.py` (both engines, through the API) | US11-AS1, US11-AS2, FR-028v: enrolled with the group and the procedure in the teacher's queue; refusals change nothing; the group's own course; a group sent is ignored; already enrolled keeps its group |
| the same file: `…::test_spec001_the_course_list_says_which_courses_enrol` | FR-028w: `enrollable` per course |
| `frontend/e2e/spec001-enrolment-teacher.spec.ts` (mocked API) | US11-AS3, FR-028w: «Matricularme» only where `enrollable`, the invitation hint and its button, the refusal message |
| earlier tests moved, coverage kept: `tests/integration/test_enrol_joins_no_group.py`, `tests/integration/test_spec001_catalogue.py`, `tests/api/test_student.py` | FR-028m, delivery INV |

## Risks and rollout

- **No migration, no repair.** The enrolments without a group that exist stay; production holds
  only demo accounts (owner, 2026-10-21).
- **The demo and verification accounts** are in groups with a course, so from the catalogue they
  enrol only in that course. `verify_deployment.py` is adapted so the switch's checks do not fail
  for it.
- **Before the switch**: it enters `redesign` before PR #3 is marked ready. No new schema version,
  so the migration rehearsal launched on `redesign` stays valid (roadmap § What the production
  switch still needs, item 2: a new rehearsal only for a change of `SCHEMA_VERSION`).
