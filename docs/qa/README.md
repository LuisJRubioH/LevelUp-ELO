# QA — revisión automatizada

Un tester humano encuentra pocas cosas por hora y solo donde mira. Esta carpeta junta las dos
piezas que lo complementan:

- **El registro de cada ronda** (`2026-11-ronda-1.md`, …): un bug por fila, con su causa, su spec,
  su ruta de arreglo y su estado.
- **El barrido de lecciones** (`scripts/qa/lesson_sweep.js`): un navegador que recorre los 63 nodos
  del camino, abre todo lo que se abre con un clic y busca *clases* de defecto, no bugs sueltos.
  No gasta tokens de modelo: es Playwright, y solo produce capturas donde una comprobación salta.

## Correr el barrido (local, nunca contra producción)

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
node scripts/qa/lesson_sweep.js --out /tmp/sweep --width 1366 --user estudiante_colegio_2
```

```bash
node scripts/qa/lesson_sweep.js --out /tmp/sweep-movil --width 375 --user estudiante_colegio_3 --shots
```

`seed_lesson_access.py` solo escribe la base SQLite local y se niega a correr si `DATABASE_URL`
está definida. Abre todos los nodos para tres estudiantes de prueba, uno por presentación:
`estudiante_colegio_1` (básico), `_2` (intermedio) y `_3` (avanzado). Si Playwright no se
encuentra desde la raíz del repositorio, antepón `NODE_PATH=$(npm root -g)`.

La API carga el contenido de los nodos al arrancar: después de cambiar `src/domain/learning/`,
reiníciala antes de barrer (o arráncala con `--reload`). El frontend se recarga solo.

El resultado queda en `report.md` y `report.json` de `--out`. Con `--shots` sale además una
captura por comprobación y nodo, centrada en el primer elemento que falla. Esas son las únicas
imágenes que vale la pena mostrarle a un modelo.

## Qué comprueba

| Comprobación | Defecto | Origen |
|---|---|---|
| `katex-broken` | Una fórmula desarmada, un símbolo por línea | Q1 |
| `latex-unrendered` | Comandos LaTeX visibles como texto | — |
| `katex-error` | KaTeX no pudo leer la fórmula | — |
| `faded-no-input` | Un «Complétalo tú» sin nada que completar | Q4 |
| `multi-no-hint` | Una pregunta de varias respuestas que no lo dice | Q2 |
| `overflow-x` | Algo que se sale del borde de la pantalla | Q7 |
| `image-broken` | Una imagen que no cargó | — |
| `console-error`, `http-error` | Errores en la consola o respuestas 4xx/5xx | — |

Cada bug nuevo de un tester se convierte, si se puede, en una comprobación más. Así el siguiente
barrido lo busca en todos los nodos.

## Reparto de modelos

- **El barrido:** ningún modelo.
- **Leer `report.md` y agrupar hallazgos en el registro:** un modelo barato (Haiku/Sonnet).
- **Mirar capturas:** solo las de `--shots` y solo de comprobaciones nuevas.
- **Decidir qué es un bug y qué es diseño:** el modelo fuerte o la dueña.

## Lo que el barrido todavía no hace

- No responde preguntas: no prueba el ciclo de responder mal y reintentar, ni el desbloqueo.
- No recorre las pantallas fuera de las lecciones: registro, práctica, Liga, exámenes ni docente.
- No compara contra una captura de referencia, así que no ve regresiones visuales sutiles.
