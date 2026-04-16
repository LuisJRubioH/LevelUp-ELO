# CLAUDE.md — LevelUp-ELO

Instrucciones para Claude Code al trabajar en este repositorio.

---

## Inicio rápido

### V1 — Streamlit (producción)
```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```
Ejecutar siempre desde la **raíz del repo** — `app.py` inyecta el root en `sys.path` ANTES de cualquier import de `src.*`.

Tests y linting:
```bash
pytest tests/unit/
black --check --line-length=100 src/ tests/ scripts/
flake8 src/ tests/ scripts/ --select=E9,F63,F7,F82
```

### V2 — React + FastAPI (en desarrollo)
```bash
# Terminal 1 — Backend
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm install --legacy-peer-deps && npm run dev
# → http://localhost:5173
```

Deploys automáticos en push a `main`: Frontend → Vercel (`luislevelupelo.vercel.app`) · Backend → Render (`levelup-elo.onrender.com`)

Documentación V2: `docs/v2-tecnico.md` (gitignoreado) · Plan de sprints: `docs/v2-plan.md`

---

## Reglas de comportamiento — leer antes de cualquier tarea

### R1 — Dual DB: siempre los dos o ninguno
Cualquier cambio en `sqlite_repository.py` **debe replicarse** en `postgres_repository.py` y viceversa. API pública idéntica. Checklist obligatorio:
- ¿Toqué un repositorio? → editar el otro también
- ¿Agregué tabla/columna? → `ALTER TABLE ADD COLUMN IF NOT EXISTS` en ambos
- ¿Modifiqué `_COURSE_BLOCK_MAP`? → sincronizar en ambos

### R2 — Clean Architecture: no cruzar capas
```
domain/         → sin imports externos ni de capas superiores
application/    → importa domain/, NO infrastructure/ directamente
infrastructure/ → implementa interfaces de domain/application/
interface/      → puede importar todo, preferir application/services/
```
Lógica de negocio nueva → `domain/`. Casos de uso → `application/services/`. Nunca SQL en `domain/` ni lógica ELO en `infrastructure/`.

### R3 — PostgreSQL: `row['column']` nunca `row[0]`
Usa `RealDictCursor`. Las fechas son objetos `datetime` — siempre `str(row['created_at'])[:10]`.

### R4 — Connection pool: nunca `conn.close()`
Siempre `self.put_connection(conn)`. `conn.close()` destruye la conexión y agota el pool.

### R5 — LaTeX en JSON: backslashes doblados
`\\frac`, `\\sin`, `\\alpha`. Un `\f` sin escapar causa `JSONDecodeError`. `correct_option` debe coincidir exactamente con uno de los strings en `options`.

### R6 — is_test_user: nunca eliminar
Estudiantes con `is_test_user=1` están protegidos. Nunca remover este flag.

### R7 — API keys: nunca persistir en DB
V1: solo en `st.session_state`. V2: `SYSTEM_AI_API_KEY` en env var del backend (nunca en frontend ni en DB). Keys de usuario en Zustand/localStorage (nunca en logs).

### R8 — Migraciones: solo aditivas
Solo `ALTER TABLE ADD COLUMN IF NOT EXISTS`. Nunca `DROP COLUMN`, `DROP TABLE` ni cambios de tipo.

### R9 — Supabase Storage: paths relativos, nunca URLs
`upload_file()` retorna SOLO el path relativo (`38/alb31/hash.jpg`). El bucket `procedimientos` es PRIVADO. Para mostrar imágenes: `get_file()` → bytes → `st.image()`. Si upload falla: fallback a `image_data` (BYTEA). Nunca dejar ambos en NULL.

### R10 — st.markdown HTML: sin indentación profunda
Streamlit 1.55+ interpreta 4+ espacios como bloque de código. Construir el HTML como string concatenado con el tag de apertura en posición 0. Nunca `f"""` con el tag indentado.

### R11 — Streamlit Cloud: `use_container_width=True`
`st.image()`, `st.button()`, `st.plotly_chart()`, `st.dataframe()` NO aceptan `width="stretch"`. Usar siempre `use_container_width=True`.

### R12 — PostgresRepository: singleton por proceso
Se crea UNA SOLA VEZ en `app.py` (`_REPO_SINGLETON` con `threading.Lock`). Nunca instanciar por sesión — cada instancia abre su propio pool y agota Supabase free tier.

### R13 — CognitiveAnalyzer puede ser None
`enable_cognitive_modifier=False` en producción. Verificar antes de acceder:
```python
if st.session_state.student_service.cognitive_analyzer is not None:
    ...
```

