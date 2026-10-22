"""B12 · Detective de falsedades — dar vuelta una afirmación la cambia.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: el error del recíproco — de «todo entero es racional» se
concluye «todo racional es entero».
"""

NODE_ID = "PREALG-N1-B12-DETECTIVE-FALSEDADES"
CONCEPT_SLUG = "detective"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "detective",
    "misconception": "error_del_reciproco",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Consolidación · Detective",
    "finish_label": "Ir al diagnóstico de cierre",
    "title": "Dar vuelta una frase no la conserva",
    "intro": (
        "Ya sabes clasificar. Ahora vas a juzgar afirmaciones: decidir si una frase sobre "
        "conjuntos es verdadera o falsa, y —esto es lo nuevo— demostrarlo. Vas a descubrir "
        "que para tumbar una afirmación basta UN ejemplo, y que la trampa más común de "
        "todas es leer una frase al revés."
    ),
    # --- Bloque 2 · Mini-diagnóstico (siembra ELO, no puntúa) ----------------
    "diagnostic": {
        "intro": (
            "Antes de empezar, tres rápidas. No hay nota; me sirven para saber por "
            "dónde entrarle."
        ),
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "«Todo entero es racional». ¿Verdadera o falsa?",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "no_reconoce_inclusion"},
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "«Todo racional es entero». ¿Verdadera o falsa?",
                "options": [
                    {"id": "false", "text": "Falsa"},
                    {"id": "true", "text": "Verdadera"},
                ],
                # Es el recíproco literal de D1. Quien responda igual a las dos
                # está leyendo la inclusión como si fuera simétrica.
                "expected": "false",
                "misconception_by_option": {"true": "error_del_reciproco"},
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Para demostrar que «todo número par es mayor que 10» es falsa, ¿qué basta?",
                "options": [
                    {"id": "one", "text": "Un solo ejemplo que la incumpla, como el 4"},
                    {"id": "many", "text": "Muchos ejemplos que la incumplan"},
                    {"id": "all", "text": "Revisar todos los números pares"},
                ],
                "expected": "one",
                "misconception_by_option": {
                    "many": "necesita_muchos_contraejemplos",
                    "all": "exige_verificacion_exhaustiva",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · Consolidación",
        "title": "El sofista en el pórtico",
        "body": (
            "Un sofista cobra por enseñar a ganar discusiones. Hoy tiene público y suelta "
            "esto: «Todos los que estudian en la escuela de Pitágoras saben geometría. "
            "Por lo tanto, todos los que saben geometría estudian en la escuela de "
            "Pitágoras».\n\n"
            "La gente asiente. Suena bien: las dos frases usan las mismas palabras y "
            "parecen decir lo mismo. Al fondo, un cantero que aprendió geometría solo, "
            "midiendo piedras, no dice nada."
        ),
        "question": (
            "¿La segunda frase se sigue de la primera? Y si no: ¿qué basta para tumbarla?"
        ),
        "image": "/leccion/01-prealg-n1-agora/b12-detective-falsedades-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "Sí se sigue: dicen lo mismo con otro orden"},
                {"id": "b", "text": "No se sigue, y el cantero del fondo lo prueba"},
                {"id": "c", "text": "No se puede decidir sin conocer a toda la gente"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber por qué "
                "ese giro de frase es el error más frecuente en todo este nivel."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "La misma frase, dada vuelta",
        "body": (
            "Las dos afirmaciones de abajo usan exactamente las mismas dos palabras. Solo "
            "cambia el orden. Una es verdadera y la otra es falsa."
        ),
        "cases": [
            {
                "label": "Verdadera",
                "context": "Todo entero es racional",
                "fraction": r"\mathbb{Z}\subset\mathbb{Q}",
                "division": r"n=\dfrac{n}{1}",
                "note": (
                    "Cualquier entero se escribe sobre 1, así que sí: no hay ni un entero "
                    "que se escape de ℚ."
                ),
            },
            {
                "label": "Falsa",
                "context": "Todo racional es entero",
                "fraction": r"\mathbb{Q}\not\subset\mathbb{Z}",
                "division": r"\dfrac{1}{2}\in\mathbb{Q},\ \dfrac{1}{2}\notin\mathbb{Z}",
                "note": (
                    "Basta 1/2 para tumbarla. Un solo caso que la incumpla y la "
                    "afirmación cae entera."
                ),
            },
        ],
        "resolution": (
            "«Todo A es B» NO es lo mismo que «todo B es A». La primera dice que A está "
            "dentro de B; la segunda diría que B está dentro de A, que es otra cosa. Y "
            "fíjate en la asimetría de la prueba: para sostener «todo A es B» hay que "
            "revisarlos todos, pero para tumbarla basta UNO solo que falle. Ese uno se "
            "llama contraejemplo, y es el arma del detective."
        ),
    },
    "definition_title": "Afirmación, recíproco y contraejemplo",
    "definition_katex": r"\text{«todo }A\text{ es }B\text{»}\ \equiv\ A\subset B\qquad\not\equiv\qquad B\subset A",
    "definition": (
        "La frase del nodo: para tumbar una afirmación universal basta un contraejemplo. "
        "Para sostenerla no basta ningún número de ejemplos."
    ),
    "definition_symbols": [
        {
            "symbol": r"A\subset B",
            "reads": "A contenido en B",
            "means": "«todo A es B»: la afirmación original",
        },
        {
            "symbol": r"B\subset A",
            "reads": "B contenido en A",
            "means": "«todo B es A»: el recíproco, que es OTRA afirmación",
        },
        {
            "symbol": r"\not\subset",
            "reads": "no está contenido",
            "means": "existe al menos un elemento que se escapa",
        },
        {
            "symbol": r"\exists",
            "reads": "existe",
            "means": "con uno alcanza: la marca del contraejemplo",
        },
        {
            "symbol": r"\forall",
            "reads": "para todo",
            "means": "sin excepciones: lo que afirma una frase universal",
        },
        {
            "symbol": r"\tfrac{1}{2}\notin\mathbb{Z}",
            "reads": "un medio no es entero",
            "means": "el contraejemplo que tumba «todo racional es entero»",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Tumbar con un contraejemplo",
            "title": "«Todo real es racional»",
            "statement": "Decide si la afirmación «todo número real es racional» es verdadera o falsa, y demuéstralo.",
            "latex": r"\mathbb{R}\subset\mathbb{Q}\ ?",
            "image_slot": False,
            "steps": [
                "La afirmación es universal: dice que NINGÚN real se escapa de ℚ.",
                "Para tumbarla no necesito revisarlos todos: me basta encontrar uno que falle.",
                "Busco un real que no sea racional. √2 es real (está en la recta).",
                "¿Es racional? No: se demostró en B07 que no existe fracción que lo dé.",
                "√2 es real y no es racional. Un contraejemplo, y la afirmación es FALSA.",
            ],
            "solution": r"Falsa. Contraejemplo: $\sqrt{2}\in\mathbb{R}$ pero $\sqrt{2}\notin\mathbb{Q}$.",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "En el paso 2 dije que no hacía falta revisarlos todos. ¿Por qué un "
                    "solo caso alcanza para tumbar la frase, si son infinitos números?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Sostener con la definición",
            "title": "«Todo natural es racional»",
            "statement": "Decide si la afirmación «todo número natural es racional» es verdadera o falsa, y demuéstralo.",
            "latex": r"\mathbb{N}\subset\mathbb{Q}\ ?",
            "image_slot": False,
            "steps": [
                "Busco un contraejemplo: un natural que no sea racional. Pruebo 7, 0, 100…",
                "No encuentro ninguno, pero eso no demuestra nada: podrían faltarme casos.",
                "Cambio de estrategia: en vez de ejemplos, uso la definición.",
                "Un racional es a/b con a, b enteros y b ≠ 0. Cualquier natural n se escribe n/1.",
                "n/1 cumple la definición para TODO n. Por eso la afirmación es VERDADERA.",
            ],
            "solution": r"Verdadera. Prueba: $n=\dfrac{n}{1}$ para todo $n\in\mathbb{N}$.",
        },
        {
            "eyebrow": "Trampa común",
            "title": "La frase leída al revés",
            "statement": (
                "Un discípulo razonó así. Está mal: «En clase probamos que todo entero es "
                "racional. Entonces también es cierto que todo racional es entero: es la "
                "misma frase, solo cambié el orden»."
            ),
            "latex": r"\mathbb{Z}\subset\mathbb{Q}\ \Rightarrow\ \mathbb{Q}\subset\mathbb{Z}",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\mathbb{Z}\subset\mathbb{Q}\ \underline{\Rightarrow}\ \mathbb{Q}\subset\mathbb{Z}",
            "error_note": (
                "Aquí se cayó. Dar vuelta una implicación produce una afirmación NUEVA, "
                "que hay que probar por separado. No viene de regalo con la original."
            ),
            "correct_version": {
                "wrong_latex": r"\text{todo entero es racional}\ \Rightarrow\ \text{todo racional es entero}",
                "right_latex": r"\mathbb{Z}\subset\mathbb{Q}\ \text{ es V};\quad \mathbb{Q}\subset\mathbb{Z}\ \text{ es F, porque }\tfrac{1}{2}\in\mathbb{Q}\setminus\mathbb{Z}",
                "rows": [
                    {
                        "wrong": "Cambiar el orden no cambia la frase",
                        "right": "Cambiar el orden produce el recíproco, que es otra afirmación",
                    },
                    {
                        "wrong": "Si una es verdadera, la otra también",
                        "right": "1/2 es racional y no es entero: la recíproca es falsa",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué el recíproco no se sigue de la afirmación original? Da el "
                "contraejemplo que lo tumba."
            ),
            "steps": [
                "Escribe las dos frases una debajo de la otra y subraya qué conjunto va primero.",
                "La primera dice ℤ está dentro de ℚ. La segunda diría ℚ está dentro de ℤ.",
                "Busca un racional que no sea entero: con uno solo alcanza.",
            ],
            "solution": (
                "Es el mismo giro del sofista: «todos los de la escuela saben geometría» "
                "no implica «todos los que saben geometría son de la escuela» — el cantero "
                "del fondo lo desmiente. Con conjuntos pasa igual: ℤ ⊂ ℚ es cierto, "
                "ℚ ⊂ ℤ es falso, y 1/2 es el cantero."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el juicio ya está empezado y "
            "solo faltan huecos. Responde 1 si la afirmación es verdadera y 0 si es falsa."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "«Todo natural es entero». ¿Verdadera (1) o falsa (0)?",
                "given_steps": [
                    r"\mathbb{N}\subset\mathbb{Z}\ \text{es la cadena de inclusión}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Respuesta (1=V, 0=F)}=", "answer": "1"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "«Todo entero es natural» y «todo irracional es real». Juzga las dos."
                ),
                "given_steps": [
                    r"\text{Contraejemplo para la primera}:\ -3",
                ],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"\text{«Todo entero es natural» (1=V, 0=F)}=",
                        "answer": "0",
                    },
                    {
                        "id": "P2-b2",
                        "label": r"\text{«Todo irracional es real» (1=V, 0=F)}=",
                        "answer": "1",
                    },
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: «Ningún racional es irracional». ¿Verdadera (1) "
                    "o falsa (0)? Cuidado: esta afirmación no es del mismo tipo que las anteriores."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Respuesta (1=V, 0=F)}=", "answer": "1"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos formas de juzgar una afirmación",
        "intro": r"¿Es verdadera «todo racional es real»? Las dos soluciones son correctas.",
        "methods": [
            {
                "label": "Método 1 · Buscar contraejemplo",
                "steps": [
                    r"\tfrac{1}{2}?\ \text{real}",
                    r"-\tfrac{7}{3}?\ \text{real}",
                    r"\text{no aparece ninguno}",
                ],
                "note": "Rápido para TUMBAR. Si no aparece, no concluye nada por sí solo.",
            },
            {
                "label": "Método 2 · Usar la definición",
                "steps": [
                    r"\mathbb{R}=\mathbb{Q}\cup\mathbb{I}",
                    r"\text{todo }x\in\mathbb{Q}\ \text{está en la unión}",
                    r"\Rightarrow\ \text{verdadera}",
                ],
                "note": "Único que puede SOSTENER una afirmación universal.",
            },
        ],
        "question": (
            "¿Cuál conviene aquí y por qué? Y la de verdad: si buscas contraejemplos "
            "durante una hora y no encuentras ninguno, ¿ya probaste la afirmación?"
        ),
        "insight": (
            "No. Ese es el punto asimétrico de todo el nodo: un contraejemplo tumba, pero "
            "mil ejemplos no sostienen. Para afirmar «todo A es B» hay que argumentar "
            "desde la definición, como en el ejemplo 2. Buscar contraejemplos sirve para "
            "sospechar, no para concluir."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "«Todo número natural es real». ¿Verdadera o falsa?",
            "options": [
                {"id": "true", "text": "Verdadera: ℕ ⊂ ℝ"},
                {"id": "false", "text": "Falsa"},
                {"id": "cannot", "text": "No se puede decidir"},
            ],
            "expected": "true",
            "feedback_by_option": {
                "true": "correct",
                "false": "fb_b12_e1_false",
                "cannot": "fb_b12_e1_cannot",
            },
            "misconception_by_option": {
                "false": "no_reconoce_inclusion",
                "cannot": "habito_evita_decidir",
            },
            "hints": {
                "n1": "¿Puedes ubicar el 7 en la recta numérica?",
                "n2": "Sí, y todo lo que está en la recta es real.",
                "n3": "ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ: la cadena lo garantiza para todos.",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "«Todo número real es natural». ¿Verdadera o falsa?",
            "options": [
                {"id": "false", "text": "Falsa: −3 es real y no es natural"},
                {"id": "true", "text": "Verdadera: es la misma frase de antes"},
                {"id": "cannot", "text": "No se puede decidir"},
            ],
            # Recíproco literal de E1, a propósito y consecutivo.
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_b12_e2_reciprocal",
                "cannot": "fb_b12_e2_cannot",
            },
            "misconception_by_option": {
                "true": "error_del_reciproco",
                "cannot": "habito_evita_decidir",
            },
            "hints": {
                "n1": "Es la frase anterior dada vuelta: hay que juzgarla de nuevo.",
                "n2": "Busca un real que no sea natural.",
                "n3": "−3 o 0,5 sirven: los dos son reales y ninguno es natural.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estos contraejemplos tumba «todo número racional es positivo»?",
            "options": [
                {"id": "neg_frac", "text": "−1/2, que es racional y negativo"},
                {"id": "sqrt2", "text": "√2, que no es racional"},
                {"id": "zero", "text": "0, que no es racional"},
                {"id": "five", "text": "5, que es racional y positivo"},
            ],
            "expected": "neg_frac",
            "feedback_by_option": {
                "neg_frac": "correct",
                "sqrt2": "fb_b12_e3_notrational",
                "zero": "fb_b12_e3_zero",
                "five": "fb_b12_e3_confirms",
            },
            "misconception_by_option": {
                "sqrt2": "contraejemplo_fuera_del_conjunto",
                "zero": "cero_no_es_racional",
                "five": "confunde_ejemplo_con_contraejemplo",
            },
            "hints": {
                "n1": "Un contraejemplo debe CUMPLIR la hipótesis y FALLAR la conclusión.",
                "n2": "Aquí: tiene que ser racional (hipótesis) y no positivo (falla la conclusión).",
                "n3": "√2 no sirve porque ni siquiera es racional: no cumple la hipótesis.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un discípulo argumentó: «Probé con 4, con 16 y con 100, y en los tres "
                "casos la raíz dio un natural. Entonces la raíz de todo natural es un "
                "natural». ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "examples",
                    "text": "Tres ejemplos no prueban una afirmación universal; √2 la tumba",
                },
                {"id": "wrong_roots", "text": "Calculó mal alguna de las tres raíces"},
                {"id": "reciprocal", "text": "Confundió la afirmación con su recíproca"},
                {"id": "none", "text": "Ningún error: los tres casos lo confirman"},
            ],
            "expected": "examples",
            "feedback_by_option": {
                "examples": "correct",
                "wrong_roots": "fb_b12_e4_roots",
                "reciprocal": "fb_b12_e4_reciprocal",
                "none": "fb_b12_e4_none",
            },
            "misconception_by_option": {
                "wrong_roots": "duda_del_calculo_correcto",
                "reciprocal": "confunde_tipo_de_error",
                "none": "ejemplos_prueban_universal",
            },
            "hints": {
                "n1": "Las tres raíces están bien calculadas: 2, 4 y 10.",
                "n2": "El problema es el salto de «tres casos» a «todos los casos».",
                "n3": "√2 es raíz de un natural y no es natural: la afirmación es falsa.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "«Todo irracional es real» es verdadera. ¿Se sigue de ahí que «todo real "
                "es irracional»?"
            ),
            "options": [
                {"id": "no_reciprocal", "text": "No: es el recíproco, y 5 lo tumba"},
                {"id": "yes_same", "text": "Sí: es la misma frase con el orden cambiado"},
                {"id": "no_first_false", "text": "No, porque la primera también es falsa"},
                {"id": "cannot", "text": "No se puede decidir sin más información"},
            ],
            "expected": "no_reciprocal",
            "feedback_by_option": {
                "no_reciprocal": "correct",
                "yes_same": "fb_b12_e5_trap",
                "no_first_false": "fb_b12_e5_first",
                "cannot": "fb_b12_e5_cannot",
            },
            "misconception_by_option": {
                "yes_same": "error_del_reciproco",
                "no_first_false": "no_reconoce_inclusion",
                "cannot": "habito_evita_decidir",
            },
            "hints": {
                "n1": "Dar vuelta una frase produce una afirmación nueva.",
                "n2": "Busca un real que NO sea irracional.",
                "n3": "5 es real y es racional, no irracional: tumba el recíproco.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El sofista vuelve con esta: «Todo número con coma es racional». ¿Cómo la "
                "juzgas?"
            ),
            "options": [
                {
                    "id": "false_pi",
                    "text": "Falsa: π se escribe con coma (3,1415…) y es irracional",
                },
                {"id": "true_comma", "text": "Verdadera: la coma indica que viene de una división"},
                {
                    "id": "false_integers",
                    "text": "Falsa: los enteros no llevan coma y también son racionales",
                },
                {"id": "cannot", "text": "No se puede decidir"},
            ],
            "expected": "false_pi",
            "feedback_by_option": {
                "false_pi": "correct",
                "true_comma": "fb_b12_e6_comma",
                "false_integers": "fb_b12_e6_integers",
                "cannot": "fb_b12_e6_cannot",
            },
            "misconception_by_option": {
                "true_comma": "clasifica_por_apariencia",
                "false_integers": "confunde_contraejemplo_con_caso_no_cubierto",
                "cannot": "habito_evita_decidir",
            },
            "hints": {
                "n1": "Necesitas un número con coma que NO sea racional.",
                "n2": "Piensa en los irracionales: ¿cómo se escriben en decimal?",
                "n3": "π = 3,1415… lleva coma y no es fracción de enteros.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas cuatro afirmaciones es la ÚNICA falsa?",
            "options": [
                {"id": "false_one", "text": "Todo racional es entero"},
                {"id": "true_nat", "text": "Todo natural es entero"},
                {"id": "true_int", "text": "Todo entero es real"},
                {"id": "true_irr", "text": "Ningún irracional es racional"},
            ],
            "expected": "false_one",
            "feedback_by_option": {
                "false_one": "correct",
                "true_nat": "fb_b12_e7_true",
                "true_int": "fb_b12_e7_true",
                "true_irr": "fb_b12_e7_true",
            },
            "misconception_by_option": {
                "true_nat": "no_reconoce_inclusion",
                "true_int": "no_reconoce_inclusion",
                "true_irr": "no_distingue_exclusion",
            },
            "hints": {
                "n1": "Tres son inclusiones del mapa; una va en dirección contraria.",
                "n2": "Busca la que dice que un conjunto grande cabe dentro de uno pequeño.",
                "n3": "1/2 es racional y no es entero: esa es la falsa.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "El expediente del detective",
        "title": "Cada afirmación, su veredicto y su prueba",
        "intro": "Verdadera se prueba con la definición; falsa se tumba con un contraejemplo.",
        "rows": [
            {
                "symbol": r"\mathbb{N}\subset\mathbb{Z}",
                "name": "Todo natural es entero",
                "closed": "yes",
                "latex": r"n=n",
                "note": "Verdadera. Prueba: la cadena de inclusión.",
            },
            {
                "symbol": r"\mathbb{Z}\subset\mathbb{Q}",
                "name": "Todo entero es racional",
                "closed": "yes",
                "latex": r"n=\tfrac{n}{1}",
                "note": "Verdadera. Prueba: se escribe sobre 1.",
            },
            {
                "symbol": r"\mathbb{Q}\subset\mathbb{Z}",
                "name": "Todo racional es entero",
                "closed": "no",
                "latex": r"\tfrac{1}{2}\notin\mathbb{Z}",
                "note": "FALSA. El recíproco de la anterior.",
            },
            {
                "symbol": r"\mathbb{R}\subset\mathbb{Q}",
                "name": "Todo real es racional",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Q}",
                "note": "FALSA. Contraejemplo: la diagonal de B07.",
            },
            {
                "symbol": r"\mathbb{Q}\cap\mathbb{I}=\varnothing",
                "name": "Ningún racional es irracional",
                "closed": "yes",
                "latex": r"\varnothing",
                "note": "Verdadera. Prueba: irracional significa «no racional».",
            },
        ],
        "outro": (
            "Mira las filas 2 y 3: son la misma frase dada vuelta, y tienen veredictos "
            "opuestos. Ese par es el resumen del nodo entero."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué tienen en común los razonamientos falsos que cazaste hoy?",
        "thumbnails": [
            r"\mathbb{Q}\subset\mathbb{Z}",
            r"\mathbb{R}\subset\mathbb{N}",
            r"\mathbb{R}\subset\mathbb{I}",
        ],
        "options": [
            {
                "id": "reciprocal",
                "text": "En todos se dio vuelta una afirmación verdadera y se supuso que seguía valiendo",
                "correct": True,
            },
            {
                "id": "one_counter",
                "text": "Todos se tumban con un solo contraejemplo",
                "correct": True,
            },
            {"id": "calculation", "text": "Todos tienen un error de cálculo", "correct": False},
            {"id": "irrational", "text": "Todos hablan de números irracionales", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El sofista suelta cinco afirmaciones: (1) Todo natural es racional. "
            "(2) Todo racional es natural. (3) Todo irracional es real. "
            "(4) Todo real es irracional. (5) Ningún entero es irracional. "
            "¿Cuántas son VERDADERAS?"
        ),
        "polya": {
            "comprender": (
                "Me dan cinco afirmaciones. Debo decidir cuántas son verdaderas. Noto que "
                "vienen en pares: la 2 es el recíproco de la 1, y la 4 el de la 3."
            ),
            "planear": (
                "Juzgo cada una por separado, sin asumir que el recíproco hereda el "
                "veredicto. Verdadera → la justifico con la definición; falsa → busco un "
                "contraejemplo."
            ),
            "ejecutar": (
                "(1) V: n = n/1. (2) F: 1/2 es racional y no natural. (3) V: 𝕀 ⊂ ℝ. "
                "(4) F: 5 es real y racional. (5) V: todo entero es racional, y ℚ e 𝕀 "
                "no comparten nada. Van 3."
            ),
            "comprobar": (
                "Reviso los dos pares: en cada uno una es verdadera y su recíproca es "
                "falsa. ✓ Coherente con el nodo: dar vuelta la frase no conserva el "
                "veredicto."
            ),
        },
        "prompt": "¿Cuántas de las cinco son verdaderas?",
        "answer": "3",
        "hints": {
            "n1": "Juzga cada una por separado; no supongas que el recíproco hereda nada.",
            "n2": "Las afirmaciones 2 y 4 son los recíprocos de la 1 y la 3.",
            "n3": "1/2 tumba la 2, y 5 tumba la 4. Quedan tres verdaderas.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico ----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otras frases. Sin nota: solo miramos si algo se movió.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: hoy resolviste más que al entrar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué dar "
            "vuelta una frase produce otra afirmación."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "«Todo natural es racional». ¿Verdadera o falsa?",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "no_reconoce_inclusion"},
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "«Todo racional es natural». ¿Verdadera o falsa?",
                "options": [
                    {"id": "false", "text": "Falsa"},
                    {"id": "true", "text": "Verdadera"},
                ],
                "expected": "false",
                "misconception_by_option": {"true": "error_del_reciproco"},
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Para tumbar «todo número entero es positivo», ¿qué basta?",
                "options": [
                    {"id": "one", "text": "Un solo contraejemplo, como −4"},
                    {"id": "many", "text": "Varios contraejemplos"},
                    {"id": "all", "text": "Revisar todos los enteros"},
                ],
                "expected": "one",
                "misconception_by_option": {
                    "many": "necesita_muchos_contraejemplos",
                    "all": "exige_verificacion_exhaustiva",
                },
            },
        ],
    },
    # --- Bloque 11 · Footer + feedback ---------------------------------------
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
        "default": "Revisa el procedimiento paso a paso y vuelve a intentarlo.",
        "fb_b12_e1_false": (
            "Para que fuera falsa tendría que existir un natural que no sea real, y no "
            "existe: todos están en la recta. → Intenta dar un contraejemplo y verás que "
            "no aparece."
        ),
        "fb_b12_e1_cannot": (
            "Sí se puede decidir: la cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ lo resuelve. → Di si 7 está en "
            "la recta."
        ),
        "fb_b12_e2_reciprocal": (
            "Esa es la trampa del nodo: no es la misma frase, es su recíproca, y hay que "
            "juzgarla aparte. → Busca un real que no sea natural."
        ),
        "fb_b12_e2_cannot": (
            "Sí se puede: basta un contraejemplo. → Nombra un número real que no sirva "
            "para contar."
        ),
        "fb_b12_e3_notrational": (
            "√2 no sirve como contraejemplo aquí: para serlo tendría que ser racional "
            "(cumplir la hipótesis) y no serlo. → Busca uno que SÍ sea racional."
        ),
        "fb_b12_e3_zero": (
            "0 sí es racional (0/1), así que la razón que diste no se sostiene. Además 0 "
            "no es negativo. → Busca un racional que sea claramente negativo."
        ),
        "fb_b12_e3_confirms": (
            "5 confirma la afirmación en vez de tumbarla: es racional Y positivo. Un "
            "contraejemplo tiene que FALLAR la conclusión. → Busca uno negativo."
        ),
        "fb_b12_e4_roots": (
            "Las tres están bien: √4 = 2, √16 = 4, √100 = 10. El error es de razonamiento, "
            "no de cálculo. → Di si tres casos alcanzan para afirmar «todos»."
        ),
        "fb_b12_e4_reciprocal": (
            "Aquí no hay recíproco: no dio vuelta ninguna frase. El error es otro: saltó "
            "de tres ejemplos a todos los casos. → Da un contraejemplo a su conclusión."
        ),
        "fb_b12_e4_none": (
            "Sí hay error: √2 es raíz de un natural y no es natural. Ningún número de "
            "ejemplos prueba una afirmación universal. → Nombra el contraejemplo."
        ),
        "fb_b12_e5_trap": (
            "Ese es justo el error del nodo: cambiar el orden crea una afirmación nueva. "
            "5 es real y NO es irracional. → Escribe el contraejemplo del recíproco."
        ),
        "fb_b12_e5_first": (
            "La primera sí es verdadera: todo irracional está en la recta. Lo que falla "
            "es la segunda. → Busca un real que no sea irracional."
        ),
        "fb_b12_e5_cannot": (
            "Sí se puede decidir, y con un solo número. → Nombra un real que sea racional."
        ),
        "fb_b12_e6_comma": (
            "La coma no garantiza nada: π se escribe 3,1415… y no es fracción de enteros. "
            "Es el error de clasificar por el símbolo (B10). → Da ese contraejemplo."
        ),
        "fb_b12_e6_integers": (
            "Que los enteros no lleven coma no tumba la frase: la afirmación solo habla "
            "de los que SÍ la llevan. → Busca un número con coma que no sea racional."
        ),
        "fb_b12_e6_cannot": (
            "Sí se puede: basta un contraejemplo. → Piensa cómo se escribe π en decimal."
        ),
        "fb_b12_e7_true": (
            "Esa es verdadera: es una inclusión (o una exclusión) del mapa. → Busca la que "
            "mete un conjunto grande dentro de uno pequeño."
        ),
    },
    "closing": (
        "El cantero del fondo nunca dijo nada, y con existir bastaba. Un contraejemplo "
        "tumba; ningún número de ejemplos sostiene. Con eso cierras el nivel."
    ),
    "validation_status": "F1_B12_11bloques",
}
