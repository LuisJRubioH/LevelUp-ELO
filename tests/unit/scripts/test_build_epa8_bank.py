"""Spec 008 delivery V, FR-012 (D6): the EPA8 bank is its generator's output.

`build_epa8_bank.py --check` compares the committed `items/bank/evaluar_para_avanzar_8.json`,
byte for byte (O-V9), with what the generator writes, and the «Banco de preguntas» job runs it.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "build_epa8_bank.py"
BANK = ROOT / "items" / "bank" / "evaluar_para_avanzar_8.json"
sys.path.insert(0, str(ROOT / "scripts"))


def _check(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", *args], capture_output=True, text=True
    )


def test_spec008_v_the_committed_epa8_bank_passes_the_check():
    """FR-012, US2-AS3: the committed bank is the generator's output."""
    result = _check()

    assert result.returncode == 0, result.stdout + result.stderr


def test_spec008_v_a_hand_edited_epa8_bank_fails_the_check(tmp_path):
    """FR-012, US2-AS3: one option edited by hand makes `--check` fail, naming the item and the
    fix."""
    copy = tmp_path / "evaluar_para_avanzar_8.json"
    shutil.copy(BANK, copy)
    items = json.loads(copy.read_text(encoding="utf-8"))
    items[3]["options"][0] += " (editado)"
    copy.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = _check("--bank", str(copy))

    assert result.returncode == 1, result.stdout + result.stderr
    assert items[3]["id"] in result.stdout and "build_epa8_bank.py" in result.stdout


def test_spec008_v_the_bank_job_runs_the_epa8_check():
    """FR-012: the «Banco de preguntas» job of the CI runs the check (text, no YAML library: the
    job installs only pytest)."""
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    job = ci.split("\n  validate-bank:\n", 1)[1].split("\n  lint:\n", 1)[0]

    assert "run: python scripts/build_epa8_bank.py --check" in job


def test_spec008_v_the_generator_applies_the_bank_difficulty_rule():
    """FR-010 in the generator (constitution II): a source item at 2100 is reported, as the
    validator would."""
    from build_epa8_bank import revisar

    item = {"id": "P99", "difficulty": 2100, "options": ["a", "b"], "correct_option": "a"}

    problems = revisar([item])

    assert any("P99" in p and "400–2000" in p for p in problems)
    assert revisar([{**item, "difficulty": 2000}]) == []