### R14 — Imports en backfill: locales dentro de la función
```python
def _backfill_prob_failure(self):
    from src.domain.elo.model import expected_score  # aquí, no a nivel de módulo
```

---

## Skills disponibles

Leer el skill correspondiente **antes de empezar**:

| Tarea | Skill |
|---|---|
| Repositorios, tablas, migraciones, queries | `.claude/skills/db-dual-backend.md` |
| Domain/application/infrastructure, módulos nuevos | `.claude/skills/clean-architecture.md` |
| Ítems, cursos, banco de preguntas, calibración | `.claude/skills/items-bank.md` · `.claude/skills/item-calibration/SKILL.md` |
| Tras modificar cualquier repositorio | `.claude/skills/db-sync-checker.md` + `python scripts/db_sync_check.py` |

---

## Arquitectura

Clean Architecture — 4 capas en `src/`:

**`domain/`** — lógica pura sin dependencias externas:
- `elo/model.py` — ELO clásico, Factor K dinámico, dataclasses `Item`/`StudentELO`
- `elo/vector_elo.py` — `VectorRating`: ELO + RD por tópico. `impact_modifier=1.0` fijo en producción (el CognitiveAnalyzer existe pero no escala el delta ELO — causaba discrepancias con el preview)
- `elo/uncertainty.py` — RD inicial=350, mín=30, decay=RD×0.95
- `elo/zdp.py` — intervalo ZDP
- `selector/item_selector.py` — `AdaptiveItemSelector`: Fisher Information, ZDP [0.4, 0.75], expansión ±0.05 hasta 10 pasos
- `katia/katia_messages.py` — mensajes predefinidos de KatIA por rango de score y racha

**`application/services/`** — casos de uso:
- `student_service.py` — `process_answer()`, `get_next_question()`, `get_socratic_help()`
- `teacher_service.py` — dashboard y análisis pedagógico

**`infrastructure/`** — implementaciones concretas:
- `persistence/sqlite_repository.py` — SQLite local (~1200 líneas)
- `persistence/postgres_repository.py` — PostgreSQL/Supabase, `RealDictCursor`, `SimpleConnectionPool(1–5)`
- `storage/supabase_storage.py` — bucket `procedimientos` (PRIVADO)
- `external_api/ai_client.py` — multi-proveedor IA (detección por prefijo de key)
- `external_api/math_procedure_review.py` — Groq + Llama 4 Scout, score 0–100, ajuste ELO: `(score−50)×0.2`
- `security/hashing_service.py` — Argon2id + migración transparente desde SHA-256

**`interface/streamlit/`** — `app.py` (167 líneas) + `views/` + `state.py` + `assets.py` + `timers.py`

### Flujo al responder una pregunta
```
StudentService.process_answer()
  ├→ VectorRating.update()          ← delta ELO al tópico (impact_modifier=1.0 siempre)
  ├→ Repository.update_item_rating() ← actualiza dificultad del ítem
  └→ Repository.save_attempt()       ← persiste intento (transacción atómica)
```

---

## Conceptos clave del dominio

- **VectorRating**: ELO + RD por tópico. `aggregate_global_elo()` promedia para mostrar.
- **Factor K dinámico**: K=40 (<30 intentos) → K=32 (ELO<1400) → K=16 (estable, error<15% últimos 20) → K=24 (default). K efectivo = `K_base × (RD / 350)`.
- **AdaptiveItemSelector**: P(éxito) ∈ [0.4, 0.75]. Maximiza `P×(1−P)`. Expande ±0.05/paso (max 10). Prioriza no vistas, luego falladas con cooldown ≥3.
- **ELO del ítem**: se actualiza simétricamente con cada respuesta — auto-calibración automática.
- **Calibración manual directa**: `D*(R, P*) = R + 400×log10((1−P*)/P*)`. Para olimpiadas: P*=0.25 → D = R+191; P*=0.10 → D = R+382.
- **Ranking**: 16 niveles, Aspirante (0–399) → Leyenda Suprema (2500+).

---

## Base de datos

Selección automática: `DATABASE_URL` → PostgreSQL (Supabase) · ausente → SQLite (`data/elo_database.db`).

Inicialización: `init_db()` → `_migrate_db()` → `_seed_admin()` → `_seed_demo_data()` → `_backfill_prob_failure()` → `sync_items_from_bank_folder()` → `_seed_test_students()`

PostgreSQL: `pg_try_advisory_lock` (no-bloqueante) con IDs 12345–12349. Nunca `pg_advisory_lock` (bloqueante) ni `pg_advisory_xact_lock` — `statement_timeout=60s` los cancela. Lock siempre liberado en `finally`.

### Tablas principales

