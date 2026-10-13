# Tasks: KatIA guides without giving the answer (spec 005, block 6)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/api.md](contracts/api.md)

**Tests are mandatory.** `[AS-IS]` pins pass on the unchanged code; `[CHANGE]` tests fail on it
first. Backend tests use a fake tutor model; nothing here calls a real model (§ Model evaluation
is T060–T062 and is never cited in § Traceability).

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [ ] T001 Create `tests/api/test_spec005_katia_api.py` with a fake-tutor fixture that replaces
  `api.routers.ai.make_tutor`, records `(route, max_tokens, system, messages)` and returns
  scripted completions; a helper that serves an item through `/api/student/next-question`.
- [ ] T002 [P] Create `tests/integration/test_spec005_katia_store.py` on the two-engine `repo`
  fixture.

---

## Phase 2: Pin current behaviour (blocking — pass on the unchanged code)

- [ ] T003 [P] FR-021: pin 404 for an unknown item in `tests/api/test_spec005_katia_api.py`
  (`test_spec005_unknown_item_is_not_found`).
- [ ] T004 [P] FR-033, US6-AS3: keep `tests/api/test_rate_limit.py::test_socratic_rate_limit_is_enforced_per_access_token`
  as the pin (10 pass the limiter, the 11th is 429).
- [ ] T005 [P] FR-035: keep `tests/api/test_ai_errors_and_scores.py` (#57) as the pin.
- [ ] T006 [P] FR-026, US4-AS3: Playwright pin in `frontend/e2e/katia-chat.spec.ts` — the exam
  screen offers no KatIA.

**Checkpoint**: T003–T006 green on the base before any change.

---

## Phase 3: [CHANGE] tests first (must fail on the base)

### Domain (unit)

- [ ] T010 [P] [US1] `tests/unit/domain/test_spec005_guardrails.py`: FR-003, FR-004, FR-005
  (es and en: direct requests, proposals by letter/position/content, overrides; genuine
  questions pass); FR-010 … FR-015 (correct text, equal value, statement exclusion, short
  options, positions, other options, eliminations, verdicts, step markers, accumulation);
  FR-032 (trimming).
- [ ] T011 [P] [US1, US2] `tests/unit/domain/test_spec005_tutor_prompt.py`: FR-001 (allowed and
  forbidden moves, no "felicita"/"distractor"), FR-002 (message is the last user turn, never in
  the instructions), FR-006 (no key; identical whichever option is correct — SC-001), FR-007
  (internal reference after an answer), es and en.

### Application (unit, fake repository and tutor)

- [ ] T012 [US1–US6] `tests/unit/application/test_spec005_katia_service.py`: refusal order
  (FR-019, FR-020, FR-024, FR-025) with no model call and nothing stored; redirects without a
  model call (FR-003 … FR-005); rejected reply → reviewed hint, rejected text not stored (FR-009,
  FR-017); escalation (FR-016); turn cap (FR-034); history bound (FR-023); answered vs earlier
  serving (FR-007, FR-008); outcomes stored (FR-037); truncation (FR-032).

### Infrastructure (unit)

- [ ] T013 [P] [US5, US6] `tests/unit/infrastructure/test_spec005_katia_tutor.py`: routing
  (FR-027, FR-028, FR-029), `max_tokens` forwarded (FR-031), truncation flags, failures become
  `TutorUnavailable` with no key in the log (FR-030).

### Storage (both engines)

- [ ] T014 [US2, US3, US4] `tests/integration/test_spec005_katia_store.py`: serving watermark and
  answered check across two servings (FR-008, FR-022), open-exam item ids for open, submitted
  and expired sessions (FR-025), turns by serving with outcome (FR-037), idempotent migration.

### API (end to end, fake tutor)

- [ ] T015 [US1–US6] `tests/api/test_spec005_katia_api.py`: US1-AS1 … US6-AS4 and the API side of
  FR-018 … FR-030, FR-031, FR-034; adapt `test_rate_limit.py` (served item), `test_ai_errors_and_scores.py`
  (new seam, same assertions) and
  `tests/api/test_spec001_api.py::test_spec001_every_surface_reads_the_canonical_rating`
  (the rating reaches KatIA's instructions).

### Frontend (Playwright, mocked API)

- [ ] T016 [US3, US6] `frontend/e2e/katia-chat.spec.ts`: the request carries no statement and no
  provider unless the student has a key (FR-018); each refusal code shows its translated message
  in es and en, 429 included (FR-036, US6-AS5).

**Checkpoint**: T010–T016 fail on the base for the intended reason.

---

## Phase 4: Implementation

- [ ] T020 [P] `src/domain/katia/limits.py` (KatiaLimits, SOCRATIC_MAX_TOKENS moved; R11) and
  `model_router.py` importing it.
- [ ] T021 [P] `src/domain/katia/guardrails.py` (R3, R4, R8) → T010 green.
- [ ] T022 [P] `src/domain/katia/reviewed_messages.py`, `src/domain/katia/tutor_prompt.py` (R5)
  → T011 green.
- [ ] T023 `src/application/interfaces/tutor.py`, `IKatiaRepository`, `KatiaService` → T012 green;
  contract test lists the new service.
- [ ] T024 Both repositories: `item_serves`, `katia_interactions` columns, the six methods
  (data-model) → T014 green; `db_sync_check.py`.
- [ ] T025 `src/infrastructure/external_api/katia_tutor.py` (R6, R7) → T013 green.
- [ ] T026 `api/config.py` limits; `api/schemas/student.py`; `api/routers/student.py` records the
  serving; `api/routers/ai.py` composition (R9) → T015 green.
- [ ] T027 Remove `get_socratic_guidance`, `get_socratic_guidance_stream` and V1's unused alias
  (R10).
- [ ] T028 Frontend: `SocraticChat.tsx`, `Practice.tsx`, `CourseRail.tsx`, i18n es/en → T016 green;
  `pnpm run build`.

---

## Phase 5: Documentation and model evaluation

- [ ] T030 `AGENTS.md` § AI integration and `README.md` § IA pedagógica: V2 guardrails summarised
  with a link to this spec, V1's check named as V1-only, § Known limits stated (SC-005).
- [ ] T031 `docs/sdd/roadmap.md`: spec 005 started by block 6.
- [ ] T060 [P] `scripts/evaluate_katia_models.py` (R12) with
  `tests/unit/scripts/test_evaluate_katia_models.py` for its scoring and cost arithmetic.
- [ ] T061 `docs/sdd/katia-model-evaluation.md`: protocol, command, report format; results
  pending until a run with keys.
- [ ] T062 Run the evaluation with keys and present the report to the owner — **owner's step**;
  no model change before it.

---

## Phase 6: Traceability and verification

- [ ] T040 Bold every FR and scenario ID in spec.md and fill § Traceability; no `PENDING`.
- [ ] T041 `python scripts/check_traceability.py --run` (with `POSTGRES_TEST_DATABASE_URL`),
  `pytest tests/`, `db_sync_check.py`, `black --check`, `flake8`, `pnpm run build`,
  `pnpm exec playwright test`; report the actual output.

## Dependencies

Phase 2 → Phase 3 → Phase 4 (T020 → T021/T022 → T023 → T024/T025 → T026 → T027 → T028) →
Phase 5 → Phase 6. T060–T061 can run in parallel with Phase 4 once T023 exists.
