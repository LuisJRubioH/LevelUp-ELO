# Nodo: Resta — La Máquina de Quitar o Comparar
**ID:** PREALG-N2-E02-RESTA-QUITAR

> **Nivel 2 — Operaciones básicas.** Edificio 2 de la ciudad.

> **Origen:** Desarrolla la Página 3 del borrador (verbatim: Texto 1 —corregido—, instrucciones, las 5 situaciones, formalización). Lo **[NUEVO]** es autoría para el calibre.

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N2-E02-RESTA-QUITAR |
| **Título visible** | Resta — La Máquina de Quitar o Comparar |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 2 — Operaciones básicas |
| **Tipo de nodo** | Edificio de contenido con resolución de situaciones |
| **Ubicación en la ruta** | Edificio 2; se accede desde el hub (E00) |
| **Función pedagógica** | Introducir la resta con sus dos sentidos: **quitar** (sustraer) y **comparar** (diferencia), e introducir la deuda (resultado negativo) |
| **Objetivo de aprendizaje** | El estudiante resuelve situaciones de sustracción y comparación, y reconoce que restar puede llevar a un resultado por debajo de cero (deuda) |
| **Microhabilidades** | • Interpretar "quitar" como resta<br>• Interpretar "comparar / diferencia" como resta<br>• Resolver una situación de varios pasos (suma y resta)<br>• Reconocer la deuda como resultado negativo<br>• Verificar el resultado |
| **Misconception tags [NUEVO]** | invierte_minuendo_y_sustraendo<br>cree_que_resta_es_conmutativa<br>no_reconoce_diferencia_como_resta<br>no_representa_deuda_como_negativo<br>error_en_situacion_multipaso |
| **Personajes** | Katia (guía) · Manuel (situación) |
| **Referencias de refuerzo** | E01-SUMA (inversa) · Nivel 1 B05-ENTEROS-DEUDA (deudas y saldos) · E04-DIVISION |

> **Nota de corrección:** El borrador abre con "Bienvenido al edificio de la **suma**" → corregido a **resta** (copy-paste del edificio anterior). Notación es-CO. La Situación 5 (deuda) se conecta explícitamente con el nodo de Enteros del Nivel 1.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Texto de bienvenida (Texto 1 — verbatim, corregido)
**Diálogo de Katia:**
```
Bienvenido al edificio de la resta. Aquí aprenderás a saber cuánto te queda 
cuando quitas una cantidad, o cuánta diferencia hay entre dos cantidades. 
Para eso ayudaremos a Manuel en diferentes situaciones, escribiendo el 
resultado correspondiente.
```

#### 2.2 Instrucciones (verbatim)
```
Manuel necesita tu ayuda en una serie de situaciones dentro de su colegio. 
Para eso deberás indicar el valor correspondiente de la resta según los datos 
indicados por Manuel y darle clic en validar para comprobar el resultado.
```

#### 2.3 Descripción de la interacción (verbatim)
```
Se mostrarán una serie de situaciones en las cuales se proporcionará un valor 
inicial y una cantidad que se le restará; el estudiante tendrá que colocar el 
resultado correspondiente y darle en la casilla de validar para pasar al 
siguiente escenario.

El fondo de cada situación puede variar según el contexto (la cafetería, el 
aula de clase o la cancha deportiva).
```

#### 2.4 Definición y ejemplos base [NUEVO]

> Se presenta **antes** de la práctica, como definición y modelo a imitar.

**Diálogo de Katia (introduce la operación):**
```
Antes de ayudar a Manuel, veamos qué es restar.

Restar es quitar una cantidad (el sustraendo) de otra (el minuendo) para 
obtener la diferencia. También sirve para comparar dos cantidades. Símbolo −.

a − b = c

donde a es el minuendo, b el sustraendo y c la diferencia. Ojo: el orden 
importa, porque a − b no es lo mismo que b − a.
```

