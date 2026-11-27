# Plan — spec 006, deliveries AB1 … AB3: the open question

**Spec**: [spec.md](spec.md) § Deliveries, AB1 … AB3 (US8-AS1 … US8-AS7; FR-060 … FR-067) ·
**Branch**: `claude/dazzling-mendel-uta2jw` · **Date**: 2026-11-27 · **Status**: AB1 and AB2 for the
owner's approval; AB3 planned (Clarifications, sessions 2026-11-26 and 2026-11-27)

## Summary

The 2027 municipal olympiad's three tests carry 1, 2 and 4 open questions of two kinds (user,
2026-11-27): a **short answer** — a word or a number — graded by the platform on its own, and a
**procedure**, a photo of the student's sheet, the only kind the AI intervenes in: a vision model
proposes the rubric's levels and the teachers decide. Every manual grade is on record and shown to
the student and the institutions. A template held multiple-choice items only.

A first version of AB1 and AB2 (2026-11-26, commit `0661c79`, never merged) treated every open
question as typed text proposed by the AI; this plan replaces it. Its migration had not reached any
deployed database, so `SCHEMA_VERSION` 11 was redefined rather than raised again.

## Constitution Check (1.2.0)

| Principle | AB |
|---|---|
| Migrations additive (R8) | three new tables — `exam_open_questions`, `exam_open_answers`, `exam_open_grade_changes` — by `_create_exam_open_questions` on both engines; `SCHEMA_VERSION` 11 with its digest |
| Dual database (R1) | new repository methods and one new argument of `complete_active_exam_session`, on both engines; `db_sync_check.py`, `test_spec002_d3_parity.py` |
| Storage (R9) | a procedure photo is stored as procedures are: on PostgreSQL in the private bucket by its relative path, its bytes in the row only when the upload fails; on SQLite in the row |
| Layers (R2) | the kinds, the short answer's equivalences, the rubric, the prompt and its reading are pure domain (`src/domain/exams/open_answers.py`); the vision call is infrastructure; the background proposal is composition (`api/open_answer_review.py`) |
| Ratings (R15) | an open answer moves no rating, as no exam does (FR-004) |
| Keys (R7) | the proposal uses the procedure function's key or the general key, never a student's; vision is Groq's (spec 005 FR-014) |
| Personal data (VI) | the vision model receives the photo and the answer's code, never a name, username or identification; the student is told not to write their name on the sheet |
| Tests first (VII) | the AB1 and AB2 integration tests and both browser tests fail on the code before them |

## Design

- **Questions (FR-060).** In the template: `kind` `short` (statement, 1–10 accepted answers of
  ≤ 200 characters) or `procedure` (statement, reference solution ≤ 4,000), at most 6, in order.
  `PATCH` replaces them all and is refused once a student started the template (FR-031); a duplicate
  carries them. The teacher's form has a kind selector per question.
- **What the student sees (FR-061).** `open_questions` on start and resume: `id`, `statement`,
  `kind`, and on a resume `has_photo`. Never an accepted answer or a reference solution.
- **Short answers (FR-062).** Typed in a one-line field; on submission `short_answer_is_right`
  compares with the accepted answers — case, accents, spaces and a final period ignored; numbers
  compared by value (decimal comma or point, fractions). `auto_correct` and state `auto`; the
  response's `open_results` says which were right, never what was accepted. A typed answer to a
  procedure question is 400.
- **Procedure photos (FR-063).** `POST /api/student/exam/open-photo` (`session_id`, `question_id`,
  file): only the session's student, only while unsubmitted and before the deadline, only to a
  procedure question, only JPEG/PNG/WebP (validated as procedures are); an upsert keyed by
  `(session_id, question_id)`, so a new photo replaces the last. At submission an answer with a
  photo is `pending`, one without is `blank` (0 on every criterion).
- **The code.** `R-` and the answer's number, six digits (`answer_code`).
- **The AI's proposal (FR-064).** A background task after the response (`propose_for_session`):
  one call per pending photo with `rubric_from_image` and `rubric_prompt` — statement, reference,
  code — and `parse_rubric` on the reply. States: `proposed`, `failed` (provider error, unreadable
  reply, no image), `no_key` (no Groq key).
- **AB3 (planned).** A queue for the template's teacher by code: procedures with the photo and the
  proposal, short answers with their automatic grade. A teacher's grade — deciding a procedure or
  changing an automatic or earlier manual grade — is written with who, when, before, after and a
  required reason in `exam_open_grade_changes` (created in AB1's migration), shown to the student
  with their result and listed in the institution's report; results and export count open answers.

## Out of scope

- The olympiad's classification, weighting (40 % / 60 %) and tie-breaks: adjustments 9, 10 and 13.
- Re-asking the AI for a `failed` or `no_key` answer: the teacher grades it in AB3.
- PDFs as procedure photos: the vision model reads pictures.
