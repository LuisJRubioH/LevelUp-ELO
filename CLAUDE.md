# CLAUDE.md — LevelUp-ELO

Instrucciones para Claude Code al trabajar en este repositorio.

---

## Inicio rápido

```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```

Ejecutar siempre desde la **raíz del repo** — `app.py` inyecta el root en `sys.path` usando `sys.path.insert(0, base_path)` ANTES de cualquier import de `src.*`.

Tests y linting están configurados: `pytest tests/unit/`, `black --check --line-length=100 src/ tests/ scripts/`, `flake8 src/ tests/ scripts/ --select=E9,F63,F7,F82`.

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

### Regla #10 — st.markdown con HTML: sin indentación profunda

En Streamlit 1.55+ el parser CommonMark interpreta cualquier línea con 4+ espacios de indentación como bloque de código, no como HTML. Resultado: el tag `<div>` queda invisible y los `<p>` internos aparecen como texto crudo.

**Regla:** cuando `st.markdown` renderiza HTML, construir el string de forma que el tag de apertura (`<div>`, `<p>`, etc.) quede en la posición 0 del string (sin espacios previos).

```python
# MAL — 24 espacios antes de <div → code block → HTML como texto plano
st.markdown(f"""
                        <div style="...">...</div>
                        """, unsafe_allow_html=True)

# BIEN — string de concatenación, <div en posición 0
_html = (
    f'<div style="...">'
    f'<p>contenido</p>'
    f'</div>'
)
st.markdown(_html, unsafe_allow_html=True)
```

### Regla #11 — Streamlit Cloud: `use_container_width` no `width="stretch"`
`st.image()`, `st.button()`, `st.plotly_chart()` y `st.dataframe()` NO aceptan `width="stretch"` en Streamlit < 1.45. Usar siempre `use_container_width=True`.

```python
# MAL
st.image(img, width="stretch")
st.button("OK", width="stretch")

# BIEN
st.image(img, use_container_width=True)
st.button("OK", use_container_width=True)
```

### Regla #12 — PostgresRepository: singleton por proceso
`PostgresRepository` se crea UNA SOLA VEZ por proceso en `app.py` (variable `_REPO_SINGLETON` a nivel de módulo, protegida por `threading.Lock`). Nunca crear una nueva instancia por sesión o por request — cada instancia abre su propio `ThreadedConnectionPool(1, 5)` y Supabase free tier se agota rápido con múltiples pools.

### Regla #13 — CognitiveAnalyzer puede ser None
`StudentService.cognitive_analyzer` es `None` cuando `enable_cognitive_modifier=False` (modo producción). Siempre verificar antes de acceder:

```python
if st.session_state.student_service.cognitive_analyzer is not None:
    st.session_state.student_service.cognitive_analyzer.model_name = ...
```

### Regla #14 — imports en funciones `_backfill_*` y similares
Los imports locales dentro de funciones de migración/backfill deben estar DENTRO de la función, no a nivel de módulo. Ejemplo correcto en `_backfill_prob_failure()`:

```python
def _backfill_prob_failure(self):
    from src.domain.elo.model import expected_score  # import local aquí
    conn = self.get_connection()
    ...
```

---

## Skills disponibles

Consultar la skill correspondiente **antes de empezar** cuando la tarea entre en alguna de estas categorías:

| Tarea | Skill a consultar |
|---|---|
| Modificar repositorios, tablas, migraciones, seeds, queries | `.claude/skills/db-dual-backend.md` |
| Agregar servicios, modificar domain/app/infra, crear módulos | `.claude/skills/clean-architecture.md` |
| Crear o editar ítems, agregar cursos, modificar banco de preguntas | `.claude/skills/items-bank.md` |
| Después de modificar cualquier repositorio | `.claude/skills/db-sync-checker.md` + `python scripts/db_sync_check.py` |

### Plan V1.0 — Skills por sprint

