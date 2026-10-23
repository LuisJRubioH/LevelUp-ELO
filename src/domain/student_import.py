"""
src/domain/student_import.py
============================
Spec 009 delivery I1: the initial import's rules, without I/O — reading an identification (FR-004,
N16), the form's grade words (N20), the display name from one or two columns (N19) and the digest
of a preview (FR-003). Each problem is a reason code; the screens say it in words.
"""

import hashlib
import json
import re
import unicodedata

# A spreadsheet keeps 15 significant digits: a longer number in a numeric cell was already altered.
SPREADSHEET_DIGITS = 15

_DIGITS = re.compile(r"[0-9]+")
# Scientific notation typed back as text, as a spreadsheet shows a long number: «1,2E+09».
_SCIENTIFIC = re.compile(r"[0-9]+([.,][0-9]+)?[eE][+-]?[0-9]+")

# The Google Form's grade answers (spec 009, session 2026-10-18), compared without case or accents.
_GRADE_WORDS = {
    "sexto": 6,
    "septimo": 7,
    "octavo": 8,
    "noveno": 9,
    "decimo": 10,
    "undecimo": 11,
}


def read_identification(value) -> tuple[str | None, str | None]:
    """FR-004: (the identification, None) or (None, reason). Text keeps its digits as written once
    the outer spaces are removed; anything else is refused, never corrected. A numeric cell holding
    a whole number of up to 15 digits reads as its digits (N16); a decimal, a longer number or
    scientific notation was altered by the spreadsheet and is never rebuilt."""
    if value is None:
        return None, "identification_missing"
    if isinstance(value, bool):
        return None, "identification_not_digits"
    if isinstance(value, (int, float)):
        if value < 0:
            return None, "identification_not_digits"
        if isinstance(value, float) and not value.is_integer():
            return None, "identification_altered"
        digits = str(int(value))
        if len(digits) > SPREADSHEET_DIGITS:
            return None, "identification_altered"
        return digits, None
    text = str(value).strip()
    if not text:
        return None, "identification_missing"
    if _DIGITS.fullmatch(text):
        return text, None
    if _SCIENTIFIC.fullmatch(text):
        return None, "identification_altered"
    return None, "identification_not_digits"


def _folded(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.strip())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


def read_grade(value) -> tuple[int | None, str | None]:
    """N20, P9: the form's six words «Sexto» … «Undécimo» read as 6 … 11, without case, accents or
    outer spaces; anything else is an error for the row, never guessed."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None, "grade_missing"
    if not isinstance(value, str):
        return None, "grade_unknown"
    grade = _GRADE_WORDS.get(_folded(value))
    return (grade, None) if grade else (None, "grade_unknown")


def join_display_name(parts) -> str | None:
    """N19: the display name from one or two columns, in the order the admin chose, joined with one
    space; each part loses its outer spaces and inner runs of spaces. None when nothing is left —
    the row is then an error (US1-AS10). Spec 004's filter judges the joined name."""
    words = []
    for part in parts:
        if part is None:
            continue
        words.extend(str(part).split())
    return " ".join(words) or None


def preview_digest(file_bytes: bytes, mapping: dict, batch: dict, statuses: list) -> str:
    """FR-003: what the admin saw — the file, the mapping, the batch choices and every row's status.
    The confirmation recomputes it; any difference asks for a new preview."""
    seen = json.dumps(
        {
            "file": hashlib.sha256(file_bytes).hexdigest(),
            "mapping": mapping,
            "batch": batch,
            "statuses": [json.dumps(status, sort_keys=True, default=str) for status in statuses],
        },
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(seen.encode("utf-8")).hexdigest()
