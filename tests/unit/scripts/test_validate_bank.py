"""
validate_bank.py: text between two `$` that is not math. The frontend's MathText and V1's
st.markdown render it as one formula, so a sentence with two peso amounts showed
"10millonesimportamaquinariapor" in italics (DIAN item B_Adu_05).
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_bank import prose_read_as_math  # noqa: E402


def test_two_amounts_in_one_sentence_are_flagged():
    text = "un capital de $10 millones importa maquinaria por $5.000 millones"
    assert prose_read_as_math(text) == ["$10 millones importa maquinaria por $"]


@pytest.mark.parametrize(
    "text",
    [
        "una tarjeta de regalo de $500.000",  # one $ is shown as written
        "Si $x^2 = 4$ y $y > 0$, entonces",  # real formulas
        "$\\text{área total}$ más $x$",  # words inside \text are meant
        "$$\\int_0^1 x\\,dx$$",
        "cuesta \\$5 y \\$6",  # escaped dollars are not delimiters
        "10 millones de pesos importa maquinaria por 5.000 millones de pesos",
    ],
)
def test_math_and_single_amounts_pass(text):
    assert prose_read_as_math(text) == []


def test_the_bank_has_no_prose_read_as_math():
    import json

    found = []
    for path in sorted((ROOT / "items" / "bank").rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("items", [])
        for item in items:
            for text in [item.get("content")] + list(item.get("options") or []):
                if isinstance(text, str):
                    found += [(item.get("id"), t) for t in prose_read_as_math(text)]
    assert found == []


# ── Survey 008 B7 (`docs/sdd/item-bank-survey.md` § 7): R5 and the required `topic` ──────────


def _run(tmp_path, item):
    """Runs the validator, as CI does, on a bank with one file holding `item`."""
    import json
    import subprocess

    bank = tmp_path / "items" / "bank"
    bank.mkdir(parents=True)
    good = {
        "id": "b7_1",
        "content": "¿Cuánto es $\\frac{1}{2}+\\frac{1}{2}$?",
        "difficulty": 900,
        "topic": "Fracciones",
        "options": ["$1$", "$2$"],
        "correct_option": "$1$",
    }
    (bank / "b7.json").write_text(json.dumps([{**good, **item}]), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_bank.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def test_a_well_formed_item_passes(tmp_path):
    result = _run(tmp_path, {})
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("field", ["content", "options"])
def test_an_unescaped_backslash_in_latex_is_an_error(tmp_path, field):
    """R5: `"\\frac"` written with one backslash in the JSON decodes to a form feed + "rac"."""
    text = "$\frac{1}{2}$"  # a form feed: what json.loads gives for "$\frac{1}{2}$"
    item = {"content": text} if field == "content" else {"options": [text, "$2$"]}
    if field == "options":
        item["correct_option"] = "$2$"

    result = _run(tmp_path, item)

    assert result.returncode == 1
    assert "carácter de control" in result.stdout and "R5" in result.stdout


def test_a_newline_that_cuts_a_formula_is_an_error(tmp_path):
    """R5: `"$a \\neq b$"` with one backslash is a newline + "eq" inside the formula. A newline
    between formulas is Markdown (the bank's lists and tables) and passes."""
    broken = _run(tmp_path / "broken", {"content": "Si $a \neq b$, entonces"})
    markdown = _run(tmp_path / "markdown", {"content": "Lista:\n\n- $a+b$\n- $a-b$"})

    assert broken.returncode == 1 and "dentro de una fórmula" in broken.stdout
    assert markdown.returncode == 0, markdown.stdout


@pytest.mark.parametrize("topic", ["", "   ", None, 3])
def test_an_empty_or_non_text_topic_is_an_error(tmp_path, topic):
    """`topic` is a required field (AGENTS § Item bank): it names the rating row (R15)."""
    result = _run(tmp_path, {"topic": topic})

    assert result.returncode == 1
    assert "'topic'" in result.stdout
