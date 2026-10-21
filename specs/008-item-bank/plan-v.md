# Plan — spec 008, delivery V: validator rules (D1, D4, D6)

**Spec**: [spec.md](spec.md) § Deliveries, V (US2; FR-010, FR-011, FR-012) · **Branch**: `008-v`,
from `redesign` · **Date**: 2026-10-21 · **Status**: draft for the owner's approval (decisions
O-V1 … O-V9 open)

## Summary

Three rules the bank does not enforce today, each a CI failure once V lands:

- **D1 (FR-010)** — a difficulty is an integer in 400–2000. Today `scripts/validate_bank.py`
  accepts anything `float()` reads (`"900"`, `900.5`, `true`) and only *warns* outside [100, 3000].
- **D4 (FR-011)** — an id never changes course or topic. A committed manifest,
  `items/id_manifest.json` (N1), records each id's course and topic; the validator fails when the
  bank disagrees with it, naming the id and both values. A new id enters the manifest through a
  script, never by hand.
- **D6 (FR-012)** — the EPA8 bank is its generator's output. The «Banco de preguntas» job runs
  `build_epa8_bank.py --check`, which fails when `items/bank/evaluar_para_avanzar_8.json` differs
  from what the generator writes.

V changes no schema, no repository and no bank data (measured below). T is closed, so the topics V
freezes are the regrouped ones (spec § Edge Cases).

## Constitution Check (1.2.0)

| Principle | V |
|---|---|
| Spec is the contract (I) | FR-010 … FR-012 are `[CHANGE]`; every one and US2-AS1 … AS3 gets a test that fails on today's code (tasks-v.md Phase 2) |
| One source of truth (II) | one owner per rule: the difficulty range and the manifest rules are defined once (O-V2) and read by the validator **and** the EPA8 generator, which today carries its own [100, 3000] copy (`scripts/build_epa8_bank.py:65`); AGENTS § Item bank and README summarise the range and link to spec 008 |
| Layers (III, R2) | the rules are pure functions over values — `difficulty_problem(value)`, `manifest_problems(manifest, bank_entries)`, `manifest_changes(base, head)`, `appended_manifest(manifest, bank_entries)` — with no I/O; the scripts read the files and print. Recommended home `src/domain/bank/rules.py`, standard library only (O-V2); `tests/unit/test_architecture_layers.py` already guards `domain/` |
| Dual database (IV, R1, R8) | not touched: no repository, no migration, no `SCHEMA_VERSION` change |
| Learning measurement (V, R15) | D4 is the guard for R15: a topic or course change re-keys an item's future answers to another rating row while the old row keeps counting in the course mean (survey B10). V forbids it before it happens |
| Simplicity (VII) | no new dependency (the bank job installs only pytest); the manifest is plain JSON, one line per id |
| Production (VI) | nothing runs against a database; nothing is deployed by an agent |

## Measured facts (`redesign @ 9177907`, 2026-10-21)

**Bank.** 49 files (13 top-level, 36 in `semillero/`; `rglob` and the sync read the same set),
**2,031 items, 2,031 unique ids**, 196 (course, topic) pairs. `validate_bank.py` passes (exit 0,
129 small-topic warnings from FR-043) in **0.26 s**.

**D1 (FR-010).** Every difficulty is a JSON integer (2,031 `int`, 0 floats, 0 strings, 0
booleans). Minimum **500**, maximum **1,550**. **0 items fail 400–2000**, so V needs **no data
change** and nothing has to be grandfathered. The 32 easy semillero items (13 at 500, 19 at 550 —
survey B6) are inside 400–2000 and outside AGENTS' «600–1800»; D1 keeps them as they are.

**AGENTS / README discrepancy.** `AGENTS.md:645` (§ Item bank) says `difficulty (int, 600–1800)`
and `README.md:262` says `difficulty (600–1800)`. The spec (FR-010, D1, SC-002) says 400–2000 and
requires AGENTS to state it. The validator says [100, 3000], as a warning; the EPA8 generator
says [100, 3000], as an error. Four places, three ranges, one bank that fits all of them. The code
PR aligns all four on 400–2000 (T009).

