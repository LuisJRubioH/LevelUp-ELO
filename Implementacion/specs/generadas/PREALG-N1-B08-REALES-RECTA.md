# Nodo: La recta no tiene huecos — PREALG-N1-B08-REALES-RECTA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B08-REALES-RECTA` |
| `concept_slug` | `reales` |
| Error focal | `existe_el_siguiente` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B07-IRRACIONALES-DECIMALES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Quinto peldaño · Reales

**Título:** La recta no tiene huecos

Tienes las fracciones y tienes los irracionales. Aquí los juntas y descubres que la recta queda completa: cada punto tiene nombre y cada nombre tiene punto. Y descubres también algo que contradice todo lo que aprendiste contando: aquí ningún número tiene un «siguiente».

**Escena:** Los reales reúnen racionales e irracionales: son los números de la recta

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

¿Qué número viene inmediatamente después del 7 en los ENTEROS?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `eight` | El 8 | — |
| 　 | `none` | Ninguno: siempre hay uno en medio | `confunde_denso_con_discreto` |
| 　 | `seven_one` | El 7,1 | `mezcla_conjuntos` |

**D2**

¿Existe algún número entre 0,4 y 0,5?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes_many` | Sí, y hay infinitos | — |
| 　 | `no` | No: 0,5 va justo después de 0,4 | `existe_el_siguiente` |
| 　 | `one` | Sí, exactamente uno: 0,45 | `densidad_finita` |

**D3**

¿Dónde vive $\sqrt{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `line` | En la recta, entre 1 y 2 | — |
| 　 | `nowhere` | En ningún lugar: no se puede ubicar | `irracional_no_existe` |
| 　 | `outside` | Fuera de la recta, porque no es una fracción | `recta_es_solo_racionales` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · El quinto peldaño* — **La cuerda del agrimensor**

El agrimensor tensa una cuerda de un extremo al otro del muro del gimnasio y clava una marca en el 0 y otra en el 1. Le pide a un aprendiz que marque con tinta TODOS los puntos que haya entre las dos.

El aprendiz marca la mitad. Luego los tercios. Luego los cuartos, los quintos, los milésimos. Trabaja hasta que se le acaba la tinta y el muro es una mancha negra. Entonces el agrimensor apoya la diagonal de una baldosa sobre la cuerda, hace una marca — y esa marca cae en un punto que el aprendiz no había tocado.

**Pregunta:** Si el aprendiz hubiera tenido tinta infinita y hubiera marcado TODAS las fracciones, ¿habría quedado algún punto sin marcar?

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | No: con todas las fracciones ya está todo cubierto | — |
| 　 | `b` | Sí: quedan huecos, y son los irracionales | — |
| 　 | `c` | Quedan huecos, pero muy pocos | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos preguntas sobre la misma cuerda**

La cuerda entre el 0 y el 1 se ve igual en los dos casos de abajo, pero las preguntas son distintas y las respuestas te van a sorprender por razones opuestas.

- **Caso que ya sabías** — Entre dos marcas cualesquiera siempre puede meter otra: basta el promedio. Nunca termina, y nunca hay «la siguiente».
- **Caso que rompe la expectativa** — Ese punto existe, se puede construir con regla — y NO es ninguna de las infinitas marcas del aprendiz. Estaba en un hueco.

**Resolución:** Dos cosas a la vez, y cuestan de tragar juntas. Las fracciones están APRETADAS: entre dos cualesquiera hay infinitas más, así que ninguna tiene siguiente. Y aun así, apretadas y todo, DEJAN HUECOS. La recta completa necesita las fracciones y los irracionales al tiempo. A esa unión la llamamos los reales.

**Definición — Los números reales**

$$\mathbb{R}=\mathbb{Q}\cup\mathbb{I}\quad\text{con}\quad\mathbb{Q}\cap\mathbb{I}=\varnothing$$

La frase del nodo: los reales son los números de la recta. Cada punto tiene nombre, cada nombre tiene punto, y entre dos cualesquiera siempre hay otro.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\mathbb{R}` | los reales | todos los puntos de la recta numérica, sin huecos |
| `\cup` | unión | junta los dos conjuntos en uno solo |
| `\cap` | intersección | lo que tienen en común |
| `\varnothing` | conjunto vacío | nada: ningún número es racional e irracional a la vez |
| `\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}` | la cadena de inclusiones | cada peldaño contiene enterito al anterior; no se perdió nada |
| `\dfrac{a+b}{2}` | el promedio de a y b | la receta para meter siempre un número entre otros dos |

