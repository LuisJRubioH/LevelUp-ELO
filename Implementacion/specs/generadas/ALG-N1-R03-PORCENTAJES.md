# Nodo: Subir y bajar lo mismo no devuelve al punto de partida — ALG-N1-R03-PORCENTAJES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-R03-PORCENTAJES` |
| `concept_slug` | `porcentajes` |
| Error focal | `descuento_y_recargo_se_cancelan` |
| Sala / edificio | El pan de oro |
| Guía | Iuty |
| Entra después de | `ALG-N1-R02-REGLA-DE-TRES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El pan de oro · Porcentajes

**Título:** Subir y bajar lo mismo no devuelve al punto de partida

Un porcentaje es una razón con el denominador fijado en cien. Eso lo hace cómodo de comparar y peligroso de encadenar: el segundo cambio nunca se aplica sobre lo mismo que el primero.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar al obrador. Sin nota.

**D1**

¿Cuánto es el 10 % de 200 láminas?

Respuesta: `20`

**D2**

¿Cuánto es el 25 % de 80 láminas?

Respuesta: `20`

**D3**

Si un encargo de 100 láminas sube un 10 % y luego baja un 10 %, ¿queda en 100?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: queda en 99 | — |
| 　 | `yes` | Sí: sube 10 y baja 10 | `descuento_y_recargo_se_cancelan` |
| 　 | `more` | No: queda en 101 | `descuento_y_recargo_se_cancelan` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el obrador del pan de oro* — **Las cuatro láminas que faltaron**

El batihoja aplasta el oro hasta dejarlo en hojas finísimas. Se cuentan por láminas y no se pueden improvisar: el oro llega pesado desde el tesoro.

Iuty repasa el encargo del muro:

«Eran cien láminas. El maestro mandó ampliar el friso y subimos el encargo un veinte por ciento. A los tres días recortaron el friso y el encargo bajó un veinte por ciento.»

«El escriba anotó que volvíamos a estar en cien y pidió el oro de cien. Llegaron noventa y seis láminas y el batihoja no puede fabricar las otras cuatro: el oro que falta no está en el obrador, está en el tesoro.»

**Pregunta:** Si algo sube un tanto por ciento y luego baja el mismo, ¿vuelve a donde estaba?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí: lo que sube y baja lo mismo se compensa | — |
| 　 | `b` | No: el segundo cambio se calcula sobre una cantidad distinta | — |
| 　 | `c` | Depende de si primero sube o primero baja | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo veinte por ciento, dos cantidades distintas**

Un porcentaje no es una cantidad: es una parte DE algo. Y ese algo cambió.

- **La subida** — Veinte láminas más. La base del cálculo eran 100.
- **La bajada** — Veinticuatro láminas menos, no veinte. La base ya no era 100.

**Resolución:** El porcentaje que baja es el mismo, pero se aplica a una cantidad mayor, así que quita más de lo que había puesto. Escrito con factores queda a la vista: subir un 20 % es multiplicar por 1,20 y bajar un 20 % es multiplicar por 0,80, y 1,20 · 0,80 = 0,96. Nunca da 1.

**Definición — Porcentaje y factor de variación**

$$p\%\ \text{de}\ N=\dfrac{p}{100}\,N\qquad N\xrightarrow{+p\%} N\Bigl(1+\dfrac{p}{100}\Bigr)$$

Un PORCENTAJE es una razón de denominador 100: el p % de N es (p/100) · N. AUMENTAR un p % es multiplicar por 1 + p/100 y DISMINUIR un p % es multiplicar por 1 − p/100. Encadenar varios cambios es multiplicar sus factores, y por eso los porcentajes no se suman ni se cancelan entre sí.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{p}{100}` | por ciento | una razón con el denominador fijado en cien |
| `1{,}20` | factor de subida | aumentar un 20 % en un solo paso |
| `0{,}80` | factor de bajada | disminuir un 20 % en un solo paso |
| `1{,}20\cdot 0{,}80=0{,}96` | encadenar | dos cambios seguidos: los factores se multiplican |
| `1{,}25\cdot 0{,}80=1` | el que sí deshace | bajar un 20 % se deshace subiendo un 25 % |

### A5. Ejemplos resueltos

#### Calcular una parte de cien · *resuelto*

De cada encargo de 240 láminas, el 15 % se pierde en merma al batir el oro. ¿Cuántas láminas se pierden?

- El 15 % significa 15 de cada 100: la razón es 15/100.
- Aplico la razón a las 240 láminas: (15/100) · 240.
- 15 · 240 = 3600, y 3600 ÷ 100 = 36.
- Se pierden 36 láminas y quedan 204.
- Compruebo: el 10 % son 24 y el 5 % son 12; 24 + 12 = 36 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué el 15 % de 240 no son 15 láminas?'}

#### Subir un porcentaje en un solo paso · *resuelto*

El encargo era de 240 láminas y el maestro pide ampliarlo un 15 %. ¿Cuántas láminas se encargan?

