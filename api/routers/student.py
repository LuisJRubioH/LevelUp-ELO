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
import random

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
    ExamTemplateSummary,
    ItemResponse,
    NextQuestionRequest,
    NextQuestionResponse,
    PendingExam,
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

    # Consolidar tópicos duplicados.
    #
    # Algunos estudiantes tienen intentos con `attempts.topic = item.topic` (flujo
    # viejo) y otros con `attempts.topic = course_id` (flujo actual con elo_topic).
    # Ambos persisten en student_topic_elo y aparecen como tópicos distintos en
    # vector.ratings, confundiendo al estudiante (ver bug #7 del QA de mayo 2026).
    #
    # Fix: usar el catálogo de cursos para mapear slugs (course_id) a nombre
    # legible. Si el mismo curso aparece como slug Y como nombre, conservar la
    # entrada del slug (refleja el flujo actual) y descartar el twin viejo.
    courses_catalog = repo.get_courses() if hasattr(repo, "get_courses") else []
    course_id_to_name = {c["id"]: c["name"] for c in courses_catalog}
    # Nombre humano → slug, para detectar twins (case-insensitive)
    name_lower_to_id = {c["name"].lower(): c["id"] for c in courses_catalog}

    consolidated: dict[str, tuple[float, float]] = {}
    for topic, (r, rd) in vector.ratings.items():
        if topic in course_id_to_name:
            # Es un slug — el display es el nombre del curso.
            display = course_id_to_name[topic]
            consolidated[display] = (r, rd)
        else:
            # Posible nombre humano. Si su slug equivalente ya está en
            # vector.ratings, omitir esta entrada (la del slug gana).
            twin_slug = name_lower_to_id.get(topic.lower())
            if twin_slug and twin_slug in vector.ratings:
                continue
            consolidated[topic] = (r, rd)

    topic_elos = [
        TopicELO(topic=t, rating=round(r, 2), rd=round(rd, 2))
        for t, (r, rd) in sorted(consolidated.items())
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
    ai_proposed_score: float | None = Form(default=None),
    ai_feedback: str | None = Form(default=None),
):
    """Recibe y persiste un procedimiento manuscrito del estudiante.

    Si vienen ai_proposed_score/ai_feedback (del endpoint /procedure/analyze),
    se guardan en la submission para que el docente los vea como sugerencia.
    El score de IA (ai_proposed_score) NO afecta el ELO — solo teacher_score lo hace.
    """
    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    mime = file.content_type or "image/jpeg"
    if mime not in allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {mime}. Usa JPEG, PNG, WebP o PDF.",
        )

    image_data = await file.read()
    if len(image_data) > 10 * 1024 * 1024:
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

    if ai_proposed_score is not None:
        try:
            repo.save_ai_proposed_score(
                user["user_id"],
                item_id,
                float(ai_proposed_score),
                ai_feedback=ai_feedback or "",
            )
        except Exception:
            pass

    return ProcedureSubmitResponse(
        submission_id=0,
        ai_score=ai_proposed_score,
        ai_feedback=ai_feedback,
        status="pending" if ai_proposed_score is None else "PENDING_TEACHER_VALIDATION",
    )


@router.get("/ai-status")
def ai_status():
    """Indica al frontend si el servidor tiene IA configurada (sin revelar keys)."""
    from api.config import settings
    from src.infrastructure.external_api.ai_client import detect_provider_from_key

    procedure_key = settings.get_ai_key("procedure")
    if not procedure_key:
        return {"available": False, "provider": None}
    provider = settings.system_ai_provider or detect_provider_from_key(procedure_key) or "unknown"
    return {"available": True, "provider": provider}


