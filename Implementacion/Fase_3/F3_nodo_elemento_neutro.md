# Nodo: Máquina del Elemento Neutro — La Propiedad del Que No Cambia
**ID:** PREALG-N3-M04-ELEMENTO-NEUTRO

> **Nivel 3 — Propiedades.** Máquina 4 del laboratorio.

> **Origen:** Desarrolla las Páginas 5–6 del borrador + el gancho de la Página 1 (verbatim: demostración, Texto 1, operaciones, diálogos de Katia, formalización). Lo **[NUEVO]** es autoría para el calibre. **Requirió corrección conceptual** (ver nota).

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N3-M04-ELEMENTO-NEUTRO |
| **Título visible** | Máquina del Elemento Neutro — La Propiedad del Que No Cambia |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 3 — Propiedades |
| **Tipo de nodo** | Máquina del laboratorio; contenido con descubrimiento guiado |
| **Ubicación en la ruta** | Máquina 4; se accede desde el hub (M00), tras M03 |
| **Función pedagógica** | Descubrir que la suma tiene elemento neutro 0 y la multiplicación tiene elemento neutro 1 (operan en ambos lados sin cambiar el número); y que la resta y la división **no tienen** elemento neutro (verdadero, bilateral) |
| **Objetivo de aprendizaje** | El estudiante identifica el 0 y el 1 como elementos neutros de suma y multiplicación, y entiende por qué la resta y la división no tienen elemento neutro (un neutro debe funcionar a ambos lados) |
| **Microhabilidades** | • Reconocer el 0 como neutro de la suma<br>• Reconocer el 1 como neutro de la multiplicación<br>• Verificar la neutralidad en ambos órdenes<br>• Entender que un neutro debe funcionar a ambos lados<br>• Reconocer que resta y división no tienen neutro |
| **Misconception tags [NUEVO]** | cree_que_resta_tiene_neutro<br>cree_que_division_tiene_neutro<br>acepta_neutro_de_un_solo_lado<br>confunde_0_y_1_como_neutros |
| **Personajes** | Katia (guía) |
| **Referencias de refuerzo** | M01-CONMUTATIVA · M05-INVERSOS · Nivel 2 E01-SUMA, E03-MULTIPLICACION |

> **Nota de corrección (conceptual):** El borrador (Texto 4 y Texto 5) afirma que la resta y la división "sí tienen elemento neutro, pero solo a la derecha". Eso **contradice** la formalización del propio borrador ("Resta: No tiene elemento neutro"). Un elemento neutro **verdadero debe funcionar en ambos lados** (a ⊕ e = e ⊕ a = a). Como el 0 en la resta solo funciona por la derecha (a − 0 = a, pero 0 − a = −a ≠ a), la resta **NO tiene** elemento neutro; igual la división con el 1. Se reescribieron los Texto 4 y Texto 5 para decir que 0 y 1 son **"neutros por la derecha"** pero **no elementos neutros verdaderos**, alineando el diálogo con la formalización. Además se **renumeraron** las operaciones repetidas (dos "13/14") y se cambiaron los ":" por "=". Notación es-CO; signo menos real (−).

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Gancho de apertura — demostración de arrastre (verbatim del hub)
```
El estudiante arrastra los números 5 y 0 agrupados como 5 + 0, y la máquina 
devuelve 5. Luego arrastra 5 y 1 agrupados como 5 × 1, y devuelve 5. La máquina 
parpadea y Katia dice:
```
**Mensaje de Katia:**
```
Hay números que no cambian el resultado.
```

#### 2.2 Texto de bienvenida (Texto 1 — verbatim)
**Diálogo de Katia:**
```
Bienvenido a la máquina del elemento neutro. Aquí aprenderás cómo, en ciertas 
operaciones matemáticas, existe un valor específico que, al operar con cualquier 
otro número, no altera ni modifica su valor original, sin importar incluso el 
orden en que se exprese.
```

