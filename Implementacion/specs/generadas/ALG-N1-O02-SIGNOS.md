# Nodo: El menos de fuera entra hasta el último término — ALG-N1-O02-SIGNOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-O02-SIGNOS` |
| `concept_slug` | `signos_y_parentesis` |
| Error focal | `el_menos_solo_afecta_al_primero` |
| Sala / edificio | El patio de aparejos |
| Guía | Bakenra |
| Entra después de | `ALG-N1-O01-SEMEJANTES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El patio de aparejos · Signos y paréntesis

**Título:** El menos de fuera entra hasta el último término

Ya sabes juntar lo que es del mismo tipo. Ahora aparecen devoluciones: partidas enteras que se restan de golpe. Un paréntesis con un menos delante no es un adorno — es una instrucción que afecta a todo lo que hay dentro.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar al patio. Sin nota.

**D1**

¿Cuánto es 10 − (4 + 3)?

Respuesta: `3`

**D2**

¿A qué equivale $-(x+5)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | $-x-5$ | — |
| 　 | `first` | $-x+5$ | `el_menos_solo_afecta_al_primero` |
| 　 | `none` | $x-5$ | `pierde_el_signo_del_termino` |

**D3**

¿Cuánto es 7 − (2 − 5)?

Respuesta: `10`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el patio de aparejos* — **El inventario que salía siempre de más**

El patio guarda las poleas, las sogas y los contrapesos. Cada mañana sale un vale con lo que se entrega y cada tarde vuelve otro con lo que se devuelve.

Bakenra sostiene un vale de devolución: dos poleas y tres contrapesos.

«El escriba anotó que salían ocho poleas y volvían dos, y hasta ahí bien. Pero los tres contrapesos que también volvían los sumó en vez de restarlos. Llevamos un mes creyendo que tenemos seis contrapesos más de los que hay, y hoy la cuadrilla de la cara norte se ha quedado sin aparejo.»

**Pregunta:** Cuando se resta una partida entera, ¿a qué parte le llega el menos?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Al primer término de la partida; el resto se copia igual | — |
| 　 | `b` | A todos los términos de la partida | — |
| 　 | `c` | A ninguno: el paréntesis se borra y ya está | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El mismo paréntesis, dos signos delante**

Los dos registros se quitan el paréntesis. Solo en uno cambia algo dentro.

- **Con más delante** — Los signos de dentro se quedan tal cual. El paréntesis no hacía nada.
- **Con menos delante** — Los DOS signos de dentro se dan la vuelta. Devolver sogas no puede aumentar las sogas.

**Resolución:** El paréntesis agrupa una partida entera. Con un más delante, agrupar da igual. Con un menos delante, lo que se resta es la partida COMPLETA, así que cada uno de sus términos entra restando. Escrito con símbolos: el menos de fuera es un −1 que multiplica todo lo de dentro.

**Definición — Quitar un paréntesis**

$$-(a+b)=-a-b\qquad -(a-b)=-a+b$$

Un paréntesis precedido de + se borra sin tocar nada. Un paréntesis precedido de − se borra CAMBIANDO EL SIGNO de todos sus términos, sin excepción: los que sumaban pasan a restar y los que restaban pasan a sumar. Equivale a multiplicar por −1. Si delante hay un número, no basta con los signos: hay que repartir ese factor.

| Símbolo | Se lee | Significa |
|---|---|---|
| `+(2p+3)` | más, abre, dos pe más tres | se borra el paréntesis y ya |
| `-(2p+3)=-2p-3` | menos, abre… | los dos términos cambian de signo |
| `-(2p-3)=-2p+3` | menos, abre… | el que restaba pasa a sumar |
| `-(-5)=+5` | menos, menos cinco | restar una devolución es sumar |
| `-1\cdot(a+b)` | menos uno por… | de dónde sale la regla: es la distributiva |

### A5. Ejemplos resueltos

#### Restar una partida entera · *resuelto*

Por la mañana salen 9 sogas y 6 contrapesos. Por la tarde se devuelven 4 sogas y 6 contrapesos. ¿Qué queda fuera del patio?

- Lo devuelto se resta entero: por eso va agrupado en un paréntesis.
- Quito el primer paréntesis, que no lleva menos delante: 9s + 6 − (4s + 6).
- Quito el segundo cambiando los DOS signos: 9s + 6 − 4s − 6.
- Junto semejantes: 9s − 4s = 5s, y 6 − 6 = 0.
- Queda 5s. Los contrapesos volvieron todos, así que no queda ninguno fuera ✓.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué el 6 de dentro del segundo paréntesis pasa a restar, si estaba sumando?'}

#### Cuando dentro del paréntesis ya hay una resta · *resuelto*

El inventario del patio marca 12 aparejos. Se descuenta un vale que dice «3 poleas menos 5 que nunca salieron». ¿Cuántos aparejos hay?

- El menos de fuera afecta a los dos términos de dentro, sean del signo que sean.
- El 3p sumaba dentro: pasa a restar → −3p.
- El −5 restaba dentro: pasa a sumar → +5.
- Queda 12 − 3p + 5 = 17 − 3p.
- Compruebo con p = 2: el original da 12 − (6 − 5) = 11, y 17 − 6 = 11 ✓.

#### El escriba que se quedó a mitad del paréntesis · *TRAMPA*

Vuelve el vale de la apertura: salen 8 poleas y 3 contrapesos, y se devuelven 2 poleas y 3 contrapesos. El escriba anota 8p − 2p + 3.

- Sustituyo p = 10 en el original: (83) − (23) = 60.
- Sustituyo en el registro del escriba: 6 · 10 + 6 = 66. Sobran 6.
- Regla para no volver a caer: cuenta los términos de dentro y cámbiale el signo a todos, uno por uno.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '8p+3-2p+3=6p+6', 'right_latex': '8p+3-2p-3=6p', 'rows': [{'wrong': 'El menos se aplica al 2p y el 3 se copia', 'right': 'El menos se aplica a los dos: −2p y −3'}, {'wrong': 'Quedan 6 contrapesos fuera', 'right': '3 − 3 = 0: no queda ninguno fuera'}]}
**¿Por qué falla?:** Explica a qué términos llega el menos de fuera y comprueba el error sustituyendo p = 10.


### A6. Puente — parcialmente resueltos

El vale va empezado; completa los huecos.

**P1** (*falta: last*) — Quita el paréntesis y reduce: $7s-(2s+4)$.

- dado: $7s-2s-4$
- hueco `P1-b1`: $\text{coeficiente de }s:\ 7-2=$ → `5`

**P2** (*falta: middle*) — Reduce $10-(3c-6)$ y evalúa con $c=2$.

- dado: $10-3c+6$
- hueco `P2-b1`: $10+6=$ → `16`
- hueco `P2-b2`: $16-3\cdot 2=$ → `10`

**P3** (*falta: statement_only*) — Solo el planteamiento: salen 15 sogas y se devuelve un vale de $(4s-9)$. Reduce y evalúa con $s=3$.

- hueco `P3-b1`: $15s-(4s-9)\ \text{con}\ s=3:$ → `42`


### A7. Comparación de métodos

**Dos maneras de quitar el paréntesis**

$9c-(4c+2-7d)$. Tres términos dentro: es donde se pierde la gente.

- **Método 1 · Cambiar los signos de un vistazo** — 
- **Método 2 · Escribir el −1 y repartirlo** — 

**Pregunta:** ¿Cuál elegirías con un paréntesis de cuatro o cinco términos?

**Insight:** El segundo. No porque el primero esté mal —dan lo mismo—, sino porque el primero depende de que no se te escape ninguno, y con cuatro términos se escapa. Escribir el −1 convierte «acordarse» en «multiplicar», y multiplicar se hace término a término sin depender de la memoria. Esa idea de repartir un factor por dentro del paréntesis es la que vas a usar en el taller de cinceles.

### A8. Práctica independiente (7 ítems)

**E1**

Reduce $8p-(3p+2)$.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $5p-2$ | — |
| 　 | `half` | $5p+2$ | `el_menos_solo_afecta_al_primero` |
| 　 | `all` | $11p+2$ | `ignora_el_signo_de_fuera` |
| 　 | `glue` | $3p$ | `combina_no_semejantes` |

Escalera de pistas:
1. Dentro del paréntesis hay dos términos. Cuéntalos.
2. A los dos hay que cambiarles el signo.
3. Queda 8p − 3p − 2.

**E2**

Reduce $14-(5c-3)$ y escribe el resultado. Usa el orden en que quede y no dejes espacios.

Respuesta: `17-5c`
También válidas: `-5c+17`

Escalera de pistas:
1. El −3 de dentro pasa a sumar.
2. Queda 14 − 5c + 3.
3. Junta las constantes: 14 + 3 = 17.

**E3**

El patio tiene $20$ aparejos y se descuenta el vale $(6a-9)$. Con $a=2$, ¿cuántos aparejos quedan?

Respuesta: `17`

Escalera de pistas:
1. Primero quita el paréntesis: 20 − 6a + 9.
2. Eso es 29 − 6a.
3. 29 − 12 = …

**E4**

Un escriba escribe $10s-(2s-4)=8s-4$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sign` | El $-4$ de dentro pasa a sumar: queda $8s+4$ | — |
| 　 | `coef` | Restó mal los coeficientes de s | `pierde_el_signo_del_termino` |
| 　 | `like` | Juntó términos que no eran semejantes | `combina_no_semejantes` |
| 　 | `none` | No hay error | `el_menos_solo_afecta_al_primero` |

