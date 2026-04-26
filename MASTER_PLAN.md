# MASTER PLAN — LevelUp-ELO
# Plan unificado: V2 (calidad + pulido) + Motor ML (mejoras ELO)
# Última revisión: 2026-04-25
#
# ═══════════════════════════════════════════════════════════════
# PROTOCOLO OBLIGATORIO — leer ANTES de empezar cualquier tarea
# ═══════════════════════════════════════════════════════════════
#
# 1. CLAUDE.md                              (reglas del proyecto)
# 2. Los skills indicados en cada sección   (ver bloque READ_SKILLS)
# 3. python scripts/db_sync_check.py        (si la tarea toca repos)
#
# ⚠️  Nunca escribir código sin leer los skills de la sección.
#     Cada sección tiene un bloque READ_SKILLS con los archivos exactos.
# ═══════════════════════════════════════════════════════════════

---

## CONTEXTO

**Estado actual:**
- V2 (React + FastAPI): Sprints 1–6 completos, ~95% paridad con V1. Deploy activo en Vercel + Render.
- Motor ML: plan definido, 0% implementado.

**Dos líneas de trabajo independientes:**
- **Línea A — V2 calidad/producción**: Sprints 7–8. Hace V2 confiable para usuarios reales.
- **Línea B — Motor ML**: Fases 1–4. Mejora la precisión del motor ELO.

Ambas líneas se pueden ejecutar en paralelo. La Línea B Fase 1 es **urgente** antes de la próxima sesión del Semillero.

---

## PRIORIDADES GLOBALES

```
P0  URGENTE     — antes próxima sesión Semillero
P1  ESTA SEMANA — producción lista y motor limpio
P2  PRÓXIMA     — V2 confiable + examen
P3  CON UMBRAL  — requiere N estudiantes ≥ 100
P4  DESEABLE    — pulido fino y largo plazo
```

---

## P0 — URGENTE (antes próxima sesión Semillero)

### [ML-1] Filtro de outliers time_taken → flag elo_valid

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md
  2. .claude/skills/ml-improvements/SKILL.md
  3. .claude/skills/item-calibration/SKILL.md
  4. .claude/skills/db-dual-backend.md
```

**Esfuerzo:** 1–2 h
**Por qué ahora:** limpia los datos de entrada para todo el pipeline ML. Sin esto, intentos de <3s (adivinanzas) y >600s (sesiones abandonadas) contaminan el ELO.

#### Archivos a tocar
```
src/infrastructure/persistence/sqlite_repository.py    (Regla R1: siempre los dos)
src/infrastructure/persistence/postgres_repository.py
```

#### Tareas
```
1. _migrate_db():
   ALTER TABLE attempts ADD COLUMN IF NOT EXISTS elo_valid INTEGER DEFAULT 1;

2. Método nuevo en ambos repos:
   def _tiempo_valido(self, time_taken: float) -> bool:
       return 3.0 <= time_taken <= 600.0
   # Fuera de rango = adivinanza (<3s) o sesión abandonada (>600s)

3. save_answer_transaction() en ambos repos:
   - Siempre: INSERT attempt con elo_valid = _tiempo_valido(time_taken)
   - Solo si elo_valid=True: UPDATE users ELO + UPDATE items difficulty
   - Si elo_valid=False: insertar intento igual, pero NO actualizar ELO

4. Método nuevo en ambos repos:
   def get_all_attempts_for_calibration(
       self,
       education_level: str = None,
       exclude_test_users: bool = True
   ) -> list[dict]:
       # SELECT a.id, a.user_id, a.item_id, a.is_correct,
       #        a.expected_score, a.elo_valid, a.time_taken,
       #        u.education_level
       # FROM attempts a JOIN users u ON a.user_id = u.id
       # WHERE a.elo_valid = 1
       #   AND (NOT exclude OR COALESCE(u.is_test_user,0)=0)
       #   AND (education_level IS NULL OR u.education_level = ?)
       # ORDER BY a.attempt_timestamp