**OBLIGATORIO**: Antes de implementar cualquier tarea del Plan V1.0, leer el skill del sprint correspondiente **completo** antes de escribir una sola línea de código.

| Sprint | Tarea | Skill — LEER ANTES DE EMPEZAR |
|---|---|---|
| Sprint 1 | Fix encoding banco, logging carga JSON, validate_bank.py | `.claude/skills/v1-sprint1-bank-integrity.md` |
| Sprint 2 | Eliminar importlib.reload, feature flag CognitiveAnalyzer, transacciones atómicas, Protocol interfaces, zdp_interval, requirements | `.claude/skills/v1-sprint2-technical-debt.md` |
| Sprint 3 | logging_config.py, reemplazar except silenciosos, feedback diferenciado usuario | `.claude/skills/v1-sprint3-logging-errors.md` |
| Sprint 4 | Modularizar app.py en vistas, state.py, assets.py, timers.py | `.claude/skills/v1-sprint4-modularization.md` |
| Sprint 5 | Tests unitarios dominio ELO, selector, student_service, banco, integración SQLite | `.claude/skills/v1-sprint5-testing.md` |
| Sprint 6 | pre-commit hooks, GitHub Actions CI, __version__.py, CHANGELOG.md, tag v1.0.0 | `.claude/skills/v1-sprint6-cicd.md` |

**Regla de los sprints**: implementar en orden (1 → 2 → 3 → 4 → 5 → 6). Cada sprint tiene un checklist de completitud al final del skill — no pasar al siguiente hasta que todos los ítems estén marcados.

---

## Arquitectura

Clean Architecture con cuatro capas dentro de `src/`:

- **`domain/`** — Lógica de negocio pura, sin dependencias externas.
  - `elo/model.py` — Factor K dinámico, ELO clásico, dataclasses `Item`/`StudentELO`.
  - `elo/vector_elo.py` — `VectorRating`: ELO + Rating Deviation (RD) por tópico.
  - `elo/uncertainty.py` — `RatingModel` (Glicko-simplificado): RD inicial=350, mín=30, decay=RD×0.95 por intento.
  - `elo/cognitive.py` — `CognitiveAnalyzer`: clasifica respuestas del estudiante vía IA. **Nota:** `impact_modifier` está fijado en 1.0 en `student_service.py` — el análisis cognitivo por texto/tiempo fue desactivado porque causaba discrepancias entre el preview de puntos y el resultado real para el estudiante.
  - `elo/zdp.py` — Cálculo del intervalo ZDP.
  - `selector/item_selector.py` — `AdaptiveItemSelector`: selección por Fisher Information.
  - `katia/katia_messages.py` — Bancos de mensajes de KatIA (tutora socrática gata cyborg). Funciones: `get_random_message()`, `get_procedure_comment(score)`, `get_streak_message(streak)`. Mensajes por rango: 0–59 (tutoría), 60–90 (buen trabajo), 91–100 (excelente). Rachas: 5, 10, 20. Bienvenida, fin de módulo, fin de curso.

- **`application/services/`** — Orquestadores de casos de uso:
  - `student_service.py` — `process_answer()`, `get_next_question()`, `get_socratic_help()`.
  - `teacher_service.py` — Análisis del dashboard y reportes con IA.

- **`infrastructure/`**
  - `persistence/sqlite_repository.py` — SQLite: esquema, migraciones, seed, queries (~1200 líneas). Fallback local.
  - `persistence/postgres_repository.py` — PostgreSQL (psycopg2): port completo de SQLite para producción (Supabase). Pool `SimpleConnectionPool(1–5)`, `RealDictCursor`, `ON CONFLICT DO NOTHING`, `SERIAL PRIMARY KEY`, `BYTEA`.
  - `persistence/seed_test_students.py` — Seed idempotente de 7 estudiantes de prueba (3 colegio, 2 universidad, 2 semillero).
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