Escalera de pistas:
1. Los coeficientes de s están bien: 10 − 2 = 8.
2. Mira qué le pasó al segundo término de dentro.
3. Restar algo que ya restaba lo convierte en suma.

**E5**

¿Verdadera o falsa? «El menos que va delante de un paréntesis solo cambia el signo del primer término de dentro.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: $-(2p+3)$ es $-2p-3$, con los dos cambiados | — |
| 　 | `true` | Verdadera: por eso está pegado al primero | `el_menos_solo_afecta_al_primero` |
| 　 | `true_two` | Verdadera si dentro hay más de dos términos | `el_menos_solo_afecta_al_primero` |
| 　 | `false_none` | Falsa: el menos no cambia ningún signo, solo borra el paréntesis | `ignora_el_signo_de_fuera` |

Escalera de pistas:
1. Prueba con números: 10 − (4 + 3).
2. El resultado es 3, no 10 − 4 + 3 = 9.
3. El menos llegó también al 3.

**E6**

Selecciona TODOS los paréntesis que se pueden borrar sin tocar ningún signo.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $5c+(2c+7)$ | — |
| 　 | `b` | $5c-(2c+7)$ | — |
| ✅ | `c` | $(2c+7)+5c$ | — |
| 　 | `d` | $5c-(2c-7)$ | — |

