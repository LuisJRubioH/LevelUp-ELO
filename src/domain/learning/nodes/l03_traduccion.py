"""L03 · La mesa de dictado — el orden de las palabras no es el orden de los símbolos.

Tercera sala de la Casa de la Vida. Guía: Meritka. Vocabulario propio de la sala:
mesa de dictado, mensajero, encargo hablado, frase, voz, orden. Nada de cálamos
ni tinta (L01), ni de estantes ni varas patrón (L02).

Error focal: traducir palabra por palabra en el orden en que se oyen, que funciona
en la suma y revienta en la resta y en la división.
"""

NODE_ID = "ALG-N1-L03-TRADUCCION"
CONCEPT_SLUG = "traduccion"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "traduccion",
    "misconception": "traduce_en_el_orden_de_las_palabras",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La mesa de dictado · Traducción",
    "house": "La mesa de dictado",
    "guide": "Meritka",
    "finish_label": "Bajar a la cámara del recuento",
    "title": "El orden en que se oye no es el orden en que se escribe",
    "intro": (
        "Ya sabes qué símbolo cambia y cuál está fijado. Ahora los encargos llegan "
        "hablados: alguien dicta una frase y hay que dejarla en un registro corto. La "
        "trampa está en creer que se escribe en el mismo orden en que se oye."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de sentarte a la mesa. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Un mensajero dicta: «el doble de siete». ¿Qué número es?",
                "answer": "14",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "«Tres más que un número» se escribe…",
                "options": [
                    {"id": "plus", "text": r"$n+3$", "latex": r"n+3"},
                    {"id": "times", "text": r"$3n$", "latex": r"3n"},
                    {"id": "minus", "text": r"$n-3$", "latex": r"n-3"},
                ],
                "expected": "plus",
                "misconception_by_option": {
                    "times": "confunde_mas_con_veces",
                    "minus": "confunde_la_operacion_dictada",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Da lo mismo escribir 9 − 4 que 4 − 9?",
                "options": [
                    {"id": "no", "text": "No: la resta cambia si se invierte"},
                    {"id": "yes", "text": "Sí: son los mismos dos números"},
                    {"id": "sign", "text": "Sí, salvo por el signo, que da igual"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "resta_es_conmutativa",
                    "sign": "resta_es_conmutativa",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/l03-traduccion-katia.png",
        "eyebrow": "KatIA · En la mesa de dictado",
        "title": "Dos escribas, una frase, dos registros",
        "body": (
            "Llega un mensajero con prisa y dicta de corrido: «cinco menos que las cestas "
            "que traiga la barca».\n\n"
            "Los dos escribas de la mesa anotan a la vez. Meritka mira las dos tablillas y "
            "no dice cuál está bien. Dice otra cosa:\n\n"
            "«Uno de los dos escribió lo que oyó. El otro escribió lo que significa. Si la "
            "barca trae ocho cestas, sus dos registros no dan el mismo número, y solo uno "
            "de ellos sirve para pedir grano.»"
        ),
        "question": "¿Se escribe en el orden en que se dicta?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Sí: se anota palabra por palabra, según se oyen"},
                {"id": "b", "text": "Depende de la operación: unas admiten el cambio y otras no"},
                {"id": "c", "text": "No: siempre se escribe al revés de como se dicta"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder traducir «cinco menos que» sin "
                "dudar, y explicar por qué «cinco más que» sí se deja tal cual."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "La misma palabra, dos comportamientos",
        "body": "Dos encargos con la misma forma. Solo uno se puede anotar tal como suena.",
        "cases": [
            {
                "label": "Se deja igual",
                "context": "«Cinco más que las cestas»",
                "fraction": r"c+5",
                "division": r"c=8\Rightarrow 13",
                "note": "5 + c da lo mismo que c + 5. La suma no distingue el orden.",
            },
            {
                "label": "Hay que darle la vuelta",
                "context": "«Cinco menos que las cestas»",
                "fraction": r"c-5",
                "division": r"c=8\Rightarrow 3",
                "note": "Escrito como suena daría 5 − 8 = −3. La resta sí distingue el orden.",
            },
        ],
        "resolution": (
            "Traducir no es copiar el orden de las palabras: es decidir QUIÉN pone la "
            "cantidad y QUIÉN la quita. En la suma y en la multiplicación da igual el "
            "orden, así que la copia literal cuela. En la resta y en la división no, y ahí "
            "es donde el registro sale al revés."
        ),
    },
    "definition_title": "Traducir un encargo hablado",
    "definition_katex": r"\text{«cinco menos que }c\text{»}\;\longrightarrow\; c-5",
    "definition": (
        "TRADUCIR es pasar de una frase a una expresión con tres decisiones: qué cantidad "
        "no se conoce (le pones letra), qué operación pide la frase, y en qué orden entran "
        "los términos en esa operación. Las expresiones «más que» y «veces» no cambian con "
        "el orden; «menos que» y «entre» sí. Cuando la frase agrupa —«el doble de la suma "
        "de…»— hace falta un paréntesis."
    ),
    "definition_symbols": [
        {"symbol": r"c+5", "reads": "ce más cinco", "means": "«cinco más que c» · el orden da igual"},
        {"symbol": r"c-5", "reads": "ce menos cinco", "means": "«cinco menos que c» · c es quien pierde"},
        {"symbol": r"5-c", "reads": "cinco menos ce", "means": "«c menos que cinco» · otra frase distinta"},
        {"symbol": r"3c", "reads": "tres ce", "means": "«el triple de c» · el orden da igual"},
        {"symbol": r"\dfrac{c}{3}", "reads": "ce entre tres", "means": "«c repartido en tres» · el orden importa"},
        {"symbol": r"2(c+5)", "reads": "dos por, abre, ce más cinco", "means": "«el doble de la suma» · la frase agrupa"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · El encargo de la barca",
            "title": "Nombrar primero, operar después",
            "statement": (
                "Un mensajero dicta: «el doble de las cestas que traiga la barca, y tres "
                "más». Deja el encargo en un registro."
            ),
            "latex": r"2c+3",
            "image_slot": False,
            "steps": [
                "Lo que no se sabe todavía es cuántas cestas trae la barca: la llamo c.",
                "«El doble de las cestas» actúa sobre c y da 2c.",
                "«Y tres más» añade 3 a lo anterior: 2c + 3.",
                "Compruebo con un caso: si trae 6 cestas, el doble es 12 y tres más, 15.",
                "Sustituyo: 2 · 6 + 3 = 15. Coinciden, así que el registro dice lo mismo que la voz.",
            ],
            "solution": r"$2c+3$",
            "self_explanation": {
                "step_index": 1,
                "prompt": "¿Por qué el 2 se escribe pegado a la c y el 3 no?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · La frase que agrupa",
            "title": "Cuando hace falta un paréntesis",
            "statement": (
                "Otro encargo: «el doble de lo que sumen las cestas y las tres jarras». "
                "¿Es 2c + 3?"
            ),
            "latex": r"2(c+3)",
            "image_slot": False,
            "steps": [
                "La frase dice «el doble de lo que SUMEN»: primero se suma, después se dobla.",
                "Lo que suman es c + 3.",
                "El doble de eso es 2(c + 3). El paréntesis marca qué se dobla.",
                "Con c = 6: la frase da (6 + 3) · 2 = 18, y 2c + 3 daría 15.",
                "No son la misma expresión. El paréntesis no es adorno: cambia el resultado.",
            ],
            "solution": r"$2(c+3)$, no $2c+3$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que anotó lo que oyó",
            "statement": (
                "Vuelve el encargo del principio: «cinco menos que las cestas». Un escriba "
                "anota 5 − c, porque el cinco se dijo primero."
            ),
            "latex": r"c-5",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\text{«cinco menos que }c\text{»}\to 5-c",
            "error_note": (
                "Copió el orden de la voz. Con 8 cestas su registro da −3, y no existe una "
                "barca que descargue menos tres cestas."
            ),
            "correct_version": {
                "wrong_latex": r"5-c",
                "right_latex": r"c-5",
                "rows": [
                    {"wrong": "El cinco se dijo primero, luego va primero",
                     "right": "«Menos que c» significa que a c se le quitan cinco"},
                    {"wrong": r"c=8\Rightarrow 5-8=-3",
                     "right": r"c=8\Rightarrow 8-5=3"},
                ],
            },
            "explain_prompt": (
                "Explica por qué con «cinco MÁS que las cestas» el orden literal sí habría "
                "funcionado, y con «menos que» no."
            ),
            "steps": [
                "Pruebo la frase con un caso claro: si hay 8 cestas y son cinco menos, quedan 3.",
                "Mi registro tiene que dar 3 con c = 8. El de 5 − c da −3: descartado.",
                "Regla para no volver a caer: escribe primero la cantidad de la que se habla, y después qué le pasa.",
            ],
            "solution": (
                "«Cinco menos que c» es c − 5. La suma perdona el orden literal; la resta lo "
                "cobra, porque 5 − c y c − 5 no son el mismo número."
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
                "statement": "«Cuatro menos que las jarras». Si hay 11 jarras, ¿cuántas quedan?",
                "given_steps": [r"j-4", r"j=11"],
                "blanks": [{"id": "P1-b1", "label": r"11-4=", "answer": "7"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "«El triple de las cestas, y dos más». Escribe el coeficiente y evalúa con c = 5.",
                "given_steps": [r"3c+2"],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{coeficiente}=", "answer": "3"},
                    {"id": "P2-b2", "label": r"3\cdot 5+2=", "answer": "17"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: «el doble de la suma de las jarras y 4». "
                    "¿Cuánto vale si hay 6 jarras?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"2(j+4)=", "answer": "20"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de traducir un encargo",
        "intro": r"«Siete menos que el triple de las cestas». ¿Cómo se llega al registro?",
        "methods": [
            {
                "label": "Método 1 · Trocear la frase en orden",
                "steps": [
                    r"\text{«siete menos»}\to 7-",
                    r"\text{«el triple de las cestas»}\to 3c",
                    r"7-3c",
                ],
                "note": "Rápido de escribir, y aquí ha producido un registro equivocado.",
            },
            {
                "label": "Método 2 · Nombrar primero la cantidad",
                "steps": [
                    r"\text{la cantidad de la que se habla}\to c",
                    r"\text{lo que se le hace primero: el triple}\to 3c",
                    r"\text{lo que se le quita después}\to 3c-7",
                ],
                "note": "Un paso más largo, pero coloca cada término en su sitio.",
            },
        ],
        "question": "Con 4 cestas, ¿qué da cada registro, y cuál coincide con la frase?",
        "insight": (
            "El triple de 4 son 12, y siete menos son 5. El método 2 da 3·4 − 7 = 5 ✓; el "
            "método 1 da 7 − 12 = −5 ✗. Trocear en orden solo es fiable cuando todas las "
            "operaciones de la frase son sumas o productos; en cuanto aparece un «menos "
            "que» o un «entre», hay que nombrar primero la cantidad y construir alrededor."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "«Seis menos que el número de remeros». ¿Qué registro lo dice?",
            "options": [
                {"id": "rminus", "text": r"$r-6$", "latex": r"r-6"},
                {"id": "minusr", "text": r"$6-r$", "latex": r"6-r"},
                {"id": "rplus", "text": r"$r+6$", "latex": r"r+6"},
                {"id": "sixr", "text": r"$6r$", "latex": r"6r"},
            ],
            "expected": "rminus",
            "feedback_by_option": {
                "rminus": "correct",
                "minusr": "fb_l03_e1_order",
                "rplus": "fb_l03_e1_op",
                "sixr": "fb_l03_e1_times",
            },
            "misconception_by_option": {
                "minusr": "traduce_en_el_orden_de_las_palabras",
                "rplus": "confunde_la_operacion_dictada",
                "sixr": "confunde_mas_con_veces",
            },
            "hints": {
                "n1": "¿A quién se le quitan seis: a los remeros o al seis?",
                "n2": "Prueba con 10 remeros: seis menos son 4.",
                "n3": "Busca el registro que dé 4 cuando r = 10.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                "Escribe el registro de «el triple de las jarras, más dos». Usa j para las "
                "jarras y no dejes espacios."
            ),
            "answer": "3j+2",
            "accepted": ["2+3j"],
            "hints": {
                "n1": "«El triple de j» se escribe pegando el 3 a la j.",
                "n2": "«Más dos» añade un término suelto.",
                "n3": "Queda un producto y una suma: 3j y luego +2.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "«El doble de la suma de las cestas y cinco». ¿Cuál es?",
            "options": [
                {"id": "paren", "text": r"$2(c+5)$", "latex": r"2(c+5)"},
                {"id": "flat", "text": r"$2c+5$", "latex": r"2c+5"},
                {"id": "both", "text": r"$2c+10$… solo si se reparte después", "latex": r"2c+10"},
                {"id": "swap", "text": r"$c+10$", "latex": r"c+10"},
            ],
            "expected": "paren",
            "feedback_by_option": {
                "paren": "correct",
                "flat": "fb_l03_e3_flat",
                "both": "fb_l03_e3_both",
                "swap": "fb_l03_e3_swap",
            },
            "misconception_by_option": {
                "flat": "ignora_la_agrupacion_de_la_frase",
                "both": "confunde_forma_con_traduccion",
                "swap": "confunde_la_operacion_dictada",
            },
            "hints": {
                "n1": "¿Qué se dobla: solo las cestas, o la suma entera?",
                "n2": "Prueba con c = 3: la frase da (3 + 5) · 2 = 16.",
                "n3": "2c + 5 daría 11. Hace falta marcar qué se dobla.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un escriba traduce «las jarras repartidas entre cuatro» como 4/j. "
                "¿Dónde está el error?"
            ),
            "options": [
                {"id": "order", "text": "Invirtió el orden: lo que se reparte va arriba, j/4"},
                {"id": "op", "text": "No es división, es resta"},
                {"id": "letter", "text": "No debió usar letra para las jarras"},
                {"id": "none", "text": "No hay error: da lo mismo"},
            ],
            "expected": "order",
            "feedback_by_option": {
                "order": "correct",
                "op": "fb_l03_e4_op",
                "letter": "fb_l03_e4_letter",
                "none": "fb_l03_e4_none",
            },
            "misconception_by_option": {
                "op": "confunde_la_operacion_dictada",
                "letter": "toda_letra_es_variable",
                "none": "traduce_en_el_orden_de_las_palabras",
            },
            "hints": {
                "n1": "Con 12 jarras entre cuatro, tocan a 3 por parte.",
                "n2": "4/12 no es 3.",
                "n3": "Lo que se reparte va en el numerador.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Una frase se traduce escribiendo los símbolos en el "
                "mismo orden en que se oyen las palabras.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: «cinco menos que c» se oye 5 primero y se escribe c − 5"},
                {"id": "true", "text": "Verdadera: para eso se dicta despacio"},
                {"id": "true_short", "text": "Verdadera si la frase es corta"},
                {"id": "false_always", "text": "Falsa: nunca coincide el orden"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_l03_e5_trap",
                "true_short": "fb_l03_e5_short",
                "false_always": "fb_l03_e5_never",
            },
            "misconception_by_option": {
                "true": "traduce_en_el_orden_de_las_palabras",
                "true_short": "traduce_en_el_orden_de_las_palabras",
                "false_always": "sobregeneraliza_traduccion",
            },
            "hints": {
                "n1": "Para tumbar un «siempre» basta un contraejemplo.",
                "n2": "Piensa en una resta dictada al revés.",
                "n3": "«Cinco menos que las cestas» no se escribe 5 − c.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (
                "Selecciona TODAS las frases que se pueden anotar en el mismo orden en que "
                "se oyen, sin darles la vuelta."
            ),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": "«Cuatro más que las cestas»"},
                {"id": "b", "text": "«Cuatro menos que las cestas»"},
                {"id": "c", "text": "«Cuatro veces las cestas»"},
                {"id": "d", "text": "«Cuatro repartido entre las cestas»"},
            ],
            "expected": ["a", "c", "d"],
            "trap_options": ["b"],
            "hints": {
                "n1": "Pregúntate si esa operación cambia al invertir el orden.",
                "n2": "La suma y el producto no cambian; la resta sí.",
                "n3": "En «cuatro repartido entre las cestas» el cuatro sí es el que se reparte.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "«El doble de los remeros, menos siete». Si la barca lleva 9 remeros, "
                "¿cuánto vale el registro?"
            ),
            "expr": r"2r-7,\quad r=9",
            "answer": "11",
            "hints": {
                "n1": "Primero el doble, después la resta.",
                "n2": "El doble de 9 es 18.",
                "n3": "18 − 7 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se puede escribir tal como suena?",
        "title": "Qué frases perdonan el orden literal y cuáles no",
        "intro": (
            "La copia literal no es siempre un error: hay operaciones a las que el orden "
            "les da igual. El problema es no saber cuáles."
        ),
        "rows": [
            {"symbol": r"c+4", "name": "«Cuatro más que c»", "closed": "yes",
             "latex": r"4+c=c+4",
             "note": "La suma no distingue el orden: escribirlo como suena da lo mismo."},
            {"symbol": r"4c", "name": "«Cuatro veces c»", "closed": "yes",
             "latex": r"4\cdot c=c\cdot 4",
             "note": "El producto tampoco lo distingue. Otro caso en que la copia cuela."},
            {"symbol": r"c-4", "name": "«Cuatro menos que c»", "closed": "no",
             "latex": r"4-c\neq c-4",
             "note": "Aquí se rompe: hay que poner primero a quien pierde. Es el caso focal."},
            {"symbol": r"\dfrac{c}{4}", "name": "«c repartido entre cuatro»", "closed": "no",
             "latex": r"\dfrac{4}{c}\neq\dfrac{c}{4}",
             "note": "Igual que la resta: lo que se reparte va arriba, se diga cuando se diga."},
            {"symbol": r"2(c+4)", "name": "«El doble de la suma de c y cuatro»", "closed": "no",
             "latex": r"2(c+4)\neq 2c+4",
             "note": "No falla el orden sino la agrupación: la frase manda hacer la suma primero."},
            {"symbol": r"c-4\ \text{vs}\ 4-c", "name": "«c menos que cuatro»", "closed": "partial",
             "latex": r"4-c",
             "note": "Cambiando dos palabras la frase cambia de bando: ahora sí es 4 − c. El orden literal acierta por casualidad."},
        ],
        "outro": (
            "La última fila avisa de lo peor que puede pasar: acertar por el motivo "
            "equivocado. Si traduces copiando el orden, a veces te sale bien, y eso "
            "refuerza el hábito que va a fallarte a la siguiente. Nombra la cantidad "
            "primero y construye alrededor: entonces aciertas siempre por el mismo motivo."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres encargos trabajados en este nodo?",
        "thumbnails": [r"2c+3", r"2(c+3)", r"c-5"],
        "options": [
            {"id": "name_first", "text": "En los tres conviene nombrar la cantidad desconocida antes de operar", "correct": True},
            {"id": "order_matters", "text": "En los tres el orden o la agrupación cambia el resultado si se descuida", "correct": True},
            {"id": "literal", "text": "En los tres basta con escribir los símbolos según se oyen", "correct": False},
            {"id": "no_paren", "text": "En los tres los paréntesis se pueden quitar sin consecuencias", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Último encargo de la jornada: «el doble de las cestas que traiga la barca, "
            "menos las cuatro que se quedan en el puerto». Hoy la barca trae 15 cestas. "
            "¿Cuántas llegan a la Casa de la Vida?"
        ),
        "polya": {
            "comprender": "Hay una cantidad que cambia (las cestas de la barca) y una pérdida fija de cuatro.",
            "planear": "Nombro primero: c son las cestas. El doble es 2c, y después se quitan 4: 2c − 4.",
            "ejecutar": "Con c = 15: 2 · 15 − 4 = 30 − 4 = 26.",
            "comprobar": "Al revés: 26 + 4 = 30, que es el doble de 15 ✓. Y no escribí 4 − 2c, que habría dado −26.",
        },
        "prompt": "¿Cuántas cestas llegan?",
        "answer": "26",
        "hints": {
            "n1": "Nombra las cestas de la barca con una letra antes de operar.",
            "n2": "El doble primero, la resta después: 2c − 4.",
            "n3": "30 − 4 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros encargos. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya colocas la cantidad antes de decidir qué se le hace.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el «menos que», "
            "que es el que tumba la traducción literal."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Un mensajero dicta: «el triple de seis». ¿Qué número es?",
                "answer": "18",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "«Dos menos que las jarras» se escribe…",
                "options": [
                    {"id": "jminus", "text": r"$j-2$", "latex": r"j-2"},
                    {"id": "minusj", "text": r"$2-j$", "latex": r"2-j"},
                    {"id": "twoj", "text": r"$2j$", "latex": r"2j"},
                ],
                "expected": "jminus",
                "misconception_by_option": {
                    "minusj": "traduce_en_el_orden_de_las_palabras",
                    "twoj": "confunde_mas_con_veces",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿En cuál de estas frases el orden literal NO importa?",
                "options": [
                    {"id": "sum", "text": "«Tres más que las cestas»"},
                    {"id": "sub", "text": "«Tres menos que las cestas»"},
                    {"id": "div", "text": "«Las cestas repartidas entre tres»"},
                ],
                "expected": "sum",
                "misconception_by_option": {
                    "sub": "traduce_en_el_orden_de_las_palabras",
                    "div": "traduce_en_el_orden_de_las_palabras",
                },
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
        "default": "Nombra primero la cantidad de la que habla la frase, y después decide qué se le hace.",
        "fb_l03_e1_order": (
            "Ese es el orden en que se oye, no el que significa. → Con 10 remeros, seis "
            "menos son 4, y 6 − 10 da −4."
        ),
        "fb_l03_e1_op": "«Menos que» quita, no añade. → La operación es una resta.",
        "fb_l03_e1_times": "«Menos que» no multiplica. → 6r sería «seis veces los remeros».",
        "fb_l03_e3_flat": (
            "Así solo se dobla la c. → La frase dice «el doble de la SUMA»: primero se suma."
        ),
        "fb_l03_e3_both": (
            "2c + 10 es el resultado de repartir el 2, no la traducción de la frase. → Se "
            "pide el registro que dice lo mismo que la voz."
        ),
        "fb_l03_e3_swap": "Ahí se perdió el doble. → Prueba con c = 3 y compara con la frase.",
        "fb_l03_e4_op": "«Repartidas entre» sí es una división. → Lo que falla es quién va arriba.",
        "fb_l03_e4_letter": "Usar letra está bien: las jarras son la cantidad que cambia. → Mira el orden.",
        "fb_l03_e4_none": (
            "4/j y j/4 no dan lo mismo. → Con 12 jarras, una da 3 y la otra un tercio."
        ),
        "fb_l03_e5_trap": (
            "Dictar despacio no cambia el significado. → «Cinco menos que c» se oye con el "
            "5 delante y se escribe con la c delante."
        ),
        "fb_l03_e5_short": (
            "La longitud no tiene nada que ver. → «Dos menos que j» es cortísima y también "
            "hay que darle la vuelta."
        ),
        "fb_l03_e5_never": (
            "Te pasaste al otro extremo: en «tres más que c» el orden literal funciona. → "
            "Depende de la operación."
        ),
    },
    "closing": (
        "Ya puedes convertir una voz en un registro sin que se te dé la vuelta. Falta el "
        "camino contrario: tener el registro y sacar el número. Eso se hace abajo, en la "
        "cámara del recuento."
    ),
    "validation_status": "F5_L03_11bloques",
}
