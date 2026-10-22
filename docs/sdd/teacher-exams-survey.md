# Teacher console & exams — as-is survey (spec 006 input)

Read-only survey of `redesign @ 1d6fcf6`, 2026-10-10. Input for `specs/006-teacher-exams/spec.md`
(roadmap M6: dashboard metrics, exports, exam mode, procedure grading flow). Under the roadmap's
lean scope, spec 006 is written the first time a feature touches the area. Several findings below
are fixed in their own PRs. The rest wait for that spec or for an owner decision.

Each finding cites code at that commit (`S` = `src/infrastructure/persistence/sqlite_repository.py`,
`P` = `src/infrastructure/persistence/postgres_repository.py`, `stu` = `api/routers/student.py`,
`tch` = `api/routers/teacher.py`, `FE/` = `frontend/src/`).

How each finding was checked:
- **Verified**: read in the code.
- **Reproduced**: run against a throwaway local API (SQLite, or through the test client) or a
  local PostgreSQL 16.
- **Inferred**: reasoned from the code, not run.

Nothing here was run against production. Security-sensitive details are shared with the owner
directly, not in this repository. Rating arithmetic and which writer moves which rating belong to
spec 001. Group membership and roles belong to spec 004 (see `docs/sdd/identity-survey.md`).

## 1. Where things live

| Concern | File |
|---|---|
| Student exam API | `stu:707-961` (templates, pending, start, submit, history) |
| Teacher exam API | `tch:416-639` (templates, assignments, results, catalogue) |
| Exam storage | `create_active_exam_session` P:4998 S:4104 · `complete_active_exam_session` P:5048 S:4144 · templates P:5247-5392 S:4531-4672 · assignments P:5396-5483 S:4676-4747 · visibility P:5485-5580 S:4749-4830 · results P:5143 S:4411 |
| Exam screens | `FE/pages/Student/Exam.tsx`, `FE/pages/Teacher/Exams.tsx` |
| Dashboard and metrics | `tch:75-90, 327-330` · `get_teacher_dashboard_stats` P:2824 · `get_teacher_metrics` P:2910 · `FE/pages/Teacher/Dashboard.tsx` |
| Student report | `tch:277-344` · `TeacherService.get_student_dashboard` (`src/application/services/teacher_service.py:50-76`) |
| Exports | `tch:350-413` · `export_teacher_student_data` P:3038 · enrolments P:3154 · procedures P:3192 · KatIA P:2003 · `FE/pages/Teacher/Export.tsx` |
| Procedure grading | `tch:152-271` · `get_pending_submissions_for_teacher` P:4557 S:3886 · `validate_procedure_submission` P:4607 S:3928 · `save_procedure_submission` P:4313 S:3676 · `FE/pages/Teacher/Procedures.tsx` |
| Groups screen | `FE/pages/Teacher/Groups.tsx` |

## 2. Actual behaviour

**Exam mode (student).**
- **Starting an exam:** `POST /exam/start` builds an exam in one of two ways:
  - from a template the student can see;
  - or a "standard" exam of 1–30 items from the course bank, in difficulty bands of 30/40/30.

  It stores an `active_exam_sessions` row (items, deadline) and returns the items without
  `correct_option`.
- **Submitting:** `POST /exam/submit` must name exactly the started items, in order. It grades
  them against `correct_option` and stores `exam_sessions` and `exam_responses` in one transaction.
  - Each result says, per item, whether it was correct.
  - A replayed submission returns the stored result.
  - A late one answers 409. #39 adds a 30-second grace.
- **No rating effect:** exams never move a rating. `global_elo_after` is a read-only snapshot
  (spec 001).
- **Resume:** client-only. The draft lives in localStorage (`levelup-exam-draft`).

**Exam templates and assignments (teacher).**
- **Templates:** a teacher creates templates per course: a title, 5–180 minutes, and 1–60 items
  that must exist in that course's bank. Edits change the items in place. Archiving is a soft
  delete, and nothing restores an archived template.
- **Assignment:** a template is assigned to the teacher's own groups, with an optional window.
  #41 validates the window and stores it in UTC.
