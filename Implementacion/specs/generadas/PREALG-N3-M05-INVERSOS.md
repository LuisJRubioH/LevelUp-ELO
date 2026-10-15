# Nodo: Hay dos formas de cancelar, no una — PREALG-N3-M05-INVERSOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N3-M05-INVERSOS` |
| `concept_slug` | `inversos` |
| Error focal | `inverso_es_solo_cambiar_el_signo` |
| Sala / edificio | La Prensa de Contrapesos |
| Guía | KatIA |
| Entra después de | `PREALG-N3-M04-ELEMENTO-NEUTRO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La Prensa de Contrapesos · Inversos

**Título:** Hay dos formas de cancelar, no una

En el Calibre Cero encontraste los números que no cambian nada. Aquí buscas otra cosa: dado un número, la pieza que lo DEVUELVE a ese neutro. Y hay dos piezas distintas según la operación, aunque casi todo el mundo solo conoce una.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de cargar la prensa. Sin nota.

**D1**

¿Cuánto vale $9+(-9)$?

Respuesta: `0`

**D2**

¿Por cuánto hay que multiplicar $5$ para obtener $1$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `fifth` | un quinto | — |
| 　 | `minus_five` | menos cinco | `inverso_es_solo_cambiar_el_signo` |
| 　 | `one` | uno | `confunde_inverso_con_neutro` |
| 　 | `cannot` | No se puede | `niega_la_existencia_del_reciproco` |

**D3**

¿Qué es «el inverso» de un número?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `depends` | Depende de la operación: hay uno para sumar y otro para multiplicar | — |
| 　 | `sign` | El mismo número con el signo cambiado | `inverso_es_solo_cambiar_el_signo` |
| 　 | `fraction` | El número dado vuelta como fracción | `inverso_es_solo_dar_vuelta_la_fraccion` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la Prensa de Contrapesos* — **El brazo que hay que devolver al fiel**

La última estación de la fábrica es una prensa con balanza de brazo. Cada pieza que se carga inclina el brazo, y antes de seguir hay que devolverlo al fiel — la posición de equilibrio. Para eso está la caja de contrapesos.

El operario tiene un método infalible: si la pieza inclina a la derecha, pone una igual a la izquierda. Le funciona todos los días. Hoy la prensa cambió de modo: ya no suma cargas, las multiplica. El operario puso su contrapeso de siempre y el brazo se fue al otro extremo.

**Pregunta:** ¿Qué pieza cancela a un número cuando la prensa multiplica en vez de sumar?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | La misma: el número con el signo cambiado | — |
| 　 | `b` | Otra distinta | — |
| 　 | `c` | Multiplicando no se puede cancelar nada | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo 5, dos contrapesos distintos**

Abajo, una carga de 5 en los dos modos de la prensa. Fíjate en qué pieza devuelve el brazo al fiel en cada uno, y a qué número llega.

- **Caso que ya conoces** — El contrapeso es −5 y el fiel está en 0: el neutro de la suma.
- **Caso que rompe la expectativa** — El contrapeso es 1/5 y el fiel está en 1: el neutro del producto.

**Resolución:** Si el operario hubiera puesto −5 en el modo multiplicar, habría obtenido −25: el brazo al otro extremo. Cancelar no es «poner lo contrario»: es llegar al neutro DE ESA OPERACIÓN. Cambian el neutro y el contrapeso a la vez.

**Definición — Los elementos inversos**

$$a+(-a)=0\qquad a\times\dfrac{1}{a}=1\quad(a\neq 0)$$

El opuesto de a es el número que sumado a a da 0. El recíproco de a es el número que multiplicado por a da 1. Todo número tiene opuesto; todos menos el 0 tienen recíproco.

| Símbolo | Se lee | Significa |
|---|---|---|
| `-a` | el opuesto de a | el contrapeso de la suma: lleva al 0 |
| `\dfrac{1}{a}` | el recíproco de a | el contrapeso del producto: lleva al 1 |
| `a\neq 0` | a distinto de cero | el 0 no tiene recíproco: nada multiplicado por 0 da 1 |
| `-(-a)=a` | el opuesto del opuesto | quitar el contrapeso deja la carga original |
| `a-b=a+(-b)` | restar es sumar el opuesto | por eso la resta no necesitó reglas nuevas (E02) |
| `a\div b=a\times\dfrac{1}{b}` | dividir es multiplicar por el recíproco | el mismo truco, con el otro contrapeso (E04) |

### A5. Ejemplos resueltos

#### Devolver el brazo al fiel en los dos modos · *resuelto*

Una carga de 4 inclina el brazo. ¿Qué contrapeso hay que poner si la prensa suma? ¿Y si multiplica?

- Modo sumar: el fiel está en 0, así que busco x con 4 + x = 0. Es x = −4.
- Modo multiplicar: el fiel está en 1, así que busco x con 4 × x = 1.
- No es −4: 4 × (−4) = −16, y eso no es el fiel.
- Es 1/4, porque 4 × 1/4 = 4/4 = 1.
- Dos contrapesos distintos para la misma carga, porque el fiel está en sitios distintos.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se descarta el −4 para el modo multiplicar. ¿Qué tendría que cumplir el contrapeso correcto?'}

#### El recíproco de una carga que no es fracción · *resuelto*

La prensa carga una pieza de longitud √2 en modo multiplicar. ¿Cuál es su contrapeso, y sigue siendo irracional?

- El recíproco de √2 es 1/√2, porque al multiplicarlos da 1.
- Un recíproco con una raíz abajo es incómodo de medir. Se puede reescribir.
- Multiplico arriba y abajo por √2: (1 × √2) / (√2 × √2) = √2 / 2.
- Eso es exactamente lo mismo, escrito sin raíz en el denominador: se llama racionalizar.
- √2/2 ≈ 0,707: sigue siendo irracional. El recíproco de un irracional también lo es.

#### El operario que usó un solo contrapeso · *TRAMPA*

El operario deja la nota del turno: «Para cancelar cualquier carga, se pone la misma con el signo cambiado. Carga de 8, contrapeso −8. Vale para los dos modos de la prensa».

- Comprueba la nota: 8 × (−8) = −64. Ni siquiera se acerca al fiel.
- El fiel del modo multiplicar está en 1, no en 0.
- El número que multiplicado por 8 da 1 es 1/8 = 0,125.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '8\\times(-8)=1', 'right_latex': '8\\times\\dfrac{1}{8}=1', 'rows': [{'wrong': 'Cancelar es siempre cambiar el signo', 'right': 'Cancelar es llegar al neutro de esa operación'}, {'wrong': 'El contrapeso de 8 es −8 en cualquier modo', 'right': 'Es −8 sumando y 1/8 multiplicando'}]}
**¿Por qué falla?:** ¿Qué contrapeso cancela al 8 en el modo multiplicar? Escribe la igualdad completa.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Carga de 17 en modo sumar. Busca el contrapeso que devuelve el brazo al fiel.

- dado: $17+x=0$
- hueco `P1-b1`: $x=$ → `-17`

**P2** (*falta: middle*) — Carga de 4 en modo multiplicar.

- dado: $4\times x=1$
- hueco `P2-b1`: $x\text{ en decimal}=$ → `0,25`
- hueco `P2-b2`: $4\times 0{,}25=$ → `1`

**P3** (*falta: statement_only*) — Solo el planteamiento: carga de 0,2 en modo multiplicar. ¿Cuál es su recíproco?

- hueco `P3-b1`: $0{,}2\times x=1\ \Rightarrow\ x=$ → `5`


### A7. Comparación de métodos

**Dos caminos para la misma división**

¿Cuánto vale $\dfrac{3}{4}\div\dfrac{3}{8}$? Las dos soluciones de abajo son correctas.

- **Método 1 · Multiplicar por el recíproco** — 
- **Método 2 · Contar cuántos caben** — 

**Pregunta:** ¿Por qué el método 1 «da vuelta» la segunda fracción y no la primera?

**Insight:** Porque dividir entre b es multiplicar por el contrapeso de b, y el contrapeso del producto es el recíproco. La primera fracción no se cancela: se conserva. Esa regla que memorizaste como «se invierte y se multiplica» no es un truco — es esta propiedad, aplicada.

### A8. Práctica independiente (7 ítems)

**E1**

¿Qué contrapeso cancela una carga de 23 en modo sumar?

Respuesta: `-23`

Escalera de pistas:
1. El fiel del modo sumar está en 0.
2. Busca x con 23 + x = 0.
3. Es la misma carga apuntando al otro lado.

**E2**

¿Qué contrapeso cancela una carga de 8 en modo multiplicar? (decimal)

Respuesta: `0,125`

Escalera de pistas:
1. El fiel del modo multiplicar está en 1.
2. Es un octavo.
3. 1 ÷ 8 = …

**E3**

¿Cuál es el recíproco de $0{,}5$?

Respuesta: `2`

Escalera de pistas:
1. Busca el número que multiplicado por 0,5 da 1.
2. 0,5 es un medio.
3. El recíproco de 1/2 es 2/1.

**E4**

Un operario anota «El recíproco de $7$ es $-7$, porque $7\times(-7)$ cancela». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `reciprocal` | El recíproco es 1/7; el −7 es el opuesto, y cancela sumando | — |
| 　 | `sign` | Debía ser 7, no −7 | `confunde_inverso_con_neutro` |
| 　 | `arith` | Se equivocó: 7 × (−7) da −48 | `habito_error_de_calculo_no_de_metodo` |
| 　 | `none` | Ningún error, está bien | `inverso_es_solo_cambiar_el_signo` |

Escalera de pistas:
1. Calcula 7 × (−7) y mira si llega al fiel del modo multiplicar.
2. 7 × (−7) = −49, y el fiel está en 1.
3. El número que multiplicado por 7 da 1 es 1/7.

**E5**

¿Es verdadera o falsa? «Todo número tiene recíproco.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_zero` | Falsa: el 0 no tiene, porque nada multiplicado por 0 da 1 | — |
| 　 | `true` | Verdadera: basta darle vuelta | `olvida_la_excepcion_del_cero` |
| 　 | `false_negatives` | Falsa: los negativos no tienen recíproco | `reciproco_solo_para_positivos` |
| 　 | `false_irrationals` | Falsa: los irracionales no tienen recíproco | `irracional_no_tiene_reciproco` |

