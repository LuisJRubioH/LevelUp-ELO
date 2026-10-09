# Nodo: Juntar no siempre agranda — PREALG-N2-E01-SUMA-JUNTAR

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N2-E01-SUMA-JUNTAR` |
| `concept_slug` | `suma` |
| Error focal | `sumar_siempre_agranda` |
| Sala / edificio | El Granero Público |
| Guía | KatIA |
| Entra después de | `PREALG-N2-E00-CIUDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El Granero Público · Suma

**Título:** Juntar no siempre agranda

Sumar es juntar. Eso lo sabes desde que contabas con los dedos. Lo que vas a decidir hoy es qué pasa cuando lo que juntas apunta hacia el otro lado, y hasta dónde llega la suma cuando los números dejan de ser enteros.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el granero. No hay nota; me dicen por dónde entrarle.

**D1**

Hay 14 medidas de trigo en el granero y entran 9 más. ¿Cuántas quedan?

Respuesta: `23`

**D2**

¿Cuánto vale $7+(-4)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three` | 3 | — |
| 　 | `eleven` | 11 | `ignora_el_signo_al_sumar` |
| 　 | `minus_eleven` | -11 | `ignora_el_signo_al_sumar` |
| 　 | `cannot` | No se puede sumar un negativo | `sumar_solo_con_positivos` |

**D3**

Si a un número le sumas otro número, ¿el resultado siempre es mayor que el primero?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `always` | Sí, siempre | `sumar_siempre_agranda` |
| ✅ | `depends` | Depende de qué número sumes | — |
| 　 | `never` | No, nunca | `sumar_siempre_achica` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Dentro del Granero Público* — **La tablilla de las dos columnas**

El primer edificio de la ciudad es el Granero Público: dos pisos de sacos, una balanza de suelo y, junto a la puerta, la tablilla donde el escriba anota todo lo que entra y todo lo que sale. Durante años usó dos columnas: en una las carretas que llegaban, en otra los sacos que salían. Al cerrar el mes contaba cada columna aparte y restaba.

Este mes entró un escriba nuevo y dijo que sobraba una columna. Que una salida también se puede sumar, si se anota con signo.

**Pregunta:** Si sumas una salida, ¿la cuenta del granero crece o se achica?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Crece: sumar siempre agranda | — |
| 　 | `b` | Se achica: una salida quita | — |
| 　 | `c` | Depende del signo de lo que sumes | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos sumas, dos direcciones**

Las dos filas de abajo son sumas. Fíjate en qué le pasa al número de partida en cada una.

- **Caso que confirma lo que esperas** — El resultado quedó por encima del punto de partida.
- **Caso que rompe la expectativa** — También es una suma, y el resultado quedó por debajo.

**Resolución:** Las dos operaciones son sumas: en las dos junté lo que había con lo que llegó. Lo que cambió no fue la operación, fue la dirección de lo que se juntó. «Sumar agranda» solo vale mientras todo apunte hacia el mismo lado.

**Definición — La suma**

$$a+b=c,\qquad a,b,c\in\mathbb{R}$$

Sumar es juntar dos cantidades en una sola. El signo de cada sumando dice hacia qué lado apunta; el resultado se llama suma o total.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a,b` | sumandos | las dos cantidades que se juntan |
| `+` | más | la orden de juntar, no la de agrandar |
| `c` | suma o total | el resultado de juntarlas |
| `-b` | sumando negativo | algo que apunta al lado contrario (viene de B05) |
| `a+0=a` | sumar cero deja igual | el neutro de la suma; lo formaliza N3-M04 |

### A5. Ejemplos resueltos

#### El mes del granero en una sola columna · *resuelto*

En el mes entraron 120 medidas de trigo y salieron 145. El escriba nuevo quiere una sola cuenta. ¿Cómo queda el granero respecto a como empezó?

- Entrada: +120. Salida: −145. Las dos van a la misma columna, con su signo.
- Sumo: 120 + (−145).
- Como apuntan a lados contrarios, se cancelan hasta donde alcanza el menor: 120 con 120.
- Del −145 sobran 25 sin cancelar, y apuntan hacia abajo: −25.
- 120 + (−145) = −25: el granero terminó 25 medidas por debajo de como empezó.

**Autoexplicación (focal):** {'step_index': 3, 'prompt': 'En el paso 4 sobran 25 y el resultado sale negativo. ¿Por qué negativo y no 25 a secas?'}

#### Cuando la carreta no viene llena · *resuelto*

En el granero hay 3/4 de medida de cebada y llega otro 1/2 de medida. ¿Cuánta cebada queda?

- No puedo juntar cuartos con medios directamente: son partes de distinto tamaño.
- Llevo las dos al mismo tamaño de parte: 1/2 = 2/4.
- Ahora sí: 3/4 + 2/4. Junto los numeradores y dejo el denominador.
- 3 + 2 = 5, entonces 5/4.
- 5/4 = 1,25 medidas: la suma cierra dentro de los racionales.

