# Feature Specification: ELO Engine

**Feature Branch**: `001-elo-engine`
**Created**: 2026-10-05
**Status**: Draft (as-is, brownfield)
**Input**: Reverse-engineered from the code on `main @ cf88c55` and `docs/sdd/elo-survey.md`.
Describes how a student's rating is created, updated and read, how items self-calibrate, how the
next practice item is chosen, and every path that writes a rating.

**Outcome served** (constitution VIII): the rating is how Oulad decides what a student practises
next and how a teacher reads a student's level. If it is wrong, students get items that are too
easy or too hard and teachers act on false information.

## Clarifications

### Session 2026-10-05 (during /speckit-specify)

- Q: What is the canonical rating key (D-1)? → A: one rating per topic; a course rating is the
  derived average of its topics, never stored (FR-029, FR-029a).
- Q: Which rank scale is shared by every surface? → A: the student API's 16 levels "Aspirante →
  Leyenda Suprema"; the diagnostic league stays a separate placement label (FR-031, FR-031a).
- Q: Which topics receive a PvP delta? → A: every topic the player has rated in the match's
  course, shifted by the full delta, so the course average moves by exactly the delta (FR-029b).

### Session 2026-10-06 (/speckit-plan, data contradiction found)

- Q: Is a topic rating per topic name across courses, or per topic within one course? → A: per
  course and topic. Courses are separate contexts (e.g. "Álgebra Básica" is a course level, not a
  topic; "Geometría" in grade 6 and grade 7 are different courses a student is promoted through).
  Identity uses stable course and topic identifiers; labels may coincide (FR-029, FR-029a,
  FR-033 … FR-036 rewritten).
- Q: After promotion, do previous-grade courses count in the overall rating? → A: no — only
  enrolled courses of the current level and grade with rated topics, weighted equally; earlier
  courses kept as history; no ratings yet → "pending diagnostic"; a lower number after promotion
  is a new-context baseline, never shown as a loss (FR-028a, FR-028b, FR-028c).
- Q: How certain are migrated legacy values? → A: attempts/diagnostics only establish which
  contexts are eligible; migrated values are approximate baselines with recorded provenance,
  never described as exact recovery; a legacy row with no eligible context stays unassigned and
  the diagnostic initializes (FR-034, FR-034a, FR-034b).

### Session 2026-10-06 (/speckit-analyze remediation, owner + expert review)

- Q: What ranks a group? → A: precedence — an explicitly requested, validated and authorized
  course; otherwise the group's course; otherwise the overall rating. One basis per list, applied
  to every participant and shown in the response/UI; students without a rating on that basis are
  listed last as "pending diagnostic", never ranked on another rating (FR-028d, FR-028f).
- Q: How are ties and positions decided? → A: one explicit tie rule; a position is the index in
  the same ordered list the ranking returns (FR-028h). *(Superseded the same day — next bullet.)*
- Q: Do equal ratings share a rank? → A: yes — competition ranking (1, 2, 2, 4). Ratings are
  compared at the precision the UI displays them; attempt count is never a tie-breaker; user id
  only orders display within a tie and never changes the shared rank; pending-diagnostic students
  come last with no numeric rank (FR-028h, US6-AS8).
- Q: At what precision are ranking ratings compared and shown? → A: whole numbers
  (`RATING_DISPLAY_DECIMALS = 0`). Stored ratings, rating updates and intermediate averages keep
  full precision; only the final derived rating used for ranking comparison and display is rounded,
  by one backend rule (half up on the decimal value: 1199.5 → 1200, 1200.5 → 1201), and clients show
  the returned value without rounding it again (FR-028h, FR-028i).
- Q: Must a rating and its rank label agree when shown together outside rankings? → A: yes —
  wherever a current rating and its rank label appear together, both derive from the same
  backend-rounded display value (half up); full precision stays in storage and calculations
  (FR-028j; boundary 999.6 → "1000", "Plata I").
- Q: Where may rating arithmetic live? → A: calculations in the domain; orchestration in one
  application read service; participant selection and raw rows in repositories. Adding a
  domain-computed delta atomically in SQL is persistence, not arithmetic (plan, research R3).

### Session 2026-10-07 (/speckit-implement, Phase 2 pin review, owner decision)

- Q: Is an explicit response time of 0 s a missing value or an invalid one? → A: invalid. The
  attempt is recorded; the student's rating and uncertainty and the item's difficulty stay
  unchanged. Only an absent value is treated as 30 s (FR-008a). *(Found while pinning FR-008:
  today an explicit 0 is read as absent and moves the rating.)*
- Q: How precise must stored ratings be on PostgreSQL? → A: as precise as on SQLite — the rating
  and uncertainty columns of the new table are `DOUBLE PRECISION` on PostgreSQL (SQLite `REAL` is
  already 8 bytes), so a stored value displays the same number and rank label on both engines
  (FR-028i; 999.4999999 → 999 "Plata II" on both). *(PostgreSQL `REAL` stores it as 999.5, which
  displays 1000 "Plata I".)*
- Q: With a retry key, which values does an answer return, given that PostgreSQL stores attempt
  values in 4 bytes? → A: the persisted attempt values, on the first response and on every retry,
  so both are identical; the stored rating and every later calculation keep full precision and are
  never derived from the persisted attempt values (FR-012a). Widening the attempt columns was
  rejected: it is a type change (AGENTS R8). *(Found at the Phase 3 checkpoint: a first response of
  1243.66 and a retry of 1243.67.)*

### Session 2026-10-08 (follow-up F-1, owner decisions)

Found while surveying roadmap follow-up F-1 (`docs/sdd/f1-semillero-survey.md`): a semillero
student with a grade was offered no course, one without a grade was offered all 36, registration
accepted semillero without a grade and `/enroll` accepted any existing course.

- Q: Does a semillero student need a grade? → A: yes, a grade from 6 to 11 is mandatory; a
  registration without one is rejected, and the catalogue is exactly the six semillero courses of
  that grade (FR-028k, FR-028m).
- Q: Which courses may a student enrol in? → A: only the courses of their catalogue, on every
  level; any other enrolment request is rejected (FR-028m).
- Q: What do teacher invitations do? → A: they keep their purpose, explicit access to the group's
  course across levels, but a semillero student needs a grade to use one. An invitation never
  changes the student's level or grade, and the invited course does not become part of the
  catalogue, so it never counts toward the overall rating (FR-028l).
- Q: What about existing semillero students without a grade? → A: no grade is assigned
  automatically. Before the change ships they are counted and given their grade by the documented
  procedure (`docs/sdd/f1-semillero-survey.md` § 3); any account still without a grade has an
  empty catalogue, no current course and a "pending diagnostic" rating (FR-028k, FR-028b).
- Q: Who changes a student's grade later (promotion)? → A: out of this spec — spec 004
  (identity and access); FR-028c already defines what promotion does to ratings.
- Q: What does a semillero student without a grade see? → A: an empty catalogue with the notice
  «Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu docente o al
  administrador.» No grade is assigned automatically, and the courses they are already enrolled
  in — including any reached by a valid invitation — stay listed and open for practice (FR-028o).
- Q: Where does a course reached by invitation appear? → A: among the student's enrolments,
  marked as outside the catalogue; it is never offered in the catalogue to explore (FR-028l).
- Q: What if an old database's `courses.block` constraint does not accept one of the four
  blocks? → A: the migration stops with a clear error naming the missing values and changes
  nothing; the automatic widenings (PostgreSQL drop and re-add, SQLite table rebuild) are removed.
  Any manual repair is prepared and reviewed separately, with a backup; this decision does not
  authorise running that DDL (FR-028n, `docs/sdd/f1-semillero-survey.md` § 4.3).

### Session 2026-10-05 (/speckit-clarify)

- Q: What happens to ratings already stored under a course id or course name? → A: existing topic
  ratings are preserved; a missing topic rating is initialized only for topics the student
  actually practised, from the legacy course rating as an approximate baseline; legacy rows are
  kept but excluded from active reads and averages; the migration is idempotent; if both a
  course-id and a course-name row exist, a deterministic rule picks one and they are never added
  together; historical attempts are not replayed (FR-033 … FR-036).
- Q: Is the overall rating the mean of topic ratings or of course ratings? → A: mean of course
  ratings, each the mean of its existing topic ratings; unrated topics, courses with no rated
  topic and legacy rows excluded; recorded as [CHANGE] (FR-028a). *(Fallback refined on
  2026-10-06: "pending diagnostic" instead of 1000.)*
- Q: What does a PvP result do to a player with no rated topic in the course? → A: their ratings
  stay unchanged; an applied delta of 0 is persisted with reason `no_rated_topics` and reported;
  the opponent's delta applies normally; completion stays idempotent; matchmaking eligibility is
  a follow-up for spec 007 (FR-029c).

### Session 2026-10-08 (follow-up F-4, owner decisions)

Found while surveying follow-up F-1 (`docs/sdd/f1-semillero-survey.md` § 1): `next-question`,
`/answer` and the diagnostic endpoints worked on any course. A colegio student with no enrolment
was served a `probabilidad` (universidad) item and its answer stored a rating of 1018 there.

- Q: Which practice endpoints check enrolment? → A: all three doors — the next practice item, the
  practice answer and the diagnostic (its status and questions, and its submission) (FR-037,
  FR-037a).
- Q: What counts as enrolled? → A: any enrolment of the student in that course, from their
  level's courses or through a valid invitation code; an invitation course is practised like any
  other.
- Q: When is a request refused? → A: before any item is served and before any rating, attempt,
  item difficulty, retry record or diagnostic result is read for update or written; a refused
  request changes nothing (FR-037a).
- Q: How is it tested? → A: allowed and denied access, the denied side with no side effect
  (US8-AS1 … AS5).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A practice answer updates my rating correctly (Priority: P1)

A student answers a practice item. Their rating for that course moves up when they answer
correctly and down when they answer incorrectly, by an amount that depends on how surprising the
result was and how settled their rating already is. The item's difficulty moves the opposite way.

**Why this priority**: this is the core loop of the product; every other feature reads its result.

**Independent Test**: submit answers for one student on one item and compare the stored rating,
uncertainty and item difficulty with the formulas in FR-001…FR-006.

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a student with no rating for the item's topic, **When** they answer an item
   of difficulty 1000 correctly in 20 s, **Then** their rating becomes 1016.00 (1000 + 32 × 1 ×
   (1 − 0.5)), their uncertainty becomes 332.5, and the item's difficulty becomes 984.
