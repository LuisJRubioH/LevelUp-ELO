"""
Spec 003 L3 (FR-030; N1, N2, N3; V2-R11): one completion rule, read from node data.
"""

import pytest

from src.domain.learning import prealgebra
from src.domain.learning.path import completion_gaps, completion_refused

ELEVEN_BLOCK = [
    node_id
    for node_id, lesson in prealgebra._LESSONS.items()
    if (lesson.get("content") or {}).get("kind") == "eleven_block_node"
]


def _node(completion=None):
    lesson = {
        "node_id": "X",
        "content": {"practice": [{"id": "E1"}, {"id": "E2"}], "closing_item": {"id": "C"}},
        "interactions": [{"interaction_id": f"X-{suffix}"} for suffix in ("E1", "E2", "C")],
    }
    if completion:
        lesson["completion"] = completion
    return lesson


def test_the_default_rule_needs_every_latest_answer_right():
    """FR-030: wrong and unanswered are both gaps, labelled where the student finds them."""
    answers = {"X-E1": {"is_expected": True}, "X-C": {"is_expected": False}}
    gaps = completion_gaps(_node(), answers)

    assert [g["interaction_id"] for g in gaps] == ["X-E2", "X-C"]
    assert completion_refused(_node(), gaps) == "Te falta acertar: Práctica 2 y Cierre."
    every_right = {f"X-{s}": {"is_expected": True} for s in ("E1", "E2", "C")}
    assert completion_gaps(_node(), every_right) == []


def test_view_answered_and_cards_rules():
    """N1: view needs nothing. N2: answered accepts wrong answers. N3: cards need each opened."""
    wrong = {f"X-{s}": {"is_expected": False} for s in ("E1", "E2", "C")}
    assert completion_gaps(_node("view"), {}) == []
    assert completion_gaps(_node("answered"), wrong) == []
    assert completion_refused(_node("answered"), completion_gaps(_node("answered"), {})) == (
        "Te falta responder: Práctica 1, Práctica 2 y Cierre."
    )
    cards = completion_gaps(_node("cards"), {"X-E1": {"is_expected": None}})
    assert completion_refused(_node("cards"), cards) == "Te falta abrir: Tarjeta 2 y Tarjeta 3."


def test_every_eleven_block_node_completes_on_right_answers():
    """FR-030: the rule is data on the node; every eleven-block node uses `correct`."""
    assert ELEVEN_BLOCK
    assert {prealgebra._LESSONS[n]["completion"] for n in ELEVEN_BLOCK} == {"correct"}


@pytest.mark.parametrize("node_id", ELEVEN_BLOCK)
def test_diagnostic_items_never_gate(node_id):
    """V2-R11: practice and closing right, every diagnostic, bridge and post-diagnostic item
    unanswered → no gap. No `required=False` interaction is ever a gap."""
    lesson = prealgebra._LESSONS[node_id]
    content = lesson["content"]
    optional = {
        f"{node_id}-{item['id']}"
        for block in ("diagnostic", "post_diagnostic")
        for item in (content.get(block) or {}).get("items", [])
    } | {
        f"{node_id}-{blank['id']}"
        for item in (content.get("bridge") or {}).get("items", [])
        for blank in item["blanks"]
    }
    right = {
        i["interaction_id"]: {"is_expected": True}
        for i in lesson["interactions"]
        if i["interaction_id"] not in optional
    }

    assert completion_gaps(lesson, right) == []
    assert not optional & {i["interaction_id"] for i in lesson["interactions"]}
