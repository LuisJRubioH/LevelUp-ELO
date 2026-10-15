# De qué ítem sale cada nodo — niveles Monomios → Factorización

Auditoría del 2026-08-13, contra los cinco documentos entregados (N6 Monomios · N7 Polinomios ·
N8 Operaciones con polinomios · N9 Productos notables · N10 Factorización) y los ítems ya
extraídos en `items/source/`.

**Resultado corto:** la estructura de secciones del libro coincide con la estructura de nodos
del documento casi 1:1. **772 ítems** de Hipertexto caen sobre 13 de los 18 nodos sin tener que
reclasificar nada. El único hueco real es N7.

---

## 1 · Cobertura por nodo

| Nodo objetivo | Archivos fuente | Ítems | `simbolico` | numérica | selección | ej. resuelto |
|---|---|---:|---:|---:|---:|---:|
| **B17/B18/B19** monomios | `u3_suma_resta_monomios_p48` | 35 | 22 | 11 | 23 | 22 |
| **B20–B22** polinomios | `u3_apertura_p45` | **6** | 1 | 1 | 3 | 3 |
| **B23/B24** suma y resta | `u3_suma_resta_polinomios_p51` | 40 | 26 | 13 | 26 | 28 |
| **B25** multiplicación | `u3_multiplicacion_monomios_p53` · `…_polinomios_p57` | 63 | 61 | 16 | 44 | 38 |
| **B26** división | `u3_division_p59` · `…_polinomios_p62` · `u3_ruffini_p65` | 100 | 72 | 20 | 67 | 51 |
| **B27** cuadrado de binomio | `u4_productos_notables_p74` · `u4_cuadrado_trinomio_p75` | 71 | 66 | 27 | 44 | 26 |
| **B28** conjugados | `u4_suma_por_diferencia_p77` | 24 | 24 | 7 | 17 | 7 |
| **B29** cubo de binomio | `u4_cubo_binomio_p83` | 44 | 44 | 15 | 34 | 44 |
| **B30** término común | `u4_x_mas_a_por_x_mas_b_p79` | 27 | 23 | 3 | 22 | 9 |
| **B31** factor común y agrupación | `u5_factorizacion_monomios_p101` · `u5_factor_comun_p104` · `u5_agrupacion_p106` | 136 | 82 | 29 | 108 | 91 |
| **B32** cuadrados | `u5_diferencia_cuadrados_p108` · `u5_trinomio_cuadrado_perfecto_p116` · `u5_tcp_adicion_sustraccion_p118` | 94 | 76 | 6 | 87 | 65 |
| **B33** trinomio general | `u5_trinomio_x2n_bxn_c_p120` · `u5_trinomio_ax2n_bxn_c_p122` | 64 | 53 | 4 | 63 | 47 |
| **B34** cubos | `u5_cubos_p111` · `u5_cubo_perfecto_p124` | 68 | 59 | 10 | 64 | 46 |
| | **TOTAL** | **772** | | | | |

### El hueco: N7 Polinomios

El libro **no enseña la clasificación por número de términos como tema propio** — binomio,
trinomio y polinomio aparecen de paso en la apertura de U3. De ahí los 6 ítems.

Se tapa con **Caminos 8**, que sí lo trata como sección:

| Archivo | Ítems |
|---|---:|
| `caminos8/u2_polinomios_p043` | 24 |
| `caminos8/u2_repaso_polinomios_p047` | 18 |
| `caminos8/u2_repaso_lenguaje_monomios_p046` | 21 |
| `caminos8/u2_valor_numerico_p045` | 22 |
| | **85** |

(Los 22 de valor numérico también sirven para alimentar retroactivamente **ALG-N1-L04**, que
hoy tiene la práctica escrita a mano.)

---

## 2 · Hallazgo: las respuestas `simbolico` son sympy, no texto

```json
{ "id": "HT8-U4-P77-A1a",
  "enunciado": "Relaciona $(x+3)(x-3)$ con su producto notable.",
  "respuesta": "x**2 - 9" }
```

Esto cambia el diagnóstico que teníamos en D4. Los **1 385 ítems `simbolico`** no son
inevaluables: su respuesta está en sintaxis de sympy, o sea **es comparable por máquina**.
Lo que no sirve es la comparación por cadena, que es lo que hace `text_exact` hoy —
`x^2-9`, `-9+x^2` y `(x+3)(x-3)` son la misma respuesta y solo una pasaría.

**Lo que habilita:** un comparador `sympy.simplify(a - b) == 0` acepta cualquier forma
equivalente, que es exactamente lo que uno quiere de un ejercicio de álgebra.

**Lo que exige decidir:** parsear entrada de usuario con sympy es un límite de confianza.
`parse_expr` con `evaluate=False`, lista blanca de símbolos y sin `sympify` crudo. No es
gratis y no se hace de pasada.

**Y un segundo uso, más interesante:** con la respuesta en sympy, los **distractores se pueden
derivar aplicando el error focal**. Para `(a+b)²` el distractor es `a**2 + b**2` — el resultado
de cometer la trampa del nodo, no un número al azar. Eso ataca el hueco real de D4, que eran
los distractores.

---

