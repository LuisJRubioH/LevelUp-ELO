# Nodo: Racionales — la fracción es una división — PREALG-N1-B06-RACIONALES-FRACCION-DIVISION

> **Nodo prototipo de la reestructuración a 11 bloques.** Todo lo que se apruebe aquí
> (contrato de claves, segmentación por color en una sola ventana, ruteo de ítems desde
> `items/source/hipertexto8/`) se replica en los ~30 nodos restantes.
> Insumos de banco usados: `u1_decimales_fraccion.json` (28), `u1_racionales.json` (9),
> `u1_aplicacion_musica.json` (9).

## A0. Ficha del nodo (obligatoria antes de redactar)

```yaml
nodo:
  codigo: B06
  titulo: {es: "La fracción es una división", en: "A fraction is a division"}
  nivel: 1                    # conjuntos numéricos
  nivel_educativo: secundaria_baja
  objetivo: "Escribe un reparto como fracción, obtiene su expresión decimal por división y decide si un decimal dado es el valor exacto de esa fracción o solo un recorte."
  prerrequisitos: [PREALG-N1-B04-NATURALES-CONTAR, PREALG-N1-B05-ENTEROS-DEUDA]
  dba: [MEN-MAT-7.1, MEN-MAT-7.2]
  estandar_ebc:
    - "6-7 · Numérico: utilizo números racionales en sus distintas expresiones (fracciones, razones, decimales, porcentajes) para resolver problemas en contextos de medida."
    - "6-7 · Numérico: justifico el uso de representaciones y procedimientos en situaciones de proporcionalidad directa."
  competencia_icfes: [interpretación, argumentación]
  misconception: "El decimal truncado ES el número: 25/7 «es» 3,57142. La fracción y su expresión decimal se tratan como el mismo objeto aunque el decimal se haya cortado; se confunde una aproximación legible con el valor exacto."
  dos_metodos: sí             # división larga  vs.  amplificar a denominador 10^n
  cpa: sí                     # barra repartida → recta numérica → símbolo a/b
  escenario: "El monocordio de Pitágoras — una sola cuerda tensada sobre una tabla, con un puente móvil que la acorta."
  conjunto: [ℚ]
  callejon_opcional: no
  posicion_ruta: "ruta núcleo — tercer nodo (ℕ → ℤ → **ℚ** → 𝕀 → ℝ)"
```

**Chequeo de contexto (regla del catálogo, ≤2 usos por objeto).**
`grep -i` sobre `src/domain/learning/prealgebra.py`: `pintura` 0 · `terreno` 0 · `receta` 0 ·
`presupuesto` 0 · `monocordio` 0 · `cuerda` **2** (N4, «cuerda de medir» para marcar postes).
El monocordio sería el 3.er uso de la palabra *cuerda* pero con referente distinto
(instrumento, no herramienta de medida) y el objeto no reaparece en ningún ejercicio de este
nodo. **Aceptado con nota**; si en la revisión se prefiere cero fricción, el escenario alterno
ya validado es el reparto de una jornada de riego (0 usos).

**Cambio respecto del nodo actual.** El B06 vigente abre con «tres panes para cuatro personas»
(`prealgebra.py:371-380`). `pan` acumula 13 usos en el catálogo y el reparto de panes es el
contexto del *descubrimiento*, no de la apertura. Se mueve: la apertura pasa al monocordio
(lo pide `MAPA_NODOS_ALGEBRA8.md` §5: «la escala pitagórica es una tabla de fracciones —
mejor apertura que la actual») y el reparto de panes se retira por saturación.

---

## PARTE A — Especificación por bloques

### A1. Encabezado
**`[ZONA 1 · EXPLORAR]`**

> ### La fracción es una división
> Ya sabes contar y ya sabes deber. Falta repartir. En este nodo vas a escribir un reparto
> como fracción, a convertirlo en decimal dividiendo, y a decidir cuándo un decimal dice
> *exactamente* lo mismo que la fracción y cuándo solo se le parece.

Sin fórmula, sin definición, sin `ℚ` todavía. La primera aparición de
`\mathbb{Q}=\{a/b : a,b\in\mathbb{Z},\ b\neq 0\}` es en A4 y en ningún lugar antes.

---

### A2. Mini-diagnóstico (3 ítems)
**`[ZONA 1 · EXPLORAR]`** · presentación conversacional, sin cronómetro, sin nota al terminar,
sin la palabra examen/prueba/evaluación. Transición directa a A3.

> **Antes de empezar, tres rápidas.** No hay nota; me sirven para saber por dónde entrarle.

| # | Ítem | Tipo | Origen | Qué mide |
|---|---|---|---|---|
| D1 | ¿Cuál de estos números es menor: $-3$ o $-\dfrac{1}{2}$? | `single_select` | prerrequisito B05 | orden en ℤ y lectura de una fracción como número único |
| D2 | $18 \div 4$ no da un entero. ¿Cuánto sobra? | `numeric` | prerrequisito B04 | división con residuo (el gancho: el residuo es lo que la fracción va a nombrar) |
| D3 | Tres botellas iguales se reparten entre cuatro personas. ¿Cuánta botella recibe cada una? | `single_select` | concepto nuclear | fracción como reparto, antes de enseñarla |

- **D1** opciones: $-3$ ✔ · $-\dfrac{1}{2}$ (*tipo_error:* `magnitud_sin_signo`) · «son iguales» (*tipo_error:* `no_compara_entero_con_fraccion`).
- **D2** respuesta `2`. Regex `numeric` ✔.
- **D3** opciones: $\dfrac{3}{4}$ de botella ✔ · $\dfrac{4}{3}$ de botella (*tipo_error:* `invierte_cociente`) ·
  «no alcanza, sobra 1» (*tipo_error:* `reparto_solo_entero`) · «cada una 1 y sobra» (*tipo_error:* `reparto_solo_entero`).
- Siembran ELO (factor de arranque en frío alto) y **no puntúan** (Pelánek, 2016). El
  conocimiento previo es el mayor moderador de todo lo que sigue, por eso se mide antes de
  enseñar (Sinha & Kapur, 2021).
- Resultado guardado como línea base para A10. El estudiante no ve nada al terminar.

---

### A3. Apertura de KatIA — intento genuino
**`[ZONA 1 · EXPLORAR]`** · `KatiaStorySlot` con ilustración (única del nodo; coherencia,
Mayer, 2021).

> **KatIA · El puente que se mueve**
>
> Pitágoras tenía una tabla con una sola cuerda tensada y un puente que podía deslizar. Cuando
> pulsaba la cuerda entera sonaba una nota. Cuando ponía el puente justo en la mitad, sonaba
> *la misma nota*, más aguda. Con el puente en 2 de cada 3 partes de la cuerda salía la nota
> que a él le parecía la más hermosa de todas.
>
> Dos de cada tres partes. Pero el taller solo tenía reglas marcadas en décimas, y ahí empieza
> el problema.
>
> **¿Qué número debía marcar Pitágoras en su regla para dejar el puente exactamente donde
> suena esa nota?**

**Intento genuino** — formato `acotado` (dosis de `secundaria_baja`), obligatorio, **no
calificado**. El sistema responde «Veámoslo» a cualquier opción; nada se marca en rojo.

- `0{,}66`
- `0{,}666`
- «Ninguno de los dos: solo $\dfrac{2}{3}$ lo dice exacto»

Resolver antes de la instrucción mejora conocimiento conceptual y transferencia sin costo
procedimental, y el beneficio existe desde 6.º grado (Sinha & Kapur, 2021). La cuerda funciona
además como organizador previo: ancla lo nuevo en algo continuo y familiar (Ausubel, 1960).

**Regla dura:** el monocordio, la cuerda, las notas y $\dfrac{2}{3}$ **no vuelven a aparecer**
en A5, A6 ni A8.

---

### A4. Descubrimiento guiado + definición formal
**`[ZONA 2 · CONSTRUIR]`** · dos columnas. Espacio de búsqueda restringido a exactamente dos
casos: la indagación funciona con guía y fracasa sin ella (Lazonder & Harmsen, 2016).

#### Columna izquierda — contraste de dos casos

**CPA (`cpa: sí`)** — cada caso se muestra primero como barra repartida, luego sobre la recta,
luego como símbolo.

