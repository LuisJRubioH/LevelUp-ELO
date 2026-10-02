"""O01 · La rampa — solo se juntan las cargas del mismo tipo.

Primera sala de la obra de la pirámide. Guía: Bakenra, el que organiza las cuadrillas.
Vocabulario propio: rampa, cuerda, trineo, bloque, cuadrilla, turno, carga,
herramienta, mazo. Nada de poleas ni vales (O02), cinceles (O03) ni agua (O04).

La obra NO reduce el álgebra a contar bloques: los ejemplos van por cuerdas,
herramientas y turnos, y el bloque aparece una sola vez.
"""

NODE_ID = "ALG-N1-O01-SEMEJANTES"
CONCEPT_SLUG = "terminos_semejantes"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "terminos_semejantes",
    "misconception": "combina_no_semejantes",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La rampa · Términos semejantes",
    "house": "La rampa",
    "guide": "Bakenra",
    "finish_label": "Bajar al patio de aparejos",
    "title": "Un registro más corto sin mezclar lo que no se mezcla",
    "intro": (
        "Ya sabes escribir una cantidad que cambia. Ahora llegan dos registros a la vez y "
        "hay que dejarlos en uno solo — pero acortar no es amontonar: hay cantidades que "
        "no se pueden juntar por mucho que estén en la misma línea."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de subir a la rampa. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": (
                    "Una cuadrilla arrastra 7 trineos por turno. ¿Cuántos trineos arrastra "
                    "en 3 turnos?"
                ),
                "answer": "21",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuántos términos tiene $3x+4$?",
                "options": [
                    {"id": "two", "text": "2"},
                    {"id": "three", "text": "3"},
                    {"id": "one", "text": "1"},
                ],
                "expected": "two",
                "misconception_by_option": {
                    "three": "cuenta_simbolos_no_terminos",
                    "one": "no_separa_por_los_signos",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Se puede escribir $2x+3y$ como un solo término?",
                "options": [
                    {"id": "no", "text": "No: son cantidades de tipos distintos"},
                    {"id": "yes_sum", "text": r"Sí: $5xy$"},
                    {"id": "yes_num", "text": r"Sí: $5$"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes_sum": "combina_no_semejantes",
                    "yes_num": "combina_no_semejantes",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/o01-semejantes-katia.png",
        "eyebrow": "KatIA · Al pie de la rampa",
        "title": "Los dos registros del capataz",
        "body": (
            "Bakenra tiene dos tablillas de turno delante y una cuadrilla esperando "
            "instrucciones. La primera anota lo que se sacó del almacén por la mañana; la "
            "segunda, lo de la tarde. Las dos usan letras: c para las cuerdas que se "
            "gastan, h para las herramientas.\n\n"
            "«Necesito una sola lista», dice Bakenra, «o la cuadrilla va a bajar dos veces "
            "al almacén. Pero el escriba de ayer me juntó las cuerdas con las herramientas "
            "y subieron con la mitad de lo que hacía falta.»"
        ),
        "question": "¿Qué se puede juntar en un registro y qué tiene que seguir separado?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Todo lo que esté sumado se puede juntar"},
                {"id": "b", "text": "Solo lo que sea del mismo tipo"},
                {"id": "c", "text": "Nada: hay que dejar las dos tablillas"},
            ],
            "response": (
                "Probemos esa idea. Guarda tu respuesta: al final vas a poder decir la regla "
                "exacta que decide si dos cantidades se juntan."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos sumas que parecen iguales y no lo son",
        "body": "Las dos tienen la misma forma escrita. Solo una se puede acortar.",
        "cases": [
            {
                "label": "Se juntan",
                "context": "Cuerdas por la mañana y cuerdas por la tarde",
                "fraction": r"3c+2c=5c",
                "division": r"(3+2)\cdot c",
                "note": "Es la misma cantidad contada dos veces: 3 veces c más 2 veces c son 5 veces c.",
            },
            {
                "label": "No se juntan",
                "context": "Cuerdas por la mañana y herramientas por la tarde",
                "fraction": r"3c+2h",
                "division": r"\text{se queda así}",
                "note": "No hay ningún número que sea «cuerdas y herramientas a la vez». La suma queda indicada.",
            },
        ],
        "resolution": (
            "Lo que permite acortar no es que estén sumados, sino que la parte con letras "
            "sea EXACTAMENTE la misma. Cuando lo es, la distributiva saca esa parte fuera "
            "y solo quedan los coeficientes sumándose. Cuando no lo es, no hay nada que sacar."
        ),
    },
    "definition_title": "Términos semejantes",
    "definition_katex": r"ac+bc=(a+b)\,c",
    "definition": (
        "Dos términos son SEMEJANTES cuando tienen exactamente la misma parte literal: las "
        "mismas letras elevadas a los mismos exponentes. Para sumarlos o restarlos se "
        "operan los coeficientes y la parte literal se conserva intacta. Los términos "
        "constantes son semejantes entre sí."
    ),
    "definition_symbols": [
        {"symbol": r"3c", "reads": "tres ce", "means": "coeficiente 3, parte literal c"},
        {"symbol": r"3c+2c=5c", "reads": "se juntan", "means": "misma parte literal: se suman los coeficientes"},
        {"symbol": r"3c+2h", "reads": "no se juntan", "means": "partes literales distintas: la suma queda indicada"},
        {"symbol": r"3x\ \text{y}\ 3x^{2}", "reads": "tampoco", "means": "misma letra pero distinto exponente — no son semejantes"},
        {"symbol": r"x=1x", "reads": "el coeficiente invisible", "means": "una letra sola lleva un 1 delante que no se escribe"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Tramos de cuerda",
            "title": "Reordenar antes de juntar",
            "statement": (
                "El almacén entrega 4 tramos de cuerda, luego 3 estacas y luego 2 tramos "
                "más de cuerda. Escribe el registro lo más corto posible."
            ),
            "latex": r"4r+3+2r",
            "image_slot": False,
            "steps": [
                "Llamo r a la longitud de un tramo de cuerda. Las 3 estacas son una cantidad fija.",
                "El registro largo es 4r + 3 + 2r.",
                "Reordeno para poner juntos los semejantes: 4r + 2r + 3. Sumar en otro orden no cambia el total.",
                "Junto los dos términos en r: 4r + 2r = 6r.",
                "El 3 se queda solo, porque no hay ningún otro término sin letra: 6r + 3.",
            ],
            "solution": r"$4r+3+2r=6r+3$",
            "self_explanation": {
                "step_index": 4,
                "prompt": "¿Por qué el 3 no se junta ni con 4r ni con 2r?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Herramientas de dos turnos",
            "title": "Cuando hay que devolver parte de lo entregado",
            "statement": (
                "En el turno de mañana se sacan 5 lotes de herramienta y 4 mazos. En el de "
                "tarde se devuelven 2 lotes y 1 mazo. ¿Qué queda en la obra?"
            ),
            "latex": r"(5h+4)-(2h+1)",
            "image_slot": False,
            "steps": [
                "Lo devuelto se resta entero, así que va dentro de un paréntesis.",
                "El signo menos afecta a TODO lo del paréntesis: 5h + 4 − 2h − 1.",
                "Junto los términos en h: 5h − 2h = 3h.",
                "Junto las constantes: 4 − 1 = 3.",
                "Queda 3h + 3. Compruebo con h = 10: (54) − (21) = 33, y 3 · 10 + 3 = 33 ✓.",
            ],
            "solution": r"$(5h+4)-(2h+1)=3h+3$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que juntó cuerdas con bloques",
            "statement": (
                "El escriba de ayer entregó este registro: «3 tramos de cuerda y 4 bloques "
                "son 7 cuerdas-bloque», y lo escribió así: 3x + 4y = 7xy."
            ),
            "latex": r"3x+4y=7xy",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"3x+4y\ne 7xy",
            "error_note": (
                "Hay dos errores encadenados: sumó coeficientes de partes literales "
                "distintas, y además multiplicó las letras sin que nadie multiplicara nada."
            ),
            "correct_version": {
                "wrong_latex": r"3x+4y=7xy",
                "right_latex": r"3x+4y",
                "rows": [
                    {"wrong": "3 + 4 = 7, así que el resultado lleva un 7",
                     "right": "Los coeficientes solo se suman si la parte literal es la misma"},
                    {"wrong": "x junto a y da xy",
                     "right": "xy significa x · y, un producto — aquí solo había una suma"},
                ],
            },
            "explain_prompt": (
                "Explica por qué 3x + 4y no se puede acortar y comprueba el error "
                "sustituyendo x = 2 e y = 5."
            ),
            "steps": [
                "Sustituyo x = 2 e y = 5 en el original: 3 · 2 + 4 · 5 = 6 + 20 = 26.",
                "Sustituyo en el resultado del escriba: 7 · 2 · 5 = 70. No es lo mismo.",
                "Un solo contraejemplo basta: la igualdad es falsa, y la cuadrilla subió con 26 en vez de 70.",
            ],
            "solution": (
                "3x + 4y ya está todo lo corto que puede estar. Cuando las partes literales "
                "difieren, la respuesta correcta es dejar la suma indicada."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El registro ya va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": (
                    "Simplifica 7a + 2a + 5 y evalúa el resultado para a = 4."
                ),
                "given_steps": [
                    r"7a+2a+5=9a+5",
                    r"a=4",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"9a+5=", "answer": "41"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "Simplifica (6t + 9) − (2t + 3) y evalúa para t = 5. Completa los dos pasos."
                ),
                "given_steps": [
                    r"6t+9-2t-3",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{coeficiente de }t:\ 6-2=", "answer": "4"},
                    {"id": "P2-b2", "label": r"4t+6\ \text{con}\ t=5:", "answer": "26"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: cada cuadrilla necesita 2 lotes de herramienta "
                    "más 3 de repuesto. Con m cuadrillas la obra pide 2(m + 3) lotes. "
                    "¿Cuántos lotes con 7 cuadrillas?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"2(m+3)=2m+6\ \text{con}\ m=7:", "answer": "20"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de acortar el mismo registro",
        "intro": r"Simplifica $2x+5+3x-2$. Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Reordenar y sumar",
                "steps": [r"2x+5+3x-2", r"(2x+3x)+(5-2)", r"5x+3"],
                "note": "Compacto. Pide cuidado con los signos al mover términos de sitio.",
            },
            {
                "label": "Método 2 · Separar por tipos y contar",
                "steps": [
                    r"\text{con letra: }2x,\ 3x\ \to\ 5x",
                    r"\text{sin letra: }+5,\ -2\ \to\ +3",
                    r"5x+3",
                ],
                "note": "Más lento, pero cada término se toca una sola vez: cuesta perder uno.",
            },
        ],
        "question": "¿Cuál conviene aquí y cuál preferirías con doce términos y tres letras distintas?",
        "insight": (
            "Con cuatro términos el primero va sobrado. Cuando la lista crece, el segundo "
            "gana: hacer una columna por parte literal convierte el problema en varias "
            "sumas cortas e independientes, y un término olvidado se ve enseguida porque "
            "deja una columna sin cerrar."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Simplifica $3x+5x$.",
            "options": [
                {"id": "eightx", "text": r"$8x$", "latex": r"8x"},
                {"id": "eightx2", "text": r"$8x^{2}$", "latex": r"8x^{2}"},
                {"id": "fifteenx", "text": r"$15x$", "latex": r"15x"},
                {"id": "eight", "text": r"$8$", "latex": r"8"},
            ],
            "expected": "eightx",
            "feedback_by_option": {
                "eightx": "correct",
                "eightx2": "fb_a02_e1_exp",
                "fifteenx": "fb_a02_e1_mult",
                "eight": "fb_a02_e1_drop",
            },
            "misconception_by_option": {
                "eightx2": "suma_los_exponentes_al_sumar",
                "fifteenx": "confunde_suma_con_producto",
                "eight": "pierde_la_parte_literal",
            },
            "hints": {
                "n1": "Los dos tienen la misma parte literal: x.",
                "n2": "Se suman los coeficientes y la parte literal se queda igual.",
                "n3": "3 + 5 = 8, y la x sigue siendo x.",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Simplifica $(7h+4)-(3h+1)$.",
            "options": [
                {"id": "correct", "text": r"$4h+3$", "latex": r"4h+3"},
                {"id": "nosign", "text": r"$4h+5$", "latex": r"4h+5"},
                {"id": "allsub", "text": r"$10h+5$", "latex": r"10h+5"},
                {"id": "mixed", "text": r"$7h$", "latex": r"7h"},
            ],
            "expected": "correct",
            "feedback_by_option": {
                "correct": "correct",
                "nosign": "fb_a02_e2_sign",
                "allsub": "fb_a02_e2_added",
                "mixed": "fb_a02_e2_mixed",
            },
            "misconception_by_option": {
                "nosign": "distribucion_parcial_del_signo",
                "allsub": "ignora_el_signo_de_resta",
                "mixed": "combina_no_semejantes",
            },
            "hints": {
                "n1": "El menos de delante afecta a los DOS términos del paréntesis.",
                "n2": "Quedan 7h + 4 − 3h − 1.",
                "n3": "7 − 3 = 4 para la h, y 4 − 1 = 3 para las constantes.",
            },
        },
        {
            "id": "E3",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                "Simplifica 4r + 3 + 2r. Escribe la expresión más corta equivalente."
            ),
            "expr": r"4r+3+2r",
            "answer": "6r+3",
            "accepted": ["3+6r"],
            "hints": {
                "n1": "Junta primero los términos que llevan r.",
                "n2": "4r + 2r = 6r, y el 3 se queda solo.",
                "n3": "Escríbelo como coeficiente, letra y después la constante.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un escriba anota: «(8k + 5) − (3k + 2) = 8k + 5 − 3k + 2 = 5k + 7». "
                "¿Dónde está el error?"
            ),
            "options": [
                {"id": "sign", "text": "No repartió el menos al 2: debía quedar −2, y el resultado es 5k + 3"},
                {"id": "coef", "text": "Se equivocó al restar los coeficientes de k"},
                {"id": "like", "text": "Juntó términos que no eran semejantes"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "sign",
            "feedback_by_option": {
                "sign": "correct",
                "coef": "fb_a02_e4_coef",
                "like": "fb_a02_e4_like",
                "none": "fb_a02_e4_none",
            },
            "misconception_by_option": {
                "coef": "habito_busca_el_error_donde_no_esta",
                "like": "habito_busca_el_error_donde_no_esta",
                "none": "distribucion_parcial_del_signo",
            },
            "hints": {
                "n1": "Mira el paso donde desaparece el paréntesis y sigue los signos uno a uno.",
                "n2": "8k − 3k = 5k está bien. El problema está en el término sin letra.",
                "n3": "Restar (3k + 2) es restar el 3k Y el 2.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «$3x+4y=7xy$.»",
            "options": [
                {"id": "false", "text": "Falsa: las partes literales son distintas, la suma se queda indicada"},
                {"id": "true", "text": "Verdadera: 3 + 4 = 7 y las letras se juntan en xy"},
                {"id": "true_if", "text": r"Verdadera solo si $x=y$"},
                {"id": "false_seven", "text": r"Falsa: el resultado correcto es $7x+7y$"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_a02_e5_trap",
                "true_if": "fb_a02_e5_ifxy",
                "false_seven": "fb_a02_e5_seven",
            },
            "misconception_by_option": {
                "true": "combina_no_semejantes",
                "true_if": "combina_no_semejantes",
                "false_seven": "reparte_el_coeficiente_a_todo",
            },
            "hints": {
                "n1": "Para tumbar una igualdad basta UN par de valores.",
                "n2": "Prueba con x = 2 e y = 5 en los dos lados.",
                "n3": "26 en un lado y 70 en el otro: no puede ser cierta.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODOS los pares de términos que SÍ son semejantes.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$5m$ y $-2m$", "latex": r"5m,\ -2m"},
                {"id": "b", "text": r"$3k^{2}$ y $7k$", "latex": r"3k^{2},\ 7k"},
                {"id": "c", "text": r"$4ab$ y $9ba$", "latex": r"4ab,\ 9ba"},
                {"id": "d", "text": r"$6p$ y $6q$", "latex": r"6p,\ 6q"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Semejantes = misma parte literal, exponentes incluidos.",
                "n2": "ab y ba son la misma parte literal: el orden del producto da igual.",
                "n3": "k² y k no son lo mismo, y p y q son letras distintas.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "La rampa se mide en tramos iguales de longitud t. Un turno construye 5 "
                "tramos y deja 2 codos de remate; el siguiente construye 3 tramos y deja "
                "4 codos. Si un tramo mide 9 codos, ¿cuánto mide la rampa en total?"
            ),
            "expr": r"(5t+2)+(3t+4)=8t+6,\quad t=9",
            "answer": "78",
            "hints": {
                "n1": "Junta primero los tramos y aparte los codos de remate.",
                "n2": "Queda 8t + 6.",
                "n3": "8 · 9 + 6 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se juntan en un solo término?",
        "title": "Qué decide que dos cantidades se puedan sumar",
        "intro": (
            "Estar sumados en la misma línea no basta. Lo único que decide es si la parte "
            "literal coincide entera."
        ),
        "rows": [
            {"symbol": r"3x+2x", "name": "Misma letra, mismo exponente", "closed": "yes",
             "latex": r"=5x",
             "note": "Se suman los coeficientes y la x se conserva."},
            {"symbol": r"3x+2y", "name": "Letras distintas", "closed": "no",
             "latex": r"3x+2y",
             "note": "No hay nada que sacar factor común: la suma se queda indicada."},
            {"symbol": r"3x^{2}+2x", "name": "Misma letra, distinto exponente", "closed": "no",
             "latex": r"3x^{2}+2x",
             "note": "x² y x son cantidades distintas. Con x = 3 valen 27 y 6."},
            {"symbol": r"5+3", "name": "Dos constantes", "closed": "yes",
             "latex": r"=8",
             "note": "Los términos sin letra son semejantes entre sí. Siempre se juntan."},
            {"symbol": r"4ab+9ba", "name": "Mismo producto, otro orden", "closed": "yes",
             "latex": r"=13ab",
             "note": "ab y ba son la misma parte literal: multiplicar es conmutativo (N3-M01)."},
            {"symbol": r"2x+6", "name": "Sin letra pero con factor común", "closed": "partial",
             "latex": r"=2(x+3)",
             "note": "Como suma no se acortan. Como producto sí: es la distributiva al revés, y de ahí sale toda la factorización."},
        ],
        "outro": (
            "La regla cabe en una línea: se suman los coeficientes solo cuando la parte "
            "literal es idéntica. Y la última fila deja una puerta abierta — que dos "
            "términos no se junten sumando no significa que no se pueda hacer nada con ellos."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres registros trabajados en este nodo?",
        "thumbnails": [r"4r+3+2r", r"(5h+4)-(2h+1)", r"3x+4y"],
        "options": [
            {"id": "same_literal", "text": "En los tres hay que mirar la parte literal antes de operar", "correct": True},
            {"id": "coefficients", "text": "En los tres solo cambian los coeficientes; la parte literal se conserva", "correct": True},
            {"id": "always_shorter", "text": "En los tres el registro final tiene menos términos que el inicial", "correct": False},
            {"id": "one_term", "text": "En los tres el resultado se puede escribir con un solo término", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última tablilla del día: la cuadrilla de la rampa gasta 6 cuerdas y 8 codos de "
            "lino; la del trineo devuelve 2 cuerdas y saca 5 codos más. Si una cuerda "
            "equivale a 7 codos de lino, ¿cuántos codos de lino salen del almacén en total?"
        ),
        "polya": {
            "comprender": "Hay dos tipos de carga: cuerdas (con letra c) y codos de lino (constantes). No se juntan entre sí hasta el final.",
            "planear": "Escribo el registro: (6c + 8) + (−2c + 5). Simplifico y solo entonces sustituyo c = 7.",
            "ejecutar": "6c − 2c = 4c y 8 + 5 = 13, así que 4c + 13. Con c = 7: 4 · 7 + 13 = 28 + 13 = 41.",
            "comprobar": "Por separado: 6 − 2 = 4 cuerdas son 28 codos, más 8 + 5 = 13 codos ⇒ 41 ✓.",
        },
        "prompt": "¿Cuántos codos de lino salen en total?",
        "answer": "41",
        "hints": {
            "n1": "Simplifica primero, sustituye después.",
            "n2": "El registro simplificado es 4c + 13.",
            "n3": "Con c = 7: 28 + 13 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otras cargas. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya compruebas la parte literal antes de sumar coeficientes.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué hace que dos "
            "términos sean semejantes."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Simplifica 5b + 2b y evalúa el resultado para b = 6.",
                "answer": "42",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es el resultado de $9n-4n$?",
                "options": [
                    {"id": "fiven", "text": r"$5n$", "latex": r"5n"},
                    {"id": "five", "text": r"$5$", "latex": r"5"},
                    {"id": "thirteen", "text": r"$13n$", "latex": r"13n"},
                ],
                "expected": "fiven",
                "misconception_by_option": {
                    "five": "pierde_la_parte_literal",
                    "thirteen": "confunde_resta_con_suma",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Se puede acortar $5a+2a^{2}$?",
                "options": [
                    {"id": "no", "text": "No: los exponentes son distintos"},
                    {"id": "yes", "text": r"Sí: $7a^{2}$"},
                    {"id": "yes_a", "text": r"Sí: $7a$"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "combina_no_semejantes",
                    "yes_a": "combina_no_semejantes",
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
        "default": "Compara la parte literal entera —letras y exponentes— antes de operar.",
        "fb_a02_e1_exp": (
            "Los exponentes se suman al MULTIPLICAR, no al sumar. → Comprueba con x = 2: "
            "3 · 2 + 5 · 2 = 16, y 8 · 2 = 16."
        ),
        "fb_a02_e1_mult": (
            "Ahí multiplicaste los coeficientes en vez de sumarlos. → Vuelve a leer el signo."
        ),
        "fb_a02_e1_drop": (
            "La parte literal no desaparece: se conserva. → ¿3 cuerdas más 5 cuerdas son 8 qué?"
        ),
        "fb_a02_e2_sign": (
            "Al 3h sí le cambiaste el signo, pero al 1 no. → El menos entra a todo el paréntesis."
        ),
        "fb_a02_e2_added": (
            "Ahí sumaste los dos paréntesis en vez de restarlos. → Fíjate en el signo de en medio."
        ),
        "fb_a02_e2_mixed": (
            "Las constantes no se juntan con los términos en h. → Trátalas como una columna aparte."
        ),
        "fb_a02_e4_coef": (
            "8k − 3k = 5k está bien calculado. → Revisa el término sin letra."
        ),
        "fb_a02_e4_like": (
            "No juntó nada que no fuera semejante: k con k y número con número. → El fallo está en un signo."
        ),
        "fb_a02_e4_none": (
            "Restar (3k + 2) obliga a restar también el 2. → Escribe el paso sin paréntesis "
            "con mucho cuidado."
        ),
        "fb_a02_e5_trap": (
            "Con x = 2 e y = 5 el lado izquierdo da 26 y el derecho 70. → Comprueba ese caso."
        ),
        "fb_a02_e5_ifxy": (
            "Ojo: aunque x = y, 3x + 4x = 7x, no 7x². → Prueba con x = y = 2 y verás que "
            "tampoco cuadra."
        ),
        "fb_a02_e5_seven": (
            "El 7 no se reparte: nadie multiplicó nada. → La respuesta correcta es dejar "
            "3x + 4y tal cual."
        ),
    },
    "closing": (
        "La cuadrilla sube una sola vez con el registro corto y correcto. Bakenra avisa de lo "
        "que viene: en el patio de aparejos no se entrega, se DEVUELVE, y una partida que "
        "vuelve entera se resta entera. Ahí es donde se tuercen los inventarios."
    ),
    "validation_status": "F5_O01_11bloques",
}
