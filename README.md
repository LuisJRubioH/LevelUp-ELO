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
- [Base de datos](#base-de-datos)
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
- **Sin infraestructura externa obligatoria**: funciona completamente offline con LM Studio u Ollama; las funciones de IA degradan con gracia si no hay servidor disponible.

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
│   │   └── sqlite_repository.py  # SQLite: esquema, migraciones, seed, queries
│   ├── external_api/
│   │   └── ai_client.py          # Cliente universal multi-proveedor de IA
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
│   └── bank.json           # Banco de preguntas (sincronizado automáticamente al inicio)
├── requirements.txt        # Dependencias Python
├── elo_project.db          # Base de datos SQLite (generada en el primer arranque)
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

### Tres funciones de IA

- **`get_socratic_guidance()`** / **`get_socratic_guidance_stream()`**: tutor socrático que guía al alumno con preguntas sin revelar la respuesta. Soporta streaming token a token.
- **`get_pedagogical_analysis()`**: análisis profundo del desempeño de un estudiante para el docente.
- **`analyze_performance_local()`**: genera 3 recomendaciones en JSON para el dashboard de estadísticas del alumno.

---

## Base de datos

SQLite (archivo `elo_project.db` en el directorio de trabajo). Se crea y migra automáticamente en cada arranque.

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
| `rating_deviation` | REAL | RD global (promedio de tópicos) |

**`groups`**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER PK | Identificador |
| `name` | TEXT | Nombre del grupo |
| `teacher_id` | INTEGER FK | Docente propietario |

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

**`audit_group_changes`**: log de reasignaciones de grupo (admin), con usuario, grupo anterior/nuevo y timestamp.

### Migraciones

Las migraciones son **aditivas** (`ALTER TABLE ADD COLUMN IF NOT EXISTS`). No hay migraciones destructivas. Se ejecutan automáticamente en `SQLiteRepository.__init__()`.

### Credenciales por defecto

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | admin |

---

## Roles de usuario

### Estudiante
- Debe pertenecer a un grupo (asignado por docente o admin).
- Accede al **modo práctica**: responde preguntas, ve retroalimentación socrática con IA, rastrea su ELO por tópico.
- Puede ver su **dashboard de estadísticas**: historial de intentos, evolución del ELO, recomendaciones generadas con IA.

### Docente
- Requiere aprobación del admin tras el registro.
- Crea y gestiona **grupos de alumnos**.
- Accede al **dashboard docente**: ELO por tópico de cada alumno, tasa de acierto reciente, probabilidades de fallo por pregunta, historial de intentos.
- Puede generar **análisis pedagógico con IA** sobre cualquier alumno.

### Admin
- Aprueba o rechaza solicitudes de docentes.
- Reasigna alumnos entre grupos (con log de auditoría).
- Activa/desactiva usuarios.
- Acceso completo a todos los datos.

---

## Seguridad

- **Argon2id** como algoritmo de hashing de contraseñas (vía `passlib[argon2]`).
- **Migración automática** desde hashes SHA-256 legacy: en el próximo login del usuario, el hash antiguo se reemplaza por Argon2id de forma transparente.
- Las contraseñas nunca se almacenan en texto plano ni en logs.
- Las API keys de los proveedores de IA se gestionan solo en memoria de sesión (sidebar de Streamlit); nunca se persisten en base de datos.

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

La base de datos `elo_project.db` se crea automáticamente en el primer arranque junto con el usuario admin y las preguntas del banco.

---

## Configuración de IA en la UI

En el **panel lateral (sidebar)** de Streamlit:

1. **Proveedor**: se detecta automáticamente al pegar la API key. Para proveedores locales (LM Studio / Ollama) no se necesita key.
2. **URL del servidor**: para LM Studio/Ollama, configurable (por defecto `http://localhost:1234/v1`).
3. **Modelo**: se puede escribir manualmente o, para servidores locales, se detectan los modelos cargados vía `/models`.

Si no se configura ningún proveedor, todas las funciones de IA retornan valores por defecto y la aplicación funciona completamente sin IA.

---

## Agregar preguntas

Edita `items/bank.json`. Cada pregunta requiere:

```json
{
    "id": "q_nuevo",
    "content": "Enunciado con soporte de LaTeX: $ax^2 + bx + c = 0$",
    "difficulty": 1200,
    "topic": "Álgebra Lineal",
    "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
    "correct_option": "Opción A"
}
```

| Campo | Requerido | Descripción |
|---|---|---|
| `id` | Sí | String único en todo el banco |
| `content` | Sí | Enunciado; usar `$...$` para LaTeX inline y `$$...$$` para bloque |
| `difficulty` | Sí | Rating ELO inicial del ítem (rango recomendado: 600–1800) |
| `topic` | Sí | Tema (debe coincidir exactamente con los de la UI para filtrar) |
| `options` | Sí | Lista de 2 a 4 opciones |
| `correct_option` | Sí | Debe coincidir exactamente con uno de los strings en `options` |

En el siguiente arranque de la app, el ítem se sincroniza automáticamente a la base de datos **sin sobrescribir** el rating ELO que ya hubiera acumulado.

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
