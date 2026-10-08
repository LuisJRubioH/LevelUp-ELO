# Nodo: El Clasificador II — pertenencia múltiple
**ID:** PREALG-N1-B11-CLASIFICADOR-RIGUROSO

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B11-CLASIFICADOR-RIGUROSO |
| **Título visible** | El Clasificador II: pertenencia múltiple |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular principal de práctica formativa avanzada |
| **Ubicación en la ruta** | Tras B10 (Clasificador Básico) |
| **Función pedagógica** | Consolidar la relación de inclusión: identificar **todos** los conjuntos a los que pertenece cada número, no solo el más específico |
| **Objetivo de aprendizaje** | El estudiante reconoce que un mismo número puede pertenecer a varios conjuntos simultáneamente, según las relaciones de inclusión ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ |
| **Microhabilidades** | • Reconocer pertenencia múltiple<br>• Aplicar cadena de inclusión<br>• Reconocer ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ<br>• Reconocer irracionales como reales y complejos<br>• Reconocer complejos no reales en ℂ pero no en ℝ<br>• Diferenciar conjunto formal de descriptor ("imaginario puro") |
| **Misconception tags** | marca_solo_conjunto_mas_especifico<br>no_reconoce_pertenencia_multiple<br>no_reconoce_N_dentro_de_Z_Q_R_C<br>no_reconoce_Z_dentro_de_Q_R_C<br>no_reconoce_Q_dentro_de_R_C<br>no_reconoce_irracionales_como_reales<br>no_reconoce_reales_como_complejos<br>ubica_complejos_no_reales_en_recta_real<br>confunde_imaginario_puro_con_irracional<br>confunde_conjunto_formal_con_descriptor |
| **Referencias de refuerzo** | B03-ESCALERA, B08-REALES, B09-COMPLEJOS, B10-CLASIFICADOR-BASICO, B12-DETECTIVE-FALSEDADES |

> **Nota de migración:** En el .docx original, la cadena de inclusión, las fracciones (5/1, −3/1), las expresiones (a + 0i, 2i = 0 + 2i) y los símbolos de conjuntos quedaron como corchetes vacíos. Aquí se restauran a partir de la matriz de pertenencia y el contexto.

> **Nota de gating:** Las filas de 2i y 3 + 2i, y la columna ℂ con descriptor "imaginario puro / complejo no real", **solo aparecen si `explored_complex_branch = true`**. Para banda Básico sin rama compleja, la matriz se limita a ℕ, ℤ, ℚ, Irracional, ℝ (sin columna ℂ ni filas complejas).

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
El Clasificador II: pertenencia múltiple
```

**Subtítulo:**
```
Segunda fase: marca todos los conjuntos a los que pertenece cada número.
```

---

#### 2.2 Diálogo inicial de Katia

**Contexto visual:** Katia aparece junto al diagrama de inclusión.

**Diálogo de Katia:**
```
En el clasificador anterior buscamos el conjunto más específico de cada número.

Ahora haremos algo más riguroso.

Un número puede pertenecer a varios conjuntos al mismo tiempo.

Por ejemplo, 5 es natural, pero también es entero, racional, real y complejo.
```

---

#### 2.3 Recordatorio visual

**Título visible:**
```
Recuerda la cadena de inclusión
```

**Texto visible:**
```
Los conjuntos que hemos estudiado se relacionan así:

ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ

Además:

𝕀 ⊂ ℝ  (los irracionales están dentro de los reales)

