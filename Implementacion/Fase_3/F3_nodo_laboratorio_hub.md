# Nodo: El Laboratorio de las Propiedades Misteriosas (Hub)
**ID:** PREALG-N3-M00-LABORATORIO

> **Nivel 3 — Propiedades** (módulo Preálgebra). Pantalla de entrada / hub del laboratorio con 5 máquinas.

> **Origen:** Desarrolla la Página 1 del borrador (verbatim: Texto 1 y las descripciones de las 5 máquinas). Lo **[NUEVO]** es autoría para el calibre (gating, storyboard, accesibilidad, JSON).

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N3-M00-LABORATORIO |
| **Título visible** | El Laboratorio de las Propiedades Misteriosas |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 3 — Propiedades |
| **Tipo de nodo** | Hub / mapa del nivel (laboratorio con 5 máquinas) |
| **Ubicación en la ruta** | Entrada del Nivel 3; precede a las 5 máquinas |
| **Función pedagógica** | Presentar las propiedades de las operaciones como máquinas explorables y activar la curiosidad con una demostración por descubrimiento en cada una |
| **Objetivo de aprendizaje** | El estudiante reconoce que existen propiedades que rigen el comportamiento de las operaciones y se dispone a descubrirlas máquina por máquina |
| **Mecánica de avance** | El estudiante entra a cada máquina; al completar las 5 se cierra el nivel. Orden sugerido secuencial (las propiedades se construyen unas sobre otras) |
| **Personajes** | Katia (mascota guía) |
| **Referencias de refuerzo** | M01-CONMUTATIVA, M02-ASOCIATIVA, M03-DISTRIBUTIVA, M04-ELEMENTO-NEUTRO, M05-INVERSOS · Nivel 2 (operaciones) |

> **Nota de corrección:** Notación es-CO. Signo menos real (−). El nivel se rotula correctamente como **Nivel 3** en el borrador.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Descripción de la escena (verbatim del borrador)
```
El estudiante entra al laboratorio de propiedades misteriosas, en el cual hay 
5 máquinas industriales. El estudiante deberá ingresar a cada una, una por una. 
Una vez adentro, aparece Katia indicándole que seleccione los números 
correspondientes y los arrastre a las casillas indicadas dentro de la interfaz; 
la máquina arroja un número según el orden puesto y luego un mensaje que indica 
la propiedad que está viendo en ese momento.
```

#### 2.2 Texto de bienvenida (Texto 1 — verbatim)
**Diálogo de Katia:**
```
Hola, bienvenido al laboratorio de las propiedades misteriosas. Aquí podrás 
conocer algunas de las propiedades más importantes de los números al realizar 
operaciones matemáticas. Espero que te diviertas y te deseo el mayor de los 
éxitos.
```

#### 2.3 Las 5 máquinas (verbatim, con su demostración y mensaje de Katia)

| Máquina | Propiedad | Demostración (arrastre) | Mensaje de Katia |
|---|---|---|---|
| 1 | Conmutativa | 3 + 5 → 8; luego 5 + 3 → 8 | "¡Qué curioso! El orden no importa." |
| 2 | Asociativa | (2 + 3) + 4 → 9; luego 2 + (3 + 4) → 9 | "¡Extraño! La forma de agrupar no cambia el resultado." |
| 3 | Distributiva | 3 × (4 + 2) → 18; luego 3 × 4 + 3 × 2 → 18 | "¡Increíble! La multiplicación se distribuye sobre la suma." |
| 4 | Elemento neutro | 5 + 0 → 5; luego 5 × 1 → 5 | "Hay números que no cambian el resultado." |
| 5 | Inversos | 5 − 5 → 0; luego 5 × 1/5 → 1 | "Hay números que se cancelan entre sí." |

> Cada demostración de arrastre es el **gancho de apertura** del nodo de máquina correspondiente (ver cada F3_nodo).

#### 2.4 Regla de arrastre guiado (verbatim)
```
Para que el estudiante arrastre correctamente los números a las casillas 
indicadas, cada vez que seleccione un número, la casilla donde va se iluminará 
de verde y las demás de rojo; además, solo permitirá arrastrar el número a la 
casilla correspondiente.
```

#### 2.5 Avance [NUEVO]
**Diálogo de Katia (al completar las 5 máquinas):**
```
¡Descubriste las cinco propiedades del laboratorio! Ahora entiendes algunas de 
las reglas secretas que siguen los números cuando operamos con ellos.
```

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Vista del laboratorio con 5 máquinas industriales (cada una con su símbolo/aspecto). Katia da la bienvenida.

#### 3.2 Interacción del estudiante
1. Lee la bienvenida (Texto 1).
2. Entra a una máquina (orden sugerido M01→M05).
3. Completa la máquina (gancho de arrastre + serie guiada + formalización).
4. Vuelve al laboratorio; la máquina queda marcada como completada.
5. Repite hasta completar las 5; aparece el mensaje de avance.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Bienvenida | Laboratorio + Katia + Texto 1 | Explorar | — |
| 2 — Exploración | 5 máquinas (entrables) | Entrar a una máquina | Contador 0/5 → 5/5 |
| 3 — Completado | Máquinas completadas + mensaje de Katia | Volver / cerrar nivel | Nivel completado |

#### 3.4 Animaciones (Framer Motion)
- Máquinas con vapor/engranajes sutiles; la entrada hace zoom hacia la máquina.
- Máquina completada: luz/sello.
- Al llegar a 5/5, el laboratorio "se enciende".