**D4 (FR-011).** No manifest exists. One generated from today's bank, one line per id sorted by
id, `{"<id>": ["<course>", "<topic>"]}`, is **2,033 lines, ~117 KB** (an object of objects would be
~170 KB). The course is the file name without extension (as the sync: `sync_items_from_bank_folder`,
S:4312, P:4754); the topic is compared byte for byte, as the sync stores it (no stripping). The
manifest lives outside `items/bank/`, so **it does not enter the bank fingerprint**
(`schema_version.py::bank_files` reads `items/bank/*.json` and `items/bank/semillero/*.json`):
committing it triggers no resync.

**D6 (FR-012).** `scripts/build_epa8_bank.py --check` exists but **does not do what FR-012 needs**:
it validates the sources (`items/source/epa8/*.json`: ids, key, options, range, figures) and
returns 0 **without reading the bank file** (lines 95-96 return before the projection). A
hand-edited bank file passes it today. The generator's full output, compared with the committed
`evaluar_para_avanzar_8.json`, is **byte-identical today** (55,648 bytes, 60 items), so adding the
comparison breaks nothing. The run takes **0.04 s**, standard library only; the bank job needs no
new install.

**CI.** The «Banco de preguntas» job (`.github/workflows/ci.yml:21-41`) runs `validate_bank.py`,
then `pytest tests/unit/infrastructure/test_bank_content.py tests/unit/scripts/test_validate_bank.py`
with only pytest installed. The traceability job already uses `fetch-depth: 2` and `HEAD^1` as the
base of a pull request (`ci.yml:368, 400`) — the precedent for the manifest's append-only check
(O-V5). The pre-commit hook runs `validate_bank.py` (`.pre-commit-config.yaml:57`).

**Pinned behaviour that flips.** `tests/unit/infrastructure/test_bank_validator.py::TestValidateItem::test_out_of_range_difficulty_is_warning_not_error`
pins the [100, 3000] warning (5000 → warning, no error). FR-010 makes 5000 an error; T008 flips
that test explicitly, citing FR-010. `::test_non_numeric_difficulty_is_error` stays green.

## Design

### D1 — difficulty (FR-010)

`difficulty_problem(value) -> str | None`: `None` when `value` is a JSON integer (Python `int`,
not `bool`) with `400 <= value <= 2000`; otherwise a message naming the value and the range.
Whether an integral float (`900.0`) or a numeric string (`"900"`) counts as an integer is O-V1.
`validate_item` replaces its float check and its [100, 3000] warning with this rule, as an error.
`build_epa8_bank.py::revisar` uses the same function instead of its own range. AGENTS § Item bank
and README say 400–2000.

### D4 — the id manifest (FR-011)

- **File** (O-V3): `items/id_manifest.json`, a JSON object sorted by id, one entry per line:
  `"A1_1": ["DIAN", "Constitución Política"]`. Committed. Every id that ever entered the bank stays
  in it (append-only), so an id removed and later reused with another course or topic still fails.
- **Validator** (`manifest_problems`), errors naming the id and both values:
  - a bank id in the manifest with another course or topic → «`<id>`: curso `<old>` → `<new>`» /
    «tema `<old>` → `<new>`» (FR-011, US2-AS2);
  - a bank id not in the manifest → «`<id>` no está en `items/id_manifest.json`; corre
    `python scripts/update_id_manifest.py`» (US2-AS2: a new id passes *once added*);
  - a manifest id absent from the bank → O-V6;
  - no manifest file → O-V8.
- **Script** `scripts/update_id_manifest.py` (O-V4): reads the bank, appends the ids the manifest
  lacks with their course and topic, never changes or removes an entry (`appended_manifest`), writes
  the canonical format; idempotent. It refuses (exit 1, writes nothing) when an existing id's course
  or topic differs, pointing to D4: a moved item gets a new id.
