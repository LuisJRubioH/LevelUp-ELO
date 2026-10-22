# Nodo: El orden en que se oye no es el orden en que se escribe — ALG-N1-L03-TRADUCCION

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-L03-TRADUCCION` |
| `concept_slug` | `traduccion` |
| Error focal | `traduce_en_el_orden_de_las_palabras` |
| Sala / edificio | La mesa de dictado |
| Guía | Meritka |
| Entra después de | `ALG-N1-L02-CONSTANTES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La mesa de dictado · Traducción

**Título:** El orden en que se oye no es el orden en que se escribe

Ya sabes qué símbolo cambia y cuál está fijado. Ahora los encargos llegan hablados: alguien dicta una frase y hay que dejarla en un registro corto. La trampa está en creer que se escribe en el mismo orden en que se oye.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de sentarte a la mesa. Sin nota.

**D1**

Un mensajero dicta: «el doble de siete». ¿Qué número es?

Respuesta: `14`

**D2**

«Tres más que un número» se escribe…

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `plus` | $n+3$ | — |
| 　 | `times` | $3n$ | `confunde_mas_con_veces` |
| 　 | `minus` | $n-3$ | `confunde_la_operacion_dictada` |

**D3**

¿Da lo mismo escribir 9 − 4 que 4 − 9?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: la resta cambia si se invierte | — |
| 　 | `yes` | Sí: son los mismos dos números | `resta_es_conmutativa` |
| 　 | `sign` | Sí, salvo por el signo, que da igual | `resta_es_conmutativa` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la mesa de dictado* — **Dos escribas, una frase, dos registros**

Llega un mensajero con prisa y dicta de corrido: «cinco menos que las cestas que traiga la barca».

Los dos escribas de la mesa anotan a la vez. Meritka mira las dos tablillas y no dice cuál está bien. Dice otra cosa:

«Uno de los dos escribió lo que oyó. El otro escribió lo que significa. Si la barca trae ocho cestas, sus dos registros no dan el mismo número, y solo uno de ellos sirve para pedir grano.»

**Pregunta:** ¿Se escribe en el orden en que se dicta?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí: se anota palabra por palabra, según se oyen | — |
| 　 | `b` | Depende de la operación: unas admiten el cambio y otras no | — |
| 　 | `c` | No: siempre se escribe al revés de como se dicta | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **La misma palabra, dos comportamientos**

Dos encargos con la misma forma. Solo uno se puede anotar tal como suena.

- **Se deja igual** — 5 + c da lo mismo que c + 5. La suma no distingue el orden.
- **Hay que darle la vuelta** — Escrito como suena daría 5 − 8 = −3. La resta sí distingue el orden.

**Resolución:** Traducir no es copiar el orden de las palabras: es decidir QUIÉN pone la cantidad y QUIÉN la quita. En la suma y en la multiplicación da igual el orden, así que la copia literal cuela. En la resta y en la división no, y ahí es donde el registro sale al revés.

**Definición — Traducir un encargo hablado**

$$\text{«cinco menos que }c\text{»}\;\longrightarrow\; c-5$$

TRADUCIR es pasar de una frase a una expresión con tres decisiones: qué cantidad no se conoce (le pones letra), qué operación pide la frase, y en qué orden entran los términos en esa operación. Las expresiones «más que» y «veces» no cambian con el orden; «menos que» y «entre» sí. Cuando la frase agrupa —«el doble de la suma de…»— hace falta un paréntesis.

| Símbolo | Se lee | Significa |
|---|---|---|
| `c+5` | ce más cinco | «cinco más que c» · el orden da igual |
| `c-5` | ce menos cinco | «cinco menos que c» · c es quien pierde |
| `5-c` | cinco menos ce | «c menos que cinco» · otra frase distinta |
| `3c` | tres ce | «el triple de c» · el orden da igual |
| `\dfrac{c}{3}` | ce entre tres | «c repartido en tres» · el orden importa |
| `2(c+5)` | dos por, abre, ce más cinco | «el doble de la suma» · la frase agrupa |

