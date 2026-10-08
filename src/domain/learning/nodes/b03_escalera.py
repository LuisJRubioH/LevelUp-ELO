"""B03 · La escalera de la necesidad — cada conjunto amplía, no reemplaza.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «cuando aparece un conjunto nuevo, el anterior deja de valer».
"""

NODE_ID = "PREALG-N1-B03-ESCALERA-NECESIDAD"
CONCEPT_SLUG = "escalera"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "escalera",
    "misconception": "conjuntos_se_reemplazan",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Antes de subir · El mapa del camino",
    "finish_label": "Empezar por los naturales",
    "title": "Cada peldaño amplía; ninguno borra al anterior",
    "intro": (
        "Vas a recorrer cinco conjuntos de números. Antes de subir el primero conviene "
        "entender cómo está armada la escalera, porque la forma en que la mayoría se la "
        "imagina está equivocada y esa idea equivocada estorba durante todo el camino."
    ),
    # --- Escalera interactiva (bloque propio de este nodo) -------------------
    "staircase": {
        "image": "/leccion/00-comunes/escalera-conjuntos.png",
        "aria": "Escalera de los conjuntos numéricos: naturales, enteros, racionales, irracionales y reales",
        "chain": r"\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
        "steps": [
            {
                "name": "Naturales",
                "symbol": r"\mathbb{N}",
                "question": "¿Cuántos hay?",
                "explanation": (
                    "El primer peldaño sirve para contar cantidades completas, y el 0 cuenta "
                    "el montón vacío. Aquí se puede sumar y multiplicar sin salirse nunca."
                ),
            },
            {
                "name": "Enteros",
                "symbol": r"\mathbb{Z}",
                "question": "¿Y si quito más de lo que hay?",
                "explanation": (
                    "3 − 5 no tiene respuesta contando. Los enteros agregan el lado izquierdo "
                    "del 0 para que toda resta tenga resultado. Los naturales siguen ahí, "
                    "intactos, del lado derecho."
                ),
            },
            {
                "name": "Racionales",
                "symbol": r"\mathbb{Q}",
                "question": "¿Y si reparto una unidad?",
                "explanation": (
                    "3 ÷ 4 cae entre 0 y 1, donde no hay enteros. Los racionales agregan todas "
                    "las fracciones para que la división (salvo entre 0) siempre cierre."
                ),
            },
            {
                "name": "Irracionales",
                "symbol": r"\mathbb{R}\setminus\mathbb{Q}",
                "question": "¿Y si la medida no es ninguna fracción?",
                "explanation": (
                    "La diagonal de un cuadrado de lado 1 se puede dibujar pero no se puede "
                    "escribir como fracción. Estos números no reemplazan a nadie: rellenan "
                    "los huecos que las fracciones dejaban en la recta."
                ),
            },
            {
                "name": "Reales",
                "symbol": r"\mathbb{R}",
                "question": "¿Qué queda cuando se juntan todos?",
                "explanation": (
                    "Racionales e irracionales juntos llenan la recta sin dejar un solo hueco. "
                    "Ese es el último peldaño del camino principal."
                ),
            },
        ],
    },
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
                "prompt": "Cuando aparecen los números negativos, ¿qué pasa con los naturales?",
                "options": [
                    {"id": "stay", "text": "Siguen existiendo: el conjunto nuevo los incluye"},
                    {"id": "replaced", "text": "Se reemplazan: ahora se usan los negativos"},
                    {"id": "separate", "text": "Quedan aparte: son dos mundos que no se tocan"},
                ],
                "expected": "stay",
                "misconception_by_option": {
                    "replaced": "conjuntos_se_reemplazan",
                    "separate": "conjuntos_son_disjuntos",
                },
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Por qué crees que se inventaron números nuevos a lo largo de la historia?",
                "options": [
                    {"id": "need", "text": "Porque había cuentas sin respuesta"},
                    {"id": "bigger", "text": "Porque hacían falta números más grandes"},
                    {"id": "harder", "text": "Para hacer las matemáticas más difíciles"},
                ],
                "expected": "need",
                "misconception_by_option": {
                    "bigger": "amplia_es_agrandar",
                    "harder": "matematica_arbitraria",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"El número $5$, ¿en cuántos de estos conjuntos está? $\mathbb{N}$, $\mathbb{Z}$, $\mathbb{Q}$, $\mathbb{R}$",
                "options": [
                    {"id": "four", "text": "En los cuatro"},
                    {"id": "one", "text": "Solo en ℕ: es un natural"},
                    {"id": "two", "text": "En ℕ y ℤ nada más"},
                ],
                "expected": "four",
                "misconception_by_option": {
                    "one": "pertenencia_unica",
                    "two": "pertenencia_unica",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · Antes de subir",
        "title": "El taller del carpintero",
        "body": (
            "El carpintero del ágora empezó con un cincel. Con el cincel podía hacer casi "
            "todo, hasta que le encargaron una junta que el cincel no lograba. Entonces "
            "consiguió una gubia.\n\n"
            "Después vino un encargo que la gubia tampoco resolvía, y consiguió un "
            "berbiquí. Y así, herramienta tras herramienta, hasta llenar la pared del "
            "taller. Hoy tiene once herramientas colgadas."
        ),
        "question": (
            "Cuando el carpintero consiguió la gubia, ¿qué hizo con el cincel? Piensa la "
            "respuesta, porque con los números pasa exactamente lo mismo."
        ),
        "image": "/leccion/01-prealg-n1-agora/b03-escalera-necesidad-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "Lo botó: ya tenía una herramienta mejor"},
                {"id": "b", "text": "Lo dejó colgado: sigue sirviendo para lo suyo"},
                {"id": "c", "text": "Lo guardó por si acaso, pero ya no lo usa"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber cuál de las "
                "tres describe lo que pasa con los conjuntos de números."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos cuentas que obligaron a construir un peldaño",
        "body": (
            "Ningún conjunto nuevo apareció porque a alguien se le ocurrió. Cada uno "
            "apareció porque había una cuenta concreta sin respuesta. Mira las dos que "
            "abrieron los dos primeros peldaños."
        ),
        "cases": [
            {
                "label": "La cuenta que abrió ℤ",
                "context": "Prestó 5 cinceles y solo tenía 3",
                "fraction": r"3-5",
                "division": r"3-5\notin\mathbb{N}",
                "note": (
                    "Contando no hay respuesta. Aparece el lado izquierdo del 0 — y los "
                    "naturales no se van: quedan adentro del conjunto nuevo."
                ),
            },
            {
                "label": "La cuenta que abrió ℚ",
                "context": "Tres panes para cuatro personas",
                "fraction": r"3\div4",
                "division": r"3\div4\notin\mathbb{Z}",
                "note": (
                    "Con enteros no hay respuesta: cae entre 0 y 1. Aparecen las fracciones "
                    "— y los enteros tampoco se van."
                ),
            },
        ],
        "resolution": (
            "El patrón es siempre el mismo: una operación se sale del conjunto, y el "
            "conjunto siguiente se construye para que quepa. Nunca se borra lo anterior. "
            "Por eso la escalera se dibuja como cajas una dentro de otra, no como escalones "
            "separados."
        ),
    },
    "definition_title": "La cadena de inclusión",
    "definition_katex": r"\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
    "definition": (
        "La frase del nodo: cada conjunto CONTIENE al anterior. Subir un peldaño es ganar "
        "números, nunca perderlos."
    ),
    "definition_symbols": [
        {
            "symbol": r"\subset",
            "reads": "está contenido en",
            "means": "todo lo del primero está también en el segundo",
        },
        {
            "symbol": r"\mathbb{N}\subset\mathbb{Z}",
            "reads": "ℕ dentro de ℤ",
            "means": "todo natural es también entero; 5 no dejó de ser natural",
        },
        {"symbol": r"\in", "reads": "pertenece a", "means": "relaciona UN número con UN conjunto"},
        {
            "symbol": r"\notin",
            "reads": "no pertenece a",
            "means": "el número se sale de ese conjunto: ahí nace el siguiente",
        },
        {
            "symbol": r"\mathbb{R}\setminus\mathbb{Q}",
            "reads": "los irracionales",
            "means": "el único que NO contiene a los anteriores: rellena, no envuelve",
        },
        {
            "symbol": r"\cup",
            "reads": "unión",
            "means": "ℝ = ℚ ∪ 𝕀: los reales son las fracciones más lo que las fracciones no alcanzan",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Un número en varios peldaños",
            "title": "Dónde vive el 7",
            "statement": "¿A cuáles de los conjuntos ℕ, ℤ, ℚ y ℝ pertenece el número 7?",
            "latex": r"7\in\ ?",
            "image_slot": False,
            "steps": [
                "¿Sirve para contar cantidades completas? Sí → 7 ∈ ℕ.",
                "¿Está en la recta de los enteros? Sí, a la derecha del 0 → 7 ∈ ℤ.",
                "¿Se puede escribir como fracción de enteros? Sí: 7/1 → 7 ∈ ℚ.",
                "¿Está en la recta completa? Sí → 7 ∈ ℝ.",
                "7 pertenece a los cuatro. No cambió de conjunto: cada conjunto nuevo lo recibió.",
            ],
            "solution": r"$7\in\mathbb{N},\ 7\in\mathbb{Z},\ 7\in\mathbb{Q},\ 7\in\mathbb{R}$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 2,
                "prompt": (
                    "En el paso 3 escribí 7 como 7/1 para probar que es racional. "
                    "¿Por qué ese truco funciona con CUALQUIER entero?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Un número que solo cabe arriba",
            "title": "Dónde vive −3/4",
            "statement": "¿A cuáles de los conjuntos ℕ, ℤ, ℚ y ℝ pertenece el número −3/4?",
            "latex": r"-\dfrac{3}{4}\in\ ?",
            "image_slot": False,
            "steps": [
                "¿Cuenta cantidades completas? No: es negativo y además es una parte → −3/4 ∉ ℕ.",
                "¿Es entero? No: cae entre −1 y 0 → −3/4 ∉ ℤ.",
                "¿Es fracción de enteros? Sí: −3 sobre 4 → −3/4 ∈ ℚ.",
                "¿Está en la recta completa? Sí → −3/4 ∈ ℝ.",
                "Entra recién en el tercer peldaño. Los conjuntos de abajo se le quedaron cortos, no al revés.",
            ],
            "solution": r"$-\dfrac{3}{4}\in\mathbb{Q}$ y $\in\mathbb{R}$, pero $\notin\mathbb{N}$, $\notin\mathbb{Z}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El número al que le quitaron su casa",
            "statement": (
                "Un discípulo resumió el nodo así. Está mal: «Cuando llegamos a los "
                "racionales, el 5 dejó de ser natural y pasó a ser racional. Un número "
                "está en el peldaño al que llegó, no en los de abajo»."
            ),
            "latex": r"5\in\mathbb{Q}\ \Rightarrow\ 5\notin\mathbb{N}",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"5\in\mathbb{Q}\ \Rightarrow\ 5\ \underline{\notin}\ \mathbb{N}",
            "error_note": (
                "Aquí se cayó. Leyó la escalera como escalones separados —donde estar en "
                "uno impide estar en otro— en vez de como cajas una dentro de otra."
            ),
            "correct_version": {
                "wrong_latex": r"5\in\mathbb{Q}\ \Rightarrow\ 5\notin\mathbb{N}",
                "right_latex": r"5\in\mathbb{N}\ \Rightarrow\ 5\in\mathbb{Z},\ \mathbb{Q},\ \mathbb{R}",
                "rows": [
                    {
                        "wrong": "Un número vive en un solo conjunto",
                        "right": "Un número vive en todos los que lo contienen",
                    },
                    {
                        "wrong": "Subir de peldaño es mudarse",
                        "right": "Subir de peldaño es que lleguen vecinos nuevos",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué 5 sigue siendo natural aunque también sea racional? Escribe a "
                "qué conjuntos pertenece."
            ),
            "steps": [
                "Vuelve a la definición: ℕ ⊂ ℤ significa que TODO natural está en ℤ.",
                "Contener no es reemplazar: la caja grande no vacía a la pequeña.",
                "Comprueba con el carpintero: ¿la gubia hizo desaparecer el cincel?",
            ],
            "solution": (
                "El símbolo ⊂ dice exactamente esto: lo de adentro sigue adentro. 5 es "
                "natural Y entero Y racional Y real, las cuatro cosas a la vez y para "
                "siempre. Es la misma idea que el cincel colgado en la pared: nunca dejó "
                "de servir para lo suyo."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el análisis ya está empezado y "
            "solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "¿En cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ está el número 12?",
                "given_steps": [
                    r"12\ \text{cuenta objetos completos}\Rightarrow 12\in\mathbb{N}",
                    r"\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Número de conjuntos}=", "answer": "4"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "¿En cuántos de los cuatro está el número −6? ¿Y el número 1/2?",
                "given_steps": [
                    r"-6\ \text{es negativo}\Rightarrow -6\notin\mathbb{N}",
                ],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"\text{Conjuntos que contienen a }-6=",
                        "answer": "3",
                    },
                    {
                        "id": "P2-b2",
                        "label": r"\text{Conjuntos que contienen a }\tfrac{1}{2}=",
                        "answer": "2",
                    },
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: √2 no es fracción de enteros. ¿En cuántos de "
                    "los cuatro conjuntos ℕ, ℤ, ℚ, ℝ está?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Número de conjuntos}=", "answer": "1"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos formas de dibujar la escalera",
        "intro": (
            "Las dos imágenes de abajo representan lo mismo. Una se presta a confusión y "
            "la otra no."
        ),
        "methods": [
            {
                "label": "Dibujo 1 · Escalones",
                "steps": [
                    r"\mathbb{N}\ \to\ \mathbb{Z}\ \to\ \mathbb{Q}\ \to\ \mathbb{R}",
                    r"\text{uno tras otro}",
                ],
                "note": "Muestra bien el ORDEN histórico y la necesidad que abrió cada peldaño.",
            },
            {
                "label": "Dibujo 2 · Cajas anidadas",
                "steps": [
                    r"\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
                    r"\text{una dentro de otra}",
                ],
                "note": "Muestra bien que nada se pierde: lo de adentro sigue adentro.",
            },
        ],
        "question": (
            "¿Cuál conviene para explicar POR QUÉ nacieron los negativos? ¿Y cuál para "
            "explicar que 5 sigue siendo natural?"
        ),
        "insight": (
            "Ninguno de los dos alcanza solo, y ahí está el contenido: el de escalones "
            "cuenta la historia pero sugiere que uno reemplaza al otro; el de cajas cuenta "
            "la estructura pero esconde la necesidad. La escalera de arriba usa los dos a "
            "la vez a propósito. Y ojo: los irracionales no encajan en ninguno de los dos "
            "limpiamente — no contienen a nadie, rellenan huecos."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿A cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ pertenece el número 0?",
            "expr": r"0",
            "answer": "4",
            "hints": {
                "n1": "En este curso, ¿el 0 es natural?",
                "n2": "Sí lo es. Y si está en ℕ, la cadena de inclusión hace el resto.",
                "n3": "ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ: si está en el primero, está en los cuatro.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿A cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ pertenece el número −8?",
            "expr": r"-8",
            "answer": "3",
            "hints": {
                "n1": "¿Se puede contar −8 objetos?",
                "n2": "No: los naturales no llegan por debajo del 0.",
                "n3": "Entra desde ℤ, y de ahí para arriba: ℤ, ℚ y ℝ.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas afirmaciones sobre la escalera es correcta?",
            "options": [
                {"id": "ok", "text": "Todo entero es racional, pero no todo racional es entero"},
                {
                    "id": "reverse",
                    "text": "Todo racional es entero, pero no todo entero es racional",
                },
                {"id": "both", "text": "Todo entero es racional y todo racional es entero"},
                {"id": "neither", "text": "Los enteros y los racionales no se tocan"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "reverse": "fb_b03_e3_reverse",
                "both": "fb_b03_e3_both",
                "neither": "fb_b03_e3_neither",
            },
            "misconception_by_option": {
                "reverse": "error_del_reciproco",
                "both": "conjuntos_son_iguales",
                "neither": "conjuntos_son_disjuntos",
            },
            "hints": {
                "n1": "Piensa en 1/2: ¿es racional? ¿es entero?",
                "n2": "Es racional pero no entero, así que ℚ tiene números que ℤ no tiene.",
                "n3": "Y todo entero se escribe n/1, así que ℤ está dentro de ℚ.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un discípulo dibujó la escalera así: «ℕ, después ℤ, después ℚ, después 𝕀, "
                "después ℝ; cada uno dentro del siguiente». ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "irrationals",
                    "text": "𝕀 no contiene a ℚ: los irracionales no envuelven a nadie, rellenan",
                },
                {"id": "order", "text": "El orden está mal: ℤ va antes que ℕ"},
                {"id": "reals", "text": "ℝ no debería ir al final"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "irrationals",
            "feedback_by_option": {
                "irrationals": "correct",
                "order": "fb_b03_e4_order",
                "reals": "fb_b03_e4_reals",
                "none": "fb_b03_e4_none",
            },
            "misconception_by_option": {
                "order": "invierte_la_escalera",
                "reals": "reales_no_son_el_final",
                "none": "irracionales_contienen_racionales",
            },
            "hints": {
                "n1": "¿1/2 es irracional?",
                "n2": "No lo es, así que ℚ no puede estar dentro de 𝕀.",
                "n3": "𝕀 y ℚ no se tocan; ℝ es la unión de los dos.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Como $4$ es real, entonces ya no es natural.»",
            "options": [
                {"id": "false_both", "text": "Falsa: 4 es natural Y real al mismo tiempo"},
                {"id": "true_moved", "text": "Verdadera: subió de peldaño"},
                {"id": "false_notreal", "text": "Falsa: 4 no es real, solo natural"},
                {"id": "depends", "text": "Depende de en qué peldaño estemos trabajando"},
            ],
            "expected": "false_both",
            "feedback_by_option": {
                "false_both": "correct",
                "true_moved": "fb_b03_e5_trap",
                "false_notreal": "fb_b03_e5_notreal",
                "depends": "fb_b03_e5_depends",
            },
            "misconception_by_option": {
                "true_moved": "conjuntos_se_reemplazan",
                "false_notreal": "pertenencia_unica",
                "depends": "pertenencia_depende_del_contexto",
            },
            "hints": {
                "n1": "Lee otra vez qué significa ℕ ⊂ ℝ.",
                "n2": "Significa que todo natural es también real.",
                "n3": "Estar en la caja grande no te saca de la pequeña: 4 es las dos cosas.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "Un maestro de otra escuela dice: «yo no enseño enteros; con los naturales "
                "me alcanza para todo». ¿Qué encargo NO va a poder resolver con su clase?"
            ),
            "options": [
                {"id": "debt", "text": "Anotar cuánto queda debiendo un puesto del mercado"},
                {"id": "count", "text": "Contar cuántas columnas tiene el pórtico"},
                {"id": "add", "text": "Sumar las mercancías de dos puestos"},
                {"id": "compare", "text": "Decir cuál de dos puestos tiene más"},
            ],
            "expected": "debt",
            "feedback_by_option": {
                "debt": "correct",
                "count": "fb_b03_e6_naturals",
                "add": "fb_b03_e6_naturals",
                "compare": "fb_b03_e6_naturals",
            },
            "misconception_by_option": {
                "count": "cree_naturales_insuficientes",
                "add": "cree_naturales_insuficientes",
                "compare": "cree_naturales_insuficientes",
            },
            "hints": {
                "n1": "Tres de los cuatro encargos se resuelven contando.",
                "n2": "Busca el que obliga a bajar por debajo del 0.",
                "n3": "Deber es el hueco que abrió el segundo peldaño.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Qué operación fue la que obligó a construir el peldaño de los racionales?",
            "options": [
                {"id": "division", "text": "La división: 3 ÷ 4 no cabía en los enteros"},
                {"id": "subtraction", "text": "La resta: 3 − 5 no cabía en los naturales"},
                {"id": "root", "text": "La raíz: √2 no cabía en las fracciones"},
                {"id": "sum", "text": "La suma: se salía del conjunto"},
            ],
            "expected": "division",
            "feedback_by_option": {
                "division": "correct",
                "subtraction": "fb_b03_e7_integers",
                "root": "fb_b03_e7_irrationals",
                "sum": "fb_b03_e7_sum",
            },
            "misconception_by_option": {
                "subtraction": "confunde_peldanos",
                "root": "confunde_peldanos",
                "sum": "suma_no_es_cerrada",
            },
            "hints": {
                "n1": "Cada peldaño lleva el nombre de la operación que lo rompió.",
                "n2": "La resta abrió ℤ. ¿Cuál abrió ℚ?",
                "n3": "Repartir 3 entre 4 cae entre 0 y 1: eso es dividir.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "El mapa completo",
        "title": "Qué gana cada peldaño y qué NO pierde",
        "intro": "Léelo de abajo hacia arriba: cada fila agrega, ninguna quita.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "yes",
                "latex": r"0,1,2,3,\ldots",
                "note": "Contar. Se rompe con la resta.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "yes",
                "latex": r"\mathbb{N}\cup\{-1,-2,\ldots\}",
                "note": "Agrega el lado izquierdo. Se rompe con la división.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"\mathbb{Z}\cup\left\{\tfrac{a}{b}\right\}",
                "note": "Agrega las partes. Se rompe con la diagonal del cuadrado.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\mathbb{I}\cap\mathbb{Q}=\varnothing",
                "note": "El raro: no contiene a nadie. Rellena huecos.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\mathbb{R}=\mathbb{Q}\cup\mathbb{I}",
                "note": "La recta completa, sin un solo hueco.",
            },
        ],
        "outro": (
            "Fíjate en la única fila marcada distinto: 𝕀. Todos los demás peldaños "
            "CONTIENEN al anterior; los irracionales no contienen a ninguno. Por eso los "
            "reales no son «el quinto conjunto», son la unión de dos."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué patrón se repite en el nacimiento de cada peldaño?",
        "thumbnails": [r"3-5", r"3\div4", r"\sqrt{2}"],
        "options": [
            {
                "id": "operation",
                "text": "Una operación se salió del conjunto y hubo que ampliarlo",
                "correct": True,
            },
            {
                "id": "keeps",
                "text": "El conjunto nuevo conserva todo lo del anterior",
                "correct": True,
            },
            {
                "id": "bigger_numbers",
                "text": "Cada peldaño usa números más grandes",
                "correct": False,
            },
            {"id": "replace", "text": "Cada peldaño reemplaza al anterior", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Toma estos cinco números: 3 · −2 · 0,25 · √5 · 0. ¿Cuántos de ellos " "pertenecen a ℤ?"
        ),
        "polya": {
            "comprender": (
                "Me dan cinco números mezclados. Me piden cuántos son enteros, o sea "
                "cuántos están en la recta de ℤ (sin partes, con o sin signo)."
            ),
            "planear": (
                "Reviso uno por uno. Cuidado con dos trampas: el 0 SÍ es entero, y un "
                "número con coma o con raíz normalmente no lo es."
            ),
            "ejecutar": (
                "3 ✓ · −2 ✓ (negativo pero sin partes) · 0,25 ✗ (cae entre 0 y 1) · "
                "√5 ✗ (ni siquiera es racional) · 0 ✓. Van 3."
            ),
            "comprobar": (
                "Los tres que conté no tienen parte decimal y sí signo o cero. ✓ Y noto "
                "que los tres también están en ℚ y en ℝ: pertenecer a ℤ no los saca de ahí."
            ),
        },
        "prompt": "¿Cuántos de los cinco pertenecen a ℤ?",
        "answer": "3",
        "hints": {
            "n1": "Un entero es un número sin parte decimal, positivo, negativo o cero.",
            "n2": "El 0 cuenta; 0,25 no.",
            "n3": "√5 no es entero ni racional: queda fuera.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico ----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros casos. Sin nota: solo miramos si algo se movió.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: hoy resolviste más que al entrar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué un "
            "número puede estar en varios conjuntos a la vez."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Cuando aparecen las fracciones, ¿qué pasa con los enteros?",
                "options": [
                    {"id": "stay", "text": "Siguen dentro: ℤ ⊂ ℚ"},
                    {"id": "replaced", "text": "Se reemplazan por fracciones"},
                ],
                "expected": "stay",
                "misconception_by_option": {"replaced": "conjuntos_se_reemplazan"},
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿A cuántos de los cuatro conjuntos ℕ, ℤ, ℚ, ℝ pertenece el número 100?",
                "answer": "4",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Qué operación abrió el peldaño de los enteros?",
                "options": [
                    {"id": "sub", "text": "La resta"},
                    {"id": "div", "text": "La división"},
                    {"id": "root", "text": "La raíz cuadrada"},
                ],
                # Inversa del E7 a propósito: allá se preguntó por ℚ, aquí por ℤ.
                "expected": "sub",
                "misconception_by_option": {
                    "div": "confunde_peldanos",
                    "root": "confunde_peldanos",
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
        "fb_b03_e3_reverse": (
            "Le diste la vuelta a la inclusión. 1/2 es racional y NO es entero, así que "
            "no todo racional es entero. → Di en qué conjunto está 1/2 y en cuál no."
        ),
        "fb_b03_e3_both": (
            "Si fueran iguales, 1/2 tendría que ser entero, y no lo es. → Busca un "
            "racional que no sea entero."
        ),
        "fb_b03_e3_neither": (
            "Sí se tocan: todo entero se escribe n/1, así que ℤ está DENTRO de ℚ. → "
            "Escribe 5 como fracción."
        ),
        "fb_b03_e4_order": (
            "El orden está bien: ℕ nació primero y ℤ lo amplió. El error está más "
            "adelante, en el peldaño de los irracionales. → Pregúntate si 1/2 es irracional."
        ),
        "fb_b03_e4_reals": (
            "ℝ sí va al final del camino principal: es la recta completa. El error está "
            "en el peldaño anterior. → Revisa si ℚ puede estar dentro de 𝕀."
        ),
        "fb_b03_e4_none": (
            "Hay uno: 𝕀 no contiene a ℚ. Los irracionales son justamente los que NO son "
            "fracciones. → Di qué relación tienen ℚ y 𝕀 entre sí."
        ),
        "fb_b03_e5_trap": (
            "Ese es justo el error del nodo: ℕ ⊂ ℝ significa que todo natural TAMBIÉN es "
            "real, no que deje de ser natural. La caja grande no vacía a la pequeña. → "
            "Escribe a qué conjuntos pertenece el 4."
        ),
        "fb_b03_e5_notreal": (
            "4 sí es real: está en la recta. Lo que pasa es que además es natural, entero "
            "y racional. → Di cuántos conjuntos lo contienen."
        ),
        "fb_b03_e5_depends": (
            "La pertenencia no cambia según el tema de la clase: 4 es natural siempre. → "
            "Revisa la definición de ⊂."
        ),
        "fb_b03_e6_naturals": (
            "Eso sí se puede con naturales: contar, sumar y comparar no salen del "
            "conjunto. → Busca el encargo que obliga a bajar del 0."
        ),
        "fb_b03_e7_integers": (
            "La resta es correcta, pero abrió el peldaño ANTERIOR: los enteros. → Di qué "
            "operación se sale de ℤ."
        ),
        "fb_b03_e7_irrationals": (
            "La raíz rompe el peldaño SIGUIENTE: √2 se sale de ℚ, no de ℤ. → Di qué "
            "operación se sale de los enteros."
        ),
        "fb_b03_e7_sum": (
            "La suma nunca se sale: sumar dos naturales da un natural. Por eso no abrió "
            "ningún peldaño. → Busca la operación que sí deja resultados fuera."
        ),
    },
    "closing": (
        "El cincel sigue colgado en la pared. Cada peldaño que subas de aquí en adelante "
        "va a agregar números, y ninguno te va a quitar los que ya tienes."
    ),
    "validation_status": "F1_B03_11bloques",
}