**Ejemplo resuelto 1 (quitar):**
```
Manuel tiene 10 monedas y gasta 4. ¿Cuántas le quedan?

10 − 4 = 6

Le quedan 6 monedas.
```

**Ejemplo resuelto 2 (comparar / diferencia):**
```
Manuel tiene 7 monedas y su amigo tiene 4. ¿Cuántas más tiene Manuel?

Comparamos restando: 7 − 4 = 3

Manuel tiene 3 monedas más.
```

**Diálogo de Katia (cierre del modelo):**
```
Listo. Ahora ayudemos a Manuel en sus situaciones del colegio.
```

---

#### 2.5 Las 5 situaciones (cuadros de diálogo de Manuel — verbatim)

| # | Situación | Operación | Resultado |
|---|-----------|-----------|-----------|
| 1 | "Manuel está en la tienda y tiene 10 monedas. Compra un producto que cuesta 4 monedas. ¿Cuántas monedas le quedan?" | 10 − 4 | **6** |
| 2 | "Manuel tiene 7 monedas y su amigo tiene 4. ¿Cuántas monedas más tienes que tu amigo?" | 7 − 4 | **3** (comparación) |
| 3 | "Manuel se encuentra en la cancha enumerada, está en el número 7 y da 3 saltos hacia atrás. ¿En qué casilla se encuentra ahora?" | 7 − 3 | **4** (recta) |
| 4 | "Manuel tiene 5 monedas y le hace un favor a la profesora; como recompensa le dan 3 monedas, así que ahora tiene 8 monedas, pero decide comprar un dulce que cuesta 3 monedas. ¿Cuántas monedas le quedan ahora?" | 5 + 3 − 3 | **5** (multipaso) |
| 5 | "Manuel tiene 2 monedas y necesita comprar una cartulina que cuesta 8 monedas; el tendero le dice que le dé lo que tiene y el resto se lo paga después. ¿Cuánto queda debiendo Manuel en la tienda?" | 2 − 8 | **−6** (deuda) |

> **[NOTA — los tres sentidos]** Las situaciones cubren intencionadamente: quitar (S1), comparar/diferencia (S2), desplazamiento en la recta (S3), multipaso suma-resta (S4) y deuda/resultado negativo (S5). La S5 enlaza con el nodo de Enteros del Nivel 1.

#### 2.6 Retroalimentación por situación [NUEVO]

##### Correcta (general)
```
✓ Correcto. Restar es quitar o comparar: partiste del valor inicial y 
hallaste lo que queda o la diferencia.
```

##### S2 — si responde 4 o intenta "comparar sumando"
```
Para saber cuántas monedas MÁS tiene Manuel, comparamos las dos cantidades 
restando:

7 − 4 = 3

La diferencia también es una resta.
```
**Misconception:** `no_reconoce_diferencia_como_resta`

##### Si invierte minuendo y sustraendo (p. ej. S1: 4 − 10)
```
Cuidado con el orden. En la resta, primero va la cantidad que tienes 
(minuendo) y luego la que quitas (sustraendo):

10 − 4 = 6,  no  4 − 10.

La resta no es conmutativa: a − b no es lo mismo que b − a.
```
**Misconception:** `invierte_minuendo_y_sustraendo`

##### S4 — error de multipaso
```
Vamos por partes:

Manuel tenía 5, le dan 3 → 5 + 3 = 8.
Luego gasta 3 → 8 − 3 = 5.

Le quedan 5 monedas.
```
**Misconception:** `error_en_situacion_multipaso`

##### S5 — no representa la deuda como negativo
```
Manuel tiene 2 y debe pagar 8. Le falta para completar:

2 − 8 = −6

Queda debiendo 6 monedas. Cuando lo que falta supera lo que se tiene, el 
resultado es negativo: una deuda. (Lo viste con los enteros en el nivel 
anterior.)
```
**Misconception:** `no_representa_deuda_como_negativo`

