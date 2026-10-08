# Nodo: La que se da la vuelta es la de la derecha — ALG-N1-F04-DIVISION

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-F04-DIVISION` |
| `concept_slug` | `division_de_fracciones_algebraicas` |
| Error focal | `invierte_la_primera_fraccion` |
| Sala / edificio | El silo de simiente |
| Guía | Tabiry |
| Entra después de | `ALG-N1-F03-PRODUCTO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El silo de simiente · División de fracciones

**Título:** La que se da la vuelta es la de la derecha

En la era tomabas una parte de otra parte y el resultado salía más pequeño. Aquí pasa lo contrario y el registro se escribe casi igual — con una diferencia de una sola fracción, que es justo donde se equivoca todo el mundo.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el silo. Sin nota.

**D1**

¿Cuántas medias medidas caben en 3 medidas?

Respuesta: `6`

**D2**

¿Cuánto es $\dfrac{1}{2}\div\dfrac{1}{4}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | 2 | — |
| 　 | `eighth` | $\dfrac{1}{8}$ | `multiplica_en_vez_de_dividir` |
| 　 | `half` | $\dfrac{1}{2}$ | `invierte_la_primera_fraccion` |

**D3**

Al dividir dos fracciones, ¿a cuál de las dos se le da la vuelta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `second` | A la segunda, la que dice entre cuánto | — |
| 　 | `first` | A la primera | `invierte_la_primera_fraccion` |
| 　 | `both` | A las dos | `invierte_la_primera_fraccion` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el silo de simiente* — **El silo lleno que no daba ni para un saco**

El silo guarda la simiente de la próxima sementera. Se saca en sacos, y cada saco lleva dos tercios de medida.

Tabiry señala el registro:

«Hay ocho medidas de simiente. La pregunta es cuántos sacos salen. El escriba escribió la división, se acordó de que había que dar la vuelta a una fracción y le dio la vuelta a la de la izquierda. Le salió un doceavo de saco.»

«Con el silo lleno hasta arriba, su tablilla decía que no llegaba ni para un saco. Y la sementera empieza pasado mañana.»

**Pregunta:** Al dividir entre una fracción, ¿cuál de las dos se da la vuelta, y por qué esa?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | La primera, que es la que se está repartiendo | — |
| 　 | `b` | La segunda, que es la que dice entre cuánto se reparte | — |
| 　 | `c` | Da igual: el resultado sale el mismo | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dividir no siempre achica**

La pregunta que hay detrás de toda división es «¿cuántos de estos caben?».

- **Entre un entero** — Cada saco se lleva 2 medidas. El resultado es menor que 6.
- **Entre una fracción** — En cada medida caben 3 tercios, así que salen 18 sacos. El resultado CRECE.

**Resolución:** Dividir entre algo menor que 1 da un resultado mayor, porque caben muchos. Esa es la razón de dar la vuelta al divisor: preguntar «¿cuántos tercios caben en 6?» es lo mismo que preguntar «¿cuánto son 6 veces 3?». La fracción que se invierte es la que dice el tamaño del saco, no la que dice cuánta simiente hay.

**Definición — División de fracciones algebraicas**

$$\dfrac{a}{b}\div\dfrac{c}{d}=\dfrac{a}{b}\cdot\dfrac{d}{c}$$