| | **Caso que funciona** | **Caso que rompe la expectativa** |
|---|---|---|
| Reparto | 15 litros en 6 baldes | 5 hectáreas entre 9 herederos |
| Concreto | barra de 15 partida en 6 tramos iguales | barra de 5 partida en 9 tramos iguales |
| Fracción | $\dfrac{15}{6}$ | $\dfrac{5}{9}$ |
| Divido | $15 \div 6 = 2{,}5$ — **la división termina** | $5 \div 9 = 0{,}5555\ldots$ — **la división no termina** |
| Pictórico | el punto cae justo sobre una marca de la recta | el punto cae entre marcas, siempre |

> **¿Y entonces $\dfrac{5}{9}$ no es un número?**
> Sí lo es, y es exacto. Lo que no termina es *el intento de escribirlo en decimales*. La
> fracción ya lo dice completo; el decimal es un retrato que a veces no cabe en la hoja.

Este es el punto crítico del nodo y la raíz de la trampa de A5c: la fracción es la
representación **transparente** y el decimal la **opaca** (Zazkis & Sirotic, 2010).

#### Columna derecha — definición formal (después del contraste, nunca antes)

$$\mathbb{Q}=\left\{\dfrac{a}{b}\ :\ a,b\in\mathbb{Z},\ b\neq 0\right\}$$

| Símbolo | Se lee | Qué significa aquí |
|---|---|---|
| $\mathbb{Q}$ | «los racionales» | de *quotient*, cociente: el conjunto de los cocientes |
| $a$ | numerador | **cuánto** se reparte (el dividendo) |
| $b$ | denominador | **entre cuántos** se reparte (el divisor) |
| la barra | «dividido entre» | no es un adorno: **es el signo de dividir** |
| $a,b\in\mathbb{Z}$ | «$a$ y $b$ son enteros» | arriba y abajo pueden ser negativos (traído de B05) |
| $b\neq 0$ | «$b$ distinto de cero» | repartir entre cero baldes no es un reparto |

> **La frase del nodo:** $\dfrac{a}{b}$ **es** $a \div b$. No «se parece a», no «se puede
> convertir en». Es.

Convención declarada y sostenida en todo el nodo: **0 ∈ ℕ**; coma decimal es-CO (`2{,}5`).

---

### A5. Ejemplos resueltos — tres tarjetas
**`[ZONA 2 · CONSTRUIR]`** para (a) y (b) · **`[ZONA 3 · TRAMPA]`** para (c).
Segmentado por pasos: cada paso se revela al tocar (obligatorio en móvil; Mayer, 2021).
Base del bloque: efecto de ejemplos resueltos g = 0,48 en matemáticas (Barbieri et al., 2023).

#### Tarjeta (a) — «15 litros de pintura en 6 baldes» · *fuente banco:* `HT8-U1-P17-A5f`

| Paso | Qué hago | Por qué |
|---|---|---|
| 1 | El reparto es **15 entre 6** → $\dfrac{15}{6}$ | arriba lo que se reparte, abajo entre cuántos |
| 2 | La barra es dividir → calculo $15 \div 6$ | la definición de A4, aplicada |
| 3 | $6 \times 2 = 12$, sobran $3$ | el entero cabe 2 veces |
| 4 | $3$ que sobran entre $6$ → $0{,}5$ | el residuo también se reparte |
| 5 | $\dfrac{15}{6} = 2{,}5$ · **cada balde lleva 2,5 litros** | la división terminó: el decimal es exacto |

> **Autoexplicación focal** (única en todo el nodo, sobre el paso 4):
> *«En el paso 4 el 3 que sobra se vuelve 0,5. ¿Por qué 0,5 y no 3?»*
> Campo corto, una sola pregunta. Los prompts extensos moderan el efecto **a la baja**; el
> beneficio documentado exige que sean breves y dirigidos a un paso (Renkl, 2014; Atkinson,
> Renkl & Merrill, 2003).

#### Tarjeta (b) — «5 hectáreas entre 9 herederos» · *fuente banco:* `HT8-U1-P17-A5h`
Contexto distinto de (a) por exigencia de transferencia (Barbieri et al., 2023).

| Paso | Qué hago | Por qué |
|---|---|---|
| 1 | $\dfrac{5}{9}$ | 5 hectáreas entre 9 |
| 2 | $5 \div 9$: pongo $5{,}000\ldots$ y divido | la barra es dividir |
| 3 | $0{,}5$ · resto 5 · $0{,}55$ · resto 5 · $0{,}555$ · resto 5 | **el resto se repite: nunca va a terminar** |
| 4 | Escribo $0{,}\overline{5}$ | la barra encima marca lo que se repite para siempre |
| 5 | $\dfrac{5}{9} = 0{,}\overline{5}$ | ambas escrituras son exactas; la fracción es la más corta |

Sin autoexplicación (ya se usó la única del nodo en la tarjeta a).

#### Tarjeta (c) — TRAMPA · *fuente banco:* `HT8-U1-P17-A5b`
Encarna la `misconception` de A0. Encabezado inequívoco de error con **icono + color reservado
exclusivamente a trampas en toda la interfaz**.

> ⚠️ **Un estudiante escribió esto. Está mal.**
>
> «La ficha técnica dice $\dfrac{25}{7}$. Yo dividí y me dio $3{,}57142$.
> Entonces $\dfrac{25}{7} = 3{,}57142$.»

**1 · Deslizador de confianza — obligatorio ANTES de revelar nada.**
> *«¿Qué tan seguro estás de dónde falla?»* — deslizador de 0 a 100, fijo, no omitible.
> Alta confianza + corrección produce hipercorrección duradera (Metcalfe, 2017).

**2 · Señalización del error** (resaltado visual sustituye texto, no lo acompaña):
$$3{,}5714\underline{2}\quad\longleftarrow\quad \text{aquí se cortó}$$
La división no había terminado. Siguió: $3{,}571428\,571428\,571428\ldots$

**3 · Contraste con la versión correcta, a un toque.** Comparar incorrecto vs. correcto reduce
concepciones erróneas más que solo ejemplos correctos (Durkin & Rittle-Johnson, 2012; Adams
et al., 2014), y también beneficia a quien viene con bajo rendimiento previo cuando el error
está claramente marcado (Barbieri & Booth, 2016).

| ❌ Lo que escribió | ✅ Lo correcto |
|---|---|
| $\dfrac{25}{7} = 3{,}57142$ | $\dfrac{25}{7} = 3{,}\overline{571428}$ |
| El decimal se cortó donde se acabó la paciencia | El bloque `571428` se repite para siempre |
| $3{,}57142 < \dfrac{25}{7}$ | La **única** escritura corta y exacta es $\dfrac{25}{7}$ |

**4 · Explica-y-corrige** (campo obligatorio, texto libre corto):
> *«¿Por qué $3{,}57142$ no es $\dfrac{25}{7}$? Escribe la igualdad corregida.»*

> **Cierre de la trampa:** un decimal cortado es una **foto** del número, no el número. Cuando
> necesites el valor exacto, la fracción. Cuando necesites leerlo rápido, el decimal
> redondeado — y lo dices: «aproximadamente».

#### Diferenciación por nivel de presentación

| | Básico | Intermedio | Avanzado |
|---|---|---|---|
| (a) 15/6 | los 5 pasos visibles | pasos 3 y 4 en blanco | solo pasos 1 y 5; el resto en blanco |
| (b) 5/9 | los 5 pasos visibles | paso 3 en blanco | solo enunciado y resultado |
| (c) trampa | **idéntica** | **idéntica** | idéntica **+ variante de reto:** «inventa otra fracción donde truncar en 5 cifras dé un error mayor que el de $\dfrac{25}{7}$ y justifica» |
| Andamiaje inicial | máximo, todo expandido | medio | mínimo, colapsado |

La trampa **no se desvanece en ningún nivel**: ni la calibración de confianza ni el
explica-y-corrige son opcionales.

---

### A6. Puente — parcialmente resueltos
**`[ZONA 4 · TRABAJAR]`** · huecos editables dentro del procedimiento. El andamiaje sube o baja
según indicadores **en silencio**, sin anunciar cambios de nivel. Los problemas de
completamiento son la transición entre el ejemplo resuelto y la resolución autónoma
(Sweller & Cooper, 1985; Atkinson, Renkl & Merrill, 2003).

**P1 — falta el último paso** · *fuente banco:* `HT8-U1-P17-A5c` (el libro afirma $\dfrac{32}{5}=6{,}5$; es falso)

