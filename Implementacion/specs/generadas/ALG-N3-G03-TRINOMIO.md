# Nodo: Acertar el producto no basta: también hay que acertar la suma — ALG-N3-G03-TRINOMIO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N3-G03-TRINOMIO` |
| `concept_slug` | `trinomio_general` |
| Error focal | `pares_sin_verificar` |
| Sala / edificio | La mesa de despiece |
| Guía | Salim |
| Entra después de | `ALG-N3-G02-CUADRADOS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La mesa de despiece · Trinomio general

**Título:** Acertar el producto no basta: también hay que acertar la suma

En el cotejo de huellas bastaba reconocer una marca. Aquí llegan fardos de tres bultos que no traen ninguna: hay que despiezarlos a mano, buscando dos listones que encajen. Y encajar significa cumplir dos medidas a la vez, no una.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de sentarte al banco. Sin nota.

**D1**

¿Qué dos números suman 5 y multiplican 6? Escribe el mayor.

Respuesta: `3`

**D2**

¿A qué equivale $(x+2)(x+3)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $x^{2}+5x+6$ | — |
| 　 | `noMid` | $x^{2}+6$ | `termino_comun_falta_suma` |
| 　 | `swap` | $x^{2}+6x+5$ | `intercambia_suma_y_producto` |

**D3**

¿Cuánto es (−4) × (−5)?

Respuesta: `20`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la mesa de despiece* — **Los dos listones que no encajaban**

En el fondo del almacén hay un banco largo con muescas. Los fardos de tres bultos que no traen marca se despiezan aquí: se buscan dos listones cuyo largo y cuya suma encajen en las muescas del banco.

Salim señala un despiece a medio hacer:

«El fardo pedía dos listones que multiplicaran 6 y sumaran 5. El mozo probó 1 y 6: multiplican 6, perfecto. Los cortó y los llevó al banco.»

«Uno y seis suman siete, no cinco. Los listones no entraron en la muesca, y ya estaban cortados.»

**Pregunta:** Si 1 y 6 multiplican exactamente lo que pedía el fardo, ¿por qué no sirven?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `dos` | Porque hay dos condiciones y solo cumplen una | — |
| 　 | `orden` | Porque están en el orden equivocado | — |
| 　 | `signo` | Porque les falta un signo menos | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El producto propone, la suma dispone**

Un trinomio $x^{2}+bx+c$ viene de la bandeja de parejas: $(x+p)(x+q)$. Al estampar, $p$ y $q$ dejaban su suma en el medio y su producto al final. Aquí se lee al revés.

- **La lista de candidatos** — El producto es el que da la lista, porque los divisores de un número son pocos. Por eso se empieza por ahí.
- **La suma decide** — El producto reduce a dos o tres candidatas; la suma elige una. Saltarse el segundo paso es cortar los listones a ciegas.

**Resolución:** Para $x^{2}+bx+c$: se listan las parejas de enteros que multiplican $c$ y se queda la que suma $b$. Si el coeficiente de $x^{2}$ es mayor que 1, primero se multiplica ese coeficiente por el término independiente y se busca la pareja para ese producto nuevo.

**Definición — Trinomio general**

$$x^{2}+bx+c = (x+p)(x+q)\ \text{ con } p+q=b\ \text{ y } pq=c$$

Factorizar un trinomio con coeficiente principal 1 es buscar dos números que cumplan DOS condiciones: que sumen el coeficiente del medio y que multipliquen el término independiente. Los signos salen solos de esas dos cuentas.

Si el coeficiente principal es mayor que 1, se busca la pareja para el producto $a\cdot c$, se parte el término del medio con esos dos números y se agrupa.

| Símbolo | Se lee | Significa |
|---|---|---|
| `p+q=b` | p más q igual a b | la condición de la suma — la que se olvida |
| `pq=c` | p por q igual a c | la condición del producto — la que da la lista de candidatos |
| `x^{2}-9x+20=(x-4)(x-5)` | equis cuadrado menos nueve equis más veinte | medio negativo y final positivo: los dos números son negativos |
| `x^{2}+x-6=(x+3)(x-2)` | equis cuadrado más equis menos seis | final negativo: los dos números tienen signos distintos |
| `a\cdot c` | a por c | cuando el coeficiente principal no es 1, la lista sale de este producto |

### A5. Ejemplos resueltos

#### Listar y después elegir · *resuelto*

Salim despieza un fardo marcado $x^{2}+4x+3$.

- Busco dos números que multipliquen 3: solo hay 1 · 3 (y −1 · −3).
- ¿Cuál de esas suma 4? 1 + 3 = 4 ✓.
- Los dos son positivos, así que los dos paréntesis suman.
- Queda (x + 1)(x + 3).
- Compruebo estampando: x² + 3x + x + 3 = x² + 4x + 3 ✓.

**Autoexplicación (focal):** {'step_index': 0, 'prompt': '¿Por qué conviene empezar por el producto y no por la suma, si las dos condiciones hacen falta?'}

#### Los signos salen de las dos cuentas · *resuelto*

Otro fardo: $x^{2}-9x+20$. El medio resta y el final suma.

- Producto 20, positivo: los dos números tienen el MISMO signo.
- Suma −9, negativa: entonces los dos son negativos.
- Parejas negativas que multiplican 20: (−1)(−20), (−2)(−10), (−4)(−5).
- ¿Cuál suma −9? −4 − 5 = −9 ✓.
- Queda (x − 4)(x − 5).

#### El mozo que cortó los listones antes de sumar · *TRAMPA*

Vuelve el fardo de la apertura, ahora escrito: $x^{2}+5x+6$. El mozo anota:

- (x + 1)(x + 6) = x² + 7x + 6.
- El primero y el último coinciden; el del medio no: 7x en vez de 5x.
- Por eso la condición de la suma no es opcional: es la que fija el término del medio.
- Regla para no volver a caer: lista con el producto, ELIGE con la suma.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '(x+1)(x+6)=x^{2}+7x+6', 'right_latex': '(x+2)(x+3)=x^{2}+5x+6', 'rows': [{'wrong': 'Basta con que multipliquen el último término', 'right': 'Tienen que multiplicar el último Y sumar el del medio'}, {'wrong': '1 y 6 multiplican 6, así que sirven', 'right': '2 y 3 multiplican 6 y además suman 5'}]}
**¿Por qué falla?:** Estampa la anotación del mozo y di en qué término se separa del fardo original.


### A6. Puente — parcialmente resueltos

El despiece va empezado; completa los huecos.

**P1** (*falta: last*) — Factoriza $x^{2}+8x+15$.

- dado: $\text{parejas que multiplican }15:\ 1\cdot 15,\ 3\cdot 5$
- hueco `P1-b1`: $\text{la que suma }8\text{: el mayor es}$ → `5`

**P2** (*falta: middle*) — Factoriza $x^{2}-6x+8$.

- dado: $\text{producto }8>0\ \text{y suma }-6<0\Rightarrow\ \text{ambos negativos}$
- hueco `P2-b1`: $(-2)+(-4)=$ → `-6`
- hueco `P2-b2`: $(-2)\cdot(-4)=$ → `8`

**P3** (*falta: statement_only*) — Solo el planteamiento: $2x^{2}+7x+3$. El coeficiente principal no es 1 — di primero sobre qué número hay que buscar la pareja.

- hueco `P3-b1`: $a\cdot c=2\cdot 3=$ → `6`


### A7. Comparación de métodos

**Dos maneras de buscar la pareja**

$x^{2}+5x+6$. Una arranca por la suma; la otra por el producto.

- **Método 1 · Empezar por la suma** — 
- **Método 2 · Empezar por el producto** — 

**Pregunta:** ¿Por qué conviene empezar por el producto si las dos condiciones pesan igual?

**Insight:** Porque solo una de las dos cierra la búsqueda. Sumar 5 lo hacen infinitas parejas de enteros; multiplicar 6 lo hacen cuatro. El producto no es más importante que la suma — es más ÚTIL para empezar, porque acota. La suma sigue siendo la que decide, y por eso saltársela es el error de esta sala.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es la factorización de $x^{2}+5x+6$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $(x+2)(x+3)$ | — |
| 　 | `prod` | $(x+1)(x+6)$ | `pares_sin_verificar` |
| 　 | `sum` | $(x+2)(x+3)$ o $(x+1)(x+4)$, las dos valen | `pares_sin_verificar` |
| 　 | `neg` | $(x-2)(x-3)$ | `ignora_el_signo_de_la_suma` |

Escalera de pistas:
1. Lista las parejas que multiplican 6.
2. Son 1·6 y 2·3.
3. ¿Cuál de las dos suma 5?

**E2**

Dos números suman $-9$ y multiplican $20$. ¿Cuál es el menor de los dos?

Respuesta: `-5`

Escalera de pistas:
1. Producto positivo y suma negativa: los dos son negativos.
2. Parejas negativas que multiplican 20: −1·−20, −2·−10, −4·−5.
3. La que suma −9.

**E3**

Para factorizar $2x^{2}+7x+3$, ¿sobre qué número hay que buscar la pareja?

Respuesta: `6`

Escalera de pistas:
1. Con coeficiente principal distinto de 1 no se usa el término independiente solo.
2. Se multiplica el coeficiente principal por el independiente.
3. 2 · 3.

**E4**

¿Cuántos valores ENTEROS POSITIVOS puede tomar $b$ para que $x^{2}+bx+12$ se pueda factorizar con enteros?

Respuesta: `3`

Escalera de pistas:
1. Lista las parejas de enteros positivos que multiplican 12.
2. Son 1·12, 2·6 y 3·4.
3. Cada pareja da una suma distinta: 13, 8 y 7.

**E5**

Un mozo anota $x^{2}-5x+6=(x+2)(x+3)$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sign` | Los signos: deberían ser $(x-2)(x-3)$ | — |
| 　 | `pair` | La pareja: deberían ser 1 y 6 | `pares_sin_verificar` |
| 　 | `first` | El primer término: debería ser $2x^{2}$ | `confunde_coeficiente_principal` |
| 　 | `none` | No hay error | `ignora_el_signo_de_la_suma` |

