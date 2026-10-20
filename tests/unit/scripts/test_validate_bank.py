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


def _run(tmp_path, item, course="geometria"):
    """Runs the validator, as CI does, on a bank with one file holding `item`. The file is named
    after a mapped course unless `course` says otherwise."""
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
    (bank / f"{course}.json").write_text(json.dumps([{**good, **item}]), encoding="utf-8")
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


# ── Survey 008 B7, decision 2 (owner, 2026-10-20): the rest of the checks, as errors ──────────


@pytest.mark.parametrize("item_id", [17, "", "   ", None])
def test_an_id_that_is_not_text_is_an_error(tmp_path, item_id):
    """`id` is globally unique text: a number would collide with "17" once stored."""
    result = _run(tmp_path, {"id": item_id})

    assert result.returncode == 1
    assert "'id'" in result.stdout


@pytest.mark.parametrize("tags", ["algebra", ["algebra", 3], ["algebra", ""], {"a": 1}])
def test_tags_must_be_a_list_of_text(tmp_path, tags):
    result = _run(tmp_path, {"tags": tags})

    assert result.returncode == 1
    assert "'tags'" in result.stdout


def test_a_list_of_text_tags_passes(tmp_path):
    result = _run(tmp_path, {"tags": ["algebra", "fracciones"]})

    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("field", ["image_url", "image_path"])
def test_an_image_that_does_not_exist_is_an_error(tmp_path, field):
    result = _run(tmp_path, {field: "items/assets/no_existe.svg"})

    assert result.returncode == 1
    assert "no existe" in result.stdout


def test_an_image_that_exists_passes(tmp_path):
    image = tmp_path / "items" / "assets" / "figura.svg"
    image.parent.mkdir(parents=True)
    image.write_text("<svg/>", encoding="utf-8")

    result = _run(tmp_path, {"image_url": "items/assets/figura.svg"})

    assert result.returncode == 0, result.stdout


def test_a_course_missing_from_the_course_map_is_an_error(tmp_path):
    """A file whose course is not in `_COURSE_BLOCK_MAP` used to land in «Universidad» silently."""
    result = _run(tmp_path, {}, course="curso_sin_mapa")

    assert result.returncode == 1
    assert "curso_sin_mapa" in result.stdout and "_COURSE_BLOCK_MAP" in result.stdout


def test_the_course_map_is_read_from_both_repositories():
    from validate_bank import course_block_maps

    sqlite_map, postgres_map = course_block_maps()

    assert sqlite_map == postgres_map  # R1
    assert sqlite_map["geometria"] == "Colegio"
