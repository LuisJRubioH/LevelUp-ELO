"""L02 · El estante sellado — ser letra no te hace variable.

Segunda sala de la Casa de la Vida. Guía: Meritka. Vocabulario propio de la sala:
estante sellado, medida patrón, sello, cuerda de medir, vara, marca grabada.
Nada de cálamos ni tinta (eso es L01), ni de rampas ni parcelas.

Error focal: creer que la frontera pasa por el tipo de símbolo — toda letra
variable, todo número constante. La frontera pasa por si el valor puede cambiar.
"""

NODE_ID = "ALG-N1-L02-CONSTANTES"
CONCEPT_SLUG = "constantes"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "constantes",
    "misconception": "toda_letra_es_variable",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El estante sellado · Constantes",
    "house": "El estante sellado",
    "guide": "Meritka",
    "finish_label": "Pasar a la mesa de dictado",
    "title": "Ser letra no te hace variable",
    "intro": (
        "Ya sabes que una letra guarda un número. Ahora hay que separar, dentro del mismo "
        "registro, lo que cambia de lo que está fijado de una vez para siempre — y el "
        "aspecto del símbolo no sirve para decidirlo."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el estante. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Una vara patrón mide 7 palmos y no cambia nunca. ¿Cuánto miden 5 varas?",
                "answer": "35",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $6k$, ¿qué parte puede tomar valores distintos?",
                "options": [
                    {"id": "k", "text": r"La $k$"},
                    {"id": "six", "text": r"El $6$"},
                    {"id": "both", "text": "Las dos"},
                ],
                "expected": "k",
                "misconception_by_option": {
                    "six": "confunde_coeficiente_con_variable",
                    "both": "toda_letra_es_variable",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Puede un número fijo escribirse con una letra?",
                "options": [
                    {"id": "yes", "text": "Sí, si a esa letra se le ha fijado un valor"},
                    {"id": "no", "text": "No: las letras son siempre para lo que cambia"},
                    {"id": "only_greek", "text": "Solo si es una letra griega"},
                ],
                "expected": "yes",
                "misconception_by_option": {
                    "no": "toda_letra_es_variable",
                    "only_greek": "toda_letra_es_variable",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/l02-constantes-katia.png",
        "eyebrow": "KatIA · Ante el estante sellado",
        "title": "El estante que nadie puede corregir",
        "body": (
            "Meritka descorre un sello de arcilla. Dentro hay medidas patrón: una vara, "
            "una cuerda con nudos, un peso de piedra con una marca grabada.\n\n"
            "«Esto no se toca», dice. «Si mañana alguien decide que la vara mide otra cosa, "
            "todos los registros del archivo dejan de valer a la vez. Por eso está sellado: "
            "no porque sea valioso, sino porque tiene que ser el mismo siempre.»\n\n"
            "En el registro que KatIA acaba de escribir, en cambio, hay tres símbolos, y uno "
            "de ellos es una letra que tampoco puede cambiar nunca."
        ),
        "question": "¿Cómo se sabe si un símbolo puede cambiar de valor o no?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Las letras cambian y los números no"},
                {"id": "b", "text": "Depende de lo que represente, no de si es letra o número"},
                {"id": "c", "text": "Lo que va al principio de la expresión no cambia"},
            ],
            "response": (
                "Probemos esa idea. Guarda tu respuesta: al final vas a poder señalar el "
                "símbolo fijo de un registro aunque esté escrito con letra."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos símbolos que se parecen y no se comportan igual",
        "body": "Los dos son letras. Solo uno admite que le cambien el valor.",
        "cases": [
            {
                "label": "Cambia",
                "context": "El número de varas que se piden al almacén",
                "fraction": r"v",
                "division": r"v=3,\ 8,\ 12\ldots",
                "note": "Cada pedido trae un valor distinto. Es una variable.",
            },
            {
                "label": "No cambia",
                "context": "La longitud de la vara patrón, sellada en el estante",
                "fraction": r"L=7",
                "division": r"L=7\ \text{siempre}",
                "note": "Se escribe con letra por comodidad, pero su valor está fijado. Es una constante.",
            },
        ],
        "resolution": (
            "La frontera no pasa por el tipo de símbolo, sino por una pregunta: ¿alguien "
            "puede darle otro valor sin romper el registro? Si sí, es variable. Si no, es "
            "constante — y da igual que se escriba con cifra, con letra latina o con letra "
            "griega."
        ),
    },
    "definition_title": "Constante, coeficiente y término constante",
    "definition_katex": r"7v+2\qquad v\ \text{varía};\ 7\ \text{y}\ 2\ \text{no}",
    "definition": (
        "Una CONSTANTE es un valor que no cambia dentro del problema. Puede escribirse con "
        "cifra (el 2) o con letra (π, o una L a la que se le ha fijado un valor). Dentro de "
        "una expresión conviene distinguir dos papeles: el COEFICIENTE es la constante que "
        "multiplica a una variable, y el TÉRMINO CONSTANTE es la que va sola, sin letra al lado."
    ),
    "definition_symbols": [
        {"symbol": r"v", "reads": "uve", "means": "variable: cambia con cada pedido"},
        {
            "symbol": r"7\ \text{en}\ 7v",
            "reads": "coeficiente",
            "means": "constante que multiplica a la variable",
        },
        {
            "symbol": r"2\ \text{en}\ 7v+2",
            "reads": "término constante",
            "means": "constante que va sola, sin letra",
        },
        {
            "symbol": r"\pi\approx 3{,}1416",
            "reads": "pi",
            "means": "constante escrita con letra: nunca cambia",
        },
        {
            "symbol": r"L=7",
            "reads": "ele igual a siete",
            "means": "una letra a la que se le fija un valor deja de variar",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · El pedido al almacén",
            "title": "Separar lo fijo de lo que cambia",
            "statement": (
                "Cada vara que se pide cuesta 7 medidas de grano, y por cada pedido se "
                "cobran 2 medidas fijas de acarreo. Escribe el coste y di qué papel tiene "
                "cada número."
            ),
            "latex": r"7v+2",
            "image_slot": False,
            "steps": [
                "Lo que cambia es cuántas varas se piden: la llamo v. Es la variable.",
                "El 7 acompaña a la v y la multiplica: es el coeficiente.",
                "El 2 no toca a ninguna letra: es el término constante.",
                "El coste es 7v + 2. Con v = 4 son 30 medidas; con v = 10, son 72.",
                "Fíjate: el 7 y el 2 no cambiaron entre un pedido y otro. Solo cambió la v.",
            ],
            "solution": r"$7v+2$: variable $v$, coeficiente $7$, término constante $2$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "El 7 y el 2 son los dos constantes. ¿Por qué se les llama distinto?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El brocal del pozo",
            "title": "Una constante escrita con letra",
            "statement": (
                "El brocal del pozo del patio es circular. Su contorno se calcula con 2·π·r, "
                "donde r es el radio. ¿Qué cambia aquí y qué no?"
            ),
            "latex": r"2\pi r",
            "image_slot": False,
            "steps": [
                "Hay tres símbolos: el 2, la π y la r.",
                "El 2 es una cifra fija: constante, sin discusión.",
                "La π es una LETRA, pero su valor es siempre el mismo, unos 3,1416: constante también.",
                "La r es el radio: cambia según el pozo que se mida. Es la única variable.",
                "En 2πr hay dos constantes y una variable, aunque a simple vista haya una cifra y dos letras.",
            ],
            "solution": r"Variable: $r$. Constantes: $2$ y $\pi$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que contó las letras",
            "statement": (
                "Un aprendiz recibe el registro 2πr y anuncia: «hay dos letras, así que hay "
                "dos cantidades que cambian; el único número fijo es el 2»."
            ),
            "latex": r"2\pi r",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\pi\ \text{es letra}\Rightarrow\pi\ \text{varía}",
            "error_note": (
                "Contó símbolos en vez de preguntarse qué representa cada uno. Si π pudiera "
                "cambiar, el contorno del mismo pozo daría un número distinto cada día."
            ),
            "correct_version": {
                "wrong_latex": r"\pi\ \text{cambia}",
                "right_latex": r"\pi\approx 3{,}1416\ \text{siempre}",
                "rows": [
                    {
                        "wrong": "Es letra, luego varía",
                        "right": "Varía o no según lo que represente; π representa un valor fijo",
                    },
                    {
                        "wrong": "El 2 es el único fijo",
                        "right": "El 2 y π son fijos; la única que varía es r",
                    },
                ],
            },
            "explain_prompt": (
                "Explica por qué π no puede ser variable y di cuántas cantidades cambian de "
                "verdad en 2πr."
            ),
            "steps": [
                "Mido dos veces el mismo pozo: r vale lo mismo las dos veces y el contorno también.",
                "Mido otro pozo más ancho: cambia r, y solo r. π sigue valiendo 3,1416.",
                "Regla para no volver a caer: no cuentes letras, pregunta «¿esto puede tomar otro valor?».",
            ],
            "solution": (
                "En 2πr cambia una sola cosa: el radio. Ser letra no da permiso para variar, "
                "y ser cifra no es requisito para estar fijo."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El registro va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "El coste de un pedido es 7v + 2. ¿Cuánto cuesta pedir 6 varas?",
                "given_steps": [r"7v+2\quad\text{con }v=6", r"7\cdot 6=42"],
                "blanks": [{"id": "P1-b1", "label": r"42+2=", "answer": "44"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "En 9m + 5, escribe primero el coeficiente y después el término constante.",
                "given_steps": [r"9m+5"],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{coeficiente}=", "answer": "9"},
                    {"id": "P2-b2", "label": r"\text{término constante}=", "answer": "5"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: una cuerda patrón mide 12 palmos y se cortan t "
                    "trozos de 2 palmos. ¿Cuántos palmos quedan si t = 4?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"12-2t=", "answer": "4"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de decidir si algo es constante",
        "intro": r"¿Es constante la $g$ de $g\cdot t$, si $g$ es el peso de una piedra patrón?",
        "methods": [
            {
                "label": "Método 1 · Preguntar al enunciado",
                "steps": [
                    r"\text{«piedra patrón»}\Rightarrow\text{valor fijado}",
                    r"g\ \text{no cambia}",
                    r"g\ \text{es constante}",
                ],
                "note": "Inmediato cuando el enunciado dice de dónde sale el símbolo.",
            },
            {
                "label": "Método 2 · Probar dos casos",
                "steps": [
                    r"t=3:\ g\cdot 3",
                    r"t=8:\ g\cdot 8",
                    r"g\ \text{vale igual en los dos}\Rightarrow\text{constante}",
                ],
                "note": "Más lento, pero funciona aunque el enunciado no lo diga con claridad.",
            },
        ],
        "question": "¿Cuál usarías si el registro solo trae la fórmula, sin explicación?",
        "insight": (
            "El segundo. Cuando falta el enunciado, la única prueba fiable es mover una "
            "cantidad y mirar cuáles se mueven con ella: las que no se inmutan son las "
            "constantes, estén escritas como estén."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"En $8p-3$, ¿cuál es el término constante?",
            "options": [
                {"id": "minus3", "text": "−3", "latex": r"-3"},
                {"id": "eight", "text": "8", "latex": r"8"},
                {"id": "p", "text": "p", "latex": r"p"},
                {"id": "three", "text": "3", "latex": r"3"},
            ],
            "expected": "minus3",
            "feedback_by_option": {
                "minus3": "correct",
                "eight": "fb_l02_e1_coef",
                "p": "fb_l02_e1_var",
                "three": "fb_l02_e1_sign",
            },
            "misconception_by_option": {
                "eight": "confunde_coeficiente_con_constante",
                "p": "toda_letra_es_variable",
                "three": "pierde_el_signo_del_termino",
            },
            "hints": {
                "n1": "El término constante es el que va SIN letra al lado.",
                "n2": "El 8 está pegado a la p: multiplica, no va solo.",
                "n3": "El signo forma parte del término.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "El coste de un pedido es 7v + 2 medidas, donde v es el número de varas. "
                "¿Cuánto cuesta pedir 9 varas?"
            ),
            "expr": r"7v+2,\quad v=9",
            "answer": "65",
            "hints": {
                "n1": "Sustituye v por 9.",
                "n2": "Primero el producto, después la suma.",
                "n3": "63 + 2 = …",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"En el área del círculo, $A=\pi r^{2}$, ¿qué es $\pi$?",
            "options": [
                {"id": "constant", "text": "Una constante: siempre vale lo mismo"},
                {"id": "variable", "text": "Una variable: es una letra"},
                {"id": "unknown", "text": "Una incógnita que hay que despejar"},
                {"id": "area", "text": "El área, escrita de otra forma"},
            ],
            "expected": "constant",
            "feedback_by_option": {
                "constant": "correct",
                "variable": "fb_l02_e3_trap",
                "unknown": "fb_l02_e3_unknown",
                "area": "fb_l02_e3_area",
            },
            "misconception_by_option": {
                "variable": "toda_letra_es_variable",
                "unknown": "toda_letra_es_variable",
                "area": "confunde_simbolo_con_resultado",
            },
            "hints": {
                "n1": "¿Puede π valer una cosa hoy y otra mañana?",
                "n2": "Su valor es siempre unos 3,1416.",
                "n3": "Lo que cambia de un círculo a otro es el radio.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un escriba anota: «en 5x + 4 hay dos constantes, el 5 y el 4, y las dos son "
                "términos constantes». ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "role",
                    "text": "Constantes sí son las dos, pero el 5 es coeficiente: término constante solo el 4",
                },
                {"id": "not_constant", "text": "El 5 no es constante"},
                {"id": "count", "text": "Hay tres constantes, no dos"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "role",
            "feedback_by_option": {
                "role": "correct",
                "not_constant": "fb_l02_e4_notconst",
                "count": "fb_l02_e4_count",
                "none": "fb_l02_e4_none",
            },
            "misconception_by_option": {
                "not_constant": "confunde_coeficiente_con_variable",
                "count": "cuenta_simbolos_no_terminos",
                "none": "confunde_coeficiente_con_constante",
            },
            "hints": {
                "n1": "Las dos son constantes: eso está bien dicho.",
                "n2": "La diferencia está en si acompañan a una letra o van solas.",
                "n3": "El 5 multiplica a la x; el 4 no multiplica a nada.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Todo símbolo escrito con letra es una variable.»",
            "options": [
                {"id": "false", "text": r"Falsa: $\pi$ es letra y su valor nunca cambia"},
                {"id": "true", "text": "Verdadera: para eso se usan las letras"},
                {
                    "id": "true_latin",
                    "text": "Verdadera para las latinas; las griegas son otra cosa",
                },
                {
                    "id": "false_never",
                    "text": "Falsa: ninguna letra representa cantidades que cambian",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_l02_e5_trap",
                "true_latin": "fb_l02_e5_latin",
                "false_never": "fb_l02_e5_never",
            },
            "misconception_by_option": {
                "true": "toda_letra_es_variable",
                "true_latin": "toda_letra_es_variable",
                "false_never": "sobregeneraliza_constantes",
            },
            "hints": {
                "n1": "Para tumbar un «todo» basta UN contraejemplo.",
                "n2": "Piensa en una letra que siempre valga lo mismo.",
                "n3": "π vale 3,1416 hoy, mañana y en cualquier círculo.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": r"En el registro $4c+\pi-9$, selecciona TODOS los símbolos cuyo valor NO cambia.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$4$", "latex": r"4"},
                {"id": "b", "text": r"$c$", "latex": r"c"},
                {"id": "c", "text": r"$\pi$", "latex": r"\pi"},
                {"id": "d", "text": r"$-9$", "latex": r"-9"},
            ],
            "expected": ["a", "c", "d"],
            "trap_options": ["b"],
            "hints": {
                "n1": "Pregunta símbolo a símbolo: ¿puede tomar otro valor?",
                "n2": "π es letra, pero su valor está fijado.",
                "n3": "La única que depende del registro es la c.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Una cuerda patrón mide 12 palmos. De ella se cortan t trozos de 2 palmos "
                "para marcar linderos. Si se cortan 5 trozos, ¿cuántos palmos quedan?"
            ),
            "expr": r"12-2t,\quad t=5",
            "answer": "2",
            "hints": {
                "n1": "El 12 y el 2 no cambian; lo que cambia es t.",
                "n2": "Lo cortado es 2 · 5 = 10.",
                "n3": "12 − 10 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Cambia o está fijado?",
        "title": "Qué decide que un símbolo sea constante",
        "intro": (
            "El aspecto no decide nada. Lo único que importa es si alguien puede darle otro "
            "valor sin romper el registro."
        ),
        "rows": [
            {
                "symbol": r"2\ \text{en}\ 2\pi r",
                "name": "Una cifra suelta",
                "closed": "no",
                "latex": r"2",
                "note": "Constante evidente: es el caso fácil, y por eso engaña poco.",
            },
            {
                "symbol": r"\pi",
                "name": "Una letra fijada",
                "closed": "no",
                "latex": r"\pi\approx 3{,}1416",
                "note": "Letra y constante a la vez. Es el caso que desarma la trampa.",
            },
            {
                "symbol": r"7\ \text{en}\ 7v",
                "name": "El coeficiente",
                "closed": "no",
                "latex": r"7\cdot v",
                "note": "Constante, aunque esté pegado a una variable. No es término constante: acompaña.",
            },
            {
                "symbol": r"v",
                "name": "La variable",
                "closed": "yes",
                "latex": r"v=3,\ 8,\ 12\ldots",
                "note": "Cambia con cada pedido. La única del registro que se mueve.",
            },
            {
                "symbol": r"L=7",
                "name": "Una letra a la que se fija valor",
                "closed": "no",
                "latex": r"L=7",
                "note": "Nació como letra libre y quedó sellada. A partir de ahí, constante.",
            },
            {
                "symbol": r"a\ \text{en}\ ax+b",
                "name": "El parámetro",
                "closed": "partial",
                "latex": r"ax+b",
                "note": "Constante DENTRO de un problema, pero cambia de un problema a otro. Ni fijo del todo ni variable.",
            },
        ],
        "outro": (
            "La última fila es la honesta: hay símbolos quietos mientras dura el problema y "
            "que se mueven cuando cambias de problema. Se llaman parámetros, y por eso la "
            "pregunta útil no es «¿cambia?» sino «¿cambia AQUÍ?»."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres registros trabajados en este nodo?",
        "thumbnails": [r"7v+2", r"2\pi r", r"12-2t"],
        "options": [
            {
                "id": "mixed",
                "text": "En los tres conviven cantidades fijas con al menos una que cambia",
                "correct": True,
            },
            {
                "id": "not_shape",
                "text": "En los tres el aspecto del símbolo no basta para clasificarlo",
                "correct": True,
            },
            {
                "id": "letters_vary",
                "text": "En los tres todas las letras representan cantidades que cambian",
                "correct": False,
            },
            {
                "id": "digits_fixed",
                "text": "En los tres solo las cifras están fijas",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última anotación del estante: por cada sello de arcilla que se repone se gastan "
            "3 medidas de barro, y en cada hornada se pierden 4 medidas fijas por rotura. "
            "Hoy se reponen 11 sellos. ¿Cuántas medidas de barro hay que sacar?"
        ),
        "polya": {
            "comprender": "Hay una cantidad que cambia (los sellos) y una pérdida fija que no depende de cuántos sean.",
            "planear": "Escribo la regla con letra: 3s + 4, con s el número de sellos. Después sustituyo.",
            "ejecutar": "Con s = 11: 3 · 11 + 4 = 33 + 4 = 37.",
            "comprobar": "Si mañana se reponen 20, el 3 y el 4 no cambian: 3 · 20 + 4 = 64. Solo se movió la s ✓.",
        },
        "prompt": "¿Cuántas medidas de barro hacen falta?",
        "answer": "37",
        "hints": {
            "n1": "Separa lo que depende del número de sellos de lo que no.",
            "n2": "3s + 4, con s = 11.",
            "n3": "33 + 4 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otras medidas. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya decides por lo que representa el símbolo, no por su aspecto.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué una letra "
            "puede estar fijada."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Un peso patrón vale 4 medidas. ¿Cuánto pesan 8 de esos patrones?",
                "answer": "32",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $3y+11$, ¿cuál es el coeficiente?",
                "options": [
                    {"id": "three", "text": "3", "latex": r"3"},
                    {"id": "eleven", "text": "11", "latex": r"11"},
                    {"id": "y", "text": "y", "latex": r"y"},
                ],
                "expected": "three",
                "misconception_by_option": {
                    "eleven": "confunde_coeficiente_con_constante",
                    "y": "confunde_coeficiente_con_variable",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál de estos símbolos NO cambia nunca de valor?",
                "options": [
                    {"id": "pi", "text": r"$\pi$"},
                    {"id": "x", "text": r"la $x$ de $2x+1$"},
                    {"id": "r", "text": r"la $r$ de $2\pi r$"},
                ],
                "expected": "pi",
                "misconception_by_option": {
                    "x": "toda_letra_es_variable",
                    "r": "toda_letra_es_variable",
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
        "default": "No mires si es letra o cifra: pregunta si su valor puede cambiar aquí.",
        "fb_l02_e1_coef": (
            "El 8 está pegado a la p: la multiplica, así que es coeficiente. → El término "
            "constante va solo."
        ),
        "fb_l02_e1_var": "La p es la variable, no una constante. → Busca el número que va sin letra.",
        "fb_l02_e1_sign": "Casi: el signo forma parte del término. → La expresión resta ese 3.",
        "fb_l02_e3_trap": (
            "π es letra y aun así vale siempre lo mismo. → ¿Podría el mismo círculo tener "
            "dos áreas distintas?"
        ),
        "fb_l02_e3_unknown": (
            "Una incógnita se despeja porque no se sabe; π se sabe. → Su valor es 3,1416 y pico."
        ),
        "fb_l02_e3_area": (
            "El área es A, no π. → π es el factor fijo que aparece en todo círculo."
        ),
        "fb_l02_e4_notconst": (
            "El 5 sí es constante: no cambia. → Lo que cambia es cómo se le llama según "
            "acompañe o no a una letra."
        ),
        "fb_l02_e4_count": (
            "Constantes hay dos: 5 y 4. → El error del escriba no es contar, es el nombre "
            "que les da."
        ),
        "fb_l02_e4_none": "«Término constante» es el que va SOLO. → ¿A quién multiplica el 5?",
        "fb_l02_e5_trap": "Las letras también sirven para nombrar valores fijos. → Piensa en π.",
        "fb_l02_e5_latin": (
            "El alfabeto no decide: una L latina puede quedar sellada con un valor fijo. "
            "→ Lo que decide es qué representa."
        ),
        "fb_l02_e5_never": (
            "Te pasaste al otro extremo: la v de 7v sí cambia. → Hay letras de los dos tipos."
        ),
    },
    "closing": (
        "Ya distingues lo sellado de lo que se mueve, aunque las dos cosas se escriban con "
        "letra. Con esto sabes leer un registro ya escrito — falta escribirlo tú, a partir "
        "de un encargo que llega hablado. Eso se hace en la mesa de dictado."
    ),
    "validation_status": "F5_L02_11bloques",
}
