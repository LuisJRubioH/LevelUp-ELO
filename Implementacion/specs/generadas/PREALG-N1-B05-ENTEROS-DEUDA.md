# Nodo: El signo es parte del número — PREALG-N1-B05-ENTEROS-DEUDA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B05-ENTEROS-DEUDA` |
| `concept_slug` | `enteros` |
| Error focal | `magnitud_sin_signo` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B04-NATURALES-CONTAR` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Segundo peldaño · Enteros

**Título:** El signo es parte del número

En el peldaño anterior la resta se quedó sin respuesta. Aquí vas a bajar del cero, a leer un número con su signo pegado, y a decidir cuál de dos deudas es peor — que no siempre es la que tiene el número más grande.

**Escena:** Los enteros incluyen los negativos, el cero y los positivos

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

¿Cuál de estos dos números es MAYOR?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `neg2` | −2 | — |
| 　 | `neg5` | −5 | `magnitud_sin_signo` |
| 　 | `equal` | Son iguales, solo cambia el tamaño | `ignora_el_signo` |

**D2**

Debías 8 dracmas y pagaste 8. ¿Cómo queda tu cuenta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | En 0: ni debes ni te deben | — |
| 　 | `still_owe` | Sigues debiendo 8 | `no_cancela_opuestos` |
| 　 | `they_owe` | Ahora te deben 8 a ti | `invierte_el_signo` |
| 　 | `sixteen` | La deuda sube a 16 | `suma_magnitudes` |

**D3**

El agua del pozo estaba 3 palmos bajo el brocal y bajó 4 palmos más. ¿Cuántos palmos bajo el brocal está ahora?

Respuesta: `7`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · El segundo peldaño* — **El libro del prestamista**

El prestamista del ágora lleva dos columnas en su libro: en una anota lo que le entregan, en la otra lo que le quedan debiendo. Nunca las mezcla, porque si las mezclara no sabría quién está en problemas.

Hoy llegan dos discípulos. Uno le queda debiendo 2 dracmas. El otro le queda debiendo 5. El prestamista quiere anotar en una sola columna quién está mejor, y no le alcanzan los números del peldaño anterior.

**Pregunta:** Si tuvieras que escribir las dos cuentas en UNA sola columna, ¿cómo distinguirías al que está mejor?

**Intento genuino** (`acotado`): Escoge lo que harías tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | El que debe 5 está mejor: su número es más grande | — |
| 　 | `b` | El que debe 2 está mejor: debe menos | — |
| 　 | `c` | No se puede comparar: las dos son deudas | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos columnas que se vuelven una recta**

Mira los dos casos de abajo. En los dos hay un 5, pero ese 5 significa cosas opuestas — y en cuanto los pones en la misma recta, se ve.

- **Caso que ya sabías** — Se mueve 5 pasos a la DERECHA del 0. Este es el 5 de siempre, el que ya contabas en el peldaño anterior.
- **Caso que rompe la expectativa** — Se mueve 5 pasos a la IZQUIERDA del 0. Mismo tamaño, dirección opuesta: −5 no es «5 en la otra columna», es otro número.

**Resolución:** El prestamista puede cerrar una columna. La recta hace el trabajo de las dos: a la derecha del 0 lo que se tiene, a la izquierda lo que se debe. Y ahora lo importante: en esa recta, −5 está MÁS A LA IZQUIERDA que −2. Más a la izquierda es menor. Deber 5 es peor que deber 2, y el número lo dice.

**Definición — Los números enteros**

$$\mathbb{Z}=\{\ldots,-3,-2,-1,0,1,2,3,\ldots\}$$

La frase del nodo: el signo no es un adorno que le cuelga al número — es parte del número. −5 y 5 son dos números distintos, no uno con dos disfraces.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\mathbb{Z}` | los enteros | del alemán Zahl, número: naturales, sus opuestos y el 0 |
| `-a` | el opuesto de a | el que está a la misma distancia del 0, al otro lado |
| `|a|` | valor absoluto de a | la distancia al 0, sin mirar el lado: |−5| = 5 |
| `<` | es menor que | está más a la izquierda en la recta |
| `\mathbb{N}\subset\mathbb{Z}` | ℕ está contenido en ℤ | no perdiste los naturales: siguen ahí, del lado derecho |
| `a+(-a)=0` | a más su opuesto da cero | pagar la deuda exacta deja la cuenta en 0 |