Esto significa que los irracionales están dentro de los reales, pero no dentro 
de los racionales.
```

**Nota visible:**
```
En este bloque, "imaginario puro" se usará como una descripción especial 
dentro de los complejos, no como un conjunto formal al mismo nivel que 
ℕ, ℤ, ℚ, ℝ y ℂ.
```

---

#### 2.4 Instrucción principal

**Título visible:**
```
Instrucción
```

**Texto visible:**
```
Para cada número, marca todos los conjuntos a los que pertenece.
```

**Conjuntos disponibles (columnas):**
- Naturales (ℕ)
- Enteros (ℤ)
- Racionales (ℚ)
- Irracionales (𝕀)
- Reales (ℝ)
- Complejos (ℂ)

**Descriptor adicional cuando aplique:**
- Imaginario puro

---

#### 2.5 Números de la actividad

**Tarjetas/filas visibles:**
- −3
- 0
- 1/2
- √2
- π
- 5
- 2i *(solo con rama compleja)*
- 3 + 2i *(solo con rama compleja)*

---

#### 2.6 Matriz de pertenencia esperada

| Número | ℕ | ℤ | ℚ | Irracional | ℝ | ℂ | Descriptor |
|--------|---|---|---|-----------|---|---|-----------|
| −3 | No | Sí | Sí | No | Sí | Sí | — |
| 0 | Sí | Sí | Sí | No | Sí | Sí | — |
| 1/2 | No | No | Sí | No | Sí | Sí | — |
| √2 | No | No | No | Sí | Sí | Sí | — |
| π | No | No | No | Sí | Sí | Sí | — |
| 5 | Sí | Sí | Sí | No | Sí | Sí | — |
| 2i | No | No | No | No | No | Sí | Imaginario puro |
| 3 + 2i | No | No | No | No | No | Sí | Complejo no real |

---

#### 2.7 Ejemplo guiado antes de la actividad

**Título visible:**
```
Ejemplo guiado: el número 5
```

**Texto visible:**
```
El número 5 pertenece a:

ℕ

porque es natural.

También pertenece a:

ℤ

porque todo natural es entero.

También pertenece a:

ℚ

porque puede escribirse como:

5 = 5/1

También pertenece a:

ℝ

porque se ubica en la recta numérica.

Y también pertenece a:

ℂ

porque puede escribirse como:

5 = 5 + 0i
```

**Cierre del ejemplo:**
```
Entonces:

5 ∈ ℕ, ℤ, ℚ, ℝ, ℂ
```

---

#### 2.8 Interacción principal

**Tipo de interacción:** Matriz de selección (cada fila = un número, cada columna = un conjunto; se pueden marcar varias casillas por fila).

**Texto visible:**
```
Marca todos los conjuntos que correspondan a cada número.
```

**Regla visual:**
```
Cada fila corresponde a un número.
Cada columna corresponde a un conjunto.
El estudiante puede marcar varias casillas por fila.
```

---

#### 2.9 Retroalimentación general si todo está correcto

**Título del recuadro:**
```
✓ Clasificación rigurosa correcta
```

**Retroalimentación de Katia:**
```
Bien. Ahora reconoces que un número puede pertenecer a varios conjuntos.

La clave está en la inclusión:

ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ

Por eso, si un número es natural, también es entero, racional, real y complejo.
```

---

#### 2.10 Retroalimentaciones específicas por error

##### Error: marcar solo el conjunto más específico

**Título del recuadro:**
```
⚠ Ahora buscamos todas las pertenencias
```

**Retroalimentación de Katia:**
```
En el clasificador anterior bastaba con marcar el conjunto más específico.

Pero en esta fase debes marcar todos los conjuntos a los que pertenece el número.

Por ejemplo:

5 ∈ ℕ

pero también:

5 ∈ ℤ, ℚ, ℝ, ℂ
```

**Misconception tag:** `marca_solo_conjunto_mas_especifico`

---

##### Error: no marcar **0** como natural

**Título del recuadro:**
```
⚠ Recuerda la convención
```

**Retroalimentación de Katia:**
```
En este nivel usamos:

ℕ = {0, 1, 2, 3, …}

Por eso:

0 ∈ ℕ

Y además:

0 ∈ ℤ, ℚ, ℝ, ℂ
```

---

##### Error: no marcar un entero como racional

**Título del recuadro:**
```
⚠ Todo entero es racional
```

**Retroalimentación de Katia:**
```
Todo número entero puede escribirse con denominador 1.

Por ejemplo:

−3 = −3/1

Por eso:

−3 ∈ ℤ, ℚ, ℝ, ℂ
```

**Misconception tag:** `no_reconoce_Z_dentro_de_Q_R_C`

---

##### Error: no marcar racional como real

**Título del recuadro:**
```
⚠ Los racionales están en la recta
```

**Retroalimentación de Katia:**
```
Todo racional es real porque puede ubicarse en la recta numérica.

Por ejemplo:

1/2 ∈ ℚ

y también:

