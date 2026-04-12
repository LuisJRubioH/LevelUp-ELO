"""
tests/unit/domain/test_katia_messages.py
=========================================
Pruebas de las funciones de mensajes de KatIA.
Son funciones puras — sin mocks, sin I/O.
"""
import pytest
from src.domain.katia.katia_messages import (
    get_random_message,
    get_procedure_comment,
    get_streak_message,
    MENSAJES_BIENVENIDA,
    RESPUESTAS_TUTORIA,
    RESPUESTAS_MEDIA,
    RESPUESTAS_ALTA,
    FELICITACIONES_RACHA_5,
)


class TestGetRandomMessage:
    def test_returns_string_from_bank(self):
        """get_random_message retorna un string del banco recibido."""
        bank = ["Hola", "Mundo", "Test"]
        result = get_random_message(bank)
        assert isinstance(result, str)
        assert result in bank

    def test_works_with_single_item_bank(self):
        """Banco de un solo elemento → siempre retorna ese elemento."""
        result = get_random_message(["único"])
        assert result == "único"

    def test_bienvenida_bank_is_non_empty(self):
        """El banco de bienvenida no está vacío."""
        assert len(MENSAJES_BIENVENIDA) > 0

    def test_bienvenida_messages_are_strings(self):
        """Todos los mensajes de bienvenida son strings."""
        for msg in MENSAJES_BIENVENIDA:
            assert isinstance(msg, str), f"Mensaje no es string: {msg!r}"


class TestGetProcedureComment:
    def test_score_below_60_returns_tutoring_message(self):
        """Score < 60 → mensaje de tutoría (invita al chat socrático)."""
        result = get_procedure_comment(0)
        assert isinstance(result, str)
        assert result in RESPUESTAS_TUTORIA

        result = get_procedure_comment(59)
        assert result in RESPUESTAS_TUTORIA

    def test_score_60_to_90_returns_medium_message(self):
        """Score 60-90 → mensaje de buen trabajo."""
        result = get_procedure_comment(60)
        assert result in RESPUESTAS_MEDIA

        result = get_procedure_comment(90)
        assert result in RESPUESTAS_MEDIA

    def test_score_above_90_returns_excellent_message(self):
        """Score > 90 → mensaje de excelente."""
        result = get_procedure_comment(91)
        assert result in RESPUESTAS_ALTA

        result = get_procedure_comment(100)
        assert result in RESPUESTAS_ALTA

    def test_returns_string_for_all_valid_scores(self):
        """Retorna string para cualquier score en [0, 100]."""
        for score in [0, 30, 59, 60, 75, 90, 91, 100]:
            result = get_procedure_comment(score)
            assert isinstance(result, str), f"No es string para score={score}"


class TestGetStreakMessage:
    def test_streak_5_returns_message(self):
        """Racha de 5 → mensaje de felicitación."""
        result = get_streak_message(5)
        assert isinstance(result, str)
        assert result in FELICITACIONES_RACHA_5

    def test_streak_10_returns_message(self):
        """Racha de 10 → mensaje de racha 10."""
        result = get_streak_message(10)
        assert isinstance(result, str)

    def test_streak_20_returns_message(self):
        """Racha de 20 → mensaje de racha 20."""
        result = get_streak_message(20)
        assert isinstance(result, str)

    def test_unknown_streak_returns_empty_or_string(self):
        """Racha sin mensaje definido → retorna string (puede ser vacío)."""
        result = get_streak_message(7)
        assert isinstance(result, str)
