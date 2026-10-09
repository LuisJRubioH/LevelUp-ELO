# Nodo: El Detective de Falsedades
**ID:** PREALG-N1-B12-DETECTIVE-FALSEDADES

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B12-DETECTIVE-FALSEDADES |
| **Título visible** | El Detective de Falsedades |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular principal de práctica formativa conceptual |
| **Ubicación en la ruta** | Tras B11 (Clasificador Riguroso); se desbloquea al completarlo |
| **Función pedagógica** | Evaluar la comprensión conceptual de las relaciones entre conjuntos numéricos mediante afirmaciones verdadero/falso con retroalimentación específica |
| **Objetivo de aprendizaje** | El estudiante identifica afirmaciones verdaderas y falsas sobre pertenencia, inclusión, racionalidad, irracionalidad, reales y complejos |
| **Microhabilidades** | • Evaluar afirmaciones de inclusión entre conjuntos<br>• Distinguir implicaciones verdaderas y falsas (recíproca)<br>• Reconocer que no toda afirmación inversa es verdadera<br>• Diferenciar racionales e irracionales<br>• Reconocer que decimales periódicos son racionales<br>• Reconocer que los irracionales son reales<br>• Reconocer que los reales están incluidos en los complejos<br>• Diferenciar complejos reales y no reales<br>• Justificar una clasificación con propiedades matemáticas |
| **Misconception tags** | confunde_implicacion_con_reciproca<br>cree_que_todo_decimal_infinito_es_irracional<br>no_reconoce_irracionales_como_reales<br>cree_que_todo_real_es_racional<br>no_reconoce_reales_como_complejos<br>cree_que_todo_complejo_es_real<br>confunde_imaginario_puro_con_irracional<br>responde_sin_justificacion_conceptual |
| **Referencias de refuerzo** | B03-ESCALERA, B06-RACIONALES, B07-IRRACIONALES, B08-REALES, B09-COMPLEJOS, B10-CLASIFICADOR-BASICO, B11-CLASIFICADOR-RIGUROSO, B13-CIERRE-DIAGNOSTICO |

> **Nota de migración (KaTeX):** En el .docx fuente, todas las expresiones de las notas y retroalimentaciones (cadena de inclusión, fracciones, √2, π, 0.333… = 1/3, π = 3.14159265…, 5 = 5 + 0i, 2i = 0 + 2i, a + bi, símbolos de pertenencia ∈/∉) quedaron como corchetes vacíos `[ ]`. Se restauraron a partir de la sección JSON técnico del propio documento (que conserva `\pi`, `0.333...`, `\frac{1}{3}`, etc.) y del contexto de cada afirmación.

> **Nota de gating:** Las afirmaciones A10–A14 tratan sobre números complejos. Para estudiantes de banda **Básico** que **no** exploraron la rama compleja (`explored_complex_branch = false`), estas cinco afirmaciones se **omiten** y el detective se limita a A1–A9 (naturales, enteros, racionales, irracionales, reales). Para Intermedio/Avanzado se presentan las 14 afirmaciones completas. La retroalimentación global de complejos solo aplica cuando A10–A14 están presentes.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
El Detective de Falsedades
```

**Subtítulo:**
```
Lee cada afirmación y decide si es verdadera o falsa.
```

---

#### 2.2 Diálogo inicial de Katia

**Contexto visual:** Katia aparece con una lupa o elemento visual de detective.

**Diálogo de Katia:**
```
Ya clasificaste números de dos formas: por su conjunto más específico y por 
todas sus pertenencias.

Ahora vamos a revisar afirmaciones.

Algunas parecen verdaderas, pero tienen una trampa. Tu tarea es detectar 
cuáles son correctas y cuáles son falsas.

No basta con adivinar. Después de responder, revisaremos la razón.
```

---

#### 2.3 Instrucción principal

**Texto visible:**
```
Marca cada afirmación como verdadera o falsa.

Después de responder, el sistema te mostrará una explicación.
```

**Nota visible:**
```
Recuerda estas relaciones:

ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ

y:

𝕀 = ℝ ∖ ℚ
```

---

#### 2.4 Afirmaciones del detective

| Código | Afirmación | Respuesta esperada |
|--------|-----------|--------------------|
| A1 | Todo número natural es entero. | Verdadero |
| A2 | Todo número entero es natural. | Falso |
| A3 | Todo número entero es racional. | Verdadero |
| A4 | Todo número racional es real. | Verdadero |
| A5 | Todo número real es racional. | Falso |
| A6 | Todo decimal infinito es irracional. | Falso |
| A7 | 0.333… es racional. | Verdadero |
| A8 | π es racional porque se puede aproximar con 3.14. | Falso |
| A9 | Todo número irracional es real. | Verdadero |
| A10 | Todo número real es complejo. | Verdadero |
| A11 | Todo número complejo es real. | Falso |
| A12 | 2i pertenece a la recta real. | Falso |
| A13 | 3 + 2i es un complejo con parte real e imaginaria. | Verdadero |
| A14 | 2i es un imaginario puro. | Verdadero |

---

#### 2.5 Interacción principal

**Tipo de interacción:** Tabla verdadero/falso.

**Texto visible:**
```
Marca verdadero o falso en cada afirmación.
```

**Regla sugerida:**
```
El estudiante puede responder todas las afirmaciones y luego presionar "Verificar".
```

---

#### 2.6 Retroalimentaciones específicas

##### A1 — Todo número natural es entero

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. Los naturales están dentro de los enteros:

ℕ ⊂ ℤ

Por eso, todo natural es entero.
```

