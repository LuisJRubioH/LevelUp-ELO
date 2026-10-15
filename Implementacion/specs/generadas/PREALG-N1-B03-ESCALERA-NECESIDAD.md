# Nodo: Cada peldaño amplía; ninguno borra al anterior — PREALG-N1-B03-ESCALERA-NECESIDAD

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B03-ESCALERA-NECESIDAD` |
| `concept_slug` | `escalera` |
| Error focal | `conjuntos_se_reemplazan` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B02-PREGUNTA-DETONADORA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Antes de subir · El mapa del camino

**Título:** Cada peldaño amplía; ninguno borra al anterior

Vas a recorrer cinco conjuntos de números. Antes de subir el primero conviene entender cómo está armada la escalera, porque la forma en que la mayoría se la imagina está equivocada y esa idea equivocada estorba durante todo el camino.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

Cuando aparecen los números negativos, ¿qué pasa con los naturales?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `stay` | Siguen existiendo: el conjunto nuevo los incluye | — |
| 　 | `replaced` | Se reemplazan: ahora se usan los negativos | `conjuntos_se_reemplazan` |
| 　 | `separate` | Quedan aparte: son dos mundos que no se tocan | `conjuntos_son_disjuntos` |

**D2**

¿Por qué crees que se inventaron números nuevos a lo largo de la historia?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `need` | Porque había cuentas sin respuesta | — |
| 　 | `bigger` | Porque hacían falta números más grandes | `amplia_es_agrandar` |
| 　 | `harder` | Para hacer las matemáticas más difíciles | `matematica_arbitraria` |

**D3**

El número $5$, ¿en cuántos de estos conjuntos está? $\mathbb{N}$, $\mathbb{Z}$, $\mathbb{Q}$, $\mathbb{R}$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `four` | En los cuatro | — |
| 　 | `one` | Solo en ℕ: es un natural | `pertenencia_unica` |
| 　 | `two` | En ℕ y ℤ nada más | `pertenencia_unica` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Antes de subir* — **El taller del carpintero**

El carpintero del ágora empezó con un cincel. Con el cincel podía hacer casi todo, hasta que le encargaron una junta que el cincel no lograba. Entonces consiguió una gubia.

Después vino un encargo que la gubia tampoco resolvía, y consiguió un berbiquí. Y así, herramienta tras herramienta, hasta llenar la pared del taller. Hoy tiene once herramientas colgadas.

**Pregunta:** Cuando el carpintero consiguió la gubia, ¿qué hizo con el cincel? Piensa la respuesta, porque con los números pasa exactamente lo mismo.

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Lo botó: ya tenía una herramienta mejor | — |
| 　 | `b` | Lo dejó colgado: sigue sirviendo para lo suyo | — |
| 　 | `c` | Lo guardó por si acaso, pero ya no lo usa | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos cuentas que obligaron a construir un peldaño**

Ningún conjunto nuevo apareció porque a alguien se le ocurrió. Cada uno apareció porque había una cuenta concreta sin respuesta. Mira las dos que abrieron los dos primeros peldaños.

- **La cuenta que abrió ℤ** — Contando no hay respuesta. Aparece el lado izquierdo del 0 — y los naturales no se van: quedan adentro del conjunto nuevo.
- **La cuenta que abrió ℚ** — Con enteros no hay respuesta: cae entre 0 y 1. Aparecen las fracciones — y los enteros tampoco se van.

**Resolución:** El patrón es siempre el mismo: una operación se sale del conjunto, y el conjunto siguiente se construye para que quepa. Nunca se borra lo anterior. Por eso la escalera se dibuja como cajas una dentro de otra, no como escalones separados.

**Definición — La cadena de inclusión**

$$\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}$$

La frase del nodo: cada conjunto CONTIENE al anterior. Subir un peldaño es ganar números, nunca perderlos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\subset` | está contenido en | todo lo del primero está también en el segundo |
| `\mathbb{N}\subset\mathbb{Z}` | ℕ dentro de ℤ | todo natural es también entero; 5 no dejó de ser natural |
| `\in` | pertenece a | relaciona UN número con UN conjunto |
| `\notin` | no pertenece a | el número se sale de ese conjunto: ahí nace el siguiente |
| `\mathbb{R}\setminus\mathbb{Q}` | los irracionales | el único que NO contiene a los anteriores: rellena, no envuelve |
| `\cup` | unión | ℝ = ℚ ∪ 𝕀: los reales son las fracciones más lo que las fracciones no alcanzan |

