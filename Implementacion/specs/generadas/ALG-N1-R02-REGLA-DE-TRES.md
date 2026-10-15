# Nodo: Tres datos conocidos y uno que se deduce — ALG-N1-R02-REGLA-DE-TRES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-R02-REGLA-DE-TRES` |
| `concept_slug` | `regla_de_tres` |
| Error focal | `invierte_la_razon_en_la_regla_de_tres` |
| Sala / edificio | El tinte de lino |
| Guía | Iuty |
| Entra después de | `ALG-N1-R01-RAZONES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El tinte de lino · Regla de tres

**Título:** Tres datos conocidos y uno que se deduce

En la cuadrícula viste que escalar es multiplicar. Aquí se usa para lo que hace falta a diario: se conocen tres cantidades de una proporción y hay que sacar la cuarta. La cuenta es corta, y hay una manera de montarla que sale al revés.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de acercarse a la tina. Sin nota.

**D1**

Si 2 medidas de tinte tiñen 8 brazadas de lino, ¿cuántas brazadas tiñe 1 medida?

Respuesta: `4`

**D2**

Si 3 medidas tiñen 12 brazadas, ¿cuántas brazadas tiñen 6 medidas?

Respuesta: `24`

**D3**

Si hay que teñir MÁS lino, ¿qué pasa con el tinte que hace falta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `more` | Hace falta más tinte | — |
| 　 | `less` | Hace falta menos tinte | `toda_relacion_es_inversa` |
| 　 | `same` | Hace falta el mismo | `ignora_la_proporcionalidad` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Junto a la tina de tinte* — **Las brazadas que salieron descoloridas**

En la tina se tiñe el lino que después llevará el pigmento del muro. Iuty tiene la receta anotada:

«Tres medidas de tinte por cada doce brazadas de lino. Hoy hay veinte brazadas.»

«El tintorero de ayer montó la cuenta con los tres números y multiplicó los dos que tenía delante en la misma línea. Le salió menos de dos medidas para más lino del habitual.»

Iuty señala unas madejas apagadas colgando del techo.

«Las últimas seis brazadas salieron de ese color. Y el tinte no se puede volver a dar.»

**Pregunta:** Con tres datos de una proporción, ¿qué dos hay que multiplicar para sacar el cuarto?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Los dos que están en la misma fila | — |
| 　 | `b` | Los dos que están en diagonal, y se divide entre el que queda | — |
| 　 | `c` | Los dos mayores, y se divide entre el menor | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El camino largo y el atajo dan el mismo número**

La regla de tres no es una fórmula caída del cielo: es el camino largo abreviado.

- **Camino largo** — Primero cuánto tinte lleva UNA brazada, después se multiplica por las que haya.
- **El atajo** — Los mismos tres números, en un solo renglón. El 3 y el 20 están en diagonal.

**Resolución:** El atajo funciona porque la razón se conserva: tinte entre lino vale lo mismo hoy que ayer. De ahí sale la igualdad de dos fracciones, y de ahí que se multiplique en diagonal. Multiplicar los de la misma fila no responde a ninguna pregunta: junta tinte con tinte.

**Definición — Regla de tres directa**

$$\dfrac{a}{b}=\dfrac{x}{d}\;\Longrightarrow\; x=\dfrac{a\,d}{b}$$

Cuando dos magnitudes son DIRECTAMENTE proporcionales, su razón no cambia. Con tres datos conocidos se escribe la igualdad de las dos razones y se despeja el cuarto: se multiplican los dos que están en DIAGONAL con la incógnita y se divide entre el que queda. La incógnita puede ocupar cualquiera de las cuatro casillas.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{3}{12}=\dfrac{x}{20}` | la proporción | la razón tinte : lino no cambia |
| `x=\dfrac{3\cdot 20}{12}` | en diagonal | el 3 y el 20 se multiplican; el 12 divide |
| `\dfrac{3}{12}=\dfrac14` | por brazada | el camino largo: cuánto lleva una sola |
| `\dfrac{20}{12}=\dfrac53` | factor de escala | cuántas veces más lino hay hoy |
| `3\cdot\dfrac53=5` | escalar el tinte | el mismo factor se aplica a la otra magnitud |