> Una receta pide repartir 32 cucharadas de masa en 5 moldes iguales.
> $\dfrac{32}{5} = 32 \div 5$
> $5 \times 6 = 30$, sobran $2$
> $2 \div 5 = 0{,}4$
> $\dfrac{32}{5} = \boxed{\phantom{6{,}4}}$ → **6,4**

**P2 — faltan pasos intermedios** · *fuente banco:* `HT8-U1-P17-A5d` (el libro afirma $\dfrac{69}{5}=12{,}25$; es falso)

> $\dfrac{69}{5} = 69 \div 5$
> $5 \times \boxed{\phantom{13}} = 65$, sobran $\boxed{\phantom{4}}$
> $\boxed{\phantom{4}} \div 5 = \boxed{\phantom{0{,}8}}$
> $\dfrac{69}{5} = \boxed{\phantom{13{,}8}}$ → **13 · 4 · 4 · 0,8 · 13,8**

**P3 — solo el planteamiento (solo Avanzado)** · *fuente banco:* `HT8-U1-P17-A5e`

> $\dfrac{12}{7} = \boxed{\phantom{1{,}\overline{714285}}}$
> Da el resultado como fracción exacta y como decimal, y di cuál de las dos escrituras usarías
> para pegar una etiqueta de 6 caracteres.

| Nivel | Qué recibe |
|---|---|
| Básico | P1 y P2, **ambos** con solo el último paso en blanco |
| Intermedio | P1 último paso · P2 pasos intermedios |
| Avanzado | P3 solo, con P2 disponible bajo demanda |

---

### A7. Comparación de métodos (`dos_metodos: sí`)
**`[ZONA 4 · TRABAJAR]`** · **después del puente, nunca antes.** Comparar métodos mejora
procedimiento y flexibilidad, pero solo cuando el estudiante ya domina al menos uno; en
novatos conviene lo secuencial primero (Rittle-Johnson & Star, 2007; Rittle-Johnson, Star &
Durkin, 2009). Tras A6 el dominio de la división larga está garantizado.

Mismo problema, dos soluciones correctas, lado a lado: **¿cuánto vale $\dfrac{7}{8}$ en decimal?**

| **Método 1 — dividir** | **Método 2 — amplificar a denominador $10^n$** |
|---|---|
| $7 \div 8$ | $\dfrac{7}{8} = \dfrac{7 \times 125}{8 \times 125}$ |
| $8\times0{,}8=6{,}4$ · resto $0{,}6$ | $= \dfrac{875}{1000}$ |
| $8\times0{,}09=0{,}72$… | leo directo: $0{,}875$ |
| $\dfrac{7}{8}=0{,}875$ | $\dfrac{7}{8}=0{,}875$ |
| **Siempre funciona** | **Solo si el denominador se puede llevar a 10, 100, 1000…** |

> **¿Cuál conviene aquí y por qué?**
> Y la de verdad: **¿qué pasa si intentas el método 2 con $\dfrac{5}{9}$?**

El segundo método falla con $\dfrac{5}{9}$ y ese fracaso es el contenido: solo los
denominadores que se factorizan en 2 y 5 llegan a una potencia de 10; los demás son
periódicos. Gancho explícito a **N4-C04 (factorización prima)** y a **B07 (irracionales)**.

---

### A8. Práctica independiente (7 ítems)
**`[ZONA 4 · TRABAJAR]`**, salvo E5 que es **`[ZONA 3 · TRAMPA]`**.
Deslizador de confianza **opcional** (activable por el estudiante), **fijo** en E5.
Todo feedback termina en una acción del estudiante; el botón de cierre **es** la acción, nunca
un «OK» (Hattie & Timperley, 2007; Black & Wiliam, 1998). Objetivo de acierto ≈ 75 %
(Klinkenberg, Straatemeier & van der Maas, 2011).

---

**E1 · `estandar` · `numeric` · dif. 750** — Una jarra de 3 litros se reparte en 4 vasos iguales. ¿Cuántos litros lleva cada vaso?
- Respuesta: `0,75` (regex ✔)
- Distractores no aplican (numérico). `tipo_error` por respuesta capturada: `1,33` → `invierte_cociente` · `0,7` → `trunca_division` · `3` o `4` → `no_divide`.
- **Feedback `invierte_cociente`:** «Dividiste 4 entre 3. Vuelve a leerlo: ¿qué se reparte y entre cuántos? Escribe primero la fracción y después el decimal.» → **acción:** escribir la fracción antes de reintentar.
- Pistas: **n1** «¿Qué cantidad se está repartiendo?» · **n2** «Arriba lo que se reparte, abajo entre cuántos: la barra es el signo de dividir.» · **n3** «$3 \div 4$: $4\times0{,}7=2{,}8$, faltan $0{,}2$…»

**E2 · `estandar` · `numeric` · dif. 800** — Un tanque de 32 litros se vacía en 5 recipientes iguales. ¿Cuántos litros en cada uno?
- Respuesta: `6,4`
- `tipo_error`: `6,5` → **`trunca_o_redondea_sin_decir`** (es exactamente el error del libro en `HT8-U1-P17-A5c`) · `6` → `descarta_residuo`.
- **Feedback `descarta_residuo`:** «Te quedaste con la parte entera y tiraste el resto. Ese resto también se reparte. ¿Cuánto vale $2\div5$?» → **acción:** responder solo esa subpregunta y luego reintentar.
- Pistas: **n1** «¿Cabe 5 en 32 un número exacto de veces?» · **n2** «Sobran 2; reparte esos 2 entre 5.» · **n3** «$32=5\times6+2$, y $2\div5=0{,}4$.»

**E3 · `estandar` · `orden` (`multi_select` ordenado) · dif. 1050** · *fuente banco:* `HT8-U1-P14-A2c`
Ordena de mayor a menor: $\dfrac{8}{6}$, $\dfrac{2}{3}$, $\dfrac{4}{6}$, $\dfrac{1}{2}$
- Esperado (lista, **nunca** `set()`): `["8/6", "2/3", "4/6", "1/2"]` — con $\dfrac{2}{3}=\dfrac{4}{6}$ en empate declarado.
- `tipo_error`: colocar $\dfrac{1}{2}$ primero → `mayor_denominador_mayor_numero` · separar $\dfrac{2}{3}$ y $\dfrac{4}{6}$ como distintos → `no_reconoce_equivalentes`.
- **Feedback `no_reconoce_equivalentes`:** «$\dfrac{2}{3}$ y $\dfrac{4}{6}$ ocupan el mismo punto de la recta. Divide las dos y compara los decimales.» → **acción:** escribir ambos decimales.
- Pistas: **n1** «Si no puedes compararlas de un vistazo, ¿en qué otra forma sabes escribirlas?» · **n2** «Convierte todas a decimal.» · **n3** «$8\div6=1{,}\overline{3}$; sigue con las demás.»

**E4 · `detecta_error` · `single_select` · dif. 900** · *fuente banco:* `HT8-U1-P17-A5d`
> Camila escribió: «$\dfrac{69}{5} = 12{,}25$». **¿Dónde está el error?**

| Opción | `tipo_error` |
|---|---|
| Dividió mal: $5\times12=60$ y le sobran 9, no 1 ✔ | — (correcta) |
| Cortó el decimal antes de tiempo | `confunde_error_con_truncamiento` |
| Puso la fracción al revés | `invierte_cociente` |
| Ningún error, está bien | `valida_sin_verificar` |

- **Feedback `confunde_error_con_truncamiento`:** «Buen reflejo, pero aquí no se cortó nada: $\dfrac{69}{5}$ sí termina. El fallo está en la división misma. Haz $69\div5$ y compara.» → **acción:** entregar el cociente correcto.
- **Feedback `valida_sin_verificar`:** «Compruébalo al revés: $12{,}25\times5$. ¿Da 69?» → **acción:** responder ese producto.
- Pistas: **n1** «¿Cuántas veces cabe 5 en 69?» · **n2** «13 veces y sobran 4.» · **n3** «$4\div5=0{,}8$, entonces el resultado es 13,8.»

**E5 · `trampa` (reaparición de la misconception) · `single_select` · dif. 1000 · confianza FIJA** · *derivado de:* `HT8-U1-P17-A5g`
> ¿Es verdadera o falsa? $\quad\dfrac{10}{3} = 3{,}333$

| Opción | `tipo_error` |
|---|---|
| Falsa: $3{,}333$ está cortado, el exacto es $3{,}\overline{3}$ ✔ | — (correcta) |
| Verdadera, es lo mismo | **`decimal_truncado_es_el_numero`** ← la misconception del nodo |
| Falsa: $\dfrac{10}{3}$ no tiene decimal | `periodico_no_es_numero` |
| Falsa: da $0{,}3$ | `invierte_cociente` |