2. **US1-AS2** — **Given** the same starting point, **When** they answer incorrectly in 20 s,
   **Then** their rating becomes 984.00 and the item's difficulty becomes 1016.
3. **US1-AS3** — **Given** a student, **When** they answer in 2 s (or 601 s), **Then** the
   attempt is recorded and neither their rating, their uncertainty nor the item's difficulty
   changes.
4. **US1-AS4** — **Given** an answer already accepted with a retry key, **When** the same request
   is sent again with the same key, **Then** the original result is returned and nothing changes
   a second time.
5. **US1-AS5** — **Given** a retry key already used for a different answer, **When** it is
   reused, **Then** the request is rejected as a conflict.
6. **US1-AS6** — **Given** eight answers from the same student arriving at the same moment,
   **When** all complete, **Then** the final rating equals applying them one after another
   (no update is lost).
7. **US1-AS7** — **Given** a client that submits an answer for an item with a difficulty, topic
   or option set of its own, **When** the answer is processed, **Then** the stored item data is
   used and an option that does not belong to the item is rejected.

---

### User Story 2 - The next item fits my level (Priority: P1)

A student asks for the next practice item. They get one they have a reasonable chance of
answering — not trivial, not hopeless — preferring items they have not seen yet.

**Why this priority**: adaptive selection is the product's promise; it consumes US1's rating.

**Independent Test**: with a fixed item pool and a fixed random seed, request items for a given
rating and history and check which items are eligible and which one is chosen.

**Acceptance Scenarios**:

1. **US2-AS1** — **Given** a rating of 1000 and items of difficulty 600, 950, 1100 and 1600,
   **When** the next item is requested, **Then** it is 950: 600 and 1600 are more than 250 away,
   and 1100 gives a success chance of 0.36, outside the 0.40–0.75 band (950 gives 0.57).
2. **US2-AS2** — **Given** no item inside the 40–75 % band, **When** the next item is requested,
   **Then** the band widens by 5 points on each side, up to 10 times, and then falls back to the
   whole pool.
3. **US2-AS3** — **Given** unseen items exist, **When** the next item is requested, **Then** it is
   unseen; only when none remain does an item failed this session at least 3 questions ago become
   eligible, and only then a previously answered one.
4. **US2-AS4** — **Given** an item answered correctly in this session, **When** the next item is
   requested, **Then** it is never offered again in this session.
5. **US2-AS5** — **Given** every eligible item is exhausted and the rating is at least 1800,
   **When** the next item is requested, **Then** the student is told they have reached mastery.

---

### User Story 3 - The diagnostic sets my starting point (Priority: P2)

A student takes the course diagnostic. Their starting rating per topic reflects how they did,
without ever erasing progress they already made in practice.

**Why this priority**: it removes the cold start, but only once per course.

**Independent Test**: submit a diagnostic with known answers and check the starting ratings.

**Acceptance Scenarios**:

1. **US3-AS1** — **Given** no practice yet, **When** the student answers a diagnostic item of
   difficulty 1200 correctly, **Then** that topic's starting rating rises by 22 from 1000 (14
   below difficulty 1100, 34 at 1450 or above; wrong answers −20 / −12 / −6 respectively).
2. **US3-AS2** — **Given** a very poor diagnostic, **When** it is scored, **Then** no starting
   rating is set below 760.
3. **US3-AS3** — **Given** the student already practised a topic, **When** they retake the
   diagnostic, **Then** that topic's rating is not overwritten.
4. **US3-AS4** — **Given** a skipped question ("I don't know"), **When** it is scored, **Then** it
   does not change the rating.

---

### User Story 4 - A teacher's grade on my procedure adjusts my rating once (Priority: P2)

A teacher grades a handwritten procedure. The student's rating moves by a small amount tied to the
grade, exactly once. An AI-proposed grade never moves it.

**Why this priority**: it rewards reasoning, not just the final answer, and it is the teacher's
authority (constitution, Domain Rules).

**Independent Test**: validate one submission, then try to validate it again; compare ratings.

**Acceptance Scenarios**:

1. **US4-AS1** — **Given** a pending submission, **When** the teacher grades it 80/100, **Then**
   the student's rating rises by 6 ((80 − 50) × 0.2).
2. **US4-AS2** — **Given** an already graded submission, **When** a second validation is
   attempted, **Then** the rating does not change again.
3. **US4-AS3** — **Given** an AI-proposed score on a submission, **When** it is stored, **Then**
   the rating does not change.
4. **US4-AS4** — **Given** a teacher who does not own the student's group, **When** they try to
   validate, **Then** nothing changes.
5. **US4-AS5** — **Given** a grade outside 0–100, **When** it is submitted, **Then** it is
   rejected.

---

### User Story 5 - A finished PvP match adjusts my rating once (Priority: P3)

Two students finish a match. The winner gains and the loser loses rating (or both move toward
each other on a draw), exactly once, and the change persists.

**Why this priority**: secondary mode; the lobby itself belongs to spec 007.

**Independent Test**: finish a match twice (timer and last answer at once); compare ratings.

**Acceptance Scenarios**:

1. **US5-AS1** — **Given** two players with equal ratings, **When** one wins, **Then** the winner
   gains 12 and the loser loses 12 (K = 24).
2. **US5-AS2** — **Given** a match that is closed twice, **When** both closes complete, **Then**
   the change is applied once.
3. **US5-AS3** — **Given** a match left active by a restart, **When** it is expired, **Then** it is
   marked abandoned and no rating changes.
4. **US5-AS4** — **Given** a finished match, **When** the player answers their next practice item,
   **Then** the match's change is still reflected in their rating.
5. **US5-AS5** — **Given** a player with no rated topic in the match's course, **When** the match
   finishes, **Then** their ratings are unchanged, the match records and reports an applied change
   of 0 with reason `no_rated_topics`, and the opponent's change is applied.

---

### User Story 6 - My rating reads the same everywhere (Priority: P3)

A student or teacher looks at a rating, a predicted change, or a rank. The same underlying rating
gives the same number and the same rank on every screen.

**Why this priority**: trust; this is where the current drift is (D-1, D-2, rank tables).

**Independent Test**: for one student, compare the rating, preview and rank on every surface that
shows them.

**Acceptance Scenarios**:

1. **US6-AS1** — **Given** a student of the current level and grade with topic ratings 1100 and
   1300 in course X and 1000 in course Y, **When** their overall rating is shown, **Then** it is
   1100 — the mean of course X (1200) and course Y (1000), not the mean of the three topics
   (1133.33).
2. **US6-AS2** — **Given** a student about to answer, **When** the predicted gain/loss is shown,
   **Then** it equals the change the engine applies for that answer at that moment.
3. **US6-AS3** — **Given** one rating, **When** its rank is shown on any surface, **Then** it is
   the same rank.
4. **US6-AS4** — **Given** an exam submission, **When** it is graded, **Then** no rating changes.
5. **US6-AS5** — **Given** a student just promoted to a grade whose courses have no rated topic,
   **When** their overall rating is shown, **Then** it reads "pending diagnostic", not a number,
   and no negative change is shown.
6. **US6-AS6** — **Given** a promoted student whose new-grade diagnostic gives an overall rating
   lower than before, **When** it is shown, **Then** no loss or negative delta is shown, and the
   previous grade's course ratings remain viewable unchanged.
7. **US6-AS7** — **Given** a group tied to course C whose members are A (C rating 1200),
   B (C rating 1100, overall 1500) and D (no rating in C), **When** the group ranking is shown
   without a requested course, **Then** the basis shown is "course C (group)", the order is A, B,
   then D marked "pending diagnostic", and B is not ranked by its overall rating.
8. **US6-AS8** — **Given** ratings on the ranking's basis that are, after rounding to the display
   precision, 1250, 1200, 1200 and 1150, plus one pending student, **When** the ranking and each
   student's own rank are shown, **Then** the ranks are 1, 2, 2, 4; the two tied students appear in
   user-id order with the same rank; attempt counts do not affect the order; the pending student is
   last with no numeric rank; and each student's own rank equals the rank on their list entry.
9. **US6-AS9** — **Given** a student whose full-precision overall rating is 999.6, **When** it is
   shown on the student stats screen, the teacher dashboard, the teacher student report and a
   ranking, **Then** every surface shows 1000 with "Plata I"; for 999.4 every surface shows 999
   with "Plata II"; the stored rating stays 999.6 / 999.4.

---

### User Story 7 - My catalogue matches my level and grade (Priority: P2)

A student sees, and can enrol in, the courses of their education level — for semillero, of their
grade — and those are the courses whose ratings make up their overall rating. A teacher's
invitation can open a course of another level without changing either.

**Why this priority**: today a semillero student with a grade is offered no course at all, and the
courses offered and the courses counted in the overall rating come from two different rules.

**Independent Test**: register students of each level (semillero with each grade), list their
catalogue, try to enrol inside and outside it, join a group of another level by invitation, and
compare the overall rating before and after.

**Acceptance Scenarios**:

1. **US7-AS1** — **Given** a semillero student of grade 7, **When** their catalogue is shown,
   **Then** it is exactly the six grade-7 semillero courses, and those are the courses that count
   as current for their overall rating.
2. **US7-AS2** — **Given** a registration as a semillero student without a grade, or with a grade
   outside 6–11, **When** it is submitted, **Then** it is rejected and no account is created.
3. **US7-AS3** — **Given** a colegio student and a grade-6 semillero student, **When** they ask to
   enrol in a universidad course and in a grade-7 semillero course respectively, **Then** both
   requests are rejected and nothing is enrolled; a course of their own catalogue enrols normally.
4. **US7-AS4** — **Given** a grade-6 semillero student with an overall rating, **When** they join,
   through its invitation code, a group whose course is a colegio course, **Then** they are
   enrolled in it and can practise it; their level and grade stay the same; the course is not in
   their catalogue; and their overall rating is still computed from their grade-6 courses only.
5. **US7-AS5** — **Given** a semillero student without a grade (an account created before this
   rule), **When** their catalogue and overall rating are shown, **Then** the catalogue is empty
   and the screen shows «Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu
   docente o al administrador.», the rating reads "pending diagnostic", a new invitation code is
   refused until a grade is set, and the courses they are already enrolled in stay listed and
   open for practice.
