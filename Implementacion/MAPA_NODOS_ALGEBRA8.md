# Mapa de nodos — Álgebra 8 (reorganización desde los ejercicios extraídos)

Fuente: `items/source/hipertexto8/*.json` (2.506 ítems, U1–U8; U8 al 8/15, U9–U10 sin transcribir)
+ `items/bank/evaluar_para_avanzar_8.json` (60 ítems EPA8).

Arquitectura: 11 bloques (`.claude/skills/levelup-node-author`), formato de dict por nivel
(`.claude/skills/prealgebra-node-author`), mundos narrativos
(`Implementacion/GUION_MAESTRO_NARRATIVA_PREALGEBRA.md`).

---

## 1. Principio organizador — la resignificación, no el índice del libro

El orden de los nodos **no** es el orden de las unidades del libro. Cada nodo de álgebra
resignifica un nodo de preálgebra ya construido: el estudiante no aprende un tema nuevo,
reencuentra uno viejo con letras. El puente (bloque 5 de los 11) es literalmente esa frase.

| Preálgebra (ya construido) | Se resignifica en | Frase-puente |
|---|---|---|
| N1-B04..B08 conjuntos, cierre ℕ→ℤ→ℚ | N6 polinomios / N9 fracciones algebraicas | los polinomios son "los enteros del álgebra": cerrados bajo `+ − ×`, **no** bajo `÷` → nacen las fracciones algebraicas igual que nació ℚ |
| N2-E01..E06 operaciones | N6 operaciones con polinomios | la misma operación, ahora sobre expresiones |
| N2-E05 potenciación | N7 productos notables | `(a+b)²` no es `a²+b²` — la trampa central del nivel |
| N3-M03 distributiva | N7 productos notables / N6-O04 | un producto notable es la distributiva comprimida |
| N3-M05 inversos | N10 ecuaciones | despejar = aplicar el inverso a ambos lados |
| N4-C03 primos, C04 factorización prima | N8 factorización | los factores irreducibles son "los primos del álgebra" |
| N4-C05 MCD, C06 MCM | N9-R01/R02 MCD y MCM de polinomios | mismo algoritmo, factores en vez de primos |
| N1-B08 recta real, intervalos | N10-Q10 conjunto solución de inecuaciones | el intervalo vuelve, ahora como respuesta |
| N1-B09 complejos (callejón opcional) | N9-R09b fracciones continuas (callejón opcional) | mismo rol: desvío avanzado, no obligatorio |

**Consecuencia de ordenamiento:** factorización (U5) va **después** de productos notables (U4)
porque es su inversa, y fracciones algebraicas (U6) va después de factorización porque
simplificar exige factorizar. Coincide con el libro. Lo que **no** coincide: el lenguaje
algebraico de U7 p190/p203 sube a N5 (es el mismo contenido que U2 p29) y el MCD/MCM de
polinomios de U6 p139/p142 se declara explícitamente como continuación de N4-C05/C06.

---

## 2. Curso destino e IDs

Curso nuevo `algebra_8` → bloque `Colegio` (agregar en `_COURSE_BLOCK_MAP` de **ambos**
repositorios, R1). Los nodos PREALG viven en `algebra_basica`; no se mezclan.

Convención de ID: `ALG8-N<n>-<P><nn>-<SLUG>`, con prefijo de letra por nivel, siguiendo
B(N1)/E(N2)/M(N3)/C(N4):

| Nivel | Prefijo | Tema | Unidad fuente | Ítems disponibles |
|---|---|---|---|---|
| N5 | `L` | Lenguaje algebraico y expresiones | U2 + U7 p190/p203 | 113 + 37 |
| N6 | `O` | Operaciones con polinomios | U3 | 315 |
| N7 | `P` | Productos y cocientes notables | U4 | 350 |
| N8 | `F` | Factorización | U5 | 595 |
| N9 | `R` | Fracciones algebraicas | U6 | 349 |
| N10 | `Q` | Ecuaciones e inecuaciones | U7 (menos lenguaje) | ~400 |
| N11 | `V` | Función lineal | U8 | 176 (incompleto) |

---

## 3. Mundo narrativo — el viaje de KatIA

