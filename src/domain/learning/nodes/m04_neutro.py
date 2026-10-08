"""M04 · Elemento neutro — cada operación tiene el suyo, y a veces por un solo lado.

Estación del nodo: EL CALIBRE CERO (varillas medidas contra galgas patrón).
Ninguna otra estación usa este material.
"""

NODE_ID = "PREALG-N3-M04-ELEMENTO-NEUTRO"
CONCEPT_SLUG = "elemento_neutro"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "elemento_neutro",
    "misconception": "neutro_es_el_mismo_para_toda_operacion",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El Calibre Cero · Elemento neutro",
    "station": "El Calibre Cero",
    "finish_label": "Salir hacia la Prensa de Contrapesos",
    "title": "Cada operación tiene su propio «no cambies nada»",
    "intro": (
        "Hay un número que, aplicado a cualquier otro, lo deja exactamente igual. Pero no "
        "es el mismo para todas las operaciones, y en algunas solo funciona si se pone de "
        "un lado. Vas a averiguar cuál es en cada caso y por qué el cero no sirve para todo."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de coger el calibre. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $37+0$?",
                "answer": "37",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $37\times 0$?",
                "options": [
                    {"id": "zero", "text": "0", "latex": r"0"},
                    {"id": "same", "text": "37", "latex": r"37"},
                    {"id": "one", "text": "1", "latex": r"1"},
                ],
                "expected": "zero",
                "misconception_by_option": {
                    "same": "neutro_es_el_mismo_para_toda_operacion",
                    "one": "confunde_neutro_con_absorbente",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Qué número deja igual a cualquier otro al MULTIPLICARLO?",
                "options": [
                    {"id": "one", "text": "El 1", "latex": r"1"},
                    {"id": "zero", "text": "El 0", "latex": r"0"},
                    {"id": "none", "text": "Ninguno: multiplicar siempre cambia el número"},
                ],
                "expected": "one",
                "misconception_by_option": {
                    "zero": "neutro_es_el_mismo_para_toda_operacion",
                    "none": "multiplicar_siempre_agranda",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el Calibre Cero",
        "title": "La galga que no cambia nada",
        "body": (
            "La cuarta estación es un banco de calibración: varillas de acero, un calibre "
            "de precisión y una fila de galgas patrón colgadas por tamaño. Una galga se "
            "aplica a una varilla y la deja lista para el siguiente paso.\n\n"
            "En la fila hay una galga marcada con un cero. Aplicada al banco de sumar, la "
            "varilla sale idéntica a como entró, y por eso el calibrador la llama «la que "
            "no cambia nada». Hoy la aplicó al banco de multiplicar. La varilla no salió "
            "idéntica: no salió nada."
        ),
        "question": "¿Existe un número que deje igual a cualquier otro, en cualquier operación?",
        "image": "/leccion/03-prealg-n3-fabrica/m04-elemento-neutro-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Sí: el cero, en todas"},
                {"id": "b", "text": "Sí, pero cambia según la operación"},
                {"id": "c", "text": "No existe ninguno"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder nombrar el neutro de "
                "cada operación y decir en cuáles solo funciona por un lado."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "La misma galga, dos bancos distintos",
        "body": (
            "Abajo, la galga del cero aplicada a los dos bancos. Fíjate en qué sale de cada uno."
        ),
        "cases": [
            {
                "label": "Caso que funciona",
                "context": "Varilla de 37, banco de sumar, galga del 0",
                "fraction": r"37+0",
                "division": r"37+0=37",
                "note": "Sale idéntica. Aquí el 0 sí es «el que no cambia nada».",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "La misma varilla de 37, banco de multiplicar, galga del 0",
                "fraction": r"37\times 0",
                "division": r"37\times 0=0",
                "note": "No sale idéntica: no sale nada. El 0 arrasó la varilla.",
            },
        ],
        "resolution": (
            "El 0 no es «la nada» que se puede ignorar: es el punto de partida de la suma. "
            "Sumar 0 es no moverse, y por eso no cambia nada. Multiplicar por 0 es hacer "
            "cero copias, y eso no deja nada. El neutro del producto es otro: el 1, hacer "
            "una sola copia."
        ),
    },
    "definition_title": "El elemento neutro",
    "definition_katex": r"a+0=a\qquad a\times 1=a",
    "definition": (
        "El elemento neutro de una operación es el número que, combinado con cualquier "
        "otro, lo deja igual. El de la suma es 0; el del producto es 1. No hay un neutro "
        "universal, y en la resta y la división solo funciona puesto a la derecha."
    ),
    "definition_symbols": [
        {"symbol": r"0", "reads": "neutro aditivo", "means": "no moverse desde donde estás"},
        {"symbol": r"1", "reads": "neutro multiplicativo", "means": "hacer una sola copia"},
        {
            "symbol": r"a\times 0=0",
            "reads": "el cero absorbe",
            "means": "no es neutro del producto: lo arrasa todo",
        },
        {
            "symbol": r"a-0=a\ \text{pero}\ 0-a=-a",
            "reads": "neutro por la derecha",
            "means": "en la resta el 0 solo sirve puesto detrás",
        },
        {
            "symbol": r"a\div 1=a\ \text{pero}\ 1\div a\neq a",
            "reads": "neutro por la derecha",
            "means": "en la división el 1 solo sirve puesto detrás",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Los dos neutros",
            "title": "Dos galgas para dos bancos",
            "statement": (
                "Una varilla de 46 tiene que pasar por el banco de sumar y por el de "
                "multiplicar saliendo intacta de los dos. ¿Qué galga se usa en cada uno?"
            ),
            "latex": r"46+0=46\qquad 46\times 1=46",
            "image_slot": False,
            "steps": [
                "Banco de sumar: busco el número que sumado a 46 deja 46. Es el 0.",
                "Compruebo que sirve para cualquier varilla: 7 + 0 = 7, −3 + 0 = −3. Siempre.",
                "Banco de multiplicar: busco el número que multiplicado por 46 deja 46. No es el 0 (da 0): es el 1.",
                "Compruebo: 7 × 1 = 7, −3 × 1 = −3. También siempre.",
                "Dos operaciones, dos neutros distintos. Ninguna galga sirve para las dos.",
            ],
            "solution": r"Suma: $0$. Producto: $1$.",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se descarta el 0 para el producto. ¿Por qué «no cambiar nada» y «no dejar nada» no son lo mismo?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Neutro por un solo lado",
            "title": "La galga que solo sirve puesta detrás",
            "statement": (
                "La varilla de 46 entra al banco de restar con la galga del 0. ¿Sale "
                "idéntica? ¿Y si la galga entra primero?"
            ),
            "latex": r"46-0=46\quad\text{pero}\quad 0-46=-46",
            "image_slot": False,
            "steps": [
                "Con la galga detrás: 46 − 0 = 46. Sale idéntica.",
                "Con la galga delante: 0 − 46 = −46. Sale con el signo cambiado.",
                "En la suma daba igual el lado, porque la suma conmuta (M01).",
                "En la resta no conmuta, así que el neutro solo vale por un lado: se dice neutro POR LA DERECHA.",
                "Lo mismo pasa en la división con el 1: 46 ÷ 1 = 46, pero 1 ÷ 46 ≈ 0,02.",
            ],
            "solution": r"$46-0=46$; el 0 es neutro solo por la derecha",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El calibrador que usó una sola galga",
            "statement": (
                "El calibrador deja escrito: «La galga del cero no cambia nada, lo comprobé "
                "en el banco de sumar. Así que la uso también en el de multiplicar: "
                "46 × 0 = 46»."
            ),
            "latex": r"46\times 0=46",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"46\times 0=\underline{46}",
            "error_note": "Confundió «no cambia nada» con «no es nada». El 0 no es neutro del producto: es su absorbente.",
            "correct_version": {
                "wrong_latex": r"46\times 0=46",
                "right_latex": r"46\times 0=0\qquad 46\times 1=46",
                "rows": [
                    {
                        "wrong": "El 0 no cambia nada en ninguna operación",
                        "right": "El 0 no cambia nada al SUMAR; al multiplicar lo arrasa",
                    },
                    {
                        "wrong": "Hay una sola galga que sirve para todos los bancos",
                        "right": "Cada operación tiene su propio neutro",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 46 × 0 no puede dar 46? Di cuál es el neutro correcto del producto.",
            "steps": [
                "Vuelve a la definición del producto: 46 × 0 es hacer CERO grupos de 46.",
                "Cero grupos no dejan nada: el resultado es 0, y eso vale para cualquier varilla.",
                "El número que deja la varilla intacta al multiplicar es el 1: hacer un solo grupo.",
            ],
            "solution": (
                "El 0 y el 1 no son intercambiables. El 0 es el punto de partida de la suma; "
                "el 1, el del producto. Confundirlos es lo que hace que un cálculo largo "
                "colapse de golpe a cero."
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
                "statement": "Una varilla de 58 pasa por el banco de sumar con la galga neutra.",
                "given_steps": [
                    r"\text{neutro de la suma}=0",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"58+0=", "answer": "58"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "La misma varilla pasa por el banco de multiplicar, primero con la galga del 0 y después con la neutra.",
                "given_steps": [
                    r"\text{banco de multiplicar}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"58\times 0=", "answer": "0"},
                    {"id": "P2-b2", "label": r"58\times 1=", "answer": "58"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: en el banco de elevar, ¿qué sale de una varilla "
                    "de 58 con exponente 1? ¿Y qué sale de una varilla de 1 con exponente 58?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"58^{1}=", "answer": "58"},
                    {"id": "P3-b2", "label": r"1^{58}=", "answer": "1"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma varilla",
        "intro": r"¿Cuánto vale $(83\times 1)+(0\times 47)$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Calcular todo",
                "steps": [r"83\times 1=83", r"0\times 47=0", r"83+0=83"],
                "note": "Fiable: hace cada paso sin saltarse nada.",
            },
            {
                "label": "Método 2 · Reconocer neutro y absorbente",
                "steps": [
                    r"83\times 1\to\text{neutro: queda }83",
                    r"0\times 47\to\text{absorbente: }0",
                    r"=83",
                ],
                "note": "Lee la expresión en vez de calcularla.",
            },
        ],
        "question": "¿Qué habría pasado en el método 2 si el segundo término fuera 0 + 47 en vez de 0 × 47?",
        "insight": (
            "Con 0 + 47 el cero es NEUTRO y deja pasar el 47, así que el total sería 130. "
            "Con 0 × 47 es ABSORBENTE y lo borra. El mismo cero, dos comportamientos "
            "opuestos según el signo que tenga al lado: por eso no basta con reconocer el "
            "número, hay que leer la operación."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuánto vale $64\times 1$?",
            "expr": r"64\times 1",
            "answer": "64",
            "hints": {
                "n1": "Multiplicar por 1 es hacer un solo grupo.",
                "n2": "Un grupo de 64.",
                "n3": "El 1 es el neutro del producto.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuánto vale $64\times 0$?",
            "expr": r"64\times 0",
            "answer": "0",
            "hints": {
                "n1": "Multiplicar por 0 es hacer cero grupos.",
                "n2": "Cero grupos no dejan nada.",
                "n3": "El 0 no es neutro del producto: lo absorbe.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuánto vale $0-29$?",
            "expr": r"0-29",
            "answer": "-29",
            "hints": {
                "n1": "Aquí el 0 va DELANTE, no detrás.",
                "n2": "Se le quitan 29 a nada.",
                "n3": "El resultado queda por debajo del cero.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"Un calibrador anota «$1\div 25=25$, porque el 1 es neutro». ¿Dónde está el error?",
            "options": [
                {
                    "id": "right_only",
                    "text": "El 1 solo es neutro puesto a la derecha: 25 ÷ 1 = 25, pero 1 ÷ 25 = 0,04",
                },
                {"id": "wrong_neutral", "text": "El neutro de la división es el 0, no el 1"},
                {"id": "arith", "text": "Se equivocó al dividir: da 26"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "right_only",
            "feedback_by_option": {
                "right_only": "correct",
                "wrong_neutral": "fb_m04_e4_zero",
                "arith": "fb_m04_e4_arith",
                "none": "fb_m04_e4_none",
            },
            "misconception_by_option": {
                "wrong_neutral": "neutro_es_el_mismo_para_toda_operacion",
                "arith": "habito_error_de_calculo_no_de_metodo",
                "none": "neutro_funciona_por_los_dos_lados",
            },
            "hints": {
                "n1": "¿La división conmuta? Eso lo decidiste en la Prensa de Intercambio.",
                "n2": "1 ÷ 25 reparte 1 entre 25 partes.",
                "n3": "El resultado es menor que 1, no 25.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Existe un número que deja igual a cualquier otro en TODAS las operaciones.»",
            "options": [
                {
                    "id": "false_each",
                    "text": "Falsa: cada operación tiene el suyo (0 para sumar, 1 para multiplicar)",
                },
                {"id": "true_zero", "text": "Verdadera: el 0"},
                {"id": "true_one", "text": "Verdadera: el 1"},
                {"id": "false_none", "text": "Falsa: no existe neutro en ninguna operación"},
            ],
            "expected": "false_each",
            "feedback_by_option": {
                "false_each": "correct",
                "true_zero": "fb_m04_e5_trap",
                "true_one": "fb_m04_e5_one",
                "false_none": "fb_m04_e5_none",
            },
            "misconception_by_option": {
                "true_zero": "neutro_es_el_mismo_para_toda_operacion",
                "true_one": "neutro_es_el_mismo_para_toda_operacion",
                "false_none": "niega_la_existencia_del_neutro",
            },
            "hints": {
                "n1": "Prueba el candidato en las dos operaciones antes de decidir.",
                "n2": "Si dices 0: calcula 5 × 0. Si dices 1: calcula 5 + 1.",
                "n3": "Ninguno de los dos sobrevive a las dos pruebas.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("Sin calcular término a término: ¿cuánto vale (72 × 1) + (0 × 96)?"),
            "expr": r"(72\times 1)+(0\times 96)",
            "answer": "72",
            "hints": {
                "n1": "Uno de los dos términos es neutro y el otro absorbente.",
                "n2": "72 × 1 = 72.",
                "n3": "0 × 96 = 0, y 72 + 0 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": r"Una cuenta larga incluye el factor $(15-15)$ multiplicando a todo lo demás. ¿Cuánto vale la cuenta entera?",
            "options": [
                {"id": "zero", "text": "0: uno de los factores es cero y absorbe todo"},
                {"id": "rest", "text": "Lo que valga el resto: el (15−15) no cambia nada"},
                {"id": "cannot", "text": "No se puede saber sin calcular el resto"},
                {"id": "one", "text": "1"},
            ],
            "expected": "zero",
            "feedback_by_option": {
                "zero": "correct",
                "rest": "fb_m04_e7_rest",
                "cannot": "fb_m04_e7_cannot",
                "one": "fb_m04_e7_one",
            },
            "misconception_by_option": {
                "rest": "neutro_es_el_mismo_para_toda_operacion",
                "cannot": "no_reconoce_el_absorbente",
                "one": "confunde_neutro_con_absorbente",
            },
            "hints": {
                "n1": "Calcula primero cuánto vale (15 − 15).",
                "n2": "15 − 15 = 0.",
                "n3": "Cualquier cosa multiplicada por 0 da 0.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "El neutro a lo largo de las operaciones",
        "title": "¿Qué número deja el resultado intacto, y por qué lado?",
        "intro": "Las seis operaciones de la ciudad, cada una con su galga.",
        "rows": [
            {
                "symbol": r"+",
                "name": "Suma",
                "closed": "yes",
                "latex": r"a+0=0+a=a",
                "note": "Neutro 0, por los dos lados: la suma conmuta.",
            },
            {
                "symbol": r"-",
                "name": "Resta",
                "closed": "partial",
                "latex": r"a-0=a\quad\text{pero}\quad 0-a=-a",
                "note": "Neutro 0 solo por la DERECHA. Puesto delante, cambia el signo.",
            },
            {
                "symbol": r"\times",
                "name": "Multiplicación",
                "closed": "yes",
                "latex": r"a\times 1=1\times a=a",
                "note": "Neutro 1, por los dos lados. Ojo: el 0 aquí no es neutro sino absorbente.",
            },
            {
                "symbol": r"\div",
                "name": "División",
                "closed": "partial",
                "latex": r"a\div 1=a\quad\text{pero}\quad 1\div a=\dfrac{1}{a}",
                "note": "Neutro 1 solo por la DERECHA. Puesto delante da el recíproco — y eso es la estación siguiente.",
            },
            {
                "symbol": r"a^{n}",
                "name": "Potenciación",
                "closed": "partial",
                "latex": r"a^{1}=a\quad\text{pero}\quad 1^{a}=1",
                "note": "Neutro 1 solo en el EXPONENTE. En la base, el 1 absorbe.",
            },
            {
                "symbol": r"\sqrt[n]{a}",
                "name": "Radicación",
                "closed": "partial",
                "latex": r"\sqrt[1]{a}=a",
                "note": "Índice 1 deja el radicando intacto, pero no hay ningún radicando que deje intacto el índice.",
            },
        ],
        "outro": (
            "Ninguna galga sirve para todos los bancos, y en cuatro operaciones solo sirve "
            "por un lado. Fíjate en el patrón: las que aguantan por los dos lados son "
            "exactamente las que conmutan. En la Prensa de Contrapesos vas a buscar, para "
            "cada número, la pieza que lo devuelve al neutro."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los casos donde el neutro funciona por los DOS lados?",
        "thumbnails": [r"a+0=0+a", r"a\times 1=1\times a", r"a-0\neq 0-a"],
        "options": [
            {"id": "commutative", "text": "Son las operaciones que conmutan", "correct": True},
            {"id": "same_number", "text": "Usan el mismo número como neutro", "correct": False},
            {
                "id": "roles",
                "text": "Son aquellas donde los dos números hacen el mismo papel",
                "correct": True,
            },
            {"id": "grow", "text": "Son las que hacen crecer el resultado", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última calibración: una varilla pasa por la cuenta (91 × 1) − 0 + (0 × 44). "
            "¿Con qué medida sale?"
        ),
        "polya": {
            "comprender": "Tres términos, cada uno con un 0 o un 1. Piden el resultado final.",
            "planear": "Identifico en cada término si el número es neutro o absorbente, según la operación.",
            "ejecutar": "91 × 1 = 91 (neutro) → 91 − 0 = 91 (neutro por la derecha) → 0 × 44 = 0 (absorbente) → 91 + 0 = 91.",
            "comprobar": "Todos los términos añadidos valían 0 o dejaban igual: la varilla sale con su medida original, 91.",
        },
        "prompt": "¿Con qué medida sale la varilla?",
        "answer": "91",
        "hints": {
            "n1": "Trata cada término por separado y mira qué operación lo acompaña.",
            "n2": "91 × 1 = 91 y 91 − 0 = 91.",
            "n3": "0 × 44 = 0, así que el último término no aporta nada.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya eliges la galga según el banco, no por costumbre.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre "
            "«no cambia nada» y «no deja nada»."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $52+0$?",
                "answer": "52",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $52\times 0$?",
                "options": [
                    {"id": "zero", "text": "0", "latex": r"0"},
                    {"id": "same", "text": "52", "latex": r"52"},
                    {"id": "one", "text": "1", "latex": r"1"},
                ],
                "expected": "zero",
                "misconception_by_option": {
                    "same": "neutro_es_el_mismo_para_toda_operacion",
                    "one": "confunde_neutro_con_absorbente",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? $52-0=52$",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "sobregeneraliza_elemento_neutro"},
                # Caso donde el 0 SÍ deja igual: comprueba que aprendió el criterio
                # y no la heurística "el cero siempre arruina la cuenta".
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
        "default": "Mira qué operación acompaña al número antes de decidir si es neutro.",
        "fb_m04_e4_zero": (
            "El 0 en una división no es neutro: dividir entre 0 ni siquiera está definido. "
            "→ Comprueba 25 ÷ 1 y 1 ÷ 25 y di por qué lado funciona el 1."
        ),
        "fb_m04_e4_arith": (
            "No es un fallo de cálculo: 1 ÷ 25 no se acerca ni de lejos a 25. → Fíjate en "
            "qué número puso primero."
        ),
        "fb_m04_e4_none": (
            "Comprueba al revés: si 1 ÷ 25 fuera 25, entonces 25 × 25 debería dar 1. "
            "→ Calcula ese producto."
        ),
        "fb_m04_e5_trap": (
            "Prueba el 0 en el banco de multiplicar: 5 × 0. → Di qué sale y si eso es "
            "«dejar igual»."
        ),
        "fb_m04_e5_one": (
            "Prueba el 1 en el banco de sumar: 5 + 1. → Di qué sale y si eso es «dejar igual»."
        ),
        "fb_m04_e5_none": (
            "Sí existe, pero uno distinto por operación. → Nombra el que deja igual al sumar."
        ),
        "fb_m04_e7_rest": (
            "Calcula primero cuánto vale (15 − 15). → Di ese número y qué le hace a un producto."
        ),
        "fb_m04_e7_cannot": (
            "Sí se puede saber sin tocar el resto. → Calcula (15 − 15) y mira qué pasa al "
            "multiplicar por ese número."
        ),
        "fb_m04_e7_one": (
            "El 1 es el neutro del producto, pero aquí el factor no es 1. → Calcula (15 − 15)."
        ),
    },
    "closing": (
        "Cada operación tiene su neutro y no son intercambiables: 0 para sumar, 1 para "
        "multiplicar, y solo por la derecha en resta y división. En la Prensa de "
        "Contrapesos vas a buscar, para cada número, la pieza que lo lleva de vuelta al neutro."
    ),
    "validation_status": "F3_M04_11bloques",
}