1/2 ∈ ℝ
```

**Misconception tag:** `no_reconoce_Q_dentro_de_R_C`

---

##### Error: no marcar racional como complejo

**Título del recuadro:**
```
⚠ Los reales también son complejos
```

**Retroalimentación de Katia:**
```
Todo número real puede escribirse como complejo con parte imaginaria cero.

Por ejemplo:

1/2 = 1/2 + 0i

Por eso:

1/2 ∈ ℂ
```

**Misconception tag:** `no_reconoce_reales_como_complejos`

---

##### Error: marcar **√2** o **π** como racional

**Título del recuadro:**
```
⚠ Son reales, pero no racionales
```

**Retroalimentación de Katia:**
```
√2 y π son irracionales.

Eso significa que pertenecen a:

𝕀 (irracionales)

También son reales y complejos, pero no racionales.
```

**Misconception tag:** `clasifica_irracional_como_racional`

---

##### Error: no marcar **√2** o **π** como reales

**Título del recuadro:**
```
⚠ Los irracionales también son reales
```

**Retroalimentación de Katia:**
```
Los irracionales sí pertenecen a los reales.

𝕀 ⊂ ℝ

Eso significa que están dentro de ℝ, pero fuera de ℚ.
```

**Misconception tag:** `no_reconoce_irracionales_como_reales`

---

##### Error: no marcar **√2** o **π** como complejos

**Título del recuadro:**
```
⚠ Todo real también es complejo
```

**Retroalimentación de Katia:**
```
√2 y π son reales.

Todo real puede escribirse como complejo con parte imaginaria cero:

√2 = √2 + 0i

π = π + 0i

Por eso también pertenecen a ℂ.
```

**Misconception tag:** `no_reconoce_reales_como_complejos`

---

##### Error: marcar **2i** como real

**Título del recuadro:**
```
⚠ 2i no está en la recta real
```

**Retroalimentación de Katia:**
```
2i es un complejo no real.

Se puede escribir como:

2i = 0 + 2i

Pertenece a ℂ, pero no a ℝ.

También es un imaginario puro.
```

**Misconception tag:** `ubica_complejos_no_reales_en_recta_real`

---

##### Error: marcar **2i** como irracional

**Título del recuadro:**
```
⚠ Irracional no es lo mismo que imaginario
```

**Retroalimentación de Katia:**
```
Los irracionales son números reales que no son racionales.

Pero 2i no es real. Pertenece a los complejos y es un imaginario puro.

Por eso no se clasifica como irracional.
```

**Misconception tag:** `confunde_imaginario_puro_con_irracional`

---

##### Error: marcar **3 + 2i** como real

**Título del recuadro:**
```
⚠ Tiene parte imaginaria distinta de cero
```

**Retroalimentación de Katia:**
```
3 + 2i tiene parte real 3 y parte imaginaria 2.

Como su parte imaginaria no es cero, no pertenece a la recta real.

Pertenece a ℂ, pero no a ℝ.
```

**Misconception tag:** `ubica_complejos_no_reales_en_recta_real`

---

##### Error: marcar **3 + 2i** como imaginario puro

**Título del recuadro:**
```
⚠ No es imaginario puro
```

**Retroalimentación de Katia:**
```
Un imaginario puro tiene parte real cero.

Por ejemplo:

2i = 0 + 2i

Pero:

3 + 2i

tiene parte real 3. Por eso no es imaginario puro.
```

**Misconception tag:** `confunde_conjunto_formal_con_descriptor`

---

#### 2.11 Ayuda opcional

**Botón visible:**
```
Necesito una pista
```

**Contenido de la pista:**
```
Usa estas reglas:

- Si un número es natural, también es entero, racional, real y complejo.
- Si un número es entero, también es racional, real y complejo.
- Si un número es racional, también es real y complejo.
- Si un número es irracional, también es real y complejo.
- Si un número tiene i y su parte imaginaria no es cero, es complejo.
- Si un complejo tiene parte imaginaria distinta de cero, no está en la recta real.
- Si un complejo tiene parte imaginaria cero, es real.
```

---

#### 2.12 Intentos permitidos

**Texto visible sugerido:**
```
Puedes revisar tus respuestas después de leer la retroalimentación.
```

**Regla pedagógica:**
```
Permitir al menos dos intentos.
Registrar el primer intento como diagnóstico.
Registrar el segundo intento como evidencia de corrección o persistencia del error.
```

---

#### 2.13 Mensaje de cierre

**Texto visible:**
```
Clasificación rigurosa completada.
```

**Diálogo de Katia:**
```
Ahora ya puedes distinguir dos ideas:

Una cosa es el conjunto más específico de un número.

Otra cosa es la lista completa de conjuntos a los que pertenece.

Con eso listo, pasaremos al Detective de Falsedades.
```

**Botón principal:**
```
Ir al detective
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B11-CLASIFICADOR-RIGUROSO.
- El nodo aparece en estado `actual` tras completar B10.
- Un hexágono de transición aparece **antes** del nodo:
  ```
  De conjunto específico a pertenencia múltiple
  ```

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. Aparece el título "El Clasificador II: pertenencia múltiple".
2. Katia explica que esta fase es más rigurosa.
3. Se muestra el recordatorio de la cadena de inclusión (ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ).
4. Se muestra la nota sobre "imaginario puro" como descriptor.
5. Se presenta el ejemplo guiado del número 5.
6. Se muestra la matriz de selección.
7. Se activa la interacción.

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante realiza esto:

1. **Lee la cadena de inclusión** y la nota sobre descriptores.
2. **Estudia el ejemplo guiado** (5 pertenece a ℕ, ℤ, ℚ, ℝ, ℂ).
3. **Marca, para cada número, todos los conjuntos** a los que pertenece (matriz de checkboxes).
4. **Presiona "Verificar".**
5. **Lee retroalimentación** general o específica por error.
6. **Corrige** las marcas incorrectas si es necesario.
7. **Vuelve a verificar.**
8. **Completa la matriz.**
9. **Lee el mensaje de cierre.**
10. **Presiona "Ir al detective"** y el nodo se marca como completado.

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Presentación** | Cadena de inclusión, nota descriptor | Lectura | Prepara el marco |
| **2 — Ejemplo guiado** | Desarrollo de 5 ∈ ℕ, ℤ, ℚ, ℝ, ℂ | Lectura | Modela la tarea |
| **3 — Matriz activa** | Matriz números × conjuntos con checkboxes | Marcar casillas | El estudiante clasifica |
| **4 — Verificación** | Resultado por celda/fila + retroalimentación | Botón "Verificar" | Sistema evalúa |
| **5 — Corrección** | Celdas incorrectas resaltadas | Re-marcar + re-verificar | El estudiante corrige |
| **6 — Finalización** | Mensaje de cierre + Katia | Botón "Continuar" | Nodo completado |
| **7 — Transición** | Hexágono + botón "Ir al detective" | Botón navegable | Prepara B12 |

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono.
- **Cadena de inclusión:** Animación que muestra los conjuntos anidándose (ℕ dentro de ℤ dentro de ℚ...).
- **Ejemplo guiado:** Aparición progresiva de cada pertenencia de 5.
- **Matriz aparece:** Fade-in con filas en stagger.
- **Marcar casilla:** Checkbox con animación de "check".
- **Verificación:** Celdas correctas brillan verde; incorrectas vibran ámbar.
- **Corrección:** Celdas se actualizan con animación.
- **Finalización:** Toda la matriz correcta brilla; el peldaño se marca completado.

---

#### 3.6 Relación con el mapa visual

**Nodo circular:** Representa la pantalla principal del clasificador riguroso.

**Punticos internos (eventos registrados):**
- Visualizó cadena de inclusión
- Visualizó ejemplo guiado
- Abrió pista
- Marcó casillas
- Verificó matriz
- Recibió retroalimentación
- Corrigió matriz
- Completó actividad
- Completó nodo

**Hexágono de transición (posterior):**
- Texto: "De clasificar a detectar errores"
- Conecta hacia: PREALG-N1-B12-DETECTIVE-FALSEDADES
- Se ilumina al completar B11.

---

### A4. Diferenciación por nivel (Básico / Intermedio / Avanzado)

| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| **Columnas de la matriz** | ℕ, ℤ, ℚ, Irracional, ℝ (sin ℂ) | + ℂ y descriptor | + ℂ y descriptor |
| **Filas (números)** | Sin 2i, 3 + 2i | Con filas complejas | Con filas complejas |
| **Ejemplo guiado** | Completo y detallado (5) | Resumido | Solo el resultado |
| **Pista** | Reglas completas visibles | Reglas bajo botón | Reglas bajo botón |
| **Retroalimentación** | Muy explícita por celda | Por grupo de error | Resumida |
| **Números adicionales (opcional)** | — | — | Variante: −7/2, 0.333…, 1 − i |

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Pertenencia múltiple vs. conjunto mínimo]**
El contraste deliberado con B10 (conjunto más específico) es el núcleo pedagógico. B10 redujo carga cognitiva pidiendo una sola zona; B11 ahora exige reconocer **todas** las pertenencias. La transición explícita ("antes bastaba con el más específico; ahora marcamos todos") previene la misconception `confunde_conjunto_minimo_con_pertenencia_multiple`.

**[NOTA PEDAGÓGICA — Cadena de inclusión como herramienta]**
La cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ funciona como regla generativa: si conoces el conjunto más específico, la cadena te da automáticamente las demás pertenencias. El ejemplo guiado de 5 modela este razonamiento paso a paso.

**[NOTA PEDAGÓGICA — Irracionales como caso especial]**
Los irracionales rompen la cadena lineal: están en ℝ y ℂ, pero NO en ℚ. Esto requiere atención especial (𝕀 ⊂ ℝ pero 𝕀 ⊄ ℚ). La retroalimentación específica aborda tanto "marcar irracional como racional" como "no marcar irracional como real".

**[NOTA PEDAGÓGICA — Descriptor vs. conjunto formal]**
La nota sobre "imaginario puro" como descriptor (no conjunto formal) es sutil pero importante. Previene que los estudiantes traten "imaginario puro" como una columna más al nivel de ℕ, ℤ, etc. Es una **descripción** dentro de ℂ, no un conjunto de la cadena.

---

### A6. Accesibilidad

- **Matriz de checkboxes:** Navegable por teclado; cada celda con etiqueta ARIA ("¿5 pertenece a Naturales?").
- **Colores:** Estados de celda no dependen solo de color; íconos ✓ y ⚠.
- **Matemática:** Todas las expresiones (cadena de inclusión, 5/1, −3/1, a + 0i, 2i = 0 + 2i) con KaTeX y ARIA.
- **Encabezados de matriz:** Headers de fila y columna asociados semánticamente a cada celda.
- **Contraste:** Relación mínima 4.5:1.

---

### A7. Notas de citas pedagógicas

- **Relaciones de inclusión y razonamiento transitivo:** Piaget (1965) — la comprensión de inclusión de clases es un hito cognitivo.
- **De simple a complejo:** Sweller (1988) — secuenciar conjunto único (B10) antes de pertenencia múltiple (B11).
- **Ejemplo trabajado (worked example):** Sweller & Cooper (1985) — el ejemplo guiado de 5 reduce carga antes de la práctica.
- **Misconception de irracionales:** Sirotic & Zazkis (2007), Fischbein (1994) — la relación irracionales/reales es contraintuitiva.

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo]
- [componente-cadena-inclusion] — Visualización de ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ
- [componente-ejemplo-guiado] — Desarrollo paso a paso del número 5
- [componente-matriz-pertenencia] — Matriz números × conjuntos con checkboxes
- [componente-pista] — Reglas de inclusión
- [componente-retroalimentacion-modal] — Feedback por celda/grupo
- [componente-transicion-hexagono]

**Gating:**
- [flag-explored_complex_branch] — Controla columna ℂ y filas complejas

