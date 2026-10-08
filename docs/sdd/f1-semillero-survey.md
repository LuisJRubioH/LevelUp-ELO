# F-1 — Semillero catalogue: as-is survey and proposal

Read-only survey of `redesign @ 9546ab5`, 2026-10-08, for roadmap follow-up **F-1**
(`docs/sdd/roadmap.md` § Follow-ups). **Status: proposal for the owner's review — no behaviour has
been changed.** Each finding cites code; "verified" means reproduced on that commit through the V2
API on a fresh SQLite database or on a local PostgreSQL.

## 1. As-is

| Concern | Behaviour today | Where | |
|---|---|---|---|
| Course data | All 36 semillero courses have `block = 'Semillero'`; the grade is the id suffix (`algebra_semillero_6`) | `_COURSE_BLOCK_MAP` in both repositories | verified |
| Catalogue, semillero **with** grade | Looks for `block = 'Semillero {grade}°'`, which no course has → **0 courses** (grade 6, 9 and 11 checked) | `sqlite_repository.py:3094`, `postgres_repository.py:3653` | verified |
| Catalogue, semillero **without** grade | `block = 'Semillero'` → **all 36 courses**, grades 6–11 | same | verified |
| The correct rule already exists twice | `in_catalogue` (domain, used for spec 001's current context) and `get_teachers_with_groups_and_courses` (`c.id LIKE '%semillero_{grade}'`) filter by id suffix | `src/domain/entities.py:34`, `sqlite_repository.py:2196` | read |
| Registration | V2 API accepts semillero without grade (201); `grade` is optional in the schema and the repository stores it as given. Both UIs always send one (V1 select box; V2 default 9) | `api/schemas/auth.py:22`, `sqlite_repository.py:1179`, `postgres_repository.py:1515` | verified |
| Changing the grade later | **No path**: `set_grade` exists in both repositories but nothing calls it (no V1 view, no API route, no admin screen) | `sqlite_repository.py:3279`, `postgres_repository.py:3859` | read |
| Enrolment | `POST /api/student/enroll` checks only that the course exists: a grade-6 student enrols in `calculo_diferencial` (Universidad) and in `algebra_semillero_11` → 201 | `api/routers/student.py:295` | verified |
| Enrolment by invite code | Cross-level by design (the teacher's group course) | `api/routers/student.py` `enroll-by-code` | read |
| Practice | `POST /api/student/next-question` serves items of any course, enrolled or not | `api/routers/student.py:105` | verified |
| Ratings context | `in_catalogue(semillero, grade=None, …)` is true for every semillero course, so a grade-less student's overall rating averages enrolled courses of all grades | `src/domain/entities.py:45` | read |
| V1 (frozen) | Filters enrolments by `block == 'Semillero {grade}°'` but also shows any enrolment made through a group, so group enrolments still appear | `student_view.py:166` | read |
| Data | In the legacy-data simulation every semillero student has a grade (9 and 11). The production count is unknown | — | — |

Selection of exercises does not depend on the grade directly: within a course the selector uses
the topic or course rating (spec 001 FR-016–019, FR-029a). The grade decides **which courses** a
student is offered, and through `in_catalogue` which ones count as current for the overall
rating and rankings (FR-028a–c).

## 2. Decision 1 — a semillero student without a grade

Owner's rule (2026-10-08): **a student cannot enter Semillero without a grade; the grade they
practise for is mandatory.**

| Option | What the student sees | Enrolment and practice | Fits the rule? |
|---|---|---|---|
| A. Keep today's behaviour | All 36 courses of grades 6–11 | Enrols in any of them; all count as current | No |
| B. Empty catalogue only | Nothing until a grade exists | Registration still accepts no grade, and nothing lets the grade be set later | Partly |
| **C. Grade required (recommended)** | Exactly the six courses of their grade | Cannot register without a grade; cannot enrol outside the catalogue | Yes |

Option C, in detail:

1. **Registration** rejects `education_level = semillero` without `grade`: an API schema rule
   (422) and the same check in `register_user` on both engines. Neither UI changes: both already
   send a grade.
2. **Catalogue** = the semillero courses whose id ends in `_semillero_{grade}`, through the domain
   rule `in_catalogue`, in both repositories. The catalogue and the current context of spec 001
   cannot diverge.
3. **No grade** (only rows created before this rule): `in_catalogue` matches no semillero course,
   so the catalogue is empty and nothing counts as current; ratings show "pending", never 1000
   (FR-028b).
4. **Enrolment** (`/enroll`) rejects a course outside the student's catalogue. This applies to
   every level, closing enrolment outside one's level through the API. `enroll-by-code` stays as
   the teacher's cross-level access: **owner decision** whether it should also require a grade for
   a semillero student.
5. **Existing grade-less semillero students**: count them first with a read-only query:

   ```sql
   SELECT count(*) FROM users
   WHERE role = 'student' AND education_level = 'semillero' AND (grade IS NULL OR grade = '');
   ```

   Since no screen can set a grade, any found are fixed by the owner (a documented one-off
   update). A grade editor, which promotion also needs, belongs to spec 004 (identity and access).

**Out of F-1** (proposed as separate follow-ups, not widened into this fix):

- **F-4:** `next-question` without an enrolment check. This is access control for practice, not
  the catalogue.
- **Spec 004:** changing the grade (promotion).
- **V1:** its own `Semillero {grade}°` filter. V1 is frozen and gets only the shared fix.

## 3. Decision 2 — the `courses.block` CHECK

| Engine | Constraint today | Migration guard |
|---|---|---|
| SQLite | `block IN ('Universidad','Colegio','Concursos','Semillero')` | Probes an insert of `'Semillero'`; if accepted, does nothing (`sqlite_repository.py:915`) |
| PostgreSQL | `block IN ('Universidad','Colegio','Concursos','Semillero', 'Semillero' ×5, 'Semillero 11°')`, i.e. those four plus `'Semillero 11°'` | Returns only if the definition contains `'Semillero 6'`, which it never does: **every migration drops and re-adds the constraint** (`postgres_repository.py:1244`; the constraint's oid changed on each of two consecutive `migrate.py` runs) |

**What F-1 needs: no new value.** Every semillero course is `'Semillero'`, and the fix reads the
grade from the id. The `'Semillero {grade}°'` blocks were never written by any code.

| Option | Change | Additive (AGENTS R8)? | Parity |
|---|---|---|---|
| A. Leave it | none | It already breaks the spirit of R8: a `DROP CONSTRAINT` on every migration, with an exclusive lock on `courses` | PostgreSQL also accepts `'Semillero 11°'` |
| **B. Fix the guard (recommended)** | Return when the constraint already accepts the four blocks the code writes (read-only check of `pg_get_constraintdef`). Only an old database lacking one of them is widened, with values added, never removed. Fresh PostgreSQL databases get the de-duplicated four-value list | **Yes.** No DDL at all on any current database, production included | Same values written on both engines; legacy PostgreSQL databases keep the unused `'Semillero 11°'`, documented |
| C. Normalise existing databases | Drop and re-add without `'Semillero 11°'` | **No** (narrows a constraint; fails if a row uses that value) — needs an owner exception | Exact |

Parity is proven by a two-engine test rather than by text:
- each of the four blocks is accepted;
- a value no code writes (`'Semillero 6°'`) is rejected;
- on PostgreSQL, two migrations leave the constraint's oid unchanged.

`db_sync_check.py` keeps checking the repositories' public API.

## 4. Tests, written first (each fails on `9546ab5`)

| Test | Engines | Today |
|---|---|---|
| A grade-*g* semillero student's catalogue is exactly the six `*_semillero_g` courses, for *g* = 6 … 11 | SQLite + PostgreSQL | 0 courses |
| The same through `GET /api/student/courses` | API | 0 courses |
| Registration of semillero without grade → 422 (API) and rejected by `register_user` | API, both engines | 201 / accepted |
| A grade-less semillero row: empty catalogue, no current course, ratings "pending" | both engines + domain | 36 courses |
| `/enroll` outside the catalogue → rejected; inside → 201 | API | 201 for both |
| `in_catalogue` table: level × grade × course id (grades 6 … 11, a course of another grade, no grade) | domain | grade-less case differs |
| The block CHECK: four accepted, `'Semillero 6°'` rejected; on PostgreSQL the oid is stable over two migrations | both engines | oid changes |

## 5. How it would ship

- **Branch:** `fix/f1-semillero-catalogue`, its own PR after PR #3, because it touches
  migration code that was rehearsed for the transfer.
- **Spec record:** the owner's rule goes into spec 001 as a clarification plus a lettered
  `[CHANGE]` requirement on the catalogue for a grade-less semillero student, with its
  traceability row (checked by A-2). The registration rule is noted for spec 004.
- **Verification:**
  - full suite on PostgreSQL, `db_sync_check.py`, the traceability check;
  - `scripts/rehearse_migration.py` on the legacy-data simulation, showing that the second
    migration issues no DDL;
  - the read-only count of § 2 on production, before merging.

**Owner decisions needed:**
1. Option C for Decision 1, including the `/enroll` check for every level.
2. Whether `enroll-by-code` should require a grade.
3. Option B for Decision 2.