#### 2.3 Definición y ejemplos base [NUEVO]

**Diálogo de Katia (introduce la propiedad):**
```
Antes de empezar, veamos qué es un elemento neutro.

Un elemento neutro es un número que, al operarlo con cualquier otro, NO lo 
cambia, sin importar de qué lado se ponga (a ambos lados). Es la clave: debe 
funcionar a la izquierda y a la derecha.

a ⊕ e = e ⊕ a = a
```

**Ejemplo resuelto 1 (la suma SÍ tiene neutro: 0):**
```
7 + 0 = 7   y   0 + 7 = 7

El 0 no cambia el número por ningún lado: es el elemento neutro de la suma.
```

**Ejemplo resuelto 2 (la resta NO tiene neutro):**
```
6 − 0 = 6   (parece neutro)   pero   0 − 6 = −6   (¡cambia!)

Como solo funciona por un lado, el 0 NO es elemento neutro de la resta. La resta 
no tiene elemento neutro.
```

#### 2.4 Instrucciones (verbatim)
```
Escribe el valor correspondiente a las siguientes operaciones matemáticas.
```

#### 2.5 Serie de operaciones con diálogos de Katia (verbatim + corrección)

**Operación 1:** 5 + 0 = **5**
**Operación 2:** 0 + 5 = **5**
**Operación 3:** 100 + 0 = **100**
**Operación 4:** 0 + 100 = **100**

**Texto 2 (Katia):**
```
Ya pescamos nuestro primer elemento neutro: en la suma, el elemento neutro es 
el 0, que al operarlo de todas las maneras posibles no altera el resultado 
original. Ahora veamos si existe un elemento neutro para la multiplicación.
```

**Operación 5:** 8 × 1 = **8**
**Operación 6:** 1 × 8 = **8**
**Operación 7:** 150 × 1 = **150**
**Operación 8:** 1 × 150 = **150**

**Texto 3 (Katia):**
```
Para la multiplicación también identificamos un elemento neutro: en este caso 
es el 1, que no altera el resultado original en cualquier orden en que lo 
ubiquemos. Ahora veamos si existe uno para la resta.
```

**Operación 9:** 6 − 0 = **6**
**Operación 10:** 0 − 6 = **−6**
**Operación 11:** 17 − 0 = **17**
**Operación 12:** 0 − 17 = **−17**

**Texto 4 (Katia) [CORREGIDO]:**
```
Ohhh, vaya, fíjate en algo: el 0 funciona como neutro solo cuando está a la 
DERECHA (6 − 0 = 6), pero si lo ponemos a la izquierda el resultado cambia de 
signo (0 − 6 = −6). Como un elemento neutro de verdad debe funcionar por los dos 
lados, la resta NO tiene elemento neutro. Ahora veamos qué pasa con la división.
```

> [CORRECCIÓN] El borrador decía que la resta "sí posee un elemento neutro, pero solo a la derecha". Se corrigió: el 0 es solo "neutro por la derecha", y por eso la resta **no tiene** elemento neutro verdadero (debe ser bilateral). Esto alinea el diálogo con la formalización.

**Operación 13:** 4 ÷ 1 = **4**
**Operación 14:** 1 ÷ 4 = **0,25**
**Operación 15:** 8 ÷ 1 = **8**
**Operación 16:** 1 ÷ 8 = **0,125**

> [CORRECCIÓN] El borrador repetía "Operación 13/14" y usaba ":" en vez de "=". Se renumeró a 13–16 y se unificó "=". es-CO: 0,25 y 0,125.

**Texto 5 (Katia) [CORREGIDO]:**
```
Con la división pasa lo mismo que con la resta: el 1 funciona solo cuando está a 
la derecha, en el divisor (4 ÷ 1 = 4), pero si lo ponemos en el dividendo el 
resultado cambia (1 ÷ 4 = 0,25). Como no funciona por los dos lados, la división 
TAMPOCO tiene elemento neutro.
```

