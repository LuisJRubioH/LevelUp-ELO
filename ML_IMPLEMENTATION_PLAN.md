# PLAN COMPLETO — Mejoras ML para LevelUp-ELO
# Entregar este archivo a Claude Code al inicio de cada fase.
# Claude Code debe leerlo completo antes de escribir una sola línea.

---

## ANTES DE EMPEZAR CUALQUIER FASE

```
Read these files in this exact order before any implementation:
1. CLAUDE.md
2. .claude/skills/ml-improvements/SKILL.md
3. .claude/skills/item-calibration/SKILL.md
```

Skills de diseño (solo si la fase toca frontend):
```
4. .claude/skills/impeccable/SKILL.md
5. .claude/skills/design-taste-frontend/SKILL.md
```

---

## PREREQUISITOS — Instalar una sola vez antes de la Fase 1

### Plugin recomendado: sequential-thinking

Ayuda a Claude Code a planificar tareas multi-paso sin perder contexto.
Instalar dentro de Claude Code:
```
/plugin marketplace add modelcontextprotocol/servers
/plugin install sequential-thinking
/reload-plugins
```

Si no aparece en el marketplace, alternativa manual:
```bash
# En la raíz del repo
npx @modelcontextprotocol/create-server sequential-thinking
```

### Dependencias Python para ML

Agregar a requirements.txt (y requirements-api.txt si aplica):
```
scikit-learn>=1.4.0
numpy>=1.26.0
pandas>=2.1.0
```

Para Fase 4 únicamente (IRT 2PL) — agregar cuando llegue el momento:
```
pyirt>=0.3.0
```

Instalar:
```bash
pip install scikit-learn numpy pandas
```

---

## FASE 1 — Calidad de datos: filtro de outliers en time_taken

**Cuándo**: AHORA — antes de la próxima sesión del Semillero
**Esfuerzo**: 1–2 horas
**Impacto**: limpia los datos de entrada para todo el pipeline ML siguiente

### Prompt para Claude Code

```
Read CLAUDE.md and .claude/skills/ml-improvements/SKILL.md before starting.

PHASE 1: time_taken filter — data quality improvement.
All DB changes in BOTH repositories (Rule R1).

TASK 1 — Migration
In _migrate_db() of sqlite_repository.py AND postgres_repository.py:
  ALTER TABLE attempts ADD COLUMN IF NOT EXISTS elo_valid INTEGER DEFAULT 1;

TASK 2 — Helper method in both repos
  def _tiempo_valido(self, time_taken: float) -> bool:
      """Valid range: [3s, 600s]. Outside = guess or abandoned session."""
      return 3.0 <= time_taken <= 600.0

TASK 3 — Modify save_answer_transaction() in both repos
  time_taken = attempt_data.get('time_taken', 30.0)
  elo_valido = self._tiempo_valido(time_taken)

  Always: INSERT attempt with elo_valid = 1 if elo_valido else 0
  Only if elo_valido=True: UPDATE users ELO, UPDATE items difficulty
  If elo_valido=False: skip both UPDATE statements, rollback nothing

TASK 4 — New method in both repos
  def get_all_attempts_for_calibration(self,
      education_level: str = None,
      exclude_test_users: bool = True) -> list[dict]:
    """
    For ML calibration. Filters elo_valid=1 and is_test_user=0.
    luisito-s and torieg have is_test_user=1 — always excluded.
    """
    Query:
      SELECT a.id, a.user_id, a.item_id, a.is_correct,
             a.expected_score, a.elo_valid, a.time_taken,
             u.education_level
      FROM attempts a
      JOIN users u ON a.user_id = u.id
      WHERE a.elo_valid = 1
        AND (NOT %(exclude_test_users)s OR COALESCE(u.is_test_user,0)=0)
        AND (%(education_level)s IS NULL
             OR u.education_level = %(education_level)s)
      ORDER BY a.attempt_timestamp

VERIFICATION:
  python scripts/db_sync_check.py  → 0 differences
  pytest tests/unit/ tests/integration/ -v  → all pass

  Manual checks:
    time=1s  → elo_valid=0, ELO unchanged ✓
    time=700s → elo_valid=0, ELO unchanged ✓
    time=45s  → elo_valid=1, ELO updates  ✓

CHANGELOG entry:
  feat: elo_valid flag on attempts — times <3s or >600s excluded from ELO
```

### Nuevo skill a crear después de implementar

