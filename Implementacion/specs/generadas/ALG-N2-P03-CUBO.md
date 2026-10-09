# Nodo: Al subir de dos a tres, no se pierde una pieza: se pierden dos — ALG-N2-P03-CUBO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N2-P03-CUBO` |
| `concept_slug` | `cubo_de_binomio` |
| Error focal | `binomio_cubo_falta_terminos` |
| Sala / edificio | El molde de tres capas |
| Guía | Rayhana |
| Entra después de | `ALG-N2-P02-CONJUGADOS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El molde de tres capas · Cubo de binomio

**Título:** Al subir de dos a tres, no se pierde una pieza: se pierden dos

Ya viste que elevar una suma al cuadrado deja tres términos y no dos. Aquí la pregunta es qué pasa al subir un piso más. La respuesta no es «uno más»: el molde deja cuatro capas, y las dos de en medio son las que se caen del registro.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de encender el horno. Sin nota.

**D1**

¿Cuánto es 2³?

Respuesta: `8`

**D2**

¿A qué equivale $(x+1)^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $x^{2}+2x+1$ | — |
| 　 | `split` | $x^{2}+1$ | `binomio_cuadrado_falta_2ab` |
| 　 | `double` | $2x+2$ | `confunde_cuadrado_con_duplicar` |

**D3**

Calcula (2 + 1)³.

Respuesta: `27`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el molde de tres capas* — **El bloque de arcilla que salió hueco**

Al fondo de la sala hay moldes altos: en vez de estampar una lámina plana, vacían un bloque macizo de arcilla. El molde se llena por capas.

Rayhana desenrolla una hoja manchada de barro:

«Pedían un bloque cúbico de arista 3 dedos, y luego lo quisieron de arista 4: tres dedos y uno más. El aprendiz calculó la arcilla sumando el bloque de tres con el bloque de uno. Veintisiete más uno: veintiocho.»

«El bloque de arista cuatro se lleva sesenta y cuatro. Faltaron treinta y seis dedos de arcilla, y el bloque salió hueco por dentro.»

**Pregunta:** Al pasar de un cubo de arista 3 a uno de arista 4, ¿dónde se metió toda esa arcilla que faltó?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `capas` | En unas capas planas pegadas a las caras del cubo viejo | — |
| 　 | `esquina` | Solo en la esquina nueva del cubo | — |
| 　 | `nada` | En ningún sitio: 27 + 1 debería bastar | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **El molde se llena por capas, y hay cuatro**

Elevar al cubo es elevar al cuadrado y volver a multiplicar. Ahí se ve de dónde salen las capas de en medio.

- **Paso a paso** — Cada uno de los tres términos del cuadrado se multiplica por a y por b. Al juntar semejantes aparecen los dos treses.
- **Los coeficientes crecen** — Una suma elevada a n deja n + 1 capas. Al cuadrado, tres; al cubo, cuatro. Nunca dos.

**Resolución:** Con arista 3 + 1: el cubo de 3 se lleva 27, el de 1 se lleva 1, y las capas de en medio se llevan 3·9·1 = 27 y 3·3·1 = 9. Suma: 27 + 27 + 9 + 1 = 64. Justo el bloque completo.

**Definición — Cubo de un binomio**

$$(a+b)^{3} = a^{3} + 3a^{2}b + 3ab^{2} + b^{3} \qquad (a-b)^{3} = a^{3} - 3a^{2}b + 3ab^{2} - b^{3}$$

El cubo de un binomio tiene CUATRO términos. Los exponentes del primero bajan 3, 2, 1, 0 y los del segundo suben 0, 1, 2, 3; los coeficientes van 1, 3, 3, 1. Si el binomio resta, los signos se alternan: más, menos, más, menos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a^{3}` | a al cubo | el bloque viejo, la primera capa |
| `3a^{2}b` | tres a al cuadrado b | las tres losas planas pegadas a las caras |
| `3ab^{2}` | tres a b al cuadrado | las tres varillas de las aristas |
| `b^{3}` | b al cubo | el cubito de la esquina |
| `1,3,3,1` | uno, tres, tres, uno | los coeficientes: en el cuadrado eran 1, 2, 1 |

