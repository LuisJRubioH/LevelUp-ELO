"""R03 · El pan de oro — subir y bajar lo mismo no devuelve al punto de partida.

Tercera sala del taller del canon. Guía: Iuty. Vocabulario propio: pan de oro,
lámina, hoja, batihoja, merma, encargo. Nada de cuadrículas ni bocetos (R01),
tinas ni brazadas (R02), ni lámparas (R04).

Error focal: creer que un recargo y un descuento del mismo tanto por ciento se
cancelan. No se cancelan porque el segundo se aplica sobre una base distinta.
"""

NODE_ID = "ALG-N1-R03-PORCENTAJES"
CONCEPT_SLUG = "porcentajes"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "porcentajes",
    "misconception": "descuento_y_recargo_se_cancelan",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El pan de oro · Porcentajes",
    "house": "El pan de oro",
    "guide": "Iuty",
    "finish_label": "Bajar a la sala de las lámparas",
    "title": "Subir y bajar lo mismo no devuelve al punto de partida",
    "intro": (
        "Un porcentaje es una razón con el denominador fijado en cien. Eso lo hace cómodo "
        "de comparar y peligroso de encadenar: el segundo cambio nunca se aplica sobre lo "
        "mismo que el primero."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar al obrador. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es el 10 % de 200 láminas?",
                "answer": "20",
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es el 25 % de 80 láminas?",
                "answer": "20",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si un encargo de 100 láminas sube un 10 % y luego baja un 10 %, ¿queda en 100?",
                "options": [
                    {"id": "no", "text": "No: queda en 99"},
                    {"id": "yes", "text": "Sí: sube 10 y baja 10"},
                    {"id": "more", "text": "No: queda en 101"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "descuento_y_recargo_se_cancelan",
                    "more": "descuento_y_recargo_se_cancelan",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/r03-porcentajes-katia.png",
        "eyebrow": "KatIA · En el obrador del pan de oro",
        "title": "Las cuatro láminas que faltaron",
        "body": (
            "El batihoja aplasta el oro hasta dejarlo en hojas finísimas. Se cuentan por "
            "láminas y no se pueden improvisar: el oro llega pesado desde el tesoro.\n\n"
            "Iuty repasa el encargo del muro:\n\n"
            "«Eran cien láminas. El maestro mandó ampliar el friso y subimos el encargo un "
            "veinte por ciento. A los tres días recortaron el friso y el encargo bajó un "
            "veinte por ciento.»\n\n"
            "«El escriba anotó que volvíamos a estar en cien y pidió el oro de cien. "
            "Llegaron noventa y seis láminas y el batihoja no puede fabricar las otras "
            "cuatro: el oro que falta no está en el obrador, está en el tesoro.»"
        ),
        "question": "Si algo sube un tanto por ciento y luego baja el mismo, ¿vuelve a donde estaba?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Sí: lo que sube y baja lo mismo se compensa"},
                {"id": "b", "text": "No: el segundo cambio se calcula sobre una cantidad distinta"},
                {"id": "c", "text": "Depende de si primero sube o primero baja"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decir, sin calcular, qué "
                "porcentaje de bajada SÍ deshace una subida del veinte por ciento."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo veinte por ciento, dos cantidades distintas",
        "body": "Un porcentaje no es una cantidad: es una parte DE algo. Y ese algo cambió.",
        "cases": [
            {
                "label": "La subida",
                "context": "El 20 % de las 100 láminas del encargo original",
                "fraction": r"20\%\ \text{de}\ 100",
                "division": r"100+20=120",
                "note": "Veinte láminas más. La base del cálculo eran 100.",
            },
            {
                "label": "La bajada",
                "context": "El 20 % de las 120 láminas que ya había",
                "fraction": r"20\%\ \text{de}\ 120",
                "division": r"120-24=96",
                "note": "Veinticuatro láminas menos, no veinte. La base ya no era 100.",
            },
        ],
        "resolution": (
            "El porcentaje que baja es el mismo, pero se aplica a una cantidad mayor, así "
            "que quita más de lo que había puesto. Escrito con factores queda a la vista: "
            "subir un 20 % es multiplicar por 1,20 y bajar un 20 % es multiplicar por 0,80, "
            "y 1,20 · 0,80 = 0,96. Nunca da 1."
        ),
    },
    "definition_title": "Porcentaje y factor de variación",
    "definition_katex": r"p\%\ \text{de}\ N=\dfrac{p}{100}\,N\qquad N\xrightarrow{+p\%} N\Bigl(1+\dfrac{p}{100}\Bigr)",
    "definition": (
        "Un PORCENTAJE es una razón de denominador 100: el p % de N es (p/100) · N. "
        "AUMENTAR un p % es multiplicar por 1 + p/100 y DISMINUIR un p % es multiplicar por "
        "1 − p/100. Encadenar varios cambios es multiplicar sus factores, y por eso los "
        "porcentajes no se suman ni se cancelan entre sí."
    ),
    "definition_symbols": [
        {"symbol": r"\dfrac{p}{100}", "reads": "por ciento", "means": "una razón con el denominador fijado en cien"},
        {"symbol": r"1{,}20", "reads": "factor de subida", "means": "aumentar un 20 % en un solo paso"},
        {"symbol": r"0{,}80", "reads": "factor de bajada", "means": "disminuir un 20 % en un solo paso"},
        {"symbol": r"1{,}20\cdot 0{,}80=0{,}96", "reads": "encadenar", "means": "dos cambios seguidos: los factores se multiplican"},
        {"symbol": r"1{,}25\cdot 0{,}80=1", "reads": "el que sí deshace", "means": "bajar un 20 % se deshace subiendo un 25 %"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La merma del batido",
            "title": "Calcular una parte de cien",
            "statement": (
                "De cada encargo de 240 láminas, el 15 % se pierde en merma al batir el "
                "oro. ¿Cuántas láminas se pierden?"
            ),
            "latex": r"15\%\ \text{de}\ 240",
            "image_slot": False,
            "steps": [
                "El 15 % significa 15 de cada 100: la razón es 15/100.",
                "Aplico la razón a las 240 láminas: (15/100) · 240.",
                "15 · 240 = 3600, y 3600 ÷ 100 = 36.",
                "Se pierden 36 láminas y quedan 204.",
                "Compruebo: el 10 % son 24 y el 5 % son 12; 24 + 12 = 36 ✓.",
            ],
            "solution": r"$36$ láminas",
            "self_explanation": {
                "step_index": 1,
                "prompt": "¿Por qué el 15 % de 240 no son 15 láminas?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Ampliar el encargo",
            "title": "Subir un porcentaje en un solo paso",
            "statement": (
                "El encargo era de 240 láminas y el maestro pide ampliarlo un 15 %. "
                "¿Cuántas láminas se encargan?"
            ),
            "latex": r"240\cdot 1{,}15",
            "image_slot": False,
            "steps": [
                "Puedo calcular el 15 % y sumarlo: 240 + 36 = 276.",
                "O hacerlo de una vez: quedarse con el 100 % y añadir el 15 % es el 115 %.",
                "El 115 % es el factor 1,15.",
                "240 · 1,15 = 276 láminas.",
                "Las dos maneras dan lo mismo; la segunda es la que se puede encadenar.",
            ],
            "solution": r"$276$ láminas",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que dio por compensados los dos cambios",
            "statement": (
                "Vuelve el encargo de la apertura: 100 láminas, un 20 % más y después un "
                "20 % menos. El escriba anotó 100 y pidió el oro de 100."
            ),
            "latex": r"100\xrightarrow{+20\%}\;\xrightarrow{-20\%}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"+20\%-20\%=0\%",
            "error_note": (
                "Restó los porcentajes como si fueran cantidades. Pero el 20 % de subida "
                "salió de 100 y el 20 % de bajada salió de 120: no son la misma lámina."
            ),
            "correct_version": {
                "wrong_latex": r"100\to 120\to 100",
                "right_latex": r"100\to 120\to 96",
                "rows": [
                    {"wrong": "Sube 20 y baja 20",
                     "right": "Sube 20 y baja 24, porque baja sobre 120"},
                    {"wrong": r"1{,}20-0{,}20=1",
                     "right": r"1{,}20\cdot 0{,}80=0{,}96"},
                ],
            },
            "explain_prompt": (
                "Explica por qué el resultado es menor que el de partida pase lo que pase, "
                "y di qué porcentaje de subida sí habría devuelto las 100 láminas."
            ),
            "steps": [
                "Escribo los dos cambios como factores: 1,20 y 0,80.",
                "Los multiplico: 0,96. Es menor que 1, así que siempre se pierde.",
                "Regla para no volver a caer: los porcentajes encadenados se multiplican, nunca se suman ni se restan.",
            ],
            "solution": (
                "Quedan 96 láminas. Para volver a 100 desde 120 habría que bajar un 16,67 %, "
                "y para volver a 120 desde 96, subir un 25 %: el porcentaje que deshace "
                "nunca es el mismo que el que hizo."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El encargo va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Calcula el 20 % de 350 láminas.",
                "given_steps": [r"\dfrac{20}{100}\cdot 350", r"\dfrac{7000}{100}"],
                "blanks": [{"id": "P1-b1", "label": r"7000\div 100=", "answer": "70"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Un encargo de 400 láminas sube un 25 %. ¿Cuántas quedan?",
                "given_steps": [r"400\cdot 1{,}25"],
                "blanks": [
                    {"id": "P2-b1", "label": r"25\%\ \text{de}\ 400=", "answer": "100"},
                    {"id": "P2-b2", "label": r"400+100=", "answer": "500"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: 200 láminas suben un 10 % y después bajan un "
                    "10 %. ¿Cuántas quedan?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"200\cdot 1{,}10\cdot 0{,}90=", "answer": "198"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de aplicar dos cambios seguidos",
        "intro": r"$300$ láminas suben un $10\,\%$ y después bajan un $30\,\%$.",
        "methods": [
            {
                "label": "Método 1 · Paso a paso",
                "steps": [
                    r"10\%\ \text{de}\ 300=30\Rightarrow 330",
                    r"30\%\ \text{de}\ 330=99",
                    r"330-99=231",
                ],
                "note": "Cada paso se entiende, pero hay que recalcular el porcentaje sobre la nueva base.",
            },
            {
                "label": "Método 2 · Multiplicar los factores",
                "steps": [
                    r"1{,}10\cdot 0{,}70=0{,}77",
                    r"300\cdot 0{,}77",
                    r"231",
                ],
                "note": "Un solo producto, y el 0,77 dice de golpe que se ha perdido un 23 %.",
            },
        ],
        "question": "¿Qué te dice el 0,77 que no te dicen los pasos intermedios?",
        "insight": (
            "Que el resultado de los dos cambios juntos es una bajada del 23 %, no del "
            "20 % que saldría de restar 30 − 10. El método paso a paso llega al mismo "
            "número sin que llegues a saber eso, y ahí es donde se cuela la idea de que "
            "los porcentajes se suman. El factor combinado es la respuesta a «¿y en total, "
            "cuánto?», que suele ser la pregunta que importa."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuánto es el 12 % de 450 láminas?",
            "expr": r"\dfrac{12}{100}\cdot 450",
            "answer": "54",
            "hints": {
                "n1": "El 12 % es 12 de cada 100.",
                "n2": "El 1 % de 450 son 4,5 láminas.",
                "n3": "12 · 4,5 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Un encargo de 500 láminas se reduce un 18 %. ¿Cuántas láminas quedan?",
            "expr": r"500\cdot 0{,}82",
            "answer": "410",
            "hints": {
                "n1": "Bajar un 18 % es quedarse con el 82 %.",
                "n2": "El 18 % de 500 son 90.",
                "n3": "500 − 90 = …",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "200 láminas suben un 10 % y después bajan un 10 %. ¿Cuántas quedan?",
            "options": [
                {"id": "ok", "text": "198"},
                {"id": "same", "text": "200"},
                {"id": "up", "text": "202"},
                {"id": "down", "text": "180"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "same": "fb_r03_e3_same",
                "up": "fb_r03_e3_up",
                "down": "fb_r03_e3_down",
            },
            "misconception_by_option": {
                "same": "descuento_y_recargo_se_cancelan",
                "up": "descuento_y_recargo_se_cancelan",
                "down": "suma_los_porcentajes",
            },
            "hints": {
                "n1": "La subida se calcula sobre 200; la bajada, sobre 220.",
                "n2": "El 10 % de 220 son 22, no 20.",
                "n3": "220 − 22 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un escriba anota: «el encargo bajó un 30 % y luego subió un 30 %, así que "
                "está como al principio». ¿Dónde está el error?"
            ),
            "options": [
                {"id": "base", "text": r"La subida se aplica sobre una cantidad menor: queda en el $91\,\%$"},
                {"id": "order", "text": "El error es el orden: si primero sube sí vuelve"},
                {"id": "calc", "text": "Calculó mal el 30 %"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "base",
            "feedback_by_option": {
                "base": "correct",
                "order": "fb_r03_e4_order",
                "calc": "fb_r03_e4_calc",
                "none": "fb_r03_e4_none",
            },
            "misconception_by_option": {
                "order": "el_orden_de_los_porcentajes_importa",
                "calc": "suma_los_porcentajes",
                "none": "descuento_y_recargo_se_cancelan",
            },
            "hints": {
                "n1": "Escribe los dos cambios como factores.",
                "n2": "0,70 · 1,30 = 0,91.",
                "n3": "0,91 no es 1: falta un 9 %.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Subir un 20 % y después bajar un 20 % deja la "
                "cantidad como estaba.»"
            ),
            "options": [
                {"id": "false", "text": r"Falsa: queda en el $96\,\%$, porque la bajada se aplica sobre más"},
                {"id": "true", "text": "Verdadera: se sube y se baja lo mismo"},
                {"id": "true_order", "text": "Verdadera si se hace en ese orden y no al revés"},
                {"id": "false_more", "text": r"Falsa: queda por encima, en el $104\,\%$"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_r03_e5_trap",
                "true_order": "fb_r03_e5_order",
                "false_more": "fb_r03_e5_more",
            },
            "misconception_by_option": {
                "true": "descuento_y_recargo_se_cancelan",
                "true_order": "el_orden_de_los_porcentajes_importa",
                "false_more": "descuento_y_recargo_se_cancelan",
            },
            "hints": {
                "n1": "Prueba con 100 láminas y sigue las dos cuentas.",
                "n2": "100 → 120 → 96.",
                "n3": "La bajada quitó 24, no 20.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (
                "Selecciona TODAS las parejas de cambios que devuelven la cantidad exacta "
                "de partida."
            ),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": "Subir un 25 % y luego bajar un 20 %"},
                {"id": "b", "text": "Subir un 20 % y luego bajar un 20 %"},
                {"id": "c", "text": "Subir un 100 % y luego bajar un 50 %"},
                {"id": "d", "text": "Bajar un 10 % y luego subir un 10 %"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Multiplica los dos factores de cada pareja.",
                "n2": "1,25 · 0,80 y 2 · 0,50 dan exactamente 1.",
                "n3": "Los otros dos dan 0,96 y 0,99.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El obrador recibe 800 láminas. Un 25 % se aparta para el friso y del "
                "resto se pierde un 20 % en merma. ¿Cuántas láminas quedan utilizables "
                "después de la merma?"
            ),
            "expr": r"800\cdot 0{,}75\cdot 0{,}80",
            "answer": "480",
            "hints": {
                "n1": "Apartar el 25 % deja el 75 %.",
                "n2": "El 75 % de 800 son 600.",
                "n3": "Perder el 20 % de 600 deja …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Vuelve al valor de partida?",
        "title": "Qué parejas de cambios se deshacen y cuáles no",
        "intro": (
            "Encadenar dos porcentajes es multiplicar dos factores. Que la pareja se "
            "deshaga significa una sola cosa: que su producto valga exactamente 1."
        ),
        "rows": [
            {"symbol": r"+20\%\ \text{y}\ -20\%", "name": "El mismo tanto por ciento", "closed": "no",
             "latex": r"1{,}20\cdot 0{,}80=0{,}96",
             "note": "Se pierde un 4 %. La bajada actúa sobre más de lo que había. Es el caso focal."},
            {"symbol": r"-20\%\ \text{y}\ +20\%", "name": "Al revés", "closed": "no",
             "latex": r"0{,}80\cdot 1{,}20=0{,}96",
             "note": "Sale exactamente lo mismo: el orden no arregla nada, porque el producto no cambia."},
            {"symbol": r"+20\%\ \text{y}\ +20\%", "name": "Dos subidas iguales", "closed": "no",
             "latex": r"1{,}20\cdot 1{,}20=1{,}44",
             "note": "Un 44 % más, no un 40 %. Los porcentajes tampoco se suman entre sí."},
            {"symbol": r"+25\%\ \text{y}\ -20\%", "name": "La pareja que sí vuelve", "closed": "yes",
             "latex": r"1{,}25\cdot 0{,}80=1",
             "note": "Existe el porcentaje que deshace: nunca es el mismo número que lo hizo."},
            {"symbol": r"+100\%\ \text{y}\ -50\%", "name": "Doblar y quitar la mitad", "closed": "yes",
             "latex": r"2\cdot 0{,}5=1",
             "note": "El mismo caso con números grandes: 100 y 50 no se parecen y aun así se deshacen."},
            {"symbol": r"-100\%", "name": "Bajar del todo", "closed": "partial",
             "latex": r"N\cdot 0=0",
             "note": "El único cambio sin vuelta: multiplicado por cero, ningún porcentaje posterior recupera nada."},
        ],
        "outro": (
            "Las tres primeras filas dicen lo mismo desde ángulos distintos: los "
            "porcentajes no se suman ni se restan, se multiplican como factores. La cuarta "
            "y la quinta son la parte útil — sí existe el cambio que deshace, y para "
            "encontrarlo hay que preguntarse qué número multiplicado por el primero da 1. "
            "Es el recíproco, el mismo que aprendiste a usar en el silo de simiente."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres encargos trabajados en este nodo?",
        "thumbnails": [r"15\%\ \text{de}\ 240", r"240\cdot 1{,}15", r"1{,}20\cdot 0{,}80"],
        "options": [
            {"id": "base", "text": "En los tres el porcentaje se calcula siempre sobre una cantidad concreta, y hay que saber cuál", "correct": True},
            {"id": "factor", "text": "En los tres el cambio se puede escribir como multiplicar por un factor", "correct": True},
            {"id": "add", "text": "En los tres los porcentajes se pueden sumar o restar entre sí", "correct": False},
            {"id": "fixed", "text": "En los tres un mismo porcentaje representa siempre la misma cantidad de láminas", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Encargo de cierre del obrador. Llegan 900 láminas de pan de oro. El maestro "
            "amplía el friso y el encargo sube un 20 %; al día siguiente lo recorta y baja "
            "un 25 %. ¿Cuántas láminas quedan encargadas?"
        ),
        "polya": {
            "comprender": "Son dos cambios encadenados, y el segundo se aplica sobre el resultado del primero.",
            "planear": "Escribo los factores: 1,20 y 0,75. Los multiplico y aplico el resultado a las 900.",
            "ejecutar": "1,20 · 0,75 = 0,90, y 900 · 0,90 = 810 láminas.",
            "comprobar": "Paso a paso: 900 → 1080 → 810 ✓. Restando porcentajes habría salido 900 · 0,95 = 855, que son 45 láminas de oro que nadie tiene.",
        },
        "prompt": "¿Cuántas láminas quedan encargadas?",
        "answer": "810",
        "hints": {
            "n1": "Subir un 20 % es multiplicar por 1,20; bajar un 25 %, por 0,75.",
            "n2": "1,20 · 0,75 = 0,90.",
            "n3": "El 90 % de 900 es …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otro encargo. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya multiplicas factores en vez de sumar porcentajes.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo sobre qué "
            "cantidad se calcula cada porcentaje."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es el 10 % de 350 láminas?",
                "answer": "35",
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es el 20 % de 60 láminas?",
                "answer": "12",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si un encargo de 200 láminas baja un 10 % y luego sube un 10 %, ¿queda en 200?",
                "options": [
                    {"id": "no", "text": "No: queda en 198"},
                    {"id": "yes", "text": "Sí: baja 20 y sube 20"},
                    {"id": "more", "text": "No: queda en 202"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "descuento_y_recargo_se_cancelan",
                    "more": "descuento_y_recargo_se_cancelan",
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
        "default": "Escribe cada cambio como un factor y multiplícalos: los porcentajes no se suman.",
        "fb_r03_e3_same": (
            "La subida salió de 200 y la bajada, de 220. → El 10 % de 220 son 22, no 20."
        ),
        "fb_r03_e3_up": (
            "Encadenar una subida y una bajada iguales siempre pierde, nunca gana. → 1,10 · 0,90 = 0,99."
        ),
        "fb_r03_e3_down": (
            "Ahí se restó un 20 % de golpe. → Los dos cambios eran del 10 % cada uno."
        ),
        "fb_r03_e4_order": (
            "El producto de los factores no cambia con el orden. → 0,70 · 1,30 y 1,30 · 0,70 dan 0,91."
        ),
        "fb_r03_e4_calc": (
            "El 30 % estaba bien calculado en cada paso. → El problema es que las dos bases eran distintas."
        ),
        "fb_r03_e4_none": (
            "0,70 · 1,30 = 0,91, no 1. → Falta un 9 % del encargo."
        ),
        "fb_r03_e5_trap": (
            "Se sube y se baja el mismo PORCENTAJE, no la misma cantidad. → 20 láminas "
            "arriba y 24 abajo."
        ),
        "fb_r03_e5_order": (
            "Al revés sale idéntico: el producto de dos factores no depende del orden. "
            "→ 0,96 en los dos casos."
        ),
        "fb_r03_e5_more": (
            "Va en la dirección contraria: encadenar así siempre deja por debajo. → 0,96 < 1."
        ),
    },
    "closing": (
        "El oro se encarga por la cantidad que de verdad hace falta. Falta la última sala "
        "del papiro: hasta ahora, cuando una cantidad subía la otra subía con ella. En la "
        "sala de las lámparas pasa lo contrario, y la regla de tres de la tina deja de "
        "servir tal cual."
    ),
    "validation_status": "F5_R03_11bloques",
}
