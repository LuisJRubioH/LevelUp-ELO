# CLAUDE.md — LevelUp-ELO

Instrucciones para Claude Code al trabajar en este repositorio.

---

## Inicio rápido

```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```

Ejecutar siempre desde la **raíz del repo** — `app.py` inyecta el root en `sys.path` en runtime. No hay tests ni linting configurados.

---

## Reglas de comportamiento (leer antes de cualquier tarea)

### Regla #1 — Dual DB: siempre los dos o ninguno
Cualquier cambio en `sqlite_repository.py` **debe replicarse** en `postgres_repository.py` y viceversa. Ambos tienen exactamente la misma API pública. Si modificas uno y no el otro, rompes producción (Supabase) o desarrollo local.

**Checklist mental antes de editar un repositorio:**
- [ ] ¿Toqué `sqlite_repository.py`? → editar también `postgres_repository.py`
- [ ] ¿Toqué `postgres_repository.py`? → editar también `sqlite_repository.py`
- [ ] ¿Agregué una tabla? → crear migración `ALTER TABLE ADD COLUMN IF NOT EXISTS` en ambos
- [ ] ¿Modifiqué `_COURSE_BLOCK_MAP`? → sincronizar en ambos repos

### Regla #2 — Clean Architecture: no cruzar capas
```
domain/     → sin imports de application/, infrastructure/ ni interface/
application/ → puede importar domain/, NO infrastructure/ directamente (usa interfaces)
infrastructure/ → implementa interfaces definidas en domain/ o application/
interface/  → puede importar todo, pero preferir application/services/
```
Si necesitas lógica de negocio nueva → va en `domain/`. Si necesitas un caso de uso → va en `application/services/`. Nunca pongas SQL en `domain/` ni lógica ELO en `infrastructure/`.

### Regla #3 — PostgreSQL: nunca `row[0]`, siempre `row['column']`
El repo PostgreSQL usa `RealDictCursor`. Acceder por índice numérico rompe silenciosamente. Las fechas son objetos `datetime`, no strings — siempre `str(row['created_at'])[:10]`.

### Regla #4 — Connection pool: nunca `conn.close()`
En el repo PostgreSQL usar siempre `self.put_connection(conn)` para devolver la conexión al pool. `conn.close()` destruye la conexión y agota el pool.

### Regla #5 — Ítems del banco: LaTeX siempre escapado
En JSON, los backslashes de LaTeX deben estar doblados: `\\frac`, `\\sin`, `\\alpha`. Un `\f` sin escapar causa `JSONDecodeError` en runtime. El campo `correct_option` debe coincidir carácter por carácter con uno de los strings en `options`.

### Regla #6 — is_test_user: nunca eliminar
Los estudiantes con `is_test_user=1` están protegidos. Nunca remover este flag ni agregar lógica que los borre.

### Regla #7 — API keys: nunca persistir
Las API keys viven solo en `st.session_state`. Nunca guardarlas en DB, archivos, logs ni variables de módulo.

### Regla #8 — Migraciones: solo aditivas
Solo `ALTER TABLE ADD COLUMN IF NOT EXISTS`. Nunca `DROP COLUMN`, `DROP TABLE`, ni cambios de tipo. Las migraciones destructivas rompen datos de producción.

### Regla #9 — Supabase Storage: paths relativos, nunca URLs
`upload_file()` debe retornar SOLO el path relativo (ej: `38/alb31/hash.jpg`), NUNCA una URL completa (`https://xxx.supabase.co/storage/v1/...`). El bucket `procedimientos` es PRIVADO — las URLs públicas no funcionan. Para mostrar imágenes, descargar los bytes con `get_file()` y pasarlos a `st.image()`. Si el upload falla, guardar en `image_data` (BYTEA) como fallback. Nunca dejar ambos (`storage_url` e `image_data`) en NULL.

---

## Skills disponibles

Consultar la skill correspondiente **antes de empezar** cuando la tarea entre en alguna de estas categorías:

| Tarea | Skill a consultar |
|---|---|
| Modificar repositorios, tablas, migraciones, seeds, queries | `.claude/skills/db-dual-backend.md` |
| Agregar servicios, modificar domain/app/infra, crear módulos | `.claude/skills/clean-architecture.md` |
| Crear o editar ítems, agregar cursos, modificar banco de preguntas | `.claude/skills/items-bank.md` |
| Después de modificar cualquier repositorio | `.claude/skills/db-sync-checker.md` + `python scripts/db_sync_check.py` |

