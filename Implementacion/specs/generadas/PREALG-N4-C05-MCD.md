# Nodo: El mayor de los divisores comunes, no el mayor de los números — PREALG-N4-C05-MCD

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N4-C05-MCD` |
| `concept_slug` | `mcd` |
| Error focal | `mcd_es_el_mayor_de_los_numeros` |
| Sala / edificio | Atenas · lo más grande en común |
| Guía | KatIA |
| Entra después de | `PREALG-N4-C04-FACTORIZACION-PRIMA` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** Atenas · Máximo común divisor

**Título:** El mayor de los divisores comunes, no el mayor de los números

Hasta aquí mirabas un número a la vez. Ahora son dos, y la pregunta es qué comparten. El nombre de la operación lleva tres palabras y hay que leerlas las tres: máximo, común, divisor. Saltarse la del medio es el error de este muelle.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el almacén. Sin nota.

**D1**

¿Cuál es el mayor número que divide a la vez a 12 y a 18?

Respuesta: `6`

**D2**

¿Cuánto vale el MCD de $8$ y $20$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `four` | 4 | — |
| 　 | `twenty` | 20 | `mcd_es_el_mayor_de_los_numeros` |
| 　 | `one_sixty` | 160 | `confunde_mcd_con_producto` |

**D3**

¿Dos números pueden no tener ningún divisor en común aparte del 1?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí | — |
| 　 | `no` | No: siempre comparten alguno mayor | `siempre_hay_divisor_comun_mayor_que_uno` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el almacén de Atenas* — **El cofre que servía para los dos cargamentos**

En el almacén de Atenas hay cofres de todos los tamaños. Llegan dos cargamentos —uno de 48 piezas y otro de 36— y hay que guardarlos en cofres IGUALES, sin mezclar los cargamentos y sin que quede ninguna pieza suelta.

El encargado quiere el cofre más grande posible, para hacer menos viajes. Miró los dos números, dijo «el más grande es 48, uso cofres de 48» y bajó a buscarlos. Con el cargamento de 36 no llenó ni un cofre.

**Pregunta:** ¿Cuál es el cofre más grande que reparte exacto los DOS cargamentos?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | 48: es el mayor de los dos | — |
| 　 | `b` | Algún número más pequeño que los dos | — |
| 　 | `c` | 48 × 36, para que quepan los dos | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Las dos listas y lo que tienen en medio**

Los divisores de cada cargamento, uno debajo del otro. Busca los que aparecen en las dos listas.

- **Los divisores de cada uno** — Diez divisores y nueve. Todavía no dicen nada por separado.
- **Los que están en las dos** — Seis en común, y el más grande es 12. Ese es el cofre.

**Resolución:** El cofre no puede ser 48: 48 no divide a 36. Ni siquiera puede pasar de 36, porque tiene que caber en el más pequeño. El MCD siempre está entre 1 y el menor de los dos números — nunca por encima, y nunca es el producto.

**Definición — El máximo común divisor**

$$\text{MCD}(a,b)=\max\big(D(a)\cap D(b)\big)$$

El MCD de dos números es el mayor número que divide a los dos a la vez. Siempre existe (el 1 siempre está) y nunca supera al menor de los dos. Si vale 1, los números se llaman COPRIMOS.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\text{MCD}(a,b)` | máximo común divisor de a y b | el cofre más grande que sirve para los dos |
| `\cap` | intersección | lo que está en las DOS listas de divisores |
| `\max` | el máximo | el mayor de esa lista común, no de los números |
| `\text{MCD}(a,b)\le\min(a,b)` | no supera al menor | tiene que caber en el cargamento pequeño |
| `\text{MCD}(a,b)=1` | coprimos | no comparten nada salvo el 1 |

### A5. Ejemplos resueltos

#### El MCD desde la factorización · *resuelto*

Los cargamentos son de 48 y 36 piezas. Halla el cofre más grande usando la descomposición en primos.

- Descompongo los dos: 48 = 2⁴ × 3 y 36 = 2² × 3².
- Un divisor común solo puede usar piezas que TENGAN LOS DOS.
- Del 2: uno tiene cuatro y el otro dos. Como mucho puedo usar dos → 2².
- Del 3: uno tiene uno y el otro dos. Como mucho uno → 3.
- MCD = 2² × 3 = 12. Se cogen los primos comunes con el exponente MENOR.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se coge el exponente menor, no el mayor. ¿Por qué coger cuatro doses rompería el reparto?'}

#### Dos cargamentos coprimos · *resuelto*

Ahora llegan cargamentos de 25 y 12 piezas. ¿Qué cofre sirve para los dos?

