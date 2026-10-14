# Guía: adoptar la configuración SDD de LevelUp-ELO en otro proyecto

Cómo replicar en otro repositorio el desarrollo guiado por especificaciones (SDD, *spec-driven
development*) que usa la rama `redesign` de LevelUp-ELO: Spec Kit con Claude Code, plantillas
propias, constitución, ciclo de nueve pasos con compuertas y verificación de trazabilidad en CI.

Todo lo que se cita existe en `LuisJRubioH/LevelUp-ELO`, rama `redesign` (y en las ramas
`docs/constitution-1.1.0` y `ci/traceability-deliveries` para las versiones más recientes de la
constitución y del verificador). Úsalo como referencia viva: copia y adapta, no reescribas desde
cero.

---

## 0. Qué obtienes

| Pieza | Para qué sirve |
|---|---|
| **Constitución** (`.specify/memory/constitution.md`) | Principios no negociables, reglas para agentes de IA y gobierno del proceso. Manda sobre todo lo demás |
| **Una spec por área** (`specs/NNN-<area>/`) | El comportamiento acordado de cada área, con requisitos verificables y su prueba |
| **Plantillas propias** (`.specify/templates/overrides/`) | Requisitos EARS, etiquetas `[AS-IS]`/`[CHANGE]`, pruebas obligatorias, tabla de trazabilidad |
| **Ciclo de 9 pasos** | Estudio → spec → aclarar → checklist → plan → tareas → análisis → implementar → converger, con aprobación humana entre pasos |
| **Trazabilidad en CI** (`scripts/check_traceability.py`) | Cada requisito y escenario tiene una prueba que existe, pasa y no se omite |
| **Roadmap** (`docs/sdd/roadmap.md`) | Áreas en orden de riesgo, sesiones estimadas, calendario e hitos |

Pensado sobre todo para proyectos **brownfield** (código que ya existe): primero se fija con
pruebas lo que el código hace hoy y solo después se cambia.

---

## 1. Requisitos

