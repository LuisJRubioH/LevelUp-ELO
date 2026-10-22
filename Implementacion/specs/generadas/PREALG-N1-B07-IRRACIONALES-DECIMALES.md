# Nodo: No toda medida cabe en una fracción — PREALG-N1-B07-IRRACIONALES-DECIMALES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B07-IRRACIONALES-DECIMALES` |
| `concept_slug` | `irracionales` |
| Error focal | `decimal_infinito_es_irracional` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Cuarto peldaño · Irracionales

**Título:** No toda medida cabe en una fracción

En el peldaño anterior aprendiste que una fracción es una división y que su decimal a veces no termina. Aquí viene la parte incómoda: existen medidas reales, dibujables con regla, que NINGUNA fracción puede escribir. Y aprender a reconocerlas no es mirar si el decimal es largo.

**Escena:** Los irracionales son los reales que no son racionales: erre menos cu

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

$\dfrac{1}{3}=0{,}333\ldots$ ¿Ese número es racional o irracional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `rational` | Racional: viene de una fracción | — |
| 　 | `irrational` | Irracional: su decimal no termina | `decimal_infinito_es_irracional` |
| 　 | `neither` | Ninguno de los dos | `habito_evita_decidir` |

**D2**

Un cuadrado tiene lado 1. ¿Cuánto vale el área de ese cuadrado?

Respuesta: `1`

**D3**

¿Es cierto que $\pi=\dfrac{22}{7}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no_approx` | No: 22/7 solo se le parece | — |
| 　 | `yes` | Sí, es la fracción de π | `pi_es_una_fraccion` |
| 　 | `no_other` | No, pero existe otra fracción que sí lo da exacto | `todo_numero_es_fraccion` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · El cuarto peldaño* — **La diagonal que rompió la escuela**

Los pitagóricos creían algo hermoso y lo creían de verdad: que todo en el mundo se podía escribir como razón de dos números enteros. Toda longitud, toda nota musical, toda proporción.

Entonces alguien dibujó en una baldosa un cuadrado de lado 1 y trazó su diagonal. Una raya. La cosa más simple del mundo. Y se pusieron a buscar la fracción que diera esa longitud exacta. Probaron 7/5. Probaron 17/12. Probaron 99/70. Cada una se acercaba más, y ninguna daba.

**Pregunta:** ¿Crees que no la encontraron porque no buscaron lo suficiente, o porque esa fracción no existe?

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Existe, solo que con números muy grandes | — |
| 　 | `b` | No existe ninguna fracción que la dé exacta | — |
| 　 | `c` | La diagonal no es un número de verdad | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos decimales infinitos que no se parecen en nada**

Los dos decimales de abajo siguen para siempre. Si tu criterio para decidir es «no termina», los vas a clasificar igual — y son de familias distintas. Mira qué hace cada uno.

- **Caso que ya sabías** — No termina, PERO se repite: 27, 27, 27, para siempre. Ese patrón es la huella de una fracción. Es racional.
- **Caso que rompe la expectativa** — No termina Y no se repite nunca: no hay bloque que vuelva. Sin patrón no hay fracción. Es irracional.

**Resolución:** El criterio no es «¿termina?». Es «¿se repite?». Un decimal que termina o que se repite viene de una fracción. Uno que sigue para siempre SIN repetirse no viene de ninguna, y no porque no la hayamos encontrado: se puede demostrar que no existe. Eso es lo que descubrieron los pitagóricos, y no les gustó nada.

**Definición — Los números irracionales**

$$\mathbb{I}=\mathbb{R}\setminus\mathbb{Q}=\left\{x\ :\ x\neq\dfrac{a}{b}\ \text{con}\ a,b\in\mathbb{Z}\right\}$$

La frase del nodo: irracional no significa «raro» ni «muy largo». Significa una sola cosa: que no se puede escribir como fracción de enteros.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\mathbb{I}` | los irracionales | los que NO son razón (ratio) de dos enteros |
| `\setminus` | menos, quitando | ℝ quitándole ℚ: lo que queda de la recta al sacar las fracciones |
| `\sqrt{2}` | raíz de dos | el número que multiplicado por sí mismo da 2; mide la diagonal del cuadrado de lado 1 |
| `\pi` | pi | cuántas veces cabe el diámetro en el contorno de un círculo |
| `0{,}\overline{27}` | cero coma veintisiete periódico | la barra marca el bloque que se repite: esto SÍ es racional |
| `\notin\mathbb{Q}` | no pertenece a ℚ | la prueba de irracionalidad: no hay fracción que lo dé |

