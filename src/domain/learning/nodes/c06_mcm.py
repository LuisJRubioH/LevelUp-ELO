"""C06 · MCM — el producto solo acierta cuando no comparten nada.

Destino del nodo: ESPARTA · donde coinciden las rutas. Contexto propio: las
salidas de los barcos del muelle (dos naves que zarpan cada cierto número de días).
"""

NODE_ID = "PREALG-N4-C06-MCM"
CONCEPT_SLUG = "mcm"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "mcm",
    "misconception": "mcm_es_el_producto_de_los_numeros",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "Esparta · Mínimo común múltiplo",
    "destination": "Esparta · donde coinciden las rutas",
    "finish_label": "Terminar el viaje",
    "title": "El producto solo acierta cuando no comparten nada",
    "intro": (
        "En Atenas buscabas lo más grande que cabía en los dos. Aquí buscas lo más pequeño "
        "donde caben los dos. Multiplicar siempre da UNA respuesta válida — pero casi nunca "
        "la más pequeña, y ese «casi» tiene una regla exacta."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes del último muelle. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es el número más pequeño que es múltiplo de 3 y de 5 a la vez?",
                "answer": "15",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale el MCM de $4$ y $6$?",
                "options": [
                    {"id": "twelve", "text": "12", "latex": r"12"},
                    {"id": "twentyfour", "text": "24", "latex": r"24"},
                    {"id": "two", "text": "2", "latex": r"2"},
                ],
                "expected": "twelve",
                "misconception_by_option": {
                    "twentyfour": "mcm_es_el_producto_de_los_numeros",
                    "two": "confunde_mcm_con_mcd",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿El MCM de dos números puede ser menor que uno de ellos?",
                "options": [
                    {"id": "no", "text": "No: tiene que ser múltiplo de los dos"},
                    {"id": "yes", "text": "Sí, si son muy distintos"},
                ],
                "expected": "no",
                "misconception_by_option": {"yes": "confunde_mcm_con_mcd"},
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "eyebrow": "KatIA · En el muelle de Esparta",
        "title": "Las dos naves que nunca coincidían",
        "body": (
            "Del muelle de Esparta salen dos naves de aprovisionamiento. Una zarpa cada 4 "
            "días y la otra cada 6. El día que las dos coinciden en puerto se aprovecha "
            "para hacer el inventario grande, y el capitán quiere saber cada cuánto pasa.\n\n"
            "El escribiente hizo la cuenta rápida: «cada 4 y cada 6, pues cada 24 días». "
            "El capitán programó el inventario para el día 24. Las dos naves ya habían "
            "coincidido el día 12, con todo el mundo trabajando en otra cosa."
        ),
        "question": "¿Cada cuántos días coinciden de verdad las dos naves?",
        "image": "/leccion/04-prealg-n4-puerto/c06-mcm-katia-v4.png",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Cada 24 días: 4 × 6"},
                {"id": "b", "text": "Antes de los 24"},
                {"id": "c", "text": "Cada 2 días"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder decir el día exacto y "
                "explicar cuándo multiplicar sí funciona."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Las dos listas de salidas, una debajo de la otra",
        "body": (
            "Los días en que zarpa cada nave. Busca el primer día que aparece en las dos " "listas."
        ),
        "cases": [
            {
                "label": "Las salidas de cada nave",
                "context": "Una cada 4 días, otra cada 6",
                "fraction": r"M(4),\ M(6)",
                "division": r"4,8,12,16,20,24\ldots\quad 6,12,18,24\ldots",
                "note": "Las dos listas son infinitas (C02), pero se cruzan.",
            },
            {
                "label": "Los días en que coinciden",
                "context": "Los múltiplos COMUNES",
                "fraction": r"M(4)\cap M(6)",
                "division": r"12,24,36,48,\ldots\ \to\ \text{el menor es }12",
                "note": "Coinciden cada 12 días, no cada 24. El 24 también vale, pero llega tarde.",
            },
        ],
        "resolution": (
            "24 no era una respuesta falsa: las naves SÍ coinciden el día 24. Era una "
            "respuesta tardía. El producto siempre da un múltiplo común, porque contiene "
            "todas las piezas de los dos — pero repite las que comparten. 4 y 6 comparten "
            "un 2, y multiplicar lo cuenta dos veces."
        ),
    },
    "definition_title": "El mínimo común múltiplo",
    "definition_katex": r"\text{MCM}(a,b)=\min\big(M(a)\cap M(b)\setminus\{0\}\big)",
    "definition": (
        "El MCM de dos números es el menor múltiplo positivo que tienen en común. Siempre "
        "existe (el producto siempre sirve) y nunca es menor que el mayor de los dos. Solo "
        "coincide con el producto cuando los números son coprimos."
    ),
    "definition_symbols": [
        {
            "symbol": r"\text{MCM}(a,b)",
            "reads": "mínimo común múltiplo",
            "means": "el primer día en que las dos naves coinciden",
        },
        {
            "symbol": r"\min",
            "reads": "el mínimo",
            "means": "el PRIMERO de los comunes; el producto suele ser uno posterior",
        },
        {
            "symbol": r"\text{MCM}(a,b)\ge\max(a,b)",
            "reads": "no baja del mayor",
            "means": "tiene que ser múltiplo de los dos",
        },
        {
            "symbol": r"\text{MCM}\times\text{MCD}=a\times b",
            "reads": "la relación con Atenas",
            "means": "lo que sobra del producto es exactamente el MCD",
        },
        {
            "symbol": r"\text{MCD}=1\Rightarrow\text{MCM}=a\times b",
            "reads": "solo si son coprimos",
            "means": "ahí el producto sí es la respuesta mínima",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Con las piezas de Mileto",
            "title": "El MCM desde la factorización",
            "statement": (
                "Una nave zarpa cada 12 días y otra cada 18. ¿Cada cuántos días coinciden?"
            ),
            "latex": r"12=2^{2}\times 3\qquad 18=2\times 3^{2}",
            "image_slot": False,
            "steps": [
                "Descompongo: 12 = 2² × 3 y 18 = 2 × 3².",
                "El resultado tiene que ser múltiplo de los dos, así que necesita TODAS las piezas de cada uno.",
                "Del 2: uno pide dos y el otro pide uno. Con dos me sobra para los dos → 2².",
                "Del 3: uno pide uno y el otro pide dos → 3².",
                "MCM = 2² × 3² = 36. Se cogen todos los primos con el exponente MAYOR. (El producto habría dado 216, seis veces más tarde.)",
            ],
            "solution": r"$\text{MCM}(12,18)=2^{2}\times 3^{2}=36$",
            "self_explanation": {
                "step_index": 2,
                "prompt": "En el paso 3 se coge el exponente mayor, y en el MCD de Atenas se cogía el menor. ¿Por qué al revés?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Cuando el producto sí acierta",
            "title": "Dos naves coprimas",
            "statement": (
                "Ahora una nave zarpa cada 5 días y otra cada 7. ¿Cada cuántos coinciden?"
            ),
            "latex": r"\text{MCM}(5,7)=35",
            "image_slot": False,
            "steps": [
                "5 y 7 son primos distintos: no comparten ninguna pieza.",
                "El MCM necesita todas las piezas de los dos: un 5 y un 7.",
                "MCM = 5 × 7 = 35. Aquí el producto SÍ es la respuesta mínima.",
                "Compruebo con la fórmula: MCM × MCD = a × b. Como MCD = 1, MCM = 35.",
                "La regla: el producto acierta exactamente cuando los números son coprimos (C05).",
            ],
            "solution": r"$\text{MCM}(5,7)=35$, y aquí sí coincide con el producto",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El escribiente que multiplicó sin mirar",
            "statement": (
                "El escribiente defiende su cuenta: «Una cada 4 días y otra cada 6. "
                "4 × 6 = 24, así que el inventario va el día 24. El 24 es múltiplo de los "
                "dos, así que está bien»."
            ),
            "latex": r"\text{MCM}(4,6)=24",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\text{M}\underline{\text{C}}\text{M}\ \text{sin la M de mínimo}",
            "error_note": "24 es común, sí — pero no es el MÍNIMO. El escribiente contestó a otra pregunta.",
            "correct_version": {
                "wrong_latex": r"\text{MCM}(4,6)=24",
                "right_latex": r"\text{MCM}(4,6)=12",
                "rows": [
                    {
                        "wrong": "El producto es el MCM",
                        "right": "El producto es UN múltiplo común, no siempre el menor",
                    },
                    {
                        "wrong": "4 y 6 no comparten nada",
                        "right": "Comparten un 2, y multiplicar lo cuenta dos veces",
                    },
                ],
            },
            "explain_prompt": "¿Por qué 24 no es la respuesta? Da el valor correcto y di qué pieza se contó de más.",
            "steps": [
                "Escribe los múltiplos: 4, 8, 12… y 6, 12… El 12 aparece antes que el 24.",
                "Desde las piezas: 4 = 2² y 6 = 2 × 3. El producto usa 2³ × 3, pero con 2² basta.",
                "Ese 2 de más es exactamente el MCD(4,6) = 2. Por eso MCM × MCD = producto.",
            ],
            "solution": (
                "El producto siempre da una respuesta VÁLIDA pero tardía. Solo es la mínima "
                "si los números son coprimos. Y hay un atajo: divide el producto entre el "
                "MCD y ya tienes el MCM."
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
                "statement": "Halla el MCM de 6 y 8 con las factorizaciones.",
                "given_steps": [
                    r"6=2\times 3,\quad 8=2^{3}",
                    r"\text{todos los primos con exponente mayor: }2^{3}\times 3",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"\text{MCM}(6,8)=", "answer": "24"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": "Halla el MCM de 10 y 15 usando que MCM × MCD = producto.",
                "given_steps": [
                    r"10\times 15=150,\quad \text{MCD}(10,15)=5",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"150\div 5=", "answer": "30"},
                    {"id": "P2-b2", "label": r"30\div 10=", "answer": "3"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    "Solo el planteamiento: dos naves zarpan cada 9 y cada 4 días. ¿Cada "
                    "cuántos coinciden?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"\text{MCM}(9,4)=", "answer": "36"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos caminos para la misma coincidencia",
        "intro": r"¿Cuánto vale $\text{MCM}(24,36)$? Las dos soluciones de abajo son correctas.",
        "methods": [
            {
                "label": "Método 1 · Por factorización",
                "steps": [
                    r"24=2^{3}\times 3",
                    r"36=2^{2}\times 3^{2}",
                    r"\text{mayores: }2^{3}\times 3^{2}=72",
                ],
                "note": "Todos los primos, cada uno con su exponente más alto.",
            },
            {
                "label": "Método 2 · Con el MCD",
                "steps": [r"24\times 36=864", r"\text{MCD}(24,36)=12", r"864\div 12=72"],
                "note": "Reaprovecha el trabajo de Atenas.",
            },
        ],
        "question": "¿Por qué dividir entre el MCD arregla el producto?",
        "insight": (
            "Porque el producto cuenta dos veces todo lo que los dos números comparten, y "
            "lo que comparten es exactamente el MCD. Dividir entre él quita esa repetición. "
            "De ahí la identidad MCM(a,b) × MCD(a,b) = a × b, que vale siempre: cada pieza "
            "del producto acaba o en el MCD o en el MCM."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el MCM de 3 y 4?",
            "expr": r"\text{MCM}(3,4)",
            "answer": "12",
            "hints": {
                "n1": "¿Comparten algún primo?",
                "n2": "3 y 4 son coprimos: no comparten nada.",
                "n3": "Cuando son coprimos, el MCM es el producto.",
            },
        },
        {
            "id": "E2",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el MCM de 6 y 9?",
            "expr": r"\text{MCM}(6,9)",
            "answer": "18",
            "hints": {
                "n1": "6 = 2 × 3 y 9 = 3², así que comparten un 3.",
                "n2": "Coge todos los primos con el exponente mayor: 2 × 3².",
                "n3": "2 × 9 = …  (el producto 54 llegaría tarde)",
            },
        },
        {
            "id": "E3",
            "kind": "numeric",
            "tipo": "estandar",
            "prompt": "¿Cuál es el MCM de 5 y 20?",
            "expr": r"\text{MCM}(5,20)",
            "answer": "20",
            "hints": {
                "n1": "Comprueba primero si el pequeño divide al grande.",
                "n2": "20 ÷ 5 = 4, exacto.",
                "n3": "Si a divide a b, el MCM es b.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": "Un escribiente anota «MCM(8, 12) = 96, porque 8 × 12 = 96». ¿Dónde está el error?",
            "options": [
                {
                    "id": "not_minimum",
                    "text": "96 es común pero no mínimo: comparten un 4, y el MCM es 24",
                },
                {"id": "arith", "text": "Se equivocó: 8 × 12 no da 96"},
                {"id": "not_multiple", "text": "96 no es múltiplo de 8"},
                {"id": "none", "text": "Ningún error, está bien"},
            ],
            "expected": "not_minimum",
            "feedback_by_option": {
                "not_minimum": "correct",
                "arith": "fb_c06_e4_arith",
                "not_multiple": "fb_c06_e4_multiple",
                "none": "fb_c06_e4_none",
            },
            "misconception_by_option": {
                "arith": "habito_error_de_calculo_no_de_metodo",
                "not_multiple": "no_verifica_la_condicion_de_comun",
                "none": "mcm_es_el_producto_de_los_numeros",
            },
            "hints": {
                "n1": "96 sí es múltiplo de los dos. La pregunta es si es el MENOR.",
                "n2": "Escribe los múltiplos de 12: 12, 24… ¿alguno es múltiplo de 8?",
                "n3": "24 = 8 × 3 y 24 = 12 × 2. Llega mucho antes que 96.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «El MCM de dos números es siempre su producto.»",
            "options": [
                {"id": "false_coprime", "text": "Falsa: solo cuando son coprimos, como 5 y 7"},
                {"id": "true", "text": "Verdadera: multiplicando siempre sale el menor común"},
                {"id": "false_never", "text": "Falsa: nunca puede ser el producto"},
                {"id": "true_primes", "text": "Verdadera solo si los dos son primos"},
            ],
            "expected": "false_coprime",
            "feedback_by_option": {
                "false_coprime": "correct",
                "true": "fb_c06_e5_trap",
                "false_never": "fb_c06_e5_never",
                "true_primes": "fb_c06_e5_primes",
            },
            "misconception_by_option": {
                "true": "mcm_es_el_producto_de_los_numeros",
                "false_never": "olvida_el_caso_coprimo",
                "true_primes": "confunde_primo_con_coprimo",
            },
            "hints": {
                "n1": "Para tumbar un «siempre» basta UN caso.",
                "n2": "Prueba con 4 y 6: el producto es 24 pero coinciden en 12.",
                "n3": "¿Y hay casos donde SÍ acierta? Prueba con 5 y 7.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODOS los pares donde el MCM SÍ es el producto de los dos números.",
            "valid_options": ["p1", "p2", "p3", "p4"],
            "options": [
                {"id": "p1", "text": "3 y 8"},
                {"id": "p2", "text": "4 y 10"},
                {"id": "p3", "text": "9 y 10"},
                {"id": "p4", "text": "6 y 15"},
            ],
            "expected": ["p1", "p3"],
            "trap_options": ["p2", "p4"],
            "hints": {
                "n1": "El producto acierta exactamente cuando el MCD es 1.",
                "n2": "3 y 8 no comparten primos; 9 y 10 tampoco (3² y 2×5).",
                "n3": "4 y 10 comparten un 2; 6 y 15 comparten un 3.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "Una nave zarpa cada 15 días y otra cada 20. Hoy coincidieron en puerto. "
                "¿Dentro de cuántos días vuelven a coincidir?"
            ),
            "expr": r"\text{MCM}(15,20)",
            "answer": "60",
            "hints": {
                "n1": "15 = 3 × 5 y 20 = 2² × 5.",
                "n2": "Todos los primos con el exponente mayor: 2² × 3 × 5.",
                "n3": "4 × 3 × 5 = …  (el producto 300 llegaría cinco veces más tarde)",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿El producto acierta?",
        "title": "¿Es el MCM igual a a × b?",
        "intro": "La respuesta depende de una sola cosa: si los dos números comparten piezas.",
        "rows": [
            {
                "symbol": r"(4,6)",
                "name": "Comparten un 2",
                "closed": "no",
                "latex": r"\text{MCM}=12,\ 4\times 6=24",
                "note": "El producto llega el doble de tarde. Ese doble es el MCD.",
            },
            {
                "symbol": r"(3,5)",
                "name": "Coprimos",
                "closed": "yes",
                "latex": r"\text{MCM}=15=3\times 5",
                "note": "No comparten nada, así que no hay nada repetido que quitar.",
            },
            {
                "symbol": r"(6,12)",
                "name": "Uno divide al otro",
                "closed": "no",
                "latex": r"\text{MCM}=12,\ 6\times 12=72",
                "note": "El MCM es directamente el mayor. Compruébalo siempre primero.",
            },
            {
                "symbol": r"(7,11)",
                "name": "Dos primos distintos",
                "closed": "yes",
                "latex": r"\text{MCM}=77=7\times 11",
                "note": "Dos primos distintos siempre son coprimos: el producto acierta.",
            },
            {
                "symbol": r"(a,a)",
                "name": "El mismo dos veces",
                "closed": "no",
                "latex": r"\text{MCM}(a,a)=a",
                "note": "Comparten todo. El producto a² se pasa muchísimo.",
            },
            {
                "symbol": r"(n,1)",
                "name": "Con el uno",
                "closed": "yes",
                "latex": r"\text{MCM}(n,1)=n=n\times 1",
                "note": "El producto acierta, aunque por una razón boba: multiplicar por 1 no cambia nada (N3-M04).",
            },
        ],
        "outro": (
            "El producto acierta cuando el MCD es 1 y falla en todo lo demás — y falla "
            "exactamente por un factor MCD. Esa es la última pieza del puerto: "
            "MCM × MCD = a × b."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres casos trabajados en este nodo?",
        "thumbnails": [r"\text{MCM}(12,18)", r"\text{MCM}(5,7)", r"\text{MCM}(4,6)=24?"],
        "options": [
            {
                "id": "common_multiple",
                "text": "En los tres se busca un número donde quepan los DOS",
                "correct": True,
            },
            {
                "id": "floor",
                "text": "En los tres el resultado no puede bajar del número mayor",
                "correct": True,
            },
            {
                "id": "product",
                "text": "En los tres el resultado es el producto de los dos",
                "correct": False,
            },
            {
                "id": "smaller",
                "text": "En los tres el resultado es menor que los dos números",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Última cuenta del puerto: una nave zarpa cada 8 días y otra cada 14. Hoy las "
            "dos están en el muelle. ¿Dentro de cuántos días vuelven a coincidir?"
        ),
        "polya": {
            "comprender": "Busco el primer día futuro que sea múltiplo de 8 y de 14 a la vez.",
            "planear": "Compruebo si 8 divide a 14 (no). Descompongo los dos y cojo todos los primos con exponente mayor.",
            "ejecutar": "8 = 2³ y 14 = 2 × 7 → 2³ × 7 = 56.",
            "comprobar": "56 ÷ 8 = 7 ✓ y 56 ÷ 14 = 4 ✓. Y con la identidad: 8 × 14 = 112, MCD = 2, y 112 ÷ 2 = 56 ✓.",
        },
        "prompt": "¿Dentro de cuántos días coinciden?",
        "answer": "56",
        "hints": {
            "n1": "Descompón los dos números.",
            "n2": "8 = 2³ y 14 = 2 × 7.",
            "n3": "Todos los primos con el exponente mayor: 2³ × 7 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otros números. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya compruebas si comparten piezas antes de multiplicar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué el producto "
            "casi siempre llega tarde."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "¿Cuál es el número más pequeño que es múltiplo de 2 y de 7 a la vez?",
                "answer": "14",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale el MCM de $6$ y $10$?",
                "options": [
                    {"id": "thirty", "text": "30", "latex": r"30"},
                    {"id": "sixty", "text": "60", "latex": r"60"},
                    {"id": "two", "text": "2", "latex": r"2"},
                ],
                "expected": "thirty",
                "misconception_by_option": {
                    "sixty": "mcm_es_el_producto_de_los_numeros",
                    "two": "confunde_mcm_con_mcd",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale el MCM de $4$ y $9$?",
                "options": [
                    {"id": "thirtysix", "text": "36: son coprimos, así que sí es el producto"},
                    {"id": "twelve", "text": "12"},
                    {"id": "one", "text": "1"},
                ],
                "expected": "thirtysix",
                "misconception_by_option": {
                    "twelve": "sobregeneraliza_mcm",
                    "one": "confunde_mcm_con_mcd",
                },
                # Caso donde el producto SÍ acierta: comprueba que aprendió el
                # criterio y no la heurística "el producto siempre está mal".
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
        "default": "Comprueba si los dos números comparten algún primo antes de multiplicar.",
        "fb_c06_e4_arith": (
            "8 × 12 = 96 está bien. → El problema es si 96 es el MENOR común, no si el "
            "producto está bien calculado."
        ),
        "fb_c06_e4_multiple": (
            "96 sí es múltiplo de 8: 96 ÷ 8 = 12. → Busca si hay algún múltiplo común más pequeño."
        ),
        "fb_c06_e4_none": (
            "Escribe los múltiplos de 12 y busca el primero que también lo sea de 8. → Di "
            "cuál es."
        ),
        "fb_c06_e5_trap": (
            "Con 4 y 6 el producto da 24 pero coinciden en 12. → Comprueba ese caso."
        ),
        "fb_c06_e5_never": ("Casi: hay casos donde sí acierta. → Calcula MCM(5, 7)."),
        "fb_c06_e5_primes": (
            "No hace falta que sean primos, solo COPRIMOS: 4 y 9 son compuestos y el "
            "producto acierta. → Calcula MCM(4, 9)."
        ),
    },
    "closing": (
        "El MCM es el primer encuentro, no cualquiera: el producto sirve solo si los "
        "números no comparten piezas, y falla exactamente por un factor MCD. Con esto "
        "cierras el Puerto de la Polis y todo el mapa de Preálgebra."
    ),
    "validation_status": "F4_C06_11bloques",
}