Crear `.claude/skills/data-quality/SKILL.md` con estas instrucciones:
```markdown
---
name: data-quality
description: Use when checking data quality of attempts, identifying
  outliers in time_taken, or querying filtered datasets. Triggers:
  "datos limpios", "elo_valid", "outliers", "time_taken", "filtrar intentos".
---
# Data Quality — LevelUp-ELO

## Filtros obligatorios en cualquier query de análisis

Todo SELECT sobre attempts para análisis debe incluir:
  AND a.elo_valid = 1
  AND COALESCE(u.is_test_user, 0) = 0  (join con users u requerido)

## Usuarios excluidos permanentemente
  luisito-s (is_test_user=1 desde 2026-04-15)
  torieg    (is_test_user=1 desde 2026-04-15)
  Razón: cuentas del propietario usadas para pruebas manuales.

## Rangos válidos
  time_taken: [3.0s, 600.0s] — fuera de rango → elo_valid=0
  expected_score: (0.0, 1.0) — valores en límites indican error
  elo_after: [400, 2000] — fuera de rango → revisar motor

## Método principal
  repo.get_all_attempts_for_calibration(
      education_level=None,     # None = todos los niveles
      exclude_test_users=True   # SIEMPRE True en análisis
  )
```

---

## FASE 2 — Isotonic Regression: corregir sesgo sistemático

**Cuándo**: inmediatamente después de Fase 1
**Esfuerzo**: 2–3 horas
**Impacto**: sesgo pasa de +0.165 a <0.05 sin cambiar el motor ELO

### Prompt para Claude Code

```
Read CLAUDE.md and .claude/skills/ml-improvements/SKILL.md before starting.
Phase 1 (elo_valid) must already be implemented before this phase.

PHASE 2: Isotonic Regression calibrator.

TASK 1 — Create src/domain/elo/calibration.py
Implement IsotonicCalibrator class:

  class IsotonicCalibrator:
      MODEL_PATH = "models/isotonic_calibrator.pkl"

      def __init__(self): self._model=None; self._trained=False

      def load(self) -> bool:
          """Load trained model. Returns True if file exists."""
          # Load with pickle. Sets self._trained=True if successful.
          # Returns False silently if file not found — never raises.

      def predict(self, p_raw: float) -> float:
          """Apply calibration. Returns p_raw if model not loaded."""
          # Never raises exception.
          # Clamp output to [0.001, 0.999].

      def train_and_save(self, y_true, y_pred) -> dict:
          """Train on data and save model. Returns metrics dict."""
          # Uses sklearn.isotonic.IsotonicRegression(out_of_bounds='clip')
          # Saves to MODEL_PATH with pickle.
          # Returns {'auc_before','auc_after','bias_before','bias_after'}

      @property
      def is_active(self) -> bool: return self._trained

TASK 2 — Create scripts/train_calibrator.py
  Usage:
    python scripts/train_calibrator.py
    python scripts/train_calibrator.py --level semillero
    python scripts/train_calibrator.py --level colegio

  Steps:
    1. Load attempts via repo.get_all_attempts_for_calibration()
       with exclude_test_users=True and elo_valid=1 filter
    2. Print: N intentos, AUC before, sesgo before, log-loss before
    3. Train IsotonicCalibrator
    4. Print: AUC after (should be same ±0.001), sesgo after (<0.05)
    5. Save model to models/isotonic_calibrator_{level}.pkl
    6. Exit with error message if N < 50

TASK 3 — Create scripts/monthly_metrics.py
  Usage: python scripts/monthly_metrics.py
  Prints:
    - Date and N intentos (filtered)
    - AUC global and per level (semillero/colegio/universidad)
    - Sesgo global
    - Log-loss global
    - List of items with success_rate=0% and ≥10 attempts
    - Calibrator status (active/not trained)
  Always filters: elo_valid=1, is_test_user=0

TASK 4 — Integrate in student_service.py
  In __init__:
    from src.domain.elo.calibration import IsotonicCalibrator
    self._calibrator = IsotonicCalibrator()
    self._calibrator.load()

  In process_answer():
    p_raw = expected_score(student_elo, item_difficulty)
    p_calibrated = self._calibrator.predict(p_raw)

    # ELO delta uses p_raw (never calibrated value)
    delta = K * (actual - p_raw)

    # Save p_calibrated to attempts.expected_score
    # This is what the dashboard shows — corrected prediction

TASK 5 — Setup
  mkdir models/
  Add to .gitignore: models/*.pkl
  Create models/.gitkeep

VERIFICATION:
  python scripts/db_sync_check.py  → 0 differences
  python scripts/train_calibrator.py  → runs, prints metrics
  python scripts/monthly_metrics.py  → prints report
  pytest tests/unit/ -v  → add test: IsotonicCalibrator with no
    model file returns p_raw unchanged (graceful degradation)

CHANGELOG:
  feat: isotonic calibration — corrects +0.165 bias without changing ELO
  feat: monthly_metrics.py — automated AUC/bias monitoring
```

