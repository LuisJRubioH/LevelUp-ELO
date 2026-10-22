"""Spec 008 delivery V, FR-011 (D4): `scripts/update_id_manifest.py` writes the id manifest.

A new id enters `items/id_manifest.json` through the script, never by hand (O-V4); the script only
appends, and CI compares the manifest with the pull request's base so a changed or removed entry
fails (O-V5).
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "update_id_manifest.py"


def _item(item_id, topic):
    return {
        "id": item_id,
        "content": "¿Cuánto es $1+1$?",
        "difficulty": 900,
        "topic": topic,
        "options": ["$2$", "$3$"],
        "correct_option": "$2$",
    }


def _bank(tmp_path, files):
    for name, items in files.items():
        path = tmp_path / "items" / "bank" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


def _script(tmp_path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], cwd=tmp_path, capture_output=True, text=True
    )


def test_spec008_v_the_script_only_appends(tmp_path):
    """New ids are added sorted with their course (the file name) and topic; an existing entry is
    never changed or removed; a second run changes nothing; a moved id is refused and nothing is
    written."""
    _bank(
        tmp_path,
        {
            "geometria.json": [_item("g2", "Ángulos"), _item("g1", "Triángulos")],
            "semillero/algebra_semillero_9.json": [_item("s1", "Ecuaciones")],
        },
    )
    manifest = tmp_path / "items" / "id_manifest.json"
    manifest.write_text(json.dumps({"g1": ["geometria", "Triángulos"], "old": ["x", "y"]}))

    first = _script(tmp_path)

    assert first.returncode == 0, first.stdout + first.stderr
    written = manifest.read_text(encoding="utf-8")
    assert json.loads(written) == {
        "g1": ["geometria", "Triángulos"],
        "g2": ["geometria", "Ángulos"],
        "old": ["x", "y"],  # gone from the bank, kept: the manifest only grows
        "s1": ["algebra_semillero_9", "Ecuaciones"],
    }
    assert written.splitlines()[1:-1] == [
        '  "g1": ["geometria", "Triángulos"],',
        '  "g2": ["geometria", "Ángulos"],',
        '  "old": ["x", "y"],',
        '  "s1": ["algebra_semillero_9", "Ecuaciones"]',
    ]

    second = _script(tmp_path)
    assert second.returncode == 0, second.stdout + second.stderr
    assert manifest.read_text(encoding="utf-8") == written

    _bank(tmp_path, {"geometria.json": [_item("g2", "Polígonos"), _item("g1", "Triángulos")]})
    moved = _script(tmp_path)

    assert moved.returncode == 1
    assert "g2" in moved.stdout and "Ángulos" in moved.stdout and "Polígonos" in moved.stdout
    assert manifest.read_text(encoding="utf-8") == written


def test_spec008_v_a_changed_or_removed_entry_against_the_base_fails(tmp_path):
    """O-V5: `--against <base>` fails naming an entry the head changed or removed; a manifest that
    only grew passes."""
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"a1": ["dian", "Constitución"], "b2": ["sena", "Lógica"]}))
    head = tmp_path / "items" / "id_manifest.json"
    head.parent.mkdir(parents=True)

    head.write_text(json.dumps({"a1": ["dian", "Constitución"], "b2": ["sena", "Lógica"], "c": []}))
    grown = _script(tmp_path, "--against", str(base))
    assert grown.returncode == 0, grown.stdout + grown.stderr

    head.write_text(json.dumps({"a1": ["dian", "Economía"]}))
    changed = _script(tmp_path, "--against", str(base))

    assert changed.returncode == 1
    assert "a1" in changed.stdout and "Constitución" in changed.stdout
    assert "Economía" in changed.stdout and "b2" in changed.stdout


def _bank_job():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    return ci.split("\n  validate-bank:\n", 1)[1].split("\n  lint:\n", 1)[0]


def test_spec008_v_the_bank_job_checks_the_manifest_against_the_base():
    """O-V5: the «Banco de preguntas» job fetches the base commit and runs the append-only check
    against the base's manifest."""
    job = _bank_job()

    assert "fetch-depth: 2" in job
    assert "update_id_manifest.py --against" in job and "HEAD^1:items/id_manifest.json" in job
