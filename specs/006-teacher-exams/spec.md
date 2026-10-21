# Feature Specification: Teacher Console & Exams

**Feature Branch**: `006-teacher-exams` (one branch per delivery once implementation starts)

**Created**: 2026-10-19

**Status**: Approved by the owner (2026-10-19), with N1 … N11 as recommended except N10's range
buttons, which get a use (FR-043). Written from the as-is survey
(`docs/sdd/teacher-exams-survey.md`, LuisJRubioH/LevelUp-ELO#43), re-verified on 2026-10-19 (its
§ 7). Delivery A pins what already holds; X1, X2, C1 and P1 are implemented. Delivery RV
(2026-10-21) fixes three findings of the 2026-10-20 review before the switch.

**Input**: Roadmap M6 (`docs/sdd/roadmap.md`): dashboard metrics, exports, exam mode, procedure
grading flow.

**Outcome served** (constitution VIII): a teacher sees, for their own students and courses, figures
the server computed once — the same numbers and ranks a student sees — and exams that measure what
the student knows on a first try, without changing any rating.

## Code Scope *(mandatory)*

- `api/routers/teacher.py` — dashboard, metrics, reports, exports, exam templates and assignments,
  procedure queue and grading (the grading's rating effect belongs to spec 001)
- `api/routers/student.py` — the exam endpoints (shared with specs 001, 003, 005)
- `api/schemas/teacher.py`, `api/schemas/student.py` — the exam and teacher bodies (shared)
- `src/application/services/teacher_service.py` (shared with spec 005)
- `src/domain/elo/console.py`; `src/application/services/rating_read_service.py` — the console's
  figures (the service is spec 001's; C1 and RV add `console_summary`)
- `src/infrastructure/persistence/sqlite_repository.py`,
  `src/infrastructure/persistence/postgres_repository.py` — exam storage, teacher queries,
  exports, the procedure queue (shared)
- `frontend/src/pages/Student/Exam.tsx`
- `frontend/src/pages/Teacher/Dashboard.tsx`, `frontend/src/pages/Teacher/Groups.tsx`,
  `frontend/src/pages/Teacher/Exams.tsx`, `frontend/src/pages/Teacher/Export.tsx`,
  `frontend/src/pages/Teacher/Procedures.tsx`
- `frontend/src/api/teacher.ts`

## Deliveries *(this spec is delivered in steps)*

Constitution 1.1.0, § Governance: `PENDING` is allowed only in rows of an open delivery; the pull
request that completes a delivery marks it closed and fills all its rows.

| Delivery | Content | State |
|---|---|---|
| **A** | As-is pins: what exams and the console already guarantee, each requirement tied to a test that exists today | closed |
| **X1** | Exam access and attempts: enrolled students only, one graded attempt per template, pending exams shown and dropped once submitted, server-side course name, a rate limit, stale sessions cleaned, a removed item no longer blocks a submission | closed |
| **X2** | Templates and results: private until assigned, locked once taken, assignment checks the course and commits all groups or none, results of the teacher's own students on their first attempt, per student, with the chosen option kept | closed |
| **C1** | The console from the server: one student set everywhere (screens, exports, counts), the group summary, ranking and «attention» list computed by the server with competition ranks, the dashboard's 7-day, 30-day and full-history views, teacher routes for teachers only, dead code removed | closed |
| **P1** | The procedures queue: follows the item's course, active non-test students only, no submission left without a teacher, the grade slider starts empty, the AI feedback shown, a stale AI score cleared on resubmission | closed |
| **RV** | Review fixes before the switch (owner, 2026-10-21): a student sees the exams of every group that links them to the course; the console ranks a group on its course and «Todos» on the courses that link each student to the teacher, and shows the rating it ranked on | planned |

## Clarifications

### Session 2026-10-15

- Q: Exam grace period (survey decision 11)? → A: keep 30 seconds (owner).

### Answered elsewhere

- Resubmitted procedures (survey decision 6): spec 001 block 7 — a regrade applies only the
  difference to the last contribution (spec 001 FR-024d), once per review round.

### Session 2026-10-19 (owner decisions on the spec)

- Q: N1 … N11? → A: approved as recommended, except the dashboard's range buttons (7d / 30d /
  Todo): they stay and work — the dashboard's activity figures over the last 7 days, the last 30
  days, or the whole history since the student registered (FR-043).

### Session 2026-10-21 (findings of the 2026-10-20 review; delivery RV)

- Q: Fix the three findings before or after the switch? → A: before the switch (owner).
- Q: What does the console rank by under «Todos los grupos», where the students' groups have
  different courses? → A: the mean of the ratings of the courses that link each student to the
  teacher; the overall rating when one of those links names no course, because that teacher
  reviews every course (owner: «Media de sus cursos contigo»; FR-041b).
- Q: Templates with no assignment were shown to every enrolled student on `main` and become drafts
  at the switch (FR-030). Turn them into assignments, or document and count them? → A: document
  them and count them before the switch (owner: «Documentar y contar»). Production holds only demo
  accounts (owner, 2026-10-21).
- The first finding needs no decision: the exam screens read the student's main group only, so a
  student who joined a second teacher's group lost the exams of their first group's course,
  against FR-040's links (FR-022a).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - What already holds keeps holding (Priority: P1) — A

**Why this priority**: the exam deadline, the windows, the exports and the teacher's access were
fixed in the last weeks; they stay fixed while the rest changes.

**Independent Test**: the existing API, integration and browser tests named in § Traceability.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** an exam started with a time limit, **When** the submission arrives up to
   30 seconds after it, **Then** it is graded; later, it is refused with 409 and the screen says
   why without retrying.
2. **US1-AS2** — **Given** an exam started or submitted, **When** the response arrives, **Then** it
   carries no correct option and no rating has moved.
3. **US1-AS3** — **Given** a teacher who is not the teacher of a student's groups, **When** they
   open that student's report, history or analysis, **Then** the answer is 404.
4. **US1-AS4** — **Given** typed text that looks like a formula or holds a control character,
   **When** the teacher exports, **Then** the workbook and the CSV keep it as text.

### User Story 2 - Exams only for my students, once (Priority: P1) — X1

**Why this priority**: today anyone with a token takes any course's exams any number of times and
sees which items were right after each try, so a result says little about what was learned.

**Independent Test**: students enrolled and not enrolled, a teacher and an admin call the exam
endpoints through the API.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** a student not enrolled in the course, or a user who is not a student,
   **When** they list, start or submit an exam of that course, **Then** the answer is 403 and no
   session is created.
2. **US2-AS2** — **Given** a template the student already submitted, **When** they start it again,
   **Then** the answer is 409 and the exam no longer appears among their pending exams.
3. **US2-AS3** — **Given** an item removed from the bank after the exam started, **When** the
   student submits, **Then** the remaining items are graded and the removed one is reported as not
   graded.
4. **US2-AS4** — **Given** a student enrolled in course X through their first group who then
   joined a second teacher's group for another course, so that the second group became their main
   group, **When** they list the exams of course X, their pending exams or start one, **Then** the
   exams assigned to their first group are there; once they join another group for course X, the
   first group's exams are no longer listed (N7; RV).

### User Story 3 - Results of my students, as they first answered (Priority: P2) — X2

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** a template taken by the teacher's students, by other teachers' students
   and retaken by some, **When** the teacher opens its results, **Then** they count only the
   teacher's students and each one's first submission, per student and per item, with the option
   each chose.
2. **US3-AS2** — **Given** a template that a student has started, **When** the teacher edits its
   items, **Then** the edit is refused with 409 naming the way out (duplicate the template).
3. **US3-AS3** — **Given** a template with no assignment, **When** a student of the course lists
   exams, **Then** it is not there.

### User Story 4 - The console shows the server's figures (Priority: P2) — C1

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** two students of a group with the same displayed rating and one pending,
   **When** the teacher opens the group ranking, **Then** the two share a place (1, 1, 3 …) and the
   pending student is listed last without a place, as on the student side.
2. **US4-AS2** — **Given** students in main groups, enrolment groups, inactive or test accounts,
   **When** the teacher opens the dashboard, the metrics, the group counts and each export sheet,
   **Then** every one of them lists the same students.
3. **US4-AS3** — **Given** an admin, **When** they call a teacher route, **Then** the answer is 403.
4. **US4-AS4** — **Given** students with attempts 3, 20 and 90 days ago, **When** the teacher
   picks 7 days, 30 days or «Todo» on the dashboard, **Then** the attempts, accuracy and activity
   shown count only that window (all of them for «Todo»), and the ratings and ranks stay the
   current ones.
5. **US4-AS5** — **Given** a group of course X whose students also have ratings in other
   courses, **When** the teacher opens that group's ranking, figures and «attention» list, **Then**
   they are computed on each student's course X rating, shown beside each place with the basis
   named; under «Todos», on the mean of the courses that link each student to the teacher (RV).

### User Story 5 - Every procedure reaches a teacher, graded with care (Priority: P2) — P1

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** a procedure for an item of a course, **When** a teacher with a group in
   that course opens the queue, **Then** it is there; an inactive or test student's procedure is
   not, and none is left without a teacher.
2. **US5-AS2** — **Given** a pending procedure with an AI score, **When** the teacher opens it,
   **Then** the grade slider starts empty and the AI score and feedback are shown beside it; after
   a resubmission the old AI score is gone.

### Edge Cases

- **A student moved to another group** keeps their first submissions; the former teacher keeps
  seeing them only for the course they shared (N7).
- **A template assigned to several groups, one of them of another course**: the whole assignment
  is refused; nothing is assigned (N5).
- **The grace period** applies to the server's deadline; the screen still counts down from the
  start's limit (US1-AS1).
- **Standard exams** (no template) stay unlimited in attempts: they are practice without rating
  (N3).
- **A template with no assignment**, shown to every enrolled student on `main`, is a draft from the
  switch on (FR-030): students see it again once the teacher assigns it. The precheck counts such
  templates before the switch (`docs/transfer.md` § 6; owner, 2026-10-21).
- **A group without a course** ranks a student linked to it by their main group on their overall
  rating (the teacher reviews every course, spec 001 FR-028d) and a student linked to it only by an
  enrolment in course X on X (FR-041a, N7).

## Requirements *(mandatory)*

### Functional Requirements

**What already holds (A)**

- **FR-001** [AS-IS]: When a student starts an exam, the system shall return its items and time
  limit without any correct option.
- **FR-002** [AS-IS]: If a submission does not name exactly the items started, then the system
  shall refuse it with 400.
- **FR-003** [AS-IS]: When a submission arrives up to 30 seconds after the session's deadline, the
  system shall grade it; if it arrives later, then the system shall refuse it with 409, and the
  screen shall show the reason without retrying.
- **FR-004** [AS-IS]: The system shall change no rating when an exam is submitted.
- **FR-005** [AS-IS]: If an exam is asked for with no course, then the system shall answer 422; for
  a course with no items, 404.
- **FR-006** [AS-IS]: When a teacher assigns a template, the system shall refuse an unreadable or
  reversed window, store it in UTC and return it with its zone, and refuse a template that is not
  the teacher's.
- **FR-007** [AS-IS]: The system shall let a teacher open the report, history and analysis only of
  students of their groups — main group or enrolment group — and answer 404 for anyone else.
- **FR-008** [AS-IS]: When a teacher exports, the system shall keep typed text as text in the
  workbook and the CSV, drop characters a workbook cannot hold, and mark the CSV as UTF-8.
- **FR-009** [AS-IS]: If a teacher screen cannot load its data, then the screen shall say so,
  never show the empty state.
- **FR-010** [AS-IS]: When the stored file of a procedure cannot be read from Storage, the system
  shall serve the copy kept in the row; a PDF shall be shown as a document.
- **FR-011** [AS-IS]: The system shall accept a rating-history limit from 1 to 200 only.
- **FR-012** [AS-IS]: The system shall let a teacher grade only pending procedures of their own
  students and answer 404 otherwise.

**Exam access and attempts (X1)**

- **FR-020** [CHANGE]: The system shall let only a student enrolled in the course list, start and
  submit its exams, and refuse anyone else with 403 before creating a session (N1).
- **FR-021** [CHANGE]: If a student starts a template they already submitted, then the system
  shall refuse it with 409; standard exams stay unlimited (N3).
- **FR-022** [CHANGE]: The system shall list to a student their pending exams — assigned, open and
  not yet submitted — on the exam screen (N3).
- **FR-022a** [CHANGE]: The system shall list to a student, and let them start, the exams of a
  course assigned to their main group or to the group of their enrolment in that course; an exam
  assigned to a group that no longer links them to the course is not listed (FR-040, N7; RV).
- **FR-023** [CHANGE]: The system shall store the course name from the course, not from the
  request; limit exam starts per account; and delete active sessions 24 hours after their
  deadline (N11).
- **FR-024** [CHANGE]: If an item of a started exam no longer exists, then the system shall grade
  the remaining items and report the removed one as not graded (N11).

**Templates and results (X2)**

- **FR-030** [CHANGE]: While a template has no assignment, the system shall show it to no student
  (N2).
- **FR-031** [CHANGE]: If a teacher edits the items of a template that a student has started, then
  the system shall refuse it with 409 and offer to duplicate the template (N5).
- **FR-032** [CHANGE]: When a teacher assigns a template to groups, the system shall refuse a group
  of another course and commit all groups or none (N5).
- **FR-033** [CHANGE]: The system shall compute a template's results over the teacher's own
  students and each one's first submission, per student and per item, and store the option chosen
  for each item (N4).

**The console from the server (C1)**

- **FR-040** [CHANGE]: The system shall build one student set for a teacher — active, non-test
  students of the teacher's groups, by main group or enrolment group — and use it for the
  dashboard, the metrics, the group counts and every export sheet, showing each student's data
  only for the courses of those groups (N6, N7).
- **FR-041** [CHANGE]: The system shall compute the group summary, the ranking with competition
  ranks and the «attention» list from `RatingReadService` (AGENTS.md R15), and the screens shall
  render them as given (N8).
- **FR-041a** [CHANGE]: The system shall compute a group's summary, ranking and «attention» list on
  the rating spec 001 FR-028d gives that group: its course's rating when the group has a course;
  for a group without a course, the FR-041b rating over the links through that group (N7; RV).
- **FR-041b** [CHANGE]: The system shall compute the summary, ranking and «attention» list of the
  whole set («Todos») on each student's mean of the ratings of the courses that link them to the
  teacher, or on their overall rating when one of those links names no course (owner, 2026-10-21;
  RV).
- **FR-041c** [CHANGE]: Each ranking entry shall carry the rating and rank label it was ranked on,
  and each student row of the dashboard those of «Todos»; the screens shall show them and name the
  basis, and the dashboard shall send no other rating of the student — not the overall rating,
  which counts courses of other teachers (FR-040, N7; RV).
- **FR-042** [CHANGE]: The system shall answer 403 to a user who is not a teacher on every teacher
  route, and the screens shall offer no control that does nothing (N10).
- **FR-043** [CHANGE]: When the teacher picks 7 days, 30 days or the whole history on the
  dashboard, the system shall compute each student's attempts and accuracy and the activity
  metrics over that window on the server; ratings and ranks stay the current ones (N10, owner
  2026-10-19).

**The procedures queue (P1)**

- **FR-050** [CHANGE]: The system shall show a pending procedure to the teachers of the groups
  enrolled in the item's course, only for active non-test students, so that no procedure is left
  without a teacher (N9).
- **FR-051** [CHANGE]: The grade slider shall start empty, with the AI score and the AI feedback
  shown beside it; a resubmission shall clear the AI score of the earlier round (N9).

### Key Entities

- **Exam template**: a teacher's set of items of one course, with a time limit; private until
  assigned; locked once started.
- **Assignment**: a template given to one of the teacher's groups, with an optional UTC window.
- **Exam session**: one student's start and submission; graded on the server; never moves a
  rating.
- **Teacher's student set**: the students the console, metrics and exports describe.
- **Basis**: the rating a set of the console is ranked on — a course's rating, or the mean of the
  courses that link each student to the teacher (FR-041a, FR-041b).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 exam sessions created by users who are not enrolled students of the course.
- **SC-002**: The same students in the dashboard, the metrics, the group counts and the four
  export sheets, for every teacher of the test data.
- **SC-003**: 0 ranks, means, thresholds or windowed counts computed in the browser (checked by reading the
  screens' code in review and by a test of the server's ranking).
- **SC-004**: 0 pending procedures without a teacher who can grade them.

## Assumptions

- Exams never move a rating (spec 001 FR-032, out of this spec).
- Group membership, roles and invitations belong to spec 004; this spec only uses its rule.
- A course enrolled from the catalogue has its group's teacher (spec 001 FR-028v, delivery TCH), so
  FR-050 finds a teacher for its procedures; enrolments without a group made before it are kept.
- The grade's rating effect belongs to spec 001 block 7.
- V1 is disconnected at the switch and retired (roadmap F-10); survey finding T12 is V1's only.
- At the switch production holds only demo accounts (owner, 2026-10-21), so the templates that
  become drafts (FR-030) are counted, not converted.

## New Decisions and Contradictions

| # | Point (survey) | Recommendation |
|---|---|---|
| N1 | Exams and enrolment (T3) | Only enrolled students, as practice (spec 001 FR-037); 403 for anyone else, teachers and admins included. |
| N2 | Publishing a template (T4) | Private until assigned: a template with no assignment is a draft. |
| N3 | Attempts (T5) | One graded attempt per template; standard exams unlimited. After submitting, the score and which items were right, as today. Pending exams listed on the exam screen and dropped once submitted. |
| N4 | Results (T6) | The teacher's own students, first submission only; per student and per item; the chosen option stored. |
| N5 | Editing a template already taken (T7) | Lock its items once any student has started it; the teacher duplicates it to change it. Assignment checks the course and commits all groups or none. |
| N6 | The teacher's student set (T13, T14) | One set everywhere: active, non-test students of the teacher's groups, by main or enrolment group. |
| N7 | After a student moves (T13) | The former teacher keeps the student only while an enrolment through one of their groups remains, and sees only that course's data. |
| N8 | Ratings in the console (T17) | From the server: group summary, competition ranking and «attention» list (R15); the browser renders them. Test students excluded from rankings. |
| N9 | The procedures queue and the slider (T15, T16) | Follow the item's course; active non-test students only; the slider starts empty; show the AI feedback; clear the AI score on resubmission. |
| N10 | Admins on teacher routes and dead controls (T20) | Teacher routes for teachers only (admins use the admin console); remove the discarded query and the unused client calls. **Owner (2026-10-19): the range buttons stay and work** — 7 days, 30 days, whole history (FR-043). |
| N11 | Exam smells (T8) | Course name from the server; a per-account limit on exam starts; delete active sessions 24 h after their deadline; a removed item is reported, not a 409 forever. |
| N12 | Review of 2026-10-20 (delivery RV) | **Owner (2026-10-21): fixed before the switch.** A student's exams follow every group that links them to the course (FR-022a). A group ranks on its course; «Todos» on the mean of each student's courses with the teacher (FR-041a … c). Templates without an assignment: documented and counted, not converted. |

**For spec 001 (not decided here):** survey T10 — grading a procedure whose item no longer exists
records 0 applied (spec 001 FR-024f) but marks the submission `elo_applied = 1` with the computed
delta. Decided by the owner (2026-10-19), after free exercise ids were found to look the same as
removed items: keep grading every procedure and record what was applied, 0 — done as
spec 001 FR-024m (delivery PM). The earlier approval of a 409 was withdrawn.

## Out of Scope *(mandatory)*

- The rating effect of a grade, of exams and of PvP — spec 001 (block 7 for procedures).
- Group membership, roles, invitations and the student-route role boundary in general — spec 004.
- AI providers, keys, KatIA and the teacher's AI analysis — spec 005.
- Storage, stored images and the database mechanics — spec 002.
- V1 beyond keeping it working until it is retired (roadmap F-10).

## Traceability *(mandatory)*

Rows of delivery A cite tests that exist today; the rest are filled by the pull request that
closes their delivery.

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| US1-AS1 | A | `tests/integration/test_exam_submit_deadline.py::test_a_submission_just_after_the_limit_is_graded`<br>`tests/integration/test_exam_submit_deadline.py::test_a_submission_long_after_the_limit_is_refused`<br>`frontend/e2e/exam-deadline.spec.ts › un rechazo del servidor no se reintenta y muestra su motivo` |
| US1-AS2 | A | `tests/api/test_spec001_answer_pins.py::test_spec001_no_response_carries_the_correct_option`<br>`tests/api/test_spec001_answer_pins.py::test_spec001_exam_submission_changes_no_rating` |
| US1-AS3 | A | `tests/api/test_teacher_resource_access.py::test_student_routes_require_current_teacher_relationship` |
| US1-AS4 | A | `tests/integration/test_teacher_export_cells.py::test_the_workbook_keeps_typed_text_as_text`<br>`tests/integration/test_teacher_export_cells.py::test_the_csv_neutralises_formulas_and_declares_utf8` |
| US2-AS1 | X1 | `tests/integration/test_spec006_x1_exams.py::test_only_enrolled_students_reach_exams` |
| US2-AS2 | X1 | `tests/integration/test_spec006_x1_exams.py::test_a_template_is_graded_once`<br>`tests/integration/test_spec006_x1_exams.py::test_pending_drops_a_submitted_template` |
| US2-AS3 | X1 | `tests/integration/test_spec006_x1_exams.py::test_a_removed_item_is_reported_not_blocking`<br>`frontend/e2e/spec006-x1-pending.spec.ts › una pregunta retirada del banco se muestra como no calificada` |
| US2-AS4 | RV | PENDING |
| US3-AS1 | X2 | `tests/integration/test_spec006_x2_templates.py::test_results_count_my_students_first_submission`<br>`frontend/e2e/spec006-x2-templates.spec.ts › los resultados muestran a cada estudiante con la opción que eligió` |
| US3-AS2 | X2 | `tests/integration/test_spec006_x2_templates.py::test_a_started_template_cannot_change_its_items` |
| US3-AS3 | X2 | `tests/integration/test_spec006_x2_templates.py::test_an_unassigned_template_is_a_draft` |
| US4-AS1 | C1 | `tests/integration/test_spec006_c1_console.py::test_the_summary_comes_from_the_server`<br>`tests/integration/test_spec006_c1_console.py::test_the_group_ranking_leaves_out_test_students`<br>`frontend/e2e/spec006-c1-console.spec.ts › el ranking, el promedio y «atención» son los del servidor (US4-AS1, FR-041)` |
| US4-AS2 | C1 | `tests/integration/test_spec006_c1_console.py::test_every_place_lists_the_same_students` |
| US4-AS3 | C1 | `tests/integration/test_spec006_c1_console.py::test_an_admin_gets_403_on_teacher_routes` |
| US4-AS4 | C1 | `tests/integration/test_spec006_c1_console.py::test_the_dashboard_counts_the_chosen_window`<br>`frontend/e2e/spec006-c1-console.spec.ts › 7d, 30d y Todo piden esa ventana al servidor (US4-AS4, FR-043)` |
| US4-AS5 | RV | PENDING |
| US5-AS1 | P1 | `tests/integration/test_spec006_p1_queue.py::test_the_queue_follows_the_items_course`<br>`tests/integration/test_spec006_p1_queue.py::test_inactive_and_test_students_are_not_queued` |
| US5-AS2 | P1 | `tests/integration/test_spec006_p1_queue.py::test_a_resubmission_clears_the_ai_score`<br>`frontend/e2e/spec006-p1-grade.spec.ts › la nota empieza vacía y la de la IA se muestra al lado, con su retroalimentación (US5-AS2, FR-051)` |
| FR-001 | A | `tests/api/test_student.py::TestExamMode::test_exam_start`<br>`tests/api/test_spec001_answer_pins.py::test_spec001_no_response_carries_the_correct_option` |
| FR-002 | A | `tests/api/test_student.py::TestExamMode::test_exam_submit_empty` |
| FR-003 | A | `tests/integration/test_exam_submit_deadline.py::test_a_submission_just_after_the_limit_is_graded`<br>`tests/integration/test_exam_submit_deadline.py::test_a_submission_long_after_the_limit_is_refused`<br>`frontend/e2e/exam-deadline.spec.ts › se envía al vencer el tiempo aunque el navegador haya frenado el temporizador`<br>`frontend/e2e/exam-deadline.spec.ts › un rechazo del servidor no se reintenta y muestra su motivo` |
| FR-004 | A | `tests/api/test_spec001_answer_pins.py::test_spec001_exam_submission_changes_no_rating` |
| FR-005 | A | `tests/integration/test_request_bounds.py::test_an_exam_needs_a_course`<br>`tests/integration/test_spec006_x1_exams.py::test_a_course_without_items_is_404` |
| FR-006 | A | `tests/integration/test_exam_assignment_window.py::test_an_invalid_window_is_refused`<br>`tests/integration/test_exam_assignment_window.py::test_a_window_is_read_back_in_utc`<br>`tests/integration/test_exam_assignment_window.py::test_a_window_open_now_shows_the_exam_to_the_group`<br>`tests/api/test_teacher_resource_access.py::test_assignment_must_belong_to_authorized_template` |
| FR-007 | A | `tests/api/test_teacher_resource_access.py::test_student_routes_require_current_teacher_relationship`<br>`tests/integration/test_teacher_student_scope.py::test_a_student_who_joined_a_second_group_stays_open_to_the_first_teacher` |
| FR-008 | A | `tests/integration/test_teacher_export_cells.py::test_the_workbook_keeps_typed_text_as_text`<br>`tests/integration/test_teacher_export_cells.py::test_the_csv_neutralises_formulas_and_declares_utf8` |
| FR-009 | A | `frontend/e2e/teacher-load-errors.spec.ts › procedimientos: un error no se muestra como «¡Al día!»`<br>`frontend/e2e/teacher-load-errors.spec.ts › grupos: un error no se muestra como «0 grupos»`<br>`frontend/e2e/teacher-load-errors.spec.ts › panel: si las métricas no cargan, la pestaña lo dice` |
| FR-010 | A | `tests/integration/test_teacher_image_fallback.py::test_image_falls_back_to_the_row_when_storage_fails`<br>`frontend/e2e/teacher-procedure-view.spec.ts › un PDF se muestra como documento, no como imagen rota` |
| FR-011 | A | `tests/integration/test_request_bounds.py::test_the_rating_history_limit_is_bounded` |
| FR-012 | A | `tests/api/test_procedure_grading.py::test_teacher_can_grade_own_pending_submission`<br>`tests/api/test_procedure_grading.py::test_other_teacher_cannot_grade_or_view_submission` |
| FR-020 | X1 | `tests/integration/test_spec006_x1_exams.py::test_only_enrolled_students_reach_exams`<br>`tests/integration/test_spec006_x1_exams.py::test_a_student_no_longer_enrolled_cannot_submit`<br>`tests/integration/test_spec006_x1_exams.py::test_an_empty_course_is_refused_when_listing`<br>`tests/api/test_student.py::TestExamMode::test_exam_start_nonexistent_course` |
| FR-021 | X1 | `tests/integration/test_spec006_x1_exams.py::test_a_template_is_graded_once` |
| FR-022 | X1 | `tests/integration/test_spec006_x1_exams.py::test_pending_drops_a_submitted_template`<br>`frontend/e2e/spec006-x1-pending.spec.ts › lista los exámenes asignados pendientes y prepara el elegido` |
| FR-022a | RV | PENDING |
| FR-023 | X1 | `tests/integration/test_spec006_x1_exams.py::test_the_course_name_comes_from_the_course`<br>`tests/integration/test_spec006_x1_exams.py::test_exam_starts_are_limited`<br>`tests/integration/test_spec006_x1_exams.py::test_stale_sessions_are_deleted` |
| FR-024 | X1 | `tests/integration/test_spec006_x1_exams.py::test_a_removed_item_is_reported_not_blocking`<br>`frontend/e2e/spec006-x1-pending.spec.ts › una pregunta retirada del banco se muestra como no calificada` |
| FR-030 | X2 | `tests/integration/test_spec006_x2_templates.py::test_an_unassigned_template_is_a_draft`<br>`frontend/e2e/spec006-x2-templates.spec.ts › un examen sin asignar es borrador y uno ya presentado se duplica para cambiarlo` |
| FR-031 | X2 | `tests/integration/test_spec006_x2_templates.py::test_a_started_template_cannot_change_its_items`<br>`frontend/e2e/spec006-x2-templates.spec.ts › un examen sin asignar es borrador y uno ya presentado se duplica para cambiarlo` |
| FR-032 | X2 | `tests/integration/test_spec006_x2_templates.py::test_an_assignment_is_one_course_and_all_or_nothing` |
| FR-033 | X2 | `tests/integration/test_spec006_x2_templates.py::test_results_count_my_students_first_submission`<br>`tests/unit/domain/test_spec006_exam_results.py::test_only_my_students_first_submission_count`<br>`tests/unit/domain/test_spec006_exam_results.py::test_each_student_keeps_the_option_chosen`<br>`tests/unit/domain/test_spec006_exam_results.py::test_per_item_counts_the_wrong_options`<br>`tests/unit/domain/test_spec006_exam_results.py::test_per_topic_and_the_topic_to_reinforce`<br>`tests/unit/domain/test_spec006_exam_results.py::test_no_submission_is_an_empty_result` |
| FR-040 | C1 | `tests/integration/test_spec006_c1_console.py::test_every_place_lists_the_same_students`<br>`tests/integration/test_spec006_c1_console.py::test_a_moved_student_shows_only_the_shared_course` |
| FR-041 | C1 | `tests/integration/test_spec006_c1_console.py::test_the_summary_comes_from_the_server`<br>`tests/integration/test_spec006_c1_console.py::test_the_group_ranking_leaves_out_test_students`<br>`tests/unit/domain/test_spec006_console.py::test_ranks_are_competition_ranks_with_pending_last`<br>`tests/unit/domain/test_spec006_console.py::test_mean_accuracy_and_attempts`<br>`tests/unit/domain/test_spec006_console.py::test_attention_needs_a_low_rating_or_low_accuracy_with_attempts`<br>`tests/unit/domain/test_spec006_console.py::test_histogram_counts_rated_students`<br>`tests/unit/domain/test_spec006_console.py::test_each_group_has_its_own_figures`<br>`tests/unit/domain/test_spec006_console.py::test_no_students_is_an_empty_summary`<br>`frontend/e2e/spec006-c1-console.spec.ts › el ranking, el promedio y «atención» son los del servidor (US4-AS1, FR-041)` |
| FR-041a | RV | PENDING |
| FR-041b | RV | PENDING |
| FR-041c | RV | PENDING |
| FR-042 | C1 | `tests/integration/test_spec006_c1_console.py::test_an_admin_gets_403_on_teacher_routes` |
| FR-043 | C1 | `tests/integration/test_spec006_c1_console.py::test_the_dashboard_counts_the_chosen_window`<br>`frontend/e2e/spec006-c1-console.spec.ts › 7d, 30d y Todo piden esa ventana al servidor (US4-AS4, FR-043)` |
| FR-050 | P1 | `tests/integration/test_spec006_p1_queue.py::test_the_queue_follows_the_items_course`<br>`tests/integration/test_spec006_p1_queue.py::test_inactive_and_test_students_are_not_queued` |
| FR-051 | P1 | `tests/integration/test_spec006_p1_queue.py::test_a_resubmission_clears_the_ai_score`<br>`frontend/e2e/spec006-p1-grade.spec.ts › la nota empieza vacía y la de la IA se muestra al lado, con su retroalimentación (US5-AS2, FR-051)` |
