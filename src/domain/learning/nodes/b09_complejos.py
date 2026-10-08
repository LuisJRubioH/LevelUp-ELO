"""B09 · Complejos — cuando la recta se queda corta.

Arquitectura de 11 bloques (molde aprobado en B06).
Desvío opcional de la escalera: no hay peldaño `scene` porque ℂ no está en la
recta. Misconception focal: «un cuadrado siempre es positivo, luego i² = 1».
"""

NODE_ID = "PREALG-N1-B09-COMPLEJOS-PLANO"
CONCEPT_SLUG = "complejos"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "complejos",
    "misconception": "cuadrado_siempre_positivo",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    # Sin `scene`: ℂ no es un peldaño de la escalera, es salirse de la recta.
    "kicker": "Desvío opcional · Complejos",
    "finish_label": "Volver al mapa",
    "title": "Cuando la recta se queda corta",
    "intro": (
        "Este nodo es un desvío, no un peldaño: los complejos no están en la recta. "
        "Aquí vas a ver qué pasa cuando una operación perfectamente razonable no tiene "
        "respuesta en ℝ, y cómo la solución no fue subir un escalón sino salirse de la "
        "línea y usar todo el plano."
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
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto vale (−3) × (−3)?",
                "answer": "9",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Existe algún número REAL que multiplicado por sí mismo dé $-1$?",
                "options": [
                    {"id": "no", "text": "No: los cuadrados de reales nunca son negativos"},
                    {"id": "yes_neg", "text": "Sí: el −1, porque es negativo"},
                    {"id": "yes_frac", "text": "Sí, pero es una fracción muy pequeña"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes_neg": "cuadrado_conserva_signo",
                    "yes_frac": "todo_tiene_solucion_real",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Para ubicar un punto en un plano cuadriculado, ¿cuántos números necesitas?",
                "options": [
                    {"id": "two", "text": "Dos: cuánto a lo ancho y cuánto a lo largo"},
                    {"id": "one", "text": "Uno solo, como en la recta"},
                    {"id": "three", "text": "Tres"},
                ],
                "expected": "two",
                "misconception_by_option": {
                    "one": "plano_como_recta",
                    "three": "confunde_dimensiones",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · El desvío",
        "title": "La ciudad de Hipodamo",
        "body": (
            "Hipodamo de Mileto hizo algo que nadie había hecho: en vez de dejar que la "
            "ciudad creciera enredada, la trazó en cuadrícula. Para decir dónde queda una "
            "casa ya no bastaba con «la tercera de la calle»: hacían falta dos números, "
            "uno a lo ancho y otro a lo largo.\n\n"
            "KatIA se queda pensando en eso mientras revisa una cuenta que no le sale. "
            "Está buscando un número que, multiplicado por sí mismo, dé −1. En la recta "
            "no está: los positivos al cuadrado dan positivo, los negativos al cuadrado "
            "también, y el 0 da 0. La recta entera, revisada, y nada."
        ),
        "question": (
            "Si el número que buscas no está en ninguna parte de la recta, ¿la respuesta "
            "es que no existe, o que estás buscando en el lugar equivocado?"
        ),
        "image": "/leccion/01-prealg-n1-agora/b09-complejos-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "No existe: la pregunta está mal hecha"},
                {"id": "b", "text": "Existe, pero fuera de la recta"},
                {"id": "c", "text": "Existe en la recta, solo que no lo hemos encontrado"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber que la "
                "misma jugada ya la hiciste cuatro veces antes en esta escalera."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Una calle no alcanza para una ciudad",
        "body": (
            "Los dos casos de abajo son la misma pregunta hecha en dos lugares "
            "distintos. Fíjate en qué cambia cuando dejas de mirar solo la recta."
        ),
        "cases": [
            {
                "label": "Caso que ya sabías",
                "context": "Buscar en la recta un número cuyo cuadrado sea −1",
                "fraction": r"x^2=-1",
                "division": r"x\in\mathbb{R}\ \Rightarrow\ x^2\geq0",
                "note": (
                    "Positivo × positivo = positivo. Negativo × negativo = positivo. "
                    "0 × 0 = 0. En la recta no hay candidato, y no es por falta de buscar."
                ),
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Salirse de la recta y usar el plano de Hipodamo",
                "fraction": r"i^2=-1",
                "division": r"i=\sqrt{-1}",
                "note": (
                    "Se define un número nuevo, i, que vive a una unidad ARRIBA del 0, "
                    "fuera de la recta. Y su cuadrado sí da −1, por definición."
                ),
            },
        ],
        "resolution": (
            "Esta jugada ya la viste: cada vez que una operación no cabía, se amplió el "
            "conjunto. La resta no cabía en ℕ → ℤ. La división no cabía en ℤ → ℚ. La "
            "diagonal no cabía en ℚ → ℝ. Ahora la raíz de un negativo no cabe en ℝ → ℂ. "
            "La única diferencia es que esta vez no alcanzaba con estirar la recta: "
            "hubo que agregarle una dirección."
        ),
    },
    "definition_title": "Los números complejos",
    "definition_katex": r"\mathbb{C}=\{a+bi\ :\ a,b\in\mathbb{R}\}\quad\text{con}\quad i^2=-1",
    "definition": (
        "La frase del nodo: «imaginario» es un mal nombre histórico. i no es menos real "
        "que −3 o que √2 — los tres se inventaron para resolver algo que no cabía."
    ),
    "definition_symbols": [
        {
            "symbol": r"\mathbb{C}",
            "reads": "los complejos",
            "means": "todos los puntos del plano, no solo los de la recta",
        },
        {
            "symbol": r"i",
            "reads": "la unidad imaginaria",
            "means": "el número definido por i × i = −1; está una unidad arriba del 0",
        },
        {
            "symbol": r"a+bi",
            "reads": "a más b i",
            "means": "las dos coordenadas: a a lo ancho (real), b a lo alto (imaginaria)",
        },
        {
            "symbol": r"a",
            "reads": "parte real",
            "means": "cuánto te mueves sobre la recta de siempre",
        },
        {
            "symbol": r"b",
            "reads": "parte imaginaria",
            "means": "cuánto te separas de la recta; si b = 0, el número es real",
        },
        {
            "symbol": r"\mathbb{R}\subset\mathbb{C}",
            "reads": "ℝ está contenido en ℂ",
            "means": "todo real es complejo con b = 0: la recta es una calle del plano",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Una raíz que no cabía",
            "title": "La cuenta que no salía",
            "statement": r"¿Cuánto vale $\sqrt{-9}$, y por qué no está en la recta?",
            "latex": r"\sqrt{-9}",
            "image_slot": False,
            "steps": [
                "Busco un número que multiplicado por sí mismo dé −9. En la recta no hay: todo cuadrado real es ≥ 0.",
                "Separo el signo del tamaño: −9 = 9 × (−1).",
                "La raíz del 9 sí la sé: 3. Y para la raíz de −1 uso el número nuevo: i.",
                "Junto las dos partes: √(−9) = 3i.",
                "Compruebo: 3i × 3i = 9 × i² = 9 × (−1) = −9. ✓",
            ],
            "solution": r"$\sqrt{-9}=3i$, con parte real 0 y parte imaginaria 3.",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 4,
                "prompt": (
                    "En el paso 5 comprobé el resultado multiplicándolo por sí mismo. "
                    "¿Por qué esa comprobación es la única que sirve aquí?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Ubicar un complejo en el plano",
            "title": "La casa en la cuadrícula",
            "statement": (
                "En el plano de Hipodamo, ¿dónde queda el número 3 + 2i, y por qué no "
                "puede quedar sobre la recta real?"
            ),
            "latex": r"3+2i",
            "image_slot": False,
            "steps": [
                "Leo las dos coordenadas: parte real 3, parte imaginaria 2.",
                "Me muevo 3 a la derecha sobre la recta de siempre (el eje real).",
                "Desde ahí subo 2 en la dirección nueva (el eje imaginario).",
                "Ahí queda el punto. Está fuera de la recta porque su parte imaginaria no es 0.",
                "Contraste: 3 + 0i = 3 sí queda sobre la recta. Los reales son los complejos con b = 0.",
            ],
            "solution": r"$3+2i$ está 3 a la derecha y 2 arriba: fuera de la recta, dentro del plano.",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El cuadrado que se volvió positivo",
            "statement": (
                "Un discípulo hizo esta cuenta. Está mal: «i × i = √(−1) × √(−1) = "
                "√((−1)×(−1)) = √1 = 1. Entonces i² = 1, porque todo cuadrado es positivo»."
            ),
            "latex": r"i^2=1",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\sqrt{-1}\times\sqrt{-1}\ \underline{=}\ \sqrt{(-1)\times(-1)}",
            "error_note": (
                "Aquí se cayó. Usó la regla √a × √b = √(ab), que solo vale cuando a y b "
                "son ≥ 0. Con negativos deja de valer, y él la aplicó igual."
            ),
            "correct_version": {
                "wrong_latex": r"i^2=1",
                "right_latex": r"i^2=-1\ \ \text{(por definición)}",
                "rows": [
                    {
                        "wrong": "√a × √b = √(ab) siempre",
                        "right": "Esa regla solo vale para a, b ≥ 0",
                    },
                    {
                        "wrong": "Todo cuadrado es positivo",
                        "right": "Todo cuadrado REAL es positivo; i no es real",
                    },
                ],
            },
            "explain_prompt": (
                "¿Por qué no se puede usar √a × √b = √(ab) con negativos? Escribe cuánto "
                "vale i² y por qué."
            ),
            "steps": [
                "Fíjate en qué regla usó para juntar las dos raíces.",
                "Comprueba esa regla con dos negativos y mira si sobrevive.",
                "Recuerda de dónde salió i: se DEFINIÓ para que i² = −1. Si diera 1, no habría hecho falta inventarlo.",
            ],
            "solution": (
                "i² = −1 no es un resultado que se calcula: es la definición, la razón de "
                "existir de i. Y «todo cuadrado es positivo» es una frase verdadera SOLO "
                "dentro de ℝ. Cada vez que amplías el conjunto, algunas reglas viejas "
                "dejan de valer — igual que «restar siempre achica» dejó de valer al "
                "llegar los negativos."
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
                "statement": r"Calcula $\sqrt{-25}$ separando el signo del tamaño.",
                "given_steps": [
                    r"-25=25\times(-1)",
                    r"\sqrt{25}=5",
                ],
                "blanks": [
                    {
                        "id": "P1-b1",
                        "label": r"\text{Parte imaginaria de }\sqrt{-25}=",
                        "answer": "5",
                    },
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"El arquitecto anota la casa $7-4i$ en el plano de la ciudad.",
                "given_steps": [
                    r"a+bi\ \Rightarrow\ a=\text{parte real}",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\text{Parte real}=", "answer": "7"},
                    {"id": "P2-b2", "label": r"\text{Parte imaginaria}=", "answer": "-4"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: si i² = −1, entonces i³ = i² × i. ¿Cuánto vale "
                    "i⁴? Responde con el número."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"i^4=", "answer": "1"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos caminos para la misma raíz",
        "intro": (r"Hay que calcular $\sqrt{-16}$. Las dos soluciones de abajo son correctas."),
        "methods": [
            {
                "label": "Método 1 · Separar signo y tamaño",
                "steps": [r"-16=16\times(-1)", r"\sqrt{16}=4,\ \sqrt{-1}=i", r"\sqrt{-16}=4i"],
                "note": "Siempre funciona con raíces de negativos.",
            },
            {
                "label": "Método 2 · Buscar por tanteo el número que da −16",
                "steps": [r"4\times4=16", r"(-4)\times(-4)=16", r"\text{ninguno da}-16"],
                "note": "Concluye que en ℝ no hay, pero no entrega la respuesta.",
            },
        ],
        "question": (
            "¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué te dice el método 2, "
            "aunque no te dé el resultado?"
        ),
        "insight": (
            "El método 2 no fracasa por torpe: te está demostrando algo. Recorre toda la "
            "recta y prueba que ahí NO está la respuesta. Ese fracaso es la justificación "
            "de que haga falta ℂ — igual que buscar la fracción de √2 fracasaba en B07. "
            "Un método que falla bien te dice dónde no buscar."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuál es la parte imaginaria de $\sqrt{-36}$? (Solo el número, sin la i.)",
            "expr": r"\sqrt{-36}",
            "answer": "6",
            "hints": {
                "n1": "Separa −36 en 36 × (−1).",
                "n2": "√36 = 6 y √(−1) = i.",
                "n3": "√(−36) = 6i, así que la parte imaginaria es 6.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"El arquitecto marca la casa $-2+9i$. ¿Cuál es su parte real?",
            "expr": r"-2+9i",
            "answer": "-2",
            "hints": {
                "n1": "En a + bi, ¿cuál de los dos es la parte real?",
                "n2": "La parte real es la que NO va acompañada de i.",
                "n3": "Aquí es −2, y no pierde su signo.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estos números NO es real?",
            "options": [
                {"id": "imaginary", "text": "5i", "latex": r"5i"},
                {"id": "irrational", "text": "√7", "latex": r"\sqrt{7}"},
                {"id": "negative", "text": "−12", "latex": r"-12"},
                {"id": "fraction", "text": "8/3", "latex": r"\dfrac{8}{3}"},
            ],
            "expected": "imaginary",
            "feedback_by_option": {
                "imaginary": "correct",
                "irrational": "fb_b09_e3_irrational",
                "negative": "fb_b09_e3_real",
                "fraction": "fb_b09_e3_real",
            },
            "misconception_by_option": {
                "irrational": "irracional_no_es_real",
                "negative": "negativo_no_es_real",
                "fraction": "fraccion_no_es_real",
            },
            "hints": {
                "n1": "Tres de los cuatro los puedes ubicar en la recta.",
                "n2": "√7 ≈ 2,64 está entre 2 y 3; −12 y 8/3 también tienen su punto.",
                "n3": "5i no está en la recta: su parte imaginaria no es 0.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un discípulo anotó: «√(−4) = −2, porque (−2) × (−2) = −4». ¿Dónde está "
                "el error?"
            ),
            "options": [
                {"id": "product", "text": "(−2) × (−2) = +4, no −4; la respuesta correcta es 2i"},
                {"id": "sign", "text": "Le faltó el signo: es +2"},
                {"id": "no_root", "text": "√(−4) no se puede calcular de ninguna forma"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "product",
            "feedback_by_option": {
                "product": "correct",
                "sign": "fb_b09_e4_sign",
                "no_root": "fb_b09_e4_noroot",
                "none": "fb_b09_e4_none",
            },
            "misconception_by_option": {
                "sign": "cuadrado_conserva_signo",
                "no_root": "irracional_no_existe",
                "none": "cuadrado_conserva_signo",
            },
            "hints": {
                "n1": "Comprueba su cuenta: multiplica (−2) por (−2).",
                "n2": "Da +4, no −4. Negativo por negativo es positivo (eso viene de B05).",
                "n3": "Ningún real sirve; hay que salirse de la recta: √(−4) = 2i.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Cuánto vale $i^2$?",
            "options": [
                {"id": "minus_one", "text": "−1, por definición de i"},
                {"id": "one", "text": "1, porque todo cuadrado es positivo"},
                {"id": "i", "text": "i, porque i por i sigue siendo i"},
                {"id": "zero", "text": "0"},
            ],
            "expected": "minus_one",
            "feedback_by_option": {
                "minus_one": "correct",
                "one": "fb_b09_e5_trap",
                "i": "fb_b09_e5_identity",
                "zero": "fb_b09_e5_zero",
            },
            "misconception_by_option": {
                "one": "cuadrado_siempre_positivo",
                "i": "confunde_producto_con_identidad",
                "zero": "trata_i_como_nada",
            },
            "hints": {
                "n1": "¿Para qué se inventó i? Vuelve a la definición.",
                "n2": "Se definió justamente como el número cuyo cuadrado da −1.",
                "n3": "Si i² diera 1, i sería 1 o −1 y no habría hecho falta inventar nada.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "Mira la escalera completa: ℕ → ℤ → ℚ → ℝ → ℂ. ¿Qué tienen en común TODAS "
                "las ampliaciones?"
            ),
            "options": [
                {
                    "id": "operation",
                    "text": "Cada una nació de una operación que no tenía respuesta en el conjunto anterior",
                },
                {"id": "bigger", "text": "Cada una tiene números más grandes que la anterior"},
                {"id": "replace", "text": "Cada una reemplaza a la anterior, que deja de servir"},
                {"id": "harder", "text": "Cada una es más difícil de entender que la anterior"},
            ],
            "expected": "operation",
            "feedback_by_option": {
                "operation": "correct",
                "bigger": "fb_b09_e6_bigger",
                "replace": "fb_b09_e6_replace",
                "harder": "fb_b09_e6_harder",
            },
            "misconception_by_option": {
                "bigger": "conjuntos_ordenados_por_tamano",
                "replace": "conjunto_nuevo_reemplaza",
                "harder": "dificultad_como_criterio",
            },
            "hints": {
                "n1": "Repasa qué operación falló en cada peldaño.",
                "n2": "Restar en ℕ, dividir en ℤ, la diagonal en ℚ, la raíz de un negativo en ℝ.",
                "n3": "Ninguno reemplaza al anterior: lo contiene. ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál de estos complejos está SOBRE la recta real?",
            "options": [
                {"id": "real", "text": "6 + 0i", "latex": r"6+0i"},
                {"id": "pure", "text": "0 + 6i", "latex": r"0+6i"},
                {"id": "mixed", "text": "6 + 6i", "latex": r"6+6i"},
                {"id": "neg_i", "text": "−6i", "latex": r"-6i"},
            ],
            "expected": "real",
            "feedback_by_option": {
                "real": "correct",
                "pure": "fb_b09_e7_pure",
                "mixed": "fb_b09_e7_mixed",
                "neg_i": "fb_b09_e7_pure",
            },
            "misconception_by_option": {
                "pure": "parte_imaginaria_no_separa",
                "mixed": "parte_imaginaria_no_separa",
                "neg_i": "parte_imaginaria_no_separa",
            },
            "hints": {
                "n1": "¿Qué condición tiene que cumplir b para no separarse de la recta?",
                "n2": "La parte imaginaria debe ser 0.",
                "n3": "6 + 0i = 6, que es el punto de siempre en la recta.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "La escalera de la necesidad",
        "title": "¿Toda raíz cuadrada vive en el conjunto?",
        "intro": "La misma pregunta de B08, ahora con la respuesta completa.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{N}",
                "note": "Ni la diagonal ni las de negativos.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Z}",
                "note": "Los negativos entraron como números, no como raíces.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "no",
                "latex": r"\sqrt{2}\notin\mathbb{Q}",
                "note": "La diagonal no es fracción (B07).",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "no",
                "latex": r"\sqrt{-1}\notin\mathbb{R}",
                "note": "Las de positivos sí; las de negativos no.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"\sqrt{-1}=i\in\mathbb{C}",
                "note": "Aquí toda raíz tiene respuesta. Y aquí se acaba la escalera.",
            },
        ],
        "outro": (
            "ℂ es el final del camino para este tipo de pregunta: cualquier ecuación "
            "polinómica que escribas tiene todas sus soluciones aquí. No hay un ℂ' "
            "esperando después. La escalera terminó."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué estructura comparten las cinco ampliaciones de la escalera?",
        "thumbnails": [r"3-5", r"3\div4", r"\sqrt{2}", r"\sqrt{-1}"],
        "options": [
            {
                "id": "no_answer",
                "text": "En cada una, una operación se quedó sin respuesta",
                "correct": True,
            },
            {
                "id": "contains",
                "text": "Cada conjunto nuevo contiene enterito al anterior",
                "correct": True,
            },
            {
                "id": "bigger_numbers",
                "text": "Cada conjunto tiene números más grandes",
                "correct": False,
            },
            {"id": "same_op", "text": "Todas nacieron de la misma operación", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            r"Calcula $\sqrt{-49}$ y compruébalo multiplicando el resultado por sí mismo. "
            r"¿Cuál es la parte imaginaria del resultado? (Solo el número.)"
        ),
        "polya": {
            "comprender": (
                "Me dan la raíz de un negativo. Me piden el resultado en forma a + bi y "
                "la comprobación. Reporto la parte imaginaria."
            ),
            "planear": (
                "Separo el signo del tamaño, saco la raíz del tamaño, uso i para el signo, "
                "y compruebo elevando al cuadrado."
            ),
            "ejecutar": (
                "−49 = 49 × (−1) → √49 = 7 y √(−1) = i → √(−49) = 7i. "
                "Parte real 0, parte imaginaria 7."
            ),
            "comprobar": (
                "7i × 7i = 49 × i² = 49 × (−1) = −49. ✓ Y noto la trampa evitada: no dije "
                "que fuera −7, porque (−7) × (−7) = +49, no −49."
            ),
        },
        "prompt": "¿Cuál es la parte imaginaria de √(−49)?",
        "answer": "7",
        "hints": {
            "n1": "Separa −49 en 49 × (−1).",
            "n2": "√49 = 7.",
            "n3": "√(−49) = 7i: la parte imaginaria es 7.",
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
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué i² = −1 "
            "es una definición y no un cálculo."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto vale (−5) × (−5)?",
                "answer": "25",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $i^2$?",
                "options": [
                    {"id": "minus_one", "text": "−1"},
                    {"id": "one", "text": "1"},
                    {"id": "i", "text": "i"},
                ],
                "expected": "minus_one",
                "misconception_by_option": {
                    "one": "cuadrado_siempre_positivo",
                    "i": "confunde_producto_con_identidad",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿El número $4+0i$ es real?",
                "options": [
                    {"id": "yes", "text": "Sí: su parte imaginaria es 0, así que está en la recta"},
                    {"id": "no", "text": "No: lleva una i escrita, así que es imaginario"},
                ],
                # Inversa del D3: allá se preguntó por el plano, aquí por el caso
                # en que el plano se reduce a la recta.
                "expected": "yes",
                "misconception_by_option": {"no": "parte_imaginaria_no_separa"},
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
        "fb_b09_e3_irrational": (
            "√7 es irracional pero SÍ es real: cae entre 2 y 3 en la recta (eso fue B08). "
            "→ Busca el que no se puede ubicar en la recta."
        ),
        "fb_b09_e3_real": (
            "Ese tiene su punto en la recta: los negativos y las fracciones son reales. "
            "→ Busca el que tiene parte imaginaria distinta de 0."
        ),
        "fb_b09_e4_sign": (
            "El signo no es el problema: (+2) × (+2) = 4 y (−2) × (−2) = 4. Ningún real "
            "da −4. → Di qué número al cuadrado da −4."
        ),
        "fb_b09_e4_noroot": (
            "Sí se puede, pero fuera de la recta: √(−4) = 2i. «No cabe en ℝ» no es lo "
            "mismo que «no existe». → Comprueba cuánto da 2i × 2i."
        ),
        "fb_b09_e4_none": (
            "Compruébalo: multiplica (−2) por (−2) y mira si da −4. → Entrega ese producto "
            "antes de seguir."
        ),
        "fb_b09_e5_trap": (
            "«Todo cuadrado es positivo» vale dentro de ℝ, y i no es real. i se DEFINIÓ "
            "para que i² = −1: si diera 1, no habría hecho falta inventarlo. → Escribe la "
            "definición de i."
        ),
        "fb_b09_e5_identity": (
            "Eso pasaría con el 1 (1 × 1 = 1) o con el 0, no con i. → Multiplica i por i "
            "usando su definición."
        ),
        "fb_b09_e5_zero": (
            "i no es cero ni «nada»: es un número con su punto en el plano, a una unidad "
            "arriba del 0. → Vuelve a la definición y di cuánto da su cuadrado."
        ),
        "fb_b09_e6_bigger": (
            "El tamaño no es el criterio: −1000 es más «grande» que 2 y aun así ℤ no nació "
            "por eso. → Di qué OPERACIÓN falló en cada peldaño."
        ),
        "fb_b09_e6_replace": (
            "Ninguno reemplaza al anterior: lo contiene. Los naturales siguen ahí dentro "
            "de ℂ. → Mira la cadena ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ."
        ),
        "fb_b09_e6_harder": (
            "La dificultad no define un conjunto de números. → Busca qué se rompía en cada "
            "paso: una operación sin respuesta."
        ),
        "fb_b09_e7_pure": (
            "Ese tiene parte imaginaria distinta de 0, así que se separa de la recta. → "
            "Busca el que tiene b = 0."
        ),
        "fb_b09_e7_mixed": (
            "Ese se mueve a lo ancho Y a lo alto: queda dentro del plano, fuera de la "
            "recta. → Busca el que solo se mueve a lo ancho."
        ),
    },
    "closing": (
        "«Imaginario» fue un insulto que le pusieron a estos números cuando aparecieron, "
        "y se les quedó pegado. No son menos reales que −3: los dos se inventaron para "
        "que una operación tuviera respuesta. Con esto la escalera está completa."
    ),
    "validation_status": "F1_B09_11bloques",
}
