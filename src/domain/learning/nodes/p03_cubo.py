"""P03 · El molde de tres capas — elevar al cubo deja cuatro capas, no dos.

Tercera sala de La sala de los troqueles (Casa de la Sabiduría, Bagdad).
Guía: Rayhana. Vocabulario propio: molde, capa, vaciado, arcilla, cochura,
altura. Nada de matrices ni orlas (P01), cuños ni grecas (P02), bandejas ni
parejas (P04).

Error focal: desarrollar (a + b)³ como a³ + b³, perdiendo las dos capas
intermedias. En el cuadrado se perdía una; aquí se pierden dos.

Ítems de práctica derivados de Hipertexto U4 p83 (A1a, A2a, A2b, A2c, A2d).
"""

NODE_ID = "ALG-N2-P03-CUBO"
CONCEPT_SLUG = "cubo_de_binomio"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "cubo_de_binomio",
    "misconception": "binomio_cubo_falta_terminos",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El molde de tres capas · Cubo de binomio",
    "house": "El molde de tres capas",
    "guide": "Rayhana",
    "finish_label": "Pasar a la bandeja de parejas",
    "title": "Al subir de dos a tres, no se pierde una pieza: se pierden dos",
    "intro": (
        "Ya viste que elevar una suma al cuadrado deja tres términos y no dos. Aquí la "
        "pregunta es qué pasa al subir un piso más. La respuesta no es «uno más»: el molde "
        "deja cuatro capas, y las dos de en medio son las que se caen del registro."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de encender el horno. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 2³?",
                "answer": "8",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $(x+1)^{2}$?",
                "options": [
                    {"id": "full", "text": r"$x^{2}+2x+1$", "latex": r"x^{2}+2x+1"},
                    {"id": "split", "text": r"$x^{2}+1$", "latex": r"x^{2}+1"},
                    {"id": "double", "text": r"$2x+2$", "latex": r"2x+2"},
                ],
                "expected": "full",
                "misconception_by_option": {
                    "split": "binomio_cuadrado_falta_2ab",
                    "double": "confunde_cuadrado_con_duplicar",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Calcula (2 + 1)³.",
                "answer": "27",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/06-alg-n2-troqueles/p03-cubo-katia.png",
        "eyebrow": "KatIA · En el molde de tres capas",
        "title": "El bloque de arcilla que salió hueco",
        "body": (
            "Al fondo de la sala hay moldes altos: en vez de estampar una lámina plana, "
            "vacían un bloque macizo de arcilla. El molde se llena por capas.\n\n"
            "Rayhana desenrolla una hoja manchada de barro:\n\n"
            "«Pedían un bloque cúbico de arista 3 dedos, y luego lo quisieron de arista 4: "
            "tres dedos y uno más. El aprendiz calculó la arcilla sumando el bloque de tres "
            "con el bloque de uno. Veintisiete más uno: veintiocho.»\n\n"
            "«El bloque de arista cuatro se lleva sesenta y cuatro. Faltaron treinta y seis "
            "dedos de arcilla, y el bloque salió hueco por dentro.»"
        ),
        "question": (
            "Al pasar de un cubo de arista 3 a uno de arista 4, ¿dónde se metió toda esa "
            "arcilla que faltó?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "capas", "text": "En unas capas planas pegadas a las caras del cubo viejo"},
                {"id": "esquina", "text": "Solo en la esquina nueva del cubo"},
                {"id": "nada", "text": "En ningún sitio: 27 + 1 debería bastar"},
            ],
            "response": (
                "Guarda tu respuesta. Al final del nodo vas a poder decir cuántas capas hay, "
                "cuánto mide cada una y por qué dos de ellas van repetidas tres veces."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El molde se llena por capas, y hay cuatro",
        "body": (
            "Elevar al cubo es elevar al cuadrado y volver a multiplicar. Ahí se ve de "
            "dónde salen las capas de en medio."
        ),
        "cases": [
            {
                "label": "Paso a paso",
                "context": r"$(a+b)^{3}=(a+b)^{2}(a+b)$",
                "fraction": r"(a^{2}+2ab+b^{2})(a+b)",
                "division": r"a^{3}+3a^{2}b+3ab^{2}+b^{3}",
                "note": (
                    "Cada uno de los tres términos del cuadrado se multiplica por a y por b. "
                    "Al juntar semejantes aparecen los dos treses."
                ),
            },
            {
                "label": "Los coeficientes crecen",
                "context": r"Lo que deja cada altura del molde",
                "fraction": r"\begin{matrix}1&1\\1&2&1\\1&3&3&1\end{matrix}",
                "division": r"n+1\ \text{capas}",
                "note": (
                    "Una suma elevada a n deja n + 1 capas. Al cuadrado, tres; al cubo, "
                    "cuatro. Nunca dos."
                ),
            },
        ],
        "resolution": (
            "Con arista 3 + 1: el cubo de 3 se lleva 27, el de 1 se lleva 1, y las capas de "
            "en medio se llevan 3·9·1 = 27 y 3·3·1 = 9. Suma: 27 + 27 + 9 + 1 = 64. Justo el "
            "bloque completo."
        ),
    },
    "definition_title": "Cubo de un binomio",
    "definition_katex": (
        r"(a+b)^{3} = a^{3} + 3a^{2}b + 3ab^{2} + b^{3} \qquad "
        r"(a-b)^{3} = a^{3} - 3a^{2}b + 3ab^{2} - b^{3}"
    ),
    "definition": (
        "El cubo de un binomio tiene CUATRO términos. Los exponentes del primero bajan "
        "3, 2, 1, 0 y los del segundo suben 0, 1, 2, 3; los coeficientes van 1, 3, 3, 1. "
        "Si el binomio resta, los signos se alternan: más, menos, más, menos."
    ),
    "definition_symbols": [
        {
            "symbol": r"a^{3}",
            "reads": "a al cubo",
            "means": "el bloque viejo, la primera capa",
        },
        {
            "symbol": r"3a^{2}b",
            "reads": "tres a al cuadrado b",
            "means": "las tres losas planas pegadas a las caras",
        },
        {
            "symbol": r"3ab^{2}",
            "reads": "tres a b al cuadrado",
            "means": "las tres varillas de las aristas",
        },
        {
            "symbol": r"b^{3}",
            "reads": "b al cubo",
            "means": "el cubito de la esquina",
        },
        {
            "symbol": r"1,3,3,1",
            "reads": "uno, tres, tres, uno",
            "means": "los coeficientes: en el cuadrado eran 1, 2, 1",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Un bloque de arista con letra",
            "title": "Las cuatro capas, una por una",
            "statement": "Rayhana encarga un bloque de arista $y+2$ dedos. ¿Cuánta arcilla lleva?",
            "latex": r"(y+2)^{3}",
            "image_slot": False,
            "steps": [
                "Cubo del primero: y³.",
                "Tres veces el cuadrado del primero por el segundo: 3 · y² · 2 = 6y².",
                "Tres veces el primero por el cuadrado del segundo: 3 · y · 4 = 12y.",
                "Cubo del segundo: 2³ = 8.",
                "Queda y³ + 6y² + 12y + 8. Compruebo con y = 1: la arista mide 3 y el bloque 27. Y 1 + 6 + 12 + 8 = 27 ✓.",
            ],
            "solution": r"$(y+2)^{3}=y^{3}+6y^{2}+12y+8$",
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "¿Por qué la capa lleva un 3 delante, si el molde solo tiene una cara "
                    "arriba?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando la arista resta",
            "title": "Los signos se alternan",
            "statement": (
                "Otro encargo: arista $2a-3$. Mismo molde, y ahora hay que vigilar cuatro signos."
            ),
            "latex": r"(2a-3)^{3}",
            "image_slot": False,
            "steps": [
                "Cubo del primero: (2a)³ = 8a³. Se eleva el 2 y la a.",
                "Tres por el cuadrado del primero por el segundo: 3 · 4a² · 3 = 36a², y va restando.",
                "Tres por el primero por el cuadrado del segundo: 3 · 2a · 9 = 54a, y va sumando.",
                "Cubo del segundo: (−3)³ = −27. Un cubo SÍ conserva el signo, a diferencia de un cuadrado.",
                "Queda 8a³ − 36a² + 54a − 27. Más, menos, más, menos.",
            ],
            "solution": r"$(2a-3)^{3}=8a^{3}-36a^{2}+54a-27$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que vació dos capas de cuatro",
            "statement": (
                "Vuelve el bloque de la apertura, ahora con letras. El aprendiz anota la "
                "arcilla de una arista $x+3$ así:"
            ),
            "latex": r"(x+3)^{3}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"(x+3)^{3}=x^{3}+27",
            "error_note": (
                "Repartió el exponente sobre la suma, igual que en la matriz cuadrada — pero "
                "aquí no se cae una capa, se caen dos."
            ),
            "correct_version": {
                "wrong_latex": r"(x+3)^{3}=x^{3}+27",
                "right_latex": r"(x+3)^{3}=x^{3}+9x^{2}+27x+27",
                "rows": [
                    {
                        "wrong": "Dos capas: el bloque viejo y el cubito",
                        "right": "Cuatro capas: el bloque, tres losas, tres varillas y el cubito",
                    },
                    {
                        "wrong": "Los coeficientes son 1 y 1",
                        "right": "Los coeficientes son 1, 3, 3, 1",
                    },
                ],
            },
            "explain_prompt": (
                "Comprueba con x = 1 cuánta arcilla falta en la anotación del aprendiz, y di "
                "a qué dos capas corresponde."
            ),
            "steps": [
                "Con x = 1 la arista mide 4 y el bloque se lleva 64.",
                "La anotación del aprendiz da 1 + 27 = 28. Faltan 36.",
                "Esos 36 son 9x² + 27x con x = 1: las losas y las varillas.",
                "Regla para no volver a caer: cuenta las capas. Al cubo son cuatro, siempre.",
            ],
            "solution": (
                "(x + 3)³ = x³ + 9x² + 27x + 27. Elevar una suma al cubo deja cuatro " "términos."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La hoja del horno va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Desarrolla $(m-3)^{3}$.",
                "given_steps": [r"m^{3}", r"3\cdot m^{2}\cdot 3=9m^{2}\ \text{(resta)}"],
                "blanks": [
                    {
                        "id": "P1-b1",
                        "label": r"3\cdot m\cdot 3^{2}=\ \_\_\,m\ \text{, coeficiente}=",
                        "answer": "27",
                    }
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Desarrolla $(3x+2)^{3}$.",
                "given_steps": [r"(3x)^{3}=27x^{3}", r"2^{3}=8"],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"3\cdot (3x)^{2}\cdot 2\ \text{, coeficiente}=",
                        "answer": "54",
                    },
                    {
                        "id": "P2-b2",
                        "label": r"3\cdot 3x\cdot 2^{2}\ \text{, coeficiente}=",
                        "answer": "36",
                    },
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $(3x^{2})^{3}$. Ojo, esto NO es un binomio — "
                    "decide antes si el molde de cuatro capas aplica."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{coeficiente del resultado}=", "answer": "27"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de llegar a las cuatro capas",
        "intro": r"$(x+1)^{3}$. Una la memoriza; la otra la construye.",
        "methods": [
            {
                "label": "Método 1 · El molde de memoria",
                "steps": [
                    r"(x+1)^{3}",
                    r"1,3,3,1\ \text{sobre}\ x^{3},x^{2},x,1",
                    r"x^{3}+3x^{2}+3x+1",
                ],
                "note": "Rapidísimo, pero si se olvida un 3 no hay nada que avise.",
            },
            {
                "label": "Método 2 · Cuadrado y otra vuelta",
                "steps": [
                    r"(x+1)^{2}(x+1)",
                    r"(x^{2}+2x+1)(x+1)",
                    r"x^{3}+x^{2}+2x^{2}+2x+x+1=x^{3}+3x^{2}+3x+1",
                ],
                "note": "Más largo, pero los treses aparecen solos al juntar semejantes.",
            },
        ],
        "question": "¿Cuál de los dos explica de dónde salen los dos treses?",
        "insight": (
            "El segundo. El molde de memoria da el resultado, pero los coeficientes 1, 3, 3, 1 "
            "quedan como un conjuro. Multiplicando el cuadrado por el binomio se ve que el 3 "
            "es una suma: x² viene una vez de x²·x y dos veces de 2x·x. El coeficiente no es "
            "una regla, es una cuenta de cuántas maneras sale la misma capa."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿A qué equivale $(a+b)^{3}$?",
            "options": [
                {
                    "id": "full",
                    "text": r"$a^{3}+3a^{2}b+3ab^{2}+b^{3}$",
                    "latex": r"a^{3}+3a^{2}b+3ab^{2}+b^{3}",
                },
                {"id": "split", "text": r"$a^{3}+b^{3}$", "latex": r"a^{3}+b^{3}"},
                {
                    "id": "square",
                    "text": r"$a^{3}+2ab+b^{3}$",
                    "latex": r"a^{3}+2ab+b^{3}",
                },
                {"id": "triple", "text": r"$3a+3b$", "latex": r"3a+3b"},
            ],
            "expected": "full",
            "feedback_by_option": {
                "full": "correct",
                "split": "fb_p03_e1_split",
                "square": "fb_p03_e1_square",
                "triple": "fb_p03_e1_triple",
            },
            "misconception_by_option": {
                "split": "binomio_cubo_falta_terminos",
                "square": "usa_los_coeficientes_del_cuadrado_en_el_cubo",
                "triple": "confunde_cubo_con_triplicar",
            },
            "hints": {
                "n1": "Cuenta las capas: una suma al cubo deja cuatro términos.",
                "n2": "Los coeficientes van 1, 3, 3, 1.",
                "n3": "Prueba con a = 3 y b = 1: el bloque se lleva 64.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Desarrolla $(y+2)^{3}$. Usa $\wedge$ para el exponente, así: "
                "y^3+6y^2+12y+8. No dejes espacios."
            ),
            "answer": "y^3+6y^2+12y+8",
            "hints": {
                "n1": "Cubo del primero: y³.",
                "n2": "Las capas de en medio: 3·y²·2 y 3·y·2².",
                "n3": "El cubito de la esquina es 2³ = 8.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (r"Un bloque tiene arista $x+1$ dedos. Con $x=3$, ¿cuánta arcilla lleva?"),
            "expr": r"(x+1)^{3},\quad x=3",
            "answer": "64",
            "hints": {
                "n1": "Primero calcula la arista: 3 + 1.",
                "n2": "La arista mide 4.",
                "n3": "4 · 4 · 4.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En $(2a-3)^{3}$, ¿cuál es el coeficiente del término con $a^{2}$, sin el signo?"
            ),
            "expr": r"3\cdot (2a)^{2}\cdot 3=36a^{2}",
            "answer": "36",
            "hints": {
                "n1": "Esa capa es 3 · (primero)² · (segundo).",
                "n2": "(2a)² = 4a².",
                "n3": "3 · 4 · 3.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (r"Un aprendiz anota $(x-2)^{3}=x^{3}-6x^{2}+12x+8$. ¿Dónde está el error?"),
            "options": [
                {"id": "last", "text": r"El último: $(-2)^{3}=-8$, no $+8$"},
                {"id": "middle", "text": r"El de $x^{2}$: debería ser $+6x^{2}$"},
                {"id": "third", "text": r"El de $x$: debería ser $-12x$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "last",
            "feedback_by_option": {
                "last": "correct",
                "middle": "fb_p03_e5_middle",
                "third": "fb_p03_e5_third",
                "none": "fb_p03_e5_none",
            },
            "misconception_by_option": {
                "middle": "signo_alterno_invertido",
                "third": "signo_alterno_invertido",
                "none": "cubo_de_negativo_es_positivo",
            },
            "hints": {
                "n1": "Los signos van alternando: +, −, +, −.",
                "n2": "El cuarto término debería restar.",
                "n3": "Un cubo conserva el signo: (−2)³ = −8, no +8.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Elevar una suma al cubo da el cubo de cada término, "
                "igual que elevar un producto.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: aparecen además dos capas intermedias"},
                {"id": "true", "text": "Verdadera: el exponente entra a cada término"},
                {
                    "id": "true_one",
                    "text": "Falsa, pero solo falta una capa, como en el cuadrado",
                },
                {
                    "id": "false_never",
                    "text": "Falsa: el exponente nunca se reparte, ni sobre productos",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_p03_e6_trap",
                "true_one": "fb_p03_e6_one",
                "false_never": "fb_p03_e6_never",
            },
            "misconception_by_option": {
                "true": "binomio_cubo_falta_terminos",
                "true_one": "binomio_cubo_falta_terminos",
                "false_never": "reparte_la_potencia_sobre_la_suma",
            },
            "hints": {
                "n1": "Prueba con (3 + 1)³ frente a 3³ + 1³.",
                "n2": "64 frente a 28. Faltan 36.",
                "n3": "Esos 36 son las dos capas de en medio: 27 y 9.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Rayhana revisa cuatro moldes. ¿En cuáles el resultado tiene CUATRO términos? "
                "Marca todas las que apliquen."
            ),
            "options": [
                {"id": "sum", "text": r"$(x+5)^{3}$"},
                {"id": "dif", "text": r"$(x-5)^{3}$"},
                {"id": "prod", "text": r"$(5x)^{3}$"},
                {"id": "sq", "text": r"$(x+5)^{2}$"},
            ],
            "expected": ["sum", "dif"],
            "valid_options": ["sum", "dif", "prod", "sq"],
            "trap_options": ["prod", "sq"],
            "feedback_by_option": {"sum": "correct", "dif": "correct"},
            "misconception_by_option": {
                "prod": "reparte_la_potencia_sobre_la_suma",
                "sq": "usa_los_coeficientes_del_cuadrado_en_el_cubo",
            },
            "hints": {
                "n1": "Una suma elevada a n deja n + 1 términos.",
                "n2": "Un producto elevado al cubo sigue siendo un solo término.",
                "n3": "El cuadrado deja tres, no cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Cuántas capas deja el molde?",
        "title": "El número de términos no es un capricho",
        "intro": (
            "Elevar una suma a n deja n + 1 términos, y los coeficientes se pueden leer de "
            "un triángulo. Esta es la lista de alturas."
        ),
        "rows": [
            {
                "name": "Altura 1",
                "symbol": r"(a+b)^{1}",
                "latex": r"a+b",
                "closed": "yes",
                "note": "2 términos, coeficientes 1 y 1.",
            },
            {
                "name": "Altura 2",
                "symbol": r"(a+b)^{2}",
                "latex": r"a^{2}+2ab+b^{2}",
                "closed": "yes",
                "note": "3 términos, coeficientes 1, 2, 1. La orla de la matriz cuadrada.",
            },
            {
                "name": "Altura 3",
                "symbol": r"(a+b)^{3}",
                "latex": r"a^{3}+3a^{2}b+3ab^{2}+b^{3}",
                "closed": "yes",
                "note": "4 términos, coeficientes 1, 3, 3, 1. El molde de esta sala.",
            },
            {
                "name": "Altura 3, restando",
                "symbol": r"(a-b)^{3}",
                "latex": r"a^{3}-3a^{2}b+3ab^{2}-b^{3}",
                "closed": "yes",
                "note": "Siguen siendo 4 términos; lo que cambia es que los signos alternan.",
            },
            {
                "name": "Altura 4",
                "symbol": r"(a+b)^{4}",
                "latex": r"a^{4}+4a^{3}b+6a^{2}b^{2}+4ab^{3}+b^{4}",
                "closed": "yes",
                "note": "5 términos, 1, 4, 6, 4, 1. El patrón sigue tan arriba como quieras.",
            },
            {
                "name": "Un producto, no una suma",
                "symbol": r"(ab)^{3}",
                "latex": r"a^{3}b^{3}",
                "closed": "partial",
                "note": (
                    "Aquí el molde no aplica: sigue siendo UN término. Sobre un producto el "
                    "exponente sí se reparte, y por eso no aparecen capas intermedias."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **una suma elevada a n deja n + 1 términos.** Si te salen "
            "dos, no importa a qué exponente elevaste: te faltan capas."
        ),
    },
    "abstraction_question": {
        "prompt": "Mira los tres desarrollos. ¿Qué se mantiene igual en los tres?",
        "thumbnails": [
            r"(x+1)^{3}=x^{3}+3x^{2}+3x+1",
            r"(2x+1)^{3}=8x^{3}+12x^{2}+6x+1",
            r"(x-1)^{3}=x^{3}-3x^{2}+3x-1",
        ],
        "options": [
            {
                "id": "structure",
                "text": (
                    "Los tres tienen cuatro términos, con el exponente del primero bajando "
                    "3, 2, 1, 0"
                ),
                "correct": True,
            },
            {
                "id": "coef",
                "text": "Los tres tienen los mismos coeficientes: 1, 3, 3, 1",
                "correct": False,
            },
            {
                "id": "signs",
                "text": "En los tres todos los signos son positivos",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Rayhana necesita un bloque de arista $x+2$ dedos. Con $x=2$, ¿cuánta arcilla lleva?"
        ),
        "polya": [
            "Entender: la arista es x + 2 y hay que hallar el volumen del cubo.",
            "Planear: o sustituyo primero y elevo al cubo, o uso el molde y sustituyo después.",
            "Ejecutar: 2 + 2 = 4, y 4³ = 64.",
            "Comprobar: por el molde, x³ + 6x² + 12x + 8 con x = 2 da 8 + 24 + 24 + 8 = 64 ✓.",
        ],
        "prompt": "¿Cuántos dedos de arcilla lleva el bloque?",
        "answer": "64",
        "hints": {
            "n1": "Primero calcula la arista con x = 2.",
            "n2": "La arista mide 4.",
            "n3": "4 · 4 · 4.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que conoces el molde.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya cuentas las capas antes de cerrar el registro.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo las capas "
            "intermedias antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuánto es 3³?",
                "answer": "27",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuántos términos tiene el desarrollo de $(x+4)^{3}$?",
                "options": [
                    {"id": "four", "text": "Cuatro"},
                    {"id": "two", "text": "Dos"},
                    {"id": "three", "text": "Tres"},
                ],
                "expected": "four",
                "misconception_by_option": {
                    "two": "binomio_cubo_falta_terminos",
                    "three": "usa_los_coeficientes_del_cuadrado_en_el_cubo",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "Calcula (3 + 1)³.",
                "answer": "64",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de pasar a la bandeja de parejas.",
            "consolidacion": "Resuelto con ayuda: el molde ya está, falta que salga solo.",
            "sin_ayuda": "Bloque macizo. Ninguna capa se te quedó fuera.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Las cuatro capas en su sitio.",
        "default": (
            "Cuenta las capas antes de cerrar: una suma al cubo deja cuatro términos, con "
            "coeficientes 1, 3, 3, 1."
        ),
        "fb_p03_e1_split": (
            "Ese es el error del nodo, y aquí cuesta el doble que en el cuadrado: faltan DOS "
            "capas. Con a = 3 y b = 1 tu respuesta da 28 y el bloque lleva 64."
        ),
        "fb_p03_e1_square": (
            "Mezclaste los dos moldes: el 2 del medio es del cuadrado. Al cubo los "
            "coeficientes son 1, 3, 3, 1 y hay cuatro términos, no tres."
        ),
        "fb_p03_e1_triple": (
            "Eso es triplicar, no elevar al cubo. Elevar al cubo es multiplicar por sí mismo "
            "tres veces."
        ),
        "fb_p03_e5_middle": (
            "Ese está bien: con el binomio restando, el segundo término resta. Mira el último."
        ),
        "fb_p03_e5_third": (
            "Ese está bien: los signos alternan, así que el tercero suma. Mira el último."
        ),
        "fb_p03_e5_none": (
            "Sí lo hay: (−2)³ = −8. Un cubo conserva el signo, a diferencia de un cuadrado."
        ),
        "fb_p03_e6_trap": (
            "Con un producto sí; con una suma no. (3 + 1)³ = 64, pero 3³ + 1³ = 28. Faltan "
            "las dos capas de en medio."
        ),
        "fb_p03_e6_one": (
            "Vas en la dirección correcta, pero al cubo se caen dos capas, no una: 3a²b y "
            "3ab². Por eso el desarrollo tiene cuatro términos."
        ),
        "fb_p03_e6_never": (
            "Te pasaste al otro lado. Sobre un producto sí se reparte: (2 · 3)³ = 216 y "
            "2³ · 3³ = 8 · 27 = 216. Lo que no admite reparto es la suma."
        ),
    },
    "closing": (
        "Ya tienes tres troqueles: la matriz que añade una orla, el cuño que se come el "
        "medio y el molde que apila cuatro capas. En la última mesa hay una bandeja donde "
        "los dos paréntesis se parecen pero no son ni iguales ni opuestos — y ahí vas a ver "
        "que los dos primeros troqueles eran casos particulares de uno solo."
    ),
    "validation_status": "F5_P03_11bloques",
}
