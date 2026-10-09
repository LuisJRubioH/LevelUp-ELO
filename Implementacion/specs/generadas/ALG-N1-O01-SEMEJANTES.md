# Nodo: Un registro más corto sin mezclar lo que no se mezcla — ALG-N1-O01-SEMEJANTES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-O01-SEMEJANTES` |
| `concept_slug` | `terminos_semejantes` |
| Error focal | `combina_no_semejantes` |
| Sala / edificio | La rampa |
| Guía | Bakenra |
| Entra después de | `ALG-N1-L04-VALOR-NUMERICO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La rampa · Términos semejantes

**Título:** Un registro más corto sin mezclar lo que no se mezcla

Ya sabes escribir una cantidad que cambia. Ahora llegan dos registros a la vez y hay que dejarlos en uno solo — pero acortar no es amontonar: hay cantidades que no se pueden juntar por mucho que estén en la misma línea.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de subir a la rampa. Sin nota.

**D1**

Una cuadrilla arrastra 7 trineos por turno. ¿Cuántos trineos arrastra en 3 turnos?

Respuesta: `21`

**D2**

¿Cuántos términos tiene $3x+4$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | 2 | — |
| 　 | `three` | 3 | `cuenta_simbolos_no_terminos` |
| 　 | `one` | 1 | `no_separa_por_los_signos` |

**D3**

¿Se puede escribir $2x+3y$ como un solo término?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: son cantidades de tipos distintos | — |
| 　 | `yes_sum` | Sí: $5xy$ | `combina_no_semejantes` |
| 　 | `yes_num` | Sí: $5$ | `combina_no_semejantes` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Al pie de la rampa* — **Los dos registros del capataz**

Bakenra tiene dos tablillas de turno delante y una cuadrilla esperando instrucciones. La primera anota lo que se sacó del almacén por la mañana; la segunda, lo de la tarde. Las dos usan letras: c para las cuerdas que se gastan, h para las herramientas.

«Necesito una sola lista», dice Bakenra, «o la cuadrilla va a bajar dos veces al almacén. Pero el escriba de ayer me juntó las cuerdas con las herramientas y subieron con la mitad de lo que hacía falta.»

**Pregunta:** ¿Qué se puede juntar en un registro y qué tiene que seguir separado?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Todo lo que esté sumado se puede juntar | — |
| 　 | `b` | Solo lo que sea del mismo tipo | — |
| 　 | `c` | Nada: hay que dejar las dos tablillas | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos sumas que parecen iguales y no lo son**

Las dos tienen la misma forma escrita. Solo una se puede acortar.

- **Se juntan** — Es la misma cantidad contada dos veces: 3 veces c más 2 veces c son 5 veces c.
- **No se juntan** — No hay ningún número que sea «cuerdas y herramientas a la vez». La suma queda indicada.

**Resolución:** Lo que permite acortar no es que estén sumados, sino que la parte con letras sea EXACTAMENTE la misma. Cuando lo es, la distributiva saca esa parte fuera y solo quedan los coeficientes sumándose. Cuando no lo es, no hay nada que sacar.

**Definición — Términos semejantes**

$$ac+bc=(a+b)\,c$$

Dos términos son SEMEJANTES cuando tienen exactamente la misma parte literal: las mismas letras elevadas a los mismos exponentes. Para sumarlos o restarlos se operan los coeficientes y la parte literal se conserva intacta. Los términos constantes son semejantes entre sí.

| Símbolo | Se lee | Significa |
|---|---|---|
| `3c` | tres ce | coeficiente 3, parte literal c |
| `3c+2c=5c` | se juntan | misma parte literal: se suman los coeficientes |
| `3c+2h` | no se juntan | partes literales distintas: la suma queda indicada |
| `3x\ \text{y}\ 3x^{2}` | tampoco | misma letra pero distinto exponente — no son semejantes |
| `x=1x` | el coeficiente invisible | una letra sola lleva un 1 delante que no se escribe |

### A5. Ejemplos resueltos

#### Reordenar antes de juntar · *resuelto*

El almacén entrega 4 tramos de cuerda, luego 3 estacas y luego 2 tramos más de cuerda. Escribe el registro lo más corto posible.

- Llamo r a la longitud de un tramo de cuerda. Las 3 estacas son una cantidad fija.
- El registro largo es 4r + 3 + 2r.
- Reordeno para poner juntos los semejantes: 4r + 2r + 3. Sumar en otro orden no cambia el total.
- Junto los dos términos en r: 4r + 2r = 6r.
- El 3 se queda solo, porque no hay ningún otro término sin letra: 6r + 3.

**Autoexplicación (focal):** {'step_index': 4, 'prompt': '¿Por qué el 3 no se junta ni con 4r ni con 2r?'}

#### Cuando hay que devolver parte de lo entregado · *resuelto*

En el turno de mañana se sacan 5 lotes de herramienta y 4 mazos. En el de tarde se devuelven 2 lotes y 1 mazo. ¿Qué queda en la obra?

- Lo devuelto se resta entero, así que va dentro de un paréntesis.
- El signo menos afecta a TODO lo del paréntesis: 5h + 4 − 2h − 1.
- Junto los términos en h: 5h − 2h = 3h.
- Junto las constantes: 4 − 1 = 3.
- Queda 3h + 3. Compruebo con h = 10: (54) − (21) = 33, y 3 · 10 + 3 = 33 ✓.

#### El escriba que juntó cuerdas con bloques · *TRAMPA*

El escriba de ayer entregó este registro: «3 tramos de cuerda y 4 bloques son 7 cuerdas-bloque», y lo escribió así: 3x + 4y = 7xy.

- Sustituyo x = 2 e y = 5 en el original: 3 · 2 + 4 · 5 = 6 + 20 = 26.
- Sustituyo en el resultado del escriba: 7 · 2 · 5 = 70. No es lo mismo.
- Un solo contraejemplo basta: la igualdad es falsa, y la cuadrilla subió con 26 en vez de 70.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '3x+4y=7xy', 'right_latex': '3x+4y', 'rows': [{'wrong': '3 + 4 = 7, así que el resultado lleva un 7', 'right': 'Los coeficientes solo se suman si la parte literal es la misma'}, {'wrong': 'x junto a y da xy', 'right': 'xy significa x · y, un producto — aquí solo había una suma'}]}
**¿Por qué falla?:** Explica por qué 3x + 4y no se puede acortar y comprueba el error sustituyendo x = 2 e y = 5.


### A6. Puente — parcialmente resueltos

El registro ya va empezado; completa los huecos.

**P1** (*falta: last*) — Simplifica 7a + 2a + 5 y evalúa el resultado para a = 4.

- dado: $7a+2a+5=9a+5$
- dado: $a=4$
- hueco `P1-b1`: $9a+5=$ → `41`

**P2** (*falta: middle*) — Simplifica (6t + 9) − (2t + 3) y evalúa para t = 5. Completa los dos pasos.

- dado: $6t+9-2t-3$
- hueco `P2-b1`: $\text{coeficiente de }t:\ 6-2=$ → `4`
- hueco `P2-b2`: $4t+6\ \text{con}\ t=5:$ → `26`

**P3** (*falta: statement_only*) — Solo el planteamiento: cada cuadrilla necesita 2 lotes de herramienta más 3 de repuesto. Con m cuadrillas la obra pide 2(m + 3) lotes. ¿Cuántos lotes con 7 cuadrillas?

- hueco `P3-b1`: $2(m+3)=2m+6\ \text{con}\ m=7:$ → `20`


### A7. Comparación de métodos

**Dos maneras de acortar el mismo registro**

Simplifica $2x+5+3x-2$. Las dos soluciones de abajo son correctas.

- **Método 1 · Reordenar y sumar** — 
- **Método 2 · Separar por tipos y contar** — 

**Pregunta:** ¿Cuál conviene aquí y cuál preferirías con doce términos y tres letras distintas?

**Insight:** Con cuatro términos el primero va sobrado. Cuando la lista crece, el segundo gana: hacer una columna por parte literal convierte el problema en varias sumas cortas e independientes, y un término olvidado se ve enseguida porque deja una columna sin cerrar.

### A8. Práctica independiente (7 ítems)

**E1**

Simplifica $3x+5x$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `eightx` | $8x$ | — |
| 　 | `eightx2` | $8x^{2}$ | `suma_los_exponentes_al_sumar` |
| 　 | `fifteenx` | $15x$ | `confunde_suma_con_producto` |
| 　 | `eight` | $8$ | `pierde_la_parte_literal` |

Escalera de pistas:
1. Los dos tienen la misma parte literal: x.
2. Se suman los coeficientes y la parte literal se queda igual.
3. 3 + 5 = 8, y la x sigue siendo x.

**E2**

Simplifica $(7h+4)-(3h+1)$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `correct` | $4h+3$ | — |
| 　 | `nosign` | $4h+5$ | `distribucion_parcial_del_signo` |
| 　 | `allsub` | $10h+5$ | `ignora_el_signo_de_resta` |
| 　 | `mixed` | $7h$ | `combina_no_semejantes` |

Escalera de pistas:
1. El menos de delante afecta a los DOS términos del paréntesis.
2. Quedan 7h + 4 − 3h − 1.
3. 7 − 3 = 4 para la h, y 4 − 1 = 3 para las constantes.

**E3**

Simplifica 4r + 3 + 2r. Escribe la expresión más corta equivalente.

Respuesta: `6r+3`
También válidas: `3+6r`

Escalera de pistas:
1. Junta primero los términos que llevan r.
2. 4r + 2r = 6r, y el 3 se queda solo.
3. Escríbelo como coeficiente, letra y después la constante.

**E4**

Un escriba anota: «(8k + 5) − (3k + 2) = 8k + 5 − 3k + 2 = 5k + 7». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sign` | No repartió el menos al 2: debía quedar −2, y el resultado es 5k + 3 | — |
| 　 | `coef` | Se equivocó al restar los coeficientes de k | `habito_busca_el_error_donde_no_esta` |
| 　 | `like` | Juntó términos que no eran semejantes | `habito_busca_el_error_donde_no_esta` |
| 　 | `none` | No hay error | `distribucion_parcial_del_signo` |