#### El escriba que sumó de más · *TRAMPA*

Un aprendiz cierra la tablilla así: «Había 60 medidas, sumé una salida de 18 y me dio 78. Sumar agranda, así que va bien».

- Compara: 60 + 18 = 78 y 60 + (−18) = 42. Solo cambió un signo.
- El −18 apunta al lado contrario del 60: cancela 18 de esos 60.
- Quedan 42. El resultado de sumar un negativo está POR DEBAJO del punto de partida.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '60+(-18)=78', 'right_latex': '60+(-18)=42', 'rows': [{'wrong': 'El signo del sumando se puede ignorar', 'right': 'El signo es parte del número que se junta'}, {'wrong': 'Sumar siempre da un resultado mayor', 'right': 'Sumar un negativo da un resultado menor'}]}
**¿Por qué falla?:** ¿Por qué 78 no puede ser la respuesta? Escribe la igualdad corregida.


### A6. Puente — parcialmente resueltos

Ahora tú, pero el procedimiento ya está empezado: solo faltan huecos.

**P1** (*falta: last*) — El granero registra +85 de entrada y −37 de salida en el mismo día.

- dado: $85+(-37)$
- dado: $\text{apuntan a lados contrarios: se cancelan 37}$
- hueco `P1-b1`: $85+(-37)=$ → `48`

**P2** (*falta: middle*) — Otro día: entran 2/5 de medida de mijo y luego 1/5 más.

- dado: $\dfrac{2}{5}+\dfrac{1}{5}$
- hueco `P2-b1`: $\text{numerador de la suma}=$ → `3`
- hueco `P2-b2`: $\dfrac{3}{5}\text{ en decimal}=$ → `0,6`

**P3** (*falta: statement_only*) — Solo el planteamiento: el granero arranca en −18 medidas (debe trigo) y entran tres carretas de 7 medidas cada una. ¿En cuánto termina?

- hueco `P3-b1`: $-18+7+7+7=$ → `3`


### A7. Comparación de métodos

**Dos caminos para la misma suma**

¿Cuánto vale $-14+9+14$? Las dos soluciones de abajo son correctas.

- **Método 1 · De izquierda a derecha** — 
- **Método 2 · Reagrupar primero lo que se cancela** — 

**Pregunta:** ¿Cuál conviene aquí? ¿Y qué propiedad de la suma te permitió mover el 14 de sitio en el método 2?

**Insight:** El método 2 solo es legal porque la suma es conmutativa y asociativa: puedes reordenar y reagrupar sin cambiar el resultado. Eso es exactamente lo que se formaliza en N3 (M01 y M02). Con la resta ese permiso desaparece — lo ves en el nodo siguiente.

### A8. Práctica independiente (7 ítems)

**E1**

En el silo del granero hay 46 sacos y descargan 28 más. ¿Cuántos sacos hay?

Respuesta: `74`

Escalera de pistas:
1. Las dos cantidades apuntan al mismo lado.
2. Junta las dos: 46 + 28.
3. 46 + 20 = 66, y 66 + 8 = …

**E2**

El silo del fondo abre el día debiendo 9 medidas y le descargan 15. ¿Cómo queda?

Respuesta: `6`

Escalera de pistas:
1. Los dos números apuntan a lados contrarios.
2. Se cancelan hasta donde alcanza el menor: 9 con 9.
3. Del 15 sobran 6, y apuntan hacia arriba.

**E3**

La balanza del granero pesa 1/4 de medida de mijo y le añaden 2/4 más. ¿Cuánto marca? (decimal)

Respuesta: `0,75`

Escalera de pistas:
1. Las partes ya son del mismo tamaño: cuartos con cuartos.
2. Junta los numeradores y deja el denominador: 3/4.
3. 3 ÷ 4 = …

**E4**

Un aprendiz escribe «-12 + 5 = -17». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `same_side` | Los sumó como si apuntaran al mismo lado; se cancelan y da -7 | — |
| 　 | `sign` | El resultado debía ser 17 positivo | `ignora_el_signo_al_sumar` |
| 　 | `order` | Cambió el orden de los sumandos | `resta_es_conmutativa` |
| 　 | `none` | Ningún error, está bien | `habito_valida_sin_verificar` |

Escalera de pistas:
1. ¿Los dos sumandos apuntan al mismo lado?
2. Uno es negativo y el otro positivo: se cancelan entre sí.
3. De −12 sobran 7 después de cancelar 5.

**E5**

