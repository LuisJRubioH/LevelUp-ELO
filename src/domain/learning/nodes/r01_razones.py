"""R01 · La cuadrícula del canon — escalar es multiplicar, no sumar.

Primera sala del taller del canon. Guía: Iuty, que conserva las proporciones
al pasar un motivo de un tamaño a otro. Vocabulario propio:
cuadrícula, boceto, relieve, molde, escala, proporción, maestro, aprendiz.
Nada de tinas ni brazadas (R02), pan de oro (R03) ni lámparas (R04).

Nota histórica: la cuadrícula del taller es AMBIENTACIÓN. No se atribuye
ninguna razón concreta (1:9 ni otra) al canon egipcio real — la ficha del nivel
lo marca como afirmación pendiente de validación experta.
"""

NODE_ID = "ALG-N1-R01-RAZONES"
CONCEPT_SLUG = "razones_y_proporciones"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "razones_y_proporciones",
    "misconception": "escalado_aditivo",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La cuadrícula del canon · Razones y proporciones",
    "house": "La cuadrícula del canon",
    "guide": "Iuty",
    "finish_label": "Bajar al tinte de lino",
    "title": "Sumar lo mismo a los dos lados no conserva la forma",
    "intro": (
        "Última sección del papiro. Un motivo hay que repetirlo grande en el muro y "
        "pequeño en el molde, y tiene que seguir siendo el mismo motivo. Lo que se "
        "conserva al cambiar de tamaño no es la diferencia: es el cociente."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de coger el pigmento. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Por qué número hay que multiplicar $3$ para obtener $12$?",
                "answer": "4",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Son equivalentes $\dfrac{2}{3}$ y $\dfrac{4}{6}$?",
                "options": [
                    {"id": "yes", "text": "Sí: las dos partes se multiplicaron por 2"},
                    {"id": "no", "text": "No: los números son distintos"},
                    {"id": "yes_add", "text": "Sí, porque a las dos se les sumó lo mismo"},
                ],
                "expected": "yes",
                "misconception_by_option": {
                    "no": "no_reconoce_fracciones_equivalentes",
                    "yes_add": "escalado_aditivo",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Describen $2:3$ y $4:6$ la misma relación?",
                "options": [
                    {"id": "same", "text": "Sí: por cada 2 de lo primero hay 3 de lo segundo, en las dos"},
                    {"id": "diff", "text": "No: en la segunda hay más cantidad"},
                    {"id": "unknown", "text": "No se puede saber sin más datos"},
                ],
                "expected": "same",
                "misconception_by_option": {
                    "diff": "confunde_cantidad_con_relacion",
                    "unknown": "confunde_cantidad_con_relacion",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/r01-razones-katia.png",
        "eyebrow": "KatIA · En el taller de Iuty",
        "title": "El relieve que salió deforme",
        "body": (
            "Iuty tiene delante dos versiones del mismo motivo: el boceto pequeño y el "
            "relieve grande que un aprendiz acaba de terminar sobre el muro. El grande no "
            "está mal hecho — está mal proporcionado. Algo creció más que lo demás.\n\n"
            "«El aprendiz me dijo que lo había agrandado todo por igual», cuenta Iuty. "
            "«Y es verdad que le sumó lo mismo a cada medida. Ese fue el problema.»"
        ),
        "question": "¿Qué tiene que mantenerse igual para que la forma no cambie?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "La diferencia entre las medidas"},
                {"id": "b", "text": "El cociente entre las medidas"},
                {"id": "c", "text": "El tamaño total del motivo"},
            ],
            "response": (
                "Probemos esa idea. Guarda tu respuesta: al final vas a poder decir por qué "
                "el aprendiz deformó el relieve creyendo que lo hacía bien."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos maneras de agrandar el mismo motivo",
        "body": (
            "Las dos parten de un motivo de 2 por 6 y lo hacen más grande. Fíjate en cuál "
            "sigue teniendo la misma forma."
        ),
        "cases": [
            {
                "label": "Multiplicar por el mismo factor",
                "context": "Las dos medidas por 2",
                "fraction": r"2:6\ \to\ 4:12",
                "division": r"\dfrac{2}{6}=\dfrac{1}{3},\qquad \dfrac{4}{12}=\dfrac{1}{3}",
                "note": "El cociente no se mueve. El motivo grande es el pequeño mirado de cerca.",
            },
            {
                "label": "Sumar la misma cantidad",
                "context": "A las dos medidas, +2",
                "fraction": r"2:6\ \to\ 4:8",
                "division": r"\dfrac{2}{6}=\dfrac{1}{3},\qquad \dfrac{4}{8}=\dfrac{1}{2}",
                "note": "El cociente cambió de 1/3 a 1/2. El motivo se ensanchó: ya es otro.",
            },
        ],
        "resolution": (
            "Sumar 2 a un 2 lo duplica; sumar 2 a un 6 apenas lo mueve. Por eso sumar lo "
            "mismo afecta más a la cantidad pequeña y desequilibra la relación. Multiplicar, "
            "en cambio, respeta el peso de cada una: eso es lo que conserva la forma."
        ),
    },
    "definition_title": "Razón y proporción",
    "definition_katex": r"\dfrac{a}{b}=\dfrac{c}{d}\iff a\cdot d=b\cdot c\quad (b,d\ne 0)",
    "definition": (
        "Una RAZÓN compara dos cantidades mediante una división: a : b es el cociente a/b. "
        "Dos razones forman una PROPORCIÓN cuando valen lo mismo. Se comprueba de dos "
        "maneras: buscando el factor de escala que lleva una a la otra, o viendo que los "
        "productos cruzados coinciden."
    ),
    "definition_symbols": [
        {"symbol": r"a:b", "reads": "a es a b", "means": "la razón entre dos cantidades, es decir su cociente"},
        {"symbol": r"\dfrac{a}{b}=\dfrac{c}{d}", "reads": "proporción", "means": "las dos razones valen lo mismo"},
        {"symbol": r"k", "reads": "factor de escala", "means": "el número que multiplica a AMBAS cantidades"},
        {"symbol": r"a\cdot d=b\cdot c", "reads": "productos cruzados", "means": "sirve aunque el factor no sea un número redondo"},
        {"symbol": r"b,d\ne 0", "reads": "no nulos", "means": "una razón es una división: el segundo término nunca es cero"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Mezcla de pigmentos",
            "title": "Encontrar el factor de escala",
            "statement": (
                "La mezcla del taller lleva 2 medidas de pigmento azul por cada 3 de base "
                "clara. Hace falta más cantidad y se preparan 6 medidas de base clara. "
                "¿Cuánto azul?"
            ),
            "latex": r"\dfrac{2}{3}=\dfrac{?}{6}",
            "image_slot": False,
            "steps": [
                "La razón que hay que conservar es 2 : 3.",
                "Miro qué le pasó a la base clara: de 3 a 6, o sea por 2. Ese es el factor de escala.",
                "Aplico el MISMO factor al azul: 2 · 2 = 4.",
                "La mezcla grande es 4 : 6.",
                "Compruebo que la razón se mantiene: 4/6 se simplifica a 2/3 ✓.",
            ],
            "solution": r"4 medidas de azul: $\dfrac{2}{3}=\dfrac{4}{6}$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué hay que multiplicar las dos partes por el mismo número y no solo una?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El molde ampliado",
            "title": "Cuando el factor no salta a la vista",
            "statement": (
                "Un molde mide 3 por 5 dedos. El maestro dice que el relieve del muro, de "
                "9 por 15 palmos, conserva la proporción. ¿Tiene razón?"
            ),
            "latex": r"\dfrac{3}{5}\ \text{vs}\ \dfrac{9}{15}",
            "image_slot": False,
            "steps": [
                "Podría buscar el factor: de 3 a 9 es por 3, y de 5 a 15 también por 3. Coincide.",
                "Pero cuando el factor no es redondo conviene el otro camino: los productos cruzados.",
                "Multiplico en cruz: 3 · 15 = 45 y 5 · 9 = 45.",
                "Como los dos productos coinciden, las razones son iguales: sí es una proporción.",
                "El maestro tiene razón. El relieve es el molde a escala 3.",
            ],
            "solution": r"Sí: $3\cdot 15=5\cdot 9=45$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que le sumó 2 a todo",
            "statement": (
                "El aprendiz explica cómo agrandó el relieve: «el motivo era 3 : 5. Le añadí "
                "2 dedos a cada medida, que es lo justo, y quedó 5 : 7. Las dos crecieron "
                "lo mismo»."
            ),
            "latex": r"3:5\ \to\ 5:7",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\dfrac{3}{5}=0{,}6\qquad \dfrac{5}{7}\approx 0{,}714",
            "error_note": (
                "«Lo justo» no es sumar lo mismo. Los dos crecieron 2 dedos, pero el 3 creció "
                "mucho más EN PROPORCIÓN que el 5."
            ),
            "correct_version": {
                "wrong_latex": r"3:5\ \to\ 5:7",
                "right_latex": r"3:5\ \to\ 6:10\quad(\text{factor }2)",
                "rows": [
                    {"wrong": "Crecer lo mismo es sumar la misma cantidad",
                     "right": "Crecer lo mismo es multiplicar por el mismo factor"},
                    {"wrong": "3 : 5 y 5 : 7 son la misma forma",
                     "right": "3 · 7 = 21 y 5 · 5 = 25: los productos cruzados no coinciden"},
                ],
            },
            "explain_prompt": (
                "Explica por qué el error es aditivo y no de cálculo, y da una ampliación "
                "correcta de 3 : 5."
            ),
            "steps": [
                "Comparo los cocientes: 3/5 = 0,6 y 5/7 ≈ 0,714. No son iguales.",
                "Compruebo con productos cruzados: 3 · 7 = 21 frente a 5 · 5 = 25. Tampoco.",
                "Miro el crecimiento relativo: el 3 aumentó dos tercios de sí mismo; el 5, solo dos quintos. Por eso se ensanchó.",
            ],
            "solution": (
                "Sumar la misma cantidad favorece siempre a la medida más pequeña. Para "
                "conservar la forma hay que multiplicar las dos por el mismo factor: "
                "3 : 5 se amplía a 6 : 10, a 9 : 15, a 12 : 20…"
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La ampliación ya va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Completa la razón equivalente: $\dfrac{2}{5}=\dfrac{?}{20}$.",
                "given_steps": [
                    r"5\cdot 4=20\ \Rightarrow\ \text{factor }4",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"2\cdot 4=", "answer": "8"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Halla el factor de escala que lleva $7:4$ a $?:24$ y completa.",
                "given_steps": [
                    r"4\to 24",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{factor}=24\div 4=", "answer": "6"},
                    {"id": "P2-b2", "label": r"7\cdot 6=", "answer": "42"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: ¿forman proporción $\dfrac{6}{9}$ y $\dfrac{10}{15}$? "
                    r"Escribe el valor del producto cruzado $6\cdot 15$."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"6\cdot 15=", "answer": "90"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de decidir si hay proporción",
        "intro": r"¿Forman proporción $4:6$ y $10:15$? Las dos comprobaciones son correctas.",
        "methods": [
            {
                "label": "Método 1 · Simplificar las dos razones",
                "steps": [
                    r"\dfrac{4}{6}=\dfrac{2}{3}",
                    r"\dfrac{10}{15}=\dfrac{2}{3}",
                    r"\text{iguales}\Rightarrow\text{sí}",
                ],
                "note": "Rápido y deja ver la forma común. Necesita que la simplificación sea fácil.",
            },
            {
                "label": "Método 2 · Productos cruzados",
                "steps": [
                    r"4\cdot 15=60",
                    r"6\cdot 10=60",
                    r"\text{iguales}\Rightarrow\text{sí}",
                ],
                "note": "Siempre funciona, aunque el factor no sea entero ni evidente.",
            },
        ],
        "question": "¿Cuál es más rápido con estos números y cuál usarías con 7 : 11 y 21 : 33?",
        "insight": (
            "Con 4 : 6 el primero gana porque la simplificación salta a la vista. Con "
            "7 : 11 no hay nada que simplificar y el factor 3 hay que adivinarlo; el "
            "producto cruzado lo resuelve sin buscar nada: 7 · 33 = 231 = 11 · 21."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"Completa la razón equivalente: $\dfrac{3}{7}=\dfrac{?}{28}$.",
            "expr": r"\dfrac{3}{7}=\dfrac{?}{28}",
            "answer": "12",
            "hints": {
                "n1": "Mira qué le pasó al 7 para llegar a 28.",
                "n2": "28 ÷ 7 = 4, así que el factor es 4.",
                "n3": "Aplica el mismo factor arriba: 3 · 4 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "Un molde de 5 por 8 dedos se amplía hasta que el lado de 5 mide 20. "
                "¿Cuánto mide entonces el lado de 8?"
            ),
            "expr": r"5:8\ \to\ 20:?",
            "answer": "32",
            "hints": {
                "n1": "Primero el factor: de 5 a 20.",
                "n2": "20 ÷ 5 = 4.",
                "n3": "8 · 4 = …",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Forman proporción $\dfrac{4}{6}$ y $\dfrac{6}{9}$?",
            "options": [
                {"id": "yes", "text": r"Sí: $4\cdot 9=6\cdot 6=36$"},
                {"id": "no_diff", "text": "No: la diferencia es 2 en una y 3 en la otra"},
                {"id": "no_factor", "text": "No: no hay ningún número entero que lleve 4 a 6"},
                {"id": "cannot", "text": "No se puede decidir sin simplificar"},
            ],
            "expected": "yes",
            "feedback_by_option": {
                "yes": "correct",
                "no_diff": "fb_a04_e3_diff",
                "no_factor": "fb_a04_e3_factor",
                "cannot": "fb_a04_e3_cannot",
            },
            "misconception_by_option": {
                "no_diff": "razon_como_diferencia",
                "no_factor": "exige_factor_entero",
                "cannot": "exige_factor_entero",
            },
            "hints": {
                "n1": "Simplifica las dos: ¿a qué se reducen?",
                "n2": "4/6 = 2/3 y 6/9 = 2/3.",
                "n3": "También sirve el producto cruzado: 4 · 9 frente a 6 · 6.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un aprendiz amplía la mezcla 2 : 5 a 6 : 9 y dice que conserva la "
                "proporción. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "different_factors", "text": "Multiplicó el 2 por 3 pero al 5 solo le sumó 4: los factores no coinciden"},
                {"id": "order", "text": "Cambió el orden de las cantidades"},
                {"id": "too_big", "text": "El error es que amplió demasiado"},
                {"id": "none", "text": "No hay error: las dos cantidades crecieron"},
            ],
            "expected": "different_factors",
            "feedback_by_option": {
                "different_factors": "correct",
                "order": "fb_a04_e4_order",
                "too_big": "fb_a04_e4_size",
                "none": "fb_a04_e4_none",
            },
            "misconception_by_option": {
                "order": "habito_busca_el_error_donde_no_esta",
                "too_big": "confunde_cantidad_con_relacion",
                "none": "escalado_aditivo",
            },
            "hints": {
                "n1": "Calcula por separado qué factor lleva 2 a 6 y qué factor lleva 5 a 9.",
                "n2": "6 ÷ 2 = 3, pero 9 ÷ 5 = 1,8. No es el mismo.",
                "n3": "Con factor 3 el segundo tendría que ser 15, no 9.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                r"¿Es verdadera o falsa? «Si a $3:5$ le sumo $2$ a cada parte, la relación "
                r"se conserva.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: la relación se conserva multiplicando, no sumando"},
                {"id": "true", "text": "Verdadera: las dos partes crecieron lo mismo"},
                {"id": "true_small", "text": "Verdadera si la cantidad sumada es pequeña"},
                {"id": "false_order", "text": "Falsa: habría que sumar primero a la parte mayor"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_a04_e5_trap",
                "true_small": "fb_a04_e5_small",
                "false_order": "fb_a04_e5_order",
            },
            "misconception_by_option": {
                "true": "escalado_aditivo",
                "true_small": "escalado_aditivo",
                "false_order": "razon_como_diferencia",
            },
            "hints": {
                "n1": "Calcula los dos cocientes y compáralos.",
                "n2": "3/5 = 0,6 y 5/7 ≈ 0,714.",
                "n3": "Si el cociente cambia, la forma cambia.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": r"Selecciona TODAS las razones equivalentes a $2:3$.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$8:12$", "latex": r"8:12"},
                {"id": "b", "text": r"$4:5$", "latex": r"4:5"},
                {"id": "c", "text": r"$10:15$", "latex": r"10:15"},
                {"id": "d", "text": r"$5:6$", "latex": r"5:6"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Simplifica cada una y compárala con 2 : 3.",
                "n2": "8 : 12 se divide entre 4 y 10 : 15 entre 5.",
                "n3": "4 : 5 y 5 : 6 salen de SUMAR a 2 : 3, no de multiplicar.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "En un plano del taller, 2 dedos representan 14 codos reales. Un muro "
                "aparece dibujado con 9 dedos de largo. ¿Cuántos codos mide de verdad?"
            ),
            "expr": r"\dfrac{2}{14}=\dfrac{9}{?}",
            "answer": "63",
            "hints": {
                "n1": "Cada dedo del plano son 14 ÷ 2 codos reales.",
                "n2": "Un dedo son 7 codos.",
                "n3": "9 · 7 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se conserva la forma?",
        "title": "Qué le puedes hacer a una razón sin cambiarla",
        "intro": (
            "Partimos siempre de 2 : 6 y le hacemos algo a las dos cantidades. Solo algunas "
            "operaciones dejan el cociente donde estaba."
        ),
        "rows": [
            {"symbol": r"\times k\ \text{a las dos}", "name": "Multiplicar por el mismo factor", "closed": "yes",
             "latex": r"2:6\ \to\ 4:12",
             "note": "1/3 antes y 1/3 después. Es la operación que define ampliar."},
            {"symbol": r"\div k\ \text{a las dos}", "name": "Dividir por el mismo factor", "closed": "yes",
             "latex": r"2:6\ \to\ 1:3",
             "note": "Reducir es lo mismo al revés: también conserva la forma."},
            {"symbol": r"+k\ \text{a las dos}", "name": "Sumar la misma cantidad", "closed": "no",
             "latex": r"2:6\ \to\ 4:8",
             "note": "De 1/3 a 1/2. Es la trampa de este nodo: afecta más a la cantidad pequeña."},
            {"symbol": r"\times k\ \text{a una sola}", "name": "Multiplicar solo una parte", "closed": "no",
             "latex": r"2:6\ \to\ 4:6",
             "note": "De 1/3 a 2/3. Justo el relieve deforme del aprendiz."},
            {"symbol": r"\text{invertir las dos}", "name": "Dar la vuelta a la razón", "closed": "partial",
             "latex": r"2:6\ \to\ 6:2",
             "note": "El cociente cambia (1/3 pasa a 3), pero la relación se conserva leída al revés. Vale si se invierten las DOS."},
            {"symbol": r"+k\ \text{proporcional}", "name": "Sumar en proporción", "closed": "yes",
             "latex": r"2:6\ \to\ 2+2:6+6",
             "note": "Aquí sumar sí vale, porque sumar a cada una su propio tamaño es multiplicar por 2 disfrazado."},
        ],
        "outro": (
            "La última fila es la que desarma la trampa del todo: no es que sumar esté "
            "prohibido, es que hay que sumarle a cada cantidad una parte proporcional a "
            "ella misma. Cuando la suma es la misma para las dos, la pequeña sale ganando "
            "y la forma se pierde."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"2:3\ \to\ 4:6", r"3\cdot 15=5\cdot 9", r"3:5\ \to\ 5:7?"],
        "options": [
            {"id": "quotient", "text": "En los tres lo que hay que vigilar es el cociente, no la diferencia", "correct": True},
            {"id": "both", "text": "En los tres la operación tiene que afectar a las DOS cantidades igual", "correct": True},
            {"id": "grow", "text": "En los tres las dos cantidades crecen", "correct": False},
            {"id": "integer", "text": "En los tres el factor de escala es un número entero", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última pieza del papiro: la cuadrícula del taller marca que por cada 4 "
            "cuadros de ancho el motivo lleva 7 de alto. El muro admite un motivo de 28 "
            "cuadros de ancho. ¿Cuántos cuadros de alto debe tener para conservar la forma?"
        ),
        "polya": {
            "comprender": "La razón ancho : alto es 4 : 7 y no puede cambiar. Me dan el ancho nuevo y busco el alto.",
            "planear": "Hallo el factor de escala mirando el ancho, y aplico ese mismo factor al alto.",
            "ejecutar": "28 ÷ 4 = 7, así que el factor es 7. El alto es 7 · 7 = 49.",
            "comprobar": "Productos cruzados: 4 · 49 = 196 y 7 · 28 = 196 ✓. Y de paso: si hubiera sumado 24 a las dos, el alto sería 31 y la razón 28/31, muy lejos de 4/7.",
        },
        "prompt": "¿Cuántos cuadros de alto?",
        "answer": "49",
        "hints": {
            "n1": "Busca el factor con la pareja que conoces entera: 4 → 28.",
            "n2": "El factor es 7.",
            "n3": "7 · 7 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otras medidas. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya escalas multiplicando y compruebas el cociente.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué sumar lo "
            "mismo a las dos partes deforma la figura."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Por qué número hay que multiplicar $4$ para obtener $20$?",
                "answer": "5",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es equivalente a $\dfrac{3}{4}$?",
                "options": [
                    {"id": "nine", "text": r"$\dfrac{9}{12}$", "latex": r"\dfrac{9}{12}"},
                    {"id": "five", "text": r"$\dfrac{5}{6}$", "latex": r"\dfrac{5}{6}"},
                    {"id": "seven", "text": r"$\dfrac{7}{8}$", "latex": r"\dfrac{7}{8}"},
                ],
                "expected": "nine",
                "misconception_by_option": {
                    "five": "escalado_aditivo",
                    "seven": "escalado_aditivo",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Forman proporción $5:8$ y $15:24$?",
                "options": [
                    {"id": "yes", "text": r"Sí: $5\cdot 24=8\cdot 15=120$"},
                    {"id": "no", "text": "No: la segunda es mucho más grande"},
                    {"id": "no_diff", "text": "No: las diferencias son 3 y 9"},
                ],
                "expected": "yes",
                "misconception_by_option": {
                    "no": "confunde_cantidad_con_relacion",
                    "no_diff": "razon_como_diferencia",
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
        "default": "Compara los cocientes, no las diferencias: la forma vive en la división.",
        "fb_a04_e3_diff": (
            "La diferencia no decide nada: 2 : 3 y 200 : 300 tienen diferencias muy "
            "distintas y son la misma razón. → Compara los cocientes."
        ),
        "fb_a04_e3_factor": (
            "El factor no tiene por qué ser entero, y aquí además lo es: mira 4 → 6 como "
            "1,5. → Prueba con el producto cruzado."
        ),
        "fb_a04_e3_cannot": (
            "Sí se puede decidir sin simplificar: multiplica en cruz. → 4 · 9 frente a 6 · 6."
        ),
        "fb_a04_e4_order": (
            "El orden está bien: ancho primero en las dos. → Calcula el factor de cada parte "
            "por separado."
        ),
        "fb_a04_e4_size": (
            "Ampliar mucho no es un error: 2 : 5 se puede llevar a 200 : 500. → El problema "
            "es que las dos partes no crecieron por el mismo número."
        ),
        "fb_a04_e4_none": (
            "Crecer no basta: tienen que crecer en la misma medida. → 6 ÷ 2 = 3 pero "
            "9 ÷ 5 = 1,8."
        ),
        "fb_a04_e5_trap": (
            "Crecieron lo mismo en cantidad, no en proporción: 2 sobre 3 es mucho y 2 sobre "
            "5 es poco. → Compara 3/5 con 5/7."
        ),
        "fb_a04_e5_small": (
            "El tamaño de lo sumado no arregla nada, solo hace el error menos visible. "
            "→ Prueba a sumar 1 y comprueba si 4/6 es igual a 3/5."
        ),
        "fb_a04_e5_order": (
            "El orden de las sumas no influye: sumar es conmutativo (N3-M01). → El problema "
            "es la operación, no el orden."
        ),
    },
    "closing": (
        "El relieve vuelve a tener la forma del boceto: la razón se conservó porque se "
        "multiplicó, no se sumó. Iuty baja al tinte de lino, donde esa misma razón sirve "
        "para lo que hace falta a diario — conocer tres cantidades y deducir la cuarta."
    ),
    "validation_status": "F5_R01_11bloques",
}
