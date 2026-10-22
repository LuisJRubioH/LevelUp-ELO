# Nodo: Ser letra no te hace variable — ALG-N1-L02-CONSTANTES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-L02-CONSTANTES` |
| `concept_slug` | `constantes` |
| Error focal | `toda_letra_es_variable` |
| Sala / edificio | El estante sellado |
| Guía | Meritka |
| Entra después de | `ALG-N1-L01-VARIABLES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El estante sellado · Constantes

**Título:** Ser letra no te hace variable

Ya sabes que una letra guarda un número. Ahora hay que separar, dentro del mismo registro, lo que cambia de lo que está fijado de una vez para siempre — y el aspecto del símbolo no sirve para decidirlo.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el estante. Sin nota.

**D1**

Una vara patrón mide 7 palmos y no cambia nunca. ¿Cuánto miden 5 varas?

Respuesta: `35`

**D2**

En $6k$, ¿qué parte puede tomar valores distintos?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `k` | La $k$ | — |
| 　 | `six` | El $6$ | `confunde_coeficiente_con_variable` |
| 　 | `both` | Las dos | `toda_letra_es_variable` |

**D3**

¿Puede un número fijo escribirse con una letra?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí, si a esa letra se le ha fijado un valor | — |
| 　 | `no` | No: las letras son siempre para lo que cambia | `toda_letra_es_variable` |
| 　 | `only_greek` | Solo si es una letra griega | `toda_letra_es_variable` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Ante el estante sellado* — **El estante que nadie puede corregir**

Meritka descorre un sello de arcilla. Dentro hay medidas patrón: una vara, una cuerda con nudos, un peso de piedra con una marca grabada.

«Esto no se toca», dice. «Si mañana alguien decide que la vara mide otra cosa, todos los registros del archivo dejan de valer a la vez. Por eso está sellado: no porque sea valioso, sino porque tiene que ser el mismo siempre.»

En el registro que KatIA acaba de escribir, en cambio, hay tres símbolos, y uno de ellos es una letra que tampoco puede cambiar nunca.

**Pregunta:** ¿Cómo se sabe si un símbolo puede cambiar de valor o no?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Las letras cambian y los números no | — |
| 　 | `b` | Depende de lo que represente, no de si es letra o número | — |
| 　 | `c` | Lo que va al principio de la expresión no cambia | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos símbolos que se parecen y no se comportan igual**

Los dos son letras. Solo uno admite que le cambien el valor.

- **Cambia** — Cada pedido trae un valor distinto. Es una variable.
- **No cambia** — Se escribe con letra por comodidad, pero su valor está fijado. Es una constante.

**Resolución:** La frontera no pasa por el tipo de símbolo, sino por una pregunta: ¿alguien puede darle otro valor sin romper el registro? Si sí, es variable. Si no, es constante — y da igual que se escriba con cifra, con letra latina o con letra griega.

**Definición — Constante, coeficiente y término constante**

$$7v+2\qquad v\ \text{varía};\ 7\ \text{y}\ 2\ \text{no}$$

Una CONSTANTE es un valor que no cambia dentro del problema. Puede escribirse con cifra (el 2) o con letra (π, o una L a la que se le ha fijado un valor). Dentro de una expresión conviene distinguir dos papeles: el COEFICIENTE es la constante que multiplica a una variable, y el TÉRMINO CONSTANTE es la que va sola, sin letra al lado.

| Símbolo | Se lee | Significa |
|---|---|---|
| `v` | uve | variable: cambia con cada pedido |
| `7\ \text{en}\ 7v` | coeficiente | constante que multiplica a la variable |
| `2\ \text{en}\ 7v+2` | término constante | constante que va sola, sin letra |
| `\pi\approx 3{,}1416` | pi | constante escrita con letra: nunca cambia |
| `L=7` | ele igual a siete | una letra a la que se le fija un valor deja de variar |

### A5. Ejemplos resueltos

#### Separar lo fijo de lo que cambia · *resuelto*

Cada vara que se pide cuesta 7 medidas de grano, y por cada pedido se cobran 2 medidas fijas de acarreo. Escribe el coste y di qué papel tiene cada número.

- Lo que cambia es cuántas varas se piden: la llamo v. Es la variable.
- El 7 acompaña a la v y la multiplica: es el coeficiente.
- El 2 no toca a ninguna letra: es el término constante.
- El coste es 7v + 2. Con v = 4 son 30 medidas; con v = 10, son 72.
- Fíjate: el 7 y el 2 no cambiaron entre un pedido y otro. Solo cambió la v.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'El 7 y el 2 son los dos constantes. ¿Por qué se les llama distinto?'}

#### Una constante escrita con letra · *resuelto*

El brocal del pozo del patio es circular. Su contorno se calcula con 2·π·r, donde r es el radio. ¿Qué cambia aquí y qué no?

- Hay tres símbolos: el 2, la π y la r.
- El 2 es una cifra fija: constante, sin discusión.
- La π es una LETRA, pero su valor es siempre el mismo, unos 3,1416: constante también.
- La r es el radio: cambia según el pozo que se mida. Es la única variable.
- En 2πr hay dos constantes y una variable, aunque a simple vista haya una cifra y dos letras.

#### El aprendiz que contó las letras · *TRAMPA*

Un aprendiz recibe el registro 2πr y anuncia: «hay dos letras, así que hay dos cantidades que cambian; el único número fijo es el 2».

- Mido dos veces el mismo pozo: r vale lo mismo las dos veces y el contorno también.
- Mido otro pozo más ancho: cambia r, y solo r. π sigue valiendo 3,1416.
- Regla para no volver a caer: no cuentes letras, pregunta «¿esto puede tomar otro valor?».

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\pi\\ \\text{cambia}', 'right_latex': '\\pi\\approx 3{,}1416\\ \\text{siempre}', 'rows': [{'wrong': 'Es letra, luego varía', 'right': 'Varía o no según lo que represente; π representa un valor fijo'}, {'wrong': 'El 2 es el único fijo', 'right': 'El 2 y π son fijos; la única que varía es r'}]}
**¿Por qué falla?:** Explica por qué π no puede ser variable y di cuántas cantidades cambian de verdad en 2πr.


### A6. Puente — parcialmente resueltos

El registro va empezado; completa los huecos.

**P1** (*falta: last*) — El coste de un pedido es 7v + 2. ¿Cuánto cuesta pedir 6 varas?

- dado: $7v+2\quad\text{con }v=6$
- dado: $7\cdot 6=42$
- hueco `P1-b1`: $42+2=$ → `44`

**P2** (*falta: middle*) — En 9m + 5, escribe primero el coeficiente y después el término constante.

- dado: $9m+5$
- hueco `P2-b1`: $\text{coeficiente}=$ → `9`
- hueco `P2-b2`: $\text{término constante}=$ → `5`

**P3** (*falta: statement_only*) — Solo el planteamiento: una cuerda patrón mide 12 palmos y se cortan t trozos de 2 palmos. ¿Cuántos palmos quedan si t = 4?

- hueco `P3-b1`: $12-2t=$ → `4`


### A7. Comparación de métodos

**Dos maneras de decidir si algo es constante**

¿Es constante la $g$ de $g\cdot t$, si $g$ es el peso de una piedra patrón?

- **Método 1 · Preguntar al enunciado** — 
- **Método 2 · Probar dos casos** — 

**Pregunta:** ¿Cuál usarías si el registro solo trae la fórmula, sin explicación?

**Insight:** El segundo. Cuando falta el enunciado, la única prueba fiable es mover una cantidad y mirar cuáles se mueven con ella: las que no se inmutan son las constantes, estén escritas como estén.

### A8. Práctica independiente (7 ítems)

**E1**

En $8p-3$, ¿cuál es el término constante?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `minus3` | −3 | — |
| 　 | `eight` | 8 | `confunde_coeficiente_con_constante` |
| 　 | `p` | p | `toda_letra_es_variable` |
| 　 | `three` | 3 | `pierde_el_signo_del_termino` |

Escalera de pistas:
1. El término constante es el que va SIN letra al lado.
2. El 8 está pegado a la p: multiplica, no va solo.
3. El signo forma parte del término.

**E2**

El coste de un pedido es 7v + 2 medidas, donde v es el número de varas. ¿Cuánto cuesta pedir 9 varas?

Respuesta: `65`

Escalera de pistas:
1. Sustituye v por 9.
2. Primero el producto, después la suma.
3. 63 + 2 = …

**E3**

En el área del círculo, $A=\pi r^{2}$, ¿qué es $\pi$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `constant` | Una constante: siempre vale lo mismo | — |
| 　 | `variable` | Una variable: es una letra | `toda_letra_es_variable` |
| 　 | `unknown` | Una incógnita que hay que despejar | `toda_letra_es_variable` |
| 　 | `area` | El área, escrita de otra forma | `confunde_simbolo_con_resultado` |

Escalera de pistas:
1. ¿Puede π valer una cosa hoy y otra mañana?
2. Su valor es siempre unos 3,1416.
3. Lo que cambia de un círculo a otro es el radio.

**E4**

Un escriba anota: «en 5x + 4 hay dos constantes, el 5 y el 4, y las dos son términos constantes». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `role` | Constantes sí son las dos, pero el 5 es coeficiente: término constante solo el 4 | — |
| 　 | `not_constant` | El 5 no es constante | `confunde_coeficiente_con_variable` |
| 　 | `count` | Hay tres constantes, no dos | `cuenta_simbolos_no_terminos` |
| 　 | `none` | No hay error | `confunde_coeficiente_con_constante` |

Escalera de pistas:
1. Las dos son constantes: eso está bien dicho.
2. La diferencia está en si acompañan a una letra o van solas.
3. El 5 multiplica a la x; el 4 no multiplica a nada.

**E5**

¿Es verdadera o falsa? «Todo símbolo escrito con letra es una variable.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: $\pi$ es letra y su valor nunca cambia | — |
| 　 | `true` | Verdadera: para eso se usan las letras | `toda_letra_es_variable` |
| 　 | `true_latin` | Verdadera para las latinas; las griegas son otra cosa | `toda_letra_es_variable` |
| 　 | `false_never` | Falsa: ninguna letra representa cantidades que cambian | `sobregeneraliza_constantes` |

Escalera de pistas:
1. Para tumbar un «todo» basta UN contraejemplo.
2. Piensa en una letra que siempre valga lo mismo.
3. π vale 3,1416 hoy, mañana y en cualquier círculo.

**E6**

En el registro $4c+\pi-9$, selecciona TODOS los símbolos cuyo valor NO cambia.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $4$ | — |
| 　 | `b` | $c$ | — |
| ✅ | `c` | $\pi$ | — |
| ✅ | `d` | $-9$ | — |

Escalera de pistas:
1. Pregunta símbolo a símbolo: ¿puede tomar otro valor?
2. π es letra, pero su valor está fijado.
3. La única que depende del registro es la c.

**E7**

Una cuerda patrón mide 12 palmos. De ella se cortan t trozos de 2 palmos para marcar linderos. Si se cortan 5 trozos, ¿cuántos palmos quedan?

Respuesta: `2`

Escalera de pistas:
1. El 12 y el 2 no cambian; lo que cambia es t.
2. Lo cortado es 2 · 5 = 10.
3. 12 − 10 = …


### A9. Cierre

*¿Cambia o está fijado?* — **Qué decide que un símbolo sea constante**

El aspecto no decide nada. Lo único que importa es si alguien puede darle otro valor sin romper el registro.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Constante evidente: es el caso fácil, y por eso engaña poco. |
|  | ✗ | Letra y constante a la vez. Es el caso que desarma la trampa. |
|  | ✗ | Constante, aunque esté pegado a una variable. No es término constante: acompaña. |
|  | ✅ | Cambia con cada pedido. La única del registro que se mueve. |
|  | ✗ | Nació como letra libre y quedó sellada. A partir de ahí, constante. |
|  | ~ (ámbar) | Constante DENTRO de un problema, pero cambia de un problema a otro. Ni fijo del todo ni variable. |

La última fila es la honesta: hay símbolos quietos mientras dura el problema y que se mueven cuando cambias de problema. Se llaman parámetros, y por eso la pregunta útil no es «¿cambia?» sino «¿cambia AQUÍ?».

#### Pregunta de abstracción

¿Qué comparten los tres registros trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `mixed` | En los tres conviven cantidades fijas con al menos una que cambia | — |
| 　 | `not_shape` | En los tres el aspecto del símbolo no basta para clasificarlo | — |
| 　 | `letters_vary` | En los tres todas las letras representan cantidades que cambian | — |
| 　 | `digits_fixed` | En los tres solo las cifras están fijas | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas medidas de barro hacen falta?
¿Cuántas medidas de barro hacen falta?

Respuesta: `37`

Escalera de pistas:
1. Separa lo que depende del número de sellos de lo que no.
2. 3s + 4, con s = 11.
3. 33 + 4 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otras medidas. Sin nota.

- **Mejoró:** Avance: ya decides por lo que representa el símbolo, no por su aspecto.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué una letra puede estar fijada.

**PD1**

Un peso patrón vale 4 medidas. ¿Cuánto pesan 8 de esos patrones?

Respuesta: `32`

**PD2**

En $3y+11$, ¿cuál es el coeficiente?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three` | 3 | — |
| 　 | `eleven` | 11 | `confunde_coeficiente_con_constante` |
| 　 | `y` | y | `confunde_coeficiente_con_variable` |

