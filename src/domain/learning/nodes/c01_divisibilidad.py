"""C01 · Divisibilidad — «divide a» no es lo mismo que «se divide entre».

Destino del nodo: CORINTO · el reparto exacto. Contexto propio: el cordelero del
muelle (maromas cortadas en tramos iguales, sin desperdicio).
"""

NODE_ID = "PREALG-N4-C01-DIVISIBILIDAD"
CONCEPT_SLUG = "divisibilidad"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "divisibilidad",
    "misconception": "invierte_la_direccion_de_la_divisibilidad",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "Corinto · Divisibilidad",
    "destination": "Corinto · el reparto exacto",
    "finish_label": "Zarpar hacia Rodas",
    "title": "«Divide a» no es lo mismo que «se divide entre»",
    "intro": (
        "Toda división se puede hacer. Lo que no siempre se puede es hacerla SIN QUE "
        "SOBRE. Aquí vas a aprender a decidirlo sin dividir, con criterios que se leen "
        "de un vistazo, y a no invertir la frase — que es donde casi todo el mundo tropieza."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de bajar al muelle. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Una maroma de 36 codos se corta en tramos de 4 codos. ¿Cuántos tramos salen?",
                "answer": "9",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál de estas frases es verdadera?",
                "options": [
                    {"id": "three_div_12", "text": "3 divide a 12", "latex": r"3\mid 12"},
                    {"id": "twelve_div_3", "text": "12 divide a 3", "latex": r"12\mid 3"},
                    {"id": "both", "text": "Las dos"},
                ],
                "expected": "three_div_12",
                "misconception_by_option": {
                    "twelve_div_3": "invierte_la_direccion_de_la_divisibilidad",
                    "both": "invierte_la_direccion_de_la_divisibilidad",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cómo sabes si un número es divisible entre 2 sin dividir?",
                "options": [
                    {"id": "last_even", "text": "Mirando si termina en cifra par"},
                    {"id": "sum", "text": "Sumando sus cifras"},
                    {"id": "cannot", "text": "No se puede saber sin dividir"},
                ],
                "expected": "last_even",
                "misconception_by_option": {
                    "sum": "confunde_criterio_de_2_con_el_de_3",
                    "cannot": "no_conoce_criterios",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el muelle de Corinto",
        "title": "El cordelero que cortó de más",
        "body": (
            "En el muelle de Corinto trabaja un cordelero. Las maromas le llegan en piezas "
            "largas y él las corta en tramos iguales para los aparejos de cada barco. La "
            "regla del gremio es dura: un tramo corto sobrante no se vende, se tira.\n\n"
            "Esta mañana le pidieron tramos de 6 codos de una maroma de 92. El cordelero "
            "miró el 92, vio que era par, dijo «6 también es par, esto sale exacto» y "
            "cortó. Le sobraron 2 codos que fueron a la basura."
        ),
        "question": "¿Cómo se sabe, antes de cortar, si el reparto va a salir sin desperdicio?",
        "image": "/leccion/04-prealg-n4-puerto/c01-divisibilidad-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Si los dos son pares, sale exacto"},
                {"id": "b", "text": "Solo dividiendo y viendo si sobra"},
                {"id": "c", "text": "Hay señales en el número que lo dicen antes"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decidirlo de un vistazo "
                "para 2, 3, 4, 5, 9 y 10."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos maromas, dos finales distintos",
        "body": (
            "Abajo, dos cortes con la misma medida de tramo. Fíjate en qué queda al final "
            "de cada maroma."
        ),
        "cases": [
            {
                "label": "Caso que funciona",
                "context": "Maroma de 96 codos, tramos de 6",
                "fraction": r"96\div 6",
                "division": r"96=6\times 16,\ \text{residuo }0",
                "note": "No sobra nada. Se dice: 6 divide a 96.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Maroma de 92 codos, los mismos tramos de 6",
                "fraction": r"92\div 6",
                "division": r"92=6\times 15+2,\ \text{residuo }2",
                "note": "Sobran 2 codos. La división existe, pero 6 NO divide a 92.",
            },
        ],
        "resolution": (
            "Las dos divisiones se pueden hacer; la diferencia está en el residuo. Que los "
            "dos números sean pares no basta: 92 y 6 lo son y aun así sobra. La "
            "divisibilidad no es una propiedad de un número suelto, es una relación entre "
            "dos, y tiene DIRECCIÓN."
        ),
    },
    "definition_title": "La divisibilidad",
    "definition_katex": r"b\mid a\iff\exists\,k\in\mathbb{Z}:\ a=b\times k",
    "definition": (
        "b divide a a (se escribe b | a) si existe un entero k tal que a = b × k; es decir, "
        "si la división a ÷ b tiene residuo 0. El divisor es el pequeño y el múltiplo es el "
        "grande: la frase no se puede dar vuelta."
    ),
    "definition_symbols": [
        {
            "symbol": r"b\mid a",
            "reads": "b divide a a",
            "means": "b es el tramo, a es la maroma entera",
        },
        {"symbol": r"b\nmid a", "reads": "b no divide a a", "means": "el corte deja desperdicio"},
        {
            "symbol": r"k",
            "reads": "el cociente",
            "means": "cuántos tramos salen; tiene que ser entero",
        },
        {
            "symbol": r"r=0",
            "reads": "residuo cero",
            "means": "la marca de que el reparto fue exacto",
        },
        {
            "symbol": r"b\mid a\ \Rightarrow\ b\le a",
            "reads": "el divisor no supera al múltiplo",
            "means": "para a positivo: por eso 12 no divide a 3",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Criterios de un vistazo",
            "title": "Decidir sin dividir",
            "statement": (
                "El cordelero tiene una maroma de 1 350 codos. ¿Puede cortarla en tramos "
                "de 2? ¿De 5? ¿De 3? ¿De 9?"
            ),
            "latex": r"1350",
            "image_slot": False,
            "steps": [
                "Entre 2: miro la última cifra. Es 0, que es par → sí.",
                "Entre 5: la última cifra es 0 o 5. Es 0 → sí.",
                "Entre 3: sumo las cifras. 1+3+5+0 = 9, y 9 es múltiplo de 3 → sí.",
                "Entre 9: la misma suma, 9, ¿es múltiplo de 9? Sí → sí.",
                "Cuatro respuestas sin hacer ni una división. Los criterios de 2, 5 y 10 miran el final; los de 3 y 9 miran la suma.",
            ],
            "solution": r"$1350$ es divisible entre 2, 3, 5 y 9",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se suman las cifras para el 3, pero para el 2 bastaba mirar la última. ¿Por qué unos criterios miran el final y otros la suma?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · La dirección importa",
            "title": "Quién divide a quién",
            "statement": (
                "El registro del muelle dice «7 y 42». ¿Cuál de los dos divide al otro, y "
                "cómo se comprueba?"
            ),
            "latex": r"7\mid 42",
            "image_slot": False,
            "steps": [
                "Pruebo 7 | 42: ¿existe un entero k con 42 = 7 × k? Sí, k = 6.",
                "Pruebo 42 | 7: ¿existe un entero k con 7 = 42 × k? Tendría que ser k = 1/6, que no es entero.",
                "Así que 7 divide a 42, pero 42 no divide a 7.",
                "La comprobación rápida: para números positivos, el divisor nunca es mayor que el múltiplo.",
                "En una maroma: el tramo cabe en la cuerda, no la cuerda en el tramo.",
            ],
            "solution": r"$7\mid 42$ (con $k=6$), pero $42\nmid 7$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que dio vuelta la frase",
            "statement": (
                "El escriba del muelle anota: «El barco trae 8 fardos y cada fardo pesa 24 "
                "minas. Como 24 ÷ 8 = 3 sale exacto, escribo que 24 divide a 8»."
            ),
            "latex": r"24\mid 8",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\underline{24}\mid 8",
            "error_note": "La cuenta 24 ÷ 8 = 3 es correcta; lo que está al revés es la frase que escribió a partir de ella.",
            "correct_version": {
                "wrong_latex": r"24\mid 8",
                "right_latex": r"8\mid 24",
                "rows": [
                    {
                        "wrong": "«24 dividido entre 8» se escribe 24 | 8",
                        "right": "24 ÷ 8 exacto se escribe 8 | 24: divide el pequeño",
                    },
                    {
                        "wrong": "La barra vertical se lee igual que la de dividir",
                        "right": "b | a se lee «b divide a a», no «b dividido entre a»",
                    },
                ],
            },
            "explain_prompt": "Escribe la afirmación correcta y di qué entero k la justifica.",
            "steps": [
                "Comprueba con la definición: 24 | 8 querría decir que existe k con 8 = 24 × k.",
                "Ese k tendría que ser 1/3, que no es entero. Falso.",
                "Lo verdadero es 8 | 24, con k = 3: 24 = 8 × 3.",
            ],
            "solution": (
                "La barra de dividir y la barra de dividir A no son la misma. En a ÷ b el "
                "grande va primero; en b | a el pequeño va primero. Léela siempre en voz "
                "alta: «b divide a a»."
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
                "statement": "Una maroma de 84 codos se corta en tramos de 4.",
                "given_steps": [
                    r"84\div 4",
                    r"\text{últimas dos cifras: }84,\ \text{y }84=4\times 21",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{tramos que salen}=", "answer": "21"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "¿Es 738 divisible entre 9? Usa el criterio de la suma de cifras.",
                "given_steps": [
                    r"7+3+8",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"7+3+8=", "answer": "18"},
                    {"id": "P2-b2", "label": r"18\div 9=", "answer": "2"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: una maroma de 145 codos se corta en tramos de 6. "
                    "¿Cuántos codos se desperdician?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"145=6\times 24+r,\ r=", "answer": "1"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para decidir lo mismo",
        "intro": r"¿Es $2\,346$ divisible entre 6? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Dividir y mirar el residuo",
                "steps": [r"2346\div 6", r"6\times 391=2346", r"r=0\ \Rightarrow\ \text{sí}"],
                "note": "Siempre funciona, pero hay que hacer la división entera.",
            },
            {
                "label": "Método 2 · Descomponer el 6",
                "steps": [
                    r"6=2\times 3",
                    r"2346\text{ termina en }6\ \Rightarrow\ \text{divisible entre }2",
                    r"2+3+4+6=15\ \Rightarrow\ \text{divisible entre }3",
                ],
                "note": "Dos criterios de un vistazo en vez de una división larga.",
            },
        ],
        "question": "¿Y si el número fuera 2 344? ¿Y por qué NO vale descomponer el 8 como 2 × 4 y aplicar los dos criterios?",
        "insight": (
            "El método 2 vale porque 2 y 3 no comparten divisores: son coprimos. Con "
            "8 = 2 × 4 falla, porque 2 y 4 sí comparten el 2 — el número 12 pasa los dos "
            "criterios y no es divisible entre 8. Esa condición de «no compartir divisores» "
            "es lo que vas a formalizar en Atenas con el MCD (C05)."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una maroma de 72 codos se corta en tramos de 8. ¿Cuántos tramos salen?",
            "expr": r"72\div 8",
            "answer": "9",
            "hints": {
                "n1": "Busca el entero k con 72 = 8 × k.",
                "n2": "8 × 8 = 64, se queda corto.",
                "n3": "8 × 9 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una maroma de 100 codos se corta en tramos de 7. ¿Cuántos codos se desperdician?",
            "expr": r"100=7\times k+r",
            "answer": "2",
            "hints": {
                "n1": "Busca el mayor múltiplo de 7 que no pase de 100.",
                "n2": "7 × 14 = 98.",
                "n3": "100 − 98 = …",
            },
        },
        {
            "id": "E3",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODOS los que dividen a 540.",
            "valid_options": ["two", "three", "four", "five", "seven", "nine"],
            "options": [
                {"id": "two", "text": "2"},
                {"id": "three", "text": "3"},
                {"id": "four", "text": "4"},
                {"id": "five", "text": "5"},
                {"id": "seven", "text": "7"},
                {"id": "nine", "text": "9"},
            ],
            "expected": ["two", "three", "four", "five", "nine"],
            "trap_options": ["seven"],
            "hints": {
                "n1": "Aplica un criterio por candidato en vez de dividir seis veces.",
                "n2": "Suma de cifras: 5+4+0 = 9. Eso decide el 3 y el 9.",
                "n3": "Para el 4, mira las dos últimas cifras: 40. Y el 7 no tiene criterio corto: divide.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un escriba anota «15 divide a 5, porque 15 ÷ 5 = 3». ¿Dónde está el error?",
            "options": [
                {"id": "direction", "text": "Dio vuelta la frase: lo correcto es 5 divide a 15"},
                {"id": "arith", "text": "Se equivocó: 15 ÷ 5 no da 3"},
                {"id": "not_exact", "text": "La división no es exacta, sobra algo"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "direction",
            "feedback_by_option": {
                "direction": "correct",
                "arith": "fb_c01_e4_arith",
                "not_exact": "fb_c01_e4_exact",
                "none": "fb_c01_e4_none",
            },
            "misconception_by_option": {
                "arith": "error_de_calculo_no_de_direccion",
                "not_exact": "confunde_residuo_con_direccion",
                "none": "invierte_la_direccion_de_la_divisibilidad",
            },
            "hints": {
                "n1": "La cuenta está bien; lo que falla es cómo la escribió.",
                "n2": "«15 divide a 5» querría decir que 5 = 15 × k con k entero.",
                "n3": "Ese k sería 1/3. En b | a, el pequeño va primero.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Si $a$ y $b$ son los dos pares, entonces $b$ divide a $a$.»",
            "options": [
                {"id": "false_counter", "text": "Falsa: 92 y 6 son pares y 6 no divide a 92"},
                {"id": "true", "text": "Verdadera: dos pares siempre se reparten exacto"},
                {"id": "false_never", "text": "Falsa: dos pares nunca se dividen exacto"},
                {"id": "true_if_bigger", "text": "Verdadera si a es mayor que b"},
            ],
            "expected": "false_counter",
            "feedback_by_option": {
                "false_counter": "correct",
                "true": "fb_c01_e5_trap",
                "false_never": "fb_c01_e5_never",
                "true_if_bigger": "fb_c01_e5_bigger",
            },
            "misconception_by_option": {
                "true": "paridad_implica_divisibilidad",
                "false_never": "niega_toda_divisibilidad_entre_pares",
                "true_if_bigger": "paridad_implica_divisibilidad",
            },
            "hints": {
                "n1": "Para tumbar un «entonces» basta UN contraejemplo.",
                "n2": "Vuelve a la maroma del cordelero.",
                "n3": "92 ÷ 6 deja residuo 2, y los dos números son pares.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": "¿Cuál de estos números es divisible entre 6?",
            "options": [
                {"id": "n234", "text": "234"},
                {"id": "n232", "text": "232"},
                {"id": "n235", "text": "235"},
                {"id": "n239", "text": "239"},
            ],
            "expected": "n234",
            "feedback_by_option": {
                "n234": "correct",
                "n232": "fb_c01_e6_only2",
                "n235": "fb_c01_e6_odd",
                "n239": "fb_c01_e6_odd",
            },
            "misconception_by_option": {
                "n232": "olvida_uno_de_los_dos_criterios",
                "n235": "ignora_el_criterio_de_2",
                "n239": "ignora_el_criterio_de_2",
            },
            "hints": {
                "n1": "6 = 2 × 3: hay que pasar los DOS criterios.",
                "n2": "Descarta primero los impares.",
                "n3": "De los pares que quedan, suma las cifras y mira cuál da múltiplo de 3.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El cordelero tiene una maroma de 203 codos y quiere tramos de 5. "
                "¿Cuántos codos van a la basura?"
            ),
            "expr": r"203=5\times k+r",
            "answer": "3",
            "hints": {
                "n1": "El criterio del 5 mira la última cifra: 3 no es ni 0 ni 5, así que va a sobrar.",
                "n2": "El mayor múltiplo de 5 que no pasa de 203 es 200.",
                "n3": "203 − 200 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Los criterios, uno por uno",
        "title": "¿Basta mirar el final del número?",
        "intro": (
            "Los criterios no son magia ni hay que memorizarlos sueltos: se agrupan en dos "
            "familias según dónde hay que mirar."
        ),
        "rows": [
            {
                "symbol": r"2",
                "name": "Entre 2",
                "closed": "yes",
                "latex": r"1350\to 0\ \text{par}",
                "note": "Basta la última cifra: 0, 2, 4, 6 u 8.",
            },
            {
                "symbol": r"5",
                "name": "Entre 5",
                "closed": "yes",
                "latex": r"1350\to 0",
                "note": "Basta la última cifra: 0 o 5.",
            },
            {
                "symbol": r"10",
                "name": "Entre 10",
                "closed": "yes",
                "latex": r"1350\to 0",
                "note": "Basta la última cifra: 0. Es el criterio de 2 y el de 5 a la vez.",
            },
            {
                "symbol": r"4",
                "name": "Entre 4",
                "closed": "partial",
                "latex": r"1350\to 50,\ 50\div 4\ \text{no exacto}",
                "note": "No basta la última: hay que mirar las DOS últimas. Aquí falla.",
            },
            {
                "symbol": r"3",
                "name": "Entre 3",
                "closed": "no",
                "latex": r"1+3+5+0=9",
                "note": "Hay que sumar TODAS las cifras y ver si la suma es múltiplo de 3.",
            },
            {
                "symbol": r"9",
                "name": "Entre 9",
                "closed": "no",
                "latex": r"1+3+5+0=9",
                "note": "La misma suma, pero exigiendo múltiplo de 9. Todo divisible entre 9 lo es entre 3, no al revés.",
            },
        ],
        "outro": (
            "Dos familias: los que miran el final (2, 5, 10 y, con dos cifras, el 4) y los "
            "que suman (3 y 9). Para el resto se divide y punto. En Rodas vas a mirar la "
            "misma relación desde el otro lado: no quién divide, sino qué se repite."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"96=6\times 16", r"92=6\times 15+2", r"8\mid 24"],
        "options": [
            {"id": "remainder", "text": "En los tres lo que decide es el residuo", "correct": True},
            {"id": "exact", "text": "En los tres el reparto sale exacto", "correct": False},
            {
                "id": "relation",
                "text": "En los tres se relacionan DOS números, no uno solo",
                "correct": True,
            },
            {"id": "even", "text": "En los tres los números son pares", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Llega al muelle una maroma de 918 codos. El cordelero quiere el tramo más "
            "largo posible entre 2, 3, 4, 5 y 9 que no deje desperdicio. ¿Cuál elige?"
        ),
        "polya": {
            "comprender": "Tengo 918 y cinco tramos candidatos. Quiero el mayor que divida exacto.",
            "planear": "Aplico el criterio de cada uno, de mayor a menor, y me quedo con el primero que pase.",
            "ejecutar": "9: 9+1+8 = 18, múltiplo de 9 → pasa. Ya puedo parar: es el mayor de la lista.",
            "comprobar": "918 ÷ 9 = 102, exacto. Y compruebo que el 5 y el 4 fallaban: termina en 8 (no 0 ni 5) y 18 no es múltiplo de 4.",
        },
        "prompt": "¿Qué tramo elige el cordelero?",
        "answer": "9",
        "hints": {
            "n1": "Empieza por el candidato más grande y baja.",
            "n2": "Para el 9, suma las cifras: 9 + 1 + 8.",
            "n3": "18 es múltiplo de 9.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya escribes la divisibilidad en la dirección correcta.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre "
            "«b divide a a» y «a dividido entre b»."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Una maroma de 56 codos se corta en tramos de 7. ¿Cuántos tramos salen?",
                "answer": "8",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál de estas frases es verdadera?",
                "options": [
                    {"id": "five_div_20", "text": "5 divide a 20", "latex": r"5\mid 20"},
                    {"id": "twenty_div_5", "text": "20 divide a 5", "latex": r"20\mid 5"},
                    {"id": "both", "text": "Las dos"},
                ],
                "expected": "five_div_20",
                "misconception_by_option": {
                    "twenty_div_5": "invierte_la_direccion_de_la_divisibilidad",
                    "both": "invierte_la_direccion_de_la_divisibilidad",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cómo sabes si un número es divisible entre 3 sin dividir?",
                "options": [
                    {
                        "id": "sum",
                        "text": "Sumando sus cifras y viendo si la suma es múltiplo de 3",
                    },
                    {"id": "last", "text": "Mirando la última cifra"},
                    {"id": "cannot", "text": "No se puede saber sin dividir"},
                ],
                "expected": "sum",
                "misconception_by_option": {
                    "last": "confunde_criterio_de_2_con_el_de_3",
                    "cannot": "no_conoce_criterios",
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
        "default": "Comprueba el residuo antes de decidir, y lee «b divide a a» en voz alta.",
        "fb_c01_e4_arith": (
            "15 ÷ 5 = 3 está bien. → Fíjate en cuál de los dos números va primero al escribir b | a."
        ),
        "fb_c01_e4_exact": (
            "La división sí es exacta: no sobra nada. → El problema es el orden en que escribió los números."
        ),
        "fb_c01_e4_none": (
            "«15 divide a 5» querría decir que 5 es múltiplo de 15. → Di si 5 puede ser múltiplo de 15."
        ),
        "fb_c01_e5_trap": ("Eso es lo que le costó 2 codos al cordelero. → Prueba con 92 y 6."),
        "fb_c01_e5_never": (
            "Te pasaste: 96 y 6 son pares y sí sale exacto. → Da un caso donde funcione y otro donde no."
        ),
        "fb_c01_e5_bigger": (
            "92 es mayor que 6 y aun así sobra. → Calcula 92 ÷ 6 y mira el residuo."
        ),
        "fb_c01_e6_only2": (
            "232 sí pasa el criterio del 2, pero le falta el del 3: 2+3+2 = 7. → Busca el "
            "que pase los dos."
        ),
        "fb_c01_e6_odd": (
            "Ese número es impar, así que ni siquiera pasa el criterio del 2. → Descarta los "
            "impares primero."
        ),
    },
    "closing": (
        "Divisible es residuo cero, y la relación tiene dirección: divide el pequeño. Los "
        "criterios se agrupan en los que miran el final y los que suman cifras. En Rodas "
        "vas a mirar la misma relación desde el otro lado."
    ),
    "validation_status": "F4_C01_11bloques",
}