Preálgebra transcurre en Grecia (ágora → mercado → fábrica → puerto). Álgebra **cambia de
mundo**: KatIA viaja a **la Casa de la Sabiduría (Bagdad, s. IX)** — al-Juarismi, de quien
viene la palabra *álgebra*. Lo pide el propio libro: la apertura de U2 es "El servidor del
califa".

Un sub-espacio por nivel, vocabulario sin cruces (regla del guión maestro):

| Nivel | Sub-espacio | Banco de vocabulario |
|---|---|---|
| N5 | Sala de los copistas | cálamos, tinta, pergaminos, atriles, catálogo, símbolos |
| N6 | Taller de traductores | tablillas de cotejo, columnas de texto, glosas, cajas de tipos |
| N7 | ~~Patio de los mosaicos~~ → **Sala de los troqueles** | troquel, matriz, cuño, lámina de cobre, orla, molde, bandeja |
| N8 | Almacén de la caravana | fardos, sacos, cajas anidadas, inventario, balanzas de carga |
| N9 | Casa de las acequias | canales, compuertas, caudales, norias, repartos de agua |
| N10 | Sala de la balanza | balanza de dos platos, pesas, contrapesos, fiel, sellos |
| N11 | Observatorio | astrolabio, cuadrante, sombras, alturas, tablas de posición |

> **Corrección 2026-08-13 — «patio de los mosaicos» estaba tomado.** E03 de N2 es
> **El Taller de Mosaicos** (V2-R12), así que el sub-espacio de productos notables cambia a
> **la sala de los troqueles**: un producto notable es un troquel, se estampa el patrón en vez
> de multiplicar término a término. Hay test que impide que dos nodos compartan sala.
>
> **Curso:** este mapa proponía crear `algebra_8`. Se descarta: ALG-N1 ya vive en
> `algebra_basica` (V2-R15) y la posición la fija `unlock_after`. Un solo curso, sin tocar
> `_COURSE_BLOCK_MAP` ni los dos repositorios.

Retrofuturismo: mecanismos puntuales (astrolabio, noria, prensa), nunca sci-fi.
Regla dura heredada: ningún objeto concreto se repite más de 2 veces dentro del mismo nivel.

---

## 4. Mapa de nodos

Cada fila: nodo → páginas fuente → ítems disponibles → nodo de preálgebra que resignifica.
La trampa listada es la que ocupa la tarjeta (c) de ejemplos y reaparece en la práctica.

### N5 — Lenguaje algebraico (Sala de los copistas)

| Nodo | Fuente | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `L00` Hub — La Casa de la Sabiduría | U2 p29 diagnóstico + apertura | 8 | — | — |
| `L01` De número a letra | U2 p29-33 + U7 p190 (25) + p203 (9) | ~40 | N2 completo | "el doble de un número más 3" ≠ `2(x+3)` |
| `L02` Monomio | U2 p33 | 18 | N4-C04 (partes de un objeto) | `3x²` y `3x³` como semejantes |
| `L03` Polinomio | U2 p37 | 10 | N1-B04 (clasificar) | grado = número de términos |
| `L04` Valor numérico | U2 p39 + p43 | 35 | N2-E01..E06 | `−x²` con `x=−2` → `4` |
| `L05` Cierre — Taller 2 | U2 p40-41 | 42 | — | — |

### N6 — Operaciones con polinomios (Taller de traductores)

| Nodo | Fuente | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `O00` Hub | U3 p45 | 6 | — | — |
| `O01` Suma y resta de monomios | U3 p48 | 27 | N2-E01/E02 | sumar exponentes al sumar semejantes |
| `O02` Suma, resta y signos de agrupación | U3 p51 | 39 | N3-M02 asociativa | signo menos delante del paréntesis |
| `O03` Multiplicación de monomios | U3 p53 | 21 | N2-E03 + N2-E05 | `x²·x³ = x⁶` |
| `O04` Multiplicación de polinomios | U3 p57 | 31 | N3-M03 distributiva | distribuir solo el primer término |
| `O05` División de monomios y por monomio | U3 p59 | 17 | N2-E04 | dividir solo el primer término |
| `O06` División entre polinomios | U3 p62 | 23 | N4 división euclidiana | no ordenar / no dejar hueco al término faltante |
| `O07` Ruffini y teorema del residuo | U3 p65 | 52 | N4-C01 divisibilidad | usar Ruffini con divisor `2x−1` sin ajustar |
| `O08` Cierre — ¿son cerrados los polinomios? | U3 p66-67 taller + p69 | 71 | N1-B05/B06 cierre | — (nodo puente a N9) |