- **Append-only in CI** (O-V5): `update_id_manifest.py --against <base file>` fails when an entry
  of the base manifest is changed or removed (`manifest_changes`). The bank job runs it against
  `git show HEAD^1:items/id_manifest.json` on a pull request (checkout `fetch-depth: 2`), skipped
  when the base has no manifest (the PR that introduces it).
- **A moved item** (spec § Edge Cases, D4): the old id stays in the bank and the manifest; the item
  gets a new id. Until delivery L adds `"retired": true`, the old id cannot be taken out of
  circulation (survey B8: removing it from the JSON leaves it served) — O-V6. A topic rename is
  O-V7.

### D6 — EPA8 against its generator (FR-012)

`build_epa8_bank.py` gains a pure step `render(items) -> str` (the exact text it writes today:
projection, `image_url`, `json.dumps(…, ensure_ascii=False, indent=2) + "\n"`). `--check` keeps its
source checks and then compares `render(cargar())` with the committed file: equal → exit 0;
different → exit 1, naming the first differing ids (or «el archivo no existe») and the fix
(«regenera con `python scripts/build_epa8_bank.py` desde `items/source/epa8/`; no edites el banco a
mano»). Byte or parsed comparison is O-V9. A `--bank PATH` option (default the real file) lets the
test point it at a temporary copy. The «Banco de preguntas» job adds a step
`python scripts/build_epa8_bank.py --check` after the validator.

### Tests (written first; Phase 2 of tasks-v.md)