- Descompongo: 25 = 5² y 12 = 2² × 3.
- Busco primos comunes: el 5 no está en 12, y ni el 2 ni el 3 están en 25.
- No hay ningún primo compartido, así que el único divisor común es el 1.
- MCD(25, 12) = 1: se dice que son coprimos.
- El cofre tendría que ser de una pieza. No hay forma de agrupar más sin romper alguno de los dos repartos.

#### El encargado que se saltó la palabra «común» · *TRAMPA*

El encargado anota en el registro: «Cargamentos de 48 y 36. El máximo es 48, así que uso cofres de 48».

- Comprueba: ¿48 divide a 36? 36 ÷ 48 no es entero. No.
- Un divisor común tiene que dividir a los DOS, así que no puede ser mayor que el menor de ellos.
- Lo mayor que puede ser el MCD aquí es 36, y de hecho es 12.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\text{MCD}(48,36)=48', 'right_latex': '\\text{MCD}(48,36)=12', 'rows': [{'wrong': 'El MCD es el mayor de los dos números', 'right': 'Es el mayor de sus divisores COMUNES'}, {'wrong': 'Un cofre de 48 sirve para los dos cargamentos', 'right': 'No cabe en 36: el MCD nunca supera al número menor'}]}
**¿Por qué falla?:** ¿Por qué el MCD no puede pasar de 36? Da el valor correcto.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Halla el MCD de 20 y 30 con las factorizaciones.

- dado: $20=2^{2}\times 5,\quad 30=2\times 3\times 5$
- dado: $\text{comunes: }2\ \text{y}\ 5,\ \text{con el exponente menor}$
- hueco `P1-b1`: $\text{MCD}(20,30)=$ → `10`

**P2** (*falta: middle*) — Halla el MCD de 18 y 24.

- dado: $18=2\times 3^{2},\quad 24=2^{3}\times 3$
- hueco `P2-b1`: $\text{exponente del 3 que se coge}=$ → `1`
- hueco `P2-b2`: $\text{MCD}(18,24)=$ → `6`

**P3** (*falta: statement_only*) — Solo el planteamiento: dos cargamentos de 14 y 15 piezas. ¿Qué cofre sirve para los dos?

- hueco `P3-b1`: $\text{MCD}(14,15)=$ → `1`


### A7. Comparación de métodos

**Dos caminos para el mismo cofre**

¿Cuánto vale $\text{MCD}(84,120)$? Las dos soluciones de abajo son correctas.

- **Método 1 · Por factorización** — 
- **Método 2 · Algoritmo de Euclides** — 

**Pregunta:** ¿Cuál usarías con dos números de cinco cifras que no sabes factorizar?

**Insight:** El método 2 nunca necesita conocer los primos: va cambiando el par por (divisor, residuo) hasta que el residuo es 0, y el último divisor no nulo es el MCD. Funciona porque todo divisor común de a y b también divide al residuo. Es de los algoritmos más antiguos que se siguen usando — está en Euclides, hace más de dos mil años.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es el MCD de 16 y 24?

Respuesta: `8`

Escalera de pistas:
1. El resultado no puede pasar de 16.
2. 16 = 2⁴ y 24 = 2³ × 3.
3. El único primo común es el 2, con exponente 3.

**E2**

¿Cuál es el MCD de 9 y 28?

Respuesta: `1`

Escalera de pistas:
1. Descompón los dos y busca primos compartidos.
2. 9 = 3² y 28 = 2² × 7.
3. No comparten ningún primo: son coprimos.

**E3**

¿Cuál es el MCD de 15 y 45?

Respuesta: `15`

Escalera de pistas:
1. Comprueba primero si el pequeño divide al grande.
2. 45 ÷ 15 = 3, exacto.
3. Si a divide a b, el MCD es a.

**E4**

Un encargado anota «MCD(10, 25) = 50». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `too_big` | 50 pasa de 25: el MCD nunca supera al número menor. Es 5 | — |
| 　 | `arith` | Se equivocó: el MCD es 10 | `mcd_es_el_mayor_de_los_numeros` |
| 　 | `coprime` | No tienen divisores comunes: es 1 | `no_busca_divisores_comunes` |
| 　 | `none` | Ningún error, está bien | `confunde_mcd_con_mcm` |

Escalera de pistas:
1. Antes de calcular nada: ¿puede un divisor de 10 valer 50?
2. El MCD tiene que dividir al 10, así que no pasa de 10.
3. Los divisores comunes de 10 y 25 son 1 y 5.

**E5**