Escalera de pistas:
1. El producto está bien: 2 · 3 = 6.
2. Mira la suma: 2 + 3 = 5, pero el trinomio tiene −5x.
3. Producto positivo y suma negativa: los dos números son negativos.

**E6**

¿Verdadera o falsa? «Si dos números multiplican el término independiente, ya sirven para factorizar el trinomio.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: además tienen que sumar el coeficiente del medio | — |
| 　 | `true` | Verdadera: el producto es la condición que manda | `pares_sin_verificar` |
| 　 | `true_pos` | Verdadera cuando los dos números son positivos | `pares_sin_verificar` |
| 　 | `false_prod` | Falsa: lo que tienen que cumplir es solo la suma | `ignora_la_condicion_del_producto` |

Escalera de pistas:
1. Prueba 1 y 6 en x² + 5x + 6.
2. Multiplican 6, correcto.
3. Pero estampan x² + 7x + 6, no x² + 5x + 6.

**E7**

Sin despiezar ninguno: ¿cuáles de estos trinomios se pueden factorizar con números enteros? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok1` | $x^{2}+7x+12$ | — |
| ✅ | `ok2` | $x^{2}-x-6$ | — |
| 　 | `no1` | $x^{2}+x+1$ | `cree_que_todo_trinomio_se_factoriza` |
| 　 | `no2` | $x^{2}+2x+5$ | `cree_que_todo_trinomio_se_factoriza` |

Escalera de pistas:
1. Para cada uno, lista las parejas que multiplican el último término.
2. En x² + x + 1 la única pareja entera es 1 y 1, que suma 2, no 1.
3. Hay trinomios que simplemente no se abren con enteros. Son dos de los cuatro.


### A9. Cierre

*¿Cumple las DOS condiciones?* — **Una pareja no vale por acertar la mitad**

Cada fila propone una pareja para un trinomio. La pregunta es si encaja: producto Y suma, las dos.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Las dos condiciones. Encaja. |
|  | ✗ | Acierta el producto y falla la suma. Es el error de esta sala. |
|  | ✅ | Producto positivo con suma negativa: los dos números negativos. |
|  | ✅ | Producto negativo: los signos son distintos. Encaja igual. |
|  | ~ (ámbar) | El método sirve, pero la lista NO sale del 3: sale de 2·3 = 6. Se parte el medio con 6 y 1 y se agrupa. Mismo oficio, un paso más. |
|  | ✗ | La única pareja que multiplica 1 es 1 y 1, y suma 2. No es que no la encontremos: no existe. |

La regla en una línea: **el producto da la lista, la suma elige.** Y si ninguna pareja de la lista suma lo que hace falta, el fardo no se despieza con enteros.

#### Pregunta de abstracción

Los tres tienen el mismo último término. ¿Qué determina el signo de los dos factores?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `both` | El signo del último dice si los dos números tienen el mismo signo, y el del medio dice cuál es | — |
| 　 | `mid` | Solo el signo del término del medio | — |
| 　 | `last` | Solo el signo del término independiente | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuánto vale el mayor menos el menor?
¿Cuánto vale el mayor menos el menor?

Respuesta: `5`

Escalera de pistas:
1. Lista las parejas de enteros positivos que multiplican 24.
2. La que suma 11 es 3 y 8.
3. 8 − 3.

Pólya: Entender: hay que hallar la pareja y luego restar. → Planear: listo las parejas que multiplican 24 y elijo la que suma 11. → Ejecutar: 1·24, 2·12, 3·8, 4·6. La que suma 11 es 3 y 8. → Comprobar: (x + 3)(x + 8) = x² + 11x + 24 ✓. Y 8 − 3 = 5.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que sabes probar antes de cortar.

- **Mejoró:** Avance: ya compruebas las dos condiciones antes de cerrar el despiece.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la condición de la suma antes de seguir.

**Q1**

¿Qué dos números suman 7 y multiplican 12? Escribe el mayor.

Respuesta: `4`

**Q2**

¿Cuál es la factorización de $x^{2}+7x+10$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $(x+2)(x+5)$ | — |
| 　 | `prod` | $(x+1)(x+10)$ | `pares_sin_verificar` |
| 　 | `neg` | $(x-2)(x-5)$ | `ignora_el_signo_de_la_suma` |

**Q3**

¿Cuánto es (−3) × (−6)?

Respuesta: `18`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N3-G03-TRINOMIO-D2` | `noMid` | `termino_comun_falta_suma` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-D2` | `swap` | `intercambia_suma_y_producto` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E1` | `prod` | `pares_sin_verificar` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E1` | `sum` | `pares_sin_verificar` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E1` | `neg` | `ignora_el_signo_de_la_suma` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E5` | `pair` | `pares_sin_verificar` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E5` | `first` | `confunde_coeficiente_principal` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E5` | `none` | `ignora_el_signo_de_la_suma` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E6` | `true` | `pares_sin_verificar` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E6` | `true_pos` | `pares_sin_verificar` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-E6` | `false_prod` | `ignora_la_condicion_del_producto` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-Q2` | `prod` | `pares_sin_verificar` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |
| `ALG-N3-G03-TRINOMIO-Q2` | `neg` | `ignora_el_signo_de_la_suma` | Lista con el producto y elige con la suma. Una pareja que solo acierta el producto estampa otro trinomio. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
