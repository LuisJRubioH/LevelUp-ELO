# Nodo: La fracción es una división — PREALG-N1-B06-RACIONALES-FRACCION-DIVISION

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION` |
| `concept_slug` | `racionales` |
| Error focal | `decimal_truncado_es_el_numero` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B05-ENTEROS-DEUDA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Tercer peldaño · Racionales

**Título:** La fracción es una división

Ya sabes contar y ya sabes deber. Falta repartir. Aquí vas a escribir un reparto como fracción, convertirlo en decimal dividiendo, y decidir cuándo un decimal dice exactamente lo mismo que la fracción y cuándo solo se le parece.

**Escena:** Los racionales son cocientes de enteros con denominador distinto de cero

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

¿Cuál de estos dos números es menor?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `neg3` | -3 | — |
| 　 | `neg_half` | -1/2 | `magnitud_sin_signo` |
| 　 | `equal` | Son iguales | `no_compara_entero_con_fraccion` |

**D2**

$18\div4$ no da un número entero. ¿Cuánto sobra?

Respuesta: `2`

**D3**

Tres botellas iguales se reparten entre cuatro personas. ¿Cuánta botella recibe cada una?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three_fourths` | tres cuartos de botella | — |
| 　 | `four_thirds` | cuatro tercios de botella | `invierte_cociente` |
| 　 | `not_enough` | No alcanza: sobra 1 | `reparto_solo_entero` |
| 　 | `one_and_left` | Cada una 1 y sobra | `reparto_solo_entero` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · El puente que se mueve* — **La cuerda de Pitágoras**

Pitágoras tenía una tabla con una sola cuerda tensada y un puente que podía deslizar. Con la cuerda entera sonaba una nota. Con el puente justo en la mitad sonaba la misma nota, más aguda. Y con el puente en 2 de cada 3 partes salía la nota que a él le parecía la más hermosa de todas.

Dos de cada tres partes. Pero el taller solo tenía reglas marcadas en décimas, y ahí empieza el problema.

**Pregunta:** ¿Qué número debía marcar Pitágoras en su regla para dejar el puente exactamente donde suena esa nota?

**Intento genuino** (`acotado`): Escoge la que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` |  | — |
| 　 | `b` |  | — |
| 　 | `c` | Ninguno de los dos: solo 2/3 lo dice exacto | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos repartos, dos finales distintos**

Mira los dos casos de abajo. Los dos son un reparto que no da entero, pero terminan de forma distinta: uno cierra y el otro no cierra nunca.

- **Caso que funciona** — La división termina. El punto cae justo sobre una marca de la recta.
- **Caso que rompe la expectativa** — La división no termina. El punto cae entre marcas, siempre.

**Resolución:** ¿Y entonces 5/9 no es un número? Sí lo es, y es exacto. Lo que no termina es el intento de escribirlo en decimales. La fracción ya lo dice completo; el decimal es un retrato que a veces no cabe en la hoja.

**Definición — Los números racionales**

$$\mathbb{Q}=\left\{\dfrac{a}{b}\ :\ a,b\in\mathbb{Z},\ b\neq 0\right\}$$

La frase del nodo: a/b ES a÷b. No «se parece a», no «se puede convertir en». Es.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\mathbb{Q}` | los racionales | de quotient, cociente: el conjunto de los cocientes |
| `a` | numerador | cuánto se reparte (el dividendo) |
| `b` | denominador | entre cuántos se reparte (el divisor) |
| `\dfrac{\ \ }{\ \ }` | dividido entre | la barra no es un adorno: es el signo de dividir |
| `a,b\in\mathbb{Z}` | a y b son enteros | arriba y abajo pueden ser negativos (viene de B05) |
| `b\neq 0` | b distinto de cero | repartir entre cero baldes no es un reparto |

### A5. Ejemplos resueltos

#### La miel de la despensa · *resuelto*

