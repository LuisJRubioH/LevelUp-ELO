# Nodo: Dos piezas que se diferencian en un signo, y el medio desaparece — ALG-N2-P02-CONJUGADOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N2-P02-CONJUGADOS` |
| `concept_slug` | `binomios_conjugados` |
| Error focal | `conjugado_da_suma_de_cuadrados` |
| Sala / edificio | El cuño de la cenefa |
| Guía | Rayhana |
| Entra después de | `ALG-N2-P01-CUADRADO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El cuño de la cenefa · Binomios conjugados

**Título:** Dos piezas que se diferencian en un signo, y el medio desaparece

En la matriz cuadrada apareció una orla que nadie pidió. Aquí pasa lo contrario: hay un producto donde el término del medio se va solo. Y no se va por magia — se va porque son dos tiras iguales con signos opuestos.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar. Sin nota.

**D1**

¿Cuánto es 13 × 7?

Respuesta: `91`

**D2**

¿Cuánto vale $+5m - 5m$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | 0 | — |
| 　 | `ten` | $10m$ | `suma_opuestos_como_si_fueran_iguales` |
| 　 | `keep` | $5m$ | `opuestos_no_se_anulan` |

**D3**

Calcula 10² − 3².

Respuesta: `91`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el cuño de la cenefa* — **La greca que sobraba por un lado y faltaba por el otro**

En esta mesa se estampan cenefas: tiras largas y estrechas que bordean una página. El cuño trabaja con dos medidas, un largo y un ancho.

Rayhana pone un encargo sobre la mesa:

«Una greca de 13 dedos de largo por 7 de ancho. Trece es diez y tres; siete es diez menos tres. El aprendiz vio los dos dieces y los dos treses y anotó: cien más nueve, ciento nueve.»

«La greca ocupa noventa y uno. Le sobró tinta para dieciocho dedos que no existen, y el cuño se atascó.»

**Pregunta:** ¿Por qué 13 × 7 da noventa y uno y no ciento nueve, si los números son 10 y 3?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `resta` | Porque en realidad hay que restar, no sumar | — |
| 　 | `cancela` | Porque algo se suma por un lado y se quita por el otro | — |
| 　 | `otro` | Porque 13 × 7 no tiene nada que ver con 10 y 3 | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Las dos tiras que se comen entre sí**

Estampar (a + b) por (a − b) da cuatro productos, igual que cualquier otro par de binomios. Lo especial es lo que pasa con los dos del medio.

- **Los cuatro productos** — Los dos del medio son −ab y +ab: la misma tira, una sumando y otra restando.
- **Lo que sobrevive** — Queda menos que a², no más. Por eso 13 × 7 se queda en 91 y no llega a 100: le falta justo el cuadrado de 3.

**Resolución:** Dos binomios son conjugados cuando tienen los mismos dos términos y solo se diferencian en el signo del segundo. Su producto no tiene término del medio, y el resultado es una resta: el cuadrado del primero menos el cuadrado del segundo.

**Definición — Producto de binomios conjugados**

$$(a+b)(a-b) = a^{2} - b^{2}$$

Suma por diferencia da diferencia de cuadrados. Solo dos términos, no tres: los productos cruzados son opuestos y se anulan. Y el signo del resultado es SIEMPRE una resta, aunque los dos binomios lleven un más delante — porque el que resta es el segundo cuadrado, no el binomio.

| Símbolo | Se lee | Significa |
|---|---|---|
| `(a+b)(a-b)` | a más b, por a menos b | los conjugados: mismos términos, distinto signo en el segundo |
| `-ab+ab=0` | menos a b más a b es cero | las dos tiras del medio, que se anulan entre sí |
| `a^{2}-b^{2}` | a al cuadrado menos b al cuadrado | lo único que queda: una diferencia, nunca una suma |
| `(x^{n}+1)(x^{n}-1)=x^{2n}-1` | equis a la ene más uno, por equis a la ene menos uno | el primero puede ser cualquier monomio; el troquel no cambia |
| `(x+y+1)(x+y-1)` | equis más ye más uno, por equis más ye menos uno | el primero puede ser un bloque entero: aquí a = x + y |

### A5. Ejemplos resueltos

#### Dos términos, no tres · *resuelto*

Rayhana encarga una cenefa de $(x+6)$ de largo por $(x-6)$ de ancho. ¿Cuánta greca ocupa?

- Cuadrado del primero: x · x = x².
- Tiras del medio: −6x y +6x. Suman cero, así que ni se escriben.
- Cuadrado del segundo: 6 · 6 = 36, y va restando.
- Queda x² − 36. Dos términos.
- Compruebo con x = 10: la greca mide 16 × 4 = 64, y 100 − 36 = 64 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué las dos tiras del medio miden exactamente lo mismo, si una viene del primer paréntesis y la otra del segundo?'}

#### El troquel no mira qué hay dentro · *resuelto*

Otro encargo: $(a^{3}-b^{3})(a^{3}+b^{3})$. Están al revés y son potencias, pero siguen siendo conjugados.

- Primero: a³. Al cuadrado da a⁶, porque 3 · 2 = 6.
- Segundo: b³. Al cuadrado da b⁶.
- Las tiras del medio, −a³b³ y +a³b³, se anulan igual que antes.
- Queda a⁶ − b⁶.
- El orden de los paréntesis no importa: el que resta es el segundo TÉRMINO, no el segundo factor.

#### El aprendiz que sumó los dos cuadrados · *TRAMPA*

Vuelve la greca de la apertura, ahora con letras. El aprendiz anota el encargo $(x+4)(x-4)$ así:

- Con x = 5 la greca mide 9 × 1 = 9.
- La anotación del aprendiz da 25 + 16 = 41. Le sobran 32.
- Regla para no volver a caer: conjugados → SIEMPRE resta. Si escribiste un más, revisa.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '(x+4)(x-4)=x^{2}+16', 'right_latex': '(x+4)(x-4)=x^{2}-16', 'rows': [{'wrong': 'Los dos cuadrados se suman', 'right': 'El segundo cuadrado se resta: sale de (+4)·(−4)'}, {'wrong': 'La greca ocupa más que un cuadrado de lado x', 'right': 'Ocupa menos: le falta justo el cuadrado del recorte'}]}
**¿Por qué falla?:** Comprueba con x = 5 que la anotación del aprendiz da un número distinto, y di cuánta greca sobra en su cuenta.


### A6. Puente — parcialmente resueltos

El encargo va empezado; completa los huecos.

**P1** (*falta: last*) — Multiplica $(3m-4)(3m+4)$.

- dado: $(3m)^{2}=9m^{2}$
- hueco `P1-b1`: $\text{lo que se resta}=$ → `16`

**P2** (*falta: middle*) — Multiplica $\left(\dfrac{1}{2}x-1\right)\left(\dfrac{1}{2}x+1\right)$ y evalúa en $x=4$.

- dado: $\left(\tfrac{1}{2}x\right)^{2}=\tfrac{1}{4}x^{2},\quad 1^{2}=1$
- hueco `P2-b1`: $\tfrac{1}{4}\cdot 16=$ → `4`
- hueco `P2-b2`: $4-1=$ → `3`

**P3** (*falta: statement_only*) — Solo el planteamiento: $(8x^{2}y-3x)(3x+8x^{2}y)$. El segundo paréntesis viene en otro orden — identifica cuál es el término que resta.

- hueco `P3-b1`: $\text{exponente de }x\text{ en el primer cuadrado}=$ → `4`


### A7. Comparación de métodos

**Dos maneras de ver por qué el medio se va**

$(x+5)(x-5)$. Una lo calcula; la otra explica por qué siempre pasa.

- **Método 1 · Multiplicar y tachar** — 
- **Método 2 · Recortar y pegar** — 

**Pregunta:** ¿Cuál de los dos deja claro que el resultado es MENOR que x²?

**Insight:** El segundo. Multiplicando y tachando uno confirma el resultado, pero el signo menos sigue pareciendo un accidente del cálculo. Recortando y pegando se ve que la greca es un cuadrado al que le falta un trozo, y que ese trozo es siempre un cuadrado. Por eso la respuesta nunca puede ser una suma: no se le puede quitar algo a una figura y que salga más grande.

### A8. Práctica independiente (7 ítems)

**E1**

¿A qué equivale $(a+b)(a-b)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `dif` | $a^{2}-b^{2}$ | — |
| 　 | `sum` | $a^{2}+b^{2}$ | `conjugado_da_suma_de_cuadrados` |
| 　 | `middle` | $a^{2}-2ab+b^{2}$ | `confunde_conjugados_con_cuadrado_de_binomio` |
| 　 | `flat` | $a^{2}-b$ | `no_eleva_el_segundo_termino` |

Escalera de pistas:
1. Escribe los cuatro productos y mira los dos del medio.
2. −ab y +ab suman cero.
3. Prueba con a = 10 y b = 3: la greca mide 13 × 7 = 91.

**E2**

Multiplica $(x+6)(x-6)$. Usa $\wedge$ para el exponente, así: x^2-36. No dejes espacios.

Respuesta: `x^2-36`

Escalera de pistas:
1. Las tiras del medio se anulan: quedan dos términos.
2. El cuadrado del primero es x².
3. El del segundo, 36, va restando.

**E3**

Una greca mide $(x+9)$ de largo por $(x-9)$ de ancho. Con $x=11$, ¿cuánta greca ocupa?

Respuesta: `40`

Escalera de pistas:
1. Puedes multiplicar directo: 20 × 2.
2. O usar el troquel: 121 − 81.
3. Las dos vías dan lo mismo.

**E4**

En $(a^{3}-b^{3})(a^{3}+b^{3})$, ¿cuál es el exponente de $a$ en el resultado?

Respuesta: `6`

Escalera de pistas:
1. El primer término se eleva al cuadrado.
2. Elevar una potencia al cuadrado multiplica el exponente por 2.
3. 3 · 2.

**E5**

Un aprendiz anota $(2m-4)(2m+4)=2m^{2}-16$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `first` | El primero: $(2m)^{2}=4m^{2}$, no $2m^{2}$ | — |
| 　 | `sign` | El signo: debería ser $+16$ | `conjugado_da_suma_de_cuadrados` |
| 　 | `middle` | Falta el término del medio, $-16m$ | `confunde_conjugados_con_cuadrado_de_binomio` |
| 　 | `none` | No hay error | `eleva_solo_la_letra_y_no_el_coeficiente` |

Escalera de pistas:
1. El signo está bien: conjugados dan resta.
2. Mira el primer término. ¿Qué se eleva al cuadrado, solo la m?
3. (2m)² = 2² · m² = 4m².

**E6**

¿Verdadera o falsa? «Como los dos paréntesis llevan los mismos términos, el resultado es la suma de sus cuadrados.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: es la resta, porque un cruzado sale negativo | — |
| 　 | `true` | Verdadera: los dos términos aparecen elevados al cuadrado | `conjugado_da_suma_de_cuadrados` |
| 　 | `true_pos` | Verdadera cuando el primer paréntesis es el de la suma | `conjugado_da_suma_de_cuadrados` |
| 　 | `false_middle` | Falsa: queda además un término del medio | `confunde_conjugados_con_cuadrado_de_binomio` |

Escalera de pistas:
1. Prueba con a = 10 y b = 3: 13 × 7.
2. 91, no 109.
3. La diferencia, 18, es 2 · 9: el cuadrado de 3 contado dos veces de más.

**E7**

Rayhana revisa cuatro encargos. ¿En cuáles se anula el término del medio? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `conj` | $(x+7)(x-7)$ | — |
| ✅ | `swap` | $(3x-2)(2+3x)$ | — |
| 　 | `same` | $(x+7)(x+7)$ | `confunde_conjugados_con_cuadrado_de_binomio` |
| 　 | `other` | $(x+7)(x-5)$ | `cree_que_cualquier_par_de_binomios_cancela` |

Escalera de pistas:
1. Se anula cuando los dos paréntesis tienen los MISMOS términos y difieren solo en un signo.
2. El orden dentro del paréntesis da igual: 2 + 3x es lo mismo que 3x + 2.
3. Son dos de los cuatro.


### A9. Cierre

*¿Se anula el término del medio?* — **Cuándo el cuño deja dos piezas y cuándo tres**

Todo el nodo cabe en una pregunta: ¿los dos productos cruzados son opuestos? Si lo son, se van. Si no, se quedan.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | −ab y +ab son opuestos: se anulan y quedan dos términos. |
|  | ✗ | Los cruzados son iguales, no opuestos: se suman y dan la orla. |
|  | ✗ | Igual que arriba: los dos cruzados restan y se acumulan. |
|  | ~ (ámbar) | El medio SÍ se anula, pero el resultado sale invertido: aquí el que resta es a². Fíjate en qué término lleva el menos, no en qué paréntesis. |
|  | ✗ | Los cruzados no son opuestos: no hay nada que anular. |
|  | ✅ | El «primero» puede ser una suma: aquí a = x + y. El troquel no cambia. |

La regla en una línea: **suma por diferencia da diferencia de cuadrados.** Y si el resultado te sale con un más entre los dos cuadrados, algo se rompió: la greca no puede ocupar más que el cuadrado del que salió.

#### Pregunta de abstracción

Mira los tres productos. ¿Qué tienen en común, más allá de los números concretos?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `structure` | En los tres el resultado tiene dos términos y el segundo resta, sea cual sea lo que haya dentro del paréntesis | — |
| 　 | `letters` | En los tres el primer término es una letra sola elevada al cuadrado | — |
| 　 | `numbers` | En los tres el segundo término es un número | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuántos dedos de greca ocupa?
¿Cuántos dedos de greca ocupa?

Respuesta: `63`

Escalera de pistas:
1. Con n = 3 y x = 2, ¿cuánto vale xⁿ?
2. xⁿ = 8, así que los paréntesis son (8 + 1) y (8 − 1).
3. 9 · 7.

Pólya: Entender: son conjugados, con xⁿ de primer término y 1 de segundo. → Planear: aplico el troquel, x^{2n} − 1, y luego sustituyo. → Ejecutar: con n = 3 queda x⁶ − 1; con x = 2, 64 − 1 = 63. → Comprobar: directo, (8 + 1)(8 − 1) = 9 · 7 = 63 ✓.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que conoces el cuño.

- **Mejoró:** Avance: ya ves por qué el medio se va, y por qué el resultado resta.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo los productos cruzados antes de seguir.

**Q1**

¿Cuánto es 12 × 8?

Respuesta: `96`

**Q2**

¿A qué equivale $(m+9)(m-9)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `dif` | $m^{2}-81$ | — |
| 　 | `sum` | $m^{2}+81$ | `conjugado_da_suma_de_cuadrados` |
| 　 | `middle` | $m^{2}-18m+81$ | `confunde_conjugados_con_cuadrado_de_binomio` |

**Q3**

Calcula 10² − 2².

Respuesta: `96`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N2-P02-CONJUGADOS-D2` | `ten` | `suma_opuestos_como_si_fueran_iguales` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-D2` | `keep` | `opuestos_no_se_anulan` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E1` | `sum` | `conjugado_da_suma_de_cuadrados` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E1` | `middle` | `confunde_conjugados_con_cuadrado_de_binomio` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E1` | `flat` | `no_eleva_el_segundo_termino` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E5` | `sign` | `conjugado_da_suma_de_cuadrados` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E5` | `middle` | `confunde_conjugados_con_cuadrado_de_binomio` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E5` | `none` | `eleva_solo_la_letra_y_no_el_coeficiente` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E6` | `true` | `conjugado_da_suma_de_cuadrados` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E6` | `true_pos` | `conjugado_da_suma_de_cuadrados` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-E6` | `false_middle` | `confunde_conjugados_con_cuadrado_de_binomio` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-Q2` | `sum` | `conjugado_da_suma_de_cuadrados` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |
| `ALG-N2-P02-CONJUGADOS-Q2` | `middle` | `confunde_conjugados_con_cuadrado_de_binomio` | Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van y queda una resta. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
