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
| `MIGRATION_DATABASE_URL` | Only for `scripts/migrate.py`: the **session pooler (5432)** — the migration's advisory lock is not reliable on the transaction pooler (6543). Supabase's direct connection also takes the lock, but its host has only IPv6 unless the project buys the IPv4 add-on, and neither Render nor GitHub-hosted runners (the `transfer-ops` jobs) reach IPv6 |
| `DB_POOL_MIN_IDLE` | Optional (default `2`, 1–5): idle PostgreSQL connections the API keeps between requests (spec 002 D2). The pool never opens more than 5 |
| `DB_POOL_PROBE_AFTER_S` | Optional (default `30`): a connection idle longer than this is checked with `SELECT 1` before use |
| `RUN_MIGRATIONS` | `0` on the web process; the schema is applied by the separate migration step |
| `WEB_CONCURRENCY` | `1` (required: PvP lobby and notification rooms live in process memory — AGENTS.md R18) |
| `JWT_SECRET_KEY` | ≥ 32 random characters (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `CORS_ORIGINS` | JSON list with the frontend's exact origin; no `localhost` in production |
| `RATE_LIMIT_STORAGE_URI` | shared Redis/Valkey URI; `memory://` is refused in production |
| `PUBLIC_REGISTRATION_ENABLED` | **`true`** (owner, 2026-10-18): new users keep registering themselves after the merge, as production does today. Unset means closed — then accounts come only from the administrator (spec 004 FR-005). Registration by the admin and public registration behind a paywall are a feature planned after the refactor (`docs/sdd/roadmap.md` § 6) |
| `RATE_LIMIT_LOGIN_ACCOUNT`, `RATE_LIMIT_LOGIN_GLOBAL`, `RATE_LIMIT_REGISTER` | optional; defaults `10/minute` per account, `300/minute` for all logins, `20/minute` per address for public registration (spec 004 E1). `RATE_LIMIT_AUTH` no longer exists |
| `RATE_LIMIT_STORAGE_CONNECT_TIMEOUT`, `RATE_LIMIT_STORAGE_TIMEOUT`, `RATE_LIMIT_STORAGE_PROBE_INTERVAL`, `RATE_LIMIT_FALLBACK_MAX_KEYS` | optional; defaults 0.5 s, 0.5 s, 10 s and 50 000 — the fallback when the limit store fails (§ 3.2, spec 004 E6) |
| `AUTH_COOKIE_SAMESITE` | `none` (default) while the page calls the API from another origin; `lax` after the switch of § 3.3 (spec 004 E5) |
| `SUPABASE_URL`, `SUPABASE_KEY` | Storage for the **private** bucket `procedimientos` (images are served as bytes, never by public URL) |
| `ADMIN_USER`, `ADMIN_PASSWORD` | seed of the administrator account (only created if the password is set) |
| `SYSTEM_AI_API_KEY` | optional; without it AI features degrade gracefully. Optional per-feature keys: `AI_KEY_KATIA`, `AI_KEY_PROCEDURE`, `AI_KEY_TEACHER_ANALYSIS`; the key's prefix picks the provider, and `AI_MODEL_KATIA` / `AI_MODEL_VISION` / `AI_MODEL_ANALYSIS` override the Groq models. `SYSTEM_AI_PROVIDER` and `AI_KEY_STUDENT_ANALYSIS` are no longer read (spec 005 K4): remove them from the host |
| `DATABASE_SSLMODE`, `LOG_LEVEL` | optional |

Both database URLs take the form `postgresql://user:password@host:port/database` and nothing more.
The app splits them with its own pattern instead of handing them to libpq: a `?sslmode=…` (or any
`?query`) part becomes part of the database name, and a percent-encoded password (`%40`) is sent
as written. `pg_dump`, `psql` and the backup workflow read both forms, so a URL can pass the backup
and still stop `migrate.py`. Write the password as is, and prefer one of letters and digits, which
every reader takes the same way; SSL comes from `DATABASE_SSLMODE` (default `require`). The
`transfer-ops` precheck and backup connect with the app's own parser first and stop if it cannot.

Frontend (build time): `VITE_API_URL` = the API's public origin (empty after the switch of § 3.3, with `VITE_WS_URL` = the API's `wss://` origin). **Never** put a secret in a
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

