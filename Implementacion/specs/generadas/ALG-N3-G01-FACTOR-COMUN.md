# Nodo: Sacar la mitad de lo común es dejar el trabajo a medias — ALG-N3-G01-FACTOR-COMUN

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N3-G01-FACTOR-COMUN` |
| `concept_slug` | `factor_comun_y_agrupacion` |
| Error focal | `factor_comun_incompleto` |
| Sala / edificio | El pesaje de entrada |
| Guía | Salim |
| Entra después de | `ALG-N2-P04-TERMINO-COMUN` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El pesaje de entrada · Factor común y agrupación

**Título:** Sacar la mitad de lo común es dejar el trabajo a medias

En la sala de los troqueles estampabas: de dos piezas salía una. Aquí se hace el camino de vuelta. Llegan fardos ya cerrados y hay que averiguar de qué bultos estaban hechos. Y el primer error del almacén no es equivocarse: es parar antes de tiempo.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas en la puerta. Sin nota.

**D1**

¿Cuál es el máximo común divisor de 6 y 9?

Respuesta: `3`

**D2**

¿A qué equivale $2x(3x+4)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | $6x^{2}+8x$ | — |
| 　 | `first` | $6x^{2}+4$ | `distribuye_solo_al_primer_termino` |
| 　 | `flat` | $6x+8x$ | `no_suma_los_exponentes_al_multiplicar` |

**D3**

En $3x^{2}+6x$, ¿qué tienen en común los dos términos?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | Un 3 y una $x$ | — |
| 　 | `num` | Solo el 3 | `factor_comun_incompleto` |
| 　 | `letter` | Solo la $x$ | `factor_comun_incompleto` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el pesaje de entrada* — **El fardo que se volvió a abrir**

En la puerta del almacén hay una romana y un mostrador. Todo lo que llega se pesa, se abre y se anota en el albarán: de cuántos bultos iguales está hecho cada fardo.

Salim empuja hacia KatIA un albarán tachado:

«Entró un fardo de 6 arrobas de comino y 9 de comino molido. El mozo vio que los dos números se partían entre 3 y anotó: tres partes, una de 2 y otra de 3.»

«Pero los dos bultos también compartían el molido. El fardo aún se podía partir otra vez, y el albarán salió firmado a medias. Tuvimos que desatarlo todo y volver a empezar.»

**Pregunta:** Si dos bultos comparten un número Y una medida, ¿basta con sacar el número?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `todo` | No: hay que sacar todo lo que compartan de una vez | — |
| 　 | `numero` | Sí: con el número basta, la letra queda dentro | — |
| 　 | `orden` | Depende del orden en que se saquen | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **La prueba del albarán terminado**

Factorizar es deshacer una multiplicación. Y como toda operación inversa, se comprueba haciendo la de ida.

- **Albarán a medias** — Multiplicando vuelve a salir el fardo, así que no está mal — pero dentro del paréntesis todavía queda algo común. No está terminado.
- **Albarán terminado** — Ahora lo de dentro no se puede partir más: 2 y 3 no tienen divisor común y ya no hay letra en los dos términos.

**Resolución:** El factor común se saca completo: el MCD de los coeficientes, y de cada letra la potencia MÁS PEQUEÑA que aparezca en todos los términos. La prueba de que está terminado es mirar dentro del paréntesis: si lo de dentro todavía comparte algo, falta trabajo.

**Definición — Factor común y agrupación**

$$ab+ac = a(b+c) \qquad ax+ay+bx+by = (x+y)(a+b)$$

El FACTOR COMÚN se saca cuando todos los términos comparten algo: se toma el MCD de los coeficientes y la menor potencia de cada letra común. Lo común puede ser un binomio entero. Cuando no todos los términos comparten algo pero sí lo hacen por parejas, se AGRUPA: se saca el común de cada pareja y, si las dos dejan el mismo binomio, ese binomio se saca a su vez.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a(b+c)` | a por, b más c | el factor común fuera, lo que queda dentro |
| `6x^{2}+9x=3x(2x+3)` | seis equis cuadrado más nueve equis, igual a tres equis por dos equis más tres | MCD de 6 y 9 es 3; menor potencia de x es x¹ |
| `3x(2x+1)+5(2x+1)` | tres equis por dos equis más uno, más cinco por dos equis más uno | aquí lo común es un binomio entero, no un monomio |
| `(x+y)(a+b)` | equis más ye, por a más b | el resultado de agrupar de dos en dos |
| `\text{MCD}` | máximo común divisor | el mismo de Atenas, ahora sobre coeficientes |

