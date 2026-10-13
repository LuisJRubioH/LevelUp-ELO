"""
Server-side checks of KatIA's conversation (spec 005, research R3, R4, R8).

Two questions, both answered before anything reaches the student:

- ``inspect_message``: does the student's message ask for the answer, propose an option or try to
  change the tutor's rules? Then it never reaches the model (FR-003 … FR-005).
- ``inspect_reply``: does the model's reply give the answer away — its text, an equal value, an
  option by position, another option, an elimination, a verdict or a worked solution, alone or
  added to the serving's earlier replies? Then it is replaced (FR-009 … FR-015).

These are deterministic heuristics, strict on purpose (spec K4). They do not prove that no
solution can leak — see spec 005 § Known limits. Pure Python: no I/O, no third-party library.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

# ── Reason codes ─────────────────────────────────────────────────────────────

ASKS_FOR_ANSWER = "asks_for_answer"
PROPOSES_OPTION = "proposes_option"
OVERRIDES_INSTRUCTIONS = "overrides_instructions"

ANSWER_TEXT = "answer_text"
ANSWER_VALUE = "answer_value"
OPTION_POSITION = "option_position"
OPTION_TEXT = "option_text"
ELIMINATION = "elimination"
VERDICT = "verdict"
SOLUTION = "solution"
ACCUMULATED_SOLUTION = "accumulated_solution"

# Equations ("=") outside the statement: a single reply with this many is a worked solution
# (FR-014); the serving's accepted replies plus the new one reaching the second is one too (FR-015).
SOLUTION_EQUATIONS = 3
ACCUMULATED_EQUATIONS = 4

# An option this short (after normalisation) is matched only at a token boundary, and a short
# word only next to a cue such as "es" or "is": "no", "x" or "si" occur everywhere.
SHORT_OPTION = 2


@dataclass(frozen=True)
class ItemFacts:
    """What the checks know about the item: always the store's data, never the client's."""

    statement: str
    options: tuple[str, ...]
    correct_option: str


# ── Normalisation ────────────────────────────────────────────────────────────

_SPACING = re.compile(r"\\(?:left|right|displaystyle|textstyle|quad|qquad|[,;:! ])")
_WRAPPERS = re.compile(r"\\(?:text|mathrm|mathbf|operatorname)\s*")
_FRAC_VARIANTS = re.compile(r"\\[dt]frac")


def _fold(text: str) -> str:
    """Lower case, accents removed, unicode math signs mapped to their ASCII/LaTeX forms."""
    text = (text or "").replace("−", "-").replace("√", "\\sqrt").replace("…", "...")
    text = text.replace("×", "*").replace("·", "*")
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.lower()


def _light(text: str) -> str:
    """Folded text without `$` and LaTeX spacing commands; words and spaces kept."""
    text = _FRAC_VARIANTS.sub(r"\\frac", _fold(text))
    text = _SPACING.sub(" ", _WRAPPERS.sub("", text))
    text = text.replace("$", " ").replace("\\cdot", "*").replace("\\times", "*")
    return re.sub(r"\s+", " ", text).strip()


def _compact(text: str) -> str:
    """Light text without spaces, braces, backslashes and multiplication signs."""
    return re.sub(r"[\s{}\\*]", "", _light(text)).rstrip(".")


# ── Numbers ──────────────────────────────────────────────────────────────────

# A number not glued to a variable, an exponent or a subscript (x^7 and a_2 are not values).
_FRAC = re.compile(r"(?<![\w^_])(-?)\\frac\s*\{\s*(-?\d+)\s*\}\s*\{\s*(\d+)\s*\}")
_SLASH = re.compile(r"(?<![\w^_.,])(-?\d+)\s*/\s*(\d+)(?![\d.,]\d)")
_DECIMAL = re.compile(r"(?<![\w^_.,])(-?\d+)[.,](\d+)(?![\d.,]*\d)")


def _values(light: str) -> list[Fraction]:
    """Every number in light text: fractions first, then decimals, then integers."""
    found = []
    rest = light

    def take(pattern, build):
        nonlocal rest
        for match in pattern.finditer(rest):
            value = build(match)
            if value is not None:
                found.append(value)
        rest = pattern.sub(" ", rest)

    def frac(m):
        denominator = int(m.group(3))
        if denominator == 0:
            return None
        value = Fraction(int(m.group(2)), denominator)
        return -value if m.group(1) else value

    def slash(m):
        denominator = int(m.group(2))
        return Fraction(int(m.group(1)), denominator) if denominator else None

    def decimal(m):
        sign = -1 if m.group(1).startswith("-") else 1
        whole = abs(int(m.group(1)))
        return sign * (whole + Fraction(int(m.group(2)), 10 ** len(m.group(2))))

    take(_FRAC, frac)
    take(_SLASH, slash)
    take(_DECIMAL, decimal)
    for match in re.finditer(r"(?<![\w^_.,])(-?\d+)(?![\w.,]?\d)", rest):
        found.append(Fraction(int(match.group(1))))
    return found


def _option_value(option: str) -> Fraction | None:
    """The value of an option that is only a number, a decimal or a fraction."""
    light = _light(option)
    values = _values(light)
    if len(values) != 1:
        return None
    if re.fullmatch(
        r"-?\s*(\\frac\s*\{\s*-?\d+\s*\}\s*\{\s*\d+\s*\}|\d+\s*/\s*\d+|\d+([.,]\d+)?)", light
    ):
        return values[0]
    return None


# ── Options ──────────────────────────────────────────────────────────────────

_CUE_WORDS = (
    r"es|sera|seria|serian|son|da|dan|queda|resulta|vale|sale|igual a|fuera|"
    r"is|is it|equals|would be|it's|its|get|gives"
)


@dataclass(frozen=True)
class _Option:
    light: str
    compact: str
    value: Fraction | None
    in_statement: bool
    # Notation (digits, symbols, LaTeX) compares without spaces; prose compares word by word —
    # without spaces "en un caso" would contain the option "Nunca".
    math: bool

    @property
    def short(self) -> bool:
        return len(self.compact) <= SHORT_OPTION

    @property
    def is_word(self) -> bool:
        return self.value is None and self.compact.isalpha()


@lru_cache(maxsize=256)
def _options(facts: ItemFacts) -> tuple[tuple[_Option, ...], _Option]:
    statement_light = _light(facts.statement)
    statement_compact = _compact(facts.statement)
    built = []
    correct = None
    for text in facts.options:
        built.append(_option(text, statement_light, statement_compact))
        if text == facts.correct_option:
            correct = built[-1]
    if correct is None:
        correct = _option(facts.correct_option, statement_light, statement_compact)
    return tuple(built), correct


_NOTATION = re.compile(r"[\d=+\-*/^_\\()<>|$]")


def _option(text: str, statement_light: str, statement_compact: str) -> _Option:
    light, compact = _light(text), _compact(text)
    math = bool(_NOTATION.search(text))
    if math and len(compact) > SHORT_OPTION:
        in_statement = compact in statement_compact
    else:
        in_statement = _token_in(light, statement_light)
    return _Option(light, compact, _option_value(text), in_statement, math)


def _token_pattern(light: str) -> str:
    return r"(?<![\w^_.\\])" + re.escape(light) + r"(?![\w])(?![.,]\d)"


def _token_in(light: str, text: str) -> bool:
    return bool(light) and re.search(_token_pattern(light), text) is not None


def _with_cue(light: str, text: str) -> bool:
    cue = r"(?:^|[\s¿(])(?:" + _CUE_WORDS + r")\s*(?:la\s+|el\s+|que\s+)?(?:opcion\s+)?"
    return re.search(cue + _token_pattern(light), text) is not None


def _whole_message_is(light: str, text: str) -> bool:
    bare = re.sub(r"[\s¿?¡!.,:;()\"'«»]", "", text)
    return bool(light) and bare == re.sub(r"\s", "", light)


def _mentions(option: _Option, light: str, compact: str, *, cue_for_words: bool) -> bool:
    """Whether the text names this option (statement occurrences never count)."""
    if option.in_statement or not option.compact:
        return False
    if option.math and not option.short:
        return option.compact in compact
    if option.is_word and option.short and cue_for_words:
        return _with_cue(option.light, light) or _whole_message_is(option.light, light)
    return _token_in(option.light, light)


def _mentions_value(option: _Option, light: str, statement_values: list[Fraction]) -> bool:
    if option.value is None or option.value in statement_values:
        return False
    return option.value in _values(light)


# ── Positions, verdicts, markers ─────────────────────────────────────────────

_ORDINALS = (
    r"primera|segunda|tercera|cuarta|quinta|ultima|penultima|first|second|third|fourth|fifth|last"
)
_POSITION = re.compile(
    r"\b(?:opcion|alternativa|literal|inciso|option|choice|alternative)\s*\(?(?:[a-f]|[1-6])\)?(?![\w])"
    r"|\b(?:"
    + _ORDINALS
    + r")\s+(?:opcion|alternativa|respuesta|eleccion|option|choice|answer|alternative)\b"
    r"|\b(?:opcion|alternativa|option|choice)\s+(?:" + _ORDINALS + r")\b"
)
# A bare letter as the student's proposal: "¿es la b?", "la c?", "¿A?".
_LETTER_PROPOSAL = re.compile(
    r"(?:^|[\s¿])(?:es|sera|seria|creo que es)\s+(?:la|el)\s+[a-f](?![\w])"
    r"|(?:^|[\s¿])(?:la|el)\s+[a-f]\s*\?"
    r"|^\W*[a-f]\W*$"
)

# A verdict on a proposal (FR-013). Common words that only confirm as a sentence of their own
# ("¡Exacto!", "Correcto.", "Perfect,") are matched only there: "el valor exacto", "the correct
# rule" or "what exactly does it ask?" are not verdicts.
_VERDICTS = re.compile(
    r"\b(?:es (?:la )?correct[oa]|es (?:la )?incorrect[oa]|son correct[oa]s|son incorrect[oa]s|"
    r"esta (?:bien|mal)|estas en lo cierto|acertaste|has acertado|acertad[oa]|tienes razon|"
    r"vas (?:muy )?bien|buen camino|bien hecho|muy bien|te equivocaste|equivocad[oa]|"
    r"no es esa|esa no es|"
    r"is (?:the )?(?:correct|incorrect|right|wrong)|you'?re right|you are right|that'?s right|"
    r"that'?s (?:correct|wrong|incorrect)|right answer|wrong answer|right track|not quite|"
    r"spot on|nailed it|good job|great job|well done)\b"
    r"|(?:^|[.!?¡¿]\s*)(?:correct[oa]|incorrect[oa]|exact[oa]|perfect[oa]|asi es|eso es|esa no|"
    r"correct|incorrect|exactly|perfect|right|wrong|that'?s it|yes|si|no)\s*[!.,;:]"
)
_SOLUTION_MARKERS = re.compile(
    r"\b(?:paso\s*\d|step\s*\d|la respuesta (?:correcta )?es|la solucion es|el resultado es|"
    r"la opcion correcta es|the (?:correct )?answer is|the solution is|the result is|"
    r"the correct option is)\b"
)
_NEGATIONS = (
    r"(?:no es|no son|no puede ser|no seria|no da|descarta(?:r|mos)?|elimina(?:r|mos)?|"
    r"isn'?t|is not|cannot be|can'?t be|not|rule out|eliminate|discard)"
)

# ── Student messages ─────────────────────────────────────────────────────────

_ASKS = re.compile(
    r"\b(?:cual|que)\s+es\s+(?:la\s+)?(?:respuesta|solucion|opcion correcta|correcta|resultado|buena)"
    r"|\b(?:dame|dime|decime|muestrame|pasame|regalame|dar|decir)\s+(?:cual\s+es\s+)?(?:la\s+|el\s+)?"
    r"(?:respuesta|solucion|resultado|opcion correcta|clave)"
    r"|\b(?:cual|que)\s+(?:opcion|alternativa|marco|elijo|escojo|pongo)\b"
    r"|\bopcion correcta\b|\brespuesta correcta\b"
    r"|\bresuelve(?:lo|la|me|melo)?\b|\bresolver(?:lo)?\s+(?:todo|completo|por mi)"
    r"|\bsolucion completa\b|\bpaso a paso\b|\bhazlo (?:tu|por mi)\b"
    r"|\bwhat(?:'s| is)\s+the\s+(?:answer|solution|result|correct)"
    r"|\b(?:give|tell|show)\s+me\s+(?:the\s+)?(?:answer|solution|result|correct)"
    r"|\bsolve\s+(?:it|this|the)\b|\bwhich\s+(?:option|one|choice|answer)\b"
    r"|\bcorrect\s+(?:answer|option|choice)\b|\bstep[\s-]by[\s-]step\b|\bfull\s+solution\b"
    r"|\bdo\s+it\s+for\s+me\b"
)
_OVERRIDES = re.compile(
    r"\bignora(?:r)?\b|\bolvida\s+(?:tus|las|todas)\b|\b(?:tus|las)\s+(?:instrucciones|reglas)\b"
    r"|\bprompt\b|\bmodo\s+(?:desarrollador|dios|admin|administrador|profesor|docente)\b"
    r"|\bsistema\s*:|\bahora\s+eres\b|\bactua\s+como\b|\bfinge\b|\bjailbreak\b"
    r"|\bsin\s+restricciones\b|\bsoy\s+(?:el|la|tu)\s+(?:profesor|profesora|docente|administrador)"
    r"|\bignore\s+(?:all|any|the|your|previous|prior|above)\b|\b(?:system|developer)\s+(?:prompt|message|mode)\b"
    r"|\bsystem\s*:|\byou\s+are\s+now\b|\bact\s+as\b|\bpretend\b|\bno\s+restrictions\b"
    r"|\bi\s+am\s+(?:the|your)\s+(?:teacher|admin|developer)\b|\bforget\s+(?:your|the|all)\b"
)


def inspect_message(message: str, facts: ItemFacts) -> tuple[str, ...]:
    """Reasons to answer the student's message without the model (FR-003 … FR-005)."""
    light = _light(message)
    compact = _compact(message)
    reasons = set()
    if _OVERRIDES.search(light):
        reasons.add(OVERRIDES_INSTRUCTIONS)
    if _ASKS.search(light):
        reasons.add(ASKS_FOR_ANSWER)
    options, _ = _options(facts)
    statement_values = _values(_light(facts.statement))
    proposes = bool(_POSITION.search(light) or _LETTER_PROPOSAL.search(light))
    for option in options:
        if proposes:
            break
        if option.in_statement or option.short:
            # Text the statement also contains counts only as a proposal: "¿es 4?", "da 4", "4".
            proposes = _with_cue(option.light, light) or _whole_message_is(option.light, light)
        else:
            proposes = _mentions(option, light, compact, cue_for_words=True)
        if not proposes and option.value is not None and option.value not in statement_values:
            proposes = _proposed_value(option.value, light)
    if proposes:
        reasons.add(PROPOSES_OPTION)
    return tuple(sorted(reasons))


