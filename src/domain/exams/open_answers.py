"""
Spec 006 AB (FR-060 … FR-067): the two kinds of open question.

A **short answer** (a word or a number) is graded on submission against the teacher's accepted
answers, equivalent forms counted, with no AI (FR-062). A **procedure** is a photo of the
student's sheet; a vision model proposes four levels 0–3 — comprensión, estrategia, ejecución,
justificación — so it is worth 0–12, and the teacher decides (FR-064, FR-065). An answer is known
to the AI and the teacher by its code, never by a name. Pure: no I/O.
"""

import json
import re
import unicodedata
from fractions import Fraction

CRITERIA = ("comprension", "estrategia", "ejecucion", "justificacion")
CRITERIA_LABELS = {
    "comprension": "Comprensión del problema",
    "estrategia": "Estrategia",
    "ejecucion": "Ejecución",
    "justificacion": "Justificación",
}
MAX_LEVEL = 3
MAX_SCORE = MAX_LEVEL * len(CRITERIA)  # 12
MAX_OPEN_QUESTIONS = 6
MAX_TEXT = 4000
MAX_SHORT = 200
MAX_ACCEPTED = 10

SHORT = "short"
PROCEDURE = "procedure"
KINDS = (SHORT, PROCEDURE)

# The answer's state (FR-062 … FR-064).
AUTO = "auto"  # a short answer, graded on submission with no AI
PENDING = "pending"  # a procedure photo submitted; the AI has not been asked yet
PROPOSED = "proposed"  # the AI proposed four levels
BLANK = "blank"  # a procedure with no photo: 0 on every criterion, no call
NO_KEY = "no_key"  # no system key: the teacher grades it
FAILED = "failed"  # the provider failed or its reply could not be read

_LEVEL_TEXT = (
    "0 = no aparece; 1 = aparece con errores importantes; 2 = adecuado con fallas menores; "
    "3 = completo y correcto"
)


def answer_code(answer_id: int) -> str:
    """The code an answer goes by with the AI and the teacher: «R-» and its number."""
    return f"R-{int(answer_id):06d}"


def blank_levels() -> dict:
    return {criterion: 0 for criterion in CRITERIA}


def is_blank(text: str | None) -> bool:
    return not (text or "").strip()


def score(levels: dict) -> int:
    """A question's score, 0–12, from its four levels."""
    return sum(int(levels[c]) for c in CRITERIA)


def rubric_prompt(code: str, statement: str, reference: str) -> str:
    """What the vision model reads beside the photo of one procedure: the statement, the
    reference solution and the answer's code — never who wrote it (FR-064)."""
    criteria = "\n".join(f"- {c}: {CRITERIA_LABELS[c]}" for c in CRITERIA)
    keys = ", ".join(f'"{c}": <0-3>' for c in CRITERIA)
    return (
        "Eres evaluador de una olimpiada escolar de matemáticas. La imagen es el procedimiento "
        f"manuscrito de la respuesta {code}. Califícalo con esta rúbrica; cada criterio recibe un "
        f"nivel de 0 a 3 ({_LEVEL_TEXT}). Si la imagen no muestra un procedimiento de este "
        "problema, todos los niveles son 0.\n"
        f"Criterios:\n{criteria}\n\n"
        f"Enunciado:\n{statement}\n\n"
        f"Solución de referencia (puede haber otros caminos válidos):\n{reference or '(no hay)'}\n\n"
        "Responde solo con un objeto JSON, sin texto antes ni después: "
        f'{{{keys}, "comentario": "<una o dos frases sobre el procedimiento>"}}'
    )


def parse_rubric(reply: str | None) -> tuple[dict, str] | None:
    """The four levels and the comment in the AI's reply, or None if it cannot be read: a
    missing criterion, a level outside 0–3 or no JSON object."""
    if not reply:
        return None
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    levels = {}
    for criterion in CRITERIA:
        value = data.get(criterion)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if value != int(value) or not 0 <= value <= MAX_LEVEL:
            return None
        levels[criterion] = int(value)
    comment = data.get("comentario")
    return levels, (str(comment).strip()[:500] if comment else "")


def valid_levels(levels: dict) -> bool:
    """Whether a teacher's levels name the four criteria, each 0–3 (FR-064)."""
    if set(levels) != set(CRITERIA):
        return False
    return all(
        isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= MAX_LEVEL
        for v in levels.values()
    )


# ── Short answers (FR-062) ────────────────────────────────────────────────────

_NUMBER = re.compile(r"^[+-]?(\d+([.,]\d+)?|\d+/\d+|[.,]\d+)$")


def normalize_text(text: str) -> str:
    """Case, accents and spaces ignored; a trailing period dropped."""
    decomposed = unicodedata.normalize("NFD", str(text or ""))
    bare = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", "", bare.lower()).rstrip(".")


def as_number(text: str) -> Fraction | None:
    """The value of a number written with a decimal comma or point, or as a fraction; None for
    anything else."""
    compact = normalize_text(text)
    if not _NUMBER.match(compact):
        return None
    try:
        if "/" in compact:
            numerator, denominator = compact.split("/")
            if int(denominator) == 0:
                return None
            return Fraction(int(numerator), int(denominator))
        return Fraction(compact.replace(",", "."))
    except (ValueError, ZeroDivisionError):
        return None


def short_answer_is_right(answer: str, accepted: list[str]) -> bool:
    """Whether a short answer equals one of the accepted ones: the same text once case, accents
    and spaces are ignored, or numbers of equal value (2,5 = 2.5 = 5/2)."""
    given = normalize_text(answer)
    if not given:
        return False
    value = as_number(answer)
    for option in accepted:
        if normalize_text(option) == given:
            return True
        if value is not None and as_number(option) == value:
            return True
    return False
