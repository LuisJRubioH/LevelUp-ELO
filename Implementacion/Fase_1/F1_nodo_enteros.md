# Nodo: Números enteros — deudas y saldos
**ID:** PREALG-N1-B05-ENTEROS-DEUDA

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B05-ENTEROS-DEUDA |
| **Título visible** | Enteros: deudas y saldos |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular principal de contenido conceptual |
| **Ubicación en la ruta** | Segundo nodo numérico; se desbloquea tras completar B04 (Naturales) |
| **Función pedagógica** | Introducir ℤ como ampliación de ℕ para representar situaciones con valores opuestos (deudas, saldos, temperaturas bajo cero, desplazamientos) |
| **Objetivo de aprendizaje** | El estudiante reconoce que ℤ permite representar cantidades positivas, cero y cantidades negativas, especialmente en contextos de deuda/saldo |
| **Microhabilidades** | • Reconocer deudas como números negativos<br>• Interpretar cero como punto de equilibrio<br>• Diferenciar deuda de saldo a favor<br>• Calcular deuda total y saldo después de abono<br>• Ubicar valores en recta numérica<br>• Comparar enteros (−5 < −1 en la recta) |
| **Misconception tags** | confunde_deuda_con_cantidad_positiva<br>no_reconoce_numero_negativo<br>interpreta_negativos_por_valor_absoluto<br>no_reconoce_cero_como_equilibrio<br>confunde_abono_con_aumento_de_deuda<br>confunde_saldo_a_favor_con_deuda |
| **Referencias de refuerzo** | PREALG-N1-B02-PREGUNTA-DETONADORA<br>PREALG-N1-B03-ESCALERA-NECESIDAD<br>PREALG-N1-B04-NATURALES-CONTAR<br>PREALG-N1-B10-CLASIFICADOR-BASICO<br>PREALG-N1-B11-CLASIFICADOR-RIGUROSO |

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
Enteros: deudas y saldos
```

**Subtítulo:**
```
Cuando necesitamos representar cantidades por debajo de cero, los naturales ya no alcanzan.
```

---

#### 2.2 Diálogo inicial de Katia

**Contexto visual:** Katia aparece junto al segundo peldaño de la escalera.

**Diálogo de Katia:**
```
Con los números naturales podemos contar cantidades completas: 0, 1, 2, 3, 4…

Pero hay situaciones en las que necesitamos representar algo más: deudas, 
temperaturas bajo cero, pisos subterráneos o pérdidas.

Para eso aparecen los números enteros.

Los enteros incluyen los naturales, el cero y los números negativos.
```

---

#### 2.3 Apertura narrativa corregida — antes de practicar

**Texto visible:**
```
Antes de resolver cuentas, detengámonos un momento.

En el primer peldaño usamos los números naturales para contar cosas completas:
0 lápices, 1 cuaderno, 2 estudiantes, 3 bolsas.

Pero Katia mira la escalera y nota algo extraño.

Si los naturales sirven para contar lo que hay, ¿qué número usamos para decir
que algo falta?

Por ejemplo, si una persona debe dinero, no basta con decir "5.000".

Ese 5.000 no representa dinero disponible.

Representa una falta, una deuda, una cantidad que todavía está pendiente.

Katia pregunta:
"Si el cero significa estar en equilibrio, ¿cómo marcamos que estamos por
debajo de ese equilibrio?"

Esa pregunta es la puerta de entrada a los números enteros.

Los enteros nacen cuando necesitamos hablar de cantidades completas en dos
direcciones:

cantidades a favor,

el punto de equilibrio,

y cantidades en contra.
```

---

#### 2.4 Descubrimiento guiado — de la necesidad al símbolo

**Texto visible:**
```
Pensemos primero en una cuenta sencilla.

Si tienes $8.000 y compras algo de $3.000, todavía te quedan $5.000.

Ese resultado es positivo porque sigues teniendo dinero disponible.

Ahora cambiemos la situación.

Si tienes $3.000 y compras algo de $8.000 fiado, ya no basta con decir
"me faltan 5.000".

Matemáticamente necesitamos registrar que quedaste $5.000 por debajo de cero.

Katia dibuja una recta:

a la derecha del 0 coloca lo que tienes a favor;

en el 0 coloca el equilibrio;

a la izquierda del 0 coloca lo que debes o lo que falta.

Entonces una deuda de $5.000 se representa como −5.000.

Observa otro caso.

Una temperatura de 4 °C está por encima de cero.

Una temperatura de −4 °C está por debajo de cero.

El número 4 y el número −4 tienen la misma distancia al cero,
pero no significan lo mismo.

4 está a la derecha del 0.

−4 está a la izquierda del 0.

Ese contraste es la idea clave:
el signo indica el lado del equilibrio.

Contraejemplo importante:

−3.5 no es un entero, aunque sea negativo,
porque tiene parte decimal.

1/2 tampoco es entero,
porque representa media unidad.

Los enteros sí pueden ser negativos,
pero siguen representando cantidades completas.

Entonces, ¿qué hace especial a los números enteros?

Que permiten representar cantidades completas positivas,
el cero,
y cantidades completas negativas en una misma recta.
```

---

#### 2.5 Definición formal integrada + ejemplos base

**Introducción visible:**
```
Ya vimos la necesidad: los naturales no alcanzan cuando queremos representar
deudas, pérdidas, temperaturas bajo cero o desplazamientos hacia la izquierda.

