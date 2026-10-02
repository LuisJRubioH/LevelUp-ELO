"""G03 · La mesa de despiece — dos condiciones a la vez, no una.

Tercera sala del Almacén de la caravana (Casa de la Sabiduría, Bagdad).
Guía: Salim. Vocabulario propio: despiece, listón, encaje, tanteo, muesca,
banco. Nada de fardos ni básculas (G01), huellas ni calcos (G02), toneles ni
duelas (G04).

Error focal: quedarse con la primera pareja de números que cumple UNA de las dos
condiciones —normalmente el producto— sin comprobar la otra. Encajar no es
acertar el producto: es acertar el producto Y la suma.

Ítems derivados de Hipertexto U5 p120 (A1, A2a, A2b, E3) y p122, más un ítem de
parámetro y uno de control sin calcular, que el libro no trae.
"""

NODE_ID = "ALG-N3-G03-TRINOMIO"
CONCEPT_SLUG = "trinomio_general"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "trinomio_general",
    "misconception": "pares_sin_verificar",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La mesa de despiece · Trinomio general",
    "house": "La mesa de despiece",
    "guide": "Salim",
    "finish_label": "Pasar a la bodega de los toneles",
    "title": "Acertar el producto no basta: también hay que acertar la suma",
    "intro": (
        "En el cotejo de huellas bastaba reconocer una marca. Aquí llegan fardos de tres "
        "bultos que no traen ninguna: hay que despiezarlos a mano, buscando dos listones que "
        "encajen. Y encajar significa cumplir dos medidas a la vez, no una."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de sentarte al banco. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Qué dos números suman 5 y multiplican 6? Escribe el mayor.",
                "answer": "3",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $(x+2)(x+3)$?",
                "options": [
                    {"id": "ok", "text": r"$x^{2}+5x+6$", "latex": r"x^{2}+5x+6"},
                    {"id": "noMid", "text": r"$x^{2}+6$", "latex": r"x^{2}+6"},
                    {"id": "swap", "text": r"$x^{2}+6x+5$", "latex": r"x^{2}+6x+5"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "noMid": "termino_comun_falta_suma",
                    "swap": "intercambia_suma_y_producto",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es (−4) × (−5)?",
                "answer": "20",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/07-alg-n3-caravana/g03-trinomio-katia.png",
        "eyebrow": "KatIA · En la mesa de despiece",
        "title": "Los dos listones que no encajaban",
        "body": (
            "En el fondo del almacén hay un banco largo con muescas. Los fardos de tres "
            "bultos que no traen marca se despiezan aquí: se buscan dos listones cuyo largo "
            "y cuya suma encajen en las muescas del banco.\n\n"
            "Salim señala un despiece a medio hacer:\n\n"
            "«El fardo pedía dos listones que multiplicaran 6 y sumaran 5. El mozo probó 1 y "
            "6: multiplican 6, perfecto. Los cortó y los llevó al banco.»\n\n"
            "«Uno y seis suman siete, no cinco. Los listones no entraron en la muesca, y ya "
            "estaban cortados.»"
        ),
        "question": (
            "Si 1 y 6 multiplican exactamente lo que pedía el fardo, ¿por qué no sirven?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "dos", "text": "Porque hay dos condiciones y solo cumplen una"},
                {"id": "orden", "text": "Porque están en el orden equivocado"},
                {"id": "signo", "text": "Porque les falta un signo menos"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a tener una forma de probar parejas sin "
                "cortar nada hasta estar seguro."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El producto propone, la suma dispone",
        "body": (
            "Un trinomio $x^{2}+bx+c$ viene de la bandeja de parejas: $(x+p)(x+q)$. Al "
            "estampar, $p$ y $q$ dejaban su suma en el medio y su producto al final. Aquí se "
            "lee al revés."
        ),
        "cases": [
            {
                "label": "La lista de candidatos",
                "context": r"$x^{2}+5x+6$ — parejas que multiplican 6",
                "fraction": r"1\cdot 6,\quad 2\cdot 3",
                "division": r"\text{dos candidatas}",
                "note": (
                    "El producto es el que da la lista, porque los divisores de un número "
                    "son pocos. Por eso se empieza por ahí."
                ),
            },
            {
                "label": "La suma decide",
                "context": r"¿Cuál de las dos suma 5?",
                "fraction": r"1+6=7\ \text{✗}\qquad 2+3=5\ \text{✓}",
                "division": r"(x+2)(x+3)",
                "note": (
                    "El producto reduce a dos o tres candidatas; la suma elige una. Saltarse "
                    "el segundo paso es cortar los listones a ciegas."
                ),
            },
        ],
        "resolution": (
            "Para $x^{2}+bx+c$: se listan las parejas de enteros que multiplican $c$ y se "
            "queda la que suma $b$. Si el coeficiente de $x^{2}$ es mayor que 1, primero se "
            "multiplica ese coeficiente por el término independiente y se busca la pareja "
            "para ese producto nuevo."
        ),
    },
    "definition_title": "Trinomio general",
    "definition_katex": (
        r"x^{2}+bx+c = (x+p)(x+q)\ \text{ con } p+q=b\ \text{ y } pq=c"
    ),
    "definition": (
        "Factorizar un trinomio con coeficiente principal 1 es buscar dos números que "
        "cumplan DOS condiciones: que sumen el coeficiente del medio y que multipliquen el "
        "término independiente. Los signos salen solos de esas dos cuentas.\n\n"
        "Si el coeficiente principal es mayor que 1, se busca la pareja para el producto "
        "$a\\cdot c$, se parte el término del medio con esos dos números y se agrupa."
    ),
    "definition_symbols": [
        {
            "symbol": r"p+q=b",
            "reads": "p más q igual a b",
            "means": "la condición de la suma — la que se olvida",
        },
        {
            "symbol": r"pq=c",
            "reads": "p por q igual a c",
            "means": "la condición del producto — la que da la lista de candidatos",
        },
        {
            "symbol": r"x^{2}-9x+20=(x-4)(x-5)",
            "reads": "equis cuadrado menos nueve equis más veinte",
            "means": "medio negativo y final positivo: los dos números son negativos",
        },
        {
            "symbol": r"x^{2}+x-6=(x+3)(x-2)",
            "reads": "equis cuadrado más equis menos seis",
            "means": "final negativo: los dos números tienen signos distintos",
        },
        {
            "symbol": r"a\cdot c",
            "reads": "a por c",
            "means": "cuando el coeficiente principal no es 1, la lista sale de este producto",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Un fardo de tres bultos",
            "title": "Listar y después elegir",
            "statement": "Salim despieza un fardo marcado $x^{2}+4x+3$.",
            "latex": r"x^{2}+4x+3",
            "image_slot": False,
            "steps": [
                "Busco dos números que multipliquen 3: solo hay 1 · 3 (y −1 · −3).",
                "¿Cuál de esas suma 4? 1 + 3 = 4 ✓.",
                "Los dos son positivos, así que los dos paréntesis suman.",
                "Queda (x + 1)(x + 3).",
                "Compruebo estampando: x² + 3x + x + 3 = x² + 4x + 3 ✓.",
            ],
            "solution": r"$x^{2}+4x+3=(x+1)(x+3)$",
            "self_explanation": {
                "step_index": 0,
                "prompt": (
                    "¿Por qué conviene empezar por el producto y no por la suma, si las dos "
                    "condiciones hacen falta?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando el medio resta",
            "title": "Los signos salen de las dos cuentas",
            "statement": "Otro fardo: $x^{2}-9x+20$. El medio resta y el final suma.",
            "latex": r"x^{2}-9x+20",
            "image_slot": False,
            "steps": [
                "Producto 20, positivo: los dos números tienen el MISMO signo.",
                "Suma −9, negativa: entonces los dos son negativos.",
                "Parejas negativas que multiplican 20: (−1)(−20), (−2)(−10), (−4)(−5).",
                "¿Cuál suma −9? −4 − 5 = −9 ✓.",
                "Queda (x − 4)(x − 5).",
            ],
            "solution": r"$x^{2}-9x+20=(x-4)(x-5)$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El mozo que cortó los listones antes de sumar",
            "statement": (
                "Vuelve el fardo de la apertura, ahora escrito: $x^{2}+5x+6$. El mozo anota:"
            ),
            "latex": r"x^{2}+5x+6",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"x^{2}+5x+6=(x+1)(x+6)",
            "error_note": (
                "Comprobó el producto y paró ahí. 1 · 6 = 6, correcto — pero 1 + 6 = 7, y el "
                "fardo pedía 5."
            ),
            "correct_version": {
                "wrong_latex": r"(x+1)(x+6)=x^{2}+7x+6",
                "right_latex": r"(x+2)(x+3)=x^{2}+5x+6",
                "rows": [
                    {
                        "wrong": "Basta con que multipliquen el último término",
                        "right": "Tienen que multiplicar el último Y sumar el del medio",
                    },
                    {
                        "wrong": "1 y 6 multiplican 6, así que sirven",
                        "right": "2 y 3 multiplican 6 y además suman 5",
                    },
                ],
            },
            "explain_prompt": (
                "Estampa la anotación del mozo y di en qué término se separa del fardo "
                "original."
            ),
            "steps": [
                "(x + 1)(x + 6) = x² + 7x + 6.",
                "El primero y el último coinciden; el del medio no: 7x en vez de 5x.",
                "Por eso la condición de la suma no es opcional: es la que fija el término del medio.",
                "Regla para no volver a caer: lista con el producto, ELIGE con la suma.",
            ],
            "solution": (
                "x² + 5x + 6 = (x + 2)(x + 3). Dos condiciones, y hay que comprobar las dos."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El despiece va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Factoriza $x^{2}+8x+15$.",
                "given_steps": [r"\text{parejas que multiplican }15:\ 1\cdot 15,\ 3\cdot 5"],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{la que suma }8\text{: el mayor es}", "answer": "5"}
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Factoriza $x^{2}-6x+8$.",
                "given_steps": [r"\text{producto }8>0\ \text{y suma }-6<0\Rightarrow\ \text{ambos negativos}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"(-2)+(-4)=", "answer": "-6"},
                    {"id": "P2-b2", "label": r"(-2)\cdot(-4)=", "answer": "8"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $2x^{2}+7x+3$. El coeficiente principal no es 1 "
                    "— di primero sobre qué número hay que buscar la pareja."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"a\cdot c=2\cdot 3=", "answer": "6"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de buscar la pareja",
        "intro": r"$x^{2}+5x+6$. Una arranca por la suma; la otra por el producto.",
        "methods": [
            {
                "label": "Método 1 · Empezar por la suma",
                "steps": [
                    r"\text{parejas que suman }5:",
                    r"1+4,\ 2+3,\ 0+5,\ (-1)+6,\ (-2)+7,\dots",
                    r"\text{lista infinita}",
                ],
                "note": "Hay infinitas parejas que suman 5. La búsqueda no se cierra.",
            },
            {
                "label": "Método 2 · Empezar por el producto",
                "steps": [
                    r"\text{parejas que multiplican }6:",
                    r"1\cdot 6,\ 2\cdot 3\ \text{(y sus negativas)}",
                    r"\text{dos candidatas, se prueba la suma}",
                ],
                "note": "Los divisores de 6 son pocos: la lista es corta y termina.",
            },
        ],
        "question": "¿Por qué conviene empezar por el producto si las dos condiciones pesan igual?",
        "insight": (
            "Porque solo una de las dos cierra la búsqueda. Sumar 5 lo hacen infinitas "
            "parejas de enteros; multiplicar 6 lo hacen cuatro. El producto no es más "
            "importante que la suma — es más ÚTIL para empezar, porque acota. La suma sigue "
            "siendo la que decide, y por eso saltársela es el error de esta sala."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál es la factorización de $x^{2}+5x+6$?",
            "options": [
                {"id": "ok", "text": r"$(x+2)(x+3)$", "latex": r"(x+2)(x+3)"},
                {"id": "prod", "text": r"$(x+1)(x+6)$", "latex": r"(x+1)(x+6)"},
                {"id": "sum", "text": r"$(x+2)(x+3)$ o $(x+1)(x+4)$, las dos valen"},
                {"id": "neg", "text": r"$(x-2)(x-3)$", "latex": r"(x-2)(x-3)"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "prod": "fb_g03_e1_prod",
                "sum": "fb_g03_e1_sum",
                "neg": "fb_g03_e1_neg",
            },
            "misconception_by_option": {
                "prod": "pares_sin_verificar",
                "sum": "pares_sin_verificar",
                "neg": "ignora_el_signo_de_la_suma",
            },
            "hints": {
                "n1": "Lista las parejas que multiplican 6.",
                "n2": "Son 1·6 y 2·3.",
                "n3": "¿Cuál de las dos suma 5?",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Dos números suman $-9$ y multiplican $20$. ¿Cuál es el menor de los dos?"
            ),
            "expr": r"-4\ \text{y}\ -5",
            "answer": "-5",
            "hints": {
                "n1": "Producto positivo y suma negativa: los dos son negativos.",
                "n2": "Parejas negativas que multiplican 20: −1·−20, −2·−10, −4·−5.",
                "n3": "La que suma −9.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Para factorizar $2x^{2}+7x+3$, ¿sobre qué número hay que buscar la pareja?"
            ),
            "expr": r"a\cdot c=2\cdot 3",
            "answer": "6",
            "hints": {
                "n1": "Con coeficiente principal distinto de 1 no se usa el término independiente solo.",
                "n2": "Se multiplica el coeficiente principal por el independiente.",
                "n3": "2 · 3.",
            },
        },
        {
            "id": "E4",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"¿Cuántos valores ENTEROS POSITIVOS puede tomar $b$ para que $x^{2}+bx+12$ "
                "se pueda factorizar con enteros?"
            ),
            "expr": r"1+12,\ 2+6,\ 3+4\Rightarrow b\in\{13,8,7\}",
            "answer": "3",
            "hints": {
                "n1": "Lista las parejas de enteros positivos que multiplican 12.",
                "n2": "Son 1·12, 2·6 y 3·4.",
                "n3": "Cada pareja da una suma distinta: 13, 8 y 7.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un mozo anota $x^{2}-5x+6=(x+2)(x+3)$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "sign", "text": r"Los signos: deberían ser $(x-2)(x-3)$"},
                {"id": "pair", "text": r"La pareja: deberían ser 1 y 6"},
                {"id": "first", "text": r"El primer término: debería ser $2x^{2}$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "sign",
            "feedback_by_option": {
                "sign": "correct",
                "pair": "fb_g03_e5_pair",
                "first": "fb_g03_e5_first",
                "none": "fb_g03_e5_none",
            },
            "misconception_by_option": {
                "pair": "pares_sin_verificar",
                "first": "confunde_coeficiente_principal",
                "none": "ignora_el_signo_de_la_suma",
            },
            "hints": {
                "n1": "El producto está bien: 2 · 3 = 6.",
                "n2": "Mira la suma: 2 + 3 = 5, pero el trinomio tiene −5x.",
                "n3": "Producto positivo y suma negativa: los dos números son negativos.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Si dos números multiplican el término independiente, "
                "ya sirven para factorizar el trinomio.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: además tienen que sumar el coeficiente del medio"},
                {"id": "true", "text": "Verdadera: el producto es la condición que manda"},
                {
                    "id": "true_pos",
                    "text": "Verdadera cuando los dos números son positivos",
                },
                {
                    "id": "false_prod",
                    "text": "Falsa: lo que tienen que cumplir es solo la suma",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_g03_e6_trap",
                "true_pos": "fb_g03_e6_pos",
                "false_prod": "fb_g03_e6_prod",
            },
            "misconception_by_option": {
                "true": "pares_sin_verificar",
                "true_pos": "pares_sin_verificar",
                "false_prod": "ignora_la_condicion_del_producto",
            },
            "hints": {
                "n1": "Prueba 1 y 6 en x² + 5x + 6.",
                "n2": "Multiplican 6, correcto.",
                "n3": "Pero estampan x² + 7x + 6, no x² + 5x + 6.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Sin despiezar ninguno: ¿cuáles de estos trinomios se pueden factorizar con "
                "números enteros? Marca todas las que apliquen."
            ),
            "options": [
                {"id": "ok1", "text": r"$x^{2}+7x+12$"},
                {"id": "ok2", "text": r"$x^{2}-x-6$"},
                {"id": "no1", "text": r"$x^{2}+x+1$"},
                {"id": "no2", "text": r"$x^{2}+2x+5$"},
            ],
            "expected": ["ok1", "ok2"],
            "valid_options": ["ok1", "ok2", "no1", "no2"],
            "trap_options": ["no1", "no2"],
            "feedback_by_option": {"ok1": "correct", "ok2": "correct"},
            "misconception_by_option": {
                "no1": "cree_que_todo_trinomio_se_factoriza",
                "no2": "cree_que_todo_trinomio_se_factoriza",
            },
            "hints": {
                "n1": "Para cada uno, lista las parejas que multiplican el último término.",
                "n2": "En x² + x + 1 la única pareja entera es 1 y 1, que suma 2, no 1.",
                "n3": "Hay trinomios que simplemente no se abren con enteros. Son dos de los cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Cumple las DOS condiciones?",
        "title": "Una pareja no vale por acertar la mitad",
        "intro": (
            "Cada fila propone una pareja para un trinomio. La pregunta es si encaja: "
            "producto Y suma, las dos."
        ),
        "rows": [
            {
                "name": "2 y 3 en x²+5x+6",
                "symbol": r"2\cdot 3=6,\ 2+3=5",
                "latex": r"(x+2)(x+3)",
                "closed": "yes",
                "note": "Las dos condiciones. Encaja.",
            },
            {
                "name": "1 y 6 en x²+5x+6",
                "symbol": r"1\cdot 6=6,\ 1+6=7",
                "latex": r"(x+1)(x+6)=x^{2}+7x+6",
                "closed": "no",
                "note": "Acierta el producto y falla la suma. Es el error de esta sala.",
            },
            {
                "name": "−4 y −5 en x²−9x+20",
                "symbol": r"(-4)(-5)=20,\ -4-5=-9",
                "latex": r"(x-4)(x-5)",
                "closed": "yes",
                "note": "Producto positivo con suma negativa: los dos números negativos.",
            },
            {
                "name": "3 y −2 en x²+x−6",
                "symbol": r"3\cdot(-2)=-6,\ 3-2=1",
                "latex": r"(x+3)(x-2)",
                "closed": "yes",
                "note": "Producto negativo: los signos son distintos. Encaja igual.",
            },
            {
                "name": "El coeficiente principal no es 1",
                "symbol": r"2x^{2}+7x+3",
                "latex": r"(2x+1)(x+3)",
                "closed": "partial",
                "note": (
                    "El método sirve, pero la lista NO sale del 3: sale de 2·3 = 6. Se parte "
                    "el medio con 6 y 1 y se agrupa. Mismo oficio, un paso más."
                ),
            },
            {
                "name": "No hay pareja entera",
                "symbol": r"x^{2}+x+1",
                "latex": r"\text{no se factoriza con enteros}",
                "closed": "no",
                "note": (
                    "La única pareja que multiplica 1 es 1 y 1, y suma 2. No es que no la "
                    "encontremos: no existe."
                ),
            },
        ],
        "outro": (
            "La regla en una línea: **el producto da la lista, la suma elige.** Y si ninguna "
            "pareja de la lista suma lo que hace falta, el fardo no se despieza con enteros."
        ),
    },
    "abstraction_question": {
        "prompt": "Los tres tienen el mismo último término. ¿Qué determina el signo de los dos factores?",
        "thumbnails": [
            r"x^{2}+5x+6=(x+2)(x+3)",
            r"x^{2}-5x+6=(x-2)(x-3)",
            r"x^{2}-x-6=(x-3)(x+2)",
        ],
        "options": [
            {
                "id": "both",
                "text": (
                    "El signo del último dice si los dos números tienen el mismo signo, y el "
                    "del medio dice cuál es"
                ),
                "correct": True,
            },
            {
                "id": "mid",
                "text": "Solo el signo del término del medio",
                "correct": False,
            },
            {
                "id": "last",
                "text": "Solo el signo del término independiente",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Salim despieza $x^{2}+11x+24$. Si los dos listones miden $p$ y $q$, ¿cuánto vale "
            "el mayor menos el menor?"
        ),
        "polya": [
            "Entender: hay que hallar la pareja y luego restar.",
            "Planear: listo las parejas que multiplican 24 y elijo la que suma 11.",
            "Ejecutar: 1·24, 2·12, 3·8, 4·6. La que suma 11 es 3 y 8.",
            "Comprobar: (x + 3)(x + 8) = x² + 11x + 24 ✓. Y 8 − 3 = 5.",
        ],
        "prompt": "¿Cuánto vale el mayor menos el menor?",
        "answer": "5",
        "hints": {
            "n1": "Lista las parejas de enteros positivos que multiplican 24.",
            "n2": "La que suma 11 es 3 y 8.",
            "n3": "8 − 3.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que sabes probar antes de cortar.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya compruebas las dos condiciones antes de cerrar el despiece.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la condición de la "
            "suma antes de seguir."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Qué dos números suman 7 y multiplican 12? Escribe el mayor.",
                "answer": "4",
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuál es la factorización de $x^{2}+7x+10$?",
                "options": [
                    {"id": "ok", "text": r"$(x+2)(x+5)$", "latex": r"(x+2)(x+5)"},
                    {"id": "prod", "text": r"$(x+1)(x+10)$", "latex": r"(x+1)(x+10)"},
                    {"id": "neg", "text": r"$(x-2)(x-5)$", "latex": r"(x-2)(x-5)"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "prod": "pares_sin_verificar",
                    "neg": "ignora_el_signo_de_la_suma",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": "¿Cuánto es (−3) × (−6)?",
                "answer": "18",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de pasar a la bodega de los toneles.",
            "consolidacion": "Resuelto con ayuda: el despiece ya está, falta que salga solo.",
            "sin_ayuda": "Listones encajados. Compruebas las dos condiciones sin que te lo recuerden.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Producto y suma, las dos.",
        "default": (
            "Lista con el producto y elige con la suma. Una pareja que solo acierta el "
            "producto estampa otro trinomio."
        ),
        "fb_g03_e1_prod": (
            "Multiplican 6, sí — pero suman 7. Estampa (x+1)(x+6) y sale x² + 7x + 6, no el "
            "fardo original. Ese es el error del nodo."
        ),
        "fb_g03_e1_sum": (
            "Solo vale una: 1 y 4 multiplican 4, no 6. La factorización de un trinomio con "
            "enteros es única salvo el orden."
        ),
        "fb_g03_e1_neg": (
            "Con los dos negativos el producto sigue siendo 6, pero la suma sale −5 y el "
            "trinomio tiene +5x."
        ),
        "fb_g03_e5_pair": (
            "1 y 6 tampoco: multiplican 6 pero suman 7. El problema de la anotación son los "
            "signos, no la pareja."
        ),
        "fb_g03_e5_first": (
            "El primer término está bien: (x)(x) = x². El coeficiente principal es 1."
        ),
        "fb_g03_e5_none": (
            "Sí lo hay: 2 + 3 = 5, pero el trinomio tiene −5x. Con producto positivo y suma "
            "negativa, los dos números son negativos."
        ),
        "fb_g03_e6_trap": (
            "El producto solo da la lista de candidatos. 1 y 6 multiplican 6 y estampan "
            "x² + 7x + 6: la suma es la que decide."
        ),
        "fb_g03_e6_pos": (
            "El signo no cambia nada: 1 y 6 son positivos y siguen sin servir para "
            "x² + 5x + 6."
        ),
        "fb_g03_e6_prod": (
            "La respuesta es falsa, pero las dos condiciones hacen falta. Solo con la suma "
            "hay infinitas parejas."
        ),
    },
    "closing": (
        "Ya despiezas fardos de tres bultos comprobando las dos medidas. Queda un último "
        "tipo de carga en el almacén: los toneles. Vienen de dos en dos, con un volumen "
        "que suma o resta, y su molde no se parece a ninguno de los que has visto — deja "
        "un binomio y un trinomio, no dos binomios."
    ),
    "validation_status": "F5_G03_11bloques",
}