- Puedo calcular el 15 % y sumarlo: 240 + 36 = 276.
- O hacerlo de una vez: quedarse con el 100 % y añadir el 15 % es el 115 %.
- El 115 % es el factor 1,15.
- 240 · 1,15 = 276 láminas.
- Las dos maneras dan lo mismo; la segunda es la que se puede encadenar.

#### El escriba que dio por compensados los dos cambios · *TRAMPA*

Vuelve el encargo de la apertura: 100 láminas, un 20 % más y después un 20 % menos. El escriba anotó 100 y pidió el oro de 100.

- Escribo los dos cambios como factores: 1,20 y 0,80.
- Los multiplico: 0,96. Es menor que 1, así que siempre se pierde.
- Regla para no volver a caer: los porcentajes encadenados se multiplican, nunca se suman ni se restan.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '100\\to 120\\to 100', 'right_latex': '100\\to 120\\to 96', 'rows': [{'wrong': 'Sube 20 y baja 20', 'right': 'Sube 20 y baja 24, porque baja sobre 120'}, {'wrong': '1{,}20-0{,}20=1', 'right': '1{,}20\\cdot 0{,}80=0{,}96'}]}
**¿Por qué falla?:** Explica por qué el resultado es menor que el de partida pase lo que pase, y di qué porcentaje de subida sí habría devuelto las 100 láminas.


### A6. Puente — parcialmente resueltos

El encargo va empezado; completa los huecos.

**P1** (*falta: last*) — Calcula el 20 % de 350 láminas.

- dado: $\dfrac{20}{100}\cdot 350$
- dado: $\dfrac{7000}{100}$
- hueco `P1-b1`: $7000\div 100=$ → `70`

**P2** (*falta: middle*) — Un encargo de 400 láminas sube un 25 %. ¿Cuántas quedan?

- dado: $400\cdot 1{,}25$
- hueco `P2-b1`: $25\%\ \text{de}\ 400=$ → `100`
- hueco `P2-b2`: $400+100=$ → `500`

**P3** (*falta: statement_only*) — Solo el planteamiento: 200 láminas suben un 10 % y después bajan un 10 %. ¿Cuántas quedan?

- hueco `P3-b1`: $200\cdot 1{,}10\cdot 0{,}90=$ → `198`


### A7. Comparación de métodos

**Dos maneras de aplicar dos cambios seguidos**

$300$ láminas suben un $10\,\%$ y después bajan un $30\,\%$.

- **Método 1 · Paso a paso** — 
- **Método 2 · Multiplicar los factores** — 

**Pregunta:** ¿Qué te dice el 0,77 que no te dicen los pasos intermedios?

**Insight:** Que el resultado de los dos cambios juntos es una bajada del 23 %, no del 20 % que saldría de restar 30 − 10. El método paso a paso llega al mismo número sin que llegues a saber eso, y ahí es donde se cuela la idea de que los porcentajes se suman. El factor combinado es la respuesta a «¿y en total, cuánto?», que suele ser la pregunta que importa.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto es el 12 % de 450 láminas?

Respuesta: `54`

Escalera de pistas:
1. El 12 % es 12 de cada 100.
2. El 1 % de 450 son 4,5 láminas.
3. 12 · 4,5 = …

**E2**

Un encargo de 500 láminas se reduce un 18 %. ¿Cuántas láminas quedan?

Respuesta: `410`

Escalera de pistas:
1. Bajar un 18 % es quedarse con el 82 %.
2. El 18 % de 500 son 90.
3. 500 − 90 = …

**E3**

200 láminas suben un 10 % y después bajan un 10 %. ¿Cuántas quedan?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | 198 | — |
| 　 | `same` | 200 | `descuento_y_recargo_se_cancelan` |
| 　 | `up` | 202 | `descuento_y_recargo_se_cancelan` |
| 　 | `down` | 180 | `suma_los_porcentajes` |

Escalera de pistas:
1. La subida se calcula sobre 200; la bajada, sobre 220.
2. El 10 % de 220 son 22, no 20.
3. 220 − 22 = …

**E4**

Un escriba anota: «el encargo bajó un 30 % y luego subió un 30 %, así que está como al principio». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `base` | La subida se aplica sobre una cantidad menor: queda en el $91\,\%$ | — |
| 　 | `order` | El error es el orden: si primero sube sí vuelve | `el_orden_de_los_porcentajes_importa` |
| 　 | `calc` | Calculó mal el 30 % | `suma_los_porcentajes` |
| 　 | `none` | No hay error | `descuento_y_recargo_se_cancelan` |

Escalera de pistas:
1. Escribe los dos cambios como factores.
2. 0,70 · 1,30 = 0,91.
3. 0,91 no es 1: falta un 9 %.

**E5**

