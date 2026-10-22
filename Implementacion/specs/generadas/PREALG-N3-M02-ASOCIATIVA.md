# Nodo: Los paréntesis no son adorno — PREALG-N3-M02-ASOCIATIVA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N3-M02-ASOCIATIVA` |
| `concept_slug` | `asociativa` |
| Error focal | `parentesis_son_decorativos` |
| Sala / edificio | El Horno de Fundición |
| Guía | KatIA |
| Entra después de | `PREALG-N3-M01-CONMUTATIVA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El Horno de Fundición · Asociativa

**Título:** Los paréntesis no son adorno

En la prensa aprendiste a mover números de sitio. Aquí no se mueve nada: se cambia qué va JUNTO con qué. Vas a ver por qué en la suma da igual y en la resta cambia el resultado, y qué hacer cuando quieres reagrupar de todas formas.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el horno. Sin nota.

**D1**

¿Cuánto vale $(2+3)+7$?

Respuesta: `12`

**D2**

¿Dan lo mismo $(10-4)-3$ y $10-(4-3)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No | — |
| 　 | `yes` | Sí | `parentesis_son_decorativos` |

**D3**

¿Para qué sirven los paréntesis en una cuenta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `order` | Para decir qué se calcula primero | — |
| 　 | `clarity` | Solo para que se lea más claro | `parentesis_son_decorativos` |
| 　 | `decor` | No sirven para nada, se pueden quitar | `parentesis_son_decorativos` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el Horno de Fundición* — **Las tandas del horno**

La segunda estación es un horno de crisol con tres carriles de carga. Los lingotes no entran de uno en uno: entran por TANDAS. El fundidor decide qué lingotes van juntos en cada tanda y en qué orden se funden las tandas.

Con lingotes iguales daba igual cómo los agrupara, así que el fundidor dejó de pensarlo. Hoy le llegaron tres piezas donde una hay que RETIRAR del crisol, no añadirla. Agrupó como siempre, y la colada salió con un peso que no era el encargado.

**Pregunta:** ¿Cambiar qué va junto con qué puede cambiar el resultado?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | No: los paréntesis solo ordenan la lectura | — |
| 　 | `b` | Sí, en algunas operaciones | — |
| 　 | `c` | Sí, siempre cambia | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Los mismos tres lingotes, dos agrupaciones**

Abajo están los mismos tres números agrupados de las dos formas posibles, primero con el horno sumando y después restando.

- **Caso que confirma lo que esperas** — Las dos agrupaciones dan la misma colada.
- **Caso que rompe la expectativa** — 3 contra 9. Cambió qué iba con qué, y cambió la colada.

**Resolución:** En la segunda, el paréntesis del centro decidió si el 3 se retiraba del crisol o se le devolvía al 4. Los paréntesis no describen la cuenta: la construyen. Cuando todas las piezas entran (suma, producto) da igual agrupar; cuando alguna sale (resta, división), no.

**Definición — La propiedad asociativa**

$$(a+b)+c=a+(b+c)\qquad (a\times b)\times c=a\times(b\times c)$$

Una operación es asociativa si cambiar la agrupación de tres números no cambia el resultado. La suma y la multiplicación lo son; la resta, la división y la potenciación no.

| Símbolo | Se lee | Significa |
|---|---|---|
| `(\ )` | paréntesis | la tanda: lo que se funde junto y primero |
| `a,b,c` | tres operandos | hacen falta tres para que la agrupación signifique algo |
| `(a-b)-c\neq a-(b-c)` | la resta no asocia | el paréntesis decide de quién se resta c |
| `a-(b-c)=a-b+c` | quitar el paréntesis cambia signos | el signo de menos delante voltea todo lo de dentro |
| `a+(-b)+(-c)` | todo como suma | el truco: con cada número llevando su signo, sí puedes reagrupar |

### A5. Ejemplos resueltos

#### La tanda que se puede rearmar · *resuelto*

El horno debe fundir lingotes de 2, 5 y 19, sumando sus pesos. ¿Conviene alguna agrupación concreta?

- Primera agrupación: (2 + 5) + 19 = 7 + 19 = 26.
- Segunda agrupación: 2 + (5 + 19) = 2 + 24 = 26.
- Coinciden, así que el fundidor puede armar las tandas como le convenga.
- Y le conviene: si hubiera un 8 y un 2, agruparlos primero da 10 y el resto sale solo.
- La asociativa no cambia el resultado; cambia cuánto trabajo cuesta llegar a él.

**Autoexplicación (focal):** {'step_index': 3, 'prompt': 'En el paso 4 se agrupa buscando un 10. ¿Por qué eso es legal aquí y no lo sería en una resta?'}

#### Cómo reagrupar una resta sin romperla · *resuelto*

El horno debe procesar 30, retirar 7 y retirar 13. El fundidor quiere agrupar los dos retiros en una sola tanda. ¿Puede?

- Tal cual está, la resta no asocia: no puedo escribir 30 − (7 − 13), eso daría 36.
- El truco es dejar de ver restas: cada retiro es una suma de un número negativo.
- 30 − 7 − 13 = 30 + (−7) + (−13). Ahora TODO son sumas.
- Y la suma sí asocia: 30 + ((−7) + (−13)) = 30 + (−20) = 10.
- Agrupé los dos retiros en una sola tanda y el resultado se mantuvo: 10.

#### El fundidor que movió el paréntesis · *TRAMPA*

El fundidor anota: «Encargo de 30, retirar 7 y retirar 13. Agrupo los dos retiros: 30 − (7 − 13) = 30 − (−6) = 36». Y funde 36.

- Sin calcular: se parte de 30 y se retira dos veces. El resultado TIENE que ser menor que 30.
- 36 es mayor que 30, así que está mal antes de revisar la aritmética.
- La agrupación correcta es 30 − (7 + 13) = 30 − 20 = 10: bajo un signo menos, los dos retiros se suman.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '30-7-13=36', 'right_latex': '30-7-13=30-(7+13)=10', 'rows': [{'wrong': 'Los retiros se agrupan tal cual dentro del paréntesis', 'right': 'Al agrupar bajo un menos, los retiros se SUMAN entre sí'}, {'wrong': 'Retirar 7 y luego 13 deja más de lo que había', 'right': 'Retirar dos veces siempre deja menos: 10, no 36'}]}
**¿Por qué falla?:** ¿Por qué 36 es imposible sin hacer ninguna cuenta? Escribe la agrupación correcta.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Agrupa para calcular rápido: lingotes de 37, 8 y 2, sumando.

- dado: $37+(8+2)$
- dado: $8+2=10$
- hueco `P1-b1`: $37+10=$ → `47`

**P2** (*falta: middle*) — El horno procesa 50, retira 12 y retira 8. Agrupa los dos retiros.

- dado: $50-12-8=50-(12+8)$
- hueco `P2-b1`: $12+8=$ → `20`
- hueco `P2-b2`: $50-20=$ → `30`

**P3** (*falta: statement_only*) — Solo el planteamiento: el horno eleva. Calcula primero (2 elevado a 3) elevado a 2 y comprueba si coincide con 2 elevado a (3 elevado a 2).

- hueco `P3-b1`: $(2^{3})^{2}=$ → `64`
- hueco `P3-b2`: $2^{(3^{2})}=$ → `512`


### A7. Comparación de métodos

**Dos caminos para la misma colada**

¿Cuánto vale $80-25-15$? Las dos soluciones de abajo son correctas.

- **Método 1 · De izquierda a derecha** — 
- **Método 2 · Agrupar los retiros** — 

**Pregunta:** ¿Por qué en el método 2 los retiros se SUMAN dentro del paréntesis, si en la cuenta original los dos eran restas?

**Insight:** Porque el signo menos de delante afecta a todo el paréntesis. Retirar 25 y luego retirar 15 es retirar 40 de una vez: los retiros se acumulan. Si escribieras 80 − (25 − 15) estarías diciendo otra cosa — que al 25 le devuelves 15 antes de retirarlo — y daría 70.

### A8. Práctica independiente (7 ítems)

**E1**

Agrupa para calcular rápido: 46 + 7 + 3. ¿Cuánto da?

Respuesta: `56`

Escalera de pistas:
1. ¿Qué dos números juntos dan un número redondo?
2. 7 + 3 = 10.
3. 46 + 10 = …

**E2**

El horno procesa 90, retira 34 y retira 26. ¿Cuánto queda?

Respuesta: `30`

Escalera de pistas:
1. Los dos retiros se pueden juntar en uno solo.
2. 34 + 26 = 60.
3. 90 − 60 = …

**E3**

¿Cuánto vale $12-(5-4)$?

Respuesta: `11`

Escalera de pistas:
1. Lo de dentro del paréntesis va primero.
2. 5 − 4 = 1.
3. 12 − 1 = …

**E4**

Un fundidor anota «$60-15-5=60-(15-5)=50$». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sign` | Al agrupar bajo un menos, los retiros se suman: es 60 − 20 = 40 | — |
| 　 | `arith` | Se equivocó al restar: 60 − 10 son 40 | `error_de_calculo_no_de_agrupacion` |
| 　 | `order` | Debía calcular de derecha a izquierda | `invierte_el_sentido_de_lectura` |
| 　 | `none` | Ningún error, está bien | `parentesis_son_decorativos` |

