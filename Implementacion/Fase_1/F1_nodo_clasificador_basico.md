# Nodo: El Clasificador I — conjunto más específico
**ID:** PREALG-N1-B10-CLASIFICADOR-BASICO

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B10-CLASIFICADOR-BASICO |
| **Título visible** | El Clasificador I: conjunto más específico |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular principal de práctica formativa |
| **Ubicación en la ruta** | Tras B09 (Complejos) para Intermedio/Avanzado, o tras B08 (Reales) para Básico |
| **Función pedagógica** | Consolidar el recorrido mediante clasificación simple: ubicar cada número en su conjunto **más específico** |
| **Objetivo de aprendizaje** | El estudiante clasifica naturales, enteros, racionales, irracionales, imaginarios puros y complejos generales en su conjunto más específico |
| **Microhabilidades** | • Clasificar naturales (convención 0 ∈ ℕ)<br>• Clasificar enteros negativos<br>• Clasificar fracciones como racionales<br>• Clasificar decimales periódicos/exactos como racionales<br>• Clasificar √2 y π como irracionales<br>• Clasificar 2i como imaginario puro<br>• Clasificar 3 + 2i como complejo general<br>• Diferenciar conjunto más específico de pertenencia múltiple |
| **Misconception tags** | excluye_cero_de_naturales_pese_a_convencion<br>clasifica_entero_positivo_como_Z_en_vez_de_N<br>clasifica_fraccion_como_entero<br>clasifica_decimal_periodico_como_irracional<br>clasifica_irracional_como_racional<br>confunde_i_imaginaria_con_I_irracionales<br>clasifica_complejo_general_como_imaginario_puro<br>ubica_complejos_no_reales_en_recta_real<br>confunde_conjunto_minimo_con_pertenencia_multiple |
| **Referencias de refuerzo** | B04-NATURALES, B05-ENTEROS, B06-RACIONALES, B07-IRRACIONALES, B08-REALES, B09-COMPLEJOS, B11-CLASIFICADOR-RIGUROSO |

> **Nota de migración:** En el .docx original, las expresiones (½, √2, π, ℕ, ℤ, ℚ, 2i = 0 + 2i, a + bi) quedaron como corchetes/paréntesis vacíos por fallo de exportación KaTeX. Aquí se restauran a partir del contexto y el JSON técnico del original.

> **Nota de gating:** La tarjeta 2i y 3 + 2i, y sus zonas de imaginarios puros / complejos generales, **solo aparecen si el estudiante exploró la rama compleja** (`explored_complex_branch = true`). Para banda Básico sin esa rama, esas tarjetas y zonas se omiten, y la clasificación se limita a ℕ, ℤ, ℚ, irracionales.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
El Clasificador I: conjunto más específico
```

**Subtítulo:**
```
Primera fase: ubica cada número en el conjunto más pequeño o más preciso 
que lo describe.
```

---

#### 2.2 Diálogo inicial de Katia

**Contexto visual:** Katia aparece junto a una zona de clasificación con tarjetas de números.

**Diálogo de Katia:**
```
Ya recorrimos los conjuntos numéricos principales de este nivel.

Ahora vamos a practicar.

En esta primera fase no vamos a marcar todos los conjuntos posibles. Solo 
debes elegir el conjunto más específico para cada número.

Por ejemplo, 5 también es entero, racional, real y complejo, pero aquí lo 
clasificaremos como natural porque es el conjunto más pequeño dentro del 
recorrido.

Después haremos una segunda fase más rigurosa donde sí miraremos todas las 
pertenencias.
```

---

#### 2.3 Instrucción principal

**Título visible:**
```
Instrucción
```

**Texto visible:**
```
Arrastra cada número al conjunto más específico que le corresponde.
```

**Nota visible:**
```
Usa la convención del nivel:

ℕ = {0, 1, 2, 3, …}

