"""
tests/unit/application/test_student_service.py
===============================================
Pruebas unitarias de StudentService.
Usa repositorio mock — sin acceso a BD real.

API real:
  process_answer(user_id, item_data, selected_option, reasoning, time_taken,
                 request_id=None, request_fingerprint=None)
    → (is_correct: bool, result: dict)  — spec 001: the rating is the item's (course, topic)

  get_next_question(student_id, course_id, topic_filter=None,
                    session_correct_ids, session_wrong_timestamps,
                    session_questions_count, block)  — rating from the course × topic store
    → (item_data | None, status_str)
"""

import pytest
from unittest.mock import MagicMock
from src.application.services.student_service import StudentService
from src.domain.elo.vector_elo import VectorRating


@pytest.fixture
def service(mock_repository) -> StudentService:
    """StudentService con repositorio mock y cognitive modifier desactivado."""
    return StudentService(
        repository=mock_repository,
        ai_client=None,
    )


@pytest.fixture
def service_with_items(mock_repository_with_items) -> StudentService:
    """StudentService para simular estudiante con ítems disponibles."""
    return StudentService(
        repository=mock_repository_with_items,
        ai_client=None,
    )


class TestProcessAnswer:
    def test_correct_answer_returns_is_correct_true(self, service, medium_item, student_vector):
        """process_answer con opción correcta → is_correct=True."""
        is_correct, _ = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=15.0,
        )
        assert is_correct is True

    def test_wrong_answer_returns_is_correct_false(self, service, medium_item, student_vector):
        """process_answer con opción incorrecta → is_correct=False."""
        wrong_option = next(
            opt for opt in medium_item["options"] if opt != medium_item["correct_option"]
        )
        is_correct, _ = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=wrong_option,
            reasoning="",
            time_taken=20.0,
        )
        assert is_correct is False

    def test_correct_answer_increases_elo(self, service, medium_item, student_vector):
        """Acierto → ELO del tópico sube."""
        _, result = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=12.0,
        )
        assert result["elo_after"] > result["elo_before"]

    def test_wrong_answer_decreases_elo(self, service, medium_item, student_vector):
        """Fallo → ELO del tópico baja."""
        wrong = next(opt for opt in medium_item["options"] if opt != medium_item["correct_option"])
        _, result = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=wrong,
            reasoning="",
            time_taken=25.0,
        )
        assert result["elo_after"] < result["elo_before"]

    def test_save_answer_transaction_called_once(
        self, service, mock_repository, medium_item, student_vector
    ):
        """Se llama save_answer_transaction exactamente una vez por respuesta."""
        service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=10.0,
        )
        mock_repository.save_answer_transaction.assert_called_once()

    def test_cog_data_contains_expected_fields(self, service, medium_item, student_vector):
        """El resultado incluye los valores del intento (spec 001: sin impact_modifier)."""
        _, cog_data = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=15.0,
        )
        required_fields = {
            "confidence_score",
            "error_type",
            "elo_before",
            "elo_after",
            "rd_after",
            "elo_valid",
        }
        assert required_fields.issubset(
            cog_data.keys()
        ), f"Faltan campos en cog_data: {required_fields - cog_data.keys()}"


class TestGetNextQuestion:
    def test_preserves_selected_identity_when_difficulties_match(
        self, service, mock_repository, student_vector, monkeypatch
    ):
        first = {"id": "first", "difficulty": 1000}
        second = {"id": "second", "difficulty": 1000}
        mock_repository.get_items_from_db.return_value = [first, second]
        monkeypatch.setattr(
            "src.application.services.student_service.AdaptiveItemSelector.select_optimal_item",
            lambda self, rating, items: items[-1],
        )
        result, status = service.get_next_question(1, "algebra")
        assert status == "ok"
        assert result is second

    @pytest.mark.parametrize("blocked", ["historical", "correct", "cooldown"])
    def test_variety_preserves_unseen_priority_and_session_exclusions(
        self, service, mock_repository, student_vector, blocked
    ):
        mock_repository.get_items_from_db.return_value = [
            {"id": "blocked", "difficulty": 1000},
            {"id": "unseen", "difficulty": 1050},
        ]
        mock_repository.get_answered_item_ids.return_value = (
            ["blocked"] if blocked == "historical" else []
        )
        result, status = service.get_next_question(
            1,
            "algebra",
            session_correct_ids={"blocked"} if blocked == "correct" else set(),
            session_wrong_timestamps={"blocked": 1} if blocked == "cooldown" else {},
            session_questions_count=2,
        )
        assert status == "ok"
        assert result["id"] == "unseen"

    def test_returns_none_when_no_items(self, service, mock_repository, student_vector):
        """Sin ítems disponibles → retorna (None, status)."""
        mock_repository.get_items_from_db.return_value = []
        mock_repository.get_answered_item_ids.return_value = []
        result, status = service.get_next_question(
            student_id=1,
            course_id="algebra_basica",
        )
        assert result is None

    def test_returns_item_dict_from_pool(self, service_with_items, item_pool, student_vector):
        """Con ítems disponibles → retorna un dict del pool."""
        item, status = service_with_items.get_next_question(
            student_id=1,
            course_id="algebra_basica",
        )
        assert item is not None
        assert item["id"] in {i["id"] for i in item_pool}

    def test_returns_ok_status_when_item_found(self, service_with_items, student_vector):
        """Cuando hay ítems, el status es 'ok'."""
        _, status = service_with_items.get_next_question(
            student_id=1,
            course_id="algebra_basica",
        )
        assert status == "ok"


class TestTopicFilter:
    """Refuerzo desde el mapa: topic_filter restringe el pool a un tópico."""

    def test_topic_filter_restricts_to_topic(self, service_with_items, student_vector):
        """Con topic_filter='Álgebra' solo se sirven ítems de ese tópico."""
        item, status = service_with_items.get_next_question(
            student_id=1,
            course_id="algebra_basica",
            topic_filter="Álgebra",
        )
        assert item is not None
        assert item["topic"] == "Álgebra"

    def test_topic_filter_single_match(self, service_with_items, student_vector):
        """topic_filter='Derivadas' (un solo ítem) devuelve justo ese ítem."""
        item, _ = service_with_items.get_next_question(
            student_id=1,
            course_id="calculo_diferencial",
            topic_filter="Derivadas",
        )
        assert item is not None
        assert item["topic"] == "Derivadas"

    def test_unknown_topic_filter_falls_back_to_full_pool(self, service_with_items, student_vector):
        """Un tópico inexistente NO vacía el pool: cae al pool completo del curso."""
        item, status = service_with_items.get_next_question(
            student_id=1,
            course_id="algebra_basica",
            topic_filter="__no_existe__",
        )
        assert item is not None  # devuelve algo en vez de None
        assert status == "ok"