### A5. Ejemplos resueltos

#### La marca entre dos marcas · *resuelto*

El aprendiz ya marcó 0,3 y 0,4 en la cuerda y dice que ahí no cabe nada más. ¿Puedes darle un número que caiga justo en medio?

- Para meter un número entre dos, el promedio siempre sirve.
- Sumo los dos extremos: 0,3 + 0,4 = 0,7.
- Divido entre 2: 0,7 ÷ 2 = 0,35.
- Compruebo que quedó en medio: 0,3 < 0,35 < 0,4. ✓
- Y lo importante: puedo repetir la receta con 0,3 y 0,35, y otra vez, sin fin.

**Autoexplicación (focal):** {'step_index': 4, 'prompt': 'El paso 5 dice que la receta se puede repetir sin fin. ¿Qué significa eso sobre la idea de «el número que sigue»?'}

#### La diagonal apoyada sobre la cuerda · *resuelto*

¿Entre qué dos enteros cae √2, y cómo se marca ese punto exacto sin medirlo con la regla?

- 1 × 1 = 1 y 2 × 2 = 4. Como 2 está entre 1 y 4, √2 está entre 1 y 2.
- Afino: 1,4 × 1,4 = 1,96 (se queda corto) y 1,5 × 1,5 = 2,25 (se pasa).
- Entonces √2 está entre 1,4 y 1,5. Puedo seguir afinando para siempre.
- Para el punto EXACTO no mido: construyo. Apoyo la diagonal de la baldosa de lado 1 sobre la cuerda desde el 0.
- Donde cae la punta, ahí está √2. Es un punto de la recta como cualquier otro, aunque no sea fracción.

#### El número que venía después · *TRAMPA*

Un aprendiz escribió esto en la tablilla. Está mal: «Después del 2,5 viene el 2,6, igual que después del 2 viene el 3. Entre 2,5 y 2,6 no hay nada».

- Calcula el promedio de 2,5 y 2,6.
- Comprueba que el resultado esté estrictamente entre los dos.
- Ahora repite con 2,5 y ese nuevo número, y date cuenta de que nunca se acaba.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\text{entre }2{,}5\\text{ y }2{,}6:\\ \\text{nada}', 'right_latex': '2{,}5<2{,}55<2{,}555<\\ldots<2{,}6', 'rows': [{'wrong': 'Después de 2,5 viene 2,6', 'right': 'No hay «el siguiente»: el promedio 2,55 se cuela en medio'}, {'wrong': 'En ℤ pasa igual que en ℝ', 'right': 'En ℤ sí hay siguiente (3 sigue a 2); en ℝ nunca'}]}
**¿Por qué falla?:** ¿Por qué en los reales ningún número tiene siguiente? Escribe un número entre 2,5 y 2,6.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el procedimiento ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — Mete un número entre 1,2 y 1,3 usando la receta del promedio.

- dado: $1{,}2+1{,}3=2{,}5$
- dado: $2{,}5\div2$
- hueco `P1-b1`: $\text{Número en medio}=$ → `1,25`

**P2** (*falta: middle*) — El agrimensor quiere saber entre qué dos enteros cae √30, para clavar las marcas de referencia.

- dado: $5\times5=25$
- hueco `P2-b1`: $6\times6=$ → `36`
- hueco `P2-b2`: $\text{Entero de la izquierda}=$ → `5`
- hueco `P2-b3`: $\text{Entero de la derecha}=$ → `6`

**P3** (*falta: statement_only*) — Solo el planteamiento: la clepsidra se vacía en 4 horas y hay que marcar el punto medio del vaciado, luego el punto medio de la primera mitad, y así 3 veces. ¿En qué hora cae la tercera marca?

- hueco `P3-b1`: $\text{Tercera marca (horas)}=$ → `0,5`


### A7. Comparación de métodos

**Dos caminos para meter un número entre otros dos**

