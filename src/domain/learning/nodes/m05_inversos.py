"""M05 · Inversos — el opuesto lleva a 0, el recíproco lleva a 1.

Estación del nodo: LA PRENSA DE CONTRAPESOS (pesas y contrapesos sobre una
balanza de brazo). Ninguna otra estación usa este material.
"""

NODE_ID = "PREALG-N3-M05-INVERSOS"
CONCEPT_SLUG = "inversos"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "inversos",
    "misconception": "inverso_es_solo_cambiar_el_signo",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La Prensa de Contrapesos · Inversos",
    "station": "La Prensa de Contrapesos",
    "finish_label": "Salir hacia el Puerto de la Polis",
    "title": "Hay dos formas de cancelar, no una",
    "intro": (
        "En el Calibre Cero encontraste los números que no cambian nada. Aquí buscas otra "
        "cosa: dado un número, la pieza que lo DEVUELVE a ese neutro. Y hay dos piezas "
        "distintas según la operación, aunque casi todo el mundo solo conoce una."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de cargar la prensa. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $9+(-9)$?",
                "answer": "0",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Por cuánto hay que multiplicar $5$ para obtener $1$?",
                "options": [
                    {"id": "fifth", "text": "un quinto", "latex": r"\dfrac{1}{5}"},
                    {"id": "minus_five", "text": "menos cinco", "latex": r"-5"},
                    {"id": "one", "text": "uno", "latex": r"1"},
                    {"id": "cannot", "text": "No se puede"},
                ],
                "expected": "fifth",
                "misconception_by_option": {
                    "minus_five": "inverso_es_solo_cambiar_el_signo",
                    "one": "confunde_inverso_con_neutro",
                    "cannot": "niega_la_existencia_del_reciproco",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Qué es «el inverso» de un número?",
                "options": [
                    {
                        "id": "depends",
                        "text": "Depende de la operación: hay uno para sumar y otro para multiplicar",
                    },
                    {"id": "sign", "text": "El mismo número con el signo cambiado"},
                    {"id": "fraction", "text": "El número dado vuelta como fracción"},
                ],
                "expected": "depends",
                "misconception_by_option": {
                    "sign": "inverso_es_solo_cambiar_el_signo",
                    "fraction": "inverso_es_solo_dar_vuelta_la_fraccion",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En la Prensa de Contrapesos",
        "title": "El brazo que hay que devolver al fiel",
        "body": (
            "La última estación de la fábrica es una prensa con balanza de brazo. Cada pieza "
            "que se carga inclina el brazo, y antes de seguir hay que devolverlo al fiel — "
            "la posición de equilibrio. Para eso está la caja de contrapesos.\n\n"
            "El operario tiene un método infalible: si la pieza inclina a la derecha, pone "
            "una igual a la izquierda. Le funciona todos los días. Hoy la prensa cambió de "
            "modo: ya no suma cargas, las multiplica. El operario puso su contrapeso de "
            "siempre y el brazo se fue al otro extremo."
        ),
        "question": "¿Qué pieza cancela a un número cuando la prensa multiplica en vez de sumar?",
        "image": "/leccion/03-prealg-n3-fabrica/m05-inversos-katia-v5.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "La misma: el número con el signo cambiado"},
                {"id": "b", "text": "Otra distinta"},
                {"id": "c", "text": "Multiplicando no se puede cancelar nada"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder nombrar las dos piezas "
                "y decir a qué neutro lleva cada una."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo 5, dos contrapesos distintos",
        "body": (
            "Abajo, una carga de 5 en los dos modos de la prensa. Fíjate en qué pieza "
            "devuelve el brazo al fiel en cada uno, y a qué número llega."
        ),
        "cases": [
            {
                "label": "Caso que ya conoces",
                "context": "Prensa sumando, carga de 5",
                "fraction": r"5+(-5)",
                "division": r"5+(-5)=0",
                "note": "El contrapeso es −5 y el fiel está en 0: el neutro de la suma.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Prensa multiplicando, la misma carga de 5",
                "fraction": r"5\times\dfrac{1}{5}",
                "division": r"5\times\dfrac{1}{5}=1",
                "note": "El contrapeso es 1/5 y el fiel está en 1: el neutro del producto.",
            },
        ],
        "resolution": (
            "Si el operario hubiera puesto −5 en el modo multiplicar, habría obtenido −25: "
            "el brazo al otro extremo. Cancelar no es «poner lo contrario»: es llegar al "
            "neutro DE ESA OPERACIÓN. Cambian el neutro y el contrapeso a la vez."
        ),
    },
    "definition_title": "Los elementos inversos",
    "definition_katex": r"a+(-a)=0\qquad a\times\dfrac{1}{a}=1\quad(a\neq 0)",
    "definition": (
        "El opuesto de a es el número que sumado a a da 0. El recíproco de a es el número "
        "que multiplicado por a da 1. Todo número tiene opuesto; todos menos el 0 tienen "
        "recíproco."
    ),
    "definition_symbols": [
        {
            "symbol": r"-a",
            "reads": "el opuesto de a",
            "means": "el contrapeso de la suma: lleva al 0",
        },
        {
            "symbol": r"\dfrac{1}{a}",
            "reads": "el recíproco de a",
            "means": "el contrapeso del producto: lleva al 1",
        },
        {
            "symbol": r"a\neq 0",
            "reads": "a distinto de cero",
            "means": "el 0 no tiene recíproco: nada multiplicado por 0 da 1",
        },
        {
            "symbol": r"-(-a)=a",
            "reads": "el opuesto del opuesto",
            "means": "quitar el contrapeso deja la carga original",
        },
        {
            "symbol": r"a-b=a+(-b)",
            "reads": "restar es sumar el opuesto",
            "means": "por eso la resta no necesitó reglas nuevas (E02)",
        },
        {
            "symbol": r"a\div b=a\times\dfrac{1}{b}",
            "reads": "dividir es multiplicar por el recíproco",
            "means": "el mismo truco, con el otro contrapeso (E04)",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Los dos contrapesos",
            "title": "Devolver el brazo al fiel en los dos modos",
            "statement": (
                "Una carga de 4 inclina el brazo. ¿Qué contrapeso hay que poner si la prensa "
                "suma? ¿Y si multiplica?"
            ),
            "latex": r"4+(-4)=0\qquad 4\times\dfrac{1}{4}=1",
            "image_slot": True,
            "image": "/leccion/03-prealg-n3-fabrica/m05-opuesto-descargar-prensa-v4.png",
            "steps": [
                "Modo sumar: el fiel está en 0, así que busco x con 4 + x = 0. Es x = −4.",
                "Modo multiplicar: el fiel está en 1, así que busco x con 4 × x = 1.",
                "No es −4: 4 × (−4) = −16, y eso no es el fiel.",
                "Es 1/4, porque 4 × 1/4 = 4/4 = 1.",
                "Dos contrapesos distintos para la misma carga, porque el fiel está en sitios distintos.",
            ],
            "solution": r"Opuesto: $-4$. Recíproco: $\dfrac{1}{4}=0{,}25$.",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se descarta el −4 para el modo multiplicar. ¿Qué tendría que cumplir el contrapeso correcto?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Irracionales",
            "title": "El recíproco de una carga que no es fracción",
            "statement": (
                "La prensa carga una pieza de longitud √2 en modo multiplicar. ¿Cuál es su "
                "contrapeso, y sigue siendo irracional?"
            ),
            "latex": r"\sqrt{2}\times\dfrac{1}{\sqrt{2}}=1",
            "image_slot": True,
            "image": "/leccion/03-prealg-n3-fabrica/m05-reciproco-recomponer-plancha-v4.png",
            "steps": [
                "El recíproco de √2 es 1/√2, porque al multiplicarlos da 1.",
                "Un recíproco con una raíz abajo es incómodo de medir. Se puede reescribir.",
                "Multiplico arriba y abajo por √2: (1 × √2) / (√2 × √2) = √2 / 2.",
                "Eso es exactamente lo mismo, escrito sin raíz en el denominador: se llama racionalizar.",
                "√2/2 ≈ 0,707: sigue siendo irracional. El recíproco de un irracional también lo es.",
            ],
            "solution": r"$\dfrac{1}{\sqrt{2}}=\dfrac{\sqrt{2}}{2}\approx 0{,}707$, irracional",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El operario que usó un solo contrapeso",
            "statement": (
                "El operario deja la nota del turno: «Para cancelar cualquier carga, se pone "
                "la misma con el signo cambiado. Carga de 8, contrapeso −8. Vale para los "
                "dos modos de la prensa»."
            ),
            "latex": r"8\times(-8)=1",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"8\times(-8)=\underline{1}",
            "error_note": "8 × (−8) = −64, no 1. El opuesto cancela sumando, no multiplicando.",
            "correct_version": {
                "wrong_latex": r"8\times(-8)=1",
                "right_latex": r"8\times\dfrac{1}{8}=1",
                "rows": [
                    {
                        "wrong": "Cancelar es siempre cambiar el signo",
                        "right": "Cancelar es llegar al neutro de esa operación",
                    },
                    {
                        "wrong": "El contrapeso de 8 es −8 en cualquier modo",
                        "right": "Es −8 sumando y 1/8 multiplicando",
                    },
                ],
            },
            "explain_prompt": "¿Qué contrapeso cancela al 8 en el modo multiplicar? Escribe la igualdad completa.",
            "steps": [
                "Comprueba la nota: 8 × (−8) = −64. Ni siquiera se acerca al fiel.",
                "El fiel del modo multiplicar está en 1, no en 0.",
                "El número que multiplicado por 8 da 1 es 1/8 = 0,125.",
            ],
            "solution": (
                "Antes de elegir el contrapeso, pregunta dónde está el fiel. Si la operación "
                "suma, el fiel está en 0 y el contrapeso es el opuesto. Si multiplica, el "
                "fiel está en 1 y el contrapeso es el recíproco."
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
                "statement": "Carga de 17 en modo sumar. Busca el contrapeso que devuelve el brazo al fiel.",
                "given_steps": [
                    r"17+x=0",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"x=", "answer": "-17"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Carga de 4 en modo multiplicar.",
                "given_steps": [
                    r"4\times x=1",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"x\text{ en decimal}=", "answer": "0,25"},
                    {"id": "P2-b2", "label": r"4\times 0{,}25=", "answer": "1"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: carga de 0,2 en modo multiplicar. ¿Cuál es su "
                    "recíproco?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"0{,}2\times x=1\ \Rightarrow\ x=", "answer": "5"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma división",
        "intro": r"¿Cuánto vale $\dfrac{3}{4}\div\dfrac{3}{8}$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar por el recíproco",
                "steps": [r"\dfrac{3}{4}\times\dfrac{8}{3}", r"=\dfrac{24}{12}", r"=2"],
                "note": "Usa el contrapeso del producto: dar vuelta la segunda fracción.",
            },
            {
                "label": "Método 2 · Contar cuántos caben",
                "steps": [
                    r"\dfrac{3}{4}=\dfrac{6}{8}",
                    r"\text{¿cuántos }\tfrac{3}{8}\text{ caben en }\tfrac{6}{8}?",
                    r"=2",
                ],
                "note": "Vuelve al significado de dividir, sin recíprocos.",
            },
        ],
        "question": "¿Por qué el método 1 «da vuelta» la segunda fracción y no la primera?",
        "insight": (
            "Porque dividir entre b es multiplicar por el contrapeso de b, y el contrapeso "
            "del producto es el recíproco. La primera fracción no se cancela: se conserva. "
            "Esa regla que memorizaste como «se invierte y se multiplica» no es un truco — "
            "es esta propiedad, aplicada."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Qué contrapeso cancela una carga de 23 en modo sumar?",
            "expr": r"23+x=0",
            "answer": "-23",
            "hints": {
                "n1": "El fiel del modo sumar está en 0.",
                "n2": "Busca x con 23 + x = 0.",
                "n3": "Es la misma carga apuntando al otro lado.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Qué contrapeso cancela una carga de 8 en modo multiplicar? (decimal)",
            "expr": r"8\times x=1",
            "answer": "0,125",
            "hints": {
                "n1": "El fiel del modo multiplicar está en 1.",
                "n2": "Es un octavo.",
                "n3": "1 ÷ 8 = …",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuál es el recíproco de $0{,}5$?",
            "expr": r"0{,}5\times x=1",
            "answer": "2",
            "hints": {
                "n1": "Busca el número que multiplicado por 0,5 da 1.",
                "n2": "0,5 es un medio.",
                "n3": "El recíproco de 1/2 es 2/1.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"Un operario anota «El recíproco de $7$ es $-7$, porque $7\times(-7)$ cancela». ¿Dónde está el error?",
            "options": [
                {
                    "id": "reciprocal",
                    "text": "El recíproco es 1/7; el −7 es el opuesto, y cancela sumando",
                },
                {"id": "sign", "text": "Debía ser 7, no −7"},
                {"id": "arith", "text": "Se equivocó: 7 × (−7) da −48"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "reciprocal",
            "feedback_by_option": {
                "reciprocal": "correct",
                "sign": "fb_m05_e4_sign",
                "arith": "fb_m05_e4_arith",
                "none": "fb_m05_e4_none",
            },
            "misconception_by_option": {
                "sign": "confunde_inverso_con_neutro",
                "arith": "habito_error_de_calculo_no_de_metodo",
                "none": "inverso_es_solo_cambiar_el_signo",
            },
            "hints": {
                "n1": "Calcula 7 × (−7) y mira si llega al fiel del modo multiplicar.",
                "n2": "7 × (−7) = −49, y el fiel está en 1.",
                "n3": "El número que multiplicado por 7 da 1 es 1/7.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Todo número tiene recíproco.»",
            "options": [
                {
                    "id": "false_zero",
                    "text": "Falsa: el 0 no tiene, porque nada multiplicado por 0 da 1",
                },
                {"id": "true", "text": "Verdadera: basta darle vuelta"},
                {"id": "false_negatives", "text": "Falsa: los negativos no tienen recíproco"},
                {"id": "false_irrationals", "text": "Falsa: los irracionales no tienen recíproco"},
            ],
            "expected": "false_zero",
            "feedback_by_option": {
                "false_zero": "correct",
                "true": "fb_m05_e5_trap",
                "false_negatives": "fb_m05_e5_negatives",
                "false_irrationals": "fb_m05_e5_irrationals",
            },
            "misconception_by_option": {
                "true": "olvida_la_excepcion_del_cero",
                "false_negatives": "reciproco_solo_para_positivos",
                "false_irrationals": "irracional_no_tiene_reciproco",
            },
            "hints": {
                "n1": "Busca un número donde el recíproco no exista.",
                "n2": "Prueba con el 0: ¿hay algún x con 0 × x = 1?",
                "n3": "Cualquier cosa por 0 da 0, nunca 1.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "La prensa carga 6 en modo multiplicar, se cancela con su recíproco y "
                "después se carga 19 en modo sumar. ¿En qué queda el brazo?"
            ),
            "expr": r"\left(6\times\dfrac{1}{6}\right)+19",
            "answer": "20",
            "hints": {
                "n1": "Resuelve primero la cancelación del modo multiplicar.",
                "n2": "6 × 1/6 = 1.",
                "n3": "1 + 19 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": r"¿Cuál es el recíproco de $\sqrt{2}$, escrito sin raíz en el denominador?",
            "options": [
                {
                    "id": "rationalized",
                    "text": "raíz de 2 partido por 2",
                    "latex": r"\dfrac{\sqrt{2}}{2}",
                },
                {"id": "negative", "text": "menos raíz de 2", "latex": r"-\sqrt{2}"},
                {"id": "two", "text": "2", "latex": r"2"},
                {"id": "half", "text": "un medio", "latex": r"\dfrac{1}{2}"},
            ],
            "expected": "rationalized",
            "feedback_by_option": {
                "rationalized": "correct",
                "negative": "fb_m05_e7_negative",
                "two": "fb_m05_e7_two",
                "half": "fb_m05_e7_half",
            },
            "misconception_by_option": {
                "negative": "inverso_es_solo_cambiar_el_signo",
                "two": "confunde_reciproco_con_cuadrado",
                "half": "confunde_reciproco_del_radicando",
            },
            "hints": {
                "n1": "El recíproco es 1/√2. Falta quitarle la raíz de abajo.",
                "n2": "Multiplica arriba y abajo por √2.",
                "n3": "√2 × √2 = 2, así que queda √2 partido por 2.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Los inversos a lo largo de los conjuntos numéricos",
        "title": "¿Cada número del conjunto tiene su contrapeso dentro del conjunto?",
        "intro": (
            "Esta propiedad no se recorre por operaciones sino por conjuntos: es la que "
            "explica por qué la escalera de N1 tuvo que crecer."
        ),
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"5+x=0\ \Rightarrow\ x\notin\mathbb{N}",
                "note": "Ni opuesto ni recíproco: no hay natural que sumado a 5 dé 0.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "partial",
                "latex": r"5+(-5)=0\quad\text{pero}\quad \dfrac{1}{5}\notin\mathbb{Z}",
                "note": "Aparece el OPUESTO — para esto nacieron los enteros (B05) — pero el recíproco sigue fuera.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"\dfrac{a}{b}\times\dfrac{b}{a}=1",
                "note": "Aparece el RECÍPROCO: dar vuelta la fracción. Para esto nacieron los racionales (B06). Única excepción: el 0.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "partial",
                "latex": r"\dfrac{1}{\sqrt{2}}=\dfrac{\sqrt{2}}{2}\in\mathbb{I}",
                "note": "Cada irracional tiene opuesto y recíproco, y los DOS son irracionales — racionalizar es exactamente eso. Pero los neutros 0 y 1 no viven aquí, así que el hogar completo son los reales.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\pi\times\dfrac{1}{\pi}=1",
                "note": "Todo real distinto de 0 tiene los dos contrapesos, y los neutros están dentro.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"i\times(-i)=1",
                "note": "También cierra, y aquí el recíproco de i resulta ser su opuesto. Desvío opcional (B09).",
            },
        ],
        "outro": (
            "Mira lo que acabas de reconstruir: ℤ existe porque a ℕ le faltaban los "
            "opuestos, y ℚ existe porque a ℤ le faltaban los recíprocos. La escalera de "
            "conjuntos que recorriste en N1 es, en el fondo, la búsqueda de estos dos "
            "contrapesos."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten el opuesto y el recíproco?",
        "thumbnails": [r"5+(-5)=0", r"5\times\tfrac{1}{5}=1", r"8\times(-8)\neq 1"],
        "options": [
            {
                "id": "to_neutral",
                "text": "Los dos llevan el resultado al neutro de su operación",
                "correct": True,
            },
            {"id": "sign", "text": "Los dos cambian el signo del número", "correct": False},
            {
                "id": "cancel",
                "text": "Los dos cancelan al número, cada uno en su operación",
                "correct": True,
            },
            {
                "id": "always",
                "text": "Los dos existen para cualquier número sin excepción",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última carga de la fábrica: la prensa procesa (12 × 1/12) + (30 + (−30)) y "
            "después suma 7. ¿En qué queda el brazo?"
        ),
        "polya": {
            "comprender": "Dos cancelaciones, una en modo multiplicar y otra en modo sumar, más un 7 al final.",
            "planear": "Cada cancelación lleva a SU neutro: la del producto a 1, la de la suma a 0.",
            "ejecutar": "12 × 1/12 = 1 → 30 + (−30) = 0 → 1 + 0 = 1 → 1 + 7 = 8.",
            "comprobar": "Si hubiera puesto los dos a 0, saldría 7. El 1 de más viene de que el fiel del producto no está en 0.",
        },
        "prompt": "¿En qué número queda el brazo?",
        "answer": "8",
        "hints": {
            "n1": "Resuelve cada paréntesis por separado antes de sumar.",
            "n2": "12 × 1/12 = 1, no 0.",
            "n3": "30 + (−30) = 0, y luego 1 + 0 + 7 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya eliges el contrapeso según dónde esté el fiel.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre "
            "el opuesto y el recíproco."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $14+(-14)$?",
                "answer": "0",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Por cuánto hay que multiplicar $3$ para obtener $1$?",
                "options": [
                    {"id": "third", "text": "un tercio", "latex": r"\dfrac{1}{3}"},
                    {"id": "minus_three", "text": "menos tres", "latex": r"-3"},
                    {"id": "one", "text": "uno", "latex": r"1"},
                ],
                "expected": "third",
                "misconception_by_option": {
                    "minus_three": "inverso_es_solo_cambiar_el_signo",
                    "one": "confunde_inverso_con_neutro",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? El opuesto de $7$ es $-7$.",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "sobregeneraliza_inversos"},
                # Caso donde cambiar el signo SÍ es la respuesta: comprueba que
                # aprendió a distinguir, no que "cambiar el signo siempre está mal".
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
        "default": "Pregúntate dónde está el fiel de esa operación antes de elegir el contrapeso.",
        "fb_m05_e4_sign": (
            "7 × 7 = 49, tampoco llega al fiel. → Busca el número que multiplicado por 7 dé 1."
        ),
        "fb_m05_e4_arith": (
            "7 × (−7) = −49, pero el problema no es la cuenta: es que el fiel del modo "
            "multiplicar está en 1. → Di qué número multiplicado por 7 da 1."
        ),
        "fb_m05_e4_none": (
            "Comprueba: 7 × (−7) = −49, y el fiel del producto está en 1. → Nombra el "
            "contrapeso correcto."
        ),
        "fb_m05_e5_trap": (
            "Prueba a darle vuelta al 0: 1/0 no es ningún número. → Di si existe algún x "
            "con 0 × x = 1."
        ),
        "fb_m05_e5_negatives": (
            "El recíproco de −4 es −1/4, y −4 × (−1/4) = 1. Sí tienen. → Busca el número "
            "que de verdad no tiene."
        ),
        "fb_m05_e5_irrationals": (
            "El recíproco de √2 es √2/2, y su producto da 1. Sí tienen. → Busca el número "
            "que de verdad no tiene."
        ),
        "fb_m05_e7_negative": (
            "√2 × (−√2) = −2, no 1. Ese es el opuesto, no el recíproco. → Parte de 1/√2 y "
            "quítale la raíz de abajo."
        ),
        "fb_m05_e7_two": ("√2 × 2 = 2√2 ≈ 2,83, no 1. → Parte de 1/√2 y racionaliza."),
        "fb_m05_e7_half": (
            "El 2 de abajo no es el radicando: es el resultado de √2 × √2 al racionalizar. "
            "→ Haz esa multiplicación y mira qué queda arriba."
        ),
    },
    "closing": (
        "Hay dos contrapesos: el opuesto lleva al 0 y el recíproco lleva al 1. Buscarlos "
        "es lo que hizo crecer la escalera de conjuntos. Con esto terminas la fábrica de "
        "propiedades; el siguiente destino es el Puerto de la Polis."
    ),
    "validation_status": "F3_M05_11bloques",
}
