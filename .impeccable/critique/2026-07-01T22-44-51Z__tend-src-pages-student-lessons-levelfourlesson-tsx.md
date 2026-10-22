---
target: LevelFourLesson.tsx hub (Puerto de la Polis)
total_score: 30
p0_count: 0
p1_count: 3
timestamp: 2026-07-01T22-44-51Z
slug: tend-src-pages-student-lessons-levelfourlesson-tsx
---
## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Live "0/6 abiertos" counter es bueno; falta un indicador visual (barra/puntos) para escaneo rápido |
| 2 | Match System / Real World | 4 | Metáfora del puerto/griego mapeada consistentemente a los 6 conceptos |
| 3 | User Control and Freedom | 3 | "Volver al mapa" presente; muelles no se pueden "cerrar" de nuevo (decisión de contenido, no bug de estilo) |
| 4 | Consistency and Standards | 3 | Reusa clases `.n2-*`/`.set-*` (bien), pero introduce un segundo acento (teal) sin precedente documentado |
| 5 | Error Prevention | 3 | Estados disabled presentes en botones y CTA de footer |
| 6 | Recognition Rather Than Recall | 2 | El título del rompe-hielo es un `<span>`, no un heading — debilita el escaneo de "en qué sección estoy" |
| 7 | Flexibility and Efficiency | 3 | Adecuado para una visita única al hub |
| 8 | Aesthetic and Minimalist Design | 3 | Limpio, pero rompe-hielo y muelles comparten el mismo peso visual, aplanando la jerarquía |
| 9 | Error Recovery | 3 | Feedback inline consistente con el resto de la app |
| 10 | Help and Documentation | 3 | `.n4-port-hint` funciona como ayuda inline, adecuado |
| **Total** | | **30/40** | **Good — base sólida, hay áreas débiles puntuales** |

## Anti-Patterns Verdict

