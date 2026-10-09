# Nodo: Tachar lo que se repite solo vale si multiplica a todo — ALG-N1-F01-SIMPLIFICAR

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-F01-SIMPLIFICAR` |
| `concept_slug` | `fracciones_algebraicas` |
| Error focal | `cancelacion_en_suma` |
| Sala / edificio | La parcela partida |
| Guía | Tabiry |
| Entra después de | `ALG-N1-O04-COCIENTE` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La parcela partida · Simplificación

**Título:** Tachar lo que se repite solo vale si multiplica a todo

El agua ha borrado los linderos y hay que repartir de nuevo. Aquí la barra de fracción no es un adorno: es una división que espera a saber entre cuántos. Y hay una tachadura que parece legal y no lo es.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de pisar el barro. Sin nota.

**D1**

Una franja de 12 medidas se reparte entre 3 familias por igual. ¿Cuánto toca a cada una?

Respuesta: `4`

**D2**

¿Cuál es un factor común de todos los términos de $6x$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `six` | $6$ (y también $x$, y también $3$) | — |
| 　 | `plus` | No tiene: $6x$ es un solo término | `no_reconoce_factores_en_un_monomio` |
| 　 | `seven` | $7$ | `confunde_factor_con_suma` |

**D3**

¿Qué pasa si el número de familias entre las que se reparte fuera 0?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `undefined` | No hay reparto posible: dividir entre 0 no está definido | — |
| 　 | `zero` | El reparto da 0 a cada una | `denominador_cero` |
| 　 | `all` | Le toca todo a la primera | `denominador_cero` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Sobre el terreno húmedo* — **El reparto que aún no se puede calcular**

Tabiry recorre la orilla con la cuerda anudada. La crecida ha dejado una franja de tierra buena, pero este año no se sabe cuántas familias volverán: unas se quedaron río arriba y otras no han llegado.

«Tengo que dejar escrito el reparto hoy», dice Tabiry, «y el número de familias lo sabré en la próxima luna. Además la franja tampoco mide siempre lo mismo: el agua se lleva un trozo y devuelve otro.»

**Pregunta:** ¿Cómo se escribe un reparto cuando no se sabe ni cuánto hay ni entre cuántos?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Esperar a la próxima luna y calcularlo entonces | — |
| 　 | `b` | Escribir la división con letras y dejarla indicada | — |
| 　 | `c` | Repartir en partes iguales por si acaso | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos repartos que se escriben igual y se simplifican distinto**

Los dos son una barra con letras arriba. Solo uno se puede acortar, y la diferencia está en si lo que se repite multiplica a TODO el numerador.

- **Sí se simplifica** — El 3 multiplica a todo el numerador: se puede sacar y cancelar con el de abajo.
- **No se simplifica** — La x de arriba está SUMADA con el 4, no multiplicando al conjunto. No hay nada que sacar.

**Resolución:** Cancelar es dividir arriba y abajo por lo mismo, y dividir reparte sobre un producto, no sobre una suma. Por eso solo se tacha lo que multiplica al numerador entero. Si un término está sumado, tacharlo cambia el valor — y hay un número que lo demuestra en una línea.

**Definición — Fracción algebraica**

$$\dfrac{a\cdot m}{a\cdot n}=\dfrac{m}{n}\quad (a\ne 0,\ n\ne 0)$$

Una FRACCIÓN ALGEBRAICA es un cociente en el que el numerador o el denominador contienen expresiones con letras. La barra significa división, así que el denominador nunca puede valer 0. Solo se simplifican FACTORES comunes completos: los sumandos no se cancelan.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{6x}{3}` | seis equis entre tres | reparto de 6x en 3 partes iguales |
| `a\ne 0` | a distinto de cero | solo se cancela lo que no es cero |
| `n\ne 0` | denominador no nulo | restricción obligatoria: sin ella la fracción no existe |
| `\dfrac{x+4}{x}` | no simplificable | la x de arriba es un sumando, no un factor |
| `x\in\mathbb{N},\ x>0` | dominio del contexto | aquí x cuenta familias: entero y positivo |

### A5. Ejemplos resueltos