Escalera de pistas:
1. Busca un número donde el recíproco no exista.
2. Prueba con el 0: ¿hay algún x con 0 × x = 1?
3. Cualquier cosa por 0 da 0, nunca 1.

**E6**

La prensa carga 6 en modo multiplicar, se cancela con su recíproco y después se carga 19 en modo sumar. ¿En qué queda el brazo?

Respuesta: `20`

Escalera de pistas:
1. Resuelve primero la cancelación del modo multiplicar.
2. 6 × 1/6 = 1.
3. 1 + 19 = …

**E7**

¿Cuál es el recíproco de $\sqrt{2}$, escrito sin raíz en el denominador?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `rationalized` | raíz de 2 partido por 2 | — |
| 　 | `negative` | menos raíz de 2 | `inverso_es_solo_cambiar_el_signo` |
| 　 | `two` | 2 | `confunde_reciproco_con_cuadrado` |
| 　 | `half` | un medio | `confunde_reciproco_del_radicando` |

Escalera de pistas:
1. El recíproco es 1/√2. Falta quitarle la raíz de abajo.
2. Multiplica arriba y abajo por √2.
3. √2 × √2 = 2, así que queda √2 partido por 2.


### A9. Cierre

*Los inversos a lo largo de los conjuntos numéricos* — **¿Cada número del conjunto tiene su contrapeso dentro del conjunto?**

