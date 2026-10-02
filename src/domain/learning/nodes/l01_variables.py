"""L01 · La sala de los cálamos — la letra es una cantidad, no una etiqueta.

Primer nodo del módulo de Álgebra (ALG-N1, «El Papiro de las Cuatro Casas»).
Casa de la Vida (Per-Ankh), en Kemet. Personaje guía: Meritka, la custodia del
papiro. Vocabulario propio del espacio: papiro, cálamo, tinta, estante, sello,
rollo, escriba, registro, lámpara, tablilla — nada de cantera, parcela ni taller.

Nodo piloto del nivel: se valida antes de replicar B02–B04.
"""

NODE_ID = "ALG-N1-L01-VARIABLES"
CONCEPT_SLUG = "variables"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "variables",
    "misconception": "variable_como_etiqueta",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La sala de los cálamos · Variables",
    "house": "La sala de los cálamos",
    "guide": "Meritka",
    "finish_label": "Pasar al estante sellado",
    "title": "Una letra no nombra la cosa: cuenta cuántas hay",
    "intro": (
        "Hasta ahora cada registro servía para un solo día. Aquí aprendes a escribir uno "
        "que sirva para todos: una regla que no necesita saber de antemano cuántos "
        "trabajadores llegarán."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar. No se califican: solo quiero ver desde dónde partimos.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Cada escriba recibe 3 panes. ¿Cuántos panes se necesitan para 4 escribas?",
                "answer": "12",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $2\cdot(3+4)$?",
                "options": [
                    {"id": "fourteen", "text": "14", "latex": r"14"},
                    {"id": "ten", "text": "10", "latex": r"10"},
                    {"id": "twentyfour", "text": "24", "latex": r"24"},
                ],
                "expected": "fourteen",
                "misconception_by_option": {
                    "ten": "multiplica_solo_el_primer_sumando",
                    "twentyfour": "pega_los_digitos_en_vez_de_operar",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": (
                    "El número de trabajadores cambia cada día. ¿Qué usarías para escribir "
                    "UNA regla que sirva para cualquier día?"
                ),
                "options": [
                    {"id": "letter", "text": "Un símbolo que ocupe el lugar de esa cantidad"},
                    {"id": "many", "text": "Un registro distinto para cada día"},
                    {"id": "blank", "text": "Dejar el espacio en blanco y rellenarlo a mano"},
                ],
                "expected": "letter",
                "misconception_by_option": {
                    "many": "no_generaliza_enumera",
                    "blank": "no_generaliza_enumera",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/l01-variables-katia.png",
        "eyebrow": "KatIA · En la Casa de la Vida",
        "title": "El papiro que se repetía a sí mismo",
        "body": (
            "Meritka abre un estante entero de registros. En cada rollo está escrita la "
            "misma instrucción: «tres panes por trabajador». Solo cambia el número del "
            "final: veintiuno un día, treinta el siguiente, dieciocho el otro.\n\n"
            "«Un rollo por día», dice Meritka. «Y el rollo que se perdió con la crecida "
            "era el único que no tenía número: el que servía para todos. Ese es el que "
            "hay que volver a escribir, y no sé cómo se escribe una cantidad que "
            "todavía no ha llegado.»"
        ),
        "question": "¿Cómo se escribe una regla cuando aún no sabes la cantidad?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Escribiendo todos los casos posibles"},
                {"id": "b", "text": "Dejando un hueco en blanco"},
                {"id": "c", "text": "Poniendo un símbolo en el lugar de la cantidad"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder escribir el rollo "
                "perdido y explicar qué significa exactamente cada signo que pongas."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos registros para la misma instrucción",
        "body": (
            "Los dos dicen «tres panes por trabajador». Fíjate en cuál de los dos sigue "
            "sirviendo mañana."
        ),
        "cases": [
            {
                "label": "El registro de ayer",
                "context": "Ayer llegaron 4 trabajadores",
                "fraction": r"3\cdot 4 = 12",
                "division": r"\text{sirve para el día en que se escribió}",
                "note": "Exacto y verdadero. Pero mañana no llegan cuatro, y el rollo ya no vale.",
            },
            {
                "label": "El rollo perdido",
                "context": "Lleguen los que lleguen",
                "fraction": r"3n",
                "division": r"n=4\to 12,\quad n=7\to 21,\quad n=10\to 30",
                "note": "Un solo rollo cubre todos los días. La n espera a que le digan cuánto vale.",
            },
        ],
        "resolution": (
            "La letra no abrevia la palabra «trabajador»: ocupa el lugar del NÚMERO de "
            "trabajadores. Por eso 3n se puede calcular en cuanto alguien diga cuántos "
            "llegaron, y por eso el mismo rollo sirve para todos los días del año."
        ),
    },
    "definition_title": "Variable, término y expresión",
    "definition_katex": r"3n \;=\; \underbrace{3}_{\text{coeficiente}}\cdot\underbrace{n}_{\text{variable}}",
    "definition": (
        "Una VARIABLE es un símbolo que ocupa el lugar de un número: uno que cambia o uno "
        "que todavía no conocemos. Una CONSTANTE es un valor que no cambia. Un TÉRMINO es "
        "cada parte separada por + o por −, y una EXPRESIÓN ALGEBRAICA combina números, "
        "variables y operaciones sin afirmar todavía ninguna igualdad."
    ),
    "definition_symbols": [
        {"symbol": r"n", "reads": "ene", "means": "la variable: el número de trabajadores, no la palabra «trabajador»"},
        {"symbol": r"3n", "reads": "tres ene", "means": "quiere decir 3 · n, un producto — nunca 3 + n"},
        {"symbol": r"3", "reads": "tres", "means": "el coeficiente: el número que multiplica a la variable"},
        {"symbol": r"2c+1", "reads": "dos ce más uno", "means": "dos términos; el 1 es una constante, no lleva letra"},
        {"symbol": r"n\in\mathbb{N},\ n>0", "reads": "ene natural positivo", "means": "en este registro n cuenta personas: no admite 2,5 ni −3"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · En los estantes",
            "title": "Cuando parte de la cantidad sí se conoce",
            "statement": (
                "Cada estante de la sala guarda la misma cantidad de rollos, que varía según "
                "el estante, y además hay 2 rollos de consulta fuera del estante. Escribe "
                "cuántos rollos hay en total por estante."
            ),
            "latex": r"r+2",
            "image_slot": False,
            "steps": [
                "Lo que cambia de un estante a otro: la cantidad de rollos guardados. La llamo r.",
                "Lo que no cambia: los 2 rollos de consulta. Ese 2 es una constante.",
                "Los junto con una suma, porque hay que contarlos todos: r + 2.",
                "Compruebo con un caso: si el estante guarda 9 rollos, r = 9 y el total es 11.",
                "La expresión tiene dos términos: r y 2. El primero lleva letra; el segundo no.",
            ],
            "solution": r"$r+2$ rollos, donde $r$ es el número de rollos guardados",
            "self_explanation": {
                "step_index": 1,
                "prompt": "¿Por qué el 2 no lleva letra y la otra cantidad sí?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · En la mesa de la tinta",
            "title": "Un coeficiente y una constante en la misma regla",
            "statement": (
                "Cada copista gasta 2 medidas de tinta en su jornada, y aparte se reserva "
                "1 medida para corregir los errores del día. Escribe la tinta que hay que "
                "preparar."
            ),
            "latex": r"2c+1",
            "image_slot": False,
            "steps": [
                "La cantidad que cambia es el número de copistas: la llamo c.",
                "Cada uno gasta 2 medidas, así que ese gasto es 2 · c, que se escribe 2c.",
                "La medida de correcciones es siempre 1, llegue quien llegue: es constante.",
                "Total: 2c + 1. El 2 es el coeficiente de c; el 1 es el término constante.",
                "Compruebo: con 6 copistas hacen falta 2 · 6 + 1 = 13 medidas.",
            ],
            "solution": r"$2c+1$ medidas de tinta",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que leyó la letra como una palabra",
            "statement": (
                "Un aprendiz lee el registro y explica: «2c son dos copistas, porque la c "
                "es de copista. Y r + 2 son un rollo y dos rollos, o sea tres rollos»."
            ),
            "latex": r"2c \ne \text{«dos copistas»}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"c=\text{«copista»}\quad\text{en vez de}\quad c=\text{cuántos copistas}",
            "error_note": (
                "Si la letra fuera la palabra, 2c no se podría calcular nunca — y el "
                "aprendiz acaba de calcularlo mal dos veces."
            ),
            "correct_version": {
                "wrong_latex": r"2c=\text{dos copistas}",
                "right_latex": r"c=7\Rightarrow 2c=14",
                "rows": [
                    {"wrong": "La c abrevia la palabra «copista»",
                     "right": "La c es CUÁNTOS copistas hay: un número"},
                    {"wrong": "En r + 2 la r vale 1 porque es un rollo",
                     "right": "La r vale lo que valga ese estante; no se sabe hasta que se cuenta"},
                ],
            },
            "explain_prompt": (
                "Explica por qué la letra no funciona como abreviatura y di cuánto valen "
                "2c y r + 2 si hay 7 copistas y el estante guarda 9 rollos."
            ),
            "steps": [
                "Prueba a sustituir: si c = 7, entonces 2c = 14 medidas. La lectura del aprendiz no permite sustituir nada.",
                "En r + 2, la r no vale 1: vale lo que se cuente en ese estante. Con r = 9 el total es 11.",
                "Regla para no volver a caer: antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?».",
            ],
            "solution": (
                "La letra siempre ocupa el lugar de un número. La palabra que empieza por "
                "esa letra es solo una ayuda para recordar de qué cantidad hablamos."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La regla ya va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": (
                    "Cada escriba recibe 5 medidas de papiro. Si hay s escribas, la "
                    "expresión es 5s. ¿Cuántas medidas hacen falta si llegan 8 escribas?"
                ),
                "given_steps": [
                    r"5s\quad\text{con } s=8",
                    r"5\cdot 8",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"5s=", "answer": "40"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "En la sala hay 4 lámparas fijas y una lámpara más por cada mesa. "
                    "Con m mesas, la expresión es m + 4. Complétala para 6 mesas."
                ),
                "given_steps": [
                    r"m+4\quad\text{con } m=6",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"m=", "answer": "6"},
                    {"id": "P2-b2", "label": r"m+4=", "answer": "10"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: la sala tiene el doble de lámparas que de mesas, "
                    "y además 3 lámparas en la entrada. Si hay 7 mesas, ¿cuántas lámparas hay?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"2m+3=", "answer": "17"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    # No se comparan dos formas de traducir, sino dos formas de COMPROBAR que la
    # traducción es correcta. El segundo método obliga a sustituir un número, que
    # es justo lo que la misconception focal impide hacer.
    "method_comparison": {
        "title": "Dos maneras de comprobar una traducción",
        "intro": (
            "«El triple de un número, menos 4». Las dos comprobaciones de abajo son "
            "correctas y llevan a la misma expresión."
        ),
        "methods": [
            {
                "label": "Método 1 · Leer la frase por partes",
                "steps": [
                    r"\text{«el triple de un número»}\to 3x",
                    r"\text{«menos 4»}\to -4",
                    r"3x-4",
                ],
                "note": "Rápido, pero se rompe si la frase agrupa (ahí hace falta paréntesis).",
            },
            {
                "label": "Método 2 · Probar con un número",
                "steps": [
                    r"\text{con } x=10:\ \text{el triple es }30,\ \text{menos }4\to 26",
                    r"3\cdot 10-4=26",
                    r"\text{coinciden}\Rightarrow 3x-4",
                ],
                "note": "Más lento, pero detecta el error aunque la frase sea enredada.",
            },
        ],
        "question": "¿Cuál de los dos te salva cuando la frase dice «el doble de la suma de un número y 3»?",
        "insight": (
            "El segundo. Leer por partes daría 2x + 3, pero al probar con x = 5 la frase "
            "da 16 y 2x + 3 da 13: no coinciden, así que hace falta el paréntesis, 2(x+3). "
            "Y fíjate en lo que exige sustituir: tratar la letra como un número. Si la "
            "lees como una palabra, este método no se puede ni empezar."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "«El doble de un número, más 3». ¿Qué expresión lo dice?",
            "options": [
                {"id": "correct", "text": r"$2x+3$", "latex": r"2x+3"},
                {"id": "grouped", "text": r"$2(x+3)$", "latex": r"2(x+3)"},
                {"id": "swapped", "text": r"$3x+2$", "latex": r"3x+2"},
                {"id": "product", "text": r"$2x\cdot 3$", "latex": r"2x\cdot 3"},
            ],
            "expected": "correct",
            "feedback_by_option": {
                "correct": "correct",
                "grouped": "fb_a01_e1_grouped",
                "swapped": "fb_a01_e1_swapped",
                "product": "fb_a01_e1_product",
            },
            "misconception_by_option": {
                "grouped": "agrupa_lo_que_la_frase_no_agrupa",
                "swapped": "invierte_coeficiente_y_constante",
                "product": "confunde_mas_con_por",
            },
            "hints": {
                "n1": "¿Qué se duplica: el número solo, o el número ya sumado con 3?",
                "n2": "La frase dobla primero y suma después. El paréntesis haría lo contrario.",
                "n3": "El doble de x es 2x. Ahora añádele 3.",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"En la expresión $5m-4$, ¿cuál es el coeficiente?",
            "options": [
                {"id": "five", "text": "5", "latex": r"5"},
                {"id": "minusfour", "text": "−4", "latex": r"-4"},
                {"id": "m", "text": "m", "latex": r"m"},
                {"id": "four", "text": "4", "latex": r"4"},
            ],
            "expected": "five",
            "feedback_by_option": {
                "five": "correct",
                "minusfour": "fb_a01_e2_constant",
                "m": "fb_a01_e2_variable",
                "four": "fb_a01_e2_constant",
            },
            "misconception_by_option": {
                "minusfour": "confunde_coeficiente_con_constante",
                "m": "confunde_coeficiente_con_variable",
                "four": "confunde_coeficiente_con_constante",
            },
            "hints": {
                "n1": "El coeficiente es el número que MULTIPLICA a una letra.",
                "n2": "El −4 no multiplica a nada: está sumado (restado) aparte.",
                "n3": "¿Qué número está pegado a la m?",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "La tinta de la jornada se calcula con 2c + 1, donde c es el número de "
                "copistas. ¿Cuántas medidas hacen falta si vienen 6 copistas?"
            ),
            "expr": r"2c+1,\quad c=6",
            "answer": "13",
            "hints": {
                "n1": "Sustituye c por 6 y calcula.",
                "n2": "Primero el producto 2 · 6, después la suma.",
                "n3": "12 + 1 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Para «el triple de un número» un escriba anota 3 + x. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "sum_vs_product", "text": "«Triple» es multiplicar por 3, no sumar 3: se escribe 3x"},
                {"id": "order", "text": "Está bien el signo, solo cambió el orden: debería ser x + 3"},
                {"id": "letter", "text": "El error es la letra: debería usar t de «triple»"},
                {"id": "none", "text": "No hay error, 3 + x es el triple de x"},
            ],
            "expected": "sum_vs_product",
            "feedback_by_option": {
                "sum_vs_product": "correct",
                "order": "fb_a01_e4_order",
                "letter": "fb_a01_e4_letter",
                "none": "fb_a01_e4_none",
            },
            "misconception_by_option": {
                "order": "confunde_mas_con_por",
                "letter": "variable_como_etiqueta",
                "none": "confunde_mas_con_por",
            },
            "hints": {
                "n1": "Prueba con un número: el triple de 10, ¿es 13?",
                "n2": "Triplicar es repetir tres veces, y repetir es multiplicar.",
                "n3": "El triple de x se escribe 3 · x, es decir 3x.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"En el registro $4t$, la $t$ está por «tablilla». ¿Qué representa exactamente la $t$?",
            "options": [
                {"id": "count", "text": "El número de tablillas, una cantidad que puede cambiar"},
                {"id": "label", "text": "La palabra «tablilla»: 4t son cuatro tablillas"},
                {"id": "unit", "text": "La unidad de medida en que se cuentan las tablillas"},
                {"id": "fixed", "text": "Un número fijo que ya está decidido de antemano"},
            ],
            "expected": "count",
            "feedback_by_option": {
                "count": "correct",
                "label": "fb_a01_e5_trap",
                "unit": "fb_a01_e5_unit",
                "fixed": "fb_a01_e5_fixed",
            },
            "misconception_by_option": {
                "label": "variable_como_etiqueta",
                "unit": "variable_como_etiqueta",
                "fixed": "confunde_variable_con_constante",
            },
            "hints": {
                "n1": "Pregúntate «¿cuántos?», no «¿qué cosa?».",
                "n2": "Si la t fuera la palabra, no podrías calcular 4t nunca.",
                "n3": "Con 9 tablillas, t = 9 y 4t = 36. La letra guarda el número.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODAS las que son expresiones algebraicas (no ecuaciones).",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$3x+5$", "latex": r"3x+5"},
                {"id": "b", "text": r"$2x+3=7$", "latex": r"2x+3=7"},
                {"id": "c", "text": r"$r-2$", "latex": r"r-2"},
                {"id": "d", "text": r"$A=b\cdot h$", "latex": r"A=b\cdot h"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Una expresión describe una cantidad; una ecuación AFIRMA una igualdad.",
                "n2": "Busca el signo igual: si está, ya no es solo una expresión.",
                "n3": "3x + 5 y r − 2 no afirman nada; las otras dos sí.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Un rollo de papiro mide L codos. Antes de escribirlo se recorta un borde "
                "de 2 codos en cada extremo. Si el rollo medía 15 codos, ¿cuántos codos "
                "quedan para escribir?"
            ),
            "expr": r"L-4,\quad L=15",
            "answer": "11",
            "hints": {
                "n1": "Se recorta en los DOS extremos: ¿cuánto se pierde en total?",
                "n2": "La expresión es L − 4, no L − 2.",
                "n3": "15 − 4 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    # Nivel nuevo: el cierre NO copia la escalera de conjuntos. El eje aquí es el
    # que gobierna todo el nodo: ¿este símbolo guarda un valor que cambia o no?
    "closure": {
        "eyebrow": "¿Cambia o no cambia?",
        "title": "Qué guarda cada símbolo de una expresión",
        "intro": (
            "Ser una letra no convierte a un símbolo en variable, y ser un número no lo "
            "convierte en constante. Lo que decide es si su valor puede cambiar."
        ),
        "rows": [
            {"symbol": r"n\ \text{en}\ 3n", "name": "La variable", "closed": "yes",
             "latex": r"n=4,\ 7,\ 10\ldots",
             "note": "Cambia cada día. Es justo lo que el rollo perdido no podía fijar."},
            {"symbol": r"3\ \text{en}\ 3n", "name": "El coeficiente", "closed": "no",
             "latex": r"3\cdot n",
             "note": "Siempre tres panes por trabajador. Multiplica a la variable, pero no varía."},
            {"symbol": r"2\ \text{en}\ r+2", "name": "El término constante", "closed": "no",
             "latex": r"r+2",
             "note": "Los dos rollos de consulta están siempre, haya los que haya en el estante."},
            {"symbol": r"\pi\ \text{en}\ 2\pi r", "name": "Una letra que NO varía", "closed": "no",
             "latex": r"\pi\approx 3{,}1416",
             "note": "Es letra y aun así es constante. Aquí la que cambia es la r."},
            {"symbol": r"x\ \text{en}\ 2x+3=7", "name": "La incógnita", "closed": "partial",
             "latex": r"x=2",
             "note": "No cambia libremente: hay un único valor que hace cierta la igualdad, y aún no lo sabemos."},
            {"symbol": r"b,h\ \text{en}\ A=b\cdot h", "name": "Dos variables a la vez", "closed": "yes",
             "latex": r"A=b\cdot h",
             "note": "Cambian con cada rectángulo, y A cambia con ellas."},
        ],
        "outro": (
            "La pregunta útil nunca es «¿es letra o es número?», sino «¿su valor puede "
            "cambiar?». Una constante puede escribirse con letra (π) y una incógnita es "
            "un caso intermedio: fija, pero todavía desconocida."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten las tres expresiones trabajadas en este nodo?",
        "thumbnails": [r"3n", r"r+2", r"2c+1"],
        "options": [
            {"id": "part_changes", "text": "En las tres hay una parte que cambia y otra que se queda fija", "correct": True},
            {"id": "computable", "text": "En las tres se puede calcular el total en cuanto se sabe el valor de la letra", "correct": True},
            {"id": "equal", "text": "En las tres se afirma una igualdad entre dos cantidades", "correct": False},
            {"id": "initial", "text": "En las tres la letra es la inicial de la palabra que representa", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El rollo que hay que reponer: en la Casa de la Vida se entregan 3 medidas de "
            "papiro a cada escriba, y además se apartan 5 medidas para el archivo. Hoy han "
            "llegado 12 escribas. ¿Cuántas medidas de papiro hay que sacar del almacén?"
        ),
        "polya": {
            "comprender": "Hay una cantidad que cambia (los escribas) y una que no (las 5 del archivo).",
            "planear": "Escribo la regla general primero: 3e + 5, con e el número de escribas. Después sustituyo.",
            "ejecutar": "Con e = 12: 3 · 12 + 5 = 36 + 5 = 41.",
            "comprobar": "Sin la regla: 12 escribas × 3 = 36, más 5 del archivo = 41 ✓. Y si mañana llegan 20, el mismo rollo sirve: 3 · 20 + 5 = 65.",
        },
        "prompt": "¿Cuántas medidas hay que sacar?",
        "answer": "41",
        "hints": {
            "n1": "Escribe primero la regla con letra, y sustituye al final.",
            "n2": "3e + 5, con e = 12.",
            "n3": "36 + 5 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros datos. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya lees la letra como una cantidad y no como una palabra.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué guarda una "
            "letra dentro de una expresión."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": (
                    "Cada estante guarda 6 rollos. ¿Cuántos rollos hay en 5 estantes iguales?"
                ),
                "answer": "30",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"Si $p$ es el número de panes, ¿qué significa $4p$?",
                "options": [
                    {"id": "quadruple", "text": "Cuatro veces esa cantidad de panes"},
                    {"id": "four_breads", "text": "Cuatro panes"},
                    {"id": "sum", "text": "Cuatro más esa cantidad de panes"},
                ],
                "expected": "quadruple",
                "misconception_by_option": {
                    "four_breads": "variable_como_etiqueta",
                    "sum": "confunde_mas_con_por",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $7k+2$, ¿cuál es el término constante?",
                "options": [
                    {"id": "two", "text": "2", "latex": r"2"},
                    {"id": "seven", "text": "7", "latex": r"7"},
                    {"id": "k", "text": "k", "latex": r"k"},
                ],
                "expected": "two",
                "misconception_by_option": {
                    "seven": "confunde_coeficiente_con_constante",
                    "k": "confunde_coeficiente_con_variable",
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
        "default": "Antes de leer una letra, pregúntate «¿cuántos?», no «¿qué cosa?».",
        "fb_a01_e1_grouped": (
            "El paréntesis suma primero y dobla después: 2(x+3) es «el doble de la suma». "
            "→ Prueba las dos con x = 5 y compara."
        ),
        "fb_a01_e1_swapped": (
            "Ahí el 3 multiplica y el 2 se suma, justo al revés. → Vuelve a leer la frase "
            "marcando qué número acompaña a «doble»."
        ),
        "fb_a01_e1_product": (
            "«Más 3» es una suma, no un producto. → Sustituye la palabra «más» por su signo."
        ),
        "fb_a01_e2_constant": (
            "Ese número está restado aparte: no multiplica a ninguna letra. → Busca el que "
            "está pegado a la m."
        ),
        "fb_a01_e2_variable": (
            "La m es la variable, no el coeficiente. → El coeficiente es el NÚMERO que la "
            "multiplica."
        ),
        "fb_a01_e4_order": (
            "El orden no es el problema: x + 3 sigue siendo una suma. → Calcula el triple "
            "de 10 y compáralo con 3 + 10."
        ),
        "fb_a01_e4_letter": (
            "La letra elegida da igual: x, t o n valen lo mismo. → El error está en la "
            "operación, no en el nombre."
        ),
        "fb_a01_e4_none": (
            "Con x = 10, 3 + x da 13 y el triple es 30. → Escribe la operación que repite "
            "el número tres veces."
        ),
        "fb_a01_e5_trap": (
            "Si la t fuera la palabra, 4t no se podría calcular. → Con 9 tablillas, ¿cuánto "
            "vale 4t?"
        ),
        "fb_a01_e5_unit": (
            "Las unidades no se guardan en la letra: la letra guarda el número. → ¿Qué "
            "número pondrías en su lugar?"
        ),
        "fb_a01_e5_fixed": (
            "Si estuviera decidido de antemano sería una constante y no haría falta letra. "
            "→ Piensa si el número de tablillas puede cambiar de un día a otro."
        ),
    },
    "closing": (
        "Ya puedes escribir el rollo perdido: una sola regla que sirve para cualquier "
        "cantidad. Pero en el mismo rollo hay números que NUNCA cambian, y todavía no "
        "sabes distinguirlos de un vistazo. Meritka abre el estante sellado."
    ),
    "validation_status": "F5_L01_pilot",
}
