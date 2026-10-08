# Nodo: Radicación — La Máquina de Encontrar la Raíz
**ID:** PREALG-N2-E06-RADICACION-RAIZ

> **Nivel 2 — Operaciones básicas.** Edificio 6 (último) de la ciudad.

> **Origen:** Desarrolla la Página 7 del borrador (verbatim: Texto 1, las 4 situaciones con sus diálogos de Katia, formalización con propiedades). Lo **[NUEVO]** es autoría para el calibre. **Requirió corrección de unidades** (ver nota).

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N2-E06-RADICACION-RAIZ |
| **Título visible** | Radicación — La Máquina de Encontrar la Raíz |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 2 — Operaciones básicas |
| **Tipo de nodo** | Edificio de contenido con situaciones geométricas (último del nivel) |
| **Ubicación en la ruta** | Edificio 6; se accede desde el hub (E00). Cierra el nivel |
| **Función pedagógica** | Introducir la radicación como **inversa de la potenciación** (raíz cuadrada vía área, raíz cúbica vía volumen) y reconocer raíces no exactas |
| **Objetivo de aprendizaje** | El estudiante halla raíces como operación inversa de la potencia, las interpreta geométricamente y distingue raíces exactas de no exactas (irracionales) |
| **Microhabilidades** | • Interpretar √a como inversa de elevar al cuadrado<br>• Interpretar ∛a vía volumen<br>• Reconocer la radicación como inversa de la potenciación<br>• Distinguir raíz exacta de no exacta (decimal/irracional)<br>• Reconocer la condición de índice par (a ≥ 0) |
| **Misconception tags [NUEVO]** | confunde_raiz_con_division_entre_indice (√16 = 8)<br>no_relaciona_radicacion_con_potenciacion<br>cree_que_toda_raiz_es_exacta<br>error_de_unidades (lado/área)<br>ignora_restriccion_indice_par |
| **Personajes** | Katia (guía, con intervenciones conceptuales) |
| **Referencias de refuerzo** | E05-POTENCIACION (inversa) · Nivel 1 B07-IRRACIONALES (raíces no exactas) · Nivel 1 B08-REALES |

> **Nota de corrección:**
> 1. **Unidades (Situación 1):** el borrador dice "cada lado mide **4 cm**" para un área de 16 m² → corregido a **4 m** (√16 m² = 4 m). La del cubo (3 cm para 27 cm³) sí es correcta.
> 2. **es-CO:** "√20 ≈ 4.4721" → **√20 ≈ 4,4721** (coma decimal).
> 3. El Texto 1 del borrador dice "bienvenido al último de la radicación" (falta "edificio"): se completa a "último edificio".

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Texto de bienvenida (Texto 1 — verbatim, completado)
**Diálogo de Katia:**
```
Bienvenido al último edificio: el de la radicación. Aquí aprenderás a encontrar 
qué número, multiplicado por sí mismo cierta cantidad de veces, da un resultado 
específico.
```

#### 2.2 Descripción de la interacción (verbatim)
```
En este sexto y último edificio, teniendo presente la dificultad del tema, se 
diseñaron diferentes situaciones en contextos distintos para entender de manera 
profunda a qué hace alusión la radicación. El escenario y el fondo de cada 
situación cambian según las características del problema.
```

#### 2.3 Instrucciones (verbatim)
```
De acuerdo con las diferentes situaciones que se vayan presentando, determina 
el valor solicitado y dale a la opción de validar para corroborar el resultado.
```

#### 2.4 Definición y ejemplos base [NUEVO]

> Se presenta **antes** de la práctica, como definición y modelo a imitar.

**Diálogo de Katia (introduce la operación):**
```
Antes de empezar, veamos qué es una raíz.

La radicación es la operación inversa de la potenciación: busca el número 
(la raíz) que, elevado al índice, da el radicando. Se escribe ⁿ√a.

ⁿ√a = b  ⇔  bⁿ = a
```

**Ejemplo resuelto 1 (raíz cuadrada):**
```
√16 = 4, porque 4 × 4 = 16.

La raíz cuadrada deshace el cuadrado.
```

**Ejemplo resuelto 2 (raíz cúbica):**
```
∛8 = 2, porque 2 × 2 × 2 = 8.

La raíz cúbica deshace el cubo.
```

---

#### 2.5 Situación 1 — raíz cuadrada vía área (verbatim, unidad corregida)
**Cuadro de diálogo:**
```
Un jardín cuadrado tiene un área de 16 m². ¿Cuánto mide cada lado?
```
**Respuesta esperada:** 4 m

