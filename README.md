# LevelUp-ELO

> Plataforma de evaluación y aprendizaje adaptativo basada en el sistema de rating **ELO** — el mismo del ajedrez competitivo — aplicado a la educación matemática.

[![CI](https://github.com/LuisJRubioH/LevelUp-ELO/actions/workflows/ci.yml/badge.svg)](https://github.com/LuisJRubioH/LevelUp-ELO/actions/workflows/ci.yml)
[![Versión](https://img.shields.io/badge/versión-1.0.0-blue)](https://github.com/LuisJRubioH/LevelUp-ELO/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.11+-green)](https://www.python.org/)
[![Licencia](https://img.shields.io/badge/licencia-MIT-orange)](LICENSE)

**Demo en producción**: [levelup-elo.streamlit.app](https://levelup-elo-9yg9ewez4smvlylgwcls2q.streamlit.app)

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
- [Agregar preguntas al banco](#agregar-preguntas-al-banco)
- [CI/CD](#cicd)
- [Tests](#tests)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Roadmap](#roadmap)

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
- **Model Router inteligente**: selecciona el mejor modelo por tarea (socrático → rápido+razonamiento, imagen → visión+razonamiento).

### Plataforma completa
- **Dual DB**: SQLite local y PostgreSQL (Supabase) con API pública idéntica. Selección automática por `DATABASE_URL`.
- **Tres roles**: estudiante, docente, admin con flujos completos.
- **Dashboard docente**: ELO por tópico, tasa de error, análisis pedagógico con IA, exportación CSV/XLSX.
- **Supabase Storage**: procedimientos en bucket privado con fallback BYTEA en DB.
- **Seguridad**: Argon2id para contraseñas, migración transparente desde SHA-256 legacy, API keys solo en session_state.
- **Temporizadores en tiempo real**: JavaScript `setInterval` — cronómetro de sesión + cronómetro por pregunta, sin reruns de Streamlit.
- **Ranking de 16 niveles**: Aspirante (0–399) → Leyenda Suprema (2500+), separado por nivel educativo.
- **Anti-plagio SHA-256**: detecta procedimientos duplicados del mismo estudiante en el mismo ejercicio.

---

## Arquitectura

**Clean Architecture** con cuatro capas:

```
src/
├── domain/                      # Lógica de negocio pura — sin dependencias externas
│   ├── elo/
│   │   ├── model.py             # Factor K dinámico, ELO clásico
│   │   ├── vector_elo.py        # VectorRating: ELO + RD por tópico
│   │   ├── uncertainty.py       # RatingModel (Glicko simplificado)
│   │   ├── cognitive.py         # CognitiveAnalyzer (desactivado en producción)
│   │   └── zdp.py               # Cálculo del intervalo ZDP
│   ├── selector/
│   │   └── item_selector.py     # AdaptiveItemSelector (Fisher Information)
│   ├── katia/
│   │   └── katia_messages.py    # Bancos de mensajes de KatIA
│   └── entities.py              # Constantes y dataclasses de dominio
│
├── application/
│   ├── interfaces/
│   │   └── repositories.py      # Protocolos ISP: IStudentRepository, ITeacherRepository, IAdminRepository
│   └── services/
│       ├── student_service.py   # process_answer(), get_next_question(), get_socratic_help()
│       └── teacher_service.py   # Análisis pedagógico con IA
│
├── infrastructure/
│   ├── persistence/
│   │   ├── sqlite_repository.py    # SQLite: esquema, migraciones, seed (~1200 líneas)
│   │   └── postgres_repository.py  # PostgreSQL (psycopg2): port completo para Supabase
│   ├── storage/
│   │   └── supabase_storage.py     # Cliente Supabase Storage (bucket privado)
│   ├── external_api/
│   │   ├── ai_client.py            # Cliente multi-proveedor de IA
│   │   ├── math_procedure_review.py # Revisión manuscritos (Groq + Llama 4 Scout)
│   │   ├── model_router.py         # Selección inteligente de modelo por tarea
│   │   └── pedagogical_feedback.py # Hints socráticos por tipo de error
│   └── security/
│       └── hashing_service.py      # Argon2id + migración SHA-256
│
└── interface/
    └── streamlit/
        ├── app.py               # Punto de entrada (167 líneas) — setup + routing
        ├── state.py             # login(), logout(), helpers de session_state
        ├── assets.py            # CSS global, logo, banners pixel art
        ├── timers.py            # Componentes JavaScript de temporizadores
        └── views/
            ├── auth_view.py     # Login + wizard de registro multi-paso
            ├── student_view.py  # Práctica, estadísticas, procedimientos, feedback
            ├── teacher_view.py  # Dashboard, revisión de procedimientos, exportación
            └── admin_view.py    # Gestión de usuarios, grupos, reportes técnicos
```

### Regla de dependencia

```
domain/ ← application/ ← infrastructure/ ← interface/
```

Nunca al revés. El dominio no importa nada de infraestructura. Los servicios reciben los repositorios por constructor (DI).

---

## Motor ELO — Cómo funciona

### Flujo al responder una pregunta

```
app.py → StudentService.process_answer()
           ├→ VectorRating.update()          ← aplica delta ELO al tópico
           ├→ Repository.update_item_rating() ← actualiza dificultad del ítem
           └→ Repository.save_attempt()       ← persiste metadatos del intento
```

Todo ocurre en una **transacción atómica** (`save_answer_transaction`) — si falla el update del ítem, el intento tampoco se guarda.

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

### Formato de un ítem

```json
{
  "id": "cd_01",
  "content": "¿Cuál es la derivada de $f(x) = x^2$?",
  "difficulty": 800,
  "topic": "Derivadas básicas",
  "options": ["$2x$", "$x^2$", "$2$", "$x$"],
  "correct_option": "$2x$",
  "tags": ["recordar", "derivadas", "potencia"]
}
```

### Agregar preguntas al banco

1. Crear o editar `items/bank/<course_id>.json`
2. Agregar `'<course_id>': 'Bloque'` en `_COURSE_BLOCK_MAP` de **ambos** repositorios
3. Correr `python scripts/validate_bank.py`
4. Reiniciar la app — `sync_items_from_bank_folder()` carga automáticamente

---

## Roles de usuario

| Rol | Acceso |
|---|---|
| **Estudiante** | Práctica adaptativa, estadísticas, procedimientos, chat con KatIA, racha por materia, ranking |
| **Docente** | Dashboard ELO por alumno/tópico, revisión de procedimientos, análisis con IA, exportación CSV/XLSX, códigos de invitación inter-nivel |
| **Admin** | Aprobación de docentes, reasignación de estudiantes (auditada), gestión de usuarios, reportes técnicos |

---

## Instalación local

```bash
# Clonar el repositorio
git clone https://github.com/LuisJRubioH/LevelUp-ELO.git
cd LevelUp-ELO

# Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Instalar pre-commit hooks (opcional, recomendado)
pip install pre-commit
pre-commit install

# Ejecutar la app (siempre desde la raíz del repo)
streamlit run src/interface/streamlit/app.py
```

Sin `DATABASE_URL`, usa SQLite local (`data/elo_database.db`). La base de datos se crea automáticamente con datos demo.

---

## Despliegue en producción

La app está desplegada en **Streamlit Cloud** con **Supabase** como backend.

### Streamlit Cloud

1. Conectar el repositorio en [share.streamlit.io](https://share.streamlit.io)
2. Main file: `src/interface/streamlit/app.py`
3. Configurar secrets (ver Variables de entorno)

### Variables de entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | URL PostgreSQL Supabase (`postgresql://...`) | Sí (producción) |
| `ADMIN_PASSWORD` | Contraseña del usuario admin | Sí |
| `ADMIN_USER` | Nombre del admin (default: `admin`) | No |
| `SUPABASE_URL` | URL del proyecto Supabase | Sí (Storage) |
| `SUPABASE_KEY` | Publishable key de Supabase | Sí (Storage) |

> **Nota Supabase**: usar el **connection pooler** (puerto 6543, `aws-...pooler.supabase.com`) en lugar de la conexión directa (puerto 5432). El pool interno usa `ThreadedConnectionPool(minconn=1, maxconn=5)` — nunca subir `maxconn` más de 5 en el free tier.

---

## CI/CD

GitHub Actions con 5 jobs en cada push a `main`:

| Job | Qué verifica |
|---|---|
| `validate-bank` | `python scripts/validate_bank.py` — estructura e integridad de los 1.900+ ítems |
| `lint` | Black (line-length=100) + Flake8 (E9, F63, F7, F82) |
| `test-unit` | `pytest tests/unit/` — 108 tests, cobertura ≥80% |
| `test-integration` | `pytest tests/integration/` — 4 tests SQLite end-to-end |
| `db-sync` | `python scripts/db_sync_check.py` — paridad de API SQLite ↔ PostgreSQL |

Pre-commit hooks locales: validate-bank, db-sync-check, Black, pytest-unit.

---

## Tests

```bash
# Tests unitarios con cobertura
python -m pytest tests/unit/ -v --cov=src/domain --cov=src/application --cov-fail-under=80

# Tests de integración
python -m pytest tests/integration/ -v

# Validar banco de preguntas
python scripts/validate_bank.py

# Verificar paridad SQLite/PostgreSQL
python scripts/db_sync_check.py
```

**Cobertura actual**: 85% (dominio + servicios de aplicación).

---

## Usuarios de prueba

| Usuario | Contraseña | Rol / Nivel |
|---|---|---|
| `admin` | (variable de entorno) | Admin |
| `profesor1` | `demo1234` | Docente (pre-aprobado) |
| `estudiante1` | `demo1234` | Estudiante — Universidad |
| `estudiante2` | `demo1234` | Estudiante — Colegio |
| `estudiante_colegio_1..3` | `test1234` | Estudiante Colegio (is_test_user=1) |
| `estudiante_universidad_1..2` | `test1234` | Estudiante Universidad (is_test_user=1) |
| `estudiante_semillero_1` | `test1234` | Estudiante Semillero grado 9 |
| `estudiante_semillero_2` | `test1234` | Estudiante Semillero grado 11 |

---

## Roadmap

**V1.0.0** (actual) — Plataforma Streamlit estable con Clean Architecture, CI/CD, 85% cobertura de tests.

**V2.0** (en desarrollo) — Migración a FastAPI + React:
- API REST + WebSocket (39 endpoints, ya implementados en `api/`)
- Frontend React + TypeScript + Tailwind + shadcn/ui
- El motor ELO, dominio y IA se reutilizan sin cambios
- Deploy: Railway (API) + Vercel (frontend)

Ver [`ROADMAP_V2.md`](ROADMAP_V2.md) para el plan completo.

---

## Licencia

MIT — ver [LICENSE](LICENSE).
