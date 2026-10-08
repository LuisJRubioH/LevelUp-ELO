# Nodo: Sumar lo mismo a los dos lados no conserva la forma — ALG-N1-R01-RAZONES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-R01-RAZONES` |
| `concept_slug` | `razones_y_proporciones` |
| Error focal | `escalado_aditivo` |
| Sala / edificio | La cuadrícula del canon |
| Guía | Iuty |
| Entra después de | `ALG-N1-F04-DIVISION` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La cuadrícula del canon · Razones y proporciones

**Título:** Sumar lo mismo a los dos lados no conserva la forma

Última sección del papiro. Un motivo hay que repetirlo grande en el muro y pequeño en el molde, y tiene que seguir siendo el mismo motivo. Lo que se conserva al cambiar de tamaño no es la diferencia: es el cociente.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de coger el pigmento. Sin nota.

**D1**

¿Por qué número hay que multiplicar $3$ para obtener $12$?

Respuesta: `4`

**D2**

¿Son equivalentes $\dfrac{2}{3}$ y $\dfrac{4}{6}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: las dos partes se multiplicaron por 2 | — |
| 　 | `no` | No: los números son distintos | `no_reconoce_fracciones_equivalentes` |
| 　 | `yes_add` | Sí, porque a las dos se les sumó lo mismo | `escalado_aditivo` |

**D3**

¿Describen $2:3$ y $4:6$ la misma relación?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `same` | Sí: por cada 2 de lo primero hay 3 de lo segundo, en las dos | — |
| 　 | `diff` | No: en la segunda hay más cantidad | `confunde_cantidad_con_relacion` |
| 　 | `unknown` | No se puede saber sin más datos | `confunde_cantidad_con_relacion` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el taller de Iuty* — **El relieve que salió deforme**

Iuty tiene delante dos versiones del mismo motivo: el boceto pequeño y el relieve grande que un aprendiz acaba de terminar sobre el muro. El grande no está mal hecho — está mal proporcionado. Algo creció más que lo demás.

«El aprendiz me dijo que lo había agrandado todo por igual», cuenta Iuty. «Y es verdad que le sumó lo mismo a cada medida. Ese fue el problema.»

**Pregunta:** ¿Qué tiene que mantenerse igual para que la forma no cambie?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | La diferencia entre las medidas | — |
| 　 | `b` | El cociente entre las medidas | — |
| 　 | `c` | El tamaño total del motivo | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos maneras de agrandar el mismo motivo**

Las dos parten de un motivo de 2 por 6 y lo hacen más grande. Fíjate en cuál sigue teniendo la misma forma.

- **Multiplicar por el mismo factor** — El cociente no se mueve. El motivo grande es el pequeño mirado de cerca.
- **Sumar la misma cantidad** — El cociente cambió de 1/3 a 1/2. El motivo se ensanchó: ya es otro.

**Resolución:** Sumar 2 a un 2 lo duplica; sumar 2 a un 6 apenas lo mueve. Por eso sumar lo mismo afecta más a la cantidad pequeña y desequilibra la relación. Multiplicar, en cambio, respeta el peso de cada una: eso es lo que conserva la forma.

**Definición — Razón y proporción**

$$\dfrac{a}{b}=\dfrac{c}{d}\iff a\cdot d=b\cdot c\quad (b,d\ne 0)$$