### Nuevo skill a crear después de implementar

Crear `.claude/skills/calibration-ml/SKILL.md`:
```markdown
---
name: calibration-ml
description: Use when working with the IsotonicCalibrator, training
  calibration models, or interpreting AUC/bias metrics. Triggers:
  "calibrador", "sesgo", "isotonic", "train_calibrator", "AUC".
---
# ML Calibration — LevelUp-ELO

## Regla crítica
El calibrador corrige expected_score GUARDADO en attempts.
El motor ELO SIEMPRE usa expected_score RAW para calcular deltas.
Nunca pasar el valor calibrado al cálculo de delta ELO.

## Modelos entrenados
  models/isotonic_calibrator_global.pkl   — todos los niveles
  models/isotonic_calibrator_semillero.pkl
  models/isotonic_calibrator_colegio.pkl

## Cuándo reentrenar
  Reentrenar mensualmente o cuando:
  - N intentos nuevos > 500 desde último entrenamiento
  - Sesgo global > 0.10 (detectado por monthly_metrics.py)
  - Se agrega un nivel educativo nuevo

## Métricas esperadas tras calibración
  Sesgo: < 0.05 (antes: +0.165 global, +0.282 Semillero)
  AUC: igual ± 0.002 (isotonic preserva ranking)
  Log-loss: mejora ~5-10%
```

---

## FASE 3 — Clustering de estudiantes

**Cuándo**: cuando haya ≥ 100 estudiantes activos
**Esfuerzo**: 4–6 horas
**Impacto**: personaliza Factor K por perfil de rendimiento

### Verificar antes de empezar

```bash
python scripts/monthly_metrics.py
# Verificar que N estudiantes únicos ≥ 100
```

### Prompt para Claude Code

```
Read CLAUDE.md, .claude/skills/ml-improvements/SKILL.md,
and .claude/skills/calibration-ml/SKILL.md before starting.
Phases 1 and 2 must be implemented before this phase.

PHASE 3: Student profiler — 3 performance clusters.

TASK 1 — Create src/domain/elo/student_profiler.py
  Implement StudentProfiler class with:

  N_CLUSTERS = 3
  K_MODIFIERS = {0: 1.3, 1: 1.0, 2: 0.8}

  Features for clustering (4 dimensions):
    tasa_acierto    (float 0-1)
    elo_medio       (float, normalized)
    n_intentos      (int, capped at 200)
    rd_final        (float)

  Methods:
    fit(student_data: list[dict]) → None
      Train KMeans(n_clusters=3) with StandardScaler normalization.
      Map cluster labels so:
        cluster 0 = lowest tasa_acierto (bajo rendimiento, K×1.3)
        cluster 1 = medium (estándar, K×1.0)
        cluster 2 = highest tasa_acierto (alto rendimiento, K×0.8)

    predict_profile(student_stats: dict) -> int
      Returns 0, 1, or 2.
      Returns 1 (standard) if model not trained — graceful degradation.

    k_modifier(profile: int) -> float
      Returns K_MODIFIERS[profile].

    save(path="models/student_profiler.pkl") → None
    load(path="models/student_profiler.pkl") → bool

TASK 2 — Create scripts/train_profiler.py
  Load student aggregated stats from DB:
    SELECT u.id, u.username,
           AVG(a.is_correct) as tasa_acierto,
           AVG(a.elo_after) as elo_medio,
           COUNT(a.id) as n_intentos,
           MIN(a.attempt_rd) as rd_final
    FROM users u JOIN attempts a ON a.user_id=u.id
    WHERE COALESCE(u.is_test_user,0)=0 AND a.elo_valid=1
    GROUP BY u.id HAVING COUNT(a.id) >= 10

  Train StudentProfiler and save model.
  Print cluster sizes and mean tasa_acierto per cluster.
  Exit with message if fewer than 30 students with ≥10 attempts.

TASK 3 — Integrate in VectorRating.update()
  In src/domain/elo/vector_elo.py, accept optional k_modifier param:

  def update(self, topic, expected, actual, k_base,
             impact_modifier=1.0, k_modifier=1.0):
      k_eff = k_base * (rd / RD_BASE) * impact_modifier * k_modifier

  In student_service.py, before calling update():
      profile = self._profiler.predict_profile(student_stats)
      k_mod = self._profiler.k_modifier(profile)
      vector.update(..., k_modifier=k_mod)

  If profiler not trained: k_modifier=1.0 (standard behavior)

TASK 4 — Add to models/.gitignore
  models/student_profiler.pkl

VERIFICATION:
  python scripts/train_profiler.py  → prints 3 clusters with sizes
  Cluster 0: low success rate, K×1.3
  Cluster 1: medium, K×1.0
  Cluster 2: high success rate, K×0.8
  No changes to existing test behavior when k_modifier=1.0

CHANGELOG:
  feat: student profiler — 3 performance clusters, personalized K factor
```