### A5. Ejemplos resueltos

#### Dónde vive el 7 · *resuelto*

¿A cuáles de los conjuntos ℕ, ℤ, ℚ y ℝ pertenece el número 7?

- ¿Sirve para contar cantidades completas? Sí → 7 ∈ ℕ.
- ¿Está en la recta de los enteros? Sí, a la derecha del 0 → 7 ∈ ℤ.
- ¿Se puede escribir como fracción de enteros? Sí: 7/1 → 7 ∈ ℚ.
- ¿Está en la recta completa? Sí → 7 ∈ ℝ.
- 7 pertenece a los cuatro. No cambió de conjunto: cada conjunto nuevo lo recibió.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 escribí 7 como 7/1 para probar que es racional. ¿Por qué ese truco funciona con CUALQUIER entero?'}

#### Dónde vive −3/4 · *resuelto*

¿A cuáles de los conjuntos ℕ, ℤ, ℚ y ℝ pertenece el número −3/4?

- ¿Cuenta cantidades completas? No: es negativo y además es una parte → −3/4 ∉ ℕ.
- ¿Es entero? No: cae entre −1 y 0 → −3/4 ∉ ℤ.
- ¿Es fracción de enteros? Sí: −3 sobre 4 → −3/4 ∈ ℚ.
- ¿Está en la recta completa? Sí → −3/4 ∈ ℝ.
- Entra recién en el tercer peldaño. Los conjuntos de abajo se le quedaron cortos, no al revés.

#### El número al que le quitaron su casa · *TRAMPA*

Un discípulo resumió el nodo así. Está mal: «Cuando llegamos a los racionales, el 5 dejó de ser natural y pasó a ser racional. Un número está en el peldaño al que llegó, no en los de abajo».

- Vuelve a la definición: ℕ ⊂ ℤ significa que TODO natural está en ℤ.
- Contener no es reemplazar: la caja grande no vacía a la pequeña.
- Comprueba con el carpintero: ¿la gubia hizo desaparecer el cincel?

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '5\\in\\mathbb{Q}\\ \\Rightarrow\\ 5\\notin\\mathbb{N}', 'right_latex': '5\\in\\mathbb{N}\\ \\Rightarrow\\ 5\\in\\mathbb{Z},\\ \\mathbb{Q},\\ \\mathbb{R}', 'rows': [{'wrong': 'Un número vive en un solo conjunto', 'right': 'Un número vive en todos los que lo contienen'}, {'wrong': 'Subir de peldaño es mudarse', 'right': 'Subir de peldaño es que lleguen vecinos nuevos'}]}
**¿Por qué falla?:** ¿Por qué 5 sigue siendo natural aunque también sea racional? Escribe a qué conjuntos pertenece.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el análisis ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — ¿En cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ está el número 12?

- dado: $12\ \text{cuenta objetos completos}\Rightarrow 12\in\mathbb{N}$
- dado: $\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}$
- hueco `P1-b1`: $\text{Número de conjuntos}=$ → `4`

**P2** (*falta: middle*) — ¿En cuántos de los cuatro está el número −6? ¿Y el número 1/2?

- dado: $-6\ \text{es negativo}\Rightarrow -6\notin\mathbb{N}$
- hueco `P2-b1`: $\text{Conjuntos que contienen a }-6=$ → `3`
- hueco `P2-b2`: $\text{Conjuntos que contienen a }\tfrac{1}{2}=$ → `2`

**P3** (*falta: statement_only*) — Solo el planteamiento: √2 no es fracción de enteros. ¿En cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ está?

- hueco `P3-b1`: $\text{Número de conjuntos}=$ → `1`


### A7. Comparación de métodos

**Dos formas de dibujar la escalera**

Las dos imágenes de abajo representan lo mismo. Una se presta a confusión y la otra no.

- **Dibujo 1 · Escalones** — 
- **Dibujo 2 · Cajas anidadas** — 

