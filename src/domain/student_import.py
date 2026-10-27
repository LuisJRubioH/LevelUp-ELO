"""
src/domain/student_import.py
============================
Spec 009 delivery I1: the initial import's rules, without I/O — reading an identification (FR-004,
N16), the form's grade words (N20), the display name from one or two columns (N19), the recovery
e-mail (FR-018), the classification of every row of a preview (FR-002, FR-007, N21) and its digest
(FR-003). Each problem is a reason code; the screens say it in words, and the audit keeps the code
alone, never the value (FR-009).
"""

import hashlib
import json
import re
import unicodedata

from src.domain.entities import VALID_LEVELS
from src.domain.identity import (
    access_expired,
    display_name_problem,
    normalize_display_name,
    parse_last_day,
    student_level_problem,
)

# A spreadsheet keeps 15 significant digits: a longer number in a numeric cell was already altered.
SPREADSHEET_DIGITS = 15

_DIGITS = re.compile(r"[0-9]+")
# Scientific notation typed back as text, as a spreadsheet shows a long number: «1,2E+09».
_SCIENTIFIC = re.compile(r"[0-9]+([.,][0-9]+)?[eE][+-]?[0-9]+")

_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
EMAIL_MAX_LENGTH = 254

# Plan § Running the import: an import without progress for this long was left by a worker that
# died (a restart); it reads as interrupted, takes no more rows, and the admin can start again.
IMPORT_IDLE_SECONDS = 600

# Each row's result in the import's audit (FR-009), in the order the counts are shown.
ROW_RESULTS = ("created", "updated", "unchanged", "skipped", "duplicate", "error")

# A group is for one grade of the form (N26 (a)): 6.º … 11.º.
GROUP_GRADES = range(6, 12)

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


def confirmation_key(digest: str, confirmed: dict) -> str:
    """FR-010: what identifies one confirmation — the preview's digest and the changes to existing
    accounts confirmed with it (`{row: fields}`). The same key again is a retry and returns the
    first import; the same preview confirmed with other changes is a new confirmation (FR-008)."""
    chosen = sorted((int(row), sorted(fields)) for row, fields in confirmed.items() if fields)
    return hashlib.sha256(json.dumps([digest, chosen]).encode("utf-8")).hexdigest()


def read_recovery_email(value) -> tuple[str | None, str | None]:
    """FR-018 (N24): (the address, None), (None, None) for an empty cell, or (None, reason) for a
    value that is not an e-mail address. Never unique: siblings may share one."""
    text = "" if value is None else str(value).strip()
    if not text:
        return None, None
    if len(text) > EMAIL_MAX_LENGTH or not _EMAIL.fullmatch(text):
        return None, "email_invalid"
    return text, None


def _read_level(value) -> tuple[str | None, str | None]:
    level = _folded(str(value)) if value is not None else ""
    return (level, None) if level in VALID_LEVELS else (None, "level_unknown")


def _cell(values: dict, column):
    return values.get(column) if column else None


def classify_rows(rows, mapping: dict, batch: dict, pairing: dict, linked: dict, usernames) -> list:
    """FR-002: each `(number, values)` row as `new`, `existing`, `duplicate` or `error`, with its
    reasons and what it would get. Nothing is saved.

    `mapping` names the file's columns: `identification`, `name` (one or two, in order, N19) and,
    optionally, `level`, `grade`, `institution` and `recovery_email`. `batch` holds the level and
    grade for what is not mapped (N20) and the last day of access. `pairing` maps each
    (institution, grade) to its group (N21). `linked` maps each linked identification to its account
    (`user_id`, `group_id`, `access_until`, `recovery_email`); `usernames` holds the usernames in use
    (FR-007).

    An `existing` row lists the group, last day and recovery e-mail that differ from its account
    under `changes`; the preview never applies them (FR-006, FR-008, N27). Only the first occurrence of an identification
    counts; later ones are `duplicate`."""
    seen, results = set(), []
    for number, values in rows:
        identification, problem = read_identification(_cell(values, mapping["identification"]))
        result = {
            "row": number,
            "status": "error",
            "reasons": [problem] if problem else [],
            "identification": identification,
            "display_name": None,
            "level": None,
            "grade": None,
            "group_id": None,
            "recovery_email": None,
            "account_id": None,
            "changes": {},
        }
        results.append(result)
        if identification is not None and identification in seen:
            result.update(status="duplicate", reasons=[])
            continue
        if identification is not None:
            seen.add(identification)
        reasons = result["reasons"]

        name = normalize_display_name(
            join_display_name(_cell(values, column) for column in mapping["name"]) or ""
        )
        result["display_name"] = name
        if name is None:
            reasons.append("name_missing")
        elif display_name_problem(name):
            reasons.append("name_refused")

        level, grade = batch.get("level"), batch.get("grade")
        if mapping.get("level"):
            level, level_problem = _read_level(_cell(values, mapping["level"]))
            if level_problem:
                reasons.append(level_problem)
        if mapping.get("grade"):
            grade, grade_problem = read_grade(_cell(values, mapping["grade"]))
            if grade_problem:
                reasons.append(grade_problem)
        if level is not None and not any(r.startswith("grade_") for r in reasons):
            if student_level_problem(level, grade):
                reasons.append("level_grade")
        result["level"], result["grade"] = level, grade

        institution = _cell(values, mapping.get("institution"))
        institution = str(institution).strip() if institution is not None else None
        result["group_id"] = pairing.get((institution, grade))
        if result["group_id"] is None:
            reasons.append("group_missing")

        if mapping.get("recovery_email"):
            email, email_problem = read_recovery_email(_cell(values, mapping["recovery_email"]))
            result["recovery_email"] = email
            if email_problem:
                reasons.append(email_problem)

        account = linked.get(identification) if identification is not None else None
        if account is not None:
            result.update(status="existing", reasons=[], account_id=account["user_id"])
            if result["group_id"] is not None and result["group_id"] != account.get("group_id"):
                result["changes"]["group_id"] = {
                    "from": account.get("group_id"),
                    "to": result["group_id"],
                }
            wanted, current = batch.get("access_until"), account.get("access_until")
            if (str(wanted) if wanted else None) != (str(current) if current else None):
                result["changes"]["access_until"] = {"from": current, "to": wanted}
            email = result["recovery_email"]
            if email is not None and email != account.get("recovery_email"):
                result["changes"]["recovery_email"] = {
                    "from": account.get("recovery_email"),
                    "to": email,
                }
            continue
        if identification is not None and identification in usernames:
            reasons.append("identification_is_username")
        if not reasons:
            result["status"] = "new"
    return results


