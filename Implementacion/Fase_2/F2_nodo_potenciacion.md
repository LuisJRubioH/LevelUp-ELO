# Nodo: Potenciación — La Máquina de Crecer Exponencialmente
**ID:** PREALG-N2-E05-POTENCIACION-CRECER

> **Nivel 2 — Operaciones básicas.** Edificio 5 de la ciudad.

> **Origen:** Desarrolla la Página 6 del borrador (verbatim: Texto 1, las 3 situaciones, formalización con propiedades). Lo **[NUEVO]** es autoría para el calibre. **Este edificio requirió varias correcciones** (ver nota).

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N2-E05-POTENCIACION-CRECER |
| **Título visible** | Potenciación — La Máquina de Crecer Exponencialmente |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 2 — Operaciones básicas |
| **Tipo de nodo** | Edificio de contenido con tabla temporal de crecimiento |
| **Ubicación en la ruta** | Edificio 5; se accede desde el hub (E00) |
| **Función pedagógica** | Introducir la potenciación como **multiplicación repetida** y modelar **crecimiento exponencial** (no lineal) |
| **Objetivo de aprendizaje** | El estudiante calcula potencias como producto repetido, completa una tabla de crecimiento exponencial y reconoce las propiedades básicas de la potenciación |
| **Microhabilidades** | • Interpretar aⁿ como multiplicar a por sí mismo n veces<br>• Distinguir crecimiento exponencial de lineal<br>• Completar una tabla hora a hora<br>• Reconocer base y exponente<br>• Aplicar propiedades básicas (a⁰ = 1, etc.) |
| **Misconception tags [NUEVO]** | confunde_potencia_con_multiplicacion_simple (2×3 en vez de 2³)<br>modela_crecimiento_como_lineal (suma en vez de multiplicar)<br>confunde_base_y_exponente<br>error_en_conteo_de_factores |
| **Personajes** | Katia (guía) · Juan (situación, laboratorio) |
| **Referencias de refuerzo** | E03-MULTIPLICACION (multiplicación repetida) · E06-RADICACION (inversa) |

> **Nota de corrección (varias):**
> 1. El borrador dice "crecimiento **lineal**" y "crecimiento lineal exponencial" → es **exponencial** (lineal y exponencial son opuestos; corregido en título, instrucción y notas).
> 2. El cuadro de diálogo del borrador dice "situaciones de repartición por las que pase **pablo**" → corregido a **Juan / crecimiento de bacterias** (copy-paste del edificio de División).
> 3. **Modelado [AJUSTADO]:** el borrador partía de "2 bacterias" (población = 2ⁿ⁺¹, exponente desfasado). Se reformuló para **partir de 1 individuo**, de modo que **población(hora n) = baseⁿ** y la **hora sea el exponente**. Es la realización directa de aⁿ y biológicamente válida (una bacteria que se divide). Notación es-CO.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Texto de bienvenida (Texto 1 — verbatim)
**Diálogo de Katia:**
```
Bienvenido al edificio de la potenciación. Aquí aprenderás a calcular el 
resultado de multiplicar un número por sí mismo varias veces, de forma 
eficiente. Para eso ayudaremos a Juan a calcular el crecimiento de bacterias 
dentro de su laboratorio.
```

#### 2.2 Instrucciones (verbatim, corregido)
```
Juan es un científico que trabaja en un laboratorio y desea calcular el 
crecimiento EXPONENCIAL que tienen unas bacterias después de unas cuantas 
horas. Para eso, indica debajo de cada hora el número de bacterias que habrá 
según el crecimiento.
```
> Corrección aplicada: "crecimiento lineal exponencial" → "crecimiento exponencial".

#### 2.3 Descripción de la interacción (verbatim, corregido)
```
Se mostrará una serie de recuadros de horas, desde la hora 0 hasta la hora 5. 
De acuerdo con la situación y sus directrices, el estudiante deberá indicar la 
cantidad de bacterias que hay en cada una de las horas correspondientes.
```
> Corrección aplicada: el borrador decía "situaciones de repartición por las que pase pablo" → reemplazado por la descripción correcta (Juan, crecimiento).

#### 2.4 Definición y ejemplos base [NUEVO]

> Se presenta **antes** de la práctica, como definición y modelo a imitar.

**Diálogo de Katia (introduce la operación):**
```
Antes de ayudar a Juan, veamos qué es una potencia.

Elevar a una potencia es multiplicar la base por sí misma tantas veces como 
indique el exponente. Se escribe aⁿ: a es la base y n es el exponente.

aⁿ = a × a × … × a   (n veces)
```

