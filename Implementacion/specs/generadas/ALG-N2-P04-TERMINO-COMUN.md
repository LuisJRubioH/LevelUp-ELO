# Nodo: Uno suma y el otro multiplica, y no son el mismo número — ALG-N2-P04-TERMINO-COMUN

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N2-P04-TERMINO-COMUN` |
| `concept_slug` | `producto_con_termino_comun` |
| Error focal | `termino_comun_falta_suma` |
| Sala / edificio | La bandeja de parejas |
| Guía | Rayhana |
| Entra después de | `ALG-N2-P03-CUBO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La bandeja de parejas · Producto con término común

**Título:** Uno suma y el otro multiplica, y no son el mismo número

Los tres troqueles anteriores pedían que los paréntesis fueran iguales o espejo. Aquí solo comparten el primer término, y los dos cruzados ya no se cancelan ni se duplican: se suman. Ese es el troquel más general de la sala — y los otros tres van a salir de él.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir la bandeja. Sin nota.

**D1**

¿Cuánto es 2 + 3?

Respuesta: `5`

**D2**

¿Cuánto es 2 × 3?

Respuesta: `6`

**D3**

En $(x+2)(x+3)$, ¿qué término comparten los dos paréntesis?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `x` | $x$ | — |
| 　 | `num` | Los números | `confunde_termino_comun_con_los_no_comunes` |
| 　 | `none` | Ninguno | `no_reconoce_el_termino_comun` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la bandeja de parejas* — **La bandeja que se llenó de más**

Sobre la última mesa hay bandejas de casillas. Cada bandeja se llena con dos fichas por casilla, y las fichas vienen en juegos que comparten una medida.

Rayhana saca un registro del cajón:

«Un juego medía 12 por 13. Doce es diez y dos; trece es diez y tres. El aprendiz vio los dieces y los números sueltos y anotó: cien más seis, ciento seis.»

«La bandeja se llevó ciento cincuenta y seis. Le faltaron cincuenta fichas, y no eran ni un cuadrado ni una esquina: eran cinco filas de diez.»

**Pregunta:** En 12 × 13 aparecen un 100 y un 6. ¿De dónde salen las 50 fichas que faltan?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `suma` | De sumar 2 y 3, y multiplicar el resultado por 10 | — |
| 　 | `prod` | De multiplicar 2 por 3 otra vez | — |
| 　 | `nada` | De ningún sitio: 100 + 6 debería bastar | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos cruzados que no se anulan ni se duplican**

Igual que siempre salen cuatro productos. Lo que cambia de troquel a troquel es qué pasa con los dos del medio.

- **Los cuatro productos** — Los dos del medio son bx y ax: ambos llevan x, así que son semejantes y se juntan.
- **Al juntar semejantes** — El del medio lleva la SUMA de los no comunes; el último lleva su PRODUCTO. Casi nunca son el mismo número.

**Resolución:** Con 12 × 13, o sea (10 + 2)(10 + 3): el cuadrado del común es 100, la suma de los no comunes por el común es (2 + 3)·10 = 50, y el producto de los no comunes es 6. Total 156. Las 50 que faltaban eran justo el término del medio.

**Definición — Producto de binomios con término común**

$$(x+a)(x+b) = x^{2} + (a+b)\,x + ab$$

Cuando dos binomios comparten el primer término, el resultado tiene tres términos: el cuadrado del común, la SUMA de los no comunes multiplicada por el común, y el PRODUCTO de los no comunes. Los signos entran en la suma y en el producto: si un no común es negativo, resta en el medio y cambia el signo del último.

| Símbolo | Se lee | Significa |
|---|---|---|
| `x^{2}` | equis al cuadrado | el cuadrado del término común |
| `(a+b)x` | a más b, por equis | la SUMA de los no comunes — el término que se olvida |
| `ab` | a por b | el PRODUCTO de los no comunes, sin ninguna equis |
| `(x+3)(x+3)` | equis más tres, por equis más tres | caso particular con a = b: sale el cuadrado de binomio |
| `(x+3)(x-3)` | equis más tres, por equis menos tres | caso particular con b = −a: la suma da 0 y sale la diferencia de cuadrados |