| Tabla | Campos clave |
|---|---|
| `users` | `role`, `approved`, `active`, `group_id`, `education_level`, `grade`, `is_test_user`, `rating_deviation` |
| `groups` | índice único `(teacher_id, name_normalized)`, `invite_code` (inter-nivel) |
| `items` | `difficulty`, `rating_deviation`, `image_url`, `tags` (JSON array taxonomía) |
| `attempts` | `elo_after`, `prob_failure`, `expected_score`, `time_taken`, `confidence_score`, `error_type` |
| `procedure_submissions` | `storage_url` (path relativo), `image_data` (BYTEA fallback), `ai_proposed_score` (nunca afecta ELO), `teacher_score` (oficial), `elo_delta`, `file_hash` |
| `katia_interactions` | `user_id`, `course_id`, `item_id`, `student_message`, `katia_response` |
| `problem_reports` | `user_id`, `description`, `status` (pending/resolved) |
| `audit_group_changes` | log de reasignaciones de grupo |

---

## Banco de preguntas

Viven en `items/bank/*.json` y `items/bank/semillero/*.json`. `course_id` = nombre del archivo sin extensión.

### Campos requeridos por ítem
`id` (único global) · `content` (LaTeX con `$...$`) · `difficulty` (int, 600–1800) · `topic` · `options` (list) · `correct_option` (coincide exactamente con uno de `options`)

### Agregar un curso nuevo
1. Crear `items/bank/mi_curso.json`
2. Agregar `'mi_curso': 'Bloque'` en `_COURSE_BLOCK_MAP` en **ambos** repositorios
3. `python scripts/validate_bank.py`
4. Reiniciar la app

Bloques válidos: `Universidad` · `Colegio` · `Concursos` · `Semillero`

### Calibración de dificultad
Ver `.claude/skills/item-calibration/SKILL.md`. Fórmula central:
```
D*(R, P*) = R + 400 × log10((1−P*) / P*)
```
Ítems con 0% de éxito y ≥10 intentos → recalibrar o retirar antes de la próxima sesión.

---

## Integración de IA

Proveedor detectado por prefijo de API key: `sk-ant-` (Anthropic) · `gsk_` (Groq) · `AIzaSy` (Gemini) · `hf_` (HuggingFace) · `sk-proj-`/`sk-` (OpenAI) · sin prefijo (Ollama/LM Studio local).

Todas las funciones de IA degradan con gracia si no hay proveedor disponible.

- **Chat socrático**: `SOCRATIC_MAX_TOKENS=120`. Post-validación verifica que no revele la respuesta y tenga ≤3 oraciones.
- **Revisión de procedimientos**: Groq + `meta-llama/llama-4-scout-17b-16e-instruct` (revisión rigurosa), otros proveedores con visión (revisión genérica). `ai_proposed_score` **nunca** afecta ELO directamente — solo `teacher_score` vía `final_score`.

### API keys del sistema (V2)

`api/config.py` lee variables de entorno con fallback encadenado:

| Variable | Función | Fallback |
|---|---|---|
| `SYSTEM_AI_API_KEY` | Key general para toda la IA | — (requerida) |
| `AI_KEY_KATIA` | Chat socrático KatIA | `SYSTEM_AI_API_KEY` |
| `AI_KEY_PROCEDURE` | Revisión de procedimientos | `SYSTEM_AI_API_KEY` |
| `AI_KEY_STUDENT_ANALYSIS` | Análisis del estudiante | `SYSTEM_AI_API_KEY` |
| `AI_KEY_TEACHER_ANALYSIS` | Análisis docente | `SYSTEM_AI_API_KEY` |

Prioridad por request: key del usuario (sidebar) > key de función > key general. Método: `settings.get_ai_key("procedure", user_key)`.

---

## KatIA — Tutora Socrática

Gata cyborg con mensajes predefinidos (no generados por IA) y GIFs animados.

Assets en `KatIA/`: `katIA.png` · `correcto_compressed.gif` (698KB) · `errores_compressed.gif` (1.8MB). Usar **siempre los comprimidos** — los originales son 69MB.

Mensajes: `get_procedure_comment(score)` → ALTA (≥91) / MEDIA (60–90) / TUTORIA (<60). `get_streak_message(streak)` → rachas 5/10/20.

---

## Seguridad

- Contraseñas: **Argon2id** con migración transparente desde SHA-256 legacy.
- API keys: solo en `st.session_state`, nunca en DB ni logs.
- Admin: solo vía env vars `ADMIN_PASSWORD` / `ADMIN_USER`.
- Storage: bucket `procedimientos` PRIVADO, imágenes siempre por bytes nunca URL pública.
- Anti-plagio: SHA-256 del archivo antes de aceptar procedimiento.

