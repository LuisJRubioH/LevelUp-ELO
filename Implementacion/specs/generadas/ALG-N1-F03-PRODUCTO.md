# Nodo: «Tres cuartos de la parva» es un por, no una suma — ALG-N1-F03-PRODUCTO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-F03-PRODUCTO` |
| `concept_slug` | `producto_de_fracciones_algebraicas` |
| Error focal | `busca_comun_denominador_para_multiplicar` |
| Sala / edificio | La era de trilla |
| Guía | Tabiry |
| Entra después de | `ALG-N1-F02-SUMA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La era de trilla · Producto de fracciones

**Título:** «Tres cuartos de la parva» es un por, no una suma

En el canal madre juntabas partes del mismo reparto. En la era no se juntan partes: se toman partes DE otras partes. La cuenta es más corta de lo que parece, y el error habitual es hacer de más.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de subir a la era. Sin nota.

**D1**

¿Cuánto es la mitad de 12?

Respuesta: `6`

**D2**

¿Cuánto es $\dfrac{2}{3}\cdot\dfrac{1}{5}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $\dfrac{2}{15}$ | — |
| 　 | `same` | $\dfrac{2}{5}$ | `olvida_multiplicar_los_denominadores` |
| 　 | `sum` | $\dfrac{13}{15}$ | `busca_comun_denominador_para_multiplicar` |

**D3**

Para multiplicar dos fracciones, ¿hace falta un denominador común?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: se multiplica arriba con arriba y abajo con abajo | — |
| 　 | `yes` | Sí, igual que para sumarlas | `busca_comun_denominador_para_multiplicar` |
| 　 | `sometimes` | Solo si los denominadores son distintos | `busca_comun_denominador_para_multiplicar` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la era de trilla* — **La troje que recibió más grano del que se trilló**

En la era se trilla la parva y se separa el grano limpio de la paja. Tabiry lleva una tablilla con dos números:

«De la parva, dos tercios salen como grano limpio. Y de ese grano, tres cuartos van a la troje del templo.»

«El escriba de ayer hizo lo mismo que hace para el riego: buscó doceavos, los puso a la misma altura, sumó, y anotó que a la troje iban diecisiete doceavos de la parva.»

Tabiry mira la era vacía.

«Mandó al templo más grano del que se había trillado. Y la parva era una sola.»

**Pregunta:** Cuando se toma una parte DE otra parte, ¿la cuenta es una suma o un producto?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Una suma: hay dos fracciones, se juntan | — |
| 　 | `b` | Un producto: la segunda parte se toma dentro de la primera | — |
| 　 | `c` | Una resta: lo que va al templo se descuenta | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Las mismas dos fracciones, dos operaciones distintas**

Con un tercio y un medio se pueden hacer dos cuentas, y no se parecen en nada.

- **Juntar dos partes** — Hay que igualar los trozos. El resultado es mayor que cada parte.
- **Una parte DE otra parte** — Se parte en dos lo que ya estaba partido en tres: salen seis trozos. Sale MENOR.

**Resolución:** Al sumar hay que igualar los trozos porque se cuentan juntos. Al multiplicar no se cuenta nada junto: se vuelve a partir lo que ya estaba partido, y por eso los denominadores se multiplican entre sí. Buscar denominador común aquí no es un paso de más — es un paso que cambia el resultado.

**Definición — Producto de fracciones algebraicas**

$$\dfrac{a}{b}\cdot\dfrac{c}{d}=\dfrac{a\,c}{b\,d}$$

Para MULTIPLICAR dos fracciones se multiplican los numeradores entre sí y los denominadores entre sí. No hace falta denominador común. La palabra «de» en «dos tercios DE la parva» es una multiplicación. Como arriba y abajo todo son factores, se puede simplificar antes de multiplicar — incluso cruzando el numerador de una con el denominador de la otra.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{2}{3}\cdot\dfrac{1}{5}=\dfrac{2}{15}` | arriba con arriba, abajo con abajo | la regla entera |
| `\text{«de»}\to\cdot` | de es por | dos tercios DE tres cuartos es un producto |
| `\dfrac{3}{x}\cdot\dfrac{x}{5}=\dfrac{3}{5}` | la letra se va | arriba y abajo son factores: la x se cancela |
| `6=\dfrac{6}{1}` | un entero es fracción | todo número tiene un 1 debajo |
| `\dfrac{8}{15}\cdot\dfrac{25}{12}` | se puede cruzar | simplificar antes deja números pequeños |

