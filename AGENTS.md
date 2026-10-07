# AGENTS.md — Oulad

Operational rules for AI agents (Claude Code, Codex) and humans working in this repository.

**Read first:** [`.specify/memory/constitution.md`](.specify/memory/constitution.md). It holds the
principles, the non-negotiables, the agent rules and the governance. This file holds the
**how-to**: commands, patterns, file locations. Rationale and history live in
[`docs/arquitectura.md`](docs/arquitectura.md); the behaviour of a specced area lives in its
`specs/NNN-*/spec.md`. Where this file summarises a rule owned elsewhere, the owner wins.

Rule IDs (R1…, V2-R1…, D1…) are stable: code comments cite them. Never renumber; retire a rule
by marking it *Superseded*.

---

## Quickstart

### V2 — FastAPI + React (active)

```bash
# Backend
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# Frontend (pnpm, Node >= 22.13)
cd frontend && pnpm install --frozen-lockfile && pnpm run dev   # → http://localhost:5173
```

### V1 — Streamlit (frozen)

```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```

Run from the **repo root**: `app.py` injects the root into `sys.path` before any `src.*` import.
V1 is frozen — see the constitution § Stack for what that allows.

### Deploy

Push to `main` auto-deploys this repo's **sandbox**: frontend on Vercel, backend on Render
(`oulad-sandbox-api`, `render.yaml`), database on a separate Supabase project. The original
product's production lives in `LuisJRubioH/LevelUp-ELO`. Environment variables and startup order:
[`docs/arquitectura.md` § Despliegue](docs/arquitectura.md).

### Verify before saying "done"

Bash / Git Bash / CI:

```bash
ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q   # always
python scripts/db_sync_check.py          # if a repository changed (mandatory)
python scripts/validate_bank.py          # if items/ changed
cd frontend && pnpm run build            # if frontend/ changed
black --check --line-length=100 src/ tests/ scripts/
flake8 src/ api/ tests/ scripts/ --max-line-length=100 --select=E9,F63,F7,F82
```

