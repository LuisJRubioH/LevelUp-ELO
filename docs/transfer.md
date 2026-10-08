# Transfer of the redesign into the deployment repository

The redesign was built in the development copy `Ori-G-A/Oulad_redesing`, which deploys nothing.
This repository, `LuisJRubioH/LevelUp-ELO`, is the deployment repository: **its `main` deploys
automatically** (Vercel builds the frontend, Render redeploys the API and runs its migration on
start). This guide is the checklist for bringing the redesign into it. § 1 is the pull request from
the `redesign` branch; § 3–6 need the production hosts and credentials, so **only the owner runs
them**. Agents prepare and verify locally; they never merge that pull request and never run the
migration against production.

The order matters: back up and rehearse first, then migrate, then start the new code, then verify.

---

## 1. Code

1. **Source.** The branch `redesign` holds the development copy's history (its `main` at
   `461e999` and the constitution amendment `34b6da7`) with this repository's previous `main` as
   an ancestor, so the pull request to `main` shows the full replacement and the development
   history stays traceable.
2. **Review it as a pull request, never a direct push.** This repository's CI runs on it, Vercel
   builds a preview of it, and the owner reviews the diff against what is deployed today. Merging
   it is the switch (§ 5–6): do not merge before § 3–5 are done.
3. **Transfer only tracked files.** Never copy:

   | Path | Why |
   |---|---|
   | `.env`, `frontend/.env.local` | secrets — set them in the host instead (§ 3) |
   | `data/*.db` | local SQLite development data |
   | `node_modules/`, `frontend/dist/`, `.venv*/`, `__pycache__/` | rebuilt from lockfiles |
   | `.audit-python-runtimes.tmp/`, `*.tmp`, `test-results/` | local tooling output |
   | `.claude/`, `CLAUDE.md` | local agent configuration (gitignored) |

   `specs/`, `.specify/`, `docs/` and `AGENTS.md` are documentation; keep them if the final
   repository follows the same spec-driven process.
4. **Host configuration.** `render.yaml` (backend service, `autoDeploy: true`) and
   `frontend/vercel.json` (pnpm install and build, SPA rewrites, cache headers) describe the
   hosting. Vercel reads `frontend/vercel.json` on every build. Render applies `render.yaml` only
   if the service is managed as a Blueprint; otherwise its dashboard settings (start command,
   environment variables) are what runs, and they must be set by hand to match § 3.

## 2. Dependencies

| Part | Runtime | Install | Build / run |
|---|---|---|---|
| API (FastAPI) | Python **3.11** (`.python-version` = 3.11.9; CI uses 3.11) | `pip install -r requirements-api.txt` (constrained by `requirements-security.txt`) | `python scripts/migrate.py && uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| Frontend (React SPA) | Node **≥ 22.13**, pnpm **11.19.0** (`packageManager`) | `pnpm install --frozen-lockfile` in `frontend/` | `pnpm run build` (= `tsc -b && vite build`) → static files in `frontend/dist/` |
| V1 Streamlit (frozen) | Python 3.11 | `pip install -r requirements.txt` | only if V1 is deployed at all |

The API needs no scikit-learn, pandas or Streamlit: the API test suite and the PostgreSQL suite
pass with only `requirements-api.txt` importable. Serve `frontend/dist/` as static files with an
SPA fallback to `index.html`, and no cache on `index.html`, `manifest.webmanifest` and `sw.js`
(`frontend/vercel.json` has the exact headers).

## 3. Environment variables

Backend (`api/config.py`; `validate_runtime()` refuses to start in production if a critical one is
wrong):

| Variable | Value in the final environment |
|---|---|
| `ENVIRONMENT` | `production` — turns on the runtime checks below |
| `DATABASE_URL` | PostgreSQL for web traffic. On Supabase: the **transaction pooler, port 6543** |
| `MIGRATION_DATABASE_URL` | Only for `scripts/migrate.py`: a **direct connection (5432) or session pooler** — the migration's advisory lock is not reliable on the transaction pooler |
| `RUN_MIGRATIONS` | `0` on the web process; the schema is applied by the separate migration step |
| `WEB_CONCURRENCY` | `1` (required: PvP lobby and notification rooms live in process memory — AGENTS.md R18) |
| `JWT_SECRET_KEY` | ≥ 32 random characters (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `CORS_ORIGINS` | JSON list with the frontend's exact origin; no `localhost` in production |
| `RATE_LIMIT_STORAGE_URI` | shared Redis/Valkey URI; `memory://` is refused in production |
| `SUPABASE_URL`, `SUPABASE_KEY` | Storage for the **private** bucket `procedimientos` (images are served as bytes, never by public URL) |
| `ADMIN_USER`, `ADMIN_PASSWORD` | seed of the administrator account (only created if the password is set) |
| `SYSTEM_AI_API_KEY` | optional; without it AI features degrade gracefully. Optional per-feature keys: `AI_KEY_KATIA`, `AI_KEY_PROCEDURE`, `AI_KEY_STUDENT_ANALYSIS`, `AI_KEY_TEACHER_ANALYSIS` |
| `DATABASE_SSLMODE`, `LOG_LEVEL` | optional |

