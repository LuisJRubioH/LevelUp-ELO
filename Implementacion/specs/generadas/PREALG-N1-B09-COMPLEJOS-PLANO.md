# Nodo: Cuando la recta se queda corta — PREALG-N1-B09-COMPLEJOS-PLANO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B09-COMPLEJOS-PLANO` |
| `concept_slug` | `complejos` |
| Error focal | `cuadrado_siempre_positivo` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B08-REALES-RECTA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Desvío opcional · Complejos

**Título:** Cuando la recta se queda corta

Este nodo es un desvío, no un peldaño: los complejos no están en la recta. Aquí vas a ver qué pasa cuando una operación perfectamente razonable no tiene respuesta en ℝ, y cómo la solución no fue subir un escalón sino salirse de la línea y usar todo el plano.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

¿Cuánto vale (−3) × (−3)?

Respuesta: `9`

**D2**

¿Existe algún número REAL que multiplicado por sí mismo dé $-1$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: los cuadrados de reales nunca son negativos | — |
| 　 | `yes_neg` | Sí: el −1, porque es negativo | `cuadrado_conserva_signo` |
| 　 | `yes_frac` | Sí, pero es una fracción muy pequeña | `todo_tiene_solucion_real` |

**D3**

Para ubicar un punto en un plano cuadriculado, ¿cuántos números necesitas?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | Dos: cuánto a lo ancho y cuánto a lo largo | — |
| 　 | `one` | Uno solo, como en la recta | `plano_como_recta` |
| 　 | `three` | Tres | `confunde_dimensiones` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · El desvío* — **La ciudad de Hipodamo**

Hipodamo de Mileto hizo algo que nadie había hecho: en vez de dejar que la ciudad creciera enredada, la trazó en cuadrícula. Para decir dónde queda una casa ya no bastaba con «la tercera de la calle»: hacían falta dos números, uno a lo ancho y otro a lo largo.

KatIA se queda pensando en eso mientras revisa una cuenta que no le sale. Está buscando un número que, multiplicado por sí mismo, dé −1. En la recta no está: los positivos al cuadrado dan positivo, los negativos al cuadrado también, y el 0 da 0. La recta entera, revisada, y nada.

**Pregunta:** Si el número que buscas no está en ninguna parte de la recta, ¿la respuesta es que no existe, o que estás buscando en el lugar equivocado?

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | No existe: la pregunta está mal hecha | — |
| 　 | `b` | Existe, pero fuera de la recta | — |
| 　 | `c` | Existe en la recta, solo que no lo hemos encontrado | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Una calle no alcanza para una ciudad**

Los dos casos de abajo son la misma pregunta hecha en dos lugares distintos. Fíjate en qué cambia cuando dejas de mirar solo la recta.

- **Caso que ya sabías** — Positivo × positivo = positivo. Negativo × negativo = positivo. 0 × 0 = 0. En la recta no hay candidato, y no es por falta de buscar.
- **Caso que rompe la expectativa** — Se define un número nuevo, i, que vive a una unidad ARRIBA del 0, fuera de la recta. Y su cuadrado sí da −1, por definición.

**Resolución:** Esta jugada ya la viste: cada vez que una operación no cabía, se amplió el conjunto. La resta no cabía en ℕ → ℤ. La división no cabía en ℤ → ℚ. La diagonal no cabía en ℚ → ℝ. Ahora la raíz de un negativo no cabe en ℝ → ℂ. La única diferencia es que esta vez no alcanzaba con estirar la recta: hubo que agregarle una dirección.

**Definición — Los números complejos**

$$\mathbb{C}=\{a+bi\ :\ a,b\in\mathbb{R}\}\quad\text{con}\quad i^2=-1$$

