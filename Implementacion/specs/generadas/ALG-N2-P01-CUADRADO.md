# Nodo: Al agrandar una lámina aparece una orla que nadie pidió — ALG-N2-P01-CUADRADO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N2-P01-CUADRADO` |
| `concept_slug` | `cuadrado_de_binomio` |
| Error focal | `binomio_cuadrado_falta_2ab` |
| Sala / edificio | La matriz cuadrada |
| Guía | Rayhana |
| Entra después de | `ALG-S00-CASA-DE-LA-SABIDURIA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La matriz cuadrada · Cuadrado de binomio

**Título:** Al agrandar una lámina aparece una orla que nadie pidió

En Kemet multiplicaste término a término y funcionó siempre. Aquí vas a encontrarte con un producto que aparece tantas veces que conviene tener un troquel para él. Pero el troquel estampa tres piezas, y casi todo el mundo recuerda solo dos.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar en la sala. Sin nota.

**D1**

¿Cuánto es 7²?

Respuesta: `49`

**D2**

¿A qué equivale $(3\cdot 5)^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | $3^{2}\cdot 5^{2}$ | — |
| 　 | `sum` | $3^{2}+5^{2}$ | `reparte_la_potencia_sobre_la_suma` |
| 　 | `once` | $3\cdot 5^{2}$ | `eleva_solo_el_segundo_factor` |

**D3**

Calcula 10² y luego (7 + 3)². ¿Cuánto vale el segundo?

Respuesta: `100`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la matriz cuadrada* — **La lámina que salió pequeña**

La sala guarda las matrices: planchas de cobre con las que se estampan láminas cuadradas. Cada matriz tiene un lado, y el lado se mide en dedos.

Rayhana señala una hoja de encargo de la semana pasada:

«Pedían una lámina cuadrada de lado 7 dedos, y al llegar el encargo la querían de lado 10: siete dedos y tres más. El aprendiz calculó el cobre necesario sumando lo que ocupa un cuadrado de 7 con lo que ocupa uno de 3. Cuarenta y nueve más nueve: cincuenta y ocho.»

«La lámina de lado 10 ocupa cien. Faltaron cuarenta y dos dedos de cobre, y la lámina salió con un borde sin estampar.»

**Pregunta:** Al agrandar un cuadrado de lado 7 a lado 10, ¿dónde se metió el cobre que faltó?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `orla` | En un borde alrededor del cuadrado viejo | — |
| 　 | `esquina` | Solo en la esquina nueva | — |
| 　 | `nada` | En ningún sitio: 49 + 9 debería bastar | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Cuatro piezas, no dos**

Estampar un cuadrado de lado a + b es estampar cuatro piezas sobre la misma plancha. Dos son cuadrados y dos son tiras iguales.

- **Lo que sí se reparte** — Aquí sí se puede repartir el exponente: los factores se reordenan y cada uno se junta con su pareja. Nada sobra.
- **Lo que no se reparte** — Al multiplicar término a término salen cuatro productos: a·a, a·b, b·a y b·b. Los dos del medio son iguales y se juntan en 2ab. Esa es la orla.

**Resolución:** El exponente se reparte sobre productos y cocientes, nunca sobre sumas ni restas. Con lado 7 + 3: el cuadrado de 7 ocupa 49, el de 3 ocupa 9, y las dos tiras ocupan 2 · 7 · 3 = 42. Justo el cobre que faltó.

**Definición — Cuadrado de un binomio**

$$(a+b)^{2} = a^{2} + 2ab + b^{2} \qquad (a-b)^{2} = a^{2} - 2ab + b^{2}$$

El cuadrado de un binomio tiene TRES términos: el cuadrado del primero, el doble del producto de los dos, y el cuadrado del segundo. El signo del término del medio es el signo que separa al binomio; los dos cuadrados salen siempre positivos, porque un cuadrado nunca es negativo.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a^{2}` | a al cuadrado | la lámina del lado viejo |
| `2ab` | dos a b | las dos tiras de la orla — el término que se olvida |
| `b^{2}` | b al cuadrado | la esquina nueva, el cuadradito de la ampliación |
| `(a-b)^{2}` | a menos b, al cuadrado | misma matriz, la orla se resta en vez de sumarse |
| `(ab)^{2}=a^{2}b^{2}` | a b al cuadrado es a cuadrado por b cuadrado | sobre un producto el exponente sí se reparte |

