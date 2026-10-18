# Tasks — spec 001, delivery B7 (a regraded procedure counts once)

**Plan**: [plan-b7.md](plan-b7.md). One `[AS-IS]` requirement, FR-024c (a resubmission returns the
procedure to review and keeps its rating effect): its characterization test passes on the unchanged
code before anything else. Every other B7 requirement is `[CHANGE]`: its test is written first and
must fail on the unchanged code (missing function, column, table, field or behaviour), then pass
with its implementation. The existing pins of FR-022, FR-023 and FR-024 (§ Traceability, delivery
S1) must stay green throughout: a first grading still adds `(grade − 50) × 0.2`.

`[P]` marks tasks that can run in parallel with the others of their phase.

## Phase 1 — Setup

- [x] T001 Branch `001-b7` from `redesign`; spec 001's Code Scope gains `src/domain/procedures.py`,
  `frontend/src/pages/Student/ProcedureUpload.tsx` and
  `frontend/src/components/Procedure/ProcedureSection.tsx` as they change (the checker accepts only
  tracked files)

## Phase 2 — Pin current behaviour (blocking)

- [x] T002 Characterization test, both engines, in `tests/integration/test_spec001_b7_procedures.py`:
  a procedure graded 80 (+6) and resubmitted is pending review and the topic rating still holds the
  +6 (FR-024c, US9-AS4) — **passes on the unchanged code**
- [x] T003 Re-run the S1 pins of FR-022, FR-023 and FR-024 with T002 on the unchanged code and
  record the green run here — 2026-10-18, both engines: T002 and the procedure pins of
  `test_spec001_course_topic_store.py` 6 passed; the repository pins, `test_elo_single_source.py`,
  `tests/api/test_procedure_grading.py`, the upload tests and the image fallback 48 passed

**Checkpoint**: no task below starts before T002–T003 are green on the unchanged code.

## Phase 3 — User Story 9: tests first (each must fail on the unchanged code)

### Domain, no I/O — `tests/unit/domain/test_spec001_b7_procedures.py`

- [x] T004 [P] `procedure_grading`: 80 then 80 → correction 0, contribution +6 (US9-AS1); 60 then 90
  → +6, contribution +8 (US9-AS2); 80 then 30 → −10, contribution −4 (US9-AS3); rating 3, grade 0 →
  applied −3, then 80 at rating 0 → +9, rating 9, contribution +6 (US9-AS7); rating 3, grade 0,
  then 0 at rating 20 → −7 (B7-P2); a first grading equals today's delta (FR-022 unchanged)
  (FR-024b, FR-024d)
- [x] T005 [P] `procedure_grading` with an unknown contribution applies 0 and keeps it unknown
  (FR-024h)
- [x] T006 [P] `classify_upload`: own file, same item → `refuse_same_item` (FR-024k); own file,
  other item → `refuse_other_item` (FR-024j); another student's file → `copy` (FR-024i); own
  earlier copy re-uploaded → refused, not a second copy; a new file → `accept`

### Both engines, repository — `tests/integration/test_spec001_b7_procedures.py`

- [x] T007 Equal, higher and lower regrade move the rating by the correction and store the
  contribution (US9-AS1, US9-AS2, US9-AS3; FR-024b, FR-024d)
- [x] T008 The floor: rating 3, grade 0, resubmission, grade 80 → rating 9, contribution +6
  (US9-AS7; FR-024d)
- [x] T009 Two gradings of one procedure leave two history rows with grade, computed delta,
  correction, amount applied, contribution after, grader and time, kept across the resubmission
  (US9-AS8; FR-024e)
- [x] T010 A retried grading returns the stored result and applies nothing (US9-AS5); two gradings
  of one review in two threads apply exactly one correction and both get the same result (US9-AS6)
  (FR-024g)
- [x] T011 Two first submissions of one student and item in two threads leave one procedure
  (FR-024a)
- [x] T012 Migration on a copy holding never-graded, positively graded, negatively graded and
  resubmitted procedures and one duplicate (student, item) pair: no rating changes; contributions
  backfilled as `legacy_delta` / `legacy_unknown` / 0; the unique index skipped with the log line
  while the duplicate exists and created once it is gone; a second run changes nothing; a
  `legacy_unknown` procedure regraded applies nothing (FR-024h, FR-024a)
- [x] T013 A file another student uploaded, for the same item and for another one, makes a procedure
  graded 0 by the system, marked as a copy, −10 on the item's topic (floor 0) (US9-AS10; FR-024i);
  two students uploading one new file in two threads leave exactly one first owner
- [x] T014 The student's own file for another item and for the same item is refused and nothing
  changes — no procedure, no review round, no rating (US9-AS11, US9-AS12; FR-024j, FR-024k)

### Both engines, API — `tests/integration/test_spec001_b7_api.py`

The integration `client` fixture runs these on SQLite and PostgreSQL; `tests/api/` is SQLite only.

- [x] T015 Grading response, `procedure_graded` notification and the student's procedure list report
  the amount applied and the contribution, never the computed delta, after a regrade and after a
  floored grade (US9-AS9; FR-024f)
- [x] T016 A retried `POST /api/teacher/procedures/grade` with the same `review_round` returns the
  same body and notifies once; a round that is neither the current one nor already graded is
  refused (FR-024g, US9-AS5)
