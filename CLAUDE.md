# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```

Must be launched from the **repo root** — `app.py` injects the project root into `sys.path` at runtime to resolve the `src/` package. There are no tests or linting configured in this project.

## Architecture

Clean Architecture with four layers inside `src/`:

- **`domain/`** — Pure business logic, no external dependencies.
  - `elo/model.py` — Dynamic K factor, classic ELO, `Item`/`StudentELO` dataclasses.
  - `elo/vector_elo.py` — `VectorRating`: per-topic ELO + Rating Deviation (RD).
  - `elo/uncertainty.py` — `RatingModel` (Glicko-simplified): RD initial=350, min=30, decay=RD×0.95 per attempt.
  - `elo/cognitive.py` — `CognitiveAnalyzer`: classifies student responses via AI → `impact_modifier` ∈ [0.5, 1.5].
  - `elo/zdp.py` — ZDP interval calculation.
  - `selector/item_selector.py` — `AdaptiveItemSelector`: question selection via Fisher Information.

- **`application/services/`** — Use-case orchestrators:
  - `student_service.py` — `process_answer()`, `get_next_question()`, `get_socratic_help()`.
  - `teacher_service.py` — Dashboard analysis and AI reports.

- **`infrastructure/`**
  - `persistence/sqlite_repository.py` — SQLite implementation: schema, migrations, seed, queries (~1200 lines). Used as local fallback.
  - `persistence/postgres_repository.py` — PostgreSQL implementation (psycopg2): full port of SQLite repo for production (Supabase). Uses `SimpleConnectionPool(1–5)`, `RealDictCursor`, `ON CONFLICT DO NOTHING`, `SERIAL PRIMARY KEY`, `BYTEA`. Connection pooling eliminates per-query TCP+SSL overhead. Retry logic for `DeadlockDetected`/`QueryCanceled` in migrations.
  - `persistence/seed_test_students.py` — Idempotent seed of 5 test students (never overwrites existing ELO/progress). Used by SQLite repo; PostgreSQL repo has inline equivalent.
  - `external_api/ai_client.py` — Universal multi-provider AI client.
  - `external_api/math_procedure_review.py` — Groq + Llama 4 Scout vision review of handwritten procedures.
  - `external_api/model_router.py` — Intelligent model router: selects best model per task type (`tutor_socratic`, `image_procedure_analysis`, `general_chat`).
  - `external_api/model_capability_detector.py` — Auto-detects vision/reasoning/speed capabilities from model name heuristics.
  - `external_api/symbolic_math_verifier.py` — SymPy-based 4-layer algebraic verification (simplify → expand → abs equivalence → numeric fallback).
  - `external_api/math_step_extractor.py` — Extracts and classifies math steps from OCR output.
  - `external_api/math_ocr.py` — OCR pipeline: pix2tex > tesseract > regex.
  - `external_api/math_reasoning_analyzer.py` — Step-by-step reasoning analysis.
  - `external_api/pedagogical_feedback.py` — Rotating Socratic hints by error type (never reveals answer).
  - `external_api/math_analysis_pipeline.py` — Full pipeline: OCR → steps → symbolic verification → feedback.
  - `security/hashing_service.py` — Argon2id hashing + transparent migration from legacy SHA-256.

- **`interface/streamlit/app.py`** — Single-file UI: login, student panel, teacher dashboard, admin panel.

**Data flow for a student answer:**
1. `app.py` → `StudentService.process_answer()`
2. `CognitiveAnalyzer` calls AI → `impact_modifier`
3. `VectorRating.update()` applies ELO delta per topic
4. `Repository.update_item_rating()` updates item difficulty symmetrically (SQLite or PostgreSQL)
5. `save_attempt()` persists all metadata

## Key Domain Concepts

- **VectorRating**: Per-topic ELO + RD (not one global rating). `aggregate_global_elo()` averages for display.
- **Dynamic K factor** (`domain/elo/model.py`):
  - K=40 (< 30 attempts) → K=32 (ELO < 1400) → K=16 (stable, error < 15% in last 20) → K=24 (default).
  - Effective K scales with RD: `K_eff = K_BASE × (RD / RD_BASE)`.
