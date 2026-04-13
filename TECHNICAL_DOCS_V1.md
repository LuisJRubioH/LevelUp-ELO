# Documentación Técnica — LevelUp-ELO V1.0.0

> Versión: 1.0.0 | Fecha: 2026-04-12 | Autor: Luis Rubio
> Estado: **Estable** — tag git `v1.0.0`

---

## Índice

1. [Visión general](#1-visión-general)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Motor ELO — Algoritmos](#3-motor-elo--algoritmos)
4. [Banco de preguntas](#4-banco-de-preguntas)
5. [Capa de infraestructura](#5-capa-de-infraestructura)
6. [Integración de IA](#6-integración-de-ia)
7. [Interfaz de usuario (Streamlit)](#7-interfaz-de-usuario-streamlit)
8. [Base de datos — Esquema completo](#8-base-de-datos--esquema-completo)
9. [Seguridad](#9-seguridad)
10. [CI/CD y calidad](#10-cicd-y-calidad)
11. [Decisiones de diseño](#11-decisiones-de-diseño)
12. [Bugs conocidos y limitaciones de V1](#12-bugs-conocidos-y-limitaciones-de-v1)
13. [Guía de extensión](#13-guía-de-extensión)

---

## 1. Visión general

LevelUp-ELO es una plataforma de evaluación adaptativa para matemáticas. Usa el sistema de rating **ELO** — el mismo del ajedrez competitivo — para medir y ajustar el nivel de cada estudiante en tiempo real.

**Principio central**: cada respuesta actualiza simultáneamente el rating del alumno y el rating del ítem. El sistema siempre sirve el reto correcto usando la Zona de Desarrollo Próximo (ZDP) como criterio de selección.

### Stack tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.11+ |
| UI | Streamlit | 1.40–1.45 |
| DB local | SQLite | stdlib |
| DB producción | PostgreSQL (Supabase) | psycopg2-binary 2.9+ |
| ORM | Ninguno (SQL raw) | — |
| IA | Multi-proveedor (Groq, Anthropic, OpenAI…) | — |
| Hash | Argon2id | passlib 1.7+ |
| Storage | Supabase Storage | supabase 2.0+ |
| CI | GitHub Actions | — |
| Deploy | Streamlit Cloud | — |

---

## 2. Arquitectura del sistema

### Clean Architecture — 4 capas

```
┌──────────────────────────────────────────────────────────┐
│  interface/streamlit/                                    │
│  app.py (167 líneas) + views/ + state.py + assets.py    │
└────────────────────┬─────────────────────────────────────┘
                     │ importa
┌────────────────────▼─────────────────────────────────────┐
│  application/services/                                   │
│  StudentService  ·  TeacherService                       │
│  application/interfaces/repositories.py (Protocolos)    │
└────────────────────┬─────────────────────────────────────┘
                     │ implementa
┌────────────────────▼─────────────────────────────────────┐
│  infrastructure/                                         │
│  persistence/   storage/   external_api/   security/    │
└────────────────────┬─────────────────────────────────────┘
                     │ importa
┌────────────────────▼─────────────────────────────────────┐
│  domain/                                                 │
│  elo/  ·  selector/  ·  katia/  ·  entities.py          │
└──────────────────────────────────────────────────────────┘
```

**Regla de dependencia**: los imports fluyen hacia adentro (interface → domain). El dominio no importa nada externo.

### Protocolos ISP (Interface Segregation Principle)

```python
# src/application/interfaces/repositories.py
class IStudentRepository(Protocol):
    def get_next_items(...) -> list: ...
    def save_answer_transaction(...) -> None: ...

class ITeacherRepository(Protocol):
    def get_group_students(...) -> list: ...
    def export_teacher_student_data(...) -> list: ...

class IAdminRepository(Protocol):
    def approve_teacher(...) -> None: ...
    def reassign_student_group(...) -> None: ...
```

`StudentService` está tipado con `IStudentRepository` — no depende de la implementación concreta.

### Singleton del repositorio (producción)

En `app.py`:

```python
_REPO_SINGLETON = None
_REPO_LOCK = threading.Lock()

def _get_repo():
    global _REPO_SINGLETON
    if _REPO_SINGLETON is not None:
        return _REPO_SINGLETON
    with _REPO_LOCK:
        if _REPO_SINGLETON is None:
            _REPO_SINGLETON = PostgresRepository() if DATABASE_URL else SQLiteRepository()
    return _REPO_SINGLETON
```

Esto garantiza que todas las sesiones Streamlit compartan UN solo `ThreadedConnectionPool(1, 5)`.

---

## 3. Motor ELO — Algoritmos

### 3.1 ELO clásico

**Archivo**: `src/domain/elo/model.py`

```python
def expected_score(rating_a: float, rating_b: float) -> float:
    """P(A gana contra B) — fórmula FIDE estándar."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating: float, expected: float, actual: float, k: float) -> float:
    return rating + k * (actual - expected)
```

`actual` = 1.0 (correcto) o 0.0 (incorrecto). El ítem recibe el resultado opuesto: si el estudiante gana (1.0), el ítem pierde (0.0) y viceversa.

### 3.2 Factor K dinámico

```python
def dynamic_k(rating: float, attempts: int, recent_errors: list) -> float:
    if attempts < 30:
        k_base = 40          # Novato: converge rápido
    elif rating < 1400:
        k_base = 32
    elif error_rate(recent_errors[-20:]) < 0.15:
        k_base = 16          # Estable: cambios menores
    else:
        k_base = 24          # Default
    return k_base
```

### 3.3 VectorRating — ELO por tópico

**Archivo**: `src/domain/elo/vector_elo.py`

```python
@dataclass
class VectorRating:
    ratings: dict[str, tuple[float, float]]  # topic → (elo, rd)

    def update(self, topic: str, expected: float, actual: float,
                k_base: float, impact_modifier: float = 1.0):
        elo, rd = self.ratings.get(topic, (1000.0, 350.0))
        k_eff = k_base * (rd / RD_BASE) * impact_modifier
        new_elo = elo + k_eff * (actual - expected)
        new_rd = max(RD_MIN, rd * RD_DECAY)
        self.ratings[topic] = (new_elo, new_rd)

    def aggregate_global_elo(self) -> float:
        if not self.ratings:
            return 1000.0
        return sum(elo for elo, _ in self.ratings.values()) / len(self.ratings)
```

**Nota importante**: `impact_modifier` está fijado en `1.0` en producción. El `CognitiveAnalyzer` sigue existiendo pero su output no escala el delta ELO. Razón: el preview de puntos mostrado al estudiante no puede predecir el modifier, causando discrepancias.

### 3.4 Rating Deviation (Glicko simplificado)

**Archivo**: `src/domain/elo/uncertainty.py`

| Parámetro | Valor |
|---|---|
| RD inicial | 350.0 |
| RD mínimo | 30.0 |
| Decay por intento | `RD × 0.95` |

### 3.5 Selector adaptativo (ZDP)

**Archivo**: `src/domain/selector/item_selector.py`

```
Objetivo: P(éxito) ∈ [0.40, 0.75]
Maximiza: Fisher Information = P × (1 − P)
```

**Algoritmo de selección**:
1. Calcular `P(éxito)` para cada ítem candidato usando ELO actual del tópico
2. Filtrar candidatos en el rango ZDP `[0.40, 0.75]`
3. Si no hay candidatos, expandir ±0.05 (hasta 10 expansiones = rango `[−0.05, 1.25]`)
4. Dentro del rango, maximizar `P × (1−P)`
5. Prioridad: preguntas no vistas > preguntas falladas con cooldown ≥3

### 3.6 Transacción atómica al responder

**Archivo**: `src/infrastructure/persistence/{sqlite,postgres}_repository.py`

```python
def save_answer_transaction(self, user_id, item_id, is_correct,
                             new_student_rating, new_item_rating,
                             attempt_data):
    """
    Actualiza rating del estudiante, rating del ítem y guarda el intento
    en una sola transacción. Si falla, rollback completo.
    """
    conn = self.get_connection()
    try:
        cursor = conn.cursor(...)
        # 1. UPDATE users SET ... (ELO + RD)
        # 2. UPDATE items SET ... (dificultad + RD del ítem)
        # 3. INSERT INTO attempts ...
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        self.put_connection(conn)
```

---

## 4. Banco de preguntas

### 4.1 Estructura

Los ítems viven en `items/bank/` como archivos JSON:

```
items/bank/
├── calculo_diferencial.json      # Cálculo Diferencial (Universidad)
├── algebra_lineal.json           # Álgebra Lineal (Universidad)
├── ...
└── semillero/
    ├── algebra_semillero_6.json  # Álgebra grado 6° (Semillero)
    ├── algebra_semillero_7.json
    └── ...
```

### 4.2 Formato de ítem

```json
{
  "id": "cd_01",
  "content": "¿Cuál es la derivada de $f(x) = x^2$?",
  "difficulty": 800,
  "topic": "Derivadas básicas",
  "options": ["$2x$", "$x^2$", "$2$", "$x$"],
  "correct_option": "$2x$",
  "image_url": null,
  "tags": ["recordar", "derivadas", "potencia"]
}
```

**Invariantes**:
- `id` único en todo el banco
- `correct_option` debe ser exactamente uno de los strings en `options`
- LaTeX en JSON: backslashes doblados (`\\frac`, `\\sin`)
- `difficulty` recomendado: 600–1800 (ELO inicial del ítem)

### 4.3 Sincronización automática

Al arrancar, `sync_items_from_bank_folder()` escanea todos los JSON y:
1. Inserta cursos nuevos en `courses` (ON CONFLICT DO NOTHING)
2. Inserta ítems nuevos en `items` (ON CONFLICT DO NOTHING — NO sobreescribe ELO calculado)
3. Actualiza `image_url` y `tags` en ítems existentes si estaban NULL

En PostgreSQL usa `pg_try_advisory_lock(12348)` para que solo una instancia sincronice simultáneamente.

### 4.4 Validador de banco

```bash
python scripts/validate_bank.py
```

Verifica: campos requeridos, `correct_option` en `options`, difficulty en rango, IDs únicos. Exit code 1 si hay errores — integrado en CI y pre-commit.

### 4.5 Estadísticas actuales

| Bloque | Cursos | Ítems aprox. |
|---|---|---|
| Universidad | 6 | ~600 |
| Colegio | 4 | ~400 |
| Concursos | 2 | ~200 |
| Semillero | 36 archivos (6 materias × 6 grados) | ~770 |
| **Total** | **~48 archivos** | **~1.970** |

---

## 5. Capa de infraestructura

### 5.1 Dual DB — Selección automática

```python
# app.py — al arrancar
if os.environ.get("DATABASE_URL"):
    repo = PostgresRepository()    # Supabase (producción)
else:
    repo = SQLiteRepository()      # SQLite local (desarrollo)
```

Ambos repositorios implementan exactamente la misma API pública (~94 métodos). La regla Dual DB: cualquier cambio en uno debe replicarse en el otro en el mismo commit.

### 5.2 PostgresRepository — Detalles de implementación

**Pool de conexiones**:
```python
self._pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1, maxconn=5, **conn_kwargs
)
```

`ThreadedConnectionPool` es thread-safe (necesario para Streamlit Cloud con múltiples hilos). `maxconn=5` es el límite seguro para Supabase free tier.

**Patrón de uso de conexiones**:
```python
conn = self.get_connection()
try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # ... operaciones SQL ...
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    self.put_connection(conn)  # SIEMPRE devolver al pool
```

**Advisory locks** (migraciones/seeds idempotentes):
```python
cursor.execute("SELECT pg_try_advisory_lock(12345)")
locked = cursor.fetchone()["pg_try_advisory_lock"]
if not locked:
    return  # Otra instancia ya está ejecutando esta función
# ... trabajo ...
# finally: pg_advisory_unlock(12345) + put_connection()
```

Lock IDs usados: 12345 (_migrate_db), 12346 (_seed_admin), 12347 (_seed_demo_data), 12348 (sync_items), 12349 (_seed_test_students).

**Importante**: usar `pg_try_advisory_lock` (no-bloqueante), nunca `pg_advisory_lock` (bloqueante) ni `pg_advisory_xact_lock` — el `statement_timeout=60s` los cancela.

### 5.3 Secuencia de inicialización

Orden en el constructor de ambos repos:
```
init_db()               → CREATE TABLE IF NOT EXISTS (todas las tablas + índices)
_migrate_db()           → ALTER TABLE ADD COLUMN IF NOT EXISTS (migraciones aditivas)
_seed_admin()           → crea usuario admin si ADMIN_PASSWORD está definida
_seed_demo_data()       → crea profesor1, estudiante1, estudiante2 y grupos demo
_backfill_prob_failure()→ rellena prob_failure NULL en intentos históricos
sync_items_from_bank_folder() → sincroniza items/bank/*.json con la DB
_seed_test_students()   → crea 7 estudiantes de prueba (is_test_user=1)
```

### 5.4 Supabase Storage

**Bucket**: `procedimientos` (PRIVADO — no hay URLs públicas).

**Flujo de upload**:
```
bytes del archivo
  → supabase_storage.upload_file('procedimientos', path, bytes, mime)
  → retorna SOLO el path relativo: "38/alb31/hash.jpg"
  → DB guarda: storage_url = "38/alb31/hash.jpg"
  → Si falla: guarda bytes en image_data (BYTEA) como fallback
```

**Flujo de descarga** (para mostrar al docente/estudiante):
```
repo.resolve_storage_image(storage_url)
  → supabase_storage.get_file('procedimientos', storage_url)
  → extract_path() limpia el path (maneja URLs legacy y paths con bucket)
  → retorna bytes → st.image(bytes)
```

`extract_path()` maneja 3 formatos de entrada:
- URL completa: `https://xxx.supabase.co/.../procedimientos/38/alb31/hash.jpg` → `38/alb31/hash.jpg`
- Path con bucket: `procedimientos/38/alb31/hash.jpg` → `38/alb31/hash.jpg`
- Path limpio: `38/alb31/hash.jpg` → `38/alb31/hash.jpg`

---

## 6. Integración de IA

### 6.1 Multi-proveedor

**Archivo**: `src/infrastructure/external_api/ai_client.py`

Detección automática por prefijo de API key:

| Prefijo | Proveedor |
|---|---|
| `sk-ant-` | Anthropic Claude |
| `gsk_` | Groq |
| `AIzaSy` | Google Gemini |
| `hf_` | HuggingFace |
| `sk-proj-` / `sk-` | OpenAI |
| Sin prefijo | LM Studio / Ollama (local) |

Las API keys viven SOLO en `st.session_state` — nunca se persisten en DB, archivos ni logs.

Todas las funciones de IA **degradan con gracia**: si no hay cliente disponible, retornan valores neutros sin lanzar excepción al usuario.

### 6.2 Model Router

**Archivo**: `src/infrastructure/external_api/model_router.py`

Selección automática de modelo por tarea:
- `socratic`: rápido + razonamiento, excluye modelos lentos (>14B o MoE)
- `image_proc`: visión + razonamiento, retorna `None` si no hay modelo con visión disponible
- Fallback: modelo por defecto del proveedor

### 6.3 Chat socrático (KatIA)

**Parámetros**: `SOCRATIC_MAX_TOKENS = 120` — respuestas cortas para mantener el foco pedagógico.

**Post-validación** (`validate_socratic_response()`): verifica que la respuesta:
1. No revele la respuesta correcta
2. Tenga ≤3 oraciones

Si falla la validación, se usa un mensaje de fallback genérico.

### 6.4 Revisión de procedimientos manuscritos

**Archivo**: `src/infrastructure/external_api/math_procedure_review.py`

Solo disponible con Groq. Modelo: `meta-llama/llama-4-scout-17b-16e-instruct` (visión).

**Retorna JSON**:
```json
{
  "transcripcion": "...",
  "pasos": [...],
  "errores_detectados": [...],
  "saltos_logicos": [...],
  "resultado_correcto": true,
  "evaluacion_global": "...",
  "score_procedimiento": 85
}
```

**Ajuste ELO**: `elo_delta = (score − 50) × 0.2` → máximo ±10 puntos.

**Importante**: `ai_proposed_score` NUNCA afecta el ELO directamente. Solo el `teacher_score` (calificación oficial del docente) lo hace, vía `final_score`.

El LLM frecuentemente genera LaTeX sin escapar en JSON (`\frac` en lugar de `\\frac`). `_parse_json_response()` incluye un paso de escape de backslashes antes del `json.loads()`.

---

## 7. Interfaz de usuario (Streamlit)

### 7.1 Estructura de app.py (167 líneas)

```python
# 1. sys.path.insert(0, base_path)   ← ANTES de cualquier import src.*
# 2. configure_logging()
# 3. st.set_page_config()
# 4. apply_global_css()
# 5. _get_repo() → singleton PostgresRepository o SQLiteRepository
# 6. CookieManager() para persistencia de sesión
# 7. StudentService, TeacherService → session_state
# 8. Detección de proveedor de IA → session_state
# 9. Restauración de sesión por cookie (validate_session)
# 10. Routing por rol → render_auth() / render_student() / render_teacher() / render_admin()
```

### 7.2 Gestión de estado

Todo el estado compartido vive en `st.session_state`. Las claves más importantes:

| Clave | Tipo | Descripción |
|---|---|---|
| `db` | Repository | Instancia del repositorio (apunta al singleton) |
| `student_service` | StudentService | Servicio de lógica de estudiante |
| `logged_in` | bool | Estado de autenticación |
| `user_id` | int | ID del usuario autenticado |
| `role` | str | `student` / `teacher` / `admin` |
| `vector` | VectorRating | ELO vectorial del estudiante activo |
| `selected_course` | dict | Curso activo en la sala de estudio |
| `current_item` | dict | Pregunta activa |
| `session_start_time` | float | `time.time()` al hacer login |
| `question_start_time` | float | `time.time()` al cargar la pregunta |
| `cloud_api_key` | str | API key del proveedor de IA |
| `ai_provider` | str | Proveedor detectado |

### 7.3 Temporizadores en tiempo real

**Archivo**: `src/interface/streamlit/timers.py`

```python
# JavaScript setInterval — no depende de reruns de Streamlit
st.components.v1.html(f"""
<script>
  var start = {start_ts};
  setInterval(function() {{
    var elapsed = Math.floor(Date.now()/1000 - start);
    document.getElementById('{timer_id}').innerText = formatTime(elapsed);
  }}, 1000);
</script>
<div id="{timer_id}">00:00</div>
""")
```

IDs únicos generados con `_TIMER_ID_COUNTER` para evitar colisiones DOM en reruns.

### 7.4 Wizard de registro

Flujo multi-paso en `auth_view.py`:
- `st.session_state.reg_step`: paso actual (1 o 2)
- `st.session_state.reg_chosen_role`: rol elegido en paso 1

Paso 1: selección Estudiante / Docente. Paso 2: datos de cuenta (usuario, contraseña, nivel educativo, grado si es Semillero).

### 7.5 Reglas de renderizado HTML

Streamlit 1.55+ interpreta líneas con 4+ espacios como bloques de código en CommonMark. Siempre construir HTML sin indentación previa:

```python
# CORRECTO
_html = f'<div style="...">' + f'<p>...</p>' + f'</div>'
st.markdown(_html, unsafe_allow_html=True)
```

### 7.6 Componentes de Streamlit y versiones

En Streamlit Cloud (versión 1.40–1.44), `width="stretch"` NO es válido. Usar siempre:
- `st.image(..., use_container_width=True)`
- `st.button(..., use_container_width=True)`
- `st.plotly_chart(..., use_container_width=True)`
- `st.dataframe(..., use_container_width=True)`

---

## 8. Base de datos — Esquema completo

### Tablas principales

**`users`**
```sql
id               SERIAL PRIMARY KEY
username         TEXT UNIQUE NOT NULL
password_hash    TEXT NOT NULL          -- Argon2id
role             TEXT DEFAULT 'student' -- 'student'/'teacher'/'admin'
approved         INTEGER DEFAULT 1      -- 0=pendiente (docentes)
active           INTEGER DEFAULT 1      -- 0=desactivado
group_id         INTEGER                -- FK groups.id
education_level  TEXT                   -- 'universidad'/'colegio'/'concursos'/'semillero'
grade            TEXT                   -- '6'-'11' (solo semillero)
is_test_user     INTEGER DEFAULT 0      -- 1=protegido contra borrado
rating_deviation REAL DEFAULT 350.0
created_at       TIMESTAMP
```

**`items`**
```sql
id               TEXT PRIMARY KEY       -- Ej: 'cd_01'
topic            TEXT NOT NULL
content          TEXT NOT NULL          -- Soporta LaTeX ($...$)
options          TEXT NOT NULL          -- JSON array
correct_option   TEXT NOT NULL          -- Debe coincidir con uno de options
difficulty       REAL NOT NULL          -- Rating ELO del ítem
rating_deviation REAL DEFAULT 350.0
image_url        TEXT                   -- URL o path relativo (opcional)
tags             TEXT                   -- JSON array ['cognitiva','general','especifica']
course_id        TEXT                   -- FK courses.id
created_at       TIMESTAMP
```

**`attempts`**
```sql
id               SERIAL PRIMARY KEY
user_id          INTEGER NOT NULL       -- FK users.id
item_id          TEXT NOT NULL          -- FK items.id
is_correct       BOOLEAN NOT NULL
difficulty       INTEGER                -- ELO del ítem en ese momento
topic            TEXT
elo_after        REAL                   -- ELO del alumno post-respuesta
prob_failure     REAL                   -- 1 - P(éxito) calculada antes
expected_score   REAL                   -- P(éxito) según ELO
time_taken       REAL                   -- Segundos en responder
confidence_score REAL                   -- [0,1] CognitiveAnalyzer (desactivado)
error_type       TEXT                   -- 'conceptual'/'superficial'/'none'
rating_deviation REAL                   -- RD del tópico tras el intento
timestamp        TIMESTAMP
```

**`groups`**
```sql
id               SERIAL PRIMARY KEY
name             TEXT NOT NULL
teacher_id       INTEGER NOT NULL       -- FK users.id (docente propietario)
course_id        TEXT                   -- FK courses.id
name_normalized  TEXT                   -- nombre.strip().lower() para unicidad
invite_code      TEXT UNIQUE            -- Código inter-nivel generado por docente
created_at       TIMESTAMP
-- UNIQUE INDEX: (teacher_id, name_normalized)
-- UNIQUE INDEX: invite_code WHERE NOT NULL
```

**`enrollments`**
```sql
user_id          INTEGER NOT NULL       -- FK users.id
course_id        TEXT NOT NULL          -- FK courses.id
group_id         INTEGER                -- FK groups.id (NULL = legado sin grupo)
-- UNIQUE: (user_id, course_id, group_id)
```

**`procedure_submissions`**
```sql
id               SERIAL PRIMARY KEY
student_id       INTEGER NOT NULL       -- FK users.id
item_id          TEXT NOT NULL          -- FK items.id
image_data       BYTEA                  -- Fallback si Storage falla
storage_url      TEXT                   -- Path relativo en Supabase Storage
mime_type        TEXT                   -- 'image/jpeg', 'application/pdf', etc.
file_hash        TEXT                   -- SHA-256 anti-plagio
status           TEXT DEFAULT 'pending' -- 'pending'/'PENDING_TEACHER_VALIDATION'/'VALIDATED_BY_TEACHER'/'reviewed'
ai_proposed_score REAL                  -- Score 0-100 de la IA (NO afecta ELO)
teacher_score    REAL                   -- Score oficial del docente (SÍ afecta ELO)
final_score      REAL                   -- = teacher_score
elo_delta        REAL                   -- (final_score - 50) × 0.2
proc_elo_applied INTEGER DEFAULT 0      -- Flag para no aplicar ELO dos veces
teacher_comment  TEXT
created_at       TIMESTAMP
reviewed_at      TIMESTAMP
```

**`katia_interactions`**
```sql
id               SERIAL PRIMARY KEY
user_id          INTEGER NOT NULL
course_id        TEXT
item_id          TEXT
item_topic       TEXT
student_message  TEXT
katia_response   TEXT
created_at       TIMESTAMP
```

**`problem_reports`**
```sql
id               SERIAL PRIMARY KEY
user_id          INTEGER NOT NULL
description      TEXT NOT NULL          -- Mín 10 caracteres
status           TEXT DEFAULT 'pending' -- 'pending'/'resolved'
created_at       TIMESTAMP
```

**`sessions`**
```sql
token            TEXT PRIMARY KEY
user_id          INTEGER NOT NULL
expires_at       TIMESTAMP NOT NULL
```

**`audit_group_changes`**
```sql
id               SERIAL PRIMARY KEY
student_id       INTEGER NOT NULL
old_group_id     INTEGER
new_group_id     INTEGER
admin_id         INTEGER NOT NULL
timestamp        TIMESTAMP
```

### Índices de performance

```sql
idx_attempts_user_id             -- attempts(user_id)
idx_enrollments_user_id          -- enrollments(user_id)
idx_groups_teacher_id            -- groups(teacher_id)
idx_procedure_submissions_student_id
idx_groups_teacher               -- groups(teacher_id)
idx_users_group                  -- users(group_id)
```

---

## 9. Seguridad

### Contraseñas

**Algoritmo actual**: Argon2id via `passlib[argon2]`.

**Migración legacy**: en el login, si el hash es SHA-256 (legacy), se verifica con SHA-256. Si es correcto, se rehashea con Argon2id y se actualiza en DB — transparente para el usuario. Las cuentas con hash vacío/null se desactivan en `_migrate_db()`.

### API Keys

- Viven SOLO en `st.session_state.cloud_api_key`
- NUNCA se guardan en DB, archivos, logs ni variables de módulo
- Se detecta el proveedor automáticamente desde el prefijo de la key

### Admin

- Credenciales solo desde variables de entorno (`ADMIN_PASSWORD`, `ADMIN_USER`)
- Sin credenciales hardcodeadas en código
- Si `ADMIN_PASSWORD` no está definida, no se crea ningún admin

### Protección de datos

- `is_test_user=1`: estudiantes protegidos contra borrado por cualquier flujo
- Storage: bucket `procedimientos` es PRIVADO — las imágenes se sirven descargando bytes, nunca con URLs públicas
- Anti-plagio: SHA-256 del archivo se verifica antes de aceptar un procedimiento

---

## 10. CI/CD y calidad

### GitHub Actions — `ci.yml`

5 jobs ejecutados en cada push a `main`:

```
validate-bank ──────────────────────────────── (paralelo)
lint ────────────────────────────────────────── (paralelo)
test-unit ──── test-integration ── db-sync      (secuencial)
```

| Job | Herramienta | Criterio de éxito |
|---|---|---|
| validate-bank | `scripts/validate_bank.py` | Exit 0 |
| lint | Black (line-length=100) + Flake8 (E9,F63,F7,F82) | 0 errores |
| test-unit | pytest + pytest-cov | 108 tests OK, cobertura ≥70% |
| test-integration | pytest | 4 tests OK |
| db-sync | `scripts/db_sync_check.py` | 0 diferencias de API |

### Pre-commit hooks (`.pre-commit-config.yaml`)

Se ejecutan antes de cada commit local:
1. `trailing-whitespace` — elimina espacios finales
2. `end-of-file-fixer` — newline al final
3. `check-json` — valida JSON (solo archivos .json)
4. `check-merge-conflict` — detecta marcadores `<<<<<<`
5. `black` — formatea Python (line-length=100)
6. `validate-bank` — valida integridad del banco (solo si hay cambios en items/)
7. `db-sync-check` — verifica paridad SQLite/PostgreSQL (solo si hay cambios en repos)
8. `pytest-unit` — corre tests unitarios (solo si hay cambios en src/ o tests/)

### Cobertura de tests

```
src/domain/elo/model.py          → 98%
src/domain/elo/vector_elo.py     → 88%
src/domain/elo/uncertainty.py    → 88%
src/domain/selector/item_selector.py → 100%
src/domain/katia/katia_messages.py   → 100%
src/application/services/student_service.py → 78%
src/application/services/teacher_service.py → 86%
─────────────────────────────────────────────
TOTAL                            → 85%
```

### Herramientas de desarrollo

```bash
# Formatear código
black --line-length=100 src/ tests/ scripts/

# Verificar linting
flake8 src/ tests/ scripts/ --select=E9,F63,F7,F82 --max-line-length=100

# Validar banco de preguntas
python scripts/validate_bank.py

# Verificar paridad SQLite/PostgreSQL
python scripts/db_sync_check.py
```

---

## 11. Decisiones de diseño

### ¿Por qué ELO vectorial por tópico y no uno global?

Un ELO global no distingue entre un estudiante que domina álgebra pero falla en cálculo integral. Con ELO por tópico, el selector puede servir retos de dificultad apropiada para CADA área, maximizando el aprendizaje.

### ¿Por qué `impact_modifier=1.0` siempre?

`CognitiveAnalyzer` detecta confianza y tipo de error para escalar el delta ELO. Pero la UI muestra un "preview de puntos" antes de responder (`K × (1 − P(éxito))`) que no puede predecir el modifier. Esto causaba discrepancias frustrantes para el estudiante. La decisión: desactivar el modifier, mantener la predicción precisa. El CognitiveAnalyzer queda como infraestructura lista para V2.

### ¿Por qué dual DB (SQLite + PostgreSQL)?

SQLite para desarrollo local: zero config, portable, testeable sin conexión externa. PostgreSQL (Supabase) para producción: concurrent access, pool de conexiones, Storage para procedimientos. La misma API pública en ambos permite cambiar de backend con una sola variable de entorno.

### ¿Por qué Clean Architecture para un proyecto Streamlit?

Streamlit monolítico con 3700 líneas en `app.py` era imposible de testear y mantener. Clean Architecture fuerza la separación de dominio, servicios y UI. El beneficio concreto: el dominio ELO se puede testear sin Streamlit. Los servicios se pueden testear sin DB. Los repositorios se pueden testear sin UI.

### ¿Por qué Singleton para PostgresRepository?

Streamlit Cloud ejecuta un único proceso Python con múltiples threads (uno por sesión/rerun). Sin singleton, cada sesión crea su propio `ThreadedConnectionPool(1,5)`. Con 3 usuarios simultáneos = 3 pools × 5 conexiones = hasta 15 conexiones a Supabase, que excede el límite del free tier. El singleton garantiza un solo pool de 5 conexiones para TODOS los usuarios.

### ¿Por qué SQL raw en lugar de ORM?

SQLAlchemy añadiría complejidad y overhead para un proyecto donde las queries son conocidas y controladas. SQL raw con `RealDictCursor` (PostgreSQL) y `row_factory=sqlite3.Row` (SQLite) da acceso por nombre de columna, es legible y predecible.

---

## 12. Bugs conocidos y limitaciones de V1

### Limitaciones estructurales de Streamlit

| Limitación | Impacto | Solución en V2 |
|---|---|---|
| Rerun completo en cada interacción | UX lenta en conexiones lentas | React con actualizaciones parciales |
| Un hilo por sesión (GIL Python) | No escala bien con muchos usuarios concurrentes | FastAPI async + Uvicorn workers |
| Sin routing nativo | URLs no compartibles | React Router |
| Sin WebSockets nativos | Sin notificaciones en tiempo real | WebSocket nativo en FastAPI |

### Comportamientos conocidos

- **CognitiveAnalyzer desactivado**: el campo `confidence_score` en `attempts` siempre es NULL en producción. El análisis cognitivo existe pero no escala el ELO.

- **`pg_try_advisory_lock` por sesión**: los advisory locks son de nivel sesión. Si la conexión se cierra antes del `pg_advisory_unlock`, PostgreSQL libera el lock automáticamente — esto es correcto y esperado.

- **Streaming en Streamlit**: el streaming del chat socrático usa `st.write_stream()` que re-renderiza en cada token. En conexiones lentas puede verse entrecortado.

- **Banners pixel art**: se cargan como base64 desde archivos locales con `@st.cache_resource`. Si los archivos no existen en el deploy, las tarjetas de curso se muestran sin banner (sin error).

---

## 13. Guía de extensión

### Agregar un nuevo curso

1. Crear `items/bank/mi_curso.json` con un array de ítems válidos
2. Agregar en **ambos** repositorios:
   ```python
   # En _COURSE_BLOCK_MAP
   'mi_curso': 'Universidad',  # o 'Colegio', 'Concursos', 'Semillero'
   # En _COURSE_NAME_MAP
   'mi_curso': 'Mi Curso — Nombre Legible',
   ```
3. Ejecutar `python scripts/validate_bank.py`
4. Reiniciar la app — `sync_items_from_bank_folder()` carga automáticamente

### Agregar un nuevo método al repositorio

1. Definir la firma en `src/application/interfaces/repositories.py` si es un caso de uso nuevo
2. Implementar en `sqlite_repository.py`
3. Implementar en `postgres_repository.py` (misma firma, mismo comportamiento)
4. Ejecutar `python scripts/db_sync_check.py` — debe retornar 0 errores
5. Agregar test unitario o de integración

### Agregar un nuevo proveedor de IA

En `src/infrastructure/external_api/ai_client.py`:
```python
PROVIDERS = {
    'mi_proveedor': {
        'label': 'Mi Proveedor',
        'base_url': 'https://api.miproveedor.com/v1',
        'model_cog': 'modelo-rapido',
        'model_analysis': 'modelo-vision',
    }
}
# Agregar detección por prefijo en detect_provider_from_key()
```

### Agregar una nueva tabla

1. En `init_db()` de ambos repos: `CREATE TABLE IF NOT EXISTS nueva_tabla (...)`
2. En `_migrate_db()` de ambos repos: `ALTER TABLE ADD COLUMN IF NOT EXISTS ...` para columnas futuras
3. Nunca `DROP TABLE` ni `DROP COLUMN` — migraciones solo aditivas

### Agregar un test unitario de dominio

```python
# tests/unit/domain/test_mi_modulo.py
import pytest
from src.domain.elo.model import expected_score

class TestExpectedScore:
    def test_equal_ratings_gives_half(self):
        assert expected_score(1000, 1000) == pytest.approx(0.5)

    def test_higher_rating_gives_more(self):
        assert expected_score(1200, 1000) > 0.5
```

Los tests de dominio no necesitan DB ni Streamlit — corren en milisegundos.