def _row_pair(values: dict, mapping: dict, batch: dict):
    institution = _cell(values, mapping.get("institution"))
    institution = str(institution).strip() if institution is not None else None
    grade = batch.get("grade")
    if mapping.get("grade"):
        grade, problem = read_grade(_cell(values, mapping["grade"]))
        if problem:
            return None
    return institution, grade


def file_pairs(rows, mapping: dict, batch: dict) -> list:
    """N21: the distinct (institution, grade) pairs of the file, in the order they first appear —
    what the admin pairs with a group. A row whose grade does not read gives none (it is an error
    anyway)."""
    pairs = []
    for _number, values in rows:
        pair = _row_pair(values, mapping, batch)
        if pair is not None and pair not in pairs:
            pairs.append(pair)
    return pairs


OTHER_INSTITUTION = "otro"  # the form's «Otro»: free text, never paired by itself (N21)


def suggest_pairing(pairs, groups) -> dict:
    """N26 (a): each pair whose institution and grade match exactly one group's — compared without
    case, accents or outer spaces — gets that group as a suggestion; «Otro», a pair without an
    institution and a pair two groups match get none. The admin can change every pairing."""
    suggested = {}
    for institution, grade in pairs:
        if institution is None or _folded(institution) == OTHER_INSTITUTION:
            continue
        matches = [
            group["group_id"]
            for group in groups
            if group.get("institution") is not None
            and _folded(group["institution"]) == _folded(institution)
            and group.get("grade") == grade
        ]
        if len(matches) == 1:
            suggested[(institution, grade)] = matches[0]
    return suggested


def import_creation(row: dict, now_utc) -> tuple[dict | None, str | None]:
    """FR-003, FR-005: what an import row creates through spec 004's validations (FR-040, FR-043,
    FR-044) — the identification as username, a display name the filter accepts, a level and grade
    that go together, a last day not yet past and a valid recovery e-mail — or (None, reason). The
    repositories call it again inside each row's transaction."""
    identification, problem = read_identification(row.get("identification"))
    if problem:
        return None, problem
    name = normalize_display_name(row.get("display_name") or "")
    if name is None:
        return None, "name_missing"
    if display_name_problem(name):
        return None, "name_refused"
    level, grade = row.get("level"), row.get("grade")
    if student_level_problem(level, grade):
        return None, "level_grade"
    try:
        last_day = parse_last_day(row.get("access_until"))
    except ValueError:
        return None, "access_invalid"
    if access_expired(last_day, now_utc):
        return None, "access_expired"
    email, problem = read_recovery_email(row.get("recovery_email"))
    if problem:
        return None, problem
    return {
        "identification": identification,
        "display_name": name,
        "level": level,
        "grade": str(grade) if level == "semillero" else None,
        "access_until": last_day,
        "recovery_email": email,
    }, None


def group_for_teacher_problem(name, institution, grade) -> str | None:
    """N25, N26 (a): why the admin cannot create a group with this name, institution and grade, or
    None. The name is required; the institution and grade are optional, the grade 6 … 11."""
    if not isinstance(name, str) or not name.strip():
        return "Escribe el nombre del grupo."
    if institution is not None and not isinstance(institution, str):
        return "La institución debe ser un texto."
    if grade is not None and (isinstance(grade, bool) or grade not in GROUP_GRADES):
        return "El grado del grupo va de 6.º a 11.º."
    return None


# T024: the Google Form's headers, compared without case, accents or extra spaces. The grade's
# header carries the year («Grado que cursas en 2027»), so it matches by its start.
_SUGGESTED_HEADERS = (
    ("identification", "numero de documento", False),
    ("name", "nombres", False),
    ("name", "apellidos", False),
    ("grade", "grado que cursas", True),
    ("institution", "institucion educativa", False),
    ("recovery_email", "correo electronico de contacto", False),
)


def suggest_mapping(header) -> dict:
    """T024: the mapping the form's headers suggest — the display name from «Nombres» then
    «Apellidos». A header the form does not have suggests nothing; the admin changes every
    suggestion."""
    folded = [(column, " ".join(_folded(str(column)).split())) for column in header]
    mapping = {}
    for field, wanted, by_start in _SUGGESTED_HEADERS:
        match = next(
            (
                column
                for column, text in folded
                if (text.startswith(wanted) if by_start else text == wanted)
            ),
            None,
        )
        if match is None:
            continue
        if field == "name":
            mapping.setdefault("name", []).append(match)
        else:
            mapping[field] = match
    return mapping