Por tanto, 0 es natural.
```

---

#### 2.4 Zonas de clasificación

**Zonas visibles:**
- Naturales (ℕ)
- Enteros (ℤ)
- Racionales (ℚ)
- Irracionales (𝕀)
- Imaginarios puros *(solo con rama compleja)*
- Complejos con parte real e imaginaria *(solo con rama compleja)*

**Nota de diseño:**
```
La zona "Racionales" en esta fase debe entenderse como "racionales no enteros" 
para efectos de conjunto más específico. Es decir, fracciones o decimales 
racionales que no sean enteros.

La zona "Enteros" debe entenderse como "enteros que no son naturales", por 
ejemplo negativos.

La zona "Naturales" recibe 0 y enteros positivos.
```

---

#### 2.5 Tarjetas de números

**Tarjetas visibles:**
- −3
- 0
- 1/2
- √2
- π
- 5
- 2i *(solo con rama compleja)*
- 3 + 2i *(solo con rama compleja)*

---

#### 2.6 Clasificación esperada

| Número | Conjunto más específico |
|--------|------------------------|
| −3 | Enteros (ℤ) |
| 0 | Naturales (ℕ) |
| 1/2 | Racionales (ℚ) |
| √2 | Irracionales (𝕀) |
| π | Irracionales (𝕀) |
| 5 | Naturales (ℕ) |
| 2i | Imaginarios puros |
| 3 + 2i | Complejos con parte real e imaginaria |

---

#### 2.7 Retroalimentación general si todo está correcto

**Título del recuadro:**
```
✓ Clasificación correcta
```

**Retroalimentación de Katia:**
```
Bien. Clasificaste cada número en su conjunto más específico.

Recuerda que esta fue la clasificación básica. Algunos números también 
pertenecen a conjuntos más grandes.

Por ejemplo:

5 ∈ ℕ

pero también:

5 ∈ ℤ, ℚ, ℝ, ℂ

Eso lo trabajaremos en el siguiente clasificador.
```

---

#### 2.8 Retroalimentaciones específicas por error

##### Error: ubicar **0** fuera de naturales

**Título del recuadro:**
```
⚠ Atención a la convención
```

**Retroalimentación de Katia:**
```
En este nivel usamos:

ℕ = {0, 1, 2, 3, …}

Por eso, en esta actividad, el 0 se clasifica como natural.
```

**Misconception tag:** `excluye_cero_de_naturales_pese_a_convencion`

---

##### Error: ubicar **5** en enteros en lugar de naturales

**Título del recuadro:**
```
⚠ Busca el conjunto más específico
```

**Retroalimentación de Katia:**
```
5 sí es entero, pero también es natural.

Como esta fase pide el conjunto más específico, debemos ubicarlo en:

ℕ

En la siguiente fase veremos que también pertenece a otros conjuntos.
```

**Misconception tag:** `clasifica_entero_positivo_como_Z_en_vez_de_N`

---

##### Error: ubicar **−3** como natural

**Título del recuadro:**
```
⚠ Cuidado con los negativos
```

**Retroalimentación de Katia:**
```
−3 es un número entero, pero no es natural.

Los naturales de este nivel son:

0, 1, 2, 3, …

Los negativos pertenecen a los enteros.
```

---

##### Error: ubicar **1/2** como entero o natural

**Título del recuadro:**
```
⚠ Es una parte de la unidad
```

**Retroalimentación de Katia:**
```
1/2 no es entero ni natural porque representa una parte de la unidad.

Es racional porque puede escribirse como fracción de enteros:

1/2
```

**Misconception tag:** `clasifica_fraccion_como_entero`

---

##### Error: ubicar **1/2** como irracional

**Título del recuadro:**
```
⚠ Sí puede escribirse como fracción
```

**Retroalimentación de Katia:**
```
1/2 no es irracional.

