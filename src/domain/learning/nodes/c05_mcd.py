"""C05 · MCD — el mayor de los divisores COMUNES, no el mayor de los números.

Destino del nodo: ATENAS · lo más grande en común. Contexto propio: los cofres
del almacén portuario (el cofre más grande que reparte exacto dos cargamentos).
"""

NODE_ID = "PREALG-N4-C05-MCD"
CONCEPT_SLUG = "mcd"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "mcd",
    "misconception": "mcd_es_el_mayor_de_los_numeros",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "Atenas · Máximo común divisor",
    "destination": "Atenas · lo más grande en común",
    "finish_label": "Zarpar hacia Esparta",
    "title": "El mayor de los divisores comunes, no el mayor de los números",
    "intro": (
        "Hasta aquí mirabas un número a la vez. Ahora son dos, y la pregunta es qué "
        "comparten. El nombre de la operación lleva tres palabras y hay que leerlas las "
        "tres: máximo, común, divisor. Saltarse la del medio es el error de este muelle."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el almacén. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es el mayor número que divide a la vez a 12 y a 18?",
                "answer": "6",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale el MCD de $8$ y $20$?",
                "options": [
                    {"id": "four", "text": "4", "latex": r"4"},
                    {"id": "twenty", "text": "20", "latex": r"20"},
                    {"id": "one_sixty", "text": "160", "latex": r"160"},
                ],
                "expected": "four",
                "misconception_by_option": {
                    "twenty": "mcd_es_el_mayor_de_los_numeros",
                    "one_sixty": "confunde_mcd_con_producto",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Dos números pueden no tener ningún divisor en común aparte del 1?",
                "options": [
                    {"id": "yes", "text": "Sí"},
                    {"id": "no", "text": "No: siempre comparten alguno mayor"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "siempre_hay_divisor_comun_mayor_que_uno"},
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el almacén de Atenas",
        "title": "El cofre que servía para los dos cargamentos",
        "body": (
            "En el almacén de Atenas hay cofres de todos los tamaños. Llegan dos "
            "cargamentos —uno de 48 piezas y otro de 36— y hay que guardarlos en cofres "
            "IGUALES, sin mezclar los cargamentos y sin que quede ninguna pieza suelta.\n\n"
            "El encargado quiere el cofre más grande posible, para hacer menos viajes. "
            "Miró los dos números, dijo «el más grande es 48, uso cofres de 48» y bajó a "
            "buscarlos. Con el cargamento de 36 no llenó ni un cofre."
        ),
        "question": "¿Cuál es el cofre más grande que reparte exacto los DOS cargamentos?",
        "image": "/leccion/04-prealg-n4-puerto/c05-mcd-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "48: es el mayor de los dos"},
                {"id": "b", "text": "Algún número más pequeño que los dos"},
                {"id": "c", "text": "48 × 36, para que quepan los dos"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir el tamaño exacto "
                "del cofre y por qué no puede ser mayor."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Las dos listas y lo que tienen en medio",
        "body": (
            "Los divisores de cada cargamento, uno debajo del otro. Busca los que aparecen "
            "en las dos listas."
        ),
        "cases": [
            {
                "label": "Los divisores de cada uno",
                "context": "Cargamentos de 48 y de 36",
                "fraction": r"D(48),\ D(36)",
                "division": r"\{1,2,3,4,6,8,12,16,24,48\}\quad\{1,2,3,4,6,9,12,18,36\}",
                "note": "Diez divisores y nueve. Todavía no dicen nada por separado.",
            },
            {
                "label": "Los que están en las dos",
                "context": "Los divisores COMUNES",
                "fraction": r"D(48)\cap D(36)",
                "division": r"\{1,2,3,4,6,12\}\ \to\ \text{el mayor es }12",
                "note": "Seis en común, y el más grande es 12. Ese es el cofre.",
            },
        ],
        "resolution": (
            "El cofre no puede ser 48: 48 no divide a 36. Ni siquiera puede pasar de 36, "
            "porque tiene que caber en el más pequeño. El MCD siempre está entre 1 y el "
            "menor de los dos números — nunca por encima, y nunca es el producto."
        ),
    },
    "definition_title": "El máximo común divisor",
    "definition_katex": r"\text{MCD}(a,b)=\max\big(D(a)\cap D(b)\big)",
    "definition": (
        "El MCD de dos números es el mayor número que divide a los dos a la vez. Siempre "
        "existe (el 1 siempre está) y nunca supera al menor de los dos. Si vale 1, los "
        "números se llaman COPRIMOS."
    ),
    "definition_symbols": [
        {
            "symbol": r"\text{MCD}(a,b)",
            "reads": "máximo común divisor de a y b",
            "means": "el cofre más grande que sirve para los dos",
        },
        {
            "symbol": r"\cap",
            "reads": "intersección",
            "means": "lo que está en las DOS listas de divisores",
        },
        {
            "symbol": r"\max",
            "reads": "el máximo",
            "means": "el mayor de esa lista común, no de los números",
        },
        {
            "symbol": r"\text{MCD}(a,b)\le\min(a,b)",
            "reads": "no supera al menor",
            "means": "tiene que caber en el cargamento pequeño",
        },
        {
            "symbol": r"\text{MCD}(a,b)=1",
            "reads": "coprimos",
            "means": "no comparten nada salvo el 1",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Con las piezas de Mileto",
            "title": "El MCD desde la factorización",
            "statement": (
                "Los cargamentos son de 48 y 36 piezas. Halla el cofre más grande usando la "
                "descomposición en primos."
            ),
            "latex": r"48=2^{4}\times 3\qquad 36=2^{2}\times 3^{2}",
            "image_slot": False,
            "steps": [
                "Descompongo los dos: 48 = 2⁴ × 3 y 36 = 2² × 3².",
                "Un divisor común solo puede usar piezas que TENGAN LOS DOS.",
                "Del 2: uno tiene cuatro y el otro dos. Como mucho puedo usar dos → 2².",
                "Del 3: uno tiene uno y el otro dos. Como mucho uno → 3.",
                "MCD = 2² × 3 = 12. Se cogen los primos comunes con el exponente MENOR.",
            ],
            "solution": r"$\text{MCD}(48,36)=2^{2}\times 3=12$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se coge el exponente menor, no el mayor. ¿Por qué coger cuatro doses rompería el reparto?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando no comparten nada",
            "title": "Dos cargamentos coprimos",
            "statement": (
                "Ahora llegan cargamentos de 25 y 12 piezas. ¿Qué cofre sirve para los dos?"
            ),
            "latex": r"25=5^{2}\qquad 12=2^{2}\times 3",
            "image_slot": False,
            "steps": [
                "Descompongo: 25 = 5² y 12 = 2² × 3.",
                "Busco primos comunes: el 5 no está en 12, y ni el 2 ni el 3 están en 25.",
                "No hay ningún primo compartido, así que el único divisor común es el 1.",
                "MCD(25, 12) = 1: se dice que son coprimos.",
                "El cofre tendría que ser de una pieza. No hay forma de agrupar más sin romper alguno de los dos repartos.",
            ],
            "solution": r"$\text{MCD}(25,12)=1$: son coprimos",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El encargado que se saltó la palabra «común»",
            "statement": (
                "El encargado anota en el registro: «Cargamentos de 48 y 36. El máximo es "
                "48, así que uso cofres de 48»."
            ),
            "latex": r"\text{MCD}(48,36)=48",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\text{M}\underline{\text{C}}\text{D}",
            "error_note": "Leyó «máximo divisor» y se saltó la C. El máximo se busca DENTRO de lo común, no entre los dos números.",
            "correct_version": {
                "wrong_latex": r"\text{MCD}(48,36)=48",
                "right_latex": r"\text{MCD}(48,36)=12",
                "rows": [
                    {
                        "wrong": "El MCD es el mayor de los dos números",
                        "right": "Es el mayor de sus divisores COMUNES",
                    },
                    {
                        "wrong": "Un cofre de 48 sirve para los dos cargamentos",
                        "right": "No cabe en 36: el MCD nunca supera al número menor",
                    },
                ],
            },
            "explain_prompt": "¿Por qué el MCD no puede pasar de 36? Da el valor correcto.",
            "steps": [
                "Comprueba: ¿48 divide a 36? 36 ÷ 48 no es entero. No.",
                "Un divisor común tiene que dividir a los DOS, así que no puede ser mayor que el menor de ellos.",
                "Lo mayor que puede ser el MCD aquí es 36, y de hecho es 12.",
            ],
            "solution": (
                "Antes de responder un MCD, comprueba el techo: tiene que ser menor o igual "
                "que el número más pequeño. Si tu respuesta se pasa de ahí, está mal sin "
                "necesidad de revisar el procedimiento."
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
                "statement": "Halla el MCD de 20 y 30 con las factorizaciones.",
                "given_steps": [
                    r"20=2^{2}\times 5,\quad 30=2\times 3\times 5",
                    r"\text{comunes: }2\ \text{y}\ 5,\ \text{con el exponente menor}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{MCD}(20,30)=", "answer": "10"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Halla el MCD de 18 y 24.",
                "given_steps": [
                    r"18=2\times 3^{2},\quad 24=2^{3}\times 3",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{exponente del 3 que se coge}=", "answer": "1"},
                    {"id": "P2-b2", "label": r"\text{MCD}(18,24)=", "answer": "6"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: dos cargamentos de 14 y 15 piezas. ¿Qué cofre "
                    "sirve para los dos?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{MCD}(14,15)=", "answer": "1"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para el mismo cofre",
        "intro": r"¿Cuánto vale $\text{MCD}(84,120)$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Por factorización",
                "steps": [
                    r"84=2^{2}\times 3\times 7",
                    r"120=2^{3}\times 3\times 5",
                    r"\text{comunes: }2^{2}\times 3=12",
                ],
                "note": "Hay que descomponer los dos números primero.",
            },
            {
                "label": "Método 2 · Algoritmo de Euclides",
                "steps": [
                    r"120=84\times 1+36",
                    r"84=36\times 2+12",
                    r"36=12\times 3+0\ \Rightarrow\ 12",
                ],
                "note": "Solo divisiones con residuo, sin descomponer nada.",
            },
        ],
        "question": "¿Cuál usarías con dos números de cinco cifras que no sabes factorizar?",
        "insight": (
            "El método 2 nunca necesita conocer los primos: va cambiando el par por "
            "(divisor, residuo) hasta que el residuo es 0, y el último divisor no nulo es "
            "el MCD. Funciona porque todo divisor común de a y b también divide al residuo. "
            "Es de los algoritmos más antiguos que se siguen usando — está en Euclides, "
            "hace más de dos mil años."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el MCD de 16 y 24?",
            "expr": r"\text{MCD}(16,24)",
            "answer": "8",
            "hints": {
                "n1": "El resultado no puede pasar de 16.",
                "n2": "16 = 2⁴ y 24 = 2³ × 3.",
                "n3": "El único primo común es el 2, con exponente 3.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el MCD de 9 y 28?",
            "expr": r"\text{MCD}(9,28)",
            "answer": "1",
            "hints": {
                "n1": "Descompón los dos y busca primos compartidos.",
                "n2": "9 = 3² y 28 = 2² × 7.",
                "n3": "No comparten ningún primo: son coprimos.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el MCD de 15 y 45?",
            "expr": r"\text{MCD}(15,45)",
            "answer": "15",
            "hints": {
                "n1": "Comprueba primero si el pequeño divide al grande.",
                "n2": "45 ÷ 15 = 3, exacto.",
                "n3": "Si a divide a b, el MCD es a.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un encargado anota «MCD(10, 25) = 50». ¿Dónde está el error?",
            "options": [
                {
                    "id": "too_big",
                    "text": "50 pasa de 25: el MCD nunca supera al número menor. Es 5",
                },
                {"id": "arith", "text": "Se equivocó: el MCD es 10"},
                {"id": "coprime", "text": "No tienen divisores comunes: es 1"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "too_big",
            "feedback_by_option": {
                "too_big": "correct",
                "arith": "fb_c05_e4_arith",
                "coprime": "fb_c05_e4_coprime",
                "none": "fb_c05_e4_none",
            },
            "misconception_by_option": {
                "arith": "mcd_es_el_mayor_de_los_numeros",
                "coprime": "no_busca_divisores_comunes",
                "none": "confunde_mcd_con_mcm",
            },
            "hints": {
                "n1": "Antes de calcular nada: ¿puede un divisor de 10 valer 50?",
                "n2": "El MCD tiene que dividir al 10, así que no pasa de 10.",
                "n3": "Los divisores comunes de 10 y 25 son 1 y 5.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «El MCD de dos números siempre es uno de los dos números.»",
            "options": [
                {
                    "id": "false_unless",
                    "text": "Falsa: solo si uno divide al otro, como MCD(15,45) = 15",
                },
                {"id": "true", "text": "Verdadera: siempre es el mayor de los dos"},
                {"id": "false_never", "text": "Falsa: nunca puede ser uno de ellos"},
                {"id": "true_smaller", "text": "Verdadera: siempre es el menor de los dos"},
            ],
            "expected": "false_unless",
            "feedback_by_option": {
                "false_unless": "correct",
                "true": "fb_c05_e5_trap",
                "false_never": "fb_c05_e5_never",
                "true_smaller": "fb_c05_e5_smaller",
            },
            "misconception_by_option": {
                "true": "mcd_es_el_mayor_de_los_numeros",
                "false_never": "olvida_el_caso_de_divisibilidad",
                "true_smaller": "mcd_es_siempre_el_menor",
            },
            "hints": {
                "n1": "Busca un par donde el MCD no sea ninguno de los dos.",
                "n2": "Prueba con 48 y 36: el MCD es 12.",
                "n3": "¿Y hay algún par donde SÍ lo sea? Prueba 15 y 45.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODOS los pares que son coprimos (MCD = 1).",
            "valid_options": ["p1", "p2", "p3", "p4"],
            "options": [
                {"id": "p1", "text": "8 y 15"},
                {"id": "p2", "text": "6 y 9"},
                {"id": "p3", "text": "7 y 13"},
                {"id": "p4", "text": "12 y 18"},
            ],
            "expected": ["p1", "p3"],
            "trap_options": ["p2", "p4"],
            "hints": {
                "n1": "Coprimos quiere decir que no comparten ningún primo.",
                "n2": "8 = 2³ y 15 = 3 × 5: nada en común.",
                "n3": "6 y 9 comparten el 3; 12 y 18 comparten 2 y 3.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Dos cargamentos, de 54 y 72 piezas, se guardan en cofres iguales sin que "
                "sobre nada. ¿Cuántas piezas lleva el cofre más grande posible?"
            ),
            "expr": r"\text{MCD}(54,72)",
            "answer": "18",
            "hints": {
                "n1": "Descompón los dos.",
                "n2": "54 = 2 × 3³ y 72 = 2³ × 3².",
                "n3": "Comunes con exponente menor: 2 × 3² = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Casos que conviene reconocer de un vistazo",
        "title": "¿El MCD es uno de los dos números?",
        "intro": "Cinco situaciones que aparecen todo el tiempo y una que hay que descartar siempre.",
        "rows": [
            {
                "symbol": r"(48,36)",
                "name": "Caso general",
                "closed": "no",
                "latex": r"\text{MCD}=12",
                "note": "Ninguno de los dos. Hay que calcularlo: comunes con exponente menor.",
            },
            {
                "symbol": r"(15,45)",
                "name": "Uno divide al otro",
                "closed": "yes",
                "latex": r"15\mid 45\ \Rightarrow\ \text{MCD}=15",
                "note": "El MCD es el pequeño. Compruébalo siempre primero: ahorra todo el trabajo.",
            },
            {
                "symbol": r"(7,13)",
                "name": "Coprimos",
                "closed": "no",
                "latex": r"\text{MCD}=1",
                "note": "No comparten primos. Dos primos distintos siempre son coprimos.",
            },
            {
                "symbol": r"(a,a)",
                "name": "El mismo dos veces",
                "closed": "yes",
                "latex": r"\text{MCD}(a,a)=a",
                "note": "Comparten todo. Caso extremo del anterior.",
            },
            {
                "symbol": r"(n,1)",
                "name": "Con el uno",
                "closed": "yes",
                "latex": r"\text{MCD}(n,1)=1",
                "note": "El 1 divide a todo y no tiene más divisores: el MCD es 1, que aquí sí es uno de los dos.",
            },
            {
                "symbol": r"(n,0)",
                "name": "Con el cero",
                "closed": "yes",
                "latex": r"\text{MCD}(n,0)=n",
                "note": "Todo divide al 0 (C02), así que los comunes son los de n y el mayor es n.",
            },
        ],
        "outro": (
            "Dos comprobaciones antes de calcular: ¿uno divide al otro? ¿comparten algún "
            "primo? Y un techo que nunca falla: el MCD no puede pasar del número menor. En "
            "Esparta vas a hacer la pregunta contraria."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"\text{MCD}(48,36)", r"\text{MCD}(25,12)", r"\text{MCD}(48,36)=48?"],
        "options": [
            {
                "id": "intersection",
                "text": "En los tres se busca algo que esté en las DOS listas de divisores",
                "correct": True,
            },
            {
                "id": "ceiling",
                "text": "En los tres el resultado no puede pasar del número menor",
                "correct": True,
            },
            {
                "id": "biggest",
                "text": "En los tres el resultado es el mayor de los dos números",
                "correct": False,
            },
            {"id": "always_one", "text": "En los tres el resultado es 1", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Llegan dos cargamentos, de 84 y 126 piezas. Hay que guardarlos en cofres "
            "iguales, sin mezclar y sin que sobre nada, usando el cofre más grande posible. "
            "¿De cuántas piezas es ese cofre?"
        ),
        "polya": {
            "comprender": "Busco el mayor número que divida a 84 y a 126 a la vez.",
            "planear": "Compruebo primero si 84 divide a 126; si no, descompongo los dos y cojo los primos comunes con exponente menor.",
            "ejecutar": "126 ÷ 84 no es exacto. 84 = 2²×3×7 y 126 = 2×3²×7 → comunes: 2¹, 3¹, 7¹ → 2×3×7 = 42.",
            "comprobar": "84 ÷ 42 = 2 ✓ y 126 ÷ 42 = 3 ✓. Y 42 ≤ 84, así que respeta el techo.",
        },
        "prompt": "¿De cuántas piezas es el cofre?",
        "answer": "42",
        "hints": {
            "n1": "Descompón los dos números en primos.",
            "n2": "84 = 2² × 3 × 7 y 126 = 2 × 3² × 7.",
            "n3": "Comunes con el exponente menor: 2 × 3 × 7 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya lees la C de «común» antes de responder.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el MCD no "
            "puede pasar del número más pequeño."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es el mayor número que divide a la vez a 20 y a 30?",
                "answer": "10",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale el MCD de $9$ y $21$?",
                "options": [
                    {"id": "three", "text": "3", "latex": r"3"},
                    {"id": "twentyone", "text": "21", "latex": r"21"},
                    {"id": "product", "text": "189", "latex": r"189"},
                ],
                "expected": "three",
                "misconception_by_option": {
                    "twentyone": "mcd_es_el_mayor_de_los_numeros",
                    "product": "confunde_mcd_con_producto",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale el MCD de $6$ y $30$?",
                "options": [
                    {"id": "six", "text": "6: el menor divide al mayor"},
                    {"id": "thirty", "text": "30"},
                    {"id": "one", "text": "1"},
                ],
                "expected": "six",
                "misconception_by_option": {
                    "thirty": "mcd_es_el_mayor_de_los_numeros",
                    "one": "sobregeneraliza_mcd",
                },
                # Caso donde el MCD SÍ es uno de los dos: comprueba que aprendió
                # el criterio y no la heurística "nunca es ninguno de ellos".
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
        "default": "Comprueba el techo: el MCD no puede pasar del número más pequeño.",
        "fb_c05_e4_arith": (
            "10 sí divide a 10, pero no divide a 25: 25 ÷ 10 no es entero. → Busca los "
            "divisores comunes de los dos."
        ),
        "fb_c05_e4_coprime": (
            "Sí comparten algo: los dos son múltiplos de 5. → Escribe los divisores comunes."
        ),
        "fb_c05_e4_none": (
            "50 no divide ni a 10 ni a 25. → Di cuál es el mayor número que divide a los dos."
        ),
        "fb_c05_e5_trap": (
            "Con 48 y 36 el MCD es 12, que no es ninguno de los dos. → Comprueba ese caso."
        ),
        "fb_c05_e5_never": ("Casi: hay un caso donde sí lo es. → Calcula MCD(15, 45)."),
        "fb_c05_e5_smaller": (
            "El menor solo es la respuesta si divide al mayor. → Calcula MCD(48, 36) y "
            "compáralo con 36."
        ),
    },
    "closing": (
        "Máximo, COMÚN, divisor: las tres palabras cuentan, y el techo es siempre el número "
        "menor. Con las mismas piezas de Mileto, en Esparta vas a resolver la pregunta "
        "opuesta: cuándo vuelven a coincidir dos ritmos."
    ),
    "validation_status": "F4_C05_11bloques",
}
