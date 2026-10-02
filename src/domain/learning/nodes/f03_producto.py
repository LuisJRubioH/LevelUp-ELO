"""F03 · La era de trilla — multiplicar es tomar una parte de otra parte.

Tercera sala de los campos tras la crecida. Guía: Tabiry. Vocabulario propio:
era de trilla, parva, gavilla, haz, espiga, trillo, troje. Nada de parcelas ni
linderos (F01), canales ni caudales (F02), ni simiente (F04).

Error focal: arrastrar el ritual de la suma —buscar denominador común— a un
producto, donde no pinta nada. El «de» de «tres cuartos DE la parva» es un por.
"""

NODE_ID = "ALG-N1-F03-PRODUCTO"
CONCEPT_SLUG = "producto_de_fracciones_algebraicas"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "producto_de_fracciones_algebraicas",
    "misconception": "busca_comun_denominador_para_multiplicar",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La era de trilla · Producto de fracciones",
    "house": "La era de trilla",
    "guide": "Tabiry",
    "finish_label": "Bajar al silo de simiente",
    "title": "«Tres cuartos de la parva» es un por, no una suma",
    "intro": (
        "En el canal madre juntabas partes del mismo reparto. En la era no se juntan "
        "partes: se toman partes DE otras partes. La cuenta es más corta de lo que "
        "parece, y el error habitual es hacer de más."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de subir a la era. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es la mitad de 12?",
                "answer": "6",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $\dfrac{2}{3}\cdot\dfrac{1}{5}$?",
                "options": [
                    {"id": "ok", "text": r"$\dfrac{2}{15}$", "latex": r"\dfrac{2}{15}"},
                    {"id": "same", "text": r"$\dfrac{2}{5}$", "latex": r"\dfrac{2}{5}"},
                    {"id": "sum", "text": r"$\dfrac{13}{15}$", "latex": r"\dfrac{13}{15}"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "same": "olvida_multiplicar_los_denominadores",
                    "sum": "busca_comun_denominador_para_multiplicar",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Para multiplicar dos fracciones, ¿hace falta un denominador común?",
                "options": [
                    {"id": "no", "text": "No: se multiplica arriba con arriba y abajo con abajo"},
                    {"id": "yes", "text": "Sí, igual que para sumarlas"},
                    {"id": "sometimes", "text": "Solo si los denominadores son distintos"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "busca_comun_denominador_para_multiplicar",
                    "sometimes": "busca_comun_denominador_para_multiplicar",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/f03-producto-katia.png",
        "eyebrow": "KatIA · En la era de trilla",
        "title": "La troje que recibió más grano del que se trilló",
        "body": (
            "En la era se trilla la parva y se separa el grano limpio de la paja. Tabiry "
            "lleva una tablilla con dos números:\n\n"
            "«De la parva, dos tercios salen como grano limpio. Y de ese grano, tres "
            "cuartos van a la troje del templo.»\n\n"
            "«El escriba de ayer hizo lo mismo que hace para el riego: buscó doceavos, los "
            "puso a la misma altura, sumó, y anotó que a la troje iban diecisiete doceavos "
            "de la parva.»\n\n"
            "Tabiry mira la era vacía.\n\n"
            "«Mandó al templo más grano del que se había trillado. Y la parva era una sola.»"
        ),
        "question": "Cuando se toma una parte DE otra parte, ¿la cuenta es una suma o un producto?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Una suma: hay dos fracciones, se juntan"},
                {"id": "b", "text": "Un producto: la segunda parte se toma dentro de la primera"},
                {"id": "c", "text": "Una resta: lo que va al templo se descuenta"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decir sin dudar por qué el "
                "resultado tiene que ser MENOR que las dos partes de las que salió."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Las mismas dos fracciones, dos operaciones distintas",
        "body": "Con un tercio y un medio se pueden hacer dos cuentas, y no se parecen en nada.",
        "cases": [
            {
                "label": "Juntar dos partes",
                "context": r"Un tercio de la era MÁS un medio de la era",
                "fraction": r"\dfrac{1}{3}+\dfrac{1}{2}",
                "division": r"\dfrac{2}{6}+\dfrac{3}{6}=\dfrac{5}{6}",
                "note": "Hay que igualar los trozos. El resultado es mayor que cada parte.",
            },
            {
                "label": "Una parte DE otra parte",
                "context": r"La mitad DE un tercio de la era",
                "fraction": r"\dfrac{1}{2}\cdot\dfrac{1}{3}",
                "division": r"\dfrac{1}{6}",
                "note": "Se parte en dos lo que ya estaba partido en tres: salen seis trozos. Sale MENOR.",
            },
        ],
        "resolution": (
            "Al sumar hay que igualar los trozos porque se cuentan juntos. Al multiplicar "
            "no se cuenta nada junto: se vuelve a partir lo que ya estaba partido, y por "
            "eso los denominadores se multiplican entre sí. Buscar denominador común aquí "
            "no es un paso de más — es un paso que cambia el resultado."
        ),
    },
    "definition_title": "Producto de fracciones algebraicas",
    "definition_katex": r"\dfrac{a}{b}\cdot\dfrac{c}{d}=\dfrac{a\,c}{b\,d}",
    "definition": (
        "Para MULTIPLICAR dos fracciones se multiplican los numeradores entre sí y los "
        "denominadores entre sí. No hace falta denominador común. La palabra «de» en «dos "
        "tercios DE la parva» es una multiplicación. Como arriba y abajo todo son "
        "factores, se puede simplificar antes de multiplicar — incluso cruzando el "
        "numerador de una con el denominador de la otra."
    ),
    "definition_symbols": [
        {"symbol": r"\dfrac{2}{3}\cdot\dfrac{1}{5}=\dfrac{2}{15}", "reads": "arriba con arriba, abajo con abajo", "means": "la regla entera"},
        {"symbol": r"\text{«de»}\to\cdot", "reads": "de es por", "means": "dos tercios DE tres cuartos es un producto"},
        {"symbol": r"\dfrac{3}{x}\cdot\dfrac{x}{5}=\dfrac{3}{5}", "reads": "la letra se va", "means": "arriba y abajo son factores: la x se cancela"},
        {"symbol": r"6=\dfrac{6}{1}", "reads": "un entero es fracción", "means": "todo número tiene un 1 debajo"},
        {"symbol": r"\dfrac{8}{15}\cdot\dfrac{25}{12}", "reads": "se puede cruzar", "means": "simplificar antes deja números pequeños"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · De la parva a la troje",
            "title": "Una parte de otra parte",
            "statement": (
                "De la parva, dos tercios salen como grano limpio; de ese grano, tres "
                "cuartos van a la troje. ¿Qué parte de la parva llega a la troje?"
            ),
            "latex": r"\dfrac{2}{3}\cdot\dfrac{3}{4}",
            "image_slot": False,
            "steps": [
                "«Tres cuartos DE dos tercios» es un producto: no se juntan, se toma dentro.",
                "Multiplico arriba con arriba: 2 · 3 = 6.",
                "Multiplico abajo con abajo: 3 · 4 = 12.",
                "Queda 6/12, que se simplifica a 1/2.",
                "Media parva. Menos que dos tercios y menos que tres cuartos, como tenía que ser.",
            ],
            "solution": r"$\dfrac{2}{3}\cdot\dfrac{3}{4}=\dfrac{1}{2}$",
            "self_explanation": {
                "step_index": 4,
                "prompt": "¿Por qué el resultado tiene que ser menor que las dos fracciones de partida?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Gavillas por espiga",
            "title": "Cuando la letra se cancela sola",
            "statement": (
                "Cada haz da 3/x de medida de grano, y en la era se trillan x/5 haces por "
                "jornada. ¿Cuánto grano sale por jornada?"
            ),
            "latex": r"\dfrac{3}{x}\cdot\dfrac{x}{5}",
            "image_slot": False,
            "steps": [
                "Multiplico arriba: 3 · x = 3x. Y abajo: x · 5 = 5x.",
                "Queda 3x/5x.",
                "Arriba y abajo todo son factores, así que la x se puede tachar.",
                "Queda 3/5 de medida por jornada, sin ninguna x.",
                "Tiene sentido: cuantos más haces, menos grano por haz — los dos efectos se compensan.",
            ],
            "solution": r"$\dfrac{3}{x}\cdot\dfrac{x}{5}=\dfrac{3}{5}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que buscó doceavos",
            "statement": (
                "Vuelve el registro de la apertura: dos tercios de la parva, y tres cuartos "
                "de eso. El escriba pasó las dos a doceavos, las sumó y anotó 17/12."
            ),
            "latex": r"\dfrac{2}{3}\cdot\dfrac{3}{4}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\dfrac{8}{12}+\dfrac{9}{12}=\dfrac{17}{12}",
            "error_note": (
                "Aplicó el procedimiento del riego a un problema que no era de juntar. El "
                "denominador común es la herramienta de la suma; aquí sobra y además miente."
            ),
            "correct_version": {
                "wrong_latex": r"\dfrac{2}{3}\cdot\dfrac{3}{4}=\dfrac{17}{12}",
                "right_latex": r"\dfrac{2}{3}\cdot\dfrac{3}{4}=\dfrac{6}{12}=\dfrac{1}{2}",
                "rows": [
                    {"wrong": "Igualar denominadores y sumar",
                     "right": "Multiplicar arriba con arriba y abajo con abajo"},
                    {"wrong": r"\dfrac{17}{12}\ \text{es más de una parva entera}",
                     "right": r"\dfrac{1}{2}\ \text{es media parva, y cabe}"},
                ],
            },
            "explain_prompt": (
                "Explica por qué un resultado mayor que 1 delata el error sin necesidad de "
                "rehacer la cuenta, y di qué operación sí habría dado 17/12."
            ),
            "steps": [
                "Tomo una parte de algo que ya era una parte: no puede salir más de lo que había.",
                "17/12 es más que la parva entera, así que la cuenta no era esa.",
                "Regla para no volver a caer: antes de operar, pregunta si es «y» (suma) o «de» (producto).",
            ],
            "solution": (
                "2/3 · 3/4 = 1/2. La suma habría dado 17/12, pero nadie pidió juntar las "
                "dos partes: la segunda estaba dentro de la primera."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El registro de la era va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Multiplica $\dfrac{3}{5}\cdot\dfrac{2}{7}$ y di cuánto vale el denominador.",
                "given_steps": [r"\dfrac{3\cdot 2}{5\cdot 7}"],
                "blanks": [{"id": "P1-b1", "label": r"5\cdot 7=", "answer": "35"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Multiplica $\dfrac{4}{9}\cdot\dfrac{3}{8}$ y simplifica.",
                "given_steps": [r"\dfrac{12}{72}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"72\div 12=", "answer": "6"},
                    {"id": "P2-b2", "label": r"\text{numerador simplificado}=", "answer": "1"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $\dfrac{2}{5}$ de una parva de $\,30\,$ medidas, "
                    "y de eso la mitad va a la troje. ¿Cuántas medidas llegan?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"\dfrac{1}{2}\cdot\dfrac{2}{5}\cdot 30=", "answer": "6"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de multiplicar y simplificar",
        "intro": r"$\dfrac{8}{15}\cdot\dfrac{25}{12}$. Los dos llegan a lo mismo con números muy distintos.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar y simplificar al final",
                "steps": [
                    r"\dfrac{8\cdot 25}{15\cdot 12}",
                    r"\dfrac{200}{180}",
                    r"\dfrac{10}{9}",
                ],
                "note": "Siempre funciona, pero hay que simplificar 200/180 sin equivocarse.",
            },
            {
                "label": "Método 2 · Simplificar en cruz antes",
                "steps": [
                    r"\dfrac{8}{12}\to\dfrac{2}{3},\quad \dfrac{25}{15}\to\dfrac{5}{3}",
                    r"\dfrac{2\cdot 5}{3\cdot 3}",
                    r"\dfrac{10}{9}",
                ],
                "note": "Números pequeños todo el rato y el resultado sale ya simplificado.",
            },
        ],
        "question": "¿Por qué se puede cruzar el 8 de arriba con el 12 de abajo, si están en fracciones distintas?",
        "insight": (
            "Porque al multiplicar todo acaba en un solo numerador y un solo denominador: "
            "el 8 y el 12 van a quedar arriba y abajo de la MISMA fracción, así que "
            "tacharlos ahora o después da igual. Ojo con generalizarlo: esto vale solo "
            "cuando la operación es un producto. En una suma, cruzar no significa nada — "
            "ahí no se juntan en una sola fracción hasta el final."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuánto es $\dfrac{3}{4}\cdot\dfrac{2}{7}$?",
            "options": [
                {"id": "ok", "text": r"$\dfrac{6}{28}=\dfrac{3}{14}$", "latex": r"\dfrac{3}{14}"},
                {"id": "common", "text": r"$\dfrac{29}{28}$", "latex": r"\dfrac{29}{28}"},
                {"id": "num", "text": r"$\dfrac{6}{7}$", "latex": r"\dfrac{6}{7}"},
                {"id": "cross", "text": r"$\dfrac{21}{8}$", "latex": r"\dfrac{21}{8}"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "common": "fb_f03_e1_common",
                "num": "fb_f03_e1_num",
                "cross": "fb_f03_e1_cross",
            },
            "misconception_by_option": {
                "common": "busca_comun_denominador_para_multiplicar",
                "num": "olvida_multiplicar_los_denominadores",
                "cross": "invierte_al_multiplicar",
            },
            "hints": {
                "n1": "Arriba con arriba y abajo con abajo.",
                "n2": "3 · 2 = 6 y 4 · 7 = 28.",
                "n3": "6/28 se simplifica entre 2.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Multiplica $\dfrac{2}{5}\cdot\dfrac{4}{9}$ y escribe el resultado como "
                "fracción, así: 5/12. No dejes espacios."
            ),
            "answer": "8/45",
            "hints": {
                "n1": "No hace falta denominador común.",
                "n2": "2 · 4 = 8.",
                "n3": "5 · 9 = 45.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "Una parva da 45 medidas de grano. Tres quintos son grano limpio y, de eso, "
                "dos tercios van a la troje. ¿Cuántas medidas llegan a la troje?"
            ),
            "expr": r"\dfrac{2}{3}\cdot\dfrac{3}{5}\cdot 45",
            "answer": "18",
            "hints": {
                "n1": "«De» significa por: multiplica las dos fracciones.",
                "n2": "2/3 · 3/5 = 6/15 = 2/5.",
                "n3": "2/5 de 45 son …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un escriba calcula $\dfrac{1}{2}\cdot\dfrac{1}{3}$ pasándolas a sextos y "
                r"anota $\dfrac{5}{6}$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "op", "text": r"Sumó en vez de multiplicar: el producto es $\dfrac{1}{6}$"},
                {"id": "common", "text": "Eligió mal el denominador común"},
                {"id": "simp", "text": "Olvidó simplificar el resultado"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "op",
            "feedback_by_option": {
                "op": "correct",
                "common": "fb_f03_e4_common",
                "simp": "fb_f03_e4_simp",
                "none": "fb_f03_e4_none",
            },
            "misconception_by_option": {
                "common": "busca_comun_denominador_para_multiplicar",
                "simp": "habito_deja_el_resultado_sin_simplificar",
                "none": "busca_comun_denominador_para_multiplicar",
            },
            "hints": {
                "n1": "La mitad de un tercio no puede ser casi la era entera.",
                "n2": "Tomar una parte de una parte da menos, no más.",
                "n3": "5/6 es lo que sale de SUMARLAS.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Antes de multiplicar dos fracciones hay que ponerlas "
                "con el mismo denominador.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: eso es para sumar; multiplicando se opera arriba con arriba"},
                {"id": "true", "text": "Verdadera: es el primer paso con cualquier par de fracciones"},
                {"id": "true_diff", "text": "Verdadera solo si los denominadores son distintos"},
                {"id": "false_never", "text": "Falsa: el denominador común no sirve para nada en ninguna operación"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_f03_e5_trap",
                "true_diff": "fb_f03_e5_diff",
                "false_never": "fb_f03_e5_never",
            },
            "misconception_by_option": {
                "true": "busca_comun_denominador_para_multiplicar",
                "true_diff": "busca_comun_denominador_para_multiplicar",
                "false_never": "sobregeneraliza_producto_de_fracciones_algebraicas",
            },
            "hints": {
                "n1": "Prueba con 1/2 · 1/3 de dos maneras.",
                "n2": "Multiplicando da 1/6; igualando y sumando da 5/6.",
                "n3": "Solo una de las dos es el producto.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": r"Selecciona TODAS las igualdades verdaderas.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$\dfrac{2}{3}\cdot\dfrac{5}{7}=\dfrac{10}{21}$", "latex": r"\dfrac{2}{3}\cdot\dfrac{5}{7}=\dfrac{10}{21}"},
                {"id": "b", "text": r"$\dfrac{3}{a}\cdot\dfrac{a}{4}=\dfrac{3}{4}$", "latex": r"\dfrac{3}{a}\cdot\dfrac{a}{4}=\dfrac{3}{4}"},
                {"id": "c", "text": r"$\dfrac{2}{3}\cdot\dfrac{5}{7}=\dfrac{29}{21}$", "latex": r"\dfrac{2}{3}\cdot\dfrac{5}{7}=\dfrac{29}{21}"},
                {"id": "d", "text": r"$\dfrac{2}{3}\cdot 6=\dfrac{2}{18}$", "latex": r"\dfrac{2}{3}\cdot 6=\dfrac{2}{18}"},
            ],
            "expected": ["a", "b"],
            "trap_options": ["c", "d"],
            "hints": {
                "n1": "Comprueba cada una multiplicando arriba y abajo.",
                "n2": "Un entero se escribe con 1 debajo, no debajo.",
                "n3": "29/21 es lo que sale de sumar, no de multiplicar.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "En la era se trillan h haces por jornada y cada haz da 8/h medidas de "
                "grano. Tres cuartos de lo que sale va a la troje. Con h = 5, ¿cuántas "
                "medidas llegan a la troje?"
            ),
            "expr": r"\dfrac{3}{4}\cdot h\cdot\dfrac{8}{h}",
            "answer": "6",
            "hints": {
                "n1": "Multiplica los haces por lo que da cada uno: h · 8/h.",
                "n2": "La h se cancela: salen 8 medidas, valga lo que valga h.",
                "n3": "Tres cuartos de 8 son …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se multiplica arriba con arriba?",
        "title": "Cuándo el denominador común sobra",
        "intro": (
            "El denominador común es la herramienta de una operación concreta. Estas filas "
            "dicen en cuáles sirve y en cuáles estorba."
        ),
        "rows": [
            {"symbol": r"\dfrac{2}{3}\cdot\dfrac{1}{5}", "name": "Producto de dos fracciones", "closed": "yes",
             "latex": r"\dfrac{2}{15}",
             "note": "Arriba con arriba y abajo con abajo. No hace falta igualar nada. Es el caso focal."},
            {"symbol": r"\dfrac{3}{x}\cdot\dfrac{x}{5}", "name": "Con letras que se cancelan", "closed": "yes",
             "latex": r"\dfrac{3}{5}",
             "note": "Todo acaba siendo factores de una sola fracción, así que la x se tacha."},
            {"symbol": r"\dfrac{8}{15}\cdot\dfrac{25}{12}", "name": "Se puede simplificar antes", "closed": "yes",
             "latex": r"\dfrac{10}{9}",
             "note": "Cruzar el 8 con el 12 está permitido justo porque es un producto."},
            {"symbol": r"\dfrac{2}{3}\cdot 6", "name": "Fracción por entero", "closed": "partial",
             "latex": r"\dfrac{2}{3}\cdot\dfrac{6}{1}=4",
             "note": "La regla es la misma, pero primero hay que ver el entero como 6/1. Sin ese paso, el 6 se coloca mal."},
            {"symbol": r"\dfrac{2}{3}+\dfrac{1}{5}", "name": "Una suma", "closed": "no",
             "latex": r"\dfrac{10}{15}+\dfrac{3}{15}",
             "note": "Aquí sí hace falta el denominador común. La herramienta no es mala: era de otra operación."},
            {"symbol": r"\dfrac{2}{3}\div\dfrac{1}{5}", "name": "Una división", "closed": "no",
             "latex": r"\dfrac{2}{3}\cdot\dfrac{5}{1}",
             "note": "Tampoco se multiplica directo: primero hay que dar la vuelta a una de las dos. Eso es el silo."},
        ],
        "outro": (
            "La cuarta fila es la que más se falla en un examen con prisa: un entero suelto "
            "no tiene aspecto de fracción y acaba multiplicando al denominador. Y las dos "
            "últimas dicen lo mismo desde fuera — cada operación tiene su ritual, y "
            "aplicar el de otra no es un rodeo, es un resultado distinto."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres registros de la era trabajados en este nodo?",
        "thumbnails": [r"\dfrac{2}{3}\cdot\dfrac{3}{4}", r"\dfrac{3}{x}\cdot\dfrac{x}{5}", r"\dfrac{8}{15}\cdot\dfrac{25}{12}"],
        "options": [
            {"id": "one_fraction", "text": "En los tres el producto acaba siendo una sola fracción, y por eso se puede tachar entre ellas", "correct": True},
            {"id": "no_common", "text": "En los tres el denominador común no hace ninguna falta", "correct": True},
            {"id": "bigger", "text": "En los tres el resultado es mayor que las fracciones de partida", "correct": False},
            {"id": "same_rule", "text": "En los tres se opera igual que en una suma", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Cierre de la era. La parva de hoy da 60 medidas. Cuatro quintos salen como "
            "grano limpio y, de ese grano, tres cuartos van a la troje del templo. "
            "¿Cuántas medidas llegan a la troje?"
        ),
        "polya": {
            "comprender": "Son dos partes encadenadas: una parte del total y después una parte de esa parte.",
            "planear": "«De» es por: multiplico 3/4 por 4/5 y aplico el resultado a las 60 medidas.",
            "ejecutar": "3/4 · 4/5 = 12/20 = 3/5. Y 3/5 de 60 son 36 medidas.",
            "comprobar": "Por pasos: 4/5 de 60 son 48, y 3/4 de 48 son 36 ✓. Si hubiera sumado las fracciones habría salido 31/20 del total, más de una parva.",
        },
        "prompt": "¿Cuántas medidas llegan a la troje?",
        "answer": "36",
        "hints": {
            "n1": "Multiplica las dos fracciones antes de tocar el 60.",
            "n2": "3/4 · 4/5 = 3/5.",
            "n3": "3/5 de 60 son …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otra parva. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya distingues el «y» de la suma del «de» del producto.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué tomar una "
            "parte de otra parte da MENOS."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es un tercio de 21?",
                "answer": "7",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $\dfrac{3}{4}\cdot\dfrac{1}{2}$?",
                "options": [
                    {"id": "ok", "text": r"$\dfrac{3}{8}$", "latex": r"\dfrac{3}{8}"},
                    {"id": "same", "text": r"$\dfrac{3}{2}$", "latex": r"\dfrac{3}{2}"},
                    {"id": "sum", "text": r"$\dfrac{5}{4}$", "latex": r"\dfrac{5}{4}"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "same": "olvida_multiplicar_los_denominadores",
                    "sum": "busca_comun_denominador_para_multiplicar",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿En cuál de estas operaciones hace falta un denominador común?",
                "options": [
                    {"id": "sum", "text": r"$\dfrac{1}{3}+\dfrac{1}{4}$"},
                    {"id": "mult", "text": r"$\dfrac{1}{3}\cdot\dfrac{1}{4}$"},
                    {"id": "both", "text": "En las dos"},
                ],
                "expected": "sum",
                "misconception_by_option": {
                    "mult": "confunde_la_operacion_dictada",
                    "both": "busca_comun_denominador_para_multiplicar",
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
        "default": "Pregunta primero si es un «y» o un «de»: la suma junta, el producto toma parte de una parte.",
        "fb_f03_e1_common": (
            "Ese es el resultado de sumarlas. → Multiplicando no hace falta igualar denominadores."
        ),
        "fb_f03_e1_num": "Multiplicaste arriba y copiaste un denominador. → Abajo también se multiplica.",
        "fb_f03_e1_cross": (
            "Cruzaste numerador con denominador. → Eso es dividir; aquí la operación es un producto."
        ),
        "fb_f03_e4_common": (
            "El denominador común estaba bien elegido; el problema es que no hacía falta. "
            "→ La operación era un producto."
        ),
        "fb_f03_e4_simp": "1/6 ya está simplificado. → Lo que falló fue la operación, no el último paso.",
        "fb_f03_e4_none": (
            "La mitad de un tercio es menos que un tercio. → 5/6 es casi la era entera."
        ),
        "fb_f03_e5_trap": (
            "El denominador común es el primer paso de la SUMA. → Multiplicando se opera "
            "directo, arriba con arriba."
        ),
        "fb_f03_e5_diff": (
            "Da igual si son iguales o distintos: multiplicando nunca hace falta. → 1/3 · 1/3 = 1/9."
        ),
        "fb_f03_e5_never": (
            "Te pasaste al otro extremo: para sumar sí es imprescindible. → Lo que sobra es "
            "usarlo en un producto."
        ),
    },
    "closing": (
        "Ya sabes tomar una parte de otra parte sin que el grano se multiplique solo. "
        "Queda el caso más raro de todos: cuando lo que hay que repartir se divide ENTRE "
        "una fracción y el resultado sale más grande. Eso se ve en el silo de simiente."
    ),
    "validation_status": "F5_F03_11bloques",
}