## 3 · Defecto corregido de paso

Los ítems que preguntan «¿cuál es su raíz?» tenían **el radicando como respuesta**:

```
HT8-U5-P108-A2a   «Halla la raíz cuadrada de 4x²»   →  respuesta: 4*x**2   ✗
```

Bug sistemático y en una sola dirección: los inversos («la raíz es X, ¿cuál es el monomio?»)
estaban bien. **11 ítems** corregidos en `u5_diferencia_cuadrados_p108` y `u5_cubos_p111`,
verificados con sympy (`raíz**índice == radicando`) y marcados con `nota_correccion`.

Importaba porque son justo los ítems de entrada de B32 y B34.

---

## 4 · Solape con ALG-N1, que ya está construido

De los 18 nodos del documento, **cuatro pisan territorio ya cubierto** por El Papiro de las
Cuatro Casas:

| Nodo nuevo | Ya existe | Relación |
|---|---|---|
| **B19** suma y resta de monomios | `ALG-N1-O01` la rampa (`combina_no_semejantes`) | **Es el mismo nodo** |
| **B24** resta de polinomios | `ALG-N1-O02` el patio de aparejos (`el_menos_solo_afecta_al_primero`) | **Mismo error focal** |
| **B25** multiplicación | `ALG-N1-O03` el taller de cinceles | O03 es monomio×monomio; B25 extiende a polinomio×polinomio |
| **B26** división | `ALG-N1-O04` la caseta del capataz | O04 es monomio÷monomio; B26 extiende a división larga |

B25 y B26 son extensiones legítimas: el nodo nuevo empieza donde el viejo terminó.

### Resolución · DECIDIDO 2026-08-13

| Nodo | Qué se hace |
|---|---|
| **B17** | Se construye. Nada en Kemet define coeficiente, parte literal ni grado. |
| **B18** | Se construye y hace de **BASE** del nivel: semejantes, opuestos y nulo. O01 daba la definición de semejante de pasada, para poder operar; aquí es el objeto. |
| **B19** | **Se conserva junto a O01, subiendo la dificultad.** O01 opera monomios de una letra; B19 entra con varias letras, exponentes distintos y coeficientes fraccionarios. No es el mismo nodo otra vez: es el mismo concepto con carga real. |
| **B20–B22** | Se construyen. Pero su taxonomía comparte `grado_confundido` en los tres: hay que precisarla (V2-R18). |
| **B23** | **Extiende el trabajo con monomios**: la misma acción —juntar semejantes— ahora sobre expresiones de varios términos. Su tag NO puede ser `combina_no_semejantes`, que es el focal de O01. |
| **B24** | Se construye. Choca con O02 en el concepto; se resuelve como B19, subiendo la carga (paréntesis anidados, restas encadenadas). |
| **B25 · B26** | Extensiones directas de O03 y O04. |

**Y la taxonomía se precisa por operación** (V2-R18): en vez de `signo_perdido` en cinco
nodos, `signo_perdido_en_la_resta_de_polinomios`, `signo_perdido_al_distribuir`,
`signo_perdido_en_el_cubo`. El prefijo agrega por fenómeno, el sufijo enruta.


---

## 5 · Lo que el libro NO ofrece · MEDIDO 2026-08-13

Conteo sobre los **4 656 enunciados** de Hipertexto, Caminos y EPA8:

| Tipo de ítem | Ítems | % |
|---|---:|---:|
| **Decisión de método** | **0** | 0,00 % |
| **Control sin calcular** | **0** | 0,00 % |
| Parámetro / condición | 5 | 0,11 % |
| Contraejemplo | 8 | 0,17 % |
| Detecta-error | 45 | 0,97 % |
| *Construcción inversa* | *81* | *1,74 %* |
| *Verdadero / falso* | *62* | *1,33 %* |
| *Geométrico* | *356* | *7,65 %* |

**El cero de «decisión de método» es estructural, no un descuido.** El índice del libro ya
responde la pregunta: todo lo de la página 108 es diferencia de cuadrados, así que el
estudiante nunca elige el método — llega a él por dónde está parado. Elegir es justo lo que
falla en un examen, donde los ejercicios vienen sin encabezado de sección. Ningún libro
organizado por temas puede entrenar eso.

**Dónde se llenó el hueco:**

- **G05 · La sala de expedición** (`ALG-N3-G05-EXPEDICION`) existe para esto: su práctica es
  decisión de método (E1, E7), control sin calcular (E3, E4), parámetro (E2) y contraejemplo
  (E6). Se apoya en los **46 ítems de `u5_factorizacion_completa_p127`**, que el mapa de la
  sección 1 no había asignado a ningún nodo y que sí piden encadenar casos.
- **G02** lleva dos ítems de parámetro (`¿para qué k es cuadrado perfecto?`) y uno de decisión
  sin abrir.
- **G03** y **G04** llevan uno de control sin calcular cada uno.
- El **detecta-error** de cada nodo está escrito a mano: el libro nunca muestra un
  procedimiento equivocado.

Lo que el libro sí aporta y no esperábamos: **356 ítems geométricos** (área, perímetro, lado
del cuadrado). Material bueno y gratis para las aperturas.