**Ejemplo resuelto 1 (potencia ≠ multiplicación simple):**
```
2³ no es 2 × 3.

2³ = 2 × 2 × 2 = 8

El exponente 3 dice cuántas veces se repite el 2 como factor.
```

**Ejemplo resuelto 2:**
```
3² = 3 × 3 = 9

Por eso una población que empieza en 3 y se triplica pasa de 3 a 9 en una hora.
```

---

#### 2.5 Las 3 situaciones (cuadros de diálogo — [AJUSTADO] desde el borrador)

> **Ajuste de modelado:** el borrador partía de "2 bacterias" (población = 2ⁿ⁺¹). Se reformuló para **partir de 1 individuo**, de modo que la población sea una **potencia pura** y la **hora coincida con el exponente**: población(hora n) = baseⁿ. Es la realización más directa de aⁿ y es biológicamente válido (una bacteria que se divide).

##### Situación 1
```
Juan tiene 1 bacteria que después de cada hora se duplica. ¿Cuál será la 
población de la bacteria en las siguientes horas?
```
**Tabla esperada (factor ×2):**

| Hora | 0 | 1 | 2 | 3 | 4 | 5 |
|------|---|---|---|---|---|---|
| Bacterias | 1 | 2 | 4 | 8 | 16 | 32 |
| Como potencia | 2⁰ | 2¹ | 2² | 2³ | 2⁴ | 2⁵ |

> Población(hora n) = 2ⁿ. La hora es el exponente.

##### Situación 2
```
Juan tiene 1 bacteria que después de cada hora se triplica. ¿Cuál será la 
población de la bacteria en las siguientes horas?
```
**Tabla esperada (factor ×3):**

| Hora | 0 | 1 | 2 | 3 |
|------|---|---|---|---|
| Bacterias | 1 | 3 | 9 | 27 |
| Como potencia | 3⁰ | 3¹ | 3² | 3³ |

> Población(hora n) = 3ⁿ.

##### Situación 3
```
Juan tiene 1 bacteria que después de cada hora se quintuplica. ¿Cuál será la 
población de la bacteria en las siguientes horas?
```
**Tabla esperada (factor ×5):**

| Hora | 0 | 1 | 2 | 3 |
|------|---|---|---|---|
| Bacterias | 1 | 5 | 25 | 125 |
| Como potencia | 5⁰ | 5¹ | 5² | 5³ |

> Población(hora n) = 5ⁿ.

#### 2.6 Intervención de Katia — exponencial vs lineal [NUEVO]
```
Fíjate en algo importante: la población no crece sumando siempre lo mismo (eso 
sería lineal). Cada hora se MULTIPLICA por el mismo número. Por eso pasa de 1 a 
2, a 4, a 8… cada vez salta más. A esto lo llamamos crecimiento exponencial, y 
lo escribimos con potencias: en la hora n hay 2ⁿ bacterias.
```

#### 2.7 Retroalimentación diferenciada [NUEVO]

##### Correcta
```
✓ Correcto. Cada hora se multiplica por el mismo factor: 2 → 4 → 8 → 16. 
Multiplicar un número por sí mismo varias veces es elevarlo a una potencia.
```

##### Si modela como lineal (suma el mismo número)
```
Aquí no sumamos siempre 2. Cada hora la población se MULTIPLICA por 2:

2 × 2 = 4,  4 × 2 = 8,  8 × 2 = 16…

Ese crecimiento que se acelera es exponencial, no lineal.
```
**Misconception:** `modela_crecimiento_como_lineal`

##### Si confunde potencia con multiplicación simple (2³ = 6)
```
2³ no es 2 × 3. Es multiplicar el 2 por sí mismo 3 veces:

2³ = 2 × 2 × 2 = 8

El exponente dice cuántas veces se repite la base como factor.
```
**Misconception:** `confunde_potencia_con_multiplicacion_simple`

#### 2.8 Formalización (verbatim, KaTeX restaurado)
```
POTENCIACIÓN

Operación que consiste en multiplicar un número (base) por sí mismo tantas 
veces como indique otro número (exponente). Se denota aⁿ, donde a es la base y 
n es el exponente.

Formalmente:

aⁿ = a × a × … × a   (n veces)

Propiedades:
• Producto de potencias de igual base:   aⁿ × aᵐ = aⁿ⁺ᵐ
• Cociente de potencias de igual base:   aⁿ ÷ aᵐ = aⁿ⁻ᵐ   (a ≠ 0)
• Potencia de una potencia:              (aⁿ)ᵐ = aⁿˣᵐ
• Exponente cero:                        a⁰ = 1   (a ≠ 0)
• Exponente negativo:                    a⁻ⁿ = 1/aⁿ   (a ≠ 0)
• Distributiva sobre la multiplicación:  (a × b)ⁿ = aⁿ × bⁿ
• Distributiva sobre la división:        (a ÷ b)ⁿ = aⁿ ÷ bⁿ   (b ≠ 0)
```

