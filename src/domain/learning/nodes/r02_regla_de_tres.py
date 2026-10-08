"""R02 · El tinte de lino — la regla de tres multiplica en diagonal.

Segunda sala del taller del canon. Guía: Iuty. Vocabulario propio: tina de
tinte, lino, brazada, madeja, tintorero. Nada de cuadrículas ni bocetos (R01),
pan de oro (R03) ni lámparas (R04).

Error focal: montar la regla de tres con la razón del revés, multiplicando los
dos datos que están en la misma fila en vez de los de la diagonal.
"""

NODE_ID = "ALG-N1-R02-REGLA-DE-TRES"
CONCEPT_SLUG = "regla_de_tres"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "regla_de_tres",
    "misconception": "invierte_la_razon_en_la_regla_de_tres",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El tinte de lino · Regla de tres",
    "house": "El tinte de lino",
    "guide": "Iuty",
    "finish_label": "Pasar al pan de oro",
    "title": "Tres datos conocidos y uno que se deduce",
    "intro": (
        "En la cuadrícula viste que escalar es multiplicar. Aquí se usa para lo que hace "
        "falta a diario: se conocen tres cantidades de una proporción y hay que sacar la "
        "cuarta. La cuenta es corta, y hay una manera de montarla que sale al revés."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de acercarse a la tina. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Si 2 medidas de tinte tiñen 8 brazadas de lino, ¿cuántas brazadas tiñe 1 medida?",
                "answer": "4",
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Si 3 medidas tiñen 12 brazadas, ¿cuántas brazadas tiñen 6 medidas?",
                "answer": "24",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si hay que teñir MÁS lino, ¿qué pasa con el tinte que hace falta?",
                "options": [
                    {"id": "more", "text": "Hace falta más tinte"},
                    {"id": "less", "text": "Hace falta menos tinte"},
                    {"id": "same", "text": "Hace falta el mismo"},
                ],
                "expected": "more",
                "misconception_by_option": {
                    "less": "toda_relacion_es_inversa",
                    "same": "ignora_la_proporcionalidad",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/r02-regla-de-tres-katia.png",
        "eyebrow": "KatIA · Junto a la tina de tinte",
        "title": "Las brazadas que salieron descoloridas",
        "body": (
            "En la tina se tiñe el lino que después llevará el pigmento del muro. Iuty "
            "tiene la receta anotada:\n\n"
            "«Tres medidas de tinte por cada doce brazadas de lino. Hoy hay veinte "
            "brazadas.»\n\n"
            "«El tintorero de ayer montó la cuenta con los tres números y multiplicó los "
            "dos que tenía delante en la misma línea. Le salió menos de dos medidas para "
            "más lino del habitual.»\n\n"
            "Iuty señala unas madejas apagadas colgando del techo.\n\n"
            "«Las últimas seis brazadas salieron de ese color. Y el tinte no se puede "
            "volver a dar.»"
        ),
        "question": "Con tres datos de una proporción, ¿qué dos hay que multiplicar para sacar el cuarto?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Los dos que están en la misma fila"},
                {
                    "id": "b",
                    "text": "Los dos que están en diagonal, y se divide entre el que queda",
                },
                {"id": "c", "text": "Los dos mayores, y se divide entre el menor"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decir de antemano si la cuarta "
                "cantidad tiene que salir mayor o menor, y usar eso para descartar el error."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El camino largo y el atajo dan el mismo número",
        "body": "La regla de tres no es una fórmula caída del cielo: es el camino largo abreviado.",
        "cases": [
            {
                "label": "Camino largo",
                "context": "Bajar a una brazada y volver a subir",
                "fraction": r"12\ \text{brazadas}\to 3\ \text{medidas}",
                "division": r"1\to\tfrac{3}{12}=\tfrac14;\quad 20\to 20\cdot\tfrac14=5",
                "note": "Primero cuánto tinte lleva UNA brazada, después se multiplica por las que haya.",
            },
            {
                "label": "El atajo",
                "context": "Multiplicar en diagonal y dividir",
                "fraction": r"\dfrac{3}{12}=\dfrac{x}{20}",
                "division": r"x=\dfrac{3\cdot 20}{12}=5",
                "note": "Los mismos tres números, en un solo renglón. El 3 y el 20 están en diagonal.",
            },
        ],
        "resolution": (
            "El atajo funciona porque la razón se conserva: tinte entre lino vale lo mismo "
            "hoy que ayer. De ahí sale la igualdad de dos fracciones, y de ahí que se "
            "multiplique en diagonal. Multiplicar los de la misma fila no responde a "
            "ninguna pregunta: junta tinte con tinte."
        ),
    },
    "definition_title": "Regla de tres directa",
    "definition_katex": r"\dfrac{a}{b}=\dfrac{x}{d}\;\Longrightarrow\; x=\dfrac{a\,d}{b}",
    "definition": (
        "Cuando dos magnitudes son DIRECTAMENTE proporcionales, su razón no cambia. Con "
        "tres datos conocidos se escribe la igualdad de las dos razones y se despeja el "
        "cuarto: se multiplican los dos que están en DIAGONAL con la incógnita y se divide "
        "entre el que queda. La incógnita puede ocupar cualquiera de las cuatro casillas."
    ),
    "definition_symbols": [
        {
            "symbol": r"\dfrac{3}{12}=\dfrac{x}{20}",
            "reads": "la proporción",
            "means": "la razón tinte : lino no cambia",
        },
        {
            "symbol": r"x=\dfrac{3\cdot 20}{12}",
            "reads": "en diagonal",
            "means": "el 3 y el 20 se multiplican; el 12 divide",
        },
        {
            "symbol": r"\dfrac{3}{12}=\dfrac14",
            "reads": "por brazada",
            "means": "el camino largo: cuánto lleva una sola",
        },
        {
            "symbol": r"\dfrac{20}{12}=\dfrac53",
            "reads": "factor de escala",
            "means": "cuántas veces más lino hay hoy",
        },
        {
            "symbol": r"3\cdot\dfrac53=5",
            "reads": "escalar el tinte",
            "means": "el mismo factor se aplica a la otra magnitud",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La receta de la tina",
            "title": "Sacar la cuarta cantidad",
            "statement": (
                "Tres medidas de tinte tiñen 12 brazadas de lino. Hoy hay 20 brazadas. "
                "¿Cuánto tinte hace falta?"
            ),
            "latex": r"\dfrac{3}{12}=\dfrac{x}{20}",
            "image_slot": False,
            "steps": [
                "Escribo las dos razones con las magnitudes en el mismo sitio: tinte arriba, lino abajo.",
                "La incógnita es el tinte de hoy: 3/12 = x/20.",
                "Multiplico en diagonal con la x: 3 · 20 = 60.",
                "Divido entre el que queda: 60 ÷ 12 = 5.",
                "Hacen falta 5 medidas. Hay más lino que ayer, así que tenía que salir más de 3 ✓.",
            ],
            "solution": r"$x=5$ medidas",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué se multiplica el 3 con el 20 y no el 3 con el 12?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Manos en la tina",
            "title": "Cuando la incógnita no está donde la esperabas",
            "statement": (
                "Cinco tintoreros tiñen 30 brazadas en una jornada. Hoy hay 8 tintoreros. "
                "¿Cuántas brazadas se tiñen?"
            ),
            "latex": r"\dfrac{5}{30}=\dfrac{8}{x}",
            "image_slot": False,
            "steps": [
                "Coloco tintoreros arriba y brazadas abajo, en las dos razones.",
                "La incógnita está ahora abajo a la derecha: 5/30 = 8/x.",
                "La diagonal de la x es 30 · 8 = 240.",
                "Divido entre el que queda: 240 ÷ 5 = 48 brazadas.",
                "Compruebo: cada tintorero hace 6 brazadas, y 8 · 6 = 48 ✓.",
            ],
            "solution": r"$x=48$ brazadas",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El tintorero que multiplicó en la misma fila",
            "statement": (
                "Vuelve la receta de la apertura. El tintorero escribió los tres números y "
                "calculó 3 · 12 ÷ 20, y le salieron 1,8 medidas para las 20 brazadas."
            ),
            "latex": r"\dfrac{3}{12}=\dfrac{x}{20}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"x=\dfrac{3\cdot 12}{20}=1{,}8",
            "error_note": (
                "Multiplicó el 3 con el 12, que son la receta de ayer entera, y dividió "
                "entre el dato de hoy. La razón le quedó del revés."
            ),
            "correct_version": {
                "wrong_latex": r"x=\dfrac{3\cdot 12}{20}",
                "right_latex": r"x=\dfrac{3\cdot 20}{12}",
                "rows": [
                    {
                        "wrong": "Se multiplican los dos de la misma fila",
                        "right": "Se multiplican los dos de la diagonal de la incógnita",
                    },
                    {
                        "wrong": r"1{,}8\ \text{medidas para MÁS lino que ayer}",
                        "right": r"5\ \text{medidas: más lino, más tinte ✓}",
                    },
                ],
            },
            "explain_prompt": (
                "Explica por qué el resultado tenía que ser mayor que 3, y usa eso para "
                "descartar 1,8 sin rehacer la cuenta."
            ),
            "steps": [
                "Hoy hay 20 brazadas y ayer eran 12: hay más lino que teñir.",
                "Si hace falta más lino, hace falta más tinte. Cualquier resultado por debajo de 3 delata el error.",
                "Regla para no volver a caer: antes de dividir, di en voz alta si la respuesta debe subir o bajar.",
            ],
            "solution": (
                "Hacen falta 5 medidas. La regla de tres bien montada da un número mayor, "
                "y la mal montada da justo su recíproco escalado — por eso sale ridículo."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La cuenta de la tina va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Si 4 medidas tiñen 20 brazadas, ¿cuántas medidas para 35 brazadas?",
                "given_steps": [r"\dfrac{4}{20}=\dfrac{x}{35}", r"4\cdot 35=140"],
                "blanks": [{"id": "P1-b1", "label": r"140\div 20=", "answer": "7"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Si 6 tintoreros tiñen 42 brazadas, ¿cuántas tiñen 9?",
                "given_steps": [r"\dfrac{6}{42}=\dfrac{9}{x}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"42\cdot 9=", "answer": "378"},
                    {"id": "P2-b2", "label": r"378\div 6=", "answer": "63"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: 5 medidas de tinte tiñen 15 brazadas. ¿Cuántas "
                    "brazadas se tiñen con 12 medidas?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"x=", "answer": "36"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de llegar a la cuarta cantidad",
        "intro": r"7 medidas tiñen 21 brazadas. ¿Cuánto tinte para 30 brazadas?",
        "methods": [
            {
                "label": "Método 1 · Bajar a la unidad",
                "steps": [
                    r"21\ \text{brazadas}\to 7\ \text{medidas}",
                    r"1\to\dfrac{7}{21}=\dfrac13",
                    r"30\cdot\dfrac13=10",
                ],
                "note": "Se entiende paso a paso, pero pasa por una fracción intermedia.",
            },
            {
                "label": "Método 2 · Usar el factor de escala",
                "steps": [
                    r"\dfrac{30}{21}=\dfrac{10}{7}",
                    r"7\cdot\dfrac{10}{7}",
                    r"10",
                ],
                "note": "Se apoya en lo de la cuadrícula: el mismo factor escala las dos magnitudes.",
            },
        ],
        "question": "¿Qué pasa con cada método si los números no dan una unidad cómoda?",
        "insight": (
            "Los dos aguantan, pero el segundo lo dice antes: el factor 30/21 es mayor que "
            "1, así que el tinte tiene que subir, y eso se ve antes de calcular nada. El "
            "primero da la fracción 7/21 y hay que llegar al final para saber si el "
            "resultado creció. Es la misma idea de la cuadrícula: escalar es multiplicar "
            "por un factor, y ese factor es el que avisa de la dirección."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Si 5 medidas de tinte tiñen 20 brazadas, ¿cuántas medidas hacen falta para 28 brazadas?",
            "expr": r"\dfrac{5}{20}=\dfrac{x}{28}",
            "answer": "7",
            "hints": {
                "n1": "Hay más lino que antes: el tinte tiene que subir.",
                "n2": "Multiplica en diagonal: 5 · 28.",
                "n3": "140 ÷ 20 = …",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": (r"Para resolver $\dfrac{4}{9}=\dfrac{x}{27}$, ¿qué operación se hace?"),
            "options": [
                {
                    "id": "ok",
                    "text": r"$x=\dfrac{4\cdot 27}{9}$",
                    "latex": r"x=\dfrac{4\cdot 27}{9}",
                },
                {
                    "id": "row",
                    "text": r"$x=\dfrac{4\cdot 9}{27}$",
                    "latex": r"x=\dfrac{4\cdot 9}{27}",
                },
                {"id": "all", "text": r"$x=4\cdot 9\cdot 27$", "latex": r"x=4\cdot 9\cdot 27"},
                {"id": "sub", "text": r"$x=27-9+4$", "latex": r"x=27-9+4"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "row": "fb_r02_e2_row",
                "all": "fb_r02_e2_all",
                "sub": "fb_r02_e2_sub",
            },
            "misconception_by_option": {
                "row": "invierte_la_razon_en_la_regla_de_tres",
                "all": "ignora_la_proporcionalidad",
                "sub": "escalado_aditivo",
            },
            "hints": {
                "n1": "Localiza la x y mira qué número tiene enfrente en diagonal.",
                "n2": "La diagonal de la x es el 4 y el 27.",
                "n3": "El que queda, el 9, divide.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Si 8 tintoreros tiñen 56 brazadas en una jornada, ¿cuántas tiñen 3 tintoreros?",
            "expr": r"\dfrac{8}{56}=\dfrac{3}{x}",
            "answer": "21",
            "hints": {
                "n1": "Hay menos tintoreros: el resultado tiene que bajar.",
                "n2": "Cada tintorero hace 7 brazadas.",
                "n3": "3 · 7 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un tintorero calcula el tinte para 30 brazadas sabiendo que 6 medidas "
                "tiñen 24, y anota 4,8 medidas. ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "inverted",
                    "text": r"Montó la razón del revés: son $\dfrac{6\cdot 30}{24}=7{,}5$",
                },
                {"id": "div", "text": "Dividió cuando tenía que restar"},
                {"id": "unit", "text": "Calculó mal cuánto tiñe una medida"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "inverted",
            "feedback_by_option": {
                "inverted": "correct",
                "div": "fb_r02_e4_div",
                "unit": "fb_r02_e4_unit",
                "none": "fb_r02_e4_none",
            },
            "misconception_by_option": {
                "div": "escalado_aditivo",
                "unit": "ignora_la_proporcionalidad",
                "none": "invierte_la_razon_en_la_regla_de_tres",
            },
            "hints": {
                "n1": "30 brazadas son más que 24.",
                "n2": "Con más lino hace falta más tinte que 6 medidas.",
                "n3": "4,8 es menos que 6: imposible.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «En una regla de tres se multiplican los dos números "
                "que están en la misma fila y se divide entre el tercero.»"
            ),
            "options": [
                {"id": "false", "text": "Falsa: se multiplican los de la diagonal de la incógnita"},
                {"id": "true", "text": "Verdadera: son los dos que se conocen juntos"},
                {"id": "true_order", "text": "Verdadera si se escriben en el orden correcto"},
                {"id": "false_none", "text": "Falsa: en una regla de tres no se multiplica nada"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_r02_e5_trap",
                "true_order": "fb_r02_e5_order",
                "false_none": "fb_r02_e5_none",
            },
            "misconception_by_option": {
                "true": "invierte_la_razon_en_la_regla_de_tres",
                "true_order": "invierte_la_razon_en_la_regla_de_tres",
                "false_none": "sobregeneraliza_regla_de_tres",
            },
            "hints": {
                "n1": "Prueba con 3/12 = x/20 de las dos maneras.",
                "n2": "En diagonal da 5; en la misma fila da 1,8.",
                "n3": "Solo una sube cuando el lino sube.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (
                "Selecciona TODAS las situaciones que se resuelven con una regla de tres "
                "DIRECTA."
            ),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": "Medidas de tinte y brazadas teñidas"},
                {"id": "b", "text": "Número de tintoreros y días que tardan en la misma tarea"},
                {"id": "c", "text": "Brazadas de lino y su precio en grano"},
                {"id": "d", "text": "La edad del tintorero y las brazadas de la tina"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Directa significa que las dos suben a la vez.",
                "n2": "Más tintoreros para la MISMA tarea son menos días, no más.",
                "n3": "Y hay pares de cantidades que no tienen ninguna relación.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "La receta dice 7 medidas de tinte por 21 brazadas. Iuty encarga teñir 45 "
                "brazadas, pero en la tina solo caben 15 brazadas por tanda. ¿Cuántas "
                "medidas de tinte se gastan en total?"
            ),
            "expr": r"\dfrac{7}{21}=\dfrac{x}{45}",
            "answer": "15",
            "hints": {
                "n1": "El tamaño de la tanda no cambia el total de tinte.",
                "n2": "Cada brazada lleva 7/21 = 1/3 de medida.",
                "n3": "45 · 1/3 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se resuelve con regla de tres directa?",
        "title": "Cuándo sirve el atajo y cuándo miente",
        "intro": (
            "La regla de tres es rápida y no comprueba nada por su cuenta. Antes de "
            "aplicarla hay que saber si las dos cantidades suben juntas."
        ),
        "rows": [
            {
                "symbol": r"\dfrac{3}{12}=\dfrac{x}{20}",
                "name": "Tinte y lino",
                "closed": "yes",
                "latex": r"x=5",
                "note": "Más lino, más tinte. La diagonal de la x da el resultado. Es el caso focal.",
            },
            {
                "symbol": r"\dfrac{5}{30}=\dfrac{8}{x}",
                "name": "La incógnita abajo",
                "closed": "yes",
                "latex": r"x=48",
                "note": "La posición de la x no cambia nada: siempre se multiplica su diagonal.",
            },
            {
                "symbol": r"\dfrac{7}{21}=\dfrac{x}{30}",
                "name": "Sin unidad cómoda",
                "closed": "partial",
                "latex": r"x=10",
                "note": "Se resuelve igual, pero bajar a la unidad deja 1/3 por medio. Ahí conviene el factor de escala.",
            },
            {
                "symbol": r"0\to 0",
                "name": "La comprobación del cero",
                "closed": "partial",
                "latex": r"0\ \text{medidas}\to 0\ \text{brazadas}",
                "note": "Toda proporcionalidad directa pasa por el cero. Si con 0 de una no sale 0 de la otra, no es directa y el atajo no vale.",
            },
            {
                "symbol": r"5\ \text{tintoreros}\to 6\ \text{días}",
                "name": "Más manos, menos días",
                "closed": "no",
                "latex": r"5\cdot 6=10\cdot 3",
                "note": "Aquí una sube cuando la otra baja. Lo que se conserva es el producto, no la razón. Es la sala de las lámparas.",
            },
            {
                "symbol": r"\text{edad}\ \text{y}\ \text{brazadas}",
                "name": "Sin ninguna relación",
                "closed": "no",
                "latex": r"\text{---}",
                "note": "Que haya tres números no obliga a que exista una cuarta cantidad. A veces no hay proporción que valga.",
            },
        ],
        "outro": (
            "La cuarta fila es la comprobación más barata que existe y casi nadie la hace: "
            "con cero de una magnitud, ¿sale cero de la otra? Si la respuesta es no, la "
            "regla de tres va a devolver un número creíble y equivocado. Y la quinta abre "
            "el caso que sí tiene regla propia: cuando una sube y la otra baja."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten las tres cuentas de la tina trabajadas en este nodo?",
        "thumbnails": [
            r"\dfrac{3}{12}=\dfrac{x}{20}",
            r"\dfrac{5}{30}=\dfrac{8}{x}",
            r"\dfrac{7}{21}=\dfrac{x}{30}",
        ],
        "options": [
            {
                "id": "diagonal",
                "text": "En las tres se multiplica la diagonal de la incógnita y se divide entre el que queda",
                "correct": True,
            },
            {
                "id": "direction",
                "text": "En las tres se puede saber antes de calcular si el resultado sube o baja",
                "correct": True,
            },
            {
                "id": "row",
                "text": "En las tres se multiplican los dos datos que se conocen juntos",
                "correct": False,
            },
            {
                "id": "always",
                "text": "En las tres el atajo sirve porque sirve para cualquier par de magnitudes",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Encargo de cierre de la tina: la receta es 9 medidas de tinte por cada 24 "
            "brazadas de lino. El maestro pide teñir 64 brazadas para el friso del muro. "
            "¿Cuántas medidas de tinte hay que preparar?"
        ),
        "polya": {
            "comprender": "Tinte y lino suben juntos: es proporcionalidad directa, y se conocen tres de las cuatro cantidades.",
            "planear": "Escribo 9/24 = x/64 y multiplico la diagonal de la x, dividiendo entre el que queda.",
            "ejecutar": "9 · 64 = 576, y 576 ÷ 24 = 24 medidas.",
            "comprobar": "64 brazadas son más del doble de 24, y 24 medidas son más del doble de 9 ✓. Montada del revés habría dado 3,375, menos que la receta original.",
        },
        "prompt": "¿Cuántas medidas de tinte hay que preparar?",
        "answer": "24",
        "hints": {
            "n1": "Hay más lino que en la receta: el tinte tiene que subir.",
            "n2": "Multiplica 9 · 64.",
            "n3": "576 ÷ 24 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otra receta. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya multiplicas en diagonal y compruebas la dirección del resultado.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el camino largo: "
            "cuánto tinte lleva UNA brazada."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Si 3 medidas de tinte tiñen 15 brazadas, ¿cuántas brazadas tiñe 1 medida?",
                "answer": "5",
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Si 4 medidas tiñen 20 brazadas, ¿cuántas brazadas tiñen 8 medidas?",
                "answer": "40",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si hay que teñir MENOS lino, ¿qué pasa con el tinte necesario?",
                "options": [
                    {"id": "less", "text": "Hace falta menos tinte"},
                    {"id": "more", "text": "Hace falta más tinte"},
                    {"id": "same", "text": "Hace falta el mismo"},
                ],
                "expected": "less",
                "misconception_by_option": {
                    "more": "toda_relacion_es_inversa",
                    "same": "ignora_la_proporcionalidad",
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
        "default": "Antes de dividir, di si la respuesta debe subir o bajar: eso descarta la mitad de los errores.",
        "fb_r02_e2_row": (
            "Esos dos están en la misma fila. → La diagonal de la x es la que se multiplica."
        ),
        "fb_r02_e2_all": ("No se multiplican los tres. → Dos se multiplican y el tercero divide."),
        "fb_r02_e2_sub": (
            "Escalar no es sumar ni restar, es multiplicar. → Eso ya se vio en la cuadrícula."
        ),
        "fb_r02_e4_div": "La división estaba bien planteada. → Lo que estaba del revés era la razón.",
        "fb_r02_e4_unit": (
            "Una medida tiñe 4 brazadas y eso es correcto. → El fallo está en cómo montó la cuenta."
        ),
        "fb_r02_e4_none": (
            "4,8 es menos tinte que las 6 de la receta, y hoy hay más lino. → Imposible."
        ),
        "fb_r02_e5_trap": (
            "Que se conozcan juntos no los pone en la misma operación. → Se multiplica en diagonal."
        ),
        "fb_r02_e5_order": (
            "El orden en que escribas las razones no salva la cuenta. → Lo que decide es "
            "dónde está la incógnita."
        ),
        "fb_r02_e5_none": (
            "Te pasaste al otro extremo: sí se multiplica. → Lo que hay que acertar es qué par."
        ),
    },
    "closing": (
        "La tina ya se prepara con el tinte justo y el lino sale del mismo color hasta la "
        "última brazada. Iuty sube al pan de oro, donde las cantidades no se dan en "
        "medidas sino en partes de cien — y donde subir y bajar lo mismo no devuelve al "
        "punto de partida."
    ),
    "validation_status": "F5_R02_11bloques",
}