¿Es verdadera o falsa? «El MCD de dos números siempre es uno de los dos números.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_unless` | Falsa: solo si uno divide al otro, como MCD(15,45) = 15 | — |
| 　 | `true` | Verdadera: siempre es el mayor de los dos | `mcd_es_el_mayor_de_los_numeros` |
| 　 | `false_never` | Falsa: nunca puede ser uno de ellos | `olvida_el_caso_de_divisibilidad` |
| 　 | `true_smaller` | Verdadera: siempre es el menor de los dos | `mcd_es_siempre_el_menor` |

Escalera de pistas:
1. Busca un par donde el MCD no sea ninguno de los dos.
2. Prueba con 48 y 36: el MCD es 12.
3. ¿Y hay algún par donde SÍ lo sea? Prueba 15 y 45.

**E6**

Selecciona TODOS los pares que son coprimos (MCD = 1).

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `p1` | 8 y 15 | — |
| 　 | `p2` | 6 y 9 | — |
| ✅ | `p3` | 7 y 13 | — |
| 　 | `p4` | 12 y 18 | — |

Escalera de pistas:
1. Coprimos quiere decir que no comparten ningún primo.
2. 8 = 2³ y 15 = 3 × 5: nada en común.
3. 6 y 9 comparten el 3; 12 y 18 comparten 2 y 3.

**E7**

Dos cargamentos, de 54 y 72 piezas, se guardan en cofres iguales sin que sobre nada. ¿Cuántas piezas lleva el cofre más grande posible?

Respuesta: `18`

Escalera de pistas:
1. Descompón los dos.
2. 54 = 2 × 3³ y 72 = 2³ × 3².
3. Comunes con exponente menor: 2 × 3² = …


### A9. Cierre

*Casos que conviene reconocer de un vistazo* — **¿El MCD es uno de los dos números?**

Cinco situaciones que aparecen todo el tiempo y una que hay que descartar siempre.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | Ninguno de los dos. Hay que calcularlo: comunes con exponente menor. |
|  | ✅ | El MCD es el pequeño. Compruébalo siempre primero: ahorra todo el trabajo. |
|  | ✗ | No comparten primos. Dos primos distintos siempre son coprimos. |
|  | ✅ | Comparten todo. Caso extremo del anterior. |
|  | ✅ | El 1 divide a todo y no tiene más divisores: el MCD es 1, que aquí sí es uno de los dos. |
|  | ✅ | Todo divide al 0 (C02), así que los comunes son los de n y el mayor es n. |

Dos comprobaciones antes de calcular: ¿uno divide al otro? ¿comparten algún primo? Y un techo que nunca falla: el MCD no puede pasar del número menor. En Esparta vas a hacer la pregunta contraria.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `intersection` | En los tres se busca algo que esté en las DOS listas de divisores | — |
| 　 | `ceiling` | En los tres el resultado no puede pasar del número menor | — |
| 　 | `biggest` | En los tres el resultado es el mayor de los dos números | — |
| 　 | `always_one` | En los tres el resultado es 1 | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿De cuántas piezas es el cofre?
¿De cuántas piezas es el cofre?

Respuesta: `42`

Escalera de pistas:
1. Descompón los dos números en primos.
2. 84 = 2² × 3 × 7 y 126 = 2 × 3² × 7.
3. Comunes con el exponente menor: 2 × 3 × 7 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya lees la C de «común» antes de responder.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el MCD no puede pasar del número más pequeño.

**PD1**

¿Cuál es el mayor número que divide a la vez a 20 y a 30?

Respuesta: `10`

**PD2**

¿Cuánto vale el MCD de $9$ y $21$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `three` | 3 | — |
| 　 | `twentyone` | 21 | `mcd_es_el_mayor_de_los_numeros` |
| 　 | `product` | 189 | `confunde_mcd_con_producto` |

**PD3**

¿Cuánto vale el MCD de $6$ y $30$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `six` | 6: el menor divide al mayor | — |
| 　 | `thirty` | 30 | `mcd_es_el_mayor_de_los_numeros` |
| 　 | `one` | 1 | `sobregeneraliza_mcd` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N4-C05-MCD-D2` | `twenty` | `mcd_es_el_mayor_de_los_numeros` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-D2` | `one_sixty` | `confunde_mcd_con_producto` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-D3` | `no` | `siempre_hay_divisor_comun_mayor_que_uno` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-E4` | `arith` | `mcd_es_el_mayor_de_los_numeros` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-E4` | `coprime` | `no_busca_divisores_comunes` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-E4` | `none` | `confunde_mcd_con_mcm` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-E5` | `true` | `mcd_es_el_mayor_de_los_numeros` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-E5` | `false_never` | `olvida_el_caso_de_divisibilidad` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-E5` | `true_smaller` | `mcd_es_siempre_el_menor` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-PD2` | `twentyone` | `mcd_es_el_mayor_de_los_numeros` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-PD2` | `product` | `confunde_mcd_con_producto` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-PD3` | `thirty` | `mcd_es_el_mayor_de_los_numeros` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |
| `PREALG-N4-C05-MCD-PD3` | `one` | `sobregeneraliza_mcd` | Comprueba el techo: el MCD no puede pasar del número más pequeño. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/04-prealg-n4-puerto/c05-mcd-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