### A5. Ejemplos resueltos

#### Sacar la cuarta cantidad · *resuelto*

Tres medidas de tinte tiñen 12 brazadas de lino. Hoy hay 20 brazadas. ¿Cuánto tinte hace falta?

- Escribo las dos razones con las magnitudes en el mismo sitio: tinte arriba, lino abajo.
- La incógnita es el tinte de hoy: 3/12 = x/20.
- Multiplico en diagonal con la x: 3 · 20 = 60.
- Divido entre el que queda: 60 ÷ 12 = 5.
- Hacen falta 5 medidas. Hay más lino que ayer, así que tenía que salir más de 3 ✓.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué se multiplica el 3 con el 20 y no el 3 con el 12?'}

#### Cuando la incógnita no está donde la esperabas · *resuelto*

Cinco tintoreros tiñen 30 brazadas en una jornada. Hoy hay 8 tintoreros. ¿Cuántas brazadas se tiñen?

- Coloco tintoreros arriba y brazadas abajo, en las dos razones.
- La incógnita está ahora abajo a la derecha: 5/30 = 8/x.
- La diagonal de la x es 30 · 8 = 240.
- Divido entre el que queda: 240 ÷ 5 = 48 brazadas.
- Compruebo: cada tintorero hace 6 brazadas, y 8 · 6 = 48 ✓.

#### El tintorero que multiplicó en la misma fila · *TRAMPA*

Vuelve la receta de la apertura. El tintorero escribió los tres números y calculó 3 · 12 ÷ 20, y le salieron 1,8 medidas para las 20 brazadas.

- Hoy hay 20 brazadas y ayer eran 12: hay más lino que teñir.
- Si hace falta más lino, hace falta más tinte. Cualquier resultado por debajo de 3 delata el error.
- Regla para no volver a caer: antes de dividir, di en voz alta si la respuesta debe subir o bajar.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': 'x=\\dfrac{3\\cdot 12}{20}', 'right_latex': 'x=\\dfrac{3\\cdot 20}{12}', 'rows': [{'wrong': 'Se multiplican los dos de la misma fila', 'right': 'Se multiplican los dos de la diagonal de la incógnita'}, {'wrong': '1{,}8\\ \\text{medidas para MÁS lino que ayer}', 'right': '5\\ \\text{medidas: más lino, más tinte ✓}'}]}
**¿Por qué falla?:** Explica por qué el resultado tenía que ser mayor que 3, y usa eso para descartar 1,8 sin rehacer la cuenta.


### A6. Puente — parcialmente resueltos

La cuenta de la tina va empezada; completa los huecos.

**P1** (*falta: last*) — Si 4 medidas tiñen 20 brazadas, ¿cuántas medidas para 35 brazadas?

- dado: $\dfrac{4}{20}=\dfrac{x}{35}$
- dado: $4\cdot 35=140$
- hueco `P1-b1`: $140\div 20=$ → `7`

**P2** (*falta: middle*) — Si 6 tintoreros tiñen 42 brazadas, ¿cuántas tiñen 9?

- dado: $\dfrac{6}{42}=\dfrac{9}{x}$
- hueco `P2-b1`: $42\cdot 9=$ → `378`
- hueco `P2-b2`: $378\div 6=$ → `63`

**P3** (*falta: statement_only*) — Solo el planteamiento: 5 medidas de tinte tiñen 15 brazadas. ¿Cuántas brazadas se tiñen con 12 medidas?

- hueco `P3-b1`: $x=$ → `36`


### A7. Comparación de métodos

**Dos maneras de llegar a la cuarta cantidad**

7 medidas tiñen 21 brazadas. ¿Cuánto tinte para 30 brazadas?

- **Método 1 · Bajar a la unidad** — 
- **Método 2 · Usar el factor de escala** — 

**Pregunta:** ¿Qué pasa con cada método si los números no dan una unidad cómoda?