**SEC — FastAPI (V2):**
- JWT: access token en Zustand/localStorage (15 min) + refresh token HttpOnly cookie (7 días). Nunca loggear tokens. `credentials: "include"` en todos los fetch.
- Uploads: `apiClient.postForm()`, no establecer `Content-Type` manualmente en multipart.
- `AnswerResponse` y `/exam/submit` NO incluyen `correct_option`. Al responder, solo colorear la opción elegida — nunca revelar la correcta.

---

## Roles de usuario

- **student**: grupo obligatorio · práctica adaptativa · estadísticas · procedimientos · KatIA · racha por materia · reportes de problemas (sidebar)
- **teacher**: aprobación requerida · dashboard ELO temporal · revisión procedimientos · análisis IA · exportación CSV/XLSX · códigos de invitación inter-nivel
- **admin**: aprueba docentes · reasigna estudiantes (auditado) · activa/desactiva usuarios · notificaciones de problemas técnicos

---

## Usuarios de prueba

| Usuario | Contraseña | Rol / Nivel |
|---|---|---|
| `profesor1` | `demo1234` | Docente (pre-aprobado) |
| `estudiante1` | `demo1234` | Universidad |
| `estudiante2` | `demo1234` | Colegio |
| `estudiante_colegio_1..3` | `test1234` | Colegio (`is_test_user=1`) |
| `estudiante_universidad_1..2` | `test1234` | Universidad (`is_test_user=1`) |
| `estudiante_semillero_1` | `test1234` | Semillero grado 9 (`is_test_user=1`) |
| `estudiante_semillero_2` | `test1234` | Semillero grado 11 (`is_test_user=1`) |

---

## V2 — React + FastAPI

### Reglas V2

- **V2-R1**: cambios en `src/`, `items/`, `scripts/` afectan V1 y V2. Modificar V1 solo si es bug real; cambios solo-V2 van en `api/` o `frontend/`.
- **V2-R2**: Dual DB sigue obligatorio. `python scripts/db_sync_check.py` antes de cada commit que toque repos.
- **V2-R3**: `estimateEloDelta()` en `Practice.tsx` usa K=24 fijo — la discrepancia con el K real es aceptable para un preview.
- **V2-R7**: siempre `npm install --legacy-peer-deps` (vite-plugin-pwa@1.2.0 vs vite@8).
- **V2-R8**: `sessionStartTime` en `authStore`, persiste en localStorage, se resetea en logout.
- **V2-R9**: respuesta correcta **nunca** viaja al frontend. Sin `correct_option` en ningún response de `/answer` ni `/exam/submit`.

### Archivos clave V2

```
api/main.py                              # FastAPI, CORS, routers, WebSocket
api/dependencies.py                      # CurrentUser, RepoDep, require_role
api/config.py                            # pydantic-settings: JWT, DB, IA keys por función
api/routers/student.py                   # 19 endpoints estudiante (incl. procedure/analyze, ai-status)
api/routers/teacher.py                   # 13 endpoints docente
api/routers/ai.py                        # Chat socrático SSE + revisión procedimientos
api/routers/auth.py                      # 4 endpoints auth
frontend/src/stores/authStore.ts         # Zustand: token + user + sessionStartTime
frontend/src/stores/practiceStore.ts     # Zustand: ítem actual, historial sesión
frontend/src/api/client.ts               # HTTP client (get/post/patch/delete/postForm)
frontend/src/pages/Student/Practice.tsx  # Sala de práctica
frontend/src/pages/Student/Stats.tsx     # Estadísticas: radar + heatmap + ranking
frontend/src/pages/Student/ProcedureUpload.tsx # Subida + revisión IA en vivo
frontend/src/pages/Student/Feedback.tsx  # Historial de procedimientos + KatIA
frontend/src/pages/Teacher/Dashboard.tsx # Panel docente (4 tabs)
docs/v2-plan.md                          # Checklist de sprints
```

### Comandos V2

```bash
cd frontend && npm run build                              # build TypeScript
python scripts/db_sync_check.py                          # paridad DB (obligatorio)
flake8 src/ api/ --max-line-length=100 --select=E9,F63,F7,F82
ADMIN_PASSWORD=testadmin123 python -m pytest tests/api/ -v
```

### Estado V2 — abril 2026

Sprints 1–6 completos. Paridad funcional ~95% con V1. Deploy en Vercel + Render, CI con 7 jobs verdes.