Por eso ampliamos el conjunto.
```

**Definición formal en KaTeX:**

$$\mathbb{Z}=\{\ldots,-3,-2,-1,0,1,2,3,\ldots\}$$

**Texto visible:**
```
Los números enteros son los números que representan cantidades completas
positivas, el cero y cantidades completas negativas.

El símbolo Z se lee "enteros".

En esta recta, el 0 es el punto de equilibrio.

Los números positivos quedan a la derecha.

Los números negativos quedan a la izquierda.

Katia lo resume así:
"Un entero no solo dice cuánto hay; también puede decir de qué lado del cero
está la situación."
```

##### Ejemplo 1 (básico) — deuda simple

**Enunciado:**
```
Laura debe $4.000 en la tienda escolar.
Representa esa deuda con un número entero.
```

**Solución paso a paso:**
```
Paso 1. Identificamos el punto de equilibrio: no deber nada es 0.

Paso 2. Como Laura debe dinero, la situación está por debajo de 0.

Paso 3. La cantidad completa pendiente es 4.000.

Paso 4. Escribimos el signo negativo para indicar deuda.

Resultado:

−4.000

Entonces, una deuda de $4.000 se representa con el entero −4.000.
```

##### Ejemplo 2 (intermedio) — abono hacia el equilibrio

**Enunciado:**
```
Mateo debía $12.000 y abonó $7.000.
¿Qué entero representa su saldo después del abono?
```

**Solución paso a paso:**
```
Paso 1. La deuda inicial está por debajo de cero:

−12.000

Paso 2. Abonar significa moverse hacia la derecha en la recta,
porque la deuda disminuye.

Paso 3. Restamos la cantidad abonada a la deuda:

12.000 − 7.000 = 5.000

Paso 4. Todavía queda una deuda, así que el saldo sigue siendo negativo.

Resultado:

−5.000

Entonces, después del abono, Mateo todavía está $5.000 por debajo del equilibrio.
```

##### Ejemplo 3 (trampa común) — negativo no significa "no entero"

**Enunciado:**
```
Decide cuáles son enteros: −6, 0, 2.5, 1/3, 9.
```

**Solución paso a paso:**
```
−6 sí es entero porque es una cantidad completa negativa.

0 sí es entero porque representa el equilibrio.

2.5 no es entero porque tiene parte decimal.

1/3 no es entero porque representa una parte de unidad.

9 sí es entero porque es una cantidad completa positiva.

Katia advierte:
"El signo negativo no saca a un número del conjunto de los enteros.
Lo que lo saca es tener parte decimal o fraccionaria."
```

**Transición hacia la práctica:**
```
Ahora sí vamos a usar esta idea en una situación real.

Primero calcularemos cantidades completas.

Luego interpretaremos si el resultado queda a favor, en cero o como deuda.
```

---

#### 2.6 Situación problema

**Título visible:**
```
Situación: cuenta en la tienda escolar
```

**Texto visible:**
```
Un estudiante acuerda con el tendero de su colegio que puede pedir productos 
durante el mes y pagarlos al final.

Durante cuatro semanas pidió lo siguiente:
```

**Tabla de compras:**

| Semana | Compra | Valor |
|--------|--------|-------|
| Semana 1 | Arepa y jugo | $10.000 |
| Semana 2 | Empanadas y agua | $7.000 |
| Semana 3 | Almuerzos acumulados | $14.000 |
| Semana 4 | Galletas y bebida | $4.000 |

**Texto visible (continuación):**
```
Al final del mes, sus padres le dan $30.000 para pagar la cuenta.
```

**Preguntas guía:**
1. ¿Cuánto pidió en total durante el mes?
2. Después de abonar $30.000, ¿cuánto queda debiendo?
3. ¿Cómo podemos representar esa deuda usando números enteros?

---

#### 2.7 Interacción 1 — Deuda total

**Pregunta visible:**
```
¿Cuánto pidió en total durante el mes?
```

**Tipo de respuesta:** Entrada numérica  
**Respuesta esperada:** 35000 (porque 10000 + 7000 + 14000 + 4000 = 35000)

---

#### 2.8 Retroalimentación para Interacción 1

##### Si responde **35000**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
El estudiante pidió productos por un total de $35.000.

10.000 + 7.000 + 14.000 + 4.000 = 35.000
```

##### Si responde **otro valor**

**Título del recuadro:**
```
Revisemos la suma
```

**Retroalimentación de Katia:**
```
Para saber cuánto debe antes de pagar, sumamos todas las compras del mes:

10.000 + 7.000 + 14.000 + 4.000 = 35.000

La deuda total inicial es de $35.000.
```

---

#### 2.9 Interacción 2 — Saldo después del abono

**Pregunta visible:**
```
Si la deuda total es de $35.000 y abona $30.000, ¿cuánto queda debiendo?
```

**Tipo de respuesta:** Entrada numérica  
**Respuesta esperada:** 5000 (porque 35000 − 30000 = 5000)

---

#### 2.10 Retroalimentación para Interacción 2

##### Si responde **5000**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
Después de abonar $30.000, todavía queda debiendo $5.000.