En la despensa de la escuela quedan 15 medidas de miel y hay que pasarlas a 6 tarros iguales. ¿Cuánta miel lleva cada tarro?

- El reparto es 15 entre 6 → 15/6. Arriba la miel, abajo entre cuántos tarros.
- La barra es dividir, así que calculo 15÷6. Es la definición, aplicada.
- 6 × 2 = 12, sobran 3. El entero cabe 2 veces.
- Las 3 medidas que sobran también se reparten entre los 6 tarros → 0,5.
- 15/6 = 2,5. Cada tarro lleva 2,5 medidas: la división terminó y el decimal es exacto.

**Autoexplicación (focal):** {'step_index': 3, 'prompt': 'En el paso 4 el 3 que sobra se vuelve 0,5. ¿Por qué 0,5 y no 3?'}

#### El huerto de la escuela · *resuelto*

El huerto de la escuela tiene 5 parcelas iguales y hay 9 discípulos encargados de cuidarlo. ¿Cuánto huerto cuida cada uno?

- 5 parcelas entre 9 discípulos → 5/9.
- 5÷9: pongo 5,000… y divido, porque la barra es dividir.
- 0,5 y resto 5. 0,55 y resto 5. 0,555 y resto 5: el resto se repite, nunca va a terminar.
- Escribo 0,5 con barra encima: la barra marca lo que se repite para siempre.
- 5/9 = 0,5̄. Las dos escrituras son exactas; la fracción es la más corta.

#### El decimal que se cortó · *TRAMPA*

Un discípulo midió el lado del patio y anotó esto en su tablilla. Está mal: «La medida da 25/7 varas. Dividí y me salió 3,57142. Entonces 25/7 = 3,57142».

- Divide 25÷7 y no te detengas en la quinta cifra.
- Observa que los restos empiezan a repetirse: el bloque 571428 vuelve a salir.
- Un decimal cortado siempre queda por debajo del valor real.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{25}{7}=3{,}57142', 'right_latex': '\\dfrac{25}{7}=3{,}\\overline{571428}', 'rows': [{'wrong': 'El decimal se cortó donde se acabó la paciencia', 'right': 'El bloque 571428 se repite para siempre'}, {'wrong': '3,57142 es menor que 25/7', 'right': 'La única escritura corta y exacta es 25/7'}]}
**¿Por qué falla?:** ¿Por qué 3,57142 no es 25/7? Escribe la igualdad corregida.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el procedimiento ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — Traen 32 medidas de agua de la fuente y hay que llenar 5 tinajas iguales.

- dado: $\dfrac{32}{5}=32\div5$
- dado: $5\times6=30,\ \text{sobran }2$
- dado: $2\div5=0{,}4$
- hueco `P1-b1`: $\dfrac{32}{5}=$ → `6,4`

**P2** (*falta: middle*) — Ahora son 69 espuertas de arena para nivelar 5 tramos iguales del patio.

- dado: $\dfrac{69}{5}=69\div5$
- hueco `P2-b1`: $5\times\square=65\ \Rightarrow\ \square=$ → `13`
- hueco `P2-b2`: $4\div5=$ → `0,8`
- hueco `P2-b3`: $\dfrac{69}{5}=$ → `13,8`

**P3** (*falta: statement_only*) — Solo el planteamiento: la sombra del gnomon mide 12 dedos y hay que partirla en 7 tramos iguales. Da el resultado y decide qué escritura cabría en una marca de 6 caracteres.

- hueco `P3-b1`: $\text{Parte entera de }\dfrac{12}{7}=$ → `1`


### A7. Comparación de métodos

**Dos caminos para el mismo decimal**

¿Cuánto vale $\dfrac{7}{8}$ en decimal? Las dos soluciones de abajo son correctas.

- **Método 1 · Dividir** — 
- **Método 2 · Amplificar a denominador $10^n$** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si intentas el método 2 con 5/9?

