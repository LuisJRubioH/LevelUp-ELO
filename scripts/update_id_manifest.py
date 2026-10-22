"""Adds the bank's new ids to the id manifest (spec 008 FR-011, D4).

`items/id_manifest.json` records each id's course (the bank file name without extension) and
topic. This script is the only way an id enters it (O-V4): it appends the ids the manifest lacks,
never changes or removes an entry, and writes the committed format (sorted, one line per id). It
refuses — exit 1, nothing written — when an id already listed has another course or topic in the
bank: a moved item gets a new id.

    python scripts/update_id_manifest.py                   # append the new ids
    python scripts/update_id_manifest.py --against BASE    # CI: fail if an entry of BASE changed
                                                           # or disappeared (O-V5); writes nothing

Run from the repository root (like `validate_bank.py`). Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.domain.bank import rules  # noqa: E402

BANK_DIR = Path("items/bank")
MANIFEST = Path(rules.MANIFEST_PATH)


def bank_entries(bank_dir: Path) -> list:
    """(id, course, topic) of every bank item whose id and topic are text, in the sync's files
    (`items/bank/*.json`, then `items/bank/semillero/*.json`)."""
    files = sorted(bank_dir.glob("*.json")) + sorted((bank_dir / "semillero").glob("*.json"))
    entries = []
    for path in files:
        for item in json.loads(path.read_text(encoding="utf-8")):
            if isinstance(item.get("id"), str) and isinstance(item.get("topic"), str):
                entries.append((item["id"], path.stem, item["topic"]))
    return entries


def read_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    problem = rules.manifest_format_problem(data)
    if problem:
        raise SystemExit(f"ERROR  {problem}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--against",
        metavar="BASE",
        help="manifiesto base (p. ej. el de la rama destino): falla si una entrada cambió o se "
        "quitó; no escribe",
    )
    args = parser.parse_args()

    if args.against:
        base = read_manifest(Path(args.against))
        head = read_manifest(MANIFEST) if MANIFEST.is_file() else {}
        changes = rules.manifest_changes(base, head)
        for change in changes:
            print(f"ERROR  {change}")
        if changes:
            print(
                f"\n{MANIFEST} solo crece (spec 008 FR-011): un ítem movido lleva un id nuevo; "
                f"los ids nuevos se agregan con {rules.MANIFEST_SCRIPT}, nunca a mano."
            )
            return 1
        print(f"{MANIFEST}: ninguna de las {len(base)} entradas de la base cambió")
        return 0

    manifest = read_manifest(MANIFEST) if MANIFEST.is_file() else {}
    entries = bank_entries(BANK_DIR)
    moved = rules.moved_ids(manifest, entries)
    if moved:
        for problem in rules.manifest_problems(manifest, entries):
            if any(f"'{item_id}' cambió" in problem for item_id in moved):
                print(f"ERROR  {problem}")
        print(f"\nNo se escribió {MANIFEST}: un id no cambia de curso ni de tema (spec 008 D4).")
        return 1

    grown = rules.appended_manifest(manifest, entries)
    added = len(grown) - len(manifest)
    text = rules.render_manifest(grown)
    if not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8") != text:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(text, encoding="utf-8")
    print(f"{MANIFEST}: {len(grown)} ids, {added} nuevos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
