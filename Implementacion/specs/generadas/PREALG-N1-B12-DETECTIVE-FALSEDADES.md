# Nodo: Dar vuelta una frase no la conserva — PREALG-N1-B12-DETECTIVE-FALSEDADES

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B12-DETECTIVE-FALSEDADES` |
| `concept_slug` | `detective` |
| Error focal | `error_del_reciproco` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B11-CLASIFICADOR-RIGUROSO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Consolidación · Detective

**Título:** Dar vuelta una frase no la conserva

Ya sabes clasificar. Ahora vas a juzgar afirmaciones: decidir si una frase sobre conjuntos es verdadera o falsa, y —esto es lo nuevo— demostrarlo. Vas a descubrir que para tumbar una afirmación basta UN ejemplo, y que la trampa más común de todas es leer una frase al revés.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

«Todo entero es racional». ¿Verdadera o falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `no_reconoce_inclusion` |

**D2**

«Todo racional es entero». ¿Verdadera o falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa | — |
| 　 | `true` | Verdadera | `error_del_reciproco` |

**D3**

Para demostrar que «todo número par es mayor que 10» es falsa, ¿qué basta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `one` | Un solo ejemplo que la incumpla, como el 4 | — |
| 　 | `many` | Muchos ejemplos que la incumplan | `necesita_muchos_contraejemplos` |
| 　 | `all` | Revisar todos los números pares | `exige_verificacion_exhaustiva` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Consolidación* — **El sofista en el pórtico**

Un sofista cobra por enseñar a ganar discusiones. Hoy tiene público y suelta esto: «Todos los que estudian en la escuela de Pitágoras saben geometría. Por lo tanto, todos los que saben geometría estudian en la escuela de Pitágoras».

La gente asiente. Suena bien: las dos frases usan las mismas palabras y parecen decir lo mismo. Al fondo, un cantero que aprendió geometría solo, midiendo piedras, no dice nada.

**Pregunta:** ¿La segunda frase se sigue de la primera? Y si no: ¿qué basta para tumbarla?

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí se sigue: dicen lo mismo con otro orden | — |
| 　 | `b` | No se sigue, y el cantero del fondo lo prueba | — |
| 　 | `c` | No se puede decidir sin conocer a toda la gente | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **La misma frase, dada vuelta**

Las dos afirmaciones de abajo usan exactamente las mismas dos palabras. Solo cambia el orden. Una es verdadera y la otra es falsa.

- **Verdadera** — Cualquier entero se escribe sobre 1, así que sí: no hay ni un entero que se escape de ℚ.
- **Falsa** — Basta 1/2 para tumbarla. Un solo caso que la incumpla y la afirmación cae entera.

**Resolución:** «Todo A es B» NO es lo mismo que «todo B es A». La primera dice que A está dentro de B; la segunda diría que B está dentro de A, que es otra cosa. Y fíjate en la asimetría de la prueba: para sostener «todo A es B» hay que revisarlos todos, pero para tumbarla basta UNO solo que falle. Ese uno se llama contraejemplo, y es el arma del detective.

**Definición — Afirmación, recíproco y contraejemplo**

$$\text{«todo }A\text{ es }B\text{»}\ \equiv\ A\subset B\qquad\not\equiv\qquad B\subset A$$

La frase del nodo: para tumbar una afirmación universal basta un contraejemplo. Para sostenerla no basta ningún número de ejemplos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `A\subset B` | A contenido en B | «todo A es B»: la afirmación original |
| `B\subset A` | B contenido en A | «todo B es A»: el recíproco, que es OTRA afirmación |
| `\not\subset` | no está contenido | existe al menos un elemento que se escapa |
| `\exists` | existe | con uno alcanza: la marca del contraejemplo |
| `\forall` | para todo | sin excepciones: lo que afirma una frase universal |
| `\tfrac{1}{2}\notin\mathbb{Z}` | un medio no es entero | el contraejemplo que tumba «todo racional es entero» |

### A5. Ejemplos resueltos

#### «Todo real es racional» · *resuelto*

Decide si la afirmación «todo número real es racional» es verdadera o falsa, y demuéstralo.

- La afirmación es universal: dice que NINGÚN real se escapa de ℚ.
- Para tumbarla no necesito revisarlos todos: me basta encontrar uno que falle.
- Busco un real que no sea racional. √2 es real (está en la recta).
- ¿Es racional? No: se demostró en B07 que no existe fracción que lo dé.
- √2 es real y no es racional. Un contraejemplo, y la afirmación es FALSA.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': 'En el paso 2 dije que no hacía falta revisarlos todos. ¿Por qué un solo caso alcanza para tumbar la frase, si son infinitos números?'}

#### «Todo natural es racional» · *resuelto*

Decide si la afirmación «todo número natural es racional» es verdadera o falsa, y demuéstralo.

- Busco un contraejemplo: un natural que no sea racional. Pruebo 7, 0, 100…
- No encuentro ninguno, pero eso no demuestra nada: podrían faltarme casos.
- Cambio de estrategia: en vez de ejemplos, uso la definición.
- Un racional es a/b con a, b enteros y b ≠ 0. Cualquier natural n se escribe n/1.
- n/1 cumple la definición para TODO n. Por eso la afirmación es VERDADERA.

#### La frase leída al revés · *TRAMPA*

Un discípulo razonó así. Está mal: «En clase probamos que todo entero es racional. Entonces también es cierto que todo racional es entero: es la misma frase, solo cambié el orden».

- Escribe las dos frases una debajo de la otra y subraya qué conjunto va primero.
- La primera dice ℤ está dentro de ℚ. La segunda diría ℚ está dentro de ℤ.
- Busca un racional que no sea entero: con uno solo alcanza.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\text{todo entero es racional}\\ \\Rightarrow\\ \\text{todo racional es entero}', 'right_latex': '\\mathbb{Z}\\subset\\mathbb{Q}\\ \\text{ es V};\\quad \\mathbb{Q}\\subset\\mathbb{Z}\\ \\text{ es F, porque }\\tfrac{1}{2}\\in\\mathbb{Q}\\setminus\\mathbb{Z}', 'rows': [{'wrong': 'Cambiar el orden no cambia la frase', 'right': 'Cambiar el orden produce el recíproco, que es otra afirmación'}, {'wrong': 'Si una es verdadera, la otra también', 'right': '1/2 es racional y no es entero: la recíproca es falsa'}]}
**¿Por qué falla?:** ¿Por qué el recíproco no se sigue de la afirmación original? Da el contraejemplo que lo tumba.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el juicio ya está empezado y solo faltan huecos. Responde 1 si la afirmación es verdadera y 0 si es falsa.

**P1** (*falta: last*) — «Todo natural es entero». ¿Verdadera (1) o falsa (0)?

- dado: $\mathbb{N}\subset\mathbb{Z}\ \text{es la cadena de inclusión}$
- hueco `P1-b1`: $\text{Respuesta (1=V, 0=F)}=$ → `1`

**P2** (*falta: middle*) — «Todo entero es natural» y «todo irracional es real». Juzga las dos.

- dado: $\text{Contraejemplo para la primera}:\ -3$
- hueco `P2-b1`: $\text{«Todo entero es natural» (1=V, 0=F)}=$ → `0`
- hueco `P2-b2`: $\text{«Todo irracional es real» (1=V, 0=F)}=$ → `1`

**P3** (*falta: statement_only*) — Solo el planteamiento: «Ningún racional es irracional». ¿Verdadera (1) o falsa (0)? Cuidado: esta afirmación no es del mismo tipo que las anteriores.

- hueco `P3-b1`: $\text{Respuesta (1=V, 0=F)}=$ → `1`


### A7. Comparación de métodos

**Dos formas de juzgar una afirmación**

¿Es verdadera «todo racional es real»? Las dos soluciones son correctas.

- **Método 1 · Buscar contraejemplo** — 
- **Método 2 · Usar la definición** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: si buscas contraejemplos durante una hora y no encuentras ninguno, ¿ya probaste la afirmación?

**Insight:** No. Ese es el punto asimétrico de todo el nodo: un contraejemplo tumba, pero mil ejemplos no sostienen. Para afirmar «todo A es B» hay que argumentar desde la definición, como en el ejemplo 2. Buscar contraejemplos sirve para sospechar, no para concluir.

### A8. Práctica independiente (7 ítems)

**E1**

«Todo número natural es real». ¿Verdadera o falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera: ℕ ⊂ ℝ | — |
| 　 | `false` | Falsa | `no_reconoce_inclusion` |
| 　 | `cannot` | No se puede decidir | `habito_evita_decidir` |

Escalera de pistas:
1. ¿Puedes ubicar el 7 en la recta numérica?
2. Sí, y todo lo que está en la recta es real.
3. ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ: la cadena lo garantiza para todos.

**E2**

«Todo número real es natural». ¿Verdadera o falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: −3 es real y no es natural | — |
| 　 | `true` | Verdadera: es la misma frase de antes | `error_del_reciproco` |
| 　 | `cannot` | No se puede decidir | `habito_evita_decidir` |

Escalera de pistas:
1. Es la frase anterior dada vuelta: hay que juzgarla de nuevo.
2. Busca un real que no sea natural.
3. −3 o 0,5 sirven: los dos son reales y ninguno es natural.

**E3**

¿Cuál de estos contraejemplos tumba «todo número racional es positivo»?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `neg_frac` | −1/2, que es racional y negativo | — |
| 　 | `sqrt2` | √2, que no es racional | `contraejemplo_fuera_del_conjunto` |
| 　 | `zero` | 0, que no es racional | `cero_no_es_racional` |
| 　 | `five` | 5, que es racional y positivo | `confunde_ejemplo_con_contraejemplo` |

Escalera de pistas:
1. Un contraejemplo debe CUMPLIR la hipótesis y FALLAR la conclusión.
2. Aquí: tiene que ser racional (hipótesis) y no positivo (falla la conclusión).
3. √2 no sirve porque ni siquiera es racional: no cumple la hipótesis.

**E4**

Un discípulo argumentó: «Probé con 4, con 16 y con 100, y en los tres casos la raíz dio un natural. Entonces la raíz de todo natural es un natural». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `examples` | Tres ejemplos no prueban una afirmación universal; √2 la tumba | — |
| 　 | `wrong_roots` | Calculó mal alguna de las tres raíces | `duda_del_calculo_correcto` |
| 　 | `reciprocal` | Confundió la afirmación con su recíproca | `confunde_tipo_de_error` |
| 　 | `none` | Ningún error: los tres casos lo confirman | `ejemplos_prueban_universal` |

Escalera de pistas:
1. Las tres raíces están bien calculadas: 2, 4 y 10.
2. El problema es el salto de «tres casos» a «todos los casos».
3. √2 es raíz de un natural y no es natural: la afirmación es falsa.

**E5**

«Todo irracional es real» es verdadera. ¿Se sigue de ahí que «todo real es irracional»?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no_reciprocal` | No: es el recíproco, y 5 lo tumba | — |
| 　 | `yes_same` | Sí: es la misma frase con el orden cambiado | `error_del_reciproco` |
| 　 | `no_first_false` | No, porque la primera también es falsa | `no_reconoce_inclusion` |
| 　 | `cannot` | No se puede decidir sin más información | `habito_evita_decidir` |

