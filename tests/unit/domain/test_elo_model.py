"""
tests/unit/domain/test_elo_model.py
=====================================
Pruebas unitarias del motor ELO.
Sin mocks, sin I/O — lógica matemática pura.

API real:
  expected_score(rating_a, rating_b) -> float

Dynamic K (`calculate_dynamic_k`) and `update_elo` were never used by the engine and were
deleted by spec 001 (task T026, constitution VII); their tests went with them.
"""

import pytest
from src.domain.elo.model import expected_score


class TestExpectedScore:
    """Fórmula P = 1 / (1 + 10^((D - R) / 400))"""

    def test_equal_ratings_give_50_percent(self):
        """Estudiante y ítem con igual rating → P exactamente 0.5."""
        p = expected_score(1000, 1000)
        assert p == pytest.approx(0.5, abs=1e-6)

    def test_stronger_student_has_higher_probability(self):
        """Estudiante más fuerte tiene mayor probabilidad de éxito."""
        p_strong = expected_score(1200, 1000)
        p_weak = expected_score(800, 1000)
        assert p_strong > 0.5
        assert p_weak < 0.5
        assert p_strong > p_weak

    def test_probability_always_in_valid_range(self):
        """La probabilidad siempre está en (0, 1) — nunca 0 ni 1 exacto."""
        extreme_cases = [
            (0, 3000),
            (3000, 0),
            (1000, 1000),
            (500, 2500),
            (2500, 500),
        ]
        for student, item in extreme_cases:
            p = expected_score(student, item)
            assert 0.0 < p < 1.0, f"P fuera de rango para ({student}, {item}): {p}"

    def test_400_point_advantage_gives_approx_91_percent(self):
        """Diferencia de 400 puntos a favor → P ≈ 0.909."""
        p = expected_score(1400, 1000)
        assert p == pytest.approx(1 / (1 + 10 ** (-400 / 400)), abs=1e-6)

    def test_symmetry_complements_to_one(self):
        """P(A vs B) + P(B vs A) == 1.0."""
        p_ab = expected_score(1200, 1000)
        p_ba = expected_score(1000, 1200)
        assert p_ab + p_ba == pytest.approx(1.0, abs=1e-6)
