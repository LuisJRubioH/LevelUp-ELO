# Nodo: Una letra no nombra la cosa: cuenta cuántas hay — ALG-N1-L01-VARIABLES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-L01-VARIABLES` |
| `concept_slug` | `variables` |
| Error focal | `variable_como_etiqueta` |
| Sala / edificio | La sala de los cálamos |
| Guía | Meritka |
| Entra después de | `ALG-A00-PAPIRO-CUATRO-CASAS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La sala de los cálamos · Variables

**Título:** Una letra no nombra la cosa: cuenta cuántas hay

Hasta ahora cada registro servía para un solo día. Aquí aprendes a escribir uno que sirva para todos: una regla que no necesita saber de antemano cuántos trabajadores llegarán.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar. No se califican: solo quiero ver desde dónde partimos.

**D1**

Cada escriba recibe 3 panes. ¿Cuántos panes se necesitan para 4 escribas?

Respuesta: `12`

**D2**

¿Cuánto vale $2\cdot(3+4)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `fourteen` | 14 | — |
| 　 | `ten` | 10 | `multiplica_solo_el_primer_sumando` |
| 　 | `twentyfour` | 24 | `pega_los_digitos_en_vez_de_operar` |

**D3**

El número de trabajadores cambia cada día. ¿Qué usarías para escribir UNA regla que sirva para cualquier día?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `letter` | Un símbolo que ocupe el lugar de esa cantidad | — |
| 　 | `many` | Un registro distinto para cada día | `no_generaliza_enumera` |
| 　 | `blank` | Dejar el espacio en blanco y rellenarlo a mano | `no_generaliza_enumera` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la Casa de la Vida* — **El papiro que se repetía a sí mismo**

Meritka abre un estante entero de registros. En cada rollo está escrita la misma instrucción: «tres panes por trabajador». Solo cambia el número del final: veintiuno un día, treinta el siguiente, dieciocho el otro.

«Un rollo por día», dice Meritka. «Y el rollo que se perdió con la crecida era el único que no tenía número: el que servía para todos. Ese es el que hay que volver a escribir, y no sé cómo se escribe una cantidad que todavía no ha llegado.»

**Pregunta:** ¿Cómo se escribe una regla cuando aún no sabes la cantidad?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Escribiendo todos los casos posibles | — |
| 　 | `b` | Dejando un hueco en blanco | — |
| 　 | `c` | Poniendo un símbolo en el lugar de la cantidad | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos registros para la misma instrucción**

Los dos dicen «tres panes por trabajador». Fíjate en cuál de los dos sigue sirviendo mañana.

- **El registro de ayer** — Exacto y verdadero. Pero mañana no llegan cuatro, y el rollo ya no vale.
- **El rollo perdido** — Un solo rollo cubre todos los días. La n espera a que le digan cuánto vale.

**Resolución:** La letra no abrevia la palabra «trabajador»: ocupa el lugar del NÚMERO de trabajadores. Por eso 3n se puede calcular en cuanto alguien diga cuántos llegaron, y por eso el mismo rollo sirve para todos los días del año.

**Definición — Variable, término y expresión**

$$3n \;=\; \underbrace{3}_{\text{coeficiente}}\cdot\underbrace{n}_{\text{variable}}$$

Una VARIABLE es un símbolo que ocupa el lugar de un número: uno que cambia o uno que todavía no conocemos. Una CONSTANTE es un valor que no cambia. Un TÉRMINO es cada parte separada por + o por −, y una EXPRESIÓN ALGEBRAICA combina números, variables y operaciones sin afirmar todavía ninguna igualdad.

| Símbolo | Se lee | Significa |
|---|---|---|
| `n` | ene | la variable: el número de trabajadores, no la palabra «trabajador» |
| `3n` | tres ene | quiere decir 3 · n, un producto — nunca 3 + n |
| `3` | tres | el coeficiente: el número que multiplica a la variable |
| `2c+1` | dos ce más uno | dos términos; el 1 es una constante, no lleva letra |
| `n\in\mathbb{N},\ n>0` | ene natural positivo | en este registro n cuenta personas: no admite 2,5 ni −3 |

### A5. Ejemplos resueltos

#### Cuando parte de la cantidad sí se conoce · *resuelto*

Cada estante de la sala guarda la misma cantidad de rollos, que varía según el estante, y además hay 2 rollos de consulta fuera del estante. Escribe cuántos rollos hay en total por estante.

- Lo que cambia de un estante a otro: la cantidad de rollos guardados. La llamo r.
- Lo que no cambia: los 2 rollos de consulta. Ese 2 es una constante.
- Los junto con una suma, porque hay que contarlos todos: r + 2.
- Compruebo con un caso: si el estante guarda 9 rollos, r = 9 y el total es 11.
- La expresión tiene dos términos: r y 2. El primero lleva letra; el segundo no.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué el 2 no lleva letra y la otra cantidad sí?'}

#### Un coeficiente y una constante en la misma regla · *resuelto*

Cada copista gasta 2 medidas de tinta en su jornada, y aparte se reserva 1 medida para corregir los errores del día. Escribe la tinta que hay que preparar.

- La cantidad que cambia es el número de copistas: la llamo c.
- Cada uno gasta 2 medidas, así que ese gasto es 2 · c, que se escribe 2c.
- La medida de correcciones es siempre 1, llegue quien llegue: es constante.
- Total: 2c + 1. El 2 es el coeficiente de c; el 1 es el término constante.
- Compruebo: con 6 copistas hacen falta 2 · 6 + 1 = 13 medidas.

#### El aprendiz que leyó la letra como una palabra · *TRAMPA*

Un aprendiz lee el registro y explica: «2c son dos copistas, porque la c es de copista. Y r + 2 son un rollo y dos rollos, o sea tres rollos».

- Prueba a sustituir: si c = 7, entonces 2c = 14 medidas. La lectura del aprendiz no permite sustituir nada.
- En r + 2, la r no vale 1: vale lo que se cuente en ese estante. Con r = 9 el total es 11.
- Regla para no volver a caer: antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?».

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '2c=\\text{dos copistas}', 'right_latex': 'c=7\\Rightarrow 2c=14', 'rows': [{'wrong': 'La c abrevia la palabra «copista»', 'right': 'La c es CUÁNTOS copistas hay: un número'}, {'wrong': 'En r + 2 la r vale 1 porque es un rollo', 'right': 'La r vale lo que valga ese estante; no se sabe hasta que se cuenta'}]}
**¿Por qué falla?:** Explica por qué la letra no funciona como abreviatura y di cuánto valen 2c y r + 2 si hay 7 copistas y el estante guarda 9 rollos.


### A6. Puente — parcialmente resueltos

La regla ya va empezada; completa los huecos.

**P1** (*falta: last*) — Cada escriba recibe 5 medidas de papiro. Si hay s escribas, la expresión es 5s. ¿Cuántas medidas hacen falta si llegan 8 escribas?

- dado: $5s\quad\text{con } s=8$
- dado: $5\cdot 8$
- hueco `P1-b1`: $5s=$ → `40`

**P2** (*falta: middle*) — En la sala hay 4 lámparas fijas y una lámpara más por cada mesa. Con m mesas, la expresión es m + 4. Complétala para 6 mesas.

- dado: $m+4\quad\text{con } m=6$
- hueco `P2-b1`: $m=$ → `6`
- hueco `P2-b2`: $m+4=$ → `10`

**P3** (*falta: statement_only*) — Solo el planteamiento: la sala tiene el doble de lámparas que de mesas, y además 3 lámparas en la entrada. Si hay 7 mesas, ¿cuántas lámparas hay?

- hueco `P3-b1`: $2m+3=$ → `17`


### A7. Comparación de métodos

**Dos maneras de comprobar una traducción**

«El triple de un número, menos 4». Las dos comprobaciones de abajo son correctas y llevan a la misma expresión.

- **Método 1 · Leer la frase por partes** — 
- **Método 2 · Probar con un número** — 

**Pregunta:** ¿Cuál de los dos te salva cuando la frase dice «el doble de la suma de un número y 3»?

**Insight:** El segundo. Leer por partes daría 2x + 3, pero al probar con x = 5 la frase da 16 y 2x + 3 da 13: no coinciden, así que hace falta el paréntesis, 2(x+3). Y fíjate en lo que exige sustituir: tratar la letra como un número. Si la lees como una palabra, este método no se puede ni empezar.

### A8. Práctica independiente (7 ítems)

**E1**

«El doble de un número, más 3». ¿Qué expresión lo dice?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `correct` | $2x+3$ | — |
| 　 | `grouped` | $2(x+3)$ | `agrupa_lo_que_la_frase_no_agrupa` |
| 　 | `swapped` | $3x+2$ | `invierte_coeficiente_y_constante` |
| 　 | `product` | $2x\cdot 3$ | `confunde_mas_con_por` |

Escalera de pistas:
1. ¿Qué se duplica: el número solo, o el número ya sumado con 3?
2. La frase dobla primero y suma después. El paréntesis haría lo contrario.
3. El doble de x es 2x. Ahora añádele 3.

**E2**

En la expresión $5m-4$, ¿cuál es el coeficiente?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `five` | 5 | — |
| 　 | `minusfour` | −4 | `confunde_coeficiente_con_constante` |
| 　 | `m` | m | `confunde_coeficiente_con_variable` |
| 　 | `four` | 4 | `confunde_coeficiente_con_constante` |

Escalera de pistas:
1. El coeficiente es el número que MULTIPLICA a una letra.
2. El −4 no multiplica a nada: está sumado (restado) aparte.
3. ¿Qué número está pegado a la m?

**E3**

La tinta de la jornada se calcula con 2c + 1, donde c es el número de copistas. ¿Cuántas medidas hacen falta si vienen 6 copistas?

Respuesta: `13`

Escalera de pistas:
1. Sustituye c por 6 y calcula.
2. Primero el producto 2 · 6, después la suma.
3. 12 + 1 = …

**E4**

Para «el triple de un número» un escriba anota 3 + x. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum_vs_product` | «Triple» es multiplicar por 3, no sumar 3: se escribe 3x | — |
| 　 | `order` | Está bien el signo, solo cambió el orden: debería ser x + 3 | `confunde_mas_con_por` |
| 　 | `letter` | El error es la letra: debería usar t de «triple» | `variable_como_etiqueta` |
| 　 | `none` | No hay error, 3 + x es el triple de x | `confunde_mas_con_por` |

