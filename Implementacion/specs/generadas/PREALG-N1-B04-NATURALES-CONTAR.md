# Nodo: Contar es ponerle número a un montón — PREALG-N1-B04-NATURALES-CONTAR

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B04-NATURALES-CONTAR` |
| `concept_slug` | `naturales` |
| Error focal | `cero_no_es_numero` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B03-ESCALERA-NECESIDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Primer peldaño · Naturales

**Título:** Contar es ponerle número a un montón

Este es el primer peldaño y el más engañoso, porque crees que ya lo sabes. Aquí vas a decidir qué cantidades se pueden contar, por qué el montón vacío también tiene número, y en qué momento contar deja de alcanzar.

**Escena:** Los números naturales son cero, uno, dos, tres y así sucesivamente

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

En una repisa hay 6 lámparas de aceite y en la de al lado hay 5. ¿Cuántas lámparas hay en total?

Respuesta: `11`

**D2**

Un cofre de ofrendas está completamente vacío. ¿Cuántas monedas tiene?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | Tiene 0 monedas | — |
| 　 | `none` | No tiene un número: simplemente no tiene nada | `cero_no_es_numero` |
| 　 | `cannot` | No se puede saber sin abrirlo | `habito_evita_decidir` |

**D3**

Tenías 3 cinceles y prestaste 5. ¿Cuántos te quedan?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `impossible` | No se puede: no tenías 5 para prestar | — |
| 　 | `two` | Quedan 2 | `resta_al_reves` |
| 　 | `zero` | Quedan 0 | `trunca_en_cero` |
| 　 | `minus_two` | Quedan −2 | `adelanta_enteros` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · El primer peldaño* — **El censo del ágora**

El arconte mandó contar todo lo que hay en el ágora antes del festival. KatIA recorre la plaza con una tablilla: 12 columnas en el pórtico, 9 puestos abiertos, 4 fuentes, 7 palomas en el tejado.

Llega al último puesto de la fila. El comerciante se fue de viaje y no queda nada: ni una jarra, ni un saco, ni un banco. KatIA levanta el cincel sobre la tablilla y se queda quieta, sin saber qué grabar.

**Pregunta:** ¿Qué debe grabar KatIA en la casilla de ese puesto?

**Intento genuino** (`acotado`): Escoge lo que harías tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Dejar la casilla en blanco: no hay nada que contar | — |
| 　 | `b` | Grabar un 0 | — |
| 　 | `c` | Tachar el puesto del censo | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos casillas del censo, dos problemas distintos**

Mira las dos casillas de abajo. En las dos KatIA no puede escribir un número «normal», pero por razones opuestas: una se resuelve hoy y la otra no cabe todavía en este peldaño.

- **Caso que se resuelve** — Sí hay número: el 0. Contar un montón vacío da cero, y cero es una respuesta, no un hueco. La casilla queda utilizable.
- **Caso que rompe la expectativa** — Aquí no hay ningún natural que sirva. No es que no sepamos: es que la respuesta no existe DENTRO de este conjunto.

**Resolución:** Fíjate en la diferencia. «Vacío» sí tiene número y ese número es 0. «Deber» no tiene número aquí, y por eso el siguiente peldaño tendrá que inventarlo. Cero no es la falta de número: es el número de la falta.

**Definición — Los números naturales**

$$\mathbb{N}=\{0,1,2,3,4,\ldots\}$$

La frase del nodo: contar es ponerle un número a un montón, y el montón vacío también tiene el suyo.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\mathbb{N}` | los naturales | de natural: los números con los que se cuenta |
| `0` | cero | el número del montón vacío; en este curso SÍ es natural |
| `\{\ \}` | llaves | encierran a los miembros del conjunto, uno por uno |
| `\ldots` | puntos suspensivos | sigue igual para siempre: no hay un último natural |
| `n\in\mathbb{N}` | n pertenece a ℕ | n es uno de esos números |
| `n+1` | el siguiente de n | cada natural tiene sucesor; por eso no se acaban |