### A5. Ejemplos resueltos

#### Las tres piezas, una por una · *resuelto*

Rayhana pide estampar una lámina de lado 6x + 1 dedos. ¿Cuánto cobre ocupa?

- Cuadrado del primero: (6x)² = 36x². Ojo, se eleva el 6 y la x.
- Doble producto: 2 · 6x · 1 = 12x. Esta es la orla.
- Cuadrado del segundo: 1² = 1. La esquina.
- Queda 36x² + 12x + 1.
- Compruebo con x = 1: el lado mide 7 y la lámina ocupa 49. Y 36 + 12 + 1 = 49 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué la orla vale 12x y no 6x, si la tira de un lado mide 6x · 1?'}

#### La orla también puede quitar · *resuelto*

Otra matriz: lado 9m⁴ − 3n. Mismo troquel, y hay que vigilar un signo.

- Cuadrado del primero: (9m⁴)² = 81m⁸.
- Doble producto: 2 · 9m⁴ · 3n = 54m⁴n, y va restando porque el binomio resta.
- Cuadrado del segundo: (3n)² = 9n². Positivo, aunque el término restaba.
- Queda 81m⁸ − 54m⁴n + 9n².
- Solo el término del medio cambia de signo. Los de los extremos son cuadrados: nunca negativos.

#### El aprendiz que estampó dos piezas de tres · *TRAMPA*

Vuelve el encargo de la apertura, ahora con letras. El aprendiz anota el cobre de una lámina de lado x + 4 así:

- Con x = 1 el lado mide 5, así que la lámina ocupa 25.
- La anotación del aprendiz da 1 + 16 = 17. Faltan 8, que es justo 8x con x = 1.
- Regla para no volver a caer: antes de cerrar, cuenta los términos. Si son dos, falta la orla.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '(x+4)^{2}=x^{2}+16', 'right_latex': '(x+4)^{2}=x^{2}+8x+16', 'rows': [{'wrong': 'El exponente entra a cada sumando', 'right': 'El exponente entra a cada factor, y una suma no es un producto'}, {'wrong': 'Dos piezas: la lámina vieja y la esquina', 'right': 'Tres piezas: la lámina, las dos tiras y la esquina'}]}
**¿Por qué falla?:** Comprueba con x = 1 que la anotación del aprendiz da un número distinto, y di cuánto cobre se perdió.


### A6. Puente — parcialmente resueltos

La hoja de encargo va empezada; completa los huecos.

**P1** (*falta: last*) — Desarrolla $(x+5)^{2}$.

- dado: $x^{2}$
- dado: $5^{2}=25$
- hueco `P1-b1`: $\text{coeficiente de la orla}=$ → `10`

**P2** (*falta: middle*) — Desarrolla $(2x-3)^{2}$.

- dado: $(2x)^{2}=4x^{2}$
- dado: $(-3)^{2}=9$
- hueco `P2-b1`: $2\cdot 2x\cdot 3=$ → `12`
- hueco `P2-b2`: $\text{con }x=1:\ 4-12+9=$ → `1`

**P3** (*falta: statement_only*) — Solo el planteamiento: $[7w-(a^{2}+7w)]^{2}$. Simplifica el interior del corchete ANTES de estampar el troquel.

- hueco `P3-b1`: $\text{exponente de }a\text{ en el resultado}=$ → `4`


### A7. Comparación de métodos

**Dos maneras de estampar el mismo cuadrado**

$(x+2)^{2}$. Las dos llegan al mismo sitio; una enseña por qué.

- **Método 1 · El troquel** — 
- **Método 2 · Multiplicar término a término** — 

**Pregunta:** ¿Cuál de los dos explica de dónde sale el 2 del doble producto?