Una RAZÓN compara dos cantidades mediante una división: a : b es el cociente a/b. Dos razones forman una PROPORCIÓN cuando valen lo mismo. Se comprueba de dos maneras: buscando el factor de escala que lleva una a la otra, o viendo que los productos cruzados coinciden.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a:b` | a es a b | la razón entre dos cantidades, es decir su cociente |
| `\dfrac{a}{b}=\dfrac{c}{d}` | proporción | las dos razones valen lo mismo |
| `k` | factor de escala | el número que multiplica a AMBAS cantidades |
| `a\cdot d=b\cdot c` | productos cruzados | sirve aunque el factor no sea un número redondo |
| `b,d\ne 0` | no nulos | una razón es una división: el segundo término nunca es cero |

### A5. Ejemplos resueltos

#### Encontrar el factor de escala · *resuelto*

La mezcla del taller lleva 2 medidas de pigmento azul por cada 3 de base clara. Hace falta más cantidad y se preparan 6 medidas de base clara. ¿Cuánto azul?

- La razón que hay que conservar es 2 : 3.
- Miro qué le pasó a la base clara: de 3 a 6, o sea por 2. Ese es el factor de escala.
- Aplico el MISMO factor al azul: 2 · 2 = 4.
- La mezcla grande es 4 : 6.
- Compruebo que la razón se mantiene: 4/6 se simplifica a 2/3 ✓.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué hay que multiplicar las dos partes por el mismo número y no solo una?'}

#### Cuando el factor no salta a la vista · *resuelto*

Un molde mide 3 por 5 dedos. El maestro dice que el relieve del muro, de 9 por 15 palmos, conserva la proporción. ¿Tiene razón?

- Podría buscar el factor: de 3 a 9 es por 3, y de 5 a 15 también por 3. Coincide.
- Pero cuando el factor no es redondo conviene el otro camino: los productos cruzados.
- Multiplico en cruz: 3 · 15 = 45 y 5 · 9 = 45.
- Como los dos productos coinciden, las razones son iguales: sí es una proporción.
- El maestro tiene razón. El relieve es el molde a escala 3.

#### El aprendiz que le sumó 2 a todo · *TRAMPA*

El aprendiz explica cómo agrandó el relieve: «el motivo era 3 : 5. Le añadí 2 dedos a cada medida, que es lo justo, y quedó 5 : 7. Las dos crecieron lo mismo».

- Comparo los cocientes: 3/5 = 0,6 y 5/7 ≈ 0,714. No son iguales.
- Compruebo con productos cruzados: 3 · 7 = 21 frente a 5 · 5 = 25. Tampoco.
- Miro el crecimiento relativo: el 3 aumentó dos tercios de sí mismo; el 5, solo dos quintos. Por eso se ensanchó.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '3:5\\ \\to\\ 5:7', 'right_latex': '3:5\\ \\to\\ 6:10\\quad(\\text{factor }2)', 'rows': [{'wrong': 'Crecer lo mismo es sumar la misma cantidad', 'right': 'Crecer lo mismo es multiplicar por el mismo factor'}, {'wrong': '3 : 5 y 5 : 7 son la misma forma', 'right': '3 · 7 = 21 y 5 · 5 = 25: los productos cruzados no coinciden'}]}
**¿Por qué falla?:** Explica por qué el error es aditivo y no de cálculo, y da una ampliación correcta de 3 : 5.


### A6. Puente — parcialmente resueltos

La ampliación ya va empezada; completa los huecos.

**P1** (*falta: last*) — Completa la razón equivalente: $\dfrac{2}{5}=\dfrac{?}{20}$.

- dado: $5\cdot 4=20\ \Rightarrow\ \text{factor }4$
- hueco `P1-b1`: $2\cdot 4=$ → `8`

**P2** (*falta: middle*) — Halla el factor de escala que lleva $7:4$ a $?:24$ y completa.

- dado: $4\to 24$
- hueco `P2-b1`: $\text{factor}=24\div 4=$ → `6`
- hueco `P2-b2`: $7\cdot 6=$ → `42`

**P3** (*falta: statement_only*) — Solo el planteamiento: ¿forman proporción $\dfrac{6}{9}$ y $\dfrac{10}{15}$? Escribe el valor del producto cruzado $6\cdot 15$.

- hueco `P3-b1`: $6\cdot 15=$ → `90`


### A7. Comparación de métodos

**Dos maneras de decidir si hay proporción**

¿Forman proporción $4:6$ y $10:15$? Las dos comprobaciones son correctas.

- **Método 1 · Simplificar las dos razones** — 
- **Método 2 · Productos cruzados** — 

**Pregunta:** ¿Cuál es más rápido con estos números y cuál usarías con 7 : 11 y 21 : 33?

**Insight:** Con 4 : 6 el primero gana porque la simplificación salta a la vista. Con 7 : 11 no hay nada que simplificar y el factor 3 hay que adivinarlo; el producto cruzado lo resuelve sin buscar nada: 7 · 33 = 231 = 11 · 21.

### A8. Práctica independiente (7 ítems)

**E1**

Completa la razón equivalente: $\dfrac{3}{7}=\dfrac{?}{28}$.

Respuesta: `12`

Escalera de pistas:
1. Mira qué le pasó al 7 para llegar a 28.
2. 28 ÷ 7 = 4, así que el factor es 4.
3. Aplica el mismo factor arriba: 3 · 4 = …

**E2**

Un molde de 5 por 8 dedos se amplía hasta que el lado de 5 mide 20. ¿Cuánto mide entonces el lado de 8?

Respuesta: `32`

Escalera de pistas:
1. Primero el factor: de 5 a 20.
2. 20 ÷ 5 = 4.
3. 8 · 4 = …

**E3**

¿Forman proporción $\dfrac{4}{6}$ y $\dfrac{6}{9}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: $4\cdot 9=6\cdot 6=36$ | — |
| 　 | `no_diff` | No: la diferencia es 2 en una y 3 en la otra | `razon_como_diferencia` |
| 　 | `no_factor` | No: no hay ningún número entero que lleve 4 a 6 | `exige_factor_entero` |
| 　 | `cannot` | No se puede decidir sin simplificar | `exige_factor_entero` |

Escalera de pistas:
1. Simplifica las dos: ¿a qué se reducen?
2. 4/6 = 2/3 y 6/9 = 2/3.
3. También sirve el producto cruzado: 4 · 9 frente a 6 · 6.

**E4**

Un aprendiz amplía la mezcla 2 : 5 a 6 : 9 y dice que conserva la proporción. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `different_factors` | Multiplicó el 2 por 3 pero al 5 solo le sumó 4: los factores no coinciden | — |
| 　 | `order` | Cambió el orden de las cantidades | `habito_busca_el_error_donde_no_esta` |
| 　 | `too_big` | El error es que amplió demasiado | `confunde_cantidad_con_relacion` |
| 　 | `none` | No hay error: las dos cantidades crecieron | `escalado_aditivo` |

Escalera de pistas:
1. Calcula por separado qué factor lleva 2 a 6 y qué factor lleva 5 a 9.
2. 6 ÷ 2 = 3, pero 9 ÷ 5 = 1,8. No es el mismo.
3. Con factor 3 el segundo tendría que ser 15, no 9.

**E5**

¿Es verdadera o falsa? «Si a $3:5$ le sumo $2$ a cada parte, la relación se conserva.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: la relación se conserva multiplicando, no sumando | — |
| 　 | `true` | Verdadera: las dos partes crecieron lo mismo | `escalado_aditivo` |
| 　 | `true_small` | Verdadera si la cantidad sumada es pequeña | `escalado_aditivo` |
| 　 | `false_order` | Falsa: habría que sumar primero a la parte mayor | `razon_como_diferencia` |

Escalera de pistas:
1. Calcula los dos cocientes y compáralos.
2. 3/5 = 0,6 y 5/7 ≈ 0,714.
3. Si el cociente cambia, la forma cambia.

**E6**

Selecciona TODAS las razones equivalentes a $2:3$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $8:12$ | — |
| 　 | `b` | $4:5$ | — |
| ✅ | `c` | $10:15$ | — |
| 　 | `d` | $5:6$ | — |

Escalera de pistas:
1. Simplifica cada una y compárala con 2 : 3.
2. 8 : 12 se divide entre 4 y 10 : 15 entre 5.
3. 4 : 5 y 5 : 6 salen de SUMAR a 2 : 3, no de multiplicar.

**E7**

En un plano del taller, 2 dedos representan 14 codos reales. Un muro aparece dibujado con 9 dedos de largo. ¿Cuántos codos mide de verdad?

Respuesta: `63`

Escalera de pistas:
1. Cada dedo del plano son 14 ÷ 2 codos reales.
2. Un dedo son 7 codos.
3. 9 · 7 = …


### A9. Cierre

*¿Se conserva la forma?* — **Qué le puedes hacer a una razón sin cambiarla**

Partimos siempre de 2 : 6 y le hacemos algo a las dos cantidades. Solo algunas operaciones dejan el cociente donde estaba.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | 1/3 antes y 1/3 después. Es la operación que define ampliar. |
|  | ✅ | Reducir es lo mismo al revés: también conserva la forma. |
|  | ✗ | De 1/3 a 1/2. Es la trampa de este nodo: afecta más a la cantidad pequeña. |
|  | ✗ | De 1/3 a 2/3. Justo el relieve deforme del aprendiz. |
|  | ~ (ámbar) | El cociente cambia (1/3 pasa a 3), pero la relación se conserva leída al revés. Vale si se invierten las DOS. |
|  | ✅ | Aquí sumar sí vale, porque sumar a cada una su propio tamaño es multiplicar por 2 disfrazado. |

La última fila es la que desarma la trampa del todo: no es que sumar esté prohibido, es que hay que sumarle a cada cantidad una parte proporcional a ella misma. Cuando la suma es la misma para las dos, la pequeña sale ganando y la forma se pierde.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `quotient` | En los tres lo que hay que vigilar es el cociente, no la diferencia | — |
| 　 | `both` | En los tres la operación tiene que afectar a las DOS cantidades igual | — |
| 　 | `grow` | En los tres las dos cantidades crecen | — |
| 　 | `integer` | En los tres el factor de escala es un número entero | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos cuadros de alto?
¿Cuántos cuadros de alto?

Respuesta: `49`

Escalera de pistas:
1. Busca el factor con la pareja que conoces entera: 4 → 28.
2. El factor es 7.
3. 7 · 7 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otras medidas. Sin nota.

- **Mejoró:** Avance: ya escalas multiplicando y compruebas el cociente.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué sumar lo mismo a las dos partes deforma la figura.

**PD1**

¿Por qué número hay que multiplicar $4$ para obtener $20$?

Respuesta: `5`

**PD2**

¿Cuál es equivalente a $\dfrac{3}{4}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `nine` | $\dfrac{9}{12}$ | — |
| 　 | `five` | $\dfrac{5}{6}$ | `escalado_aditivo` |
| 　 | `seven` | $\dfrac{7}{8}$ | `escalado_aditivo` |

**PD3**

¿Forman proporción $5:8$ y $15:24$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: $5\cdot 24=8\cdot 15=120$ | — |
| 　 | `no` | No: la segunda es mucho más grande | `confunde_cantidad_con_relacion` |
| 　 | `no_diff` | No: las diferencias son 3 y 9 | `razon_como_diferencia` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-R01-RAZONES-D2` | `no` | `no_reconoce_fracciones_equivalentes` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-D2` | `yes_add` | `escalado_aditivo` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-D3` | `diff` | `confunde_cantidad_con_relacion` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-D3` | `unknown` | `confunde_cantidad_con_relacion` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E3` | `no_diff` | `razon_como_diferencia` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E3` | `no_factor` | `exige_factor_entero` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E3` | `cannot` | `exige_factor_entero` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E4` | `order` | `habito_busca_el_error_donde_no_esta` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E4` | `too_big` | `confunde_cantidad_con_relacion` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E4` | `none` | `escalado_aditivo` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E5` | `true` | `escalado_aditivo` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E5` | `true_small` | `escalado_aditivo` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-E5` | `false_order` | `razon_como_diferencia` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-PD2` | `five` | `escalado_aditivo` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-PD2` | `seven` | `escalado_aditivo` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-PD3` | `no` | `confunde_cantidad_con_relacion` | Compara los cocientes, no las diferencias: la forma vive en la división. |
| `ALG-N1-R01-RAZONES-PD3` | `no_diff` | `razon_como_diferencia` | Compara los cocientes, no las diferencias: la forma vive en la división. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
