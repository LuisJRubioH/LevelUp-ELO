"""
Spec 003 L2 (FR-020): what of a node's content reaches the browser.

An allow-list projection: a field is sent only when its path is listed in `PUBLIC_PATHS` (or lies
under one of `OPAQUE_PATHS`, maps of display text keyed by feedback key). Anything else — the
grading keys in `GRADING_KEYS`, the internal fields in `INTERNAL_PATHS`, and any field added later
and not yet classified — is left out. The catalogue itself is untouched: the server grades with it.

Paths read `.block.field`, with `[]` for each list level, e.g. `.practice[].options[].text`.
Worked-example `solution` and `correct_version` are teaching content the student is meant to see
(N8); `valid_options` is the list of choices of a multiple-answer item (N7).

Pure domain: no I/O.
"""

from copy import deepcopy

# Grading keys, by field name wherever they appear; plus the abstraction question's `correct`
# flag (N9: that question is graded on the server now).
GRADING_KEYS = frozenset(
    {
        "accepted",
        "answer",
        "expected",
        "feedback_by_option",
        "feedback_correct",
        "feedback_incorrect",
        "feedback_missing",
        "feedback_trap",
        "misconception_by_option",
        "misconception_incorrect",
        "misconception_missing",
        "trap_options",
    }
)

# Fields no renderer reads: authoring and routing data the server keeps.
INTERNAL_PATHS = frozenset(
    {
        ".concept_slug",
        ".misconception",
        ".post_diagnostic.compara_con",
        ".post_diagnostic.trigger_refuerzo",
        ".house",
        ".guide",
        ".validation_status",
    }
)

# Maps of display text keyed by feedback key: copied whole.
OPAQUE_PATHS = frozenset({".feedback"})

