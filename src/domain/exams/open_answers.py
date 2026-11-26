"""
Spec 006 AB (FR-060 … FR-065): the open question's rubric, the AI's prompt and its reading.

Four criteria, each on a level 0–3, so a question is worth 0–12 (Clarifications, 2026-11-26). An
answer is known to the AI and to the teacher by its code, never by a name. The AI only proposes;
the teacher decides (FR-064). Pure: no I/O.
"""

import json
import re

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

# The answer's state as to the AI (FR-063).
PENDING = "pending"  # submitted; the AI has not been asked yet
PROPOSED = "proposed"  # the AI proposed four levels
BLANK = "blank"  # nothing typed: 0 on every criterion, no call
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


def rubric_prompt(code: str, statement: str, reference: str, answer: str) -> str:
    """What the AI receives for one answer: the statement, the reference solution, the answer
    and its code — never who wrote it (FR-063)."""
    criteria = "\n".join(f"- {c}: {CRITERIA_LABELS[c]}" for c in CRITERIA)
    keys = ", ".join(f'"{c}": <0-3>' for c in CRITERIA)
    return (
        "Eres evaluador de una olimpiada escolar de matemáticas. Califica la respuesta "
        f"{code} con esta rúbrica. Cada criterio recibe un nivel de 0 a 3 ({_LEVEL_TEXT}).\n"
        f"Criterios:\n{criteria}\n\n"
        f"Enunciado:\n{statement}\n\n"
        f"Solución de referencia (puede haber otros caminos válidos):\n{reference or '(no hay)'}\n\n"
        f"Respuesta {code}:\n{answer}\n\n"
        "Responde solo con un objeto JSON, sin texto antes ni después: "
        f'{{{keys}, "comentario": "<una o dos frases sobre la respuesta>"}}'
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
