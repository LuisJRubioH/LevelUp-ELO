# Nodo: «Divide a» no es lo mismo que «se divide entre» — PREALG-N4-C01-DIVISIBILIDAD

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N4-C01-DIVISIBILIDAD` |
| `concept_slug` | `divisibilidad` |
| Error focal | `invierte_la_direccion_de_la_divisibilidad` |
| Sala / edificio | Corinto · el reparto exacto |
| Guía | KatIA |
| Entra después de | `PREALG-N4-C00-PUERTO-DE-LA-POLIS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Corinto · Divisibilidad

**Título:** «Divide a» no es lo mismo que «se divide entre»

Toda división se puede hacer. Lo que no siempre se puede es hacerla SIN QUE SOBRE. Aquí vas a aprender a decidirlo sin dividir, con criterios que se leen de un vistazo, y a no invertir la frase — que es donde casi todo el mundo tropieza.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de bajar al muelle. Sin nota.

**D1**

Una maroma de 36 codos se corta en tramos de 4 codos. ¿Cuántos tramos salen?

Respuesta: `9`

**D2**

¿Cuál de estas frases es verdadera?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three_div_12` | 3 divide a 12 | — |
| 　 | `twelve_div_3` | 12 divide a 3 | `invierte_la_direccion_de_la_divisibilidad` |
| 　 | `both` | Las dos | `invierte_la_direccion_de_la_divisibilidad` |

**D3**

¿Cómo sabes si un número es divisible entre 2 sin dividir?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `last_even` | Mirando si termina en cifra par | — |
| 　 | `sum` | Sumando sus cifras | `confunde_criterio_de_2_con_el_de_3` |
| 　 | `cannot` | No se puede saber sin dividir | `no_conoce_criterios` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el muelle de Corinto* — **El cordelero que cortó de más**

En el muelle de Corinto trabaja un cordelero. Las maromas le llegan en piezas largas y él las corta en tramos iguales para los aparejos de cada barco. La regla del gremio es dura: un tramo corto sobrante no se vende, se tira.

Esta mañana le pidieron tramos de 6 codos de una maroma de 92. El cordelero miró el 92, vio que era par, dijo «6 también es par, esto sale exacto» y cortó. Le sobraron 2 codos que fueron a la basura.

**Pregunta:** ¿Cómo se sabe, antes de cortar, si el reparto va a salir sin desperdicio?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Si los dos son pares, sale exacto | — |
| 　 | `b` | Solo dividiendo y viendo si sobra | — |
| 　 | `c` | Hay señales en el número que lo dicen antes | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos maromas, dos finales distintos**

Abajo, dos cortes con la misma medida de tramo. Fíjate en qué queda al final de cada maroma.

- **Caso que funciona** — No sobra nada. Se dice: 6 divide a 96.
- **Caso que rompe la expectativa** — Sobran 2 codos. La división existe, pero 6 NO divide a 92.

**Resolución:** Las dos divisiones se pueden hacer; la diferencia está en el residuo. Que los dos números sean pares no basta: 92 y 6 lo son y aun así sobra. La divisibilidad no es una propiedad de un número suelto, es una relación entre dos, y tiene DIRECCIÓN.

**Definición — La divisibilidad**

$$b\mid a\iff\exists\,k\in\mathbb{Z}:\ a=b\times k$$

b divide a a (se escribe b | a) si existe un entero k tal que a = b × k; es decir, si la división a ÷ b tiene residuo 0. El divisor es el pequeño y el múltiplo es el grande: la frase no se puede dar vuelta.

| Símbolo | Se lee | Significa |
|---|---|---|
| `b\mid a` | b divide a a | b es el tramo, a es la maroma entera |
| `b\nmid a` | b no divide a a | el corte deja desperdicio |
| `k` | el cociente | cuántos tramos salen; tiene que ser entero |
| `r=0` | residuo cero | la marca de que el reparto fue exacto |
| `b\mid a\ \Rightarrow\ b\le a` | el divisor no supera al múltiplo | para a positivo: por eso 12 no divide a 3 |

### A5. Ejemplos resueltos

#### Decidir sin dividir · *resuelto*

El cordelero tiene una maroma de 1 350 codos. ¿Puede cortarla en tramos de 2? ¿De 5? ¿De 3? ¿De 9?

- Entre 2: miro la última cifra. Es 0, que es par → sí.
- Entre 5: la última cifra es 0 o 5. Es 0 → sí.
- Entre 3: sumo las cifras. 1+3+5+0 = 9, y 9 es múltiplo de 3 → sí.
- Entre 9: la misma suma, 9, ¿es múltiplo de 9? Sí → sí.
- Cuatro respuestas sin hacer ni una división. Los criterios de 2, 5 y 10 miran el final; los de 3 y 9 miran la suma.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se suman las cifras para el 3, pero para el 2 bastaba mirar la última. ¿Por qué unos criterios miran el final y otros la suma?'}

#### Quién divide a quién · *resuelto*

El registro del muelle dice «7 y 42». ¿Cuál de los dos divide al otro, y cómo se comprueba?

- Pruebo 7 | 42: ¿existe un entero k con 42 = 7 × k? Sí, k = 6.
- Pruebo 42 | 7: ¿existe un entero k con 7 = 42 × k? Tendría que ser k = 1/6, que no es entero.
- Así que 7 divide a 42, pero 42 no divide a 7.
- La comprobación rápida: para números positivos, el divisor nunca es mayor que el múltiplo.
- En una maroma: el tramo cabe en la cuerda, no la cuerda en el tramo.

#### El escriba que dio vuelta la frase · *TRAMPA*

El escriba del muelle anota: «El barco trae 8 fardos y cada fardo pesa 24 minas. Como 24 ÷ 8 = 3 sale exacto, escribo que 24 divide a 8».

- Comprueba con la definición: 24 | 8 querría decir que existe k con 8 = 24 × k.
- Ese k tendría que ser 1/3, que no es entero. Falso.
- Lo verdadero es 8 | 24, con k = 3: 24 = 8 × 3.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '24\\mid 8', 'right_latex': '8\\mid 24', 'rows': [{'wrong': '«24 dividido entre 8» se escribe 24 | 8', 'right': '24 ÷ 8 exacto se escribe 8 | 24: divide el pequeño'}, {'wrong': 'La barra vertical se lee igual que la de dividir', 'right': 'b | a se lee «b divide a a», no «b dividido entre a»'}]}
**¿Por qué falla?:** Escribe la afirmación correcta y di qué entero k la justifica.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Una maroma de 84 codos se corta en tramos de 4.

- dado: $84\div 4$
- dado: $\text{últimas dos cifras: }84,\ \text{y }84=4\times 21$
- hueco `P1-b1`: $\text{tramos que salen}=$ → `21`

**P2** (*falta: middle*) — ¿Es 738 divisible entre 9? Usa el criterio de la suma de cifras.

- dado: $7+3+8$
- hueco `P2-b1`: $7+3+8=$ → `18`
- hueco `P2-b2`: $18\div 9=$ → `2`

**P3** (*falta: statement_only*) — Solo el planteamiento: una maroma de 145 codos se corta en tramos de 6. ¿Cuántos codos se desperdician?

- hueco `P3-b1`: $145=6\times 24+r,\ r=$ → `1`


### A7. Comparación de métodos

**Dos caminos para decidir lo mismo**

¿Es $2\,346$ divisible entre 6? Las dos soluciones de abajo son correctas.

- **Método 1 · Dividir y mirar el residuo** — 
- **Método 2 · Descomponer el 6** — 

**Pregunta:** ¿Y si el número fuera 2 344? ¿Y por qué NO vale descomponer el 8 como 2 × 4 y aplicar los dos criterios?

**Insight:** El método 2 vale porque 2 y 3 no comparten divisores: son coprimos. Con 8 = 2 × 4 falla, porque 2 y 4 sí comparten el 2 — el número 12 pasa los dos criterios y no es divisible entre 8. Esa condición de «no compartir divisores» es lo que vas a formalizar en Atenas con el MCD (C05).

### A8. Práctica independiente (7 ítems)

**E1**

Una maroma de 72 codos se corta en tramos de 8. ¿Cuántos tramos salen?

Respuesta: `9`

Escalera de pistas:
1. Busca el entero k con 72 = 8 × k.
2. 8 × 8 = 64, se queda corto.
3. 8 × 9 = …

**E2**

Una maroma de 100 codos se corta en tramos de 7. ¿Cuántos codos se desperdician?

Respuesta: `2`

Escalera de pistas:
1. Busca el mayor múltiplo de 7 que no pase de 100.
2. 7 × 14 = 98.
3. 100 − 98 = …

**E3**

Selecciona TODOS los que dividen a 540.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | 2 | — |
| ✅ | `three` | 3 | — |
| ✅ | `four` | 4 | — |
| ✅ | `five` | 5 | — |
| 　 | `seven` | 7 | — |
| ✅ | `nine` | 9 | — |

Escalera de pistas:
1. Aplica un criterio por candidato en vez de dividir seis veces.
2. Suma de cifras: 5+4+0 = 9. Eso decide el 3 y el 9.
3. Para el 4, mira las dos últimas cifras: 40. Y el 7 no tiene criterio corto: divide.

**E4**

Un escriba anota «15 divide a 5, porque 15 ÷ 5 = 3». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `direction` | Dio vuelta la frase: lo correcto es 5 divide a 15 | — |
| 　 | `arith` | Se equivocó: 15 ÷ 5 no da 3 | `error_de_calculo_no_de_direccion` |
| 　 | `not_exact` | La división no es exacta, sobra algo | `confunde_residuo_con_direccion` |
| 　 | `none` | Ningún error, está bien | `invierte_la_direccion_de_la_divisibilidad` |

Escalera de pistas:
1. La cuenta está bien; lo que falla es cómo la escribió.
2. «15 divide a 5» querría decir que 5 = 15 × k con k entero.
3. Ese k sería 1/3. En b | a, el pequeño va primero.

**E5**

¿Es verdadera o falsa? «Si $a$ y $b$ son los dos pares, entonces $b$ divide a $a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_counter` | Falsa: 92 y 6 son pares y 6 no divide a 92 | — |
| 　 | `true` | Verdadera: dos pares siempre se reparten exacto | `paridad_implica_divisibilidad` |
| 　 | `false_never` | Falsa: dos pares nunca se dividen exacto | `niega_toda_divisibilidad_entre_pares` |
| 　 | `true_if_bigger` | Verdadera si a es mayor que b | `paridad_implica_divisibilidad` |

