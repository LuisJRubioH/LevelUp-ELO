"""O02 · El patio de aparejos — el menos de fuera entra hasta el último término.

Segunda sala de la obra de la pirámide. Guía: Bakenra. Vocabulario propio:
patio de aparejos, polea, soga, contrapeso, vale de salida, devolución,
inventario. Nada de rampas ni trineos (O01), ni cinceles (O03), ni agua (O04).

Error focal: aplicar el signo menos que precede a un paréntesis solo al primer
término de dentro. Es el error que hace que los inventarios nunca cuadren.
"""

NODE_ID = "ALG-N1-O02-SIGNOS"
CONCEPT_SLUG = "signos_y_parentesis"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "signos_y_parentesis",
    "misconception": "el_menos_solo_afecta_al_primero",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El patio de aparejos · Signos y paréntesis",
    "house": "El patio de aparejos",
    "guide": "Bakenra",
    "finish_label": "Subir al taller de cinceles",
    "title": "El menos de fuera entra hasta el último término",
    "intro": (
        "Ya sabes juntar lo que es del mismo tipo. Ahora aparecen devoluciones: partidas "
        "enteras que se restan de golpe. Un paréntesis con un menos delante no es un "
        "adorno — es una instrucción que afecta a todo lo que hay dentro."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar al patio. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 10 − (4 + 3)?",
                "answer": "3",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $-(x+5)$?",
                "options": [
                    {"id": "both", "text": r"$-x-5$", "latex": r"-x-5"},
                    {"id": "first", "text": r"$-x+5$", "latex": r"-x+5"},
                    {"id": "none", "text": r"$x-5$", "latex": r"x-5"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "first": "el_menos_solo_afecta_al_primero",
                    "none": "pierde_el_signo_del_termino",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 7 − (2 − 5)?",
                "answer": "10",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/o02-signos-katia.png",
        "eyebrow": "KatIA · En el patio de aparejos",
        "title": "El inventario que salía siempre de más",
        "body": (
            "El patio guarda las poleas, las sogas y los contrapesos. Cada mañana sale un "
            "vale con lo que se entrega y cada tarde vuelve otro con lo que se devuelve.\n\n"
            "Bakenra sostiene un vale de devolución: dos poleas y tres contrapesos.\n\n"
            "«El escriba anotó "
            "que salían ocho poleas y volvían dos, y hasta ahí bien. Pero los tres "
            "contrapesos que también volvían los sumó en vez de restarlos. Llevamos un mes "
            "creyendo que tenemos seis contrapesos más de los que hay, y hoy la cuadrilla "
            "de la cara norte se ha quedado sin aparejo.»"
        ),
        "question": "Cuando se resta una partida entera, ¿a qué parte le llega el menos?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Al primer término de la partida; el resto se copia igual"},
                {"id": "b", "text": "A todos los términos de la partida"},
                {"id": "c", "text": "A ninguno: el paréntesis se borra y ya está"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder quitar un paréntesis de tres "
                "términos sin dejarte ninguno por el camino."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo paréntesis, dos signos delante",
        "body": "Los dos registros se quitan el paréntesis. Solo en uno cambia algo dentro.",
        "cases": [
            {
                "label": "Con más delante",
                "context": "Salen 6 poleas y después salen otras 2 poleas y 3 sogas",
                "fraction": r"6p+(2p+3s)",
                "division": r"6p+2p+3s=8p+3s",
                "note": "Los signos de dentro se quedan tal cual. El paréntesis no hacía nada.",
            },
            {
                "label": "Con menos delante",
                "context": "Salen 6 poleas y después se devuelven 2 poleas y 3 sogas",
                "fraction": r"6p-(2p+3s)",
                "division": r"6p-2p-3s=4p-3s",
                "note": "Los DOS signos de dentro se dan la vuelta. Devolver sogas no puede aumentar las sogas.",
            },
        ],
        "resolution": (
            "El paréntesis agrupa una partida entera. Con un más delante, agrupar da igual. "
            "Con un menos delante, lo que se resta es la partida COMPLETA, así que cada uno "
            "de sus términos entra restando. Escrito con símbolos: el menos de fuera es un "
            "−1 que multiplica todo lo de dentro."
        ),
    },
    "definition_title": "Quitar un paréntesis",
    "definition_katex": r"-(a+b)=-a-b\qquad -(a-b)=-a+b",
    "definition": (
        "Un paréntesis precedido de + se borra sin tocar nada. Un paréntesis precedido de − "
        "se borra CAMBIANDO EL SIGNO de todos sus términos, sin excepción: los que sumaban "
        "pasan a restar y los que restaban pasan a sumar. Equivale a multiplicar por −1. "
        "Si delante hay un número, no basta con los signos: hay que repartir ese factor."
    ),
    "definition_symbols": [
        {
            "symbol": r"+(2p+3)",
            "reads": "más, abre, dos pe más tres",
            "means": "se borra el paréntesis y ya",
        },
        {
            "symbol": r"-(2p+3)=-2p-3",
            "reads": "menos, abre…",
            "means": "los dos términos cambian de signo",
        },
        {
            "symbol": r"-(2p-3)=-2p+3",
            "reads": "menos, abre…",
            "means": "el que restaba pasa a sumar",
        },
        {
            "symbol": r"-(-5)=+5",
            "reads": "menos, menos cinco",
            "means": "restar una devolución es sumar",
        },
        {
            "symbol": r"-1\cdot(a+b)",
            "reads": "menos uno por…",
            "means": "de dónde sale la regla: es la distributiva",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · El vale de devolución",
            "title": "Restar una partida entera",
            "statement": (
                "Por la mañana salen 9 sogas y 6 contrapesos. Por la tarde se devuelven 4 "
                "sogas y 6 contrapesos. ¿Qué queda fuera del patio?"
            ),
            "latex": r"(9s+6)-(4s+6)",
            "image_slot": False,
            "steps": [
                "Lo devuelto se resta entero: por eso va agrupado en un paréntesis.",
                "Quito el primer paréntesis, que no lleva menos delante: 9s + 6 − (4s + 6).",
                "Quito el segundo cambiando los DOS signos: 9s + 6 − 4s − 6.",
                "Junto semejantes: 9s − 4s = 5s, y 6 − 6 = 0.",
                "Queda 5s. Los contrapesos volvieron todos, así que no queda ninguno fuera ✓.",
            ],
            "solution": r"$5s$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué el 6 de dentro del segundo paréntesis pasa a restar, si estaba sumando?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · La devolución que trae menos",
            "title": "Cuando dentro del paréntesis ya hay una resta",
            "statement": (
                "El inventario del patio marca 12 aparejos. Se descuenta un vale que dice "
                "«3 poleas menos 5 que nunca salieron». ¿Cuántos aparejos hay?"
            ),
            "latex": r"12-(3p-5)",
            "image_slot": False,
            "steps": [
                "El menos de fuera afecta a los dos términos de dentro, sean del signo que sean.",
                "El 3p sumaba dentro: pasa a restar → −3p.",
                "El −5 restaba dentro: pasa a sumar → +5.",
                "Queda 12 − 3p + 5 = 17 − 3p.",
                "Compruebo con p = 2: el original da 12 − (6 − 5) = 11, y 17 − 6 = 11 ✓.",
            ],
            "solution": r"$12-(3p-5)=17-3p$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que se quedó a mitad del paréntesis",
            "statement": (
                "Vuelve el vale de la apertura: salen 8 poleas y 3 contrapesos, y se "
                "devuelven 2 poleas y 3 contrapesos. El escriba anota 8p − 2p + 3."
            ),
            "latex": r"(8p+3)-(2p+3)",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"(8p+3)-(2p+3)=6p+3",
            "error_note": (
                "Cambió el signo del primer término y copió el segundo tal cual. Los tres "
                "contrapesos que volvían quedaron contados como si hubieran salido."
            ),
            "correct_version": {
                "wrong_latex": r"8p+3-2p+3=6p+6",
                "right_latex": r"8p+3-2p-3=6p",
                "rows": [
                    {
                        "wrong": "El menos se aplica al 2p y el 3 se copia",
                        "right": "El menos se aplica a los dos: −2p y −3",
                    },
                    {
                        "wrong": "Quedan 6 contrapesos fuera",
                        "right": "3 − 3 = 0: no queda ninguno fuera",
                    },
                ],
            },
            "explain_prompt": (
                "Explica a qué términos llega el menos de fuera y comprueba el error "
                "sustituyendo p = 10."
            ),
            "steps": [
                "Sustituyo p = 10 en el original: (83) − (23) = 60.",
                "Sustituyo en el registro del escriba: 6 · 10 + 6 = 66. Sobran 6.",
                "Regla para no volver a caer: cuenta los términos de dentro y cámbiale el signo a todos, uno por uno.",
            ],
            "solution": (
                "(8p + 3) − (2p + 3) = 6p. El menos de fuera no se cansa a mitad del "
                "paréntesis: llega hasta el último término."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El vale va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Quita el paréntesis y reduce: $7s-(2s+4)$.",
                "given_steps": [r"7s-2s-4"],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{coeficiente de }s:\ 7-2=", "answer": "5"}
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Reduce $10-(3c-6)$ y evalúa con $c=2$.",
                "given_steps": [r"10-3c+6"],
                "blanks": [
                    {"id": "P2-b1", "label": r"10+6=", "answer": "16"},
                    {"id": "P2-b2", "label": r"16-3\cdot 2=", "answer": "10"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: salen 15 sogas y se devuelve un vale de "
                    r"$(4s-9)$. Reduce y evalúa con $s=3$."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"15s-(4s-9)\ \text{con}\ s=3:", "answer": "42"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de quitar el paréntesis",
        "intro": r"$9c-(4c+2-7d)$. Tres términos dentro: es donde se pierde la gente.",
        "methods": [
            {
                "label": "Método 1 · Cambiar los signos de un vistazo",
                "steps": [
                    r"9c-(4c+2-7d)",
                    r"9c-4c-2+7d",
                    r"5c-2+7d",
                ],
                "note": "Rápido cuando dentro hay dos términos; con tres ya se salta alguno.",
            },
            {
                "label": "Método 2 · Escribir el −1 y repartirlo",
                "steps": [
                    r"9c+(-1)(4c+2-7d)",
                    r"9c+(-4c)+(-2)+(+7d)",
                    r"5c-2+7d",
                ],
                "note": "Un renglón más, pero obliga a tocar cada término una vez.",
            },
        ],
        "question": "¿Cuál elegirías con un paréntesis de cuatro o cinco términos?",
        "insight": (
            "El segundo. No porque el primero esté mal —dan lo mismo—, sino porque el "
            "primero depende de que no se te escape ninguno, y con cuatro términos se "
            "escapa. Escribir el −1 convierte «acordarse» en «multiplicar», y multiplicar "
            "se hace término a término sin depender de la memoria. Esa idea de repartir un "
            "factor por dentro del paréntesis es la que vas a usar en el taller de cinceles."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Reduce $8p-(3p+2)$.",
            "options": [
                {"id": "ok", "text": r"$5p-2$", "latex": r"5p-2"},
                {"id": "half", "text": r"$5p+2$", "latex": r"5p+2"},
                {"id": "all", "text": r"$11p+2$", "latex": r"11p+2"},
                {"id": "glue", "text": r"$3p$", "latex": r"3p"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "half": "fb_o02_e1_half",
                "all": "fb_o02_e1_all",
                "glue": "fb_o02_e1_glue",
            },
            "misconception_by_option": {
                "half": "el_menos_solo_afecta_al_primero",
                "all": "ignora_el_signo_de_fuera",
                "glue": "combina_no_semejantes",
            },
            "hints": {
                "n1": "Dentro del paréntesis hay dos términos. Cuéntalos.",
                "n2": "A los dos hay que cambiarles el signo.",
                "n3": "Queda 8p − 3p − 2.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Reduce $14-(5c-3)$ y escribe el resultado. Usa el orden en que quede "
                "y no dejes espacios."
            ),
            "answer": "17-5c",
            "accepted": ["-5c+17"],
            "hints": {
                "n1": "El −3 de dentro pasa a sumar.",
                "n2": "Queda 14 − 5c + 3.",
                "n3": "Junta las constantes: 14 + 3 = 17.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"El patio tiene $20$ aparejos y se descuenta el vale $(6a-9)$. Con $a=2$, "
                "¿cuántos aparejos quedan?"
            ),
            "expr": r"20-(6a-9),\quad a=2",
            "answer": "17",
            "hints": {
                "n1": "Primero quita el paréntesis: 20 − 6a + 9.",
                "n2": "Eso es 29 − 6a.",
                "n3": "29 − 12 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (r"Un escriba escribe $10s-(2s-4)=8s-4$. ¿Dónde está el error?"),
            "options": [
                {"id": "sign", "text": r"El $-4$ de dentro pasa a sumar: queda $8s+4$"},
                {"id": "coef", "text": "Restó mal los coeficientes de s"},
                {"id": "like", "text": "Juntó términos que no eran semejantes"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "sign",
            "feedback_by_option": {
                "sign": "correct",
                "coef": "fb_o02_e4_coef",
                "like": "fb_o02_e4_like",
                "none": "fb_o02_e4_none",
            },
            "misconception_by_option": {
                "coef": "pierde_el_signo_del_termino",
                "like": "combina_no_semejantes",
                "none": "el_menos_solo_afecta_al_primero",
            },
            "hints": {
                "n1": "Los coeficientes de s están bien: 10 − 2 = 8.",
                "n2": "Mira qué le pasó al segundo término de dentro.",
                "n3": "Restar algo que ya restaba lo convierte en suma.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «El menos que va delante de un paréntesis solo cambia "
                "el signo del primer término de dentro.»"
            ),
            "options": [
                {"id": "false", "text": r"Falsa: $-(2p+3)$ es $-2p-3$, con los dos cambiados"},
                {"id": "true", "text": "Verdadera: por eso está pegado al primero"},
                {"id": "true_two", "text": "Verdadera si dentro hay más de dos términos"},
                {
                    "id": "false_none",
                    "text": "Falsa: el menos no cambia ningún signo, solo borra el paréntesis",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_o02_e5_trap",
                "true_two": "fb_o02_e5_two",
                "false_none": "fb_o02_e5_none",
            },
            "misconception_by_option": {
                "true": "el_menos_solo_afecta_al_primero",
                "true_two": "el_menos_solo_afecta_al_primero",
                "false_none": "ignora_el_signo_de_fuera",
            },
            "hints": {
                "n1": "Prueba con números: 10 − (4 + 3).",
                "n2": "El resultado es 3, no 10 − 4 + 3 = 9.",
                "n3": "El menos llegó también al 3.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (
                "Selecciona TODOS los paréntesis que se pueden borrar sin tocar ningún signo."
            ),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$5c+(2c+7)$", "latex": r"5c+(2c+7)"},
                {"id": "b", "text": r"$5c-(2c+7)$", "latex": r"5c-(2c+7)"},
                {"id": "c", "text": r"$(2c+7)+5c$", "latex": r"(2c+7)+5c"},
                {"id": "d", "text": r"$5c-(2c-7)$", "latex": r"5c-(2c-7)"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Mira qué signo hay JUSTO delante de cada paréntesis.",
                "n2": "Un paréntesis sin nada delante es como si tuviera un más.",
                "n3": "Los dos que llevan menos delante obligan a cambiar signos.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El patio anota 30 sogas. Por la mañana sale un vale de (7s + 4) y por la "
                "tarde vuelve uno de (2s − 4). Con s = 3, ¿cuántas sogas quedan anotadas?"
            ),
            "expr": r"30-(7s+4)+(2s-4),\quad s=3",
            "answer": "7",
            "hints": {
                "n1": "El primer paréntesis lleva menos delante; el segundo, más.",
                "n2": "Queda 30 − 7s − 4 + 2s − 4 = 22 − 5s.",
                "n3": "22 − 15 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se puede borrar el paréntesis tal cual?",
        "title": "Qué manda el signo que va delante",
        "intro": (
            "El paréntesis no dice nada por sí solo. Lo que decide es el símbolo que tiene "
            "pegado por fuera, a su izquierda."
        ),
        "rows": [
            {
                "symbol": r"(2p+3)",
                "name": "Sin nada delante",
                "closed": "yes",
                "latex": r"(2p+3)=2p+3",
                "note": "Un paréntesis suelto agrupa y no manda. Se borra sin más.",
            },
            {
                "symbol": r"+(2p+3)",
                "name": "Con más delante",
                "closed": "yes",
                "latex": r"+(2p+3)=+2p+3",
                "note": "Sumar una partida entera es sumar cada cosa: nada cambia de signo.",
            },
            {
                "symbol": r"-(2p+3)",
                "name": "Con menos delante",
                "closed": "no",
                "latex": r"-(2p+3)=-2p-3",
                "note": "Los dos términos se dan la vuelta. Es el caso focal.",
            },
            {
                "symbol": r"-(2p-3)",
                "name": "Menos fuera y menos dentro",
                "closed": "no",
                "latex": r"-(2p-3)=-2p+3",
                "note": "El que restaba pasa a sumar. Restar una devolución devuelve.",
            },
            {
                "symbol": r"-(-5)",
                "name": "Un solo término negativo",
                "closed": "no",
                "latex": r"-(-5)=+5",
                "note": "El mismo caso reducido al mínimo: sigue habiendo un cambio de signo.",
            },
            {
                "symbol": r"4(2p+3)",
                "name": "Con un número delante",
                "closed": "partial",
                "latex": r"4(2p+3)=8p+12",
                "note": "Los paréntesis sí se quitan, pero no gratis: hay que repartir el 4 a cada término.",
            },
        ],
        "outro": (
            "Las cinco primeras filas son la misma idea vista de cinco maneras: lo de fuera "
            "entra hasta el final. La sexta la lleva un paso más lejos — si en vez de un "
            "menos hay un número, tampoco basta con copiar: hay que multiplicar por dentro. "
            "Ese reparto es el trabajo del taller de cinceles."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres vales trabajados en este nodo?",
        "thumbnails": [r"(9s+6)-(4s+6)", r"12-(3p-5)", r"(8p+3)-(2p+3)"],
        "options": [
            {
                "id": "all_terms",
                "text": "En los tres el signo de fuera actúa sobre todos los términos de dentro",
                "correct": True,
            },
            {
                "id": "then_like",
                "text": "En los tres hay que quitar el paréntesis antes de poder juntar semejantes",
                "correct": True,
            },
            {
                "id": "first_only",
                "text": "En los tres basta con cambiar el signo del primer término",
                "correct": False,
            },
            {
                "id": "erase",
                "text": "En los tres el paréntesis se borra sin consecuencias",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Inventario de fin de mes. El patio tenía 40 contrapesos. Salió un vale de "
            "(9k + 6) y volvió una devolución de (9k − 6), con k el número de cuadrillas "
            "que trabajaron. Hoy trabajaron 4 cuadrillas. ¿Cuántos contrapesos quedan?"
        ),
        "polya": {
            "comprender": "Lo que sale se resta y lo que vuelve se suma; los dos vales van agrupados.",
            "planear": "Escribo 40 − (9k + 6) + (9k − 6) y quito los paréntesis mirando el signo de cada uno.",
            "ejecutar": "40 − 9k − 6 + 9k − 6 = 40 − 12 = 28. Los términos en k se cancelan.",
            "comprobar": "Con k = 4: salió 42 y volvió 30, luego 40 − 42 + 30 = 28 ✓. Y el resultado no depende de k, cosa que se ve sin sustituir.",
        },
        "prompt": "¿Cuántos contrapesos quedan?",
        "answer": "28",
        "hints": {
            "n1": "El primer paréntesis lleva menos delante; el segundo, más.",
            "n2": "Los términos en k se van: −9k + 9k = 0.",
            "n3": "40 − 6 − 6 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros vales. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: el menos de fuera ya te llega hasta el último término.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el paréntesis con "
            "menos delante, término por término."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 12 − (5 + 4)?",
                "answer": "3",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $-(y+7)$?",
                "options": [
                    {"id": "both", "text": r"$-y-7$", "latex": r"-y-7"},
                    {"id": "first", "text": r"$-y+7$", "latex": r"-y+7"},
                    {"id": "none", "text": r"$y-7$", "latex": r"y-7"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "first": "el_menos_solo_afecta_al_primero",
                    "none": "pierde_el_signo_del_termino",
                },
            },
            {
                "id": "PD3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 9 − (3 − 6)?",
                "answer": "12",
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
        "default": "Cuenta los términos de dentro del paréntesis y cámbiales el signo a todos.",
        "fb_o02_e1_half": (
            "Cambiaste el signo del 3p y copiaste el 2. → El menos de fuera llega también "
            "al segundo término."
        ),
        "fb_o02_e1_all": (
            "Ahí sumaste la partida en vez de restarla. → El signo de fuera es un menos."
        ),
        "fb_o02_e1_glue": (
            "El 2 no es semejante con los términos en p. → Se queda como término suelto."
        ),
        "fb_o02_e4_coef": "Los coeficientes están bien: 10 − 2 = 8. → El fallo está en el segundo término.",
        "fb_o02_e4_like": "No juntó nada indebido. → Mira el signo del 4 después de quitar el paréntesis.",
        "fb_o02_e4_none": (
            "El −4 de dentro tenía que pasar a sumar. → Prueba con s = 1: el original da 12 "
            "y su registro, 4."
        ),
        "fb_o02_e5_trap": (
            "Estar pegado al primero no le da preferencia. → 10 − (4 + 3) es 3, no 9."
        ),
        "fb_o02_e5_two": (
            "El número de términos no cambia la regla; solo hace más fácil olvidarse de "
            "alguno. → Con dos también cambian los dos."
        ),
        "fb_o02_e5_none": (
            "Te pasaste al otro extremo: sí cambia signos. → Lo que no hace es dejarlo todo igual."
        ),
    },
    "closing": (
        "Ya puedes restar una partida entera sin que el inventario mienta. Lo siguiente es "
        "el reparto de verdad: en el taller de cinceles no hay un menos delante del "
        "paréntesis, hay un factor, y multiplicar letras tiene su propia contabilidad."
    ),
    "validation_status": "F5_O02_11bloques",
}
