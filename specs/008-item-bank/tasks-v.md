# Tasks — spec 008, delivery V (validator rules)

**Plan**: [plan-v.md](plan-v.md) · **Status**: approved (owner decisions O-V1 …
O-V9 answered 2026-10-21, each as recommended). FR-010, FR-011 and FR-012 are `[CHANGE]`; US2-AS1 … AS3 are their scenarios. V has no
`[AS-IS]` requirement of its own, but it touches the validator delivery A pinned (FR-001), so
Phase 1 re-runs those pins on the unchanged code before anything changes.

## Phase 0 — Owner decisions (blocking)

- [x] T000 The owner decides O-V1 … O-V9 (plan-v.md § Owner decisions) and the plan's status
  becomes approved. **No task below starts before this.** A decision that differs from the
  recommendation is written into plan-v.md first and the affected tasks are adjusted in the same
  commit (e.g. O-V6 «warning» turns T005's case into a warning assertion; O-V7 «rename mode» adds a
  test and a script option to T006/T011). Done 2026-10-21: every recommended option was approved,
  so the tasks below stand as written.

## Phase 1 — Pins green on the unchanged code (blocking)

- [ ] T001 Run delivery A's and T's validator and content pins on `redesign` unchanged and record
  the green run in the PR: `tests/unit/scripts/test_validate_bank.py`,
  `tests/unit/infrastructure/test_bank_validator.py`, `tests/unit/infrastructure/test_bank_content.py`
  (50 passed on 2026-10-21), `python scripts/validate_bank.py` (exit 0) and
  `python scripts/build_epa8_bank.py --check` (exit 0) (FR-001, FR-002, FR-043 stay green through V).
- [ ] T002 [P] Data pin, passes on unchanged data:
  `tests/unit/infrastructure/test_bank_content.py::test_spec008_v_every_bank_difficulty_is_an_integer_in_400_2000`
  (SC-002; measured 0 failures, min 500, max 1,550).
- [ ] T003 [P] Pin the passing half of US2-AS1 and US2-AS3 on unchanged code:
  `tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_integer_difficulty_in_400_2000_passes`
  (400, 1000, 2000) and
  `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_the_committed_epa8_bank_passes_the_check`
  (FR-010, US2-AS1; FR-012, US2-AS3).

**Checkpoint**: T001–T003 green on unchanged code.

## Phase 2 — `[CHANGE]` tests first (each fails on the unchanged code, for the stated reason)

- [ ] T004 [P] [US2] D1 (depends on T001):
  - `tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_difficulty_outside_400_2000_or_not_an_integer_fails`
    — parametrised 350, 399, 2001, 2100, 900.5, `true`, `"900"` (and `900.0` per O-V1); exit 1 and
    the message names the value and 400–2000. Fails today: all pass or only warn.
  - `tests/unit/domain/test_spec008_v_bank_rules.py::test_spec008_v_difficulty_rule` — the pure
    rule (module per O-V2). Fails today: module absent.
  - `tests/unit/scripts/test_validate_bank.py::test_spec008_v_agents_states_the_validators_difficulty_range`
    — AGENTS § Item bank and `README.md` state the validator's range. Fails today: 600–1800.
  - `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_the_generator_applies_the_bank_difficulty_rule`
    — a source item at 2100 makes `revisar` report it. Fails today: [100, 3000].
  (FR-010, US2-AS1)
- [ ] T005 [P] [US2] D4, the validator (depends on T001):
  - `tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_id_whose_course_changed_fails_naming_both_values`
  - `…::test_spec008_v_an_id_whose_topic_changed_fails_naming_both_values`
  - `…::test_spec008_v_a_new_id_fails_until_the_script_adds_it` (exit 1 naming the id and
    `update_id_manifest.py`; run the script; exit 0)
  - `…::test_spec008_v_a_manifest_id_missing_from_the_bank_fails` (per O-V6)
  - `…::test_spec008_v_a_missing_manifest_fails` (per O-V8)
  Each builds a temporary bank and manifest and runs the validator as CI does. Fail today: no
  manifest check. (FR-011, US2-AS2)
- [ ] T006 [P] [US2] D4, the script and the base check (depends on T001):
  - `tests/unit/scripts/test_id_manifest.py::test_spec008_v_the_script_only_appends` — new ids added
    sorted, existing entries never changed or removed, a second run changes nothing, a moved id
    refused with exit 1 and nothing written.
  - `…::test_spec008_v_a_changed_or_removed_entry_against_the_base_fails` — `--against <base>`
    fails naming the entry (O-V5).
  - `tests/unit/infrastructure/test_bank_content.py::test_spec008_v_the_committed_manifest_matches_the_bank`
    — every bank id is in `items/id_manifest.json` with its course and topic (SC-004).
  Fail today: no script, no manifest. (FR-011, US2-AS2)
