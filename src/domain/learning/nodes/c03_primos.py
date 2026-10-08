"""C03 · Primos — exactamente dos divisores, ni uno más ni uno menos.

Destino del nodo: DELOS · la isla indivisible. Contexto propio: los sellos de
aduana y las tablillas de registro del puerto.
"""

NODE_ID = "PREALG-N4-C03-PRIMOS"
CONCEPT_SLUG = "primos"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "primos",
    "misconception": "uno_es_primo",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "Delos · Primos",
    "destination": "Delos · la isla indivisible",
    "finish_label": "Zarpar hacia Mileto",
    "title": "Exactamente dos divisores, ni uno más ni uno menos",
    "intro": (
        "En Rodas viste que algunos números tienen muchos divisores y otros muy pocos. "
        "Los que tienen el mínimo posible son las piezas con las que se construyen todos "
        "los demás. Vas a aprender a reconocerlos y a entender por qué el 1 se queda fuera."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de desembarcar. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuántos divisores tiene el 13?",
                "answer": "2",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Es 1 un número primo?",
                "options": [
                    {"id": "no", "text": "No"},
                    {"id": "yes", "text": "Sí"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "uno_es_primo"},
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Es 2 un número primo?",
                "options": [
                    {"id": "yes", "text": "Sí"},
                    {"id": "no", "text": "No, porque es par"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "par_no_puede_ser_primo"},
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En la aduana de Delos",
        "title": "El sello que no se podía repartir",
        "body": (
            "En la aduana de Delos, cada cargamento recibe un sello con su número de "
            "piezas. La costumbre es que el aduanero divida el cargamento en lotes iguales "
            "para inspeccionar solo uno. Con 12 piezas puede hacer lotes de 2, de 3, de 4 o "
            "de 6. Con 13 no puede hacer ningún lote: o inspecciona una pieza, o las trece.\n\n"
            "Un aduanero nuevo llegó con una lista de «números que no se dejan repartir» y "
            "puso el 1 en primer lugar. Su maestro le tachó esa línea sin decirle por qué."
        ),
        "question": "¿Por qué el 1, que tampoco se deja repartir, no está en esa lista?",
        "image": "/leccion/04-prealg-n4-puerto/c03-primos-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Es un error del maestro: el 1 debería estar"},
                {"id": "b", "text": "El 1 tiene menos divisores que los demás de la lista"},
                {"id": "c", "text": "El 1 es demasiado pequeño para contar"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder explicar la tachadura "
                "del maestro con una sola frase."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Contar divisores en vez de opinar",
        "body": (
            "En vez de discutir si un número «se deja repartir», cuenta cuántos divisores "
            "tiene. Abajo, dos cargamentos y el caso raro."
        ),
        "cases": [
            {
                "label": "Caso que se reparte",
                "context": "Cargamento de 12 piezas",
                "fraction": r"D(12)",
                "division": r"\{1,2,3,4,6,12\}\ \to\ 6\ \text{divisores}",
                "note": "Más de dos: hay lotes intermedios posibles. Se llama compuesto.",
            },
            {
                "label": "Caso que no se reparte",
                "context": "Cargamento de 13 piezas",
                "fraction": r"D(13)",
                "division": r"\{1,13\}\ \to\ 2\ \text{divisores}",
                "note": "Exactamente dos: solo 1 y él mismo. Se llama primo.",
            },
        ],
        "resolution": (
            "Ahora mira el 1: sus divisores son {1}. UNO solo, porque «1 y él mismo» son la "
            "misma cosa. No tiene dos, tiene uno. Por eso no entra en la lista: no cumple "
            "la definición, que exige exactamente dos. No es un capricho — si el 1 fuera "
            "primo, romperías algo importante, y lo vas a ver en Mileto."
        ),
    },
    "definition_title": "Números primos y compuestos",
    "definition_katex": r"p\ \text{primo}\iff |D(p)|=2",
    "definition": (
        "Un número natural es PRIMO si tiene exactamente dos divisores: el 1 y él mismo. "
        "Es COMPUESTO si tiene más de dos. El 1 no es ninguna de las dos cosas: tiene un "
        "solo divisor."
    ),
    "definition_symbols": [
        {
            "symbol": r"p",
            "reads": "un primo",
            "means": "un cargamento que no admite lotes intermedios",
        },
        {
            "symbol": r"|D(p)|",
            "reads": "cuántos divisores tiene p",
            "means": "el número de la lista de Rodas (C02)",
        },
        {
            "symbol": r"|D(1)|=1",
            "reads": "el uno tiene un solo divisor",
            "means": "por eso no es primo ni compuesto",
        },
        {
            "symbol": r"2",
            "reads": "el dos",
            "means": "el único primo par: todos los demás pares tienen al 2 de divisor extra",
        },
        {
            "symbol": r"\sqrt{n}",
            "reads": "raíz de n",
            "means": "el tope hasta donde hay que probar divisores (E06 y C02)",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Decidir con la raíz",
            "title": "¿Es primo el 97?",
            "statement": (
                "Llega un cargamento de 97 piezas. ¿Puede el aduanero hacer lotes iguales, "
                "o le toca inspeccionar todo?"
            ),
            "latex": r"\sqrt{97}\approx 9{,}8",
            "image_slot": False,
            "steps": [
                "No hace falta probar del 2 al 96: los divisores vienen en parejas (C02).",
                "En cada pareja uno es menor o igual que √97 ≈ 9,8, así que basta probar hasta el 9.",
                "Y solo con primos: 2 (97 es impar, no), 3 (9+7 = 16, no), 5 (no acaba en 0 ni 5, no), 7 (7×13 = 91, 7×14 = 98, no).",
                "Ningún primo hasta 9 lo divide, así que no hay ninguna pareja: solo quedan 1 y 97.",
                "97 es primo. Cuatro pruebas en vez de noventa y cinco.",
            ],
            "solution": r"$97$ es primo: $D(97)=\{1,97\}$",
            "self_explanation": {
                "step_index": 1,
                "prompt": "En el paso 2 se para en √97. ¿Por qué probar más allá no puede encontrar nada nuevo?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Un compuesto que engaña",
            "title": "El 51 parece primo y no lo es",
            "statement": (
                "Un cargamento de 51 piezas. Es impar y no acaba en 0 ni en 5. ¿Es primo?"
            ),
            "latex": r"51=3\times 17",
            "image_slot": False,
            "steps": [
                "Impar, así que el 2 queda descartado. No acaba en 0 ni 5, así que el 5 también.",
                "Falta el criterio del 3: sumo las cifras, 5 + 1 = 6.",
                "6 es múltiplo de 3, así que 3 divide a 51.",
                "51 ÷ 3 = 17, entonces D(51) = {1, 3, 17, 51}: cuatro divisores.",
                "51 es compuesto. Que sea impar no lo hace primo — hay que probar TODOS los primos hasta la raíz.",
            ],
            "solution": r"$51=3\times 17$: compuesto",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aduanero que puso el 1 en la lista",
            "statement": (
                "El aduanero nuevo defiende su lista: «El 1 solo se puede dividir entre 1 y "
                "entre sí mismo, igual que el 13. Si el 13 es primo, el 1 también»."
            ),
            "latex": r"D(1)=\{1\}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"D(1)=\{1,\underline{1}\}",
            "error_note": "«1 y él mismo» son el MISMO número. No son dos divisores, es uno contado dos veces.",
            "correct_version": {
                "wrong_latex": r"|D(1)|=2\ \Rightarrow\ 1\ \text{primo}",
                "right_latex": r"|D(1)|=1\ \Rightarrow\ 1\ \text{ni primo ni compuesto}",
                "rows": [
                    {
                        "wrong": "El 1 tiene dos divisores, como todo primo",
                        "right": "El 1 tiene UNO: el 1 y «él mismo» coinciden",
                    },
                    {
                        "wrong": "Primo = «no se puede repartir»",
                        "right": "Primo = «tiene exactamente dos divisores»",
                    },
                ],
            },
            "explain_prompt": "Escribe D(1) sin repetir elementos y di cuántos tiene.",
            "steps": [
                "Escribe el conjunto de divisores del 13: {1, 13}. Dos elementos distintos.",
                "Ahora el del 1: {1}. Un solo elemento, porque «él mismo» ES el 1.",
                "La definición pide exactamente dos, así que el 1 no cumple. No es primo, y tampoco compuesto.",
            ],
            "solution": (
                "La definición útil no es «no se deja repartir» sino «tiene exactamente dos "
                "divisores». Contar es objetivo; opinar sobre si se reparte, no. En Mileto "
                "vas a ver el motivo profundo de dejar al 1 fuera."
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
                "statement": "¿Cuántos divisores tiene el 29?",
                "given_steps": [
                    r"\sqrt{29}\approx 5{,}4",
                    r"2\nmid 29,\ 3\nmid 29,\ 5\nmid 29",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"|D(29)|=", "answer": "2"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "¿Es primo el 91? Prueba los primos hasta su raíz.",
                "given_steps": [
                    r"\sqrt{91}\approx 9{,}5;\quad 2\nmid,\ 3\nmid,\ 5\nmid",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"91\div 7=", "answer": "13"},
                    {"id": "P2-b2", "label": r"|D(91)|=", "answer": "4"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: ¿cuántos primos hay entre 1 y 20? Cuéntalos."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{cantidad de primos hasta }20=", "answer": "8"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para encontrar los primos hasta 30",
        "intro": "Las dos soluciones de abajo dan la misma lista.",
        "methods": [
            {
                "label": "Método 1 · Probar cada número",
                "steps": [
                    r"2:\ \text{primo}",
                    r"3:\ \text{primo}",
                    r"4=2\times 2:\ \text{no}\ \ldots",
                ],
                "note": "Uno por uno, buscándole divisores a cada candidato.",
            },
            {
                "label": "Método 2 · Criba de Eratóstenes",
                "steps": [
                    r"\text{escribo }2\ldots 30",
                    r"\text{tacho los múltiplos de }2,3,5",
                    r"\text{lo que queda es primo}",
                ],
                "note": "En vez de buscar divisores, tacha los múltiplos de lo ya encontrado.",
            },
        ],
        "question": "¿Por qué en el método 2 basta con tachar los múltiplos de 2, 3 y 5, y no hace falta seguir con 7?",
        "insight": (
            "Porque los múltiplos de 7 menores que 30 que aún no estuvieran tachados "
            "tendrían que ser 7 × algo ≥ 7, es decir al menos 49, que ya se pasa de 30. La "
            "regla general: basta cribar con los primos hasta √30 ≈ 5,5. Es la misma idea "
            "de las parejas de divisores que usaste en Rodas."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuántos divisores tiene el 23?",
            "expr": r"|D(23)|",
            "answer": "2",
            "hints": {
                "n1": "Prueba los primos hasta √23 ≈ 4,8.",
                "n2": "El 2 y el 3 no lo dividen.",
                "n3": "Solo quedan el 1 y el propio 23.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuántos divisores tiene el 49?",
            "expr": r"|D(49)|",
            "answer": "3",
            "hints": {
                "n1": "Prueba los primos hasta √49 = 7.",
                "n2": "7 × 7 = 49, así que el 7 lo divide.",
                "n3": "Los divisores son 1, 7 y 49: la pareja del 7 es él mismo.",
            },
        },
        {
            "id": "E3",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODOS los que son primos.",
            "valid_options": ["n1", "n2", "n9", "n17", "n51", "n97"],
            "options": [
                {"id": "n1", "text": "1"},
                {"id": "n2", "text": "2"},
                {"id": "n9", "text": "9"},
                {"id": "n17", "text": "17"},
                {"id": "n51", "text": "51"},
                {"id": "n97", "text": "97"},
            ],
            "expected": ["n2", "n17", "n97"],
            "trap_options": ["n1", "n51"],
            "hints": {
                "n1": "Cuenta los divisores de cada uno: primo es exactamente dos.",
                "n2": "El 1 tiene uno solo. El 9 tiene tres (1, 3, 9).",
                "n3": "El 51 engaña por impar: 5+1 = 6, así que el 3 lo divide.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un aduanero anota «2 no es primo porque es par». ¿Dónde está el error?",
            "options": [
                {
                    "id": "two_divisors",
                    "text": "Ser par no importa: 2 tiene exactamente dos divisores, 1 y 2",
                },
                {"id": "one_divisor", "text": "2 tiene un solo divisor"},
                {"id": "three", "text": "2 tiene tres divisores: 1, 2 y él mismo"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "two_divisors",
            "feedback_by_option": {
                "two_divisors": "correct",
                "one_divisor": "fb_c03_e4_one",
                "three": "fb_c03_e4_three",
                "none": "fb_c03_e4_none",
            },
            "misconception_by_option": {
                "one_divisor": "confunde_dos_con_uno",
                "three": "cuenta_el_numero_dos_veces",
                "none": "par_no_puede_ser_primo",
            },
            "hints": {
                "n1": "La definición no dice nada sobre pares o impares: cuenta divisores.",
                "n2": "Escribe D(2).",
                "n3": "D(2) = {1, 2}: dos elementos distintos.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": "¿Es verdadera o falsa? «Todos los números primos son impares.»",
            "options": [
                {"id": "false_two", "text": "Falsa: el 2 es primo y es par"},
                {"id": "true", "text": "Verdadera: un par siempre se puede dividir entre 2"},
                {"id": "false_many", "text": "Falsa: hay muchos primos pares"},
                {"id": "true_after_two", "text": "Verdadera a partir del 3"},
            ],
            "expected": "false_two",
            "feedback_by_option": {
                "false_two": "correct",
                "true": "fb_c03_e5_trap",
                "false_many": "fb_c03_e5_many",
                "true_after_two": "fb_c03_e5_after",
            },
            "misconception_by_option": {
                "true": "par_no_puede_ser_primo",
                "false_many": "cree_que_hay_varios_primos_pares",
                "true_after_two": "reformula_en_vez_de_refutar",
            },
            "hints": {
                "n1": "Para tumbar un «todos» basta UN caso.",
                "n2": "Busca un primo par.",
                "n3": "D(2) = {1, 2}: dos divisores, y 2 es par.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("¿Cuál es el primo más pequeño que supera a 30?"),
            "expr": r"p>30",
            "answer": "31",
            "hints": {
                "n1": "Empieza en 31 y sube.",
                "n2": "Para 31 prueba los primos hasta √31 ≈ 5,6.",
                "n3": "Ni 2, ni 3, ni 5 lo dividen.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": "¿Hasta qué número hay que probar divisores para decidir si 143 es primo?",
            "options": [
                {"id": "sqrt", "text": "Hasta 11, porque 11 × 11 = 121 y 12 × 12 pasa de 143"},
                {"id": "half", "text": "Hasta 71, la mitad de 143"},
                {"id": "all", "text": "Hasta 142"},
                {"id": "ten", "text": "Hasta 10, siempre basta con eso"},
            ],
            "expected": "sqrt",
            "feedback_by_option": {
                "sqrt": "correct",
                "half": "fb_c03_e7_half",
                "all": "fb_c03_e7_all",
                "ten": "fb_c03_e7_ten",
            },
            "misconception_by_option": {
                "half": "no_usa_la_raiz_como_tope",
                "all": "no_usa_la_raiz_como_tope",
                "ten": "generaliza_un_tope_fijo",
            },
            "hints": {
                "n1": "Los divisores vienen en parejas que multiplicadas dan 143.",
                "n2": "En cada pareja uno es menor o igual que la raíz.",
                "n3": "√143 está entre 11 y 12. (Y de hecho 143 = 11 × 13.)",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Contar divisores decide la categoría",
        "title": "¿Tiene exactamente dos divisores?",
        "intro": "Sin opiniones: se cuenta la lista de divisores y la respuesta cae sola.",
        "rows": [
            {
                "symbol": r"1",
                "name": "El uno",
                "closed": "no",
                "latex": r"D(1)=\{1\}",
                "note": "UN divisor. Ni primo ni compuesto: la única excepción de toda la clasificación.",
            },
            {
                "symbol": r"2",
                "name": "El dos",
                "closed": "yes",
                "latex": r"D(2)=\{1,2\}",
                "note": "Dos divisores: primo. Y el único primo par que existe.",
            },
            {
                "symbol": r"9",
                "name": "El nueve",
                "closed": "no",
                "latex": r"D(9)=\{1,3,9\}",
                "note": "Tres divisores: compuesto. Impar, pero no primo.",
            },
            {
                "symbol": r"17",
                "name": "El diecisiete",
                "closed": "yes",
                "latex": r"D(17)=\{1,17\}",
                "note": "Dos divisores: primo. Basta probar hasta √17 ≈ 4,1.",
            },
            {
                "symbol": r"51",
                "name": "El cincuenta y uno",
                "closed": "no",
                "latex": r"D(51)=\{1,3,17,51\}",
                "note": "Cuatro divisores: compuesto. Engaña porque es impar y no acaba en 5.",
            },
            {
                "symbol": r"97",
                "name": "El noventa y siete",
                "closed": "yes",
                "latex": r"D(97)=\{1,97\}",
                "note": "Dos divisores: primo. Cuatro pruebas bastan (2, 3, 5, 7).",
            },
        ],
        "outro": (
            "Dos divisores y ni uno más. El 1 se queda fuera por tener uno, no por ser "
            "pequeño, y en Mileto vas a ver qué se rompería si lo dejáramos entrar."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"D(97)", r"D(51)", r"D(1)"],
        "options": [
            {
                "id": "count",
                "text": "En los tres la decisión sale de CONTAR divisores",
                "correct": True,
            },
            {
                "id": "odd",
                "text": "En los tres el número es impar y por eso es primo",
                "correct": False,
            },
            {
                "id": "sqrt",
                "text": "En los tres basta probar divisores hasta la raíz",
                "correct": True,
            },
            {"id": "prime", "text": "Los tres son primos", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Llega a la aduana un cargamento de 113 piezas. El aduanero quiere saber si "
            "puede hacer lotes iguales. ¿Cuántos divisores tiene 113?"
        ),
        "polya": {
            "comprender": "Me piden decidir si 113 admite lotes, es decir, si es primo.",
            "planear": "Pruebo solo los primos hasta √113 ≈ 10,6: 2, 3, 5 y 7.",
            "ejecutar": "113 es impar (no 2); 1+1+3 = 5 (no 3); no acaba en 0 ni 5 (no 5); 7×16 = 112 (no 7). Ninguno divide.",
            "comprobar": "El siguiente primo es 11, y 11 × 11 = 121 > 113: ya me pasé del tope. No hay más que probar.",
        },
        "prompt": "¿Cuántos divisores tiene 113?",
        "answer": "2",
        "hints": {
            "n1": "Prueba solo los primos hasta la raíz de 113.",
            "n2": "√113 está entre 10 y 11: bastan 2, 3, 5 y 7.",
            "n3": "Ninguno lo divide, así que solo quedan 1 y 113.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya decides contando divisores, no por el aspecto del número.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el 1 tiene "
            "un solo divisor."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuántos divisores tiene el 19?",
                "answer": "2",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Es 1 un número primo?",
                "options": [
                    {"id": "no", "text": "No"},
                    {"id": "yes", "text": "Sí"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "uno_es_primo"},
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Es 15 un número primo?",
                "options": [
                    {"id": "no", "text": "No: 3 y 5 también lo dividen"},
                    {"id": "yes", "text": "Sí: es impar"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "impar_implica_primo"},
                # Complementa PD2: allí la respuesta era "no" por tener MENOS de
                # dos divisores; aquí es "no" por tener MÁS. Distinto motivo.
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
        "default": "Escribe la lista de divisores y cuéntala antes de decidir.",
        "fb_c03_e4_one": (
            "D(2) = {1, 2}: son dos números distintos. → Escribe la lista y cuéntala."
        ),
        "fb_c03_e4_three": (
            "«2» y «él mismo» son el mismo número: no se cuenta dos veces. → Escribe D(2) "
            "sin repetir."
        ),
        "fb_c03_e4_none": (
            "La definición de primo no menciona pares ni impares. → Cuenta los divisores de 2."
        ),
        "fb_c03_e5_trap": (
            "Un par se divide entre 2, sí — pero eso solo lo saca de la lista si el 2 es "
            "distinto de él mismo. → Cuenta los divisores del 2."
        ),
        "fb_c03_e5_many": (
            "Solo hay UNO: cualquier otro par tiene al 2 como tercer divisor. → Nómbralo."
        ),
        "fb_c03_e5_after": (
            "Eso ya no es la afirmación original; es otra distinta. → Di si la afirmación "
            "tal como está escrita es verdadera o falsa."
        ),
        "fb_c03_e7_half": (
            "La mitad funciona pero prueba muchísimo de más. → Piensa en las parejas de "
            "divisores y en dónde se cruzan."
        ),
        "fb_c03_e7_all": (
            "Eso siempre funciona pero es lo más lento posible. → Usa que los divisores "
            "vienen en parejas."
        ),
        "fb_c03_e7_ten": (
            "Con 143 el 11 es justo el que lo divide, y se te escaparía. → Calcula la raíz "
            "de 143 y usa eso como tope."
        ),
    },
    "closing": (
        "Primo es tener exactamente dos divisores; el 1 tiene uno y por eso queda fuera. "
        "Los primos son las piezas mínimas, y en Mileto vas a desmontar cualquier número "
        "en ellas."
    ),
    "validation_status": "F4_C03_11bloques",
}
