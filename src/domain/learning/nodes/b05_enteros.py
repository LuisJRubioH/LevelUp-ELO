"""B05 · Enteros — el signo es parte del número.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «−5 es mayor que −2 porque 5 es mayor que 2» (magnitud sin signo).
"""

NODE_ID = "PREALG-N1-B05-ENTEROS-DEUDA"
CONCEPT_SLUG = "enteros"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "enteros",
    "misconception": "magnitud_sin_signo",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Segundo peldaño · Enteros",
    "scene": {
        "image": "/leccion/00-comunes/step-enteros.png",
        "step": "integers",
        "aria": "Los enteros incluyen los negativos, el cero y los positivos",
    },
    "finish_label": "Continuar a racionales",
    "title": "El signo es parte del número",
    "intro": (
        "En el peldaño anterior la resta se quedó sin respuesta. Aquí vas a bajar del "
        "cero, a leer un número con su signo pegado, y a decidir cuál de dos deudas es "
        "peor — que no siempre es la que tiene el número más grande."
    ),
    # --- Bloque 2 · Mini-diagnóstico (siembra ELO, no puntúa) ----------------
    "diagnostic": {
        "intro": (
            "Antes de empezar, tres rápidas. No hay nota; me sirven para saber por "
            "dónde entrarle."
        ),
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál de estos dos números es MAYOR?",
                "options": [
                    {"id": "neg2", "text": "−2", "latex": r"-2"},
                    {"id": "neg5", "text": "−5", "latex": r"-5"},
                    {"id": "equal", "text": "Son iguales, solo cambia el tamaño"},
                ],
                "expected": "neg2",
                "misconception_by_option": {
                    "neg5": "magnitud_sin_signo",
                    "equal": "ignora_el_signo",
                },
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Debías 8 dracmas y pagaste 8. ¿Cómo queda tu cuenta?",
                "options": [
                    {"id": "zero", "text": "En 0: ni debes ni te deben", "latex": r"0"},
                    {"id": "still_owe", "text": "Sigues debiendo 8"},
                    {"id": "they_owe", "text": "Ahora te deben 8 a ti"},
                    {"id": "sixteen", "text": "La deuda sube a 16"},
                ],
                "expected": "zero",
                "misconception_by_option": {
                    "still_owe": "no_cancela_opuestos",
                    "they_owe": "invierte_el_signo",
                    "sixteen": "suma_magnitudes",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "El agua del pozo estaba 3 palmos bajo el brocal y bajó 4 palmos más. ¿Cuántos palmos bajo el brocal está ahora?",
                "answer": "7",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · El segundo peldaño",
        "title": "El libro del prestamista",
        "body": (
            "El prestamista del ágora lleva dos columnas en su libro: en una anota lo "
            "que le entregan, en la otra lo que le quedan debiendo. Nunca las mezcla, "
            "porque si las mezclara no sabría quién está en problemas.\n\n"
            "Hoy llegan dos discípulos. Uno le queda debiendo 2 dracmas. El otro le "
            "queda debiendo 5. El prestamista quiere anotar en una sola columna quién "
            "está mejor, y no le alcanzan los números del peldaño anterior."
        ),
        "question": "Si tuvieras que escribir las dos cuentas en UNA sola columna, ¿cómo distinguirías al que está mejor?",
        "image": "/leccion/01-prealg-n1-agora/b05-enteros-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que harías tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "El que debe 5 está mejor: su número es más grande"},
                {"id": "b", "text": "El que debe 2 está mejor: debe menos"},
                {"id": "c", "text": "No se puede comparar: las dos son deudas"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber por qué "
                "el número más grande puede ser el peor número."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos columnas que se vuelven una recta",
        "body": (
            "Mira los dos casos de abajo. En los dos hay un 5, pero ese 5 significa "
            "cosas opuestas — y en cuanto los pones en la misma recta, se ve."
        ),
        "cases": [
            {
                "label": "Caso que ya sabías",
                "context": "Un discípulo entrega 5 dracmas al prestamista",
                "fraction": r"+5",
                "division": r"0+5=5",
                "note": (
                    "Se mueve 5 pasos a la DERECHA del 0. Este es el 5 de siempre, el "
                    "que ya contabas en el peldaño anterior."
                ),
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Otro discípulo queda debiendo 5 dracmas",
                "fraction": r"-5",
                "division": r"0-5=-5",
                "note": (
                    "Se mueve 5 pasos a la IZQUIERDA del 0. Mismo tamaño, dirección "
                    "opuesta: −5 no es «5 en la otra columna», es otro número."
                ),
            },
        ],
        "resolution": (
            "El prestamista puede cerrar una columna. La recta hace el trabajo de las "
            "dos: a la derecha del 0 lo que se tiene, a la izquierda lo que se debe. "
            "Y ahora lo importante: en esa recta, −5 está MÁS A LA IZQUIERDA que −2. "
            "Más a la izquierda es menor. Deber 5 es peor que deber 2, y el número lo dice."
        ),
    },
    "definition_title": "Los números enteros",
    "definition_katex": r"\mathbb{Z}=\{\ldots,-3,-2,-1,0,1,2,3,\ldots\}",
    "definition": (
        "La frase del nodo: el signo no es un adorno que le cuelga al número — es parte "
        "del número. −5 y 5 son dos números distintos, no uno con dos disfraces."
    ),
    "definition_symbols": [
        {
            "symbol": r"\mathbb{Z}",
            "reads": "los enteros",
            "means": "del alemán Zahl, número: naturales, sus opuestos y el 0",
        },
        {
            "symbol": r"-a",
            "reads": "el opuesto de a",
            "means": "el que está a la misma distancia del 0, al otro lado",
        },
        {
            "symbol": r"|a|",
            "reads": "valor absoluto de a",
            "means": "la distancia al 0, sin mirar el lado: |−5| = 5",
        },
        {"symbol": r"<", "reads": "es menor que", "means": "está más a la izquierda en la recta"},
        {
            "symbol": r"\mathbb{N}\subset\mathbb{Z}",
            "reads": "ℕ está contenido en ℤ",
            "means": "no perdiste los naturales: siguen ahí, del lado derecho",
        },
        {
            "symbol": r"a+(-a)=0",
            "reads": "a más su opuesto da cero",
            "means": "pagar la deuda exacta deja la cuenta en 0",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Bajar del cero",
            "title": "El nivel del pozo",
            "statement": (
                "El agua del pozo está 2 palmos bajo el brocal. En la sequía baja 6 "
                "palmos más. ¿En qué nivel queda respecto al brocal?"
            ),
            "latex": r"-2-6",
            "image_slot": False,
            "steps": [
                "Pongo el brocal en el 0: arriba positivo, abajo negativo.",
                "El nivel de partida está bajo el brocal → −2, no 2.",
                "«Baja 6 más» es moverse 6 pasos hacia la izquierda: −2 − 6.",
                "Desde −2 avanzo 6 hacia la izquierda: −3, −4, −5, −6, −7, −8.",
                "−2 − 6 = −8. El agua está 8 palmos bajo el brocal.",
            ],
            "solution": r"$-2-6=-8$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 1,
                "prompt": (
                    "En el paso 2 escribí −2 y no 2, aunque el enunciado dice «2 palmos». "
                    "¿Qué información se habría perdido con el 2 solo?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · La deuda que se cancela",
            "title": "La cuenta del cantero",
            "statement": (
                "El cantero le debe 9 dracmas al prestamista. Entrega 9 dracmas de una "
                "vez. ¿Cómo queda su cuenta?"
            ),
            "latex": r"-9+9",
            "image_slot": False,
            "steps": [
                "La deuda de 9 se escribe −9: está a la izquierda del 0.",
                "Entregar 9 es moverse 9 pasos hacia la derecha: −9 + 9.",
                "Desde −9 avanzo 9 hacia la derecha y caigo justo en el 0.",
                "−9 + 9 = 0. Ni debe ni le deben.",
                "9 y −9 son opuestos: están a la misma distancia del 0, en lados contrarios.",
            ],
            "solution": r"$-9+9=0$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "La deuda que parecía mejor",
            "statement": (
                "Un discípulo revisó el libro del prestamista y anotó esto. Está mal: "
                "«Yo debo −5 dracmas y mi hermano debe −2. Como 5 es mayor que 2, "
                "entonces −5 > −2: yo estoy mejor que él»."
            ),
            "latex": r"-5>-2",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"-5\ \underline{>}\ -2",
            "error_note": (
                "Aquí se cayó. Comparó los tamaños (5 contra 2) y se olvidó del signo. "
                "Pero el signo dice de qué LADO del 0 está el número."
            ),
            "correct_version": {
                "wrong_latex": r"-5>-2",
                "right_latex": r"-5<-2",
                "rows": [
                    {
                        "wrong": "5 es mayor que 2, así que −5 es mayor que −2",
                        "right": "En la recta, −5 está más a la izquierda: es menor",
                    },
                    {
                        "wrong": "Deber 5 es mejor que deber 2",
                        "right": "Deber 5 es peor: te falta más para volver al 0",
                    },
                ],
            },
            "explain_prompt": ("¿Por qué −5 no es mayor que −2? Escribe la desigualdad corregida."),
            "steps": [
                "Dibuja la recta y marca el 0, el −2 y el −5.",
                "Fíjate cuál de los dos queda más lejos del 0 hacia la izquierda.",
                "Más a la izquierda es menor, sin importar qué tan grande se vea el número.",
            ],
            "solution": (
                "El tamaño del número (su valor absoluto) y su valor son cosas distintas "
                "en cuanto hay negativos. |−5| = 5 es más grande que |−2| = 2, y "
                "justamente por eso −5 < −2: cuanto más grande la deuda, peor la cuenta."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el procedimiento ya está "
            "empezado y solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "El agua del pozo está 4 palmos bajo el brocal y sube 6 palmos tras la lluvia.",
                "given_steps": [
                    r"\text{nivel inicial}=-4",
                    r"-4+6",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{Nivel final}=", "answer": "2"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": (
                    "El cantero debía 12 dracmas, entregó 5 y volvió a pedir 9 prestadas."
                ),
                "given_steps": [
                    r"\text{deuda inicial}=-12",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"-12+5=", "answer": "-7"},
                    {"id": "P2-b2", "label": r"-7-9=", "answer": "-16"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: la polis se fundó en el año que llamamos 0. "
                    "Un templo se levantó 40 años ANTES de la fundación y se derrumbó "
                    "25 años DESPUÉS de ella. ¿Cuántos años estuvo en pie?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Años en pie}=", "answer": "65"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos caminos para la misma cuenta",
        "intro": (
            r"El prestamista cierra el día así: le entregaron 7, prestó 12, le "
            r"entregaron 3. ¿Cómo queda? Las dos soluciones de abajo son correctas."
        ),
        "methods": [
            {
                "label": "Método 1 · Paso a paso en la recta",
                "steps": [r"0+7=7", r"7-12=-5", r"-5+3=-2"],
                "note": "Siempre funciona: te mueves de a un movimiento por vez.",
            },
            {
                "label": "Método 2 · Agrupar por signo",
                "steps": [r"(+7)+(+3)=+10", r"(-12)", r"10-12=-2"],
                "note": "Junta primero todo lo que entra y todo lo que sale.",
            },
        ],
        "question": (
            "¿Cuál conviene aquí y por qué? Y la de verdad: ¿cuál de los dos preferirías "
            "si el prestamista tuviera 30 movimientos en el día?"
        ),
        "insight": (
            "El método 2 gana cuando hay muchos movimientos, porque reordena sin cambiar "
            "el resultado. Y eso es exactamente una propiedad que todavía no has "
            "demostrado: la conmutativa y la asociativa de la suma (N3-M01 y N3-M02). "
            "Aquí la estás usando de contrabando; allá vas a ver por qué está permitida."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El tejedor debía 6 dracmas y pidió 5 más. ¿Cuánto debe ahora? (Responde con el entero, con signo.)",
            "expr": r"-6-5",
            "answer": "-11",
            "hints": {
                "n1": "Deber se escribe con signo negativo.",
                "n2": "Pedir más es alejarse del 0 hacia la izquierda.",
                "n3": "−6 − 5: cuenta 5 pasos a la izquierda desde −6.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El nivel del pozo está 9 palmos bajo el brocal y sube 9 palmos. ¿En qué nivel queda?",
            "expr": r"-9+9",
            "answer": "0",
            "hints": {
                "n1": "El brocal es el 0.",
                "n2": "Subir es moverse hacia la derecha.",
                "n3": "Un número y su opuesto se cancelan: dan 0.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "Ordena de MENOR a MAYOR: −7, 3, −1, 0. ¿Cuál es el orden correcto?",
            "options": [
                {"id": "ok", "text": "−7 · −1 · 0 · 3", "latex": r"-7<-1<0<3"},
                {"id": "by_size", "text": "0 · −1 · 3 · −7", "latex": r"0<-1<3<-7"},
                {"id": "neg_last", "text": "0 · 3 · −1 · −7", "latex": r"0<3<-1<-7"},
                {"id": "neg1_first", "text": "−1 · −7 · 0 · 3", "latex": r"-1<-7<0<3"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "by_size": "fb_b05_e3_size",
                "neg_last": "fb_b05_e3_negatives",
                "neg1_first": "fb_b05_e3_size",
            },
            "misconception_by_option": {
                "by_size": "magnitud_sin_signo",
                "neg_last": "negativos_despues_de_positivos",
                "neg1_first": "magnitud_sin_signo",
            },
            "hints": {
                "n1": "Dibuja la recta y marca los cuatro números.",
                "n2": "El orden de menor a mayor es el orden de izquierda a derecha.",
                "n3": "Todos los negativos van antes del 0, y −7 está más lejos que −1.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Teano revisa el libro y lee: «Debía 10, entregó 4, luego debe −14». "
                "¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "should_subtract",
                    "text": "Sumó la entrega a la deuda en vez de restarla: debe −6",
                },
                {"id": "sign", "text": "El resultado debía ser positivo: +14"},
                {"id": "initial", "text": "La deuda inicial estaba mal escrita"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "should_subtract",
            "feedback_by_option": {
                "should_subtract": "correct",
                "sign": "fb_b05_e4_sign",
                "initial": "fb_b05_e4_initial",
                "none": "fb_b05_e4_none",
            },
            "misconception_by_option": {
                "sign": "invierte_el_signo",
                "initial": "duda_del_dato_correcto",
                "none": "suma_magnitudes",
            },
            "hints": {
                "n1": "Entregar dinero, ¿acerca o aleja del 0?",
                "n2": "Acerca: mueve hacia la derecha, así que la deuda se achica.",
                "n3": "−10 + 4 = −6, no −14.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? $-8>-3$ porque $8>3$.",
            "options": [
                {"id": "false_left", "text": "Falsa: −8 está más a la izquierda, así que −8 < −3"},
                {"id": "true_size", "text": "Verdadera: 8 es mayor que 3"},
                {"id": "false_equal", "text": "Falsa: los dos son negativos, así que son iguales"},
                {"id": "cannot", "text": "No se pueden comparar dos negativos"},
            ],
            "expected": "false_left",
            "feedback_by_option": {
                "false_left": "correct",
                "true_size": "fb_b05_e5_trap",
                "false_equal": "fb_b05_e5_equal",
                "cannot": "fb_b05_e5_cannot",
            },
            "misconception_by_option": {
                "true_size": "magnitud_sin_signo",
                "false_equal": "ignora_el_signo",
                "cannot": "habito_evita_decidir",
            },
            "hints": {
                "n1": "Marca −8 y −3 en la recta. ¿Cuál queda más a la izquierda?",
                "n2": "Con negativos, cuanto más grande el número, más a la izquierda cae.",
                "n3": "−8 < −3. El tamaño (8 > 3) es cierto, pero el orden se invierte.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "Dos discípulos deben dinero. Uno debe 4 dracmas, el otro debe 11. El "
                "prestamista perdona 4 dracmas a cada uno. ¿Quién queda mejor y por qué?"
            ),
            "options": [
                {"id": "first_zero", "text": "El primero: llega a 0; el segundo sigue en −7"},
                {
                    "id": "second_more",
                    "text": "El segundo: le perdonaron más deuda proporcionalmente",
                },
                {"id": "same", "text": "Iguales: a los dos les perdonaron lo mismo"},
                {"id": "second_bigger", "text": "El segundo: su número sigue siendo más grande"},
            ],
            "expected": "first_zero",
            "feedback_by_option": {
                "first_zero": "correct",
                "second_more": "fb_b05_e6_proportion",
                "same": "fb_b05_e6_same",
                "second_bigger": "fb_b05_e6_bigger",
            },
            "misconception_by_option": {
                "second_more": "confunde_cambio_con_estado",
                "same": "confunde_cambio_con_estado",
                "second_bigger": "magnitud_sin_signo",
            },
            "hints": {
                "n1": "Calcula en qué número queda cada uno después del perdón.",
                "n2": "−4 + 4 = 0 y −11 + 4 = −7.",
                "n3": "0 está más a la derecha que −7: quedar en 0 es quedar mejor.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas operaciones NO tiene resultado dentro de los enteros?",
            "options": [
                {"id": "division", "text": "3 ÷ 4", "latex": r"3\div4"},
                {"id": "sub", "text": "3 − 40", "latex": r"3-40"},
                {"id": "sum", "text": "−12 + 5", "latex": r"-12+5"},
                {"id": "mult", "text": "−6 × 7", "latex": r"-6\times7"},
            ],
            "expected": "division",
            "feedback_by_option": {
                "division": "correct",
                "sub": "fb_b05_e7_closed",
                "sum": "fb_b05_e7_closed",
                "mult": "fb_b05_e7_closed",
            },
            "misconception_by_option": {
                "sub": "resta_no_cabe_en_enteros",
                "sum": "resta_no_cabe_en_enteros",
                "mult": "producto_negativo_no_es_entero",
            },
            "hints": {
                "n1": "Haz las cuatro y mira cuál da un resultado que no es entero.",
                "n2": "Restar, sumar y multiplicar enteros siempre dan enteros, aunque salgan negativos.",
                "n3": "3 ÷ 4 cae ENTRE 0 y 1: ahí no hay ningún entero. Ese es el próximo peldaño.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "La escalera de la necesidad",
        "title": "¿Toda resta de dos números del conjunto vive en el conjunto?",
        "intro": "Este peldaño nació justo de la pregunta que quedó abierta en B04.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"3-5\notin\mathbb{N}",
                "note": "Se salía: no había nada por debajo del 0.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "yes",
                "latex": r"3-5=-2\in\mathbb{Z}",
                "note": "El conjunto se hizo para esto: la resta ya siempre cabe.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"3\div4=\dfrac{3}{4}\in\mathbb{Q}",
                "note": "Pero la DIVISIÓN todavía no cabe en ℤ: eso abre B06.",
            },
        ],
        "outro": (
            "Cerraste la resta y ganaste una recta completa. Pero 3 ÷ 4 sigue sin tener "
            "casa: cae entre el 0 y el 1, donde no hay enteros. El siguiente peldaño "
            "nace de ese hueco."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué estructura comparten los tres problemas de este nodo?",
        "thumbnails": [r"-2-6", r"-9+9", r"-5<-2"],
        "options": [
            {
                "id": "line",
                "text": "Los tres se resuelven moviéndose en una recta con el 0 en el centro",
                "correct": True,
            },
            {
                "id": "sign",
                "text": "En los tres el signo cambia el significado del número",
                "correct": True,
            },
            {
                "id": "negative_result",
                "text": "Los tres terminan en un número negativo",
                "correct": False,
            },
            {"id": "money", "text": "Los tres hablan de dinero", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El prestamista cierra la semana: el lunes le entregaron 15 dracmas, el "
            "martes prestó 23, el jueves le entregaron 6 y el viernes prestó 4. "
            "¿Con qué número cierra la semana?"
        ),
        "polya": {
            "comprender": (
                "Me dan cuatro movimientos: dos entradas (15 y 6) y dos salidas (23 y 4). "
                "Me piden el saldo final con su signo."
            ),
            "planear": (
                "Agrupo por signo: sumo todo lo que entra, sumo todo lo que sale, y "
                "comparo los dos montones en la recta."
            ),
            "ejecutar": "Entra: 15 + 6 = 21. Sale: 23 + 4 = 27. Saldo: 21 − 27 = −6.",
            "comprobar": (
                "Paso a paso: 0 + 15 = 15 → 15 − 23 = −8 → −8 + 6 = −2 → −2 − 4 = −6. ✓ "
                "Mismo resultado por los dos caminos. Y el signo importa: cierra debiendo, "
                "no teniendo."
            ),
        },
        "prompt": "¿Con qué número cierra la semana? (Con signo.)",
        "answer": "-6",
        "hints": {
            "n1": "Separa lo que entra de lo que sale.",
            "n2": "Entra 21 en total; sale 27 en total.",
            "n3": "21 − 27 se va por debajo del 0.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico ----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota: solo miramos si algo se movió.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: hoy resolviste más que al entrar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el "
            "número más grande puede ser el menor."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál de estos dos números es MENOR?",
                "options": [
                    {"id": "neg9", "text": "−9", "latex": r"-9"},
                    {"id": "neg4", "text": "−4", "latex": r"-4"},
                    {"id": "equal", "text": "Son iguales"},
                ],
                # Inversa del D1 a propósito: allá se preguntó el mayor, aquí el
                # menor. Contesta bien quien usa la recta, no quien memorizó.
                "expected": "neg9",
                "misconception_by_option": {
                    "neg4": "magnitud_sin_signo",
                    "equal": "ignora_el_signo",
                },
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Debías 14 dracmas y entregaste 14. ¿En qué número queda tu cuenta?",
                "answer": "0",
            },
            {
                "id": "PD3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "El agua estaba 5 palmos bajo el brocal y bajó 3 más. ¿En qué número queda respecto al brocal? (Con signo.)",
                "answer": "-8",
            },
        ],
    },
    # --- Bloque 11 · Footer + feedback ---------------------------------------
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
        "default": "Revisa el procedimiento paso a paso y vuelve a intentarlo.",
        "fb_b05_e3_size": (
            "Ordenaste por tamaño y te olvidaste del lado. En la recta, los negativos "
            "van todos ANTES del 0, y el más grande es el que queda más lejos a la "
            "izquierda. → Marca los cuatro en la recta y léelos de izquierda a derecha."
        ),
        "fb_b05_e3_negatives": (
            "Los negativos no van al final: van antes del 0. Todo lo que está a la "
            "izquierda del 0 es menor que el 0. → Ubica −1 y −7 respecto al 0."
        ),
        "fb_b05_e4_sign": (
            "Debía, así que el resultado sigue siendo una deuda: negativo. El fallo está "
            "en el tamaño, no en el signo. → Calcula −10 + 4."
        ),
        "fb_b05_e4_initial": (
            "La deuda inicial está bien escrita: debía 10, o sea −10. El error aparece "
            "al aplicar la entrega. → Haz −10 + 4 y compara con lo que anotó."
        ),
        "fb_b05_e4_none": (
            "Compruébalo al revés: si debe −14 después de entregar 4, entregar le habría "
            "AUMENTADO la deuda. → Di si entregar acerca o aleja del 0."
        ),
        "fb_b05_e5_trap": (
            "8 > 3 es cierto, y por eso mismo −8 < −3: cuanto más grande el número, más "
            "a la izquierda cae. El tamaño y el orden se invierten al cruzar el 0. → "
            "Marca −8 y −3 en la recta."
        ),
        "fb_b05_e5_equal": (
            "Ser los dos negativos no los hace iguales, igual que ser los dos positivos "
            "no haría iguales a 8 y 3. → Di cuál de los dos está más lejos del 0."
        ),
        "fb_b05_e5_cannot": (
            "Sí se pueden comparar: para eso es la recta. Todo par de enteros tiene uno "
            "más a la izquierda. → Ubica −8 y −3 y di cuál va primero."
        ),
        "fb_b05_e6_proportion": (
            "Estás mirando el CAMBIO (cuánto le perdonaron) en vez del ESTADO (en qué "
            "número quedó). Les perdonaron lo mismo a los dos. → Calcula en qué número "
            "queda cada uno."
        ),
        "fb_b05_e6_same": (
            "El perdón fue igual, pero no partían del mismo lugar. → Calcula −4 + 4 y "
            "−11 + 4 y compara los dos resultados."
        ),
        "fb_b05_e6_bigger": (
            "Ese es justo el error del nodo: con negativos, el número más grande es el "
            "peor. −7 está más a la izquierda que 0. → Di cuál de los dos resultados "
            "queda más cerca del 0."
        ),
        "fb_b05_e7_closed": (
            "Esa sí cabe: sumar, restar y multiplicar enteros siempre dan enteros, "
            "aunque el resultado sea negativo. → Busca la que cae ENTRE dos enteros."
        ),
    },
    "closing": (
        "El signo no acompaña al número: es el número. Ya cerraste la resta. En el "
        "siguiente nodo la división te va a dejar sin casa otra vez."
    ),
    "validation_status": "F1_B05_11bloques",
}