Escalera de pistas:
1. Dar vuelta una frase produce una afirmación nueva.
2. Busca un real que NO sea irracional.
3. 5 es real y es racional, no irracional: tumba el recíproco.

**E6**

El sofista vuelve con esta: «Todo número con coma es racional». ¿Cómo la juzgas?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_pi` | Falsa: π se escribe con coma (3,1415…) y es irracional | — |
| 　 | `true_comma` | Verdadera: la coma indica que viene de una división | `clasifica_por_apariencia` |
| 　 | `false_integers` | Falsa: los enteros no llevan coma y también son racionales | `confunde_contraejemplo_con_caso_no_cubierto` |
| 　 | `cannot` | No se puede decidir | `habito_evita_decidir` |

Escalera de pistas:
1. Necesitas un número con coma que NO sea racional.
2. Piensa en los irracionales: ¿cómo se escriben en decimal?
3. π = 3,1415… lleva coma y no es fracción de enteros.

**E7**

¿Cuál de estas cuatro afirmaciones es la ÚNICA falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_one` | Todo racional es entero | — |
| 　 | `true_nat` | Todo natural es entero | `no_reconoce_inclusion` |
| 　 | `true_int` | Todo entero es real | `no_reconoce_inclusion` |
| 　 | `true_irr` | Ningún irracional es racional | `no_distingue_exclusion` |

