---
name: clean-architecture
description: >
  Guía de arquitectura para LevelUp-ELO. Usar SIEMPRE que la tarea involucre:
  crear módulos nuevos, agregar servicios de aplicación, extender la lógica
  ELO o cognitiva, crear nuevos casos de uso, agregar proveedores de IA,
  refactorizar código existente entre capas, o cuando no estés seguro de
  en qué capa va una pieza de lógica nueva. También usar si encuentras imports
  cruzados sospechosos entre capas.
---

# Skill: clean-architecture

## Las cuatro capas

```
src/
├── domain/          ← reglas de negocio puras
├── application/     ← casos de uso (orquestación)
├── infrastructure/  ← implementaciones concretas (DB, IA, seguridad)
└── interface/       ← UI (Streamlit)
```

### Regla de dependencias

Las dependencias solo apuntan **hacia adentro**:

```
interface → application → domain
infrastructure → domain (implementa interfaces)
```

**Lo que esto significa en la práctica:**

| Capa | Puede importar | NUNCA importar |
|---|---|---|
| `domain/` | nada externo, solo stdlib | `application/`, `infrastructure/`, `interface/` |
| `application/` | `domain/` | `infrastructure/` directamente, `interface/` |
| `infrastructure/` | `domain/` | `application/`, `interface/` |
| `interface/` | `application/`, `infrastructure/` | — |

---

## ¿Dónde va cada cosa nueva?

### Lógica de negocio → `domain/`

Va en domain si:
- Es una regla del sistema ELO (cálculo de K, delta de rating, ZDP)
- Es independiente de cualquier tecnología (sin DB, sin HTTP, sin Streamlit)
- Podría usarse en un contexto completamente distinto (tests unitarios puros)

```
domain/elo/          → fórmulas ELO, VectorRating, RatingModel, CognitiveAnalyzer
domain/selector/     → AdaptiveItemSelector, Fisher Information
```

**Ejemplo correcto:** una nueva fórmula de ajuste de RD va en `domain/elo/uncertainty.py`.

### Caso de uso nuevo → `application/services/`

Va en application si:
- Orquesta múltiples componentes del dominio
- Coordina dominio + repositorio (sin implementar el repo)
- Representa una acción del usuario de alto nivel

```
application/services/student_service.py  → process_answer, get_next_question
application/services/teacher_service.py  → análisis de dashboard, reportes IA
```

**Ejemplo correcto:** "calcular el ranking histórico de un estudiante" es un caso de uso — va en `teacher_service.py` o un nuevo service.

### Implementación concreta → `infrastructure/`

Va en infrastructure si:
- Habla con una DB (SQL, queries, migrations)
- Llama a una API externa (OpenAI, Groq, Anthropic)
- Hace I/O de archivos, hashing, OCR
- Implementa una interfaz definida en domain o application

```
infrastructure/persistence/     → repositorios SQLite y PostgreSQL
infrastructure/external_api/    → clientes IA, OCR, verificación simbólica
infrastructure/security/        → hashing de contraseñas
```

### UI y presentación → `interface/streamlit/`

Va en interface si:
- Renderiza componentes de Streamlit
- Maneja `st.session_state`
- Traduce acciones del usuario en llamadas a application/services

`app.py` es intencionalmente monolítico. No crear archivos auxiliares en esta capa sin necesidad.

---

## Módulos existentes — no duplicar

Antes de crear algo nuevo, revisar si ya existe:

| Necesidad | Módulo existente |
|---|---|
| Llamar a cualquier proveedor de IA | `infrastructure/external_api/ai_client.py` |
| Elegir el mejor modelo por tarea | `infrastructure/external_api/model_router.py` |
| Detectar capacidades de un modelo | `infrastructure/external_api/model_capability_detector.py` |
| Verificar equivalencias algebraicas | `infrastructure/external_api/symbolic_math_verifier.py` |
| OCR de expresiones matemáticas | `infrastructure/external_api/math_ocr.py` |
| Extraer pasos matemáticos de texto | `infrastructure/external_api/math_step_extractor.py` |
| Feedback socrático por tipo de error | `infrastructure/external_api/pedagogical_feedback.py` |
| Pipeline completo OCR→verificación | `infrastructure/external_api/math_analysis_pipeline.py` |
| Hashear / verificar contraseñas | `infrastructure/security/hashing_service.py` |
| ELO vectorial por tópico | `domain/elo/vector_elo.py` → `VectorRating` |
| Factor K dinámico | `domain/elo/model.py` |
| Rating Deviation (Glicko) | `domain/elo/uncertainty.py` → `RatingModel` |
| Clasificar respuesta del estudiante | `domain/elo/cognitive.py` → `CognitiveAnalyzer` |
| Seleccionar siguiente pregunta | `domain/selector/item_selector.py` → `AdaptiveItemSelector` |