### A5. Ejemplos resueltos

#### El nivel del pozo · *resuelto*

El agua del pozo está 2 palmos bajo el brocal. En la sequía baja 6 palmos más. ¿En qué nivel queda respecto al brocal?

- Pongo el brocal en el 0: arriba positivo, abajo negativo.
- El nivel de partida está bajo el brocal → −2, no 2.
- «Baja 6 más» es moverse 6 pasos hacia la izquierda: −2 − 6.
- Desde −2 avanzo 6 hacia la izquierda: −3, −4, −5, −6, −7, −8.
- −2 − 6 = −8. El agua está 8 palmos bajo el brocal.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': 'En el paso 2 escribí −2 y no 2, aunque el enunciado dice «2 palmos». ¿Qué información se habría perdido con el 2 solo?'}

#### La cuenta del cantero · *resuelto*

El cantero le debe 9 dracmas al prestamista. Entrega 9 dracmas de una vez. ¿Cómo queda su cuenta?

- La deuda de 9 se escribe −9: está a la izquierda del 0.
- Entregar 9 es moverse 9 pasos hacia la derecha: −9 + 9.
- Desde −9 avanzo 9 hacia la derecha y caigo justo en el 0.
- −9 + 9 = 0. Ni debe ni le deben.
- 9 y −9 son opuestos: están a la misma distancia del 0, en lados contrarios.

#### La deuda que parecía mejor · *TRAMPA*

Un discípulo revisó el libro del prestamista y anotó esto. Está mal: «Yo debo −5 dracmas y mi hermano debe −2. Como 5 es mayor que 2, entonces −5 > −2: yo estoy mejor que él».

- Dibuja la recta y marca el 0, el −2 y el −5.
- Fíjate cuál de los dos queda más lejos del 0 hacia la izquierda.
- Más a la izquierda es menor, sin importar qué tan grande se vea el número.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '-5>-2', 'right_latex': '-5<-2', 'rows': [{'wrong': '5 es mayor que 2, así que −5 es mayor que −2', 'right': 'En la recta, −5 está más a la izquierda: es menor'}, {'wrong': 'Deber 5 es mejor que deber 2', 'right': 'Deber 5 es peor: te falta más para volver al 0'}]}
**¿Por qué falla?:** ¿Por qué −5 no es mayor que −2? Escribe la desigualdad corregida.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el procedimiento ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — El agua del pozo está 4 palmos bajo el brocal y sube 6 palmos tras la lluvia.

- dado: $\text{nivel inicial}=-4$
- dado: $-4+6$
- hueco `P1-b1`: $\text{Nivel final}=$ → `2`

**P2** (*falta: middle*) — El cantero debía 12 dracmas, entregó 5 y volvió a pedir 9 prestadas.

- dado: $\text{deuda inicial}=-12$
- hueco `P2-b1`: $-12+5=$ → `-7`
- hueco `P2-b2`: $-7-9=$ → `-16`

**P3** (*falta: statement_only*) — Solo el planteamiento: la polis se fundó en el año que llamamos 0. Un templo se levantó 40 años ANTES de la fundación y se derrumbó 25 años DESPUÉS de ella. ¿Cuántos años estuvo en pie?

- hueco `P3-b1`: $\text{Años en pie}=$ → `65`


### A7. Comparación de métodos

**Dos caminos para la misma cuenta**

El prestamista cierra el día así: le entregaron 7, prestó 12, le entregaron 3. ¿Cómo queda? Las dos soluciones de abajo son correctas.

