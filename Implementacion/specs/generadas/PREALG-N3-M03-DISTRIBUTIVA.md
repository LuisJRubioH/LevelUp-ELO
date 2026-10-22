# Nodo: Se reparte sobre la suma, no sobre el producto — PREALG-N3-M03-DISTRIBUTIVA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N3-M03-DISTRIBUTIVA` |
| `concept_slug` | `distributiva` |
| Error focal | `distribuye_sobre_el_producto` |
| Sala / edificio | La Cinta Repartidora |
| Guía | KatIA |
| Entra después de | `PREALG-N3-M02-ASOCIATIVA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La Cinta Repartidora · Distributiva

**Título:** Se reparte sobre la suma, no sobre el producto

Las dos estaciones anteriores trabajaban con UNA operación a la vez. Aquí se mezclan dos: un factor por fuera y una suma por dentro. Vas a ver por qué el factor entra a cada sumando, y por qué el mismo movimiento con un producto por dentro multiplica de más.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de encender la cinta. Sin nota.

**D1**

¿Cuánto vale $3\times(4+2)$?

Respuesta: `18`

**D2**

¿Cuál es igual a $5\times(7+3)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | 5 × 7 + 5 × 3 | — |
| 　 | `partial` | 5 × 7 + 3 | `distribuye_solo_al_primer_sumando` |
| 　 | `double` | (5 × 7) × (5 × 3) | `distribuye_sobre_el_producto` |

**D3**

¿Cuánto vale $2\times(3\times 5)$?

Respuesta: `30`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la Cinta Repartidora* — **La caja que llegó llena de más**

La tercera estación es una cinta larga con un brazo repartidor: los engranajes bajan por la cinta y el brazo los va soltando en las cajas que haya al final. Si hay dos cajas, el brazo reparte a las dos; si hay tres, a las tres.

El encargado escribió el pedido así: «triple de lo que hay en las dos cajas». El brazo trabajó bien. Después escribió otro pedido igual de corto — «triple de una caja de cuatro filas de dos» — y el brazo triplicó la fila Y triplicó la columna. Salieron nueve veces los engranajes pedidos.

**Pregunta:** ¿Un factor que entra en un paréntesis se reparte a todo lo que hay dentro?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí: entra a todo lo que haya dentro | — |
| 　 | `b` | Solo si dentro hay una suma | — |
| 　 | `c` | Nunca: hay que calcular el paréntesis primero | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo factor, dos paréntesis distintos**

Abajo, el mismo 3 por fuera. Lo único que cambia es la operación de dentro.

- **Caso que funciona** — El 3 entra a cada caja. Y 3 × 6 = 18: coincide.
- **Caso que rompe la expectativa** — Repartir el 3 aquí multiplica de más: 72 en vez de 24.

**Resolución:** En la suma hay DOS montones distintos y el triple se le aplica a cada uno. En el producto hay UN solo montón descrito de dos maneras — filas y columnas — y triplicar las dos cosas triplica dos veces. El factor entra una sola vez, donde tú elijas.

**Definición — La propiedad distributiva**

$$a\times(b+c)=a\times b+a\times c$$

Multiplicar por una suma es lo mismo que multiplicar por cada sumando y después sumar. Es la única propiedad que conecta dos operaciones distintas, y es la base de todo lo que viene en álgebra.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a` | el factor que se reparte | el brazo repartidor: llega a cada caja |
| `b+c` | la suma de dentro | las cajas distintas que hay al final de la cinta |
| `a\times b+a\times c` | forma desarrollada | el factor ya repartido |
| `a\times(b\times c)\neq (a\times b)\times(a\times c)` | no se reparte sobre el producto | un solo montón: el factor entra una vez |
| `a\times(b-c)=a\times b-a\times c` | también sobre la resta | la resta es una suma con signo, así que sí vale |

### A5. Ejemplos resueltos

#### El pedido que el brazo hizo bien · *resuelto*

El encargo pide 7 veces el contenido de dos cajas: una con 30 engranajes y otra con 4. ¿Cuántos engranajes salen?

- Camino directo: 30 + 4 = 34, y 7 × 34. Cuesta de cabeza.
- Camino repartido: el 7 entra a cada caja. 7 × 30 = 210 y 7 × 4 = 28.
- Sumo lo que salió de cada caja: 210 + 28 = 238.
- Compruebo con el camino directo: 7 × 34 = 238. Coinciden.
- Repartir no cambió el resultado; convirtió una multiplicación difícil en dos fáciles.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': 'En el paso 2 el 7 entra a las DOS cajas. ¿Qué pasaría si solo entrara a la primera?'}

#### Repartir hacia atrás · *resuelto*

El encargo pide 8 veces lo que queda en una caja de 50 engranajes después de retirar 3. ¿Cuántos salen?

