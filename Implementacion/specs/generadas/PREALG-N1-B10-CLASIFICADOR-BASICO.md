# Nodo: Un número no es su disfraz — PREALG-N1-B10-CLASIFICADOR-BASICO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B10-CLASIFICADOR-BASICO` |
| `concept_slug` | `clasificador` |
| Error focal | `clasifica_por_apariencia` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B08-REALES-RECTA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Consolidación · Clasificador

**Título:** Un número no es su disfraz

Ya conoces los cinco peldaños. Ahora viene la habilidad que los pone a trabajar: mirar un número cualquiera y decir a qué conjunto pertenece. El truco no está en reconocer símbolos — está en resolver antes de decidir.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

¿Qué clase de número es $\dfrac{6}{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `natural` | Natural: vale 3 | — |
| 　 | `fraction_only` | Racional no entero: es una fracción | `clasifica_por_apariencia` |
| 　 | `irrational` | Irracional: tiene barra de división | `clasifica_por_apariencia` |

**D2**

¿Cuánto vale $\sqrt{100}$?

Respuesta: `10`

**D3**

¿$0{,}5$ es racional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: es 1/2 | — |
| 　 | `no_decimal` | No: es un decimal, no un racional | `decimal_y_racional_son_categorias_distintas` |
| 　 | `no_irrational` | No: es irracional | `clasifica_por_apariencia` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Consolidación* — **El bibliotecario y las tablillas sin abrir**

La biblioteca del ágora recibió un cargamento de tablillas y el bibliotecario tiene que ordenarlas por tema. Como son cientos, decidió clasificarlas por el color de la cuerda con que vienen atadas: las de cuerda roja a poesía, las de cuerda azul a geometría.

Al día siguiente un discípulo fue a buscar un tratado de geometría y encontró en ese estante una lista de mercado. Venía con cuerda azul.

**Pregunta:** ¿Qué tenía que haber hecho el bibliotecario antes de decidir el estante de cada tablilla?

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Abrir y leer cada tablilla antes de clasificarla | — |
| 　 | `b` | Usar cuerdas de más colores | — |
| 　 | `c` | Nada: con cientos de tablillas hay que confiar en la cuerda | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos números con el mismo disfraz y distinta casa**

Los dos números de abajo están escritos igual: barra de fracción, dos enteros. Si clasificas por el aspecto, van al mismo estante. Y no van al mismo estante.

- **Se ve fracción y NO lo es** — Al resolver da 2, que es natural. La barra era solo la forma de escribirlo, no lo que era.
- **Se ve fracción y SÍ lo es** — Al resolver da 1,6, que cae entre dos enteros. Este sí es racional no entero: no hay forma de escribirlo sin partes.

**Resolución:** La regla sale sola: **primero resuelve, después clasifica**. El aspecto de un número —barra, coma, signo de raíz— es su ropa, no su identidad. 8/4 y 8/5 usan la misma ropa y viven en peldaños distintos.

**Definición — Clasificar un número**

$$\text{simplificar}\ \longrightarrow\ \text{identificar}\ \longrightarrow\ \text{el conjunto MÁS PEQUEÑO que lo contiene}$$

La frase del nodo: clasificar es decir cuál es el peldaño más bajo en el que el número ya cabe. Por la cadena de inclusión, todos los de arriba lo contienen también.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{a}{b}` | una fracción escrita | puede dar entero o no: hay que dividir para saberlo |
| `\sqrt{n}` | raíz de n | puede ser natural (√9=3) o irracional (√2): hay que resolverla |
| `0{,}\overline{3}` | decimal periódico | se repite ⇒ viene de fracción ⇒ es racional |
| `-4` | menos cuatro | el signo baja de peldaño (sale de ℕ), no sube |
| `\subset` | contenido en | por eso basta nombrar el más pequeño: los mayores vienen incluidos |
| `\mathbb{R}` | los reales | la respuesta de seguridad: casi todo lo que verás está aquí |

### A5. Ejemplos resueltos

#### El sello de la tablilla · *resuelto*

Clasifica el número $\sqrt{49}$: ¿cuál es el conjunto más pequeño que lo contiene?

- No clasifico todavía: primero resuelvo lo que se pueda resolver.
- Busco el número que multiplicado por sí mismo da 49: es 7.
- √49 = 7, y ahora sí clasifico el 7, no el símbolo de raíz.
- 7 cuenta cantidades completas → cabe ya en ℕ, el peldaño más bajo.
- Respuesta: natural. Y por inclusión también es entero, racional y real.

**Autoexplicación (focal):** {'step_index': 0, 'prompt': 'En el paso 1 me negué a clasificar antes de resolver. ¿Qué habría pasado si clasificaba mirando el signo de raíz?'}

#### La medida del inventario · *resuelto*

Clasifica el número $-2{,}75$: ¿cuál es el conjunto más pequeño que lo contiene?

- Tiene coma, así que no es natural ni entero: cae entre −3 y −2.
- ¿Se puede escribir como fracción de enteros? El decimal termina, así que sí.
- −2,75 = −275/100 = −11/4, fracción de enteros.
- Cabe en ℚ, y no cabe en ningún peldaño más bajo.
- Respuesta: racional no entero. Por inclusión también es real.

#### La clasificación hecha de un vistazo · *TRAMPA*

Un discípulo clasificó estas tres así. Está mal: «6/3 es racional no entero porque tiene barra. √16 es irracional porque tiene raíz. Y 0,25 no es racional, es decimal».

- Resuelve cada una antes de mirar a qué conjunto la mandas.
- 6 ÷ 3 = 2 y √16 = 4: los dos son naturales.
- 0,25 termina, así que viene de una fracción: 1/4, racional.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{6}{3}\\in\\mathbb{Q}\\setminus\\mathbb{Z},\\ \\ \\sqrt{16}\\in\\mathbb{I},\\ \\ 0{,}25\\notin\\mathbb{Q}', 'right_latex': '\\dfrac{6}{3}=2\\in\\mathbb{N},\\ \\ \\sqrt{16}=4\\in\\mathbb{N},\\ \\ 0{,}25=\\dfrac{1}{4}\\in\\mathbb{Q}', 'rows': [{'wrong': 'Barra de fracción ⇒ racional no entero', 'right': '6/3 = 2: la barra desaparece al dividir'}, {'wrong': 'Signo de raíz ⇒ irracional · coma ⇒ no racional', 'right': '√16 = 4 es natural; 0,25 = 1/4 es racional'}]}
**¿Por qué falla?:** ¿Qué paso se saltó en las tres? Escribe la clasificación correcta de las tres.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: la simplificación ya está empezada y solo faltan huecos.

**P1** (*falta: last*) — Clasifica $\dfrac{20}{5}$. ¿Cuánto vale?

- dado: $\dfrac{20}{5}=20\div5$
- hueco `P1-b1`: $\dfrac{20}{5}=$ → `4`

**P2** (*falta: middle*) — Clasifica $\sqrt{144}$ y $\dfrac{9}{4}$: da el valor de cada una.

- dado: $12\times12=144$
- hueco `P2-b1`: $\sqrt{144}=$ → `12`
- hueco `P2-b2`: $\dfrac{9}{4}=$ → `2,25`

**P3** (*falta: statement_only*) — Solo el planteamiento: de esta lista, ¿cuántos números son naturales después de resolverlos? 15/3 · √25 · 7/2 · √8 · 0

- hueco `P3-b1`: $\text{Naturales en la lista}=$ → `3`


### A7. Comparación de métodos

**Dos formas de clasificar el mismo número**

¿Qué clase de número es $\dfrac{45}{15}$? Las dos soluciones son correctas.

- **Método 1 · Simplificar primero** — 
- **Método 2 · Dividir y mirar el decimal** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si aplicas el método 2 a $\dfrac{1}{3}$?

**Insight:** Con 1/3 el método 2 te deja mirando 0,333… sin final, y si te apuras concluyes «no termina ⇒ irracional» — el error de B07. El método 1 no tiene ese riesgo: 1/3 ya está escrito como fracción de enteros, y con eso basta para decir racional. Cuando la fracción está a la vista, no la conviertas.

### A8. Práctica independiente (7 ítems)

**E1**

Resuelve antes de clasificar: ¿cuánto vale $\dfrac{36}{4}$?

Respuesta: `9`

Escalera de pistas:
1. La barra es el signo de dividir.
2. ¿Cuántas veces cabe 4 en 36?
3. 36 ÷ 4 = 9, que es natural aunque viniera escrito como fracción.

**E2**

De esta lista, ¿cuántos son NATURALES una vez resueltos? 24/8 · √36 · 5/2 · √7 · 0 · −3

Respuesta: `3`

Escalera de pistas:
1. Resuelve cada uno antes de contar.
2. 24/8 = 3 y √36 = 6; el 0 también es natural en este curso.
3. 5/2 = 2,5 no lo es, √7 tampoco, y −3 es entero pero no natural.

**E3**

¿Cuál es el conjunto MÁS PEQUEÑO que contiene a $\dfrac{14}{7}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `naturals` | ℕ, los naturales | — |
| 　 | `rationals` | ℚ, los racionales | `clasifica_por_apariencia` |
| 　 | `integers` | ℤ, los enteros | `olvida_que_es_positivo` |
| 　 | `reals` | ℝ, los reales | `elige_el_mas_grande` |

Escalera de pistas:
1. Primero resuelve la división.
2. 14 ÷ 7 = 2.
3. El 2 ya cabe en el primer peldaño: ℕ.

**E4**

Un discípulo anotó: «√81 es irracional, porque todas las raíces cuadradas son irracionales». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `resolve` | No resolvió: √81 = 9, que es natural | — |
| 　 | `sign` | Se le olvidó que la raíz también puede ser negativa | `distrae_con_signo` |
| 　 | `rational` | √81 es racional no entero, no natural | `clasifica_por_apariencia` |
| 　 | `none` | Ningún error, está bien | `toda_raiz_es_irracional` |

Escalera de pistas:
1. ¿9 × 9 cuánto da?
2. 81. Así que √81 = 9.
3. 9 es natural: la generalización «toda raíz es irracional» es falsa.

**E5**

¿Es verdadera o falsa? «$\dfrac{10}{5}$ es racional no entero, porque está escrito como fracción.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_two` | Falsa: 10/5 = 2, que es natural y entero | — |
| 　 | `true_written` | Verdadera: si está escrito como fracción, es racional no entero | `clasifica_por_apariencia` |
| 　 | `false_irrational` | Falsa: 10/5 es irracional | `clasifica_por_apariencia` |
| 　 | `depends` | Depende de si lo simplificas o no | `representacion_define_el_numero` |

Escalera de pistas:
1. Divide antes de decidir.
2. 10 ÷ 5 = 2.
3. El 2 es natural. La ropa era de fracción; el número no.

**E6**

El bibliotecario quiere una regla que le sirva SIEMPRE para clasificar un número. ¿Cuál le sirve?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `resolve_first` | Resolver todas las operaciones y después buscar el peldaño más bajo | — |
| 　 | `look_symbol` | Mirar si tiene barra, coma o raíz | `clasifica_por_apariencia` |
| 　 | `count_digits` | Contar cuántas cifras tiene | `confunde_tamano_con_tipo` |
| 　 | `always_real` | Decir siempre «real»: nunca se equivoca | `elige_el_mas_grande` |

Escalera de pistas:
1. Vuelve a la historia del bibliotecario: ¿qué le falló?
2. Clasificó por la cuerda sin abrir la tablilla.
3. La regla equivalente con números es resolver antes de decidir.

**E7**

¿Cuál de estos números NO es natural una vez resuelto?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `seven_halves` | 7/2 | — |
| 　 | `thirty_six` | √36 | `clasifica_por_apariencia` |
| 　 | `eighteen_thirds` | 18/3 | `clasifica_por_apariencia` |
| 　 | `hundred` | √100 | `clasifica_por_apariencia` |

Escalera de pistas:
1. Resuelve los cuatro antes de comparar.
2. √36 = 6, 18/3 = 6 y √100 = 10: los tres son naturales.
3. 7 ÷ 2 = 3,5, que cae entre dos enteros.


### A9. Cierre

*El disfraz y la casa* — **Cómo se ve un número y dónde vive de verdad**

Cada fila es una escritura que engaña. Resuelve y mira dónde cae.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | La barra se fue al dividir. |
|  | ✅ | El radicando era cuadrado perfecto. |
|  | ✅ | Decimal que termina ⇒ racional. |
|  | ✅ | Se repite ⇒ racional, aunque no termine. |
|  | ✗ | Aquí sí: el radicando no es cuadrado perfecto. |

Las dos filas de raíz se ven igual y terminan en peldaños opuestos. Esa es la prueba de que el símbolo no clasifica: solo el valor lo hace.

#### Pregunta de abstracción

¿Qué tienen en común los errores de clasificación de este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `symbol` | En los tres se decidió mirando el símbolo, sin resolver | — |
| 　 | `skipped` | En los tres faltó un paso antes de clasificar | — |
| 　 | `hard` | Los tres son números difíciles | — |
| 　 | `irrational` | Los tres son irracionales | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas de las seis van al estante de los naturales?
¿Cuántas de las seis van al estante de los naturales?

Respuesta: `2`

Escalera de pistas:
1. Resuelve las seis antes de contar nada.
2. 48/6 y √64 dan los dos el mismo número.
3. −7 es entero pero no natural; 9/4 y 0,125 tienen parte decimal.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el paso que se salta antes de clasificar.

**PD1**

¿Qué clase de número es $\dfrac{12}{4}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `natural` | Natural: vale 3 | — |
| 　 | `fraction_only` | Racional no entero: es fracción | `clasifica_por_apariencia` |

**PD2**

¿Cuánto vale $\sqrt{121}$?

Respuesta: `11`

**PD3**

¿$\sqrt{3}$ es racional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: 3 no es cuadrado de ningún entero | — |
| 　 | `yes` | Sí: toda raíz se puede escribir como fracción | `todo_numero_es_fraccion` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B10-CARD-decimal_0333` | `irrationals` | `cree_que_todo_decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-five` | `integers` | `clasifica_entero_positivo_como_Z_en_vez_de_N` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-four_fourths` | `rationals` | `confunde_fraccion_aparente_con_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-four_fourths` | `integers` | `confunde_fraccion_aparente_con_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-half` | `naturals` | `clasifica_fraccion_como_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-half` | `integers` | `clasifica_fraccion_como_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-pi` | `rationals` | `clasifica_irracional_como_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-sqrt2` | `rationals` | `clasifica_irracional_como_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-three_plus_two_i` | `pure_imaginary` | `clasifica_complejo_general_como_imaginario_puro` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-three_plus_two_i` | `naturals` | `ubica_complejos_no_reales_en_recta_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-three_plus_two_i` | `integers` | `ubica_complejos_no_reales_en_recta_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-three_plus_two_i` | `rationals` | `ubica_complejos_no_reales_en_recta_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-three_plus_two_i` | `irrationals` | `ubica_complejos_no_reales_en_recta_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-two_i` | `irrationals` | `confunde_i_imaginaria_con_I_irracionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-zero` | `integers` | `excluye_cero_de_naturales_pese_a_convencion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-zero` | `rationals` | `excluye_cero_de_naturales_pese_a_convencion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-zero` | `irrationals` | `excluye_cero_de_naturales_pese_a_convencion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-zero` | `pure_imaginary` | `excluye_cero_de_naturales_pese_a_convencion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CARD-zero` | `complex_general` | `excluye_cero_de_naturales_pese_a_convencion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-D1` | `fraction_only` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-D1` | `irrational` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-D3` | `no_decimal` | `decimal_y_racional_son_categorias_distintas` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-D3` | `no_irrational` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E3` | `rationals` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E3` | `integers` | `olvida_que_es_positivo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E3` | `reals` | `elige_el_mas_grande` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E4` | `sign` | `distrae_con_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E4` | `rational` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E4` | `none` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E5` | `true_written` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E5` | `false_irrational` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E5` | `depends` | `representacion_define_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E6` | `look_symbol` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E6` | `count_digits` | `confunde_tamano_con_tipo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E6` | `always_real` | `elige_el_mas_grande` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E7` | `thirty_six` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E7` | `eighteen_thirds` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-E7` | `hundred` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-PD1` | `fraction_only` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B10-CLASIFICADOR-BASICO-PD3` | `yes` | `todo_numero_es_fraccion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b10-clasificador-i-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