Escalera de pistas:
1. Mira el paso donde desaparece el paréntesis y sigue los signos uno a uno.
2. 8k − 3k = 5k está bien. El problema está en el término sin letra.
3. Restar (3k + 2) es restar el 3k Y el 2.

**E5**

¿Es verdadera o falsa? «$3x+4y=7xy$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: las partes literales son distintas, la suma se queda indicada | — |
| 　 | `true` | Verdadera: 3 + 4 = 7 y las letras se juntan en xy | `combina_no_semejantes` |
| 　 | `true_if` | Verdadera solo si $x=y$ | `combina_no_semejantes` |
| 　 | `false_seven` | Falsa: el resultado correcto es $7x+7y$ | `reparte_el_coeficiente_a_todo` |

Escalera de pistas:
1. Para tumbar una igualdad basta UN par de valores.
2. Prueba con x = 2 e y = 5 en los dos lados.
3. 26 en un lado y 70 en el otro: no puede ser cierta.

**E6**

Selecciona TODOS los pares de términos que SÍ son semejantes.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $5m$ y $-2m$ | — |
| 　 | `b` | $3k^{2}$ y $7k$ | — |
| ✅ | `c` | $4ab$ y $9ba$ | — |
| 　 | `d` | $6p$ y $6q$ | — |

