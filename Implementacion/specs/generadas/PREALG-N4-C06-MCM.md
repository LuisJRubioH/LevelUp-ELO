# Nodo: El producto solo acierta cuando no comparten nada — PREALG-N4-C06-MCM

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N4-C06-MCM` |
| `concept_slug` | `mcm` |
| Error focal | `mcm_es_el_producto_de_los_numeros` |
| Sala / edificio | Esparta · donde coinciden las rutas |
| Guía | KatIA |
| Entra después de | `PREALG-N4-C05-MCD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Esparta · Mínimo común múltiplo

**Título:** El producto solo acierta cuando no comparten nada

En Atenas buscabas lo más grande que cabía en los dos. Aquí buscas lo más pequeño donde caben los dos. Multiplicar siempre da UNA respuesta válida — pero casi nunca la más pequeña, y ese «casi» tiene una regla exacta.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes del último muelle. Sin nota.

**D1**

¿Cuál es el número más pequeño que es múltiplo de 3 y de 5 a la vez?

Respuesta: `15`

**D2**

¿Cuánto vale el MCM de $4$ y $6$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `twelve` | 12 | — |
| 　 | `twentyfour` | 24 | `mcm_es_el_producto_de_los_numeros` |
| 　 | `two` | 2 | `confunde_mcm_con_mcd` |

**D3**

¿El MCM de dos números puede ser menor que uno de ellos?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: tiene que ser múltiplo de los dos | — |
| 　 | `yes` | Sí, si son muy distintos | `confunde_mcm_con_mcd` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el muelle de Esparta* — **Las dos naves que nunca coincidían**

Del muelle de Esparta salen dos naves de aprovisionamiento. Una zarpa cada 4 días y la otra cada 6. El día que las dos coinciden en puerto se aprovecha para hacer el inventario grande, y el capitán quiere saber cada cuánto pasa.

El escribiente hizo la cuenta rápida: «cada 4 y cada 6, pues cada 24 días». El capitán programó el inventario para el día 24. Las dos naves ya habían coincidido el día 12, con todo el mundo trabajando en otra cosa.

**Pregunta:** ¿Cada cuántos días coinciden de verdad las dos naves?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Cada 24 días: 4 × 6 | — |
| 　 | `b` | Antes de los 24 | — |
| 　 | `c` | Cada 2 días | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Las dos listas de salidas, una debajo de la otra**

Los días en que zarpa cada nave. Busca el primer día que aparece en las dos listas.

- **Las salidas de cada nave** — Las dos listas son infinitas (C02), pero se cruzan.
- **Los días en que coinciden** — Coinciden cada 12 días, no cada 24. El 24 también vale, pero llega tarde.

**Resolución:** 24 no era una respuesta falsa: las naves SÍ coinciden el día 24. Era una respuesta tardía. El producto siempre da un múltiplo común, porque contiene todas las piezas de los dos — pero repite las que comparten. 4 y 6 comparten un 2, y multiplicar lo cuenta dos veces.

**Definición — El mínimo común múltiplo**

$$\text{MCM}(a,b)=\min\big(M(a)\cap M(b)\setminus\{0\}\big)$$

