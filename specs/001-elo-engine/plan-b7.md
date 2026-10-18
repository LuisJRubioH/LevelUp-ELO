# Plan — spec 001, delivery B7: a regraded procedure counts once

**Spec**: [spec.md](spec.md) § Deliveries, B7 (User Story 9; FR-024a … FR-024k; owner decisions
B7-P1 … B7-P4 of 2026-10-13 and 2026-10-14) · **Branch**: `001-b7`, from `redesign` · **Date**:
2026-10-18 · **Constitution**: 1.2.0 (the automatic 0 of a copied procedure is a rating writer,
LuisJRubioH/LevelUp-ELO#71)

Not part of the switch to `main` (LuisJRubioH/LevelUp-ELO#3). Its read-only count in production
(§ Operations) comes first.

## Today, on `redesign @ 65b95d5`

- `save_procedure_submission` looks up the student's row for the item and updates or inserts it;
  nothing makes the pair unique, so two first submissions at once leave two rows (FR-024a).
- A resubmission returns the row to review and erases `teacher_score`, `final_score` and the
  feedback; `elo_delta` keeps the last computed delta, and no history exists (FR-024e).
- `validate_procedure_submission` stores `(grade − 50) × 0.2` in `elo_delta` and adds that **full**
  delta through `_bump_course_topic_rating` (floor 0 in SQL) every time the row is pending: grade
  80 (+6), resubmission, grade 30 (−4) leaves +2 instead of −4 (FR-024b, FR-024d). With a rating
  of 3, grade 0 stores −10 although −3 was applied.
- The grading response, the `procedure_graded` notification and the student's card show the
  computed delta (FR-024f). A retried grading finds the row no longer pending and gets 404
  (FR-024g).
- An upload whose SHA-256 another student already sent **for the same item** is refused with 409
  (`tests/api/test_procedure_upload_security.py::test_duplicate_file_from_another_student_is_rejected`);
  across items, and for the student's own files, nothing is checked (FR-024i … FR-024k).

## Constitution Check (1.2.0)

| Principle | B7 |
|---|---|
| Dual database (R1) | Same tables, columns and methods in both repositories; `db_sync_check.py`; every repository test parametrised over SQLite and PostgreSQL |
| Additive migrations (R8) | Four columns, three tables and one unique index added; nothing dropped or retyped. The unique index of FR-024a is created only where the data allow it (§ Data) |
| Layers (R2) | The grading arithmetic (correction, floor, contribution) and the upload's classification are pure functions in `src/domain/`; the repositories lock, read, call them and persist, as `save_answer_transaction` does (R16) |
| Single rating state (R15) | Still `student_course_topic_elo`; the procedure writer changes from "add the delta" to "apply the correction", and the copy is a new writer, both through one transaction method |
| Teacher authority (constitution, Domain Rules) | Only a teacher's grade or the automatic 0 of a copy moves a rating; the AI score never does (FR-024, unchanged) |
| No blocking I/O in async code (R17) | The upload route keeps its repository and Storage calls in `asyncio.to_thread`; grading is a `def` route |
| Personal data (VI) | The copy mark never names the other student; the count in production logs numbers only |

## Design

### The arithmetic, in the domain (FR-024b, FR-024d, B7-P2)

New pure function in `src/domain/elo/model.py`, beside `procedure_elo_delta`:

```
procedure_grading(grade, contribution, rating_before) -> ProcedureGrading
    computed   = (grade − 50) × 0.2                       # procedure_elo_delta
    correction = computed − contribution                   # FR-024d
    applied    = max(correction, −rating_before)           # the floor of 0
    contribution_after = contribution + applied
```

- `rating_before` is the item's (course, topic) rating read under lock; an absent row is 1000, as
  today.
- **Unknown contribution** (`contribution` is `None`, § Procedures graded before B7): `applied = 0`,
  `contribution_after = None`, and the result says so. The grade is recorded and the rating does
  not move until the procedure is reviewed one by one (FR-024h, B7-P1).
- Worked cases, each a test: 80 then 80 → correction 0 (US9-AS1); 60 then 90 → +6, contribution +8
  (US9-AS2); 80 then 30 → −10, contribution −4 (US9-AS3); rating 3, grade 0 → applied −3, then 80
  at rating 0 → correction +9, rating 9 (US9-AS7); rating 3, grade 0, then 0 again at rating 20 →
  correction −7 (B7-P2).

### The upload, in the domain (FR-024i … FR-024k)

New module `src/domain/procedures.py` (no I/O): `classify_upload(student_id, item_id,
own_upload_item, first_owner)` returns `accept`, `copy`, `refuse_same_item` or `refuse_other_item`:

1. The student already uploaded this file (any time, any item): for this item →
   `refuse_same_item` (FR-024k); for another item → `refuse_other_item` (FR-024j). Nothing changes.
2. Otherwise, another student uploaded it first, for any item → `copy` (FR-024i).
3. Otherwise → `accept`.

Rule 1 comes first: re-uploading a file the student already sent — their own or one recorded as a
copy — never starts a new review or a new 0.

### Data (R1, R8)

| Change | Purpose |
|---|---|
| `procedure_submissions.contribution` (`DOUBLE PRECISION` / `REAL`, default 0; NULL = unknown) | C, the net amount the procedure's gradings applied (FR-024b) |
| `procedure_submissions.contribution_origin` (`TEXT`) | `grading` or `legacy_unknown` (FR-024h) |
| `procedure_submissions.review_round` (`INTEGER`, default 1) | Which review a grading belongs to; a resubmission adds 1 (FR-024g) |
| `procedure_submissions.is_copy` (`INTEGER`, default 0) | The copy mark the teacher sees (FR-024i) |
| table `procedure_gradings` — `submission_id`, `review_round`, `grade`, `computed_delta`, `correction`, `applied`, `contribution_after` (NULL when unknown), `grader_id` (NULL = the system), `reason` (`teacher` / `copy`), `created_at`; **unique** `(submission_id, review_round)` | The history (FR-024e) and the one-grading-per-review guarantee (FR-024g) |
| table `procedure_files` — `file_hash` primary key, `student_id`, `item_id`, `created_at` | The first upload of each file: claimed with `INSERT … ON CONFLICT DO NOTHING`, so of two students sending the same new file at once exactly one is first (FR-024i) |
| table `procedure_uploads` — `student_id`, `item_id`, `file_hash`, `submission_id`, `outcome` (`accepted` / `copy`), `created_at`; **unique** `(student_id, file_hash)` | Each file a student uploaded, kept across resubmissions; the unique pair makes rules FR-024j and FR-024k atomic |
| unique index `procedure_submissions (student_id, item_id)` | FR-024a, when no duplicate pair exists (below) |

- **Backfill, idempotent and rating-neutral (FR-024h as amended 2026-10-18):** a row never graded
  keeps `contribution 0`; a graded row (a stored `elo_delta`), validated or resubmitted and
  pending, gets `NULL`, `legacy_unknown`, whatever the sign of its delta. On `main` a validated
  delta is added only when the rating is read; the stored rating that the switch carries is the
  last answer's, which holds the delta only through later answers stored under the item's topic,
  once per such answer — so no stored value says what the procedure contributed.
  `procedure_files` takes the earliest row of each `file_hash`; `procedure_uploads` one row per
  current submission with a hash (a pair already taken is skipped). Only rows whose
  `contribution_origin` is still NULL are touched, so a second run changes nothing. No rating is
  read or written.
- **Duplicate (student, item) pairs:** the migration counts them. With none, it creates the unique
  index. With some, it logs `procedure_submissions: N duplicate (student_id, item_id) pairs — unique
  index not created (spec 001 FR-024a)` and goes on. The per-student lock below still prevents new
  duplicates, and the count in production (§ Operations) reports the existing ones first, so their
  merge is prepared apart with a backup (B7-P4 as replaced).

### Uploading (FR-024a, FR-024c, FR-024i … FR-024k)

The route `POST /api/student/procedure` keeps reading and validating the file and hashing it. Then:

`StudentService.submit_procedure` calls `submit_procedure` in both repositories with the domain's
`classify_upload` and the copy's grading:

1. **Read-only classification** (the two facts, then the domain). A refused file answers 409
   before anything is uploaded to Storage:
   - `refuse_same_item` → «Ya subiste este archivo para este ejercicio.»;
   - `refuse_other_item` → «Este archivo pertenece a otro ejercicio.».
2. **Storage upload**, as today (the object path holds the hash).
3. **One transaction** (inside `submit_procedure`): lock the student's `users` row (PostgreSQL
   `FOR UPDATE`; SQLite `BEGIN IMMEDIATE`) — the lock order of answers, so no deadlock — insert the
   `procedure_uploads` row (a conflict means a concurrent upload of the same file: refuse as in
   step 1), claim `procedure_files`, upsert the one procedure of the pair (a resubmission adds 1 to
   `review_round`, returns it to review and keeps `contribution`, FR-024c), and, for a `copy`,
   grade it 0 inside the same transaction through the grading below, with the system as grader and
   `is_copy = 1`.
   - A refusal decided only here (a race between steps 1 and 3) leaves the stored object
     unreferenced; it is logged without the hash or the student.
4. The response says what happened. For a copy: `status "graded"`, `is_copy true`, grade 0 and the
   amount applied; the screen shows «Este archivo ya lo había entregado otro estudiante. El
   procedimiento quedó calificado con 0 y marcado como copia.»

An item that does not exist in the bank (the upload accepts any item id today) records the copy's
grade with nothing applied, as grading such an item applies nothing today.

### Grading (FR-024b, FR-024d … FR-024g)

`grade_procedure_transaction(submission_id, review_round, grader_id, grade, feedback, reason,
compute)` in both repositories:

1. Lock the student's `users` row, then the procedure row (PostgreSQL `FOR UPDATE`; SQLite
   `BEGIN IMMEDIATE`). For a teacher, the procedure must belong to one of their groups (FR-023,
   unchanged).
