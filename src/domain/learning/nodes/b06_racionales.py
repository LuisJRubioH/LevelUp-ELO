"""B06 · Racionales — la fracción es una división.

Nodo piloto de la arquitectura de 11 bloques (prototipo aprobado).
Spec: Implementacion/specs/PREALG-N1-B06-RACIONALES-FRACCION-DIVISION.md
"""

NODE_ID = "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION"
CONCEPT_SLUG = "racionales"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "racionales",
    "misconception": "decimal_truncado_es_el_numero",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado (sin fórmula, sin definición) -----------------
    "kicker": "Tercer peldaño · Racionales",
    "scene": {
        "image": "/leccion/00-comunes/step-racionales.png",
        "step": "rationals",
        "aria": "Los racionales son cocientes de enteros con denominador distinto de cero",
    },
    "finish_label": "Continuar a irracionales",
    "title": "La fracción es una división",
    "intro": (
        "Ya sabes contar y ya sabes deber. Falta repartir. Aquí vas a escribir un "
        "reparto como fracción, convertirlo en decimal dividiendo, y decidir cuándo "
        "un decimal dice exactamente lo mismo que la fracción y cuándo solo se le parece."
    ),
    # --- Bloque 2 · Mini-diagnóstico (siembra ELO, no puntúa) ----------------
    "diagnostic": {
        "intro": "Antes de empezar, tres rápidas. No hay nota; me sirven para saber por dónde entrarle.",
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál de estos dos números es menor?",
                "options": [
                    {"id": "neg3", "text": r"-3", "latex": r"-3"},
                    {"id": "neg_half", "text": r"-1/2", "latex": r"-\dfrac{1}{2}"},
                    {"id": "equal", "text": "Son iguales"},
                ],
                "expected": "neg3",
                "misconception_by_option": {
                    "neg_half": "magnitud_sin_signo",
                    "equal": "no_compara_entero_con_fraccion",
                },
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"$18\div4$ no da un número entero. ¿Cuánto sobra?",
                "answer": "2",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Tres botellas iguales se reparten entre cuatro personas. ¿Cuánta botella recibe cada una?",
                "options": [
                    {
                        "id": "three_fourths",
                        "text": "tres cuartos de botella",
                        "latex": r"\dfrac{3}{4}",
                    },
                    {
                        "id": "four_thirds",
                        "text": "cuatro tercios de botella",
                        "latex": r"\dfrac{4}{3}",
                    },
                    {"id": "not_enough", "text": "No alcanza: sobra 1"},
                    {"id": "one_and_left", "text": "Cada una 1 y sobra"},
                ],
                "expected": "three_fourths",
                "misconception_by_option": {
                    "four_thirds": "invierte_cociente",
                    "not_enough": "reparto_solo_entero",
                    "one_and_left": "reparto_solo_entero",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · El puente que se mueve",
        "title": "La cuerda de Pitágoras",
        "body": (
            "Pitágoras tenía una tabla con una sola cuerda tensada y un puente que podía "
            "deslizar. Con la cuerda entera sonaba una nota. Con el puente justo en la mitad "
            "sonaba la misma nota, más aguda. Y con el puente en 2 de cada 3 partes salía la "
            "nota que a él le parecía la más hermosa de todas.\n\n"
            "Dos de cada tres partes. Pero el taller solo tenía reglas marcadas en décimas, "
            "y ahí empieza el problema."
        ),
        "question": (
            "¿Qué número debía marcar Pitágoras en su regla para dejar el puente exactamente "
            "donde suena esa nota?"
        ),
        "image": "/leccion/01-prealg-n1-agora/b06-racionales-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado. No viaja al backend —
        # el sistema responde "veámoslo" a cualquier opción.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge la que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "a", "latex": r"0{,}66"},
                {"id": "b", "latex": r"0{,}666"},
                {
                    "id": "c",
                    "text": "Ninguno de los dos: solo 2/3 lo dice exacto",
                    "latex": r"\dfrac{2}{3}",
                },
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber cuál de las tres "
                "escribe el número exacto y por qué las otras dos se quedan cortas."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos repartos, dos finales distintos",
        "body": (
            "Mira los dos casos de abajo. Los dos son un reparto que no da entero, pero "
            "terminan de forma distinta: uno cierra y el otro no cierra nunca."
        ),
        "cases": [
            {
                "label": "Caso que funciona",
                "context": "15 medidas de miel para 6 tarros de la despensa",
                "fraction": r"\dfrac{15}{6}",
                "division": r"15\div6=2{,}5",
                "note": "La división termina. El punto cae justo sobre una marca de la recta.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "5 parcelas del huerto entre 9 discípulos",
                "fraction": r"\dfrac{5}{9}",
                "division": r"5\div9=0{,}5555\ldots",
                "note": "La división no termina. El punto cae entre marcas, siempre.",
            },
        ],
        "resolution": (
            "¿Y entonces 5/9 no es un número? Sí lo es, y es exacto. Lo que no termina es el "
            "intento de escribirlo en decimales. La fracción ya lo dice completo; el decimal "
            "es un retrato que a veces no cabe en la hoja."
        ),
    },
    "definition_title": "Los números racionales",
    "definition_katex": r"\mathbb{Q}=\left\{\dfrac{a}{b}\ :\ a,b\in\mathbb{Z},\ b\neq 0\right\}",
    "definition": (
        "La frase del nodo: a/b ES a÷b. No «se parece a», no «se puede convertir en». Es."
    ),
    "definition_symbols": [
        {
            "symbol": r"\mathbb{Q}",
            "reads": "los racionales",
            "means": "de quotient, cociente: el conjunto de los cocientes",
        },
        {"symbol": r"a", "reads": "numerador", "means": "cuánto se reparte (el dividendo)"},
        {"symbol": r"b", "reads": "denominador", "means": "entre cuántos se reparte (el divisor)"},
        {
            "symbol": r"\dfrac{\ \ }{\ \ }",
            "reads": "dividido entre",
            "means": "la barra no es un adorno: es el signo de dividir",
        },
        {
            "symbol": r"a,b\in\mathbb{Z}",
            "reads": "a y b son enteros",
            "means": "arriba y abajo pueden ser negativos (viene de B05)",
        },
        {
            "symbol": r"b\neq 0",
            "reads": "b distinto de cero",
            "means": "repartir entre cero baldes no es un reparto",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La división termina",
            "title": "La miel de la despensa",
            "statement": (
                "En la despensa de la escuela quedan 15 medidas de miel y hay que "
                "pasarlas a 6 tarros iguales. ¿Cuánta miel lleva cada tarro?"
            ),
            "latex": r"\dfrac{15}{6}=15\div6",
            "image_slot": False,
            "steps": [
                "El reparto es 15 entre 6 → 15/6. Arriba la miel, abajo entre cuántos tarros.",
                "La barra es dividir, así que calculo 15÷6. Es la definición, aplicada.",
                "6 × 2 = 12, sobran 3. El entero cabe 2 veces.",
                "Las 3 medidas que sobran también se reparten entre los 6 tarros → 0,5.",
                "15/6 = 2,5. Cada tarro lleva 2,5 medidas: la división terminó y el decimal es exacto.",
            ],
            "solution": r"$\dfrac{15}{6}=2{,}5$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 3,
                "prompt": "En el paso 4 el 3 que sobra se vuelve 0,5. ¿Por qué 0,5 y no 3?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · La división no termina",
            "title": "El huerto de la escuela",
            "statement": (
                "El huerto de la escuela tiene 5 parcelas iguales y hay 9 discípulos "
                "encargados de cuidarlo. ¿Cuánto huerto cuida cada uno?"
            ),
            "latex": r"\dfrac{5}{9}=5\div9",
            "image_slot": False,
            "steps": [
                "5 parcelas entre 9 discípulos → 5/9.",
                "5÷9: pongo 5,000… y divido, porque la barra es dividir.",
                "0,5 y resto 5. 0,55 y resto 5. 0,555 y resto 5: el resto se repite, nunca va a terminar.",
                "Escribo 0,5 con barra encima: la barra marca lo que se repite para siempre.",
                "5/9 = 0,5̄. Las dos escrituras son exactas; la fracción es la más corta.",
            ],
            "solution": r"$\dfrac{5}{9}=0{,}\overline{5}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El decimal que se cortó",
            "statement": (
                "Un discípulo midió el lado del patio y anotó esto en su tablilla. Está mal: "
                "«La medida da 25/7 varas. Dividí y me salió 3,57142. Entonces "
                "25/7 = 3,57142»."
            ),
            "latex": r"\dfrac{25}{7}=3{,}57142",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"3{,}5714\underline{2}",
            "error_note": "Aquí se cortó. La división no había terminado: siguió 3,571428 571428 571428…",
            "correct_version": {
                "wrong_latex": r"\dfrac{25}{7}=3{,}57142",
                "right_latex": r"\dfrac{25}{7}=3{,}\overline{571428}",
                "rows": [
                    {
                        "wrong": "El decimal se cortó donde se acabó la paciencia",
                        "right": "El bloque 571428 se repite para siempre",
                    },
                    {
                        "wrong": "3,57142 es menor que 25/7",
                        "right": "La única escritura corta y exacta es 25/7",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 3,57142 no es 25/7? Escribe la igualdad corregida.",
            "steps": [
                "Divide 25÷7 y no te detengas en la quinta cifra.",
                "Observa que los restos empiezan a repetirse: el bloque 571428 vuelve a salir.",
                "Un decimal cortado siempre queda por debajo del valor real.",
            ],
            "solution": (
                "Un decimal cortado es una FOTO del número, no el número. Cuando necesites el "
                "valor exacto, la fracción. Cuando necesites leerlo rápido, el decimal "
                "redondeado — y lo dices: «aproximadamente»."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: el procedimiento ya está empezado y "
            "solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Traen 32 medidas de agua de la fuente y hay que llenar 5 tinajas iguales.",
                "given_steps": [
                    r"\dfrac{32}{5}=32\div5",
                    r"5\times6=30,\ \text{sobran }2",
                    r"2\div5=0{,}4",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\dfrac{32}{5}=", "answer": "6,4"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Ahora son 69 espuertas de arena para nivelar 5 tramos iguales del patio.",
                "given_steps": [
                    r"\dfrac{69}{5}=69\div5",
                ],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"5\times\square=65\ \Rightarrow\ \square=",
                        "answer": "13",
                    },
                    {"id": "P2-b2", "label": r"4\div5=", "answer": "0,8"},
                    {"id": "P2-b3", "label": r"\dfrac{69}{5}=", "answer": "13,8"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: la sombra del gnomon mide 12 dedos y hay que "
                    "partirla en 7 tramos iguales. Da el resultado y decide qué escritura "
                    "cabría en una marca de 6 caracteres."
                ),
                "given_steps": [],
                "blanks": [
                    {
                        "id": "P3-b1",
                        "label": r"\text{Parte entera de }\dfrac{12}{7}=",
                        "answer": "1",
                    },
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos caminos para el mismo decimal",
        "intro": r"¿Cuánto vale $\dfrac{7}{8}$ en decimal? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Dividir",
                "steps": [
                    r"7\div8",
                    r"8\times0{,}8=6{,}4\ \text{resto }0{,}6",
                    r"\dfrac{7}{8}=0{,}875",
                ],
                "note": "Siempre funciona.",
            },
            {
                "label": r"Método 2 · Amplificar a denominador $10^n$",
                "steps": [
                    r"\dfrac{7}{8}=\dfrac{7\times125}{8\times125}",
                    r"=\dfrac{875}{1000}",
                    r"\dfrac{7}{8}=0{,}875",
                ],
                "note": "Solo si el denominador se puede llevar a 10, 100, 1000…",
            },
        ],
        "question": "¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si intentas el método 2 con 5/9?",
        "insight": (
            "El segundo método falla con 5/9, y ese fracaso es el contenido: solo los "
            "denominadores que se factorizan en 2 y 5 llegan a una potencia de 10; los demás "
            "son periódicos. Lo vas a volver a ver en factorización prima (N4-C04)."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Se reparten 3 medidas de vino en 4 copas iguales. ¿Cuánto lleva cada copa?",
            "expr": r"\dfrac{3}{4}",
            "answer": "0,75",
            "hints": {
                "n1": "¿Qué cantidad se está repartiendo?",
                "n2": "Arriba lo que se reparte, abajo entre cuántos: la barra es el signo de dividir.",
                "n3": "3÷4: 4×0,7=2,8, faltan 0,2…",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Hay 32 codos de lino para repartir entre 5 telares. ¿Cuántos codos por telar?",
            "expr": r"\dfrac{32}{5}",
            "answer": "6,4",
            "hints": {
                "n1": "¿Cabe 5 en 32 un número exacto de veces?",
                "n2": "Sobran 2; reparte esos 2 entre 5.",
                "n3": "32 = 5×6 + 2, y 2÷5 = 0,4.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "Ordena de mayor a menor: 8/6, 2/3, 4/6, 1/2. ¿Cuál es el orden correcto?",
            "options": [
                {
                    "id": "ok",
                    "text": "8/6 · 2/3 = 4/6 · 1/2",
                    "latex": r"\dfrac{8}{6}>\dfrac{2}{3}=\dfrac{4}{6}>\dfrac{1}{2}",
                },
                {
                    "id": "half_first",
                    "text": "1/2 primero",
                    "latex": r"\dfrac{1}{2}>\dfrac{2}{3}>\dfrac{4}{6}>\dfrac{8}{6}",
                },
                {
                    "id": "split_equiv",
                    "text": "2/3 y 4/6 en puestos distintos",
                    "latex": r"\dfrac{8}{6}>\dfrac{4}{6}>\dfrac{2}{3}>\dfrac{1}{2}",
                },
                {
                    "id": "by_numerator",
                    "text": "Por el numerador",
                    "latex": r"\dfrac{8}{6}>\dfrac{4}{6}>\dfrac{2}{3}>\dfrac{1}{2}",
                },
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "half_first": "fb_b06_e3_half",
                "split_equiv": "fb_b06_e3_equiv",
                "by_numerator": "fb_b06_e3_equiv",
            },
            "misconception_by_option": {
                "half_first": "mayor_denominador_mayor_numero",
                "split_equiv": "no_reconoce_equivalentes",
                "by_numerator": "no_reconoce_equivalentes",
            },
            "hints": {
                "n1": "Si no puedes compararlas de un vistazo, ¿en qué otra forma sabes escribirlas?",
                "n2": "Convierte todas a decimal.",
                "n3": "8÷6 = 1,3̄; sigue con las demás.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Teano revisa la tablilla de otro discípulo y lee «69/5 = 12,25». ¿Dónde está el error?",
            "options": [
                {"id": "division", "text": "Dividió mal: 5×12=60 y le sobran 9, no 1"},
                {"id": "truncated", "text": "Cortó el decimal antes de tiempo"},
                {"id": "inverted", "text": "Puso la fracción al revés"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "division",
            "feedback_by_option": {
                "division": "correct",
                "truncated": "fb_b06_e4_truncated",
                "inverted": "fb_b06_e4_inverted",
                "none": "fb_b06_e4_none",
            },
            "misconception_by_option": {
                "truncated": "confunde_error_con_truncamiento",
                "inverted": "invierte_cociente",
                "none": "habito_valida_sin_verificar",
            },
            "hints": {
                "n1": "¿Cuántas veces cabe 5 en 69?",
                "n2": "13 veces y sobran 4.",
                "n3": "4÷5 = 0,8, entonces el resultado es 13,8.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? $\dfrac{10}{3}=3{,}333$",
            "options": [
                {"id": "false_cut", "text": "Falsa: 3,333 está cortado, el exacto es 3,3̄"},
                {"id": "true_same", "text": "Verdadera, es lo mismo"},
                {"id": "false_nodecimal", "text": "Falsa: 10/3 no tiene decimal"},
                {"id": "false_03", "text": "Falsa: da 0,3"},
            ],
            "expected": "false_cut",
            "feedback_by_option": {
                "false_cut": "correct",
                "true_same": "fb_b06_e5_trap",
                "false_nodecimal": "fb_b06_e5_nodecimal",
                "false_03": "fb_b06_e5_inverted",
            },
            "misconception_by_option": {
                "true_same": "decimal_truncado_es_el_numero",
                "false_nodecimal": "periodico_no_es_numero",
                "false_03": "invierte_cociente",
            },
            "hints": {
                "n1": "Multiplica el decimal por 3. ¿Vuelve a darte 10?",
                "n2": "Un decimal que se corta siempre queda por debajo del valor real.",
                "n3": "10÷3 = 3,3333… sin final; se escribe 3,3̄.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El cantero debe tallar una losa de 4/9 de codo, pero su regla solo llega a "
                "dos decimales y marca 0,44. ¿La losa le va a quedar bien?"
            ),
            "options": [
                {"id": "short", "text": "No: 4/9 = 0,4̄; queda un poco corta"},
                {"id": "exact", "text": "Sí, 0,44 es exactamente 4/9"},
                {"id": "long", "text": "No: queda un poco larga"},
                {"id": "unknown", "text": "No se puede saber sin más datos"},
            ],
            "expected": "short",
            "feedback_by_option": {
                "short": "correct",
                "exact": "fb_b06_e6_exact",
                "long": "fb_b06_e6_long",
                "unknown": "fb_b06_e6_unknown",
            },
            "misconception_by_option": {
                "exact": "decimal_truncado_es_el_numero",
                "long": "direccion_del_truncamiento",
                "unknown": "habito_evita_decidir",
            },
            "hints": {
                "n1": "¿0,44 y 0,4444… son el mismo número?",
                "n2": "Divide 4÷9 y mira si se detiene.",
                "n3": "0,44 < 0,4̄: falta material.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estas fracciones da un decimal que TERMINA?",
            "options": [
                {"id": "three_eighths", "text": "3/8", "latex": r"\dfrac{3}{8}"},
                {"id": "two_sevenths", "text": "2/7", "latex": r"\dfrac{2}{7}"},
                {"id": "five_sixths", "text": "5/6", "latex": r"\dfrac{5}{6}"},
                {"id": "one_ninth", "text": "1/9", "latex": r"\dfrac{1}{9}"},
            ],
            "expected": "three_eighths",
            "feedback_by_option": {
                "three_eighths": "correct",
                "two_sevenths": "fb_b06_e7_denominator",
                "five_sixths": "fb_b06_e7_denominator",
                "one_ninth": "fb_b06_e7_denominator",
            },
            "misconception_by_option": {
                "two_sevenths": "denominador_no_2_ni_5",
                "five_sixths": "denominador_no_2_ni_5",
                "one_ninth": "denominador_no_2_ni_5",
            },
            "hints": {
                "n1": "Prueba a llevar cada denominador a 10, 100 o 1000.",
                "n2": "8 × 125 = 1000. ¿Y el 7?",
                "n3": "Solo terminan las que se factorizan con 2 y 5 (lo verás en N4-C04).",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "La escalera de la necesidad",
        "title": "¿Toda división de dos números del conjunto vive en el conjunto?",
        "intro": "Cada peldaño nació de una operación que no cabía en el anterior.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"3\div4\notin\mathbb{N}",
                "note": "Se sale: no hay natural que valga.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"3\div4\notin\mathbb{Z}",
                "note": "Sigue sin caber; los negativos no ayudaron.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"3\div4=\dfrac{3}{4}\in\mathbb{Q}",
                "note": "El conjunto se hizo para esto (mientras b ≠ 0).",
            },
        ],
        "outro": (
            "Igual que ℤ nació de una resta que no cabía (B05). El siguiente peldaño (B07) va a "
            "nacer de algo que NINGUNA fracción puede escribir."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué estructura comparten los tres problemas de este nodo?",
        "thumbnails": [r"\dfrac{15}{6}", r"\dfrac{5}{9}", r"\dfrac{25}{7}"],
        "options": [
            {"id": "division", "text": "Los tres son una división de enteros", "correct": True},
            {"id": "periodic", "text": "Los tres tienen decimal periódico", "correct": False},
            {
                "id": "improper",
                "text": "Los tres tienen numerador mayor que el denominador",
                "correct": False,
            },
            {"id": "sharing", "text": "Los tres son un reparto que no da entero", "correct": True},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "La regla graduada del taller solo admite 4 decimales y la losa debe medir "
            "7/6 de codo. ¿Qué número marcas en la regla?"
        ),
        "polya": {
            "comprender": "Me dan 7/6 de codo y un límite de 4 decimales. Me piden el número a marcar y el error.",
            "planear": "Convierto 7/6 a decimal dividiendo. Luego corto en 4 decimales. Luego resto para ver qué perdí.",
            "ejecutar": "7÷6 = 1,1666… = 1,16̄ → marco 1,1667 (redondeado) → el error es menor que 0,0001 de codo.",
            "comprobar": "1,1667 × 6 = 7,0002 ≈ 7. Y lo digo en voz alta: aproximadamente, no igual.",
        },
        "prompt": "¿Qué número marcas en la regla?",
        "answer": "1,1667",
        "hints": {
            "n1": "Primero convierte la fracción a decimal.",
            "n2": "7÷6 no termina: 1,1666…",
            "n3": "Redondea a 4 decimales: la quinta cifra es 6, así que la cuarta sube.",
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
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia "
            "entre el decimal exacto y el decimal cortado."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es menor?",
                "options": [
                    {"id": "neg2", "text": "-2", "latex": r"-2"},
                    {"id": "neg_quarter", "text": "-1/4", "latex": r"-\dfrac{1}{4}"},
                    {"id": "equal", "text": "Son iguales"},
                ],
                "expected": "neg2",
                "misconception_by_option": {"neg_quarter": "magnitud_sin_signo"},
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"$23\div4$ no da entero. ¿Cómo escribes el resultado exacto?",
                "options": [
                    {"id": "ok", "text": "23/4", "latex": r"\dfrac{23}{4}"},
                    {"id": "inverted", "text": "4/23", "latex": r"\dfrac{4}{23}"},
                    {"id": "remainder", "text": "5 y sobra 3"},
                    {"id": "cannot", "text": "No se puede escribir exacto"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "inverted": "invierte_cociente",
                    "remainder": "reparto_solo_entero",
                    "cannot": "reparto_solo_entero",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? $\dfrac{10}{3}=3{,}\overline{3}$",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "periodico_no_es_numero"},
                # Variante VERDADERA de la trampa E5, a propósito: comprueba que
                # aprendió el criterio y no la heurística "decimal largo ⇒ falso".
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
        "fb_b06_e3_half": (
            "1/2 y 1/5: divide las dos y compáralas en la recta. Un denominador más grande "
            "reparte en más partes, así que cada parte es MÁS PEQUEÑA. → Escribe los dos decimales."
        ),
        "fb_b06_e3_equiv": (
            "2/3 y 4/6 caen en el mismo punto de la recta: son el mismo número escrito de dos "
            "formas. → Divide las dos y compara los decimales."
        ),
        "fb_b06_e4_truncated": (
            "Buen reflejo, pero aquí no se cortó nada: 69/5 sí termina. El fallo está en la "
            "división misma. → Haz 69÷5 y entrega el cociente correcto."
        ),
        "fb_b06_e4_inverted": (
            "La fracción está bien puesta: 69 cucharadas entre 5 moldes. El error está en el "
            "cociente. → Haz 69÷5."
        ),
        "fb_b06_e4_none": (
            "Compruébalo al revés: 12,25 × 5. ¿Da 69? → Responde ese producto antes de seguir."
        ),
        "fb_b06_e5_trap": (
            "3,333 × 3 = 9,999, no 10. Se parecen, pero no son el mismo número: el decimal "
            "está cortado. → Escribe el decimal exacto usando la barra de periodo."
        ),
        "fb_b06_e5_nodecimal": (
            "Sí es un número, y exacto. Lo que no termina es su ESCRITURA decimal. → Ubica 10/3 "
            "entre 3 y 4 en la recta."
        ),
        "fb_b06_e5_inverted": (
            "0,3 sería 3÷10. Aquí la división es 10÷3. → Vuelve a dividir en el orden correcto."
        ),
        "fb_b06_e6_exact": (
            "0,44 × 9 = 3,96, no 4. El decimal está cortado y la pieza sale corta. → Divide 4÷9 "
            "y mira dónde se repite."
        ),
        "fb_b06_e6_long": (
            "Vas bien en que no es exacto, pero fíjate hacia dónde: cortar cifras siempre deja "
            "el número POR DEBAJO. → Compara 0,44 con 0,4444… y di cuál es mayor."
        ),
        "fb_b06_e6_unknown": (
            "Sí se puede decidir con lo que hay. → Divide 4÷9 y compara con 0,44."
        ),
        "fb_b06_e7_denominator": (
            "Divide y mira dónde se repite el resto. ¿Qué tienen en común los denominadores "
            "cuyo decimal sí termina? → Nombra el factor del denominador de la opción correcta."
        ),
    },
    "closing": (
        "Un decimal cortado es una foto del número. La fracción es el número. En el siguiente "
        "nodo vas a conocer algo que ninguna fracción puede escribir."
    ),
    "validation_status": "F1_B06_11bloques_pilot",
}
