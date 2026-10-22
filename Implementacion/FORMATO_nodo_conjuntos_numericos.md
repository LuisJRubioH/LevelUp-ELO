# Formato unificado — Nodos de conjuntos numéricos (Nivel 1)

Molde canónico para los 6 nodos de definición de conjuntos numéricos de Preálgebra:
**B04 Naturales · B05 Enteros · B06 Racionales · B07 Irracionales · B08 Reales · B09 Complejos.**

Establecido y aprobado el 2026-06-29. Cualquier nodo nuevo o revisión de estos debe seguir esta estructura **exacta** para no volver a iterar sobre el formato. El nodo de referencia es **B06 Racionales** (`RationalsLesson.tsx`).

---

## 1. Estructura de pantalla (orden fijo)

```
1. Encabezado          → kicker + h1 + intro. SIN caja en la esquina.
2. Escalera            → <SetNodeScene .../> (o figura del peldaño en B09)
3. KatIA abre el peldaño → <KatiaStorySlot> con apertura narrativa + pregunta problematizadora
4. Fila a dos columnas → [ Descubrimiento guiado | Definición formal ]   (.set-story)
5. Ejemplos resueltos  → bloque propio de 3 tarjetas, la última es la TRAMPA COMÚN (.set-base-examples.set-examples-standalone)
6. Ejercicios          → la práctica formativa existente
7. Footer
```

Secuencia pedagógica: **KatIA abre con la apertura narrativa antes de practicar → descubrimiento guiado → definición formal con ejemplos resueltos → una trampa común → ejercicios.**

### Reglas de oro

- **R1 — Sin esquina.** Nada de cajas `*-set` / `lesson-formula` / mini-KatIA en el encabezado. La fórmula del conjunto **se mueve** a la columna de definición formal (paso 4), su lugar pedagógico.
- **R2 — La pregunta problematizadora vive en KatIA.** La pregunta detonadora va como `question` del `KatiaStorySlot`, no como artículo aparte.
- **R3 — El contexto de apertura NO repite el ejercicio de la práctica.** KatIA y el descubrimiento usan un anclaje concreto distinto al del bloque de ejercicios (p. ej. B06 abre con frutas/jugo y la práctica usa el reparto de panes).
- **R4 — La última tarjeta de ejemplos es siempre la trampa común** (misconception del nodo).
- **R5 — Todo el texto va en i18n** `prealgebra.n1.bXX.story.*`, con paridad `es`/`en` (`DeepString` lo verifica en `tsc --noEmit`). Nada hardcodeado.

---

## 2. Componente `KatiaStorySlot`

`frontend/src/pages/Student/lessons/KatiaStorySlot.tsx`. Props:

| Prop | Uso |
|---|---|
| `eyebrow`, `title`, `body` | apertura narrativa (obligatorios) |
| `question` | pregunta problematizadora (recuadro destacado) |
| `formulas` | `Array<{ math, caption? }>` — fórmulas con leyenda (p. ej. B06: 2/3, 1/4) |
| `formula` | una sola fórmula (compatibilidad; preferir `formulas`) |
| `imageSrc`, `imageAlt` | imagen de KatIA; sin `imageSrc` muestra el placeholder |
| `reverse` | invierte media/copy |

---

## 3. Esquema i18n `bXX.story`

Cada nodo define este bloque en `es.ts` y `en.ts` (idéntico key-for-key):

```ts
story: {
  label,                 // aria de la fila .set-story
  katiaEyebrow,          // "KatIA abre el N peldaño"
  katiaTitle,
  katiaBody,
  katiaQuestion,         // pregunta problematizadora
  // [opcional] claves específicas del nodo: katiaFractionA/B, unitAria, etc.
  discoveryEyebrow,      // "Descubrimiento guiado"
  discoveryTitle,
  discoveryBody,         // un solo párrafo (fundir contraejemplos aquí)
  definitionEyebrow,     // "Definición formal"
  definitionTitle,
  definitionBody,
  examplesLabel,         // aria del bloque de ejemplos
  examples: {            // 3 claves; nombres libres por nodo, la 3.ª es la trampa
    <k1>: { eyebrow, title, body, steps: { 0, 1, 2 } },
    <k2>: { ... },
    trap: { eyebrow: "Trampa común", title, body, steps: { ... } },
  },
}
```

El número de `steps` puede variar por nodo (B05 usa 0–3). El `.map` del componente debe coincidir.

---

## 4. Clases CSS compartidas (`Lesson.css`)

No duplicar por nodo. Usar siempre:

- `.set-story` — fila a 2 columnas (descubrimiento | definición). Colapsa a 1 col < 760px.
- `.set-story article.set-formal` — columna de definición; su `.math-rendered` lleva fondo de acento.
- `.set-base-examples.set-examples-standalone` — ejemplos resueltos en 3 columnas. Colapsa a 1 col < 760px.
- `.katia-story-slot`, `.katia-story-formula-line`, `.katia-story-question` — bloque de KatIA.

El encabezado de cada nodo es `max-width: 760px` (una sola columna), no grid de 2.

---

## 5. Las 7 capas a tocar por nodo

Igual que cualquier nodo F1 (ver memoria `prealgebra-node-implementation`), pero el formato afecta solo a:

1. `frontend/src/pages/Student/lessons/<Set>Lesson.tsx` — markup según §1.
2. `frontend/src/pages/Student/lessons/<Set>Lesson.css` — encabezado a 1 col; borrar clases `*-set`/`*-story`/`*-definition-flow` propias.
3. `frontend/src/i18n/locales/es.ts` y `en.ts` — bloque `story` del §3 (paridad obligatoria).

Verificación: `cd frontend && ./node_modules/.bin/tsc --noEmit` (paridad i18n) + revisar render real del nodo (la página es pesada en KaTeX; los screenshots del preview pueden agotar tiempo — verificar por DOM).