PUBLIC_PATHS = frozenset(
    {
        # abstraction_question
        ".abstraction_question",
        ".abstraction_question.options",
        ".abstraction_question.options[].id",
        ".abstraction_question.options[].text",
        ".abstraction_question.prompt",
        ".abstraction_question.thumbnails",
        # advance_text
        ".advance_text",
        # bridge
        ".bridge",
        ".bridge.intro",
        ".bridge.items",
        ".bridge.items[].blanks",
        ".bridge.items[].blanks[].id",
        ".bridge.items[].blanks[].label",
        ".bridge.items[].given_steps",
        ".bridge.items[].id",
        ".bridge.items[].missing",
        ".bridge.items[].presentation",
        ".bridge.items[].statement",
        # building
        ".building",
        # buildings
        ".buildings",
        ".buildings[].building",
        ".buildings[].card",
        ".buildings[].id",
        ".buildings[].node_id",
        ".buildings[].operation",
        ".buildings[].symbol",
        ".buildings[].trade",
        # card_closed_hint
        ".card_closed_hint",
        # card_cta
        ".card_cta",
        # cards
        ".cards",
        ".cards[].concept",
        ".cards[].destination",
        ".cards[].id",
        ".cards[].node_id",
        ".cards[].symbol",
        ".cards[].teaser",
        # cards_aria
        ".cards_aria",
        # cards_hint
        ".cards_hint",
        # closing
        ".closing",
        # closing_item
        ".closing_item",
        ".closing_item.hints",
        ".closing_item.hints.n1",
        ".closing_item.hints.n2",
        ".closing_item.hints.n3",
        ".closing_item.id",
        ".closing_item.polya",
        ".closing_item.polya.comprender",
        ".closing_item.polya.comprobar",
        ".closing_item.polya.ejecutar",
        ".closing_item.polya.planear",
        ".closing_item.prompt",
        ".closing_item.statement",
        # closure
        ".closure",
        ".closure.eyebrow",
        ".closure.intro",
        ".closure.outro",
        ".closure.rows",
        ".closure.rows[].closed",
        ".closure.rows[].latex",
        ".closure.rows[].name",
        ".closure.rows[].note",
        ".closure.rows[].symbol",
        ".closure.title",
        # definition
        ".definition",
        # definition_katex
        ".definition_katex",
        # definition_symbols
        ".definition_symbols",
        ".definition_symbols[].means",
        ".definition_symbols[].reads",
        ".definition_symbols[].symbol",
        # definition_title
        ".definition_title",
        # destination
        ".destination",
        # diagnostic
        ".diagnostic",
        ".diagnostic.intro",
        ".diagnostic.items",
        ".diagnostic.items[].id",
        ".diagnostic.items[].kind",
        ".diagnostic.items[].options",
        ".diagnostic.items[].options[].id",
        ".diagnostic.items[].options[].latex",
        ".diagnostic.items[].options[].text",
        ".diagnostic.items[].prompt",
        ".diagnostic.items[].tipo",
        # discovery
        ".discovery",
        ".discovery.body",
        ".discovery.cases",
        ".discovery.cases[].context",
        ".discovery.cases[].division",
        ".discovery.cases[].fraction",
        ".discovery.cases[].label",
        ".discovery.cases[].note",
        ".discovery.eyebrow",
        ".discovery.resolution",
        ".discovery.title",
        # drag_rule
        ".drag_rule",
        # finish_label
        ".finish_label",
        # footer
        ".footer",
        ".footer.label",
        ".footer.note",
        ".footer.states",
        ".footer.states.consolidacion",
        ".footer.states.repasar",
        ".footer.states.sin_ayuda",
        # gating
        ".gating",
        ".gating.cards_required",
        ".gating.machines_required",
        ".gating.rule",
        # gating_label
        ".gating_label",
        # icebreaker
        ".icebreaker",
        ".icebreaker.intro",
        ".icebreaker.items",
        ".icebreaker.items[].expr",
        ".icebreaker.items[].id",
        ".icebreaker.items[].image",
        ".icebreaker.items[].image_slot",
        ".icebreaker.items[].kind",
        ".icebreaker.items[].options",
        ".icebreaker.items[].options[].id",
        ".icebreaker.items[].options[].text",
        ".icebreaker.items[].prompt",
        ".icebreaker.items[].story",
        ".icebreaker.items[].support_objects",
        ".icebreaker.items[].valid_options",
        ".icebreaker.title",
        # image
        ".image",
        # intro
        ".intro",
        # katia
        ".katia",
        ".katia.attempt",
        ".katia.attempt.format",
        ".katia.attempt.options",
        ".katia.attempt.options[].id",
        ".katia.attempt.options[].latex",
        ".katia.attempt.options[].text",
        ".katia.attempt.prompt",
        ".katia.attempt.response",
        ".katia.body",
        ".katia.eyebrow",
        ".katia.image",
        ".katia.question",
        ".katia.title",
        # kicker
        ".kicker",
        # kind
        ".kind",
        # level
        ".level",
        # machines
        ".machines",
        ".machines[].demo",
        ".machines[].id",
        ".machines[].katia_message",
        ".machines[].node_id",
        ".machines[].property",
        ".machines[].station",
        ".machines[].symbol",
        # method_comparison
        ".method_comparison",
        ".method_comparison.insight",
        ".method_comparison.intro",
        ".method_comparison.methods",
        ".method_comparison.methods[].label",
        ".method_comparison.methods[].note",
        ".method_comparison.methods[].steps",
        ".method_comparison.question",
        ".method_comparison.title",
        # post_diagnostic
        ".post_diagnostic",
        ".post_diagnostic.intro",
        ".post_diagnostic.items",
        ".post_diagnostic.items[].id",
        ".post_diagnostic.items[].kind",
        ".post_diagnostic.items[].options",
        ".post_diagnostic.items[].options[].id",
        ".post_diagnostic.items[].options[].latex",
        ".post_diagnostic.items[].options[].text",
        ".post_diagnostic.items[].prompt",
        ".post_diagnostic.items[].tipo",
        ".post_diagnostic.outcome_flat",
        ".post_diagnostic.outcome_gain",
        ".post_diagnostic.resultados",
        # practice
        ".practice",
        ".practice[].confidence",
        ".practice[].expr",
        ".practice[].hints",
        ".practice[].hints.n1",
        ".practice[].hints.n2",
        ".practice[].hints.n3",
        ".practice[].id",
        ".practice[].kind",
        ".practice[].options",
        ".practice[].options[].id",
        ".practice[].options[].latex",
        ".practice[].options[].text",
        ".practice[].prompt",
        ".practice[].tipo",
        ".practice[].valid_options",
        # scene
        ".scene",
        ".scene.aria",
        ".scene.image",
        ".scene.step",
        # scene_text
        ".scene_text",
        # staircase
        ".staircase",
        ".staircase.aria",
        ".staircase.chain",
        ".staircase.image",
        ".staircase.steps",
        ".staircase.steps[].explanation",
        ".staircase.steps[].name",
        ".staircase.steps[].question",
        ".staircase.steps[].symbol",
        # station
        ".station",
        # story_contract
        ".story_contract",
        ".story_contract.is_integrated",
        ".story_contract.practice_position",
        ".story_contract.type",
        # title
        ".title",
        # welcome_text
        ".welcome_text",
        # worked_examples
        ".worked_examples",
        ".worked_examples[].confidence_prompt",
        ".worked_examples[].correct_version",
        ".worked_examples[].correct_version.right_latex",
        ".worked_examples[].correct_version.rows",
        ".worked_examples[].correct_version.rows[].right",
        ".worked_examples[].correct_version.rows[].wrong",
        ".worked_examples[].correct_version.wrong_latex",
        ".worked_examples[].error_latex",
        ".worked_examples[].error_note",
        ".worked_examples[].explain_prompt",
        ".worked_examples[].eyebrow",
        ".worked_examples[].image",
        ".worked_examples[].image_slot",
        ".worked_examples[].latex",
        ".worked_examples[].self_explanation",
        ".worked_examples[].self_explanation.prompt",
        ".worked_examples[].self_explanation.step_index",
        ".worked_examples[].solution",
        ".worked_examples[].statement",
        ".worked_examples[].steps",
        ".worked_examples[].title",
        ".worked_examples[].trap",
    }
)


def public_content(content: dict | None) -> dict | None:
    """The content a lesson response carries: the allow-listed fields only, as a new object."""
    if content is None:
        return None
    return _project(content, "")


def _project(value, path: str):
    if isinstance(value, dict):
        projected = {}
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if child_path in OPAQUE_PATHS:
                projected[key] = deepcopy(child)
            elif child_path in PUBLIC_PATHS:
                projected[key] = _project(child, child_path)
        return projected
    if isinstance(value, (list, tuple)):
        return [_project(child, f"{path}[]") for child in value]
    return value