Hay que dar un número entre $0{,}7$ y $0{,}8$. Las dos soluciones de abajo son correctas.

- **Método 1 · Promedio** — 
- **Método 2 · Agregar una cifra decimal** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si te piden un número entre $0{,}7$ y $0{,}70001$?

**Insight:** El método 2 se queda sin cifras cuando los dos números están muy cerca — hay que seguir agregando decimales y termina siendo el mismo trabajo. El promedio no falla nunca: por muy pegados que estén, siempre hay un punto medio. Esa es la demostración de que los reales son densos.

### A8. Práctica independiente (7 ítems)

**E1**

Da un número que esté entre 3,1 y 3,2, usando la receta del promedio.

Respuesta: `3,15`

Escalera de pistas:
1. Suma los dos y divide entre 2.
2. 3,1 + 3,2 = 6,3.
3. 6,3 ÷ 2 = 3,15.

**E2**

¿Cuál es el entero inmediatamente a la IZQUIERDA de √52 en la recta?

Respuesta: `7`

Escalera de pistas:
1. Busca cuadrados perfectos cerca de 52.
2. 7 × 7 = 49 y 8 × 8 = 64.
3. 52 está entre 49 y 64, así que √52 está entre 7 y 8.

**E3**

¿Cuál de estas afirmaciones sobre los reales es VERDADERA?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `dense` | Entre dos reales distintos siempre hay otro real | — |
| 　 | `next` | Cada real tiene un siguiente, igual que los enteros | `existe_el_siguiente` |
| 　 | `only_q` | Todos los reales se pueden escribir como fracción | `recta_es_solo_racionales` |
| 　 | `finite` | Entre 0 y 1 hay una cantidad finita de reales | `densidad_finita` |

Escalera de pistas:
1. Prueba cada una con un ejemplo concreto.
2. Para la del siguiente: ¿qué número va después de 0,5?
3. El promedio siempre se cuela: por eso ninguna tiene siguiente y hay infinitos.

**E4**

Un aprendiz anotó: «√9 no es real, porque las raíces son irracionales y los irracionales no caben en la recta». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | Dos errores: √9 = 3 es racional, y los irracionales SÍ están en la recta | — |
| 　 | `only_root` | Solo uno: √9 = 3, pero es cierto que los irracionales no caben | `recta_es_solo_racionales` |
| 　 | `only_line` | Solo uno: los irracionales sí caben, pero √9 sí es irracional | `toda_raiz_es_irracional` |
| 　 | `none` | Ningún error, está bien | `recta_es_solo_racionales` |

Escalera de pistas:
1. Revisa las dos afirmaciones por separado.
2. √9 = 3, y 3 = 3/1 es racional (eso lo viste en B07).
3. Y ℝ = ℚ ∪ 𝕀: los irracionales son la mitad de la recta, no unos intrusos.

**E5**

¿Cuál es el número real que sigue inmediatamente después de $0{,}9$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `none` | Ninguno: no existe el siguiente en los reales | — |
| 　 | `one` | El 1 | `existe_el_siguiente` |
| 　 | `ninety_one` | El 0,91 | `existe_el_siguiente` |
| 　 | `nines` | El 0,99999… | `existe_el_siguiente` |

Escalera de pistas:
1. Escoge cualquier candidato y busca un número entre 0,9 y él.
2. Si dices 0,91, ahí está 0,905 en medio. Y luego 0,9005.
3. Cualquier candidato se cae por el promedio: por eso no hay siguiente.

**E6**

La balanza del mercado tiene marcas cada 10 gramos. Un comerciante dice: «entonces solo existen pesos de 10 en 10». ¿Qué le respondes?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `instrument` | Que la balanza es el límite del instrumento, no del peso: entre 10 y 20 g hay infinitos pesos posibles | — |
| 　 | `agree` | Que tiene razón: si no se puede medir, no existe | `instrumento_define_el_numero` |
| 　 | `finer` | Que con una balanza más fina sí existirían todos los pesos intermedios | `instrumento_define_el_numero` |
| 　 | `integers` | Que los pesos siempre son enteros | `existe_el_siguiente` |

Escalera de pistas:
1. ¿El peso de una manzana depende de qué balanza uses para pesarla?
2. El peso ya está ahí; la balanza solo lo aproxima a la marca más cercana.
3. Es el mismo error que la regla graduada de B06: el instrumento corta, el número no.

