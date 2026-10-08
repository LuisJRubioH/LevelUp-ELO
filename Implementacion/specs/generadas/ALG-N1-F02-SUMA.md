# Nodo: El denominador nombra la parte, no se suma — ALG-N1-F02-SUMA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-F02-SUMA` |
| `concept_slug` | `suma_de_fracciones_algebraicas` |
| Error focal | `suma_numeradores_y_denominadores` |
| Sala / edificio | El canal madre |
| Guía | Tabiry |
| Entra después de | `ALG-N1-F01-SIMPLIFICAR` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El canal madre · Suma de fracciones

**Título:** El denominador nombra la parte, no se suma

En la parcela partida aprendiste cuándo se puede tachar. Aquí llegan dos ramales que riegan lo mismo y hay que anotar cuánto agua es en total. La cuenta parece obvia y hay una manera de hacerla que encoge el caudal.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el azud. Sin nota.

**D1**

¿Cuánto es $\dfrac{2}{7}+\dfrac{3}{7}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `five7` | $\dfrac{5}{7}$ | — |
| 　 | `five14` | $\dfrac{5}{14}$ | `suma_numeradores_y_denominadores` |
| 　 | `six7` | $\dfrac{6}{7}$ | `multiplica_en_vez_de_sumar` |

**D2**

Un ramal lleva 3 partes de un caudal dividido en 8, y otro lleva 2 de esas mismas partes. ¿Cuántas partes de 8 llevan entre los dos?

Respuesta: `5`

**D3**

¿Se pueden sumar $\dfrac{1}{2}$ y $\dfrac{1}{3}$ sumando los numeradores?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: las partes no son del mismo tamaño | — |
| 　 | `yes` | Sí: da $\dfrac{2}{5}$ | `suma_numeradores_y_denominadores` |
| 　 | `yes_big` | Sí, si el resultado se simplifica después | `suma_numeradores_y_denominadores` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Junto al canal madre* — **El caudal que menguaba al sumarlo**

El canal madre baja del río y se reparte en ramales. Tabiry lleva la cuenta de qué parte del caudal toma cada acequia en su turno de riego.

«La acequia del norte toma dos quintos y la del este, un quinto. El escriba sumó arriba y sumó abajo: tres décimos. Según su tablilla, juntar dos aguas deja menos agua que la que traía la del norte sola.»

Tabiry hunde la mano en el canal.

«El agua no sabe leer. Lo que menguó fue el registro.»

**Pregunta:** Al juntar dos partes de un mismo reparto, ¿qué pasa con el número de abajo?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Se suma también, como el de arriba | — |
| 　 | `b` | Se queda igual: sigue siendo el mismo reparto | — |
| 　 | `c` | Se multiplica por dos, porque ahora hay dos fracciones | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Los dos números de una fracción no hacen el mismo trabajo**

Uno cuenta trozos. El otro dice de qué tamaño son. Solo se suma el que cuenta.

- **Mismo reparto** — Tres trozos de los mismos quintos. El canal sigue partido en cinco: el 5 no se toca.
- **Repartos distintos** — Los trozos no son del mismo tamaño: primero hay que repartir todo en sextos.

**Resolución:** El numerador CUENTA trozos y el denominador los NOMBRA. Sumar cuenta trozos, así que solo se suman los de arriba. Si los trozos no son del mismo tamaño no se pueden contar juntos, igual que en la rampa no se juntaban cuerdas con herramientas: primero hay que llevarlos a un reparto común.

**Definición — Suma y resta de fracciones algebraicas**

$$\dfrac{a}{c}+\dfrac{b}{c}=\dfrac{a+b}{c}$$