---

## Arquitectura

Clean Architecture con cuatro capas dentro de `src/`:

- **`domain/`** — Lógica de negocio pura, sin dependencias externas.
  - `elo/model.py` — Factor K dinámico, ELO clásico, dataclasses `Item`/`StudentELO`.
  - `elo/vector_elo.py` — `VectorRating`: ELO + Rating Deviation (RD) por tópico.
  - `elo/uncertainty.py` — `RatingModel` (Glicko-simplificado): RD inicial=350, mín=30, decay=RD×0.95 por intento.
  - `elo/cognitive.py` — `CognitiveAnalyzer`: clasifica respuestas del estudiante vía IA → `impact_modifier` ∈ [0.5, 1.5].
  - `elo/zdp.py` — Cálculo del intervalo ZDP.
  - `selector/item_selector.py` — `AdaptiveItemSelector`: selección por Fisher Information.

- **`application/services/`** — Orquestadores de casos de uso:
  - `student_service.py` — `process_answer()`, `get_next_question()`, `get_socratic_help()`.
  - `teacher_service.py` — Análisis del dashboard y reportes con IA.

- **`infrastructure/`**
  - `persistence/sqlite_repository.py` — SQLite: esquema, migraciones, seed, queries (~1200 líneas). Fallback local.
  - `persistence/postgres_repository.py` — PostgreSQL (psycopg2): port completo de SQLite para producción (Supabase). Pool `SimpleConnectionPool(1–5)`, `RealDictCursor`, `ON CONFLICT DO NOTHING`, `SERIAL PRIMARY KEY`, `BYTEA`.
  - `persistence/seed_test_students.py` — Seed idempotente de 5 estudiantes de prueba.
  - `storage/supabase_storage.py` — Cliente Supabase Storage. Upload/download de archivos al bucket `procedimientos`. Lee `SUPABASE_URL` y `SUPABASE_KEY` de env vars. Degrada con gracia si no están definidas.
  - `external_api/ai_client.py` — Cliente universal multi-proveedor de IA.
  - `external_api/math_procedure_review.py` — Revisión de procedimientos manuscritos (Groq + Llama 4 Scout).
  - `external_api/model_router.py` — Router inteligente: selecciona mejor modelo por tarea.
  - `external_api/model_capability_detector.py` — Detecta capacidades (visión/razonamiento/velocidad) desde nombre del modelo.
  - `external_api/symbolic_math_verifier.py` — Verificación algebraica con SymPy en 4 capas.
  - `external_api/math_step_extractor.py` — Extrae y clasifica pasos matemáticos de OCR.
  - `external_api/math_ocr.py` — Pipeline OCR: pix2tex > tesseract > regex.
  - `external_api/math_reasoning_analyzer.py` — Análisis de razonamiento paso a paso.
  - `external_api/pedagogical_feedback.py` — Hints socráticos rotantes por tipo de error (nunca revela la respuesta).
  - `external_api/math_analysis_pipeline.py` — Pipeline completo: OCR → pasos → verificación simbólica → feedback.
  - `security/hashing_service.py` — Argon2id + migración transparente desde SHA-256 legacy.

- **`interface/streamlit/app.py`** — UI monolítica: login, panel estudiante, dashboard docente, panel admin.

### Flujo de datos al responder una pregunta

```
app.py → StudentService.process_answer()
           ├→ CognitiveAnalyzer.analyze_cognition()   ← IA clasifica razonamiento
           ├→ VectorRating.update()                   ← aplica delta ELO con impact_modifier
           ├→ Repository.update_item_rating()          ← actualiza dificultad del ítem
           └→ Repository.save_attempt()                ← persiste metadatos del intento
```

---

## Conceptos clave del dominio

- **VectorRating**: ELO + RD por tópico (no uno global). `aggregate_global_elo()` promedia para mostrar.
- **Factor K dinámico** (`domain/elo/model.py`):
  - K=40 (< 30 intentos) → K=32 (ELO < 1400) → K=16 (estable, error < 15% en últimos 20) → K=24 (default).
  - K efectivo escala con RD: `K_eff = K_BASE × (RD / RD_BASE)`.