La frase del nodo: «imaginario» es un mal nombre histórico. i no es menos real que −3 o que √2 — los tres se inventaron para resolver algo que no cabía.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\mathbb{C}` | los complejos | todos los puntos del plano, no solo los de la recta |
| `i` | la unidad imaginaria | el número definido por i × i = −1; está una unidad arriba del 0 |
| `a+bi` | a más b i | las dos coordenadas: a a lo ancho (real), b a lo alto (imaginaria) |
| `a` | parte real | cuánto te mueves sobre la recta de siempre |
| `b` | parte imaginaria | cuánto te separas de la recta; si b = 0, el número es real |
| `\mathbb{R}\subset\mathbb{C}` | ℝ está contenido en ℂ | todo real es complejo con b = 0: la recta es una calle del plano |

### A5. Ejemplos resueltos

#### La cuenta que no salía · *resuelto*

¿Cuánto vale $\sqrt{-9}$, y por qué no está en la recta?

- Busco un número que multiplicado por sí mismo dé −9. En la recta no hay: todo cuadrado real es ≥ 0.
- Separo el signo del tamaño: −9 = 9 × (−1).
- La raíz del 9 sí la sé: 3. Y para la raíz de −1 uso el número nuevo: i.
- Junto las dos partes: √(−9) = 3i.
- Compruebo: 3i × 3i = 9 × i² = 9 × (−1) = −9. ✓

**Autoexplicación (focal):** {'step_index': 4, 'prompt': 'En el paso 5 comprobé el resultado multiplicándolo por sí mismo. ¿Por qué esa comprobación es la única que sirve aquí?'}

#### La casa en la cuadrícula · *resuelto*

En el plano de Hipodamo, ¿dónde queda el número 3 + 2i, y por qué no puede quedar sobre la recta real?

- Leo las dos coordenadas: parte real 3, parte imaginaria 2.
- Me muevo 3 a la derecha sobre la recta de siempre (el eje real).
- Desde ahí subo 2 en la dirección nueva (el eje imaginario).
- Ahí queda el punto. Está fuera de la recta porque su parte imaginaria no es 0.
- Contraste: 3 + 0i = 3 sí queda sobre la recta. Los reales son los complejos con b = 0.

#### El cuadrado que se volvió positivo · *TRAMPA*

Un discípulo hizo esta cuenta. Está mal: «i × i = √(−1) × √(−1) = √((−1)×(−1)) = √1 = 1. Entonces i² = 1, porque todo cuadrado es positivo».

- Fíjate en qué regla usó para juntar las dos raíces.
- Comprueba esa regla con dos negativos y mira si sobrevive.
- Recuerda de dónde salió i: se DEFINIÓ para que i² = −1. Si diera 1, no habría hecho falta inventarlo.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': 'i^2=1', 'right_latex': 'i^2=-1\\ \\ \\text{(por definición)}', 'rows': [{'wrong': '√a × √b = √(ab) siempre', 'right': 'Esa regla solo vale para a, b ≥ 0'}, {'wrong': 'Todo cuadrado es positivo', 'right': 'Todo cuadrado REAL es positivo; i no es real'}]}
**¿Por qué falla?:** ¿Por qué no se puede usar √a × √b = √(ab) con negativos? Escribe cuánto vale i² y por qué.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el procedimiento ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — Calcula $\sqrt{-25}$ separando el signo del tamaño.

- dado: $-25=25\times(-1)$
- dado: $\sqrt{25}=5$
- hueco `P1-b1`: $\text{Parte imaginaria de }\sqrt{-25}=$ → `5`

**P2** (*falta: middle*) — El arquitecto anota la casa $7-4i$ en el plano de la ciudad.

- dado: $a+bi\ \Rightarrow\ a=\text{parte real}$
- hueco `P2-b1`: $\text{Parte real}=$ → `7`
- hueco `P2-b2`: $\text{Parte imaginaria}=$ → `-4`

**P3** (*falta: statement_only*) — Solo el planteamiento: si i² = −1, entonces i³ = i² × i. ¿Cuánto vale i⁴? Responde con el número.

- hueco `P3-b1`: $i^4=$ → `1`


### A7. Comparación de métodos

**Dos caminos para la misma raíz**

Hay que calcular $\sqrt{-16}$. Las dos soluciones de abajo son correctas.

- **Método 1 · Separar signo y tamaño** — 
- **Método 2 · Buscar por tanteo el número que da −16** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué te dice el método 2, aunque no te dé el resultado?

**Insight:** El método 2 no fracasa por torpe: te está demostrando algo. Recorre toda la recta y prueba que ahí NO está la respuesta. Ese fracaso es la justificación de que haga falta ℂ — igual que buscar la fracción de √2 fracasaba en B07. Un método que falla bien te dice dónde no buscar.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es la parte imaginaria de $\sqrt{-36}$? (Solo el número, sin la i.)

Respuesta: `6`

Escalera de pistas:
1. Separa −36 en 36 × (−1).
2. √36 = 6 y √(−1) = i.
3. √(−36) = 6i, así que la parte imaginaria es 6.

**E2**

El arquitecto marca la casa $-2+9i$. ¿Cuál es su parte real?

Respuesta: `-2`

Escalera de pistas:
1. En a + bi, ¿cuál de los dos es la parte real?
2. La parte real es la que NO va acompañada de i.
3. Aquí es −2, y no pierde su signo.

**E3**

¿Cuál de estos números NO es real?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `imaginary` | 5i | — |
| 　 | `irrational` | √7 | `irracional_no_es_real` |
| 　 | `negative` | −12 | `negativo_no_es_real` |
| 　 | `fraction` | 8/3 | `fraccion_no_es_real` |

Escalera de pistas:
1. Tres de los cuatro los puedes ubicar en la recta.
2. √7 ≈ 2,64 está entre 2 y 3; −12 y 8/3 también tienen su punto.
3. 5i no está en la recta: su parte imaginaria no es 0.

**E4**

Un discípulo anotó: «√(−4) = −2, porque (−2) × (−2) = −4». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `product` | (−2) × (−2) = +4, no −4; la respuesta correcta es 2i | — |
| 　 | `sign` | Le faltó el signo: es +2 | `cuadrado_conserva_signo` |
| 　 | `no_root` | √(−4) no se puede calcular de ninguna forma | `irracional_no_existe` |
| 　 | `none` | Ningún error, está bien | `cuadrado_conserva_signo` |

Escalera de pistas:
1. Comprueba su cuenta: multiplica (−2) por (−2).
2. Da +4, no −4. Negativo por negativo es positivo (eso viene de B05).
3. Ningún real sirve; hay que salirse de la recta: √(−4) = 2i.

**E5**

¿Cuánto vale $i^2$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `minus_one` | −1, por definición de i | — |
| 　 | `one` | 1, porque todo cuadrado es positivo | `cuadrado_siempre_positivo` |
| 　 | `i` | i, porque i por i sigue siendo i | `confunde_producto_con_identidad` |
| 　 | `zero` | 0 | `trata_i_como_nada` |

Escalera de pistas:
1. ¿Para qué se inventó i? Vuelve a la definición.
2. Se definió justamente como el número cuyo cuadrado da −1.
3. Si i² diera 1, i sería 1 o −1 y no habría hecho falta inventar nada.

**E6**

Mira la escalera completa: ℕ → ℤ → ℚ → ℝ → ℂ. ¿Qué tienen en común TODAS las ampliaciones?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `operation` | Cada una nació de una operación que no tenía respuesta en el conjunto anterior | — |
| 　 | `bigger` | Cada una tiene números más grandes que la anterior | `conjuntos_ordenados_por_tamano` |
| 　 | `replace` | Cada una reemplaza a la anterior, que deja de servir | `conjunto_nuevo_reemplaza` |
| 　 | `harder` | Cada una es más difícil de entender que la anterior | `dificultad_como_criterio` |

Escalera de pistas:
1. Repasa qué operación falló en cada peldaño.
2. Restar en ℕ, dividir en ℤ, la diagonal en ℚ, la raíz de un negativo en ℝ.
3. Ninguno reemplaza al anterior: lo contiene. ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ.

**E7**

¿Cuál de estos complejos está SOBRE la recta real?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `real` | 6 + 0i | — |
| 　 | `pure` | 0 + 6i | `parte_imaginaria_no_separa` |
| 　 | `mixed` | 6 + 6i | `parte_imaginaria_no_separa` |
| 　 | `neg_i` | −6i | `parte_imaginaria_no_separa` |

Escalera de pistas:
1. ¿Qué condición tiene que cumplir b para no separarse de la recta?
2. La parte imaginaria debe ser 0.
3. 6 + 0i = 6, que es el punto de siempre en la recta.


### A9. Cierre

*La escalera de la necesidad* — **¿Toda raíz cuadrada vive en el conjunto?**

La misma pregunta de B08, ahora con la respuesta completa.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Ni la diagonal ni las de negativos. |
|  | ✗ | Los negativos entraron como números, no como raíces. |
|  | ✗ | La diagonal no es fracción (B07). |
|  | ✗ | Las de positivos sí; las de negativos no. |
|  | ✅ | Aquí toda raíz tiene respuesta. Y aquí se acaba la escalera. |

ℂ es el final del camino para este tipo de pregunta: cualquier ecuación polinómica que escribas tiene todas sus soluciones aquí. No hay un ℂ' esperando después. La escalera terminó.

#### Pregunta de abstracción

¿Qué estructura comparten las cinco ampliaciones de la escalera?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `no_answer` | En cada una, una operación se quedó sin respuesta | — |
| 　 | `contains` | Cada conjunto nuevo contiene enterito al anterior | — |
| 　 | `bigger_numbers` | Cada conjunto tiene números más grandes | — |
| 　 | `same_op` | Todas nacieron de la misma operación | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuál es la parte imaginaria de √(−49)?
¿Cuál es la parte imaginaria de √(−49)?

Respuesta: `7`

Escalera de pistas:
1. Separa −49 en 49 × (−1).
2. √49 = 7.
3. √(−49) = 7i: la parte imaginaria es 7.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué i² = −1 es una definición y no un cálculo.

**PD1**

¿Cuánto vale (−5) × (−5)?

Respuesta: `25`

**PD2**

¿Cuánto vale $i^2$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `minus_one` | −1 | — |
| 　 | `one` | 1 | `cuadrado_siempre_positivo` |
| 　 | `i` | i | `confunde_producto_con_identidad` |

**PD3**

¿El número $4+0i$ es real?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: su parte imaginaria es 0, así que está en la recta | — |
| 　 | `no` | No: lleva una i escrita, así que es imaginario | `parte_imaginaria_no_separa` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B09-COMPLEJOS-PLANO-D2` | `yes_neg` | `cuadrado_conserva_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-D2` | `yes_frac` | `todo_tiene_solucion_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-D3` | `one` | `plano_como_recta` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-D3` | `three` | `confunde_dimensiones` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E3` | `irrational` | `irracional_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E3` | `negative` | `negativo_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E3` | `fraction` | `fraccion_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E4` | `sign` | `cuadrado_conserva_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E4` | `no_root` | `irracional_no_existe` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E4` | `none` | `cuadrado_conserva_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E5` | `one` | `cuadrado_siempre_positivo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E5` | `i` | `confunde_producto_con_identidad` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E5` | `zero` | `trata_i_como_nada` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E6` | `bigger` | `conjuntos_ordenados_por_tamano` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E6` | `replace` | `conjunto_nuevo_reemplaza` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E6` | `harder` | `dificultad_como_criterio` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E7` | `pure` | `parte_imaginaria_no_separa` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E7` | `mixed` | `parte_imaginaria_no_separa` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-E7` | `neg_i` | `parte_imaginaria_no_separa` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-PD2` | `one` | `cuadrado_siempre_positivo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-PD2` | `i` | `confunde_producto_con_identidad` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B09-COMPLEJOS-PLANO-PD3` | `no` | `parte_imaginaria_no_separa` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b09-complejos-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
