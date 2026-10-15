# Nodo: Cada operación tiene su propio «no cambies nada» — PREALG-N3-M04-ELEMENTO-NEUTRO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N3-M04-ELEMENTO-NEUTRO` |
| `concept_slug` | `elemento_neutro` |
| Error focal | `neutro_es_el_mismo_para_toda_operacion` |
| Sala / edificio | El Calibre Cero |
| Guía | KatIA |
| Entra después de | `PREALG-N3-M03-DISTRIBUTIVA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El Calibre Cero · Elemento neutro

**Título:** Cada operación tiene su propio «no cambies nada»

Hay un número que, aplicado a cualquier otro, lo deja exactamente igual. Pero no es el mismo para todas las operaciones, y en algunas solo funciona si se pone de un lado. Vas a averiguar cuál es en cada caso y por qué el cero no sirve para todo.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de coger el calibre. Sin nota.

**D1**

¿Cuánto vale $37+0$?

Respuesta: `37`

**D2**

¿Cuánto vale $37\times 0$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | 0 | — |
| 　 | `same` | 37 | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `one` | 1 | `confunde_neutro_con_absorbente` |

**D3**

¿Qué número deja igual a cualquier otro al MULTIPLICARLO?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `one` | El 1 | — |
| 　 | `zero` | El 0 | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `none` | Ninguno: multiplicar siempre cambia el número | `multiplicar_siempre_agranda` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el Calibre Cero* — **La galga que no cambia nada**

La cuarta estación es un banco de calibración: varillas de acero, un calibre de precisión y una fila de galgas patrón colgadas por tamaño. Una galga se aplica a una varilla y la deja lista para el siguiente paso.

En la fila hay una galga marcada con un cero. Aplicada al banco de sumar, la varilla sale idéntica a como entró, y por eso el calibrador la llama «la que no cambia nada». Hoy la aplicó al banco de multiplicar. La varilla no salió idéntica: no salió nada.

**Pregunta:** ¿Existe un número que deje igual a cualquier otro, en cualquier operación?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí: el cero, en todas | — |
| 　 | `b` | Sí, pero cambia según la operación | — |
| 　 | `c` | No existe ninguno | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **La misma galga, dos bancos distintos**

Abajo, la galga del cero aplicada a los dos bancos. Fíjate en qué sale de cada uno.

- **Caso que funciona** — Sale idéntica. Aquí el 0 sí es «el que no cambia nada».
- **Caso que rompe la expectativa** — No sale idéntica: no sale nada. El 0 arrasó la varilla.

**Resolución:** El 0 no es «la nada» que se puede ignorar: es el punto de partida de la suma. Sumar 0 es no moverse, y por eso no cambia nada. Multiplicar por 0 es hacer cero copias, y eso no deja nada. El neutro del producto es otro: el 1, hacer una sola copia.

**Definición — El elemento neutro**

$$a+0=a\qquad a\times 1=a$$

El elemento neutro de una operación es el número que, combinado con cualquier otro, lo deja igual. El de la suma es 0; el del producto es 1. No hay un neutro universal, y en la resta y la división solo funciona puesto a la derecha.

| Símbolo | Se lee | Significa |
|---|---|---|
| `0` | neutro aditivo | no moverse desde donde estás |
| `1` | neutro multiplicativo | hacer una sola copia |
| `a\times 0=0` | el cero absorbe | no es neutro del producto: lo arrasa todo |
| `a-0=a\ \text{pero}\ 0-a=-a` | neutro por la derecha | en la resta el 0 solo sirve puesto detrás |
| `a\div 1=a\ \text{pero}\ 1\div a\neq a` | neutro por la derecha | en la división el 1 solo sirve puesto detrás |

### A5. Ejemplos resueltos

#### Dos galgas para dos bancos · *resuelto*

Una varilla de 46 tiene que pasar por el banco de sumar y por el de multiplicar saliendo intacta de los dos. ¿Qué galga se usa en cada uno?

- Banco de sumar: busco el número que sumado a 46 deja 46. Es el 0.
- Compruebo que sirve para cualquier varilla: 7 + 0 = 7, −3 + 0 = −3. Siempre.
- Banco de multiplicar: busco el número que multiplicado por 46 deja 46. No es el 0 (da 0): es el 1.
- Compruebo: 7 × 1 = 7, −3 × 1 = −3. También siempre.
- Dos operaciones, dos neutros distintos. Ninguna galga sirve para las dos.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se descarta el 0 para el producto. ¿Por qué «no cambiar nada» y «no dejar nada» no son lo mismo?'}

#### La galga que solo sirve puesta detrás · *resuelto*

La varilla de 46 entra al banco de restar con la galga del 0. ¿Sale idéntica? ¿Y si la galga entra primero?

- Con la galga detrás: 46 − 0 = 46. Sale idéntica.
- Con la galga delante: 0 − 46 = −46. Sale con el signo cambiado.
- En la suma daba igual el lado, porque la suma conmuta (M01).
- En la resta no conmuta, así que el neutro solo vale por un lado: se dice neutro POR LA DERECHA.
- Lo mismo pasa en la división con el 1: 46 ÷ 1 = 46, pero 1 ÷ 46 ≈ 0,02.

#### El calibrador que usó una sola galga · *TRAMPA*

El calibrador deja escrito: «La galga del cero no cambia nada, lo comprobé en el banco de sumar. Así que la uso también en el de multiplicar: 46 × 0 = 46».

- Vuelve a la definición del producto: 46 × 0 es hacer CERO grupos de 46.
- Cero grupos no dejan nada: el resultado es 0, y eso vale para cualquier varilla.
- El número que deja la varilla intacta al multiplicar es el 1: hacer un solo grupo.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '46\\times 0=46', 'right_latex': '46\\times 0=0\\qquad 46\\times 1=46', 'rows': [{'wrong': 'El 0 no cambia nada en ninguna operación', 'right': 'El 0 no cambia nada al SUMAR; al multiplicar lo arrasa'}, {'wrong': 'Hay una sola galga que sirve para todos los bancos', 'right': 'Cada operación tiene su propio neutro'}]}
**¿Por qué falla?:** ¿Por qué 46 × 0 no puede dar 46? Di cuál es el neutro correcto del producto.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Una varilla de 58 pasa por el banco de sumar con la galga neutra.

- dado: $\text{neutro de la suma}=0$
- hueco `P1-b1`: $58+0=$ → `58`

**P2** (*falta: middle*) — La misma varilla pasa por el banco de multiplicar, primero con la galga del 0 y después con la neutra.

- dado: $\text{banco de multiplicar}$
- hueco `P2-b1`: $58\times 0=$ → `0`
- hueco `P2-b2`: $58\times 1=$ → `58`

**P3** (*falta: statement_only*) — Solo el planteamiento: en el banco de elevar, ¿qué sale de una varilla de 58 con exponente 1? ¿Y qué sale de una varilla de 1 con exponente 58?

- hueco `P3-b1`: $58^{1}=$ → `58`
- hueco `P3-b2`: $1^{58}=$ → `1`


### A7. Comparación de métodos

**Dos caminos para la misma varilla**

¿Cuánto vale $(83\times 1)+(0\times 47)$? Las dos soluciones de abajo son correctas.

- **Método 1 · Calcular todo** — 
- **Método 2 · Reconocer neutro y absorbente** — 

**Pregunta:** ¿Qué habría pasado en el método 2 si el segundo término fuera 0 + 47 en vez de 0 × 47?

**Insight:** Con 0 + 47 el cero es NEUTRO y deja pasar el 47, así que el total sería 130. Con 0 × 47 es ABSORBENTE y lo borra. El mismo cero, dos comportamientos opuestos según el signo que tenga al lado: por eso no basta con reconocer el número, hay que leer la operación.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto vale $64\times 1$?

Respuesta: `64`

Escalera de pistas:
1. Multiplicar por 1 es hacer un solo grupo.
2. Un grupo de 64.
3. El 1 es el neutro del producto.

**E2**

¿Cuánto vale $64\times 0$?

Respuesta: `0`

Escalera de pistas:
1. Multiplicar por 0 es hacer cero grupos.
2. Cero grupos no dejan nada.
3. El 0 no es neutro del producto: lo absorbe.

**E3**

¿Cuánto vale $0-29$?

Respuesta: `-29`

Escalera de pistas:
1. Aquí el 0 va DELANTE, no detrás.
2. Se le quitan 29 a nada.
3. El resultado queda por debajo del cero.

**E4**

Un calibrador anota «$1\div 25=25$, porque el 1 es neutro». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `right_only` | El 1 solo es neutro puesto a la derecha: 25 ÷ 1 = 25, pero 1 ÷ 25 = 0,04 | — |
| 　 | `wrong_neutral` | El neutro de la división es el 0, no el 1 | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `arith` | Se equivocó al dividir: da 26 | `habito_error_de_calculo_no_de_metodo` |
| 　 | `none` | Ningún error, está bien | `neutro_funciona_por_los_dos_lados` |

Escalera de pistas:
1. ¿La división conmuta? Eso lo decidiste en la Prensa de Intercambio.
2. 1 ÷ 25 reparte 1 entre 25 partes.
3. El resultado es menor que 1, no 25.

**E5**

¿Es verdadera o falsa? «Existe un número que deja igual a cualquier otro en TODAS las operaciones.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_each` | Falsa: cada operación tiene el suyo (0 para sumar, 1 para multiplicar) | — |
| 　 | `true_zero` | Verdadera: el 0 | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `true_one` | Verdadera: el 1 | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `false_none` | Falsa: no existe neutro en ninguna operación | `niega_la_existencia_del_neutro` |