- **AdaptiveItemSelector**: Picks questions where P(success) ∈ [0.4, 0.75] (ZDP). Maximizes Fisher Information `P×(1−P)`. Expands ±0.05 per step (up to 10 steps) if no candidates. Prioritizes unseen questions, then failed ones with ≥3 cooldown.
- **CognitiveAnalyzer**: Classifies confidence [0,1] and error type (`conceptual`/`superficial`). Combined with response time to compute `impact_modifier`.
- **Item ELO**: Items have their own difficulty rating that updates symmetrically (item "loses" when student wins).
- **16-level ELO ranking**: Aspirante (0–399) → Leyenda Suprema (2500+).
- **Study streak**: Consecutive days of activity tracked and displayed.

## Database

**Dual-backend**: app.py auto-selects based on environment:
- If `DATABASE_URL` is set → `PostgresRepository` (production, Supabase).
- Otherwise → `SQLiteRepository` (local development, file `data/elo_database.db`).

**SQLite** (local): file at `data/elo_database.db` (fixed path, auto-created). Override with env var `DB_PATH`.

**PostgreSQL** (production): reads `DATABASE_URL` env var (format: `postgresql://user:pass@host:port/dbname`). Uses `psycopg2` with `SimpleConnectionPool(minconn=1, maxconn=5)` to reuse TCP+SSL connections. URL parsed via regex to handle special characters in passwords. `sslmode='require'` and `statement_timeout=60000` (60s) on every connection.

Both repositories run on init: `init_db()` → `_migrate_db()` → `_seed_admin()` → `_seed_demo_data()` → `_backfill_prob_failure()` → `sync_items_from_bank_folder()` → `_seed_test_students()`.
- Migrations are **additive only** (`ALTER TABLE ADD COLUMN IF NOT EXISTS`) — no destructive migrations.
- PostgreSQL migrations use retry logic (3 attempts) for `DeadlockDetected`/`QueryCanceled` with `time.sleep(2)` between retries.
- Admin user created only if env var `ADMIN_PASSWORD` is set (`ADMIN_USER` defaults to `"admin"`). No hardcoded credentials.

### Tables

| Table | Key details |
|---|---|
| `users` | `role` (student/teacher/admin), `approved`, `active`, `group_id`, `education_level`, `is_test_user` (protects against deletion), `rating_deviation` |
| `groups` | Unique index on `(teacher_id, name_normalized)` — no duplicate group names per teacher (case-insensitive) |
| `items` | `difficulty`, `rating_deviation`, `image_url` (optional) |
| `attempts` | `elo_after`, `prob_failure`, `expected_score`, `time_taken`, `confidence_score`, `error_type`, `rating_deviation` |
| `courses` | `id` (slug), `name`, `block` (Universidad/Colegio/Concursos) |
| `enrollments` | `user_id`, `course_id`, `group_id` |
| `procedure_submissions` | `image_data` (BLOB/BYTEA), `status`, `ai_proposed_score` (never affects ELO directly), `teacher_score` (official), `final_score` = teacher_score, `elo_delta` = (final_score−50)×0.2, `file_hash` (SHA-256 anti-plagiarism) |
| `audit_group_changes` | Log of group reassignments by admin |

### Test users (seed_test_students.py — idempotent)

| User | Password | Level |
|---|---|---|
| `profesor1` | `demo1234` | Teacher (pre-approved) |
| `estudiante1` | `demo1234` | Universidad |
| `estudiante2` | `demo1234` | Colegio |
| `estudiante_colegio_1..3` | `test1234` | Colegio (`is_test_user=1`) |
| `estudiante_universidad_1..2` | `test1234` | Universidad (`is_test_user=1`) |

## Question Bank

Questions live in **`items/bank/`** as individual JSON files per course. Filename (without extension) = `course_id`.

Required fields per item: `id` (unique string), `content` (LaTeX `$...$`), `difficulty` (600–1800), `topic`, `options` (list), `correct_option` (exact match).

Optional: `image_url` or `image_path` — displayed below the question stem. If both present, `image_url` takes priority. Missing/broken image never breaks UI.

**Important**: LaTeX backslashes must be escaped in JSON (`\\frac`, `\\sin`, etc.).

`sync_items_from_bank_folder()` on startup registers courses and syncs items **without overwriting** existing ELO ratings.

### Course catalog

