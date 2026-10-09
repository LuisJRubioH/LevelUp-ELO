# Nodo: Exactamente dos divisores, ni uno más ni uno menos — PREALG-N4-C03-PRIMOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N4-C03-PRIMOS` |
| `concept_slug` | `primos` |
| Error focal | `uno_es_primo` |
| Sala / edificio | Delos · la isla indivisible |
| Guía | KatIA |
| Entra después de | `PREALG-N4-C02-MULTIPLOS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Delos · Primos

**Título:** Exactamente dos divisores, ni uno más ni uno menos

En Rodas viste que algunos números tienen muchos divisores y otros muy pocos. Los que tienen el mínimo posible son las piezas con las que se construyen todos los demás. Vas a aprender a reconocerlos y a entender por qué el 1 se queda fuera.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de desembarcar. Sin nota.

**D1**

¿Cuántos divisores tiene el 13?

Respuesta: `2`

**D2**

¿Es 1 un número primo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No | — |
| 　 | `yes` | Sí | `uno_es_primo` |

**D3**

¿Es 2 un número primo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí | — |
| 　 | `no` | No, porque es par | `par_no_puede_ser_primo` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la aduana de Delos* — **El sello que no se podía repartir**

En la aduana de Delos, cada cargamento recibe un sello con su número de piezas. La costumbre es que el aduanero divida el cargamento en lotes iguales para inspeccionar solo uno. Con 12 piezas puede hacer lotes de 2, de 3, de 4 o de 6. Con 13 no puede hacer ningún lote: o inspecciona una pieza, o las trece.

Un aduanero nuevo llegó con una lista de «números que no se dejan repartir» y puso el 1 en primer lugar. Su maestro le tachó esa línea sin decirle por qué.

**Pregunta:** ¿Por qué el 1, que tampoco se deja repartir, no está en esa lista?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Es un error del maestro: el 1 debería estar | — |
| 　 | `b` | El 1 tiene menos divisores que los demás de la lista | — |
| 　 | `c` | El 1 es demasiado pequeño para contar | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Contar divisores en vez de opinar**

En vez de discutir si un número «se deja repartir», cuenta cuántos divisores tiene. Abajo, dos cargamentos y el caso raro.

- **Caso que se reparte** — Más de dos: hay lotes intermedios posibles. Se llama compuesto.
- **Caso que no se reparte** — Exactamente dos: solo 1 y él mismo. Se llama primo.

**Resolución:** Ahora mira el 1: sus divisores son {1}. UNO solo, porque «1 y él mismo» son la misma cosa. No tiene dos, tiene uno. Por eso no entra en la lista: no cumple la definición, que exige exactamente dos. No es un capricho — si el 1 fuera primo, romperías algo importante, y lo vas a ver en Mileto.

**Definición — Números primos y compuestos**

$$p\ \text{primo}\iff |D(p)|=2$$

Un número natural es PRIMO si tiene exactamente dos divisores: el 1 y él mismo. Es COMPUESTO si tiene más de dos. El 1 no es ninguna de las dos cosas: tiene un solo divisor.

| Símbolo | Se lee | Significa |
|---|---|---|
| `p` | un primo | un cargamento que no admite lotes intermedios |
| `|D(p)|` | cuántos divisores tiene p | el número de la lista de Rodas (C02) |
| `|D(1)|=1` | el uno tiene un solo divisor | por eso no es primo ni compuesto |
| `2` | el dos | el único primo par: todos los demás pares tienen al 2 de divisor extra |
| `\sqrt{n}` | raíz de n | el tope hasta donde hay que probar divisores (E06 y C02) |

### A5. Ejemplos resueltos

#### ¿Es primo el 97? · *resuelto*

Llega un cargamento de 97 piezas. ¿Puede el aduanero hacer lotes iguales, o le toca inspeccionar todo?

- No hace falta probar del 2 al 96: los divisores vienen en parejas (C02).
- En cada pareja uno es menor o igual que √97 ≈ 9,8, así que basta probar hasta el 9.
- Y solo con primos: 2 (97 es impar, no), 3 (9+7 = 16, no), 5 (no acaba en 0 ni 5, no), 7 (7×13 = 91, 7×14 = 98, no).
- Ningún primo hasta 9 lo divide, así que no hay ninguna pareja: solo quedan 1 y 97.
- 97 es primo. Cuatro pruebas en vez de noventa y cinco.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': 'En el paso 2 se para en √97. ¿Por qué probar más allá no puede encontrar nada nuevo?'}

#### El 51 parece primo y no lo es · *resuelto*

Un cargamento de 51 piezas. Es impar y no acaba en 0 ni en 5. ¿Es primo?

- Impar, así que el 2 queda descartado. No acaba en 0 ni 5, así que el 5 también.
- Falta el criterio del 3: sumo las cifras, 5 + 1 = 6.
- 6 es múltiplo de 3, así que 3 divide a 51.
- 51 ÷ 3 = 17, entonces D(51) = {1, 3, 17, 51}: cuatro divisores.
- 51 es compuesto. Que sea impar no lo hace primo — hay que probar TODOS los primos hasta la raíz.

#### El aduanero que puso el 1 en la lista · *TRAMPA*

El aduanero nuevo defiende su lista: «El 1 solo se puede dividir entre 1 y entre sí mismo, igual que el 13. Si el 13 es primo, el 1 también».

- Escribe el conjunto de divisores del 13: {1, 13}. Dos elementos distintos.
- Ahora el del 1: {1}. Un solo elemento, porque «él mismo» ES el 1.
- La definición pide exactamente dos, así que el 1 no cumple. No es primo, y tampoco compuesto.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '|D(1)|=2\\ \\Rightarrow\\ 1\\ \\text{primo}', 'right_latex': '|D(1)|=1\\ \\Rightarrow\\ 1\\ \\text{ni primo ni compuesto}', 'rows': [{'wrong': 'El 1 tiene dos divisores, como todo primo', 'right': 'El 1 tiene UNO: el 1 y «él mismo» coinciden'}, {'wrong': 'Primo = «no se puede repartir»', 'right': 'Primo = «tiene exactamente dos divisores»'}]}
**¿Por qué falla?:** Escribe D(1) sin repetir elementos y di cuántos tiene.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — ¿Cuántos divisores tiene el 29?

- dado: $\sqrt{29}\approx 5{,}4$
- dado: $2\nmid 29,\ 3\nmid 29,\ 5\nmid 29$
- hueco `P1-b1`: $|D(29)|=$ → `2`

**P2** (*falta: middle*) — ¿Es primo el 91? Prueba los primos hasta su raíz.

- dado: $\sqrt{91}\approx 9{,}5;\quad 2\nmid,\ 3\nmid,\ 5\nmid$
- hueco `P2-b1`: $91\div 7=$ → `13`
- hueco `P2-b2`: $|D(91)|=$ → `4`

**P3** (*falta: statement_only*) — Solo el planteamiento: ¿cuántos primos hay entre 1 y 20? Cuéntalos.

- hueco `P3-b1`: $\text{cantidad de primos hasta }20=$ → `8`


### A7. Comparación de métodos

**Dos caminos para encontrar los primos hasta 30**

Las dos soluciones de abajo dan la misma lista.

- **Método 1 · Probar cada número** — 
- **Método 2 · Criba de Eratóstenes** — 

**Pregunta:** ¿Por qué en el método 2 basta con tachar los múltiplos de 2, 3 y 5, y no hace falta seguir con 7?

**Insight:** Porque los múltiplos de 7 menores que 30 que aún no estuvieran tachados tendrían que ser 7 × algo ≥ 7, es decir al menos 49, que ya se pasa de 30. La regla general: basta cribar con los primos hasta √30 ≈ 5,5. Es la misma idea de las parejas de divisores que usaste en Rodas.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuántos divisores tiene el 23?

Respuesta: `2`

Escalera de pistas:
1. Prueba los primos hasta √23 ≈ 4,8.
2. El 2 y el 3 no lo dividen.
3. Solo quedan el 1 y el propio 23.

**E2**

¿Cuántos divisores tiene el 49?

Respuesta: `3`

Escalera de pistas:
1. Prueba los primos hasta √49 = 7.
2. 7 × 7 = 49, así que el 7 lo divide.
3. Los divisores son 1, 7 y 49: la pareja del 7 es él mismo.

**E3**

Selecciona TODOS los que son primos.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `n1` | 1 | — |
| ✅ | `n2` | 2 | — |
| 　 | `n9` | 9 | — |
| ✅ | `n17` | 17 | — |
| 　 | `n51` | 51 | — |
| ✅ | `n97` | 97 | — |

Escalera de pistas:
1. Cuenta los divisores de cada uno: primo es exactamente dos.
2. El 1 tiene uno solo. El 9 tiene tres (1, 3, 9).
3. El 51 engaña por impar: 5+1 = 6, así que el 3 lo divide.

**E4**

Un aduanero anota «2 no es primo porque es par». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two_divisors` | Ser par no importa: 2 tiene exactamente dos divisores, 1 y 2 | — |
| 　 | `one_divisor` | 2 tiene un solo divisor | `confunde_dos_con_uno` |
| 　 | `three` | 2 tiene tres divisores: 1, 2 y él mismo | `cuenta_el_numero_dos_veces` |
| 　 | `none` | Ningún error, está bien | `par_no_puede_ser_primo` |