Escalera de pistas:
1. Prueba el candidato en las dos operaciones antes de decidir.
2. Si dices 0: calcula 5 × 0. Si dices 1: calcula 5 + 1.
3. Ninguno de los dos sobrevive a las dos pruebas.

**E6**

Sin calcular término a término: ¿cuánto vale (72 × 1) + (0 × 96)?

Respuesta: `72`

Escalera de pistas:
1. Uno de los dos términos es neutro y el otro absorbente.
2. 72 × 1 = 72.
3. 0 × 96 = 0, y 72 + 0 = …

**E7**

Una cuenta larga incluye el factor $(15-15)$ multiplicando a todo lo demás. ¿Cuánto vale la cuenta entera?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | 0: uno de los factores es cero y absorbe todo | — |
| 　 | `rest` | Lo que valga el resto: el (15−15) no cambia nada | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `cannot` | No se puede saber sin calcular el resto | `no_reconoce_el_absorbente` |
| 　 | `one` | 1 | `confunde_neutro_con_absorbente` |

Escalera de pistas:
1. Calcula primero cuánto vale (15 − 15).
2. 15 − 15 = 0.
3. Cualquier cosa multiplicada por 0 da 0.


### A9. Cierre

*El neutro a lo largo de las operaciones* — **¿Qué número deja el resultado intacto, y por qué lado?**

