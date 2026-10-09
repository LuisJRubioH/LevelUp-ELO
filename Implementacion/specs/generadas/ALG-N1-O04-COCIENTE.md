# Nodo: Tacharlo todo deja un uno, no una nada — ALG-N1-O04-COCIENTE

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-O04-COCIENTE` |
| `concept_slug` | `cociente_de_monomios` |
| Error focal | `cancelar_completo_da_cero` |
| Sala / edificio | La caseta del capataz |
| Guía | Bakenra |
| Entra después de | `ALG-N1-O03-PRODUCTO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La caseta del capataz · Cociente de monomios

**Título:** Tacharlo todo deja un uno, no una nada

En el taller multiplicaste monomios sumando exponentes. Aquí toca el camino de vuelta: repartir. Y hay un momento del reparto en el que la mano tacha lo último que quedaba y no sabe qué escribir en su lugar.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar en la caseta. Sin nota.

**D1**

¿Cuánto es 12 ÷ 4?

Respuesta: `3`

**D2**

¿Cuánto es 7 ÷ 7?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `one` | 1 | — |
| 　 | `zero` | 0 | `cancelar_completo_da_cero` |
| 　 | `seven` | 7 | `confunde_division_con_resta` |

**D3**

¿A qué equivale $\dfrac{x^{5}}{x^{2}}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three` | $x^{3}$ | — |
| 　 | `seven` | $x^{7}$ | `suma_los_exponentes_al_dividir` |
| 　 | `ten` | $x^{10}$ | `multiplica_los_exponentes_al_dividir` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la caseta del capataz* — **El día que nadie bebió**

La caseta lleva el censo de la obra y el reparto del agua. Cada jornada se cuenta cuántos cántaros suben y entre cuántos aguadores se reparten.

Bakenra señala una línea del censo de la semana pasada:

«Subieron 6a³ cántaros y había 6a³ aguadores. El escriba tachó los seis, tachó las aes, tachó los cubos… y al quedarse sin nada que tachar escribió un cero. Ración por aguador: cero.»

«Tenían el agua delante. La caseta les dijo que no les tocaba nada.»

**Pregunta:** Cuando arriba y abajo hay exactamente lo mismo, ¿qué queda al repartir?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Cero: se ha tachado todo y no queda nada escrito | — |
| 　 | `b` | Uno: a cada uno le toca una parte entera | — |
| 　 | `c` | Lo mismo que había arriba | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Tachar de a pares**

Dividir potencias es emparejar factores. Lo interesante pasa al final.

- **Sobran factores** — Cada x de abajo tacha una de arriba. Sobran tres: se restan los exponentes.
- **No sobra ninguno** — Se emparejan todos. Cada pareja vale 1, y 1 · 1 · 1 = 1. No queda un cero: queda un uno.

**Resolución:** Tachar no es borrar: es dividir cada factor entre sí mismo, y eso da 1. Mientras sobran factores el 1 no se nota, porque multiplicar por 1 no cambia nada. Cuando no sobra ninguno, el 1 es lo único que queda — y ahí es cuando hay que escribirlo.

**Definición — Cociente de monomios**

$$\dfrac{a x^{m}}{b x^{n}} = \dfrac{a}{b}\,x^{m-n}\qquad \dfrac{x^{n}}{x^{n}}=x^{0}=1$$

Para DIVIDIR dos monomios se dividen los coeficientes y, en cada letra, se RESTAN los exponentes. Si el exponente de arriba es mayor, la letra queda arriba; si es menor, queda abajo; si son iguales, la letra desaparece y en su lugar hay un 1. Los coeficientes tienen su propia cuenta: aunque las letras se vayan, el número que resulte de dividirlos se queda.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{x^{5}}{x^{2}}=x^{3}` | equis cinco entre equis dos | se restan los exponentes |
| `\dfrac{x^{3}}{x^{3}}=1` | queda uno | se emparejan todos: el resultado es 1, no 0 |
| `x^{0}=1` | equis a la cero | otra forma de escribir lo mismo |
| `\dfrac{x^{2}}{x^{5}}=\dfrac{1}{x^{3}}` | queda abajo | si sobran factores abajo, la letra se queda abajo |
| `\dfrac{15a^{3}}{5a^{3}}=3` | queda el coeficiente | las letras se van, el 3 se queda |

