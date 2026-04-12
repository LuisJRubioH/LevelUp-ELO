"""
api/routers/student.py
======================
Endpoints del flujo de práctica del estudiante:
  POST /student/next-question  → siguiente pregunta adaptativa
  POST /student/answer         → procesar respuesta + actualizar ELO
  GET  /student/stats          → ELO global, por tópico, racha
  GET  /student/courses        → catálogo de cursos disponibles
  POST /student/enroll         → matricularse en un curso
  POST /student/enroll-by-code → acceso especial por código de invitación
  DELETE /student/enroll/{course_id} → darse de baja
  GET  /student/history        → historial de intentos
"""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import CurrentUser, RepoDep, build_vector_rating
from api.schemas.student import (
    AnswerRequest,
    AnswerResponse,
    CourseResponse,
    EnrollByCodeRequest,
    EnrollRequest,
    ItemResponse,
    NextQuestionRequest,
    NextQuestionResponse,
    StudentStatsResponse,
    TopicELO,
)
from src.application.services.student_service import StudentService
from src.domain.elo.vector_elo import aggregate_global_elo

router = APIRouter(prefix="/student", tags=["student"])


def _make_service(repo) -> StudentService:
    return StudentService(repository=repo, enable_cognitive_modifier=False)


# ── Preguntas ──────────────────────────────────────────────────────────────────


@router.post("/next-question", response_model=NextQuestionResponse)
def next_question(body: NextQuestionRequest, user: CurrentUser, repo: RepoDep):
    """Selecciona la siguiente pregunta adaptativa (ZDP) para el estudiante."""
    service = _make_service(repo)
    vector = build_vector_rating(user["user_id"], repo)

    topic = body.topic or body.course_id  # fallback: usar curso como tópico ELO

    item, status_str = service.get_next_question(
        student_id=user["user_id"],
        topic=topic,
        vector_rating=vector,
        session_correct_ids=set(body.session_correct_ids),
        session_wrong_timestamps=body.session_wrong_timestamps,
        session_questions_count=body.session_questions_count,
        course_id=body.course_id,
    )

    if item is None:
        return NextQuestionResponse(item=None, status=status_str)

    return NextQuestionResponse(
        item=ItemResponse(
            id=item["id"],
            content=item["content"],
            difficulty=item["difficulty"],
            topic=item["topic"],
            options=item["options"],
            image_url=item.get("image_url"),
            tags=item.get("tags") or [],
        ),
        status=status_str,
    )


# ── Respuestas ─────────────────────────────────────────────────────────────────


@router.post("/answer", response_model=AnswerResponse)
def answer(body: AnswerRequest, user: CurrentUser, repo: RepoDep):
    """Procesa una respuesta: actualiza ELO y persiste el intento de forma atómica."""
    service = _make_service(repo)
    vector = build_vector_rating(user["user_id"], repo)

    elo_topic = body.elo_topic or body.item_data.get("topic", body.item_id)
    elo_before = vector.get(elo_topic)

    is_correct, cog_data = service.process_answer(
        user_id=user["user_id"],
        item_data=body.item_data,
        selected_option=body.selected_option,
        reasoning=body.reasoning or "",
        time_taken=body.time_taken,
        vector_rating=vector,
        elo_topic=elo_topic,
    )

    elo_after = vector.get(elo_topic)
    rd_after = vector.get_rd(elo_topic)

    return AnswerResponse(
        is_correct=is_correct,
        correct_option=body.item_data.get("correct_option", ""),
        elo_before=round(elo_before, 2),
        elo_after=round(elo_after, 2),
        rd_after=round(rd_after, 2),
        delta_elo=round(elo_after - elo_before, 2),
        cog_data=cog_data,
    )


# ── Stats ──────────────────────────────────────────────────────────────────────