- La resta es una suma con signo: 50 − 3 = 50 + (−3).
- Así que el 8 también se reparte: 8 × 50 + 8 × (−3).
- 8 × 50 = 400 y 8 × (−3) = −24.
- 400 − 24 = 376.
- Compruebo: 50 − 3 = 47, y 8 × 47 = 376. Coinciden.

#### El brazo que repartió sobre un producto · *TRAMPA*

El encargado anota: «Pedido: 3 veces una caja de 4 filas de 2. Reparto el 3 como siempre: 3 × 4 por 3 × 2, o sea 12 × 6 = 72 engranajes».

- Cuenta lo que hay realmente: 4 filas de 2 son 8 engranajes en total.
- El triple de 8 es 24, no 72. 72 es el triple del triple.
- Repartir el 3 sobre un producto lo aplica dos veces: 3 × 3 = 9, y 9 × 8 = 72.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '3\\times(4\\times 2)=72', 'right_latex': '3\\times(4\\times 2)=3\\times 8=24', 'rows': [{'wrong': 'El factor se reparte a todo lo que haya en el paréntesis', 'right': 'Solo se reparte sobre sumas y restas, no sobre productos'}, {'wrong': '4 filas de 2 son dos montones distintos', 'right': 'Son UN montón de 8, descrito por filas y columnas'}]}
**¿Por qué falla?:** ¿Por qué 72 es imposible? Escribe la cuenta correcta.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — El encargo pide 6 veces dos cajas, una con 20 y otra con 5.

- dado: $6\times(20+5)=6\times 20+6\times 5$
- dado: $6\times 20=120,\quad 6\times 5=30$
- hueco `P1-b1`: $120+30=$ → `150`

**P2** (*falta: middle*) — El encargo pide 9 veces lo que queda de una caja de 40 tras retirar 2.

- dado: $9\times(40-2)=9\times 40-9\times 2$
- hueco `P2-b1`: $9\times 40=$ → `360`
- hueco `P2-b2`: $360-18=$ → `342`

**P3** (*falta: statement_only*) — Solo el planteamiento: el encargo pide 5 veces una caja de 6 filas de 3 engranajes. Da el total, sin repartir el 5.

- hueco `P3-b1`: $5\times(6\times 3)=$ → `90`


### A7. Comparación de métodos

**Dos caminos para el mismo pedido**

¿Cuánto vale $4\times 98$? Las dos soluciones de abajo son correctas.

- **Método 1 · Multiplicar directo** — 
- **Método 2 · Repartir sobre una resta** — 

**Pregunta:** ¿Cuál harías de cabeza con 4 × 97? ¿Y qué tuviste que inventar en el método 2 que no estaba en el enunciado?

**Insight:** El método 2 no simplifica una cuenta que ya existía: REESCRIBE el 98 como 100 − 2 para poder repartir. Esa reescritura es el motor de casi toda el álgebra que viene — sacar factor común, desarrollar un producto notable, factorizar — y todas son la distributiva leída en un sentido o en el otro.

### A8. Práctica independiente (7 ítems)

**E1**

El encargo pide 5 veces dos cajas, una con 12 y otra con 8. ¿Cuántos engranajes salen?

Respuesta: `100`

Escalera de pistas:
1. El 5 entra a cada caja.
2. 5 × 12 = 60 y 5 × 8 = 40.
3. 60 + 40 = …

**E2**

Calcula 6 × 99 repartiendo sobre una resta cómoda.

Respuesta: `594`

Escalera de pistas:
1. Reescribe 99 como 100 menos algo.
2. 6 × 100 = 600.
3. 600 − 6 = …

**E3**

El encargo pide 4 veces una caja de 7 filas de 3 engranajes. ¿Cuántos salen?

Respuesta: `84`

Escalera de pistas:
1. Primero cuenta lo que hay en la caja.
2. 7 × 3 = 21 engranajes.
3. 4 × 21 = …  (no repartas el 4)

**E4**

Un encargado anota «$6\times(10+4)=6\times 10+4=64$». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `half` | Repartió solo al primer sumando; falta multiplicar el 4 por 6 | — |
| 　 | `product` | Debía multiplicar los dos resultados en vez de sumarlos | `distribuye_sobre_el_producto` |
| 　 | `arith` | Se equivocó en 6 × 10 | `habito_error_de_calculo_no_de_metodo` |
| 　 | `none` | Ningún error, está bien | `distribuye_solo_al_primer_sumando` |

Escalera de pistas:
1. Calcula el paréntesis primero y compara: 6 × 14.
2. 6 × 14 = 84, no 64.
3. Faltan 20, que es exactamente 6 × 4 − 4.

**E5**