**Insight:** El segundo método falla con 5/9, y ese fracaso es el contenido: solo los denominadores que se factorizan en 2 y 5 llegan a una potencia de 10; los demás son periódicos. Lo vas a volver a ver en factorización prima (N4-C04).

### A8. Práctica independiente (7 ítems)

**E1**

Se reparten 3 medidas de vino en 4 copas iguales. ¿Cuánto lleva cada copa?

Respuesta: `0,75`

Escalera de pistas:
1. ¿Qué cantidad se está repartiendo?
2. Arriba lo que se reparte, abajo entre cuántos: la barra es el signo de dividir.
3. 3÷4: 4×0,7=2,8, faltan 0,2…

**E2**

Hay 32 codos de lino para repartir entre 5 telares. ¿Cuántos codos por telar?

Respuesta: `6,4`

Escalera de pistas:
1. ¿Cabe 5 en 32 un número exacto de veces?
2. Sobran 2; reparte esos 2 entre 5.
3. 32 = 5×6 + 2, y 2÷5 = 0,4.

**E3**

Ordena de mayor a menor: 8/6, 2/3, 4/6, 1/2. ¿Cuál es el orden correcto?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | 8/6 · 2/3 = 4/6 · 1/2 | — |
| 　 | `half_first` | 1/2 primero | `mayor_denominador_mayor_numero` |
| 　 | `split_equiv` | 2/3 y 4/6 en puestos distintos | `no_reconoce_equivalentes` |
| 　 | `by_numerator` | Por el numerador | `no_reconoce_equivalentes` |

Escalera de pistas:
1. Si no puedes compararlas de un vistazo, ¿en qué otra forma sabes escribirlas?
2. Convierte todas a decimal.
3. 8÷6 = 1,3̄; sigue con las demás.

**E4**

Teano revisa la tablilla de otro discípulo y lee «69/5 = 12,25». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `division` | Dividió mal: 5×12=60 y le sobran 9, no 1 | — |
| 　 | `truncated` | Cortó el decimal antes de tiempo | `confunde_error_con_truncamiento` |
| 　 | `inverted` | Puso la fracción al revés | `invierte_cociente` |
| 　 | `none` | Ningún error, está bien | `habito_valida_sin_verificar` |

Escalera de pistas:
1. ¿Cuántas veces cabe 5 en 69?
2. 13 veces y sobran 4.
3. 4÷5 = 0,8, entonces el resultado es 13,8.

**E5**

¿Es verdadera o falsa? $\dfrac{10}{3}=3{,}333$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_cut` | Falsa: 3,333 está cortado, el exacto es 3,3̄ | — |
| 　 | `true_same` | Verdadera, es lo mismo | `decimal_truncado_es_el_numero` |
| 　 | `false_nodecimal` | Falsa: 10/3 no tiene decimal | `periodico_no_es_numero` |
| 　 | `false_03` | Falsa: da 0,3 | `invierte_cociente` |

Escalera de pistas:
1. Multiplica el decimal por 3. ¿Vuelve a darte 10?
2. Un decimal que se corta siempre queda por debajo del valor real.
3. 10÷3 = 3,3333… sin final; se escribe 3,3̄.

**E6**

El cantero debe tallar una losa de 4/9 de codo, pero su regla solo llega a dos decimales y marca 0,44. ¿La losa le va a quedar bien?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `short` | No: 4/9 = 0,4̄; queda un poco corta | — |
| 　 | `exact` | Sí, 0,44 es exactamente 4/9 | `decimal_truncado_es_el_numero` |
| 　 | `long` | No: queda un poco larga | `direccion_del_truncamiento` |
| 　 | `unknown` | No se puede saber sin más datos | `habito_evita_decidir` |

Escalera de pistas:
1. ¿0,44 y 0,4444… son el mismo número?
2. Divide 4÷9 y mira si se detiene.
3. 0,44 < 0,4̄: falta material.

**E7**

¿Cuál de estas fracciones da un decimal que TERMINA?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three_eighths` | 3/8 | — |
| 　 | `two_sevenths` | 2/7 | `denominador_no_2_ni_5` |
| 　 | `five_sixths` | 5/6 | `denominador_no_2_ni_5` |
| 　 | `one_ninth` | 1/9 | `denominador_no_2_ni_5` |

