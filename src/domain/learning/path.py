"""
Spec 003 L5: the rules of the learning path, read from node data only (FR-050, FR-051).

A node is open when its `unlock_after` is completed, every node in its `gates` is completed, and,
if it declares `requires_band`, the student's diagnostic band is one of them. The map and the API
both ask `node_access`, so they cannot disagree. Which interactions a node needs answered before
it completes is its own `interactions` list; a hub (`completion: "cards"`) completes on the server
once every card is opened.

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


def missing_interactions(lesson: dict, answered) -> list[str]:
    """The node's registered interactions with no answer yet, in the node's order."""
    return [
        interaction["interaction_id"]
        for interaction in lesson.get("interactions", [])
        if interaction["interaction_id"] not in answered
    ]


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
