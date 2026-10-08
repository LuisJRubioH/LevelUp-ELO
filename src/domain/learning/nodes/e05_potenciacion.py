"""E05 · Potenciación — el exponente cuenta factores, no sumandos.

Edificio del nodo: EL INVERNADERO (esquejes que se duplican, bandejas de
germinación, el registro diario del vivero). Ningún otro edificio usa este oficio.
"""

NODE_ID = "PREALG-N2-E05-POTENCIACION-CRECER"
CONCEPT_SLUG = "potenciacion"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "potenciacion",
    "misconception": "potencia_es_multiplicar_por_el_exponente",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El Invernadero · Potenciación",
    "building": "El Invernadero",
    "finish_label": "Salir hacia la Cantera",
    "title": "El exponente cuenta factores, no sumandos",
    "intro": (
        "Aquí dentro nada crece sumando: cada día multiplica al anterior. Vas a ver "
        "qué dice exactamente el número pequeño de arriba, por qué 2³ no es 6, y hasta "
        "dónde llega esta operación cuando el exponente deja de ser un número de contar."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar al invernadero. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $2^{3}$?",
                "answer": "8",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Qué significa $5^{2}$?",
                "options": [
                    {
                        "id": "factor",
                        "text": "5 multiplicado por sí mismo 2 veces",
                        "latex": r"5\times 5",
                    },
                    {"id": "sum", "text": "5 sumado 2 veces", "latex": r"5+5"},
                    {"id": "product", "text": "5 multiplicado por 2", "latex": r"5\times 2"},
                ],
                "expected": "factor",
                "misconception_by_option": {
                    "sum": "potencia_es_suma_repetida",
                    "product": "potencia_es_multiplicar_por_el_exponente",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Un esqueje se duplica cada día. Si hoy hay 1, ¿cuántos habrá en 4 días?",
                "options": [
                    {"id": "sixteen", "text": "16", "latex": r"2^{4}"},
                    {"id": "eight", "text": "8", "latex": r"2^{3}"},
                    {"id": "four", "text": "4"},
                    {"id": "two_four", "text": "2 × 4 = 8"},
                ],
                "expected": "sixteen",
                "misconception_by_option": {
                    "eight": "cuenta_mal_los_pasos",
                    "four": "crecimiento_lineal",
                    "two_four": "potencia_es_multiplicar_por_el_exponente",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · Dentro del Invernadero",
        "title": "El esqueje que se comió la bandeja",
        "body": (
            "El quinto edificio es el Invernadero: techo de vidrio, bandejas de "
            "germinación en filas y un registro colgado en la puerta donde el jardinero "
            "anota cada mañana cuántos esquejes hay. La variedad que cultivan tiene una "
            "particularidad — cada día se duplica sola.\n\n"
            "El aprendiz calculó el encargo así: «Un esqueje que se duplica durante 10 "
            "días son 2 por 10, o sea 20 esquejes. Cabe de sobra en una bandeja». Pidió "
            "una bandeja. Al décimo día tuvieron que abrir un ala nueva del invernadero."
        ),
        "question": "Un esqueje que se duplica cada día, ¿cuántos son al décimo día?",
        "image": "/leccion/02-prealg-n2-mercado/e05-potenciacion-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "20: es 2 por 10 días"},
                {"id": "b", "text": "Unos cientos"},
                {"id": "c", "text": "Más de mil"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final del nodo vas a poder decir el "
                "número exacto y explicar por qué el aprendiz se quedó tan corto."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos registros del invernadero, dos crecimientos",
        "body": (
            "Las dos bandejas de abajo arrancan igual y crecen distinto. Mira cuánto "
            "aporta cada día en cada una."
        ),
        "cases": [
            {
                "label": "Caso que ya conoces",
                "context": "Bandeja A: el jardinero añade 2 esquejes cada día durante 10 días",
                "fraction": r"2\times 10",
                "division": r"2\times 10=20",
                "note": "Cada día aporta lo mismo: 2. Es multiplicación.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Bandeja B: el esqueje se duplica solo cada día durante 10 días",
                "fraction": r"2^{10}",
                "division": r"2^{10}=1024",
                "note": "Cada día aporta tanto como TODO lo acumulado. Es potenciación.",
            },
        ],
        "resolution": (
            "1024 contra 20: la diferencia no es que un número sea más grande, es que las "
            "dos operaciones cuentan cosas distintas. En la multiplicación el 10 cuenta "
            "SUMANDOS iguales; en la potencia el 10 cuenta FACTORES iguales. El aprendiz "
            "leyó el exponente como si fuera un factor, y se equivocó por más de mil."
        ),
    },
    "definition_title": "La potenciación",
    "definition_katex": r"a^{n}=\underbrace{a\times a\times\cdots\times a}_{n\ \text{factores}}",
    "definition": (
        "Elevar a a la n es multiplicar a por sí mismo n veces. La base dice qué se "
        "repite; el exponente dice cuántas veces se repite como FACTOR. No es a por n."
    ),
    "definition_symbols": [
        {"symbol": r"a", "reads": "base", "means": "el número que se repite"},
        {
            "symbol": r"n",
            "reads": "exponente",
            "means": "cuántas veces aparece la base como factor",
        },
        {"symbol": r"a^{n}", "reads": "potencia", "means": "el resultado"},
        {
            "symbol": r"a^{1}=a",
            "reads": "exponente uno",
            "means": "un solo factor: la base tal cual",
        },
        {
            "symbol": r"a^{0}=1",
            "reads": "exponente cero",
            "means": "ningún factor; el producto vacío es 1, no 0",
        },
        {
            "symbol": r"a^{-n}=\dfrac{1}{a^{n}}",
            "reads": "exponente negativo",
            "means": "invierte la potencia; se sale de ℤ y cae en ℚ",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Naturales",
            "title": "Los diez días de la bandeja B",
            "statement": (
                "Un esqueje que se duplica cada día. ¿Cuántos hay al décimo día, y por qué "
                "no cabía en una bandeja?"
            ),
            "latex": r"2^{10}",
            "image_slot": True,
            "image": "/leccion/02-prealg-n2-mercado/e05-crecimiento-niveles-v4.png",
            "steps": [
                "Día 1: 2. Día 2: 2 × 2 = 4. Día 3: 4 × 2 = 8. Cada día multiplico por 2, no sumo 2.",
                "Al día n hay 2 multiplicado por sí mismo n veces: 2ⁿ.",
                "2¹⁰ = 2×2×2×2×2×2×2×2×2×2. Lo agrupo: 2⁵ = 32, y 2¹⁰ = 32 × 32.",
                "32 × 32 = 1024.",
                "1024 esquejes, no 20. El aprendiz confundió el exponente con un factor.",
            ],
            "solution": r"$2^{10}=1024$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se parte 2¹⁰ en 2⁵ × 2⁵. ¿Por qué se pueden juntar así los exponentes?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Racionales",
            "title": "Cuando el exponente apunta al otro lado",
            "statement": (
                "El registro del invernadero anota hacia atrás: si hoy hay 1 esqueje, "
                "¿cuánto había 3 días antes, cuando aún se duplicaba cada día?"
            ),
            "latex": r"2^{-3}",
            "image_slot": True,
            "image": "/leccion/02-prealg-n2-mercado/e05-exponente-negativo-v4.png",
            "steps": [
                "Ir hacia adelante multiplica por 2; ir hacia atrás hace lo contrario: divide entre 2.",
                "Tres días atrás es dividir tres veces entre 2, y eso se escribe 2⁻³.",
                "2⁻³ = 1 ÷ 2³ = 1/8.",
                "1/8 = 0,125: un octavo de esqueje. No es un esqueje real, pero sí un número.",
                "El exponente negativo no da un número negativo: da el inverso. Y ese inverso ya no es entero.",
            ],
            "solution": r"$2^{-3}=\dfrac{1}{8}=0{,}125$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que multiplicó la base por el exponente",
            "statement": (
                "El aprendiz pide material así: «Necesito 3⁴ macetas. Eso es 3 por 4, o sea "
                "12 macetas»."
            ),
            "latex": r"3^{4}=12",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"3^{4}=3\times\underline{4}",
            "error_note": "El 4 no es un factor: dice CUÁNTOS factores hay. 3×4 es 3 sumado 4 veces, no 3 multiplicado 4 veces.",
            "correct_version": {
                "wrong_latex": r"3^{4}=12",
                "right_latex": r"3^{4}=81",
                "rows": [
                    {
                        "wrong": "El exponente es un factor más",
                        "right": "El exponente cuenta cuántas veces aparece la base",
                    },
                    {"wrong": "3⁴ = 3 × 4", "right": "3⁴ = 3 × 3 × 3 × 3"},
                ],
            },
            "explain_prompt": "¿Por qué 12 no puede ser la respuesta? Escribe la potencia desarrollada y su valor.",
            "steps": [
                "Desarrolla la potencia sin atajos: 3 × 3 × 3 × 3.",
                "3 × 3 = 9, 9 × 3 = 27, 27 × 3 = 81.",
                "81 macetas, casi siete veces más de lo que pidió. La confusión cuesta caro cuando el exponente crece.",
            ],
            "solution": (
                "Un truco para no volver a caer: lee la potencia en voz alta como «tres, "
                "cuatro veces, multiplicándose». Si al leerla dices «por», estás "
                "multiplicando; si dices «veces, como factor», estás elevando."
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
                "statement": "Una bandeja del invernadero tiene 4 filas de 4 macetas, y hay 4 bandejas iguales.",
                "given_steps": [
                    r"4^{3}=4\times 4\times 4",
                    r"4\times 4=16",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"4^{3}=", "answer": "64"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "El registro cuenta hacia atrás dos días desde 1 esqueje.",
                "given_steps": [
                    r"2^{-2}=\dfrac{1}{2^{2}}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"2^{2}=", "answer": "4"},
                    {"id": "P2-b2", "label": r"2^{-2}\text{ en decimal}=", "answer": "0,25"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: un esqueje que se TRIPLICA cada día, empezando "
                    "por uno. ¿Cuántos hay al quinto día?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"3^{5}=", "answer": "243"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma potencia",
        "intro": r"¿Cuánto vale $2^{12}$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar doce veces",
                "steps": [r"2,4,8,16,32,64,\ldots", r"\text{doce pasos}", r"2^{12}=4096"],
                "note": "Siempre funciona, pero doce oportunidades de equivocarse.",
            },
            {
                "label": "Método 2 · Partir el exponente",
                "steps": [r"2^{12}=2^{6}\times 2^{6}", r"2^{6}=64", r"64\times 64=4096"],
                "note": "Dos multiplicaciones en vez de doce.",
            },
        ],
        "question": "¿Cuál usarías para 2²⁰? ¿Y qué regla estás usando sin nombrarla en el método 2?",
        "insight": (
            "El método 2 usa que al multiplicar potencias de la misma base los exponentes "
            "se SUMAN: 2⁶ × 2⁶ = 2⁶⁺⁶ = 2¹². Tiene sentido si vuelves a la definición — seis "
            "factores junto a otros seis factores son doce factores. No es una regla que "
            "haya que memorizar: se lee en el conteo."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una bandeja cuadrada tiene 6 filas de 6 macetas. ¿Cuántas macetas caben?",
            "expr": r"6^{2}",
            "answer": "36",
            "hints": {
                "n1": "El exponente 2 dice cuántas veces aparece el 6 como factor.",
                "n2": "6 × 6.",
                "n3": "6 × 6 = 36, no 6 × 2.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Un esqueje se duplica cada día. Si hoy hay 1, ¿cuántos habrá en 6 días?",
            "expr": r"2^{6}",
            "answer": "64",
            "hints": {
                "n1": "Cada día multiplica por 2, no suma 2.",
                "n2": "2, 4, 8, 16…",
                "n3": "2⁵ = 32, y falta un día más.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"El registro cuenta hacia atrás: ¿cuánto vale $2^{-2}$? (decimal)",
            "expr": r"2^{-2}",
            "answer": "0,25",
            "hints": {
                "n1": "El exponente negativo invierte, no cambia el signo.",
                "n2": "2⁻² = 1 ÷ 2².",
                "n3": "1 ÷ 4 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"El aprendiz anota «$4^{3}=12$». ¿Dónde está el error?",
            "options": [
                {"id": "times", "text": "Multiplicó la base por el exponente; lo correcto es 64"},
                {"id": "sum", "text": "Sumó 4 tres veces"},
                {"id": "swapped", "text": "Cambió base y exponente: quiso decir 3⁴"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "times",
            "feedback_by_option": {
                "times": "correct",
                "sum": "fb_e05_e4_sum",
                "swapped": "fb_e05_e4_swapped",
                "none": "fb_e05_e4_none",
            },
            "misconception_by_option": {
                "sum": "potencia_es_suma_repetida",
                "swapped": "confunde_base_con_exponente",
                "none": "potencia_es_multiplicar_por_el_exponente",
            },
            "hints": {
                "n1": "Desarrolla la potencia antes de juzgar.",
                "n2": "4³ = 4 × 4 × 4.",
                "n3": "4 × 4 = 16, y 16 × 4 = 64.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para todo $a$ y todo $n$: $a^{n}=a\times n$.»",
            "options": [
                {
                    "id": "false_factors",
                    "text": "Falsa: el exponente cuenta factores, no es un factor",
                },
                {"id": "true", "text": "Verdadera: elevar es multiplicar por el exponente"},
                {"id": "false_never", "text": "Falsa: nunca coinciden los dos resultados"},
                {"id": "true_small", "text": "Verdadera si los números son pequeños"},
            ],
            "expected": "false_factors",
            "feedback_by_option": {
                "false_factors": "correct",
                "true": "fb_e05_e5_trap",
                "false_never": "fb_e05_e5_never",
                "true_small": "fb_e05_e5_small",
            },
            "misconception_by_option": {
                "true": "potencia_es_multiplicar_por_el_exponente",
                "false_never": "olvida_el_caso_de_igualdad",
                "true_small": "potencia_es_multiplicar_por_el_exponente",
            },
            "hints": {
                "n1": "Para tumbar un «para todo» basta UN caso.",
                "n2": "Prueba con a = 3 y n = 4.",
                "n3": "3⁴ = 81 y 3 × 4 = 12. ¿Hay algún par donde sí coincidan? Prueba a = 2, n = 2.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Un esqueje se triplica cada día. Si hoy hay 1, ¿cuántos habrá al cuarto día?"
            ),
            "expr": r"3^{4}",
            "answer": "81",
            "hints": {
                "n1": "Triplicarse es multiplicar por 3 cada día.",
                "n2": "3 × 3 = 9.",
                "n3": "9 × 3 = 27, y falta un día.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estas potencias de base y exponente enteros SE SALE de los enteros?",
            "options": [
                {"id": "neg_exp", "text": "2 elevado a -1", "latex": r"2^{-1}"},
                {"id": "zero_exp", "text": "7 elevado a 0", "latex": r"7^{0}"},
                {"id": "neg_base", "text": "-3 elevado a 2", "latex": r"(-3)^{2}"},
                {"id": "big", "text": "5 elevado a 4", "latex": r"5^{4}"},
            ],
            "expected": "neg_exp",
            "feedback_by_option": {
                "neg_exp": "correct",
                "zero_exp": "fb_e05_e7_stays",
                "neg_base": "fb_e05_e7_stays",
                "big": "fb_e05_e7_stays",
            },
            "misconception_by_option": {
                "zero_exp": "exponente_cero_da_cero",
                "neg_base": "base_negativa_da_no_entero",
                "big": "confunde_grande_con_fuera_del_conjunto",
            },
            "hints": {
                "n1": "Calcula las cuatro y mira cuál no es un entero.",
                "n2": "7⁰ = 1 y (−3)² = 9: los dos son enteros.",
                "n3": "2⁻¹ = 1/2, que es racional pero no entero.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "La escalera de la potenciación",
        "title": "¿La potencia de dos elementos del conjunto vive en el conjunto?",
        "intro": "Esta operación rompe DOS peldaños, y el segundo abre la puerta del nodo siguiente.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "yes",
                "latex": r"2^{10}=1024\in\mathbb{N}",
                "note": "Multiplicar naturales por sí mismos da naturales, por grande que sea.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"2^{-1}=\dfrac{1}{2}\notin\mathbb{Z}",
                "note": "El exponente negativo invierte, y el inverso de un entero casi nunca es entero.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "no",
                "latex": r"2^{1/2}=\sqrt{2}\notin\mathbb{Q}",
                "note": "Con exponente fraccionario la potencia se sale de ℚ. Este es el hueco del que sale la Cantera (E06).",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\left(\sqrt{2}\right)^{2}=2\in\mathbb{Q}",
                "note": "Ni siquiera con exponente natural: el resultado SE SALE. Ninguna operación aritmética cierra 𝕀.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "partial",
                "latex": r"(-4)^{1/2}\notin\mathbb{R}",
                "note": "Cierra con base positiva (π² ∈ ℝ). Se rompe en un solo caso: base negativa con exponente fraccionario, y ahí empieza B09.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"(-4)^{1/2}=2i",
                "note": "El único peldaño donde toda potencia tiene respuesta. Desvío opcional (B09).",
            },
        ],
        "outro": (
            "El agujero de ℚ es el más interesante: 2^(1/2) existe, no es ninguna fracción, y "
            "ya lo conociste como √2 en B07. La operación que lo desentierra se llama "
            "radicación, y se trabaja en la Cantera."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"2^{10}", r"2^{-3}", r"3^{4}"],
        "options": [
            {
                "id": "factors",
                "text": "En los tres el exponente dice cuántas veces aparece la base como factor",
                "correct": True,
            },
            {
                "id": "bigger",
                "text": "En los tres el resultado es mayor que la base",
                "correct": False,
            },
            {
                "id": "repeated",
                "text": "En los tres se repite una misma multiplicación",
                "correct": True,
            },
            {"id": "base_two", "text": "En los tres la base es 2", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El jardinero encarga bandejas para la variedad que se duplica: empieza con 1 "
            "esqueje y quiere saber cuántos habrá al octavo día para pedir el espacio justo."
        ),
        "polya": {
            "comprender": "Parto de 1 esqueje, se duplica cada día, y me piden el número al día 8.",
            "planear": "Es 2⁸. Lo parto en 2⁴ × 2⁴ para no multiplicar ocho veces seguidas.",
            "ejecutar": "2⁴ = 16 → 16 × 16 = 256.",
            "comprobar": "Cuento la sucesión: 2, 4, 8, 16, 32, 64, 128, 256. Ocho pasos, cuadra.",
        },
        "prompt": "¿Cuántos esquejes hay al octavo día?",
        "answer": "256",
        "hints": {
            "n1": "Duplicarse cada día durante 8 días es 2⁸.",
            "n2": "Parte el exponente: 2⁸ = 2⁴ × 2⁴.",
            "n3": "2⁴ = 16, y 16 × 16 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya lees el exponente como un contador de factores.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre "
            "el exponente y un factor."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $3^{3}$?",
                "answer": "27",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Qué significa $6^{2}$?",
                "options": [
                    {
                        "id": "factor",
                        "text": "6 multiplicado por sí mismo 2 veces",
                        "latex": r"6\times 6",
                    },
                    {"id": "product", "text": "6 multiplicado por 2", "latex": r"6\times 2"},
                    {"id": "sum", "text": "6 sumado 2 veces", "latex": r"6+6"},
                ],
                "expected": "factor",
                "misconception_by_option": {
                    "product": "potencia_es_multiplicar_por_el_exponente",
                    "sum": "potencia_es_suma_repetida",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? $2^{2}=2\times 2$",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "sobregeneraliza_potenciacion"},
                # Caso donde a^n y a×n SÍ coinciden: comprueba que aprendió el
                # criterio y no la heurística "potencia nunca es una multiplicación".
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
        "default": "Desarrolla la potencia como producto antes de responder.",
        "fb_e05_e4_sum": (
            "Si hubiera sumado, 4 + 4 + 4 daría 12 también — pero por otro camino. Lo que hizo "
            "fue 4 × 3. → Escribe 4³ desarrollado y calcúlalo."
        ),
        "fb_e05_e4_swapped": (
            "3⁴ = 81 y 4³ = 64: los dos son distintos de 12, así que el problema no es el "
            "orden. → Desarrolla 4³ y compáralo con 12."
        ),
        "fb_e05_e4_none": (
            "Comprueba desarrollando: 4 × 4 × 4. ¿Da 12? → Escribe el producto completo."
        ),
        "fb_e05_e5_trap": (
            "Eso es exactamente lo que hizo el aprendiz de las macetas. → Calcula 3⁴ y 3 × 4 "
            "y compara los dos."
        ),
        "fb_e05_e5_never": (
            "Casi: fallan casi siempre, pero hay un caso donde coinciden. → Prueba con a = 2 y n = 2."
        ),
        "fb_e05_e5_small": (
            "El tamaño no tiene nada que ver: 3⁴ y 3 × 4 son números pequeños y ya difieren "
            "mucho. → Calcula los dos."
        ),
        "fb_e05_e7_stays": (
            "Esa potencia sí da un entero. → Calcula las cuatro y busca la que da una fracción."
        ),
    },
    "closing": (
        "El exponente cuenta factores. Con exponente negativo la potencia se salió de los "
        "enteros; con exponente 1/2 se sale de los racionales, y ese hueco tiene nombre "
        "propio: raíz. Te espera la Cantera."
    ),
    "validation_status": "F2_E05_11bloques",
}