- **Método 1 · Paso a paso en la recta** — 
- **Método 2 · Agrupar por signo** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿cuál de los dos preferirías si el prestamista tuviera 30 movimientos en el día?

**Insight:** El método 2 gana cuando hay muchos movimientos, porque reordena sin cambiar el resultado. Y eso es exactamente una propiedad que todavía no has demostrado: la conmutativa y la asociativa de la suma (N3-M01 y N3-M02). Aquí la estás usando de contrabando; allá vas a ver por qué está permitida.

### A8. Práctica independiente (7 ítems)

**E1**

El tejedor debía 6 dracmas y pidió 5 más. ¿Cuánto debe ahora? (Responde con el entero, con signo.)

Respuesta: `-11`

Escalera de pistas:
1. Deber se escribe con signo negativo.
2. Pedir más es alejarse del 0 hacia la izquierda.
3. −6 − 5: cuenta 5 pasos a la izquierda desde −6.

**E2**

El nivel del pozo está 9 palmos bajo el brocal y sube 9 palmos. ¿En qué nivel queda?

Respuesta: `0`

Escalera de pistas:
1. El brocal es el 0.
2. Subir es moverse hacia la derecha.
3. Un número y su opuesto se cancelan: dan 0.

**E3**

Ordena de MENOR a MAYOR: −7, 3, −1, 0. ¿Cuál es el orden correcto?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | −7 · −1 · 0 · 3 | — |
| 　 | `by_size` | 0 · −1 · 3 · −7 | `magnitud_sin_signo` |
| 　 | `neg_last` | 0 · 3 · −1 · −7 | `negativos_despues_de_positivos` |
| 　 | `neg1_first` | −1 · −7 · 0 · 3 | `magnitud_sin_signo` |

Escalera de pistas:
1. Dibuja la recta y marca los cuatro números.
2. El orden de menor a mayor es el orden de izquierda a derecha.
3. Todos los negativos van antes del 0, y −7 está más lejos que −1.

**E4**

Teano revisa el libro y lee: «Debía 10, entregó 4, luego debe −14». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `should_subtract` | Sumó la entrega a la deuda en vez de restarla: debe −6 | — |
| 　 | `sign` | El resultado debía ser positivo: +14 | `invierte_el_signo` |
| 　 | `initial` | La deuda inicial estaba mal escrita | `duda_del_dato_correcto` |
| 　 | `none` | Ningún error, está bien | `suma_magnitudes` |

Escalera de pistas:
1. Entregar dinero, ¿acerca o aleja del 0?
2. Acerca: mueve hacia la derecha, así que la deuda se achica.
3. −10 + 4 = −6, no −14.

**E5**