| File | Course | Block |
|---|---|---|
| `algebra_lineal.json` | Álgebra Lineal | Universidad |
| `calculo_diferencial.json` | Cálculo Diferencial | Universidad |
| `calculo_integral.json` | Cálculo Integral | Universidad |
| `calculo_varias_variables.json` | Cálculo de Varias Variables | Universidad |
| `ecuaciones_diferenciales.json` | Ecuaciones Diferenciales | Universidad |
| `probabilidad.json` | Probabilidad | Universidad |
| `algebra_basica.json` | Álgebra Básica | Colegio |
| `aritmetica_basica.json` | Aritmética Básica | Colegio |
| `trigonometria.json` | Trigonometría | Colegio |
| `geometria.json` | Geometría | Colegio |
| `DIAN.json` | Concurso DIAN — Gestor I | Concursos |
| `SENA.json` | Concurso SENA — Profesional 10 | Concursos |

To add a new course: create the JSON, add entry to `_COURSE_BLOCK_MAP` in both `sqlite_repository.py` and `postgres_repository.py`, restart.

## AI Integration

Multi-provider via `ai_client.py`. Provider auto-detected from API key prefix in sidebar:

| Prefix | Provider |
|---|---|
| `sk-ant-` | Anthropic |
| `gsk_` | Groq |
| `AIzaSy` | Google Gemini |
| `hf_` | HuggingFace |
| `sk-proj-`/`sk-` | OpenAI |
| (none) | LM Studio / Ollama local |

All AI features **degrade gracefully** if unavailable (fallback to neutral values).

**Model Router** (`model_router.py`): selects best model per task. Sources in priority order: manual registry → provider defaults → heuristic name detection.

**Socratic validation** (`validate_socratic_response()`): post-generation check that response doesn't reveal the answer and is ≤3 sentences. `SOCRATIC_MAX_TOKENS = 120`.

**Math procedure review** (`math_procedure_review.py`): Groq-only, uses `meta-llama/llama-4-scout-17b-16e-instruct`. Returns JSON with step evaluation and `score_procedimiento` (0–100). ELO adjustment: `(score − 50) × 0.2`. Applied once per item (flag `proc_elo_applied_{item_id}`).

**Symbolic math pipeline** (`symbolic_math_verifier.py`): 4-layer verification with SymPy. Error diagnosis: `incorrect_distributive`, `sign_error`, `fraction_simplification`, `not_equivalent`. Optional dependency — degrades gracefully.

**Procedure relevance validation** (`validate_procedure_relevance()`): light YES/NO check before submission. After 3 failed attempts, alternative options are offered.

**Anti-plagiarism**: SHA-256 hash of each uploaded file compared against prior submissions for same student+item.

## Security

- **Argon2id** (via `passlib[argon2]`) for all passwords.
- Transparent migration from legacy SHA-256: replaced on next login.
- Accounts with empty/null password hash are auto-deactivated on DB migration.
- API keys stored only in Streamlit session memory — never persisted to DB.
- Admin credentials via env vars only (`ADMIN_PASSWORD`, `ADMIN_USER`).

## User Roles

- **student**: Must belong to a group. Practice mode + personal stats + procedure submissions + feedback center (with unread badge).
- **teacher**: Requires admin approval. Creates/manages groups (unique names per teacher). Dashboard with cascade filters (Group → Level → Subject). Reviews and scores procedures (badge shows pending count). Generates AI pedagogical analysis per student.
- **admin**: Approves teachers, reassigns students between groups (audited), deletes groups, activates/deactivates users. All destructive actions require UI confirmation.

## Important Implementation Notes

- **Dual DB backend**: `DATABASE_URL` env var → PostgreSQL (Supabase); absent → SQLite local. Both repos have identical public API.
- **PostgreSQL connection pool**: `SimpleConnectionPool(1–5)` reuses TCP+SSL connections. Never call `conn.close()` — use `self.put_connection(conn)` to return to pool.
- **PostgreSQL uses `RealDictCursor`**: all row access is `row['column_name']`, never `row[0]`. Date fields return `datetime` objects (not strings) — always wrap with `str()` before slicing (e.g., `str(row['created_at'])[:10]`).
- **`_COURSE_BLOCK_MAP`** exists in both `sqlite_repository.py` and `postgres_repository.py` — keep them in sync when adding courses.
- **DB path (SQLite)**: `data/elo_database.db` (fixed). Override with `DB_PATH` env var.
- **`is_test_user=1`**: these students are protected against deletion — never remove this flag.
- **Streamlit Cloud**: uses `DATABASE_URL` pointing to Supabase PostgreSQL for persistent data. SQLite fallback is for local development only.
- **Single-file UI**: `app.py` is intentionally monolithic. Be careful with changes — all panels share session state via `st.session_state`.
- **Procedure ELO**: `ai_proposed_score` never directly affects ELO. Only `teacher_score` (via `final_score`) does.
