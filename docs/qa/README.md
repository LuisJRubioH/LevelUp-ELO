# QA — revisión automatizada

Un tester humano encuentra pocas cosas por hora y solo donde mira. Esta carpeta junta lo que lo
complementa:

- **El registro de cada ronda** (`2026-11-ronda-1.md`, …): un bug por fila, con su causa, su spec,
  su ruta de arreglo y su estado.
- **Four automated sweeps** in `scripts/qa/` look for defect classes. They use no model tokens
  and only capture screenshots when a check fires.

No reemplazan a `frontend/e2e/`, la suite de Playwright que corre en CI contra una API simulada y
que prueba flujos concretos, citados desde las specs. Las revisiones de aquí recorren *todo* contra
la API real en local y buscan lo que nadie pensó en probar.

| Revisión | Qué recorre | Necesita | Tarda |
|---|---|---|---|
| `math_check.js` | Cada fórmula del banco (enunciados y opciones) y de los 52 nodos de once bloques, renderizada con el KaTeX del frontend | Nada: ni servidor ni navegador | ~2 s |
| `lesson_sweep.js` | Los 60 nodos del camino en Chromium. Abre cada paso que se abre con un clic y, con `--answer`, responde cada pregunta | API + frontend + semilla | ~10 min; ~1,5 min por nodo con `--answer` (córrelo por niveles con `--node`, o en primer plano) |
| `screen_sweep.js` | Todas las pantallas de los cuatro roles (anónimo, estudiante, docente, admin), el registro con cada nivel y unas preguntas de práctica por materia | API + frontend + semilla | ~2 min |
| `flow_sweep.js` | Complete lesson and successor unlock; teacher-assigned exam; image upload and teacher grading without AI; a full League match in two browser contexts | Isolated local API + frontend; installed Playwright/Chromium | ~1–2 min |

## Correr las revisiones (en local, nunca contra producción)

`math_check.js` no necesita nada más:

```bash
node scripts/qa/math_check.js --out /tmp/qa-math
```

Termina con código 1 si encuentra algo que el estudiante vería roto, así que sirve como paso de CI.

The browser sweeps need the API and frontend running:

```bash
pip install -r requirements-api.txt
```

```bash
ADMIN_PASSWORD=testadmin123 PUBLIC_REGISTRATION_ENABLED=true uvicorn api.main:app --port 8000
```

```bash
cd frontend && pnpm install --frozen-lockfile && pnpm run dev
```

```bash
python scripts/qa/seed_lesson_access.py
```

```bash
node scripts/qa/lesson_sweep.js --out /tmp/qa-lessons --answer --user estudiante_colegio_1
```

```bash
node scripts/qa/lesson_sweep.js --out /tmp/qa-lessons-movil --width 375 --user estudiante_colegio_3 --shots
```

```bash
node scripts/qa/screen_sweep.js --out /tmp/qa-screens --width 375 --shots
```

Notas para correrlas:

- `seed_lesson_access.py` solo escribe la base SQLite local y se niega a correr si `DATABASE_URL`
  está definida. Abre todos los nodos para tres estudiantes de prueba, uno por presentación:
  `estudiante_colegio_1` (básico), `_2` (intermedio) y `_3` (avanzado).
- `--answer` y la práctica de `screen_sweep.js` **escriben** respuestas e intentos del estudiante
  de prueba local, y la práctica mueve sus ratings.
- Si Playwright no se encuentra desde la raíz del repositorio, antepón `NODE_PATH=$(npm root -g)`.
- La API carga el contenido de los nodos al arrancar: después de cambiar `src/domain/learning/`,
  reiníciala antes de barrer (o arráncala con `--reload`). El frontend se recarga solo.
- Los barridos dejan `report.md` y `report.json` en `--out`. Con `--shots` sacan además una
  captura por comprobación y pantalla, centrada en el primer elemento que falla. Esas son las
  únicas imágenes que vale la pena mostrarle a un modelo.