- **Visibility:** a template with **no** assignment is visible to every student of the course. One
  with assignments is visible to the students whose main group (`users.group_id`) has an open
  window.
- **Results:** aggregates only, over every session of the template:
  - sessions, students and average score;
  - accuracy per question and per topic.

  There are no per-student results.

**Dashboard, report and metrics.**
- **Dashboard:** lists the teacher's students as the union of main group and enrolment group;
  active, non-test students. For each it shows the server's `display_rating` and `rank_label`.
- **Report:** a student's report, rating history and KatIA history open for the same students
  after #36.
- **Metrics:** cover all of those students' attempts in every course.
- **Computed in the browser:** the group mean, the histogram and the ranking order.

**Exports.**
- **CSV:** «Intentos».
- **XLSX:** four sheets, «Intentos», «Matrículas», «Procedimientos» and «KatIA». Each sheet uses its
  own student set.
- **Raw log values:** no current rating is exported, only per-attempt log values (`elo_after`,
  `attempt_rd`, `prob_failure`, `expected_score`). So R15 holds.

**Procedure grading.**
- **The queue:** pending submissions of students whose main group belongs to the teacher.
- **Grading:** 0–100, checked three times: by the schema, by the domain and by the slider.
- **What a grade writes:** `validate_procedure_submission` applies `(grade − 50) × 0.2` to the
  item's (course, topic) rating, sets `elo_applied = 1`, and closes the submission. A second grade
  of the same pending cycle answers 404.