El MCM de dos números es el menor múltiplo positivo que tienen en común. Siempre existe (el producto siempre sirve) y nunca es menor que el mayor de los dos. Solo coincide con el producto cuando los números son coprimos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\text{MCM}(a,b)` | mínimo común múltiplo | el primer día en que las dos naves coinciden |
| `\min` | el mínimo | el PRIMERO de los comunes; el producto suele ser uno posterior |
| `\text{MCM}(a,b)\ge\max(a,b)` | no baja del mayor | tiene que ser múltiplo de los dos |
| `\text{MCM}\times\text{MCD}=a\times b` | la relación con Atenas | lo que sobra del producto es exactamente el MCD |
| `\text{MCD}=1\Rightarrow\text{MCM}=a\times b` | solo si son coprimos | ahí el producto sí es la respuesta mínima |

### A5. Ejemplos resueltos

#### El MCM desde la factorización · *resuelto*

Una nave zarpa cada 12 días y otra cada 18. ¿Cada cuántos días coinciden?

- Descompongo: 12 = 2² × 3 y 18 = 2 × 3².
- El resultado tiene que ser múltiplo de los dos, así que necesita TODAS las piezas de cada uno.
- Del 2: uno pide dos y el otro pide uno. Con dos me sobra para los dos → 2².
- Del 3: uno pide uno y el otro pide dos → 3².
- MCM = 2² × 3² = 36. Se cogen todos los primos con el exponente MAYOR. (El producto habría dado 216, seis veces más tarde.)

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se coge el exponente mayor, y en el MCD de Atenas se cogía el menor. ¿Por qué al revés?'}

#### Dos naves coprimas · *resuelto*

Ahora una nave zarpa cada 5 días y otra cada 7. ¿Cada cuántos coinciden?

- 5 y 7 son primos distintos: no comparten ninguna pieza.
- El MCM necesita todas las piezas de los dos: un 5 y un 7.
- MCM = 5 × 7 = 35. Aquí el producto SÍ es la respuesta mínima.
- Compruebo con la fórmula: MCM × MCD = a × b. Como MCD = 1, MCM = 35.
- La regla: el producto acierta exactamente cuando los números son coprimos (C05).

#### El escribiente que multiplicó sin mirar · *TRAMPA*

El escribiente defiende su cuenta: «Una cada 4 días y otra cada 6. 4 × 6 = 24, así que el inventario va el día 24. El 24 es múltiplo de los dos, así que está bien».

- Escribe los múltiplos: 4, 8, 12… y 6, 12… El 12 aparece antes que el 24.
- Desde las piezas: 4 = 2² y 6 = 2 × 3. El producto usa 2³ × 3, pero con 2² basta.
- Ese 2 de más es exactamente el MCD(4,6) = 2. Por eso MCM × MCD = producto.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\text{MCM}(4,6)=24', 'right_latex': '\\text{MCM}(4,6)=12', 'rows': [{'wrong': 'El producto es el MCM', 'right': 'El producto es UN múltiplo común, no siempre el menor'}, {'wrong': '4 y 6 no comparten nada', 'right': 'Comparten un 2, y multiplicar lo cuenta dos veces'}]}
**¿Por qué falla?:** ¿Por qué 24 no es la respuesta? Da el valor correcto y di qué pieza se contó de más.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Halla el MCM de 6 y 8 con las factorizaciones.

- dado: $6=2\times 3,\quad 8=2^{3}$
- dado: $\text{todos los primos con exponente mayor: }2^{3}\times 3$
- hueco `P1-b1`: $\text{MCM}(6,8)=$ → `24`

**P2** (*falta: middle*) — Halla el MCM de 10 y 15 usando que MCM × MCD = producto.

- dado: $10\times 15=150,\quad \text{MCD}(10,15)=5$
- hueco `P2-b1`: $150\div 5=$ → `30`
- hueco `P2-b2`: $30\div 10=$ → `3`

**P3** (*falta: statement_only*) — Solo el planteamiento: dos naves zarpan cada 9 y cada 4 días. ¿Cada cuántos coinciden?

- hueco `P3-b1`: $\text{MCM}(9,4)=$ → `36`


### A7. Comparación de métodos

**Dos caminos para la misma coincidencia**

¿Cuánto vale $\text{MCM}(24,36)$? Las dos soluciones de abajo son correctas.

- **Método 1 · Por factorización** — 
- **Método 2 · Con el MCD** — 

**Pregunta:** ¿Por qué dividir entre el MCD arregla el producto?

**Insight:** Porque el producto cuenta dos veces todo lo que los dos números comparten, y lo que comparten es exactamente el MCD. Dividir entre él quita esa repetición. De ahí la identidad MCM(a,b) × MCD(a,b) = a × b, que vale siempre: cada pieza del producto acaba o en el MCD o en el MCM.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es el MCM de 3 y 4?

Respuesta: `12`

Escalera de pistas:
1. ¿Comparten algún primo?
2. 3 y 4 son coprimos: no comparten nada.
3. Cuando son coprimos, el MCM es el producto.

**E2**

¿Cuál es el MCM de 6 y 9?

Respuesta: `18`

Escalera de pistas:
1. 6 = 2 × 3 y 9 = 3², así que comparten un 3.
2. Coge todos los primos con el exponente mayor: 2 × 3².
3. 2 × 9 = …  (el producto 54 llegaría tarde)

**E3**

¿Cuál es el MCM de 5 y 20?

Respuesta: `20`

Escalera de pistas:
1. Comprueba primero si el pequeño divide al grande.
2. 20 ÷ 5 = 4, exacto.
3. Si a divide a b, el MCM es b.

**E4**

Un escribiente anota «MCM(8, 12) = 96, porque 8 × 12 = 96». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `not_minimum` | 96 es común pero no mínimo: comparten un 4, y el MCM es 24 | — |
| 　 | `arith` | Se equivocó: 8 × 12 no da 96 | `habito_error_de_calculo_no_de_metodo` |
| 　 | `not_multiple` | 96 no es múltiplo de 8 | `no_verifica_la_condicion_de_comun` |
| 　 | `none` | Ningún error, está bien | `mcm_es_el_producto_de_los_numeros` |

Escalera de pistas:
1. 96 sí es múltiplo de los dos. La pregunta es si es el MENOR.
2. Escribe los múltiplos de 12: 12, 24… ¿alguno es múltiplo de 8?
3. 24 = 8 × 3 y 24 = 12 × 2. Llega mucho antes que 96.

**E5**

¿Es verdadera o falsa? «El MCM de dos números es siempre su producto.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_coprime` | Falsa: solo cuando son coprimos, como 5 y 7 | — |
| 　 | `true` | Verdadera: multiplicando siempre sale el menor común | `mcm_es_el_producto_de_los_numeros` |
| 　 | `false_never` | Falsa: nunca puede ser el producto | `olvida_el_caso_coprimo` |
| 　 | `true_primes` | Verdadera solo si los dos son primos | `confunde_primo_con_coprimo` |