- [ ] T007 [US2] D6 (depends on T001):
  - `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_a_hand_edited_epa8_bank_fails_the_check`
    — a temporary copy of the bank with one option edited; `--check --bank <copy>` exits 1 naming
    the item. Fails today: `--check` never reads the bank.
  - `…::test_spec008_v_the_bank_job_runs_the_epa8_check` — the «Banco de preguntas» job in
    `.github/workflows/ci.yml` runs `build_epa8_bank.py --check` (text check, no YAML library).
    Fails today.
  (FR-012, US2-AS3)

**Checkpoint**: T004–T007 collected and failing for the reasons stated; T001–T003 still green.

## Phase 3 — Implementation (after Phase 2 fails for the right reason)

- [ ] T008 [US2] D1: `difficulty_problem` in the rules module (O-V2); `validate_item` uses it as an
  error and drops the [100, 3000] warning; `build_epa8_bank.py::revisar` uses it. **Flip** the pinned
  `tests/unit/infrastructure/test_bank_validator.py::TestValidateItem::test_out_of_range_difficulty_is_warning_not_error`
  to «5000 is an error», renamed, citing FR-010 in its docstring (depends on T004).
- [ ] T009 [US2] Docs of D1: `AGENTS.md` § Item bank `difficulty (int, 400–2000)` (FR-010's own
  clause), `README.md:262` the same (depends on T004).
- [ ] T010 [US2] D4: `manifest_problems`, `manifest_changes`, `appended_manifest` in the rules
  module; `scripts/update_id_manifest.py` (append, `--against <base>`); the validator reads
  `items/id_manifest.json`; `test_validate_bank.py::_run` writes the temporary bank's manifest — a
  fixture change only, no assertion of delivery A or T changes (depends on T005, T006).
- [ ] T011 [US2] Generate and commit `items/id_manifest.json` with the script from the current bank
  (2,031 ids, after T is closed); confirm `bank_fingerprint` is unchanged (no file under
  `items/bank/` changed) (depends on T010).
- [ ] T012 [US2] D6: `render` and the comparing `--check` (O-V9) with `--bank PATH` in
  `scripts/build_epa8_bank.py`; its output stays byte-identical to the committed bank (depends on
  T007).
- [ ] T013 CI, bank job only: step `python scripts/build_epa8_bank.py --check`; checkout
  `fetch-depth: 2` and, on a pull request whose base has a manifest, step
  `python scripts/update_id_manifest.py --against <(git show HEAD^1:items/id_manifest.json)`; add
  `tests/unit/scripts/test_build_epa8_bank.py`, `tests/unit/scripts/test_id_manifest.py` and
  `tests/unit/domain/test_spec008_v_bank_rules.py` to its pytest line (depends on T010, T012).
- [ ] T014 `AGENTS.md` § Item bank: the manifest, its script, «a moved item gets a new id» (D4) and
  the EPA8 regeneration rule; § Verify adds `build_epa8_bank.py --check` when `items/` changes
  (depends on T013).

## Phase 4 — Traceability and verification

- [ ] T015 `specs/008-item-bank/spec.md`: fill the V rows — FR-010 (T004, T008's flipped test,
  T002), FR-011 (T005, T006), FR-012 (T007), US2-AS1 (T003, T004), US2-AS2 (T005, T006), US2-AS3
  (T003, T007); add `items/id_manifest.json`, `scripts/update_id_manifest.py` and the rules module
  to § Code Scope; mark V `closed`. `docs/sdd/roadmap.md` M8 status line.
- [ ] T016 Review assertion adequacy: each US2 scenario's «fails» and «passes» halves are both
  cited; FR-011's message names the id and both values.
- [ ] T017 Verification: `ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q`;
  `python scripts/validate_bank.py`; `python scripts/build_epa8_bank.py --check`;
  `python scripts/check_traceability.py --run`; black and flake8. No repository changed, so
  `db_sync_check.py` only as a sanity run; no `frontend/` change. V1 unaffected (no shared runtime
  code changed).

## Dependencies

T000 → T001 → (T002, T003) and (T004 ∥ T005 ∥ T006 ∥ T007) → T008/T009 (after T004), T010 → T011
(after T005, T006), T012 (after T007) → T013 → T014 → T015 → T016 → T017.
No implementation task starts before its Phase 2 test fails for the stated reason.