Es racional porque ya está escrito como una fracción entre enteros, con 
denominador distinto de cero.
```

---

##### Error: ubicar **√2** como racional

**Título del recuadro:**
```
⚠ No puede escribirse como fracción de enteros
```

**Retroalimentación de Katia:**
```
√2 es irracional.

Su desarrollo decimal es infinito y no periódico. No puede escribirse como 
una fracción entre enteros.
```

**Misconception tag:** `clasifica_irracional_como_racional`

---

##### Error: ubicar **π** como racional

**Título del recuadro:**
```
⚠ π no es una fracción exacta
```

**Retroalimentación de Katia:**
```
π es irracional.

Podemos aproximarlo con números como 3.14, pero π exacto tiene infinitas 
cifras decimales no periódicas.
```

**Misconception tag:** `clasifica_irracional_como_racional`

---

##### Error: ubicar **2i** como irracional

**Título del recuadro:**
```
⚠ No confundas i con irracionales
```

**Retroalimentación de Katia:**
```
2i no es irracional.

La i minúscula representa la unidad imaginaria. Por eso 2i pertenece a los 
números complejos y, más específicamente, es un imaginario puro.
```

**Misconception tag:** `confunde_i_imaginaria_con_I_irracionales`

---

##### Error: ubicar **2i** como complejo con parte real e imaginaria

**Título del recuadro:**
```
⚠ Es imaginario puro
```

**Retroalimentación de Katia:**
```
2i sí es complejo, pero en esta fase buscamos el conjunto más específico.

Como no tiene parte real visible, podemos escribirlo así:

2i = 0 + 2i

Por eso se clasifica como imaginario puro.
```

---

##### Error: ubicar **3 + 2i** como imaginario puro

**Título del recuadro:**
```
⚠ Tiene parte real
```

**Retroalimentación de Katia:**
```
3 + 2i no es imaginario puro porque tiene parte real 3.

En la forma:

a + bi

tenemos:

a = 3, b = 2

Por eso se clasifica como complejo con parte real e imaginaria.
```

**Misconception tag:** `clasifica_complejo_general_como_imaginario_puro`

---

##### Error: ubicar **3 + 2i** como real

**Título del recuadro:**
```
⚠ Sale de la recta real
```

**Retroalimentación de Katia:**
```
3 + 2i no pertenece a la recta real.

Tiene parte real 3 y parte imaginaria 2. Por eso se representa en el plano 
complejo, no solo en la recta real.
```

**Misconception tag:** `ubica_complejos_no_reales_en_recta_real`

---

#### 2.9 Ayuda opcional

**Botón visible:**
```
Necesito una pista
```

**Contenido de la pista:**
```
Recuerda esta ruta:

ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ

Pero en esta fase buscamos el conjunto más específico.

Ejemplos:
- 5 va en naturales.
- −3 va en enteros.
- 1/2 va en racionales.
- √2 va en irracionales.
- 2i va en imaginarios puros.
- 3 + 2i va en complejos con parte real e imaginaria.
```

---

#### 2.10 Intentos permitidos

**Texto visible sugerido:**
```
Puedes corregir tu clasificación después de leer la retroalimentación.
```

**Regla pedagógica:**
```
Permitir al menos dos intentos antes de marcar el nodo como completado. El 
primer error debe producir retroalimentación específica. El segundo intento 
permite verificar si el estudiante corrigió la misconception.
```

---

#### 2.11 Mensaje de cierre

**Texto visible:**
```
Primera fase completada.
```

**Diálogo de Katia:**
```
Acabas de clasificar cada número en su conjunto más específico.

Ahora haremos una segunda fase: veremos todos los conjuntos a los que puede 
pertenecer un mismo número.
```

**Botón principal:**
```
Ir al clasificador riguroso
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B10-CLASIFICADOR-BASICO.
- El nodo aparece en estado `actual` tras completar B09 (Complejos) o B08 (Reales) según banda.
- Un hexágono de transición aparece **antes** del nodo:
  ```
  De aprender conjuntos a clasificarlos
  ```

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. Aparece el título "El Clasificador I: conjunto más específico".
2. Katia explica que esta es la primera fase de clasificación.
3. Se muestran las zonas de clasificación.
4. Se muestran las tarjetas de números.
5. Se muestra la nota sobre la convención 0 ∈ ℕ.
6. Se activa la interacción de arrastrar y soltar.

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante realiza esto:

