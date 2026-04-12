"""
tests/unit/application/test_student_service.py
===============================================
Pruebas unitarias de StudentService.
Usa repositorio mock — sin acceso a BD real.

API real:
  process_answer(user_id, item_data, selected_option, reasoning, time_taken,
                 vector_rating, elo_topic=None)
    → (is_correct: bool, cog_data: dict)

  get_next_question(student_id, topic, vector_rating,
                    session_correct_ids, session_wrong_timestamps,
                    session_questions_count, course_id)
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
        enable_cognitive_modifier=False,
    )


@pytest.fixture
def service_with_items(mock_repository_with_items) -> StudentService:
    """StudentService para simular estudiante con ítems disponibles."""
    return StudentService(
        repository=mock_repository_with_items,
        ai_client=None,
        enable_cognitive_modifier=False,
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
            vector_rating=student_vector,
            elo_topic="calculo_diferencial",
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
            vector_rating=student_vector,
            elo_topic="calculo_diferencial",
        )
        assert is_correct is False

    def test_correct_answer_increases_elo(self, service, medium_item, student_vector):
        """Acierto → ELO del tópico sube."""
        elo_before = student_vector.get("calculo_diferencial")
        service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=12.0,
            vector_rating=student_vector,
            elo_topic="calculo_diferencial",
        )
        assert student_vector.get("calculo_diferencial") > elo_before

    def test_wrong_answer_decreases_elo(self, service, medium_item, student_vector):
        """Fallo → ELO del tópico baja."""
        wrong = next(opt for opt in medium_item["options"] if opt != medium_item["correct_option"])
        elo_before = student_vector.get("calculo_diferencial")
        service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=wrong,
            reasoning="",
            time_taken=25.0,
            vector_rating=student_vector,
            elo_topic="calculo_diferencial",
        )
        assert student_vector.get("calculo_diferencial") < elo_before

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
            vector_rating=student_vector,
            elo_topic="calculo_diferencial",
        )
        mock_repository.save_answer_transaction.assert_called_once()

    def test_cognitive_modifier_is_1_when_disabled(self, service, medium_item, student_vector):
        """Con enable_cognitive_modifier=False, impact_modifier=1.0 siempre."""
        _, cog_data = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="Porque aprendí bien",
            time_taken=8.0,
            vector_rating=student_vector,
            elo_topic="calculo_diferencial",
        )
        assert cog_data.get("impact_modifier", 1.0) == 1.0

    def test_cog_data_contains_expected_fields(self, service, medium_item, student_vector):
        """El cog_data retornado incluye confidence_score, error_type, impact_modifier."""
        _, cog_data = service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=15.0,
            vector_rating=student_vector,
        )
        required_fields = {"confidence_score", "error_type", "impact_modifier"}
        assert required_fields.issubset(
            cog_data.keys()
        ), f"Faltan campos en cog_data: {required_fields - cog_data.keys()}"

    def test_elo_topic_overrides_item_topic(self, service, medium_item, student_vector):
        """elo_topic='curso_id' consolida el ELO en esa clave, no en item['topic']."""
        service.process_answer(
            user_id=1,
            item_data=medium_item,
            selected_option=medium_item["correct_option"],
            reasoning="",
            time_taken=10.0,
            vector_rating=student_vector,
            elo_topic="mi_curso",
        )
        # 'mi_curso' debe haberse actualizado
        assert student_vector.get("mi_curso") != 1000.0
        # El tópico del ítem NO debe haberse actualizado
        assert student_vector.get(medium_item["topic"]) == 1000.0


class TestGetNextQuestion:
    def test_returns_none_when_no_items(self, service, mock_repository, student_vector):
        """Sin ítems disponibles → retorna (None, status)."""
        mock_repository.get_items_from_db.return_value = []
        mock_repository.get_answered_item_ids.return_value = []
        result, status = service.get_next_question(
            student_id=1,
            topic="Álgebra",
            vector_rating=student_vector,
            course_id="algebra_basica",
        )
        assert result is None

    def test_returns_item_dict_from_pool(self, service_with_items, item_pool, student_vector):
        """Con ítems disponibles → retorna un dict del pool."""
        item, status = service_with_items.get_next_question(
            student_id=1,
            topic="Álgebra",
            vector_rating=student_vector,
            course_id="algebra_basica",
        )
        assert item is not None
        assert item["id"] in {i["id"] for i in item_pool}

    def test_returns_ok_status_when_item_found(self, service_with_items, student_vector):
        """Cuando hay ítems, el status es 'ok'."""
        _, status = service_with_items.get_next_question(
            student_id=1,
            topic="Álgebra",
            vector_rating=student_vector,
            course_id="algebra_basica",
        )
        assert status == "ok"
