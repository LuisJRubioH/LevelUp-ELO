# Nodo: El mismo número, varias casas — PREALG-N1-B11-CLASIFICADOR-RIGUROSO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N1-B11-CLASIFICADOR-RIGUROSO` |
| `concept_slug` | `clasificador_riguroso` |
| Error focal | `pertenencia_unica` |
| Sala / edificio | — |
| Guía | KatIA |
| Entra después de | `PREALG-N1-B10-CLASIFICADOR-BASICO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Consolidación · Clasificador riguroso

**Título:** El mismo número, varias casas

En el nodo anterior buscabas el peldaño más bajo. Aquí vas a hacer lo contrario: listar TODOS los conjuntos a los que pertenece un número. Suena a más trabajo y en realidad es una sola idea: la cadena de inclusión hace casi todo el trabajo.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.

**D1**

¿A cuántos de los cinco conjuntos $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ pertenece el número 8?

Respuesta: `4`

**D2**

Si un número es entero, ¿puede ser racional al mismo tiempo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: todo entero se escribe n/1 | — |
| 　 | `no` | No: o es entero o es racional, no las dos | `pertenencia_unica` |
| 　 | `sometimes` | Solo algunos enteros | `pertenencia_unica` |

**D3**

¿Puede un número ser racional e irracional a la vez?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `never` | Nunca: son los únicos dos que se excluyen | — |
| 　 | `sometimes` | Sí, algunos son los dos | `no_distingue_exclusion` |
| 　 | `always` | Todos los reales son los dos | `no_distingue_exclusion` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Consolidación* — **El padrón de la polis**

El escribano del padrón tiene que anotar a cada ciudadano en los registros que le corresponden. Llega Nicómaco: es alfarero, es vecino del barrio alto, es padre de familia y es miembro del coro.

El escribano lo anota en el registro de alfareros y cierra el rollo. Cuando el coro pide su lista para el festival, Nicómaco no aparece.

**Pregunta:** ¿En cuántos registros tenía que estar Nicómaco? Piénsalo, porque con los números pasa lo mismo.

**Intento genuino** (`acotado`): Escoge lo que crees tú. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | En uno: el más importante | — |
| 　 | `b` | En todos los que le apliquen a la vez | — |
| 　 | `c` | En uno, pero con una nota que remita a los demás | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos números y sus listas de pertenencia**

Abajo hay dos números. Para cada uno pregúntate las cinco veces: ¿está en ℕ? ¿en ℤ? ¿en ℚ? ¿en 𝕀? ¿en ℝ? Fíjate en cuántas veces la respuesta es sí.

- **El que está en cuatro** — Entra en ℕ y, por la cadena de inclusión, entra automáticamente en todos los de arriba. Solo se queda fuera de 𝕀.
- **El que está en dos** — No es fracción, así que se queda fuera de ℕ, ℤ y ℚ. Entra solo en 𝕀 — y en ℝ, porque ℝ es la unión de ℚ con 𝕀.

**Resolución:** La regla es corta: **encuentra el peldaño más bajo y márcalo hacia arriba**. Como ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ, entrar en uno te mete en todos los siguientes sin esfuerzo. La única excepción es 𝕀, que no está en la cadena: o eres racional o eres irracional, nunca los dos.

**Definición — Pertenencia múltiple**

$$x\in\mathbb{N}\ \Rightarrow\ x\in\mathbb{Z}\ \Rightarrow\ x\in\mathbb{Q}\ \Rightarrow\ x\in\mathbb{R}\qquad \mathbb{Q}\cap\mathbb{I}=\varnothing$$

La frase del nodo: pertenecer a un conjunto no te saca de ningún otro. Solo ℚ y 𝕀 se excluyen entre sí, y por eso ℝ es la unión de los dos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\Rightarrow` | implica | si lo de la izquierda es cierto, lo de la derecha también |
| `\cap` | intersección | lo que está en los dos conjuntos a la vez |
| `\varnothing` | conjunto vacío | no hay ni un solo elemento: ℚ y 𝕀 no comparten nada |
| `\mathbb{Q}\cup\mathbb{I}=\mathbb{R}` | ℚ unión 𝕀 es ℝ | juntos, y sin repetir a nadie, forman la recta |
| `x\in\mathbb{Z},\ x\notin\mathbb{N}` | entero pero no natural | solo los negativos: −4, −17… |
| `x\in\mathbb{Q},\ x\notin\mathbb{Z}` | racional pero no entero | las fracciones con parte decimal: 1/2, −2,75… |