- **Feedback `decimal_truncado_es_el_numero`** (el importante): «$3{,}333 \times 3 = 9{,}999$, no 10. Se parecen, pero no son el mismo número. Escribe el decimal exacto usando la barra de periodo.» → **acción:** escribir $3{,}\overline{3}$.
- Nota deliberada: en la tarjeta (c) el decimal truncado era **falso**; en el banco existe la variante **verdadera** ($\dfrac{10}{3}=3{,}\overline{3}$, `A5g`). Se reserva para el post-diagnóstico A10 para que el estudiante no aprenda «si tiene decimal largo, marca falso».
- Pistas: **n1** «Multiplica el decimal por 3. ¿Vuelve a darte 10?» · **n2** «Un decimal que se corta siempre queda por debajo del valor real.» · **n3** «$10\div3=3{,}3333\ldots$ sin final; se escribe $3{,}\overline{3}$.»

**E6 · `transferencia` · `single_select` · dif. 1100** — superficie nueva, sin anunciar el tema
> Un plano dice que la pieza mide $\dfrac{4}{9}$ de metro. El operario teclea $0{,}44$ en la
> cortadora. **¿La pieza le va a quedar bien?**

| Opción | `tipo_error` |
|---|---|
| No: $\dfrac{4}{9}=0{,}\overline{4}$; queda un poco corta ✔ | — (correcta) |
| Sí, $0{,}44$ es exactamente $\dfrac{4}{9}$ | `decimal_truncado_es_el_numero` |
| No: queda un poco larga | `direccion_del_truncamiento` |
| No se puede saber sin más datos | `evita_decidir` |

- **Feedback `direccion_del_truncamiento`:** «Vas bien en que no es exacto, pero fíjate hacia dónde: cortar cifras siempre deja el número **por debajo**. Compara $0{,}44$ con $0{,}4444\ldots$» → **acción:** decir cuál de los dos es mayor.
- Pistas: **n1** «¿$0{,}44$ y $0{,}4444\ldots$ son el mismo número?» · **n2** «Divide $4\div9$ y mira si se detiene.» · **n3** «$0{,}44 < 0{,}\overline{4}$: falta material.»

**E7 · `estandar` · `single_select` · dif. 950** — ¿Cuál de estas fracciones da un decimal que **termina**?
$\dfrac{3}{8}$ ✔ · $\dfrac{2}{7}$ (`denominador_no_2_ni_5`) · $\dfrac{5}{6}$ (`denominador_no_2_ni_5`) · $\dfrac{1}{9}$ (`denominador_no_2_ni_5`)
- **Feedback `denominador_no_2_ni_5`:** «Divide y mira dónde se repite el resto. ¿Qué tienen en común los denominadores que sí terminan?» → **acción:** nombrar el factor del denominador de la opción correcta.
- Pistas: **n1** «Prueba a llevar cada denominador a 10, 100 o 1000.» · **n2** «$8\times125=1000$. ¿Y $7$?» · **n3** «Solo terminan las que se factorizan con 2 y 5 (gancho a N4-C04).»

**Cobertura del bloque:** 4 estándar (E1, E2, E3, E7) · 1 `detecta_error` (E4) · 1 reaparición
de trampa (E5) · 1 `transferencia` (E6). Contextos: vasos · tanque · recta numérica · error
ajeno · verificación numérica · taller de corte · estructura del denominador. **Ninguno repite
el monocordio de A3, ni la pintura de A5a, ni las hectáreas de A5b, ni la receta de A6.**

---

### A9. Cierre
**`[ZONA 5 · CERRAR]`**

#### Escalera de cierre (nivel 1) — reutiliza B04 y B05

| Conjunto | ¿Toda división de dos de sus números vive aquí? | El ejemplo que lo rompe / lo salva |
|---|---|---|
| $\mathbb{N}$ | ✗ No | $3 \div 4$ se sale: no hay natural que valga |
| $\mathbb{Z}$ | ✗ No | $3 \div 4$ sigue sin caber; los negativos no ayudaron |
| $\mathbb{Q}$ | ✓ Sí (mientras $b\neq0$) | $3 \div 4 = \dfrac{3}{4}$ — el conjunto se hizo **para** esto |

> Cada peldaño nació de una división que no cabía. Igual que $\mathbb{Z}$ nació de una resta
> que no cabía (B05). El siguiente peldaño (B07) va a nacer de algo que **ninguna** fracción
> puede escribir.

#### Pregunta de abstracción
Con las miniaturas de los tres problemas trabajados lado a lado ($\dfrac{15}{6}$, $\dfrac{5}{9}$, $\dfrac{25}{7}$):

> **¿Qué estructura comparten estos tres problemas?**
> - Los tres son un reparto que no da entero ✔
> - Los tres tienen decimal periódico ✗ (15/6 no)
> - Los tres tienen numerador mayor que el denominador ✗ (5/9 no)
> - Los tres se resuelven con la misma operación: una división de enteros ✔

Buscar la estructura común y no la superficie es el mecanismo de la transferencia
(Peltier & Vannest, 2017 — evidencia de primaria, mecanismo extrapolado **con cautela** a
secundaria baja).

#### Ítem final con protocolo de Pólya (4 micro-pasos visibles)

> Una impresora 3D acepta medidas de máximo 4 decimales. La pieza debe medir $\dfrac{7}{6}$ cm.
> ¿Qué escribes en la máquina y qué error cometes?

| Micro-paso | Contenido |
|---|---|
| **Comprender** | ¿Qué me dan? $\dfrac{7}{6}$ cm y un límite de 4 decimales. ¿Qué me piden? El número a teclear **y** el error. |
| **Planear** | Primero convierto $\dfrac{7}{6}$ a decimal dividiendo. Luego corto en 4 decimales. Luego resto para ver qué perdí. |
| **Ejecutar** | $7\div6 = 1{,}1666\ldots = 1{,}1\overline{6}$ → tecleo $1{,}1667$ (redondeado) → el error es menor que $0{,}0001$ cm. |
| **Comprobar** | $1{,}1667 \times 6 = 7{,}0002 \approx 7$ ✔. Y digo en voz alta: *aproximadamente*, no *igual*. |

Pólya es un protocolo metacognitivo: requiere conocimiento ya adquirido, por eso vive al final
del nodo y no al principio (Schoenfeld, 1987; Foster, 2023).

---

### A10. Post-diagnóstico y footer
**`[ZONA 5 · CERRAR]`**

Tres ítems paralelos a A2, mismo constructo y **distintos números y contextos**:

| # | Ítem | Paralelo de |
|---|---|---|
| PD1 | ¿Cuál es menor: $-2$ o $-\dfrac{1}{4}$? | D1 |
| PD2 | $23 \div 4$ no da entero. Escribe el resultado exacto como fracción. | D2 |
| PD3 | ¿Es verdadera? $\dfrac{10}{3}=3{,}\overline{3}$ | D3 + la trampa **en su variante verdadera** |

PD3 es deliberadamente la versión **verdadera** de E5 (`HT8-U1-P17-A5g`): comprueba que el
estudiante aprendió el criterio y no la heurística «decimal largo ⇒ falso».

```yaml
post_diagnostic:
  compara_con: diagnostic
  resultados_posibles: [avance, sin_evidencia_de_avance]   # "empeoró" NO existe
  trigger_refuerzo: sin_evidencia_avance
  refuerzo: "KatIA abre nombrando el motivo concreto; orden de menor a mayor complejidad:
             (1) fracción como reparto, (2) la barra es dividir, (3) decimal exacto vs. cortado"
  si_persiste: reporte_al_docente
  confirmacion_real_de_dominio: item_demorado_de_recuperacion   # no este post inmediato
```

Desempeño inmediato ≠ retención: el efecto del espaciado vive en la medición demorada
(Murray, Horner & Göbel, 2025). El post-diagnóstico interno **no** confirma dominio; lo hace el
ítem demorado que entra en la racha diaria.

**Footer — estado de dominio**, nunca porcentaje de lectura ni check de completado:
`dominado sin ayuda` / `en consolidación` / `para repasar`.
«Correcto con ayuda» no cuenta como dominio (VanLehn, 2011): un ítem resuelto con pista 2 o 3
queda como `en consolidación` y lo dice: *«resuelto con pista 2»*.