### A5. Ejemplos resueltos

#### Una parte de otra parte · *resuelto*

De la parva, dos tercios salen como grano limpio; de ese grano, tres cuartos van a la troje. ¿Qué parte de la parva llega a la troje?

- «Tres cuartos DE dos tercios» es un producto: no se juntan, se toma dentro.
- Multiplico arriba con arriba: 2 · 3 = 6.
- Multiplico abajo con abajo: 3 · 4 = 12.
- Queda 6/12, que se simplifica a 1/2.
- Media parva. Menos que dos tercios y menos que tres cuartos, como tenía que ser.

**Autoexplicación (focal):** {'step_index': 4, 'prompt': '¿Por qué el resultado tiene que ser menor que las dos fracciones de partida?'}

#### Cuando la letra se cancela sola · *resuelto*

Cada haz da 3/x de medida de grano, y en la era se trillan x/5 haces por jornada. ¿Cuánto grano sale por jornada?

- Multiplico arriba: 3 · x = 3x. Y abajo: x · 5 = 5x.
- Queda 3x/5x.
- Arriba y abajo todo son factores, así que la x se puede tachar.
- Queda 3/5 de medida por jornada, sin ninguna x.
- Tiene sentido: cuantos más haces, menos grano por haz — los dos efectos se compensan.

#### El escriba que buscó doceavos · *TRAMPA*

Vuelve el registro de la apertura: dos tercios de la parva, y tres cuartos de eso. El escriba pasó las dos a doceavos, las sumó y anotó 17/12.

- Tomo una parte de algo que ya era una parte: no puede salir más de lo que había.
- 17/12 es más que la parva entera, así que la cuenta no era esa.
- Regla para no volver a caer: antes de operar, pregunta si es «y» (suma) o «de» (producto).

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{2}{3}\\cdot\\dfrac{3}{4}=\\dfrac{17}{12}', 'right_latex': '\\dfrac{2}{3}\\cdot\\dfrac{3}{4}=\\dfrac{6}{12}=\\dfrac{1}{2}', 'rows': [{'wrong': 'Igualar denominadores y sumar', 'right': 'Multiplicar arriba con arriba y abajo con abajo'}, {'wrong': '\\dfrac{17}{12}\\ \\text{es más de una parva entera}', 'right': '\\dfrac{1}{2}\\ \\text{es media parva, y cabe}'}]}
**¿Por qué falla?:** Explica por qué un resultado mayor que 1 delata el error sin necesidad de rehacer la cuenta, y di qué operación sí habría dado 17/12.


### A6. Puente — parcialmente resueltos

El registro de la era va empezado; completa los huecos.

**P1** (*falta: last*) — Multiplica $\dfrac{3}{5}\cdot\dfrac{2}{7}$ y di cuánto vale el denominador.

- dado: $\dfrac{3\cdot 2}{5\cdot 7}$
- hueco `P1-b1`: $5\cdot 7=$ → `35`

**P2** (*falta: middle*) — Multiplica $\dfrac{4}{9}\cdot\dfrac{3}{8}$ y simplifica.

- dado: $\dfrac{12}{72}$
- hueco `P2-b1`: $72\div 12=$ → `6`
- hueco `P2-b2`: $\text{numerador simplificado}=$ → `1`

**P3** (*falta: statement_only*) — Solo el planteamiento: $\dfrac{2}{5}$ de una parva de $\,30\,$ medidas, y de eso la mitad va a la troje. ¿Cuántas medidas llegan?

- hueco `P3-b1`: $\dfrac{1}{2}\cdot\dfrac{2}{5}\cdot 30=$ → `6`


### A7. Comparación de métodos

**Dos maneras de multiplicar y simplificar**

$\dfrac{8}{15}\cdot\dfrac{25}{12}$. Los dos llegan a lo mismo con números muy distintos.

- **Método 1 · Multiplicar y simplificar al final** — 
- **Método 2 · Simplificar en cruz antes** — 

