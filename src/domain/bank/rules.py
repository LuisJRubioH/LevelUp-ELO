"""Spec 008 delivery V: the bank's validator rules, as pure functions (O-V2).

Read by `scripts/validate_bank.py` and `scripts/build_epa8_bank.py`; standard library only, no I/O
(the CI job that runs the validator installs nothing). The scripts read the files and print.

- FR-010 (D1): a difficulty is a JSON integer in 400–2000 (O-V1: not `900.0`, `"900"` or `true`).
- FR-011 (D4): an id never changes course or topic. `items/id_manifest.json` records each id's
  course (the bank file name without extension) and topic, `{"<id>": ["<course>", "<topic>"]}`,
  sorted, one line per id (O-V3); it only grows, through `scripts/update_id_manifest.py` (O-V4).
"""

from __future__ import annotations

import json
from typing import Iterable

DIFFICULTY_RANGE = (400, 2000)
MANIFEST_PATH = "items/id_manifest.json"
MANIFEST_SCRIPT = "python scripts/update_id_manifest.py"

# (id, course, topic) of each bank item whose id and topic are text
BankEntry = tuple[str, str, str]


def difficulty_problem(value: object) -> str | None:
    """None when `value` is a JSON integer in 400–2000 inclusive; otherwise what is wrong, naming
    the value and the range (FR-010)."""
    low, high = DIFFICULTY_RANGE
    if type(value) is int and low <= value <= high:
        return None
    kind = "no es un entero" if type(value) is not int else "está fuera de rango"
    return f"difficulty={value!r} {kind}: debe ser un entero en {low}–{high} (spec 008 FR-010)"


def moved_ids(manifest: dict, bank_entries: Iterable[BankEntry]) -> list[str]:
    """Ids the manifest lists whose course or topic in the bank differs (D4)."""
    return sorted(
        {
            item_id
            for item_id, course, topic in bank_entries
            if item_id in manifest and list(manifest[item_id]) != [course, topic]
        }
    )


def manifest_problems(manifest: dict, bank_entries: Iterable[BankEntry]) -> list[str]:
    """Errors of the bank against the manifest (FR-011): an id moved to another course or topic,
    naming both values; an id the manifest lacks, naming the script; a listed id gone from the
    bank (O-V6)."""
    entries = list(bank_entries)
    problems = []
    for item_id, course, topic in entries:
        if item_id not in manifest:
            problems.append(f"'{item_id}' no está en {MANIFEST_PATH}; corre {MANIFEST_SCRIPT}")
            continue
        old_course, old_topic = manifest[item_id]
        if old_course != course:
            problems.append(
                f"'{item_id}' cambió de curso: '{old_course}' → '{course}'; un ítem movido lleva "
                "un id nuevo (spec 008 D4)"
            )
        if old_topic != topic:
            problems.append(
                f"'{item_id}' cambió de tema: '{old_topic}' → '{topic}'; un ítem movido lleva un "
                "id nuevo (spec 008 D4)"
            )
    in_bank = {item_id for item_id, _, _ in entries}
    for item_id in sorted(set(manifest) - in_bank):
        problems.append(
            f"'{item_id}' está en {MANIFEST_PATH} y no en el banco; un ítem no se borra del banco "
            "(spec 008 O-V6)"
        )
    return problems


def appended_manifest(manifest: dict, bank_entries: Iterable[BankEntry]) -> dict:
    """The manifest with the bank ids it lacks added; an existing entry is never changed or
    removed (O-V4). Returns a new dict, sorted by id."""
    grown = {item_id: list(value) for item_id, value in manifest.items()}
    for item_id, course, topic in bank_entries:
        grown.setdefault(item_id, [course, topic])
    return dict(sorted(grown.items()))


def manifest_changes(base: dict, head: dict) -> list[str]:
    """Entries of the base manifest that the head changed or removed (O-V5: the manifest only
    grows)."""
    changes = []
    for item_id, value in sorted(base.items()):
        if item_id not in head:
            changes.append(f"'{item_id}' {list(value)} se quitó del manifiesto")
        elif list(head[item_id]) != list(value):
            changes.append(f"'{item_id}' cambió en el manifiesto: {list(value)} → {head[item_id]}")
    return changes


def render_manifest(manifest: dict) -> str:
    """The manifest's committed text: sorted by id, one line per entry (O-V3)."""
    lines = [
        f"  {json.dumps(item_id, ensure_ascii=False)}: {json.dumps(list(value), ensure_ascii=False)}"
        for item_id, value in sorted(manifest.items())
    ]
    return "{\n" + ",\n".join(lines) + "\n}\n"


def manifest_format_problem(data: object) -> str | None:
    """None when `data` (the parsed manifest) is an object of `[course, topic]` text pairs."""
    if not isinstance(data, dict):
        return f"{MANIFEST_PATH} debe ser un objeto JSON, es {type(data).__name__}"
    for item_id, value in data.items():
        if not (
            isinstance(value, list) and len(value) == 2 and all(isinstance(v, str) for v in value)
        ):
            return f"{MANIFEST_PATH}: '{item_id}' debe ser [curso, tema], es {value!r}"
    return None