- [x] T017 Upload: the copy answers `graded`, `copy true`, grade 0; the two refusals answer 409 with
  their messages; flip `test_procedure_upload_security.py::test_duplicate_file_from_another_student_is_rejected`
  to the copy, renamed `…_is_graded_zero_as_a_copy`, citing FR-024i (US9-AS10 … AS12). Earlier tests that met block 7, each changed in the
  open: `test_postgres_production_guards.py` (its duplicate upload is a copy now, FR-024i; its file
  is unique per run, since that database keeps earlier runs' files);
  `test_procedure_upload_security.py::test_client_cannot_forge_ai_score_but_signed_review_is_accepted`
  (the signed review comes with a second file: the same file again is refused, FR-024k);
  `test_procedure_grading.py::test_reassignment_between_lookup_and_update_prevents_grading` (the
  reassignment lands before `grade_procedure_transaction`, where the update now runs; assertions
  unchanged); `tests/unit/application/test_teacher_service.py::TestValidateProcedure` (the same seam,
  plus a grade outside 0–100 never reaching the repository, FR-023);
  `test_spec004_e2_display_names.py::test_spec004_teacher_views_show_name_and_group` (a file unique
  per run, for the same reason)
- [x] T018 The grading history is served to the student's group teacher only: another teacher gets
  404, a student 403 (the teacher routes' role guard); the copies list names the copier, never the
  first sender, and is empty for another teacher (FR-024e, FR-024i, FR-023)

### Screens — `frontend/e2e/spec001-b7-procedures.spec.ts`

- [x] T019 [P] The student's card shows the amount applied and the copy mark (US9-AS9, US9-AS10)
- [x] T020 [P] The teacher sees the amount applied after grading and the «Copias detectadas» list,
  which never names the first sender (FR-024f, FR-024i)
- [x] T021 [P] The upload shows the copy result and each refusal's message (FR-024i … FR-024k)

Run on the unchanged screens first: T019, T020 and the copy result of T021 failed; the two refusals
passed, because the upload screen already showed the server's reason. Their change is the
server's, and T017 covers it.

## Phase 4 — Implementation

- [x] T022 `procedure_grading` in `src/domain/elo/model.py` and `classify_upload` in
  `src/domain/procedures.py` (makes T004–T006 pass)
- [x] T023 Schema in both repositories, additive and idempotent (R1, R8): the four columns,
  `procedure_gradings`, `procedure_files`, `procedure_uploads`, the conditional unique index and the
  rating-neutral backfill; `db_sync_check.py` (T012)
- [x] T024 `grade_procedure_transaction` and `validate_procedure_submission` on top of it, lock order
  users → procedure, in both repositories; protocol (T007–T010)
- [x] T025 `submit_procedure` (read-only classification before storing, then under the per-student
  lock: the first-owner claim, the upload record, the review round and the copy graded in the
  same transaction); `save_procedure_submission` keeps its contract on top of it, and
  `check_file_hash_duplicate` stays, because V1 (frozen) calls both (T011, T013, T014)
- [x] T026 Services: `TeacherService.grade_procedure` refuses a grade outside 0–100, supplies the
  domain computation and returns the result (`validate_procedure` returns its amount applied); the
  student's upload goes through `StudentService.submit_procedure` (R2)
- [x] T027 API: upload route with the pre-upload classification and responses; grading request and
  response fields; notification; student list fields; the history endpoint (T015–T018)
- [x] T028 Screens and i18n: `Feedback.tsx`, `Procedures.tsx` (amount applied, review round, copies
  list), `ProcedureUpload.tsx` / `ProcedureSection.tsx` (copy result, refusals) (T019–T021)
- [x] T029 Read-only job `b7check` on the `ops/transfer` branch, triggered by pushing
  `ops/transfer-b7check` (numbers only, no artifact), tested locally against the simulated
  production and its migrated copy; that branch is pushed only when the owner says so

## Phase 4b — Review follow-ups

An independent review of the implementation (2026-10-18) found three defects. Each test was written
first and failed on 262e470, on both engines, then passed with its fix.

- [x] T031 V1 records the AI's score after every upload, a copy or a refused file included, and
  `save_ai_proposed_score` reopened the procedure for review: a copy's automatic 0 then stayed in
  the queue, and grading it applied nothing. Only a procedure waiting for review takes the score
  now, in both repositories (FR-024i, FR-024k) —
  `test_spec001_b7_an_ai_score_never_reopens_a_graded_procedure_or_a_copy`
- [x] T032 While an old duplicate (student, item) pair holds the unique index back, an upload
  updated both rows and graded one: the other was left pending with its own contribution, and
  grading it applied a second correction. The upload now resubmits or grades the first procedure
  only (FR-024b, FR-024a) —
  `test_spec001_b7_with_a_duplicate_pair_an_upload_changes_one_procedure`
- [x] T033 The teacher's export (V2 `/export/xlsx`, V1's «Delta ELO») showed the computed delta;
  it shows the amount applied, as every screen does (FR-024f) —
  `test_spec001_b7_the_teacher_export_reports_the_amount_applied`

## Phase 5 — Close

- [x] T030 Traceability: every B7 row filled with its tests; B7 `closed`; AGENTS.md R15 (the
  procedure writer applies the correction; the copy writer); `docs/guia-docente.md` and
  `docs/guia-estudiante.md` (resubmission, copies); `check_traceability.py`, the full suite on both
  engines, Playwright, `db_sync_check.py`, black, flake8 and the build
