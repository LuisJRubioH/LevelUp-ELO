"""
tests/unit/domain/test_vector_elo.py
=====================================
Pruebas del VectorRating (ELO por tópico).

API real:
  VectorRating() — sin parámetros, defaults 1000.0/350.0
  v.get(concept) -> float
  v.get_rd(concept) -> float
  v.update(concept, difficulty, result) -> (new_r, new_rd)
"""

import pytest
from src.domain.elo.vector_elo import VectorRating

_DEFAULT_RATING = 1000.0
_DEFAULT_RD = 350.0


class TestVectorRatingDefaults:
    def test_unknown_topic_returns_default_rating(self, student_vector):
        """Tópico nunca actualizado → rating por defecto 1000.0."""
        assert student_vector.get("TemaDesconocido") == _DEFAULT_RATING

    def test_unknown_topic_returns_default_rd(self, student_vector):
        """Tópico nunca actualizado → RD por defecto 350.0."""
        assert student_vector.get_rd("TemaDesconocido") == _DEFAULT_RD


class TestVectorRatingUpdate:
    def test_correct_answer_increases_topic_rating(self, student_vector):
        """Acierto en un tópico aumenta el rating de ese tópico."""
        initial_rating = student_vector.get("Álgebra")
        student_vector.update("Álgebra", 1000.0, 1.0)
        new_rating = student_vector.get("Álgebra")
        assert new_rating > initial_rating

    def test_wrong_answer_decreases_topic_rating(self, student_vector):
        """Fallo en un tópico disminuye el rating de ese tópico."""
        initial_rating = student_vector.get("Álgebra")
        student_vector.update("Álgebra", 1000.0, 0.0)
        new_rating = student_vector.get("Álgebra")
        assert new_rating < initial_rating

    def test_topics_are_independent(self, student_vector):
        """Actualizar un tópico no afecta otros tópicos."""
        student_vector.update("Álgebra", 1000.0, 1.0)
        algebra_rating = student_vector.get("Álgebra")
        calculus_rating = student_vector.get("Cálculo")
        # Cálculo debe mantener el rating por defecto (sin actualizar)
        assert calculus_rating == _DEFAULT_RATING
        assert algebra_rating != _DEFAULT_RATING

    def test_rd_decreases_with_experience(self, student_vector):
        """El Rating Deviation disminuye a medida que se acumula experiencia."""
        initial_rd = student_vector.get_rd("Álgebra")
        for _ in range(10):
            student_vector.update("Álgebra", 1000.0, 1.0)
        final_rd = student_vector.get_rd("Álgebra")
        assert final_rd < initial_rd

    def test_update_returns_new_rating_and_rd(self, student_vector):
        """update() retorna tupla (new_rating, new_rd)."""
        result = student_vector.update("Álgebra", 1000.0, 1.0)
        assert isinstance(result, tuple)
        assert len(result) == 2
        new_r, new_rd = result
        assert new_r == student_vector.get("Álgebra")
        assert new_rd == student_vector.get_rd("Álgebra")


# TestAggregateGlobalElo was removed by spec 001 (T064, FR-028a): the overall rating is the
# mean of course ratings, `src/domain/elo/aggregation.py::overall_rating`
# (tests/unit/domain/test_spec001_domain.py).