**Pregunta:** ¿Por qué se puede cruzar el 8 de arriba con el 12 de abajo, si están en fracciones distintas?

**Insight:** Porque al multiplicar todo acaba en un solo numerador y un solo denominador: el 8 y el 12 van a quedar arriba y abajo de la MISMA fracción, así que tacharlos ahora o después da igual. Ojo con generalizarlo: esto vale solo cuando la operación es un producto. En una suma, cruzar no significa nada — ahí no se juntan en una sola fracción hasta el final.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto es $\dfrac{3}{4}\cdot\dfrac{2}{7}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $\dfrac{6}{28}=\dfrac{3}{14}$ | — |
| 　 | `common` | $\dfrac{29}{28}$ | `busca_comun_denominador_para_multiplicar` |
| 　 | `num` | $\dfrac{6}{7}$ | `olvida_multiplicar_los_denominadores` |
| 　 | `cross` | $\dfrac{21}{8}$ | `invierte_al_multiplicar` |

Escalera de pistas:
1. Arriba con arriba y abajo con abajo.
2. 3 · 2 = 6 y 4 · 7 = 28.
3. 6/28 se simplifica entre 2.

**E2**

Multiplica $\dfrac{2}{5}\cdot\dfrac{4}{9}$ y escribe el resultado como fracción, así: 5/12. No dejes espacios.

Respuesta: `8/45`

Escalera de pistas:
1. No hace falta denominador común.
2. 2 · 4 = 8.
3. 5 · 9 = 45.

**E3**

Una parva da 45 medidas de grano. Tres quintos son grano limpio y, de eso, dos tercios van a la troje. ¿Cuántas medidas llegan a la troje?

Respuesta: `18`

Escalera de pistas:
1. «De» significa por: multiplica las dos fracciones.
2. 2/3 · 3/5 = 6/15 = 2/5.
3. 2/5 de 45 son …

**E4**

Un escriba calcula $\dfrac{1}{2}\cdot\dfrac{1}{3}$ pasándolas a sextos y anota $\dfrac{5}{6}$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `op` | Sumó en vez de multiplicar: el producto es $\dfrac{1}{6}$ | — |
| 　 | `common` | Eligió mal el denominador común | `busca_comun_denominador_para_multiplicar` |
| 　 | `simp` | Olvidó simplificar el resultado | `habito_deja_el_resultado_sin_simplificar` |
| 　 | `none` | No hay error | `busca_comun_denominador_para_multiplicar` |

Escalera de pistas:
1. La mitad de un tercio no puede ser casi la era entera.
2. Tomar una parte de una parte da menos, no más.
3. 5/6 es lo que sale de SUMARLAS.

**E5**

¿Verdadera o falsa? «Antes de multiplicar dos fracciones hay que ponerlas con el mismo denominador.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: eso es para sumar; multiplicando se opera arriba con arriba | — |
| 　 | `true` | Verdadera: es el primer paso con cualquier par de fracciones | `busca_comun_denominador_para_multiplicar` |
| 　 | `true_diff` | Verdadera solo si los denominadores son distintos | `busca_comun_denominador_para_multiplicar` |
| 　 | `false_never` | Falsa: el denominador común no sirve para nada en ninguna operación | `sobregeneraliza_producto_de_fracciones_algebraicas` |

Escalera de pistas:
1. Prueba con 1/2 · 1/3 de dos maneras.
2. Multiplicando da 1/6; igualando y sumando da 5/6.
3. Solo una de las dos es el producto.

**E6**

Selecciona TODAS las igualdades verdaderas.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $\dfrac{2}{3}\cdot\dfrac{5}{7}=\dfrac{10}{21}$ | — |
| ✅ | `b` | $\dfrac{3}{a}\cdot\dfrac{a}{4}=\dfrac{3}{4}$ | — |
| 　 | `c` | $\dfrac{2}{3}\cdot\dfrac{5}{7}=\dfrac{29}{21}$ | — |
| 　 | `d` | $\dfrac{2}{3}\cdot 6=\dfrac{2}{18}$ | — |

Escalera de pistas:
1. Comprueba cada una multiplicando arriba y abajo.
2. Un entero se escribe con 1 debajo, no debajo.
3. 29/21 es lo que sale de sumar, no de multiplicar.

