"""
src/application/interfaces/repositories.py
===========================================
Protocolos de repositorio por rol de consumidor.

Principio Interface Segregation (ISP):
Cada servicio solo ve los métodos que necesita.
SQLiteRepository y PostgresRepository implementan todos los protocolos.

Uso:
    from src.application.interfaces.repositories import IStudentRepository
    class StudentService:
        def __init__(self, repository: IStudentRepository): ...
"""

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class IStudentRepository(Protocol):
    """Interfaz mínima que necesita StudentService."""

    def get_item(self, item_id: str) -> Optional[dict]: ...
    def get_available_items(self, user_id: int, course_id: str) -> list: ...
    def get_attempt_count(self, user_id: int) -> int: ...
    def get_latest_elo_by_topic(self, user_id: int) -> dict: ...
    def get_study_streak(self, user_id: int, course_id: Optional[str] = None) -> int: ...
    def save_answer_transaction(
        self,
        user_id: int,
        item_id: str,
        item_difficulty_new: float,
        item_rd_new: float,
        attempt_data: dict,
    ) -> None: ...
    def save_katia_interaction(
        self,
        user_id: int,
        course_id: str,
        item_id: str,
        item_topic: str,
        student_message: str,
        katia_response: Optional[str] = None,
    ) -> None: ...


@runtime_checkable
class ITeacherRepository(Protocol):
    """Interfaz mínima que necesita TeacherService y el panel docente."""

    def get_teacher_groups(self, teacher_id: int) -> list: ...
    def get_group_students(self, group_id: int) -> list: ...
    def get_student_attempts(self, student_id: int, limit: int = 100) -> list: ...
    def get_student_procedure_scores(self, student_id: int) -> list: ...
    def save_procedure_score(
        self,
        submission_id: int,
        teacher_score: float,
        teacher_comment: Optional[str] = None,
    ) -> None: ...
    def export_teacher_student_data(
        self, teacher_id: int, group_id: Optional[int] = None
    ) -> list: ...
    def export_teacher_katia_interactions(
        self, teacher_id: int, group_id: Optional[int] = None
    ) -> list: ...


@runtime_checkable
class IAdminRepository(Protocol):
    """Interfaz mínima que necesita el panel de administración."""

    def get_pending_teachers(self) -> list: ...
    def approve_teacher(self, user_id: int) -> None: ...
    def deactivate_user(self, user_id: int) -> None: ...
    def activate_user(self, user_id: int) -> None: ...
    def get_problem_reports(self, status: Optional[str] = None) -> list: ...
    def mark_problem_resolved(self, report_id: int) -> None: ...