Escalera de pistas:
1. Mira qué signo hay JUSTO delante de cada paréntesis.
2. Un paréntesis sin nada delante es como si tuviera un más.
3. Los dos que llevan menos delante obligan a cambiar signos.

**E7**

El patio anota 30 sogas. Por la mañana sale un vale de (7s + 4) y por la tarde vuelve uno de (2s − 4). Con s = 3, ¿cuántas sogas quedan anotadas?

Respuesta: `7`

Escalera de pistas:
1. El primer paréntesis lleva menos delante; el segundo, más.
2. Queda 30 − 7s − 4 + 2s − 4 = 22 − 5s.
3. 22 − 15 = …


### A9. Cierre

*¿Se puede borrar el paréntesis tal cual?* — **Qué manda el signo que va delante**

El paréntesis no dice nada por sí solo. Lo que decide es el símbolo que tiene pegado por fuera, a su izquierda.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Un paréntesis suelto agrupa y no manda. Se borra sin más. |
|  | ✅ | Sumar una partida entera es sumar cada cosa: nada cambia de signo. |
|  | ✗ | Los dos términos se dan la vuelta. Es el caso focal. |
|  | ✗ | El que restaba pasa a sumar. Restar una devolución devuelve. |
|  | ✗ | El mismo caso reducido al mínimo: sigue habiendo un cambio de signo. |
|  | ~ (ámbar) | Los paréntesis sí se quitan, pero no gratis: hay que repartir el 4 a cada término. |

Las cinco primeras filas son la misma idea vista de cinco maneras: lo de fuera entra hasta el final. La sexta la lleva un paso más lejos — si en vez de un menos hay un número, tampoco basta con copiar: hay que multiplicar por dentro. Ese reparto es el trabajo del taller de cinceles.

#### Pregunta de abstracción

¿Qué comparten los tres vales trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `all_terms` | En los tres el signo de fuera actúa sobre todos los términos de dentro | — |
| 　 | `then_like` | En los tres hay que quitar el paréntesis antes de poder juntar semejantes | — |
| 　 | `first_only` | En los tres basta con cambiar el signo del primer término | — |
| 　 | `erase` | En los tres el paréntesis se borra sin consecuencias | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos contrapesos quedan?
¿Cuántos contrapesos quedan?

Respuesta: `28`

Escalera de pistas:
1. El primer paréntesis lleva menos delante; el segundo, más.
2. Los términos en k se van: −9k + 9k = 0.
3. 40 − 6 − 6 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros vales. Sin nota.

- **Mejoró:** Avance: el menos de fuera ya te llega hasta el último término.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el paréntesis con menos delante, término por término.

**PD1**

¿Cuánto es 12 − (5 + 4)?

Respuesta: `3`

**PD2**

¿A qué equivale $-(y+7)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | $-y-7$ | — |
| 　 | `first` | $-y+7$ | `el_menos_solo_afecta_al_primero` |
| 　 | `none` | $y-7$ | `pierde_el_signo_del_termino` |

**PD3**

¿Cuánto es 9 − (3 − 6)?

Respuesta: `12`

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-O02-SIGNOS-D2` | `first` | `el_menos_solo_afecta_al_primero` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-D2` | `none` | `pierde_el_signo_del_termino` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E1` | `half` | `el_menos_solo_afecta_al_primero` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E1` | `all` | `ignora_el_signo_de_fuera` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E1` | `glue` | `combina_no_semejantes` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E4` | `coef` | `pierde_el_signo_del_termino` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E4` | `like` | `combina_no_semejantes` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E4` | `none` | `el_menos_solo_afecta_al_primero` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E5` | `true` | `el_menos_solo_afecta_al_primero` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E5` | `true_two` | `el_menos_solo_afecta_al_primero` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-E5` | `false_none` | `ignora_el_signo_de_fuera` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-PD2` | `first` | `el_menos_solo_afecta_al_primero` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |
| `ALG-N1-O02-SIGNOS-PD2` | `none` | `pierde_el_signo_del_termino` | Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
