"""G02 · El cotejo de huellas — la suma de cuadrados no salió de ningún troquel.

Segunda sala del Almacén de la caravana (Casa de la Sabiduría, Bagdad).
Guía: Salim. Vocabulario propio: huella, calco, cotejo, catálogo, inventario,
marca. Nada de fardos ni básculas (G01), despiece ni muescas (G03), toneles ni
duelas (G04).

Error focal: creer que a² + b² se factoriza como (a+b)(a−b), o en general que
toda expresión con dos cuadrados sale de un troquel. La diferencia sí; la suma
no sale de ninguno.

Ítems de práctica derivados de Hipertexto U5 p108 (A2) y p116 (E1a, E1c, A2b,
A2c, A2d, E2), más tres tipos que el libro NO trae: parámetro, control sin
calcular y decisión de método.
"""

NODE_ID = "ALG-N3-G02-CUADRADOS"
CONCEPT_SLUG = "diferencia_de_cuadrados_y_tcp"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "diferencia_de_cuadrados_y_tcp",
    "misconception": "suma_de_cuadrados_es_factorizable",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El cotejo de huellas · Diferencia de cuadrados y trinomio cuadrado perfecto",
    "house": "El cotejo de huellas",
    "guide": "Salim",
    "finish_label": "Pasar a la mesa de despiece",
    "title": "Hay una huella que no está en el catálogo, y no es que falte",
    "intro": (
        "En el pesaje abrías fardos por lo que compartían sus bultos. Aquí llegan fardos que "
        "no comparten nada y aun así se abren: llevan la marca del troquel que los estampó. "
        "El oficio es cotejar la marca contra el catálogo. Y lo difícil no es reconocer las "
        "que están: es aceptar que una de las que buscas no existe."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el catálogo. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es la raíz cuadrada de 49?",
                "answer": "7",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $(x+3)(x-3)$?",
                "options": [
                    {"id": "dif", "text": r"$x^{2}-9$", "latex": r"x^{2}-9"},
                    {"id": "sum", "text": r"$x^{2}+9$", "latex": r"x^{2}+9"},
                    {"id": "mid", "text": r"$x^{2}-6x+9$", "latex": r"x^{2}-6x+9"},
                ],
                "expected": "dif",
                "misconception_by_option": {
                    "sum": "conjugado_da_suma_de_cuadrados",
                    "mid": "confunde_conjugados_con_cuadrado_de_binomio",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"En $x^{2}+6x+9$, ¿cuánto vale el doble producto de las raíces de los extremos?",
                "answer": "6",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/07-alg-n3-caravana/g02-cuadrados-katia.png",
        "eyebrow": "KatIA · En el cotejo de huellas",
        "title": "La marca que el mozo se inventó",
        "body": (
            "En esta sala hay un catálogo de calcos: una hoja por cada troquel de la casa, "
            "con la huella que deja. Un fardo sin factor común se coteja contra el catálogo, "
            "y si su marca aparece, se sabe con qué troquel se cerró.\n\n"
            "Salim abre el catálogo por la mitad:\n\n"
            "«Llegó un fardo marcado $x^{2}+9$. El mozo vio dos cuadrados y buscó la hoja del "
            "cuño de la cenefa. Anotó que venía de $(x+3)(x-3)$ y lo mandó a desatar.»\n\n"
            "«Ese cuño deja la marca $x^{2}-9$, con un menos. El fardo llegó cerrado y se fue "
            "roto: no venía de ningún troquel de esta casa.»"
        ),
        "question": (
            "Si el cuño de la cenefa deja siempre una resta, ¿de qué troquel puede salir una "
            "suma de dos cuadrados?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "ninguno", "text": "De ninguno: esa huella no está en el catálogo"},
                {"id": "mismo", "text": "Del mismo, cambiando el signo al final"},
                {"id": "otro", "text": "De otro troquel que todavía no hemos visto"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decidir, mirando solo la marca, si "
                "un fardo se abre o si hay que devolverlo cerrado."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos huellas en el catálogo, y un hueco",
        "body": (
            "Factorizar con troquel es leer al revés lo que aprendiste en la sala anterior. "
            "Cada estampa deja una marca reconocible."
        ),
        "cases": [
            {
                "label": "Dos términos: la resta sí, la suma no",
                "context": r"$a^{2}-b^{2}$ frente a $a^{2}+b^{2}$",
                "fraction": r"a^{2}-b^{2}=(a+b)(a-b)",
                "division": r"a^{2}+b^{2}\ \text{no se abre}",
                "note": (
                    "Compruébalo: cualquier par de factores que pruebes deja un término del "
                    "medio o cambia el signo. La suma de dos cuadrados no sale de multiplicar "
                    "dos binomios."
                ),
            },
            {
                "label": "Tres términos: hay que verificar el del medio",
                "context": r"$a^{2}\pm 2ab+b^{2}$",
                "fraction": r"x^{2}+6x+9=(x+3)^{2}",
                "division": r"2\cdot x\cdot 3=6x\ \checkmark",
                "note": (
                    "No basta con que los extremos sean cuadrados: el del medio tiene que ser "
                    "exactamente el doble producto de sus raíces."
                ),
            },
        ],
        "resolution": (
            "Dos huellas y un hueco. Con DOS términos: si restan y ambos son cuadrados, sale "
            "el cuño de la cenefa; si suman, no hay troquel. Con TRES términos: si los "
            "extremos son cuadrados Y el del medio es su doble producto, sale la matriz "
            "cuadrada; si el del medio no cuadra, tampoco hay troquel."
        ),
    },
    "definition_title": "Diferencia de cuadrados y trinomio cuadrado perfecto",
    "definition_katex": (r"a^{2}-b^{2} = (a+b)(a-b) \qquad a^{2}\pm 2ab+b^{2} = (a\pm b)^{2}"),
    "definition": (
        "DIFERENCIA DE CUADRADOS: dos términos, ambos cuadrados exactos, restando. Se abre "
        "como suma por diferencia de sus raíces. La SUMA de cuadrados no se factoriza.\n\n"
        "TRINOMIO CUADRADO PERFECTO: tres términos; los extremos son cuadrados exactos y "
        "positivos, y el del medio es el doble producto de sus raíces. Se abre como el "
        "cuadrado de un binomio, con el signo del término del medio."
    ),
    "definition_symbols": [
        {
            "symbol": r"a^{2}-b^{2}=(a+b)(a-b)",
            "reads": "a cuadrado menos b cuadrado, igual a a más b por a menos b",
            "means": "la huella del cuño de la cenefa, leída al revés",
        },
        {
            "symbol": r"a^{2}+b^{2}",
            "reads": "a cuadrado más b cuadrado",
            "means": "el hueco del catálogo: no sale de ningún troquel",
        },
        {
            "symbol": r"2ab",
            "reads": "dos a b",
            "means": "el doble producto, la condición que hay que verificar",
        },
        {
            "symbol": r"a^{2}-2ab+b^{2}=(a-b)^{2}",
            "reads": "a cuadrado menos dos a b más b cuadrado",
            "means": "los extremos siempre suman; el signo del medio va dentro del paréntesis",
        },
        {
            "symbol": r"x^{4}-16",
            "reads": "equis a la cuarta menos dieciséis",
            "means": "se abre, y uno de los trozos se vuelve a abrir",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Un fardo de dos marcas",
            "title": "Restan y los dos son cuadrados",
            "statement": "Salim coteja un fardo marcado $4x^{2}-25$. ¿Se abre?",
            "latex": r"4x^{2}-25",
            "image_slot": False,
            "steps": [
                "Dos términos y restan: candidato a diferencia de cuadrados.",
                "¿4x² es cuadrado exacto? Sí: (2x)². ¿25? Sí: 5².",
                "Las dos raíces son 2x y 5.",
                "Se abre como suma por diferencia: (2x + 5)(2x − 5).",
                "Compruebo estampando: (2x)² − 5² = 4x² − 25 ✓.",
            ],
            "solution": r"$4x^{2}-25=(2x+5)(2x-5)$",
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "¿Por qué hay que comprobar que los DOS términos son cuadrados exactos, "
                    "y no basta con que uno lo sea?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Tres marcas y una verificación",
            "title": "El del medio decide",
            "statement": (
                "Otro fardo: $4x^{2}+12xy+9y^{2}$. Los extremos prometen; falta comprobar el "
                "del medio."
            ),
            "latex": r"4x^{2}+12xy+9y^{2}",
            "image_slot": False,
            "steps": [
                "Extremos: 4x² = (2x)² y 9y² = (3y)². Los dos son cuadrados exactos y positivos.",
                "Raíces: 2x y 3y.",
                "Doble producto: 2 · 2x · 3y = 12xy.",
                "El trinomio tiene 12xy: coincide. Es cuadrado perfecto.",
                "El signo del medio es +, así que queda (2x + 3y)².",
            ],
            "solution": r"$4x^{2}+12xy+9y^{2}=(2x+3y)^{2}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El mozo que abrió una suma de cuadrados",
            "statement": (
                "Vuelve el fardo de la apertura. El mozo coteja $x^{2}+9$ contra la hoja del "
                "cuño y anota:"
            ),
            "latex": r"x^{2}+9",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"x^{2}+9=(x+3)(x-3)",
            "error_note": (
                "Vio dos cuadrados y dio por hecho que había troquel. Pero esa hoja del "
                "catálogo deja una RESTA."
            ),
            "correct_version": {
                "wrong_latex": r"x^{2}+9=(x+3)(x-3)",
                "right_latex": r"x^{2}+9\ \text{no se factoriza}",
                "rows": [
                    {
                        "wrong": "Dos cuadrados, luego hay troquel",
                        "right": "Dos cuadrados Y restando. La suma no tiene hoja en el catálogo",
                    },
                    {
                        "wrong": "El signo del medio da igual",
                        "right": "El signo es la marca: (x+3)(x−3) estampa x²−9, no x²+9",
                    },
                ],
            },
            "explain_prompt": (
                "Estampa $(x+3)(x-3)$ y comprueba qué marca deja. Después prueba con $x=1$ en "
                "las dos expresiones y di cuánto se separan."
            ),
            "steps": [
                "(x + 3)(x − 3) = x² − 9. Deja un menos, no un más.",
                "Con x = 1: x² + 9 vale 10, y (x + 3)(x − 3) vale 4 · (−2) = −8.",
                "No solo son distintas: una es positiva y la otra negativa.",
                "Regla para no volver a caer: dos términos que SUMAN y son cuadrados → el fardo se devuelve cerrado.",
            ],
            "solution": (
                "x² + 9 no se factoriza. La diferencia de cuadrados se abre; la suma, no."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El cotejo va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Factoriza $9x^{2}-49$.",
                "given_steps": [r"\sqrt{9x^{2}}=3x"],
                "blanks": [{"id": "P1-b1", "label": r"\sqrt{49}=", "answer": "7"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"¿Es $x^{2}+10x+25$ cuadrado perfecto?",
                "given_steps": [r"\sqrt{x^{2}}=x,\quad \sqrt{25}=5"],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"2\cdot x\cdot 5\ \text{, coeficiente}=",
                        "answer": "10",
                    },
                    {
                        "id": "P2-b2",
                        "label": r"\text{términos del binomio resultante}=",
                        "answer": "2",
                    },
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $m^{2}-8m+25$. Comprueba las tres condiciones y "
                    "di cuál falla."
                ),
                "given_steps": [],
                "blanks": [
                    {
                        "id": "P3-b1",
                        "label": r"\text{doble producto que debería tener}=",
                        "answer": "10",
                    }
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de decidir si un fardo se abre",
        "intro": r"$4x^{2}-4x+9$. Una tantea; la otra verifica.",
        "methods": [
            {
                "label": "Método 1 · Probar binomios",
                "steps": [
                    r"(2x-3)^{2}=4x^{2}-12x+9",
                    r"(2x+3)^{2}=4x^{2}+12x+9",
                    r"\text{ninguno da }-4x",
                ],
                "note": "Funciona, pero hay que estampar cada candidato para descartarlo.",
            },
            {
                "label": "Método 2 · Verificar el doble producto",
                "steps": [
                    r"\sqrt{4x^{2}}=2x,\quad \sqrt{9}=3",
                    r"2\cdot 2x\cdot 3=12x",
                    r"\text{el trinomio tiene }4x\neq 12x",
                ],
                "note": "Tres cuentas cortas y se decide sin estampar nada.",
            },
        ],
        "question": "¿Cuál de los dos sirve también cuando el fardo NO se abre?",
        "insight": (
            "El segundo. Probando binomios uno puede descartar dos candidatos y quedarse con "
            "la duda de si faltaba probar otro. Verificando el doble producto se obtiene una "
            "respuesta cerrada: o el término del medio es exactamente 2ab, o no es cuadrado "
            "perfecto, y no hay tercera opción. Por eso este método también contesta las "
            "preguntas que empiezan por «¿se puede…?»."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál es la factorización de $4x^{2}-25$?",
            "options": [
                {"id": "ok", "text": r"$(2x+5)(2x-5)$", "latex": r"(2x+5)(2x-5)"},
                {"id": "sq", "text": r"$(2x-5)^{2}$", "latex": r"(2x-5)^{2}"},
                {"id": "half", "text": r"$(4x+5)(x-5)$", "latex": r"(4x+5)(x-5)"},
                {"id": "none", "text": "No se puede factorizar"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "sq": "fb_g02_e1_sq",
                "half": "fb_g02_e1_half",
                "none": "fb_g02_e1_none",
            },
            "misconception_by_option": {
                "sq": "confunde_diferencia_con_cuadrado_perfecto",
                "half": "no_saca_la_raiz_del_coeficiente",
                "none": "suma_de_cuadrados_es_factorizable",
            },
            "hints": {
                "n1": "Dos términos que restan: busca las raíces de cada uno.",
                "n2": "√(4x²) = 2x y √25 = 5.",
                "n3": "Suma por diferencia de esas dos raíces.",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Es $5a^{2}+30ab+9b^{2}$ un trinomio cuadrado perfecto?",
            "options": [
                {
                    "id": "no_first",
                    "text": r"No: 5 no es cuadrado exacto, así que el primer término no tiene raíz",
                },
                {"id": "yes", "text": r"Sí: $(5a+3b)^{2}$"},
                {"id": "no_mid", "text": "No: los extremos están bien, falla el del medio"},
                {"id": "no_sign", "text": "No: le falta un signo menos"},
            ],
            "expected": "no_first",
            "feedback_by_option": {
                "no_first": "correct",
                "yes": "fb_g02_e2_yes",
                "no_mid": "fb_g02_e2_mid",
                "no_sign": "fb_g02_e2_sign",
            },
            "misconception_by_option": {
                "yes": "no_saca_la_raiz_del_coeficiente",
                "no_mid": "no_verifica_los_extremos_antes_del_medio",
                "no_sign": "cree_que_el_signo_decide_el_tcp",
            },
            "hints": {
                "n1": "La primera condición es que los extremos sean cuadrados exactos.",
                "n2": "¿Qué número al cuadrado da 5?",
                "n3": "Ninguno entero: ni hace falta mirar el término del medio.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"¿Para qué valor POSITIVO de $k$ es $x^{2}+kx+36$ un trinomio cuadrado "
                "perfecto?"
            ),
            "expr": r"2\cdot x\cdot 6=12x",
            "answer": "12",
            "hints": {
                "n1": "Los extremos son x² y 36; sus raíces son x y 6.",
                "n2": "El del medio tiene que ser el doble producto de esas raíces.",
                "n3": "2 · 1 · 6.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"En $m^{2}-8m+25$ los extremos son cuadrados. ¿Cuánto tendría que valer el "
                "coeficiente del medio, sin signo, para que fuera cuadrado perfecto?"
            ),
            "expr": r"2\cdot m\cdot 5=10m",
            "answer": "10",
            "hints": {
                "n1": "Las raíces de los extremos son m y 5.",
                "n2": "El doble producto es 2 · m · 5.",
                "n3": "Falla por poco: tiene 8 y necesitaría 10.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un mozo anota $x^{4}-16=(x^{2}+4)(x^{2}-4)$ y cierra el albarán. ¿Está "
                "terminado?"
            ),
            "options": [
                {
                    "id": "no",
                    "text": r"No: $x^{2}-4$ es otra diferencia de cuadrados y se vuelve a abrir",
                },
                {"id": "yes", "text": "Sí: ya está en dos factores"},
                {"id": "wrong", "text": r"No: el primer factor $x^{2}+4$ también se abre"},
                {
                    "id": "err",
                    "text": r"No: la factorización está mal, debería ser $(x^{2}+4)^{2}$",
                },
            ],
            "expected": "no",
            "feedback_by_option": {
                "no": "correct",
                "yes": "fb_g02_e5_yes",
                "wrong": "fb_g02_e5_wrong",
                "err": "fb_g02_e5_err",
            },
            "misconception_by_option": {
                "yes": "factor_comun_incompleto",
                "wrong": "suma_de_cuadrados_es_factorizable",
                "err": "confunde_diferencia_con_cuadrado_perfecto",
            },
            "hints": {
                "n1": "La factorización es correcta. La pregunta es si está terminada.",
                "n2": "Mira dentro de cada factor, como en el pesaje de entrada.",
                "n3": "x² − 4 son dos cuadrados que restan.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Si una expresión tiene dos términos y los dos son "
                "cuadrados exactos, se puede factorizar.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: solo si RESTAN. Si suman, no hay troquel"},
                {"id": "true", "text": "Verdadera: dos cuadrados siempre dan suma por diferencia"},
                {
                    "id": "true_pos",
                    "text": "Verdadera, y el signo solo cambia el orden de los factores",
                },
                {
                    "id": "false_never",
                    "text": "Falsa: con dos términos nunca se puede factorizar",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_g02_e6_trap",
                "true_pos": "fb_g02_e6_order",
                "false_never": "fb_g02_e6_never",
            },
            "misconception_by_option": {
                "true": "suma_de_cuadrados_es_factorizable",
                "true_pos": "suma_de_cuadrados_es_factorizable",
                "false_never": "cree_que_dos_terminos_nunca_se_factorizan",
            },
            "hints": {
                "n1": "Prueba a estampar (x + 3)(x − 3) y mira qué signo deja.",
                "n2": "Deja x² − 9.",
                "n3": "Con x = 1, x² + 9 vale 10 y (x+3)(x−3) vale −8.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Salim reparte cuatro fardos SIN abrirlos. ¿Cuáles se pueden abrir con las "
                "huellas de esta sala? Marca todas las que apliquen."
            ),
            "options": [
                {"id": "dif", "text": r"$9x^{2}-49$"},
                {"id": "tcp", "text": r"$x^{2}+10x+25$"},
                {"id": "sum", "text": r"$x^{2}+49$"},
                {"id": "nomid", "text": r"$4x^{2}-4x+9$"},
            ],
            "expected": ["dif", "tcp"],
            "valid_options": ["dif", "tcp", "sum", "nomid"],
            "trap_options": ["sum", "nomid"],
            "feedback_by_option": {"dif": "correct", "tcp": "correct"},
            "misconception_by_option": {
                "sum": "suma_de_cuadrados_es_factorizable",
                "nomid": "no_verifica_el_doble_producto",
            },
            "hints": {
                "n1": "Con dos términos: cuadrados exactos Y restando.",
                "n2": "Con tres: extremos cuadrados Y el medio igual al doble producto.",
                "n3": "En 4x² − 4x + 9 el doble producto sería 12x, no 4x. Son dos de los cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Está la huella en el catálogo?",
        "title": "Dos hojas, un hueco y un fardo que se abre dos veces",
        "intro": (
            "El cotejo se decide mirando cuántos términos hay, si son cuadrados exactos y "
            "qué signo llevan. Esta es la hoja de ruta."
        ),
        "rows": [
            {
                "name": "Dos términos, restando",
                "symbol": r"a^{2}-b^{2}",
                "latex": r"(a+b)(a-b)",
                "closed": "yes",
                "note": "La huella del cuño de la cenefa. Se abre siempre.",
            },
            {
                "name": "Dos términos, sumando",
                "symbol": r"a^{2}+b^{2}",
                "latex": r"\text{no se factoriza}",
                "closed": "no",
                "note": (
                    "El hueco del catálogo. No es que no lo hayamos visto todavía: no sale "
                    "de multiplicar dos binomios."
                ),
            },
            {
                "name": "Tres términos, doble producto correcto",
                "symbol": r"a^{2}+2ab+b^{2}",
                "latex": r"(a+b)^{2}",
                "closed": "yes",
                "note": "La huella de la matriz cuadrada. Los extremos siempre suman.",
            },
            {
                "name": "Tres términos, el medio restando",
                "symbol": r"a^{2}-2ab+b^{2}",
                "latex": r"(a-b)^{2}",
                "closed": "yes",
                "note": "El signo del medio es el que entra en el binomio; los extremos no cambian.",
            },
            {
                "name": "El extremo no es cuadrado exacto",
                "symbol": r"5a^{2}+30ab+9b^{2}",
                "latex": r"\sqrt{5}\notin\mathbb{Z}",
                "closed": "no",
                "note": (
                    "Falla en la primera condición: ni hace falta mirar el término del medio."
                ),
            },
            {
                "name": "Se abre, y vuelve a abrirse",
                "symbol": r"x^{4}-16",
                "latex": r"(x^{2}+4)(x^{2}-4)=(x^{2}+4)(x+2)(x-2)",
                "closed": "partial",
                "note": (
                    "Es diferencia de cuadrados, sí, pero uno de los trozos también lo es. "
                    "Vale la regla del pesaje: mira dentro. El otro trozo, x² + 4, se queda "
                    "cerrado."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **la diferencia de cuadrados se abre; la suma, no.** Y "
            "con tres términos, los extremos son la entrada pero el que decide es el del "
            "medio."
        ),
    },
    "abstraction_question": {
        "prompt": (
            "Los tres tienen dos cuadrados exactos. ¿Qué es lo único que decide si se abren?"
        ),
        "thumbnails": [
            r"x^{2}-9",
            r"x^{2}+9",
            r"x^{2}+6x+9",
        ],
        "options": [
            {
                "id": "sign",
                "text": (
                    "El signo y el número de términos: restando se abre, sumando no, y con "
                    "tres decide el doble producto"
                ),
                "correct": True,
            },
            {
                "id": "size",
                "text": "El tamaño de los números: 9 es cuadrado y por eso los tres se abren",
                "correct": False,
            },
            {
                "id": "letter",
                "text": "Que aparezca la letra en los dos términos",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Salim recibe un fardo marcado $x^{2}+14x+c$. Si es un trinomio cuadrado "
            "perfecto, ¿cuánto vale $c$?"
        ),
        "polya": [
            "Entender: el del medio es 14x y falta el último término.",
            "Planear: el del medio es 2ab, con a = x. Despejo b y elevo al cuadrado.",
            "Ejecutar: 2 · x · b = 14x → b = 7, así que c = 7² = 49.",
            "Comprobar: x² + 14x + 49 = (x + 7)², y 2 · x · 7 = 14x ✓.",
        ],
        "prompt": "¿Cuánto vale c?",
        "answer": "49",
        "hints": {
            "n1": "El término del medio es el doble producto de las dos raíces.",
            "n2": "Una raíz es x, así que 2 · x · b = 14x.",
            "n3": "b = 7, y c es su cuadrado.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que conoces el catálogo.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya distingues el fardo que se abre del que hay que devolver cerrado.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la suma de cuadrados "
            "antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuál es la raíz cuadrada de 64?",
                "answer": "8",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuál de estas NO se puede factorizar?",
                "options": [
                    {"id": "sum", "text": r"$x^{2}+16$", "latex": r"x^{2}+16"},
                    {"id": "dif", "text": r"$x^{2}-16$", "latex": r"x^{2}-16"},
                    {"id": "tcp", "text": r"$x^{2}+8x+16$", "latex": r"x^{2}+8x+16"},
                ],
                "expected": "sum",
                "misconception_by_option": {
                    "dif": "suma_de_cuadrados_es_factorizable",
                    "tcp": "no_verifica_el_doble_producto",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": r"En $x^{2}+12x+36$, ¿cuánto vale el doble producto de las raíces de los extremos?",
                "answer": "12",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de pasar a la mesa de despiece.",
            "consolidacion": "Resuelto con ayuda: el cotejo ya está, falta que salga solo.",
            "sin_ayuda": "Catálogo dominado. Reconoces las dos huellas y también el hueco.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. La huella coincide con su hoja del catálogo.",
        "default": (
            "Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo "
            "llevan. Con eso se decide sin estampar nada."
        ),
        "fb_g02_e1_sq": (
            "Ese es el cuadrado de un binomio, y deja tres términos: 4x² − 20x + 25. Aquí "
            "solo hay dos."
        ),
        "fb_g02_e1_half": (
            "Las raíces tienen que salir de cada término completo: √(4x²) = 2x, no 4x."
        ),
        "fb_g02_e1_none": (
            "Sí se puede: son dos cuadrados exactos que RESTAN, que es justo el caso que se "
            "abre."
        ),
        "fb_g02_e2_yes": (
            "Para que fuera (5a + 3b)² el primer término tendría que ser 25a², no 5a². El 5 "
            "no tiene raíz cuadrada exacta."
        ),
        "fb_g02_e2_mid": (
            "Los extremos NO están bien: 5 no es cuadrado exacto. Se descarta antes de llegar "
            "al término del medio."
        ),
        "fb_g02_e2_sign": (
            "El signo no es el problema: en un cuadrado perfecto los extremos siempre suman. "
            "Falla la raíz del primero."
        ),
        "fb_g02_e5_yes": (
            "La igualdad es correcta, pero no está terminada — es la misma lección del pesaje "
            "de entrada: mira dentro de cada factor."
        ),
        "fb_g02_e5_wrong": (
            "x² + 4 es una SUMA de cuadrados: ese se queda cerrado. El que se vuelve a abrir "
            "es x² − 4."
        ),
        "fb_g02_e5_err": (
            "La factorización está bien: (x²+4)(x²−4) estampa x⁴ − 16. Lo que falta es seguir "
            "abriendo."
        ),
        "fb_g02_e6_trap": (
            "Solo si restan. (x + 3)(x − 3) deja x² − 9; no hay ningún par de binomios que "
            "deje x² + 9."
        ),
        "fb_g02_e6_order": (
            "El orden de los factores no cambia el signo del resultado: (x+3)(x−3) y "
            "(x−3)(x+3) dan lo mismo, x² − 9."
        ),
        "fb_g02_e6_never": (
            "Te pasaste al otro lado: con dos términos sí se puede, siempre que sean "
            "cuadrados exactos y resten."
        ),
    },
    "closing": (
        "Ya sabes cotejar una huella contra el catálogo, y sabes que hay un hueco: la suma de "
        "cuadrados no salió de ningún troquel. Pero la mayoría de los fardos que llegan traen "
        "tres marcas que no cuadran con la matriz cuadrada. Para esos hay una mesa donde se "
        "despiezan a mano, buscando dos números que cumplan dos condiciones a la vez."
    ),
    "validation_status": "F5_G02_11bloques",
}
