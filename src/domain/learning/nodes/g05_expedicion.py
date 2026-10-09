"""G05 · La sala de expedición — elegir el molde, y no parar en el primero.

Quinta y última sala del Almacén de la caravana (Casa de la Sabiduría, Bagdad).
Guía: Salim. Vocabulario propio: expedición, guía de carga, precinto, remesa,
ruta, sello de salida. Nada de fardos ni básculas (G01), huellas ni calcos (G02),
despiece ni muescas (G03), toneles ni duelas (G04).

Error focal: parar en el primer molde que funciona. Una factorización puede ser
correcta y estar sin terminar, y el sitio donde eso duele es aquí, donde ya no
hay una sala que diga qué método toca.

**Este nodo existe para llenar un hueco medido en el banco de ítems.** Sobre los
4 656 enunciados extraídos de Hipertexto, Caminos y EPA8 hay CERO ítems de
decisión de método y CERO de control sin calcular, y no es un descuido: el índice
del libro ya responde la pregunta —todo lo de la página 108 es diferencia de
cuadrados— así que el estudiante nunca elige. Elegir es lo que falla en un examen.
La práctica de esta sala está escrita a mano con esos tipos, apoyada en los 46
ítems de `u5_factorizacion_completa_p127`, que sí piden encadenar casos.
"""