Escalera de pistas:
1. Prueba con un número: el triple de 10, ¿es 13?
2. Triplicar es repetir tres veces, y repetir es multiplicar.
3. El triple de x se escribe 3 · x, es decir 3x.

**E5**

En el registro $4t$, la $t$ está por «tablilla». ¿Qué representa exactamente la $t$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `count` | El número de tablillas, una cantidad que puede cambiar | — |
| 　 | `label` | La palabra «tablilla»: 4t son cuatro tablillas | `variable_como_etiqueta` |
| 　 | `unit` | La unidad de medida en que se cuentan las tablillas | `variable_como_etiqueta` |
| 　 | `fixed` | Un número fijo que ya está decidido de antemano | `confunde_variable_con_constante` |

Escalera de pistas:
1. Pregúntate «¿cuántos?», no «¿qué cosa?».
2. Si la t fuera la palabra, no podrías calcular 4t nunca.
3. Con 9 tablillas, t = 9 y 4t = 36. La letra guarda el número.

**E6**

Selecciona TODAS las que son expresiones algebraicas (no ecuaciones).

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $3x+5$ | — |
| 　 | `b` | $2x+3=7$ | — |
| ✅ | `c` | $r-2$ | — |
| 　 | `d` | $A=b\cdot h$ | — |