#### 3.5 Relación con el mapa
- Contenedor de los 5 nodos-máquina. Estado de cada máquina: `bloqueado` → `actual` → `completado`.
- Registra qué máquinas se completaron y el progreso del nivel.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Orden | Forzado M01→M05 | Sugerido | Libre |
| Demostración de apertura | Guiada paso a paso | Estándar | Rápida |
| Pista de avance | "Te faltan N máquinas" | Contador 0/5 | Solo contador |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Aprendizaje por descubrimiento]** Cada máquina revela su propiedad mediante un contraste manipulativo (mismo cálculo, distinto orden/agrupamiento) antes de formalizar. El estudiante infiere la regla en vez de recibirla.

**[NOTA — Orden de las propiedades]** La secuencia conmutativa → asociativa → distributiva → neutro → inversos va de lo más intuitivo a lo más abstracto (los inversos sostienen el despeje de ecuaciones del futuro), por eso se sugiere recorrerlas en ese orden.

---

### A6. Accesibilidad [NUEVO]
- Máquinas navegables por teclado; cada una con etiqueta (propiedad).
- Arrastre con alternativa tocar-para-colocar; casillas con estado por ícono además de color (verde/rojo).
- Escena de laboratorio con alternativa 2D / descripción textual.
- Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Aprendizaje por descubrimiento guiado:** Bruner (1961).
- **Organizadores previos:** Ausubel (1968).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-laboratorio-escena], [componente-maquina-propiedad] (×5), [componente-katia-dialogo], [componente-contador-maquinas], [componente-gate-nivel].
**Tokens:** [asset-mascota:Katia], [asset-laboratorio-fondo], [color-acento-morado], [color-acento-teal], [color-casilla-correcta-verde], [color-casilla-incorrecta-rojo].
**Render bloqueante:** símbolos +, −, ×, ÷, ⊕, fracción 1/5, y las operaciones de las demostraciones.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N3-M00-LABORATORIO",
  "level_id": "PREALG-N3",
  "module": "Preálgebra",
  "name": "El Laboratorio de las Propiedades Misteriosas",
  "node_type": "level_hub_laboratory",
  "position_in_route": "laboratorio_propiedades_hub",
  "unlock_rule": "level_unlocked:PREALG-N3",
  "previous_node_id": null,
  "next_node_id": "PREALG-N3-M01-CONMUTATIVA",
  "order": 0,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia" },

  "welcome_text": "Hola, bienvenido al laboratorio de las propiedades misteriosas. Aquí podrás conocer algunas de las propiedades más importantes de los números al realizar operaciones matemáticas. Espero que te diviertas y te deseo el mayor de los éxitos.",

  "machines": [
    { "id": "M01", "property": "conmutativa", "node_id": "PREALG-N3-M01-CONMUTATIVA", "demo": "3 + 5 = 8; 5 + 3 = 8", "katia_message": "¡Qué curioso! El orden no importa." },
    { "id": "M02", "property": "asociativa", "node_id": "PREALG-N3-M02-ASOCIATIVA", "demo": "(2 + 3) + 4 = 9; 2 + (3 + 4) = 9", "katia_message": "¡Extraño! La forma de agrupar no cambia el resultado." },
    { "id": "M03", "property": "distributiva", "node_id": "PREALG-N3-M03-DISTRIBUTIVA", "demo": "3 × (4 + 2) = 18; 3 × 4 + 3 × 2 = 18", "katia_message": "¡Increíble! La multiplicación se distribuye sobre la suma." },
    { "id": "M04", "property": "elemento_neutro", "node_id": "PREALG-N3-M04-ELEMENTO-NEUTRO", "demo": "5 + 0 = 5; 5 × 1 = 5", "katia_message": "Hay números que no cambian el resultado." },
    { "id": "M05", "property": "inversos", "node_id": "PREALG-N3-M05-INVERSOS", "demo": "5 − 5 = 0; 5 × 1/5 = 1", "katia_message": "Hay números que se cancelan entre sí." }
  ],

  "drag_rule": "Al seleccionar un número, la casilla destino se ilumina de verde y las demás de rojo; solo se permite soltar el número en la casilla correspondiente.",

  "gating": {
    "rule": "complete_all_machines",
    "machines_required": 5,
    "suggested_order": ["M01","M02","M03","M04","M05"],
    "note": "Orden secuencial sugerido (propiedades acumulativas); sin penalización"
  },

  "events_to_register": ["hub_viewed","machine_entered","machine_completed","all_machines_completed","level_progress_updated"],

  "level_presentation": {
    "basico": { "navigation": "forced_order", "hint": "remaining_machines" },
    "intermedio": { "navigation": "suggested_order", "hint": "counter" },
    "avanzado": { "navigation": "free", "hint": "counter" }
  },

  "persistence_required": ["hub_viewed","machines_completed","level_progress"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-laboratorio-escena]","[componente-maquina-propiedad]","[componente-katia-dialogo]","[componente-contador-maquinas]","[componente-gate-nivel]"],
    "design_tokens": ["[asset-mascota:Katia]","[asset-laboratorio-fondo]","[color-acento-morado]","[color-acento-teal]","[color-casilla-correcta-verde]","[color-casilla-incorrecta-rojo]"],
    "render_blocker": "Verificar render de +, −, ×, ÷, ⊕, 1/5 y las operaciones de demostración"
  },

  "i18n_prefix": "prealgebra.n3.m00"
}
```

---

## Notas finales
Verbatim del borrador: escena, Texto 1, las 5 máquinas con su demostración y mensaje, regla de arrastre. **[NUEVO]:** gating, storyboard, diferenciación, accesibilidad, citas, handoff, JSON. **Correcciones:** es-CO y signo menos.