1. **Lee la instrucción** (clasificar por conjunto más específico).
2. **Arrastra cada número** a una zona de clasificación.
   - Cada tarjeta tiene estado visual: sin ubicar, ubicada, pendiente.
3. **Presiona "Verificar"** la clasificación.
4. **Lee retroalimentación** general (si todo correcto) o específica (por error).
5. **Corrige** las tarjetas incorrectas si es necesario.
6. **Vuelve a verificar.**
7. **Completa la clasificación.**
8. **Lee el mensaje de cierre.**
9. **Presiona "Ir al clasificador riguroso"** y el nodo se marca como completado.

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Presentación** | Instrucciones, zonas, tarjetas, nota convención | Lectura | Prepara la actividad |
| **2 — Clasificación activa** | Tablero drag-drop con tarjetas y zonas | Arrastrar tarjetas | El estudiante clasifica |
| **3 — Verificación** | Resultado por tarjeta + retroalimentación | Botón "Verificar" | Sistema evalúa |
| **4 — Corrección** | Tarjetas incorrectas resaltadas | Mover + re-verificar | El estudiante corrige |
| **5 — Finalización** | Mensaje de cierre + Katia | Botón "Continuar" | Nodo completado |
| **6 — Transición** | Hexágono + botón "Ir al clasificador riguroso" | Botón navegable | Prepara B11 |

**Estados visuales por tarjeta:**
- Sin ubicar
- Ubicada
- Pendiente de verificación
- Correcta (✓ verde)
- Requiere revisión (⚠ ámbar)

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono de transición.
- **Katia aparece:** Slide-in lateral.
- **Tarjetas aparecen:** Fade-in con stagger.
- **Zonas se iluminan al hover:** La zona destino se resalta cuando se arrastra una tarjeta sobre ella.
- **Arrastre:** Animación suave de la tarjeta siguiendo el cursor/dedo.
- **Soltado:** La tarjeta se ancla a la zona con un "snap".
- **Verificación:** Cada tarjeta correcta brilla verde; las incorrectas vibran sutilmente (ámbar).
- **Corrección:** La tarjeta vuelve a la bandeja o cambia de zona con animación.
- **Finalización:** Todas las tarjetas correctas brillan; el peldaño se marca completado.

---

#### 3.6 Relación con el mapa visual

**Nodo circular:** Representa la pantalla principal del clasificador básico.

**Punticos internos (eventos registrados):**
- Visualizó instrucción
- Abrió pista
- Arrastró una tarjeta
- Verificó clasificación
- Recibió retroalimentación
- Corrigió clasificación
- Completó actividad
- Completó nodo

**Hexágono de transición (posterior):**
- Texto: "De conjunto específico a pertenencia múltiple"
- Conecta hacia: PREALG-N1-B11-CLASIFICADOR-RIGUROSO
- Se ilumina al completar B10.

---

### A4. Diferenciación por nivel (Básico / Intermedio / Avanzado)

| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| **Tarjetas presentadas** | Sin 2i, 3 + 2i (sin rama compleja) | Con tarjetas complejas | Con tarjetas complejas |
| **Zonas presentadas** | ℕ, ℤ, ℚ, irracionales | + imaginarios puros, complejos | + imaginarios puros, complejos |
| **Pista disponible** | Siempre visible/accesible | Disponible bajo botón | Disponible bajo botón |
| **Retroalimentación** | Muy explícita por tarjeta | Por grupo de error | Resumida |
| **Intentos** | Ilimitados con guía | 2+ con guía | 2+ sin guía adicional |
| **Tarjetas adicionales (opcional)** | — | — | Variante: 0.333…, −7, 4/4 (que = 1) |

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Conjunto más específico reduce carga cognitiva]**
La decisión de clasificar por "conjunto más específico" (no pertenencia múltiple) reduce deliberadamente la carga cognitiva de esta primera actividad integradora. El estudiante no debe marcar todas las pertenencias simultáneamente, sino elegir una sola zona. Esto consolida las diferencias básicas antes de la complejidad de la pertenencia múltiple (B11).

