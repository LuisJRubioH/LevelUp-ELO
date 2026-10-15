# Nodo: Poner el número donde estaba la letra no basta — ALG-N1-L04-VALOR-NUMERICO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-L04-VALOR-NUMERICO` |
| `concept_slug` | `valor_numerico` |
| Error focal | `yuxtapone_en_vez_de_multiplicar` |
| Sala / edificio | La cámara del recuento |
| Guía | Meritka |
| Entra después de | `ALG-N1-L03-TRADUCCION` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La cámara del recuento · Valor numérico

**Título:** Poner el número donde estaba la letra no basta

Ya sabes escribir un registro. Ahora hay que devolverlo a números: llega el día del arqueo y cada registro tiene que dar una cantidad concreta de grano. Ahí se ve si entendiste lo que estabas escribiendo o solo lo copiabas.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de bajar a la cámara. Sin nota.

**D1**

¿Cuánto es 3 · 7 + 2?

Respuesta: `23`

**D2**

Si $n=4$, ¿cuánto vale $3n$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `twelve` | 12 | — |
| 　 | `thirtyfour` | 34 | `yuxtapone_en_vez_de_multiplicar` |
| 　 | `seven` | 7 | `confunde_producto_con_suma` |

**D3**

¿Cuánto es 2 + 3 · 4?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `fourteen` | 14 | — |
| 　 | `twenty` | 20 | `opera_de_izquierda_a_derecha` |
| 　 | `nine` | 9 | `confunde_producto_con_suma` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la cámara del recuento* — **El arqueo que no cuadró por una letra**

En la cámara hay fichas de barro con las cuentas del año y un cordel de conteo colgado de la pared. Meritka descuelga una tablilla:

«Este registro dice 3n. Hoy n vale cuatro. El contable de la primavera anotó treinta y cuatro medidas de grano y mandó cargar treinta y cuatro carros.»

Se quedó mirando el cordel: quedaban veintidós carros sin nada que cargar.

«No se equivocó al escribir el registro. Se equivocó al leerlo.»

**Pregunta:** ¿Qué se hace exactamente cuando se sustituye una letra por su valor?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Se escribe el número en el hueco de la letra y se lee lo que quede | — |
| 　 | `b` | Se pone el número y además se hace la operación que había entre medias | — |
| 　 | `c` | Se suma el número al que ya estaba delante | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El hueco no está vacío: hay una operación escondida**

Dos registros parecidos. En uno la operación se ve; en el otro está callada.

- **La operación se ve** — El signo está escrito: nadie duda de qué hacer.
- **La operación está callada** — Pegar el 3 a la n YA significa multiplicar. Sustituir no borra ese producto.

**Resolución:** Escribir 3n junto es una abreviatura de 3 · n. Al sustituir, la abreviatura deja de valer —3 · 4 no se puede escribir «34»— así que el punto tiene que reaparecer. Lo mismo pasa con los paréntesis: se ponen al sustituir aunque no estuvieran en el registro.

**Definición — Valor numérico de una expresión**

$$3n\ \text{con}\ n=4\;\longrightarrow\;3\cdot(4)=12$$

El VALOR NUMÉRICO de una expresión es el número que resulta de sustituir cada letra por su valor y operar. Sustituir tiene dos reglas que no se ven en el registro: la yuxtaposición (3n) es un producto y hay que escribirlo como tal, y el valor entra entre paréntesis, para que el orden de operaciones y los signos sigan funcionando.

| Símbolo | Se lee | Significa |
|---|---|---|
| `3n\to 3\cdot(4)` | tres por cuatro | el producto callado reaparece |
| `3+n\to 3+(4)` | tres más cuatro | la operación ya estaba escrita |
| `n^{2}\to (4)^{2}` | cuatro al cuadrado | el exponente afecta a todo el valor |
| `5-n\to 5-(-3)` | cinco menos, menos tres | con negativos, el paréntesis es obligatorio |
| `2n^{2}\to 2\cdot(3)^{2}` | dos por tres al cuadrado | primero la potencia, después el producto |

### A5. Ejemplos resueltos

#### Sustituir y operar · *resuelto*

El registro del almacén de remos dice 5r + 8, donde r es el número de barcas. Hoy hay 6 barcas. ¿Cuántos remos figuran?

- Reescribo el producto callado: 5r es 5 · r.
- Sustituyo r por su valor entre paréntesis: 5 · (6) + 8.
- Primero el producto: 5 · 6 = 30.
- Después la suma: 30 + 8 = 38.
- El arqueo da 38 remos. Si hubiera 7 barcas darían 43: solo se movió la r.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué se hace el producto antes que la suma, si la suma está escrita después?'}

#### Cuando el valor es negativo · *resuelto*

En las fichas de barro una deuda se anota con signo. El registro 5 − d mide lo que queda, y hoy d vale −3. ¿Cuánto queda?