> [CORRECCIÓN] Igual que en la resta: el 1 es solo "neutro por la derecha" en la división, así que la división **no tiene** elemento neutro verdadero.

#### 2.6 Retroalimentación [NUEVO]

##### Resultado correcto
```
✓ Correcto. Recuerda: un elemento neutro de verdad no cambia el número por 
NINGÚN lado.
```

##### Si cree que la resta o la división tienen elemento neutro
```
Cuidado: el 0 en la resta (y el 1 en la división) solo funcionan por la 
derecha:

6 − 0 = 6  pero  0 − 6 = −6
4 ÷ 1 = 4  pero  1 ÷ 4 = 0,25

Como un elemento neutro debe funcionar por los DOS lados, la resta y la división 
no tienen elemento neutro.
```
**Misconception:** `cree_que_resta_tiene_neutro` / `cree_que_division_tiene_neutro` / `acepta_neutro_de_un_solo_lado`

##### Si confunde 0 y 1
```
El neutro de la SUMA es el 0 (a + 0 = a). El neutro de la MULTIPLICACIÓN es el 
1 (a × 1 = a). Sumar 0 o multiplicar por 1 no cambia el número.
```
**Misconception:** `confunde_0_y_1_como_neutros`

#### 2.7 Formalización (verbatim, con KaTeX restaurado)
```
ELEMENTO NEUTRO

Es un número que, al operarse con cualquier otro número, no lo modifica (por 
ambos lados).

• Elemento neutro de la suma (0):            a + 0 = 0 + a = a
• Elemento neutro de la multiplicación (1):  a × 1 = 1 × a = a
• Resta:    No tiene elemento neutro. (0 funciona solo a la derecha: a − 0 = a, 
            pero 0 − a ≠ a.)
• División: No tiene elemento neutro. (1 funciona solo a la derecha: a ÷ 1 = a, 
            pero 1 ÷ a ≠ a, excepto a = 1.)
```

#### 2.8 Cierre y transición [NUEVO]
**Diálogo de Katia:**
```
Ahora conoces a los neutros: el 0 para la suma y el 1 para la multiplicación, 
que no cambian el número por ningún lado. La resta y la división no tienen uno 
verdadero. En la última máquina veremos números que, al operarse, se cancelan y 
nos llevan justo a esos neutros: los inversos.
```
**Botón:** `Volver al laboratorio`

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Interior de la máquina del elemento neutro; casillas para el número y el candidato a neutro. Katia presente.

#### 3.2 Interacción del estudiante
1. Gancho de arrastre (5 + 0, luego 5 × 1) + mensaje de Katia.
2. Lee Texto 1 y la definición + ejemplos base (énfasis en "ambos lados").
3. Resuelve cada operación; nota cuándo el número se conserva y cuándo cambia.
4. Avanza con la flecha; lee los diálogos de Katia (con la corrección de "neutro por la derecha").
5. Tras la Operación 16, ve la formalización.
6. Lee el cierre y vuelve al laboratorio.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Gancho de arrastre | 5 + 0 → 5; 5 × 1 → 5 | Arrastrar | Katia: "no cambian" |
| 2 — Bienvenida + base | Texto 1 + definición + 2 ejemplos | Continuar | Énfasis "ambos lados" |
| 3 — Suma y multiplicación | Operaciones con 0 y con 1 | Entrada numérica, flecha | Katia: neutros |
| 4 — Resta y división | Operaciones con 0 y 1 en ambos lados | Entrada numérica, flecha | Katia: solo por la derecha → no hay neutro |
| 5 — Retroalimentación | Resultado + Katia | Siguiente/Corregir | Diferenciada |
| 6 — Formalización | Definición + 4 casos | Continuar | Tras la Op 16 |
| 7 — Cierre | Katia + botón | Volver al laboratorio | Completada |