### 3.2 Rate limits: their store and the client's address

The API limits sign-in (`RATE_LIMIT_LOGIN_ACCOUNT`, 10 attempts per account per minute, and
`RATE_LIMIT_LOGIN_GLOBAL`, 300 per minute overall), public registration while it is open
(`RATE_LIMIT_REGISTER`, 20 per address per minute) and the AI routes per account
(`RATE_LIMIT_SOCRATIC`, `RATE_LIMIT_REVIEW`). Its counters live in `RATE_LIMIT_STORAGE_URI`.
Nothing in this section changes a host's settings or the start command; the owner does that.

- **What the store holds**: one counter per key and window, expiring with the window — keyed by
  account for sign-in (an identifier that names no account, only as its SHA-256), by address for
  registration, by account for the AI routes. No password, token, name or answer.
- **Which store**: any Redis-protocol server the API reaches — a Render Key Value instance in the
  API's region (its *internal* URL, `redis://…:6379`) or an external one over TLS (`rediss://…`).
  The URI carries a password: it goes only in Render's environment (`render.yaml` declares it
  `sync: false`), never in the repository or a chat.
- **If the store stops answering** (spec 004 E6, constitution 1.1.0): the call that finds the
  failure waits at most its timeouts (`RATE_LIMIT_STORAGE_CONNECT_TIMEOUT` and
  `RATE_LIMIT_STORAGE_TIMEOUT`, 0.5 s each, no client retries); from then on the API counts every
  limit in its own memory with the same values, and no request calls the store. Render's log shows
  one warning, `Rate-limit store unreachable (…)`. A background probe checks the store at most every
  `RATE_LIMIT_STORAGE_PROBE_INTERVAL` (10 s), started by a limited request or a health check. When
  it answers, what memory counted is added to the store, one warning `Rate-limit store recovered`
  is logged and the store is used again: no key gets a new allowance on return. Limits of the
  fallback:
  - counts kept in the store before the outage cannot be read during it, so for a key counted just
    before, memory starts from zero;
  - a restart during the outage loses the memory counters;
  - memory holds at most `RATE_LIMIT_FALLBACK_MAX_KEYS` (50 000) counters, and serves only while
    one process runs (`WEB_CONCURRENCY=1`). Beyond that the limits cannot be applied: limited
    routes answer 503 and so does `/api/health`.
- **`GET /api/health`** answers 200 with `"limits": "normal"` or `"degraded"` (and `"status"`
  `"ok"` or `"degraded"`), and 503 if the database fails or the limits cannot be applied. Render's
  health check reads only the status code, so a degraded 200 keeps the instance in service and
  alerts nobody: an external monitor that reads the body is the owner's step (spec 004 N8).
- **Which address the limits see.** uvicorn trusts `X-Forwarded-For` only from `127.0.0.1` unless
  `FORWARDED_ALLOW_IPS` says otherwise, and the start command sets neither. Behind Render's proxy
  every request may therefore be counted under the proxy's address. Reproduced locally with
  uvicorn 0.53, together with the opposite case: trusting every proxy counts the left-most
  `X-Forwarded-For` entry, which a client can write if the proxy appends to the header rather than
  replacing it (reported for Render, not verified here). **Do not set `FORWARDED_ALLOW_IPS` to `*`,
  or to any address list Render does not publish**: either lets a client choose the address it is
  counted under. Sign-in does not depend on the address (spec 004 E1): a class behind one school
  address signs in without sharing a limit. Only public registration counts per address, so if it
  is opened (`PUBLIC_REGISTRATION_ENABLED`), its 20 per minute may be shared by everyone.

### 3.3 Session renewal through the frontend's origin (Safari) — prepared, not active