- Git y un repositorio en GitHub con GitHub Actions.
- [`uv`](https://docs.astral.sh/uv/) para instalar el CLI de Spec Kit.
- Claude Code (opcional también Codex CLI como segunda integración).
- Un framework de pruebas cuyas pruebas tengan identificador estable. El verificador de
  LevelUp entiende **pytest** (`ruta::prueba`) y **Playwright** (`archivo.spec.ts › título`); con
  otro stack hay que adaptar esa parte (§ 8).

---

## 2. Instalar Spec Kit

LevelUp fija **Spec Kit (`specify-cli`) 1.0.13**. Fija tú también una versión: los comandos y
plantillas cambian entre versiones.

```bash
uv tool install specify-cli==1.0.13
specify version            # → 1.0.13
```

**Proyecto que aún no tiene `.specify/`** (desde la raíz del repo):

```bash
specify init --here --ai claude --script sh    # Linux/macOS (bash)
specify init --here --ai claude --script ps    # Windows (PowerShell) — lo que usa LevelUp
specify check                                  # herramientas requeridas encontradas
```

Las opciones exactas pueden variar con la versión: confírmalas con `specify init --help`. El
resultado queda registrado en `.specify/init-options.json` (en LevelUp: `"ai": "claude"`,
`"script": "ps"`, `"feature_numbering": "sequential"`).

**Clon limpio de un repo que ya tiene `.specify/`** (los comandos no vienen en el clon):

```bash
specify integration install claude --script sh          # crea .claude/skills/speckit-*
specify integration install codex --script sh --force   # opcional, Codex CLI
specify integration status
```

Después, en Claude Code quedan disponibles `/speckit-constitution`, `/speckit-specify`,
`/speckit-clarify`, `/speckit-checklist`, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`,
`/speckit-implement`, `/speckit-converge` y `/speckit-taskstoissues`.

### Qué se versiona

| Ruta | ¿En git? | Contenido |
|---|---|---|
| `.specify/` | **sí** | scripts, plantillas core, **overrides**, constitución, workflow |
| `.specify/feature.json` | no (lo ignora `.specify/.gitignore`) | puntero local a la feature activa |
| `.claude/skills/speckit-*` | en LevelUp **no** (`.claude/` está en `.gitignore`) | los comandos; se regeneran con `specify integration install` |
| `specs/`, `docs/sdd/` | **sí** | specs, planes, tareas, estudios, roadmap |

Si prefieres que un clon funcione sin instalar nada, puedes versionar `.claude/skills/speckit-*`;
el costo es que una actualización de Spec Kit genera diffs grandes.

---

## 3. Personalizar las plantillas (lo que hace distinta esta configuración)

**Regla:** nunca edites `.specify/templates/*.md` directamente; una actualización de Spec Kit los
reemplaza. Pon tus versiones en **`.specify/templates/overrides/`**, la primera capa de resolución
de plantillas, que `specify integration upgrade` y un re-init no tocan.

Copia de LevelUp (`redesign`) estos dos archivos y adáptalos:

### 3.1 `overrides/spec-template.md`

Añade a la plantilla core cuatro secciones obligatorias y dos convenciones:

1. **`## Code Scope`**: las rutas de código cuyo comportamiento define la spec (una por viñeta,
   entre backticks; un directorio termina en `/`; `*` también cruza `/`). Cada entrada debe
   nombrar al menos un archivo versionado. El verificador de CI la usa para saber si un PR es un
   cambio de código de esa spec.
2. **Requisitos en EARS**, uno por respuesta verificable:
   - Ubicuo: *The system shall …*
   - Por evento: *When <disparador>, the system shall …*
   - Por estado: *While <estado>, the system shall …*
   - No deseado: *If <condición>, then the system shall …*
   - Opcional: *Where <característica>, the system shall …*
3. **Etiqueta brownfield obligatoria en cada FR:**
   - `[AS-IS]`: el código ya lo hace hoy y una prueba lo fija.
   - `[CHANGE]`: comportamiento decidido en `/speckit-clarify` que el código todavía no tiene.
4. **`## Out of Scope`**: lo que la spec deliberadamente no cubre, nombrando la spec vecina
   cuando corresponda. Evita que el plan o el agente amplíen el alcance.
5. **`## Traceability`**: tabla `| Requirement / Scenario | Test |` con una fila por cada
   `FR-nnn` y cada escenario `USn-ASm`. La celda es un id de pytest, un título de Playwright o
   `PENDING`.
6. Toda spec declara el **resultado para el usuario** que sirve (en LevelUp, *Outcome served*).

### 3.2 `overrides/tasks-template.md`

1. **Pruebas obligatorias** (la plantilla core dice que son opcionales): cada FR y escenario de la
   tabla de trazabilidad genera una tarea de prueba, reutilizando una existente si ya lo prueba.
2. **Dos tipos de prueba, dos secuencias:**

   | Etiqueta | Tipo | Antes de implementar | Después |
   |---|---|---|---|
   | `[AS-IS]` | caracterización | **pasa** sobre el código sin cambios | sigue pasando |
   | `[CHANGE]` | cambio de comportamiento | **falla** | pasa |

3. **Fase 2 “Pin Current Behaviour” (bloqueante):** ninguna tarea de implementación empieza hasta
   que todas las pruebas de caracterización pasan sobre el código sin tocar. Si una falla, se
   lleva a `/speckit-clarify`; no se “arregla” el código ahí.
4. Cada tarea de prueba nombra los IDs que cubre (`FR-003, US1-AS2`).
5. **Fase final “Traceability & Verification”:** sin filas `PENDING`, revisar que las aserciones
   prueban de verdad el requisito, correr la verificación completa, retirar desviaciones resueltas.
6. **Adapta** la sección *Path Conventions* y los comandos de verificación a tu proyecto.

Para ver qué archivo resuelve una plantilla (PowerShell):

```powershell
. .\.specify\scripts\powershell\common.ps1
Resolve-Template -TemplateName tasks-template -RepoRoot (Get-Location).Path
```

---

## 4. Escribir la constitución

Corre `/speckit-constitution` partiendo de las reglas que ya tengas (tu `CLAUDE.md`, README,
convenciones) **corregidas contra el código**: lo que el código contradice no entra como regla
sino como desviación conocida.

Estructura de la constitución de LevelUp (copia el esqueleto, cambia el contenido de dominio):

1. **Core Principles**, cada uno con reglas en MUST y un *Rationale*. Los dos primeros son
   genéricos y conviene conservarlos:
   - **I. The Spec Is the Contract**: el comportamiento lo define `specs/NNN-*/spec.md`; cada FR
     tiene al menos una prueba; código y spec en desacuerdo es un defecto; un cambio de
     comportamiento llega primero como `[CHANGE]`; un área sin spec se rige por la constitución
     y recibe su spec la primera vez que se toca.
   - **II. One Source of Truth per Fact**, con una tabla de **dueño normativo** por tema:

     | Tema | Dueño normativo |
     |---|---|
     | Principios, no negociables, gobierno | la constitución |
     | Comportamiento de un área con spec | `specs/NNN-*/spec.md` |
     | Cómo hacer (comandos, patrones, rutas) | `AGENTS.md` |
     | Razones e historia de las decisiones | `docs/arquitectura.md` |

   - El resto son de tu dominio (en LevelUp: capas, paridad de bases de datos, integridad de la
     medición, seguridad, simplicidad, pedagogía).
2. **Project Nature & Technology Stack**.
3. **Domain Rules**, **Code Style & Structure**, **Validation & Error Management**.
4. **AI Agent Behaviour (SDD Rules)**: las ocho reglas son genéricas; cópialas casi tal cual:
   1. *Bounded reach*: alcance = objetivo autorizado + dependencias necesarias. Lo que esté fuera
      se reporta, no se arregla de paso. Nunca push a `main`, nunca deploy.
   2. *Measurable acceptance*: todo criterio es una prueba o un número.
   3. *What, not how, in specs*: la spec dice qué; el plan elige cómo.
   4. *Outcome traceability*: tarea → historia de usuario → resultado.
   5. *Humans decide, agents evidence*: una decisión nueva se marca `[NEEDS CLARIFICATION]` con
      una recomendación; las afirmaciones sobre el código citan `archivo:línea` o una prueba.
   6. *Brownfield safety*: caracterizar antes de refactorizar.
   7. *Workflow gates*: una rama por spec (o por entrega), un commit por paso aprobado, PR de docs
      tras tasks + analyze, PR de código tras converge. **El dueño fusiona.**
   8. *Verification before "done"*: la lista de comandos de verificación del proyecto.
5. **Known Deviations**: tabla `ID | Desviación | Contradice | Se arregla en | Fecha límite`.
   Toleradas hasta su fecha, pero no se pueden extender a código nuevo.
6. **Governance**:
   - **Precedencia:** constitución > spec del área > `AGENTS.md` > `docs/arquitectura.md` >
     `CLAUDE.md` (puntero local, no versionado).
   - Principios **no negociables** que ningún plan puede saltarse; los demás solo con aprobación
     del dueño, fecha límite y registro en Known Deviations.
   - Enmiendas por `/speckit-constitution` en su propia rama y PR, con *Sync Impact Report*.
   - Versionado semántico (MAJOR quita o redefine un principio; MINOR añade; PATCH redacta).
   - Lista de **lo que ya verifica CI** y de **lo que todavía solo verifica la revisión**.

Pie de la constitución: `**Version**: X.Y.Z | **Ratified**: AAAA-MM-DD | **Last Amended**: AAAA-MM-DD`.

---

## 5. Documentos de apoyo

| Archivo | Contenido | Nota |
|---|---|---|
| `AGENTS.md` | El **cómo**: inicio rápido, comandos de verificación, instalación de Spec Kit, secuencia obligatoria (§ 6), reglas operativas con IDs estables (R1, R2…) | Empieza con “Read first: la constitución”. Los IDs nunca se renumeran; una regla retirada se marca *Superseded* |
| `CLAUDE.md` | Solo un puntero a la constitución y a `AGENTS.md` | En LevelUp está en `.gitignore` (local) |
| `docs/arquitectura.md` | Por qué se decidió cada cosa | |
| `docs/sdd/roadmap.md` | Plan de adopción (§ 7) | |
| `docs/sdd/<area>-survey.md` | Estudio previo de cada área (§ 6, paso 0) | |

---

## 6. El ciclo por spec

Una spec por **área acotada** (*bounded area*), no por funcionalidad suelta. Cada spec recorre:

| # | Paso | Comando | Compuerta antes de seguir |
|---|---|---|---|
| 0 | Estudio (solo lectura) | — | `docs/sdd/<area>-survey.md` leído por el dueño |
| 1 | Especificar | `/speckit-specify` | el dueño aprueba `spec.md` (comportamiento **as-is**) |
| 2 | Aclarar | `/speckit-clarify` | cada `[NEEDS CLARIFICATION]` resuelto o diferido **por el dueño** (mantener, arreglar o eliminar cada desvío) |
| 3 | Checklist | `/speckit-checklist` | todos los ítems de calidad de requisitos pasan |
| 4 | Planear | `/speckit-plan` | *Constitution Check* pasa; el dueño aprueba |
| 5 | Tareas | `/speckit-tasks` | cada fila de trazabilidad tiene una tarea de prueba |
| 6 | Analizar | `/speckit-analyze` | sin hallazgos CRITICAL |
| — | **PR de docs** | — | spec + plan + tareas, sin código; el dueño fusiona |
| 7 | Implementar | `/speckit-implement` | pruebas de la Fase 2 en verde sobre el código sin cambios antes de refactorizar |
| 8 | Converger | `/speckit-converge` | sin brechas nuevas (repetir 7 ↔ 8 hasta vaciar) |
| — | **PR de código** | — | sin filas `PENDING`; verificación en verde; el dueño fusiona |

Reglas de ramas y commits:

- Una rama por spec (`NNN-<area>`, la crea `/speckit-specify`), o una por **entrega** si la spec
  declara entregas (§ 6.2).
- **Un commit por paso aprobado.**
- **Dos PR por spec:** el de docs (barato de revisar, sin riesgo de deploy) y el de código.
- Cambiar un requisito después: `/speckit-clarify` → plan → tasks → analyze → implement. Si
  contradice un principio, primero `/speckit-constitution`.

> **Importante:** el workflow que trae Spec Kit (`.specify/workflows/speckit/workflow.yml`) solo
> tiene compuertas después de *specify* y *plan*. Las demás compuertas de esta tabla son
> **manuales**: escríbelas en `AGENTS.md` y hazlas cumplir en la revisión.

### 6.1 Paso 0: el estudio

Un documento de solo lectura que sirve de insumo a `/speckit-specify`. Estructura usada en LevelUp:

```markdown
# <Área> — as-is survey (spec NNN input)

Read-only survey of `<rama> @ <commit>`, <fecha>. Input for `specs/NNN-<area>/spec.md`.

Each finding cites code at that commit:
| Abbreviation | File |
|---|---|
| `W` | `ruta/al/archivo.py` |

How each finding was checked:
- **Verified**: read in the code.
- **Reproduced**: run locally (nunca contra producción).
- **Inferred**: reasoned from the code, not run.

## 1. Where things live
## 2. Actual behaviour
## 3. Findings
## 4. Existing evidence        (pruebas que ya existen)
## 5. Decisions for the owner  (insumo para /speckit-clarify, con opciones)
## 6. Proposed scope for spec NNN (draft)
```

### 6.2 Specs grandes: entregas (*deliveries*)

Cuando una spec es demasiado grande para un solo PR de código (en LevelUp, la spec 004 de
identidad), declárala en entregas:

```markdown
## Deliveries *(mandatory for this spec)*

| Delivery | Content | Order rule | State |
|---|---|---|---|
| **E1** | … | … | closed |
| **E2** | … | Before E3 | in progress |
| **E3** | … | After E2 | planned |
```

- Estados válidos: `planned`, `in progress`, `closed`.
- La tabla de trazabilidad gana una columna central `Delivery` en cada fila.
- `PENDING` solo se permite en filas de una entrega no cerrada. El PR que cierra una entrega la
  marca `closed` y no deja ninguna de sus filas en `PENDING`.
- Cada entrega tiene su rama, `plan-eN.md` y `tasks-eN.md`.

---

## 7. El roadmap de adopción

Crea `docs/sdd/roadmap.md` con:

1. **Cómo se trabaja**: la tabla del § 6.
2. **Fase 0, fundación (una vez):**

   | # | Trabajo | Sesiones |
   |---|---|---|
   | 0.1 | Overrides de plantillas (EARS, Out of Scope, Traceability) | 0.5 |
   | 0.2 | Constitución desde las reglas actuales, corregidas contra el código | 1.5 |
   | 0.3 | Reducir `CLAUDE.md` a puntero; mover el cómo a `AGENTS.md` | 1 |

3. **Specs por área, en orden de riesgo**, con lo que cubre cada una y sus sesiones estimadas.
   En LevelUp: motor ELO (8), persistencia (6), ruta de aprendizaje (6), identidad (4), IA (4),
   consola docente (5), PvP (4), banco de ítems (4).
4. **Tareas de automatización**, cada una en su rama y PR: por ejemplo A-1 (E2E en CI) y A-2
   (trazabilidad en CI).
5. **Seguimientos (F-n):** defectos fuera del alcance de la spec en curso, con reproducción,
   criterio de aceptación y momento. Cada uno se arregla en su propia rama, con la prueba primero.
6. **Calendario** con hitos (M0, M1, …), cadencia supuesta (LevelUp: 5 sesiones/semana de medio
   día) y festivos.
7. **Alcance lean recomendado:** las 2–3 áreas más riesgosas reciben su spec ya; las demás se
   especifican la primera vez que una funcionalidad las toca (*spec on touch*), así ninguna área
   se especifica dos veces.
8. **Definición de terminado:** constitución ratificada; cada área en alcance con spec/plan/tareas
   fusionados a `main`; cada escenario con una prueba que pasa; `/speckit-converge` sin brechas.

Si el sistema actual tiene una versión congelada (en LevelUp, V1 en Streamlit), decláralo:
sin specs propias, solo se toca por caídas, corrupción de datos o para que siga funcionando
tras un cambio en una capa compartida.

---

## 8. Trazabilidad en CI

Copia `scripts/check_traceability.py` de la rama `ci/traceability-deliveries` (la versión con
soporte de entregas) y adapta las constantes del principio (`FRONTEND`, `E2E_DIR`) y las funciones
que recolectan pruebas si tu stack no es pytest + Playwright.

Qué comprueba, por cada `specs/*/spec.md`:

1. Cada `FR-nnn` y `USn-ASm` se define una sola vez (en cualquier formato Markdown) y toda
   mención apunta a un ID definido (salvo IDs de otra spec, “spec 001 FR-028m”).
2. La tabla de trazabilidad tiene exactamente una fila por ID, sin celdas vacías; cada referencia
   va entre backticks.
3. Entregas: `PENDING` solo en entregas no cerradas.
4. Sin entregas: `PENDING` se rechaza en un PR que cambie código de la spec (rutas de su Code
   Scope, una prueba que cita, o código junto con su propio directorio `specs/NNN-*/`).
5. Cada referencia existe (`pytest --collect-only`, `playwright test --list`).
6. Con `--run`: las pruebas referenciadas pasan y ninguna se omite.

Uso local:

```bash
python scripts/check_traceability.py          # pasos 1–5
python scripts/check_traceability.py --run    # también las corre, como en CI
```

Job de CI (extracto del de LevelUp; añade los servicios que tus pruebas necesiten):

```yaml
  traceability:
    name: "Trazabilidad spec → tests"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2   # en un PR, HEAD es el merge commit y HEAD^1 la base

      # … instalar Python, dependencias y, si aplica, Node + navegador de Playwright …

      - name: Files the pull request changes
        if: github.event_name == 'pull_request'
        # --no-renames: mover código fuera del Code Scope también cuenta como cambiarlo
        run: git diff --name-only --no-renames HEAD^1 HEAD > "$RUNNER_TEMP/changed-files.txt"

      - name: Verificar trazabilidad
        run: |
          args=(--run)
          if [ -f "$RUNNER_TEMP/changed-files.txt" ]; then
            args+=(--changed-files "$RUNNER_TEMP/changed-files.txt")
          fi
          python scripts/check_traceability.py "${args[@]}"
```

Complementa con un piso de cobertura (`--cov-fail-under`) en las capas de dominio y aplicación.
Cobertura y trazabilidad no se sustituyen: la primera dice que el código se ejecutó; la segunda,
que cada requisito tiene prueba. Ninguna prueba que las aserciones sean adecuadas: eso queda en la
revisión.

---

## 9. Lista de arranque

1. [ ] `uv tool install specify-cli==<versión>` y `specify init --here --ai claude --script <sh|ps>`.
2. [ ] Decidir si `.claude/` se versiona; si no, documentar `specify integration install` en `AGENTS.md`.
3. [ ] Crear `.specify/templates/overrides/spec-template.md` y `tasks-template.md` (§ 3).
4. [ ] `/speckit-constitution` → `.specify/memory/constitution.md` (§ 4).
5. [ ] `AGENTS.md` con verificación, instalación y la secuencia obligatoria; `CLAUDE.md` como puntero (§ 5).
6. [ ] `docs/sdd/roadmap.md` con áreas en orden de riesgo y calendario (§ 7).
7. [ ] `scripts/check_traceability.py` + job de CI (§ 8); protección de rama para que el dueño fusione.
8. [ ] Primera área: estudio → … → PR de docs → … → PR de código (§ 6).
9. [ ] **Revisión del primer `/speckit-tasks`** antes de hacer commit (ver § 10).

---

## 10. Lecciones de LevelUp

- **Revisa a mano el primer `tasks.md`.** La skill upstream sigue diciendo que las pruebas son
  opcionales; los overrides las vuelven obligatorias, pero hay que verificar que la generación lo
  cumple: cada FR y escenario con una tarea de prueba que nombre sus IDs; cada `[AS-IS]` tocado con
  caracterización en la fase bloqueante; cada `[CHANGE]` con una prueba que falle antes de su
  implementación. Si falla de forma sistemática, corrige el override, no la skill upstream.
- **Una enmienda en vuelo por spec.** Mientras una spec tenga filas `PENDING` en la rama base, todo
  PR que toque su código falla. Para trabajo largo, usa entregas.
- **Toda rama de trabajo con su PR**, aunque sea borrador. En LevelUp, la spec 005 quedó en una rama
  sin PR y es fácil perderle la pista.
- **El orden por riesgo se desvía** cuando las decisiones del dueño empujan otras áreas (*spec on
  touch*). Está bien, pero anótalo en el roadmap para que el porcentaje de avance no engañe.
- **Los estudios nunca tocan producción**; los pasos que necesitan datos o credenciales de
  producción se marcan como del dueño (por ejemplo, LevelUp T084).
- **El agente evidencia, el humano decide:** cada decisión nueva llega con opciones,
  consecuencias y una recomendación, citando `archivo:línea`.