Escalera de pistas:
1. Prueba a llevar cada denominador a 10, 100 o 1000.
2. 8 × 125 = 1000. ¿Y el 7?
3. Solo terminan las que se factorizan con 2 y 5 (lo verás en N4-C04).


### A9. Cierre

*La escalera de la necesidad* — **¿Toda división de dos números del conjunto vive en el conjunto?**

Cada peldaño nació de una operación que no cabía en el anterior.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Se sale: no hay natural que valga. |
|  | ✗ | Sigue sin caber; los negativos no ayudaron. |
|  | ✅ | El conjunto se hizo para esto (mientras b ≠ 0). |

Igual que ℤ nació de una resta que no cabía (B05). El siguiente peldaño (B07) va a nacer de algo que NINGUNA fracción puede escribir.

#### Pregunta de abstracción

¿Qué estructura comparten los tres problemas de este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `division` | Los tres son una división de enteros | — |
| 　 | `periodic` | Los tres tienen decimal periódico | — |
| 　 | `improper` | Los tres tienen numerador mayor que el denominador | — |
| 　 | `sharing` | Los tres son un reparto que no da entero | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Qué número marcas en la regla?
¿Qué número marcas en la regla?

Respuesta: `1,1667`

Escalera de pistas:
1. Primero convierte la fracción a decimal.
2. 7÷6 no termina: 1,1666…
3. Redondea a 4 decimales: la quinta cifra es 6, así que la cuarta sube.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre el decimal exacto y el decimal cortado.

**PD1**

¿Cuál es menor?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `neg2` | -2 | — |
| 　 | `neg_quarter` | -1/4 | `magnitud_sin_signo` |
| 　 | `equal` | Son iguales | — |

**PD2**

$23\div4$ no da entero. ¿Cómo escribes el resultado exacto?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | 23/4 | — |
| 　 | `inverted` | 4/23 | `invierte_cociente` |
| 　 | `remainder` | 5 y sobra 3 | `reparto_solo_entero` |
| 　 | `cannot` | No se puede escribir exacto | `reparto_solo_entero` |

**PD3**

¿Es verdadera? $\dfrac{10}{3}=3{,}\overline{3}$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `periodico_no_es_numero` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-D1` | `neg_half` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-D1` | `equal` | `no_compara_entero_con_fraccion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-D3` | `four_thirds` | `invierte_cociente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-D3` | `not_enough` | `reparto_solo_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-D3` | `one_and_left` | `reparto_solo_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E3` | `half_first` | `mayor_denominador_mayor_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E3` | `split_equiv` | `no_reconoce_equivalentes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E3` | `by_numerator` | `no_reconoce_equivalentes` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E4` | `truncated` | `confunde_error_con_truncamiento` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E4` | `inverted` | `invierte_cociente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E4` | `none` | `habito_valida_sin_verificar` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E5` | `true_same` | `decimal_truncado_es_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E5` | `false_nodecimal` | `periodico_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E5` | `false_03` | `invierte_cociente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E6` | `exact` | `decimal_truncado_es_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E6` | `long` | `direccion_del_truncamiento` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E6` | `unknown` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E7` | `two_sevenths` | `denominador_no_2_ni_5` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E7` | `five_sixths` | `denominador_no_2_ni_5` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-E7` | `one_ninth` | `denominador_no_2_ni_5` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-PD1` | `neg_quarter` | `magnitud_sin_signo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-PD2` | `inverted` | `invierte_cociente` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-PD2` | `remainder` | `reparto_solo_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-PD2` | `cannot` | `reparto_solo_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B06-RACIONALES-FRACCION-DIVISION-PD3` | `false` | `periodico_no_es_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b06-racionales-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
