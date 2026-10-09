# Nodo: La raíz no se reparte sobre una suma — PREALG-N2-E06-RADICACION-RAIZ

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N2-E06-RADICACION-RAIZ` |
| `concept_slug` | `radicacion` |
| Error focal | `raiz_de_suma_es_suma_de_raices` |
| Sala / edificio | La Cantera |
| Guía | KatIA |
| Entra después de | `PREALG-N2-E00-CIUDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La Cantera · Radicación

**Título:** La raíz no se reparte sobre una suma

Último edificio. Aquí no te dan el lado y te piden la superficie: te dan la superficie y tienes que deducir el lado. Vas a ver qué operación deshace a la potencia, y por qué el error más caro de la cantera es partir una raíz en dos.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de bajar a la cantera. Sin nota.

**D1**

Una losa cuadrada tiene 49 palmos² de superficie. ¿Cuánto mide su lado?

Respuesta: `7`

**D2**

¿Cuánto vale $\sqrt{9+16}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `five` | 5 | — |
| 　 | `seven` | 7 | `raiz_de_suma_es_suma_de_raices` |
| 　 | `twentyfive` | 25 | `olvida_aplicar_la_raiz` |

**D3**

¿Qué tipo de número es $\sqrt{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `irrational` | Irracional: su decimal no termina ni se repite | — |
| 　 | `rational` | Racional: es 1,41 | `decimal_truncado_es_el_numero` |
| 　 | `not_number` | No es un número: no se puede calcular exacto | `irracional_no_es_numero` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Dentro de la Cantera* — **La losa que salió torcida**

El sexto y último edificio no tiene techo: es la Cantera, un tajo de piedra con poleas, cinceles y una plomada colgando. Aquí los encargos llegan al revés que en el Taller de Mosaicos — no te dicen cuánto mide el lado, te dicen cuánta superficie quieren y tú tienes que deducir el lado.

Llegó un encargo de dos losas cuadradas, una de 9 palmos² y otra de 16, para fundirlas en una sola losa cuadrada. El cantero calculó el lado de la losa nueva sumando los lados de las dos: 3 y 4, siete palmos. Cortó la piedra. No encajó.

**Pregunta:** Si juntas una superficie de 9 y una de 16, ¿cuánto mide el lado del cuadrado que forman?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | 7 palmos: 3 más 4 | — |
| 　 | `b` | 5 palmos | — |
| 　 | `c` | 25 palmos | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos encargos de la cantera**

Los dos encargos de abajo piden un lado a partir de una superficie. Fíjate en cómo termina cada cuenta.

- **Caso que funciona** — El lado es exacto: 6 × 6 = 36. La cuenta cierra en los naturales.
- **Caso que rompe la expectativa** — El lado existe y se puede trazar con la plomada, pero ninguna fracción lo escribe.

**Resolución:** El segundo lado es tan real como el primero: es la diagonal de un cuadrado de lado 1, la puedes marcar con una cuerda. Lo que no existe es una fracción que lo mida exacto. Por eso la radicación fue la operación que obligó a inventar los irracionales (B07): la piedra cabía, el número no.

**Definición — La radicación**

$$\sqrt[n]{a}=b\iff b^{n}=a$$

La raíz deshace la potencia: buscar la raíz n-ésima de a es preguntar qué número elevado a n da a. En la cantera, la raíz cuadrada de la superficie es el lado.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a` | radicando | lo que está dentro; en la cantera, la superficie |
| `n` | índice | a qué potencia hay que elevar; si no se escribe, es 2 |
| `b` | raíz | el resultado; en la cantera, el lado |
| `\sqrt{a}=a^{1/2}` | raíz como potencia | la raíz es la potencia de exponente 1/2 (viene de E05) |
| `\sqrt{a\times b}=\sqrt{a}\times\sqrt{b}` | sí se reparte sobre el producto | esta sí vale |
| `\sqrt{a+b}\neq\sqrt{a}+\sqrt{b}` | no se reparte sobre la suma | esta NO vale, y es el error de este nodo |

### A5. Ejemplos resueltos

#### La losa que sí encaja · *resuelto*

Encargan una losa cuadrada que cubra 9 palmos² y otra que cubra 16. Al fundirlas, la losa nueva debe cubrir toda esa superficie. ¿Cuánto mide su lado?

- Primero junto las superficies: 9 + 16 = 25 palmos². Eso es lo que debe cubrir la losa nueva.
- Ahora busco el lado del cuadrado de 25 palmos²: √25.
- ¿Qué número por sí mismo da 25? 5 × 5 = 25.
- El lado es 5 palmos. Compruebo: 5 × 5 = 25, y 25 es lo que sumé.
- El cantero había cortado 7. Con 7 la losa habría cubierto 49 palmos²: casi el doble de piedra desperdiciada.

**Autoexplicación (focal):** {'step_index': 0, 'prompt': 'En el paso 1 se suma DENTRO de la raíz antes de sacarla. ¿Por qué no se puede sacar la raíz de cada número por separado?'}

#### El lado que no cabe en ninguna fracción · *resuelto*

Encargan una losa cuadrada de exactamente 2 palmos² de superficie. ¿Cuánto mide el lado y cómo se marca en la piedra?

- Busco el número que por sí mismo da 2. No es 1 (da 1) ni 2 (da 4): está en medio.
- 1,4 × 1,4 = 1,96. 1,41 × 1,41 = 1,9881. Me acerco pero nunca llego exacto.
- Ninguna fracción lo consigue: eso se demuestra en B07, y por eso √2 es irracional.
- En la piedra sí se marca: es la diagonal de un cuadrado de lado 1 palmo. Una cuerda y un cincel bastan.
- √2 = 1,41421… El lado existe; lo que no existe es su fracción exacta.

#### El cantero que partió la raíz en dos · *TRAMPA*

El cantero anota en la piedra: «Superficie total 9 + 16. El lado es √9 más √16, o sea 3 + 4 = 7 palmos». Corta la losa de 7 y no encaja.

- Comprueba al revés: una losa de lado 7 cubre 7 × 7 = 49 palmos².
- Pero solo se encargaron 9 + 16 = 25 palmos². Sobran 24: casi el doble de piedra.
- El lado correcto es √25 = 5. Con la multiplicación sí funcionaría: √(9×16) = 3 × 4 = 12.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\sqrt{9+16}=7', 'right_latex': '\\sqrt{9+16}=\\sqrt{25}=5', 'rows': [{'wrong': 'La raíz se reparte sobre cada sumando', 'right': 'Primero se suma dentro, después se saca la raíz'}, {'wrong': 'Dos cuadrados de lado 3 y 4 forman uno de lado 7', 'right': 'Forman uno de lado 5: los lados no se suman, las superficies sí'}]}
**¿Por qué falla?:** ¿Por qué 7 no puede ser el lado? Escribe la cuenta corregida.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Una losa cuadrada debe cubrir 36 + 28 palmos².

- dado: $36+28=64$
- dado: $\text{ahora sí, la raíz de la suma}$
- hueco `P1-b1`: $\sqrt{64}=$ → `8`

**P2** (*falta: middle*) — Dos losas cuadradas de 4 y 25 palmos² se cortan de un mismo bloque rectangular.

- dado: $\sqrt{4\times 25}=\sqrt{4}\times\sqrt{25}$
- hueco `P2-b1`: $\sqrt{4}=$ → `2`
- hueco `P2-b2`: $\sqrt{4\times 25}=$ → `10`

**P3** (*falta: statement_only*) — Solo el planteamiento: una losa cúbica de 27 palmos³ de volumen. ¿Cuánto mide su arista?

- hueco `P3-b1`: $\sqrt[3]{27}=$ → `3`


### A7. Comparación de métodos

**Dos caminos para la misma raíz**

¿Cuánto vale $\sqrt{144}$? Las dos soluciones de abajo son correctas.

- **Método 1 · Buscar el cuadrado** — 
- **Método 2 · Descomponer el radicando** — 

**Pregunta:** ¿Cuál usarías con √3600? ¿Y qué pasa si intentas el método 2 escribiendo 144 como 100 + 44?

**Insight:** El método 2 funciona porque 144 = 16 × 9, un PRODUCTO. Si lo escribes como 100 + 44 y repartes la raíz, obtienes 10 + 6,63… = 16,63, que no es 12. Ese fracaso es el contenido del nodo: la raíz se reparte sobre el producto y nunca sobre la suma. Descomponer en factores es lo que vas a hacer en N4-C04.

### A8. Práctica independiente (7 ítems)

**E1**

Una losa cuadrada cubre 81 palmos². ¿Cuánto mide su lado?

Respuesta: `9`

Escalera de pistas:
1. Busca el número que multiplicado por sí mismo da 81.
2. 8 × 8 = 64, se queda corto.
3. 9 × 9 = …

**E2**

Una losa debe cubrir 40 + 60 palmos². ¿Cuánto mide su lado?

Respuesta: `10`

Escalera de pistas:
1. Primero suma lo de dentro; la raíz va después.
2. 40 + 60 = 100.
3. 10 × 10 = 100.

**E3**

Un bloque cúbico tiene 64 palmos³ de volumen. ¿Cuánto mide su arista?

Respuesta: `4`

Escalera de pistas:
1. El índice 3 pide el número que elevado al cubo da 64.
2. 3³ = 27, se queda corto.
3. 4 × 4 × 4 = …

**E4**

El cantero anota «$\sqrt{16+9}=4+3=7$». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `split_sum` | Repartió la raíz sobre una suma; primero se suma dentro y da 5 | — |
| 　 | `arith` | Sumó mal: 4 + 3 son 8 | `habito_error_de_calculo_no_de_metodo` |
| 　 | `product` | Debía multiplicar las raíces: 4 × 3 = 12 | `confunde_regla_del_producto_con_la_suma` |
| 　 | `none` | Ningún error, está bien | `raiz_de_suma_es_suma_de_raices` |

Escalera de pistas:
1. Comprueba elevando al cuadrado: ¿7 × 7 da 16 + 9?
2. 7 × 7 = 49, pero 16 + 9 = 25.
3. El lado correcto es √25.

**E5**

¿Es verdadera o falsa? «Para $a,b\ge 0$: $\sqrt{a+b}=\sqrt{a}+\sqrt{b}$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_sum` | Falsa: vale sobre el producto, no sobre la suma | — |
| 　 | `true` | Verdadera: la raíz se reparte sobre cada término | `raiz_de_suma_es_suma_de_raices` |
| 　 | `false_never` | Falsa: los dos lados nunca coinciden | `olvida_el_caso_con_cero` |
| 　 | `true_squares` | Verdadera si a y b son cuadrados perfectos | `raiz_de_suma_es_suma_de_raices` |

Escalera de pistas:
1. Para tumbar un «para todo» basta UN caso.
2. Prueba con a = 9 y b = 16.
3. √25 = 5, pero 3 + 4 = 7. ¿Y si uno de los dos fuera 0?

**E6**

Se funden dos losas cuadradas, una de 45 palmos² y otra de 76, en una sola losa cuadrada. ¿Cuánto mide su lado?

Respuesta: `11`

Escalera de pistas:
1. Las superficies sí se suman; los lados no.
2. 45 + 76 = 121.
3. 11 × 11 = 121.

**E7**

¿Cuál es el primer peldaño de la escalera donde √2 ya tiene respuesta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `irrationals` | Los irracionales | — |
| 　 | `naturals` | Los naturales | `raiz_siempre_da_entero` |
| 　 | `rationals` | Los racionales | `decimal_truncado_es_el_numero` |
| 　 | `complex` | Los complejos | `no_busca_el_minimo` |

Escalera de pistas:
1. ¿Existe alguna fracción cuyo cuadrado sea exactamente 2?
2. No: eso se demostró en B07.
3. El conjunto de los números que no son fracción tiene nombre propio.


### A9. Cierre

*La escalera de la radicación* — **¿La raíz de un elemento del conjunto vive en el conjunto?**

Esta es la operación que más lejos te lleva: rompe tres peldaños seguidos.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | √4 = 2 sí es natural, pero basta un caso para romper el peldaño: √2 no lo es. |
|  | ✗ | Los negativos no ayudan: √2 sigue sin ser entero. |
|  | ✗ | Ninguna fracción tiene cuadrado 2 (B07). ESTE es el hueco del que nacieron los irracionales. |
|  | ~ (ámbar) | Aquí 𝕀 se porta mejor que de costumbre: la raíz de un irracional POSITIVO siempre es irracional. Se rompe solo con los negativos, y ahí sale de ℝ entera. |
|  | ~ (ámbar) | Cierra para todo radicando positivo. Se rompe en un solo caso: raíz par de un número negativo. |
|  | ✅ | El único peldaño donde toda raíz tiene respuesta. Por eso existe B09. |

Recorriste los seis edificios. Suma y multiplicación no rompieron nada; la resta trajo los enteros, la división trajo los racionales, la potencia y la raíz trajeron los irracionales y dejaron entreabierta la puerta de los complejos. La escalera de conjuntos no fue un capricho: la construyeron las operaciones.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `undo` | En los tres se busca el número que elevado al cuadrado da el radicando | — |
| 　 | `exact` | En los tres el resultado es un número entero | — |
| 　 | `side` | En los tres se pasa de una superficie a un lado | — |
| 　 | `split` | En los tres la raíz se puede repartir sobre cada término | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuánto mide el lado de la losa?
¿Cuánto mide el lado de la losa?

Respuesta: `13`

Escalera de pistas:
1. Las superficies se suman; los lados no.
2. 60 + 109 = 169.
3. 12 × 12 = 144, se queda corto. Prueba el siguiente.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya sumas dentro de la raíz antes de sacarla.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué la raíz se reparte sobre el producto pero no sobre la suma.

**PD1**

Una losa cuadrada cubre 100 palmos². ¿Cuánto mide su lado?

Respuesta: `10`

**PD2**

¿Cuánto vale $\sqrt{36+64}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ten` | 10 | — |
| 　 | `fourteen` | 14 | `raiz_de_suma_es_suma_de_raices` |
| 　 | `hundred` | 100 | `olvida_aplicar_la_raiz` |

**PD3**

¿Es verdadera? $\sqrt{4\times 9}=\sqrt{4}\times\sqrt{9}$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `sobregeneraliza_radicacion` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N2-E06-RADICACION-RAIZ-D2` | `seven` | `raiz_de_suma_es_suma_de_raices` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-D2` | `twentyfive` | `olvida_aplicar_la_raiz` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-D3` | `rational` | `decimal_truncado_es_el_numero` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-D3` | `not_number` | `irracional_no_es_numero` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E4` | `arith` | `habito_error_de_calculo_no_de_metodo` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E4` | `product` | `confunde_regla_del_producto_con_la_suma` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E4` | `none` | `raiz_de_suma_es_suma_de_raices` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E5` | `true` | `raiz_de_suma_es_suma_de_raices` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E5` | `false_never` | `olvida_el_caso_con_cero` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E5` | `true_squares` | `raiz_de_suma_es_suma_de_raices` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E7` | `naturals` | `raiz_siempre_da_entero` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E7` | `rationals` | `decimal_truncado_es_el_numero` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-E7` | `complex` | `no_busca_el_minimo` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-PD2` | `fourteen` | `raiz_de_suma_es_suma_de_raices` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-PD2` | `hundred` | `olvida_aplicar_la_raiz` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |
| `PREALG-N2-E06-RADICACION-RAIZ-PD3` | `false` | `sobregeneraliza_radicacion` | Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/02-prealg-n2-mercado/e06-radicacion-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