Escalera de pistas:
1. Semejantes = misma parte literal, exponentes incluidos.
2. ab y ba son la misma parte literal: el orden del producto da igual.
3. k² y k no son lo mismo, y p y q son letras distintas.

**E7**

La rampa se mide en tramos iguales de longitud t. Un turno construye 5 tramos y deja 2 codos de remate; el siguiente construye 3 tramos y deja 4 codos. Si un tramo mide 9 codos, ¿cuánto mide la rampa en total?

Respuesta: `78`

Escalera de pistas:
1. Junta primero los tramos y aparte los codos de remate.
2. Queda 8t + 6.
3. 8 · 9 + 6 = …


### A9. Cierre

*¿Se juntan en un solo término?* — **Qué decide que dos cantidades se puedan sumar**

Estar sumados en la misma línea no basta. Lo único que decide es si la parte literal coincide entera.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Se suman los coeficientes y la x se conserva. |
|  | ✗ | No hay nada que sacar factor común: la suma se queda indicada. |
|  | ✗ | x² y x son cantidades distintas. Con x = 3 valen 27 y 6. |
|  | ✅ | Los términos sin letra son semejantes entre sí. Siempre se juntan. |
|  | ✅ | ab y ba son la misma parte literal: multiplicar es conmutativo (N3-M01). |
|  | ~ (ámbar) | Como suma no se acortan. Como producto sí: es la distributiva al revés, y de ahí sale toda la factorización. |