- **`interface/streamlit/app.py`** — UI monolítica: login (con wizard de registro multi-paso), panel estudiante, dashboard docente, panel admin. GIFs animados de KatIA para revisión de procedimientos. Temporizadores en tiempo real (JavaScript vía `st.components.v1.html`): sesión global + por pregunta. Exportación CSV/XLSX de datos de estudiantes para el docente. Banners pixel art por materia en tarjetas de curso (`Banners/`). Registro de interacciones con KatIA en DB + visualización en dashboard docente.

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
- **CognitiveAnalyzer**: clasifica confianza [0,1] y tipo de error (`conceptual`/`superficial`). **Desactivado en la práctica**: `student_service.py` pasa `impact_modifier=1.0` siempre, porque el modificador variable causaba discrepancias entre el preview de puntos y el resultado real.
- **ELO del ítem**: los ítems tienen su propio rating de dificultad que se actualiza simétricamente (el ítem "pierde" cuando el estudiante gana).
- **Ranking de 16 niveles**: Aspirante (0–399) → Leyenda Suprema (2500+).
- **Racha de estudio por materia**: `get_study_streak(user_id, course_id=None)` — con `course_id` filtra solo los intentos de ese curso (JOIN con `items`); sin `course_id` es global. En la sala de estudio se pasa `selected_course_id`; en la página de Estadísticas es global. Caché independiente por curso: `cache_streak_{course_id}`.

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
- PostgreSQL: `pg_try_advisory_lock` (no-bloqueante) en `_migrate_db()` (lock 12345), `_seed_admin()` (12346), `_seed_demo_data()` (12347), `sync_items_from_bank_folder()` (12348) y `_seed_test_students()` (12349). Si otra instancia ya tiene el lock, la actual retorna inmediatamente sin bloquear. Lock liberado con `pg_advisory_unlock()` en `finally`. **No usar** `pg_advisory_lock` (bloqueante) ni `pg_advisory_xact_lock` — causan `QueryCanceled` por `statement_timeout`.
- Admin solo se crea si la env var `ADMIN_PASSWORD` está seteada (`ADMIN_USER` default `"admin"`). Sin credenciales hardcodeadas.

### Tablas principales

| Tabla | Detalles clave |
|---|---|
| `users` | `role` (student/teacher/admin), `approved`, `active`, `group_id`, `education_level`, `grade` (solo semillero: '6'–'11'), `is_test_user` (protege contra borrado), `rating_deviation` |
| `groups` | Índice único en `(teacher_id, name_normalized)` — sin nombres duplicados por docente. `invite_code` TEXT (único, generado por docente para acceso inter-nivel) |
| `items` | `difficulty`, `rating_deviation`, `image_url` (opcional), `tags` (JSON array: taxonomía cognitiva/general/específica) |
| `attempts` | `elo_after`, `prob_failure`, `expected_score`, `time_taken`, `confidence_score`, `error_type`, `rating_deviation` |
| `courses` | `id` (slug), `name`, `block` (Universidad/Colegio/Concursos/Semillero) |
| `enrollments` | `user_id`, `course_id`, `group_id` |
| `procedure_submissions` | `image_data` (BLOB/BYTEA fallback), `storage_url` (path en Supabase Storage, ej: `38/alb31/hash.jpg`), `procedure_image_path` (ruta local legacy), `status` (pending/reviewed/PENDING_TEACHER_VALIDATION/VALIDATED_BY_TEACHER), `ai_proposed_score` (nunca afecta ELO), `teacher_score` (oficial), `final_score` = teacher_score, `elo_delta` = (final_score−50)×0.2, `file_hash` (SHA-256 anti-plagio), `mime_type` |
| `problem_reports` | `user_id` FK, `description` TEXT, `status` (`pending`/`resolved`), `created_at`. Métodos: `save_problem_report()`, `get_problem_reports(status=None)`, `mark_problem_resolved()` |
| `katia_interactions` | `user_id`, `course_id`, `item_id`, `item_topic`, `student_message`, `katia_response`, `created_at`. Registro de interacciones del estudiante con el chat socrático de KatIA. Métodos: `save_katia_interaction()`, `get_katia_interactions()`, `export_teacher_katia_interactions()` |
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
   'mi_curso': 'Universidad',  # o 'Colegio', 'Concursos' o 'Semillero'
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
| `semillero/algebra_semillero_6..11.json` | Álgebra Semillero 6°–11° | Semillero |
| `semillero/aritmetica_semillero_6..9,10,11.json` | Aritmética Semillero 6°–11° (incluye `aritmetica_semillero_9.json` creado en integración 2026) | Semillero |
| `semillero/geometria_semillero_6..11.json` | Geometría Semillero 6°–11° | Semillero |
| `semillero/logica_semillero_6..11.json` | Lógica Semillero 6°–11° | Semillero |
| `semillero/conteo_combinatoria_semillero_6..11.json` | Conteo y Combinatoria Semillero 6°–11° | Semillero |
| `semillero/probabilidad_semillero_6..11.json` | Probabilidad Semillero 6°–11° | Semillero |

