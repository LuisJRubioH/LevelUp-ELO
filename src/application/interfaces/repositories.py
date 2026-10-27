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

    # ── Procedimientos (spec 001 bloque 7) ────────────────────────────────────
    def submit_procedure(
        self,
        student_id,
        item_id,
        item_content,
        image_data,
        mime_type,
        file_hash,
        classify: Callable,
        grade_copy: Callable,
    ) -> dict: ...

    # ── Catálogo y matrícula ──────────────────────────────────────────────────
    def get_education_level(self, user_id): ...
    def get_grade(self, user_id): ...
    def get_available_courses_by_level(self, level: str, grade=None) -> list: ...
    def get_available_groups_for_course(self, course_id) -> list: ...
    def enroll_user(self, user_id, course_id, group_id=None): ...
    def get_user_enrollments(self, user_id) -> list: ...  # ensure_enrolled (FR-037)
    def redeem_group_invitation(self, user_id, token) -> dict: ...  # spec 001 FR-028q
    def get_student_group(self, user_id) -> dict | None: ...  # spec 001 FR-028v
    def get_subtopic_attempts(self, user_id) -> list: ...

    # Spec 007 FR-070: the League's answers for study (StudyReportService)
    def get_league_answers(self, user_id) -> list: ...
    def get_teacher_league_answers(self, teacher_id, student_id=None) -> list: ...
    def get_item_by_id(self, item_id: str) -> dict | None: ...  # the most-missed statements


@runtime_checkable
class ITeacherRepository(Protocol):
    """Lo que TeacherService necesita del repositorio."""

    def get_students_by_teacher(self, teacher_id) -> list: ...
    def get_groups_by_teacher(self, teacher_id) -> list: ...
    def create_group(self, name, teacher_id, course_id=None, institution=None, grade=None): ...
    def get_student_attempts_detail(self, student_id) -> list: ...
    def get_procedure_stats_by_course(self, student_id): ...
    def validate_procedure_submission(
        self,
        submission_id: int,
        teacher_score: float,
        feedback: str = "",
        teacher_id: Optional[int] = None,
    ) -> bool: ...
    def grade_procedure_transaction(
        self,
        submission_id: int,
        grade: float,
        compute: Callable,
        feedback: str = "",
        teacher_id: Optional[int] = None,
        review_round: Optional[int] = None,
    ) -> Optional[dict]: ...


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
    def get_pvp_history(self, user_id: int, limit: int = 20, before: int | None = None) -> list: ...


@runtime_checkable
class IAdminRepository(Protocol):
    """Lo que necesita el panel de administración."""

    def get_pending_teachers(self) -> list: ...
    def approve_teacher(self, user_id): ...
    def deactivate_user(self, user_id): ...
    def get_problem_reports(self, status: Optional[str] = None) -> list: ...
    def mark_problem_resolved(self, report_id: int) -> None: ...

    # Spec 004 E2: administrative account operations, each recorded without the password.
    def get_accounts_admin(self) -> list: ...
    def reset_user_password(self, admin_id, user_id, temporary_password): ...
    def create_teacher_account(self, admin_id, username, temporary_password, email=None): ...
    def get_account_audit(self, limit=100) -> list: ...

    # Spec 004 E3: students created one by one (FR-040) and the last day of access (FR-050).
    def create_student_account(
        self,
        admin_id,
        username,
        temporary_password,
        display_name,
        group_id,
        education_level,
        grade=None,
        access_until=None,
    ): ...
    def set_access_until(self, admin_id, user_id, access_until): ...

    # Spec 009 I1: the initial import (FR-003 … FR-010), identifications (FR-007, FR-017), the
    # recovery e-mail (FR-018) and the groups the admin creates for a teacher (N25, N26 (a)).
    def get_import_lookups(self, identifications) -> dict: ...
    def start_import(self, admin_id, digest, total_rows): ...
    def import_student_chunk(self, import_id, rows): ...
    def record_import_rows(self, import_id, rows) -> bool: ...
    def finish_import(self, import_id, state="finished") -> bool: ...
    def get_confirmed_import(self, admin_id, digest): ...
    def get_import(self, import_id): ...
    def list_imports(self, admin_id, limit=50) -> list: ...
    def link_identification(self, admin_id, user_id, identification): ...
    def unlink_identification(self, admin_id, user_id): ...
    def set_recovery_email(self, admin_id, user_id, recovery_email): ...
    def create_group_for_teacher(
        self, admin_id, teacher_id, name, course_id=None, institution=None, grade=None
    ): ...


@runtime_checkable
class IAccountRepository(Protocol):
    """Spec 004 E2: the account's own credentials — password and security version."""

    def get_user_by_id(self, user_id: int): ...
    def verify_user_password(self, user_id, password) -> bool: ...
    def set_user_password(self, user_id, password, must_change=False): ...

    # FR-025: the student's own display name, or any student's by the admin; recorded.
    def set_display_name(self, actor_id, user_id, display_name): ...

    # FR-047: the last day of access of the accounts with an open connection.
    def get_access_until_bulk(self, user_ids) -> dict: ...

    # Spec 009 FR-013: the account's own identification, and whether the import created it.
    def get_student_identification(self, user_id) -> dict: ...


@runtime_checkable
class IRepository(
    IStudentRepository,
    ITeacherRepository,
    IRatingReadRepository,
    IAdminRepository,
    IAccountRepository,
    Protocol,
):
    """Un repositorio completo — lo que `RepoDep` inyecta en los routers.

    Es la unión de los tres roles, no el catálogo entero: los routers usan más
    métodos de los que aparecen aquí. Sirve para que `RepoDep` deje de estar
    tipado como `object` y para anclar el test de contratos.
    """