- Para recorrer la app en inglés, pasa `--lang en` a `screen_sweep.js`.
- **El idioma importa.** Los barridos fijan el español (`es-CO`), el idioma de los estudiantes.
  Un texto más largo en un idioma que en otro cambia qué cabe: Q7 solo falla en español.

## Qué comprueban

Comprobaciones del DOM, compartidas por los dos barridos (`scripts/qa/lib.js`):

| Comprobación | Defecto | Origen |
|---|---|---|
| `katex-broken` | Una fórmula desarmada, un símbolo por línea | Q1 |
| `latex-unrendered` | Comandos LaTeX visibles como texto | Q9 |
| `katex-error` | Una fórmula que KaTeX no pudo leer: se ve el código en gris | — |
| `faded-no-input` | Un «Complétalo tú» sin nada que completar | Q4 |
| `multi-no-hint` | Una pregunta de varias respuestas que no lo dice | Q2 |
| `overflow-x` | Algo que se sale del borde de la pantalla | Q7 |
| `clipped-control` | Un botón o enlace cortado: su texto no cabe, o un contenedor que oculta su desborde lo tapa en parte | Q7 |
| `label-style-leak` | El estilo de una etiqueta sobre el contenido de al lado: una frase en mayúsculas diminutas o una fórmula más pequeña que su texto | Q11 |
| `formula-uppercased` | Una fórmula dentro de un elemento en mayúsculas, que le cambia las letras (`n` → `N`) | Q11 |
| `image-broken` | Una imagen que no cargó | — |
| `i18n-key` | Una clave de traducción sin traducir (`practice.sendAnswer`) | — |
| `error-screen` | La pantalla de «Algo salió mal» | — |
| `console-error`, `page-crash`, `http-error` | Errores de consola (con el `%s` de React resuelto), excepciones y respuestas 4xx/5xx | Q10 |

Comprobaciones al responder (`lesson_sweep.js --answer` y la práctica de `screen_sweep.js`):

| Comprobación | Defecto | Origen |
|---|---|---|
| `no-feedback` | Una respuesta que no recibe ninguna retroalimentación | — |
| `dead-end` | Tras un error no queda nada con qué reintentar | Q2 |
| `generic-feedback` | «Revisa el procedimiento paso a paso» en una pregunta sin procedimiento | Q3 |
| `wrong-route` | La app manda al usuario a otra pantalla (una guarda o un fallo) | — |

Comprobaciones estáticas (`math_check.js`):

| Comprobación | Defecto |
|---|---|
| `parse-error` | KaTeX rechaza la fórmula |
| `bare-latex` | Un comando LaTeX o un `{,}` en prosa, fuera de `$…$` |
| `prose-in-math` | Dos `$` puestos como dinero que quedaron emparejados en una fórmula («$500 y $300») |
| `katex-strict` | KaTeX la dibuja, pero con un aviso (unicode en modo matemático). Es informativo. |

Cada bug nuevo de un tester se convierte, si se puede, en una comprobación más. Así el siguiente
barrido lo busca en todas partes.

## Reparto de modelos

- **Las revisiones:** ningún modelo.
- **Leer `report.md` y agrupar hallazgos en el registro:** un modelo barato (Haiku/Sonnet).
- **Mirar capturas:** solo las de `--shots` y solo de comprobaciones nuevas.
- **Decidir qué es un bug y qué es diseño:** el modelo fuerte o la dueña.

## Lo que todavía no hacen

- No comparan contra una captura de referencia, así que no ven regresiones visuales sutiles: un
  glifo mal dibujado, colores o espaciados.

## Complete local flows

Use the dedicated API launcher below instead of the ordinary API command. It binds only to
loopback, bootstraps `tmp/qa-flows/elo.db`, disables AI keys and Supabase Storage (including values
from `.env`), and uses the existing database on subsequent runs. It refuses to start when
`DATABASE_URL` is defined, even as an empty string. Stop another API using port 8000 first.
No `playwright install` is needed or run.

```bash
python scripts/qa/serve_flow_app.py
```