Escalera de pistas:
1. La definición no dice nada sobre pares o impares: cuenta divisores.
2. Escribe D(2).
3. D(2) = {1, 2}: dos elementos distintos.

**E5**

¿Es verdadera o falsa? «Todos los números primos son impares.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_two` | Falsa: el 2 es primo y es par | — |
| 　 | `true` | Verdadera: un par siempre se puede dividir entre 2 | `par_no_puede_ser_primo` |
| 　 | `false_many` | Falsa: hay muchos primos pares | `cree_que_hay_varios_primos_pares` |
| 　 | `true_after_two` | Verdadera a partir del 3 | `reformula_en_vez_de_refutar` |

Escalera de pistas:
1. Para tumbar un «todos» basta UN caso.
2. Busca un primo par.
3. D(2) = {1, 2}: dos divisores, y 2 es par.

**E6**

¿Cuál es el primo más pequeño que supera a 30?

Respuesta: `31`

Escalera de pistas:
1. Empieza en 31 y sube.
2. Para 31 prueba los primos hasta √31 ≈ 5,6.
3. Ni 2, ni 3, ni 5 lo dividen.

**E7**

¿Hasta qué número hay que probar divisores para decidir si 143 es primo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sqrt` | Hasta 11, porque 11 × 11 = 121 y 12 × 12 pasa de 143 | — |
| 　 | `half` | Hasta 71, la mitad de 143 | `no_usa_la_raiz_como_tope` |
| 　 | `all` | Hasta 142 | `no_usa_la_raiz_como_tope` |
| 　 | `ten` | Hasta 10, siempre basta con eso | `generaliza_un_tope_fijo` |