**Pregunta:** ¿Cuál conviene para explicar POR QUÉ nacieron los negativos? ¿Y cuál para explicar que 5 sigue siendo natural?

**Insight:** Ninguno de los dos alcanza solo, y ahí está el contenido: el de escalones cuenta la historia pero sugiere que uno reemplaza al otro; el de cajas cuenta la estructura pero esconde la necesidad. La escalera de arriba usa los dos a la vez a propósito. Y ojo: los irracionales no encajan en ninguno de los dos limpiamente — no contienen a nadie, rellenan huecos.

### A8. Práctica independiente (7 ítems)

**E1**

¿A cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ pertenece el número 0?

Respuesta: `4`

Escalera de pistas:
1. En este curso, ¿el 0 es natural?
2. Sí lo es. Y si está en ℕ, la cadena de inclusión hace el resto.
3. ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ: si está en el primero, está en los cuatro.

**E2**

¿A cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ pertenece el número −8?

Respuesta: `3`

Escalera de pistas:
1. ¿Se puede contar −8 objetos?
2. No: los naturales no llegan por debajo del 0.
3. Entra desde ℤ, y de ahí para arriba: ℤ, ℚ y ℝ.

**E3**

¿Cuál de estas afirmaciones sobre la escalera es correcta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | Todo entero es racional, pero no todo racional es entero | — |
| 　 | `reverse` | Todo racional es entero, pero no todo entero es racional | `error_del_reciproco` |
| 　 | `both` | Todo entero es racional y todo racional es entero | `conjuntos_son_iguales` |
| 　 | `neither` | Los enteros y los racionales no se tocan | `conjuntos_son_disjuntos` |

Escalera de pistas:
1. Piensa en 1/2: ¿es racional? ¿es entero?
2. Es racional pero no entero, así que ℚ tiene números que ℤ no tiene.
3. Y todo entero se escribe n/1, así que ℤ está dentro de ℚ.

**E4**

Un discípulo dibujó la escalera así: «ℕ, después ℤ, después ℚ, después 𝕀, después ℝ; cada uno dentro del siguiente». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `irrationals` | 𝕀 no contiene a ℚ: los irracionales no envuelven a nadie, rellenan | — |
| 　 | `order` | El orden está mal: ℤ va antes que ℕ | `invierte_la_escalera` |
| 　 | `reals` | ℝ no debería ir al final | `reales_no_son_el_final` |
| 　 | `none` | Ningún error, está bien | `irracionales_contienen_racionales` |

Escalera de pistas:
1. ¿1/2 es irracional?
2. No lo es, así que ℚ no puede estar dentro de 𝕀.
3. 𝕀 y ℚ no se tocan; ℝ es la unión de los dos.

**E5**

