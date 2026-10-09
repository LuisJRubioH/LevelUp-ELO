# Nodo: Máquina Asociativa — La Propiedad de la Agrupación
**ID:** PREALG-N3-M02-ASOCIATIVA

> **Nivel 3 — Propiedades.** Máquina 2 del laboratorio.

> **Origen:** Desarrolla la Página 3 del borrador + el gancho de la Página 1 (verbatim: demostración, Texto 1, operaciones, diálogos de Katia, formalización). Lo **[NUEVO]** es autoría para el calibre. **Requirió corrección conceptual** (ver nota).

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N3-M02-ASOCIATIVA |
| **Título visible** | Máquina Asociativa — La Propiedad de la Agrupación |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 3 — Propiedades |
| **Tipo de nodo** | Máquina del laboratorio; contenido con descubrimiento guiado |
| **Ubicación en la ruta** | Máquina 2; se accede desde el hub (M00), tras M01 |
| **Función pedagógica** | Descubrir que al operar tres o más números, la forma de **agrupar** no cambia el resultado en la suma y la multiplicación, pero sí en la resta y la división |
| **Objetivo de aprendizaje** | El estudiante reconoce la asociatividad, la distingue de la conmutatividad (agrupar ≠ reordenar) y la expresa como (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c) |
| **Microhabilidades** | • Operar respetando el agrupamiento (paréntesis primero)<br>• Comparar resultados según el agrupamiento<br>• Reconocer que + y × son asociativas<br>• Reconocer que − y ÷ no lo son<br>• Distinguir agrupar de reordenar |
| **Misconception tags [NUEVO]** | confunde_asociativa_con_conmutativa<br>cree_que_resta_es_asociativa<br>cree_que_division_es_asociativa<br>ignora_prioridad_de_parentesis |
| **Personajes** | Katia (guía) |
| **Referencias de refuerzo** | M01-CONMUTATIVA · M03-DISTRIBUTIVA · Nivel 2 (operaciones, jerarquía de paréntesis) |

> **Nota de corrección (conceptual):** El borrador "comprobaba" la asociatividad de la suma con (12 + 5) + (24 + 15) vs (24 + 12) + (15 + 5). Ese par **reordena** los números (24, 12, 15, 5), por lo que mezcla la **conmutativa** con la **asociativa**. La asociatividad pura mantiene **el mismo orden** y solo cambia el **agrupamiento**. Se reemplazó por **(12 + 5) + 24 = 12 + (5 + 24)** (mismo orden, distinta agrupación). También se unificó la doble etiqueta "Texto 5" del borrador. Notación es-CO.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Gancho de apertura — demostración de arrastre (verbatim del hub)
```
El estudiante arrastra los números 2, 3 y 4 agrupados como (2 + 3) + 4, y la 
máquina devuelve 9. Luego los arrastra como 2 + (3 + 4), y devuelve 9. La 
máquina parpadea y Katia dice:
```
**Mensaje de Katia:**
```
¡Extraño! La forma de agrupar no cambia el resultado.
```

#### 2.2 Texto de bienvenida (Texto 1 — verbatim)
**Diálogo de Katia:**
```
Bienvenido a la máquina asociativa. Aquí aprenderás en cuáles operaciones 
básicas, al operar tres o más números, el resultado no cambia sin importar 
cómo se agrupen o asocien los términos.
```

#### 2.3 Definición y ejemplos base [NUEVO]

**Diálogo de Katia (introduce la propiedad):**
```
Antes de empezar, veamos qué es asociar.

Asociar es agrupar los números (con paréntesis) para decidir qué operación se 
hace primero, SIN cambiar el orden de los números. Una operación es asociativa 
si, al cambiar solo el agrupamiento, el resultado no cambia:

(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)

Ojo: asociar no es lo mismo que conmutar. Conmutar cambia el ORDEN; asociar 
cambia el AGRUPAMIENTO (el orden se mantiene).
```

**Ejemplo resuelto 1 (la suma SÍ es asociativa):**
```
(2 + 3) + 4   →   5 + 4 = 9
2 + (3 + 4)   →   2 + 7 = 9

Mismo orden (2, 3, 4), distinto agrupamiento, mismo resultado: la suma es 
asociativa.
```