If V1 (Streamlit Community Cloud) is still deployed from `main`, it builds this same repository
and its repository bootstraps the schema on start unless told not to: set `RUN_MIGRATIONS=0` in its
secrets (or pause the app) before the merge, so that only the migration step migrates.

Frontend (build time): `VITE_API_URL` = the API's public origin. **Never** put a secret in a
`VITE_*` variable — Vite bundles them into the JavaScript every visitor downloads.

Order when the hosts are new: database → API (needs `DATABASE_URL`) → frontend (needs the API URL
as `VITE_API_URL`) → back to the API to set `CORS_ORIGINS` to the frontend's origin. Without the
last step the browser blocks every call and the API looks down.

## 4. Backups (before any migration)

1. **Database:** a full logical dump of the final database over a direct connection:

   ```bash
   pg_dump --format=custom --no-owner --no-privileges --file=pre-transfer-YYYYMMDD.dump "$MIGRATION_DATABASE_URL"
   ```

2. **Prove the dump restores:** `pg_restore --list pre-transfer-YYYYMMDD.dump` and a full restore
   into a scratch database (`createdb scratch && pg_restore --no-owner -d scratch pre-transfer-YYYYMMDD.dump`).
   An untested backup is not a backup.
3. **Storage:** export the `procedimientos` bucket (procedure images). The dashboard has no bulk
   download; `python scripts/backup_storage_bucket.py --out backup-procedimientos-YYYYMMDD
   --database-url "$MIGRATION_DATABASE_URL"` saves every object with a SHA-256 manifest and checks
   that each `procedure_submissions.storage_url` is in the backup (needs `SUPABASE_URL`,
   `SUPABASE_KEY`).
4. **Record the legacy rating state** for the reconciliation audit (§ 5) — row counts of
   `student_topic_elo`, `users` (with `current_elo`), `attempts` and `exam_sessions`.
5. Keep the dump and the export until § 6 passes. The dump holds student data: never commit it.

`scripts/rehearse_migration.py` runs steps 1, 2 and 4 and the whole § 5 rehearsal in one command,
against a throwaway local PostgreSQL, and exits non-zero if any check fails:

```bash
python scripts/rehearse_migration.py --source-url "$MIGRATION_DATABASE_URL" \
    --dump pre-transfer-YYYYMMDD.dump --scratch-url postgresql://u:p@localhost:5432/scratch \
    --report rehearsal-YYYYMMDD.txt
```

It dumps the `public` schema (the application's tables; Supabase's own schemas do not restore into
a plain PostgreSQL), so keep a full backup from the Supabase dashboard as well. `pg_dump` must be at
least as new as the server (the Supabase project uses PostgreSQL 17).

## 5. Migrations

All schema changes are **additive** (AGENTS.md R8: `CREATE … IF NOT EXISTS`, `ADD COLUMN IF NOT
EXISTS`, never `DROP` or a type change), and `scripts/migrate.py` is idempotent. Spec 001 adds:

| Change | Effect |
|---|---|
| table `student_course_topic_elo` (+ index) | the only rating state from now on, one row per student × course × topic |
| `pvp_matches.elo_reason_p1/p2` | why a PvP delta was or was not applied |
| `exam_sessions.global_elo_status` | `rated`/`pending` at exam submission; `NULL` on rows recorded before it (reported as `unknown`, never backfilled) |
| one-time **reconciliation** | turns eligible legacy `student_topic_elo` rows into **approximate baselines** with provenance (`origin`, `approximate`, `legacy_source_key`, `reconciled_at`); legacy rows are left unchanged; guarded by `pg_try_advisory_xact_lock(12345)`; a second run creates nothing |

After it, nothing writes `student_topic_elo` or `users.current_elo`.

**Rehearse on the restored copy first** (the scratch database from § 4):

```bash
MIGRATION_DATABASE_URL=<scratch db> python scripts/migrate.py   # prints "Migraciones completadas."
MIGRATION_DATABASE_URL=<scratch db> python scripts/migrate.py   # second run: must change nothing
```

Then check on the scratch database:

```sql
SELECT origin, approximate, COUNT(*) FROM student_course_topic_elo GROUP BY 1, 2;
SELECT COUNT(*) FROM student_topic_elo;                        -- equals the count from § 4
SELECT COUNT(*) FROM exam_sessions WHERE global_elo_status IS NULL;  -- all pre-existing rows
```

Every reconciled row must have `approximate = true` and a `legacy_source_key`; the second run must
not add rows. Only then run `scripts/migrate.py` against the final database, **before** the new web
process starts (with `RUN_MIGRATIONS=0` on the web process).

**Rollback.** Because the migration only adds, the previous application version still starts on
the migrated schema. But ratings written after the switch live only in `student_course_topic_elo`,
which the previous version does not read, so a rollback hides them. To return to the exact
pre-transfer state, restore the § 4 dump.

## 6. Verification in the final environment

**Before the switch** (on the final repository's pull request):

```bash
python scripts/db_sync_check.py          # SQLite ↔ PostgreSQL parity
python scripts/validate_bank.py          # item bank integrity
POSTGRES_TEST_DATABASE_URL=<disposable local db> ADMIN_PASSWORD=<test value> python -m pytest tests/ --ignore=tests/e2e -q
cd frontend && pnpm install --frozen-lockfile && pnpm run build && pnpm exec playwright test
```

`POSTGRES_TEST_DATABASE_URL` must point at a **throwaway local** PostgreSQL — `tests/conftest.py`
refuses any non-local host. Never point tests at the production database.

**After the switch:**

1. The migration step exits 0 and prints `Migraciones completadas.`; the web process started
   (startup does not swallow an initialisation error, and `validate_runtime()` stops it on a bad
   production setting).
2. `GET /api/health` → 200 (readiness: it queries the database and answers 503 if it cannot).
3. `GET /api/meta/ranks` → 200, 16 ranks ascending from "Aspirante" to "Leyenda Suprema", with
   `Cache-Control: public, max-age=3600`.
4. With a test student: stats shows a rating with its rank, or "Diagnóstico pendiente" — never a
   bare 1000; answering a practice question changes the topic rating by the previewed amount;
   reconciled topics show "aproximado"/≈; exam history loads.
5. With a test teacher: the dashboard lists students with display rating and rank label.
6. The SQL checks from § 5 return the same answers as on the rehearsal copy.

`scripts/verify_deployment.py --api-url <API> --frontend-url <SPA> --report verify-YYYYMMDD.txt`
runs 2–4 and more with the test accounts: health, ranks, CORS, login, a diagnostic, a practice answer
whose rating change equals the preview, the course map, every lesson image served by the frontend,
and a procedure uploaded, seen by the teacher with the same image bytes and graded. Run it from a
checkout of the deployed commit (it reads the lesson content to list the images).

## 7. Known operating constraints

- One API process only (`WEB_CONCURRENCY=1`) until matchmaking and notifications are shared —
  AGENTS.md R18.
- Do not raise the PostgreSQL pool above `(1, 5)` on a small plan; always return connections with
  `put_connection`.
- If the host sleeps idle services (free tiers), the first request after a pause takes about a
  minute; warm it with `GET /api/health` before a class. Capacity notes: `docs/arquitectura.md`
  § Capacidad.