### A5. Ejemplos resueltos

#### Nombrar primero, operar después · *resuelto*

Un mensajero dicta: «el doble de las cestas que traiga la barca, y tres más». Deja el encargo en un registro.

- Lo que no se sabe todavía es cuántas cestas trae la barca: la llamo c.
- «El doble de las cestas» actúa sobre c y da 2c.
- «Y tres más» añade 3 a lo anterior: 2c + 3.
- Compruebo con un caso: si trae 6 cestas, el doble es 12 y tres más, 15.
- Sustituyo: 2 · 6 + 3 = 15. Coinciden, así que el registro dice lo mismo que la voz.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué el 2 se escribe pegado a la c y el 3 no?'}

#### Cuando hace falta un paréntesis · *resuelto*

Otro encargo: «el doble de lo que sumen las cestas y las tres jarras». ¿Es 2c + 3?

- La frase dice «el doble de lo que SUMEN»: primero se suma, después se dobla.
- Lo que suman es c + 3.
- El doble de eso es 2(c + 3). El paréntesis marca qué se dobla.
- Con c = 6: la frase da (6 + 3) · 2 = 18, y 2c + 3 daría 15.
- No son la misma expresión. El paréntesis no es adorno: cambia el resultado.

#### El escriba que anotó lo que oyó · *TRAMPA*

Vuelve el encargo del principio: «cinco menos que las cestas». Un escriba anota 5 − c, porque el cinco se dijo primero.

- Pruebo la frase con un caso claro: si hay 8 cestas y son cinco menos, quedan 3.
- Mi registro tiene que dar 3 con c = 8. El de 5 − c da −3: descartado.
- Regla para no volver a caer: escribe primero la cantidad de la que se habla, y después qué le pasa.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '5-c', 'right_latex': 'c-5', 'rows': [{'wrong': 'El cinco se dijo primero, luego va primero', 'right': '«Menos que c» significa que a c se le quitan cinco'}, {'wrong': 'c=8\\Rightarrow 5-8=-3', 'right': 'c=8\\Rightarrow 8-5=3'}]}
**¿Por qué falla?:** Explica por qué con «cinco MÁS que las cestas» el orden literal sí habría funcionado, y con «menos que» no.


### A6. Puente — parcialmente resueltos

El registro va empezado; completa los huecos.

**P1** (*falta: last*) — «Cuatro menos que las jarras». Si hay 11 jarras, ¿cuántas quedan?

- dado: $j-4$
- dado: $j=11$
- hueco `P1-b1`: $11-4=$ → `7`

**P2** (*falta: middle*) — «El triple de las cestas, y dos más». Escribe el coeficiente y evalúa con c = 5.

- dado: $3c+2$
- hueco `P2-b1`: $\text{coeficiente}=$ → `3`
- hueco `P2-b2`: $3\cdot 5+2=$ → `17`

**P3** (*falta: statement_only*) — Solo el planteamiento: «el doble de la suma de las jarras y 4». ¿Cuánto vale si hay 6 jarras?

- hueco `P3-b1`: $2(j+4)=$ → `20`


### A7. Comparación de métodos

**Dos maneras de traducir un encargo**

«Siete menos que el triple de las cestas». ¿Cómo se llega al registro?

- **Método 1 · Trocear la frase en orden** — 
- **Método 2 · Nombrar primero la cantidad** — 

**Pregunta:** Con 4 cestas, ¿qué da cada registro, y cuál coincide con la frase?

**Insight:** El triple de 4 son 12, y siete menos son 5. El método 2 da 3·4 − 7 = 5 ✓; el método 1 da 7 − 12 = −5 ✗. Trocear en orden solo es fiable cuando todas las operaciones de la frase son sumas o productos; en cuanto aparece un «menos que» o un «entre», hay que nombrar primero la cantidad y construir alrededor.