**Ejemplo resuelto 2 (la resta NO es asociativa):**
```
(8 − 3) − 2   →   5 − 2 = 3
8 − (3 − 2)   →   8 − 1 = 7

Mismo orden, distinto agrupamiento, distinto resultado: la resta no es 
asociativa.
```

#### 2.4 Instrucciones (verbatim)
```
Escribe el valor correspondiente a las siguientes operaciones matemáticas.
```

#### 2.5 Serie de operaciones con diálogos de Katia (verbatim + corrección)

**Operación 1:** (2 + 3) + 4 = **9**
**Operación 2:** 2 + (3 + 4) = **9**

**Texto 2 (Katia):**
```
Ok, ahora que estamos con 3 números diferentes, vemos que la suma se conserva 
igual, pero verifiquémoslo con otros valores.
```

**Operación 3 [CORREGIDA]:** (12 + 5) + 24 = **41**
**Operación 4 [CORREGIDA]:** 12 + (5 + 24) = **41**

> [CORRECCIÓN] El borrador usaba (12 + 5) + (24 + 15) vs (24 + 12) + (15 + 5), que reordena los números. Se reemplazó por un par de **mismo orden** (12, 5, 24) y distinto agrupamiento, que es asociatividad pura.

**Texto 3 (Katia):**
```
Efectivamente, sin importar cómo agrupemos los números, la suma da el mismo 
resultado. Ahora pasemos a la multiplicación.
```

**Operación 5:** (2 × 3) × 4 = **24**
**Operación 6:** 2 × (3 × 4) = **24**

**Texto 4 (Katia):**
```
Excelente: la multiplicación, al igual que la suma, no cambia su resultado 
según la forma en que se agrupen los números. Ahora veamos qué tal con la resta.
```

**Operación 7:** (8 − 3) − 2 = **3**
**Operación 8:** 8 − (3 − 2) = **7**

**Texto 5 (Katia):**
```
Ohhh, vaya sorpresa: con la resta, al operar varios números y cambiar el 
agrupamiento, el resultado se altera. Ahora veamos qué tal con la división.
```

**Operación 9:** (12 ÷ 4) ÷ 2 = **1,5**
**Operación 10:** 12 ÷ (4 ÷ 2) = **6**

**Texto 6 (Katia):**
```
Al parecer la resta y la división son bien rebeldes: les haces unos pequeños 
cambios al agrupamiento y ya te dan otra cosa completamente diferente.
```

> [NOTA] El borrador etiquetaba este último diálogo también como "Texto 5"; se renumeró a **Texto 6**. es-CO: (12 ÷ 4) ÷ 2 = 1,5.

#### 2.6 Retroalimentación [NUEVO]

##### Resultado correcto
```
✓ Correcto. Resolviste primero lo que está dentro del paréntesis. Si al cambiar 
solo el agrupamiento el resultado es el mismo, la operación es asociativa.
```

##### Si confunde asociativa con conmutativa
```
Cuidado: aquí no cambiamos el ORDEN de los números, solo el AGRUPAMIENTO 
(los paréntesis). El orden se mantiene. Cambiar el orden es la propiedad 
conmutativa; cambiar el agrupamiento es la asociativa.
```
**Misconception:** `confunde_asociativa_con_conmutativa`

##### Si ignora la prioridad del paréntesis
```
Recuerda: primero se resuelve lo que está dentro del paréntesis.

(8 − 3) − 2 = 5 − 2 = 3
8 − (3 − 2) = 8 − 1 = 7
```
**Misconception:** `ignora_prioridad_de_parentesis`

#### 2.7 Formalización (verbatim, con KaTeX restaurado)
```
PROPIEDAD ASOCIATIVA

Una operación ⊕ es asociativa si para todos los números a, b y c se cumple que:

(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)

• Operaciones asociativas:    Suma (+) y Multiplicación (×).
• Operaciones NO asociativas: Resta (−) y División (÷).
```

