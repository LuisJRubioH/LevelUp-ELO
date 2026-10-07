# Data Model: ELO Engine (spec 001)

All schema changes are additive (constitution IV, AGENTS.md R8): new table, new columns, new
index. Nothing is dropped or retyped. Every change is mirrored in SQLite and PostgreSQL (R1).

## New: `student_course_topic_elo` — the only rating state (FR-029)

| Column | Type (PG / SQLite) | Rule |
|---|---|---|
| `user_id` | INTEGER, FK users | PK part |
| `course_id` | TEXT, FK courses | PK part — stable course identifier |
| `topic` | TEXT | PK part — topic label **within** the course |
| `current_elo` | DOUBLE PRECISION / REAL NOT NULL | ≥ 0 |
| `rd` | DOUBLE PRECISION / REAL NOT NULL DEFAULT 350 | 30 ≤ rd ≤ 350 |
| `origin` | TEXT NOT NULL | `practice` · `diagnostic` · `legacy_topic_row` · `legacy_course_row` · `procedure` (first writer; never rewritten) |
| `approximate` | BOOLEAN / INTEGER NOT NULL DEFAULT false | true only for reconciled rows (FR-034a) |
| `legacy_source_key` | TEXT NULL | the legacy row's key when `origin` is `legacy_*` |
| `reconciled_at` | TIMESTAMP NULL | when reconciliation created the row |
| `created_at`, `updated_at` | TIMESTAMP | `updated_at` on every change |

- PK `(user_id, course_id, topic)`; index `(user_id, course_id)`.
- `current_elo` and `rd` are 8-byte floats on both engines (SQLite `REAL` is 8 bytes; PostgreSQL
  `REAL` is 4 bytes and is never used here — research R20, FR-028i).
- Writers: answer (set), diagnostic (set, only if no practice for that pair), procedure (add,
  floor 0), PvP (add to every row of `(user, course)`), reconciliation (insert-if-absent).
- `origin`/`approximate` describe how the row **started**; a later practice answer updates the
  value but keeps the provenance, so "approximate baseline" stays traceable (FR-034a).

## Changed: `student_topic_elo` → legacy store (FR-036)
- No schema change. **No writer** after this spec. Read only by reconciliation.
- Rows keyed by a topic label, a course id or a course name are indistinguishable by key; they are
  attributed only through eligibility evidence (research R10).

## Changed: `users.current_elo` → legacy column (FR-028)
- No schema change. No longer written; no consumer reads its value (`get_user_by_id` still
  selects the column for compatibility). Overall rating is derived (below).

## Changed: `attempts`
- No schema change. From now on `topic` holds the **item's** topic (not an arbitrary key) and
  `elo_after = elo_before` when `elo_valid = 0` (FR-009). Course is derived through `item_id`.
- Historical rows keep their old `topic` values — they are the eligibility evidence for
  reconciliation and are never replayed.

## Changed: `pvp_matches` (FR-029c)

| New column | Type | Rule |
|---|---|---|
| `elo_reason_p1` | TEXT NULL | `NULL` = applied normally; `no_rated_topics` = applied 0 |
| `elo_reason_p2` | TEXT NULL | same |

`elo_delta_p1/p2` hold the **applied** delta (0 when the reason is set).

## Derived values (never stored)

```
topic rating        row of student_course_topic_elo
course rating(C)    mean(current_elo of rows with course_id = C)           None if no rows
current courses     enrollments(user) ∩ catalogue(user.education_level, user.grade)
overall rating      mean(course rating(C) for C in current courses if not None)
                    None → "pending diagnostic"                             (FR-028a/b)
display value       round_for_display(overall or course rating) — half up, whole number;
                    computed only at the edge, never stored, never averaged    (FR-028i/j)
rank                rank_for(display value)  — one 16-level table               (FR-031, 028j)
selection rating    topic rating when practising a topic, else course rating (1000 if None)
```

## State transitions

**PvP match**: `active → finished` (deltas applied once, guarded by `status='active'`) ·
`active → abandoned` (startup sweep after 600 s, no rating change).

**Procedure submission**: `pending → VALIDATED_BY_TEACHER` (delta applied once, `elo_applied=1`).

**Legacy row**: `unassigned` (default) → `used as source` (a new row records it in
`legacy_source_key`); the legacy row itself never changes.

## Validation rules
- Response time in [3, 600] s inclusive, else invalid; an explicit 0 is invalid and only an absent
  value counts as 30 s (domain `is_valid_response_time`, FR-008a).
- Teacher grade in [0, 100], else rejected.
- Retry key 1–128 chars; same key + different answer fingerprint → 409.
- Selected option must be one of the item's options.