6. **US7-AS6** — **Given** a colegio student enrolled by invitation in a universidad course,
   **When** their courses are listed, **Then** the course appears among their enrolments marked
   as outside the catalogue, is not offered in the catalogue to explore, and opens for practice.

---

### User Story 8 - I practise only the courses I am enrolled in (Priority: P1)

A student gets practice items, answers them and takes a course's diagnostic only in the courses
they are enrolled in — through their catalogue or through a teacher's invitation. Any other
course is refused before anything is served or stored.

**Why this priority**: today any signed-in student can be served items, answer them and set a
diagnostic baseline in any course, so ratings appear in courses the student never joined and
change what teachers and rankings read.

**Independent Test**: with one student enrolled through the catalogue, one through an invitation
and one not enrolled, request the next item, answer one, open and submit the diagnostic of the
same course; compare attempts, ratings, item difficulty and diagnostics before and after.

**Acceptance Scenarios**:

1. **US8-AS1** — **Given** a colegio student not enrolled in `probabilidad`, **When** they ask for
   its next practice item, **Then** the request is refused as forbidden and no item is served.
2. **US8-AS2** — **Given** that student and an item of `probabilidad`, **When** they submit an
   answer to it, with or without a retry key, **Then** it is refused as forbidden and no attempt,
   rating, item difficulty or retry record changes.
3. **US8-AS3** — **Given** that student, **When** they open `probabilidad`'s diagnostic or submit
   one, **Then** both are refused as forbidden: no question is served and no baseline or
   diagnostic result is stored.
4. **US8-AS4** — **Given** a student enrolled in a course of their catalogue and another enrolled
   through an invitation in a course outside their level, **When** each asks for that course's
   next item, answers it and takes its diagnostic, **Then** all of it works as today for both.
5. **US8-AS5** — **Given** a student who practised a course and then left it, **When** they ask
   for its next item or answer one of its items, **Then** it is refused as forbidden and their
   stored ratings in that course stay unchanged.

---

### Edge Cases

- Response time exactly 3 s or exactly 600 s → valid (inclusive bounds).
- Missing response time → treated as 30 s (valid).
- An explicit response time of 0 s → invalid: recorded, nothing moves; not treated as missing
  (FR-008a).
- Uncertainty already at the floor (30) → stays at 30; changes are 32 × 30/350 ≈ 2.7 × surprise.
- A teacher grade of 50 → zero change, but the submission is still marked as applied.
- Procedure change on a topic with no rating → starts from 1000 and never goes below 0.
- Course with no rated topics → selection and PvP expectation use 1000; every display shows
  "pending diagnostic" (FR-029a).
- Requested ranking course that does not exist → rejected; one the requester may not see →
  refused (FR-028d).
- A list limit that cuts through a tie → the shown entries keep their shared rank; ranks are never
  recomputed for the shortened list (FR-028h).
- Two ratings that differ only below the display precision → they tie (FR-028h).
- A rating just below a rank threshold that displays at the threshold (999.6 → 1000) → the label
  is the threshold's ("Plata I"), matching the number shown (FR-028j).
- A stored rating of 999.4999999 → 999 with "Plata II" on both databases; storage never turns it
  into 999.5 (FR-028i).
- A rating of exactly n.5 → rounds up to n + 1 for display and ranking (FR-028i); intermediate averages are
  never rounded, so topics 1200.4, 1200.4, 1201.4 give a course ranking value of 1201, not 1200.
- Legacy row with no eligible context → kept unassigned and excluded; the diagnostic initializes.
- Promotion → the overall rating switches to the new grade's courses; until one has a rated topic
  it reads "pending diagnostic".
- Two items with the same difficulty → the chosen one is kept by identity, not by difficulty.
- Practice filtered to a topic that has no items → falls back to the whole course pool.
- Practice, an answer or a diagnostic for a course that does not exist → refused like a course the
  student is not enrolled in (FR-037).
- A retry of an accepted answer after the student left the course → refused like any answer; the
  stored attempt stays as it was (FR-037a).
- A retry key longer than 128 characters or empty → rejected.
- A diagnostic containing the same item twice, or an item from another course → rejected.
- An invitation to a course that is already in the student's catalogue → an ordinary enrolment:
  the course counts as current (FR-028l only covers courses outside the catalogue).
- A semillero course of another grade reached by invitation → accessible, never current; the
  student's grade does not change (FR-028l).
- A semillero account without a grade → empty catalogue, the notice of FR-028o and "pending
  diagnostic" until its grade is set; no grade is inferred from its enrolments (FR-028k). Its
  existing enrolments are not removed: they stay listed and open for practice, and none counts as
  current.
- A database whose block constraint lacks one of the four blocks → the migration stops before
  changing anything, naming the missing values (FR-028n); one that accepts the four plus extra
  values → no DDL, the extra values stay.

## Requirements *(mandatory)*

### Functional Requirements

**Answer update (US1)**

- **FR-001** [AS-IS]: When a student's valid practice answer is processed, the system shall
  compute the expected success as `P = 1 / (1 + 10^((D − R) / 400))`, where R is the student's
  current rating in the item's topic and D the item's current difficulty.
- **FR-002** [AS-IS]: When a valid practice answer is processed, the system shall change the
  student's rating in the item's topic by `32 × (RD / 350) × (result − P)`, with result 1 for correct and 0 for
  incorrect, and RD the student's current uncertainty.
- **FR-003** [AS-IS]: When a valid practice answer is processed, the system shall reduce the
  student's uncertainty to `max(30, RD × 0.95)`.
- **FR-004** [AS-IS]: While a student has no rating for a topic, the system shall start that topic
  from rating 1000 and uncertainty 350, unless the diagnostic set its starting point (FR-020).
  *(Today a stored course-level rating can also be seeded from the diagnostic's course average;
  that path disappears with FR-029a.)*
- **FR-005** [AS-IS]: When a valid practice answer is processed, the system shall change the item's
  difficulty by `32 × ((1 − result) − (1 − P))`.
- **FR-006** [AS-IS]: The system shall keep the item's uncertainty unchanged by answers.
- **FR-007** [AS-IS]: The system shall record every practice attempt, valid or not.
- **FR-008** [AS-IS]: If a practice answer's response time is outside 3–600 s (inclusive), then
  the system shall leave the student's rating, the student's uncertainty and the item's
  difficulty unchanged.
- **FR-008a** [CHANGE]: If a practice answer carries an explicit response time of 0 s, then the
  system shall treat it as outside the window (FR-008): record the attempt and leave the student's
  rating, the student's uncertainty and the item's difficulty unchanged. Only an absent response
  time is treated as 30 s. *(Today an explicit 0 is read as absent and moves the rating — found
  while pinning FR-008; owner decision 2026-10-07.)*
- **FR-009** [CHANGE]: If a practice answer's response time is outside 3–600 s, then the system
  shall report and record the rating as unchanged (before = after) instead of the change it did
  not apply. *(Default chosen from Principle V; today the response and the attempt log report a
  change that never happened — survey F5.)*
- **FR-010** [AS-IS]: When an answer is processed, the system shall read the rating, compute the
  change and store it as one indivisible step, so that concurrent answers from the same student
  compose as if applied one after another.
- **FR-011** [AS-IS]: When an answer arrives, the system shall take the item's difficulty, topic,
  options and correct answer from its own store, and shall reject an option that is not one of
  the item's options.
- **FR-012** [AS-IS]: When an answer carries a retry key that was already accepted for the same
  answer, the system shall return the stored result without changing anything.
- **FR-012a** [CHANGE]: When an answer carries a retry key, the system shall return the attempt
  values as persisted — before, after and uncertainty — in the first response and in every retry,
  so that the two are identical; the student's stored rating and every later calculation shall
  keep full precision and shall never be derived from those persisted attempt values. *(Today the
  first response rounds the full-precision result while a retry rounds the 4-byte value PostgreSQL
  stored, so near a rounding edge they differ by 0.01 — owner decision 2026-10-07.)*
- **FR-013** [AS-IS]: If a retry key was already accepted for a different answer, then the system
  shall reject the request as a conflict.
- **FR-014** [AS-IS]: The system shall never send the correct option to the client in an answer or
  exam response.
- **FR-015** [CHANGE]: If awarding achievements fails after an answer, then the system shall log
  the failure and still return the answer's result. *(Today the failure is silently discarded —
  Known Deviation D-3.)*

**Item selection (US2)**

In FR-016 … FR-019, "the student's rating" is the **selection rating**: the topic rating when
practising one topic, or the derived course rating (FR-029a) when practising the whole course.

- **FR-016** [AS-IS]: When the next practice item is requested, the system shall exclude items
  answered correctly in the current session and choose, in order of preference, from: items never
  answered; items failed this session at least 3 questions ago; items answered before.
- **FR-017** [AS-IS]: When choosing among eligible items, the system shall keep items within ±250
  of the student's rating (all items if none qualify), then those with expected success between
  0.40 and 0.75, widening that band by 0.05 per side up to 10 times, then all of them.
- **FR-018** [AS-IS]: When several items qualify, the system shall pick at random among those whose
  informativeness `P × (1 − P)` is at least 95 % of the best.
- **FR-019** [AS-IS]: While no eligible item remains and the student's rating is at least 1800,
  the system shall report mastery instead of an item; below 1800 it shall offer the pool again.

**Diagnostic (US3)**

- **FR-020** [AS-IS]: When a diagnostic is submitted, the system shall compute a starting rating per
  topic from 1000, adding +14/−20 (difficulty < 1100), +22/−12 (1100–1449) or +34/−6 (≥ 1450) per
  correct/incorrect answer, ignoring skipped questions, with a floor of 760.
- **FR-021** [AS-IS]: While a topic already has practice attempts, the system shall not overwrite
  its rating with a diagnostic result.

**Teacher-validated procedure (US4)**

- **FR-022** [AS-IS]: When a teacher validates a pending procedure with a grade from 0 to 100, the
  system shall add `(grade − 50) × 0.2` to the student's rating in the item's topic exactly once.
- **FR-023** [AS-IS]: If a grade is outside 0–100, or the teacher does not own the student's group,
  or the submission is not pending, then the system shall not change any rating.
- **FR-024** [AS-IS]: The system shall not change any rating from an AI-proposed procedure score.

**PvP result (US5)**

- **FR-025** [AS-IS]: When a PvP match finishes, the system shall change each player's rating by
  `24 × (outcome − expected)`, with outcome 1 / 0.5 / 0 for win / draw / loss, exactly once even if
  the match is closed more than once.
