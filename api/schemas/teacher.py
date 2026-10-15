"""
api/schemas/teacher.py
======================
Pydantic schemas para los endpoints del docente y admin.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

from src.domain.invitations import MAX_INVITATIONS_PER_REQUEST


# ── Grupos ────────────────────────────────────────────────────────────────────


class CreateGroupRequest(BaseModel):
    course_id: str
    group_name: str = Field(..., min_length=1, max_length=80)


class GroupResponse(BaseModel):
    # No reusable invitation code: groups are joined with single-use invitations (spec 001
    # FR-028u).
    group_id: int
    name: str
    course_id: str | None
    student_count: int = 0


# ── Invitaciones de un solo uso (spec 001, delivery INV) ──────────────────────


class CreateInvitationsRequest(BaseModel):
    count: int = Field(1, ge=1, le=MAX_INVITATIONS_PER_REQUEST)


class CreatedInvitationsResponse(BaseModel):
    tokens: list[str]  # XXXXX-XXXXX
    ttl_days: int


class InvitationView(BaseModel):
    id: int
    token: str  # XXXXX-XXXXX
    status: str  # unused | used | expired | revoked (FR-028t)
    created_at: str
    expires_at: str
    used_at: str | None = None
    used_by_name: str | None = None  # the student's public name (spec 004 FR-023)


class InvitationsResponse(BaseModel):
    ttl_days: int
    invitations: list[InvitationView]


# ── Dashboard ─────────────────────────────────────────────────────────────────


class StudentSummary(BaseModel):
    user_id: int
    username: str
    global_elo: float
    total_attempts: int
    accuracy: float  # 0.0–1.0
    last_activity: str | None


class StudentAIAnalysisRequest(BaseModel):
    api_key: str = ""
    provider: str = "groq"
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
    # Spec 004 FR-023: the display name, else the username (N5).
    student_name: str
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


class ExamAssignmentCreateRequest(BaseModel):
    """Asigna una plantilla a uno o varios grupos con ventana de tiempo opcional."""

    group_ids: list[int] = Field(..., min_length=1, max_length=50)
    starts_at: datetime | None = Field(
        default=None,
        description="ISO 8601; sin zona = UTC. None = abierto desde ya.",
    )
    ends_at: datetime | None = Field(
        default=None,
        description="ISO 8601; sin zona = UTC. None = sin fecha de cierre.",
    )

    @model_validator(mode="after")
    def _ends_after_it_starts(self):
        if self.starts_at and self.ends_at and _utc(self.ends_at) <= _utc(self.starts_at):
            raise ValueError("La fecha de cierre debe ser posterior a la de apertura.")
        return self


def _utc(value: datetime) -> datetime:
    """A time with no zone is UTC."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class ExamAssignmentResponse(BaseModel):
    id: int
    template_id: int
    group_id: int
    group_name: str
    starts_at: str | None
    ends_at: str | None
    created_at: str


class ItemCatalogEntry(BaseModel):
    """Resumen de item para que el docente lo seleccione al armar el examen."""

    id: str
    content: str
    difficulty: float
    topic: str
    tags: list[str] = []
