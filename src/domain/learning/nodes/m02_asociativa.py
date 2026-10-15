"""M02 · Asociativa — los paréntesis no son adorno.

Estación del nodo: EL HORNO DE FUNDICIÓN (lingotes que se funden por tandas; una
tanda es un paréntesis). Ninguna otra estación usa este material.
"""

NODE_ID = "PREALG-N3-M02-ASOCIATIVA"
CONCEPT_SLUG = "asociativa"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "asociativa",
    "misconception": "parentesis_son_decorativos",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "El Horno de Fundición · Asociativa",
    "station": "El Horno de Fundición",
    "finish_label": "Salir hacia la Cinta Repartidora",
    "title": "Los paréntesis no son adorno",
    "intro": (
        "En la prensa aprendiste a mover números de sitio. Aquí no se mueve nada: se "
        "cambia qué va JUNTO con qué. Vas a ver por qué en la suma da igual y en la resta "
        "cambia el resultado, y qué hacer cuando quieres reagrupar de todas formas."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de abrir el horno. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $(2+3)+7$?",
                "answer": "12",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $(10-4)-3$ y $10-(4-3)$?",
                "options": [
                    {"id": "no", "text": "No"},
                    {"id": "yes", "text": "Sí"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "parentesis_son_decorativos"},
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Para qué sirven los paréntesis en una cuenta?",
                "options": [
                    {"id": "order", "text": "Para decir qué se calcula primero"},
                    {"id": "clarity", "text": "Solo para que se lea más claro"},
                    {"id": "decor", "text": "No sirven para nada, se pueden quitar"},
                ],
                "expected": "order",
                "misconception_by_option": {
                    "clarity": "parentesis_son_decorativos",
                    "decor": "parentesis_son_decorativos",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el Horno de Fundición",
        "title": "Las tandas del horno",
        "body": (
            "La segunda estación es un horno de crisol con tres carriles de carga. Los "
            "lingotes no entran de uno en uno: entran por TANDAS. El fundidor decide qué "
            "lingotes van juntos en cada tanda y en qué orden se funden las tandas.\n\n"
            "Con lingotes iguales daba igual cómo los agrupara, así que el fundidor dejó de "
            "pensarlo. Hoy le llegaron tres piezas donde una hay que RETIRAR del crisol, no "
            "añadirla. Agrupó como siempre, y la colada salió con un peso que no era el "
            "encargado."
        ),
        "question": "¿Cambiar qué va junto con qué puede cambiar el resultado?",
        "image": "/leccion/03-prealg-n3-fabrica/m02-asociativa-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "No: los paréntesis solo ordenan la lectura"},
                {"id": "b", "text": "Sí, en algunas operaciones"},
                {"id": "c", "text": "Sí, siempre cambia"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir en qué "
                "operaciones el fundidor puede agrupar a su gusto y en cuáles no."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Los mismos tres lingotes, dos agrupaciones",
        "body": (
            "Abajo están los mismos tres números agrupados de las dos formas posibles, "
            "primero con el horno sumando y después restando."
        ),
        "cases": [
            {
                "label": "Caso que confirma lo que esperas",
                "context": "Lingotes de 10, 4 y 3, todos entrando al crisol",
                "fraction": r"(10+4)+3\ \text{y}\ 10+(4+3)",
                "division": r"14+3=17\quad 10+7=17",
                "note": "Las dos agrupaciones dan la misma colada.",
            },
            {
                "label": "Caso que rompe la expectativa",
                "context": "Los mismos 10, 4 y 3, pero los dos últimos se RETIRAN del crisol",
                "fraction": r"(10-4)-3\ \text{y}\ 10-(4-3)",
                "division": r"6-3=3\quad 10-1=9",
                "note": "3 contra 9. Cambió qué iba con qué, y cambió la colada.",
            },
        ],
        "resolution": (
            "En la segunda, el paréntesis del centro decidió si el 3 se retiraba del crisol "
            "o se le devolvía al 4. Los paréntesis no describen la cuenta: la construyen. "
            "Cuando todas las piezas entran (suma, producto) da igual agrupar; cuando alguna "
            "sale (resta, división), no."
        ),
    },
    "definition_title": "La propiedad asociativa",
    "definition_katex": r"(a+b)+c=a+(b+c)\qquad (a\times b)\times c=a\times(b\times c)",
    "definition": (
        "Una operación es asociativa si cambiar la agrupación de tres números no cambia el "
        "resultado. La suma y la multiplicación lo son; la resta, la división y la "
        "potenciación no."
    ),
    "definition_symbols": [
        {
            "symbol": r"(\ )",
            "reads": "paréntesis",
            "means": "la tanda: lo que se funde junto y primero",
        },
        {
            "symbol": r"a,b,c",
            "reads": "tres operandos",
            "means": "hacen falta tres para que la agrupación signifique algo",
        },
        {
            "symbol": r"(a-b)-c\neq a-(b-c)",
            "reads": "la resta no asocia",
            "means": "el paréntesis decide de quién se resta c",
        },
        {
            "symbol": r"a-(b-c)=a-b+c",
            "reads": "quitar el paréntesis cambia signos",
            "means": "el signo de menos delante voltea todo lo de dentro",
        },
        {
            "symbol": r"a+(-b)+(-c)",
            "reads": "todo como suma",
            "means": "el truco: con cada número llevando su signo, sí puedes reagrupar",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Suma y multiplicación",
            "title": "La tanda que se puede rearmar",
            "statement": (
                "El horno debe fundir lingotes de 2, 5 y 19, sumando sus pesos. ¿Conviene "
                "alguna agrupación concreta?"
            ),
            "latex": r"(2+5)+19=2+(5+19)",
            "image_slot": False,
            "steps": [
                "Primera agrupación: (2 + 5) + 19 = 7 + 19 = 26.",
                "Segunda agrupación: 2 + (5 + 19) = 2 + 24 = 26.",
                "Coinciden, así que el fundidor puede armar las tandas como le convenga.",
                "Y le conviene: si hubiera un 8 y un 2, agruparlos primero da 10 y el resto sale solo.",
                "La asociativa no cambia el resultado; cambia cuánto trabajo cuesta llegar a él.",
            ],
            "solution": r"$(2+5)+19=2+(5+19)=26$",
            "self_explanation": {
                "step_index": 3,
                "prompt": "En el paso 4 se agrupa buscando un 10. ¿Por qué eso es legal aquí y no lo sería en una resta?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Resta convertida en suma",
            "title": "Cómo reagrupar una resta sin romperla",
            "statement": (
                "El horno debe procesar 30, retirar 7 y retirar 13. El fundidor quiere "
                "agrupar los dos retiros en una sola tanda. ¿Puede?"
            ),
            "latex": r"30-7-13=30+(-7)+(-13)",
            "image_slot": False,
            "steps": [
                "Tal cual está, la resta no asocia: no puedo escribir 30 − (7 − 13), eso daría 36.",
                "El truco es dejar de ver restas: cada retiro es una suma de un número negativo.",
                "30 − 7 − 13 = 30 + (−7) + (−13). Ahora TODO son sumas.",
                "Y la suma sí asocia: 30 + ((−7) + (−13)) = 30 + (−20) = 10.",
                "Agrupé los dos retiros en una sola tanda y el resultado se mantuvo: 10.",
            ],
            "solution": r"$30-7-13=10$, agrupando los retiros como $-20$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El fundidor que movió el paréntesis",
            "statement": (
                "El fundidor anota: «Encargo de 30, retirar 7 y retirar 13. Agrupo los dos "
                "retiros: 30 − (7 − 13) = 30 − (−6) = 36». Y funde 36."
            ),
            "latex": r"30-7-13=30-(7-13)",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"30-(7\;\underline{-}\;13)",
            "error_note": "Al meter el 13 dentro del paréntesis le cambió el signo sin darse cuenta: dejó de retirarse y pasó a sumarse.",
            "correct_version": {
                "wrong_latex": r"30-7-13=36",
                "right_latex": r"30-7-13=30-(7+13)=10",
                "rows": [
                    {
                        "wrong": "Los retiros se agrupan tal cual dentro del paréntesis",
                        "right": "Al agrupar bajo un menos, los retiros se SUMAN entre sí",
                    },
                    {
                        "wrong": "Retirar 7 y luego 13 deja más de lo que había",
                        "right": "Retirar dos veces siempre deja menos: 10, no 36",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 36 es imposible sin hacer ninguna cuenta? Escribe la agrupación correcta.",
            "steps": [
                "Sin calcular: se parte de 30 y se retira dos veces. El resultado TIENE que ser menor que 30.",
                "36 es mayor que 30, así que está mal antes de revisar la aritmética.",
                "La agrupación correcta es 30 − (7 + 13) = 30 − 20 = 10: bajo un signo menos, los dos retiros se suman.",
            ],
            "solution": (
                "Antes de mover un paréntesis en una resta, reescribe todo como sumas con "
                "signo. Es más largo de escribir y te ahorra el error entero: la suma sí "
                "asocia, siempre."
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
                "statement": "Agrupa para calcular rápido: lingotes de 37, 8 y 2, sumando.",
                "given_steps": [
                    r"37+(8+2)",
                    r"8+2=10",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"37+10=", "answer": "47"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "El horno procesa 50, retira 12 y retira 8. Agrupa los dos retiros.",
                "given_steps": [
                    r"50-12-8=50-(12+8)",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"12+8=", "answer": "20"},
                    {"id": "P2-b2", "label": r"50-20=", "answer": "30"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: el horno eleva. Calcula primero (2 elevado a 3) "
                    "elevado a 2 y comprueba si coincide con 2 elevado a (3 elevado a 2)."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"(2^{3})^{2}=", "answer": "64"},
                    {"id": "P3-b2", "label": r"2^{(3^{2})}=", "answer": "512"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma colada",
        "intro": r"¿Cuánto vale $80-25-15$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · De izquierda a derecha",
                "steps": [r"80-25=55", r"55-15=40"],
                "note": "Siempre funciona; es el orden en que está escrito.",
            },
            {
                "label": "Método 2 · Agrupar los retiros",
                "steps": [r"80-(25+15)", r"=80-40", r"=40"],
                "note": "Junta lo que se retira en una sola tanda.",
            },
        ],
        "question": "¿Por qué en el método 2 los retiros se SUMAN dentro del paréntesis, si en la cuenta original los dos eran restas?",
        "insight": (
            "Porque el signo menos de delante afecta a todo el paréntesis. Retirar 25 y "
            "luego retirar 15 es retirar 40 de una vez: los retiros se acumulan. Si "
            "escribieras 80 − (25 − 15) estarías diciendo otra cosa — que al 25 le "
            "devuelves 15 antes de retirarlo — y daría 70."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "Agrupa para calcular rápido: 46 + 7 + 3. ¿Cuánto da?",
            "expr": r"46+(7+3)",
            "answer": "56",
            "hints": {
                "n1": "¿Qué dos números juntos dan un número redondo?",
                "n2": "7 + 3 = 10.",
                "n3": "46 + 10 = …",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "El horno procesa 90, retira 34 y retira 26. ¿Cuánto queda?",
            "expr": r"90-34-26",
            "answer": "30",
            "hints": {
                "n1": "Los dos retiros se pueden juntar en uno solo.",
                "n2": "34 + 26 = 60.",
                "n3": "90 − 60 = …",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": r"¿Cuánto vale $12-(5-4)$?",
            "expr": r"12-(5-4)",
            "answer": "11",
            "hints": {
                "n1": "Lo de dentro del paréntesis va primero.",
                "n2": "5 − 4 = 1.",
                "n3": "12 − 1 = …",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": r"Un fundidor anota «$60-15-5=60-(15-5)=50$». ¿Dónde está el error?",
            "options": [
                {
                    "id": "sign",
                    "text": "Al agrupar bajo un menos, los retiros se suman: es 60 − 20 = 40",
                },
                {"id": "arith", "text": "Se equivocó al restar: 60 − 10 son 40"},
                {"id": "order", "text": "Debía calcular de derecha a izquierda"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "sign",
            "feedback_by_option": {
                "sign": "correct",
                "arith": "fb_m02_e4_arith",
                "order": "fb_m02_e4_order",
                "none": "fb_m02_e4_none",
            },
            "misconception_by_option": {
                "arith": "error_de_calculo_no_de_agrupacion",
                "order": "invierte_el_sentido_de_lectura",
                "none": "parentesis_son_decorativos",
            },
            "hints": {
                "n1": "Calcula la cuenta original sin paréntesis y compara.",
                "n2": "60 − 15 = 45, y 45 − 5 = 40.",
                "n3": "El paréntesis convirtió el segundo retiro en una devolución.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «Para cualesquiera $a,b,c$: $(a-b)-c=a-(b-c)$.»",
            "options": [
                {"id": "false_c_zero", "text": "Falsa: solo coinciden cuando c = 0"},
                {"id": "true", "text": "Verdadera: los paréntesis no cambian el resultado"},
                {"id": "false_never", "text": "Falsa: nunca pueden coincidir"},
                {"id": "true_positive", "text": "Verdadera si los tres son positivos"},
            ],
            "expected": "false_c_zero",
            "feedback_by_option": {
                "false_c_zero": "correct",
                "true": "fb_m02_e5_trap",
                "false_never": "fb_m02_e5_never",
                "true_positive": "fb_m02_e5_positive",
            },
            "misconception_by_option": {
                "true": "parentesis_son_decorativos",
                "false_never": "olvida_el_caso_neutro",
                "true_positive": "parentesis_son_decorativos",
            },
            "hints": {
                "n1": "Para tumbar un «cualesquiera» basta UN caso.",
                "n2": "Prueba con a = 10, b = 4, c = 3.",
                "n3": "(10−4)−3 = 3 pero 10−(4−3) = 9. ¿Y si c fuera 0?",
            },
        },
        {
            "id": "E6",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": ("Agrupa para calcular de cabeza: 4 × 23 × 25. ¿Cuánto da?"),
            "expr": r"(4\times 25)\times 23",
            "answer": "2300",
            "hints": {
                "n1": "La multiplicación sí asocia: agrupa lo que te convenga.",
                "n2": "4 × 25 = 100.",
                "n3": "100 × 23 = …",
            },
        },
        {
            "id": "E7",
            "kind": "single_select",
            "tipo": "transferencia",
            "prompt": r"¿Cuál de estas reescrituras de $a-b-c$ es correcta?",
            "options": [
                {"id": "sum_group", "text": "a − (b + c)", "latex": r"a-(b+c)"},
                {"id": "diff_group", "text": "a − (b − c)", "latex": r"a-(b-c)"},
                {"id": "plus", "text": "a + (b + c)", "latex": r"a+(b+c)"},
                {"id": "swap", "text": "c − b − a", "latex": r"c-b-a"},
            ],
            "expected": "sum_group",
            "feedback_by_option": {
                "sum_group": "correct",
                "diff_group": "fb_m02_e7_diff",
                "plus": "fb_m02_e7_plus",
                "swap": "fb_m02_e7_swap",
            },
            "misconception_by_option": {
                "diff_group": "parentesis_son_decorativos",
                "plus": "ignora_el_signo_al_agrupar",
                "swap": "todas_las_operaciones_son_conmutativas",
            },
            "hints": {
                "n1": "Prueba las cuatro con a = 10, b = 4, c = 3.",
                "n2": "La original da 10 − 4 − 3 = 3.",
                "n3": "Solo una de las cuatro da 3 también.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "Validez a lo largo de las operaciones",
        "title": "¿En qué operaciones da igual cómo se agrupe?",
        "intro": "Misma escalera que en la prensa: las seis operaciones de la ciudad, otra pregunta.",
        "rows": [
            {
                "symbol": r"+",
                "name": "Suma",
                "closed": "yes",
                "latex": r"(10+4)+3=10+(4+3)",
                "note": "Todas las piezas entran al crisol: el orden de las tandas no importa.",
            },
            {
                "symbol": r"-",
                "name": "Resta",
                "closed": "no",
                "latex": r"(10-4)-3=3\neq 9=10-(4-3)",
                "note": "El paréntesis decide de quién se resta. Truco: reescribir todo como sumas con signo.",
            },
            {
                "symbol": r"\times",
                "name": "Multiplicación",
                "closed": "yes",
                "latex": r"(4\times 25)\times 23=4\times(25\times 23)",
                "note": "Por eso puedes buscar el par de factores cómodo antes de multiplicar.",
            },
            {
                "symbol": r"\div",
                "name": "División",
                "closed": "no",
                "latex": r"(24\div 6)\div 2=2\neq 8=24\div(6\div 2)",
                "note": "Mismo problema que la resta, y el truco es el mismo: pasar a multiplicar por el inverso.",
            },
            {
                "symbol": r"a^{n}",
                "name": "Potenciación",
                "closed": "no",
                "latex": r"(2^{3})^{2}=64\neq 512=2^{(3^{2})}",
                "note": "Por eso una torre de exponentes se lee de arriba abajo, no de izquierda a derecha.",
            },
            {
                "symbol": r"\sqrt[n]{a}",
                "name": "Radicación",
                "closed": "no",
                "latex": r"\sqrt{\sqrt{256}}=\sqrt[4]{256}=4",
                "note": "Tampoco asocia: el orden en que se anidan las raíces decide el índice final, así que cambiar el agrupamiento cambia el resultado.",
            },
        ],
        "outro": (
            "Las mismas dos que aguantaban el intercambio aguantan la reagrupación, y no es "
            "casualidad: son las que juntan sin distinguir papeles. En la Cinta Repartidora "
            "vas a ver qué pasa cuando se mezclan DOS operaciones distintas."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"(2+5)+19", r"30-7-13", r"30-(7-13)"],
        "options": [
            {
                "id": "grouping",
                "text": "En los tres cambia qué número va junto con cuál",
                "correct": True,
            },
            {
                "id": "same",
                "text": "En los tres el resultado no cambia al reagrupar",
                "correct": False,
            },
            {
                "id": "three",
                "text": "Los tres necesitan al menos tres números para tener sentido",
                "correct": True,
            },
            {
                "id": "order",
                "text": "En los tres se intercambian dos números de sitio",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "El horno recibe una colada de 120, tiene que retirar 45 y retirar otros 35. "
            "El fundidor quiere hacerlo en una sola tanda de retiro. ¿Cuánto queda?"
        ),
        "polya": {
            "comprender": "Parto de 120 y hago dos retiros. Me piden el resultado agrupando los retiros.",
            "planear": "Bajo un signo menos, los retiros se suman entre sí: 120 − (45 + 35).",
            "ejecutar": "45 + 35 = 80 → 120 − 80 = 40.",
            "comprobar": "Paso a paso: 120 − 45 = 75, y 75 − 35 = 40. Coincide.",
        },
        "prompt": "¿Cuánto queda en el crisol?",
        "answer": "40",
        "hints": {
            "n1": "Los dos retiros se pueden juntar en uno solo.",
            "n2": "Bajo el menos, se suman: 45 + 35 = 80.",
            "n3": "120 − 80 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya lees el paréntesis como parte de la cuenta, no como adorno.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo qué le pasa a un "
            "número cuando entra o sale de un paréntesis precedido de menos."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $(4+6)+11$?",
                "answer": "21",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Dan lo mismo $(20-8)-5$ y $20-(8-5)$?",
                "options": [
                    {"id": "no", "text": "No"},
                    {"id": "yes", "text": "Sí"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "parentesis_son_decorativos"},
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Es verdadera? $(3\times 4)\times 5=3\times(4\times 5)$",
                "options": [
                    {"id": "true", "text": "Verdadera"},
                    {"id": "false", "text": "Falsa"},
                ],
                "expected": "true",
                "misconception_by_option": {"false": "sobregeneraliza_asociativa"},
                # Caso donde la agrupación SÍ da igual: comprueba que aprendió el
                # criterio y no la heurística "los paréntesis siempre cambian todo".
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
        "default": "Calcula lo de dentro del paréntesis primero y compara con la cuenta original.",
        "fb_m02_e4_arith": (
            "60 − 10 sí da 50; la aritmética no es el problema. → Calcula 60 − 15 − 5 tal "
            "como está escrito y compara."
        ),
        "fb_m02_e4_order": (
            "El sentido de lectura no cambia nada aquí. → Fíjate en qué le pasó al 5 al "
            "entrar en el paréntesis."
        ),
        "fb_m02_e4_none": (
            "Calcula la cuenta original sin tocar nada: 60 − 15 − 5. → Di cuánto da y "
            "compáralo con 50."
        ),
        "fb_m02_e5_trap": (
            "Eso vale para la suma y el producto, no para la resta. → Prueba con "
            "a = 10, b = 4, c = 3."
        ),
        "fb_m02_e5_never": (
            "Casi: fallan casi siempre, pero hay un caso donde coinciden. → Prueba con c = 0."
        ),
        "fb_m02_e5_positive": (
            "10, 4 y 3 son los tres positivos y aun así falla. → Calcula las dos "
            "agrupaciones con esos números."
        ),
        "fb_m02_e7_diff": (
            "Esa es exactamente la trampa del fundidor. → Prueba las dos con a = 10, b = 4, c = 3."
        ),
        "fb_m02_e7_plus": (
            "Cambiaste el menos de delante por un más: eso suma lo que había que retirar. "
            "→ Compara los resultados con a = 10, b = 4, c = 3."
        ),
        "fb_m02_e7_swap": (
            "Eso reordena los números, que es la propiedad de la estación anterior, y "
            "además en una resta no vale. → Busca la que solo reagrupa."
        ),
    },
    "closing": (
        "Los paréntesis construyen la cuenta. Suma y producto dejan reagrupar; resta y "
        "división no, salvo que reescribas todo como sumas con signo. En la Cinta "
        "Repartidora se mezclan dos operaciones distintas a la vez."
    ),
    "validation_status": "F3_M02_11bloques",
}