### A5. Ejemplos resueltos

#### Suma en el medio, producto al final · *resuelto*

Rayhana registra una bandeja de $(x+1)$ por $(x+2)$. ¿Cuántas fichas lleva?

- Cuadrado del común: x · x = x².
- Suma de los no comunes: 1 + 2 = 3, y va multiplicando a la x → 3x.
- Producto de los no comunes: 1 · 2 = 2.
- Queda x² + 3x + 2.
- Compruebo con x = 10: la bandeja es 11 × 12 = 132, y 100 + 30 + 2 = 132 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué el 3 del medio es una suma y el 2 del final un producto, si los dos salen de los mismos números?'}

#### Los signos entran en las dos cuentas · *resuelto*

Otro registro: $(a+5)(a-3)$. El segundo no común es negativo, y eso toca los dos términos.

- Cuadrado del común: a².
- Suma de los no comunes: 5 + (−3) = 2, así que el medio es +2a.
- Producto de los no comunes: 5 · (−3) = −15.
- Queda a² + 2a − 15.
- Fíjate: el medio sale positivo y el último negativo. Cada uno lleva su propia cuenta.

#### El aprendiz que se saltó la fila de en medio · *TRAMPA*

Vuelve el registro de la apertura, ahora con letras. El aprendiz anota la bandeja $(x+3)(x+4)$ así:

- Con x = 10 la bandeja es 13 × 14 = 182.
- La anotación del aprendiz da 100 + 12 = 112. Faltan 70.
- Esos 70 son 7x con x = 10: la suma de los no comunes por el común.
- Regla para no volver a caer: si el resultado no tiene un término con x sola, falta el del medio.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '(x+3)(x+4)=x^{2}+12', 'right_latex': '(x+3)(x+4)=x^{2}+7x+12', 'rows': [{'wrong': 'Dos términos: el cuadrado y el producto', 'right': 'Tres: el cuadrado, la suma por el común, y el producto'}, {'wrong': 'El 12 es lo único que aportan el 3 y el 4', 'right': 'También aportan su suma, 7, que multiplica a la x'}]}
**¿Por qué falla?:** Comprueba con x = 10 cuántas fichas faltan en la anotación del aprendiz, y di de dónde salen.


### A6. Puente — parcialmente resueltos

El registro va empezado; completa los huecos.

**P1** (*falta: last*) — Multiplica $(x+7)(x-8)$.

- dado: $x^{2}$
- dado: $7\cdot(-8)=-56$
- hueco `P1-b1`: $7+(-8)=$ → `-1`

**P2** (*falta: middle*) — Multiplica $(x^{2}-5)(x^{2}+9)$.

- dado: $(x^{2})^{2}=x^{4}$
- hueco `P2-b1`: $-5+9=$ → `4`
- hueco `P2-b2`: $(-5)\cdot 9=$ → `-45`

**P3** (*falta: statement_only*) — Solo el planteamiento: $(a^{3}+3)(a^{3}-8)$. El común no es una letra suelta — identifica primero cuál es.

- hueco `P3-b1`: $\text{exponente de }a\text{ en el primer término}=$ → `6`


### A7. Comparación de métodos

**Dos maneras de llenar la bandeja**

$(x+2)(x+5)$. Una es más rápida; la otra enseña por qué el medio se suma.

- **Método 1 · El troquel** — 
- **Método 2 · Los cuatro productos** — 

**Pregunta:** ¿Cuál de los dos deja claro por qué el medio se suma y el final se multiplica?

