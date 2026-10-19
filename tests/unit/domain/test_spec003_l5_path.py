"""
Spec 003 L5 (FR-050, FR-051; US5-AS1, US5-AS3; N3): the unlock rules are node data, read by one
domain function, and the catalogue is checked when it loads.
"""

import pytest

from src.domain.learning import prealgebra
from src.domain.learning.path import CatalogueError, node_access, validate_catalogue


def _node(node_id, unlock_after=None, **extra):
    return {"node_id": node_id, "unlock_after": unlock_after, "node_type": "x", **extra}


def _catalogue(*nodes):
    return {n["node_id"]: n for n in nodes}


def test_catalogue_has_one_root_no_dangling_reference_no_cycle():
    """US5-AS1, FR-051: the real catalogue loads; each broken shape is refused."""
    validate_catalogue(prealgebra._LESSONS)

    with pytest.raises(CatalogueError, match="root"):
        validate_catalogue(_catalogue(_node("A"), _node("B")))
    with pytest.raises(CatalogueError, match="missing"):
        validate_catalogue(_catalogue(_node("A"), _node("B", unlock_after="Z")))
    with pytest.raises(CatalogueError, match="missing"):
        validate_catalogue(_catalogue(_node("A"), _node("B", "A", gates=["Z"])))
    with pytest.raises(CatalogueError, match="cycle"):
        validate_catalogue(_catalogue(_node("A"), _node("B", "C"), _node("C", "B")))


def test_gates_and_bands_come_from_node_data():
    """US5-AS3: a fabricated node's gates and band decide, with no id in code."""
    gated = _node("G", "A", gates=["P", "Q"])
    banded = _node("O", "A", requires_band=["intermedio", "avanzado"])
    done = {"A", "P"}

    def state_of(node_id):
        return "completed" if node_id in done else "available"

    assert node_access(_node("A"), state_of, "basico") is None
    assert node_access(gated, state_of, "basico") is not None  # Q is not completed
    done.add("Q")
    assert node_access(gated, state_of, "basico") is None
    assert node_access(banded, state_of, "basico") is not None
    assert node_access(banded, state_of, "intermedio") is None
    assert node_access(_node("B", "C"), state_of, "avanzado") is not None


def test_the_catalogue_declares_the_old_special_cases_as_data():
    """US5-AS3, N3: the N3 gate, the B09 band and every hub's completion are in the catalogue."""
    lessons = prealgebra._LESSONS
    for node_id in prealgebra.N3_NODE_IDS:
        assert set(lessons[node_id]["gates"]) == set(prealgebra.N2_OPERATION_NODE_IDS)
    assert lessons[prealgebra.COMPLEX_NODE_ID]["requires_band"] == ["intermedio", "avanzado"]
    hubs = [n for n, lesson in lessons.items() if lesson["node_type"].startswith("level_hub")]
    assert len(hubs) == 5
    assert all(lessons[n]["completion"] == "cards" for n in hubs)
