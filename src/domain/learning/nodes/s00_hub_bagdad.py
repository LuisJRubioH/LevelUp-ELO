"""S00 · La Casa de la Sabiduría — hub de aterrizaje de los dos niveles de Bagdad.

No es una lección: es la antesala de ALG-N2 (la sala de los troqueles) y ALG-N3
(el almacén de la caravana). Los dos niveles no son temas vecinos — son **la
misma operación en las dos direcciones**: en el taller se estampa, en el almacén
se abre lo estampado. Por eso comparten hub y por eso el hub tiene dos puertas y
no nueve.

Cada tarjeta abre un NIVEL y presenta a su guía: Rayhana estampa, Salim abre. El
criterio de verdad del módulo entero cabe en una frase: si abres algo y lo
vuelves a estampar, tiene que salir lo que entró.

Se pinta con el renderer de hub por tarjetas, el mismo del Papiro y del Puerto.
"""

NODE_ID = "ALG-S00-CASA-DE-LA-SABIDURIA"

# Un oficio por nivel. `node_id` apunta al PRIMER nodo de cada ala.
CARDS = [
    {
        "id": "S1",
        "concept": "productos_notables",
        "symbol": r"(a+b)^{2}",
        "node_id": "ALG-N2-P01-CUADRADO",
        "destination": "La sala de los troqueles · Rayhana",
        "teaser": "Cuatro moldes que estampan de una vez lo que multiplicarías a mano.",
    },
    {
        "id": "S2",
        "concept": "factorizacion",
        "symbol": r"a^{2}-b^{2}",
        "node_id": "ALG-N3-G01-FACTOR-COMUN",
        "destination": "El almacén de la caravana · Salim",
        "teaser": "Cinco formas de averiguar de qué molde salió algo que llega cerrado.",
    },
]

CONTENT = {
    "kind": "level_hub_cards",
    "level": "Módulo de Álgebra · Bagdad",
    "title": "La Casa de la Sabiduría",
    "welcome_text": (
        "Kemet quedó atrás. KatIA siguió la ruta de la caravana hasta Bagdad y entró "
        "en una casa donde se traduce, se copia y se calcula todo el día. En Kemet "
        "aprendiste a multiplicar término a término y funcionaba siempre. Aquí vas a "
        "ver que hay productos que aparecen tantas veces que no se calculan: se "
        "reconocen."
    ),
    "scene_text": (
        "El patio tiene dos puertas enfrentadas. Por la de la izquierda entran láminas "
        "en blanco y salen estampadas: es el taller de Rayhana. Por la de la derecha "
        "entran fardos cerrados que hay que abrir para saber de qué estaban hechos: es "
        "el almacén de Salim. Es el mismo trabajo cruzando el patio en dos sentidos, y "
        "quien solo aprende uno se queda a medias — no se reconoce una huella que "
        "nunca se ha visto estampar."
    ),
    "image": "/leccion/06-alg-n2-troqueles/s00-hub-patio-katia.png",
    "cards_hint": "Abre las dos puertas del patio",
    "cards_aria": "Puertas del patio",
    "card_cta": "Entrar",
    "gating_label": "Para cruzar el patio",
    "finish_label": "Entrar en el taller",
    "card_closed_hint": "Toca la puerta para ver qué oficio se aprende dentro.",
    "icebreaker": {
        "title": "Antes de cruzar el patio",
        "intro": (
            "Tres preguntas para calentar. No se califican y no bloquean nada: solo "
            "quiero ver desde dónde partimos."
        ),
        "items": [
            {
                "id": "ICE1",
                "kind": "numeric",
                "prompt": (
                    "En el patio se cierra un fardo juntando 3 sacos de 8 arrobas cada "
                    "uno. ¿Cuántas arrobas pesa el fardo cerrado?"
                ),
                "expr": r"3\times 8",
                "answer": "24",
            },
            {
                "id": "ICE2",
                "kind": "single_select",
                "prompt": (
                    "Ese mismo fardo llega a destino y hay que repartirlo otra vez en "
                    "sacos de 8 arrobas. ¿Cuántos sacos salen?"
                ),
                "options": [
                    {"id": "back", "text": "3, porque es la cuenta de antes al revés"},
                    {"id": "same", "text": "24, uno por arroba"},
                    {"id": "unknown", "text": "No se puede saber sin abrirlo"},
                ],
                "expected": "back",
            },
            {
                "id": "ICE3",
                "kind": "single_select",
                "prompt": (
                    "Si abres un fardo y vuelves a juntar exactamente lo que sacaste, "
                    "¿qué tiene que darte?"
                ),
                "options": [
                    {"id": "identical", "text": "El fardo de partida, idéntico"},
                    {"id": "lighter", "text": "Algo más ligero: al abrirlo se pierde algo"},
                    {"id": "depends", "text": "Depende de cómo lo abras"},
                ],
                "expected": "identical",
            },
        ],
    },
    "advance_text": (
        "Empieza por el taller. El almacén consiste en reconocer huellas, y no se "
        "reconoce una huella que nunca se ha visto estampar."
    ),
    "gating": {"rule": "all_cards_opened", "cards_required": 2},
    "cards": CARDS,
    "feedback": {
        "correct": "¡Correcto!",
        "default": "Revisa la respuesta con calma antes de continuar.",
        "card_opened": "Puerta abierta.",
        "fb_hub_ice2_same": (
            "24 es el peso del fardo, no el número de sacos. → Si cada saco lleva 8 "
            "arrobas, ¿cuántos hacen falta para 24?"
        ),
        "fb_hub_ice2_unknown": (
            "Abrirlo confirma, pero la cuenta ya lo dice: se cerró juntando 3 de 8. "
            "→ ¿Qué operación deshace «juntar 3 grupos de 8»?"
        ),
        "fb_hub_ice3_lighter": (
            "Nada se pierde al abrir: es la misma mercancía en otra disposición. → Si "
            "faltara algo, ¿habrías abierto bien?"
        ),
        "fb_hub_ice3_depends": (
            "Puedes abrirlo de varias formas, pero todas tienen que reconstruir lo "
            "mismo. → Eso es justo lo que se comprueba al volver a juntar."
        ),
    },
    "validation_status": "F5_S00_hub",
}