Escalera de pistas:
1. Los divisores vienen en parejas que multiplicadas dan 143.
2. En cada pareja uno es menor o igual que la raíz.
3. √143 está entre 11 y 12. (Y de hecho 143 = 11 × 13.)


### A9. Cierre

*Contar divisores decide la categoría* — **¿Tiene exactamente dos divisores?**

Sin opiniones: se cuenta la lista de divisores y la respuesta cae sola.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | UN divisor. Ni primo ni compuesto: la única excepción de toda la clasificación. |
|  | ✅ | Dos divisores: primo. Y el único primo par que existe. |
|  | ✗ | Tres divisores: compuesto. Impar, pero no primo. |
|  | ✅ | Dos divisores: primo. Basta probar hasta √17 ≈ 4,1. |
|  | ✗ | Cuatro divisores: compuesto. Engaña porque es impar y no acaba en 5. |
|  | ✅ | Dos divisores: primo. Cuatro pruebas bastan (2, 3, 5, 7). |

Dos divisores y ni uno más. El 1 se queda fuera por tener uno, no por ser pequeño, y en Mileto vas a ver qué se rompería si lo dejáramos entrar.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `count` | En los tres la decisión sale de CONTAR divisores | — |
| 　 | `odd` | En los tres el número es impar y por eso es primo | — |
| 　 | `sqrt` | En los tres basta probar divisores hasta la raíz | — |
| 　 | `prime` | Los tres son primos | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos divisores tiene 113?
¿Cuántos divisores tiene 113?

Respuesta: `2`

Escalera de pistas:
1. Prueba solo los primos hasta la raíz de 113.
2. √113 está entre 10 y 11: bastan 2, 3, 5 y 7.
3. Ninguno lo divide, así que solo quedan 1 y 113.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya decides contando divisores, no por el aspecto del número.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el 1 tiene un solo divisor.

**PD1**

¿Cuántos divisores tiene el 19?

Respuesta: `2`

**PD2**

¿Es 1 un número primo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No | — |
| 　 | `yes` | Sí | `uno_es_primo` |

**PD3**

¿Es 15 un número primo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: 3 y 5 también lo dividen | — |
| 　 | `yes` | Sí: es impar | `impar_implica_primo` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N4-C03-PRIMOS-D2` | `yes` | `uno_es_primo` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-D3` | `no` | `par_no_puede_ser_primo` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E4` | `one_divisor` | `confunde_dos_con_uno` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E4` | `three` | `cuenta_el_numero_dos_veces` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E4` | `none` | `par_no_puede_ser_primo` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E5` | `true` | `par_no_puede_ser_primo` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E5` | `false_many` | `cree_que_hay_varios_primos_pares` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E5` | `true_after_two` | `reformula_en_vez_de_refutar` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E7` | `half` | `no_usa_la_raiz_como_tope` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E7` | `all` | `no_usa_la_raiz_como_tope` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-E7` | `ten` | `generaliza_un_tope_fijo` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-PD2` | `yes` | `uno_es_primo` | Escribe la lista de divisores y cuéntala antes de decidir. |
| `PREALG-N4-C03-PRIMOS-PD3` | `yes` | `impar_implica_primo` | Escribe la lista de divisores y cuéntala antes de decidir. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/04-prealg-n4-puerto/c03-primos-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
