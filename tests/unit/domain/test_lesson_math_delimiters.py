"""QA ronda 1: text the lesson renders through `MathText` carries its LaTeX inside `$…$`.

`MathText` renders only what sits between dollar signs; the rest is plain text. The trap's
comparison rows (`correct_version.rows[].wrong/right`) mix words and formulas, so a bare
`\\dfrac{3}{10}\\ \\text{es menos que}…` reached the student as backslashes. Fields that go
through `MathFormula` (`latex`, `*_latex`, `symbol`, …) are LaTeX already and are not checked.
"""

import re

import pytest

from src.domain.learning.nodes import NODE_MODULES

_LATEX_OUTSIDE = re.compile(r"\\[a-zA-Z]+|\{,\}")


def _modules():
    import importlib

    return [importlib.import_module(m) if isinstance(m, str) else m for m in NODE_MODULES]


def _bare_latex(text: str) -> str | None:
    outside = re.sub(r"\$\$[^$]*\$\$|\$[^$]*\$", "", text)
    found = _LATEX_OUTSIDE.search(outside)
    return found.group(0) if found else None


@pytest.mark.parametrize("module", _modules(), ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_qa_trap_rows_keep_latex_inside_dollars(module):
    offenders = [
        text
        for example in module.CONTENT.get("worked_examples", [])
        for row in (example.get("correct_version") or {}).get("rows", [])
        for text in (row.get("wrong", ""), row.get("right", ""))
        if _bare_latex(text)
    ]
    assert offenders == [], f"LaTeX outside $…$ in a trap row (wrap the formula): {offenders}"


def test_qa_the_check_catches_the_rows_that_reached_the_student_as_backslashes():
    assert _bare_latex(r"\dfrac{3}{10}\ \text{es menos que}\ \dfrac{2}{5}") == r"\dfrac"
    assert _bare_latex(r"1{,}20-0{,}20=1") == "{,}"
    assert _bare_latex(r"$\dfrac{3}{10}$ es menos que $\dfrac{2}{5}$") is None
    assert _bare_latex("3 · 4 = 12") is None
