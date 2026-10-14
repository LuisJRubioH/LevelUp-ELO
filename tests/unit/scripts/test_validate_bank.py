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
