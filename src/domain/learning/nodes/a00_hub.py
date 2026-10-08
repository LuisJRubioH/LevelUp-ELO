"""A00 · El Papiro de las Cuatro Casas — hub de aterrizaje del módulo de Álgebra.

No es una lección: es la antesala. Presenta Kemet, el papiro dañado y las cuatro
casas que hay que visitar para restaurarlo. Cada tarjeta abre un NIVEL, no un
nodo suelto — la casa se recorre entera.

Se pinta con el renderer de hub por tarjetas (el mismo del Puerto de la Polis):
mismo contrato de contenido, distinta imagen y distinto mundo.
"""

NODE_ID = "ALG-A00-PAPIRO-CUATRO-CASAS"

# Una casa por nivel. `node_id` apunta al PRIMER nodo de cada casa.
CARDS = [
    {
        "id": "A1",
        "concept": "lenguaje_algebraico",
        "symbol": r"3n",
        "node_id": "ALG-N1-L01-VARIABLES",
        "destination": "La Casa de la Vida",
        "teaser": "Poner por escrito una cantidad que todavía no ha llegado.",
    },
    {
        "id": "A2",
        "concept": "operaciones_con_expresiones",
        "symbol": r"4r+2r",
        "node_id": "ALG-N1-O01-SEMEJANTES",
        "destination": "La obra de la pirámide",
        "teaser": "Juntar dos registros en uno sin mezclar lo que no se mezcla.",
    },
    {
        "id": "A3",
        "concept": "fracciones_algebraicas",
        "symbol": r"\dfrac{6x}{3}",
        "node_id": "ALG-N1-F01-SIMPLIFICAR",
        "destination": "Los campos tras la crecida",
        "teaser": "Repartir una franja entre un número de familias que cambia cada año.",
    },
    {
        "id": "A4",
        "concept": "razones_y_proporciones",
        "symbol": r"2:3=4:6",
        "node_id": "ALG-N1-R01-RAZONES",
        "destination": "El taller del canon",
        "teaser": "Cambiar el tamaño de una figura sin que deje de ser la misma figura.",
    },
]

CONTENT = {
    "kind": "level_hub_cards",
    "level": "Módulo de Álgebra",
    "title": "El Papiro de las Cuatro Casas",
    "welcome_text": (
        "Preálgebra terminó en el puerto, y en el puerto había un barco. KatIA lo tomó "
        "río arriba hasta Kemet, donde los números llevan siglos escribiéndose sobre "
        "papiro. Aquí las cuentas dejan de ser solo cuentas: aprenden a hablar de "
        "cantidades que todavía no se conocen."
    ),
    "scene_text": (
        "Meritka, la custodia del archivo, extiende sobre la mesa lo que queda de un "
        "papiro largo. La crecida se llevó cuatro secciones, y sin ellas el archivo no "
        "sabe registrar nada que cambie. Cada sección se restaura en una casa distinta, "
        "y ninguna se puede escribir antes que la anterior."
    ),
    "image": "/leccion/05-alg-n1-kemet/a00-hub-papiro-katia.png",
    "cards_hint": "Abre las cuatro casas para desplegar el papiro",
    "cards_aria": "Las cuatro casas del papiro",
    "card_cta": "Entrar",
    "gating_label": "Para desplegar el papiro",
    "finish_label": "Entrar en la Casa de la Vida",
    "card_closed_hint": "Toca la casa para ver qué se restaura en ella.",
    "icebreaker": {
        "title": "Antes de entrar",
        "intro": (
            "Tres preguntas para calentar. No se califican y no bloquean nada: solo "
            "quiero ver desde dónde partimos."
        ),
        "items": [
            {
                "id": "ICE1",
                "kind": "numeric",
                "prompt": (
                    "En el granero de la Polis cada saco pesaba 7 medidas. Aquí cada cesto "
                    "de grano pesa 9 y han llegado 6 cestos. ¿Cuántas medidas hay?"
                ),
                "expr": r"9\times 6",
                "answer": "54",
            },
            {
                "id": "ICE2",
                "kind": "single_select",
                "prompt": (
                    "Un registro dice «tres panes por trabajador» y otro dice «veintiún "
                    "panes». ¿Cuál de los dos sirve para cualquier día?"
                ),
                "options": [
                    {"id": "rule", "text": "El primero: describe una regla"},
                    {"id": "total", "text": "El segundo: da el número exacto"},
                    {"id": "both", "text": "Los dos sirven igual"},
                ],
                "expected": "rule",
            },
            {
                "id": "ICE3",
                "kind": "single_select",
                "prompt": (
                    "¿Qué crees que hace falta para escribir una cuenta cuando falta un dato?"
                ),
                "options": [
                    {"id": "symbol", "text": "Un símbolo que ocupe el lugar de ese dato"},
                    {"id": "wait", "text": "Esperar a conocerlo"},
                    {"id": "guess", "text": "Poner un número cualquiera"},
                ],
                "expected": "symbol",
            },
        ],
    },
    "advance_text": (
        "Ya sabes qué se restaura en cada casa. Empieza por la Casa de la Vida: sin saber "
        "nombrar lo desconocido, las otras tres no se pueden ni empezar."
    ),
    "gating": {"rule": "all_cards_opened", "cards_required": 4},
    "cards": CARDS,
    "feedback": {
        "correct": "¡Correcto!",
        "default": "Revisa la respuesta con calma antes de continuar.",
        "card_opened": "Casa abierta.",
        "fb_hub_ice2_total": (
            "«Veintiún panes» solo vale el día que vinieron siete trabajadores. → ¿Cuál de "
            "los dos sigue sirviendo mañana?"
        ),
    },
    "validation_status": "F5_A00_hub",
}