Safari blocks third-party cookies, and today the renewal cookie comes from the API's origin while
the page lives on the frontend's: on Safari the session can end when the 15-minute access token
expires. Spec 004 E5 prepares the fix; it changes nothing until the owner switches it on.

Already in the code, whatever the switch:

- `frontend/vercel.json` forwards `/api/*` from the frontend's origin to the API (unused while
  `VITE_API_URL` points at the API).
- Authentication responses carry `Cache-Control: no-store`; a state-changing authentication request
  with an `Origin` the API does not serve (`CORS_ORIGINS`) is refused; logout deletes the cookie
  with the same attributes it was set with; a browser WebSocket from another origin is refused.

The switch, outside class hours:

1. **Vercel** (frontend): set `VITE_API_URL` to an empty value and `VITE_WS_URL` to
   `wss://levelup-elo.onrender.com` (WebSockets cannot go through the proxy), then redeploy.
   The renewal cookie still works with `SameSite=None` on the same origin, so nothing breaks yet.
   Everyone signs in once more: the old cookie belonged to the API's domain, the new one to the
   frontend's.
2. **Render** (API): set `AUTH_COOKIE_SAMESITE=lax`, then redeploy. From now on the cookie is
   first-party.
3. Check, labelling each result *real device* or *automated*: on Safari for iPhone, iPad and
   desktop, and on Chrome — sign in; wait past 15 minutes (or delete the access token from
   localStorage) and keep working; reload; sign out and confirm a reload asks to sign in; change
   the password in one browser and confirm the other is signed out; open the KatIA chat and
   confirm the answer streams word by word through the proxy (spec 004 N6).
   The automated half already runs on every pull request: CI job "Sesión en Safari (WebKit)"
   (`frontend/playwright.session.config.ts`) covers sign-in, renewal, reload, sign-out and the
   password change in WebKit as Safari desktop, iPhone and iPad. Without an iPhone, a remote
   real-device service (BrowserStack, LambdaTest) counts as *real device*.
   **Owner decision (2026-10-20):** with no Apple device at hand, switch it on with the automated
   check and watch for students on iPhone or iPad who report being signed out; undo below if any
   does (spec 004 `plan-e5.md`).

To undo: `AUTH_COOKIE_SAMESITE=none` on Render first, then `VITE_API_URL` back to the API's origin
on Vercel. The order matters: with `lax` and a cross-origin page, renewal fails everywhere.

Behind the proxy the API sees Vercel's addresses, not the browser's; sign-in limits do not depend on
the address (§ 3.2), only public registration's per-address limit, which then counts Vercel's.

## 4. Backups (before any migration)

1. **Database:** a full logical dump of the final database over the session pooler (5432) — the
   same URL as `MIGRATION_DATABASE_URL`:

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
per table when the dump was taken), `SHA256SUMS`, the rehearsal report and the rehearsal's full
output. The workflow's second job already downloads that artifact, checks its SHA-256, decrypts it,
verifies every file and restores `public.dump` into a throwaway database with the same row counts.
GitHub keeps the artifact 7 days: download it and store it with the passphrase kept separately.

The repository is public, so anyone can read the run logs and download the other artifacts. They
carry check results and counts only. When a step fails, PostgreSQL quotes row data in its errors
(`DETAIL: Key (email)=(…) is duplicated`), so the rehearsal's raw output goes only into the
encrypted backup; read it there. Restrict the `production-ops` environment to the
`ops/transfer-*` branches and require the owner's approval for every run.

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
DROP TABLE IF EXISTS active_exam_sessions, audit_account_events, bank_syncs, diagnostics,
  exam_responses, group_invitations, katia_conversations, katia_messages, lesson_answers,
  lesson_interactions, lesson_outcomes, lesson_progress, procedure_files, procedure_gradings,
  procedure_uploads, pvp_answers, pvp_matches, schema_versions, student_course_topic_elo CASCADE;
