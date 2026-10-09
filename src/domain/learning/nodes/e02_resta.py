"""E02 · Resta — el orden no se puede dar vuelta.

Edificio del nodo: LA CASA DE CUENTAS (óbolos, deudas, saldos y el muro con la
línea del cero). Ningún otro edificio de N2 usa este oficio.
"""

NODE_ID = "PREALG-N2-E02-RESTA-QUITAR"
CONCEPT_SLUG = "resta"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "resta",
    "misconception": "resta_es_conmutativa",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La Casa de Cuentas · Resta",
    "building": "La Casa de Cuentas",
    "finish_label": "Salir hacia el Taller de Mosaicos",
    "title": "El orden no se puede dar vuelta",
    "intro": (
        "En el Granero podías cambiar los sumandos de sitio y no pasaba nada. Aquí no. "
        "Vas a ver qué significa exactamente 5 − 8, por qué durante siglos se dijo "
        "que «no se podía», y qué se rompe si le das vuelta a la resta para que quepa."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir la tablilla. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "El arca de la Casa tenía 23 óbolos y se prestaron 15. ¿Cuántos le quedan?",
                "answer": "8",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $6-11$?",
                "options": [
                    {"id": "minus_five", "text": "-5", "latex": r"-5"},
                    {"id": "five", "text": "5", "latex": r"5"},
                    {"id": "cannot", "text": "No se puede: 6 es menor que 11"},
                ],
                "expected": "minus_five",
                "misconception_by_option": {
                    "five": "resta_es_conmutativa",
                    "cannot": "resta_menor_menos_mayor_no_existe",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $9-4$ y $4-9$?",
                "options": [
                    {"id": "no", "text": "No: dan resultados distintos"},
                    {"id": "yes", "text": "Sí: la resta es como la suma, el orden da igual"},
                    {"id": "same_magnitude", "text": "Sí, porque las dos dan 5"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "resta_es_conmutativa",
                    "same_magnitude": "resta_es_conmutativa",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · Dentro de la Casa de Cuentas",
        "title": "El muro donde el cero es una línea",
        "body": (
            "El segundo edificio es la Casa de Cuentas: un salón con arcas al fondo y, en "
            "la pared, un muro de tablillas atravesado por una línea grabada. Lo que se "
            "tiene se anota por encima de la línea; lo que se debe, por debajo. La línea "
            "es el cero.\n\n"
            "El contador viejo, sin embargo, nunca escribía debajo de la línea: decía que "
            "restarle a lo poco lo mucho «no se puede anotar». Hoy entró un cliente con 7 "
            "óbolos y una deuda de 12. El contador le dio vuelta a la resta para que "
            "cupiera arriba y anotó 5. El cliente salió creyendo que le sobraban 5 óbolos."
        ),
        "question": "¿Puede una resta dar vuelta a sus dos números sin cambiar de significado?",
        "image": "/leccion/02-prealg-n2-mercado/e02-resta-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge la que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "Sí: 7 − 12 y 12 − 7 son la misma cuenta"},
                {"id": "b", "text": "No: son cuentas distintas y solo una describe al cliente"},
                {"id": "c", "text": "7 − 12 simplemente no existe"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir cuántos óbolos "
                "tenía realmente el cliente."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "La misma pareja, dos restas distintas",
        "body": (
            "Abajo están los mismos dos números en las dos restas posibles. Fíjate en "
            "qué pregunta responde cada una."
        ),
        "cases": [
            {
                "label": "Caso que funciona",
                "context": "El arca de la Casa tiene 12 óbolos y entrega 7",
                "fraction": r"12-7",
                "division": r"12-7=5",
                "note": "Pregunta: ¿cuánto le queda? Le quedan 5.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "El cliente tiene 7 óbolos y debe 12",
                "fraction": r"7-12",
                "division": r"7-12=-5",
                "note": "Pregunta: ¿cómo queda? Queda debiendo 5. No es lo mismo.",
            },
        ],
        "resolution": (
            "Los dos resultados tienen el mismo 5, y ahí está la trampa: parece que da "
            "igual el orden. Pero uno dice «me sobran 5» y el otro dice «debo 5». El "
            "signo no es un detalle de escritura: es la diferencia entre cobrar y pagar."
        ),
    },
    "definition_title": "La resta",
    "definition_katex": r"a-b=a+(-b)",
    "definition": (
        "Restar es quitar, o medir la distancia dirigida desde b hasta a. Restar b es "
        "lo mismo que sumar el opuesto de b: por eso la resta no necesita reglas nuevas, "
        "solo los negativos."
    ),
    "definition_symbols": [
        {
            "symbol": r"a",
            "reads": "minuendo",
            "means": "de lo que se quita; va primero y no se puede mover",
        },
        {"symbol": r"b", "reads": "sustraendo", "means": "lo que se quita"},
        {"symbol": r"a-b", "reads": "diferencia", "means": "el resultado"},
        {
            "symbol": r"-b",
            "reads": "el opuesto de b",
            "means": "el número que apunta al lado contrario (B05)",
        },
        {
            "symbol": r"a-b\neq b-a",
            "reads": "la resta no es conmutativa",
            "means": "cambiar el orden cambia el resultado; se formaliza en N3-M01",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Enteros",
            "title": "La cuenta del cliente",
            "statement": (
                "El cliente llega con 7 óbolos y debe 12 al prestamista. ¿Cómo queda su "
                "cuenta después de pagar todo lo que puede?"
            ),
            "latex": r"7-12",
            "image_slot": False,
            "steps": [
                "Tiene 7 y hay que quitarle 12: la resta se escribe 7 − 12, en ese orden.",
                "Convierto a suma: 7 − 12 = 7 + (−12). Restar es sumar el opuesto.",
                "7 y −12 apuntan a lados contrarios: se cancelan 7 con 7.",
                "Del −12 sobran 5 sin cancelar, y apuntan hacia abajo: −5.",
                "7 − 12 = −5. Queda debiendo 5 óbolos, no sobrándole 5.",
            ],
            "solution": r"$7-12=-5$",
            "self_explanation": {
                "step_index": 1,
                "prompt": "En el paso 2 la resta se convierte en suma. ¿Qué gano al reescribirla así?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Enteros con doble signo",
            "title": "Borrar una tablilla de debajo de la línea",
            "statement": (
                "En el muro, una cuenta está justo en la línea del cero y tiene colgada "
                "debajo una tablilla de deuda de 4 óbolos. Se descubre que esa deuda ya "
                "estaba pagada y se retira la tablilla. ¿En cuánto queda la cuenta?"
            ),
            "latex": r"0-(-4)",
            "image_slot": False,
            "steps": [
                "La cuenta parte en 0 y lo que se quita es una tablilla de −4.",
                "Escribo la resta: 0 − (−4).",
                "Restar es sumar el opuesto, y el opuesto de −4 es +4: 0 + 4.",
                "0 + 4 = 4. Quitar algo que colgaba POR DEBAJO de la línea sube la cuenta.",
                "Por eso menos por menos da más: no es una regla arbitraria, es qué pasa al retirar un déficit.",
            ],
            "solution": r"$0-(-4)=4$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El contador que dio vuelta la resta",
            "statement": (
                "La tablilla del contador viejo dice: «El cliente trae 7 y debe 12. Como "
                "7 − 12 no se puede anotar encima de la línea, escribo 12 − 7 = 5. Le "
                "sobran 5 óbolos»."
            ),
            "latex": r"7-12=12-7=5",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"7-12\;\underline{=}\;12-7",
            "error_note": "Ese signo igual es el error: 7 − 12 y 12 − 7 no son la misma cuenta.",
            "correct_version": {
                "wrong_latex": r"7-12=5",
                "right_latex": r"7-12=-5",
                "rows": [
                    {
                        "wrong": "Si el minuendo es menor, se da vuelta la resta",
                        "right": "El orden se respeta y el resultado sale negativo",
                    },
                    {
                        "wrong": "El cliente tiene 5 óbolos de sobra",
                        "right": "El cliente queda debiendo 5 óbolos",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 12 − 7 no responde la pregunta del cliente? Escribe la resta correcta.",
            "steps": [
                "Comprueba al revés: si al cliente le sobraran 5, tendría 12 óbolos, no 7.",
                "12 − 7 responde otra pregunta: cuánto le queda al ARCA de la Casa, no al cliente.",
                "La resta correcta es 7 − 12 = −5, y el signo dice quién le debe a quién.",
            ],
            "solution": (
                "Dar vuelta la resta para que «quepa» cambia la pregunta. Cuando el minuendo "
                "es menor, el resultado no deja de existir: se sale de los naturales y cae en "
                "los enteros. Para eso nacieron."
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
                "statement": "Un tejedor tenía 18 óbolos y pagó una multa de 25.",
                "given_steps": [
                    r"18-25=18+(-25)",
                    r"\text{se cancelan 18 con 18}",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"18-25=", "answer": "-7"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Una cuenta del muro estaba 3 óbolos por debajo de la línea y se le añaden 5 de deuda.",
                "given_steps": [
                    r"-3-5",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"-3-5=-3+(\square),\ \square=", "answer": "-5"},
                    {"id": "P2-b2", "label": r"-3-5=", "answer": "-8"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: en el muro, la cuenta de un naviero está 6 "
                    "óbolos por encima de la línea y la de un alfarero, 9 por debajo. "
                    "¿Cuántos óbolos separan una cuenta de la otra?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"6-(-9)=", "answer": "15"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma diferencia",
        "intro": r"¿Cuánto vale $-4-(-11)$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Convertir a suma del opuesto",
                "steps": [r"-4-(-11)", r"=-4+11", r"=7"],
                "note": "Siempre funciona: restar es sumar el opuesto.",
            },
            {
                "label": "Método 2 · Contar la distancia en la recta",
                "steps": [
                    r"\text{de }-11\text{ a }-4",
                    r"\text{avanzo }7\text{ hacia la derecha}",
                    r"=7",
                ],
                "note": "Ver la resta como distancia dirigida entre dos puntos.",
            },
        ],
        "question": "¿Cuál usarías con números grandes? ¿Y qué te dice el método 2 sobre el signo del resultado?",
        "insight": (
            "El método 2 explica el signo sin memorizar reglas: si vas hacia la derecha el "
            "resultado es positivo, si vas hacia la izquierda es negativo. Y deja ver por qué "
            "a − b y b − a solo se diferencian en el sentido del recorrido: mismo tramo, dirección contraria."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Un naviero llega con 92 óbolos y salda una deuda de 47. ¿Cuántos le quedan?",
            "expr": r"92-47",
            "answer": "45",
            "hints": {
                "n1": "El minuendo es lo que tenía.",
                "n2": "92 − 40 = 52.",
                "n3": "52 − 7 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Un aprendiz tenía 14 óbolos y debía pagar 31. ¿Cómo queda su cuenta?",
            "expr": r"14-31",
            "answer": "-17",
            "hints": {
                "n1": "Respeta el orden: primero lo que tiene.",
                "n2": "14 − 31 = 14 + (−31): se cancelan 14.",
                "n3": "Del −31 sobran 17, y apuntan hacia abajo.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Una cuenta está 6 óbolos por debajo de la línea y se le retira una deuda de 2. ¿En cuánto queda?",
            "expr": r"-6-(-2)",
            "answer": "-4",
            "hints": {
                "n1": "Restar un negativo es sumar su opuesto.",
                "n2": "−6 − (−2) = −6 + 2.",
                "n3": "Se cancelan 2 del −6.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un escriba anota «5 - 9 = 4». ¿Dónde está el error?",
            "options": [
                {"id": "swapped", "text": "Restó al revés: hizo 9 - 5. Lo correcto es -4"},
                {"id": "arith", "text": "Se equivocó en la aritmética: da 14"},
                {
                    "id": "sign_only",
                    "text": "El resultado debía ser 4 pero con otro signo por casualidad",
                },
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "swapped",
            "feedback_by_option": {
                "swapped": "correct",
                "arith": "fb_e02_e4_arith",
                "sign_only": "fb_e02_e4_sign_only",
                "none": "fb_e02_e4_none",
            },
            "misconception_by_option": {
                "arith": "confunde_resta_con_suma",
                "sign_only": "signo_es_decorativo",
                "none": "habito_valida_sin_verificar",
            },
            "hints": {
                "n1": "¿Qué número escribió primero y cuál está primero en el enunciado?",
                "n2": "9 − 5 = 4, pero la cuenta pedida era 5 − 9.",
                "n3": "5 − 9 = 5 + (−9) = −4.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para cualesquiera $a$ y $b$: $a-b=b-a$.»",
            "options": [
                {"id": "false_opposite", "text": "Falsa: dan opuestos, salvo cuando a = b"},
                {"id": "true", "text": "Verdadera: el orden no importa, como en la suma"},
                {"id": "false_never", "text": "Falsa: nunca pueden coincidir"},
                {"id": "true_positive", "text": "Verdadera solo si los dos son positivos"},
            ],
            "expected": "false_opposite",
            "feedback_by_option": {
                "false_opposite": "correct",
                "true": "fb_e02_e5_trap",
                "false_never": "fb_e02_e5_never",
                "true_positive": "fb_e02_e5_positive",
            },
            "misconception_by_option": {
                "true": "resta_es_conmutativa",
                "false_never": "olvida_el_caso_de_igualdad",
                "true_positive": "resta_es_conmutativa",
            },
            "hints": {
                "n1": "Prueba con a = 9 y b = 4.",
                "n2": "9 − 4 = 5 y 4 − 9 = −5. No son iguales.",
                "n3": "¿Hay algún par donde sí coincidan? Prueba a = b.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "En el muro, una cuenta está 8 óbolos por encima de la línea y otra 11 por "
                "debajo. ¿Cuántos óbolos separan la de abajo de la de arriba?"
            ),
            "expr": r"8-(-11)",
            "answer": "19",
            "hints": {
                "n1": "La distancia es la resta de los dos niveles.",
                "n2": "8 − (−11) = 8 + 11.",
                "n3": "Cuenta desde −11 hasta 0 y de 0 hasta 8.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál es el conjunto más pequeño de la escalera donde TODA resta tiene resultado?",
            "options": [
                {"id": "integers", "text": "Los enteros", "latex": r"\mathbb{Z}"},
                {"id": "naturals", "text": "Los naturales", "latex": r"\mathbb{N}"},
                {"id": "rationals", "text": "Los racionales", "latex": r"\mathbb{Q}"},
                {"id": "reals", "text": "Los reales", "latex": r"\mathbb{R}"},
            ],
            "expected": "integers",
            "feedback_by_option": {
                "integers": "correct",
                "naturals": "fb_e02_e7_naturals",
                "rationals": "fb_e02_e7_bigger",
                "reals": "fb_e02_e7_bigger",
            },
            "misconception_by_option": {
                "naturals": "resta_menor_menos_mayor_no_existe",
                "rationals": "no_busca_el_minimo",
                "reals": "no_busca_el_minimo",
            },
            "hints": {
                "n1": "Busca el primer peldaño donde 5 − 8 ya tiene respuesta.",
                "n2": "En ℕ la resta 5 − 8 se sale del conjunto.",
                "n3": "Piden el MÁS PEQUEÑO que sirva, no cualquiera que sirva.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "La escalera de la resta",
        "title": "¿La resta de dos elementos del conjunto vive en el conjunto?",
        "intro": "Aquí es donde la escalera dio su primer salto obligado.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"7-12\notin\mathbb{N}",
                "note": "El primer conjunto que se rompe: no hay natural que responda 7 − 12.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "yes",
                "latex": r"7-12=-5\in\mathbb{Z}",
                "note": "ℤ nació exactamente de esto (B05): darle respuesta a toda resta.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"\dfrac{1}{3}-\dfrac{3}{4}=-\dfrac{5}{12}\in\mathbb{Q}",
                "note": "Fracción menos fracción sigue siendo fracción.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\sqrt{5}-\sqrt{5}=0\in\mathbb{Q}",
                "note": "Dos irracionales pueden restar un racional: el resultado SE SALE. Ninguna operación aritmética los cierra.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\pi-3\in\mathbb{R}",
                "note": "ℝ = ℚ ∪ 𝕀 (B08) sí cierra: la resta vive cómoda ahí.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"(2+3i)-(1-i)=1+4i",
                "note": "También cierra. Desvío opcional (B09).",
            },
        ],
        "outro": (
            "La suma no rompió ningún peldaño; la resta rompió el primero. Ese es el motor de "
            "toda la escalera: una operación que no cabe obliga a inventar números nuevos."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"7-12", r"0-(-4)", r"12-7"],
        "options": [
            {
                "id": "order",
                "text": "En los tres el orden de los números cambia el resultado",
                "correct": True,
            },
            {"id": "negative", "text": "En los tres el resultado es negativo", "correct": False},
            {
                "id": "as_sum",
                "text": "Los tres se pueden reescribir como una suma del opuesto",
                "correct": True,
            },
            {
                "id": "naturals",
                "text": "En los tres los dos números son naturales",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "La cuenta del cliente cierra así en el muro: empezó debiendo 34 óbolos, "
            "pagó 20, y luego se le retiró una deuda de 9 que ya estaba saldada. "
            "¿Cuánto debe al final?"
        ),
        "polya": {
            "comprender": "Parto de −34, se paga 20 y se retira una deuda de 9. Me piden el saldo final.",
            "planear": "Escribo los tres movimientos en orden, respetando quién resta a quién.",
            "ejecutar": "−34 + 20 = −14 → −14 − (−9) = −14 + 9 = −5.",
            "comprobar": "Debía 34, cubrió 20 + 9 = 29, y 34 − 29 = 5 de deuda. Coincide con −5.",
        },
        "prompt": "¿Cuál es el saldo final del cliente?",
        "answer": "-5",
        "hints": {
            "n1": "Empieza en −34 y aplica un movimiento a la vez.",
            "n2": "−34 + 20 = −14.",
            "n3": "Retirar una deuda de 9 es −14 − (−9) = −14 + 9.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya respetas el orden de la resta aunque el minuendo sea menor.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué a − b y "
            "b − a no responden la misma pregunta."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "El arca tenía 41 óbolos y se prestaron 16. ¿Cuántos le quedan?",
                "answer": "25",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $4-13$?",
                "options": [
                    {"id": "minus_nine", "text": "-9", "latex": r"-9"},
                    {"id": "nine", "text": "9", "latex": r"9"},
                    {"id": "cannot", "text": "No se puede"},
                ],
                "expected": "minus_nine",
                "misconception_by_option": {
                    "nine": "resta_es_conmutativa",
                    "cannot": "resta_menor_menos_mayor_no_existe",
                },
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
                    "yes_always": "resta_es_conmutativa",
                },
                # Complemento de E5: allí la afirmación general era falsa; aquí se
                # comprueba que no se quedó con "la resta nunca coincide".
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
        "default": "Revisa cuál número va primero antes de operar y vuelve a intentarlo.",
        "fb_e02_e4_arith": (
            "La aritmética de las magnitudes está bien; el problema es el orden. → Escribe "
            "5 − 9 como suma del opuesto y resuélvela."
        ),
        "fb_e02_e4_sign_only": (
            "No es casualidad: el signo sale de que el minuendo es menor que el sustraendo. "
            "→ Di qué resultado da 5 − 9 y por qué."
        ),
        "fb_e02_e4_none": (
            "Compruébalo: si 5 − 9 fuera 4, entonces 4 + 9 debería dar 5. → Calcula 4 + 9."
        ),
        "fb_e02_e5_trap": (
            "Eso vale para la suma, no para la resta. → Calcula 9 − 4 y 4 − 9 y compara los dos."
        ),
        "fb_e02_e5_never": (
            "Casi: fallan casi siempre, pero hay un caso donde coinciden. → Prueba con a = 6 y b = 6."
        ),
        "fb_e02_e5_positive": (
            "Prueba con dos positivos distintos: 9 y 4. → Calcula las dos restas y compáralas."
        ),
        "fb_e02_e7_naturals": (
            "En ℕ la resta 7 − 12 no tiene respuesta: ese fue el peldaño que se rompió. "
            "→ Busca el siguiente."
        ),
        "fb_e02_e7_bigger": (
            "Ahí sí funciona, pero te piden el conjunto MÁS PEQUEÑO donde ya funciona. "
            "→ Baja un peldaño y comprueba si todavía sirve."
        ),
    },
    "closing": (
        "Restar es sumar el opuesto, y el orden manda. Aquí se rompió el primer peldaño de "
        "la escalera. En el nodo siguiente vas a ver qué le pasa a la multiplicación cuando "
        "el factor no es un número de contar."
    ),
    "validation_status": "F2_E02_11bloques",
}