**[NOTA PEDAGÓGICA — Anticipar la confusión con B11]**
El guión aclara explícitamente desde el inicio que 5 se clasifica como natural **aunque también** sea entero, racional, real y complejo. Esta aclaración previa previene la misconception `confunde_conjunto_minimo_con_pertenencia_multiple` y prepara conceptualmente el contraste con el clasificador riguroso.

**[NOTA PEDAGÓGICA — Errores frecuentes documentados]**
Los errores cubiertos (omitir 0, clasificar 5 como entero, tratar decimales periódicos como irracionales, confundir 2i con irracional) son misconceptions documentadas. Cada una tiene retroalimentación específica que reconecta con el nodo de origen.

---

### A6. Accesibilidad

- **Drag-and-drop:** Debe tener alternativa accesible por teclado (seleccionar tarjeta + seleccionar zona).
- **Colores:** Estados de tarjeta no dependen solo de color; usar íconos ✓ y ⚠.
- **Matemática:** Todas las expresiones (1/2, √2, π, ℕ, ℤ, ℚ, 2i, 3 + 2i, a + bi) con KaTeX y ARIA.
- **Zonas:** Cada zona con etiqueta ARIA clara (ej. "Zona de naturales").
- **Contraste:** Relación mínima 4.5:1.
- **Feedback:** Anunciado por lector de pantalla al verificar.

---

### A7. Notas de citas pedagógicas

- **Reducción de carga cognitiva en tareas integradoras:** Sweller (1988) — secuenciar de simple (conjunto único) a complejo (pertenencia múltiple).
- **Clasificación como consolidación:** Bruner (1960) — categorizar consolida estructuras conceptuales.
- **Retroalimentación específica por error:** Hattie & Timperley (2007) — el feedback efectivo identifica el error y la corrección.
- **Práctica con reintento sin penalización:** Kapur (2008), error productivo — los errores en zona segura promueven aprendizaje.

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo]
- [componente-instruccion-clasificador] — Tarjeta con instrucción y nota de convención
- [componente-tablero-drag-drop] — Tablero de clasificación
- [componente-zona-clasificacion] — Zona destino (drop zone) por conjunto
- [componente-tarjeta-numero] — Tarjeta arrastrable con expresión KaTeX
- [componente-pista] — Tarjeta de ayuda opcional
- [componente-retroalimentacion-modal] — Feedback por tarjeta/grupo
- [componente-resumen-clasificacion] — Resumen final
- [componente-transicion-hexagono]

**Gating:**
- [flag-explored_complex_branch] — Controla aparición de tarjetas/zonas complejas

