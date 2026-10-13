# Data Model: KatIA guardrails (spec 005)

Additive only (AGENTS R8), idempotent, identical in both engines (constitution IV).

## New table `item_serves`

One row per item `next-question` serves to a student (research R1).

| Column | SQLite | PostgreSQL | Meaning |
|---|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` | the serving |
| `user_id` | `INTEGER NOT NULL` | `INTEGER NOT NULL REFERENCES users(id)` | student |
| `item_id` | `TEXT NOT NULL` | `TEXT NOT NULL` | item served |
| `course_id` | `TEXT` | `TEXT` | course asked for |
| `attempt_watermark` | `INTEGER NOT NULL DEFAULT 0` | `INTEGER NOT NULL DEFAULT 0` | the student's highest `attempts.id` when served |
| `served_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | audit only; never compared |

Index `idx_item_serves_user_item (user_id, item_id, id)`.

- Current serving of (student, item): the row with the highest `id`.
- Answered: `EXISTS (SELECT 1 FROM attempts WHERE user_id = ? AND item_id = ? AND id > attempt_watermark)`.

## `katia_interactions` — two new columns

| Column | Type (both) | Meaning |
|---|---|---|
| `serve_id` | `INTEGER` (nullable; old rows and V1 turns have none) | serving the turn belongs to |
| `guard_outcome` | `TEXT` (nullable) | `accepted`, `truncated`, `redirected:<reason>`, `rejected:<reason>[,<reason>…]`, `truncated_empty`, `restricted`, `closed` |

Index `idx_katia_interactions_serve (serve_id)`.

`katia_response` keeps meaning "the text the student saw" (teachers read and export it). A
rejected model reply is never written.

## Reads on existing tables

- Open exams: `active_exam_sessions` rows of the student with `submitted_at IS NULL` and
  `expires_at` not passed — the same condition `complete_active_exam_session` uses in each engine.
- Enrolment: `get_user_enrollments` (spec 001 FR-037).

## Repository methods (both engines, declared in `IKatiaRepository`)

| Method | Returns |
|---|---|
| `record_item_serve(user_id, item_id, course_id)` | id of the new serving |
| `get_latest_item_serve(user_id, item_id)` | `{"id", "attempt_watermark"}` or `None` |
| `has_attempt_after(user_id, item_id, attempt_id)` | `bool` |
| `get_open_exam_item_ids(user_id)` | `list[str]` |
| `get_katia_turns(serve_id)` | `[{"student_message", "katia_response", "guard_outcome"}]`, oldest first |
| `save_katia_interaction(…, serve_id=None, guard_outcome=None)` | `None` (two new optional parameters; V1's call is unchanged) |
