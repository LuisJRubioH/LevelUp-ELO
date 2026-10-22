# Nodo: Dividir no siempre achica — PREALG-N2-E04-DIVISION-REPARTIR

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N2-E04-DIVISION-REPARTIR` |
| `concept_slug` | `division` |
| Error focal | `dividir_siempre_achica` |
| Sala / edificio | El Comedor Comunal |
| Guía | KatIA |
| Entra después de | `PREALG-N2-E00-CIUDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El Comedor Comunal · División

**Título:** Dividir no siempre achica

Repartir en partes iguales es lo que se hace todo el día en este edificio. Hoy vas a decidir dos cosas: qué pasa cuando el reparto no da exacto, y por qué dividir entre media hogaza da MÁS raciones, no menos.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar a la cocina. Sin nota.

**D1**

Hay 18 hogazas para 3 mesas iguales. ¿Cuántas hogazas por mesa?

Respuesta: `6`

**D2**

¿Cuánto vale $12\div\dfrac{1}{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `twentyfour` | 24 | — |
| 　 | `six` | 6 | `dividir_siempre_achica` |
| 　 | `twelve_half` | 12,5 | `confunde_dividir_con_restar` |

**D3**

5 hogazas para 2 mesas iguales. ¿Cuánto recibe cada mesa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two_half` | 2 hogazas y media | — |
| 　 | `two_left` | 2 y sobra 1 que no se reparte | `reparto_solo_entero` |
| 　 | `cannot` | No se puede: 5 no es divisible entre 2 | `reparto_solo_entero` |
| 　 | `inverted` | 2/5 de hogaza | `invierte_cociente` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Dentro del Comedor Comunal* — **La noche que faltaba comida y sobraba**

El cuarto edificio es el Comedor Comunal: un salón con mesas corridas, un caldero grande al fondo y una regla de la casa que nadie discute — todo se sirve en partes iguales, y lo que sobra también se reparte.

Esta noche llegaron más comensales de los previstos y el cocinero mandó cortar cada hogaza por la mitad. El ayudante que llevaba la cuenta se puso pálido: si ahora hay que dividir entre media hogaza, dijo, van a salir muchísimas menos raciones. Dividir siempre achica.

**Pregunta:** Al repartir 12 hogazas en raciones de media hogaza, ¿salen más raciones o menos?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Menos: dividir siempre achica | — |
| 　 | `b` | Más: cada ración es más pequeña, así que caben más | — |
| 　 | `c` | Las mismas: partirlas no cambia la cantidad de comida | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo caldero, dos repartos distintos**

Abajo hay dos divisiones que arrancan de las mismas 12 hogazas. Mira dónde termina cada una respecto al 12 de partida.

- **Caso que confirma lo que esperas** — 3 está por debajo de 12: el divisor era mayor que 1.
- **Caso que rompe la expectativa** — 24 está por encima de 12: el divisor era menor que 1.

**Resolución:** La pregunta de la segunda no es «cuánto le toca a cada uno» sino «cuántas raciones de media hogaza caben en 12 hogazas». Esa es la otra cara de la división, y con divisores menores que 1 el resultado crece. Lo que decide no es dividir: es si el divisor está por encima o por debajo de 1.

**Definición — La división**

$$a\div b=c\iff a=b\times c,\qquad b\neq 0$$

Dividir responde dos preguntas con la misma cuenta: cuánto le toca a cada uno de b grupos, o cuántos grupos de tamaño b caben en a. Si el reparto no es exacto queda un residuo, y ese residuo también se reparte. El divisor nunca puede ser cero.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a` | dividendo | lo que se reparte |
| `b` | divisor | entre cuántos, o de qué tamaño es cada parte |
| `c` | cociente | el resultado del reparto |
| `r` | residuo | lo que queda sin repartir en enteros; sigue siendo comida |
| `b\neq 0` | b distinto de cero | repartir entre cero mesas no es un reparto |
| `0<b<1` | divisor entre cero y uno | el cociente queda POR ENCIMA del dividendo |

### A5. Ejemplos resueltos

#### Cuando el reparto no da entero · *resuelto*

Quedan 27 hogazas y hay 6 mesas ocupadas. La regla de la casa dice que lo que sobra también se reparte. ¿Cuánto recibe cada mesa?

- Reparto 27 entre 6. El múltiplo de 6 más cercano sin pasarse es 6 × 4 = 24.
- Cada mesa lleva 4 hogazas enteras y sobran 27 − 24 = 3.
- Aquí es donde el comedor no se detiene: esas 3 hogazas también se reparten entre las 6 mesas.
- 3 ÷ 6 = 0,5. Cada mesa recibe media hogaza más.
- 27 ÷ 6 = 4,5. El reparto SÍ terminó; lo que no cabía era el resultado en los enteros.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 las 3 hogazas que sobran se vuelven a repartir. ¿Por qué el residuo no es el final de la cuenta?'}

#### Raciones de media hogaza · *resuelto*

El cocinero manda servir 12 hogazas en raciones de media hogaza cada una. ¿Cuántas raciones salen?

- La pregunta no es cuánto le toca a cada uno: es cuántas medias hogazas caben en 12.
- De cada hogaza salen 2 raciones, y hay 12 hogazas.
- Dividir entre una fracción es multiplicar por su inverso: 12 ÷ 1/2 = 12 × 2.
- 12 × 2 = 24 raciones.
- El divisor era menor que 1 y el resultado creció: 24 está por encima de 12.

#### El ayudante que se quedó corto · *TRAMPA*

El ayudante anota en la pizarra de la cocina: «Hay 20 hogazas y las vamos a servir en raciones de media. Dividir achica, así que salen 10 raciones. No alcanza para los 30 comensales».

- Comprueba con la definición: si 20 ÷ 1/2 fuera 10, entonces 10 × 1/2 debería dar 20.
- 10 × 1/2 = 5, no 20. La igualdad no se sostiene.
- De una sola hogaza salen 2 medias raciones. De 20 salen 40, y sí alcanza para 30 comensales.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '20\\div\\dfrac{1}{2}=10', 'right_latex': '20\\div\\dfrac{1}{2}=40', 'rows': [{'wrong': 'Dividir siempre da un resultado menor', 'right': 'Dividir entre un número entre 0 y 1 da un resultado mayor'}, {'wrong': 'De 20 hogazas salen 10 medias raciones', 'right': 'De 20 hogazas salen 40 medias raciones'}]}
**¿Por qué falla?:** ¿Por qué 10 no puede ser la respuesta? Escribe la igualdad corregida.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Quedan 32 raciones de sopa y hay 5 mesas iguales.

