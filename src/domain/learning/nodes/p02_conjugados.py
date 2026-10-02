"""P02 · El cuño de la cenefa — cuando el término del medio se anula solo.

Segunda sala de La sala de los troqueles (Casa de la Sabiduría, Bagdad).
Guía: Rayhana. Vocabulario propio: cuño, cenefa, greca, franja, tira, espejo.
Nada de matrices ni orlas (P01), moldes ni capas (P03), bandejas ni parejas (P04).

Error focal: creer que (a + b)(a − b) da a² + b². Da a² − b²: los dos productos
cruzados son opuestos y se anulan, y lo que queda es una RESTA de cuadrados.

Ítems de práctica derivados de Hipertexto U4 p77 (A2a, A2c, A2e, A3e, A4a).
"""

NODE_ID = "ALG-N2-P02-CONJUGADOS"
CONCEPT_SLUG = "binomios_conjugados"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "binomios_conjugados",
    "misconception": "conjugado_da_suma_de_cuadrados",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El cuño de la cenefa · Binomios conjugados",
    "house": "El cuño de la cenefa",
    "guide": "Rayhana",
    "finish_label": "Pasar al molde de tres capas",
    "title": "Dos piezas que se diferencian en un signo, y el medio desaparece",
    "intro": (
        "En la matriz cuadrada apareció una orla que nadie pidió. Aquí pasa lo contrario: "
        "hay un producto donde el término del medio se va solo. Y no se va por magia — se "
        "va porque son dos tiras iguales con signos opuestos."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 13 × 7?",
                "answer": "91",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $+5m - 5m$?",
                "options": [
                    {"id": "zero", "text": "0"},
                    {"id": "ten", "text": r"$10m$", "latex": "10m"},
                    {"id": "keep", "text": r"$5m$", "latex": "5m"},
                ],
                "expected": "zero",
                "misconception_by_option": {
                    "ten": "suma_opuestos_como_si_fueran_iguales",
                    "keep": "opuestos_no_se_anulan",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Calcula 10² − 3².",
                "answer": "91",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/06-alg-n2-troqueles/p02-conjugados-katia.png",
        "eyebrow": "KatIA · En el cuño de la cenefa",
        "title": "La greca que sobraba por un lado y faltaba por el otro",
        "body": (
            "En esta mesa se estampan cenefas: tiras largas y estrechas que bordean una "
            "página. El cuño trabaja con dos medidas, un largo y un ancho.\n\n"
            "Rayhana pone un encargo sobre la mesa:\n\n"
            "«Una greca de 13 dedos de largo por 7 de ancho. Trece es diez y tres; siete es "
            "diez menos tres. El aprendiz vio los dos dieces y los dos treses y anotó: "
            "cien más nueve, ciento nueve.»\n\n"
            "«La greca ocupa noventa y uno. Le sobró tinta para dieciocho dedos que no "
            "existen, y el cuño se atascó.»"
        ),
        "question": "¿Por qué 13 × 7 da noventa y uno y no ciento nueve, si los números son 10 y 3?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "resta", "text": "Porque en realidad hay que restar, no sumar"},
                {"id": "cancela", "text": "Porque algo se suma por un lado y se quita por el otro"},
                {"id": "otro", "text": "Porque 13 × 7 no tiene nada que ver con 10 y 3"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decir exactamente qué tira se "
                "suma, cuál se quita, y por qué siempre miden lo mismo."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Las dos tiras que se comen entre sí",
        "body": (
            "Estampar (a + b) por (a − b) da cuatro productos, igual que cualquier otro "
            "par de binomios. Lo especial es lo que pasa con los dos del medio."
        ),
        "cases": [
            {
                "label": "Los cuatro productos",
                "context": r"$(a+b)(a-b)$ — término a término",
                "fraction": r"a\cdot a\;+\;a\cdot(-b)\;+\;b\cdot a\;+\;b\cdot(-b)",
                "division": r"a^{2}-ab+ab-b^{2}",
                "note": (
                    "Los dos del medio son −ab y +ab: la misma tira, una sumando y otra "
                    "restando."
                ),
            },
            {
                "label": "Lo que sobrevive",
                "context": r"Se anulan y queda una RESTA de cuadrados",
                "fraction": r"a^{2}\;\cancel{-ab}\;\cancel{+ab}\;-b^{2}",
                "division": r"a^{2}-b^{2}",
                "note": (
                    "Queda menos que a², no más. Por eso 13 × 7 se queda en 91 y no llega "
                    "a 100: le falta justo el cuadrado de 3."
                ),
            },
        ],
        "resolution": (
            "Dos binomios son conjugados cuando tienen los mismos dos términos y solo se "
            "diferencian en el signo del segundo. Su producto no tiene término del medio, y "
            "el resultado es una resta: el cuadrado del primero menos el cuadrado del segundo."
        ),
    },
    "definition_title": "Producto de binomios conjugados",
    "definition_katex": r"(a+b)(a-b) = a^{2} - b^{2}",
    "definition": (
        "Suma por diferencia da diferencia de cuadrados. Solo dos términos, no tres: los "
        "productos cruzados son opuestos y se anulan. Y el signo del resultado es SIEMPRE "
        "una resta, aunque los dos binomios lleven un más delante — porque el que resta es "
        "el segundo cuadrado, no el binomio."
    ),
    "definition_symbols": [
        {
            "symbol": r"(a+b)(a-b)",
            "reads": "a más b, por a menos b",
            "means": "los conjugados: mismos términos, distinto signo en el segundo",
        },
        {
            "symbol": r"-ab+ab=0",
            "reads": "menos a b más a b es cero",
            "means": "las dos tiras del medio, que se anulan entre sí",
        },
        {
            "symbol": r"a^{2}-b^{2}",
            "reads": "a al cuadrado menos b al cuadrado",
            "means": "lo único que queda: una diferencia, nunca una suma",
        },
        {
            "symbol": r"(x^{n}+1)(x^{n}-1)=x^{2n}-1",
            "reads": "equis a la ene más uno, por equis a la ene menos uno",
            "means": "el primero puede ser cualquier monomio; el troquel no cambia",
        },
        {
            "symbol": r"(x+y+1)(x+y-1)",
            "reads": "equis más ye más uno, por equis más ye menos uno",
            "means": "el primero puede ser un bloque entero: aquí a = x + y",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Una greca con el largo en dedos",
            "title": "Dos términos, no tres",
            "statement": (
                "Rayhana encarga una cenefa de $(x+6)$ de largo por $(x-6)$ de ancho. "
                "¿Cuánta greca ocupa?"
            ),
            "latex": r"(x+6)(x-6)",
            "image_slot": False,
            "steps": [
                "Cuadrado del primero: x · x = x².",
                "Tiras del medio: −6x y +6x. Suman cero, así que ni se escriben.",
                "Cuadrado del segundo: 6 · 6 = 36, y va restando.",
                "Queda x² − 36. Dos términos.",
                "Compruebo con x = 10: la greca mide 16 × 4 = 64, y 100 − 36 = 64 ✓.",
            ],
            "solution": r"$(x+6)(x-6)=x^{2}-36$",
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "¿Por qué las dos tiras del medio miden exactamente lo mismo, si una "
                    "viene del primer paréntesis y la otra del segundo?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando los términos no son letras sueltas",
            "title": "El troquel no mira qué hay dentro",
            "statement": (
                "Otro encargo: $(a^{3}-b^{3})(a^{3}+b^{3})$. Están al revés y son potencias, "
                "pero siguen siendo conjugados."
            ),
            "latex": r"(a^{3}-b^{3})(a^{3}+b^{3})",
            "image_slot": False,
            "steps": [
                "Primero: a³. Al cuadrado da a⁶, porque 3 · 2 = 6.",
                "Segundo: b³. Al cuadrado da b⁶.",
                "Las tiras del medio, −a³b³ y +a³b³, se anulan igual que antes.",
                "Queda a⁶ − b⁶.",
                "El orden de los paréntesis no importa: el que resta es el segundo TÉRMINO, no el segundo factor.",
            ],
            "solution": r"$(a^{3}-b^{3})(a^{3}+b^{3})=a^{6}-b^{6}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que sumó los dos cuadrados",
            "statement": (
                "Vuelve la greca de la apertura, ahora con letras. El aprendiz anota el "
                "encargo $(x+4)(x-4)$ así:"
            ),
            "latex": r"(x+4)(x-4)",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"(x+4)(x-4)=x^{2}+16",
            "error_note": (
                "Vio los dos cuadrados y los sumó. Pero el 16 viene de multiplicar +4 por "
                "−4, y eso da −16."
            ),
            "correct_version": {
                "wrong_latex": r"(x+4)(x-4)=x^{2}+16",
                "right_latex": r"(x+4)(x-4)=x^{2}-16",
                "rows": [
                    {
                        "wrong": "Los dos cuadrados se suman",
                        "right": "El segundo cuadrado se resta: sale de (+4)·(−4)",
                    },
                    {
                        "wrong": "La greca ocupa más que un cuadrado de lado x",
                        "right": "Ocupa menos: le falta justo el cuadrado del recorte",
                    },
                ],
            },
            "explain_prompt": (
                "Comprueba con x = 5 que la anotación del aprendiz da un número distinto, y "
                "di cuánta greca sobra en su cuenta."
            ),
            "steps": [
                "Con x = 5 la greca mide 9 × 1 = 9.",
                "La anotación del aprendiz da 25 + 16 = 41. Le sobran 32.",
                "Regla para no volver a caer: conjugados → SIEMPRE resta. Si escribiste un más, revisa.",
            ],
            "solution": (
                "(x + 4)(x − 4) = x² − 16. Suma por diferencia da diferencia de cuadrados, "
                "nunca suma."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El encargo va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Multiplica $(3m-4)(3m+4)$.",
                "given_steps": [r"(3m)^{2}=9m^{2}"],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{lo que se resta}=", "answer": "16"}
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Multiplica $\left(\dfrac{1}{2}x-1\right)\left(\dfrac{1}{2}x+1\right)$ y evalúa en $x=4$.",
                "given_steps": [r"\left(\tfrac{1}{2}x\right)^{2}=\tfrac{1}{4}x^{2},\quad 1^{2}=1"],
                "blanks": [
                    {"id": "P2-b1", "label": r"\tfrac{1}{4}\cdot 16=", "answer": "4"},
                    {"id": "P2-b2", "label": r"4-1=", "answer": "3"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $(8x^{2}y-3x)(3x+8x^{2}y)$. El segundo paréntesis "
                    "viene en otro orden — identifica cuál es el término que resta."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{exponente de }x\text{ en el primer cuadrado}=", "answer": "4"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de ver por qué el medio se va",
        "intro": r"$(x+5)(x-5)$. Una lo calcula; la otra explica por qué siempre pasa.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar y tachar",
                "steps": [
                    r"(x+5)(x-5)",
                    r"x^{2}-5x+5x-25",
                    r"x^{2}-25",
                ],
                "note": "Se ve el cero nacer, pero hay que escribir los cuatro productos cada vez.",
            },
            {
                "label": "Método 2 · Recortar y pegar",
                "steps": [
                    r"\text{Rectángulo de }(x+5)\text{ por }(x-5)",
                    r"\text{Corto la franja de 5 y la pego al otro lado}",
                    r"\text{Queda el cuadrado }x^{2}\text{ menos el cuadradito }25",
                ],
                "note": "No hace falta multiplicar: se ve que falta justo un cuadrado de lado 5.",
            },
        ],
        "question": "¿Cuál de los dos deja claro que el resultado es MENOR que x²?",
        "insight": (
            "El segundo. Multiplicando y tachando uno confirma el resultado, pero el signo "
            "menos sigue pareciendo un accidente del cálculo. Recortando y pegando se ve que "
            "la greca es un cuadrado al que le falta un trozo, y que ese trozo es siempre un "
            "cuadrado. Por eso la respuesta nunca puede ser una suma: no se le puede quitar "
            "algo a una figura y que salga más grande."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿A qué equivale $(a+b)(a-b)$?",
            "options": [
                {"id": "dif", "text": r"$a^{2}-b^{2}$", "latex": r"a^{2}-b^{2}"},
                {"id": "sum", "text": r"$a^{2}+b^{2}$", "latex": r"a^{2}+b^{2}"},
                {"id": "middle", "text": r"$a^{2}-2ab+b^{2}$", "latex": r"a^{2}-2ab+b^{2}"},
                {"id": "flat", "text": r"$a^{2}-b$", "latex": r"a^{2}-b"},
            ],
            "expected": "dif",
            "feedback_by_option": {
                "dif": "correct",
                "sum": "fb_p02_e1_sum",
                "middle": "fb_p02_e1_middle",
                "flat": "fb_p02_e1_flat",
            },
            "misconception_by_option": {
                "sum": "conjugado_da_suma_de_cuadrados",
                "middle": "confunde_conjugados_con_cuadrado_de_binomio",
                "flat": "no_eleva_el_segundo_termino",
            },
            "hints": {
                "n1": "Escribe los cuatro productos y mira los dos del medio.",
                "n2": "−ab y +ab suman cero.",
                "n3": "Prueba con a = 10 y b = 3: la greca mide 13 × 7 = 91.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Multiplica $(x+6)(x-6)$. Usa $\wedge$ para el exponente, así: x^2-36. "
                "No dejes espacios."
            ),
            "answer": "x^2-36",
            "hints": {
                "n1": "Las tiras del medio se anulan: quedan dos términos.",
                "n2": "El cuadrado del primero es x².",
                "n3": "El del segundo, 36, va restando.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Una greca mide $(x+9)$ de largo por $(x-9)$ de ancho. Con $x=11$, "
                "¿cuánta greca ocupa?"
            ),
            "expr": r"(x+9)(x-9)=x^{2}-81,\quad x=11",
            "answer": "40",
            "hints": {
                "n1": "Puedes multiplicar directo: 20 × 2.",
                "n2": "O usar el troquel: 121 − 81.",
                "n3": "Las dos vías dan lo mismo.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En $(a^{3}-b^{3})(a^{3}+b^{3})$, ¿cuál es el exponente de $a$ en el resultado?"
            ),
            "expr": r"(a^{3})^{2}=a^{6}",
            "answer": "6",
            "hints": {
                "n1": "El primer término se eleva al cuadrado.",
                "n2": "Elevar una potencia al cuadrado multiplica el exponente por 2.",
                "n3": "3 · 2.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un aprendiz anota $(2m-4)(2m+4)=2m^{2}-16$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "first", "text": r"El primero: $(2m)^{2}=4m^{2}$, no $2m^{2}$"},
                {"id": "sign", "text": r"El signo: debería ser $+16$"},
                {"id": "middle", "text": r"Falta el término del medio, $-16m$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "first",
            "feedback_by_option": {
                "first": "correct",
                "sign": "fb_p02_e5_sign",
                "middle": "fb_p02_e5_middle",
                "none": "fb_p02_e5_none",
            },
            "misconception_by_option": {
                "sign": "conjugado_da_suma_de_cuadrados",
                "middle": "confunde_conjugados_con_cuadrado_de_binomio",
                "none": "eleva_solo_la_letra_y_no_el_coeficiente",
            },
            "hints": {
                "n1": "El signo está bien: conjugados dan resta.",
                "n2": "Mira el primer término. ¿Qué se eleva al cuadrado, solo la m?",
                "n3": "(2m)² = 2² · m² = 4m².",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Como los dos paréntesis llevan los mismos términos, el "
                "resultado es la suma de sus cuadrados.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: es la resta, porque un cruzado sale negativo",
                },
                {"id": "true", "text": "Verdadera: los dos términos aparecen elevados al cuadrado"},
                {
                    "id": "true_pos",
                    "text": "Verdadera cuando el primer paréntesis es el de la suma",
                },
                {
                    "id": "false_middle",
                    "text": "Falsa: queda además un término del medio",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_p02_e6_trap",
                "true_pos": "fb_p02_e6_order",
                "false_middle": "fb_p02_e6_middle",
            },
            "misconception_by_option": {
                "true": "conjugado_da_suma_de_cuadrados",
                "true_pos": "conjugado_da_suma_de_cuadrados",
                "false_middle": "confunde_conjugados_con_cuadrado_de_binomio",
            },
            "hints": {
                "n1": "Prueba con a = 10 y b = 3: 13 × 7.",
                "n2": "91, no 109.",
                "n3": "La diferencia, 18, es 2 · 9: el cuadrado de 3 contado dos veces de más.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Rayhana revisa cuatro encargos. ¿En cuáles se anula el término del medio? "
                "Marca todas las que apliquen."
            ),
            "options": [
                {"id": "conj", "text": r"$(x+7)(x-7)$"},
                {"id": "swap", "text": r"$(3x-2)(2+3x)$"},
                {"id": "same", "text": r"$(x+7)(x+7)$"},
                {"id": "other", "text": r"$(x+7)(x-5)$"},
            ],
            "expected": ["conj", "swap"],
            "valid_options": ["conj", "swap", "same", "other"],
            "trap_options": ["same", "other"],
            "feedback_by_option": {"conj": "correct", "swap": "correct"},
            "misconception_by_option": {
                "same": "confunde_conjugados_con_cuadrado_de_binomio",
                "other": "cree_que_cualquier_par_de_binomios_cancela",
            },
            "hints": {
                "n1": "Se anula cuando los dos paréntesis tienen los MISMOS términos y difieren solo en un signo.",
                "n2": "El orden dentro del paréntesis da igual: 2 + 3x es lo mismo que 3x + 2.",
                "n3": "Son dos de los cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se anula el término del medio?",
        "title": "Cuándo el cuño deja dos piezas y cuándo tres",
        "intro": (
            "Todo el nodo cabe en una pregunta: ¿los dos productos cruzados son opuestos? "
            "Si lo son, se van. Si no, se quedan."
        ),
        "rows": [
            {
                "name": "Conjugados",
                "symbol": r"(a+b)(a-b)",
                "latex": r"a^{2}-b^{2}",
                "closed": "yes",
                "note": "−ab y +ab son opuestos: se anulan y quedan dos términos.",
            },
            {
                "name": "El mismo dos veces",
                "symbol": r"(a+b)(a+b)",
                "latex": r"a^{2}+2ab+b^{2}",
                "closed": "no",
                "note": "Los cruzados son iguales, no opuestos: se suman y dan la orla.",
            },
            {
                "name": "El mismo dos veces, restando",
                "symbol": r"(a-b)(a-b)",
                "latex": r"a^{2}-2ab+b^{2}",
                "closed": "no",
                "note": "Igual que arriba: los dos cruzados restan y se acumulan.",
            },
            {
                "name": "Conjugados al revés",
                "symbol": r"(a+b)(b-a)",
                "latex": r"b^{2}-a^{2}",
                "closed": "partial",
                "note": (
                    "El medio SÍ se anula, pero el resultado sale invertido: aquí el que "
                    "resta es a². Fíjate en qué término lleva el menos, no en qué paréntesis."
                ),
            },
            {
                "name": "Términos distintos",
                "symbol": r"(a+b)(a-c)",
                "latex": r"a^{2}-ac+ab-bc",
                "closed": "no",
                "note": "Los cruzados no son opuestos: no hay nada que anular.",
            },
            {
                "name": "Un bloque entero como primero",
                "symbol": r"(x+y+1)(x+y-1)",
                "latex": r"(x+y)^{2}-1",
                "closed": "yes",
                "note": "El «primero» puede ser una suma: aquí a = x + y. El troquel no cambia.",
            },
        ],
        "outro": (
            "La regla en una línea: **suma por diferencia da diferencia de cuadrados.** Y si "
            "el resultado te sale con un más entre los dos cuadrados, algo se rompió: la "
            "greca no puede ocupar más que el cuadrado del que salió."
        ),
    },
    "abstraction_question": {
        "prompt": (
            "Mira los tres productos. ¿Qué tienen en común, más allá de los números "
            "concretos?"
        ),
        "thumbnails": [
            r"(x+3)(x-3)=x^{2}-9",
            r"(2m+5)(2m-5)=4m^{2}-25",
            r"(a^{3}+b)(a^{3}-b)=a^{6}-b^{2}",
        ],
        "options": [
            {
                "id": "structure",
                "text": (
                    "En los tres el resultado tiene dos términos y el segundo resta, sea "
                    "cual sea lo que haya dentro del paréntesis"
                ),
                "correct": True,
            },
            {
                "id": "letters",
                "text": "En los tres el primer término es una letra sola elevada al cuadrado",
                "correct": False,
            },
            {
                "id": "numbers",
                "text": "En los tres el segundo término es un número",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Rayhana encarga una greca de $(x^{n}+1)$ por $(x^{n}-1)$. Si $n=3$ y $x=2$, "
            "¿cuánta greca ocupa?"
        ),
        "polya": [
            "Entender: son conjugados, con xⁿ de primer término y 1 de segundo.",
            "Planear: aplico el troquel, x^{2n} − 1, y luego sustituyo.",
            "Ejecutar: con n = 3 queda x⁶ − 1; con x = 2, 64 − 1 = 63.",
            "Comprobar: directo, (8 + 1)(8 − 1) = 9 · 7 = 63 ✓.",
        ],
        "prompt": "¿Cuántos dedos de greca ocupa?",
        "answer": "63",
        "hints": {
            "n1": "Con n = 3 y x = 2, ¿cuánto vale xⁿ?",
            "n2": "xⁿ = 8, así que los paréntesis son (8 + 1) y (8 − 1).",
            "n3": "9 · 7.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que conoces el cuño.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya ves por qué el medio se va, y por qué el resultado resta.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo los productos "
            "cruzados antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuánto es 12 × 8?",
                "answer": "96",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿A qué equivale $(m+9)(m-9)$?",
                "options": [
                    {"id": "dif", "text": r"$m^{2}-81$", "latex": r"m^{2}-81"},
                    {"id": "sum", "text": r"$m^{2}+81$", "latex": r"m^{2}+81"},
                    {"id": "middle", "text": r"$m^{2}-18m+81$", "latex": r"m^{2}-18m+81"},
                ],
                "expected": "dif",
                "misconception_by_option": {
                    "sum": "conjugado_da_suma_de_cuadrados",
                    "middle": "confunde_conjugados_con_cuadrado_de_binomio",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "Calcula 10² − 2².",
                "answer": "96",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de pasar al molde de tres capas.",
            "consolidacion": "Resuelto con ayuda: el cuño ya está, falta que salga solo.",
            "sin_ayuda": "Cenefa limpia. El término del medio ya no te sorprende.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Dos términos, y el segundo restando.",
        "default": (
            "Escribe los cuatro productos y mira los dos del medio: si son opuestos, se van "
            "y queda una resta."
        ),
        "fb_p02_e1_sum": (
            "Ese más es el error del nodo. El segundo cuadrado sale de multiplicar +b por "
            "−b, y eso da −b². Con a = 10 y b = 3: 91, no 109."
        ),
        "fb_p02_e1_middle": (
            "Eso es el cuadrado de un binomio, (a − b)². Aquí los cruzados son opuestos y se "
            "anulan: no queda término del medio."
        ),
        "fb_p02_e1_flat": (
            "Al segundo término también se le eleva al cuadrado: b · b = b², no b."
        ),
        "fb_p02_e5_sign": (
            "El signo está bien: conjugados siempre dan resta. El error está en el primer "
            "término."
        ),
        "fb_p02_e5_middle": (
            "No falta: en conjugados el término del medio se anula. Mira el primer término."
        ),
        "fb_p02_e5_none": (
            "Sí lo hay: (2m)² eleva el 2 y la m, así que da 4m², no 2m²."
        ),
        "fb_p02_e6_trap": (
            "Aparecen los dos cuadrados, sí, pero el segundo restando. Con 10 y 3 la greca "
            "mide 91 y la suma de cuadrados da 109."
        ),
        "fb_p02_e6_order": (
            "El orden de los paréntesis no cambia nada: multiplicar es conmutativo. Lo que "
            "manda es qué TÉRMINO lleva el menos."
        ),
        "fb_p02_e6_middle": (
            "La respuesta es falsa, pero no por eso: en conjugados el término del medio "
            "justamente NO queda. Se anula."
        ),
    },
    "closing": (
        "Ya tienes el segundo troquel: $(a+b)(a-b)=a^{2}-b^{2}$, dos términos y una resta. "
        "Fíjate en el par que llevas: uno añade una orla y el otro se come el medio. En la "
        "mesa siguiente hay un molde más alto, de tres capas, y allí no aparece un término "
        "de más — aparecen dos."
    ),
    "validation_status": "F5_P02_11bloques",
}
