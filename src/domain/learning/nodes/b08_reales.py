"""B08 · Reales — la recta sin huecos.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «cada número tiene un siguiente» — se traslada la
intuición discreta de ℕ/ℤ a una recta que es densa.
"""

NODE_ID = "PREALG-N1-B08-REALES-RECTA"
CONCEPT_SLUG = "reales"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "reales",
    "misconception": "existe_el_siguiente",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Quinto peldaño · Reales",
    "scene": {
        "image": "/leccion/00-comunes/step-reales.png",
        "step": "reals",
        "aria": "Los reales reúnen racionales e irracionales: son los números de la recta",
    },
    "finish_label": "Terminar los conjuntos numéricos",
    "title": "La recta no tiene huecos",
    "intro": (
        "Tienes las fracciones y tienes los irracionales. Aquí los juntas y descubres "
        "que la recta queda completa: cada punto tiene nombre y cada nombre tiene punto. "
        "Y descubres también algo que contradice todo lo que aprendiste contando: aquí "
        "ningún número tiene un «siguiente»."
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
                "prompt": "¿Qué número viene inmediatamente después del 7 en los ENTEROS?",
                "options": [
                    {"id": "eight", "text": "El 8"},
                    {"id": "none", "text": "Ninguno: siempre hay uno en medio"},
                    {"id": "seven_one", "text": "El 7,1"},
                ],
                # En ℤ sí existe el siguiente. Aquí la respuesta correcta es 8,
                # y esa certeza es justo la que el nodo va a poner en crisis.
                "expected": "eight",
                "misconception_by_option": {
                    "none": "confunde_denso_con_discreto",
                    "seven_one": "mezcla_conjuntos",
                },
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Existe algún número entre 0,4 y 0,5?",
                "options": [
                    {"id": "yes_many", "text": "Sí, y hay infinitos"},
                    {"id": "no", "text": "No: 0,5 va justo después de 0,4"},
                    {"id": "one", "text": "Sí, exactamente uno: 0,45"},
                ],
                "expected": "yes_many",
                "misconception_by_option": {
                    "no": "existe_el_siguiente",
                    "one": "densidad_finita",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dónde vive $\sqrt{2}$?",
                "options": [
                    {"id": "line", "text": "En la recta, entre 1 y 2"},
                    {"id": "nowhere", "text": "En ningún lugar: no se puede ubicar"},
                    {"id": "outside", "text": "Fuera de la recta, porque no es una fracción"},
                ],
                "expected": "line",
                "misconception_by_option": {
                    "nowhere": "irracional_no_existe",
                    "outside": "recta_es_solo_racionales",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · El quinto peldaño",
        "title": "La cuerda del agrimensor",
        "body": (
            "El agrimensor tensa una cuerda de un extremo al otro del muro del gimnasio "
            "y clava una marca en el 0 y otra en el 1. Le pide a un aprendiz que marque "
            "con tinta TODOS los puntos que haya entre las dos.\n\n"
            "El aprendiz marca la mitad. Luego los tercios. Luego los cuartos, los "
            "quintos, los milésimos. Trabaja hasta que se le acaba la tinta y el muro "
            "es una mancha negra. Entonces el agrimensor apoya la diagonal de una "
            "baldosa sobre la cuerda, hace una marca — y esa marca cae en un punto que "
            "el aprendiz no había tocado."
        ),
        "question": (
            "Si el aprendiz hubiera tenido tinta infinita y hubiera marcado TODAS las "
            "fracciones, ¿habría quedado algún punto sin marcar?"
        ),
        "image": "/leccion/01-prealg-n1-agora/b08-reales-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "No: con todas las fracciones ya está todo cubierto"},
                {"id": "b", "text": "Sí: quedan huecos, y son los irracionales"},
                {"id": "c", "text": "Quedan huecos, pero muy pocos"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber que la "
                "recta necesita a los DOS conjuntos, y ninguno sobra."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos preguntas sobre la misma cuerda",
        "body": (
            "La cuerda entre el 0 y el 1 se ve igual en los dos casos de abajo, pero las "
            "preguntas son distintas y las respuestas te van a sorprender por razones opuestas."
        ),
        "cases": [
            {
                "label": "Caso que ya sabías",
                "context": "El aprendiz marca todas las fracciones entre 0 y 1",
                "fraction": r"\dfrac{1}{2},\ \dfrac{1}{3},\ \dfrac{2}{3},\ \dfrac{1}{4},\ \ldots",
                "division": r"\text{infinitas marcas}",
                "note": (
                    "Entre dos marcas cualesquiera siempre puede meter otra: basta el "
                    "promedio. Nunca termina, y nunca hay «la siguiente»."
                ),
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "El agrimensor apoya la diagonal de la baldosa",
                "fraction": r"\dfrac{\sqrt{2}}{2}",
                "division": r"\approx0{,}7071\ldots",
                "note": (
                    "Ese punto existe, se puede construir con regla — y NO es ninguna de "
                    "las infinitas marcas del aprendiz. Estaba en un hueco."
                ),
            },
        ],
        "resolution": (
            "Dos cosas a la vez, y cuestan de tragar juntas. Las fracciones están "
            "APRETADAS: entre dos cualesquiera hay infinitas más, así que ninguna tiene "
            "siguiente. Y aun así, apretadas y todo, DEJAN HUECOS. La recta completa "
            "necesita las fracciones y los irracionales al tiempo. A esa unión la "
            "llamamos los reales."
        ),
    },
    "definition_title": "Los números reales",
    "definition_katex": r"\mathbb{R}=\mathbb{Q}\cup\mathbb{I}\quad\text{con}\quad\mathbb{Q}\cap\mathbb{I}=\varnothing",
    "definition": (
        "La frase del nodo: los reales son los números de la recta. Cada punto tiene "
        "nombre, cada nombre tiene punto, y entre dos cualesquiera siempre hay otro."
    ),
    "definition_symbols": [
        {
            "symbol": r"\mathbb{R}",
            "reads": "los reales",
            "means": "todos los puntos de la recta numérica, sin huecos",
        },
        {"symbol": r"\cup", "reads": "unión", "means": "junta los dos conjuntos en uno solo"},
        {"symbol": r"\cap", "reads": "intersección", "means": "lo que tienen en común"},
        {
            "symbol": r"\varnothing",
            "reads": "conjunto vacío",
            "means": "nada: ningún número es racional e irracional a la vez",
        },
        {
            "symbol": r"\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
            "reads": "la cadena de inclusiones",
            "means": "cada peldaño contiene enterito al anterior; no se perdió nada",
        },
        {
            "symbol": r"\dfrac{a+b}{2}",
            "reads": "el promedio de a y b",
            "means": "la receta para meter siempre un número entre otros dos",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Meter un número donde no cabía",
            "title": "La marca entre dos marcas",
            "statement": (
                "El aprendiz ya marcó 0,3 y 0,4 en la cuerda y dice que ahí no cabe nada "
                "más. ¿Puedes darle un número que caiga justo en medio?"
            ),
            "latex": r"\dfrac{0{,}3+0{,}4}{2}",
            "image_slot": False,
            "steps": [
                "Para meter un número entre dos, el promedio siempre sirve.",
                "Sumo los dos extremos: 0,3 + 0,4 = 0,7.",
                "Divido entre 2: 0,7 ÷ 2 = 0,35.",
                "Compruebo que quedó en medio: 0,3 < 0,35 < 0,4. ✓",
                "Y lo importante: puedo repetir la receta con 0,3 y 0,35, y otra vez, sin fin.",
            ],
            "solution": r"$0{,}35$, y la receta se repite infinitas veces.",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 4,
                "prompt": (
                    "El paso 5 dice que la receta se puede repetir sin fin. ¿Qué significa "
                    "eso sobre la idea de «el número que sigue»?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Ubicar un irracional en la recta",
            "title": "La diagonal apoyada sobre la cuerda",
            "statement": (
                "¿Entre qué dos enteros cae √2, y cómo se marca ese punto exacto sin "
                "medirlo con la regla?"
            ),
            "latex": r"1<\sqrt{2}<2",
            "image_slot": False,
            "steps": [
                "1 × 1 = 1 y 2 × 2 = 4. Como 2 está entre 1 y 4, √2 está entre 1 y 2.",
                "Afino: 1,4 × 1,4 = 1,96 (se queda corto) y 1,5 × 1,5 = 2,25 (se pasa).",
                "Entonces √2 está entre 1,4 y 1,5. Puedo seguir afinando para siempre.",
                "Para el punto EXACTO no mido: construyo. Apoyo la diagonal de la baldosa de lado 1 sobre la cuerda desde el 0.",
                "Donde cae la punta, ahí está √2. Es un punto de la recta como cualquier otro, aunque no sea fracción.",
            ],
            "solution": r"$\sqrt{2}\in\mathbb{R}$, entre 1 y 2, construible con regla.",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El número que venía después",
            "statement": (
                "Un aprendiz escribió esto en la tablilla. Está mal: «Después del 2,5 "
                "viene el 2,6, igual que después del 2 viene el 3. Entre 2,5 y 2,6 no "
                "hay nada»."
            ),
            "latex": r"\text{siguiente}(2{,}5)=2{,}6",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"2{,}5\ \underline{\rightarrow}\ 2{,}6",
            "error_note": (
                "Aquí se cayó. Trajo a la recta una idea que solo vale en ℕ y ℤ: que "
                "cada número tiene un vecino inmediato. En los reales eso no existe."
            ),
            "correct_version": {
                "wrong_latex": r"\text{entre }2{,}5\text{ y }2{,}6:\ \text{nada}",
                "right_latex": r"2{,}5<2{,}55<2{,}555<\ldots<2{,}6",
                "rows": [
                    {
                        "wrong": "Después de 2,5 viene 2,6",
                        "right": "No hay «el siguiente»: el promedio 2,55 se cuela en medio",
                    },
                    {
                        "wrong": "En ℤ pasa igual que en ℝ",
                        "right": "En ℤ sí hay siguiente (3 sigue a 2); en ℝ nunca",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué en los reales ningún número tiene siguiente? Escribe un número "
                "entre 2,5 y 2,6."
            ),
            "steps": [
                "Calcula el promedio de 2,5 y 2,6.",
                "Comprueba que el resultado esté estrictamente entre los dos.",
                "Ahora repite con 2,5 y ese nuevo número, y date cuenta de que nunca se acaba.",
            ],
            "solution": (
                "En ℕ y ℤ los números están separados: el 2 y el 3 son vecinos y no hay "
                "nada en medio. En ℝ están APRETADOS: entre dos cualesquiera siempre "
                "cabe otro, así que «el siguiente» no existe. Esa es la diferencia entre "
                "contar y medir, y es la razón de que la recta se vea llena."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el procedimiento ya está "
            "empezado y solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Mete un número entre 1,2 y 1,3 usando la receta del promedio.",
                "given_steps": [
                    r"1{,}2+1{,}3=2{,}5",
                    r"2{,}5\div2",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Número en medio}=", "answer": "1,25"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "El agrimensor quiere saber entre qué dos enteros cae √30, para clavar "
                    "las marcas de referencia."
                ),
                "given_steps": [
                    r"5\times5=25",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"6\times6=", "answer": "36"},
                    {"id": "P2-b2", "label": r"\text{Entero de la izquierda}=", "answer": "5"},
                    {"id": "P2-b3", "label": r"\text{Entero de la derecha}=", "answer": "6"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: la clepsidra se vacía en 4 horas y hay que "
                    "marcar el punto medio del vaciado, luego el punto medio de la primera "
                    "mitad, y así 3 veces. ¿En qué hora cae la tercera marca?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Tercera marca (horas)}=", "answer": "0,5"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos caminos para meter un número entre otros dos",
        "intro": (
            r"Hay que dar un número entre $0{,}7$ y $0{,}8$. Las dos soluciones de abajo "
            r"son correctas."
        ),
        "methods": [
            {
                "label": "Método 1 · Promedio",
                "steps": [r"\dfrac{0{,}7+0{,}8}{2}", r"=\dfrac{1{,}5}{2}", r"=0{,}75"],
                "note": "Siempre funciona, con cualquier par de reales.",
            },
            {
                "label": "Método 2 · Agregar una cifra decimal",
                "steps": [r"0{,}7=0{,}70", r"0{,}8=0{,}80", r"0{,}71,\ 0{,}72,\ \ldots"],
                "note": "Rápido de ver, pero solo da algunos de los infinitos que hay.",
            },
        ],
        "question": (
            r"¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si te piden un "
            r"número entre $0{,}7$ y $0{,}70001$?"
        ),
        "insight": (
            "El método 2 se queda sin cifras cuando los dos números están muy cerca — hay "
            "que seguir agregando decimales y termina siendo el mismo trabajo. El promedio "
            "no falla nunca: por muy pegados que estén, siempre hay un punto medio. Esa "
            "es la demostración de que los reales son densos."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Da un número que esté entre 3,1 y 3,2, usando la receta del promedio.",
            "expr": r"\dfrac{3{,}1+3{,}2}{2}",
            "answer": "3,15",
            "hints": {
                "n1": "Suma los dos y divide entre 2.",
                "n2": "3,1 + 3,2 = 6,3.",
                "n3": "6,3 ÷ 2 = 3,15.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el entero inmediatamente a la IZQUIERDA de √52 en la recta?",
            "expr": r"\sqrt{52}",
            "answer": "7",
            "hints": {
                "n1": "Busca cuadrados perfectos cerca de 52.",
                "n2": "7 × 7 = 49 y 8 × 8 = 64.",
                "n3": "52 está entre 49 y 64, así que √52 está entre 7 y 8.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas afirmaciones sobre los reales es VERDADERA?",
            "options": [
                {"id": "dense", "text": "Entre dos reales distintos siempre hay otro real"},
                {"id": "next", "text": "Cada real tiene un siguiente, igual que los enteros"},
                {"id": "only_q", "text": "Todos los reales se pueden escribir como fracción"},
                {"id": "finite", "text": "Entre 0 y 1 hay una cantidad finita de reales"},
            ],
            "expected": "dense",
            "feedback_by_option": {
                "dense": "correct",
                "next": "fb_b08_e3_next",
                "only_q": "fb_b08_e3_onlyq",
                "finite": "fb_b08_e3_finite",
            },
            "misconception_by_option": {
                "next": "existe_el_siguiente",
                "only_q": "recta_es_solo_racionales",
                "finite": "densidad_finita",
            },
            "hints": {
                "n1": "Prueba cada una con un ejemplo concreto.",
                "n2": "Para la del siguiente: ¿qué número va después de 0,5?",
                "n3": "El promedio siempre se cuela: por eso ninguna tiene siguiente y hay infinitos.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un aprendiz anotó: «√9 no es real, porque las raíces son irracionales y "
                "los irracionales no caben en la recta». ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "both",
                    "text": "Dos errores: √9 = 3 es racional, y los irracionales SÍ están en la recta",
                },
                {
                    "id": "only_root",
                    "text": "Solo uno: √9 = 3, pero es cierto que los irracionales no caben",
                },
                {
                    "id": "only_line",
                    "text": "Solo uno: los irracionales sí caben, pero √9 sí es irracional",
                },
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "both",
            "feedback_by_option": {
                "both": "correct",
                "only_root": "fb_b08_e4_line",
                "only_line": "fb_b08_e4_root",
                "none": "fb_b08_e4_none",
            },
            "misconception_by_option": {
                "only_root": "recta_es_solo_racionales",
                "only_line": "toda_raiz_es_irracional",
                "none": "recta_es_solo_racionales",
            },
            "hints": {
                "n1": "Revisa las dos afirmaciones por separado.",
                "n2": "√9 = 3, y 3 = 3/1 es racional (eso lo viste en B07).",
                "n3": "Y ℝ = ℚ ∪ 𝕀: los irracionales son la mitad de la recta, no unos intrusos.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Cuál es el número real que sigue inmediatamente después de $0{,}9$?",
            "options": [
                {"id": "none", "text": "Ninguno: no existe el siguiente en los reales"},
                {"id": "one", "text": "El 1"},
                {"id": "ninety_one", "text": "El 0,91"},
                {"id": "nines", "text": "El 0,99999…"},
            ],
            "expected": "none",
            "feedback_by_option": {
                "none": "correct",
                "one": "fb_b08_e5_one",
                "ninety_one": "fb_b08_e5_trap",
                "nines": "fb_b08_e5_nines",
            },
            "misconception_by_option": {
                "one": "existe_el_siguiente",
                "ninety_one": "existe_el_siguiente",
                "nines": "existe_el_siguiente",
            },
            "hints": {
                "n1": "Escoge cualquier candidato y busca un número entre 0,9 y él.",
                "n2": "Si dices 0,91, ahí está 0,905 en medio. Y luego 0,9005.",
                "n3": "Cualquier candidato se cae por el promedio: por eso no hay siguiente.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "La balanza del mercado tiene marcas cada 10 gramos. Un comerciante dice: "
                "«entonces solo existen pesos de 10 en 10». ¿Qué le respondes?"
            ),
            "options": [
                {
                    "id": "instrument",
                    "text": "Que la balanza es el límite del instrumento, no del peso: entre 10 y 20 g hay infinitos pesos posibles",
                },
                {"id": "agree", "text": "Que tiene razón: si no se puede medir, no existe"},
                {
                    "id": "finer",
                    "text": "Que con una balanza más fina sí existirían todos los pesos intermedios",
                },
                {"id": "integers", "text": "Que los pesos siempre son enteros"},
            ],
            "expected": "instrument",
            "feedback_by_option": {
                "instrument": "correct",
                "agree": "fb_b08_e6_agree",
                "finer": "fb_b08_e6_finer",
                "integers": "fb_b08_e6_integers",
            },
            "misconception_by_option": {
                "agree": "instrumento_define_el_numero",
                "finer": "instrumento_define_el_numero",
                "integers": "existe_el_siguiente",
            },
            "hints": {
                "n1": "¿El peso de una manzana depende de qué balanza uses para pesarla?",
                "n2": "El peso ya está ahí; la balanza solo lo aproxima a la marca más cercana.",
                "n3": "Es el mismo error que la regla graduada de B06: el instrumento corta, el número no.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estas operaciones NO tiene resultado dentro de los reales?",
            "options": [
                {"id": "sqrt_neg", "text": "√(−4)", "latex": r"\sqrt{-4}"},
                {"id": "sqrt_two", "text": "√2", "latex": r"\sqrt{2}"},
                {"id": "div", "text": "1 ÷ 3", "latex": r"1\div3"},
                {"id": "sub", "text": "2 − 9", "latex": r"2-9"},
            ],
            "expected": "sqrt_neg",
            "feedback_by_option": {
                "sqrt_neg": "correct",
                "sqrt_two": "fb_b08_e7_closed",
                "div": "fb_b08_e7_closed",
                "sub": "fb_b08_e7_closed",
            },
            "misconception_by_option": {
                "sqrt_two": "irracional_no_es_real",
                "div": "fraccion_no_es_real",
                "sub": "negativo_no_es_real",
            },
            "hints": {
                "n1": "Tres de las cuatro las resolviste en peldaños anteriores.",
                "n2": "√2 es irracional pero real; 1÷3 y 2−9 también son reales.",
                "n3": "Ningún real multiplicado por sí mismo da un negativo. Ese es el próximo desvío.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "La escalera de la necesidad",
        "title": "¿Toda raíz cuadrada vive en el conjunto?",
        "intro": "Cerraste la recta. Ahora la pregunta que la parte otra vez.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{N}",
                "note": "No alcanza ni para la diagonal.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Z}",
                "note": "Los negativos no ayudaron aquí.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Q}",
                "note": "El golpe de B07: la diagonal no es fracción.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "no",
                "latex": r"\sqrt{-4}\notin\mathbb{R}",
                "note": "Casi: todas las raíces de positivos sí, pero las de negativos no.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"\sqrt{-4}=2i\in\mathbb{C}",
                "note": "Para eso hay que salirse de la recta. Desvío opcional: B09.",
            },
        ],
        "outro": (
            "Con ℝ tienes toda la recta y no falta ni un punto. Pero la recta tiene un "
            "límite propio: ningún número de ella, multiplicado por sí mismo, da negativo. "
            "Para resolver eso no hace falta un peldaño más alto — hace falta salirse de "
            "la línea y usar el plano."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres momentos clave de este nodo?",
        "thumbnails": [
            r"\dfrac{0{,}3+0{,}4}{2}",
            r"1<\sqrt{2}<2",
            r"\mathbb{R}=\mathbb{Q}\cup\mathbb{I}",
        ],
        "options": [
            {"id": "line", "text": "Los tres hablan de puntos de una misma recta", "correct": True},
            {
                "id": "dense",
                "text": "Los tres muestran que entre dos puntos siempre cabe otro",
                "correct": False,
            },
            {
                "id": "complete",
                "text": "Los tres apuntan a que la recta queda completa sin huecos",
                "correct": True,
            },
            {"id": "roots", "text": "Los tres necesitan raíces cuadradas", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El agrimensor debe clavar una marca justo en el punto medio entre 2,4 y "
            "2,5, y otra en el punto medio entre 2,4 y esa primera marca. ¿En qué "
            "número queda la SEGUNDA marca?"
        ),
        "polya": {
            "comprender": (
                "Me dan 2,4 y 2,5. Primero el punto medio de esos dos; después el punto "
                "medio entre 2,4 y ese resultado. Me piden el segundo."
            ),
            "planear": (
                "Aplico la receta del promedio dos veces seguidas, usando el resultado de "
                "la primera como extremo de la segunda."
            ),
            "ejecutar": (
                "Primera: (2,4 + 2,5) ÷ 2 = 4,9 ÷ 2 = 2,45. "
                "Segunda: (2,4 + 2,45) ÷ 2 = 4,85 ÷ 2 = 2,425."
            ),
            "comprobar": (
                "2,4 < 2,425 < 2,45 < 2,5 ✓. Y noto lo importante: podría seguir para "
                "siempre acercándome a 2,4 sin llegar nunca — no hay «el siguiente de 2,4»."
            ),
        },
        "prompt": "¿En qué número queda la segunda marca?",
        "answer": "2,425",
        "hints": {
            "n1": "Haz primero el punto medio entre 2,4 y 2,5.",
            "n2": "Ese da 2,45. Ahora promedia 2,4 con 2,45.",
            "n3": "(2,4 + 2,45) ÷ 2 = 4,85 ÷ 2.",
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
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué en la "
            "recta ningún número tiene siguiente."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Qué número REAL viene inmediatamente después del 7?",
                "options": [
                    {"id": "none", "text": "Ninguno: siempre hay uno en medio"},
                    {"id": "eight", "text": "El 8"},
                    {"id": "seven_one", "text": "El 7,1"},
                ],
                # Misma pregunta del D1 pero en ℝ, no en ℤ: la respuesta correcta se
                # invierte. Contesta bien quien distingue los dos conjuntos.
                "expected": "none",
                "misconception_by_option": {
                    "eight": "existe_el_siguiente",
                    "seven_one": "existe_el_siguiente",
                },
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Da un número entre 1,6 y 1,7 (usa el promedio).",
                "answer": "1,65",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿$\pi$ es un número real?",
                "options": [
                    {"id": "yes", "text": "Sí: está en la recta, entre 3 y 4"},
                    {"id": "no", "text": "No: es irracional, y los irracionales no son reales"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "recta_es_solo_racionales"},
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
        "fb_b08_e3_next": (
            "Eso vale en ℤ, no en ℝ. Si 0,5 tuviera siguiente, el promedio de los dos se "
            "colaría en medio. → Busca un número entre 0,5 y tu candidato."
        ),
        "fb_b08_e3_onlyq": (
            "√2 y π son reales y no son fracción. ℝ = ℚ ∪ 𝕀: los irracionales son parte "
            "de la recta. → Busca la afirmación que habla de lo que hay ENTRE dos reales."
        ),
        "fb_b08_e3_finite": (
            "Con la receta del promedio puedes fabricar uno nuevo cuantas veces quieras "
            "sin salirte de 0 y 1: son infinitos. → Prueba a meter un número entre 0 y 0,1."
        ),
        "fb_b08_e4_line": (
            "Acertaste con √9 = 3, pero la segunda afirmación también está mal: los "
            "irracionales SÍ están en la recta. → Ubica √2 entre 1 y 2."
        ),
        "fb_b08_e4_root": (
            "Acertaste con la recta, pero √9 no es irracional: da 3, y 3 es racional. → "
            "Calcula √9 antes de clasificarla."
        ),
        "fb_b08_e4_none": (
            "Hay dos errores en esa frase. Empieza por calcular √9. → Di cuánto vale y "
            "de qué conjunto es."
        ),
        "fb_b08_e5_one": (
            "Entre 0,9 y 1 hay infinitos: 0,95, 0,99, 0,999… → Escribe uno de ellos."
        ),
        "fb_b08_e5_trap": (
            "0,905 está entre 0,9 y 0,91, así que 0,91 no es el siguiente. Y con 0,905 "
            "pasa lo mismo. → Repite el promedio y mira si alguna vez se acaba."
        ),
        "fb_b08_e5_nines": (
            "Ese número no está «justo después»: 0,99999… con infinitos nueves es "
            "exactamente 1, y entre 0,9 y 1 hay infinitos más. → Busca un número entre "
            "0,9 y tu candidato."
        ),
        "fb_b08_e6_agree": (
            "Ese es el error de fondo del nodo: el instrumento no crea el número. Una "
            "manzana de 13 g pesa 13 g aunque la balanza marque 10. → Di si el peso "
            "depende de la balanza."
        ),
        "fb_b08_e6_finer": (
            "Vas cerca, pero al revés: los pesos intermedios YA existen; una balanza más "
            "fina solo los muestra. → Di qué existe primero, el peso o la marca."
        ),
        "fb_b08_e6_integers": (
            "El peso de media manzana no es entero, y existe igual. → Piensa en un peso "
            "que caiga entre dos marcas."
        ),
        "fb_b08_e7_closed": (
            "Esa sí cabe en ℝ: los irracionales, las fracciones y los negativos son "
            "todos reales. → Busca la que pide un número que multiplicado por sí mismo "
            "dé negativo."
        ),
    },
    "closing": (
        "La recta quedó llena y ordenada, y sin ningún «siguiente». Ese es el sistema de "
        "números con el que vas a trabajar de aquí en adelante. Lo que viene es un "
        "desvío opcional: qué pasa cuando la recta se queda corta."
    ),
    "validation_status": "F1_B08_11bloques",
}
