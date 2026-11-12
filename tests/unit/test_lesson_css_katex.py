"""QA ronda 1, Q1: a lesson stylesheet must not turn every descendant `span` into a block.

KaTeX builds a formula out of nested `span`s laid out inline. A rule such as
`.block-trap-contrast .wrong span { display: block }`, meant for a label, also reached every
span of the formula beside it: the formula fell apart one piece a line and `\\notin` lost its
stroke, so the trap's «lo que escribió» read «∈» where it said «∉». A label rule names its own
span as a direct child (`> span`) or by class.
"""

import re
from pathlib import Path

LESSONS = Path(__file__).resolve().parents[2] / "frontend" / "src" / "pages" / "Student" / "lessons"

# The last compound of a selector is a bare `span` reached through a descendant combinator.
_DESCENDANT_SPAN = re.compile(r"[\w\)\]\*]\s+span(?::[\w-]+(?:\([^)]*\))?)*\s*$")


def _descendant_span_blocks(css: str) -> list[str]:
    found = []
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if not re.search(r"display\s*:\s*block", body):
            continue
        for part in selector.split(","):
            part = re.sub(r"/\*.*?\*/", "", part, flags=re.S).strip()
            if _DESCENDANT_SPAN.search(part):
                found.append(part)
    return found


def test_qa_q1_no_lesson_rule_blocks_every_descendant_span():
    offenders = {
        str(path.relative_to(LESSONS)): rules
        for path in sorted(LESSONS.rglob("*.css"))
        if (rules := _descendant_span_blocks(path.read_text(encoding="utf-8")))
    }
    assert offenders == {}, (
        "A descendant `span { display: block }` also breaks the KaTeX formulas inside it; "
        f"use `> span` or a class: {offenders}"
    )


def test_qa_q1_the_check_catches_the_rule_that_broke_the_trap():
    assert _descendant_span_blocks(".block-trap-contrast .wrong span { display: block; }")
    assert not _descendant_span_blocks(".block-trap-contrast .wrong > span { display: block; }")
    assert not _descendant_span_blocks(".block-trap-contrast span.label { display: block; }")