In another terminal, start the frontend with its frozen dependencies:

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm run dev
```

Then, from the repository root:

```bash
node scripts/qa/flow_sweep.js --out tmp/qa-flows/latest --shots
```

PowerShell uses the same commands. The driver also resolves Playwright from
`frontend/node_modules`, so a global install is unnecessary. `--browser <absolute executable>`
selects an already installed Chromium when its location differs from Playwright's default.
`--python <executable>`, `--width 375`, `--web http://localhost:5173` and
`--api http://localhost:8000` are supported. Keep the web origin as `localhost`, as configured by
the app's local authentication checks. HTTP and WebSocket traffic is restricted to loopback;
redirects from API setup requests are refused. The driver refuses a defined `DATABASE_URL` too.

The sweep creates a fresh student, a teacher-owned group and a single-use invitation through
the API on every run. Those local records remain available for investigation. It does **not**
need `seed_lesson_access.py`: only the lesson's predecessors are completed through the API,
leaving the tested node and its successor untouched until the browser reaches them. Answers
come from `dump_flow_answers.py`, which reads the domain grading rules and versioned item bank
without database access. Grading data stays in the Node driver, outside the browser.

The browser then:

1. Answers every required practice question and the Pólya closing question correctly, makes the
   genuine attempt, finishes the node, reads back completion and opens its newly unlocked successor.
2. Creates and assigns a two-question exam as the teacher, submits it as the student, and compares
   the visible scores, persisted history and exact selected answers with the teacher's result.
3. Uploads a unique 16×16 PNG without an AI key, verifies the visible fallback, opens the real image
   as the teacher, grades it 80 with a unique comment, and checks the student's persisted feedback.
4. Signs in `estudiante_colegio_1` and `_2` in separate contexts, obtains rating through the real
   diagnostic endpoint, queues both, answers all ten items per player and compares both results
   with persisted history. These seeded accounts have `is_test_user=1`; R19 exempts them from the
   institution requirement and permits them to meet each other. No rating is written with SQL.

`inspect()` and the shared console/HTTP collectors run at every visited screen and after every
transition. A failed flow does not stop the remaining flows. `report.md` and `report.json` include
all four outcomes; JSON adds a `flows` array to the existing report format. Exit **0** means no
findings, **1** means findings or a failed flow, **2** means setup prevented execution. A completed
flow can still contain visual or transport findings. `--shots` also captures flow failures whose
evidence is not attached to a DOM element. An absent/disabled button or missing next screen fails
within a bounded timeout. An unexpected exception is recorded as `flow-error`.

| New check | Required evidence |
|---|---|
| `flow-step` | Visible, enabled control and its expected next state |
| `lesson-completed` | First completion, correct persisted responses and completed map state |
| `lesson-next` | Successor changed from blocked to accessible and opened in the browser |
| `exam-result` | Student/teacher scores, answer counts, choices, visible results and history agree |
| `procedure-grade` | Pending upload, actual image, teacher grading and student's score/comment agree |
| `ai-degraded` | No system AI, visible explanation, direct submission enabled, no analysis control, submission succeeds |
| `league-result` | Same match, all answers, mirrored scores, complementary outcomes, visible results and persisted deltas agree; no forfeit or abandonment |
| `league-close` | No abnormal close or admission/reconnect refusal code |

### Check the checks

```bash
node scripts/qa/flow_checks_probe.js --out tmp/qa-flows/probes
```

This separate Chromium fixture deliberately hides/disables a button and removes its action,
then restores it. For **every field** of the eight flow predicates it first checks an intact
observation, mutates one field (missing persistence, mismatched score/choice, absent image,
missing AI notice, wrong match, etc.), requires a finding, then restores the original and requires
silence. UI action mutations run in a real DOM; role/persistence mutations use isolated observation
payloads. No app response is stubbed in the real sweep and no product file is edited. It also
injects each League refusal code and verifies remote-target, defined-DB and unreachable-API setup
failures, including their four blocked outcomes and exit code 2. These probes produce their own
reports and exit nonzero if a detector fails. Actual runs and product findings are recorded in
[`2026-11-ronda-2.md`](2026-11-ronda-2.md).