Esta propiedad no se recorre por operaciones sino por conjuntos: es la que explica por qué la escalera de N1 tuvo que crecer.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Ni opuesto ni recíproco: no hay natural que sumado a 5 dé 0. |
|  | ~ (ámbar) | Aparece el OPUESTO — para esto nacieron los enteros (B05) — pero el recíproco sigue fuera. |
|  | ✅ | Aparece el RECÍPROCO: dar vuelta la fracción. Para esto nacieron los racionales (B06). Única excepción: el 0. |
|  | ~ (ámbar) | Cada irracional tiene opuesto y recíproco, y los DOS son irracionales — racionalizar es exactamente eso. Pero los neutros 0 y 1 no viven aquí, así que el hogar completo son los reales. |
|  | ✅ | Todo real distinto de 0 tiene los dos contrapesos, y los neutros están dentro. |
|  | ✅ | También cierra, y aquí el recíproco de i resulta ser su opuesto. Desvío opcional (B09). |

Mira lo que acabas de reconstruir: ℤ existe porque a ℕ le faltaban los opuestos, y ℚ existe porque a ℤ le faltaban los recíprocos. La escalera de conjuntos que recorriste en N1 es, en el fondo, la búsqueda de estos dos contrapesos.

#### Pregunta de abstracción

¿Qué comparten el opuesto y el recíproco?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `to_neutral` | Los dos llevan el resultado al neutro de su operación | — |
| 　 | `sign` | Los dos cambian el signo del número | — |
| 　 | `cancel` | Los dos cancelan al número, cada uno en su operación | — |
| 　 | `always` | Los dos existen para cualquier número sin excepción | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿En qué número queda el brazo?
¿En qué número queda el brazo?

