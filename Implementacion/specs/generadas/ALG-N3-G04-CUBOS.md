# Nodo: La suma de cubos sí se abre, y no en las piezas que esperas — ALG-N3-G04-CUBOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N3-G04-CUBOS` |
| `concept_slug` | `suma_y_diferencia_de_cubos` |
| Error focal | `suma_de_cubos_es_cubo_de_binomio` |
| Sala / edificio | La bodega de los toneles |
| Guía | Salim |
| Entra después de | `ALG-N3-G03-TRINOMIO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La bodega de los toneles · Suma y diferencia de cubos

**Título:** La suma de cubos sí se abre, y no en las piezas que esperas

En el cotejo de huellas aprendiste que una suma de cuadrados no sale de ningún troquel. Aquí viene el contraste: una suma de CUBOS sí se abre. Pero no en dos binomios, y no en lo que se le parece.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de bajar a la bodega. Sin nota.

**D1**

¿Cuál es la raíz cúbica de 27?

Respuesta: `3`

**D2**

¿A qué equivale $(x+2)^{3}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `four` | $x^{3}+6x^{2}+12x+8$ | — |
| 　 | `two` | $x^{3}+8$ | `binomio_cubo_falta_terminos` |
| 　 | `three` | $x^{3}+6x+8$ | `usa_los_coeficientes_del_cuadrado_en_el_cubo` |

**D3**

¿Cuánto es $2^{3}$?

Respuesta: `8`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la bodega de los toneles* — **El arqueo que no cuadró**

Abajo, en la bodega, se guardan toneles. Cada tonel se mide por su arqueo: el volumen que cabe dentro, y ese volumen es siempre el cubo de una medida.

Salim baja con una lámpara y señala una anotación en la pared:

«Llegó una remesa marcada $x^{3}+8$. El mozo vio un cubo y un ocho, que también es un cubo, y anotó que venía de un solo tonel de medida $x+2$: escribió $(x+2)^{3}$.»

«Probamos con $x=1$. La remesa arqueaba nueve; su tonel arqueaba veintisiete. Sobraban dieciocho de un vino que no existía.»

**Pregunta:** Si $x^{3}$ y $8$ son los dos cubos, ¿por qué $x^{3}+8$ no es lo mismo que $(x+2)^{3}$?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `capas` | Porque al cubo de un binomio le salen capas de en medio | — |
| 　 | `igual` | Son lo mismo: se puede repartir el exponente | — |
| 　 | `nada` | Porque una suma de cubos no se puede abrir de ninguna forma | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Un binomio y un trinomio, no dos binomios**

Todos los troqueles anteriores dejaban dos binomios o un binomio al cuadrado. Este deja piezas de distinto tamaño.

- **No es el cubo de un binomio** — El cubo de un binomio deja cuatro capas. La remesa solo tenía dos términos: no puede ser eso.
- **Sí es una suma de cubos** — Estampando: x·x² − 2x² + 4x + 2x² − 4x + 8. Todo lo de en medio se anula y quedan x³ y 8.

**Resolución:** La suma de cubos se abre en un binomio por un trinomio. El binomio lleva la SUMA de las raíces cúbicas; el trinomio lleva sus cuadrados y el producto con el signo CONTRARIO al del binomio. Y ese trinomio no es cuadrado perfecto: le falta el doble en el término del medio.

**Definición — Suma y diferencia de cubos**

$$a^{3}+b^{3} = (a+b)(a^{2}-ab+b^{2}) \qquad a^{3}-b^{3} = (a-b)(a^{2}+ab+b^{2})$$

Un binomio se abre por este molde si sus dos términos son CUBOS exactos. El resultado es un binomio por un trinomio: el binomio repite el signo de la remesa; el trinomio lleva el cuadrado del primero, el producto de los dos con el signo CONTRARIO, y el cuadrado del segundo.

Regla para el signo: «el mismo signo, el contrario, y siempre más».

| Símbolo | Se lee | Significa |
|---|---|---|
| `a^{3}+b^{3}=(a+b)(a^{2}-ab+b^{2})` | a al cubo más b al cubo | suma de cubos: binomio que suma, trinomio con el medio restando |
| `a^{3}-b^{3}=(a-b)(a^{2}+ab+b^{2})` | a al cubo menos b al cubo | diferencia de cubos: binomio que resta, trinomio con el medio sumando |
| `a^{2}-ab+b^{2}` | a cuadrado menos a b más b cuadrado | no es cuadrado perfecto: le falta el doble en el término del medio |
| `(a+b)^{3}` | a más b, al cubo | otra cosa: cuatro términos, y no se factoriza porque ya es un producto |
| `\sqrt[3]{8x^{6}}=2x^{2}` | raíz cúbica de ocho equis a la sexta | raíz del coeficiente, exponente entre 3 |

### A5. Ejemplos resueltos

#### Las dos piezas, una por una · *resuelto*

Salim arquea una remesa marcada $8x^{3}+27$. ¿En qué toneles se abre?

- ¿Son cubos exactos? 8x³ = (2x)³ y 27 = 3³. Sí.
- Raíces cúbicas: 2x y 3.
- Binomio: la suma de las raíces, con el mismo signo de la remesa → (2x + 3).
- Trinomio: (2x)² − (2x)(3) + 3² = 4x² − 6x + 9. El medio con el signo contrario.
- Queda (2x + 3)(4x² − 6x + 9). Compruebo con x = 0: 27 = 3 · 9 ✓.

**Autoexplicación (focal):** {'step_index': 3, 'prompt': '¿Por qué el término del medio del trinomio no lleva un 2 delante, si en el cuadrado de un binomio sí lo llevaba?'}

#### Los dos signos se cambian a la vez · *resuelto*

Otra remesa: $64x^{3}-125$. Todo igual, con los signos volteados.

- Cubos exactos: 64x³ = (4x)³ y 125 = 5³.
- Binomio: (4x − 5), repitiendo el signo de la remesa.
- Trinomio: (4x)² + (4x)(5) + 5² = 16x² + 20x + 25, con el medio sumando.
- Queda (4x − 5)(16x² + 20x + 25).
- Fíjate: el trinomio SIEMPRE acaba en más, tanto en la suma como en la diferencia.

#### El mozo que arqueó un tonel de más · *TRAMPA*

Vuelve la remesa de la apertura. El mozo anota $x^{3}+1$ así:

- Con x = 2: x³ + 1 = 9. Y (x + 1)³ = 27. Se separan en 18.
- La correcta: (2 + 1)(4 − 2 + 1) = 3 · 3 = 9 ✓.
- Contar términos es la prueba rápida: la remesa tiene dos, un cubo de binomio tendría cuatro.
- Regla para no volver a caer: suma de cubos → binomio POR trinomio. Nunca un solo paréntesis.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': 'x^{3}+1=(x+1)^{3}', 'right_latex': 'x^{3}+1=(x+1)(x^{2}-x+1)', 'rows': [{'wrong': 'Dos cubos sumando salen de un binomio al cubo', 'right': 'Salen de un binomio por un trinomio'}, {'wrong': '(x+1)³ tiene dos términos', 'right': '(x+1)³ = x³ + 3x² + 3x + 1: tiene cuatro'}]}
**¿Por qué falla?:** Comprueba con $x=2$ las dos expresiones y di cuánto se separan. Después estampa la factorización correcta.


### A6. Puente — parcialmente resueltos

El arqueo va empezado; completa los huecos.

**P1** (*falta: last*) — Factoriza $x^{3}+27$.

- dado: $\sqrt[3]{x^{3}}=x,\quad \sqrt[3]{27}=3$
- dado: $\text{binomio}:(x+3)$
- hueco `P1-b1`: $\text{coeficiente del medio del trinomio, sin signo}=$ → `3`

**P2** (*falta: middle*) — Factoriza $8x^{3}-27$.

- dado: $(2x)^{3}-3^{3}$
- hueco `P2-b1`: $\text{primer término del trinomio}: (2x)^{2}\ \text{, coeficiente}=$ → `4`
- hueco `P2-b2`: $\text{medio}: (2x)(3)\ \text{, coeficiente}=$ → `6`

**P3** (*falta: statement_only*) — Solo el planteamiento: $x^{6}-64$. Se puede abrir por dos caminos — di cuántos factores quedan si empiezas por diferencia de cuadrados.

- hueco `P3-b1`: $\text{número de factores finales}=$ → `4`


### A7. Comparación de métodos

**Dos caminos para abrir la misma remesa**

$x^{6}-64$. Es a la vez diferencia de cuadrados y diferencia de cubos.

- **Método 1 · Empezar por cuadrados** — 
- **Método 2 · Empezar por cubos** — 

**Pregunta:** ¿Por qué conviene empezar por la diferencia de cuadrados?

**Insight:** Porque parte en trozos más pequeños desde el principio, y cada trozo cae en un molde conocido. Empezando por cubos se llega a un trinomio de grado 4 que todavía se puede abrir, y hay que darse cuenta. Las dos rutas dan el mismo resultado —la factorización completa es única— pero una llega antes al final. Cuando un fardo admite dos moldes, empieza por el que deje los trozos más chicos.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es la factorización de $x^{3}+8$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $(x+2)(x^{2}-2x+4)$ | — |
| 　 | `cube` | $(x+2)^{3}$ | `suma_de_cubos_es_cubo_de_binomio` |
| 　 | `conj` | $(x+2)(x-2)$ | `aplica_diferencia_de_cuadrados_a_los_cubos` |
| 　 | `sq` | $(x+2)(x^{2}+2x+4)$ | `no_cambia_el_signo_del_medio_del_trinomio` |

Escalera de pistas:
1. Las raíces cúbicas son x y 2.
2. El binomio repite el signo de la remesa.
3. En el trinomio, el término del medio lleva el signo CONTRARIO.

**E2**

¿Cuál es la raíz cúbica de $8x^{6}$? Escribe solo el coeficiente.

Respuesta: `2`

Escalera de pistas:
1. La raíz cúbica del coeficiente y el exponente entre 3.
2. ¿Qué número al cubo da 8?
3. 2 · 2 · 2 = 8.

**E3**

En la factorización de $64x^{3}-125$, ¿cuál es el coeficiente del término del medio del trinomio, sin signo?

Respuesta: `20`

Escalera de pistas:
1. Las raíces cúbicas son 4x y 5.
2. El medio del trinomio es el producto de las dos raíces.
3. 4 · 5, y sin el doble que llevaba el cuadrado de binomio.

**E4**

Sin factorizar: ¿cuántos términos tiene el SEGUNDO factor de una suma de cubos?

Respuesta: `3`

Escalera de pistas:
1. La suma de cubos se abre en dos piezas de distinto tamaño.
2. La primera es un binomio.
3. La segunda es un trinomio.

**E5**

Un mozo anota $x^{3}-27=(x-3)(x^{2}-3x+9)$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `mid` | El medio del trinomio: debería ser $+3x$ | — |
| 　 | `bin` | El binomio: debería ser $(x+3)$ | `no_repite_el_signo_en_el_binomio` |
| 　 | `last` | El último del trinomio: debería ser $-9$ | `cree_que_el_trinomio_puede_acabar_restando` |
| 　 | `none` | No hay error | `no_cambia_el_signo_del_medio_del_trinomio` |

Escalera de pistas:
1. El binomio está bien: repite el signo de la remesa.
2. El del medio del trinomio lleva el signo CONTRARIO al del binomio.
3. Binomio con menos → medio del trinomio con más.

**E6**

¿Verdadera o falsa? «Como una suma de cuadrados no se factoriza, una suma de cubos tampoco.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: la de cubos sí se abre, en binomio por trinomio | — |
| 　 | `true` | Verdadera: ninguna suma se factoriza | `cree_que_ninguna_suma_se_factoriza` |
| 　 | `true_even` | Verdadera para exponentes pares e impares por igual | `cree_que_ninguna_suma_se_factoriza` |
| 　 | `false_cube` | Falsa: la de cubos se abre como $(a+b)^{3}$ | `suma_de_cubos_es_cubo_de_binomio` |

Escalera de pistas:
1. Estampa (x + 2)(x² − 2x + 4) y mira qué sale.
2. Todo lo de en medio se anula y quedan x³ y 8.
3. La suma de cuadrados no se abre; la de cubos sí. El exponente importa.

**E7**

Sin abrir ninguno: ¿cuáles de estos son suma o diferencia de CUBOS? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok1` | $x^{3}+64$ | — |
| ✅ | `ok2` | $27a^{3}-1$ | — |
| 　 | `no1` | $x^{3}+9$ | `no_verifica_que_sean_cubos_exactos` |
| 　 | `no2` | $x^{2}+64$ | `no_verifica_que_sean_cubos_exactos` |