### A5. Ejemplos resueltos

#### Dos cuentas separadas · *resuelto*

Suben 12c⁴ cántaros y se reparten entre 3c² aguadores, donde c es el número de cuerdas de acarreo. ¿Cuántos cántaros toca a cada uno?

- Separo la cuenta de los números y la de la letra.
- Coeficientes: 12 ÷ 3 = 4. Se dividen, como cualquier par de números.
- Letra: c⁴ entre c² empareja dos factores y sobran dos → 4 − 2 = 2.
- Queda 4c².
- Compruebo con c = 3: arriba 12 · 81 = 972, abajo 3 · 9 = 27, y 972 ÷ 27 = 36 = 4 · 9 ✓.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué los coeficientes se dividen y los exponentes se restan, si es la misma división?'}

#### Lo que sobrevive a la cancelación · *resuelto*

Otra jornada: suben 15a³ cántaros y hay 5a³ aguadores. ¿Cuántos toca a cada uno?

- Coeficientes: 15 ÷ 5 = 3.
- Letra: a³ entre a³ empareja todos los factores y no sobra ninguno → 3 − 3 = 0.
- a⁰ es 1, así que la letra desaparece del registro.
- Queda 3 · 1 = 3 cántaros por aguador.
- Fíjate: se fueron las letras, no el número. El 3 no se cancela con nada.

#### El escriba que se quedó sin nada que tachar · *TRAMPA*

Vuelve el censo de la apertura: 6a³ cántaros entre 6a³ aguadores. El escriba tachó el 6, tachó la a, tachó el exponente, y escribió 0.

- Pruebo con a = 2: arriba 6 · 8 = 48, abajo 6 · 8 = 48, y 48 ÷ 48 = 1.
- Para que el reparto diera 0 tendría que no haber subido ningún cántaro: 0 ÷ 48 = 0.
- Regla para no volver a caer: al tachar lo último, escribe el 1 antes de cerrar el registro.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{6a^{3}}{6a^{3}}=0', 'right_latex': '\\dfrac{6a^{3}}{6a^{3}}=1', 'rows': [{'wrong': 'No queda nada escrito, luego vale 0', 'right': 'Cada pareja tachada vale 1, y el producto de unos es 1'}, {'wrong': 'Ración por aguador: 0 cántaros', 'right': 'Ración por aguador: 1 cántaro, que es justo lo que había'}]}
**¿Por qué falla?:** Explica con números por qué el resultado es 1, y di qué habría hecho falta arriba para que de verdad saliera 0.


### A6. Puente — parcialmente resueltos

El censo va empezado; completa los huecos.

**P1** (*falta: last*) — Divide $\dfrac{20c^{5}}{4c^{2}}$.

- dado: $20\div 4=5$
- dado: $5-2=3$
- hueco `P1-b1`: $\text{exponente del resultado}=$ → `3`

**P2** (*falta: middle*) — Divide $\dfrac{18a^{4}}{6a^{4}}$ y di cuánto vale con $a=7$.

- dado: $18\div 6=3,\quad 4-4=0$
- hueco `P2-b1`: $a^{0}=$ → `1`
- hueco `P2-b2`: $3\cdot 1=$ → `3`

**P3** (*falta: statement_only*) — Solo el planteamiento: $\dfrac{24c^{3}}{8c}$ con $c=3$. Primero el monomio, después el valor.

- hueco `P3-b1`: $3c^{2}\ \text{con}\ c=3:$ → `27`


### A7. Comparación de métodos

**Dos maneras de dividir potencias**

$\dfrac{a^{4}}{a^{4}}$. Es el caso en el que las dos maneras se separan.

- **Método 1 · Restar los exponentes** — 
- **Método 2 · Emparejar y tachar** — 

**Pregunta:** ¿Cuál de los dos evita que alguien escriba 0 al tacharlo todo?