#### 3.4 Animaciones (Framer Motion)
- Gancho: el 0 y el 1 "entran" y el número sale igual.
- Casos por la izquierda: el resultado cambia visiblemente (signo o decimal), contrastando con el caso por la derecha.
- Formalización: se resaltan los dos lados (a ⊕ e = e ⊕ a).

#### 3.5 Relación con el mapa
- Máquina 4. `bloqueado→actual→completado`. Punticos: gancho, operaciones validadas, formalización, completada.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Operaciones | Solo suma y multiplicación (neutros) | Las 16 (incluye resta/división) | Las 16 + "¿por qué no hay neutro?" |
| Énfasis "ambos lados" | Resaltado en cada caso | En resta/división | Implícito |
| Resta/división sin neutro | Guiado por Katia | Aparece | El estudiante lo justifica |
| Pistas | Máximo | Medio | Mínimo |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Bilateralidad del neutro]** Es la corrección clave del nodo: el borrador trataba el "neutro por la derecha" como un elemento neutro. Un elemento neutro verdadero debe funcionar por ambos lados; por eso la resta y la división no lo tienen. El diálogo ahora coincide con la formalización.

**[NOTA — Contraste izquierda/derecha]** Mostrar 6 − 0 (conserva) junto a 0 − 6 (cambia) hace visible por qué el lado importa. Es el corazón conceptual.

**[NOTA — Puente a inversos]** Los neutros (0 y 1) son la meta de la siguiente máquina: los inversos son los números que, al operarse, producen el neutro.

---

