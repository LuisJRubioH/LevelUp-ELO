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

### Edge Cases

- Response time exactly 3 s or exactly 600 s → valid (inclusive bounds).
- Missing response time → treated as 30 s (valid).
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
- A rating of exactly n.5 → rounds up to n + 1 for display and ranking (FR-028i); intermediate averages are
  never rounded, so topics 1200.4, 1200.4, 1201.4 give a course ranking value of 1201, not 1200.
- Legacy row with no eligible context → kept unassigned and excluded; the diagnostic initializes.
- Promotion → the overall rating switches to the new grade's courses; until one has a rated topic
  it reads "pending diagnostic".
- Two items with the same difficulty → the chosen one is kept by identity, not by difficulty.
- Practice filtered to a topic that has no items → falls back to the whole course pool.
- A retry key longer than 128 characters or empty → rejected.
- A diagnostic containing the same item twice, or an item from another course → rejected.

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
  themselves. *(Today the API
  returns 2 decimals, Python's `round` rounds half to even, and every screen rounds again with
  `Math.round`.)*
- **FR-028j** [CHANGE]: Wherever a current rating is shown together with its rank label — student
  stats (overall and per course), teacher dashboard and student report, group and V1 rankings,
  the rank badge — the system shall return the **display value** (FR-028i) with the rating and
  derive the rank label from that same display value, never from the full-precision rating; the
  full-precision value stays available for calculations and is not displayed. Example: an overall
  rating of 999.6 is shown as 1000 with "Plata I"; 999.4 as 999 with "Plata II"; 999.5 as 1000
  with "Plata I". *(Today the label is computed from the full-precision value while the screen
  rounds it, so 999.6 shows "1000" next to "Plata II".)*
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
- Badge/achievement rules themselves (only their failure handling, FR-015).
- New features or screens in V1.

## Traceability *(mandatory)*

**Automated tests are explicitly required for every functional requirement and acceptance
scenario. Reuse adequate existing tests; create or strengthen tests where coverage is missing.**

Docs stage: every row names the task(s) in tasks.md that produce its test; `PENDING` until T068
replaces it with the collected test id.

| Requirement / Scenario | Test |
|---|---|
| US1-AS1 | `PENDING` (T011, T012, T033) |
| US1-AS2 | `PENDING` (T011, T033) |
| US1-AS3 | `PENDING` (T006) |
| US1-AS4 | `PENDING` (T013) |
| US1-AS5 | `PENDING` (T013) |
| US1-AS6 | `PENDING` (T006) |
| US1-AS7 | `PENDING` (T009) |
| US2-AS1 | `PENDING` (T015) |
| US2-AS2 | `PENDING` (T004) |
| US2-AS3 | `PENDING` (T014) |
| US2-AS4 | `PENDING` (T014) |
| US2-AS5 | `PENDING` (T014) |
| US3-AS1 | `PENDING` (T016) |
| US3-AS2 | `PENDING` (T016) |
| US3-AS3 | `PENDING` (T006) |
| US3-AS4 | `PENDING` (T016) |
| US4-AS1 | `PENDING` (T017, T047) |
| US4-AS2 | `PENDING` (T006) |
| US4-AS3 | `PENDING` (T017) |
| US4-AS4 | `PENDING` (T008) |
| US4-AS5 | `PENDING` (T017) |
| US5-AS1 | `PENDING` (T018) |
| US5-AS2 | `PENDING` (T007) |
| US5-AS3 | `PENDING` (T007) |
| US5-AS4 | `PENDING` (T018) |
| US5-AS5 | `PENDING` (T049) |
| US6-AS1 | `PENDING` (T022, T031, T053) |
| US6-AS2 | `PENDING` (T058, T061) |
| US6-AS3 | `PENDING` (T057, T061) |
| US6-AS4 | `PENDING` (T013, T019) |
| US6-AS5 | `PENDING` (T053, T061) |
| US6-AS6 | `PENDING` (T053) |
| US6-AS7 | `PENDING` (T055, T061) |
| US6-AS8 | `PENDING` (T022, T056, T061) |
| US6-AS9 | `PENDING` (T022, T057, T061) |
| FR-001 | `PENDING` (T003) |
| FR-002 | `PENDING` (T011) |
| FR-003 | `PENDING` (T011) |
| FR-004 | `PENDING` (T011, T042, T044) |
| FR-005 | `PENDING` (T012) |
| FR-006 | `PENDING` (T012) |
| FR-007 | `PENDING` (T006, T019) |
| FR-008 | `PENDING` (T006, T019, T034) |
| FR-009 | `PENDING` (T034) |
| FR-010 | `PENDING` (T006) |
| FR-011 | `PENDING` (T009) |
| FR-012 | `PENDING` (T010, T013) |
| FR-013 | `PENDING` (T013) |
| FR-014 | `PENDING` (T013) |
| FR-015 | `PENDING` (T012, T035) |
| FR-016 | `PENDING` (T005, T014) |
| FR-017 | `PENDING` (T004, T015) |
| FR-018 | `PENDING` (T004) |
| FR-019 | `PENDING` (T014) |
| FR-020 | `PENDING` (T016) |
| FR-021 | `PENDING` (T006, T045) |
| FR-022 | `PENDING` (T006, T017) |
| FR-023 | `PENDING` (T008, T017) |
| FR-024 | `PENDING` (T017) |
| FR-025 | `PENDING` (T007, T018) |
| FR-026 | `PENDING` (T050) |
| FR-027 | `PENDING` (T007) |
| FR-028 | `PENDING` (T006, T054) |
| FR-028a | `PENDING` (T053) |
| FR-028b | `PENDING` (T053) |
| FR-028c | `PENDING` (T053) |
| FR-028d | `PENDING` (T055) |
| FR-028e | `PENDING` (T019) |
| FR-028f | `PENDING` (T029, T056) |
| FR-028g | `PENDING` (T019) |
| FR-028h | `PENDING` (T022, T056) |
| FR-028i | `PENDING` (T022, T031, T061) |
| FR-028j | `PENDING` (T022, T031, T057, T061) |
| FR-029 | `PENDING` (T033, T036, T040, T045, T047, T052) |
| FR-029a | `PENDING` (T042) |
| FR-029b | `PENDING` (T049) |
| FR-029c | `PENDING` (T049) |
| FR-030 | `PENDING` (T058) |
| FR-031 | `PENDING` (T057) |
| FR-031a | `PENDING` (T016) |
| FR-032 | `PENDING` (T013, T019) |
| FR-033 | `PENDING` (T059) |
| FR-034 | `PENDING` (T059) |
| FR-034a | `PENDING` (T059) |
| FR-034b | `PENDING` (T059) |
| FR-035 | `PENDING` (T059) |
| FR-036 | `PENDING` (T054, T059) |

