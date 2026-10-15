# Nodo: Números complejos — números en el plano
**ID:** PREALG-N1-B09-COMPLEJOS-PLANO

> ⚠️ **NODO DE CALLEJÓN OPCIONAL.** Este nodo solo se desbloquea para estudiantes en banda ELO **Intermedio** o **Avanzado**. El acceso se controla mediante el flag por estudiante `explored_complex_branch`. Los estudiantes de banda Básico avanzan directamente de B08 (Reales) a B10 (Clasificador Básico) sin ver este nodo. Ver Fase 0 (decisiones bloqueadas) para el detalle del gating.

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B09-COMPLEJOS-PLANO |
| **Título visible** | Complejos: números en el plano |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular de ampliación conceptual (callejón opcional) |
| **Ubicación en la ruta** | Después de B08 (Reales); **solo** para bandas Intermedio/Avanzado |
| **Gating** | Flag `explored_complex_branch`; desbloqueo condicionado a banda ELO ≠ Básico |
| **Función pedagógica** | Introducir ℂ como ampliación de ℝ hacia el plano, evitando reducirlos a "números imaginarios" |
| **Objetivo de aprendizaje** | El estudiante reconoce que los complejos tienen parte real e imaginaria, se representan en un plano, y diferencia imaginario puro de complejo con ambas partes |
| **Microhabilidades** | • Reconocer que ℝ se ubica en la recta<br>• Reconocer que ℂ se representa en el plano<br>• Identificar la forma a + bi<br>• Identificar parte real e imaginaria<br>• Diferenciar 2i (imaginario puro) de 3 + 2i<br>• Reconocer que todo real es complejo con parte imaginaria cero |
| **Misconception tags** | cree_que_todo_complejo_es_imaginario<br>cree_que_imaginarios_no_existen<br>confunde_i_imaginaria_con_I_irracionales<br>ubica_complejos_no_reales_en_recta_real<br>no_identifica_parte_real<br>no_identifica_parte_imaginaria<br>no_reconoce_reales_como_complejos_con_imaginaria_cero |
| **Referencias de refuerzo** | PREALG-N1-B07-IRRACIONALES-DECIMALES<br>PREALG-N1-B08-REALES-RECTA<br>PREALG-N1-B10-CLASIFICADOR-BASICO<br>PREALG-N1-B11-CLASIFICADOR-RIGUROSO<br>PREALG-N1-B12-DETECTIVE-FALSEDADES |

> **Nota de migración:** En el .docx original varias expresiones (i² = −1, a + bi, ℂ, √2, etc.) quedaron como corchetes vacíos `[ ]` por fallo de exportación KaTeX. Aquí se restauran a partir del JSON técnico del original.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
Complejos: números en el plano
```

**Subtítulo:**
```
Cuando la recta real no alcanza, ampliamos hacia el plano.
```

---

#### 2.2 Diálogo inicial de Katia

**Contexto visual:** Katia aparece junto al último peldaño de la escalera.

**Diálogo de Katia:**
```
Hasta ahora, todos los números que estudiamos podían ubicarse en una recta: 
la recta real.

Pero algunas situaciones matemáticas necesitan una ampliación más.

Para eso aparecen los números complejos. No son simplemente "los imaginarios"; 
son números que se representan en un plano.
```

---

#### 2.3 Pregunta detonadora del bloque

**Título visible:**
```
Una pregunta extraña
```

**Texto visible:**
```
Sabemos que:

1² = 1

y también:

(−1)² = 1

Entonces aparece una pregunta:

¿Existe un número cuyo cuadrado sea −1?

En los números reales, no existe un número que cumpla eso.

Por eso se define un nuevo número:

i² = −1

Ese número se llama unidad imaginaria.
```

---

#### 2.4 Interacción 1 — Reconocer la unidad imaginaria

**Pregunta visible:**
```
Si i² = −1, ¿qué representa la letra i?
```

**Opciones de respuesta:**
- La unidad imaginaria.
- El conjunto de los irracionales.
- Un número natural.
- El número cero.

**Respuesta esperada:** La unidad imaginaria.

---

#### 2.5 Retroalimentación para Interacción 1

##### Si responde **"La unidad imaginaria"**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
La letra i representa la unidad imaginaria.

Se define por esta propiedad:

i² = −1

Esta idea permite construir números que ya no se ubican solo en la recta real.
```

##### Si responde **"El conjunto de los irracionales"**

**Título del recuadro:**
```
⚠ Cuidado con la notación
```

**Retroalimentación de Katia:**
```
La i minúscula representa la unidad imaginaria.

No es lo mismo que la I que algunos materiales usan para hablar de irracionales.

En este nivel, los irracionales los pensamos como números que no pueden 
escribirse como fracción de enteros.
```

**Misconception tag registrado:** `confunde_i_imaginaria_con_I_irracionales`

##### Si responde **"Un número natural"** o **"El número cero"**

**Título del recuadro:**
```
⚠ No pertenece a esos conjuntos
```

