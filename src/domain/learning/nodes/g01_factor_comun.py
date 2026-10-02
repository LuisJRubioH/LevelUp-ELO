"""G01 · El pesaje de entrada — sacar lo común es sacarlo TODO.

Primera sala del Almacén de la caravana (Casa de la Sabiduría, Bagdad).
Guía: Salim. Vocabulario propio: fardo, saco, báscula, tara, albarán, romana.
Nada de huellas ni calcos (G02), despiece ni muescas (G03), toneles ni duelas (G04).

Error focal: extraer un factor común incompleto — sacar el número y dejar la
letra, o sacar un divisor cualquiera en vez del MAYOR. Factorizar a medias no
está a medio bien: está mal, porque el resultado se puede seguir partiendo.

Ítems de práctica derivados de Hipertexto U5 p104 y p106 (A1a, A1b, A1d, A1h).
"""

NODE_ID = "ALG-N3-G01-FACTOR-COMUN"
CONCEPT_SLUG = "factor_comun_y_agrupacion"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "factor_comun_y_agrupacion",
    "misconception": "factor_comun_incompleto",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El pesaje de entrada · Factor común y agrupación",
    "house": "El pesaje de entrada",
    "guide": "Salim",
    "finish_label": "Pasar al cotejo de huellas",
    "title": "Sacar la mitad de lo común es dejar el trabajo a medias",
    "intro": (
        "En la sala de los troqueles estampabas: de dos piezas salía una. Aquí se hace el "
        "camino de vuelta. Llegan fardos ya cerrados y hay que averiguar de qué bultos "
        "estaban hechos. Y el primer error del almacén no es equivocarse: es parar antes de "
        "tiempo."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas en la puerta. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es el máximo común divisor de 6 y 9?",
                "answer": "3",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $2x(3x+4)$?",
                "options": [
                    {"id": "both", "text": r"$6x^{2}+8x$", "latex": r"6x^{2}+8x"},
                    {"id": "first", "text": r"$6x^{2}+4$", "latex": r"6x^{2}+4"},
                    {"id": "flat", "text": r"$6x+8x$", "latex": r"6x+8x"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "first": "distribuye_solo_al_primer_termino",
                    "flat": "no_suma_los_exponentes_al_multiplicar",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $3x^{2}+6x$, ¿qué tienen en común los dos términos?",
                "options": [
                    {"id": "both", "text": r"Un 3 y una $x$"},
                    {"id": "num", "text": "Solo el 3"},
                    {"id": "letter", "text": r"Solo la $x$"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "num": "factor_comun_incompleto",
                    "letter": "factor_comun_incompleto",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/07-alg-n3-caravana/g01-factor-comun-katia.png",
        "eyebrow": "KatIA · En el pesaje de entrada",
        "title": "El fardo que se volvió a abrir",
        "body": (
            "En la puerta del almacén hay una romana y un mostrador. Todo lo que llega se "
            "pesa, se abre y se anota en el albarán: de cuántos bultos iguales está hecho "
            "cada fardo.\n\n"
            "Salim empuja hacia KatIA un albarán tachado:\n\n"
            "«Entró un fardo de 6 arrobas de comino y 9 de comino molido. El mozo vio que "
            "los dos números se partían entre 3 y anotó: tres partes, una de 2 y otra de 3.»\n\n"
            "«Pero los dos bultos también compartían el molido. El fardo aún se podía partir "
            "otra vez, y el albarán salió firmado a medias. Tuvimos que desatarlo todo y "
            "volver a empezar.»"
        ),
        "question": (
            "Si dos bultos comparten un número Y una medida, ¿basta con sacar el número?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "todo", "text": "No: hay que sacar todo lo que compartan de una vez"},
                {"id": "numero", "text": "Sí: con el número basta, la letra queda dentro"},
                {"id": "orden", "text": "Depende del orden en que se saquen"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a tener una prueba para saber si un "
                "albarán está terminado, sin tener que fiarte del ojo."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "La prueba del albarán terminado",
        "body": (
            "Factorizar es deshacer una multiplicación. Y como toda operación inversa, se "
            "comprueba haciendo la de ida."
        ),
        "cases": [
            {
                "label": "Albarán a medias",
                "context": r"$6x^{2}+9x=3(2x^{2}+3x)$",
                "fraction": r"3(2x^{2}+3x)",
                "division": r"2x^{2}+3x\ \text{aún tiene }x\text{ común}",
                "note": (
                    "Multiplicando vuelve a salir el fardo, así que no está mal — pero "
                    "dentro del paréntesis todavía queda algo común. No está terminado."
                ),
            },
            {
                "label": "Albarán terminado",
                "context": r"$6x^{2}+9x=3x(2x+3)$",
                "fraction": r"3x(2x+3)",
                "division": r"2\ \text{y}\ 3\ \text{no comparten nada}",
                "note": (
                    "Ahora lo de dentro no se puede partir más: 2 y 3 no tienen divisor "
                    "común y ya no hay letra en los dos términos."
                ),
            },
        ],
        "resolution": (
            "El factor común se saca completo: el MCD de los coeficientes, y de cada letra "
            "la potencia MÁS PEQUEÑA que aparezca en todos los términos. La prueba de que "
            "está terminado es mirar dentro del paréntesis: si lo de dentro todavía comparte "
            "algo, falta trabajo."
        ),
    },
    "definition_title": "Factor común y agrupación",
    "definition_katex": (
        r"ab+ac = a(b+c) \qquad ax+ay+bx+by = (x+y)(a+b)"
    ),
    "definition": (
        "El FACTOR COMÚN se saca cuando todos los términos comparten algo: se toma el MCD de "
        "los coeficientes y la menor potencia de cada letra común. Lo común puede ser un "
        "binomio entero. Cuando no todos los términos comparten algo pero sí lo hacen por "
        "parejas, se AGRUPA: se saca el común de cada pareja y, si las dos dejan el mismo "
        "binomio, ese binomio se saca a su vez."
    ),
    "definition_symbols": [
        {
            "symbol": r"a(b+c)",
            "reads": "a por, b más c",
            "means": "el factor común fuera, lo que queda dentro",
        },
        {
            "symbol": r"6x^{2}+9x=3x(2x+3)",
            "reads": "seis equis cuadrado más nueve equis, igual a tres equis por dos equis más tres",
            "means": "MCD de 6 y 9 es 3; menor potencia de x es x¹",
        },
        {
            "symbol": r"3x(2x+1)+5(2x+1)",
            "reads": "tres equis por dos equis más uno, más cinco por dos equis más uno",
            "means": "aquí lo común es un binomio entero, no un monomio",
        },
        {
            "symbol": r"(x+y)(a+b)",
            "reads": "equis más ye, por a más b",
            "means": "el resultado de agrupar de dos en dos",
        },
        {
            "symbol": r"\text{MCD}",
            "reads": "máximo común divisor",
            "means": "el mismo de Atenas, ahora sobre coeficientes",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Un fardo de dos bultos",
            "title": "Números y letras, cada uno con su cuenta",
            "statement": (
                "Salim pesa un fardo anotado como $12x^{3}-18x^{2}$. ¿De qué bultos está hecho?"
            ),
            "latex": r"12x^{3}-18x^{2}",
            "image_slot": False,
            "steps": [
                "Coeficientes: el MCD de 12 y 18 es 6.",
                "Letra: x aparece con exponentes 3 y 2; me quedo con el MENOR, x².",
                "Factor común: 6x².",
                "Divido cada término: 12x³ ÷ 6x² = 2x, y −18x² ÷ 6x² = −3.",
                "Queda 6x²(2x − 3). Compruebo dentro: 2 y 3 no comparten nada y no hay x en los dos. Terminado.",
            ],
            "solution": r"$12x^{3}-18x^{2}=6x^{2}(2x-3)$",
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "¿Por qué se saca la potencia MENOR de la letra y no la mayor?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando no todos comparten",
            "title": "Agrupar de dos en dos",
            "statement": (
                "Otro fardo: $5x^{2}y-10x^{2}z+3y-6z$. Los cuatro bultos no comparten nada "
                "entre sí, pero por parejas sí."
            ),
            "latex": r"5x^{2}y-10x^{2}z+3y-6z",
            "image_slot": False,
            "steps": [
                "Los cuatro juntos no tienen factor común: el 3y no lleva x.",
                "Primera pareja: 5x²y − 10x²z = 5x²(y − 2z).",
                "Segunda pareja: 3y − 6z = 3(y − 2z).",
                "Las dos dejan el MISMO binomio, (y − 2z). Esa es la señal de que la agrupación sirve.",
                "Saco ese binomio: (y − 2z)(5x² + 3).",
            ],
            "solution": r"$5x^{2}y-10x^{2}z+3y-6z=(y-2z)(5x^{2}+3)$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El mozo que firmó el albarán a medias",
            "statement": (
                "Vuelve el fardo de la apertura, ahora con letras. El mozo anota "
                "$6x^{2}+9x$ así:"
            ),
            "latex": r"6x^{2}+9x",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"6x^{2}+9x=3(2x^{2}+3x)",
            "error_note": (
                "Sacó el MCD de los coeficientes y se olvidó de la letra. Lo de dentro "
                "todavía comparte una x."
            ),
            "correct_version": {
                "wrong_latex": r"6x^{2}+9x=3(2x^{2}+3x)",
                "right_latex": r"6x^{2}+9x=3x(2x+3)",
                "rows": [
                    {
                        "wrong": "Lo común son los números",
                        "right": "Lo común son los números Y las letras que estén en todos",
                    },
                    {
                        "wrong": "Multiplicando vuelve a salir, así que está bien",
                        "right": "Multiplicar solo prueba que no es falso, no que esté terminado",
                    },
                ],
            },
            "explain_prompt": (
                "Comprueba que la anotación del mozo multiplicada da el fardo original, y "
                "explica entonces por qué aun así está incompleta."
            ),
            "steps": [
                "3 · 2x² = 6x² y 3 · 3x = 9x. La igualdad es cierta.",
                "Pero dentro del paréntesis, 2x² y 3x comparten una x: se puede seguir.",
                "3(2x² + 3x) = 3 · x(2x + 3) = 3x(2x + 3).",
                "Regla para no volver a caer: después de sacar, MIRA DENTRO. Si lo de dentro comparte algo, no terminaste.",
            ],
            "solution": (
                "6x² + 9x = 3x(2x + 3). Factorizar a medias no está a medio bien: el albarán "
                "hay que rehacerlo."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El albarán va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Factoriza $8x^{3}+12x^{2}$.",
                "given_steps": [r"\text{MCD}(8,12)=4", r"\text{menor potencia}=x^{2}"],
                "blanks": [
                    {"id": "P1-b1", "label": r"8x^{3}\div 4x^{2}\ \text{, coeficiente}=", "answer": "2"}
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Factoriza $2ax+2ay+3bx+3by$ agrupando.",
                "given_steps": [r"2a(x+y)+3b(x+y)"],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{términos del binomio común}=", "answer": "2"},
                    {"id": "P2-b2", "label": r"\text{factores del resultado}=", "answer": "2"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $27a^{2}b^{3}-18a^{4}b^{5}+45ab^{4}$. Decide "
                    "primero si esto se agrupa o se saca factor común."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{coeficiente del factor común}=", "answer": "9"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de comprobar que el albarán está cerrado",
        "intro": r"$12x^{3}+8x^{2}$. Las dos llegan a $4x^{2}(3x+2)$; solo una avisa si te quedaste corto.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar de vuelta",
                "steps": [
                    r"4x^{2}(3x+2)",
                    r"4x^{2}\cdot 3x+4x^{2}\cdot 2",
                    r"12x^{3}+8x^{2}\ \checkmark",
                ],
                "note": "Confirma que no es falso. Pero 2x²(6x + 4) también pasa esta prueba.",
            },
            {
                "label": "Método 2 · Mirar dentro del paréntesis",
                "steps": [
                    r"4x^{2}(3x+2)\rightarrow 3\ \text{y}\ 2\ \text{sin divisor común}",
                    r"2x^{2}(6x+4)\rightarrow 6\ \text{y}\ 4\ \text{comparten}\ 2",
                    r"\text{la segunda no está terminada}",
                ],
                "note": "Distingue lo cierto de lo terminado, que es lo que hace falta aquí.",
            },
        ],
        "question": "¿Cuál de los dos detecta un factor común incompleto?",
        "insight": (
            "El segundo. Multiplicar de vuelta solo comprueba que la igualdad es cierta, y "
            "una factorización incompleta también es cierta: 2x²(6x + 4) da exactamente el "
            "mismo fardo. Por eso la comprobación de este nodo no es multiplicar, es "
            "MIRAR DENTRO: si lo que queda en el paréntesis todavía comparte un número o una "
            "letra, el trabajo sigue abierto."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál es la factorización COMPLETA de $6x^{2}+9x$?",
            "options": [
                {"id": "full", "text": r"$3x(2x+3)$", "latex": r"3x(2x+3)"},
                {"id": "half", "text": r"$3(2x^{2}+3x)$", "latex": r"3(2x^{2}+3x)"},
                {"id": "letter", "text": r"$x(6x+9)$", "latex": r"x(6x+9)"},
                {"id": "wrong", "text": r"$3x(2x+3x)$", "latex": r"3x(2x+3x)"},
            ],
            "expected": "full",
            "feedback_by_option": {
                "full": "correct",
                "half": "fb_g01_e1_half",
                "letter": "fb_g01_e1_letter",
                "wrong": "fb_g01_e1_wrong",
            },
            "misconception_by_option": {
                "half": "factor_comun_incompleto",
                "letter": "factor_comun_incompleto",
                "wrong": "divide_mal_al_sacar_el_factor",
            },
            "hints": {
                "n1": "Saca el MCD de 6 y 9, y también la letra que esté en los dos.",
                "n2": "Después mira dentro del paréntesis: ¿queda algo común?",
                "n3": "3 y una x.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Al factorizar $12x^{3}-18x^{2}$, ¿cuál es el coeficiente del factor común?"
            ),
            "expr": r"\text{MCD}(12,18)=6",
            "answer": "6",
            "hints": {
                "n1": "Es el máximo común divisor de los dos coeficientes.",
                "n2": "Los divisores comunes de 12 y 18 son 1, 2, 3 y 6.",
                "n3": "El mayor.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En $27a^{2}b^{3}-18a^{4}b^{5}+45ab^{4}$, ¿cuál es el exponente de $b$ en el "
                "factor común?"
            ),
            "expr": r"\min(3,5,4)=3",
            "answer": "3",
            "hints": {
                "n1": "De cada letra se saca la potencia MENOR que aparezca en todos.",
                "n2": "Los exponentes de b son 3, 5 y 4.",
                "n3": "El menor de los tres.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Al agrupar $3x(2x+1)+5(2x+1)$, ¿qué se saca como factor común?",
            "options": [
                {"id": "bin", "text": r"El binomio $(2x+1)$"},
                {"id": "x", "text": r"La letra $x$"},
                {"id": "num", "text": "Nada: no hay factor común"},
                {"id": "all", "text": r"$3x\cdot 5=15x$"},
            ],
            "expected": "bin",
            "feedback_by_option": {
                "bin": "correct",
                "x": "fb_g01_e4_x",
                "num": "fb_g01_e4_num",
                "all": "fb_g01_e4_all",
            },
            "misconception_by_option": {
                "x": "solo_busca_monomios_como_factor_comun",
                "num": "solo_busca_monomios_como_factor_comun",
                "all": "multiplica_en_vez_de_factorizar",
            },
            "hints": {
                "n1": "Lo común no tiene por qué ser un monomio.",
                "n2": "Mira qué aparece entero en los dos sumandos.",
                "n3": "El paréntesis (2x + 1) está en ambos.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un mozo anota $b(3a-2c)+4d(3a-2c)$ y firma el albarán. ¿Está terminado?"
            ),
            "options": [
                {
                    "id": "no",
                    "text": r"No: falta sacar el binomio común y queda $(3a-2c)(b+4d)$",
                },
                {"id": "yes", "text": "Sí: ya no hay ningún monomio común"},
                {"id": "wrong", "text": r"No: hay que multiplicar y dejarlo desarrollado"},
                {"id": "other", "text": r"No: falta sacar también un 4"},
            ],
            "expected": "no",
            "feedback_by_option": {
                "no": "correct",
                "yes": "fb_g01_e5_yes",
                "wrong": "fb_g01_e5_wrong",
                "other": "fb_g01_e5_other",
            },
            "misconception_by_option": {
                "yes": "factor_comun_incompleto",
                "wrong": "multiplica_en_vez_de_factorizar",
                "other": "divide_mal_al_sacar_el_factor",
            },
            "hints": {
                "n1": "La agrupación tiene dos pasos, y este es solo el primero.",
                "n2": "Los dos sumandos dejaron el mismo binomio.",
                "n3": "Ese binomio se saca a su vez.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Si al multiplicar de vuelta sale el fardo original, la "
                "factorización está terminada.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: eso prueba que es cierta, no que esté completa",
                },
                {"id": "true", "text": "Verdadera: si la igualdad se cumple, está terminada"},
                {
                    "id": "true_mono",
                    "text": "Verdadera cuando el factor sacado es un monomio",
                },
                {
                    "id": "false_never",
                    "text": "Falsa: multiplicar de vuelta no sirve para nada",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_g01_e6_trap",
                "true_mono": "fb_g01_e6_mono",
                "false_never": "fb_g01_e6_never",
            },
            "misconception_by_option": {
                "true": "factor_comun_incompleto",
                "true_mono": "factor_comun_incompleto",
                "false_never": "multiplica_en_vez_de_factorizar",
            },
            "hints": {
                "n1": "Prueba con 2x²(6x + 4): multiplica y mira qué sale.",
                "n2": "Sale 12x³ + 8x², el fardo correcto.",
                "n3": "Y sin embargo 6 y 4 todavía comparten un 2.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Salim revisa cuatro fardos. ¿Cuáles se pueden factorizar POR AGRUPACIÓN? "
                "Marca todas las que apliquen."
            ),
            "options": [
                {"id": "ok1", "text": r"$2ax+2ay+3bx+3by$"},
                {"id": "ok2", "text": r"$5x^{2}y-10x^{2}z+3y-6z$"},
                {"id": "no1", "text": r"$2x^{2}+6x+8x^{3}-10x^{4}$"},
                {"id": "no2", "text": r"$27a^{2}b^{3}-18a^{4}b^{5}+45ab^{4}$"},
            ],
            "expected": ["ok1", "ok2"],
            "valid_options": ["ok1", "ok2", "no1", "no2"],
            "trap_options": ["no1", "no2"],
            "feedback_by_option": {"ok1": "correct", "ok2": "correct"},
            "misconception_by_option": {
                "no1": "agrupa_sin_que_salga_el_mismo_binomio",
                "no2": "agrupa_sin_que_salga_el_mismo_binomio",
            },
            "hints": {
                "n1": "Para agrupar hacen falta parejas que dejen EL MISMO binomio.",
                "n2": "Con tres términos no hay forma de hacer dos parejas.",
                "n3": "Los que no se agrupan sí tienen factor común. Son dos de los cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Queda algo común dentro?",
        "title": "La diferencia entre cierto y terminado",
        "intro": (
            "Todas las filas de abajo son igualdades ciertas. La pregunta no es si son "
            "verdad: es si el albarán se puede cerrar."
        ),
        "rows": [
            {
                "name": "Número y letra sacados",
                "symbol": r"3x(2x+3)",
                "latex": r"6x^{2}+9x=3x(2x+3)",
                "closed": "yes",
                "note": "Dentro quedan 2 y 3, sin divisor común y sin letra compartida.",
            },
            {
                "name": "Solo el número",
                "symbol": r"3(2x^{2}+3x)",
                "latex": r"6x^{2}+9x=3(2x^{2}+3x)",
                "closed": "no",
                "note": "Cierto, pero dentro todavía hay una x en los dos términos.",
            },
            {
                "name": "Menor potencia de la letra",
                "symbol": r"6x^{2}(2x-3)",
                "latex": r"12x^{3}-18x^{2}=6x^{2}(2x-3)",
                "closed": "yes",
                "note": "MCD 6 y la potencia menor, x². Dentro no queda nada compartido.",
            },
            {
                "name": "Agrupación a medio hacer",
                "symbol": r"b(3a-2c)+4d(3a-2c)",
                "latex": r"(3a-2c)(b+4d)",
                "closed": "no",
                "note": (
                    "Los dos sumandos dejaron el mismo binomio y ese binomio todavía no se "
                    "ha sacado. Falta el segundo paso."
                ),
            },
            {
                "name": "Lo común es un binomio",
                "symbol": r"(2x+1)(3x+5)",
                "latex": r"3x(2x+1)+5(2x+1)=(2x+1)(3x+5)",
                "closed": "yes",
                "note": "Lo común no tiene que ser un monomio: aquí era un paréntesis entero.",
            },
            {
                "name": "Se esperaba agrupar y no salía",
                "symbol": r"2x(x+3+4x^{2}-5x^{3})",
                "latex": r"2x^{2}+6x+8x^{3}-10x^{4}",
                "closed": "partial",
                "note": (
                    "Por agrupación NO se puede: ninguna pareja deja el mismo binomio. Por "
                    "factor común SÍ, y así queda terminado. Que un método falle no significa "
                    "que el fardo no se abra."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **después de sacar, mira dentro.** Multiplicar de vuelta "
            "solo dice que no te equivocaste; mirar dentro dice si terminaste."
        ),
    },
    "abstraction_question": {
        "prompt": (
            "Las tres factorizaciones de abajo son ciertas. ¿Qué distingue a la primera de "
            "las otras dos?"
        ),
        "thumbnails": [
            r"12x^{3}+8x^{2}=4x^{2}(3x+2)",
            r"12x^{3}+8x^{2}=2x^{2}(6x+4)",
            r"12x^{3}+8x^{2}=4x(3x^{2}+2x)",
        ],
        "options": [
            {
                "id": "inside",
                "text": (
                    "Solo en la primera lo que queda dentro del paréntesis ya no comparte "
                    "nada"
                ),
                "correct": True,
            },
            {
                "id": "biggest",
                "text": "Solo la primera tiene el coeficiente más grande fuera",
                "correct": False,
            },
            {
                "id": "true",
                "text": "Solo la primera es una igualdad verdadera",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Salim recibe un fardo anotado como $20m^{4}-30m^{3}$. Si el factor común es "
            "$km^{p}$, ¿cuánto vale $k+p$?"
        ),
        "polya": [
            "Entender: hay que hallar el factor común completo y sumar su coeficiente y su exponente.",
            "Planear: MCD de los coeficientes, y menor potencia de la letra.",
            "Ejecutar: MCD(20, 30) = 10 y la menor potencia es m³, así que k = 10 y p = 3.",
            "Comprobar: 10m³(2m − 3), y dentro 2 y 3 no comparten nada ✓. 10 + 3 = 13.",
        ],
        "prompt": "¿Cuánto vale k + p?",
        "answer": "13",
        "hints": {
            "n1": "Primero el MCD de 20 y 30.",
            "n2": "Es 10. Ahora la menor potencia de m entre m⁴ y m³.",
            "n3": "10 + 3.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que sabes cerrar un albarán.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya miras dentro del paréntesis antes de firmar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el factor común "
            "completo antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuál es el máximo común divisor de 8 y 12?",
                "answer": "4",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuál es la factorización completa de $10x^{2}+15x$?",
                "options": [
                    {"id": "full", "text": r"$5x(2x+3)$", "latex": r"5x(2x+3)"},
                    {"id": "half", "text": r"$5(2x^{2}+3x)$", "latex": r"5(2x^{2}+3x)"},
                    {"id": "letter", "text": r"$x(10x+15)$", "latex": r"x(10x+15)"},
                ],
                "expected": "full",
                "misconception_by_option": {
                    "half": "factor_comun_incompleto",
                    "letter": "factor_comun_incompleto",
                },
            },
            {
                "id": "Q3",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"En $4a^{3}+8a$, ¿qué comparten los dos términos?",
                "options": [
                    {"id": "both", "text": r"Un 4 y una $a$"},
                    {"id": "num", "text": "Solo el 4"},
                    {"id": "letter", "text": r"Solo la $a$"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "num": "factor_comun_incompleto",
                    "letter": "factor_comun_incompleto",
                },
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de pasar al cotejo de huellas.",
            "consolidacion": "Resuelto con ayuda: la prueba de mirar dentro ya está, falta que salga sola.",
            "sin_ayuda": "Albarán cerrado. No dejaste nada común dentro del paréntesis.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Dentro del paréntesis ya no queda nada común.",
        "default": (
            "Después de sacar el factor, mira dentro del paréntesis: si lo que queda todavía "
            "comparte un número o una letra, falta trabajo."
        ),
        "fb_g01_e1_half": (
            "Es cierto, pero no está terminado: dentro quedan 2x² y 3x, y los dos llevan una "
            "x. Ese es el error del nodo."
        ),
        "fb_g01_e1_letter": (
            "Sacaste la letra y dejaste el número: dentro quedan 6 y 9, que comparten un 3."
        ),
        "fb_g01_e1_wrong": (
            "Ahí la división salió mal: 9x ÷ 3x = 3, no 3x. Multiplica de vuelta y verás que "
            "no da el fardo original."
        ),
        "fb_g01_e4_x": (
            "La x no está sola en los dos sumandos: el segundo es 5(2x + 1). Lo que sí está "
            "entero en ambos es el paréntesis."
        ),
        "fb_g01_e4_num": (
            "Sí lo hay, solo que no es un monomio. Mira qué aparece igual en los dos sumandos."
        ),
        "fb_g01_e4_all": (
            "Multiplicar los coeficientes va en la dirección contraria: aquí se trata de "
            "sacar, no de juntar."
        ),
        "fb_g01_e5_yes": (
            "Monomio no queda, cierto — pero sí queda un binomio: (3a − 2c) está en los dos "
            "sumandos y todavía no se ha sacado."
        ),
        "fb_g01_e5_wrong": (
            "Multiplicar deshace lo hecho. Lo que falta es el segundo paso de la agrupación, "
            "no volver atrás."
        ),
        "fb_g01_e5_other": (
            "El 4 solo está en el segundo sumando, así que no es común. Lo común es el "
            "binomio."
        ),
        "fb_g01_e6_trap": (
            "Una factorización incompleta también cumple la igualdad: 2x²(6x + 4) da "
            "12x³ + 8x². Multiplicar no distingue lo terminado de lo que va a medias."
        ),
        "fb_g01_e6_mono": (
            "El ejemplo que falla es justo con un monomio: 2x²(6x + 4) es un monomio fuera y "
            "sigue incompleto."
        ),
        "fb_g01_e6_never": (
            "Sí sirve: detecta los errores de división. Lo que no detecta es que te hayas "
            "quedado corto."
        ),
    },
    "closing": (
        "Ya sabes abrir un fardo por lo que comparten sus bultos, y sabes cuándo el albarán "
        "está cerrado. Pero algunos fardos no comparten nada y aun así se abren: llegan con "
        "una huella del troquel que los estampó. En la sala de al lado está el catálogo para "
        "reconocerlas."
    ),
    "validation_status": "F5_G01_11bloques",
}