#### 2.9 Cierre y transición [NUEVO]
**Diálogo de Katia:**
```
Ya sabes que elevar a una potencia es multiplicar un número por sí mismo varias 
veces, y que así se modela el crecimiento exponencial. En el último edificio 
haremos la pregunta inversa: si sé el resultado, ¿cuál era el número? Eso es la 
radicación.
```
**Botón:** `Volver a la ciudad`

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Laboratorio de Juan; placas de cultivo y una línea temporal con recuadros de horas (0–5).

#### 3.2 Interacción
1. Lee la situación. 2. Completa la población hora a hora en los recuadros. 3. Valida. 4. Katia conecta con potencias y con exponencial vs lineal. 5. Repite S1–S3. 6. Formalización. 7. Cierre.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Bienvenida | Katia + Juan + Texto 1 | Instrucciones | — |
| 2 — Definición y ejemplos | Definición de la operación + 1–2 ejemplos resueltos | Continuar | Base antes de practicar |
| 3 — Tabla horas | Recuadros 0–5 + campos | Entrada numérica, Validar | Una situación por vez |
| 4 — Intervención | Katia: exponencial vs lineal | Continuar | Tras validar |
| 5 — Retroalimentación | Resultado + Katia | Siguiente/Corregir | Diferenciada |
| 6 — Formalización | Definición y 7 propiedades | Continuar | Tras S3 |
| 7 — Cierre | Katia + botón | Volver a la ciudad | Completado |

#### 3.4 Animaciones (Framer Motion)
- Las bacterias se multiplican visualmente al pasar de una hora a la siguiente (cada placa se llena más rápido).
- La curva de crecimiento se dibuja acelerándose (contraste con una recta lineal punteada).
- Validación verde / error ámbar.

#### 3.5 Relación con el mapa
- Edificio 5. `bloqueado→actual→completado`. Punticos: S1–S3 validadas, intervención vista, formalización, completado.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Horas a completar | Hasta hora 3 | Hasta hora 4–5 | Hasta hora 5 + pedir la potencia |
| Columna "como potencia" | Mostrada | Semi-oculta | Oculta (la deduce) |
| Propiedades formalizadas | a⁰ = 1 y producto de potencias | + cociente y potencia de potencia | Todas (incl. negativo) |
| Pistas | Máximo | Medio | Mínimo |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Exponencial ≠ lineal]** La corrección conceptual central del borrador: el crecimiento por multiplicación repetida es exponencial. La intervención de Katia y la curva acelerada (vs recta) lo hacen visible.

**[NOTA — Modelado población = baseⁿ]** Cada situación parte de **1** individuo que se multiplica por la base cada hora, así que en la hora n hay baseⁿ. La hora coincide con el exponente, lo que hace la tabla una lectura directa de las potencias. La columna "como potencia" muestra 2⁰, 2¹, 2²… para que el estudiante vea el exponente crecer con la hora.

**[NOTA — Potencia ≠ multiplicación simple]** El error 2³ = 6 (en vez de 8) es frecuente; la retroalimentación lo ataca mostrando los factores repetidos.

---

