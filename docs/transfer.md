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

Frontend (build time): `VITE_API_URL` = the API's public origin. **Never** put a secret in a
`VITE_*` variable — Vite bundles them into the JavaScript every visitor downloads.

Order when the hosts are new: database → API (needs `DATABASE_URL`) → frontend (needs the API URL
as `VITE_API_URL`) → back to the API to set `CORS_ORIGINS` to the frontend's origin. Without the
last step the browser blocks every call and the API looks down.

### 3.1 V1 (Streamlit Community Cloud) during the switch

V1 must have no way into the production database from the backup until the owner decides what to
do with it, for two reasons:

- **Before the merge, Streamlit runs the old code** (`main`), which knows no `RUN_MIGRATIONS`.
  Every answer moves the legacy ratings (`student_topic_elo`, `users.current_elo`). Whatever it
  writes after the backup is lost by a rollback, and rating changes it makes after the migration
  land in tables the new version no longer reads.
- **The merge redeploys V1 with the new code.** Still connected and without `RUN_MIGRATIONS=0`,
  its first session runs the whole bootstrap from a web session: schema, reconciliation, and demo
  and test accounts unless `ENVIRONMENT=production`. It uses its own connection (on Streamlit Cloud
  normally the transaction pooler, where the advisory locks protect nothing) and may overlap
  Render's `scripts/migrate.py`. If V1 holds a bootstrap lock at that moment, `migrate.py` exits 1
  and the API does not start (R17): safe, but the switch stalls. Rehearsed locally, the new V1
  migrated an unmigrated copy from its first page.

Streamlit Community Cloud has no pause. What each option does, checked on 2026-10-08 by running
V1 headless with the code Streamlit runs today (`main`, `c5ebac8`) and the code the merge gives it:

| Option | What V1 does (both versions) | Production database and bucket | A pause? |
|---|---|---|---|
| Remove `DATABASE_URL` | Falls back to a throwaway SQLite and keeps serving, login form included | Untouched (the SQLite repository never uses Storage) | **No**: anyone can log in and practise; everything is lost |
| **`DATABASE_URL` pointing at a host that cannot exist** | Shows only «Error al conectar con la base de datos» in 0.2 s and stops: no repository, no login, no Storage, no AI | Untouched | **Yes, in practice**, and undone by pasting the original value back |
| Let it sleep, or "Only specific people can view this app" | Any allowed visitor wakes it; it still redeploys on the merge | Reachable | No |
| Delete the app | Gone | Untouched | Yes, but it has to be recreated (needs admin rights on the repository) |

**Temporary disconnection**, before the backup that will be the rollback point. V1 stays like
this through the merge and the verification of § 6: the new code shows the same error.

1. Copy the current value of `DATABASE_URL` from the app's *Settings → Secrets* into the password
   manager (never into the repository or a chat). Leave every other secret as it is.
2. Replace only that value, then save:

   ```toml
   DATABASE_URL = "postgresql://mantenimiento:mantenimiento@mantenimiento.invalid:5432/mantenimiento"
   ```

   `.invalid` is a reserved top-level domain: the name never resolves, so V1 cannot connect
   anywhere.
3. Reboot the app (⋮ → *Reboot app*). A process that is already running keeps its open
   connections to production until it restarts.
4. Open the app's URL. It must show only «Error al conectar con la base de datos: No se pudo
   conectar a PostgreSQL…», with no login form. Take the backup only after this check.

**Reconnecting V1 is a later decision, not a step of the transfer.** Nothing in the switch or in
§ 6 depends on V1. If the owner later decides to bring it back, it is done in one save of the
secrets — the original `DATABASE_URL` plus these two keys **at root level** (root keys become
environment variables; keys under a `[section]` do not) — then a reboot, a login and a check that
V1 shows the same ratings as V2:

```toml
RUN_MIGRATIONS = "0"
ENVIRONMENT = "production"
```

Checked so that decision can be taken (2026-10-08, new V1 code on PostgreSQL copies of the legacy
data):

- **`RUN_MIGRATIONS=0` is respected.** On an unmigrated copy, V1's first page left the schema and
  every table byte-identical. The same run without the variable migrated the copy.
  `tests/integration/test_v1_run_migrations.py` pins this on both engines, against a fresh
  database, through V1's real entry point.
