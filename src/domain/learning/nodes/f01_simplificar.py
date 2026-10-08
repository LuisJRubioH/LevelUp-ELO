"""F01 · La parcela partida — solo se simplifican factores completos.

Primera sala de los campos tras la crecida. Guía: Tabiry, que coordina los repartos.
Vocabulario propio: parcela, lindero, franja, familia, reparto, terreno húmedo.
Nada de canales ni caudales (F02), eras ni gavillas (F03), ni simiente (F04).

Alcance de ESTA sala: interpretar, evaluar para valores válidos, reconocer el
denominador no nulo y simplificar factores comunes evidentes. Sumar, multiplicar
y dividir fracciones algebraicas son las tres salas siguientes. No se factorizan
polinomios en ninguna de las cuatro.
"""

NODE_ID = "ALG-N1-F01-SIMPLIFICAR"
CONCEPT_SLUG = "fracciones_algebraicas"

CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": "fracciones_algebraicas",
    "misconception": "cancelacion_en_suma",
    "story_contract": {
        "type": "guided_discovery_formalization",
        "practice_position": "after_definition_plus_examples",
        "is_integrated": True,
    },
    # --- Bloque 1 · Encabezado ------------------------------------------------
    "kicker": "La parcela partida · Simplificación",
    "house": "La parcela partida",
    "guide": "Tabiry",
    "finish_label": "Bajar al canal madre",
    "title": "Tachar lo que se repite solo vale si multiplica a todo",
    "intro": (
        "El agua ha borrado los linderos y hay que repartir de nuevo. Aquí la barra de "
        "fracción no es un adorno: es una división que espera a saber entre cuántos. Y "
        "hay una tachadura que parece legal y no lo es."
    ),
    # --- Bloque 2 · Mini-diagnóstico -----------------------------------------
    "diagnostic": {
        "intro": "Tres rápidas antes de pisar el barro. Sin nota.",
        "items": [
            {
                "id": "D1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": "Una franja de 12 medidas se reparte entre 3 familias por igual. ¿Cuánto toca a cada una?",
                "answer": "4",
            },
            {
                "id": "D2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuál es un factor común de todos los términos de $6x$?",
                "options": [
                    {"id": "six", "text": r"$6$ (y también $x$, y también $3$)"},
                    {"id": "plus", "text": r"No tiene: $6x$ es un solo término"},
                    {"id": "seven", "text": r"$7$"},
                ],
                "expected": "six",
                "misconception_by_option": {
                    "plus": "no_reconoce_factores_en_un_monomio",
                    "seven": "confunde_factor_con_suma",
                },
            },
            {
                "id": "D3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": "¿Qué pasa si el número de familias entre las que se reparte fuera 0?",
                "options": [
                    {
                        "id": "undefined",
                        "text": "No hay reparto posible: dividir entre 0 no está definido",
                    },
                    {"id": "zero", "text": "El reparto da 0 a cada una"},
                    {"id": "all", "text": "Le toca todo a la primera"},
                ],
                "expected": "undefined",
                "misconception_by_option": {
                    "zero": "denominador_cero",
                    "all": "denominador_cero",
                },
            },
        ],
    },
    # --- Bloque 3 · Apertura de KatIA + intento genuino -----------------------
    "katia": {
        "image": "/leccion/05-alg-n1-kemet/f01-simplificar-katia.png",
        "eyebrow": "KatIA · Sobre el terreno húmedo",
        "title": "El reparto que aún no se puede calcular",
        "body": (
            "Tabiry recorre la orilla con la cuerda anudada. La crecida ha dejado una "
            "franja de tierra buena, pero este año no se sabe cuántas familias volverán: "
            "unas se quedaron río arriba y otras no han llegado.\n\n"
            "«Tengo que dejar escrito el reparto hoy», dice Tabiry, «y el número de "
            "familias lo sabré en la próxima luna. Además la franja tampoco mide siempre "
            "lo mismo: el agua se lleva un trozo y devuelve otro.»"
        ),
        "question": "¿Cómo se escribe un reparto cuando no se sabe ni cuánto hay ni entre cuántos?",
        "attempt": {
            "format": "acotado",
            "prompt": "Escoge lo que creas ahora. No se califica.",
            "options": [
                {"id": "a", "text": "Esperar a la próxima luna y calcularlo entonces"},
                {"id": "b", "text": "Escribir la división con letras y dejarla indicada"},
                {"id": "c", "text": "Repartir en partes iguales por si acaso"},
            ],
            "response": (
                "Veámoslo. Guarda tu respuesta: al final vas a poder escribir el reparto y "
                "decir qué valores no puede tomar."
            ),
        },
    },
    # --- Bloque 4 · Descubrimiento guiado + definición ------------------------
    "discovery": {
        "eyebrow": "Descubrimiento guiado",
        "title": "Dos repartos que se escriben igual y se simplifican distinto",
        "body": (
            "Los dos son una barra con letras arriba. Solo uno se puede acortar, y la "
            "diferencia está en si lo que se repite multiplica a TODO el numerador."
        ),
        "cases": [
            {
                "label": "Sí se simplifica",
                "context": "Una franja de 6 parcelas se reparte entre 3 familias",
                "fraction": r"\dfrac{6x}{3}=2x",
                "division": r"\dfrac{3\cdot 2x}{3}",
                "note": "El 3 multiplica a todo el numerador: se puede sacar y cancelar con el de abajo.",
            },
            {
                "label": "No se simplifica",
                "context": "Una franja de x parcelas más 4 de reserva, entre x familias",
                "fraction": r"\dfrac{x+4}{x}",
                "division": r"\ne 4",
                "note": "La x de arriba está SUMADA con el 4, no multiplicando al conjunto. No hay nada que sacar.",
            },
        ],
        "resolution": (
            "Cancelar es dividir arriba y abajo por lo mismo, y dividir reparte sobre un "
            "producto, no sobre una suma. Por eso solo se tacha lo que multiplica al "
            "numerador entero. Si un término está sumado, tacharlo cambia el valor — y hay "
            "un número que lo demuestra en una línea."
        ),
    },
    "definition_title": "Fracción algebraica",
    "definition_katex": r"\dfrac{a\cdot m}{a\cdot n}=\dfrac{m}{n}\quad (a\ne 0,\ n\ne 0)",
    "definition": (
        "Una FRACCIÓN ALGEBRAICA es un cociente en el que el numerador o el denominador "
        "contienen expresiones con letras. La barra significa división, así que el "
        "denominador nunca puede valer 0. Solo se simplifican FACTORES comunes completos: "
        "los sumandos no se cancelan."
    ),
    "definition_symbols": [
        {
            "symbol": r"\dfrac{6x}{3}",
            "reads": "seis equis entre tres",
            "means": "reparto de 6x en 3 partes iguales",
        },
        {
            "symbol": r"a\ne 0",
            "reads": "a distinto de cero",
            "means": "solo se cancela lo que no es cero",
        },
        {
            "symbol": r"n\ne 0",
            "reads": "denominador no nulo",
            "means": "restricción obligatoria: sin ella la fracción no existe",
        },
        {
            "symbol": r"\dfrac{x+4}{x}",
            "reads": "no simplificable",
            "means": "la x de arriba es un sumando, no un factor",
        },
        {
            "symbol": r"x\in\mathbb{N},\ x>0",
            "reads": "dominio del contexto",
            "means": "aquí x cuenta familias: entero y positivo",
        },
    ],
    # --- Bloque 5 · Ejemplos resueltos ----------------------------------------
    "worked_examples": [
        {
            "eyebrow": "Ejemplo 1 · Longitud por equipo",
            "title": "Cuando el divisor multiplica a todo",
            "statement": (
                "Un canal de 8r codos de largo se abre entre 4 equipos, que hacen tramos "
                "iguales. ¿Cuánto abre cada equipo?"
            ),
            "latex": r"\dfrac{8r}{4}",
            "image_slot": False,
            "steps": [
                "El reparto es una división: 8r entre 4.",
                "Busco un factor que multiplique a TODO el numerador. 8r = 4 · 2r, así que el 4 está.",
                "Cancelo el 4 de arriba con el de abajo: queda 2r.",
                "Compruebo al revés: 4 · 2r = 8r ✓. Esa es la comprobación que nunca falla.",
                "Restricción: aquí no hace falta, el denominador es el número 4 y nunca es cero.",
            ],
            "solution": r"$\dfrac{8r}{4}=2r$ codos por equipo",
            "self_explanation": {
                "step_index": 1,
                "prompt": "¿Qué significa exactamente «que multiplique a todo el numerador»?",
            },
        },
        {
            "eyebrow": "Ejemplo 2 · Medidas para los canales",
            "title": "Un factor que es un paréntesis entero",
            "statement": (
                "Se necesitan 6(c + 2) cuerdas anudadas para marcar los canales, y se "
                "reparten entre 3 jornadas iguales. ¿Cuántas por jornada?"
            ),
            "latex": r"\dfrac{6(c+2)}{3}",
            "image_slot": False,
            "steps": [
                "El numerador ya viene escrito como producto: 6 por el paréntesis.",
                "Simplifico solo la parte numérica: 6 ÷ 3 = 2.",
                "El paréntesis se queda entero: 2(c + 2). No se toca lo de dentro.",
                "Compruebo con c = 4: arriba 6 · 6 = 36, entre 3 son 12; y 2 · 6 = 12 ✓.",
                "Ojo con la tentación: NO se puede cancelar el 3 con el 2 de dentro del paréntesis.",
            ],
            "solution": r"$\dfrac{6(c+2)}{3}=2(c+2)$",
        },
        {
            "eyebrow": "Trampa común",
            "title": "El aprendiz que tachó una x sumada",
            "statement": (
                "El aprendiz de Tabiry entrega el reparto así: «la franja mide x + 4 y hay "
                "x familias, tacho las dos x y a cada familia le tocan 4»."
            ),
            "latex": r"\dfrac{x+4}{x}=4",
            "trap": True,
            "confidence_prompt": "¿Qué tan seguro estás de dónde falla?",
            "error_latex": r"\dfrac{\cancel{x}+4}{\cancel{x}}\ \text{no está permitido}",
            "error_note": (
                "La x de arriba está sumando con el 4. Tacharla no es dividir el numerador "
                "entero: es borrar solo un trozo."
            ),
            "correct_version": {
                "wrong_latex": r"\dfrac{x+4}{x}=4",
                "right_latex": r"\dfrac{x+4}{x}=1+\dfrac{4}{x}\quad (x\ne 0)",
                "rows": [
                    {
                        "wrong": "Si la x está arriba y abajo, se tacha",
                        "right": "Solo si multiplica a TODO el numerador",
                    },
                    {
                        "wrong": "Queda 4, un número fijo",
                        "right": "Queda algo que depende de x: con 2 familias toca 3 y con 4 familias toca 2",
                    },
                ],
            },
            "explain_prompt": (
                "Explica por qué no se puede tachar y comprueba el error tomando x = 2."
            ),
            "steps": [
                "Sustituyo x = 2 en el original: (2 + 4) ÷ 2 = 6 ÷ 2 = 3.",
                "El aprendiz dice que siempre da 4. Con 2 familias da 3, no 4: un contraejemplo basta.",
                "La forma correcta se obtiene repartiendo la barra sobre cada sumando: x/x + 4/x = 1 + 4/x, y eso solo vale si x ≠ 0.",
            ],
            "solution": (
                "Regla para no volver a caer: antes de tachar, pregúntate si eso que vas a "
                "tachar multiplica al numerador ENTERO. Si hay un + o un − por medio, no."
            ),
        },
    ],
    # --- Bloque 6 · Puente ----------------------------------------------------
    "bridge": {
        "intro": "El reparto ya va empezado; completa los huecos.",
        "items": [
            {
                "id": "P1",
                "missing": "last",
                "statement": r"Simplifica $\dfrac{10m}{5}$ y evalúa el resultado para $m=7$.",
                "given_steps": [
                    r"\dfrac{10m}{5}=2m",
                    r"m=7",
                ],
                "blanks": [
                    {"id": "P1-b1", "label": r"2m=", "answer": "14"},
                ],
            },
            {
                "id": "P2",
                "missing": "middle",
                "statement": r"Simplifica $\dfrac{12(a+1)}{4}$ y evalúa para $a=5$.",
                "given_steps": [
                    r"\text{el factor numérico común es }4",
                ],
                "blanks": [
                    {"id": "P2-b1", "label": r"12\div 4=", "answer": "3"},
                    {"id": "P2-b2", "label": r"3(a+1)\ \text{con}\ a=5:", "answer": "18"},
                ],
            },
            {
                "id": "P3",
                "missing": "statement_only",
                "presentation": "avanzado",
                "statement": (
                    r"Solo el planteamiento: en $\dfrac{5}{x-2}$, ¿qué valor NO puede tomar $x$?"
                ),
                "given_steps": [],
                "blanks": [
                    {"id": "P3-b1", "label": r"x\ne", "answer": "2"},
                ],
            },
        ],
    },
    # --- Bloque 7 · Comparación de métodos ------------------------------------
    "method_comparison": {
        "title": "Dos maneras de ver la misma simplificación",
        "intro": r"Simplifica $\dfrac{12(x+1)}{4}$. Las dos soluciones son correctas.",
        "methods": [
            {
                "label": "Método 1 · Simplificar el factor numérico",
                "steps": [
                    r"\dfrac{12(x+1)}{4}",
                    r"12\div 4=3",
                    r"3(x+1)",
                ],
                "note": "Directo. Exige tener claro que el paréntesis es un factor y no se toca.",
            },
            {
                "label": "Método 2 · Repartir y comprobar",
                "steps": [
                    r"12(x+1)=12x+12",
                    r"\dfrac{12x+12}{4}=3x+3",
                    r"3x+3=3(x+1)",
                ],
                "note": "Más largo, pero enseña POR QUÉ es válido: el 4 divide a los dos sumandos.",
            },
        ],
        "question": "¿Cuál muestra mejor por qué la simplificación es legítima?",
        "insight": (
            "El segundo. Al desarrollar se ve que el 4 divide a CADA término del numerador "
            "—12x y 12— y por eso puede salir. En cambio en (x+4)/x la x no divide al 4, y "
            "ese es exactamente el motivo de que ahí no se pueda tachar nada."
        ),
    },
    # --- Bloque 8 · Práctica ---------------------------------------------------
    "practice": [
        {
            "id": "E1",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Simplifica $\dfrac{15p}{5}$.",
            "options": [
                {"id": "threep", "text": r"$3p$", "latex": r"3p"},
                {"id": "three", "text": r"$3$", "latex": r"3"},
                {"id": "tenp", "text": r"$10p$", "latex": r"10p"},
                {"id": "p3", "text": r"$\dfrac{p}{3}$", "latex": r"\dfrac{p}{3}"},
            ],
            "expected": "threep",
            "feedback_by_option": {
                "threep": "correct",
                "three": "fb_a03_e1_drop",
                "tenp": "fb_a03_e1_sub",
                "p3": "fb_a03_e1_inv",
            },
            "misconception_by_option": {
                "three": "pierde_la_parte_literal",
                "tenp": "resta_en_vez_de_dividir",
                "p3": "invierte_el_cociente",
            },
            "hints": {
                "n1": "15p es 5 · 3p.",
                "n2": "El 5 multiplica a todo el numerador, así que se puede cancelar.",
                "n3": "Queda 3 por p.",
            },
        },
        {
            "id": "E2",
            "kind": "single_select",
            "tipo": "estandar",
            "prompt": r"Simplifica $\dfrac{9(k+3)}{3}$.",
            "options": [
                {"id": "correct", "text": r"$3(k+3)$", "latex": r"3(k+3)"},
                {"id": "inside", "text": r"$9(k+1)$", "latex": r"9(k+1)"},
                {"id": "both", "text": r"$3(k+1)$", "latex": r"3(k+1)"},
                {"id": "k3", "text": r"$3k+3$", "latex": r"3k+3"},
            ],
            "expected": "correct",
            "feedback_by_option": {
                "correct": "correct",
                "inside": "fb_a03_e2_inside",
                "both": "fb_a03_e2_both",
                "k3": "fb_a03_e2_partial",
            },
            "misconception_by_option": {
                "inside": "cancela_dentro_del_parentesis",
                "both": "cancela_dentro_del_parentesis",
                "k3": "reparte_solo_al_primer_termino",
            },
            "hints": {
                "n1": "El denominador se simplifica con el 9, no con lo de dentro del paréntesis.",
                "n2": "El paréntesis es un factor: entra o sale entero.",
                "n3": "9 ÷ 3 = 3, y (k + 3) se queda como está.",
            },
        },
        {
            "id": "E3",
            "kind": "text_exact",
            "tipo": "estandar",
            "prompt": (
                "El reparto de una franja se escribe 8n ÷ 4, donde n es el número de "
                "parcelas por familia. Escribe la fracción ya simplificada."
            ),
            "expr": r"\dfrac{8n}{4}",
            "answer": "2n",
            "hints": {
                "n1": "Busca el factor que multiplica a todo el numerador.",
                "n2": "8n = 4 · 2n.",
                "n3": "Al cancelar el 4 queda el coeficiente 2 con su letra.",
            },
        },
        {
            "id": "E4",
            "kind": "single_select",
            "tipo": "detecta_error",
            "prompt": (r"Un aprendiz escribe: «$\dfrac{2y+6}{2}=y+6$». ¿Dónde está el error?"),
            "options": [
                {
                    "id": "partial",
                    "text": "Dividió solo el primer término: el 6 también hay que dividirlo, y queda y + 3",
                },
                {"id": "cancel", "text": "No se puede simplificar nada en esa fracción"},
                {"id": "coef", "text": "2y ÷ 2 no es y"},
                {"id": "none", "text": "No hay error"},
            ],
            "expected": "partial",
            "feedback_by_option": {
                "partial": "correct",
                "cancel": "fb_a03_e4_cancel",
                "coef": "fb_a03_e4_coef",
                "none": "fb_a03_e4_none",
            },
            "misconception_by_option": {
                "cancel": "no_reconoce_factor_comun_real",
                "coef": "habito_busca_el_error_donde_no_esta",
                "none": "reparte_solo_al_primer_termino",
            },
            "hints": {
                "n1": "Comprueba con y = 4: ¿dan lo mismo los dos lados?",
                "n2": "Arriba sale 14, entre 2 son 7. Y y + 6 daría 10.",
                "n3": "El 2 divide a los DOS sumandos: 2y ÷ 2 = y y 6 ÷ 2 = 3.",
            },
        },
        {
            "id": "E5",
            "kind": "single_select",
            "tipo": "trampa",
            "confidence": "fija",
            "prompt": r"¿Es verdadera o falsa? «$\dfrac{x+4}{x}=4$ para cualquier $x$.»",
            "options": [
                {
                    "id": "false",
                    "text": "Falsa: la x está sumada, no multiplicando; no se puede tachar",
                },
                {"id": "true", "text": "Verdadera: la x de arriba y la de abajo se cancelan"},
                {"id": "true_not0", "text": "Verdadera siempre que x ≠ 0"},
                {"id": "false_five", "text": r"Falsa: en realidad da $5$"},
            ],
            "expected": "false",
            "feedback_by_option": {
                "false": "correct",
                "true": "fb_a03_e5_trap",
                "true_not0": "fb_a03_e5_not0",
                "false_five": "fb_a03_e5_five",
            },
            "misconception_by_option": {
                "true": "cancelacion_en_suma",
                "true_not0": "cancelacion_en_suma",
                "false_five": "cancelacion_en_suma",
            },
            "hints": {
                "n1": "Para tumbar un «para cualquier x» basta UN valor.",
                "n2": "Prueba con x = 2.",
                "n3": "(2 + 4) ÷ 2 = 3, y 3 no es 4.",
            },
        },
        {
            "id": "E6",
            "kind": "multi_select",
            "tipo": "estandar",
            "prompt": "Selecciona TODAS las fracciones que SÍ se pueden simplificar.",
            "valid_options": ["a", "b", "c", "d"],
            "options": [
                {"id": "a", "text": r"$\dfrac{4t}{2}$", "latex": r"\dfrac{4t}{2}"},
                {"id": "b", "text": r"$\dfrac{t+2}{2}$", "latex": r"\dfrac{t+2}{2}"},
                {"id": "c", "text": r"$\dfrac{5(t+1)}{5}$", "latex": r"\dfrac{5(t+1)}{5}"},
                {"id": "d", "text": r"$\dfrac{t+5}{t}$", "latex": r"\dfrac{t+5}{t}"},
            ],
            "expected": ["a", "c"],
            "trap_options": ["b", "d"],
            "hints": {
                "n1": "Pregunta en cada una: ¿lo de abajo multiplica al numerador ENTERO?",
                "n2": "4t = 2 · 2t y 5(t+1) ya viene escrito como producto.",
                "n3": "En t + 2 y en t + 5 hay sumas: el denominador no divide a los dos sumandos.",
            },
        },
        {
            "id": "E7",
            "kind": "numeric",
            "tipo": "transferencia",
            "prompt": (
                "El agua de un canal se reparte por turnos: 20w medidas entre 5 turnos "
                "iguales, donde w es la anchura de la compuerta. Si w = 3, ¿cuántas "
                "medidas corresponden a cada turno?"
            ),
            "expr": r"\dfrac{20w}{5},\quad w=3",
            "answer": "12",
            "hints": {
                "n1": "Simplifica antes de sustituir.",
                "n2": "20w ÷ 5 = 4w.",
                "n3": "4 · 3 = …",
            },
        },
    ],
    # --- Bloque 9 · Cierre -----------------------------------------------------
    "closure": {
        "eyebrow": "¿Se puede tachar?",
        "title": "Qué decide si una fracción se simplifica",
        "intro": (
            "Que un símbolo aparezca arriba y abajo no da permiso para nada. La pregunta "
            "es si multiplica al numerador entero."
        ),
        "rows": [
            {
                "symbol": r"\dfrac{6x}{3}",
                "name": "Factor numérico común",
                "closed": "yes",
                "latex": r"=2x",
                "note": "6x = 3 · 2x: el 3 multiplica a todo lo de arriba.",
            },
            {
                "symbol": r"\dfrac{x+4}{x}",
                "name": "La x está sumada",
                "closed": "no",
                "latex": r"\ne 4",
                "note": "Con x = 2 da 3, no 4. Es la trampa de este nodo.",
            },
            {
                "symbol": r"\dfrac{6(c+2)}{3}",
                "name": "El factor es un paréntesis",
                "closed": "yes",
                "latex": r"=2(c+2)",
                "note": "Se simplifica el 6 con el 3; lo de dentro del paréntesis no se toca.",
            },
            {
                "symbol": r"\dfrac{2y+6}{2}",
                "name": "Suma con factor común real",
                "closed": "yes",
                "latex": r"=y+3",
                "note": "Aquí sí: el 2 divide a los DOS sumandos. Hay suma, pero también factor común.",
            },
            {
                "symbol": r"\dfrac{5}{x-2}",
                "name": "Nada que simplificar",
                "closed": "no",
                "latex": r"x\ne 2",
                "note": "No se acorta, pero sí hay que declarar la restricción: en x = 2 no existe.",
            },
            {
                "symbol": r"\dfrac{x+4}{x}",
                "name": "Repartir la barra",
                "closed": "partial",
                "latex": r"=1+\dfrac{4}{x}",
                "note": "No se simplifica, pero sí se puede reescribir repartiendo el denominador entre los sumandos.",
            },
        ],
        "outro": (
            "Dos filas conviven a propósito: (x+4)/x no se simplifica y aun así se puede "
            "reescribir. «No se puede tachar» nunca significa «no se puede hacer nada» — "
            "significa que la operación que ibas a hacer no era la correcta."
        ),
    },
    "abstraction_question": {
        "prompt": "¿Qué comparten los tres repartos trabajados en este nodo?",
        "thumbnails": [r"\dfrac{8r}{4}", r"\dfrac{6(c+2)}{3}", r"\dfrac{x+4}{x}"],
        "options": [
            {
                "id": "division",
                "text": "En los tres la barra significa una división",
                "correct": True,
            },
            {
                "id": "factor",
                "text": "En los tres hay que mirar si lo repetido es factor o sumando",
                "correct": True,
            },
            {
                "id": "always",
                "text": "En los tres se puede tachar lo que se repite arriba y abajo",
                "correct": False,
            },
            {
                "id": "number",
                "text": "En los tres el resultado es un número que no depende de la letra",
                "correct": False,
            },
        ],
    },
    "closing_item": {
        "id": "CIERRE",
        "statement": (
            "Último reparto antes de la próxima crecida: una franja de 18f medidas se "
            "divide entre 6 familias por igual, donde f es el número de fanegas que "
            "produjo cada parcela el año pasado. Si f = 5, ¿cuántas medidas recibe cada "
            "familia?"
        ),
        "polya": {
            "comprender": "Reparto en partes iguales: es una división. El numerador tiene letra; el denominador es un número fijo, 6.",
            "planear": "Simplifico la fracción con letras primero y sustituyo al final: así el número grande solo aparece una vez.",
            "ejecutar": "18f ÷ 6 = 3f, porque 18f = 6 · 3f. Con f = 5: 3 · 5 = 15.",
            "comprobar": "Al revés: 6 · 15 = 90, y 18 · 5 = 90 ✓. Además 6 ≠ 0, así que el reparto existe.",
        },
        "prompt": "¿Cuántas medidas recibe cada familia?",
        "answer": "15",
        "hints": {
            "n1": "Busca el factor que multiplica a todo el numerador.",
            "n2": "18f = 6 · 3f, así que la fracción vale 3f.",
            "n3": "3 · 5 = …",
        },
    },
    # --- Bloque 10 · Post-diagnóstico -----------------------------------------
    "post_diagnostic": {
        "compara_con": "diagnostic",
        "intro": "Las mismas tres de la entrada, con otro reparto. Sin nota.",
        "trigger_refuerzo": "sin_evidencia_avance",
        "resultados": ["avance", "sin_evidencia_de_avance"],
        "outcome_gain": "Avance: ya distingues un factor de un sumando antes de tachar.",
        "outcome_flat": (
            "Sin evidencia de avance todavía. KatIA va a retomar contigo por qué un sumando "
            "no se puede cancelar."
        ),
        "items": [
            {
                "id": "PD1",
                "kind": "numeric",
                "tipo": "diagnostico",
                "prompt": r"Simplifica $\dfrac{9q}{3}$ y evalúa el resultado para $q=8$.",
                "answer": "24",
            },
            {
                "id": "PD2",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"¿Cuánto vale $\dfrac{3y+9}{3}$?",
                "options": [
                    {"id": "y3", "text": r"$y+3$", "latex": r"y+3"},
                    {"id": "y9", "text": r"$y+9$", "latex": r"y+9"},
                    {"id": "nine", "text": r"$9$", "latex": r"9"},
                ],
                "expected": "y3",
                "misconception_by_option": {
                    "y9": "reparte_solo_al_primer_termino",
                    "nine": "cancelacion_en_suma",
                },
            },
            {
                "id": "PD3",
                "kind": "single_select",
                "tipo": "diagnostico",
                "prompt": r"En $\dfrac{7}{x-5}$, ¿qué valor no puede tomar $x$?",
                "options": [
                    {"id": "five", "text": r"$x=5$"},
                    {"id": "zero", "text": r"$x=0$"},
                    {"id": "seven", "text": r"$x=7$"},
                ],
                "expected": "five",
                "misconception_by_option": {
                    "zero": "confunde_x_cero_con_denominador_cero",
                    "seven": "mira_el_numerador_en_vez_del_denominador",
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
        "default": "Antes de tachar, comprueba si eso multiplica al numerador entero.",
        "fb_a03_e1_drop": (
            "La letra no se va al simplificar: el 5 solo se lleva parte del coeficiente. "
            "→ 15p ÷ 5 son 3 qué."
        ),
        "fb_a03_e1_sub": "Ahí restaste en vez de dividir. → 15 ÷ 5, no 15 − 5.",
        "fb_a03_e1_inv": (
            "El cociente está al revés: el 5 divide a 15, no al contrario. → Comprueba con p = 1."
        ),
        "fb_a03_e2_inside": (
            "El denominador no se simplifica con lo de dentro del paréntesis. → El 3 divide al 9."
        ),
        "fb_a03_e2_both": (
            "Simplificaste dos veces con el mismo 3. → Solo hay un 3 abajo, y ya lo usaste con el 9."
        ),
        "fb_a03_e2_partial": (
            "Casi: 3(k+3) desarrollado es 3k + 9, no 3k + 3. → Reparte el 3 a los dos términos."
        ),
        "fb_a03_e4_cancel": (
            "Sí se puede: el 2 divide a 2y y también a 6. → Divide cada sumando por separado."
        ),
        "fb_a03_e4_coef": ("2y ÷ 2 = y está bien. → El fallo está en el otro sumando."),
        "fb_a03_e4_none": (
            "Comprueba con y = 4: arriba 14, entre 2 son 7; y + 6 daría 10. → No coinciden."
        ),
        "fb_a03_e5_trap": (
            "Solo se cancela lo que multiplica al numerador ENTERO, y esa x está sumada. "
            "→ Prueba con x = 2."
        ),
        "fb_a03_e5_not0": (
            "La restricción x ≠ 0 hace falta, pero no arregla la cancelación. → Con x = 2, "
            "que cumple la restricción, sale 3 y no 4."
        ),
        "fb_a03_e5_five": (
            "El resultado no es un número fijo: cambia con x. → Calcula el valor para x = 2 "
            "y para x = 4."
        ),
    },
    "closing": (
        "El reparto queda escrito antes de saber cuántas familias vuelven, con su "
        "restricción incluida. Tabiry señala el canal madre: cuando dos ramales riegan la "
        "misma parcela hay que juntar sus partes en una sola, y ahí la barra de fracción "
        "tiene otra regla que no perdona."
    ),
    "validation_status": "F5_F01_11bloques",
}