**LLM (Assessment A):** No es "slop" — sistema restringido y tokenizado: superficies planas, radio de 8px consistente, un acento usado con moderación, sin gradientes morados decorativos ni Cardocalypse. El teal es una señal deliberada, no ruido decorativo — aunque su alcance creció más de lo previsto (ver Issue #4). Una textura sutil tipo "madera" (`repeating-linear-gradient`) en `.n4-card-face` roza el terreno de "textura de stock" pero es lo bastante sutil para pasar.

**Detector determinístico (Assessment B):** `detect.mjs` sobre `LevelFourLesson.tsx` → exit 0, `[]` (cero hallazgos). Nada que objetar automáticamente en este archivo.

**Evidencia de navegador (Assessment B):** Sin errores de consola relevantes. Contraste verificado por cómputo: teal `rgb(45,212,191)` sobre superficie casi negra (~10:1) y texto muted sobre superficie (~7.3:1) — ambos superan AA cómodamente (nivel AAA). El hallazgo central es estructural, no de contraste (ver Priority Issue #1).

## Overall Impression

La base es sólida y fiel al sistema documentado (plano por diseño, acento único, 8px de radio). El problema real no es "mal gusto" sino una **jerarquía visual insuficiente entre el rompe-hielo (calentamiento opcional) y los 6 muelles (la tarea real y con gate)** — combinado con un bug técnico concreto que explica por qué el aviso de gating se siente "pegado" y no bien integrado, exactamente la queja que motivó este critique.

## What's Working

1. **Disciplina de tokens real, no solo declarada**: radio de 8px consistente, bordes de 1px, superficies planas — coincide con lo documentado en DESIGN.md, no solo lo aparenta.
2. **El cambio de tinte violeta→teal al abrir un muelle** (`.n4-card.opened .n4-card-face`) es una señal no genérica y pedagógicamente legible: se escanea al instante cuáles muelles ya están completos.
3. **Colapso responsive limpio**: grid a 1 columna <900px, columnas más ajustadas <560px, sin overflow ni aplastamiento a 375px.

## Priority Issues

**[P1] El aviso de gating no tiene separación real de sus vecinos (bug técnico, no solo percepción).**
- **Por qué importa**: `.n4-shell` declara `gap: 24px` pero el elemento es `display: block` (no flex/grid), así que ese gap nunca se aplica. Medido en vivo: 0px de espacio arriba y abajo de `.n4-port-hint`. Esto es literalmente la causa técnica de tu queja anterior ("no está bien integrado con el contexto") — no era solo el color o la posición, es que no hay espacio real entre las cajas.
- **Fix**: dar a `.n4-port-hint` su propio margen vertical explícito (o convertir `.n4-shell` en una columna con gap real), sin mover ni reordenar ninguna sección.
- **Comando sugerido**: `$impeccable layout`

**[P1] La sección de rompe-hielo no tiene un heading real.**
- **Por qué importa**: "Antes de zarpar: rompiendo el hielo" vive en un `<span>` dentro de `<header>`, no en un `<h2>`. En una página con 3 zonas de contenido (bienvenida, rompe-hielo, muelles), un usuario de lector de pantalla solo tiene 1 landmark de encabezado en toda la pantalla — regresión concreta de accesibilidad (persona Sam).
- **Fix**: promover a `<h2>` (mantener el estilo visual vía clase CSS, no vía la etiqueta) — cambio de solo estilo/semántica, sin tocar copy ni orden.
- **Comando sugerido**: `$impeccable audit` o `$impeccable typeset`

**[P1] Rompe-hielo y muelles tienen el mismo peso visual — no se distingue "calentamiento" de "tarea con gate".**
- **Por qué importa**: ambos usan idéntico `border: 1px solid var(--n4-line)` + mismo fondo + mismo radio de 8px. Un estudiante que hace scroll rápido no puede distinguir "esto es opcional" de "esto es lo que debo completar" hasta leer el texto — refuerza el mismo problema de integración desde otro ángulo.
- **Fix**: bajar levemente el peso visual del contenedor del rompe-hielo (sin borde, o borde más tenue/discontinuo), sin cambiar copy ni orden.
- **Comando sugerido**: `$impeccable layout`

**[P2] El teal se convirtió en un segundo acento de facto (5+ roles), diluyendo la "Regla del Acento Único".**
- **Por qué importa**: teal aparece en el aviso de gating, el eyebrow del rompe-hielo, los eyebrows de las tarjetas de muelle, el tinte de "abierto", las etiquetas de formalización, y el botón "Zarpar" — el botón "Zarpar" es teal, no violeta, lo cual puede leerse como "este es el color de acción principal", compitiendo con el rol documentado de `#6C63FF` como único acento de CTA.
- **Esto es una pregunta de intención, no un bug claro** — ver preguntas abajo.
- **Comando sugerido**: `$impeccable colorize` (una vez resuelta la intención)

**[P2] Botones numéricos del rompe-hielo con target táctil <44px en móvil.**
- **Por qué importa**: medidos en 375px, ~36.5–40.3px de ancho — bajo el mínimo recomendado de 44×44px para un público mobile-first de adolescentes.
- **Fix**: aumentar el padding horizontal / min-width en `.n4-option-btn` cuando el contenido es un solo dígito.
- **Comando sugerido**: `$impeccable adapt`

**[P3] Sin animación de entrada que diferencie rompe-hielo de muelles** (oportunidad D2, no defecto).
**[P3] Textura "madera" en `.n4-card-face` casi invisible** — verificar si es intencional.
**[P3] `.n4-closing` usa violeta mientras el resto del hub usa teal** — inconsistencia interna menor.

## Persona Red Flags

**Jordan (primera vez, confundido)**: ve bienvenida de KatIA → texto de escena → rompe-hielo (3 preguntas) → recién ahí descubre que los 6 muelles son la tarea real. El aviso de gating es la única señal de que existe un gate, y visualmente pesa igual que el texto de alrededor (13px) — riesgo de que responda el rompe-hielo y no entienda que las tarjetas de abajo son el contenido real, no "más calentamiento".

**Casey (móvil, distraído)**: scroll largo antes del contenido interactivo (imagen de KatIA + bienvenida + escena + 3 preguntas) reduce la probabilidad de llegar al gate en una sesión corta. El aviso queda lejos en móvil.

**Sam (depende de accesibilidad)**: contraste confirmado por cómputo, sin problema ahí. Pero la falta de `<h2>` en el rompe-hielo (Issue #2) es una regresión concreta de navegación por encabezados.

## Minor Observations

- `.n4-card-closed` usa `font-style: italic` para el teaser no revelado — señal barata y razonable de "aún no disponible".
- El placeholder de imagen de KatIA (`KatiaStorySlot`, ~219×174) ocupa buena parte de la primera pantalla en 375px antes de cualquier texto — es un componente compartido fuera de estos 2 archivos, se menciona solo como aviso.
- `detect.mjs` no encontró nada — el archivo está limpio en términos del escaneo determinístico.

## Questions to Consider

1. ¿El teal debería ser un segundo acento permanente con significado propio ("estado de gating/progreso") en todos los niveles, o debería acotarse solo a este hub — y en ese caso, el botón "Zarpar" debería volver a violeta para que ese color siga significando "acción principal" en toda la app?
2. ¿El rompe-hielo debería demotarse visualmente a propósito (para que los estudiantes perciban las 6 tarjetas como "lo real"), o el peso visual igual es intencional para que el calentamiento se sienta igual de legítimo?
