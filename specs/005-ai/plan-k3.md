# Plan — spec 005, delivery K3: KatIA's record

**Spec**: [spec.md](spec.md) § Deliveries, K3 (US3; FR-030 … FR-033) · **Branch**: `005-ai-k3`,
from `redesign` after K2 · **Date**: 2026-10-19 · **Status**: draft for the owner's approval

## Summary

Today every message a student types is kept in `katia_interactions` with no expiry, read by the
teacher and exported with the student's name, and KatIA answers each message alone (no earlier
turns). K3 turns a chat into a conversation about one item, records how it ended and what kind of
difficulty it showed, and deletes its text when it closes.

## Constitution Check (1.2.0)

| Principle | K3 |
|---|---|
| Minors (VI) | No free text kept after a conversation; the summary has none |
| Additive migrations (R8) and dual database (IV, R1) | Two new tables on both engines; `katia_interactions` stays (no DROP) and stops being written |
| Schema version (spec 002 D1) | `SCHEMA_VERSION` + 1 and a new digest; `docs/transfer.md` § 4.1 and § 5 updated (the rule of 2026-10-19) |
| Layers (III) | Outcome rules in the domain; the repository stores rows |

## Design

- **Tables:**
  - `katia_conversations` — `id`, `user_id`, `course_id`, `item_id`, `topic`, `opened_at`,
    `last_message_at`, `turns`, `status` (`open`/`closed`), `outcome`
    (`superado`/`no_superado`/`abandonado`), `difficulty`, `misconception_tag`, `closed_at`;
    index `(user_id, status)`.
  - `katia_messages` — `conversation_id`, `role` (`student`/`katia`), `text`, `created_at`; rows of
    a closed conversation are deleted in the transaction that closes it.
- **Turns (FR-030):** `/ai/socratic` opens (or continues) the student's open conversation on the
  item and sends its earlier turns to the provider as context, at most the last 6.
- **Closing (FR-031):** pure rule `close_outcome(event)`:
  - `/answer` for that item → `superado` or `no_superado` from the attempt's result (the same
    transaction as the answer, so it cannot disagree with it);
  - `/next-question` for another item, `/auth/logout` → `abandonado` for every open conversation of
    the student;
  - 24 h with no message → `abandonado`, by `expire_stale_katia_conversations()` (called at start
    and on each KatIA request, like `expire_stale_pvp_matches`).
  The difficulty is chosen after the response is sent (a background task): one provider call with
  the conversation's text and the fixed list of N2, answer constrained to one label; anything else,
  or a failure, records `sin_clasificar`. The text is deleted after that call, and by the 24-hour
  sweep in any case (FR-032). The misconception tag is the chosen option's, from the item's data.
- **Teacher (FR-033):** `GET /teacher/student/{id}/katia-history` returns summaries (topic, item,
  turns, outcome, difficulty, tag, dates); the export gives counts per topic × outcome. The
  frontend has no KatIA-history screen today; the summaries join the student panel's «Ruta de
  aprendizaje» area as a short table (data first, D3).
- **Before K3 (N3):** `katia_interactions` is no longer written; `scripts/repairs/
  delete_katia_texts.py` counts and, with `--apply`, deletes its rows — run by the owner after the
  switch.

## Tests (written first; each fails on today's code)

| Test (both engines where storage is involved) | Proves |
|---|---|
| `tests/integration/test_spec005_k3_record.py::test_a_conversation_keeps_its_turns_and_sends_them_as_context` | FR-030 |
| `…::test_answering_right_or_wrong_closes_as_superado_or_no_superado` | US3-AS1, FR-031 |
| `…::test_another_item_logout_or_24h_close_as_abandonado` | US3-AS2, FR-031 |
| `…::test_no_text_remains_after_closing` (and none older than 24 h; SC-004) | US3-AS3, FR-032 |
| `…::test_an_unclassifiable_difficulty_is_sin_clasificar` | FR-031 |
| `…::test_the_teacher_reads_summaries_and_exports_counts_only` | FR-033 |
| `tests/unit/domain/test_spec005_close_outcome.py` | FR-031 |
| D1's digest test and D3's parity tests | the schema change is on both engines and versioned |