**Semillero**: los JSONs están en `items/bank/semillero/` separados por grado (ej. `geometria_semillero_8.json`). `sync_items_from_bank_folder()` escanea automáticamente ese subdirectorio además de `items/bank/*.json`.

### Figuras de Semillero

Las figuras geométricas de las Olimpiadas UdeA están en `items/images/` (86 PNGs):
- **UdeA 2020** (33 PNGs): Taller Primaria, Séptimo, Octavo, Noveno, Décimo, Undécimo. Extraídos con `page.get_image_rects()` de PyMuPDF — **no** regenerar con matplotlib.
- **UdeA 2012–2014 Octavo/Noveno** (22 PNGs): Octavo/Noveno Geometría y Lógica. Generados con matplotlib por `octavo_geometria.py` / `octavo_logica.py` / `noveno_geometria.py` / `noveno_logica.py` en `Semillero/para poblar/2012, 2013 y 2014/octavo y noveno/`. Nombres: `Octavo_Geometria_2012_F1_Q4.png`, etc.
- **UdeA 2012–2014 Sexto/Séptimo** (31 PNGs): Sexto/Séptimo Geometría y Lógica, más Taller2014 Nivel1. Generados con matplotlib por los scripts `.py` en `Semillero/para poblar/2012, 2013 y 2014/sexto y septimo/`. Nombres: `Sexto_Geometria_2013_F1_Q9.png`, `Septimo_Logica_2013_F1_Q6.png`, etc.

- **PDFs originales**: `Semillero/OLIMPIADAS-2020/`
- **Script de extracción**: `scripts/extract_figures_from_pdfs.py`
- **Ejecutar**: `venv/Scripts/python.exe scripts/extract_figures_from_pdfs.py` (desde la raíz del repo)
- Las coordenadas del script se obtuvieron de `get_image_rects()` — son las posiciones exactas de cada imagen embebida en el PDF, no estimaciones manuales.

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

**Revisión de procedimientos** (`math_procedure_review.py`): solo Groq, usa `meta-llama/llama-4-scout-17b-16e-instruct`. Retorna JSON con evaluación por pasos y `score_procedimiento` (0–100). Ajuste ELO: `(score − 50) × 0.2`. Aplicado una vez por ítem (flag `proc_elo_applied_{item_id}`). El `ai_proposed_score` **nunca** afecta el ELO directamente — solo `teacher_score` lo hace. `_parse_json_response()` incluye fallback para escapar backslashes LaTeX no válidos en JSON (`\frac`, `\sin`, etc.) que el LLM genera sin escapar.

---

## KatIA — Tutora Socrática

