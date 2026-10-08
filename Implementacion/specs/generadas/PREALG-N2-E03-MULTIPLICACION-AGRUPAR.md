# Nodo: Multiplicar no siempre agranda — PREALG-N2-E03-MULTIPLICACION-AGRUPAR

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N2-E03-MULTIPLICACION-AGRUPAR` |
| `concept_slug` | `multiplicacion` |
| Error focal | `multiplicar_siempre_agranda` |
| Sala / edificio | El Taller de Mosaicos |
| Guía | KatIA |
| Entra después de | `PREALG-N2-E00-CIUDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El Taller de Mosaicos · Multiplicación

**Título:** Multiplicar no siempre agranda

Multiplicar es agrupar: tantas veces tanto. Mientras el multiplicador fue un número de contar, el resultado siempre creció. Hoy vas a ver qué pasa cuando ese multiplicador es medio, o es negativo, y por qué la frase «multiplicar agranda» se cae.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar al taller. Sin nota.

**D1**

Un mosaico tiene 7 filas de 8 teselas. ¿Cuántas teselas lleva?

Respuesta: `56`

**D2**

¿Cuánto vale $12\times\dfrac{1}{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `six` | 6 | — |
| 　 | `twentyfour` | 24 | `multiplicar_siempre_agranda` |
| 　 | `twelve_half` | 12,5 | `confunde_multiplicar_con_sumar` |

**D3**

Si multiplicas un número por otro, ¿el resultado siempre es mayor que el primero?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `depends` | Depende de por cuánto multipliques | — |
| 　 | `always` | Sí, siempre | `multiplicar_siempre_agranda` |
| 　 | `only_positive` | Sí, mientras los dos sean positivos | `multiplicar_siempre_agranda` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Dentro del Taller de Mosaicos* — **El encargo a media escala**

El tercer edificio es el Taller de Mosaicos: mesas largas, cajones de teselas por color y una bodega al fondo de donde se saca el material. Aquí nadie cuenta tesela por tesela. El maestro dice «doce hileras de doce» y el aprendiz ya sabe cuánto pedir: multiplicar es su forma de contar sin contar.

Esta mañana llegó un encargo distinto: una copia del mosaico grande, pero a media escala. El aprendiz bajó a la bodega y pidió el doble de teselas. Dijo que era una multiplicación, y que multiplicar siempre pide más.

**Pregunta:** Si multiplicas una cantidad por un medio, ¿pides más teselas o menos?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Más: toda multiplicación agranda | — |
| 　 | `b` | Menos: media escala es la mitad | — |
| 　 | `c` | Igual: multiplicar por una fracción no cambia nada | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo 12, dos resultados opuestos**

Abajo hay dos multiplicaciones que arrancan del mismo número. Mira dónde termina cada una respecto al 12 de partida.

- **Caso que confirma lo que esperas** — 36 está por encima de 12: el multiplicador era mayor que 1.
- **Caso que rompe la expectativa** — 6 está por debajo de 12: el multiplicador era menor que 1.

**Resolución:** La operación no cambió: en las dos tomé el 12 tantas veces como decía el otro factor. Lo que decide si crece o se achica no es multiplicar, es si el multiplicador está por encima o por debajo de 1. «Tres veces» agranda; «media vez» achica.

**Definición — La multiplicación**

$$a\times b=\underbrace{a+a+\cdots+a}_{b\ \text{veces}}\quad(b\in\mathbb{N})$$

Multiplicar es agrupar: tomar la cantidad a tantas veces como diga b. Cuando b deja de ser un número de contar, «tantas veces» se convierte en «esa parte de», y ahí es donde el resultado puede achicarse.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a,b` | factores | las dos cantidades que se multiplican |
| `a\times b` | producto | el resultado de agrupar |
| `b>1` | multiplicador mayor que uno | el producto queda por encima de a |
| `0<b<1` | multiplicador entre cero y uno | el producto queda por debajo de a |
| `a\times 1=a` | multiplicar por uno deja igual | el neutro del producto; lo formaliza N3-M04 |
| `a\times 0=0` | todo por cero es cero | cero grupos no dejan nada |

### A5. Ejemplos resueltos

#### El mosaico a media escala · *resuelto*

El mosaico grande lleva 144 teselas. El encargo pide una copia a media escala en cada lado. ¿Cuántas teselas hay que pedir a la bodega?

- Media escala significa la mitad del ancho Y la mitad del alto: dos mitades, no una.
- 144 × 1/2 = 72: así queda si solo se reduce un lado.
- 72 × 1/2 = 36: ahora también el otro lado.
- 36 teselas. El aprendiz iba a pedir 288: ocho veces de más.
- Multiplicar por 1/2 achicó dos veces seguidas, aunque las dos fueran multiplicaciones.

**Autoexplicación (focal):** {'step_index': 0, 'prompt': 'En el paso 1 se aplican DOS mitades, no una. ¿Por qué la mitad de la escala no es la mitad de las teselas?'}

#### Cuando el factor apunta al otro lado · *resuelto*

Al cortar, el aprendiz rompe 3 teselas en cada hilada y el mosaico lleva 7 hiladas. ¿Cuántas teselas perdió el taller?

- Cada hilada aporta −3 teselas: la pérdida se anota con signo.
- Son 7 hiladas iguales: 7 × (−3) = (−3) + (−3) + … siete veces.
- Siete grupos de −3 dan −21.
- 7 × (−3) = −21: el producto quedó por debajo de 0, y eso son 21 teselas menos.
- El signo del producto sale de los signos de los factores; el tamaño sale de sus magnitudes.

#### El aprendiz que pidió de más · *TRAMPA*

El aprendiz anota en la bodega: «El mosaico lleva 60 teselas. Lo quieren a media escala, o sea multiplicado por 1/2. Multiplicar agranda, así que pido 120».

- Comprueba al revés: si 60 × 1/2 fuera 120, entonces 120 × 2 debería dar 60.
- 120 × 2 = 240, no 60. La igualdad no se sostiene.
- 60 × 1/2 es la mitad de 60, es decir 30. Un factor menor que 1 achica.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '60\\times\\dfrac{1}{2}=120', 'right_latex': '60\\times\\dfrac{1}{2}=30', 'rows': [{'wrong': 'Multiplicar siempre da un resultado mayor', 'right': 'Multiplicar por un número entre 0 y 1 da un resultado menor'}, {'wrong': 'Media escala pide el doble de teselas', 'right': 'Media escala pide la mitad'}]}
**¿Por qué falla?:** ¿Por qué 120 no puede ser la respuesta? Escribe la igualdad corregida.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Un friso lleva 9 paneles y cada panel 14 teselas.

- dado: $9\times 14$
- dado: $9\times 10=90,\quad 9\times 4=36$
- hueco `P1-b1`: $9\times 14=$ → `126`

**P2** (*falta: middle*) — Una cenefa de 48 teselas se rehace a un cuarto de su largo.

- dado: $48\times\dfrac{1}{4}$
- hueco `P2-b1`: $\text{¿el factor es mayor o menor que 1? escribe }0\text{ si menor}, 1\text{ si mayor}$ → `0`
- hueco `P2-b2`: $48\times\dfrac{1}{4}=$ → `12`

**P3** (*falta: statement_only*) — Solo el planteamiento: el cortador rompe 6 teselas por hilada y el mosaico lleva 8 hiladas. Anota la pérdida total con su signo.

- hueco `P3-b1`: $8\times(-6)=$ → `-48`


### A7. Comparación de métodos

**Dos caminos para el mismo producto**

¿Cuánto vale $25\times 12$? Las dos soluciones de abajo son correctas.

- **Método 1 · Descomponer un factor** — 
- **Método 2 · Reagrupar los factores** — 

**Pregunta:** ¿Cuál te sale más rápido de cabeza? ¿Y qué permiso usaste en cada uno para reordenar?

**Insight:** El método 1 reparte un factor sobre una suma (distributiva) y el método 2 reagrupa factores (asociativa). Las dos son propiedades de la multiplicación, no atajos de cálculo, y se formalizan en N3 (M02 y M03). Con la división ninguna de las dos vale — lo compruebas en el nodo siguiente.

### A8. Práctica independiente (7 ítems)

**E1**

Un mosaico tiene 13 filas de 6 teselas. ¿Cuántas teselas lleva?

Respuesta: `78`

Escalera de pistas:
1. Cada fila aporta lo mismo.
2. 10 × 6 = 60.
3. 3 × 6 = 18, y 60 + 18 = …

**E2**

Una cenefa de 36 teselas se rehace a un tercio de su largo. ¿Cuántas teselas lleva?

Respuesta: `12`

Escalera de pistas:
1. El factor es menor que 1: el resultado va a quedar por debajo de 36.
2. Un tercio de 36 es 36 dividido entre 3.
3. 3 × 12 = 36.

**E3**

El cortador rompe 4 teselas por hilada y hay 9 hiladas. ¿Cuántas teselas perdió? (con signo)

Respuesta: `-36`

Escalera de pistas:
1. Cada hilada aporta una cantidad negativa.
2. Nueve grupos de −4.
3. 9 × 4 = 36, y el signo lo pone la pérdida.

**E4**

Un escriba anota «$20\times 0{,}5=100$». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `inverted` | Multiplicó por 5 en vez de por 0,5; lo correcto es 10 | — |
| 　 | `added` | Sumó en vez de multiplicar | `confunde_multiplicar_con_sumar` |
| 　 | `decimal` | Se le olvidó la coma en el resultado: es 10,0 | `error_de_notacion_no_de_valor` |
| 　 | `none` | Ningún error, está bien | `habito_valida_sin_verificar` |

Escalera de pistas:
1. ¿0,5 está por encima o por debajo de 1?
2. Si el factor es menor que 1, el producto tiene que quedar por DEBAJO de 20.
3. 0,5 de 20 es la mitad de 20.

**E5**

¿Es verdadera o falsa? «Para cualesquiera $a>0$ y $b$: $a\times b>a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_small` | Falsa: si b está entre 0 y 1, el producto queda por debajo de a | — |
| 　 | `true` | Verdadera: multiplicar siempre agranda | `multiplicar_siempre_agranda` |
| 　 | `false_never` | Falsa: el producto nunca supera a a | `multiplicar_siempre_achica` |
| 　 | `true_if_int` | Verdadera siempre que b sea entero | `olvida_enteros_negativos_y_cero` |

Escalera de pistas:
1. Para tumbar un «siempre» basta UN caso.
2. Prueba con a = 10 y b = 0,5.
3. 10 × 0,5 = 5, y 5 no es mayor que 10.

**E6**

Un mosaico de 200 teselas se copia a la mitad de ancho y a la mitad de alto. ¿Cuántas teselas lleva la copia?

Respuesta: `50`

Escalera de pistas:
1. Reducir la escala afecta a los dos lados, no a uno.
2. 200 × 1/2 = 100.
3. Ahora vuelve a tomar la mitad de 100.

**E7**

¿Cuál de estos productos de dos irracionales SE SALE de los irracionales?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sqrt2_sqrt2` | √2 × √2 | — |
| 　 | `sqrt2_sqrt3` | √2 × √3 | `irracional_por_irracional_siempre_irracional` |
| 　 | `pi_sqrt2` | π × √2 | `irracional_por_irracional_siempre_irracional` |
| 　 | `pi_pi` | π × π | `irracional_por_irracional_siempre_irracional` |

Escalera de pistas:
1. Busca el producto que da un número que ya conoces.
2. $\sqrt{2}\times\sqrt{2}$ es el lado por el lado de un cuadrado de área 2.
3. $\sqrt{2}\times\sqrt{2}=2$, y 2 es racional.


### A9. Cierre

*La escalera de la multiplicación* — **¿El producto de dos elementos del conjunto vive en el conjunto?**

La multiplicación no rompe ningún peldaño nuevo… salvo uno.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Agrupar cantidades de contar da otra cantidad de contar. |
|  | ✅ | Con signos también cierra: el signo del producto lo deciden los factores. |
|  | ✅ | Numerador por numerador, denominador por denominador: sigue siendo fracción. |
|  | ✗ | Dos irracionales pueden dar un racional: el resultado SE SALE. Ninguna operación aritmética cierra 𝕀. |
|  | ✅ | ℝ = ℚ ∪ 𝕀 (B08) sí cierra: por eso el producto vive ahí sin problemas. |
|  | ✅ | También cierra, y aquí el producto hace algo que en ℝ es imposible. Desvío opcional (B09). |

Como la suma, la multiplicación no obligó a inventar un peldaño nuevo. Lo que sí hizo fue tumbar una creencia: agrupar puede achicar. La división, en cambio, sí va a romper un peldaño.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `grouping` | En los tres se toma una cantidad tantas veces como diga el otro factor | — |
| 　 | `bigger` | En los tres el producto es mayor que el primer factor | — |
| 　 | `below` | En los tres el segundo factor decide si el resultado sube o baja | — |
| 　 | `fractions` | En los tres aparece una fracción | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas teselas hay que pedir?
¿Cuántas teselas hay que pedir?

Respuesta: `90`

Escalera de pistas:
1. Primero el total sin reducir.
2. 15 × 24 = 360.
3. Media escala en los dos lados deja la cuarta parte.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya miras el multiplicador antes de decidir si el resultado crece.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué pasa al multiplicar por un número entre 0 y 1.

**PD1**

Un mosaico tiene 9 filas de 7 teselas. ¿Cuántas lleva?

Respuesta: `63`

**PD2**

¿Cuánto vale $30\times\dfrac{1}{3}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ten` | 10 | — |
| 　 | `ninety` | 90 | `multiplicar_siempre_agranda` |
| 　 | `thirty_third` | 30,3 | `confunde_multiplicar_con_sumar` |

**PD3**

¿Existen $a>0$ y $b>0$ tales que $a\times b<a$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí | — |
| 　 | `no` | No | `multiplicar_siempre_agranda` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-D2` | `twentyfour` | `multiplicar_siempre_agranda` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-D2` | `twelve_half` | `confunde_multiplicar_con_sumar` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-D3` | `always` | `multiplicar_siempre_agranda` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-D3` | `only_positive` | `multiplicar_siempre_agranda` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E4` | `added` | `confunde_multiplicar_con_sumar` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E4` | `decimal` | `error_de_notacion_no_de_valor` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E4` | `none` | `habito_valida_sin_verificar` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E5` | `true` | `multiplicar_siempre_agranda` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E5` | `false_never` | `multiplicar_siempre_achica` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E5` | `true_if_int` | `olvida_enteros_negativos_y_cero` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E7` | `sqrt2_sqrt3` | `irracional_por_irracional_siempre_irracional` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E7` | `pi_sqrt2` | `irracional_por_irracional_siempre_irracional` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-E7` | `pi_pi` | `irracional_por_irracional_siempre_irracional` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-PD2` | `ninety` | `multiplicar_siempre_agranda` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-PD2` | `thirty_third` | `confunde_multiplicar_con_sumar` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |
| `PREALG-N2-E03-MULTIPLICACION-AGRUPAR-PD3` | `no` | `multiplicar_siempre_agranda` | Mira si el multiplicador está por encima o por debajo de 1 antes de decidir. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/02-prealg-n2-mercado/e03-multiplicacion-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
