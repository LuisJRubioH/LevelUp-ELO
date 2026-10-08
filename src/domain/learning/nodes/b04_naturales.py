"""B04 · Naturales — contar cantidades completas.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «el 0 no es un número, es la ausencia de número».
"""

NODE_ID = "PREALG-N1-B04-NATURALES-CONTAR"
CONCEPT_SLUG = "naturales"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "naturales",
    "misconception": "cero_no_es_numero",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Primer peldaño · Naturales",
    "scene": {
        "image": "/leccion/00-comunes/step-naturales.png",
        "step": "naturals",
        "aria": "Los números naturales son cero, uno, dos, tres y así sucesivamente",
    },
    "finish_label": "Continuar a enteros",
    "title": "Contar es ponerle número a un montón",
    "intro": (
        "Este es el primer peldaño y el más engañoso, porque crees que ya lo sabes. "
        "Aquí vas a decidir qué cantidades se pueden contar, por qué el montón vacío "
        "también tiene número, y en qué momento contar deja de alcanzar."
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
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "En una repisa hay 6 lámparas de aceite y en la de al lado hay 5. ¿Cuántas lámparas hay en total?",
                "answer": "11",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Un cofre de ofrendas está completamente vacío. ¿Cuántas monedas tiene?",
                "options": [
                    {"id": "zero", "text": "Tiene 0 monedas"},
                    {"id": "none", "text": "No tiene un número: simplemente no tiene nada"},
                    {"id": "cannot", "text": "No se puede saber sin abrirlo"},
                ],
                "expected": "zero",
                "misconception_by_option": {
                    "none": "cero_no_es_numero",
                    "cannot": "habito_evita_decidir",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Tenías 3 cinceles y prestaste 5. ¿Cuántos te quedan?",
                "options": [
                    {"id": "impossible", "text": "No se puede: no tenías 5 para prestar"},
                    {"id": "two", "text": "Quedan 2"},
                    {"id": "zero", "text": "Quedan 0"},
                    {"id": "minus_two", "text": "Quedan −2"},
                ],
                # Trampa deliberada: la pregunta no tiene respuesta DENTRO de ℕ.
                # "No se puede" es la lectura honesta en este peldaño; −2 se
                # acepta como intuición adelantada y se recoge en B05.
                "expected": "impossible",
                "misconception_by_option": {
                    "two": "resta_al_reves",
                    "zero": "trunca_en_cero",
                    "minus_two": "adelanta_enteros",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · El primer peldaño",
        "title": "El censo del ágora",
        "body": (
            "El arconte mandó contar todo lo que hay en el ágora antes del festival. "
            "KatIA recorre la plaza con una tablilla: 12 columnas en el pórtico, "
            "9 puestos abiertos, 4 fuentes, 7 palomas en el tejado.\n\n"
            "Llega al último puesto de la fila. El comerciante se fue de viaje y no "
            "queda nada: ni una jarra, ni un saco, ni un banco. KatIA levanta el "
            "cincel sobre la tablilla y se queda quieta, sin saber qué grabar."
        ),
        "question": "¿Qué debe grabar KatIA en la casilla de ese puesto?",
        "image": "/leccion/01-prealg-n1-agora/b04-naturales-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que harías tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "Dejar la casilla en blanco: no hay nada que contar"},
                {"id": "b", "text": "Grabar un 0", "latex": r"0"},
                {"id": "c", "text": "Tachar el puesto del censo"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber por qué "
                "las tres se pueden defender, pero solo una deja el censo utilizable."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos casillas del censo, dos problemas distintos",
        "body": (
            "Mira las dos casillas de abajo. En las dos KatIA no puede escribir un "
            "número «normal», pero por razones opuestas: una se resuelve hoy y la otra "
            "no cabe todavía en este peldaño."
        ),
        "cases": [
            {
                "label": "Caso que se resuelve",
                "context": "El puesto vacío del comerciante que se fue",
                "fraction": r"0",
                "division": r"\text{cantidad}=0",
                "note": (
                    "Sí hay número: el 0. Contar un montón vacío da cero, y cero es una "
                    "respuesta, no un hueco. La casilla queda utilizable."
                ),
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Prestó 5 cinceles y solo tenía 3",
                "fraction": r"3-5",
                "division": r"3-5=\ ?",
                "note": (
                    "Aquí no hay ningún natural que sirva. No es que no sepamos: es que "
                    "la respuesta no existe DENTRO de este conjunto."
                ),
            },
        ],
        "resolution": (
            "Fíjate en la diferencia. «Vacío» sí tiene número y ese número es 0. «Deber» "
            "no tiene número aquí, y por eso el siguiente peldaño tendrá que inventarlo. "
            "Cero no es la falta de número: es el número de la falta."
        ),
    },
    "definition_title": "Los números naturales",
    "definition_katex": r"\mathbb{N}=\{0,1,2,3,4,\ldots\}",
    "definition": (
        "La frase del nodo: contar es ponerle un número a un montón, y el montón vacío "
        "también tiene el suyo."
    ),
    "definition_symbols": [
        {
            "symbol": r"\mathbb{N}",
            "reads": "los naturales",
            "means": "de natural: los números con los que se cuenta",
        },
        {
            "symbol": r"0",
            "reads": "cero",
            "means": "el número del montón vacío; en este curso SÍ es natural",
        },
        {
            "symbol": r"\{\ \}",
            "reads": "llaves",
            "means": "encierran a los miembros del conjunto, uno por uno",
        },
        {
            "symbol": r"\ldots",
            "reads": "puntos suspensivos",
            "means": "sigue igual para siempre: no hay un último natural",
        },
        {
            "symbol": r"n\in\mathbb{N}",
            "reads": "n pertenece a ℕ",
            "means": "n es uno de esos números",
        },
        {
            "symbol": r"n+1",
            "reads": "el siguiente de n",
            "means": "cada natural tiene sucesor; por eso no se acaban",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Contar objetos completos",
            "title": "Las gradas del teatro",
            "statement": (
                "Hay que anotar cuántas gradas tiene el teatro. KatIA cuenta 14 en el "
                "sector de arriba y 9 en el de abajo. ¿Cuántas gradas grabo en la tablilla?"
            ),
            "latex": r"14+9",
            "image_slot": False,
            "steps": [
                "Compruebo que sean objetos completos: una grada no se cuenta por mitades.",
                "Cuento cada sector por separado: 14 arriba, 9 abajo.",
                "Junto los dos montones: 14 + 9.",
                "14 + 9 = 23, y 23 es natural, así que cabe en el censo.",
                "Grabo 23 en la tablilla.",
            ],
            "solution": r"$14+9=23$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 0,
                "prompt": (
                    "En el paso 1 comprobé que fueran objetos completos antes de contar. "
                    "¿Por qué ese chequeo va primero y no al final?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El montón vacío",
            "title": "El puesto sin comerciante",
            "statement": (
                "El puesto del comerciante que se fue de viaje no tiene ni una jarra. "
                "¿Qué cantidad va en su casilla del censo?"
            ),
            "latex": r"0",
            "image_slot": False,
            "steps": [
                "Miro el puesto y cuento lo que hay: no empiezo a contar porque no hay nada.",
                "Un montón sin objetos también tiene una cantidad: la cantidad es cero.",
                "Escribo 0, no dejo la casilla en blanco.",
                "Una casilla en blanco significa «no lo revisé»; un 0 significa «lo revisé y no había nada».",
                "El censo queda completo: 0 es un dato, el blanco es un vacío de información.",
            ],
            "solution": r"$\text{cantidad}=0,\ \ 0\in\mathbb{N}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El censo con casillas en blanco",
            "statement": (
                "Un escriba entregó su parte del censo así. Está mal: «Puse 0 solo donde "
                "sobraba algo y dejé en blanco los puestos vacíos, porque el 0 no es un "
                "número: es que no hay nada»."
            ),
            "latex": r"0=\text{«nada»}",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"0\ \ \neq\ \ \underline{\text{casilla en blanco}}",
            "error_note": (
                "Aquí se cayó. Confundió el número 0 con la ausencia de dato. El arconte "
                "no puede distinguir un puesto vacío de uno que nadie revisó."
            ),
            "correct_version": {
                "wrong_latex": r"\text{puesto vacío}\ \rightarrow\ \square",
                "right_latex": r"\text{puesto vacío}\ \rightarrow\ 0\in\mathbb{N}",
                "rows": [
                    {
                        "wrong": "0 significa «no hay nada que decir»",
                        "right": "0 es la respuesta a «¿cuántos hay?»: ninguno",
                    },
                    {
                        "wrong": "Un blanco y un 0 dicen lo mismo",
                        "right": "El blanco dice «sin revisar»; el 0 dice «revisado, vacío»",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué un 0 y una casilla en blanco no dicen lo mismo? Escribe qué "
                "debía grabar el escriba."
            ),
            "steps": [
                "Pregúntate qué información pierde el arconte con cada opción.",
                "Con el 0 sabe que ese puesto fue revisado y estaba vacío.",
                "Con el blanco no sabe si estaba vacío o si el escriba no llegó hasta allá.",
            ],
            "solution": (
                "El 0 es un número con trabajo que hacer: responde «¿cuántos hay?» cuando "
                "la respuesta es ninguno. La ausencia de dato no es un número — es un "
                "hueco en el censo, y por eso se ve distinto."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el conteo ya está empezado y "
            "solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "En el pórtico hay 12 columnas de un lado y 12 del otro. Se derrumbaron 3.",
                "given_steps": [
                    r"12+12=24",
                    r"24-3",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Columnas en pie}=", "answer": "21"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "El festival necesita 40 antorchas. Hay 3 repisas con 8 antorchas "
                    "cada una y ninguna más."
                ),
                "given_steps": [
                    r"3\times8",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{Antorchas disponibles}=", "answer": "24"},
                    {"id": "P2-b2", "label": r"\text{Faltan }40-24=", "answer": "16"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: KatIA revisó 9 puestos. En 5 había mercancía "
                    "y los otros 4 estaban vacíos. ¿Cuántas casillas del censo llevan un "
                    "número escrito?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Casillas con número}=", "answer": "9"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos caminos para el mismo total",
        "intro": (
            "En el almacén del festival hay 6 estantes y cada uno guarda 4 jarras. "
            "¿Cuántas jarras hay? Las dos soluciones de abajo son correctas."
        ),
        "methods": [
            {
                "label": "Método 1 · Contar una por una",
                "steps": [r"1,2,3,4", r"5,6,7,8\ \ldots", r"\text{total}=24"],
                "note": "Siempre funciona y nunca falla, pero se hace eterno.",
            },
            {
                "label": "Método 2 · Agrupar y multiplicar",
                "steps": [
                    r"6\ \text{estantes}\times4\ \text{jarras}",
                    r"6\times4",
                    r"\text{total}=24",
                ],
                "note": "Solo si todos los grupos tienen el mismo tamaño.",
            },
        ],
        "question": (
            "¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si un estante "
            "tiene 4 jarras y otro tiene 3?"
        ),
        "insight": (
            "El segundo método falla en cuanto los grupos son desiguales, y ese fracaso "
            "es el contenido: multiplicar es contar grupos IGUALES, no un atajo universal. "
            "Lo vas a volver a ver cuando la multiplicación se defina en serio (N2-E03)."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "En el taller hay 17 sacos de trigo y llegan 8 más en la carreta. ¿Cuántos sacos quedan en el taller?",
            "expr": r"17+8",
            "answer": "25",
            "hints": {
                "n1": "¿Los sacos que llegan se suman o se restan?",
                "n2": "Junta los dos montones: los que había y los que llegaron.",
                "n3": "17 + 8: primero 17 + 3 = 20, y quedan 5 más.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Se reparten 5 filas de bancos con 7 bancos cada una. ¿Cuántos bancos hay?",
            "expr": r"5\times7",
            "answer": "35",
            "hints": {
                "n1": "Todas las filas tienen el mismo tamaño: ¿puedes agrupar?",
                "n2": "Contar 5 grupos de 7 es multiplicar.",
                "n3": "5 × 7 = 35.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas cantidades NO se puede escribir con un número natural?",
            "options": [
                {"id": "half", "text": "Media jarra de aceite", "latex": r"\tfrac{1}{2}"},
                {"id": "zero_doves", "text": "Ninguna paloma en el tejado", "latex": r"0"},
                {"id": "twelve", "text": "Doce columnas", "latex": r"12"},
                {"id": "hundred", "text": "Cien escalones", "latex": r"100"},
            ],
            "expected": "half",
            "feedback_by_option": {
                "half": "correct",
                "zero_doves": "fb_b04_e3_zero",
                "twelve": "fb_b04_e3_whole",
                "hundred": "fb_b04_e3_whole",
            },
            "misconception_by_option": {
                "zero_doves": "cero_no_es_numero",
                "twelve": "confunde_tamano_con_tipo",
                "hundred": "confunde_tamano_con_tipo",
            },
            "hints": {
                "n1": "¿Cuál de las cuatro habla de una parte y no de un objeto completo?",
                "n2": "Los naturales cuentan cosas enteras: 1 jarra, 2 jarras, 3 jarras.",
                "n3": "Media jarra cae ENTRE 0 y 1: no hay natural ahí.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un escriba anotó: «Había 9 palomas, volaron 4, quedan 5. Y como en el "
                "otro tejado no quedó ninguna, dejé esa casilla vacía». ¿Dónde está el error?"
            ),
            "options": [
                {"id": "blank", "text": "Debió grabar 0 en la casilla del otro tejado"},
                {"id": "subtraction", "text": "Restó mal: 9 − 4 no da 5"},
                {"id": "should_add", "text": "Debió sumar las que volaron, no restarlas"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "blank",
            "feedback_by_option": {
                "blank": "correct",
                "subtraction": "fb_b04_e4_subtraction",
                "should_add": "fb_b04_e4_add",
                "none": "fb_b04_e4_none",
            },
            "misconception_by_option": {
                "subtraction": "duda_del_calculo_correcto",
                "should_add": "confunde_operacion",
                "none": "cero_no_es_numero",
            },
            "hints": {
                "n1": "La cuenta 9 − 4 está bien. Mira la segunda frase.",
                "n2": "«No quedó ninguna» es una cantidad, y las cantidades se escriben.",
                "n3": "Ninguna paloma = 0 palomas, y 0 va grabado en la tablilla.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? $0\in\mathbb{N}$ y además $0$ cuenta algo.",
            "options": [
                {"id": "true_counts", "text": "Verdadera: 0 es natural y cuenta el montón vacío"},
                {"id": "false_nothing", "text": "Falsa: 0 no es un número, es que no hay nada"},
                {"id": "false_starts_one", "text": "Falsa: los naturales empiezan en 1"},
                {"id": "true_but_empty", "text": "Verdadera que es natural, pero 0 no cuenta nada"},
            ],
            "expected": "true_counts",
            "feedback_by_option": {
                "true_counts": "correct",
                "false_nothing": "fb_b04_e5_nothing",
                "false_starts_one": "fb_b04_e5_startsone",
                "true_but_empty": "fb_b04_e5_empty",
            },
            "misconception_by_option": {
                "false_nothing": "cero_no_es_numero",
                "false_starts_one": "convencion_sin_cero",
                "true_but_empty": "cero_no_es_numero",
            },
            "hints": {
                "n1": "Si el 0 no fuera un número, ¿cómo escribirías el resultado del censo del puesto vacío?",
                "n2": "«Ninguno» es una respuesta a «¿cuántos hay?», y las respuestas a esa pregunta son naturales.",
                "n3": "En este curso ℕ = {0, 1, 2, 3, …}: el 0 entra, y cuenta el montón vacío.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El arconte pide que el censo permita sumar y restar libremente. KatIA "
                "solo tiene naturales. ¿Qué encargo NO va a poder cumplir?"
            ),
            "options": [
                {
                    "id": "debt",
                    "text": "Anotar cuánto DEBE un puesto que gastó más de lo que tenía",
                },
                {"id": "total", "text": "Sumar todos los puestos para dar un total"},
                {"id": "empty", "text": "Registrar un puesto vacío"},
                {"id": "compare", "text": "Decir cuál puesto tiene más mercancía"},
            ],
            "expected": "debt",
            "feedback_by_option": {
                "debt": "correct",
                "total": "fb_b04_e6_closed",
                "empty": "fb_b04_e6_empty",
                "compare": "fb_b04_e6_closed",
            },
            "misconception_by_option": {
                "total": "cree_naturales_insuficientes_para_sumar",
                "empty": "cero_no_es_numero",
                "compare": "cree_naturales_no_ordenados",
            },
            "hints": {
                "n1": "Tres de los cuatro encargos ya los resolviste en este nodo.",
                "n2": "Piensa en el discípulo que prestó 5 cinceles teniendo 3.",
                "n3": "Deber lleva a un resultado por debajo de 0, y ahí no hay naturales.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas restas SÍ tiene resultado dentro de los naturales?",
            "options": [
                {"id": "ok", "text": "20 − 20", "latex": r"20-20"},
                {"id": "neg_small", "text": "7 − 9", "latex": r"7-9"},
                {"id": "neg_big", "text": "1 − 100", "latex": r"1-100"},
                {"id": "neg_one", "text": "0 − 1", "latex": r"0-1"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "neg_small": "fb_b04_e7_negative",
                "neg_big": "fb_b04_e7_negative",
                "neg_one": "fb_b04_e7_negative",
            },
            "misconception_by_option": {
                "neg_small": "resta_siempre_cabe",
                "neg_big": "resta_siempre_cabe",
                "neg_one": "resta_siempre_cabe",
            },
            "hints": {
                "n1": "Haz cada resta y mira si el resultado está en {0, 1, 2, 3, …}.",
                "n2": "Si el número de la izquierda es menor, te vas por debajo del 0.",
                "n3": "20 − 20 = 0, y 0 sí es natural. Las otras tres se salen.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "La escalera de la necesidad",
        "title": "¿Toda resta de dos números del conjunto vive en el conjunto?",
        "intro": "Cada peldaño nace de una operación que no cabía en el anterior. Este es el primero.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"3-5\notin\mathbb{N}",
                "note": "Se sale: no hay natural por debajo del 0.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "yes",
                "latex": r"3-5=-2\in\mathbb{Z}",
                "note": "El siguiente peldaño nace exactamente de esto.",
            },
        ],
        "outro": (
            "Sumar y multiplicar naturales siempre da un natural. Restar, no. Ese único "
            "agujero es el que abre B05: los enteros no se inventaron por gusto, se "
            "inventaron para que la resta siempre tenga respuesta."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué tienen en común los tres momentos en que KatIA no pudo grabar un natural?",
        "thumbnails": [r"3-5", r"7-9", r"0-1"],
        "options": [
            {
                "id": "below_zero",
                "text": "En los tres el resultado queda por debajo de 0",
                "correct": True,
            },
            {
                "id": "subtraction",
                "text": "Los tres son restas donde se quita más de lo que hay",
                "correct": True,
            },
            {
                "id": "zero",
                "text": "Los tres tienen que ver con que el 0 no es natural",
                "correct": False,
            },
            {"id": "big", "text": "Los tres usan números demasiado grandes", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El festival necesita 50 antorchas. En el almacén hay 4 repisas con 9 "
            "antorchas cada una, y una quinta repisa vacía. ¿Cuántas antorchas faltan?"
        ),
        "polya": {
            "comprender": (
                "Me dan 4 repisas de 9 y una repisa vacía; hacen falta 50. Me piden "
                "cuántas faltan."
            ),
            "planear": (
                "Cuento lo disponible agrupando (4 × 9), sumo la repisa vacía como 0, y "
                "resto del total necesario."
            ),
            "ejecutar": "4 × 9 = 36 → 36 + 0 = 36 → 50 − 36 = 14.",
            "comprobar": (
                "36 + 14 = 50. ✓ Y la repisa vacía sí entró en la cuenta: aportó 0, que "
                "no es lo mismo que no haberla mirado."
            ),
        },
        "prompt": "¿Cuántas antorchas faltan?",
        "answer": "14",
        "hints": {
            "n1": "Primero averigua cuántas antorchas hay en total.",
            "n2": "4 repisas de 9, más una repisa que aporta 0.",
            "n3": "Hay 36. Ahora resta: 50 − 36.",
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
            "entre «cero» y «casilla en blanco»."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "En una repisa hay 7 lámparas y en la de al lado hay 6. ¿Cuántas hay en total?",
                "answer": "13",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Un anaquel quedó sin una sola jarra. ¿Qué se anota en su casilla?",
                "options": [
                    {"id": "zero", "text": "Se anota 0", "latex": r"0"},
                    {"id": "blank", "text": "Se deja en blanco"},
                    {"id": "dash", "text": "Se pone una raya para indicar que no aplica"},
                ],
                "expected": "zero",
                "misconception_by_option": {
                    "blank": "cero_no_es_numero",
                    "dash": "cero_no_es_numero",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál de estas operaciones SIEMPRE da un natural si empiezas con naturales?",
                "options": [
                    {"id": "sum", "text": "Sumar", "latex": r"a+b"},
                    {"id": "sub", "text": "Restar", "latex": r"a-b"},
                    {"id": "both", "text": "Las dos"},
                ],
                # Variante inversa del D3, a propósito: comprueba que aprendió
                # el criterio de cierre y no la heurística "restar está prohibido".
                "expected": "sum",
                "misconception_by_option": {
                    "sub": "confunde_operacion",
                    "both": "resta_siempre_cabe",
                },
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
        "fb_b04_e3_zero": (
            "«Ninguna paloma» sí tiene número, y es 0. Cero es natural y responde "
            "«¿cuántas hay?». → Busca la opción que hable de una PARTE de un objeto."
        ),
        "fb_b04_e3_whole": (
            "Ese sí se escribe con un natural: 12 y 100 cuentan objetos completos. Ser "
            "grande no lo saca del conjunto. → Busca la que no cuenta objetos enteros."
        ),
        "fb_b04_e4_subtraction": (
            "La resta está bien: 9 − 4 = 5. El fallo está en la otra frase, la del "
            "tejado sin palomas. → Di qué debía escribir en esa casilla."
        ),
        "fb_b04_e4_add": (
            "Si volaron, se van: restar es lo correcto. El error está en la casilla que "
            "dejó vacía. → Vuelve a leer la segunda frase."
        ),
        "fb_b04_e4_none": (
            "Casi: la cuenta está bien, pero dejar la casilla en blanco borra información. "
            "→ Responde qué diferencia hay entre un 0 y un blanco en el censo."
        ),
        "fb_b04_e5_nothing": (
            "Si 0 no fuera número, el censo del puesto vacío no se podría escribir, y sí "
            "se puede. → Escribe cuántas monedas tiene un cofre vacío."
        ),
        "fb_b04_e5_startsone": (
            "Hay cursos donde ℕ empieza en 1; en este empieza en 0, y lo decimos de "
            "frente. → Vuelve a la definición y mira el primer elemento del conjunto."
        ),
        "fb_b04_e5_empty": (
            "Sí cuenta algo: cuenta el montón vacío. Decir «hay 0 jarras» es un dato tan "
            "bueno como «hay 7». → Di qué información pierde el arconte si borras ese 0."
        ),
        "fb_b04_e6_closed": (
            "Eso sí lo puede hacer con naturales: sumar y comparar nunca la sacan del "
            "conjunto. → Busca el encargo que la obliga a bajar del 0."
        ),
        "fb_b04_e6_empty": (
            "Registrar un puesto vacío es justo lo que aprendiste a hacer: se escribe 0. "
            "→ Busca el encargo que ningún natural puede escribir."
        ),
        "fb_b04_e7_negative": (
            "Haz la resta y ubica el resultado: queda por debajo del 0, y ahí no hay "
            "naturales. → Busca la resta cuyo resultado caiga en {0, 1, 2, 3, …}."
        ),
    },
    "closing": (
        "Contar alcanza para lo que hay. No alcanza para lo que se debe. En el siguiente "
        "nodo vas a bajar del cero por primera vez."
    ),
    "validation_status": "F1_B04_11bloques",
}