¿Es verdadera o falsa? $-8>-3$ porque $8>3$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_left` | Falsa: −8 está más a la izquierda, así que −8 < −3 | — |
| 　 | `true_size` | Verdadera: 8 es mayor que 3 | `magnitud_sin_signo` |
| 　 | `false_equal` | Falsa: los dos son negativos, así que son iguales | `ignora_el_signo` |
| 　 | `cannot` | No se pueden comparar dos negativos | `habito_evita_decidir` |

Escalera de pistas:
1. Marca −8 y −3 en la recta. ¿Cuál queda más a la izquierda?
2. Con negativos, cuanto más grande el número, más a la izquierda cae.
3. −8 < −3. El tamaño (8 > 3) es cierto, pero el orden se invierte.

**E6**

Dos discípulos deben dinero. Uno debe 4 dracmas, el otro debe 11. El prestamista perdona 4 dracmas a cada uno. ¿Quién queda mejor y por qué?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `first_zero` | El primero: llega a 0; el segundo sigue en −7 | — |
| 　 | `second_more` | El segundo: le perdonaron más deuda proporcionalmente | `confunde_cambio_con_estado` |
| 　 | `same` | Iguales: a los dos les perdonaron lo mismo | `confunde_cambio_con_estado` |
| 　 | `second_bigger` | El segundo: su número sigue siendo más grande | `magnitud_sin_signo` |

Escalera de pistas:
1. Calcula en qué número queda cada uno después del perdón.
2. −4 + 4 = 0 y −11 + 4 = −7.
3. 0 está más a la derecha que −7: quedar en 0 es quedar mejor.

**E7**

¿Cuál de estas operaciones NO tiene resultado dentro de los enteros?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `division` | 3 ÷ 4 | — |
| 　 | `sub` | 3 − 40 | `resta_no_cabe_en_enteros` |
| 　 | `sum` | −12 + 5 | `resta_no_cabe_en_enteros` |
| 　 | `mult` | −6 × 7 | `producto_negativo_no_es_entero` |

Escalera de pistas:
1. Haz las cuatro y mira cuál da un resultado que no es entero.
2. Restar, sumar y multiplicar enteros siempre dan enteros, aunque salgan negativos.
3. 3 ÷ 4 cae ENTRE 0 y 1: ahí no hay ningún entero. Ese es el próximo peldaño.


### A9. Cierre

*La escalera de la necesidad* — **¿Toda resta de dos números del conjunto vive en el conjunto?**

Este peldaño nació justo de la pregunta que quedó abierta en B04.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Se salía: no había nada por debajo del 0. |
|  | ✅ | El conjunto se hizo para esto: la resta ya siempre cabe. |
|  | ✅ | Pero la DIVISIÓN todavía no cabe en ℤ: eso abre B06. |

Cerraste la resta y ganaste una recta completa. Pero 3 ÷ 4 sigue sin tener casa: cae entre el 0 y el 1, donde no hay enteros. El siguiente peldaño nace de ese hueco.

#### Pregunta de abstracción

¿Qué estructura comparten los tres problemas de este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `line` | Los tres se resuelven moviéndose en una recta con el 0 en el centro | — |
| 　 | `sign` | En los tres el signo cambia el significado del número | — |
| 　 | `negative_result` | Los tres terminan en un número negativo | — |
| 　 | `money` | Los tres hablan de dinero | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Con qué número cierra la semana? (Con signo.)
¿Con qué número cierra la semana? (Con signo.)

Respuesta: `-6`

Escalera de pistas:
1. Separa lo que entra de lo que sale.
2. Entra 21 en total; sale 27 en total.
3. 21 − 27 se va por debajo del 0.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el número más grande puede ser el menor.

**PD1**

¿Cuál de estos dos números es MENOR?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `neg9` | −9 | — |
| 　 | `neg4` | −4 | `magnitud_sin_signo` |
| 　 | `equal` | Son iguales | `ignora_el_signo` |

**PD2**

Debías 14 dracmas y entregaste 14. ¿En qué número queda tu cuenta?

Respuesta: `0`

**PD3**

El agua estaba 5 palmos bajo el brocal y bajó 3 más. ¿En qué número queda respecto al brocal? (Con signo.)

Respuesta: `-8`

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B05-ENTEROS-DEUDA-D1` | `neg5` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-D1` | `equal` | `ignora_el_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-D2` | `still_owe` | `no_cancela_opuestos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-D2` | `they_owe` | `invierte_el_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-D2` | `sixteen` | `suma_magnitudes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E3` | `by_size` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E3` | `neg_last` | `negativos_despues_de_positivos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E3` | `neg1_first` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E4` | `sign` | `invierte_el_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E4` | `initial` | `duda_del_dato_correcto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E4` | `none` | `suma_magnitudes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E5` | `true_size` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E5` | `false_equal` | `ignora_el_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E5` | `cannot` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E6` | `second_more` | `confunde_cambio_con_estado` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E6` | `same` | `confunde_cambio_con_estado` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E6` | `second_bigger` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E7` | `sub` | `resta_no_cabe_en_enteros` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E7` | `sum` | `resta_no_cabe_en_enteros` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-E7` | `mult` | `producto_negativo_no_es_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-PD1` | `neg4` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B05-ENTEROS-DEUDA-PD1` | `equal` | `ignora_el_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b05-enteros-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
