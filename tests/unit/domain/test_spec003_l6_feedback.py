"""
Spec 003 L6 (US7; FR-060 … FR-062, SC-004; N12): a multiple-answer question tells a partial
answer from a wrong one, and nothing that is graded or stored moves.

The pins (`[AS-IS]`) were written first and recorded from the unchanged code: the grade and the
misconception tag of every selection every multiple-answer interaction admits, and the feedback
key of every interaction that defines its own message.
"""

import hashlib
from itertools import combinations

from src.domain.learning import prealgebra

MULTI = {
    interaction_id: rule
    for interaction_id, rule in sorted(prealgebra._INTERACTION_RULES.items())
    if rule.get("input_kind") == "multi_select"
}
OWN_RULES = [i for i, rule in MULTI.items() if "error_rules" in rule]
ICEBREAKER = "PREALG-N4-C00-PUERTO-DE-LA-POLIS-ICE1"

# Recorded from the code before L6 (main at e83dd55). FR-062: these two never change.
GRADE_AND_TAG_DIGEST = "847733e39f86daecf6be6ec598c23eb4b1331d50ace4f3c9cb878b7bfaf4b07a"
OWN_RULES_FEEDBACK_DIGEST = "353feee59d89296996c1c967fee48310d20bc49ee4117a158912adb61fa148f3"


def _selections(rule):
    """Every selection the interaction admits: each non-empty subset of its options."""
    options = sorted(rule["valid_options"])
    for size in range(1, len(options) + 1):
        for chosen in combinations(options, size):
            yield set(chosen)


def _answers(interaction_ids):
    for interaction_id in interaction_ids:
        rule = MULTI[interaction_id]
        for selection in _selections(rule):
            sent = ",".join(sorted(selection))
            graded = prealgebra.evaluate_interaction(rule["node_id"], interaction_id, sent)
            yield interaction_id, rule, selection, sent, graded


def _digest(lines):
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def test_grade_and_tag_of_every_multiple_answer_selection_are_unchanged():
    """FR-062, US7-AS3: right only as the whole right set; every selection keeps its tag."""
    lines = []
    for interaction_id, rule, selection, sent, graded in _answers(MULTI):
        assert graded["is_expected"] is (selection == rule["expected"]), (interaction_id, sent)
        lines.append(
            f"{interaction_id}\t{sent}\t{graded['is_expected']}\t{graded['misconception_tag']}"
        )

    assert len(MULTI) == 92
    assert len(lines) == 5916
    assert _digest(lines) == GRADE_AND_TAG_DIGEST


def test_an_interaction_with_its_own_message_keeps_it():
    """US7-AS4: the C00 icebreaker's `feedback_missing` and the `error_rules` interactions."""
    rule = MULTI[ICEBREAKER]
    assert rule["feedback_missing"] == "fb_hub_ice1_missing"
    missing = 0
    for _, _, selection, sent, graded in _answers([ICEBREAKER]):
        if rule["expected"] - selection:
            missing += 1
            assert graded["feedback_key"] == "fb_hub_ice1_missing", sent
    assert missing == 4095 - 2**6  # every selection that leaves a right option out

    row = "PREALG-N1-B11-ROW-minus3"
    node_id = MULTI[row]["node_id"]
    keys = {
        sent: prealgebra.evaluate_interaction(node_id, row, sent)["feedback_key"]
        for sent in ("c,q,r,z", "c,r,z", "q,r,z", "c,q,z", "c,n,q,r,z", "c,q,r")
    }
    assert keys == {
        "c,q,r,z": "row_correct",
        "c,r,z": "integer_not_rational",
        "q,r,z": "real_not_complex",
        "c,q,z": "rational_not_real",
        "c,n,q,r,z": "row_review",
        "c,q,r": "row_review",
    }

    assert len(OWN_RULES) == 8
    lines = [
        f"{interaction_id}\t{sent}\t{graded['feedback_key']}"
        for interaction_id, _, _, sent, graded in _answers(OWN_RULES)
    ]
    assert len(lines) == 8 * 63
    assert _digest(lines) == OWN_RULES_FEEDBACK_DIGEST