---

## Extender el sistema ELO

Si necesitas modificar el comportamiento del ELO:

### Modificar el factor K
→ `domain/elo/model.py`, función `dynamic_k_factor()`. Lógica actual:
```python
K=40 (< 30 intentos) → K=32 (ELO < 1400) → K=16 (estable) → K=24 (default)
K_eff = K_BASE × (RD / RD_BASE)
```

### Modificar el Rating Deviation
→ `domain/elo/uncertainty.py`, clase `RatingModel`.
Valores actuales: RD inicial=350, mín=30, decay=RD×0.95 por intento.

### Modificar la selección de preguntas
→ `domain/selector/item_selector.py`, clase `AdaptiveItemSelector`.
ZDP actual: P(éxito) ∈ [0.4, 0.75]. Fisher Information = P×(1−P).

### Modificar el análisis cognitivo
→ `domain/elo/cognitive.py`, clase `CognitiveAnalyzer`.
Clasifica confianza [0,1] y tipo de error (`conceptual`/`superficial`).
`impact_modifier` ∈ [0.5, 1.5] escala el delta ELO.

---

## Agregar un proveedor de IA nuevo

1. Identificar el prefijo de API key del nuevo proveedor.
2. En `infrastructure/external_api/ai_client.py` → agregar detección en la función de auto-detect.
3. En `infrastructure/external_api/model_capability_detector.py` → agregar heurísticas de nombre si aplica.
4. En `infrastructure/external_api/model_router.py` → agregar al registro manual si el proveedor tiene modelos especializados.
5. Verificar que el nuevo proveedor tenga fallback graceful (no lanzar excepciones que rompan el flujo del estudiante).

---

## Agregar un servicio de aplicación nuevo

1. Crear el archivo en `application/services/mi_servicio.py`.
2. El servicio recibe el repositorio por inyección (parámetro en `__init__` o en el método).
3. El servicio NO importa `sqlite_repository` ni `postgres_repository` directamente.
4. Llamar al servicio desde `interface/streamlit/app.py`.

```python
# CORRECTO
class MiServicio:
    def __init__(self, repository):
        self.repo = repository   # inyectado desde app.py

    def hacer_algo(self, user_id: int) -> dict:
        data = self.repo.get_user_data(user_id)
        # lógica de dominio aquí
        return result

# INCORRECTO
from infrastructure.persistence.sqlite_repository import SQLiteRepository

class MiServicio:
    def __init__(self):
        self.repo = SQLiteRepository()   # acopla infrastructure a application
```

---

## Señales de alerta — código en la capa equivocada

Si encuentras alguno de estos patrones, la lógica está en el lugar incorrecto:

| Patrón | Problema | Solución |
|---|---|---|
| SQL en `domain/` | domain no puede tener I/O | mover a `infrastructure/persistence/` |
| Cálculo ELO en `app.py` | lógica de negocio en UI | mover a `domain/elo/` |
| `import streamlit` en `domain/` o `application/` | dependencia hacia afuera | extraer a `interface/` |
| `import sqlite3` en `application/` | application no implementa repos | usar inyección de dependencias |
| Lógica de negocio en un repositorio | repositorios son solo I/O | extraer a un service o domain |
| Llamada a API externa en `domain/` | domain debe ser puro | mover a `infrastructure/external_api/` |

---

## Flujo de datos completo (referencia)

```
app.py (interface)
  └→ StudentService.process_answer() (application)
       ├→ CognitiveAnalyzer.analyze_cognition() (domain)
       │    └→ ai_client.complete() (infrastructure) ← única salida permitida desde domain
       ├→ VectorRating.update() (domain)
       ├→ repository.update_item_rating() (infrastructure via interface de domain)
       └→ repository.save_attempt() (infrastructure)
```

La única excepción al aislamiento de domain es `CognitiveAnalyzer`, que llama a IA como dependencia inyectada — no importa `ai_client` directamente.
