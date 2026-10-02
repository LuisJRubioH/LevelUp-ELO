"""O04 · La caseta del capataz — tacharlo todo deja un uno, no una nada.

Cuarta y última sala de la obra de la pirámide. Guía: Bakenra. Vocabulario propio:
caseta del capataz, aguador, cántaro, ración de agua, censo, jornada. Nada de
cuerdas ni trineos (O01), poleas ni vales (O02), cinceles ni sillares (O03).

Error focal: creer que cuando el numerador y el denominador se cancelan por
completo el resultado es 0. Lo que queda es 1: cancelar es dividir, no borrar.
"""

NODE_ID = "ALG-N1-O04-COCIENTE"
CONCEPT_SLUG = "cociente_de_monomios"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "cociente_de_monomios",
    "misconception": "cancelar_completo_da_cero",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La caseta del capataz · Cociente de monomios",
    "house": "La caseta del capataz",
    "guide": "Bakenra",
    "finish_label": "Salir hacia los campos",
    "title": "Tacharlo todo deja un uno, no una nada",
    "intro": (
        "En el taller multiplicaste monomios sumando exponentes. Aquí toca el camino de "
        "vuelta: repartir. Y hay un momento del reparto en el que la mano tacha lo último "
        "que quedaba y no sabe qué escribir en su lugar."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar en la caseta. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 12 ÷ 4?",
                "answer": "3",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 7 ÷ 7?",
                "options": [
                    {"id": "one", "text": "1"},
                    {"id": "zero", "text": "0"},
                    {"id": "seven", "text": "7"},
                ],
                "expected": "one",
                "misconception_by_option": {
                    "zero": "cancelar_completo_da_cero",
                    "seven": "confunde_division_con_resta",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $\dfrac{x^{5}}{x^{2}}$?",
                "options": [
                    {"id": "three", "text": r"$x^{3}$", "latex": r"x^{3}"},
                    {"id": "seven", "text": r"$x^{7}$", "latex": r"x^{7}"},
                    {"id": "ten", "text": r"$x^{10}$", "latex": r"x^{10}"},
                ],
                "expected": "three",
                "misconception_by_option": {
                    "seven": "suma_los_exponentes_al_dividir",
                    "ten": "multiplica_los_exponentes_al_dividir",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/o04-cociente-katia.png",
        "eyebrow": "KatIA · En la caseta del capataz",
        "title": "El día que nadie bebió",
        "body": (
            "La caseta lleva el censo de la obra y el reparto del agua. Cada jornada se "
            "cuenta cuántos cántaros suben y entre cuántos aguadores se reparten.\n\n"
            "Bakenra señala una línea del censo de la semana pasada:\n\n"
            "«Subieron 6a³ cántaros y había 6a³ aguadores. El escriba tachó los seis, tachó "
            "las aes, tachó los cubos… y al quedarse sin nada que tachar escribió un cero. "
            "Ración por aguador: cero.»\n\n"
            "«Tenían el agua delante. La caseta les dijo que no les tocaba nada.»"
        ),
        "question": "Cuando arriba y abajo hay exactamente lo mismo, ¿qué queda al repartir?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Cero: se ha tachado todo y no queda nada escrito"},
                {"id": "b", "text": "Uno: a cada uno le toca una parte entera"},
                {"id": "c", "text": "Lo mismo que había arriba"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a saber por qué tachar hasta el final "
                "deja un 1, y por qué el 1 no se ve pero está."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Tachar de a pares",
        "body": "Dividir potencias es emparejar factores. Lo interesante pasa al final.",
        "cases": [
            {
                "label": "Sobran factores",
                "context": r"$\dfrac{x^{5}}{x^{2}}$ desplegado",
                "fraction": r"\dfrac{x\,x\,x\,x\,x}{x\,x}",
                "division": r"x^{3}",
                "note": "Cada x de abajo tacha una de arriba. Sobran tres: se restan los exponentes.",
            },
            {
                "label": "No sobra ninguno",
                "context": r"$\dfrac{x^{3}}{x^{3}}$ desplegado",
                "fraction": r"\dfrac{x\,x\,x}{x\,x\,x}",
                "division": r"1",
                "note": "Se emparejan todos. Cada pareja vale 1, y 1 · 1 · 1 = 1. No queda un cero: queda un uno.",
            },
        ],
        "resolution": (
            "Tachar no es borrar: es dividir cada factor entre sí mismo, y eso da 1. "
            "Mientras sobran factores el 1 no se nota, porque multiplicar por 1 no cambia "
            "nada. Cuando no sobra ninguno, el 1 es lo único que queda — y ahí es cuando "
            "hay que escribirlo."
        ),
    },
    "definition_title": "Cociente de monomios",
    "definition_katex": r"\dfrac{a x^{m}}{b x^{n}} = \dfrac{a}{b}\,x^{m-n}\qquad \dfrac{x^{n}}{x^{n}}=x^{0}=1",
    "definition": (
        "Para DIVIDIR dos monomios se dividen los coeficientes y, en cada letra, se RESTAN "
        "los exponentes. Si el exponente de arriba es mayor, la letra queda arriba; si es "
        "menor, queda abajo; si son iguales, la letra desaparece y en su lugar hay un 1. "
        "Los coeficientes tienen su propia cuenta: aunque las letras se vayan, el número "
        "que resulte de dividirlos se queda."
    ),
    "definition_symbols": [
        {"symbol": r"\dfrac{x^{5}}{x^{2}}=x^{3}", "reads": "equis cinco entre equis dos", "means": "se restan los exponentes"},
        {"symbol": r"\dfrac{x^{3}}{x^{3}}=1", "reads": "queda uno", "means": "se emparejan todos: el resultado es 1, no 0"},
        {"symbol": r"x^{0}=1", "reads": "equis a la cero", "means": "otra forma de escribir lo mismo"},
        {"symbol": r"\dfrac{x^{2}}{x^{5}}=\dfrac{1}{x^{3}}", "reads": "queda abajo", "means": "si sobran factores abajo, la letra se queda abajo"},
        {"symbol": r"\dfrac{15a^{3}}{5a^{3}}=3", "reads": "queda el coeficiente", "means": "las letras se van, el 3 se queda"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Cántaros por aguador",
            "title": "Dos cuentas separadas",
            "statement": (
                "Suben 12c⁴ cántaros y se reparten entre 3c² aguadores, donde c es el "
                "número de cuerdas de acarreo. ¿Cuántos cántaros toca a cada uno?"
            ),
            "latex": r"\dfrac{12c^{4}}{3c^{2}}",
            "image_slot": False,
            "steps": [
                "Separo la cuenta de los números y la de la letra.",
                "Coeficientes: 12 ÷ 3 = 4. Se dividen, como cualquier par de números.",
                "Letra: c⁴ entre c² empareja dos factores y sobran dos → 4 − 2 = 2.",
                "Queda 4c².",
                "Compruebo con c = 3: arriba 12 · 81 = 972, abajo 3 · 9 = 27, y 972 ÷ 27 = 36 = 4 · 9 ✓.",
            ],
            "solution": r"$\dfrac{12c^{4}}{3c^{2}}=4c^{2}$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué los coeficientes se dividen y los exponentes se restan, si es la misma división?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando las letras se van y el número no",
            "title": "Lo que sobrevive a la cancelación",
            "statement": (
                "Otra jornada: suben 15a³ cántaros y hay 5a³ aguadores. ¿Cuántos toca a "
                "cada uno?"
            ),
            "latex": r"\dfrac{15a^{3}}{5a^{3}}",
            "image_slot": False,
            "steps": [
                "Coeficientes: 15 ÷ 5 = 3.",
                "Letra: a³ entre a³ empareja todos los factores y no sobra ninguno → 3 − 3 = 0.",
                "a⁰ es 1, así que la letra desaparece del registro.",
                "Queda 3 · 1 = 3 cántaros por aguador.",
                "Fíjate: se fueron las letras, no el número. El 3 no se cancela con nada.",
            ],
            "solution": r"$\dfrac{15a^{3}}{5a^{3}}=3$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que se quedó sin nada que tachar",
            "statement": (
                "Vuelve el censo de la apertura: 6a³ cántaros entre 6a³ aguadores. El "
                "escriba tachó el 6, tachó la a, tachó el exponente, y escribió 0."
            ),
            "latex": r"\dfrac{6a^{3}}{6a^{3}}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\dfrac{6a^{3}}{6a^{3}}=0",
            "error_note": (
                "Confundió tachar con borrar. Tachar una pareja es dividirla entre sí "
                "misma, y eso deja un 1 en su sitio, no un hueco."
            ),
            "correct_version": {
                "wrong_latex": r"\dfrac{6a^{3}}{6a^{3}}=0",
                "right_latex": r"\dfrac{6a^{3}}{6a^{3}}=1",
                "rows": [
                    {"wrong": "No queda nada escrito, luego vale 0",
                     "right": "Cada pareja tachada vale 1, y el producto de unos es 1"},
                    {"wrong": "Ración por aguador: 0 cántaros",
                     "right": "Ración por aguador: 1 cántaro, que es justo lo que había"},
                ],
            },
            "explain_prompt": (
                "Explica con números por qué el resultado es 1, y di qué habría hecho falta "
                "arriba para que de verdad saliera 0."
            ),
            "steps": [
                "Pruebo con a = 2: arriba 6 · 8 = 48, abajo 6 · 8 = 48, y 48 ÷ 48 = 1.",
                "Para que el reparto diera 0 tendría que no haber subido ningún cántaro: 0 ÷ 48 = 0.",
                "Regla para no volver a caer: al tachar lo último, escribe el 1 antes de cerrar el registro.",
            ],
            "solution": (
                "6a³ ÷ 6a³ = 1. Repartir algo entre exactamente tantos como hay da una "
                "parte a cada uno, no ninguna."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El censo va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Divide $\dfrac{20c^{5}}{4c^{2}}$.",
                "given_steps": [r"20\div 4=5", r"5-2=3"],
                "blanks": [{"id": "P1-b1", "label": r"\text{exponente del resultado}=", "answer": "3"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Divide $\dfrac{18a^{4}}{6a^{4}}$ y di cuánto vale con $a=7$.",
                "given_steps": [r"18\div 6=3,\quad 4-4=0"],
                "blanks": [
                    {"id": "P2-b1", "label": r"a^{0}=", "answer": "1"},
                    {"id": "P2-b2", "label": r"3\cdot 1=", "answer": "3"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $\dfrac{24c^{3}}{8c}$ con $c=3$. Primero el "
                    "monomio, después el valor."
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"3c^{2}\ \text{con}\ c=3:", "answer": "27"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de dividir potencias",
        "intro": r"$\dfrac{a^{4}}{a^{4}}$. Es el caso en el que las dos maneras se separan.",
        "methods": [
            {
                "label": "Método 1 · Restar los exponentes",
                "steps": [
                    r"\dfrac{a^{4}}{a^{4}}",
                    r"4-4=0",
                    r"a^{0}=1",
                ],
                "note": "Directo, pero obliga a saberse de memoria que a⁰ vale 1.",
            },
            {
                "label": "Método 2 · Emparejar y tachar",
                "steps": [
                    r"\dfrac{a\,a\,a\,a}{a\,a\,a\,a}",
                    r"\dfrac{a}{a}\cdot\dfrac{a}{a}\cdot\dfrac{a}{a}\cdot\dfrac{a}{a}",
                    r"1\cdot 1\cdot 1\cdot 1=1",
                ],
                "note": "Más largo, pero enseña de dónde sale el 1 en vez de pedir que te lo creas.",
            },
        ],
        "question": "¿Cuál de los dos evita que alguien escriba 0 al tacharlo todo?",
        "insight": (
            "El segundo. Restando exponentes se llega a a⁰ y hay que saber qué significa; "
            "si no se sabe, el hueco se rellena con lo primero que suene a «nada», que es "
            "el cero. Emparejando se ve que cada pareja vale 1 y que multiplicar unos "
            "sigue dando uno. Por eso a⁰ = 1 no es un convenio raro: es lo que sale de "
            "dividir algo entre sí mismo."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuánto es $\dfrac{8a^{3}}{8a^{3}}$?",
            "options": [
                {"id": "one", "text": "1"},
                {"id": "zero", "text": "0"},
                {"id": "keep", "text": r"$a^{3}$", "latex": r"a^{3}"},
                {"id": "eight", "text": "8"},
            ],
            "expected": "one",
            "feedback_by_option": {
                "one": "correct",
                "zero": "fb_o04_e1_zero",
                "keep": "fb_o04_e1_keep",
                "eight": "fb_o04_e1_eight",
            },
            "misconception_by_option": {
                "zero": "cancelar_completo_da_cero",
                "keep": "no_cancela_la_parte_literal",
                "eight": "no_divide_los_coeficientes",
            },
            "hints": {
                "n1": "Arriba y abajo hay exactamente lo mismo.",
                "n2": "Cualquier cantidad dividida entre sí misma da…",
                "n3": "Prueba con a = 2: 64 ÷ 64.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Divide $\dfrac{20c^{6}}{5c^{2}}$ y escribe el resultado. Usa $\wedge$ "
                "para el exponente, así: 4c^4. No dejes espacios."
            ),
            "answer": "4c^4",
            "hints": {
                "n1": "Divide los coeficientes: 20 ÷ 5.",
                "n2": "Resta los exponentes: 6 − 2.",
                "n3": "Queda un 4 delante y la c elevada a 4.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Suben $18c^{4}$ cántaros y hay $6c^{2}$ aguadores. Con $c=2$, ¿cuántos "
                "cántaros toca a cada aguador?"
            ),
            "expr": r"\dfrac{18c^{4}}{6c^{2}}=3c^{2},\quad c=2",
            "answer": "12",
            "hints": {
                "n1": "Primero el monomio: 18 ÷ 6 = 3 y 4 − 2 = 2.",
                "n2": "Queda 3c².",
                "n3": "3 · 4 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un escriba anota $\dfrac{10a^{5}}{5a^{5}}=0$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "two", "text": r"Las letras sí se van, pero queda $10\div 5=2$"},
                {"id": "exp", "text": r"El exponente se resta mal: queda $a^{10}$"},
                {"id": "one", "text": "El resultado es 1, porque arriba y abajo hay lo mismo"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "two",
            "feedback_by_option": {
                "two": "correct",
                "exp": "fb_o04_e4_exp",
                "one": "fb_o04_e4_one",
                "none": "fb_o04_e4_none",
            },
            "misconception_by_option": {
                "exp": "suma_los_exponentes_al_dividir",
                "one": "no_divide_los_coeficientes",
                "none": "cancelar_completo_da_cero",
            },
            "hints": {
                "n1": "Las letras se cancelan del todo: hasta ahí bien.",
                "n2": "¿Y los coeficientes? Arriba hay 10 y abajo 5.",
                "n3": "No son iguales: no se cancelan, se dividen.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Cuando arriba y abajo se tacha todo, el resultado es 0.»"
            ),
            "options": [
                {"id": "false", "text": r"Falsa: es 1, porque cada pareja tachada vale $1$"},
                {"id": "true", "text": "Verdadera: no queda nada escrito"},
                {"id": "true_letters", "text": "Verdadera solo cuando lo que se tacha son letras"},
                {"id": "false_keep", "text": "Falsa: no se puede tachar todo, siempre queda la letra"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_o04_e5_trap",
                "true_letters": "fb_o04_e5_letters",
                "false_keep": "fb_o04_e5_keep",
            },
            "misconception_by_option": {
                "true": "cancelar_completo_da_cero",
                "true_letters": "cancelar_completo_da_cero",
                "false_keep": "no_cancela_la_parte_literal",
            },
            "hints": {
                "n1": "Prueba con números: 7 ÷ 7.",
                "n2": "Da 1, no 0.",
                "n3": "Tachar es dividir entre sí mismo, y eso deja un 1.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": r"Selecciona TODAS las igualdades verdaderas.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$\dfrac{x^{6}}{x^{2}}=x^{4}$", "latex": r"\dfrac{x^{6}}{x^{2}}=x^{4}"},
                {"id": "b", "text": r"$\dfrac{x^{6}}{x^{6}}=0$", "latex": r"\dfrac{x^{6}}{x^{6}}=0"},
                {"id": "c", "text": r"$\dfrac{9x^{4}}{3x^{4}}=3$", "latex": r"\dfrac{9x^{4}}{3x^{4}}=3"},
                {"id": "d", "text": r"$\dfrac{x^{6}}{x^{2}}=x^{3}$", "latex": r"\dfrac{x^{6}}{x^{2}}=x^{3}"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Resta los exponentes y comprueba el resto.",
                "n2": "Cuando las letras se van del todo queda 1, no 0.",
                "n3": "Y el coeficiente sigue su propia cuenta.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                r"El censo dice que subieron $30a^{4}$ cántaros y que hay $10a^{4}$ "
                r"aguadores. Con $a=5$, ¿cuántos cántaros toca a cada aguador?"
            ),
            "expr": r"\dfrac{30a^{4}}{10a^{4}},\quad a=5",
            "answer": "3",
            "hints": {
                "n1": "Las letras son iguales arriba y abajo: se cancelan.",
                "n2": "Pero los coeficientes no: 30 ÷ 10.",
                "n3": "El resultado no depende de a.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Qué sobrevive al reparto?",
        "title": "Qué queda después de emparejar",
        "intro": (
            "Tachar solo vale entre factores, y lo que deja no siempre es lo que parece. "
            "Estas seis filas son todos los finales posibles de un reparto."
        ),
        "rows": [
            {"symbol": r"\dfrac{x^{5}}{x^{2}}", "name": "Sobran factores arriba", "closed": "yes",
             "latex": r"x^{3}",
             "note": "El caso cómodo: se empareja lo que se puede y lo que sobra queda arriba."},
            {"symbol": r"\dfrac{12c^{4}}{3c^{2}}", "name": "Con coeficientes", "closed": "yes",
             "latex": r"4c^{2}",
             "note": "Dos cuentas a la vez: los números se dividen, los exponentes se restan."},
            {"symbol": r"\dfrac{x^{3}}{x^{3}}", "name": "Se empareja todo", "closed": "yes",
             "latex": r"1",
             "note": "Se tacha hasta el final y queda 1. Es el caso focal: 1, nunca 0."},
            {"symbol": r"\dfrac{15a^{3}}{5a^{3}}", "name": "Se van las letras, no el número", "closed": "partial",
             "latex": r"3",
             "note": "Las letras desaparecen, pero el 3 sobrevive: los coeficientes no se cancelaban, se dividían."},
            {"symbol": r"\dfrac{x^{2}}{x^{5}}", "name": "Sobran factores abajo", "closed": "partial",
             "latex": r"\dfrac{1}{x^{3}}",
             "note": "También se empareja, pero lo que sobra queda debajo. Arriba se queda el 1 de siempre."},
            {"symbol": r"\dfrac{x+3}{3}", "name": "Arriba hay una suma", "closed": "no",
             "latex": r"\dfrac{x+3}{3}",
             "note": "No hay nada que tachar: el 3 de arriba es un sumando, no un factor. Ese es el trabajo de los campos."},
        ],
        "outro": (
            "La tercera fila es la que costó una jornada sin agua. La cuarta y la quinta "
            "avisan de que «se canceló» no significa «desapareció todo»: casi siempre "
            "sobrevive algo, y muchas veces es un número. Y la última marca el límite de "
            "esta sala — donde hay una suma arriba, tachar deja de estar permitido."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres repartos trabajados en este nodo?",
        "thumbnails": [r"\dfrac{12c^{4}}{3c^{2}}", r"\dfrac{15a^{3}}{5a^{3}}", r"\dfrac{6a^{3}}{6a^{3}}"],
        "options": [
            {"id": "pairs", "text": "En los tres se empareja factor con factor, y cada pareja vale 1", "correct": True},
            {"id": "two_books", "text": "En los tres el coeficiente y el exponente llevan cuentas distintas", "correct": True},
            {"id": "empty", "text": "En los tres, si se tacha todo, el resultado es 0", "correct": False},
            {"id": "letters_stay", "text": "En los tres la letra sobrevive siempre en el resultado", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Censo de cierre de la jornada: subieron 24a⁵ cántaros y bajaron a repartirlos "
            "entre 8a⁵ aguadores, con a el número de aguadas del día. Hoy hubo 4 aguadas. "
            "¿Cuántos cántaros le tocan a cada aguador?"
        ),
        "polya": {
            "comprender": "Es un reparto: cántaros entre aguadores. Arriba y abajo llevan la misma letra con el mismo exponente.",
            "planear": "Divido coeficientes (24 ÷ 8) y resto exponentes (5 − 5). Después miro qué queda.",
            "ejecutar": "24 ÷ 8 = 3, y 5 − 5 = 0, así que a⁰ = 1. Queda 3 · 1 = 3.",
            "comprobar": "Con a = 4: arriba 24 · 1024 y abajo 8 · 1024; la potencia se va y quedan 24 ÷ 8 = 3 ✓. El resultado no depende de a.",
        },
        "prompt": "¿Cuántos cántaros toca a cada aguador?",
        "answer": "3",
        "hints": {
            "n1": "Las letras son idénticas arriba y abajo.",
            "n2": "Se cancelan y dejan un 1, no un 0.",
            "n3": "Queda 24 ÷ 8 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otro censo. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya escribes el 1 cuando se tacha hasta el final.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el emparejado: "
            "cada pareja tachada vale 1, no cero."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 18 ÷ 6?",
                "answer": "3",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 9 ÷ 9?",
                "options": [
                    {"id": "one", "text": "1"},
                    {"id": "zero", "text": "0"},
                    {"id": "nine", "text": "9"},
                ],
                "expected": "one",
                "misconception_by_option": {
                    "zero": "cancelar_completo_da_cero",
                    "nine": "confunde_division_con_resta",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $\dfrac{y^{7}}{y^{3}}$?",
                "options": [
                    {"id": "four", "text": r"$y^{4}$", "latex": r"y^{4}"},
                    {"id": "ten", "text": r"$y^{10}$", "latex": r"y^{10}"},
                    {"id": "twentyone", "text": r"$y^{21}$", "latex": r"y^{21}"},
                ],
                "expected": "four",
                "misconception_by_option": {
                    "ten": "suma_los_exponentes_al_dividir",
                    "twentyone": "multiplica_los_exponentes_al_dividir",
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
        "default": "Empareja factor con factor: cada pareja tachada vale 1, y los coeficientes llevan su propia cuenta.",
        "fb_o04_e1_zero": (
            "Tachar no es borrar. → Cada pareja vale 1; prueba con a = 2 y divide 64 entre 64."
        ),
        "fb_o04_e1_keep": (
            "Las letras sí se cancelan: arriba y abajo hay lo mismo. → Lo que queda en su sitio es un 1."
        ),
        "fb_o04_e1_eight": (
            "Los coeficientes también se dividen: 8 ÷ 8. → No se copia el de arriba."
        ),
        "fb_o04_e4_exp": (
            "Al dividir los exponentes se restan, no se suman. → 5 − 5 = 0, y a⁰ = 1."
        ),
        "fb_o04_e4_one": (
            "Sería 1 si los coeficientes fueran iguales, pero son 10 y 5. → 10 ÷ 5 = 2."
        ),
        "fb_o04_e4_none": (
            "Un reparto entre menos aguadores de los que hay cántaros no puede dar cero. "
            "→ Divide los coeficientes."
        ),
        "fb_o04_e5_trap": (
            "«No queda nada escrito» y «vale cero» no son lo mismo. → 7 ÷ 7 = 1, y ahí "
            "tampoco queda nada escrito."
        ),
        "fb_o04_e5_letters": (
            "Con números pasa igual: 8 ÷ 8 = 1. → La regla no distingue letras de cifras."
        ),
        "fb_o04_e5_keep": (
            "Te pasaste al otro extremo: sí se puede tachar todo. → Lo que no puede es "
            "quedar un hueco vacío."
        ),
    },
    "closing": (
        "Con esto la obra está terminada: sabes juntar lo semejante, restar una partida "
        "entera, repartir un factor y dividir monomios sin perder el 1 por el camino. Lo "
        "último que viste —una suma arriba de una fracción— es justo por donde empiezan "
        "los campos tras la crecida."
    ),
    "validation_status": "F5_O04_11bloques",
}