**E7**

En la era se trillan h haces por jornada y cada haz da 8/h medidas de grano. Tres cuartos de lo que sale va a la troje. Con h = 5, ¿cuántas medidas llegan a la troje?

Respuesta: `6`

Escalera de pistas:
1. Multiplica los haces por lo que da cada uno: h · 8/h.
2. La h se cancela: salen 8 medidas, valga lo que valga h.
3. Tres cuartos de 8 son …


### A9. Cierre

*¿Se multiplica arriba con arriba?* — **Cuándo el denominador común sobra**

El denominador común es la herramienta de una operación concreta. Estas filas dicen en cuáles sirve y en cuáles estorba.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Arriba con arriba y abajo con abajo. No hace falta igualar nada. Es el caso focal. |
|  | ✅ | Todo acaba siendo factores de una sola fracción, así que la x se tacha. |
|  | ✅ | Cruzar el 8 con el 12 está permitido justo porque es un producto. |
|  | ~ (ámbar) | La regla es la misma, pero primero hay que ver el entero como 6/1. Sin ese paso, el 6 se coloca mal. |
|  | ✗ | Aquí sí hace falta el denominador común. La herramienta no es mala: era de otra operación. |
|  | ✗ | Tampoco se multiplica directo: primero hay que dar la vuelta a una de las dos. Eso es el silo. |

La cuarta fila es la que más se falla en un examen con prisa: un entero suelto no tiene aspecto de fracción y acaba multiplicando al denominador. Y las dos últimas dicen lo mismo desde fuera — cada operación tiene su ritual, y aplicar el de otra no es un rodeo, es un resultado distinto.

#### Pregunta de abstracción

¿Qué comparten los tres registros de la era trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `one_fraction` | En los tres el producto acaba siendo una sola fracción, y por eso se puede tachar entre ellas | — |
| 　 | `no_common` | En los tres el denominador común no hace ninguna falta | — |
| 　 | `bigger` | En los tres el resultado es mayor que las fracciones de partida | — |
| 　 | `same_rule` | En los tres se opera igual que en una suma | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas medidas llegan a la troje?
¿Cuántas medidas llegan a la troje?

Respuesta: `36`

Escalera de pistas:
1. Multiplica las dos fracciones antes de tocar el 60.
2. 3/4 · 4/5 = 3/5.
3. 3/5 de 60 son …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otra parva. Sin nota.

- **Mejoró:** Avance: ya distingues el «y» de la suma del «de» del producto.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué tomar una parte de otra parte da MENOS.

**PD1**

¿Cuánto es un tercio de 21?

Respuesta: `7`

**PD2**

¿Cuánto es $\dfrac{3}{4}\cdot\dfrac{1}{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $\dfrac{3}{8}$ | — |
| 　 | `same` | $\dfrac{3}{2}$ | `olvida_multiplicar_los_denominadores` |
| 　 | `sum` | $\dfrac{5}{4}$ | `busca_comun_denominador_para_multiplicar` |

**PD3**

¿En cuál de estas operaciones hace falta un denominador común?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | $\dfrac{1}{3}+\dfrac{1}{4}$ | — |
| 　 | `mult` | $\dfrac{1}{3}\cdot\dfrac{1}{4}$ | `confunde_la_operacion_dictada` |
| 　 | `both` | En las dos | `busca_comun_denominador_para_multiplicar` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-F03-PRODUCTO-D2` | `same` | `olvida_multiplicar_los_denominadores` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-D2` | `sum` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-D3` | `yes` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-D3` | `sometimes` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E1` | `common` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E1` | `num` | `olvida_multiplicar_los_denominadores` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E1` | `cross` | `invierte_al_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E4` | `common` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E4` | `simp` | `habito_deja_el_resultado_sin_simplificar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E4` | `none` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E5` | `true` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E5` | `true_diff` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-E5` | `false_never` | `sobregeneraliza_producto_de_fracciones_algebraicas` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-PD2` | `same` | `olvida_multiplicar_los_denominadores` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-PD2` | `sum` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-PD3` | `mult` | `confunde_la_operacion_dictada` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |
| `ALG-N1-F03-PRODUCTO-PD3` | `both` | `busca_comun_denominador_para_multiplicar` | Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