def _proposed_value(value: Fraction, light: str) -> bool:
    """A number equal to an option's value, right after a cue ("vale 14/2", "da 7,0")."""
    cue = re.compile(r"(?:^|[\s¿(])(?:" + _CUE_WORDS + r")\s*(?:la\s+|el\s+)?(.{1,24})")
    for match in cue.finditer(light):
        values = _values(match.group(1))
        if values and values[0] == value:
            return True
    return False


# ── Model replies ────────────────────────────────────────────────────────────


def _equations(text: str, statement: str) -> int:
    """`=` signs outside the statement's own text and outside math quoted from it."""
    statement_compact = _compact(statement)
    folded = _without_statement(_fold(text), _fold(statement))
    count = 0
    for segment in re.split(r"[.;?!\n]|\s(?:y|luego|asi|entonces|and|then|so)\s", folded):
        for piece in re.split(r"\$", segment):
            if "=" not in piece:
                continue
            if _compact(piece) and _compact(piece) in statement_compact:
                continue
            count += (
                piece.count("=") - piece.count("==") * 2 - piece.count("<=") - piece.count(">=")
            )
    return count


def _without_statement(light: str, statement_light: str) -> str:
    """The reply's light text with the statement, and each of its sentences, taken out."""
    text = light.replace(statement_light, " ") if statement_light else light
    for sentence in re.split(r"(?<=[.?!])\s+", statement_light):
        sentence = sentence.strip(" ¿?¡!.,")
        if len(sentence) >= 12:
            text = text.replace(sentence, " ")
    return text


