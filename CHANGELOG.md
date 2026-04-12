# Changelog — LevelUp-ELO

Todos los cambios notables del proyecto se documentan en este archivo.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).
Versioning basado en [Semantic Versioning](https://semver.org/lang/es/).

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