### A6. Accesibilidad [NUEVO]
- Recuadros de horas como campos con etiqueta ("hora 3, bacterias"); tabla navegable por teclado.
- Notación de potencias (aⁿ, 2³, a⁰ = 1, a⁻ⁿ = 1/aⁿ) con KaTeX + MathML; vocalizar "dos elevado a tres".
- Estados con íconos ✓/⚠. Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Crecimiento exponencial; concepciones erróneas exponencial/lineal:** Confrey & Smith (1994).
- **Potenciación como multiplicación repetida:** marco de aritmética avanzada (anclar a fuente del proyecto).
- **Retroalimentación formativa:** Hattie & Timperley (2007).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-katia-dialogo], [componente-personaje-situacion:Juan], [componente-tabla-horas], [componente-campo-numerico], [componente-curva-crecimiento], [componente-boton-validar], [componente-retroalimentacion-modal], [componente-formalizacion-expandible], [componente-nav-volver-ciudad].
**Tokens:** [asset-mascota:Katia], [asset-personaje:Juan], [color-acento-morado], [color-acento-teal].
**Render bloqueante:** aⁿ, 2³ = 8, 2ⁿ, aⁿ × aᵐ = aⁿ⁺ᵐ, aⁿ ÷ aᵐ = aⁿ⁻ᵐ, (aⁿ)ᵐ = aⁿˣᵐ, a⁰ = 1, a⁻ⁿ = 1/aⁿ, (a × b)ⁿ = aⁿ × bⁿ, (a ÷ b)ⁿ = aⁿ ÷ bⁿ. **Crítico:** superíndices deben renderizar (riesgo alto de exponentes vacíos).

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N2-E05-POTENCIACION-CRECER",
  "level_id": "PREALG-N2",
  "module": "Preálgebra",
  "name": "Potenciación — La Máquina de Crecer Exponencialmente",
  "node_type": "operation_building_growth_table",
  "operation": "exponentiation",
  "position_in_route": "ciudad_operaciones_edificio_5",
  "unlock_rule": "completed_hub_cards:PREALG-N2-E00-CIUDAD",
  "previous_node_id": "PREALG-N2-E04-DIVISION-REPARTIR",
  "next_node_id": "PREALG-N2-E06-RADICACION-RAIZ",
  "order": 5,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia", "situation": "Juan" },

  "corrections_applied": [
    "lineal->exponencial (titulo, instruccion, notas)",
    "pablo/reparticion->Juan/crecimiento (cuadro de dialogo)",
    "modelado AJUSTADO: parte de 1 -> poblacion(hora n) = baseⁿ (hora = exponente)"
  ],

  "mathematical_content": {
    "operation": "exponentiation",
    "notation": "aⁿ",
    "definition": "Multiplicar la base por sí misma tantas veces como indique el exponente.",
    "formal": "aⁿ = a × a × … × a (n veces)",
    "growth_type": "exponential",
    "growth_model": "poblacion(hora_n) = baseⁿ; se parte de 1 individuo que se multiplica por la base cada hora; la hora es el exponente",
    "properties": {
      "product_same_base": "aⁿ × aᵐ = aⁿ⁺ᵐ",
      "quotient_same_base": "aⁿ ÷ aᵐ = aⁿ⁻ᵐ (a ≠ 0)",
      "power_of_power": "(aⁿ)ᵐ = aⁿˣᵐ",
      "zero_exponent": "a⁰ = 1 (a ≠ 0)",
      "negative_exponent": "a⁻ⁿ = 1/aⁿ (a ≠ 0)",
      "distributive_over_multiplication": "(a × b)ⁿ = aⁿ × bⁿ",
      "distributive_over_division": "(a ÷ b)ⁿ = aⁿ ÷ bⁿ (b ≠ 0)"
    }
  },

  "definition_and_worked_examples": {
    "shown_before_interaction": true,
    "definition": "Elevar a una potencia es multiplicar la base por sí misma tantas veces como el exponente. aⁿ = a × a × … × a (n veces).",
    "katia_intro": "Una potencia aⁿ es multiplicar la base a por sí misma n veces.",
    "worked_examples": [
      { "id": "WE1", "statement": "2³ (no es 2×3)", "solution": "2 × 2 × 2 = 8", "answer": 8 },
      { "id": "WE2", "statement": "3²", "solution": "3 × 3 = 9", "answer": 9 }
    ],
    "origin": "NEW_pedagogical_addition"
  },

  "interaction": {
    "interaction_id": "PREALG-N2-E05-GROWTH",
    "type": "fill_growth_table_per_hour",
    "situations": [
      { "id": "S1", "prompt": "Juan tiene 1 bacteria que cada hora se duplica. ¿Cuál será la población en las siguientes horas?", "factor": 2, "start": 1,
        "table": { "0": 1, "1": 2, "2": 4, "3": 8, "4": 16, "5": 32 }, "as_power": "2ⁿ" },
      { "id": "S2", "prompt": "Juan tiene 1 bacteria que cada hora se triplica. ¿Cuál será la población en las siguientes horas?", "factor": 3, "start": 1,
        "table": { "0": 1, "1": 3, "2": 9, "3": 27 }, "as_power": "3ⁿ" },
      { "id": "S3", "prompt": "Juan tiene 1 bacteria que cada hora se quintuplica. ¿Cuál será la población en las siguientes horas?", "factor": 5, "start": 1,
        "table": { "0": 1, "1": 5, "2": 25, "3": 125 }, "as_power": "5ⁿ" }
    ],
    "katia_intervention": "La población no crece sumando siempre lo mismo (eso sería lineal). Cada hora se MULTIPLICA por el mismo número, por eso salta de 1 a 2 a 4 a 8. Eso es crecimiento exponencial: en la hora n hay 2ⁿ bacterias.",
    "feedback": {
      "correct": "✓ Correcto. Cada hora se multiplica por el mismo factor: 2 → 4 → 8 → 16. Multiplicar un número por sí mismo varias veces es elevarlo a una potencia.",
      "linear_model": "Aquí no sumamos siempre 2. Cada hora se MULTIPLICA por 2: 2×2=4, 4×2=8, 8×2=16. Ese crecimiento que se acelera es exponencial.",
      "power_as_product": "2³ no es 2 × 3. Es 2 × 2 × 2 = 8: el exponente dice cuántas veces se repite la base como factor."
    },
    "feedback_origin": "NEW_not_in_source_draft; katia_intervention_NEW"
  },

  "events_to_register": ["node_viewed","instructions_opened","definition_and_examples_viewed","situation_presented","hour_value_submitted","situation_validated","katia_intervention_viewed","misconception_detected","feedback_viewed","situation_corrected","all_situations_completed","formalization_viewed","node_completed","return_to_hub"],

  "alert_conditions": [
    { "condition_id": "ALERT_OBS_POW", "level": "observation", "trigger": "Error de conteo de factores puntual corregido", "message_educator": "Error puntual al contar factores, corregido. Sin acción." },
    { "condition_id": "ALERT_REINF_LINEAR", "level": "reinforcement_suggested", "trigger": "Modela como lineal o confunde potencia con multiplicación tras feedback", "message_educator": "Dificultad para distinguir crecimiento exponencial de lineal o para entender la potencia. Reforzar con la tabla y la curva." },
    { "condition_id": "ALERT_INT_POW", "level": "teacher_intervention", "trigger": "Errores persistentes en las 3 situaciones tras feedback", "message_educator": "Dificultad persistente con la potenciación. Intervención directa recomendada." }
  ],

  "level_presentation": {
    "basico": { "max_hour": 3, "show_power_column": true, "properties": ["zero_exponent","product_same_base"], "hint_availability": "máximo" },
    "intermedio": { "max_hour": 5, "show_power_column": "semi", "properties": ["zero_exponent","product_same_base","quotient_same_base","power_of_power"], "hint_availability": "medio" },
    "avanzado": { "max_hour": 5, "show_power_column": false, "ask_for_power": true, "properties": "all", "hint_availability": "mínimo" }
  },

  "persistence_required": ["node_viewed","tables_completed","attempts_per_situation","misconceptions_detected","formalization_viewed","node_completed","time_on_node"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-katia-dialogo]","[componente-personaje-situacion:Juan]","[componente-tabla-horas]","[componente-campo-numerico]","[componente-curva-crecimiento]","[componente-boton-validar]","[componente-retroalimentacion-modal]","[componente-formalizacion-expandible]","[componente-nav-volver-ciudad]"],
    "design_tokens": ["[asset-mascota:Katia]","[asset-personaje:Juan]","[color-acento-morado]","[color-acento-teal]"],
    "render_blocker": "Verificar render de superíndices: aⁿ, 2³ = 8, 2ⁿ, aⁿ × aᵐ = aⁿ⁺ᵐ, aⁿ ÷ aᵐ = aⁿ⁻ᵐ, (aⁿ)ᵐ = aⁿˣᵐ, a⁰ = 1, a⁻ⁿ = 1/aⁿ, (a×b)ⁿ = aⁿ×bⁿ, (a÷b)ⁿ = aⁿ÷bⁿ"
  },

  "i18n_prefix": "prealgebra.n2.e05"
}
```

---

## Notas finales
Verbatim del borrador: Texto 1, las 3 situaciones, formalización con las 7 propiedades. **[NUEVO]:** intervención de Katia (exponencial vs lineal), retroalimentaciones por error, storyboard, diferenciación, notas, accesibilidad, citas, handoff, JSON.
**Correcciones aplicadas:** "lineal"→"exponencial"; "pablo/repartición"→"Juan/crecimiento"; modelado AJUSTADO población(hora n) = baseⁿ (parte de 1, hora = exponente); es-CO. **Riesgo de render:** superíndices (exponentes) — verificar especialmente.
