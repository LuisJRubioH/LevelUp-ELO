"""
Spec 003 L5: the rules of the learning path, read from node data only (FR-050, FR-051).

A node is open when its `unlock_after` is completed, every node in its `gates` is completed, and,
if it declares `requires_band`, the student's diagnostic band is one of them. The map and the API
both ask `node_access`, so they cannot disagree. When a node completes is its `completion` field
(L3, `completion_gaps`); a hub (`completion: "cards"`) completes on the server once every card is
opened.

Pure domain: no I/O. `state_of` is a function node_id -> stored state, supplied by the caller.
"""

UNLOCK_REFUSED = "Completa el nodo anterior primero"
BAND_REFUSED = "Nodo opcional disponible solo para banda intermedia o avanzada"
GATES_REFUSED = "Completa los nodos que abren este primero"


class CatalogueError(ValueError):
    """The catalogue cannot be walked: not one root, a reference to a missing node, a cycle."""


def prerequisites(lesson: dict) -> list[str]:
    """Every node that must be completed before this one opens."""
    first = [lesson["unlock_after"]] if lesson.get("unlock_after") else []
    return first + list(lesson.get("gates") or [])


def node_access(lesson: dict, state_of, band: str) -> str | None:
    """None when the node is open; otherwise why it is closed, as the student reads it."""
    if lesson.get("unlock_after") and state_of(lesson["unlock_after"]) != "completed":
        return UNLOCK_REFUSED
    gates = lesson.get("gates") or []
    if not all(state_of(node_id) == "completed" for node_id in gates):
        return lesson.get("gates_refused", GATES_REFUSED)
    bands = lesson.get("requires_band")
    if bands and band not in bands:
        return BAND_REFUSED
    return None


def shown_in_band(lesson: dict, band: str | None) -> bool:
    """A node that needs a band the student lacks is not shown on the map at all."""
    bands = lesson.get("requires_band")
    return band is None or not bands or band in bands


def completes_on_cards(lesson: dict) -> bool:
    return lesson.get("completion") == "cards"


def validate_catalogue(lessons: dict) -> None:
    """FR-051: exactly one root, every reference names a node, no cycle."""
    roots = [node_id for node_id, lesson in lessons.items() if not lesson.get("unlock_after")]
    if len(roots) != 1:
        raise CatalogueError(f"the catalogue must have one root, it has {len(roots)}: {roots}")
    for node_id, lesson in lessons.items():
        for needed in prerequisites(lesson):
            if needed not in lessons:
                raise CatalogueError(f"{node_id} needs {needed}, which is missing")
    done, visiting = set(), set()

    def visit(node_id):
        if node_id in done:
            return
        if node_id in visiting:
            raise CatalogueError(f"the unlock rules have a cycle through {node_id}")
        visiting.add(node_id)
        for needed in prerequisites(lessons[node_id]):
            visit(needed)
        visiting.discard(node_id)
        done.add(node_id)

    for node_id in lessons:
        visit(node_id)


# ── Completion (spec 003 L3, FR-030; N1, N2, N3) ─────────────────────────────
# A node's `completion` field says what «done» means:
#   view      — opening it is enough (B01: no question, N1);
#   answered  — every required interaction has an answer, right or wrong (B13, N2; B02, a
#               safe-zone prompt that is not an eleven-block node);
#   cards     — every card opened (hubs, N3);
#   correct   — the latest answer of every required interaction is right (FR-030; the default).

REFUSED_PREFIX = {
    "correct": "Te falta acertar",
    "answered": "Te falta responder",
    "cards": "Te falta abrir",
}


def completion_rule(lesson: dict) -> str:
    return lesson.get("completion", "correct")


def _gap_label(lesson: dict, interaction_id: str, position: int) -> str:
    """Where the student finds the item, never its text: «Práctica 2», «Cierre», «Pregunta 1»."""
    if completion_rule(lesson) == "cards":
        return f"Tarjeta {position}"
    node_id = lesson["node_id"]
    content = lesson.get("content") or {}
    practice = [f"{node_id}-{item['id']}" for item in content.get("practice") or []]
    if interaction_id in practice:
        return f"Práctica {practice.index(interaction_id) + 1}"
    closing = content.get("closing_item")
    if closing and interaction_id == f"{node_id}-{closing['id']}":
        return "Cierre"
    return f"Pregunta {position}"


def completion_gaps(lesson: dict, latest_answers) -> list[dict]:
    """The required interactions that keep the node from completing, in the node's order.

    `latest_answers` maps interaction_id -> the stored current answer ({"is_expected": …}).
    Each gap is {"interaction_id", "label"}; an empty list means the node may complete.
    """
    rule = completion_rule(lesson)
    if rule == "view":
        return []
    gaps = []
    for position, interaction in enumerate(lesson.get("interactions", []), start=1):
        interaction_id = interaction["interaction_id"]
        answer = latest_answers.get(interaction_id)
        missing = answer is None or (rule == "correct" and answer.get("is_expected") is not True)
        if missing:
            gaps.append(
                {
                    "interaction_id": interaction_id,
                    "label": _gap_label(lesson, interaction_id, position),
                }
            )
    return gaps


def completion_refused(lesson: dict, gaps: list[dict]) -> str:
    """«Te falta acertar: Práctica 2 y Cierre.»"""
    labels = [gap["label"] for gap in gaps]
    listed = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " y " + labels[-1]
    return f"{REFUSED_PREFIX[completion_rule(lesson)]}: {listed}."