**Insight:** El segundo. El troquel es el atajo, pero quien solo conoce el atajo no tiene cómo notar que le falta una pieza. Multiplicando término a término aparecen cuatro productos, y los dos del medio —x·2 y 2·x— son el mismo número contado dos veces. Por eso el término del medio lleva un 2 delante: no es una regla que memorizar, es una tira contada por sus dos lados.

### A8. Práctica independiente (7 ítems)

**E1**

¿A qué equivale $(a+b)^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $a^{2}+2ab+b^{2}$ | — |
| 　 | `split` | $a^{2}+b^{2}$ | `binomio_cuadrado_falta_2ab` |
| 　 | `once` | $a^{2}+ab+b^{2}$ | `olvida_el_doble_en_el_producto_cruzado` |
| 　 | `double` | $2a+2b$ | `confunde_cuadrado_con_duplicar` |

Escalera de pistas:
1. Cuenta las piezas de la lámina: ¿son dos o son cuatro?
2. Las dos tiras del medio son iguales.
3. Prueba con a = 7 y b = 3: la lámina ocupa 100.

**E2**

Desarrolla $(6x+1)^{2}$. Usa $\wedge$ para el exponente, así: 36x^2+12x+1. No dejes espacios.

Respuesta: `36x^2+12x+1`

Escalera de pistas:
1. Cuadrado del primero: (6x)² — se elevan el 6 y la x.
2. Orla: 2 · 6x · 1.
3. La esquina es 1² = 1.

**E3**

Una lámina tiene lado $x+5$ dedos. Con $x=3$, ¿cuánto cobre ocupa?

Respuesta: `64`

Escalera de pistas:
1. Puedes sumar primero: 3 + 5.
2. O estampar el troquel: 9 + 30 + 25.
3. Las dos vías dan lo mismo. Ese es el punto.

**E4**

En $(2x-3)^{2}$, ¿cuál es el coeficiente del término del medio, sin el signo?

Respuesta: `12`

Escalera de pistas:
1. La orla es el doble del producto de los dos términos.
2. 2 · 2 · 3.
3. El signo va aparte: aquí resta.

**E5**