#### 2.8 Cierre y transición [NUEVO]
**Diálogo de Katia:**
```
Ya tienes dos propiedades: conmutar (cambiar el orden) y asociar (cambiar el 
agrupamiento). La suma y la multiplicación cumplen ambas; la resta y la 
división, ninguna. En la siguiente máquina veremos cómo se relacionan la 
multiplicación y la suma: la propiedad distributiva.
```
**Botón:** `Volver al laboratorio`

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Interior de la máquina asociativa; casillas con paréntesis. Katia presente.

#### 3.2 Interacción del estudiante
1. Gancho de arrastre ((2+3)+4, luego 2+(3+4)) + mensaje de Katia.
2. Lee Texto 1 y la definición + ejemplos base (con el contraste asociar≠conmutar).
3. Resuelve cada pareja respetando los paréntesis.
4. Avanza con la flecha; lee los diálogos de Katia.
5. Tras la Operación 10, ve la formalización.
6. Lee el cierre y vuelve al laboratorio.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Gancho de arrastre | (2+3)+4 → 9; 2+(3+4) → 9 | Arrastrar | Katia: "agrupar no cambia" |
| 2 — Bienvenida + base | Texto 1 + definición + 2 ejemplos | Continuar | Asociar ≠ conmutar |
| 3 — Serie de operaciones | Pareja con paréntesis + campo | Entrada numérica, flecha | Katia guía entre parejas |
| 4 — Retroalimentación | Resultado + Katia | Siguiente/Corregir | Diferenciada |
| 5 — Formalización | Definición de asociatividad | Continuar | Tras la Op 10 |
| 6 — Cierre | Katia + botón | Volver al laboratorio | Completada |

#### 3.4 Animaciones (Framer Motion)
- Gancho: los paréntesis se mueven (reagrupan) y la máquina parpadea.
- Cada pareja: se resalta primero el paréntesis resuelto, luego el resultado.
- Resta/división: al cambiar el agrupamiento, los resultados distintos se contrastan.

#### 3.5 Relación con el mapa
- Máquina 2. `bloqueado→actual→completado`. Punticos: gancho, parejas validadas, formalización, completada.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Parejas | Suma y multiplicación + 1 resta | Las 5 parejas | Las 5 + variante con 4 números |
| Resaltado del paréntesis | Automático paso a paso | En suma/resta | El estudiante resuelve solo |
| Contraste asociar/conmutar | Explícito y repetido | Una vez | Implícito |
| Pistas | Máximo | Medio | Mínimo |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Asociar ≠ conmutar]** Es la confusión central del tema y la razón de la corrección del ejemplo del borrador: si el "ejemplo de asociatividad" reordena los números, el estudiante no puede distinguir las dos propiedades. Todos los pares de esta máquina mantienen el orden y solo cambian los paréntesis.

**[NOTA — Prioridad del paréntesis]** La asociatividad presupone que se resuelve primero lo agrupado. Reforzar esa prioridad evita el error de operar de izquierda a derecha ignorando los paréntesis.

**[NOTA — No-ejemplos]** Resta y división como no-asociativas son tan importantes como los casos que sí cumplen, para impedir la sobregeneralización.

---