### A5. Ejemplos resueltos

#### Las cuatro capas, una por una · *resuelto*

Rayhana encarga un bloque de arista $y+2$ dedos. ¿Cuánta arcilla lleva?

- Cubo del primero: y³.
- Tres veces el cuadrado del primero por el segundo: 3 · y² · 2 = 6y².
- Tres veces el primero por el cuadrado del segundo: 3 · y · 4 = 12y.
- Cubo del segundo: 2³ = 8.
- Queda y³ + 6y² + 12y + 8. Compruebo con y = 1: la arista mide 3 y el bloque 27. Y 1 + 6 + 12 + 8 = 27 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué la capa lleva un 3 delante, si el molde solo tiene una cara arriba?'}

#### Los signos se alternan · *resuelto*

Otro encargo: arista $2a-3$. Mismo molde, y ahora hay que vigilar cuatro signos.

- Cubo del primero: (2a)³ = 8a³. Se eleva el 2 y la a.
- Tres por el cuadrado del primero por el segundo: 3 · 4a² · 3 = 36a², y va restando.
- Tres por el primero por el cuadrado del segundo: 3 · 2a · 9 = 54a, y va sumando.
- Cubo del segundo: (−3)³ = −27. Un cubo SÍ conserva el signo, a diferencia de un cuadrado.
- Queda 8a³ − 36a² + 54a − 27. Más, menos, más, menos.

#### El aprendiz que vació dos capas de cuatro · *TRAMPA*

Vuelve el bloque de la apertura, ahora con letras. El aprendiz anota la arcilla de una arista $x+3$ así:

- Con x = 1 la arista mide 4 y el bloque se lleva 64.
- La anotación del aprendiz da 1 + 27 = 28. Faltan 36.
- Esos 36 son 9x² + 27x con x = 1: las losas y las varillas.
- Regla para no volver a caer: cuenta las capas. Al cubo son cuatro, siempre.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '(x+3)^{3}=x^{3}+27', 'right_latex': '(x+3)^{3}=x^{3}+9x^{2}+27x+27', 'rows': [{'wrong': 'Dos capas: el bloque viejo y el cubito', 'right': 'Cuatro capas: el bloque, tres losas, tres varillas y el cubito'}, {'wrong': 'Los coeficientes son 1 y 1', 'right': 'Los coeficientes son 1, 3, 3, 1'}]}
**¿Por qué falla?:** Comprueba con x = 1 cuánta arcilla falta en la anotación del aprendiz, y di a qué dos capas corresponde.


### A6. Puente — parcialmente resueltos

La hoja del horno va empezada; completa los huecos.

**P1** (*falta: last*) — Desarrolla $(m-3)^{3}$.

- dado: $m^{3}$
- dado: $3\cdot m^{2}\cdot 3=9m^{2}\ \text{(resta)}$
- hueco `P1-b1`: $3\cdot m\cdot 3^{2}=\ \_\_\,m\ \text{, coeficiente}=$ → `27`

**P2** (*falta: middle*) — Desarrolla $(3x+2)^{3}$.

- dado: $(3x)^{3}=27x^{3}$
- dado: $2^{3}=8$
- hueco `P2-b1`: $3\cdot (3x)^{2}\cdot 2\ \text{, coeficiente}=$ → `54`
- hueco `P2-b2`: $3\cdot 3x\cdot 2^{2}\ \text{, coeficiente}=$ → `36`

**P3** (*falta: statement_only*) — Solo el planteamiento: $(3x^{2})^{3}$. Ojo, esto NO es un binomio — decide antes si el molde de cuatro capas aplica.

- hueco `P3-b1`: $\text{coeficiente del resultado}=$ → `27`


### A7. Comparación de métodos

**Dos maneras de llegar a las cuatro capas**

$(x+1)^{3}$. Una la memoriza; la otra la construye.

- **Método 1 · El molde de memoria** — 
- **Método 2 · Cuadrado y otra vuelta** — 

