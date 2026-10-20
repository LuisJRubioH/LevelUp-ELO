"""
Spec 003 L4 (FR-041; N11): the outcome rule and the labels the teacher reads are domain rules.
"""

import pytest

from src.domain.learning import prealgebra
from src.domain.learning.path import interaction_label, post_diagnostic_outcome

ELEVEN_BLOCK = [
    n
    for n, lesson in prealgebra._LESSONS.items()
    if (lesson.get("content") or {}).get("kind") == "eleven_block_node"
]


def _ids(lesson, block):
    return [f"{lesson['node_id']}-{i['id']}" for i in lesson["content"][block]["items"]]


@pytest.mark.parametrize("node_id", ELEVEN_BLOCK[:3])
def test_the_outcome_waits_for_every_post_item_and_is_gain_or_flat(node_id):
    """FR-041: none until every post item is answered; gain when post > diagnostic, else flat."""
    lesson = prealgebra._LESSONS[node_id]
    diagnostic, post = _ids(lesson, "diagnostic"), _ids(lesson, "post_diagnostic")
    answers = {i: {"is_expected": True} for i in diagnostic}
    answers.update({i: {"is_expected": True} for i in post[:-1]})
    assert post_diagnostic_outcome(lesson, answers) is None

    answers[post[-1]] = {"is_expected": True}
    assert post_diagnostic_outcome(lesson, answers)["outcome"] == "flat"  # equal: no gain
    for i in diagnostic:
        answers[i] = {"is_expected": False}
    assert post_diagnostic_outcome(lesson, answers) == {
        "diagnostic_correct": 0,
        "post_correct": len(post),
        "items": len(post),
        "outcome": "gain",
    }


def test_every_interaction_of_the_catalogue_has_a_label():
    """N11: the teacher reads where the item is, never its text or the chosen value."""
    for node_id, lesson in prealgebra._LESSONS.items():
        content = lesson.get("content") or {}
        ids = [i["interaction_id"] for i in lesson.get("interactions", [])]
        for block in ("diagnostic", "post_diagnostic", "icebreaker"):
            ids += [f"{node_id}-{i['id']}" for i in (content.get(block) or {}).get("items", [])]
        for interaction_id in ids:
            label = interaction_label(lesson, interaction_id)
            assert label and interaction_id not in label, (node_id, interaction_id, label)
    lesson = prealgebra._LESSONS[ELEVEN_BLOCK[0]]
    assert interaction_label(lesson, _ids(lesson, "diagnostic")[1]) == "Diagnóstico 2"
    assert interaction_label(lesson, _ids(lesson, "post_diagnostic")[0]) == "Post-diagnóstico 1"
    assert interaction_label(lesson, f"{lesson['node_id']}-ABSTRACCION") == "Abstracción"
