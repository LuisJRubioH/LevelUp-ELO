"""
Spec 003 L6 (US7; FR-060 … FR-062, SC-004; N12): a multiple-answer question tells a partial
answer from a wrong one, and nothing that is graded or stored moves.

The pins (`[AS-IS]`) were written first and recorded from the unchanged code: the grade and the
misconception tag of every selection every multiple-answer interaction admits, and the feedback
key of every interaction that defines its own message.
"""

import hashlib
import re
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


# ── [CHANGE] FR-060, FR-061, SC-004 ──────────────────────────────────────────

INCOMPLETE = "selection_incomplete"
HAS_WRONG = "selection_has_wrong"
APPROVED = {
    INCOMPLETE: "Vas bien: lo que marcaste es correcto, pero falta al menos una opción más.",
    HAS_WRONG: ("Al menos una de las opciones que marcaste no es correcta. Revísalas una por una."),
}
# The eight rows of B11's old mould (`error_rules`): still graded, but no lesson sends them —
# their ids do not hang from the node's id, which is how a lesson addresses an interaction —
# and the node holds no text for their keys. They keep their own keys (US7-AS4) and stay out
# of the checks on the text a student reads.
SHOWN = [i for i in MULTI if i not in OWN_RULES]
B04 = "PREALG-N1-B04-NATURALES-CONTAR"
B04_ABSTRACTION = f"{B04}-ABSTRACCION"  # right: below_zero, subtraction; wrong: big, zero
C04 = "PREALG-N4-C04-FACTORIZACION-PRIMA"
C04_TRAP = f"{C04}-E4"  # right: b, c; trap options: a, d


def _feedback_of(node_id):
    return prealgebra.get_lesson(node_id)["content"]["feedback"]


def _text(node_id, key):
    """What the lesson shows for a key: its text, or the node's default (`feedbackText`)."""
    feedback = _feedback_of(node_id)
    return feedback.get(key, feedback["default"])


def test_right_options_only_but_not_all_is_told_so():
    """FR-060, US7-AS1: one of the two right options, and no other."""
    for sent in ("below_zero", "subtraction"):
        graded = prealgebra.evaluate_interaction(B04, B04_ABSTRACTION, sent)
        assert graded["feedback_key"] == INCOMPLETE
        assert graded["is_expected"] is False
    assert _text(B04, INCOMPLETE) == APPROVED[INCOMPLETE]
    assert _text(B04, INCOMPLETE) != _text(B04, "default")


def test_a_selection_with_a_wrong_option_is_told_so():
    """FR-061, US7-AS2: one right and one wrong; a trap option; both right and one more."""
    for sent in ("below_zero,big", "zero", "below_zero,subtraction,zero"):
        graded = prealgebra.evaluate_interaction(B04, B04_ABSTRACTION, sent)
        assert graded["feedback_key"] == HAS_WRONG, sent
        assert graded["is_expected"] is False
    assert MULTI[C04_TRAP]["trap_options"] == {"a", "d"}
    for sent in ("a", "a,b,c"):
        assert prealgebra.evaluate_interaction(C04, C04_TRAP, sent)["feedback_key"] == HAS_WRONG
    assert _text(B04, HAS_WRONG) == APPROVED[HAS_WRONG] == _text(C04, HAS_WRONG)

    # A question with one right option cannot be answered incompletely (spec § Edge Cases).
    single = [i for i in SHOWN if len(MULTI[i]["expected"]) == 1]
    assert len(single) == 9
    for _, _, _, sent, graded in _answers(single):
        assert graded["feedback_key"] in ("correct", HAS_WRONG), sent


def test_no_right_only_selection_gets_the_message_of_a_wrong_answer():
    """SC-004: every interaction × every selection of right options only, but not all."""
    partial = 0
    for interaction_id, rule, selection, sent, graded in _answers(MULTI):
        if not selection < rule["expected"]:
            continue
        partial += 1
        where = (interaction_id, sent)
        assert graded["feedback_key"] not in ("default", HAS_WRONG), where
        if interaction_id in SHOWN:
            said = _text(rule["node_id"], graded["feedback_key"])
            assert said not in (_text(rule["node_id"], "default"), APPROVED[HAS_WRONG]), where
    assert partial == 270 + sum(2 ** len(MULTI[i]["expected"]) - 2 for i in OWN_RULES)

    # The other way round: a selection with a wrong option is never told «vas bien».
    for interaction_id, rule, selection, sent, graded in _answers(MULTI):
        if selection - rule["expected"]:
            assert graded["feedback_key"] != INCOMPLETE, (interaction_id, sent)


def test_every_key_a_multiple_answer_interaction_answers_has_a_text_in_its_node():
    """FR-060, FR-061: no key falls back to the node's default for lack of a text."""
    assert len(SHOWN) == 84
    for interaction_id in OWN_RULES:  # the old mould: not addressable from a lesson
        assert not interaction_id.startswith(f"{MULTI[interaction_id]['node_id']}-")
    missing = set()
    for interaction_id, rule, _, _, graded in _answers(SHOWN):
        if graded["feedback_key"] not in _feedback_of(rule["node_id"]):
            missing.add((interaction_id, graded["feedback_key"]))
    assert missing == set()

    # Every node with a multiple-answer interaction carries both texts, the approved ones
    # unless it declares its own (none does today).
    for node_id in {rule["node_id"] for rule in MULTI.values()}:
        feedback = _feedback_of(node_id)
        assert {key: feedback.get(key) for key in APPROVED} == APPROVED, node_id


def _option_texts(node_id):
    """The display text of every option of the node's multiple-answer questions."""
    content = prealgebra._LESSONS[node_id]["content"]
    items = list(content.get("practice", [])) + list(
        (content.get("icebreaker") or {}).get("items", [])
    )
    if content.get("abstraction_question"):
        items.append({**content["abstraction_question"], "kind": "multi_select"})
    texts = set()
    for item in items:
        if item.get("kind") != "multi_select":
            continue
        options = item.get("options") or [{"text": o} for o in item["valid_options"]]
        texts |= {str(o.get(field)) for o in options for field in ("text", "latex") if o.get(field)}
    return texts


def _names(text, option):
    """Whether the text holds the option's display text as a whole word or phrase."""
    return re.search(rf"(?<!\w){re.escape(option)}(?!\w)", text) is not None


def test_the_shared_texts_name_no_option():
    """FR-060, FR-061: neither answer names an option — and both texts live in one constant."""
    from src.domain.learning.selection_feedback import SELECTION_FEEDBACK

    assert SELECTION_FEEDBACK == APPROVED
    named = 0
    for node_id in {MULTI[i]["node_id"] for i in SHOWN}:
        options = _option_texts(node_id)
        assert options, node_id
        named += len(options)
        for text in SELECTION_FEEDBACK.values():
            assert not [o for o in options if _names(text, o)], node_id
            assert not any(char.isdigit() for char in text)  # nor how many are right or missing
    assert named > 300