**Insight:** El segundo. Con el troquel uno acaba recitando «suma en el medio, producto al final» sin saber por qué. Escribiendo los cuatro productos se ve que los dos cruzados llevan x y por eso son semejantes: se juntan sumando coeficientes. El último no lleva x y no se junta con nadie. La suma y el producto no salen de una regla: salen de qué términos son semejantes y cuáles no.

### A8. Práctica independiente (7 ítems)

**E1**

¿A qué equivale $(x+a)(x+b)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $x^{2}+(a+b)x+ab$ | — |
| 　 | `noMid` | $x^{2}+ab$ | `termino_comun_falta_suma` |
| 　 | `swap` | $x^{2}+ab\,x+(a+b)$ | `intercambia_suma_y_producto` |
| 　 | `sq` | $x^{2}+2abx+ab$ | `usa_el_doble_producto_del_cuadrado` |

Escalera de pistas:
1. Escribe los cuatro productos y mira los dos del medio.
2. Los dos del medio llevan x: son semejantes y se juntan.
3. Prueba con x = 10, a = 2, b = 3: la bandeja es 12 × 13 = 156.

**E2**

Multiplica $(x+1)(x+2)$. Usa $\wedge$ para el exponente, así: x^2+3x+2. No dejes espacios.

Respuesta: `x^2+3x+2`

Escalera de pistas:
1. El primer término es x².
2. El del medio lleva la suma: 1 + 2.
3. El último lleva el producto: 1 · 2.

**E3**

En $(a+5)(a-3)$, ¿cuál es el coeficiente del término del medio? Escríbelo con su signo.

Respuesta: `2`

Escalera de pistas:
1. El del medio lleva la suma de los no comunes.
2. Los no comunes son 5 y −3.
3. 5 − 3.

**E4**

En $(x+7)(x-8)$, ¿cuál es el término sin $x$? Escríbelo con su signo.

Respuesta: `-56`

Escalera de pistas:
1. El último lleva el producto de los no comunes.
2. 7 · (−8).
3. Un positivo por un negativo da negativo.

**E5**

Un aprendiz anota $(x-11)(x+10)=x^{2}+21x-110$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `mid` | El del medio: $-11+10=-1$, así que es $-x$ | — |
| 　 | `last` | El último: debería ser $+110$ | `ignora_los_signos_en_el_producto` |
| 　 | `first` | El primero: debería ser $2x^{2}$ | `suma_los_terminos_comunes` |
| 　 | `none` | No hay error | `intercambia_suma_y_producto` |

Escalera de pistas:
1. El último está bien: (−11) · 10 = −110.
2. Mira el del medio: ¿es la suma o el producto?
3. −11 + 10 = −1, no 21. Sumó los valores sin mirar el signo.

**E6**

¿Verdadera o falsa? «Como los dos números aparecen multiplicados en el último término, no hace falta escribirlos otra vez en el medio.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: en el medio va su suma, que es otra cuenta distinta | — |
| 　 | `true` | Verdadera: ya están contados en el producto | `termino_comun_falta_suma` |
| 　 | `true_eq` | Verdadera cuando los dos números son iguales | `termino_comun_falta_suma` |
| 　 | `false_prod` | Falsa: en el medio va su producto otra vez | `intercambia_suma_y_producto` |

Escalera de pistas:
1. Prueba con 12 × 13, o sea (10 + 2)(10 + 3).
2. 156, no 106.
3. Las 50 que faltan son (2 + 3) · 10: la suma, no el producto.

**E7**

Rayhana ordena la sala. ¿Cuáles de estos productos se pueden resolver con el troquel de la bandeja? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `plain` | $(x+2)(x+9)$ | — |
| ✅ | `sq` | $(x+4)(x+4)$ | — |
| ✅ | `conj` | $(x+4)(x-4)$ | — |
| 　 | `nocommon` | $(2x+1)(x+5)$ | `cree_que_2x_y_x_son_el_mismo_termino_comun` |

Escalera de pistas:
1. Hace falta que el primer término sea EL MISMO en los dos paréntesis.
2. El cuadrado de binomio y los conjugados son casos particulares de este troquel.
3. 2x y x no son el mismo término común. Son tres de las cuatro.