### A5. Ejemplos resueltos

#### El registro del número −6 · *resuelto*

Lista TODOS los conjuntos entre $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ a los que pertenece $-6$.

- ¿Está en ℕ? No: es negativo y los naturales empiezan en 0.
- ¿Está en ℤ? Sí: es un número sin partes, del lado izquierdo del 0.
- Encontré el peldaño más bajo. Ahora marco hacia arriba sin volver a pensar.
- ℤ ⊂ ℚ ⊂ ℝ, así que −6 está también en ℚ y en ℝ.
- ¿Está en 𝕀? No: es racional, y ℚ e 𝕀 no comparten elementos. Total: tres conjuntos.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 dejé de revisar conjunto por conjunto y marqué todos los de arriba de golpe. ¿Qué me da derecho a hacer eso?'}

#### El registro del número π · *resuelto*

Lista TODOS los conjuntos a los que pertenece $\pi$.

- ¿Está en ℕ? No. ¿En ℤ? No: no es un número sin partes.
- ¿Está en ℚ? No: no se puede escribir como fracción de enteros.
- Aquí la cadena no me sirve: no encontré ningún peldaño donde entrara.
- ¿Está en 𝕀? Sí, justamente por no ser fracción. Ese es su único conjunto propio.
- ¿Está en ℝ? Sí: ℝ = ℚ ∪ 𝕀, y π está en 𝕀. Total: dos conjuntos.

#### El número al que le dieron un solo registro · *TRAMPA*

Un discípulo llenó el padrón así. Está mal: «5 es natural, así que no es entero ni racional. −3 es entero, así que no es racional. Cada número tiene un conjunto, igual que cada persona tiene un oficio».

- Escribe 5 como fracción: 5/1. ¿Eso lo hace racional?
- Sí. Y sigue siendo natural: escribirlo distinto no lo cambia.
- Ahora aplica lo mismo a −3: ¿se puede escribir −3/1?

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '5\\in\\mathbb{N}\\ \\Rightarrow\\ 5\\notin\\mathbb{Z},\\ \\mathbb{Q}', 'right_latex': '5\\in\\mathbb{N}\\ \\Rightarrow\\ 5\\in\\mathbb{Z},\\ \\mathbb{Q},\\ \\mathbb{R}', 'rows': [{'wrong': 'Cada número tiene un conjunto, como cada persona un oficio', 'right': 'Cada número está en todos los que lo contienen, como Nicómaco en todos sus registros'}, {'wrong': 'Ser natural impide ser entero', 'right': 'Ser natural GARANTIZA ser entero: ℕ ⊂ ℤ'}]}
**¿Por qué falla?:** ¿Por qué 5 está en cuatro conjuntos y no en uno? Escribe la lista completa.


### A6. Puente — parcialmente resueltos

Ahora los resuelves tú, pero no desde cero: el registro ya está empezado y solo faltan huecos.

**P1** (*falta: last*) — ¿A cuántos de los cinco conjuntos $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ pertenece $-15$?

- dado: $-15\notin\mathbb{N}\ (\text{es negativo})$
- dado: $-15\in\mathbb{Z}$
- hueco `P1-b1`: $\text{Total de conjuntos}=$ → `3`

**P2** (*falta: middle*) — ¿A cuántos pertenece $\dfrac{3}{8}$? ¿Y $\sqrt{7}$?

- dado: $\dfrac{3}{8}=0{,}375\ \Rightarrow\ \text{racional no entero}$
- hueco `P2-b1`: $\text{Conjuntos de }\tfrac{3}{8}=$ → `2`
- hueco `P2-b2`: $\text{Conjuntos de }\sqrt{7}=$ → `2`

**P3** (*falta: statement_only*) — Solo el planteamiento: ¿a cuántos de los cinco conjuntos pertenece el número 0? Cuidado con los dos casos límite del curso.

- hueco `P3-b1`: $\text{Total de conjuntos}=$ → `4`