Escalera de pistas:
1. Los DOS términos tienen que ser cubos exactos.
2. 9 no es cubo de ningún entero: 2³ = 8 y 3³ = 27.
3. En x² + 64 el primero es un cuadrado, no un cubo. Son dos de los cuatro.


### A9. Cierre

*¿Es una suma o diferencia de cubos?* — **Con dos términos, el exponente decide**

En el cotejo de huellas la suma se quedaba cerrada. Aquí depende del exponente, y esta es la lista.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Los dos son cubos exactos. Se abre en binomio por trinomio. |
|  | ✅ | Mismo molde con los dos signos volteados. El trinomio siempre acaba en más. |
|  | ✗ | El hueco del catálogo, que sigue ahí. Con exponente 2 la suma no se abre. |
|  | ✗ | Entre 8 y 27 no hay ningún cubo. El molde no aplica. |
|  | ✗ | No es una suma de cubos: es un cubo de binomio, ya factorizado. Tiene cuatro términos al desarrollarlo, no dos. |
|  | ~ (ámbar) | Cabe en los dos moldes. Los dos llegan al mismo sitio, pero empezando por cuadrados se termina antes. |

La regla en una línea: **con dos términos, mira el exponente.** Al cuadrado solo se abre la resta; al cubo se abren las dos, y en un binomio por un trinomio.