**Retroalimentación de Katia:**
```
La unidad imaginaria i no es un número natural ni es el cero.

Es un nuevo tipo de número que permite construir números complejos.
```

---

#### 2.6 Forma general de un número complejo

**Título visible:**
```
¿Cómo se escribe un número complejo?
```

**Texto visible:**
```
Un número complejo se escribe así:

z = a + bi

donde:

a, b ∈ ℝ

La parte a se llama parte real.
La parte b se llama parte imaginaria.
```

**Ejemplo:**
```
3 + 2i

Parte real: 3
Parte imaginaria: 2
```

**Nota de Katia:**
```
La parte imaginaria es el número que acompaña a i. En 3 + 2i, la parte 
imaginaria es 2, no 2i.
```

---

#### 2.7 Interacción 2 — Parte real y parte imaginaria

**Pregunta visible:**
```
En el número complejo 3 + 2i, ¿cuál es la parte real y cuál es la parte 
imaginaria?
```

**Opciones de respuesta:**
- A. Parte real: 3. Parte imaginaria: 2.
- B. Parte real: 2. Parte imaginaria: 3.
- C. Parte real: 3. Parte imaginaria: 2i.
- D. Parte real: 0. Parte imaginaria: 3 + 2i.

**Respuesta esperada:** A

---

#### 2.8 Retroalimentación para Interacción 2

##### Si responde **A**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
En:

3 + 2i

la parte real es 3, y la parte imaginaria es 2.

El número completo es 3 + 2i.
```

##### Si responde **B**

**Título del recuadro:**
```
⚠ Revisa el orden
```

**Retroalimentación de Katia:**
```
En la forma:

a + bi

la parte real es a, y la parte imaginaria es b.

En 3 + 2i, a = 3 y b = 2.
```

**Misconception tag registrado:** `no_identifica_parte_real`

##### Si responde **C**

**Título del recuadro:**
```
⚠ Distingamos coeficiente y término
```

**Retroalimentación de Katia:**
```
El término imaginario es 2i, pero la parte imaginaria es el número que 
acompaña a i.

Por eso, en 3 + 2i, la parte imaginaria es 2.
```

**Misconception tag registrado:** `no_identifica_parte_imaginaria`

##### Si responde **D**

**Título del recuadro:**
```
⚠ El número completo no es la parte imaginaria
```

**Retroalimentación de Katia:**
```
3 + 2i es todo el número complejo.

Su parte real es 3 y su parte imaginaria es 2.
```

---

#### 2.9 Imaginario puro y complejo general

**Título visible:**
```
No todos los complejos se ven igual
```

**Texto visible:**
```
Un número como:

2i

es un imaginario puro, porque no tiene parte real visible.

También puede escribirse como:

0 + 2i

En cambio:

3 + 2i

tiene parte real 3 y parte imaginaria 2.

Por eso es un número complejo con parte real e imaginaria.
```

---

#### 2.10 Interacción 3 — Clasificar tipo de complejo

**Pregunta visible:**
```
¿Cuál de estos números es un imaginario puro?
```

**Opciones de respuesta:**
- 2i
- 3 + 2i
- 5
- √2

**Respuesta esperada:** 2i

---

#### 2.11 Retroalimentación para Interacción 3

##### Si responde **2i**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
2i es un imaginario puro porque su parte real es 0.

Podemos escribirlo así:

2i = 0 + 2i
```

##### Si responde **3 + 2i**

**Título del recuadro:**
```
⚠ Ese tiene parte real
```

**Retroalimentación de Katia:**
```
3 + 2i sí es complejo, pero no es imaginario puro porque tiene parte real 3.
```

##### Si responde **5** o **√2**

**Título del recuadro:**
```
⚠ Ese número es real
```

**Retroalimentación de Katia:**
```
5 y √2 son números reales.

También pueden verse como complejos con parte imaginaria cero:

5 = 5 + 0i

√2 = √2 + 0i

Pero no son imaginarios puros.
```

**Misconception tag registrado:** `no_reconoce_reales_como_complejos_con_imaginaria_cero`

---

#### 2.12 Visualización en el plano complejo

**Título visible:**
```
Del eje real al plano complejo
```

**Texto visible:**
```
Los números reales se ubican en una recta.

Los números complejos se representan en un plano con dos ejes:

- Eje horizontal: parte real.
- Eje vertical: parte imaginaria.

Por ejemplo, el número:

3 + 2i

se representa como el punto:

(3, 2)
```

**Diálogo de Katia:**
```
La parte real indica cuánto nos movemos horizontalmente.

La parte imaginaria indica cuánto nos movemos verticalmente.
```

---

#### 2.13 Interacción 4 — Ubicación en el plano

**Pregunta visible:**
```
¿Dónde se ubica el número 3 + 2i en el plano complejo?
```

**Opciones de respuesta:**
- En el punto (3, 2).
- En el punto (2, 3).
- En el punto (3, 0).
- En el punto (0, 2).

**Respuesta esperada:** En el punto (3, 2).

---