- **AdaptiveItemSelector**: selecciona preguntas donde P(éxito) ∈ [0.4, 0.75] (ZDP). Maximiza Fisher Information `P×(1−P)`. Expande ±0.05 por paso (hasta 10) si no hay candidatos. Prioriza preguntas no vistas, luego falladas con ≥3 de cooldown.
- **CognitiveAnalyzer**: clasifica confianza [0,1] y tipo de error (`conceptual`/`superficial`). Combinado con tiempo de respuesta para calcular `impact_modifier`.
- **ELO del ítem**: los ítems tienen su propio rating de dificultad que se actualiza simétricamente (el ítem "pierde" cuando el estudiante gana).
- **Ranking de 16 niveles**: Aspirante (0–399) → Leyenda Suprema (2500+).
- **Racha de estudio**: días consecutivos de actividad.

---

## Base de datos

### Selección automática de backend

```python
# En app.py — selección de repo al arrancar
if os.environ.get("DATABASE_URL"):
    repo = PostgresRepository()   # producción (Supabase)
else:
    repo = SQLiteRepository()     # desarrollo local
```

### SQLite (local)
Archivo en `data/elo_database.db` (ruta fija, se crea automáticamente). Override con env var `DB_PATH`.

### PostgreSQL (producción)
Lee env var `DATABASE_URL` (formato: `postgresql://user:pass@host:port/dbname`). Pool `SimpleConnectionPool(minconn=1, maxconn=5)`. URL parseada por regex para manejar caracteres especiales en contraseñas. `sslmode='require'` y `statement_timeout=60000` (60s) en cada conexión.

**IMPORTANTE:** Supabase free tier limita las conexiones. `minconn=1, maxconn=5` es el máximo seguro. NUNCA subir `maxconn` a 10 o más — causa `MaxClientsInSessionMode`.

### Inicialización (ambos repos)
`init_db()` → `_migrate_db()` → `_seed_admin()` → `_seed_demo_data()` → `_backfill_prob_failure()` → `sync_items_from_bank_folder()` → `_seed_test_students()`

- Migraciones **solo aditivas** (`ALTER TABLE ADD COLUMN IF NOT EXISTS`).
- PostgreSQL: `pg_advisory_lock(12345)` envuelve `_migrate_db()` para evitar deadlocks cuando Streamlit ejecuta múltiples instancias en paralelo.
- PostgreSQL: retry logic (3 intentos) para `DeadlockDetected`/`QueryCanceled` con `time.sleep(2)` entre reintentos.
- Admin solo se crea si la env var `ADMIN_PASSWORD` está seteada (`ADMIN_USER` default `"admin"`). Sin credenciales hardcodeadas.

### Tablas principales

| Tabla | Detalles clave |
|---|---|
| `users` | `role` (student/teacher/admin), `approved`, `active`, `group_id`, `education_level`, `is_test_user` (protege contra borrado), `rating_deviation` |
| `groups` | Índice único en `(teacher_id, name_normalized)` — sin nombres duplicados por docente |
| `items` | `difficulty`, `rating_deviation`, `image_url` (opcional) |
| `attempts` | `elo_after`, `prob_failure`, `expected_score`, `time_taken`, `confidence_score`, `error_type`, `rating_deviation` |
| `courses` | `id` (slug), `name`, `block` (Universidad/Colegio/Concursos) |
| `enrollments` | `user_id`, `course_id`, `group_id` |
| `procedure_submissions` | `image_data` (BLOB/BYTEA fallback), `storage_url` (path en Supabase Storage, ej: `38/alb31/hash.jpg`), `procedure_image_path` (ruta local legacy), `status` (pending/reviewed/PENDING_TEACHER_VALIDATION/VALIDATED_BY_TEACHER), `ai_proposed_score` (nunca afecta ELO), `teacher_score` (oficial), `final_score` = teacher_score, `elo_delta` = (final_score−50)×0.2, `file_hash` (SHA-256 anti-plagio), `mime_type` |
| `audit_group_changes` | Log de reasignaciones de grupo por admin |

---

## Supabase Storage

Archivos de procedimientos (imágenes/PDFs) se guardan en Supabase Storage, bucket `procedimientos` (PRIVADO).