- **FR-026** [CHANGE]: When a PvP match's expected outcome is computed, the system shall use each
  player's derived rating for the match's course (FR-029a). *(Today it uses the overall average
  across all courses — survey F4.)*
- **FR-027** [AS-IS]: When the system starts and prepares its data, it shall mark every match still
  active after more than 600 s as abandoned, without changing any rating.

**Reading the rating (US6)**

- **FR-028** [AS-IS]: The system shall hold each rating in exactly one place and derive every
  aggregate from stored ratings (history rule: FR-028e).
- **FR-028a** [CHANGE]: The system shall derive a student's overall rating as the arithmetic mean,
  each course weighted equally, of the course ratings of the courses the student is enrolled in
  that belong to their **current education level and grade** and have at least one rated topic;
  each course rating is the arithmetic mean of that course's existing topic ratings (FR-029a).
  Unrated topics, courses with no rated topic, courses outside the current level and grade, and
  legacy rows (FR-036) are excluded. Course ratings are derived values, not a second source of
  rating state. *(Today: the plain mean of all stored rows, legacy rows included — so a student's
  displayed overall rating and rank may change after migration.)*
- **FR-028b** [CHANGE]: While no course of the student's current level and grade has a rated
  topic, the system shall show the overall rating and rank as "pending diagnostic" instead of a
  number.
- **FR-028c** [CHANGE]: When the student's level or grade changes, the system shall keep the
  ratings of earlier courses unchanged and viewable as history, and shall not present the
  difference between the old and the new overall rating as a rating change or loss.
- **FR-028d** [CHANGE]: When a group ranking is shown (to a student or a teacher), the system shall
  choose **one rating basis** for the whole list, in this order: (1) a course explicitly requested,
  which must exist (else rejected) and which the requester may see — for a student, a course they
  are enrolled in; for a teacher, only via a group they own (else refused); (2) otherwise the
  group's course, if the group has one; (3) otherwise the overall rating (FR-028a). Every
  participant is ranked on that basis (course rating per FR-029a), the basis is returned with the
  list and shown in the UI, and students without a rating on that basis are listed after the rated
  ones as "pending diagnostic", with no numeric rank — never ranked on a different rating. *(Today the group ranking
  averages every past attempt's rating in both engines, and its course filter does not filter —
  research R18.)*
- **FR-028e** [AS-IS]: The system shall show past per-attempt ratings only as history (student
  history, teacher rating history, exports) and shall never derive a current rating from them.
- **FR-028f** [CHANGE]: When a V1 ranking is shown or a student's rank in one is computed,
  the system shall decide **who appears** by the ranking's participation rule and **what they are
  ranked by** from the derived ratings, as follows:

  | Ranking | Who appears | Ranked by |
  |---|---|---|
  | Global | students (of the requested level and grade, when given) with ≥ 1 attempt in the last 7 days | overall rating (FR-028a) |
  | Course | students with ≥ 1 attempt on that course's items in the last 7 days | that course's rating (FR-029a) |
  | Weekly (group) | students of the group with ≥ 1 attempt in the last 7 days | the group basis of FR-028d |
  | Group (V2) | students of the group | the group basis of FR-028d |

  Students without a rating on the basis are listed last as "pending diagnostic", with no numeric
  rank. A student's rank is read from the same ranked list (FR-028h). *(Today these readers rebuild ratings
  from `attempts.elo_after` — research R18.)*
- **FR-028g** [AS-IS]: The system shall keep stored weekly ranking snapshots unchanged as history;
  a snapshot records the rating as it was when it was taken.
- **FR-028h** [CHANGE]: The system shall rank every ranking list by **competition ranking**:
  - ratings on the list's basis are compared after rounding to the **ranking display precision**,
    which is **whole numbers** — the same value every ranking surface displays (FR-028i);
  - equal rounded ratings share a rank, and the next distinct rating takes the rank equal to one
    plus the number of students ranked above it (1, 2, 2, 4);
  - attempt count is never a tie-breaker;
  - within a tie, display order is by lower user id — this never changes the shared rank;
  - pending-diagnostic students follow all rated ones, ordered by lower user id, with no numeric
    rank.

  A student's rank anywhere (list entry, own position) is the rank of their entry in that same
  list. *(Today ties fall in database order, which differs between engines, and tied students get
  different positions.)*
- **FR-028i** [CHANGE]: The system shall keep full precision in stored ratings, in rating updates
  and in every intermediate average (topic → course → overall), and shall round only a final
  derived rating that is compared in a ranking or displayed with a rank label, to a whole number,
  with a single backend rule: round half up on the value's decimal representation
  (1199.5 → 1200, 1200.5 → 1201, 1200.4999 → 1200). A ranking entry's rank label derives from that
  same displayed whole number. Clients display the returned value as given and never round it
  themselves. Stored ratings and uncertainties keep the same 8-byte floating-point precision on
  both databases, so a stored value displays the same number and label on each (999.4999999 →
  999, "Plata II"). *(Today the API
  returns 2 decimals, Python's `round` rounds half to even, every screen rounds again with
  `Math.round`, and PostgreSQL stores ratings as 4-byte `REAL`, turning 999.4999999 into 999.5.)*
- **FR-028j** [CHANGE]: Wherever a current rating is shown together with its rank label — student
  stats (overall and per course), teacher dashboard and student report, group and V1 rankings,
  the rank badge — the system shall return the **display value** (FR-028i) with the rating and
  derive the rank label from that same display value, never from the full-precision rating; the
  full-precision value stays available for calculations and is not displayed. Example: an overall
  rating of 999.6 is shown as 1000 with "Plata I"; 999.4 as 999 with "Plata II"; 999.5 as 1000
  with "Plata I". *(Today the label is computed from the full-precision value while the screen
  rounds it, so 999.6 shows "1000" next to "Plata II".)*
- **FR-028k** [CHANGE]: The system shall define a student's **catalogue** from their education
  level and, for semillero, their grade: for universidad, colegio and concursos, every course of
  that level's block; for semillero with grade *g* (6–11), exactly the semillero courses of grade
  *g* (those whose id ends in `_semillero_g`); for semillero without a grade, no course. The
  catalogue offered to the student and the "current level and grade" of FR-028a are the same set,
  computed by one domain rule. *(Today: a semillero student with a grade is offered no course,
  because the catalogue looks for a block `Semillero g°` that no course has; one without a grade
  is offered all 36 courses and has every grade's courses counted as current.)*
- **FR-028l** [CHANGE]: When a student joins a group through its invitation code, the system shall
  enrol them in the group's course even if it is outside their catalogue — provided a semillero
  student has a grade — and shall change neither the student's level nor their grade; the invited
  course shall not become part of the catalogue, so it never counts toward the overall rating
  (FR-028a) while the student keeps access to practise it. When the student's courses are listed,
  the system shall list such a course among their enrolments, marked as outside the catalogue, and
  shall not offer it in the catalogue to explore. *(Today: `POST /api/student/enroll-by-code`
  answers 500 for every valid code on both engines — it reads the group's id under a key the
  repositories do not return; the rule does not check a semillero student's grade; and the course
  list returns only the catalogue, so a course reached by invitation appears on no screen.)*
- **FR-028m** [CHANGE]: The system shall reject a registration as a semillero student without a
  grade from 6 to 11, and shall reject any enrolment request — other than through an invitation
  (FR-028l) — for a course outside the student's catalogue, on every level. *(Today: both are
  accepted; only the screens keep students to their catalogue.)* Registration and enrolment belong
  to identity and access: these two rules are stated here because they decide the catalogue, and
  move to spec 004 when it is written.
