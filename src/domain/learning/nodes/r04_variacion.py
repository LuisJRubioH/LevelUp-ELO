"""R04 · La sala de las lámparas — no todo lo que se relaciona es directo.

Cuarta y última sala del taller del canon, y último nodo del Papiro de las
Cuatro Casas. Guía: Iuty. Vocabulario propio: lámpara, mecha, torcida, aceite,
reserva, noche. Nada de cuadrículas (R01), tinas (R02) ni pan de oro (R03).

Error focal: aplicar el esquema de la proporcionalidad directa a cualquier par
de magnitudes relacionadas. Cuando una sube y la otra baja, lo que se conserva
es el producto, no el cociente.
"""

NODE_ID = "ALG-N1-R04-VARIACION"
CONCEPT_SLUG = "variacion_directa_e_inversa"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "variacion_directa_e_inversa",
    "misconception": "toda_relacion_es_directa",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La sala de las lámparas · Variación directa e inversa",
    "house": "La sala de las lámparas",
    "guide": "Iuty",
    "finish_label": "Cerrar el papiro",
    "title": "Cuando una sube y la otra baja, lo que se conserva es el producto",
    "intro": (
        "Hasta ahora, cuando una cantidad crecía la otra crecía con ella. Esta sala trata "
        "el caso contrario, y el peligro no es que sea difícil: es que la cuenta de la "
        "tina se puede aplicar igual y devuelve un número creíble."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de encender nada. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Si 2 pintores tardan 6 días en un muro, ¿cuántos días tardan 4 pintores?",
                "answer": "3",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si se encienden MÁS lámparas, ¿cuánto dura la misma reserva de aceite?",
                "options": [
                    {"id": "less", "text": "Menos noches"},
                    {"id": "more", "text": "Más noches"},
                    {"id": "same", "text": "Las mismas noches"},
                ],
                "expected": "less",
                "misconception_by_option": {
                    "more": "toda_relacion_es_directa",
                    "same": "ignora_la_proporcionalidad",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Cuatro lámparas encendidas durante 12 noches. ¿Cuántas noches de lámpara son en total?",
                "answer": "48",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/r04-variacion-katia.png",
        "eyebrow": "KatIA · En la sala de las lámparas",
        "title": "La noche en que el taller se quedó a oscuras",
        "body": (
            "El taller trabaja de noche con lámparas de aceite. La reserva se guarda en "
            "una tinaja y se anota cuánto dura.\n\n"
            "«Con cuatro lámparas encendidas, la reserva daba para doce noches», dice "
            "Iuty. «El maestro mandó encender seis para acabar antes el friso.»\n\n"
            "«El escriba montó la cuenta como la de la tina de tinte: cuatro es a doce como "
            "seis es a equis. Le salieron dieciocho noches. Escribió que con más lámparas "
            "el aceite duraba más.»\n\n"
            "Iuty señala la tinaja vacía.\n\n"
            "«En la octava noche se apagó la última. Y el pan de oro no se puede pegar a "
            "oscuras.»"
        ),
        "question": "¿Toda pareja de cantidades relacionadas se calcula igual que el tinte y el lino?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Sí: si están relacionadas, la regla de tres siempre vale"},
                {"id": "b", "text": "No: cuando una sube y la otra baja hay que montarla al revés"},
                {"id": "c", "text": "No: cuando una baja no se puede calcular nada"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a poder decidir en dos segundos, antes "
                "de calcular, si lo que se conserva es el cociente o el producto."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos parejas de cantidades, dos cosas que no cambian",
        "body": "En las dos hay una relación firme. Lo que se conserva no es lo mismo.",
        "cases": [
            {
                "label": "Directa · se conserva el cociente",
                "context": "Tinte y lino: 3 medidas por 12 brazadas, 5 por 20",
                "fraction": r"\dfrac{3}{12}=\dfrac{5}{20}=\dfrac14",
                "division": r"\dfrac{y}{x}=k",
                "note": "Las dos suben juntas y su razón vale siempre lo mismo.",
            },
            {
                "label": "Inversa · se conserva el producto",
                "context": "Lámparas y noches: 4 por 12 noches, 6 por 8",
                "fraction": r"4\cdot 12=6\cdot 8=48",
                "division": r"x\cdot y=k",
                "note": "Una sube y la otra baja. El aceite total gastado es el mismo: 48 noches de lámpara.",
            },
        ],
        "resolution": (
            "Detrás de la proporcionalidad inversa hay una cantidad fija que se reparte: "
            "aquí, las 48 noches de lámpara que da la tinaja. Si enciendes más lámparas te "
            "toca a menos noches cada una. Por eso lo que no cambia es el producto — y por "
            "eso montar la regla de tres como si fuera directa da siempre el resultado en "
            "la dirección equivocada."
        ),
    },
    "definition_title": "Variación directa e inversa",
    "definition_katex": r"\text{directa: }\dfrac{y}{x}=k\qquad\text{inversa: }x\,y=k",
    "definition": (
        "Dos magnitudes varían de forma DIRECTA si al multiplicar una por un número la "
        "otra queda multiplicada por el mismo: su cociente es constante. Varían de forma "
        "INVERSA si al multiplicar una por un número la otra queda dividida entre ese "
        "número: su producto es constante. Hay parejas relacionadas que no son ni lo uno "
        "ni lo otro, y ahí ninguna de las dos reglas de tres sirve."
    ),
    "definition_symbols": [
        {"symbol": r"\dfrac{y}{x}=k", "reads": "directa", "means": "el cociente no cambia"},
        {"symbol": r"x\,y=k", "reads": "inversa", "means": "el producto no cambia"},
        {
            "symbol": r"4\cdot 12=48",
            "reads": "la constante",
            "means": "las noches de lámpara que da la tinaja",
        },
        {
            "symbol": r"x=\dfrac{48}{6}",
            "reads": "despejar",
            "means": "con la constante, la cuarta cantidad sale sola",
        },
        {
            "symbol": r"\dfrac{a}{b}=\dfrac{d}{c}",
            "reads": "regla de tres inversa",
            "means": "la misma cuenta, con una razón dada la vuelta",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · La reserva de la tinaja",
            "title": "Usar el producto constante",
            "statement": (
                "Con 4 lámparas la reserva dura 12 noches. Si se encienden 6 lámparas, "
                "¿cuántas noches dura?"
            ),
            "latex": r"4\cdot 12=6\cdot x",
            "image_slot": False,
            "steps": [
                "Primero decido el tipo: más lámparas gastan más deprisa, así que es inversa.",
                "Lo que se conserva es el producto: 4 · 12 = 48 noches de lámpara.",
                "Con 6 lámparas, 6 · x = 48.",
                "x = 48 ÷ 6 = 8 noches.",
                "Comprobación de dirección: 8 es menos que 12, como tenía que ser ✓.",
            ],
            "solution": r"$8$ noches",
            "self_explanation": {
                "step_index": 1,
                "prompt": "¿Qué representa el 48, si no son ni lámparas ni noches?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Manos para el friso",
            "title": "Decidir el tipo antes de calcular",
            "statement": (
                "Seis pintores acaban el friso en 10 días. ¿Cuántos días tardarían 15 " "pintores?"
            ),
            "latex": r"6\cdot 10=15\cdot x",
            "image_slot": False,
            "steps": [
                "¿Más pintores hacen falta más días? No: hacen falta menos. Es inversa.",
                "El producto constante es el trabajo total: 6 · 10 = 60 jornadas de pintor.",
                "Con 15 pintores: 15 · x = 60.",
                "x = 60 ÷ 15 = 4 días.",
                "Montada como directa habría dado 25 días, más que con seis pintores: un disparate visible.",
            ],
            "solution": r"$4$ días",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escriba que usó la cuenta de la tina",
            "statement": (
                "Vuelve el caso de la apertura: 4 lámparas dan 12 noches, y se encienden 6. "
                "El escriba escribió 4/12 = 6/x y anotó 18 noches."
            ),
            "latex": r"\dfrac{4}{12}=\dfrac{6}{x}",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"x=\dfrac{12\cdot 6}{4}=18",
            "error_note": (
                "La cuenta está bien hecha; lo que está mal es la cuenta elegida. Aplicó "
                "el esquema de una relación directa a una que es inversa."
            ),
            "correct_version": {
                "wrong_latex": r"\dfrac{4}{12}=\dfrac{6}{x}\Rightarrow x=18",
                "right_latex": r"4\cdot 12=6\cdot x\Rightarrow x=8",
                "rows": [
                    {
                        "wrong": "Más lámparas, más noches",
                        "right": "Más lámparas, menos noches: el aceite se reparte entre más",
                    },
                    {
                        "wrong": "Se conserva el cociente 4/12",
                        "right": "Se conserva el producto 4 · 12 = 48",
                    },
                ],
            },
            "explain_prompt": (
                "Explica qué pregunta habría que hacerse ANTES de montar la cuenta, y por "
                "qué 18 noches se puede descartar sin calcular nada."
            ),
            "steps": [
                "Antes de escribir nada: ¿si una sube, la otra sube o baja?",
                "Aquí baja, así que el resultado tiene que ser menor que 12. Dieciocho queda descartado de un vistazo.",
                "Regla para no volver a caer: primero el tipo de relación, después la cuenta. Nunca al revés.",
            ],
            "solution": (
                "Son 8 noches. La regla de tres no comprueba de qué tipo es la relación: "
                "eso lo tienes que decidir tú, y es el paso que el escriba se saltó."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La cuenta de la reserva va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": "Con 3 lámparas la reserva dura 20 noches. ¿Cuánto dura con 5 lámparas?",
                "given_steps": [r"3\cdot 20=60", r"5\cdot x=60"],
                "blanks": [{"id": "P1-b1", "label": r"60\div 5=", "answer": "12"}],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Ocho pintores acaban un muro en 9 días. ¿Cuántos días tardan 12?",
                "given_steps": [r"\text{inversa: el producto se conserva}"],
                "blanks": [
                    {"id": "P2-b1", "label": r"8\cdot 9=", "answer": "72"},
                    {"id": "P2-b2", "label": r"72\div 12=", "answer": "6"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: con 10 lámparas la reserva dura 6 noches. "
                    "¿Cuántas lámparas se pueden encender para que dure 15 noches?"
                ),
                "given_steps": [],
                "blanks": [{"id": "P3-b1", "label": r"x=", "answer": "4"}],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de resolver una inversa",
        "intro": r"Con 5 lámparas la reserva dura 24 noches. ¿Cuánto dura con 8?",
        "methods": [
            {
                "label": "Método 1 · Hallar la constante",
                "steps": [
                    r"5\cdot 24=120",
                    r"8\cdot x=120",
                    r"x=15",
                ],
                "note": "La constante tiene significado: 120 noches de lámpara en la tinaja.",
            },
            {
                "label": "Método 2 · Regla de tres inversa",
                "steps": [
                    r"\dfrac{5}{8}=\dfrac{x}{24}",
                    r"x=\dfrac{5\cdot 24}{8}",
                    r"15",
                ],
                "note": "Es la de la tina con una razón dada la vuelta. Hay que acordarse de invertirla.",
            },
        ],
        "question": "¿Cuál de los dos te avisa si te has equivocado de tipo de relación?",
        "insight": (
            "El primero, porque obliga a nombrar la constante. Si el producto de lámparas "
            "por noches no significa nada en el problema, es que la relación no era "
            "inversa y hay que parar. El segundo funciona igual de bien y es más rápido, "
            "pero depende de acordarse de dar la vuelta a una razón — el mismo tipo de "
            "olvido que dejaba al silo de simiente sin sacos."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "Con 6 lámparas la reserva dura 10 noches. ¿Cuántas noches dura con 4 " "lámparas?"
            ),
            "expr": r"6\cdot 10=4\cdot x",
            "answer": "15",
            "hints": {
                "n1": "Menos lámparas: el resultado tiene que subir.",
                "n2": "La constante es 6 · 10 = 60.",
                "n3": "60 ÷ 4 = …",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": (
                "Diez pintores acaban un muro en 12 días. ¿Cómo se calcula lo que tardan 8?"
            ),
            "options": [
                {
                    "id": "ok",
                    "text": r"$x=\dfrac{10\cdot 12}{8}$",
                    "latex": r"x=\dfrac{10\cdot 12}{8}",
                },
                {
                    "id": "direct",
                    "text": r"$x=\dfrac{8\cdot 12}{10}$",
                    "latex": r"x=\dfrac{8\cdot 12}{10}",
                },
                {"id": "sub", "text": r"$x=12-2$", "latex": r"x=12-2"},
                {"id": "same", "text": r"$x=12$", "latex": r"x=12"},
            ],
            "expected": "ok",
            "feedback_by_option": {
                "ok": "correct",
                "direct": "fb_r04_e2_direct",
                "sub": "fb_r04_e2_sub",
                "same": "fb_r04_e2_same",
            },
            "misconception_by_option": {
                "direct": "toda_relacion_es_directa",
                "sub": "escalado_aditivo",
                "same": "ignora_la_proporcionalidad",
            },
            "hints": {
                "n1": "Menos pintores tardan más días: es inversa.",
                "n2": "Lo que se conserva es el producto 10 · 12.",
                "n3": "Ese producto dividido entre 8.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                "La reserva da para 72 noches de lámpara. ¿Cuántas lámparas se pueden "
                "encender si el friso necesita 9 noches de trabajo?"
            ),
            "expr": r"x\cdot 9=72",
            "answer": "8",
            "hints": {
                "n1": "La constante ya la tienes: 72.",
                "n2": "Lámparas por noches = 72.",
                "n3": "72 ÷ 9 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                "Un escriba calcula: «5 pintores tardan 8 días, luego 10 pintores tardan "
                "16». ¿Dónde está el error?"
            ),
            "options": [
                {
                    "id": "inverse",
                    "text": r"Es inversa: el doble de pintores tarda la mitad, $4$ días",
                },
                {"id": "calc", "text": "Multiplicó mal: son 15 días"},
                {"id": "direct", "text": "Es directa pero se equivocó en el factor"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "inverse",
            "feedback_by_option": {
                "inverse": "correct",
                "calc": "fb_r04_e4_calc",
                "direct": "fb_r04_e4_direct",
                "none": "fb_r04_e4_none",
            },
            "misconception_by_option": {
                "calc": "ignora_la_proporcionalidad",
                "direct": "toda_relacion_es_directa",
                "none": "toda_relacion_es_directa",
            },
            "hints": {
                "n1": "¿Más manos tardan más o menos?",
                "n2": "Menos. Así que el resultado debe bajar de 8.",
                "n3": "El trabajo total es 5 · 8 = 40 jornadas.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Si dos cantidades están relacionadas, se pueden "
                "calcular siempre con una regla de tres directa.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: si una sube cuando la otra baja, lo que se conserva es el producto",
                },
                {"id": "true", "text": "Verdadera: para eso sirve la regla de tres"},
                {"id": "true_num", "text": "Verdadera siempre que los tres datos sean números"},
                {"id": "false_never", "text": "Falsa: la regla de tres directa no sirve para nada"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_r04_e5_trap",
                "true_num": "fb_r04_e5_num",
                "false_never": "fb_r04_e5_never",
            },
            "misconception_by_option": {
                "true": "toda_relacion_es_directa",
                "true_num": "toda_relacion_es_directa",
                "false_never": "sobregeneraliza_variacion_directa_e_inversa",
            },
            "hints": {
                "n1": "Piensa en lámparas y noches de reserva.",
                "n2": "Más lámparas dan menos noches.",
                "n3": "La regla directa daría más noches: imposible.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODAS las parejas que varían de forma INVERSA.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": "Lámparas encendidas y noches que dura la reserva"},
                {"id": "b", "text": "Medidas de tinte y brazadas de lino teñidas"},
                {"id": "c", "text": "Pintores y días para acabar el mismo muro"},
                {"id": "d", "text": "Lado de un cuadrado y su perímetro"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Inversa es «una sube y la otra baja».",
                "n2": "Comprueba si el producto se mantiene constante.",
                "n3": "El perímetro sube cuando sube el lado: esa es directa.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "La tinaja da 90 noches de lámpara. El taller enciende 5 lámparas durante "
                "6 noches y después apaga una. ¿Cuántas noches más aguanta la reserva con "
                "las 4 restantes?"
            ),
            "expr": r"\dfrac{90-5\cdot 6}{4}",
            "answer": "15",
            "hints": {
                "n1": "Primero calcula lo gastado: 5 lámparas por 6 noches.",
                "n2": "Quedan 90 − 30 = 60 noches de lámpara.",
                "n3": "60 ÷ 4 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se conserva el cociente?",
        "title": "Qué tipo de relación tiene cada pareja",
        "intro": (
            "La pregunta no es si están relacionadas: casi todo lo está. La pregunta es "
            "qué cantidad no cambia cuando las otras dos se mueven."
        ),
        "rows": [
            {
                "symbol": r"\text{tinte y lino}",
                "name": "Directa",
                "closed": "yes",
                "latex": r"\dfrac{3}{12}=\dfrac{5}{20}",
                "note": "Suben juntas y el cociente se conserva. Es lo de la tina.",
            },
            {
                "symbol": r"\text{lado y perímetro}",
                "name": "Directa también",
                "closed": "yes",
                "latex": r"\dfrac{P}{\ell}=4",
                "note": "Al doble de lado, el doble de perímetro. El cociente vale 4 siempre.",
            },
            {
                "symbol": r"\text{lámparas y noches}",
                "name": "Inversa",
                "closed": "no",
                "latex": r"4\cdot 12=6\cdot 8",
                "note": "Una sube y la otra baja: lo constante es el producto. Es el caso focal.",
            },
            {
                "symbol": r"\text{pintores y días}",
                "name": "Inversa también",
                "closed": "no",
                "latex": r"6\cdot 10=15\cdot 4",
                "note": "El producto es el trabajo total, y no cambia por repartirlo entre más manos.",
            },
            {
                "symbol": r"\text{lado y área}",
                "name": "Ni una cosa ni la otra",
                "closed": "partial",
                "latex": r"\ell=2\to A=4;\ \ell=4\to A=16",
                "note": "Crecen juntas, pero al doble de lado el área se hace CUATRO veces mayor. Ni el cociente ni el producto se conservan.",
            },
            {
                "symbol": r"\text{edad y brazadas}",
                "name": "Sin relación",
                "closed": "partial",
                "latex": r"\text{---}",
                "note": "No hay nada que conservar. Aquí ninguna de las dos reglas devuelve un número con sentido.",
            },
        ],
        "outro": (
            "La quinta fila es la más importante de todo el nodo: dos cantidades pueden "
            "crecer juntas sin ser proporcionales. Que suban a la vez no basta — hay que "
            "comprobar si al doblar una se dobla la otra. Y la sexta cierra el aviso: "
            "las dos reglas de tres devuelven un número siempre, tenga sentido o no. "
            "Decidir el tipo de relación es tu trabajo, no el de la cuenta."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos de la sala trabajados en este nodo?",
        "thumbnails": [r"4\cdot 12=6\cdot 8", r"6\cdot 10=15\cdot 4", r"x\cdot 9=72"],
        "options": [
            {
                "id": "product",
                "text": "En los tres hay una cantidad total fija que se reparte, y es el producto",
                "correct": True,
            },
            {
                "id": "direction",
                "text": "En los tres se puede saber antes de calcular si el resultado sube o baja",
                "correct": True,
            },
            {
                "id": "quotient",
                "text": "En los tres lo que se conserva es el cociente de las dos magnitudes",
                "correct": False,
            },
            {
                "id": "always",
                "text": "En los tres sirve la misma regla de tres que en la tina de tinte",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última anotación del papiro. Para terminar el friso antes de la crecida, el "
            "taller calcula: con 3 lámparas la reserva daba 20 noches, pero el maestro "
            "quiere trabajar solo 5 noches seguidas. ¿Cuántas lámparas se pueden encender?"
        ),
        "polya": {
            "comprender": "Más lámparas, menos noches: es una relación inversa, y se conoce el total que da la tinaja.",
            "planear": "Calculo la constante 3 · 20 y la divido entre las 5 noches que se quieren.",
            "ejecutar": "3 · 20 = 60 noches de lámpara, y 60 ÷ 5 = 12 lámparas.",
            "comprobar": "12 lámparas por 5 noches son 60 ✓, el mismo aceite. Con una regla de tres directa habrían salido 0,75 lámparas, que no es una lámpara ni es nada.",
        },
        "prompt": "¿Cuántas lámparas se pueden encender?",
        "answer": "12",
        "hints": {
            "n1": "Menos noches: harán falta más lámparas.",
            "n2": "La constante es 3 · 20 = 60.",
            "n3": "60 ÷ 5 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otra reserva. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya decides el tipo de relación antes de montar la cuenta.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo la pregunta "
            "previa: si una sube, ¿la otra sube o baja?"
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Si 3 pintores tardan 12 días en un muro, ¿cuántos días tardan 6 pintores?",
                "answer": "6",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "Si se encienden MENOS lámparas, ¿cuánto dura la misma reserva?",
                "options": [
                    {"id": "more", "text": "Más noches"},
                    {"id": "less", "text": "Menos noches"},
                    {"id": "same", "text": "Las mismas noches"},
                ],
                "expected": "more",
                "misconception_by_option": {
                    "less": "toda_relacion_es_directa",
                    "same": "ignora_la_proporcionalidad",
                },
            },
            {
                "id": "PD3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Cinco lámparas encendidas durante 9 noches. ¿Cuántas noches de lámpara son en total?",
                "answer": "45",
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
        "default": "Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva.",
        "fb_r04_e2_direct": (
            "Esa es la cuenta de una relación directa. → Menos pintores tardan más días, "
            "no menos."
        ),
        "fb_r04_e2_sub": (
            "Quitar dos pintores no quita dos días. → La relación es multiplicativa, no aditiva."
        ),
        "fb_r04_e2_same": (
            "Cambiar el número de pintores sí cambia los días. → Lo que no cambia es el "
            "trabajo total."
        ),
        "fb_r04_e4_calc": (
            "No hay error de cuentas: hay error de tipo. → Con más pintores el resultado "
            "tiene que bajar."
        ),
        "fb_r04_e4_direct": (
            "No es directa: más pintores no son más días. → Lo que se conserva es el producto."
        ),
        "fb_r04_e4_none": (
            "Diez pintores tardando 16 días es más que cinco tardando 8. → El doble de "
            "manos no puede tardar el doble."
        ),
        "fb_r04_e5_trap": (
            "La regla de tres sirve, pero hay dos. → La directa solo vale cuando las dos "
            "suben juntas."
        ),
        "fb_r04_e5_num": (
            "Que los datos sean números no dice nada del tipo de relación. → Lámparas y "
            "noches son números y varían al revés."
        ),
        "fb_r04_e5_never": (
            "Te pasaste al otro extremo: la directa es la correcta para el tinte y el lino. "
            "→ Lo que hay que elegir es cuál de las dos."
        ),
    },
    "closing": (
        "El friso se termina con luz suficiente y el papiro queda completo. Las cuatro "
        "casas están: nombrar lo que todavía no se conoce, combinarlo sin mezclar lo que "
        "no se mezcla, repartirlo sin perder nada por el camino y conservar la relación al "
        "cambiar de escala — sabiendo, además, cuándo esa relación va al revés. Con eso "
        "termina el Papiro de las Cuatro Casas."
    ),
    "validation_status": "F5_R04_11bloques",
}