#### Pregunta de abstracción

Los tres tienen dos términos. ¿Qué decide cuál se abre y en qué piezas?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `exp` | El exponente y el signo: al cuadrado solo se abre la resta, al cubo las dos, y en piezas distintas | — |
| 　 | `sign` | Solo el signo: la resta se abre siempre y la suma nunca | — |
| 　 | `size` | El tamaño del número que acompaña | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuánto vale a + b?
¿Cuánto vale a + b?

Respuesta: `7`

Escalera de pistas:
1. ¿Qué número al cubo da 125?
2. 5. Y la raíz cúbica de 8 es 2.
3. 5 + 2.

Pólya: Entender: hay que hallar las raíces cúbicas y sumar sus coeficientes. → Planear: raíz cúbica de cada término; el binomio lleva la suma de ambas. → Ejecutar: ∛(125m³) = 5m y ∛8 = 2, así que a = 5 y b = 2. → Comprobar: (5m + 2)(25m² − 10m + 4) estampa 125m³ + 8 ✓. Y 5 + 2 = 7.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que conoces el molde de los toneles.

- **Mejoró:** Avance: ya no confundes la suma de cubos con el cubo de una suma.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el contraste entre los dos moldes antes de seguir.

**Q1**

¿Cuál es la raíz cúbica de 64?