**Pregunta:** ¿Cuál de los dos explica de dónde salen los dos treses?

**Insight:** El segundo. El molde de memoria da el resultado, pero los coeficientes 1, 3, 3, 1 quedan como un conjuro. Multiplicando el cuadrado por el binomio se ve que el 3 es una suma: x² viene una vez de x²·x y dos veces de 2x·x. El coeficiente no es una regla, es una cuenta de cuántas maneras sale la misma capa.

### A8. Práctica independiente (7 ítems)

**E1**

¿A qué equivale $(a+b)^{3}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `full` | $a^{3}+3a^{2}b+3ab^{2}+b^{3}$ | — |
| 　 | `split` | $a^{3}+b^{3}$ | `binomio_cubo_falta_terminos` |
| 　 | `square` | $a^{3}+2ab+b^{3}$ | `usa_los_coeficientes_del_cuadrado_en_el_cubo` |
| 　 | `triple` | $3a+3b$ | `confunde_cubo_con_triplicar` |

Escalera de pistas:
1. Cuenta las capas: una suma al cubo deja cuatro términos.
2. Los coeficientes van 1, 3, 3, 1.
3. Prueba con a = 3 y b = 1: el bloque se lleva 64.

**E2**

Desarrolla $(y+2)^{3}$. Usa $\wedge$ para el exponente, así: y^3+6y^2+12y+8. No dejes espacios.

Respuesta: `y^3+6y^2+12y+8`

Escalera de pistas:
1. Cubo del primero: y³.
2. Las capas de en medio: 3·y²·2 y 3·y·2².
3. El cubito de la esquina es 2³ = 8.

**E3**

Un bloque tiene arista $x+1$ dedos. Con $x=3$, ¿cuánta arcilla lleva?

Respuesta: `64`

Escalera de pistas:
1. Primero calcula la arista: 3 + 1.
2. La arista mide 4.
3. 4 · 4 · 4.

**E4**

En $(2a-3)^{3}$, ¿cuál es el coeficiente del término con $a^{2}$, sin el signo?

Respuesta: `36`

Escalera de pistas:
1. Esa capa es 3 · (primero)² · (segundo).
2. (2a)² = 4a².
3. 3 · 4 · 3.

**E5**

Un aprendiz anota $(x-2)^{3}=x^{3}-6x^{2}+12x+8$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `last` | El último: $(-2)^{3}=-8$, no $+8$ | — |
| 　 | `middle` | El de $x^{2}$: debería ser $+6x^{2}$ | `signo_alterno_invertido` |
| 　 | `third` | El de $x$: debería ser $-12x$ | `signo_alterno_invertido` |
| 　 | `none` | No hay error | `cubo_de_negativo_es_positivo` |

Escalera de pistas:
1. Los signos van alternando: +, −, +, −.
2. El cuarto término debería restar.
3. Un cubo conserva el signo: (−2)³ = −8, no +8.

**E6**

¿Verdadera o falsa? «Elevar una suma al cubo da el cubo de cada término, igual que elevar un producto.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: aparecen además dos capas intermedias | — |
| 　 | `true` | Verdadera: el exponente entra a cada término | `binomio_cubo_falta_terminos` |
| 　 | `true_one` | Falsa, pero solo falta una capa, como en el cuadrado | `binomio_cubo_falta_terminos` |
| 　 | `false_never` | Falsa: el exponente nunca se reparte, ni sobre productos | `reparte_la_potencia_sobre_la_suma` |

Escalera de pistas:
1. Prueba con (3 + 1)³ frente a 3³ + 1³.
2. 64 frente a 28. Faltan 36.
3. Esos 36 son las dos capas de en medio: 27 y 9.

**E7**

Rayhana revisa cuatro moldes. ¿En cuáles el resultado tiene CUATRO términos? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | $(x+5)^{3}$ | — |
| ✅ | `dif` | $(x-5)^{3}$ | — |
| 　 | `prod` | $(5x)^{3}$ | `reparte_la_potencia_sobre_la_suma` |
| 　 | `sq` | $(x+5)^{2}$ | `usa_los_coeficientes_del_cuadrado_en_el_cubo` |