35.000 − 30.000 = 5.000
```

##### Si responde **otro valor**

**Título del recuadro:**
```
Comparemos deuda y abono
```

**Retroalimentación de Katia:**
```
La deuda total era de $35.000 y el abono fue de $30.000.

Para saber cuánto falta por pagar, restamos:

35.000 − 30.000 = 5.000

Todavía queda una deuda de $5.000.
```

---

#### 2.11 Interacción 3 — Representación con entero

**Pregunta visible:**
```
Si todavía debe $5.000, ¿cómo podemos representar esa deuda 
usando números enteros?
```

**Opciones de respuesta:**
- 5.000
- −5.000
- 0

**Respuesta esperada:** −5.000

---

#### 2.12 Retroalimentación para Interacción 3

##### Si responde **−5.000**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
La deuda se representa como un valor negativo porque está por debajo 
del punto de equilibrio.

Si el punto de equilibrio es no deber nada, entonces:

deuda de 5.000 = −5.000
```

##### Si responde **5.000**

**Título del recuadro:**
```
⚠ Cuidado con el significado
```

**Retroalimentación de Katia:**
```
5.000 puede representar una cantidad positiva, pero aquí no significa que 
el estudiante tenga $5.000 disponibles.

Como todavía debe $5.000, lo representamos como:

−5.000
```

**Misconception tag registrado:** `confunde_deuda_con_cantidad_positiva`

##### Si responde **0**

**Título del recuadro:**
```
⚠ El cero significa equilibrio
```

**Retroalimentación de Katia:**
```
0 representaría que el estudiante no debe nada y tampoco tiene saldo a favor.

Pero en este caso todavía debe $5.000. Por eso lo representamos como:

−5.000
```

**Misconception tag registrado:** `no_reconoce_cero_como_equilibrio`

---

#### 2.13 Visualización en recta numérica

**Título visible:**
```
La recta numérica
```

**Texto visible:**
```
Los números enteros se pueden ubicar en una recta numérica.

A la izquierda del cero están los números negativos.
En el centro está el cero.
A la derecha están los números positivos.

…, −3, −2, −1, 0, 1, 2, 3, …
```

**Diálogo de Katia:**
```
Mientras más a la derecha esté un número, mayor es.

Por eso:

−1 > −5

Porque −1 está más a la derecha que −5.
```

---

#### 2.14 Interacción 4 — Ubicación en recta numérica

**Pregunta visible:**
```
¿Dónde deberías ubicar −5.000 en la recta numérica?
```

**Tipo de respuesta:** Drag-and-drop o clic en posición  
**Respuesta esperada:** Posición correcta de −5.000 (a la izquierda del 0)

**Nota adicional:** Se muestra una animación que desplaza el saldo desde −35.000 hacia −5.000 cuando se "abona", mostrando cómo el número se acerca a 0.

---

#### 2.15 Retroalimentación para Interacción 4

##### Si ubica **correctamente**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
Excelente. −5.000 está a la izquierda del 0 porque representa una deuda.

Cuando abonamos, el saldo se desplaza hacia la derecha, acercándose a 0.
```

##### Si ubica **incorrectamente** (ej. a la derecha de 0)

**Título del recuadro:**
```
⚠ Revisa la posición
```

**Retroalimentación de Katia:**
```
Los números negativos están a la izquierda del 0, no a la derecha.

−5.000 representa una deuda (algo que falta), por eso va a la izquierda 
del punto de equilibrio (0).
```

**Misconception tag registrado:** `interpreta_negativos_por_valor_absoluto`

---

#### 2.16 Formalización de consolidación

**Título visible:**
```
¿Qué son los números enteros?
```

**Texto visible:**
```
Los números enteros son los números que usamos para representar cantidades 
positivas, cero y cantidades negativas.

Los enteros incluyen todos los naturales, el cero y los números negativos.

En este nivel usaremos:

Z = {…, −3, −2, −1, 0, 1, 2, 3, …}

El cero es el punto de equilibrio. A la izquierda del cero están las deudas, 
pérdidas o valores bajo cero. A la derecha están las ganancias o valores 
positivos.
```

---

#### 2.17 Ejemplos y no ejemplos

**Título visible:**
```
Ejemplos
```

**Texto visible:**
```
Son números enteros:

−10, −5, −1, 0, 1, 5, 10, 100
```

**Título visible:**
```
No son números enteros:
```

**Texto visible:**
```
−3.5, −1/2, 0.75, 1/3, 2.5
```

**Nota de Katia:**
```
Los enteros representan cantidades completas. Cuando necesitemos partes o 
divisiones, vamos a usar otro conjunto llamado números racionales.
```

---

#### 2.18 Microactividad de cierre (Mini reto)

**Título visible:**
```
Mini reto
```

**Pregunta visible:**
```
Selecciona todos los números enteros según la definición de este nivel.
```

**Opciones (checkboxes; respuesta múltiple):**
- [ ] −8
- [ ] −3.5
- [ ] 0
- [ ] 1/2
- [ ] 6
- [ ] −2.1

**Respuestas esperadas:**
- [x] −8
- [x] 0
- [x] 6

---

#### 2.19 Retroalimentación para el mini reto

##### Si selecciona exactamente **{−8, 0, 6}**

**Título del recuadro:**
```
✓ Bien
```

**Retroalimentación de Katia:**
```
Correcto. En este nivel, −8, 0 y 6 son enteros.

