"""G04 · La bodega de los toneles — una suma de cubos SÍ se abre, y no en dos binomios.

Cuarta sala del Almacén de la caravana (Casa de la Sabiduría, Bagdad).
Guía: Salim. Vocabulario propio: tonel, duela, aro, cuba, arqueo, bodega.
Nada de fardos ni básculas (G01), huellas ni calcos (G02), despiece ni muescas (G03).

Error focal: confundir la suma de cubos con el cubo de un binomio — escribir
a³ + b³ = (a + b)³. Son cosas distintas: una se factoriza en binomio por
trinomio, la otra es un producto ya hecho que se desarrolla en cuatro términos.

Contraste clave con G02: la suma de CUADRADOS no se abre, la suma de CUBOS sí.

Ítems derivados de Hipertexto U5 p111 (A1a, A1b, A2) y p124, más un ítem de
contraejemplo y uno de control sin calcular, que el libro no trae.
"""

NODE_ID = "ALG-N3-G04-CUBOS"
CONCEPT_SLUG = "suma_y_diferencia_de_cubos"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "suma_y_diferencia_de_cubos",
    "misconception": "suma_de_cubos_es_cubo_de_binomio",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La bodega de los toneles · Suma y diferencia de cubos",
    "house": "La bodega de los toneles",
    "guide": "Salim",
    "finish_label": "Salir hacia la sala de expedición",
    "title": "La suma de cubos sí se abre, y no en las piezas que esperas",
    "intro": (
        "En el cotejo de huellas aprendiste que una suma de cuadrados no sale de ningún "
        "troquel. Aquí viene el contraste: una suma de CUBOS sí se abre. Pero no en dos "
        "binomios, y no en lo que se le parece."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de bajar a la bodega. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es la raíz cúbica de 27?",
                "answer": "3",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $(x+2)^{3}$?",
                "options": [
                    {
                        "id": "four",
                        "text": r"$x^{3}+6x^{2}+12x+8$",
                        "latex": r"x^{3}+6x^{2}+12x+8",
                    },
                    {"id": "two", "text": r"$x^{3}+8$", "latex": r"x^{3}+8"},
                    {"id": "three", "text": r"$x^{3}+6x+8$", "latex": r"x^{3}+6x+8"},
                ],
                "expected": "four",
                "misconception_by_option": {
                    "two": "binomio_cubo_falta_terminos",
                    "three": "usa_los_coeficientes_del_cuadrado_en_el_cubo",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $2^{3}$?",
                "answer": "8",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/07-alg-n3-caravana/g04-cubos-katia.png",
        "eyebrow": "KatIA · En la bodega de los toneles",
        "title": "El arqueo que no cuadró",
        "body": (
            "Abajo, en la bodega, se guardan toneles. Cada tonel se mide por su arqueo: el "
            "volumen que cabe dentro, y ese volumen es siempre el cubo de una medida.\n\n"
            "Salim baja con una lámpara y señala una anotación en la pared:\n\n"
            "«Llegó una remesa marcada $x^{3}+8$. El mozo vio un cubo y un ocho, que también "
            "es un cubo, y anotó que venía de un solo tonel de medida $x+2$: escribió "
            "$(x+2)^{3}$.»\n\n"
            "«Probamos con $x=1$. La remesa arqueaba nueve; su tonel arqueaba veintisiete. "
            "Sobraban dieciocho de un vino que no existía.»"
        ),
        "question": (
            "Si $x^{3}$ y $8$ son los dos cubos, ¿por qué $x^{3}+8$ no es lo mismo que "
            "$(x+2)^{3}$?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "capas", "text": "Porque al cubo de un binomio le salen capas de en medio"},
                {"id": "igual", "text": "Son lo mismo: se puede repartir el exponente"},
                {"id": "nada", "text": "Porque una suma de cubos no se puede abrir de ninguna forma"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder abrir esa remesa, y vas a ver que "
                "sale en dos piezas de tamaños distintos."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Un binomio y un trinomio, no dos binomios",
        "body": (
            "Todos los troqueles anteriores dejaban dos binomios o un binomio al cuadrado. "
            "Este deja piezas de distinto tamaño."
        ),
        "cases": [
            {
                "label": "No es el cubo de un binomio",
                "context": r"$(x+2)^{3}$ frente a $x^{3}+8$",
                "fraction": r"(x+2)^{3}=x^{3}+6x^{2}+12x+8",
                "division": r"x^{3}+8\ \text{solo tiene dos términos}",
                "note": (
                    "El cubo de un binomio deja cuatro capas. La remesa solo tenía dos "
                    "términos: no puede ser eso."
                ),
            },
            {
                "label": "Sí es una suma de cubos",
                "context": r"$a^{3}+b^{3}=(a+b)(a^{2}-ab+b^{2})$",
                "fraction": r"x^{3}+8=(x+2)(x^{2}-2x+4)",
                "division": r"\text{binomio}\times\text{trinomio}",
                "note": (
                    "Estampando: x·x² − 2x² + 4x + 2x² − 4x + 8. Todo lo de en medio se anula "
                    "y quedan x³ y 8."
                ),
            },
        ],
        "resolution": (
            "La suma de cubos se abre en un binomio por un trinomio. El binomio lleva la SUMA "
            "de las raíces cúbicas; el trinomio lleva sus cuadrados y el producto con el "
            "signo CONTRARIO al del binomio. Y ese trinomio no es cuadrado perfecto: le falta "
            "el doble en el término del medio."
        ),
    },
    "definition_title": "Suma y diferencia de cubos",
    "definition_katex": (
        r"a^{3}+b^{3} = (a+b)(a^{2}-ab+b^{2}) \qquad a^{3}-b^{3} = (a-b)(a^{2}+ab+b^{2})"
    ),
    "definition": (
        "Un binomio se abre por este molde si sus dos términos son CUBOS exactos. El "
        "resultado es un binomio por un trinomio: el binomio repite el signo de la remesa; "
        "el trinomio lleva el cuadrado del primero, el producto de los dos con el signo "
        "CONTRARIO, y el cuadrado del segundo.\n\n"
        "Regla para el signo: «el mismo signo, el contrario, y siempre más»."
    ),
    "definition_symbols": [
        {
            "symbol": r"a^{3}+b^{3}=(a+b)(a^{2}-ab+b^{2})",
            "reads": "a al cubo más b al cubo",
            "means": "suma de cubos: binomio que suma, trinomio con el medio restando",
        },
        {
            "symbol": r"a^{3}-b^{3}=(a-b)(a^{2}+ab+b^{2})",
            "reads": "a al cubo menos b al cubo",
            "means": "diferencia de cubos: binomio que resta, trinomio con el medio sumando",
        },
        {
            "symbol": r"a^{2}-ab+b^{2}",
            "reads": "a cuadrado menos a b más b cuadrado",
            "means": "no es cuadrado perfecto: le falta el doble en el término del medio",
        },
        {
            "symbol": r"(a+b)^{3}",
            "reads": "a más b, al cubo",
            "means": "otra cosa: cuatro términos, y no se factoriza porque ya es un producto",
        },
        {
            "symbol": r"\sqrt[3]{8x^{6}}=2x^{2}",
            "reads": "raíz cúbica de ocho equis a la sexta",
            "means": "raíz del coeficiente, exponente entre 3",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Una remesa que suma",
            "title": "Las dos piezas, una por una",
            "statement": "Salim arquea una remesa marcada $8x^{3}+27$. ¿En qué toneles se abre?",
            "latex": r"8x^{3}+27",
            "image_slot": False,
            "steps": [
                "¿Son cubos exactos? 8x³ = (2x)³ y 27 = 3³. Sí.",
                "Raíces cúbicas: 2x y 3.",
                "Binomio: la suma de las raíces, con el mismo signo de la remesa → (2x + 3).",
                "Trinomio: (2x)² − (2x)(3) + 3² = 4x² − 6x + 9. El medio con el signo contrario.",
                "Queda (2x + 3)(4x² − 6x + 9). Compruebo con x = 0: 27 = 3 · 9 ✓.",
            ],
            "solution": r"$8x^{3}+27=(2x+3)(4x^{2}-6x+9)$",
            "self_explanation": {
                "step_index": 3,
                "prompt": (
                    "¿Por qué el término del medio del trinomio no lleva un 2 delante, si en "
                    "el cuadrado de un binomio sí lo llevaba?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Una remesa que resta",
            "title": "Los dos signos se cambian a la vez",
            "statement": "Otra remesa: $64x^{3}-125$. Todo igual, con los signos volteados.",
            "latex": r"64x^{3}-125",
            "image_slot": False,
            "steps": [
                "Cubos exactos: 64x³ = (4x)³ y 125 = 5³.",
                "Binomio: (4x − 5), repitiendo el signo de la remesa.",
                "Trinomio: (4x)² + (4x)(5) + 5² = 16x² + 20x + 25, con el medio sumando.",
                "Queda (4x − 5)(16x² + 20x + 25).",
                "Fíjate: el trinomio SIEMPRE acaba en más, tanto en la suma como en la diferencia.",
            ],
            "solution": r"$64x^{3}-125=(4x-5)(16x^{2}+20x+25)$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El mozo que arqueó un tonel de más",
            "statement": (
                "Vuelve la remesa de la apertura. El mozo anota $x^{3}+1$ así:"
            ),
            "latex": r"x^{3}+1",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"x^{3}+1=(x+1)^{3}",
            "error_note": (
                "Confundió la suma de dos cubos con el cubo de una suma. Son cosas distintas: "
                "una tiene dos términos, la otra cuatro."
            ),
            "correct_version": {
                "wrong_latex": r"x^{3}+1=(x+1)^{3}",
                "right_latex": r"x^{3}+1=(x+1)(x^{2}-x+1)",
                "rows": [
                    {
                        "wrong": "Dos cubos sumando salen de un binomio al cubo",
                        "right": "Salen de un binomio por un trinomio",
                    },
                    {
                        "wrong": "(x+1)³ tiene dos términos",
                        "right": "(x+1)³ = x³ + 3x² + 3x + 1: tiene cuatro",
                    },
                ],
            },
            "explain_prompt": (
                "Comprueba con $x=2$ las dos expresiones y di cuánto se separan. Después "
                "estampa la factorización correcta."
            ),
            "steps": [
                "Con x = 2: x³ + 1 = 9. Y (x + 1)³ = 27. Se separan en 18.",
                "La correcta: (2 + 1)(4 − 2 + 1) = 3 · 3 = 9 ✓.",
                "Contar términos es la prueba rápida: la remesa tiene dos, un cubo de binomio tendría cuatro.",
                "Regla para no volver a caer: suma de cubos → binomio POR trinomio. Nunca un solo paréntesis.",
            ],
            "solution": (
                "x³ + 1 = (x + 1)(x² − x + 1). El cubo de un binomio es otra cosa y tiene "
                "cuatro términos."
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
                "statement": r"Factoriza $x^{3}+27$.",
                "given_steps": [r"\sqrt[3]{x^{3}}=x,\quad \sqrt[3]{27}=3", r"\text{binomio}:(x+3)"],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{coeficiente del medio del trinomio, sin signo}=", "answer": "3"}
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Factoriza $8x^{3}-27$.",
                "given_steps": [r"(2x)^{3}-3^{3}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{primer término del trinomio}: (2x)^{2}\ \text{, coeficiente}=", "answer": "4"},
                    {"id": "P2-b2", "label": r"\text{medio}: (2x)(3)\ \text{, coeficiente}=", "answer": "6"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $x^{6}-64$. Se puede abrir por dos caminos — di "
                    "cuántos factores quedan si empiezas por diferencia de cuadrados."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{número de factores finales}=", "answer": "4"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para abrir la misma remesa",
        "intro": r"$x^{6}-64$. Es a la vez diferencia de cuadrados y diferencia de cubos.",
        "methods": [
            {
                "label": "Método 1 · Empezar por cuadrados",
                "steps": [
                    r"x^{6}-64=(x^{3})^{2}-8^{2}",
                    r"(x^{3}+8)(x^{3}-8)",
                    r"(x+2)(x^{2}-2x+4)(x-2)(x^{2}+2x+4)",
                ],
                "note": "Cuatro factores, y todos irreducibles. Termina.",
            },
            {
                "label": "Método 2 · Empezar por cubos",
                "steps": [
                    r"x^{6}-64=(x^{2})^{3}-4^{3}",
                    r"(x^{2}-4)(x^{4}+4x^{2}+16)",
                    r"(x+2)(x-2)(x^{4}+4x^{2}+16)",
                ],
                "note": "Llega a lo mismo, pero el trinomio de grado 4 aún se puede partir.",
            },
        ],
        "question": "¿Por qué conviene empezar por la diferencia de cuadrados?",
        "insight": (
            "Porque parte en trozos más pequeños desde el principio, y cada trozo cae en un "
            "molde conocido. Empezando por cubos se llega a un trinomio de grado 4 que "
            "todavía se puede abrir, y hay que darse cuenta. Las dos rutas dan el mismo "
            "resultado —la factorización completa es única— pero una llega antes al final. "
            "Cuando un fardo admite dos moldes, empieza por el que deje los trozos más chicos."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál es la factorización de $x^{3}+8$?",
            "options": [
                {"id": "ok", "text": r"$(x+2)(x^{2}-2x+4)$", "latex": r"(x+2)(x^{2}-2x+4)"},
                {"id": "cube", "text": r"$(x+2)^{3}$", "latex": r"(x+2)^{3}"},
                {"id": "conj", "text": r"$(x+2)(x-2)$", "latex": r"(x+2)(x-2)"},
                {"id": "sq", "text": r"$(x+2)(x^{2}+2x+4)$", "latex": r"(x+2)(x^{2}+2x+4)"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "cube": "fb_g04_e1_cube",
                "conj": "fb_g04_e1_conj",
                "sq": "fb_g04_e1_sq",
            },
            "misconception_by_option": {
                "cube": "suma_de_cubos_es_cubo_de_binomio",
                "conj": "aplica_diferencia_de_cuadrados_a_los_cubos",
                "sq": "no_cambia_el_signo_del_medio_del_trinomio",
            },
            "hints": {
                "n1": "Las raíces cúbicas son x y 2.",
                "n2": "El binomio repite el signo de la remesa.",
                "n3": "En el trinomio, el término del medio lleva el signo CONTRARIO.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuál es la raíz cúbica de $8x^{6}$? Escribe solo el coeficiente.",
            "expr": r"\sqrt[3]{8x^{6}}=2x^{2}",
            "answer": "2",
            "hints": {
                "n1": "La raíz cúbica del coeficiente y el exponente entre 3.",
                "n2": "¿Qué número al cubo da 8?",
                "n3": "2 · 2 · 2 = 8.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En la factorización de $64x^{3}-125$, ¿cuál es el coeficiente del término "
                "del medio del trinomio, sin signo?"
            ),
            "expr": r"(4x)(5)=20x",
            "answer": "20",
            "hints": {
                "n1": "Las raíces cúbicas son 4x y 5.",
                "n2": "El medio del trinomio es el producto de las dos raíces.",
                "n3": "4 · 5, y sin el doble que llevaba el cuadrado de binomio.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Sin factorizar: ¿cuántos términos tiene el SEGUNDO factor de una suma de "
                "cubos?"
            ),
            "expr": r"a^{2}-ab+b^{2}",
            "answer": "3",
            "hints": {
                "n1": "La suma de cubos se abre en dos piezas de distinto tamaño.",
                "n2": "La primera es un binomio.",
                "n3": "La segunda es un trinomio.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un mozo anota $x^{3}-27=(x-3)(x^{2}-3x+9)$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "mid", "text": r"El medio del trinomio: debería ser $+3x$"},
                {"id": "bin", "text": r"El binomio: debería ser $(x+3)$"},
                {"id": "last", "text": r"El último del trinomio: debería ser $-9$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "mid",
            "feedback_by_option": {
                "mid": "correct",
                "bin": "fb_g04_e5_bin",
                "last": "fb_g04_e5_last",
                "none": "fb_g04_e5_none",
            },
            "misconception_by_option": {
                "bin": "no_repite_el_signo_en_el_binomio",
                "last": "cree_que_el_trinomio_puede_acabar_restando",
                "none": "no_cambia_el_signo_del_medio_del_trinomio",
            },
            "hints": {
                "n1": "El binomio está bien: repite el signo de la remesa.",
                "n2": "El del medio del trinomio lleva el signo CONTRARIO al del binomio.",
                "n3": "Binomio con menos → medio del trinomio con más.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Como una suma de cuadrados no se factoriza, una suma de "
                "cubos tampoco.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: la de cubos sí se abre, en binomio por trinomio",
                },
                {"id": "true", "text": "Verdadera: ninguna suma se factoriza"},
                {
                    "id": "true_even",
                    "text": "Verdadera para exponentes pares e impares por igual",
                },
                {
                    "id": "false_cube",
                    "text": r"Falsa: la de cubos se abre como $(a+b)^{3}$",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_g04_e6_trap",
                "true_even": "fb_g04_e6_even",
                "false_cube": "fb_g04_e6_cube",
            },
            "misconception_by_option": {
                "true": "cree_que_ninguna_suma_se_factoriza",
                "true_even": "cree_que_ninguna_suma_se_factoriza",
                "false_cube": "suma_de_cubos_es_cubo_de_binomio",
            },
            "hints": {
                "n1": "Estampa (x + 2)(x² − 2x + 4) y mira qué sale.",
                "n2": "Todo lo de en medio se anula y quedan x³ y 8.",
                "n3": "La suma de cuadrados no se abre; la de cubos sí. El exponente importa.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Sin abrir ninguno: ¿cuáles de estos son suma o diferencia de CUBOS? Marca "
                "todas las que apliquen."
            ),
            "options": [
                {"id": "ok1", "text": r"$x^{3}+64$"},
                {"id": "ok2", "text": r"$27a^{3}-1$"},
                {"id": "no1", "text": r"$x^{3}+9$"},
                {"id": "no2", "text": r"$x^{2}+64$"},
            ],
            "expected": ["ok1", "ok2"],
            "valid_options": ["ok1", "ok2", "no1", "no2"],
            "trap_options": ["no1", "no2"],
            "feedback_by_option": {"ok1": "correct", "ok2": "correct"},
            "misconception_by_option": {
                "no1": "no_verifica_que_sean_cubos_exactos",
                "no2": "no_verifica_que_sean_cubos_exactos",
            },
            "hints": {
                "n1": "Los DOS términos tienen que ser cubos exactos.",
                "n2": "9 no es cubo de ningún entero: 2³ = 8 y 3³ = 27.",
                "n3": "En x² + 64 el primero es un cuadrado, no un cubo. Son dos de los cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Es una suma o diferencia de cubos?",
        "title": "Con dos términos, el exponente decide",
        "intro": (
            "En el cotejo de huellas la suma se quedaba cerrada. Aquí depende del exponente, "
            "y esta es la lista."
        ),
        "rows": [
            {
                "name": "Suma de cubos",
                "symbol": r"x^{3}+8",
                "latex": r"(x+2)(x^{2}-2x+4)",
                "closed": "yes",
                "note": "Los dos son cubos exactos. Se abre en binomio por trinomio.",
            },
            {
                "name": "Diferencia de cubos",
                "symbol": r"x^{3}-27",
                "latex": r"(x-3)(x^{2}+3x+9)",
                "closed": "yes",
                "note": "Mismo molde con los dos signos volteados. El trinomio siempre acaba en más.",
            },
            {
                "name": "Suma de cuadrados",
                "symbol": r"x^{2}+64",
                "latex": r"\text{no se factoriza}",
                "closed": "no",
                "note": "El hueco del catálogo, que sigue ahí. Con exponente 2 la suma no se abre.",
            },
            {
                "name": "El segundo no es cubo exacto",
                "symbol": r"x^{3}+9",
                "latex": r"\sqrt[3]{9}\notin\mathbb{Z}",
                "closed": "no",
                "note": "Entre 8 y 27 no hay ningún cubo. El molde no aplica.",
            },
            {
                "name": "Un producto ya hecho",
                "symbol": r"(x+2)^{3}",
                "latex": r"x^{3}+6x^{2}+12x+8",
                "closed": "no",
                "note": (
                    "No es una suma de cubos: es un cubo de binomio, ya factorizado. Tiene "
                    "cuatro términos al desarrollarlo, no dos."
                ),
            },
            {
                "name": "Cuadrado y cubo a la vez",
                "symbol": r"x^{6}-64",
                "latex": r"(x+2)(x^{2}-2x+4)(x-2)(x^{2}+2x+4)",
                "closed": "partial",
                "note": (
                    "Cabe en los dos moldes. Los dos llegan al mismo sitio, pero empezando "
                    "por cuadrados se termina antes."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **con dos términos, mira el exponente.** Al cuadrado solo "
            "se abre la resta; al cubo se abren las dos, y en un binomio por un trinomio."
        ),
    },
    "abstraction_question": {
        "prompt": "Los tres tienen dos términos. ¿Qué decide cuál se abre y en qué piezas?",
        "thumbnails": [
            r"x^{2}-9",
            r"x^{2}+9",
            r"x^{3}+27",
        ],
        "options": [
            {
                "id": "exp",
                "text": (
                    "El exponente y el signo: al cuadrado solo se abre la resta, al cubo las "
                    "dos, y en piezas distintas"
                ),
                "correct": True,
            },
            {
                "id": "sign",
                "text": "Solo el signo: la resta se abre siempre y la suma nunca",
                "correct": False,
            },
            {
                "id": "size",
                "text": "El tamaño del número que acompaña",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Salim arquea la remesa $125m^{3}+8$. Si se abre como $(am+b)(\\dots)$, ¿cuánto "
            "vale $a+b$?"
        ),
        "polya": [
            "Entender: hay que hallar las raíces cúbicas y sumar sus coeficientes.",
            "Planear: raíz cúbica de cada término; el binomio lleva la suma de ambas.",
            "Ejecutar: ∛(125m³) = 5m y ∛8 = 2, así que a = 5 y b = 2.",
            "Comprobar: (5m + 2)(25m² − 10m + 4) estampa 125m³ + 8 ✓. Y 5 + 2 = 7.",
        ],
        "prompt": "¿Cuánto vale a + b?",
        "answer": "7",
        "hints": {
            "n1": "¿Qué número al cubo da 125?",
            "n2": "5. Y la raíz cúbica de 8 es 2.",
            "n3": "5 + 2.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que conoces el molde de los toneles.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya no confundes la suma de cubos con el cubo de una suma.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el contraste entre "
            "los dos moldes antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuál es la raíz cúbica de 64?",
                "answer": "4",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuál es la factorización de $x^{3}+1$?",
                "options": [
                    {"id": "ok", "text": r"$(x+1)(x^{2}-x+1)$", "latex": r"(x+1)(x^{2}-x+1)"},
                    {"id": "cube", "text": r"$(x+1)^{3}$", "latex": r"(x+1)^{3}"},
                    {"id": "none", "text": "No se puede factorizar"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "cube": "suma_de_cubos_es_cubo_de_binomio",
                    "none": "cree_que_ninguna_suma_se_factoriza",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuánto es $3^{3}$?",
                "answer": "27",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de salir hacia la sala de expedición.",
            "consolidacion": "Resuelto con ayuda: el molde ya está, falta que salga solo.",
            "sin_ayuda": "Arqueo cuadrado. Distingues los dos moldes de tres sin dudar.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Binomio por trinomio, con el medio cambiado de signo.",
        "default": (
            "Cuenta los términos: una suma de cubos tiene dos y se abre en binomio por "
            "trinomio. Un cubo de binomio tiene cuatro al desarrollarlo."
        ),
        "fb_g04_e1_cube": (
            "Ese es el error del nodo. (x+2)³ = x³ + 6x² + 12x + 8, que tiene cuatro "
            "términos. Con x = 1: la remesa arquea 9 y tu respuesta 27."
        ),
        "fb_g04_e1_conj": (
            "Esa es la diferencia de cuadrados, y además esto suma. (x+2)(x−2) estampa "
            "x² − 4, con exponente 2."
        ),
        "fb_g04_e1_sq": (
            "Casi: el trinomio lleva el término del medio con el signo CONTRARIO al del "
            "binomio. Binomio con más → medio con menos."
        ),
        "fb_g04_e5_bin": (
            "El binomio está bien: repite el signo de la remesa, y esta resta."
        ),
        "fb_g04_e5_last": (
            "El trinomio siempre acaba en más, porque es el cuadrado del segundo término."
        ),
        "fb_g04_e5_none": (
            "Sí lo hay: con el binomio restando, el medio del trinomio suma. Debería ser "
            "x² + 3x + 9."
        ),
        "fb_g04_e6_trap": (
            "El exponente cambia las cosas. Estampa (x+2)(x² − 2x + 4): todo lo de en medio "
            "se anula y quedan x³ y 8."
        ),
        "fb_g04_e6_even": (
            "Justo al revés: es el exponente el que decide. Con 2 la suma no se abre, con 3 sí."
        ),
        "fb_g04_e6_cube": (
            "Se abre, pero no así: (a+b)³ tiene cuatro términos al desarrollarlo. La suma de "
            "cubos da un binomio POR un trinomio."
        ),
    },
    "closing": (
        "Con esto tienes los cuatro moldes del almacén: sacar lo común, cotejar una huella, "
        "despiezar a mano y arquear toneles. Pero hasta ahora cada sala te decía qué molde "
        "usar. En la expedición llegan las remesas mezcladas, sin etiqueta, y lo único que "
        "hay que decidir es por dónde empezar."
    ),
    "validation_status": "F5_G04_11bloques",
}