**Insight:** El segundo. Restando exponentes se llega a a⁰ y hay que saber qué significa; si no se sabe, el hueco se rellena con lo primero que suene a «nada», que es el cero. Emparejando se ve que cada pareja vale 1 y que multiplicar unos sigue dando uno. Por eso a⁰ = 1 no es un convenio raro: es lo que sale de dividir algo entre sí mismo.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto es $\dfrac{8a^{3}}{8a^{3}}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `one` | 1 | — |
| 　 | `zero` | 0 | `cancelar_completo_da_cero` |
| 　 | `keep` | $a^{3}$ | `no_cancela_la_parte_literal` |
| 　 | `eight` | 8 | `no_divide_los_coeficientes` |

Escalera de pistas:
1. Arriba y abajo hay exactamente lo mismo.
2. Cualquier cantidad dividida entre sí misma da…
3. Prueba con a = 2: 64 ÷ 64.

**E2**

Divide $\dfrac{20c^{6}}{5c^{2}}$ y escribe el resultado. Usa $\wedge$ para el exponente, así: 4c^4. No dejes espacios.

Respuesta: `4c^4`

Escalera de pistas:
1. Divide los coeficientes: 20 ÷ 5.
2. Resta los exponentes: 6 − 2.
3. Queda un 4 delante y la c elevada a 4.

**E3**

Suben $18c^{4}$ cántaros y hay $6c^{2}$ aguadores. Con $c=2$, ¿cuántos cántaros toca a cada aguador?

Respuesta: `12`

Escalera de pistas:
1. Primero el monomio: 18 ÷ 6 = 3 y 4 − 2 = 2.
2. Queda 3c².
3. 3 · 4 = …

**E4**

Un escriba anota $\dfrac{10a^{5}}{5a^{5}}=0$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `two` | Las letras sí se van, pero queda $10\div 5=2$ | — |
| 　 | `exp` | El exponente se resta mal: queda $a^{10}$ | `suma_los_exponentes_al_dividir` |
| 　 | `one` | El resultado es 1, porque arriba y abajo hay lo mismo | `no_divide_los_coeficientes` |
| 　 | `none` | No hay error | `cancelar_completo_da_cero` |

Escalera de pistas:
1. Las letras se cancelan del todo: hasta ahí bien.
2. ¿Y los coeficientes? Arriba hay 10 y abajo 5.
3. No son iguales: no se cancelan, se dividen.

**E5**

¿Verdadera o falsa? «Cuando arriba y abajo se tacha todo, el resultado es 0.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: es 1, porque cada pareja tachada vale $1$ | — |
| 　 | `true` | Verdadera: no queda nada escrito | `cancelar_completo_da_cero` |
| 　 | `true_letters` | Verdadera solo cuando lo que se tacha son letras | `cancelar_completo_da_cero` |
| 　 | `false_keep` | Falsa: no se puede tachar todo, siempre queda la letra | `no_cancela_la_parte_literal` |

Escalera de pistas:
1. Prueba con números: 7 ÷ 7.
2. Da 1, no 0.
3. Tachar es dividir entre sí mismo, y eso deja un 1.

**E6**

Selecciona TODAS las igualdades verdaderas.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $\dfrac{x^{6}}{x^{2}}=x^{4}$ | — |
| 　 | `b` | $\dfrac{x^{6}}{x^{6}}=0$ | — |
| ✅ | `c` | $\dfrac{9x^{4}}{3x^{4}}=3$ | — |
| 　 | `d` | $\dfrac{x^{6}}{x^{2}}=x^{3}$ | — |

Escalera de pistas:
1. Resta los exponentes y comprueba el resto.
2. Cuando las letras se van del todo queda 1, no 0.
3. Y el coeficiente sigue su propia cuenta.

**E7**

El censo dice que subieron $30a^{4}$ cántaros y que hay $10a^{4}$ aguadores. Con $a=5$, ¿cuántos cántaros toca a cada aguador?

Respuesta: `3`

