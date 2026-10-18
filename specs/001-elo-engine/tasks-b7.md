# Tasks — spec 001, delivery B7 (a regraded procedure counts once)

**Plan**: [plan-b7.md](plan-b7.md). One `[AS-IS]` requirement, FR-024c (a resubmission returns the
procedure to review and keeps its rating effect): its characterization test passes on the unchanged
code before anything else. Every other B7 requirement is `[CHANGE]`: its test is written first and
must fail on the unchanged code (missing function, column, table, field or behaviour), then pass
with its implementation. The existing pins of FR-022, FR-023 and FR-024 (§ Traceability, delivery
S1) must stay green throughout: a first grading still adds `(grade − 50) × 0.2`.

`[P]` marks tasks that can run in parallel with the others of their phase.

## Phase 1 — Setup

- [ ] T001 Branch `001-b7` from `redesign`; spec 001's Code Scope gains `src/domain/procedures.py`,
  `frontend/src/pages/Student/ProcedureUpload.tsx` and
  `frontend/src/components/Procedure/ProcedureSection.tsx` as they change (the checker accepts only
  tracked files)

## Phase 2 — Pin current behaviour (blocking)

- [ ] T002 Characterization test, both engines, in `tests/integration/test_spec001_b7_procedures.py`:
  a procedure graded 80 (+6) and resubmitted is pending review and the topic rating still holds the
  +6 (FR-024c, US9-AS4) — **passes on the unchanged code**
- [ ] T003 Re-run the S1 pins of FR-022, FR-023 and FR-024 with T002 on the unchanged code and
  record the green run here

**Checkpoint**: no task below starts before T002–T003 are green on the unchanged code.

## Phase 3 — User Story 9: tests first (each must fail on the unchanged code)

### Domain, no I/O — `tests/unit/domain/test_spec001_b7_procedures.py`

- [ ] T004 [P] `procedure_grading`: 80 then 80 → correction 0, contribution +6 (US9-AS1); 60 then 90
  → +6, contribution +8 (US9-AS2); 80 then 30 → −10, contribution −4 (US9-AS3); rating 3, grade 0 →
  applied −3, then 80 at rating 0 → +9, rating 9, contribution +6 (US9-AS7); rating 3, grade 0,
  then 0 at rating 20 → −7 (B7-P2); a first grading equals today's delta (FR-022 unchanged)
  (FR-024b, FR-024d)
- [ ] T005 [P] `procedure_grading` with an unknown contribution applies 0 and keeps it unknown
  (FR-024h)
- [ ] T006 [P] `classify_upload`: own file, same item → `refuse_same_item` (FR-024k); own file,
  other item → `refuse_other_item` (FR-024j); another student's file → `copy` (FR-024i); own
  earlier copy re-uploaded → refused, not a second copy; a new file → `accept`

### Both engines, repository — `tests/integration/test_spec001_b7_procedures.py`

- [ ] T007 Equal, higher and lower regrade move the rating by the correction and store the
  contribution (US9-AS1, US9-AS2, US9-AS3; FR-024b, FR-024d)
- [ ] T008 The floor: rating 3, grade 0, resubmission, grade 80 → rating 9, contribution +6
  (US9-AS7; FR-024d)
- [ ] T009 Two gradings of one procedure leave two history rows with grade, computed delta,
  correction, amount applied, contribution after, grader and time, kept across the resubmission
  (US9-AS8; FR-024e)
- [ ] T010 A retried grading returns the stored result and applies nothing (US9-AS5); two gradings
  of one review in two threads apply exactly one correction and both get the same result (US9-AS6)
  (FR-024g)
- [ ] T011 Two first submissions of one student and item in two threads leave one procedure
  (FR-024a)
- [ ] T012 Migration on a copy holding never-graded, positively graded, negatively graded and
  resubmitted procedures and one duplicate (student, item) pair: no rating changes; contributions
  backfilled as `legacy_delta` / `legacy_unknown` / 0; the unique index skipped with the log line
  while the duplicate exists and created once it is gone; a second run changes nothing; a
  `legacy_unknown` procedure regraded applies nothing (FR-024h, FR-024a)