Con el MISMO denominador, se suman o restan los numeradores y el denominador se copia sin tocarlo. Con denominadores DISTINTOS hay que llevar las dos fracciones a un denominador común antes de sumar: se multiplica cada fracción arriba y abajo por lo que le falte. El resultado puede quedar todavía simplificable.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{3}{x}+\dfrac{2}{x}=\dfrac{5}{x}` | mismo denominador | se suman los de arriba y el de abajo se copia |
| `\dfrac{5c}{6}-\dfrac{c}{6}=\dfrac{4c}{6}` | la resta va igual | 5c − c = 4c, y el 6 se queda |
| `\dfrac{4c}{6}=\dfrac{2c}{3}` | aún se simplifica | sumar no exime de revisar el resultado |
| `\dfrac{1}{2}+\dfrac{1}{3}=\dfrac{3+2}{6}` | denominador común | primero al mismo reparto, después se suma |
| `\dfrac{1}{x}+\dfrac{1}{y}=\dfrac{y+x}{xy}` | con letras | el común denominador puede ser un producto de letras |

### A5. Ejemplos resueltos

#### Mismo denominador · *resuelto*

Dos acequias riegan la misma tabla. La primera toma 3 partes de un caudal repartido en x turnos y la segunda, 2 de esas partes. ¿Cuánto toman entre las dos?

- Las dos fracciones cuentan trozos del MISMO reparto: los dos denominadores son x.
- Sumo los trozos: 3 + 2 = 5.
- El reparto no cambia por juntarlos: sigue habiendo x turnos.
- Queda 5/x.
- Compruebo con x = 10: 0,3 + 0,2 = 0,5, y 5/10 = 0,5 ✓.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué el denominador no cambia si estamos juntando dos cosas?'}

#### Restar y revisar el resultado · *resuelto*

Una acequia llevaba 5c partes de un caudal dividido en 6 y se le cierra el azud hasta dejarle c partes menos. ¿Qué parte del caudal le queda?

- Mismo denominador: resto los numeradores. 5c − c = 4c.
- El 6 se copia: queda 4c/6.
- No he terminado: 4 y 6 tienen un factor común, el 2.
- Simplifico dividiendo arriba y abajo entre 2: 2c/3.
- Compruebo con c = 3: 15/6 − 3/6 = 2, y 2 · 3/3 = 2 ✓.

#### El escriba que sumó abajo · *TRAMPA*

Vuelve el registro de la apertura: dos quintos del caudal y un quinto más. El escriba anotó tres décimos, y con las letras haría lo mismo: 3/x + 2/x = 5/2x.

- Junto agua con agua: el resultado no puede ser menor que lo que ya traía un ramal.
- Dos quintos son 0,4 y tres décimos son 0,3. El registro decía que juntar agua quita agua.
- Regla para no volver a caer: antes de sumar, mira si los denominadores ya son iguales; si lo son, no los toques.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{2}{5}+\\dfrac{1}{5}=\\dfrac{2+1}{5+5}', 'right_latex': '\\dfrac{2}{5}+\\dfrac{1}{5}=\\dfrac{2+1}{5}=\\dfrac{3}{5}', 'rows': [{'wrong': 'Los cuatro números entran en la suma', 'right': 'Solo entran los de arriba: los de abajo nombran el trozo'}, {'wrong': '\\dfrac{3}{10}\\ \\text{es menos que}\\ \\dfrac{2}{5}', 'right': '\\dfrac{3}{5}\\ \\text{es más que}\\ \\dfrac{2}{5}\\ \\text{✓}'}]}
**¿Por qué falla?:** Explica por qué el resultado tiene que ser MAYOR que cada sumando, y usa eso para descartar tres décimos sin hacer la cuenta.


### A6. Puente — parcialmente resueltos

El registro del turno va empezado; completa los huecos.

**P1** (*falta: last*) — Suma $\dfrac{4}{9}+\dfrac{2}{9}$ y di cuánto vale el numerador.

- dado: $\dfrac{4+2}{9}$
- hueco `P1-b1`: $4+2=$ → `6`

**P2** (*falta: middle*) — Suma $\dfrac{1}{4}+\dfrac{1}{6}$ llevándolas a doceavos.

- dado: $\dfrac{3}{12}+\dfrac{2}{12}$
- hueco `P2-b1`: $3+2=$ → `5`
- hueco `P2-b2`: $\text{denominador}=$ → `12`

**P3** (*falta: statement_only*) — Solo el planteamiento: $\dfrac{7c}{10}-\dfrac{2c}{10}$ con $c=4$. Primero la fracción, después el valor.

- hueco `P3-b1`: $\dfrac{5c}{10}=\dfrac{c}{2}\ \text{con}\ c=4:$ → `2`


### A7. Comparación de métodos

**Dos maneras de encontrar el denominador común**

$\dfrac{1}{4}+\dfrac{1}{6}$. Los dos caminos llegan a la misma agua.

- **Método 1 · Multiplicar los denominadores** — 
- **Método 2 · Buscar el mínimo común múltiplo** — 

**Pregunta:** ¿En qué se nota la diferencia con denominadores como 8 y 12?

**Insight:** Multiplicar daría 96 y el mcm es 24: cuatro veces menos. Los dos métodos son correctos, y el primero es el que conviene cuando dudas — vale más una cuenta grande bien hecha que un mcm inventado. Esto es exactamente el mcm que aprendiste en Esparta: no era un ejercicio suelto, era la herramienta para poder sumar estas fracciones sin números enormes.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto es $\dfrac{4}{y}+\dfrac{3}{y}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $\dfrac{7}{y}$ | — |
| 　 | `trap` | $\dfrac{7}{2y}$ | `suma_numeradores_y_denominadores` |
| 　 | `sq` | $\dfrac{7}{y^{2}}$ | `suma_numeradores_y_denominadores` |
| 　 | `twelve` | $\dfrac{12}{y}$ | `multiplica_en_vez_de_sumar` |

Escalera de pistas:
1. ¿Son iguales los dos denominadores?
2. Si lo son, solo se suman los de arriba.
3. El denominador se copia tal cual.

**E2**

Suma $\dfrac{1}{3}+\dfrac{1}{4}$ y escribe el resultado como fracción, así: 5/12. No dejes espacios.

Respuesta: `7/12`

Escalera de pistas:
1. Los trozos no son del mismo tamaño: hace falta un reparto común.
2. Con doceavos: 4/12 y 3/12.
3. 4 + 3 = 7, y el denominador es 12.

**E3**

¿Cuánto es $\dfrac{7a}{8}-\dfrac{3a}{8}$, ya simplificado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $\dfrac{a}{2}$ | — |
| 　 | `unsimplified` | $\dfrac{4a}{8}$… pero aún se simplifica | `habito_deja_el_resultado_sin_simplificar` |
| 　 | `trap` | $\dfrac{4a}{0}$ | `resta_los_denominadores` |
| 　 | `wrong` | $\dfrac{4a}{16}$ | `suma_numeradores_y_denominadores` |

Escalera de pistas:
1. Mismo denominador: resta arriba y copia abajo.
2. Queda 4a/8.
3. 4 y 8 se dividen los dos entre 4.

**E4**

Un escriba anota $\dfrac{1}{2}+\dfrac{1}{5}=\dfrac{2}{7}$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `common` | Sumó arriba y abajo sin llevarlas a un denominador común: es $\dfrac{7}{10}$ | — |
| 　 | `num` | Sumó mal los numeradores | `suma_numeradores_y_denominadores` |
| 　 | `op` | La operación no era una suma | `confunde_la_operacion_dictada` |
| 　 | `none` | No hay error | `suma_numeradores_y_denominadores` |

Escalera de pistas:
1. Medio caudal ya es más que dos séptimos.
2. Los trozos no son del mismo tamaño.
3. Con décimos: 5/10 y 2/10.

**E5**

¿Verdadera o falsa? «Para sumar dos fracciones se suman los numeradores entre sí y los denominadores entre sí.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: $\dfrac{2}{5}+\dfrac{1}{5}$ sería $\dfrac{3}{10}$, menos que lo que ya había | — |
| 　 | `true` | Verdadera: se opera arriba con arriba y abajo con abajo | `suma_numeradores_y_denominadores` |
| 　 | `true_same` | Verdadera cuando los denominadores son iguales | `suma_numeradores_y_denominadores` |
| 　 | `false_never` | Falsa: los numeradores tampoco se suman nunca | `sobregeneraliza_suma_de_fracciones_algebraicas` |

Escalera de pistas:
1. Juntar agua no puede dar menos agua.
2. 2/5 son 0,4 y 3/10 son 0,3.
3. El denominador nombra el trozo; no se suma.

**E6**

Selecciona TODAS las sumas que se pueden hacer sin cambiar ningún denominador.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $\dfrac{2}{x}+\dfrac{5}{x}$ | — |
| 　 | `b` | $\dfrac{1}{3}+\dfrac{1}{5}$ | — |
| ✅ | `c` | $\dfrac{3a}{7}-\dfrac{a}{7}$ | — |
| 　 | `d` | $\dfrac{1}{x}+\dfrac{1}{y}$ | — |

Escalera de pistas:
1. Compara los dos denominadores de cada suma.
2. Si son idénticos, se suma directo.
3. x e y son denominadores distintos aunque los dos sean letras.

**E7**

Dos acequias riegan la misma tabla: una toma 5c partes de un caudal repartido en 12 y la otra, 3c partes. Con c = 3, ¿cuántas partes de 12 toman entre las dos?

Respuesta: `24`

Escalera de pistas:
1. Mismo denominador: suma los numeradores.
2. 5c + 3c = 8c.
3. Con c = 3: 8 · 3 = …


### A9. Cierre

*¿Se puede sumar directamente?* — **Qué hay que mirar antes de juntar dos fracciones**

La primera pregunta nunca es cuánto suman, sino si los trozos son del mismo tamaño. Y la última, si el resultado ya está en su forma más corta.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Se suman los de arriba y el de abajo se copia. Es el caso focal. |
|  | ✅ | Restar cuenta trozos igual que sumar: el denominador tampoco se toca. |
|  | ~ (ámbar) | La suma salió bien y aun así falta un paso. Terminar no es lo mismo que sumar. |
|  | ✗ | Hay que repartirlo todo en trozos del mismo tamaño antes de contar. |
|  | ✗ | Dos letras distintas son dos repartos distintos. El común es su producto. |
|  | ✗ | Aquí el denominador común no pinta nada: multiplicar tiene otra regla. Es lo de la era. |

La tercera fila es la que se olvida cuando ya se sabe la regla: el resultado correcto puede seguir sin estar terminado. La sexta marca el límite de esta sala — en cuanto la operación es un producto, buscar denominador común deja de tener sentido, y eso se ve en la era de trilla.

#### Pregunta de abstracción

¿Qué comparten los tres registros de riego trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `same_size` | En los tres hay que asegurarse de que los trozos son del mismo tamaño antes de contar | — |
| 　 | `roles` | En los tres el número de arriba cuenta y el de abajo nombra | — |
| 　 | `both_sum` | En los tres se suman los cuatro números que aparecen | — |
| 　 | `done` | En los tres el resultado ya queda simplificado al sumar | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas partes de 15 salen en total?
¿Cuántas partes de 15 salen en total?

Respuesta: `30`

Escalera de pistas:
1. Los dos denominadores son 15: no se tocan.
2. 7n + 3n = 10n.
3. Con n = 3: 10 · 3 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otro turno de riego. Sin nota.

- **Mejoró:** Avance: ya copias el denominador en vez de sumarlo.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo qué trabajo hace cada uno de los dos números de una fracción.

**PD1**

¿Cuánto es $\dfrac{3}{8}+\dfrac{4}{8}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `seven8` | $\dfrac{7}{8}$ | — |
| 　 | `seven16` | $\dfrac{7}{16}$ | `suma_numeradores_y_denominadores` |
| 　 | `twelve` | $\dfrac{12}{8}$ | `multiplica_en_vez_de_sumar` |

**PD2**

Un ramal lleva 5 partes de un caudal repartido en 9 y otro lleva 2. ¿Cuántas partes de 9 llevan entre los dos?

Respuesta: `7`

**PD3**

¿Se pueden sumar $\dfrac{1}{3}$ y $\dfrac{1}{4}$ sumando los numeradores?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: las partes no son del mismo tamaño | — |
| 　 | `yes` | Sí: da $\dfrac{2}{7}$ | `suma_numeradores_y_denominadores` |
| 　 | `yes_after` | Sí, y luego se simplifica | `suma_numeradores_y_denominadores` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-F02-SUMA-D1` | `five14` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-D1` | `six7` | `multiplica_en_vez_de_sumar` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-D3` | `yes` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-D3` | `yes_big` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E1` | `trap` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E1` | `sq` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E1` | `twelve` | `multiplica_en_vez_de_sumar` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E3` | `unsimplified` | `habito_deja_el_resultado_sin_simplificar` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E3` | `trap` | `resta_los_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E3` | `wrong` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E4` | `num` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E4` | `op` | `confunde_la_operacion_dictada` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E4` | `none` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E5` | `true` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E5` | `true_same` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-E5` | `false_never` | `sobregeneraliza_suma_de_fracciones_algebraicas` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-PD1` | `seven16` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-PD1` | `twelve` | `multiplica_en_vez_de_sumar` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-PD3` | `yes` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |
| `ALG-N1-F02-SUMA-PD3` | `yes_after` | `suma_numeradores_y_denominadores` | Mira primero si los denominadores son iguales; si lo son, no los toques. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
