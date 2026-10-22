"""E03 · Multiplicación — multiplicar no siempre agranda.

Edificio del nodo: EL TALLER DE MOSAICOS (teselas en filas y columnas, copias a
otra escala, teselas rotas al cortar). Ningún otro edificio de N2 usa este oficio.
"""

NODE_ID = "PREALG-N2-E03-MULTIPLICACION-AGRUPAR"
CONCEPT_SLUG = "multiplicacion"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "multiplicacion",
    "misconception": "multiplicar_siempre_agranda",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El Taller de Mosaicos · Multiplicación",
    "building": "El Taller de Mosaicos",
    "finish_label": "Salir hacia el Comedor Comunal",
    "title": "Multiplicar no siempre agranda",
    "intro": (
        "Multiplicar es agrupar: tantas veces tanto. Mientras el multiplicador fue un "
        "número de contar, el resultado siempre creció. Hoy vas a ver qué pasa cuando "
        "ese multiplicador es medio, o es negativo, y por qué la frase «multiplicar "
        "agranda» se cae."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar al taller. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Un mosaico tiene 7 filas de 8 teselas. ¿Cuántas teselas lleva?",
                "answer": "56",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $12\times\dfrac{1}{2}$?",
                "options": [
                    {"id": "six", "text": "6", "latex": r"6"},
                    {"id": "twentyfour", "text": "24", "latex": r"24"},
                    {"id": "twelve_half", "text": "12,5", "latex": r"12{,}5"},
                ],
                "expected": "six",
                "misconception_by_option": {
                    "twentyfour": "multiplicar_siempre_agranda",
                    "twelve_half": "confunde_multiplicar_con_sumar",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si multiplicas un número por otro, ¿el resultado siempre es mayor que el primero?",
                "options": [
                    {"id": "depends", "text": "Depende de por cuánto multipliques"},
                    {"id": "always", "text": "Sí, siempre"},
                    {"id": "only_positive", "text": "Sí, mientras los dos sean positivos"},
                ],
                "expected": "depends",
                "misconception_by_option": {
                    "always": "multiplicar_siempre_agranda",
                    "only_positive": "multiplicar_siempre_agranda",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · Dentro del Taller de Mosaicos",
        "title": "El encargo a media escala",
        "body": (
            "El tercer edificio es el Taller de Mosaicos: mesas largas, cajones de teselas "
            "por color y una bodega al fondo de donde se saca el material. Aquí nadie "
            "cuenta tesela por tesela. El maestro dice «doce hileras de doce» y el "
            "aprendiz ya sabe cuánto pedir: multiplicar es su forma de contar sin contar.\n\n"
            "Esta mañana llegó un encargo distinto: una copia del mosaico grande, pero a "
            "media escala. El aprendiz bajó a la bodega y pidió el doble de teselas. Dijo "
            "que era una multiplicación, y que multiplicar siempre pide más."
        ),
        "question": "Si multiplicas una cantidad por un medio, ¿pides más teselas o menos?",
        "image": "/leccion/02-prealg-n2-mercado/e03-multiplicacion-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Más: toda multiplicación agranda"},
                {"id": "b", "text": "Menos: media escala es la mitad"},
                {"id": "c", "text": "Igual: multiplicar por una fracción no cambia nada"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir exactamente cuándo "
                "una multiplicación agranda y cuándo achica."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo 12, dos resultados opuestos",
        "body": (
            "Abajo hay dos multiplicaciones que arrancan del mismo número. Mira dónde "
            "termina cada una respecto al 12 de partida."
        ),
        "cases": [
            {
                "label": "Caso que confirma lo que esperas",
                "context": "12 hileras de teselas, repetidas 3 veces",
                "fraction": r"12\times 3",
                "division": r"12\times 3=36",
                "note": "36 está por encima de 12: el multiplicador era mayor que 1.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "El mismo mosaico de 12, pero a media escala",
                "fraction": r"12\times\dfrac{1}{2}",
                "division": r"12\times\dfrac{1}{2}=6",
                "note": "6 está por debajo de 12: el multiplicador era menor que 1.",
            },
        ],
        "resolution": (
            "La operación no cambió: en las dos tomé el 12 tantas veces como decía el otro "
            "factor. Lo que decide si crece o se achica no es multiplicar, es si el "
            "multiplicador está por encima o por debajo de 1. «Tres veces» agranda; «media "
            "vez» achica."
        ),
    },
    "definition_title": "La multiplicación",
    "definition_katex": r"a\times b=\underbrace{a+a+\cdots+a}_{b\ \text{veces}}\quad(b\in\mathbb{N})",
    "definition": (
        "Multiplicar es agrupar: tomar la cantidad a tantas veces como diga b. Cuando b "
        "deja de ser un número de contar, «tantas veces» se convierte en «esa parte de», "
        "y ahí es donde el resultado puede achicarse."
    ),
    "definition_symbols": [
        {"symbol": r"a,b", "reads": "factores", "means": "las dos cantidades que se multiplican"},
        {"symbol": r"a\times b", "reads": "producto", "means": "el resultado de agrupar"},
        {
            "symbol": r"b>1",
            "reads": "multiplicador mayor que uno",
            "means": "el producto queda por encima de a",
        },
        {
            "symbol": r"0<b<1",
            "reads": "multiplicador entre cero y uno",
            "means": "el producto queda por debajo de a",
        },
        {
            "symbol": r"a\times 1=a",
            "reads": "multiplicar por uno deja igual",
            "means": "el neutro del producto; lo formaliza N3-M04",
        },
        {
            "symbol": r"a\times 0=0",
            "reads": "todo por cero es cero",
            "means": "cero grupos no dejan nada",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Racionales",
            "title": "El mosaico a media escala",
            "statement": (
                "El mosaico grande lleva 144 teselas. El encargo pide una copia a media "
                "escala en cada lado. ¿Cuántas teselas hay que pedir a la bodega?"
            ),
            "latex": r"144\times\dfrac{1}{2}\times\dfrac{1}{2}",
            "image_slot": False,
            "steps": [
                "Media escala significa la mitad del ancho Y la mitad del alto: dos mitades, no una.",
                "144 × 1/2 = 72: así queda si solo se reduce un lado.",
                "72 × 1/2 = 36: ahora también el otro lado.",
                "36 teselas. El aprendiz iba a pedir 288: ocho veces de más.",
                "Multiplicar por 1/2 achicó dos veces seguidas, aunque las dos fueran multiplicaciones.",
            ],
            "solution": r"$144\times\dfrac{1}{2}\times\dfrac{1}{2}=36$",
            "self_explanation": {
                "step_index": 0,
                "prompt": "En el paso 1 se aplican DOS mitades, no una. ¿Por qué la mitad de la escala no es la mitad de las teselas?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Enteros",
            "title": "Cuando el factor apunta al otro lado",
            "statement": (
                "Al cortar, el aprendiz rompe 3 teselas en cada hilada y el mosaico "
                "lleva 7 hiladas. ¿Cuántas teselas perdió el taller?"
            ),
            "latex": r"7\times(-3)",
            "image_slot": False,
            "steps": [
                "Cada hilada aporta −3 teselas: la pérdida se anota con signo.",
                "Son 7 hiladas iguales: 7 × (−3) = (−3) + (−3) + … siete veces.",
                "Siete grupos de −3 dan −21.",
                "7 × (−3) = −21: el producto quedó por debajo de 0, y eso son 21 teselas menos.",
                "El signo del producto sale de los signos de los factores; el tamaño sale de sus magnitudes.",
            ],
            "solution": r"$7\times(-3)=-21$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que pidió de más",
            "statement": (
                "El aprendiz anota en la bodega: «El mosaico lleva 60 teselas. Lo quieren a "
                "media escala, o sea multiplicado por 1/2. Multiplicar agranda, así que pido 120»."
            ),
            "latex": r"60\times\dfrac{1}{2}=120",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"60\times\dfrac{1}{2}=\underline{120}",
            "error_note": "120 es 60 × 2, no 60 × 1/2. Usó el denominador como si fuera el multiplicador.",
            "correct_version": {
                "wrong_latex": r"60\times\dfrac{1}{2}=120",
                "right_latex": r"60\times\dfrac{1}{2}=30",
                "rows": [
                    {
                        "wrong": "Multiplicar siempre da un resultado mayor",
                        "right": "Multiplicar por un número entre 0 y 1 da un resultado menor",
                    },
                    {
                        "wrong": "Media escala pide el doble de teselas",
                        "right": "Media escala pide la mitad",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 120 no puede ser la respuesta? Escribe la igualdad corregida.",
            "steps": [
                "Comprueba al revés: si 60 × 1/2 fuera 120, entonces 120 × 2 debería dar 60.",
                "120 × 2 = 240, no 60. La igualdad no se sostiene.",
                "60 × 1/2 es la mitad de 60, es decir 30. Un factor menor que 1 achica.",
            ],
            "solution": (
                "«Multiplicar agranda» es un resumen de cuando todos los multiplicadores eran "
                "2, 3, 4… Con fracciones deja de valer. La pregunta útil no es «¿es una "
                "multiplicación?» sino «¿el multiplicador está por encima o por debajo de 1?»."
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
                "statement": "Un friso lleva 9 paneles y cada panel 14 teselas.",
                "given_steps": [
                    r"9\times 14",
                    r"9\times 10=90,\quad 9\times 4=36",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"9\times 14=", "answer": "126"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Una cenefa de 48 teselas se rehace a un cuarto de su largo.",
                "given_steps": [
                    r"48\times\dfrac{1}{4}",
                ],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"\text{¿el factor es mayor o menor que 1? escribe }0\text{ si menor}, 1\text{ si mayor}",
                        "answer": "0",
                    },
                    {"id": "P2-b2", "label": r"48\times\dfrac{1}{4}=", "answer": "12"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: el cortador rompe 6 teselas por hilada y el "
                    "mosaico lleva 8 hiladas. Anota la pérdida total con su signo."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"8\times(-6)=", "answer": "-48"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para el mismo producto",
        "intro": r"¿Cuánto vale $25\times 12$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Descomponer un factor",
                "steps": [r"25\times 12=25\times(10+2)", r"=250+50", r"=300"],
                "note": "Usa la distributiva sin nombrarla.",
            },
            {
                "label": "Método 2 · Reagrupar los factores",
                "steps": [r"25\times 12=25\times 4\times 3", r"=100\times 3", r"=300"],
                "note": "Busca un producto redondo antes de terminar.",
            },
        ],
        "question": "¿Cuál te sale más rápido de cabeza? ¿Y qué permiso usaste en cada uno para reordenar?",
        "insight": (
            "El método 1 reparte un factor sobre una suma (distributiva) y el método 2 "
            "reagrupa factores (asociativa). Las dos son propiedades de la multiplicación, "
            "no atajos de cálculo, y se formalizan en N3 (M02 y M03). Con la división ninguna "
            "de las dos vale — lo compruebas en el nodo siguiente."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Un mosaico tiene 13 filas de 6 teselas. ¿Cuántas teselas lleva?",
            "expr": r"13\times 6",
            "answer": "78",
            "hints": {
                "n1": "Cada fila aporta lo mismo.",
                "n2": "10 × 6 = 60.",
                "n3": "3 × 6 = 18, y 60 + 18 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una cenefa de 36 teselas se rehace a un tercio de su largo. ¿Cuántas teselas lleva?",
            "expr": r"36\times\dfrac{1}{3}",
            "answer": "12",
            "hints": {
                "n1": "El factor es menor que 1: el resultado va a quedar por debajo de 36.",
                "n2": "Un tercio de 36 es 36 dividido entre 3.",
                "n3": "3 × 12 = 36.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El cortador rompe 4 teselas por hilada y hay 9 hiladas. ¿Cuántas teselas perdió? (con signo)",
            "expr": r"9\times(-4)",
            "answer": "-36",
            "hints": {
                "n1": "Cada hilada aporta una cantidad negativa.",
                "n2": "Nueve grupos de −4.",
                "n3": "9 × 4 = 36, y el signo lo pone la pérdida.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"Un escriba anota «$20\times 0{,}5=100$». ¿Dónde está el error?",
            "options": [
                {"id": "inverted", "text": "Multiplicó por 5 en vez de por 0,5; lo correcto es 10"},
                {"id": "added", "text": "Sumó en vez de multiplicar"},
                {"id": "decimal", "text": "Se le olvidó la coma en el resultado: es 10,0"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "inverted",
            "feedback_by_option": {
                "inverted": "correct",
                "added": "fb_e03_e4_added",
                "decimal": "fb_e03_e4_decimal",
                "none": "fb_e03_e4_none",
            },
            "misconception_by_option": {
                "added": "confunde_multiplicar_con_sumar",
                "decimal": "error_de_notacion_no_de_valor",
                "none": "habito_valida_sin_verificar",
            },
            "hints": {
                "n1": "¿0,5 está por encima o por debajo de 1?",
                "n2": "Si el factor es menor que 1, el producto tiene que quedar por DEBAJO de 20.",
                "n3": "0,5 de 20 es la mitad de 20.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para cualesquiera $a>0$ y $b$: $a\times b>a$.»",
            "options": [
                {
                    "id": "false_small",
                    "text": "Falsa: si b está entre 0 y 1, el producto queda por debajo de a",
                },
                {"id": "true", "text": "Verdadera: multiplicar siempre agranda"},
                {"id": "false_never", "text": "Falsa: el producto nunca supera a a"},
                {"id": "true_if_int", "text": "Verdadera siempre que b sea entero"},
            ],
            "expected": "false_small",
            "feedback_by_option": {
                "false_small": "correct",
                "true": "fb_e03_e5_trap",
                "false_never": "fb_e03_e5_never",
                "true_if_int": "fb_e03_e5_int",
            },
            "misconception_by_option": {
                "true": "multiplicar_siempre_agranda",
                "false_never": "multiplicar_siempre_achica",
                "true_if_int": "olvida_enteros_negativos_y_cero",
            },
            "hints": {
                "n1": "Para tumbar un «siempre» basta UN caso.",
                "n2": "Prueba con a = 10 y b = 0,5.",
                "n3": "10 × 0,5 = 5, y 5 no es mayor que 10.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Un mosaico de 200 teselas se copia a la mitad de ancho y a la mitad de "
                "alto. ¿Cuántas teselas lleva la copia?"
            ),
            "expr": r"200\times\dfrac{1}{2}\times\dfrac{1}{2}",
            "answer": "50",
            "hints": {
                "n1": "Reducir la escala afecta a los dos lados, no a uno.",
                "n2": "200 × 1/2 = 100.",
                "n3": "Ahora vuelve a tomar la mitad de 100.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estos productos de dos irracionales SE SALE de los irracionales?",
            "options": [
                {"id": "sqrt2_sqrt2", "text": "√2 × √2", "latex": r"\sqrt{2}\times\sqrt{2}"},
                {"id": "sqrt2_sqrt3", "text": "√2 × √3", "latex": r"\sqrt{2}\times\sqrt{3}"},
                {"id": "pi_sqrt2", "text": "π × √2", "latex": r"\pi\times\sqrt{2}"},
                {"id": "pi_pi", "text": "π × π", "latex": r"\pi\times\pi"},
            ],
            "expected": "sqrt2_sqrt2",
            "feedback_by_option": {
                "sqrt2_sqrt2": "correct",
                "sqrt2_sqrt3": "fb_e03_e7_stays",
                "pi_sqrt2": "fb_e03_e7_stays",
                "pi_pi": "fb_e03_e7_stays",
            },
            "misconception_by_option": {
                "sqrt2_sqrt3": "irracional_por_irracional_siempre_irracional",
                "pi_sqrt2": "irracional_por_irracional_siempre_irracional",
                "pi_pi": "irracional_por_irracional_siempre_irracional",
            },
            "hints": {
                "n1": "Busca el producto que da un número que ya conoces.",
                "n2": r"$\sqrt{2}\times\sqrt{2}$ es el lado por el lado de un cuadrado de área 2.",
                "n3": r"$\sqrt{2}\times\sqrt{2}=2$, y 2 es racional.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "La escalera de la multiplicación",
        "title": "¿El producto de dos elementos del conjunto vive en el conjunto?",
        "intro": "La multiplicación no rompe ningún peldaño nuevo… salvo uno.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "yes",
                "latex": r"13\times 6=78\in\mathbb{N}",
                "note": "Agrupar cantidades de contar da otra cantidad de contar.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "yes",
                "latex": r"7\times(-3)=-21\in\mathbb{Z}",
                "note": "Con signos también cierra: el signo del producto lo deciden los factores.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"\dfrac{3}{4}\times\dfrac{2}{5}=\dfrac{6}{20}=\dfrac{3}{10}\in\mathbb{Q}",
                "note": "Numerador por numerador, denominador por denominador: sigue siendo fracción.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\sqrt{2}\times\sqrt{2}=2\in\mathbb{Q}",
                "note": "Dos irracionales pueden dar un racional: el resultado SE SALE. Ninguna operación aritmética cierra 𝕀.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\pi\times 2=2\pi\in\mathbb{R}",
                "note": "ℝ = ℚ ∪ 𝕀 (B08) sí cierra: por eso el producto vive ahí sin problemas.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"i\times i=-1",
                "note": "También cierra, y aquí el producto hace algo que en ℝ es imposible. Desvío opcional (B09).",
            },
        ],
        "outro": (
            "Como la suma, la multiplicación no obligó a inventar un peldaño nuevo. Lo que sí "
            "hizo fue tumbar una creencia: agrupar puede achicar. La división, en cambio, sí "
            "va a romper un peldaño."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [
            r"144\times\tfrac{1}{2}\times\tfrac{1}{2}",
            r"7\times(-3)",
            r"60\times\tfrac{1}{2}",
        ],
        "options": [
            {
                "id": "grouping",
                "text": "En los tres se toma una cantidad tantas veces como diga el otro factor",
                "correct": True,
            },
            {
                "id": "bigger",
                "text": "En los tres el producto es mayor que el primer factor",
                "correct": False,
            },
            {
                "id": "below",
                "text": "En los tres el segundo factor decide si el resultado sube o baja",
                "correct": True,
            },
            {"id": "fractions", "text": "En los tres aparece una fracción", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El taller recibe un encargo: 15 frisos, cada uno con 24 teselas, pero a media "
            "escala en ancho y en alto. ¿Cuántas teselas hay que pedir en total?"
        ),
        "polya": {
            "comprender": "Me dan 15 frisos de 24 teselas y una reducción a media escala en los dos lados.",
            "planear": "Calculo el total a escala completa y luego aplico las dos mitades.",
            "ejecutar": "15 × 24 = 360 → 360 × 1/2 = 180 → 180 × 1/2 = 90.",
            "comprobar": "Media escala en los dos lados deja un cuarto: 360 ÷ 4 = 90. Cuadra.",
        },
        "prompt": "¿Cuántas teselas hay que pedir?",
        "answer": "90",
        "hints": {
            "n1": "Primero el total sin reducir.",
            "n2": "15 × 24 = 360.",
            "n3": "Media escala en los dos lados deja la cuarta parte.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya miras el multiplicador antes de decidir si el resultado crece.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué pasa al "
            "multiplicar por un número entre 0 y 1."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Un mosaico tiene 9 filas de 7 teselas. ¿Cuántas lleva?",
                "answer": "63",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $30\times\dfrac{1}{3}$?",
                "options": [
                    {"id": "ten", "text": "10", "latex": r"10"},
                    {"id": "ninety", "text": "90", "latex": r"90"},
                    {"id": "thirty_third", "text": "30,3", "latex": r"30{,}3"},
                ],
                "expected": "ten",
                "misconception_by_option": {
                    "ninety": "multiplicar_siempre_agranda",
                    "thirty_third": "confunde_multiplicar_con_sumar",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Existen $a>0$ y $b>0$ tales que $a\times b<a$?",
                "options": [
                    {"id": "yes", "text": "Sí"},
                    {"id": "no", "text": "No"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "multiplicar_siempre_agranda"},
                # Variante VERDADERA de E5, con los dos factores positivos a
                # propósito: cierra la salida "solo pasa con negativos".
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
        "default": "Mira si el multiplicador está por encima o por debajo de 1 antes de decidir.",
        "fb_e03_e4_added": (
            "Si hubiera sumado, 20 + 0,5 daría 20,5, no 100. → Di por cuánto multiplicó "
            "realmente para llegar a 100."
        ),
        "fb_e03_e4_decimal": (
            "No es un problema de notación: 10 y 100 se llevan un cero de diferencia. "
            "→ Calcula la mitad de 20."
        ),
        "fb_e03_e4_none": ("Compruébalo al revés: 100 ÷ 0,5 debería dar 20. → Haz esa división."),
        "fb_e03_e5_trap": (
            "Esa regla vale mientras el multiplicador sea mayor que 1. → Prueba con a = 10 "
            "y b = 0,5 y mira si se sostiene."
        ),
        "fb_e03_e5_never": (
            "Te pasaste al otro extremo: con b = 3 sí crece. → Da un caso donde crezca y "
            "otro donde se achique."
        ),
        "fb_e03_e5_int": (
            "Prueba con b = 0 y con b = −2, que también son enteros. → Di qué pasa en cada caso."
        ),
        "fb_e03_e7_stays": (
            "Ese producto sigue siendo irracional. → Busca el que da un número entero, y "
            "piensa en el área de un cuadrado de lado √2."
        ),
    },
    "closing": (
        "Multiplicar es agrupar, y quien decide si el resultado sube o baja es el "
        "multiplicador, no la operación. En el nodo siguiente la división va a hacer lo "
        "mismo al revés: dividir puede agrandar."
    ),
    "validation_status": "F2_E03_11bloques",
}