- [ ] T013 A file another student uploaded, for the same item and for another one, makes a procedure
  graded 0 by the system, marked as a copy, −10 on the item's topic (floor 0) (US9-AS10; FR-024i);
  two students uploading one new file in two threads leave exactly one first owner
- [ ] T014 The student's own file for another item and for the same item is refused and nothing
  changes — no procedure, no review round, no rating (US9-AS11, US9-AS12; FR-024j, FR-024k)

### Both engines, API — `tests/api/test_spec001_b7_procedures.py`

- [ ] T015 Grading response, `procedure_graded` notification and the student's procedure list report
  the amount applied and the contribution, never the computed delta, after a regrade and after a
  floored grade (US9-AS9; FR-024f)
- [ ] T016 A retried `POST /api/teacher/procedures/grade` with the same `review_round` returns the
  same body; a stale round is refused (FR-024g, US9-AS5)
- [ ] T017 Upload: the copy answers `graded`, `copy true`, grade 0; the two refusals answer 409 with
  their messages; flip `tests/api/test_procedure_upload_security.py::test_duplicate_file_from_another_student_is_rejected`
  to the copy, citing FR-024i (US9-AS10 … AS12)
- [ ] T018 The grading history is served to the student's group teacher only; another teacher and a
  student get 404 (FR-024e, FR-023)

### Screens — `frontend/e2e/spec001-b7-procedures.spec.ts`

- [ ] T019 [P] The student's card shows the amount applied and the copy mark (US9-AS9, US9-AS10)
- [ ] T020 [P] The teacher sees the amount applied after grading and the «Copias detectadas» list,
  which never names the first sender (FR-024f, FR-024i)
- [ ] T021 [P] The upload shows the copy result and each refusal's message (FR-024i … FR-024k)

## Phase 4 — Implementation

- [ ] T022 `procedure_grading` in `src/domain/elo/model.py` and `classify_upload` in
  `src/domain/procedures.py` (makes T004–T006 pass)
- [ ] T023 Schema in both repositories, additive and idempotent (R1, R8): the four columns,
  `procedure_gradings`, `procedure_files`, `procedure_uploads`, the conditional unique index and the
  rating-neutral backfill; `db_sync_check.py` (T012)
- [ ] T024 `grade_procedure_transaction` and `validate_procedure_submission` on top of it, lock order
  users → procedure, in both repositories; protocol (T007–T010)
- [ ] T025 `classify_procedure_upload` and `record_procedure_upload` (per-student lock, upload and
  first-owner claims, review round, copy graded in the same transaction); remove
  `check_file_hash_duplicate` from both repositories and the protocol (T011, T013, T014)
- [ ] T026 Services: `TeacherService.validate_procedure` supplies the domain computation and returns
  the result; the student's upload goes through `StudentService` (R2)
- [ ] T027 API: upload route with the pre-upload classification and responses; grading request and
  response fields; notification; student list fields; the history endpoint (T015–T018)
- [ ] T028 Screens and i18n: `Feedback.tsx`, `Procedures.tsx` (amount applied, review round, copies
  list), `ProcedureUpload.tsx` / `ProcedureSection.tsx` (copy result, refusals) (T019–T021)
- [ ] T029 Read-only job `ops/transfer-b7check` on the `ops/transfer` branch (numbers in the log,
  identifiers only in the encrypted artifact), tested locally against a simulated production; it is
  pushed only when the owner says so

## Phase 5 — Close

- [ ] T030 Traceability: every B7 row filled with its tests; B7 `closed`; AGENTS.md R15 (the
  procedure writer applies the correction; the copy writer); `docs/guia-docente.md` and
  `docs/guia-estudiante.md` (resubmission, copies); `check_traceability.py`, the full suite on both
  engines, Playwright, `db_sync_check.py`, black, flake8 and the build