@router.post("/procedure/analyze")
async def analyze_procedure(
    user: CurrentUser,
    item_id: str = Form(...),
    item_content: str = Form(default=""),
    api_key: str = Form(default=""),
    file: UploadFile = File(...),
):
    """Analiza un procedimiento con IA SIN PERSISTIR.

    Prioridad de API key: la del estudiante (si la envía) > la del sistema
    (env SYSTEM_AI_API_KEY). Soporta Groq (revisión rigurosa con Llama 4 Scout)
    y otros proveedores (revisión genérica con visión).
    """
    from api.config import settings
    from src.infrastructure.external_api.ai_client import detect_provider_from_key

    effective_key = settings.get_ai_key("procedure", api_key)
    if not effective_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay API key de IA configurada. Pide al administrador que configure SYSTEM_AI_API_KEY.",
        )

    provider = detect_provider_from_key(effective_key)
    if settings.system_ai_provider and not api_key.strip():
        provider = settings.system_ai_provider

    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    mime = file.content_type or "image/jpeg"
    if mime not in allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {mime}.",
        )

    image_data = await file.read()
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo excede el límite de 10 MB.",
        )

    if mime == "application/pdf":
        try:
            import fitz  # PyMuPDF

            pdf_doc = fitz.open(stream=image_data, filetype="pdf")
            page = pdf_doc[0]
            pix = page.get_pixmap(dpi=200)
            image_data = pix.tobytes("png")
            mime = "image/png"
            pdf_doc.close()
        except Exception as pdf_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No se pudo procesar el PDF: {pdf_err}",
            )

    if provider == "groq":
        from src.infrastructure.external_api.math_procedure_review import (
            review_math_procedure,
        )

        try:
            review = review_math_procedure(
                image_data,
                mime,
                api_key=effective_key,
                question_content=item_content or "",
            )
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=f"Respuesta inválida de la IA: {exc}")
        except ConnectionError as exc:
            raise HTTPException(status_code=503, detail=f"Error de red con Groq: {exc}")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Error al revisar procedimiento: {exc}")

        return {"item_id": item_id, "provider": "groq", "review": review}

    else:
        from src.infrastructure.external_api.ai_client import analyze_procedure_image

        try:
            result = analyze_procedure_image(
                image_data,
                mime,
                question_content=item_content or "",
                model_name="",
                api_key=effective_key,
                provider=provider,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Error al analizar procedimiento: {exc}")

        if result == "VISION_NOT_SUPPORTED":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El modelo configurado no soporta visión. Usa Groq o un modelo con visión.",
            )

        return {
            "item_id": item_id,
            "provider": provider or "unknown",
            "review": {
                "score_procedimiento": None,
                "evaluacion_global": result,
                "transcripcion": None,
                "pasos": [],
                "errores_detectados": [],
                "saltos_logicos": [],
                "resultado_correcto": None,
                "corresponde_a_pregunta": None,
            },
        }


@router.get("/procedures")
def list_my_procedures(user: CurrentUser, repo: RepoDep, limit: int = 50):
    """Lista los procedimientos enviados por el estudiante actual con su
    estado y, si están validados, score docente, comentario y delta ELO.
    Nunca incluye contenido sensible (R9/V2-R9: solo aplica a items, no a procedimientos)."""
    rows = repo.get_student_procedure_submissions(user["user_id"], limit=limit)
    return {"submissions": rows}


# ── Reportes técnicos ─────────────────────────────────────────────────────────


@router.post("/problems", status_code=status.HTTP_201_CREATED)
def submit_problem_report(body: dict, user: CurrentUser, repo: RepoDep):
    """Crea un reporte de problema técnico (mínimo 10 caracteres en la descripción)."""
    description = (body.get("description") or "").strip()
    if len(description) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La descripción debe tener al menos 10 caracteres.",
        )
    if len(description) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La descripción no puede exceder 2000 caracteres.",
        )
    repo.save_problem_report(user_id=user["user_id"], description=description)
    return {"message": "Reporte enviado. Gracias por avisarnos."}


# ── Perfil ───────────────────────────────────────────────────────────────────


@router.patch("/profile")
def update_profile(body: dict, user: CurrentUser, repo: RepoDep):
    """Actualiza el correo electrónico del estudiante."""
    email = (body.get("email") or "").strip()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El correo electrónico es obligatorio.",
        )
    try:
        repo.update_user_email(user["user_id"], email)
    except ValueError as e:
        code = (
            status.HTTP_409_CONFLICT
            if "registrado" in str(e)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=code, detail=str(e))
    return {"message": "Correo actualizado correctamente."}


# ── Modo Examen ───────────────────────────────────────────────────────────────