`O08` es el nodo-bisagra del curso: la escalera de cierre vuelve, ahora con filas
`monomios / polinomios / fracciones algebraicas` en vez de ℕ ℤ ℚ.

### N7 — Productos y cocientes notables (Patio de los mosaicos)

| Nodo | Fuente | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `P00` Hub | U4 p71 | 6 | — | — |
| `P01` Binomio al cuadrado | U4 p74 | 49 | N3-M03 | `(a+b)² = a²+b²` |
| `P02` Cuadrado de un trinomio | U4 p75 | 22 | P01 | olvidar los dobles productos cruzados |
| `P03` Suma por diferencia | U4 p77 | 24 | N1-B05 opuestos | `(a−b)(a−b)` como suma por diferencia |
| `P04` Producto `(x+a)(x+b)` | U4 p79 | 27 | P01 | `a·b` con signos mal en el término independiente |
| `P05` Cubo de un binomio | U4 p83 | 44 | N2-E05 | `(a+b)³ = a³+b³` |
| `P06` Suma y diferencia de cubos | U4 p83 (comparte) | — | P03 | signo del término medio del trinomio |
| `P07` Binomio de Newton y Pascal | U4 p85 | 37 | N4 combinatoria informal | ignorar el signo alterno en `(a−b)ⁿ` |
| `P08` Cocientes notables | U4 p87 | 32 | N2-E04 | `(a²+b²)÷(a+b)` como exacto |
| `P09` Cocientes de grado n | U4 p89 | 24 | P08 | paridad del exponente |
| `P10` Cierre — Taller 4 | U4 p90-91 + p93 + p96-97 | 79 | — | — |

### N8 — Factorización (Almacén de la caravana)

Nivel más grande (595 ítems). Apertura del nivel = "la máquina al revés": todo N8 deshace N7.

| Nodo | Fuente | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `F00` Hub — la máquina al revés | U5 p99 | 11 | N7 completo | — |
| `F01` Factor común (y de monomios) | U5 p101 + p104 | 91 | N4-C05 MCD | sacar factor común y perder el `1` |
| `F02` Factor común por agrupación | U5 p106 | 45 | N3-M02 | agrupar sin factor común real |
| `F03` Diferencia de cuadrados | U5 p108 | 34 | P03 | factorizar `a²+b²` |
| `F04` Suma y diferencia de cubos | U5 p111 | 43 | P06 | signo del trinomio no factorizable |
| `F05` Potencias de igual exponente | U5 p114 | 43 | F03/F04 | aplicar la regla con exponente par |
| `F06` Trinomio cuadrado perfecto | U5 p116 | 38 | P01 | declarar TCP sin verificar el doble producto |
| `F07` TCP por adición y sustracción | U5 p118 | 22 | F06 | sumar sin restar lo mismo |
| `F08` Trinomio `x²ⁿ+bxⁿ+c` | U5 p120 | 29 | P04 | buscar suma y producto con signos cruzados |
| `F09` Trinomio `ax²ⁿ+bxⁿ+c` | U5 p122 | 35 | F08 | no dividir por `a` al final |
| `F10` Cubo perfecto | U5 p124 | 25 | P05 | verificar solo los extremos |
| `F11` Factorización por división sintética | U5 p129 | 37 | O07 + N4-C03 | probar raíces que no dividen al término independiente |
| `F12` Factorización completa | U5 p127 | 46 | todos | detenerse en el primer caso aplicable |
| `F13` Cierre — Taller 5 | U5 p130-131 + p133 | 96 | — | — |

`F12` necesita un bloque propio no previsto en el renderer: **árbol de decisión de casos**
(¿cuántos términos? → ¿hay factor común? → …). Marcar `[PENDIENTE DE RENDERER]`.

### N9 — Fracciones algebraicas (Casa de las acequias)

