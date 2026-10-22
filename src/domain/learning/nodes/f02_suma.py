"""F02 · El canal madre — el denominador nombra la parte, no se suma.

Segunda sala de los campos tras la crecida. Guía: Tabiry. Vocabulario propio:
canal madre, acequia, ramal, caudal, azud, turno de riego. Nada de parcelas ni
linderos (F01), eras ni gavillas (F03), ni simiente (F04).

Error focal: sumar numeradores con numeradores y denominadores con denominadores.
El denominador dice EN CUÁNTAS partes está repartido el caudal; juntar dos partes
no parte el canal en más trozos.
"""

NODE_ID = "ALG-N1-F02-SUMA"
CONCEPT_SLUG = "suma_de_fracciones_algebraicas"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "suma_de_fracciones_algebraicas",
    "misconception": "suma_numeradores_y_denominadores",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El canal madre · Suma de fracciones",
    "house": "El canal madre",
    "guide": "Tabiry",
    "finish_label": "Subir a la era de trilla",
    "title": "El denominador nombra la parte, no se suma",
    "intro": (
        "En la parcela partida aprendiste cuándo se puede tachar. Aquí llegan dos ramales "
        "que riegan lo mismo y hay que anotar cuánto agua es en total. La cuenta parece "
        "obvia y hay una manera de hacerla que encoge el caudal."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el azud. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $\dfrac{2}{7}+\dfrac{3}{7}$?",
                "options": [
                    {"id": "five7", "text": r"$\dfrac{5}{7}$", "latex": r"\dfrac{5}{7}"},
                    {"id": "five14", "text": r"$\dfrac{5}{14}$", "latex": r"\dfrac{5}{14}"},
                    {"id": "six7", "text": r"$\dfrac{6}{7}$", "latex": r"\dfrac{6}{7}"},
                ],
                "expected": "five7",
                "misconception_by_option": {
                    "five14": "suma_numeradores_y_denominadores",
                    "six7": "multiplica_en_vez_de_sumar",
                },
            },
            {
                "id": "D2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": (
                    "Un ramal lleva 3 partes de un caudal dividido en 8, y otro lleva 2 de "
                    "esas mismas partes. ¿Cuántas partes de 8 llevan entre los dos?"
                ),
                "answer": "5",
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Se pueden sumar $\dfrac{1}{2}$ y $\dfrac{1}{3}$ sumando los numeradores?",
                "options": [
                    {"id": "no", "text": "No: las partes no son del mismo tamaño"},
                    {"id": "yes", "text": r"Sí: da $\dfrac{2}{5}$"},
                    {"id": "yes_big", "text": "Sí, si el resultado se simplifica después"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "suma_numeradores_y_denominadores",
                    "yes_big": "suma_numeradores_y_denominadores",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/f02-suma-katia.png",
        "eyebrow": "KatIA · Junto al canal madre",
        "title": "El caudal que menguaba al sumarlo",
        "body": (
            "El canal madre baja del río y se reparte en ramales. Tabiry lleva la cuenta "
            "de qué parte del caudal toma cada acequia en su turno de riego.\n\n"
            "«La acequia del norte toma dos quintos y la del este, un quinto. El escriba "
            "sumó arriba y sumó abajo: tres décimos. Según su tablilla, juntar dos aguas "
            "deja menos agua que la que traía la del norte sola.»\n\n"
            "Tabiry hunde la mano en el canal.\n\n"
            "«El agua no sabe leer. Lo que menguó fue el registro.»"
        ),
        "question": "Al juntar dos partes de un mismo reparto, ¿qué pasa con el número de abajo?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Se suma también, como el de arriba"},
                {"id": "b", "text": "Se queda igual: sigue siendo el mismo reparto"},
                {"id": "c", "text": "Se multiplica por dos, porque ahora hay dos fracciones"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder explicar por qué el número de "
                "abajo no es una cantidad que se sume, sino el nombre del trozo."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Los dos números de una fracción no hacen el mismo trabajo",
        "body": "Uno cuenta trozos. El otro dice de qué tamaño son. Solo se suma el que cuenta.",
        "cases": [
            {
                "label": "Mismo reparto",
                "context": "Dos quintos del caudal más un quinto del caudal",
                "fraction": r"\dfrac{2}{5}+\dfrac{1}{5}",
                "division": r"\dfrac{3}{5}",
                "note": "Tres trozos de los mismos quintos. El canal sigue partido en cinco: el 5 no se toca.",
            },
            {
                "label": "Repartos distintos",
                "context": "Medio caudal más un tercio del caudal",
                "fraction": r"\dfrac{1}{2}+\dfrac{1}{3}",
                "division": r"\dfrac{3}{6}+\dfrac{2}{6}=\dfrac{5}{6}",
                "note": "Los trozos no son del mismo tamaño: primero hay que repartir todo en sextos.",
            },
        ],
        "resolution": (
            "El numerador CUENTA trozos y el denominador los NOMBRA. Sumar cuenta trozos, "
            "así que solo se suman los de arriba. Si los trozos no son del mismo tamaño no "
            "se pueden contar juntos, igual que en la rampa no se juntaban cuerdas con "
            "herramientas: primero hay que llevarlos a un reparto común."
        ),
    },
    "definition_title": "Suma y resta de fracciones algebraicas",
    "definition_katex": r"\dfrac{a}{c}+\dfrac{b}{c}=\dfrac{a+b}{c}",
    "definition": (
        "Con el MISMO denominador, se suman o restan los numeradores y el denominador se "
        "copia sin tocarlo. Con denominadores DISTINTOS hay que llevar las dos fracciones a "
        "un denominador común antes de sumar: se multiplica cada fracción arriba y abajo "
        "por lo que le falte. El resultado puede quedar todavía simplificable."
    ),
    "definition_symbols": [
        {
            "symbol": r"\dfrac{3}{x}+\dfrac{2}{x}=\dfrac{5}{x}",
            "reads": "mismo denominador",
            "means": "se suman los de arriba y el de abajo se copia",
        },
        {
            "symbol": r"\dfrac{5c}{6}-\dfrac{c}{6}=\dfrac{4c}{6}",
            "reads": "la resta va igual",
            "means": "5c − c = 4c, y el 6 se queda",
        },
        {
            "symbol": r"\dfrac{4c}{6}=\dfrac{2c}{3}",
            "reads": "aún se simplifica",
            "means": "sumar no exime de revisar el resultado",
        },
        {
            "symbol": r"\dfrac{1}{2}+\dfrac{1}{3}=\dfrac{3+2}{6}",
            "reads": "denominador común",
            "means": "primero al mismo reparto, después se suma",
        },
        {
            "symbol": r"\dfrac{1}{x}+\dfrac{1}{y}=\dfrac{y+x}{xy}",
            "reads": "con letras",
            "means": "el común denominador puede ser un producto de letras",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Dos ramales, un turno",
            "title": "Mismo denominador",
            "statement": (
                "Dos acequias riegan la misma tabla. La primera toma 3 partes de un caudal "
                "repartido en x turnos y la segunda, 2 de esas partes. ¿Cuánto toman entre "
                "las dos?"
            ),
            "latex": r"\dfrac{3}{x}+\dfrac{2}{x}",
            "image_slot": False,
            "steps": [
                "Las dos fracciones cuentan trozos del MISMO reparto: los dos denominadores son x.",
                "Sumo los trozos: 3 + 2 = 5.",
                "El reparto no cambia por juntarlos: sigue habiendo x turnos.",
                "Queda 5/x.",
                "Compruebo con x = 10: 0,3 + 0,2 = 0,5, y 5/10 = 0,5 ✓.",
            ],
            "solution": r"$\dfrac{3}{x}+\dfrac{2}{x}=\dfrac{5}{x}$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "¿Por qué el denominador no cambia si estamos juntando dos cosas?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El azud que se cierra a medias",
            "title": "Restar y revisar el resultado",
            "statement": (
                "Una acequia llevaba 5c partes de un caudal dividido en 6 y se le cierra el "
                "azud hasta dejarle c partes menos. ¿Qué parte del caudal le queda?"
            ),
            "latex": r"\dfrac{5c}{6}-\dfrac{c}{6}",
            "image_slot": False,
            "steps": [
                "Mismo denominador: resto los numeradores. 5c − c = 4c.",
                "El 6 se copia: queda 4c/6.",
                "No he terminado: 4 y 6 tienen un factor común, el 2.",
                "Simplifico dividiendo arriba y abajo entre 2: 2c/3.",
                "Compruebo con c = 3: 15/6 − 3/6 = 2, y 2 · 3/3 = 2 ✓.",
            ],
            "solution": r"$\dfrac{5c}{6}-\dfrac{c}{6}=\dfrac{2c}{3}$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que sumó abajo",
            "statement": (
                "Vuelve el registro de la apertura: dos quintos del caudal y un quinto más. "
                "El escriba anotó tres décimos, y con las letras haría lo mismo: 3/x + 2/x = 5/2x."
            ),
            "latex": r"\dfrac{2}{5}+\dfrac{1}{5}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\dfrac{2}{5}+\dfrac{1}{5}=\dfrac{3}{10}",
            "error_note": (
                "Trató el denominador como una cantidad más que sumar. Pero el 5 no es agua: "
                "dice en cuántos trozos está partida, y juntarlos no parte el canal otra vez."
            ),
            "correct_version": {
                "wrong_latex": r"\dfrac{2}{5}+\dfrac{1}{5}=\dfrac{2+1}{5+5}",
                "right_latex": r"\dfrac{2}{5}+\dfrac{1}{5}=\dfrac{2+1}{5}=\dfrac{3}{5}",
                "rows": [
                    {
                        "wrong": "Los cuatro números entran en la suma",
                        "right": "Solo entran los de arriba: los de abajo nombran el trozo",
                    },
                    {
                        "wrong": r"\dfrac{3}{10}\ \text{es menos que}\ \dfrac{2}{5}",
                        "right": r"\dfrac{3}{5}\ \text{es más que}\ \dfrac{2}{5}\ \text{✓}",
                    },
                ],
            },
            "explain_prompt": (
                "Explica por qué el resultado tiene que ser MAYOR que cada sumando, y usa "
                "eso para descartar tres décimos sin hacer la cuenta."
            ),
            "steps": [
                "Junto agua con agua: el resultado no puede ser menor que lo que ya traía un ramal.",
                "Dos quintos son 0,4 y tres décimos son 0,3. El registro decía que juntar agua quita agua.",
                "Regla para no volver a caer: antes de sumar, mira si los denominadores ya son iguales; si lo son, no los toques.",
            ],
            "solution": (
                "2/5 + 1/5 = 3/5, y 3/x + 2/x = 5/x. El número de abajo se copia: no es un "
                "sumando, es el nombre del trozo."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El registro del turno va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Suma $\dfrac{4}{9}+\dfrac{2}{9}$ y di cuánto vale el numerador.",
                "given_steps": [r"\dfrac{4+2}{9}"],
                "blanks": [{"id": "P1-b1", "label": r"4+2=", "answer": "6"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Suma $\dfrac{1}{4}+\dfrac{1}{6}$ llevándolas a doceavos.",
                "given_steps": [r"\dfrac{3}{12}+\dfrac{2}{12}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"3+2=", "answer": "5"},
                    {"id": "P2-b2", "label": r"\text{denominador}=", "answer": "12"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $\dfrac{7c}{10}-\dfrac{2c}{10}$ con $c=4$. "
                    "Primero la fracción, después el valor."
                ),
                "given_steps": [],
                "blanks": [
                    {
                        "id": "P3-b1",
                        "label": r"\dfrac{5c}{10}=\dfrac{c}{2}\ \text{con}\ c=4:",
                        "answer": "2",
                    }
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de encontrar el denominador común",
        "intro": r"$\dfrac{1}{4}+\dfrac{1}{6}$. Los dos caminos llegan a la misma agua.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar los denominadores",
                "steps": [
                    r"4\cdot 6=24",
                    r"\dfrac{6}{24}+\dfrac{4}{24}=\dfrac{10}{24}",
                    r"\dfrac{10}{24}=\dfrac{5}{12}",
                ],
                "note": "Nunca falla, pero deja números grandes y obliga a simplificar al final.",
            },
            {
                "label": "Método 2 · Buscar el mínimo común múltiplo",
                "steps": [
                    r"\mathrm{mcm}(4,6)=12",
                    r"\dfrac{3}{12}+\dfrac{2}{12}",
                    r"\dfrac{5}{12}",
                ],
                "note": "Números más pequeños y resultado ya simplificado, si sabes hallar el mcm.",
            },
        ],
        "question": "¿En qué se nota la diferencia con denominadores como 8 y 12?",
        "insight": (
            "Multiplicar daría 96 y el mcm es 24: cuatro veces menos. Los dos métodos son "
            "correctos, y el primero es el que conviene cuando dudas — vale más una cuenta "
            "grande bien hecha que un mcm inventado. Esto es exactamente el mcm que "
            "aprendiste en Esparta: no era un ejercicio suelto, era la herramienta para "
            "poder sumar estas fracciones sin números enormes."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuánto es $\dfrac{4}{y}+\dfrac{3}{y}$?",
            "options": [
                {"id": "ok", "text": r"$\dfrac{7}{y}$", "latex": r"\dfrac{7}{y}"},
                {"id": "trap", "text": r"$\dfrac{7}{2y}$", "latex": r"\dfrac{7}{2y}"},
                {"id": "sq", "text": r"$\dfrac{7}{y^{2}}$", "latex": r"\dfrac{7}{y^{2}}"},
                {"id": "twelve", "text": r"$\dfrac{12}{y}$", "latex": r"\dfrac{12}{y}"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "trap": "fb_f02_e1_trap",
                "sq": "fb_f02_e1_sq",
                "twelve": "fb_f02_e1_mult",
            },
            "misconception_by_option": {
                "trap": "suma_numeradores_y_denominadores",
                "sq": "suma_numeradores_y_denominadores",
                "twelve": "multiplica_en_vez_de_sumar",
            },
            "hints": {
                "n1": "¿Son iguales los dos denominadores?",
                "n2": "Si lo son, solo se suman los de arriba.",
                "n3": "El denominador se copia tal cual.",
            },
        },
        {
            "id": "E2",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                r"Suma $\dfrac{1}{3}+\dfrac{1}{4}$ y escribe el resultado como fracción, "
                "así: 5/12. No dejes espacios."
            ),
            "answer": "7/12",
            "hints": {
                "n1": "Los trozos no son del mismo tamaño: hace falta un reparto común.",
                "n2": "Con doceavos: 4/12 y 3/12.",
                "n3": "4 + 3 = 7, y el denominador es 12.",
            },
        },
        {
            "id": "E3",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"¿Cuánto es $\dfrac{7a}{8}-\dfrac{3a}{8}$, ya simplificado?",
            "options": [
                {"id": "ok", "text": r"$\dfrac{a}{2}$", "latex": r"\dfrac{a}{2}"},
                {
                    "id": "unsimplified",
                    "text": r"$\dfrac{4a}{8}$… pero aún se simplifica",
                    "latex": r"\dfrac{4a}{8}",
                },
                {"id": "trap", "text": r"$\dfrac{4a}{0}$", "latex": r"\dfrac{4a}{0}"},
                {"id": "wrong", "text": r"$\dfrac{4a}{16}$", "latex": r"\dfrac{4a}{16}"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "unsimplified": "fb_f02_e3_half",
                "trap": "fb_f02_e3_zero",
                "wrong": "fb_f02_e3_sum",
            },
            "misconception_by_option": {
                "unsimplified": "habito_deja_el_resultado_sin_simplificar",
                "trap": "resta_los_denominadores",
                "wrong": "suma_numeradores_y_denominadores",
            },
            "hints": {
                "n1": "Mismo denominador: resta arriba y copia abajo.",
                "n2": "Queda 4a/8.",
                "n3": "4 y 8 se dividen los dos entre 4.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un escriba anota $\dfrac{1}{2}+\dfrac{1}{5}=\dfrac{2}{7}$. ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "common",
                    "text": r"Sumó arriba y abajo sin llevarlas a un denominador común: es $\dfrac{7}{10}$",
                },
                {"id": "num", "text": "Sumó mal los numeradores"},
                {"id": "op", "text": "La operación no era una suma"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "common",
            "feedback_by_option": {
                "common": "correct",
                "num": "fb_f02_e4_num",
                "op": "fb_f02_e4_op",
                "none": "fb_f02_e4_none",
            },
            "misconception_by_option": {
                "num": "suma_numeradores_y_denominadores",
                "op": "confunde_la_operacion_dictada",
                "none": "suma_numeradores_y_denominadores",
            },
            "hints": {
                "n1": "Medio caudal ya es más que dos séptimos.",
                "n2": "Los trozos no son del mismo tamaño.",
                "n3": "Con décimos: 5/10 y 2/10.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Para sumar dos fracciones se suman los numeradores "
                "entre sí y los denominadores entre sí.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": r"Falsa: $\dfrac{2}{5}+\dfrac{1}{5}$ sería $\dfrac{3}{10}$, menos que lo que ya había",
                },
                {"id": "true", "text": "Verdadera: se opera arriba con arriba y abajo con abajo"},
                {"id": "true_same", "text": "Verdadera cuando los denominadores son iguales"},
                {"id": "false_never", "text": "Falsa: los numeradores tampoco se suman nunca"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_f02_e5_trap",
                "true_same": "fb_f02_e5_same",
                "false_never": "fb_f02_e5_never",
            },
            "misconception_by_option": {
                "true": "suma_numeradores_y_denominadores",
                "true_same": "suma_numeradores_y_denominadores",
                "false_never": "sobregeneraliza_suma_de_fracciones_algebraicas",
            },
            "hints": {
                "n1": "Juntar agua no puede dar menos agua.",
                "n2": "2/5 son 0,4 y 3/10 son 0,3.",
                "n3": "El denominador nombra el trozo; no se suma.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": (
                "Selecciona TODAS las sumas que se pueden hacer sin cambiar ningún denominador."
            ),
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {
                    "id": "a",
                    "text": r"$\dfrac{2}{x}+\dfrac{5}{x}$",
                    "latex": r"\dfrac{2}{x}+\dfrac{5}{x}",
                },
                {
                    "id": "b",
                    "text": r"$\dfrac{1}{3}+\dfrac{1}{5}$",
                    "latex": r"\dfrac{1}{3}+\dfrac{1}{5}",
                },
                {
                    "id": "c",
                    "text": r"$\dfrac{3a}{7}-\dfrac{a}{7}$",
                    "latex": r"\dfrac{3a}{7}-\dfrac{a}{7}",
                },
                {
                    "id": "d",
                    "text": r"$\dfrac{1}{x}+\dfrac{1}{y}$",
                    "latex": r"\dfrac{1}{x}+\dfrac{1}{y}",
                },
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Compara los dos denominadores de cada suma.",
                "n2": "Si son idénticos, se suma directo.",
                "n3": "x e y son denominadores distintos aunque los dos sean letras.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Dos acequias riegan la misma tabla: una toma 5c partes de un caudal "
                "repartido en 12 y la otra, 3c partes. Con c = 3, ¿cuántas partes de 12 "
                "toman entre las dos?"
            ),
            "expr": r"\dfrac{5c}{12}+\dfrac{3c}{12}=\dfrac{8c}{12},\quad c=3",
            "answer": "24",
            "hints": {
                "n1": "Mismo denominador: suma los numeradores.",
                "n2": "5c + 3c = 8c.",
                "n3": "Con c = 3: 8 · 3 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se puede sumar directamente?",
        "title": "Qué hay que mirar antes de juntar dos fracciones",
        "intro": (
            "La primera pregunta nunca es cuánto suman, sino si los trozos son del mismo "
            "tamaño. Y la última, si el resultado ya está en su forma más corta."
        ),
        "rows": [
            {
                "symbol": r"\dfrac{3}{x}+\dfrac{2}{x}",
                "name": "Mismo denominador",
                "closed": "yes",
                "latex": r"\dfrac{5}{x}",
                "note": "Se suman los de arriba y el de abajo se copia. Es el caso focal.",
            },
            {
                "symbol": r"\dfrac{5c}{6}-\dfrac{c}{6}",
                "name": "La resta va igual",
                "closed": "yes",
                "latex": r"\dfrac{4c}{6}",
                "note": "Restar cuenta trozos igual que sumar: el denominador tampoco se toca.",
            },
            {
                "symbol": r"\dfrac{4c}{6}",
                "name": "El resultado aún se simplifica",
                "closed": "partial",
                "latex": r"\dfrac{2c}{3}",
                "note": "La suma salió bien y aun así falta un paso. Terminar no es lo mismo que sumar.",
            },
            {
                "symbol": r"\dfrac{1}{2}+\dfrac{1}{3}",
                "name": "Denominadores distintos",
                "closed": "no",
                "latex": r"\dfrac{3}{6}+\dfrac{2}{6}=\dfrac{5}{6}",
                "note": "Hay que repartirlo todo en trozos del mismo tamaño antes de contar.",
            },
            {
                "symbol": r"\dfrac{1}{x}+\dfrac{1}{y}",
                "name": "Distintos, con letras",
                "closed": "no",
                "latex": r"\dfrac{y+x}{xy}",
                "note": "Dos letras distintas son dos repartos distintos. El común es su producto.",
            },
            {
                "symbol": r"\dfrac{2}{5}\cdot\dfrac{1}{3}",
                "name": "Un producto, no una suma",
                "closed": "no",
                "latex": r"\dfrac{2}{15}",
                "note": "Aquí el denominador común no pinta nada: multiplicar tiene otra regla. Es lo de la era.",
            },
        ],
        "outro": (
            "La tercera fila es la que se olvida cuando ya se sabe la regla: el resultado "
            "correcto puede seguir sin estar terminado. La sexta marca el límite de esta "
            "sala — en cuanto la operación es un producto, buscar denominador común deja "
            "de tener sentido, y eso se ve en la era de trilla."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres registros de riego trabajados en este nodo?",
        "thumbnails": [
            r"\dfrac{3}{x}+\dfrac{2}{x}",
            r"\dfrac{5c}{6}-\dfrac{c}{6}",
            r"\dfrac{1}{2}+\dfrac{1}{3}",
        ],
        "options": [
            {
                "id": "same_size",
                "text": "En los tres hay que asegurarse de que los trozos son del mismo tamaño antes de contar",
                "correct": True,
            },
            {
                "id": "roles",
                "text": "En los tres el número de arriba cuenta y el de abajo nombra",
                "correct": True,
            },
            {
                "id": "both_sum",
                "text": "En los tres se suman los cuatro números que aparecen",
                "correct": False,
            },
            {
                "id": "done",
                "text": "En los tres el resultado ya queda simplificado al sumar",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Turno de cierre del canal madre. La acequia del norte toma 7n partes de un "
            "caudal repartido en 15 y la del este toma 3n partes del mismo reparto. Hoy "
            "n vale 3. ¿Cuántas partes de 15 salen del canal madre en total?"
        ),
        "polya": {
            "comprender": "Las dos acequias cuentan trozos del mismo reparto: los denominadores ya son iguales.",
            "planear": "Sumo los numeradores y copio el 15. Después sustituyo n = 3.",
            "ejecutar": "7n + 3n = 10n, así que son 10n/15. Con n = 3: 30 partes de 15.",
            "comprobar": "30 partes de 15 son dos caudales enteros, y en efecto 7·3 + 3·3 = 30 ✓. Si hubiera sumado abajo, el 15 se habría vuelto 30 y el agua se habría reducido a la mitad.",
        },
        "prompt": "¿Cuántas partes de 15 salen en total?",
        "answer": "30",
        "hints": {
            "n1": "Los dos denominadores son 15: no se tocan.",
            "n2": "7n + 3n = 10n.",
            "n3": "Con n = 3: 10 · 3 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otro turno de riego. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya copias el denominador en vez de sumarlo.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué trabajo hace "
            "cada uno de los dos números de una fracción."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto es $\dfrac{3}{8}+\dfrac{4}{8}$?",
                "options": [
                    {"id": "seven8", "text": r"$\dfrac{7}{8}$", "latex": r"\dfrac{7}{8}"},
                    {"id": "seven16", "text": r"$\dfrac{7}{16}$", "latex": r"\dfrac{7}{16}"},
                    {"id": "twelve", "text": r"$\dfrac{12}{8}$", "latex": r"\dfrac{12}{8}"},
                ],
                "expected": "seven8",
                "misconception_by_option": {
                    "seven16": "suma_numeradores_y_denominadores",
                    "twelve": "multiplica_en_vez_de_sumar",
                },
            },
            {
                "id": "PD2",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": (
                    "Un ramal lleva 5 partes de un caudal repartido en 9 y otro lleva 2. "
                    "¿Cuántas partes de 9 llevan entre los dos?"
                ),
                "answer": "7",
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Se pueden sumar $\dfrac{1}{3}$ y $\dfrac{1}{4}$ sumando los numeradores?",
                "options": [
                    {"id": "no", "text": "No: las partes no son del mismo tamaño"},
                    {"id": "yes", "text": r"Sí: da $\dfrac{2}{7}$"},
                    {"id": "yes_after", "text": "Sí, y luego se simplifica"},
                ],
                "expected": "no",
                "misconception_by_option": {
                    "yes": "suma_numeradores_y_denominadores",
                    "yes_after": "suma_numeradores_y_denominadores",
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
        "default": "Mira primero si los denominadores son iguales; si lo son, no los toques.",
        "fb_f02_e1_trap": (
            "Sumaste también abajo. → El denominador no es agua: dice en cuántos trozos "
            "está repartida."
        ),
        "fb_f02_e1_sq": (
            "Ahí multiplicaste los denominadores. → Con denominadores iguales no hace falta "
            "buscar nada: se copia."
        ),
        "fb_f02_e1_mult": "4 y 3 se suman, no se multiplican. → La operación era una suma.",
        "fb_f02_e3_half": (
            "Vas bien: 4a/8 es correcto pero no está terminado. → Arriba y abajo se dividen "
            "entre 4."
        ),
        "fb_f02_e3_zero": (
            "Los denominadores no se restan. → El 8 se copia; un denominador 0 no existiría."
        ),
        "fb_f02_e3_sum": "Ahí sumaste los denominadores. → El 8 se queda como está.",
        "fb_f02_e4_num": (
            "Los numeradores están bien sumados: 1 + 1 = 2. → El problema es que no se "
            "podían sumar todavía."
        ),
        "fb_f02_e4_op": "Sí era una suma. → Lo que falta es el denominador común.",
        "fb_f02_e4_none": (
            "Medio caudal es 0,5 y dos séptimos son 0,29. → Sumar agua no puede dar menos agua."
        ),
        "fb_f02_e5_trap": (
            "Arriba con arriba está bien; abajo con abajo, no. → El de abajo nombra el trozo."
        ),
        "fb_f02_e5_same": (
            "Justo cuando son iguales es cuando NO se suman: se copian. → 2/5 + 1/5 = 3/5."
        ),
        "fb_f02_e5_never": (
            "Te pasaste al otro extremo: los numeradores sí se suman. → Lo que no se suma "
            "es el denominador."
        ),
    },
    "closing": (
        "El registro del turno ya dice cuánta agua sale sin que el caudal mengüe por el "
        "camino. Tabiry sube a la era de trilla: allí no se juntan partes, se toman partes "
        "DE partes — y buscar denominador común deja de servir para nada."
    ),
    "validation_status": "F5_F02_11bloques",
}