Respuesta: `4`

**Q2**

¿Cuál es la factorización de $x^{3}+1$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $(x+1)(x^{2}-x+1)$ | — |
| 　 | `cube` | $(x+1)^{3}$ | `suma_de_cubos_es_cubo_de_binomio` |
| 　 | `none` | No se puede factorizar | `cree_que_ninguna_suma_se_factoriza` |

**Q3**

¿Cuánto es $3^{3}$?

Respuesta: `27`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N3-G04-CUBOS-D2` | `two` | `binomio_cubo_falta_terminos` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-D2` | `three` | `usa_los_coeficientes_del_cuadrado_en_el_cubo` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E1` | `cube` | `suma_de_cubos_es_cubo_de_binomio` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E1` | `conj` | `aplica_diferencia_de_cuadrados_a_los_cubos` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E1` | `sq` | `no_cambia_el_signo_del_medio_del_trinomio` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E5` | `bin` | `no_repite_el_signo_en_el_binomio` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E5` | `last` | `cree_que_el_trinomio_puede_acabar_restando` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E5` | `none` | `no_cambia_el_signo_del_medio_del_trinomio` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E6` | `true` | `cree_que_ninguna_suma_se_factoriza` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E6` | `true_even` | `cree_que_ninguna_suma_se_factoriza` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-E6` | `false_cube` | `suma_de_cubos_es_cubo_de_binomio` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-Q2` | `cube` | `suma_de_cubos_es_cubo_de_binomio` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |
| `ALG-N3-G04-CUBOS-Q2` | `none` | `cree_que_ninguna_suma_se_factoriza` | Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por trinomio. Un cubo de binomio tiene cuatro al d |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
