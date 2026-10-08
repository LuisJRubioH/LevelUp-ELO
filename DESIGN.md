---
name: LevelUp-ELO (Oulad)
description: Plataforma educativa adaptativa con motor ELO vectorial y tutora socrática KatIA
colors:
  canvas: "#0A0A0F"
  surface: "#12121A"
  accent: "#6C63FF"
  success: "#22C55E"
  error: "#EF4444"
  warning: "#F59E0B"
  elo-gold: "#FFD700"
  katia-purple: "#8B5CF6"
  text-primary: "#F1F5F9"
  text-muted: "#94A3B8"
  focus-ring: "#A78BFA"
typography:
  display:
    fontFamily: "Poppins, system-ui, sans-serif"
    fontSize: "clamp(1.8rem, 4vw, 2.8rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 900
    letterSpacing: "0.04em"
  pixel:
    fontFamily: "'Press Start 2P', monospace"
rounded:
  sm: "8px"
  md: "12px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "14px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  button-primary-hover:
    backgroundColor: "oklch(from {colors.accent} calc(l + 0.06) c h)"
  card-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "16px"
---

# Design System: LevelUp-ELO (Oulad)

## 1. Overview

**Creative North Star: "El Tablero del Ascenso"**

Oulad no se ve como un dashboard SaaS ni como una app escolar infantil: se ve como el
tablero de una partida seria que sí importa — un rango, una racha, una zona de práctica
donde cada respuesta mueve un número real. El fondo es casi negro (#0A0A0F), las
superficies son paneles planos de bajo contraste entre sí (#12121A), y el único color que
se permite gritar es el acento violeta (#6C63FF): aparece en botones primarios, focus
rings y acentos narrativos (KatIA), nunca como fondo decorativo de una sección completa.

Sobre esa base plana, cada nivel de Preálgebra abre su propio mundo narrativo (el ágora
griega para operaciones/propiedades, El Puerto de la Polis para divisibilidad) contado por
KatIA — pero el mundo narrativo es atmósfera, nunca reemplaza la jerarquía de datos: el
guión pedagógico de la pantalla (qué se enseña, en qué orden) manda sobre el lore.

Este sistema rechaza explícitamente: gradientes morados decorativos, tarjetas anidadas
("Cardocalypse"), Inter sin escala tipográfica clara, bajo contraste sobre fondo oscuro, y
el look de SaaS corporativo genérico.

**Key Characteristics:**
- Fondo casi negro + superficie ligeramente más clara, sin gradientes de fondo.
- Un solo acento violeta, usado con moderación (botones primarios, focus, KatIA).
- Bordes de 1px muy sutiles (14% opacidad) como separador por defecto, no sombra.
- Radio de esquina consistente en 8px — nunca "pill" salvo en badges/chips reales.
- Tipografía de 3 registros: Poppins (display/headings), Inter (cuerpo/UI), Press Start 2P
  (KatIA, badges de rango — uso decorativo puntual, nunca para texto largo).

## 2. Colors

Paleta restringida: neutros oscuros + un acento violeta que carga la intención (CTAs,
estado activo, foco), más 3 colores semánticos de estado (éxito/error/warning) que solo
aparecen en feedback, nunca como decoración.

### Primary
- **Violeta Ascenso** (`#6C63FF`): acento único. Botones primarios, KatIA, focus ring,
  bordes/glows de tarjetas activas. Regla dura: no debe cubrir una sección completa como
  fondo — es acento, no superficie.

### Neutral
- **Canvas** (`#0A0A0F`): fondo de página, el negro más profundo del sistema.
- **Surface** (`#12121A`): paneles, tarjetas, contenedores — un paso más claro que canvas,
  nunca igual (evita que tarjetas se fundan con el fondo).
- **Texto primario** (`#F1F5F9`): texto de cuerpo y headings sobre fondo oscuro.
- **Texto muted** (`#94A3B8`): texto secundario, subtítulos, metadatos.

### Named Rules
**La Regla del Acento Único.** Solo `#6C63FF` (violeta) actúa como color de intención en
toda la superficie de producto. Ningún otro color (dorado ELO, morado KatIA, verde/rojo de
estado) compite por ese rol — cada uno vive en su contexto específico (rango, tutora,
feedback) y no se usa para CTAs genéricos.

**La Regla del Escalón de Superficie.** `surface` (#12121A) siempre debe ser perceptiblemente
distinto de `canvas` (#0A0A0F) que lo contiene. Si un componente nuevo usa el mismo color
de fondo que su contenedor, se funde visualmente — usar `color-mix` para aclarar/oscurecer,
nunca repetir el valor exacto.

## 3. Typography

**Display Font:** Poppins (con system-ui, sans-serif de respaldo)
**Body Font:** Inter (con system-ui, sans-serif de respaldo)
**Label/Mono Font:** "Press Start 2P" (monospace pixel-art, solo KatIA y badges de rango)

**Character:** Poppins da peso y calidez a los títulos de nivel/nodo; Inter mantiene el
cuerpo legible y neutro; Press Start 2P es la única nota "gamer" explícita, reservada a
momentos puntuales (avatar de KatIA, insignias) para no saturar la lectura.

### Hierarchy
- **Display** (700, `clamp(1.8rem, 4vw, 2.8rem)`, line-height 1.1): títulos de nivel/nodo
  ("El Puerto de la Polis").
- **Label** (900, 12px, letter-spacing 0.04em, uppercase): eyebrows/kickers de KatIA,
  etiquetas de tarjeta ("RUTA A CORINTO", "GATING DEL PUERTO").
- **Body** (400, 16px, line-height 1.5): texto narrativo y de enunciados.
- **Body muted** (400, 16px, color texto muted): subtítulos, intros, metadatos.

### Named Rules
**La Regla del Pixel Puntual.** "Press Start 2P" nunca se usa para texto corrido — solo
para el nombre de KatIA, badges de rango y micro-etiquetas de una o dos palabras. Usarlo en
un párrafo es ilegible y rompe la jerarquía.

## 4. Elevation

Sistema plano por diseño: las superficies están en reposo sin sombra. La separación entre
paneles se logra con un borde de 1px muy sutil (`color-mix` de blanco al 14% sobre negro) y
un salto de tono de fondo (`surface` vs `canvas`), no con `box-shadow`. La única sombra
real del sistema es el glow del botón primario, que es una señal de intención (CTA), no
decoración ambiental.

### Shadow Vocabulary
- **Glow de CTA primario** (`box-shadow: 0 10px 24px -14px rgba(109,40,217,0.9)`): exclusivo
  del botón primario violeta; comunica "esta es la acción principal", no se replica en
  otros componentes.
- **Borde de separación** (`border: 1px solid rgba(241,245,249,0.14)`): el mecanismo por
  defecto para distinguir un panel/tarjeta de su contenedor.

### Named Rules
**La Regla Plana-en-Reposo.** Ningún panel, tarjeta o input lleva sombra en estado de
reposo. La sombra aparece únicamente como respuesta a estado (hover, focus, el CTA
primario) — nunca como estilo ambiental de fondo.

## 5. Components

### Buttons
- **Shape:** `border-radius: 12px` (rounded-xl), nunca pill salvo badges/chips reales.
- **Primary:** fondo `#6C63FF` (violeta-600), texto blanco, glow de CTA (ver Elevation).
- **Secondary:** borde sutil + fondo surface, texto primario.
- **Ghost:** transparente en reposo, borde/fondo surface solo en hover.
- **Hover / Focus:** `active:` desplaza 1px + escala 0.99 (feedback táctil); foco con
  `outline-offset` violeta.
- **Disabled:** `opacity: 50%` + `cursor: not-allowed` — es la única señal de estado
  deshabilitado; debe combinarse con copy explícito cercano (nunca dejar un botón opaco sin
  contexto de qué falta para habilitarlo).

### Cards / Containers (`.n4-practice-item` y equivalentes)
- **Corner Style:** 8px.
- **Background:** `color-mix(in srgb, surface 88%, white 3%)` — un tris más claro que el
  contenedor que lo envuelve, nunca el mismo valor.
- **Border:** 1px, tinte hacia el acento al ~22% quemado con la línea neutra (no el gris
  plano por defecto) para que la tarjeta se perciba con identidad propia.
- **Shadow Strategy:** ninguna por defecto (ver Elevation); a lo sumo una línea de
  `box-shadow` de 1px para separar del fondo, nunca blur ancho.
- **Internal Padding:** 16px.

### Labels / Eyebrows
- **Style:** texto uppercase, 12px, peso 900, color acento (violeta o teal según el nivel),
  letter-spacing 0.04em. Es el único lugar donde el color "grita" fuera del CTA primario.

### Presentación de nivel (`.level-presentation-header` / `.level-presentation-media`)
- **Sin caja:** kicker + `<h1>` + intro, sin borde ni fondo — distinto a `.katia-story-slot`
  (que sí lleva caja y es para aperturas dentro de un nodo, no para el hub del nivel).
- **Título:** `clamp(2rem, 5vw, 3.4rem)`, `text-wrap: balance`, `letter-spacing: -0.03em`.
- **Panel de imagen:** ancho completo, punteado con textura diagonal hasta tener arte real
  (`object-fit: cover` cuando hay `<img>`). Compartido por los 3 hubs de nivel (N2/N3/N4).

## 6. Do's and Don'ts

### Do:
- **Do** usar un único acento de intención (`#6C63FF`) para CTAs y estados activos en toda
  la superficie de producto.
- **Do** separar un panel de su contenedor con un salto de tono de fondo (`color-mix`) +
  borde sutil de 1px, nunca con el mismo color de fondo repetido.
- **Do** mantener las superficies planas en reposo; la sombra/glow aparece solo como
  respuesta a estado.
- **Do** dejar que el storytelling de cada nivel (ágora griega, Puerto de la Polis) sea
  telón de fondo — nunca debe tapar ni contradecir el guión pedagógico de la pantalla.
- **Do** renderizar toda expresión matemática con `react-katex`, nunca texto plano.

### Don't:
- **Don't** usar gradientes morados decorativos ni `background-clip: text` con gradiente.
- **Don't** anidar tarjetas dentro de tarjetas ("Cardocalypse").
- **Don't** usar Inter (u otra fuente) sin escala tipográfica clara — cada bloque de texto
  necesita un rol de jerarquía definido (display/label/body/muted).
- **Don't** dejar texto de bajo contraste sobre el fondo oscuro (#0A0A0F/#12121A); el texto
  muted (#94A3B8) es el piso, nunca gris más claro sobre fondo oscuro "por elegancia".
- **Don't** repetir el mismo objeto/contexto narrativo más de 2 veces en un mismo nivel de
  Preálgebra (ej. no todo son "ánforas griegas" en cada ejemplo de un nivel).
- **Don't** combinar borde de 1px + sombra ancha (blur ≥16px) en el mismo elemento — el
  patrón "ghost-card"; elegir uno.