- **AI score:** advisory. It is shown, and it starts the grade slider.

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| T1 | **Bug** | **A submission at the time limit was lost.** The countdown counted timer ticks and started when the start response arrived. A background tab slows timers, and the automatic submission always arrived after the server's deadline: 409, retried three times, then a generic error, with the answers never graded. | `FE/pages/Student/Exam.tsx:511-646`; `stu:856` | **Reproduced** (late by 5 s and 20 s: 409 on both engines). Fixed in #39 |
| T2 | **Bug** | **Assignment windows are not checked.** An unreadable date answers 500 on PostgreSQL and is stored as written on SQLite. A close before the open is accepted. SQLite compares ISO text with `datetime('now')`, so a window opening today stays hidden until UTC midnight. PostgreSQL returns a time with no zone, which the teacher's browser shifts by their offset. | `api/schemas/teacher.py:143-154`; P:5476-5478; S:4766-4767 | **Reproduced**. Fixed in #41 |
| T3 | **Access** | **Exams do not check enrolment.** `/exam/start` and `/exam/templates` serve any course; F-4 left exams out on purpose (spec 001 out of scope). An empty `course_id` builds a standard exam from the whole bank. | `stu:797-840, 721`; `api/schemas/student.py:159`; spec 001 § Out of Scope | Verified. The empty `course_id` is a one-line fix; enrolment is decision 1 |
| T4 | **Publication** | **A template with no assignment is open to the whole course.** That includes a template created a minute ago, or one whose last assignment was removed. There is no draft state. | P:5514-5516; S:4771 | Verified |
| T5 | **Attempts** | **No limit on attempts.** A template, or a standard exam, can be started and submitted any number of times, and each result shows which items were right. `/exam/pending` does not drop templates already submitted. Students never see it either: its only consumer is the shared `Layout`, which only `/admin` uses. | `stu:797-872, 921-928`; P:5546-5565; `FE/pages/Layout.tsx:134-155` vs `FE/App.tsx:131-137` | Verified |
| T6 | **Results** | Template results count every session: other teachers' students (for an open template), retakes, and non-students (`/student/*` has no role check). There are no per-student results, and `exam_responses` keeps no selected option, so wrong answers cannot be analysed. | P:5149-5194; P:1093-1103 | Verified |
| T7 | **Templates** | Editing a template already taken changes its items with no version, so its results mix item sets. Group and template courses are not compared on assignment. Assigning to several groups commits each one separately, so a failure leaves a partial result. | `tch:477-507, 559-574` | Verified |
| T8 | **Smell** | `course_name` comes from the client and is stored unchecked; `time_taken` is accepted and discarded. An item removed between start and submit makes the session unsubmittable (409 forever). `active_exam_sessions` rows are never cleaned up, and `/exam/start` has no rate limit. | `stu:911-913, 948`; `api/schemas/student.py:204-218` | Verified |
| T9 | **Rating (R15)** | **Grading a resubmitted procedure adds the delta again.** A resubmission of the same item resets the graded row to pending. It keeps `elo_applied = 1` and the old delta, and grading checks only the status. Each resubmit-and-grade cycle moves the rating again: 1010 → 1020 for two grades of 100. Spec 001 says a grade moves the rating "exactly once" (US4, FR-022) without saying what a resubmission is. | P:4376-4399 S:3707-3722; P:4636-4646 S:3969-3979 | **Reproduced** on SQLite and PostgreSQL 16. Decision 6 |
| T10 | **Bug** | **`elo_applied = 1` with no rating move.** If the item row is missing, grading sets `elo_applied = 1` and reports a delta, but no rating moves. | P:4655-4669; S:3986-4001 | Code verified |
| T11 | **Exports** | **Exports broke on typed text.** A control character in any KatIA message made the XLSX answer 500. Text starting like a formula was written as one. The CSV had no BOM, and the export page described columns that do not exist. | `tch:350-413`; `FE/pages/Teacher/Export.tsx:16-22` | **Reproduced**. Fixed in #40 |
| T12 | **Exports (V1)** | `export_teacher_*_data(group_id=…)` builds SQL that refers to an alias that does not exist (`g2`); only V1 passes a group. | P:3051, 3077; S:2601, 2627 | Code verified. V1 is frozen and disconnected at the switch |
| T13 | **Scope** | **What a teacher sees of a student is not limited to the teacher's course or group.** This covers all attempts, KatIA chats and course ratings, and every enrolment. After an admin move or a second invitation, the old enrolment group keeps a student on the former teacher's dashboard, metrics and exports. `group_name` can name another teacher's group. | P:2836-2861, 3069-3114; `teacher_service.py:57-76` | Verified. Decision 7, with spec 004 decision 3 |
| T14 | **Consistency** | **Each place builds the student set its own way.** The XLSX sheets differ: «Matrículas» uses enrolment groups with no role filter, «Procedimientos» uses main groups, and «KatIA» has no active filter. A group's `student_count` counts main groups only. Group ranking participants include test students. | P:3154-3229, 2003-2033, 2574-2576, 2277-2286 | Verified |
| T15 | **Procedures** | **The queue mixes students and loads every image.** It has no active, test or role filter. It loads every stored image (BYTEA) on each list, 30-second poll, image request and grade. It follows the main group, not the item's course. A pending submission whose student has no group can never be graded. | P:4557-4604; S:3886-3926; `tch:225-234` | Verified |
| T16 | **Grading UX** | The AI score is the slider's starting grade, and stays stale after a resubmission. `ai_feedback` is never shown. A PDF is drawn in an `<img>` and shows broken. LaTeX in the item is not rendered. | `FE/pages/Teacher/Procedures.tsx:39, 45-52, 85`; `api/schemas/teacher.py:69-78` | Verified |
| T17 | **R15** | **The browser computes ratings.** The teacher console works out a group mean, a histogram, the ranking order (positions by array index: ties get different places, and pending students can reach the podium) and an «attention» threshold of 1100. R15 says every ranking comes from `RatingReadService`, and the student ranking uses competition ranks. | `FE/pages/Teacher/Dashboard.tsx:23-31, 180-270`; `FE/pages/Teacher/Groups.tsx:52-63` | Verified. Decision 8 |
| T18 | **Bug** | **Failed reads show as empty.** In the procedures queue, groups and metrics, a failed request showed the empty state: «¡Al día!», «0 grupos», «Sin datos». A failed invitation code did nothing visible. | `FE/pages/Teacher/Procedures.tsx:194-240`; `Groups.tsx:442-488`; `Dashboard.tsx:262` | **Reproduced** (Playwright). Fixed in #42 |
| T19 | **Bug** | `/student/{id}/elo-history?limit=` takes any integer: a negative one is a 500 on PostgreSQL and returns everything on SQLite. | `tch:286`; P:2131; S:1797 | Code verified |
| T20 | **Dead code** | **Built but not used.** The report, rating-history and KatIA-history endpoints are never called by the screens. The 7d/30d/Todo range buttons do nothing. The dashboard discards one query's result (`get_students_by_teacher`). Two current courses with the same topic name overwrite each other in the AI input. An admin passes the teacher role check but sees nothing, because every scope uses the caller's id. | `FE/api/teacher.ts:161-170`; `Dashboard.tsx:482, 540-546`; `tch:89`; `teacher_service.py:170-177` | Verified |
| T21 | **Fixed elsewhere** | The AI analysis without a key: #31. The image when Storage fails: #18 (F-8). Enrolled-only students' report gave 404: #36. | — | — |