### A7. Comparación de métodos

**Dos formas de llenar el registro**

¿A qué conjuntos pertenece $-2$? Las dos soluciones son correctas.

- **Método 1 · Revisar uno por uno** — 
- **Método 2 · Peldaño más bajo y hacia arriba** — 

**Pregunta:** ¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si aplicas el método 2 a $\sqrt{3}$?

**Insight:** Con √3 el método 2 se queda mudo: no hay peldaño de la cadena donde entre, así que no hay desde dónde marcar hacia arriba. Ese silencio ES la respuesta — significa irracional. Los irracionales no están en la cadena, y por eso necesitan que les preguntes aparte.

### A8. Práctica independiente (7 ítems)

**E1**

¿A cuántos de los cinco conjuntos $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ pertenece el número 21?

Respuesta: `4`

Escalera de pistas:
1. Busca el peldaño más bajo donde entra.
2. 21 cuenta objetos completos: entra en ℕ.
3. Desde ℕ marca hacia arriba: ℕ, ℤ, ℚ, ℝ. En 𝕀 no.

**E2**

¿A cuántos de los cinco pertenece $\dfrac{5}{2}$?

Respuesta: `2`

Escalera de pistas:
1. Resuelve primero: 5 ÷ 2 = 2,5.
2. 2,5 no cuenta objetos completos ni es entero.
3. Entra recién en ℚ, y de ahí a ℝ: dos conjuntos.

**E3**

¿Cuál de estos números pertenece a EXACTAMENTE dos de los cinco conjuntos?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sqrt11` | √11 | — |
| 　 | `twelve` | 12 | `pertenencia_unica` |
| 　 | `neg9` | −9 | `cuenta_mal_la_cadena` |
| 　 | `zero` | 0 | `cero_no_es_natural` |

Escalera de pistas:
1. Cuenta para cada uno: ¿en cuántos entra?
2. 12 y 0 entran en cuatro; −9 entra en tres.
3. √11 no es fracción: solo 𝕀 y ℝ. Son dos.

**E4**

Un discípulo escribió: «−4 pertenece a ℤ y a ℝ, pero no a ℚ, porque no está escrito como fracción». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `as_fraction` | −4 sí es racional: se escribe −4/1 | — |
| 　 | `not_real` | El error es otro: −4 tampoco es real | `negativo_no_es_real` |
| 　 | `not_integer` | El error es que −4 no es entero | `negativo_no_es_entero` |
| 　 | `none` | Ningún error, está bien | `clasifica_por_apariencia` |

Escalera de pistas:
1. Ser racional no exige estar ESCRITO como fracción: exige poder serlo.
2. ¿Puedes escribir −4 con barra sin cambiar su valor?
3. −4 = −4/1, fracción de enteros. Es racional.

**E5**

¿Es verdadera o falsa? «Como $7$ es natural, entonces $7\notin\mathbb{Z}$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_both` | Falsa: 7 es natural Y entero, porque ℕ ⊂ ℤ | — |
| 　 | `true_one` | Verdadera: un número está en un solo conjunto | `pertenencia_unica` |
| 　 | `false_notnatural` | Falsa: 7 no es natural, es entero | `pertenencia_unica` |
| 　 | `depends` | Depende de si lo escribes con signo o sin signo | `representacion_define_el_numero` |

Escalera de pistas:
1. Lee qué significa ℕ ⊂ ℤ.
2. Significa que todo natural es también entero.
3. 7 está en los dos, y además en ℚ y ℝ.

**E6**

El escribano quiere una regla para llenar el padrón sin revisar los cinco registros cada vez. ¿Cuál le sirve?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `lowest` | Hallar el conjunto más bajo y marcar todos los de arriba; preguntar por 𝕀 solo si no entró en ninguno | — |
| 　 | `one_each` | Un número, un registro: el que mejor lo describa | `pertenencia_unica` |
| 　 | `all_five` | Marcar los cinco siempre: así nunca falta ninguno | `no_distingue_exclusion` |
| 　 | `biggest` | Marcar solo ℝ: contiene a todos | `pierde_informacion` |

Escalera de pistas:
1. Vuelve a Nicómaco: ¿un registro o todos los que le aplican?
2. Todos los que le apliquen — pero sin marcar los que no.
3. ℚ e 𝕀 se excluyen, así que marcar los cinco siempre es falso.