### A8. Práctica independiente (7 ítems)

**E1**

«Seis menos que el número de remeros». ¿Qué registro lo dice?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `rminus` | $r-6$ | — |
| 　 | `minusr` | $6-r$ | `traduce_en_el_orden_de_las_palabras` |
| 　 | `rplus` | $r+6$ | `confunde_la_operacion_dictada` |
| 　 | `sixr` | $6r$ | `confunde_mas_con_veces` |

Escalera de pistas:
1. ¿A quién se le quitan seis: a los remeros o al seis?
2. Prueba con 10 remeros: seis menos son 4.
3. Busca el registro que dé 4 cuando r = 10.

**E2**

Escribe el registro de «el triple de las jarras, más dos». Usa j para las jarras y no dejes espacios.

Respuesta: `3j+2`
También válidas: `2+3j`

Escalera de pistas:
1. «El triple de j» se escribe pegando el 3 a la j.
2. «Más dos» añade un término suelto.
3. Queda un producto y una suma: 3j y luego +2.

**E3**

«El doble de la suma de las cestas y cinco». ¿Cuál es?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `paren` | $2(c+5)$ | — |
| 　 | `flat` | $2c+5$ | `ignora_la_agrupacion_de_la_frase` |
| 　 | `both` | $2c+10$… solo si se reparte después | `confunde_forma_con_traduccion` |
| 　 | `swap` | $c+10$ | `confunde_la_operacion_dictada` |

Escalera de pistas:
1. ¿Qué se dobla: solo las cestas, o la suma entera?
2. Prueba con c = 3: la frase da (3 + 5) · 2 = 16.
3. 2c + 5 daría 11. Hace falta marcar qué se dobla.

**E4**

Un escriba traduce «las jarras repartidas entre cuatro» como 4/j. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `order` | Invirtió el orden: lo que se reparte va arriba, j/4 | — |
| 　 | `op` | No es división, es resta | `confunde_la_operacion_dictada` |
| 　 | `letter` | No debió usar letra para las jarras | `toda_letra_es_variable` |
| 　 | `none` | No hay error: da lo mismo | `traduce_en_el_orden_de_las_palabras` |

Escalera de pistas:
1. Con 12 jarras entre cuatro, tocan a 3 por parte.
2. 4/12 no es 3.
3. Lo que se reparte va en el numerador.

**E5**

¿Verdadera o falsa? «Una frase se traduce escribiendo los símbolos en el mismo orden en que se oyen las palabras.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: «cinco menos que c» se oye 5 primero y se escribe c − 5 | — |
| 　 | `true` | Verdadera: para eso se dicta despacio | `traduce_en_el_orden_de_las_palabras` |
| 　 | `true_short` | Verdadera si la frase es corta | `traduce_en_el_orden_de_las_palabras` |
| 　 | `false_always` | Falsa: nunca coincide el orden | `sobregeneraliza_traduccion` |

Escalera de pistas:
1. Para tumbar un «siempre» basta un contraejemplo.
2. Piensa en una resta dictada al revés.
3. «Cinco menos que las cestas» no se escribe 5 − c.

**E6**

Selecciona TODAS las frases que se pueden anotar en el mismo orden en que se oyen, sin darles la vuelta.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | «Cuatro más que las cestas» | — |
| 　 | `b` | «Cuatro menos que las cestas» | — |
| ✅ | `c` | «Cuatro veces las cestas» | — |
| ✅ | `d` | «Cuatro repartido entre las cestas» | — |

Escalera de pistas:
1. Pregúntate si esa operación cambia al invertir el orden.
2. La suma y el producto no cambian; la resta sí.
3. En «cuatro repartido entre las cestas» el cuatro sí es el que se reparte.

**E7**

«El doble de los remeros, menos siete». Si la barca lleva 9 remeros, ¿cuánto vale el registro?

Respuesta: `11`

Escalera de pistas:
1. Primero el doble, después la resta.
2. El doble de 9 es 18.
3. 18 − 7 = …