Para DIVIDIR una fracción entre otra se multiplica la primera por el RECÍPROCO de la segunda: se deja la de la izquierda como está y se da la vuelta a la de la derecha. Un número entero se divide igual, viéndolo antes como fracción con 1 debajo. A partir de ahí es un producto, con todo lo que ya sabes de la era: se puede simplificar antes de multiplicar.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{a}{b}\div\dfrac{c}{d}=\dfrac{a}{b}\cdot\dfrac{d}{c}` | la regla entera | la de la derecha se invierte |
| `\dfrac{d}{c}` | recíproco | la misma fracción del revés |
| `8=\dfrac{8}{1}` | un entero también divide | todo número lleva un 1 debajo |
| `6\div\dfrac{1}{3}=18` | dividir puede agrandar | entre algo menor que 1, el resultado crece |
| `\dfrac{c}{d}\cdot\dfrac{d}{c}=1` | por qué funciona | una fracción por su recíproco deshace la división |

### A5. Ejemplos resueltos

#### Un entero entre una fracción · *resuelto*

Hay 8 medidas de simiente y cada saco lleva dos tercios de medida. ¿Cuántos sacos salen?

- Escribo el 8 como fracción: 8/1. Así las dos tienen la misma forma.
- Dejo la primera y doy la vuelta a la segunda: 8/1 · 3/2.
- Multiplico arriba con arriba y abajo con abajo: 24/2.
- Queda 12 sacos.
- Compruebo el sentido: los sacos son más pequeños que una medida, así que tienen que salir MÁS de 8 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué se invierte la del saco y no la de la simiente?'}

#### Con letras, y simplificando antes · *resuelto*

Del silo salen 3/x medidas por sembradura y cada saco lleva 6/x² medidas. ¿Cuántos sacos salen por sembradura?

- Doy la vuelta a la de la derecha: 3/x · x²/6.
- Ahora es un producto, así que puedo simplificar antes de multiplicar.
- La x de abajo se empareja con una de las dos x de arriba: queda 3·x / 6.
- 3 y 6 se dividen entre 3: queda x/2.
- Compruebo con x = 4: 3/4 ÷ 6/16 = 3/4 · 16/6 = 2, y 4/2 = 2 ✓.

#### El escriba que dio la vuelta a la de la izquierda · *TRAMPA*

Vuelve el registro de la apertura: 8 medidas en sacos de dos tercios. El escriba escribió 1/8 · 2/3 y anotó un doceavo de saco.

- Cada saco es menor que una medida, así que en 8 medidas caben más de 8 sacos.
- Cualquier resultado por debajo de 8 delata el error, y un doceavo lo delata a gritos.
- Regla para no volver a caer: señala con el dedo el divisor —lo que va después del signo— y da la vuelta solo a eso.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '8\\div\\dfrac{2}{3}=\\dfrac{1}{8}\\cdot\\dfrac{2}{3}', 'right_latex': '8\\div\\dfrac{2}{3}=\\dfrac{8}{1}\\cdot\\dfrac{3}{2}=12', 'rows': [{'wrong': 'Se invierte la primera', 'right': 'Se invierte el divisor, que es la segunda'}, {'wrong': '\\dfrac{1}{12}\\ \\text{de saco con el silo lleno}', 'right': '12\\ \\text{sacos, más que las 8 medidas ✓}'}]}
**¿Por qué falla?:** Explica por qué el resultado tenía que ser MAYOR que 8, y usa eso para descartar un doceavo sin rehacer la cuenta.


### A6. Puente — parcialmente resueltos

El registro del silo va empezado; completa los huecos.

**P1** (*falta: last*) — Calcula $\dfrac{3}{4}\div\dfrac{1}{2}$.

- dado: $\dfrac{3}{4}\cdot\dfrac{2}{1}$
- dado: $\dfrac{6}{4}$
- hueco `P1-b1`: $\dfrac{6}{4}=\dfrac{3}{\;?\;},\quad ?=$ → `2`

**P2** (*falta: middle*) — Calcula $12\div\dfrac{3}{5}$.

- dado: $\dfrac{12}{1}\cdot\dfrac{5}{3}$
- hueco `P2-b1`: $12\cdot 5=$ → `60`
- hueco `P2-b2`: $60\div 3=$ → `20`

**P3** (*falta: statement_only*) — Solo el planteamiento: hay 15 medidas de simiente y cada saco lleva tres cuartos de medida. ¿Cuántos sacos salen?

- hueco `P3-b1`: $15\div\dfrac{3}{4}=$ → `20`


### A7. Comparación de métodos

**Dos maneras de dividir entre una fracción**

$6\div\dfrac{3}{4}$. Una aplica la regla; la otra pregunta qué significa.

- **Método 1 · Invertir y multiplicar** — 
- **Método 2 · Preguntar cuántos caben** — 

**Pregunta:** ¿Cuál de los dos habría salvado al escriba del silo?

**Insight:** El segundo, y no porque el primero esté mal: el primero es más rápido y es el que acabarás usando. El problema es que la regla «se invierte una» no dice cuál, y aplicada al revés da un número que parece una respuesta. Preguntar «¿cuántos caben?» fija de antemano si el resultado debe crecer o menguar, y eso convierte el método 2 en la comprobación del método 1.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto es $\dfrac{2}{3}\div\dfrac{4}{9}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $\dfrac{3}{2}$ | — |
| 　 | `first` | $\dfrac{2}{3}$ | `invierte_la_primera_fraccion` |
| 　 | `mult` | $\dfrac{8}{27}$ | `multiplica_en_vez_de_dividir` |
| 　 | `swap` | Invirtiendo las dos: $\dfrac{27}{8}$ | `invierte_las_dos_fracciones` |

Escalera de pistas:
1. Deja la de la izquierda y da la vuelta a la de la derecha.
2. Queda 2/3 · 9/4.
3. 18/12 se simplifica entre 6.

**E2**

Hay 10 medidas de simiente y cada saco lleva dos quintos de medida. ¿Cuántos sacos salen?

Respuesta: `25`

Escalera de pistas:
1. El 10 es 10/1.
2. Invierte el saco: 10/1 · 5/2.
3. 50 ÷ 2 = …

**E3**

Calcula $\dfrac{5}{6}\div\dfrac{2}{3}$ y escribe el resultado como fracción simplificada, así: 5/12. No dejes espacios.

Respuesta: `5/4`

Escalera de pistas:
1. Invierte la segunda: 5/6 · 3/2.
2. Queda 15/12.
3. 15 y 12 se dividen los dos entre 3.

**E4**

Un escriba calcula $9\div\dfrac{3}{4}$ y anota $\dfrac{1}{12}$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `first` | Invirtió el 9 en vez del saco: es $9\cdot\dfrac{4}{3}=12$ | — |
| 　 | `mult` | Multiplicó sin invertir nada | `multiplica_en_vez_de_dividir` |
| 　 | `simp` | Olvidó simplificar el resultado | `habito_deja_el_resultado_sin_simplificar` |
| 　 | `none` | No hay error | `invierte_la_primera_fraccion` |

Escalera de pistas:
1. Los sacos son menores que una medida.
2. Con 9 medidas tienen que salir más de 9 sacos.
3. Un doceavo no llega ni a un saco.

**E5**

¿Verdadera o falsa? «Al dividir dos fracciones se da la vuelta a la primera y se multiplica.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: se da la vuelta a la segunda — $\dfrac{1}{2}\div\dfrac{1}{4}=2$ | — |
| 　 | `true` | Verdadera: la primera es la que se reparte | `invierte_la_primera_fraccion` |
| 　 | `true_either` | Verdadera: da igual cuál, el resultado sale el mismo | `invierte_la_primera_fraccion` |
| 　 | `false_both` | Falsa: hay que dar la vuelta a las dos | `invierte_la_primera_fraccion` |

Escalera de pistas:
1. Prueba con 1/2 ÷ 1/4 contando cuántos cuartos caben en un medio.
2. Caben 2.
3. Invirtiendo la primera saldría 1/2, que tampoco es lo que se cuenta.

**E6**

Selecciona TODAS las divisiones cuyo resultado es MAYOR que la primera fracción.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $6\div\dfrac{1}{3}$ | — |
| 　 | `b` | $6\div 3$ | — |
| ✅ | `c` | $\dfrac{1}{2}\div\dfrac{1}{4}$ | — |
| 　 | `d` | $\dfrac{1}{2}\div 4$ | — |

Escalera de pistas:
1. Mira si el divisor es menor o mayor que 1.
2. Entre algo menor que 1, el resultado crece.
3. Entre algo mayor que 1, mengua.

**E7**

El silo guarda 3s medidas de simiente y cada saco lleva s/4 medidas. Con s = 6, ¿cuántos sacos salen?

Respuesta: `12`

Escalera de pistas:
1. Invierte el saco: 3s · 4/s.
2. La s se cancela: quedan 12 sacos.
3. El resultado no depende de s.


### A9. Cierre

*¿Se da la vuelta al divisor?* — **Qué fracción se invierte y qué le pasa al resultado**

La regla es una sola y se falla siempre por el mismo sitio: no por olvidarla, sino por aplicarla a la fracción de al lado.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Se invierte el saco, no la simiente. El resultado crece. Es el caso focal. |
|  | ✅ | La de la izquierda se queda quieta. Después es un producto normal. |
|  | ✅ | Una vez invertida, se puede simplificar antes de multiplicar, como en la era. |
|  | ~ (ámbar) | Se invierte igual, pero primero hay que ver el 4 como 4/1. Aquí el resultado mengua. |
|  | ~ (ámbar) | Se invierte igual y da 1, ni crece ni mengua. Sirve para comprobar que invertiste la correcta. |
|  | ✗ | Aquí no se invierte nada. La vuelta es lo que distingue una división de un producto. |

Fíjate en lo que hacen juntas la primera y la cuarta fila: el mismo procedimiento, y en una el resultado crece y en la otra mengua. No es que «dividir achique» ni que «dividir agrande» — depende de si el divisor es menor o mayor que uno. Esa es la comprobación de un vistazo que le faltó al escriba del silo.

#### Pregunta de abstracción

¿Qué comparten los tres repartos del silo trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `divisor` | En los tres se invierte el divisor y solo el divisor | — |
| 　 | `becomes_product` | En los tres la división se convierte en un producto en el primer paso | — |
| 　 | `smaller` | En los tres el resultado es menor que la primera cantidad | — |
| 　 | `common` | En los tres hace falta un denominador común antes de empezar | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos sacos salen?
¿Cuántos sacos salen?

Respuesta: `49`

Escalera de pistas:
1. El 21 es 21/1.
2. Invierte solo el saco: 21/1 · 7/3.
3. 147 ÷ 3 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otra sementera. Sin nota.

- **Mejoró:** Avance: ya inviertes el divisor y compruebas si el resultado debía crecer.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la pregunta «¿cuántos caben?», que es la que fija cuál se da la vuelta.

**PD1**

¿Cuántos tercios de medida caben en 4 medidas?

Respuesta: `12`

**PD2**

¿Cuánto es $\dfrac{1}{3}\div\dfrac{1}{6}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | 2 | — |
| 　 | `eighteenth` | $\dfrac{1}{18}$ | `multiplica_en_vez_de_dividir` |
| 　 | `half` | $\dfrac{1}{2}$ | `invierte_la_primera_fraccion` |

**PD3**

En $\dfrac{5}{8}\div\dfrac{1}{4}$, ¿a cuál se le da la vuelta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `second` | A $\dfrac{1}{4}$ | — |
| 　 | `first` | A $\dfrac{5}{8}$ | `invierte_la_primera_fraccion` |
| 　 | `both` | A las dos | `invierte_la_primera_fraccion` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-F04-DIVISION-D2` | `eighth` | `multiplica_en_vez_de_dividir` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-D2` | `half` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-D3` | `first` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-D3` | `both` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E1` | `first` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E1` | `mult` | `multiplica_en_vez_de_dividir` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E1` | `swap` | `invierte_las_dos_fracciones` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E4` | `mult` | `multiplica_en_vez_de_dividir` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E4` | `simp` | `habito_deja_el_resultado_sin_simplificar` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E4` | `none` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E5` | `true` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E5` | `true_either` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-E5` | `false_both` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-PD2` | `eighteenth` | `multiplica_en_vez_de_dividir` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-PD2` | `half` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-PD3` | `first` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |
| `ALG-N1-F04-DIVISION-PD3` | `both` | `invierte_la_primera_fraccion` | Señala el divisor —lo que va después del signo— y da la vuelta solo a eso. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
