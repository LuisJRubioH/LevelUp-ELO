"""
Spec 005 delivery K3 (FR-031, N2): how a KatIA conversation ends, and the kind of difficulty.

The next answer to the item closes it as «superado» or «no superado»; asking for another item,
ending the session or 24 hours of silence close it as «abandonado». The difficulty is one label of
N2's fixed list; anything else the model writes is «sin clasificar». Pure domain.
"""

import pytest

from src.domain.katia.conversation import (
    DIFFICULTIES,
    UNCLASSIFIED,
    classification_prompt,
    close_outcome,
    parse_difficulty,
)


@pytest.mark.parametrize(
    "event, is_correct, outcome",
    [
        ("answer", True, "superado"),
        ("answer", False, "no_superado"),
        ("other_item", None, "abandonado"),
        ("logout", None, "abandonado"),
        ("expired", None, "abandonado"),
    ],
)
def test_each_way_out_has_its_outcome(event, is_correct, outcome):
    assert close_outcome(event, is_correct) == outcome


def test_an_answer_needs_its_result_and_an_unknown_event_is_refused():
    with pytest.raises(ValueError):
        close_outcome("answer")
    with pytest.raises(ValueError):
        close_outcome("timeout")


def test_the_difficulties_are_the_five_of_n2():
    assert DIFFICULTIES == ("enunciado", "concepto", "procedimiento", "calculo", "opciones")
    assert UNCLASSIFIED == "sin_clasificar"


@pytest.mark.parametrize(
    "reply, label",
    [
        ("procedimiento", "procedimiento"),
        ("  Concepto. ", "concepto"),
        ("Cálculo", "calculo"),
        ("«opciones»", "opciones"),
        ("enunciado\n", "enunciado"),
        ("Creo que es de concepto", UNCLASSIFIED),
        ("concepto, cálculo", UNCLASSIFIED),
        ("álgebra", UNCLASSIFIED),
        ("", UNCLASSIFIED),
        (None, UNCLASSIFIED),
    ],
)
def test_only_one_exact_label_is_accepted(reply, label):
    assert parse_difficulty(reply) == label


def test_the_classification_prompt_holds_the_turns_and_the_labels():
    prompt = classification_prompt(
        [
            {"role": "student", "text": "no entiendo qué pide"},
            {"role": "katia", "text": "¿Qué te pide calcular?"},
        ]
    )
    assert "no entiendo qué pide" in prompt and "¿Qué te pide calcular?" in prompt
    assert all(label in prompt for label in DIFFICULTIES)