```

#### Verificación
```bash
python scripts/db_sync_check.py        # 0 diferencias
pytest tests/unit/ -v                  # todos pasan
# Manual:
#   time=1s   → elo_valid=0, ELO sin cambio ✓
#   time=700s → elo_valid=0, ELO sin cambio ✓
#   time=45s  → elo_valid=1, ELO actualiza  ✓
```

#### Post-implementación
Crear `.claude/skills/data-quality/SKILL.md` con reglas de filtros para queries de análisis.

---

## P1 — ESTA SEMANA

### [ML-2] Isotonic Regression: corrección de sesgo sistemático

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md
  2. .claude/skills/ml-improvements/SKILL.md
  3. .claude/skills/calibration-ml/SKILL.md  (créalo si no existe tras ML-1)
  4. .claude/skills/data-quality/SKILL.md    (créalo si no existe tras ML-1)
```

**Prerequisito:** ML-1 completo
**Esfuerzo:** 2–3 h
**Impacto:** sesgo global pasa de +0.165 a <0.05 sin cambiar motor ELO

#### Archivos a crear / tocar
```
src/domain/elo/calibration.py          (nuevo)
scripts/train_calibrator.py            (nuevo)
scripts/monthly_metrics.py             (nuevo)
src/application/services/student_service.py
models/                                (nuevo directorio + .gitkeep)
.gitignore                             (models/*.pkl)
```

#### Tareas

**1. `src/domain/elo/calibration.py` — clase IsotonicCalibrator**
```python
class IsotonicCalibrator:
    MODEL_PATH = "models/isotonic_calibrator.pkl"

    def __init__(self): self._model = None; self._trained = False

    def load(self) -> bool:
        # Carga con pickle. Returns False silenciosamente si no existe.
        # Nunca lanza excepción.

    def predict(self, p_raw: float) -> float:
        # Returns p_raw si modelo no cargado.
        # Output clamped a [0.001, 0.999].
        # Nunca lanza excepción.

    def train_and_save(self, y_true, y_pred) -> dict:
        # IsotonicRegression(out_of_bounds='clip') de sklearn
        # Guarda en MODEL_PATH con pickle
        # Returns {'auc_before','auc_after','bias_before','bias_after'}

    @property
    def is_active(self) -> bool: return self._trained
```

**2. `scripts/train_calibrator.py`**
```
python scripts/train_calibrator.py
python scripts/train_calibrator.py --level semillero
python scripts/train_calibrator.py --level colegio

Pasos:
  1. Cargar intentos vía repo.get_all_attempts_for_calibration()
  2. Imprimir: N intentos, AUC, sesgo, log-loss (antes)
  3. Entrenar IsotonicCalibrator
  4. Imprimir: AUC (debe ser igual ±0.001), sesgo (<0.05)
  5. Guardar a models/isotonic_calibrator_{level}.pkl
  6. Exit con error si N < 50
```

**3. `scripts/monthly_metrics.py`**
```
python scripts/monthly_metrics.py

Imprime:
  - Fecha y N intentos (filtrado: elo_valid=1, is_test_user=0)
  - AUC global y por nivel (semillero/colegio/universidad)
  - Sesgo global
  - Log-loss global
  - Ítems con success_rate=0% y ≥10 intentos
  - Estado del calibrador (activo / no entrenado)
```

**4. Integración `student_service.py`**
```python
# En __init__:
from src.domain.elo.calibration import IsotonicCalibrator
self._calibrator = IsotonicCalibrator()
self._calibrator.load()

# En process_answer():
p_raw = expected_score(student_elo, item_difficulty)
p_calibrated = self._calibrator.predict(p_raw)
# ELO delta SIEMPRE usa p_raw (nunca el valor calibrado)
delta = K * (actual - p_raw)
# Guardar p_calibrated en attempts.expected_score (lo que ve el dashboard)
```

#### Verificación
```bash
python scripts/db_sync_check.py
python scripts/train_calibrator.py          # imprime métricas
python scripts/monthly_metrics.py           # imprime reporte
pytest tests/unit/ -v
# Test obligatorio: calibrador sin archivo → returns p_raw sin cambio
```

