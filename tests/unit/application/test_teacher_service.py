"""
tests/unit/application/test_teacher_service.py
===============================================
Pruebas unitarias de TeacherService.
Usa repositorio mock — sin acceso a BD real ni IA real.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.application.services.teacher_service import TeacherService


@pytest.fixture
def repo() -> MagicMock:
    """Repositorio mock con respuestas por defecto."""
    r = MagicMock()
    r.get_students_by_teacher.return_value = []
    r.get_groups_by_teacher.return_value = []
    r.get_student_attempts_detail.return_value = []
    r.get_student_elo_summary.return_value = {}
    r.get_procedure_stats_by_course.return_value = {}
    r.create_group.return_value = (True, "Grupo creado exitosamente.")
    r.get_latest_elo_by_topic.return_value = {}
    return r


@pytest.fixture
def service(repo) -> TeacherService:
    return TeacherService(repository=repo)


class TestGetDashboardData:
    def test_returns_students_and_groups(self, service, repo):
        """get_dashboard_data retorna (students, groups)."""
        repo.get_students_by_teacher.return_value = [{"id": 1, "username": "s1"}]
        repo.get_groups_by_teacher.return_value = [{"id": 10, "name": "Grupo A"}]
        students, groups = service.get_dashboard_data(teacher_id=5)
        assert len(students) == 1
        assert len(groups) == 1

    def test_calls_repo_with_correct_teacher_id(self, service, repo):
        """Se llama al repositorio con el teacher_id correcto."""
        service.get_dashboard_data(teacher_id=42)
        repo.get_students_by_teacher.assert_called_once_with(42)
        repo.get_groups_by_teacher.assert_called_once_with(42)


class TestCreateNewGroup:
    def test_empty_name_returns_error(self, service):
        """Nombre vacío → False con mensaje de error."""
        ok, msg = service.create_new_group(teacher_id=1, course_id="algebra", group_name="")
        assert ok is False
        assert "vacío" in msg

    def test_whitespace_name_returns_error(self, service):
        """Nombre de solo espacios → False."""
        ok, msg = service.create_new_group(teacher_id=1, course_id="algebra", group_name="   ")
        assert ok is False

    def test_missing_course_returns_error(self, service):
        """Sin course_id → False con mensaje."""
        ok, msg = service.create_new_group(teacher_id=1, course_id="", group_name="Grupo A")
        assert ok is False
        assert "curso" in msg.lower()

    def test_valid_group_delegates_to_repo(self, service, repo):
        """Datos válidos → delega al repositorio."""
        service.create_new_group(teacher_id=1, course_id="algebra", group_name="Grupo A")
        repo.create_group.assert_called_once_with("Grupo A", 1, "algebra")

    def test_valid_group_returns_repo_result(self, service, repo):
        """El resultado es el devuelto por el repositorio."""
        repo.create_group.return_value = (True, "OK")
        ok, msg = service.create_new_group(teacher_id=1, course_id="algebra", group_name="G1")
        assert ok is True
        assert msg == "OK"

    def test_group_name_is_stripped(self, service, repo):
        """Los espacios al inicio/fin del nombre se eliminan antes de crear."""
        service.create_new_group(teacher_id=1, course_id="algebra", group_name="  G1  ")
        repo.create_group.assert_called_once_with("G1", 1, "algebra")


class TestValidateProcedure:
    def test_valid_score_calls_repo(self, service, repo):
        """Score en [0, 100] → llama a validate_procedure_submission."""
        service.validate_procedure(submission_id=5, teacher_score=85.0, feedback="Bien")
        repo.validate_procedure_submission.assert_called_once_with(5, 85.0, "Bien")

    def test_score_below_zero_raises_value_error(self, service):
        """Score < 0 → ValueError."""
        with pytest.raises(ValueError):
            service.validate_procedure(submission_id=1, teacher_score=-1.0)

    def test_score_above_100_raises_value_error(self, service):
        """Score > 100 → ValueError."""
        with pytest.raises(ValueError):
            service.validate_procedure(submission_id=1, teacher_score=101.0)

    def test_boundary_values_are_valid(self, service, repo):
        """Scores 0.0 y 100.0 son límites válidos (no deben lanzar excepción)."""
        service.validate_procedure(submission_id=1, teacher_score=0.0)
        service.validate_procedure(submission_id=2, teacher_score=100.0)
        assert repo.validate_procedure_submission.call_count == 2


class TestGenerateAiAnalysis:
    def test_returns_message_when_fewer_than_3_attempts(self, service, repo):
        """Con menos de 3 intentos → retorna mensaje informativo (sin llamar IA)."""
        repo.get_student_attempts_detail.return_value = [{"is_correct": True, "topic": "Álgebra"}]
        result = service.generate_ai_analysis(student_id=1, global_elo=1100)
        assert "3 ejercicios" in result or "3" in result

    def test_calls_repo_for_attempts(self, service, repo):
        """Siempre consulta los intentos del estudiante."""
        service.generate_ai_analysis(student_id=7, global_elo=1000)
        repo.get_student_attempts_detail.assert_called_once_with(7)

    def test_with_enough_attempts_calls_ai(self, service, repo):
        """Con ≥3 intentos → llama a get_pedagogical_analysis (mockeada)."""
        repo.get_student_attempts_detail.return_value = [
            {"is_correct": True, "topic": "Álgebra", "time_taken": 10.0},
            {"is_correct": False, "topic": "Cálculo", "time_taken": 15.0},
            {"is_correct": True, "topic": "Álgebra", "time_taken": 8.0},
        ]
        repo.get_latest_elo_by_topic.return_value = {}
        with patch(
            "src.application.services.teacher_service.get_pedagogical_analysis",
            return_value="Análisis generado",
        ) as mock_ai:
            result = service.generate_ai_analysis(student_id=1, global_elo=1200, api_key="test_key")
        mock_ai.assert_called_once()
        assert result == "Análisis generado"
