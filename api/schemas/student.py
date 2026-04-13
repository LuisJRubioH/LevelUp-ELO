"""
api/schemas/student.py
======================
Pydantic schemas para los endpoints del estudiante.
"""

from pydantic import BaseModel, Field


# ── Preguntas ─────────────────────────────────────────────────────────────────


class NextQuestionRequest(BaseModel):
    course_id: str = Field(..., description="Curso activo del estudiante")
    topic: str | None = Field(default=None, description="Tópico específico (opcional)")
    session_correct_ids: list[str] = Field(
        default_factory=list,
        description="IDs de ítems respondidos correctamente en esta sesión",
    )
    session_wrong_timestamps: dict[str, int] = Field(
        default_factory=dict,
        description="item_id → pregunta_num en que fue fallada en sesión",
    )
    session_questions_count: int = Field(default=0, ge=0)


class ItemResponse(BaseModel):
    id: str
    content: str
    difficulty: float
    topic: str
    options: list[str]
    image_url: str | None = None
    tags: list[str] = []


class NextQuestionResponse(BaseModel):
    item: ItemResponse | None
    status: str  # "ok", "empty", "course_empty"


# ── Respuestas ────────────────────────────────────────────────────────────────


class AnswerRequest(BaseModel):
    item_id: str = Field(..., description="ID del ítem respondido")
    item_data: dict = Field(..., description="Datos completos del ítem (desde /next-question)")
    selected_option: str = Field(..., description="Opción elegida por el estudiante")
    reasoning: str | None = Field(
        default="", description="Razonamiento del estudiante (para KatIA)"
    )
    time_taken: float | None = Field(default=None, ge=0, description="Segundos en responder")
    elo_topic: str | None = Field(
        default=None,
        description="Clave ELO del VectorRating (si difiere del topic del ítem)",
    )


class AnswerResponse(BaseModel):
    is_correct: bool
    correct_option: str
    elo_before: float
    elo_after: float
    rd_after: float
    delta_elo: float
    cog_data: dict


# ── Stats y ELO ──────────────────────────────────────────────────────────────


class TopicELO(BaseModel):
    topic: str
    rating: float
    rd: float


class StudentStatsResponse(BaseModel):
    user_id: int
    global_elo: float
    topic_elos: list[TopicELO]
    total_attempts: int
    study_streak: int
    rank_label: str | None = None


# ── Cursos y matrículas ───────────────────────────────────────────────────────


class CourseResponse(BaseModel):
    id: str
    name: str
    block: str
    enrolled: bool
    group_id: int | None = None


class EnrollRequest(BaseModel):
    course_id: str
    group_id: int | None = None


class EnrollByCodeRequest(BaseModel):
    invite_code: str


# ── Procedimientos ────────────────────────────────────────────────────────────


class ProcedureSubmitResponse(BaseModel):
    submission_id: int
    ai_score: float | None
    ai_feedback: str | None
    status: str


# ── Modo Examen ───────────────────────────────────────────────────────────────


class ExamStartRequest(BaseModel):
    course_id: str = Field(..., description="Curso para el examen")
    n_questions: int = Field(default=10, ge=1, le=30, description="Número de preguntas (máx 30)")
    time_limit_minutes: int = Field(
        default=20, ge=5, le=180, description="Minutos disponibles para el examen"
    )


class ExamStartResponse(BaseModel):
    items: list[ItemResponse]
    n_questions: int
    time_limit_seconds: int
    course_id: str


class ExamAnswerItem(BaseModel):
    item_id: str
    selected_option: str
    time_taken: float | None = None


class ExamSubmitRequest(BaseModel):
    answers: list[ExamAnswerItem] = Field(..., description="Respuestas del estudiante")
    total_time_taken: float | None = Field(None, description="Tiempo total en segundos")


class ExamSubmitResponse(BaseModel):
    results: list[dict]
    correct_count: int
    total_questions: int
    score_pct: float
    global_elo_after: float


# ── Socrático ─────────────────────────────────────────────────────────────────


class SocraticRequest(BaseModel):
    item_id: str
    item_content: str
    student_message: str = Field(..., min_length=1, max_length=1000)
    course_id: str | None = None
    api_key: str = Field(..., description="API key del proveedor de IA (solo viaja en el body)")
    provider: str = Field(default="groq", description="Proveedor: groq, anthropic, openai, etc.")