### A5. Ejemplos resueltos

#### Números y letras, cada uno con su cuenta · *resuelto*

Salim pesa un fardo anotado como $12x^{3}-18x^{2}$. ¿De qué bultos está hecho?

- Coeficientes: el MCD de 12 y 18 es 6.
- Letra: x aparece con exponentes 3 y 2; me quedo con el MENOR, x².
- Factor común: 6x².
- Divido cada término: 12x³ ÷ 6x² = 2x, y −18x² ÷ 6x² = −3.
- Queda 6x²(2x − 3). Compruebo dentro: 2 y 3 no comparten nada y no hay x en los dos. Terminado.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué se saca la potencia MENOR de la letra y no la mayor?'}

#### Agrupar de dos en dos · *resuelto*

Otro fardo: $5x^{2}y-10x^{2}z+3y-6z$. Los cuatro bultos no comparten nada entre sí, pero por parejas sí.

- Los cuatro juntos no tienen factor común: el 3y no lleva x.
- Primera pareja: 5x²y − 10x²z = 5x²(y − 2z).
- Segunda pareja: 3y − 6z = 3(y − 2z).
- Las dos dejan el MISMO binomio, (y − 2z). Esa es la señal de que la agrupación sirve.
- Saco ese binomio: (y − 2z)(5x² + 3).

#### El mozo que firmó el albarán a medias · *TRAMPA*

Vuelve el fardo de la apertura, ahora con letras. El mozo anota $6x^{2}+9x$ así:

- 3 · 2x² = 6x² y 3 · 3x = 9x. La igualdad es cierta.
- Pero dentro del paréntesis, 2x² y 3x comparten una x: se puede seguir.
- 3(2x² + 3x) = 3 · x(2x + 3) = 3x(2x + 3).
- Regla para no volver a caer: después de sacar, MIRA DENTRO. Si lo de dentro comparte algo, no terminaste.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '6x^{2}+9x=3(2x^{2}+3x)', 'right_latex': '6x^{2}+9x=3x(2x+3)', 'rows': [{'wrong': 'Lo común son los números', 'right': 'Lo común son los números Y las letras que estén en todos'}, {'wrong': 'Multiplicando vuelve a salir, así que está bien', 'right': 'Multiplicar solo prueba que no es falso, no que esté terminado'}]}
**¿Por qué falla?:** Comprueba que la anotación del mozo multiplicada da el fardo original, y explica entonces por qué aun así está incompleta.


### A6. Puente — parcialmente resueltos

El albarán va empezado; completa los huecos.

**P1** (*falta: last*) — Factoriza $8x^{3}+12x^{2}$.

- dado: $\text{MCD}(8,12)=4$
- dado: $\text{menor potencia}=x^{2}$
- hueco `P1-b1`: $8x^{3}\div 4x^{2}\ \text{, coeficiente}=$ → `2`

**P2** (*falta: middle*) — Factoriza $2ax+2ay+3bx+3by$ agrupando.

- dado: $2a(x+y)+3b(x+y)$
- hueco `P2-b1`: $\text{términos del binomio común}=$ → `2`
- hueco `P2-b2`: $\text{factores del resultado}=$ → `2`

**P3** (*falta: statement_only*) — Solo el planteamiento: $27a^{2}b^{3}-18a^{4}b^{5}+45ab^{4}$. Decide primero si esto se agrupa o se saca factor común.

- hueco `P3-b1`: $\text{coeficiente del factor común}=$ → `9`


### A7. Comparación de métodos

**Dos maneras de comprobar que el albarán está cerrado**

$12x^{3}+8x^{2}$. Las dos llegan a $4x^{2}(3x+2)$; solo una avisa si te quedaste corto.

- **Método 1 · Multiplicar de vuelta** — 
- **Método 2 · Mirar dentro del paréntesis** — 

**Pregunta:** ¿Cuál de los dos detecta un factor común incompleto?