**E7**

¿Cuál de estas operaciones NO tiene resultado dentro de los reales?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sqrt_neg` | √(−4) | — |
| 　 | `sqrt_two` | √2 | `irracional_no_es_real` |
| 　 | `div` | 1 ÷ 3 | `fraccion_no_es_real` |
| 　 | `sub` | 2 − 9 | `negativo_no_es_real` |

Escalera de pistas:
1. Tres de las cuatro las resolviste en peldaños anteriores.
2. √2 es irracional pero real; 1÷3 y 2−9 también son reales.
3. Ningún real multiplicado por sí mismo da un negativo. Ese es el próximo desvío.


### A9. Cierre

*La escalera de la necesidad* — **¿Toda raíz cuadrada vive en el conjunto?**

Cerraste la recta. Ahora la pregunta que la parte otra vez.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | No alcanza ni para la diagonal. |
|  | ✗ | Los negativos no ayudaron aquí. |
|  | ✗ | El golpe de B07: la diagonal no es fracción. |
|  | ✗ | Casi: todas las raíces de positivos sí, pero las de negativos no. |
|  | ✅ | Para eso hay que salirse de la recta. Desvío opcional: B09. |

Con ℝ tienes toda la recta y no falta ni un punto. Pero la recta tiene un límite propio: ningún número de ella, multiplicado por sí mismo, da negativo. Para resolver eso no hace falta un peldaño más alto — hace falta salirse de la línea y usar el plano.

#### Pregunta de abstracción

¿Qué comparten los tres momentos clave de este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `line` | Los tres hablan de puntos de una misma recta | — |
| 　 | `dense` | Los tres muestran que entre dos puntos siempre cabe otro | — |
| 　 | `complete` | Los tres apuntan a que la recta queda completa sin huecos | — |
| 　 | `roots` | Los tres necesitan raíces cuadradas | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿En qué número queda la segunda marca?
¿En qué número queda la segunda marca?

Respuesta: `2,425`

Escalera de pistas:
1. Haz primero el punto medio entre 2,4 y 2,5.
2. Ese da 2,45. Ahora promedia 2,4 con 2,45.
3. (2,4 + 2,45) ÷ 2 = 4,85 ÷ 2.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué en la recta ningún número tiene siguiente.

**PD1**

¿Qué número REAL viene inmediatamente después del 7?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `none` | Ninguno: siempre hay uno en medio | — |
| 　 | `eight` | El 8 | `existe_el_siguiente` |
| 　 | `seven_one` | El 7,1 | `existe_el_siguiente` |

**PD2**

Da un número entre 1,6 y 1,7 (usa el promedio).

Respuesta: `1,65`

**PD3**

¿$\pi$ es un número real?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: está en la recta, entre 3 y 4 | — |
| 　 | `no` | No: es irracional, y los irracionales no son reales | `recta_es_solo_racionales` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B08-REALES-RECTA-D1` | `none` | `confunde_denso_con_discreto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-D1` | `seven_one` | `mezcla_conjuntos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-D2` | `no` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-D2` | `one` | `densidad_finita` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-D3` | `nowhere` | `irracional_no_existe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-D3` | `outside` | `recta_es_solo_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E3` | `next` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E3` | `only_q` | `recta_es_solo_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E3` | `finite` | `densidad_finita` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E4` | `only_root` | `recta_es_solo_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E4` | `only_line` | `toda_raiz_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E4` | `none` | `recta_es_solo_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E5` | `one` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E5` | `ninety_one` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E5` | `nines` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E6` | `agree` | `instrumento_define_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E6` | `finer` | `instrumento_define_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E6` | `integers` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E7` | `sqrt_two` | `irracional_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E7` | `div` | `fraccion_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-E7` | `sub` | `negativo_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-PD1` | `eight` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-PD1` | `seven_one` | `existe_el_siguiente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-REALES-RECTA-PD3` | `no` | `recta_es_solo_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-S3` | `false` | `no_reconoce_irracionales_como_reales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-S4` | `true` | `cree_que_todo_real_es_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B08-S5` | `true` | `ubica_complejos_en_recta_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b08-reales-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