Sprint 6 completado:
- 6.1: Banners pixel art en tarjetas de curso (`CourseBanner.tsx`, grid responsive, deburr para acentos)
- 6.2: Centro de feedback bidireccional (`Feedback.tsx`, GIFs KatIA por score, badge de procedimientos)
- 6.3: Reporte de problemas técnicos (`ReportProblemButton.tsx`, modal + `POST /student/problems`)
- 6.4: Revisión IA en vivo (`POST /student/procedure/analyze`, KatIA revisando → resultado, multi-proveedor)
- IA del sistema: `SYSTEM_AI_API_KEY` + keys opcionales por función con fallback encadenado

Fixes post-Sprint 6:
- KatIA chat disponible antes Y después de responder (no solo en feedback)
- "Explorar" → practicar cursos matriculados / matricularse en nuevos; "Mis matrículas" → gestión
- Procedimiento auto-vinculado a la pregunta actual del practiceStore
- KatIA socrático funciona sin API key del usuario (fallback a `SYSTEM_AI_API_KEY`)

Pendiente:
- **Sprint 7**: E2E Playwright, code splitting, error boundaries, skeletons
- **Sprint 8**: modo examen, accesibilidad, tema claro/oscuro, métricas docentes

---

## Skills externas instaladas

Instalar con `npx skills add <repo>` → quedan en `.claude/skills/`. Solo invocar en tareas de UI/frontend, no en backend/Python/DB.

| Skill | Cuándo usarla |
|---|---|
| **impeccable** (pbakaus) — `/audit`, `/polish`, `/typeset` | Revisión y pulido de dashboards React |
| **taste-skill** (Leonxlnx) — automática | Generar componentes nuevos con diseño no genérico |
| **emil-kowalski** — automática en animaciones | Animaciones de logros, KatIA, transiciones |

Instalación:
```bash
npx skills add pbakaus/impeccable
npx skills add Leonxlnx/taste-skill
npx skills add emilkowalski/skill
```
Después de instalar impeccable, ejecutar una vez: `/impeccable teach`

**Anti-patrones prohibidos en el frontend React:** gradientes morados · tarjetas anidadas (Cardocalypse) · Inter sin jerarquía · bajo contraste sobre fondos oscuros.

**Paleta V2:**
```
Fondo:      #0A0A0F   Superficie: #12121A   Acento:   #6C63FF
Éxito:      #22C55E   Error:      #EF4444   Warning:  #F59E0B
Texto:      #F1F5F9   Texto2:     #94A3B8
```
Tokens como variables CSS en `frontend/src/index.css`. No hardcodear colores en componentes.

---

## claude-mem — Memoria persistente

Plugin instalado. Captura contexto automáticamente desde cada sesión.

Consultas útiles en sesiones futuras:
```
"¿Qué cambios hicimos al repositorio SQLite la última sesión?"
"¿Cómo implementamos el modo examen?"
"¿Qué archivos tocamos en el Sprint 5?"
```

Configuración recomendada (`~/.claude-mem/settings.json`):
```json
{
  "CLAUDE_MEM_MODEL": "claude-haiku-4-5",
  "CLAUDE_MEM_CONTEXT_OBSERVATIONS": "50",
  "CLAUDE_MEM_WORKER_PORT": "37777"
}
```

---

## Sistema de diseño V2 — Reglas para Claude Code

- **D1**: cada componente nuevo debe tener al menos una decisión de diseño no genérica (tipografía, espaciado, acento o animación de entrada).
- **D2**: animaciones con función pedagógica. Logros: `scale`+`opacity`. ELO delta: número animado visible. Timer bajo: pulso visual (<30% del tiempo). Usar Framer Motion (ya instalado), no `transition` CSS directa.
- **D3**: dashboard docente — datos primero. Gráficos ELO y radar van antes que acciones. No cards grandes con iconos decorativos.
- **D4**: vistas de estudiante → mobile-first (375px). Vistas de docente → desktop-first (1280px).
- **D5**: LaTeX siempre en `react-katex`. Nunca texto plano con expresiones matemáticas.

---

## Contexto del proyecto

```
PROYECTO:    LevelUp-ELO
VERSIÓN:     V2.0.0-dev (Sprints 1-6 completos)
STACK:       Python 3.11 · FastAPI · React 19 · TypeScript · Vite · Supabase · Render · Vercel
DOMINIO:     Plataforma educativa adaptativa con motor ELO vectorial por tópico
AUDIENCIA:   Semillero matemático + estudiantes de colegio y universidad (Colombia)
DEPLOY:      V1 en Streamlit Cloud · V2 en Vercel + Render
PRÓXIMO:     Sprint 7 — calidad y producción
REPO:        https://github.com/LuisJRubioH/LevelUp-ELO
```