KatIA es una gata cyborg que actúa como tutora socrática del estudiante. Tiene personalidad persistente con mensajes predefinidos (no generados por IA) y GIFs animados.

### Assets (`KatIA/`)
- `katIA.png` — Avatar estático (6.5MB, cacheado con `@st.cache_resource`).
- `correcto.gif` / `correcto_compressed.gif` — GIF animado de KatIA escribiendo (2.3MB → 698KB comprimido). Se usa como animación de "revisando" durante el análisis y como resultado cuando score >= 91.
- `errores.gif` / `errores_compressed.gif` — GIF animado de KatIA con expresión de errores (69MB → 1.8MB comprimido). Se muestra cuando score < 91.
- `instrucciones_katia.md` — Manual completo con bancos de mensajes por rango de score.

### Mensajes (`src/domain/katia/katia_messages.py`)
- `get_procedure_comment(score)`: score >= 91 → `RESPUESTAS_ALTA`, 60–90 → `RESPUESTAS_MEDIA`, < 60 → `RESPUESTAS_TUTORIA`.
- `get_streak_message(streak)`: 5 → `FELICITACIONES_RACHA_5`, 10 → `RACHA_10`, 20 → `RACHA_20`.
- `MENSAJES_BIENVENIDA`: saludo aleatorio al iniciar sesión.
- Los mensajes de tutoría (< 60) invitan al estudiante a usar el chat socrático.

### Flujo de GIFs en revisión de procedimientos
1. Estudiante sube procedimiento y presiona "Analizar"
2. → Aparece `correcto_compressed.gif` como animación de "KatIA está revisando..."
3. → IA analiza (spinner simultáneo)
4. → Se limpia el GIF de revisión
5. → Score >= 91: muestra `correcto_compressed.gif` + mensaje de `RESPUESTAS_ALTA`
6. → Score < 91: muestra `errores_compressed.gif` + mensaje de `RESPUESTAS_TUTORIA` o `RESPUESTAS_MEDIA` + diagnóstico del LLM

**Importante**: la app usa los GIFs **comprimidos** (`*_compressed.gif`), no los originales. Los originales se conservan como fuente de alta calidad.

---

## Seguridad

- **Argon2id** (via `passlib[argon2]`) para todas las contraseñas.
- Migración transparente desde SHA-256 legacy: reemplazada en el siguiente login.
- Cuentas con hash vacío/null se auto-desactivan en migración de DB.
- API keys solo en `st.session_state` — nunca persistidas en DB.
- Credenciales de admin solo vía env vars (`ADMIN_PASSWORD`, `ADMIN_USER`).

---

## Roles de usuario

- **student**: Debe pertenecer a un grupo. Práctica + estadísticas personales + envío de procedimientos con GIFs animados de KatIA + centro de feedback (con badge de no leídos) + formulario de reporte de problemas técnicos (expander en sidebar). Matrícula en 3 tabs: Explorar, Mis matrículas, Código de acceso (inter-nivel). Racha de estudio independiente por materia. Temporizadores en tiempo real: sesión global (sidebar) + por pregunta (sobre la pregunta, grande y visible).
- **teacher**: Requiere aprobación del admin. Crea/gestiona grupos (nombres únicos por docente). Genera **códigos de invitación** por grupo para acceso inter-nivel. Dashboard con filtros cascada (Grupo → Nivel → Materia). Revisa y puntúa procedimientos (badge muestra pendientes). Genera análisis pedagógico con IA por estudiante. **Exportación CSV/XLSX** de datos completos de estudiantes (intentos con `time_taken` y RD, matrículas, procedimientos) para análisis estadístico posterior.
- **admin**: Aprueba docentes, reasigna estudiantes entre grupos (auditado), elimina grupos, activa/desactiva usuarios. Notificaciones de problemas técnicos al inicio del panel (sección `🔔 Problemas Técnicos` con botón "Resuelto" por reporte). Todas las acciones destructivas requieren confirmación en la UI.

