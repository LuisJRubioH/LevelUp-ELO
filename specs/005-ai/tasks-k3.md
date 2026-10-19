# Tasks — spec 005, delivery K3 (KatIA's record)

**Plan**: [plan-k3.md](plan-k3.md) (approved by the owner, 2026-10-19). FR-030 … FR-033 are
`[CHANGE]`.

## Decisions taken while implementing (for review)

- **The text goes when the conversation closes.** The plan described two orders: the text is
  deleted in the closing transaction, or after the classification call. This delivery does the
  stricter one. The transaction that closes a conversation reads its text, deletes it and hands
  it back once. The classification runs in the response's background task with that copy, which
  lives only in memory. Nothing waits for a classifier to delete text.
- **The answer closes the conversation in its own transaction** (`save_answer_transaction`, both
  engines), so the outcome cannot disagree with the attempt. The router reads the open text just
  before, for the classification. A retry with the same `Idempotency-Key` closes nothing.
- **«Another item» means asking for a question.** `/next-question` closes every open conversation
  of the student, even if the selector serves the same item again: the student left it.
- **Ending the session.** `/auth/logout` reads the student from the access token or, when it has
  expired, from the refresh cookie. Without either, logging out still succeeds, and the 24-hour
  sweep closes what is left.
- **The 24-hour sweep** (`expire_stale_katia_conversations`) runs:
  - in the bootstrap (`scripts/migrate.py` on a deploy);
  - on every KatIA request;
  - on every `/next-question`.

  It also deletes any text left of a closed conversation. There is no scheduler, so SC-004 holds
  while the platform has traffic or a deploy. A school week always has both; a long holiday with
  neither would keep the last day's open texts until the next request.
- **Classification key.** The student's own key does not outlive their request (R7), so the
  classifier uses the function key or the general key. With neither, the difficulty stays
  `sin_clasificar` and no provider is called. One call per conversation, 10 tokens, the KatIA
  model.
- **Misconception tag.** No bank item carries a tag per option today, so `misconception_tag` is
  NULL. The column is ready for spec 008.
- **History in the prompt.** The last 6 turns go as text in KatIA's prompt («CONVERSACIÓN HASTA
  AHORA»), under the same «SISTEMA:» prefix as in K2.
- **A replaced reply** (FR-022) keeps the turn with the student's message only.
- `SocraticRequest.item_content` is optional (deprecated): the server has ignored it since K2.
- **V1** still writes `katia_interactions` until it is disconnected at the switch.
  `scripts/repairs/delete_katia_texts.py` deletes those rows. The owner runs it after V1 is off:
  `docs/transfer.md` § 6, step 8.

## Phase 1 — Tests first (fail on the unchanged code)

- [x] T001 `tests/unit/domain/test_spec005_close_outcome.py`: each way out has its outcome; one
  exact N2 label or `sin_clasificar`; the prompt holds the turns and the labels — FR-031
- [x] T002 `tests/integration/test_spec005_k3_record.py` (both engines):
  - turns as context (the last 6);
  - an answer closes as `superado` / `no_superado`, and only that item's conversation;
  - another item, logout or 24 h close it as `abandonado`;
  - no text after closing, nor in the export;
  - the difficulty is classified, or `sin_clasificar` when the reply is free text, the provider
    fails or there is no system key;
  - the teacher's summaries, and the export's counts.

  Covers US3-AS1 … AS3 and FR-030 … FR-033.
- [x] T003 `test_spec002_d1_repair_scripts_report_and_are_idempotent[katia_texts]` — N3
- [x] T004 Existing tests that read `katia_interactions` now read the open conversation's
  messages:
  - `test_spec005_k2_katia.py`;
  - `test_ai_errors_and_scores.py`;
  - `test_teacher_export_cells.py`: the KatIA sheet has no typed text left, so the control
    character moved to the user name.

## Phase 2 — Implementation

- [x] T005 `src/domain/katia/conversation.py`: `close_outcome`, `parse_difficulty`,
  `classification_prompt`, `HISTORY_TURNS`, `STALE_AFTER_HOURS`
- [x] T006 Both repositories, implementing the same methods:
  - `_create_katia_conversations` (migration);
  - `open_katia_conversation`, `record_katia_turn`, `open_katia_transcripts`;
  - `close_katia_conversations`, `expire_stale_katia_conversations`, `set_katia_difficulty`;
  - `get_katia_conversations`, `export_teacher_katia_summary`, `repair_katia_texts`;
  - `save_answer_transaction` closes the item's conversation.

  The schema moves to `SCHEMA_VERSION` 4, with a new digest.
- [x] T007 API:
  - `api/katia_record.classify_closed`;
  - KatIA: the sweep, the open conversation, the history to the provider, the turn recorded;
  - `/next-question`, `/answer` and `/auth/logout` close conversations;
  - the teacher's `katia-history` returns summaries, and the KatIA sheet in the xlsx export
    returns counts.
- [x] T008 Frontend: the student panel's «Conversaciones con KatIA» table (topic, outcome, turns,
  difficulty) for the selected course. Covered by `frontend/e2e/spec005-k3-katia-summaries.spec.ts`.
- [x] T009 `scripts/repairs/delete_katia_texts.py`. Docs:
  - `docs/transfer.md`: § 4 DROP list (19 tables), § 5 version 4, § 6 step 8;
  - `AGENTS.md`: database table.

## Phase 3 — Close

- [x] T010 Traceability: US3-AS1 … AS3 and FR-030 … FR-033 filled; K3 `closed`. Checks run:
  - the full suite on both engines;
  - Playwright;
  - black and flake8;
  - `db_sync_check.py` and `check_traceability.py`;
  - `pnpm run build`.