¿Verdadera o falsa? «Subir un 20 % y después bajar un 20 % deja la cantidad como estaba.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: queda en el $96\,\%$, porque la bajada se aplica sobre más | — |
| 　 | `true` | Verdadera: se sube y se baja lo mismo | `descuento_y_recargo_se_cancelan` |
| 　 | `true_order` | Verdadera si se hace en ese orden y no al revés | `el_orden_de_los_porcentajes_importa` |
| 　 | `false_more` | Falsa: queda por encima, en el $104\,\%$ | `descuento_y_recargo_se_cancelan` |

Escalera de pistas:
1. Prueba con 100 láminas y sigue las dos cuentas.
2. 100 → 120 → 96.
3. La bajada quitó 24, no 20.

**E6**

Selecciona TODAS las parejas de cambios que devuelven la cantidad exacta de partida.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | Subir un 25 % y luego bajar un 20 % | — |
| 　 | `b` | Subir un 20 % y luego bajar un 20 % | — |
| ✅ | `c` | Subir un 100 % y luego bajar un 50 % | — |
| 　 | `d` | Bajar un 10 % y luego subir un 10 % | — |

Escalera de pistas:
1. Multiplica los dos factores de cada pareja.
2. 1,25 · 0,80 y 2 · 0,50 dan exactamente 1.
3. Los otros dos dan 0,96 y 0,99.

**E7**

El obrador recibe 800 láminas. Un 25 % se aparta para el friso y del resto se pierde un 20 % en merma. ¿Cuántas láminas quedan utilizables después de la merma?

Respuesta: `480`

Escalera de pistas:
1. Apartar el 25 % deja el 75 %.
2. El 75 % de 800 son 600.
3. Perder el 20 % de 600 deja …


### A9. Cierre

*¿Vuelve al valor de partida?* — **Qué parejas de cambios se deshacen y cuáles no**

Encadenar dos porcentajes es multiplicar dos factores. Que la pareja se deshaga significa una sola cosa: que su producto valga exactamente 1.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Se pierde un 4 %. La bajada actúa sobre más de lo que había. Es el caso focal. |
|  | ✗ | Sale exactamente lo mismo: el orden no arregla nada, porque el producto no cambia. |
|  | ✗ | Un 44 % más, no un 40 %. Los porcentajes tampoco se suman entre sí. |
|  | ✅ | Existe el porcentaje que deshace: nunca es el mismo número que lo hizo. |
|  | ✅ | El mismo caso con números grandes: 100 y 50 no se parecen y aun así se deshacen. |
|  | ~ (ámbar) | El único cambio sin vuelta: multiplicado por cero, ningún porcentaje posterior recupera nada. |

Las tres primeras filas dicen lo mismo desde ángulos distintos: los porcentajes no se suman ni se restan, se multiplican como factores. La cuarta y la quinta son la parte útil — sí existe el cambio que deshace, y para encontrarlo hay que preguntarse qué número multiplicado por el primero da 1. Es el recíproco, el mismo que aprendiste a usar en el silo de simiente.

#### Pregunta de abstracción

¿Qué comparten los tres encargos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `base` | En los tres el porcentaje se calcula siempre sobre una cantidad concreta, y hay que saber cuál | — |
| 　 | `factor` | En los tres el cambio se puede escribir como multiplicar por un factor | — |
| 　 | `add` | En los tres los porcentajes se pueden sumar o restar entre sí | — |
| 　 | `fixed` | En los tres un mismo porcentaje representa siempre la misma cantidad de láminas | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas láminas quedan encargadas?
¿Cuántas láminas quedan encargadas?

Respuesta: `810`

Escalera de pistas:
1. Subir un 20 % es multiplicar por 1,20; bajar un 25 %, por 0,75.
2. 1,20 · 0,75 = 0,90.
3. El 90 % de 900 es …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otro encargo. Sin nota.

- **Mejoró:** Avance: ya multiplicas factores en vez de sumar porcentajes.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo sobre qué cantidad se calcula cada porcentaje.

**PD1**

¿Cuánto es el 10 % de 350 láminas?

Respuesta: `35`

**PD2**

¿Cuánto es el 20 % de 60 láminas?

Respuesta: `12`

**PD3**

Si un encargo de 200 láminas baja un 10 % y luego sube un 10 %, ¿queda en 200?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: queda en 198 | — |
| 　 | `yes` | Sí: baja 20 y sube 20 | `descuento_y_recargo_se_cancelan` |
| 　 | `more` | No: queda en 202 | `descuento_y_recargo_se_cancelan` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-R03-PORCENTAJES-D3` | `yes` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-D3` | `more` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E3` | `same` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E3` | `up` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E3` | `down` | `suma_los_porcentajes` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E4` | `order` | `el_orden_de_los_porcentajes_importa` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E4` | `calc` | `suma_los_porcentajes` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E4` | `none` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E5` | `true` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E5` | `true_order` | `el_orden_de_los_porcentajes_importa` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-E5` | `false_more` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-PD3` | `yes` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |
| `ALG-N1-R03-PORCENTAJES-PD3` | `more` | `descuento_y_recargo_se_cancelan` | Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