#### Cuando el divisor multiplica a todo · *resuelto*

Un canal de 8r codos de largo se abre entre 4 equipos, que hacen tramos iguales. ¿Cuánto abre cada equipo?

- El reparto es una división: 8r entre 4.
- Busco un factor que multiplique a TODO el numerador. 8r = 4 · 2r, así que el 4 está.
- Cancelo el 4 de arriba con el de abajo: queda 2r.
- Compruebo al revés: 4 · 2r = 8r ✓. Esa es la comprobación que nunca falla.
- Restricción: aquí no hace falta, el denominador es el número 4 y nunca es cero.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Qué significa exactamente «que multiplique a todo el numerador»?'}

#### Un factor que es un paréntesis entero · *resuelto*

Se necesitan 6(c + 2) cuerdas anudadas para marcar los canales, y se reparten entre 3 jornadas iguales. ¿Cuántas por jornada?

- El numerador ya viene escrito como producto: 6 por el paréntesis.
- Simplifico solo la parte numérica: 6 ÷ 3 = 2.
- El paréntesis se queda entero: 2(c + 2). No se toca lo de dentro.
- Compruebo con c = 4: arriba 6 · 6 = 36, entre 3 son 12; y 2 · 6 = 12 ✓.
- Ojo con la tentación: NO se puede cancelar el 3 con el 2 de dentro del paréntesis.

#### El aprendiz que tachó una x sumada · *TRAMPA*

El aprendiz de Tabiry entrega el reparto así: «la franja mide x + 4 y hay x familias, tacho las dos x y a cada familia le tocan 4».

- Sustituyo x = 2 en el original: (2 + 4) ÷ 2 = 6 ÷ 2 = 3.
- El aprendiz dice que siempre da 4. Con 2 familias da 3, no 4: un contraejemplo basta.
- La forma correcta se obtiene repartiendo la barra sobre cada sumando: x/x + 4/x = 1 + 4/x, y eso solo vale si x ≠ 0.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{x+4}{x}=4', 'right_latex': '\\dfrac{x+4}{x}=1+\\dfrac{4}{x}\\quad (x\\ne 0)', 'rows': [{'wrong': 'Si la x está arriba y abajo, se tacha', 'right': 'Solo si multiplica a TODO el numerador'}, {'wrong': 'Queda 4, un número fijo', 'right': 'Queda algo que depende de x: con 2 familias toca 3 y con 4 familias toca 2'}]}
**¿Por qué falla?:** Explica por qué no se puede tachar y comprueba el error tomando x = 2.


### A6. Puente — parcialmente resueltos

El reparto ya va empezado; completa los huecos.

**P1** (*falta: last*) — Simplifica $\dfrac{10m}{5}$ y evalúa el resultado para $m=7$.

- dado: $\dfrac{10m}{5}=2m$
- dado: $m=7$
- hueco `P1-b1`: $2m=$ → `14`

**P2** (*falta: middle*) — Simplifica $\dfrac{12(a+1)}{4}$ y evalúa para $a=5$.

- dado: $\text{el factor numérico común es }4$
- hueco `P2-b1`: $12\div 4=$ → `3`
- hueco `P2-b2`: $3(a+1)\ \text{con}\ a=5:$ → `18`

**P3** (*falta: statement_only*) — Solo el planteamiento: en $\dfrac{5}{x-2}$, ¿qué valor NO puede tomar $x$?

- hueco `P3-b1`: $x\ne$ → `2`


### A7. Comparación de métodos

**Dos maneras de ver la misma simplificación**

Simplifica $\dfrac{12(x+1)}{4}$. Las dos soluciones son correctas.

- **Método 1 · Simplificar el factor numérico** — 
- **Método 2 · Repartir y comprobar** — 

**Pregunta:** ¿Cuál muestra mejor por qué la simplificación es legítima?

**Insight:** El segundo. Al desarrollar se ve que el 4 divide a CADA término del numerador —12x y 12— y por eso puede salir. En cambio en (x+4)/x la x no divide al 4, y ese es exactamente el motivo de que ahí no se pueda tachar nada.

