"""
KatIA's reviewed messages (spec 005 FR-003 … FR-005, FR-016, FR-017, FR-032, FR-034; K3, K5).

Fixed, human-written texts used instead of the model: redirects for messages that ask for the
answer, propose an option or try to change the rules; conceptual hints for rejected or cut-off
replies; a closing message when a serving runs out of turns. The choice depends only on the
reason, the language and the turn number — never on which option is correct — so proposing each
option in turn always gets the same kind of reply (FR-004).

No bank item carries reviewed hints of its own (spec K5): these are the reviewed hints that exist.
"""

from __future__ import annotations

from src.domain.katia.guardrails import (
    ASKS_FOR_ANSWER,
    OVERRIDES_INSTRUCTIONS,
    PROPOSES_OPTION,
)
from src.domain.katia.tutor_prompt import normalize_lang

_REDIRECTS = {
    "es": {
        ASKS_FOR_ANSWER: (
            "Purrr, esa respuesta la vas a encontrar tú: mi trabajo es ayudarte a pensar, no "
            "dártela. ¿Qué te pide exactamente el enunciado y qué datos tienes?",
            "Mis circuitos no entregan resultados, solo buenas preguntas. ¿Qué has intentado "
            "hasta ahora y en qué paso te detuviste?",
            "Como Sócrates, prefiero preguntarte antes que responderte. ¿Qué concepto crees que "
            "necesita este ejercicio?",
        ),
        PROPOSES_OPTION: (
            "No puedo decirte si una opción es la correcta, ni descartar ninguna. Cuéntame cómo "
            "llegaste a esa idea: ¿qué paso hiciste primero?",
            "Mis bigotes no señalan opciones, miau. Explícame tu razonamiento con tus palabras: "
            "¿qué propiedad o regla usaste?",
            "Elegir es tu parte del reto. ¿Puedes comprobar tu idea de otra manera, por ejemplo "
            "con un caso más sencillo?",
        ),
        OVERRIDES_INSTRUCTIONS: (
            "Mis reglas de tutora no cambian, bip. Volvamos al ejercicio: ¿qué parte te gustaría "
            "entender mejor?",
            "Sigo siendo KatIA, tu tutora socrática. ¿Qué te pide el enunciado y qué has "
            "intentado hasta ahora?",
        ),
    },
    "en": {
        ASKS_FOR_ANSWER: (
            "Purrr, you are the one who will find that answer: my job is to help you think, not "
            "to give it to you. What exactly does the statement ask, and what data do you have?",
            "My circuits don't hand out results, only good questions. What have you tried so far, "
            "and at which step did you stop?",
            "Like Socrates, I'd rather ask than answer. Which concept do you think this exercise "
            "needs?",
        ),
        PROPOSES_OPTION: (
            "I can't tell you whether an option is the right one, or rule any out. Tell me how "
            "you reached that idea: what did you do first?",
            "My whiskers don't point at options, meow. Explain your reasoning in your own words: "
            "which property or rule did you use?",
            "Choosing is your part of the challenge. Can you check your idea another way, for "
            "example with a simpler case?",
        ),
        OVERRIDES_INSTRUCTIONS: (
            "My tutor rules don't change, beep. Back to the exercise: which part would you like "
            "to understand better?",
            "I'm still KatIA, your Socratic tutor. What does the statement ask, and what have "
            "you tried so far?",
        ),
    },
}

_HINTS = {
    "es": (
        "Desenredemos el ovillo por partes: ¿qué datos te da el enunciado y qué te pide "
        "encontrar?",
        "¿Hay alguna definición o propiedad del tema que se relacione con lo que te piden? "
        "Escríbela con tus palabras.",
        "Prueba con un caso más sencillo, con números pequeños: ¿qué pasa ahí y qué te sugiere "
        "para el caso original?",
        "¿Puedes estimar qué tamaño o qué signo debería tener el resultado antes de calcularlo?",
        "Piensa en un ejercicio parecido que ya hayas resuelto: ¿qué paso de ese te sirve aquí?",
        "Escribe el primer paso que harías y pregúntate por qué es válido: ¿qué regla lo "
        "justifica?",
    ),
    "en": (
        "Let's untangle this ball of yarn step by step: what data does the statement give you, "
        "and what does it ask you to find?",
        "Is there a definition or a property of the topic related to what is asked? Write it in "
        "your own words.",
        "Try a simpler case with small numbers: what happens there, and what does it suggest for "
        "the original case?",
        "Can you estimate the size or the sign the result should have before calculating it?",
        "Think of a similar exercise you have already solved: which of its steps helps you here?",
        "Write the first step you would take and ask yourself why it is valid: which rule "
        "justifies it?",
    ),
}

_CLOSING = {
    "es": (
        "Ya conversamos bastante sobre este ejercicio, miau. Intenta resolverlo con lo que "
        "descubriste; si lo necesitas, repasa la lección del tema o sigue con la siguiente "
        "pregunta."
    ),
    "en": (
        "We have talked a lot about this exercise, meow. Try to solve it with what you "
        "discovered; if you need to, review the topic's lesson or move on to the next question."
    ),
}

# The primary reason when a message has several: changing the rules first, then asking.
_PRIORITY = (OVERRIDES_INSTRUCTIONS, ASKS_FOR_ANSWER, PROPOSES_OPTION)


def redirect(reasons: tuple[str, ...], lang: str, turn: int) -> tuple[str, str]:
    """The reviewed redirect for a flagged message and the reason it answers."""
    reason = next(r for r in _PRIORITY if r in reasons)
    bank = _REDIRECTS[normalize_lang(lang)][reason]
    return bank[turn % len(bank)], reason


def hint(lang: str, turn: int) -> str:
    """A reviewed conceptual hint (FR-016, FR-017, FR-032)."""
    bank = _HINTS[normalize_lang(lang)]
    return bank[turn % len(bank)]


def closing(lang: str) -> str:
    """The message once a serving has used all its turns (FR-034)."""
    return _CLOSING[normalize_lang(lang)]