```

These are the 19 tables the redesign creates that `main` does not have (compared on 2026-10-19,
schema version 3, plus spec 005 K3's two at version 4). A spec that adds a table adds it here too.

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

Spec 002 D1 adds the tables `schema_versions` and `bank_syncs`. The first start of this code on a
database applies the whole migration once, in one transaction, and records version 1; every later
start with the version current and the item bank unchanged issues no DDL and writes no data. The
start no longer repairs data: if `migrate.py` stops with «Run `python scripts/repairs/….py`»,
run that script without arguments (it only counts), then with `--apply`, and start again — it
changed nothing before stopping. The other two repairs (`deactivate_users_without_password.py`,
`backfill_prob_failure.py`) are the owner's choice; the start does not need them.

The schema version the code expects is `SCHEMA_VERSION` in
`src/infrastructure/persistence/schema_version.py`. Today it is **5**:

| Version | Change |
|---|---|
| 1 | spec 002 D1: `schema_versions`, `bank_syncs`; the migration runs all-or-nothing |
| 2 | spec 002 D3: an index on SQLite only (PostgreSQL unchanged) |
| 3 | spec 003 L4: tables `lesson_answers` (every lesson answer, in order) and `lesson_outcomes` (the post-diagnostic outcome); each row already in `lesson_interactions` is copied once into `lesson_answers` |
| 4 | spec 005 K3: tables `katia_conversations` (one summary per KatIA conversation) and `katia_messages` (its text, only while it is open); `katia_interactions` stays and is no longer written by V2 |
| 5 | spec 006 X2: column `exam_responses.selected_option` (the option chosen for each exam item; NULL on rows stored before it) |

A production database from `main` has no schema version and no lesson tables, so its first
migration goes straight to version 5 and the L4 copy finds nothing to copy. The rehearsal must run
the **same commit that will be switched**: a rehearsal made before a version change does not
cover it, so repeat § 4 and this section whenever `SCHEMA_VERSION` changed since the last one.

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
SELECT MAX(version) FROM schema_versions;                      -- 5: the SCHEMA_VERSION of the commit
SELECT (SELECT COUNT(*) FROM lesson_answers) - (SELECT COUNT(*) FROM lesson_interactions);  -- 0
SELECT COUNT(*) FROM lesson_outcomes;                          -- 0: written only by new answers
SELECT COUNT(*) FROM katia_conversations;                      -- 0: written only by new chats
```

Every reconciled row must have `approximate = true` and a `legacy_source_key`; the second run must
not add rows. Only then run `scripts/migrate.py` against the final database, **before** the new web
process starts (with `RUN_MIGRATIONS=0` on the web process).

**Rollback.** Because the migration only adds, the previous application version still starts on
the migrated schema. But ratings written after the switch live only in `student_course_topic_elo`,
which the previous version does not read, so a rollback hides them. To return to the exact
pre-transfer state, restore the § 4 dump.

Rehearsed from a browser (2026-10-09, locally): a student whose browser runs the redesign's service
worker gets `main`'s app back by the third reload after Vercel's Instant Rollback and Render's
redeploy of `main`, still signed in when `JWT_SECRET_KEY` is unchanged, with no errors.

## 6. Verification in the final environment