Escalera de pistas:
1. Calcula la cuenta original sin paréntesis y compara.
2. 60 − 15 = 45, y 45 − 5 = 40.
3. El paréntesis convirtió el segundo retiro en una devolución.

**E5**

¿Es verdadera o falsa? «Para cualesquiera $a,b,c$: $(a-b)-c=a-(b-c)$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_c_zero` | Falsa: solo coinciden cuando c = 0 | — |
| 　 | `true` | Verdadera: los paréntesis no cambian el resultado | `parentesis_son_decorativos` |
| 　 | `false_never` | Falsa: nunca pueden coincidir | `olvida_el_caso_neutro` |
| 　 | `true_positive` | Verdadera si los tres son positivos | `parentesis_son_decorativos` |

Escalera de pistas:
1. Para tumbar un «cualesquiera» basta UN caso.
2. Prueba con a = 10, b = 4, c = 3.
3. (10−4)−3 = 3 pero 10−(4−3) = 9. ¿Y si c fuera 0?

**E6**

Agrupa para calcular de cabeza: 4 × 23 × 25. ¿Cuánto da?

Respuesta: `2300`

Escalera de pistas:
1. La multiplicación sí asocia: agrupa lo que te convenga.
2. 4 × 25 = 100.
3. 100 × 23 = …

**E7**

¿Cuál de estas reescrituras de $a-b-c$ es correcta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum_group` | a − (b + c) | — |
| 　 | `diff_group` | a − (b − c) | `parentesis_son_decorativos` |
| 　 | `plus` | a + (b + c) | `ignora_el_signo_al_agrupar` |
| 　 | `swap` | c − b − a | `todas_las_operaciones_son_conmutativas` |