**Insight:** El segundo. Multiplicar de vuelta solo comprueba que la igualdad es cierta, y una factorización incompleta también es cierta: 2x²(6x + 4) da exactamente el mismo fardo. Por eso la comprobación de este nodo no es multiplicar, es MIRAR DENTRO: si lo que queda en el paréntesis todavía comparte un número o una letra, el trabajo sigue abierto.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es la factorización COMPLETA de $6x^{2}+9x$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $3x(2x+3)$ | — |
| 　 | `half` | $3(2x^{2}+3x)$ | `factor_comun_incompleto` |
| 　 | `letter` | $x(6x+9)$ | `factor_comun_incompleto` |
| 　 | `wrong` | $3x(2x+3x)$ | `divide_mal_al_sacar_el_factor` |

Escalera de pistas:
1. Saca el MCD de 6 y 9, y también la letra que esté en los dos.
2. Después mira dentro del paréntesis: ¿queda algo común?
3. 3 y una x.

**E2**

Al factorizar $12x^{3}-18x^{2}$, ¿cuál es el coeficiente del factor común?

Respuesta: `6`

Escalera de pistas:
1. Es el máximo común divisor de los dos coeficientes.
2. Los divisores comunes de 12 y 18 son 1, 2, 3 y 6.
3. El mayor.

**E3**

En $27a^{2}b^{3}-18a^{4}b^{5}+45ab^{4}$, ¿cuál es el exponente de $b$ en el factor común?

Respuesta: `3`

Escalera de pistas:
1. De cada letra se saca la potencia MENOR que aparezca en todos.
2. Los exponentes de b son 3, 5 y 4.
3. El menor de los tres.

**E4**

Al agrupar $3x(2x+1)+5(2x+1)$, ¿qué se saca como factor común?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `bin` | El binomio $(2x+1)$ | — |
| 　 | `x` | La letra $x$ | `solo_busca_monomios_como_factor_comun` |
| 　 | `num` | Nada: no hay factor común | `solo_busca_monomios_como_factor_comun` |
| 　 | `all` | $3x\cdot 5=15x$ | `multiplica_en_vez_de_factorizar` |

Escalera de pistas:
1. Lo común no tiene por qué ser un monomio.
2. Mira qué aparece entero en los dos sumandos.
3. El paréntesis (2x + 1) está en ambos.

**E5**

Un mozo anota $b(3a-2c)+4d(3a-2c)$ y firma el albarán. ¿Está terminado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: falta sacar el binomio común y queda $(3a-2c)(b+4d)$ | — |
| 　 | `yes` | Sí: ya no hay ningún monomio común | `factor_comun_incompleto` |
| 　 | `wrong` | No: hay que multiplicar y dejarlo desarrollado | `multiplica_en_vez_de_factorizar` |
| 　 | `other` | No: falta sacar también un 4 | `divide_mal_al_sacar_el_factor` |

Escalera de pistas:
1. La agrupación tiene dos pasos, y este es solo el primero.
2. Los dos sumandos dejaron el mismo binomio.
3. Ese binomio se saca a su vez.

**E6**

¿Verdadera o falsa? «Si al multiplicar de vuelta sale el fardo original, la factorización está terminada.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: eso prueba que es cierta, no que esté completa | — |
| 　 | `true` | Verdadera: si la igualdad se cumple, está terminada | `factor_comun_incompleto` |
| 　 | `true_mono` | Verdadera cuando el factor sacado es un monomio | `factor_comun_incompleto` |
| 　 | `false_never` | Falsa: multiplicar de vuelta no sirve para nada | `multiplica_en_vez_de_factorizar` |

Escalera de pistas:
1. Prueba con 2x²(6x + 4): multiplica y mira qué sale.
2. Sale 12x³ + 8x², el fardo correcto.
3. Y sin embargo 6 y 4 todavía comparten un 2.

**E7**

