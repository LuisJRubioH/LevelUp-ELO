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
    block: str | None = Field(default=None, description="Bloque temático (DIAN/SENA)")
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


class AnswerPreview(BaseModel):
    """The change the engine will apply to the item's topic rating (FR-030)."""

    on_correct: float
    on_wrong: float


class NextQuestionResponse(BaseModel):
    item: ItemResponse | None
    status: str  # "ok", "empty", "course_empty"
    preview: AnswerPreview | None = None


# ── Respuestas ────────────────────────────────────────────────────────────────


class AnswerRequest(BaseModel):
    item_id: str = Field(..., description="ID del ítem respondido")
    item_data: dict | None = Field(
        default=None,
        description="Compatibilidad con clientes anteriores; el servidor ignora estos datos.",
        deprecated=True,
    )
    selected_option: str = Field(..., description="Opción elegida por el estudiante")
    reasoning: str | None = Field(
        default="", description="Razonamiento del estudiante (para KatIA)"
    )
    time_taken: float | None = Field(
        default=None,
        ge=0,
        description="Segundos en responder. Ausente = 30 s; un 0 explícito es inválido (FR-008a).",
    )
    elo_topic: str | None = Field(
        default=None,
        description="Ignorado: el rating es siempre el (curso, tópico) del ítem (spec 001).",
        deprecated=True,
    )


class AnswerResponse(BaseModel):
    is_correct: bool
    elo_before: float
    elo_after: float
    rd_after: float
    delta_elo: float
    elo_valid: bool  # whether this attempt moved any rating (FR-008, FR-008a, FR-009)
    cog_data: dict


# ── Stats y ELO ──────────────────────────────────────────────────────────────


class TopicELO(BaseModel):
    topic: str
    rating: float
    rd: float
    approximate: bool = False  # True = a reconciled baseline, not exact history (FR-034a)
    origin: str | None = None


class CourseRatingView(BaseModel):
    """One course of the student (spec 001): derived rating, shown value and label (FR-028j)."""

    course_id: str
    course_name: str
    rating: float | None
    display_rating: int | None
    rank_label: str | None
    current_context: bool  # False = an earlier level/grade, shown as history (FR-028c)
    topics: list[TopicELO]


class StudentStatsResponse(BaseModel):
    user_id: int
    global_elo: float | None  # None while the diagnostic is pending (FR-028b)
    display_rating: int | None = None  # what screens show next to rank_label (FR-028j)
    overall_status: str = "rated"  # "rated" | "pending_diagnostic"
    topic_elos: list[TopicELO]
    course_ratings: list[CourseRatingView] = []
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
    diagnostic_done: bool = False


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
    template_id: int | None = Field(
        default=None,
        description=(
            "ID de plantilla de examen creada por el docente. Si se proporciona, "
            "se usa esa lista de items y se ignoran n_questions y time_limit_minutes. "
            "Si es None, se genera un examen estándar con curva de dificultad."
        ),
    )


class ExamTemplateSummary(BaseModel):
    """Resumen visible al estudiante: solo título + nº de preguntas + tiempo."""

    id: int
    title: str
    course_id: str
    n_questions: int
    time_limit_min: int
    created_at: str
    window_ends_at: str | None = None  # si la asignación tiene ends_at, lo expone


class PendingExam(BaseModel):
    """Resumen para el badge de notificación en el sidebar."""

    template_id: int
    title: str
    course_id: str
    course_name: str
    time_limit_min: int


class ExamStartResponse(BaseModel):
    session_id: str
    items: list[ItemResponse]
    n_questions: int
    time_limit_seconds: int
    course_id: str


class ExamAnswerItem(BaseModel):
    item_id: str
    selected_option: str
    time_taken: float | None = None


class ExamSubmitRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    answers: list[ExamAnswerItem] = Field(..., description="Respuestas del estudiante")
    total_time_taken: float | None = Field(None, description="Tiempo total en segundos")
    course_id: str = Field(default="", description="ID del curso examinado")
    course_name: str = Field(default="", description="Nombre del curso examinado")
    template_id: int | None = Field(
        default=None, description="Plantilla del docente (para análisis de resultados)"
    )


class ExamSubmitResponse(BaseModel):
    results: list[dict]
    correct_count: int
    total_questions: int
    score_pct: float
    global_elo_after: float | None  # overall rating at submission; None while pending


# ── Examen diagnóstico (inicio de materia) ────────────────────────────────────


class DiagnosticQuestion(BaseModel):
    id: str
    content: str
    topic: str | None = None
    difficulty: int = 1000
    options: list[str] = Field(default_factory=list)


class DiagnosticStatusResponse(BaseModel):
    completed: bool
    course_id: str
    course_name: str = ""
    questions: list[DiagnosticQuestion] | None = None
    result: dict | None = None


class DiagnosticAnswerItem(BaseModel):
    item_id: str
    selected_option: str = ""  # "" = no contestada / "no lo sé"


class DiagnosticSubmitRequest(BaseModel):
    answers: list[DiagnosticAnswerItem] = Field(default_factory=list)
    course_name: str = ""


class DiagnosticResultResponse(BaseModel):
    initial_elo: float
    score_pct: float
    league: dict
    themes: list[dict]
    correct_total: int
    answered: int
    completed: bool = True


# ── Mapa de contenido (nodos = tópicos del curso) ─────────────────────────────


class MapNode(BaseModel):
    topic: str
    label: str = ""
    label_key: str | None = None
    node_id: str | None = None
    node_type: str = "practice"
    elo: float | None  # None = topic not rated yet: shown as pending, never as 1000
    rd: float | None
    approximate: bool = False  # the topic rating is a reconciled baseline (FR-034a)
    item_count: int
    state: str  # completed | current | available | blocked


class CourseMapResponse(BaseModel):
    course_id: str
    course_name: str = ""
    diagnostic_done: bool
    nodes: list[MapNode]


class LessonEventRequest(BaseModel):
    event: str = Field(
        ...,
        description=(
            "node_viewed | objectives_viewed | math_convention_viewed | node_completed"
        ),
    )


class LessonInteractionRequest(BaseModel):
    interaction_id: str = Field(..., min_length=1, max_length=80)
    selected_option: str = Field(..., min_length=1, max_length=160)


class LessonInteractionResponse(BaseModel):
    interaction_id: str
    selected_option: str
    is_expected: bool | None = None
    misconception_tag: str | None = None
    feedback_key: str


class LessonDetailResponse(BaseModel):
    node_id: str
    node_type: str
    course_id: str
    i18n_prefix: str
    next_node_id: str | None = None
    state: str
    presentation: str
    explored_complex_branch: bool = False
    affects_elo: bool
    is_safe_zone: bool
    optional_branch: bool
    objectives: list[str]
    optional_objectives: list[str]
    interactions: list[dict] = Field(default_factory=list)
    staircase: dict | None = None
    content: dict | None = None
    unlock_after: str | None = None
    progress: dict


# ── Socrático ─────────────────────────────────────────────────────────────────


class SocraticRequest(BaseModel):
    item_id: str
    item_content: str
    student_message: str = Field(..., min_length=1, max_length=1000)
    course_id: str | None = None
    api_key: str = Field(
        default="",
        description="API key del proveedor de IA (opcional — usa la del sistema si vacía)",
    )
    provider: str = Field(default="groq", description="Proveedor: groq, anthropic, openai, etc.")
    lang: str = Field(default="es", description="Idioma de la respuesta de KatIA: 'es' o 'en'.")
