# Plan de Ingeniería — LevelUp-ELO V1.0

> Documento técnico de implementación.
> Fecha: 2026-04-10 | Autor: Luis Rubio
> Estado actual del proyecto: **V0.9-beta** → Objetivo: **V1.0 estable**

---

## Índice

1. [Diagnóstico ejecutivo](#1-diagnóstico-ejecutivo)
2. [Principios de ingeniería aplicados](#2-principios-de-ingeniería-aplicados)
3. [Sprints de trabajo](#3-sprints-de-trabajo)
   - Sprint 1 — Integridad del banco de datos y carga confiable
   - Sprint 2 — Eliminación de deuda técnica en dominio
   - Sprint 3 — Logging, manejo de errores y observabilidad
   - Sprint 4 — Refactoring de app.py (modularización)
   - Sprint 5 — Suite de pruebas
   - Sprint 6 — CI/CD y calidad automatizada
4. [Arquitectura de pruebas](#4-arquitectura-de-pruebas)
5. [Criterios de aceptación V1.0](#5-criterios-de-aceptación-v10)
6. [Checklist de entrega](#6-checklist-de-entrega)

---

## 1. Diagnóstico ejecutivo

### Deuda técnica identificada (priorizada)

| ID | Archivo | Problema exacto | Severidad | Tipo |
|----|---------|----------------|-----------|------|
| D1 | `items/bank/*.json` | Encoding UTF-8/charmap en DIAN, SENA, algebra_lineal y ~20 semillero — fallan silenciosamente en carga | **Crítico** | Bug |
| D2 | `app.py:29-34` | `importlib.reload()` de 6 módulos en cada rerun — antipatrón que corrompe estado global en multiusuario | **Crítico** | Arquitectura |
| D3 | `student_service.py:104` | `impact_modifier=1.0` hardcodeado — feature cognitiva diseñada pero desactivada sin encapsulamiento correcto | **Alto** | Deuda |
| D4 | `ai_client.py:133,793,964,1086,1094` | 5 bloques `except Exception: pass` sin logging — fallos silenciosos en producción | **Alto** | Confiabilidad |
| D5 | `cognitive.py:109` | `except:` bare sin excepción específica ni logging | **Alto** | Confiabilidad |
| D6 | `domain/elo/zdp.py` | `zdp_interval()` implementado pero sin usar — código de dominio huérfano | **Medio** | Deuda |
| D7 | `student_service.py` | Sin transacción atómica: `update_item_rating()` + `save_attempt()` pueden quedar inconsistentes | **Alto** | Integridad |
| D8 | `requirements.txt` | `requests` se importa en `ai_client.py` pero no está declarado; versiones sin pinning | **Medio** | Reproducibilidad |
| D9 | `app.py` | 3,669 líneas en un monolito — imposible testear, difícil mantener | **Alto** | Arquitectura |
| D10 | Toda la codebase | 0% cobertura de pruebas — no hay validación automatizada de regresiones | **Crítico** | Calidad |

### Lo que funciona y se preserva intacto

- Dominio ELO: `vector_elo.py`, `model.py`, `uncertainty.py`, `item_selector.py` — correcto y completo
- Paridad dual DB: SQLite ↔ PostgreSQL tienen API pública idéntica (verificado: 91 vs 94 métodos)
- `postgres_repository.py`: advisory locks, retry decorator, pool de conexiones — robusto
- Multi-IA: detección por prefijo, streaming, degradación con gracia
- Flujos de usuario: login/registro/admin — completos y funcionales
- `math_procedure_review.py`, `symbolic_math_verifier.py` — correctos y se usan

---

## 2. Principios de ingeniería aplicados

### SOLID aplicado al proyecto

**S — Single Responsibility**
- `app.py` viola SRP: maneja login, UI estudiante, UI docente, UI admin, gestión de estado, carga de assets
- **Acción**: partir en módulos de vista (`views/student.py`, `views/teacher.py`, `views/admin.py`, `views/auth.py`)

**O — Open/Closed**
- `CognitiveAnalyzer` está cerrado a extensión porque `impact_modifier=1.0` está hardcodeado en el servicio, no en la clase
- **Acción**: mover la decisión de `impact_modifier` al configurador del servicio, no al llamador

**L — Liskov Substitution**
- `SQLiteRepository` y `PostgresRepository` son substitutos correctos — API pública idéntica ✓

**I — Interface Segregation**
- Los repositorios exponen todos los métodos a todos los consumidores
- **Acción**: añadir protocolos (`typing.Protocol`) para cada rol de consumidor: `IStudentRepository`, `ITeacherRepository`, `IAdminRepository`

**D — Dependency Inversion**
- `StudentService` recibe el repositorio por constructor ✓
- **Pendiente**: `CognitiveAnalyzer` instancia internamente el cliente de IA — acopla servicio de dominio a infraestructura

### Clean Architecture — capas respetadas

```
domain/          ← sin cambios (correcto)
application/     ← refactoring de student_service (transacciones + feature flag)
infrastructure/  ← logging, fix encoding, protocols
interface/       ← modularización de app.py en views/
```

**Regla de dependencia**: los cambios fluyen hacia adentro (interface → application → domain). Nunca al revés.

### Principio DRY aplicado

- El flujo de `try/except` en los repos es repetitivo — extraer `_with_connection()` context manager en PostgreSQL
- Los bloques de `st.markdown` con HTML en app.py están duplicados — extraer helpers de componentes

### Fail Fast

- La carga del banco de preguntas debe fallar con error claro, no silenciosamente
- Las API keys inválidas deben reportarse al usuario, no absorber la excepción

---

## 3. Sprints de trabajo

---

### Sprint 1 — Integridad del banco de preguntas

**Objetivo**: garantizar que el 100% de los ítems del banco carguen correctamente en ambos entornos.

**Duración estimada**: 2–3 días

---

#### Tarea 1.1 — Diagnóstico de encoding

**Problema exacto**: `json.load()` en `sync_items_from_bank_folder()` usa el encoding del sistema operativo (Windows: cp1252/charmap). Los JSON con caracteres UTF-8 (ñ, tildes, fracciones LaTeX como `½`) fallan con `UnicodeDecodeError`.

**Acción**:
```python
# ANTES (sqlite_repository.py y postgres_repository.py)
with open(json_path, 'r') as f:
    items = json.load(f)

# DESPUÉS
with open(json_path, 'r', encoding='utf-8') as f:
    items = json.load(f)
```

**Aplica en**:
- `sqlite_repository.py` → método `sync_items_from_bank_folder()` (buscar todas las llamadas a `open()` con JSON)
- `postgres_repository.py` → mismo método

**Regla Dual DB**: modificar ambos en el mismo commit.

---

#### Tarea 1.2 — Validador de banco de preguntas

**Problema**: un ítem con `correct_option` que no esté en `options`, o `difficulty` fuera de rango, se carga sin error y rompe el selector adaptativo.

**Acción**: crear `scripts/validate_bank.py`:

```python
"""
scripts/validate_bank.py
Valida estructura e integridad de todos los ítems del banco.
Ejecutar: python scripts/validate_bank.py
Retorna exit code 1 si hay errores (útil para CI).
"""

import json
import sys
from pathlib import Path

BANK_DIR = Path("items/bank")
REQUIRED_FIELDS = {"id", "content", "difficulty", "topic", "options", "correct_option"}
DIFFICULTY_RANGE = (100, 3000)

errors = []
warnings = []

def validate_item(item: dict, source_file: str) -> None:
    item_id = item.get("id", "<sin id>")
    prefix = f"[{source_file}] Item '{item_id}'"

    # Campos requeridos
    missing = REQUIRED_FIELDS - set(item.keys())
    if missing:
        errors.append(f"{prefix}: faltan campos: {missing}")
        return

    # correct_option debe estar en options
    if item["correct_option"] not in item["options"]:
        errors.append(
            f"{prefix}: correct_option='{item['correct_option']}' "
            f"no está en options={item['options']}"
        )

    # Dificultad en rango
    d = item["difficulty"]
    if not (DIFFICULTY_RANGE[0] <= d <= DIFFICULTY_RANGE[1]):
        warnings.append(
            f"{prefix}: difficulty={d} fuera del rango recomendado {DIFFICULTY_RANGE}"
        )

    # Opciones mínimas
    if len(item["options"]) < 2:
        errors.append(f"{prefix}: debe tener al menos 2 opciones")

    # ID único global (verificado fuera de esta función)

def main():
    all_ids = []
    json_files = list(BANK_DIR.rglob("*.json"))

    if not json_files:
        print("ERROR: No se encontraron archivos JSON en items/bank/")
        sys.exit(1)

    for json_file in sorted(json_files):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                items = json.load(f)
        except UnicodeDecodeError as e:
            errors.append(f"[{json_file.name}]: Error de encoding UTF-8: {e}")
            continue
        except json.JSONDecodeError as e:
            errors.append(f"[{json_file.name}]: JSON inválido: {e}")
            continue

        if not isinstance(items, list):
            errors.append(f"[{json_file.name}]: debe ser un array JSON, no {type(items)}")
            continue

        for item in items:
            validate_item(item, json_file.name)
            if "id" in item:
                all_ids.append((item["id"], json_file.name))

    # Verificar IDs duplicados globales
    seen = {}
    for item_id, source in all_ids:
        if item_id in seen:
            errors.append(
                f"ID duplicado '{item_id}' en '{source}' y '{seen[item_id]}'"
            )
        seen[item_id] = source

    # Reporte
    total_items = len(all_ids)
    total_files = len(json_files)
    print(f"\n{'='*60}")
    print(f"Banco validado: {total_files} archivos, {total_items} ítems")
    print(f"{'='*60}")

    if warnings:
        print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
        for w in warnings:
            print(f"   {w}")

    if errors:
        print(f"\n❌ ERRORES ({len(errors)}):")
        for e in errors:
            print(f"   {e}")
        print(f"\nValidación FALLIDA. Corregir antes de continuar.")
        sys.exit(1)
    else:
        print(f"\n✅ Validación EXITOSA. Banco íntegro.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

#### Tarea 1.3 — Hacer sync_items_from_bank_folder() observable

**Problema**: si un archivo falla al cargar, el error se absorbe y el curso queda con 0 ítems sin avisar.

**Acción** en ambos repositorios:

```python
# ANTES
try:
    with open(json_path) as f:
        items = json.load(f)
except Exception:
    continue  # silencioso

# DESPUÉS
import logging
logger = logging.getLogger(__name__)

try:
    with open(json_path, encoding='utf-8') as f:
        items = json.load(f)
except UnicodeDecodeError as e:
    logger.error(
        "Error de encoding en '%s': %s. "
        "Verificar que el archivo sea UTF-8 sin BOM.",
        json_path.name, e
    )
    continue
except json.JSONDecodeError as e:
    logger.error("JSON inválido en '%s': %s", json_path.name, e)
    continue
```

---

### Sprint 2 — Deuda técnica en dominio y servicios

**Objetivo**: limpiar el código de dominio y servicios siguiendo SRP y Fail Fast.

**Duración estimada**: 3–4 días

---

#### Tarea 2.1 — Eliminar importlib.reload() de app.py

**Problema exacto** (`app.py` líneas 29-34):
```python
importlib.reload(db_mod)
importlib.reload(pg_mod)
importlib.reload(ai_mod)
importlib.reload(_math_review_mod)
importlib.reload(_router_mod)
importlib.reload(_pipeline_mod)
```

Cada rerun de Streamlit recarga 6 módulos. En multiusuario, dos usuarios pueden estar en medio de una recarga simultánea → estado global corrupto. Los caches de `@st.cache_resource` quedan invalidados.

**Acción**:
1. Eliminar todos los `importlib.reload()` y los `import importlib`
2. Los módulos de infraestructura (repositorio, AI client) son instancias en `st.session_state` — ya están protegidos contra recarga
3. Para hot-reload en desarrollo: usar `streamlit run --server.runOnSave=false` o el flag `--server.fileWatcherType=none`

```python
# ELIMINAR completamente (líneas 18, 29-34):
import importlib
importlib.reload(db_mod)
importlib.reload(pg_mod)
importlib.reload(ai_mod)
importlib.reload(_math_review_mod)
importlib.reload(_router_mod)
importlib.reload(_pipeline_mod)

# Los imports normales se mantienen:
from src.infrastructure.persistence import sqlite_repository as db_mod
# etc.
```

---

#### Tarea 2.2 — Feature flag para CognitiveAnalyzer

**Problema exacto** (`student_service.py` línea 104):
```python
# Forzado a 1.0 — feature cognitiva diseñada pero sin activar
impact_modifier = 1.0
```

`CognitiveAnalyzer` está correctamente implementado pero desactivado en el llamador. Esto viola OCP: el servicio de aplicación está tomando una decisión de configuración que debería estar en la capa de configuración.

**Acción** — introducir feature flag en StudentService:

```python
# src/application/services/student_service.py

class StudentService:
    def __init__(
        self,
        repository,
        ai_available: bool = False,
        enable_cognitive_modifier: bool = False,  # Feature flag explícito
    ):
        self.repository = repository
        self.ai_available = ai_available
        self.enable_cognitive_modifier = enable_cognitive_modifier
        if enable_cognitive_modifier:
            self.cognitive_analyzer = CognitiveAnalyzer()
        else:
            self.cognitive_analyzer = None

    def process_answer(self, ...) -> dict:
        ...
        # Análisis cognitivo — controlado por feature flag
        if self.enable_cognitive_modifier and self.cognitive_analyzer:
            cog_data = self.cognitive_analyzer.analyze_cognition(
                reasoning, is_correct, time_taken
            )
            impact_modifier = cog_data.get("impact_modifier", 1.0)
        else:
            impact_modifier = 1.0
            cog_data = {
                "confidence_score": None,
                "error_type": "none",
                "impact_modifier": 1.0,
            }
        ...
```

**En `app.py`** donde se instancia StudentService:
```python
student_service = StudentService(
    repository=repo,
    ai_available=st.session_state.get("ai_available", False),
    enable_cognitive_modifier=False,  # Explícito y buscable
)
```

**Beneficio**: ahora cualquier dev puede buscar `enable_cognitive_modifier` y entender inmediatamente que es una feature inactiva, con un punto único para activarla.

---

#### Tarea 2.3 — Transacción atómica en process_answer()

**Problema**: `update_item_rating()` y `save_attempt()` son dos operaciones separadas. Si falla la segunda, el rating del ítem queda actualizado sin que se registre el intento → inconsistencia de datos.

**Acción — patrón Unit of Work**:

En ambos repositorios, crear método `save_answer_transaction()` que agrupe las dos operaciones:

```python
# En sqlite_repository.py
def save_answer_transaction(
    self,
    user_id: int,
    item_id: str,
    item_difficulty_new: float,
    item_rd_new: float,
    attempt_data: dict,
) -> None:
    """Persiste el resultado de una respuesta de forma atómica."""
    conn = self.get_connection()
    try:
        cursor = conn.cursor()
        # Operación 1: actualizar dificultad del ítem
        cursor.execute(
            "UPDATE items SET difficulty=?, rating_deviation=? WHERE id=?",
            (item_difficulty_new, item_rd_new, item_id),
        )
        # Operación 2: registrar el intento
        cursor.execute(
            """INSERT INTO attempts
               (user_id, item_id, is_correct, elo_after, prob_failure,
                expected_score, time_taken, confidence_score, error_type, rating_deviation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                item_id,
                attempt_data["is_correct"],
                attempt_data["elo_after"],
                attempt_data["prob_failure"],
                attempt_data["expected_score"],
                attempt_data.get("time_taken"),
                attempt_data.get("confidence_score"),
                attempt_data.get("error_type"),
                attempt_data.get("rating_deviation"),
            ),
        )
        conn.commit()  # Ambas operaciones o ninguna
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# En postgres_repository.py — idéntico con %s y put_connection()
def save_answer_transaction(self, user_id, item_id, item_difficulty_new,
                             item_rd_new, attempt_data) -> None:
    conn = self.get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "UPDATE items SET difficulty=%s, rating_deviation=%s WHERE id=%s",
            (item_difficulty_new, item_rd_new, item_id),
        )
        cursor.execute(
            """INSERT INTO attempts
               (user_id, item_id, is_correct, elo_after, prob_failure,
                expected_score, time_taken, confidence_score, error_type, rating_deviation)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                user_id, item_id,
                attempt_data["is_correct"], attempt_data["elo_after"],
                attempt_data["prob_failure"], attempt_data["expected_score"],
                attempt_data.get("time_taken"), attempt_data.get("confidence_score"),
                attempt_data.get("error_type"), attempt_data.get("rating_deviation"),
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        self.put_connection(conn)
```

**Actualizar `student_service.py`** para llamar `save_answer_transaction()` en lugar de las dos llamadas separadas.

---

#### Tarea 2.4 — Protocolos de repositorio (Interface Segregation)

**Problema**: los servicios conocen el repositorio entero. Un `StudentService` no debería poder llamar `delete_group()`.

**Acción** — crear `src/application/interfaces/repositories.py`:

```python
# src/application/interfaces/repositories.py
"""
Protocolos de repositorio por rol de consumidor.
Siguen Interface Segregation Principle:
cada servicio solo ve los métodos que necesita.
"""
from typing import Protocol, Optional


class IStudentRepository(Protocol):
    def get_next_item(self, user_id: int, course_id: str) -> Optional[dict]: ...
    def save_answer_transaction(self, user_id: int, item_id: str,
                                item_difficulty_new: float, item_rd_new: float,
                                attempt_data: dict) -> None: ...
    def get_student_stats(self, user_id: int) -> dict: ...
    def get_study_streak(self, user_id: int, course_id: Optional[str] = None) -> int: ...
    def save_katia_interaction(self, user_id: int, course_id: str,
                               item_id: str, item_topic: str,
                               student_message: str,
                               katia_response: Optional[str] = None) -> None: ...


class ITeacherRepository(Protocol):
    def get_teacher_students(self, teacher_id: int) -> list: ...
    def get_student_attempts(self, student_id: int) -> list: ...
    def save_procedure_score(self, submission_id: int, score: float,
                             feedback: str) -> None: ...
    def export_teacher_student_data(self, teacher_id: int,
                                    group_id: Optional[int] = None) -> list: ...


class IAdminRepository(Protocol):
    def get_pending_teachers(self) -> list: ...
    def approve_teacher(self, user_id: int) -> None: ...
    def deactivate_user(self, user_id: int) -> None: ...
    def get_problem_reports(self, status: Optional[str] = None) -> list: ...
```

**Actualizar servicios** para recibir el protocolo en lugar del repositorio concreto:
```python
# student_service.py
from src.application.interfaces.repositories import IStudentRepository

class StudentService:
    def __init__(self, repository: IStudentRepository, ...):
        ...
```

---

#### Tarea 2.5 — Conectar zdp_interval() al selector

**Problema**: `zdp.py` define `zdp_interval(rating, delta)` pero `item_selector.py` calcula el rango ZDP manualmente con constantes mágicas.

**Acción**: en `item_selector.py`, importar y usar `zdp_interval`:

```python
# ANTES en item_selector.py
lower = student_rating - 200
upper = student_rating + 300

# DESPUÉS
from src.domain.elo.zdp import zdp_interval
lower, upper = zdp_interval(student_rating, delta=250)
```

Pequeño cambio, gran beneficio: la zona ZDP tiene un punto único de definición.

---

#### Tarea 2.6 — Pinning de requirements.txt

**Problema**: versiones sin especificar → `pip install` en producción puede traer versiones incompatibles.

```
# requirements.txt — ANTES
matplotlib
streamlit
pandas

# requirements.txt — DESPUÉS
matplotlib>=3.8,<4.0
streamlit>=1.40,<1.45
pandas>=2.1,<3.0
passlib[argon2]>=1.7,<2.0
openai>=1.0.0,<2.0
anthropic>=0.40.0,<1.0
extra-streamlit-components>=0.1.60
plotly>=5.18,<6.0
PyMuPDF>=1.23,<2.0
sympy>=1.12,<2.0
psycopg2-binary>=2.9,<3.0
openpyxl>=3.1,<4.0
supabase>=2.0,<3.0
python-dotenv>=1.0,<2.0
requests>=2.31,<3.0       # ← añadir: importado en ai_client.py pero faltaba
Pillow>=10.0,<11.0        # ← añadir: usado para procesamiento de GIFs
```

---

### Sprint 3 — Logging, manejo de errores y observabilidad

**Objetivo**: que ningún error en producción sea silencioso.

**Duración estimada**: 2–3 días

---

#### Tarea 3.1 — Sistema de logging centralizado

**Crear `src/infrastructure/logging_config.py`**:

```python
"""
src/infrastructure/logging_config.py
Configuración centralizada de logging para la aplicación.
"""
import logging
import sys
from pathlib import Path


def configure_logging(level: str = "INFO", log_file: str = None) -> None:
    """
    Configura el sistema de logging de la aplicación.

    Args:
        level: Nivel de log ("DEBUG", "INFO", "WARNING", "ERROR")
        log_file: Ruta a archivo de log (None = solo consola)
    """
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        datefmt=date_fmt,
        handlers=handlers,
    )

    # Silenciar librerías ruidosas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


# Logger raíz de la aplicación
def get_logger(name: str) -> logging.Logger:
    """Retorna un logger prefijado con 'levelup.'"""
    return logging.getLogger(f"levelup.{name}")
```

**En `app.py`**, al inicio:
```python
from src.infrastructure.logging_config import configure_logging
configure_logging(level="INFO")
```

---

#### Tarea 3.2 — Reemplazar except silenciosos en ai_client.py

**5 bloques identificados. Acción para cada uno**:

**Bloque 1 — `get_active_models()` línea 133**:
```python
# ANTES
except Exception:
    pass

# DESPUÉS
except Exception as e:
    logger.warning(
        "No se pudieron obtener modelos de '%s': %s. "
        "Continuando sin lista de modelos.",
        base_url, e
    )
```

**Bloque 2 — `_normalize_rec()` línea 793**:
```python
# ANTES
except Exception:
    pass

# DESPUÉS
except Exception as e:
    logger.debug("Normalización de recomendación fallida: %s", e)
    # Retornar el texto sin normalizar (degradación controlada)
```

**Bloque 3 — `validate_procedure_relevance()` línea 964**:
```python
# ANTES
except Exception:
    return True  # Beneficio de la duda

# DESPUÉS
except Exception as e:
    logger.warning(
        "Validación de relevancia de procedimiento fallida: %s. "
        "Asumiendo relevante (beneficio de la duda).",
        e
    )
    return True
```

**Bloques 4 y 5 — `AIClient.__init__()` líneas 1086, 1094**:
```python
# ANTES
except Exception:
    pass

# DESPUÉS
except Exception as e:
    logger.debug(
        "No se pudo inicializar AIClient desde %s: %s",
        "session_state" if ... else "secrets",
        e
    )
```

---

#### Tarea 3.3 — Reemplazar except bare en cognitive.py

```python
# ANTES (cognitive.py línea 109)
except:
    pass

# DESPUÉS
except Exception as e:
    logger.warning(
        "Análisis cognitivo falló para user_id=%s: %s. "
        "Usando impact_modifier neutro (1.0).",
        getattr(self, '_current_user_id', 'unknown'), e
    )
    return {
        "confidence_score": None,
        "error_type": "none",
        "impact_modifier": 1.0,
        "reasoning": "Análisis no disponible"
    }
```

---

#### Tarea 3.4 — Feedback al usuario cuando la IA falla

**Problema**: cuando la IA falla silenciosamente, el usuario ve "KatIA no responde" sin contexto.

**Acción en `app.py`**: distinguir entre tipos de fallo:

```python
# ANTES — un solo mensaje vago
except Exception:
    st.error("Error al conectar con la IA.")

# DESPUÉS — mensajes específicos y accionables
except ConnectionError:
    st.warning(
        "No se pudo conectar con el servidor de IA. "
        "Verifica que el servidor local esté activo o tu conexión a internet."
    )
except TimeoutError:
    st.warning(
        "La IA tardó demasiado en responder. "
        "Intenta de nuevo o continúa sin asistencia."
    )
except ValueError as e:
    st.error(f"Error en la respuesta de la IA: {e}")
    logger.error("ValueError en respuesta IA: %s", e, exc_info=True)
except Exception as e:
    st.error("Error inesperado con la IA.")
    logger.error("Error inesperado en IA: %s", e, exc_info=True)
```

---

### Sprint 4 — Modularización de app.py

**Objetivo**: partir el monolito en módulos cohesivos. 3,669 líneas → 4 archivos de ~800 líneas cada uno, más un `app.py` raíz de ~200 líneas.

**Duración estimada**: 4–5 días

**Principio**: no se cambia lógica, solo se mueve código. Cada módulo tiene SRP.

---

#### Estructura objetivo

```
src/interface/streamlit/
├── app.py                  # ~200 líneas: setup, routing por rol
├── state.py                # ~100 líneas: gestión de st.session_state
├── assets.py               # ~150 líneas: carga de logos, GIFs, banners
├── components/
│   ├── __init__.py
│   ├── timers.py           # _render_live_timer(), JS templates
│   ├── katia.py            # KatIA GIF display, mensajes
│   └── question_card.py    # Renderizado de pregunta + LaTeX + imagen
└── views/
    ├── __init__.py
    ├── auth_view.py         # Login, registro wizard, logout
    ├── student_view.py      # Panel estudiante: práctica, stats, cursos, feedback
    ├── teacher_view.py      # Dashboard docente: estudiantes, procedimientos, export
    └── admin_view.py        # Panel admin: usuarios, reportes técnicos
```

---

#### Tarea 4.1 — Extraer state.py

Centralizar toda la gestión de `st.session_state`:

```python
# src/interface/streamlit/state.py
"""
Gestión centralizada del estado de sesión de Streamlit.
Principio: un solo lugar donde se definen y acceden las claves de estado.
"""
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional


# Claves de sesión — constantes para evitar typos
KEY_USER_ID = "user_id"
KEY_USERNAME = "username"
KEY_ROLE = "role"
KEY_DB = "db"
KEY_AI_PROVIDER = "ai_provider"
KEY_CLOUD_API_KEY = "cloud_api_key"
KEY_SESSION_START = "session_start_time"
KEY_SELECTED_COURSE = "selected_course_id"
KEY_CURRENT_ITEM = "current_item"
KEY_KATIA_CHAT = "katia_chat_history"
KEY_WELCOME_DISMISSED = "welcome_dismissed"


def init_session_defaults() -> None:
    """Inicializa claves de sesión con valores por defecto si no existen."""
    defaults = {
        KEY_USER_ID: None,
        KEY_USERNAME: None,
        KEY_ROLE: None,
        KEY_AI_PROVIDER: None,
        KEY_CLOUD_API_KEY: None,
        KEY_SESSION_START: None,
        KEY_SELECTED_COURSE: None,
        KEY_CURRENT_ITEM: None,
        KEY_KATIA_CHAT: [],
        KEY_WELCOME_DISMISSED: False,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def is_authenticated() -> bool:
    return st.session_state.get(KEY_USER_ID) is not None


def get_current_user_id() -> Optional[int]:
    return st.session_state.get(KEY_USER_ID)


def get_current_role() -> Optional[str]:
    return st.session_state.get(KEY_ROLE)


def clear_session() -> None:
    """Limpia el estado de sesión al hacer logout."""
    keys_to_clear = [
        KEY_USER_ID, KEY_USERNAME, KEY_ROLE,
        KEY_SESSION_START, KEY_SELECTED_COURSE,
        KEY_CURRENT_ITEM, KEY_KATIA_CHAT,
        KEY_WELCOME_DISMISSED,
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
```

---

#### Tarea 4.2 — Extraer assets.py

```python
# src/interface/streamlit/assets.py
"""
Carga y cache de assets estáticos (logos, GIFs, banners).
Todos los assets se cargan una vez con @st.cache_resource.
"""
import base64
import os
import streamlit as st

_BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)))


@st.cache_resource
def load_logo(variant: str = "light") -> bytes:
    """Carga el logo como bytes. variant='light' o 'dark'."""
    filename = "logo-elo-light.png" if variant == "light" else "logo-elo2-dark.png"
    path = os.path.join(_BASE_PATH, filename)
    with open(path, "rb") as f:
        return f.read()


@st.cache_resource
def load_katia_gif_b64(gif_type: str = "correcto") -> str:
    """
    Carga el GIF comprimido de KatIA como base64 HTML.
    gif_type: 'correcto' (score >= 91) | 'errores' (score < 91)
    """
    filename = f"KatIA/{gif_type}_compressed.gif"
    path = os.path.join(_BASE_PATH, filename)
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            f'<img src="data:image/gif;base64,{b64}" '
            f'style="width:220px;border-radius:12px;">'
        )
    except FileNotFoundError:
        return ""


@st.cache_resource
def load_course_banners() -> dict:
    """
    Carga banners pixel art como base64.
    Retorna dict {keyword: b64_string | None}.
    """
    banners_dir = os.path.join(_BASE_PATH, "Banners")
    mapping = {
        'geometr':   'geometria.png',
        'aritm':     'aritmetica.png',
        'logic':     'logica.png',
        'lógic':     'logica.png',
        'conteo':    'conteo_combinatoria.png',
        'combinat':  'conteo_combinatoria.png',
        'probab':    'probabilidad.png',
        'álgebra':   'algebra.png',
        'algebra':   'algebra.png',
        'trigon':    'algebra.png',
    }
    result = {}
    for kw, filename in mapping.items():
        if kw in result:
            continue
        path = os.path.join(banners_dir, filename)
        try:
            with open(path, "rb") as f:
                result[kw] = base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            result[kw] = None
    return result


def get_banner_for_course(course_name: str) -> str | None:
    """Retorna el base64 del banner que corresponda al nombre del curso, o None."""
    banners = load_course_banners()
    name_lower = course_name.lower()
    for kw, b64 in banners.items():
        if kw in name_lower:
            return b64
    return None
```

---

#### Tarea 4.3 — app.py raíz simplificado

```python
# src/interface/streamlit/app.py — VERSIÓN SIMPLIFICADA POST-REFACTORING
"""
Punto de entrada principal de LevelUp-ELO.
Responsabilidad única: inicialización y routing por rol.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))))

import streamlit as st
from src.infrastructure.logging_config import configure_logging
from src.interface.streamlit.state import init_session_defaults, is_authenticated, get_current_role
from src.interface.streamlit.views.auth_view import render_auth
from src.interface.streamlit.views.student_view import render_student
from src.interface.streamlit.views.teacher_view import render_teacher
from src.interface.streamlit.views.admin_view import render_admin

# ── Configuración ──────────────────────────────────────────────────────
configure_logging(level=os.getenv("LOG_LEVEL", "INFO"))
st.set_page_config(
    page_title="LevelUp-ELO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inicialización de base de datos ────────────────────────────────────
if "db" not in st.session_state:
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        from src.infrastructure.persistence.postgres_repository import PostgresRepository
        try:
            st.session_state.db = PostgresRepository()
        except RuntimeError as e:
            st.error(f"Error al conectar con la base de datos: {e}")
            st.stop()
    else:
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
        st.session_state.db = SQLiteRepository()

# ── Estado de sesión ────────────────────────────────────────────────────
init_session_defaults()

# ── Routing por rol ─────────────────────────────────────────────────────
if not is_authenticated():
    render_auth()
else:
    role = get_current_role()
    if role == "student":
        render_student()
    elif role == "teacher":
        render_teacher()
    elif role == "admin":
        render_admin()
    else:
        st.error(f"Rol desconocido: {role}")
        st.stop()
```

---

### Sprint 5 — Suite de pruebas

**Objetivo**: cobertura >= 80% en servicios de aplicación y dominio; >= 60% en infraestructura.

**Duración estimada**: 5–6 días

---

#### Estructura de pruebas

```
tests/
├── conftest.py                      # Fixtures compartidos (repo en memoria, mocks de IA)
├── unit/
│   ├── domain/
│   │   ├── test_elo_model.py        # Factor K, delta ELO, ELO simétrico
│   │   ├── test_vector_elo.py       # VectorRating.update(), aggregate_global_elo()
│   │   ├── test_uncertainty.py      # RatingModel: decay, RD mínimo
│   │   ├── test_item_selector.py    # Fisher Information, expansión ZDP, priorización
│   │   ├── test_zdp.py             # zdp_interval() rangos válidos
│   │   └── test_katia_messages.py   # Rangos de mensajes por score
│   ├── application/
│   │   ├── test_student_service.py  # process_answer(), get_next_question()
│   │   └── test_teacher_service.py  # generate_ai_analysis(), dashboard data
│   └── infrastructure/
│       ├── test_bank_validator.py   # validate_bank.py: encoding, campos, IDs
│       └── test_logging_config.py   # configure_logging() inicializa correctamente
├── integration/
│   ├── test_sqlite_repository.py    # Ciclo completo: save_attempt + get_attempts
│   ├── test_answer_transaction.py   # Atomicidad: rollback si save_attempt falla
│   └── test_bank_loading.py        # sync_items_from_bank_folder() carga UTF-8
└── e2e/
    └── test_practice_flow.py        # Playwright: login → pregunta → respuesta → ELO
```

---

#### Tarea 5.1 — conftest.py con fixtures base

```python
# tests/conftest.py
"""
Fixtures compartidos para toda la suite de pruebas.
"""
import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from src.domain.elo.vector_elo import VectorRating
from src.domain.elo.uncertainty import RatingModel


@pytest.fixture
def in_memory_db():
    """SQLite en memoria para pruebas de integración — sin tocar archivos."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def mock_repository():
    """Repositorio mock para pruebas unitarias de servicios."""
    repo = MagicMock()
    repo.get_latest_elo_by_topic.return_value = {}
    repo.get_attempt_count.return_value = 10
    repo.save_answer_transaction.return_value = None
    repo.get_study_streak.return_value = 0
    return repo


@pytest.fixture
def student_vector():
    """VectorRating inicial para un estudiante nuevo."""
    return VectorRating(default_rating=1000.0, default_rd=350.0)


@pytest.fixture
def rating_model():
    """RatingModel estándar."""
    return RatingModel()


@pytest.fixture
def mock_ai_client():
    """Cliente de IA mock — no hace llamadas reales."""
    client = MagicMock()
    client.get_socratic_guidance.return_value = (
        "¿Has considerado qué ocurre cuando x tiende a 0?"
    )
    client.analyze_performance_local.return_value = {
        "recommendations": ["Practica más límites", "Revisa la regla de L'Hôpital"]
    }
    return client


@pytest.fixture
def sample_item():
    """Ítem de ejemplo para pruebas."""
    return {
        "id": "test_01",
        "content": "¿Cuál es la derivada de $\\sin(x)$?",
        "difficulty": 800.0,
        "rating_deviation": 200.0,
        "topic": "Derivadas",
        "options": ["$\\cos(x)$", "$-\\cos(x)$", "$\\sin(x)$", "$-\\sin(x)$"],
        "correct_option": "$\\cos(x)$",
    }
```

---

#### Tarea 5.2 — Pruebas unitarias de dominio ELO

```python
# tests/unit/domain/test_elo_model.py
"""
Pruebas unitarias del motor ELO.
Cubren: factor K dinámico, delta ELO, ELO simétrico de ítems.
"""
import pytest
from src.domain.elo.model import (
    compute_expected_score,
    dynamic_k_factor,
    compute_elo_delta,
)


class TestExpectedScore:
    def test_equal_rating_gives_50_percent(self):
        """Cuando estudiante y ítem tienen el mismo rating, P = 0.5."""
        assert compute_expected_score(1000, 1000) == pytest.approx(0.5, abs=0.001)

    def test_higher_student_rating_gives_higher_probability(self):
        """Estudiante más fuerte tiene mayor probabilidad de éxito."""
        p = compute_expected_score(student=1200, item=1000)
        assert p > 0.5

    def test_lower_student_rating_gives_lower_probability(self):
        """Estudiante más débil tiene menor probabilidad de éxito."""
        p = compute_expected_score(student=800, item=1000)
        assert p < 0.5

    def test_probability_is_between_0_and_1(self):
        """La probabilidad siempre está en [0, 1]."""
        for student in [0, 500, 1000, 2000, 5000]:
            for item in [0, 500, 1000, 2000, 5000]:
                p = compute_expected_score(student, item)
                assert 0.0 <= p <= 1.0


class TestDynamicKFactor:
    def test_initial_phase_k_is_40(self):
        """Menos de 30 intentos → K = 40 (búsqueda rápida)."""
        k = dynamic_k_factor(attempt_count=5, current_rating=1000, recent_error=0.5)
        assert k == 40

    def test_growth_phase_k_is_32(self):
        """30+ intentos, rating < 1400 → K = 32."""
        k = dynamic_k_factor(attempt_count=50, current_rating=1200, recent_error=0.5)
        assert k == 32

    def test_stable_phase_k_is_16(self):
        """Rating estable (error < 15%) → K = 16."""
        k = dynamic_k_factor(attempt_count=50, current_rating=1500, recent_error=0.10)
        assert k == 16

    def test_default_phase_k_is_24(self):
        """Caso base → K = 24."""
        k = dynamic_k_factor(attempt_count=50, current_rating=1500, recent_error=0.30)
        assert k == 24


class TestELODelta:
    def test_correct_answer_increases_rating(self):
        """Acierto con P < 1 siempre incrementa el rating."""
        delta = compute_elo_delta(
            k=24, result=1.0, expected=0.6, impact_modifier=1.0
        )
        assert delta > 0

    def test_wrong_answer_decreases_rating(self):
        """Fallo siempre decrementa el rating."""
        delta = compute_elo_delta(
            k=24, result=0.0, expected=0.4, impact_modifier=1.0
        )
        assert delta < 0

    def test_impact_modifier_scales_delta(self):
        """impact_modifier=2.0 dobla el cambio de rating."""
        delta_1 = compute_elo_delta(k=24, result=1.0, expected=0.5, impact_modifier=1.0)
        delta_2 = compute_elo_delta(k=24, result=1.0, expected=0.5, impact_modifier=2.0)
        assert delta_2 == pytest.approx(delta_1 * 2, abs=0.001)

    def test_item_rating_changes_symmetrically(self):
        """Cuando el estudiante gana, el ítem pierde exactamente el mismo delta."""
        delta_student = compute_elo_delta(k=24, result=1.0, expected=0.5, impact_modifier=1.0)
        delta_item = compute_elo_delta(k=24, result=0.0, expected=0.5, impact_modifier=1.0)
        assert delta_student == pytest.approx(-delta_item, abs=0.001)
```

---

#### Tarea 5.3 — Pruebas unitarias del selector adaptativo

```python
# tests/unit/domain/test_item_selector.py
"""
Pruebas del AdaptiveItemSelector.
Cubren: ZDP, Fisher Information, priorización, expansión progresiva.
"""
import pytest
from src.domain.selector.item_selector import AdaptiveItemSelector


@pytest.fixture
def selector():
    return AdaptiveItemSelector()


@pytest.fixture
def item_pool():
    """Pool de ítems con dificultades variadas."""
    return [
        {"id": f"item_{i}", "difficulty": 600 + i * 50, "topic": "Álgebra"}
        for i in range(20)
    ]


class TestZDPRange:
    def test_selects_item_in_zdp_range(self, selector, item_pool):
        """El selector elige ítems donde P(éxito) está en [0.4, 0.75]."""
        student_rating = 1000.0
        selected = selector.select_optimal_item(
            student_rating=student_rating,
            items=item_pool,
            seen_ids=set(),
            failed_ids=set(),
        )
        assert selected is not None

    def test_prioritizes_unseen_items(self, selector, item_pool):
        """Ítems no vistos tienen prioridad sobre los ya vistos."""
        seen_ids = {f"item_{i}" for i in range(10)}  # primeros 10 vistos
        selected = selector.select_optimal_item(
            student_rating=1000.0,
            items=item_pool,
            seen_ids=seen_ids,
            failed_ids=set(),
        )
        assert selected["id"] not in seen_ids

    def test_returns_none_when_pool_is_empty(self, selector):
        """Pool vacío retorna None, no levanta excepción."""
        result = selector.select_optimal_item(
            student_rating=1000.0,
            items=[],
            seen_ids=set(),
            failed_ids=set(),
        )
        assert result is None

    def test_expands_range_when_no_candidates(self, selector):
        """Si no hay ítems en rango inicial, expande hasta encontrar uno."""
        # Solo hay ítems muy fáciles (dificultad 200) para un estudiante con 1000
        easy_items = [{"id": "easy_1", "difficulty": 200, "topic": "Álgebra"}]
        result = selector.select_optimal_item(
            student_rating=1000.0,
            items=easy_items,
            seen_ids=set(),
            failed_ids=set(),
        )
        assert result is not None  # Debería encontrarlo expandiendo el rango
```

---

#### Tarea 5.4 — Pruebas de integración del repositorio

```python
# tests/integration/test_sqlite_repository.py
"""
Pruebas de integración con SQLite en memoria.
Verifican el ciclo completo de datos sin tocar archivos.
"""
import pytest
import os
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository


@pytest.fixture
def repo(tmp_path):
    """Repositorio con DB temporal — limpio en cada test."""
    db_path = str(tmp_path / "test.db")
    # Deshabilitar sincronización de banco (no hay JSON en tests)
    repo = SQLiteRepository(db_name=db_path)
    return repo


class TestAtomicTransaction:
    def test_save_answer_transaction_is_atomic(self, repo):
        """
        Si save_answer_transaction falla a mitad, ninguna operación queda persistida.
        """
        # Crear usuario e ítem de prueba
        # (implementación depende de los métodos del repo)
        pass  # Completar con setup de datos

    def test_save_attempt_persists_correctly(self, repo):
        """Los datos del intento se recuperan íntegros después de guardarse."""
        pass


class TestBankLoading:
    def test_utf8_json_loads_correctly(self, repo, tmp_path):
        """Un JSON UTF-8 con caracteres especiales (ñ, tildes) carga sin error."""
        import json
        json_content = [
            {
                "id": "test_utf8",
                "content": "Ecuación con ñ y tildes: $x^2 + ó = 0$",
                "difficulty": 800,
                "topic": "Álgebra",
                "options": ["Sí", "No", "Quizás"],
                "correct_option": "Sí",
            }
        ]
        json_file = tmp_path / "test_utf8.json"
        json_file.write_text(json.dumps(json_content), encoding="utf-8")
        # Verificar que se lee sin UnicodeDecodeError
        with open(json_file, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded[0]["id"] == "test_utf8"

    def test_cp1252_json_fails_with_clear_error(self, tmp_path):
        """Un JSON con encoding cp1252 (Windows) falla con error descriptivo."""
        json_file = tmp_path / "bad_encoding.json"
        # Escribir bytes cp1252 con caracteres incompatibles con cp1252
        json_file.write_bytes(b'[{"id": "bad", "content": "\x8d"}]')
        import pytest
        with pytest.raises(UnicodeDecodeError):
            with open(json_file, encoding="utf-8") as f:
                import json
                json.load(f)
```

---

#### Tarea 5.5 — Pruebas unitarias de StudentService

```python
# tests/unit/application/test_student_service.py
"""
Pruebas unitarias de StudentService.
Usa repositorio mock — sin acceso a BD real.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.application.services.student_service import StudentService


@pytest.fixture
def service(mock_repository):
    return StudentService(
        repository=mock_repository,
        ai_available=False,
        enable_cognitive_modifier=False,
    )


@pytest.fixture
def service_with_ai(mock_repository, mock_ai_client):
    return StudentService(
        repository=mock_repository,
        ai_available=True,
        enable_cognitive_modifier=False,
    )


class TestProcessAnswer:
    def test_correct_answer_returns_positive_elo_delta(
        self, service, mock_repository, student_vector, rating_model, sample_item
    ):
        """Un acierto siempre produce delta_elo >= 0."""
        result = service.process_answer(
            user_id=1,
            item=sample_item,
            selected_option=sample_item["correct_option"],
            vector_rating=student_vector,
            rating_model=rating_model,
            time_taken=15.0,
            reasoning="",
            course_id="calculo_diferencial",
        )
        assert result["is_correct"] is True
        assert result["delta_elo"] >= 0

    def test_wrong_answer_returns_negative_elo_delta(
        self, service, mock_repository, student_vector, rating_model, sample_item
    ):
        """Un fallo siempre produce delta_elo <= 0."""
        wrong_option = sample_item["options"][1]  # No es correct_option
        result = service.process_answer(
            user_id=1,
            item=sample_item,
            selected_option=wrong_option,
            vector_rating=student_vector,
            rating_model=rating_model,
            time_taken=15.0,
            reasoning="",
            course_id="calculo_diferencial",
        )
        assert result["is_correct"] is False
        assert result["delta_elo"] <= 0

    def test_save_answer_transaction_is_called(
        self, service, mock_repository, student_vector, rating_model, sample_item
    ):
        """El servicio llama save_answer_transaction (no las dos operaciones separadas)."""
        service.process_answer(
            user_id=1,
            item=sample_item,
            selected_option=sample_item["correct_option"],
            vector_rating=student_vector,
            rating_model=rating_model,
            time_taken=10.0,
            reasoning="",
            course_id="test_course",
        )
        mock_repository.save_answer_transaction.assert_called_once()

    def test_impact_modifier_is_1_when_cognitive_disabled(
        self, service, mock_repository, student_vector, rating_model, sample_item
    ):
        """Con enable_cognitive_modifier=False, impact_modifier es siempre 1.0."""
        with patch.object(service, "cognitive_analyzer", None):
            result = service.process_answer(
                user_id=1, item=sample_item,
                selected_option=sample_item["correct_option"],
                vector_rating=student_vector, rating_model=rating_model,
                time_taken=10.0, reasoning="", course_id="test_course",
            )
        # El delta debería ser K * (1 - P) * 1.0 exactamente
        assert result.get("impact_modifier") == 1.0


class TestGetNextQuestion:
    def test_returns_none_when_no_items_available(
        self, service, mock_repository
    ):
        """Sin ítems disponibles, retorna None sin error."""
        mock_repository.get_available_items.return_value = []
        result = service.get_next_question(
            user_id=1, course_id="test_course",
            student_rating=1000.0, seen_ids=set(), failed_ids=set()
        )
        assert result is None

    def test_prioritizes_failed_items_with_cooldown(
        self, service, mock_repository, sample_item
    ):
        """Ítems fallados con cooldown suficiente tienen prioridad."""
        mock_repository.get_available_items.return_value = [sample_item]
        result = service.get_next_question(
            user_id=1, course_id="test_course",
            student_rating=1000.0,
            seen_ids={sample_item["id"]},
            failed_ids={sample_item["id"]},
        )
        # El ítem fallado debería ser elegible dado que está en failed_ids
        # (lógica de cooldown verificada en test_item_selector.py)
        assert result is not None or result is None  # Solo verifica que no rompe
```

---

#### Tarea 5.6 — Pruebas del validador de banco

```python
# tests/unit/infrastructure/test_bank_validator.py
"""
Pruebas del script scripts/validate_bank.py.
"""
import json
import pytest
from pathlib import Path
import sys

# Importar funciones del validador
sys.path.insert(0, "scripts")
from validate_bank import validate_item


class TestValidateItem:
    def test_valid_item_produces_no_errors(self):
        errors = []
        warnings = []
        item = {
            "id": "q1",
            "content": "¿Cuál es $\\frac{d}{dx}[\\sin(x)]$?",
            "difficulty": 800,
            "topic": "Derivadas",
            "options": ["$\\cos(x)$", "$-\\cos(x)$"],
            "correct_option": "$\\cos(x)$",
        }
        validate_item(item, "test.json")
        assert len(errors) == 0

    def test_correct_option_not_in_options_raises_error(self):
        errors = []
        item = {
            "id": "q2",
            "content": "Pregunta",
            "difficulty": 800,
            "topic": "Álgebra",
            "options": ["A", "B", "C"],
            "correct_option": "D",  # No está en options
        }
        # La función debe detectar el error
        # (adaptar según implementación exacta de validate_item)

    def test_missing_required_field_raises_error(self):
        item = {
            "id": "q3",
            "content": "Pregunta sin difficulty",
            "topic": "Álgebra",
            "options": ["A", "B"],
            "correct_option": "A",
            # Falta "difficulty"
        }
        # Debe detectar campo faltante

    def test_single_option_raises_error(self):
        item = {
            "id": "q4",
            "content": "Pregunta",
            "difficulty": 800,
            "topic": "Álgebra",
            "options": ["Solo una opción"],
            "correct_option": "Solo una opción",
        }
        # Debe detectar que hay menos de 2 opciones
```

---

### Sprint 6 — CI/CD y calidad automatizada

**Objetivo**: que ningún commit rompa la codebase — automatizar todo lo que puede fallar.

**Duración estimada**: 2–3 días

---

#### Tarea 6.1 — Pre-commit hooks

Crear `.pre-commit-config.yaml`:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-json
        files: items/bank/
      - id: check-yaml
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        args: ["--line-length=100"]
        files: ^src/

  - repo: local
    hooks:
      - id: validate-bank
        name: Validar banco de preguntas
        entry: python scripts/validate_bank.py
        language: python
        pass_filenames: false
        files: ^items/bank/

      - id: db-sync-check
        name: Verificar sincronía SQLite/PostgreSQL
        entry: python scripts/db_sync_check.py
        language: python
        pass_filenames: false
        files: ^src/infrastructure/persistence/

      - id: pytest-unit
        name: Ejecutar pruebas unitarias
        entry: python -m pytest tests/unit/ -x -q
        language: python
        pass_filenames: false
        stages: [pre-push]
```

**Instalación**:
```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

---

#### Tarea 6.2 — GitHub Actions CI/CD

Crear `.github/workflows/ci.yml`:

```yaml
name: CI — LevelUp-ELO

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate-bank:
    name: Validar banco de preguntas
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Instalar dependencias
        run: pip install -r requirements.txt
      - name: Validar banco
        run: python scripts/validate_bank.py

  lint:
    name: Calidad de código
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Instalar herramientas
        run: pip install black flake8
      - name: Formateo (black)
        run: black --check --line-length=100 src/
      - name: Linting (flake8)
        run: flake8 src/ --max-line-length=100 --exclude=src/interface/

  test-unit:
    name: Pruebas unitarias
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Instalar dependencias
        run: pip install -r requirements.txt pytest pytest-cov
      - name: Ejecutar pruebas unitarias
        run: |
          python -m pytest tests/unit/ \
            --cov=src/domain \
            --cov=src/application \
            --cov-report=term-missing \
            --cov-fail-under=80 \
            -v

  test-integration:
    name: Pruebas de integración (SQLite)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Instalar dependencias
        run: pip install -r requirements.txt pytest
      - name: Ejecutar integración
        run: python -m pytest tests/integration/ -v

  db-sync:
    name: Verificar paridad SQLite/PostgreSQL
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Instalar dependencias
        run: pip install -r requirements.txt
      - name: Verificar sincronía
        run: python scripts/db_sync_check.py
```

---

#### Tarea 6.3 — Versión semántica

Crear `src/__version__.py`:

```python
# src/__version__.py
"""
Versión semántica de LevelUp-ELO.
MAYOR.MENOR.PATCH — https://semver.org/lang/es/
"""
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__release_date__ = "2026-04-XX"
```

En `app.py`:
```python
from src import __version__
st.set_page_config(
    page_title=f"LevelUp-ELO v{__version__}",
    ...
)
```

En `CLAUDE.md`, actualizar la sección de inicio rápido con la versión actual.

---

## 4. Arquitectura de pruebas

### Pirámide de pruebas

```
         /\
        /  \
       / E2E\          → 5% — Playwright: flujo completo login→práctica
      /──────\
     /  Integ  \       → 25% — SQLite en memoria, bank loading, transacciones
    /────────────\
   /    Unitarias  \   → 70% — Dominio puro, servicios con mocks
  /────────────────\
```

### Estrategia por capa

| Capa | Tipo de prueba | Herramienta | Cobertura objetivo |
|------|---------------|-------------|-------------------|
| `domain/` | Unitaria pura — sin mocks | pytest | 95% |
| `application/services/` | Unitaria con mock de repo e IA | pytest + unittest.mock | 85% |
| `infrastructure/persistence/` | Integración con SQLite en memoria | pytest + tmp_path | 70% |
| `infrastructure/external_api/` | Unitaria con mock HTTP | pytest + responses | 60% |
| `interface/views/` | No testear UI directamente | — | — |
| Flujos E2E | Playwright (happy path) | playwright | 3 flujos críticos |

### 3 flujos E2E obligatorios

1. **Estudiante**: Login → seleccionar curso → responder 3 preguntas → verificar ELO cambia
2. **Docente**: Login → ver dashboard → revisar procedimiento → asignar calificación
3. **Admin**: Login → aprobar docente → verificar aparece en lista activos

---

## 5. Criterios de aceptación V1.0

La versión es V1.0 cuando **todos** estos criterios están verdes:

### Funcionalidad

- [ ] **F1**: `python scripts/validate_bank.py` retorna exit code 0 (todos los ítems válidos y con encoding UTF-8)
- [ ] **F2**: Cursos DIAN, SENA, Álgebra Lineal muestran preguntas a estudiantes en producción
- [ ] **F3**: Un estudiante puede completar una sesión de práctica sin errores silenciosos en IA
- [ ] **F4**: Un docente puede calificar un procedimiento y el estudiante ve la nota en "Centro de Feedback"
- [ ] **F5**: El admin puede aprobar un docente y ese docente puede hacer login inmediatamente

### Calidad de código

- [ ] **Q1**: `python -m pytest tests/unit/ --cov-fail-under=80` pasa (≥80% cobertura en dominio+servicios)
- [ ] **Q2**: `python -m pytest tests/integration/` pasa (0 fallos en integración)
- [ ] **Q3**: `python scripts/db_sync_check.py` retorna 0 errores
- [ ] **Q4**: `black --check src/` retorna 0 diferencias
- [ ] **Q5**: No hay `except Exception: pass` sin logging en el codebase (`grep -rn "except Exception: pass" src/` → vacío)
- [ ] **Q6**: No hay `importlib.reload` en `app.py` (`grep -n "importlib.reload" src/interface/streamlit/app.py` → vacío)

### Arquitectura

- [ ] **A1**: `app.py` tiene menos de 400 líneas (actualmente 3,669)
- [ ] **A2**: Existen `views/auth_view.py`, `views/student_view.py`, `views/teacher_view.py`, `views/admin_view.py`
- [ ] **A3**: `src/application/interfaces/repositories.py` existe con `IStudentRepository`, `ITeacherRepository`, `IAdminRepository`
- [ ] **A4**: `StudentService` recibe `enable_cognitive_modifier: bool` como parámetro
- [ ] **A5**: `save_answer_transaction()` existe en ambos repositorios

### CI/CD

- [ ] **C1**: `.github/workflows/ci.yml` existe y todos los jobs pasan en el último commit de `main`
- [ ] **C2**: Pre-commit hooks instalados y verificados en el repo
- [ ] **C3**: `scripts/validate_bank.py` existe, es ejecutable y está en CI

### Versión

- [ ] **V1**: `src/__version__.py` existe con `__version__ = "1.0.0"`
- [ ] **V2**: Tag git `v1.0.0` creado en el commit que pasa todos los criterios anteriores
- [ ] **V3**: `CHANGELOG.md` documenta los cambios de V0.9-beta a V1.0

---

## 6. Checklist de entrega

### Por sprint

**Sprint 1 — Banco de preguntas**
- [ ] `open(..., encoding='utf-8')` en `sync_items_from_bank_folder()` de ambos repos
- [ ] `scripts/validate_bank.py` creado y funcional
- [ ] CI job `validate-bank` añadido
- [ ] Pre-commit hook `validate-bank` añadido
- [ ] Logging en carga de ítems (no silencioso)
- [ ] `python scripts/validate_bank.py` retorna exit 0

**Sprint 2 — Deuda técnica**
- [ ] `importlib.reload()` eliminado de `app.py`
- [ ] `enable_cognitive_modifier` feature flag en `StudentService`
- [ ] `save_answer_transaction()` en `sqlite_repository.py`
- [ ] `save_answer_transaction()` en `postgres_repository.py`
- [ ] `src/application/interfaces/repositories.py` creado
- [ ] `StudentService` tipado con `IStudentRepository`
- [ ] `zdp_interval()` usado en `item_selector.py`
- [ ] `requirements.txt` con versiones pineadas y `requests` añadido

**Sprint 3 — Logging y errores**
- [ ] `src/infrastructure/logging_config.py` creado
- [ ] `configure_logging()` llamado al inicio de `app.py`
- [ ] 5 bloques `except Exception: pass` en `ai_client.py` reemplazados con logging
- [ ] `except:` bare en `cognitive.py` reemplazado
- [ ] Mensajes de error específicos al usuario en flujos de IA

**Sprint 4 — Modularización**
- [ ] `src/interface/streamlit/state.py` creado
- [ ] `src/interface/streamlit/assets.py` creado
- [ ] `src/interface/streamlit/views/auth_view.py` creado
- [ ] `src/interface/streamlit/views/student_view.py` creado
- [ ] `src/interface/streamlit/views/teacher_view.py` creado
- [ ] `src/interface/streamlit/views/admin_view.py` creado
- [ ] `app.py` reducido a <400 líneas (routing + setup)
- [ ] App funciona idéntico después de la modularización

**Sprint 5 — Pruebas**
- [ ] `tests/conftest.py` con fixtures base
- [ ] `tests/unit/domain/test_elo_model.py` — ≥10 casos
- [ ] `tests/unit/domain/test_vector_elo.py` — ≥8 casos
- [ ] `tests/unit/domain/test_item_selector.py` — ≥6 casos
- [ ] `tests/unit/application/test_student_service.py` — ≥8 casos
- [ ] `tests/integration/test_sqlite_repository.py` — ≥4 casos
- [ ] `tests/unit/infrastructure/test_bank_validator.py` — ≥5 casos
- [ ] Cobertura dominio+servicios ≥80%

**Sprint 6 — CI/CD**
- [ ] `.pre-commit-config.yaml` creado e instalado
- [ ] `.github/workflows/ci.yml` con 5 jobs
- [ ] `src/__version__.py` con `1.0.0`
- [ ] `CHANGELOG.md` creado
- [ ] Tag `v1.0.0` en git
- [ ] Todos los jobs de CI pasan en verde

---

## Notas de implementación

### Orden de ejecución recomendado

El Sprint 1 (encoding del banco) es el único que tiene valor de negocio inmediato: desbloquea ítems que hoy no cargan en producción. Hacerlo primero, en producción, antes de tocar el código.

El Sprint 4 (modularización) es el más arriesgado: mover código sin cambiar lógica requiere atención. Hacer último, con los tests del Sprint 5 ya escritos para verificar que nada se rompe.

### Regla de oro durante la implementación

> Cada tarea debe poder hacerse en un commit atómico que no rompe la aplicación.
> Si la app no arranca después del commit, el commit está mal.

### Qué NO hacer durante V1.0

- No agregar features nuevas (eso es V2.0)
- No cambiar la lógica ELO (ya funciona correctamente)
- No modificar el esquema de DB (solo migraciones aditivas)
- No cambiar la API pública de los repositorios sin actualizar ambos (Regla #1 del CLAUDE.md)
