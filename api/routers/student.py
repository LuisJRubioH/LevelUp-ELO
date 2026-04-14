"""
api/routers/student.py
======================
Endpoints del flujo de práctica del estudiante:
  POST /student/next-question  → siguiente pregunta adaptativa
  POST /student/answer         → procesar respuesta + actualizar ELO
  GET  /student/stats          → ELO global, por tópico, racha
  GET  /student/achievements   → logros/badges desbloqueados
  GET  /student/courses        → catálogo de cursos disponibles
  POST /student/enroll         → matricularse en un curso
  POST /student/enroll-by-code → acceso especial por código de invitación
  DELETE /student/enroll/{course_id} → darse de baja
  GET  /student/history        → historial de intentos
  POST /student/exam/start     → inicia sesión de examen cronometrado
  POST /student/exam/submit    → envía respuestas del examen y obtiene resultados
"""

import hashlib

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from api.dependencies import CurrentUser, RepoDep, build_vector_rating
from api.schemas.student import (
    AnswerRequest,
    AnswerResponse,
    CourseResponse,
    EnrollByCodeRequest,
    EnrollRequest,
    ExamStartRequest,
    ExamStartResponse,
    ExamSubmitRequest,
    ExamSubmitResponse,
    ItemResponse,
    NextQuestionRequest,
    NextQuestionResponse,
    ProcedureSubmitResponse,
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

    # Recuperar correct_option desde DB — el cliente no la envía (seguridad)
    item_db = repo.get_item_by_id(body.item_id)
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem '{body.item_id}' no encontrado.",
        )
    # Fusionar datos del cliente con datos canónicos de la DB
    item_data = {**body.item_data, "correct_option": item_db["correct_option"]}

    elo_topic = body.elo_topic or item_data.get("topic", body.item_id)
    elo_before = vector.get(elo_topic)

    is_correct, cog_data = service.process_answer(
        user_id=user["user_id"],
        item_data=item_data,
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
    enrolled_ids = {e["id"] for e in repo.get_user_enrollments(user["user_id"])}

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
    # Validar que el curso existe
    courses = repo.get_courses()
    valid_ids = {c["id"] if isinstance(c, dict) else c[0] for c in courses}
    if body.course_id not in valid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El curso '{body.course_id}' no existe.",
        )
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


@router.get("/activity")
def activity(user: CurrentUser, repo: RepoDep, days: int = 70):
    """Heatmap de actividad diaria: {date: count} de intentos por día (últimos N días)."""
    data = repo.get_activity_heatmap(user["user_id"], days=days)
    return {"activity": data}


@router.get("/streak/{course_id}")
def streak_by_course(course_id: str, user: CurrentUser, repo: RepoDep):
    """Racha de estudio para un curso específico."""
    streak = repo.get_study_streak(user["user_id"], course_id=course_id)
    return {"course_id": course_id, "streak": streak}


@router.get("/group-ranking")
def group_ranking(user: CurrentUser, repo: RepoDep, course_id: str | None = None):
    """Ranking ELO de los compañeros del grupo del estudiante."""
    user_data = repo.get_user_by_id(user["user_id"])
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    group_id = user_data.get("group_id") if isinstance(user_data, dict) else None
    if not group_id:
        return {"ranking": [], "my_rank": None}
    ranking = repo.get_group_ranking(group_id, course_id=course_id)
    # Encontrar la posición del usuario actual
    my_rank = next((r["rank_pos"] for r in ranking if r["user_id"] == user["user_id"]), None)
    return {"ranking": ranking, "my_rank": my_rank}


# ── Logros / Achievements ─────────────────────────────────────────────────────


@router.get("/achievements")
def achievements(user: CurrentUser, repo: RepoDep):
    """Retorna los logros/badges desbloqueados por el estudiante."""
    earned = repo.get_achievements(user["user_id"])
    # Enriquecer con metadatos del catálogo
    svc = _make_service(repo)
    catalog_map = {b["badge_id"]: b for b in svc._BADGE_CATALOG}
    result = []
    for a in earned:
        info = catalog_map.get(a["badge_id"], {})
        result.append(
            {
                "badge_id": a["badge_id"],
                "label": info.get("label", a["badge_id"]),
                "icon": info.get("icon", "🏅"),
                "desc": info.get("desc", ""),
                "earned_at": a["earned_at"],
            }
        )
    return {"achievements": result, "catalog": svc._BADGE_CATALOG}


# ── Procedimientos manuscritos ────────────────────────────────────────────────