Un aprendiz anota $(3m-4)^{2}=9m^{2}-24m-16$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sign` | El último término: $(-4)^{2}=+16$, no $-16$ | — |
| 　 | `middle` | La orla: debería ser $-12m$ | `olvida_el_doble_en_el_producto_cruzado` |
| 　 | `first` | El primero: debería ser $3m^{2}$ | `eleva_solo_la_letra_y_no_el_coeficiente` |
| 　 | `none` | No hay error | `cuadrado_de_negativo_es_negativo` |

Escalera de pistas:
1. La orla está bien: 2 · 3m · 4 = 24m, y resta.
2. Mira los extremos. ¿Un cuadrado puede dar negativo?
3. (−4) · (−4) = +16.

**E6**

¿Verdadera o falsa? «Elevar al cuadrado se puede hacer término a término, igual que con un producto.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: sobre una suma aparece además el doble producto | — |
| 　 | `true` | Verdadera: el exponente entra a cada término | `binomio_cuadrado_falta_2ab` |
| 　 | `true_pos` | Verdadera solo cuando los dos términos son positivos | `binomio_cuadrado_falta_2ab` |
| 　 | `false_never` | Falsa: el exponente nunca se puede repartir, ni sobre productos | `reparte_la_potencia_sobre_la_suma` |

Escalera de pistas:
1. Prueba con números: (2 + 3)² frente a 2² + 3².
2. 25 frente a 13. La diferencia es 12 = 2 · 2 · 3.
3. Sobre un producto sí se reparte: (2 · 3)² = 4 · 9 = 36.

**E7**

Rayhana va a estampar cuatro encargos. ¿En cuáles hace falta la orla, o sea el doble producto? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | $(x+7)^{2}$ | — |
| ✅ | `dif` | $(x-7)^{2}$ | — |
| 　 | `prod` | $(7x)^{2}$ | `reparte_la_potencia_sobre_la_suma` |
| 　 | `quot` | $\left(\dfrac{x}{7}\right)^{2}$ | `reparte_la_potencia_sobre_la_suma` |

Escalera de pistas:
1. La orla aparece cuando dentro del paréntesis hay una suma o una resta.
2. Un producto y un cociente sí admiten repartir el exponente.
3. Son dos de los cuatro.


### A9. Cierre

*¿El exponente se puede repartir?* — **Dónde vale el atajo y dónde cuesta una orla**

El error de hoy no es olvidarse de un término: es repartir el exponente donde no se puede. Esta es la lista de dónde sí.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Los factores se reordenan y cada uno se junta con su pareja. |
|  | ✅ | Mismo motivo: dividir es multiplicar por el recíproco. |
|  | ✗ | Aparece la orla. Repartir aquí cuesta 2ab de cobre. |
|  | ✗ | La orla también está: resta en vez de sumar, pero está. |
|  | ~ (ámbar) | Aquí repartir da la respuesta correcta — pero por casualidad: la orla vale 2·a·0 = 0. Acertar no es lo mismo que tener razón. |
|  | ~ (ámbar) | Se reparte igual que la potencia, pero solo con a y b no negativos. Fuera de ahí deja de valer. |

La regla en una línea: **el exponente se reparte sobre lo que se multiplica, no sobre lo que se suma.** Y cuando hay suma, lo que aparece de más es el doble producto.

#### Pregunta de abstracción

Mira los tres desarrollos. ¿Qué es lo único que cambia entre ellos, y qué se mantiene igual?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `structure` | Siempre son tres términos con la misma estructura; cambian el coeficiente del primero y el signo de la orla | — |
| 　 | `terms` | Cambia el número de términos según el signo del binomio | — |
| 　 | `last` | Cambia el último término según el signo del binomio | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuántos dedos de cobre ocupa la lámina?
¿Cuántos dedos de cobre ocupa la lámina?

Respuesta: `169`

Escalera de pistas:
1. Primero calcula cuánto mide el lado con x = 2.
2. El lado mide 13.
3. 13 · 13.

Pólya: Entender: el lado es 4x + 5 y hay que hallar el área del cuadrado. → Planear: o sustituyo primero y elevo, o estampo el troquel y sustituyo después. → Ejecutar: 4·2 + 5 = 13, y 13² = 169. → Comprobar: por el troquel, 16x² + 40x + 25 con x = 2 da 64 + 80 + 25 = 169 ✓.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que conoces el troquel.

- **Mejoró:** Avance: hoy ves la orla donde antes había un hueco.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el reparto del exponente antes de seguir.

**Q1**

¿Cuánto es 12²?

Respuesta: `144`

**Q2**

¿A qué equivale $(x+6)^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $x^{2}+12x+36$ | — |
| 　 | `split` | $x^{2}+36$ | `binomio_cuadrado_falta_2ab` |
| 　 | `once` | $x^{2}+6x+36$ | `olvida_el_doble_en_el_producto_cruzado` |

**Q3**

Calcula (8 + 2)². ¿Cuánto vale?

Respuesta: `100`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N2-P01-CUADRADO-D2` | `sum` | `reparte_la_potencia_sobre_la_suma` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-D2` | `once` | `eleva_solo_el_segundo_factor` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E1` | `split` | `binomio_cuadrado_falta_2ab` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E1` | `once` | `olvida_el_doble_en_el_producto_cruzado` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E1` | `double` | `confunde_cuadrado_con_duplicar` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E5` | `middle` | `olvida_el_doble_en_el_producto_cruzado` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E5` | `first` | `eleva_solo_la_letra_y_no_el_coeficiente` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E5` | `none` | `cuadrado_de_negativo_es_negativo` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E6` | `true` | `binomio_cuadrado_falta_2ab` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E6` | `true_pos` | `binomio_cuadrado_falta_2ab` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-E6` | `false_never` | `reparte_la_potencia_sobre_la_suma` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-Q2` | `split` | `binomio_cuadrado_falta_2ab` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |
| `ALG-N2-P01-CUADRADO-Q2` | `once` | `olvida_el_doble_en_el_producto_cruzado` | Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, falta la orla. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