def _build_standard_exam(repo, course_id: str, n: int) -> list[dict]:
    """
    Construye un examen estándar de N preguntas con curva de dificultad fija.

    Distribución por bandas:
      - 30% fácil (cuartil bajo de difficulty)
      - 40% media
      - 30% difícil
    Mezcla aleatoria dentro de cada banda, orden global ascendente.
    Sin selector adaptativo y sin tocar el ELO del estudiante.
    """
    all_items = repo.get_items_from_db(course_id=course_id)
    if not all_items:
        return []

    sorted_items = sorted(all_items, key=lambda it: it["difficulty"])
    total = len(sorted_items)
    third = max(1, total // 3)
    band_easy = sorted_items[:third]
    band_mid = sorted_items[third : 2 * third]
    band_hard = sorted_items[2 * third :]

    n_easy = max(1, round(n * 0.30))
    n_hard = max(1, round(n * 0.30))
    n_mid = max(0, n - n_easy - n_hard)

    pool: list[dict] = []
    pool += random.sample(band_easy, min(n_easy, len(band_easy)))
    pool += random.sample(band_mid, min(n_mid, len(band_mid)))
    pool += random.sample(band_hard, min(n_hard, len(band_hard)))

    # Si alguna banda quedó corta, rellenar con items no usados de cualquier banda
    used_ids = {it["id"] for it in pool}
    remaining = [it for it in sorted_items if it["id"] not in used_ids]
    random.shuffle(remaining)
    while len(pool) < n and remaining:
        pool.append(remaining.pop())

    pool.sort(key=lambda it: it["difficulty"])
    return pool[:n]


def _items_from_template(repo, template: dict) -> list[dict]:
    """Carga los items de una plantilla preservando el orden definido por el docente."""
    by_id = {it["id"]: it for it in repo.get_items_from_db(course_id=template["course_id"])}
    return [by_id[i] for i in template["item_ids"] if i in by_id]


@router.get("/exam/templates", response_model=list[ExamTemplateSummary])
def list_exam_templates_for_student(
    repo: RepoDep,
    user: CurrentUser,
    course_id: str,
):
    """Plantillas de examen visibles a este estudiante en el curso.

    Filtrado por:
    - Plantilla NO archivada del curso indicado
    - Y: no tiene asignaciones (legacy/abierta) → visible a todos los inscritos
    -    O: hay una asignación al grupo del estudiante con ventana activa
    """
    templates = repo.list_active_templates_for_student(user_id=user["user_id"], course_id=course_id)
    return [
        ExamTemplateSummary(
            id=t["id"],
            title=t["title"],
            course_id=t["course_id"],
            n_questions=len(t["item_ids"]),
            time_limit_min=t["time_limit_min"],
            created_at=t["created_at"],
            window_ends_at=t.get("window_ends_at"),
        )
        for t in templates
    ]


@router.get("/exam/pending", response_model=list[PendingExam])
def list_pending_exams(repo: RepoDep, user: CurrentUser):
    """Plantillas pendientes para el estudiante en TODOS sus cursos inscritos.

    Se usa para el badge de notificación en el sidebar.
    """
    rows = repo.list_pending_exams_for_student(user_id=user["user_id"])
    return [PendingExam(**r) for r in rows]


@router.post("/exam/start", response_model=ExamStartResponse)
def exam_start(body: ExamStartRequest, user: CurrentUser, repo: RepoDep):
    """
    Inicia una sesión de examen.

    Modos:
      - Con `template_id`: usa exactamente los items de la plantilla del docente
        en el orden definido. Ignora n_questions y time_limit_minutes (toma los
        del template).
      - Sin `template_id`: examen estándar con curva de dificultad 30/40/30.

    En ambos casos, NO afecta el ELO del estudiante.
    """
    if body.template_id is not None:
        template = repo.get_exam_template(body.template_id)
        if not template or template.get("archived"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plantilla no encontrada o archivada.",
            )
        if template["course_id"] != body.course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La plantilla no corresponde al curso indicado.",
            )
        selected = _items_from_template(repo, template)
        time_limit_seconds = template["time_limit_min"] * 60
    else:
        n = min(body.n_questions, 30)
        selected = _build_standard_exam(repo, body.course_id, n)
        time_limit_seconds = body.time_limit_minutes * 60

    if not selected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay preguntas disponibles para este examen.",
        )

    items = [
        ItemResponse(
            id=it["id"],
            content=it["content"],
            difficulty=it["difficulty"],
            topic=it["topic"],
            options=it["options"],
            image_url=it.get("image_url"),
            tags=it.get("tags") or [],
        )
        for it in selected
    ]

    return ExamStartResponse(
        items=items,
        n_questions=len(items),
        time_limit_seconds=time_limit_seconds,
        course_id=body.course_id,
    )


@router.post("/exam/submit", response_model=ExamSubmitResponse)
def exam_submit(body: ExamSubmitRequest, user: CurrentUser, repo: RepoDep):
    """
    Recibe las respuestas del examen y devuelve la calificación.

    El examen es EVALUATIVO, no formativo: NO actualiza el ELO del estudiante
    ni la dificultad del ítem. Solo cuenta correctas/incorrectas y persiste
    la sesión en `exam_sessions` para el historial.

    El ELO solo cambia en la sala de práctica.
    """
    results = []
    correct_count = 0

    for ans in body.answers:
        item_db = repo.get_item_by_id(ans.item_id)
        if not item_db:
            continue

        is_correct = ans.selected_option == item_db["correct_option"]
        if is_correct:
            correct_count += 1

        results.append(
            {
                "item_id": ans.item_id,
                "is_correct": is_correct,
                "selected_option": ans.selected_option,
                "elo_delta": 0.0,  # examen no afecta ELO
            }
        )

    # ELO global actual (sin modificación, solo para mostrar en results)
    vector = build_vector_rating(user["user_id"], repo)
    score_pct = round(correct_count / len(body.answers) * 100, 1) if body.answers else 0.0
    global_elo = round(aggregate_global_elo(vector), 2)

    try:
        repo.save_exam_session(
            user_id=user["user_id"],
            course_id=body.course_id,
            course_name=body.course_name,
            n_questions=len(body.answers),
            correct_count=correct_count,
            score_pct=score_pct,
            global_elo_after=global_elo,
        )
    except Exception:
        pass

    return ExamSubmitResponse(
        results=results,
        correct_count=correct_count,
        total_questions=len(body.answers),
        score_pct=score_pct,
        global_elo_after=global_elo,
    )


@router.get("/exam/history")
def exam_history(user: CurrentUser, repo: RepoDep):
    """Historial de intentos de examen del estudiante (últimos 20)."""
    return repo.get_exam_history(user["user_id"], limit=20)


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