### A6. Accesibilidad [NUEVO]
- Paréntesis y agrupamientos anunciados por ARIA ("abre paréntesis 3 más 4 cierra paréntesis").
- Casillas de arrastre con estado por ícono además de color; alternativa teclado/tocar.
- Expresiones ((a ⊕ b) ⊕ c = a ⊕ (b ⊕ c), (12 ÷ 4) ÷ 2 = 1,5) con KaTeX + MathML.
- Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Distinción conmutativa/asociativa; rol de no-ejemplos:** Watson & Mason (2005).
- **Prioridad de operaciones y agrupamiento:** Kieran (1979).
- **Retroalimentación formativa:** Hattie & Timperley (2007).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-maquina-interfaz], [componente-casillas-arrastre-parentesis], [componente-katia-dialogo], [componente-pareja-operacion], [componente-campo-numerico], [componente-boton-flecha-avanzar], [componente-retroalimentacion-modal], [componente-formalizacion-expandible], [componente-nav-volver-laboratorio].
**Tokens:** [asset-mascota:Katia], [color-acento-morado], [color-acento-teal], [color-casilla-correcta-verde], [color-casilla-incorrecta-rojo].
**Render bloqueante:** (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c), paréntesis, (8 − 3) − 2 = 3, 8 − (3 − 2) = 7, (12 ÷ 4) ÷ 2 = 1,5, 12 ÷ (4 ÷ 2) = 6.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N3-M02-ASOCIATIVA",
  "level_id": "PREALG-N3",
  "module": "Preálgebra",
  "name": "Máquina Asociativa — La Propiedad de la Agrupación",
  "node_type": "property_machine_guided_discovery",
  "property": "associative",
  "position_in_route": "laboratorio_propiedades_maquina_2",
  "unlock_rule": "completed_node:PREALG-N3-M01-CONMUTATIVA",
  "previous_node_id": "PREALG-N3-M01-CONMUTATIVA",
  "next_node_id": "PREALG-N3-M03-DISTRIBUTIVA",
  "order": 2,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia" },

  "corrections_applied": [
    "CONCEPTUAL: ejemplo de 'valores grandes' reformulado a asociatividad pura (mismo orden, distinto agrupamiento): (12+5)+24 = 12+(5+24)",
    "doble 'Texto 5' renumerado a Texto 6",
    "es-CO: (12 ÷ 4) ÷ 2 = 1,5"
  ],

  "mathematical_content": {
    "property": "associative",
    "formal": "(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)",
    "holds_for": ["suma", "multiplicacion"],
    "does_not_hold_for": ["resta", "division"],
    "key_distinction": "asociar cambia el AGRUPAMIENTO; conmutar cambia el ORDEN"
  },

  "opening_hook": {
    "type": "drag_to_slots",
    "demo": "(2 + 3) + 4 = 9; 2 + (3 + 4) = 9",
    "katia_message": "¡Extraño! La forma de agrupar no cambia el resultado."
  },

  "definition_and_worked_examples": {
    "shown_before_interaction": true,
    "definition": "Una operación es asociativa si al cambiar solo el agrupamiento (paréntesis), sin cambiar el orden, el resultado no cambia: (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c).",
    "katia_intro": "Asociar es agrupar con paréntesis sin cambiar el orden. (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c). No confundir con conmutar (que cambia el orden).",
    "worked_examples": [
      { "id": "WE1", "statement": "La suma SÍ es asociativa", "solution": "(2+3)+4 = 5+4 = 9; 2+(3+4) = 2+7 = 9", "answer": 9 },
      { "id": "WE2", "statement": "La resta NO es asociativa", "solution": "(8−3)−2 = 3; 8−(3−2) = 7", "note": "mismo orden, distinto resultado" }
    ],
    "origin": "NEW_pedagogical_addition"
  },

  "interaction": {
    "interaction_id": "PREALG-N3-M02-OPS",
    "type": "write_result_with_katia_dialogue",
    "instruction": "Escribe el valor correspondiente a las siguientes operaciones matemáticas.",
    "operation_pairs": [
      { "ops": [{"id":"O1","expr":"(2 + 3) + 4","ans":9},{"id":"O2","expr":"2 + (3 + 4)","ans":9}], "katia_after": "Ok, con 3 números diferentes la suma se conserva igual, pero verifiquémoslo con otros valores." },
      { "ops": [{"id":"O3","expr":"(12 + 5) + 24","ans":41},{"id":"O4","expr":"12 + (5 + 24)","ans":41}], "katia_after": "Efectivamente, sin importar cómo agrupemos, la suma da el mismo resultado. Ahora la multiplicación.", "corrected": true },
      { "ops": [{"id":"O5","expr":"(2 × 3) × 4","ans":24},{"id":"O6","expr":"2 × (3 × 4)","ans":24}], "katia_after": "La multiplicación, igual que la suma, no cambia según el agrupamiento. Ahora la resta." },
      { "ops": [{"id":"O7","expr":"(8 − 3) − 2","ans":3},{"id":"O8","expr":"8 − (3 − 2)","ans":7}], "katia_after": "Sorpresa: con la resta, cambiar el agrupamiento altera el resultado. Ahora la división." },
      { "ops": [{"id":"O9","expr":"(12 ÷ 4) ÷ 2","ans":"1,5"},{"id":"O10","expr":"12 ÷ (4 ÷ 2)","ans":6}], "katia_after": "La resta y la división son rebeldes: un pequeño cambio de agrupamiento y dan algo distinto." }
    ],
    "feedback": {
      "correct": "✓ Correcto. Resolviste primero el paréntesis. Si al cambiar solo el agrupamiento el resultado es el mismo, la operación es asociativa.",
      "confuses_with_commutative": "Aquí no cambiamos el ORDEN, solo el AGRUPAMIENTO (los paréntesis). Cambiar el orden es conmutativa; cambiar el agrupamiento es asociativa.",
      "ignores_parentheses": "Primero se resuelve el paréntesis: (8 − 3) − 2 = 5 − 2 = 3; 8 − (3 − 2) = 8 − 1 = 7."
    },
    "feedback_origin": "katia_dialogues_VERBATIM(corrected); error_feedback_NEW"
  },

  "events_to_register": ["node_viewed","opening_hook_done","definition_and_examples_viewed","operation_submitted","pair_completed","katia_dialogue_viewed","misconception_detected","feedback_viewed","all_operations_completed","formalization_viewed","node_completed","return_to_hub"],

  "alert_conditions": [
    { "condition_id": "ALERT_OBS_PAREN", "level": "observation", "trigger": "Ignora paréntesis una vez y corrige", "message_educator": "Olvido puntual de la prioridad del paréntesis, corregido. Sin acción." },
    { "condition_id": "ALERT_REINF_ASSOC_COMM", "level": "reinforcement_suggested", "trigger": "Confunde asociativa con conmutativa o cree que resta/división son asociativas tras feedback", "message_educator": "El estudiante confunde agrupar con reordenar, o sobregeneraliza la asociatividad. Reforzar el contraste y los contraejemplos." },
    { "condition_id": "ALERT_INT_PROP", "level": "teacher_intervention", "trigger": "Persisten errores conceptuales tras feedback", "message_educator": "Dificultad persistente con la asociatividad. Intervención directa recomendada." }
  ],

  "level_presentation": {
    "basico": { "pairs": "suma_mult_plus_one_resta", "highlight_parentheses": true, "hint_availability": "máximo" },
    "intermedio": { "pairs": "all", "highlight_parentheses": "suma_resta", "hint_availability": "medio" },
    "avanzado": { "pairs": "all", "highlight_parentheses": false, "hint_availability": "mínimo", "challenge_variant": "cuatro_numeros" }
  },

  "persistence_required": ["node_viewed","operations_validated","attempts_per_operation","misconceptions_detected","formalization_viewed","node_completed","time_on_node"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-maquina-interfaz]","[componente-casillas-arrastre-parentesis]","[componente-katia-dialogo]","[componente-pareja-operacion]","[componente-campo-numerico]","[componente-boton-flecha-avanzar]","[componente-retroalimentacion-modal]","[componente-formalizacion-expandible]","[componente-nav-volver-laboratorio]"],
    "design_tokens": ["[asset-mascota:Katia]","[color-acento-morado]","[color-acento-teal]","[color-casilla-correcta-verde]","[color-casilla-incorrecta-rojo]"],
    "render_blocker": "Verificar render de: (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c), (8 − 3) − 2 = 3, 8 − (3 − 2) = 7, (12 ÷ 4) ÷ 2 = 1,5, 12 ÷ (4 ÷ 2) = 6"
  },

  "i18n_prefix": "prealgebra.n3.m02"
}
```

---

## Notas finales
Verbatim del borrador: gancho, Texto 1, operaciones, diálogos de Katia, formalización. **[NUEVO]:** definición + ejemplos base (con contraste asociar≠conmutar), retroalimentación, storyboard, diferenciación, notas, accesibilidad, citas, handoff, JSON. **Correcciones:** ejemplo de asociatividad reformulado a agrupamiento puro; doble "Texto 5" → "Texto 6"; es-CO (1,5).