---

### A11. Interacción + accesibilidad

| Interacción | Tipo | Accesibilidad |
|---|---|---|
| D1, D3, E4, E5, E6, E7, PD3 | `single_select` | `aria-label` por opción con la fracción vocalizada («tres cuartos», no «tres barra cuatro»); foco de teclado visible |
| D2, E1, E2, PD2 | `numeric` | teclado numérico con coma; `inputmode="decimal"`; regex `-?\d{1,6}(,\d{1,4})?` |
| E3 | orden (`multi_select` ordenado) | **tap-to-place obligatorio** como alternativa al arrastre (móvil + lector de pantalla) |
| A3 intento | `single_select` acotado | ninguna opción marcada en rojo; `aria-live="polite"` para el «Veámoslo» |
| A5c deslizador | `[componente-deslizador-confianza]` | operable con flechas del teclado; valor anunciado; no bloquea si el usuario prefiere teclear el número |
| A5 pasos | revelar al tocar | cada paso es un `<button>` con `aria-expanded`; `prefers-reduced-motion` respetado |
| A6 huecos | inputs dentro del procedimiento | cada hueco con `aria-label` que nombra el paso, no «campo 1» |
| A4 recta numérica | ilustración CPA | anclajes discretos (paso fijo), nunca arrastre libre; alternativa textual del punto |

**Render KaTeX — verificado, sin bloqueantes.** Todas las expresiones usan `\dfrac`, `\overline`,
`\mathbb{}`, `\neq`, `\in`, `\times`, `\div` y coma con llave (`2{,}5`), todos soportados.
**Riesgo revisado y descartado:** en E3 las opciones $\dfrac{2}{3}$ y $\dfrac{4}{6}$ son
visualmente distintas (numeradores y denominadores distintos) pese a ser el mismo valor — el
empate es contenido, no un fallo de render. En D3 las opciones $\dfrac{3}{4}$ y $\dfrac{4}{3}$
sí se diferencian solo por la posición de los dígitos: **se acompañan de la lectura en texto**
(«tres cuartos de botella» / «cuatro tercios de botella») para que no dependan de leer bien la
fracción — regla 7 de `math-precision-rules.md`.

**Bajo consumo:** una sola ilustración en todo el nodo (A3, `KatiaStorySlot`). A4 usa el
diagrama CPA en SVG inline recolorable. Sin la ilustración, el nodo mantiene toda su
funcionalidad.

---

### A12. Misconceptions → feedback → alerta

| `misconception_tag` | Dónde aparece | Feedback + acción requerida | Alerta | Refuerzo |
|---|---|---|---|---|
| `decimal_truncado_es_el_numero` **(nuclear)** | A5c, E5, E6 | «$3{,}333\times3=9{,}999$, no 10. Escribe el decimal exacto con barra de periodo.» → escribirlo | **alta** si reaparece en E5 **y** E6 | KatIA abre nombrando el motivo; repaso de A4 columna izquierda |
| `invierte_cociente` | D3, E1, E4 | «¿Qué se reparte y entre cuántos? Escribe la fracción antes del decimal.» → escribir la fracción | media | tarjeta (a) de A5 reabierta en modo Básico |
| `descarta_residuo` | E2 | «El resto también se reparte. ¿Cuánto es $2\div5$?» → responder la subpregunta | media | P1 del puente |
| `trunca_o_redondea_sin_decir` | E2 | «6,5 no es 6,4. ¿Redondeaste? Dilo y da el valor exacto.» → dar el exacto | media | A5c |
| `mayor_denominador_mayor_numero` | E3 | «$\dfrac{1}{2}$ y $\dfrac{1}{5}$: divide las dos y compáralas en la recta.» → dar los dos decimales | media | B05 orden + A4 |
| `no_reconoce_equivalentes` | E3 | «$\dfrac{2}{3}$ y $\dfrac{4}{6}$ caen en el mismo punto. Divide y compara.» → dar los dos decimales | baja | A4 pictórico |
| `periodico_no_es_numero` | E5 | «Sí es un número, y exacto. Lo que no termina es su escritura decimal.» → ubicar $\dfrac{10}{3}$ entre 3 y 4 en la recta | **alta** — obstáculo epistemológico (Fischbein et al., 1995); es el que bloquea B07 | A4 caso 2 + adelanto de B07 |
| `denominador_no_2_ni_5` | E7 | «¿Qué tienen en común los denominadores cuyo decimal termina?» → nombrar el factor | baja | A7 método 2 |
| `valida_sin_verificar` | E4 | «Compruébalo al revés: $12{,}25\times5$. ¿Da 69?» → responder el producto | media | micro-paso *comprobar* de A9 |
| `magnitud_sin_signo` | D1 | (diagnóstico: sin feedback correctivo, solo se registra) | — | B05 |
| `direccion_del_truncamiento` | E6 | «Cortar cifras deja el número por debajo. ¿$0{,}44$ o $0{,}\overline{4}$?» → decir cuál es mayor | baja | A5c contraste |

El feedback es específico y accionable, y el resultado modifica lo que sigue — evaluación
formativa de ciclo cerrado (Hattie & Timperley, 2007; Black & Wiliam, 1998). Las alertas altas
se priorizan en la vista docente (Arnold & Pistilli, 2012).

---

### A13. Notas de citas

Afirmaciones del nodo con fuente en punto de uso (solo biblioteca aprobada):

- Mini-diagnóstico como semilla de ELO en arranque frío → Pelánek (2016).
- Conocimiento previo como moderador; intento antes de la instrucción → Sinha & Kapur (2021).
- La cuerda del monocordio como organizador previo → Ausubel (1960).
- Contraste de dos casos con guía → Lazonder & Harmsen (2016); Alfieri et al. (2011).
- Fracción transparente vs. decimal opaco → Zazkis & Sirotic (2010); el decimal es pista, no criterio → Sirotic & Zazkis (2007a).
- Ejemplos resueltos → Barbieri et al. (2023). Autoexplicación breve y focal → Renkl (2014); Atkinson, Renkl & Merrill (2003).
- Trampa (incorrecto vs. correcto) → Durkin & Rittle-Johnson (2012); Adams et al. (2014); también beneficia a bajo rendimiento previo con el error marcado → Barbieri & Booth (2016).
- Deslizador de confianza / hipercorrección → Metcalfe (2017).
- Puente por completamiento y desvanecimiento → Sweller & Cooper (1985); Atkinson, Renkl & Merrill (2003).
- Comparación de métodos después del puente → Rittle-Johnson & Star (2007); Rittle-Johnson, Star & Durkin (2009).
- Acierto objetivo ≈ 75 % → Klinkenberg, Straatemeier & van der Maas (2011).
- Feedback accionable → Hattie & Timperley (2007); Black & Wiliam (1998). Alertas docentes → Arnold & Pistilli (2012).
- Abstracción estructural al cierre → Peltier & Vannest (2017), **con cautela de extrapolación**.
- Pólya como protocolo metacognitivo final → Schoenfeld (1987); Foster (2023).
- Post inmediato ≠ retención → Murray, Horner & Göbel (2025). «Correcto con ayuda» ≠ dominio → VanLehn (2011).
- Rechazo del periódico como número (obstáculo epistemológico) → Fischbein, Jehiam & Cohen (1995).
- Contigüidad, señalización, segmentación, coherencia → Mayer (2021). Carga cognitiva → Sweller (1988).
- ELO privado / error normalizado → Barroso et al. (2021).

**Sin respaldo en la biblioteca (no se fabricó cita):**
- `[SIN RESPALDO — buscar fuente]` La afirmación «el sesgo de número natural lleva a invertir
  el cociente en repartos donde el dividendo es menor que el divisor» (`invierte_cociente`,
  D3/E1). El tag se conserva porque el error está atestiguado en el propio banco, pero la
  explicación causal no tiene fuente aprobada. Candidata a añadir a la biblioteca.
- `[SIN RESPALDO — buscar fuente]` La dosis exacta del intento genuino por nivel educativo
  (acotado en secundaria baja vs. abierto en media) — es una predicción comprobable registrada
  para el piloto, no un hallazgo (declarado así en `03a`, §Bloque 3).

**Bibliografía completa** — ver `references/citation-library.md`; todas las entradas usadas
provienen de las secciones A, B y C de esa biblioteca.

---

### A14. Notas de handoff a Design