**Insight:** Los dos aguantan, pero el segundo lo dice antes: el factor 30/21 es mayor que 1, así que el tinte tiene que subir, y eso se ve antes de calcular nada. El primero da la fracción 7/21 y hay que llegar al final para saber si el resultado creció. Es la misma idea de la cuadrícula: escalar es multiplicar por un factor, y ese factor es el que avisa de la dirección.

### A8. Práctica independiente (7 ítems)

**E1**

Si 5 medidas de tinte tiñen 20 brazadas, ¿cuántas medidas hacen falta para 28 brazadas?

Respuesta: `7`

Escalera de pistas:
1. Hay más lino que antes: el tinte tiene que subir.
2. Multiplica en diagonal: 5 · 28.
3. 140 ÷ 20 = …

**E2**

Para resolver $\dfrac{4}{9}=\dfrac{x}{27}$, ¿qué operación se hace?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $x=\dfrac{4\cdot 27}{9}$ | — |
| 　 | `row` | $x=\dfrac{4\cdot 9}{27}$ | `invierte_la_razon_en_la_regla_de_tres` |
| 　 | `all` | $x=4\cdot 9\cdot 27$ | `ignora_la_proporcionalidad` |
| 　 | `sub` | $x=27-9+4$ | `escalado_aditivo` |

Escalera de pistas:
1. Localiza la x y mira qué número tiene enfrente en diagonal.
2. La diagonal de la x es el 4 y el 27.
3. El que queda, el 9, divide.

**E3**

Si 8 tintoreros tiñen 56 brazadas en una jornada, ¿cuántas tiñen 3 tintoreros?

Respuesta: `21`

Escalera de pistas:
1. Hay menos tintoreros: el resultado tiene que bajar.
2. Cada tintorero hace 7 brazadas.
3. 3 · 7 = …

**E4**

Un tintorero calcula el tinte para 30 brazadas sabiendo que 6 medidas tiñen 24, y anota 4,8 medidas. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `inverted` | Montó la razón del revés: son $\dfrac{6\cdot 30}{24}=7{,}5$ | — |
| 　 | `div` | Dividió cuando tenía que restar | `escalado_aditivo` |
| 　 | `unit` | Calculó mal cuánto tiñe una medida | `ignora_la_proporcionalidad` |
| 　 | `none` | No hay error | `invierte_la_razon_en_la_regla_de_tres` |

Escalera de pistas:
1. 30 brazadas son más que 24.
2. Con más lino hace falta más tinte que 6 medidas.
3. 4,8 es menos que 6: imposible.

**E5**

¿Verdadera o falsa? «En una regla de tres se multiplican los dos números que están en la misma fila y se divide entre el tercero.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: se multiplican los de la diagonal de la incógnita | — |
| 　 | `true` | Verdadera: son los dos que se conocen juntos | `invierte_la_razon_en_la_regla_de_tres` |
| 　 | `true_order` | Verdadera si se escriben en el orden correcto | `invierte_la_razon_en_la_regla_de_tres` |
| 　 | `false_none` | Falsa: en una regla de tres no se multiplica nada | `sobregeneraliza_regla_de_tres` |

Escalera de pistas:
1. Prueba con 3/12 = x/20 de las dos maneras.
2. En diagonal da 5; en la misma fila da 1,8.
3. Solo una sube cuando el lino sube.

**E6**

Selecciona TODAS las situaciones que se resuelven con una regla de tres DIRECTA.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | Medidas de tinte y brazadas teñidas | — |
| 　 | `b` | Número de tintoreros y días que tardan en la misma tarea | — |
| ✅ | `c` | Brazadas de lino y su precio en grano | — |
| 　 | `d` | La edad del tintorero y las brazadas de la tina | — |

Escalera de pistas:
1. Directa significa que las dos suben a la vez.
2. Más tintoreros para la MISMA tarea son menos días, no más.
3. Y hay pares de cantidades que no tienen ninguna relación.

**E7**

La receta dice 7 medidas de tinte por 21 brazadas. Iuty encarga teñir 45 brazadas, pero en la tina solo caben 15 brazadas por tanda. ¿Cuántas medidas de tinte se gastan en total?

