# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```

Must be launched from the repo root — `app.py` injects the project root into `sys.path` at runtime to resolve the `src/` package. There are no tests or linting configured in this project.

## Architecture

Clean Architecture with four layers inside `src/`:

- **`domain/`** — Pure business logic, no external dependencies. Contains the ELO engine (`elo/`) and adaptive question selector (`selector/`).
- **`application/services/`** — Use-case orchestrators: `StudentService` (answer processing, question selection) and `TeacherService` (dashboards, reports).
- **`infrastructure/`** — External dependencies: `persistence/sqlite_repository.py` (single ~1200-line file with schema, migrations, queries), `external_api/` (multi-provider AI client + math procedure review), `security/` (Argon2id hashing).
- **`interface/streamlit/app.py`** — Single-file UI with all panels and routing.

**Data flow for a student answer:**
1. `app.py` → `StudentService.process_answer()`
2. `CognitiveAnalyzer` calls AI to classify reasoning → `impact_modifier` ∈ [0.5, 1.5]
3. `VectorRating.update()` applies ELO delta per topic
4. `SQLiteRepository.update_item_rating()` updates item difficulty symmetrically
5. `save_attempt()` persists all metadata

## Key Domain Concepts

- **VectorRating**: Per-topic ELO (not one global rating). `aggregate_global_elo()` averages for display.
- **Dynamic K factor** (`domain/elo/model.py`): 40 (< 30 attempts) → 32 (< 1400 ELO) → 16 (stable) → 24 (default).
- **AdaptiveItemSelector**: Picks questions where P(success) ∈ [0.4, 0.75] (ZDP). Maximizes Fisher information `P*(1-P)`. Expands range ±0.05 per step if no candidates.
- **CognitiveAnalyzer** (`domain/elo/cognitive.py`): AI classifies confidence/error-type. Modifies ELO delta via `impact_modifier`.
- **Item ELO**: Items have their own difficulty rating that updates symmetrically (item "loses" when student wins).

## Database

- SQLite at `elo_project.db` in working directory, auto-created on first run.
- `SQLiteRepository.__init__()` runs: `init_db()` → `_migrate_db()` → `_seed_admin()` → `_backfill_prob_failure()` → `sync_items_from_bank_folder()`.
- Migrations are additive only (`ALTER TABLE ADD COLUMN IF NOT EXISTS`) — no destructive migrations.
- Admin user created only if env var `ADMIN_PASSWORD` is set (`ADMIN_USER` defaults to "admin"). No hardcoded credentials.
- Tables include: `users`, `groups`, `items`, `attempts`, `courses`, `enrollments`, `procedure_submissions`, `audit_group_changes`.

## Question Bank

Questions live in **`items/bank/`** as individual JSON files per topic (e.g., `algebra_lineal.json`, `calculo_diferencial.json`). Each file is an array of items. The filename (without extension) becomes the `course_id`.

Each item needs: `id` (unique string), `content` (supports LaTeX `$...$`), `difficulty` (ELO, 600–1800), `topic`, `options` (list), `correct_option` (must exactly match one option string).

On startup, `sync_items_from_bank_folder()` registers each file as a course and syncs items to the DB without overwriting existing ELO ratings.

## AI Integration

Multi-provider support via `ai_client.py`: Groq, OpenAI, Anthropic, Google Gemini, HuggingFace, LM Studio (local), Ollama (local). Provider auto-detected from API key prefix in the sidebar. All AI features degrade gracefully if unavailable.

Key AI functions:
- `get_socratic_guidance()` / `get_socratic_guidance_stream()` — student tutor (never reveals answer)
- `get_pedagogical_analysis()` — teacher dashboard analysis
- `analyze_performance_local()` — student stats, returns JSON recommendations
- `CognitiveAnalyzer` (`domain/elo/cognitive.py`) — classifies student reasoning for ELO impact
- `review_math_procedure()` (`math_procedure_review.py`) — Groq-only, vision model analyzes handwritten math procedures, returns JSON with step-by-step review and score 0–100 that nudges ELO

## User Roles

- **student**: Must belong to a group; practice mode + personal stats.
- **teacher**: Requires admin approval; creates groups, views student dashboards, generates AI reports.
- **admin**: Manages teacher approvals, group reassignment (audited), user activation/deactivation.