Escalera de pistas:
1. Para tumbar un «siempre» basta UN caso.
2. Prueba con 4 y 6: el producto es 24 pero coinciden en 12.
3. ¿Y hay casos donde SÍ acierta? Prueba con 5 y 7.

**E6**

Selecciona TODOS los pares donde el MCM SÍ es el producto de los dos números.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `p1` | 3 y 8 | — |
| 　 | `p2` | 4 y 10 | — |
| ✅ | `p3` | 9 y 10 | — |
| 　 | `p4` | 6 y 15 | — |

Escalera de pistas:
1. El producto acierta exactamente cuando el MCD es 1.
2. 3 y 8 no comparten primos; 9 y 10 tampoco (3² y 2×5).
3. 4 y 10 comparten un 2; 6 y 15 comparten un 3.

**E7**

Una nave zarpa cada 15 días y otra cada 20. Hoy coincidieron en puerto. ¿Dentro de cuántos días vuelven a coincidir?

Respuesta: `60`

Escalera de pistas:
1. 15 = 3 × 5 y 20 = 2² × 5.
2. Todos los primos con el exponente mayor: 2² × 3 × 5.
3. 4 × 3 × 5 = …  (el producto 300 llegaría cinco veces más tarde)


### A9. Cierre

*¿El producto acierta?* — **¿Es el MCM igual a a × b?**

La respuesta depende de una sola cosa: si los dos números comparten piezas.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | El producto llega el doble de tarde. Ese doble es el MCD. |
|  | ✅ | No comparten nada, así que no hay nada repetido que quitar. |
|  | ✗ | El MCM es directamente el mayor. Compruébalo siempre primero. |
|  | ✅ | Dos primos distintos siempre son coprimos: el producto acierta. |
|  | ✗ | Comparten todo. El producto a² se pasa muchísimo. |
|  | ✅ | El producto acierta, aunque por una razón boba: multiplicar por 1 no cambia nada (N3-M04). |

El producto acierta cuando el MCD es 1 y falla en todo lo demás — y falla exactamente por un factor MCD. Esa es la última pieza del puerto: MCM × MCD = a × b.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `common_multiple` | En los tres se busca un número donde quepan los DOS | — |
| 　 | `floor` | En los tres el resultado no puede bajar del número mayor | — |
| 　 | `product` | En los tres el resultado es el producto de los dos | — |
| 　 | `smaller` | En los tres el resultado es menor que los dos números | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Dentro de cuántos días coinciden?
¿Dentro de cuántos días coinciden?

Respuesta: `56`

Escalera de pistas:
1. Descompón los dos números.
2. 8 = 2³ y 14 = 2 × 7.
3. Todos los primos con el exponente mayor: 2³ × 7 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya compruebas si comparten piezas antes de multiplicar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el producto casi siempre llega tarde.

**PD1**

¿Cuál es el número más pequeño que es múltiplo de 2 y de 7 a la vez?

Respuesta: `14`

**PD2**

¿Cuánto vale el MCM de $6$ y $10$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `thirty` | 30 | — |
| 　 | `sixty` | 60 | `mcm_es_el_producto_de_los_numeros` |
| 　 | `two` | 2 | `confunde_mcm_con_mcd` |

**PD3**

¿Cuánto vale el MCM de $4$ y $9$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `thirtysix` | 36: son coprimos, así que sí es el producto | — |
| 　 | `twelve` | 12 | `sobregeneraliza_mcm` |
| 　 | `one` | 1 | `confunde_mcm_con_mcd` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N4-C06-MCM-D2` | `twentyfour` | `mcm_es_el_producto_de_los_numeros` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-D2` | `two` | `confunde_mcm_con_mcd` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-D3` | `yes` | `confunde_mcm_con_mcd` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-E4` | `arith` | `habito_error_de_calculo_no_de_metodo` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-E4` | `not_multiple` | `no_verifica_la_condicion_de_comun` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-E4` | `none` | `mcm_es_el_producto_de_los_numeros` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-E5` | `true` | `mcm_es_el_producto_de_los_numeros` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-E5` | `false_never` | `olvida_el_caso_coprimo` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-E5` | `true_primes` | `confunde_primo_con_coprimo` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-PD2` | `sixty` | `mcm_es_el_producto_de_los_numeros` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-PD2` | `two` | `confunde_mcm_con_mcd` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-PD3` | `twelve` | `sobregeneraliza_mcm` | Comprueba si los dos números comparten algún primo antes de multiplicar. |
| `PREALG-N4-C06-MCM-PD3` | `one` | `confunde_mcm_con_mcd` | Comprueba si los dos números comparten algún primo antes de multiplicar. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/04-prealg-n4-puerto/c06-mcm-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