- **FR-028n** [CHANGE]: When the schema is migrated, the system shall check, without changing it,
  that the `courses.block` constraint accepts the four blocks (`Universidad`, `Colegio`,
  `Concursos`, `Semillero`). If it does, the system shall issue no DDL for it and shall keep any
  extra value it already allows. If it does not, the system shall stop the migration with an
  error that names the missing values, before any change to that constraint or table, and shall
  never drop, re-add or rebuild them automatically (AGENTS R8, R17). A new database is created
  with a constraint that accepts the same set on both engines. *(Today: PostgreSQL drops and
  re-adds the constraint on every migration; SQLite rebuilds the table when its probe fails,
  leaving the other tables' foreign keys pointing at a dropped table.)* Persistence belongs to
  spec 002; this rule is stated here because the catalogue depends on it, and moves there.
- **FR-028o** [CHANGE]: While a semillero student has no grade, the courses screen shall show the
  notice «Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu docente o al
  administrador.» in place of the empty catalogue, shall keep listing the courses the student is
  already enrolled in (FR-028l) with their access to practise, and shall offer no way to set the
  grade. *(Today: such a student is offered all 36 semillero courses.)*
- **FR-029** [CHANGE]: The system shall store every rating change — practice answer, diagnostic,
  procedure — under the **course and topic of the item involved**, identified by the course's
  stable identifier and the topic within it. There is one stored rating per student, course and
  topic, and no other stored rating. A topic shared by several courses (e.g. "Geometría" in grades
  6–9 and university) is a separate rating in each course. A topic label may equal a course name;
  identity never depends on labels being distinct. *(Today: course name in V1, topic or course id in V2
  practice, topic for procedures and diagnostic, course id for PvP, all in one store keyed by a
  single name — Known Deviation D-1.)*
- **FR-029a** [CHANGE]: Where a rating is needed for a whole course (course-wide practice
  selection, PvP expected outcome, course display), the system shall derive it as the average of
  the student's topic ratings in that course, and shall never store it; with no rated topic it
  uses 1000 for selection and PvP expectation, and displays "pending diagnostic". Practice,
  procedures and PvP in one course never change a rating in another course.
- **FR-029b** [CHANGE]: When a PvP result is applied, the system shall add the player's PvP delta
  to every topic rating that player has in the match's course, so the derived course rating moves
  by exactly that delta.
- **FR-029c** [CHANGE]: If a PvP player has no rated topic in the match's course, then the system
  shall leave that player's ratings unchanged, persist an applied delta of 0 for that player with
  the reason `no_rated_topics`, report that applied delta (not the computed one) in the match
  result, and apply the opponent's delta normally. Match completion stays idempotent (FR-025).
- **FR-030** [CHANGE]: When a predicted rating change is shown before answering, the system shall
  show the change the engine will apply (FR-002) for that student's current topic rating and
  uncertainty. *(Today the preview uses its own K of 32/24 — Known Deviation D-2.)*
- **FR-031** [CHANGE]: The system shall map a rating to a rank with one scale, defined once and
  used by every V2 surface (student, teacher, home page): the 16 levels "Aspirante → Leyenda
  Suprema" currently served by the student API. *(Today five scales coexist: that one; 16
  different levels in V1; 7 levels "Hierro → Maestro" on teacher screens; 8 tiers "Plata I →
  Maestro" on the home page; 4 diagnostic leagues.)*
- **FR-031a** [AS-IS]: When a diagnostic result is shown, the system shall label the starting
  point with its own league (Bronce / Plata / Oro / Diamante), presented as a placement, not as a
  rank.
- **FR-032** [AS-IS]: The system shall not change any rating from an exam submission.

**Legacy ratings (one-time reconciliation, FR-029)**

Every rating stored before this spec is a **legacy row**: keyed by a single name that may be a
topic, a course id or a course name, and ambiguous when a course name equals a topic name. A row
is attributed to a course only by evidence: practice attempts recorded under that row's key on
items of that course, or the student's diagnostic for that course.

- **FR-033** [CHANGE]: When legacy ratings are reconciled, the system shall leave every rating
  already stored under a course and topic unchanged.
- **FR-034** [CHANGE]: When legacy ratings are reconciled, the system shall create a rating for a
  course and topic that has none only if that context is **eligible** — the student practised that
  topic in that course or took that course's diagnostic — starting it from the first available
  source: (a) the legacy row keyed by that topic's label, if the student has practice attempts
  under that key on items of that course or took that course's diagnostic; otherwise (b) the
  legacy row for that course (FR-035), if the student practised that topic in that course. The
  new rating takes the source row's value and uncertainty. Eligibility shows that a context may
  receive a value; it does not prove what the legacy value originally meant.
- **FR-034a** [CHANGE]: The system shall mark every rating created by reconciliation as an
  **approximate baseline** and record its provenance (which legacy row, which rule, when). It
  shall never present such a rating as an exact recovery of past history.
- **FR-034b** [CHANGE]: If no eligible context can be established for a legacy row, then the system
  shall keep that row unassigned and shall not create any rating from it; that student's ratings
  in the affected courses start from the diagnostic (FR-020).
- **FR-035** [CHANGE]: If a student has both a course-id row and a course-name row for the same
  course, then the system shall use the one updated most recently (the course-id row on a tie);
  the system shall never add or average two legacy rows.
- **FR-036** [CHANGE]: The system shall keep legacy rows stored but exclude them from every rating
  read, derived course rating, overall rating and rank; reconciliation shall not replay historical
  attempts, and running it again shall change nothing.

**Practice access (follow-up F-4)**

- **FR-037** [CHANGE]: When a student asks for the next practice item of a course, or for a
  course's diagnostic (its status or its questions), the system shall serve it only if the
  student is enrolled in that course — whether they enrolled from their level's courses or
  through a teacher's invitation code; otherwise it shall refuse the request as forbidden
  (HTTP 403) and serve no item.
  *(Today: any course is served.)*
- **FR-037a** [CHANGE]: When a student submits a practice answer or a diagnostic, the system shall
  check that the student is enrolled in the course of the answered item — for a diagnostic, the
  diagnosed course — before reading for update or writing any rating, attempt, item difficulty,
  retry record or diagnostic result; if the student is not enrolled, it shall refuse the request
  as forbidden (HTTP 403) and change nothing. The check comes before a retry-key replay (FR-012a).
  *(Today: the answer is stored and sets a rating in a course the student never joined.)*

### Key Entities

- **Topic rating**: a student's level in one topic of one course — value, uncertainty (30–350),
  last update. The only stored rating state (FR-029).
- **Legacy row**: a rating stored before this spec under a single ambiguous name; kept, never read
  as a rating (FR-036).
- **Rating provenance**: for a topic rating, how it started — diagnostic, practice, or legacy
  approximate baseline (with source row and rule, FR-034a).
- **Course rating**: derived average of the student's topic ratings in a course; never stored.
- **Overall rating**: derived mean of the student's course ratings (FR-028a); never a source of
  state.
- **Item difficulty**: an item's level on the same scale; moves with every valid answer.
- **Attempt**: log of one practice answer — correctness, time, rating before/after, validity,
  retry key. History, not state.
- **Diagnostic result**: per-course record that a diagnostic was taken, with its starting point.
- **Procedure submission**: a teacher's grade and the rating change it produced, applied once.
- **PvP match**: two players, scores, status (active / finished / abandoned), changes applied once.
- **Rank**: a label derived from a rating (FR-031).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 100 % of the acceptance scenarios above, an automated check reproduces the
  stated numbers. Every scenario whose outcome depends on stored data runs against both supported
  databases with identical results; scenarios that exercise only domain rules or response shapes
  run once.
- **SC-002**: 0 rating changes are produced by answers outside the 3–600 s window, by exams, or by
  AI-proposed scores.
- **SC-003**: Retrying any accepted answer, procedure validation or match close changes ratings
  0 times beyond the first.
- **SC-004**: With 8 simultaneous answers from one student, the final rating equals the
  one-after-another result in 100 % of runs.
- **SC-005**: For any student, the overall rating and rank shown are identical on every V2 screen
  that shows them (V1 keeps its own labels — research R16).
- **SC-006**: The predicted change shown before an answer equals the applied change to within 0.1
  points.
- **SC-007**: After this spec is implemented, every new rating change lands on a topic, and 0
  legacy rows contribute to any rating, average or rank shown.
- **SC-008**: Running the reconciliation a second time changes 0 ratings; no student's existing
  topic rating changes because of it.

## Assumptions

- Formulas, constants (K = 32 practice, 24 PvP, 32 items; RD 350 → 30, ×0.95; window 3–600 s;
  band 0.40–0.75; mastery 1800) are pinned as they are. Changing any of them is a new `[CHANGE]`.
- V1 is frozen: its writer must follow FR-029 (a data-integrity fix — today it writes under the
  course name), but V1 screens are not required to follow FR-030 or FR-031.
- Legacy rows (D-1) are reconciled once per FR-033 … FR-036. Where
  and when the reconciliation runs is a plan decision, constrained by additive-only migrations
  (Principle IV). "Updated most recently" uses the row's last-update time.
- FR-009 and FR-026 use the default implied by the constitution; `/speckit-clarify` may overturn
  them.
- Unused rating code (`calculate_dynamic_k`, `update_elo`, the always-1.0 impact modifier) is
  removed when this area is refactored (constitution VII); it is not behaviour, so no FR covers it.

## Out of Scope *(mandatory)*

- Redesigning the rating model (Glicko/Elo variants, dynamic K, item uncertainty that shrinks —
  survey F9). This spec pins the current model.
- PvP lobby, matchmaking and realtime events — spec 007. Follow-up recorded for spec 007: whether
  a player with no rated topic in a course should be eligible for matchmaking (see FR-029c).
- Procedure upload, AI review and the teacher review UI — spec 006 (only the rating effect is here).
- Course map node unlocking and the 1250 "completed" threshold — spec 003 (it reads ratings
  defined here).
- Access to exams, the course map and lessons (`/exam/start`, `/map/{course}`, the lesson
  endpoints): exams change no rating (FR-032) and the map and lessons belong to spec 003; F-4
  does not check them.
- Badge/achievement rules themselves (only their failure handling, FR-015).
- New features or screens in V1.
- Changing a student's grade after registration (promotion) — spec 004 (FR-028c defines what it
  does to ratings).

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario. Reuse adequate existing tests; create or strengthen tests where coverage is missing.**

Each row cites collected pytest node ids (`path::test`, parametrised cases included) and Playwright
titles (`file › title`). Scenarios proven through the API on one engine also cite the two-engine test
of their storage behaviour (SC-001). Filled by T069 on 2026-10-07.