- Sustituyo d por su valor, entre paréntesis: 5 − (−3).
- Sin el paréntesis quedaría 5 − −3, que no es una cuenta legible.
- Restar una deuda es sumar: 5 − (−3) = 5 + 3.
- El resultado es 8.
- Tiene sentido: si lo que se resta es una deuda, lo que queda aumenta.

#### El contable que pegó los números · *TRAMPA*

Vuelve el caso de la apertura: el registro 3n con n = 4. El contable de la primavera anotó 34 y mandó cargar 34 carros.

- Pruebo con un valor pequeño: si n = 1, «pegar» daría 31, y el triple de 1 es 3.
- Con n = 0, «pegar» daría 30, y el triple de 0 es 0. El disparate es visible.
- Regla para no volver a caer: al sustituir, escribe el punto y el paréntesis, aunque no estuvieran.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '3n=34', 'right_latex': '3n=3\\cdot 4=12', 'rows': [{'wrong': 'El 3 y el 4 se escriben seguidos: 34', 'right': 'El 3 y la n estaban multiplicándose: 3 · 4 = 12'}, {'wrong': '34 medidas → 34 carros', 'right': '12 medidas → 12 carros, y sobran 22'}]}
**¿Por qué falla?:** Explica por qué escribir 3n junto no es lo mismo que escribir 34 junto, aunque las dos cosas se vean pegadas.


### A6. Puente — parcialmente resueltos

El arqueo va empezado; completa los huecos.

**P1** (*falta: last*) — Calcula el valor de $4m+7$ cuando $m=5$.

- dado: $4\cdot(5)+7$
- dado: $20+7$
- hueco `P1-b1`: $20+7=$ → `27`

**P2** (*falta: middle*) — Calcula el valor de $2k^{2}$ cuando $k=3$.

- dado: $2\cdot(3)^{2}$
- hueco `P2-b1`: $(3)^{2}=$ → `9`
- hueco `P2-b2`: $2\cdot 9=$ → `18`

**P3** (*falta: statement_only*) — Solo el planteamiento: el registro $6-p$ con $p=-2$. Recuerda el paréntesis.

- hueco `P3-b1`: $6-(-2)=$ → `8`


### A7. Comparación de métodos

**Dos maneras de sustituir**

El registro $7-2n$, con $n=-4$. Las dos empiezan igual y no acaban igual.

- **Método 1 · Escribir el valor en el hueco** — 
- **Método 2 · Meter el valor entre paréntesis** — 

**Pregunta:** ¿Cuándo se nota la diferencia entre los dos métodos?

**Insight:** Con valores positivos los dos dan lo mismo y el paréntesis parece un capricho. La diferencia aparece con negativos y con exponentes: en 7 − 2n con n = −4, sin paréntesis es fácil terminar en 7 − 8 = −1 en vez de 15. Por eso conviene poner el paréntesis siempre, y no solo cuando ya se ve el peligro — cuando se ve, normalmente ya te equivocaste.

### A8. Práctica independiente (7 ítems)

**E1**

Calcula el valor de $6t+5$ cuando $t=7$.

Respuesta: `47`

Escalera de pistas:
1. 6t es 6 · t: el producto está callado, pero está.
2. 6 · 7 = 42.
3. 42 + 5 = …

**E2**

Si $m=5$, ¿cuánto vale $4m$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `twenty` | 20 | — |
| 　 | `fortyfive` | 45 | `yuxtapone_en_vez_de_multiplicar` |
| 　 | `nine` | 9 | `confunde_producto_con_suma` |
| 　 | `fivefour` | 54 | `yuxtapone_en_vez_de_multiplicar` |

Escalera de pistas:
1. Escribe el producto que estaba callado.
2. 4 · m con m = 5.
3. Cuatro veces cinco.

**E3**

Calcula el valor de $3k^{2}$ cuando $k=4$.

Respuesta: `48`

Escalera de pistas:
1. El exponente afecta solo a la k, no al 3.
2. Primero la potencia: 4² = 16.
3. 3 · 16 = …

**E4**

Un contable calcula 9 − b con b = −5 y anota 4, porque «nueve menos cinco». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `paren` | Ignoró el signo del valor: 9 − (−5) = 14 | — |
| 　 | `op` | La operación no era una resta | `confunde_la_operacion_dictada` |
| 　 | `value` | b no puede valer un número negativo | `magnitud_sin_signo` |
| 　 | `none` | No hay error: 9 − 5 = 4 | `sustituye_sin_parentesis` |

Escalera de pistas:
1. Sustituye poniendo el valor entre paréntesis.
2. Queda 9 − (−5), no 9 − 5.
3. Restar una cantidad negativa suma.

**E5**

¿Verdadera o falsa? «Para hallar el valor de $2n$ basta con escribir el valor de $n$ al lado del 2.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: $2n$ es $2\cdot n$, así que con $n=7$ vale 14, no 27 | — |
| 　 | `true` | Verdadera: por eso se escriben pegados | `yuxtapone_en_vez_de_multiplicar` |
| 　 | `true_small` | Verdadera si el valor es de una sola cifra | `yuxtapone_en_vez_de_multiplicar` |
| 　 | `false_never` | Falsa: nunca se puede sustituir directamente | `sobregeneraliza_valor_numerico` |

