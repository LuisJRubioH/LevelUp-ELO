"""
tests/conftest.py
==================
Fixtures compartidos para toda la suite de pruebas.
Disponibles automáticamente en todos los tests sin importar.
"""
import pytest
from unittest.mock import MagicMock

from src.domain.elo.vector_elo import VectorRating
from src.domain.elo.uncertainty import RatingModel
from src.domain.elo.model import Item


# ── Fixtures de dominio ──────────────────────────────────────────────────────

@pytest.fixture
def student_vector() -> VectorRating:
    """VectorRating con rating inicial 1000 y RD 350 (estudiante nuevo, defaults)."""
    return VectorRating()


@pytest.fixture
def experienced_vector() -> VectorRating:
    """VectorRating con ELO alto y baja incertidumbre (estudiante experimentado).
    Se consigue haciendo varias actualizaciones sobre el mismo tópico.
    """
    v = VectorRating()
    # Simular un estudiante que ha respondido muchas preguntas → RD baja
    for _ in range(30):
        v.update("Álgebra", 1200.0, 1.0, 1.0)
    return v


@pytest.fixture
def rating_model() -> RatingModel:
    """RatingModel estándar."""
    return RatingModel()


@pytest.fixture
def easy_item() -> dict:
    """Ítem fácil (dificultad 600) para probar respuestas de estudiante avanzado."""
    return {
        "id": "easy_01",
        "content": "¿Cuánto es 2 + 2?",
        "difficulty": 600.0,
        "rating_deviation": 200.0,
        "topic": "Aritmética Básica",
        "options": ["3", "4", "5", "6"],
        "correct_option": "4",
        "course_id": "aritmetica_basica",
    }


@pytest.fixture
def medium_item() -> dict:
    """Ítem medio (dificultad 1000) para estudiante típico."""
    return {
        "id": "medium_01",
        "content": "¿Cuál es la derivada de $\\sin(x)$?",
        "difficulty": 1000.0,
        "rating_deviation": 200.0,
        "topic": "Derivadas",
        "options": ["$\\cos(x)$", "$-\\cos(x)$", "$\\sin(x)$", "$-\\sin(x)$"],
        "correct_option": "$\\cos(x)$",
        "course_id": "calculo_diferencial",
    }


@pytest.fixture
def hard_item() -> dict:
    """Ítem difícil (dificultad 1600) para probar estudiante avanzado."""
    return {
        "id": "hard_01",
        "content": "Calcula $\\int_0^\\pi \\sin(x) dx$",
        "difficulty": 1600.0,
        "rating_deviation": 200.0,
        "topic": "Integrales definidas",
        "options": ["$0$", "$2$", "$\\pi$", "$1$"],
        "correct_option": "$2$",
        "course_id": "calculo_integral",
    }


@pytest.fixture
def item_pool(easy_item, medium_item, hard_item) -> list:
    """Pool de 10 ítems con dificultades variadas para pruebas del selector."""
    items = [easy_item, medium_item, hard_item]
    for i in range(7):
        items.append({
            "id": f"pool_{i:02d}",
            "content": f"Pregunta {i}",
            "difficulty": 700.0 + i * 120,
            "rating_deviation": 200.0,
            "topic": "Álgebra",
            "options": ["A", "B", "C", "D"],
            "correct_option": "A",
            "course_id": "algebra_basica",
        })
    return items


@pytest.fixture
def item_pool_objs(item_pool) -> list:
    """Pool de ítems como objetos Item (para AdaptiveItemSelector)."""
    return [Item(difficulty=i["difficulty"]) for i in item_pool]


# ── Fixtures de infraestructura ──────────────────────────────────────────────

@pytest.fixture
def mock_repository() -> MagicMock:
    """
    Repositorio mock para pruebas unitarias de servicios.
    Preconfigura retornos por defecto para los métodos usados por StudentService.
    """
    repo = MagicMock()
    repo.get_items_from_db.return_value = []
    repo.get_answered_item_ids.return_value = []
    repo.save_answer_transaction.return_value = None
    repo.get_study_streak.return_value = 0
    repo.save_katia_interaction.return_value = None
    return repo


@pytest.fixture
def mock_repository_with_items(mock_repository, item_pool) -> MagicMock:
    """Repositorio mock con ítems disponibles (dicts, como devuelve la DB)."""
    mock_repository.get_items_from_db.return_value = item_pool
    mock_repository.get_answered_item_ids.return_value = []
    return mock_repository


@pytest.fixture
def mock_ai_unavailable() -> MagicMock:
    """Simula IA no disponible — todos los métodos lanzan ConnectionError."""
    client = MagicMock()
    client.get_socratic_guidance.side_effect = ConnectionError("IA no disponible")
    client.analyze_performance_local.side_effect = ConnectionError("IA no disponible")
    return client
