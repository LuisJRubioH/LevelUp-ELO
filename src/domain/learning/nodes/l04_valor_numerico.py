"""L04 · La cámara del recuento — poner el número en el lugar de la letra no basta.

Cuarta y última sala de la Casa de la Vida. Guía: Meritka. Vocabulario propio:
cámara del recuento, arqueo, ficha de barro, cordel de conteo, contable, cuenta
final. Nada de cálamos (L01), estantes (L02) ni dictados (L03).

Error focal: sustituir por yuxtaposición — leer 3n con n = 4 como «34» en vez de
como 3 · 4. Es el error que convierte el álgebra en un juego de pegar símbolos.
"""

NODE_ID = "ALG-N1-L04-VALOR-NUMERICO"
CONCEPT_SLUG = "valor_numerico"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "valor_numerico",
    "misconception": "yuxtapone_en_vez_de_multiplicar",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La cámara del recuento · Valor numérico",
    "house": "La cámara del recuento",
    "guide": "Meritka",
    "finish_label": "Salir hacia la obra",
    "title": "Poner el número donde estaba la letra no basta",
    "intro": (
        "Ya sabes escribir un registro. Ahora hay que devolverlo a números: llega el día "
        "del arqueo y cada registro tiene que dar una cantidad concreta de grano. Ahí se "
        "ve si entendiste lo que estabas escribiendo o solo lo copiabas."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de bajar a la cámara. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 3 · 7 + 2?",
                "answer": "23",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"Si $n=4$, ¿cuánto vale $3n$?",
                "options": [
                    {"id": "twelve", "text": "12"},
                    {"id": "thirtyfour", "text": "34"},
                    {"id": "seven", "text": "7"},
                ],
                "expected": "twelve",
                "misconception_by_option": {
                    "thirtyfour": "yuxtapone_en_vez_de_multiplicar",
                    "seven": "confunde_producto_con_suma",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 2 + 3 · 4?",
                "options": [
                    {"id": "fourteen", "text": "14"},
                    {"id": "twenty", "text": "20"},
                    {"id": "nine", "text": "9"},
                ],
                "expected": "fourteen",
                "misconception_by_option": {
                    "twenty": "opera_de_izquierda_a_derecha",
                    "nine": "confunde_producto_con_suma",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/l04-valor-numerico-katia.png",
        "eyebrow": "KatIA · En la cámara del recuento",
        "title": "El arqueo que no cuadró por una letra",
        "body": (
            "En la cámara hay fichas de barro con las cuentas del año y un cordel de conteo "
            "colgado de la pared. Meritka descuelga una tablilla:\n\n"
            "«Este registro dice 3n. Hoy n vale cuatro. El contable de la primavera anotó "
            "treinta y cuatro medidas de grano y mandó cargar treinta y cuatro carros.»\n\n"
            "Se quedó mirando el cordel: quedaban veintidós carros sin nada que cargar.\n\n"
            "«No se equivocó al escribir el registro. Se equivocó al leerlo.»"
        ),
        "question": "¿Qué se hace exactamente cuando se sustituye una letra por su valor?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {
                    "id": "a",
                    "text": "Se escribe el número en el hueco de la letra y se lee lo que quede",
                },
                {
                    "id": "b",
                    "text": "Se pone el número y además se hace la operación que había entre medias",
                },
                {"id": "c", "text": "Se suma el número al que ya estaba delante"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a saber por qué al contable le sobraron "
                "veintidós carros, y por qué con un paréntesis no le habría pasado."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El hueco no está vacío: hay una operación escondida",
        "body": "Dos registros parecidos. En uno la operación se ve; en el otro está callada.",
        "cases": [
            {
                "label": "La operación se ve",
                "context": r"El registro $3+n$, con $n=4$",
                "fraction": r"3+n",
                "division": r"3+4=7",
                "note": "El signo está escrito: nadie duda de qué hacer.",
            },
            {
                "label": "La operación está callada",
                "context": r"El registro $3n$, con $n=4$",
                "fraction": r"3n",
                "division": r"3\cdot 4=12",
                "note": "Pegar el 3 a la n YA significa multiplicar. Sustituir no borra ese producto.",
            },
        ],
        "resolution": (
            "Escribir 3n junto es una abreviatura de 3 · n. Al sustituir, la abreviatura "
            "deja de valer —3 · 4 no se puede escribir «34»— así que el punto tiene que "
            "reaparecer. Lo mismo pasa con los paréntesis: se ponen al sustituir aunque no "
            "estuvieran en el registro."
        ),
    },
    "definition_title": "Valor numérico de una expresión",
    "definition_katex": r"3n\ \text{con}\ n=4\;\longrightarrow\;3\cdot(4)=12",
    "definition": (
        "El VALOR NUMÉRICO de una expresión es el número que resulta de sustituir cada "
        "letra por su valor y operar. Sustituir tiene dos reglas que no se ven en el "
        "registro: la yuxtaposición (3n) es un producto y hay que escribirlo como tal, y "
        "el valor entra entre paréntesis, para que el orden de operaciones y los signos "
        "sigan funcionando."
    ),
    "definition_symbols": [
        {
            "symbol": r"3n\to 3\cdot(4)",
            "reads": "tres por cuatro",
            "means": "el producto callado reaparece",
        },
        {
            "symbol": r"3+n\to 3+(4)",
            "reads": "tres más cuatro",
            "means": "la operación ya estaba escrita",
        },
        {
            "symbol": r"n^{2}\to (4)^{2}",
            "reads": "cuatro al cuadrado",
            "means": "el exponente afecta a todo el valor",
        },
        {
            "symbol": r"5-n\to 5-(-3)",
            "reads": "cinco menos, menos tres",
            "means": "con negativos, el paréntesis es obligatorio",
        },
        {
            "symbol": r"2n^{2}\to 2\cdot(3)^{2}",
            "reads": "dos por tres al cuadrado",
            "means": "primero la potencia, después el producto",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · El arqueo de los remos",
            "title": "Sustituir y operar",
            "statement": (
                "El registro del almacén de remos dice 5r + 8, donde r es el número de "
                "barcas. Hoy hay 6 barcas. ¿Cuántos remos figuran?"
            ),
            "latex": r"5r+8",
            "image_slot": False,
            "steps": [
                "Reescribo el producto callado: 5r es 5 · r.",
                "Sustituyo r por su valor entre paréntesis: 5 · (6) + 8.",
                "Primero el producto: 5 · 6 = 30.",
                "Después la suma: 30 + 8 = 38.",
                "El arqueo da 38 remos. Si hubiera 7 barcas darían 43: solo se movió la r.",
            ],
            "solution": r"$38$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué se hace el producto antes que la suma, si la suma está escrita después?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · La deuda del granero",
            "title": "Cuando el valor es negativo",
            "statement": (
                "En las fichas de barro una deuda se anota con signo. El registro 5 − d "
                "mide lo que queda, y hoy d vale −3. ¿Cuánto queda?"
            ),
            "latex": r"5-d",
            "image_slot": False,
            "steps": [
                "Sustituyo d por su valor, entre paréntesis: 5 − (−3).",
                "Sin el paréntesis quedaría 5 − −3, que no es una cuenta legible.",
                "Restar una deuda es sumar: 5 − (−3) = 5 + 3.",
                "El resultado es 8.",
                "Tiene sentido: si lo que se resta es una deuda, lo que queda aumenta.",
            ],
            "solution": r"$8$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El contable que pegó los números",
            "statement": (
                "Vuelve el caso de la apertura: el registro 3n con n = 4. El contable de la "
                "primavera anotó 34 y mandó cargar 34 carros."
            ),
            "latex": r"3n,\ n=4",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"3n\to 34",
            "error_note": (
                "Leyó 3n como dos casillas que se rellenan y se leen seguidas. Pero 3n es "
                "una abreviatura de 3 · n, y al sustituir hay que devolver el producto."
            ),
            "correct_version": {
                "wrong_latex": r"3n=34",
                "right_latex": r"3n=3\cdot 4=12",
                "rows": [
                    {
                        "wrong": "El 3 y el 4 se escriben seguidos: 34",
                        "right": "El 3 y la n estaban multiplicándose: 3 · 4 = 12",
                    },
                    {
                        "wrong": "34 medidas → 34 carros",
                        "right": "12 medidas → 12 carros, y sobran 22",
                    },
                ],
            },
            "explain_prompt": (
                "Explica por qué escribir 3n junto no es lo mismo que escribir 34 junto, "
                "aunque las dos cosas se vean pegadas."
            ),
            "steps": [
                "Pruebo con un valor pequeño: si n = 1, «pegar» daría 31, y el triple de 1 es 3.",
                "Con n = 0, «pegar» daría 30, y el triple de 0 es 0. El disparate es visible.",
                "Regla para no volver a caer: al sustituir, escribe el punto y el paréntesis, aunque no estuvieran.",
            ],
            "solution": (
                "3n con n = 4 vale 12. En 34 el 3 son decenas; en 3n el 3 es un factor. "
                "Pegado en el registro significa multiplicar, no yuxtaponer cifras."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El arqueo va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Calcula el valor de $4m+7$ cuando $m=5$.",
                "given_steps": [r"4\cdot(5)+7", r"20+7"],
                "blanks": [{"id": "P1-b1", "label": r"20+7=", "answer": "27"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Calcula el valor de $2k^{2}$ cuando $k=3$.",
                "given_steps": [r"2\cdot(3)^{2}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"(3)^{2}=", "answer": "9"},
                    {"id": "P2-b2", "label": r"2\cdot 9=", "answer": "18"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: el registro $6-p$ con $p=-2$. "
                    "Recuerda el paréntesis."
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"6-(-2)=", "answer": "8"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de sustituir",
        "intro": r"El registro $7-2n$, con $n=-4$. Las dos empiezan igual y no acaban igual.",
        "methods": [
            {
                "label": "Método 1 · Escribir el valor en el hueco",
                "steps": [
                    r"7-2n",
                    r"7-2\cdot -4",
                    r"\text{¿}-2\cdot 4\text{ o }-(2\cdot 4)\text{?}",
                ],
                "note": "Se escribe rápido y deja una cuenta ambigua justo donde hay un signo.",
            },
            {
                "label": "Método 2 · Meter el valor entre paréntesis",
                "steps": [
                    r"7-2\cdot(-4)",
                    r"7-(-8)",
                    r"7+8=15",
                ],
                "note": "Un símbolo más y la cuenta queda cerrada: no hay dos lecturas posibles.",
            },
        ],
        "question": "¿Cuándo se nota la diferencia entre los dos métodos?",
        "insight": (
            "Con valores positivos los dos dan lo mismo y el paréntesis parece un capricho. "
            "La diferencia aparece con negativos y con exponentes: en 7 − 2n con n = −4, sin "
            "paréntesis es fácil terminar en 7 − 8 = −1 en vez de 15. Por eso conviene "
            "poner el paréntesis siempre, y no solo cuando ya se ve el peligro — cuando se "
            "ve, normalmente ya te equivocaste."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"Calcula el valor de $6t+5$ cuando $t=7$.",
            "expr": r"6t+5,\quad t=7",
            "answer": "47",
            "hints": {
                "n1": "6t es 6 · t: el producto está callado, pero está.",
                "n2": "6 · 7 = 42.",
                "n3": "42 + 5 = …",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Si $m=5$, ¿cuánto vale $4m$?",
            "options": [
                {"id": "twenty", "text": "20"},
                {"id": "fortyfive", "text": "45"},
                {"id": "nine", "text": "9"},
                {"id": "fivefour", "text": "54"},
            ],
            "expected": "twenty",
            "feedback_by_option": {
                "twenty": "correct",
                "fortyfive": "fb_l04_e2_glue",
                "nine": "fb_l04_e2_sum",
                "fivefour": "fb_l04_e2_glue",
            },
            "misconception_by_option": {
                "fortyfive": "yuxtapone_en_vez_de_multiplicar",
                "nine": "confunde_producto_con_suma",
                "fivefour": "yuxtapone_en_vez_de_multiplicar",
            },
            "hints": {
                "n1": "Escribe el producto que estaba callado.",
                "n2": "4 · m con m = 5.",
                "n3": "Cuatro veces cinco.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"Calcula el valor de $3k^{2}$ cuando $k=4$.",
            "expr": r"3k^{2},\quad k=4",
            "answer": "48",
            "hints": {
                "n1": "El exponente afecta solo a la k, no al 3.",
                "n2": "Primero la potencia: 4² = 16.",
                "n3": "3 · 16 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un contable calcula 9 − b con b = −5 y anota 4, porque «nueve menos cinco». "
                "¿Dónde está el error?"
            ),
            "options": [
                {"id": "paren", "text": "Ignoró el signo del valor: 9 − (−5) = 14"},
                {"id": "op", "text": "La operación no era una resta"},
                {"id": "value", "text": "b no puede valer un número negativo"},
                {"id": "none", "text": "No hay error: 9 − 5 = 4"},
            ],
            "expected": "paren",
            "feedback_by_option": {
                "paren": "correct",
                "op": "fb_l04_e4_op",
                "value": "fb_l04_e4_value",
                "none": "fb_l04_e4_none",
            },
            "misconception_by_option": {
                "op": "confunde_la_operacion_dictada",
                "value": "magnitud_sin_signo",
                "none": "sustituye_sin_parentesis",
            },
            "hints": {
                "n1": "Sustituye poniendo el valor entre paréntesis.",
                "n2": "Queda 9 − (−5), no 9 − 5.",
                "n3": "Restar una cantidad negativa suma.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                r"¿Verdadera o falsa? «Para hallar el valor de $2n$ basta con escribir el "
                r"valor de $n$ al lado del 2.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": r"Falsa: $2n$ es $2\cdot n$, así que con $n=7$ vale 14, no 27",
                },
                {"id": "true", "text": "Verdadera: por eso se escriben pegados"},
                {"id": "true_small", "text": "Verdadera si el valor es de una sola cifra"},
                {"id": "false_never", "text": "Falsa: nunca se puede sustituir directamente"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_l04_e5_trap",
                "true_small": "fb_l04_e5_small",
                "false_never": "fb_l04_e5_never",
            },
            "misconception_by_option": {
                "true": "yuxtapone_en_vez_de_multiplicar",
                "true_small": "yuxtapone_en_vez_de_multiplicar",
                "false_never": "sobregeneraliza_valor_numerico",
            },
            "hints": {
                "n1": "Prueba con n = 0 y mira si el resultado tiene sentido.",
                "n2": "«Pegar» daría 20; el doble de 0 es 0.",
                "n3": "Estar pegados significa multiplicar.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (r"Con $x=3$, selecciona TODOS los registros cuyo valor numérico es $9$."),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$3x$", "latex": r"3x"},
                {"id": "b", "text": r"$x^{2}$", "latex": r"x^{2}"},
                {"id": "c", "text": r"$x+3$", "latex": r"x+3"},
                {"id": "d", "text": r"$2x+3$", "latex": r"2x+3"},
            ],
            "expected": ["a", "b", "d"],
            "trap_options": ["c"],
            "hints": {
                "n1": "Evalúa uno por uno; no descartes por el aspecto.",
                "n2": "3x y x² dan lo mismo solo porque x vale 3.",
                "n3": "x + 3 con x = 3 da 6.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El registro del granero dice 8g − 12, donde g son los graneros abiertos. "
                "Hoy hay 5 abiertos. ¿Cuántas medidas figuran en el arqueo?"
            ),
            "expr": r"8g-12,\quad g=5",
            "answer": "28",
            "hints": {
                "n1": "8g es 8 · g.",
                "n2": "8 · 5 = 40.",
                "n3": "40 − 12 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Basta con poner el número en el hueco?",
        "title": "Qué hay que reponer al sustituir",
        "intro": (
            "Sustituir no es rellenar una casilla. Hay cosas que el registro daba por "
            "sabidas y que al poner el número tienen que volver a escribirse."
        ),
        "rows": [
            {
                "symbol": r"n+3",
                "name": "Suma escrita",
                "closed": "yes",
                "latex": r"(4)+3=7",
                "note": "Nada que reponer: la operación ya estaba a la vista.",
            },
            {
                "symbol": r"3n",
                "name": "Producto callado",
                "closed": "no",
                "latex": r"3\cdot(4)=12",
                "note": "Hay que devolver el punto. Es el caso focal: pegado significa multiplicar.",
            },
            {
                "symbol": r"n^{2}",
                "name": "Potencia",
                "closed": "no",
                "latex": r"(4)^{2}=16",
                "note": "El exponente afecta a todo el valor sustituido, no a una cifra suelta.",
            },
            {
                "symbol": r"5-n",
                "name": "Valor negativo",
                "closed": "no",
                "latex": r"5-(-3)=8",
                "note": "Sin paréntesis quedan dos signos seguidos y la cuenta deja de ser legible.",
            },
            {
                "symbol": r"2n^{2}",
                "name": "Potencia y producto juntos",
                "closed": "no",
                "latex": r"2\cdot(3)^{2}=18",
                "note": "Además del punto y el paréntesis, hay que respetar el orden: potencia antes que producto.",
            },
            {
                "symbol": r"-n",
                "name": "Menos delante de la letra",
                "closed": "partial",
                "latex": r"-(-4)=4",
                "note": "Se sustituye igual que los demás, pero el resultado sale positivo: ese menos no dice «negativo», dice «el opuesto».",
            },
        ],
        "outro": (
            "La última fila es la que más cuesta: −n no es «un número negativo», es «el "
            "opuesto de n», y si n ya era negativo el valor sale positivo. Todas las filas "
            "dicen lo mismo desde ángulos distintos — el registro está abreviado, y "
            "sustituir es el momento de desabreviarlo."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres arqueos trabajados en este nodo?",
        "thumbnails": [r"5r+8", r"5-d", r"3n"],
        "options": [
            {
                "id": "restore",
                "text": "En los tres hay que reponer algo que el registro daba por sabido",
                "correct": True,
            },
            {
                "id": "order",
                "text": "En los tres el resultado depende de operar en el orden correcto",
                "correct": True,
            },
            {
                "id": "fill",
                "text": "En los tres basta con escribir el número donde estaba la letra",
                "correct": False,
            },
            {
                "id": "same",
                "text": "En los tres el valor numérico es el mismo cualquiera que sea la letra",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Arqueo de cierre del año: el registro del grano dice 7c − 9, donde c son los "
            "carros que entraron. Este año entraron 12 carros. El contable anterior habría "
            "anotado «712 menos 9». ¿Cuál es la cifra correcta?"
        ),
        "polya": {
            "comprender": "7c es un producto abreviado; c vale 12 y hay que restar 9 al final.",
            "planear": "Repongo el punto y el paréntesis: 7 · (12) − 9. Producto primero, resta después.",
            "ejecutar": "7 · 12 = 84, y 84 − 9 = 75.",
            "comprobar": "Con 13 carros daría 82, nueve menos que 91: solo se movió la c ✓. Y 703 no era una cantidad de grano, era dos números pegados.",
        },
        "prompt": "¿Cuántas medidas figuran en el arqueo?",
        "answer": "75",
        "hints": {
            "n1": "Escribe el producto callado antes de sustituir.",
            "n2": "7 · 12 = 84.",
            "n3": "84 − 9 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otras cifras. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya repones el producto y el paréntesis antes de operar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué 3n con "
            "n = 4 no puede ser 34."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 5 · 6 + 3?",
                "answer": "33",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"Si $m=6$, ¿cuánto vale $2m$?",
                "options": [
                    {"id": "twelve", "text": "12"},
                    {"id": "twentysix", "text": "26"},
                    {"id": "eight", "text": "8"},
                ],
                "expected": "twelve",
                "misconception_by_option": {
                    "twentysix": "yuxtapone_en_vez_de_multiplicar",
                    "eight": "confunde_producto_con_suma",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"Si $p=-2$, ¿cuánto vale $4-p$?",
                "options": [
                    {"id": "six", "text": "6"},
                    {"id": "two", "text": "2"},
                    {"id": "minussix", "text": "−6"},
                ],
                "expected": "six",
                "misconception_by_option": {
                    "two": "sustituye_sin_parentesis",
                    "minussix": "magnitud_sin_signo",
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
        "default": "Repón lo que el registro abreviaba: el punto del producto y el paréntesis del valor.",
        "fb_l04_e2_glue": (
            "Ahí pegaste las cifras en vez de multiplicarlas. → 4m es 4 · m; prueba con "
            "m = 0 y verás el disparate."
        ),
        "fb_l04_e2_sum": "Estar pegados no es sumar, es multiplicar. → 4 · 5, no 4 + 5.",
        "fb_l04_e4_op": "La resta sí era la operación. → Lo que se perdió fue el signo del valor.",
        "fb_l04_e4_value": (
            "Una letra puede valer un número negativo sin problema. → Lo que falta es el "
            "paréntesis al sustituirla."
        ),
        "fb_l04_e4_none": (
            "El valor de b es −5, no 5. → Sustituido queda 9 − (−5), que suma en vez de restar."
        ),
        "fb_l04_e5_trap": (
            "Se escriben pegados justamente porque se multiplican. → Con n = 7, el doble es "
            "14 y no 27."
        ),
        "fb_l04_e5_small": (
            "El número de cifras no cambia la regla. → Con n = 7, una cifra, «pegar» ya da "
            "27 en vez de 14."
        ),
        "fb_l04_e5_never": (
            "Te pasaste al otro extremo: sí se sustituye directamente. → Lo que hay que "
            "reponer es el producto, no evitar la sustitución."
        ),
    },
    "closing": (
        "Con esto la Casa de la Vida está completa: sabes nombrar lo que cambia, "
        "distinguirlo de lo que está fijado, escribir un encargo hablado y devolverlo a "
        "números. Los registros ya se escriben y se leen — pero se están volviendo largos. "
        "En la obra, Bakenra te va a enseñar a acortarlos sin mezclar lo que no se mezcla."
    ),
    "validation_status": "F5_L04_11bloques",
}
