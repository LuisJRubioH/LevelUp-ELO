"""B10 · Clasificador básico — primero resuelve, después clasifica.

Arquitectura de 11 bloques (molde aprobado en B06).
Misconception focal: «clasifico por cómo está escrito el número» — 6/2 «es una
fracción», 0,5 «es un decimal, no un racional».
"""

NODE_ID = "PREALG-N1-B10-CLASIFICADOR-BASICO"
CONCEPT_SLUG = "clasificador"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "clasificador",
    "misconception": "clasifica_por_apariencia",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ----------------------------------------------
    "kicker": "Consolidación · Clasificador",
    "finish_label": "Continuar al clasificador riguroso",
    "title": "Un número no es su disfraz",
    "intro": (
        "Ya conoces los cinco peldaños. Ahora viene la habilidad que los pone a trabajar: "
        "mirar un número cualquiera y decir a qué conjunto pertenece. El truco no está en "
        "reconocer símbolos — está en resolver antes de decidir."
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
                "prompt": r"¿Qué clase de número es $\dfrac{6}{2}$?",
                "options": [
                    {"id": "natural", "text": "Natural: vale 3"},
                    {"id": "fraction_only", "text": "Racional no entero: es una fracción"},
                    {"id": "irrational", "text": "Irracional: tiene barra de división"},
                ],
                "expected": "natural",
                "misconception_by_option": {
                    "fraction_only": "clasifica_por_apariencia",
                    "irrational": "clasifica_por_apariencia",
                },
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $\sqrt{100}$?",
                "answer": "10",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿$0{,}5$ es racional?",
                "options": [
                    {"id": "yes", "text": "Sí: es 1/2"},
                    {"id": "no_decimal", "text": "No: es un decimal, no un racional"},
                    {"id": "no_irrational", "text": "No: es irracional"},
                ],
                "expected": "yes",
                "misconception_by_option": {
                    "no_decimal": "decimal_y_racional_son_categorias_distintas",
                    "no_irrational": "clasifica_por_apariencia",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino ----------------------
    "katia": {
        "eyebrow": "KatIA · Consolidación",
        "title": "El bibliotecario y las tablillas sin abrir",
        "body": (
            "La biblioteca del ágora recibió un cargamento de tablillas y el bibliotecario "
            "tiene que ordenarlas por tema. Como son cientos, decidió clasificarlas por el "
            "color de la cuerda con que vienen atadas: las de cuerda roja a poesía, las de "
            "cuerda azul a geometría.\n\n"
            "Al día siguiente un discípulo fue a buscar un tratado de geometría y encontró "
            "en ese estante una lista de mercado. Venía con cuerda azul."
        ),
        "question": (
            "¿Qué tenía que haber hecho el bibliotecario antes de decidir el estante de "
            "cada tablilla?"
        ),
        "image": "/leccion/01-prealg-n1-agora/b10-clasificador-i-v4.png",
        # Intento genuino: obligatorio, NUNCA calificado.
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que crees tú. Cualquiera vale.",
            "options": [
                {"id": "a", "text": "Abrir y leer cada tablilla antes de clasificarla"},
                {"id": "b", "text": "Usar cuerdas de más colores"},
                {"id": "c", "text": "Nada: con cientos de tablillas hay que confiar en la cuerda"},
            ],
            "response": (
                "Veámoslo. Guarda esa respuesta: al final del nodo vas a saber por qué con "
                "los números pasa exactamente lo mismo que con las cuerdas."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición formal ----------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos números con el mismo disfraz y distinta casa",
        "body": (
            "Los dos números de abajo están escritos igual: barra de fracción, dos enteros. "
            "Si clasificas por el aspecto, van al mismo estante. Y no van al mismo estante."
        ),
        "cases": [
            {
                "label": "Se ve fracción y NO lo es",
                "context": "Ocho tablillas repartidas en cuatro cajones",
                "fraction": r"\dfrac{8}{4}",
                "division": r"\dfrac{8}{4}=2",
                "note": (
                    "Al resolver da 2, que es natural. La barra era solo la forma de "
                    "escribirlo, no lo que era."
                ),
            },
            {
                "label": "Se ve fracción y SÍ lo es",
                "context": "Ocho tablillas repartidas en cinco cajones",
                "fraction": r"\dfrac{8}{5}",
                "division": r"\dfrac{8}{5}=1{,}6",
                "note": (
                    "Al resolver da 1,6, que cae entre dos enteros. Este sí es racional no "
                    "entero: no hay forma de escribirlo sin partes."
                ),
            },
        ],
        "resolution": (
            "La regla sale sola: **primero resuelve, después clasifica**. El aspecto de un "
            "número —barra, coma, signo de raíz— es su ropa, no su identidad. 8/4 y 8/5 "
            "usan la misma ropa y viven en peldaños distintos."
        ),
    },
    "definition_title": "Clasificar un número",
    "definition_katex": r"\text{simplificar}\ \longrightarrow\ \text{identificar}\ \longrightarrow\ \text{el conjunto MÁS PEQUEÑO que lo contiene}",
    "definition": (
        "La frase del nodo: clasificar es decir cuál es el peldaño más bajo en el que el "
        "número ya cabe. Por la cadena de inclusión, todos los de arriba lo contienen también."
    ),
    "definition_symbols": [
        {
            "symbol": r"\dfrac{a}{b}",
            "reads": "una fracción escrita",
            "means": "puede dar entero o no: hay que dividir para saberlo",
        },
        {
            "symbol": r"\sqrt{n}",
            "reads": "raíz de n",
            "means": "puede ser natural (√9=3) o irracional (√2): hay que resolverla",
        },
        {
            "symbol": r"0{,}\overline{3}",
            "reads": "decimal periódico",
            "means": "se repite ⇒ viene de fracción ⇒ es racional",
        },
        {
            "symbol": r"-4",
            "reads": "menos cuatro",
            "means": "el signo baja de peldaño (sale de ℕ), no sube",
        },
        {
            "symbol": r"\subset",
            "reads": "contenido en",
            "means": "por eso basta nombrar el más pequeño: los mayores vienen incluidos",
        },
        {
            "symbol": r"\mathbb{R}",
            "reads": "los reales",
            "means": "la respuesta de seguridad: casi todo lo que verás está aquí",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos (a, b, trampa) ------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La raíz que era natural",
            "title": "El sello de la tablilla",
            "statement": r"Clasifica el número $\sqrt{49}$: ¿cuál es el conjunto más pequeño que lo contiene?",
            "latex": r"\sqrt{49}",
            "image_slot": False,
            "steps": [
                "No clasifico todavía: primero resuelvo lo que se pueda resolver.",
                "Busco el número que multiplicado por sí mismo da 49: es 7.",
                "√49 = 7, y ahora sí clasifico el 7, no el símbolo de raíz.",
                "7 cuenta cantidades completas → cabe ya en ℕ, el peldaño más bajo.",
                "Respuesta: natural. Y por inclusión también es entero, racional y real.",
            ],
            "solution": r"$\sqrt{49}=7\in\mathbb{N}$",
            # Bloque 5 · UNA sola autoexplicación focal en todo el nodo.
            "self_explanation": {
                "step_index": 0,
                "prompt": (
                    "En el paso 1 me negué a clasificar antes de resolver. ¿Qué habría "
                    "pasado si clasificaba mirando el signo de raíz?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El decimal que era racional",
            "title": "La medida del inventario",
            "statement": r"Clasifica el número $-2{,}75$: ¿cuál es el conjunto más pequeño que lo contiene?",
            "latex": r"-2{,}75",
            "image_slot": False,
            "steps": [
                "Tiene coma, así que no es natural ni entero: cae entre −3 y −2.",
                "¿Se puede escribir como fracción de enteros? El decimal termina, así que sí.",
                "−2,75 = −275/100 = −11/4, fracción de enteros.",
                "Cabe en ℚ, y no cabe en ningún peldaño más bajo.",
                "Respuesta: racional no entero. Por inclusión también es real.",
            ],
            "solution": r"$-2{,}75=-\dfrac{11}{4}\in\mathbb{Q}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "La clasificación hecha de un vistazo",
            "statement": (
                "Un discípulo clasificó estas tres así. Está mal: «6/3 es racional no "
                "entero porque tiene barra. √16 es irracional porque tiene raíz. Y 0,25 "
                "no es racional, es decimal»."
            ),
            "latex": r"\dfrac{6}{3},\ \sqrt{16},\ 0{,}25",
            "trap": True,
            # Deslizador de confianza ANTES de revelar (hipercorrección, Metcalfe 2017).
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\text{criterio usado}:\ \underline{\text{el símbolo que se ve}}",
            "error_note": (
                "Aquí se cayó, y las tres veces por lo mismo: clasificó por el símbolo "
                "visible en vez de resolver. Ninguna de las tres respuestas es correcta."
            ),
            "correct_version": {
                "wrong_latex": r"\dfrac{6}{3}\in\mathbb{Q}\setminus\mathbb{Z},\ \ \sqrt{16}\in\mathbb{I},\ \ 0{,}25\notin\mathbb{Q}",
                "right_latex": r"\dfrac{6}{3}=2\in\mathbb{N},\ \ \sqrt{16}=4\in\mathbb{N},\ \ 0{,}25=\dfrac{1}{4}\in\mathbb{Q}",
                "rows": [
                    {
                        "wrong": "Barra de fracción ⇒ racional no entero",
                        "right": "6/3 = 2: la barra desaparece al dividir",
                    },
                    {
                        "wrong": "Signo de raíz ⇒ irracional · coma ⇒ no racional",
                        "right": "√16 = 4 es natural; 0,25 = 1/4 es racional",
                    },
                ],
            },
            "explain_prompt": (
                "¿Qué paso se saltó en las tres? Escribe la clasificación correcta de " "las tres."
            ),
            "steps": [
                "Resuelve cada una antes de mirar a qué conjunto la mandas.",
                "6 ÷ 3 = 2 y √16 = 4: los dos son naturales.",
                "0,25 termina, así que viene de una fracción: 1/4, racional.",
            ],
            "solution": (
                "Decimal y racional no son categorías rivales: un decimal que termina o se "
                "repite ES un racional escrito de otra forma. Y la barra o la raíz son "
                "operaciones pendientes, no etiquetas. Resuelve primero; clasifica después."
            ),
        },
    ],
    # --- Bloque 6 · Puente (parcialmente resueltos) --------------------------
    "bridge": {
        "intro": (
            "Ahora los resuelves tú, pero no desde cero: la simplificación ya está "
            "empezada y solo faltan huecos."
        ),
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Clasifica $\dfrac{20}{5}$. ¿Cuánto vale?",
                "given_steps": [
                    r"\dfrac{20}{5}=20\div5",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\dfrac{20}{5}=", "answer": "4"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Clasifica $\sqrt{144}$ y $\dfrac{9}{4}$: da el valor de cada una.",
                "given_steps": [
                    r"12\times12=144",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"\sqrt{144}=", "answer": "12"},
                    {"id": "P2-b2", "label": r"\dfrac{9}{4}=", "answer": "2,25"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: de esta lista, ¿cuántos números son naturales "
                    "después de resolverlos? 15/3 · √25 · 7/2 · √8 · 0"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{Naturales en la lista}=", "answer": "3"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos (siempre DESPUÉS del puente) ------
    "method_comparison": {
        "title": "Dos formas de clasificar el mismo número",
        "intro": r"¿Qué clase de número es $\dfrac{45}{15}$? Las dos soluciones son correctas.",
        "methods": [
            {
                "label": "Método 1 · Simplificar primero",
                "steps": [r"\dfrac{45}{15}=\dfrac{3}{1}", r"=3", r"3\in\mathbb{N}"],
                "note": "Rápido cuando la simplificación salta a la vista.",
            },
            {
                "label": "Método 2 · Dividir y mirar el decimal",
                "steps": [
                    r"45\div15=3{,}0",
                    r"\text{decimal exacto sin parte decimal}",
                    r"\Rightarrow\ \text{entero}",
                ],
                "note": "Siempre funciona, incluso con números feos.",
            },
        ],
        "question": (
            r"¿Cuál conviene aquí y por qué? Y la de verdad: ¿qué pasa si aplicas el "
            r"método 2 a $\dfrac{1}{3}$?"
        ),
        "insight": (
            "Con 1/3 el método 2 te deja mirando 0,333… sin final, y si te apuras "
            "concluyes «no termina ⇒ irracional» — el error de B07. El método 1 no tiene "
            "ese riesgo: 1/3 ya está escrito como fracción de enteros, y con eso basta "
            "para decir racional. Cuando la fracción está a la vista, no la conviertas."
        ),
    },
    # --- Bloque 8 · Práctica independiente -----------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"Resuelve antes de clasificar: ¿cuánto vale $\dfrac{36}{4}$?",
            "expr": r"\dfrac{36}{4}",
            "answer": "9",
            "hints": {
                "n1": "La barra es el signo de dividir.",
                "n2": "¿Cuántas veces cabe 4 en 36?",
                "n3": "36 ÷ 4 = 9, que es natural aunque viniera escrito como fracción.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "De esta lista, ¿cuántos son NATURALES una vez resueltos? 24/8 · √36 · 5/2 · √7 · 0 · −3",
            "expr": r"\tfrac{24}{8},\ \sqrt{36},\ \tfrac{5}{2},\ \sqrt{7},\ 0,\ -3",
            "answer": "3",
            "hints": {
                "n1": "Resuelve cada uno antes de contar.",
                "n2": "24/8 = 3 y √36 = 6; el 0 también es natural en este curso.",
                "n3": "5/2 = 2,5 no lo es, √7 tampoco, y −3 es entero pero no natural.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuál es el conjunto MÁS PEQUEÑO que contiene a $\dfrac{14}{7}$?",
            "options": [
                {"id": "naturals", "text": "ℕ, los naturales", "latex": r"\mathbb{N}"},
                {"id": "rationals", "text": "ℚ, los racionales", "latex": r"\mathbb{Q}"},
                {"id": "integers", "text": "ℤ, los enteros", "latex": r"\mathbb{Z}"},
                {"id": "reals", "text": "ℝ, los reales", "latex": r"\mathbb{R}"},
            ],
            "expected": "naturals",
            "feedback_by_option": {
                "naturals": "correct",
                "rationals": "fb_b10_e3_appearance",
                "integers": "fb_b10_e3_integers",
                "reals": "fb_b10_e3_reals",
            },
            "misconception_by_option": {
                "rationals": "clasifica_por_apariencia",
                "integers": "olvida_que_es_positivo",
                "reals": "elige_el_mas_grande",
            },
            "hints": {
                "n1": "Primero resuelve la división.",
                "n2": "14 ÷ 7 = 2.",
                "n3": "El 2 ya cabe en el primer peldaño: ℕ.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un discípulo anotó: «√81 es irracional, porque todas las raíces "
                "cuadradas son irracionales». ¿Dónde está el error?"
            ),
            "options": [
                {"id": "resolve", "text": "No resolvió: √81 = 9, que es natural"},
                {"id": "sign", "text": "Se le olvidó que la raíz también puede ser negativa"},
                {"id": "rational", "text": "√81 es racional no entero, no natural"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "resolve",
            "feedback_by_option": {
                "resolve": "correct",
                "sign": "fb_b10_e4_sign",
                "rational": "fb_b10_e4_rational",
                "none": "fb_b10_e4_none",
            },
            "misconception_by_option": {
                "sign": "distrae_con_signo",
                "rational": "clasifica_por_apariencia",
                "none": "toda_raiz_es_irracional",
            },
            "hints": {
                "n1": "¿9 × 9 cuánto da?",
                "n2": "81. Así que √81 = 9.",
                "n3": "9 es natural: la generalización «toda raíz es irracional» es falsa.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «$\dfrac{10}{5}$ es racional no entero, porque está escrito como fracción.»",
            "options": [
                {"id": "false_two", "text": "Falsa: 10/5 = 2, que es natural y entero"},
                {
                    "id": "true_written",
                    "text": "Verdadera: si está escrito como fracción, es racional no entero",
                },
                {"id": "false_irrational", "text": "Falsa: 10/5 es irracional"},
                {"id": "depends", "text": "Depende de si lo simplificas o no"},
            ],
            "expected": "false_two",
            "feedback_by_option": {
                "false_two": "correct",
                "true_written": "fb_b10_e5_trap",
                "false_irrational": "fb_b10_e5_irrational",
                "depends": "fb_b10_e5_depends",
            },
            "misconception_by_option": {
                "true_written": "clasifica_por_apariencia",
                "false_irrational": "clasifica_por_apariencia",
                "depends": "representacion_define_el_numero",
            },
            "hints": {
                "n1": "Divide antes de decidir.",
                "n2": "10 ÷ 5 = 2.",
                "n3": "El 2 es natural. La ropa era de fracción; el número no.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": (
                "El bibliotecario quiere una regla que le sirva SIEMPRE para clasificar un "
                "número. ¿Cuál le sirve?"
            ),
            "options": [
                {
                    "id": "resolve_first",
                    "text": "Resolver todas las operaciones y después buscar el peldaño más bajo",
                },
                {"id": "look_symbol", "text": "Mirar si tiene barra, coma o raíz"},
                {"id": "count_digits", "text": "Contar cuántas cifras tiene"},
                {"id": "always_real", "text": "Decir siempre «real»: nunca se equivoca"},
            ],
            "expected": "resolve_first",
            "feedback_by_option": {
                "resolve_first": "correct",
                "look_symbol": "fb_b10_e6_symbol",
                "count_digits": "fb_b10_e6_digits",
                "always_real": "fb_b10_e6_real",
            },
            "misconception_by_option": {
                "look_symbol": "clasifica_por_apariencia",
                "count_digits": "confunde_tamano_con_tipo",
                "always_real": "elige_el_mas_grande",
            },
            "hints": {
                "n1": "Vuelve a la historia del bibliotecario: ¿qué le falló?",
                "n2": "Clasificó por la cuerda sin abrir la tablilla.",
                "n3": "La regla equivalente con números es resolver antes de decidir.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál de estos números NO es natural una vez resuelto?",
            "options": [
                {"id": "seven_halves", "text": "7/2", "latex": r"\dfrac{7}{2}"},
                {"id": "thirty_six", "text": "√36", "latex": r"\sqrt{36}"},
                {"id": "eighteen_thirds", "text": "18/3", "latex": r"\dfrac{18}{3}"},
                {"id": "hundred", "text": "√100", "latex": r"\sqrt{100}"},
            ],
            "expected": "seven_halves",
            "feedback_by_option": {
                "seven_halves": "correct",
                "thirty_six": "fb_b10_e7_natural",
                "eighteen_thirds": "fb_b10_e7_natural",
                "hundred": "fb_b10_e7_natural",
            },
            "misconception_by_option": {
                "thirty_six": "clasifica_por_apariencia",
                "eighteen_thirds": "clasifica_por_apariencia",
                "hundred": "clasifica_por_apariencia",
            },
            "hints": {
                "n1": "Resuelve los cuatro antes de comparar.",
                "n2": "√36 = 6, 18/3 = 6 y √100 = 10: los tres son naturales.",
                "n3": "7 ÷ 2 = 3,5, que cae entre dos enteros.",
            },
        },
    ],
    # --- Bloque 9 · Cierre (escalera + abstracción + Pólya) ------------------
    "closure": {
        "eyebrow": "El disfraz y la casa",
        "title": "Cómo se ve un número y dónde vive de verdad",
        "intro": "Cada fila es una escritura que engaña. Resuelve y mira dónde cae.",
        "rows": [
            {
                "symbol": r"\dfrac{8}{4}",
                "name": "Se ve fracción",
                "closed": "yes",
                "latex": r"=2\in\mathbb{N}",
                "note": "La barra se fue al dividir.",
            },
            {
                "symbol": r"\sqrt{25}",
                "name": "Se ve raíz",
                "closed": "yes",
                "latex": r"=5\in\mathbb{N}",
                "note": "El radicando era cuadrado perfecto.",
            },
            {
                "symbol": r"0{,}75",
                "name": "Se ve decimal",
                "closed": "yes",
                "latex": r"=\dfrac{3}{4}\in\mathbb{Q}",
                "note": "Decimal que termina ⇒ racional.",
            },
            {
                "symbol": r"0{,}\overline{6}",
                "name": "Se ve infinito",
                "closed": "yes",
                "latex": r"=\dfrac{2}{3}\in\mathbb{Q}",
                "note": "Se repite ⇒ racional, aunque no termine.",
            },
            {
                "symbol": r"\sqrt{2}",
                "name": "Se ve raíz (otra vez)",
                "closed": "no",
                "latex": r"\notin\mathbb{Q}",
                "note": "Aquí sí: el radicando no es cuadrado perfecto.",
            },
        ],
        "outro": (
            "Las dos filas de raíz se ven igual y terminan en peldaños opuestos. Esa es la "
            "prueba de que el símbolo no clasifica: solo el valor lo hace."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué tienen en común los errores de clasificación de este nodo?",
        "thumbnails": [r"\dfrac{6}{3}", r"\sqrt{16}", r"0{,}25"],
        "options": [
            {
                "id": "symbol",
                "text": "En los tres se decidió mirando el símbolo, sin resolver",
                "correct": True,
            },
            {
                "id": "skipped",
                "text": "En los tres faltó un paso antes de clasificar",
                "correct": True,
            },
            {"id": "hard", "text": "Los tres son números difíciles", "correct": False},
            {"id": "irrational", "text": "Los tres son irracionales", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El bibliotecario tiene seis tablillas con estos números: 48/6 · √64 · 9/4 · "
            "√5 · −7 · 0,125. ¿Cuántas van al estante de los NATURALES?"
        ),
        "polya": {
            "comprender": (
                "Me dan seis números escritos de formas distintas. Me piden cuántos son "
                "naturales una vez resueltos."
            ),
            "planear": (
                "Resuelvo los seis primero, sin clasificar nada. Después miro cuáles "
                "quedaron como cantidades completas sin signo negativo."
            ),
            "ejecutar": (
                "48/6 = 8 ✓ · √64 = 8 ✓ · 9/4 = 2,25 ✗ · √5 ✗ (irracional) · "
                "−7 ✗ (entero, no natural) · 0,125 = 1/8 ✗. Van 2."
            ),
            "comprobar": (
                "Los dos que conté (8 y 8) cuentan cantidades completas. ✓ Y noto la "
                "trampa: los dos venían disfrazados, uno de fracción y otro de raíz."
            ),
        },
        "prompt": "¿Cuántas de las seis van al estante de los naturales?",
        "answer": "2",
        "hints": {
            "n1": "Resuelve las seis antes de contar nada.",
            "n2": "48/6 y √64 dan los dos el mismo número.",
            "n3": "−7 es entero pero no natural; 9/4 y 0,125 tienen parte decimal.",
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
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el paso que se "
            "salta antes de clasificar."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Qué clase de número es $\dfrac{12}{4}$?",
                "options": [
                    {"id": "natural", "text": "Natural: vale 3"},
                    {"id": "fraction_only", "text": "Racional no entero: es fracción"},
                ],
                "expected": "natural",
                "misconception_by_option": {"fraction_only": "clasifica_por_apariencia"},
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $\sqrt{121}$?",
                "answer": "11",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿$\sqrt{3}$ es racional?",
                "options": [
                    {"id": "no", "text": "No: 3 no es cuadrado de ningún entero"},
                    {"id": "yes", "text": "Sí: toda raíz se puede escribir como fracción"},
                ],
                # Inversa del D3 a propósito: allá la respuesta era «sí», aquí «no».
                # Contesta bien quien resuelve, no quien memorizó una de las dos.
                "expected": "no",
                "misconception_by_option": {"yes": "todo_numero_es_fraccion"},
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
        "fb_b10_e3_appearance": (
            "Clasificaste por la barra sin dividir. 14 ÷ 7 = 2, y 2 es natural. → Resuelve "
            "la división y vuelve a decidir."
        ),
        "fb_b10_e3_integers": (
            "Sí es entero, pero te falta un peldaño hacia abajo: 2 es positivo y cuenta "
            "objetos completos. → Di si 2 cabe en ℕ."
        ),
        "fb_b10_e3_reals": (
            "Es real, cierto, pero se pide el conjunto MÁS PEQUEÑO que lo contiene. Con ese "
            "criterio «real» sirve para todos y no clasifica nada. → Baja hasta el primer "
            "peldaño donde 2 ya cabe."
        ),
        "fb_b10_e4_sign": (
            "El signo no es el problema aquí: la raíz cuadrada que usamos da el valor "
            "positivo. El fallo es que no resolvió. → Calcula √81."
        ),
        "fb_b10_e4_rational": (
            "√81 = 9, que es natural, no racional no entero. Caíste en el mismo error de "
            "clasificar sin resolver. → Di cuánto vale √81."
        ),
        "fb_b10_e4_none": (
            "Compruébalo: 9 × 9 = 81, así que √81 = 9 y 9 es natural. La regla «toda raíz "
            "es irracional» tiene contraejemplos. → Da uno."
        ),
        "fb_b10_e5_trap": (
            "Ese es justo el error del nodo: cómo está ESCRITO no decide qué ES. 10/5 = 2, "
            "natural. → Divide y clasifica el resultado."
        ),
        "fb_b10_e5_irrational": (
            "10/5 ya es fracción de enteros, así que racional seguro. Y además da 2. → "
            "Haz la división."
        ),
        "fb_b10_e5_depends": (
            "El número es el mismo esté simplificado o no: 10/5 y 2 son idénticos. La "
            "escritura no lo cambia. → Di cuánto vale 10 ÷ 5."
        ),
        "fb_b10_e6_symbol": (
            "Es exactamente lo que le falló al bibliotecario con las cuerdas. √16 y √2 "
            "llevan el mismo símbolo y viven en peldaños opuestos. → Busca la regla que "
            "mira el valor."
        ),
        "fb_b10_e6_digits": (
            "El tamaño no clasifica: 1000000 es natural y 0,5 no lo es. → Busca la regla "
            "que resuelve antes de decidir."
        ),
        "fb_b10_e6_real": (
            "Nunca se equivoca y por eso no sirve: si todo es «real», no clasificaste "
            "nada. Clasificar es encontrar el peldaño MÁS BAJO. → Busca la regla que sí "
            "distingue."
        ),
        "fb_b10_e7_natural": (
            "Ese sí da natural al resolverlo. → Resuelve los cuatro y busca el único que "
            "queda con parte decimal."
        ),
    },
    "closing": (
        "El bibliotecario aprendió a abrir la tablilla antes de elegir el estante. Resolver "
        "primero, clasificar después. En el siguiente nodo vas a ver que un mismo número "
        "vive en varios estantes a la vez."
    ),
    "validation_status": "F1_B10_11bloques",
}