@router.get("/stats", response_model=StudentStatsResponse)
def stats(user: CurrentUser, repo: RepoDep):
    """Retorna el ELO global, ELO por tópico, racha de estudio y total de intentos."""
    vector = build_vector_rating(user["user_id"], repo)
    global_elo = aggregate_global_elo(vector)

    topic_elos = [
        TopicELO(topic=t, rating=round(r, 2), rd=round(rd, 2))
        for t, (r, rd) in sorted(vector.ratings.items())
    ]

    total = repo.get_total_attempts_count(user["user_id"])
    streak = repo.get_study_streak(user["user_id"])

    # Rank label (16 niveles)
    rank_label = _elo_to_rank(global_elo)

    return StudentStatsResponse(
        user_id=user["user_id"],
        global_elo=round(global_elo, 2),
        topic_elos=topic_elos,
        total_attempts=total,
        study_streak=streak,
        rank_label=rank_label,
    )


# ── Cursos y matrículas ────────────────────────────────────────────────────────


@router.get("/courses", response_model=list[CourseResponse])
def courses(user: CurrentUser, repo: RepoDep):
    """Catálogo de cursos disponibles para el nivel educativo del estudiante."""
    service = _make_service(repo)
    available = service.get_available_courses(user["user_id"])
    enrolled_ids = {e["course_id"] for e in repo.get_user_enrollments(user["user_id"])}

    return [
        CourseResponse(
            id=c["id"],
            name=c["name"],
            block=c.get("block", ""),
            enrolled=c["id"] in enrolled_ids,
            group_id=c.get("group_id"),
        )
        for c in available
    ]


@router.post("/enroll", status_code=status.HTTP_201_CREATED)
def enroll(body: EnrollRequest, user: CurrentUser, repo: RepoDep):
    """Matricula al estudiante en un curso."""
    service = _make_service(repo)
    service.enroll_in_course(user["user_id"], body.course_id, body.group_id)
    return {"message": f"Matriculado en {body.course_id} correctamente."}


@router.post("/enroll-by-code", status_code=status.HTTP_201_CREATED)
def enroll_by_code(body: EnrollByCodeRequest, user: CurrentUser, repo: RepoDep):
    """Acceso especial inter-nivel mediante código de invitación del docente."""
    group = repo.get_group_by_invite_code(body.invite_code)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código de invitación inválido o expirado.",
        )
    group_id = group["id"] if isinstance(group, dict) else group[0]
    course_id = group["course_id"] if isinstance(group, dict) else group[2]
    if not course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El grupo no tiene un curso asignado.",
        )
    repo.enroll_user(user["user_id"], course_id, group_id)
    return {"message": "Acceso especial activado correctamente.", "course_id": course_id}


@router.delete("/enroll/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll(course_id: str, user: CurrentUser, repo: RepoDep):
    """Cancela la matrícula en un curso."""
    repo.unenroll_user(user["user_id"], course_id)


# ── Historial ──────────────────────────────────────────────────────────────────


@router.get("/history")
def history(user: CurrentUser, repo: RepoDep):
    """Últimos 20 intentos del estudiante (para el gráfico de ELO en el frontend)."""
    attempts = repo.get_latest_attempts(user["user_id"], limit=20)
    return {"attempts": attempts}


# ── Helpers ───────────────────────────────────────────────────────────────────


_RANK_THRESHOLDS = [
    (2500, "Leyenda Suprema"),
    (2200, "Leyenda"),
    (2000, "Gran Maestro"),
    (1800, "Maestro"),
    (1600, "Diamante I"),
    (1500, "Diamante II"),
    (1400, "Platino I"),
    (1300, "Platino II"),
    (1200, "Oro I"),
    (1100, "Oro II"),
    (1000, "Plata I"),
    (900, "Plata II"),
    (800, "Bronce I"),
    (700, "Bronce II"),
    (600, "Hierro"),
    (0, "Aspirante"),
]


def _elo_to_rank(elo: float) -> str:
    for threshold, label in _RANK_THRESHOLDS:
        if elo >= threshold:
            return label
    return "Aspirante"