2. If a grading already exists for `(submission_id, review_round)`, return it unchanged: a retry
   or the loser of two simultaneous gradings gets the same result and nothing is applied twice
   (FR-024g). The unique pair of `procedure_gradings` backs this on both engines.
3. If the procedure is not pending in that round, refuse (404, as today).
4. Read `contribution` and the item's (course, topic) rating, call `compute` — the domain's
   `procedure_grading` supplied by the service — and persist in the same transaction: the rating
   (`current_elo = before + applied`, absent row created from 1000 + applied with origin
   `procedure`), the `procedure_gradings` row, and the procedure (`teacher_score`, `final_score`,
   feedback, `elo_delta` = computed, `contribution`, `contribution_origin = 'grading'` unless it
   stays unknown, `elo_applied = 1`, status `VALIDATED_BY_TEACHER`).

`validate_procedure_submission(submission_id, teacher_score, feedback, teacher_id)` and
`save_procedure_submission(...)` stay, with their contracts, as thin calls to the new methods for
the current round and with the domain's rules, so V1 (frozen) and today's callers keep working.
`TeacherService.grade_procedure` refuses a grade outside 0–100 before the repository runs
(FR-023), supplies the domain computation and returns the result; `validate_procedure` returns its
amount applied. `check_file_hash_duplicate` stays: V1 calls it.

