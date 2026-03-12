# LevelUp-ELO

Plataforma de **aprendizaje adaptativo** construida con Python y Streamlit que usa el **sistema de rating ELO** (el mismo del ajedrez competitivo) para medir y ajustar en tiempo real el nivel académico de los estudiantes. Cada pregunta respondida actualiza el rating del alumno y el de la pregunta simultáneamente, garantizando que el sistema siempre sirva el reto correcto.

---

## Tabla de contenidos

- [Características principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Estructura de archivos](#estructura-de-archivos)
- [Motor ELO — Detalle técnico](#motor-elo--detalle-técnico)
- [Selector adaptativo ZDP](#selector-adaptativo-zdp)
- [Analizador Cognitivo con IA](#analizador-cognitivo-con-ia)
- [Integración multi-proveedor de IA](#integración-multi-proveedor-de-ia)
  - [Model Router inteligente](#model-router-inteligente-model_routerpy)
  - [Detección automática de capacidades](#detección-automática-de-capacidades-model_capability_detectorpy)
  - [Pipeline de verificación simbólica](#pipeline-de-verificación-simbólica)
- [Base de datos](#base-de-datos)
- [Niveles educativos y catálogo de cursos](#niveles-educativos-y-catálogo-de-cursos)
- [Roles de usuario](#roles-de-usuario)
- [Seguridad](#seguridad)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Configuración de IA en la UI](#configuración-de-ia-en-la-ui)
- [Agregar preguntas](#agregar-preguntas)
- [Dependencias](#dependencias)

---

## Características principales

- **Rating ELO vectorial**: cada estudiante mantiene un ELO independiente por tema (no uno global), lo que permite detectar fortalezas y debilidades con precisión quirúrgica.
- **Factor K dinámico**: el peso de cada respuesta cambia según la experiencia y la estabilidad del estudiante, acelerando la convergencia del rating.
- **Incertidumbre tipo Glicko**: el sistema rastrea un *Rating Deviation* (RD) por tópico. A mayor RD, mayor variación del rating tras cada respuesta; se reduce con la experiencia.
- **Selector ZDP (Zona de Desarrollo Próximo)**: elige la pregunta que maximiza el aprendizaje — ni tan fácil que aburra, ni tan difícil que frustre.
- **Analizador cognitivo**: la IA clasifica la respuesta del alumno (confianza alta/baja, error conceptual vs. superficial) y escala el impacto en el ELO.
- **Tutor socrático con streaming**: guía al estudiante mediante preguntas sin revelar la respuesta.
- **Dashboard docente**: los profesores visualizan ELO por tópico, tasa de error reciente, probabilidad de fallo por pregunta y pueden generar reportes con IA.
- **Soporte multi-proveedor de IA**: Groq, OpenAI, Anthropic Claude, Google Gemini, HuggingFace, LM Studio local, Ollama local — detección automática por prefijo de API key.
- **Model Router inteligente**: selección automática del mejor modelo por tarea (tutor socrático → rápido + razonamiento, análisis de imagen → visión + razonamiento, chat general → modelo del usuario). Registro manual de capacidades + detección heurística automática desde endpoints `/v1/models`.
- **Pipeline de verificación simbólica**: verificación algebraica con SymPy en 4 capas (simplificación → expansión → equivalencia con valor absoluto → fallback numérico), diagnóstico de errores (distributiva incorrecta, error de signo, fracción mal simplificada) y feedback pedagógico socrático por tipo de error.
- **Sin infraestructura externa obligatoria**: funciona completamente offline con LM Studio u Ollama; las funciones de IA degradan con gracia si no hay servidor disponible.
- **Revisión matemática rigurosa de procedimientos**: cuando el proveedor activo es Groq, el sistema analiza imágenes de desarrollos manuscritos con `meta-llama/llama-4-scout-17b-16e-instruct` y devuelve una corrección paso a paso en JSON con un score 0–100 que ajusta el ELO del estudiante de forma secundaria.
- **Soporte PDF en procedimientos**: los estudiantes pueden subir procedimientos en formato PDF además de imágenes; el sistema renderiza la primera página con PyMuPDF para análisis visual.
- **Centro de feedback del estudiante**: los alumnos consultan notas numéricas (IA y docente) y comentarios de cada procedimiento enviado, con badge de notificación para revisiones nuevas.
- **Filtros cascada en dashboard docente**: Grupo → Nivel → Materia, con opciones dinámicas que se actualizan según la selección.
- **Badges de notificación**: el docente ve cuántos procedimientos tiene pendientes de revisar; el estudiante ve cuántas revisiones nuevas tiene sin leer.
- **Anti-plagio SHA-256**: cada archivo subido se hashea y se compara contra envíos previos del mismo estudiante y ejercicio para detectar duplicados.
- **Validación de relevancia de procedimientos**: antes de enviar, la IA verifica que el archivo corresponda al ejercicio actual; tras 3 intentos fallidos se ofrecen opciones alternativas.
- **Racha de estudio**: el sistema calcula días consecutivos de actividad y lo muestra en la sala de estudio y estadísticas.
- **Ranking ELO de 16 niveles**: desde Aspirante (0–399) hasta Leyenda Suprema (2500+), con nombre y rango dinámico según el ELO global.
- **Imágenes en preguntas**: los ítems del banco pueden incluir una URL de imagen que se muestra junto al enunciado.

---

## Arquitectura

El proyecto sigue **Clean Architecture** con cuatro capas bien definidas:

```
src/
├── domain/              # Reglas de negocio puras — sin dependencias externas
│   ├── elo/
│   │   ├── model.py         # Factor K dinámico, ELO clásico, dataclasses Item/StudentELO
│   │   ├── vector_elo.py    # VectorRating: ELO + RD por tópico
│   │   ├── uncertainty.py   # RatingModel (Glicko-simplificado)
│   │   ├── cognitive.py     # CognitiveAnalyzer: clasifica respuestas con IA local
│   │   └── zdp.py           # Cálculo del intervalo ZDP
│   └── selector/
│       └── item_selector.py # AdaptiveItemSelector: selección por Fisher Information
│
├── application/             # Casos de uso — orquestan dominio e infraestructura
│   └── services/
│       ├── student_service.py   # process_answer, get_next_question, get_socratic_help
│       └── teacher_service.py   # análisis y reportes para el panel docente
│
├── infrastructure/          # Implementaciones concretas (detalles técnicos)
│   ├── persistence/
│   │   ├── sqlite_repository.py  # SQLite: esquema, migraciones, seed, queries
│   │   └── seed_test_students.py # Seed idempotente de 5 estudiantes de prueba
│   ├── external_api/
│   │   ├── ai_client.py                 # Cliente universal multi-proveedor de IA
│   │   ├── math_procedure_review.py     # Revisión matemática rigurosa (Groq + Llama 4 Scout)
│   │   ├── model_router.py             # Router inteligente: selección de modelo por tarea
│   │   ├── model_capability_detector.py # Detección automática de capacidades desde nombre
│   │   ├── symbolic_math_verifier.py   # Verificador simbólico con SymPy (4 capas)
│   │   ├── math_step_extractor.py      # Extracción estructurada de pasos matemáticos
│   │   ├── math_ocr.py                 # OCR matemático (pix2tex > tesseract > regex)
│   │   ├── math_reasoning_analyzer.py  # Análisis de razonamiento paso a paso
│   │   ├── pedagogical_feedback.py     # Feedback pedagógico socrático por error
│   │   └── math_analysis_pipeline.py   # Pipeline completo: OCR → pasos → verificación → feedback
│   └── security/
│       └── hashing_service.py    # Argon2id + migración desde SHA-256 legacy
│
└── interface/
    └── streamlit/
        └── app.py           # UI completa: login, paneles de estudiante, docente y admin
```

### Flujo de datos al responder una pregunta

```
app.py
  └─→ StudentService.process_answer()
        ├─→ CognitiveAnalyzer.analyze_cognition()   ← IA local clasifica el razonamiento
        ├─→ VectorRating.update()                   ← aplica ELO delta con impact_modifier
        ├─→ SQLiteRepository.update_item_rating()   ← actualiza dificultad del ítem simétricamente
        └─→ SQLiteRepository.save_attempt()         ← persiste todos los metadatos del intento
```

---

## Estructura de archivos

```
LevelUp-ELO/
├── src/                    # Código fuente (ver árbol de arriba)
├── items/
│   └── bank/               # Banco de preguntas por curso (1 JSON por curso)
│       ├── algebra_lineal.json
│       ├── calculo_diferencial.json
│       ├── calculo_integral.json
│       ├── calculo_varias_variables.json
│       ├── ecuaciones_diferenciales.json
│       ├── probabilidad.json
│       ├── algebra_basica.json
│       ├── aritmetica_basica.json
│       ├── trigonometria.json
│       ├── geometria.json
│       ├── DIAN.json
│       └── SENA.json
├── data/
│   └── elo_database.db     # Base de datos SQLite (generada en el primer arranque)
├── requirements.txt        # Dependencias Python
└── CLAUDE.md               # Instrucciones para Claude Code
```

---

## Motor ELO — Detalle técnico

### ELO clásico

La probabilidad esperada de que el estudiante (rating `R`) resuelva un ítem de dificultad `D` es:

```
P(R, D) = 1 / (1 + 10^((D - R) / 400))
```

El delta de rating tras una respuesta es:

```
Δ = K × (resultado - P) × impact_modifier
```

donde `resultado` es 1.0 (acierto) o 0.0 (fallo), y `impact_modifier` proviene del analizador cognitivo.

### Factor K dinámico (`model.py`)

| Fase | Condición | K |
|---|---|---|
| Inicial | < 30 intentos | **40** — búsqueda rápida del nivel real |
| Crecimiento | rating < 1400 | **32** — convergencia estable en niveles bajos |
| Estabilidad | error medio < 15 % en últimas 20 respuestas | **16** — protege ratings maduros |
| Base | cualquier otro caso | **24** |

### Rating Deviation — Incertidumbre tipo Glicko (`uncertainty.py`)

Cada tópico tiene asociado un `RD` (Rating Deviation). El sistema usa un `RatingModel` con:

- **RD inicial**: 350 (máxima incertidumbre)
- **RD mínimo**: 30 (estabilidad máxima)
- **Decaimiento**: `RD_nuevo = max(30, RD × 0.95)` por cada intento
- **Escala de impacto**: `K_efectiva = K_BASE × (RD / RD_BASE)`, lo que amplifica los cambios cuando el sistema aún no conoce bien al estudiante

### ELO simétrico de los ítems

Cuando el estudiante gana, la dificultad del ítem baja (el ítem "perdió"). Cuando el estudiante falla, la dificultad sube. Esto calibra automáticamente el banco de preguntas con el tiempo.

### Vector ELO (`vector_elo.py`)

```python
vector_rating.update(topic, difficulty, result, impact_modifier)
# → actualiza (rating, RD) del tópico de forma independiente

aggregate_global_elo(vector)
# → promedio de todos los ratings por tópico → ELO global para mostrar
```

---

## Selector adaptativo ZDP

`AdaptiveItemSelector` implementa la **Zona de Desarrollo Próximo** de Vygotsky en términos matemáticos:

1. **Probabilidad óptima**: selecciona ítems donde `0.4 ≤ P ≤ 0.75`
   - `P > 0.75` → demasiado fácil (aburrimiento)
   - `P < 0.4` → demasiado difícil (frustración)

2. **Fisher Information**: entre los candidatos válidos, elige el que maximiza `I(P) = P × (1 − P)`, que es máximo en P = 0.5. Esto garantiza que el rating converja más rápido.

3. **Expansión progresiva**: si no hay candidatos en el rango inicial, el intervalo se relaja ±0.05 por paso (hasta 10 pasos) hasta encontrar al menos un ítem. Como último recurso, evalúa todo el banco.

4. **Priorización de novedades**:
   - Preguntas nunca vistas (máxima prioridad)
   - Preguntas falladas en sesión con cooldown de ≥ 3 preguntas
   - Preguntas del historial de sesiones anteriores

---

## Analizador Cognitivo con IA

`CognitiveAnalyzer` (`domain/elo/cognitive.py`) llama a la IA local para enriquecer el impacto de cada respuesta. El resultado modifica el delta ELO mediante `impact_modifier ∈ [0.5, 1.5]`.

### Componentes del modificador

| Factor | Cálculo | Efecto |
|---|---|---|
| Confianza (IA) | `0.8 + confianza × 0.4` → [0.8, 1.2] | Alta confianza amplifica el cambio |
| Tipo de error (IA) | Superficial: 0.7 / Conceptual: 1.2 | Descuido penaliza menos que ignorancia |
| Velocidad de respuesta | Acierto <5s: 1.2 / >30s: 0.8 / Fallo <3s: 0.7 | Maestría vs. duda vs. click accidental |

El modificador final es el **producto** de los tres factores, recortado al intervalo [0.5, 1.5].

### Prompt a la IA (resumen)

La IA recibe el texto de razonamiento del alumno y devuelve JSON:

```json
{"confidence": 0.85, "error_type": "superficial", "explanation": "El alumno domina el concepto pero cometió un error aritmético."}
```

Si la IA no está disponible, el sistema cae back a valores neutros (`confidence: 0.5`, `impact_modifier: 1.0`) sin interrumpir la sesión.

---

## Integración multi-proveedor de IA

`ai_client.py` expone un cliente universal con soporte para 7 proveedores:

| Proveedor | Modelo cognitivo (rápido) | Modelo análisis (potente) | Tipo |
|---|---|---|---|
| **Groq** | `llama-3.1-8b-instant` | `llama-3.3-70b-versatile` | Cloud |
| **OpenAI** | `gpt-4o-mini` | `gpt-4o` | Cloud |
| **Anthropic** | `claude-haiku-4-5-20251001` | `claude-sonnet-4-6` | Cloud (SDK nativo) |
| **Google Gemini** | `gemini-2.0-flash` | `gemini-2.0-flash` | Cloud (OpenAI-compat.) |
| **HuggingFace** | `meta-llama/Llama-3.1-8B-Instruct` | `meta-llama/Llama-3.3-70B-Instruct` | Cloud |
| **LM Studio** | Detectado automáticamente | Detectado automáticamente | Local |
| **Ollama** | Detectado automáticamente | Detectado automáticamente | Local |

### Detección automática de proveedor

El proveedor se infiere del prefijo de la API key ingresada en la sidebar:

| Prefijo | Proveedor |
|---|---|
| `sk-ant-` | Anthropic |
| `gsk_` | Groq |
| `AIzaSy` | Google Gemini |
| `hf_` | HuggingFace |
| `sk-proj-` / `sk-` | OpenAI |
| (sin key) | LM Studio / Ollama local |

### Funciones de IA

- **`get_socratic_guidance()`** / **`get_socratic_guidance_stream()`**: tutor socrático que guía al alumno con preguntas sin revelar la respuesta. Soporta streaming token a token.
- **`get_pedagogical_analysis()`**: análisis profundo del desempeño de un estudiante para el docente.
- **`analyze_performance_local()`**: genera 3 recomendaciones en JSON para el dashboard de estadísticas del alumno.
- **`analyze_procedure_image()`**: revisión visual genérica de procedimientos usando el modelo activo (para OpenAI, Anthropic, Gemini y modelos locales con visión).
- **`validate_procedure_relevance()`**: verificación ligera (SÍ/NO) de que el archivo subido corresponde al ejercicio actual.
- **`select_best_math_model()`**: selecciona el mejor modelo disponible para razonamiento matemático entre los cargados en servidores locales.

### Revisión matemática rigurosa (`math_procedure_review.py`)

Servicio dedicado que se activa automáticamente cuando el proveedor es **Groq**. Usa el modelo de visión `meta-llama/llama-4-scout-17b-16e-instruct` con temperatura 0.1 y fuerza respuesta en JSON estricto.

**Flujo:**
1. La imagen del procedimiento se envía en base64 a `https://api.groq.com/openai/v1`.
2. El modelo transcribe el contenido, evalúa cada paso y asigna un `score_procedimiento` (0–100).
3. En caso de JSON inválido, se reintenta una vez; si falla de nuevo, se lanza un `ValueError` controlado.
4. El score ajusta el ELO del estudiante en el tópico activo como factor secundario:

```
ELO_final = ELO_base + (score_procedimiento − 50) × 0.2
```

Ejemplos de ajuste: score 100 → +10 ELO · score 50 → 0 · score 0 → −10 ELO.

**JSON de respuesta:**

```json
{
  "transcripcion": "...",
  "pasos": [
    { "numero": 1, "contenido": "...", "evaluacion": "Valido | Algebraicamente incorrecto | Conceptualmente incorrecto | Incompleto", "comentario": "..." }
  ],
  "errores_detectados": [],
  "saltos_logicos": [],
  "resultado_correcto": true,
  "evaluacion_global": "...",
  "score_procedimiento": 85
}
```

El ajuste ELO se aplica una sola vez por ejercicio (flag de sesión `proc_elo_applied_{item_id}`) y se muestra al alumno junto con el detalle de la revisión en la interfaz.

### Model Router inteligente (`model_router.py`)

Selecciona automáticamente el mejor modelo disponible según el tipo de tarea, eliminando la necesidad de usar un solo modelo para todo.

**Tareas soportadas:**

| Tarea | Requisitos | Prioridad |
|---|---|---|
| `tutor_socratic` | Razonamiento + velocidad rápida | Excluye modelos lentos; prioriza `fast` + `reasoning` |
| `image_procedure_analysis` | Visión + razonamiento | Retorna `None` si no hay modelo con visión |
| `general_chat` | Texto | Usa el modelo seleccionado por el usuario |

**Fuentes de capacidades (en orden de prioridad):**
1. Registro manual (`_MODEL_REGISTRY`) — modelos cloud conocidos (GPT-4o, Claude, Llama, etc.)
2. Valores por defecto del proveedor — cada proveedor tiene capacidades típicas
3. Detección heurística automática — análisis del nombre del modelo

**Validación socrática:** `validate_socratic_response()` verifica post-generación que la respuesta no revele la solución directa (detecta patrones como "la respuesta es", "la solución es", etc.) y que sea concisa (≤ 3 oraciones). Límite de tokens: `SOCRATIC_MAX_TOKENS = 120`.

### Detección automática de capacidades (`model_capability_detector.py`)

Infiere visión, razonamiento y velocidad a partir del nombre del modelo mediante heurísticas:

- **Visión**: detecta keywords como `vision`, `vl`, `llava`, `gpt-4o`, `gemma-3`, `llama-4`, `pixtral`, `moondream`, `fuyu`, etc.
- **Razonamiento**: detecta `math`, `instruct`, `reason`, `-r1`, `deepseek`, `qwen`, `gpt-4`, `phi-3`, `claude`, etc.
- **Velocidad**: `≤9B → fast`, `≤14B → medium`, `>14B/MoE/mixtral/70b → slow`

`detect_all_capabilities(base_url)` consulta `GET /v1/models` y retorna las capacidades de todos los modelos disponibles en servidores OpenAI-compatibles (LM Studio, Ollama).

### Pipeline de verificación simbólica

Cadena de 4 módulos que complementa el análisis LLM con verificación algebraica formal:

```
OCR (math_ocr.py) → Extracción de pasos (math_step_extractor.py)
    → Verificación simbólica (symbolic_math_verifier.py)
        → Feedback pedagógico (pedagogical_feedback.py)
```

**Verificador simbólico (`symbolic_math_verifier.py`)** — Verificación en 4 capas:

1. `simplify(e1 - e2) == 0` — equivalencia algebraica directa
2. `expand(e1 - e2) == 0` — equivalencia tras expansión
3. Equivalencia con valor absoluto — acepta `sqrt(x²) = x` en contexto escolar (variables positivas)
4. Verificación numérica — sustituye valores de prueba (`x=2, 3, -2`) como fallback

Diagnóstico de errores: `incorrect_distributive`, `sign_error`, `fraction_simplification`, `not_equivalent`. Soporte para ecuaciones (verifica múltiplos escalares: `3x=9 ↔ x=3`).

Optimizaciones: `@lru_cache(maxsize=256)` en `simplify` y `expand`; limpieza LaTeX→SymPy con 18 patrones de reemplazo; SymPy como dependencia opcional (degrada con gracia).

**Extractor de pasos (`math_step_extractor.py`)** — Detecta separadores naturales (saltos de línea, flechas `→/⇒`, numeración `1.`, prefijos `Paso N`) y clasifica cada paso en: `equation`, `simplification`, `substitution`, `factoring`, `derivative`, `integral`, `limit`, `definition`.

**Feedback pedagógico (`pedagogical_feedback.py`)** — Genera pistas socráticas rotativas según el tipo de error detectado, sin revelar la respuesta.

**Pipeline completo (`math_analysis_pipeline.py`)** — Orquesta los 4 módulos con fallback independiente por etapa. Se invoca automáticamente tras la revisión LLM de procedimientos en la UI.

---

## Base de datos

SQLite (archivo `data/elo_database.db`, ruta fija). Se crea y migra automáticamente en cada arranque. La carpeta `data/` se genera si no existe. La ruta se puede sobreescribir con la variable de entorno `DB_PATH`.

### Esquema principal

**`users`**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER PK | Identificador |
| `username` | TEXT UNIQUE | Nombre de usuario |
| `password_hash` | TEXT | Hash Argon2id |
| `role` | TEXT | `student` / `teacher` / `admin` |
| `approved` | INTEGER | 0 = pendiente de aprobación (docentes) |
| `active` | INTEGER | 0 = desactivado por admin |
| `group_id` | INTEGER FK | Grupo asignado (estudiantes) |
| `education_level` | TEXT | `universidad` / `colegio` / `concursos` |
| `is_test_user` | INTEGER | 1 = estudiante de prueba (protegido contra eliminación) |
| `rating_deviation` | REAL | RD global (promedio de tópicos) |

**`groups`**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER PK | Identificador |
| `name` | TEXT | Nombre del grupo |
| `teacher_id` | INTEGER FK | Docente propietario |
| `course_id` | TEXT FK | Curso vinculado (catálogo) |
| `name_normalized` | TEXT | Nombre en minúsculas para unicidad |

Restricción: **índice único** en `(teacher_id, name_normalized)` — un profesor no puede crear dos grupos con el mismo nombre (case-insensitive).

**`items`**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | TEXT PK | ID único (ej. `q1`) |
| `topic` | TEXT | Tema |
| `content` | TEXT | Enunciado (soporta LaTeX) |
| `options` | TEXT | JSON array de opciones |
| `correct_option` | TEXT | Opción correcta exacta |
| `difficulty` | REAL | Rating ELO del ítem |
| `rating_deviation` | REAL | Incertidumbre del ítem |
| `image_url` | TEXT | URL de imagen complementaria (opcional) |

**`attempts`**
| Campo | Tipo | Descripción |
|---|---|---|
| `user_id` | INTEGER FK | Alumno |
| `item_id` | TEXT | Pregunta |
| `is_correct` | BOOLEAN | Resultado |
| `elo_after` | REAL | Rating del alumno post-respuesta |
| `prob_failure` | REAL | `1 − P(éxito)` calculada antes de responder |
| `expected_score` | REAL | `P(éxito)` según ELO |
| `time_taken` | REAL | Segundos en responder |
| `confidence_score` | REAL | Confianza detectada por IA [0, 1] |
| `error_type` | TEXT | `conceptual` / `superficial` / `none` |
| `rating_deviation` | REAL | RD del alumno en ese tópico tras el intento |

**`courses`**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | TEXT PK | Slug del archivo JSON (ej. `calculo_diferencial`) |
| `name` | TEXT | Nombre legible del curso |
| `block` | TEXT | `Universidad` / `Colegio` / `Concursos` |
| `description` | TEXT | Descripción del curso |

**`enrollments`**
| Campo | Tipo | Descripción |
|---|---|---|
| `user_id` | INTEGER FK | Estudiante |
| `course_id` | TEXT FK | Curso matriculado |
| `group_id` | INTEGER FK | Grupo asociado a la matrícula |

**`procedure_submissions`**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER PK | Identificador |
| `student_id` | INTEGER FK | Estudiante que envía |
| `item_id` | TEXT | Pregunta asociada |
| `image_data` | BLOB | Imagen del procedimiento |
| `status` | TEXT | `pending` / `PENDING_TEACHER_VALIDATION` / `VALIDATED_BY_TEACHER` / `reviewed` |
| `ai_proposed_score` | REAL | Score propuesto por IA (nunca afecta ELO directamente) |
| `teacher_score` | REAL | Calificación oficial del docente (0–100) |
| `final_score` | REAL | Nota final = teacher_score (única que afecta ELO) |
| `elo_delta` | REAL | Ajuste ELO calculado: `(final_score - 50) * 0.2` |
| `file_hash` | TEXT | SHA-256 del archivo subido (detección anti-plagio) |

**`audit_group_changes`**: log de reasignaciones de grupo (admin), con usuario, grupo anterior/nuevo y timestamp.

### Migraciones

Las migraciones son **aditivas** (`ALTER TABLE ADD COLUMN IF NOT EXISTS`). No hay migraciones destructivas. Se ejecutan automáticamente en `SQLiteRepository.__init__()`.

### Usuario admin

El usuario admin se crea al primer arranque **sólo si la variable de entorno `ADMIN_PASSWORD` está definida**:

```bash
export ADMIN_USER=admin          # opcional, valor por defecto: "admin"
export ADMIN_PASSWORD=tu_clave   # obligatorio para crear el admin
```

Si `ADMIN_PASSWORD` no está definida, no se crea ningún usuario admin automáticamente. No hay credenciales por defecto en el código.

---

## Niveles educativos y catálogo de cursos

Al registrarse, cada estudiante selecciona su **nivel educativo**, que determina qué cursos puede ver:

| Nivel | Bloque | Cursos |
|---|---|---|
| Universidad | `Universidad` | Álgebra Lineal, Cálculo Diferencial, Cálculo Integral, Cálculo de Varias Variables, Ecuaciones Diferenciales, Probabilidad |
| Colegio | `Colegio` | Álgebra Básica, Aritmética Básica, Trigonometría, Geometría |
| Concursos | `Concursos` | DIAN — Gestor I, SENA — Profesional 10 |

El catálogo se genera automáticamente desde los archivos JSON en `items/bank/`. La asignación curso-bloque se define en `_COURSE_BLOCK_MAP` dentro de `sqlite_repository.py`.

Los estudiantes se **matriculan** en cursos de su nivel y se unen a un **grupo** creado por un docente para ese curso.

---

## Roles de usuario

### Estudiante
- Selecciona su **nivel educativo** al registrarse: Universidad, Colegio o Concursos.
- Se matricula en **cursos** del catálogo correspondiente a su nivel y se une a un grupo del docente.
- Accede al **modo práctica**: responde preguntas adaptativas, ve retroalimentación socrática con IA, rastrea su ELO por tópico.
- Puede subir **procedimientos manuscritos** (imagen o PDF) para revisión (IA o docente), con validación de relevancia y detección de duplicados.
- Puede ver su **dashboard de estadísticas**: historial de intentos, evolución del ELO, racha de estudio, ranking de 16 niveles, y recomendaciones generadas con IA.
- **Centro de feedback**: consulta notas numéricas (IA y docente), comentarios y estado de cada procedimiento enviado, con notificación de revisiones nuevas.

### Docente
- Requiere aprobación del admin tras el registro.
- Crea y gestiona **grupos de alumnos** vinculados a cursos del catálogo.
- Los nombres de grupo son **únicos por profesor** (case-insensitive); el sistema rechaza duplicados.
- Accede al **dashboard docente** con **filtros cascada** (Grupo → Nivel → Materia): ELO por tópico de cada alumno, tasa de acierto reciente, probabilidades de fallo por pregunta, historial de intentos.
- Revisa y califica **procedimientos** enviados por alumnos (con propuesta de la IA como referencia). Badge de notificación con cantidad de pendientes.
- Puede generar **análisis pedagógico con IA** sobre cualquier alumno (con ELO desglosado por tópico y tiempo promedio de respuesta).

### Admin
- Aprueba o rechaza solicitudes de docentes.
- Reasigna alumnos entre grupos (con log de auditoría).
- **Elimina grupos**: desvincula estudiantes y matrículas sin perder datos históricos.
- **Da de baja estudiantes y docentes** (`active = 0`): impide login conservando todo el historial. Puede reactivarlos.
- Todas las acciones destructivas requieren **confirmación** en la UI.
- Acceso completo a todos los datos.

---

## Seguridad

- **Argon2id** como algoritmo de hashing de contraseñas (vía `passlib[argon2]`).
- **Migración automática** desde hashes SHA-256 legacy: en el próximo login del usuario, el hash antiguo se reemplaza por Argon2id de forma transparente.
- **Contraseña obligatoria** en el registro: mínimo 6 caracteres, validada en UI y backend. La columna `password_hash` es `NOT NULL`.
- **Cuentas con contraseña inválida** (vacía, nula o solo espacios) se desactivan automáticamente en la migración de base de datos.
- **Login bloqueado** para cuentas con hash vacío o nulo.
- Las contraseñas nunca se almacenan en texto plano ni en logs.
- Las API keys de los proveedores de IA se gestionan solo en memoria de sesión (sidebar de Streamlit); nunca se persisten en base de datos.
- Las credenciales del admin se configuran exclusivamente vía **variables de entorno** (`ADMIN_PASSWORD`, `ADMIN_USER`); no hay credenciales hardcodeadas.

---

## Instalación y ejecución

**Requisitos**: Python 3.10+

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd LevelUp-ELO

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar (siempre desde la raíz del proyecto)
streamlit run src/interface/streamlit/app.py
```

> **Importante**: la app debe lanzarse desde la raíz del repositorio porque `app.py` inyecta el directorio raíz en `sys.path` en tiempo de ejecución para resolver el paquete `src/`.

La base de datos `data/elo_database.db` se crea automáticamente en el primer arranque junto con el usuario admin, las preguntas del banco y los usuarios de prueba.

### Usuarios de prueba

Al primer arranque se crean automáticamente los siguientes usuarios demo:

**Usuarios demo** (contraseña: `demo1234`):

| Usuario | Rol | Detalle |
|---|---|---|
| `profesor1` | Docente | Pre-aprobado, con grupos demo vinculados a cursos |
| `estudiante1` | Estudiante | Nivel **Universidad**, matriculado en Cálculo Diferencial |
| `estudiante2` | Estudiante | Nivel **Colegio**, matriculado en Álgebra Básica |

**Estudiantes de prueba persistentes** (contraseña: `test1234`, `is_test_user=1`):

| Usuario | Nivel | Cursos matriculados |
|---|---|---|
| `estudiante_colegio_1` | Colegio | Todos los cursos de Colegio |
| `estudiante_colegio_2` | Colegio | Todos los cursos de Colegio |
| `estudiante_colegio_3` | Colegio | Todos los cursos de Colegio |
| `estudiante_universidad_1` | Universidad | Todos los cursos de Universidad |
| `estudiante_universidad_2` | Universidad | Todos los cursos de Universidad |

El seed de estudiantes de prueba (`seed_test_students.py`) es estrictamente idempotente: solo crea usuarios si no existen, nunca modifica progreso, intentos, matrículas ni ELO existentes. El flag `is_test_user=1` los protege contra eliminación accidental.

Los estudiantes pueden iniciar su estudio inmediatamente tras el login — cada uno ve el catálogo de cursos de su nivel educativo.

---

## Configuración de IA en la UI

En el **panel lateral (sidebar)** de Streamlit:

1. **Proveedor**: se detecta automáticamente al pegar la API key. Para proveedores locales (LM Studio / Ollama) no se necesita key.
2. **URL del servidor**: para LM Studio/Ollama, configurable (por defecto `http://localhost:1234/v1`).
3. **Modelo**: se puede escribir manualmente o, para servidores locales, se detectan los modelos cargados vía `/models`.

Si no se configura ningún proveedor, todas las funciones de IA retornan valores por defecto y la aplicación funciona completamente sin IA.

---

## Agregar preguntas

Las preguntas se organizan en **`items/bank/`**, un archivo JSON por curso. El nombre del archivo (sin extensión) se convierte en el `course_id`. Al arrancar, `sync_items_from_bank_folder()` registra cada archivo como curso y sincroniza sus ítems a la base de datos **sin sobrescribir** los ratings ELO que ya hubieran acumulado.

### Crear un nuevo curso

1. Crea un archivo `items/bank/mi_curso.json` con un array de ítems.
2. Agrega la entrada en `_COURSE_BLOCK_MAP` en `sqlite_repository.py`:
   ```python
   'mi_curso': 'Universidad',  # o 'Colegio' o 'Concursos'
   ```
3. Reinicia la app. El curso y sus ítems aparecerán en el catálogo.

### Formato de cada ítem

**Pregunta de solo texto (sin imagen):**

```json
{
    "id": "cd_01",
    "content": "Derivada de $\\sin(x)$.",
    "difficulty": 650,
    "topic": "Cálculo Diferencial",
    "options": ["$\\cos(x)$", "-$\\cos(x)$", "$\\sin(x)$", "-$\\sin(x)$"],
    "correct_option": "$\\cos(x)$"
}
```

**Pregunta con imagen:**

```json
{
    "id": "geo_01",
    "content": "Observa la siguiente figura y calcula el área sombreada.",
    "difficulty": 1200,
    "topic": "Geometría",
    "options": ["$12\\pi$", "$8\\pi$", "$16\\pi$", "$4\\pi$"],
    "correct_option": "$12\\pi$",
    "image_url": "https://ejemplo.com/area_sombreada.png"
}
```

### Campos del ítem

| Campo | Requerido | Descripción |
|---|---|---|
| `id` | Sí | String único en todo el banco (ej. `cd_01`, `geo_15`) |
| `content` | Sí | Enunciado; usar `$...$` para LaTeX inline y `$$...$$` para bloque |
| `difficulty` | Sí | Rating ELO inicial del ítem (rango recomendado: 600–1800) |
| `topic` | Sí | Tema dentro del curso (ej. "Derivadas", "Áreas") |
| `options` | Sí | Lista de 2 a 4 opciones (soportan LaTeX) |
| `correct_option` | Sí | Debe coincidir **exactamente** con uno de los strings en `options` |
| `image_url` | No | URL o ruta de imagen complementaria (se muestra debajo del enunciado) |

### Preguntas con imágenes

Muchas preguntas de matemáticas, geometría o concursos necesitan una figura, gráfica o diagrama que el estudiante debe analizar para responder. El campo `image_url` (o su alias `image_path`) permite asociar una imagen a cualquier pregunta. La imagen se renderiza debajo del enunciado, antes de las opciones de respuesta.

#### Formas de integrar imágenes

**1. URL externa (hosting de imágenes)**

La forma más simple. Sube la imagen a cualquier servicio de hosting (GitHub, Imgur, Google Drive público, servidor propio) y usa la URL directa:

```json
{
    "id": "tri_05",
    "content": "¿Cuál es el valor del ángulo $\\alpha$ en el triángulo mostrado?",
    "difficulty": 900,
    "topic": "Trigonometría",
    "options": ["$30°$", "$45°$", "$60°$", "$90°$"],
    "correct_option": "$45°$",
    "image_url": "https://raw.githubusercontent.com/tu-usuario/tu-repo/main/images/triangulo_alpha.png"
}
```

> La URL debe apuntar directamente al archivo de imagen (terminando en `.png`, `.jpg`, `.svg`, etc.), no a una página HTML que contenga la imagen.

**2. Ruta local relativa al proyecto**

Si prefieres no depender de servicios externos, coloca las imágenes en una carpeta dentro del proyecto (por ejemplo `items/images/`) y referénciala con una ruta relativa:

```json
{
    "id": "geo_03",
    "content": "Calcula el perímetro de la figura.",
    "difficulty": 1100,
    "topic": "Geometría",
    "options": ["$24$ cm", "$18$ cm", "$30$ cm", "$12$ cm"],
    "correct_option": "$24$ cm",
    "image_path": "items/images/perimetro_figura.png"
}
```

> Usa `image_path` o `image_url` indistintamente — el sistema acepta ambos campos. Si ambos están presentes, `image_url` tiene prioridad.

**3. Usando GitHub como hosting gratuito**

Sube las imágenes a tu repositorio y usa la URL raw de GitHub:

1. Crea una carpeta `items/images/` en tu repositorio.
2. Sube las imágenes ahí.
3. Usa la URL raw: `https://raw.githubusercontent.com/<usuario>/<repo>/main/items/images/mi_imagen.png`

#### Recomendaciones para imágenes

- **Formatos soportados**: PNG, JPG, SVG, GIF, WebP.
- **Tamaño recomendado**: entre 400px y 1200px de ancho. La imagen se ajusta automáticamente al ancho del contenedor.
- **Fondo**: preferir fondo blanco o transparente (PNG) para buena legibilidad.
- **Resolución**: suficiente para que fórmulas y números sean legibles. Mínimo 150 DPI si la imagen contiene texto.
- **Nombre del archivo**: usar nombres descriptivos (`triangulo_rectangulo_30_60.png` en lugar de `img1.png`).
- **Sin imagen**: si el campo `image_url`/`image_path` no existe, está vacío o la URL no carga, la pregunta se muestra normalmente solo con texto — la imagen es siempre opcional y nunca rompe la UI.

### Notas importantes sobre el formato JSON

- Los **backslashes de LaTeX** deben estar escapados en JSON: usar `\\frac`, `\\sin`, `\\alpha`, etc. Un `\f` sin escapar causa `JSONDecodeError`.
- Las **opciones de respuesta** también soportan LaTeX: `"$\\frac{1}{2}$"`.
- El campo `correct_option` debe coincidir **carácter por carácter** con uno de los strings en `options`, incluyendo espacios y signos LaTeX.

### Cursos disponibles

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

## Dependencias

| Paquete | Uso |
|---|---|
| `streamlit` | Framework de UI |
| `pandas` | Manipulación de datos en dashboards |
| `plotly` | Gráficos interactivos de ELO y estadísticas |
| `matplotlib` | Gráficos complementarios |
| `passlib[argon2]` | Hashing de contraseñas con Argon2id |
| `openai>=1.0.0` | Cliente OpenAI-compatible (Groq, Gemini, HF, LM Studio, Ollama) |
| `anthropic>=0.40.0` | SDK nativo de Anthropic Claude |
| `extra-streamlit-components` | Componentes adicionales de UI |
| `PyMuPDF` | Renderizado de PDF a imagen para revisión de procedimientos |
| `sympy` | Verificación simbólica de equivalencias algebraicas en el pipeline matemático |
