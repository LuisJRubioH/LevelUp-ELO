"""O03 · El taller de cinceles — multiplicar no es amontonar exponentes.

Tercera sala de la obra de la pirámide. Guía: Bakenra. Vocabulario propio:
taller de cinceles, hoja, filo, sillar, plantilla, tallado, hilada de piedra.
Nada de rampas ni trineos (O01), poleas ni vales (O02), ni agua (O04).

Error focal: multiplicar los exponentes al multiplicar potencias de la misma
base — x²·x³ = x⁶ en vez de x⁵. Se cura contando factores, no memorizando.
"""

NODE_ID = "ALG-N1-O03-PRODUCTO"
CONCEPT_SLUG = "producto_de_monomios"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "producto_de_monomios",
    "misconception": "multiplica_los_exponentes_al_multiplicar",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El taller de cinceles · Producto de monomios",
    "house": "El taller de cinceles",
    "guide": "Bakenra",
    "finish_label": "Bajar a la caseta del capataz",
    "title": "Multiplicar potencias es contar factores, no amontonar exponentes",
    "intro": (
        "En el patio aprendiste que un signo de fuera entra hasta el último término. Aquí "
        "lo de fuera no es un signo, es un factor — y cuando las letras se multiplican "
        "entre sí hay una contabilidad nueva que llevar: la de los exponentes."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar al taller. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 2³?",
                "answer": "8",
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 4 · (2 + 3)?",
                "answer": "20",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $x^{2}\cdot x^{3}$?",
                "options": [
                    {"id": "five", "text": r"$x^{5}$", "latex": r"x^{5}"},
                    {"id": "six", "text": r"$x^{6}$", "latex": r"x^{6}"},
                    {"id": "two", "text": r"$2x^{5}$", "latex": r"2x^{5}"},
                ],
                "expected": "five",
                "misconception_by_option": {
                    "six": "multiplica_los_exponentes_al_multiplicar",
                    "two": "suma_las_bases_al_multiplicar",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/o03-producto-katia.png",
        "eyebrow": "KatIA · En el taller de cinceles",
        "title": "El pedido de piedra que no cabía en Egipto",
        "body": (
            "En el taller se afilan las hojas y se marcan las plantillas de cada sillar. "
            "Bakenra tiene delante un pedido de piedra que le llegó del tallador mayor.\n\n"
            "«Para una hilada hacen falta x² sillares, y hay que levantar x³ hiladas. El "
            "tallador pidió x⁶ sillares. Con x = 10 eso es un millón de piedras.»\n\n"
            "Bakenra deja la tablilla sobre el banco.\n\n"
            "«La cantera entera ha sacado ochenta mil piedras en veinte años. El número "
            "estaba mal, y lo peor es que sabía la regla: la dijo en voz alta antes de "
            "escribirla.»"
        ),
        "question": "Al multiplicar dos potencias de la misma letra, ¿qué pasa con los exponentes?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Se multiplican entre sí, igual que las potencias"},
                {"id": "b", "text": "Se suman"},
                {"id": "c", "text": "Se queda el mayor de los dos"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decidirlo sin recordar ninguna "
                "regla: contando cuántas veces aparece la letra."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Desplegar la potencia y contar",
        "body": "Una potencia es una abreviatura. Si se despliega, no hay nada que recordar.",
        "cases": [
            {
                "label": "Multiplicar potencias",
                "context": r"$x^{2}\cdot x^{3}$ desplegado",
                "fraction": r"(x\cdot x)(x\cdot x\cdot x)",
                "division": r"x^{5}",
                "note": "Dos factores y tres factores son cinco factores. Los exponentes se SUMAN.",
            },
            {
                "label": "Elevar una potencia",
                "context": r"$(x^{2})^{3}$ desplegado",
                "fraction": r"x^{2}\cdot x^{2}\cdot x^{2}",
                "division": r"x^{6}",
                "note": "Tres grupos de dos factores son seis. Aquí sí se multiplican los exponentes.",
            },
        ],
        "resolution": (
            "Las dos reglas salen de lo mismo: contar cuántas veces está escrita la letra. "
            "Multiplicar dos potencias junta los factores de las dos, así que se suman los "
            "exponentes. Elevar una potencia repite el grupo entero, así que se multiplican. "
            "El error del tallador fue usar la segunda cuenta para el primer caso."
        ),
    },
    "definition_title": "Producto de monomios",
    "definition_katex": r"(a x^{m})(b x^{n}) = ab\,x^{m+n}",
    "definition": (
        "Para MULTIPLICAR dos monomios se multiplican los coeficientes y, en cada letra que "
        "aparezca en los dos, se SUMAN los exponentes. Las letras que solo aparecen en uno "
        "se copian tal cual. Cuidado con lo que no se mezcla: los coeficientes se "
        "multiplican, los exponentes se suman — cada uno lleva su propia cuenta."
    ),
    "definition_symbols": [
        {"symbol": r"x^{2}\cdot x^{3}=x^{5}", "reads": "equis dos por equis tres", "means": "misma letra: se suman los exponentes"},
        {"symbol": r"(3x)(4x)=12x^{2}", "reads": "tres equis por cuatro equis", "means": "coeficientes se multiplican, exponentes se suman"},
        {"symbol": r"x=x^{1}", "reads": "el exponente invisible", "means": "una letra sola lleva un 1 que no se escribe"},
        {"symbol": r"x^{2}\cdot y^{3}", "reads": "no se junta", "means": "letras distintas: no hay nada que sumar"},
        {"symbol": r"(x^{2})^{3}=x^{6}", "reads": "potencia de potencia", "means": "el otro caso: aquí SÍ se multiplican"},
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La plantilla repetida",
            "title": "Repartir un factor por dentro del paréntesis",
            "statement": (
                "Cada plantilla del taller marca (2f + 3) trazos, donde f son los filos que "
                "lleva la hoja. Hay que marcar 4 plantillas iguales. ¿Cuántos trazos son?"
            ),
            "latex": r"4(2f+3)",
            "image_slot": False,
            "steps": [
                "El 4 multiplica a la plantilla ENTERA, igual que el menos del patio afectaba a todo.",
                "Reparto el 4 a cada término: 4 · 2f y 4 · 3.",
                "4 · 2f = 8f, porque se multiplican los coeficientes y la f se copia.",
                "4 · 3 = 12.",
                "Quedan 8f + 12. Con f = 5: 4 · 13 = 52, y 8 · 5 + 12 = 52 ✓.",
            ],
            "solution": r"$4(2f+3)=8f+12$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué el 4 multiplica también al 3, si el 3 no tiene letra?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Sillares por hilada",
            "title": "Multiplicar dos monomios",
            "statement": (
                "Cada hilada lleva 3s sillares y hay que levantar 5s² hiladas, donde s es "
                "el ancho del muro en varas. ¿Cuántos sillares hacen falta?"
            ),
            "latex": r"(3s)(5s^{2})",
            "image_slot": False,
            "steps": [
                "Separo las dos cuentas: la de los coeficientes y la de la letra.",
                "Coeficientes: 3 · 5 = 15. Se multiplican, como cualquier par de números.",
                "Letra: s es s¹, así que s¹ · s² tiene 1 + 2 = 3 factores → s³.",
                "Junto las dos cuentas: 15s³.",
                "Compruebo con s = 2: (6)(20) = 120, y 15 · 8 = 120 ✓.",
            ],
            "solution": r"$(3s)(5s^{2})=15s^{3}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El tallador que multiplicó los exponentes",
            "statement": (
                "Vuelve el pedido de la apertura: x² sillares por hilada, x³ hiladas. El "
                "tallador escribió x²·x³ = x⁶ y pidió un millón de piedras."
            ),
            "latex": r"x^{2}\cdot x^{3}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"x^{2}\cdot x^{3}=x^{6}",
            "error_note": (
                "Usó la regla de la potencia de una potencia en un producto de potencias. "
                "Con x = 10 la diferencia no es pequeña: 100 000 frente a 1 000 000."
            ),
            "correct_version": {
                "wrong_latex": r"x^{2}\cdot x^{3}=x^{2\cdot 3}=x^{6}",
                "right_latex": r"x^{2}\cdot x^{3}=x^{2+3}=x^{5}",
                "rows": [
                    {"wrong": "Multiplicar potencias multiplica los exponentes",
                     "right": "Multiplicar potencias junta los factores: se suman"},
                    {"wrong": r"(x\cdot x)(x\cdot x\cdot x)\ \text{tiene}\ 6\ \text{factores}",
                     "right": r"(x\cdot x)(x\cdot x\cdot x)\ \text{tiene}\ 5\ \text{factores}"},
                ],
            },
            "explain_prompt": (
                "Despliega los dos productos y di cuántas veces aparece la x. Después "
                "explica en qué caso sí se multiplican los exponentes."
            ),
            "steps": [
                "Escribo la x tantas veces como diga cada exponente: x·x y x·x·x.",
                "Las junto todas en fila y cuento: cinco. No hay manera de que salgan seis.",
                "Regla para no volver a caer: si dudas, despliega y cuenta. La regla es el atajo, no la fuente.",
            ],
            "solution": (
                "x² · x³ = x⁵. La cantera no tenía que sacar un millón de piedras sino cien "
                "mil, que ya era bastante."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El pedido va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Multiplica $(2f)(6f)$.",
                "given_steps": [r"2\cdot 6=12", r"f^{1}\cdot f^{1}=f^{2}"],
                "blanks": [{"id": "P1-b1", "label": r"\text{coeficiente del resultado}=", "answer": "12"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Reparte el factor: $5(3s+4)$, y evalúa con $s=2$.",
                "given_steps": [r"5\cdot 3s+5\cdot 4"],
                "blanks": [
                    {"id": "P2-b1", "label": r"5\cdot 4=", "answer": "20"},
                    {"id": "P2-b2", "label": r"15\cdot 2+20=", "answer": "50"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $(4s^{2})(3s)$ con $s=2$. Primero el monomio, "
                    "después el valor."
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"12s^{3}\ \text{con}\ s=2:", "answer": "96"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de multiplicar potencias",
        "intro": r"$x^{3}\cdot x^{4}$. Las dos llegan al mismo sitio; una sabe por qué.",
        "methods": [
            {
                "label": "Método 1 · Aplicar la regla",
                "steps": [
                    r"x^{3}\cdot x^{4}",
                    r"3+4=7",
                    r"x^{7}",
                ],
                "note": "Inmediato, siempre que hayas recordado bien cuál de las dos reglas era.",
            },
            {
                "label": "Método 2 · Desplegar y contar",
                "steps": [
                    r"(x\,x\,x)(x\,x\,x\,x)",
                    r"x\,x\,x\,x\,x\,x\,x",
                    r"x^{7}",
                ],
                "note": "Más largo de escribir, pero no hay nada que recordar mal.",
            },
        ],
        "question": r"¿Cuál de los dos te avisa de que $(x^{3})^{4}$ NO es $x^{7}$?",
        "insight": (
            "El segundo. Desplegar (x³)⁴ da cuatro grupos de tres factores, doce en total, "
            "y el error se ve antes de cometerlo. El primero no avisa de nada: si has "
            "guardado la regla equivocada, la aplica igual de rápido. Por eso conviene "
            "desplegar mientras la mano no lo tenga automático — y volver a desplegar el "
            "día que dudes, en vez de escoger la regla que suene mejor."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuánto es $(3x^{2})(4x^{3})$?",
            "options": [
                {"id": "ok", "text": r"$12x^{5}$", "latex": r"12x^{5}"},
                {"id": "trap", "text": r"$12x^{6}$", "latex": r"12x^{6}"},
                {"id": "sumcoef", "text": r"$7x^{5}$", "latex": r"7x^{5}"},
                {"id": "keep", "text": r"$12x^{3}$", "latex": r"12x^{3}"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "trap": "fb_o03_e1_trap",
                "sumcoef": "fb_o03_e1_sumcoef",
                "keep": "fb_o03_e1_keep",
            },
            "misconception_by_option": {
                "trap": "multiplica_los_exponentes_al_multiplicar",
                "sumcoef": "suma_los_coeficientes_al_multiplicar",
                "keep": "se_queda_el_mayor_exponente",
            },
            "hints": {
                "n1": "Lleva dos cuentas separadas: coeficientes y exponentes.",
                "n2": "Los coeficientes se multiplican: 3 · 4.",
                "n3": "Los exponentes se suman: 2 + 3.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Reparte el factor en $6(2f+5)$ y escribe el resultado. No dejes espacios."
            ),
            "answer": "12f+30",
            "accepted": ["30+12f"],
            "hints": {
                "n1": "El 6 multiplica a los dos términos.",
                "n2": "6 · 2f = 12f.",
                "n3": "6 · 5 = 30.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Cada hilada lleva $2s$ sillares y hay $4s$ hiladas. Con $s=3$, ¿cuántos "
                "sillares hacen falta en total?"
            ),
            "expr": r"(2s)(4s)=8s^{2},\quad s=3",
            "answer": "72",
            "hints": {
                "n1": "Primero el monomio: 2 · 4 = 8 y s · s = s².",
                "n2": "Queda 8s².",
                "n3": "8 · 9 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un tallador escribe $(2x)(5x^{4})=10x^{4}$. ¿Dónde está el error?"
            ),
            "options": [
                {"id": "exp", "text": r"Olvidó que $x$ es $x^{1}$: el exponente es $1+4=5$"},
                {"id": "coef", "text": "Multiplicó mal los coeficientes"},
                {"id": "mult", "text": r"Debió multiplicar los exponentes: $x^{4}$"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "exp",
            "feedback_by_option": {
                "exp": "correct",
                "coef": "fb_o03_e4_coef",
                "mult": "fb_o03_e4_mult",
                "none": "fb_o03_e4_none",
            },
            "misconception_by_option": {
                "coef": "suma_los_coeficientes_al_multiplicar",
                "mult": "multiplica_los_exponentes_al_multiplicar",
                "none": "olvida_el_exponente_invisible",
            },
            "hints": {
                "n1": "Los coeficientes están bien: 2 · 5 = 10.",
                "n2": "¿Qué exponente tiene una x escrita sola?",
                "n3": "Despliega: (x)(x·x·x·x) son cinco factores.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Al multiplicar dos potencias de la misma letra, los "
                "exponentes se multiplican.»"
            ),
            "options": [
                {"id": "false", "text": r"Falsa: se suman — $x^{2}\cdot x^{3}=x^{5}$, no $x^{6}$"},
                {"id": "true", "text": "Verdadera: si las potencias se multiplican, sus exponentes también"},
                {"id": "true_same", "text": "Verdadera cuando los dos exponentes son iguales"},
                {"id": "false_never", "text": "Falsa: los exponentes nunca se multiplican en ningún caso"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_o03_e5_trap",
                "true_same": "fb_o03_e5_same",
                "false_never": "fb_o03_e5_never",
            },
            "misconception_by_option": {
                "true": "multiplica_los_exponentes_al_multiplicar",
                "true_same": "multiplica_los_exponentes_al_multiplicar",
                "false_never": "sobregeneraliza_producto_de_monomios",
            },
            "hints": {
                "n1": "Despliega x² · x³ y cuenta las x.",
                "n2": "Son cinco factores, no seis.",
                "n3": "Multiplicar exponentes es lo de (x²)³, que es otra cosa.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": r"Selecciona TODAS las igualdades verdaderas.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$x^{4}\cdot x^{2}=x^{6}$", "latex": r"x^{4}\cdot x^{2}=x^{6}"},
                {"id": "b", "text": r"$x^{4}\cdot x^{2}=x^{8}$", "latex": r"x^{4}\cdot x^{2}=x^{8}"},
                {"id": "c", "text": r"$(x^{4})^{2}=x^{8}$", "latex": r"(x^{4})^{2}=x^{8}"},
                {"id": "d", "text": r"$x^{4}+x^{2}=x^{6}$", "latex": r"x^{4}+x^{2}=x^{6}"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Mira si la operación de fuera es un producto, una potencia o una suma.",
                "n2": "Producto de potencias: se suman. Potencia de potencia: se multiplican.",
                "n3": "En una SUMA no se toca ningún exponente.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                r"El taller marca $3(2f+7)$ trazos por plantilla y hay $2f$ plantillas. "
                r"Con $f=1$, ¿cuántos trazos se marcan en total?"
            ),
            "expr": r"2f\cdot 3(2f+7),\quad f=1",
            "answer": "54",
            "hints": {
                "n1": "Primero reparte el 3: 6f + 21.",
                "n2": "Con f = 1 son 27 trazos por plantilla.",
                "n3": "Y hay 2 plantillas: 2 · 27 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se suman los exponentes?",
        "title": "Cada operación lleva su propia cuenta",
        "intro": (
            "«Se suman» no es la regla de los exponentes: es la regla de UNA operación. "
            "Fíjate en qué está pasando por fuera antes de tocar nada."
        ),
        "rows": [
            {"symbol": r"x^{2}\cdot x^{3}", "name": "Producto de potencias", "closed": "yes",
             "latex": r"x^{2}\cdot x^{3}=x^{5}",
             "note": "Se juntan los factores de las dos: 2 + 3. Es el caso focal."},
            {"symbol": r"x\cdot x^{4}", "name": "Con exponente invisible", "closed": "yes",
             "latex": r"x^{1}\cdot x^{4}=x^{5}",
             "note": "Una letra sola es elevada a 1. El mismo caso, con un 1 que no se escribe."},
            {"symbol": r"(3x^{2})(4x^{3})", "name": "Con coeficientes", "closed": "partial",
             "latex": r"12x^{5}",
             "note": "Los exponentes sí se suman, pero los coeficientes NO: esos se multiplican. Dos cuentas a la vez."},
            {"symbol": r"x^{2}\cdot y^{3}", "name": "Letras distintas", "closed": "no",
             "latex": r"x^{2}y^{3}",
             "note": "No hay exponentes que sumar: cada letra lleva su cuenta y el producto se deja indicado."},
            {"symbol": r"(x^{2})^{3}", "name": "Potencia de una potencia", "closed": "no",
             "latex": r"(x^{2})^{3}=x^{6}",
             "note": "Aquí se MULTIPLICAN: se repite tres veces un grupo de dos factores."},
            {"symbol": r"x^{2}+x^{3}", "name": "Suma de potencias", "closed": "no",
             "latex": r"x^{2}+x^{3}",
             "note": "No se toca ningún exponente. No son semejantes, así que la suma se queda indicada."},
        ],
        "outro": (
            "La tercera fila es la que más se cobra en los exámenes: en un mismo monomio "
            "conviven dos cuentas distintas, y la mano tiende a aplicarle a los "
            "coeficientes lo que acaba de hacer con los exponentes. La última recuerda que "
            "una suma no es un producto — 3x² y 4x³ ni se suman ni se juntan."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres pedidos trabajados en este nodo?",
        "thumbnails": [r"4(2f+3)", r"(3s)(5s^{2})", r"x^{2}\cdot x^{3}"],
        "options": [
            {"id": "count", "text": "En los tres el resultado se puede comprobar desplegando y contando", "correct": True},
            {"id": "two_books", "text": "En los tres hay que llevar por separado la cuenta de los números y la de las letras", "correct": True},
            {"id": "same_rule", "text": "En los tres se aplica la misma cuenta a los coeficientes y a los exponentes", "correct": False},
            {"id": "always_add", "text": "En los tres los exponentes siempre se suman", "correct": False},
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Pedido de cierre del taller: cada hilada lleva 2h² sillares y hay que levantar "
            "3h hiladas, donde h es la altura del muro en codos. El muro de hoy tiene 2 "
            "codos. ¿Cuántos sillares hay que tallar?"
        ),
        "polya": {
            "comprender": "Se multiplican dos monomios: sillares por hilada y número de hiladas.",
            "planear": "Coeficientes por un lado (2 · 3) y exponentes por otro (h² · h¹). Después sustituyo.",
            "ejecutar": "2 · 3 = 6, y 2 + 1 = 3, así que son 6h³. Con h = 2: 6 · 8 = 48.",
            "comprobar": "Despliego: por hilada 2 · 4 = 8 sillares, y hay 3 · 2 = 6 hiladas → 48 ✓.",
        },
        "prompt": "¿Cuántos sillares hay que tallar?",
        "answer": "48",
        "hints": {
            "n1": "Multiplica coeficientes y suma exponentes.",
            "n2": "Queda 6h³.",
            "n3": "6 · 2³ = 6 · 8 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otras piezas. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya distingues el producto de potencias de la potencia de una potencia.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el despliegue: "
            "escribir la letra tantas veces como diga el exponente y contar."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 3³?",
                "answer": "27",
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuánto es 6 · (4 + 2)?",
                "answer": "36",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿A qué equivale $y^{4}\cdot y^{2}$?",
                "options": [
                    {"id": "six", "text": r"$y^{6}$", "latex": r"y^{6}"},
                    {"id": "eight", "text": r"$y^{8}$", "latex": r"y^{8}"},
                    {"id": "two", "text": r"$2y^{6}$", "latex": r"2y^{6}"},
                ],
                "expected": "six",
                "misconception_by_option": {
                    "eight": "multiplica_los_exponentes_al_multiplicar",
                    "two": "suma_las_bases_al_multiplicar",
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
        "default": "Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra.",
        "fb_o03_e1_trap": (
            "Multiplicaste los exponentes. → Despliega: (x·x)(x·x·x) son cinco factores, no seis."
        ),
        "fb_o03_e1_sumcoef": (
            "Sumaste los coeficientes en vez de multiplicarlos. → Los exponentes se suman; "
            "los coeficientes, no."
        ),
        "fb_o03_e1_keep": (
            "Ahí se quedó el exponente mayor y se perdieron dos factores. → Hay que sumarlos."
        ),
        "fb_o03_e4_coef": "2 · 5 = 10 está bien. → El fallo está en el exponente de la x.",
        "fb_o03_e4_mult": (
            "Multiplicar exponentes es la regla de (x²)³, no la de un producto. → Aquí se suman."
        ),
        "fb_o03_e4_none": (
            "Una x sola no tiene exponente 0 ni ninguno: tiene exponente 1. → 1 + 4 = 5."
        ),
        "fb_o03_e5_trap": (
            "Que las potencias se multipliquen no obliga a los exponentes a hacer lo mismo. "
            "→ Cuenta los factores desplegados."
        ),
        "fb_o03_e5_same": (
            "Con exponentes iguales también se suman: x²·x² es x⁴, no x⁴ por casualidad "
            "sino porque 2 + 2 = 4. → Prueba con x³·x³: son 6, no 9."
        ),
        "fb_o03_e5_never": (
            "Te pasaste al otro extremo: en (x²)³ sí se multiplican. → Depende de la "
            "operación de fuera."
        ),
    },
    "closing": (
        "Ya sabes repartir un factor y multiplicar monomios sin que el pedido se dispare. "
        "Falta el camino contrario: cuando lo que hay es un reparto y las letras se van "
        "cancelando. Eso se lleva en la caseta del capataz."
    ),
    "validation_status": "F5_O03_11bloques",
}