¿Es verdadera o falsa? «Como $4$ es real, entonces ya no es natural.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_both` | Falsa: 4 es natural Y real al mismo tiempo | — |
| 　 | `true_moved` | Verdadera: subió de peldaño | `conjuntos_se_reemplazan` |
| 　 | `false_notreal` | Falsa: 4 no es real, solo natural | `pertenencia_unica` |
| 　 | `depends` | Depende de en qué peldaño estemos trabajando | `pertenencia_depende_del_contexto` |

Escalera de pistas:
1. Lee otra vez qué significa ℕ ⊂ ℝ.
2. Significa que todo natural es también real.
3. Estar en la caja grande no te saca de la pequeña: 4 es las dos cosas.

**E6**

Un maestro de otra escuela dice: «yo no enseño enteros; con los naturales me alcanza para todo». ¿Qué encargo NO va a poder resolver con su clase?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `debt` | Anotar cuánto queda debiendo un puesto del mercado | — |
| 　 | `count` | Contar cuántas columnas tiene el pórtico | `cree_naturales_insuficientes` |
| 　 | `add` | Sumar las mercancías de dos puestos | `cree_naturales_insuficientes` |
| 　 | `compare` | Decir cuál de dos puestos tiene más | `cree_naturales_insuficientes` |

Escalera de pistas:
1. Tres de los cuatro encargos se resuelven contando.
2. Busca el que obliga a bajar por debajo del 0.
3. Deber es el hueco que abrió el segundo peldaño.

**E7**

¿Qué operación fue la que obligó a construir el peldaño de los racionales?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `division` | La división: 3 ÷ 4 no cabía en los enteros | — |
| 　 | `subtraction` | La resta: 3 − 5 no cabía en los naturales | `confunde_peldanos` |
| 　 | `root` | La raíz: √2 no cabía en las fracciones | `confunde_peldanos` |
| 　 | `sum` | La suma: se salía del conjunto | `suma_no_es_cerrada` |

Escalera de pistas:
1. Cada peldaño lleva el nombre de la operación que lo rompió.
2. La resta abrió ℤ. ¿Cuál abrió ℚ?
3. Repartir 3 entre 4 cae entre 0 y 1: eso es dividir.


### A9. Cierre

*El mapa completo* — **Qué gana cada peldaño y qué NO pierde**

Léelo de abajo hacia arriba: cada fila agrega, ninguna quita.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Contar. Se rompe con la resta. |
|  | ✅ | Agrega el lado izquierdo. Se rompe con la división. |
|  | ✅ | Agrega las partes. Se rompe con la diagonal del cuadrado. |
|  | ✗ | El raro: no contiene a nadie. Rellena huecos. |
|  | ✅ | La recta completa, sin un solo hueco. |

Fíjate en la única fila marcada distinto: 𝕀. Todos los demás peldaños CONTIENEN al anterior; los irracionales no contienen a ninguno. Por eso los reales no son «el quinto conjunto», son la unión de dos.

#### Pregunta de abstracción

¿Qué patrón se repite en el nacimiento de cada peldaño?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `operation` | Una operación se salió del conjunto y hubo que ampliarlo | — |
| 　 | `keeps` | El conjunto nuevo conserva todo lo del anterior | — |
| 　 | `bigger_numbers` | Cada peldaño usa números más grandes | — |
| 　 | `replace` | Cada peldaño reemplaza al anterior | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos de los cinco pertenecen a ℤ?
¿Cuántos de los cinco pertenecen a ℤ?

Respuesta: `3`

Escalera de pistas:
1. Un entero es un número sin parte decimal, positivo, negativo o cero.
2. El 0 cuenta; 0,25 no.
3. √5 no es entero ni racional: queda fuera.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros casos. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué un número puede estar en varios conjuntos a la vez.

**PD1**

Cuando aparecen las fracciones, ¿qué pasa con los enteros?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `stay` | Siguen dentro: ℤ ⊂ ℚ | — |
| 　 | `replaced` | Se reemplazan por fracciones | `conjuntos_se_reemplazan` |

**PD2**

¿A cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ pertenece el número 100?

Respuesta: `4`

**PD3**

¿Qué operación abrió el peldaño de los enteros?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sub` | La resta | — |
| 　 | `div` | La división | `confunde_peldanos` |
| 　 | `root` | La raíz cuadrada | `confunde_peldanos` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B03-ESCALERA-NECESIDAD-D1` | `replaced` | `conjuntos_se_reemplazan` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-D1` | `separate` | `conjuntos_son_disjuntos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-D2` | `bigger` | `amplia_es_agrandar` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-D2` | `harder` | `matematica_arbitraria` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-D3` | `one` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-D3` | `two` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E3` | `reverse` | `error_del_reciproco` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E3` | `both` | `conjuntos_son_iguales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E3` | `neither` | `conjuntos_son_disjuntos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E4` | `order` | `invierte_la_escalera` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E4` | `reals` | `reales_no_son_el_final` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E4` | `none` | `irracionales_contienen_racionales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E5` | `true_moved` | `conjuntos_se_reemplazan` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E5` | `false_notreal` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E5` | `depends` | `pertenencia_depende_del_contexto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E6` | `count` | `cree_naturales_insuficientes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E6` | `add` | `cree_naturales_insuficientes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E6` | `compare` | `cree_naturales_insuficientes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E7` | `subtraction` | `confunde_peldanos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E7` | `root` | `confunde_peldanos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-E7` | `sum` | `suma_no_es_cerrada` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-PD1` | `replaced` | `conjuntos_se_reemplazan` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-PD3` | `div` | `confunde_peldanos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B03-ESCALERA-NECESIDAD-PD3` | `root` | `confunde_peldanos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b03-escalera-necesidad-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