## Appendix — As-is evidence

Brownfield exception to "no implementation detail": where the current behaviour lives, so each
`[AS-IS]` claim can be checked (constitution agent rule 5). Not part of the requirements.

| FR | Evidence |
|---|---|
| FR-001–003 | `src/domain/elo/uncertainty.py:27-44`, `src/domain/elo/vector_elo.py` |
| FR-004 | `src/domain/elo/vector_elo.py` defaults; `api/dependencies.py:198-203` (diagnostic seed) |
| FR-005–006 | `src/application/services/student_service.py:158-162` (item RD passed through unchanged) |
| FR-007–008 | `sqlite_repository.py:1294-1401`, `postgres_repository.py:1648-1700` |
| FR-009 | `api/routers/student.py:225-238` reports `elo_after − elo_before` from compute |
| FR-010 | `save_answer_transaction` (BEGIN IMMEDIATE / FOR UPDATE users→items); `tests/integration/test_elo_single_source.py` |
| FR-011, FR-014 | `api/routers/student.py:155-175`; V2-R9 |
| FR-012–013 | `api/routers/student.py:176-200` |
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
| FR-028i | `round(..., 2)` (half-to-even) in API responses; `Math.round` on every rating in `Stats.tsx:142, 199, 229`, `RankBadge.tsx:52`, teacher `fmtMiles` |
| FR-028j | label from full precision: `api/routers/student.py:287` (`_elo_to_rank(global_elo)`), `Teacher/Dashboard.tsx:137, 207, 400` (`rankFor(s.global_elo)`); number rounded on screen: `Stats.tsx:142`, `RankBadge.tsx:52` |
| FR-028g | `weekly_rankings` table; `save_weekly_ranking`, `get_ranking_history` ← `teacher_view.py:550, 556` |
| FR-029 | `student_view.py:385`, `api/routers/student.py:166`, `useStudentSession.ts:74`, `finish_pvp_match`, `validate_procedure_submission`, diagnostic submit |
| FR-030 | `frontend/src/pages/Student/Practice.tsx:27-33` |
| FR-031 | `api/routers/student.py:1497` (`_RANK_THRESHOLDS`), `src/interface/streamlit/state.py:31`, `frontend/src/pages/Teacher/Dashboard.tsx:20`, `Teacher/Groups.tsx:14`, `Home.tsx:36`, `api/routers/student.py:963` (`_DIAG_LEAGUES`) |
| FR-032 | `api/routers/student.py` exam submit ("examen no afecta ELO") |
