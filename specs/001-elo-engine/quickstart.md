# Quickstart: validating spec 001 (ELO engine)

How to prove the feature works. Test files and names are fixed in `tasks.md`; the
FR → test mapping lives in `spec.md` § Traceability.

## Prerequisites

```bash
pip install -r requirements-api.txt
cd frontend && pnpm install --frozen-lockfile && cd ..
```

PostgreSQL branch of the integration tests: without `POSTGRES_TEST_DATABASE_URL` it is **skipped**
(the 11 skips of a plain local run). Run it locally against a disposable database:

```bash
docker run -d --rm --name spec001-pg -p 5433:5432 -e POSTGRES_PASSWORD=spec001 postgres:16-alpine
POSTGRES_TEST_DATABASE_URL=postgresql://postgres:spec001@localhost:5433/postgres ADMIN_PASSWORD=testadmin123 python -m pytest tests/integration -q -rs
```

or rely on the CI job `test-postgres` (it runs only the files it lists — task T003).

## 1. Pins before refactoring (must pass on the unchanged code)

Characterization tests follow the existing layout (constitution § Code Style): `tests/unit/domain/`,
`tests/integration/` (both engines), `tests/api/`. New tests contain `spec001` in their name;
reused pins live in existing files. This is the same selection as task T022 (the pin gate):

```bash
ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q -k "spec001 or elo_single_source or pvp_repository or item_selector or elo_model or student_service or procedure_grading"
```

```powershell
$env:ADMIN_PASSWORD = "testadmin123"; python -m pytest tests/ --ignore=tests/e2e -q -k "spec001 or elo_single_source or pvp_repository or item_selector or elo_model or student_service or procedure_grading"
```

Expected: all green on the unchanged code before any implementation task (agent rule 6).

## 2. Full verification after implementation

```bash
ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q
python scripts/db_sync_check.py
cd frontend && pnpm run build
```

Expected: green; `db_sync_check` reports parity.

## 3. Reconciliation on a copy of real data

SQLite (local copy; the repository bootstrap runs reconciliation):

```bash
cp data/elo_database.db "$TEMP/recon.db"
DB_PATH="$TEMP/recon.db" python -c "from src.infrastructure.persistence.sqlite_repository import SQLiteRepository as R; R(); R()"
```

PostgreSQL (deploy path): `python scripts/migrate.py` with `MIGRATION_DATABASE_URL` set; run it
twice against a staging copy.

Check, for one student who had legacy rows:
- every reconciled row has `approximate = true` and a `legacy_source_key` (FR-034a);
- no reconciled row combines two legacy rows (FR-035);
- legacy rows are unchanged; the second run creates 0 rows (FR-036, SC-008).

## 4. Manual end-to-end check (V2)

1. Start backend and frontend (AGENTS.md § Quickstart). Log in as `estudiante_semillero_1`.
2. Enter a course without a diagnostic → overall rating shows **"pending diagnostic"** (FR-028b).
3. Take the diagnostic → overall rating and rank appear; the rank label matches on the student
   stats screen and in the teacher dashboard for the same student (FR-031, SC-005).
4. Practise: the preview shown before answering equals the `delta_elo` returned (SC-006).
5. Answer in < 3 s → response shows `delta_elo = 0`, `elo_valid = false` (FR-009).
6. Home page lists the 16-level scale from `/api/meta/ranks`.

## 5. Capacity guard

```bash
python scripts/measure_capacity.py
```

Expected: CPU-ms per request within 10 % of the 26 CPU-ms baseline (`docs/arquitectura.md`).