#### Post-implementación
Crear `.claude/skills/calibration-ml/SKILL.md`.

---

### [V2-7.2] Code splitting por ruta (React.lazy)

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2 — reglas V2-R1 a V2-R9)
```

**Esfuerzo:** 1–2 h
**Impacto:** bundle inicial ~200 kB (ahora monolítico)

```
Archivo: frontend/src/App.tsx

Cambio: lazy-load cada página con React.lazy + Suspense
const Practice = React.lazy(() => import('./pages/Student/Practice'))
const Stats    = React.lazy(() => import('./pages/Student/Stats'))
const Dashboard = React.lazy(() => import('./pages/Teacher/Dashboard'))
// ...todas las rutas

Envolver en <Suspense fallback={<PageSkeleton />}>
```

---

### [V2-7.3] Error boundaries + pantalla de error amigable

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2)
```

**Esfuerzo:** 1–2 h

```
Archivo nuevo: frontend/src/components/ui/ErrorBoundary.tsx
  - class ErrorBoundary extends React.Component
  - Muestra pantalla de error con botón "Recargar"
  - Mensaje amigable en español

Aplicar en: frontend/src/App.tsx
  Envolver rutas en <ErrorBoundary>
```

---

### [V2-7.4] Skeleton loaders reemplazan "Cargando..."

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2, paleta de colores)
  2. .claude/skills/impeccable/SKILL.md
  3. .claude/skills/design-taste-frontend/SKILL.md
```

**Esfuerzo:** 2–3 h

```
Archivo nuevo: frontend/src/components/ui/Skeleton.tsx
  - SkeletonLine, SkeletonCard, SkeletonChart

Aplicar en:
  frontend/src/pages/Student/Stats.tsx       (radar + heatmap)
  frontend/src/pages/Teacher/Dashboard.tsx   (tabla + gráfico ELO)
  frontend/src/pages/Student/Courses.tsx     (tarjetas de curso)
```

---

## P2 — PRÓXIMA SEMANA

### [V2-7.1] Tests E2E con Playwright

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2 — usuarios de prueba, endpoints, reglas V2-R9)
```

**Esfuerzo:** 4–6 h

```
Archivos nuevos:
  tests/e2e/login.spec.ts
  tests/e2e/practice.spec.ts
  tests/e2e/stats.spec.ts
  tests/e2e/procedure.spec.ts
  playwright.config.ts

Flujos a cubrir:
  - Login estudiante + práctica completa (responder pregunta)
  - Login docente + ver dashboard + calificar procedimiento
  - Registro nuevo estudiante
  - Login admin + aprobar docente

CI: agregar job playwright al workflow de GitHub Actions
```

---