| Test | Proves | Before V |
|---|---|---|
| `tests/unit/scripts/test_validate_bank.py::test_spec008_v_a_difficulty_outside_400_2000_or_not_an_integer_fails` (350, 399, 2001, 2100, 900.5, `true`, `"900"`; and `900.0` if O-V1 says so) | FR-010, US2-AS1 | fails |
| `…::test_spec008_v_an_integer_difficulty_in_400_2000_passes` (400, 1000, 2000) | FR-010, US2-AS1 | passes (pin of the passing half) |
| `tests/unit/domain/test_spec008_v_bank_rules.py::test_spec008_v_difficulty_rule` | FR-010 (the pure rule) | fails (module absent) |
| `tests/unit/scripts/test_validate_bank.py::test_spec008_v_agents_states_the_validators_difficulty_range` (AGENTS § Item bank and README name the validator's range) | FR-010 (AGENTS clause) | fails |
| `tests/unit/infrastructure/test_bank_content.py::test_spec008_v_every_bank_difficulty_is_an_integer_in_400_2000` | SC-002 on the real bank | passes (data pin) |
| `tests/unit/scripts/test_validate_bank.py::test_spec008_v_an_id_whose_course_changed_fails_naming_both_values` | FR-011, US2-AS2 | fails |
| `…::test_spec008_v_an_id_whose_topic_changed_fails_naming_both_values` | FR-011, US2-AS2 | fails |
| `…::test_spec008_v_a_new_id_fails_until_the_script_adds_it` (fails; runs `update_id_manifest.py`; passes) | FR-011, US2-AS2 | fails |
| `…::test_spec008_v_a_manifest_id_missing_from_the_bank_fails` (per O-V6) | FR-011 | fails |
| `…::test_spec008_v_a_missing_manifest_fails` (per O-V8) | FR-011 | fails |
| `tests/unit/scripts/test_id_manifest.py::test_spec008_v_the_script_only_appends` (sorted, idempotent, never changes or removes; refuses a moved id) | FR-011 («by a script») | fails |
| `…::test_spec008_v_a_changed_or_removed_entry_against_the_base_fails` | FR-011 (append-only, O-V5) | fails |
| `tests/unit/infrastructure/test_bank_content.py::test_spec008_v_the_committed_manifest_matches_the_bank` | FR-011, SC-004 | fails (no manifest) |
| `tests/unit/scripts/test_build_epa8_bank.py::test_spec008_v_a_hand_edited_epa8_bank_fails_the_check` | FR-012, US2-AS3 | fails |
| `…::test_spec008_v_the_committed_epa8_bank_passes_the_check` | FR-012, US2-AS3 | passes (pin) |
| `…::test_spec008_v_the_bank_job_runs_the_epa8_check` (reads `ci.yml`: the bank job runs `build_epa8_bank.py --check`) | FR-012 | fails |
| `…::test_spec008_v_the_generator_applies_the_bank_difficulty_rule` | FR-010 in the generator (II) | fails |

The tests that read `AGENTS.md`, `README.md` and `ci.yml` are text checks with no new dependency
(the bank job installs only pytest, so no YAML parser). New test files join the bank job's pytest
line (T010).

**Delivery A's pins stay green.** `test_validate_bank.py::_run` builds a temporary bank and runs
the validator in it; after V a bank without a manifest fails (O-V8), so `_run` also writes the
manifest for its temporary bank (by calling `appended_manifest`). That is a fixture change, not an
assertion change; every delivery A row keeps its assertions (T007).

## Owner decisions (open)

| # | Question | Recommended | Alternatives |
|---|---|---|---|
| **O-V1** | What is «an integer»? | Only a JSON integer: `900.0`, `"900"` and `true` fail. The bank has 0 of them (2,031 `int`), so nothing breaks, and the sync stores what the JSON says | Accept an integral float (`900.0`) as an integer; or also accept numeric strings |
| **O-V2** | Where do the rules live? | `src/domain/bank/rules.py` (pure, standard library), imported by `validate_bank.py` and `build_epa8_bank.py`; delivery C's catalogue module can sit beside it | Keep them in `scripts/validate_bank.py` (as `prose_read_as_math` is) and have the generator import from there |
| **O-V3** | Manifest format | `{"<id>": ["<course>", "<topic>"]}`, sorted by id, one line per entry (~117 KB): a diff shows one line per new id | An object of objects `{"course": …, "topic": …}` (~170 KB, more readable); or CSV (`id,course,topic`) |
| **O-V4** | How a new id enters the manifest | `scripts/update_id_manifest.py` appends; the validator fails on an unlisted bank id and names the command; CI never writes | The pre-commit hook runs the script automatically before `validate_bank.py` (still committed by the author); or the validator adds new ids itself when run with `--fix` |
| **O-V5** | How «never by hand» is enforced | CI compares the manifest with the pull request's base (`HEAD^1`, `fetch-depth: 2`, as the traceability job): an entry changed or removed fails. A hand-added line that matches the bank is indistinguishable from the script's and is harmless | Review only (no CI check): a PR that edits an entry and the bank together passes CI; or a digest of the manifest stored beside it (adds a file to keep in step) |
| **O-V6** | A manifest id that is no longer in the bank | **Error** until delivery L: removing an item does not stop it being served (survey B8, Reproduced), so it gains nothing and hides the item from review; L then turns removal into `"retired": true` | A warning in V that becomes an error in L; or allowed (the manifest keeps the id so reuse still fails) |
| **O-V7** | A legitimate change of topic — a typo fix or a rename of a whole topic | **Forbidden in V** (D4 as written): a rename re-keys ratings (R15), so it is a spec amendment with its own ratings repair, as T was | A `--rename-topic <course> <old> <new>` mode of the script that rewrites the manifest's entries for that pair, with a reviewer note in the PR — ratings stored on the old topic would keep counting in the course mean (survey B10) until a repair moves them |
| **O-V8** | No `items/id_manifest.json` | **Error**: deleting the file would otherwise switch D4 off | Skip the check with a warning when the file is absent |
| **O-V9** | How the EPA8 check compares | Byte for byte with what the generator writes (identical today), so a reformatted file also fails and the fix is always «regenerate» | Compare parsed JSON (ignores whitespace and key order; a hand reformat passes) |

Not an open decision (recorded): D4 forbids moves (a moved item gets a new id); D1 keeps the 32 easy
items; D6 puts the check in the bank job.

## Schema

**None.** V adds no column, table or index, touches neither repository nor `schema_version.py`,
and leaves `SCHEMA_VERSION` (6 on `redesign`; 7 if E3, PR #73, lands first) and
`MIGRATION_SOURCES_DIGEST` as they are. If review adds a database change to V, it takes the next
free version — 8 at the earliest — and becomes a migration under AGENTS § Database.

## Bank data and the transfer

**No change to `items/bank/` is needed**: 0 items fail D1, and the EPA8 bank is already the
generator's byte-exact output. The one new data file, `items/id_manifest.json`, is outside the
fingerprint's files, so **the bank fingerprint does not change**, no database resyncs at the next
start, and the transfer rehearsal (`scripts/rehearse_migration.py`, `docs/transfer.md`) is
unaffected. This holds for every recommended option; a choice that edits bank files (none
proposed) would change the fingerprint and must be flagged to the session that owns the transfer.

## Files the code PR touches (shared)

| File | Change | Shared with |
|---|---|---|
| `items/id_manifest.json` | new, generated by the script | — |
| `scripts/update_id_manifest.py` | new | — |
| `src/domain/bank/__init__.py`, `src/domain/bank/rules.py` (O-V2) | new | delivery C (catalogue module beside it) |
| `scripts/validate_bank.py` | D1 rule, manifest check | delivery C (course catalogue), delivery L (`retired`) |
| `scripts/build_epa8_bank.py` | `render`, `--check` compares, `--bank`, shared range | — |
| `.github/workflows/ci.yml` | bank job only: EPA8 step, manifest base step (`fetch-depth: 2`), new test files | every job (shared file) |
| `.pre-commit-config.yaml` | nothing required (the hook already runs the validator); optional per O-V4 | — |
| `tests/unit/scripts/test_validate_bank.py`, `tests/unit/infrastructure/test_bank_validator.py`, `tests/unit/infrastructure/test_bank_content.py` | new tests; `_run` writes a manifest; one pinned test flipped | delivery A, T rows |
| `tests/unit/scripts/test_build_epa8_bank.py`, `tests/unit/scripts/test_id_manifest.py`, `tests/unit/domain/test_spec008_v_bank_rules.py` | new | — |
| `AGENTS.md` | § Item bank: 400–2000; the manifest and its script; «Verify» adds `build_epa8_bank.py --check` | every session |
| `README.md` | line 262: 400–2000 | — |
| `docs/sdd/roadmap.md` | M8 status line | every session |
| `specs/008-item-bank/spec.md` | § Traceability rows of V, V `closed`; Code Scope entries (below) | — |

**Not touched**: `docs/transfer.md`, `ops/*`, `scripts/migrate.py`, `scripts/rehearse_migration.py`,
both repositories, `schema_version.py` — production transfer belongs to another session.

## Spec notes for the owner (no change made here)

- **Code Scope.** It names `scripts/validate_bank.py`, `scripts/build_epa8_bank.py` and
  `items/bank/`, but not `items/id_manifest.json`, `scripts/update_id_manifest.py` or the rules
  module. The checker requires each entry to name a tracked file, so the code PR adds them when they
  exist (recommended), or the spec drops the manifest from Code Scope coverage.
- **FR-010 vs AGENTS and README.** The spec says 400–2000; `AGENTS.md:645` and `README.md:262` say
  600–1800. FR-010 already orders AGENTS corrected; README is a stale summary corrected with it.
- **FR-012 vs the generator.** FR-012 assumes `--check` compares the bank with the generator's
  output; today it does not (measured). V adds the comparison; no spec text needs to change, but
  the spec's survey wording («CI does not run `--check`») understates the gap.
- **FR-011 «by a script».** The spec does not name the script; this plan proposes
  `scripts/update_id_manifest.py`.

## Risks and rollout

- **Authoring friction.** Every new item now needs one extra command (`update_id_manifest.py`);
  the validator's error names it. Any author's PR that adds items without it fails CI — intended.
- **Conflicts with C and L.** Both change `validate_bank.py`. V lands first (spec order: T before
  V; C and L after); C and L rebase on it.
- **No deploy effect.** No schema change, no resync, no runtime code: the deploy of V changes
  nothing a student sees.