**Retroalimentación si responde falso:**
```
Revisa la inclusión. Todo número natural pertenece también a los enteros.

Por ejemplo:

5 ∈ ℕ

y también:

5 ∈ ℤ
```

---

##### A2 — Todo número entero es natural

**Respuesta esperada:** Falso.

**Retroalimentación si responde correctamente:**
```
Correcto. No todo entero es natural.

Por ejemplo:

−3 ∈ ℤ

pero:

−3 ∉ ℕ
```

**Retroalimentación si responde verdadero:**
```
Cuidado con la afirmación inversa. Es verdad que todo natural es entero, pero 
no es verdad que todo entero sea natural.

Los enteros incluyen números negativos, y los naturales no.
```

**Misconception tag registrado:** `confunde_implicacion_con_reciproca`

---

##### A3 — Todo número entero es racional

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. Todo entero puede escribirse como una fracción con denominador 1.

−3 = −3/1

Por eso, todo entero es racional.
```

**Retroalimentación si responde falso:**
```
Recuerda que un número es racional si puede escribirse como fracción de enteros 
con denominador distinto de cero.

Todo entero puede escribirse con denominador 1.
```

---

##### A4 — Todo número racional es real

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. Los racionales están dentro de los reales:

ℚ ⊂ ℝ
```

**Retroalimentación si responde falso:**
```
Los racionales sí son reales. Pueden ubicarse en la recta numérica.

Por ejemplo:

1/2 ∈ ℝ
```

---

##### A5 — Todo número real es racional

**Respuesta esperada:** Falso.

**Retroalimentación si responde correctamente:**
```
Correcto. No todo real es racional.

Existen reales irracionales, como:

√2, π
```

**Retroalimentación si responde verdadero:**
```
Revisa los irracionales. √2 y π son reales, pero no son racionales.

Por eso no todo real es racional.
```

**Misconception tag registrado:** `cree_que_todo_real_es_racional`

---

##### A6 — Todo decimal infinito es irracional

**Respuesta esperada:** Falso.

**Retroalimentación si responde correctamente:**
```
Correcto. Algunos decimales infinitos son racionales si son periódicos.

Por ejemplo:

0.333… = 1/3
```

**Retroalimentación si responde verdadero:**
```
No todo decimal infinito es irracional.

La clave es si el decimal repite un patrón. Si es periódico, puede ser racional.
```

**Misconception tag registrado:** `cree_que_todo_decimal_infinito_es_irracional`

---

##### A7 — 0.333… es racional

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. 0.333… es periódico y puede escribirse como:

0.333… = 1/3

Por eso es racional.
```

**Retroalimentación si responde falso:**
```
Aunque 0.333… no termina, sí repite el 3 indefinidamente.

Ese patrón periódico indica que es racional.
```

**Misconception tag registrado:** `cree_que_todo_decimal_infinito_es_irracional`

---

##### A8 — π es racional porque se puede aproximar con 3.14

**Respuesta esperada:** Falso.

**Retroalimentación si responde correctamente:**
```
Correcto. 3.14 es una aproximación racional de π, pero no es π exacto.

π = 3.14159265…

y sus decimales son infinitos no periódicos.
```

**Retroalimentación si responde verdadero:**
```
Cuidado con confundir aproximación y valor exacto.

3.14 es una aproximación. π exacto no puede escribirse como fracción de enteros.
```

**Misconception tag registrado:** `cree_que_todo_real_es_racional`

---

##### A9 — Todo número irracional es real

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. Los irracionales son reales que no son racionales:

𝕀 = ℝ ∖ ℚ
```

**Retroalimentación si responde falso:**
```
Los irracionales sí pertenecen a los reales.

Están en la recta numérica, pero no pertenecen a ℚ.
```

**Misconception tag registrado:** `no_reconoce_irracionales_como_reales`

---

##### A10 — Todo número real es complejo

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. Todo real puede escribirse como complejo con parte imaginaria cero.

Por ejemplo:

5 = 5 + 0i

Por eso:

ℝ ⊂ ℂ
```

**Retroalimentación si responde falso:**
```
Los reales también son complejos.

La diferencia es que tienen parte imaginaria cero.
```

**Misconception tag registrado:** `no_reconoce_reales_como_complejos`

---

##### A11 — Todo número complejo es real

**Respuesta esperada:** Falso.

**Retroalimentación si responde correctamente:**
```
Correcto. Algunos complejos no son reales.