Los enteros representan cantidades completas, positivas, cero o negativas.
```

---

##### Si omite el **0** (selecciona solo {−8, 6})

**Título del recuadro:**
```
⚠ Atención al cero
```

**Retroalimentación de Katia:**
```
El 0 también es un número entero. Representa el punto de equilibrio, 
el punto entre deudas y ganancias.
```

**Misconception tag registrado:** `no_reconoce_cero_como_equilibrio`

---

##### Si selecciona **−3.5** (decimal negativo)

**Título del recuadro:**
```
⚠ Cuidado con los decimales
```

**Retroalimentación de Katia:**
```
−3.5 es un número negativo, pero no es entero porque tiene una parte decimal.

Los enteros representan cantidades completas, sin partes fraccionarias.

Cuando necesitemos representar partes (como −3.5), usaremos otro conjunto 
llamado números racionales.
```

**Misconception tag registrado:** `confunde_deuda_con_cantidad_positiva` o `incluye_no_enteros_en_enteros`

---

##### Si selecciona **1/2** (fracción)

**Título del recuadro:**
```
⚠ Cuidado con las fracciones
```

**Retroalimentación de Katia:**
```
1/2 es una fracción, no un número entero. Representa una parte (media) de 
algo, no una cantidad completa.

Los enteros representan cantidades completas, positivas, cero o negativas.
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B05-ENTEROS-DEUDA.
- El nodo aparece en estado `actual` tras completar B04 (Naturales).
- Un hexágono de transición conceptual aparece **antes** del nodo:
  ```
  Representar deudas y saldos
  ```

**Pantalla:** Se muestra el título y subtítulo en la parte superior.

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. **El título y subtítulo se iluminan.**
2. **Katia aparece lateralmente**, señalando el segundo peldaño de la escalera (que se ilumina).
3. **Diálogo de Katia se muestra de forma progresiva** (párrafo por párrafo).
4. **La situación problema aparece:** título "Situación: cuenta en la tienda escolar" seguido de la narrativa y la tabla de compras.
5. **La tabla de compras aparece** con las 4 semanas y sus valores.
6. **El texto del abono inicial aparece.**

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante realiza esto **en orden secuencial:**

1. **Lee la situación** de la tienda escolar (compras por semana, abono al final).
2. **Responde Interacción 1:** ¿Cuánto pidió en total? (entrada numérica)
   - El campo se activa.
   - El estudiante escribe su respuesta.
   - Presiona "Revisar".
3. **Ve retroalimentación inmediata** de Katia.
4. **Responde Interacción 2:** ¿Cuánto queda debiendo? (entrada numérica)
   - El campo se activa.
5. **Ve retroalimentación inmediata.**
6. **Responde Interacción 3:** ¿Cómo representamos la deuda? (opción única)
   - Tres opciones aparecen.
   - El estudiante selecciona.
7. **Ve retroalimentación inmediata** (diferenciada según respuesta).
8. **Se muestra la recta numérica** con valores negativos, cero y positivos.
9. **Lee el diálogo de Katia** sobre la recta (−1 > −5).
10. **Responde Interacción 4:** Ubica −5.000 en la recta (drag-and-drop o clic)
    - Se muestra una animación que desplaza un saldo desde −35.000 a −5.000.
    - El estudiante coloca el número.
11. **Ve retroalimentación inmediata.**
12. **Lee la formalización:** "¿Qué son los números enteros?" (expandible o visible).
13. **Ve ejemplos y no ejemplos** con nota de Katia.
14. **Realiza el mini reto:** Seleccionar los números enteros (checkboxes).
    - Se activan 6 opciones.
    - El estudiante selecciona.
    - Presiona "Revisar selección".
