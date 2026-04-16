# LevelUp-ELO

> Plataforma de evaluación y aprendizaje adaptativo basada en el sistema de rating **ELO** — el mismo del ajedrez competitivo — aplicado a la educación matemática.

[![CI](https://github.com/LuisJRubioH/LevelUp-ELO/actions/workflows/ci.yml/badge.svg)](https://github.com/LuisJRubioH/LevelUp-ELO/actions/workflows/ci.yml)
[![Versión](https://img.shields.io/badge/versión-1.0.0--v2--dev-blue)](https://github.com/LuisJRubioH/LevelUp-ELO)
[![Python](https://img.shields.io/badge/python-3.11+-green)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19-61DAFB)](https://react.dev/)
[![Licencia](https://img.shields.io/badge/licencia-MIT-orange)](LICENSE)

**V1 (Streamlit):** [levelup-elo-9yg9ewez4smvlylgwcls2q.streamlit.app](https://levelup-elo-9yg9ewez4smvlylgwcls2q.streamlit.app)
**V2 (React + FastAPI):** [luislevelupelo.vercel.app](https://luislevelupelo.vercel.app)

---

## Tabla de contenidos

- [Qué es](#qué-es)
- [Características principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Motor ELO — Cómo funciona](#motor-elo--cómo-funciona)
- [Banco de preguntas](#banco-de-preguntas)
- [Roles de usuario](#roles-de-usuario)
- [Instalación local](#instalación-local)
- [Despliegue en producción](#despliegue-en-producción)
- [Variables de entorno](#variables-de-entorno)
- [CI/CD](#cicd)
- [Tests](#tests)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Versiones](#versiones)

---

## Qué es

LevelUp-ELO mide el nivel de cada estudiante en tiempo real: cada respuesta actualiza simultáneamente el rating del alumno y el de la pregunta. El sistema siempre sirve el reto correcto — ni tan fácil que aburra, ni tan difícil que frustre — usando la **Zona de Desarrollo Próximo (ZDP)** como criterio de selección.

Incluye tres roles (estudiante, docente, admin), un banco de +1.900 preguntas, revisión de procedimientos manuscritos con IA y KatIA, una tutora socrática con personalidad propia.

---

## Características principales

### Motor ELO adaptativo
- **ELO vectorial por tópico**: cada estudiante mantiene un rating independiente por tema, no uno global. Detecta fortalezas y debilidades con precisión quirúrgica.
- **Factor K dinámico**: el peso de cada respuesta cambia según la experiencia del estudiante (K=40 → 32 → 16/24), acelerando la convergencia.
- **Rating Deviation tipo Glicko**: incertidumbre por tópico (RD inicial=350, mín=30). A mayor RD, mayor variación del rating; decrece con la práctica.
- **Selector ZDP con Fisher Information**: elige la pregunta que maximiza el aprendizaje. P(éxito) objetivo: [0.40, 0.75]. Expansión progresiva si no hay candidatos.

### IA pedagógica
- **KatIA — tutora socrática**: gata cyborg con mensajes predefinidos por contexto (bienvenida, calificación por rango, rachas). GIFs animados durante revisión de procedimientos.
- **Revisión de procedimientos manuscritos**: Groq + Llama 4 Scout analiza imágenes/PDFs paso a paso, genera score 0–100 y ajusta el ELO (`(score − 50) × 0.2`).
- **Chat socrático con streaming**: guía al estudiante mediante preguntas sin revelar la respuesta. Post-generación verifica que no filtre la solución.
- **Multi-proveedor**: Anthropic, Groq, OpenAI, Google Gemini, HuggingFace, LM Studio, Ollama — detección automática por prefijo de API key.

### Plataforma completa
- **Dual DB**: SQLite local y PostgreSQL (Supabase) con API pública idéntica. Selección automática por `DATABASE_URL`.
- **ELO consultable**: tabla `student_topic_elo` con ELO actual por materia + campo `users.current_elo` global. Se actualizan automáticamente al responder y al validar procedimientos.
- **Tres roles**: estudiante, docente, admin con flujos completos.
- **Dashboard docente**: ELO temporal por alumno, radar por tópico, historial KatIA, análisis pedagógico con IA, exportación CSV/XLSX.
- **Supabase Storage**: procedimientos en bucket privado con fallback BYTEA en DB.
- **Seguridad**: Argon2id para contraseñas, migración transparente desde SHA-256 legacy.
- **Ranking de 16 niveles**: Aspirante (0–399) → Leyenda Suprema (2500+).
- **Anti-plagio SHA-256**: detecta procedimientos duplicados del mismo estudiante.

---

## Arquitectura

El proyecto tiene **dos interfaces** que comparten el mismo núcleo de lógica de negocio:

```
src/                              ← Núcleo compartido (V1 y V2)
├── domain/                       # Lógica de negocio pura
│   ├── elo/                      # ELO, VectorRating, Glicko, ZDP
│   ├── selector/                 # AdaptiveItemSelector (Fisher Information)
│   └── katia/                    # Mensajes de KatIA
├── application/services/         # StudentService, TeacherService
└── infrastructure/
    ├── persistence/              # SQLiteRepository + PostgresRepository
    ├── storage/                  # Supabase Storage
    └── external_api/             # AI client multi-proveedor

src/interface/streamlit/          ← Interfaz V1 (Streamlit)
api/                              ← Backend V2 (FastAPI REST + WebSocket)
frontend/                         ← Frontend V2 (React + TypeScript + Vite)
```

### Regla de dependencia

```
domain/ ← application/ ← infrastructure/ ← interface/
```

Nunca al revés. El dominio no importa nada de infraestructura. Los servicios reciben los repositorios por constructor (DI).

### V1 — Streamlit (producción estable)

```
src/interface/streamlit/
├── app.py               # Entrada — 167 líneas
├── state.py             # login(), logout(), session_state helpers
├── assets.py            # CSS, logos, banners
├── timers.py            # Timers JavaScript (setInterval)
└── views/
    ├── auth_view.py     # Login + wizard registro
    ├── student_view.py  # Práctica, stats, procedimientos
    ├── teacher_view.py  # Dashboard, revisión, exportación
    └── admin_view.py    # Usuarios, grupos, reportes
```

### V2 — React + FastAPI (en desarrollo)

```
api/                     # FastAPI — 42+ endpoints REST + WebSocket
├── config.py            # pydantic-settings: JWT, DB, IA keys por función
├── routers/
│   ├── auth.py          # JWT access token + HttpOnly refresh cookie
│   ├── student.py       # Práctica, stats, cursos, procedimientos, analyze IA
│   ├── teacher.py       # Dashboard, grupos, revisión, análisis IA
│   ├── admin.py         # Usuarios, grupos, reportes
│   └── ai.py            # Chat socrático SSE, revisión procedimientos
└── websocket/           # Notificaciones en tiempo real por room

frontend/                # React 19 + TypeScript + Vite
├── src/
│   ├── stores/          # Zustand: auth, practice, settings
│   ├── hooks/           # useTimer, useStudentSession, useNotifications
│   ├── components/      # ELO, KatIA (avatar+chat), Procedure, CourseCard, UI
│   └── pages/           # Student/, Teacher/, Admin/
└── vercel.json          # Deploy Vercel con rewrite SPA
```

---

## Motor ELO — Cómo funciona

### Flujo al responder una pregunta

```
StudentService.process_answer()
  ├→ VectorRating.update()          ← aplica delta ELO al tópico
  ├→ Repository.update_item_rating() ← actualiza dificultad del ítem
  └→ Repository.save_answer_transaction()
       ├→ INSERT attempts            ← persiste metadatos del intento
       ├→ UPSERT student_topic_elo   ← ELO actual por materia
       └→ UPDATE users.current_elo   ← ELO global promedio
```

Todo ocurre en una **transacción atómica** — si falla el update del ítem, el intento tampoco se guarda.

### Fórmula ELO

```
P(éxito) = 1 / (1 + 10^((dificultad_ítem - rating_estudiante) / 400))

delta = K_eff × (resultado - P(éxito))
K_eff = K_base × (RD / RD_base)
```

**Factor K dinámico:**

| Condición | K |
|---|---|
| < 30 intentos (novato) | 40 |
| ELO < 1400 | 32 |
| Estable (error < 15% en últimos 20) | 16 |
| Default | 24 |

### Selector adaptativo

`AdaptiveItemSelector` busca preguntas donde `P(éxito) ∈ [0.40, 0.75]` — el rango ZDP. Si no hay candidatos, expande ±0.05 por paso (hasta 10 pasos). Prioriza preguntas no vistas, luego falladas con ≥3 intentos de cooldown.

---

## Banco de preguntas

+1.900 ítems en `items/bank/` organizados por curso:

| Bloque | Cursos |
|---|---|
| **Universidad** | Álgebra Lineal, Cálculo Diferencial, Integral, Varias Variables, Ecuaciones Diferenciales, Probabilidad |
| **Colegio** | Álgebra Básica, Aritmética Básica, Trigonometría, Geometría |
| **Concursos** | DIAN — Gestor I, SENA — Profesional 10 |
| **Semillero** | Álgebra, Aritmética, Geometría, Lógica, Conteo y Combinatoria, Probabilidad — grados 6°–11° |

### Agregar preguntas al banco

1. Crear o editar `items/bank/<course_id>.json`
2. Agregar `'<course_id>': 'Bloque'` en `_COURSE_BLOCK_MAP` de **ambos** repositorios
3. Correr `python scripts/validate_bank.py`
4. Reiniciar la app — `sync_items_from_bank_folder()` carga automáticamente

### Calibración de dificultad

Fórmula usada para alinear `difficulty` con el ELO medio del grupo (`R_medio`) y la tasa objetivo de éxito `P*`:

```
D*(R_medio, P*) = R_medio + 400 × log10((1 − P*) / P*)
```

Rango válido para bancos semillero: **600–1200**. Redondeo a múltiplos de 50. Ver `.claude/skills/item-calibration/SKILL.md` para el protocolo completo.

---

## Roles de usuario

| Rol | Acceso |
|---|---|
| **Estudiante** | Práctica adaptativa, estadísticas, procedimientos, chat con KatIA, racha por materia, ranking del grupo |
| **Docente** | Dashboard ELO temporal por alumno, radar por tópico, historial KatIA, análisis IA, revisión de procedimientos, exportación CSV/XLSX (filtrada: excluye usuarios con `is_test_user=1`), códigos de invitación inter-nivel |
| **Admin** | Aprobación de docentes, reasignación de estudiantes (auditada), gestión de usuarios, reportes técnicos |

---

## Instalación local

### V1 (Streamlit)

```bash
git clone https://github.com/LuisJRubioH/LevelUp-ELO.git
cd LevelUp-ELO

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

streamlit run src/interface/streamlit/app.py
```

Sin `DATABASE_URL`, usa SQLite local. La base de datos se crea automáticamente con datos demo.

### V2 (React + FastAPI)

```bash
# Terminal 1 — Backend FastAPI
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend React
cd frontend
npm install --legacy-peer-deps
npm run dev
# → http://localhost:5173 (proxy /api → localhost:8000)
```

---

## Despliegue en producción

### V1 — Streamlit Cloud + Supabase

1. Conectar el repositorio en [share.streamlit.io](https://share.streamlit.io)
2. Main file: `src/interface/streamlit/app.py`
3. Configurar secrets (ver Variables de entorno)

### V2 — Vercel + Render

| Servicio | Plataforma | Config |
|---|---|---|
| Frontend | Vercel | `frontend/vercel.json` — framework Vite, rewrites SPA |
| Backend | Render | `Procfile` — `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

Ambos hacen deploy automático en cada push a `main`.

---

## Variables de entorno

### Compartidas (V1 y V2)

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | URL PostgreSQL Supabase (`postgresql://...`) | Sí (producción) |
| `ADMIN_PASSWORD` | Contraseña del usuario admin | Sí |
| `ADMIN_USER` | Nombre del admin (default: `admin`) | No |
| `SUPABASE_URL` | URL del proyecto Supabase | Sí (Storage) |
| `SUPABASE_KEY` | Publishable key de Supabase | Sí (Storage) |

### Solo V2 (backend Render)

| Variable | Descripción | Requerida |
|---|---|---|
| `JWT_SECRET_KEY` | Clave secreta para firmar JWT | Sí |
| `CORS_ORIGINS` | `["https://luislevelupelo.vercel.app"]` | Sí |
| `SYSTEM_AI_API_KEY` | API key de IA del sistema (Groq, Anthropic, OpenAI, etc.) — todos los estudiantes la usan automáticamente | Sí |
| `SYSTEM_AI_PROVIDER` | Proveedor explícito (`groq`, `anthropic`, `openai`, `google`). Auto-detectado si vacío | No |
| `AI_KEY_KATIA` | Key específica para chat socrático KatIA. Si vacía, usa `SYSTEM_AI_API_KEY` | No |
| `AI_KEY_PROCEDURE` | Key específica para revisión de procedimientos. Si vacía, usa `SYSTEM_AI_API_KEY` | No |
| `AI_KEY_STUDENT_ANALYSIS` | Key específica para análisis del estudiante. Si vacía, usa `SYSTEM_AI_API_KEY` | No |
| `AI_KEY_TEACHER_ANALYSIS` | Key específica para análisis docente. Si vacía, usa `SYSTEM_AI_API_KEY` | No |

### Solo V2 (frontend Vercel)

| Variable | Descripción |
|---|---|
| `VITE_API_URL` | URL del backend Render |

> **Nota Supabase**: usar el **connection pooler** (puerto 6543, `aws-...pooler.supabase.com`). El pool interno usa `SimpleConnectionPool(minconn=1, maxconn=5)` — nunca subir `maxconn` más de 5 en el free tier.

---

## CI/CD

GitHub Actions con 7 jobs en cada push a `main`:

| Job | Qué verifica |
|---|---|
| `validate-bank` | `python scripts/validate_bank.py` — estructura e integridad de los 1.900+ ítems |
| `lint` | Black (line-length=100) + Flake8 (E9, F63, F7, F82) |
| `test-unit` | `pytest tests/unit/` — cobertura ≥70% en domain + application |
| `test-integration` | `pytest tests/integration/` — tests SQLite end-to-end |
| `db-sync` | `python scripts/db_sync_check.py` — paridad de API SQLite ↔ PostgreSQL |
| `test-api` | `pytest tests/api/` — tests de integración FastAPI con httpx |
| `build-frontend` | `tsc + vite build` — compilación TypeScript + React |

Pre-commit hooks locales: validate-bank, db-sync-check, Black.

---

## Tests

```bash
# Tests unitarios con cobertura
python -m pytest tests/unit/ -v --cov=src/domain --cov=src/application --cov-fail-under=70

# Tests de integración
python -m pytest tests/integration/ -v

# Tests de integración API
python -m pytest tests/api/ -v

# Validar banco de preguntas
python scripts/validate_bank.py

# Verificar paridad SQLite/PostgreSQL
python scripts/db_sync_check.py
```

---

## Usuarios de prueba

| Usuario | Contraseña | Rol / Nivel |
|---|---|---|
| `admin` | (variable de entorno) | Admin |
| `profesor1` | `demo1234` | Docente (pre-aprobado) |
| `estudiante1` | `demo1234` | Estudiante — Universidad |
| `estudiante2` | `demo1234` | Estudiante — Colegio |
| `estudiante_colegio_1..3` | `test1234` | Estudiante Colegio (protegidos) |
| `estudiante_universidad_1..2` | `test1234` | Estudiante Universidad (protegidos) |
| `estudiante_semillero_1` | `test1234` | Estudiante Semillero grado 9 |
| `estudiante_semillero_2` | `test1234` | Estudiante Semillero grado 11 |

---

## Versiones

### V1.0.0 (producción)
Plataforma Streamlit estable con Clean Architecture, CI/CD completo, 85% cobertura de tests, +1.900 ítems, KatIA tutora socrática, revisión de procedimientos con IA.

### V2.0 (en desarrollo activo)
Reescritura a React 19 + FastAPI. El motor ELO, dominio y banco de preguntas se reutilizan sin cambios. Nueva interfaz moderna, mobile-ready y PWA.

**Estado actual de V2:** Sprints 1–6 completos. Paridad funcional ~98% con V1.
- ✅ Sprint 1: KatIA GIFs, timer de sesión, preview ELO, toasts de racha, fechas en gráficos, perfil en sidebar
- ✅ Sprint 2: Radar chart, heatmap de actividad, ranking del grupo, logros animados, envío de procedimientos
- ✅ Sprint 3: Panel docente completo (gráfico ELO temporal, historial KatIA, análisis IA, filtros cascada)
- ✅ Sprint 4: Admin completions (reportes, auditoría, activación, grupos, códigos invitación)
- ✅ Sprint 5: Mobile, PWA, offline, transiciones Framer Motion, selector de modelo IA
- ✅ Sprint 6: Banners pixel art, centro de feedback, reporte problemas, revisión IA en vivo, API keys por función
- ✅ Post-Sprint 6: KatIA socrático funcional con avatar, procedimiento integrado en práctica, tabla `student_topic_elo`
- ⏳ Sprint 7: Calidad y producción (E2E Playwright, code splitting, error boundaries, skeletons)
- ⏳ Sprint 8: Pulido y accesibilidad (modo examen, a11y, tema claro/oscuro, métricas)

Ver plan detallado en `docs/v2-plan.md`.

---

## Licencia

MIT — ver [LICENSE](LICENSE).