### A5. Ejemplos resueltos

#### Las gradas del teatro · *resuelto*

Hay que anotar cuántas gradas tiene el teatro. KatIA cuenta 14 en el sector de arriba y 9 en el de abajo. ¿Cuántas gradas grabo en la tablilla?

- Compruebo que sean objetos completos: una grada no se cuenta por mitades.
- Cuento cada sector por separado: 14 arriba, 9 abajo.
- Junto los dos montones: 14 + 9.
- 14 + 9 = 23, y 23 es natural, así que cabe en el censo.
- Grabo 23 en la tablilla.

**Autoexplicación (focal):** {'step_index': 0, 'prompt': 'En el paso 1 comprobé que fueran objetos completos antes de contar. ¿Por qué ese chequeo va primero y no al final?'}

#### El puesto sin comerciante · *resuelto*

El puesto del comerciante que se fue de viaje no tiene ni una jarra. ¿Qué cantidad va en su casilla del censo?

- Miro el puesto y cuento lo que hay: no empiezo a contar porque no hay nada.
- Un montón sin objetos también tiene una cantidad: la cantidad es cero.
- Escribo 0, no dejo la casilla en blanco.
- Una casilla en blanco significa «no lo revisé»; un 0 significa «lo revisé y no había nada».
- El censo queda completo: 0 es un dato, el blanco es un vacío de información.

#### El censo con casillas en blanco · *TRAMPA*

Un escriba entregó su parte del censo así. Está mal: «Puse 0 solo donde sobraba algo y dejé en blanco los puestos vacíos, porque el 0 no es un número: es que no hay nada».

- Pregúntate qué información pierde el arconte con cada opción.
- Con el 0 sabe que ese puesto fue revisado y estaba vacío.
- Con el blanco no sabe si estaba vacío o si el escriba no llegó hasta allá.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\text{puesto vacío}\\ \\rightarrow\\ \\square', 'right_latex': '\\text{puesto vacío}\\ \\rightarrow\\ 0\\in\\mathbb{N}', 'rows': [{'wrong': '0 significa «no hay nada que decir»', 'right': '0 es la respuesta a «¿cuántos hay?»: ninguno'}, {'wrong': 'Un blanco y un 0 dicen lo mismo', 'right': 'El blanco dice «sin revisar»; el 0 dice «revisado, vacío»'}]}
**¿Por qué falla?:** ¿Por qué un 0 y una casilla en blanco no dicen lo mismo? Escribe qué debía grabar el escriba.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el conteo ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — En el pórtico hay 12 columnas de un lado y 12 del otro. Se derrumbaron 3.

- dado: $12+12=24$
- dado: $24-3$
- hueco `P1-b1`: $\text{Columnas en pie}=$ → `21`

**P2** (*falta: middle*) — El festival necesita 40 antorchas. Hay 3 repisas con 8 antorchas cada una y ninguna más.

- dado: $3\times8$
- hueco `P2-b1`: $\text{Antorchas disponibles}=$ → `24`
- hueco `P2-b2`: $\text{Faltan }40-24=$ → `16`

**P3** (*falta: statement_only*) — Solo el planteamiento: KatIA revisó 9 puestos. En 5 había mercancía y los otros 4 estaban vacíos. ¿Cuántas casillas del censo llevan un número escrito?

- hueco `P3-b1`: $\text{Casillas con número}=$ → `9`


### A7. Comparación de métodos

**Dos caminos para el mismo total**

En el almacén del festival hay 6 estantes y cada uno guarda 4 jarras. ¿Cuántas jarras hay? Las dos soluciones de abajo son correctas.

- **Método 1 · Contar una por una** — 
- **Método 2 · Agrupar y multiplicar** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si un estante tiene 4 jarras y otro tiene 3?

**Insight:** El segundo método falla en cuanto los grupos son desiguales, y ese fracaso es el contenido: multiplicar es contar grupos IGUALES, no un atajo universal. Lo vas a volver a ver cuando la multiplicación se defina en serio (N2-E03).

