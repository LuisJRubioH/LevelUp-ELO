"""
A procedure's exercise id is free text typed by the student (`taller_3_p5`), and it becomes one
segment of the Storage key `{student_id}/{item_id}/{hash}.{ext}` and of the local fallback file
name. `safe_path_component` keeps ordinary ids as they are and turns anything else into `_`, so no
`/`, `\\` or `..` can reach outside the student's folder (AGENTS R9).
"""

import pytest

from src.infrastructure.storage.paths import safe_path_component


@pytest.mark.parametrize(
    "item_id",
    ["ejercicio_1", "taller_3_p5", "parcial_2_p3", "ALG-N1-O04-COCIENTE", "calc_lim_017"],
)
def test_ordinary_ids_are_kept(item_id):
    assert safe_path_component(item_id) == item_id


@pytest.mark.parametrize(
    "item_id",
    ["../../7/abc", "..", "a/b", "a\\b", "/etc/passwd", "x/../../y", "p. 74/3", "ñandú 1"],
)
def test_no_separator_or_dot_survives(item_id):
    segment = safe_path_component(item_id)
    assert segment
    assert "/" not in segment and "\\" not in segment and "." not in segment


def test_empty_and_long_ids():
    assert safe_path_component("") == "item"
    assert safe_path_component(None) == "item"
    assert len(safe_path_component("x" * 500)) == 80
