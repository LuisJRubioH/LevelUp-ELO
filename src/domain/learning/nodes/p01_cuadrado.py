"""P01 · La matriz cuadrada — el exponente no se reparte sobre una suma.

Primera sala de La sala de los troqueles, en la Casa de la Sabiduría (Bagdad).
Guía: Rayhana. Vocabulario propio: matriz, lámina de cobre, orla, esquina,
plancha, tirada. Nada de cenefas ni cuños (P02), moldes ni capas (P03),
bandejas ni parejas (P04).

Error focal: desarrollar (a + b)² como a² + b², perdiendo el término 2ab.
La orla de la lámina es exactamente ese término que se olvida.

Ítems de práctica derivados de Hipertexto U4 p74 (A2a, A2b) y p75 (A1f).
"""

NODE_ID = "ALG-N2-P01-CUADRADO"
CONCEPT_SLUG = "cuadrado_de_binomio"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "cuadrado_de_binomio",
    "misconception": "binomio_cuadrado_falta_2ab",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La matriz cuadrada · Cuadrado de binomio",
    "house": "La matriz cuadrada",
    "guide": "Rayhana",
    "finish_label": "Pasar al cuño de la cenefa",
    "title": "Al agrandar una lámina aparece una orla que nadie pidió",
    "intro": (
        "En Kemet multiplicaste término a término y funcionó siempre. Aquí vas a "
        "encontrarte con un producto que aparece tantas veces que conviene tener un "
        "troquel para él. Pero el troquel estampa tres piezas, y casi todo el mundo "
        "recuerda solo dos."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar en la sala. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 7²?",
                "answer": "49",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $(3\cdot 5)^{2}$?",
                "options": [
                    {"id": "both", "text": r"$3^{2}\cdot 5^{2}$", "latex": r"3^{2}\cdot 5^{2}"},
                    {"id": "sum", "text": r"$3^{2}+5^{2}$", "latex": r"3^{2}+5^{2}"},
                    {"id": "once", "text": r"$3\cdot 5^{2}$", "latex": r"3\cdot 5^{2}"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "sum": "reparte_la_potencia_sobre_la_suma",
                    "once": "eleva_solo_el_segundo_factor",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Calcula 10² y luego (7 + 3)². ¿Cuánto vale el segundo?",
                "answer": "100",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/06-alg-n2-troqueles/p01-cuadrado-katia.png",
        "eyebrow": "KatIA · En la matriz cuadrada",
        "title": "La lámina que salió pequeña",
        "body": (
            "La sala guarda las matrices: planchas de cobre con las que se estampan "
            "láminas cuadradas. Cada matriz tiene un lado, y el lado se mide en dedos.\n\n"
            "Rayhana señala una hoja de encargo de la semana pasada:\n\n"
            "«Pedían una lámina cuadrada de lado 7 dedos, y al llegar el encargo la "
            "querían de lado 10: siete dedos y tres más. El aprendiz calculó el cobre "
            "necesario sumando lo que ocupa un cuadrado de 7 con lo que ocupa uno de 3. "
            "Cuarenta y nueve más nueve: cincuenta y ocho.»\n\n"
            "«La lámina de lado 10 ocupa cien. Faltaron cuarenta y dos dedos de cobre, y "
            "la lámina salió con un borde sin estampar.»"
        ),
        "question": "Al agrandar un cuadrado de lado 7 a lado 10, ¿dónde se metió el cobre que faltó?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "orla", "text": "En un borde alrededor del cuadrado viejo"},
                {"id": "esquina", "text": "Solo en la esquina nueva"},
                {"id": "nada", "text": "En ningún sitio: 49 + 9 debería bastar"},
            ],
            "response": (
                "Guarda tu respuesta. Al final del nodo vas a poder señalar con el dedo "
                "las piezas exactas que faltaban, y a decir cuántos dedos ocupa cada una."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Cuatro piezas, no dos",
        "body": (
            "Estampar un cuadrado de lado a + b es estampar cuatro piezas sobre la misma "
            "plancha. Dos son cuadrados y dos son tiras iguales."
        ),
        "cases": [
            {
                "label": "Lo que sí se reparte",
                "context": r"$(a\cdot b)^{2}$ — un producto elevado al cuadrado",
                "fraction": r"(a\,b)^{2}=a\,b\cdot a\,b",
                "division": r"a^{2}b^{2}",
                "note": (
                    "Aquí sí se puede repartir el exponente: los factores se reordenan y "
                    "cada uno se junta con su pareja. Nada sobra."
                ),
            },
            {
                "label": "Lo que no se reparte",
                "context": r"$(a+b)^{2}$ — una suma elevada al cuadrado",
                "fraction": r"(a+b)^{2}=(a+b)(a+b)",
                "division": r"a^{2}+2ab+b^{2}",
                "note": (
                    "Al multiplicar término a término salen cuatro productos: a·a, a·b, "
                    "b·a y b·b. Los dos del medio son iguales y se juntan en 2ab. Esa es "
                    "la orla."
                ),
            },
        ],
        "resolution": (
            "El exponente se reparte sobre productos y cocientes, nunca sobre sumas ni "
            "restas. Con lado 7 + 3: el cuadrado de 7 ocupa 49, el de 3 ocupa 9, y las dos "
            "tiras ocupan 2 · 7 · 3 = 42. Justo el cobre que faltó."
        ),
    },
    "definition_title": "Cuadrado de un binomio",
    "definition_katex": (
        r"(a+b)^{2} = a^{2} + 2ab + b^{2} \qquad (a-b)^{2} = a^{2} - 2ab + b^{2}"
    ),
    "definition": (
        "El cuadrado de un binomio tiene TRES términos: el cuadrado del primero, el doble "
        "del producto de los dos, y el cuadrado del segundo. El signo del término del "
        "medio es el signo que separa al binomio; los dos cuadrados salen siempre "
        "positivos, porque un cuadrado nunca es negativo."
    ),
    "definition_symbols": [
        {
            "symbol": r"a^{2}",
            "reads": "a al cuadrado",
            "means": "la lámina del lado viejo",
        },
        {
            "symbol": r"2ab",
            "reads": "dos a b",
            "means": "las dos tiras de la orla — el término que se olvida",
        },
        {
            "symbol": r"b^{2}",
            "reads": "b al cuadrado",
            "means": "la esquina nueva, el cuadradito de la ampliación",
        },
        {
            "symbol": r"(a-b)^{2}",
            "reads": "a menos b, al cuadrado",
            "means": "misma matriz, la orla se resta en vez de sumarse",
        },
        {
            "symbol": r"(ab)^{2}=a^{2}b^{2}",
            "reads": "a b al cuadrado es a cuadrado por b cuadrado",
            "means": "sobre un producto el exponente sí se reparte",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Una lámina con el lado en dedos",
            "title": "Las tres piezas, una por una",
            "statement": (
                "Rayhana pide estampar una lámina de lado 6x + 1 dedos. ¿Cuánto cobre "
                "ocupa?"
            ),
            "latex": r"(6x+1)^{2}",
            "image_slot": False,
            "steps": [
                "Cuadrado del primero: (6x)² = 36x². Ojo, se eleva el 6 y la x.",
                "Doble producto: 2 · 6x · 1 = 12x. Esta es la orla.",
                "Cuadrado del segundo: 1² = 1. La esquina.",
                "Queda 36x² + 12x + 1.",
                "Compruebo con x = 1: el lado mide 7 y la lámina ocupa 49. Y 36 + 12 + 1 = 49 ✓.",
            ],
            "solution": r"$(6x+1)^{2}=36x^{2}+12x+1$",
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "¿Por qué la orla vale 12x y no 6x, si la tira de un lado mide 6x · 1?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando el binomio resta",
            "title": "La orla también puede quitar",
            "statement": (
                "Otra matriz: lado 9m⁴ − 3n. Mismo troquel, y hay que vigilar un signo."
            ),
            "latex": r"(9m^{4}-3n)^{2}",
            "image_slot": False,
            "steps": [
                "Cuadrado del primero: (9m⁴)² = 81m⁸.",
                "Doble producto: 2 · 9m⁴ · 3n = 54m⁴n, y va restando porque el binomio resta.",
                "Cuadrado del segundo: (3n)² = 9n². Positivo, aunque el término restaba.",
                "Queda 81m⁸ − 54m⁴n + 9n².",
                "Solo el término del medio cambia de signo. Los de los extremos son cuadrados: nunca negativos.",
            ],
            "solution": r"$(9m^{4}-3n)^{2}=81m^{8}-54m^{4}n+9n^{2}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que estampó dos piezas de tres",
            "statement": (
                "Vuelve el encargo de la apertura, ahora con letras. El aprendiz anota el "
                "cobre de una lámina de lado x + 4 así:"
            ),
            "latex": r"(x+4)^{2}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"(x+4)^{2}=x^{2}+16",
            "error_note": (
                "Repartió el exponente sobre la suma, que es justo lo que no se puede "
                "hacer. Estampó los dos cuadrados y se dejó la orla."
            ),
            "correct_version": {
                "wrong_latex": r"(x+4)^{2}=x^{2}+16",
                "right_latex": r"(x+4)^{2}=x^{2}+8x+16",
                "rows": [
                    {
                        "wrong": "El exponente entra a cada sumando",
                        "right": "El exponente entra a cada factor, y una suma no es un producto",
                    },
                    {
                        "wrong": "Dos piezas: la lámina vieja y la esquina",
                        "right": "Tres piezas: la lámina, las dos tiras y la esquina",
                    },
                ],
            },
            "explain_prompt": (
                "Comprueba con x = 1 que la anotación del aprendiz da un número distinto, "
                "y di cuánto cobre se perdió."
            ),
            "steps": [
                "Con x = 1 el lado mide 5, así que la lámina ocupa 25.",
                "La anotación del aprendiz da 1 + 16 = 17. Faltan 8, que es justo 8x con x = 1.",
                "Regla para no volver a caer: antes de cerrar, cuenta los términos. Si son dos, falta la orla.",
            ],
            "solution": (
                "(x + 4)² = x² + 8x + 16. El cuadrado de una suma tiene tres términos, "
                "siempre."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La hoja de encargo va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Desarrolla $(x+5)^{2}$.",
                "given_steps": [r"x^{2}", r"5^{2}=25"],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{coeficiente de la orla}=", "answer": "10"}
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Desarrolla $(2x-3)^{2}$.",
                "given_steps": [r"(2x)^{2}=4x^{2}", r"(-3)^{2}=9"],
                "blanks": [
                    {"id": "P2-b1", "label": r"2\cdot 2x\cdot 3=", "answer": "12"},
                    {"id": "P2-b2", "label": r"\text{con }x=1:\ 4-12+9=", "answer": "1"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $[7w-(a^{2}+7w)]^{2}$. Simplifica el interior "
                    "del corchete ANTES de estampar el troquel."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{exponente de }a\text{ en el resultado}=", "answer": "4"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de estampar el mismo cuadrado",
        "intro": r"$(x+2)^{2}$. Las dos llegan al mismo sitio; una enseña por qué.",
        "methods": [
            {
                "label": "Método 1 · El troquel",
                "steps": [
                    r"(x+2)^{2}",
                    r"x^{2}+2\cdot x\cdot 2+2^{2}",
                    r"x^{2}+4x+4",
                ],
                "note": "Tres golpes y listo, pero hay que fiarse de que el del medio existe.",
            },
            {
                "label": "Método 2 · Multiplicar término a término",
                "steps": [
                    r"(x+2)(x+2)",
                    r"x\cdot x+x\cdot 2+2\cdot x+2\cdot 2",
                    r"x^{2}+2x+2x+4=x^{2}+4x+4",
                ],
                "note": "Más largo, pero se ve nacer la orla: son dos productos cruzados iguales.",
            },
        ],
        "question": "¿Cuál de los dos explica de dónde sale el 2 del doble producto?",
        "insight": (
            "El segundo. El troquel es el atajo, pero quien solo conoce el atajo no tiene "
            "cómo notar que le falta una pieza. Multiplicando término a término aparecen "
            "cuatro productos, y los dos del medio —x·2 y 2·x— son el mismo número contado "
            "dos veces. Por eso el término del medio lleva un 2 delante: no es una regla "
            "que memorizar, es una tira contada por sus dos lados."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿A qué equivale $(a+b)^{2}$?",
            "options": [
                {"id": "full", "text": r"$a^{2}+2ab+b^{2}$", "latex": r"a^{2}+2ab+b^{2}"},
                {"id": "split", "text": r"$a^{2}+b^{2}$", "latex": r"a^{2}+b^{2}"},
                {"id": "once", "text": r"$a^{2}+ab+b^{2}$", "latex": r"a^{2}+ab+b^{2}"},
                {"id": "double", "text": r"$2a+2b$", "latex": r"2a+2b"},
            ],
            "expected": "full",
            "feedback_by_option": {
                "full": "correct",
                "split": "fb_p01_e1_split",
                "once": "fb_p01_e1_once",
                "double": "fb_p01_e1_double",
            },
            "misconception_by_option": {
                "split": "binomio_cuadrado_falta_2ab",
                "once": "olvida_el_doble_en_el_producto_cruzado",
                "double": "confunde_cuadrado_con_duplicar",
            },
            "hints": {
                "n1": "Cuenta las piezas de la lámina: ¿son dos o son cuatro?",
                "n2": "Las dos tiras del medio son iguales.",
                "n3": "Prueba con a = 7 y b = 3: la lámina ocupa 100.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Desarrolla $(6x+1)^{2}$. Usa $\wedge$ para el exponente, así: 36x^2+12x+1. "
                "No dejes espacios."
            ),
            "answer": "36x^2+12x+1",
            "hints": {
                "n1": "Cuadrado del primero: (6x)² — se elevan el 6 y la x.",
                "n2": "Orla: 2 · 6x · 1.",
                "n3": "La esquina es 1² = 1.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Una lámina tiene lado $x+5$ dedos. Con $x=3$, ¿cuánto cobre ocupa?"
            ),
            "expr": r"(x+5)^{2}=x^{2}+10x+25,\quad x=3",
            "answer": "64",
            "hints": {
                "n1": "Puedes sumar primero: 3 + 5.",
                "n2": "O estampar el troquel: 9 + 30 + 25.",
                "n3": "Las dos vías dan lo mismo. Ese es el punto.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En $(2x-3)^{2}$, ¿cuál es el coeficiente del término del medio, sin el signo?"
            ),
            "expr": r"2\cdot 2x\cdot 3=12x",
            "answer": "12",
            "hints": {
                "n1": "La orla es el doble del producto de los dos términos.",
                "n2": "2 · 2 · 3.",
                "n3": "El signo va aparte: aquí resta.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un aprendiz anota $(3m-4)^{2}=9m^{2}-24m-16$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "sign", "text": r"El último término: $(-4)^{2}=+16$, no $-16$"},
                {"id": "middle", "text": r"La orla: debería ser $-12m$"},
                {"id": "first", "text": r"El primero: debería ser $3m^{2}$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "sign",
            "feedback_by_option": {
                "sign": "correct",
                "middle": "fb_p01_e5_middle",
                "first": "fb_p01_e5_first",
                "none": "fb_p01_e5_none",
            },
            "misconception_by_option": {
                "middle": "olvida_el_doble_en_el_producto_cruzado",
                "first": "eleva_solo_la_letra_y_no_el_coeficiente",
                "none": "cuadrado_de_negativo_es_negativo",
            },
            "hints": {
                "n1": "La orla está bien: 2 · 3m · 4 = 24m, y resta.",
                "n2": "Mira los extremos. ¿Un cuadrado puede dar negativo?",
                "n3": "(−4) · (−4) = +16.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Elevar al cuadrado se puede hacer término a término, "
                "igual que con un producto.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: sobre una suma aparece además el doble producto",
                },
                {"id": "true", "text": "Verdadera: el exponente entra a cada término"},
                {
                    "id": "true_pos",
                    "text": "Verdadera solo cuando los dos términos son positivos",
                },
                {
                    "id": "false_never",
                    "text": "Falsa: el exponente nunca se puede repartir, ni sobre productos",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_p01_e6_trap",
                "true_pos": "fb_p01_e6_pos",
                "false_never": "fb_p01_e6_never",
            },
            "misconception_by_option": {
                "true": "binomio_cuadrado_falta_2ab",
                "true_pos": "binomio_cuadrado_falta_2ab",
                "false_never": "reparte_la_potencia_sobre_la_suma",
            },
            "hints": {
                "n1": "Prueba con números: (2 + 3)² frente a 2² + 3².",
                "n2": "25 frente a 13. La diferencia es 12 = 2 · 2 · 3.",
                "n3": "Sobre un producto sí se reparte: (2 · 3)² = 4 · 9 = 36.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Rayhana va a estampar cuatro encargos. ¿En cuáles hace falta la orla, o "
                "sea el doble producto? Marca todas las que apliquen."
            ),
            "options": [
                {"id": "sum", "text": r"$(x+7)^{2}$"},
                {"id": "dif", "text": r"$(x-7)^{2}$"},
                {"id": "prod", "text": r"$(7x)^{2}$"},
                {"id": "quot", "text": r"$\left(\dfrac{x}{7}\right)^{2}$"},
            ],
            "expected": ["sum", "dif"],
            "valid_options": ["sum", "dif", "prod", "quot"],
            "trap_options": ["prod", "quot"],
            "feedback_by_option": {"sum": "correct", "dif": "correct"},
            "misconception_by_option": {
                "prod": "reparte_la_potencia_sobre_la_suma",
                "quot": "reparte_la_potencia_sobre_la_suma",
            },
            "hints": {
                "n1": "La orla aparece cuando dentro del paréntesis hay una suma o una resta.",
                "n2": "Un producto y un cociente sí admiten repartir el exponente.",
                "n3": "Son dos de los cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿El exponente se puede repartir?",
        "title": "Dónde vale el atajo y dónde cuesta una orla",
        "intro": (
            "El error de hoy no es olvidarse de un término: es repartir el exponente donde "
            "no se puede. Esta es la lista de dónde sí."
        ),
        "rows": [
            {
                "name": "Producto",
                "symbol": r"(ab)^{2}",
                "latex": r"(ab)^{2}=a^{2}b^{2}",
                "closed": "yes",
                "note": "Los factores se reordenan y cada uno se junta con su pareja.",
            },
            {
                "name": "Cociente",
                "symbol": r"\left(\dfrac{a}{b}\right)^{2}",
                "latex": r"\left(\dfrac{a}{b}\right)^{2}=\dfrac{a^{2}}{b^{2}}",
                "closed": "yes",
                "note": "Mismo motivo: dividir es multiplicar por el recíproco.",
            },
            {
                "name": "Suma",
                "symbol": r"(a+b)^{2}",
                "latex": r"(a+b)^{2}=a^{2}+2ab+b^{2}",
                "closed": "no",
                "note": "Aparece la orla. Repartir aquí cuesta 2ab de cobre.",
            },
            {
                "name": "Resta",
                "symbol": r"(a-b)^{2}",
                "latex": r"(a-b)^{2}=a^{2}-2ab+b^{2}",
                "closed": "no",
                "note": "La orla también está: resta en vez de sumar, pero está.",
            },
            {
                "name": "Suma con un término nulo",
                "symbol": r"(a+0)^{2}",
                "latex": r"(a+0)^{2}=a^{2}+0+0",
                "closed": "partial",
                "note": (
                    "Aquí repartir da la respuesta correcta — pero por casualidad: la orla "
                    "vale 2·a·0 = 0. Acertar no es lo mismo que tener razón."
                ),
            },
            {
                "name": "Raíz de un producto",
                "symbol": r"\sqrt{ab}",
                "latex": r"\sqrt{ab}=\sqrt{a}\sqrt{b}",
                "closed": "partial",
                "note": (
                    "Se reparte igual que la potencia, pero solo con a y b no negativos. "
                    "Fuera de ahí deja de valer."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **el exponente se reparte sobre lo que se multiplica, "
            "no sobre lo que se suma.** Y cuando hay suma, lo que aparece de más es el "
            "doble producto."
        ),
    },
    "abstraction_question": {
        "prompt": (
            "Mira los tres desarrollos. ¿Qué es lo único que cambia entre ellos, y qué se "
            "mantiene igual?"
        ),
        "thumbnails": [
            r"(x+3)^{2}=x^{2}+6x+9",
            r"(2x+3)^{2}=4x^{2}+12x+9",
            r"(x-3)^{2}=x^{2}-6x+9",
        ],
        "options": [
            {
                "id": "structure",
                "text": (
                    "Siempre son tres términos con la misma estructura; cambian el "
                    "coeficiente del primero y el signo de la orla"
                ),
                "correct": True,
            },
            {
                "id": "terms",
                "text": "Cambia el número de términos según el signo del binomio",
                "correct": False,
            },
            {
                "id": "last",
                "text": "Cambia el último término según el signo del binomio",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Rayhana necesita una lámina cuadrada de lado 4x + 5 dedos. Con x = 2, "
            "¿cuánto cobre ocupa?"
        ),
        "polya": [
            "Entender: el lado es 4x + 5 y hay que hallar el área del cuadrado.",
            "Planear: o sustituyo primero y elevo, o estampo el troquel y sustituyo después.",
            "Ejecutar: 4·2 + 5 = 13, y 13² = 169.",
            "Comprobar: por el troquel, 16x² + 40x + 25 con x = 2 da 64 + 80 + 25 = 169 ✓.",
        ],
        "prompt": "¿Cuántos dedos de cobre ocupa la lámina?",
        "answer": "169",
        "hints": {
            "n1": "Primero calcula cuánto mide el lado con x = 2.",
            "n2": "El lado mide 13.",
            "n3": "13 · 13.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que conoces el troquel.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: hoy ves la orla donde antes había un hueco.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el reparto del "
            "exponente antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuánto es 12²?",
                "answer": "144",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿A qué equivale $(x+6)^{2}$?",
                "options": [
                    {"id": "full", "text": r"$x^{2}+12x+36$", "latex": r"x^{2}+12x+36"},
                    {"id": "split", "text": r"$x^{2}+36$", "latex": r"x^{2}+36"},
                    {"id": "once", "text": r"$x^{2}+6x+36$", "latex": r"x^{2}+6x+36"},
                ],
                "expected": "full",
                "misconception_by_option": {
                    "split": "binomio_cuadrado_falta_2ab",
                    "once": "olvida_el_doble_en_el_producto_cruzado",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "Calcula (8 + 2)². ¿Cuánto vale?",
                "answer": "100",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de pasar al cuño de la cenefa.",
            "consolidacion": "Resuelto con ayuda: el troquel ya está, falta que salga solo.",
            "sin_ayuda": "Estampado limpio. La orla ya no se te escapa.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Las tres piezas en su sitio.",
        "default": (
            "Cuenta las piezas de la lámina antes de cerrar: si solo escribiste dos, "
            "falta la orla."
        ),
        "fb_p01_e1_split": (
            "Ese es justo el reparto que no se puede hacer. Con a = 7 y b = 3 tu respuesta "
            "da 58 y la lámina ocupa 100: faltan las dos tiras, 2·7·3 = 42."
        ),
        "fb_p01_e1_once": (
            "Casi. La tira está, pero contada una sola vez. Son dos tiras iguales —x·b y "
            "b·x—, por eso el término lleva un 2 delante."
        ),
        "fb_p01_e1_double": (
            "Eso es duplicar el lado, no elevarlo al cuadrado. Elevar al cuadrado es "
            "multiplicar el lado por sí mismo."
        ),
        "fb_p01_e5_middle": (
            "La orla está bien: 2 · 3m · 4 = 24m, y resta porque el binomio resta. El "
            "problema está en otro término."
        ),
        "fb_p01_e5_first": (
            "El primero está bien: (3m)² eleva el 3 y la m, y da 9m². Mira el último."
        ),
        "fb_p01_e5_none": (
            "Sí lo hay: el último término es (−4)², y un número negativo al cuadrado da "
            "positivo. Debería ser +16."
        ),
        "fb_p01_e6_trap": (
            "Con un producto sí; con una suma no. (2 + 3)² = 25, pero 2² + 3² = 13. La "
            "diferencia, 12, es el doble producto."
        ),
        "fb_p01_e6_pos": (
            "El signo no tiene nada que ver: (2 − 3)² = 1 y 2² − 3² = −5. La orla aparece "
            "igual, restando."
        ),
        "fb_p01_e6_never": (
            "Te pasaste al otro lado. Sobre un producto sí se reparte: (2 · 3)² = 36 y "
            "2² · 3² = 4 · 9 = 36. Lo que no admite reparto es la suma."
        ),
    },
    "closing": (
        "Ya tienes el primer troquel de la sala: $(a+b)^{2}=a^{2}+2ab+b^{2}$, tres piezas "
        "y la del medio contada dos veces. En la mesa de al lado hay un cuño distinto: "
        "estampa dos láminas que se diferencian solo en un signo, y al juntarlas la orla "
        "desaparece."
    ),
    "validation_status": "F5_P01_11bloques",
}
