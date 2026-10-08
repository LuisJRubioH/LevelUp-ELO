"""E01 · Suma — juntar no siempre agranda.

Edificio del nodo: EL GRANERO PÚBLICO (medidas de trigo, entradas y salidas en
una sola tablilla). Ningún otro edificio de N2 usa este oficio.
"""

NODE_ID = "PREALG-N2-E01-SUMA-JUNTAR"
CONCEPT_SLUG = "suma"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "suma",
    "misconception": "sumar_siempre_agranda",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El Granero Público · Suma",
    "building": "El Granero Público",
    "finish_label": "Salir hacia la Casa de Cuentas",
    "title": "Juntar no siempre agranda",
    "intro": (
        "Sumar es juntar. Eso lo sabes desde que contabas con los dedos. Lo que "
        "vas a decidir hoy es qué pasa cuando lo que juntas apunta hacia el otro "
        "lado, y hasta dónde llega la suma cuando los números dejan de ser enteros."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el granero. No hay nota; me dicen por dónde entrarle.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Hay 14 medidas de trigo en el granero y entran 9 más. ¿Cuántas quedan?",
                "answer": "23",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $7+(-4)$?",
                "options": [
                    {"id": "three", "text": "3", "latex": r"3"},
                    {"id": "eleven", "text": "11", "latex": r"11"},
                    {"id": "minus_eleven", "text": "-11", "latex": r"-11"},
                    {"id": "cannot", "text": "No se puede sumar un negativo"},
                ],
                "expected": "three",
                "misconception_by_option": {
                    "eleven": "ignora_el_signo_al_sumar",
                    "minus_eleven": "ignora_el_signo_al_sumar",
                    "cannot": "sumar_solo_con_positivos",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si a un número le sumas otro número, ¿el resultado siempre es mayor que el primero?",
                "options": [
                    {"id": "always", "text": "Sí, siempre"},
                    {"id": "depends", "text": "Depende de qué número sumes"},
                    {"id": "never", "text": "No, nunca"},
                ],
                "expected": "depends",
                "misconception_by_option": {
                    "always": "sumar_siempre_agranda",
                    "never": "sumar_siempre_achica",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · Dentro del Granero Público",
        "title": "La tablilla de las dos columnas",
        "body": (
            "El primer edificio de la ciudad es el Granero Público: dos pisos de sacos, "
            "una balanza de suelo y, junto a la puerta, la tablilla donde el escriba anota "
            "todo lo que entra y todo lo que sale. Durante años usó dos columnas: en una "
            "las carretas que llegaban, en otra los sacos que salían. Al cerrar el mes "
            "contaba cada columna aparte y restaba.\n\n"
            "Este mes entró un escriba nuevo y dijo que sobraba una columna. Que una "
            "salida también se puede sumar, si se anota con signo."
        ),
        "question": "Si sumas una salida, ¿la cuenta del granero crece o se achica?",
        "image": "/leccion/02-prealg-n2-mercado/e01-suma-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Crece: sumar siempre agranda"},
                {"id": "b", "text": "Se achica: una salida quita"},
                {"id": "c", "text": "Depende del signo de lo que sumes"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final del nodo vas a poder decir por qué "
                "una sola de las tres funciona para todos los casos."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos sumas, dos direcciones",
        "body": (
            "Las dos filas de abajo son sumas. Fíjate en qué le pasa al número de "
            "partida en cada una."
        ),
        "cases": [
            {
                "label": "Caso que confirma lo que esperas",
                "context": "El granero tiene 40 medidas y entra una carreta con 12",
                "fraction": r"40+12",
                "division": r"40+12=52",
                "note": "El resultado quedó por encima del punto de partida.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "El granero tiene 40 medidas y sale un pedido de 12",
                "fraction": r"40+(-12)",
                "division": r"40+(-12)=28",
                "note": "También es una suma, y el resultado quedó por debajo.",
            },
        ],
        "resolution": (
            "Las dos operaciones son sumas: en las dos junté lo que había con lo que "
            "llegó. Lo que cambió no fue la operación, fue la dirección de lo que se "
            "juntó. «Sumar agranda» solo vale mientras todo apunte hacia el mismo lado."
        ),
    },
    "definition_title": "La suma",
    "definition_katex": r"a+b=c,\qquad a,b,c\in\mathbb{R}",
    "definition": (
        "Sumar es juntar dos cantidades en una sola. El signo de cada sumando dice "
        "hacia qué lado apunta; el resultado se llama suma o total."
    ),
    "definition_symbols": [
        {"symbol": r"a,b", "reads": "sumandos", "means": "las dos cantidades que se juntan"},
        {"symbol": r"+", "reads": "más", "means": "la orden de juntar, no la de agrandar"},
        {"symbol": r"c", "reads": "suma o total", "means": "el resultado de juntarlas"},
        {
            "symbol": r"-b",
            "reads": "sumando negativo",
            "means": "algo que apunta al lado contrario (viene de B05)",
        },
        {
            "symbol": r"a+0=a",
            "reads": "sumar cero deja igual",
            "means": "el neutro de la suma; lo formaliza N3-M04",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Enteros",
            "title": "El mes del granero en una sola columna",
            "statement": (
                "En el mes entraron 120 medidas de trigo y salieron 145. El escriba "
                "nuevo quiere una sola cuenta. ¿Cómo queda el granero respecto a como empezó?"
            ),
            "latex": r"120+(-145)",
            "image_slot": False,
            "steps": [
                "Entrada: +120. Salida: −145. Las dos van a la misma columna, con su signo.",
                "Sumo: 120 + (−145).",
                "Como apuntan a lados contrarios, se cancelan hasta donde alcanza el menor: 120 con 120.",
                "Del −145 sobran 25 sin cancelar, y apuntan hacia abajo: −25.",
                "120 + (−145) = −25: el granero terminó 25 medidas por debajo de como empezó.",
            ],
            "solution": r"$120+(-145)=-25$",
            "self_explanation": {
                "step_index": 3,
                "prompt": "En el paso 4 sobran 25 y el resultado sale negativo. ¿Por qué negativo y no 25 a secas?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Racionales",
            "title": "Cuando la carreta no viene llena",
            "statement": (
                "En el granero hay 3/4 de medida de cebada y llega otro 1/2 de medida. "
                "¿Cuánta cebada queda?"
            ),
            "latex": r"\dfrac{3}{4}+\dfrac{1}{2}",
            "image_slot": False,
            "steps": [
                "No puedo juntar cuartos con medios directamente: son partes de distinto tamaño.",
                "Llevo las dos al mismo tamaño de parte: 1/2 = 2/4.",
                "Ahora sí: 3/4 + 2/4. Junto los numeradores y dejo el denominador.",
                "3 + 2 = 5, entonces 5/4.",
                "5/4 = 1,25 medidas: la suma cierra dentro de los racionales.",
            ],
            "solution": r"$\dfrac{3}{4}+\dfrac{1}{2}=\dfrac{5}{4}=1{,}25$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que sumó de más",
            "statement": (
                "Un aprendiz cierra la tablilla así: «Había 60 medidas, sumé una salida de "
                "18 y me dio 78. Sumar agranda, así que va bien»."
            ),
            "latex": r"60+(-18)=78",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"60+(-18)=\underline{78}",
            "error_note": "Sumó las magnitudes y tiró el signo a la basura. 78 es 60+18, no 60+(−18).",
            "correct_version": {
                "wrong_latex": r"60+(-18)=78",
                "right_latex": r"60+(-18)=42",
                "rows": [
                    {
                        "wrong": "El signo del sumando se puede ignorar",
                        "right": "El signo es parte del número que se junta",
                    },
                    {
                        "wrong": "Sumar siempre da un resultado mayor",
                        "right": "Sumar un negativo da un resultado menor",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 78 no puede ser la respuesta? Escribe la igualdad corregida.",
            "steps": [
                "Compara: 60 + 18 = 78 y 60 + (−18) = 42. Solo cambió un signo.",
                "El −18 apunta al lado contrario del 60: cancela 18 de esos 60.",
                "Quedan 42. El resultado de sumar un negativo está POR DEBAJO del punto de partida.",
            ],
            "solution": (
                "La frase «sumar agranda» es un resumen de la primaria, cuando todos los "
                "números eran positivos. Con signos deja de valer: la suma junta, y hacia "
                "dónde te mueve lo decide el signo del sumando."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "Ahora tú, pero el procedimiento ya está empezado: solo faltan huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "El granero registra +85 de entrada y −37 de salida en el mismo día.",
                "given_steps": [
                    r"85+(-37)",
                    r"\text{apuntan a lados contrarios: se cancelan 37}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"85+(-37)=", "answer": "48"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Otro día: entran 2/5 de medida de mijo y luego 1/5 más.",
                "given_steps": [
                    r"\dfrac{2}{5}+\dfrac{1}{5}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{numerador de la suma}=", "answer": "3"},
                    {"id": "P2-b2", "label": r"\dfrac{3}{5}\text{ en decimal}=", "answer": "0,6"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: el granero arranca en −18 medidas (debe trigo) y "
                    "entran tres carretas de 7 medidas cada una. ¿En cuánto termina?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"-18+7+7+7=", "answer": "3"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma suma",
        "intro": r"¿Cuánto vale $-14+9+14$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · De izquierda a derecha",
                "steps": [r"-14+9=-5", r"-5+14=9"],
                "note": "Siempre funciona; es el orden en que está escrito.",
            },
            {
                "label": "Método 2 · Reagrupar primero lo que se cancela",
                "steps": [r"(-14+14)+9", r"=0+9", r"=9"],
                "note": "Aprovecha que −14 y 14 se anulan.",
            },
        ],
        "question": "¿Cuál conviene aquí? ¿Y qué propiedad de la suma te permitió mover el 14 de sitio en el método 2?",
        "insight": (
            "El método 2 solo es legal porque la suma es conmutativa y asociativa: puedes "
            "reordenar y reagrupar sin cambiar el resultado. Eso es exactamente lo que se "
            "formaliza en N3 (M01 y M02). Con la resta ese permiso desaparece — lo ves en el nodo siguiente."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "En el silo del granero hay 46 sacos y descargan 28 más. ¿Cuántos sacos hay?",
            "expr": r"46+28",
            "answer": "74",
            "hints": {
                "n1": "Las dos cantidades apuntan al mismo lado.",
                "n2": "Junta las dos: 46 + 28.",
                "n3": "46 + 20 = 66, y 66 + 8 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El silo del fondo abre el día debiendo 9 medidas y le descargan 15. ¿Cómo queda?",
            "expr": r"-9+15",
            "answer": "6",
            "hints": {
                "n1": "Los dos números apuntan a lados contrarios.",
                "n2": "Se cancelan hasta donde alcanza el menor: 9 con 9.",
                "n3": "Del 15 sobran 6, y apuntan hacia arriba.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "La balanza del granero pesa 1/4 de medida de mijo y le añaden 2/4 más. ¿Cuánto marca? (decimal)",
            "expr": r"\dfrac{1}{4}+\dfrac{2}{4}",
            "answer": "0,75",
            "hints": {
                "n1": "Las partes ya son del mismo tamaño: cuartos con cuartos.",
                "n2": "Junta los numeradores y deja el denominador: 3/4.",
                "n3": "3 ÷ 4 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un aprendiz escribe «-12 + 5 = -17». ¿Dónde está el error?",
            "options": [
                {
                    "id": "same_side",
                    "text": "Los sumó como si apuntaran al mismo lado; se cancelan y da -7",
                },
                {"id": "sign", "text": "El resultado debía ser 17 positivo"},
                {"id": "order", "text": "Cambió el orden de los sumandos"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "same_side",
            "feedback_by_option": {
                "same_side": "correct",
                "sign": "fb_e01_e4_sign",
                "order": "fb_e01_e4_order",
                "none": "fb_e01_e4_none",
            },
            "misconception_by_option": {
                "sign": "ignora_el_signo_al_sumar",
                "order": "resta_es_conmutativa",
                "none": "habito_valida_sin_verificar",
            },
            "hints": {
                "n1": "¿Los dos sumandos apuntan al mismo lado?",
                "n2": "Uno es negativo y el otro positivo: se cancelan entre sí.",
                "n3": "De −12 sobran 7 después de cancelar 5.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Si $a$ y $b$ son números cualesquiera, entonces $a+b>a$.»",
            "options": [
                {"id": "false_neg", "text": "Falsa: si b es negativo, a+b queda por debajo de a"},
                {"id": "true", "text": "Verdadera: sumar siempre agranda"},
                {"id": "false_always_less", "text": "Falsa: a+b siempre es menor que a"},
                {"id": "depends_a", "text": "Falsa: depende del signo de a, no del de b"},
            ],
            "expected": "false_neg",
            "feedback_by_option": {
                "false_neg": "correct",
                "true": "fb_e01_e5_trap",
                "false_always_less": "fb_e01_e5_always_less",
                "depends_a": "fb_e01_e5_depends_a",
            },
            "misconception_by_option": {
                "true": "sumar_siempre_agranda",
                "false_always_less": "sumar_siempre_achica",
                "depends_a": "atribuye_direccion_al_primer_sumando",
            },
            "hints": {
                "n1": "Para tumbar una afirmación «siempre» basta UN caso.",
                "n2": "Prueba con a = 5 y b = −3.",
                "n3": "5 + (−3) = 2, y 2 no es mayor que 5.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El granero abre el mes en 0. Entran 34 medidas, salen 51, entran 20. "
                "¿Con cuántas medidas cierra el mes?"
            ),
            "expr": r"0+34+(-51)+20",
            "answer": "3",
            "hints": {
                "n1": "Todo va a una sola columna, cada movimiento con su signo.",
                "n2": "34 + (−51) = −17.",
                "n3": "−17 + 20 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿En cuál de estos conjuntos la suma de dos elementos puede salirse del conjunto?",
            "options": [
                {"id": "irrationals", "text": "Los irracionales", "latex": r"\mathbb{I}"},
                {"id": "naturals", "text": "Los naturales", "latex": r"\mathbb{N}"},
                {"id": "integers", "text": "Los enteros", "latex": r"\mathbb{Z}"},
                {"id": "reals", "text": "Los reales", "latex": r"\mathbb{R}"},
            ],
            "expected": "irrationals",
            "feedback_by_option": {
                "irrationals": "correct",
                "naturals": "fb_e01_e7_closed",
                "integers": "fb_e01_e7_closed",
                "reals": "fb_e01_e7_closed",
            },
            "misconception_by_option": {
                "naturals": "confunde_cierre_de_suma_con_resta",
                "integers": "confunde_cierre_de_suma_con_resta",
                "reals": "confunde_cierre_de_suma_con_resta",
            },
            "hints": {
                "n1": "Busca dos números del conjunto cuya suma NO esté en el conjunto.",
                "n2": r"Prueba con $\sqrt{2}$ y $-\sqrt{2}$.",
                "n3": r"$\sqrt{2}+(-\sqrt{2})=0$, y 0 es racional, no irracional.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "La escalera de la suma",
        "title": "¿La suma de dos elementos del conjunto vive en el conjunto?",
        "intro": "Un conjunto es cerrado bajo la suma si nunca te obliga a salirte de él.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "yes",
                "latex": r"7+9=16\in\mathbb{N}",
                "note": "Juntar dos cantidades de contar da otra cantidad de contar.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "yes",
                "latex": r"120+(-145)=-25\in\mathbb{Z}",
                "note": "Con signos también cierra: por eso la suma pudo tragarse la columna de salidas.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"\dfrac{3}{4}+\dfrac{1}{2}=\dfrac{5}{4}\in\mathbb{Q}",
                "note": "Fracción más fracción da fracción.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\sqrt{2}+(-\sqrt{2})=0\in\mathbb{Q}",
                "note": "Dos irracionales pueden sumar un racional: el resultado SE SALE. Los irracionales no cierran bajo ninguna operación aritmética.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\pi+1\in\mathbb{R}",
                "note": "La unión de racionales e irracionales (B08) sí cierra: por eso la suma vive cómoda en ℝ.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"(2+3i)+(1-i)=3+2i",
                "note": "También cierra. Desvío opcional (B09).",
            },
        ],
        "outro": (
            "La suma cierra desde el primer peldaño: nunca te obligó a inventar un conjunto "
            "nuevo. La operación siguiente, la resta, sí lo hace."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"120+(-145)", r"\dfrac{3}{4}+\dfrac{1}{2}", r"60+(-18)"],
        "options": [
            {
                "id": "join",
                "text": "En los tres se juntan dos cantidades en una sola",
                "correct": True,
            },
            {
                "id": "grow",
                "text": "En los tres el resultado es mayor que el primer número",
                "correct": False,
            },
            {
                "id": "sign",
                "text": "En los tres el signo del sumando decide hacia dónde se mueve el resultado",
                "correct": True,
            },
            {"id": "integers", "text": "En los tres los números son enteros", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El granero cierra el año con este registro: −40 medidas heredadas del año "
            "anterior, entran 96, sale un pedido de 33 y entra media carreta de 8 medidas. "
            "¿Con cuántas medidas cierra?"
        ),
        "polya": {
            "comprender": "Me dan cuatro movimientos con signo y me piden el saldo final del granero.",
            "planear": "Los llevo todos a una sola columna con su signo y los sumo en orden.",
            "ejecutar": "−40 + 96 = 56 → 56 + (−33) = 23 → 23 + 8 = 31.",
            "comprobar": "Entradas: 96 + 8 = 104. Salidas y deuda: 40 + 33 = 73. 104 − 73 = 31. Cuadra.",
        },
        "prompt": "¿Con cuántas medidas cierra el granero?",
        "answer": "31",
        "hints": {
            "n1": "Escribe los cuatro movimientos con su signo antes de operar.",
            "n2": "−40 + 96 = 56.",
            "n3": "56 − 33 = 23, y le falta sumar 8.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: hoy decides el resultado por el signo, no por la costumbre.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué le pasa a un "
            "número cuando le sumas algo negativo."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Hay 26 medidas en el granero y entran 17. ¿Cuántas quedan?",
                "answer": "43",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $9+(-13)$?",
                "options": [
                    {"id": "minus_four", "text": "-4", "latex": r"-4"},
                    {"id": "four", "text": "4", "latex": r"4"},
                    {"id": "twenty_two", "text": "22", "latex": r"22"},
                ],
                "expected": "minus_four",
                "misconception_by_option": {
                    "four": "ignora_el_signo_al_sumar",
                    "twenty_two": "ignora_el_signo_al_sumar",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? «Existen $a$ y $b$ tales que $a+b<a$.»",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "sumar_siempre_agranda"},
                # Variante VERDADERA de la trampa E5, a propósito: comprueba el
                # criterio y no la heurística "afirmación general ⇒ falsa".
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
        "default": "Revisa hacia qué lado apunta cada sumando y vuelve a intentarlo.",
        "fb_e01_e4_sign": (
            "El signo del resultado no se elige aparte: sale de la cancelación. → Cancela 5 "
            "del −12 y di qué queda."
        ),
        "fb_e01_e4_order": (
            "El orden no es el problema: en la suma puedes cambiarlo sin que cambie el "
            "resultado. → Fíjate en si los sumandos apuntan al mismo lado."
        ),
        "fb_e01_e4_none": (
            "Compruébalo en la recta: parte de −12 y avanza 5 hacia la derecha. ¿Llegas a "
            "−17? → Di a qué número llegas."
        ),
        "fb_e01_e5_trap": (
            "Esa era la regla de cuando todos los números eran positivos. → Prueba con "
            "a = 5 y b = −3 y mira si se sostiene."
        ),
        "fb_e01_e5_always_less": (
            "Te pasaste al otro extremo: con b positivo sí crece. → Da un caso donde a+b sea "
            "mayor que a y otro donde sea menor."
        ),
        "fb_e01_e5_depends_a": (
            "Prueba a = −5 con b = 3 y luego a = 5 con b = 3: en los dos el resultado sube. "
            "→ Di qué signo es el que manda."
        ),
        "fb_e01_e7_closed": (
            "En ese conjunto la suma de dos elementos siempre se queda dentro. → Busca dos "
            "irracionales cuya suma sea 0."
        ),
    },
    "closing": (
        "Sumar es juntar, y el signo decide hacia dónde. La suma nunca te sacó de un "
        "conjunto; en el nodo siguiente la resta sí lo va a hacer, y de ahí nacieron los enteros."
    ),
    "validation_status": "F2_E01_11bloques",
}