| Nodo | Fuente | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `R00` Hub | U6 p135 | 7 | O08 | — |
| `R01` MCD de polinomios | U6 p139 | 48 | **N4-C05** | tomar el mayor exponente |
| `R02` MCM de polinomios | U6 p142 | 54 | **N4-C06** | multiplicar todo |
| `R03` Simplificación | U6 p146 | 33 | N1-B06 fracciones equivalentes | cancelar sumandos, no factores |
| `R04` Suma y resta, igual denominador | U6 p151 | 31 | N2-E01/E02 | no distribuir el menos al restar |
| `R05` Suma y resta, distinto denominador | U6 p153 | 12 | R02 | sumar numeradores y denominadores |
| `R06` Multiplicación | U6 p156 | 24 | N2-E03 | multiplicar sin simplificar antes |
| `R07` División | U6 p159 | 27 | N2-E04 + N3-M05 | invertir la primera fracción |
| `R08` Operaciones combinadas | U6 p162 | 23 | N3 jerarquía | ignorar restricciones del dominio |
| `R09` Fracciones complejas | U6 p165 | 32 | R07 | simplificar por niveles cruzados |
| `R09b` Fracciones continuas *(desvío opcional)* | U6 p165 | 4 | N1-B09 complejos (mismo rol) | — |
| `R10` Cierre — Taller 6 | U6 p166-167 + p169 | 54 | — | — |

**Restricciones del dominio** (`x ≠ …`) atraviesan todo N9 y no existen en preálgebra:
hay 39 ítems con campo `restricciones`. Merecen ser un bloque explícito en `R03`, no una nota.

### N10 — Ecuaciones e inecuaciones (Sala de la balanza)

U7 tiene 95 secciones muy fragmentadas; aquí se consolidan.

| Nodo | Fuente (secciones U7) | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `Q00` Hub | p171 | 6 | — | — |
| `Q01` Identidad vs. ecuación | p175 identidades, partes, p202 clasificación | 24 | N3 propiedades (identidad = siempre cierta) | toda igualdad con letras es ecuación |
| `Q02` `x ± a = b` — la balanza | p175 formas, propiedades, construcción | 30 | **N3-M05 inversos** | pasar el término "cambiando de signo" sin justificar |
| `Q03` Ecuaciones lineales | p177 | 32 | Q02 | dividir solo un lado |
| `Q04` `ax+b = cx+d` | p180 | 41 | O01 términos semejantes | agrupar incógnitas sin cambiar signo |
| `Q05` Con paréntesis y agrupación | p182 | 25 | O02 | distribuir el menos a un solo término |
| `Q06` Ecuaciones racionales | p186 | 47 | R05 + R08 | soluciones extrañas (raíz que anula el denominador) |
| `Q07` Coeficientes literales y fórmulas | p188 + p195 + p203 despejes | 74 | Q03 | despejar sin aislar el factor completo |
| `Q08` Modelación y problemas | p190 traducción → sube a N5; p193 + p202 problemas | 33 | L01 | plantear con la incógnita cambiada |
| `Q09` Desigualdades y la recta | p199 concepto, lectura en la recta | 20 | **N1-B08 recta real** | leer intervalo abierto como cerrado |
| `Q10` Solución de inecuaciones | p199 solución + p201 + p203 | 55 | Q03 + N1 intervalos | no invertir el sentido al multiplicar por negativo |
| `Q11` Cierre — Taller 7 | p202-203 + p205 gases | 45 | — | — |

### N11 — Función lineal (Observatorio) — **incompleto**

Faltan por transcribir p227, 229, 232-235, 237 (7 de 15 páginas). El mapa se cierra cuando estén.

| Nodo | Fuente | Ítems | Resignifica | Trampa |
|---|---|---|---|---|
| `V00` Hub | U8 p207 | 4 | — | — |
| `V01` Concepto de función | U8 p211 | 24 | N1-B10 clasificador (correspondencia) | relación uno-a-muchos como función |
| `V02` Representaciones | U8 p213 | 19 | L04 valor numérico | leer la gráfica por el eje equivocado |
| `V03` Variables | U8 p215 | 23 | L01 | confundir dependiente/independiente |
| `V04` Lineal vs. afín | U8 p217 | 15 | N3-M04 neutro (`b=0`) | toda recta es proporcional |
| `V05` Pendiente | U8 p220 | 35 | N2-E04 razón | pendiente = `Δx/Δy` |
| `V06` Pendiente-intercepto | U8 p222 | 26 | Q07 despeje | leer `b` como pendiente en `y = b + mx` |
| `V07` Punto-pendiente | U8 p225 | 30 | V06 | signo del punto en `y − y₁ = m(x − x₁)` |
| `V08..` (pendiente de transcripción) | p227-237 | — | — | — |

