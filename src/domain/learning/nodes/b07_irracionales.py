"""B07 · Irracionales — no toda medida cabe en una fracción.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «si el decimal no termina, es irracional» — confunde
periódico (racional) con no-periódico (irracional).
"""

NODE_ID = "PREALG-N1-B07-IRRACIONALES-DECIMALES"
CONCEPT_SLUG = "irracionales"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "irracionales",
    "misconception": "decimal_infinito_es_irracional",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Cuarto peldaño · Irracionales",
    "scene": {
        "image": "/leccion/00-comunes/step-irracionales.png",
        "step": "irrationals",
        "aria": "Los irracionales son los reales que no son racionales: erre menos cu",
    },
    "finish_label": "Continuar a reales",
    "title": "No toda medida cabe en una fracción",
    "intro": (
        "En el peldaño anterior aprendiste que una fracción es una división y que su "
        "decimal a veces no termina. Aquí viene la parte incómoda: existen medidas "
        "reales, dibujables con regla, que NINGUNA fracción puede escribir. Y aprender "
        "a reconocerlas no es mirar si el decimal es largo."
    ),
    # --- Bloque 2 · Mini-diagnóstico (siembra ELO, no puntúa) ----------------
    "diagnostic": {
        "intro": (
            "Antes de empezar, tres rápidas. No hay nota; me sirven para saber por "
            "dónde entrarle."
        ),
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"$\dfrac{1}{3}=0{,}333\ldots$ ¿Ese número es racional o irracional?",
                "options": [
                    {"id": "rational", "text": "Racional: viene de una fracción"},
                    {"id": "irrational", "text": "Irracional: su decimal no termina"},
                    {"id": "neither", "text": "Ninguno de los dos"},
                ],
                "expected": "rational",
                "misconception_by_option": {
                    "irrational": "decimal_infinito_es_irracional",
                    "neither": "habito_evita_decidir",
                },
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Un cuadrado tiene lado 1. ¿Cuánto vale el área de ese cuadrado?",
                "answer": "1",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es cierto que $\pi=\dfrac{22}{7}$?",
                "options": [
                    {"id": "no_approx", "text": "No: 22/7 solo se le parece"},
                    {"id": "yes", "text": "Sí, es la fracción de π"},
                    {"id": "no_other", "text": "No, pero existe otra fracción que sí lo da exacto"},
                ],
                "expected": "no_approx",
                "misconception_by_option": {
                    "yes": "pi_es_una_fraccion",
                    "no_other": "todo_numero_es_fraccion",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · El cuarto peldaño",
        "title": "La diagonal que rompió la escuela",
        "body": (
            "Los pitagóricos creían algo hermoso y lo creían de verdad: que todo en el "
            "mundo se podía escribir como razón de dos números enteros. Toda longitud, "
            "toda nota musical, toda proporción.\n\n"
            "Entonces alguien dibujó en una baldosa un cuadrado de lado 1 y trazó su "
            "diagonal. Una raya. La cosa más simple del mundo. Y se pusieron a buscar la "
            "fracción que diera esa longitud exacta. Probaron 7/5. Probaron 17/12. "
            "Probaron 99/70. Cada una se acercaba más, y ninguna daba."
        ),
        "question": (
            "¿Crees que no la encontraron porque no buscaron lo suficiente, o porque esa "
            "fracción no existe?"
        ),
        "image": "/leccion/01-prealg-n1-agora/b07-irracionales-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "Existe, solo que con números muy grandes"},
                {"id": "b", "text": "No existe ninguna fracción que la dé exacta"},
                {"id": "c", "text": "La diagonal no es un número de verdad"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber que se "
                "puede DEMOSTRAR cuál de las tres es la correcta, no solo sospecharlo."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos decimales infinitos que no se parecen en nada",
        "body": (
            "Los dos decimales de abajo siguen para siempre. Si tu criterio para decidir "
            "es «no termina», los vas a clasificar igual — y son de familias distintas. "
            "Mira qué hace cada uno."
        ),
        "cases": [
            {
                "label": "Caso que ya sabías",
                "context": "Tres partes de once de una jarra de aceite",
                "fraction": r"\dfrac{3}{11}",
                "division": r"3\div11=0{,}\overline{27}",
                "note": (
                    "No termina, PERO se repite: 27, 27, 27, para siempre. Ese patrón es "
                    "la huella de una fracción. Es racional."
                ),
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "La diagonal del cuadrado de lado 1",
                "fraction": r"\sqrt{2}",
                "division": r"\sqrt{2}=1{,}41421356\ldots",
                "note": (
                    "No termina Y no se repite nunca: no hay bloque que vuelva. Sin patrón "
                    "no hay fracción. Es irracional."
                ),
            },
        ],
        "resolution": (
            "El criterio no es «¿termina?». Es «¿se repite?». Un decimal que termina o "
            "que se repite viene de una fracción. Uno que sigue para siempre SIN repetirse "
            "no viene de ninguna, y no porque no la hayamos encontrado: se puede demostrar "
            "que no existe. Eso es lo que descubrieron los pitagóricos, y no les gustó nada."
        ),
    },
    "definition_title": "Los números irracionales",
    "definition_katex": r"\mathbb{I}=\mathbb{R}\setminus\mathbb{Q}=\left\{x\ :\ x\neq\dfrac{a}{b}\ \text{con}\ a,b\in\mathbb{Z}\right\}",
    "definition": (
        "La frase del nodo: irracional no significa «raro» ni «muy largo». Significa una "
        "sola cosa: que no se puede escribir como fracción de enteros."
    ),
    "definition_symbols": [
        {
            "symbol": r"\mathbb{I}",
            "reads": "los irracionales",
            "means": "los que NO son razón (ratio) de dos enteros",
        },
        {
            "symbol": r"\setminus",
            "reads": "menos, quitando",
            "means": "ℝ quitándole ℚ: lo que queda de la recta al sacar las fracciones",
        },
        {
            "symbol": r"\sqrt{2}",
            "reads": "raíz de dos",
            "means": "el número que multiplicado por sí mismo da 2; mide la diagonal del cuadrado de lado 1",
        },
        {
            "symbol": r"\pi",
            "reads": "pi",
            "means": "cuántas veces cabe el diámetro en el contorno de un círculo",
        },
        {
            "symbol": r"0{,}\overline{27}",
            "reads": "cero coma veintisiete periódico",
            "means": "la barra marca el bloque que se repite: esto SÍ es racional",
        },
        {
            "symbol": r"\notin\mathbb{Q}",
            "reads": "no pertenece a ℚ",
            "means": "la prueba de irracionalidad: no hay fracción que lo dé",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · El periódico que SÍ es fracción",
            "title": "El mosaico del alfarero",
            "statement": (
                "El alfarero divide una franja de mosaico en 11 partes iguales y toma 3. "
                "Su decimal es 0,272727… ¿Es racional o irracional?"
            ),
            "latex": r"0{,}\overline{27}=\dfrac{3}{11}",
            "image_slot": False,
            "steps": [
                "Escribo el reparto como fracción: 3 partes de 11 → 3/11.",
                "Divido: 3 ÷ 11 = 0,272727…",
                "Miro si hay patrón: el bloque 27 se repite sin cambiar. Sí lo hay.",
                "Un decimal con bloque que se repite SIEMPRE viene de una fracción.",
                "Como 3/11 es fracción de enteros, el número es racional. El decimal infinito no cambia eso.",
            ],
            "solution": r"$0{,}\overline{27}=\dfrac{3}{11}\in\mathbb{Q}$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 2,
                "prompt": (
                    "En el paso 3 busqué un patrón en vez de mirar si el decimal terminaba. "
                    "¿Por qué «termina» no sirve como criterio y «se repite» sí?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El que no puede ser fracción",
            "title": "La diagonal de la baldosa",
            "statement": (
                "Una baldosa cuadrada mide 1 palmo de lado. ¿Se puede escribir su diagonal "
                "como fracción de enteros?"
            ),
            "latex": r"\sqrt{2}",
            "image_slot": False,
            "steps": [
                "La diagonal d cumple d × d = 2, porque el cuadrado de lado 1 tiene esa relación.",
                "Supongamos que SÍ existe: d = a/b, ya simplificada al máximo (sin factores comunes).",
                "Entonces a × a = 2 × (b × b), así que a×a es par, y por tanto a también es par.",
                "Si a es par, a = 2k, y al sustituir sale que b×b también es par: b es par.",
                "Pero a y b pares se contradice con «ya simplificada al máximo». La suposición era falsa: esa fracción NO existe.",
            ],
            "solution": r"$\sqrt{2}\notin\mathbb{Q}$: no es que no se haya encontrado, es que no existe.",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El decimal largo que se clasificó mal",
            "statement": (
                "Un discípulo entregó esta clasificación. Está mal: «0,333… es irracional, "
                "porque tiene infinitas cifras y nunca termina. Y 3,14 es racional, porque "
                "es corto y termina»."
            ),
            "latex": r"0{,}\overline{3}\in\mathbb{I}\ \ \text{y}\ \ 3{,}14=\pi",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\text{criterio usado}:\ \underline{\text{¿termina?}}",
            "error_note": (
                "Aquí se cayó, y las dos veces por lo mismo: usó el largo del decimal como "
                "criterio. El largo no decide nada; el PATRÓN sí."
            ),
            "correct_version": {
                "wrong_latex": r"0{,}\overline{3}\in\mathbb{I}",
                "right_latex": r"0{,}\overline{3}=\dfrac{1}{3}\in\mathbb{Q}",
                "rows": [
                    {
                        "wrong": "0,333… no termina, luego es irracional",
                        "right": "0,333… se repite, luego es 1/3: racional",
                    },
                    {
                        "wrong": "3,14 termina, luego es π y es racional",
                        "right": "3,14 sí es racional (= 157/50), pero NO es π: π es irracional",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué «no termina» no alcanza para decir irracional? Escribe el "
                "criterio correcto."
            ),
            "steps": [
                "Divide 1 ÷ 3 y mira qué hace el resto.",
                "El resto se repite, así que el decimal repite un bloque: eso delata una fracción.",
                "Ahora mira las cifras de √2: 1,41421356… ¿ves algún bloque que vuelva?",
            ],
            "solution": (
                "El criterio es el patrón, no la longitud. Termina o se repite → racional. "
                "Infinito SIN repetirse → irracional. Y ojo con el segundo error: 3,14 es "
                "una aproximación de π, no π. Escribir π = 3,14 es el mismo pecado que "
                "escribir 25/7 = 3,57142 en el nodo anterior."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: la clasificación ya está "
            "empezada y solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Clasifica 0,625. El alfarero lo obtuvo repartiendo 5 entre 8.",
                "given_steps": [
                    r"0{,}625=\dfrac{5}{8}",
                    r"\text{decimal termina}\Rightarrow\text{viene de fracción}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Denominador de la fracción}=", "answer": "8"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "De esta lista, cuenta los irracionales: "
                    "0,5 · √9 · √2 · 2/7 · π · 1,101101110…"
                ),
                "given_steps": [
                    r"\sqrt{9}=3\ \Rightarrow\ \text{racional}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{Racionales en la lista}=", "answer": "3"},
                    {"id": "P2-b2", "label": r"\text{Irracionales en la lista}=", "answer": "3"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: una baldosa cuadrada tiene área 16 palmos "
                    "cuadrados. ¿Cuánto mide su lado, y ese número es racional o irracional? "
                    "Responde con la medida del lado."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Lado}=", "answer": "4"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos caminos para decidir si un número es racional",
        "intro": (r"¿Es $\sqrt{25}$ racional? Las dos soluciones de abajo son correctas."),
        "methods": [
            {
                "label": "Método 1 · Mirar el decimal",
                "steps": [r"\sqrt{25}=5{,}0", r"\text{termina}", r"\Rightarrow\ \text{racional}"],
                "note": "Rápido, pero solo concluye cuando el decimal termina o se repite.",
            },
            {
                "label": "Método 2 · Buscar la fracción",
                "steps": [r"\sqrt{25}=5", r"5=\dfrac{5}{1}", r"\Rightarrow\ \text{racional}"],
                "note": "Más lento, pero es la definición misma.",
            },
        ],
        "question": (
            r"¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si aplicas el "
            r"método 1 a $\sqrt{2}$ con una calculadora de 8 cifras?"
        ),
        "insight": (
            "El método 1 falla justo donde importa: la calculadora muestra 1,41421356 y "
            "corta, y si te fías de la pantalla concluyes «termina, es racional». La "
            "pantalla es una foto, igual que el decimal cortado de B06. Solo el método 2 "
            "—buscar la fracción, o demostrar que no existe— decide de verdad."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "De esta lista, ¿cuántos son IRRACIONALES? "
                "√4 · √3 · 0,75 · π · 1/6 · 2,010010001…"
            ),
            "expr": r"\sqrt{4},\ \sqrt{3},\ 0{,}75,\ \pi,\ \tfrac{1}{6},\ 2{,}010010001\ldots",
            "answer": "3",
            "hints": {
                "n1": "Empieza por descartar: ¿cuáles vienen claramente de una fracción?",
                "n2": "√4 = 2 y 1/6 = 0,1666… son racionales; 0,75 también.",
                "n3": "Quedan √3, π y el que va agregando ceros sin repetir bloque.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una baldosa cuadrada tiene área 49 palmos cuadrados. ¿Cuánto mide su lado?",
            "expr": r"\sqrt{49}",
            "answer": "7",
            "hints": {
                "n1": "El lado por sí mismo debe dar el área.",
                "n2": "Busca el número que multiplicado por sí mismo da 49.",
                "n3": "7 × 7 = 49, así que este sí es racional (no toda raíz es irracional).",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estos números NO es racional?",
            "options": [
                {"id": "sqrt5", "text": "√5", "latex": r"\sqrt{5}"},
                {"id": "periodic", "text": "0,8181…", "latex": r"0{,}\overline{81}"},
                {"id": "sqrt36", "text": "√36", "latex": r"\sqrt{36}"},
                {"id": "neg_frac", "text": "−7/4", "latex": r"-\dfrac{7}{4}"},
            ],
            "expected": "sqrt5",
            "feedback_by_option": {
                "sqrt5": "correct",
                "periodic": "fb_b07_e3_periodic",
                "sqrt36": "fb_b07_e3_root",
                "neg_frac": "fb_b07_e3_negative",
            },
            "misconception_by_option": {
                "periodic": "decimal_infinito_es_irracional",
                "sqrt36": "toda_raiz_es_irracional",
                "neg_frac": "negativo_no_es_racional",
            },
            "hints": {
                "n1": "Tres de los cuatro se pueden escribir como fracción de enteros.",
                "n2": "√36 = 6 y 0,8181… = 9/11.",
                "n3": "5 no es cuadrado de ningún entero, así que √5 no cierra en ninguna fracción.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un discípulo anotó: «Medí el contorno de la rueda y el diámetro, dividí, "
                "y me dio 3,1428. Entonces π = 3,1428 y π es racional». ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "measurement",
                    "text": "Su medida es una aproximación; π no es igual a ningún decimal que él pueda escribir",
                },
                {
                    "id": "divided_wrong",
                    "text": "Dividió al revés: debía dividir diámetro entre contorno",
                },
                {"id": "not_pi", "text": "El contorno entre el diámetro no da π"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "measurement",
            "feedback_by_option": {
                "measurement": "correct",
                "divided_wrong": "fb_b07_e4_inverted",
                "not_pi": "fb_b07_e4_definition",
                "none": "fb_b07_e4_none",
            },
            "misconception_by_option": {
                "divided_wrong": "invierte_cociente",
                "not_pi": "desconoce_definicion_pi",
                "none": "pi_es_una_fraccion",
            },
            "hints": {
                "n1": "El procedimiento (contorno ÷ diámetro) está bien: eso SÍ es π.",
                "n2": "El problema es que midió con una cuerda, y toda medida real es aproximada.",
                "n3": "Ningún decimal que quepa en su tablilla es π: π no termina ni se repite.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Si un decimal no termina, el número es irracional.»",
            "options": [
                {"id": "false_periodic", "text": "Falsa: 0,333… no termina y es 1/3, racional"},
                {
                    "id": "true_rule",
                    "text": "Verdadera: no terminar es la definición de irracional",
                },
                {
                    "id": "false_all_finite",
                    "text": "Falsa: todos los decimales terminan en algún punto",
                },
                {"id": "depends", "text": "Depende de con cuántas cifras lo escribas"},
            ],
            "expected": "false_periodic",
            "feedback_by_option": {
                "false_periodic": "correct",
                "true_rule": "fb_b07_e5_trap",
                "false_all_finite": "fb_b07_e5_finite",
                "depends": "fb_b07_e5_depends",
            },
            "misconception_by_option": {
                "true_rule": "decimal_infinito_es_irracional",
                "false_all_finite": "todo_decimal_termina",
                "depends": "representacion_define_el_numero",
            },
            "hints": {
                "n1": "Busca un contraejemplo entre los decimales que ya conoces.",
                "n2": "1/3 = 0,333… no termina. ¿Y es irracional?",
                "n3": "No: viene de una fracción. El criterio es si se REPITE, no si termina.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El agrimensor debe marcar en el muro una longitud de √2 palmos exactos. "
                "Solo tiene una regla graduada en centésimas de palmo. ¿Qué puede hacer?"
            ),
            "options": [
                {
                    "id": "construct",
                    "text": "Trazar la diagonal de un cuadrado de lado 1: eso da √2 exacto, sin regla",
                },
                {"id": "measure", "text": "Marcar 1,41 palmos: es exactamente √2"},
                {"id": "impossible", "text": "Nada: √2 no existe como longitud"},
                {"id": "fraction", "text": "Buscar la fracción de √2 y convertirla a centésimas"},
            ],
            "expected": "construct",
            "feedback_by_option": {
                "construct": "correct",
                "measure": "fb_b07_e6_measure",
                "impossible": "fb_b07_e6_impossible",
                "fraction": "fb_b07_e6_fraction",
            },
            "misconception_by_option": {
                "measure": "decimal_truncado_es_el_numero",
                "impossible": "irracional_no_existe",
                "fraction": "todo_numero_es_fraccion",
            },
            "hints": {
                "n1": "Vuelve a la historia de la apertura: ¿de dónde salió √2?",
                "n2": "Salió de una construcción con regla, no de una medición.",
                "n3": "Ser irracional impide ESCRIBIRLO como fracción, no DIBUJARLO.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estas raíces da un número racional?",
            "options": [
                {"id": "sqrt64", "text": "√64", "latex": r"\sqrt{64}"},
                {"id": "sqrt2", "text": "√2", "latex": r"\sqrt{2}"},
                {"id": "sqrt10", "text": "√10", "latex": r"\sqrt{10}"},
                {"id": "sqrt7", "text": "√7", "latex": r"\sqrt{7}"},
            ],
            "expected": "sqrt64",
            "feedback_by_option": {
                "sqrt64": "correct",
                "sqrt2": "fb_b07_e7_notsquare",
                "sqrt10": "fb_b07_e7_notsquare",
                "sqrt7": "fb_b07_e7_notsquare",
            },
            "misconception_by_option": {
                "sqrt2": "toda_raiz_es_irracional",
                "sqrt10": "toda_raiz_es_irracional",
                "sqrt7": "toda_raiz_es_irracional",
            },
            "hints": {
                "n1": "¿Cuál de los cuatro números es el cuadrado de un entero?",
                "n2": "8 × 8 = 64.",
                "n3": "√64 = 8, que es 8/1: racional. Las otras tres no cierran.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "La escalera de la necesidad",
        "title": "¿Alcanza el conjunto para nombrar toda longitud que se puede dibujar?",
        "intro": "Cada peldaño nació de algo que no cabía. Este nació de una raya sobre una baldosa.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"\tfrac{1}{2}\notin\mathbb{N}",
                "note": "Ni siquiera media baldosa cabe.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"\tfrac{1}{2}\notin\mathbb{Z}",
                "note": "Ganó los negativos, no las partes.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Q}",
                "note": "Aquí se cayó la escuela: la diagonal no tiene fracción.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\tfrac{1}{2}\notin\mathbb{I}",
                "note": "Solos tampoco alcanzan: se les fueron todas las fracciones.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\mathbb{R}=\mathbb{Q}\cup\mathbb{I}",
                "note": "Solo la UNIÓN de los dos llena la recta. Ese es B08.",
            },
        ],
        "outro": (
            "Fíjate en la fila de 𝕀: los irracionales por su cuenta no sirven como sistema "
            "de números — no tienen ni el 0, ni el 1, ni las fracciones. Su papel es "
            "completar. Por eso el siguiente peldaño no es «otro conjunto más», es la "
            "unión de dos."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué tienen en común los números irracionales que viste en este nodo?",
        "thumbnails": [r"\sqrt{2}", r"\pi", r"1{,}101101110\ldots"],
        "options": [
            {
                "id": "no_fraction",
                "text": "Ninguno se puede escribir como fracción de enteros",
                "correct": True,
            },
            {
                "id": "no_pattern",
                "text": "Su decimal es infinito y sin bloque que se repita",
                "correct": True,
            },
            {"id": "roots", "text": "Todos son raíces cuadradas", "correct": False},
            {"id": "big", "text": "Todos son números muy grandes", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El alfarero tiene seis medidas anotadas: √16 · 0,4 · √5 · 22/7 · π · "
            "3,0300300030… ¿Cuántas de las seis son racionales?"
        ),
        "polya": {
            "comprender": (
                "Me dan seis números mezclados. Me piden cuántos son racionales, o sea "
                "cuántos se pueden escribir como fracción de enteros."
            ),
            "planear": (
                "Voy uno por uno con el criterio correcto: ¿es fracción, o su decimal "
                "termina o se repite? Cuidado con las trampas: una raíz puede ser racional "
                "y una fracción de aspecto raro también."
            ),
            "ejecutar": (
                "√16 = 4 ✓ racional · 0,4 = 4/10 ✓ · √5 ✗ (5 no es cuadrado) · "
                "22/7 ✓ (es fracción, aunque se parezca a π) · π ✗ · "
                "3,0300300030… ✗ (crece el bloque, no se repite). Van 3."
            ),
            "comprobar": (
                "Reviso las dos trampas: 22/7 es racional aunque aproxime a π, y √16 es "
                "racional aunque sea raíz. 3 racionales y 3 irracionales. ✓"
            ),
        },
        "prompt": "¿Cuántas de las seis son racionales?",
        "answer": "3",
        "hints": {
            "n1": "Empieza resolviendo las raíces: ¿cuál da entero?",
            "n2": "√16 = 4 es racional; √5 no.",
            "n3": "Ojo con 22/7: es una fracción, así que es racional aunque se parezca a π.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico ----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: hoy resolviste más que al entrar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia "
            "entre un decimal que se repite y uno que no."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"$\dfrac{2}{9}=0{,}222\ldots$ ¿Racional o irracional?",
                "options": [
                    {"id": "rational", "text": "Racional"},
                    {"id": "irrational", "text": "Irracional"},
                ],
                "expected": "rational",
                "misconception_by_option": {"irrational": "decimal_infinito_es_irracional"},
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿$\sqrt{81}$ es racional o irracional?",
                "options": [
                    {"id": "rational", "text": "Racional: da 9"},
                    {"id": "irrational", "text": "Irracional: es una raíz"},
                ],
                # Inversa de la trampa: aquí la raíz SÍ es racional. Comprueba que
                # aprendió el criterio y no la heurística "raíz ⇒ irracional".
                "expected": "rational",
                "misconception_by_option": {"irrational": "toda_raiz_es_irracional"},
            },
            {
                "id": "PD3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "De esta lista, ¿cuántos son irracionales? √2 · 1/4 · π · 0,5",
                "answer": "2",
            },
        ],
    },
    # --- Bloque 11 · Footer + feedback ---------------------------------------
    "footer": {
        "label": "Estado de dominio",
        "states": {
            "sin_ayuda": "Dominado sin ayuda",
            "consolidacion": "En consolidación",
            "repasar": "Para repasar",
        },
        "note": "Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.",
    },
    "feedback": {
        "correct": "Correcto. Sigue.",
        "default": "Revisa el procedimiento paso a paso y vuelve a intentarlo.",
        "fb_b07_e3_periodic": (
            "0,8181… no termina, pero SÍ repite el bloque 81: eso lo delata como fracción "
            "(es 9/11). → Busca el que no repite ningún bloque."
        ),
        "fb_b07_e3_root": (
            "√36 = 6, y 6 es 6/1: racional. No toda raíz es irracional. → Busca la raíz "
            "cuyo radicando NO sea cuadrado de un entero."
        ),
        "fb_b07_e3_negative": (
            "El signo no saca a un número de ℚ: −7/4 ya viene escrito como fracción de "
            "enteros. → Busca el que no se puede escribir así."
        ),
        "fb_b07_e4_inverted": (
            "El orden estaba bien: contorno ÷ diámetro sí da π. El error está en creer "
            "que su medición da el valor exacto. → Di por qué 3,1428 no puede ser π."
        ),
        "fb_b07_e4_definition": (
            "Sí da π: esa es justamente la definición. El error está en el resultado que "
            "anotó, no en el procedimiento. → Mira qué tan exacto puede ser medir con una cuerda."
        ),
        "fb_b07_e4_none": (
            "Compruébalo: si π fuera 3,1428, sería 31428/10000, una fracción. Y se puede "
            "demostrar que π no es fracción. → Di qué tiene de malo esa igualdad."
        ),
        "fb_b07_e5_trap": (
            "Contraejemplo: 0,333… no termina y es 1/3. La definición de irracional es «no "
            "es fracción», no «no termina». → Escribe el criterio con la palabra REPITE."
        ),
        "fb_b07_e5_finite": (
            "No todos terminan: 1/3 = 0,333… sigue para siempre, y π también. → Divide "
            "1 ÷ 3 y mira si se detiene."
        ),
        "fb_b07_e5_depends": (
            "El número no cambia según cómo lo escribas: 0,5 y 1/2 son el mismo. La "
            "escritura es el retrato, no el número. → Decide con el criterio del patrón."
        ),
        "fb_b07_e6_measure": (
            "1,41 × 1,41 = 1,9881, no 2. Es el mismo error del decimal cortado de B06. → "
            "Busca la opción que consigue la longitud EXACTA sin medirla."
        ),
        "fb_b07_e6_impossible": (
            "Sí existe: es la diagonal de una baldosa de lado 1, y se puede dibujar. Lo "
            "que no existe es su fracción. → Distingue «no se puede escribir» de «no existe»."
        ),
        "fb_b07_e6_fraction": (
            "Esa fracción no existe, y no por falta de búsqueda: se demuestra que no puede "
            "existir (ejemplo 2). → Busca la opción que no necesita fracción."
        ),
        "fb_b07_e7_notsquare": (
            "Ese radicando no es cuadrado de ningún entero, así que la raíz no cierra en "
            "ninguna fracción. → Busca el número que sí es cuadrado perfecto."
        ),
    },
    "closing": (
        "Irracional no es «raro»: es «sin fracción». Los racionales y los irracionales "
        "juntos, y solo juntos, llenan la recta sin dejar un hueco. Eso es lo que armas "
        "en el siguiente nodo."
    ),
    "validation_status": "F1_B07_11bloques",
}
