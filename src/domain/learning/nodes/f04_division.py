"""F04 · El silo de simiente — la que se da la vuelta es la de la derecha.

Cuarta y última sala de los campos tras la crecida. Guía: Tabiry. Vocabulario
propio: silo, simiente, saco, medida, sementera, sembradura. Nada de parcelas ni
linderos (F01), canales ni caudales (F02), ni eras ni parvas (F03).

Error focal: invertir la primera fracción en vez del divisor. El divisor es el
que dice «entre cuánto», y es el único que se da la vuelta.
"""

NODE_ID = "ALG-N1-F04-DIVISION"
CONCEPT_SLUG = "division_de_fracciones_algebraicas"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "division_de_fracciones_algebraicas",
    "misconception": "invierte_la_primera_fraccion",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El silo de simiente · División de fracciones",
    "house": "El silo de simiente",
    "guide": "Tabiry",
    "finish_label": "Salir hacia el taller",
    "title": "La que se da la vuelta es la de la derecha",
    "intro": (
        "En la era tomabas una parte de otra parte y el resultado salía más pequeño. Aquí "
        "pasa lo contrario y el registro se escribe casi igual — con una diferencia de una "
        "sola fracción, que es justo donde se equivoca todo el mundo."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el silo. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuántas medias medidas caben en 3 medidas?",
                "answer": "6",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $\dfrac{1}{2}\div\dfrac{1}{4}$?",
                "options": [
                    {"id": "two", "text": "2"},
                    {"id": "eighth", "text": r"$\dfrac{1}{8}$", "latex": r"\dfrac{1}{8}"},
                    {"id": "half", "text": r"$\dfrac{1}{2}$", "latex": r"\dfrac{1}{2}"},
                ],
                "expected": "two",
                "misconception_by_option": {
                    "eighth": "multiplica_en_vez_de_dividir",
                    "half": "invierte_la_primera_fraccion",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Al dividir dos fracciones, ¿a cuál de las dos se le da la vuelta?",
                "options": [
                    {"id": "second", "text": "A la segunda, la que dice entre cuánto"},
                    {"id": "first", "text": "A la primera"},
                    {"id": "both", "text": "A las dos"},
                ],
                "expected": "second",
                "misconception_by_option": {
                    "first": "invierte_la_primera_fraccion",
                    "both": "invierte_la_primera_fraccion",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/f04-division-katia.png",
        "eyebrow": "KatIA · En el silo de simiente",
        "title": "El silo lleno que no daba ni para un saco",
        "body": (
            "El silo guarda la simiente de la próxima sementera. Se saca en sacos, y cada "
            "saco lleva dos tercios de medida.\n\n"
            "Tabiry señala el registro:\n\n"
            "«Hay ocho medidas de simiente. La pregunta es cuántos sacos salen. El escriba "
            "escribió la división, se acordó de que había que dar la vuelta a una fracción "
            "y le dio la vuelta a la de la izquierda. Le salió un doceavo de saco.»\n\n"
            "«Con el silo lleno hasta arriba, su tablilla decía que no llegaba ni para un "
            "saco. Y la sementera empieza pasado mañana.»"
        ),
        "question": "Al dividir entre una fracción, ¿cuál de las dos se da la vuelta, y por qué esa?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "La primera, que es la que se está repartiendo"},
                {"id": "b", "text": "La segunda, que es la que dice entre cuánto se reparte"},
                {"id": "c", "text": "Da igual: el resultado sale el mismo"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder descartar el error sin rehacer "
                "la cuenta, solo mirando si el resultado creció o menguó."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dividir no siempre achica",
        "body": "La pregunta que hay detrás de toda división es «¿cuántos de estos caben?».",
        "cases": [
            {
                "label": "Entre un entero",
                "context": "Seis medidas repartidas entre 3 sacos grandes",
                "fraction": r"6\div 3",
                "division": r"2",
                "note": "Cada saco se lleva 2 medidas. El resultado es menor que 6.",
            },
            {
                "label": "Entre una fracción",
                "context": "Seis medidas en sacos de un tercio de medida",
                "fraction": r"6\div\dfrac{1}{3}",
                "division": r"18",
                "note": "En cada medida caben 3 tercios, así que salen 18 sacos. El resultado CRECE.",
            },
        ],
        "resolution": (
            "Dividir entre algo menor que 1 da un resultado mayor, porque caben muchos. Esa "
            "es la razón de dar la vuelta al divisor: preguntar «¿cuántos tercios caben en "
            "6?» es lo mismo que preguntar «¿cuánto son 6 veces 3?». La fracción que se "
            "invierte es la que dice el tamaño del saco, no la que dice cuánta simiente hay."
        ),
    },
    "definition_title": "División de fracciones algebraicas",
    "definition_katex": r"\dfrac{a}{b}\div\dfrac{c}{d}=\dfrac{a}{b}\cdot\dfrac{d}{c}",
    "definition": (
        "Para DIVIDIR una fracción entre otra se multiplica la primera por el RECÍPROCO de "
        "la segunda: se deja la de la izquierda como está y se da la vuelta a la de la "
        "derecha. Un número entero se divide igual, viéndolo antes como fracción con 1 "
        "debajo. A partir de ahí es un producto, con todo lo que ya sabes de la era: se "
        "puede simplificar antes de multiplicar."
    ),
    "definition_symbols": [
        {
            "symbol": r"\dfrac{a}{b}\div\dfrac{c}{d}=\dfrac{a}{b}\cdot\dfrac{d}{c}",
            "reads": "la regla entera",
            "means": "la de la derecha se invierte",
        },
        {"symbol": r"\dfrac{d}{c}", "reads": "recíproco", "means": "la misma fracción del revés"},
        {
            "symbol": r"8=\dfrac{8}{1}",
            "reads": "un entero también divide",
            "means": "todo número lleva un 1 debajo",
        },
        {
            "symbol": r"6\div\dfrac{1}{3}=18",
            "reads": "dividir puede agrandar",
            "means": "entre algo menor que 1, el resultado crece",
        },
        {
            "symbol": r"\dfrac{c}{d}\cdot\dfrac{d}{c}=1",
            "reads": "por qué funciona",
            "means": "una fracción por su recíproco deshace la división",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Sacos de la sementera",
            "title": "Un entero entre una fracción",
            "statement": (
                "Hay 8 medidas de simiente y cada saco lleva dos tercios de medida. "
                "¿Cuántos sacos salen?"
            ),
            "latex": r"8\div\dfrac{2}{3}",
            "image_slot": False,
            "steps": [
                "Escribo el 8 como fracción: 8/1. Así las dos tienen la misma forma.",
                "Dejo la primera y doy la vuelta a la segunda: 8/1 · 3/2.",
                "Multiplico arriba con arriba y abajo con abajo: 24/2.",
                "Queda 12 sacos.",
                "Compruebo el sentido: los sacos son más pequeños que una medida, así que tienen que salir MÁS de 8 ✓.",
            ],
            "solution": r"$8\div\dfrac{2}{3}=12$",
            "self_explanation": {
                "step_index": 1,
                "prompt": "¿Por qué se invierte la del saco y no la de la simiente?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Simiente por sembradura",
            "title": "Con letras, y simplificando antes",
            "statement": (
                "Del silo salen 3/x medidas por sembradura y cada saco lleva 6/x² medidas. "
                "¿Cuántos sacos salen por sembradura?"
            ),
            "latex": r"\dfrac{3}{x}\div\dfrac{6}{x^{2}}",
            "image_slot": False,
            "steps": [
                "Doy la vuelta a la de la derecha: 3/x · x²/6.",
                "Ahora es un producto, así que puedo simplificar antes de multiplicar.",
                "La x de abajo se empareja con una de las dos x de arriba: queda 3·x / 6.",
                "3 y 6 se dividen entre 3: queda x/2.",
                "Compruebo con x = 4: 3/4 ÷ 6/16 = 3/4 · 16/6 = 2, y 4/2 = 2 ✓.",
            ],
            "solution": r"$\dfrac{3}{x}\div\dfrac{6}{x^{2}}=\dfrac{x}{2}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que dio la vuelta a la de la izquierda",
            "statement": (
                "Vuelve el registro de la apertura: 8 medidas en sacos de dos tercios. El "
                "escriba escribió 1/8 · 2/3 y anotó un doceavo de saco."
            ),
            "latex": r"8\div\dfrac{2}{3}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\dfrac{1}{8}\cdot\dfrac{2}{3}=\dfrac{1}{12}",
            "error_note": (
                "Se acordó de la regla a medias: invirtió, pero la fracción equivocada. "
                "Dio la vuelta a la simiente en vez de al saco."
            ),
            "correct_version": {
                "wrong_latex": r"8\div\dfrac{2}{3}=\dfrac{1}{8}\cdot\dfrac{2}{3}",
                "right_latex": r"8\div\dfrac{2}{3}=\dfrac{8}{1}\cdot\dfrac{3}{2}=12",
                "rows": [
                    {
                        "wrong": "Se invierte la primera",
                        "right": "Se invierte el divisor, que es la segunda",
                    },
                    {
                        "wrong": r"\dfrac{1}{12}\ \text{de saco con el silo lleno}",
                        "right": r"12\ \text{sacos, más que las 8 medidas ✓}",
                    },
                ],
            },
            "explain_prompt": (
                "Explica por qué el resultado tenía que ser MAYOR que 8, y usa eso para "
                "descartar un doceavo sin rehacer la cuenta."
            ),
            "steps": [
                "Cada saco es menor que una medida, así que en 8 medidas caben más de 8 sacos.",
                "Cualquier resultado por debajo de 8 delata el error, y un doceavo lo delata a gritos.",
                "Regla para no volver a caer: señala con el dedo el divisor —lo que va después del signo— y da la vuelta solo a eso.",
            ],
            "solution": (
                "8 ÷ 2/3 = 12 sacos. Invertir la primera no es un descuido pequeño: cambia "
                "la pregunta de «¿cuántos sacos salen?» a otra que nadie hizo."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El registro del silo va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Calcula $\dfrac{3}{4}\div\dfrac{1}{2}$.",
                "given_steps": [r"\dfrac{3}{4}\cdot\dfrac{2}{1}", r"\dfrac{6}{4}"],
                "blanks": [
                    {
                        "id": "P1-b1",
                        "label": r"\dfrac{6}{4}=\dfrac{3}{\;?\;},\quad ?=",
                        "answer": "2",
                    }
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Calcula $12\div\dfrac{3}{5}$.",
                "given_steps": [r"\dfrac{12}{1}\cdot\dfrac{5}{3}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"12\cdot 5=", "answer": "60"},
                    {"id": "P2-b2", "label": r"60\div 3=", "answer": "20"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: hay 15 medidas de simiente y cada saco lleva "
                    "tres cuartos de medida. ¿Cuántos sacos salen?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"15\div\dfrac{3}{4}=", "answer": "20"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de dividir entre una fracción",
        "intro": r"$6\div\dfrac{3}{4}$. Una aplica la regla; la otra pregunta qué significa.",
        "methods": [
            {
                "label": "Método 1 · Invertir y multiplicar",
                "steps": [
                    r"\dfrac{6}{1}\div\dfrac{3}{4}",
                    r"\dfrac{6}{1}\cdot\dfrac{4}{3}",
                    r"\dfrac{24}{3}=8",
                ],
                "note": "Rápido, siempre que hayas invertido la fracción correcta.",
            },
            {
                "label": "Método 2 · Preguntar cuántos caben",
                "steps": [
                    r"\text{en 1 medida caben}\ \tfrac{4}{3}\ \text{sacos}",
                    r"\text{en 6 medidas: } 6\cdot\tfrac{4}{3}",
                    r"8",
                ],
                "note": "Más lento, pero te dice de antemano si el resultado tiene que crecer.",
            },
        ],
        "question": "¿Cuál de los dos habría salvado al escriba del silo?",
        "insight": (
            "El segundo, y no porque el primero esté mal: el primero es más rápido y es el "
            "que acabarás usando. El problema es que la regla «se invierte una» no dice "
            "cuál, y aplicada al revés da un número que parece una respuesta. Preguntar "
            "«¿cuántos caben?» fija de antemano si el resultado debe crecer o menguar, y "
            "eso convierte el método 2 en la comprobación del método 1."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuánto es $\dfrac{2}{3}\div\dfrac{4}{9}$?",
            "options": [
                {"id": "ok", "text": r"$\dfrac{3}{2}$", "latex": r"\dfrac{3}{2}"},
                {"id": "first", "text": r"$\dfrac{2}{3}$", "latex": r"\dfrac{2}{3}"},
                {"id": "mult", "text": r"$\dfrac{8}{27}$", "latex": r"\dfrac{8}{27}"},
                {
                    "id": "swap",
                    "text": r"Invirtiendo las dos: $\dfrac{27}{8}$",
                    "latex": r"\dfrac{27}{8}",
                },
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "first": "fb_f04_e1_first",
                "mult": "fb_f04_e1_mult",
                "swap": "fb_f04_e1_swap",
            },
            "misconception_by_option": {
                "first": "invierte_la_primera_fraccion",
                "mult": "multiplica_en_vez_de_dividir",
                "swap": "invierte_las_dos_fracciones",
            },
            "hints": {
                "n1": "Deja la de la izquierda y da la vuelta a la de la derecha.",
                "n2": "Queda 2/3 · 9/4.",
                "n3": "18/12 se simplifica entre 6.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "Hay 10 medidas de simiente y cada saco lleva dos quintos de medida. "
                "¿Cuántos sacos salen?"
            ),
            "expr": r"10\div\dfrac{2}{5}",
            "answer": "25",
            "hints": {
                "n1": "El 10 es 10/1.",
                "n2": "Invierte el saco: 10/1 · 5/2.",
                "n3": "50 ÷ 2 = …",
            },
        },
        {
            "id": "E3",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Calcula $\dfrac{5}{6}\div\dfrac{2}{3}$ y escribe el resultado como "
                "fracción simplificada, así: 5/12. No dejes espacios."
            ),
            "answer": "5/4",
            "hints": {
                "n1": "Invierte la segunda: 5/6 · 3/2.",
                "n2": "Queda 15/12.",
                "n3": "15 y 12 se dividen los dos entre 3.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un escriba calcula $9\div\dfrac{3}{4}$ y anota $\dfrac{1}{12}$. ¿Dónde "
                "está el error?"
            ),
            "options": [
                {
                    "id": "first",
                    "text": r"Invirtió el 9 en vez del saco: es $9\cdot\dfrac{4}{3}=12$",
                },
                {"id": "mult", "text": r"Multiplicó sin invertir nada"},
                {"id": "simp", "text": "Olvidó simplificar el resultado"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "first",
            "feedback_by_option": {
                "first": "correct",
                "mult": "fb_f04_e4_mult",
                "simp": "fb_f04_e4_simp",
                "none": "fb_f04_e4_none",
            },
            "misconception_by_option": {
                "mult": "multiplica_en_vez_de_dividir",
                "simp": "habito_deja_el_resultado_sin_simplificar",
                "none": "invierte_la_primera_fraccion",
            },
            "hints": {
                "n1": "Los sacos son menores que una medida.",
                "n2": "Con 9 medidas tienen que salir más de 9 sacos.",
                "n3": "Un doceavo no llega ni a un saco.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Al dividir dos fracciones se da la vuelta a la "
                "primera y se multiplica.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": r"Falsa: se da la vuelta a la segunda — $\dfrac{1}{2}\div\dfrac{1}{4}=2$",
                },
                {"id": "true", "text": "Verdadera: la primera es la que se reparte"},
                {
                    "id": "true_either",
                    "text": "Verdadera: da igual cuál, el resultado sale el mismo",
                },
                {"id": "false_both", "text": "Falsa: hay que dar la vuelta a las dos"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_f04_e5_trap",
                "true_either": "fb_f04_e5_either",
                "false_both": "fb_f04_e5_both",
            },
            "misconception_by_option": {
                "true": "invierte_la_primera_fraccion",
                "true_either": "invierte_la_primera_fraccion",
                "false_both": "invierte_la_primera_fraccion",
            },
            "hints": {
                "n1": "Prueba con 1/2 ÷ 1/4 contando cuántos cuartos caben en un medio.",
                "n2": "Caben 2.",
                "n3": "Invirtiendo la primera saldría 1/2, que tampoco es lo que se cuenta.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (
                "Selecciona TODAS las divisiones cuyo resultado es MAYOR que la primera "
                "fracción."
            ),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$6\div\dfrac{1}{3}$", "latex": r"6\div\dfrac{1}{3}"},
                {"id": "b", "text": r"$6\div 3$", "latex": r"6\div 3"},
                {
                    "id": "c",
                    "text": r"$\dfrac{1}{2}\div\dfrac{1}{4}$",
                    "latex": r"\dfrac{1}{2}\div\dfrac{1}{4}",
                },
                {"id": "d", "text": r"$\dfrac{1}{2}\div 4$", "latex": r"\dfrac{1}{2}\div 4"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Mira si el divisor es menor o mayor que 1.",
                "n2": "Entre algo menor que 1, el resultado crece.",
                "n3": "Entre algo mayor que 1, mengua.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El silo guarda 3s medidas de simiente y cada saco lleva s/4 medidas. Con "
                "s = 6, ¿cuántos sacos salen?"
            ),
            "expr": r"3s\div\dfrac{s}{4}=12,\quad s=6",
            "answer": "12",
            "hints": {
                "n1": "Invierte el saco: 3s · 4/s.",
                "n2": "La s se cancela: quedan 12 sacos.",
                "n3": "El resultado no depende de s.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se da la vuelta al divisor?",
        "title": "Qué fracción se invierte y qué le pasa al resultado",
        "intro": (
            "La regla es una sola y se falla siempre por el mismo sitio: no por olvidarla, "
            "sino por aplicarla a la fracción de al lado."
        ),
        "rows": [
            {
                "symbol": r"8\div\dfrac{2}{3}",
                "name": "Entero entre fracción",
                "closed": "yes",
                "latex": r"\dfrac{8}{1}\cdot\dfrac{3}{2}=12",
                "note": "Se invierte el saco, no la simiente. El resultado crece. Es el caso focal.",
            },
            {
                "symbol": r"\dfrac{2}{3}\div\dfrac{4}{9}",
                "name": "Fracción entre fracción",
                "closed": "yes",
                "latex": r"\dfrac{2}{3}\cdot\dfrac{9}{4}=\dfrac{3}{2}",
                "note": "La de la izquierda se queda quieta. Después es un producto normal.",
            },
            {
                "symbol": r"\dfrac{3}{x}\div\dfrac{6}{x^{2}}",
                "name": "Con letras",
                "closed": "yes",
                "latex": r"\dfrac{x}{2}",
                "note": "Una vez invertida, se puede simplificar antes de multiplicar, como en la era.",
            },
            {
                "symbol": r"\dfrac{1}{2}\div 4",
                "name": "Entre un entero",
                "closed": "partial",
                "latex": r"\dfrac{1}{2}\cdot\dfrac{1}{4}=\dfrac{1}{8}",
                "note": "Se invierte igual, pero primero hay que ver el 4 como 4/1. Aquí el resultado mengua.",
            },
            {
                "symbol": r"\dfrac{2}{3}\div\dfrac{2}{3}",
                "name": "Entre sí misma",
                "closed": "partial",
                "latex": r"1",
                "note": "Se invierte igual y da 1, ni crece ni mengua. Sirve para comprobar que invertiste la correcta.",
            },
            {
                "symbol": r"\dfrac{2}{3}\cdot\dfrac{4}{9}",
                "name": "Un producto",
                "closed": "no",
                "latex": r"\dfrac{8}{27}",
                "note": "Aquí no se invierte nada. La vuelta es lo que distingue una división de un producto.",
            },
        ],
        "outro": (
            "Fíjate en lo que hacen juntas la primera y la cuarta fila: el mismo "
            "procedimiento, y en una el resultado crece y en la otra mengua. No es que "
            "«dividir achique» ni que «dividir agrande» — depende de si el divisor es "
            "menor o mayor que uno. Esa es la comprobación de un vistazo que le faltó al "
            "escriba del silo."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres repartos del silo trabajados en este nodo?",
        "thumbnails": [
            r"8\div\dfrac{2}{3}",
            r"\dfrac{3}{x}\div\dfrac{6}{x^{2}}",
            r"6\div\dfrac{3}{4}",
        ],
        "options": [
            {
                "id": "divisor",
                "text": "En los tres se invierte el divisor y solo el divisor",
                "correct": True,
            },
            {
                "id": "becomes_product",
                "text": "En los tres la división se convierte en un producto en el primer paso",
                "correct": True,
            },
            {
                "id": "smaller",
                "text": "En los tres el resultado es menor que la primera cantidad",
                "correct": False,
            },
            {
                "id": "common",
                "text": "En los tres hace falta un denominador común antes de empezar",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Cierre del silo antes de la sementera. Quedan 21 medidas de simiente y los "
            "sacos de siembra llevan tres séptimos de medida cada uno. ¿Cuántos sacos "
            "salen del silo?"
        ),
        "polya": {
            "comprender": "Es un «¿cuántos caben?»: medidas de simiente repartidas en sacos más pequeños que una medida.",
            "planear": "Escribo 21 como 21/1 y doy la vuelta al saco: 21/1 · 7/3.",
            "ejecutar": "21 · 7 = 147, y 147 ÷ 3 = 49 sacos.",
            "comprobar": "Los sacos son menores que una medida, así que tenían que salir más de 21 ✓. Invirtiendo la primera habría salido 1/49, con el silo lleno.",
        },
        "prompt": "¿Cuántos sacos salen?",
        "answer": "49",
        "hints": {
            "n1": "El 21 es 21/1.",
            "n2": "Invierte solo el saco: 21/1 · 7/3.",
            "n3": "147 ÷ 3 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otra sementera. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya inviertes el divisor y compruebas si el resultado debía crecer.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la pregunta "
            "«¿cuántos caben?», que es la que fija cuál se da la vuelta."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuántos tercios de medida caben en 4 medidas?",
                "answer": "12",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $\dfrac{1}{3}\div\dfrac{1}{6}$?",
                "options": [
                    {"id": "two", "text": "2"},
                    {"id": "eighteenth", "text": r"$\dfrac{1}{18}$", "latex": r"\dfrac{1}{18}"},
                    {"id": "half", "text": r"$\dfrac{1}{2}$", "latex": r"\dfrac{1}{2}"},
                ],
                "expected": "two",
                "misconception_by_option": {
                    "eighteenth": "multiplica_en_vez_de_dividir",
                    "half": "invierte_la_primera_fraccion",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $\dfrac{5}{8}\div\dfrac{1}{4}$, ¿a cuál se le da la vuelta?",
                "options": [
                    {"id": "second", "text": r"A $\dfrac{1}{4}$"},
                    {"id": "first", "text": r"A $\dfrac{5}{8}$"},
                    {"id": "both", "text": "A las dos"},
                ],
                "expected": "second",
                "misconception_by_option": {
                    "first": "invierte_la_primera_fraccion",
                    "both": "invierte_la_primera_fraccion",
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
        "default": "Señala el divisor —lo que va después del signo— y da la vuelta solo a eso.",
        "fb_f04_e1_first": (
            "Ahí se invirtió la de la izquierda. → La que se da la vuelta es la que dice "
            "entre cuánto se reparte."
        ),
        "fb_f04_e1_mult": "Multiplicaste sin invertir. → Eso es el producto, no la división.",
        "fb_f04_e1_swap": (
            "Invertiste las dos y volviste al principio del revés. → Solo se da la vuelta "
            "al divisor."
        ),
        "fb_f04_e4_mult": (
            "Sí invirtió algo; el problema es cuál. → Multiplicar sin invertir habría dado 27/4."
        ),
        "fb_f04_e4_simp": "1/12 está simplificado. → Lo que falla es la fracción que invirtió.",
        "fb_f04_e4_none": (
            "Con 9 medidas y sacos de tres cuartos tienen que salir más de 9 sacos. → Un "
            "doceavo no llega ni a uno."
        ),
        "fb_f04_e5_trap": (
            "Que se reparta no la convierte en la que se invierte. → Se invierte la que "
            "dice el tamaño de la parte."
        ),
        "fb_f04_e5_either": (
            "No da igual: los dos resultados son recíprocos entre sí. → 1/2 ÷ 1/4 es 2 "
            "invirtiendo la segunda y 8 invirtiendo la primera."
        ),
        "fb_f04_e5_both": (
            "Invirtiendo las dos se vuelve al principio del revés. → Solo se da la vuelta "
            "al divisor."
        ),
    },
    "closing": (
        "Los campos quedan repartidos: sabes simplificar, juntar partes del mismo reparto, "
        "tomar una parte de otra y preguntar cuántas caben. Tabiry cierra la tercera "
        "sección del papiro. Falta el taller del canon, donde las medidas de un boceto "
        "tienen que crecer todas a la vez y en la misma proporción."
    ),
    "validation_status": "F5_F04_11bloques",
}
