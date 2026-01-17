# ======================================================
# tests/test_elo.py
# ======================================================
from elo.model import expected_score, StudentELO, Item, update_elo


def test_expected_score_symmetry():
    assert abs(expected_score(1000, 1000) - 0.5) < 1e-6


def test_elo_update_direction():
    student = StudentELO(1000)
    item = Item(1000)
    update_elo(student, item, 1.0)
    assert student.rating > 1000