#### 2.7 Formalización (verbatim, KaTeX restaurado)
```
RESTA (Sustracción)

Operación binaria que consiste en quitar una cantidad (sustraendo) de otra 
(minuendo) para obtener la diferencia. Se denota con el símbolo −.

Formalmente:

a − b = c

donde a es el minuendo, b es el sustraendo y c es la diferencia.

• La resta NO es conmutativa:  a − b ≠ b − a  (en general)
• La resta NO es asociativa:   (a − b) − c ≠ a − (b − c)  (en general)
• Es la operación inversa de la suma:  a − b = c  ⇔  a = b + c
```

#### 2.8 Cierre y transición [NUEVO]
**Diálogo de Katia:**
```
Ya sabes quitar y comparar, e incluso reconocer una deuda. En el siguiente 
edificio veremos una forma rápida de sumar muchas veces lo mismo: la 
multiplicación.
```
**Botón:** `Volver a la ciudad`

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Fondo variable (cafetería / aula / cancha) según la situación. Katia + Manuel.

#### 3.2 Interacción
1. Lee la situación de Manuel. 2. Escribe el resultado. 3. Valida. 4. Ve retroalimentación. 5. Corrige si hace falta. 6. Avanza. Repite las 5. 7. Formalización. 8. Cierre.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Bienvenida | Katia + Manuel + Texto 1 | Instrucciones | — |
| 2 — Definición y ejemplos | Definición de la operación + 1–2 ejemplos resueltos | Continuar | Base antes de practicar |
| 3 — Situación activa | Enunciado + campo numérico + Validar | Entrada numérica | Fondo contextual |
| 4 — Retroalimentación | Resultado + Katia | Siguiente/Corregir | Diferenciada |
| 5 — Recta (S3) | Casillas numeradas, salto hacia atrás | Animación/selección | Modelo de recta |
| 6 — Formalización | Definición y propiedades de la resta | Continuar | Tras la 5.ª |
| 7 — Cierre | Katia + botón | Volver a la ciudad | Completado |

#### 3.4 Animaciones (Framer Motion)
- S3: ficha de Manuel salta hacia atrás 3 casillas en la recta.
- S5: el contador cruza el 0 hacia el negativo (color de deuda).
- Validación correcta: verde; error: ámbar.

#### 3.5 Relación con el mapa
- Edificio 2. Estados `bloqueado→actual→completado`. Punticos: cada situación validada, formalización, completado.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Situaciones | S1–S3 (sin multipaso ni deuda) | S1–S5 | S1–S5 + variante de deuda mayor |
| Apoyo recta numérica | Visible siempre | En S3 | Bajo demanda |
| Deuda (S5) | Guiada con recta | Aparece | Variante: "¿y si debía y le pagan?" |
| Pistas | Máximo | Medio | Mínimo |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Resta tiene dos sentidos]** Quitar (S1) y comparar/diferencia (S2) suelen enseñarse por separado; aquí conviven para que el estudiante reconozca ambos como la misma operación.

**[NOTA — No conmutatividad situada]** La retroalimentación de inversión de orden ataca la idea de que "da igual el orden", anclándola a la situación (no puedes quitar 10 de 4).

**[NOTA — Puente a enteros]** La S5 reactiva la deuda como negativo (Nivel 1, Enteros), consolidando la transferencia entre niveles.

---

