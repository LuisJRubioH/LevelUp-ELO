# Nodo: Hay que llegar hasta el final, y el final es único — PREALG-N4-C04-FACTORIZACION-PRIMA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N4-C04-FACTORIZACION-PRIMA` |
| `concept_slug` | `factorizacion_prima` |
| Error focal | `deja_factores_compuestos` |
| Sala / edificio | Mileto · piezas fundamentales |
| Guía | KatIA |
| Entra después de | `PREALG-N4-C03-PRIMOS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Mileto · Factorización prima

**Título:** Hay que llegar hasta el final, y el final es único

En Delos aprendiste a reconocer las piezas mínimas. Aquí las usas: todo número se desmonta en primos, y por muchos caminos distintos que tomes siempre llegas a las mismas piezas. Vas a ver por qué eso es un teorema y no una casualidad.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar al almacén. Sin nota.

**D1**

¿Cuánto vale $2\times 2\times 3$?

Respuesta: `12`

**D2**

¿Cuál de estas descomposiciones de $36$ está TERMINADA?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `primes` | 2 × 2 × 3 × 3 | — |
| 　 | `four_nine` | 4 × 9 | `deja_factores_compuestos` |
| 　 | `six_six` | 6 × 6 | `deja_factores_compuestos` |

**D3**

Si dos personas descomponen el mismo número en primos por caminos distintos, ¿obtienen lo mismo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `same` | Sí: siempre las mismas piezas | — |
| 　 | `different` | No: depende del camino | `la_factorizacion_no_es_unica` |
| 　 | `sometimes` | A veces sí y a veces no | `la_factorizacion_no_es_unica` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el almacén de Mileto* — **Los dos aprendices y el mismo fardo**

En el almacén de Mileto la lana llega en fardos que hay que deshacer hasta madejas sueltas para pesarlas. Un fardo grande se abre en fardos medianos, esos en pequeños, y así hasta que ya no se puede abrir nada más.

El maestro le dio a dos aprendices dos fardos idénticos de 60 madejas. El primero empezó separando por mitades; el segundo, apartando primero los lotes de tres. Terminaron con las manos llenas de madejas y discutiendo, porque cada uno juraba haber hecho un trabajo distinto del otro.

**Pregunta:** Si dos caminos distintos desmontan el mismo fardo, ¿acaban con las mismas piezas?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | No: cada camino da piezas distintas | — |
| 　 | `b` | Sí: siempre las mismas, aunque en otro orden | — |
| 　 | `c` | Depende de por dónde se empiece | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos caminos para desmontar el mismo 60**

Abajo, los dos aprendices. Compara las piezas del final, no el orden en que aparecieron.

- **Camino del primer aprendiz** — 60 → 2×30 → 2×2×15 → 2×2×3×5.
- **Camino del segundo aprendiz** — 60 → 3×20 → 3×4×5 → 3×2×2×5. Las mismas piezas.

**Resolución:** Dos caminos, dos madejas de 2, una de 3 y una de 5 en los dos casos. No se parecen: son idénticas. Ordenadas de menor a mayor, las dos listas coinciden carácter por carácter. Y eso no pasa solo con el 60: pasa con todos los números, siempre. Tiene nombre de teorema.

**Definición — El teorema fundamental de la aritmética**

$$n=p_1^{a_1}\times p_2^{a_2}\times\cdots\times p_k^{a_k}$$

Todo número natural mayor que 1 se escribe como producto de primos, y esa escritura es ÚNICA salvo el orden de los factores. Descomponer no es una técnica entre varias: es encontrar la identidad del número.

| Símbolo | Se lee | Significa |
|---|---|---|
| `p_i` | los primos que aparecen | las madejas mínimas: ya no se abren más |
| `a_i` | cuántas veces aparece cada uno | el exponente; se escribe como potencia (E05) |
| `\text{única}` | salvo el orden | 2×2×3 y 3×2×2 son la MISMA factorización |
| `n>1` | mayor que uno | el 1 queda fuera: no aporta piezas |
| `60=2^{2}\times 3\times 5` | forma con potencias | la escritura compacta de la misma lista |

### A5. Ejemplos resueltos

#### El fardo de 180 madejas · *resuelto*

Descompón 180 en primos y escríbelo con potencias.

- Divido por el primo más pequeño que pueda: 180 ÷ 2 = 90.
- Sigo con el 2: 90 ÷ 2 = 45. Ya no es par, así que el 2 se agotó.
- Paso al 3: 45 ÷ 3 = 15, y 15 ÷ 3 = 5.
- El 5 es primo: he llegado al final. Piezas: 2, 2, 3, 3, 5.
- 180 = 2² × 3² × 5. Compruebo: 4 × 9 × 5 = 180.

**Autoexplicación (focal):** {'step_index': 3, 'prompt': 'En el paso 4 se declara terminado el trabajo. ¿Cómo sabes que no se puede seguir desmontando?'}

#### Contar divisores sin buscarlos · *resuelto*

El maestro pregunta cuántos divisores tiene 180 sin escribir la lista. ¿Se puede saber desde la factorización?

- Cualquier divisor de 180 se arma con las mismas piezas, cogiendo algunas.
- Del 2 puedo coger 0, 1 o 2 madejas: 3 opciones. Del 3 igual: 3 opciones.
- Del 5 puedo coger 0 o 1: 2 opciones.
- Cada combinación da un divisor distinto: 3 × 3 × 2 = 18 divisores.
- La regla: se suma 1 a cada exponente y se multiplican. (2+1)(2+1)(1+1) = 18.

#### El aprendiz que dejó fardos sin abrir · *TRAMPA*

Un aprendiz entrega el trabajo: «Fardo de 36 desmontado: 4 × 9. Ya está, porque 4 × 9 = 36».

- Comprueba cada factor: ¿4 es primo? D(4) = {1,2,4}, tres divisores → compuesto.
- ¿9 es primo? D(9) = {1,3,9}, tres divisores → compuesto. Los dos se abren.
- 4 = 2×2 y 9 = 3×3, así que 36 = 2×2×3×3 = 2² × 3².

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '36=4\\times 9', 'right_latex': '36=2\\times 2\\times 3\\times 3=2^{2}\\times 3^{2}', 'rows': [{'wrong': 'Basta con que el producto dé el número', 'right': 'Además, TODOS los factores tienen que ser primos'}, {'wrong': '4 × 9 y 6 × 6 son descomposiciones distintas de 36', 'right': 'Las dos llevan a la misma: 2×2×3×3'}]}
**¿Por qué falla?:** Termina de desmontar 4 × 9 y escribe la factorización con potencias.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Descompón 84 en primos.

- dado: $84\div 2=42$
- dado: $42\div 2=21$
- dado: $21=3\times 7$
- hueco `P1-b1`: $\text{cantidad de factores primos (con repetición)}=$ → `4`

**P2** (*falta: middle*) — Descompón 200 en primos y cuenta sus divisores.

- dado: $200=2^{3}\times 5^{2}$
- hueco `P2-b1`: $(3+1)\times(2+1)=$ → `12`
- hueco `P2-b2`: $2^{3}\times 5^{2}=$ → `200`

**P3** (*falta: statement_only*) — Solo el planteamiento: ¿cuántos divisores tiene 72? Descompónlo primero.

- hueco `P3-b1`: $\text{divisores de }72=$ → `12`


### A7. Comparación de métodos

**Dos caminos para descomponer 90**

Las dos soluciones de abajo llegan a la misma lista de piezas.

- **Método 1 · Divisiones sucesivas** — 
- **Método 2 · Árbol de factores** — 

**Pregunta:** ¿Qué pasaría si en el método 2 empezaras por 90 = 6 × 15 en vez de 9 × 10?

**Insight:** Llegarías exactamente a 2 × 3 × 3 × 5. Ese es el contenido del teorema: el árbol puede tener cualquier forma, pero las hojas siempre son las mismas. Por eso el maestro no tuvo que decidir cuál aprendiz tenía razón — los dos hicieron el mismo trabajo.

### A8. Práctica independiente (7 ítems)

**E1**

Descompón $28$ en primos. ¿Cuántos factores primos tiene contando repeticiones?

Respuesta: `3`

Escalera de pistas:
1. Empieza dividiendo por el primo más pequeño que quepa.
2. 28 ÷ 2 = 14 y 14 ÷ 2 = 7.
3. Las piezas son 2, 2 y 7.

**E2**

Si $n=2^{3}\times 5$, ¿cuánto vale $n$?

Respuesta: `40`

Escalera de pistas:
1. Calcula la potencia primero.
2. 2³ = 8.
3. 8 × 5 = …

**E3**

¿Cuántos divisores tiene $n=2^{2}\times 3$?

Respuesta: `6`

Escalera de pistas:
1. Suma 1 a cada exponente y multiplica.
2. (2+1) × (1+1).
3. 3 × 2 = …  (comprueba: n = 12 y D(12) tiene 6 elementos)

**E4**

Selecciona TODAS las descomposiciones de 48 que estén SIN TERMINAR.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | 2 × 2 × 2 × 2 × 3 | — |
| ✅ | `b` | 16 × 3 | — |
| ✅ | `c` | 2 × 24 | — |
| 　 | `d` | 3 × 2 × 2 × 2 × 2 | — |

Escalera de pistas:
1. Revisa factor por factor: si alguno es compuesto, está sin terminar.
2. 16 y 24 son compuestos: todavía se abren.
3. El orden no importa: 2×2×2×2×3 y 3×2×2×2×2 son la misma, y las dos están terminadas.

**E5**

¿Es verdadera o falsa? «$36=6\times 6$ es la factorización prima de 36.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_composite` | Falsa: 6 es compuesto; hay que seguir hasta 2² × 3² | — |
| 　 | `true` | Verdadera: el producto da 36 | `deja_factores_compuestos` |
| 　 | `false_other` | Falsa: la factorización correcta es 4 × 9 | `deja_factores_compuestos` |
| 　 | `false_unique` | Falsa: 36 tiene varias factorizaciones primas distintas | `la_factorizacion_no_es_unica` |