**Intervención de Katia tras validar (verbatim, corregido cm→m):**
```
Efectivamente, cada lado mide 4 m, porque recuerda que el área de un cuadrado 
sale de multiplicar la base por la altura; pero como es un cuadrado, la base y 
la altura tienen el mismo valor. Entonces simplemente había que buscar un número 
que multiplicado por sí mismo diera como resultado 16 m².
```

#### 2.6 Situación 2 — raíz cúbica vía volumen (verbatim)
**Cuadro de diálogo:**
```
Un cubo tiene un volumen de 27 cm³. ¿Cuánto mide cada arista?
```
**Respuesta esperada:** 3 cm

**Intervención de Katia tras validar (verbatim):**
```
Correcto, cada arista mide 3 cm, porque recuerda que el volumen de un cubo se 
calcula elevando a la tercera potencia la longitud de sus aristas. Entonces 
simplemente había que buscar un número que multiplicado por sí mismo 3 veces 
diera como resultado 27 cm³.
```

#### 2.7 Situación 3 — radicación como inversa (verbatim)
**Cuadro de diálogo:**
```
Muy bien, ya vimos dos situaciones con procedimientos muy cercanos a la 
potenciación. Pero entonces, si 3² = 9, ¿cuánto será √9?
```
**Respuesta esperada:** 3

**Intervención de Katia tras validar (verbatim):**
```
Muy buena observación. Tanto la radicación como la potenciación son operaciones 
inversas, como lo son la suma con la resta o la multiplicación con la división. 
Por lo tanto, √(a²) = a y (√a)² = a.
```

#### 2.8 Situación 4 — raíz no exacta (verbatim, es-CO corregido)
**Cuadro de diálogo:**
```
Un jardín cuadrado tiene un área de 20 m². ¿Cuánto mide cada lado?
```
**Respuesta esperada:** √20 ≈ 4,4721 m

**Intervención de Katia tras validar (verbatim, coma decimal):**
```
Excelente. En este caso el resultado de √20 ≈ 4,4721 da a entender que estamos 
frente a una raíz que no es exacta, sino que proporciona un resultado decimal, 
pero que no deja de ser válido.
```

> **[NOTA — puente a irracionales]** La S4 conecta con el Nivel 1 (B07 Irracionales): √20 es irracional (decimal infinito no periódico). Buen enlace entre niveles.

#### 2.9 Retroalimentación diferenciada [NUEVO]

##### Correcta (exacta)
```
✓ Correcto. La raíz es la operación inversa de la potencia: como 4 × 4 = 16, 
entonces √16 = 4.
```

##### Si confunde raíz con dividir entre el índice (√16 = 8)
```
√16 no es 16 ÷ 2. Es buscar el número que multiplicado por sí mismo da 16:

4 × 4 = 16  →  √16 = 4
```
**Misconception:** `confunde_raiz_con_division_entre_indice`

##### Si trata una raíz no exacta como exacta (S4)
```
20 no es un cuadrado perfecto. No hay un entero que multiplicado por sí mismo 
dé 20:

4 × 4 = 16   y   5 × 5 = 25

Por eso √20 ≈ 4,4721: una raíz no exacta, con decimales infinitos. (Es un 
número irracional, como viste en el nivel anterior.)
```
**Misconception:** `cree_que_toda_raiz_es_exacta`

#### 2.10 Formalización (verbatim, KaTeX restaurado)
```
RADICACIÓN

Operación inversa de la potenciación que consiste en encontrar un número (raíz) 
que, elevado a un cierto índice, da como resultado el radicando. Se denota ⁿ√a, 
donde n es el índice, a es el radicando y el resultado es la raíz.

Formalmente:

ⁿ√a = b  ⇔  bⁿ = a

Propiedades:
• Raíz de un producto:   ⁿ√(a × b) = ⁿ√a × ⁿ√b
• Raíz de un cociente:   ⁿ√(a ÷ b) = ⁿ√a ÷ ⁿ√b   (b ≠ 0)
• Raíz de una potencia:  ⁿ√(aᵐ) = a^(m/n)
• Potencia de una raíz:  (ⁿ√a)ᵐ = ⁿ√(aᵐ)
• Raíz de raíz:          ᵐ√(ⁿ√a) = ᵐˣⁿ√a
• Índice par:            √a solo está definido para a ≥ 0 (en reales); el 
                         resultado es siempre ≥ 0 (raíz principal).
• Índice impar:          ⁿ√a está definido para todo a ∈ ℝ (puede ser positivo 
                         o negativo).
```