### [V2-7.5] Tests integración rutas protegidas

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección Seguridad y V2 — JWT, RequireAuth, roles)
```

**Esfuerzo:** 2–3 h

```
Archivos nuevos/a modificar:
  tests/api/test_auth_flow.py
    - GET /protected sin token → 401
    - GET /teacher/* con token estudiante → 403
    - JWT expirado → 401
    - Refresh token → nuevo access token

  frontend/tests/RequireAuth.test.tsx (Vitest)
    - Redirige a /login si no hay token
    - Muestra contenido si hay token válido
```

---

### [V2-8.1] Modo examen end-to-end

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2 — reglas V2-R9 "respuesta correcta nunca al frontend",
                 Seguridad, Archivos clave V2)
  2. .claude/skills/impeccable/SKILL.md
  3. .claude/skills/design-taste-frontend/SKILL.md
  4. .claude/skills/emil-design-eng/SKILL.md  (timer, animaciones)
  5. .claude/skills/db-dual-backend.md        (tabla exam_sessions en ambos repos)
```

**Esfuerzo:** 6–8 h (feature completo)

```
Archivos a crear/tocar:
  frontend/src/pages/Student/Exam.tsx     (nuevo)
  api/routers/student.py                  (endpoints exam)
  frontend/src/App.tsx                    (ruta /exam)

Flujo:
  1. Selector: elegir curso(s) + N preguntas (5/10/20/personalizado)
  2. Timer global visible (no por pregunta)
  3. Sin preview ELO durante el examen
  4. Respuesta correcta NO viaja al frontend (V2-R9)
  5. Al terminar: resumen de puntaje, sin revelar respuestas correctas
  6. ELO se actualiza al finalizar (no por pregunta)
  7. Guardar resultado en tabla exam_sessions (si no existe: crear)

Endpoints API:
  POST /student/exam/start    → {exam_id, items[]}
  POST /student/exam/submit   → {exam_id, answers[]} → {score, elo_delta}
```

---

## P3 — CON UMBRAL (N estudiantes ≥ 100)

### [ML-3] Clustering de estudiantes → K factor personalizado

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md
  2. .claude/skills/ml-improvements/SKILL.md
  3. .claude/skills/calibration-ml/SKILL.md
  4. .claude/skills/data-quality/SKILL.md
  5. .claude/skills/student-profiling/SKILL.md  (créalo si no existe tras ML-2)
```

**Prerequisitos:** ML-1 + ML-2 completos, N ≥ 100 estudiantes activos
**Esfuerzo:** 4–6 h

**Verificar antes de empezar:**
```bash
python scripts/monthly_metrics.py   # confirmar N estudiantes únicos ≥ 100
```

#### Tareas

**1. `src/domain/elo/student_profiler.py`**
```python
class StudentProfiler:
    N_CLUSTERS = 3
    K_MODIFIERS = {0: 1.3, 1: 1.0, 2: 0.8}
    # 0 = bajo rendimiento  → K×1.3 (converge rápido)
    # 1 = rendimiento medio → K×1.0 (estándar)
    # 2 = alto rendimiento  → K×0.8 (más estable)

    # Features de clustering (4 dimensiones):
    #   tasa_acierto (0-1)
    #   elo_medio    (normalizado)
    #   n_intentos   (cap: 200)
    #   rd_final     (float)

    def fit(self, student_data: list[dict]) -> None
    def predict_profile(self, student_stats: dict) -> int   # 0/1/2
    def k_modifier(self, profile: int) -> float
    def save(self, path="models/student_profiler.pkl") -> None
    def load(self, path="models/student_profiler.pkl") -> bool
    # Si modelo no entrenado → predict_profile retorna 1 (graceful degradation)
```

**2. `scripts/train_profiler.py`**
```
Carga stats agregados por estudiante (is_test_user=0, elo_valid=1, n_intentos≥10)
Entrena StudentProfiler (KMeans + StandardScaler)
Mapea clusters por tasa_acierto (0=lowest)
Guarda models/student_profiler.pkl
Imprime tamaños de cluster y tasa_acierto media por cluster
Exit con mensaje si < 30 estudiantes válidos
```

**3. Integración `src/domain/elo/vector_elo.py`**
```python
def update(self, topic, expected, actual, k_base,
           impact_modifier=1.0, k_modifier=1.0):
    k_eff = k_base * (rd / RD_BASE) * impact_modifier * k_modifier
```

**4. Integración `student_service.py`**
```python
# En __init__: cargar StudentProfiler
# En process_answer(): predecir profile + k_mod, pasar a vector.update()
```

#### Verificación
```bash
python scripts/train_profiler.py    # 3 clusters con tamaños
# Cluster 0: low tasa_acierto, K×1.3
# Cluster 1: medium,           K×1.0
# Cluster 2: high tasa_acierto, K×0.8
# Sin k_modifier → behavior idéntico al actual
```

#### Post-implementación
Crear `.claude/skills/student-profiling/SKILL.md`.

---

## P4 — DESEABLE / LARGO PLAZO

### [V2-8.2] Accesibilidad

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2)
  2. .claude/skills/audit/SKILL.md  (si existe — auditoría a11y)
  3. .claude/skills/impeccable/SKILL.md
```

**Esfuerzo:** 3–4 h

```
- aria-labels en todos los botones icono-only
- Focus states visibles (outline visible en tab navigation)
- Navegación por teclado en AnswerOptions.tsx y modales
- Auditoría con axe-core: npx axe http://localhost:5173
Archivos: Layout.tsx, AnswerOptions.tsx, todos los modales
```

---

### [V2-8.3] Tema claro / oscuro

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2 — paleta de colores, tokens CSS)
  2. .claude/skills/design-taste-frontend/SKILL.md
  3. .claude/skills/impeccable/SKILL.md
```

**Esfuerzo:** 6–8 h (costo alto, pospuesto de Sprint 5.6)

```
- ThemeToggle.tsx: toggle con persistencia en localStorage
- Estrategia: class="dark" en <html> + Tailwind dark: prefix
- Refactor ~40 componentes para usar CSS variables
- Variables CSS en frontend/src/index.css (ya tiene paleta V2)
Archivos: ThemeToggle.tsx, App.tsx, index.css + todos los componentes
```

---

### [V2-8.5] Métricas de uso en dashboard docente

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2 — Dashboard.tsx, reglas V2-R1/R2)
  2. .claude/skills/db-dual-backend.md
  3. .claude/skills/impeccable/SKILL.md
  4. .claude/skills/design-taste-frontend/SKILL.md
```

**Esfuerzo:** 3–4 h

```
Tab "Métricas" en Dashboard.tsx:
  - Tiempo promedio por pregunta (por estudiante y por curso)
  - Tasa de abandono de sesiones
  - Distribución de tiempo_taken (histograma)
  - Top 5 ítems con mayor tasa de error

Endpoint nuevo: GET /teacher/metrics?group_id=X&course_id=Y
Archivos: api/routers/teacher.py, frontend/src/pages/Teacher/Dashboard.tsx
```

---

### [V2-8.4] Internacionalización es/en (opcional)

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md  (sección V2)
```

**Esfuerzo:** 4–6 h
**Condición:** solo si hay demanda real de usuarios en inglés

```
- react-i18next + carpeta i18n/
- Traducciones: es.json + en.json
- Selector de idioma en sidebar
```

---

### [ML-4] IRT 2PL para Semillero

```
READ_SKILLS — leer en este orden antes de escribir una sola línea:
  1. CLAUDE.md
  2. .claude/skills/ml-improvements/SKILL.md
  3. .claude/skills/item-calibration/SKILL.md
  4. .claude/skills/calibration-ml/SKILL.md
  5. .claude/skills/data-quality/SKILL.md
  6. .claude/skills/irt-calibration/SKILL.md  (créalo si no existe tras ML-3)
  7. .claude/skills/student-profiling/SKILL.md
```

**Prerequisitos:** ML-1, ML-2, ML-3 completos
**Condición:** N intentos Semillero con elo_valid=1 ≥ 3.000
**Esfuerzo:** 1–2 semanas

**Verificar antes de empezar:**
```bash
python scripts/monthly_metrics.py   # confirmar N intentos Semillero ≥ 3.000
```

**Modelo IRT 2PL:**
```
P(correcto | θ, a, b) = 1 / (1 + exp(-a(θ - b)))
θ = habilidad estudiante = (R_elo - 1000) / 400
b = dificultad ítem     = (D_elo - 1000) / 400
a = discriminación      (parámetro nuevo, ≥ 0.5 para ítem bueno)
```

#### Tareas

**1. `scripts/calibrate_irt_semillero.py`**
```
1. Cargar intentos Semillero (is_test_user=0, elo_valid=1)
2. Ajustar IRT 2PL con pyirt: irt(data, model='2PL', max_iter=200)
3. Extraer a y b por ítem
4. Generar reporte: VALIDACION_ELO/irt_calibration_report.csv
   - Items con a < 0.5 → candidatos a revisión/retiro
   - Items con |D_irt - D_elo| > 200 → candidatos a recalibración
5. Generar SQL para review manual (NO actualizar automáticamente)
```

**2. `src/domain/elo/irt_adapter.py`**
```python
class IRT2PLAdapter:
    def predict(self, theta: float, item_id: str) -> float | None:
        # Retorna P(correcto) si hay params IRT para el ítem
        # Retorna None si no hay params → caller usa fórmula ELO
    def load(self, path="models/irt_params_semillero.json") -> bool
```

**3. Integración `student_service.py` (Semillero only)**
```python
if student.education_level == 'semillero':
    p_irt = self._irt_adapter.predict(theta, item_id)
    expected = p_irt if p_irt is not None else expected_score(R, D)
```

**4. Dependencia: `pip install pyirt>=0.3.0`** (agregar a requirements.txt)

#### Verificación
```bash
python scripts/calibrate_irt_semillero.py   # genera CSV
# IRT2PLAdapter sin archivo → retorna None (usa ELO fallback)
# python scripts/monthly_metrics.py → AUC Semillero ≥ 0.68
```

#### Post-implementación
Crear `.claude/skills/irt-calibration/SKILL.md`.

---

## RESUMEN DE TAREAS

| ID | Descripción | Prioridad | Esfuerzo | Estado |
|---|---|---|---|---|
| ML-1 | Filtro elo_valid outliers time_taken | P0 URGENTE | 1–2 h | ✅ 2026-04-25 |
| ML-2 | Isotonic Regression + monthly_metrics | P1 | 2–3 h | ✅ 2026-04-25 |
| V2-7.2 | Code splitting React.lazy | P1 | 1–2 h | ✅ 2026-04-25 |
| V2-7.3 | Error boundaries | P1 | 1–2 h | ✅ 2026-04-25 |
| V2-7.4 | Skeleton loaders | P1 | 2–3 h | ❌ |
| V2-7.1 | Tests E2E Playwright | P2 | 4–6 h | ❌ |
| V2-7.5 | Tests integración rutas protegidas | P2 | 2–3 h | ❌ |
| V2-8.1 | Modo examen end-to-end | P2 | 6–8 h | ❌ |
| ML-3 | Clustering estudiantes + K modifier | P3 (N≥100) | 4–6 h | ❌ |
| V2-8.2 | Accesibilidad (aria, focus, keyboard) | P4 | 3–4 h | ❌ |
| V2-8.3 | Tema claro/oscuro | P4 | 6–8 h | ❌ |
| V2-8.5 | Métricas de uso dashboard docente | P4 | 3–4 h | ❌ |
| V2-8.4 | Internacionalización es/en (opcional) | P4 | 4–6 h | ❌ |
| ML-4 | IRT 2PL Semillero (N≥3000 intentos) | P4 | 1–2 sem | ❌ |

**Total esfuerzo estimado P0+P1+P2:** ~25–37 h
**Total esfuerzo P0–P4 sin ML-4:** ~40–55 h

---

## DEPENDENCIAS ENTRE TAREAS

```
ML-1 ──────────────► ML-2 ──────► ML-3 ──► ML-4
                                   (N≥100)   (N≥3000)

V2-7.2 ┐
V2-7.3 ├── independientes entre sí
V2-7.4 ┘

V2-7.1 ┐
V2-7.5 ├── mejor después de V2-7.2/7.3/7.4
V2-8.1 ┘
```

---

## SKILLS NECESARIOS DURANTE EL PLAN

| Skill | Cuándo |
|---|---|
| `.claude/skills/ml-improvements/SKILL.md` | ML-1, ML-2, ML-3, ML-4 |
| `.claude/skills/item-calibration/SKILL.md` | ML-1, ML-4 |
| `.claude/skills/db-dual-backend.md` | ML-1 (toca repos) |
| `.claude/skills/db-sync-checker.md` | Tras ML-1 |
| `.claude/skills/impeccable/` | V2-7.4, V2-8.1, V2-8.2 |
| `.claude/skills/design-taste-frontend/` | V2-8.1 (Exam.tsx) |

---

## VERIFICACIÓN GLOBAL — ejecutar al terminar cualquier tarea

```bash
python scripts/db_sync_check.py                          # 0 diferencias
pytest tests/unit/ tests/integration/ -v                 # todos pasan
flake8 src/ api/ --max-line-length=100 --select=E9,F63,F7,F82
cd frontend && npm run build                             # TypeScript sin errores
```