Escalera de pistas:
1. Comprueba si cada factor es primo.
2. D(6) = {1,2,3,6}: cuatro divisores, así que 6 es compuesto.
3. Sigue abriendo: 6 = 2 × 3, dos veces.

**E6**

¿Cuántos divisores tiene 100? Descompónlo primero.

Respuesta: `9`

Escalera de pistas:
1. 100 = 2² × 5².
2. Suma 1 a cada exponente: (2+1) y (2+1).
3. 3 × 3 = …

**E7**

Si el 1 se considerara primo, ¿qué se rompería?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `uniqueness` | La unicidad: 6 sería 2×3, 1×2×3, 1×1×2×3… infinitas escrituras | — |
| 　 | `nothing` | Nada: el 1 no cambia el producto | `uno_es_primo` |
| 　 | `product` | Los productos darían resultados distintos | `confunde_valor_con_escritura` |
| 　 | `count` | Habría menos primos | `no_entiende_la_consecuencia` |

Escalera de pistas:
1. El teorema dice que la factorización es ÚNICA salvo el orden.
2. Prueba a escribir 6 metiendo unos delante.
3. 2×3, 1×2×3, 1×1×2×3… todas darían 6, y ya no habría una sola.


### A9. Cierre

*¿El trabajo está terminado?* — **¿Todos los factores son primos?**

