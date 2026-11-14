"""QA ronda 1 (D3, D5): what a lesson says to the student, checked over every node.

D3 — a node's `feedback.default` is the message a student reads after each wrong typed answer
of the practice, the bridge and the closure. It is that node's way of checking the answer, so
no two nodes share one (AGENTS.md V2-R11).

D5 — the student never sees a node code: the map calls `PREALG-N1-B05-…` «Enteros». A visible
text that says «eso abre B06» or «lo verás en N4-C04» points at nothing they can find.
"""

import re
from collections import defaultdict

import pytest

from src.domain.learning.nodes import NODE_MODULES, a00_hub, s00_hub_bagdad


def _name(module) -> str:
    return module.__name__.rsplit(".", 1)[-1]


# ── D3 ───────────────────────────────────────────────────────────────────────


def test_qa_every_node_has_a_default_feedback_of_its_own():
    nodes_by_default = defaultdict(list)
    for module in NODE_MODULES:
        default = module.CONTENT["feedback"]["default"]
        assert default.strip(), f"{_name(module)}: empty feedback.default"
        nodes_by_default[default].append(_name(module))

    shared = {text: nodes for text, nodes in nodes_by_default.items() if len(nodes) > 1}
    assert shared == {}, f"feedback.default shared by several nodes (write one per node): {shared}"


# ── D5 ───────────────────────────────────────────────────────────────────────

# Fields of CONTENT the screen never shows: identifiers, routing, answer keys and labels for
# the people who write the nodes (`validation_status`, `tipo`, `tags`).
_NOT_SHOWN = {
    "id",
    "node_id",
    "kind",
    "image",
    "scene",
    "expected",
    "valid_options",
    "trap_options",
    "answer",
    "unlock_after",
    "next_node_id",
    "tipo",
    "tags",
    "validation_status",
}

# A node code: its letter and two digits (B05, C04, M01) standing alone, a level (N1 … N4) as a
# word, or the prefix of a node id. A letter stuck to other letters or digits is not one, so
# `MCD12`, `x2`, `3A` and `H2O` pass.
_ALNUM = "0-9A-Za-zÀ-ÖØ-öø-ÿ"
_NODE_CODE = re.compile(
    rf"(?<![{_ALNUM}])[BEMCLOFRPGSA]\d{{2}}(?![{_ALNUM}])"
    rf"|(?<![{_ALNUM}])N[1-4](?![{_ALNUM}])"
    r"|ALG-|PREALG"
)
_MATH = re.compile(r"\$\$[^$]*\$\$|\$[^$]*\$")


def _visible_texts(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in _NOT_SHOWN or "misconception" in key:
                continue
            yield from _visible_texts(child, path + (key,))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from _visible_texts(child, path + (index,))
    elif isinstance(value, str):
        yield ".".join(str(part) for part in path), value


def _node_codes(text: str) -> list[str]:
    """The node codes a text cites outside its formulas."""
    return _NODE_CODE.findall(_MATH.sub(" ", text))


@pytest.mark.parametrize("module", [*NODE_MODULES, a00_hub, s00_hub_bagdad], ids=_name)
def test_qa_no_visible_text_cites_a_node_code(module):
    offenders = {path: text for path, text in _visible_texts(module.CONTENT) if _node_codes(text)}
    assert offenders == {}, (
        "a visible text cites a node code the student never sees; "
        f"name the node as the map does («Enteros», «Factorización prima»): {offenders}"
    )


@pytest.mark.parametrize(
    "text, codes",
    [
        ("Ese único agujero es el que abre B05: los enteros.", ["B05"]),
        ("Solo terminan las que se factorizan con 2 y 5 (lo verás en N4-C04).", ["N4", "C04"]),
        ("Eso se formaliza en N3 (M01 y M02).", ["N3", "M01", "M02"]),
        ("la escalera de N1 tuvo que crecer", ["N1"]),
        ("Vuelve a PREALG-N1-B05-ENTEROS-DEUDA.", ["PREALG", "N1", "B05"]),
        ("Sigue en ALG-N2-P01-CUADRADO.", ["ALG-", "N2", "P01"]),
    ],
)
def test_qa_the_check_catches_the_codes_that_reached_the_student(text, codes):
    assert _node_codes(text) == codes


@pytest.mark.parametrize(
    "text",
    [
        "Ese único agujero es el que abre el peldaño de los enteros.",
        "Lo verás en Factorización prima (Nivel 4).",
        "El área es $A = 12$ y el lado $L05$ no existe: $B12 + C04$.",
        "MCD(12, 18) = 6 y MCM(4, 6) = 12",
        "3A + 2B = 12; x2 + 16; a2b3; H2O; 2N; N = 12",
        "√9 = 3, y 3 = 3/1 es racional. ℕ ⊂ ℤ ⊂ ℚ",
        "En 1,41 × 1,41 = 1,9881 no hay 2. Caben 10 fardos de 25 kg.",
        "La sala P de los troqueles; el nivel 3; N, Z y Q.",
    ],
)
def test_qa_the_check_leaves_mathematics_and_plain_words_alone(text):
    assert _node_codes(text) == []


def test_qa_the_check_skips_what_the_screen_never_shows():
    content = {
        "node_id": "PREALG-N1-B05-ENTEROS-DEUDA",
        "validation_status": "F1_B05_11bloques",
        "default_misconception": "viene_de_B05",
        "practice": [{"id": "B05-E1", "expected": "B05", "hints": {"n1": "Mira B05."}}],
    }
    assert dict(_visible_texts(content)) == {"practice.0.hints.n1": "Mira B05."}