Respuesta: `15`

Escalera de pistas:
1. El tamaño de la tanda no cambia el total de tinte.
2. Cada brazada lleva 7/21 = 1/3 de medida.
3. 45 · 1/3 = …


### A9. Cierre

*¿Se resuelve con regla de tres directa?* — **Cuándo sirve el atajo y cuándo miente**

La regla de tres es rápida y no comprueba nada por su cuenta. Antes de aplicarla hay que saber si las dos cantidades suben juntas.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Más lino, más tinte. La diagonal de la x da el resultado. Es el caso focal. |
|  | ✅ | La posición de la x no cambia nada: siempre se multiplica su diagonal. |
|  | ~ (ámbar) | Se resuelve igual, pero bajar a la unidad deja 1/3 por medio. Ahí conviene el factor de escala. |
|  | ~ (ámbar) | Toda proporcionalidad directa pasa por el cero. Si con 0 de una no sale 0 de la otra, no es directa y el atajo no vale. |
|  | ✗ | Aquí una sube cuando la otra baja. Lo que se conserva es el producto, no la razón. Es la sala de las lámparas. |
|  | ✗ | Que haya tres números no obliga a que exista una cuarta cantidad. A veces no hay proporción que valga. |

La cuarta fila es la comprobación más barata que existe y casi nadie la hace: con cero de una magnitud, ¿sale cero de la otra? Si la respuesta es no, la regla de tres va a devolver un número creíble y equivocado. Y la quinta abre el caso que sí tiene regla propia: cuando una sube y la otra baja.

#### Pregunta de abstracción

¿Qué comparten las tres cuentas de la tina trabajadas en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `diagonal` | En las tres se multiplica la diagonal de la incógnita y se divide entre el que queda | — |
| 　 | `direction` | En las tres se puede saber antes de calcular si el resultado sube o baja | — |
| 　 | `row` | En las tres se multiplican los dos datos que se conocen juntos | — |
| 　 | `always` | En las tres el atajo sirve porque sirve para cualquier par de magnitudes | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas medidas de tinte hay que preparar?
¿Cuántas medidas de tinte hay que preparar?

Respuesta: `24`

Escalera de pistas:
1. Hay más lino que en la receta: el tinte tiene que subir.
2. Multiplica 9 · 64.
3. 576 ÷ 24 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otra receta. Sin nota.

- **Mejoró:** Avance: ya multiplicas en diagonal y compruebas la dirección del resultado.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el camino largo: cuánto tinte lleva UNA brazada.

**PD1**

Si 3 medidas de tinte tiñen 15 brazadas, ¿cuántas brazadas tiñe 1 medida?

Respuesta: `5`

**PD2**

Si 4 medidas tiñen 20 brazadas, ¿cuántas brazadas tiñen 8 medidas?

Respuesta: `40`

**PD3**

Si hay que teñir MENOS lino, ¿qué pasa con el tinte necesario?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `less` | Hace falta menos tinte | — |
| 　 | `more` | Hace falta más tinte | `toda_relacion_es_inversa` |
| 　 | `same` | Hace falta el mismo | `ignora_la_proporcionalidad` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-R02-REGLA-DE-TRES-D3` | `less` | `toda_relacion_es_inversa` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-D3` | `same` | `ignora_la_proporcionalidad` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E2` | `row` | `invierte_la_razon_en_la_regla_de_tres` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E2` | `all` | `ignora_la_proporcionalidad` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E2` | `sub` | `escalado_aditivo` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E4` | `div` | `escalado_aditivo` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E4` | `unit` | `ignora_la_proporcionalidad` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E4` | `none` | `invierte_la_razon_en_la_regla_de_tres` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E5` | `true` | `invierte_la_razon_en_la_regla_de_tres` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E5` | `true_order` | `invierte_la_razon_en_la_regla_de_tres` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-E5` | `false_none` | `sobregeneraliza_regla_de_tres` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-PD3` | `more` | `toda_relacion_es_inversa` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |
| `ALG-N1-R02-REGLA-DE-TRES-PD3` | `same` | `ignora_la_proporcionalidad` | Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