Las seis operaciones de la ciudad, cada una con su galga.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Neutro 0, por los dos lados: la suma conmuta. |
|  | ~ (ámbar) | Neutro 0 solo por la DERECHA. Puesto delante, cambia el signo. |
|  | ✅ | Neutro 1, por los dos lados. Ojo: el 0 aquí no es neutro sino absorbente. |
|  | ~ (ámbar) | Neutro 1 solo por la DERECHA. Puesto delante da el recíproco — y eso es la estación siguiente. |
|  | ~ (ámbar) | Neutro 1 solo en el EXPONENTE. En la base, el 1 absorbe. |
|  | ~ (ámbar) | Índice 1 deja el radicando intacto, pero no hay ningún radicando que deje intacto el índice. |

Ninguna galga sirve para todos los bancos, y en cuatro operaciones solo sirve por un lado. Fíjate en el patrón: las que aguantan por los dos lados son exactamente las que conmutan. En la Prensa de Contrapesos vas a buscar, para cada número, la pieza que lo devuelve al neutro.

#### Pregunta de abstracción

¿Qué comparten los casos donde el neutro funciona por los DOS lados?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `commutative` | Son las operaciones que conmutan | — |
| 　 | `same_number` | Usan el mismo número como neutro | — |
| 　 | `roles` | Son aquellas donde los dos números hacen el mismo papel | — |
| 　 | `grow` | Son las que hacen crecer el resultado | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Con qué medida sale la varilla?
¿Con qué medida sale la varilla?

Respuesta: `91`

Escalera de pistas:
1. Trata cada término por separado y mira qué operación lo acompaña.
2. 91 × 1 = 91 y 91 − 0 = 91.
3. 0 × 44 = 0, así que el último término no aporta nada.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya eliges la galga según el banco, no por costumbre.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre «no cambia nada» y «no deja nada».

**PD1**

¿Cuánto vale $52+0$?

Respuesta: `52`

**PD2**

¿Cuánto vale $52\times 0$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `zero` | 0 | — |
| 　 | `same` | 52 | `neutro_es_el_mismo_para_toda_operacion` |
| 　 | `one` | 1 | `confunde_neutro_con_absorbente` |

**PD3**

¿Es verdadera? $52-0=52$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `sobregeneraliza_elemento_neutro` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N3-M04-ELEMENTO-NEUTRO-D2` | `same` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-D2` | `one` | `confunde_neutro_con_absorbente` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-D3` | `zero` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-D3` | `none` | `multiplicar_siempre_agranda` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E4` | `wrong_neutral` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E4` | `arith` | `habito_error_de_calculo_no_de_metodo` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E4` | `none` | `neutro_funciona_por_los_dos_lados` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E5` | `true_zero` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E5` | `true_one` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E5` | `false_none` | `niega_la_existencia_del_neutro` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E7` | `rest` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E7` | `cannot` | `no_reconoce_el_absorbente` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-E7` | `one` | `confunde_neutro_con_absorbente` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-PD2` | `same` | `neutro_es_el_mismo_para_toda_operacion` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-PD2` | `one` | `confunde_neutro_con_absorbente` | Mira qué operación acompaña al número antes de decidir si es neutro. |
| `PREALG-N3-M04-ELEMENTO-NEUTRO-PD3` | `false` | `sobregeneraliza_elemento_neutro` | Mira qué operación acompaña al número antes de decidir si es neutro. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/03-prealg-n3-fabrica/m04-elemento-neutro-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