### A9. Cierre

*¿Se puede escribir tal como suena?* — **Qué frases perdonan el orden literal y cuáles no**

La copia literal no es siempre un error: hay operaciones a las que el orden les da igual. El problema es no saber cuáles.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | La suma no distingue el orden: escribirlo como suena da lo mismo. |
|  | ✅ | El producto tampoco lo distingue. Otro caso en que la copia cuela. |
|  | ✗ | Aquí se rompe: hay que poner primero a quien pierde. Es el caso focal. |
|  | ✗ | Igual que la resta: lo que se reparte va arriba, se diga cuando se diga. |
|  | ✗ | No falla el orden sino la agrupación: la frase manda hacer la suma primero. |
|  | ~ (ámbar) | Cambiando dos palabras la frase cambia de bando: ahora sí es 4 − c. El orden literal acierta por casualidad. |

La última fila avisa de lo peor que puede pasar: acertar por el motivo equivocado. Si traduces copiando el orden, a veces te sale bien, y eso refuerza el hábito que va a fallarte a la siguiente. Nombra la cantidad primero y construye alrededor: entonces aciertas siempre por el mismo motivo.

#### Pregunta de abstracción

¿Qué comparten los tres encargos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `name_first` | En los tres conviene nombrar la cantidad desconocida antes de operar | — |
| 　 | `order_matters` | En los tres el orden o la agrupación cambia el resultado si se descuida | — |
| 　 | `literal` | En los tres basta con escribir los símbolos según se oyen | — |
| 　 | `no_paren` | En los tres los paréntesis se pueden quitar sin consecuencias | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas cestas llegan?
¿Cuántas cestas llegan?

Respuesta: `26`

Escalera de pistas:
1. Nombra las cestas de la barca con una letra antes de operar.
2. El doble primero, la resta después: 2c − 4.
3. 30 − 4 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros encargos. Sin nota.

- **Mejoró:** Avance: ya colocas la cantidad antes de decidir qué se le hace.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el «menos que», que es el que tumba la traducción literal.

**PD1**

Un mensajero dicta: «el triple de seis». ¿Qué número es?

Respuesta: `18`

**PD2**

«Dos menos que las jarras» se escribe…

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `jminus` | $j-2$ | — |
| 　 | `minusj` | $2-j$ | `traduce_en_el_orden_de_las_palabras` |
| 　 | `twoj` | $2j$ | `confunde_mas_con_veces` |

**PD3**

¿En cuál de estas frases el orden literal NO importa?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | «Tres más que las cestas» | — |
| 　 | `sub` | «Tres menos que las cestas» | `traduce_en_el_orden_de_las_palabras` |
| 　 | `div` | «Las cestas repartidas entre tres» | `traduce_en_el_orden_de_las_palabras` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-L03-TRADUCCION-D2` | `times` | `confunde_mas_con_veces` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-D2` | `minus` | `confunde_la_operacion_dictada` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-D3` | `yes` | `resta_es_conmutativa` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-D3` | `sign` | `resta_es_conmutativa` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E1` | `minusr` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E1` | `rplus` | `confunde_la_operacion_dictada` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E1` | `sixr` | `confunde_mas_con_veces` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E3` | `flat` | `ignora_la_agrupacion_de_la_frase` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E3` | `both` | `confunde_forma_con_traduccion` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E3` | `swap` | `confunde_la_operacion_dictada` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E4` | `op` | `confunde_la_operacion_dictada` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E4` | `letter` | `toda_letra_es_variable` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E4` | `none` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E5` | `true` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E5` | `true_short` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-E5` | `false_always` | `sobregeneraliza_traduccion` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-PD2` | `minusj` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-PD2` | `twoj` | `confunde_mas_con_veces` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-PD3` | `sub` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |
| `ALG-N1-L03-TRADUCCION-PD3` | `div` | `traduce_en_el_orden_de_las_palabras` | Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
