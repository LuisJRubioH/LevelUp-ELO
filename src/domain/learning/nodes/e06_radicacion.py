"""E06 · Radicación — la raíz no se reparte sobre una suma.

Edificio del nodo: LA CANTERA (losas cuadradas, el área encargada, el cincel y
la plomada). Ningún otro edificio de N2 usa este oficio.
"""

NODE_ID = "PREALG-N2-E06-RADICACION-RAIZ"
CONCEPT_SLUG = "radicacion"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "radicacion",
    "misconception": "raiz_de_suma_es_suma_de_raices",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La Cantera · Radicación",
    "building": "La Cantera",
    "finish_label": "Salir de la ciudad de las operaciones",
    "title": "La raíz no se reparte sobre una suma",
    "intro": (
        "Último edificio. Aquí no te dan el lado y te piden la superficie: te dan la "
        "superficie y tienes que deducir el lado. Vas a ver qué operación deshace a la "
        "potencia, y por qué el error más caro de la cantera es partir una raíz en dos."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de bajar a la cantera. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Una losa cuadrada tiene 49 palmos² de superficie. ¿Cuánto mide su lado?",
                "answer": "7",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $\sqrt{9+16}$?",
                "options": [
                    {"id": "five", "text": "5", "latex": r"5"},
                    {"id": "seven", "text": "7", "latex": r"3+4"},
                    {"id": "twentyfive", "text": "25", "latex": r"25"},
                ],
                "expected": "five",
                "misconception_by_option": {
                    "seven": "raiz_de_suma_es_suma_de_raices",
                    "twentyfive": "olvida_aplicar_la_raiz",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Qué tipo de número es $\sqrt{2}$?",
                "options": [
                    {"id": "irrational", "text": "Irracional: su decimal no termina ni se repite"},
                    {"id": "rational", "text": "Racional: es 1,41"},
                    {"id": "not_number", "text": "No es un número: no se puede calcular exacto"},
                ],
                "expected": "irrational",
                "misconception_by_option": {
                    "rational": "decimal_truncado_es_el_numero",
                    "not_number": "irracional_no_es_numero",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · Dentro de la Cantera",
        "title": "La losa que salió torcida",
        "body": (
            "El sexto y último edificio no tiene techo: es la Cantera, un tajo de piedra "
            "con poleas, cinceles y una plomada colgando. Aquí los encargos llegan al "
            "revés que en el Taller de Mosaicos — no te dicen cuánto mide el lado, te "
            "dicen cuánta superficie quieren y tú tienes que deducir el lado.\n\n"
            "Llegó un encargo de dos losas cuadradas, una de 9 palmos² y otra de 16, para "
            "fundirlas en una sola losa cuadrada. El cantero calculó el lado de la losa "
            "nueva sumando los lados de las dos: 3 y 4, siete palmos. Cortó la piedra. "
            "No encajó."
        ),
        "question": "Si juntas una superficie de 9 y una de 16, ¿cuánto mide el lado del cuadrado que forman?",
        "image": "/leccion/02-prealg-n2-mercado/e06-radicacion-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "7 palmos: 3 más 4"},
                {"id": "b", "text": "5 palmos"},
                {"id": "c", "text": "25 palmos"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir cuánto midió la "
                "losa y cuánta piedra se perdió."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos encargos de la cantera",
        "body": (
            "Los dos encargos de abajo piden un lado a partir de una superficie. Fíjate "
            "en cómo termina cada cuenta."
        ),
        "cases": [
            {
                "label": "Caso que funciona",
                "context": "Una losa cuadrada de 36 palmos² de superficie",
                "fraction": r"\sqrt{36}",
                "division": r"\sqrt{36}=6",
                "note": "El lado es exacto: 6 × 6 = 36. La cuenta cierra en los naturales.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Una losa cuadrada de 2 palmos² de superficie",
                "fraction": r"\sqrt{2}",
                "division": r"\sqrt{2}=1{,}41421\ldots",
                "note": "El lado existe y se puede trazar con la plomada, pero ninguna fracción lo escribe.",
            },
        ],
        "resolution": (
            "El segundo lado es tan real como el primero: es la diagonal de un cuadrado de "
            "lado 1, la puedes marcar con una cuerda. Lo que no existe es una fracción que "
            "lo mida exacto. Por eso la radicación fue la operación que obligó a inventar "
            "los irracionales (B07): la piedra cabía, el número no."
        ),
    },
    "definition_title": "La radicación",
    "definition_katex": r"\sqrt[n]{a}=b\iff b^{n}=a",
    "definition": (
        "La raíz deshace la potencia: buscar la raíz n-ésima de a es preguntar qué número "
        "elevado a n da a. En la cantera, la raíz cuadrada de la superficie es el lado."
    ),
    "definition_symbols": [
        {
            "symbol": r"a",
            "reads": "radicando",
            "means": "lo que está dentro; en la cantera, la superficie",
        },
        {
            "symbol": r"n",
            "reads": "índice",
            "means": "a qué potencia hay que elevar; si no se escribe, es 2",
        },
        {"symbol": r"b", "reads": "raíz", "means": "el resultado; en la cantera, el lado"},
        {
            "symbol": r"\sqrt{a}=a^{1/2}",
            "reads": "raíz como potencia",
            "means": "la raíz es la potencia de exponente 1/2 (viene de E05)",
        },
        {
            "symbol": r"\sqrt{a\times b}=\sqrt{a}\times\sqrt{b}",
            "reads": "sí se reparte sobre el producto",
            "means": "esta sí vale",
        },
        {
            "symbol": r"\sqrt{a+b}\neq\sqrt{a}+\sqrt{b}",
            "reads": "no se reparte sobre la suma",
            "means": "esta NO vale, y es el error de este nodo",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Naturales",
            "title": "La losa que sí encaja",
            "statement": (
                "Encargan una losa cuadrada que cubra 9 palmos² y otra que cubra 16. "
                "Al fundirlas, la losa nueva debe cubrir toda esa superficie. ¿Cuánto mide su lado?"
            ),
            "latex": r"\sqrt{9+16}",
            "image_slot": True,
            "image": "/leccion/02-prealg-n2-mercado/e06-cuadrado-perfecto-v4.png",
            "steps": [
                "Primero junto las superficies: 9 + 16 = 25 palmos². Eso es lo que debe cubrir la losa nueva.",
                "Ahora busco el lado del cuadrado de 25 palmos²: √25.",
                "¿Qué número por sí mismo da 25? 5 × 5 = 25.",
                "El lado es 5 palmos. Compruebo: 5 × 5 = 25, y 25 es lo que sumé.",
                "El cantero había cortado 7. Con 7 la losa habría cubierto 49 palmos²: casi el doble de piedra desperdiciada.",
            ],
            "solution": r"$\sqrt{9+16}=\sqrt{25}=5$",
            "self_explanation": {
                "step_index": 0,
                "prompt": "En el paso 1 se suma DENTRO de la raíz antes de sacarla. ¿Por qué no se puede sacar la raíz de cada número por separado?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Irracionales",
            "title": "El lado que no cabe en ninguna fracción",
            "statement": (
                "Encargan una losa cuadrada de exactamente 2 palmos² de superficie. "
                "¿Cuánto mide el lado y cómo se marca en la piedra?"
            ),
            "latex": r"\sqrt{2}",
            "image_slot": True,
            "image": "/leccion/02-prealg-n2-mercado/e06-raiz-no-entera-v4.png",
            "steps": [
                "Busco el número que por sí mismo da 2. No es 1 (da 1) ni 2 (da 4): está en medio.",
                "1,4 × 1,4 = 1,96. 1,41 × 1,41 = 1,9881. Me acerco pero nunca llego exacto.",
                "Ninguna fracción lo consigue: eso se demuestra en B07, y por eso √2 es irracional.",
                "En la piedra sí se marca: es la diagonal de un cuadrado de lado 1 palmo. Una cuerda y un cincel bastan.",
                "√2 = 1,41421… El lado existe; lo que no existe es su fracción exacta.",
            ],
            "solution": r"$\sqrt{2}=1{,}41421\ldots\in\mathbb{I}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El cantero que partió la raíz en dos",
            "statement": (
                "El cantero anota en la piedra: «Superficie total 9 + 16. El lado es √9 más "
                "√16, o sea 3 + 4 = 7 palmos». Corta la losa de 7 y no encaja."
            ),
            "latex": r"\sqrt{9+16}=\sqrt{9}+\sqrt{16}=7",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\sqrt{9+16}\;\underline{=}\;\sqrt{9}+\sqrt{16}",
            "error_note": "Ese signo igual es el error: la raíz se reparte sobre el PRODUCTO, nunca sobre la suma.",
            "correct_version": {
                "wrong_latex": r"\sqrt{9+16}=7",
                "right_latex": r"\sqrt{9+16}=\sqrt{25}=5",
                "rows": [
                    {
                        "wrong": "La raíz se reparte sobre cada sumando",
                        "right": "Primero se suma dentro, después se saca la raíz",
                    },
                    {
                        "wrong": "Dos cuadrados de lado 3 y 4 forman uno de lado 7",
                        "right": "Forman uno de lado 5: los lados no se suman, las superficies sí",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 7 no puede ser el lado? Escribe la cuenta corregida.",
            "steps": [
                "Comprueba al revés: una losa de lado 7 cubre 7 × 7 = 49 palmos².",
                "Pero solo se encargaron 9 + 16 = 25 palmos². Sobran 24: casi el doble de piedra.",
                "El lado correcto es √25 = 5. Con la multiplicación sí funcionaría: √(9×16) = 3 × 4 = 12.",
            ],
            "solution": (
                "La raíz se lleva bien con el producto y mal con la suma. Si dudas, comprueba "
                "elevando al cuadrado: (3+4)² = 49 y 9 + 16 = 25. Si no coinciden, la raíz no "
                "se podía repartir."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El procedimiento ya va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Una losa cuadrada debe cubrir 36 + 28 palmos².",
                "given_steps": [
                    r"36+28=64",
                    r"\text{ahora sí, la raíz de la suma}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\sqrt{64}=", "answer": "8"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Dos losas cuadradas de 4 y 25 palmos² se cortan de un mismo bloque rectangular.",
                "given_steps": [
                    r"\sqrt{4\times 25}=\sqrt{4}\times\sqrt{25}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\sqrt{4}=", "answer": "2"},
                    {"id": "P2-b2", "label": r"\sqrt{4\times 25}=", "answer": "10"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: una losa cúbica de 27 palmos³ de volumen. "
                    "¿Cuánto mide su arista?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\sqrt[3]{27}=", "answer": "3"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma raíz",
        "intro": r"¿Cuánto vale $\sqrt{144}$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Buscar el cuadrado",
                "steps": [r"10^{2}=100,\ 11^{2}=121", r"12^{2}=144", r"\sqrt{144}=12"],
                "note": "Tanteo dirigido: sirve cuando el número es un cuadrado conocido.",
            },
            {
                "label": "Método 2 · Descomponer el radicando",
                "steps": [
                    r"\sqrt{144}=\sqrt{16\times 9}",
                    r"=\sqrt{16}\times\sqrt{9}",
                    r"=4\times 3=12",
                ],
                "note": "Reparte la raíz sobre el producto, que sí está permitido.",
            },
        ],
        "question": "¿Cuál usarías con √3600? ¿Y qué pasa si intentas el método 2 escribiendo 144 como 100 + 44?",
        "insight": (
            "El método 2 funciona porque 144 = 16 × 9, un PRODUCTO. Si lo escribes como "
            "100 + 44 y repartes la raíz, obtienes 10 + 6,63… = 16,63, que no es 12. Ese "
            "fracaso es el contenido del nodo: la raíz se reparte sobre el producto y nunca "
            "sobre la suma. Descomponer en factores es lo que vas a hacer en N4-C04."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una losa cuadrada cubre 81 palmos². ¿Cuánto mide su lado?",
            "expr": r"\sqrt{81}",
            "answer": "9",
            "hints": {
                "n1": "Busca el número que multiplicado por sí mismo da 81.",
                "n2": "8 × 8 = 64, se queda corto.",
                "n3": "9 × 9 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una losa debe cubrir 40 + 60 palmos². ¿Cuánto mide su lado?",
            "expr": r"\sqrt{40+60}",
            "answer": "10",
            "hints": {
                "n1": "Primero suma lo de dentro; la raíz va después.",
                "n2": "40 + 60 = 100.",
                "n3": "10 × 10 = 100.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Un bloque cúbico tiene 64 palmos³ de volumen. ¿Cuánto mide su arista?",
            "expr": r"\sqrt[3]{64}",
            "answer": "4",
            "hints": {
                "n1": "El índice 3 pide el número que elevado al cubo da 64.",
                "n2": "3³ = 27, se queda corto.",
                "n3": "4 × 4 × 4 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"El cantero anota «$\sqrt{16+9}=4+3=7$». ¿Dónde está el error?",
            "options": [
                {
                    "id": "split_sum",
                    "text": "Repartió la raíz sobre una suma; primero se suma dentro y da 5",
                },
                {"id": "arith", "text": "Sumó mal: 4 + 3 son 8"},
                {"id": "product", "text": "Debía multiplicar las raíces: 4 × 3 = 12"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "split_sum",
            "feedback_by_option": {
                "split_sum": "correct",
                "arith": "fb_e06_e4_arith",
                "product": "fb_e06_e4_product",
                "none": "fb_e06_e4_none",
            },
            "misconception_by_option": {
                "arith": "habito_error_de_calculo_no_de_metodo",
                "product": "confunde_regla_del_producto_con_la_suma",
                "none": "raiz_de_suma_es_suma_de_raices",
            },
            "hints": {
                "n1": "Comprueba elevando al cuadrado: ¿7 × 7 da 16 + 9?",
                "n2": "7 × 7 = 49, pero 16 + 9 = 25.",
                "n3": "El lado correcto es √25.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para $a,b\ge 0$: $\sqrt{a+b}=\sqrt{a}+\sqrt{b}$.»",
            "options": [
                {"id": "false_sum", "text": "Falsa: vale sobre el producto, no sobre la suma"},
                {"id": "true", "text": "Verdadera: la raíz se reparte sobre cada término"},
                {"id": "false_never", "text": "Falsa: los dos lados nunca coinciden"},
                {"id": "true_squares", "text": "Verdadera si a y b son cuadrados perfectos"},
            ],
            "expected": "false_sum",
            "feedback_by_option": {
                "false_sum": "correct",
                "true": "fb_e06_e5_trap",
                "false_never": "fb_e06_e5_never",
                "true_squares": "fb_e06_e5_squares",
            },
            "misconception_by_option": {
                "true": "raiz_de_suma_es_suma_de_raices",
                "false_never": "olvida_el_caso_con_cero",
                "true_squares": "raiz_de_suma_es_suma_de_raices",
            },
            "hints": {
                "n1": "Para tumbar un «para todo» basta UN caso.",
                "n2": "Prueba con a = 9 y b = 16.",
                "n3": "√25 = 5, pero 3 + 4 = 7. ¿Y si uno de los dos fuera 0?",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Se funden dos losas cuadradas, una de 45 palmos² y otra de 76, en una sola "
                "losa cuadrada. ¿Cuánto mide su lado?"
            ),
            "expr": r"\sqrt{45+76}",
            "answer": "11",
            "hints": {
                "n1": "Las superficies sí se suman; los lados no.",
                "n2": "45 + 76 = 121.",
                "n3": "11 × 11 = 121.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál es el primer peldaño de la escalera donde √2 ya tiene respuesta?",
            "options": [
                {"id": "irrationals", "text": "Los irracionales", "latex": r"\mathbb{I}"},
                {"id": "naturals", "text": "Los naturales", "latex": r"\mathbb{N}"},
                {"id": "rationals", "text": "Los racionales", "latex": r"\mathbb{Q}"},
                {"id": "complex", "text": "Los complejos", "latex": r"\mathbb{C}"},
            ],
            "expected": "irrationals",
            "feedback_by_option": {
                "irrationals": "correct",
                "naturals": "fb_e06_e7_breaks",
                "rationals": "fb_e06_e7_breaks",
                "complex": "fb_e06_e7_bigger",
            },
            "misconception_by_option": {
                "naturals": "raiz_siempre_da_entero",
                "rationals": "decimal_truncado_es_el_numero",
                "complex": "no_busca_el_minimo",
            },
            "hints": {
                "n1": "¿Existe alguna fracción cuyo cuadrado sea exactamente 2?",
                "n2": "No: eso se demostró en B07.",
                "n3": "El conjunto de los números que no son fracción tiene nombre propio.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "La escalera de la radicación",
        "title": "¿La raíz de un elemento del conjunto vive en el conjunto?",
        "intro": "Esta es la operación que más lejos te lleva: rompe tres peldaños seguidos.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{N}",
                "note": "√4 = 2 sí es natural, pero basta un caso para romper el peldaño: √2 no lo es.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Z}",
                "note": "Los negativos no ayudan: √2 sigue sin ser entero.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Q}",
                "note": "Ninguna fracción tiene cuadrado 2 (B07). ESTE es el hueco del que nacieron los irracionales.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "partial",
                "latex": r"\sqrt{-\sqrt{2}}\notin\mathbb{R}",
                "note": "Aquí 𝕀 se porta mejor que de costumbre: la raíz de un irracional POSITIVO siempre es irracional. Se rompe solo con los negativos, y ahí sale de ℝ entera.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "partial",
                "latex": r"\sqrt{-4}\notin\mathbb{R}",
                "note": "Cierra para todo radicando positivo. Se rompe en un solo caso: raíz par de un número negativo.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"\sqrt{-4}=2i",
                "note": "El único peldaño donde toda raíz tiene respuesta. Por eso existe B09.",
            },
        ],
        "outro": (
            "Recorriste los seis edificios. Suma y multiplicación no rompieron nada; la resta "
            "trajo los enteros, la división trajo los racionales, la potencia y la raíz "
            "trajeron los irracionales y dejaron entreabierta la puerta de los complejos. "
            "La escalera de conjuntos no fue un capricho: la construyeron las operaciones."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"\sqrt{9+16}", r"\sqrt{2}", r"\sqrt{9}+\sqrt{16}"],
        "options": [
            {
                "id": "undo",
                "text": "En los tres se busca el número que elevado al cuadrado da el radicando",
                "correct": True,
            },
            {
                "id": "exact",
                "text": "En los tres el resultado es un número entero",
                "correct": False,
            },
            {
                "id": "side",
                "text": "En los tres se pasa de una superficie a un lado",
                "correct": True,
            },
            {
                "id": "split",
                "text": "En los tres la raíz se puede repartir sobre cada término",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Último encargo de la cantera: fundir dos losas cuadradas, una de 60 palmos² y "
            "otra de 109, en una sola losa cuadrada. ¿Cuánto mide su lado?"
        ),
        "polya": {
            "comprender": "Me dan dos superficies y me piden el lado de la losa que las cubre a las dos.",
            "planear": "Sumo las superficies DENTRO de la raíz y después saco la raíz. Nunca al revés.",
            "ejecutar": "60 + 109 = 169 → √169 = 13.",
            "comprobar": "13 × 13 = 169, que es lo que sumé. Y compruebo el error clásico: √60 + √109 ≈ 7,75 + 10,44 = 18,19, que no es 13.",
        },
        "prompt": "¿Cuánto mide el lado de la losa?",
        "answer": "13",
        "hints": {
            "n1": "Las superficies se suman; los lados no.",
            "n2": "60 + 109 = 169.",
            "n3": "12 × 12 = 144, se queda corto. Prueba el siguiente.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya sumas dentro de la raíz antes de sacarla.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué la raíz se "
            "reparte sobre el producto pero no sobre la suma."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Una losa cuadrada cubre 100 palmos². ¿Cuánto mide su lado?",
                "answer": "10",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $\sqrt{36+64}$?",
                "options": [
                    {"id": "ten", "text": "10", "latex": r"10"},
                    {"id": "fourteen", "text": "14", "latex": r"6+8"},
                    {"id": "hundred", "text": "100", "latex": r"100"},
                ],
                "expected": "ten",
                "misconception_by_option": {
                    "fourteen": "raiz_de_suma_es_suma_de_raices",
                    "hundred": "olvida_aplicar_la_raiz",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? $\sqrt{4\times 9}=\sqrt{4}\times\sqrt{9}$",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "sobregeneraliza_radicacion"},
                # Variante VERDADERA de E5, a propósito: comprueba que aprendió la
                # distinción suma/producto y no la heurística "la raíz nunca se reparte".
            },
        ],
    },
    # --- Bloque 11 · Footer + feedback ----------------------------------------
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
        "default": "Comprueba elevando al cuadrado: si no vuelves al radicando, algo falló.",
        "fb_e06_e4_arith": (
            "4 + 3 sí son 7; la suma no es el problema. → Fíjate en si esa suma se podía "
            "hacer antes de sacar la raíz."
        ),
        "fb_e06_e4_product": (
            "Esa regla es real, pero es para el producto: √(16×9) = 4 × 3. Aquí dentro hay "
            "una SUMA. → Suma primero y saca la raíz después."
        ),
        "fb_e06_e4_none": (
            "Comprueba elevando al cuadrado: 7 × 7 = 49, pero dentro había 25. → Calcula √25."
        ),
        "fb_e06_e5_trap": (
            "Eso es exactamente lo que le costó una losa al cantero. → Prueba con a = 9 y "
            "b = 16 y compara los dos lados."
        ),
        "fb_e06_e5_never": (
            "Casi: fallan casi siempre, pero hay un caso donde coinciden. → Prueba con b = 0."
        ),
        "fb_e06_e5_squares": (
            "9 y 16 son cuadrados perfectos y aun así falla. → Calcula √(9+16) y √9 + √16."
        ),
        "fb_e06_e7_breaks": (
            "Ahí √2 no tiene respuesta: no hay ningún número de ese conjunto cuyo cuadrado "
            "sea 2. → Sube un peldaño."
        ),
        "fb_e06_e7_bigger": (
            "Ahí sí existe, pero te piden el PRIMER peldaño donde ya existe. → Baja y "
            "comprueba si todavía sirve."
        ),
    },
    "closing": (
        "La raíz deshace la potencia y se reparte sobre el producto, nunca sobre la suma. "
        "Con ella termina la ciudad de las operaciones: las seis construyeron, entre todas, "
        "la escalera de conjuntos que ya conocías."
    ),
    "validation_status": "F2_E06_11bloques",
}
