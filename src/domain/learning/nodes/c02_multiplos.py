"""C02 · Múltiplos — los divisores se acaban, los múltiplos no.

Destino del nodo: RODAS · lo que se repite. Contexto propio: la campana del faro
(un toque cada cierto número de golpes de remo).
"""

NODE_ID = "PREALG-N4-C02-MULTIPLOS"
CONCEPT_SLUG = "multiplos"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "multiplos",
    "misconception": "los_multiplos_se_acaban",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "Rodas · Múltiplos",
    "destination": "Rodas · lo que se repite",
    "finish_label": "Zarpar hacia Delos",
    "title": "Los divisores se acaban; los múltiplos no",
    "intro": (
        "En Corinto miraste quién divide a quién. Aquí das vuelta la mirada: dado un "
        "número, ¿qué números lo contienen un número exacto de veces? La respuesta tiene "
        "una propiedad que la de los divisores no tiene, y esa diferencia es todo el nodo."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de subir al faro. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "La campana suena cada 4 golpes de remo. ¿En qué golpe suena la quinta vez?",
                "answer": "20",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuántos múltiplos tiene el número 6?",
                "options": [
                    {"id": "infinite", "text": "Infinitos"},
                    {"id": "four", "text": "Cuatro: 1, 2, 3 y 6"},
                    {"id": "depends", "text": "Depende de hasta dónde cuentes"},
                ],
                "expected": "infinite",
                "misconception_by_option": {
                    "four": "confunde_multiplo_con_divisor",
                    "depends": "los_multiplos_se_acaban",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es el múltiplo MÁS PEQUEÑO de 7 que es positivo?",
                "options": [
                    {"id": "seven", "text": "7"},
                    {"id": "one", "text": "1"},
                    {"id": "fourteen", "text": "14"},
                ],
                "expected": "seven",
                "misconception_by_option": {
                    "one": "confunde_multiplo_con_divisor",
                    "fourteen": "excluye_el_numero_de_sus_multiplos",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el faro de Rodas",
        "title": "La campana que nunca terminaba de sonar",
        "body": (
            "El faro de Rodas tiene una campana de niebla. El vigía la hace sonar cada 4 "
            "golpes de remo del bote guía, para que las naves sepan a qué ritmo entrar. "
            "Cada toque marca un número: 4, 8, 12, 16…\n\n"
            "Un aprendiz recibió el encargo de anotar «todos los toques posibles» en una "
            "tablilla. Llenó las dos caras, pidió otra tablilla, llenó esa también y volvió "
            "diciendo que necesitaba más. El vigía le preguntó cuántas iba a necesitar y el "
            "aprendiz no supo qué contestar."
        ),
        "question": "¿Cuántos números marca esa campana en total?",
        "image": "/leccion/04-prealg-n4-puerto/c02-multiplos-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Un número grande, pero se acaban"},
                {"id": "b", "text": "No se acaban nunca"},
                {"id": "c", "text": "Cuatro, uno por cada golpe"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder explicarle al aprendiz "
                "por qué la tablilla nunca le va a alcanzar."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo 6, dos listas muy distintas",
        "body": (
            "Abajo, las dos preguntas que se le pueden hacer a un número. Fíjate en dónde "
            "termina cada lista."
        ),
        "cases": [
            {
                "label": "Caso que se acaba",
                "context": "Los DIVISORES de 6: quién cabe en 6 un número exacto de veces",
                "fraction": r"D(6)",
                "division": r"D(6)=\{1,2,3,6\}",
                "note": "Cuatro y se acabó. Ningún número mayor que 6 puede dividirlo.",
            },
            {
                "label": "Caso que no se acaba",
                "context": "Los MÚLTIPLOS de 6: dónde cabe el 6 un número exacto de veces",
                "fraction": r"M(6)",
                "division": r"M(6)=\{0,6,12,18,24,\ldots\}",
                "note": "Nunca se acaban: siempre puedes sumar 6 más y seguir.",
            },
        ],
        "resolution": (
            "La diferencia no es de tamaño, es estructural. Un divisor de 6 no puede pasar "
            "de 6, así que la lista está encerrada. Un múltiplo de 6 puede ser tan grande "
            "como quieras: dame el más grande que se te ocurra y le sumo 6. La lista de "
            "arriba tiene techo; la de abajo no."
        ),
    },
    "definition_title": "Los múltiplos",
    "definition_katex": r"M(b)=\{b\times k\ :\ k\in\mathbb{Z}\}",
    "definition": (
        "Un múltiplo de b es cualquier número que se obtiene multiplicando b por un entero. "
        "Todo número es múltiplo de sí mismo (k = 1) y el 0 es múltiplo de todos (k = 0). "
        "Un número tiene finitos divisores pero infinitos múltiplos."
    ),
    "definition_symbols": [
        {
            "symbol": r"M(b)",
            "reads": "los múltiplos de b",
            "means": "los números marcados por la campana de b",
        },
        {
            "symbol": r"D(b)",
            "reads": "los divisores de b",
            "means": "la otra lista, la que sí se acaba",
        },
        {
            "symbol": r"k",
            "reads": "cuántas veces",
            "means": "puede ser cualquier entero, y por eso la lista no tiene techo",
        },
        {
            "symbol": r"b\in M(b)",
            "reads": "b es múltiplo de sí mismo",
            "means": "con k = 1; el primer toque de la campana",
        },
        {
            "symbol": r"0\in M(b)",
            "reads": "el cero es múltiplo de todos",
            "means": "con k = 0; b × 0 = 0 siempre",
        },
        {
            "symbol": r"b\mid a\iff a\in M(b)",
            "reads": "las dos caras de lo mismo",
            "means": "Corinto y Rodas dicen lo mismo desde lados opuestos",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La lista que no termina",
            "title": "Cuántas tablillas necesita el aprendiz",
            "statement": (
                "El aprendiz quiere anotar todos los múltiplos positivos de 4. ¿Dónde "
                "termina la lista?"
            ),
            "latex": r"M(4)=\{4,8,12,16,\ldots\}",
            "image_slot": False,
            "steps": [
                "Escribo los primeros: 4 × 1 = 4, 4 × 2 = 8, 4 × 3 = 12, 4 × 4 = 16.",
                "Supongo que llegué al último y lo llamo N. Entonces N = 4 × k para algún k.",
                "Pero N + 4 = 4 × (k + 1) también es múltiplo de 4, y es mayor que N.",
                "Así que N no era el último. El razonamiento vale para cualquier N que elija.",
                "No hay último: la lista es infinita, y ninguna cantidad de tablillas alcanza.",
            ],
            "solution": r"$M(4)$ es infinito: no existe el múltiplo mayor",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se construye un múltiplo mayor que el supuesto último. ¿Por qué eso demuestra que no hay último?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Las dos listas del mismo número",
            "title": "Divisores contra múltiplos de 12",
            "statement": (
                "Escribe los divisores de 12 y los primeros múltiplos de 12. ¿Qué números "
                "aparecen en las dos listas?"
            ),
            "latex": r"D(12)\cap M(12)=\{12\}",
            "image_slot": False,
            "steps": [
                "Divisores: busco parejas que multiplicadas den 12 → 1×12, 2×6, 3×4.",
                "Los ordeno: D(12) = {1, 2, 3, 4, 6, 12}. Seis en total, y se acabó.",
                "Múltiplos: 12, 24, 36, 48… sin final.",
                "El único número en las dos listas es el 12: es divisor de sí mismo y múltiplo de sí mismo.",
                "Los divisores van del 1 al propio número; los múltiplos van del propio número hacia arriba.",
            ],
            "solution": r"$D(12)=\{1,2,3,4,6,12\}$ (seis); $M(12)$ infinito; comparten el 12",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que confundió las dos listas",
            "statement": (
                "El aprendiz entrega la tablilla: «Múltiplos de 10: son 1, 2, 5 y 10. Ya "
                "están todos, por eso me sobró sitio»."
            ),
            "latex": r"M(10)=\{1,2,5,10\}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"M(10)=\{\underline{1,2,5},10\}",
            "error_note": "Esos son los DIVISORES de 10. Anotó la lista de al lado.",
            "correct_version": {
                "wrong_latex": r"M(10)=\{1,2,5,10\}",
                "right_latex": r"M(10)=\{10,20,30,40,\ldots\}",
                "rows": [
                    {
                        "wrong": "Los múltiplos de 10 son los que caben en 10",
                        "right": "Son aquellos en los que cabe el 10",
                    },
                    {"wrong": "La lista tiene cuatro elementos", "right": "La lista es infinita"},
                ],
            },
            "explain_prompt": "Escribe los cuatro primeros múltiplos positivos de 10 y di por qué la lista no termina.",
            "steps": [
                "Comprueba con la definición: ¿existe un entero k con 10 × k = 2?",
                "Tendría que ser k = 0,2, que no es entero. El 2 no es múltiplo de 10.",
                "Los múltiplos se construyen multiplicando: 10×1 = 10, 10×2 = 20, 10×3 = 30…",
            ],
            "solution": (
                "Truco para no volver a cambiarlas: los divisores son más PEQUEÑOS o iguales "
                "que el número, los múltiplos más GRANDES o iguales. Si tu lista va bajando, "
                "estás en la lista equivocada."
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
                "statement": "La campana suena cada 6 golpes. ¿En qué golpe suena la séptima vez?",
                "given_steps": [
                    r"6\times 7",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"6\times 7=", "answer": "42"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "¿Cuántos divisores tiene 18? Búscalos por parejas.",
                "given_steps": [
                    r"1\times 18,\quad 2\times 9,\quad 3\times 6",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{cantidad de divisores}=", "answer": "6"},
                    {"id": "P2-b2", "label": r"\text{el mayor de ellos}=", "answer": "18"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: ¿cuál es el múltiplo de 9 más pequeño que sea "
                    "mayor que 100?"
                ),
                "given_steps": [],
                "blanks": [
                    {
                        "id": "P3-b1",
                        "label": r"9\times k>100\ \Rightarrow\ 9\times k=",
                        "answer": "108",
                    },
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para contar los divisores",
        "intro": r"¿Cuántos divisores tiene $36$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Probar uno por uno",
                "steps": [
                    r"1,2,3,4,6,9,12,18,36",
                    r"\text{probando del 1 al 36}",
                    r"=9\text{ divisores}",
                ],
                "note": "Seguro, pero hay que probar 36 candidatos.",
            },
            {
                "label": "Método 2 · Buscar por parejas",
                "steps": [
                    r"1\times 36,\ 2\times 18,\ 3\times 12,\ 4\times 9,\ 6\times 6",
                    r"\text{parar en }\sqrt{36}=6",
                    r"=9\text{ divisores}",
                ],
                "note": "Cada pareja da dos divisores; el 6 se cuenta una sola vez.",
            },
        ],
        "question": "¿Por qué el método 2 se puede detener en 6 y no hace falta seguir hasta 36?",
        "insight": (
            "Porque los divisores vienen en parejas que multiplicadas dan 36, y en cada "
            "pareja uno es menor o igual que √36 = 6 y el otro mayor o igual. Al pasar de 6 "
            "solo volverías a encontrar los compañeros que ya tienes. Por eso los divisores "
            "se acaban: están encerrados entre 1 y el número."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "La campana suena cada 8 golpes. ¿En qué golpe suena la sexta vez?",
            "expr": r"8\times 6",
            "answer": "48",
            "hints": {
                "n1": "Cada toque es 8 multiplicado por el número de toque.",
                "n2": "8 × 5 = 40.",
                "n3": "Falta un toque más.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuántos divisores tiene 20?",
            "expr": r"D(20)",
            "answer": "6",
            "hints": {
                "n1": "Búscalos por parejas que multiplicadas den 20.",
                "n2": "1×20, 2×10, 4×5.",
                "n3": "Tres parejas, ninguna repetida.",
            },
        },
        {
            "id": "E3",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODOS los que son múltiplos de 7.",
            "valid_options": ["n7", "n14", "n21", "n1", "n35", "n50"],
            "options": [
                {"id": "n1", "text": "1"},
                {"id": "n7", "text": "7"},
                {"id": "n14", "text": "14"},
                {"id": "n21", "text": "21"},
                {"id": "n35", "text": "35"},
                {"id": "n50", "text": "50"},
            ],
            "expected": ["n7", "n14", "n21", "n35"],
            "trap_options": ["n1"],
            "hints": {
                "n1": "Un múltiplo de 7 se obtiene multiplicando 7 por un entero.",
                "n2": "El 1 es DIVISOR de 7, no múltiplo: no hay entero k con 7 × k = 1.",
                "n3": "7×5 = 35, y 7×7 = 49, así que 50 no es.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un aprendiz anota «Los múltiplos de 15 son 1, 3, 5 y 15». ¿Dónde está el error?",
            "options": [
                {
                    "id": "divisors",
                    "text": "Esos son los divisores: los múltiplos son 15, 30, 45… y son infinitos",
                },
                {"id": "missing", "text": "Le faltó incluir el 45"},
                {"id": "extra", "text": "El 15 sobra: un número no es múltiplo de sí mismo"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "divisors",
            "feedback_by_option": {
                "divisors": "correct",
                "missing": "fb_c02_e4_missing",
                "extra": "fb_c02_e4_extra",
                "none": "fb_c02_e4_none",
            },
            "misconception_by_option": {
                "missing": "confunde_multiplo_con_divisor",
                "extra": "excluye_el_numero_de_sus_multiplos",
                "none": "confunde_multiplo_con_divisor",
            },
            "hints": {
                "n1": "¿Existe un entero k con 15 × k = 3?",
                "n2": "Tendría que ser 0,2: no es entero.",
                "n3": "Los múltiplos se obtienen multiplicando, así que van hacia arriba.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Todo número tiene una cantidad finita de múltiplos.»",
            "options": [
                {"id": "false_infinite", "text": "Falsa: son infinitos, salvo los del 0"},
                {"id": "true", "text": "Verdadera: igual que los divisores, se acaban"},
                {"id": "false_all", "text": "Falsa: absolutamente todos tienen infinitos"},
                {"id": "true_big", "text": "Verdadera si el número es grande"},
            ],
            "expected": "false_infinite",
            "feedback_by_option": {
                "false_infinite": "correct",
                "true": "fb_c02_e5_trap",
                "false_all": "fb_c02_e5_zero",
                "true_big": "fb_c02_e5_big",
            },
            "misconception_by_option": {
                "true": "los_multiplos_se_acaban",
                "false_all": "olvida_el_caso_del_cero",
                "true_big": "los_multiplos_se_acaban",
            },
            "hints": {
                "n1": "Coge el múltiplo más grande que se te ocurra y súmale el número otra vez.",
                "n2": "Siempre puedes: la lista no tiene techo.",
                "n3": "¿Y si el número fuera 0? 0 × k = 0 siempre: su único múltiplo es el 0.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("¿Cuál es el múltiplo de 12 más pequeño que supera los 100?"),
            "expr": r"12\times k>100",
            "answer": "108",
            "hints": {
                "n1": "Divide 100 entre 12 para saber por dónde andas.",
                "n2": "12 × 8 = 96, todavía no pasa de 100.",
                "n3": "El siguiente es 12 × 9.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": r"Si $b\mid a$, ¿qué se puede decir con seguridad?",
            "options": [
                {"id": "a_multiple", "text": "a es múltiplo de b"},
                {"id": "b_multiple", "text": "b es múltiplo de a"},
                {"id": "both", "text": "Cada uno es múltiplo del otro"},
                {"id": "neither", "text": "Nada: son cosas distintas"},
            ],
            "expected": "a_multiple",
            "feedback_by_option": {
                "a_multiple": "correct",
                "b_multiple": "fb_c02_e7_inverted",
                "both": "fb_c02_e7_both",
                "neither": "fb_c02_e7_neither",
            },
            "misconception_by_option": {
                "b_multiple": "invierte_la_direccion_de_la_divisibilidad",
                "both": "confunde_multiplo_con_divisor",
                "neither": "no_ve_la_equivalencia",
            },
            "hints": {
                "n1": "b | a quiere decir que existe k entero con a = b × k.",
                "n2": "Esa igualdad es exactamente la definición de múltiplo.",
                "n3": "a se obtiene multiplicando b, así que a es el múltiplo.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿La lista se acaba o no?",
        "title": "Conjuntos que este nodo pone lado a lado",
        "intro": "La pregunta de la columna es siempre la misma: ¿esta lista tiene un último elemento?",
        "rows": [
            {
                "symbol": r"M(1)",
                "name": "Múltiplos de 1",
                "closed": "no",
                "latex": r"\{1,2,3,4,\ldots\}",
                "note": "Todos los números son múltiplos de 1. Infinitos.",
            },
            {
                "symbol": r"M(7)",
                "name": "Múltiplos de 7",
                "closed": "no",
                "latex": r"\{7,14,21,\ldots\}",
                "note": "Infinitos: a cualquiera le sumas 7 y sigues.",
            },
            {
                "symbol": r"M(100)",
                "name": "Múltiplos de 100",
                "closed": "no",
                "latex": r"\{100,200,300,\ldots\}",
                "note": "Que empiecen grandes no los hace menos infinitos.",
            },
            {
                "symbol": r"M(0)",
                "name": "Múltiplos de 0",
                "closed": "yes",
                "latex": r"\{0\}",
                "note": "La única lista de múltiplos que SÍ se acaba: 0 × k = 0 siempre. Un solo elemento.",
            },
            {
                "symbol": r"D(12)",
                "name": "Divisores de 12",
                "closed": "yes",
                "latex": r"\{1,2,3,4,6,12\}",
                "note": "Seis. Encerrados entre 1 y 12: ninguno puede pasarse.",
            },
            {
                "symbol": r"D(97)",
                "name": "Divisores de 97",
                "closed": "yes",
                "latex": r"\{1,97\}",
                "note": "Solo dos. Los números con exactamente dos divisores tienen nombre, y es el próximo destino.",
            },
        ],
        "outro": (
            "Los múltiplos suben sin techo; los divisores están encerrados entre 1 y el "
            "número. Y esa última fila deja la pregunta servida: ¿qué tienen de especial "
            "los números con solo dos divisores? Eso se ve en Delos."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"M(4)", r"D(12)", r"M(10)"],
        "options": [
            {
                "id": "same_relation",
                "text": "Los tres describen la misma relación mirada desde un lado o desde el otro",
                "correct": True,
            },
            {"id": "infinite", "text": "Los tres son conjuntos infinitos", "correct": False},
            {"id": "exact", "text": "En los tres el reparto es exacto: residuo 0", "correct": True},
            {
                "id": "small",
                "text": "En los tres todos los elementos son menores que el número",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "La campana del faro suena cada 15 golpes de remo. Una nave entra en el golpe "
            "200. ¿En qué golpe sonó la campana por última vez antes de que entrara?"
        ),
        "polya": {
            "comprender": "Busco el mayor múltiplo de 15 que no pase de 200.",
            "planear": "Divido 200 entre 15, me quedo con la parte entera y vuelvo a multiplicar.",
            "ejecutar": "200 ÷ 15 = 13 y sobra 5 → 15 × 13 = 195.",
            "comprobar": "195 ≤ 200 y el siguiente toque, 15 × 14 = 210, ya se pasa. Correcto.",
        },
        "prompt": "¿En qué golpe sonó por última vez?",
        "answer": "195",
        "hints": {
            "n1": "Busca el mayor múltiplo de 15 que no supere 200.",
            "n2": "200 ÷ 15 da 13 con residuo.",
            "n3": "15 × 13 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya distingues la lista que sube de la que está encerrada.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué los "
            "múltiplos no tienen último y los divisores sí."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "La campana suena cada 5 golpes. ¿En qué golpe suena la sexta vez?",
                "answer": "30",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuántos múltiplos tiene el número 9?",
                "options": [
                    {"id": "infinite", "text": "Infinitos"},
                    {"id": "three", "text": "Tres: 1, 3 y 9"},
                    {"id": "depends", "text": "Depende de hasta dónde cuentes"},
                ],
                "expected": "infinite",
                "misconception_by_option": {
                    "three": "confunde_multiplo_con_divisor",
                    "depends": "los_multiplos_se_acaban",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Cuántos DIVISORES tiene el número 9?",
                "options": [
                    {"id": "three", "text": "Tres: 1, 3 y 9"},
                    {"id": "infinite", "text": "Infinitos"},
                    {"id": "two", "text": "Dos: 1 y 9"},
                ],
                "expected": "three",
                "misconception_by_option": {
                    "infinite": "sobregeneraliza_multiplos",
                    "two": "olvida_el_divisor_del_medio",
                },
                # Espejo de PD2: comprueba que aprendió la DISTINCIÓN y no la
                # heurística "la respuesta siempre es infinitos".
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
        "default": "Comprueba si tu lista sube o baja: los múltiplos suben, los divisores no pasan del número.",
        "fb_c02_e4_missing": (
            "No es que falte uno: la lista entera es la equivocada. → Comprueba si existe "
            "un entero k con 15 × k = 3."
        ),
        "fb_c02_e4_extra": (
            "El 15 sí es múltiplo de sí mismo, con k = 1. → El problema son los otros tres."
        ),
        "fb_c02_e4_none": (
            "Comprueba el 3: ¿hay algún entero k con 15 × k = 3? → Responde eso antes de seguir."
        ),
        "fb_c02_e5_trap": (
            "Los divisores se acaban, los múltiplos no. → Coge el múltiplo más grande que "
            "se te ocurra y súmale el número."
        ),
        "fb_c02_e5_zero": (
            "Casi: vale para todos menos uno. → Escribe los múltiplos de 0 y cuéntalos."
        ),
        "fb_c02_e5_big": (
            "El tamaño no cambia nada: los múltiplos de 100 también son infinitos. "
            "→ Escribe los cuatro primeros y di si podrías seguir."
        ),
        "fb_c02_e7_inverted": (
            "b | a quiere decir a = b × k. → Di cuál de los dos se obtiene multiplicando al otro."
        ),
        "fb_c02_e7_both": ("Solo pasa cuando a y b son iguales. → Prueba con b = 3 y a = 12."),
        "fb_c02_e7_neither": (
            "Sí hay relación, y es exactamente la misma vista desde el otro lado. → Escribe "
            "la definición de b | a y compárala con la de múltiplo."
        ),
    },
    "closing": (
        "Divisores y múltiplos son la misma relación mirada desde lados opuestos, pero una "
        "lista está encerrada y la otra no. Los números con solo dos divisores tienen nombre "
        "propio, y te esperan en Delos."
    ),
    "validation_status": "F4_C02_11bloques",
}