Respuesta: `8`

Escalera de pistas:
1. Resuelve cada paréntesis por separado antes de sumar.
2. 12 × 1/12 = 1, no 0.
3. 30 + (−30) = 0, y luego 1 + 0 + 7 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya eliges el contrapeso según dónde esté el fiel.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre el opuesto y el recíproco.

**PD1**

¿Cuánto vale $14+(-14)$?

Respuesta: `0`

**PD2**

¿Por cuánto hay que multiplicar $3$ para obtener $1$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `third` | un tercio | — |
| 　 | `minus_three` | menos tres | `inverso_es_solo_cambiar_el_signo` |
| 　 | `one` | uno | `confunde_inverso_con_neutro` |

**PD3**

¿Es verdadera? El opuesto de $7$ es $-7$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `sobregeneraliza_inversos` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N3-M05-INVERSOS-D2` | `minus_five` | `inverso_es_solo_cambiar_el_signo` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-D2` | `one` | `confunde_inverso_con_neutro` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-D2` | `cannot` | `niega_la_existencia_del_reciproco` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-D3` | `sign` | `inverso_es_solo_cambiar_el_signo` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-D3` | `fraction` | `inverso_es_solo_dar_vuelta_la_fraccion` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E4` | `sign` | `confunde_inverso_con_neutro` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E4` | `arith` | `habito_error_de_calculo_no_de_metodo` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E4` | `none` | `inverso_es_solo_cambiar_el_signo` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E5` | `true` | `olvida_la_excepcion_del_cero` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E5` | `false_negatives` | `reciproco_solo_para_positivos` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E5` | `false_irrationals` | `irracional_no_tiene_reciproco` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E7` | `negative` | `inverso_es_solo_cambiar_el_signo` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E7` | `two` | `confunde_reciproco_con_cuadrado` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-E7` | `half` | `confunde_reciproco_del_radicando` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-PD2` | `minus_three` | `inverso_es_solo_cambiar_el_signo` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-PD2` | `one` | `confunde_inverso_con_neutro` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |
| `PREALG-N3-M05-INVERSOS-PD3` | `false` | `sobregeneraliza_inversos` | Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/03-prealg-n3-fabrica/m05-inversos-katia-v5.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