¿Es verdadera o falsa? «Si $a$ y $b$ son números cualesquiera, entonces $a+b>a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_neg` | Falsa: si b es negativo, a+b queda por debajo de a | — |
| 　 | `true` | Verdadera: sumar siempre agranda | `sumar_siempre_agranda` |
| 　 | `false_always_less` | Falsa: a+b siempre es menor que a | `sumar_siempre_achica` |
| 　 | `depends_a` | Falsa: depende del signo de a, no del de b | `atribuye_direccion_al_primer_sumando` |

Escalera de pistas:
1. Para tumbar una afirmación «siempre» basta UN caso.
2. Prueba con a = 5 y b = −3.
3. 5 + (−3) = 2, y 2 no es mayor que 5.

**E6**

El granero abre el mes en 0. Entran 34 medidas, salen 51, entran 20. ¿Con cuántas medidas cierra el mes?

Respuesta: `3`

Escalera de pistas:
1. Todo va a una sola columna, cada movimiento con su signo.
2. 34 + (−51) = −17.
3. −17 + 20 = …

**E7**

¿En cuál de estos conjuntos la suma de dos elementos puede salirse del conjunto?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `irrationals` | Los irracionales | — |
| 　 | `naturals` | Los naturales | `confunde_cierre_de_suma_con_resta` |
| 　 | `integers` | Los enteros | `confunde_cierre_de_suma_con_resta` |
| 　 | `reals` | Los reales | `confunde_cierre_de_suma_con_resta` |

Escalera de pistas:
1. Busca dos números del conjunto cuya suma NO esté en el conjunto.
2. Prueba con $\sqrt{2}$ y $-\sqrt{2}$.
3. $\sqrt{2}+(-\sqrt{2})=0$, y 0 es racional, no irracional.


### A9. Cierre

*La escalera de la suma* — **¿La suma de dos elementos del conjunto vive en el conjunto?**

Un conjunto es cerrado bajo la suma si nunca te obliga a salirte de él.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Juntar dos cantidades de contar da otra cantidad de contar. |
|  | ✅ | Con signos también cierra: por eso la suma pudo tragarse la columna de salidas. |
|  | ✅ | Fracción más fracción da fracción. |
|  | ✗ | Dos irracionales pueden sumar un racional: el resultado SE SALE. Los irracionales no cierran bajo ninguna operación aritmética. |
|  | ✅ | La unión de racionales e irracionales (B08) sí cierra: por eso la suma vive cómoda en ℝ. |
|  | ✅ | También cierra. Desvío opcional (B09). |

La suma cierra desde el primer peldaño: nunca te obligó a inventar un conjunto nuevo. La operación siguiente, la resta, sí lo hace.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `join` | En los tres se juntan dos cantidades en una sola | — |
| 　 | `grow` | En los tres el resultado es mayor que el primer número | — |
| 　 | `sign` | En los tres el signo del sumando decide hacia dónde se mueve el resultado | — |
| 　 | `integers` | En los tres los números son enteros | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Con cuántas medidas cierra el granero?
¿Con cuántas medidas cierra el granero?

Respuesta: `31`

Escalera de pistas:
1. Escribe los cuatro movimientos con su signo antes de operar.
2. −40 + 96 = 56.
3. 56 − 33 = 23, y le falta sumar 8.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: hoy decides el resultado por el signo, no por la costumbre.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué le pasa a un número cuando le sumas algo negativo.

**PD1**

Hay 26 medidas en el granero y entran 17. ¿Cuántas quedan?

Respuesta: `43`

**PD2**

¿Cuánto vale $9+(-13)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `minus_four` | -4 | — |
| 　 | `four` | 4 | `ignora_el_signo_al_sumar` |
| 　 | `twenty_two` | 22 | `ignora_el_signo_al_sumar` |

**PD3**

¿Es verdadera? «Existen $a$ y $b$ tales que $a+b<a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `sumar_siempre_agranda` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N2-E01-SUMA-JUNTAR-D2` | `eleven` | `ignora_el_signo_al_sumar` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-D2` | `minus_eleven` | `ignora_el_signo_al_sumar` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-D2` | `cannot` | `sumar_solo_con_positivos` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-D3` | `always` | `sumar_siempre_agranda` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-D3` | `never` | `sumar_siempre_achica` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E4` | `sign` | `ignora_el_signo_al_sumar` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E4` | `order` | `resta_es_conmutativa` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E4` | `none` | `habito_valida_sin_verificar` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E5` | `true` | `sumar_siempre_agranda` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E5` | `false_always_less` | `sumar_siempre_achica` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E5` | `depends_a` | `atribuye_direccion_al_primer_sumando` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E7` | `naturals` | `confunde_cierre_de_suma_con_resta` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E7` | `integers` | `confunde_cierre_de_suma_con_resta` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-E7` | `reals` | `confunde_cierre_de_suma_con_resta` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-PD2` | `four` | `ignora_el_signo_al_sumar` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-PD2` | `twenty_two` | `ignora_el_signo_al_sumar` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |
| `PREALG-N2-E01-SUMA-JUNTAR-PD3` | `false` | `sumar_siempre_agranda` | Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/02-prealg-n2-mercado/e01-suma-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