### A9. Cierre

*¿Qué manda en el término del medio?* — **Los cuatro troqueles eran uno**

Este es el troquel general de la sala. Los otros tres se obtienen eligiendo qué son los dos no comunes.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Medio = 2 + 3 = 5. Último = 2 · 3 = 6. Suma y producto, distintos. |
|  | ✅ | Los signos entran en las dos cuentas: 5 − 2 = 3 y 5·(−2) = −10. |
|  | ✅ | Medio negativo, último positivo. Dos negativos multiplicados suman. |
|  | ~ (ámbar) | Aquí la suma vale 2·3 y el troquel se convierte en la matriz cuadrada. No es un troquel aparte: es este con a = b. |
|  | ~ (ámbar) | La suma vale 0, así que el medio desaparece y queda el cuño de la cenefa. Tampoco era un troquel aparte. |
|  | ✗ | 2x y x no son el mismo término: el troquel no aplica y toca multiplicar los cuatro productos a mano. |

La regla en una línea: **el medio lleva la suma de los no comunes; el último, su producto.** Y los tres troqueles anteriores de la sala son casos particulares de este: cuando los no comunes son iguales sale el cuadrado, y cuando son opuestos sale la diferencia de cuadrados.

#### Pregunta de abstracción

Mira los tres productos. ¿Qué determina el signo del término del medio y el del último?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `sumprod` | El medio lo decide la suma de los dos números con su signo, y el último su producto | — |
| 　 | `count` | Los decide cuántos signos menos hay en los paréntesis | — |
| 　 | `first` | Los decide el signo del primer paréntesis | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuántas fichas lleva la bandeja?
¿Cuántas fichas lleva la bandeja?

Respuesta: `20`

Escalera de pistas:
1. Calcula cuánto vale cada paréntesis con x = 4.
2. Salen 10 y 2.
3. 10 · 2.

Pólya: Entender: comparten la x; los no comunes son +6 y −2. → Planear: o multiplico directo, o uso el troquel y sustituyo. → Ejecutar: 4 + 6 = 10 y 4 − 2 = 2, así que 10 · 2 = 20. → Comprobar: por el troquel, x² + 4x − 12 con x = 4 da 16 + 16 − 12 = 20 ✓.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que conoces el troquel general.

- **Mejoró:** Avance: ya separas la suma del producto sin dudar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el término del medio antes de cerrar la sala.

**Q1**

¿Cuánto es 4 + 7?

Respuesta: `11`

**Q2**

¿Cuánto es 4 × 7?

Respuesta: `28`

**Q3**

¿A qué equivale $(x+4)(x+7)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $x^{2}+11x+28$ | — |
| 　 | `noMid` | $x^{2}+28$ | `termino_comun_falta_suma` |
| 　 | `swap` | $x^{2}+28x+11$ | `intercambia_suma_y_producto` |

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N2-P04-TERMINO-COMUN-D3` | `num` | `confunde_termino_comun_con_los_no_comunes` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-D3` | `none` | `no_reconoce_el_termino_comun` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E1` | `noMid` | `termino_comun_falta_suma` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E1` | `swap` | `intercambia_suma_y_producto` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E1` | `sq` | `usa_el_doble_producto_del_cuadrado` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E5` | `last` | `ignora_los_signos_en_el_producto` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E5` | `first` | `suma_los_terminos_comunes` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E5` | `none` | `intercambia_suma_y_producto` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E6` | `true` | `termino_comun_falta_suma` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E6` | `true_eq` | `termino_comun_falta_suma` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-E6` | `false_prod` | `intercambia_suma_y_producto` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-Q3` | `noMid` | `termino_comun_falta_suma` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |
| `ALG-N2-P04-TERMINO-COMUN-Q3` | `swap` | `intercambia_suma_y_producto` | Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, el último su PRODUCTO. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