Escalera de pistas:
1. Tres son inclusiones del mapa; una va en dirección contraria.
2. Busca la que dice que un conjunto grande cabe dentro de uno pequeño.
3. 1/2 es racional y no es entero: esa es la falsa.


### A9. Cierre

*El expediente del detective* — **Cada afirmación, su veredicto y su prueba**

Verdadera se prueba con la definición; falsa se tumba con un contraejemplo.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Verdadera. Prueba: la cadena de inclusión. |
|  | ✅ | Verdadera. Prueba: se escribe sobre 1. |
|  | ✗ | FALSA. El recíproco de la anterior. |
|  | ✗ | FALSA. Contraejemplo: la diagonal de B07. |
|  | ✅ | Verdadera. Prueba: irracional significa «no racional». |

Mira las filas 2 y 3: son la misma frase dada vuelta, y tienen veredictos opuestos. Ese par es el resumen del nodo entero.

#### Pregunta de abstracción

¿Qué tienen en común los razonamientos falsos que cazaste hoy?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `reciprocal` | En todos se dio vuelta una afirmación verdadera y se supuso que seguía valiendo | — |
| 　 | `one_counter` | Todos se tumban con un solo contraejemplo | — |
| 　 | `calculation` | Todos tienen un error de cálculo | — |
| 　 | `irrational` | Todos hablan de números irracionales | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas de las cinco son verdaderas?
¿Cuántas de las cinco son verdaderas?