NODE_ID = "ALG-N3-G05-EXPEDICION"
CONCEPT_SLUG = "factorizacion_completa"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "factorizacion_completa",
    "misconception": "se_queda_en_el_primer_caso",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La sala de expedición · Factorización completa",
    "house": "La sala de expedición",
    "guide": "Salim",
    "finish_label": "Cerrar el almacén de la caravana",
    "title": "Las remesas salen sin etiqueta, y hay un orden para abrirlas",
    "intro": (
        "Hasta ahora cada sala te decía qué molde usar: en el cotejo se cotejaba, en la mesa "
        "se despiezaba. Aquí llegan remesas mezcladas y sin etiqueta. Lo único que hay que "
        "decidir es por dónde empezar — y cuándo parar."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de firmar la primera guía. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Qué tienen en común los términos de $12mx^{2}-12m$?",
                "options": [
                    {"id": "both", "text": r"Un 12 y una $m$"},
                    {"id": "num", "text": "Solo el 12"},
                    {"id": "none", "text": "Nada"},
                ],
                "expected": "both",
                "misconception_by_option": {
                    "num": "factor_comun_incompleto",
                    "none": "factor_comun_incompleto",
                },
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es la factorización de $x^{2}-1$?",
                "options": [
                    {"id": "ok", "text": r"$(x+1)(x-1)$", "latex": r"(x+1)(x-1)"},
                    {"id": "sq", "text": r"$(x-1)^{2}$", "latex": r"(x-1)^{2}"},
                    {"id": "none", "text": "No se puede"},
                ],
                "expected": "ok",
                "misconception_by_option": {
                    "sq": "confunde_diferencia_con_cuadrado_perfecto",
                    "none": "suma_de_cuadrados_es_factorizable",
                },
            },
            {
                "id": "D3",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"¿En cuántos factores queda $x^{2}-9$ una vez abierto del todo?",
                "answer": "2",
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/07-alg-n3-caravana/g05-expedicion-katia.png",
        "eyebrow": "KatIA · En la sala de expedición",
        "title": "La guía que se firmó con la carga a medias",
        "body": (
            "En la sala de expedición se precinta lo que sale. Cada remesa lleva una guía de "
            "carga donde se anota en cuántos bultos quedó dividida, y una vez sellada no se "
            "vuelve a abrir.\n\n"
            "Salim deja una guía sobre el mostrador:\n\n"
            "«Salía la remesa $12mx^{2}-12m$. El mozo vio dos términos que restaban, aplicó "
            "el cotejo de huellas y anotó dos bultos. Firmó y precintó.»\n\n"
            "«Antes había un 12 y una eme en los dos términos que nadie sacó. La remesa "
            "llegó a destino en dos bultos cuando eran tres, y hubo que romper el precinto.»"
        ),
        "question": (
            "Si la factorización que anotó el mozo era correcta, ¿por qué la guía estaba mal?"
        ),
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que más se acerque a lo que crees. Cualquiera vale.",
            "options": [
                {"id": "orden", "text": "Porque había que empezar por otro molde"},
                {"id": "falsa", "text": "Porque la factorización que anotó era falsa"},
                {"id": "parar", "text": "Porque paró antes de tiempo, aunque no se equivocara"},
            ],
            "response": (
                "Guarda tu respuesta. Al final vas a tener un orden fijo para abrir cualquier "
                "remesa, y una señal para saber cuándo se puede precintar."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Siempre se empieza por lo mismo",
        "body": (
            "Cuando una remesa admite varios moldes, el orden no da igual: hay uno que "
            "conviene siempre primero, porque simplifica todo lo que viene detrás."
        ),
        "cases": [
            {
                "label": "Empezando por el molde llamativo",
                "context": r"$12mx^{2}-12m$ tratado como diferencia de cuadrados",
                "fraction": r"12m(x^{2}-1)\ \text{no se vio}",
                "division": r"\text{2 bultos, y quedaba carga suelta}",
                "note": (
                    "Los términos no son cuadrados exactos —12m no lo es—, así que el molde "
                    "ni siquiera aplicaba tal cual."
                ),
            },
            {
                "label": "Empezando por el factor común",
                "context": r"Primero se saca lo común, después se coteja",
                "fraction": r"12m(x^{2}-1)=12m(x+1)(x-1)",
                "division": r"\text{3 bultos}",
                "note": (
                    "Al sacar el 12m, lo que queda dentro es limpio y el molde se reconoce "
                    "de un vistazo."
                ),
            },
        ],
        "resolution": (
            "El factor común va SIEMPRE primero. Después se mira cuántos términos quedan: con "
            "dos, diferencia de cuadrados o de cubos; con tres, cuadrado perfecto o trinomio "
            "general; con cuatro, agrupación. Y al terminar cada paso se vuelve a mirar cada "
            "trozo, porque un trozo puede volver a abrirse."
        ),
    },
    "definition_title": "Factorización completa",
    "definition_katex": (
        r"\text{común}\ \rightarrow\ \text{contar términos}\ \rightarrow\ "
        r"\text{molde}\ \rightarrow\ \text{repetir en cada trozo}"
    ),
    "definition": (
        "Factorizar COMPLETAMENTE es repetir el proceso hasta que ningún factor se pueda "
        "abrir más. La ruta:\n\n"
        "1. Sacar el factor común, si lo hay.\n"
        "2. Contar los términos de lo que queda: 2 → cuadrados o cubos · 3 → cuadrado "
        "perfecto o trinomio general · 4 → agrupación.\n"
        "3. Volver al paso 1 con cada factor obtenido.\n\n"
        "Se para cuando todos los factores son irreducibles. El resultado no depende del "
        "camino elegido."
    ),
    "definition_symbols": [
        {
            "symbol": r"12m(x+1)(x-1)",
            "reads": "doce eme, por equis más uno, por equis menos uno",
            "means": "tres bultos: el común y los dos del molde",
        },
        {
            "symbol": r"5m^{4}+5m=5m(m^{3}+1)",
            "reads": "cinco eme a la cuarta más cinco eme",
            "means": "sacar el común deja a la vista una suma de cubos",
        },
        {
            "symbol": r"5m(m+1)(m^{2}-m+1)",
            "reads": "cinco eme por eme más uno por eme cuadrado menos eme más uno",
            "means": "la misma remesa terminada: tres factores",
        },
        {
            "symbol": r"x^{2}+4",
            "reads": "equis cuadrado más cuatro",
            "means": "un factor irreducible: aquí se para",
        },
        {
            "symbol": r"1-n^{6}",
            "reads": "uno menos ene a la sexta",
            "means": "cuadrados y cubos a la vez: cuatro factores al final",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Común primero, molde después",
            "title": "Tres bultos, no dos",
            "statement": "Salim expide la remesa $12mx^{2}-12m$. ¿En cuántos bultos sale?",
            "latex": r"12mx^{2}-12m",
            "image_slot": False,
            "steps": [
                "Paso 1, factor común: MCD(12, 12) = 12 y la m está en los dos → 12m.",
                "Queda 12m(x² − 1).",
                "Paso 2, cuento términos dentro: dos, y restan.",
                "¿Cuadrados exactos? x² y 1. Sí → (x + 1)(x − 1).",
                "Paso 3, reviso cada trozo: 12m es un monomio y los dos binomios no se abren. Tres bultos: 12m(x + 1)(x − 1).",
            ],
            "solution": r"$12mx^{2}-12m=12m(x+1)(x-1)$",
            "self_explanation": {
                "step_index": 0,
                "prompt": (
                    "¿Por qué conviene sacar el factor común ANTES de mirar qué molde aplica, "
                    "y no después?"
                ),
            },
        },
        {
            "eyebrow": "Ejemplo 2 · El común destapa el molde",
            "title": "Lo que aparece al quitar de encima",
            "statement": ("Otra remesa: $5m^{4}+5m$. Tal como viene no encaja en ningún molde."),
            "latex": r"5m^{4}+5m",
            "image_slot": False,
            "steps": [
                "Tal cual: dos términos que suman, pero m⁴ y m no son ni cuadrados ni cubos exactos.",
                "Paso 1, factor común: 5 y la menor potencia de m, o sea 5m.",
                "Queda 5m(m³ + 1).",
                "Ahora sí: m³ y 1 son cubos exactos. Suma de cubos → (m + 1)(m² − m + 1).",
                "Tres bultos: 5m(m + 1)(m² − m + 1). El común no era un trámite: era lo que dejaba ver el molde.",
            ],
            "solution": r"$5m^{4}+5m=5m(m+1)(m^{2}-m+1)$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El mozo que precintó demasiado pronto",
            "statement": (
                "Vuelve la remesa de la apertura. El mozo saca el común, aplica un molde y "
                "firma la guía:"
            ),
            "latex": r"5m^{5}-40m^{3}+80m",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"5m^{5}-40m^{3}+80m=5m(m^{4}-8m^{2}+16)",
            "error_note": (
                "El factor común está completo y la igualdad es cierta. Pero dentro del "
                "paréntesis hay un trinomio cuadrado perfecto sin abrir."
            ),
            "correct_version": {
                "wrong_latex": r"5m(m^{4}-8m^{2}+16)",
                "right_latex": r"5m(m+2)^{2}(m-2)^{2}",
                "rows": [
                    {
                        "wrong": "Saqué el común: ya está",
                        "right": "Después del común hay que contar términos y volver a mirar",
                    },
                    {
                        "wrong": "Dos bultos",
                        "right": "Tres, y dos de ellos van al cuadrado",
                    },
                ],
            },
            "explain_prompt": (
                "Sigue abriendo el paréntesis y di en cuántos bultos sale la remesa de verdad."
            ),
            "steps": [
                "Dentro hay tres términos: m⁴ − 8m² + 16.",
                "Extremos: (m²)² y 4². Doble producto: 2 · m² · 4 = 8m² ✓. Es cuadrado perfecto: (m² − 4)².",
                "Y m² − 4 es diferencia de cuadrados: (m + 2)(m − 2).",
                "Queda 5m(m + 2)²(m − 2)². Regla: después de cada paso, vuelve a mirar cada trozo.",
            ],
            "solution": (
                "5m⁵ − 40m³ + 80m = 5m(m + 2)²(m − 2)². Correcto y sin terminar no es lo "
                "mismo que terminado."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "La guía de carga va empezada; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Factoriza completamente $3x^{2}-27$.",
                "given_steps": [r"\text{común}: 3", r"3(x^{2}-9)"],
                "blanks": [
                    {
                        "id": "P1-b1",
                        "label": r"\text{número de factores al terminar}=",
                        "answer": "3",
                    }
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Factoriza completamente $2x^{3}+16$.",
                "given_steps": [r"\text{común}: 2\ \Rightarrow\ 2(x^{3}+8)"],
                "blanks": [
                    {"id": "P2-b1", "label": r"\sqrt[3]{8}=", "answer": "2"},
                    {"id": "P2-b2", "label": r"\text{términos del segundo factor}=", "answer": "3"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: $1-n^{6}$. Decide por qué molde empezar y di "
                    "cuántos factores quedan al final."
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{número de factores finales}=", "answer": "4"}
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos órdenes para abrir la misma remesa",
        "intro": r"$3x^{2}-27$. Los dos llegan a lo mismo; uno cuesta más.",
        "methods": [
            {
                "label": "Método 1 · Molde primero",
                "steps": [
                    r"3x^{2}-27\ \text{¿diferencia de cuadrados?}",
                    r"3x^{2}\ \text{no es cuadrado exacto}",
                    r"\text{hay que volver atrás y sacar el }3",
                ],
                "note": "Se pierde un paso descartando un molde que sí aplicaba, pero después.",
            },
            {
                "label": "Método 2 · Común primero",
                "steps": [
                    r"3(x^{2}-9)",
                    r"x^{2}\ \text{y}\ 9\ \text{sí son cuadrados}",
                    r"3(x+3)(x-3)",
                ],
                "note": "El común deja lo de dentro limpio y el molde se reconoce enseguida.",
            },
        ],
        "question": "¿Por qué el factor común va siempre primero, aunque no sea obligatorio?",
        "insight": (
            "Porque los moldes exigen formas exactas —cuadrados, cubos— y un coeficiente de "
            "más las estropea. 3x² − 27 no es diferencia de cuadrados; x² − 9 sí lo es, y es "
            "la misma remesa con el 3 fuera. Sacar el común no es un trámite previo: es lo "
            "que hace visible el molde. Por eso el orden no es una costumbre, es lo que "
            "evita descartar un caso que sí aplicaba."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    # Tipos que el banco NO tiene: decisión de método (E1, E7), control sin
    # calcular (E3, E4), parámetro (E2) y contraejemplo (E6).
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": (r"Para factorizar $18x^{3}-2x$, ¿por qué molde hay que EMPEZAR?"),
            "options": [
                {"id": "comun", "text": "Factor común"},
                {"id": "cuadrados", "text": "Diferencia de cuadrados"},
                {"id": "cubos", "text": "Diferencia de cubos"},
                {"id": "trinomio", "text": "Trinomio general"},
            ],
            "expected": "comun",
            "feedback_by_option": {
                "comun": "correct",
                "cuadrados": "fb_g05_e1_cuad",
                "cubos": "fb_g05_e1_cubos",
                "trinomio": "fb_g05_e1_tri",
            },
            "misconception_by_option": {
                "cuadrados": "no_saca_el_factor_comun_primero",
                "cubos": "no_saca_el_factor_comun_primero",
                "trinomio": "cuenta_mal_los_terminos",
            },
            "hints": {
                "n1": "Antes de mirar la forma, mira si los términos comparten algo.",
                "n2": "18 y 2 comparten un 2; x³ y x comparten una x.",
                "n3": "Sacando 2x queda 2x(9x² − 1), y ahí sí se ve el molde.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (r"Al factorizar completamente $12mx^{2}-12m$, ¿en cuántos factores queda?"),
            "expr": r"12m(x+1)(x-1)",
            "answer": "3",
            "hints": {
                "n1": "Primero el factor común.",
                "n2": "Queda 12m(x² − 1), y lo de dentro se vuelve a abrir.",
                "n3": "El común cuenta como uno de los factores.",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": (
                r"Sin factorizar: $x^{6}-1$ es a la vez diferencia de cuadrados y de cubos. "
                "¿En cuántos factores queda al abrirlo del todo?"
            ),
            "expr": r"(x+1)(x^{2}-x+1)(x-1)(x^{2}+x+1)",
            "answer": "4",
            "hints": {
                "n1": "Empieza por cuadrados: (x³ + 1)(x³ − 1).",
                "n2": "Cada uno de esos dos es una suma o diferencia de cubos.",
                "n3": "Cada uno se parte en dos: 2 × 2.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": (r"Sin hacer ninguna cuenta: ¿cuál de estas remesas NO se puede abrir más?"),
            "options": [
                {"id": "irred", "text": r"$x^{2}+4$", "latex": r"x^{2}+4"},
                {"id": "dif", "text": r"$x^{2}-4$", "latex": r"x^{2}-4"},
                {"id": "comun", "text": r"$2x^{2}+8x$", "latex": r"2x^{2}+8x"},
                {"id": "cubo", "text": r"$x^{3}+8$", "latex": r"x^{3}+8"},
            ],
            "expected": "irred",
            "feedback_by_option": {
                "irred": "correct",
                "dif": "fb_g05_e4_dif",
                "comun": "fb_g05_e4_comun",
                "cubo": "fb_g05_e4_cubo",
            },
            "misconception_by_option": {
                "dif": "suma_de_cuadrados_es_factorizable",
                "comun": "no_saca_el_factor_comun_primero",
                "cubo": "cree_que_ninguna_suma_se_factoriza",
            },
            "hints": {
                "n1": "Mira una por una: ¿tiene factor común? ¿cae en algún molde?",
                "n2": "La suma de cuadrados es el hueco del catálogo.",
                "n3": "La suma de CUBOS sí se abre; la de cuadrados no.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (
                r"Un mozo anota $5m^{5}-40m^{3}+80m=5m(m^{4}-8m^{2}+16)$ y precinta. ¿Está "
                "terminado?"
            ),
            "options": [
                {
                    "id": "no",
                    "text": r"No: lo de dentro es cuadrado perfecto y se abre dos veces más",
                },
                {"id": "yes", "text": "Sí: el factor común está completo"},
                {"id": "wrong", "text": "No: el factor común debería ser 5m³"},
                {"id": "err", "text": "No: la igualdad es falsa"},
            ],
            "expected": "no",
            "feedback_by_option": {
                "no": "correct",
                "yes": "fb_g05_e5_yes",
                "wrong": "fb_g05_e5_wrong",
                "err": "fb_g05_e5_err",
            },
            "misconception_by_option": {
                "yes": "se_queda_en_el_primer_caso",
                "wrong": "factor_comun_incompleto",
                "err": "se_queda_en_el_primer_caso",
            },
            "hints": {
                "n1": "El factor común está bien. Cuenta los términos de lo que quedó dentro.",
                "n2": "Son tres: extremos cuadrados y doble producto 2 · m² · 4 = 8m² ✓.",
                "n3": "(m² − 4)², y m² − 4 todavía se abre.",
            },
        },
        {
            "id": "E6",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": (
                "¿Verdadera o falsa? «Si al multiplicar los factores vuelve a salir la remesa "
                "original, la guía se puede precintar.»"
            ),
            "options": [
                {
                    "id": "false",
                    "text": r"Falsa: $5m(m^{4}-8m^{2}+16)$ lo cumple y no está terminada",
                },
                {"id": "true", "text": "Verdadera: si la igualdad es cierta, está terminada"},
                {
                    "id": "true_comun",
                    "text": "Verdadera siempre que se haya sacado el factor común",
                },
                {
                    "id": "false_never",
                    "text": "Falsa: multiplicar de vuelta nunca sirve de nada",
                },
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_g05_e6_trap",
                "true_comun": "fb_g05_e6_comun",
                "false_never": "fb_g05_e6_never",
            },
            "misconception_by_option": {
                "true": "se_queda_en_el_primer_caso",
                "true_comun": "se_queda_en_el_primer_caso",
                "false_never": "cuenta_mal_los_terminos",
            },
            "hints": {
                "n1": "Es la misma lección del pesaje de entrada, ahora sobre toda la cadena.",
                "n2": "Una factorización incompleta también cumple la igualdad.",
                "n3": "La señal de parar no es que multiplique bien: es que ningún factor se abra.",
            },
        },
        {
            "id": "E7",
            "kind": "multi_select",
            "tipo": "transferencia",
            "prompt": (
                "Cuatro remesas sin etiqueta. ¿En cuáles hay que sacar factor común ANTES de "
                "aplicar ningún molde? Marca todas las que apliquen."
            ),
            "options": [
                {"id": "ok1", "text": r"$3x^{2}-27$"},
                {"id": "ok2", "text": r"$2x^{3}+16$"},
                {"id": "no1", "text": r"$x^{2}-49$"},
                {"id": "no2", "text": r"$x^{2}+10x+25$"},
            ],
            "expected": ["ok1", "ok2"],
            "valid_options": ["ok1", "ok2", "no1", "no2"],
            "trap_options": ["no1", "no2"],
            "feedback_by_option": {"ok1": "correct", "ok2": "correct"},
            "misconception_by_option": {
                "no1": "cuenta_mal_los_terminos",
                "no2": "cuenta_mal_los_terminos",
            },
            "hints": {
                "n1": "Mira si los términos comparten un número o una letra.",
                "n2": "En x² − 49 los coeficientes son 1 y 49: no comparten nada.",
                "n3": "Son dos de las cuatro.",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Por dónde se empieza?",
        "title": "La ruta de expedición",
        "intro": (
            "Cada fila es una remesa sin etiqueta. La pregunta no es en qué se factoriza: es "
            "qué se hace PRIMERO."
        ),
        "rows": [
            {
                "name": "Hay factor común",
                "symbol": r"3x^{2}-27",
                "latex": r"3(x+3)(x-3)",
                "closed": "yes",
                "note": "Común primero, siempre. Sin el 3 fuera no hay cuadrados exactos.",
            },
            {
                "name": "El común destapa el molde",
                "symbol": r"5m^{4}+5m",
                "latex": r"5m(m+1)(m^{2}-m+1)",
                "closed": "yes",
                "note": "Tal cual no encajaba en nada; con 5m fuera aparece una suma de cubos.",
            },
            {
                "name": "No hay común: contar términos",
                "symbol": r"x^{2}+10x+25",
                "latex": r"(x+5)^{2}",
                "closed": "yes",
                "note": "Tres términos → cuadrado perfecto o trinomio general. Se decide ahí.",
            },
            {
                "name": "Cuatro términos",
                "symbol": r"ax+ay+bx+by",
                "latex": r"(x+y)(a+b)",
                "closed": "yes",
                "note": "Cuatro términos y sin común → agrupación.",
            },
            {
                "name": "Cabe en dos moldes",
                "symbol": r"x^{6}-1",
                "latex": r"(x+1)(x^{2}-x+1)(x-1)(x^{2}+x+1)",
                "closed": "partial",
                "note": (
                    "Cuadrados y cubos a la vez. Los dos caminos llegan al mismo sitio —la "
                    "factorización completa es única— pero empezando por cuadrados se llega "
                    "antes."
                ),
            },
            {
                "name": "Ya no se abre",
                "symbol": r"x^{2}+4",
                "latex": r"\text{irreducible}",
                "closed": "no",
                "note": "Sin común, dos términos que suman y son cuadrados: aquí se precinta.",
            },
        ],
        "outro": (
            "La ruta en una línea: **común primero, después cuenta los términos, y al "
            "terminar vuelve a mirar cada trozo.** Se precinta cuando ningún factor se abre, "
            "no cuando la multiplicación cuadra."
        ),
    },
    "abstraction_question": {
        "prompt": (
            "Las tres remesas se abren con moldes distintos. ¿Qué tienen en común los tres "
            "primeros pasos?"
        ),
        "thumbnails": [
            r"3x^{2}-27=3(x+3)(x-3)",
            r"5m^{4}+5m=5m(m+1)(m^{2}-m+1)",
            r"2x^{2}+8x=2x(x+4)",
        ],
        "options": [
            {
                "id": "comun",
                "text": (
                    "En las tres se saca primero el factor común, y solo después se decide "
                    "el molde"
                ),
                "correct": True,
            },
            {
                "id": "dos",
                "text": "En las tres el resultado tiene exactamente dos factores",
                "correct": False,
            },
            {
                "id": "cuadrados",
                "text": "En las tres se aplica diferencia de cuadrados",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "C1",
        "statement": (
            "Salim expide la remesa $2x^{4}-32$. ¿En cuántos factores queda al abrirla del " "todo?"
        ),
        "polya": [
            "Entender: hay que factorizar completamente y contar los factores.",
            "Planear: común primero, después contar términos y repetir en cada trozo.",
            "Ejecutar: 2(x⁴ − 16) = 2(x² + 4)(x² − 4) = 2(x² + 4)(x + 2)(x − 2).",
            "Comprobar: x² + 4 es suma de cuadrados, irreducible. Cuatro factores.",
        ],
        "prompt": "¿En cuántos factores queda?",
        "answer": "4",
        "hints": {
            "n1": "Saca el 2 primero.",
            "n2": "Queda x⁴ − 16, que es diferencia de cuadrados.",
            "n3": "De los dos trozos, solo x² − 4 se vuelve a abrir; x² + 4 no.",
        },
    },
    # --- Bloque 10 · Post-diagnóstico y footer --------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres, ahora que tienes la ruta.",
        "trigger_refuerzo": True,
        "resultados": True,
        "outcome_gain": "Avance: ya decides el orden y sabes cuándo se puede precintar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo el orden de los "
            "moldes antes de cerrar el almacén."
        ),
        "items": [
            {
                "id": "Q1",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"En $8ax^{2}-8a$, ¿qué se hace primero?",
                "options": [
                    {"id": "comun", "text": "Sacar el factor común 8a"},
                    {"id": "cuad", "text": "Aplicar diferencia de cuadrados"},
                    {"id": "nada", "text": "No se puede factorizar"},
                ],
                "expected": "comun",
                "misconception_by_option": {
                    "cuad": "no_saca_el_factor_comun_primero",
                    "nada": "se_queda_en_el_primer_caso",
                },
            },
            {
                "id": "Q2",
                "kind": "single_select",
                "tipo": "postdiagnostico",
                "prompt": r"¿Cuál de estas NO se puede abrir más?",
                "options": [
                    {"id": "irred", "text": r"$x^{2}+9$", "latex": r"x^{2}+9"},
                    {"id": "dif", "text": r"$x^{2}-9$", "latex": r"x^{2}-9"},
                    {"id": "cubo", "text": r"$x^{3}+27$", "latex": r"x^{3}+27"},
                ],
                "expected": "irred",
                "misconception_by_option": {
                    "dif": "suma_de_cuadrados_es_factorizable",
                    "cubo": "cree_que_ninguna_suma_se_factoriza",
                },
            },
            {
                "id": "Q3",
                "kind": "numeric",
                "tipo": "postdiagnostico",
                "prompt": r"¿En cuántos factores queda $5x^{2}-45$ al abrirla del todo?",
                "answer": "3",
            },
        ],
    },
    "footer": {
        "label": "Estado de la sala",
        "states": {
            "repasar": "Te falta cerrar la práctica antes de precintar el almacén.",
            "consolidacion": "Resuelto con ayuda: la ruta ya está, falta que salga sola.",
            "sin_ayuda": "Guías firmadas. Eliges el orden y sabes cuándo parar.",
        },
        "note": "Zona segura: nada de esto mueve tu ELO.",
    },
    # --- Feedback por distractor ----------------------------------------------
    "feedback": {
        "correct": "Correcto. Común primero, y después contar términos.",
        "default": (
            "La ruta es siempre la misma: factor común, contar los términos de lo que queda, "
            "aplicar el molde, y volver a mirar cada trozo."
        ),
        "fb_g05_e1_cuad": (
            "Tal cual no aplica: 18x³ no es un cuadrado exacto. Sacando 2x queda 2x(9x² − 1), "
            "y ahí sí — pero primero va el común."
        ),
        "fb_g05_e1_cubos": (
            "18x³ y 2x no son cubos exactos. Y aunque lo fueran, el común va antes."
        ),
        "fb_g05_e1_tri": ("El trinomio general pide TRES términos y aquí hay dos."),
        "fb_g05_e4_dif": ("Esa sí se abre: dos cuadrados exactos que restan → (x + 2)(x − 2)."),
        "fb_g05_e4_comun": ("Esa tiene factor común: 2x(x + 4). Se abre en dos factores."),
        "fb_g05_e4_cubo": (
            "La suma de CUBOS sí se abre: (x + 2)(x² − 2x + 4). La que se queda cerrada es la "
            "suma de cuadrados."
        ),
        "fb_g05_e5_yes": (
            "El factor común está completo, cierto — pero dentro quedó un trinomio cuadrado "
            "perfecto sin abrir. Ese es el error de esta sala."
        ),
        "fb_g05_e5_wrong": (
            "5m es correcto: la menor potencia de m entre m⁵, m³ y m es m¹. El problema está "
            "dentro del paréntesis."
        ),
        "fb_g05_e5_err": (
            "La igualdad es cierta: 5m · m⁴ = 5m⁵ y así con los tres. Lo que falla es que no "
            "está terminada."
        ),
        "fb_g05_e6_trap": (
            "Una factorización incompleta también cumple la igualdad. 5m(m⁴ − 8m² + 16) "
            "multiplica bien y aún se abre dos veces más."
        ),
        "fb_g05_e6_comun": (
            "El ejemplo que falla tiene el común bien sacado: 5m está completo y el trabajo "
            "sigue abierto dentro del paréntesis."
        ),
        "fb_g05_e6_never": (
            "Sí sirve: detecta los errores de cuenta. Lo que no detecta es que te hayas "
            "quedado corto."
        ),
    },
    "closing": (
        "Con esto el almacén de la caravana queda precintado. Sabes sacar lo común, cotejar "
        "una huella, despiezar a mano, arquear toneles — y, sobre todo, decidir por dónde "
        "empezar cuando la remesa llega sin etiqueta. Esa última es la que no viene escrita "
        "en ningún libro, porque los libros llegan ya ordenados por casos."
    ),
    "validation_status": "F5_G05_11bloques",
}