Por ejemplo:

3 + 2i

no está en la recta real porque su parte imaginaria es distinta de cero.
```

**Retroalimentación si responde verdadero:**
```
Cuidado con la inclusión inversa.

Todo real es complejo, pero no todo complejo es real.
```

**Misconception tag registrado:** `cree_que_todo_complejo_es_real`

---

##### A12 — 2i pertenece a la recta real

**Respuesta esperada:** Falso.

**Retroalimentación si responde correctamente:**
```
Correcto. 2i no pertenece a la recta real.

Se representa sobre el eje imaginario del plano complejo.
```

**Retroalimentación si responde verdadero:**
```
2i no está en la recta real.

Puede escribirse como:

2i = 0 + 2i

Tiene parte imaginaria distinta de cero, por eso es complejo no real.
```

**Misconception tag registrado:** `cree_que_todo_complejo_es_real`

---

##### A13 — 3 + 2i es complejo con parte real e imaginaria

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. En:

3 + 2i

la parte real es 3 y la parte imaginaria es 2.
```

**Retroalimentación si responde falso:**
```
Revisa la forma general:

a + bi

En 3 + 2i, a = 3 y b = 2. Por eso tiene parte real e imaginaria.
```

---

##### A14 — 2i es imaginario puro

**Respuesta esperada:** Verdadero.

**Retroalimentación si responde correctamente:**
```
Correcto. 2i puede escribirse como:

0 + 2i

Su parte real es cero, por eso es imaginario puro.
```

**Retroalimentación si responde falso:**
```
Un imaginario puro es un complejo cuya parte real es cero.

Como:

2i = 0 + 2i

entonces 2i sí es imaginario puro.
```

**Misconception tag registrado:** `confunde_imaginario_puro_con_irracional`

---

#### 2.7 Retroalimentación global

##### Si el estudiante acierta todas o casi todas

**Título del recuadro:**
```
Buen trabajo de detective
```

**Texto visible:**
```
Identificaste correctamente la mayoría de afirmaciones. Ya puedes distinguir 
inclusión, pertenencia y ejemplos específicos de cada conjunto.
```

---

##### Si falla varias afirmaciones de inclusión

**Título del recuadro:**
```
Revisemos las inclusiones
```

**Texto visible:**
```
Tus errores se concentran en relaciones entre conjuntos.

Conviene repasar esta cadena:

ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ
```

---

##### Si falla varias afirmaciones sobre racionales e irracionales

**Título del recuadro:**
```
Revisemos racionales e irracionales
```

**Texto visible:**
```
Tus errores se concentran en decimales y fracciones.

Recuerda:

- Decimal exacto: racional.
- Decimal periódico: racional.
- Decimal infinito no periódico: irracional.
```

---

##### Si falla varias afirmaciones sobre complejos

**Título del recuadro:**
```
Revisemos recta y plano
```

**Texto visible:**
```
Tus errores se concentran en números complejos.

Recuerda:

- Los reales están en la recta.
- Los complejos se representan en el plano.
- Todo real es complejo.
- No todo complejo es real.
```

---

#### 2.8 Mensaje de cierre

**Texto visible:**
```
Detective completado.
```

**Diálogo de Katia:**
```
Ya revisaste afirmaciones sobre los conjuntos numéricos.

Ahora veremos tu diagnóstico final del nivel: qué dominaste, qué conviene 
reforzar y qué pantallas puedes volver a visitar.
```

