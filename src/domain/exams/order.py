"""
Spec 006 AL (FR-028): the order in which a template's items and options are shown.

Each session draws its own order of the items, and each item's options are shuffled from a seed
made of the session and the item, so a resumed session (FR-025) shows the same order without
storing it. An option that refers to the others («Ninguna de las anteriores», «Todas las
anteriores») keeps its place at the end, where it makes sense. Grading compares the chosen
option's text, so no order changes a result. Pure: no I/O.
"""

import random
import re

# «Ninguna de las anteriores», «Todos los anteriores», «Ninguno de los anteriores» and the like.
_REFERS_TO_THE_OTHERS = re.compile(
    r"^\s*(ninguna|ninguno|todas|todos)\s+(de\s+)?(las|los)\s+(opciones\s+)?anteriores\b",
    re.IGNORECASE,
)


def refers_to_the_others(option: str) -> bool:
    """Whether an option only makes sense after the others («Ninguna de las anteriores»)."""
    return bool(_REFERS_TO_THE_OTHERS.match(str(option)))


def item_order(item_ids: list[str], rng: random.Random) -> list[str]:
    """A new order of the items, drawn with `rng`; the list given is not changed."""
    order = list(item_ids)
    rng.shuffle(order)
    return order


def option_order(options: list[str], session_id: str, item_id: str) -> list[str]:
    """The options of one item in the order this session shows them: the same for the same
    session and item every time, different from one session to another. Options that refer to
    the others stay last, in their own order."""
    movable = [o for o in options if not refers_to_the_others(o)]
    anchored = [o for o in options if refers_to_the_others(o)]
    random.Random(f"{session_id}:{item_id}").shuffle(movable)
    return movable + anchored
