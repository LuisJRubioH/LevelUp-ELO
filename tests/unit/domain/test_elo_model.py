"""
tests/unit/domain/test_elo_model.py
=====================================
Pruebas unitarias del motor ELO.
Sin mocks, sin I/O — lógica matemática pura.

API real:
  expected_score(rating_a, rating_b) -> float
  calculate_dynamic_k(attempts, rating, recent_results) -> float
  update_elo(student, item, result, k, impact_modifier) -> float
"""

import pytest
from src.domain.elo.model import (
    expected_score,
    calculate_dynamic_k,
    update_elo,
    StudentELO,
    Item,
)


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


class TestDynamicKFactor:
    """Factor K dinámico: K=40 (nuevo) → K=32 (creciendo) → K=16 (estable) → K=24"""

    def test_new_student_gets_k40(self):
        """Menos de 30 intentos → K = 40 (convergencia rápida)."""
        k = calculate_dynamic_k(attempts=0, rating=1000, recent_results=[])
        assert k == 40

        k = calculate_dynamic_k(attempts=29, rating=1000, recent_results=[])
        assert k == 40

    def test_growing_student_gets_k32(self):
        """30+ intentos y rating < 1400 → K = 32."""
        k = calculate_dynamic_k(
            attempts=50,
            rating=1200,
            recent_results=[(1, 0.5)] * 50,
        )
        assert k == 32

    def test_stable_student_gets_k16(self):
        """Rating estable (error medio < 15% en últimos 20) → K = 16."""
        # Error de 0.05 < 0.15 → estable
        recent = [(1.0, 0.95)] * 20  # error = 0.05 por intento
        k = calculate_dynamic_k(attempts=100, rating=1600, recent_results=recent)
        assert k == 16

    def test_default_case_gets_k24(self):
        """Rating alto con error alto → K = 24 (base)."""
        # Error de 0.30 > 0.15 → no estable
        recent = [(1.0, 0.7)] * 20  # error = 0.30 por intento
        k = calculate_dynamic_k(attempts=100, rating=1600, recent_results=recent)
        assert k == 24

    def test_k_factor_is_always_positive(self):
        """El factor K nunca puede ser negativo o cero."""
        cases = [
            (0, 500, []),
            (50, 1200, [(1, 0.5)] * 10),
            (100, 1600, [(1, 0.7)] * 20),
            (200, 2000, [(1, 0.96)] * 20),
        ]
        for attempts, rating, recent in cases:
            k = calculate_dynamic_k(attempts, rating, recent)
            assert k > 0, f"K no positivo para ({attempts}, {rating})"


class TestUpdateElo:
    """update_elo(student, item, result, k, impact_modifier) → nuevo rating"""

    def test_correct_answer_increases_rating(self):
        """Acierto donde P < 1.0 siempre produce subida de rating."""
        student = StudentELO(rating=1000.0)
        item = Item(difficulty=1000.0)
        old_rating = student.rating
        new_rating = update_elo(student, item, result=1.0, k=24, impact_modifier=1.0)
        assert new_rating > old_rating

    def test_wrong_answer_decreases_rating(self):
        """Fallo donde P > 0.0 siempre produce bajada de rating."""
        student = StudentELO(rating=1000.0)
        item = Item(difficulty=1000.0)
        old_rating = student.rating
        new_rating = update_elo(student, item, result=0.0, k=24, impact_modifier=1.0)
        assert new_rating < old_rating

    def test_impact_modifier_scales_delta_linearly(self):
        """impact_modifier escala el delta de forma lineal."""
        s1 = StudentELO(rating=1000.0)
        s2 = StudentELO(rating=1000.0)
        item = Item(difficulty=1000.0)
        new1 = update_elo(s1, item, result=1.0, k=24, impact_modifier=1.0)
        new2 = update_elo(s2, item, result=1.0, k=24, impact_modifier=2.0)
        delta1 = new1 - 1000.0
        delta2 = new2 - 1000.0
        assert delta2 == pytest.approx(delta1 * 2.0, abs=1e-6)

    def test_update_elo_mutates_student_rating(self):
        """update_elo modifica student.rating in-place además de retornarlo."""
        student = StudentELO(rating=1000.0)
        item = Item(difficulty=1000.0)
        returned = update_elo(student, item, result=1.0, k=24, impact_modifier=1.0)
        assert student.rating == returned

    def test_invalid_result_raises_value_error(self):
        """Resultado fuera de [0, 1] lanza ValueError."""
        student = StudentELO(rating=1000.0)
        item = Item(difficulty=1000.0)
        with pytest.raises(ValueError):
            update_elo(student, item, result=1.5, k=24, impact_modifier=1.0)

    def test_student_item_elo_symmetry(self):
        """
        El sistema es simétrico: delta(estudiante acierta) = -delta(ítem pierde).
        Usando K idéntico, K*(1-P) para el estudiante = -K*(0-P) para el ítem.
        """
        k = 24
        student_rating = 1000.0
        item_difficulty = 1000.0
        p = expected_score(student_rating, item_difficulty)

        # Delta del estudiante al acertar
        s = StudentELO(rating=student_rating)
        new_s = update_elo(s, Item(difficulty=item_difficulty), 1.0, k=k, impact_modifier=1.0)
        delta_student = new_s - student_rating  # k*(1 - p)

        # Delta simétrico del ítem (el ítem "pierde" cuando el estudiante gana)
        # item_result=0 (perdió), p_item_wins = 1-p
        delta_item = k * (0.0 - (1.0 - p))  # k*(0 - (1-p)) = -k*(1-p) = -delta_student

        assert delta_student == pytest.approx(-delta_item, abs=1e-6)