Salim revisa cuatro fardos. ¿Cuáles se pueden factorizar POR AGRUPACIÓN? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok1` | $2ax+2ay+3bx+3by$ | — |
| ✅ | `ok2` | $5x^{2}y-10x^{2}z+3y-6z$ | — |
| 　 | `no1` | $2x^{2}+6x+8x^{3}-10x^{4}$ | `agrupa_sin_que_salga_el_mismo_binomio` |
| 　 | `no2` | $27a^{2}b^{3}-18a^{4}b^{5}+45ab^{4}$ | `agrupa_sin_que_salga_el_mismo_binomio` |

Escalera de pistas:
1. Para agrupar hacen falta parejas que dejen EL MISMO binomio.
2. Con tres términos no hay forma de hacer dos parejas.
3. Los que no se agrupan sí tienen factor común. Son dos de los cuatro.


### A9. Cierre

*¿Queda algo común dentro?* — **La diferencia entre cierto y terminado**

Todas las filas de abajo son igualdades ciertas. La pregunta no es si son verdad: es si el albarán se puede cerrar.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Dentro quedan 2 y 3, sin divisor común y sin letra compartida. |
|  | ✗ | Cierto, pero dentro todavía hay una x en los dos términos. |
|  | ✅ | MCD 6 y la potencia menor, x². Dentro no queda nada compartido. |
|  | ✗ | Los dos sumandos dejaron el mismo binomio y ese binomio todavía no se ha sacado. Falta el segundo paso. |
|  | ✅ | Lo común no tiene que ser un monomio: aquí era un paréntesis entero. |
|  | ~ (ámbar) | Por agrupación NO se puede: ninguna pareja deja el mismo binomio. Por factor común SÍ, y así queda terminado. Que un método falle no significa que el fardo no se abra. |

La regla en una línea: **después de sacar, mira dentro.** Multiplicar de vuelta solo dice que no te equivocaste; mirar dentro dice si terminaste.

#### Pregunta de abstracción

Las tres factorizaciones de abajo son ciertas. ¿Qué distingue a la primera de las otras dos?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `inside` | Solo en la primera lo que queda dentro del paréntesis ya no comparte nada | — |
| 　 | `biggest` | Solo la primera tiene el coeficiente más grande fuera | — |
| 　 | `true` | Solo la primera es una igualdad verdadera | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuánto vale k + p?
¿Cuánto vale k + p?

Respuesta: `13`

Escalera de pistas:
1. Primero el MCD de 20 y 30.
2. Es 10. Ahora la menor potencia de m entre m⁴ y m³.
3. 10 + 3.

Pólya: Entender: hay que hallar el factor común completo y sumar su coeficiente y su exponente. → Planear: MCD de los coeficientes, y menor potencia de la letra. → Ejecutar: MCD(20, 30) = 10 y la menor potencia es m³, así que k = 10 y p = 3. → Comprobar: 10m³(2m − 3), y dentro 2 y 3 no comparten nada ✓. 10 + 3 = 13.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que sabes cerrar un albarán.

- **Mejoró:** Avance: ya miras dentro del paréntesis antes de firmar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el factor común completo antes de seguir.

**Q1**

¿Cuál es el máximo común divisor de 8 y 12?

Respuesta: `4`

**Q2**

¿Cuál es la factorización completa de $10x^{2}+15x$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $5x(2x+3)$ | — |
| 　 | `half` | $5(2x^{2}+3x)$ | `factor_comun_incompleto` |
| 　 | `letter` | $x(10x+15)$ | `factor_comun_incompleto` |

**Q3**

En $4a^{3}+8a$, ¿qué comparten los dos términos?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | Un 4 y una $a$ | — |
| 　 | `num` | Solo el 4 | `factor_comun_incompleto` |
| 　 | `letter` | Solo la $a$ | `factor_comun_incompleto` |

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N3-G01-FACTOR-COMUN-D2` | `first` | `distribuye_solo_al_primer_termino` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-D2` | `flat` | `no_suma_los_exponentes_al_multiplicar` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-D3` | `num` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-D3` | `letter` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E1` | `half` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E1` | `letter` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E1` | `wrong` | `divide_mal_al_sacar_el_factor` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E4` | `x` | `solo_busca_monomios_como_factor_comun` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E4` | `num` | `solo_busca_monomios_como_factor_comun` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E4` | `all` | `multiplica_en_vez_de_factorizar` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E5` | `yes` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E5` | `wrong` | `multiplica_en_vez_de_factorizar` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E5` | `other` | `divide_mal_al_sacar_el_factor` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E6` | `true` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E6` | `true_mono` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-E6` | `false_never` | `multiplica_en_vez_de_factorizar` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-Q2` | `half` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-Q2` | `letter` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-Q3` | `num` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |
| `ALG-N3-G01-FACTOR-COMUN-Q3` | `letter` | `factor_comun_incompleto` | Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía comparte un número o una letra, falta tr |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