@router.post("/procedure", response_model=ProcedureSubmitResponse)
async def submit_procedure(
    user: CurrentUser,
    repo: RepoDep,
    item_id: str = Form(...),
    item_content: str = Form(default=""),
    file: UploadFile = File(...),
):
    """Recibe y persiste un procedimiento manuscrito del estudiante.

    El archivo se almacena en disco (SQLite) o Supabase Storage (PostgreSQL).
    Retorna el submission_id y el estado del procesamiento.
    El score de IA (ai_proposed_score) NO afecta el ELO — solo teacher_score lo hace.
    """
    # Validar tipo de archivo
    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    mime = file.content_type or "image/jpeg"
    if mime not in allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {mime}. Usa JPEG, PNG, WebP o PDF.",
        )

    image_data = await file.read()
    if len(image_data) > 10 * 1024 * 1024:  # 10MB límite
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo excede el límite de 10 MB.",
        )

    file_hash = hashlib.sha256(image_data).hexdigest()

    repo.save_procedure_submission(
        student_id=user["user_id"],
        item_id=item_id,
        item_content=item_content,
        image_data=image_data,
        mime_type=mime,
        file_hash=file_hash,
    )

    return ProcedureSubmitResponse(
        submission_id=0,  # SQLite no retorna el ID; suficiente para el frontend
        ai_score=None,
        ai_feedback=None,
        status="pending",
    )


# ── Modo Examen ───────────────────────────────────────────────────────────────


@router.post("/exam/start", response_model=ExamStartResponse)
def exam_start(body: ExamStartRequest, user: CurrentUser, repo: RepoDep):
    """
    Inicia una sesión de examen cronometrado.
    Selecciona N preguntas adaptativas del curso dado y las devuelve de una vez.
    El estudiante tiene `time_limit_minutes` para responderlas todas.
    """
    service = _make_service(repo)
    vector = build_vector_rating(user["user_id"], repo)

    topic = body.course_id
    n = min(body.n_questions, 30)  # máximo 30 preguntas por examen

    items = []
    session_correct_ids: set[str] = set()

    for _ in range(n):
        item, status_str = service.get_next_question(
            student_id=user["user_id"],
            topic=topic,
            vector_rating=vector,
            session_correct_ids=session_correct_ids,
            session_wrong_timestamps={},
            session_questions_count=len(items),
            course_id=body.course_id,
        )
        if item is None:
            break
        session_correct_ids.add(item["id"])  # evitar duplicados en el examen
        items.append(
            ItemResponse(
                id=item["id"],
                content=item["content"],
                difficulty=item["difficulty"],
                topic=item["topic"],
                options=item["options"],
                image_url=item.get("image_url"),
                tags=item.get("tags") or [],
            )
        )

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay preguntas disponibles para este curso.",
        )

    return ExamStartResponse(
        items=items,
        n_questions=len(items),
        time_limit_seconds=body.time_limit_minutes * 60,
        course_id=body.course_id,
    )


@router.post("/exam/submit", response_model=ExamSubmitResponse)
def exam_submit(body: ExamSubmitRequest, user: CurrentUser, repo: RepoDep):
    """
    Recibe las respuestas del examen y calcula los resultados.
    Actualiza el ELO por cada respuesta (igual que el modo práctica).
    """
    service = _make_service(repo)
    vector = build_vector_rating(user["user_id"], repo)

    results = []
    correct_count = 0

    for ans in body.answers:
        item_db = repo.get_item_by_id(ans.item_id)
        if not item_db:
            continue

        is_correct = ans.selected_option == item_db["correct_option"]
        if is_correct:
            correct_count += 1

        elo_topic = item_db.get("topic", ans.item_id)
        elo_before = vector.get(elo_topic)

        item_data = {**item_db}
        service.process_answer(
            user_id=user["user_id"],
            item_data=item_data,
            selected_option=ans.selected_option,
            reasoning="",
            time_taken=ans.time_taken or 0.0,
            vector_rating=vector,
            elo_topic=elo_topic,
        )

        elo_after = vector.get(elo_topic)
        results.append(
            {
                "item_id": ans.item_id,
                "is_correct": is_correct,
                "correct_option": item_db["correct_option"],
                "selected_option": ans.selected_option,
                "elo_delta": round(elo_after - elo_before, 2),
            }
        )

    from src.domain.elo.vector_elo import aggregate_global_elo

    score_pct = round(correct_count / len(body.answers) * 100, 1) if body.answers else 0.0

    return ExamSubmitResponse(
        results=results,
        correct_count=correct_count,
        total_questions=len(body.answers),
        score_pct=score_pct,
        global_elo_after=round(aggregate_global_elo(vector), 2),
    )


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