**E7**

¿Cuál de estas afirmaciones es FALSA?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_one` | Un número puede ser racional e irracional a la vez | — |
| 　 | `true_nat` | Todo natural es real | `no_reconoce_inclusion` |
| 　 | `true_int` | Todo entero es racional | `no_reconoce_inclusion` |
| 　 | `true_irr` | Todo irracional es real | `no_reconoce_inclusion` |

Escalera de pistas:
1. Tres de las cuatro son inclusiones que ya usaste en el nodo.
2. ℕ ⊂ ℝ, ℤ ⊂ ℚ e 𝕀 ⊂ ℝ son las tres verdaderas.
3. Irracional significa «no racional»: no se puede ser los dos.


### A9. Cierre

*El padrón completo* — **Cuántos registros le tocan a cada número**

Cada fila cuenta en cuántos de los cinco conjuntos entra el número.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Cuatro. Entra en el más bajo y sube toda la cadena. |
|  | ✅ | Cuatro, igual que 7: en este curso 0 ∈ ℕ. |
|  | ✅ | Tres. El signo lo deja fuera de ℕ. |
|  | ✅ | Dos. Entra recién en el tercer peldaño. |
|  | ✗ | Dos, pero por fuera de la cadena: 𝕀 no contiene a nadie. |

Lee la columna de la derecha de arriba abajo: 4, 4, 3, 2, 2. Cuanto más arriba entra un número, en menos registros aparece. Y la última fila es la única que llega por otro camino.

#### Pregunta de abstracción

¿Qué regla estructural explica todos los casos de este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `chain` | Entrar en un conjunto de la cadena te mete en todos los de arriba | — |
| 　 | `exclusive` | ℚ e 𝕀 son los únicos dos que se excluyen entre sí | — |
| 　 | `one_each` | Cada número pertenece a exactamente un conjunto | — |
| 　 | `all_five` | Todo número real pertenece a los cinco conjuntos | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas anotaciones hace en total?
¿Cuántas anotaciones hace en total?

Respuesta: `11`

Escalera de pistas:
1. Cuenta los conjuntos de cada número por separado y después suma.
2. 4 entra en cuatro; −11 en tres.
3. 2/5 y √13 entran en dos cada uno: 4 + 3 + 2 + 2.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.

- **Mejoró:** Avance: hoy resolviste más que al entrar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué un número aparece en varios registros a la vez.

**PD1**

¿A cuántos de los cinco conjuntos pertenece el número 30?

Respuesta: `4`

**PD2**

Si un número es natural, ¿puede ser real al mismo tiempo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí: ℕ ⊂ ℝ | — |
| 　 | `no` | No: o es natural o es real | `pertenencia_unica` |

**PD3**

¿A cuántos de los cinco conjuntos pertenece $\sqrt{5}$?

Respuesta: `2`

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-D2` | `no` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-D2` | `sometimes` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-D3` | `sometimes` | `no_distingue_exclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-D3` | `always` | `no_distingue_exclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E3` | `twelve` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E3` | `neg9` | `cuenta_mal_la_cadena` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E3` | `zero` | `cero_no_es_natural` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E4` | `not_real` | `negativo_no_es_real` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E4` | `not_integer` | `negativo_no_es_entero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E4` | `none` | `clasifica_por_apariencia` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E5` | `true_one` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E5` | `false_notnatural` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E5` | `depends` | `representacion_define_el_numero` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E6` | `one_each` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E6` | `all_five` | `no_distingue_exclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E6` | `biggest` | `pierde_informacion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E7` | `true_nat` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E7` | `true_int` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-E7` | `true_irr` | `no_reconoce_inclusion` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-CLASIFICADOR-RIGUROSO-PD2` | `no` | `pertenencia_unica` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-DESC-three_plus_two_i` | `pure_imaginary` | `confunde_conjunto_formal_con_descriptor` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |
| `PREALG-N1-B11-DESC-two_i` | `complex_non_real` | `confunde_conjunto_formal_con_descriptor` | Revisa el procedimiento paso a paso y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/01-prealg-n1-agora/b11-clasificador-ii-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