15. **Ve retroalimentación del mini reto** (diferenciada).
16. **Un botón "Continuar" o "Ir a Racionales" aparece** en la parte inferior.
17. **Presiona el botón y el nodo se marca como completado.**

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Presentación del conjunto** | Título, subtítulo, Katia, escalera | Desplazamiento para leer | No hay interacción aún |
| **2 — Situación problema** | Tienda escolar, tabla de compras, abono inicial | Desplazamiento para leer | Prepara el contexto |
| **3a — Interacción 1** | Pregunta "¿Cuánto pidió en total?" + campo | Campo de entrada numérica | El estudiante responde |
| **3b — Retroalimentación 1** | Respuesta + Diálogo de Katia | Botón "Siguiente" | Aclara el cálculo |
| **4a — Interacción 2** | Pregunta "¿Cuánto queda debiendo?" + campo | Campo de entrada numérica | El estudiante responde |
| **4b — Retroalimentación 2** | Respuesta + Diálogo de Katia | Botón "Siguiente" | Aclara el saldo restante |
| **5a — Interacción 3** | Pregunta "¿Cómo representamos?" + 3 opciones | Botones seleccionables | El estudiante elige |
| **5b — Retroalimentación 3** | Respuesta + Diálogo de Katia diferenciado | Botón "Siguiente" | Aclara el significado del negativo |
| **6 — Recta numérica** | Recta completa con negativos, cero, positivos | Desplazamiento para leer | Introduce la representación visual |
| **6b — Diálogo de Katia sobre recta** | "Mientras más a la derecha..." + comparación | Desplazamiento | Refuerza orden en la recta |
| **7a — Interacción 4** | Pregunta "¿Dónde ubicar −5.000?" + recta visual | Drag-and-drop o clic en posición | El estudiante ubica el número |
| **7b — Animación** | Saldo se desplaza de −35.000 a −5.000 | Animación automática | Visualiza el abono |
| **7c — Retroalimentación 4** | Resultado + Diálogo de Katia | Botón "Siguiente" | Aclara la posición |
| **8 — Formalización** | Definición de Z, conjunto simbólico, significado del cero | Desplazamiento para leer | Formaliza lo aprendido |
| **9 — Ejemplos y no ejemplos** | Ejemplos válidos, no ejemplos, nota de Katia | Desplazamiento para leer | Refuerza el reconocimiento |
| **10a — Mini reto** | Pregunta + 6 checkboxes (−8, −3.5, 0, 1/2, 6, −2.1) | Checkboxes seleccionables | El estudiante selecciona |
| **10b — Retroalimentación del reto** | Resultado + Diálogo de Katia diferenciado | Botón "Continuar" | Cierra con refuerzo |
| **11 — Transición** | Hexágono "De deudas a repartos" + botón "Ir a Racionales" | Botón navegable | Prepara el siguiente nodo |

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono de transición.
- **Katia aparece:** Slide-in lateral + 200ms delay.
- **Tabla de compras aparece:** Fade-in + animación de filas (stagger).
- **Situación se ilumina:** Glow sutil alrededor de la tabla.
- **Interacciones aparecen:** Cada pregunta entra con fade-in secuencial.
- **Retroalimentación:** Slide-down suave con cambio de color (verde/ámbar según corrección).
- **Recta numérica aparece:** Fade-in + línea se dibuja de izquierda a derecha.
- **Saldo en recta se desplaza:** Animación suave de −35.000 → −5.000 cuando se "abona".
- **Números en recta se iluminan:** Al colocar −5.000, se destaca su posición.
- **Formalización se destaca:** Recuadro con borde sutil que brilla.
- **Mini reto aparece:** Checkboxes se iluminan al hover.
- **Transición final:** El peldaño se marca como completado (checkmark + glow) y el hexágono siguiente se ilumina.

---

#### 3.6 Relación con el mapa visual

**Nodo circular:**
- Representa esta pantalla principal (B05 Enteros).
- Estado: `actual` (durante el recorrido) → `completado` (al terminar).

**Punticos internos (eventos registrados):**
- Punto: Situación visualizada
- Punto: Pregunta 1 respondida
- Punto: Retroalimentación 1 vista
- Punto: Pregunta 2 respondida
- Punto: Retroalimentación 2 vista
- Punto: Pregunta 3 respondida
- Punto: Retroalimentación 3 vista
- Punto: Recta numérica interactuada
- Punto: Mini reto realizado
- Punto: Nodo completado

**Hexágono de transición (posterior):**
- Texto: "De deudas a repartos"
- Conecta hacia: PREALG-N1-B06-RACIONALES-REPARTO
- Se ilumina al completar B05.

---

### A4. Diferenciación por nivel (Básico / Intermedio / Avanzado)

| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| **Ejemplo resuelto en situación** | Completo: se muestran sumas y restas paso a paso | Parcialmente guiado: tabla visible, estudiante suma | Mínimo: solo tabla, estudiante calcula |
| **Divulgación de formalización** | Expandida por defecto | Colapsada inicialmente; puede expandir | Colapsada; se sugiere "Expandir si necesitas" |
| **Visualización de recta** | Siempre visible con color/etiquetas | Visible pero sin etiquetas de cada número | Solo la estructura básica (− 0 +) |
| **Intensidad del mini reto** | 6 opciones simples (−8, −3.5, 0, 1/2, 6, −2.1) | 6 opciones simples | Variante: incluye −2, 3/4, −0.5, etc. |
| **Pistas disponibles** | Máximo: "Lee la formalización", "Mira ejemplos" | Medio: "Lee la formalización" | Mínimo: ninguna, solo feedback |
| **Estado por defecto de expansión** | Expandido | Parcialmente expandido | Colapsado |

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Cero como punto de equilibrio]**
El cero no es meramente un número más; es el punto de referencia respecto al cual se definen deudas (negativo) y ganancias (positivo). Esta conceptualización evita que estudiantes interpreten −5 como "mayor" que −1 por el valor absoluto.

**[NOTA PEDAGÓGICA — Recta numérica como herramienta]**
La recta numérica cumple tres funciones: (1) ubicación espacial de enteros, (2) comparación entre enteros (mayor a la derecha), (3) visualización de operaciones (abono desplaza el saldo hacia la derecha). La animación de desplazamiento refuerza especialmente que "pagar una deuda" acerca el saldo a cero.

**[NOTA PEDAGÓGICA — Contexto de deuda/saldo]**
El contexto de la tienda escolar es cercano a estudiantes de octavo grado. A diferencia de "dinero ganado/gastado" (que puede ser abstracto), la deuda es una experiencia concreta: "debo dinero" es una experiencia real. Esto facilita la transferencia conceptual a otros contextos (temperaturas bajo cero, pisos subterráneos).