**Before the switch** (on the final repository's pull request):

- The § 4 backup and the § 5 rehearsal were run on the commit being switched, or on one with the
  same `SCHEMA_VERSION`. The rehearsal report shows the migration passing twice, and
  `SELECT MAX(version) FROM schema_versions` returns that version on the copy (5 today).

- Roadmap follow-ups **F-4** (PR #9: `next-question`, `/answer` and the diagnostic serve only
  courses the student is enrolled in, spec 001 FR-037, FR-037a) and **F-5** (PR #8: PvP lets
  enrolled students in) are merged into `redesign` (checked 2026-10-19).
- Roadmap follow-up **F-1** is merged into `redesign` (PRs #6, #10; decided 2026-10-09):
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
2. `GET /api/health` → 200 with `"limits": "normal"` (readiness: it queries the database and the
   limit store; 503 if either cannot serve, `"degraded"` if Redis does not answer — § 3.2).
3. `GET /api/meta/ranks` → 200, 16 ranks ascending from "Aspirante" to "Leyenda Suprema", with
   `Cache-Control: public, max-age=3600`.
4. With a test student: stats shows a rating with its rank, or "Diagnóstico pendiente" — never a
   bare 1000; answering a practice question changes the topic rating by the previewed amount;
   reconciled topics show "aproximado"/≈; exam history loads.
5. With a test teacher: the dashboard loads. It lists only active, non-test students, with
   display rating and rank label (spec 006 FR-040), so it is empty while the teacher's groups hold
   only the seeded test students.
6. The SQL checks from § 5 return the same answers as on the rehearsal copy.
7. No answer was saved by the old API after the migration (§ 6.1): the query below returns 0.
8. Once V1 is disconnected (§ 3.1), delete the KatIA messages typed before spec 005 K3 (decision
   N3): `python scripts/repairs/delete_katia_texts.py` counts them, `--apply` deletes them, and a
   second `--apply` reports 0. It prints counts only.

`scripts/verify_deployment.py --api-url <API> --frontend-url <SPA> --report verify-YYYYMMDD.txt`
runs 2–4 and more with the test accounts: health, ranks, CORS, login, a diagnostic, a practice answer
whose rating change equals the preview, the course map, every lesson image served by the frontend,
and a procedure upload. Run it from a checkout of the deployed commit (it reads the lesson content
to list the images).

Teachers review active, non-test students only (spec 006 FR-050). With the default test student,
the procedure must appear in the student's list, stay out of the teacher's queue and be refused
when graded (404). Setting `VERIFY_STUDENT` to a non-test student of the teacher's group checks
instead that the teacher sees it with the same image bytes and that grading it moves that
student's rating; a test account there fails the queue check.

The image check passes even without Storage: when the upload or the download fails, the API serves
the copy kept in the row (R9). The database says which path was used: the verify submission (its id
is in the report) must have `storage_url` set. A NULL `storage_url` means uploads fall back to the
row; check `SUPABASE_URL` and `SUPABASE_KEY` on the API host.

### 6.1 The minutes between the merge and the new API

Merging deploys the frontend (Vercel) at once, while the API changes only when the new Render
instance has run `scripts/migrate.py` and passed its health check; until then Render keeps routing
to the old instance. Rehearsed locally on 2026-10-09 with `main`'s code and the redesign:

- **New frontend, old API.** No JavaScript error. Home, courses, stats, exams and the teacher
  dashboard work; the course page, the map, the lessons and the league get 404 until the new API
  answers.
- **Migration beside the old API.** `migrate.py` does not wait on the old instance (0.5 s on the
  rehearsal copy) and the old API keeps answering without errors.
- **Answers in between.** An answer the old API saves after the migration is logged in `attempts`
  but moves only the legacy table, so the new rating never sees it. The old code leaves
  `attempts.elo_before` NULL, which the new code always sets; the `dbcheck` job counts them:

  ```sql
  SELECT COUNT(*) AS old_api_answers_after_migration, COUNT(DISTINCT user_id) AS students
    FROM attempts
   WHERE elo_before IS NULL
     AND timestamp > (SELECT MIN(reconciled_at) FROM student_course_topic_elo);
  ```

- **A student with the old app open.** Without a service worker (main's build has not registered
  one since 2026-04-25) the next reload loads the new app. With main's service worker it takes up
  to three reloads, and the old app works against the new API in between. Keeping
  `JWT_SECRET_KEY` keeps sessions open; a new key sends everyone to the sign-in page, without
  errors.

So: switch when nobody is practising, start Render's deploy right after merging, and check the
count above afterwards.

## 7. Known operating constraints

- One API process only (`WEB_CONCURRENCY=1`) until matchmaking and notifications are shared —
  AGENTS.md R18.
- Do not raise the PostgreSQL pool above `(1, 5)` on a small plan; always return connections with
  `put_connection`.
- If the host sleeps idle services (free tiers), the first request after a pause takes about a
  minute; warm it with `GET /api/health` before a class. Capacity notes: `docs/arquitectura.md`
  § Capacidad.
