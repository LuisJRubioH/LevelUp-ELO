# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (must be run from the repo root)
streamlit run src/interface/streamlit/app.py
```

The app must be launched from the repo root because `app.py` injects the project root into `sys.path` at runtime to resolve imports (the `src/` package structure requires this).

## Architecture

The project follows Clean Architecture with four layers inside `src/`:

```
src/
├── domain/          # Core business logic, no external dependencies
│   ├── elo/         # ELO engine: model.py, vector_elo.py, uncertainty.py, cognitive.py, zdp.py
│   └── selector/    # AdaptiveItemSelector (ZDP-based question picker)
├── application/     # Use-case orchestrators
│   └── services/    # StudentService, TeacherService
├── infrastructure/  # External dependencies
│   ├── persistence/ # SQLiteRepository (single file: elo_project.db)
│   ├── external_api/# ai_client.py — calls LM Studio over HTTP
│   └── security/    # Argon2id hashing + legacy SHA-256 migration
└── interface/
    └── streamlit/   # app.py — single-file UI, all panels and routing
```

**Data flow for a student answer:**
1. `app.py` calls `StudentService.process_answer()`
2. `StudentService` invokes `CognitiveAnalyzer` (AI confidence/error-type classification)
3. `VectorRating.update()` applies ELO delta with a cognitive `impact_modifier`
4. `SQLiteRepository.update_item_rating()` updates the item's own ELO symmetrically (item loses difficulty when student wins)
5. Attempt is persisted via `save_attempt()`

## Key Domain Concepts

- **VectorRating**: Each student holds a separate ELO rating per topic (not one global rating). `aggregate_global_elo()` averages them for display.
- **Dynamic K factor**: Starts at 40 (first 30 attempts), drops to 32 (below 1400 ELO), then to 16 (stable performance). Defined as constants in `domain/elo/model.py`.
- **AdaptiveItemSelector**: Selects questions where success probability P is in [0.4, 0.75] (ZDP). Maximizes Fisher information `P*(1-P)` among candidates. Expands the range by ±0.05 per step if no candidates found.
- **CognitiveAnalyzer** (`domain/elo/cognitive.py`): Calls the local LM Studio AI to classify student reasoning as confident/unconfident and errors as conceptual/superficial. The result modifies the ELO delta via `impact_modifier` (range [0.5, 1.5]).
- **Item ELO**: Items have their own `difficulty` rating that updates symmetrically — if the student wins, the item's difficulty decreases.

## Database

- SQLite file created at `elo_project.db` in the working directory.
- `SQLiteRepository.__init__()` runs `init_db()` → `_migrate_db()` → `_seed_admin()` → `_backfill_prob_failure()` on every startup.
- Schema migrations are additive (`ALTER TABLE ADD COLUMN IF NOT EXISTS` pattern) — no destructive migrations.
- Default admin credentials: `admin` / `admin123` (seeded automatically if not present).
- Questions from `items/bank.json` are synced to the `items` table via `sync_items_from_json()` without overwriting existing ELO ratings.

## AI Integration (LM Studio)

- All AI calls go to a local LM Studio instance at `http://192.168.40.66:1234/v1` by default.
- The URL and model are configurable per-session in the Streamlit sidebar.
- Three AI functions in `infrastructure/external_api/ai_client.py`:
  - `get_socratic_guidance()` — student tutor (socratic hints, never reveals answer)
  - `get_pedagogical_analysis()` — teacher dashboard analysis
  - `analyze_performance_local()` — student stats panel, returns JSON recommendations
- `CognitiveAnalyzer` in `domain/elo/cognitive.py` also calls LM Studio directly.
- All AI features degrade gracefully if LM Studio is unavailable (fallback returns hardcoded neutral values).

## User Roles

Three roles with different access:
- **student**: Must belong to a group; accesses practice mode and personal stats.
- **teacher**: Requires admin approval; can create groups, view student dashboards, generate AI reports.
- **admin**: Auto-approved; manages teacher approvals, group reassignment (with audit log in `audit_group_changes` table), and user deactivation.

## Adding Questions

Edit `items/bank.json`. Each item needs: `id` (unique string), `content` (supports LaTeX), `difficulty` (numeric ELO, e.g. 600–1800), `topic`, `options` (list), `correct_option` (must exactly match one option string). On next app startup the item is synced to the DB automatically.