### What is shown (FR-024e, FR-024f)

- **Grading response** (`POST /api/teacher/procedures/grade`): `elo_delta` becomes the amount
  applied; new fields `computed_delta`, `contribution` (null when unknown) and `review_round`. The
  request takes an optional `review_round`; the teacher's queue returns it, and a request without
  it means the current round.
- **Notification** `procedure_graded`: the same amount applied, plus `computed_delta`.
- **Student** (`GET /api/student/procedures` and the card in `Feedback.tsx`): the latest grading's
  amount applied, the contribution and the copy mark — never the computed delta (US9-AS9).
- **Teacher** (`Procedures.tsx`): after grading, the amount applied. Below the queue, a «Copias
  detectadas» list of the copies marked in their groups in the last 30 days: student, item, date,
  «Calificado 0 automáticamente». The other student is never named: they may belong to another
  teacher's group.
- **History** (`GET /api/teacher/procedures/{id}/gradings`): every grading of the procedure — grade,
  computed delta, correction, amount applied, contribution after, who graded (a teacher's name, or
  none for the system's copy grade) and when (US9-AS8). Teachers of the student's group only:
  another teacher gets 404 and a student 403 (the teacher routes' role guard).

### Procedures graded before B7 (FR-024h, B7-P1)

Installing B7 changes no rating. Every procedure graded before B7 is `legacy_unknown` (amended
2026-10-18; until then a non-negative stored delta was taken as the contribution). One that is regraded
records the grade, applies nothing, and appears in the teacher's history as «Pendiente de revisión:
no se sabe cuánto aplicó la calificación anterior». The owner reviews those one by one, with the
count of § Operations; nothing in B7 resolves them automatically.

## Operations (before merging B7 into `main`)

A read-only job in the `transfer-ops` workflow (`ops/transfer-b7check`, Environment
`production-ops`, transactions `READ ONLY`), whose public log holds numbers only:

- graded procedures, all of which become `legacy_unknown`, and how many of them are resubmitted
  and still pending;
- validated procedures whose delta reached the stored rating through later answers on the item's
  topic, and how many such answers — the ones to review first;
- duplicate `(student_id, item_id)` pairs (FR-024a's index is not created while any exist);
- files sent by more than one student (they stay as they are; the first sender becomes the file's
  first owner).

It logs numbers only and keeps no artifact. The owner reads the counts before the merge; a
duplicate pair is merged apart, with a backup, before or after B7, and the procedures whose
contribution is unknown are looked up one by one when the owner reviews them.

## Tests

- **Domain** (`tests/unit/domain/test_spec001_b7_procedures.py`): every worked case above, the
  unknown contribution, and the upload's classification and its order.
- **Both engines, repository** (`tests/integration/test_spec001_b7_procedures.py`): resubmission
  keeps the contribution (characterization, on unchanged code first); equal, higher and lower
  regrade; the floor and its remainder; history kept across resubmissions; a retried grading and
  two at once (threads, each engine) apply one correction; concurrent first submissions leave one
  row; the migration on a copy with graded, negative and duplicate rows changes no rating, backfills
  as above, runs twice the same, and skips the index only when a duplicate pair exists; copy,
  same-item and other-item uploads; two students sending one new file at once leave exactly one
  first owner.
- **API, both engines** (`tests/integration/test_spec001_b7_api.py`): the response, the notification and the
  student's list report the amount applied; a retried request returns the same body; the copy and
  the two refusals with their messages; the history for the group's teacher only. The existing
  `test_duplicate_file_from_another_student_is_rejected` is flipped to the copy, citing FR-024i.
- **Screens** (`frontend/e2e/spec001-b7-procedures.spec.ts`): the student's card shows the amount
  applied and the copy mark; the teacher sees the amount after grading and the «Copias detectadas»
  list; the upload shows the copy result and both refusals.

## Files

Code Scope additions in the code PR: `src/domain/procedures.py`,
`frontend/src/pages/Student/ProcedureUpload.tsx`, `frontend/src/components/Procedure/ProcedureSection.tsx`.
Changed: `src/domain/elo/model.py`, both repositories and `application/interfaces/repositories.py`,
`application/services/teacher_service.py` and `student_service.py`, `api/routers/student.py`,
`api/routers/teacher.py`, `api/schemas/`, `frontend/src/api/{student,teacher}.ts`,
`frontend/src/pages/Teacher/Procedures.tsx`, `frontend/src/pages/Student/Feedback.tsx`, the i18n
files, `AGENTS.md` (R15's writer table: the correction and the copy), `docs/guia-docente.md` and
`docs/guia-estudiante.md`.

## Choices made here, for the owner's review

1. The copy list names the copier, never the first sender, and shows the last 30 days.
2. A re-upload of a file the student already sent is refused even if that earlier upload was a
   copy: rule 1 before rule 2, so a copy is graded 0 once.
3. Duplicate pairs skip FR-024a's index instead of stopping the migration; the lock covers new
   ones and the count reports old ones.
4. A `legacy_unknown` procedure that is regraded applies nothing until reviewed one by one.
5. The student's and teacher's wording above.

## Owner answers of 2026-10-18 (after the review of LuisJRubioH/LevelUp-ELO#77)

- **Every earlier grading is unknown** (FR-024h): the backfill above, and `b7check` counts the
  procedures whose delta reached the stored rating.
- **A copy is a 0 like any other** (FR-024i): `submit_procedure` already grades it with the
  domain's `procedure_grading(0, C, R)`, the computation a teacher's 0 uses; only `reason` and
  `grader_id` differ, so where C is unknown neither moves the rating. No code changes; a test
  compares the two gradings field by field.
- **A review a resubmission replaced** (FR-024l): `grade_procedure_transaction`, in both
  repositories, raises the domain's `ReviewRoundSuperseded(current_round)` when the round asked
  is older than the procedure's and was never graded (a retry of a graded round still returns its
  result, FR-024g). `POST /api/teacher/procedures/grade` answers 409 «El estudiante reenvió este
  procedimiento; revisa el envío nuevo antes de calificar.»; the teacher's screen reloads the
  queue on that 409, and the procedure's image is cached per review round, so the new file is
  shown.
- **A refused upload leaves no file** (FR-024j, FR-024k): when an upload is not recorded —
  refused under the lock, or failed — `submit_procedure` removes the local file it wrote and, on
  PostgreSQL, the Storage object (`SupabaseStorage.remove_file`), unless a procedure uses that
  file: two uploads of one file for one item share its Storage path, and a local file name can
  repeat within one second.

## Merge order

After this plan is approved: the code PR on `redesign` (or `main` after the switch), with the count
of § Operations run before it reaches `main`.