---

### A6. Accesibilidad

- **Colores:** No dependen únicamente de rojo/verde; se usan símbolos ✓ y ⚠.
- **Tabla:** Headers semánticos, aria-labels en cada celda.
- **Matemática:** Todas las expresiones (10000 + 7000, −5.000, Z = {...}, etc.) se renderizan con KaTeX y tienen ARIA.
- **Recta numérica:** Descripciones ARIA para cada sección (negativos, cero, positivos); valores etiquetados.
- **Contraste:** Fondos claros, texto oscuro (o viceversa en modo oscuro); relación mínima 4.5:1.
- **Lectura de pantalla:** Diálogos de Katia como texto; números y símbolos anunciados correctamente.

---

### A7. Notas de citas pedagógicas

- **Concepto de deuda como número negativo:** Piaget (1965) — los números negativos requieren abstracción de un referente (no hay "-5 objetos").
- **Recta numérica como modelo mental:** Van Hiele (1986) — la representación visual apoya la transición de lo concreto a lo abstracto.
- **Retroalimentación específica:** Hattie & Timperley (2007) — la retroalimentación efectiva aclara qué fue el error y cómo corregirlo.
- **Zona segura (sin penalización):** Dweck (2006) — los errores son información, no fracasos.

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo] — Recuadro lateral con personaje Katia
- [componente-tabla-compras] — Tabla con filas animadas
- [componente-pregunta-entrada-numerica] — Campo de entrada con validación
- [componente-pregunta-opcion-unica] — Botones de selección
- [componente-pregunta-checkboxes] — Múltiple selección
- [componente-retroalimentacion-modal] — Feedback diferenciado
- [componente-recta-numerica] — Recta con animación de desplazamiento
- [componente-ubicacion-en-recta] — Drag-and-drop o clic en recta
- [componente-formalización-expandible] — Texto que puede colapsar/expandir
- [componente-ejemplos-tarjetas] — Tarjetas para ejemplos y no ejemplos
- [componente-transicion-hexagono] — Hexágono del mapa

**Tokens del sistema de diseño:**
- Acentos: morado (primario), teal (secundario)
- Tipografía: sans-serif para body, serif para títulos
- Espaciado: usar variables CSS del proyecto
- Animaciones: Framer Motion con easing suave