## 4. Existing evidence

- **Exam API:**
  - `tests/api/test_student.py::TestExamMode` (start, fields, unknown course, submit, empty answers,
    auth);
  - `tests/api/test_spec001_answer_pins.py` (no `correct_option`; exams move no rating);
  - `tests/api/test_spec001_api.py` (`global_elo_after` equals the overall rating);
  - `tests/integration/test_postgres_production_guards.py` (template window, duplicates, replay,
    one submitted row, cross-teacher assignment delete);
  - `tests/integration/test_spec001_course_topic_store.py` (T078 snapshot);
  - new: `test_exam_submit_deadline.py` (#39), `test_exam_assignment_window.py` (#41).
- **Teacher API:**
  - `tests/api/test_teacher.py`;
  - `tests/api/test_teacher_resource_access.py` (ownership, 404s);
  - `tests/api/test_procedure_grading.py` (deltas, regrade 404, foreign teacher, race);
  - `tests/integration/test_spec001_repository_pins.py` and `test_elo_single_source.py` (delta
    applied once per pending cycle);
  - new: `test_teacher_student_scope.py` (#36), `test_teacher_export_cells.py` (#40).
- **Browser:**
  - `frontend/e2e/spec001-ratings.spec.ts` (dashboard renders the server's rating and label);
  - `protected-routes.spec.ts`;
  - new: `exam-deadline.spec.ts` (#39), `teacher-load-errors.spec.ts` (#42).
- **Not covered:**
  - template create, patch and archive validation;
  - `/exam/templates` and `/exam/pending`;
  - results scope;
  - resubmit-then-regrade (T9);
  - the item-missing grade (T10);
  - export scope and per-sheet sets;
  - the procedures queue's filters;
  - the browser's ranking (T17);
  - no e2e for the Exams, Groups, Procedures or Export pages beyond #42.

## 5. Decisions for the owner (input for `/speckit-clarify`)

None blocks the transfer (PR #3).

1. **Exams and enrolment (T3).** Should exams require enrolment in the course, like practice
   (F-4)?
2. **Publishing a template (T4).** Should a template stay private until it is assigned (a draft
   state), or remain open to the whole course when it has no assignment, as today?
3. **Attempts (T5).** Allow unlimited attempts, one per template, or a set number? What does a
   student see after submitting: the score only, or which items were right? Should pending
   exams be shown to students, and should they drop out once submitted?
4. **Results (T6).** Count only the teacher's own students, the first attempt, or every attempt?
   Add per-student results, and store the chosen option for each item?
5. **Editing a template already taken (T7).** Lock it, version it, or allow edits as today?
6. **Resubmitted procedures (T9).** When a student resubmits after a grade:
   - refuse the resubmission;
   - re-grade it and replace the earlier delta (apply only the difference);
   - re-grade it and add a new delta (today)?

   This needs a spec 001 amendment whichever is chosen.
7. **What a teacher sees of a student (T13, T14).** Should it be limited to the teacher's courses
   and groups, and what happens to the old teacher's view when a student moves?
8. **Ratings in the console (T17).** Should the server return the group summary, ranking and
   «attention» list (R15), with competition ranks as on the student side?
9. **The procedures queue (T15).** Should it follow the item's course or the student's group? What
   happens to inactive or test students, and to a submission whose student has no group?
10. **AI score as the starting grade (T16).** Keep it, or start the slider empty?
11. **Exam grace period (#39).** 30 seconds was my choice. Keep it or change it? **Answered
    (owner, 2026-10-15): keep 30 seconds.**

## 6. Proposed scope for spec 006 (draft)

- **In:**
  - the teacher dashboard, metrics and student report: what is shown, and for which students
    (with spec 004's membership rule);
  - exports: contents, per-sheet sets and cell safety;
  - the procedure grading flow (queue, image, grade, notification), apart from the rating it
    applies;
  - exam templates, assignments and their windows;
  - exam sessions: start, deadline, submit, grading, retries and resume;
  - exam results.
- **Out:**
  - the rating effect of a grade and of exams (spec 001; T9's rule is an amendment there);
  - group membership and roles (spec 004);
  - AI providers and keys (spec 005);
  - Storage and BYTEA mechanics (spec 002);
  - V1 beyond keeping it working.

## 7. Re-verified on 2026-10-19 (`redesign` after spec 001 block 7, spec 004 E1/E2/E6, spec 003)

Every finding was checked again on the current code before spec 006 was written. Numbers are
current line numbers.

| # | Now | What changed or still holds |
|---|---|---|
| T1 | Fixed (#39) | 30 s grace on the server (`stu:810-812`); the client counts from the clock |
| T2 | Fixed (#41) | Windows validated, stored and returned in UTC |
| T3 | Partly | An empty `course_id` on `/exam/start` is a 422. Still no enrolment or role check on `/exam/start`, `/exam/templates`, `/exam/pending` (`stu:863-981`); `/exam/templates?course_id=` accepts an empty string |
| T4 | Holds | A template with no assignment is open to the whole course (P:6984-6988, S:6091-6135) |
| T5 | Holds | No attempt limit; `/exam/pending` keeps submitted templates and no student screen shows it |
| T6 | Holds | Results count every session of the template; no per-student results; `exam_responses` keeps no chosen option |
| T7 | Holds | Edits rewrite the items in place; no course check on assignment; one commit per group |
| T8 | Partly | A mismatched course or template is now a 400. `course_name` still comes from the client, `total_time_taken` is discarded, a removed item makes the session unsubmittable, `active_exam_sessions` is never cleaned, `/exam/start` has no rate limit |
| T9 | **Resolved by spec 001 block 7** | A regrade applies only the difference (spec 001 FR-024d), per review round (FR-024l in spec 001) |
| T10 | Partly | With the item gone, the grading records 0 applied (spec 001 FR-024f), but the submission row still gets `elo_applied = 1` and the computed delta |
| T11 | Fixed (#40) | — |
| T12 | Holds, V1 only | V1 is disconnected at the switch and retired (roadmap F-10) |
| T13 | Holds | Main ∪ enrolment group; attempts, metrics, report and KatIA history not limited to the teacher's courses; pinned for #36 by `test_teacher_student_scope.py` |
| T14 | Holds | The four XLSX sheets build four different student sets; group rankings include test students |
| T15 | Partly | PostgreSQL no longer loads stored images in the queue when Storage has them (F-8); no active, test or role filter; follows the main group; a group-less student's procedure can never be graded |
| T16 | Partly | PDF and formulas fixed. The AI score still starts the slider and stays stale after a resubmission; `ai_feedback` is never shown |
| T17 | Holds | The browser computes the group mean, histogram, ranking (index positions) and the 1100 «attention» threshold; the server's `ranking_view` (`tch:463-474`) is not used by any screen |
| T18 | Fixed (#42) | — |
| T19 | Fixed | `limit` is bounded 1–200 |
| T20 | Mostly holds | Report and rating-history client calls unused; range buttons inert; a discarded query; an admin passes the teacher check and can edit and assign any template |
| T21 | — | Historical |

Decision 6 (resubmitted procedures) is answered by spec 001 block 7. Decision 11 (grace period)
was answered on 2026-10-15. The rest are the decisions of spec 006 (`specs/006-teacher-exams/
spec.md` § New Decisions).
