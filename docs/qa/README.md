# QA — revisión automatizada

Un tester humano encuentra pocas cosas por hora y solo donde mira. Esta carpeta junta lo que lo
complementa:

- **El registro de cada ronda** (`2026-11-ronda-1.md`, …): un bug por fila, con su causa, su spec,
  su ruta de arreglo y su estado.
- **Tres revisiones automáticas** en `scripts/qa/`, que buscan *clases* de defecto y no bugs
  sueltos. Ninguna gasta tokens de modelo, y solo producen capturas donde una comprobación salta.

| Revisión | Qué recorre | Necesita | Tarda |
|---|---|---|---|
| `math_check.js` | Cada fórmula del banco (enunciados y opciones) y de los 52 nodos de once bloques, renderizada con el KaTeX del frontend | Nada: ni servidor ni navegador | ~2 s |
| `lesson_sweep.js` | Los 63 nodos del camino en Chromium. Abre cada paso que se abre con un clic y, con `--answer`, responde cada pregunta | API + frontend + semilla | ~10 min |
| `screen_sweep.js` | Todas las pantallas de los cuatro roles (anónimo, estudiante, docente, admin), el registro con cada nivel y unas preguntas de práctica por materia | API + frontend + semilla | ~2 min |

## Correr las revisiones (en local, nunca contra producción)

`math_check.js` no necesita nada más:

```bash
node scripts/qa/math_check.js --out /tmp/qa-math
```

Termina con código 1 si encuentra algo que el estudiante vería roto, así que sirve como paso de CI.

Las otras dos necesitan la API y el frontend arrancados:

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
| `clipped-control` | Un botón o enlace cuyo texto no cabe y se corta | Q7 |
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

- Responden siempre la primera opción: no prueban el desbloqueo de un nodo ni terminar una lección.
- No juegan la Liga (el WebSocket necesita dos estudiantes), no presentan un examen y no suben un
  procedimiento.
- No comparan contra una captura de referencia, así que no ven regresiones visuales sutiles: un
  glifo mal dibujado, colores o espaciados.