Escalera de pistas:
1. Para tumbar un «entonces» basta UN contraejemplo.
2. Vuelve a la maroma del cordelero.
3. 92 ÷ 6 deja residuo 2, y los dos números son pares.

**E6**

¿Cuál de estos números es divisible entre 6?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `n234` | 234 | — |
| 　 | `n232` | 232 | `olvida_uno_de_los_dos_criterios` |
| 　 | `n235` | 235 | `ignora_el_criterio_de_2` |
| 　 | `n239` | 239 | `ignora_el_criterio_de_2` |

Escalera de pistas:
1. 6 = 2 × 3: hay que pasar los DOS criterios.
2. Descarta primero los impares.
3. De los pares que quedan, suma las cifras y mira cuál da múltiplo de 3.

**E7**

El cordelero tiene una maroma de 203 codos y quiere tramos de 5. ¿Cuántos codos van a la basura?

Respuesta: `3`

Escalera de pistas:
1. El criterio del 5 mira la última cifra: 3 no es ni 0 ni 5, así que va a sobrar.
2. El mayor múltiplo de 5 que no pasa de 203 es 200.
3. 203 − 200 = …


### A9. Cierre

*Los criterios, uno por uno* — **¿Basta mirar el final del número?**

Los criterios no son magia ni hay que memorizarlos sueltos: se agrupan en dos familias según dónde hay que mirar.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Basta la última cifra: 0, 2, 4, 6 u 8. |
|  | ✅ | Basta la última cifra: 0 o 5. |
|  | ✅ | Basta la última cifra: 0. Es el criterio de 2 y el de 5 a la vez. |
|  | ~ (ámbar) | No basta la última: hay que mirar las DOS últimas. Aquí falla. |
|  | ✗ | Hay que sumar TODAS las cifras y ver si la suma es múltiplo de 3. |
|  | ✗ | La misma suma, pero exigiendo múltiplo de 9. Todo divisible entre 9 lo es entre 3, no al revés. |

