# Nodo: Los divisores se acaban; los múltiplos no — PREALG-N4-C02-MULTIPLOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N4-C02-MULTIPLOS` |
| `concept_slug` | `multiplos` |
| Error focal | `los_multiplos_se_acaban` |
| Sala / edificio | Rodas · lo que se repite |
| Guía | KatIA |
| Entra después de | `PREALG-N4-C01-DIVISIBILIDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Rodas · Múltiplos

**Título:** Los divisores se acaban; los múltiplos no

En Corinto miraste quién divide a quién. Aquí das vuelta la mirada: dado un número, ¿qué números lo contienen un número exacto de veces? La respuesta tiene una propiedad que la de los divisores no tiene, y esa diferencia es todo el nodo.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de subir al faro. Sin nota.

**D1**

La campana suena cada 4 golpes de remo. ¿En qué golpe suena la quinta vez?

Respuesta: `20`

**D2**

¿Cuántos múltiplos tiene el número 6?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `infinite` | Infinitos | — |
| 　 | `four` | Cuatro: 1, 2, 3 y 6 | `confunde_multiplo_con_divisor` |
| 　 | `depends` | Depende de hasta dónde cuentes | `los_multiplos_se_acaban` |

**D3**

¿Cuál es el múltiplo MÁS PEQUEÑO de 7 que es positivo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `seven` | 7 | — |
| 　 | `one` | 1 | `confunde_multiplo_con_divisor` |
| 　 | `fourteen` | 14 | `excluye_el_numero_de_sus_multiplos` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el faro de Rodas* — **La campana que nunca terminaba de sonar**

El faro de Rodas tiene una campana de niebla. El vigía la hace sonar cada 4 golpes de remo del bote guía, para que las naves sepan a qué ritmo entrar. Cada toque marca un número: 4, 8, 12, 16…

Un aprendiz recibió el encargo de anotar «todos los toques posibles» en una tablilla. Llenó las dos caras, pidió otra tablilla, llenó esa también y volvió diciendo que necesitaba más. El vigía le preguntó cuántas iba a necesitar y el aprendiz no supo qué contestar.

**Pregunta:** ¿Cuántos números marca esa campana en total?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Un número grande, pero se acaban | — |
| 　 | `b` | No se acaban nunca | — |
| 　 | `c` | Cuatro, uno por cada golpe | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo 6, dos listas muy distintas**

Abajo, las dos preguntas que se le pueden hacer a un número. Fíjate en dónde termina cada lista.

- **Caso que se acaba** — Cuatro y se acabó. Ningún número mayor que 6 puede dividirlo.
- **Caso que no se acaba** — Nunca se acaban: siempre puedes sumar 6 más y seguir.

**Resolución:** La diferencia no es de tamaño, es estructural. Un divisor de 6 no puede pasar de 6, así que la lista está encerrada. Un múltiplo de 6 puede ser tan grande como quieras: dame el más grande que se te ocurra y le sumo 6. La lista de arriba tiene techo; la de abajo no.

**Definición — Los múltiplos**

$$M(b)=\{b\times k\ :\ k\in\mathbb{Z}\}$$

Un múltiplo de b es cualquier número que se obtiene multiplicando b por un entero. Todo número es múltiplo de sí mismo (k = 1) y el 0 es múltiplo de todos (k = 0). Un número tiene finitos divisores pero infinitos múltiplos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `M(b)` | los múltiplos de b | los números marcados por la campana de b |
| `D(b)` | los divisores de b | la otra lista, la que sí se acaba |
| `k` | cuántas veces | puede ser cualquier entero, y por eso la lista no tiene techo |
| `b\in M(b)` | b es múltiplo de sí mismo | con k = 1; el primer toque de la campana |
| `0\in M(b)` | el cero es múltiplo de todos | con k = 0; b × 0 = 0 siempre |
| `b\mid a\iff a\in M(b)` | las dos caras de lo mismo | Corinto y Rodas dicen lo mismo desde lados opuestos |

### A5. Ejemplos resueltos

#### Cuántas tablillas necesita el aprendiz · *resuelto*

El aprendiz quiere anotar todos los múltiplos positivos de 4. ¿Dónde termina la lista?

- Escribo los primeros: 4 × 1 = 4, 4 × 2 = 8, 4 × 3 = 12, 4 × 4 = 16.
- Supongo que llegué al último y lo llamo N. Entonces N = 4 × k para algún k.
- Pero N + 4 = 4 × (k + 1) también es múltiplo de 4, y es mayor que N.
- Así que N no era el último. El razonamiento vale para cualquier N que elija.
- No hay último: la lista es infinita, y ninguna cantidad de tablillas alcanza.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se construye un múltiplo mayor que el supuesto último. ¿Por qué eso demuestra que no hay último?'}

#### Divisores contra múltiplos de 12 · *resuelto*

Escribe los divisores de 12 y los primeros múltiplos de 12. ¿Qué números aparecen en las dos listas?

- Divisores: busco parejas que multiplicadas den 12 → 1×12, 2×6, 3×4.
- Los ordeno: D(12) = {1, 2, 3, 4, 6, 12}. Seis en total, y se acabó.
- Múltiplos: 12, 24, 36, 48… sin final.
- El único número en las dos listas es el 12: es divisor de sí mismo y múltiplo de sí mismo.
- Los divisores van del 1 al propio número; los múltiplos van del propio número hacia arriba.

#### El aprendiz que confundió las dos listas · *TRAMPA*

El aprendiz entrega la tablilla: «Múltiplos de 10: son 1, 2, 5 y 10. Ya están todos, por eso me sobró sitio».

- Comprueba con la definición: ¿existe un entero k con 10 × k = 2?
- Tendría que ser k = 0,2, que no es entero. El 2 no es múltiplo de 10.
- Los múltiplos se construyen multiplicando: 10×1 = 10, 10×2 = 20, 10×3 = 30…

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': 'M(10)=\\{1,2,5,10\\}', 'right_latex': 'M(10)=\\{10,20,30,40,\\ldots\\}', 'rows': [{'wrong': 'Los múltiplos de 10 son los que caben en 10', 'right': 'Son aquellos en los que cabe el 10'}, {'wrong': 'La lista tiene cuatro elementos', 'right': 'La lista es infinita'}]}
**¿Por qué falla?:** Escribe los cuatro primeros múltiplos positivos de 10 y di por qué la lista no termina.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — La campana suena cada 6 golpes. ¿En qué golpe suena la séptima vez?

- dado: $6\times 7$
- hueco `P1-b1`: $6\times 7=$ → `42`

**P2** (*falta: middle*) — ¿Cuántos divisores tiene 18? Búscalos por parejas.

- dado: $1\times 18,\quad 2\times 9,\quad 3\times 6$
- hueco `P2-b1`: $\text{cantidad de divisores}=$ → `6`
- hueco `P2-b2`: $\text{el mayor de ellos}=$ → `18`

**P3** (*falta: statement_only*) — Solo el planteamiento: ¿cuál es el múltiplo de 9 más pequeño que sea mayor que 100?

- hueco `P3-b1`: $9\times k>100\ \Rightarrow\ 9\times k=$ → `108`


### A7. Comparación de métodos

**Dos caminos para contar los divisores**

¿Cuántos divisores tiene $36$? Las dos soluciones de abajo son correctas.

- **Método 1 · Probar uno por uno** — 
- **Método 2 · Buscar por parejas** — 

**Pregunta:** ¿Por qué el método 2 se puede detener en 6 y no hace falta seguir hasta 36?

**Insight:** Porque los divisores vienen en parejas que multiplicadas dan 36, y en cada pareja uno es menor o igual que √36 = 6 y el otro mayor o igual. Al pasar de 6 solo volverías a encontrar los compañeros que ya tienes. Por eso los divisores se acaban: están encerrados entre 1 y el número.

### A8. Práctica independiente (7 ítems)

**E1**

La campana suena cada 8 golpes. ¿En qué golpe suena la sexta vez?

Respuesta: `48`

Escalera de pistas:
1. Cada toque es 8 multiplicado por el número de toque.
2. 8 × 5 = 40.
3. Falta un toque más.

**E2**

¿Cuántos divisores tiene 20?

Respuesta: `6`

Escalera de pistas:
1. Búscalos por parejas que multiplicadas den 20.
2. 1×20, 2×10, 4×5.
3. Tres parejas, ninguna repetida.

**E3**

Selecciona TODOS los que son múltiplos de 7.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `n1` | 1 | — |
| ✅ | `n7` | 7 | — |
| ✅ | `n14` | 14 | — |
| ✅ | `n21` | 21 | — |
| ✅ | `n35` | 35 | — |
| 　 | `n50` | 50 | — |

Escalera de pistas:
1. Un múltiplo de 7 se obtiene multiplicando 7 por un entero.
2. El 1 es DIVISOR de 7, no múltiplo: no hay entero k con 7 × k = 1.
3. 7×5 = 35, y 7×7 = 49, así que 50 no es.

**E4**

Un aprendiz anota «Los múltiplos de 15 son 1, 3, 5 y 15». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `divisors` | Esos son los divisores: los múltiplos son 15, 30, 45… y son infinitos | — |
| 　 | `missing` | Le faltó incluir el 45 | `confunde_multiplo_con_divisor` |
| 　 | `extra` | El 15 sobra: un número no es múltiplo de sí mismo | `excluye_el_numero_de_sus_multiplos` |
| 　 | `none` | Ningún error, está bien | `confunde_multiplo_con_divisor` |

Escalera de pistas:
1. ¿Existe un entero k con 15 × k = 3?
2. Tendría que ser 0,2: no es entero.
3. Los múltiplos se obtienen multiplicando, así que van hacia arriba.

**E5**

¿Es verdadera o falsa? «Todo número tiene una cantidad finita de múltiplos.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_infinite` | Falsa: son infinitos, salvo los del 0 | — |
| 　 | `true` | Verdadera: igual que los divisores, se acaban | `los_multiplos_se_acaban` |
| 　 | `false_all` | Falsa: absolutamente todos tienen infinitos | `olvida_el_caso_del_cero` |
| 　 | `true_big` | Verdadera si el número es grande | `los_multiplos_se_acaban` |