### A8. Práctica independiente (7 ítems)

**E1**

Simplifica $\dfrac{15p}{5}$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `threep` | $3p$ | — |
| 　 | `three` | $3$ | `pierde_la_parte_literal` |
| 　 | `tenp` | $10p$ | `resta_en_vez_de_dividir` |
| 　 | `p3` | $\dfrac{p}{3}$ | `invierte_el_cociente` |

Escalera de pistas:
1. 15p es 5 · 3p.
2. El 5 multiplica a todo el numerador, así que se puede cancelar.
3. Queda 3 por p.

**E2**

Simplifica $\dfrac{9(k+3)}{3}$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `correct` | $3(k+3)$ | — |
| 　 | `inside` | $9(k+1)$ | `cancela_dentro_del_parentesis` |
| 　 | `both` | $3(k+1)$ | `cancela_dentro_del_parentesis` |
| 　 | `k3` | $3k+3$ | `reparte_solo_al_primer_termino` |

Escalera de pistas:
1. El denominador se simplifica con el 9, no con lo de dentro del paréntesis.
2. El paréntesis es un factor: entra o sale entero.
3. 9 ÷ 3 = 3, y (k + 3) se queda como está.

**E3**

El reparto de una franja se escribe 8n ÷ 4, donde n es el número de parcelas por familia. Escribe la fracción ya simplificada.

Respuesta: `2n`

Escalera de pistas:
1. Busca el factor que multiplica a todo el numerador.
2. 8n = 4 · 2n.
3. Al cancelar el 4 queda el coeficiente 2 con su letra.

**E4**

Un aprendiz escribe: «$\dfrac{2y+6}{2}=y+6$». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `partial` | Dividió solo el primer término: el 6 también hay que dividirlo, y queda y + 3 | — |
| 　 | `cancel` | No se puede simplificar nada en esa fracción | `no_reconoce_factor_comun_real` |
| 　 | `coef` | 2y ÷ 2 no es y | `habito_busca_el_error_donde_no_esta` |
| 　 | `none` | No hay error | `reparte_solo_al_primer_termino` |

Escalera de pistas:
1. Comprueba con y = 4: ¿dan lo mismo los dos lados?
2. Arriba sale 14, entre 2 son 7. Y y + 6 daría 10.
3. El 2 divide a los DOS sumandos: 2y ÷ 2 = y y 6 ÷ 2 = 3.

**E5**

¿Es verdadera o falsa? «$\dfrac{x+4}{x}=4$ para cualquier $x$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: la x está sumada, no multiplicando; no se puede tachar | — |
| 　 | `true` | Verdadera: la x de arriba y la de abajo se cancelan | `cancelacion_en_suma` |
| 　 | `true_not0` | Verdadera siempre que x ≠ 0 | `cancelacion_en_suma` |
| 　 | `false_five` | Falsa: en realidad da $5$ | `cancelacion_en_suma` |

Escalera de pistas:
1. Para tumbar un «para cualquier x» basta UN valor.
2. Prueba con x = 2.
3. (2 + 4) ÷ 2 = 3, y 3 no es 4.

**E6**

Selecciona TODAS las fracciones que SÍ se pueden simplificar.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $\dfrac{4t}{2}$ | — |
| 　 | `b` | $\dfrac{t+2}{2}$ | — |
| ✅ | `c` | $\dfrac{5(t+1)}{5}$ | — |
| 　 | `d` | $\dfrac{t+5}{t}$ | — |

Escalera de pistas:
1. Pregunta en cada una: ¿lo de abajo multiplica al numerador ENTERO?
2. 4t = 2 · 2t y 5(t+1) ya viene escrito como producto.
3. En t + 2 y en t + 5 hay sumas: el denominador no divide a los dos sumandos.

**E7**

El agua de un canal se reparte por turnos: 20w medidas entre 5 turnos iguales, donde w es la anchura de la compuerta. Si w = 3, ¿cuántas medidas corresponden a cada turno?

Respuesta: `12`

Escalera de pistas:
1. Simplifica antes de sustituir.
2. 20w ÷ 5 = 4w.
3. 4 · 3 = …