**Render bloqueante:**
- Verificar render de: cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ, 𝕀 ⊂ ℝ, 5/1, −3/1, a + 0i, 2i = 0 + 2i, 3 + 2i, √2, π.
- **Crítico:** Matriz de selección responsiva y accesible en móvil (puede requerir scroll horizontal o diseño adaptado).

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
  "node_type": "formative_practice_classification_multiple",
  "name": "El Clasificador II: pertenencia múltiple",
  "position_in_route": "ruta_nucleo_practica_clasificacion_2",
  "unlock_rule": "completed_node:PREALG-N1-B10-CLASIFICADOR-BASICO",
  "previous_node_id": "PREALG-N1-B10-CLASIFICADOR-BASICO",
  "next_node_id": "PREALG-N1-B12-DETECTIVE-FALSEDADES",
  "order": 11,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "affects_elo": false,
  "safe_zone": true,
  "min_attempts_before_completion": 2,

  "inclusion_chain": "ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ",
  "special_inclusion": "𝕀 ⊂ ℝ (irracionales dentro de reales, fuera de racionales)",
  "descriptor_note": "'Imaginario puro' es descriptor dentro de ℂ, no conjunto formal de la cadena",

  "classification_task": {
    "task_type": "membership_matrix",
    "instruction": "Para cada número, marca todos los conjuntos a los que pertenece.",
    "columns": [
      {"id": "N", "label": "Naturales (ℕ)"},
      {"id": "Z", "label": "Enteros (ℤ)"},
      {"id": "Q", "label": "Racionales (ℚ)"},
      {"id": "I", "label": "Irracionales (𝕀)"},
      {"id": "R", "label": "Reales (ℝ)"},
      {"id": "C", "label": "Complejos (ℂ)", "requires_flag": "explored_complex_branch"}
    ],
    "descriptor_column": {"id": "descriptor", "label": "Descriptor", "values": ["Imaginario puro", "Complejo no real", "—"]},
    "expected_membership": [
      {"number": "-3",   "label": "-3",         "N": false, "Z": true,  "Q": true,  "I": false, "R": true,  "C": true,  "descriptor": "—"},
      {"number": "0",    "label": "0",          "N": true,  "Z": true,  "Q": true,  "I": false, "R": true,  "C": true,  "descriptor": "—"},
      {"number": "1/2",  "label": "\\frac{1}{2}","N": false, "Z": false, "Q": true,  "I": false, "R": true,  "C": true,  "descriptor": "—"},
      {"number": "sqrt2","label": "\\sqrt{2}",  "N": false, "Z": false, "Q": false, "I": true,  "R": true,  "C": true,  "descriptor": "—"},
      {"number": "pi",   "label": "\\pi",       "N": false, "Z": false, "Q": false, "I": true,  "R": true,  "C": true,  "descriptor": "—"},
      {"number": "5",    "label": "5",          "N": true,  "Z": true,  "Q": true,  "I": false, "R": true,  "C": true,  "descriptor": "—"},
      {"number": "2i",   "label": "2i",         "N": false, "Z": false, "Q": false, "I": false, "R": false, "C": true,  "descriptor": "Imaginario puro", "requires_flag": "explored_complex_branch"},
      {"number": "3+2i", "label": "3 + 2i",     "N": false, "Z": false, "Q": false, "I": false, "R": false, "C": true,  "descriptor": "Complejo no real", "requires_flag": "explored_complex_branch"}
    ]
  },

  "guided_example": {
    "number": "5",
    "steps": [
      {"set": "ℕ", "reason": "porque es natural"},
      {"set": "ℤ", "reason": "porque todo natural es entero"},
      {"set": "ℚ", "reason": "porque puede escribirse como 5 = 5/1"},
      {"set": "ℝ", "reason": "porque se ubica en la recta numérica"},
      {"set": "ℂ", "reason": "porque puede escribirse como 5 = 5 + 0i"}
    ],
    "conclusion": "5 ∈ ℕ, ℤ, ℚ, ℝ, ℂ"
  },

  "feedback": {
    "all_correct": {
      "title": "✓ Clasificación rigurosa correcta",
      "body": "Bien. Ahora reconoces que un número puede pertenecer a varios conjuntos.\nLa clave está en la inclusión: ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ\nPor eso, si un número es natural, también es entero, racional, real y complejo."
    },
    "errors": [
      {
        "error_id": "only_most_specific",
        "title": "⚠ Ahora buscamos todas las pertenencias",
        "body": "En el clasificador anterior bastaba con marcar el conjunto más específico.\nPero en esta fase debes marcar todos los conjuntos a los que pertenece el número.\nPor ejemplo: 5 ∈ ℕ, pero también 5 ∈ ℤ, ℚ, ℝ, ℂ",
        "misconception_tag": "marca_solo_conjunto_mas_especifico"
      },
      {
        "error_id": "zero_not_natural",
        "title": "⚠ Recuerda la convención",
        "body": "En este nivel usamos: ℕ = {0, 1, 2, 3, …}\nPor eso: 0 ∈ ℕ\nY además: 0 ∈ ℤ, ℚ, ℝ, ℂ",
        "misconception_tag": "excluye_cero_de_naturales_pese_a_convencion"
      },
      {
        "error_id": "integer_not_rational",
        "title": "⚠ Todo entero es racional",
        "body": "Todo número entero puede escribirse con denominador 1.\nPor ejemplo: −3 = −3/1\nPor eso: −3 ∈ ℤ, ℚ, ℝ, ℂ",
        "misconception_tag": "no_reconoce_Z_dentro_de_Q_R_C"
      },
      {
        "error_id": "rational_not_real",
        "title": "⚠ Los racionales están en la recta",
        "body": "Todo racional es real porque puede ubicarse en la recta numérica.\nPor ejemplo: 1/2 ∈ ℚ y también 1/2 ∈ ℝ",
        "misconception_tag": "no_reconoce_Q_dentro_de_R_C"
      },
      {
        "error_id": "rational_not_complex",
        "title": "⚠ Los reales también son complejos",
        "body": "Todo número real puede escribirse como complejo con parte imaginaria cero.\nPor ejemplo: 1/2 = 1/2 + 0i\nPor eso: 1/2 ∈ ℂ",
        "misconception_tag": "no_reconoce_reales_como_complejos"
      },
      {
        "error_id": "irrational_as_rational",
        "title": "⚠ Son reales, pero no racionales",
        "body": "√2 y π son irracionales.\nEso significa que pertenecen a: 𝕀 (irracionales)\nTambién son reales y complejos, pero no racionales.",
        "misconception_tag": "clasifica_irracional_como_racional"
      },
      {
        "error_id": "irrational_not_real",
        "title": "⚠ Los irracionales también son reales",
        "body": "Los irracionales sí pertenecen a los reales.\n𝕀 ⊂ ℝ\nEso significa que están dentro de ℝ, pero fuera de ℚ.",
        "misconception_tag": "no_reconoce_irracionales_como_reales"
      },
      {
        "error_id": "irrational_not_complex",
        "title": "⚠ Todo real también es complejo",
        "body": "√2 y π son reales.\nTodo real puede escribirse como complejo con parte imaginaria cero:\n√2 = √2 + 0i, π = π + 0i\nPor eso también pertenecen a ℂ.",
        "misconception_tag": "no_reconoce_reales_como_complejos"
      },
      {
        "error_id": "2i_as_real",
        "title": "⚠ 2i no está en la recta real",
        "body": "2i es un complejo no real.\nSe puede escribir como: 2i = 0 + 2i\nPertenece a ℂ, pero no a ℝ.\nTambién es un imaginario puro.",
        "misconception_tag": "ubica_complejos_no_reales_en_recta_real"
      },
      {
        "error_id": "2i_as_irrational",
        "title": "⚠ Irracional no es lo mismo que imaginario",
        "body": "Los irracionales son números reales que no son racionales.\nPero 2i no es real. Pertenece a los complejos y es un imaginario puro.\nPor eso no se clasifica como irracional.",
        "misconception_tag": "confunde_imaginario_puro_con_irracional"
      },
      {
        "error_id": "3plus2i_as_real",
        "title": "⚠ Tiene parte imaginaria distinta de cero",
        "body": "3 + 2i tiene parte real 3 y parte imaginaria 2.\nComo su parte imaginaria no es cero, no pertenece a la recta real.\nPertenece a ℂ, pero no a ℝ.",
        "misconception_tag": "ubica_complejos_no_reales_en_recta_real"
      },
      {
        "error_id": "3plus2i_as_pure",
        "title": "⚠ No es imaginario puro",
        "body": "Un imaginario puro tiene parte real cero.\nPor ejemplo: 2i = 0 + 2i\nPero: 3 + 2i tiene parte real 3. Por eso no es imaginario puro.",
        "misconception_tag": "confunde_conjunto_formal_con_descriptor"
      }
    ]
  },

  "hint": {
    "button_label": "Necesito una pista",
    "body": "Usa estas reglas:\n- Si un número es natural, también es entero, racional, real y complejo.\n- Si un número es entero, también es racional, real y complejo.\n- Si un número es racional, también es real y complejo.\n- Si un número es irracional, también es real y complejo.\n- Si un número tiene i y su parte imaginaria no es cero, es complejo.\n- Si un complejo tiene parte imaginaria distinta de cero, no está en la recta real.\n- Si un complejo tiene parte imaginaria cero, es real."
  },

  "events_to_register": [
    "node_viewed",
    "inclusion_chain_viewed",
    "guided_example_viewed",
    "activity_started",
    "hint_opened",
    "cell_marked",
    "matrix_verified",
    "feedback_viewed",
    "misconception_detected",
    "matrix_corrected",
    "activity_completed",
    "node_completed",
    "transition_initiated"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_ONLY_SPECIFIC_CORRECTED",
      "level": "observation",
      "trigger": "Student marks only most specific set but corrects after feedback",
      "message_educator": "El estudiante inicialmente marcó solo el conjunto más específico, pero corrigió tras la retroalimentación. Se recomienda observar su desempeño en el Detective de Falsedades."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_INCLUSION_FAILURE",
      "level": "reinforcement_suggested",
      "trigger": "Student fails inclusion relations (Z⊂Q, Q⊂R, R⊂C) repeatedly",
      "message_educator": "El estudiante presenta dificultad recurrente con las relaciones de inclusión entre conjuntos. Se recomienda reforzar la cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ antes de avanzar."
    },
    {
      "condition_id": "ALERT_INTERVENTION_BROAD_INCLUSION",
      "level": "teacher_intervention",
      "trigger": "Student maintains inclusion errors after feedback across multiple numbers",
      "message_educator": "El estudiante mantiene dificultades amplias con la pertenencia múltiple. Se recomienda intervención directa con el diagrama de inclusión y ejemplos guiados."
    },
    {
      "condition_id": "ALERT_GROUP_IRRATIONALS_REALS",
      "level": "reinforcement_suggested_group",
      "trigger": "More than 40% of group fails to mark irrationals as real or complex",
      "message_educator": "El grupo presenta dificultades con la relación irracionales/reales. Se recomienda reforzar que 𝕀 ⊂ ℝ ⊂ ℂ."
    }
  ],

  "level_presentation": {
    "basico": {
      "show_complex_column_and_rows": false,
      "guided_example": "full",
      "hint_always_visible": true,
      "feedback_detail": "per_cell_explicit"
    },
    "intermedio": {
      "show_complex_column_and_rows": true,
      "guided_example": "summarized",
      "hint_always_visible": false,
      "feedback_detail": "per_error_group"
    },
    "avanzado": {
      "show_complex_column_and_rows": true,
      "guided_example": "result_only",
      "hint_always_visible": false,
      "feedback_detail": "summarized",
      "additional_numbers": ["-7/2", "0.333...", "1-i"]
    }
  },

  "design_handoff": {
    "node_state": "bloqueado|actual|completado",
    "path_position": "ruta_nucleo_practica_clasificacion_2",
    "gating_flag": "explored_complex_branch",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-cadena-inclusion]",
      "[componente-ejemplo-guiado]",
      "[componente-matriz-pertenencia]",
      "[componente-pista]",
      "[componente-retroalimentacion-modal]",
      "[componente-transicion-hexagono]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[color-celda-correcta]",
      "[color-celda-revision]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ, 𝕀 ⊂ ℝ, 5/1, −3/1, a + 0i, 2i = 0 + 2i, 3 + 2i, √2, π; matriz de selección responsiva y accesible en móvil"
  }
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** de B11 (Clasificador II):
- ✅ Texto completo de Katia
- ✅ Cadena de inclusión y nota sobre descriptores
- ✅ Matriz de pertenencia completa (8 números × 6 conjuntos + descriptor)
- ✅ Ejemplo guiado del número 5
- ✅ 12 retroalimentaciones específicas por error
- ✅ Pista con reglas de inclusión
- ✅ Storyboard detallado
- ✅ **Gating de columna ℂ y filas complejas** por `explored_complex_branch`
- ✅ JSON técnico limpio

**Corrección de migración:** Se restauró la cadena de inclusión completa, las fracciones, las expresiones a + 0i y todos los símbolos de conjuntos que en el .docx original quedaron como corchetes vacíos.