¿Es verdadera o falsa? «Para cualesquiera $a,b,c$: $a\times(b\times c)=(a\times b)\times(a\times c)$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_product` | Falsa: sobre un producto el factor entra una sola vez | — |
| 　 | `true` | Verdadera: el factor se reparte a todo el paréntesis | `distribuye_sobre_el_producto` |
| 　 | `false_never` | Falsa: nunca pueden coincidir | `olvida_el_caso_neutro` |
| 　 | `true_small` | Verdadera si los números son pequeños | `distribuye_sobre_el_producto` |

Escalera de pistas:
1. Para tumbar un «cualesquiera» basta UN caso.
2. Prueba con a = 3, b = 4, c = 2.
3. 3 × 8 = 24 pero 12 × 6 = 72. ¿Y si a fuera 1?

**E6**

Calcula 7 × 103 reescribiendo el 103 de forma cómoda.

Respuesta: `721`

Escalera de pistas:
1. 103 = 100 + 3.
2. 7 × 100 = 700 y 7 × 3 = 21.
3. 700 + 21 = …

**E7**

¿Cuál de estas expresiones es igual a $9\times 15+9\times 5$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `common` | 9 × (15 + 5) | — |
| 　 | `sum_all` | 9 + 15 + 5 | `confunde_factor_comun_con_suma` |
| 　 | `double_factor` | (9 + 9) × (15 + 5) | `duplica_el_factor_comun` |
| 　 | `product` | 9 × 15 × 5 | `confunde_suma_con_producto` |

Escalera de pistas:
1. Es la distributiva leída al revés: el 9 se repite en los dos términos.
2. Saca el 9 fuera y deja lo demás dentro.
3. 9 × 15 + 9 × 5 = 135 + 45 = 180. Comprueba cuál de las cuatro da 180.


### A9. Cierre

*Sobre qué se puede repartir un factor* — **¿El factor de fuera entra a cada término de dentro?**

Esta propiedad no habla de una operación sino de un PAR: la de fuera y la de dentro.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | El caso central. Dos montones distintos, el factor llega a los dos. |
|  | ✅ | También vale: la resta es una suma con signo. |
|  | ✗ | Un solo montón: repartir aplicaría el factor dos veces. Esta es la trampa del nodo. |
|  | ~ (ámbar) | Solo si la suma está ARRIBA. Repartir un denominador es de los errores más caros del álgebra. |
|  | ✅ | El exponente sí se reparte sobre un producto — justo al revés que el factor. |
|  | ✗ | Y aquí se invierte del todo: sobre una suma NO se reparte. Es el mismo error que la raíz en la Cantera (E06). |

Fíjate en la simetría: el factor se reparte sobre sumas y no sobre productos; el exponente sobre productos y no sobre sumas. Nunca «se reparte todo sobre todo». En el Calibre Cero vas a buscar los números que no cambian nada.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `two_ops` | En los tres se mezclan dos operaciones distintas | — |
| 　 | `always` | En los tres el factor de fuera entra a cada término | — |
| 　 | `inside` | En los tres hay que mirar qué operación hay DENTRO del paréntesis | — |
| 　 | `easier` | En los tres repartir hace la cuenta más fácil | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos engranajes salen?
¿Cuántos engranajes salen?

Respuesta: `360`

Escalera de pistas:
1. Dentro hay una suma: el 12 se puede repartir.
2. 12 × 25 = 300.
3. 12 × 5 = 60, y 300 + 60 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya miras qué operación hay dentro antes de repartir.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el factor entra una sola vez cuando dentro hay un producto.

**PD1**

¿Cuánto vale $4\times(5+3)$?

Respuesta: `32`

**PD2**

¿Cuál es igual a $6\times(9+2)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | 6 × 9 + 6 × 2 | — |
| 　 | `partial` | 6 × 9 + 2 | `distribuye_solo_al_primer_sumando` |
| 　 | `double` | (6 × 9) × (6 × 2) | `distribuye_sobre_el_producto` |

**PD3**

¿Cuánto vale $5\times(2\times 4)$?

Respuesta: `40`

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N3-M03-DISTRIBUTIVA-D2` | `partial` | `distribuye_solo_al_primer_sumando` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-D2` | `double` | `distribuye_sobre_el_producto` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E4` | `product` | `distribuye_sobre_el_producto` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E4` | `arith` | `habito_error_de_calculo_no_de_metodo` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E4` | `none` | `distribuye_solo_al_primer_sumando` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E5` | `true` | `distribuye_sobre_el_producto` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E5` | `false_never` | `olvida_el_caso_neutro` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E5` | `true_small` | `distribuye_sobre_el_producto` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E7` | `sum_all` | `confunde_factor_comun_con_suma` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E7` | `double_factor` | `duplica_el_factor_comun` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-E7` | `product` | `confunde_suma_con_producto` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-PD2` | `partial` | `distribuye_solo_al_primer_sumando` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |
| `PREALG-N3-M03-DISTRIBUTIVA-PD2` | `double` | `distribuye_sobre_el_producto` | Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/03-prealg-n3-fabrica/m03-distributiva-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