Windows PowerShell (the maintainer's local shell):

```powershell
$env:ADMIN_PASSWORD = "testadmin123"; python -m pytest tests/ --ignore=tests/e2e -q
python scripts/db_sync_check.py
python scripts/validate_bank.py
Push-Location frontend; pnpm run build; Pop-Location
```

`$env:` sets the variable for the rest of the session; open a new shell (or
`Remove-Item Env:ADMIN_PASSWORD`) to clear it.

---

## Spec-driven development (Spec Kit)

### Installation in a clean clone

Supported version: **Spec Kit (`specify-cli`) 1.0.13**, recorded in `.specify/init-options.json`.

| Path | Versioned? | Contents |
|---|---|---|
| `.specify/` | yes | scripts (PowerShell), core templates, **project template overrides**, constitution, workflow |
| `.claude/skills/speckit-*` | **no** (`.claude/` is gitignored) | the Claude Code command skills |
| `.agents/` or Codex equivalents | no | only if the Codex integration is installed |

A clean clone has `.specify/` but **not** the commands. To get them:

```bash
uv tool install specify-cli==1.0.13                # PyPI; how the maintainer's copy was installed
specify integration install claude --script ps     # Claude Code: creates .claude/skills/speckit-*
specify integration install codex --script ps --force   # optional, Codex CLI (second integration)
```

Verify:

```bash
specify version                  # → 1.0.13
specify integration status       # → claude installed (and codex, if added)
specify check                    # → required tools found
```

Then in Claude Code the `/speckit-*` commands are available. Command availability per agent:

| Agent | How commands are invoked | Requires |
|---|---|---|
| Claude Code | `/speckit-specify`, `/speckit-clarify`, … (skills) | `specify integration install claude` |
| Codex CLI | the Codex integration's command files | `specify integration install codex` |
| Anything else | not supported here; follow the manual sequence below by reading `.specify/templates/` | — |

**Customized templates are preserved by living in `.specify/templates/overrides/`** — the first
layer of Spec Kit's template resolution, which `specify integration upgrade` and re-init do not
overwrite. Never edit the core files in `.specify/templates/` directly: an upgrade replaces them.
Current overrides:
- `overrides/spec-template.md` — EARS requirements tagged `[AS-IS]` / `[CHANGE]`, mandatory Out
  of Scope and Traceability sections.
- `overrides/tasks-template.md` — tests mandatory; `[AS-IS]` characterization tests pass on
  unchanged code, `[CHANGE]` tests fail first; traceability closing phase.

Check which file a template resolves to (PowerShell):
`. .\.specify\scripts\powershell\common.ps1; Resolve-Template -TemplateName tasks-template -RepoRoot (Get-Location).Path`

### Required sequence (manual — not enforced by tooling)

The bundled workflow `.specify/workflows/speckit/workflow.yml` runs only
specify → gate → plan → gate → tasks → implement. **It does not enforce this project's full
process.** Until that is automated, follow this sequence by hand, one commit per approved step:

| # | Step | Command | Gate before moving on |
|---|---|---|---|
| 0 | Survey (read-only) | — | `docs/sdd/<area>-survey.md` read by the owner |
| 1 | Specify | `/speckit-specify` | owner approves spec.md |
| 2 | Clarify | `/speckit-clarify` | every `[NEEDS CLARIFICATION]` resolved or deferred by the owner |
| 3 | Checklist | `/speckit-checklist` | all requirement-quality items pass |
| 4 | Plan | `/speckit-plan` | Constitution Check passes; owner approves |
| 5 | Tasks | `/speckit-tasks` | every Traceability row has a test task; on spec 001, the first-run review below |
| 6 | Analyze | `/speckit-analyze` | no CRITICAL findings |
| — | **Docs PR** | — | spec + plan + tasks, no code; owner merges |
| 7 | Implement | `/speckit-implement` | Phase 2 pins green on unchanged code before any refactor |
| 8 | Converge | `/speckit-converge` | no new gaps (loop 7 ↔ 8 until empty) |
| — | **Code PR** | — | no `PENDING` traceability rows; verification green; owner merges |

**First-run review of `/speckit-tasks` (required checkpoint before committing spec 001's
tasks.md).** The upstream skill still says tests are optional unless requested; the overrides make
them requested, but generation compliance is unverified until this review passes. Check, and fix
tasks.md by hand where it fails:

1. Every FR and every acceptance scenario in spec.md maps to a concrete test task (reused or new)
   that names its IDs — a matching label is not enough.
2. Every `[AS-IS]` requirement the refactor touches has a characterization task in the blocking
   phase, required to pass against the unchanged code.
3. Every `[CHANGE]` requirement has a test task required to fail before its implementation task.
4. Task dependencies enforce that order: pins before any refactor; each `[CHANGE]` test before
   its implementation task.
5. Each kind is required only where the spec has requirements of that tag — no empty phases.

If the review finds systematic failures, record them in the PR and fix the override before the
next spec; do not patch the upstream skill.

Branch, commit and PR rules: constitution § AI Agent Behaviour, rule 7. Adoption plan and
calendar: [`docs/sdd/roadmap.md`](docs/sdd/roadmap.md).

---

## Operational rules

### R1 — Dual DB: both repositories or neither
Any change to `sqlite_repository.py` is mirrored in `postgres_repository.py` and vice versa, with
an identical public API. Checklist:
- Touched one repository? → edit the other too.
- Added a table or column? → idempotent additive migration in both (R8).
- Changed `_COURSE_BLOCK_MAP`? → change it in both.
- Run `python scripts/db_sync_check.py`. It compares text, signatures and DDL only; behavioural
  equivalence is proven by tests parametrised over both engines.

### R2 — Layers
```
src/domain/          no I/O, no third-party libraries, no upper layers
src/application/     imports domain/; NEVER infrastructure/
src/infrastructure/  implements interfaces from domain/application
src/interface/, api/ composition: the only places that wire infrastructure into services
```
New business logic → `domain/`. Use cases → `application/services/`. No SQL in `domain/`, no
rating arithmetic in `infrastructure/`. Enforced by `tests/unit/test_architecture_layers.py`.
Composition points: `api/routers/student.py::_make_service` and `src/interface/streamlit/app.py`.

### R3 — PostgreSQL: `row["column"]`, never `row[0]`
`RealDictCursor`. Dates come back as `datetime` — format with `str(row["created_at"])[:10]`.

### R4 — Connection pool: never `conn.close()`
Always `self.put_connection(conn)`. Closing destroys the pooled connection and exhausts the pool.
`ThreadedConnectionPool(1, 5)`; do not raise `maxconn` on the Supabase free tier.

### R5 — LaTeX in JSON: double the backslashes
`\\frac`, `\\sin`, `\\alpha`. An unescaped `\f` is a form feed and breaks parsing.
`correct_option` must equal one of the strings in `options` exactly.

### R6 — `is_test_user`: never remove
Students with `is_test_user=1` are protected.

### R7 — API keys: never in the database
V2: `SYSTEM_AI_API_KEY` (and per-function keys, below) in backend env vars only. A user's own key
lives in Zustand/localStorage. Never in logs. V1: only in `st.session_state`.

### R8 — Migrations: additive and idempotent
New columns, tables, indexes only — never `DROP`, never a type change.
- PostgreSQL: `ALTER TABLE … ADD COLUMN IF NOT EXISTS`.
- SQLite: `self._add_column_if_not_exists(cursor, table, column, definition)` (checks
  `PRAGMA table_info` first; SQLite has no `IF NOT EXISTS` for columns).

### R9 — Supabase Storage: relative paths, never URLs
`upload_file()` returns only the relative path (`38/alb31/hash.jpg`). Bucket `procedimientos` is
PRIVATE. To display: `get_file()` → bytes. If upload fails, fall back to `image_data` (BYTEA);
never leave both NULL.

### R10 — V1 `st.markdown` HTML: no deep indentation
Streamlit ≥ 1.55 treats 4+ leading spaces as a code block. Build HTML by concatenation with the
opening tag at column 0; never an indented `f"""` block.

### R11 — V1 Streamlit Cloud: `use_container_width=True`
`st.image`, `st.button`, `st.plotly_chart`, `st.dataframe` do not accept `width="stretch"` there.

### R12 — One repository instance per process
V1 creates it once in `app.py` (`_REPO_SINGLETON` + `threading.Lock`); V2 through the dependency
in `api/dependencies.py`. Every instance opens its own pool and exhausts the Supabase free tier.

### R13 — The CognitiveAnalyzer no longer exists
`StudentService` has no `cognitive_analyzer` and no `enable_cognitive_modifier`. Any reference
you find is residue: delete it (V1 once failed to start because `app.py` still passed the kwarg).
`impact_modifier` is always `1.0`; it is a dead parameter scheduled for removal in spec 001.

### R14 — Backfill imports are local to the function
```python
def _backfill_prob_failure(self):
    from src.domain.elo.model import expected_score  # here, not at module level
```

### R15 — `student_topic_elo` is the only rating state
`users.current_elo` is its derived average; `attempts` is a log. Writers, each applying its
effect exactly once:

| Path | Method | Effect |
|---|---|---|
| Diagnostic | `set_topic_elo_baseline` → `_set_topic_elo` | sets the value |
| Answer with `elo_valid=1` | `save_answer_transaction` → `_set_topic_elo` | sets the value |
| Teacher-validated procedure | `validate_procedure_submission` → `_bump_topic_elo` | adds `elo_delta`, sets `elo_applied=1` |
| Finished PvP match | `finish_pvp_match` → `_bump_topic_elo` | adds the delta (R19) |

Never rebuild a rating from `attempts` on read; `get_latest_elo_by_topic` is a single-table
`SELECT`. Regression: `tests/integration/test_elo_single_source.py`. Known issue: the writers do
not yet agree on the rating key (constitution Known Deviation D-1, fixed by spec 001).

### R16 — Answering: read, compute and write in one transaction
`save_answer_transaction(user_id, item_id, topic, compute, …)` locks (PostgreSQL `FOR UPDATE` on
`users` then `items`, always that order; SQLite `BEGIN IMMEDIATE`), reads, calls `compute(state)`
— the domain arithmetic supplied by `StudentService` — and persists. `compute` does no I/O.

### R17 — No migrations or blocking I/O inside the HTTP process
- Deploy: schema bootstrap runs in `scripts/migrate.py` against `MIGRATION_DATABASE_URL` (direct
  connection, port 5432); the web process runs with `RUN_MIGRATIONS=0`. Local dev and tests keep
  the in-process bootstrap (default `RUN_MIGRATIONS=1`).
- WebSockets: repositories are synchronous. From `async def`, call them through
  `await asyncio.to_thread(...)`, and **never** while holding the PvP lobby `_lock`. From a `def`
  endpoint, notify with `notify_sync`, which uses the loop bound at startup.

### R18 — The backend is a single process, and checked
PvP `_lobby` / `_matches` (`api/websocket/pvp.py`) and notification `_rooms` live in process
memory. `settings.validate_runtime()` refuses to start in production with `WEB_CONCURRENCY > 1`;
`render.yaml` sets `"1"`. Scaling needs shared matchmaking, pub/sub event fan-out and
cross-process wake-up — all three before raising the number. Details:
[`docs/arquitectura.md` § Límites conocidos](docs/arquitectura.md).

### R19 — A PvP result moves `student_topic_elo`, not `users.current_elo`
`finish_pvp_match` applies the delta with `_bump_topic_elo` on the match's `course_id`. The close
is idempotent through `AND status='active'`. Orphaned matches are closed as `abandoned` (no rating
change) by `expire_stale_pvp_matches()`.

---

## V2 rules

- **V2-R1** — Changes in `src/`, `items/`, `scripts/` affect V1 and V2. V2-only changes go in
  `api/` or `frontend/`. V1 is frozen (constitution § Stack).
- **V2-R2** — Dual DB still applies: `db_sync_check.py` before every commit that touches a
  repository.
- **V2-R3** — *Superseded* by constitution Principle II and Known Deviation D-2: the frontend
  preview must use the backend's K. Until spec 001 lands, `estimateEloDelta()` in `Practice.tsx`
  still uses its own K (32/24); do not copy that pattern.
- **V2-R7** — pnpm (version in `packageManager`), Node ≥ 22.13 (CI: Node 24).
  `pnpm install --frozen-lockfile`; never generate an npm lockfile. Overrides go in
  `frontend/pnpm-workspace.yaml`.
- **V2-R8** — `sessionStartTime` lives in `authStore`, persists in localStorage, resets on logout.
- **V2-R9** — The correct answer never reaches the frontend: no `correct_option` in any `/answer`
  or `/exam/submit` response. On answer, colour only the chosen option.
- **V2-R10** — Any direct `fetch()` outside `api/client.ts` prefixes
  `import.meta.env.VITE_API_URL ?? ""`. Vercel serves the SPA with no reverse proxy to Render
  (`SocraticChat.tsx` is the reference).

### Learning-path rules (owned by spec 003 once it exists)

- **V2-R11 — 11-block node architecture.** A rebuilt node declares
  `content["kind"] == "eleven_block_node"` and is rendered by the **generic**
  `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx`, which knows no `node_id`.
  **Migrating a node = writing a module in `src/domain/learning/nodes/` and listing it in
  `nodes/__init__.py::NODE_MODULES`.** No change to the renderer, `Lesson.tsx`,
  `api/routers/student.py` or the tests. One window, five colour zones: `explorar` (header +
  ladder + mini-diagnostic + KatIA + genuine attempt) · `construir` (discovery + definition + two
  worked examples) · `trampa` (reserved colour, three steps with submission) · `tu turno`
  (bridge + method comparison + practice) · `cerrar` (closing ladder + abstraction + Pólya +
  post-diagnostic). Node-specific keys in `content`: `kicker`, `scene {image, step, aria}` (omit
  when the node is not a ladder rung, e.g. B09), `finish_label`,
  `post_diagnostic.outcome_gain/_flat`. Invariants: **exactly one** focal `self_explanation` per
  node; the last `worked_examples` card is the trap (`trap: True` + `confidence_prompt` +
  `correct_version` + `explain_prompt`); every practice item has hints `n1/n2/n3`; only practice
  and closure block `node_completed` (diagnostic, bridge and post-diagnostic use
  `required=False`); the mini-diagnostic **does not grade** (it acknowledges with
  «Anotado. Seguimos.») because it is the baseline for the post-diagnostic. Reference node:
  `nodes/b06_racionales.py`. `Implementacion/FORMATO_nodo_conjuntos_numericos.md` describes the
  OLD format and no longer applies to B04–B09.
- **V2-R12 — Pre-algebra N2, the city of operations (E01–E06).** Six buildings, one per node, and
  every example comes from that building's trade: E01 **El Granero Público** · E02 **La Casa de
  Cuentas** (a wall where zero is an engraved line) · E03 **El Taller de Mosaicos** · E04 **El
  Comedor Comunal** · E05 **El Invernadero** · E06 **La Cantera**. Names live in
  `_N2_BUILDINGS[*]["building"]`/`["trade"]` (hub) and in each node's `CONTENT["building"]`; a test
  requires them to match. All six use V2-R11. Invariants: (a) **KatIA is a GREEK cat** and the
  scene is the building's INTERIOR, never a market stall; (b) every `closure` ladder carries
  **all 6 sets** ℕ ℤ ℚ 𝕀 ℝ ℂ, and `closed` accepts `yes`/`no`/**`partial`** (amber `~`) when
  closure fails only in one concrete case; (c) **𝕀 is not closed under + − × ÷** (√2·√2=2,
  √2÷√2=1) but **is closed under roots of positive radicands**, so the 𝕀 row in E06 is
  `partial`; (d) **one distinct focal misconception per building** (`sumar_siempre_agranda`,
  `resta_es_conmutativa`, `multiplicar_siempre_agranda`, `dividir_siempre_achica`,
  `potencia_es_multiplicar_por_el_exponente`, `raiz_de_suma_es_suma_de_raices`); (e) no concrete
  case repeats across opening, examples and practice; (f) practice answers are finite and
  typeable (regex `-?\d{1,6}(,\d{1,4})?`, es-CO decimal comma `2{,}5`). Reference node: E05.
  Image prompts: `Implementacion/image-prompts/02-prealg-n2-ciudad.md` — the current art in
  `generated/n2-mercado/` still shows market stalls and must be regenerated.
- **V2-R13 — Pre-algebra N3, the factory of properties (M01–M05).** Each property lives in a named
  **station** (`_N3_MACHINES[*]["station"]` ↔ `CONTENT["station"]`, tested) with its own
  material: M01 **La Prensa de Intercambio**, bronze plates
  (`todas_las_operaciones_son_conmutativas`) · M02 **El Horno de Fundición**, ingots
  (`parentesis_son_decorativos`) · M03 **La Cinta Repartidora**, gears
  (`distribuye_sobre_el_producto`) · M04 **El Calibre Cero**, rods and gauges
  (`neutro_es_el_mismo_para_toda_operacion`) · M05 **La Prensa de Contrapesos**, beam balance
  (`inverso_es_solo_cambiar_el_signo`). All five use V2-R11. Mixed ladder: by **operation** for
  M01–M04 (the six of N2, `partial` when the identity holds on one side only) and by **set** for
  M05. The inverses ladder carries **all 6 sets**: ℕ✗ → ℤ partial (opposite appears, motivates
  B05) → ℚ✓ (reciprocal appears, motivates B06) → **𝕀 partial** → ℝ✓ → ℂ✓. 𝕀 **is included**:
  every irrational has an opposite and a reciprocal, **and they are irrational** — the reciprocal
  of √2 is `\dfrac{1}{\sqrt{2}}=\dfrac{\sqrt{2}}{2}`, i.e. rationalising (explicit hook to the
  future topic). Honest nuance in the 𝕀 row: the inverse exists but the identity 1 ∉ 𝕀, so the
  full home of inverses is ℝ. Content in `_N3_MACHINE_CONTENT`, rendered in
  `LevelThreeLesson.tsx`.
- **V2-R14 — Pre-algebra N4, the Port of the Polis (C01–C06).** Hub `C00` + six named
  destinations, **strictly sequential** unlock after N3. Each node's `CONTENT["destination"]`
  must match `_N4_CARDS[*]["destination"]` (tested): C01 **Corinto**
  (`invierte_la_direccion_de_la_divisibilidad`) · C02 **Rodas** (`los_multiplos_se_acaban`) ·
  C03 **Delos** (`uno_es_primo`) · C04 **Mileto** (`deja_factores_compuestos`) · C05 **Atenas**
  (`mcd_es_el_mayor_de_los_numeros`) · C06 **Esparta** (`mcm_es_el_producto_de_los_numeros`).
  All six use V2-R11 (`src/domain/learning/nodes/cNN_*.py`). Invariants: (a) **varied context
  bank** — no concrete object appears more than twice in the level; (b) `valid_options`,
  `expected`, `trap_options` of `multi_select` are **lists**, never Python `set()` (they are
  serialised to JSON — tested); (c) **no set ladder**: each `closure` uses its own axis
  (divisibility criteria, does the list end?, exactly two divisors?, is it finished?, is the GCD
  one of the two?, is the LCM the product?); (d) **mixed practice is mandatory**: each node mixes
  `numeric` + `single_select` + `multi_select` (tested). The engine receives a `multi_select` as
  a comma-separated string (`"a,b"`). Reference node: C06.
- **V2-R15 — Algebra N1, El Papiro de las Cuatro Casas (hub + 16 rooms).** First Algebra module.
  New setting — pre-algebra happens in Greece, algebra in **Kemet (Ancient Egypt)** — but a
  **technical** continuation: same course `algebra_basica`, same 11-block renderer, same
  interaction log. Position in the path comes from `unlock_after` (the hub chains after
  `PREALG-N4-C06-MCM`), not from the ID prefix. **One landing hub + 4 houses × 4 rooms = 17
  nodes.** Hub `ALG-A00-PAPIRO-CUATRO-CASAS` uses `kind: level_hub_cards`, rendered by
  `LevelFourLesson` (parametrised by `content.image` / `cards_hint` / `card_closed_hint`); its 4
  cards point to each house's first room. Each room declares `CONTENT["house"]` (the ROOM name,
  unique among the 16 — tested) and `CONTENT["guide"]` (same per house).
  - **La Casa de la Vida · Meritka** — L01 la sala de los cálamos (`variable_como_etiqueta`) ·
    L02 el estante sellado (`toda_letra_es_variable`) · L03 la mesa de dictado
    (`traduce_en_el_orden_de_las_palabras`) · L04 la cámara del recuento
    (`yuxtapone_en_vez_de_multiplicar`).
  - **La obra de la pirámide · Bakenra** — O01 la rampa (`combina_no_semejantes`) · O02 el patio
    de aparejos (`el_menos_solo_afecta_al_primero`) · O03 el taller de cinceles
    (`multiplica_los_exponentes_al_multiplicar`) · O04 la caseta del capataz
    (`cancelar_completo_da_cero`).
  - **Los campos tras la crecida · Tabiry** — F01 la parcela partida (`cancelacion_en_suma`) ·
    F02 el canal madre (`suma_numeradores_y_denominadores`) · F03 la era de trilla
    (`busca_comun_denominador_para_multiplicar`) · F04 el silo de simiente
    (`invierte_la_primera_fraccion`). **No polynomial factoring**: monomial or numeric
    denominators only.
  - **El taller del canon · Iuty** — R01 la cuadrícula del canon (`escalado_aditivo`) · R02 el
    tinte de lino (`invierte_la_razon_en_la_regla_de_tres`) · R03 el pan de oro
    (`descuento_y_recargo_se_cancelan`) · R04 la sala de las lámparas
    (`toda_relacion_es_directa`).

  Invariants: (a) **no vocabulary crossing**, not even within a house — each room has its own
  lane (cálamo · estante/vara · mesa de dictado · cámara del recuento; rampa/trineo · polea/vale ·
  cincel/sillar · cántaro/aguador; parcela/lindero · canal/caudal · era/parva · silo/simiente;
  cuadrícula/boceto · tina/brazada · pan de oro/lámina · lámpara/aceite); (b) `method_comparison`
  is **mandatory** in every 11-block node (tested), so a node whose sheet says
  `dos_metodos: no` compares two ways of **checking**; (c) `closure` **does not copy the set
  ladder**: each room has its own axis, with `partial` for the honest intermediate case — where
  the nuance that keeps the node from being a memorised rule goes (the parameter in L02, right by
  accident in L03, the surviving coefficient in O04, the zero check in R02, side-vs-area in R04);
  (d) the **16 focal misconceptions are distinct** from each other and from pre-algebra's 27
  (tested over all `NODE_MODULES`); (e) **historical facts are setting only**: no claim of an
  exact Per-Ankh function or a specific Egyptian canon ratio. Guide: `docs/ruta-de-aprendizaje.md`.
  Reference node: O04.
- **V2-R16 — Algebra N2, La sala de los troqueles (Baghdad).** KatIA leaves Kemet for the **House
  of Wisdom (Baghdad, 9th c.)**, per `Implementacion/MAPA_NODOS_ALGEBRA8.md`. Same course `algebra_basica`, same
  renderer; chained after `ALG-N1-R04-VARIACION`. Wiring: module in `nodes/pNN_*.py`, list it in
  `NODE_MODULES`, add the row to `_ALG_N2_SEQUENCE` and `_MAP_PRESENTATION`. **Nothing else** —
  `Lesson.tsx` no longer whitelists node IDs (the backend 404s), and the map test derives its list
  from `ALG_N1_NODE_IDS + ALG_N2_NODE_IDS`.
  - **Shared hub `ALG-S00-CASA-DE-LA-SABIDURIA`** (`nodes/s00_hub_bagdad.py`,
    `kind: level_hub_cards`): ALG-N2 and ALG-N3 share one antechamber — the workshop stamps, the
    warehouse opens what was stamped — with **two** cards, one per wing, each with its guide
    (Rayhana / Salim). Hubs are dispatched by `node_type == "level_hub_cards"`, not by node ID,
    so a new hub needs no frontend change. Port-specific strings in `LevelFourLesson` are
    parametrised (`card_cta`, `finish_label`, `gating_label`, `cards_aria`) with the port text
    as fallback.
  - The map's original sub-space «patio de los mosaicos» **collides with E03** and was replaced by
    **la sala de los troqueles** (a notable product is a die: stamp the pattern instead of
    multiplying term by term). `test_no_two_nodes_share_a_room_name` forbids shared room names
    across all `NODE_MODULES`.
  - Four rooms, guide **Rayhana**, own vocabulary lane and focal misconception each:
    **P01 la matriz cuadrada** (`binomio_cuadrado_falta_2ab`; matriz, lámina de cobre, orla,
    esquina) · **P02 el cuño de la cenefa** (`conjugado_da_suma_de_cuadrados`; cuño, greca,
    franja, espejo) · **P03 el molde de tres capas** (`binomio_cubo_falta_terminos`; molde, capa,
    vaciado, arcilla) · **P04 la bandeja de parejas** (`termino_comun_falta_suma`; bandeja,
    casilla, pareja, ficha).
  - **P04 closes the level by collecting it**: its `closure` shows P01 and P02 as special cases —
    equal non-common terms give the binomial square (`partial`), opposite ones cancel and give
    the difference of squares (`partial`). One die with different settings, not four dies.
  - **One `closure` axis per room**: P01 «can the exponent be distributed?» (yes over product and
    quotient, no over sum; `partial` for the zero addend — right *by accident* — and for the root
    of a product, which needs non-negative radicands) · P02 «does the middle term cancel?»
    (`partial` for reversed conjugates) · P03 «how many layers does the mould leave?» (n + 1 terms;
    `partial` for `(ab)³`) · P04 «what drives the middle term?».
  - Practice comes from the textbook (Hipertexto U4 p74/p75); item→node map in
    `Implementacion/MAPA_ITEMS_A_NODOS_N6_N10.md` (772 items over 13 nodes).
- **V2-R17 — Algebra N3, El almacén de la caravana (Baghdad).** Factoring, the way back from the
  dies. Guide **Salim**. Chained after `ALG-N2-P04-TERMINO-COMUN`. Five rooms, each with its lane
  and focal misconception: **G01 el pesaje de entrada** (`factor_comun_incompleto`; fardo, saco,
  báscula, tara) · **G02 el cotejo de huellas** (`suma_de_cuadrados_es_factorizable`; huella,
  calco, catálogo) · **G03 la mesa de despiece** (`pares_sin_verificar`; despiece, listón, encaje,
  muesca) · **G04 la bodega de los toneles** (`suma_de_cubos_es_cubo_de_binomio`; tonel, duela,
  aro, arqueo) · **G05 la sala de expedición** (`se_queda_en_el_primer_caso`; guía de carga,
  precinto, remesa, ruta).
  - **G05 fills a measured gap**: among the **4,656 statements** in `items/source/` there are
    **ZERO method-choice items and ZERO check-without-computing items** — structurally, because
    the textbook index already tells the student which method applies. Its practice is entirely
    of the missing types, based on the 46 items of `u5_factorizacion_completa_p127`.
  - **The level's thread is "correct ≠ finished"**: G01 installs it (multiplying back does NOT
    detect an incomplete common factor; look inside), G02 re-engages it (`x⁴−16` opens and one
    piece opens again), G05 closes it over the whole chain.
  - **Deliberate contrast G02 ↔ G04**: a sum of SQUARES does not factor, a sum of CUBES does.
    G04's axis: «with two terms, the exponent decides».
  - `closure` axes, one per room: «is anything common left inside?» · «is the print in the
    catalogue?» · «does it meet BOTH conditions?» · «sum or difference of cubes?» · «where do you
    start?».
- **V2-R18 — Misconception tags say WHERE, not only WHAT.** A generic tag emitted by many nodes
  routes review to "the first node that can emit it", which is right by accident. Format:
  **`<symptom>_<operation>`** (e.g. `sobregeneraliza_la_correccion`, once emitted by 16 nodes, is
  now `sobregeneraliza_producto_de_monomios`, `sobregeneraliza_mcm`,
  `sobregeneraliza_regla_de_tres`…).
  - **Content error** → the node that teaches the concept is its review screen; many nodes may
    emit it (`magnitud_sin_signo` lives in B05 and fires in three more).
  - **Process habit** (`habito_*`: not checking, not deciding, not simplifying) → has no owner and
    must not have one.
  - `test_a_content_error_seen_in_many_nodes_has_a_node_that_teaches_it` fails if a new content
    tag is emitted by 3+ nodes with no node declaring it focal. Nine inherited pre-algebra tags are
    listed as known debt and must not grow.
  - `test_every_focal_misconception_is_distinct` only catches LITERAL collisions; two nodes
    teaching the same error under different tags must be caught in review.

---

## Architecture map

Four layers in `src/` (R2). Rationale: [`docs/arquitectura.md`](docs/arquitectura.md).

**`domain/`**
- `elo/model.py` — `expected_score`, `procedure_elo_delta`, dataclasses. (`calculate_dynamic_k`
  and `update_elo` are unused — scheduled for removal in spec 001.)
- `elo/uncertainty.py` — `RatingModel`: `ΔR = 32 × (RD/350) × (result − P)`; RD starts at 350,
  ×0.95 per answer, floor 30.
- `elo/vector_elo.py` — `VectorRating` (rating + RD per key), `aggregate_global_elo`.
- `selector/item_selector.py` — `AdaptiveItemSelector`: pre-filter `D ∈ [R−250, R+250]`, target
  `P ∈ [0.40, 0.75]` widened ±0.05 per step (max 10), random pick among candidates within 95 % of
  the best `P(1−P)`.
- `learning/` — nodes, map, lessons (V2-R11 … V2-R18).
- `katia/katia_messages.py` — predefined KatIA messages by score band and streak.

**`application/services/`** — `student_service.py` (`process_answer`, `get_next_question`,
badges), `teacher_service.py`. Interfaces: `application/interfaces/repositories.py`, checked
both ways by `tests/unit/application/test_repository_contracts.py`.

**`infrastructure/`** — `persistence/sqlite_repository.py`, `persistence/postgres_repository.py`
(`RealDictCursor`, `ThreadedConnectionPool(1–5)`), `storage/supabase_storage.py`,
`external_api/ai_client.py`, `external_api/math_procedure_review.py`,
`security/hashing_service.py`, `ml/calibration.py` (isotonic calibrator, display only).

**`api/`** — `main.py`, `config.py` (settings + `validate_runtime()`), `dependencies.py`,
`routers/{student,teacher,ai,auth,…}.py`, `websocket/{pvp,notifications}.py`.

**`frontend/src/`** — `api/client.ts` (HTTP client), `stores/` (Zustand), `pages/Student/`,
`pages/Teacher/`, `components/KatIA/SocraticChat.tsx`, `i18n/` (es is the source of truth, en
satisfies `DeepString<typeof es>`).

---

## Database

`DATABASE_URL` set → PostgreSQL (Supabase); absent → SQLite (`data/elo_database.db`).

Bootstrap: `init_db()` → `_migrate_db()` → `_seed_admin()` → `_seed_demo_data()` →
`_backfill_prob_failure()` → `sync_items_from_bank_folder()` → `_seed_test_students()`.

PostgreSQL: `pg_try_advisory_lock` (non-blocking), IDs 12345–12349, always released in `finally`.
Never `pg_advisory_lock` or `pg_advisory_xact_lock` — `statement_timeout=60s` cancels them.

| Table | Key fields |
|---|---|
| `users` | `role`, `approved`, `active`, `group_id`, `education_level`, `grade`, `is_test_user`, `rating_deviation`, `current_elo` (derived), `email` (partial UNIQUE, NULL ok) |
| `student_topic_elo` | PK `(user_id, topic)`, `current_elo`, `rd`, `updated_at` — the rating (R15) |
| `groups` | unique `(teacher_id, name_normalized)`, `invite_code` |
| `items` | `difficulty`, `rating_deviation`, `image_url`, `tags` (JSON array) |
| `attempts` | `elo_before`, `elo_after`, `elo_valid`, `prob_failure`, `expected_score`, `time_taken`, `request_id` |
| `procedure_submissions` | `storage_url` (relative), `image_data` (BYTEA fallback), `ai_proposed_score` (never moves rating), `teacher_score`, `elo_delta`, `elo_applied`, `file_hash` |
| `pvp_matches` | `status` (active/finished/abandoned), `course_id`, deltas |
| `katia_interactions`, `problem_reports`, `audit_group_changes`, `diagnostics`, `exam_sessions` | see repositories |

---

## Item bank

Items live in `items/bank/*.json` and `items/bank/semillero/*.json`; `course_id` = file name
without extension. Required fields: `id` (globally unique) · `content` (LaTeX in `$…$`, R5) ·
`difficulty` (int, 600–1800) · `topic` · `options` (list) · `correct_option`.

New course: create `items/bank/my_course.json` → add `'my_course': '<Block>'` to
`_COURSE_BLOCK_MAP` in **both** repositories → `python scripts/validate_bank.py` → restart.
Blocks: `Universidad` · `Colegio` · `Concursos` · `Semillero`.

Manual calibration: `D*(R, P*) = R + 400 × log10((1 − P*) / P*)` (olympiad P*=0.25 → R+191;
P*=0.10 → R+382). Items at 0 % success with ≥ 10 attempts: recalibrate or retire.

---

## AI integration

Provider detected by key prefix: `sk-ant-` Anthropic · `gsk_` Groq · `AIzaSy` Gemini · `hf_`
HuggingFace · `sk-proj-`/`sk-` OpenAI · no prefix → local (Ollama / LM Studio). Every AI feature
degrades gracefully without a provider.

| Env var | Use | Fallback |
|---|---|---|
| `SYSTEM_AI_API_KEY` | all AI | — |
| `AI_KEY_KATIA` | Socratic chat | `SYSTEM_AI_API_KEY` |
| `AI_KEY_PROCEDURE` | procedure review | `SYSTEM_AI_API_KEY` |
| `AI_KEY_STUDENT_ANALYSIS` | student analysis | `SYSTEM_AI_API_KEY` |
| `AI_KEY_TEACHER_ANALYSIS` | teacher analysis | `SYSTEM_AI_API_KEY` |

Per request: user key > function key > general key, via `settings.get_ai_key("procedure", user_key)`.

- **Socratic chat** (`api/routers/ai.py`, SSE): `SOCRATIC_MAX_TOKENS=120`; post-validation rejects
  replies that reveal the answer or exceed 3 sentences.
- **Procedure review**: Groq + `meta-llama/llama-4-scout-17b-16e-instruct` (rigorous), other
  vision providers (generic). Score 0–100 is advisory; only `teacher_score` moves the rating
  (`(score − 50) × 0.2`).
- **KatIA assets** (`KatIA/`): always the compressed GIFs (`correcto_compressed.gif`,
  `errores_compressed.gif`); the originals are 69 MB. Predefined messages:
  `get_procedure_comment(score)` ALTA ≥ 91 / MEDIA 60–90 / TUTORIA < 60;
  `get_streak_message(streak)` at 5/10/20.

---

## Security (how-to; principles in constitution VI)

- JWT: access token in Zustand/localStorage (15 min) + refresh token in HttpOnly cookie (7 days).
  `credentials: "include"` on every fetch. Never log tokens.
- Uploads: `apiClient.postForm()`; never set `Content-Type` manually on multipart.
- Admin only through `ADMIN_USER` / `ADMIN_PASSWORD` env vars.
- Anti-plagiarism: SHA-256 of the file before accepting a procedure.
- WebSockets: `authenticate_access_token` is shared with REST; rooms are authorised against the
  user; PvP requires the student role and enrolment in the course.

## Roles

- **student** — group required · adaptive practice · stats · procedures · KatIA · per-course streak
  · problem reports.
- **teacher** — approval required · ELO dashboard · procedure review · AI analysis · CSV/XLSX export
  · cross-level invite codes.
- **admin** — approves teachers · reassigns students (audited) · activates/deactivates users ·
  problem-report notifications.

## Test users (local seed data)

| User | Password | Role / level |
|---|---|---|
| `profesor1` | `demo1234` | teacher (pre-approved) |
| `estudiante1` | `demo1234` | Universidad |
| `estudiante2` | `demo1234` | Colegio |
| `concursante1` | `demo1234` | Concursos — DIAN (thematic blocks) |
| `estudiante_colegio_1..3` | `test1234` | Colegio (`is_test_user=1`) |
| `estudiante_universidad_1..2` | `test1234` | Universidad (`is_test_user=1`) |
| `estudiante_semillero_1` | `test1234` | Semillero grade 9 (`is_test_user=1`) |
| `estudiante_semillero_2` | `test1234` | Semillero grade 11 (`is_test_user=1`) |

---

## Frontend design rules

- **D1** — Every new component has at least one non-generic design decision (type, spacing,
  accent or entrance motion).
- **D2** — Motion carries meaning: achievements `scale` + `opacity`; ELO delta as an animated
  number; low timer pulses (< 30 % left). Use Framer Motion, not raw CSS `transition`.
- **D3** — Teacher dashboard: data first. ELO and radar charts before actions; no big decorative
  icon cards.
- **D4** — Student views mobile-first (375 px); teacher views desktop-first (1280 px).
- **D5** — LaTeX always through `react-katex`, never plain text.

Forbidden: purple gradients · nested cards · Inter without hierarchy · low contrast on dark
backgrounds. Colours are CSS tokens in `frontend/src/index.css`; never hard-code them.

```
Background #0A0A0F   Surface #12121A   Accent  #6C63FF
Success    #22C55E   Error   #EF4444   Warning #F59E0B
Text       #F1F5F9   Text2   #94A3B8
```

Optional local UI skills (not in the repo; never base a mandatory rule on them):
`pnpm dlx skills add pbakaus/impeccable`, `Leonxlnx/taste-skill`, `emilkowalski/skill`
(`npx` is not on PATH on the maintainer's machine).
