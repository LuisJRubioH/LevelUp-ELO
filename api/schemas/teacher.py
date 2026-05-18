"""
api/schemas/teacher.py
======================
Pydantic schemas para los endpoints del docente y admin.
"""

from pydantic import BaseModel, Field


# ── Grupos ────────────────────────────────────────────────────────────────────


class CreateGroupRequest(BaseModel):
    course_id: str
    group_name: str = Field(..., min_length=1, max_length=80)


class GroupResponse(BaseModel):
    group_id: int
    name: str
    course_id: str | None
    invite_code: str | None
    student_count: int = 0


# ── Dashboard ─────────────────────────────────────────────────────────────────


class StudentSummary(BaseModel):
    user_id: int
    username: str
    global_elo: float
    total_attempts: int
    accuracy: float  # 0.0–1.0
    last_activity: str | None
    # Campos para filtros cascada (opcionales para compatibilidad)
    group_id: int | None = None
    group_name: str | None = None
    education_level: str | None = None


class DashboardResponse(BaseModel):
    teacher_id: int
    groups: list[GroupResponse]
    students: list[StudentSummary]


# ── Procedimientos ────────────────────────────────────────────────────────────


class GradeRequest(BaseModel):
    submission_id: int
    teacher_score: float = Field(..., ge=0, le=100)
    teacher_feedback: str | None = None


class GradeResponse(BaseModel):
    submission_id: int
    teacher_score: float
    elo_delta: float
    status: str


class PendingProcedure(BaseModel):
    submission_id: int
    student_id: int
    student_username: str
    item_id: str
    item_content: str | None
    ai_score: float | None
    status: str
    created_at: str
    has_image: bool = False  # True si hay imagen disponible para ver


# ── Reporte por estudiante ────────────────────────────────────────────────────


class StudentReportResponse(BaseModel):
    user_id: int
    username: str
    global_elo: float
    topic_breakdown: dict  # topic → {rating, rd, attempts}
    recent_attempts: list[dict]
    procedure_history: list[dict]


# ── Admin ─────────────────────────────────────────────────────────────────────


class UserAdminRow(BaseModel):
    user_id: int
    username: str
    role: str
    approved: bool
    active: bool
    education_level: str | None
    group_name: str | None


class ApproveTeacherRequest(BaseModel):
    user_id: int
    action: str = Field(..., pattern="^(approve|reject)$")


class ChangeGroupRequest(BaseModel):
    student_id: int
    new_group_id: int | None


# ── Sprint C: Plantillas de examen del docente ───────────────────────────────


class ExamTemplateCreateRequest(BaseModel):
    course_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=140)
    time_limit_min: int = Field(default=20, ge=5, le=180)
    item_ids: list[str] = Field(..., min_length=1, max_length=60)


class ExamTemplatePatchRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=140)
    time_limit_min: int | None = Field(default=None, ge=5, le=180)
    item_ids: list[str] | None = Field(default=None, min_length=1, max_length=60)


class ExamTemplateResponse(BaseModel):
    id: int
    teacher_id: int
    course_id: str
    title: str
    time_limit_min: int
    item_ids: list[str]
    archived: bool
    created_at: str


class ItemCatalogEntry(BaseModel):
    """Resumen de item para que el docente lo seleccione al armar el examen."""

    id: str
    content: str
    difficulty: float
    topic: str
    tags: list[str] = []