#### Estado y ruta
`node_state: actual` · `path_position: ruta núcleo, 3.º de 6` · desbloquea tras B05 ·
desbloquea a B07 · sin rama opcional.

#### ⬛ Segmentación por color — UNA sola ventana (decisión nueva, define la plantilla)

Los 11 bloques viven en **un solo scroll continuo**. No hay tres pantallas ni pestañas. La
lectura se guía por **cinco zonas de color**, no por once: once colores no significan nada, y
la señalización solo funciona si es escasa (Mayer, 2021). Cada zona = riel vertical de 3 px en
el borde izquierdo + eyebrow con el rótulo + fondo de superficie a 4 % del color.

| Zona | Bloques | Rótulo | Token | Significado para el estudiante |
|---|---|---|---|---|
| **1 · Explorar** | 1 Encabezado · 2 Mini-diagnóstico · 3 Apertura + intento | `EXPLORAR` | `--zone-explore` (teal) | «Aquí todavía no hay respuestas correctas.» Nada se marca en rojo en toda la zona. |
| **2 · Construir** | 4 Descubrimiento + definición · 5a · 5b | `CONSTRUIR` | `--zone-build` = `--accent` `#6C63FF` | «Aquí está lo que hay que entender.» Es la zona a la que apuntan todos los enlaces «repasa esto». |
| **3 · Trampa** | 5c · reaparición en E5 | `⚠ ERROR` | `--zone-trap` = `--error` `#EF4444` | **Reservado.** Este color e icono no aparecen en ningún otro lugar de la interfaz — ni en respuestas incorrectas de práctica, que usan estado neutro. |
| **4 · Trabajar** | 6 Puente · 7 Comparación · 8 Práctica | `TU TURNO` | `--zone-work` = `--success` `#22C55E` | «Aquí produces tú.» Es donde viven pistas, feedback con acción y el ELO. |
| **5 · Cerrar** | 9 Cierre + Pólya · 10 Post-diagnóstico · 11 Footer | `CERRAR` | `--zone-close` (neutro `--text-2` con hairline) | «Zoom out: qué comparten los problemas y dónde quedaste.» |

Reglas duras de la segmentación:
1. El color de la **zona 3 es exclusivo**. Una respuesta incorrecta en A8 **no** se pinta de
   `--error`: usa el estado neutro con el feedback accionable. Si el rojo aparece en dos
   contextos, deja de significar «trampa» (`02_diseno_interfaz.md`, §Tarjetas de ejemplos).
2. **El riel es el único portador de color de zona.** El texto del cuerpo no cambia de color
   entre zonas; el contraste AA se mantiene idéntico en las cinco.
3. Transición entre zonas: `scroll-margin-top` + el eyebrow pegado. **Sin** barra de navegación
   por bloques — el scroll continuo es el recorrido y una nav lateral duplicaría la señal.
4. Modo bajo consumo: los rieles se conservan (son 3 px de CSS); lo que se cae es la
   ilustración de A3.
5. Las cinco variables se definen **una vez** en `frontend/src/index.css` junto a la paleta V2,
   nunca hardcodeadas en el componente (regla de tokens del proyecto).

#### Tokens usados
`[componente-botón]` · `[componente-nav-inferior]` · `[asset-mascota: Katia]` ·
`[componente-deslizador-confianza]` · `[estilo-trampa]` (icono + `--zone-trap`) ·
`[componente-riel-zona]` *(nuevo — sale de este nodo)* · `[componente-escalera-pistas]` *(nuevo)*

#### Requisitos visuales
- **A3:** ilustración del monocordio con el puente móvil, en el hueco de `KatiaStorySlot`. Sin
  `imageSrc` cae al placeholder existente. Estilo: revisar `Implementacion/image-prompts/referencias/` antes
  de encargar arte — no inventar estilo nuevo.
- **A4:** diagrama CPA en tres franjas horizontales (barra repartida → recta con el punto →
  símbolo), contiguo a su texto. Prohibida la leyenda aparte (contigüidad espacial).
- **A5c:** el subrayado del dígito donde se cortó el decimal es **señalización**, sustituye
  texto explicativo, no lo acompaña.
- **A6:** los huecos son inputs dentro del procedimiento, no una lista de preguntas debajo.
- **A9:** las tres miniaturas de la pregunta de abstracción, lado a lado, en una fila.

#### 🔧 Estado de implementación por bloque (`implementation-mapping.md`)

| # | Bloque | Clave del dict | Estado |
|---|---|---|---|
| 1 | Encabezado | i18n `prealgebra.n1.b06.story.eyebrow/title` | ✔ existe |
| 2 | Mini-diagnóstico | `diagnostic` | **[PENDIENTE DE RENDERER]** |
| 3 | Apertura KatIA | `katia{eyebrow,title,body,question}` | ✔ parcial |
| 3 | Intento genuino | `katia["attempt"]` | **[PENDIENTE DE RENDERER]** |
| 4 | Descubrimiento + definición | `discovery` + `definition_katex` | ✔ existe (hoy como `sections[]`; migra al par de columnas) |
| 5 | Ejemplos (a)(b) | `worked_examples[]` | ✔ existe |
| 5 | Autoexplicación focal | `worked_examples[0]["self_explanation"]` | **[PENDIENTE DE RENDERER]** |
| 5 | Trampa completa | `confidence_prompt`, `correct_version`, `explain_prompt` en la tarjeta `trap: True` | **[PENDIENTE DE RENDERER]** |
| 6 | Puente | `bridge` | **[PENDIENTE DE RENDERER]** |
| 7 | Comparación de métodos | `method_comparison` | **[PENDIENTE DE RENDERER]** |
| 8 | Práctica | `practice[]` mixto | ✔ parcial — faltan `pistas` n1–n3 y `tipo` de ítem |
| 9 | Cierre escalera | `closure{rows}` | ✔ existe |
| 9 | Abstracción + Pólya | `abstraction_question` + `closing_item` | **[PENDIENTE DE RENDERER]** |
| 10 | Post-diagnóstico | `post_diagnostic` | **[PENDIENTE DE RENDERER]** |
| 11 | Footer estado de dominio | `lesson_progress` | ✔ aproximado |

**8 piezas pendientes de renderer.** Se implementan **una sola vez** en componentes compartidos
consumidos por el molde de N1 y por `LevelTwoLesson` / `LevelThreeLesson` / `LevelFourLesson`.
Ese es el motivo de que este nodo sea el prototipo: al terminarlo queda construida la
infraestructura de los ~30 restantes, y lo que falta en ellos es contenido, no código.

**Migración del B06 vigente:** el nodo actual (`prealgebra.py:353-450`) usa
`content.sections[]` con `i18n_key` por sección y 4 `interactions`. Se conserva
`definition_katex`, se reubica el descubrimiento a la columna izquierda de A4, se retiran los
panes por saturación de contexto y se reescriben las 4 interacciones existentes como parte de
A8 (`Q01`→E1, `Q02`→E3, `Q03`→E7, `Q04` se retira: mezcla clasificación de ℚ/𝕀 y pertenece a B07).
**Paridad i18n es/en obligatoria** para todo texto nuevo, incluidos feedback y pistas.

---