La regla cabe en una línea: se suman los coeficientes solo cuando la parte literal es idéntica. Y la última fila deja una puerta abierta — que dos términos no se junten sumando no significa que no se pueda hacer nada con ellos.

#### Pregunta de abstracción

¿Qué comparten los tres registros trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `same_literal` | En los tres hay que mirar la parte literal antes de operar | — |
| 　 | `coefficients` | En los tres solo cambian los coeficientes; la parte literal se conserva | — |
| 　 | `always_shorter` | En los tres el registro final tiene menos términos que el inicial | — |
| 　 | `one_term` | En los tres el resultado se puede escribir con un solo término | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos codos de lino salen en total?
¿Cuántos codos de lino salen en total?

Respuesta: `41`

Escalera de pistas:
1. Simplifica primero, sustituye después.
2. El registro simplificado es 4c + 13.
3. Con c = 7: 28 + 13 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otras cargas. Sin nota.

- **Mejoró:** Avance: ya compruebas la parte literal antes de sumar coeficientes.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué hace que dos términos sean semejantes.

**PD1**

Simplifica 5b + 2b y evalúa el resultado para b = 6.

Respuesta: `42`

**PD2**

¿Cuál es el resultado de $9n-4n$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `fiven` | $5n$ | — |
| 　 | `five` | $5$ | `pierde_la_parte_literal` |
| 　 | `thirteen` | $13n$ | `confunde_resta_con_suma` |

**PD3**

¿Se puede acortar $5a+2a^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: los exponentes son distintos | — |
| 　 | `yes` | Sí: $7a^{2}$ | `combina_no_semejantes` |
| 　 | `yes_a` | Sí: $7a$ | `combina_no_semejantes` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-O01-SEMEJANTES-D2` | `three` | `cuenta_simbolos_no_terminos` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-D2` | `one` | `no_separa_por_los_signos` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-D3` | `yes_sum` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-D3` | `yes_num` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E1` | `eightx2` | `suma_los_exponentes_al_sumar` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E1` | `fifteenx` | `confunde_suma_con_producto` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E1` | `eight` | `pierde_la_parte_literal` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E2` | `nosign` | `distribucion_parcial_del_signo` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E2` | `allsub` | `ignora_el_signo_de_resta` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E2` | `mixed` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E4` | `coef` | `habito_busca_el_error_donde_no_esta` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E4` | `like` | `habito_busca_el_error_donde_no_esta` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E4` | `none` | `distribucion_parcial_del_signo` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E5` | `true` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E5` | `true_if` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-E5` | `false_seven` | `reparte_el_coeficiente_a_todo` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-PD2` | `five` | `pierde_la_parte_literal` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-PD2` | `thirteen` | `confunde_resta_con_suma` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-PD3` | `yes` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |
| `ALG-N1-O01-SEMEJANTES-PD3` | `yes_a` | `combina_no_semejantes` | Compara la parte literal entera —letras y exponentes— antes de operar. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