| Requirement / Scenario | Test |
|---|---|
| US1-AS1 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_new_topic_answer_from_defaults`<br>`tests/unit/application/test_spec001_service_pins.py::test_spec001_answer_moves_rating_and_item_symmetrically`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_answer_writes_only_the_items_course_topic` |
| US1-AS2 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_new_topic_answer_from_defaults`<br>`tests/unit/application/test_spec001_service_pins.py::test_spec001_answer_moves_rating_and_item_symmetrically`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_answer_writes_only_the_items_course_topic` |
| US1-AS3 | `tests/integration/test_elo_single_source.py::test_an_invalid_attempt_does_not_move_the_rating`<br>`tests/integration/test_spec001_repository_pins.py::test_spec001_response_time_window_is_inclusive` |
| US1-AS4 | `tests/api/test_spec001_answer_pins.py::test_spec001_retry_with_the_same_key_returns_the_stored_result`<br>`tests/integration/test_spec001_answer_retry.py::test_spec001_retry_returns_the_persisted_attempt_and_applies_once`<br>`tests/integration/test_postgres_production_guards.py::test_postgres_concurrent_answer_retry_has_one_effect` |
| US1-AS5 | `tests/api/test_spec001_answer_pins.py::test_spec001_same_key_for_another_answer_is_a_conflict`<br>`tests/integration/test_postgres_production_guards.py::test_postgres_concurrent_answer_retry_has_one_effect` |
| US1-AS6 | `tests/integration/test_elo_single_source.py::test_concurrent_answers_on_the_same_item_compose_serially` |
| US1-AS7 | `tests/api/test_student.py::TestAnswer::test_ignores_tampered_item_data`<br>`tests/api/test_student.py::TestAnswer::test_invalid_answer_context_has_no_side_effects`<br>`tests/api/test_student.py::TestAnswer::test_answer_without_legacy_item_data` |
| US2-AS1 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_selection_keeps_the_zdp_window_and_the_probability_band` |
| US2-AS2 | `tests/unit/domain/test_item_selector.py::test_spec001_band_widens_by_005_up_to_10_steps_then_whole_pool` |
| US2-AS3 | `tests/unit/application/test_spec001_service_pins.py::test_spec001_failed_item_returns_after_three_questions` |
| US2-AS4 | `tests/unit/application/test_spec001_service_pins.py::test_spec001_item_correct_this_session_is_never_offered` |
| US2-AS5 | `tests/unit/application/test_spec001_service_pins.py::test_spec001_exhausted_pool_mastery_threshold`<br>`tests/unit/application/test_spec001_service.py::test_spec001_selection_rating_is_topic_or_course` |
| US3-AS1 | `tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_correct_at_1200_and_a_skipped_answer`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_diagnostic_writes_course_topic_baselines`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_diagnostic_baseline` |
| US3-AS2 | `tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_floor_is_760`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_diagnostic_baseline` |
| US3-AS3 | `tests/integration/test_elo_single_source.py::test_diagnostic_baseline_survives_until_the_first_practice`<br>`tests/api/test_student.py::test_first_practice_uses_diagnostic_rating` |
| US3-AS4 | `tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_correct_at_1200_and_a_skipped_answer`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_diagnostic_baseline` |
| US4-AS1 | `tests/integration/test_spec001_repository_pins.py::test_spec001_validated_grade_adds_grade_minus_50_times_02`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_procedure_grade_bumps_the_items_course_topic_once`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_procedure_grade_creates_an_absent_row_and_floors_at_zero` |
| US4-AS2 | `tests/integration/test_elo_single_source.py::test_a_validated_procedure_delta_is_applied_exactly_once` |
| US4-AS3 | `tests/integration/test_spec001_repository_pins.py::test_spec001_grade_out_of_range_changes_nothing` |
| US4-AS4 | `tests/api/test_procedure_grading.py::test_other_teacher_cannot_grade_or_view_submission`<br>`tests/api/test_procedure_grading.py::test_reassignment_between_lookup_and_update_prevents_grading` |
| US4-AS5 | `tests/integration/test_spec001_repository_pins.py::test_spec001_ai_proposed_score_changes_no_rating` |
| US5-AS1 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_pvp_equal_ratings_win_and_draw`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_pvp_deltas` |
| US5-AS2 | `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_closing_a_match_twice_applies_the_delta_once`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once` |
| US5-AS3 | `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_matches_orphaned_by_a_restart_are_closed`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_a_live_match_is_left_alone` |
| US5-AS4 | `tests/integration/test_spec001_repository_pins.py::test_spec001_practice_after_pvp_starts_from_the_post_match_rating` |
| US5-AS5 | `tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_player_without_rated_topics_gets_zero` |
| US6-AS1 | `tests/unit/domain/test_spec001_domain.py::test_spec001_overall_rating`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_overall_is_the_mean_of_course_ratings`<br>`tests/api/test_spec001_api.py::test_spec001_stats_overall_is_the_mean_of_current_courses`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_every_ranking_reads_the_canonical_rating` |
| US6-AS2 | `tests/api/test_spec001_api.py::test_spec001_preview_equals_the_applied_change`<br>`frontend/e2e/spec001-ratings.spec.ts › Práctica muestra la previsión que envía la API (US6-AS2)` |
| US6-AS3 | `tests/api/test_spec001_api.py::test_spec001_number_and_label_agree_on_every_surface`<br>`tests/api/test_spec001_api.py::test_spec001_meta_ranks_is_public_and_ascending`<br>`frontend/e2e/spec001-ratings.spec.ts › Panel docente usa display_rating y rank_label de la API (US6-AS3, FR-028j)` |
| US6-AS4 | `tests/api/test_spec001_answer_pins.py::test_spec001_exam_submission_changes_no_rating`<br>`tests/integration/test_spec001_repository_pins.py::test_spec001_exam_storage_writes_no_rating` |
| US6-AS5 | `tests/api/test_spec001_api.py::test_spec001_promoted_student_is_pending_and_keeps_history`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_pending_diagnostic_and_history_courses`<br>`frontend/e2e/spec001-ratings.spec.ts › Estadísticas: diagnóstico pendiente y cursos de grados anteriores (US6-AS5/AS6)` |
| US6-AS6 | `tests/api/test_spec001_api.py::test_spec001_promoted_student_is_pending_and_keeps_history`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_pending_diagnostic_and_history_courses` |
| US6-AS7 | `tests/api/test_spec001_api.py::test_spec001_group_ranking_basis_errors_and_pending`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_group_ranking_never_substitutes_another_rating`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_group_ranking_on_the_group_course_without_substitution`<br>`frontend/e2e/spec001-ratings.spec.ts › Ranking del grupo: base, empates con el mismo puesto, valor tal cual y pendientes al final (US6-AS7/AS8)` |
| US6-AS8 | `tests/unit/domain/test_spec001_domain.py::test_spec001_rank_competition`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_rankings_follow_participation_and_competition`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_competition_ranks_and_limit`<br>`frontend/e2e/spec001-ratings.spec.ts › Ranking del grupo: base, empates con el mismo puesto, valor tal cual y pendientes al final (US6-AS7/AS8)` |
| US6-AS9 | `tests/unit/domain/test_spec001_domain.py::test_spec001_rating_display_number_and_label_agree`<br>`tests/api/test_spec001_api.py::test_spec001_number_and_label_agree_on_every_surface`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_stored_precision_and_display_agree_on_both_engines`<br>`frontend/e2e/spec001-ratings.spec.ts › Número y rango salen del mismo valor: 999.6 → 1000 «Plata I» (US6-AS9)`<br>`frontend/e2e/spec001-ratings.spec.ts › La pantalla muestra display_rating tal cual, sin redondear por su cuenta (FR-028i/j)` |
| US7-AS1 | `tests/integration/test_spec001_catalogue.py::test_spec001_semillero_catalogue_by_grade`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_current_courses_are_the_catalogue`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_courses_of_a_grade_7_student` |
| US7-AS2 | `tests/integration/test_spec001_catalogue.py::test_spec001_register_user_rejects_semillero_without_a_valid_grade`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_api_registration_rejects_semillero_without_a_valid_grade` |
| US7-AS3 | `tests/integration/test_spec001_catalogue.py::test_spec001_enrol_only_in_the_catalogue` |
| US7-AS4 | `tests/integration/test_spec001_catalogue.py::test_spec001_invitation_crosses_levels_without_changing_them` |
| US7-AS5 | `tests/integration/test_spec001_catalogue.py::test_spec001_gradeless_semillero_keeps_enrolments_but_no_new_invitation`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_gradeless_course_list_is_its_enrolments`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_current_courses_are_the_catalogue`<br>`frontend/e2e/f1-catalogue.spec.ts › Semillero sin grado: aviso, sin catálogo y con sus matrículas abiertas (FR-028o)` |
| US7-AS6 | `tests/integration/test_spec001_catalogue.py::test_spec001_course_list_marks_invited_courses`<br>`frontend/e2e/f1-catalogue.spec.ts › Un curso por invitación solo aparece en Mis matrículas (FR-028l)` |
| US8-AS1 | `tests/integration/test_spec001_practice_access.py::test_spec001_next_question_outside_enrolment_is_forbidden` |
| US8-AS2 | `tests/integration/test_spec001_practice_access.py::test_spec001_answer_outside_enrolment_changes_nothing` |
| US8-AS3 | `tests/integration/test_spec001_practice_access.py::test_spec001_diagnostic_outside_enrolment_is_forbidden` |
| US8-AS4 | `tests/integration/test_spec001_practice_access.py::test_spec001_enrolled_students_practise_as_before` |
| US8-AS5 | `tests/integration/test_spec001_practice_access.py::test_spec001_leaving_a_course_closes_it` |
| FR-001 | `tests/unit/domain/test_elo_model.py::TestExpectedScore::test_400_point_advantage_gives_approx_91_percent`<br>`tests/unit/domain/test_spec001_engine_pins.py::test_spec001_fr001_both_engine_paths_use_the_same_expected_success` |
| FR-002 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_new_topic_answer_from_defaults`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_rating_delta` |
| FR-003 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_rd_floor_30_holds_and_scales_the_change`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_next_rd_has_a_floor_of_30` |
| FR-004 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_new_topic_answer_from_defaults`<br>`tests/unit/application/test_spec001_service.py::test_spec001_unrated_course_selects_at_1000_and_ignores_the_diagnostic_average`<br>`tests/api/test_student.py::test_first_practice_uses_diagnostic_rating` |
| FR-005 | `tests/unit/application/test_spec001_service_pins.py::test_spec001_answer_moves_rating_and_item_symmetrically`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_item_difficulty_delta` |
| FR-006 | `tests/unit/application/test_spec001_service_pins.py::test_spec001_answer_moves_rating_and_item_symmetrically` |
| FR-007 | `tests/integration/test_elo_single_source.py::test_an_invalid_attempt_does_not_move_the_rating`<br>`tests/integration/test_spec001_repository_pins.py::test_spec001_response_time_window_is_inclusive` |
| FR-008 | `tests/integration/test_spec001_repository_pins.py::test_spec001_response_time_window_is_inclusive`<br>`tests/integration/test_elo_single_source.py::test_an_invalid_attempt_does_not_move_the_rating`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_is_valid_response_time` |
| FR-008a | `tests/integration/test_spec001_course_topic_store.py::test_spec001_explicit_zero_seconds_is_invalid`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_is_valid_response_time`<br>`tests/unit/application/test_spec001_service.py::test_spec001_process_answer_reports_validity` |
| FR-009 | `tests/api/test_spec001_api.py::test_spec001_invalid_time_reports_and_records_no_change`<br>`tests/unit/application/test_spec001_service.py::test_spec001_process_answer_reports_validity` |
| FR-010 | `tests/integration/test_elo_single_source.py::test_concurrent_answers_on_the_same_item_compose_serially` |
| FR-011 | `tests/api/test_student.py::TestAnswer::test_ignores_tampered_item_data`<br>`tests/api/test_student.py::TestAnswer::test_invalid_answer_context_has_no_side_effects` |
| FR-012 | `tests/api/test_spec001_answer_pins.py::test_spec001_retry_with_the_same_key_returns_the_stored_result`<br>`tests/integration/test_postgres_production_guards.py::test_postgres_concurrent_answer_retry_has_one_effect` |
| FR-012a | `tests/integration/test_spec001_answer_retry.py::test_spec001_retry_returns_the_persisted_attempt_and_applies_once`<br>`tests/integration/test_spec001_answer_retry.py::test_spec001_boundary_values_are_a_real_boundary` |
| FR-013 | `tests/api/test_spec001_answer_pins.py::test_spec001_same_key_for_another_answer_is_a_conflict`<br>`tests/integration/test_postgres_production_guards.py::test_postgres_concurrent_answer_retry_has_one_effect` |
| FR-014 | `tests/api/test_spec001_answer_pins.py::test_spec001_no_response_carries_the_correct_option` |
| FR-015 | `tests/unit/application/test_spec001_service.py::test_spec001_badge_failure_is_logged_and_the_answer_returns` |
| FR-016 | `tests/unit/application/test_student_service.py::TestGetNextQuestion::test_variety_preserves_unseen_priority_and_session_exclusions`<br>`tests/unit/application/test_spec001_service_pins.py::test_spec001_failed_item_returns_after_three_questions`<br>`tests/unit/application/test_spec001_service_pins.py::test_spec001_item_correct_this_session_is_never_offered`<br>`tests/unit/application/test_student_service.py::TestTopicFilter::test_unknown_topic_filter_falls_back_to_full_pool` |
| FR-017 | `tests/unit/domain/test_spec001_engine_pins.py::test_spec001_selection_keeps_the_zdp_window_and_the_probability_band`<br>`tests/unit/domain/test_item_selector.py::test_spec001_band_widens_by_005_up_to_10_steps_then_whole_pool` |
| FR-018 | `tests/unit/domain/test_item_selector.py::TestControlledVariety::test_variety_stays_near_best_information_and_inside_zdp`<br>`tests/unit/domain/test_item_selector.py::TestFisherInformation::test_prefers_item_closest_to_50_percent_success` |
| FR-019 | `tests/unit/application/test_spec001_service_pins.py::test_spec001_exhausted_pool_mastery_threshold` |
| FR-020 | `tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_correct_at_1200_and_a_skipped_answer`<br>`tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_floor_is_760`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_diagnostic_tier`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_diagnostic_baseline` |
| FR-021 | `tests/integration/test_spec001_course_topic_store.py::test_spec001_diagnostic_writes_course_topic_baselines`<br>`tests/api/test_student.py::test_first_practice_uses_diagnostic_rating`<br>`tests/integration/test_postgres_production_guards.py::test_postgres_permissions_diagnostic_and_canonical_answer` |
| FR-022 | `tests/integration/test_spec001_repository_pins.py::test_spec001_validated_grade_adds_grade_minus_50_times_02`<br>`tests/integration/test_elo_single_source.py::test_a_validated_procedure_delta_is_applied_exactly_once`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_procedure_grade_bumps_the_items_course_topic_once` |
| FR-023 | `tests/integration/test_spec001_repository_pins.py::test_spec001_grade_out_of_range_changes_nothing`<br>`tests/api/test_procedure_grading.py::test_other_teacher_cannot_grade_or_view_submission`<br>`tests/api/test_procedure_grading.py::test_reassignment_between_lookup_and_update_prevents_grading` |
| FR-024 | `tests/integration/test_spec001_repository_pins.py::test_spec001_ai_proposed_score_changes_no_rating` |
| FR-025 | `tests/unit/domain/test_spec001_domain.py::test_spec001_pvp_deltas`<br>`tests/unit/domain/test_spec001_engine_pins.py::test_spec001_pvp_equal_ratings_win_and_draw`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_closing_a_match_twice_applies_the_delta_once`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once` |
| FR-026 | `tests/unit/application/test_spec001_service.py::test_spec001_pvp_lobby_rating_is_the_course_rating_read_outside_the_lock` |
| FR-027 | `tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_matches_orphaned_by_a_restart_are_closed`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_a_live_match_is_left_alone`<br>`tests/integration/test_pvp_repository.py::TestPvpStateSurvivesTheProcess::test_spec001_abandonment_starts_after_600_seconds` |
| FR-028 | `tests/integration/test_spec001_course_topic_store.py::test_spec001_every_ranking_reads_the_canonical_rating`<br>`tests/api/test_spec001_api.py::test_spec001_every_surface_reads_the_canonical_rating`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_course_topic_ratings_are_new_table_rows_only` |
| FR-028a | `tests/unit/domain/test_spec001_domain.py::test_spec001_overall_rating`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_overall_is_the_mean_of_course_ratings`<br>`tests/api/test_spec001_api.py::test_spec001_stats_overall_is_the_mean_of_current_courses`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_current_context_is_enrollments_in_the_users_catalogue` |
| FR-028b | `tests/api/test_spec001_api.py::test_spec001_promoted_student_is_pending_and_keeps_history`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_pending_diagnostic_and_history_courses`<br>`tests/api/test_student.py::TestStats::test_stats_initial_elo`<br>`frontend/e2e/spec001-ratings.spec.ts › Estadísticas: diagnóstico pendiente y cursos de grados anteriores (US6-AS5/AS6)`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_pending_exam_snapshot_is_null_not_zero`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_genuine_zero_snapshot_is_reported_as_zero`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_diagnostic_after_the_exam_keeps_the_pending_snapshot`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_snapshot_recorded_before_the_status_is_unknown`<br>`tests/unit/application/test_teacher_service.py::TestGetStudentDashboard::test_pending_student_gets_no_number` |
| FR-028c | `tests/api/test_spec001_api.py::test_spec001_promoted_student_is_pending_and_keeps_history`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_pending_diagnostic_and_history_courses` |
| FR-028d | `tests/api/test_spec001_api.py::test_spec001_group_ranking_basis_errors_and_pending`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_group_ranking_never_substitutes_another_rating`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_group_basis_precedence` |
| FR-028e | `tests/integration/test_spec001_repository_pins.py::test_spec001_attempt_history_keeps_each_attempts_rating` |
| FR-028f | `tests/integration/test_spec001_course_topic_store.py::test_spec001_rankings_follow_participation_and_competition`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_global_participants_are_active_this_week`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_course_participants_count_only_that_course`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_group_and_weekly_participants`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_weekly_snapshot_stores_the_ranking_as_shown` |
| FR-028g | `tests/integration/test_spec001_repository_pins.py::test_spec001_weekly_snapshot_is_returned_unchanged`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_weekly_snapshot_stores_the_ranking_as_shown` |
| FR-028h | `tests/unit/domain/test_spec001_domain.py::test_spec001_rank_competition`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_competition_ranks_and_limit`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_rankings_follow_participation_and_competition` |
| FR-028i | `tests/unit/domain/test_spec001_domain.py::test_spec001_round_for_display_is_half_up`<br>`tests/unit/domain/test_spec001_domain.py::test_spec001_average_then_round_once`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_full_precision_until_the_one_rounding`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_stored_precision_and_display_agree_on_both_engines`<br>`tests/integration/test_spec001_answer_retry.py::test_spec001_retry_returns_the_persisted_attempt_and_applies_once`<br>`frontend/e2e/spec001-ratings.spec.ts › La pantalla muestra display_rating tal cual, sin redondear por su cuenta (FR-028i/j)` |
| FR-028j | `tests/unit/domain/test_spec001_domain.py::test_spec001_rating_display_number_and_label_agree`<br>`tests/api/test_spec001_api.py::test_spec001_number_and_label_agree_on_every_surface`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_stored_precision_and_display_agree_on_both_engines`<br>`frontend/e2e/spec001-ratings.spec.ts › Número y rango salen del mismo valor: 999.6 → 1000 «Plata I» (US6-AS9)`<br>`frontend/e2e/spec001-ratings.spec.ts › Panel docente usa display_rating y rank_label de la API (US6-AS3, FR-028j)`<br>`tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_number_and_rank_come_from_one_display_value`<br>`tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_views_rank_only_through_the_display_value` |
| FR-028k | `tests/unit/domain/test_spec001_catalogue.py::test_spec001_semillero_catalogue_is_the_courses_of_the_grade`<br>`tests/unit/domain/test_spec001_catalogue.py::test_spec001_semillero_without_a_grade_has_no_course`<br>`tests/unit/domain/test_spec001_catalogue.py::test_spec001_other_levels_are_their_block`<br>`tests/unit/domain/test_spec001_catalogue.py::test_spec001_unknown_level_falls_back_to_universidad`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_semillero_catalogue_by_grade`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_current_courses_are_the_catalogue` |
| FR-028l | `tests/integration/test_spec001_catalogue.py::test_spec001_invitation_crosses_levels_without_changing_them`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_gradeless_semillero_keeps_enrolments_but_no_new_invitation`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_course_list_marks_invited_courses`<br>`frontend/e2e/f1-catalogue.spec.ts › Un curso por invitación solo aparece en Mis matrículas (FR-028l)` |
| FR-028m | `tests/unit/domain/test_spec001_catalogue.py::test_spec001_valid_semillero_grades_are_6_to_11`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_register_user_rejects_semillero_without_a_valid_grade`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_api_registration_rejects_semillero_without_a_valid_grade`<br>`tests/integration/test_spec001_catalogue.py::test_spec001_enrol_only_in_the_catalogue` |
| FR-028n | `tests/integration/test_spec001_course_block_constraint.py::test_spec001_new_database_accepts_exactly_the_four_blocks`<br>`tests/integration/test_spec001_course_block_constraint.py::test_spec001_constraint_with_extra_values_is_left_as_it_is`<br>`tests/integration/test_spec001_course_block_constraint.py::test_spec001_old_database_stops_the_migration`<br>`tests/integration/test_spec001_course_block_constraint.py::test_spec001_migrate_py_exits_1_on_an_old_database` |
| FR-028o | `tests/integration/test_spec001_catalogue.py::test_spec001_gradeless_course_list_is_its_enrolments`<br>`frontend/e2e/f1-catalogue.spec.ts › Semillero sin grado: aviso, sin catálogo y con sus matrículas abiertas (FR-028o)`<br>`frontend/e2e/f1-catalogue.spec.ts › Semillero con grado: sin aviso (FR-028o)` |
| FR-029 | `tests/integration/test_spec001_course_topic_store.py::test_spec001_answer_writes_only_the_items_course_topic`<br>`tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_answer_lands_on_the_items_course_and_topic`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_diagnostic_writes_course_topic_baselines`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_procedure_grade_bumps_the_items_course_topic_once` |
| FR-029a | `tests/unit/application/test_spec001_service.py::test_spec001_selection_rating_is_topic_or_course`<br>`tests/unit/application/test_spec001_service.py::test_spec001_unrated_course_selects_at_1000_and_ignores_the_diagnostic_average`<br>`tests/unit/application/test_spec001_rating_read_service.py::test_spec001_course_rating_of`<br>`tests/unit/application/test_spec001_service.py::test_spec001_pvp_shows_pending_never_the_1000_fallback`<br>`tests/api/test_spec001_api.py::test_spec001_course_map_shows_unrated_topics_as_pending` |
| FR-029b | `tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_delta_reaches_every_rated_topic_once` |
| FR-029c | `tests/integration/test_spec001_course_topic_store.py::test_spec001_pvp_player_without_rated_topics_gets_zero`<br>`tests/unit/infrastructure/test_pvp_logic.py::test_spec001_game_end_sends_the_applied_delta_and_reason`<br>`tests/unit/infrastructure/test_pvp_logic.py::test_spec001_game_end_reports_not_applied_when_persistence_fails` |
| FR-030 | `tests/api/test_spec001_api.py::test_spec001_preview_equals_the_applied_change`<br>`frontend/e2e/spec001-ratings.spec.ts › Práctica muestra la previsión que envía la API (US6-AS2)`<br>`tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_stakes_preview_is_the_applied_change` |
| FR-031 | `tests/unit/domain/test_spec001_domain.py::test_spec001_one_rank_scale`<br>`tests/api/test_spec001_api.py::test_spec001_meta_ranks_is_public_and_ascending`<br>`frontend/e2e/spec001-ratings.spec.ts › Inicio lista los rangos de /api/meta/ranks`<br>`tests/api/test_spec001_api.py::test_spec001_meta_ranks_is_cacheable` |
| FR-031a | `tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_correct_at_1200_and_a_skipped_answer`<br>`tests/api/test_spec001_answer_pins.py::test_spec001_diagnostic_floor_is_760` |
| FR-032 | `tests/api/test_spec001_answer_pins.py::test_spec001_exam_submission_changes_no_rating`<br>`tests/integration/test_spec001_repository_pins.py::test_spec001_exam_storage_writes_no_rating` |
| FR-033 | `tests/integration/test_spec001_reconciliation.py::test_spec001_existing_rows_and_unassigned_legacy_rows_are_left_alone` |
| FR-034 | `tests/integration/test_spec001_reconciliation.py::test_spec001_topic_label_row_reaches_only_the_practised_course`<br>`tests/integration/test_spec001_reconciliation.py::test_spec001_course_name_equal_to_a_topic_label`<br>`tests/integration/test_spec001_reconciliation.py::test_spec001_diagnostic_makes_the_courses_topics_eligible`<br>`tests/integration/test_spec001_reconciliation.py::test_spec001_course_row_most_recent_wins_and_is_never_summed` |
| FR-034a | `tests/integration/test_spec001_reconciliation.py::test_spec001_topic_label_row_reaches_only_the_practised_course`<br>`tests/integration/test_spec001_reconciliation.py::test_spec001_course_row_most_recent_wins_and_is_never_summed`<br>`tests/api/test_spec001_api.py::test_spec001_stats_marks_approximate_baselines`<br>`tests/unit/application/test_teacher_service.py::TestGetStudentDashboard::test_rated_student_gets_the_derived_rating_and_its_label`<br>`frontend/e2e/spec001-ratings.spec.ts › Estadísticas marcan las líneas base aproximadas de la reconciliación (FR-034a)`<br>`tests/unit/interface/test_spec001_v1_compat.py::test_spec001_v1_teacher_topic_table_marks_approximate_baselines`<br>`tests/api/test_spec001_api.py::test_spec001_course_map_marks_approximate_topics`<br>`frontend/e2e/spec001-ratings.spec.ts › Mapa y riel del curso marcan los temas con línea base aproximada (FR-034a)` |
| FR-034b | `tests/integration/test_spec001_reconciliation.py::test_spec001_existing_rows_and_unassigned_legacy_rows_are_left_alone` |
| FR-035 | `tests/integration/test_spec001_reconciliation.py::test_spec001_course_row_most_recent_wins_and_is_never_summed` |
| FR-036 | `tests/integration/test_spec001_reconciliation.py::test_spec001_reconciliation_is_idempotent`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_every_ranking_reads_the_canonical_rating`<br>`tests/api/test_spec001_api.py::test_spec001_every_surface_reads_the_canonical_rating`<br>`tests/integration/test_spec001_course_topic_store.py::test_spec001_course_topic_ratings_are_new_table_rows_only` |
| FR-037 | `tests/integration/test_spec001_practice_access.py::test_spec001_next_question_outside_enrolment_is_forbidden`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_diagnostic_outside_enrolment_is_forbidden`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_enrolled_students_practise_as_before`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_leaving_a_course_closes_it`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_ensure_enrolled` |
| FR-037a | `tests/integration/test_spec001_practice_access.py::test_spec001_answer_outside_enrolment_changes_nothing`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_diagnostic_outside_enrolment_is_forbidden`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_leaving_a_course_closes_it`<br>`tests/integration/test_spec001_practice_access.py::test_spec001_ensure_enrolled` |

## Appendix — As-is evidence

Brownfield exception to "no implementation detail": where the current behaviour lives, so each
`[AS-IS]` claim can be checked (constitution agent rule 5). Not part of the requirements.

| FR | Evidence |
|---|---|
| FR-001–003 | `src/domain/elo/uncertainty.py:27-44`, `src/domain/elo/vector_elo.py` |
| FR-004 | `src/domain/elo/vector_elo.py` defaults; `api/dependencies.py:198-203` (diagnostic seed) |
| FR-005–006 | `src/application/services/student_service.py:158-162` (item RD passed through unchanged) |
| FR-007–008 | `sqlite_repository.py:1294-1401`, `postgres_repository.py:1648-1700` |
| FR-008a | `save_answer_transaction` in both repositories: `attempt_data.get("time_taken", 30.0) or 30.0` reads 0 as absent; `api/schemas/student.py:57` accepts `time_taken` with `ge=0` |
| FR-009 | `api/routers/student.py:225-238` reports `elo_after − elo_before` from compute |
| FR-010 | `save_answer_transaction` (BEGIN IMMEDIATE / FOR UPDATE users→items); `tests/integration/test_elo_single_source.py` |
| FR-011, FR-014 | `api/routers/student.py:155-175`; V2-R9 |
| FR-012–013 | `api/routers/student.py:176-200` |
| FR-012a | `api/routers/student.py` `replay()` rounds the stored `attempts.elo_after` (PostgreSQL `REAL`); the first response rounds `cog_data["elo_after"]` (full precision) — from 1181 at difficulty 1000: 1189.344952 → 1189.34 first; PostgreSQL returns the stored value as 1189.345 → 1189.35 on retry |
| FR-015 | `student_service.py:203-213` (`except Exception: pass`) |
| FR-016, FR-019 | `student_service.py:66-98` |
| FR-017–018 | `src/domain/selector/item_selector.py:40-80` |
| FR-020–021 | `api/routers/student.py:954-960, 1007-1053` |
| FR-022–024 | `procedure_elo_delta` in `src/domain/elo/model.py`; `validate_procedure_submission` (both repos) |
| FR-025, FR-027 | `api/websocket/pvp.py:28, 83-125`; `finish_pvp_match`, `expire_stale_pvp_matches` |
| FR-026 | `api/websocket/pvp.py:191` (global `current_elo`) vs `finish_pvp_match` (course key) |
| FR-028 | `get_latest_elo_by_topic`, `_refresh_global_elo` (both repos); `aggregate_global_elo` |
| FR-028d | `get_group_ranking` (both repos) ← `api/routers/student.py:401-413` (unvalidated `course_id`), `api/routers/teacher.py:328-337` (no course); `groups.course_id` nullable |
| FR-028e | `get_latest_attempts`, `get_student_attempts_detail`, `export_teacher_student_data` |
| FR-028f | `get_global_ranking`, `get_course_ranking`, `get_weekly_ranking`, `get_student_rank` (both repos) ← `student_view.py:538, 610, 634, 729, 757`, `teacher_view.py:465, 495, 528` |
| FR-028h | `ORDER BY elo DESC` / `ORDER BY ue.global_elo DESC` with no tie-break in every ranking query (both repos) |
| FR-028i | PostgreSQL rating columns are `REAL` (4-byte: `999.4999999::real` = 999.5); `round(..., 2)` (half-to-even) in API responses; `Math.round` on every rating in `Stats.tsx:142, 199, 229`, `RankBadge.tsx:52`, teacher `fmtMiles` |
| FR-028j | label from full precision: `api/routers/student.py:287` (`_elo_to_rank(global_elo)`), `Teacher/Dashboard.tsx:137, 207, 400` (`rankFor(s.global_elo)`); number rounded on screen: `Stats.tsx:142`, `RankBadge.tsx:52` |
| FR-028k | `get_available_courses_by_level` (both repos) filters on block `Semillero {grade}°`, which no course has; without a grade it returns every `Semillero` course; `student_view.py` `_student_block` (V1) |
| FR-028l | `enroll_by_code` (`api/routers/student.py:311`) reads `group["id"]` while `get_group_by_invite_code` returns `group_id` (500 on both engines), and has no grade check; `GET /api/student/courses` returns only `get_available_courses` |
| FR-028m | `api/schemas/auth.py:22` (`grade` optional for every level); `POST /api/student/enroll` checks only that the course exists |
| FR-028n | `_migrate_courses_block_check`: `postgres_repository.py:1228` (returns only if the definition contains `'Semillero 6'`, so it drops and re-adds every run), `sqlite_repository.py:915` (probe insert, then rename → create → copy → drop) |
| FR-028o | `frontend/src/pages/Student/Courses.tsx` shows `courses.noAvailable` for an empty catalogue |
| FR-028g | `weekly_rankings` table; `save_weekly_ranking`, `get_ranking_history` ← `teacher_view.py:550, 556` |
| FR-029 | `student_view.py:385`, `api/routers/student.py:166`, `useStudentSession.ts:74`, `finish_pvp_match`, `validate_procedure_submission`, diagnostic submit |
| FR-030 | `frontend/src/pages/Student/Practice.tsx:27-33` |
| FR-031 | `api/routers/student.py:1497` (`_RANK_THRESHOLDS`), `src/interface/streamlit/state.py:31`, `frontend/src/pages/Teacher/Dashboard.tsx:20`, `Teacher/Groups.tsx:14`, `Home.tsx:36`, `api/routers/student.py:963` (`_DIAG_LEAGUES`) |
| FR-032 | `api/routers/student.py` exam submit ("examen no afecta ELO") |
| FR-037, FR-037a | `api/routers/student.py` `next_question`, `answer`, `diagnostic_status`, `diagnostic_submit`: no enrolment check (only PvP checks it, `api/websocket/pvp.py`) |