#### 2.11 Cierre del nivel [NUEVO]
**Diálogo de Katia:**
```
¡Felicidades! Recorriste los seis edificios de la ciudad de las operaciones: 
sumar, restar, multiplicar, dividir, elevar a potencias y encontrar raíces. 
Ahora tienes las herramientas básicas para resolver casi cualquier problema 
matemático que se te presente.
```
**Botón:** `Volver a la ciudad`

> Al completar este edificio se completa el Nivel 2. (Si el producto define un cierre diagnóstico del nivel, conectar aquí.)

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Fondo variable por situación (jardín cuadrado, cubo 3D, jardín mayor). Katia como guía activa.

#### 3.2 Interacción
1. Lee la situación. 2. Determina el valor (lado/arista/raíz). 3. Valida. 4. Katia conecta con potenciación / inversa / raíz no exacta. 5. Repite S1–S4. 6. Formalización. 7. Cierre del nivel.

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Bienvenida | Katia + Texto 1 | Instrucciones | — |
| 2 — Definición y ejemplos | Definición de la operación + 1–2 ejemplos resueltos | Continuar | Base antes de practicar |
| 3 — S1 área | Jardín 16 m², lado = ? | Entrada, Validar | √ vía área |
| 4 — S2 volumen | Cubo 27 cm³, arista = ? | Entrada, Validar | ∛ vía volumen |
| 5 — S3 inversa | 3² = 9, √9 = ? | Entrada, Validar | Katia: inversa |
| 6 — S4 no exacta | Jardín 20 m², lado ≈ ? | Entrada, Validar | Raíz irracional |
| 7 — Formalización | Definición y propiedades | Continuar | — |
| 8 — Cierre nivel | Katia felicita + botón | Volver a la ciudad | Nivel completado |

#### 3.4 Animaciones (Framer Motion)
- S1: el cuadrado se forma desde el lado; área 16 ↔ lado 4.
- S2: el cubo se construye desde la arista; volumen 27 ↔ arista 3.
- S4: la raíz "no encaja" en un entero; se muestra el decimal aproximado.
- Validación verde / error ámbar.

#### 3.5 Relación con el mapa
- Edificio 6 (último). `bloqueado→actual→completado`. Al completarlo, el nivel queda cerrado.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Situaciones | S1–S3 (exactas) | S1–S4 | S1–S4 + índice impar / negativos |
| Apoyo geométrico | Figura siempre visible | S1–S2 | Simbólico |
| Raíz no exacta (S4) | Guiada (entre 4 y 5) | Aparece | Variante: estimar otras |
| Propiedades | Inversa + producto | + cociente y potencia | Todas (incl. índice par/impar) |
| Pistas | Máximo | Medio | Mínimo |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Radicación como inversa]** El borrador construye la raíz desde la geometría (área/volumen) y luego la nombra como inversa de la potencia (S3). Esta secuencia concreta→simbólica es valiosa; las intervenciones de Katia ya la traen verbatim.

**[NOTA — Raíces no exactas y puente a irracionales]** La S4 (√20) reactiva los irracionales del Nivel 1: una raíz no exacta es un decimal infinito no periódico. Refuerza la cohesión entre niveles.

**[NOTA — Unidades]** El error 4 cm vs 4 m del borrador es justo el tipo de descuido que confunde; la corrección mantiene la coherencia dimensional (√(m²) = m).

**[NOTA — Índice par]** La restricción a ≥ 0 para índice par se incluye en la formalización; conviene no exigirla como evaluación en este nivel, solo presentarla.

---

