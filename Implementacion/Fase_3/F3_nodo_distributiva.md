# Nodo: Máquina Distributiva — La Propiedad del Reparto
**ID:** PREALG-N3-M03-DISTRIBUTIVA

> **Nivel 3 — Propiedades.** Máquina 3 del laboratorio.

> **Origen:** Desarrolla la Página 4 del borrador + el gancho de la Página 1 (verbatim: demostración, Texto 1, operaciones, diálogos de Katia, formalización). Lo **[NUEVO]** es autoría para el calibre.

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N3-M03-DISTRIBUTIVA |
| **Título visible** | Máquina Distributiva — La Propiedad del Reparto |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 3 — Propiedades |
| **Tipo de nodo** | Máquina del laboratorio; contenido con descubrimiento guiado |
| **Ubicación en la ruta** | Máquina 3; se accede desde el hub (M00), tras M02 |
| **Función pedagógica** | Descubrir que multiplicar un número por una suma (o resta) equivale a multiplicarlo por cada término y luego sumar (o restar) los resultados |
| **Objetivo de aprendizaje** | El estudiante aplica la distributiva de la multiplicación sobre la suma y la resta, y la expresa como a × (b + c) = a × b + a × c |
| **Microhabilidades** | • Resolver multiplicando primero el paréntesis<br>• Resolver distribuyendo el factor<br>• Verificar que ambos caminos dan lo mismo<br>• Aplicar la distributiva sobre la resta<br>• Reconocer la distributiva por ambos lados |
| **Misconception tags [NUEVO]** | distribuye_solo_al_primer_termino<br>olvida_el_signo_en_la_resta<br>suma_el_factor_en_vez_de_multiplicar<br>no_respeta_prioridad_de_parentesis |
| **Personajes** | Katia (guía) |
| **Referencias de refuerzo** | M01-CONMUTATIVA · M02-ASOCIATIVA · Nivel 2 E03-MULTIPLICACION · (futuro) factorización |

> **Nota de corrección:** Sin errores matemáticos en este edificio. Notación es-CO; signo menos real (−).

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Gancho de apertura — demostración de arrastre (verbatim del hub)
```
El estudiante arrastra los números 3, 4 y 2 agrupados como 3 × (4 + 2), y la 
máquina devuelve 18. Luego los arrastra como 3 × 4 + 3 × 2, y devuelve 18. La 
máquina parpadea y Katia dice:
```
**Mensaje de Katia:**
```
¡Increíble! La multiplicación se distribuye sobre la suma.
```

#### 2.2 Texto de bienvenida (Texto 1 — verbatim)
**Diálogo de Katia:**
```
Bienvenido a la máquina distributiva. Aquí aprenderás cómo, al multiplicar un 
número por una suma o resta, será igual a multiplicar dicho número por cada uno 
de los términos que integran esa operación de manera individual y luego sumar o 
restar todos los resultados.
```

#### 2.3 Definición y ejemplos base [NUEVO]

**Diálogo de Katia (introduce la propiedad):**
```
Antes de empezar, veamos qué es distribuir.

Distribuir es repartir un factor que multiplica a una suma (o resta) entre cada 
uno de sus términos. El resultado es el mismo por los dos caminos:

a × (b + c) = a × b + a × c
```

**Ejemplo resuelto 1 (sobre la suma):**
```
2 × (5 + 3)

Camino 1 (primero el paréntesis):  2 × 8 = 16
Camino 2 (distribuyendo el 2):     2 × 5 + 2 × 3 = 10 + 6 = 16

Mismo resultado: el 2 se reparte entre el 5 y el 3.
```

**Ejemplo resuelto 2 (sobre la resta):**
```
4 × (6 − 1)

Camino 1:  4 × 5 = 20
Camino 2:  4 × 6 − 4 × 1 = 24 − 4 = 20

También funciona con la resta (cuidando el signo del segundo término).
```

#### 2.4 Instrucciones (verbatim)
```
Escribe el valor correspondiente a las siguientes operaciones matemáticas.
```

#### 2.5 Serie de operaciones con diálogos de Katia (verbatim)

**Operación 1:** 3 × (4 + 2) = 3 × 6 = **18**
**Operación 2:** (3 × 4) + (3 × 2) = 12 + 6 = **18**

