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


def _run(tmp_path, item, course="geometria", manifest=None):
    """Runs the validator, as CI does, on a bank with one file holding `item`. The file is named
    after a mapped course unless `course` says otherwise. The bank's id manifest (spec 008 FR-011)
    lists the item as it is, unless `manifest` gives one (`False`: no manifest file)."""
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
    written = {**good, **item}
    (bank / f"{course}.json").write_text(json.dumps([written]), encoding="utf-8")
    if manifest is None:
        valid = isinstance(written["id"], str) and isinstance(written["topic"], str)
        manifest = {written["id"]: [course, written["topic"]]} if valid else {}
    if manifest is not False:
        (tmp_path / "items" / "id_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )
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


# ── Spec 008 delivery T (B19): `subtopic` and small topics ────────────────────────────────────


@pytest.mark.parametrize("subtopic", ["", "   ", 3, ["fracciones"]])
def test_subtopic_must_be_text(tmp_path, subtopic):
    """FR-040: `subtopic` is optional; when present it is non-empty text, like `topic`."""
    result = _run(tmp_path, {"subtopic": subtopic})

    assert result.returncode == 1
    assert "'subtopic'" in result.stdout


def test_a_text_subtopic_passes(tmp_path):
    result = _run(tmp_path, {"subtopic": "suma de fracciones"})

    assert result.returncode == 0, result.stdout


def test_a_small_topic_warns_and_passes(tmp_path):
    """FR-043, US5-AS4: a topic with fewer than 5 items warns, naming it, and does not fail."""
    result = _run(tmp_path, {})

    assert result.returncode == 0, result.stdout
    warning = [line for line in result.stdout.splitlines() if "tema 'Fracciones'" in line]
    assert warning and "menos de 5" in warning[0]


# ── Spec 008 delivery V: validator rules (FR-010 D1, FR-011 D4) ───────────────────────────────


@pytest.mark.parametrize("difficulty", [350, 399, 2001, 2100, 900.5, 900.0, True, "900"])
def test_spec008_v_a_difficulty_outside_400_2000_or_not_an_integer_fails(tmp_path, difficulty):
    """FR-010, US2-AS1: a difficulty that is not a JSON integer in 400–2000 fails, naming the value
    and the range (O-V1: `900.0`, `"900"` and `true` are not integers)."""
    result = _run(tmp_path, {"difficulty": difficulty})

    assert result.returncode == 1, result.stdout
    line = next(line for line in result.stdout.splitlines() if "difficulty" in line)
    assert repr(difficulty) in line and "400–2000" in line


@pytest.mark.parametrize("difficulty", [400, 1000, 2000])
def test_spec008_v_an_integer_difficulty_in_400_2000_passes(tmp_path, difficulty):
    """FR-010, US2-AS1: an integer in 400–2000, both ends included, passes."""
    result = _run(tmp_path, {"difficulty": difficulty})

    assert result.returncode == 0, result.stdout


def test_spec008_v_agents_states_the_validators_difficulty_range():
    """FR-010: AGENTS § Item bank states the validator's range (400–2000); README's summary of the
    required fields says the same."""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    section = agents.split("\n## Item bank\n", 1)[1].split("\n## ", 1)[0]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "`difficulty` (int, 400–2000)" in section
    assert "`difficulty` (entero, 400–2000)" in readme
    assert "600–1800" not in section and "600–1800" not in readme


def test_spec008_v_an_id_whose_course_changed_fails_naming_both_values(tmp_path):
    """FR-011, US2-AS2: the manifest says `b7_1` is in trigonometria; the bank has it in
    geometria."""
    result = _run(tmp_path, {}, manifest={"b7_1": ["trigonometria", "Fracciones"]})

    assert result.returncode == 1, result.stdout
    line = next(line for line in result.stdout.splitlines() if "b7_1" in line)
    assert "trigonometria" in line and "geometria" in line


def test_spec008_v_an_id_whose_topic_changed_fails_naming_both_values(tmp_path):
    """FR-011, US2-AS2: the manifest says `b7_1` is in topic «Ángulos»; the bank says
    «Fracciones»."""
    result = _run(tmp_path, {}, manifest={"b7_1": ["geometria", "Ángulos"]})

    assert result.returncode == 1, result.stdout
    line = next(line for line in result.stdout.splitlines() if "b7_1" in line)
    assert "Ángulos" in line and "Fracciones" in line


def test_spec008_v_a_new_id_fails_until_the_script_adds_it(tmp_path):
    """FR-011, US2-AS2: a bank id the manifest lacks fails, naming the id and the script that adds
    it (O-V4); once the script ran, the bank passes."""
    import subprocess

    before = _run(tmp_path, {}, manifest={})

    assert before.returncode == 1, before.stdout
    line = next(line for line in before.stdout.splitlines() if "b7_1" in line)
    assert "update_id_manifest.py" in line

    added = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "update_id_manifest.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert added.returncode == 0, added.stdout + added.stderr
    after = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_bank.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert after.returncode == 0, after.stdout


def test_spec008_v_a_manifest_id_missing_from_the_bank_fails(tmp_path):
    """FR-011, O-V6: an id the manifest lists and the bank no longer has is an error until
    delivery L (removing an item does not stop it being served)."""
    manifest = {"b7_1": ["geometria", "Fracciones"], "b7_0": ["geometria", "Fracciones"]}

    result = _run(tmp_path, {}, manifest=manifest)

    assert result.returncode == 1, result.stdout
    assert any("b7_0" in line for line in result.stdout.splitlines())


def test_spec008_v_a_missing_manifest_fails(tmp_path):
    """FR-011, O-V8: without `items/id_manifest.json` the validator fails (deleting the file would
    switch D4 off)."""
    result = _run(tmp_path, {}, manifest=False)

    assert result.returncode == 1, result.stdout
    assert "id_manifest.json" in result.stdout