**PD3**

¿Cuál de estos símbolos NO cambia nunca de valor?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `pi` | $\pi$ | — |
| 　 | `x` | la $x$ de $2x+1$ | `toda_letra_es_variable` |
| 　 | `r` | la $r$ de $2\pi r$ | `toda_letra_es_variable` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-L02-CONSTANTES-D2` | `six` | `confunde_coeficiente_con_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-D2` | `both` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-D3` | `no` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-D3` | `only_greek` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E1` | `eight` | `confunde_coeficiente_con_constante` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E1` | `p` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E1` | `three` | `pierde_el_signo_del_termino` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E3` | `variable` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E3` | `unknown` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E3` | `area` | `confunde_simbolo_con_resultado` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E4` | `not_constant` | `confunde_coeficiente_con_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E4` | `count` | `cuenta_simbolos_no_terminos` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E4` | `none` | `confunde_coeficiente_con_constante` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E5` | `true` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E5` | `true_latin` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-E5` | `false_never` | `sobregeneraliza_constantes` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-PD2` | `eleven` | `confunde_coeficiente_con_constante` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-PD2` | `y` | `confunde_coeficiente_con_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-PD3` | `x` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |
| `ALG-N1-L02-CONSTANTES-PD3` | `r` | `toda_letra_es_variable` | No mires si es letra o cifra: pregunta si su valor puede cambiar aquí. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