La única pregunta que hay que hacerle a una descomposición antes de entregarla.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | 2 y 3 son primos: terminada. |
|  | ✗ | Los dos factores son compuestos: quedan fardos sin abrir. |
|  | ✗ | Uno primo y otro compuesto. Basta que UNO se pueda abrir para que no esté terminada. |
|  | ✅ | Terminada. Y es la única, venga de 4×9, de 6×6 o de 2×18. |
|  | ✗ | Un solo factor compuesto tampoco vale: no se ha desmontado nada. |
|  | ✗ | El 1 sobra: no es primo (C03) y además rompería la unicidad. |

Terminada quiere decir que ningún factor se abre más. Y el premio es fuerte: esas piezas son las mismas para todo el mundo, siempre. En Atenas vas a usarlas para comparar DOS números a la vez.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `until_prime` | En los tres hay que seguir abriendo hasta que solo queden primos | — |
| 　 | `same_pieces` | En los tres el camino elegido no cambia las piezas finales | — |
| 　 | `two_factors` | En los tres el número se parte en exactamente dos factores | — |
| 　 | `even` | En los tres el número es par | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos divisores tiene 360?
¿Cuántos divisores tiene 360?

Respuesta: `24`

Escalera de pistas:
1. Descompón primero: empieza dividiendo entre 2 todas las veces que puedas.
2. 360 = 2³ × 3² × 5.
3. (3+1) × (2+1) × (1+1) = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya revisas que ningún factor se pueda seguir abriendo.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo cómo saber que una descomposición está terminada.

**PD1**

¿Cuánto vale $2\times 3\times 5$?

Respuesta: `30`

**PD2**

¿Cuál de estas descomposiciones de $24$ está TERMINADA?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `primes` | 2 × 2 × 2 × 3 | — |
| 　 | `four_six` | 4 × 6 | `deja_factores_compuestos` |
| 　 | `eight_three` | 8 × 3 | `deja_factores_compuestos` |

**PD3**

¿Son la MISMA factorización $2\times 3\times 3$ y $3\times 2\times 3$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: el orden no cuenta | — |
| 　 | `no` | No: están escritas distinto | `confunde_orden_con_identidad` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N4-C04-FACTORIZACION-PRIMA-D2` | `four_nine` | `deja_factores_compuestos` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-D2` | `six_six` | `deja_factores_compuestos` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-D3` | `different` | `la_factorizacion_no_es_unica` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-D3` | `sometimes` | `la_factorizacion_no_es_unica` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-E5` | `true` | `deja_factores_compuestos` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-E5` | `false_other` | `deja_factores_compuestos` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-E5` | `false_unique` | `la_factorizacion_no_es_unica` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-E7` | `nothing` | `uno_es_primo` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-E7` | `product` | `confunde_valor_con_escritura` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-E7` | `count` | `no_entiende_la_consecuencia` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-PD2` | `four_six` | `deja_factores_compuestos` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-PD2` | `eight_three` | `deja_factores_compuestos` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |
| `PREALG-N4-C04-FACTORIZACION-PRIMA-PD3` | `no` | `confunde_orden_con_identidad` | Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/04-prealg-n4-puerto/c04-factorizacion-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
