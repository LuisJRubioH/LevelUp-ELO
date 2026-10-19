# Plan — spec 003, delivery L1: access

**Spec**: [spec.md](spec.md) § Deliveries, L1 (US1; FR-010, FR-011; N6) · **Branch**:
`003-learning-path-l1`, from `redesign` · **Date**: 2026-10-19 · **Status**: for the owner's approval

## Summary

Today the five path endpoints check only that the caller is signed in. Any student of any course
can open lessons, write progress and answers, read the summary and the map of `algebra_basica`.
The same holds for a teacher, whose progress would also be stored. The endpoints are:

- `GET /lessons/{course}/{node}`
- `POST …/events`
- `POST …/interactions`
- `GET /prealgebra-summary/{course}`
- the map's curriculum rows

L1 puts one access rule in front of all five:

- a student must be enrolled in the course (spec 001 FR-037's check);
- a teacher with a group in the course reads every node, with no progress, and writes nothing;
- anyone else is refused.

## Constitution Check (1.2.0)

| Principle | L1 |
|---|---|
| Security (VI) | A server-side refusal before any read or write; nothing stored on a refused call |
| Layers (III) | The rule is a function of the router layer over the existing `ensure_enrolled` and the teacher's groups; no domain change |
| Dual database (IV) | No schema change; the tests run on both engines (`client` fixture) |
| Simplicity (VII) | One dependency for all five endpoints instead of five checks |

## Design

- **`_path_access(repo, user, course_id) -> "student" | "preview"`**, in `api/routers/student.py`
  next to `_require_enrolment`:
  - **student:** `StudentService.ensure_enrolled`, the same call practice uses (spec 001 FR-037,
    FR-037a). Leaving the course closes the path; progress is kept (spec edge case).
  - **teacher:** allowed only when one of their groups has `course_id == course` (from
    `get_groups_by_teacher`); the result is `preview`.
  - **admin:** see N10.
  - **anyone else:** 403 «No estás inscrito en este curso.»
- **Writes:** `events` and `interactions` called in `preview` mode answer 403 «Vista previa: no se
  guarda progreso.» before any repository call.
- **Reads in `preview`:**
  - the lesson is returned with `state = "available"` and empty `progress`; the unlock and band
    rules are skipped (every node is available, FR-011);
  - the map returns every curriculum node as `available` and no rating rows;
  - the summary is refused: it summarises one student's progress, and the teacher's view of a
    student comes in L4.
- **The map:** `GET /map/{course}` also serves practice topics. L1 adds the same check to the whole
  endpoint, because practice already requires enrolment, so the map's rating rows are refused for
  outsiders too.
- **The summary (N6):** a response model `PathSummaryResponse` (course, completed, total, status,
  review), and the course must be one with a path (404 otherwise).
- **The frontend:** `Lesson.tsx` and `CourseMap.tsx` already show an error state for 403. A
  teacher's preview needs an entry point: a «Ver ruta» link in the teacher's group view, opening the
  same pages read-only (the API's `preview` flag hides the answer controls). The pages need only the
  read-only switch.

## Tests (written first; each fails on today's code)

| Test (both engines) | Proves |
|---|---|
| `tests/integration/test_spec003_l1_access.py::test_a_student_not_enrolled_is_refused_everywhere`: lesson, event, interaction, summary, map, each 403, and no progress or answer row afterwards | US1-AS1, FR-010, SC-001 |
| `…::test_an_enrolled_student_walks_the_path_as_today` | US1-AS2 |
| `…::test_a_teacher_of_the_course_previews_without_storing` (every node opens; events and answers 403; no rows) | US1-AS3, FR-011 |
| `…::test_a_teacher_without_a_group_in_the_course_is_refused` | US1-AS4, FR-011 |
| `…::test_the_summary_has_a_response_model_and_checks_the_course` | N6 |
| Delivery A pins (`test_map_matches_lesson_access.py`, `test_student.py` lesson tests) re-run with enrolled students | unchanged behaviour |

Some existing lesson tests may sign in a student not enrolled in `algebra_basica`. Each pin is
run against L1 first. Where one fails for that reason alone, it gets an `enroll(...)` line, the only
change allowed to a pin, and the PR lists every such edit.

## Owner decisions (open)

- **N10 — admins.** Recommended: an admin previews like a teacher of every course, read-only. The
  alternative is to refuse them.
