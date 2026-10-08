# F-1 — Semillero catalogue: as-is survey, decisions and plan

Read-only survey of `redesign @ 9546ab5`, 2026-10-08, for roadmap follow-up **F-1**
(`docs/sdd/roadmap.md` § Follow-ups).

**Status:**
- Owner decisions taken 2026-10-08 (§ 2), including the old-database path of the block
  constraint (§ 4.3) and the notice for semillero accounts without a grade (§ 2, decision 6).
- Spec 001 amended (FR-028k … FR-028o, User Story 7, traceability rows `PENDING`).
- Code is developed and tested locally only; the production checks of § 3 and § 4.3 step 1 are
  requirements before deploying, not part of the code PR.

Each finding cites code. "Verified" means reproduced on that commit through the V2 API on a fresh
SQLite database or on a local PostgreSQL.

## 1. As-is

| Concern | Behaviour today | Where | |
|---|---|---|---|
| Course data | All 36 semillero courses have `block = 'Semillero'`; the grade is the id suffix (`algebra_semillero_6`) | `_COURSE_BLOCK_MAP` in both repositories | verified |
| Catalogue, semillero **with** grade | Looks for `block = 'Semillero {grade}°'`, which no course has → **0 courses** (grades 6, 9 and 11 checked) | `sqlite_repository.py:3094`, `postgres_repository.py:3653` | verified |
| Catalogue, semillero **without** grade | `block = 'Semillero'` → **all 36 courses**, grades 6–11 | same | verified |
| The correct rule already exists twice | `in_catalogue` (domain, used for spec 001's current context) and `get_teachers_with_groups_and_courses` (`c.id LIKE '%semillero_{grade}'`) filter by id suffix | `src/domain/entities.py:34`, `sqlite_repository.py:2196` | read |
| Registration | V2 API accepts semillero without grade (201). Both UIs always send one (V1 select box; V2 default 9) | `api/schemas/auth.py:22`, `sqlite_repository.py:1179`, `postgres_repository.py:1515` | verified |
| Changing the grade later | **No path**: `set_grade` exists in both repositories but nothing calls it | `sqlite_repository.py:3279`, `postgres_repository.py:3859` | read |
| Enrolment | `POST /api/student/enroll` checks only that the course exists. A grade-6 student enrols in `calculo_diferencial` (Universidad) and in `algebra_semillero_11` → 201 | `api/routers/student.py:295` | verified |
| Enrolment by invite code | Cross-level by design (the teacher's group course); no grade check. **Every valid code answers 500**: the router reads `group["id"]`, but `get_group_by_invite_code` (both repositories) returns `group_id`, so no student can use an invitation through V2 — `main` has the same code | `api/routers/student.py` `enroll-by-code` | verified (both engines) |
| Practice | `next-question`, `answer` and `diagnostic/{course}` work on any course, enrolled or not. A colegio student with no enrolment answered a `probabilidad` (Universidad) item and got a stored rating of 1018 there, outside their current context → **F-4** | `api/routers/student.py:105` | verified |
| Ratings context | `in_catalogue(semillero, grade=None, …)` is true for every semillero course | `src/domain/entities.py:45` | read |
| V1 (frozen) | Filters enrolments by `block == 'Semillero {grade}°'`, but also shows any enrolment made through a group | `student_view.py:166` | read |
| Data | In the legacy-data simulation every semillero student has a grade. The production count is unknown (§ 3) | — | — |

Exercise selection inside a course uses the topic or course rating (spec 001 FR-016–019,
FR-029a). The grade decides **which courses** are offered and, through the catalogue, which count
as current for the overall rating and rankings (FR-028a–c).

## 2. Owner decisions (2026-10-08) and where they are written

| # | Decision | Spec 001 |
|---|---|---|
| 1 | Semillero requires a grade from 6 to 11. Its catalogue is exactly the six courses of that grade. The API rejects a registration without a grade, and `/enroll` checks the catalogue on **every** level | FR-028k, FR-028m; US7-AS1 … AS3 |
| 2 | Invitations keep their cross-level purpose but require a grade from a semillero student. They change neither level nor grade, and the invited course never joins the catalogue or the overall rating | FR-028l; US7-AS4, AS5 |
| 3 | Existing semillero students without a grade are never given one automatically; the way to set it is documented before any of them is left with an empty catalogue | Clarifications 2026-10-08; § 3 below |
| 4 | The block constraint is not touched when it already accepts the four blocks the code writes; existing extra values stay. Widening for an old database needs the exact DDL and its R8 justification first: widening alone does not justify a `DROP` | FR-028n; § 4 below |
| 5 | An old database whose constraint lacks one of the four blocks stops the migration with a clear error; the destructive automatic widenings are removed. Any manual repair is prepared and reviewed separately, with a backup — this decision does not authorise running it | FR-028n; § 4.3 |
| 6 | A semillero student without a grade sees «Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu docente o al administrador.» No grade is assigned automatically, and valid invitation access is never blocked: the courses they are enrolled in stay listed and open | FR-028o, FR-028l; US7-AS5, AS6 |
| — | Practice access (`next-question`, `/answer`, the diagnostic) → **F-4**, its own amendment and PRs, pending before the production switch | roadmap F-4 |
| — | Grade change / promotion → spec 004 | Out of Scope |

## 3. Semillero accounts without a grade (decision 3)

Done by the owner **before F-1 is deployed**. Until then the old behaviour (all 36 courses)
still applies to these accounts, so nobody is left with an empty catalogue unannounced.

1. **Count and list them**, read-only, on production (an `ops/transfer-dbcheck`-style job or the
   Supabase SQL editor):

   ```sql
   SELECT u.id, u.username, u.created_at,
          string_agg(e.course_id, ', ' ORDER BY e.course_id) AS enrolled_courses
     FROM users u
     LEFT JOIN enrollments e ON e.user_id = u.id
    WHERE u.role = 'student' AND u.education_level = 'semillero'
      AND (u.grade IS NULL OR u.grade = '')
    GROUP BY u.id, u.username, u.created_at
    ORDER BY u.id;
   ```

2. **Decide each grade with the student or their teacher.** The grade is never inferred, not even
   from the courses the student is enrolled in.

3. **Set it, one account at a time**, in the Supabase SQL editor. `users.grade` is `TEXT`, and the
   value is one of `'6'` … `'11'`:

   ```sql
   BEGIN;
   UPDATE users SET grade = '7'
    WHERE id = 123
      AND role = 'student' AND education_level = 'semillero'
      AND (grade IS NULL OR grade = '');
   -- expect "UPDATE 1"; anything else → ROLLBACK
   COMMIT;
   ```

   No rating moves. After F-1 the account's catalogue is its grade's six courses. Enrolments in
   other grades' courses stay, shown as history and never counted (FR-028c).

4. **Re-run step 1.** Deploy F-1 when it returns no rows, or when the owner accepts the accounts
   that remain. Those see an empty catalogue and "pending diagnostic" until their grade is set the
   same way.

A screen to change the grade, which promotion also needs, belongs to spec 004.

*Optional, if the owner wants it in F-1:* the V2 catalogue screen could explain an empty
semillero catalogue ("your account has no grade; ask your teacher"). It is frontend only, since
`/api/auth/me` already returns the level and grade.

## 4. The `courses.block` CHECK (decision 4)

### 4.1 Today

| Engine | Constraint | Migration guard |
|---|---|---|
| SQLite | `block IN ('Universidad','Colegio','Concursos','Semillero')` | Probes an `INSERT … 'Semillero'`; if accepted, does nothing. Otherwise **rebuilds the table**: rename, create, copy, `DROP TABLE _courses_old` (`sqlite_repository.py:915`) |
| PostgreSQL | `block IN ('Universidad','Colegio','Concursos','Semillero', 'Semillero' ×5, 'Semillero 11°')` | Returns only if the definition contains `'Semillero 6'`, which it never does: **every migration drops and re-adds the constraint** (`postgres_repository.py:1244`; the constraint's oid changed on each of two consecutive `migrate.py` runs). Production runs `main`, whose code (`main:postgres_repository.py:995`) re-creates this same list on every start |

F-1 needs **no new value**. Every semillero course is `'Semillero'`, and the grade comes from the
id.

### 4.2 Approved: no change when the four blocks are accepted

- Each engine checks, **read-only**, whether its constraint already accepts the four blocks the
  code writes (`'Universidad'`, `'Colegio'`, `'Concursos'`, `'Semillero'`):
  - PostgreSQL: the text of `pg_get_constraintdef`;
  - SQLite: the `CREATE TABLE` text in `sqlite_master`. This replaces the probe insert.
- If it does, the migration issues **no DDL**.
- Extra values that are already allowed (`'Semillero 11°'` on PostgreSQL) stay; no code writes
  them.
- New PostgreSQL databases get the de-duplicated list with the **same allowed set**, so a fresh
  database and an existing one accept exactly the same values.
- Parity is proven by a two-engine test:
  - the four blocks are accepted;
  - `'Semillero 6°'`, which no code writes, is rejected;
  - two migrations leave the PostgreSQL constraint's oid unchanged. **Today it changes.**

### 4.3 Old databases lacking one of the four: exact DDL and R8

**PostgreSQL** cannot change a CHECK in place. `ALTER CONSTRAINT` only changes deferrability, and
a second, wider CHECK widens nothing, because every CHECK must hold. The only widening is:

```sql
-- 1. read what is allowed today
SELECT pg_get_constraintdef(oid) FROM pg_constraint
 WHERE conname = 'courses_block_check' AND conrelid = 'courses'::regclass;
-- 2. replace it with every value already allowed plus the missing ones
BEGIN;
ALTER TABLE courses DROP CONSTRAINT courses_block_check;
ALTER TABLE courses ADD CONSTRAINT courses_block_check
  CHECK (block IN (/* every value from step 1 */, /* the missing ones */));
COMMIT;
```

**SQLite** cannot alter a constraint at all; the only way is today's rebuild:

```sql
BEGIN IMMEDIATE;
ALTER TABLE courses RENAME TO _courses_old;
CREATE TABLE courses (
  id TEXT PRIMARY KEY, name TEXT NOT NULL,
  block TEXT NOT NULL CHECK (block IN ('Universidad','Colegio','Concursos','Semillero')),
  description TEXT DEFAULT '');
INSERT INTO courses (id, name, block, description)
  SELECT id, name, block, description FROM _courses_old;
DROP TABLE _courses_old;
COMMIT;
```

This is also unsafe as written. On SQLite ≥ 3.26 the `RENAME` rewrites the other tables' foreign
keys to `"_courses_old"`; that table is then dropped, leaving `enrollments`, `items` and the rest
referencing a missing table (reproduced on SQLite 3.45).

**R8 assessment.** Both are a `DROP` (of a constraint, of a table); neither is additive, so
neither may run automatically.

**Approved 2026-10-08 (decision 5):**
- Remove both automatic widening paths.
- On a database whose constraint lacks one of the four values, the migration **stops with an
  error** naming the missing values and pointing here:
  - `scripts/migrate.py` exits 1 and the API does not start (R17);
  - SQLite's in-process bootstrap raises.
- Any repair is prepared and reviewed as its own change, with a backup; the DDL above documents
  what such a repair involves and is **not** authorised by this decision. For SQLite the safe fix
  is a new local database, since SQLite holds only local or test data.
- No known database needs it:
  - test databases are created with the four values;
  - production re-creates them on every start (confirm read-only with step 1 before shipping).

The error names the missing values and this section, for example:
`courses_block_check does not accept 'Semillero'; the migration changed nothing. See
docs/sdd/f1-semillero-survey.md § 4.3.`

## 5. Tests, written first (each fails on `9546ab5`)

| Test | Engines | Today | Covers |
|---|---|---|---|
| `in_catalogue` table: level × grade 6 … 11 × own-grade / other-grade / other-level course; semillero without grade → no course | domain | grade-less case differs | FR-028k |
| A grade-*g* catalogue is exactly the six `*_semillero_g` courses (*g* = 6 … 11); grade-less → empty; other levels unchanged | SQLite + PostgreSQL | 0 courses | FR-028k, US7-AS1, US7-AS5 |
| `GET /api/student/courses` for grade 7 → the six grade-7 courses | API | 0 courses | US7-AS1 |
| Registration as semillero without grade, or with grade 5 / 12 → rejected, no account; `register_user` rejects it on both engines | API + both engines | 201 / accepted | FR-028m, US7-AS2 |
| `/enroll` outside the catalogue (colegio → universidad; grade 6 → grade 7) → rejected, nothing enrolled; inside → 201 | API | 201 for both | FR-028m, US7-AS3 |
| Invitation to a colegio group by a grade-6 student → enrolled, can practise; level and grade unchanged; not current; overall rating unchanged | API + both engines | partly holds | FR-028l, US7-AS4 |
| Invitation for a semillero account without grade → refused; its catalogue is empty and its rating "pending diagnostic" | API | accepted | FR-028l, US7-AS5 |
| Block constraint: four accepted, `'Semillero 6°'` rejected; PostgreSQL oid stable over two migrations | both engines | oid changes | § 4.2 |
| A database lacking `'Semillero'` → migration stops with the documented error naming it; constraint and table unchanged; `migrate.py` exits 1 | both engines | rebuilds / drops | FR-028n, § 4.3 |
| `GET /api/student/courses` lists an invited course as enrolled and `in_catalogue: false`; a grade-less semillero student gets only their enrolments | API | invited course missing; 36 courses | FR-028l, FR-028o, US7-AS5, AS6 |
| Courses screen: the notice for a grade-less semillero student, enrolled courses still listed; invited course only under *Mis matrículas* | Playwright | 36 courses offered | FR-028o, US7-AS5, AS6 |

## 6. How it ships

1. **This docs PR**: the spec 001 amendments, the tasks (`specs/001-elo-engine/tasks.md` Phase 12)
   and this survey. The owner merges it.
2. **Code PR** from `fix/f1-semillero-catalogue`:
   - tests first, as above;
   - the `PENDING` rows replaced by the tests that cover them;
   - full suite on PostgreSQL, `db_sync_check.py`, the traceability check;
   - `scripts/rehearse_migration.py` on the legacy-data simulation, showing that the second
     migration issues no DDL.
3. **Before deploying**: the owner runs § 3 and the read-only constraint check of § 4.3 step 1 on
   production.

**Traceability check (A-2, PR #5):** it no longer depends on the branch name. A PR that changes
any path in spec 001's *Code Scope*, or a test its Traceability cites, is a code change for spec
001 and fails while any spec 001 row is `PENDING`. So F-1's code PR must clear every row above,
and once A-2 is merged, no other PR may change spec 001's code while these rows are `PENDING` on
its base — F-4's code PR included. Merge order: § 7.

## 7. Order with F-4 and the production switch

Once the traceability check (A-2, PR #5) is merged, it judges each PR by spec, not by row: while
spec 001 has a `PENDING` row on the base branch, every PR that changes spec 001's code fails until
the PR that closes them lands. Consequences:

- F-4 (needed before the switch) and F-1 should not have their docs merged at the same time; the
  order that keeps each code PR green is **F-4 docs → F-4 code → this docs PR → F-1 code**.
- PR #5 is planned to merge after the switch, so it does not gate PR #3. Merging this docs PR
  before the switch is still allowed by the process (a docs PR may carry `PENDING`), but F-1's
  code then reaches production only with the read-only checks of § 3 and § 4.3 step 1 done first.