### Nuevo skill a crear después de implementar

Crear `.claude/skills/student-profiling/SKILL.md`:
```markdown
---
name: student-profiling
description: Use when working with StudentProfiler, cluster analysis,
  or K-factor personalization. Triggers: "clustering", "perfil",
  "k_modifier", "train_profiler", "rendimiento por perfil".
---
# Student Profiling — LevelUp-ELO

## Perfiles
  0 = Bajo rendimiento  → K×1.3 (converge más rápido al nivel real)
  1 = Rendimiento medio → K×1.0 (estándar)
  2 = Alto rendimiento  → K×0.8 (más estable, menos oscilaciones)

## Requisito mínimo para entrenar
  ≥ 100 estudiantes activos con ≥ 10 intentos cada uno

## Cuándo reentrenar
  Mensualmente si N estudiantes creció >20% desde último entrenamiento.

## Regla crítica
  k_modifier solo escala K — nunca modifica el delta ELO directamente.
  impact_modifier sigue siendo 1.0 en producción (CognitiveAnalyzer off).
```

---

## FASE 4 — IRT 2PL para Semillero

**Cuándo**: cuando haya ≥ 3.000 intentos de Semillero con elo_valid=1
**Esfuerzo**: 1–2 semanas
**Impacto**: resuelve AUC Semillero (de ~0.60 a meta ≥0.68)

### Verificar antes de empezar

```bash
python scripts/monthly_metrics.py
# Verificar que N intentos Semillero (elo_valid=1) ≥ 3000
```

### Plugin recomendado para esta fase

**pyirt** no tiene plugin de Claude Code. Instalar la dependencia:
```bash
pip install pyirt --break-system-packages
# Agregar a requirements.txt: pyirt>=0.3.0
```

Para análisis estadístico avanzado (opcional):
```
/plugin marketplace add jupyter
```
Permite correr notebooks dentro de Claude Code para explorar
los parámetros IRT antes de integrarlos al motor.

### Prompt para Claude Code

```
Read CLAUDE.md, .claude/skills/ml-improvements/SKILL.md,
.claude/skills/item-calibration/SKILL.md, and
.claude/skills/calibration-ml/SKILL.md before starting.
Phases 1, 2 and 3 must be implemented before this phase.

PHASE 4: IRT 2PL calibration for Semillero items.

Context:
  ELO classic (1PL) assumes equal discrimination for all items.
  Semillero has olympiad items with very different discrimination
  parameters. IRT 2PL adds a discrimination parameter 'a' per item,
  which resolves the low AUC specific to Semillero.

  IRT 2PL model:
    P(correct | θ, a, b) = 1 / (1 + exp(-a(θ - b)))
  Where:
    θ = student ability (maps to ELO)
    b = item difficulty (maps to D in ELO scale)
    a = item discrimination (new parameter, not in current ELO)

TASK 1 — Create scripts/calibrate_irt_semillero.py
  1. Load Semillero attempts (is_test_user=0, elo_valid=1)
  2. Fit IRT 2PL using pyirt:
     from pyirt import irt
     data = [(user_id, item_id, is_correct), ...]
     params = irt(data, model='2PL', max_iter=200)
  3. For each item, extract:
     - b parameter → new difficulty in ELO scale
       D_new = 1000 + (b * 400)  # scale from logit to ELO
     - a parameter → discrimination
       flag as "low discrimination" if a < 0.5
  4. Generate calibration report:
     - Items with a < 0.5: candidate for review or removal
     - Items where |D_irt - D_elo| > 200: candidate for recalibration
  5. Export report to VALIDACION_ELO/irt_calibration_report.csv
     (VALIDACION_ELO/ is in .gitignore — safe for sensitive data)
  6. Do NOT automatically update item difficulties — generate SQL
     for manual review first

TASK 2 — Create src/domain/elo/irt_adapter.py
  class IRT2PLAdapter:
      """
      Wraps IRT 2PL parameters to provide P(correct) estimates
      as an alternative to the standard ELO formula.

      Used when Semillero item has calibrated IRT params.
      Falls back to standard ELO formula if no IRT params available.
      """
      def predict(self, theta: float, item_id: str) -> float:
          """
          Returns P(correct) using IRT 2PL if params available,
          else uses standard ELO formula as fallback.
          theta = student ELO normalized to logit scale: (R-1000)/400
          """
          params = self._params.get(item_id)
          if params is None:
              return None  # caller uses standard ELO
          a, b = params['a'], params['b']
          return 1.0 / (1.0 + np.exp(-a * (theta - b)))

      def load(self, path="models/irt_params_semillero.json") -> bool:
          """Load IRT params from JSON. Returns False if not found."""

TASK 3 — Integrate in student_service.py (optional path)
  In process_answer(), for Semillero students:
    if student.education_level == 'semillero':
        p_irt = self._irt_adapter.predict(theta, item_id)
        if p_irt is not None:
            expected = p_irt  # use IRT prediction
        else:
            expected = expected_score(R, D)  # fallback to ELO

TASK 4 — Update item bank after manual review
  After reviewing the IRT calibration report:
  - For items where |D_irt - D_elo| > 200 AND a >= 0.8:
    Apply fórmula de calibración directa as correction
    (see .claude/skills/item-calibration/SKILL.md)
  - For items with a < 0.5 and ≥20 attempts: flag for review

VERIFICATION:
  python scripts/calibrate_irt_semillero.py → generates report CSV
  Report shows a and b per item, discrimination flags
  IRT2PLAdapter with no params file returns None (uses ELO fallback)
  AUC Semillero with IRT active ≥ 0.68 (verify with monthly_metrics)

CHANGELOG:
  feat: IRT 2PL calibration for Semillero — discrimination parameter per item
  feat: IRT2PLAdapter — uses IRT predictions when available, ELO fallback
```