- dado: $32\div 5$
- dado: $5\times 6=30,\ \text{sobran }2$
- dado: $2\div 5=0{,}4$
- hueco `P1-b1`: $32\div 5=$ → `6,4`

**P2** (*falta: middle*) — El caldero tiene 9 medidas de caldo y cada cuenco lleva un cuarto de medida.

- dado: $9\div\dfrac{1}{4}=9\times 4$
- hueco `P2-b1`: $\text{¿el divisor es mayor o menor que 1? }0\text{ si menor}, 1\text{ si mayor}$ → `0`
- hueco `P2-b2`: $9\div\dfrac{1}{4}=$ → `36`

**P3** (*falta: statement_only*) — Solo el planteamiento: se reparte una deuda de 20 raciones del comedor entre 5 turnos iguales. Anota cuánto le toca a cada turno, con su signo.

- hueco `P3-b1`: $-20\div 5=$ → `-4`


### A7. Comparación de métodos

**Dos caminos para el mismo cociente**

¿Cuántas raciones de $\dfrac{3}{4}$ de hogaza salen de $\dfrac{9}{2}$ hogazas? Las dos soluciones son correctas.

- **Método 1 · Multiplicar por el inverso** — 
- **Método 2 · Pasar todo a cuartos y contar** — 

**Pregunta:** ¿Cuál te convence más de que el resultado es 6? ¿Y qué pasa con el método 2 si las raciones fueran de 1/7?