**Texto 2 (Katia):**
```
Impresionante, ya veo por qué le dicen la propiedad distributiva: el número 3 
que multiplica a la suma (4 + 2) dio el mismo resultado al distribuirlo entre 
los números que se estaban sumando, o sea 4 y 2, y luego sumar el resultado. 
Interesante propiedad, pero veamos si también funciona en la resta.
```

**Operación 3:** 5 × (8 − 3) = 5 × 5 = **25**
**Operación 4:** 5 × 8 − 5 × 3 = 40 − 15 = **25**

**Texto 3 (Katia):**
```
Efectivamente, para la resta la propiedad distributiva también funciona, lo 
cual será muy importante en el futuro para los casos de factorización, en que 
tendrás que descomponer un número en una multiplicación. Por eso te recomiendo 
que la repases muy bien.
```

> [NOTA — puente a factorización] La distributiva leída al revés (a × b + a × c = a × (b + c)) es la base de la factorización por factor común, que el estudiante verá más adelante.

#### 2.6 Retroalimentación [NUEVO]

##### Resultado correcto
```
✓ Correcto. El factor se reparte entre cada término del paréntesis y el 
resultado coincide con resolver primero el paréntesis.
```

##### Si distribuye solo al primer término
```
El factor multiplica a TODOS los términos del paréntesis, no solo al primero:

3 × (4 + 2) = 3 × 4 + 3 × 2 = 12 + 6 = 18

(no 3 × 4 + 2)
```
**Misconception:** `distribuye_solo_al_primer_termino`

##### Si olvida el signo en la resta
```
Al distribuir sobre una resta, el segundo producto se RESTA:

5 × (8 − 3) = 5 × 8 − 5 × 3 = 40 − 15 = 25
```
**Misconception:** `olvida_el_signo_en_la_resta`

#### 2.7 Formalización (verbatim, con KaTeX restaurado)
```
PROPIEDAD DISTRIBUTIVA

La multiplicación es distributiva sobre la suma y la resta. Para todos los 
números a, b y c se cumple que:

a × (b + c) = a × b + a × c
a × (b − c) = a × b − a × c
(b + c) × a = b × a + c × a
(b − c) × a = b × a − c × a
```

#### 2.8 Cierre y transición [NUEVO]
**Diálogo de Katia:**
```
Ya viste cómo la multiplicación se reparte sobre la suma y la resta. Esta 
propiedad te servirá muchísimo más adelante para factorizar. En la siguiente 
máquina conoceremos a unos números muy especiales que no cambian el resultado: 
los elementos neutros.
```
**Botón:** `Volver al laboratorio`

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Interior de la máquina distributiva; casillas para factor y paréntesis. Katia presente.

#### 3.2 Interacción del estudiante
1. Gancho de arrastre (3 × (4+2), luego 3 × 4 + 3 × 2) + mensaje de Katia.
2. Lee Texto 1 y la definición + ejemplos base (dos caminos).
3. Resuelve cada pareja por los dos caminos.
4. Avanza con la flecha; lee los diálogos de Katia.
5. Tras la Operación 4, ve la formalización.
6. Lee el cierre y vuelve al laboratorio.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Gancho de arrastre | 3 × (4+2) → 18; 3 × 4 + 3 × 2 → 18 | Arrastrar | Katia: "se distribuye" |
| 2 — Bienvenida + base | Texto 1 + definición + 2 ejemplos | Continuar | Dos caminos |
| 3 — Serie de operaciones | Pareja (paréntesis vs distribuido) + campo | Entrada numérica, flecha | Katia guía |
| 4 — Retroalimentación | Resultado + Katia | Siguiente/Corregir | Diferenciada |
| 5 — Formalización | Definición de distributividad (4 formas) | Continuar | Tras la Op 4 |
| 6 — Cierre | Katia + botón | Volver al laboratorio | Completada |

#### 3.4 Animaciones (Framer Motion)
- Gancho: el factor "salta" sobre cada término del paréntesis (efecto de reparto).
- Cada pareja: se anima la distribución del factor (flechas del factor a cada término).
- Ambos caminos terminan en el mismo número, resaltado en verde.

