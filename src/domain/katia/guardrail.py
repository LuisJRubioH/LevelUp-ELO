"""
Spec 005 K2 (FR-022): what a KatIA reply may say before it reaches a student.

KatIA guides; it never gives the answer. A reply passes when it has at most three sentences,
none of the phrases that announce a solution, and not the text of the correct option. A reply
that fails is replaced by `GUIDING_QUESTION`. The correct option is read on the server only for
this check: it never enters KatIA's prompt (FR-020).

Pure domain: no I/O.
"""

import re

MAX_SENTENCES = 3  # owner decision N1 (spec 005): as AGENTS.md documented
GUIDING_QUESTION = "¿Qué parte del enunciado te genera más dudas? ¿Qué intentaste hasta ahora?"

# The phrases the V1 validator refused (model_router.py), kept here for V2.
REVEALING_PHRASES = (
    "la respuesta correcta es",
    "la respuesta es",
    "la solución es",
    "el resultado es",
    "la opción correcta es",
    "debes elegir",
    "la respuesta correcta sería",
    "primero derivamos",
    "primero calculamos",
    "resolvemos paso a paso",
    "paso 1:",
    "paso 2:",
    "paso 3:",
)

_SHORT = 2  # an option this short is matched as a whole token, not inside other numbers


def _plain(text: str) -> str:
    """Lower case, without LaTeX delimiters, backslashes or repeated spaces."""
    text = text.lower().replace("$", "").replace("\\", "")
    return re.sub(r"\s+", " ", text).strip()


def names_option(reply: str, option: str) -> bool:
    """Whether the reply contains the option's text, ignoring case, spaces and `$`."""
    option, reply = _plain(option), _plain(reply)
    compact = option.replace(" ", "")
    if not compact:
        return False
    if len(compact) <= _SHORT:
        return re.search(rf"(?<![0-9a-z]){re.escape(option)}(?![0-9a-z])", reply) is not None
    return compact in reply.replace(" ", "")


def sentence_count(reply: str) -> int:
    return len([s for s in re.split(r"[.!?]+", reply) if s.strip()])


def check_reply(reply: str, correct_option: str) -> bool:
    """True when the reply may reach the student (FR-022)."""
    lowered = reply.lower()
    if any(phrase in lowered for phrase in REVEALING_PHRASES):
        return False
    if sentence_count(reply) > MAX_SENTENCES:
        return False
    return not names_option(reply, correct_option)
