"""M01 · Conmutativa — el orden importa en cuatro de las seis operaciones.

Estación del nodo: LA PRENSA DE INTERCAMBIO (placas de bronce que entran por dos
bocas y se pueden cambiar de boca). Ninguna otra estación usa este material.
"""

NODE_ID = "PREALG-N3-M01-CONMUTATIVA"
CONCEPT_SLUG = "conmutativa"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "conmutativa",
    "misconception": "todas_las_operaciones_son_conmutativas",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La Prensa de Intercambio · Conmutativa",
    "station": "La Prensa de Intercambio",
    "finish_label": "Salir hacia el Horno de Fundición",
    "title": "Cambiar de boca no siempre da lo mismo",
    "intro": (
        "Ya conoces las seis operaciones. Ahora vas a preguntarles algo que ninguna te "
        "había pedido: ¿qué pasa si intercambias los dos números de sitio? En cuatro de "
        "ellas el resultado se derrumba, y saber en cuáles es lo que te deja calcular "
        "rápido sin equivocarte."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de encender la prensa. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $7+5$ y $5+7$?",
                "options": [
                    {"id": "yes", "text": "Sí"},
                    {"id": "no", "text": "No"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "orden_altera_toda_operacion"},
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $12\div 4$ y $4\div 12$?",
                "options": [
                    {"id": "no", "text": "No"},
                    {"id": "yes", "text": "Sí"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "todas_las_operaciones_son_conmutativas"},
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿En cuáles de estas operaciones puedes cambiar los dos números de sitio sin que cambie el resultado?",
                "options": [
                    {"id": "sum_mult", "text": "Solo en la suma y la multiplicación"},
                    {"id": "all", "text": "En todas"},
                    {"id": "sum_only", "text": "Solo en la suma"},
                    {"id": "none", "text": "En ninguna"},
                ],
                "expected": "sum_mult",
                "misconception_by_option": {
                    "all": "todas_las_operaciones_son_conmutativas",
                    "sum_only": "multiplicacion_no_conmutativa",
                    "none": "orden_altera_toda_operacion",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En la Prensa de Intercambio",
        "title": "Las dos bocas de la prensa",
        "body": (
            "La primera estación de la fábrica es una prensa con dos bocas de carga, una a "
            "cada lado. Entran placas de bronce por las dos y sale una pieza única. Sobre "
            "el bastidor hay una palanca que intercambia las bocas: lo que iba por la "
            "izquierda pasa a la derecha y al revés.\n\n"
            "El operario lleva años tirando de esa palanca cuando se equivoca al cargar. "
            "«Da igual el lado», dice. Hoy la prensa está configurada para dividir, tiró de "
            "la palanca por costumbre, y salió una pieza que no encaja en ningún molde."
        ),
        "question": "¿En qué operaciones se puede tirar de la palanca sin que cambie la pieza que sale?",
        "image": "/leccion/03-prealg-n3-fabrica/m01-conmutativa-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "En todas: el orden nunca importa"},
                {"id": "b", "text": "Solo en algunas"},
                {"id": "c", "text": "En ninguna: siempre importa"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder nombrar exactamente en "
                "cuáles sí y en cuáles no, y explicar por qué."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "La misma palanca, dos resultados distintos",
        "body": (
            "Abajo están las mismas dos placas cargadas en los dos órdenes, primero con la "
            "prensa sumando y después dividiendo."
        ),
        "cases": [
            {
                "label": "Caso que confirma lo que esperas",
                "context": "Placas de 8 y 3, prensa configurada para sumar",
                "fraction": r"8+3\ \text{y}\ 3+8",
                "division": r"8+3=11=3+8",
                "note": "La palanca no cambió nada: la pieza es la misma.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Las mismas placas de 8 y 3, prensa configurada para dividir",
                "fraction": r"8\div 3\ \text{y}\ 3\div 8",
                "division": r"8\div 3\approx 2{,}67\quad 3\div 8=0{,}375",
                "note": "La palanca cambió la pieza por completo. Ni siquiera se parecen.",
            },
        ],
        "resolution": (
            "La palanca no es buena ni mala: depende de para qué esté configurada la "
            "prensa. Sumar y multiplicar juntan cosas sin preguntar quién llegó primero. "
            "Restar y dividir tienen un papel de PROTAGONISTA — el minuendo, el dividendo — "
            "y otro de instrumento. Intercambiarlos cambia la pregunta."
        ),
    },
    "definition_title": "La propiedad conmutativa",
    "definition_katex": r"a+b=b+a\qquad a\times b=b\times a",
    "definition": (
        "Una operación es conmutativa si intercambiar sus dos números no cambia el "
        "resultado. La suma y la multiplicación lo son; la resta, la división y la "
        "potenciación no."
    ),
    "definition_symbols": [
        {
            "symbol": r"a,b",
            "reads": "los dos operandos",
            "means": "las dos placas cargadas en la prensa",
        },
        {
            "symbol": r"=",
            "reads": "igual",
            "means": "los dos órdenes producen exactamente la misma pieza",
        },
        {
            "symbol": r"a-b\neq b-a",
            "reads": "la resta no conmuta",
            "means": "salvo cuando a = b; lo viste en la Casa de Cuentas (E02)",
        },
        {
            "symbol": r"a\div b\neq b\div a",
            "reads": "la división no conmuta",
            "means": "salvo cuando a = b y ninguno es 0",
        },
        {
            "symbol": r"a^{b}\neq b^{a}",
            "reads": "la potencia no conmuta",
            "means": "2³ = 8 pero 3² = 9",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Suma y multiplicación",
            "title": "La palanca que sí se puede tirar",
            "statement": (
                "La prensa debe procesar placas de 25 y 4, primero sumando y después "
                "multiplicando. ¿Conviene cargar en un orden concreto?"
            ),
            "latex": r"25\times 4=4\times 25",
            "image_slot": False,
            "steps": [
                "Sumando: 25 + 4 = 29 y 4 + 25 = 29. Los dos órdenes coinciden.",
                "Multiplicando: 25 × 4 = 100 y 4 × 25 = 100. También coinciden.",
                "Coincidir no significa que dé igual para TRABAJAR: 4 × 25 se calcula de cabeza mucho más rápido.",
                "La conmutativa no cambia el resultado; cambia lo cómodo que es llegar a él.",
                "Por eso el operario puede tirar de la palanca cuando la prensa suma o multiplica: solo gana comodidad.",
            ],
            "solution": r"$25+4=29$ y $25\times 4=100$, en cualquier orden",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 los dos órdenes dan lo mismo pero uno es «mejor». ¿Mejor en qué sentido, si el resultado es idéntico?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Resta y división",
            "title": "La palanca que rompe la pieza",
            "statement": (
                "Las mismas placas de 25 y 4, ahora con la prensa configurada para restar y "
                "para dividir. ¿Qué pasa al intercambiarlas?"
            ),
            "latex": r"25-4\neq 4-25",
            "image_slot": False,
            "steps": [
                "Restando: 25 − 4 = 21, pero 4 − 25 = −21. No son iguales: son opuestos.",
                "Dividiendo: 25 ÷ 4 = 6,25, pero 4 ÷ 25 = 0,16. Ni siquiera son opuestos.",
                "En los dos casos el primer número tiene un papel distinto al segundo.",
                "En la resta, el primero es de lo que se quita; en la división, lo que se reparte.",
                "Intercambiarlos no reordena la misma cuenta: plantea otra cuenta.",
            ],
            "solution": r"$25-4=21$ pero $4-25=-21$; $25\div 4=6{,}25$ pero $4\div 25=0{,}16$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El operario que generalizó la palanca",
            "statement": (
                "El operario deja escrito en el turno de noche: «La palanca de intercambio "
                "es segura. Lo comprobé con 6 + 2 y 2 + 6, y con 6 × 2 y 2 × 6. Sale lo "
                "mismo. Vale para cualquier configuración de la prensa»."
            ),
            "latex": r"6+2=2+6\ \Rightarrow\ 6-2=2-6",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\underline{\Rightarrow}",
            "error_note": "Ese «por lo tanto» es el error: comprobó dos configuraciones y concluyó sobre todas.",
            "correct_version": {
                "wrong_latex": r"6-2=2-6",
                "right_latex": r"6-2=4\quad\text{pero}\quad 2-6=-4",
                "rows": [
                    {
                        "wrong": "Dos casos que funcionan prueban la regla general",
                        "right": "Un solo caso que falla tumba la regla general",
                    },
                    {
                        "wrong": "La palanca es segura en cualquier configuración",
                        "right": "Es segura solo sumando y multiplicando",
                    },
                ],
            },
            "explain_prompt": "Da un caso que tumbe la nota del operario y escribe las dos cuentas.",
            "steps": [
                "El operario probó donde la propiedad SÍ vale y no probó donde falla.",
                "Basta configurar la prensa para restar: 6 − 2 = 4 y 2 − 6 = −4.",
                "Un contraejemplo derriba una afirmación general; mil ejemplos a favor no la sostienen (lo viste en B12).",
            ],
            "solution": (
                "Antes de tirar de la palanca hay una sola pregunta: ¿los dos números hacen "
                "el mismo papel en esta operación? Si uno es «de lo que se quita» o «lo que "
                "se reparte», no lo puedes mover."
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
                "statement": "Reordena para calcular de cabeza: placas de 2, 47 y 5, prensa multiplicando.",
                "given_steps": [
                    r"2\times 47\times 5=2\times 5\times 47",
                    r"2\times 5=10",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"10\times 47=", "answer": "470"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "La prensa resta placas de 9 y 14, y el operario tira de la palanca.",
                "given_steps": [
                    r"\text{cuenta pedida: }9-14",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"9-14=", "answer": "-5"},
                    {"id": "P2-b2", "label": r"14-9=", "answer": "5"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: la prensa está configurada para elevar. Cargan "
                    "placas de 2 y 4. Calcula el resultado en el orden 2 elevado a 4."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"2^{4}=", "answer": "16"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para el mismo producto",
        "intro": r"¿Cuánto vale $4\times 17\times 25$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · En el orden escrito",
                "steps": [r"4\times 17=68", r"68\times 25=1700"],
                "note": "Fiel al enunciado, pero 68 × 25 no sale de cabeza.",
            },
            {
                "label": "Método 2 · Reordenar primero",
                "steps": [r"4\times 25=100", r"100\times 17=1700"],
                "note": "Usa la conmutativa para juntar los factores cómodos.",
            },
        ],
        "question": "¿Cuál harías sin papel? ¿Y podrías hacer el mismo movimiento si en vez de productos hubiera restas?",
        "insight": (
            "El método 2 vale por la conmutativa: 4 × 17 × 25 = 4 × 25 × 17. Con restas el "
            "movimiento es ilegal tal cual: 20 − 8 − 3 = 9, pero 8 − 20 − 3 = −15. Lo único "
            "que sí puedes mover en una resta es cada número CON su signo, tratándolo como "
            "una suma: 20 + (−8) + (−3). Ese truco lo vas a formalizar en la estación siguiente."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Reordena para calcular rápido: 5 × 37 × 2. ¿Cuánto da?",
            "expr": r"5\times 37\times 2",
            "answer": "370",
            "hints": {
                "n1": "¿Qué dos factores juntos dan un número redondo?",
                "n2": "5 × 2 = 10.",
                "n3": "10 × 37 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "La prensa resta placas de 6 y 19, en ese orden. ¿Qué sale?",
            "expr": r"6-19",
            "answer": "-13",
            "hints": {
                "n1": "Respeta el orden: no tires de la palanca.",
                "n2": "6 − 19 = 6 + (−19).",
                "n3": "Se cancelan 6, y del −19 sobran 13.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estas igualdades es FALSA?",
            "options": [
                {
                    "id": "power",
                    "text": "2 elevado a 3 igual a 3 elevado a 2",
                    "latex": r"2^{3}=3^{2}",
                },
                {"id": "sum", "text": "9 + 4 = 4 + 9", "latex": r"9+4=4+9"},
                {"id": "mult", "text": "9 × 4 = 4 × 9", "latex": r"9\times 4=4\times 9"},
                {"id": "same", "text": "7 − 7 = 7 − 7", "latex": r"7-7=7-7"},
            ],
            "expected": "power",
            "feedback_by_option": {
                "power": "correct",
                "sum": "fb_m01_e3_true",
                "mult": "fb_m01_e3_true",
                "same": "fb_m01_e3_same",
            },
            "misconception_by_option": {
                "sum": "orden_altera_toda_operacion",
                "mult": "multiplicacion_no_conmutativa",
                "same": "no_evalua_antes_de_juzgar",
            },
            "hints": {
                "n1": "Calcula las dos partes de cada igualdad antes de decidir.",
                "n2": "2³ = 8.",
                "n3": "3² = 9, y 8 no es 9.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un operario anota «La prensa dividió 3 entre 15 y dio 5». ¿Dónde está el error?",
            "options": [
                {"id": "swapped", "text": "Calculó 15 ÷ 3; el orden pedido daba 0,2"},
                {"id": "arith", "text": "Se equivocó al dividir: 3 ÷ 15 son 3"},
                {"id": "rounded", "text": "Redondeó mal el decimal"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "swapped",
            "feedback_by_option": {
                "swapped": "correct",
                "arith": "fb_m01_e4_arith",
                "rounded": "fb_m01_e4_rounded",
                "none": "fb_m01_e4_none",
            },
            "misconception_by_option": {
                "arith": "error_de_calculo_no_de_orden",
                "rounded": "error_de_notacion_no_de_valor",
                "none": "todas_las_operaciones_son_conmutativas",
            },
            "hints": {
                "n1": "¿Qué número escribió primero el enunciado?",
                "n2": "Dividir 3 entre 15 reparte 3 en 15 partes: el resultado es menor que 1.",
                "n3": "3 ÷ 15 = 0,2, y 15 ÷ 3 = 5.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para cualesquiera $a$ y $b$: $a\div b=b\div a$.»",
            "options": [
                {"id": "false_unless", "text": "Falsa: solo coinciden si a = b y ninguno es 0"},
                {"id": "true", "text": "Verdadera: el orden nunca importa"},
                {"id": "false_never", "text": "Falsa: nunca pueden coincidir"},
                {"id": "true_positive", "text": "Verdadera si los dos son positivos"},
            ],
            "expected": "false_unless",
            "feedback_by_option": {
                "false_unless": "correct",
                "true": "fb_m01_e5_trap",
                "false_never": "fb_m01_e5_never",
                "true_positive": "fb_m01_e5_positive",
            },
            "misconception_by_option": {
                "true": "todas_las_operaciones_son_conmutativas",
                "false_never": "olvida_el_caso_de_igualdad",
                "true_positive": "todas_las_operaciones_son_conmutativas",
            },
            "hints": {
                "n1": "Para tumbar un «cualesquiera» basta UN caso.",
                "n2": "Prueba con a = 8 y b = 2.",
                "n3": "8 ÷ 2 = 4 y 2 ÷ 8 = 0,25. ¿Y si a y b fueran iguales?",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("Reordena para calcular de cabeza: 25 × 13 × 4. ¿Cuánto da?"),
            "expr": r"25\times 13\times 4",
            "answer": "1300",
            "hints": {
                "n1": "Junta primero los factores que dan un número redondo.",
                "n2": "25 × 4 = 100.",
                "n3": "100 × 13 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El operario quiere reordenar «40 − 8 × 5» poniendo el 5 delante del 8. "
                "¿Puede hacerlo?"
            ),
            "options": [
                {
                    "id": "yes_mult",
                    "text": "Sí: el 8 y el 5 se multiplican, y el producto sí conmuta",
                },
                {"id": "no", "text": "No: hay una resta en la expresión"},
                {"id": "yes_all", "text": "Sí: cualquier número se puede mover a cualquier sitio"},
                {"id": "only_paren", "text": "Solo si añade paréntesis alrededor de todo"},
            ],
            "expected": "yes_mult",
            "feedback_by_option": {
                "yes_mult": "correct",
                "no": "fb_m01_e7_no",
                "yes_all": "fb_m01_e7_all",
                "only_paren": "fb_m01_e7_paren",
            },
            "misconception_by_option": {
                "no": "aplica_la_restriccion_a_toda_la_expresion",
                "yes_all": "todas_las_operaciones_son_conmutativas",
                "only_paren": "parentesis_como_amuleto",
            },
            "hints": {
                "n1": "La conmutativa se aplica a UNA operación, no a la expresión entera.",
                "n2": "¿Qué operación conecta al 8 con el 5?",
                "n3": "8 × 5 = 40 y 5 × 8 = 40: la resta de fuera no se ve afectada.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Validez a lo largo de las operaciones",
        "title": "¿En qué operaciones se puede tirar de la palanca?",
        "intro": "La escalera de este nivel no recorre conjuntos: recorre las seis operaciones que ya visitaste.",
        "rows": [
            {
                "symbol": r"+",
                "name": "Suma",
                "closed": "yes",
                "latex": r"8+3=3+8",
                "note": "Los dos sumandos hacen el mismo papel: juntar no distingue quién llegó primero.",
            },
            {
                "symbol": r"-",
                "name": "Resta",
                "closed": "no",
                "latex": r"8-3\neq 3-8",
                "note": "Dan opuestos. El minuendo no es intercambiable con el sustraendo.",
            },
            {
                "symbol": r"\times",
                "name": "Multiplicación",
                "closed": "yes",
                "latex": r"8\times 3=3\times 8",
                "note": "Un rectángulo de 8 por 3 tiene las mismas teselas que uno de 3 por 8 (E03).",
            },
            {
                "symbol": r"\div",
                "name": "División",
                "closed": "no",
                "latex": r"8\div 3\neq 3\div 8",
                "note": "El dividendo se reparte y el divisor reparte: papeles distintos.",
            },
            {
                "symbol": r"a^{n}",
                "name": "Potenciación",
                "closed": "no",
                "latex": r"2^{3}=8\neq 9=3^{2}",
                "note": "La base se repite y el exponente cuenta: intercambiarlos cambia quién hace qué (E05).",
            },
            {
                "symbol": r"\sqrt[n]{a}",
                "name": "Radicación",
                "closed": "no",
                "latex": r"\sqrt[3]{8}=2\neq\sqrt[8]{3}",
                "note": "Índice y radicando tampoco son intercambiables (E06).",
            },
        ],
        "outro": (
            "Dos sí y cuatro no. La regla no se memoriza: se deduce preguntando si los dos "
            "números hacen el mismo papel. En la estación siguiente vas a hacerle la misma "
            "pregunta a los paréntesis."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten las operaciones donde la palanca SÍ se puede tirar?",
        "thumbnails": [r"8+3=3+8", r"8\times 3=3\times 8", r"8-3\neq 3-8"],
        "options": [
            {
                "id": "same_role",
                "text": "Sus dos números hacen el mismo papel en la operación",
                "correct": True,
            },
            {"id": "grow", "text": "Su resultado siempre crece", "correct": False},
            {
                "id": "join",
                "text": "Las dos juntan cantidades en lugar de separarlas",
                "correct": True,
            },
            {"id": "naturals", "text": "Solo funcionan con números naturales", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "La prensa tiene que procesar tres placas: 50, 17 y 2, multiplicándolas. "
            "El operario quiere hacerlo de cabeza. ¿Cuánto sale?"
        ),
        "polya": {
            "comprender": "Me dan tres factores y me piden el producto, calculable de cabeza.",
            "planear": "La multiplicación conmuta, así que reordeno para juntar los factores que den un número redondo.",
            "ejecutar": "50 × 2 = 100 → 100 × 17 = 1700.",
            "comprobar": "En el orden original: 50 × 17 = 850, y 850 × 2 = 1700. Coincide.",
        },
        "prompt": "¿Cuánto sale?",
        "answer": "1700",
        "hints": {
            "n1": "Busca dos factores que juntos den 100.",
            "n2": "50 × 2 = 100.",
            "n3": "100 × 17 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya distingues en qué operaciones el orden se puede mover.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué la resta y "
            "la división no aguantan el intercambio."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $6\times 9$ y $9\times 6$?",
                "options": [
                    {"id": "yes", "text": "Sí"},
                    {"id": "no", "text": "No"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "multiplicacion_no_conmutativa"},
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $15-6$ y $6-15$?",
                "options": [
                    {"id": "no", "text": "No"},
                    {"id": "yes", "text": "Sí"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "todas_las_operaciones_son_conmutativas"},
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Existe algún par de números donde $a-b=b-a$?",
                "options": [
                    {"id": "yes_equal", "text": "Sí: cuando a y b son iguales"},
                    {"id": "no_never", "text": "No, nunca"},
                    {"id": "yes_always", "text": "Sí, siempre"},
                ],
                "expected": "yes_equal",
                "misconception_by_option": {
                    "no_never": "olvida_el_caso_de_igualdad",
                    "yes_always": "todas_las_operaciones_son_conmutativas",
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
        "default": "Pregúntate si los dos números hacen el mismo papel antes de moverlos.",
        "fb_m01_e3_true": (
            "Esa igualdad es verdadera: ahí la conmutativa sí vale. → Busca la operación "
            "donde no vale."
        ),
        "fb_m01_e3_same": (
            "Los dos lados son idénticos carácter por carácter, así que es verdadera. "
            "→ Calcula las cuatro y quédate con la que no cuadra."
        ),
        "fb_m01_e4_arith": (
            "3 ÷ 15 no da 3: repartir 3 entre 15 da menos que 1. → Calcula 3 ÷ 15 y compáralo con 5."
        ),
        "fb_m01_e4_rounded": (
            "No hay redondeo de por medio: 0,2 y 5 no son el mismo número ni de lejos. "
            "→ Fíjate en qué orden dividió."
        ),
        "fb_m01_e4_none": (
            "Compruébalo al revés: si 3 ÷ 15 fuera 5, entonces 5 × 15 debería dar 3. "
            "→ Calcula ese producto."
        ),
        "fb_m01_e5_trap": (
            "Eso vale para la suma y el producto, no para la división. → Calcula 8 ÷ 2 y "
            "2 ÷ 8 y compáralos."
        ),
        "fb_m01_e5_never": (
            "Casi: fallan casi siempre, pero hay un caso donde coinciden. → Prueba con a = b = 4."
        ),
        "fb_m01_e5_positive": (
            "8 y 2 son los dos positivos y aun así falla. → Calcula las dos divisiones."
        ),
        "fb_m01_e7_no": (
            "La resta está fuera del trozo que se quiere mover. La conmutativa se aplica a "
            "una operación concreta. → Mira qué operación conecta al 8 con el 5."
        ),
        "fb_m01_e7_all": (
            "Mover el 40 al final sí cambiaría el resultado. No todo se puede mover. "
            "→ Di exactamente qué dos números se pueden intercambiar aquí y por qué."
        ),
        "fb_m01_e7_paren": (
            "Los paréntesis no dan permisos que la operación no tenga. → Decide si 8 × 5 "
            "y 5 × 8 son iguales, sin añadir nada."
        ),
    },
    "closing": (
        "Dos operaciones aguantan el intercambio y cuatro no, y el criterio es si los dos "
        "números hacen el mismo papel. En el Horno de Fundición vas a hacerle la misma "
        "pregunta a los paréntesis."
    ),
    "validation_status": "F3_M01_11bloques",
}