### A8. Práctica independiente (7 ítems)

**E1**

En el taller hay 17 sacos de trigo y llegan 8 más en la carreta. ¿Cuántos sacos quedan en el taller?

Respuesta: `25`

Escalera de pistas:
1. ¿Los sacos que llegan se suman o se restan?
2. Junta los dos montones: los que había y los que llegaron.
3. 17 + 8: primero 17 + 3 = 20, y quedan 5 más.

**E2**

Se reparten 5 filas de bancos con 7 bancos cada una. ¿Cuántos bancos hay?

Respuesta: `35`

Escalera de pistas:
1. Todas las filas tienen el mismo tamaño: ¿puedes agrupar?
2. Contar 5 grupos de 7 es multiplicar.
3. 5 × 7 = 35.

**E3**

¿Cuál de estas cantidades NO se puede escribir con un número natural?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `half` | Media jarra de aceite | — |
| 　 | `zero_doves` | Ninguna paloma en el tejado | `cero_no_es_numero` |
| 　 | `twelve` | Doce columnas | `confunde_tamano_con_tipo` |
| 　 | `hundred` | Cien escalones | `confunde_tamano_con_tipo` |

Escalera de pistas:
1. ¿Cuál de las cuatro habla de una parte y no de un objeto completo?
2. Los naturales cuentan cosas enteras: 1 jarra, 2 jarras, 3 jarras.
3. Media jarra cae ENTRE 0 y 1: no hay natural ahí.

**E4**

Un escriba anotó: «Había 9 palomas, volaron 4, quedan 5. Y como en el otro tejado no quedó ninguna, dejé esa casilla vacía». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `blank` | Debió grabar 0 en la casilla del otro tejado | — |
| 　 | `subtraction` | Restó mal: 9 − 4 no da 5 | `duda_del_calculo_correcto` |
| 　 | `should_add` | Debió sumar las que volaron, no restarlas | `confunde_operacion` |
| 　 | `none` | Ningún error, está bien | `cero_no_es_numero` |

Escalera de pistas:
1. La cuenta 9 − 4 está bien. Mira la segunda frase.
2. «No quedó ninguna» es una cantidad, y las cantidades se escriben.
3. Ninguna paloma = 0 palomas, y 0 va grabado en la tablilla.

**E5**

