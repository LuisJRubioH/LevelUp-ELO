# Changelog — LevelUp-ELO

Todos los cambios notables del proyecto se documentan en este archivo.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).
Versioning basado en [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.0.0] — 2026-04-13

### Segunda versión — React + FastAPI

#### Nuevas features

**Fase 1 — API FastAPI (39 endpoints REST+WS)**
- JWT con python-jose: access token (15 min) + refresh token (7 días) en HttpOnly cookie
- Routers: `/auth`, `/student`, `/teacher`, `/admin`, `/ai`, `/ws`
- WebSocket: sala de notificaciones por usuario (`teacher_{id}`, `student_{id}`)
- Rate limiting listo para integrar (slowapi)
- OpenAPI docs en `/docs`

**Fase 2–3 — Frontend React + TypeScript**
- SPA con Vite + Tailwind CSS + React Router + Zustand + React Query
- Páginas: Login/Register (wizard), Practice, Stats, Courses, Exam
- Paneles docente: Dashboard (filtros cascada), Grupos, Procedimientos, Exportación
- Panel admin: Usuarios, Grupos, Reportes
- Chat socrático con SSE streaming
- LaTeX en tiempo real con react-katex
- Timer nativo de React (useInterval) — sin JS externo
- Upload de procedimientos con react-dropzone

**Fase 4 — Nuevas features V2.0**
- F1: Notificaciones WebSocket en tiempo real (badge en sidebar al calificar procedimiento)
- F3: Modo examen cronometrado — N preguntas con timer regresivo, mapa visual de preguntas, resultados por ítem
- F5: Sistema de logros/badges (8 badges: first_correct, ELO thresholds, rachas, intentos) — tabla `achievements` en ambos repos
- F8: Progressive Web App — manifest.json, Service Worker con Workbox, cache de preguntas

**Fase 5 — QA y tests**
- 64 tests de integración API (54 originales + 10 nuevos para exam y achievements)
- 176 tests totales (112 unitarios + 64 API)
- CI actualizado: Job 6 (test-api) + Job 7 (build-frontend)
- Todos los tests pasan (64 API, 112 unit = 176 total)

#### Fixes incluidos en V2
- `correct_option` se obtiene siempre desde DB al responder (seguridad)
- `create_group` retorna 3-tupla `(ok, msg, group_id)` — antes 2-tupla
- `difficulty` en schemas: float en lugar de int
- Placeholder SQL compatible SQLite (`?`) y PostgreSQL (`%s`)
- `get_item_by_id()` en ambos repositorios
- Login: token se guarda antes de llamar `/me`

#### Arquitectura
- Backend FastAPI envuelve el dominio V1 sin modificarlo
- Frontend React desacopla UI de lógica de negocio
- Migración gradual: Streamlit V1 sigue funcionando en paralelo

---

## [1.0.0] — 2026-04-12

### Primera versión estable

#### Añadido
- Sistema ELO vectorial por tópico (VectorRating + RD por tópico)
- Selector adaptativo (AdaptiveItemSelector) con Fisher Information y ZDP
- Banco de preguntas con cobertura Universidad, Colegio, Concursos y Semillero (6°–11°)
- KatIA — tutora socrática gata cyborg con mensajes predefinidos y GIFs animados
- Revisión de procedimientos manuscritos (Groq + Llama 4 Scout, score 0–100)
- Sistema multi-proveedor de IA (Anthropic, Groq, OpenAI, Gemini, HuggingFace, LM Studio)
- Panel docente: dashboard ELO, revisión de procedimientos, análisis pedagógico con IA
- Exportación CSV/XLSX de datos completos de estudiantes (intentos, matrículas, procedimientos, interacciones KatIA)
- Sistema de grupos con códigos de invitación (acceso inter-nivel)
- Temporizadores en tiempo real (JavaScript, sin reruns de Streamlit)
- Argon2id para contraseñas con migración transparente desde SHA-256 legacy
- Supabase Storage para procedimientos (bucket privado, fallback BYTEA)
- Panel admin: aprobación docentes, reasignación de estudiantes, reportes técnicos
- Racha de estudio independiente por materia
- Tags de taxonomía cognitiva en ítems
- Logging centralizado (`src/infrastructure/logging_config.py`)
- Transacciones atómicas (`save_answer_transaction`)
- Validador de banco de preguntas (`scripts/validate_bank.py`)
- Checker de paridad SQLite/PostgreSQL (`scripts/db_sync_check.py`)
- Pre-commit hooks: validate-bank, db-sync-check, black, pytest-unit
- CI/CD con GitHub Actions: 5 jobs (validate-bank, lint, test-unit, test-integration, db-sync)
- Suite de tests: 112 pruebas unitarias e integración, cobertura 85%

#### Arquitectura
- Clean Architecture: domain → application → infrastructure → interface
- Modularización de app.py (3701 → 158 líneas) en vistas, state.py, assets.py, timers.py
- Dual DB: SQLiteRepository (local) + PostgresRepository (Supabase)
- Protocol interfaces (ISP): IStudentRepository, ITeacherRepository, IAdminRepository
- Feature flag explícito para CognitiveAnalyzer (`enable_cognitive_modifier=False`)
- `zdp_interval` en dominio puro; `zdp_interval` importado en `item_selector.py`

#### Calidad
- Sin `importlib.reload` ni `except` silenciosos
- Logging observable en carga de banco y errores de infraestructura
- Feedback diferenciado por tipo de error (usuario vs técnico)

---

## [0.9.0-beta] — 2026-01-15

### Versión beta funcional

#### Añadido
- Banco semillero completo (6°–11°) con 500+ preguntas de olimpiadas UdeA
- GIFs animados de KatIA en revisión de procedimientos (correcto/errores)
- Pool de conexiones PostgreSQL con `pg_try_advisory_lock` (no bloqueante)
- Exportación CSV/XLSX básica para docentes
- Figuras geométricas UdeA 2012–2020 (86 PNGs)

---

## [0.8.0-alpha] — 2025-12-01

### Versión alpha funcional

#### Añadido
- Panel estudiante completo: práctica, estadísticas, procedimientos
- Panel docente básico: grupos, dashboard, revisión de procedimientos
- Panel admin: aprobación de docentes, gestión de usuarios
- Sistema ELO básico (VectorRating, Factor K dinámico)
- Integración inicial con Supabase (PostgreSQL + Storage)
- KatIA chat socrático integrado en sala de estudio
