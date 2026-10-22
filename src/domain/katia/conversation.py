"""
Spec 005 K3: how a KatIA conversation ends, and the kind of difficulty it showed (FR-031, N2).

A conversation is one student's messages about one item, with KatIA's replies. The next answer to
the item closes it as «superado» or «no superado»; asking for another item, ending the session or
24 hours without a message close it as «abandonado». The difficulty is one label of N2's fixed
list, picked by the model when the conversation closes; anything else is «sin clasificar». Pure:
no I/O.
"""

import unicodedata

OUTCOMES = ("superado", "no_superado", "abandonado")
DIFFICULTIES = ("enunciado", "concepto", "procedimiento", "calculo", "opciones")
UNCLASSIFIED = "sin_clasificar"

HISTORY_TURNS = 6  # earlier turns sent to the provider as context (FR-030)
STALE_AFTER_HOURS = 24  # with no message, the conversation is abandoned (FR-031, FR-032)

_LEAVING = ("other_item", "logout", "expired")

_LABEL_MEANING = {
    "enunciado": "no entendió el enunciado",
    "concepto": "le falta el concepto",
    "procedimiento": "no sabe qué pasos seguir",
    "calculo": "se equivoca en las cuentas",
    "opciones": "leyó mal las opciones",
}


def close_outcome(event: str, is_correct: bool | None = None) -> str:
    """The outcome of a conversation closed by `event`: «answer» (with its result), or one of
    «other_item», «logout», «expired»."""
    if event == "answer":
        if is_correct is None:
            raise ValueError("An answer closes a conversation only with its result.")
        return "superado" if is_correct else "no_superado"
    if event in _LEAVING:
        return "abandonado"
    raise ValueError(f"Unknown way to close a conversation: {event!r}")


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def parse_difficulty(reply: str | None) -> str:
    """The label the model answered, when its whole reply is exactly one label of the list."""
    word = _plain(reply or "").strip().strip(".,;:!¡¿?«»\"'`*()[] \n\t")
    return word if word in DIFFICULTIES else UNCLASSIFIED


def classification_prompt(messages: list[dict]) -> str:
    """The one request that classifies a closed conversation: its turns and the fixed list."""
    lines = [
        f"{'Estudiante' if m['role'] == 'student' else 'KatIA'}: {m['text']}" for m in messages
    ]
    labels = "\n".join(f"- {label}: {meaning}" for label, meaning in _LABEL_MEANING.items())
    return (
        "Clasifica la dificultad que muestra el estudiante en esta conversación con su tutora.\n\n"
        "CONVERSACIÓN:\n" + "\n".join(lines) + "\n\n"
        "ETIQUETAS:\n" + labels + "\n\n"
        "Responde con UNA sola etiqueta de la lista, en minúsculas y sin nada más."
    )