#### 2.14 Retroalimentación para Interacción 4

##### Si responde **(3, 2)**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
En 3 + 2i, la parte real es 3 y la parte imaginaria es 2.

Por eso se ubica en el punto:

(3, 2)
```

##### Si responde **(2, 3)**

**Título del recuadro:**
```
⚠ Revisa los ejes
```

**Retroalimentación de Katia:**
```
El eje horizontal representa la parte real y el eje vertical representa la 
parte imaginaria.

En 3 + 2i, la parte real es 3 y la parte imaginaria es 2.

Por eso el punto correcto es:

(3, 2)
```

**Misconception tag registrado:** `ubica_complejos_no_reales_en_recta_real`

##### Si responde **(3, 0)**

**Título del recuadro:**
```
⚠ Falta la parte imaginaria
```

**Retroalimentación de Katia:**
```
(3, 0) representaría el número 3 + 0i, es decir, el número real 3.

Pero 3 + 2i tiene parte imaginaria 2, así que se ubica en:

(3, 2)
```

##### Si responde **(0, 2)**

**Título del recuadro:**
```
⚠ Falta la parte real
```

**Retroalimentación de Katia:**
```
(0, 2) representaría el número 0 + 2i, es decir, 2i.

Pero 3 + 2i tiene parte real 3, así que se ubica en:

(3, 2)
```

---

#### 2.15 Relación con los reales

**Título visible:**
```
Los reales también caben dentro de los complejos
```

**Texto visible:**
```
Todo número real puede escribirse como complejo con parte imaginaria cero.

Ejemplos:

4 = 4 + 0i

−2 = −2 + 0i

√2 = √2 + 0i

Por eso:

ℝ ⊂ ℂ
```

**Diálogo de Katia:**
```
Esto no significa que todos los complejos sean reales.

Significa que los reales están incluidos dentro de los complejos.
```

---

#### 2.16 Formalización

**Título visible:**
```
¿Qué son los números complejos?
```

**Texto visible:**
```
Los números complejos son números que pueden escribirse en la forma:

a + bi

donde:

a, b ∈ ℝ

e

i² = −1

Se representan con la letra ℂ.
```

---

#### 2.17 Ejemplos y no ejemplos

**Título visible:**
```
Ejemplos de números complejos
```

**Texto visible:**
```
2i, 3 + 2i, −1 + 4i, 5, √2, 0
```

**Nota visible:**
```
Los números reales también son complejos, porque pueden escribirse con parte 
imaginaria cero.
```

**Título visible:**
```
Complejos no reales
```

**Texto visible:**
```
2i, 3 + 2i, −1 + 4i
```

**Nota de Katia:**
```
Es mejor no decir simplemente "los complejos son los imaginarios". Algunos 
complejos son imaginarios puros, otros tienen parte real e imaginaria, y los 
reales también están dentro de los complejos.
```

---

#### 2.18 Microactividad de cierre (Mini reto)

**Título visible:**
```
Mini reto
```

**Pregunta visible:**
```
Relaciona cada número con su descripción más precisa.
```

**Tipo de respuesta:** Emparejamiento (matching)

| Número | Descripción esperada |
|--------|---------------------|
| 5 | Real y complejo con parte imaginaria cero |
| 2i | Imaginario puro |
| 3 + 2i | Complejo con parte real e imaginaria |
| √2 | Irracional, real y complejo con parte imaginaria cero |
| −1 + 4i | Complejo con parte real e imaginaria |

---

#### 2.19 Retroalimentación para el mini reto

##### Si todo está correcto

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
Bien. Diferenciaste números reales, imaginarios puros y complejos con parte 
real e imaginaria.

Recuerda:

ℝ ⊂ ℂ
```

##### Si clasifica **2i** como real

**Título del recuadro:**
```
⚠ 2i no está en la recta real
```

**Retroalimentación de Katia:**
```
2i es un imaginario puro.

Se representa en el eje imaginario del plano complejo, no en la recta real.
```

**Misconception tag registrado:** `ubica_complejos_no_reales_en_recta_real`

##### Si clasifica **3 + 2i** como imaginario puro

**Título del recuadro:**
```
⚠ Tiene parte real
```

**Retroalimentación de Katia:**
```
3 + 2i no es imaginario puro porque tiene parte real 3.

Un imaginario puro tendría parte real cero, como:

2i = 0 + 2i
```

##### Si no reconoce **5** o **√2** como complejos

**Título del recuadro:**
```
⚠ Los reales también son complejos
```

**Retroalimentación de Katia:**
```
Todo número real puede verse como complejo con parte imaginaria cero.

Por ejemplo:

5 = 5 + 0i

√2 = √2 + 0i
```

**Misconception tag registrado:** `no_reconoce_reales_como_complejos_con_imaginaria_cero`

---

#### 2.20 Mensaje de transición

**Texto visible:**
```
Ya recorrimos los principales conjuntos numéricos de este nivel.
```

**Diálogo de Katia:**
```
Ahora vamos a practicar. Primero clasificaremos cada número en su conjunto 
más específico.
```