### A6. Accesibilidad [NUEVO]
- Figuras (cuadrado, cubo) con descripción ARIA y datos numéricos en texto.
- Notación radical (ⁿ√a, √16 = 4, ∛27 = 3, √20 ≈ 4,4721, ⁿ√a = b ⇔ bⁿ = a) con KaTeX + MathML; vocalizar "raíz cuadrada de…", "raíz cúbica de…".
- Estados con íconos ✓/⚠. Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Radicación como inversa; raíces no exactas e irracionales:** Sirotic & Zazkis (2007).
- **Representación geométrica de raíces:** marco de visualización matemática (anclar a fuente del proyecto).
- **Retroalimentación formativa:** Hattie & Timperley (2007).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-katia-dialogo] (con intervenciones), [componente-situacion-geometrica] (cuadrado/cubo), [componente-campo-numerico], [componente-boton-validar], [componente-retroalimentacion-modal], [componente-formalizacion-expandible], [componente-cierre-nivel], [componente-nav-volver-ciudad].
**Tokens:** [asset-mascota:Katia], [color-acento-morado], [color-acento-teal], [color-raiz-no-exacta].
**Render bloqueante:** ⁿ√a, √16 = 4, ∛27 = 3, √9 = 3, √20 ≈ 4,4721, ⁿ√a = b ⇔ bⁿ = a, ⁿ√(a×b) = ⁿ√a × ⁿ√b, ⁿ√(aᵐ) = a^(m/n), a ≥ 0. **Crítico:** índices y radicandos del radical (riesgo de radical vacío).

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N2-E06-RADICACION-RAIZ",
  "level_id": "PREALG-N2",
  "module": "Preálgebra",
  "name": "Radicación — La Máquina de Encontrar la Raíz",
  "node_type": "operation_building_geometric_last",
  "operation": "radication",
  "position_in_route": "ciudad_operaciones_edificio_6",
  "unlock_rule": "completed_hub_cards:PREALG-N2-E00-CIUDAD",
  "previous_node_id": "PREALG-N2-E05-POTENCIACION-CRECER",
  "next_node_id": null,
  "is_last_building": true,
  "order": 6,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia" },

  "corrections_applied": [
    "unidad S1: 4 cm -> 4 m (area 16 m²)",
    "es-CO: √20 ≈ 4.4721 -> 4,4721",
    "Texto 1: 'último de la radicación' -> 'último edificio: el de la radicación'"
  ],

  "mathematical_content": {
    "operation": "radication",
    "notation": "ⁿ√a",
    "definition": "Encontrar el número que, elevado al índice n, da el radicando a.",
    "formal": "ⁿ√a = b ⇔ bⁿ = a",
    "inverse_of": "exponentiation",
    "properties": {
      "root_of_product": "ⁿ√(a × b) = ⁿ√a × ⁿ√b",
      "root_of_quotient": "ⁿ√(a ÷ b) = ⁿ√a ÷ ⁿ√b (b ≠ 0)",
      "root_of_power": "ⁿ√(aᵐ) = a^(m/n)",
      "power_of_root": "(ⁿ√a)ᵐ = ⁿ√(aᵐ)",
      "root_of_root": "ᵐ√(ⁿ√a) = ^(m×n)√a",
      "even_index": "√a definido solo para a ≥ 0 (reales); raíz principal ≥ 0",
      "odd_index": "ⁿ√a definido para todo a ∈ ℝ"
    },
    "links_to": ["PREALG-N1-B07-IRRACIONALES-DECIMALES", "PREALG-N1-B08-REALES-RECTA"]
  },

  "definition_and_worked_examples": {
    "shown_before_interaction": true,
    "definition": "La radicación es la inversa de la potenciación: ⁿ√a = b ⇔ bⁿ = a (índice n, radicando a, raíz b).",
    "katia_intro": "La raíz busca el número que, elevado al índice, da el radicando: ⁿ√a = b ⇔ bⁿ = a.",
    "worked_examples": [
      { "id": "WE1", "statement": "√16", "solution": "4 × 4 = 16 → √16 = 4", "answer": 4 },
      { "id": "WE2", "statement": "∛8", "solution": "2 × 2 × 2 = 8 → ∛8 = 2", "answer": 2 }
    ],
    "origin": "NEW_pedagogical_addition"
  },

  "interaction": {
    "interaction_id": "PREALG-N2-E06-GEOMETRIC",
    "type": "geometric_situations_with_katia_intervention",
    "situations": [
      { "id": "S1", "prompt": "Un jardín cuadrado tiene un área de 16 m². ¿Cuánto mide cada lado?", "expr": "√16", "answer": "4 m", "context": "area_square", "exact": true,
        "katia_after": "Efectivamente, cada lado mide 4 m, porque el área de un cuadrado es base × altura, pero al ser cuadrado ambas son iguales: bastaba buscar un número que multiplicado por sí mismo diera 16 m²." },
      { "id": "S2", "prompt": "Un cubo tiene un volumen de 27 cm³. ¿Cuánto mide cada arista?", "expr": "∛27", "answer": "3 cm", "context": "volume_cube", "exact": true,
        "katia_after": "Correcto, cada arista mide 3 cm, porque el volumen de un cubo es la arista elevada al cubo: bastaba buscar un número que multiplicado por sí mismo 3 veces diera 27 cm³." },
      { "id": "S3", "prompt": "Si 3² = 9, ¿cuánto será √9?", "expr": "√9", "answer": 3, "context": "inverse", "exact": true,
        "katia_after": "Muy buena observación. La radicación y la potenciación son operaciones inversas, como suma/resta o multiplicación/división. Por lo tanto, √(a²) = a y (√a)² = a." },
      { "id": "S4", "prompt": "Un jardín cuadrado tiene un área de 20 m². ¿Cuánto mide cada lado?", "expr": "√20", "answer": "≈ 4,4721 m", "context": "area_square", "exact": false,
        "katia_after": "Excelente. √20 ≈ 4,4721 da a entender que estamos frente a una raíz que no es exacta, sino que da un resultado decimal, pero que no deja de ser válido." }
    ],
    "feedback": {
      "correct": "✓ Correcto. La raíz es la inversa de la potencia: como 4 × 4 = 16, entonces √16 = 4.",
      "root_as_division": "√16 no es 16 ÷ 2. Es buscar el número que multiplicado por sí mismo da 16: 4 × 4 = 16 → √16 = 4.",
      "assumes_exact": "20 no es cuadrado perfecto: 4×4=16 y 5×5=25. Por eso √20 ≈ 4,4721, una raíz no exacta con decimales infinitos (irracional)."
    },
    "feedback_origin": "katia_interventions_VERBATIM(corrected); error_feedback_NEW"
  },

  "events_to_register": ["node_viewed","instructions_opened","definition_and_examples_viewed","situation_presented","answer_submitted","situation_validated","katia_intervention_viewed","misconception_detected","feedback_viewed","situation_corrected","all_situations_completed","formalization_viewed","level_completed","return_to_hub"],

  "alert_conditions": [
    { "condition_id": "ALERT_OBS_ROOT", "level": "observation", "trigger": "Confunde raíz puntualmente y corrige", "message_educator": "Confusión puntual con la raíz, corregida. Sin acción." },
    { "condition_id": "ALERT_REINF_INEXACT_INVERSE", "level": "reinforcement_suggested", "trigger": "Cree que toda raíz es exacta o no la relaciona con la potencia tras feedback", "message_educator": "Dificultad con raíces no exactas o con la radicación como inversa. Reforzar enlazando con Potenciación (E05) e Irracionales (Nivel 1)." },
    { "condition_id": "ALERT_INT_RAD", "level": "teacher_intervention", "trigger": "Errores persistentes en 3+ situaciones tras feedback", "message_educator": "Dificultad persistente con la radicación. Intervención directa recomendada." }
  ],

  "level_presentation": {
    "basico": { "situations": ["S1","S2","S3"], "show_figure": "always", "properties": ["inverse","root_of_product"], "hint_availability": "máximo" },
    "intermedio": { "situations": "all", "show_figure": "S1_S2", "properties": ["inverse","root_of_product","root_of_quotient","root_of_power"], "hint_availability": "medio" },
    "avanzado": { "situations": "all", "show_figure": "symbolic", "properties": "all", "hint_availability": "mínimo", "challenge_variant": "indice_impar_negativos" }
  },

  "persistence_required": ["node_viewed","situations_validated","katia_interventions_viewed","attempts_per_situation","misconceptions_detected","formalization_viewed","level_completed","time_on_node"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-katia-dialogo]","[componente-situacion-geometrica]","[componente-campo-numerico]","[componente-boton-validar]","[componente-retroalimentacion-modal]","[componente-formalizacion-expandible]","[componente-cierre-nivel]","[componente-nav-volver-ciudad]"],
    "design_tokens": ["[asset-mascota:Katia]","[color-acento-morado]","[color-acento-teal]","[color-raiz-no-exacta]"],
    "render_blocker": "Verificar render de: ⁿ√a, √16 = 4, ∛27 = 3, √9 = 3, √20 ≈ 4,4721, ⁿ√a = b ⇔ bⁿ = a, ⁿ√(a×b)=ⁿ√a×ⁿ√b, ⁿ√(aᵐ)=a^(m/n), a ≥ 0"
  },

  "i18n_prefix": "prealgebra.n2.e06"
}
```

---

## Notas finales
Verbatim del borrador: Texto 1 (completado), descripción, instrucciones, las 4 situaciones y **sus 4 intervenciones de Katia**, formalización con propiedades. **[NUEVO]:** retroalimentación por error, storyboard, diferenciación, notas, accesibilidad, citas, handoff, cierre de nivel, JSON.
**Correcciones aplicadas:** unidad S1 (4 cm → **4 m**); es-CO (√20 ≈ **4,4721**); Texto 1 completado. **Riesgo de render:** radicales (índice/radicando) — verificar especialmente.