### A6. Accesibilidad [NUEVO]
- Campo numérico con etiqueta y validación accesible; recta (S3) navegable y descrita por ARIA.
- Estados con íconos ✓/⚠ además de color; resultado negativo anunciado como "menos seis / deuda".
- Expresiones (a − b = c, a − b ≠ b − a, a = b + c, 2 − 8 = −6) con KaTeX + MathML.
- Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Sentidos de la resta (quitar/comparar):** Carpenter & Moser (1984).
- **Números negativos como deuda:** (anclar a la fuente usada en Nivel 1 / Enteros).
- **Retroalimentación formativa:** Hattie & Timperley (2007).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-katia-dialogo], [componente-personaje-situacion:Manuel], [componente-situacion-fondo-variable], [componente-campo-numerico], [componente-boton-validar], [componente-recta-numerica], [componente-retroalimentacion-modal], [componente-formalizacion-expandible], [componente-nav-volver-ciudad].
**Tokens:** [asset-mascota:Katia], [asset-personaje:Manuel], [color-acento-morado], [color-deuda-negativo].
**Render bloqueante:** −, =, ≠, a − b = c, a − b ≠ b − a, a = b + c, 2 − 8 = −6.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N2-E02-RESTA-QUITAR",
  "level_id": "PREALG-N2",
  "module": "Preálgebra",
  "name": "Resta — La Máquina de Quitar o Comparar",
  "node_type": "operation_building_situations",
  "operation": "subtraction",
  "position_in_route": "ciudad_operaciones_edificio_2",
  "unlock_rule": "completed_hub_cards:PREALG-N2-E00-CIUDAD",
  "previous_node_id": "PREALG-N2-E01-SUMA-JUNTAR",
  "next_node_id": "PREALG-N2-E03-MULTIPLICACION-AGRUPAR",
  "order": 2,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia", "situation": "Manuel" },

  "mathematical_content": {
    "operation": "subtraction",
    "symbol": "−",
    "definition": "Quitar el sustraendo del minuendo para obtener la diferencia.",
    "formal": "a − b = c",
    "properties": {
      "commutative": false,
      "associative": false,
      "inverse_of": "addition",
      "inverse_relation": "a − b = c ⇔ a = b + c"
    },
    "senses": ["quitar", "comparar_diferencia", "desplazamiento_recta"],
    "introduces_negative_result": true
  },

  "definition_and_worked_examples": {
    "shown_before_interaction": true,
    "definition": "Restar es quitar el sustraendo del minuendo para obtener la diferencia; también compara cantidades. Símbolo −. a − b = c (el orden importa).",
    "katia_intro": "Restar es quitar una cantidad (sustraendo) de otra (minuendo) para obtener la diferencia; también sirve para comparar. a − b = c, y a − b ≠ b − a.",
    "worked_examples": [
      { "id": "WE1", "statement": "Manuel tiene 10 monedas y gasta 4.", "solution": "10 − 4 = 6", "answer": 6, "sense": "quitar" },
      { "id": "WE2", "statement": "Manuel tiene 7 y su amigo 4: ¿cuántas más tiene Manuel?", "solution": "7 − 4 = 3", "answer": 3, "sense": "comparar" }
    ],
    "origin": "NEW_pedagogical_addition"
  },

  "interaction": {
    "interaction_id": "PREALG-N2-E02-INPUT",
    "type": "numeric_input_per_situation",
    "situations": [
      { "id": "S1", "prompt": "Manuel está en la tienda y tiene 10 monedas. Compra un producto que cuesta 4 monedas. ¿Cuántas monedas le quedan?", "expr": "10 − 4", "answer": 6, "sense": "quitar" },
      { "id": "S2", "prompt": "Manuel tiene 7 monedas y su amigo tiene 4. ¿Cuántas monedas más tiene que su amigo?", "expr": "7 − 4", "answer": 3, "sense": "comparar" },
      { "id": "S3", "prompt": "Manuel está en la casilla número 7 y da 3 saltos hacia atrás. ¿En qué casilla se encuentra ahora?", "expr": "7 − 3", "answer": 4, "sense": "recta" },
      { "id": "S4", "prompt": "Manuel tiene 5 monedas, le dan 3 (ahora 8) y compra un dulce de 3. ¿Cuántas le quedan?", "expr": "5 + 3 − 3", "answer": 5, "sense": "multipaso" },
      { "id": "S5", "prompt": "Manuel tiene 2 monedas y la cartulina cuesta 8; paga lo que tiene y debe el resto. ¿Cuánto queda debiendo?", "expr": "2 − 8", "answer": -6, "sense": "deuda" }
    ],
    "feedback": {
      "correct": "✓ Correcto. Restar es quitar o comparar: partiste del valor inicial y hallaste lo que queda o la diferencia.",
      "difference_not_subtraction": "Para saber cuántas monedas MÁS tiene, comparamos restando: 7 − 4 = 3. La diferencia también es una resta.",
      "inverted_order": "Cuidado con el orden. Primero el minuendo, luego el sustraendo: 10 − 4 = 6, no 4 − 10. La resta no es conmutativa.",
      "multistep": "Por partes: 5 + 3 = 8; luego 8 − 3 = 5. Le quedan 5 monedas.",
      "debt_not_negative": "Manuel tiene 2 y debe pagar 8: 2 − 8 = −6. Queda debiendo 6: cuando falta más de lo que hay, el resultado es negativo (deuda)."
    },
    "feedback_origin": "NEW_not_in_source_draft"
  },

  "events_to_register": ["node_viewed","instructions_opened","definition_and_examples_viewed","situation_presented","answer_submitted","situation_validated","misconception_detected","feedback_viewed","situation_corrected","all_situations_completed","formalization_viewed","node_completed","return_to_hub"],

  "alert_conditions": [
    { "condition_id": "ALERT_OBS_ORDER", "level": "observation", "trigger": "Invierte orden una vez y corrige", "message_educator": "Confusión puntual de orden en la resta, corregida. Sin acción." },
    { "condition_id": "ALERT_REINF_DIFF_DEBT", "level": "reinforcement_suggested", "trigger": "Falla comparación (S2) o deuda (S5) tras feedback", "message_educator": "Dificultad con la resta como diferencia o con la deuda negativa. Reforzar, enlazando con Enteros del Nivel 1." },
    { "condition_id": "ALERT_INT_SUB", "level": "teacher_intervention", "trigger": "Errores persistentes en 3+ situaciones tras feedback", "message_educator": "Dificultad persistente con la resta. Intervención directa recomendada." }
  ],

  "level_presentation": {
    "basico": { "situations": ["S1","S2","S3"], "number_line_always": true, "default_expanded": true, "hint_availability": "máximo" },
    "intermedio": { "situations": "all", "number_line_always": false, "default_expanded": false, "hint_availability": "medio" },
    "avanzado": { "situations": "all", "default_expanded": false, "hint_availability": "mínimo", "challenge_variant": "deuda_mayor" }
  },

  "persistence_required": ["node_viewed","situations_validated","attempts_per_situation","misconceptions_detected","formalization_viewed","node_completed","time_on_node"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-katia-dialogo]","[componente-personaje-situacion:Manuel]","[componente-situacion-fondo-variable]","[componente-campo-numerico]","[componente-boton-validar]","[componente-recta-numerica]","[componente-retroalimentacion-modal]","[componente-formalizacion-expandible]","[componente-nav-volver-ciudad]"],
    "design_tokens": ["[asset-mascota:Katia]","[asset-personaje:Manuel]","[color-acento-morado]","[color-deuda-negativo]"],
    "render_blocker": "Verificar render de: −, =, ≠, a − b = c, a − b ≠ b − a, a = b + c, 2 − 8 = −6"
  },

  "i18n_prefix": "prealgebra.n2.e02"
}
```

---

## Notas finales
Verbatim del borrador: Texto 1 (corregido suma→resta), instrucciones, interacción, las 5 situaciones, formalización. **[NUEVO]:** retroalimentaciones diferenciadas, storyboard, diferenciación, notas, accesibilidad, citas, handoff, JSON. **Correcciones:** "suma"→"resta"; es-CO; S5 enlazada con Enteros (Nivel 1).
