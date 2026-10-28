"""Spec 008 delivery V: the bank's rules as pure functions (`src/domain/bank/rules.py`, O-V2).

FR-010 (D1): a difficulty is a JSON integer in 400–2000 (O-V1: `900.0`, `"900"` and `true` are not).
FR-011 (D4): an id never changes course or topic against the committed manifest; the manifest only
grows (O-V3 … O-V8).
"""

import json

import pytest

from src.domain.bank import rules


@pytest.mark.parametrize("value", [400, 401, 1000, 1999, 2000])
def test_spec008_v_difficulty_rule(value):
    """FR-010: an integer in 400–2000 inclusive passes; anything else is a problem naming the value
    and the range."""
    assert rules.DIFFICULTY_RANGE == (400, 2000)
    assert rules.difficulty_problem(value) is None
    for bad in (350, 399, 2001, 2100, 900.5, 900.0, True, False, "900", None, [900]):
        problem = rules.difficulty_problem(bad)
        assert problem is not None, bad
        assert repr(bad) in problem and "400–2000" in problem


def test_spec008_v_manifest_rules():
    """FR-011: a moved id names both values; an unlisted id names the script; a listed id missing
    from the bank is a problem (O-V6); the manifest only grows; its text is one line per id."""
    manifest = {"a1": ["dian", "Constitución"], "b2": ["geometria", "Ángulos"]}
    bank = [("a1", "sena", "Constitución"), ("b2", "geometria", "Triángulos"), ("c3", "x", "T")]

    problems = rules.manifest_problems(manifest, bank)

    assert any("a1" in p and "dian" in p and "sena" in p for p in problems)
    assert any("b2" in p and "Ángulos" in p and "Triángulos" in p for p in problems)
    assert any("c3" in p and "update_id_manifest.py" in p for p in problems)
    missing = rules.manifest_problems(manifest, [("a1", "dian", "Constitución")])
    assert len(missing) == 1 and "b2" in missing[0]  # O-V6: listed, gone from the bank

    grown = rules.appended_manifest(manifest, [("c3", "x", "T"), ("a1", "otro", "otro")])
    assert grown == {**manifest, "c3": ["x", "T"]}  # appends; never changes an entry
    assert manifest == {"a1": ["dian", "Constitución"], "b2": ["geometria", "Ángulos"]}
    assert rules.moved_ids(manifest, [("a1", "otro", "Constitución")]) == ["a1"]

    assert rules.manifest_changes(manifest, grown) == []
    changed = rules.manifest_changes(grown, {"a1": ["dian", "Otro"], "c3": ["x", "T"]})
    assert any("a1" in c and "Constitución" in c and "Otro" in c for c in changed)
    assert any("b2" in c for c in changed)

    text = rules.render_manifest(grown)
    assert json.loads(text) == grown
    lines = text.splitlines()
    assert lines[0] == "{" and lines[-1] == "}" and text.endswith("}\n")
    assert [line.split(":")[0].strip() for line in lines[1:-1]] == ['"a1"', '"b2"', '"c3"']
