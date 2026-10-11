# Item bank — as-is survey (spec 008 input)

Read-only survey of `redesign @ 1d6fcf6`, 2026-10-11. Input for `specs/008-item-bank/spec.md`
(roadmap M8: JSON schema, validation, course→block map, calibration). Under the roadmap's lean
scope, spec 008 is written the first time a feature touches the area. Several findings below are
fixed in their own PRs. The rest wait for that spec or for an owner decision.

Each finding cites code at that commit (`S` = `src/infrastructure/persistence/sqlite_repository.py`,
`P` = `src/infrastructure/persistence/postgres_repository.py`, `svc` =
`src/application/services/student_service.py`).

How each finding was checked:
- **Verified**: read in the code.
- **Measured**: computed over the bank files, read-only. This also covers the repository's own
  read-only checks: `validate_bank.py`, `build_epa8_bank.py --check`, `scan_dollar_prices.py` and
  `db_sync_check.py` (without `--fix`).
- **Reproduced**: run against a throwaway local database (SQLite or PostgreSQL 16) or through the
  test client.

Nothing here was run against production. The rating arithmetic (the item difficulty update and
the selector's target) belongs to spec 001. How a lesson uses items belongs to spec 003.

## 1. Where things live

| Concern | File |
|---|---|
| Practice bank | `items/bank/*.json` (13 files) and `items/bank/semillero/*.json` (36). 2,031 items, 2,031 unique ids. `course_id` = file name (P:3323, S:2957) |
| Sources, not loaded | `items/source/`: `caminos8/` (2,533 records), `hipertexto8/` (3,132, another schema), `epa8/` (60). `scripts/build_epa8_bank.py` projects `epa8/` into `items/bank/evaluar_para_avanzar_8.json` |
| Images | `items/images/` (86 files), `items/assets/epa8/` (53 SVGs); served by `api/main.py:104-106` |
| Validation | `scripts/validate_bank.py` (CI `ci.yml:33`, pre-commit `.pre-commit-config.yaml:45`); `scripts/scan_dollar_prices.py` (manual) |
| Sync to the database | `sync_items_from_bank_folder` P:3300-3483, S:2937-3052 (at bootstrap) |
| Course map | `_COURSE_BLOCK_MAP` P:76-131, S:2836-2891; `_COURSE_NAME_MAP`; parity in `scripts/db_sync_check.py:143-162` |
| Calibration | Item update `item_difficulty_delta` (`src/domain/elo/model.py:73-75`, `svc:158`); display calibrator `src/infrastructure/ml/calibration.py`; `scripts/train_calibrator.py`, `scripts/monthly_metrics.py` |
| Selection | `AdaptiveItemSelector` (`src/domain/selector/item_selector.py:40-80`); pool tiers in `svc:69-128` |

## 2. Actual behaviour

**Files.**
- Each item has the six required fields (AGENTS § Item bank).
- Optional fields: `tags` (585 items), `image_url` (566, of which 456 are empty), `image_path`
  (14), `block` (454). On DIAN and SENA items, `block` names a sub-area, not the course block.
- Options: 3 on 33 items, 4 on 1,948, 5 on 50.
- Course sizes range from 1 item (`aritmetica_semillero_10`) to 293 (DIAN). 19 courses have fewer
  than 10 items.

**Validation.**
- `validate_bank.py` scans `items/bank/` recursively and checks:
  - UTF-8, valid JSON, a list;
  - the required fields;
  - `correct_option` is one of `options`, exactly;
  - `difficulty` is numeric;
  - at least 2 options;
  - non-blank `id` and `content`;
  - ids unique across files.
- A difficulty outside [100, 3000] is only a warning.
- Today it passes with exit 0.

**Sync (every bootstrap, so every deploy).**
- Reads `bank/*.json` and `bank/semillero/*.json`. A file that does not parse is logged and
  skipped.
- A new id is inserted with RD 350.
- For an existing id, content, options, key, topic, course, image, tags and block are updated.
  `difficulty` and `rating_deviation` are never touched, on purpose: calibration by use is
  preserved (P:3374-3379).
- Nothing is ever deleted, neither items nor courses.
- A new course gets its block and name from the maps.
- An unmapped course gets «Universidad». An unnamed course takes the first item's topic.

**Calibration.**
- After each valid answer, the item's difficulty moves by `32·((1−result) − (1−P))`, with no
  bounds.
- The item's RD stays at 350 (`svc:183`).
- A display-only isotonic calibrator can adjust the stored `expected_score` and `prob_failure`.
  The rating update always uses the raw P.
- `monthly_metrics.py` lists items at 0 % success with ≥ 10 attempts and advises "recalibrar o
  retirar".

**Selection.**
- Candidate items:
  - the pool is the course's items;
  - a topic filter with no items falls back to the whole course;
  - items answered correctly this session are excluded.
- Order of preference:
  1. unseen items;
  2. items failed at least 3 questions ago;
  3. items already answered.
- Within that, the selector takes difficulties within ±250 and targets P ∈ [0.40, 0.75],
  widening step by step.

## 3. Findings

| # | Kind | Finding | Evidence | Status |
|---|---|---|---|---|
| B1 | **Bug** | **The EPA8 figures were never served.** 41 items of `evaluar_para_avanzar_8` point to `items/assets/epa8/*.svg`; the API mounted only `/items/images`, so the React app got 404 and showed the statement without its drawing. V1 reads from disk and was unaffected. | `api/main.py:104-106`; `frontend/src/api/client.ts:208-215` | **Reproduced** (test client). Fixed in #45 |
| B2 | **Data** | **A wrong answer key.** `Septimo_Aritmetica_2013_F2_Q4` was keyed 8880; the answer is 9880, as in its sixth-grade copy. | `semillero/aritmetica_semillero_7.json:115` | **Measured**. Fixed in #48 |
| B3 | **Data** | **Two right answers.** `q47` offered the same expression twice, once with an extra space; only one was the key. | `calculo_integral.json:81` | **Measured**. Fixed in #48 |
| B4 | **Data** | **Currency read as math.** In DIAN `B_Adu_05`, two peso amounts turned the prose between them into one formula. `scan_dollar_prices.py` misses it and flags three EPA8 items that are fine (`$\$…$`). | `DIAN.json:1908`; `scripts/scan_dollar_prices.py` | **Measured**. Fixed in #26, which also adds the check to `validate_bank.py` |
| B5 | **Bug** | **The calibration scripts crashed on SQLite.** SQLite's `get_all_attempts_for_calibration` called `dict(row)` on plain tuples, which raises with the first attempt. `train_calibrator.py` and `monthly_metrics.py` both read it. | S:1463 | **Reproduced**. Fixed in #49 |
| B6 | **Rule** | **32 items sit below the documented difficulty range.** They are at 500 or 550, against the 600–1800 range in AGENTS § Item bank, in `algebra_semillero_7` (3), `algebra_semillero_8` (6), `aritmetica_semillero_6` (1), `aritmetica_semillero_7` (1) and `aritmetica_semillero_8` (21). The validator's range is [100, 3000] and only warns. | `scripts/validate_bank.py:29, 62-66` | **Measured**. Decision 1 |
| B7 | **Validation** | **The validator misses most content rules.** It does not check: the 600–1800 range or an integer difficulty; R5 escaping and unbalanced `$`; that image files exist; course-map membership; repeated options or content; a blank `topic`. A non-object item crashes it. It scans subfolders the sync never loads. | `scripts/validate_bank.py:27-83, 132` | Verified. #26 and #48 add two content checks. Decision 2 |
| B8 | **Lifecycle** | **Nothing retires an item.** The schema has no retired flag, the sync never deletes, and `get_items_from_db` filters only by course. An item removed from the JSON keeps being served from any database that loaded it, as the 25 old `algebra_semillero` items (`albS1`…) and their course still are. "Recalibrate or retire" cannot be done. | S:131-140, P:387-396; P:3912, S:3318; `scripts/monthly_metrics.py:100` | Verified. Decision 3 |
| B9 | **Calibration** | **A difficulty edited in the JSON never reaches an existing item**, so AGENTS' manual-calibration formula has no way in. Item difficulty has no bounds, and item RD never changes. | P:3374-3379; `svc:158, 183` | Verified. Decision 4 |
| B10 | **Sync** | **Some edits silently change meaning.** A changed `topic` or a file move re-points the item's future ratings to another (course, topic). A changed key does not re-score past attempts. | P:3452-3467; S:3031-3049 | Verified. Decision 5 |
| B11 | **Parity (R1)** | **PostgreSQL never updates a course's name or block.** SQLite does when the map changes; PostgreSQL only inserts (`ON CONFLICT DO NOTHING`), so a block or name change in the map never reaches production. | P:3388-3390, 3434-3439; S:2992-3005 | Verified |
| B12 | **Cost** | **PostgreSQL rewrites every item on every boot.** The "nothing to do" exit can never trigger, because every existing item is queued for an update, and `executemany` is one round trip per row: 2,031 UPDATEs per deploy. The docstring's "at most 2 SELECTs + 2 INSERTs" is stale. SQLite runs about 4,000 statements. | P:3304, 3430, 3452 | Verified |
| B13 | **Robustness** | **One bad item aborts the whole bootstrap.** A missing key does it on both engines. SQLite's sync has no `try/finally`, so an error also leaks its connection. | S:2952-3052 | Verified |
| B14 | **Map** | **The course map and the bank files are not checked against each other.** `aritmetica` is in both maps with no file. An unmapped course silently becomes «Universidad». In SQLite, an unnamed course takes its first item's topic, so reordering items renames it. | P:86, 3383-3386; S:2846, 2987-2990 | Verified |
| B15 | **Calibrator** | **The isotonic calibrator never runs.** Pickles are gitignored and `models/` does not exist, so it is inactive on every deploy. Even when trained: it trains on the stored `expected_score`, which is its own output once active; per-level models are never loaded; the API loads the model on every request; `concursos` is missing from the scripts' levels; and the bias line carries the AUC flag. | `.gitignore:93-94`; `scripts/train_calibrator.py:51, 75, 96-121`; `api/routers/student.py:94-98`; `scripts/monthly_metrics.py:65, 69` | Verified. Decision 6 |
| B16 | **Side effect** | **The reporting scripts write to the database.** `train_calibrator.py` and `monthly_metrics.py` build a full repository, which runs the schema bootstrap against `DATABASE_URL`: migrations, bank sync and, outside `ENVIRONMENT=production`, demo seeding. | `scripts/train_calibrator.py:30-38`; `scripts/monthly_metrics.py:21-29`; P:249-262 | Verified |
| B17 | **Selection** | **Edge cases in small courses.** When only cooldown items are left, they are served at once, which breaks the 3-question spacing in courses of 1–3 items. Items answered correctly repeat once the course is exhausted. An empty course with a rating ≥ 1800 reports "mastery" instead of "empty". | `svc:84-110` | Verified (the repeat is pinned by spec 001) |
| B18 | **Data** | **Smaller content issues.** Three pairs of identical questions within `algebra_semillero_8`. 81 groups of identical questions across courses, mostly reused between grades 6 and 7. `gs_7_01` has conflicting `image_url` and `image_path`. `EPA8-C1-2020-P14` mentions a figure it does not have. Option images of three EPA8 items are dropped by the build script. 33 image files are never shown (32 referenced by no item; one only by the `image_path` that `gs_7_01`'s `image_url` overrides). | `semillero/algebra_semillero_8.json`; `evaluar_para_avanzar_8.json:229`; `scripts/build_epa8_bank.py` (`CAMPOS_BANCO`) | **Measured** |
| B19 | **Model** | **Topics are too fine-grained for per-(course, topic) ratings.** DIAN has 209 topics for 293 items, and EPA8 59 for 60. 376 of the 440 (course, topic) pairs have at most 2 items, so most topic ratings rest on one or two questions. | bank files | **Measured**. Decision 7 |
| B20 | **Dead code / tests** | `sync_items_from_json` (P:3868, S:3276) and `update_item_rating` (P:4199, S:3582) have no callers. `tests/integration/test_sqlite_repository.py:23-47` writes a JSON file and never calls the sync. | — | Verified |

## 4. Existing evidence

- **Validator:** `tests/unit/infrastructure/test_bank_validator.py`. It covers `validate_item` and
  `validate_file` on synthetic data and pins the [100, 3000] warning. #26 adds
  `tests/unit/scripts/test_validate_bank.py`.
- **Bank content:**
  - new in #45: `tests/api/test_item_images_served.py` (every image is served);
  - new in #48: `tests/unit/infrastructure/test_bank_content.py` (no repeated answer; copies share
    the key).
- **Selection:**
  - `tests/unit/domain/test_item_selector.py`;
  - `tests/unit/domain/test_spec001_engine_pins.py`;
  - `tests/unit/application/test_spec001_service_pins.py`.
- **Bank-dependent:**
  - `tests/integration/test_elo_single_source.py` (items exist);
  - `tests/integration/test_migrate_lock.py` (the sync's lock);
  - `tests/integration/test_spec001_catalogue.py` (blocks).
- **Calibration:** new in #49, `tests/integration/test_calibration_attempts.py` (both engines).
- **Not covered:**
  - the sync's update and no-delete behaviour, and its parity between engines;
  - the course map against the files;
  - the calibrator and the scripts;
  - `scan_dollar_prices.py`;
  - the 600–1800 rule.

## 5. Decisions for the owner (input for `/speckit-clarify`)

None blocks the transfer (PR #3).

1. **Difficulty range (B6).** Is 600–1800 the rule? If so, raise the 32 items to 600 and make the
   validator reject values outside the range. If not, widen the documented range.
2. **Validator (B7).** Which rules should fail CI: the range, R5 escaping, existing image files,
   course-map membership, repeated options?
3. **Retiring items (B8).** Add a retired flag that the selector respects, or delete from the
   database what leaves the JSON? Who retires, and from where (the bank file, an admin screen)?
4. **Manual difficulty (B9).** Should a difficulty edited in the JSON override the calibrated one,
   for example through an explicit field such as `difficulty_override`? Should item difficulty
   have bounds?
5. **Moving or re-keying an item (B10).** What happens to ratings when an item changes topic or
   course, and to past attempts when its key is corrected? Examples are B2 and B3.
6. **Calibrator (B15).** Ship a trained model and fix its loop, or remove it?
7. **Topic granularity (B19).** Merge the fine topics of DIAN and EPA8 into broader ones for
   ratings? That needs a spec 001 decision, because ratings are keyed by (course, topic).

## 6. Proposed scope for spec 008 (draft)

- **In:**
  - the item file schema and its validation;
  - the sources-to-bank build (`build_epa8_bank.py`);
  - the sync into both databases: insert, update, retire, courses;
  - the course→block and course→name maps;
  - images;
  - item calibration tooling: manual difficulty, the scripts, the display calibrator.
- **Out:**
  - the rating and difficulty update formulas and the selector's targets (spec 001);
  - lesson content and nodes (spec 003);
  - PvP item choice (spec 007).