### Flujo de upload (save_procedure_submission)
```
Estudiante sube archivo
  → app.py lee bytes del archivo
  → postgres_repository.save_procedure_submission()
    → supabase_storage.upload_file('procedimientos', path, bytes, mime)
      → Supabase Storage recibe archivo
      → Retorna SOLO el path relativo: "38/alb31/hash.jpg"
    → Guarda en DB: storage_url = path relativo
    → Si upload falla: guarda bytes en image_data (BYTEA) como fallback
    → NUNCA deja ambos (storage_url e image_data) en NULL
```

### Flujo de descarga (mostrar imagen al profesor/estudiante)
```
app.py necesita mostrar imagen
  → repo.resolve_storage_image(storage_url)
    → supabase_storage.get_file('procedimientos', storage_url)
      → extract_path() limpia el path (maneja URLs legacy y paths con bucket)
      → storage.download(clean_path) → bytes
    → st.image(bytes)
  → Si falla → fallback a image_data (BYTEA)
  → Si ambos fallan → st.warning("Imagen no disponible")
```

### extract_path() debe manejar 3 casos
| Entrada | Salida |
|---|---|
| `https://xxx.supabase.co/storage/v1/object/public/procedimientos/38/alb31/hash.jpg` | `38/alb31/hash.jpg` |
| `38/alb31/hash.jpg` | `38/alb31/hash.jpg` |
| `procedimientos/38/alb31/hash.jpg` | `38/alb31/hash.jpg` |

### Variables de entorno requeridas
```
SUPABASE_URL=https://lcgnmdpsjvfqbnzmgjzt.supabase.co
SUPABASE_KEY=sb_publishable_POX4...
```
En Streamlit Cloud van en Settings → Secrets. En local van en `.env`.

### SQLite local
`sqlite_repository.py` tiene un stub `resolve_storage_image()` que retorna `None` — en local los archivos se guardan en disco (`data/uploads/procedures/`) o en BYTEA.

---

## Banco de preguntas

Las preguntas viven en **`items/bank/`** como archivos JSON individuales por curso. El nombre del archivo (sin extensión) = `course_id`.

### Campos requeridos por ítem

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Único en todo el banco (ej. `cd_01`, `geo_15`) |
| `content` | string | Enunciado; usar `$...$` para LaTeX inline |
| `difficulty` | int | Rating ELO inicial del ítem (600–1800 recomendado) |
| `topic` | string | Tema dentro del curso |
| `options` | list[str] | 2 a 4 opciones (soportan LaTeX) |
| `correct_option` | string | Debe coincidir **exactamente** con uno de `options` |

Campos opcionales: `image_url` o `image_path`. Si ambos presentes, `image_url` tiene prioridad.

### Agregar un nuevo curso

1. Crear `items/bank/mi_curso.json` con un array de ítems.
2. Agregar entrada en `_COURSE_BLOCK_MAP` en **ambos** `sqlite_repository.py` y `postgres_repository.py`:
   ```python
   'mi_curso': 'Universidad',  # o 'Colegio' o 'Concursos'
   ```
3. Reiniciar la app.

### Catálogo actual

| Archivo | Curso | Bloque |
|---|---|---|
| `algebra_lineal.json` | Álgebra Lineal | Universidad |
| `calculo_diferencial.json` | Cálculo Diferencial | Universidad |
| `calculo_integral.json` | Cálculo Integral | Universidad |
| `calculo_varias_variables.json` | Cálculo de Varias Variables | Universidad |
| `ecuaciones_diferenciales.json` | Ecuaciones Diferenciales | Universidad |
| `probabilidad.json` | Probabilidad | Universidad |
| `algebra_basica.json` | Álgebra Básica | Colegio |
| `aritmetica_basica.json` | Aritmética Básica | Colegio |
| `trigonometria.json` | Trigonometría | Colegio |
| `geometria.json` | Geometría | Colegio |
| `DIAN.json` | Concurso DIAN — Gestor I | Concursos |
| `SENA.json` | Concurso SENA — Profesional 10 | Concursos |

---

## Integración de IA

Multi-proveedor vía `ai_client.py`. Proveedor detectado por prefijo de API key:

| Prefijo | Proveedor |
|---|---|
| `sk-ant-` | Anthropic |
| `gsk_` | Groq |
| `AIzaSy` | Google Gemini |
| `hf_` | HuggingFace |
| `sk-proj-` / `sk-` | OpenAI |
| (ninguno) | LM Studio / Ollama local |