Escalera de pistas:
1. Prueba con n = 0 y mira si el resultado tiene sentido.
2. «Pegar» daría 20; el doble de 0 es 0.
3. Estar pegados significa multiplicar.

**E6**

Con $x=3$, selecciona TODOS los registros cuyo valor numérico es $9$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $3x$ | — |
| ✅ | `b` | $x^{2}$ | — |
| 　 | `c` | $x+3$ | — |
| ✅ | `d` | $2x+3$ | — |

Escalera de pistas:
1. Evalúa uno por uno; no descartes por el aspecto.
2. 3x y x² dan lo mismo solo porque x vale 3.
3. x + 3 con x = 3 da 6.

**E7**

El registro del granero dice 8g − 12, donde g son los graneros abiertos. Hoy hay 5 abiertos. ¿Cuántas medidas figuran en el arqueo?

Respuesta: `28`

Escalera de pistas:
1. 8g es 8 · g.
2. 8 · 5 = 40.
3. 40 − 12 = …


### A9. Cierre

*¿Basta con poner el número en el hueco?* — **Qué hay que reponer al sustituir**

Sustituir no es rellenar una casilla. Hay cosas que el registro daba por sabidas y que al poner el número tienen que volver a escribirse.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Nada que reponer: la operación ya estaba a la vista. |
|  | ✗ | Hay que devolver el punto. Es el caso focal: pegado significa multiplicar. |
|  | ✗ | El exponente afecta a todo el valor sustituido, no a una cifra suelta. |
|  | ✗ | Sin paréntesis quedan dos signos seguidos y la cuenta deja de ser legible. |
|  | ✗ | Además del punto y el paréntesis, hay que respetar el orden: potencia antes que producto. |
|  | ~ (ámbar) | Se sustituye igual que los demás, pero el resultado sale positivo: ese menos no dice «negativo», dice «el opuesto». |

La última fila es la que más cuesta: −n no es «un número negativo», es «el opuesto de n», y si n ya era negativo el valor sale positivo. Todas las filas dicen lo mismo desde ángulos distintos — el registro está abreviado, y sustituir es el momento de desabreviarlo.

#### Pregunta de abstracción

¿Qué comparten los tres arqueos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `restore` | En los tres hay que reponer algo que el registro daba por sabido | — |
| 　 | `order` | En los tres el resultado depende de operar en el orden correcto | — |
| 　 | `fill` | En los tres basta con escribir el número donde estaba la letra | — |
| 　 | `same` | En los tres el valor numérico es el mismo cualquiera que sea la letra | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas medidas figuran en el arqueo?
¿Cuántas medidas figuran en el arqueo?

Respuesta: `75`

Escalera de pistas:
1. Escribe el producto callado antes de sustituir.
2. 7 · 12 = 84.
3. 84 − 9 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otras cifras. Sin nota.

- **Mejoró:** Avance: ya repones el producto y el paréntesis antes de operar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué 3n con n = 4 no puede ser 34.

**PD1**

¿Cuánto es 5 · 6 + 3?

Respuesta: `33`

**PD2**

Si $m=6$, ¿cuánto vale $2m$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `twelve` | 12 | — |
| 　 | `twentysix` | 26 | `yuxtapone_en_vez_de_multiplicar` |
| 　 | `eight` | 8 | `confunde_producto_con_suma` |

**PD3**

Si $p=-2$, ¿cuánto vale $4-p$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `six` | 6 | — |
| 　 | `two` | 2 | `sustituye_sin_parentesis` |
| 　 | `minussix` | −6 | `magnitud_sin_signo` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-L04-VALOR-NUMERICO-D2` | `thirtyfour` | `yuxtapone_en_vez_de_multiplicar` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-D2` | `seven` | `confunde_producto_con_suma` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-D3` | `twenty` | `opera_de_izquierda_a_derecha` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-D3` | `nine` | `confunde_producto_con_suma` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E2` | `fortyfive` | `yuxtapone_en_vez_de_multiplicar` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E2` | `nine` | `confunde_producto_con_suma` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E2` | `fivefour` | `yuxtapone_en_vez_de_multiplicar` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E4` | `op` | `confunde_la_operacion_dictada` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E4` | `value` | `magnitud_sin_signo` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E4` | `none` | `sustituye_sin_parentesis` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E5` | `true` | `yuxtapone_en_vez_de_multiplicar` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E5` | `true_small` | `yuxtapone_en_vez_de_multiplicar` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-E5` | `false_never` | `sobregeneraliza_valor_numerico` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-PD2` | `twentysix` | `yuxtapone_en_vez_de_multiplicar` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-PD2` | `eight` | `confunde_producto_con_suma` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-PD3` | `two` | `sustituye_sin_parentesis` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |
| `ALG-N1-L04-VALOR-NUMERICO-PD3` | `minussix` | `magnitud_sin_signo` | Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