**Botón principal:**
```
Ir al clasificador
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B09-COMPLEJOS-PLANO.
- El nodo aparece en estado `actual` tras completar B08 (Reales) **solo si** `explored_complex_branch` está habilitado (banda Intermedio/Avanzado).
- Para banda Básico, este nodo aparece en estado `bloqueado-opcional` (visible pero no obligatorio) o se omite según configuración.
- Un hexágono de transición aparece **antes** del nodo:
  ```
  De la recta al plano
  ```

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. Aparece el título "Complejos: números en el plano".
2. Se ilumina el sexto peldaño de la escalera (ℂ).
3. Katia retoma la idea de recta real.
4. Aparece la pregunta sobre un número cuyo cuadrado sea −1.
5. Se introduce i² = −1.
6. Se muestra la forma general a + bi.
7. Se presenta el plano complejo.
8. Se activan las interacciones.

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante realiza esto **en orden secuencial:**

1. **Lee la pregunta detonadora** (¿qué número al cuadrado da −1?).
2. **Responde Interacción 1:** ¿Qué representa i? (opción única).
3. **Ve retroalimentación inmediata** (diferenciada).
4. **Lee la forma general** a + bi y el ejemplo 3 + 2i.
5. **Responde Interacción 2:** ¿Cuál es la parte real/imaginaria de 3 + 2i? (opción única A-D).
6. **Ve retroalimentación inmediata.**
7. **Lee la distinción** imaginario puro (2i) vs. complejo general (3 + 2i).
8. **Responde Interacción 3:** ¿Cuál es imaginario puro? (opción única).
9. **Ve retroalimentación inmediata.**
10. **Observa el plano complejo** (eje real horizontal, eje imaginario vertical).
11. **Responde Interacción 4:** ¿Dónde se ubica 3 + 2i? (opción única).
12. **Ve retroalimentación inmediata.**
13. **Lee la relación** ℝ ⊂ ℂ (reales como complejos con imaginaria cero).
14. **Lee la formalización** (definición de ℂ).
15. **Ve ejemplos y no ejemplos.**
16. **Realiza el mini reto:** Emparejar números con descripciones (matching).
17. **Ve retroalimentación del mini reto** (diferenciada).
18. **Lee el mensaje de transición.**
19. **Presiona "Ir al clasificador"** y el nodo se marca como completado.

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Presentación del conjunto** | ℂ, sexto peldaño, transición recta→plano | Desplazamiento | Sin interacción aún |
| **2 — Unidad imaginaria** | Pregunta detonadora, i² = −1 | Desplazamiento | Define i |
| **2b — Interacción 1** | "¿Qué representa i?" + 4 opciones | Botones seleccionables | El estudiante elige |
| **2c — Retroalimentación 1** | Resultado + Katia diferenciado | Botón "Siguiente" | Aclara i |
| **3 — Forma general** | z = a + bi, ejemplo 3 + 2i | Desplazamiento | Identifica partes |
| **3b — Interacción 2** | "¿Parte real/imaginaria?" + 4 opciones | Botones seleccionables | El estudiante elige |
| **3c — Retroalimentación 2** | Resultado + Katia | Botón "Siguiente" | Aclara partes |
| **4 — Imaginario puro** | Distinción 2i vs 3 + 2i | Desplazamiento | Diferencia tipos |
| **4b — Interacción 3** | "¿Cuál es imaginario puro?" + 4 opciones | Botones seleccionables | El estudiante elige |
| **4c — Retroalimentación 3** | Resultado + Katia | Botón "Siguiente" | Aclara imaginario puro |
| **5 — Plano complejo** | Plano con eje real y eje imaginario | Desplazamiento/interacción | Introduce el plano |
| **5b — Interacción 4** | "¿Dónde se ubica 3 + 2i?" + plano | Clic/selección en plano | El estudiante ubica |
| **5c — Retroalimentación 4** | Resultado + Katia | Botón "Siguiente" | Aclara la posición |
| **6 — Inclusión de reales** | ℝ ⊂ ℂ; 4 = 4 + 0i, etc. | Desplazamiento | Reales son complejos |
| **7 — Formalización** | Definición de ℂ, a + bi, i² = −1 | Desplazamiento | Formaliza el conjunto |
| **8 — Ejemplos y no ejemplos** | Complejos, complejos no reales, nota | Desplazamiento | Refuerza reconocimiento |
| **9a — Mini reto** | Emparejamiento número↔descripción | Drag/matching | El estudiante empareja |
| **9b — Retroalimentación del reto** | Resultado + Katia diferenciado | Botón "Continuar" | Cierra con refuerzo |
| **10 — Transición** | Mensaje + botón "Ir al clasificador" | Botón navegable | Prepara B10 |

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono de transición.
- **Katia aparece:** Slide-in lateral + 200ms delay.
- **Pregunta detonadora:** Aparición progresiva de 1² = 1, (−1)² = 1, luego la pregunta.
- **Plano complejo se dibuja:** Animación de los dos ejes (horizontal real, vertical imaginario).
- **Ubicación de punto:** Al ubicar 3 + 2i, se anima un movimiento horizontal (3) y luego vertical (2).
- **Inclusión ℝ ⊂ ℂ:** Animación que muestra la recta real como subconjunto del plano.
- **Formalización se destaca:** Recuadro con borde que brilla.
- **Mini reto:** Las parejas se conectan con líneas al emparejar.
- **Transición final:** El peldaño se marca como completado y el hexágono siguiente se ilumina.

---

#### 3.6 Relación con el mapa visual

**Nodo circular:** Representa la pantalla principal de complejos. Visualmente distinguido como **nodo de rama opcional** (color/borde diferente según el sistema de diseño).

**Punticos internos (eventos registrados):**
- Visualizó transición de recta a plano
- Visualizó unidad imaginaria
- Respondió pregunta sobre i
- Visualizó forma a + bi
- Identificó parte real e imaginaria
- Diferenció imaginario puro
- Visualizó plano complejo
- Ubicó un complejo en el plano
- Visualizó inclusión ℝ ⊂ ℂ
- Vio formalización
- Resolvió mini reto
- Vio retroalimentación
- Completó nodo

**Hexágono de transición (posterior):**
- Texto: "De aprender conjuntos a clasificarlos"
- Conecta hacia: PREALG-N1-B10-CLASIFICADOR-BASICO
- Se ilumina al completar B09.

---

### A4. Diferenciación por nivel (Intermedio / Avanzado)

> Este nodo **no se presenta a banda Básico**. La diferenciación aplica solo entre Intermedio y Avanzado.

| Aspecto | Intermedio | Avanzado |
|---|---|---|
| **Pregunta detonadora** | Guiada con pasos (1² = 1, (−1)² = 1, ¿y −1?) | Directa: "¿Existe x tal que x² = −1?" |
| **Forma general a + bi** | Ejemplo desarrollado (3 + 2i con partes etiquetadas) | Solo la forma general; el estudiante interpreta |
| **Plano complejo** | Interactivo con etiquetas en ambos ejes | Interactivo sin etiquetas |
| **Divulgación de formalización** | Colapsada inicialmente; puede expandir | Colapsada; "Expandir si necesitas" |
| **Intensidad del mini reto** | 5 emparejamientos estándar | Variante: incluye −3i, 1 − i, 0, etc. |
| **Pistas disponibles** | Medio | Mínimo |

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Evitar "los complejos son imaginarios"]**
Una decisión central de este nodo es **no reducir** los complejos a "números imaginarios". La narrativa insiste en que: (1) algunos complejos son imaginarios puros (2i), (2) otros tienen parte real e imaginaria (3 + 2i), y (3) los reales también son complejos (5 = 5 + 0i). Esto previene la misconception `cree_que_todo_complejo_es_imaginario` y prepara la inclusión ℝ ⊂ ℂ para el clasificador.

**[NOTA PEDAGÓGICA — Plano vs. recta]**
La transición conceptual clave es de **recta (1D) a plano (2D)**. La visualización del plano complejo con dos ejes (real horizontal, imaginario vertical) ancla esta idea espacialmente, corrigiendo la misconception de "ubicar complejos no reales en la recta real".

**[NOTA PEDAGÓGICA — Callejón opcional]**
Este nodo es deliberadamente **opcional y gateado por banda ELO**. La razón pedagógica: los complejos exceden el currículo estándar de octavo grado, pero ofrecen enriquecimiento valioso para estudiantes avanzados. Su carácter opcional evita sobrecargar a estudiantes de banda Básico que aún consolidan ℕ→ℝ. El flag `explored_complex_branch` permite que B10–B13 ajusten su contenido sin duplicar nodos.

---

### A6. Accesibilidad

- **Colores:** No dependen únicamente de rojo/verde; símbolos ✓ y ⚠.
- **Matemática:** Todas las expresiones (i² = −1, a + bi, 3 + 2i, ℂ, ℝ ⊂ ℂ, (3,2), etc.) con KaTeX y ARIA. Importante: leer "i al cuadrado igual a menos uno", "tres más dos i".
- **Plano complejo:** Descripción ARIA de ambos ejes y de la posición de cada punto.
- **Mini reto (matching):** Accesible por teclado; cada pareja anunciada.
- **Contraste:** Relación mínima 4.5:1.

---

### A7. Notas de citas pedagógicas

- **Ampliación conceptual de conjuntos numéricos:** Fischbein (1987) — la extensión de conjuntos numéricos genera conflictos cognitivos que deben gestionarse explícitamente.
- **Representación geométrica de complejos:** Wessel/Argand (representación en el plano) — el plano complejo como modelo mental.
- **Evitar "imaginario = irreal":** Nahin (1998), *An Imaginary Tale* — la nomenclatura "imaginario" induce la misconception de que estos números "no existen".
- **Enriquecimiento diferenciado:** Tomlinson (2001) — la instrucción diferenciada ofrece contenido avanzado opcional sin penalizar a quienes consolidan lo básico.

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo]
- [componente-pregunta-detonadora] — Para la pregunta sobre i² = −1
- [componente-pregunta-opcion-unica]
- [componente-plano-complejo] — Plano interactivo con eje real e imaginario
- [componente-ubicacion-en-plano] — Clic/selección de punto en el plano
- [componente-retroalimentacion-modal]
- [componente-mini-reto-emparejamiento] — Matching número↔descripción
- [componente-formalización-expandible]
- [componente-ejemplos-tarjetas]
- [componente-transicion-hexagono]
- [componente-nodo-opcional-badge] — Indicador visual de rama opcional

**Gating:**
- [flag-explored_complex_branch] — Controla visibilidad/desbloqueo del nodo
- El nodo debe respetar el estado de banda ELO al renderizarse

**Render bloqueante:**
- Verificar render de: i² = −1, a + bi, 3 + 2i, 2i, 0 + 2i, −1 + 4i, 5 + 0i, √2 + 0i, ℂ, ℝ ⊂ ℂ, (3,2), (2,3), (3,0), (0,2).
- Verificar símbolos: i, ², ⊂, ∈, ℝ, ℂ.
- **Crítico:** El plano complejo debe alinear correctamente los ejes y los puntos.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B09-COMPLEJOS-PLANO",
  "node_type": "concept_extension_with_complex_plane",
  "name": "Complejos: números en el plano",
  "position_in_route": "ruta_opcional_complejos",
  "is_optional_branch": true,
  "unlock_rule": "completed_node:PREALG-N1-B08-REALES-RECTA AND flag:explored_complex_branch",
  "gating": {
    "flag": "explored_complex_branch",
    "enabled_for_bands": ["intermedio", "avanzado"],
    "disabled_for_bands": ["basico"],
    "note": "Banda Básico avanza directamente B08 → B10 sin ver este nodo"
  },
  "previous_node_id": "PREALG-N1-B08-REALES-RECTA",
  "next_node_id": "PREALG-N1-B10-CLASIFICADOR-BASICO",
  "order": 9,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "affects_elo": false,
  "safe_zone": true,

  "mathematical_content": {
    "primary_set": "C",
    "definition": "Números de la forma a + bi donde a, b ∈ R e i² = −1",
    "convention": "C = { a + bi : a, b ∈ R, i² = −1 }",
    "imaginary_unit": "i² = −1",
    "general_form": "z = a + bi",
    "subset_relation": "R ⊂ C",
    "key_concepts": [
      "unidad_imaginaria",
      "parte_real",
      "parte_imaginaria",
      "imaginario_puro_vs_complejo_general",
      "plano_complejo",
      "reales_como_complejos"
    ]
  },

  "pedagogical_structure": {
    "phase_0_trigger": {
      "name": "Pregunta detonadora",
      "content": "1² = 1, (−1)² = 1, ¿existe número cuyo cuadrado sea −1? → se define i² = −1"
    },
    "phase_1_interactions": {
      "interactions": [
        {
          "interaction_id": "PREALG-N1-B09-Q01",
          "type": "single_choice",
          "question": "Si i² = −1, ¿qué representa la letra i?",
          "options": [
            {"value": "imaginary_unit", "label": "La unidad imaginaria."},
            {"value": "irrational_set", "label": "El conjunto de los irracionales."},
            {"value": "natural_number", "label": "Un número natural."},
            {"value": "zero", "label": "El número cero."}
          ],
          "expected_answer": "imaginary_unit",
          "micro_skill": "reconocer_unidad_imaginaria",
          "feedback": {
            "correct": "La letra i representa la unidad imaginaria.\nSe define por esta propiedad: i² = −1\nEsta idea permite construir números que ya no se ubican solo en la recta real.",
            "irrational_set": "La i minúscula representa la unidad imaginaria.\nNo es lo mismo que la I que algunos materiales usan para hablar de irracionales.\nEn este nivel, los irracionales los pensamos como números que no pueden escribirse como fracción de enteros.",
            "other": "La unidad imaginaria i no es un número natural ni es el cero.\nEs un nuevo tipo de número que permite construir números complejos."
          }
        },
        {
          "interaction_id": "PREALG-N1-B09-Q02",
          "type": "single_choice",
          "question": "En el número complejo 3 + 2i, ¿cuál es la parte real y cuál es la parte imaginaria?",
          "options": [
            {"value": "A", "label": "Parte real: 3. Parte imaginaria: 2."},
            {"value": "B", "label": "Parte real: 2. Parte imaginaria: 3."},
            {"value": "C", "label": "Parte real: 3. Parte imaginaria: 2i."},
            {"value": "D", "label": "Parte real: 0. Parte imaginaria: 3 + 2i."}
          ],
          "expected_answer": "A",
          "micro_skill": "identificar_parte_real_imaginaria",
          "feedback": {
            "correct": "En 3 + 2i, la parte real es 3, y la parte imaginaria es 2.\nEl número completo es 3 + 2i.",
            "B": "En la forma a + bi, la parte real es a, y la parte imaginaria es b.\nEn 3 + 2i, a = 3 y b = 2.",
            "C": "El término imaginario es 2i, pero la parte imaginaria es el número que acompaña a i.\nPor eso, en 3 + 2i, la parte imaginaria es 2.",
            "D": "3 + 2i es todo el número complejo.\nSu parte real es 3 y su parte imaginaria es 2."
          }
        },
        {
          "interaction_id": "PREALG-N1-B09-Q03",
          "type": "single_choice",
          "question": "¿Cuál de estos números es un imaginario puro?",
          "options": [
            {"value": "2i", "label": "2i"},
            {"value": "3+2i", "label": "3 + 2i"},
            {"value": "5", "label": "5"},
            {"value": "sqrt2", "label": "√2"}
          ],
          "expected_answer": "2i",
          "micro_skill": "diferenciar_imaginario_puro_y_complejo_general",
          "feedback": {
            "correct": "2i es un imaginario puro porque su parte real es 0.\nPodemos escribirlo así: 2i = 0 + 2i",
            "3+2i": "3 + 2i sí es complejo, pero no es imaginario puro porque tiene parte real 3.",
            "real": "5 y √2 son números reales.\nTambién pueden verse como complejos con parte imaginaria cero:\n5 = 5 + 0i\n√2 = √2 + 0i\nPero no son imaginarios puros."
          }
        },
        {
          "interaction_id": "PREALG-N1-B09-Q04",
          "type": "single_choice",
          "question": "¿Dónde se ubica el número 3 + 2i en el plano complejo?",
          "options": [
            {"value": "(3,2)", "label": "En el punto (3, 2)."},
            {"value": "(2,3)", "label": "En el punto (2, 3)."},
            {"value": "(3,0)", "label": "En el punto (3, 0)."},
            {"value": "(0,2)", "label": "En el punto (0, 2)."}
          ],
          "expected_answer": "(3,2)",
          "micro_skill": "ubicar_complejo_en_plano",
          "feedback": {
            "correct": "En 3 + 2i, la parte real es 3 y la parte imaginaria es 2.\nPor eso se ubica en el punto: (3, 2)",
            "(2,3)": "El eje horizontal representa la parte real y el eje vertical representa la parte imaginaria.\nEn 3 + 2i, la parte real es 3 y la parte imaginaria es 2.\nPor eso el punto correcto es: (3, 2)",
            "(3,0)": "(3, 0) representaría el número 3 + 0i, es decir, el número real 3.\nPero 3 + 2i tiene parte imaginaria 2, así que se ubica en: (3, 2)",
            "(0,2)": "(0, 2) representaría el número 0 + 2i, es decir, 2i.\nPero 3 + 2i tiene parte real 3, así que se ubica en: (3, 2)"
          }
        }
      ]
    },

    "phase_2_complex_plane": {
      "name": "Plano complejo",
      "type": "interactive_complex_plane",
      "axes": {
        "horizontal": "parte_real",
        "vertical": "parte_imaginaria"
      },
      "example_point": {"number": "3 + 2i", "coordinates": [3, 2]}
    },

    "phase_3_inclusion": {
      "name": "Inclusión de reales",
      "content": "Todo real es complejo con parte imaginaria cero",
      "examples": ["4 = 4 + 0i", "−2 = −2 + 0i", "√2 = √2 + 0i"],
      "relation": "R ⊂ C"
    },

    "phase_4_formalization": {
      "name": "Formalización",
      "title": "¿Qué son los números complejos?",
      "definition": "Los números complejos son números que pueden escribirse en la forma a + bi, donde a, b ∈ R e i² = −1.",
      "symbolic_representation": "C = { a + bi : a, b ∈ R, i² = −1 }",
      "expandable": true,
      "default_state_by_level": {
        "intermedio": "collapsed",
        "avanzado": "collapsed"
      }
    },

    "phase_5_examples": {
      "name": "Ejemplos y no ejemplos",
      "complex_examples": ["2i", "3 + 2i", "−1 + 4i", "5", "√2", "0"],
      "complex_non_real": ["2i", "3 + 2i", "−1 + 4i"],
      "educator_note": "Es mejor no decir simplemente 'los complejos son los imaginarios'. Algunos complejos son imaginarios puros, otros tienen parte real e imaginaria, y los reales también están dentro de los complejos."
    },

    "phase_6_mini_challenge": {
      "interaction_id": "PREALG-N1-B09-Q05",
      "name": "Mini reto",
      "type": "matching",
      "question": "Relaciona cada número con su descripción más precisa.",
      "pairs": [
        {"number": "5", "description": "Real y complejo con parte imaginaria cero"},
        {"number": "2i", "description": "Imaginario puro"},
        {"number": "3 + 2i", "description": "Complejo con parte real e imaginaria"},
        {"number": "√2", "description": "Irracional, real y complejo con parte imaginaria cero"},
        {"number": "−1 + 4i", "description": "Complejo con parte real e imaginaria"}
      ],
      "feedback_by_error_pattern": {
        "correct_all": {
          "title": "✓ Correcto",
          "body": "Bien. Diferenciaste números reales, imaginarios puros y complejos con parte real e imaginaria.\nRecuerda: R ⊂ C",
          "misconception_tag": null
        },
        "classified_2i_as_real": {
          "title": "⚠ 2i no está en la recta real",
          "body": "2i es un imaginario puro.\nSe representa en el eje imaginario del plano complejo, no en la recta real.",
          "misconception_tag": "ubica_complejos_no_reales_en_recta_real"
        },
        "classified_complex_as_pure_imaginary": {
          "title": "⚠ Tiene parte real",
          "body": "3 + 2i no es imaginario puro porque tiene parte real 3.\nUn imaginario puro tendría parte real cero, como: 2i = 0 + 2i",
          "misconception_tag": "cree_que_todo_complejo_es_imaginario"
        },
        "doesnt_recognize_real_as_complex": {
          "title": "⚠ Los reales también son complejos",
          "body": "Todo número real puede verse como complejo con parte imaginaria cero.\nPor ejemplo: 5 = 5 + 0i, √2 = √2 + 0i",
          "misconception_tag": "no_reconoce_reales_como_complejos_con_imaginaria_cero"
        }
      }
    }
  },

  "events_to_register": [
    "node_viewed",
    "imaginary_unit_viewed",
    "interaction_attempt:PREALG-N1-B09-Q01",
    "general_form_viewed",
    "interaction_attempt:PREALG-N1-B09-Q02",
    "pure_imaginary_viewed",
    "interaction_attempt:PREALG-N1-B09-Q03",
    "complex_plane_viewed",
    "interaction_attempt:PREALG-N1-B09-Q04",
    "inclusion_viewed",
    "formalization_viewed",
    "misconception_detected",
    "feedback_viewed",
    "mini_challenge_attempt:PREALG-N1-B09-Q05",
    "mini_challenge_result",
    "node_completed",
    "transition_initiated"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_COMPLEX_ALL_IMAGINARY",
      "level": "observation",
      "trigger": "Student treats all complex numbers as imaginary but corrects after feedback",
      "message_educator": "El estudiante inicialmente trató todos los complejos como imaginarios, pero corrigió después de la retroalimentación. Se recomienda observar si reaparece en clasificación."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_PLANE_LOCATION",
      "level": "reinforcement_suggested",
      "trigger": "Student fails to locate complex numbers in the plane two or more times",
      "message_educator": "El estudiante presenta dificultad recurrente para ubicar números complejos en el plano. Se recomienda reforzar la distinción eje real/imaginario."
    }
  ],

  "level_presentation": {
    "basico": {
      "visible": false,
      "note": "Banda Básico no ve este nodo; avanza B08 → B10"
    },
    "intermedio": {
      "trigger_question": "guided",
      "general_form": "worked_example",
      "complex_plane_labels": "all",
      "default_expanded": false,
      "hint_availability": "medio"
    },
    "avanzado": {
      "trigger_question": "direct",
      "general_form": "general_only",
      "complex_plane_labels": "minimal",
      "default_expanded": false,
      "hint_availability": "mínimo"
    }
  },

  "design_handoff": {
    "node_state": "bloqueado|actual|completado|bloqueado-opcional",
    "path_position": "ruta_opcional_complejos",
    "is_optional_branch": true,
    "gating_flag": "explored_complex_branch",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-pregunta-detonadora]",
      "[componente-pregunta-opcion-unica]",
      "[componente-plano-complejo]",
      "[componente-ubicacion-en-plano]",
      "[componente-retroalimentacion-modal]",
      "[componente-mini-reto-emparejamiento]",
      "[componente-formalización-expandible]",
      "[componente-ejemplos-tarjetas]",
      "[componente-transicion-hexagono]",
      "[componente-nodo-opcional-badge]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[color-nodo-opcional]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: i² = −1, a + bi, 3 + 2i, 2i, 0 + 2i, −1 + 4i, 5 + 0i, √2 + 0i, C, R ⊂ C, (3,2), (2,3), (3,0), (0,2); plano complejo con ejes alineados"
  }
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** de B09 (Complejos), con:
- ✅ Texto completo de Katia
- ✅ Pregunta detonadora (i² = −1)
- ✅ 5 interacciones (unidad imaginaria, partes, imaginario puro, ubicación en plano, mini reto)
- ✅ Visualización del plano complejo
- ✅ Inclusión ℝ ⊂ ℂ
- ✅ Storyboard detallado
- ✅ **Gating por banda ELO y flag `explored_complex_branch`** (callejón opcional)
- ✅ JSON técnico limpio

**Corrección de migración:** Se restauraron todas las expresiones matemáticas (i² = −1, a + bi, ℂ, ℝ ⊂ ℂ, coordenadas) que en el .docx original quedaron como corchetes vacíos.