**Render bloqueante:**
- Verificar render de: −3, 0, 1/2, √2, π, 5, 2i, 3 + 2i, ℕ, ℤ, ℚ, 𝕀, a + bi, 0 + 2i, ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ.
- **Crítico:** Drag-and-drop accesible y responsivo en móvil.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B10-CLASIFICADOR-BASICO",
  "node_type": "formative_practice_classification_single",
  "name": "El Clasificador I: conjunto más específico",
  "position_in_route": "ruta_nucleo_practica_clasificacion_1",
  "unlock_rule": "completed_node:PREALG-N1-B09-COMPLEJOS-PLANO OR (completed_node:PREALG-N1-B08-REALES-RECTA AND NOT flag:explored_complex_branch)",
  "previous_node_id": "PREALG-N1-B09-COMPLEJOS-PLANO",
  "next_node_id": "PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
  "order": 10,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "affects_elo": false,
  "safe_zone": true,
  "min_attempts_before_completion": 2,

  "classification_task": {
    "task_type": "drag_drop_single_classification",
    "instruction": "Arrastra cada número al conjunto más específico que le corresponde.",
    "convention_note": "ℕ = {0, 1, 2, 3, …}; por tanto, 0 es natural",
    "zones": [
      {"id": "naturals", "label": "Naturales (ℕ)", "meaning": "0 y enteros positivos"},
      {"id": "integers", "label": "Enteros (ℤ)", "meaning": "enteros que no son naturales (negativos)"},
      {"id": "rationals", "label": "Racionales (ℚ)", "meaning": "racionales no enteros (fracciones/decimales)"},
      {"id": "irrationals", "label": "Irracionales (𝕀)", "meaning": "no expresables como fracción de enteros"},
      {"id": "pure_imaginary", "label": "Imaginarios puros", "meaning": "parte real cero", "requires_flag": "explored_complex_branch"},
      {"id": "complex_general", "label": "Complejos con parte real e imaginaria", "requires_flag": "explored_complex_branch"}
    ],
    "cards": [
      {"value": "-3", "label": "-3", "expected_zone": "integers"},
      {"value": "0", "label": "0", "expected_zone": "naturals"},
      {"value": "1/2", "label": "\\frac{1}{2}", "expected_zone": "rationals"},
      {"value": "sqrt2", "label": "\\sqrt{2}", "expected_zone": "irrationals"},
      {"value": "pi", "label": "\\pi", "expected_zone": "irrationals"},
      {"value": "5", "label": "5", "expected_zone": "naturals"},
      {"value": "2i", "label": "2i", "expected_zone": "pure_imaginary", "requires_flag": "explored_complex_branch"},
      {"value": "3+2i", "label": "3 + 2i", "expected_zone": "complex_general", "requires_flag": "explored_complex_branch"}
    ]
  },

  "feedback": {
    "all_correct": {
      "title": "✓ Clasificación correcta",
      "body": "Bien. Clasificaste cada número en su conjunto más específico.\nRecuerda que esta fue la clasificación básica. Algunos números también pertenecen a conjuntos más grandes.\nPor ejemplo: 5 ∈ ℕ, pero también 5 ∈ ℤ, ℚ, ℝ, ℂ\nEso lo trabajaremos en el siguiente clasificador."
    },
    "errors": [
      {
        "error_id": "zero_not_natural",
        "trigger": "0 placed outside naturals",
        "title": "⚠ Atención a la convención",
        "body": "En este nivel usamos: ℕ = {0, 1, 2, 3, …}\nPor eso, en esta actividad, el 0 se clasifica como natural.",
        "misconception_tag": "excluye_cero_de_naturales_pese_a_convencion"
      },
      {
        "error_id": "five_as_integer",
        "trigger": "5 placed in integers instead of naturals",
        "title": "⚠ Busca el conjunto más específico",
        "body": "5 sí es entero, pero también es natural.\nComo esta fase pide el conjunto más específico, debemos ubicarlo en: ℕ\nEn la siguiente fase veremos que también pertenece a otros conjuntos.",
        "misconception_tag": "clasifica_entero_positivo_como_Z_en_vez_de_N"
      },
      {
        "error_id": "minus_three_as_natural",
        "trigger": "-3 placed as natural",
        "title": "⚠ Cuidado con los negativos",
        "body": "−3 es un número entero, pero no es natural.\nLos naturales de este nivel son: 0, 1, 2, 3, …\nLos negativos pertenecen a los enteros.",
        "misconception_tag": null
      },
      {
        "error_id": "fraction_as_integer",
        "trigger": "1/2 placed as integer or natural",
        "title": "⚠ Es una parte de la unidad",
        "body": "1/2 no es entero ni natural porque representa una parte de la unidad.\nEs racional porque puede escribirse como fracción de enteros: 1/2",
        "misconception_tag": "clasifica_fraccion_como_entero"
      },
      {
        "error_id": "fraction_as_irrational",
        "trigger": "1/2 placed as irrational",
        "title": "⚠ Sí puede escribirse como fracción",
        "body": "1/2 no es irracional.\nEs racional porque ya está escrito como una fracción entre enteros, con denominador distinto de cero.",
        "misconception_tag": null
      },
      {
        "error_id": "sqrt2_as_rational",
        "trigger": "√2 placed as rational",
        "title": "⚠ No puede escribirse como fracción de enteros",
        "body": "√2 es irracional.\nSu desarrollo decimal es infinito y no periódico. No puede escribirse como una fracción entre enteros.",
        "misconception_tag": "clasifica_irracional_como_racional"
      },
      {
        "error_id": "pi_as_rational",
        "trigger": "π placed as rational",
        "title": "⚠ π no es una fracción exacta",
        "body": "π es irracional.\nPodemos aproximarlo con números como 3.14, pero π exacto tiene infinitas cifras decimales no periódicas.",
        "misconception_tag": "clasifica_irracional_como_racional"
      },
      {
        "error_id": "2i_as_irrational",
        "trigger": "2i placed as irrational",
        "title": "⚠ No confundas i con irracionales",
        "body": "2i no es irracional.\nLa i minúscula representa la unidad imaginaria. Por eso 2i pertenece a los números complejos y, más específicamente, es un imaginario puro.",
        "misconception_tag": "confunde_i_imaginaria_con_I_irracionales"
      },
      {
        "error_id": "2i_as_complex_general",
        "trigger": "2i placed as complex with real and imaginary part",
        "title": "⚠ Es imaginario puro",
        "body": "2i sí es complejo, pero en esta fase buscamos el conjunto más específico.\nComo no tiene parte real visible, podemos escribirlo así: 2i = 0 + 2i\nPor eso se clasifica como imaginario puro.",
        "misconception_tag": null
      },
      {
        "error_id": "3plus2i_as_pure",
        "trigger": "3+2i placed as pure imaginary",
        "title": "⚠ Tiene parte real",
        "body": "3 + 2i no es imaginario puro porque tiene parte real 3.\nEn la forma a + bi tenemos: a = 3, b = 2\nPor eso se clasifica como complejo con parte real e imaginaria.",
        "misconception_tag": "clasifica_complejo_general_como_imaginario_puro"
      },
      {
        "error_id": "3plus2i_as_real",
        "trigger": "3+2i placed as real",
        "title": "⚠ Sale de la recta real",
        "body": "3 + 2i no pertenece a la recta real.\nTiene parte real 3 y parte imaginaria 2. Por eso se representa en el plano complejo, no solo en la recta real.",
        "misconception_tag": "ubica_complejos_no_reales_en_recta_real"
      }
    ]
  },

  "hint": {
    "button_label": "Necesito una pista",
    "body": "Recuerda esta ruta: ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ\nPero en esta fase buscamos el conjunto más específico.\nEjemplos: 5 → naturales; −3 → enteros; 1/2 → racionales; √2 → irracionales; 2i → imaginarios puros; 3 + 2i → complejos con parte real e imaginaria."
  },

  "events_to_register": [
    "node_viewed",
    "activity_started",
    "instruction_viewed",
    "hint_opened",
    "card_dragged",
    "classification_verified",
    "feedback_viewed",
    "misconception_detected",
    "classification_corrected",
    "activity_completed",
    "node_completed",
    "transition_initiated"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_FEW_ERRORS_CORRECTED",
      "level": "observation",
      "trigger": "Student makes 1-2 classification errors but corrects after feedback",
      "message_educator": "El estudiante cometió errores iniciales en clasificación por conjunto específico, pero corrigió después de la retroalimentación. Se recomienda observar su desempeño en la fase rigurosa."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_MANY_ERRORS",
      "level": "reinforcement_suggested",
      "trigger": "Student makes 3+ errors on first classification or needs more than 2 attempts",
      "message_educator": "El estudiante presenta dificultad para clasificar números según su conjunto más específico. Se recomienda revisar las pantallas asociadas a los errores detectados antes de la clasificación rigurosa."
    },
    {
      "condition_id": "ALERT_INTERVENTION_PERSISTENT_BROAD",
      "level": "teacher_intervention",
      "trigger": "Student maintains errors after feedback in 3+ different categories (mixing rationals, irrationals, complexes)",
      "message_educator": "El estudiante mantiene dificultades amplias de clasificación entre conjuntos numéricos. Se recomienda intervención directa con ejemplos y no ejemplos de cada conjunto."
    },
    {
      "condition_id": "ALERT_GROUP_ZERO_OR_FIVE",
      "level": "observation_group",
      "trigger": "More than 40% of group omits 0 as natural or classifies 5 as integer instead of natural",
      "message_educator": "Una proporción importante del grupo está teniendo dificultades con la convención 0 ∈ ℕ o con la idea de conjunto más específico. Puede ser útil reforzar la diferencia entre clasificación básica y pertenencia múltiple."
    },
    {
      "condition_id": "ALERT_GROUP_ADVANCED_NUMBERS",
      "level": "reinforcement_suggested_group",
      "trigger": "More than 40% of group misclassifies 0.333…, √2, π, 2i, or 3+2i",
      "message_educator": "El grupo presenta dificultades relevantes en la clasificación de racionales, irracionales o complejos. Se recomienda revisar los bloques correspondientes antes de avanzar."
    }
  ],

  "level_presentation": {
    "basico": {
      "show_complex_cards_and_zones": false,
      "hint_always_visible": true,
      "feedback_detail": "per_card_explicit"
    },
    "intermedio": {
      "show_complex_cards_and_zones": true,
      "hint_always_visible": false,
      "feedback_detail": "per_error_group"
    },
    "avanzado": {
      "show_complex_cards_and_zones": true,
      "hint_always_visible": false,
      "feedback_detail": "summarized",
      "additional_cards": ["0.333...", "-7", "4/4"]
    }
  },

  "design_handoff": {
    "node_state": "bloqueado|actual|completado",
    "path_position": "ruta_nucleo_practica_clasificacion_1",
    "gating_flag": "explored_complex_branch",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-instruccion-clasificador]",
      "[componente-tablero-drag-drop]",
      "[componente-zona-clasificacion]",
      "[componente-tarjeta-numero]",
      "[componente-pista]",
      "[componente-retroalimentacion-modal]",
      "[componente-resumen-clasificacion]",
      "[componente-transicion-hexagono]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[color-tarjeta-correcta]",
      "[color-tarjeta-revision]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: −3, 0, 1/2, √2, π, 5, 2i, 3 + 2i, ℕ, ℤ, ℚ, 𝕀, a + bi, 0 + 2i, ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ; drag-and-drop accesible y responsivo en móvil"
  }
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** de B10 (Clasificador Básico):
- ✅ Texto completo de Katia
- ✅ Instrucción y zonas de clasificación
- ✅ 8 tarjetas con clasificación esperada
- ✅ 11 retroalimentaciones específicas por error
- ✅ Pista opcional
- ✅ Regla de intentos
- ✅ Storyboard detallado con estados de tarjeta
- ✅ **Gating de tarjetas/zonas complejas** por `explored_complex_branch`
- ✅ JSON técnico limpio

**Corrección de migración:** Se restauraron todas las expresiones (1/2, √2, π, ℕ, ℤ, ℚ, 2i = 0 + 2i, a + bi, cadena de inclusión) que en el .docx original quedaron como corchetes vacíos.
