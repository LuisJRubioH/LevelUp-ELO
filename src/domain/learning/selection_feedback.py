"""
Spec 003 L6 (FR-060, FR-061; N12): what a multiple-answer question says to a selection that is
not the whole right set, when the question defines no message of its own for the case.

Two messages, shared by every node: one for a selection of right options only that leaves some
out, one for a selection that holds an option that is not right (a trap option included).
Neither names an option. They decide only the text: the grade and the misconception tag of an
answer are decided elsewhere and do not depend on them (FR-062).

Pure domain: no I/O.
"""

SELECTION_INCOMPLETE = "selection_incomplete"
SELECTION_HAS_WRONG = "selection_has_wrong"

# The one place both texts live (approved by the owner, 2026-11-12, QA round 1 decision D1).
SELECTION_FEEDBACK = {
    SELECTION_INCOMPLETE: (
        "Vas bien: lo que marcaste es correcto, pero falta al menos una opción más."
    ),
    SELECTION_HAS_WRONG: (
        "Al menos una de las opciones que marcaste no es correcta. Revísalas una por una."
    ),
}


def selection_feedback_key(selected: set, expected: set) -> str:
    """The shared key for a selection that is not the whole right set."""
    return SELECTION_INCOMPLETE if selected <= expected else SELECTION_HAS_WRONG


def with_selection_feedback(content: dict) -> dict:
    """A copy of a node's content whose `feedback` holds both shared texts.

    A text the node declares under either key wins. The node's own content is not modified.
    """
    return {**content, "feedback": {**SELECTION_FEEDBACK, **(content.get("feedback") or {})}}