### A5. Ejemplos resueltos

#### El mosaico del alfarero · *resuelto*

El alfarero divide una franja de mosaico en 11 partes iguales y toma 3. Su decimal es 0,272727… ¿Es racional o irracional?

- Escribo el reparto como fracción: 3 partes de 11 → 3/11.
- Divido: 3 ÷ 11 = 0,272727…
- Miro si hay patrón: el bloque 27 se repite sin cambiar. Sí lo hay.
- Un decimal con bloque que se repite SIEMPRE viene de una fracción.
- Como 3/11 es fracción de enteros, el número es racional. El decimal infinito no cambia eso.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 busqué un patrón en vez de mirar si el decimal terminaba. ¿Por qué «termina» no sirve como criterio y «se repite» sí?'}

#### La diagonal de la baldosa · *resuelto*

Una baldosa cuadrada mide 1 palmo de lado. ¿Se puede escribir su diagonal como fracción de enteros?

- La diagonal d cumple d × d = 2, porque el cuadrado de lado 1 tiene esa relación.
- Supongamos que SÍ existe: d = a/b, ya simplificada al máximo (sin factores comunes).
- Entonces a × a = 2 × (b × b), así que a×a es par, y por tanto a también es par.
- Si a es par, a = 2k, y al sustituir sale que b×b también es par: b es par.
- Pero a y b pares se contradice con «ya simplificada al máximo». La suposición era falsa: esa fracción NO existe.

#### El decimal largo que se clasificó mal · *TRAMPA*

Un discípulo entregó esta clasificación. Está mal: «0,333… es irracional, porque tiene infinitas cifras y nunca termina. Y 3,14 es racional, porque es corto y termina».

- Divide 1 ÷ 3 y mira qué hace el resto.
- El resto se repite, así que el decimal repite un bloque: eso delata una fracción.
- Ahora mira las cifras de √2: 1,41421356… ¿ves algún bloque que vuelva?

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '0{,}\\overline{3}\\in\\mathbb{I}', 'right_latex': '0{,}\\overline{3}=\\dfrac{1}{3}\\in\\mathbb{Q}', 'rows': [{'wrong': '0,333… no termina, luego es irracional', 'right': '0,333… se repite, luego es 1/3: racional'}, {'wrong': '3,14 termina, luego es π y es racional', 'right': '3,14 sí es racional (= 157/50), pero NO es π: π es irracional'}]}
**¿Por qué falla?:** ¿Por qué «no termina» no alcanza para decir irracional? Escribe el criterio correcto.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: la clasificación ya está empezada y solo faltan huecos.

**P1** (*falta: last*) — Clasifica 0,625. El alfarero lo obtuvo repartiendo 5 entre 8.

- dado: $0{,}625=\dfrac{5}{8}$
- dado: $\text{decimal termina}\Rightarrow\text{viene de fracción}$
- hueco `P1-b1`: $\text{Denominador de la fracción}=$ → `8`

**P2** (*falta: middle*) — De esta lista, cuenta los irracionales: 0,5 · √9 · √2 · 2/7 · π · 1,101101110…

- dado: $\sqrt{9}=3\ \Rightarrow\ \text{racional}$
- hueco `P2-b1`: $\text{Racionales en la lista}=$ → `3`
- hueco `P2-b2`: $\text{Irracionales en la lista}=$ → `3`

**P3** (*falta: statement_only*) — Solo el planteamiento: una baldosa cuadrada tiene área 16 palmos cuadrados. ¿Cuánto mide su lado, y ese número es racional o irracional? Responde con la medida del lado.

- hueco `P3-b1`: $\text{Lado}=$ → `4`


### A7. Comparación de métodos

**Dos caminos para decidir si un número es racional**

¿Es $\sqrt{25}$ racional? Las dos soluciones de abajo son correctas.