def inspect_reply(
    reply: str, facts: ItemFacts, accepted_replies: list[str] | tuple[str, ...] = ()
) -> tuple[str, ...]:
    """Reasons to reject the model's reply (FR-010 … FR-015); empty when it may be shown."""
    light = _light(reply)
    compact = _compact(reply)
    options, correct = _options(facts)
    statement_values = _values(_light(facts.statement))
    reasons = set()

    if _mentions(correct, light, compact, cue_for_words=True):
        reasons.add(ANSWER_TEXT)
    if _mentions_value(correct, light, statement_values):
        reasons.add(ANSWER_VALUE)
    # Quoting the statement neither names a position nor passes a verdict.
    own_words = _without_statement(light, _light(facts.statement))
    if _POSITION.search(own_words):
        reasons.add(OPTION_POSITION)
    for option in options:
        if option is correct or option.compact == correct.compact:
            continue
        if not option.short and _mentions(option, light, compact, cue_for_words=True):
            reasons.add(OPTION_TEXT)
    for option in options:
        if option.in_statement or not option.light:
            continue
        if re.search(
            _NEGATIONS + r"\s+(?:la\s+|el\s+)?(?:opcion\s+)?" + _token_pattern(option.light), light
        ):
            reasons.add(ELIMINATION)
        elif not option.short and re.search(
            _NEGATIONS + r"\s+(?:la\s+|el\s+)?" + re.escape(option.light), light
        ):
            reasons.add(ELIMINATION)
    if _VERDICTS.search(own_words):
        reasons.add(VERDICT)
    equations = _equations(reply, facts.statement)
    if _SOLUTION_MARKERS.search(own_words) or equations >= SOLUTION_EQUATIONS:
        reasons.add(SOLUTION)
    earlier = sum(_equations(text, facts.statement) for text in accepted_replies)
    if accepted_replies and earlier + equations >= ACCUMULATED_EQUATIONS:
        reasons.add(ACCUMULATED_SOLUTION)
    return tuple(sorted(reasons))


# ── Cut-off replies ──────────────────────────────────────────────────────────


def trim_to_sentences(text: str) -> str:
    """The reply up to its last sentence end outside `$…$` (FR-032); "" if none."""
    in_math = False
    end = -1
    for index, char in enumerate(text or ""):
        if char == "$":
            in_math = not in_math
        elif not in_math and char in ".?!…":
            end = index
    return text[: end + 1].strip() if end >= 0 else ""
