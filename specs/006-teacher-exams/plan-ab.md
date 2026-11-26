# Plan — spec 006, deliveries AB1 … AB3: the open question

**Spec**: [spec.md](spec.md) § Deliveries, AB1 … AB3 (US8-AS1 … US8-AS5; FR-060 … FR-065) ·
**Branch**: `claude/dazzling-mendel-uta2jw` · **Date**: 2026-11-26 · **Status**: AB1 and AB2 for the
owner's approval; AB3 planned (Clarifications, session 2026-11-26)

## Summary

The 2027 municipal olympiad's three tests carry 1, 2 and 4 open questions, typed on the platform
(user, 2026-11-25), graded by the AI on a four-criterion rubric and decided by the teachers. A
template held multiple-choice items only.

## Constitution Check (1.2.0)

| Principle | AB |
|---|---|
| Migrations additive (R8) | two new tables, `exam_open_questions` and `exam_open_answers`, by `_create_exam_open_questions` on both engines; `SCHEMA_VERSION` 11 with its digest |
| Dual database (R1) | four new methods and one new argument of `complete_active_exam_session`, on both engines; `db_sync_check.py`, `test_spec002_d3_parity.py` |
| Layers (R2) | the rubric, the prompt and its reading are pure domain (`src/domain/exams/open_answers.py`); the provider call is the composition layer's (`api/open_answer_review.py`) |
| Ratings (R15) | an open answer moves no rating, as no exam does (FR-004) |
| Keys (R7) | the proposal uses the teacher-analysis function's key or the general key, never a student's |
| Personal data (VI) | the AI receives the answer's code, never a name, username or identification |
| Tests first (VII) | every AB1 and AB2 integration test and both browser tests fail on the unchanged code |

## Design

- **Where open questions live (FR-060).** In the template, not the bank: a bank item is multiple
  choice by contract (spec 008), and the olympiad's open problems are written for its tests. Each
  has a statement and a reference solution (≤ 4,000 characters), at most 6 per template, in order.
  `PATCH` replaces them all and is refused once a student started the template, like its items
  (FR-031); a duplicate carries them.
- **What the student sees (FR-061).** `POST /exam/start` and a resume add `open_questions` —
  `id` and `statement`, never the reference. The screen shows them after the multiple choice, with
  a text box (4,000 characters) each, in the question map as A1, A2…; the local draft keeps them.
- **The submission (FR-062).** `open_answers: [{question_id, text}]`; an id the template does not
  hold is 400. One row per question of the template, a blank one too, inserted in the transaction
  that records the session. `open_pending` in the response counts them; the screen says they await
  the teachers. The multiple-choice score is unchanged; the final score comes with AB3.
- **The code.** `R-` and the answer's number, six digits (`answer_code`): what the AI and the
  teacher go by.
- **The AI's proposal (FR-063).** A background task after the response
  (`propose_for_session`): one call per pending answer with `rubric_prompt` — statement, reference,
  answer, code — and `parse_rubric` on the reply: four integer levels 0–3 and a comment, or
  nothing. States: `blank` (0 on every criterion at submission, no call), `proposed`, `failed`
  (provider error or unreadable reply), `no_key`. The function's key is `teacher_analysis`'s, its
  model `AI_MODEL_ANALYSIS`.
- **AB3 (planned).** A queue for the template's teacher: answers by code, statement, answer, the
  proposal; the teacher's levels in `teacher_levels` with `verified_by` and `verified_at` beside the
  AI's (columns already created in AB1's migration); results and export count an open answer once
  decided.

## Out of scope

- The olympiad's classification, weighting (40 % / 60 %) and tie-breaks: adjustments 9, 10 and 13.
- Re-asking the AI for a `failed` or `no_key` answer: the teacher grades it in AB3.
