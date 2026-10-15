"""P04 · La bandeja de parejas — el término del medio es una suma, no un producto.

Cuarta y última sala de La sala de los troqueles (Casa de la Sabiduría, Bagdad).
Guía: Rayhana. Vocabulario propio: bandeja, casilla, pareja, ficha, juego,
registro. Nada de matrices ni orlas (P01), cuños ni grecas (P02), moldes ni
capas (P03).

Error focal: desarrollar (x + a)(x + b) como x² + ab, perdiendo el término
(a + b)x. Es el mismo hueco de P01 y P02, pero aquí los dos cruzados no son ni
iguales ni opuestos: se suman sin cancelarse.

Cierra el nivel: el cuadrado de binomio y los conjugados salen de aquí como
casos particulares (a = b y a = −b).

Ítems de práctica derivados de Hipertexto U4 p79 (A1a, A1b, A1c, A1e, A1g).
"""

NODE_ID = "ALG-N2-P04-TERMINO-COMUN"
CONCEPT_SLUG = "producto_con_termino_comun"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "producto_con_termino_comun",
    "misconception": "termino_comun_falta_suma",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La bandeja de parejas · Producto con término común",
    "house": "La bandeja de parejas",
    "guide": "Rayhana",
    "finish_label": "Cerrar la sala de los troqueles",
    "title": "Uno suma y el otro multiplica, y no son el mismo número",
    "intro": (
        "Los tres troqueles anteriores pedían que los paréntesis fueran iguales o espejo. "
        "Aquí solo comparten el primer término, y los dos cruzados ya no se cancelan ni se "
        "duplican: se suman. Ese es el troquel más general de la sala — y los otros tres "
        "van a salir de él."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir la bandeja. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 2 + 3?",
                "answer": "5",
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 2 × 3?",
                "answer": "6",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $(x+2)(x+3)$, ¿qué término comparten los dos paréntesis?",
                "options": [
                    {"id": "x", "text": r"$x$", "latex": "x"},
                    {"id": "num", "text": "Los números"},
                    {"id": "none", "text": "Ninguno"},
                ],
                "expected": "x",
                "misconception_by_option": {
                    "num": "confunde_termino_comun_con_los_no_comunes",
                    "none": "no_reconoce_el_termino_comun",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/06-alg-n2-troqueles/p04-termino-comun-katia.png",
        "eyebrow": "KatIA · En la bandeja de parejas",
        "title": "La bandeja que se llenó de más",
        "body": (
            "Sobre la última mesa hay bandejas de casillas. Cada bandeja se llena con dos "
            "fichas por casilla, y las fichas vienen en juegos que comparten una medida.\n\n"
            "Rayhana saca un registro del cajón:\n\n"
            "«Un juego medía 12 por 13. Doce es diez y dos; trece es diez y tres. El "
            "aprendiz vio los dieces y los números sueltos y anotó: cien más seis, ciento "
            "seis.»\n\n"
            "«La bandeja se llevó ciento cincuenta y seis. Le faltaron cincuenta fichas, y "
            "no eran ni un cuadrado ni una esquina: eran cinco filas de diez.»"
        ),
        "question": (
            "En 12 × 13 aparecen un 100 y un 6. ¿De dónde salen las 50 fichas que faltan?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "suma", "text": "De sumar 2 y 3, y multiplicar el resultado por 10"},
                {"id": "prod", "text": "De multiplicar 2 por 3 otra vez"},
                {"id": "nada", "text": "De ningún sitio: 100 + 6 debería bastar"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decir cuál de los dos números "
                "manda en el término del medio y cuál en el último, y por qué no son el mismo."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos cruzados que no se anulan ni se duplican",
        "body": (
            "Igual que siempre salen cuatro productos. Lo que cambia de troquel a troquel es "
            "qué pasa con los dos del medio."
        ),
        "cases": [
            {
                "label": "Los cuatro productos",
                "context": r"$(x+a)(x+b)$ — término a término",
                "fraction": r"x\cdot x\;+\;x\cdot b\;+\;a\cdot x\;+\;a\cdot b",
                "division": r"x^{2}+bx+ax+ab",
                "note": (
                    "Los dos del medio son bx y ax: ambos llevan x, así que son semejantes y "
                    "se juntan."
                ),
            },
            {
                "label": "Al juntar semejantes",
                "context": r"$bx+ax=(a+b)x$",
                "fraction": r"x^{2}+(a+b)x+ab",
                "division": r"\text{suma en el medio, producto al final}",
                "note": (
                    "El del medio lleva la SUMA de los no comunes; el último lleva su "
                    "PRODUCTO. Casi nunca son el mismo número."
                ),
            },
        ],
        "resolution": (
            "Con 12 × 13, o sea (10 + 2)(10 + 3): el cuadrado del común es 100, la suma de "
            "los no comunes por el común es (2 + 3)·10 = 50, y el producto de los no comunes "
            "es 6. Total 156. Las 50 que faltaban eran justo el término del medio."
        ),
    },
    "definition_title": "Producto de binomios con término común",
    "definition_katex": r"(x+a)(x+b) = x^{2} + (a+b)\,x + ab",
    "definition": (
        "Cuando dos binomios comparten el primer término, el resultado tiene tres términos: "
        "el cuadrado del común, la SUMA de los no comunes multiplicada por el común, y el "
        "PRODUCTO de los no comunes. Los signos entran en la suma y en el producto: si un no "
        "común es negativo, resta en el medio y cambia el signo del último."
    ),
    "definition_symbols": [
        {
            "symbol": r"x^{2}",
            "reads": "equis al cuadrado",
            "means": "el cuadrado del término común",
        },
        {
            "symbol": r"(a+b)x",
            "reads": "a más b, por equis",
            "means": "la SUMA de los no comunes — el término que se olvida",
        },
        {
            "symbol": r"ab",
            "reads": "a por b",
            "means": "el PRODUCTO de los no comunes, sin ninguna equis",
        },
        {
            "symbol": r"(x+3)(x+3)",
            "reads": "equis más tres, por equis más tres",
            "means": "caso particular con a = b: sale el cuadrado de binomio",
        },
        {
            "symbol": r"(x+3)(x-3)",
            "reads": "equis más tres, por equis menos tres",
            "means": "caso particular con b = −a: la suma da 0 y sale la diferencia de cuadrados",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Dos juegos, los dos sumando",
            "title": "Suma en el medio, producto al final",
            "statement": (
                "Rayhana registra una bandeja de $(x+1)$ por $(x+2)$. ¿Cuántas fichas lleva?"
            ),
            "latex": r"(x+1)(x+2)",
            "image_slot": False,
            "steps": [
                "Cuadrado del común: x · x = x².",
                "Suma de los no comunes: 1 + 2 = 3, y va multiplicando a la x → 3x.",
                "Producto de los no comunes: 1 · 2 = 2.",
                "Queda x² + 3x + 2.",
                "Compruebo con x = 10: la bandeja es 11 × 12 = 132, y 100 + 30 + 2 = 132 ✓.",
            ],
            "solution": r"$(x+1)(x+2)=x^{2}+3x+2$",
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "¿Por qué el 3 del medio es una suma y el 2 del final un producto, si "
                    "los dos salen de los mismos números?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando uno de los dos resta",
            "title": "Los signos entran en las dos cuentas",
            "statement": (
                "Otro registro: $(a+5)(a-3)$. El segundo no común es negativo, y eso toca "
                "los dos términos."
            ),
            "latex": r"(a+5)(a-3)",
            "image_slot": False,
            "steps": [
                "Cuadrado del común: a².",
                "Suma de los no comunes: 5 + (−3) = 2, así que el medio es +2a.",
                "Producto de los no comunes: 5 · (−3) = −15.",
                "Queda a² + 2a − 15.",
                "Fíjate: el medio sale positivo y el último negativo. Cada uno lleva su propia cuenta.",
            ],
            "solution": r"$(a+5)(a-3)=a^{2}+2a-15$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que se saltó la fila de en medio",
            "statement": (
                "Vuelve el registro de la apertura, ahora con letras. El aprendiz anota la "
                "bandeja $(x+3)(x+4)$ así:"
            ),
            "latex": r"(x+3)(x+4)",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"(x+3)(x+4)=x^{2}+12",
            "error_note": (
                "Multiplicó los extremos y los no comunes, y se saltó los dos cruzados. "
                "Otra vez el término del medio."
            ),
            "correct_version": {
                "wrong_latex": r"(x+3)(x+4)=x^{2}+12",
                "right_latex": r"(x+3)(x+4)=x^{2}+7x+12",
                "rows": [
                    {
                        "wrong": "Dos términos: el cuadrado y el producto",
                        "right": "Tres: el cuadrado, la suma por el común, y el producto",
                    },
                    {
                        "wrong": "El 12 es lo único que aportan el 3 y el 4",
                        "right": "También aportan su suma, 7, que multiplica a la x",
                    },
                ],
            },
            "explain_prompt": (
                "Comprueba con x = 10 cuántas fichas faltan en la anotación del aprendiz, y "
                "di de dónde salen."
            ),
            "steps": [
                "Con x = 10 la bandeja es 13 × 14 = 182.",
                "La anotación del aprendiz da 100 + 12 = 112. Faltan 70.",
                "Esos 70 son 7x con x = 10: la suma de los no comunes por el común.",
                "Regla para no volver a caer: si el resultado no tiene un término con x sola, falta el del medio.",
            ],
            "solution": (
                "(x + 3)(x + 4) = x² + 7x + 12. El 7 suma y el 12 multiplica: son dos cuentas "
                "distintas."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El registro va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Multiplica $(x+7)(x-8)$.",
                "given_steps": [r"x^{2}", r"7\cdot(-8)=-56"],
                "blanks": [{"id": "P1-b1", "label": r"7+(-8)=", "answer": "-1"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Multiplica $(x^{2}-5)(x^{2}+9)$.",
                "given_steps": [r"(x^{2})^{2}=x^{4}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"-5+9=", "answer": "4"},
                    {"id": "P2-b2", "label": r"(-5)\cdot 9=", "answer": "-45"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $(a^{3}+3)(a^{3}-8)$. El común no es una letra "
                    "suelta — identifica primero cuál es."
                ),
                "given_steps": [],
                "blanks": [
                    {
                        "id": "P3-b1",
                        "label": r"\text{exponente de }a\text{ en el primer término}=",
                        "answer": "6",
                    }
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de llenar la bandeja",
        "intro": r"$(x+2)(x+5)$. Una es más rápida; la otra enseña por qué el medio se suma.",
        "methods": [
            {
                "label": "Método 1 · El troquel",
                "steps": [
                    r"(x+2)(x+5)",
                    r"x^{2}+(2+5)x+2\cdot 5",
                    r"x^{2}+7x+10",
                ],
                "note": "Dos cuentas cortas: una suma y un producto.",
            },
            {
                "label": "Método 2 · Los cuatro productos",
                "steps": [
                    r"x\cdot x+x\cdot 5+2\cdot x+2\cdot 5",
                    r"x^{2}+5x+2x+10",
                    r"x^{2}+7x+10",
                ],
                "note": "Más largo, pero se ve que el 7 nace de juntar 5x con 2x.",
            },
        ],
        "question": "¿Cuál de los dos deja claro por qué el medio se suma y el final se multiplica?",
        "insight": (
            "El segundo. Con el troquel uno acaba recitando «suma en el medio, producto al "
            "final» sin saber por qué. Escribiendo los cuatro productos se ve que los dos "
            "cruzados llevan x y por eso son semejantes: se juntan sumando coeficientes. El "
            "último no lleva x y no se junta con nadie. La suma y el producto no salen de una "
            "regla: salen de qué términos son semejantes y cuáles no."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿A qué equivale $(x+a)(x+b)$?",
            "options": [
                {"id": "full", "text": r"$x^{2}+(a+b)x+ab$", "latex": r"x^{2}+(a+b)x+ab"},
                {"id": "noMid", "text": r"$x^{2}+ab$", "latex": r"x^{2}+ab"},
                {"id": "swap", "text": r"$x^{2}+ab\,x+(a+b)$", "latex": r"x^{2}+ab\,x+(a+b)"},
                {"id": "sq", "text": r"$x^{2}+2abx+ab$", "latex": r"x^{2}+2abx+ab"},
            ],
            "expected": "full",
            "feedback_by_option": {
                "full": "correct",
                "noMid": "fb_p04_e1_nomid",
                "swap": "fb_p04_e1_swap",
                "sq": "fb_p04_e1_sq",
            },
            "misconception_by_option": {
                "noMid": "termino_comun_falta_suma",
                "swap": "intercambia_suma_y_producto",
                "sq": "usa_el_doble_producto_del_cuadrado",
            },
            "hints": {
                "n1": "Escribe los cuatro productos y mira los dos del medio.",
                "n2": "Los dos del medio llevan x: son semejantes y se juntan.",
                "n3": "Prueba con x = 10, a = 2, b = 3: la bandeja es 12 × 13 = 156.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Multiplica $(x+1)(x+2)$. Usa $\wedge$ para el exponente, así: x^2+3x+2. "
                "No dejes espacios."
            ),
            "answer": "x^2+3x+2",
            "hints": {
                "n1": "El primer término es x².",
                "n2": "El del medio lleva la suma: 1 + 2.",
                "n3": "El último lleva el producto: 1 · 2.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En $(a+5)(a-3)$, ¿cuál es el coeficiente del término del medio? Escríbelo "
                "con su signo."
            ),
            "expr": r"5+(-3)=2",
            "answer": "2",
            "hints": {
                "n1": "El del medio lleva la suma de los no comunes.",
                "n2": "Los no comunes son 5 y −3.",
                "n3": "5 − 3.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (r"En $(x+7)(x-8)$, ¿cuál es el término sin $x$? Escríbelo con su signo."),
            "expr": r"7\cdot(-8)=-56",
            "answer": "-56",
            "hints": {
                "n1": "El último lleva el producto de los no comunes.",
                "n2": "7 · (−8).",
                "n3": "Un positivo por un negativo da negativo.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (r"Un aprendiz anota $(x-11)(x+10)=x^{2}+21x-110$. ¿Dónde está el error?"),
            "options": [
                {"id": "mid", "text": r"El del medio: $-11+10=-1$, así que es $-x$"},
                {"id": "last", "text": r"El último: debería ser $+110$"},
                {"id": "first", "text": r"El primero: debería ser $2x^{2}$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "mid",
            "feedback_by_option": {
                "mid": "correct",
                "last": "fb_p04_e5_last",
                "first": "fb_p04_e5_first",
                "none": "fb_p04_e5_none",
            },
            "misconception_by_option": {
                "last": "ignora_los_signos_en_el_producto",
                "first": "suma_los_terminos_comunes",
                "none": "intercambia_suma_y_producto",
            },
            "hints": {
                "n1": "El último está bien: (−11) · 10 = −110.",
                "n2": "Mira el del medio: ¿es la suma o el producto?",
                "n3": "−11 + 10 = −1, no 21. Sumó los valores sin mirar el signo.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Como los dos números aparecen multiplicados en el "
                "último término, no hace falta escribirlos otra vez en el medio.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: en el medio va su suma, que es otra cuenta distinta",
                },
                {"id": "true", "text": "Verdadera: ya están contados en el producto"},
                {
                    "id": "true_eq",
                    "text": "Verdadera cuando los dos números son iguales",
                },
                {
                    "id": "false_prod",
                    "text": "Falsa: en el medio va su producto otra vez",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_p04_e6_trap",
                "true_eq": "fb_p04_e6_eq",
                "false_prod": "fb_p04_e6_prod",
            },
            "misconception_by_option": {
                "true": "termino_comun_falta_suma",
                "true_eq": "termino_comun_falta_suma",
                "false_prod": "intercambia_suma_y_producto",
            },
            "hints": {
                "n1": "Prueba con 12 × 13, o sea (10 + 2)(10 + 3).",
                "n2": "156, no 106.",
                "n3": "Las 50 que faltan son (2 + 3) · 10: la suma, no el producto.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Rayhana ordena la sala. ¿Cuáles de estos productos se pueden resolver con el "
                "troquel de la bandeja? Marca todas las que apliquen."
            ),
            "options": [
                {"id": "plain", "text": r"$(x+2)(x+9)$"},
                {"id": "sq", "text": r"$(x+4)(x+4)$"},
                {"id": "conj", "text": r"$(x+4)(x-4)$"},
                {"id": "nocommon", "text": r"$(2x+1)(x+5)$"},
            ],
            "expected": ["plain", "sq", "conj"],
            "valid_options": ["plain", "sq", "conj", "nocommon"],
            "trap_options": ["nocommon"],
            "feedback_by_option": {
                "plain": "correct",
                "sq": "correct",
                "conj": "correct",
            },
            "misconception_by_option": {
                "nocommon": "cree_que_2x_y_x_son_el_mismo_termino_comun",
            },
            "hints": {
                "n1": "Hace falta que el primer término sea EL MISMO en los dos paréntesis.",
                "n2": "El cuadrado de binomio y los conjugados son casos particulares de este troquel.",
                "n3": "2x y x no son el mismo término común. Son tres de las cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Qué manda en el término del medio?",
        "title": "Los cuatro troqueles eran uno",
        "intro": (
            "Este es el troquel general de la sala. Los otros tres se obtienen eligiendo qué "
            "son los dos no comunes."
        ),
        "rows": [
            {
                "name": "Dos no comunes distintos",
                "symbol": r"(x+2)(x+3)",
                "latex": r"x^{2}+5x+6",
                "closed": "yes",
                "note": "Medio = 2 + 3 = 5. Último = 2 · 3 = 6. Suma y producto, distintos.",
            },
            {
                "name": "Uno de los dos resta",
                "symbol": r"(x+5)(x-2)",
                "latex": r"x^{2}+3x-10",
                "closed": "yes",
                "note": "Los signos entran en las dos cuentas: 5 − 2 = 3 y 5·(−2) = −10.",
            },
            {
                "name": "Los dos restan",
                "symbol": r"(x-2)(x-3)",
                "latex": r"x^{2}-5x+6",
                "closed": "yes",
                "note": "Medio negativo, último positivo. Dos negativos multiplicados suman.",
            },
            {
                "name": "Los dos iguales",
                "symbol": r"(x+3)(x+3)",
                "latex": r"x^{2}+6x+9",
                "closed": "partial",
                "note": (
                    "Aquí la suma vale 2·3 y el troquel se convierte en la matriz cuadrada. "
                    "No es un troquel aparte: es este con a = b."
                ),
            },
            {
                "name": "Los dos opuestos",
                "symbol": r"(x+3)(x-3)",
                "latex": r"x^{2}-9",
                "closed": "partial",
                "note": (
                    "La suma vale 0, así que el medio desaparece y queda el cuño de la "
                    "cenefa. Tampoco era un troquel aparte."
                ),
            },
            {
                "name": "Sin término común",
                "symbol": r"(2x+1)(x+5)",
                "latex": r"2x^{2}+11x+5",
                "closed": "no",
                "note": (
                    "2x y x no son el mismo término: el troquel no aplica y toca multiplicar "
                    "los cuatro productos a mano."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **el medio lleva la suma de los no comunes; el último, "
            "su producto.** Y los tres troqueles anteriores de la sala son casos particulares "
            "de este: cuando los no comunes son iguales sale el cuadrado, y cuando son "
            "opuestos sale la diferencia de cuadrados."
        ),
    },
    "abstraction_question": {
        "prompt": (
            "Mira los tres productos. ¿Qué determina el signo del término del medio y el del "
            "último?"
        ),
        "thumbnails": [
            r"(x+2)(x+3)=x^{2}+5x+6",
            r"(x+2)(x-3)=x^{2}-x-6",
            r"(x-2)(x-3)=x^{2}-5x+6",
        ],
        "options": [
            {
                "id": "sumprod",
                "text": (
                    "El medio lo decide la suma de los dos números con su signo, y el último "
                    "su producto"
                ),
                "correct": True,
            },
            {
                "id": "count",
                "text": "Los decide cuántos signos menos hay en los paréntesis",
                "correct": False,
            },
            {
                "id": "first",
                "text": "Los decide el signo del primer paréntesis",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Rayhana registra una bandeja de $(x+6)$ por $(x-2)$. Con $x=4$, ¿cuántas fichas "
            "lleva?"
        ),
        "polya": {
            "comprender": "Comparten la x; los no comunes son +6 y −2.",
            "planear": "O multiplico directo, o uso el troquel y sustituyo.",
            "ejecutar": "4 + 6 = 10 y 4 − 2 = 2, así que 10 · 2 = 20.",
            "comprobar": "Por el troquel, x² + 4x − 12 con x = 4 da 16 + 16 − 12 = 20 ✓.",
        },
        "prompt": "¿Cuántas fichas lleva la bandeja?",
        "answer": "20",
        "hints": {
            "n1": "Calcula cuánto vale cada paréntesis con x = 4.",
            "n2": "Salen 10 y 2.",
            "n3": "10 · 2.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que conoces el troquel general.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya separas la suma del producto sin dudar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el término del medio "
            "antes de cerrar la sala."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuánto es 4 + 7?",
                "answer": "11",
            },
            {
                "id": "Q2",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuánto es 4 × 7?",
                "answer": "28",
            },
            {
                "id": "Q3",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿A qué equivale $(x+4)(x+7)$?",
                "options": [
                    {"id": "full", "text": r"$x^{2}+11x+28$", "latex": r"x^{2}+11x+28"},
                    {"id": "noMid", "text": r"$x^{2}+28$", "latex": r"x^{2}+28"},
                    {"id": "swap", "text": r"$x^{2}+28x+11$", "latex": r"x^{2}+28x+11"},
                ],
                "expected": "full",
                "misconception_by_option": {
                    "noMid": "termino_comun_falta_suma",
                    "swap": "intercambia_suma_y_producto",
                },
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de salir de la sala de los troqueles.",
            "consolidacion": "Resuelto con ayuda: el troquel ya está, falta que salga solo.",
            "sin_ayuda": "Bandeja completa. La suma y el producto ya no se te mezclan.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Suma en el medio, producto al final.",
        "default": (
            "Separa las dos cuentas: el término del medio lleva la SUMA de los no comunes, "
            "el último su PRODUCTO."
        ),
        "fb_p04_e1_nomid": (
            "Ese es el error del nodo. Con x = 10, a = 2 y b = 3 tu respuesta da 106 y la "
            "bandeja lleva 156: faltan las 50 del término del medio."
        ),
        "fb_p04_e1_swap": (
            "Están cambiados de sitio. El que multiplica a la x es la suma; el que va solo al "
            "final es el producto."
        ),
        "fb_p04_e1_sq": (
            "Ese 2 es del cuadrado de binomio, donde los dos no comunes son iguales. Aquí son "
            "distintos, así que en el medio va su suma, no su doble producto."
        ),
        "fb_p04_e5_last": ("El último está bien: (−11) · 10 = −110. Mira el del medio."),
        "fb_p04_e5_first": (
            "El primero está bien: x · x = x². Los términos comunes se multiplican, no se suman."
        ),
        "fb_p04_e5_none": (
            "Sí lo hay: el del medio debería ser −1, la suma de −11 y 10. Se escribió 21, que "
            "es la suma de los valores sin mirar el signo."
        ),
        "fb_p04_e6_trap": (
            "El producto y la suma son cuentas distintas. Con 12 × 13 el producto de los no "
            "comunes aporta 6 y la suma aporta 50."
        ),
        "fb_p04_e6_eq": (
            "Aunque sean iguales la suma sigue haciendo falta: en (x + 3)(x + 3) el medio es "
            "6x, que es justo la orla de la matriz cuadrada."
        ),
        "fb_p04_e6_prod": (
            "La respuesta es falsa, pero no por eso: en el medio va la SUMA de los no comunes, "
            "no su producto otra vez."
        ),
    },
    "closing": (
        "Con esto la sala de los troqueles queda cerrada. Tienes cuatro estampas, y acabas de "
        "ver que en realidad son una sola con distintos ajustes: cuando los dos no comunes "
        "son iguales sale el cuadrado, cuando son opuestos sale la diferencia de cuadrados, y "
        "cuando el molde sube un piso salen cuatro capas. En el almacén de la caravana te "
        "espera el trabajo contrario: llegan fardos ya estampados y hay que averiguar con qué "
        "troquel se hicieron."
    ),
    "validation_status": "F5_P04_11bloques",
}