Escalera de pistas:
1. Una expresión describe una cantidad; una ecuación AFIRMA una igualdad.
2. Busca el signo igual: si está, ya no es solo una expresión.
3. 3x + 5 y r − 2 no afirman nada; las otras dos sí.

**E7**

Un rollo de papiro mide L codos. Antes de escribirlo se recorta un borde de 2 codos en cada extremo. Si el rollo medía 15 codos, ¿cuántos codos quedan para escribir?

Respuesta: `11`

Escalera de pistas:
1. Se recorta en los DOS extremos: ¿cuánto se pierde en total?
2. La expresión es L − 4, no L − 2.
3. 15 − 4 = …


### A9. Cierre

*¿Cambia o no cambia?* — **Qué guarda cada símbolo de una expresión**

Ser una letra no convierte a un símbolo en variable, y ser un número no lo convierte en constante. Lo que decide es si su valor puede cambiar.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Cambia cada día. Es justo lo que el rollo perdido no podía fijar. |
|  | ✗ | Siempre tres panes por trabajador. Multiplica a la variable, pero no varía. |
|  | ✗ | Los dos rollos de consulta están siempre, haya los que haya en el estante. |
|  | ✗ | Es letra y aun así es constante. Aquí la que cambia es la r. |
|  | ~ (ámbar) | No cambia libremente: hay un único valor que hace cierta la igualdad, y aún no lo sabemos. |
|  | ✅ | Cambian con cada rectángulo, y A cambia con ellas. |