- **Método 1 · Mirar el decimal** — 
- **Método 2 · Buscar la fracción** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si aplicas el método 1 a $\sqrt{2}$ con una calculadora de 8 cifras?

**Insight:** El método 1 falla justo donde importa: la calculadora muestra 1,41421356 y corta, y si te fías de la pantalla concluyes «termina, es racional». La pantalla es una foto, igual que el decimal cortado de B06. Solo el método 2 —buscar la fracción, o demostrar que no existe— decide de verdad.

### A8. Práctica independiente (7 ítems)

**E1**

De esta lista, ¿cuántos son IRRACIONALES? √4 · √3 · 0,75 · π · 1/6 · 2,010010001…

Respuesta: `3`

Escalera de pistas:
1. Empieza por descartar: ¿cuáles vienen claramente de una fracción?
2. √4 = 2 y 1/6 = 0,1666… son racionales; 0,75 también.
3. Quedan √3, π y el que va agregando ceros sin repetir bloque.

**E2**

Una baldosa cuadrada tiene área 49 palmos cuadrados. ¿Cuánto mide su lado?

Respuesta: `7`

Escalera de pistas:
1. El lado por sí mismo debe dar el área.
2. Busca el número que multiplicado por sí mismo da 49.
3. 7 × 7 = 49, así que este sí es racional (no toda raíz es irracional).

**E3**

¿Cuál de estos números NO es racional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sqrt5` | √5 | — |
| 　 | `periodic` | 0,8181… | `decimal_infinito_es_irracional` |
| 　 | `sqrt36` | √36 | `toda_raiz_es_irracional` |
| 　 | `neg_frac` | −7/4 | `negativo_no_es_racional` |

Escalera de pistas:
1. Tres de los cuatro se pueden escribir como fracción de enteros.
2. √36 = 6 y 0,8181… = 9/11.
3. 5 no es cuadrado de ningún entero, así que √5 no cierra en ninguna fracción.

**E4**

Un discípulo anotó: «Medí el contorno de la rueda y el diámetro, dividí, y me dio 3,1428. Entonces π = 3,1428 y π es racional». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `measurement` | Su medida es una aproximación; π no es igual a ningún decimal que él pueda escribir | — |
| 　 | `divided_wrong` | Dividió al revés: debía dividir diámetro entre contorno | `invierte_cociente` |
| 　 | `not_pi` | El contorno entre el diámetro no da π | `desconoce_definicion_pi` |
| 　 | `none` | Ningún error, está bien | `pi_es_una_fraccion` |

Escalera de pistas:
1. El procedimiento (contorno ÷ diámetro) está bien: eso SÍ es π.
2. El problema es que midió con una cuerda, y toda medida real es aproximada.
3. Ningún decimal que quepa en su tablilla es π: π no termina ni se repite.

**E5**

¿Es verdadera o falsa? «Si un decimal no termina, el número es irracional.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_periodic` | Falsa: 0,333… no termina y es 1/3, racional | — |
| 　 | `true_rule` | Verdadera: no terminar es la definición de irracional | `decimal_infinito_es_irracional` |
| 　 | `false_all_finite` | Falsa: todos los decimales terminan en algún punto | `todo_decimal_termina` |
| 　 | `depends` | Depende de con cuántas cifras lo escribas | `representacion_define_el_numero` |

Escalera de pistas:
1. Busca un contraejemplo entre los decimales que ya conoces.
2. 1/3 = 0,333… no termina. ¿Y es irracional?
3. No: viene de una fracción. El criterio es si se REPITE, no si termina.

**E6**

El agrimensor debe marcar en el muro una longitud de √2 palmos exactos. Solo tiene una regla graduada en centésimas de palmo. ¿Qué puede hacer?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `construct` | Trazar la diagonal de un cuadrado de lado 1: eso da √2 exacto, sin regla | — |
| 　 | `measure` | Marcar 1,41 palmos: es exactamente √2 | `decimal_truncado_es_el_numero` |
| 　 | `impossible` | Nada: √2 no existe como longitud | `irracional_no_existe` |
| 　 | `fraction` | Buscar la fracción de √2 y convertirla a centésimas | `todo_numero_es_fraccion` |