## PARTE B — Ficha técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION",
  "set": "Q",
  "most_specific_sets": ["racional_no_entero", "entero", "natural"],
  "nivel_educativo": "secundaria_baja",
  "dba": ["MEN-MAT-7.1", "MEN-MAT-7.2"],
  "estandar_ebc": ["EBC-6-7-NUM-racionales-representaciones", "EBC-6-7-NUM-justifica-procedimientos"],
  "competencia_icfes": ["interpretacion", "argumentacion"],
  "misconception": "decimal_truncado_es_el_numero",
  "dos_metodos": true,
  "cpa": true,
  "optional_branch": false,
  "default_state": "actual",
  "unlock_after": "PREALG-N1-B05-ENTEROS-DEUDA",
  "unlock_rule": null,
  "skip_penalty": false,
  "elo_bands": ["basico", "intermedio", "avanzado"],
  "i18n_prefix": "prealgebra.n1.b06",
  "bloques": {
    "mini_diagnostico": ["B06-D1", "B06-D2", "B06-D3"],
    "apertura_intento": {
      "formato": "acotado",
      "prompt_key": "prealgebra.n1.b06.katia.attempt.prompt"
    },
    "ejemplos": {
      "a": "B06-EX-A-pintura-15-6",
      "b": "B06-EX-B-hectareas-5-9",
      "trampa": "B06-EX-C-trampa-25-7"
    },
    "puente": ["B06-P1", "B06-P2", "B06-P3"],
    "comparacion_metodos": "B06-CM-7-8",
    "practica": ["B06-E1", "B06-E2", "B06-E3", "B06-E4", "B06-E5", "B06-E6", "B06-E7"],
    "cierre_polya_item": "B06-CIERRE-POLYA-7-6",
    "post_diagnostico": {
      "compara_con": "mini_diagnostico",
      "items": ["B06-PD1", "B06-PD2", "B06-PD3"],
      "trigger_refuerzo": "sin_evidencia_avance"
    }
  },
  "items": [
    {
      "interaction_id": "B06-D1",
      "tipo": "diagnostico",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.d1.prompt",
      "options": ["-3", "-1/2", "iguales"],
      "expected": ["-3"],
      "micro_skill": "orden_en_Z_con_fraccion",
      "tema": "orden",
      "habilidad": "comparar",
      "pensamiento": "numerico",
      "misconception_tags": ["magnitud_sin_signo"],
      "distractores": [
        {"valor": "-1/2", "tipo_error": "magnitud_sin_signo"},
        {"valor": "iguales", "tipo_error": "no_compara_entero_con_fraccion"}
      ],
      "feedback": [],
      "pistas": {"n1": "", "n2": "", "n3": ""},
      "calibracion_confianza": "no",
      "dificultad_inicial": 700,
      "can_retry": false,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-D2",
      "tipo": "diagnostico",
      "type": "numerica",
      "prompt_key": "prealgebra.n1.b06.d2.prompt",
      "options": [],
      "expected": ["2"],
      "micro_skill": "division_con_residuo",
      "tema": "division",
      "habilidad": "calcular",
      "pensamiento": "numerico",
      "misconception_tags": [],
      "distractores": [],
      "feedback": [],
      "pistas": {"n1": "", "n2": "", "n3": ""},
      "calibracion_confianza": "no",
      "dificultad_inicial": 700,
      "can_retry": false,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-D3",
      "tipo": "diagnostico",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.d3.prompt",
      "options": ["3/4", "4/3", "no_alcanza", "una_y_sobra"],
      "expected": ["3/4"],
      "micro_skill": "fraccion_como_reparto",
      "tema": "fraccion",
      "habilidad": "interpretar",
      "pensamiento": "numerico",
      "misconception_tags": ["invierte_cociente", "reparto_solo_entero"],
      "distractores": [
        {"valor": "4/3", "tipo_error": "invierte_cociente"},
        {"valor": "no_alcanza", "tipo_error": "reparto_solo_entero"},
        {"valor": "una_y_sobra", "tipo_error": "reparto_solo_entero"}
      ],
      "feedback": [],
      "pistas": {"n1": "", "n2": "", "n3": ""},
      "calibracion_confianza": "no",
      "dificultad_inicial": 800,
      "can_retry": false,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E1",
      "tipo": "estandar",
      "type": "numerica",
      "prompt_key": "prealgebra.n1.b06.e1.prompt",
      "options": [],
      "expected": ["0,75"],
      "micro_skill": "fraccion_a_decimal_exacto",
      "tema": "fraccion_division",
      "habilidad": "calcular",
      "pensamiento": "numerico",
      "misconception_tags": ["invierte_cociente", "trunca_division"],
      "distractores": [
        {"valor": "1,33", "tipo_error": "invierte_cociente"},
        {"valor": "0,7", "tipo_error": "trunca_division"},
        {"valor": "3", "tipo_error": "no_divide"}
      ],
      "feedback": [
        {"tipo_error": "invierte_cociente", "mensaje_key": "prealgebra.n1.b06.fb.invierte_cociente", "accion_requerida": "escribir_la_fraccion_antes_de_reintentar"},
        {"tipo_error": "trunca_division", "mensaje_key": "prealgebra.n1.b06.fb.trunca_division", "accion_requerida": "dar_el_decimal_completo"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e1.hint1",
        "n2": "prealgebra.n1.b06.e1.hint2",
        "n3": "prealgebra.n1.b06.e1.hint3"
      },
      "calibracion_confianza": "opcional",
      "dificultad_inicial": 750,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E2",
      "tipo": "estandar",
      "type": "numerica",
      "prompt_key": "prealgebra.n1.b06.e2.prompt",
      "options": [],
      "expected": ["6,4"],
      "micro_skill": "division_con_residuo_a_decimal",
      "tema": "fraccion_division",
      "habilidad": "calcular",
      "pensamiento": "numerico",
      "misconception_tags": ["trunca_o_redondea_sin_decir", "descarta_residuo"],
      "distractores": [
        {"valor": "6,5", "tipo_error": "trunca_o_redondea_sin_decir"},
        {"valor": "6", "tipo_error": "descarta_residuo"}
      ],
      "feedback": [
        {"tipo_error": "descarta_residuo", "mensaje_key": "prealgebra.n1.b06.fb.descarta_residuo", "accion_requerida": "responder_2_dividido_5"},
        {"tipo_error": "trunca_o_redondea_sin_decir", "mensaje_key": "prealgebra.n1.b06.fb.redondeo_no_declarado", "accion_requerida": "dar_el_valor_exacto"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e2.hint1",
        "n2": "prealgebra.n1.b06.e2.hint2",
        "n3": "prealgebra.n1.b06.e2.hint3"
      },
      "calibracion_confianza": "opcional",
      "dificultad_inicial": 800,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E3",
      "tipo": "estandar",
      "type": "seleccion_multiple",
      "prompt_key": "prealgebra.n1.b06.e3.prompt",
      "options": ["8/6", "2/3", "4/6", "1/2"],
      "expected": ["8/6", "2/3", "4/6", "1/2"],
      "micro_skill": "ordenar_racionales_via_decimal",
      "tema": "orden",
      "habilidad": "comparar",
      "pensamiento": "numerico",
      "misconception_tags": ["mayor_denominador_mayor_numero", "no_reconoce_equivalentes"],
      "distractores": [
        {"valor": "1/2_primero", "tipo_error": "mayor_denominador_mayor_numero"},
        {"valor": "2/3_y_4/6_separados", "tipo_error": "no_reconoce_equivalentes"}
      ],
      "feedback": [
        {"tipo_error": "no_reconoce_equivalentes", "mensaje_key": "prealgebra.n1.b06.fb.equivalentes", "accion_requerida": "escribir_ambos_decimales"},
        {"tipo_error": "mayor_denominador_mayor_numero", "mensaje_key": "prealgebra.n1.b06.fb.denominador_grande", "accion_requerida": "escribir_ambos_decimales"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e3.hint1",
        "n2": "prealgebra.n1.b06.e3.hint2",
        "n3": "prealgebra.n1.b06.e3.hint3"
      },
      "calibracion_confianza": "opcional",
      "dificultad_inicial": 1050,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": true, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E4",
      "tipo": "detecta_error",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.e4.prompt",
      "options": ["division_mal", "corto_el_decimal", "fraccion_al_reves", "sin_error"],
      "expected": ["division_mal"],
      "micro_skill": "verificar_cociente_ajeno",
      "tema": "fraccion_division",
      "habilidad": "argumentar",
      "pensamiento": "numerico",
      "misconception_tags": ["confunde_error_con_truncamiento", "valida_sin_verificar"],
      "distractores": [
        {"valor": "corto_el_decimal", "tipo_error": "confunde_error_con_truncamiento"},
        {"valor": "fraccion_al_reves", "tipo_error": "invierte_cociente"},
        {"valor": "sin_error", "tipo_error": "valida_sin_verificar"}
      ],
      "feedback": [
        {"tipo_error": "confunde_error_con_truncamiento", "mensaje_key": "prealgebra.n1.b06.fb.no_es_truncamiento", "accion_requerida": "entregar_el_cociente_correcto"},
        {"tipo_error": "valida_sin_verificar", "mensaje_key": "prealgebra.n1.b06.fb.verifica_al_reves", "accion_requerida": "responder_12_25_por_5"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e4.hint1",
        "n2": "prealgebra.n1.b06.e4.hint2",
        "n3": "prealgebra.n1.b06.e4.hint3"
      },
      "calibracion_confianza": "opcional",
      "dificultad_inicial": 900,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E5",
      "tipo": "trampa",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.e5.prompt",
      "options": ["falsa_truncado", "verdadera", "falsa_sin_decimal", "falsa_0_3"],
      "expected": ["falsa_truncado"],
      "micro_skill": "distinguir_exacto_de_truncado",
      "tema": "decimal_periodico",
      "habilidad": "argumentar",
      "pensamiento": "numerico",
      "misconception_tags": ["decimal_truncado_es_el_numero", "periodico_no_es_numero"],
      "distractores": [
        {"valor": "verdadera", "tipo_error": "decimal_truncado_es_el_numero"},
        {"valor": "falsa_sin_decimal", "tipo_error": "periodico_no_es_numero"},
        {"valor": "falsa_0_3", "tipo_error": "invierte_cociente"}
      ],
      "feedback": [
        {"tipo_error": "decimal_truncado_es_el_numero", "mensaje_key": "prealgebra.n1.b06.fb.truncado_no_es_exacto", "accion_requerida": "escribir_3_periodo_3"},
        {"tipo_error": "periodico_no_es_numero", "mensaje_key": "prealgebra.n1.b06.fb.periodico_si_es_numero", "accion_requerida": "ubicar_10_3_en_la_recta"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e5.hint1",
        "n2": "prealgebra.n1.b06.e5.hint2",
        "n3": "prealgebra.n1.b06.e5.hint3"
      },
      "calibracion_confianza": "fija",
      "dificultad_inicial": 1000,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E6",
      "tipo": "transferencia",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.e6.prompt",
      "options": ["no_queda_corta", "si_exacto", "no_queda_larga", "no_se_puede_saber"],
      "expected": ["no_queda_corta"],
      "micro_skill": "aplicar_exacto_vs_truncado_en_contexto_nuevo",
      "tema": "decimal_periodico",
      "habilidad": "modelar",
      "pensamiento": "numerico",
      "misconception_tags": ["decimal_truncado_es_el_numero", "direccion_del_truncamiento"],
      "distractores": [
        {"valor": "si_exacto", "tipo_error": "decimal_truncado_es_el_numero"},
        {"valor": "no_queda_larga", "tipo_error": "direccion_del_truncamiento"},
        {"valor": "no_se_puede_saber", "tipo_error": "evita_decidir"}
      ],
      "feedback": [
        {"tipo_error": "direccion_del_truncamiento", "mensaje_key": "prealgebra.n1.b06.fb.direccion_truncamiento", "accion_requerida": "decir_cual_es_mayor"},
        {"tipo_error": "evita_decidir", "mensaje_key": "prealgebra.n1.b06.fb.decide_con_lo_que_hay", "accion_requerida": "dividir_4_entre_9_y_comparar"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e6.hint1",
        "n2": "prealgebra.n1.b06.e6.hint2",
        "n3": "prealgebra.n1.b06.e6.hint3"
      },
      "calibracion_confianza": "opcional",
      "dificultad_inicial": 1100,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-E7",
      "tipo": "estandar",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.e7.prompt",
      "options": ["3/8", "2/7", "5/6", "1/9"],
      "expected": ["3/8"],
      "micro_skill": "predecir_decimal_finito_por_denominador",
      "tema": "decimal_finito",
      "habilidad": "argumentar",
      "pensamiento": "numerico",
      "misconception_tags": ["denominador_no_2_ni_5"],
      "distractores": [
        {"valor": "2/7", "tipo_error": "denominador_no_2_ni_5"},
        {"valor": "5/6", "tipo_error": "denominador_no_2_ni_5"},
        {"valor": "1/9", "tipo_error": "denominador_no_2_ni_5"}
      ],
      "feedback": [
        {"tipo_error": "denominador_no_2_ni_5", "mensaje_key": "prealgebra.n1.b06.fb.denominador_2_y_5", "accion_requerida": "nombrar_el_factor_del_denominador"}
      ],
      "pistas": {
        "n1": "prealgebra.n1.b06.e7.hint1",
        "n2": "prealgebra.n1.b06.e7.hint2",
        "n3": "prealgebra.n1.b06.e7.hint3"
      },
      "calibracion_confianza": "opcional",
      "dificultad_inicial": 950,
      "can_retry": true,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-PD1",
      "tipo": "diagnostico",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.pd1.prompt",
      "options": ["-2", "-1/4", "iguales"],
      "expected": ["-2"],
      "micro_skill": "orden_en_Z_con_fraccion",
      "tema": "orden",
      "habilidad": "comparar",
      "pensamiento": "numerico",
      "misconception_tags": ["magnitud_sin_signo"],
      "distractores": [{"valor": "-1/4", "tipo_error": "magnitud_sin_signo"}],
      "feedback": [],
      "pistas": {"n1": "", "n2": "", "n3": ""},
      "calibracion_confianza": "no",
      "dificultad_inicial": 700,
      "can_retry": false,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-PD2",
      "tipo": "diagnostico",
      "type": "opcion_unica",
      "prompt_key": "prealgebra.n1.b06.pd2.prompt",
      "options": ["23/4", "4/23", "5_sobra_3", "no_se_puede"],
      "expected": ["23/4"],
      "micro_skill": "escribir_division_no_exacta_como_fraccion",
      "tema": "fraccion_division",
      "habilidad": "interpretar",
      "pensamiento": "numerico",
      "misconception_tags": ["invierte_cociente", "reparto_solo_entero"],
      "distractores": [
        {"valor": "4/23", "tipo_error": "invierte_cociente"},
        {"valor": "5_sobra_3", "tipo_error": "reparto_solo_entero"},
        {"valor": "no_se_puede", "tipo_error": "reparto_solo_entero"}
      ],
      "feedback": [],
      "pistas": {"n1": "", "n2": "", "n3": ""},
      "calibracion_confianza": "no",
      "dificultad_inicial": 800,
      "can_retry": false,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    },
    {
      "interaction_id": "B06-PD3",
      "tipo": "diagnostico",
      "type": "vf",
      "prompt_key": "prealgebra.n1.b06.pd3.prompt",
      "options": ["verdadera", "falsa"],
      "expected": ["verdadera"],
      "micro_skill": "distinguir_exacto_de_truncado",
      "tema": "decimal_periodico",
      "habilidad": "argumentar",
      "pensamiento": "numerico",
      "misconception_tags": ["periodico_no_es_numero"],
      "distractores": [{"valor": "falsa", "tipo_error": "periodico_no_es_numero"}],
      "feedback": [],
      "pistas": {"n1": "", "n2": "", "n3": ""},
      "calibracion_confianza": "no",
      "dificultad_inicial": 1000,
      "can_retry": false,
      "affects_elo": true,
      "accessibility": {"drag_alt_tap_to_place": false, "math_aria": true, "discrete_number_line": false}
    }
  ],
  "level_presentation": {
    "basico": {"worked_example": "full", "puente": "ultimo_paso", "default_expanded": true},
    "intermedio": {"worked_example": "partial", "puente": "intermedios"},
    "avanzado": {"worked_example": "faded", "puente": "solo_planteamiento", "challenge_variant": true}
  },
  "design_handoff": {
    "node_state": "actual",
    "path_position": "ruta_nucleo_3_de_6",
    "zonas_color": {
      "explorar": ["encabezado", "mini_diagnostico", "apertura_intento"],
      "construir": ["descubrimiento_definicion", "ejemplo_a", "ejemplo_b"],
      "trampa": ["ejemplo_c", "B06-E5"],
      "trabajar": ["puente", "comparacion_metodos", "practica"],
      "cerrar": ["cierre_polya", "post_diagnostico", "footer"]
    },
    "tokens": [
      "[componente-botón]",
      "[componente-nav-inferior]",
      "[asset-mascota: Katia]",
      "[componente-deslizador-confianza]",
      "[estilo-trampa]",
      "[componente-riel-zona]",
      "[componente-escalera-pistas]"
    ]
  },
  "fuentes_banco": {
    "ejemplo_a": "HT8-U1-P17-A5f",
    "ejemplo_b": "HT8-U1-P17-A5h",
    "ejemplo_c_trampa": "HT8-U1-P17-A5b",
    "puente_p1": "HT8-U1-P17-A5c",
    "puente_p2": "HT8-U1-P17-A5d",
    "puente_p3": "HT8-U1-P17-A5e",
    "practica_e3": "HT8-U1-P14-A2c",
    "practica_e4": "HT8-U1-P17-A5d",
    "practica_e5": "HT8-U1-P17-A5g (variante truncada)",
    "post_pd3": "HT8-U1-P17-A5g",
    "apertura_escenario": "u1_aplicacion_musica.json (monocordio pitagórico)"
  }
}
```