La pregunta útil nunca es «¿es letra o es número?», sino «¿su valor puede cambiar?». Una constante puede escribirse con letra (π) y una incógnita es un caso intermedio: fija, pero todavía desconocida.

#### Pregunta de abstracción

¿Qué comparten las tres expresiones trabajadas en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `part_changes` | En las tres hay una parte que cambia y otra que se queda fija | — |
| 　 | `computable` | En las tres se puede calcular el total en cuanto se sabe el valor de la letra | — |
| 　 | `equal` | En las tres se afirma una igualdad entre dos cantidades | — |
| 　 | `initial` | En las tres la letra es la inicial de la palabra que representa | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas medidas hay que sacar?
¿Cuántas medidas hay que sacar?

Respuesta: `41`

Escalera de pistas:
1. Escribe primero la regla con letra, y sustituye al final.
2. 3e + 5, con e = 12.
3. 36 + 5 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros datos. Sin nota.

- **Mejoró:** Avance: ya lees la letra como una cantidad y no como una palabra.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué guarda una letra dentro de una expresión.

**PD1**

Cada estante guarda 6 rollos. ¿Cuántos rollos hay en 5 estantes iguales?

Respuesta: `30`

**PD2**

Si $p$ es el número de panes, ¿qué significa $4p$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `quadruple` | Cuatro veces esa cantidad de panes | — |
| 　 | `four_breads` | Cuatro panes | `variable_como_etiqueta` |
| 　 | `sum` | Cuatro más esa cantidad de panes | `confunde_mas_con_por` |

**PD3**

En $7k+2$, ¿cuál es el término constante?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | 2 | — |
| 　 | `seven` | 7 | `confunde_coeficiente_con_constante` |
| 　 | `k` | k | `confunde_coeficiente_con_variable` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-L01-VARIABLES-D2` | `ten` | `multiplica_solo_el_primer_sumando` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-D2` | `twentyfour` | `pega_los_digitos_en_vez_de_operar` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-D3` | `many` | `no_generaliza_enumera` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-D3` | `blank` | `no_generaliza_enumera` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E1` | `grouped` | `agrupa_lo_que_la_frase_no_agrupa` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E1` | `swapped` | `invierte_coeficiente_y_constante` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E1` | `product` | `confunde_mas_con_por` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E2` | `minusfour` | `confunde_coeficiente_con_constante` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E2` | `m` | `confunde_coeficiente_con_variable` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E2` | `four` | `confunde_coeficiente_con_constante` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E4` | `order` | `confunde_mas_con_por` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E4` | `letter` | `variable_como_etiqueta` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E4` | `none` | `confunde_mas_con_por` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E5` | `label` | `variable_como_etiqueta` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E5` | `unit` | `variable_como_etiqueta` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-E5` | `fixed` | `confunde_variable_con_constante` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-PD2` | `four_breads` | `variable_como_etiqueta` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-PD2` | `sum` | `confunde_mas_con_por` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-PD3` | `seven` | `confunde_coeficiente_con_constante` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |
| `ALG-N1-L01-VARIABLES-PD3` | `k` | `confunde_coeficiente_con_variable` | Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?». |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