**Render bloqueante:**
- Verificar que 10000, 7000, 14000, 4000, 35000, 30000, 5000, −5000, −8, −3.5, 0, 1/2, 6, −2.1 se renderizan correctamente.
- Verificar símbolos ∈, Z, ℤ, +, −, > se muestran correctamente.
- Verificar que la recta numérica con negativos/cero/positivos se alinea visualmente.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B05-ENTEROS-DEUDA",
  "node_type": "conceptual_content_with_formative_interaction",
  "name": "Enteros: deudas y saldos",
  "position_in_route": "ruta_nucleo_second_numeric_set",
  "unlock_rule": "completed_node:PREALG-N1-B04-NATURALES-CONTAR",
  "unlock_after": 0,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "affects_elo": false,
  "safe_zone": true,

  "mathematical_content": {
    "primary_set": "Z",
    "definition": "Números que representan cantidades completas, positivas, cero y negativas",
    "convention": "Z = {…, −3, −2, −1, 0, 1, 2, 3, …}",
    "convention_note": "Cero como punto de equilibrio; negativos representan deudas/pérdidas",
    "cardinality": "countably infinite",
    "order_type": "total_order",
    "reference_point": "zero_as_equilibrium"
  },

  "pedagogical_structure": {
    "phase_0_narrative_integrated_definition": {
      "type": "narrative_with_integrated_definition",
      "name": "Apertura narrativa, descubrimiento guiado y definición integrada",
      "position": "before_interactive_practice",
      "is_integrated": true,
      "sections": [
        {
          "type": "prose",
          "name": "Apertura narrativa corregida",
          "content_summary": "Katia plantea la necesidad de representar cantidades por debajo del cero: deudas, pérdidas y faltantes."
        },
        {
          "type": "guided_discovery",
          "name": "De la necesidad al símbolo",
          "content_summary": "Contrasta dinero disponible, deuda, temperaturas positivas/negativas y no ejemplos decimales/fraccionarios."
        },
        {
          "type": "definition_plus_examples",
          "definition_katex": "\\mathbb{Z}=\\{\\ldots,-3,-2,-1,0,1,2,3,\\ldots\\}",
          "is_integrated": true,
          "examples": [
            {
              "name": "Ejemplo 1 (básico) — deuda simple",
              "steps": [
                "Identificar 0 como equilibrio.",
                "Reconocer que una deuda está por debajo de 0.",
                "Conservar la cantidad completa.",
                "Usar signo negativo: −4.000."
              ]
            },
            {
              "name": "Ejemplo 2 (intermedio) — abono hacia el equilibrio",
              "steps": [
                "Partir de −12.000.",
                "Interpretar el abono como movimiento hacia la derecha.",
                "Calcular 12.000 − 7.000 = 5.000.",
                "Mantener signo negativo porque todavía queda deuda: −5.000."
              ]
            },
            {
              "name": "Ejemplo 3 (trampa común)",
              "steps": [
                "Aceptar −6, 0 y 9 como enteros.",
                "Rechazar 2.5 y 1/3 por no representar unidades completas."
              ]
            }
          ]
        }
      ],
      "transition_to_practice": "Ahora se usa la definición integrada para resolver una situación real de deuda en la tienda escolar."
    },

    "phase_1_concrete": {
      "name": "Situación problema",
      "content": "Contexto de tienda escolar con compras semanales y abono final",
      "interactions": [
        {
          "interaction_id": "I1_deuda_total",
          "type": "numeric_input",
          "question": "¿Cuánto pidió en total durante el mes?",
          "expected_answer": 35000,
          "misconceptions_detected": [],
          "feedback": {
            "correct": "El estudiante pidió productos por un total de $35.000.\n10.000 + 7.000 + 14.000 + 4.000 = 35.000",
            "incorrect": "Para saber cuánto debe antes de pagar, sumamos todas las compras del mes:\n10.000 + 7.000 + 14.000 + 4.000 = 35.000\nLa deuda total inicial es de $35.000."
          }
        },
        {
          "interaction_id": "I2_saldo_después_abono",
          "type": "numeric_input",
          "question": "Si la deuda total es de $35.000 y abona $30.000, ¿cuánto queda debiendo?",
          "expected_answer": 5000,
          "misconceptions_detected": [],
          "feedback": {
            "correct": "Después de abonar $30.000, todavía queda debiendo $5.000.\n35.000 − 30.000 = 5.000",
            "incorrect": "La deuda total era de $35.000 y el abono fue de $30.000.\nPara saber cuánto falta por pagar, restamos:\n35.000 − 30.000 = 5.000\nTodavía queda una deuda de $5.000."
          }
        },
        {
          "interaction_id": "I3_representacion_entero",
          "type": "single_choice",
          "question": "Si todavía debe $5.000, ¿cómo podemos representar esa deuda usando números enteros?",
          "options": ["5000", "-5000", "0"],
          "expected_answer": "-5000",
          "misconceptions_detected": ["confunde_deuda_con_cantidad_positiva", "no_reconoce_cero_como_equilibrio"],
          "feedback": {
            "correct": "La deuda se representa como un valor negativo porque está por debajo del punto de equilibrio.\nSi el punto de equilibrio es no deber nada, entonces:\ndeuda de 5.000 = −5.000",
            "5000": "5.000 puede representar una cantidad positiva, pero aquí no significa que el estudiante tenga $5.000 disponibles.\nComo todavía debe $5.000, lo representamos como:\n−5.000",
            "0": "0 representaría que el estudiante no debe nada y tampoco tiene saldo a favor.\nPero en este caso todavía debe $5.000. Por eso lo representamos como:\n−5.000"
          }
        },
        {
          "interaction_id": "I4_ubicacion_en_recta",
          "type": "numeric_line_placement",
          "question": "¿Dónde deberías ubicar −5.000 en la recta numérica?",
          "expected_answer": -5000,
          "range": [-50000, 50000],
          "misconceptions_detected": ["interpreta_negativos_por_valor_absoluto"],
          "feedback": {
            "correct": "Excelente. −5.000 está a la izquierda del 0 porque representa una deuda.\nCuando abonamos, el saldo se desplaza hacia la derecha, acercándose a 0.",
            "incorrect": "Los números negativos están a la izquierda del 0, no a la derecha.\n−5.000 representa una deuda (algo que falta), por eso va a la izquierda del punto de equilibrio (0)."
          },
          "animation": {
            "enabled": true,
            "description": "Desplaza saldo animado de −35.000 a −5.000 para mostrar efecto del abono"
          }
        }
      ]
    },

    "phase_2_formalization": {
      "name": "Formalización",
      "title": "¿Qué son los números enteros?",
      "definition": "Los números enteros son los números que usamos para representar cantidades positivas, cero y cantidades negativas.",
      "symbolic_representation": "Z = {…, −3, −2, −1, 0, 1, 2, 3, …}",
      "interpretation": "El cero es el punto de equilibrio. A la izquierda del cero están las deudas, pérdidas o valores bajo cero. A la derecha están las ganancias o valores positivos.",
      "expandable": true,
      "default_state_by_level": {
        "basico": "expanded",
        "intermedio": "collapsed",
        "avanzado": "collapsed"
      }
    },

    "phase_3_number_line": {
      "name": "Recta numérica",
      "type": "interactive_number_line",
      "range": [-10, 10],
      "content": "Los números enteros se pueden ubicar en una recta numérica.\nA la izquierda del cero están los números negativos.\nEn el centro está el cero.\nA la derecha están los números positivos.\n…, −3, −2, −1, 0, 1, 2, 3, …",
      "educator_note": "Mientras más a la derecha esté un número, mayor es.\nPor eso: −1 > −5\nPorque −1 está más a la derecha que −5."
    },

    "phase_4_examples": {
      "name": "Ejemplos y no ejemplos",
      "examples": [-10, -5, -1, 0, 1, 5, 10, 100],
      "non_examples": [-3.5, "-1/2", 0.75, "1/3", 2.5],
      "educator_note": "Los enteros representan cantidades completas. Cuando necesitemos partes o divisiones, vamos a usar otro conjunto llamado números racionales."
    },

    "phase_5_mini_challenge": {
      "name": "Mini reto",
      "type": "multi_select",
      "question": "Selecciona todos los números enteros según la definición de este nivel.",
      "options": [
        {"value": -8, "label": "−8"},
        {"value": -3.5, "label": "−3.5"},
        {"value": 0, "label": "0"},
        {"value": 0.5, "label": "1/2"},
        {"value": 6, "label": "6"},
        {"value": -2.1, "label": "−2.1"}
      ],
      "expected_answer": [-8, 0, 6],
      "feedback_by_error_pattern": {
        "correct_all": {
          "title": "✓ Bien",
          "body": "Correcto. En este nivel, −8, 0 y 6 son enteros.\nLos enteros representan cantidades completas, positivas, cero o negativas.",
          "misconception_tag": null
        },
        "omitted_zero": {
          "title": "⚠ Atención al cero",
          "body": "El 0 también es un número entero. Representa el punto de equilibrio, el punto entre deudas y ganancias.",
          "misconception_tag": "no_reconoce_cero_como_equilibrio"
        },
        "included_decimal": {
          "title": "⚠ Cuidado con los decimales",
          "body": "−3.5 es un número negativo, pero no es entero porque tiene una parte decimal.\nLos enteros representan cantidades completas, sin partes fraccionarias.\nCuando necesitemos representar partes, usaremos otro conjunto llamado números racionales.",
          "misconception_tag": "confunde_deuda_con_cantidad_positiva"
        },
        "included_fraction": {
          "title": "⚠ Cuidado con las fracciones",
          "body": "1/2 es una fracción, no un número entero. Representa una parte (media) de algo, no una cantidad completa.\nLos enteros representan cantidades completas, positivas, cero o negativas.",
          "misconception_tag": "incluye_no_enteros_en_enteros"
        }
      }
    }
  },

  "events_to_register": [
    "node_viewed",
    "situation_viewed",
    "interaction_attempt:I1_deuda_total",
    "interaction_attempt:I2_saldo_después_abono",
    "interaction_attempt:I3_representacion_entero",
    "interaction_attempt:I4_ubicacion_en_recta",
    "misconception_detected",
    "feedback_viewed",
    "number_line_viewed",
    "formalization_viewed",
    "mini_challenge_attempt",
    "mini_challenge_result",
    "node_completed",
    "transition_initiated"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_POSITIVE_REPRESENTATION",
      "level": "observation",
      "trigger": "Student represents debt as positive (5000) but corrects after feedback",
      "message_educator": "El estudiante inicialmente representó una deuda como cantidad positiva, pero corrigió después de la retroalimentación. Se recomienda observar si esta dificultad reaparece en clasificación."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_NEGATIVE_PERSISTENT",
      "level": "reinforcement_suggested",
      "trigger": "Student represents debts as positive two or more times across map activities",
      "message_educator": "El estudiante presenta dificultad recurrente para representar deudas con números negativos. Se recomienda reforzar esta pantalla y trabajar el cero como punto de equilibrio."
    },
    {
      "condition_id": "ALERT_INTERVENTION_MISINTERPRETATION",
      "level": "teacher_intervention",
      "trigger": "Student persists in locating debts as positive or interprets (−5000) as greater than (−1000) after feedback",
      "message_educator": "El estudiante mantiene dificultades para interpretar números negativos. Se recomienda intervención directa con ejemplos de deuda, cero y saldo a favor."
    }
  ],

  "level_presentation": {
    "basico": {
      "worked_example": "full",
      "default_expanded": true,
      "number_line_labels": "all",
      "hint_availability": "máximo"
    },
    "intermedio": {
      "worked_example": "partial",
      "default_expanded": false,
      "number_line_labels": "some",
      "hint_availability": "medio"
    },
    "avanzado": {
      "worked_example": "faded",
      "default_expanded": false,
      "number_line_labels": "minimal",
      "hint_availability": "mínimo"
    }
  },

  "design_handoff": {
    "node_state": "bloqueado|actual|completado",
    "path_position": "ruta_nucleo_second_numeric_set",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-tabla-compras]",
      "[componente-pregunta-entrada-numerica]",
      "[componente-pregunta-opcion-unica]",
      "[componente-pregunta-checkboxes]",
      "[componente-recta-numerica]",
      "[componente-ubicacion-en-recta]",
      "[componente-retroalimentacion-modal]",
      "[componente-formalización-expandible]",
      "[componente-ejemplos-tarjetas]",
      "[componente-transicion-hexagono]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: 10000, 7000, 14000, 4000, 35000, 30000, 5000, −5000, Z = {...}, −8, −3.5, 0, 1/2, 6, −2.1, recta numérica con negativos/cero/positivos"
  }
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** del bloque original, incluyendo:
- ✅ Texto completo de Katia
- ✅ Situación del problema (tienda escolar) con tabla de compras
- ✅ Todas las interacciones (4 en total)
- ✅ Retroalimentaciones diferenciadas
- ✅ Recta numérica con animación
- ✅ Storyboard detallado
- ✅ JSON técnico limpio

Sigue el mismo calibre que B04 (Naturales).