Todas las funciones de IA **degradan con gracia** si no están disponibles (fallback a valores neutros).

**Validación socrática** (`validate_socratic_response()`): post-generación verifica que la respuesta no revele la respuesta y tenga ≤3 oraciones. `SOCRATIC_MAX_TOKENS = 120`.

**Revisión de procedimientos** (`math_procedure_review.py`): solo Groq, usa `meta-llama/llama-4-scout-17b-16e-instruct`. Retorna JSON con evaluación por pasos y `score_procedimiento` (0–100). Ajuste ELO: `(score − 50) × 0.2`. Aplicado una vez por ítem (flag `proc_elo_applied_{item_id}`). El `ai_proposed_score` **nunca** afecta el ELO directamente — solo `teacher_score` lo hace.

---

## Seguridad

- **Argon2id** (via `passlib[argon2]`) para todas las contraseñas.
- Migración transparente desde SHA-256 legacy: reemplazada en el siguiente login.
- Cuentas con hash vacío/null se auto-desactivan en migración de DB.
- API keys solo en `st.session_state` — nunca persistidas en DB.
- Credenciales de admin solo vía env vars (`ADMIN_PASSWORD`, `ADMIN_USER`).

---

## Roles de usuario

- **student**: Debe pertenecer a un grupo. Práctica + estadísticas personales + envío de procedimientos + centro de feedback (con badge de no leídos).
- **teacher**: Requiere aprobación del admin. Crea/gestiona grupos (nombres únicos por docente). Dashboard con filtros cascada (Grupo → Nivel → Materia). Revisa y puntúa procedimientos (badge muestra pendientes). Genera análisis pedagógico con IA por estudiante.
- **admin**: Aprueba docentes, reasigna estudiantes entre grupos (auditado), elimina grupos, activa/desactiva usuarios. Todas las acciones destructivas requieren confirmación en la UI.

---

## Usuarios de prueba

| Usuario | Contraseña | Nivel |
|---|---|---|
| `profesor1` | `demo1234` | Docente (pre-aprobado) |
| `estudiante1` | `demo1234` | Universidad |
| `estudiante2` | `demo1234` | Colegio |
| `estudiante_colegio_1..3` | `test1234` | Colegio (`is_test_user=1`) |
| `estudiante_universidad_1..2` | `test1234` | Universidad (`is_test_user=1`) |

---

## Notas de implementación críticas

- **Dual DB**: `DATABASE_URL` → PostgreSQL (Supabase); ausente → SQLite local. Ambos repos tienen API pública idéntica.
- **Pool PostgreSQL**: `SimpleConnectionPool(1–5)`. Supabase free tier: NUNCA subir maxconn a más de 5. Nunca `conn.close()` — usar `self.put_connection(conn)`.
- **Advisory locks**: `_migrate_db()` usa `pg_advisory_lock(12345)` para evitar deadlocks cuando Streamlit ejecuta múltiples instancias en paralelo.
- **PostgreSQL usa `RealDictCursor`**: acceso siempre por `row['column_name']`, nunca `row[0]`. Fechas son objetos `datetime` — envolver con `str()` antes de slicear.
- **`_COURSE_BLOCK_MAP`** existe en ambos repositorios — sincronizar al agregar cursos.
- **`is_test_user=1`**: estos estudiantes están protegidos contra borrado.
- **UI monolítica**: `app.py` es intencionalmente un solo archivo. Todos los paneles comparten estado en `st.session_state` — tener cuidado con cambios.
- **ELO del procedimiento**: `ai_proposed_score` nunca afecta directamente el ELO. Solo `teacher_score` (vía `final_score`) lo hace.
- **Supabase Storage**: bucket `procedimientos` es PRIVADO. `upload_file()` retorna solo el path relativo, NUNCA una URL pública. `resolve_storage_image()` descarga bytes para `st.image()`. Si el Storage falla, `image_data` (BYTEA) es el fallback.
- **Streamlit Cloud**: usa `DATABASE_URL` apuntando a Supabase. SQLite solo para desarrollo local. Los secrets (`DATABASE_URL`, `ADMIN_PASSWORD`, `SUPABASE_URL`, `SUPABASE_KEY`) van en Settings → Secrets.