Escalera de pistas:
1. Una suma elevada a n deja n + 1 términos.
2. Un producto elevado al cubo sigue siendo un solo término.
3. El cuadrado deja tres, no cuatro.


### A9. Cierre

*¿Cuántas capas deja el molde?* — **El número de términos no es un capricho**

Elevar una suma a n deja n + 1 términos, y los coeficientes se pueden leer de un triángulo. Esta es la lista de alturas.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | 2 términos, coeficientes 1 y 1. |
|  | ✅ | 3 términos, coeficientes 1, 2, 1. La orla de la matriz cuadrada. |
|  | ✅ | 4 términos, coeficientes 1, 3, 3, 1. El molde de esta sala. |
|  | ✅ | Siguen siendo 4 términos; lo que cambia es que los signos alternan. |
|  | ✅ | 5 términos, 1, 4, 6, 4, 1. El patrón sigue tan arriba como quieras. |
|  | ~ (ámbar) | Aquí el molde no aplica: sigue siendo UN término. Sobre un producto el exponente sí se reparte, y por eso no aparecen capas intermedias. |

La regla en una línea: **una suma elevada a n deja n + 1 términos.** Si te salen dos, no importa a qué exponente elevaste: te faltan capas.

#### Pregunta de abstracción

Mira los tres desarrollos. ¿Qué se mantiene igual en los tres?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `structure` | Los tres tienen cuatro términos, con el exponente del primero bajando 3, 2, 1, 0 | — |
| 　 | `coef` | Los tres tienen los mismos coeficientes: 1, 3, 3, 1 | — |
| 　 | `signs` | En los tres todos los signos son positivos | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuántos dedos de arcilla lleva el bloque?
¿Cuántos dedos de arcilla lleva el bloque?

Respuesta: `64`

Escalera de pistas:
1. Primero calcula la arista con x = 2.
2. La arista mide 4.
3. 4 · 4 · 4.

Pólya: Entender: la arista es x + 2 y hay que hallar el volumen del cubo. → Planear: o sustituyo primero y elevo al cubo, o uso el molde y sustituyo después. → Ejecutar: 2 + 2 = 4, y 4³ = 64. → Comprobar: por el molde, x³ + 6x² + 12x + 8 con x = 2 da 8 + 24 + 24 + 8 = 64 ✓.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que conoces el molde.

- **Mejoró:** Avance: ya cuentas las capas antes de cerrar el registro.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo las capas intermedias antes de seguir.

**Q1**

¿Cuánto es 3³?

Respuesta: `27`

**Q2**

¿Cuántos términos tiene el desarrollo de $(x+4)^{3}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `four` | Cuatro | — |
| 　 | `two` | Dos | `binomio_cubo_falta_terminos` |
| 　 | `three` | Tres | `usa_los_coeficientes_del_cuadrado_en_el_cubo` |

**Q3**

Calcula (3 + 1)³.

Respuesta: `64`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N2-P03-CUBO-D2` | `split` | `binomio_cuadrado_falta_2ab` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-D2` | `double` | `confunde_cuadrado_con_duplicar` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E1` | `split` | `binomio_cubo_falta_terminos` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E1` | `square` | `usa_los_coeficientes_del_cuadrado_en_el_cubo` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E1` | `triple` | `confunde_cubo_con_triplicar` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E5` | `middle` | `signo_alterno_invertido` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E5` | `third` | `signo_alterno_invertido` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E5` | `none` | `cubo_de_negativo_es_positivo` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E6` | `true` | `binomio_cubo_falta_terminos` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E6` | `true_one` | `binomio_cubo_falta_terminos` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-E6` | `false_never` | `reparte_la_potencia_sobre_la_suma` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-Q2` | `two` | `binomio_cubo_falta_terminos` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |
| `ALG-N2-P03-CUBO-Q2` | `three` | `usa_los_coeficientes_del_cuadrado_en_el_cubo` | Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con coeficientes 1, 3, 3, 1. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
