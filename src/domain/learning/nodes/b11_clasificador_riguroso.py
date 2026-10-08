"""B11 · Clasificador riguroso — un número vive en varios conjuntos a la vez.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «un número pertenece a un solo conjunto» — si 5 es natural,
entonces no es entero.
"""

NODE_ID = "PREALG-N1-B11-CLASIFICADOR-RIGUROSO"
CONCEPT_SLUG = "clasificador_riguroso"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "clasificador_riguroso",
    "misconception": "pertenencia_unica",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Consolidación · Clasificador riguroso",
    "finish_label": "Continuar al detective",
    "title": "El mismo número, varias casas",
    "intro": (
        "En el nodo anterior buscabas el peldaño más bajo. Aquí vas a hacer lo contrario: "
        "listar TODOS los conjuntos a los que pertenece un número. Suena a más trabajo y "
        "en realidad es una sola idea: la cadena de inclusión hace casi todo el trabajo."
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
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿A cuántos de los cinco conjuntos $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ pertenece el número 8?",
                "answer": "4",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si un número es entero, ¿puede ser racional al mismo tiempo?",
                "options": [
                    {"id": "yes", "text": "Sí: todo entero se escribe n/1"},
                    {"id": "no", "text": "No: o es entero o es racional, no las dos"},
                    {"id": "sometimes", "text": "Solo algunos enteros"},
                ],
                "expected": "yes",
                "misconception_by_option": {
                    "no": "pertenencia_unica",
                    "sometimes": "pertenencia_unica",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Puede un número ser racional e irracional a la vez?",
                "options": [
                    {"id": "never", "text": "Nunca: son los únicos dos que se excluyen"},
                    {"id": "sometimes", "text": "Sí, algunos son los dos"},
                    {"id": "always", "text": "Todos los reales son los dos"},
                ],
                "expected": "never",
                "misconception_by_option": {
                    "sometimes": "no_distingue_exclusion",
                    "always": "no_distingue_exclusion",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · Consolidación",
        "title": "El padrón de la polis",
        "body": (
            "El escribano del padrón tiene que anotar a cada ciudadano en los registros "
            "que le corresponden. Llega Nicómaco: es alfarero, es vecino del barrio "
            "alto, es padre de familia y es miembro del coro.\n\n"
            "El escribano lo anota en el registro de alfareros y cierra el rollo. "
            "Cuando el coro pide su lista para el festival, Nicómaco no aparece."
        ),
        "question": (
            "¿En cuántos registros tenía que estar Nicómaco? Piénsalo, porque con los "
            "números pasa lo mismo."
        ),
        "image": "/leccion/01-prealg-n1-agora/b11-clasificador-ii-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "En uno: el más importante"},
                {"id": "b", "text": "En todos los que le apliquen a la vez"},
                {"id": "c", "text": "En uno, pero con una nota que remita a los demás"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber por qué "
                "con los conjuntos numéricos solo una de las tres funciona."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos números y sus listas de pertenencia",
        "body": (
            "Abajo hay dos números. Para cada uno pregúntate las cinco veces: ¿está en "
            "ℕ? ¿en ℤ? ¿en ℚ? ¿en 𝕀? ¿en ℝ? Fíjate en cuántas veces la respuesta es sí."
        ),
        "cases": [
            {
                "label": "El que está en cuatro",
                "context": "El número 8",
                "fraction": r"8",
                "division": r"8\in\mathbb{N},\ \mathbb{Z},\ \mathbb{Q},\ \mathbb{R}",
                "note": (
                    "Entra en ℕ y, por la cadena de inclusión, entra automáticamente en "
                    "todos los de arriba. Solo se queda fuera de 𝕀."
                ),
            },
            {
                "label": "El que está en dos",
                "context": r"El número $\sqrt{2}$",
                "fraction": r"\sqrt{2}",
                "division": r"\sqrt{2}\in\mathbb{I},\ \mathbb{R}",
                "note": (
                    "No es fracción, así que se queda fuera de ℕ, ℤ y ℚ. Entra solo en "
                    "𝕀 — y en ℝ, porque ℝ es la unión de ℚ con 𝕀."
                ),
            },
        ],
        "resolution": (
            "La regla es corta: **encuentra el peldaño más bajo y márcalo hacia arriba**. "
            "Como ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ, entrar en uno te mete en todos los siguientes sin "
            "esfuerzo. La única excepción es 𝕀, que no está en la cadena: o eres "
            "racional o eres irracional, nunca los dos."
        ),
    },
    "definition_title": "Pertenencia múltiple",
    "definition_katex": r"x\in\mathbb{N}\ \Rightarrow\ x\in\mathbb{Z}\ \Rightarrow\ x\in\mathbb{Q}\ \Rightarrow\ x\in\mathbb{R}\qquad \mathbb{Q}\cap\mathbb{I}=\varnothing",
    "definition": (
        "La frase del nodo: pertenecer a un conjunto no te saca de ningún otro. Solo ℚ y "
        "𝕀 se excluyen entre sí, y por eso ℝ es la unión de los dos."
    ),
    "definition_symbols": [
        {
            "symbol": r"\Rightarrow",
            "reads": "implica",
            "means": "si lo de la izquierda es cierto, lo de la derecha también",
        },
        {
            "symbol": r"\cap",
            "reads": "intersección",
            "means": "lo que está en los dos conjuntos a la vez",
        },
        {
            "symbol": r"\varnothing",
            "reads": "conjunto vacío",
            "means": "no hay ni un solo elemento: ℚ y 𝕀 no comparten nada",
        },
        {
            "symbol": r"\mathbb{Q}\cup\mathbb{I}=\mathbb{R}",
            "reads": "ℚ unión 𝕀 es ℝ",
            "means": "juntos, y sin repetir a nadie, forman la recta",
        },
        {
            "symbol": r"x\in\mathbb{Z},\ x\notin\mathbb{N}",
            "reads": "entero pero no natural",
            "means": "solo los negativos: −4, −17…",
        },
        {
            "symbol": r"x\in\mathbb{Q},\ x\notin\mathbb{Z}",
            "reads": "racional pero no entero",
            "means": "las fracciones con parte decimal: 1/2, −2,75…",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Marcar hacia arriba",
            "title": "El registro del número −6",
            "statement": r"Lista TODOS los conjuntos entre $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ a los que pertenece $-6$.",
            "latex": r"-6",
            "image_slot": False,
            "steps": [
                "¿Está en ℕ? No: es negativo y los naturales empiezan en 0.",
                "¿Está en ℤ? Sí: es un número sin partes, del lado izquierdo del 0.",
                "Encontré el peldaño más bajo. Ahora marco hacia arriba sin volver a pensar.",
                "ℤ ⊂ ℚ ⊂ ℝ, así que −6 está también en ℚ y en ℝ.",
                "¿Está en 𝕀? No: es racional, y ℚ e 𝕀 no comparten elementos. Total: tres conjuntos.",
            ],
            "solution": r"$-6\in\mathbb{Z},\ \mathbb{Q},\ \mathbb{R}$ · $\notin\mathbb{N},\ \notin\mathbb{I}$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 2,
                "prompt": (
                    "En el paso 3 dejé de revisar conjunto por conjunto y marqué todos los "
                    "de arriba de golpe. ¿Qué me da derecho a hacer eso?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El que rompe la cadena",
            "title": "El registro del número π",
            "statement": r"Lista TODOS los conjuntos a los que pertenece $\pi$.",
            "latex": r"\pi",
            "image_slot": False,
            "steps": [
                "¿Está en ℕ? No. ¿En ℤ? No: no es un número sin partes.",
                "¿Está en ℚ? No: no se puede escribir como fracción de enteros.",
                "Aquí la cadena no me sirve: no encontré ningún peldaño donde entrara.",
                "¿Está en 𝕀? Sí, justamente por no ser fracción. Ese es su único conjunto propio.",
                "¿Está en ℝ? Sí: ℝ = ℚ ∪ 𝕀, y π está en 𝕀. Total: dos conjuntos.",
            ],
            "solution": r"$\pi\in\mathbb{I},\ \mathbb{R}$ · $\notin\mathbb{N},\ \notin\mathbb{Z},\ \notin\mathbb{Q}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El número al que le dieron un solo registro",
            "statement": (
                "Un discípulo llenó el padrón así. Está mal: «5 es natural, así que no es "
                "entero ni racional. −3 es entero, así que no es racional. Cada número "
                "tiene un conjunto, igual que cada persona tiene un oficio»."
            ),
            "latex": r"5\in\mathbb{N}\ \Rightarrow\ 5\notin\mathbb{Z}",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"5\in\mathbb{N}\ \Rightarrow\ 5\ \underline{\notin}\ \mathbb{Z}",
            "error_note": (
                "Aquí se cayó. Leyó los conjuntos como casillas excluyentes —donde estar "
                "en una te saca de las demás— en vez de como cajas anidadas."
            ),
            "correct_version": {
                "wrong_latex": r"5\in\mathbb{N}\ \Rightarrow\ 5\notin\mathbb{Z},\ \mathbb{Q}",
                "right_latex": r"5\in\mathbb{N}\ \Rightarrow\ 5\in\mathbb{Z},\ \mathbb{Q},\ \mathbb{R}",
                "rows": [
                    {
                        "wrong": "Cada número tiene un conjunto, como cada persona un oficio",
                        "right": "Cada número está en todos los que lo contienen, como Nicómaco en todos sus registros",
                    },
                    {
                        "wrong": "Ser natural impide ser entero",
                        "right": "Ser natural GARANTIZA ser entero: ℕ ⊂ ℤ",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué 5 está en cuatro conjuntos y no en uno? Escribe la lista completa."
            ),
            "steps": [
                "Escribe 5 como fracción: 5/1. ¿Eso lo hace racional?",
                "Sí. Y sigue siendo natural: escribirlo distinto no lo cambia.",
                "Ahora aplica lo mismo a −3: ¿se puede escribir −3/1?",
            ],
            "solution": (
                "La única exclusión real en todo el mapa es entre ℚ e 𝕀. Todo lo demás se "
                "acumula: 5 es natural Y entero Y racional Y real, las cuatro cosas al "
                "mismo tiempo. El padrón de Nicómaco tenía que llevarlo en cuatro rollos."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el registro ya está empezado y "
            "solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"¿A cuántos de los cinco conjuntos $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ pertenece $-15$?",
                "given_steps": [
                    r"-15\notin\mathbb{N}\ (\text{es negativo})",
                    r"-15\in\mathbb{Z}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Total de conjuntos}=", "answer": "3"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"¿A cuántos pertenece $\dfrac{3}{8}$? ¿Y $\sqrt{7}$?",
                "given_steps": [
                    r"\dfrac{3}{8}=0{,}375\ \Rightarrow\ \text{racional no entero}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{Conjuntos de }\tfrac{3}{8}=", "answer": "2"},
                    {"id": "P2-b2", "label": r"\text{Conjuntos de }\sqrt{7}=", "answer": "2"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: ¿a cuántos de los cinco conjuntos pertenece el "
                    "número 0? Cuidado con los dos casos límite del curso."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Total de conjuntos}=", "answer": "4"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos formas de llenar el registro",
        "intro": r"¿A qué conjuntos pertenece $-2$? Las dos soluciones son correctas.",
        "methods": [
            {
                "label": "Método 1 · Revisar uno por uno",
                "steps": [
                    r"\mathbb{N}?\ \text{no}",
                    r"\mathbb{Z}?\ \text{sí}\quad\mathbb{Q}?\ \text{sí}",
                    r"\mathbb{I}?\ \text{no}\quad\mathbb{R}?\ \text{sí}",
                ],
                "note": "Cinco preguntas, cinco respuestas. Nunca falla.",
            },
            {
                "label": "Método 2 · Peldaño más bajo y hacia arriba",
                "steps": [
                    r"\text{más bajo}=\mathbb{Z}",
                    r"\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
                    r"\Rightarrow\ \mathbb{Z},\mathbb{Q},\mathbb{R}",
                ],
                "note": "Una pregunta y la cadena hace el resto.",
            },
        ],
        "question": (
            r"¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si aplicas el "
            r"método 2 a $\sqrt{3}$?"
        ),
        "insight": (
            "Con √3 el método 2 se queda mudo: no hay peldaño de la cadena donde entre, "
            "así que no hay desde dónde marcar hacia arriba. Ese silencio ES la respuesta "
            "— significa irracional. Los irracionales no están en la cadena, y por eso "
            "necesitan que les preguntes aparte."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿A cuántos de los cinco conjuntos $\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{I},\mathbb{R}$ pertenece el número 21?",
            "expr": r"21",
            "answer": "4",
            "hints": {
                "n1": "Busca el peldaño más bajo donde entra.",
                "n2": "21 cuenta objetos completos: entra en ℕ.",
                "n3": "Desde ℕ marca hacia arriba: ℕ, ℤ, ℚ, ℝ. En 𝕀 no.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿A cuántos de los cinco pertenece $\dfrac{5}{2}$?",
            "expr": r"\dfrac{5}{2}",
            "answer": "2",
            "hints": {
                "n1": "Resuelve primero: 5 ÷ 2 = 2,5.",
                "n2": "2,5 no cuenta objetos completos ni es entero.",
                "n3": "Entra recién en ℚ, y de ahí a ℝ: dos conjuntos.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estos números pertenece a EXACTAMENTE dos de los cinco conjuntos?",
            "options": [
                {"id": "sqrt11", "text": "√11", "latex": r"\sqrt{11}"},
                {"id": "twelve", "text": "12", "latex": r"12"},
                {"id": "neg9", "text": "−9", "latex": r"-9"},
                {"id": "zero", "text": "0", "latex": r"0"},
            ],
            "expected": "sqrt11",
            "feedback_by_option": {
                "sqrt11": "correct",
                "twelve": "fb_b11_e3_natural",
                "neg9": "fb_b11_e3_integer",
                "zero": "fb_b11_e3_natural",
            },
            "misconception_by_option": {
                "twelve": "pertenencia_unica",
                "neg9": "cuenta_mal_la_cadena",
                "zero": "cero_no_es_natural",
            },
            "hints": {
                "n1": "Cuenta para cada uno: ¿en cuántos entra?",
                "n2": "12 y 0 entran en cuatro; −9 entra en tres.",
                "n3": "√11 no es fracción: solo 𝕀 y ℝ. Son dos.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un discípulo escribió: «−4 pertenece a ℤ y a ℝ, pero no a ℚ, porque no "
                "está escrito como fracción». ¿Dónde está el error?"
            ),
            "options": [
                {"id": "as_fraction", "text": "−4 sí es racional: se escribe −4/1"},
                {"id": "not_real", "text": "El error es otro: −4 tampoco es real"},
                {"id": "not_integer", "text": "El error es que −4 no es entero"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "as_fraction",
            "feedback_by_option": {
                "as_fraction": "correct",
                "not_real": "fb_b11_e4_real",
                "not_integer": "fb_b11_e4_integer",
                "none": "fb_b11_e4_none",
            },
            "misconception_by_option": {
                "not_real": "negativo_no_es_real",
                "not_integer": "negativo_no_es_entero",
                "none": "clasifica_por_apariencia",
            },
            "hints": {
                "n1": "Ser racional no exige estar ESCRITO como fracción: exige poder serlo.",
                "n2": "¿Puedes escribir −4 con barra sin cambiar su valor?",
                "n3": "−4 = −4/1, fracción de enteros. Es racional.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Como $7$ es natural, entonces $7\notin\mathbb{Z}$.»",
            "options": [
                {"id": "false_both", "text": "Falsa: 7 es natural Y entero, porque ℕ ⊂ ℤ"},
                {"id": "true_one", "text": "Verdadera: un número está en un solo conjunto"},
                {"id": "false_notnatural", "text": "Falsa: 7 no es natural, es entero"},
                {"id": "depends", "text": "Depende de si lo escribes con signo o sin signo"},
            ],
            "expected": "false_both",
            "feedback_by_option": {
                "false_both": "correct",
                "true_one": "fb_b11_e5_trap",
                "false_notnatural": "fb_b11_e5_notnatural",
                "depends": "fb_b11_e5_depends",
            },
            "misconception_by_option": {
                "true_one": "pertenencia_unica",
                "false_notnatural": "pertenencia_unica",
                "depends": "representacion_define_el_numero",
            },
            "hints": {
                "n1": "Lee qué significa ℕ ⊂ ℤ.",
                "n2": "Significa que todo natural es también entero.",
                "n3": "7 está en los dos, y además en ℚ y ℝ.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El escribano quiere una regla para llenar el padrón sin revisar los cinco "
                "registros cada vez. ¿Cuál le sirve?"
            ),
            "options": [
                {
                    "id": "lowest",
                    "text": "Hallar el conjunto más bajo y marcar todos los de arriba; preguntar por 𝕀 solo si no entró en ninguno",
                },
                {"id": "one_each", "text": "Un número, un registro: el que mejor lo describa"},
                {"id": "all_five", "text": "Marcar los cinco siempre: así nunca falta ninguno"},
                {"id": "biggest", "text": "Marcar solo ℝ: contiene a todos"},
            ],
            "expected": "lowest",
            "feedback_by_option": {
                "lowest": "correct",
                "one_each": "fb_b11_e6_one",
                "all_five": "fb_b11_e6_all",
                "biggest": "fb_b11_e6_biggest",
            },
            "misconception_by_option": {
                "one_each": "pertenencia_unica",
                "all_five": "no_distingue_exclusion",
                "biggest": "pierde_informacion",
            },
            "hints": {
                "n1": "Vuelve a Nicómaco: ¿un registro o todos los que le aplican?",
                "n2": "Todos los que le apliquen — pero sin marcar los que no.",
                "n3": "ℚ e 𝕀 se excluyen, así que marcar los cinco siempre es falso.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estas afirmaciones es FALSA?",
            "options": [
                {"id": "false_one", "text": "Un número puede ser racional e irracional a la vez"},
                {"id": "true_nat", "text": "Todo natural es real"},
                {"id": "true_int", "text": "Todo entero es racional"},
                {"id": "true_irr", "text": "Todo irracional es real"},
            ],
            "expected": "false_one",
            "feedback_by_option": {
                "false_one": "correct",
                "true_nat": "fb_b11_e7_true",
                "true_int": "fb_b11_e7_true",
                "true_irr": "fb_b11_e7_true",
            },
            "misconception_by_option": {
                "true_nat": "no_reconoce_inclusion",
                "true_int": "no_reconoce_inclusion",
                "true_irr": "no_reconoce_inclusion",
            },
            "hints": {
                "n1": "Tres de las cuatro son inclusiones que ya usaste en el nodo.",
                "n2": "ℕ ⊂ ℝ, ℤ ⊂ ℚ e 𝕀 ⊂ ℝ son las tres verdaderas.",
                "n3": "Irracional significa «no racional»: no se puede ser los dos.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "El padrón completo",
        "title": "Cuántos registros le tocan a cada número",
        "intro": "Cada fila cuenta en cuántos de los cinco conjuntos entra el número.",
        "rows": [
            {
                "symbol": r"7",
                "name": "Natural",
                "closed": "yes",
                "latex": r"\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{R}",
                "note": "Cuatro. Entra en el más bajo y sube toda la cadena.",
            },
            {
                "symbol": r"0",
                "name": "Cero",
                "closed": "yes",
                "latex": r"\mathbb{N},\mathbb{Z},\mathbb{Q},\mathbb{R}",
                "note": "Cuatro, igual que 7: en este curso 0 ∈ ℕ.",
            },
            {
                "symbol": r"-6",
                "name": "Entero negativo",
                "closed": "yes",
                "latex": r"\mathbb{Z},\mathbb{Q},\mathbb{R}",
                "note": "Tres. El signo lo deja fuera de ℕ.",
            },
            {
                "symbol": r"\tfrac{3}{4}",
                "name": "Racional no entero",
                "closed": "yes",
                "latex": r"\mathbb{Q},\mathbb{R}",
                "note": "Dos. Entra recién en el tercer peldaño.",
            },
            {
                "symbol": r"\sqrt{2}",
                "name": "Irracional",
                "closed": "no",
                "latex": r"\mathbb{I},\mathbb{R}",
                "note": "Dos, pero por fuera de la cadena: 𝕀 no contiene a nadie.",
            },
        ],
        "outro": (
            "Lee la columna de la derecha de arriba abajo: 4, 4, 3, 2, 2. Cuanto más "
            "arriba entra un número, en menos registros aparece. Y la última fila es la "
            "única que llega por otro camino."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué regla estructural explica todos los casos de este nodo?",
        "thumbnails": [r"7", r"-6", r"\sqrt{2}"],
        "options": [
            {
                "id": "chain",
                "text": "Entrar en un conjunto de la cadena te mete en todos los de arriba",
                "correct": True,
            },
            {
                "id": "exclusive",
                "text": "ℚ e 𝕀 son los únicos dos que se excluyen entre sí",
                "correct": True,
            },
            {
                "id": "one_each",
                "text": "Cada número pertenece a exactamente un conjunto",
                "correct": False,
            },
            {
                "id": "all_five",
                "text": "Todo número real pertenece a los cinco conjuntos",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El escribano tiene cuatro números por registrar: 4 · −11 · 2/5 · √13. "
            "Sumando todos los registros de los cuatro (contando ℕ, ℤ, ℚ, 𝕀 y ℝ), "
            "¿cuántas anotaciones hace en total?"
        ),
        "polya": {
            "comprender": (
                "Me dan cuatro números. Para cada uno debo contar en cuántos de los cinco "
                "conjuntos entra, y después sumar los cuatro conteos."
            ),
            "planear": (
                "Para cada número busco el peldaño más bajo de la cadena y marco hacia "
                "arriba. Si no entra en ninguno, es irracional y va a 𝕀 y ℝ."
            ),
            "ejecutar": (
                "4 → ℕ,ℤ,ℚ,ℝ = 4 · −11 → ℤ,ℚ,ℝ = 3 · 2/5 → ℚ,ℝ = 2 · "
                "√13 → 𝕀,ℝ = 2. Total: 4 + 3 + 2 + 2 = 11."
            ),
            "comprobar": (
                "Los cuatro aparecen en ℝ, así que ese registro debe tener 4 anotaciones. "
                "✓ Y ninguno está en ℚ y en 𝕀 a la vez. ✓"
            ),
        },
        "prompt": "¿Cuántas anotaciones hace en total?",
        "answer": "11",
        "hints": {
            "n1": "Cuenta los conjuntos de cada número por separado y después suma.",
            "n2": "4 entra en cuatro; −11 en tres.",
            "n3": "2/5 y √13 entran en dos cada uno: 4 + 3 + 2 + 2.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico ----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: hoy resolviste más que al entrar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué un "
            "número aparece en varios registros a la vez."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿A cuántos de los cinco conjuntos pertenece el número 30?",
                "answer": "4",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si un número es natural, ¿puede ser real al mismo tiempo?",
                "options": [
                    {"id": "yes", "text": "Sí: ℕ ⊂ ℝ"},
                    {"id": "no", "text": "No: o es natural o es real"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "pertenencia_unica"},
            },
            {
                "id": "PD3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿A cuántos de los cinco conjuntos pertenece $\sqrt{5}$?",
                "answer": "2",
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
        "fb_b11_e3_natural": (
            "Ese entra en cuatro, no en dos: es natural, y la cadena lo sube hasta ℝ. → "
            "Busca el que no entra en ningún peldaño de la cadena."
        ),
        "fb_b11_e3_integer": (
            "−9 entra en tres: ℤ, ℚ y ℝ. Le falta ℕ por ser negativo, pero sigue siendo "
            "más de dos. → Busca el que solo llega a 𝕀 y ℝ."
        ),
        "fb_b11_e4_real": (
            "−4 sí es real: está en la recta. El error del discípulo es sobre ℚ, no sobre "
            "ℝ. → Di si −4 se puede escribir como fracción."
        ),
        "fb_b11_e4_integer": (
            "−4 sí es entero: es un número sin partes. El error está en lo que dijo de ℚ. "
            "→ Escribe −4 con barra de fracción."
        ),
        "fb_b11_e4_none": (
            "Hay un error: dijo que −4 no es racional. Pero −4 = −4/1 es fracción de "
            "enteros. → Escribe esa fracción."
        ),
        "fb_b11_e5_trap": (
            "Ese es justo el error del nodo: los conjuntos no son casillas excluyentes. "
            "ℕ ⊂ ℤ significa que todo natural TAMBIÉN es entero. → Lista los conjuntos del 7."
        ),
        "fb_b11_e5_notnatural": (
            "7 sí es natural: cuenta objetos completos. Y además es entero. Las dos cosas. "
            "→ Di en cuántos conjuntos está."
        ),
        "fb_b11_e5_depends": (
            "Escribir +7 o 7 no cambia el número ni sus conjuntos. → Revisa qué significa ⊂."
        ),
        "fb_b11_e6_one": (
            "Es el error de Nicómaco: un solo registro y quedó fuera del coro. → Busca la "
            "regla que marca todos los que aplican."
        ),
        "fb_b11_e6_all": (
            "Marcar los cinco siempre es falso: ningún número está en ℚ y en 𝕀 a la vez. "
            "→ Busca la regla que respeta esa exclusión."
        ),
        "fb_b11_e6_biggest": (
            "Cierto que ℝ contiene a todos, pero entonces el padrón no distingue nada: "
            "√2 y 7 quedarían iguales. → Busca la regla que sí informa."
        ),
        "fb_b11_e7_true": (
            "Esa es verdadera: es una de las inclusiones del mapa. → Busca la que afirma "
            "que un número puede estar en dos conjuntos que se excluyen."
        ),
    },
    "closing": (
        "Nicómaco iba en cuatro rollos, no en uno. Un número está en todos los conjuntos "
        "que lo contienen, y solo ℚ e 𝕀 se niegan a compartir. En el siguiente nodo vas a "
        "usar esto para cazar afirmaciones falsas."
    ),
    "validation_status": "F1_B11_11bloques",
}