Escalera de pistas:
1. Vuelve a la historia de la apertura: ¿de dónde salió √2?
2. Salió de una construcción con regla, no de una medición.
3. Ser irracional impide ESCRIBIRLO como fracción, no DIBUJARLO.

**E7**

¿Cuál de estas raíces da un número racional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sqrt64` | √64 | — |
| 　 | `sqrt2` | √2 | `toda_raiz_es_irracional` |
| 　 | `sqrt10` | √10 | `toda_raiz_es_irracional` |
| 　 | `sqrt7` | √7 | `toda_raiz_es_irracional` |

Escalera de pistas:
1. ¿Cuál de los cuatro números es el cuadrado de un entero?
2. 8 × 8 = 64.
3. √64 = 8, que es 8/1: racional. Las otras tres no cierran.


### A9. Cierre

*La escalera de la necesidad* — **¿Alcanza el conjunto para nombrar toda longitud que se puede dibujar?**

Cada peldaño nació de algo que no cabía. Este nació de una raya sobre una baldosa.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Ni siquiera media baldosa cabe. |
|  | ✗ | Ganó los negativos, no las partes. |
|  | ✗ | Aquí se cayó la escuela: la diagonal no tiene fracción. |
|  | ✗ | Solos tampoco alcanzan: se les fueron todas las fracciones. |
|  | ✅ | Solo la UNIÓN de los dos llena la recta. Ese es B08. |

Fíjate en la fila de 𝕀: los irracionales por su cuenta no sirven como sistema de números — no tienen ni el 0, ni el 1, ni las fracciones. Su papel es completar. Por eso el siguiente peldaño no es «otro conjunto más», es la unión de dos.

#### Pregunta de abstracción

¿Qué tienen en común los números irracionales que viste en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `no_fraction` | Ninguno se puede escribir como fracción de enteros | — |
| 　 | `no_pattern` | Su decimal es infinito y sin bloque que se repita | — |
| 　 | `roots` | Todos son raíces cuadradas | — |
| 　 | `big` | Todos son números muy grandes | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas de las seis son racionales?
¿Cuántas de las seis son racionales?

Respuesta: `3`

Escalera de pistas:
1. Empieza resolviendo las raíces: ¿cuál da entero?
2. √16 = 4 es racional; √5 no.
3. Ojo con 22/7: es una fracción, así que es racional aunque se parezca a π.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre un decimal que se repite y uno que no.

**PD1**

$\dfrac{2}{9}=0{,}222\ldots$ ¿Racional o irracional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `rational` | Racional | — |
| 　 | `irrational` | Irracional | `decimal_infinito_es_irracional` |

**PD2**

¿$\sqrt{81}$ es racional o irracional?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `rational` | Racional: da 9 | — |
| 　 | `irrational` | Irracional: es una raíz | `toda_raiz_es_irracional` |

**PD3**

De esta lista, ¿cuántos son irracionales? √2 · 1/4 · π · 0,5

Respuesta: `2`

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B07-G-periodic03` | `irrational` | `cree_que_todo_decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-G-pi` | `rational` | `no_reconoce_irracional_como_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-G-seven` | `irrational` | `cree_que_enteros_no_son_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-G-sqrt2` | `rational` | `no_reconoce_irracional_como_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-D1` | `irrational` | `decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-D1` | `neither` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-D3` | `yes` | `pi_es_una_fraccion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-D3` | `no_other` | `todo_numero_es_fraccion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E3` | `periodic` | `decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E3` | `sqrt36` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E3` | `neg_frac` | `negativo_no_es_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E4` | `divided_wrong` | `invierte_cociente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E4` | `not_pi` | `desconoce_definicion_pi` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E4` | `none` | `pi_es_una_fraccion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E5` | `true_rule` | `decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E5` | `false_all_finite` | `todo_decimal_termina` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E5` | `depends` | `representacion_define_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E6` | `measure` | `decimal_truncado_es_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E6` | `impossible` | `irracional_no_existe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E6` | `fraction` | `todo_numero_es_fraccion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E7` | `sqrt2` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E7` | `sqrt10` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-E7` | `sqrt7` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-PD1` | `irrational` | `decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B07-IRRACIONALES-DECIMALES-PD2` | `irrational` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b07-irracionales-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
