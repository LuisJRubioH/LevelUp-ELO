"""Spec 005 K2 (FR-022): the reply check is pure domain."""

import pytest

from src.domain.katia.guardrail import REVEALING_PHRASES, check_reply

CORRECT = "$3x^2$"


@pytest.mark.parametrize(
    "reply",
    [
        "¿Qué regla de derivación conoces para potencias?",
        "Mira el exponente. ¿Qué le pasa al derivar? ¿Y al coeficiente?",
        "",
    ],
)
def test_a_reply_that_only_guides_passes(reply):
    assert check_reply(reply, CORRECT)


@pytest.mark.parametrize(
    "reply",
    [
        "Muy bien, es $3x^2$.",
        "Es 3x^2, ¿lo ves?",  # without the LaTeX delimiters
        "Es $3 x^2$.",  # spaces inside
        "LA RESPUESTA ES la primera.",
        "Paso 1: deriva.",
        "Uno. Dos. Tres. Cuatro.",
    ],
)
def test_a_reply_that_gives_too_much_is_refused(reply):
    assert not check_reply(reply, CORRECT)


def test_the_phrases_are_the_thirteen_of_today():
    assert len(REVEALING_PHRASES) == 13
    assert "la respuesta correcta es" in REVEALING_PHRASES


def test_a_short_correct_option_does_not_refuse_every_reply():
    """A one-character option ("2") is not matched inside other numbers or words."""
    assert check_reply("¿Cuántos términos tiene la expresión 12x?", "2")
    assert not check_reply("Es 2.", "2")
