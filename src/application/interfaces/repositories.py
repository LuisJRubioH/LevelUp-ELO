"""
src/application/interfaces/repositories.py
===========================================
Protocolos de repositorio por rol de consumidor.

Principio Interface Segregation (ISP): cada servicio solo ve los métodos que
necesita. `SQLiteRepository` y `PostgresRepository` implementan todos.

**Estos protocolos describen lo que los servicios llaman de verdad.** Antes
declaraban métodos que no existían (`get_item`, `get_available_items`,
`get_teacher_groups`, `get_group_students`, `get_student_attempts`,
`save_procedure_score`) y omitían los que sí se usan, así que no daban ninguna
garantía: eran decoración. `tests/unit/application/test_repository_contracts.py`
compara cada método con los dos repositorios y falla si vuelven a divergir.

Al añadir una llamada nueva a `self.repository.<algo>` en un servicio, hay que
declararla aquí — el test lo exige.
"""

from typing import Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class IStudentRepository(Protocol):
    """Lo que StudentService necesita del repositorio."""

    # ── Selección de ítems ────────────────────────────────────────────────────
    def get_items_from_db(self, topic=None, course_id=None, block=None) -> list: ...
    def get_answered_item_ids(self, user_id) -> list: ...

    # ── Respuestas ────────────────────────────────────────────────────────────
    def save_answer_transaction(
        self,
        user_id: int,
        item_id: str,
        compute: Callable[[dict], tuple],
        request_id: Optional[str] = None,
        request_fingerprint: Optional[str] = None,
    ) -> bool: ...

    # ── Catálogo y matrícula ──────────────────────────────────────────────────
    def get_education_level(self, user_id): ...
    def get_grade(self, user_id): ...
    def get_available_courses_by_level(self, level: str, grade=None) -> list: ...
    def get_available_groups_for_course(self, course_id) -> list: ...
    def enroll_user(self, user_id, course_id, group_id=None): ...
    def get_user_enrollments(self, user_id) -> list: ...  # ensure_enrolled (FR-037)


@runtime_checkable
class ITeacherRepository(Protocol):
    """Lo que TeacherService necesita del repositorio."""

    def get_students_by_teacher(self, teacher_id) -> list: ...
    def get_groups_by_teacher(self, teacher_id) -> list: ...
    def create_group(self, name, teacher_id, course_id=None): ...
    def get_student_attempts_detail(self, student_id) -> list: ...
    def get_procedure_stats_by_course(self, student_id): ...
    def validate_procedure_submission(
        self,
        submission_id: int,
        teacher_score: float,
        feedback: str = "",
        teacher_id: Optional[int] = None,
    ) -> bool: ...


@runtime_checkable
class IRatingReadRepository(Protocol):
    """Lo que RatingReadService necesita (spec 001): filas crudas y participantes.

    Ninguno de estos métodos promedia, redondea u ordena por rating (constitución III).
    """

    def get_course_topic_ratings(self, user_id, course_id=None) -> list: ...
    def get_course_topic_ratings_bulk(self, user_ids, course_id=None) -> list: ...
    def get_current_context_course_ids(self, user_id) -> list: ...
    def get_current_context_course_ids_bulk(self, user_ids) -> dict: ...
    def get_ranking_participants(
        self,
        scope,
        group_id=None,
        course_id=None,
        education_level=None,
        grade=None,
        window_days=7,
    ) -> list: ...
    def get_group_course_id(self, group_id): ...
    def get_courses(self, block=None) -> list: ...
    def get_user_enrollments(self, user_id) -> list: ...


@runtime_checkable
class IAdminRepository(Protocol):
    """Lo que necesita el panel de administración."""

    def get_pending_teachers(self) -> list: ...
    def approve_teacher(self, user_id): ...
    def deactivate_user(self, user_id): ...
    def get_problem_reports(self, status: Optional[str] = None) -> list: ...
    def mark_problem_resolved(self, report_id: int) -> None: ...


@runtime_checkable
class IRepository(
    IStudentRepository, ITeacherRepository, IRatingReadRepository, IAdminRepository, Protocol
):
    """Un repositorio completo — lo que `RepoDep` inyecta en los routers.

    Es la unión de los tres roles, no el catálogo entero: los routers usan más
    métodos de los que aparecen aquí. Sirve para que `RepoDep` deje de estar
    tipado como `object` y para anclar el test de contratos.
    """