**Botón principal:**
```
Ver diagnóstico
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B12-DETECTIVE-FALSEDADES.
- El nodo aparece en estado `actual` tras completar el clasificador riguroso (B11).
- Un hexágono de transición aparece **antes** del nodo:
  ```
  De clasificar a evaluar afirmaciones
  ```

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. Aparece el título "El Detective de Falsedades".
2. Katia aparece con la lupa de detective e introduce la actividad.
3. Se muestra el recordatorio de inclusión (ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ; 𝕀 = ℝ ∖ ℚ).
4. Aparece la tabla de afirmaciones (A1–A14, o A1–A9 sin rama compleja).
5. El estudiante marca verdadero o falso en cada fila.
6. Se habilita el botón "Verificar".

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante realiza esto:

1. **Lee cada afirmación.**
2. **Marca verdadero o falso** en cada una.
3. **Presiona "Verificar".**
4. **Lee la retroalimentación específica** por afirmación incorrecta (o por patrón de error).
5. **Corrige** sus respuestas si se habilita un segundo intento.
6. **Lee la retroalimentación global** (resumen de fortalezas y dificultades).
7. **Presiona "Ver diagnóstico"** y el nodo se marca como completado.

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Presentación** | Instrucción + recordatorio de inclusión | Lectura | Prepara el marco |
| **2 — Tabla activa** | Tabla de afirmaciones con botones V/F por fila | Marcar V/F | El estudiante responde |
| **3 — Verificación** | Botón "Verificar"; sistema detecta patrones | Botón "Verificar" | Sistema evalúa |
| **4 — Retroalimentación específica** | Explicación por afirmación incorrecta o por grupo | Botón "Siguiente" | Aclara cada error |
| **5 — Corrección** | Afirmaciones incorrectas resaltadas | Re-marcar + re-verificar | Segundo intento si aplica |
| **6 — Retroalimentación global** | Resumen de fortalezas y dificultades | Botón "Continuar" | Cierre formativo |
| **7 — Transición** | Hexágono + botón "Ver diagnóstico" | Botón navegable | Prepara B13 |

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono de transición.
- **Katia con lupa:** Slide-in lateral; la lupa puede tener un brillo sutil.
- **Recordatorio de inclusión:** Fade-in; la cadena puede animarse de izquierda a derecha.
- **Tabla aparece:** Fade-in con filas en stagger.
- **Marcar V/F:** El botón seleccionado se resalta con animación.
- **Verificación:** Afirmaciones correctas brillan verde; incorrectas vibran ámbar.
- **Patrón de error:** Si se detecta un patrón (inclusión, racionales/irracionales, complejos), las filas afectadas se agrupan visualmente.
- **Corrección:** Las filas se actualizan con animación.
- **Cierre:** El peldaño se marca completado; el hexágono siguiente se ilumina.

---

#### 3.6 Relación con el mapa visual

**Nodo circular:** Representa la pantalla principal del Detective de Falsedades.

**Punticos internos (eventos registrados):**
- Visualizó instrucción
- Visualizó recordatorio de inclusión
- Marcó afirmaciones
- Verificó respuestas
- Vio retroalimentación específica
- Corrigió respuestas (si aplica)
- Vio retroalimentación global
- Completó nodo

**Hexágono de transición (posterior):**
- Texto: "De evaluación formativa a diagnóstico"
- Conecta hacia: PREALG-N1-B13-CIERRE-DIAGNOSTICO
- Se ilumina al completar B12.

---

### A4. Diferenciación por nivel (Básico / Intermedio / Avanzado)

| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| **Afirmaciones presentadas** | A1–A9 (sin complejos, sin rama compleja) | A1–A14 completas | A1–A14 completas |
| **Recordatorio de inclusión** | Visible y ampliado por defecto | Visible | Colapsable |
| **Retroalimentación** | Muy explícita por afirmación | Por afirmación + patrón | Resumida por patrón |
| **Segundo intento** | Siempre habilitado con guía | Habilitado | Habilitado |
| **Justificación** | Solo marcar V/F | Marcar V/F | Variante: seleccionar la razón correcta tras marcar |
| **Afirmaciones adicionales (opcional)** | — | — | Variante de reto: afirmaciones con cuantificadores ("existe un real que no es complejo") |

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Implicación vs. recíproca]**
El núcleo conceptual del nodo es la asimetría de la inclusión: "todo natural es entero" es verdadero, pero su recíproca "todo entero es natural" es falsa (A1 vs. A2; A10 vs. A11). Esta distinción lógica (implicación ≠ recíproca) es una fuente recurrente de error y se aborda con pares de afirmaciones deliberadamente contrastantes (Sweller, 1988, sobre secuenciar para no sobrecargar).

**[NOTA PEDAGÓGICA — Aproximación vs. valor exacto]**
A8 (π es racional porque ≈ 3.14) ataca directamente la misconception de que un irracional "se vuelve" racional al aproximarlo. La retroalimentación distingue explícitamente aproximación de valor exacto, anclando en la definición de irracional por "no es fracción de enteros" (Sirotic & Zazkis, 2007a), no por el patrón decimal.

**[NOTA PEDAGÓGICA — Decimal periódico es racional]**
A6 y A7 forman un par: A6 niega "todo decimal infinito es irracional" y A7 lo confirma con 0.333… = 1/3. Juntas consolidan que la infinitud del decimal no determina la irracionalidad; lo determinante es la periodicidad (Fischbein, Jehiam & Cohen, 1995).

**[NOTA PEDAGÓGICA — Retroalimentación por patrón, no solo por ítem]**
La retroalimentación global agrupa los errores en tres patrones (inclusión, racionales/irracionales, complejos) en vez de tratar cada fallo aislado. Esto convierte el detective en diagnóstico formativo: señala el área conceptual a reforzar y enlaza con los nodos de origen (Hattie & Timperley, 2007; Black & Wiliam, 1998).

---

### A6. Accesibilidad

- **Tabla V/F:** Navegable por teclado; cada fila con etiqueta ARIA ("Afirmación A1: Todo número natural es entero. ¿Verdadero o falso?").
- **Colores:** Estados de fila no dependen solo de color; íconos ✓ y ⚠.
- **Matemática:** Todas las expresiones (cadena de inclusión, −3/1, 0.333… = 1/3, π = 3.14159265…, 5 = 5 + 0i, 2i = 0 + 2i, a + bi, 𝕀 = ℝ ∖ ℚ, ∈, ∉) con KaTeX y MathML/`aria-label`. Vocalizar correctamente "0.333 periódico", "i al cuadrado", "no pertenece".
- **Feedback:** Anunciado por lector de pantalla tras verificar.
- **Contraste:** Relación mínima 4.5:1, también en modo oscuro.

---

### A7. Notas de citas pedagógicas

- **Implicación vs. recíproca; secuenciar contrastes sin sobrecargar:** Sweller, J. (1988). Cognitive load during problem solving.
- **Irracional por definición, no por patrón decimal; aproximación vs. exacto:** Sirotic, N., & Zazkis, R. (2007a). Irrational numbers: the gap between formal and intuitive knowledge.
- **Obstáculo epistemológico racional→irracional; decimales periódicos:** Fischbein, E., Jehiam, R., & Cohen, D. (1995). The concept of irrational number in high-school students and prospective teachers.
- **Retroalimentación específica, accionable y formativa; diagnóstico por patrón:** Hattie, J., & Timperley, H. (2007). The power of feedback; Black, P., & Wiliam, D. (1998). Inside the black box.
- **Alertas tempranas con retroalimentación individualizada:** Arnold, K. E., & Pistilli, M. D. (2012). Course Signals at Purdue.

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo] — con variante "detective" (lupa)
- [componente-recordatorio-inclusion] — Tarjeta con la cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ
- [componente-tabla-verdadero-falso] — Tabla con filas de afirmación y botones V/F
- [componente-fila-afirmacion] — Fila individual con expresión KaTeX
- [componente-retroalimentacion-modal] — Feedback por afirmación
- [componente-resumen-patron-error] — Retroalimentación global por patrón
- [componente-resultado-formativo] — Resumen de fortalezas/dificultades
- [componente-transicion-hexagono]
- [componente-nav-inferior] — Botón "Ver diagnóstico"

**Componente frontend sugerido (del original):** `FalsehoodDetectiveNode.tsx` con subcomponentes `KatiaDialogueCard`, `ConceptReminderCard`, `TrueFalseTableQuestion`, `TrueFalseStatementRow`, `FeedbackModal`, `MisconceptionPatternSummary`, `FormativeResultSummary`, `ConceptTransitionBadge`, `NodeActionFooter`. Hook: `useTrueFalseConceptReview(nodeId, interactionId)`.

**Gating:**
- [flag-explored_complex_branch] — Controla si A10–A14 se presentan (Básico sin rama compleja ve solo A1–A9)

**Tokens del sistema de diseño:**
- [asset-mascota:Katia], [color-acento-morado], [color-acento-teal], [tipografia-titulo], [tipografia-body]

**Render bloqueante:**
- Verificar render de: cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ, 𝕀 = ℝ ∖ ℚ, −3/1, 1/2, 0.333… = 1/3, π = 3.14159265…, √2, 5 = 5 + 0i, 2i = 0 + 2i, 3 + 2i, a + bi, ∈, ∉.
- **Crítico:** Tabla V/F responsiva y accesible en móvil (puede requerir diseño de fila apilada).

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B12-DETECTIVE-FALSEDADES",
  "level_id": "PREALG-N1",
  "module": "Preálgebra",
  "name": "El Detective de Falsedades",
  "display_title": "El Detective de Falsedades",
  "node_type": "true_false_conceptual_review",
  "map_shape": "circle",
  "position_in_route": "ruta_nucleo_practica_conceptual",
  "unlock_rule": "completed_node:PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
  "previous_node_id": "PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
  "next_node_id": "PREALG-N1-B13-CIERRE-DIAGNOSTICO",
  "order": 12,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "is_safe_zone": true,
  "safe_zone": true,
  "affects_elo": false,
  "allow_correction": true,
  "max_required_attempts": 2,
  "concept": "Evaluación conceptual de conjuntos numéricos",
  "general_tag": "Preálgebra",
  "specific_tag": "Conjuntos numéricos",

  "gating": {
    "flag": "explored_complex_branch",
    "statements_requiring_flag": ["A10", "A11", "A12", "A13", "A14"],
    "note": "Banda Básico sin rama compleja ve solo A1–A9; la retroalimentación global de complejos solo aplica si A10–A14 están presentes"
  },

  "micro_skills": [
    "evaluar_afirmaciones_de_inclusion",
    "distinguir_implicacion_y_reciproca",
    "diferenciar_racionales_e_irracionales",
    "distinguir_reales_y_complejos",
    "justificar_pertenencia_a_conjuntos"
  ],
  "misconception_tags": [
    "confunde_implicacion_con_reciproca",
    "cree_que_todo_decimal_infinito_es_irracional",
    "no_reconoce_irracionales_como_reales",
    "cree_que_todo_real_es_racional",
    "no_reconoce_reales_como_complejos",
    "cree_que_todo_complejo_es_real",
    "confunde_imaginario_puro_con_irracional",
    "responde_sin_justificacion_conceptual"
  ],

  "interaction": {
    "interaction_id": "PREALG-N1-B12-Q01",
    "interaction_type": "true_false_table",
    "prompt": "Marca cada afirmación como verdadera o falsa.",
    "reminder": {
      "inclusion_chain": "ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ",
      "irrationals": "𝕀 = ℝ ∖ ℚ"
    },
    "statements": [
      {
        "id": "A1", "text": "Todo número natural es entero.", "expected_answer": true,
        "micro_skill": "evaluar_afirmaciones_de_inclusion",
        "feedback": {
          "correct": "Correcto. Los naturales están dentro de los enteros: ℕ ⊂ ℤ\nPor eso, todo natural es entero.",
          "incorrect": "Revisa la inclusión. Todo número natural pertenece también a los enteros.\nPor ejemplo: 5 ∈ ℕ y también 5 ∈ ℤ"
        },
        "misconception_on_error": null
      },
      {
        "id": "A2", "text": "Todo número entero es natural.", "expected_answer": false,
        "micro_skill": "distinguir_implicacion_y_reciproca",
        "feedback": {
          "correct": "Correcto. No todo entero es natural.\nPor ejemplo: −3 ∈ ℤ pero −3 ∉ ℕ",
          "incorrect": "Cuidado con la afirmación inversa. Es verdad que todo natural es entero, pero no es verdad que todo entero sea natural.\nLos enteros incluyen números negativos, y los naturales no."
        },
        "misconception_on_error": "confunde_implicacion_con_reciproca"
      },
      {
        "id": "A3", "text": "Todo número entero es racional.", "expected_answer": true,
        "micro_skill": "evaluar_afirmaciones_de_inclusion",
        "feedback": {
          "correct": "Correcto. Todo entero puede escribirse como una fracción con denominador 1.\n−3 = −3/1\nPor eso, todo entero es racional.",
          "incorrect": "Recuerda que un número es racional si puede escribirse como fracción de enteros con denominador distinto de cero.\nTodo entero puede escribirse con denominador 1."
        },
        "misconception_on_error": null
      },
      {
        "id": "A4", "text": "Todo número racional es real.", "expected_answer": true,
        "micro_skill": "evaluar_afirmaciones_de_inclusion",
        "feedback": {
          "correct": "Correcto. Los racionales están dentro de los reales: ℚ ⊂ ℝ",
          "incorrect": "Los racionales sí son reales. Pueden ubicarse en la recta numérica.\nPor ejemplo: 1/2 ∈ ℝ"
        },
        "misconception_on_error": null
      },
      {
        "id": "A5", "text": "Todo número real es racional.", "expected_answer": false,
        "micro_skill": "diferenciar_reales_y_racionales",
        "feedback": {
          "correct": "Correcto. No todo real es racional.\nExisten reales irracionales, como: √2, π",
          "incorrect": "Revisa los irracionales. √2 y π son reales, pero no son racionales.\nPor eso no todo real es racional."
        },
        "misconception_on_error": "cree_que_todo_real_es_racional"
      },
      {
        "id": "A6", "text": "Todo decimal infinito es irracional.", "expected_answer": false,
        "micro_skill": "diferenciar_racionales_e_irracionales",
        "feedback": {
          "correct": "Correcto. Algunos decimales infinitos son racionales si son periódicos.\nPor ejemplo: 0.333… = 1/3",
          "incorrect": "No todo decimal infinito es irracional.\nLa clave es si el decimal repite un patrón. Si es periódico, puede ser racional."
        },
        "misconception_on_error": "cree_que_todo_decimal_infinito_es_irracional"
      },
      {
        "id": "A7", "text": "0.333… es racional.", "expected_answer": true,
        "micro_skill": "reconocer_decimal_periodico_como_racional",
        "feedback": {
          "correct": "Correcto. 0.333… es periódico y puede escribirse como: 0.333… = 1/3\nPor eso es racional.",
          "incorrect": "Aunque 0.333… no termina, sí repite el 3 indefinidamente.\nEse patrón periódico indica que es racional."
        },
        "misconception_on_error": "cree_que_todo_decimal_infinito_es_irracional"
      },
      {
        "id": "A8", "text": "π es racional porque se puede aproximar con 3.14.", "expected_answer": false,
        "micro_skill": "distinguir_aproximacion_y_valor_exacto",
        "feedback": {
          "correct": "Correcto. 3.14 es una aproximación racional de π, pero no es π exacto.\nπ = 3.14159265… y sus decimales son infinitos no periódicos.",
          "incorrect": "Cuidado con confundir aproximación y valor exacto.\n3.14 es una aproximación. π exacto no puede escribirse como fracción de enteros."
        },
        "misconception_on_error": "cree_que_todo_real_es_racional"
      },
      {
        "id": "A9", "text": "Todo número irracional es real.", "expected_answer": true,
        "micro_skill": "reconocer_irracionales_como_reales",
        "feedback": {
          "correct": "Correcto. Los irracionales son reales que no son racionales: 𝕀 = ℝ ∖ ℚ",
          "incorrect": "Los irracionales sí pertenecen a los reales.\nEstán en la recta numérica, pero no pertenecen a ℚ."
        },
        "misconception_on_error": "no_reconoce_irracionales_como_reales"
      },
      {
        "id": "A10", "text": "Todo número real es complejo.", "expected_answer": true,
        "micro_skill": "reconocer_reales_como_complejos",
        "requires_flag": "explored_complex_branch",
        "feedback": {
          "correct": "Correcto. Todo real puede escribirse como complejo con parte imaginaria cero.\nPor ejemplo: 5 = 5 + 0i\nPor eso: ℝ ⊂ ℂ",
          "incorrect": "Los reales también son complejos.\nLa diferencia es que tienen parte imaginaria cero."
        },
        "misconception_on_error": "no_reconoce_reales_como_complejos"
      },
      {
        "id": "A11", "text": "Todo número complejo es real.", "expected_answer": false,
        "micro_skill": "distinguir_reales_y_complejos",
        "requires_flag": "explored_complex_branch",
        "feedback": {
          "correct": "Correcto. Algunos complejos no son reales.\nPor ejemplo: 3 + 2i no está en la recta real porque su parte imaginaria es distinta de cero.",
          "incorrect": "Cuidado con la inclusión inversa.\nTodo real es complejo, pero no todo complejo es real."
        },
        "misconception_on_error": "cree_que_todo_complejo_es_real"
      },
      {
        "id": "A12", "text": "2i pertenece a la recta real.", "expected_answer": false,
        "micro_skill": "distinguir_reales_y_complejos",
        "requires_flag": "explored_complex_branch",
        "feedback": {
          "correct": "Correcto. 2i no pertenece a la recta real.\nSe representa sobre el eje imaginario del plano complejo.",
          "incorrect": "2i no está en la recta real.\nPuede escribirse como: 2i = 0 + 2i\nTiene parte imaginaria distinta de cero, por eso es complejo no real."
        },
        "misconception_on_error": "cree_que_todo_complejo_es_real"
      },
      {
        "id": "A13", "text": "3 + 2i es un complejo con parte real e imaginaria.", "expected_answer": true,
        "micro_skill": "identificar_complejo_general",
        "requires_flag": "explored_complex_branch",
        "feedback": {
          "correct": "Correcto. En 3 + 2i, la parte real es 3 y la parte imaginaria es 2.",
          "incorrect": "Revisa la forma general: a + bi\nEn 3 + 2i, a = 3 y b = 2. Por eso tiene parte real e imaginaria."
        },
        "misconception_on_error": null
      },
      {
        "id": "A14", "text": "2i es un imaginario puro.", "expected_answer": true,
        "micro_skill": "identificar_imaginario_puro",
        "requires_flag": "explored_complex_branch",
        "feedback": {
          "correct": "Correcto. 2i puede escribirse como: 0 + 2i\nSu parte real es cero, por eso es imaginario puro.",
          "incorrect": "Un imaginario puro es un complejo cuya parte real es cero.\nComo: 2i = 0 + 2i, entonces 2i sí es imaginario puro."
        },
        "misconception_on_error": "confunde_imaginario_puro_con_irracional"
      }
    ]
  },

  "global_feedback_by_pattern": {
    "strong": {
      "title": "Buen trabajo de detective",
      "body": "Identificaste correctamente la mayoría de afirmaciones. Ya puedes distinguir inclusión, pertenencia y ejemplos específicos de cada conjunto."
    },
    "inclusion_relations_confusion": {
      "title": "Revisemos las inclusiones",
      "affected_statements": ["A1", "A2", "A3", "A4", "A9", "A10", "A11"],
      "body": "Tus errores se concentran en relaciones entre conjuntos.\nConviene repasar esta cadena: ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ"
    },
    "rational_irrational_confusion": {
      "title": "Revisemos racionales e irracionales",
      "affected_statements": ["A5", "A6", "A7", "A8"],
      "body": "Tus errores se concentran en decimales y fracciones.\nRecuerda:\n- Decimal exacto: racional.\n- Decimal periódico: racional.\n- Decimal infinito no periódico: irracional."
    },
    "complex_confusion": {
      "title": "Revisemos recta y plano",
      "affected_statements": ["A10", "A11", "A12", "A13", "A14"],
      "body": "Tus errores se concentran en números complejos.\nRecuerda:\n- Los reales están en la recta.\n- Los complejos se representan en el plano.\n- Todo real es complejo.\n- No todo complejo es real."
    }
  },

  "events_to_register": [
    "node_viewed",
    "true_false_activity_started",
    "instruction_viewed",
    "inclusion_reminder_viewed",
    "true_false_submitted",
    "misconception_pattern_detected",
    "feedback_viewed",
    "true_false_corrected",
    "true_false_activity_completed",
    "node_completed",
    "concept_transition_started"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_FEW_ERRORS_CORRECTED",
      "level": "observation",
      "trigger": "Student fails 1-3 statements on first attempt but corrects on second",
      "message_educator": "El estudiante cometió errores iniciales en la evaluación de afirmaciones, pero corrigió en el segundo intento. Se recomienda observar su desempeño en el cierre diagnóstico."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_PATTERN",
      "level": "reinforcement_suggested",
      "trigger": "Student shows a dominant error pattern (inclusion / rational-irrational / complex) persisting after feedback",
      "message_educator": "El estudiante muestra un patrón de error concentrado en un área conceptual. Se recomienda reforzar las pantallas asociadas (inclusión, racionales/irracionales o complejos) antes del cierre diagnóstico."
    },
    {
      "condition_id": "ALERT_INTERVENTION_BROAD_PERSISTENT",
      "level": "teacher_intervention",
      "trigger": "Student maintains errors across 3+ conceptual areas after feedback, across this and prior classification nodes",
      "message_educator": "El estudiante mantiene dificultades amplias y persistentes en relaciones entre conjuntos numéricos. Se recomienda intervención directa antes de cerrar el nivel."
    }
  ],

  "level_presentation": {
    "basico": {
      "statements_shown": ["A1","A2","A3","A4","A5","A6","A7","A8","A9"],
      "show_complex_statements": false,
      "reminder_expanded": true,
      "feedback_detail": "per_statement_explicit",
      "second_attempt": "always_with_guidance"
    },
    "intermedio": {
      "statements_shown": "all",
      "show_complex_statements": true,
      "reminder_expanded": true,
      "feedback_detail": "per_statement_and_pattern",
      "second_attempt": "enabled"
    },
    "avanzado": {
      "statements_shown": "all",
      "show_complex_statements": true,
      "reminder_expanded": false,
      "feedback_detail": "pattern_summarized",
      "second_attempt": "enabled",
      "challenge_variant": "select_reason_after_marking; quantifier_statements"
    }
  },

  "persistence_required": [
    "node_viewed", "activity_started", "answers_per_statement", "attempt_count",
    "expected_or_not_per_statement", "misconceptions_detected", "dominant_error_pattern",
    "feedback_viewed", "corrections_made", "activity_completed", "time_on_node",
    "node_completed", "transition_to_diagnosis"
  ],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "node_state": "bloqueado|actual|completado",
    "path_position": "ruta_nucleo_practica_conceptual",
    "gating_flag": "explored_complex_branch",
    "frontend_component": "FalsehoodDetectiveNode.tsx",
    "subcomponents": [
      "KatiaDialogueCard", "ConceptReminderCard", "TrueFalseTableQuestion",
      "TrueFalseStatementRow", "FeedbackModal", "MisconceptionPatternSummary",
      "FormativeResultSummary", "ConceptTransitionBadge", "NodeActionFooter"
    ],
    "hook": "useTrueFalseConceptReview(nodeId, interactionId)",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-recordatorio-inclusion]",
      "[componente-tabla-verdadero-falso]",
      "[componente-fila-afirmacion]",
      "[componente-retroalimentacion-modal]",
      "[componente-resumen-patron-error]",
      "[componente-resultado-formativo]",
      "[componente-transicion-hexagono]",
      "[componente-nav-inferior]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ, 𝕀 = ℝ ∖ ℚ, −3/1, 1/2, 0.333… = 1/3, π = 3.14159265…, √2, 5 = 5 + 0i, 2i = 0 + 2i, 3 + 2i, a + bi, ∈, ∉; tabla V/F responsiva y accesible en móvil"
  },

  "i18n_prefix": "prealgebra.n1.b12"
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** de B12 (El Detective de Falsedades):
- ✅ Texto completo de Katia (intro detective + cierre)
- ✅ Instrucción y recordatorio de inclusión
- ✅ Las 14 afirmaciones con su respuesta esperada
- ✅ Retroalimentación específica **correcta e incorrecta** para cada afirmación (28 textos)
- ✅ Retroalimentación global por los 3 patrones de error
- ✅ Storyboard detallado con 7 estados de pantalla
- ✅ **Gating de afirmaciones de complejos (A10–A14)** por `explored_complex_branch`
- ✅ JSON técnico completo (interacción, eventos, alertas en 3 niveles, presentación por nivel, persistencia, handoff)

**Corrección de migración:** Se restauraron todas las expresiones (cadena de inclusión, fracciones, 0.333… = 1/3, π = 3.14159265…, 5 = 5 + 0i, 2i = 0 + 2i, a + bi, 𝕀 = ℝ ∖ ℚ, símbolos ∈/∉) que en el .docx original quedaron como corchetes vacíos, usando la sección JSON técnico del propio documento.