### A6. Accesibilidad [NUEVO]
- Cada operación con etiqueta ARIA que indique el lado del candidato a neutro ("0 a la izquierda", "0 a la derecha").
- Casillas de arrastre con estado por ícono además de color.
- Expresiones (a + 0 = 0 + a = a, a × 1 = 1 × a = a, 0 − 6 = −6, 1 ÷ 4 = 0,25) con KaTeX + MathML.
- Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Elemento neutro y estructura de las operaciones:** Gallardo & Rojano (1988).
- **Importancia de la bilateralidad; precisión en definiciones:** Vinner (1991), concept image vs concept definition.
- **Retroalimentación formativa:** Hattie & Timperley (2007).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-maquina-interfaz], [componente-casillas-numero-neutro], [componente-katia-dialogo], [componente-operacion-lado], [componente-campo-numerico], [componente-boton-flecha-avanzar], [componente-retroalimentacion-modal], [componente-formalizacion-expandible], [componente-nav-volver-laboratorio].
**Tokens:** [asset-mascota:Katia], [color-acento-morado], [color-acento-teal], [color-casilla-correcta-verde], [color-casilla-incorrecta-rojo].
**Render bloqueante:** a + 0 = 0 + a = a, a × 1 = 1 × a = a, 0 − 6 = −6, 0 − 17 = −17, 1 ÷ 4 = 0,25, 1 ÷ 8 = 0,125.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N3-M04-ELEMENTO-NEUTRO",
  "level_id": "PREALG-N3",
  "module": "Preálgebra",
  "name": "Máquina del Elemento Neutro — La Propiedad del Que No Cambia",
  "node_type": "property_machine_guided_discovery",
  "property": "identity_element",
  "position_in_route": "laboratorio_propiedades_maquina_4",
  "unlock_rule": "completed_node:PREALG-N3-M03-DISTRIBUTIVA",
  "previous_node_id": "PREALG-N3-M03-DISTRIBUTIVA",
  "next_node_id": "PREALG-N3-M05-INVERSOS",
  "order": 4,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia" },

  "corrections_applied": [
    "CONCEPTUAL: resta y división NO tienen elemento neutro (0 y 1 son solo neutros por la derecha; un neutro debe ser bilateral). Texto 4 y Texto 5 reescritos para alinear con la formalización.",
    "renumeradas operaciones repetidas (dos '13/14') -> 13–16",
    "':' cambiado por '=' en operaciones de división",
    "es-CO: 0,25 y 0,125; signo menos real (−)"
  ],

  "mathematical_content": {
    "property": "identity_element",
    "definition": "Número que no modifica a otro al operarlo, por ambos lados (a ⊕ e = e ⊕ a = a).",
    "addition_identity": "0 (a + 0 = 0 + a = a)",
    "multiplication_identity": "1 (a × 1 = 1 × a = a)",
    "subtraction": "no tiene elemento neutro (0 es solo neutro por la derecha: a − 0 = a, pero 0 − a ≠ a)",
    "division": "no tiene elemento neutro (1 es solo neutro por la derecha: a ÷ 1 = a, pero 1 ÷ a ≠ a salvo a = 1)",
    "key_idea": "un elemento neutro debe ser bilateral"
  },

  "opening_hook": {
    "type": "drag_to_slots",
    "demo": "5 + 0 = 5; 5 × 1 = 5",
    "katia_message": "Hay números que no cambian el resultado."
  },

  "definition_and_worked_examples": {
    "shown_before_interaction": true,
    "definition": "Un elemento neutro no cambia el número por ningún lado: a ⊕ e = e ⊕ a = a. Suma: 0. Multiplicación: 1. Resta y división: no tienen.",
    "katia_intro": "Un elemento neutro no cambia el número por ningún lado (izquierda y derecha): a ⊕ e = e ⊕ a = a.",
    "worked_examples": [
      { "id": "WE1", "statement": "La suma SÍ tiene neutro (0)", "solution": "7 + 0 = 7 y 0 + 7 = 7", "answer": 7 },
      { "id": "WE2", "statement": "La resta NO tiene neutro", "solution": "6 − 0 = 6 pero 0 − 6 = −6", "note": "solo funciona por la derecha → no es neutro" }
    ],
    "origin": "NEW_pedagogical_addition"
  },

  "interaction": {
    "interaction_id": "PREALG-N3-M04-OPS",
    "type": "write_result_with_katia_dialogue",
    "instruction": "Escribe el valor correspondiente a las siguientes operaciones matemáticas.",
    "operation_groups": [
      { "group": "suma", "ops": [{"id":"O1","expr":"5 + 0","ans":5},{"id":"O2","expr":"0 + 5","ans":5},{"id":"O3","expr":"100 + 0","ans":100},{"id":"O4","expr":"0 + 100","ans":100}],
        "katia_after": "Ya pescamos el primer neutro: en la suma es el 0, que no altera el resultado en ningún orden. Ahora la multiplicación." },
      { "group": "multiplicacion", "ops": [{"id":"O5","expr":"8 × 1","ans":8},{"id":"O6","expr":"1 × 8","ans":8},{"id":"O7","expr":"150 × 1","ans":150},{"id":"O8","expr":"1 × 150","ans":150}],
        "katia_after": "En la multiplicación el neutro es el 1, que no altera el resultado en ningún orden. Ahora la resta." },
      { "group": "resta", "ops": [{"id":"O9","expr":"6 − 0","ans":6},{"id":"O10","expr":"0 − 6","ans":-6},{"id":"O11","expr":"17 − 0","ans":17},{"id":"O12","expr":"0 − 17","ans":-17}],
        "katia_after": "El 0 funciona solo a la DERECHA (6 − 0 = 6); a la izquierda cambia el signo (0 − 6 = −6). Como un neutro debe funcionar por los dos lados, la resta NO tiene elemento neutro. Ahora la división.", "corrected": true },
      { "group": "division", "ops": [{"id":"O13","expr":"4 ÷ 1","ans":4},{"id":"O14","expr":"1 ÷ 4","ans":"0,25"},{"id":"O15","expr":"8 ÷ 1","ans":8},{"id":"O16","expr":"1 ÷ 8","ans":"0,125"}],
        "katia_after": "Igual que la resta: el 1 funciona solo en el divisor (4 ÷ 1 = 4); en el dividendo cambia (1 ÷ 4 = 0,25). La división TAMPOCO tiene elemento neutro.", "corrected": true }
    ],
    "feedback": {
      "correct": "✓ Correcto. Un elemento neutro de verdad no cambia el número por NINGÚN lado.",
      "thinks_has_neutral": "El 0 en la resta (y el 1 en la división) solo funcionan por la derecha: 6 − 0 = 6 pero 0 − 6 = −6; 4 ÷ 1 = 4 pero 1 ÷ 4 = 0,25. Un neutro debe funcionar por los dos lados, así que resta y división no tienen.",
      "confuses_0_and_1": "El neutro de la suma es 0 (a + 0 = a); el de la multiplicación es 1 (a × 1 = a)."
    },
    "feedback_origin": "katia_dialogues_VERBATIM(corrected); error_feedback_NEW"
  },

  "events_to_register": ["node_viewed","opening_hook_done","definition_and_examples_viewed","operation_submitted","group_completed","katia_dialogue_viewed","misconception_detected","feedback_viewed","all_operations_completed","formalization_viewed","node_completed","return_to_hub"],

  "alert_conditions": [
    { "condition_id": "ALERT_OBS_NEUTRAL", "level": "observation", "trigger": "Error puntual con 0/1 corregido", "message_educator": "Error puntual con el neutro, corregido. Sin acción." },
    { "condition_id": "ALERT_REINF_SIDED_NEUTRAL", "level": "reinforcement_suggested", "trigger": "Acepta neutro de un solo lado o cree que resta/división tienen neutro tras feedback", "message_educator": "El estudiante acepta un 'neutro' que solo funciona por un lado. Reforzar la bilateralidad del elemento neutro." },
    { "condition_id": "ALERT_INT_PROP", "level": "teacher_intervention", "trigger": "Persisten errores conceptuales sobre el neutro tras feedback", "message_educator": "Dificultad persistente con el elemento neutro. Intervención directa recomendada." }
  ],

  "level_presentation": {
    "basico": { "groups": ["suma","multiplicacion"], "emphasize_both_sides": true, "hint_availability": "máximo" },
    "intermedio": { "groups": "all", "emphasize_both_sides": "resta_division", "hint_availability": "medio" },
    "avanzado": { "groups": "all", "emphasize_both_sides": false, "ask_why_no_neutral": true, "hint_availability": "mínimo" }
  },

  "persistence_required": ["node_viewed","operations_validated","attempts_per_operation","misconceptions_detected","formalization_viewed","node_completed","time_on_node"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-maquina-interfaz]","[componente-casillas-numero-neutro]","[componente-katia-dialogo]","[componente-operacion-lado]","[componente-campo-numerico]","[componente-boton-flecha-avanzar]","[componente-retroalimentacion-modal]","[componente-formalizacion-expandible]","[componente-nav-volver-laboratorio]"],
    "design_tokens": ["[asset-mascota:Katia]","[color-acento-morado]","[color-acento-teal]","[color-casilla-correcta-verde]","[color-casilla-incorrecta-rojo]"],
    "render_blocker": "Verificar render de: a + 0 = 0 + a = a, a × 1 = 1 × a = a, 0 − 6 = −6, 0 − 17 = −17, 1 ÷ 4 = 0,25, 1 ÷ 8 = 0,125"
  },

  "i18n_prefix": "prealgebra.n3.m04"
}
```

---

## Notas finales
Verbatim del borrador: gancho, Texto 1, operaciones (renumeradas), diálogos de Katia (Texto 2–3 intactos; Texto 4–5 corregidos), formalización. **[NUEVO]:** definición + ejemplos base, retroalimentación, storyboard, diferenciación, notas, accesibilidad, citas, handoff, JSON.
**Correcciones:** la resta y la división **no tienen** elemento neutro (0 y 1 son solo neutros por la derecha; el neutro debe ser bilateral) — Texto 4 y 5 reescritos para alinear con la formalización; operaciones repetidas renumeradas a 13–16; ":" → "="; es-CO (0,25; 0,125).
