"""
tests/unit/domain/test_cognitive_analyzer.py
=============================================
Pruebas unitarias de CognitiveAnalyzer.

Solo se prueban los caminos que NO requieren llamada a IA externa:
- analyze_cognition con texto vacío/corto (short-circuit)
- compute_time_modifier (lógica pura de tiempo)
"""
import pytest
from src.domain.elo.cognitive import CognitiveAnalyzer


@pytest.fixture
def analyzer() -> CognitiveAnalyzer:
    return CognitiveAnalyzer(base_url="", model_name="test-model")


class TestAnalyzeCognitionShortCircuit:
    """Cuando el texto de razonamiento está vacío o es muy corto, se usa
    impact_modifier=1.0 sin llamar a la IA."""

    def test_empty_text_returns_neutral_modifier(self, analyzer):
        """Texto vacío → impact_modifier=1.0."""
        result = analyzer.analyze_cognition("", is_correct=True, time_taken=10.0)
        assert result["impact_modifier"] == 1.0

    def test_short_text_returns_neutral_modifier(self, analyzer):
        """Texto muy corto (< 5 chars) → impact_modifier=1.0."""
        result = analyzer.analyze_cognition("abc", is_correct=True, time_taken=10.0)
        assert result["impact_modifier"] == 1.0

    def test_empty_text_returns_required_fields(self, analyzer):
        """El resultado siempre incluye los campos requeridos."""
        result = analyzer.analyze_cognition("", is_correct=False, time_taken=5.0)
        assert "confidence_score" in result
        assert "error_type" in result
        assert "impact_modifier" in result
        assert "reasoning" in result

    def test_none_text_returns_neutral_modifier(self, analyzer):
        """Texto None → impact_modifier=1.0 (misma rama que vacío)."""
        result = analyzer.analyze_cognition(None, is_correct=True, time_taken=10.0)
        assert result["impact_modifier"] == 1.0


class TestComputeTimeModifier:
    """compute_time_modifier es lógica pura — sin IA."""

    def test_fast_correct_answer_gives_bonus(self, analyzer):
        """Acierto muy rápido (< 5s) → modificador 1.2 (maestría)."""
        mod = analyzer.compute_time_modifier(time_taken=3.0, is_correct=True)
        assert mod == 1.2

    def test_slow_correct_answer_gives_penalty(self, analyzer):
        """Acierto muy lento (> 30s) → modificador 0.8 (duda)."""
        mod = analyzer.compute_time_modifier(time_taken=45.0, is_correct=True)
        assert mod == 0.8

    def test_normal_correct_answer_gives_neutral(self, analyzer):
        """Acierto en tiempo normal → modificador 1.0."""
        mod = analyzer.compute_time_modifier(time_taken=15.0, is_correct=True)
        assert mod == 1.0

    def test_fast_wrong_answer_reduces_penalty(self, analyzer):
        """Fallo muy rápido (< 3s) → modificador 0.7 (descuido, penalización reducida)."""
        mod = analyzer.compute_time_modifier(time_taken=1.5, is_correct=False)
        assert mod == 0.7

    def test_normal_wrong_answer_gives_neutral(self, analyzer):
        """Fallo en tiempo normal → modificador 1.0."""
        mod = analyzer.compute_time_modifier(time_taken=20.0, is_correct=False)
        assert mod == 1.0

    def test_modifier_is_always_positive(self, analyzer):
        """El modificador de tiempo nunca es negativo."""
        cases = [(1.0, True), (4.9, True), (31.0, True), (2.9, False), (15.0, False)]
        for time_taken, is_correct in cases:
            mod = analyzer.compute_time_modifier(time_taken, is_correct)
            assert mod > 0