¿Es verdadera o falsa? $0\in\mathbb{N}$ y además $0$ cuenta algo.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true_counts` | Verdadera: 0 es natural y cuenta el montón vacío | — |
| 　 | `false_nothing` | Falsa: 0 no es un número, es que no hay nada | `cero_no_es_numero` |
| 　 | `false_starts_one` | Falsa: los naturales empiezan en 1 | `convencion_sin_cero` |
| 　 | `true_but_empty` | Verdadera que es natural, pero 0 no cuenta nada | `cero_no_es_numero` |

Escalera de pistas:
1. Si el 0 no fuera un número, ¿cómo escribirías el resultado del censo del puesto vacío?
2. «Ninguno» es una respuesta a «¿cuántos hay?», y las respuestas a esa pregunta son naturales.
3. En este curso ℕ = {0, 1, 2, 3, …}: el 0 entra, y cuenta el montón vacío.

**E6**

El arconte pide que el censo permita sumar y restar libremente. KatIA solo tiene naturales. ¿Qué encargo NO va a poder cumplir?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `debt` | Anotar cuánto DEBE un puesto que gastó más de lo que tenía | — |
| 　 | `total` | Sumar todos los puestos para dar un total | `cree_naturales_insuficientes_para_sumar` |
| 　 | `empty` | Registrar un puesto vacío | `cero_no_es_numero` |
| 　 | `compare` | Decir cuál puesto tiene más mercancía | `cree_naturales_no_ordenados` |

Escalera de pistas:
1. Tres de los cuatro encargos ya los resolviste en este nodo.
2. Piensa en el discípulo que prestó 5 cinceles teniendo 3.
3. Deber lleva a un resultado por debajo de 0, y ahí no hay naturales.

**E7**

¿Cuál de estas restas SÍ tiene resultado dentro de los naturales?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | 20 − 20 | — |
| 　 | `neg_small` | 7 − 9 | `resta_siempre_cabe` |
| 　 | `neg_big` | 1 − 100 | `resta_siempre_cabe` |
| 　 | `neg_one` | 0 − 1 | `resta_siempre_cabe` |

Escalera de pistas:
1. Haz cada resta y mira si el resultado está en {0, 1, 2, 3, …}.
2. Si el número de la izquierda es menor, te vas por debajo del 0.
3. 20 − 20 = 0, y 0 sí es natural. Las otras tres se salen.


### A9. Cierre

*La escalera de la necesidad* — **¿Toda resta de dos números del conjunto vive en el conjunto?**

Cada peldaño nace de una operación que no cabía en el anterior. Este es el primero.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Se sale: no hay natural por debajo del 0. |
|  | ✅ | El siguiente peldaño nace exactamente de esto. |

Sumar y multiplicar naturales siempre da un natural. Restar, no. Ese único agujero es el que abre B05: los enteros no se inventaron por gusto, se inventaron para que la resta siempre tenga respuesta.

#### Pregunta de abstracción

¿Qué tienen en común los tres momentos en que KatIA no pudo grabar un natural?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `below_zero` | En los tres el resultado queda por debajo de 0 | — |
| 　 | `subtraction` | Los tres son restas donde se quita más de lo que hay | — |
| 　 | `zero` | Los tres tienen que ver con que el 0 no es natural | — |
| 　 | `big` | Los tres usan números demasiado grandes | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas antorchas faltan?
¿Cuántas antorchas faltan?

Respuesta: `14`

Escalera de pistas:
1. Primero averigua cuántas antorchas hay en total.
2. 4 repisas de 9, más una repisa que aporta 0.
3. Hay 36. Ahora resta: 50 − 36.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre «cero» y «casilla en blanco».

**PD1**

En una repisa hay 7 lámparas y en la de al lado hay 6. ¿Cuántas hay en total?

Respuesta: `13`

**PD2**

Un anaquel quedó sin una sola jarra. ¿Qué se anota en su casilla?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | Se anota 0 | — |
| 　 | `blank` | Se deja en blanco | `cero_no_es_numero` |
| 　 | `dash` | Se pone una raya para indicar que no aplica | `cero_no_es_numero` |

**PD3**

¿Cuál de estas operaciones SIEMPRE da un natural si empiezas con naturales?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | Sumar | — |
| 　 | `sub` | Restar | `confunde_operacion` |
| 　 | `both` | Las dos | `resta_siempre_cabe` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B04-NATURALES-CONTAR-D2` | `none` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-D2` | `cannot` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-D3` | `two` | `resta_al_reves` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-D3` | `zero` | `trunca_en_cero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-D3` | `minus_two` | `adelanta_enteros` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E3` | `zero_doves` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E3` | `twelve` | `confunde_tamano_con_tipo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E3` | `hundred` | `confunde_tamano_con_tipo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E4` | `subtraction` | `duda_del_calculo_correcto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E4` | `should_add` | `confunde_operacion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E4` | `none` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E5` | `false_nothing` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E5` | `false_starts_one` | `convencion_sin_cero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E5` | `true_but_empty` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E6` | `total` | `cree_naturales_insuficientes_para_sumar` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E6` | `empty` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E6` | `compare` | `cree_naturales_no_ordenados` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E7` | `neg_small` | `resta_siempre_cabe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E7` | `neg_big` | `resta_siempre_cabe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-E7` | `neg_one` | `resta_siempre_cabe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-PD2` | `blank` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-PD2` | `dash` | `cero_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-PD3` | `sub` | `confunde_operacion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B04-NATURALES-CONTAR-PD3` | `both` | `resta_siempre_cabe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b04-naturales-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