Dos familias: los que miran el final (2, 5, 10 y, con dos cifras, el 4) y los que suman (3 y 9). Para el resto se divide y punto. En Rodas vas a mirar la misma relación desde el otro lado: no quién divide, sino qué se repite.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `remainder` | En los tres lo que decide es el residuo | — |
| 　 | `exact` | En los tres el reparto sale exacto | — |
| 　 | `relation` | En los tres se relacionan DOS números, no uno solo | — |
| 　 | `even` | En los tres los números son pares | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Qué tramo elige el cordelero?
¿Qué tramo elige el cordelero?

Respuesta: `9`

Escalera de pistas:
1. Empieza por el candidato más grande y baja.
2. Para el 9, suma las cifras: 9 + 1 + 8.
3. 18 es múltiplo de 9.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya escribes la divisibilidad en la dirección correcta.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre «b divide a a» y «a dividido entre b».

**PD1**

Una maroma de 56 codos se corta en tramos de 7. ¿Cuántos tramos salen?

Respuesta: `8`

**PD2**

¿Cuál de estas frases es verdadera?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `five_div_20` | 5 divide a 20 | — |
| 　 | `twenty_div_5` | 20 divide a 5 | `invierte_la_direccion_de_la_divisibilidad` |
| 　 | `both` | Las dos | `invierte_la_direccion_de_la_divisibilidad` |