---

## 5. U1 no es un nivel nuevo — enriquece N1–N4

Los 168 ítems de U1 caen sobre nodos ya construidos. No crear nodos:

| Fuente U1 | Destino | Uso |
|---|---|---|
| p10 naturales (10) | `PREALG-N1-B04` | práctica + 3 V/F al mini-diagnóstico |
| p12 enteros (18) | `PREALG-N1-B05` | práctica (11 numéricos) + 4 comparaciones |
| p14 + p17 racionales y decimales (37) | `PREALG-N1-B06` | práctica; los 8 `intervalo` a `B08` |
| p19 irracionales (21) | `PREALG-N1-B07` | los 10 `racionalidad` son mini-diagnóstico listo |
| p23 reales (19) | `PREALG-N1-B08` | práctica + 5 `mismo_valor` |
| p24-25 Taller 1 (54) | `B10`–`B13` | banco de práctica y post-diagnóstico |
| p27 música (9) | `PREALG-N1-B06` apertura | la escala pitagórica es una tabla de fracciones — mejor apertura que la actual |
| U1 completo | `algebra_basica.json` (banco ELO) | excedente calibrado |

---

## 6. Ruteo de ítems y el hueco del motor

`apto_para` ya trae el destino de cada ítem:

| `apto_para` | Destino | Nº |
|---|---|---|
| `practica_numerica` | `practice` con `kind: numeric` | 371 |
| `practica_seleccion` | `practice` con `single_select`/`multi_select` (distractores = tipo de error) | 1.584 |
| `ejemplo_resuelto` | `worked_examples` (2 correctos + 1 trampa por nodo) | 1.514 |
| `procedimiento_abierto` | `procedure_submissions` (revisión IA + docente), nunca autocalificado | 1.751 |

**Hueco real:** 1.385 ítems son `tipo: simbolico` y el motor solo tiene
`numeric` / `text_exact` / `single_select` / `multi_select`. Factorizar o desarrollar un
producto notable **no** tiene respuesta tecleable única (`(x+2)(x+3)` = `(x+3)(x+2)`).
Dos salidas, en este orden:

1. **Sin código nuevo:** convertir el simbólico a `single_select` con 3 distractores derivados
   de la trampa del nodo. Es lo que la pedagogía pide igual (cada distractor diagnostica un
   `tipo_error`), y `scripts/verificar_hipertexto8.py` ya calcula la respuesta correcta con
   sympy para generar el enunciado del distractor a mano.
2. **Con código:** un `input_kind: "symbolic"` en `evaluate_interaction()` que compare con
   `simplify(a − b) == 0` — exactamente el mismo criterio que ya usa el verificador. ~20 líneas
   en `prealgebra.py`, sin tocar repos ni DB.

Recomendación: (1) para los primeros nodos; (2) cuando el volumen lo justifique — a partir de
N8, donde el 90 % de la práctica es simbólica, teclear la respuesta es pedagógicamente superior
a elegir entre cuatro.

---

## 7. Orden de construcción

1. **N5** primero: es el más pequeño (6 nodos, 150 ítems), es la puerta del curso y valida el
   mundo nuevo (Casa de la Sabiduría) antes de invertir en los niveles grandes.
2. **N6** después: introduce la escalera de cierre resignificada (`O08`), que es la pieza
   estructural de la que dependen N8 y N9.
3. **N10** antes que N7/N8 si la prioridad es utilidad curricular inmediata (ecuaciones es lo
   que más se evalúa en 8.°); N7 → N8 → N9 si la prioridad es la coherencia de la resignificación.
4. **N11** al final — bloqueado hasta terminar la transcripción de U8.
5. U1 → N1–N4 se puede hacer en paralelo: es enriquecimiento, no construcción.
