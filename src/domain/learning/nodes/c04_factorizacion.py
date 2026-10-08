"""C04 · Factorización prima — hay que llegar hasta el final, y el final es único.

Destino del nodo: MILETO · piezas fundamentales. Contexto propio: los fardos de
lana del almacén, desarmados en madejas mínimas.
"""

NODE_ID = "PREALG-N4-C04-FACTORIZACION-PRIMA"
CONCEPT_SLUG = "factorizacion_prima"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "factorizacion_prima",
    "misconception": "deja_factores_compuestos",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "Mileto · Factorización prima",
    "destination": "Mileto · piezas fundamentales",
    "finish_label": "Zarpar hacia Atenas",
    "title": "Hay que llegar hasta el final, y el final es único",
    "intro": (
        "En Delos aprendiste a reconocer las piezas mínimas. Aquí las usas: todo número "
        "se desmonta en primos, y por muchos caminos distintos que tomes siempre llegas a "
        "las mismas piezas. Vas a ver por qué eso es un teorema y no una casualidad."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar al almacén. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $2\times 2\times 3$?",
                "answer": "12",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál de estas descomposiciones de $36$ está TERMINADA?",
                "options": [
                    {
                        "id": "primes",
                        "text": "2 × 2 × 3 × 3",
                        "latex": r"2\times 2\times 3\times 3",
                    },
                    {"id": "four_nine", "text": "4 × 9", "latex": r"4\times 9"},
                    {"id": "six_six", "text": "6 × 6", "latex": r"6\times 6"},
                ],
                "expected": "primes",
                "misconception_by_option": {
                    "four_nine": "deja_factores_compuestos",
                    "six_six": "deja_factores_compuestos",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si dos personas descomponen el mismo número en primos por caminos distintos, ¿obtienen lo mismo?",
                "options": [
                    {"id": "same", "text": "Sí: siempre las mismas piezas"},
                    {"id": "different", "text": "No: depende del camino"},
                    {"id": "sometimes", "text": "A veces sí y a veces no"},
                ],
                "expected": "same",
                "misconception_by_option": {
                    "different": "la_factorizacion_no_es_unica",
                    "sometimes": "la_factorizacion_no_es_unica",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el almacén de Mileto",
        "title": "Los dos aprendices y el mismo fardo",
        "body": (
            "En el almacén de Mileto la lana llega en fardos que hay que deshacer hasta "
            "madejas sueltas para pesarlas. Un fardo grande se abre en fardos medianos, "
            "esos en pequeños, y así hasta que ya no se puede abrir nada más.\n\n"
            "El maestro le dio a dos aprendices dos fardos idénticos de 60 madejas. El "
            "primero empezó separando por mitades; el segundo, apartando primero los lotes "
            "de tres. Terminaron con las manos llenas de madejas y discutiendo, porque "
            "cada uno juraba haber hecho un trabajo distinto del otro."
        ),
        "question": "Si dos caminos distintos desmontan el mismo fardo, ¿acaban con las mismas piezas?",
        "image": "/leccion/04-prealg-n4-puerto/c04-factorizacion-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "No: cada camino da piezas distintas"},
                {"id": "b", "text": "Sí: siempre las mismas, aunque en otro orden"},
                {"id": "c", "text": "Depende de por dónde se empiece"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder zanjar la discusión de "
                "los dos aprendices con un argumento, no con una opinión."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos caminos para desmontar el mismo 60",
        "body": (
            "Abajo, los dos aprendices. Compara las piezas del final, no el orden en que "
            "aparecieron."
        ),
        "cases": [
            {
                "label": "Camino del primer aprendiz",
                "context": "Empieza separando por mitades",
                "fraction": r"60=2\times 30",
                "division": r"60=2\times 2\times 3\times 5",
                "note": "60 → 2×30 → 2×2×15 → 2×2×3×5.",
            },
            {
                "label": "Camino del segundo aprendiz",
                "context": "Empieza apartando los lotes de tres",
                "fraction": r"60=3\times 20",
                "division": r"60=3\times 2\times 2\times 5=2\times 2\times 3\times 5",
                "note": "60 → 3×20 → 3×4×5 → 3×2×2×5. Las mismas piezas.",
            },
        ],
        "resolution": (
            "Dos caminos, dos madejas de 2, una de 3 y una de 5 en los dos casos. No se "
            "parecen: son idénticas. Ordenadas de menor a mayor, las dos listas coinciden "
            "carácter por carácter. Y eso no pasa solo con el 60: pasa con todos los "
            "números, siempre. Tiene nombre de teorema."
        ),
    },
    "definition_title": "El teorema fundamental de la aritmética",
    "definition_katex": r"n=p_1^{a_1}\times p_2^{a_2}\times\cdots\times p_k^{a_k}",
    "definition": (
        "Todo número natural mayor que 1 se escribe como producto de primos, y esa "
        "escritura es ÚNICA salvo el orden de los factores. Descomponer no es una técnica "
        "entre varias: es encontrar la identidad del número."
    ),
    "definition_symbols": [
        {
            "symbol": r"p_i",
            "reads": "los primos que aparecen",
            "means": "las madejas mínimas: ya no se abren más",
        },
        {
            "symbol": r"a_i",
            "reads": "cuántas veces aparece cada uno",
            "means": "el exponente; se escribe como potencia (E05)",
        },
        {
            "symbol": r"\text{única}",
            "reads": "salvo el orden",
            "means": "2×2×3 y 3×2×2 son la MISMA factorización",
        },
        {"symbol": r"n>1", "reads": "mayor que uno", "means": "el 1 queda fuera: no aporta piezas"},
        {
            "symbol": r"60=2^{2}\times 3\times 5",
            "reads": "forma con potencias",
            "means": "la escritura compacta de la misma lista",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Desmontar hasta el final",
            "title": "El fardo de 180 madejas",
            "statement": ("Descompón 180 en primos y escríbelo con potencias."),
            "latex": r"180",
            "image_slot": False,
            "steps": [
                "Divido por el primo más pequeño que pueda: 180 ÷ 2 = 90.",
                "Sigo con el 2: 90 ÷ 2 = 45. Ya no es par, así que el 2 se agotó.",
                "Paso al 3: 45 ÷ 3 = 15, y 15 ÷ 3 = 5.",
                "El 5 es primo: he llegado al final. Piezas: 2, 2, 3, 3, 5.",
                "180 = 2² × 3² × 5. Compruebo: 4 × 9 × 5 = 180.",
            ],
            "solution": r"$180=2^{2}\times 3^{2}\times 5$",
            "self_explanation": {
                "step_index": 3,
                "prompt": "En el paso 4 se declara terminado el trabajo. ¿Cómo sabes que no se puede seguir desmontando?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Para qué sirve",
            "title": "Contar divisores sin buscarlos",
            "statement": (
                "El maestro pregunta cuántos divisores tiene 180 sin escribir la lista. "
                "¿Se puede saber desde la factorización?"
            ),
            "latex": r"180=2^{2}\times 3^{2}\times 5^{1}",
            "image_slot": False,
            "steps": [
                "Cualquier divisor de 180 se arma con las mismas piezas, cogiendo algunas.",
                "Del 2 puedo coger 0, 1 o 2 madejas: 3 opciones. Del 3 igual: 3 opciones.",
                "Del 5 puedo coger 0 o 1: 2 opciones.",
                "Cada combinación da un divisor distinto: 3 × 3 × 2 = 18 divisores.",
                "La regla: se suma 1 a cada exponente y se multiplican. (2+1)(2+1)(1+1) = 18.",
            ],
            "solution": r"$180$ tiene $18$ divisores",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que dejó fardos sin abrir",
            "statement": (
                "Un aprendiz entrega el trabajo: «Fardo de 36 desmontado: 4 × 9. Ya está, "
                "porque 4 × 9 = 36»."
            ),
            "latex": r"36=4\times 9",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"36=\underline{4}\times\underline{9}",
            "error_note": "4 y 9 todavía se abren: no son madejas mínimas, son fardos medianos.",
            "correct_version": {
                "wrong_latex": r"36=4\times 9",
                "right_latex": r"36=2\times 2\times 3\times 3=2^{2}\times 3^{2}",
                "rows": [
                    {
                        "wrong": "Basta con que el producto dé el número",
                        "right": "Además, TODOS los factores tienen que ser primos",
                    },
                    {
                        "wrong": "4 × 9 y 6 × 6 son descomposiciones distintas de 36",
                        "right": "Las dos llevan a la misma: 2×2×3×3",
                    },
                ],
            },
            "explain_prompt": "Termina de desmontar 4 × 9 y escribe la factorización con potencias.",
            "steps": [
                "Comprueba cada factor: ¿4 es primo? D(4) = {1,2,4}, tres divisores → compuesto.",
                "¿9 es primo? D(9) = {1,3,9}, tres divisores → compuesto. Los dos se abren.",
                "4 = 2×2 y 9 = 3×3, así que 36 = 2×2×3×3 = 2² × 3².",
            ],
            "solution": (
                "La señal de que terminaste no es que el producto cuadre: es que ya no "
                "quede ningún factor compuesto. Revisa uno por uno antes de entregar."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El procedimiento ya va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Descompón 84 en primos.",
                "given_steps": [
                    r"84\div 2=42",
                    r"42\div 2=21",
                    r"21=3\times 7",
                ],
                "blanks": [
                    {
                        "id": "P1-b1",
                        "label": r"\text{cantidad de factores primos (con repetición)}=",
                        "answer": "4",
                    },
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Descompón 200 en primos y cuenta sus divisores.",
                "given_steps": [
                    r"200=2^{3}\times 5^{2}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"(3+1)\times(2+1)=", "answer": "12"},
                    {"id": "P2-b2", "label": r"2^{3}\times 5^{2}=", "answer": "200"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: ¿cuántos divisores tiene 72? Descompónlo primero."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{divisores de }72=", "answer": "12"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para descomponer 90",
        "intro": "Las dos soluciones de abajo llegan a la misma lista de piezas.",
        "methods": [
            {
                "label": "Método 1 · Divisiones sucesivas",
                "steps": [
                    r"90\div 2=45",
                    r"45\div 3=15",
                    r"15\div 3=5",
                    r"90=2\times 3^{2}\times 5",
                ],
                "note": "Ordenado: siempre el primo más pequeño que quepa.",
            },
            {
                "label": "Método 2 · Árbol de factores",
                "steps": [
                    r"90=9\times 10",
                    r"9=3\times 3,\quad 10=2\times 5",
                    r"90=2\times 3^{2}\times 5",
                ],
                "note": "Parte por donde se te ocurra y sigue abriendo cada rama.",
            },
        ],
        "question": "¿Qué pasaría si en el método 2 empezaras por 90 = 6 × 15 en vez de 9 × 10?",
        "insight": (
            "Llegarías exactamente a 2 × 3 × 3 × 5. Ese es el contenido del teorema: el "
            "árbol puede tener cualquier forma, pero las hojas siempre son las mismas. Por "
            "eso el maestro no tuvo que decidir cuál aprendiz tenía razón — los dos hicieron "
            "el mismo trabajo."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"Descompón $28$ en primos. ¿Cuántos factores primos tiene contando repeticiones?",
            "expr": r"28=2\times 2\times 7",
            "answer": "3",
            "hints": {
                "n1": "Empieza dividiendo por el primo más pequeño que quepa.",
                "n2": "28 ÷ 2 = 14 y 14 ÷ 2 = 7.",
                "n3": "Las piezas son 2, 2 y 7.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"Si $n=2^{3}\times 5$, ¿cuánto vale $n$?",
            "expr": r"2^{3}\times 5",
            "answer": "40",
            "hints": {
                "n1": "Calcula la potencia primero.",
                "n2": "2³ = 8.",
                "n3": "8 × 5 = …",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuántos divisores tiene $n=2^{2}\times 3$?",
            "expr": r"(2+1)\times(1+1)",
            "answer": "6",
            "hints": {
                "n1": "Suma 1 a cada exponente y multiplica.",
                "n2": "(2+1) × (1+1).",
                "n3": "3 × 2 = …  (comprueba: n = 12 y D(12) tiene 6 elementos)",
            },
        },
        {
            "id": "E4",
            "kind": "multi_select",
            "tipo": "detecta_error",
            "prompt": "Selecciona TODAS las descomposiciones de 48 que estén SIN TERMINAR.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": "2 × 2 × 2 × 2 × 3"},
                {"id": "b", "text": "16 × 3"},
                {"id": "c", "text": "2 × 24"},
                {"id": "d", "text": "3 × 2 × 2 × 2 × 2"},
            ],
            "expected": ["b", "c"],
            "trap_options": ["a", "d"],
            "hints": {
                "n1": "Revisa factor por factor: si alguno es compuesto, está sin terminar.",
                "n2": "16 y 24 son compuestos: todavía se abren.",
                "n3": "El orden no importa: 2×2×2×2×3 y 3×2×2×2×2 son la misma, y las dos están terminadas.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «$36=6\times 6$ es la factorización prima de 36.»",
            "options": [
                {
                    "id": "false_composite",
                    "text": "Falsa: 6 es compuesto; hay que seguir hasta 2² × 3²",
                },
                {"id": "true", "text": "Verdadera: el producto da 36"},
                {"id": "false_other", "text": "Falsa: la factorización correcta es 4 × 9"},
                {
                    "id": "false_unique",
                    "text": "Falsa: 36 tiene varias factorizaciones primas distintas",
                },
            ],
            "expected": "false_composite",
            "feedback_by_option": {
                "false_composite": "correct",
                "true": "fb_c04_e5_trap",
                "false_other": "fb_c04_e5_other",
                "false_unique": "fb_c04_e5_unique",
            },
            "misconception_by_option": {
                "true": "deja_factores_compuestos",
                "false_other": "deja_factores_compuestos",
                "false_unique": "la_factorizacion_no_es_unica",
            },
            "hints": {
                "n1": "Comprueba si cada factor es primo.",
                "n2": "D(6) = {1,2,3,6}: cuatro divisores, así que 6 es compuesto.",
                "n3": "Sigue abriendo: 6 = 2 × 3, dos veces.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("¿Cuántos divisores tiene 100? Descompónlo primero."),
            "expr": r"100=2^{2}\times 5^{2}",
            "answer": "9",
            "hints": {
                "n1": "100 = 2² × 5².",
                "n2": "Suma 1 a cada exponente: (2+1) y (2+1).",
                "n3": "3 × 3 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": "Si el 1 se considerara primo, ¿qué se rompería?",
            "options": [
                {
                    "id": "uniqueness",
                    "text": "La unicidad: 6 sería 2×3, 1×2×3, 1×1×2×3… infinitas escrituras",
                },
                {"id": "nothing", "text": "Nada: el 1 no cambia el producto"},
                {"id": "product", "text": "Los productos darían resultados distintos"},
                {"id": "count", "text": "Habría menos primos"},
            ],
            "expected": "uniqueness",
            "feedback_by_option": {
                "uniqueness": "correct",
                "nothing": "fb_c04_e7_nothing",
                "product": "fb_c04_e7_product",
                "count": "fb_c04_e7_count",
            },
            "misconception_by_option": {
                "nothing": "uno_es_primo",
                "product": "confunde_valor_con_escritura",
                "count": "no_entiende_la_consecuencia",
            },
            "hints": {
                "n1": "El teorema dice que la factorización es ÚNICA salvo el orden.",
                "n2": "Prueba a escribir 6 metiendo unos delante.",
                "n3": "2×3, 1×2×3, 1×1×2×3… todas darían 6, y ya no habría una sola.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿El trabajo está terminado?",
        "title": "¿Todos los factores son primos?",
        "intro": "La única pregunta que hay que hacerle a una descomposición antes de entregarla.",
        "rows": [
            {
                "symbol": r"2\times 2\times 3",
                "name": "Para 12",
                "closed": "yes",
                "latex": r"12=2^{2}\times 3",
                "note": "2 y 3 son primos: terminada.",
            },
            {
                "symbol": r"4\times 9",
                "name": "Para 36",
                "closed": "no",
                "latex": r"4=2^{2},\ 9=3^{2}",
                "note": "Los dos factores son compuestos: quedan fardos sin abrir.",
            },
            {
                "symbol": r"2\times 18",
                "name": "Para 36",
                "closed": "no",
                "latex": r"18=2\times 3^{2}",
                "note": "Uno primo y otro compuesto. Basta que UNO se pueda abrir para que no esté terminada.",
            },
            {
                "symbol": r"2\times 2\times 3\times 3",
                "name": "Para 36",
                "closed": "yes",
                "latex": r"36=2^{2}\times 3^{2}",
                "note": "Terminada. Y es la única, venga de 4×9, de 6×6 o de 2×18.",
            },
            {
                "symbol": r"36",
                "name": "Para 36",
                "closed": "no",
                "latex": r"36\ \text{compuesto}",
                "note": "Un solo factor compuesto tampoco vale: no se ha desmontado nada.",
            },
            {
                "symbol": r"1\times 2\times 3",
                "name": "Para 6",
                "closed": "no",
                "latex": r"1\ \text{no es primo}",
                "note": "El 1 sobra: no es primo (C03) y además rompería la unicidad.",
            },
        ],
        "outro": (
            "Terminada quiere decir que ningún factor se abre más. Y el premio es fuerte: "
            "esas piezas son las mismas para todo el mundo, siempre. En Atenas vas a usarlas "
            "para comparar DOS números a la vez."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [
            r"180=2^{2}\times 3^{2}\times 5",
            r"60=2^{2}\times 3\times 5",
            r"36=4\times 9",
        ],
        "options": [
            {
                "id": "until_prime",
                "text": "En los tres hay que seguir abriendo hasta que solo queden primos",
                "correct": True,
            },
            {
                "id": "same_pieces",
                "text": "En los tres el camino elegido no cambia las piezas finales",
                "correct": True,
            },
            {
                "id": "two_factors",
                "text": "En los tres el número se parte en exactamente dos factores",
                "correct": False,
            },
            {"id": "even", "text": "En los tres el número es par", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Llega al almacén un fardo de 360 madejas. El maestro pide la factorización "
            "prima y, con ella, cuántos divisores tiene el número."
        ),
        "polya": {
            "comprender": "Me piden descomponer 360 en primos y después contar sus divisores.",
            "planear": "Divido por primos de menor a mayor hasta llegar a 1, y luego sumo 1 a cada exponente y multiplico.",
            "ejecutar": "360 = 2×180 = 2×2×90 = 2×2×2×45 = 2³×3²×5 → (3+1)(2+1)(1+1) = 4×3×2 = 24.",
            "comprobar": "2³×3²×5 = 8×9×5 = 360 ✓. Y 24 divisores es coherente: 360 es un número muy divisible.",
        },
        "prompt": "¿Cuántos divisores tiene 360?",
        "answer": "24",
        "hints": {
            "n1": "Descompón primero: empieza dividiendo entre 2 todas las veces que puedas.",
            "n2": "360 = 2³ × 3² × 5.",
            "n3": "(3+1) × (2+1) × (1+1) = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya revisas que ningún factor se pueda seguir abriendo.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo cómo saber que una "
            "descomposición está terminada."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $2\times 3\times 5$?",
                "answer": "30",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál de estas descomposiciones de $24$ está TERMINADA?",
                "options": [
                    {
                        "id": "primes",
                        "text": "2 × 2 × 2 × 3",
                        "latex": r"2\times 2\times 2\times 3",
                    },
                    {"id": "four_six", "text": "4 × 6", "latex": r"4\times 6"},
                    {"id": "eight_three", "text": "8 × 3", "latex": r"8\times 3"},
                ],
                "expected": "primes",
                "misconception_by_option": {
                    "four_six": "deja_factores_compuestos",
                    "eight_three": "deja_factores_compuestos",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Son la MISMA factorización $2\times 3\times 3$ y $3\times 2\times 3$?",
                "options": [
                    {"id": "yes", "text": "Sí: el orden no cuenta"},
                    {"id": "no", "text": "No: están escritas distinto"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "confunde_orden_con_identidad"},
                # Refuerza la mitad del teorema que el diagnóstico de entrada no
                # tocaba: la unicidad es "salvo el orden".
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
        "default": "Revisa factor por factor: si alguno es compuesto, el trabajo no ha terminado.",
        "fb_c04_e5_trap": (
            "El producto sí da 36, pero 6 no es primo. → Cuenta los divisores de 6 y sigue abriendo."
        ),
        "fb_c04_e5_other": (
            "4 × 9 tampoco está terminada: los dos factores son compuestos. → Abre los dos."
        ),
        "fb_c04_e5_unique": (
            "36 tiene UNA sola factorización prima; lo que hay son varios caminos para "
            "llegar a ella. → Descompón 6×6 y 4×9 y compara los resultados."
        ),
        "fb_c04_e7_nothing": (
            "El 1 no cambia el producto, pero sí cambia la ESCRITURA. → Escribe 6 con un 1 "
            "delante, luego con dos, y di cuántas escrituras hay."
        ),
        "fb_c04_e7_product": (
            "Los productos seguirían dando lo mismo: ese no es el problema. → Fíjate en "
            "cuántas escrituras distintas habría."
        ),
        "fb_c04_e7_count": (
            "Habría uno más, no menos, y ese no es el daño. → Piensa en qué parte del "
            "teorema dejaría de cumplirse."
        ),
    },
    "closing": (
        "Todo número se desmonta en primos y esa lista es única salvo el orden. Esas piezas "
        "son la identidad del número, y en Atenas las vas a usar para comparar dos números "
        "de un vistazo."
    ),
    "validation_status": "F4_C04_11bloques",
}