---

## Usuarios de prueba

| Usuario | Contraseña | Nivel |
|---|---|---|
| `profesor1` | `demo1234` | Docente (pre-aprobado) |
| `estudiante1` | `demo1234` | Universidad |
| `estudiante2` | `demo1234` | Colegio |
| `estudiante_colegio_1..3` | `test1234` | Colegio (`is_test_user=1`) |
| `estudiante_universidad_1..2` | `test1234` | Universidad (`is_test_user=1`) |
| `estudiante_semillero_1` | `test1234` | Semillero grado 9 (`is_test_user=1`) |
| `estudiante_semillero_2` | `test1234` | Semillero grado 11 (`is_test_user=1`) |

---

## Notas de implementación críticas

- **Dual DB**: `DATABASE_URL` → PostgreSQL (Supabase); ausente → SQLite local. Ambos repos tienen API pública idéntica.
- **Pool PostgreSQL**: `SimpleConnectionPool(1–5)`. Supabase free tier: NUNCA subir maxconn a más de 5. Nunca `conn.close()` — usar `self.put_connection(conn)`.
- **Advisory locks**: todas las funciones de seed/migración usan `pg_try_advisory_lock(N)` (no-bloqueante) con IDs 12345–12349. Si no obtiene el lock, retorna sin hacer nada. Lock liberado siempre en `finally` con `pg_advisory_unlock(N)`. Nunca usar `pg_advisory_lock` (bloqueante) ni `pg_advisory_xact_lock`.
- **PostgreSQL usa `RealDictCursor`**: acceso siempre por `row['column_name']`, nunca `row[0]`. Fechas son objetos `datetime` — envolver con `str()` antes de slicear.
- **`_COURSE_BLOCK_MAP`** existe en ambos repositorios — sincronizar al agregar cursos.
- **`is_test_user=1`**: estos estudiantes están protegidos contra borrado.
- **UI monolítica**: `app.py` es intencionalmente un solo archivo. Todos los paneles comparten estado en `st.session_state` — tener cuidado con cambios.
- **ELO del procedimiento**: `ai_proposed_score` nunca afecta directamente el ELO. Solo `teacher_score` (vía `final_score`) lo hace.
- **Supabase Storage**: bucket `procedimientos` es PRIVADO. `upload_file()` retorna solo el path relativo, NUNCA una URL pública. `resolve_storage_image()` descarga bytes para `st.image()`. Si el Storage falla, `image_data` (BYTEA) es el fallback.
- **Streamlit Cloud**: usa `DATABASE_URL` apuntando a Supabase. SQLite solo para desarrollo local. Los secrets (`DATABASE_URL`, `ADMIN_PASSWORD`, `SUPABASE_URL`, `SUPABASE_KEY`) van en Settings → Secrets.
- **Racha por materia**: en la sala de estudio `get_study_streak(user_id, selected_course_id)` filtra por curso. En Estadísticas es global (`course_id=None`). Cache key: `cache_streak_{course_id}` (invalidar al guardar intento). Nunca pasar `course_id` en la llamada de Estadísticas.
- **Estrellas de dificultad**: `get_difficulty_label(d)` retorna `(n_filled: int, label: str)`. HTML: `★`×n_filled en `#FFD700` + `★`×(5-n_filled) en `#444`. Thresholds: <750=1, <950=2, <1150=3, <1400=4, ≥1400=5.
- **Problem reports**: tabla `problem_reports` en ambos repos. Formulario en sidebar del estudiante (expander `🔧 Reportar un problema`, mín 10 chars). Sección `🔔 Problemas Técnicos` en admin panel se muestra solo si hay pendientes; no se cachea (lectura directa en cada render).
- **Acceso especial inter-nivel**: un estudiante puede matricularse en un curso de otro nivel **solo** si usa un código de invitación de un docente (Tab 3 de Matrículas). La condición que los distingue de matrículas legacy es `group_id IS NOT NULL`. El filtro `_enrolled` en `app.py` incluye estos cursos aunque su `block` no coincida con `_student_block`. En la UI se marcan con `📌 Acceso especial`. El ranking y el ELO vectorial del estudiante **no** se ven afectados (siguen usando su `education_level` registrado). La exploración libre (Tab 1 Explorar) filtra siempre por nivel — solo el código de invitación puede dar acceso inter-nivel.
- **st.markdown HTML en Streamlit 1.55+**: ver Regla #10. Construir siempre el HTML como string sin indentación previa; nunca usar `f"""` con el tag de apertura indentado.
- **KatIA GIFs animados**: `correcto_compressed.gif` (698KB) y `errores_compressed.gif` (1.8MB) se cargan con `@st.cache_resource` al inicio. Se muestran durante y después de la revisión de procedimientos según el score (≥91 → correcto, <91 → errores). Siempre usar los comprimidos, no los originales (69MB).
- **Wizard de registro**: flujo multi-paso en `app.py`. Paso 1: selección de rol (Estudiante/Profesor). Paso 2: datos de cuenta (usuario, contraseña, nivel, grado). Estado en `st.session_state.reg_step` y `st.session_state.reg_chosen_role`.
- **Códigos de invitación**: `groups.invite_code` (TEXT, único). El docente genera un código desde su panel; el estudiante lo usa en Tab 3 "Código de acceso" de Matrículas para unirse a un grupo de otro nivel. Método: `generate_group_invite_code(group_id)`.
- **Tags de taxonomía**: columna `items.tags` (TEXT, JSON array). Tres dimensiones: cognitiva, general y específica. Se muestran como badges en la UI de la pregunta.
- **impact_modifier desactivado**: `student_service.py` pasa `impact_modifier=1.0` siempre. El `CognitiveAnalyzer` sigue existiendo pero su output no escala el delta ELO. Razón: el preview de puntos que se muestra al estudiante antes de responder no podía predecir el modifier, causando confusión.
- **Temporizadores en tiempo real**: implementados con `st.components.v1.html()` + JavaScript `setInterval(tick, 1000)` para actualización segundo a segundo sin reruns de Streamlit. Timer de sesión en sidebar (gris, compacto) y timer por pregunta sobre el enunciado (1.3rem, dorado, bold). `session_start_time` se setea en login manual y en restauración por cookie. `question_start_time` se resetea al cargar cada pregunta. IDs únicos vía `_TIMER_ID_COUNTER` para evitar colisiones DOM.
- **Exportación CSV/XLSX del docente**: 4 métodos en ambos repos (`export_teacher_student_data()`, `export_teacher_enrollments()`, `export_teacher_procedures()`, `export_teacher_katia_interactions()`). El Excel tiene una hoja por dataset (Intentos, Matrículas, Procedimientos, KatIA). Incluye `time_taken` y `rating_deviation` por intento. Botones en expander "📥 Exportar datos de estudiantes" del panel docente. Dependencia: `openpyxl`.
- **Banners pixel art de cursos**: imágenes PNG en `Banners/` (geometria, aritmetica, logica, conteo_combinatoria, probabilidad, algebra). Se cargan como base64 con `@st.cache_resource` y se muestran en las tarjetas de curso del estudiante. Matching por keyword en el nombre del curso.
- **Registro de interacciones KatIA**: cada pregunta del estudiante al chat socrático se guarda en `katia_interactions` con contexto (curso, ítem, tema). El docente ve un resumen (temas más consultados, historial de conversaciones) en el dashboard por estudiante. Se incluye en la exportación CSV/XLSX.
- **Fallback en procedimientos**: si la revisión de IA falla con `ValueError`/`ConnectionError`, el procedimiento se guarda de todas formas para revisión del docente (sin score de IA).