- **V1 works with the new rating state.** On a migrated copy, V1 logged in and showed the
  reconciled baselines: 909.93 shown as 910 and 886.70 as 887.
- **A V1 answer writes only to the new store.** A correct answer, after a valid 5 s, moved only
  the item's (course, topic) row in `student_course_topic_elo`. It moved by +6.69 against the
  "+6.7" V1 announced, and logged one valid attempt. `student_topic_elo`, `users.current_elo` and
  the schema were untouched.
- **V1 and V2 agree.** Both showed the same course ratings afterwards, and the teacher view
  rendered.
- **Rank names differ by design** (spec 001 research R16: V1 keeps its own labels). The same 917
  reads "Punto de Partida" in V1 and "Plata II" in V2.

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

### 4.1 The encrypted backup and how to restore it

The `transfer-ops` workflow (branch `ops/transfer`, never merged) produces one artifact,
`levelup-backup-<stamp>-encrypted`: a `.tar.gz.gpg` encrypted with `BACKUP_PASSPHRASE` (AES-256).
Inside: `full.dump` (when Supabase allows a full dump), `public.dump` (the application's schema),
`procedimientos/` (`objects/`, `manifest.json`, `backup-report.json`), `source-counts.txt` (rows
per table when the dump was taken), `SHA256SUMS` and the rehearsal report. The workflow's second
job already downloads that artifact, checks its SHA-256, decrypts it, verifies every file and
restores `public.dump` into a throwaway database with the same row counts. GitHub keeps the
artifact 7 days: download it and store it with the passphrase kept separately.

Restore (Git Bash on Windows ships `gpg`, `tar` and `sha256sum`; `pg_restore` needs the
PostgreSQL 17 client tools):

```bash
unzip levelup-backup-<stamp>-encrypted.zip
sha256sum levelup-backup-<stamp>.tar.gz.gpg          # equals "artifact sha256" in the run log
gpg --decrypt --output levelup-backup.tar.gz levelup-backup-<stamp>.tar.gz.gpg   # asks the passphrase
mkdir backup && tar -xzf levelup-backup.tar.gz -C backup && (cd backup && sha256sum -c SHA256SUMS)

# Inspect it in a throwaway database (never the production URL):
createdb scratch
pg_restore --no-owner --no-privileges --schema=public -d postgresql://<user>@localhost:5432/scratch backup/public.dump

# Bucket: verify, then upload what is missing (never overwrites, never deletes)
python scripts/restore_storage_bucket.py --backup backup/procedimientos
python scripts/restore_storage_bucket.py --backup backup/procedimientos --apply
```

**Returning production to the exact pre-transfer state** (destructive; the owner only, with the
Render service suspended and V1 disconnected as in § 3.1). Drop the tables the migration added,
then restore the application schema; rehearsed locally, the result is identical to the state
before the migration:

```sql
DROP TABLE IF EXISTS active_exam_sessions, diagnostics, exam_responses, lesson_interactions,
  lesson_progress, pvp_answers, pvp_matches, student_course_topic_elo CASCADE;
```

```bash
pg_restore --clean --if-exists --no-owner --no-privileges --schema=public \
  -d "$MIGRATION_DATABASE_URL" backup/public.dump
```

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

- Roadmap follow-up **F-4** is merged into the branch being switched: `next-question`, `/answer`
  and the diagnostic serve only courses the student is enrolled in (spec 001 FR-037, FR-037a).
  Today any course is served.
- Roadmap follow-up **F-5** is merged into the branch being switched: PvP lets enrolled students
  in. Without it the redesign's PvP refuses every student (`docs/sdd/roadmap.md` § Follow-ups).
- Roadmap follow-up **F-1** is merged into the branch being switched (decided 2026-10-09):
  Semillero students see the six courses of their grade and invitation codes work. Its read-only
  production checks (spec 001 task T084; `docs/sdd/f1-semillero-survey.md` § 3 step 1 and § 4.3
  step 1) are done by the owner first, with the counts recorded:
  - the Semillero students without a grade, listed. They get their grade by the survey's
    procedure, or the owner accepts the ones left; until then they see the notice asking for their
    grade, and their enrolments stay open;
  - the `courses.block` CHECK, read. If it lacks one of `Universidad`, `Colegio`, `Concursos`,
    `Semillero`, the migration stops with an error naming the missing values (FR-028n) and the
    switch waits for a manual repair prepared and reviewed separately, with a backup.

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