Escalera de pistas:
1. Prueba las cuatro con a = 10, b = 4, c = 3.
2. La original da 10 − 4 − 3 = 3.
3. Solo una de las cuatro da 3 también.


### A9. Cierre

*Validez a lo largo de las operaciones* — **¿En qué operaciones da igual cómo se agrupe?**

Misma escalera que en la prensa: las seis operaciones de la ciudad, otra pregunta.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Todas las piezas entran al crisol: el orden de las tandas no importa. |
|  | ✗ | El paréntesis decide de quién se resta. Truco: reescribir todo como sumas con signo. |
|  | ✅ | Por eso puedes buscar el par de factores cómodo antes de multiplicar. |
|  | ✗ | Mismo problema que la resta, y el truco es el mismo: pasar a multiplicar por el inverso. |
|  | ✗ | Por eso una torre de exponentes se lee de arriba abajo, no de izquierda a derecha. |
|  | ✗ | Tampoco asocia: el orden en que se anidan las raíces decide el índice final, así que cambiar el agrupamiento cambia el resultado. |

Las mismas dos que aguantaban el intercambio aguantan la reagrupación, y no es casualidad: son las que juntan sin distinguir papeles. En la Cinta Repartidora vas a ver qué pasa cuando se mezclan DOS operaciones distintas.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `grouping` | En los tres cambia qué número va junto con cuál | — |
| 　 | `same` | En los tres el resultado no cambia al reagrupar | — |
| 　 | `three` | Los tres necesitan al menos tres números para tener sentido | — |
| 　 | `order` | En los tres se intercambian dos números de sitio | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuánto queda en el crisol?
¿Cuánto queda en el crisol?

Respuesta: `40`

Escalera de pistas:
1. Los dos retiros se pueden juntar en uno solo.
2. Bajo el menos, se suman: 45 + 35 = 80.
3. 120 − 80 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya lees el paréntesis como parte de la cuenta, no como adorno.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué le pasa a un número cuando entra o sale de un paréntesis precedido de menos.

**PD1**

¿Cuánto vale $(4+6)+11$?

Respuesta: `21`

**PD2**

¿Dan lo mismo $(20-8)-5$ y $20-(8-5)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No | — |
| 　 | `yes` | Sí | `parentesis_son_decorativos` |

**PD3**

¿Es verdadera? $(3\times 4)\times 5=3\times(4\times 5)$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `sobregeneraliza_asociativa` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N3-M02-ASOCIATIVA-D2` | `yes` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-D3` | `clarity` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-D3` | `decor` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E4` | `arith` | `error_de_calculo_no_de_agrupacion` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E4` | `order` | `invierte_el_sentido_de_lectura` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E4` | `none` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E5` | `true` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E5` | `false_never` | `olvida_el_caso_neutro` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E5` | `true_positive` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E7` | `diff_group` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E7` | `plus` | `ignora_el_signo_al_agrupar` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-E7` | `swap` | `todas_las_operaciones_son_conmutativas` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-PD2` | `yes` | `parentesis_son_decorativos` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |
| `PREALG-N3-M02-ASOCIATIVA-PD3` | `false` | `sobregeneraliza_asociativa` | Calcula lo de dentro del paréntesis primero y compara con la cuenta original. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/03-prealg-n3-fabrica/m02-asociativa-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