### Nuevo skill a crear después de implementar

Crear `.claude/skills/irt-calibration/SKILL.md`:
```markdown
---
name: irt-calibration
description: Use when working with IRT 2PL parameters, calibrating
  Semillero items with pyirt, or interpreting discrimination parameters.
  Triggers: "IRT", "2PL", "discriminación", "pyirt", "theta".
---
# IRT 2PL Calibration — LevelUp-ELO

## Mapeo ELO ↔ IRT
  θ (IRT ability) = (R_elo - 1000) / 400
  b (IRT difficulty) = (D_elo - 1000) / 400
  D_elo = 1000 + b × 400

## Interpretación del parámetro a (discriminación)
  a < 0.5  → baja discriminación — ítem no distingue bien entre niveles
  0.5–1.0  → discriminación moderada
  a > 1.0  → alta discriminación — buen ítem para separar habilidades
  a > 2.5  → muy alto — revisar, puede ser demasiado sensible

## Cuándo usar IRT vs ELO
  ELO: todos los niveles, tiempo real, sin pretesting
  IRT: Semillero con ≥3.000 intentos, calibración offline, mejora AUC

## Archivos clave
  scripts/calibrate_irt_semillero.py  → genera report
  models/irt_params_semillero.json    → parámetros a y b por ítem
  VALIDACION_ELO/irt_calibration_report.csv → reporte manual
```

---

## RESUMEN DE SKILLS — Estado final

```
.claude/skills/
├── item-calibration/SKILL.md       ✅ ya existe
├── ml-improvements/SKILL.md        ✅ ya existe
├── data-quality/SKILL.md           → crear al terminar Fase 1
├── calibration-ml/SKILL.md         → crear al terminar Fase 2
├── student-profiling/SKILL.md      → crear al terminar Fase 3
├── irt-calibration/SKILL.md        → crear al terminar Fase 4
├── impeccable/                     ✅ ya existe
├── design-taste-frontend/          ✅ ya existe
└── emil-design-eng/                ✅ ya existe
```

## RESUMEN DE PLUGINS

| Plugin | Para qué | Cómo instalar |
|---|---|---|
| sequential-thinking | Planificación multi-paso en fases complejas | `/plugin marketplace add modelcontextprotocol/servers` |
| jupyter (opcional) | Exploración IRT antes de integrar al motor | `/plugin marketplace add jupyter` |

## ORDEN DE EJECUCIÓN

```
Fase 1 (time_taken)      → AHORA — antes próxima sesión Semillero
Fase 2 (Isotonic)        → tras Fase 1, misma semana
Fase 3 (Clustering)      → cuando N estudiantes ≥ 100
Fase 4 (IRT 2PL)         → cuando N intentos Semillero ≥ 3.000
```

## VERIFICACIÓN GLOBAL — ejecutar al terminar cada fase

```bash
python scripts/db_sync_check.py      # 0 diferencias
pytest tests/unit/ tests/integration/ -v  # todos pasan
python scripts/monthly_metrics.py    # imprime reporte sin error
```