Escalera de pistas:
1. Coge el múltiplo más grande que se te ocurra y súmale el número otra vez.
2. Siempre puedes: la lista no tiene techo.
3. ¿Y si el número fuera 0? 0 × k = 0 siempre: su único múltiplo es el 0.

**E6**

¿Cuál es el múltiplo de 12 más pequeño que supera los 100?

Respuesta: `108`

Escalera de pistas:
1. Divide 100 entre 12 para saber por dónde andas.
2. 12 × 8 = 96, todavía no pasa de 100.
3. El siguiente es 12 × 9.

**E7**

Si $b\mid a$, ¿qué se puede decir con seguridad?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a_multiple` | a es múltiplo de b | — |
| 　 | `b_multiple` | b es múltiplo de a | `invierte_la_direccion_de_la_divisibilidad` |
| 　 | `both` | Cada uno es múltiplo del otro | `confunde_multiplo_con_divisor` |
| 　 | `neither` | Nada: son cosas distintas | `no_ve_la_equivalencia` |

Escalera de pistas:
1. b | a quiere decir que existe k entero con a = b × k.
2. Esa igualdad es exactamente la definición de múltiplo.
3. a se obtiene multiplicando b, así que a es el múltiplo.


### A9. Cierre

*¿La lista se acaba o no?* — **Conjuntos que este nodo pone lado a lado**

La pregunta de la columna es siempre la misma: ¿esta lista tiene un último elemento?

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Todos los números son múltiplos de 1. Infinitos. |
|  | ✗ | Infinitos: a cualquiera le sumas 7 y sigues. |
|  | ✗ | Que empiecen grandes no los hace menos infinitos. |
|  | ✅ | La única lista de múltiplos que SÍ se acaba: 0 × k = 0 siempre. Un solo elemento. |
|  | ✅ | Seis. Encerrados entre 1 y 12: ninguno puede pasarse. |
|  | ✅ | Solo dos. Los números con exactamente dos divisores tienen nombre, y es el próximo destino. |

Los múltiplos suben sin techo; los divisores están encerrados entre 1 y el número. Y esa última fila deja la pregunta servida: ¿qué tienen de especial los números con solo dos divisores? Eso se ve en Delos.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `same_relation` | Los tres describen la misma relación mirada desde un lado o desde el otro | — |
| 　 | `infinite` | Los tres son conjuntos infinitos | — |
| 　 | `exact` | En los tres el reparto es exacto: residuo 0 | — |
| 　 | `small` | En los tres todos los elementos son menores que el número | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿En qué golpe sonó por última vez?
¿En qué golpe sonó por última vez?

Respuesta: `195`

Escalera de pistas:
1. Busca el mayor múltiplo de 15 que no supere 200.
2. 200 ÷ 15 da 13 con residuo.
3. 15 × 13 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya distingues la lista que sube de la que está encerrada.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué los múltiplos no tienen último y los divisores sí.

**PD1**

La campana suena cada 5 golpes. ¿En qué golpe suena la sexta vez?

Respuesta: `30`

**PD2**

¿Cuántos múltiplos tiene el número 9?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `infinite` | Infinitos | — |
| 　 | `three` | Tres: 1, 3 y 9 | `confunde_multiplo_con_divisor` |
| 　 | `depends` | Depende de hasta dónde cuentes | `los_multiplos_se_acaban` |

**PD3**

¿Cuántos DIVISORES tiene el número 9?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three` | Tres: 1, 3 y 9 | — |
| 　 | `infinite` | Infinitos | `sobregeneraliza_multiplos` |
| 　 | `two` | Dos: 1 y 9 | `olvida_el_divisor_del_medio` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N4-C02-MULTIPLOS-D2` | `four` | `confunde_multiplo_con_divisor` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-D2` | `depends` | `los_multiplos_se_acaban` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-D3` | `one` | `confunde_multiplo_con_divisor` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-D3` | `fourteen` | `excluye_el_numero_de_sus_multiplos` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E4` | `missing` | `confunde_multiplo_con_divisor` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E4` | `extra` | `excluye_el_numero_de_sus_multiplos` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E4` | `none` | `confunde_multiplo_con_divisor` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E5` | `true` | `los_multiplos_se_acaban` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E5` | `false_all` | `olvida_el_caso_del_cero` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E5` | `true_big` | `los_multiplos_se_acaban` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E7` | `b_multiple` | `invierte_la_direccion_de_la_divisibilidad` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E7` | `both` | `confunde_multiplo_con_divisor` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-E7` | `neither` | `no_ve_la_equivalencia` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-PD2` | `three` | `confunde_multiplo_con_divisor` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-PD2` | `depends` | `los_multiplos_se_acaban` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-PD3` | `infinite` | `sobregeneraliza_multiplos` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |
| `PREALG-N4-C02-MULTIPLOS-PD3` | `two` | `olvida_el_divisor_del_medio` | Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/04-prealg-n4-puerto/c02-multiplos-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