### A9. Cierre

*¿Se puede tachar?* — **Qué decide si una fracción se simplifica**

Que un símbolo aparezca arriba y abajo no da permiso para nada. La pregunta es si multiplica al numerador entero.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | 6x = 3 · 2x: el 3 multiplica a todo lo de arriba. |
|  | ✗ | Con x = 2 da 3, no 4. Es la trampa de este nodo. |
|  | ✅ | Se simplifica el 6 con el 3; lo de dentro del paréntesis no se toca. |
|  | ✅ | Aquí sí: el 2 divide a los DOS sumandos. Hay suma, pero también factor común. |
|  | ✗ | No se acorta, pero sí hay que declarar la restricción: en x = 2 no existe. |
|  | ~ (ámbar) | No se simplifica, pero sí se puede reescribir repartiendo el denominador entre los sumandos. |

Dos filas conviven a propósito: (x+4)/x no se simplifica y aun así se puede reescribir. «No se puede tachar» nunca significa «no se puede hacer nada» — significa que la operación que ibas a hacer no era la correcta.

#### Pregunta de abstracción

¿Qué comparten los tres repartos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `division` | En los tres la barra significa una división | — |
| 　 | `factor` | En los tres hay que mirar si lo repetido es factor o sumando | — |
| 　 | `always` | En los tres se puede tachar lo que se repite arriba y abajo | — |
| 　 | `number` | En los tres el resultado es un número que no depende de la letra | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas medidas recibe cada familia?
¿Cuántas medidas recibe cada familia?

Respuesta: `15`

Escalera de pistas:
1. Busca el factor que multiplica a todo el numerador.
2. 18f = 6 · 3f, así que la fracción vale 3f.
3. 3 · 5 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otro reparto. Sin nota.

- **Mejoró:** Avance: ya distingues un factor de un sumando antes de tachar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué un sumando no se puede cancelar.

**PD1**

Simplifica $\dfrac{9q}{3}$ y evalúa el resultado para $q=8$.

Respuesta: `24`

**PD2**

¿Cuánto vale $\dfrac{3y+9}{3}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `y3` | $y+3$ | — |
| 　 | `y9` | $y+9$ | `reparte_solo_al_primer_termino` |
| 　 | `nine` | $9$ | `cancelacion_en_suma` |

**PD3**

En $\dfrac{7}{x-5}$, ¿qué valor no puede tomar $x$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `five` | $x=5$ | — |
| 　 | `zero` | $x=0$ | `confunde_x_cero_con_denominador_cero` |
| 　 | `seven` | $x=7$ | `mira_el_numerador_en_vez_del_denominador` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-F01-SIMPLIFICAR-D2` | `plus` | `no_reconoce_factores_en_un_monomio` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-D2` | `seven` | `confunde_factor_con_suma` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-D3` | `zero` | `denominador_cero` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-D3` | `all` | `denominador_cero` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E1` | `three` | `pierde_la_parte_literal` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E1` | `tenp` | `resta_en_vez_de_dividir` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E1` | `p3` | `invierte_el_cociente` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E2` | `inside` | `cancela_dentro_del_parentesis` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E2` | `both` | `cancela_dentro_del_parentesis` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E2` | `k3` | `reparte_solo_al_primer_termino` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E4` | `cancel` | `no_reconoce_factor_comun_real` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E4` | `coef` | `habito_busca_el_error_donde_no_esta` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E4` | `none` | `reparte_solo_al_primer_termino` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E5` | `true` | `cancelacion_en_suma` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E5` | `true_not0` | `cancelacion_en_suma` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-E5` | `false_five` | `cancelacion_en_suma` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-PD2` | `y9` | `reparte_solo_al_primer_termino` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-PD2` | `nine` | `cancelacion_en_suma` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-PD3` | `zero` | `confunde_x_cero_con_denominador_cero` | Antes de tachar, comprueba si eso multiplica al numerador entero. |
| `ALG-N1-F01-SIMPLIFICAR-PD3` | `seven` | `mira_el_numerador_en_vez_del_denominador` | Antes de tachar, comprueba si eso multiplica al numerador entero. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