#### 3.5 Relación con el mapa
- Máquina 3. `bloqueado→actual→completado`. Punticos: gancho, parejas validadas, formalización, completada.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Casos | Solo sobre la suma | Suma y resta | Suma, resta y forma (b±c) × a |
| Animación de reparto | Siempre | En el primer caso | Bajo demanda |
| Puente a factorización | Mencionado | Mencionado | Mini-reto inverso (factor común) |
| Pistas | Máximo | Medio | Mínimo |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Dos caminos, un resultado]** La distributiva se entiende mejor comparando el camino "resuelvo el paréntesis" con el camino "distribuyo el factor". Que ambos coincidan es la evidencia de la propiedad.

**[NOTA — El signo en la resta]** El error más común es olvidar restar el segundo producto. La retroalimentación lo aísla explícitamente.

**[NOTA — Semilla de factorización]** Leer la propiedad al revés prepara la factorización por factor común; el Texto 3 ya lo anticipa.

---

### A6. Accesibilidad [NUEVO]
- Factor y términos del paréntesis con etiquetas ARIA; animación de reparto con alternativa textual.
- Casillas de arrastre con estado por ícono además de color.
- Expresiones (a × (b + c) = a × b + a × c, 5 × (8 − 3) = 5 × 8 − 5 × 3) con KaTeX + MathML.
- Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Distributiva como base del razonamiento algebraico y la factorización:** Kieran (1992).
- **Comparación de estrategias (dos caminos):** Rittle-Johnson & Star (2007).
- **Retroalimentación formativa:** Hattie & Timperley (2007).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-maquina-interfaz], [componente-casillas-factor-parentesis], [componente-katia-dialogo], [componente-pareja-operacion], [componente-campo-numerico], [componente-animacion-reparto], [componente-boton-flecha-avanzar], [componente-retroalimentacion-modal], [componente-formalizacion-expandible], [componente-nav-volver-laboratorio].
**Tokens:** [asset-mascota:Katia], [color-acento-morado], [color-acento-teal], [color-casilla-correcta-verde], [color-casilla-incorrecta-rojo].
**Render bloqueante:** a × (b + c) = a × b + a × c, a × (b − c) = a × b − a × c, (b + c) × a = b × a + c × a, 3 × (4 + 2) = 18, 5 × (8 − 3) = 25.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N3-M03-DISTRIBUTIVA",
  "level_id": "PREALG-N3",
  "module": "Preálgebra",
  "name": "Máquina Distributiva — La Propiedad del Reparto",
  "node_type": "property_machine_guided_discovery",
  "property": "distributive",
  "position_in_route": "laboratorio_propiedades_maquina_3",
  "unlock_rule": "completed_node:PREALG-N3-M02-ASOCIATIVA",
  "previous_node_id": "PREALG-N3-M02-ASOCIATIVA",
  "next_node_id": "PREALG-N3-M04-ELEMENTO-NEUTRO",
  "order": 3,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia" },

  "corrections_applied": ["es-CO", "signo menos real (−)"],

  "mathematical_content": {
    "property": "distributive",
    "formal": "a × (b + c) = a × b + a × c",
    "variants": ["a × (b − c) = a × b − a × c", "(b + c) × a = b × a + c × a", "(b − c) × a = b × a − c × a"],
    "holds_for": "multiplicacion sobre suma y resta",
    "links_to": "factorizacion_factor_comun"
  },

  "opening_hook": {
    "type": "drag_to_slots",
    "demo": "3 × (4 + 2) = 18; 3 × 4 + 3 × 2 = 18",
    "katia_message": "¡Increíble! La multiplicación se distribuye sobre la suma."
  },

  "definition_and_worked_examples": {
    "shown_before_interaction": true,
    "definition": "Distribuir es repartir el factor entre cada término del paréntesis: a × (b + c) = a × b + a × c (igual con resta).",
    "katia_intro": "Distribuir es repartir el factor entre cada término de la suma o resta: a × (b + c) = a × b + a × c.",
    "worked_examples": [
      { "id": "WE1", "statement": "2 × (5 + 3) por dos caminos", "solution": "2 × 8 = 16; 2 × 5 + 2 × 3 = 16", "answer": 16 },
      { "id": "WE2", "statement": "4 × (6 − 1) sobre la resta", "solution": "4 × 5 = 20; 4 × 6 − 4 × 1 = 20", "answer": 20 }
    ],
    "origin": "NEW_pedagogical_addition"
  },

  "interaction": {
    "interaction_id": "PREALG-N3-M03-OPS",
    "type": "write_result_with_katia_dialogue",
    "instruction": "Escribe el valor correspondiente a las siguientes operaciones matemáticas.",
    "operation_pairs": [
      { "ops": [{"id":"O1","expr":"3 × (4 + 2)","ans":18},{"id":"O2","expr":"(3 × 4) + (3 × 2)","ans":18}], "katia_after": "Ya veo por qué le dicen distributiva: el 3 que multiplica a (4 + 2) dio lo mismo al distribuirlo entre 4 y 2 y luego sumar. Veamos si también funciona en la resta." },
      { "ops": [{"id":"O3","expr":"5 × (8 − 3)","ans":25},{"id":"O4","expr":"5 × 8 − 5 × 3","ans":25}], "katia_after": "Efectivamente, para la resta también funciona. Esto será muy importante para la factorización; repásala bien." }
    ],
    "feedback": {
      "correct": "✓ Correcto. El factor se reparte entre cada término del paréntesis y coincide con resolver primero el paréntesis.",
      "distributes_only_first": "El factor multiplica a TODOS los términos: 3 × (4 + 2) = 3 × 4 + 3 × 2 = 18 (no 3 × 4 + 2).",
      "forgets_sign": "Al distribuir sobre una resta, el segundo producto se RESTA: 5 × (8 − 3) = 5 × 8 − 5 × 3 = 25."
    },
    "feedback_origin": "katia_dialogues_VERBATIM; error_feedback_NEW"
  },

  "events_to_register": ["node_viewed","opening_hook_done","definition_and_examples_viewed","operation_submitted","pair_completed","katia_dialogue_viewed","misconception_detected","feedback_viewed","all_operations_completed","formalization_viewed","node_completed","return_to_hub"],

  "alert_conditions": [
    { "condition_id": "ALERT_OBS_DIST", "level": "observation", "trigger": "Olvida un término o el signo una vez y corrige", "message_educator": "Error puntual al distribuir, corregido. Sin acción." },
    { "condition_id": "ALERT_REINF_DIST", "level": "reinforcement_suggested", "trigger": "Distribuye solo al primer término u olvida el signo tras feedback", "message_educator": "Dificultad para distribuir a todos los términos o con el signo en la resta. Reforzar antes de avanzar." },
    { "condition_id": "ALERT_INT_PROP", "level": "teacher_intervention", "trigger": "Persisten errores con la distributiva tras feedback", "message_educator": "Dificultad persistente con la distributiva. Intervención directa recomendada." }
  ],

  "level_presentation": {
    "basico": { "cases": "solo_suma", "show_distribution_animation": "always", "hint_availability": "máximo" },
    "intermedio": { "cases": "suma_y_resta", "show_distribution_animation": "first", "hint_availability": "medio" },
    "avanzado": { "cases": "suma_resta_y_lado_derecho", "show_distribution_animation": "on_demand", "hint_availability": "mínimo", "challenge_variant": "factor_comun_inverso" }
  },

  "persistence_required": ["node_viewed","operations_validated","attempts_per_operation","misconceptions_detected","formalization_viewed","node_completed","time_on_node"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-maquina-interfaz]","[componente-casillas-factor-parentesis]","[componente-katia-dialogo]","[componente-pareja-operacion]","[componente-campo-numerico]","[componente-animacion-reparto]","[componente-boton-flecha-avanzar]","[componente-retroalimentacion-modal]","[componente-formalizacion-expandible]","[componente-nav-volver-laboratorio]"],
    "design_tokens": ["[asset-mascota:Katia]","[color-acento-morado]","[color-acento-teal]","[color-casilla-correcta-verde]","[color-casilla-incorrecta-rojo]"],
    "render_blocker": "Verificar render de: a × (b + c) = a × b + a × c, a × (b − c) = a × b − a × c, (b + c) × a = b × a + c × a, 3 × (4 + 2) = 18, 5 × (8 − 3) = 25"
  },

  "i18n_prefix": "prealgebra.n3.m03"
}
```

---

## Notas finales
Verbatim del borrador: gancho, Texto 1, las operaciones, diálogos de Katia (Texto 2–3), formalización (4 formas). **[NUEVO]:** definición + ejemplos base (dos caminos), retroalimentación, storyboard, diferenciación, notas, accesibilidad, citas, handoff, JSON. **Correcciones:** es-CO y signo menos.