**Insight:** El método 2 solo es cómodo cuando los dos denominadores se dejan llevar a uno común pequeño; con 1/7 el conteo se vuelve impracticable y el método 1 sigue igual de barato. Y hay algo que ninguno de los dos arregla: cambiar el orden. 9/2 ÷ 3/4 y 3/4 ÷ 9/2 dan cosas distintas, porque la división no es conmutativa (N3-M01).

### A8. Práctica independiente (7 ítems)

**E1**

Hay 20 hogazas para 5 mesas iguales. ¿Cuántas hogazas por mesa?

Respuesta: `4`

Escalera de pistas:
1. Reparto en partes iguales entre las mesas.
2. ¿Cuántas veces cabe 5 en 20?
3. 5 × 4 = 20.

**E2**

Quedan 7 hogazas para 4 mesas iguales y lo que sobra también se reparte. ¿Cuánto por mesa? (decimal)

Respuesta: `1,75`

Escalera de pistas:
1. Primero las hogazas enteras: 4 × 1 = 4.
2. Sobran 3, y esas 3 también se reparten entre 4.
3. 3 ÷ 4 = 0,75.

**E3**

El caldero tiene 6 medidas de caldo y cada cuenco lleva media medida. ¿Cuántos cuencos salen?

Respuesta: `12`

Escalera de pistas:
1. La pregunta es cuántas medias medidas caben en 6.
2. De cada medida salen 2 cuencos.
3. 6 ÷ 1/2 = 6 × 2.

**E4**

El ayudante anota «22 raciones entre 4 mesas = 5, y sobran 2 que se botan». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `remainder` | El residuo también se reparte: cada mesa lleva 5,5 | — |
| 　 | `quotient` | El cociente está mal: 4 cabe 6 veces en 22 | `error_de_calculo_del_cociente` |
| 　 | `inverted` | Dividió al revés: era 4 entre 22 | `invierte_cociente` |
| 　 | `none` | Ningún error, está bien | `reparto_solo_entero` |

Escalera de pistas:
1. La regla de la casa dice que lo que sobra también se reparte.
2. Sobran 2 raciones y hay 4 mesas.
3. 2 ÷ 4 = 0,5, así que cada mesa lleva 5 + 0,5.

**E5**

