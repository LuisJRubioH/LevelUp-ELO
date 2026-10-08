"""M03 · Distributiva — un factor se reparte sobre una suma, no sobre un producto.

Estación del nodo: LA CINTA REPARTIDORA (engranajes que bajan por una cinta y se
reparten en cajas). Ninguna otra estación usa este material.
"""

NODE_ID = "PREALG-N3-M03-DISTRIBUTIVA"
CONCEPT_SLUG = "distributiva"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "distributiva",
    "misconception": "distribuye_sobre_el_producto",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La Cinta Repartidora · Distributiva",
    "station": "La Cinta Repartidora",
    "finish_label": "Salir hacia el Calibre Cero",
    "title": "Se reparte sobre la suma, no sobre el producto",
    "intro": (
        "Las dos estaciones anteriores trabajaban con UNA operación a la vez. Aquí se "
        "mezclan dos: un factor por fuera y una suma por dentro. Vas a ver por qué el "
        "factor entra a cada sumando, y por qué el mismo movimiento con un producto por "
        "dentro multiplica de más."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de encender la cinta. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $3\times(4+2)$?",
                "answer": "18",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es igual a $5\times(7+3)$?",
                "options": [
                    {"id": "ok", "text": "5 × 7 + 5 × 3", "latex": r"5\times 7+5\times 3"},
                    {"id": "partial", "text": "5 × 7 + 3", "latex": r"5\times 7+3"},
                    {
                        "id": "double",
                        "text": "(5 × 7) × (5 × 3)",
                        "latex": r"(5\times 7)\times(5\times 3)",
                    },
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "partial": "distribuye_solo_al_primer_sumando",
                    "double": "distribuye_sobre_el_producto",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $2\times(3\times 5)$?",
                "answer": "30",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En la Cinta Repartidora",
        "title": "La caja que llegó llena de más",
        "body": (
            "La tercera estación es una cinta larga con un brazo repartidor: los engranajes "
            "bajan por la cinta y el brazo los va soltando en las cajas que haya al final. "
            "Si hay dos cajas, el brazo reparte a las dos; si hay tres, a las tres.\n\n"
            "El encargado escribió el pedido así: «triple de lo que hay en las dos cajas». "
            "El brazo trabajó bien. Después escribió otro pedido igual de corto — «triple de "
            "una caja de cuatro filas de dos» — y el brazo triplicó la fila Y triplicó la "
            "columna. Salieron nueve veces los engranajes pedidos."
        ),
        "question": "¿Un factor que entra en un paréntesis se reparte a todo lo que hay dentro?",
        "image": "/leccion/03-prealg-n3-fabrica/m03-distributiva-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Sí: entra a todo lo que haya dentro"},
                {"id": "b", "text": "Solo si dentro hay una suma"},
                {"id": "c", "text": "Nunca: hay que calcular el paréntesis primero"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir exactamente "
                "cuándo el factor se reparte y cuándo entra una sola vez."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo factor, dos paréntesis distintos",
        "body": ("Abajo, el mismo 3 por fuera. Lo único que cambia es la operación de dentro."),
        "cases": [
            {
                "label": "Caso que funciona",
                "context": "Triple de lo que hay en dos cajas, una con 4 y otra con 2",
                "fraction": r"3\times(4+2)",
                "division": r"3\times 4+3\times 2=12+6=18",
                "note": "El 3 entra a cada caja. Y 3 × 6 = 18: coincide.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Triple de una caja de 4 filas de 2 engranajes",
                "fraction": r"3\times(4\times 2)",
                "division": r"3\times 4\times 3\times 2=72\quad\text{pero }3\times 8=24",
                "note": "Repartir el 3 aquí multiplica de más: 72 en vez de 24.",
            },
        ],
        "resolution": (
            "En la suma hay DOS montones distintos y el triple se le aplica a cada uno. En "
            "el producto hay UN solo montón descrito de dos maneras — filas y columnas — y "
            "triplicar las dos cosas triplica dos veces. El factor entra una sola vez, "
            "donde tú elijas."
        ),
    },
    "definition_title": "La propiedad distributiva",
    "definition_katex": r"a\times(b+c)=a\times b+a\times c",
    "definition": (
        "Multiplicar por una suma es lo mismo que multiplicar por cada sumando y después "
        "sumar. Es la única propiedad que conecta dos operaciones distintas, y es la base "
        "de todo lo que viene en álgebra."
    ),
    "definition_symbols": [
        {
            "symbol": r"a",
            "reads": "el factor que se reparte",
            "means": "el brazo repartidor: llega a cada caja",
        },
        {
            "symbol": r"b+c",
            "reads": "la suma de dentro",
            "means": "las cajas distintas que hay al final de la cinta",
        },
        {
            "symbol": r"a\times b+a\times c",
            "reads": "forma desarrollada",
            "means": "el factor ya repartido",
        },
        {
            "symbol": r"a\times(b\times c)\neq (a\times b)\times(a\times c)",
            "reads": "no se reparte sobre el producto",
            "means": "un solo montón: el factor entra una vez",
        },
        {
            "symbol": r"a\times(b-c)=a\times b-a\times c",
            "reads": "también sobre la resta",
            "means": "la resta es una suma con signo, así que sí vale",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Sobre una suma",
            "title": "El pedido que el brazo hizo bien",
            "statement": (
                "El encargo pide 7 veces el contenido de dos cajas: una con 30 engranajes y "
                "otra con 4. ¿Cuántos engranajes salen?"
            ),
            "latex": r"7\times(30+4)",
            "image_slot": False,
            "steps": [
                "Camino directo: 30 + 4 = 34, y 7 × 34. Cuesta de cabeza.",
                "Camino repartido: el 7 entra a cada caja. 7 × 30 = 210 y 7 × 4 = 28.",
                "Sumo lo que salió de cada caja: 210 + 28 = 238.",
                "Compruebo con el camino directo: 7 × 34 = 238. Coinciden.",
                "Repartir no cambió el resultado; convirtió una multiplicación difícil en dos fáciles.",
            ],
            "solution": r"$7\times(30+4)=210+28=238$",
            "self_explanation": {
                "step_index": 1,
                "prompt": "En el paso 2 el 7 entra a las DOS cajas. ¿Qué pasaría si solo entrara a la primera?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Sobre una resta",
            "title": "Repartir hacia atrás",
            "statement": (
                "El encargo pide 8 veces lo que queda en una caja de 50 engranajes después "
                "de retirar 3. ¿Cuántos salen?"
            ),
            "latex": r"8\times(50-3)",
            "image_slot": False,
            "steps": [
                "La resta es una suma con signo: 50 − 3 = 50 + (−3).",
                "Así que el 8 también se reparte: 8 × 50 + 8 × (−3).",
                "8 × 50 = 400 y 8 × (−3) = −24.",
                "400 − 24 = 376.",
                "Compruebo: 50 − 3 = 47, y 8 × 47 = 376. Coinciden.",
            ],
            "solution": r"$8\times(50-3)=400-24=376$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El brazo que repartió sobre un producto",
            "statement": (
                "El encargado anota: «Pedido: 3 veces una caja de 4 filas de 2. Reparto el 3 "
                "como siempre: 3 × 4 por 3 × 2, o sea 12 × 6 = 72 engranajes»."
            ),
            "latex": r"3\times(4\times 2)=(3\times 4)\times(3\times 2)",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"(3\times 4)\;\underline{\times}\;(3\times 2)",
            "error_note": "Metió el 3 dos veces: una en las filas y otra en las columnas. El pedido se triplicó dos veces.",
            "correct_version": {
                "wrong_latex": r"3\times(4\times 2)=72",
                "right_latex": r"3\times(4\times 2)=3\times 8=24",
                "rows": [
                    {
                        "wrong": "El factor se reparte a todo lo que haya en el paréntesis",
                        "right": "Solo se reparte sobre sumas y restas, no sobre productos",
                    },
                    {
                        "wrong": "4 filas de 2 son dos montones distintos",
                        "right": "Son UN montón de 8, descrito por filas y columnas",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 72 es imposible? Escribe la cuenta correcta.",
            "steps": [
                "Cuenta lo que hay realmente: 4 filas de 2 son 8 engranajes en total.",
                "El triple de 8 es 24, no 72. 72 es el triple del triple.",
                "Repartir el 3 sobre un producto lo aplica dos veces: 3 × 3 = 9, y 9 × 8 = 72.",
            ],
            "solution": (
                "La pregunta antes de repartir es: ¿lo de dentro son montones DISTINTOS que "
                "se juntan, o un mismo montón descrito de dos formas? Si se juntan, reparte. "
                "Si es el mismo, el factor entra una sola vez."
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
                "statement": "El encargo pide 6 veces dos cajas, una con 20 y otra con 5.",
                "given_steps": [
                    r"6\times(20+5)=6\times 20+6\times 5",
                    r"6\times 20=120,\quad 6\times 5=30",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"120+30=", "answer": "150"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "El encargo pide 9 veces lo que queda de una caja de 40 tras retirar 2.",
                "given_steps": [
                    r"9\times(40-2)=9\times 40-9\times 2",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"9\times 40=", "answer": "360"},
                    {"id": "P2-b2", "label": r"360-18=", "answer": "342"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: el encargo pide 5 veces una caja de 6 filas de 3 "
                    "engranajes. Da el total, sin repartir el 5."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"5\times(6\times 3)=", "answer": "90"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para el mismo pedido",
        "intro": r"¿Cuánto vale $4\times 98$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar directo",
                "steps": [r"4\times 98", r"\text{llevando la que va}", r"=392"],
                "note": "Funciona siempre, pero pide papel.",
            },
            {
                "label": "Método 2 · Repartir sobre una resta",
                "steps": [r"4\times(100-2)", r"=400-8", r"=392"],
                "note": "Convierte el 98 en algo cómodo y reparte.",
            },
        ],
        "question": "¿Cuál harías de cabeza con 4 × 97? ¿Y qué tuviste que inventar en el método 2 que no estaba en el enunciado?",
        "insight": (
            "El método 2 no simplifica una cuenta que ya existía: REESCRIBE el 98 como "
            "100 − 2 para poder repartir. Esa reescritura es el motor de casi toda el "
            "álgebra que viene — sacar factor común, desarrollar un producto notable, "
            "factorizar — y todas son la distributiva leída en un sentido o en el otro."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El encargo pide 5 veces dos cajas, una con 12 y otra con 8. ¿Cuántos engranajes salen?",
            "expr": r"5\times(12+8)",
            "answer": "100",
            "hints": {
                "n1": "El 5 entra a cada caja.",
                "n2": "5 × 12 = 60 y 5 × 8 = 40.",
                "n3": "60 + 40 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Calcula 6 × 99 repartiendo sobre una resta cómoda.",
            "expr": r"6\times(100-1)",
            "answer": "594",
            "hints": {
                "n1": "Reescribe 99 como 100 menos algo.",
                "n2": "6 × 100 = 600.",
                "n3": "600 − 6 = …",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El encargo pide 4 veces una caja de 7 filas de 3 engranajes. ¿Cuántos salen?",
            "expr": r"4\times(7\times 3)",
            "answer": "84",
            "hints": {
                "n1": "Primero cuenta lo que hay en la caja.",
                "n2": "7 × 3 = 21 engranajes.",
                "n3": "4 × 21 = …  (no repartas el 4)",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"Un encargado anota «$6\times(10+4)=6\times 10+4=64$». ¿Dónde está el error?",
            "options": [
                {
                    "id": "half",
                    "text": "Repartió solo al primer sumando; falta multiplicar el 4 por 6",
                },
                {
                    "id": "product",
                    "text": "Debía multiplicar los dos resultados en vez de sumarlos",
                },
                {"id": "arith", "text": "Se equivocó en 6 × 10"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "half",
            "feedback_by_option": {
                "half": "correct",
                "product": "fb_m03_e4_product",
                "arith": "fb_m03_e4_arith",
                "none": "fb_m03_e4_none",
            },
            "misconception_by_option": {
                "product": "distribuye_sobre_el_producto",
                "arith": "habito_error_de_calculo_no_de_metodo",
                "none": "distribuye_solo_al_primer_sumando",
            },
            "hints": {
                "n1": "Calcula el paréntesis primero y compara: 6 × 14.",
                "n2": "6 × 14 = 84, no 64.",
                "n3": "Faltan 20, que es exactamente 6 × 4 − 4.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para cualesquiera $a,b,c$: $a\times(b\times c)=(a\times b)\times(a\times c)$.»",
            "options": [
                {
                    "id": "false_product",
                    "text": "Falsa: sobre un producto el factor entra una sola vez",
                },
                {"id": "true", "text": "Verdadera: el factor se reparte a todo el paréntesis"},
                {"id": "false_never", "text": "Falsa: nunca pueden coincidir"},
                {"id": "true_small", "text": "Verdadera si los números son pequeños"},
            ],
            "expected": "false_product",
            "feedback_by_option": {
                "false_product": "correct",
                "true": "fb_m03_e5_trap",
                "false_never": "fb_m03_e5_never",
                "true_small": "fb_m03_e5_small",
            },
            "misconception_by_option": {
                "true": "distribuye_sobre_el_producto",
                "false_never": "olvida_el_caso_neutro",
                "true_small": "distribuye_sobre_el_producto",
            },
            "hints": {
                "n1": "Para tumbar un «cualesquiera» basta UN caso.",
                "n2": "Prueba con a = 3, b = 4, c = 2.",
                "n3": "3 × 8 = 24 pero 12 × 6 = 72. ¿Y si a fuera 1?",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("Calcula 7 × 103 reescribiendo el 103 de forma cómoda."),
            "expr": r"7\times(100+3)",
            "answer": "721",
            "hints": {
                "n1": "103 = 100 + 3.",
                "n2": "7 × 100 = 700 y 7 × 3 = 21.",
                "n3": "700 + 21 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": r"¿Cuál de estas expresiones es igual a $9\times 15+9\times 5$?",
            "options": [
                {"id": "common", "text": "9 × (15 + 5)", "latex": r"9\times(15+5)"},
                {"id": "sum_all", "text": "9 + 15 + 5", "latex": r"9+15+5"},
                {
                    "id": "double_factor",
                    "text": "(9 + 9) × (15 + 5)",
                    "latex": r"(9+9)\times(15+5)",
                },
                {"id": "product", "text": "9 × 15 × 5", "latex": r"9\times 15\times 5"},
            ],
            "expected": "common",
            "feedback_by_option": {
                "common": "correct",
                "sum_all": "fb_m03_e7_sum",
                "double_factor": "fb_m03_e7_double",
                "product": "fb_m03_e7_product",
            },
            "misconception_by_option": {
                "sum_all": "confunde_factor_comun_con_suma",
                "double_factor": "duplica_el_factor_comun",
                "product": "confunde_suma_con_producto",
            },
            "hints": {
                "n1": "Es la distributiva leída al revés: el 9 se repite en los dos términos.",
                "n2": "Saca el 9 fuera y deja lo demás dentro.",
                "n3": "9 × 15 + 9 × 5 = 135 + 45 = 180. Comprueba cuál de las cuatro da 180.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Sobre qué se puede repartir un factor",
        "title": "¿El factor de fuera entra a cada término de dentro?",
        "intro": "Esta propiedad no habla de una operación sino de un PAR: la de fuera y la de dentro.",
        "rows": [
            {
                "symbol": r"\times\ \text{sobre}\ +",
                "name": "Producto sobre suma",
                "closed": "yes",
                "latex": r"3\times(4+2)=3\times 4+3\times 2",
                "note": "El caso central. Dos montones distintos, el factor llega a los dos.",
            },
            {
                "symbol": r"\times\ \text{sobre}\ -",
                "name": "Producto sobre resta",
                "closed": "yes",
                "latex": r"8\times(50-3)=8\times 50-8\times 3",
                "note": "También vale: la resta es una suma con signo.",
            },
            {
                "symbol": r"\times\ \text{sobre}\ \times",
                "name": "Producto sobre producto",
                "closed": "no",
                "latex": r"3\times(4\times 2)\neq(3\times 4)\times(3\times 2)",
                "note": "Un solo montón: repartir aplicaría el factor dos veces. Esta es la trampa del nodo.",
            },
            {
                "symbol": r"\div\ \text{sobre}\ +",
                "name": "División sobre suma",
                "closed": "partial",
                "latex": r"\dfrac{a+b}{c}=\dfrac{a}{c}+\dfrac{b}{c}\quad\text{pero}\quad \dfrac{c}{a+b}\neq\dfrac{c}{a}+\dfrac{c}{b}",
                "note": "Solo si la suma está ARRIBA. Repartir un denominador es de los errores más caros del álgebra.",
            },
            {
                "symbol": r"a^{n}\ \text{sobre}\ \times",
                "name": "Potencia sobre producto",
                "closed": "yes",
                "latex": r"(a\times b)^{n}=a^{n}\times b^{n}",
                "note": "El exponente sí se reparte sobre un producto — justo al revés que el factor.",
            },
            {
                "symbol": r"a^{n}\ \text{sobre}\ +",
                "name": "Potencia sobre suma",
                "closed": "no",
                "latex": r"(3+4)^{2}=49\neq 25=3^{2}+4^{2}",
                "note": "Y aquí se invierte del todo: sobre una suma NO se reparte. Es el mismo error que la raíz en la Cantera (E06).",
            },
        ],
        "outro": (
            "Fíjate en la simetría: el factor se reparte sobre sumas y no sobre productos; "
            "el exponente sobre productos y no sobre sumas. Nunca «se reparte todo sobre "
            "todo». En el Calibre Cero vas a buscar los números que no cambian nada."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"7\times(30+4)", r"8\times(50-3)", r"3\times(4\times 2)"],
        "options": [
            {
                "id": "two_ops",
                "text": "En los tres se mezclan dos operaciones distintas",
                "correct": True,
            },
            {
                "id": "always",
                "text": "En los tres el factor de fuera entra a cada término",
                "correct": False,
            },
            {
                "id": "inside",
                "text": "En los tres hay que mirar qué operación hay DENTRO del paréntesis",
                "correct": True,
            },
            {
                "id": "easier",
                "text": "En los tres repartir hace la cuenta más fácil",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El encargo final de la cinta: 12 veces el contenido de dos cajas, una con 25 "
            "engranajes y otra con 5. ¿Cuántos engranajes salen?"
        ),
        "polya": {
            "comprender": "Un factor 12 por fuera y una suma de 25 + 5 por dentro. Piden el total.",
            "planear": "Dentro hay una SUMA, así que puedo repartir el 12 a cada caja.",
            "ejecutar": "12 × 25 = 300 y 12 × 5 = 60 → 300 + 60 = 360.",
            "comprobar": "Camino directo: 25 + 5 = 30, y 12 × 30 = 360. Coincide.",
        },
        "prompt": "¿Cuántos engranajes salen?",
        "answer": "360",
        "hints": {
            "n1": "Dentro hay una suma: el 12 se puede repartir.",
            "n2": "12 × 25 = 300.",
            "n3": "12 × 5 = 60, y 300 + 60 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya miras qué operación hay dentro antes de repartir.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el factor "
            "entra una sola vez cuando dentro hay un producto."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $4\times(5+3)$?",
                "answer": "32",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es igual a $6\times(9+2)$?",
                "options": [
                    {"id": "ok", "text": "6 × 9 + 6 × 2", "latex": r"6\times 9+6\times 2"},
                    {"id": "partial", "text": "6 × 9 + 2", "latex": r"6\times 9+2"},
                    {
                        "id": "double",
                        "text": "(6 × 9) × (6 × 2)",
                        "latex": r"(6\times 9)\times(6\times 2)",
                    },
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "partial": "distribuye_solo_al_primer_sumando",
                    "double": "distribuye_sobre_el_producto",
                },
            },
            {
                "id": "PD3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $5\times(2\times 4)$?",
                "answer": "40",
                # El mismo tipo de ítem que D3: aquí NO se reparte. Comprueba que
                # aprendió el criterio y no "reparto siempre que veo paréntesis".
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
        "default": "Mira qué operación hay DENTRO del paréntesis antes de decidir si repartes.",
        "fb_m03_e4_product": (
            "Multiplicar los dos resultados aplicaría el 6 dos veces. → Calcula 6 × 14 y "
            "compáralo con lo que propones."
        ),
        "fb_m03_e4_arith": (
            "6 × 10 = 60 está bien; el problema es lo que hizo con el 4. → Di por cuánto "
            "había que multiplicar el 4."
        ),
        "fb_m03_e4_none": (
            "Calcula el paréntesis primero: 10 + 4 = 14, y 6 × 14. → Compara ese resultado con 64."
        ),
        "fb_m03_e5_trap": (
            "Eso es exactamente lo que hizo el brazo con las nueve veces. → Prueba con "
            "a = 3, b = 4, c = 2 y compara los dos lados."
        ),
        "fb_m03_e5_never": (
            "Casi: fallan casi siempre, pero hay un caso donde coinciden. → Prueba con a = 1."
        ),
        "fb_m03_e5_small": (
            "3, 4 y 2 son pequeños y ya difieren en 48. → Calcula los dos lados con esos números."
        ),
        "fb_m03_e7_sum": (
            "Ahí desapareció la multiplicación. → Calcula 9 × 15 + 9 × 5 y compara con 9 + 15 + 5."
        ),
        "fb_m03_e7_double": (
            "El 9 aparece una vez en cada término, no dos veces en total. Duplicarlo dobla "
            "el resultado. → Calcula las dos y compara."
        ),
        "fb_m03_e7_product": (
            "Los dos términos se SUMAN, no se multiplican. → Calcula 9 × 15 + 9 × 5 y "
            "busca cuál de las opciones da lo mismo."
        ),
    },
    "closing": (
        "El factor se reparte sobre sumas y restas, nunca sobre productos; el exponente al "
        "revés. Esta es la propiedad que sostiene el álgebra entera. En el Calibre Cero vas "
        "a buscar los números que dejan todo como estaba."
    ),
    "validation_status": "F3_M03_11bloques",
}