Respuesta: `3`

Escalera de pistas:
1. Juzga cada una por separado; no supongas que el recíproco hereda nada.
2. Las afirmaciones 2 y 4 son los recíprocos de la 1 y la 3.
3. 1/2 tumba la 2, y 5 tumba la 4. Quedan tres verdaderas.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otras frases. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué dar vuelta una frase produce otra afirmación.

**PD1**

«Todo natural es racional». ¿Verdadera o falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `no_reconoce_inclusion` |

**PD2**

«Todo racional es natural». ¿Verdadera o falsa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa | — |
| 　 | `true` | Verdadera | `error_del_reciproco` |

**PD3**

Para tumbar «todo número entero es positivo», ¿qué basta?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `one` | Un solo contraejemplo, como −4 | — |
| 　 | `many` | Varios contraejemplos | `necesita_muchos_contraejemplos` |
| 　 | `all` | Revisar todos los enteros | `exige_verificacion_exhaustiva` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B12-A10` | `false` | `no_reconoce_reales_como_complejos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A11` | `true` | `cree_que_todo_complejo_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A12` | `true` | `cree_que_todo_complejo_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A14` | `false` | `confunde_imaginario_puro_con_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A2` | `true` | `confunde_implicacion_con_reciproca` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A5` | `true` | `cree_que_todo_real_es_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A6` | `true` | `cree_que_todo_decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A7` | `false` | `cree_que_todo_decimal_infinito_es_irracional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A8` | `true` | `cree_que_todo_real_es_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-A9` | `false` | `no_reconoce_irracionales_como_reales` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-D1` | `false` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-D2` | `true` | `error_del_reciproco` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-D3` | `many` | `necesita_muchos_contraejemplos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-D3` | `all` | `exige_verificacion_exhaustiva` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E1` | `false` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E1` | `cannot` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E2` | `true` | `error_del_reciproco` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E2` | `cannot` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E3` | `sqrt2` | `contraejemplo_fuera_del_conjunto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E3` | `zero` | `cero_no_es_racional` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E3` | `five` | `confunde_ejemplo_con_contraejemplo` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E4` | `wrong_roots` | `duda_del_calculo_correcto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E4` | `reciprocal` | `confunde_tipo_de_error` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E4` | `none` | `ejemplos_prueban_universal` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E5` | `yes_same` | `error_del_reciproco` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E5` | `no_first_false` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E5` | `cannot` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E6` | `true_comma` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E6` | `false_integers` | `confunde_contraejemplo_con_caso_no_cubierto` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E6` | `cannot` | `habito_evita_decidir` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E7` | `true_nat` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E7` | `true_int` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-E7` | `true_irr` | `no_distingue_exclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-PD1` | `false` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-PD2` | `true` | `error_del_reciproco` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-PD3` | `many` | `necesita_muchos_contraejemplos` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B12-DETECTIVE-FALSEDADES-PD3` | `all` | `exige_verificacion_exhaustiva` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b12-detective-falsedades-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