¿Es verdadera o falsa? «Para cualesquiera $a>0$ y $b>0$: $a\div b<a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_small` | Falsa: si b está entre 0 y 1, el cociente queda por encima de a | — |
| 　 | `true` | Verdadera: dividir siempre achica | `dividir_siempre_achica` |
| 　 | `false_never` | Falsa: el cociente nunca baja de a | `dividir_siempre_agranda` |
| 　 | `true_if_int` | Verdadera siempre que b sea entero | `olvida_el_divisor_uno` |

Escalera de pistas:
1. Para tumbar un «siempre» basta UN caso.
2. Prueba con a = 12 y b = 0,5.
3. 12 ÷ 0,5 = 24, y 24 no es menor que 12.

**E6**

Quedan 15 hogazas y el cocinero manda servirlas en raciones de un tercio de hogaza. ¿Cuántas raciones salen?

Respuesta: `45`

Escalera de pistas:
1. ¿Cuántos tercios caben en una hogaza?
2. De cada hogaza salen 3 raciones.
3. 15 ÷ 1/3 = 15 × 3.

**E7**

¿Cuál es el conjunto más pequeño de la escalera donde toda división (con divisor distinto de 0) tiene resultado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `rationals` | Los racionales | — |
| 　 | `naturals` | Los naturales | `reparto_solo_entero` |
| 　 | `integers` | Los enteros | `reparto_solo_entero` |
| 　 | `reals` | Los reales | `no_busca_el_minimo` |

Escalera de pistas:
1. Busca el primer peldaño donde 5 ÷ 2 ya tiene respuesta.
2. En ℕ y en ℤ, 5 ÷ 2 se sale del conjunto.
3. Piden el MÁS PEQUEÑO que sirva, no cualquiera que sirva.


### A9. Cierre

*La escalera de la división* — **¿La división de dos elementos del conjunto vive en el conjunto?**

Aquí la escalera vuelve a romperse, y en un peldaño distinto al de la resta.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | El reparto no exacto no da un número de contar. |
|  | ✗ | Los negativos no ayudaron: 5 entre 2 sigue sin ser entero. La resta se arregló aquí; la división no. |
|  | ✅ | ℚ nació exactamente de esto (B06): darle respuesta a todo reparto, mientras el divisor no sea 0. |
|  | ✗ | Dos irracionales pueden dar un racional: el resultado SE SALE. Ninguna operación aritmética cierra 𝕀. |
|  | ✅ | ℝ = ℚ ∪ 𝕀 (B08) sí cierra: la división vive cómoda ahí. |
|  | ✅ | También cierra. Desvío opcional (B09). |

Dos operaciones han roto la escalera: la resta obligó a inventar ℤ y la división obligó a inventar ℚ. Las dos que faltan van a llevarte más lejos todavía.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `equal_parts` | En los tres se reparte en partes iguales | — |
| 　 | `smaller` | En los tres el resultado es menor que el dividendo | — |
| 　 | `divisor` | En los tres el divisor decide si el resultado sube o baja | — |
| 　 | `exact` | En los tres el reparto da exacto en enteros | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas raciones salen?
¿Cuántas raciones salen?

Respuesta: `12`

Escalera de pistas:
1. La pregunta es cuántos 3/4 caben en 9.
2. Dividir entre 3/4 es multiplicar por 4/3.
3. 9 × 4 = 36, y 36 ÷ 3 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya miras el divisor antes de decidir si el resultado baja.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué pasa al dividir entre un número menor que 1.

**PD1**

Hay 24 hogazas para 4 mesas iguales. ¿Cuántas por mesa?

Respuesta: `6`

**PD2**

¿Cuánto vale $10\div\dfrac{1}{5}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `fifty` | 50 | — |
| 　 | `two` | 2 | `dividir_siempre_achica` |
| 　 | `ten_fifth` | 10,2 | `confunde_dividir_con_restar` |

**PD3**

¿Existen $a>0$ y $b>0$ tales que $a\div b>a$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí | — |
| 　 | `no` | No | `dividir_siempre_achica` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N2-E04-DIVISION-REPARTIR-D2` | `six` | `dividir_siempre_achica` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-D2` | `twelve_half` | `confunde_dividir_con_restar` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-D3` | `two_left` | `reparto_solo_entero` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-D3` | `cannot` | `reparto_solo_entero` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-D3` | `inverted` | `invierte_cociente` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E4` | `quotient` | `error_de_calculo_del_cociente` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E4` | `inverted` | `invierte_cociente` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E4` | `none` | `reparto_solo_entero` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E5` | `true` | `dividir_siempre_achica` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E5` | `false_never` | `dividir_siempre_agranda` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E5` | `true_if_int` | `olvida_el_divisor_uno` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E7` | `naturals` | `reparto_solo_entero` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E7` | `integers` | `reparto_solo_entero` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-E7` | `reals` | `no_busca_el_minimo` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-PD2` | `two` | `dividir_siempre_achica` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-PD2` | `ten_fifth` | `confunde_dividir_con_restar` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E04-DIVISION-REPARTIR-PD3` | `no` | `dividir_siempre_achica` | Mira si el divisor está por encima o por debajo de 1 antes de decidir. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/02-prealg-n2-mercado/e04-division-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