**PD3**

¿Cómo sabes si un número es divisible entre 3 sin dividir?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | Sumando sus cifras y viendo si la suma es múltiplo de 3 | — |
| 　 | `last` | Mirando la última cifra | `confunde_criterio_de_2_con_el_de_3` |
| 　 | `cannot` | No se puede saber sin dividir | `no_conoce_criterios` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N4-C01-DIVISIBILIDAD-D2` | `twelve_div_3` | `invierte_la_direccion_de_la_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-D2` | `both` | `invierte_la_direccion_de_la_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-D3` | `sum` | `confunde_criterio_de_2_con_el_de_3` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-D3` | `cannot` | `no_conoce_criterios` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E4` | `arith` | `error_de_calculo_no_de_direccion` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E4` | `not_exact` | `confunde_residuo_con_direccion` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E4` | `none` | `invierte_la_direccion_de_la_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E5` | `true` | `paridad_implica_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E5` | `false_never` | `niega_toda_divisibilidad_entre_pares` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E5` | `true_if_bigger` | `paridad_implica_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E6` | `n232` | `olvida_uno_de_los_dos_criterios` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E6` | `n235` | `ignora_el_criterio_de_2` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-E6` | `n239` | `ignora_el_criterio_de_2` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-PD2` | `twenty_div_5` | `invierte_la_direccion_de_la_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-PD2` | `both` | `invierte_la_direccion_de_la_divisibilidad` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-PD3` | `last` | `confunde_criterio_de_2_con_el_de_3` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |
| `PREALG-N4-C01-DIVISIBILIDAD-PD3` | `cannot` | `no_conoce_criterios` | Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/04-prealg-n4-puerto/c01-divisibilidad-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
