"""
Spec 003 L2 (FR-020; N7, N8, N9): the content a lesson sends is an allow-list projection.

Every field of every node's content is classified — public, a grading key, or internal — so a
field added later fails here until someone decides which it is; at runtime an unclassified field
is left out. The projection keeps every public field the renderer reads and no grading key.
"""

from collections import defaultdict

import pytest

from src.domain.learning import prealgebra
from src.domain.learning.public_content import (
    GRADING_KEYS,
    INTERNAL_PATHS,
    OPAQUE_PATHS,
    PUBLIC_PATHS,
    public_content,
)

WITH_CONTENT = [n for n, lesson in prealgebra._LESSONS.items() if lesson.get("content")]

# What the renderers read (LessonBlocks.tsx, ElevenBlockLesson.tsx, the hub lessons): kept.
RENDERER_READS = {
    ".practice[].options[].text",
    ".practice[].valid_options",  # N7: the choices of a multiple-answer item
    ".practice[].hints.n3",
    ".closing_item.polya.comprobar",
    ".bridge.items[].blanks[].label",
    ".abstraction_question.options[].text",
    ".worked_examples[].solution",  # N8
    ".worked_examples[].correct_version.rows[].right",  # N8
    ".feedback.correct",
    ".icebreaker.items[].options[].text",
    ".buildings[].building",
    ".machines[].demo",
}


def _paths(value, path="", found=None):
    found = defaultdict(int) if found is None else found
    if isinstance(value, dict):
        for key, child in value.items():
            found[f"{path}.{key}"] += 1
            if not any(f"{path}.{key}" == opaque for opaque in OPAQUE_PATHS):
                _paths(child, f"{path}.{key}", found)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _paths(child, f"{path}[]", found)
    return found


def _is_key(path):
    return (
        path.rsplit(".", 1)[-1] in GRADING_KEYS or path == ".abstraction_question.options[].correct"
    )


def test_every_content_field_is_classified():
    """FR-020: public, grading key or internal — nothing else."""
    unclassified = set()
    for node_id in WITH_CONTENT:
        for path in _paths(prealgebra._LESSONS[node_id]["content"]):
            if path not in PUBLIC_PATHS | OPAQUE_PATHS | INTERNAL_PATHS and not _is_key(path):
                unclassified.add(path)
    assert unclassified == set()
    assert not {p for p in PUBLIC_PATHS if _is_key(p)}, "a grading key is in the allow-list"


@pytest.mark.parametrize("node_id", WITH_CONTENT)
def test_projection_keeps_what_the_renderer_reads(node_id):
    """FR-020, N7, N8: every public field survives, and no grading key or internal field."""
    content = prealgebra._LESSONS[node_id]["content"]
    before, after = _paths(content), _paths(public_content(content))

    assert set(after) == {p for p in before if p in PUBLIC_PATHS | OPAQUE_PATHS}
    assert not {p for p in after if _is_key(p) or p in INTERNAL_PATHS}
    assert after == {p: n for p, n in before.items() if p in after}, "a list lost elements"


def test_the_renderer_fields_are_public():
    assert RENDERER_READS <= PUBLIC_PATHS | {
        p for p in RENDERER_READS if any(p.startswith(f"{o}.") for o in OPAQUE_PATHS)
    }


def test_the_projection_does_not_touch_the_catalogue():
    """The server keeps every key for grading (plan-l2: node modules unchanged)."""
    node_id = next(n for n in WITH_CONTENT if prealgebra._LESSONS[n]["content"].get("practice"))
    content = prealgebra._LESSONS[node_id]["content"]
    public_content(content)
    assert any("expected" in item or "answer" in item for item in content["practice"])
