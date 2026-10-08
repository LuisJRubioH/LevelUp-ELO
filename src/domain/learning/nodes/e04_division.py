"""E04 · División — dividir no siempre achica.

Edificio del nodo: EL COMEDOR COMUNAL (hogazas, raciones, mesas, el caldero y
el cucharón). Ningún otro edificio de N2 usa este oficio.
"""

NODE_ID = "PREALG-N2-E04-DIVISION-REPARTIR"
CONCEPT_SLUG = "division"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "division",
    "misconception": "dividir_siempre_achica",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El Comedor Comunal · División",
    "building": "El Comedor Comunal",
    "finish_label": "Salir hacia el Invernadero",
    "title": "Dividir no siempre achica",
    "intro": (
        "Repartir en partes iguales es lo que se hace todo el día en este edificio. "
        "Hoy vas a decidir dos cosas: qué pasa cuando el reparto no da exacto, y por "
        "qué dividir entre media hogaza da MÁS raciones, no menos."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de entrar a la cocina. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Hay 18 hogazas para 3 mesas iguales. ¿Cuántas hogazas por mesa?",
                "answer": "6",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $12\div\dfrac{1}{2}$?",
                "options": [
                    {"id": "twentyfour", "text": "24", "latex": r"24"},
                    {"id": "six", "text": "6", "latex": r"6"},
                    {"id": "twelve_half", "text": "12,5", "latex": r"12{,}5"},
                ],
                "expected": "twentyfour",
                "misconception_by_option": {
                    "six": "dividir_siempre_achica",
                    "twelve_half": "confunde_dividir_con_restar",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "5 hogazas para 2 mesas iguales. ¿Cuánto recibe cada mesa?",
                "options": [
                    {"id": "two_half", "text": "2 hogazas y media", "latex": r"2{,}5"},
                    {"id": "two_left", "text": "2 y sobra 1 que no se reparte"},
                    {"id": "cannot", "text": "No se puede: 5 no es divisible entre 2"},
                    {"id": "inverted", "text": "2/5 de hogaza", "latex": r"\dfrac{2}{5}"},
                ],
                "expected": "two_half",
                "misconception_by_option": {
                    "two_left": "reparto_solo_entero",
                    "cannot": "reparto_solo_entero",
                    "inverted": "invierte_cociente",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · Dentro del Comedor Comunal",
        "title": "La noche que faltaba comida y sobraba",
        "body": (
            "El cuarto edificio es el Comedor Comunal: un salón con mesas corridas, un "
            "caldero grande al fondo y una regla de la casa que nadie discute — todo se "
            "sirve en partes iguales, y lo que sobra también se reparte.\n\n"
            "Esta noche llegaron más comensales de los previstos y el cocinero mandó "
            "cortar cada hogaza por la mitad. El ayudante que llevaba la cuenta se puso "
            "pálido: si ahora hay que dividir entre media hogaza, dijo, van a salir "
            "muchísimas menos raciones. Dividir siempre achica."
        ),
        "question": "Al repartir 12 hogazas en raciones de media hogaza, ¿salen más raciones o menos?",
        "image": "/leccion/02-prealg-n2-mercado/e04-division-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Menos: dividir siempre achica"},
                {"id": "b", "text": "Más: cada ración es más pequeña, así que caben más"},
                {"id": "c", "text": "Las mismas: partirlas no cambia la cantidad de comida"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir cuándo una "
                "división achica y cuándo agranda, sin adivinar."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "El mismo caldero, dos repartos distintos",
        "body": (
            "Abajo hay dos divisiones que arrancan de las mismas 12 hogazas. Mira dónde "
            "termina cada una respecto al 12 de partida."
        ),
        "cases": [
            {
                "label": "Caso que confirma lo que esperas",
                "context": "12 hogazas repartidas entre 4 mesas",
                "fraction": r"12\div 4",
                "division": r"12\div 4=3",
                "note": "3 está por debajo de 12: el divisor era mayor que 1.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Las mismas 12 hogazas, servidas en raciones de media",
                "fraction": r"12\div\dfrac{1}{2}",
                "division": r"12\div\dfrac{1}{2}=24",
                "note": "24 está por encima de 12: el divisor era menor que 1.",
            },
        ],
        "resolution": (
            "La pregunta de la segunda no es «cuánto le toca a cada uno» sino «cuántas "
            "raciones de media hogaza caben en 12 hogazas». Esa es la otra cara de la "
            "división, y con divisores menores que 1 el resultado crece. Lo que decide no "
            "es dividir: es si el divisor está por encima o por debajo de 1."
        ),
    },
    "definition_title": "La división",
    "definition_katex": r"a\div b=c\iff a=b\times c,\qquad b\neq 0",
    "definition": (
        "Dividir responde dos preguntas con la misma cuenta: cuánto le toca a cada uno "
        "de b grupos, o cuántos grupos de tamaño b caben en a. Si el reparto no es "
        "exacto queda un residuo, y ese residuo también se reparte. El divisor nunca "
        "puede ser cero."
    ),
    "definition_symbols": [
        {"symbol": r"a", "reads": "dividendo", "means": "lo que se reparte"},
        {
            "symbol": r"b",
            "reads": "divisor",
            "means": "entre cuántos, o de qué tamaño es cada parte",
        },
        {"symbol": r"c", "reads": "cociente", "means": "el resultado del reparto"},
        {
            "symbol": r"r",
            "reads": "residuo",
            "means": "lo que queda sin repartir en enteros; sigue siendo comida",
        },
        {
            "symbol": r"b\neq 0",
            "reads": "b distinto de cero",
            "means": "repartir entre cero mesas no es un reparto",
        },
        {
            "symbol": r"0<b<1",
            "reads": "divisor entre cero y uno",
            "means": "el cociente queda POR ENCIMA del dividendo",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Racionales",
            "title": "Cuando el reparto no da entero",
            "statement": (
                "Quedan 27 hogazas y hay 6 mesas ocupadas. La regla de la casa dice que "
                "lo que sobra también se reparte. ¿Cuánto recibe cada mesa?"
            ),
            "latex": r"27\div 6",
            "image_slot": True,
            "image": "/leccion/02-prealg-n2-mercado/e04-reparto-residuo-v4.png",
            "steps": [
                "Reparto 27 entre 6. El múltiplo de 6 más cercano sin pasarse es 6 × 4 = 24.",
                "Cada mesa lleva 4 hogazas enteras y sobran 27 − 24 = 3.",
                "Aquí es donde el comedor no se detiene: esas 3 hogazas también se reparten entre las 6 mesas.",
                "3 ÷ 6 = 0,5. Cada mesa recibe media hogaza más.",
                "27 ÷ 6 = 4,5. El reparto SÍ terminó; lo que no cabía era el resultado en los enteros.",
            ],
            "solution": r"$27\div 6=4{,}5$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 las 3 hogazas que sobran se vuelven a repartir. ¿Por qué el residuo no es el final de la cuenta?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Racionales · cuántos caben",
            "title": "Raciones de media hogaza",
            "statement": (
                "El cocinero manda servir 12 hogazas en raciones de media hogaza cada una. "
                "¿Cuántas raciones salen?"
            ),
            "latex": r"12\div\dfrac{1}{2}",
            "image_slot": False,
            "steps": [
                "La pregunta no es cuánto le toca a cada uno: es cuántas medias hogazas caben en 12.",
                "De cada hogaza salen 2 raciones, y hay 12 hogazas.",
                "Dividir entre una fracción es multiplicar por su inverso: 12 ÷ 1/2 = 12 × 2.",
                "12 × 2 = 24 raciones.",
                "El divisor era menor que 1 y el resultado creció: 24 está por encima de 12.",
            ],
            "solution": r"$12\div\dfrac{1}{2}=24$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El ayudante que se quedó corto",
            "statement": (
                "El ayudante anota en la pizarra de la cocina: «Hay 20 hogazas y las vamos "
                "a servir en raciones de media. Dividir achica, así que salen 10 raciones. "
                "No alcanza para los 30 comensales»."
            ),
            "latex": r"20\div\dfrac{1}{2}=10",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"20\div\dfrac{1}{2}=\underline{10}",
            "error_note": "10 es 20 × 1/2, no 20 ÷ 1/2. Multiplicó donde tenía que dividir.",
            "correct_version": {
                "wrong_latex": r"20\div\dfrac{1}{2}=10",
                "right_latex": r"20\div\dfrac{1}{2}=40",
                "rows": [
                    {
                        "wrong": "Dividir siempre da un resultado menor",
                        "right": "Dividir entre un número entre 0 y 1 da un resultado mayor",
                    },
                    {
                        "wrong": "De 20 hogazas salen 10 medias raciones",
                        "right": "De 20 hogazas salen 40 medias raciones",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 10 no puede ser la respuesta? Escribe la igualdad corregida.",
            "steps": [
                "Comprueba con la definición: si 20 ÷ 1/2 fuera 10, entonces 10 × 1/2 debería dar 20.",
                "10 × 1/2 = 5, no 20. La igualdad no se sostiene.",
                "De una sola hogaza salen 2 medias raciones. De 20 salen 40, y sí alcanza para 30 comensales.",
            ],
            "solution": (
                "«Dividir achica» vale mientras repartas entre 2, entre 3, entre 10. Cuando "
                "el divisor baja de 1, la división pregunta «cuántos caben» y la respuesta "
                "crece. La pregunta útil es siempre: ¿el divisor está por encima o por debajo de 1?"
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
                "statement": "Quedan 32 raciones de sopa y hay 5 mesas iguales.",
                "given_steps": [
                    r"32\div 5",
                    r"5\times 6=30,\ \text{sobran }2",
                    r"2\div 5=0{,}4",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"32\div 5=", "answer": "6,4"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "El caldero tiene 9 medidas de caldo y cada cuenco lleva un cuarto de medida.",
                "given_steps": [
                    r"9\div\dfrac{1}{4}=9\times 4",
                ],
                "blanks": [
                    {
                        "id": "P2-b1",
                        "label": r"\text{¿el divisor es mayor o menor que 1? }0\text{ si menor}, 1\text{ si mayor}",
                        "answer": "0",
                    },
                    {"id": "P2-b2", "label": r"9\div\dfrac{1}{4}=", "answer": "36"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: se reparte una deuda de 20 raciones del comedor "
                    "entre 5 turnos iguales. Anota cuánto le toca a cada turno, con su signo."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"-20\div 5=", "answer": "-4"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para el mismo cociente",
        "intro": r"¿Cuántas raciones de $\dfrac{3}{4}$ de hogaza salen de $\dfrac{9}{2}$ hogazas? Las dos soluciones son correctas.",
        "methods": [
            {
                "label": "Método 1 · Multiplicar por el inverso",
                "steps": [
                    r"\dfrac{9}{2}\div\dfrac{3}{4}=\dfrac{9}{2}\times\dfrac{4}{3}",
                    r"=\dfrac{36}{6}",
                    r"=6",
                ],
                "note": "Siempre funciona con fracciones.",
            },
            {
                "label": "Método 2 · Pasar todo a cuartos y contar",
                "steps": [
                    r"\dfrac{9}{2}=\dfrac{18}{4}",
                    r"\text{¿cuántos }\tfrac{3}{4}\text{ caben en }\tfrac{18}{4}?",
                    r"18\div 3=6",
                ],
                "note": "Cuenta piezas del mismo tamaño; se ve por qué el resultado es entero.",
            },
        ],
        "question": "¿Cuál te convence más de que el resultado es 6? ¿Y qué pasa con el método 2 si las raciones fueran de 1/7?",
        "insight": (
            "El método 2 solo es cómodo cuando los dos denominadores se dejan llevar a uno "
            "común pequeño; con 1/7 el conteo se vuelve impracticable y el método 1 sigue "
            "igual de barato. Y hay algo que ninguno de los dos arregla: cambiar el orden. "
            "9/2 ÷ 3/4 y 3/4 ÷ 9/2 dan cosas distintas, porque la división no es conmutativa (N3-M01)."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Hay 20 hogazas para 5 mesas iguales. ¿Cuántas hogazas por mesa?",
            "expr": r"20\div 5",
            "answer": "4",
            "hints": {
                "n1": "Reparto en partes iguales entre las mesas.",
                "n2": "¿Cuántas veces cabe 5 en 20?",
                "n3": "5 × 4 = 20.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Quedan 7 hogazas para 4 mesas iguales y lo que sobra también se reparte. ¿Cuánto por mesa? (decimal)",
            "expr": r"7\div 4",
            "answer": "1,75",
            "hints": {
                "n1": "Primero las hogazas enteras: 4 × 1 = 4.",
                "n2": "Sobran 3, y esas 3 también se reparten entre 4.",
                "n3": "3 ÷ 4 = 0,75.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El caldero tiene 6 medidas de caldo y cada cuenco lleva media medida. ¿Cuántos cuencos salen?",
            "expr": r"6\div\dfrac{1}{2}",
            "answer": "12",
            "hints": {
                "n1": "La pregunta es cuántas medias medidas caben en 6.",
                "n2": "De cada medida salen 2 cuencos.",
                "n3": "6 ÷ 1/2 = 6 × 2.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "El ayudante anota «22 raciones entre 4 mesas = 5, y sobran 2 que se botan». ¿Dónde está el error?",
            "options": [
                {"id": "remainder", "text": "El residuo también se reparte: cada mesa lleva 5,5"},
                {"id": "quotient", "text": "El cociente está mal: 4 cabe 6 veces en 22"},
                {"id": "inverted", "text": "Dividió al revés: era 4 entre 22"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "remainder",
            "feedback_by_option": {
                "remainder": "correct",
                "quotient": "fb_e04_e4_quotient",
                "inverted": "fb_e04_e4_inverted",
                "none": "fb_e04_e4_none",
            },
            "misconception_by_option": {
                "quotient": "error_de_calculo_del_cociente",
                "inverted": "invierte_cociente",
                "none": "reparto_solo_entero",
            },
            "hints": {
                "n1": "La regla de la casa dice que lo que sobra también se reparte.",
                "n2": "Sobran 2 raciones y hay 4 mesas.",
                "n3": "2 ÷ 4 = 0,5, así que cada mesa lleva 5 + 0,5.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para cualesquiera $a>0$ y $b>0$: $a\div b<a$.»",
            "options": [
                {
                    "id": "false_small",
                    "text": "Falsa: si b está entre 0 y 1, el cociente queda por encima de a",
                },
                {"id": "true", "text": "Verdadera: dividir siempre achica"},
                {"id": "false_never", "text": "Falsa: el cociente nunca baja de a"},
                {"id": "true_if_int", "text": "Verdadera siempre que b sea entero"},
            ],
            "expected": "false_small",
            "feedback_by_option": {
                "false_small": "correct",
                "true": "fb_e04_e5_trap",
                "false_never": "fb_e04_e5_never",
                "true_if_int": "fb_e04_e5_int",
            },
            "misconception_by_option": {
                "true": "dividir_siempre_achica",
                "false_never": "dividir_siempre_agranda",
                "true_if_int": "olvida_el_divisor_uno",
            },
            "hints": {
                "n1": "Para tumbar un «siempre» basta UN caso.",
                "n2": "Prueba con a = 12 y b = 0,5.",
                "n3": "12 ÷ 0,5 = 24, y 24 no es menor que 12.",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Quedan 15 hogazas y el cocinero manda servirlas en raciones de un tercio "
                "de hogaza. ¿Cuántas raciones salen?"
            ),
            "expr": r"15\div\dfrac{1}{3}",
            "answer": "45",
            "hints": {
                "n1": "¿Cuántos tercios caben en una hogaza?",
                "n2": "De cada hogaza salen 3 raciones.",
                "n3": "15 ÷ 1/3 = 15 × 3.",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": "¿Cuál es el conjunto más pequeño de la escalera donde toda división (con divisor distinto de 0) tiene resultado?",
            "options": [
                {"id": "rationals", "text": "Los racionales", "latex": r"\mathbb{Q}"},
                {"id": "naturals", "text": "Los naturales", "latex": r"\mathbb{N}"},
                {"id": "integers", "text": "Los enteros", "latex": r"\mathbb{Z}"},
                {"id": "reals", "text": "Los reales", "latex": r"\mathbb{R}"},
            ],
            "expected": "rationals",
            "feedback_by_option": {
                "rationals": "correct",
                "naturals": "fb_e04_e7_breaks",
                "integers": "fb_e04_e7_breaks",
                "reals": "fb_e04_e7_bigger",
            },
            "misconception_by_option": {
                "naturals": "reparto_solo_entero",
                "integers": "reparto_solo_entero",
                "reals": "no_busca_el_minimo",
            },
            "hints": {
                "n1": "Busca el primer peldaño donde 5 ÷ 2 ya tiene respuesta.",
                "n2": "En ℕ y en ℤ, 5 ÷ 2 se sale del conjunto.",
                "n3": "Piden el MÁS PEQUEÑO que sirva, no cualquiera que sirva.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "La escalera de la división",
        "title": "¿La división de dos elementos del conjunto vive en el conjunto?",
        "intro": "Aquí la escalera vuelve a romperse, y en un peldaño distinto al de la resta.",
        "rows": [
            {
                "symbol": r"\mathbb{N}",
                "name": "Naturales",
                "closed": "no",
                "latex": r"5\div 2\notin\mathbb{N}",
                "note": "El reparto no exacto no da un número de contar.",
            },
            {
                "symbol": r"\mathbb{Z}",
                "name": "Enteros",
                "closed": "no",
                "latex": r"5\div 2\notin\mathbb{Z}",
                "note": "Los negativos no ayudaron: 5 entre 2 sigue sin ser entero. La resta se arregló aquí; la división no.",
            },
            {
                "symbol": r"\mathbb{Q}",
                "name": "Racionales",
                "closed": "yes",
                "latex": r"\dfrac{a}{b}\div\dfrac{c}{d}=\dfrac{a\,d}{b\,c}\in\mathbb{Q}",
                "note": "ℚ nació exactamente de esto (B06): darle respuesta a todo reparto, mientras el divisor no sea 0.",
            },
            {
                "symbol": r"\mathbb{I}",
                "name": "Irracionales",
                "closed": "no",
                "latex": r"\sqrt{8}\div\sqrt{2}=2\in\mathbb{Q}",
                "note": "Dos irracionales pueden dar un racional: el resultado SE SALE. Ninguna operación aritmética cierra 𝕀.",
            },
            {
                "symbol": r"\mathbb{R}",
                "name": "Reales",
                "closed": "yes",
                "latex": r"\pi\div 2=\dfrac{\pi}{2}\in\mathbb{R}",
                "note": "ℝ = ℚ ∪ 𝕀 (B08) sí cierra: la división vive cómoda ahí.",
            },
            {
                "symbol": r"\mathbb{C}",
                "name": "Complejos",
                "closed": "yes",
                "latex": r"\dfrac{1}{i}=-i",
                "note": "También cierra. Desvío opcional (B09).",
            },
        ],
        "outro": (
            "Dos operaciones han roto la escalera: la resta obligó a inventar ℤ y la división "
            "obligó a inventar ℚ. Las dos que faltan van a llevarte más lejos todavía."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"27\div 6", r"12\div\tfrac{1}{2}", r"20\div\tfrac{1}{2}"],
        "options": [
            {
                "id": "equal_parts",
                "text": "En los tres se reparte en partes iguales",
                "correct": True,
            },
            {
                "id": "smaller",
                "text": "En los tres el resultado es menor que el dividendo",
                "correct": False,
            },
            {
                "id": "divisor",
                "text": "En los tres el divisor decide si el resultado sube o baja",
                "correct": True,
            },
            {
                "id": "exact",
                "text": "En los tres el reparto da exacto en enteros",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Cierra el comedor: quedan 9 hogazas y hay que servirlas en raciones de tres "
            "cuartos de hogaza. ¿Cuántas raciones salen?"
        ),
        "polya": {
            "comprender": "Tengo 9 hogazas y raciones de 3/4. Me preguntan cuántas raciones caben, no cuánto le toca a cada uno.",
            "planear": "Divido 9 entre 3/4 multiplicando por el inverso.",
            "ejecutar": "9 ÷ 3/4 = 9 × 4/3 = 36/3 = 12.",
            "comprobar": "12 raciones × 3/4 de hogaza = 36/4 = 9 hogazas. Cuadra, y 12 > 9 porque el divisor era menor que 1.",
        },
        "prompt": "¿Cuántas raciones salen?",
        "answer": "12",
        "hints": {
            "n1": "La pregunta es cuántos 3/4 caben en 9.",
            "n2": "Dividir entre 3/4 es multiplicar por 4/3.",
            "n3": "9 × 4 = 36, y 36 ÷ 3 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya miras el divisor antes de decidir si el resultado baja.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué pasa al dividir "
            "entre un número menor que 1."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Hay 24 hogazas para 4 mesas iguales. ¿Cuántas por mesa?",
                "answer": "6",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $10\div\dfrac{1}{5}$?",
                "options": [
                    {"id": "fifty", "text": "50", "latex": r"50"},
                    {"id": "two", "text": "2", "latex": r"2"},
                    {"id": "ten_fifth", "text": "10,2", "latex": r"10{,}2"},
                ],
                "expected": "fifty",
                "misconception_by_option": {
                    "two": "dividir_siempre_achica",
                    "ten_fifth": "confunde_dividir_con_restar",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Existen $a>0$ y $b>0$ tales que $a\div b>a$?",
                "options": [
                    {"id": "yes", "text": "Sí"},
                    {"id": "no", "text": "No"},
                ],
                "expected": "yes",
                "misconception_by_option": {"no": "dividir_siempre_achica"},
                # Variante VERDADERA de E5, con los dos números positivos a
                # propósito: cierra la salida "solo pasa con negativos".
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
        "default": "Mira si el divisor está por encima o por debajo de 1 antes de decidir.",
        "fb_e04_e4_quotient": (
            "El cociente entero está bien: 4 × 5 = 20 y sobran 2. El problema es qué se hace "
            "con esos 2. → Repártelos entre las 4 mesas."
        ),
        "fb_e04_e4_inverted": (
            "El orden está bien: se reparten 22 raciones entre 4 mesas. → Fíjate en qué pasa "
            "con lo que sobra."
        ),
        "fb_e04_e4_none": (
            "En este comedor no se bota lo que sobra: se reparte. → Calcula 2 ÷ 4 y súmalo al cociente."
        ),
        "fb_e04_e5_trap": (
            "Esa regla vale mientras el divisor sea mayor que 1. → Prueba con a = 12 y "
            "b = 0,5 y mira si se sostiene."
        ),
        "fb_e04_e5_never": (
            "Te pasaste al otro extremo: con b = 4 sí baja. → Da un caso donde baje y otro donde suba."
        ),
        "fb_e04_e5_int": (
            "Prueba con b = 1, que también es entero: 12 ÷ 1 = 12, ni mayor ni menor. "
            "→ Di qué pasa en ese caso."
        ),
        "fb_e04_e7_breaks": (
            "Ahí 5 ÷ 2 no tiene respuesta dentro del conjunto: ese peldaño se rompe. "
            "→ Sube al siguiente."
        ),
        "fb_e04_e7_bigger": (
            "Ahí sí funciona, pero te piden el conjunto MÁS PEQUEÑO donde ya funciona. "
            "→ Baja un peldaño y comprueba si todavía sirve."
        ),
    },
    "closing": (
        "Dividir reparte, y quien decide si el resultado sube o baja es el divisor. Aquí se "
        "rompió el segundo peldaño de la escalera: de esta operación nacieron los racionales. "
        "En el Invernadero vas a ver una operación que crece mucho más rápido de lo que parece."
    ),
    "validation_status": "F2_E04_11bloques",
}