Escalera de pistas:
1. Las letras son iguales arriba y abajo: se cancelan.
2. Pero los coeficientes no: 30 ÷ 10.
3. El resultado no depende de a.


### A9. Cierre

*¿Qué sobrevive al reparto?* — **Qué queda después de emparejar**

Tachar solo vale entre factores, y lo que deja no siempre es lo que parece. Estas seis filas son todos los finales posibles de un reparto.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | El caso cómodo: se empareja lo que se puede y lo que sobra queda arriba. |
|  | ✅ | Dos cuentas a la vez: los números se dividen, los exponentes se restan. |
|  | ✅ | Se tacha hasta el final y queda 1. Es el caso focal: 1, nunca 0. |
|  | ~ (ámbar) | Las letras desaparecen, pero el 3 sobrevive: los coeficientes no se cancelaban, se dividían. |
|  | ~ (ámbar) | También se empareja, pero lo que sobra queda debajo. Arriba se queda el 1 de siempre. |
|  | ✗ | No hay nada que tachar: el 3 de arriba es un sumando, no un factor. Ese es el trabajo de los campos. |

La tercera fila es la que costó una jornada sin agua. La cuarta y la quinta avisan de que «se canceló» no significa «desapareció todo»: casi siempre sobrevive algo, y muchas veces es un número. Y la última marca el límite de esta sala — donde hay una suma arriba, tachar deja de estar permitido.

#### Pregunta de abstracción

¿Qué comparten los tres repartos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `pairs` | En los tres se empareja factor con factor, y cada pareja vale 1 | — |
| 　 | `two_books` | En los tres el coeficiente y el exponente llevan cuentas distintas | — |
| 　 | `empty` | En los tres, si se tacha todo, el resultado es 0 | — |
| 　 | `letters_stay` | En los tres la letra sobrevive siempre en el resultado | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos cántaros toca a cada aguador?
¿Cuántos cántaros toca a cada aguador?

Respuesta: `3`

Escalera de pistas:
1. Las letras son idénticas arriba y abajo.
2. Se cancelan y dejan un 1, no un 0.
3. Queda 24 ÷ 8 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otro censo. Sin nota.

- **Mejoró:** Avance: ya escribes el 1 cuando se tacha hasta el final.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el emparejado: cada pareja tachada vale 1, no cero.

**PD1**

¿Cuánto es 18 ÷ 6?

Respuesta: `3`

**PD2**

¿Cuánto es 9 ÷ 9?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `one` | 1 | — |
| 　 | `zero` | 0 | `cancelar_completo_da_cero` |
| 　 | `nine` | 9 | `confunde_division_con_resta` |

**PD3**

¿A qué equivale $\dfrac{y^{7}}{y^{3}}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `four` | $y^{4}$ | — |
| 　 | `ten` | $y^{10}$ | `suma_los_exponentes_al_dividir` |
| 　 | `twentyone` | $y^{21}$ | `multiplica_los_exponentes_al_dividir` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-O04-COCIENTE-D2` | `zero` | `cancelar_completo_da_cero` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-D2` | `seven` | `confunde_division_con_resta` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-D3` | `seven` | `suma_los_exponentes_al_dividir` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-D3` | `ten` | `multiplica_los_exponentes_al_dividir` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E1` | `zero` | `cancelar_completo_da_cero` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E1` | `keep` | `no_cancela_la_parte_literal` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E1` | `eight` | `no_divide_los_coeficientes` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E4` | `exp` | `suma_los_exponentes_al_dividir` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E4` | `one` | `no_divide_los_coeficientes` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E4` | `none` | `cancelar_completo_da_cero` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E5` | `true` | `cancelar_completo_da_cero` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E5` | `true_letters` | `cancelar_completo_da_cero` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-E5` | `false_keep` | `no_cancela_la_parte_literal` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-PD2` | `zero` | `cancelar_completo_da_cero` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-PD2` | `nine` | `confunde_division_con_resta` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-PD3` | `ten` | `suma_los_exponentes_al_dividir` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |
| `ALG-N1-O04-COCIENTE-PD3` | `twentyone` | `multiplica_los_exponentes_al_dividir` | Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
