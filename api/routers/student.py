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
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile, status

from api.dependencies import (
    CurrentUser, RepoDep, create_procedure_review_token, decode_token,
)
from api.rate_limit import limiter
from api.config import settings
from api.upload_validation import read_validated_upload
from api.schemas.student import (
    AnswerRequest,
    AnswerResponse,
    CourseMapResponse,
    CourseRatingView,
    CourseResponse,
    DiagnosticQuestion,
    DiagnosticResultResponse,
    DiagnosticStatusResponse,
    DiagnosticSubmitRequest,
    EnrollByCodeRequest,
    MapNode,
    EnrollRequest,
    ExamStartRequest,
    ExamStartResponse,
    ExamSubmitRequest,
    ExamSubmitResponse,
    ExamTemplateSummary,
    ItemResponse,
    LessonDetailResponse,
    LessonEventRequest,
    LessonInteractionRequest,
    LessonInteractionResponse,
    NextQuestionRequest,
    NextQuestionResponse,
    PendingExam,
    ProcedureSubmitResponse,
    StudentStatsResponse,
    TopicELO,
)
from src.application.services.student_service import StudentService
from src.domain.elo.model import diagnostic_baseline
from src.domain.learning.prealgebra import (
    CLASSIFIER_BASIC_NODE_ID,
    CLASSIFIER_RIGOROUS_NODE_ID,
    COMPLEX_NODE_ID,
    DETECTIVE_NODE_ID,
    DIAGNOSTIC_NODE_IDS,
    INTEGERS_NODE_ID,
    IRRATIONALS_NODE_ID,
    N2_HUB_NODE_ID,
    N2_OPERATION_NODE_IDS,
    N3_HUB_NODE_ID,
    N3_MACHINE_NODE_IDS,
    NATURALS_NODE_ID,
    PREALGEBRA_COURSE_ID,
    RATIONALS_NODE_ID,
    REALS_NODE_ID,
    STAIRCASE_NODE_ID,
    TRIGGER_NODE_ID,
    evaluate_interaction,
    get_lesson,
    presentation_band,
    curriculum_map_rows,
    recommended_node_for_misconception,
    route_position,
)

router = APIRouter(prefix="/student", tags=["student"])


def _make_service(repo) -> StudentService:
    """Composición: la capa de entrada es la que conoce infrastructure (R2)."""
    from src.infrastructure.ml.calibration import IsotonicCalibrator

    calibrator = IsotonicCalibrator()
    calibrator.load()  # False si no hay modelo entrenado — se usa p_raw
    return StudentService(repository=repo, calibrator=calibrator)


# ── Preguntas ──────────────────────────────────────────────────────────────────


@router.post("/next-question", response_model=NextQuestionResponse)
def next_question(body: NextQuestionRequest, user: CurrentUser, repo: RepoDep):
    """Selecciona la siguiente pregunta adaptativa (ZDP) para el estudiante."""
    service = _make_service(repo)
    item, status_str = service.get_next_question(
        student_id=user["user_id"],
        course_id=body.course_id,
        topic_filter=body.topic,  # práctica desde el mapa filtra por este tópico
        session_correct_ids=set(body.session_correct_ids),
        session_wrong_timestamps=body.session_wrong_timestamps,
        session_questions_count=body.session_questions_count,
        block=body.block,
    )

    if item is None:
        return NextQuestionResponse(item=None, status=status_str)

    return NextQuestionResponse(
        preview=service.ratings.answer_preview(user["user_id"], body.course_id, item),
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
def answer(
    body: AnswerRequest,
    user: CurrentUser,
    repo: RepoDep,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    """Procesa una respuesta: actualiza el rating del (curso, tópico) del ítem de forma atómica.

    Con `Idempotency-Key`, la primera respuesta y cada reintento devuelven los valores del
    intento tal como quedó persistido, así que son idénticos; el rating guardado conserva la
    precisión completa (FR-012a, research R21). `elo_topic` se acepta y se ignora (spec 001).
    """
    service = _make_service(repo)

    # El cliente identifica el ítem; todos los datos académicos son canónicos.
    item_db = repo.get_item_by_id(body.item_id)
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem '{body.item_id}' no encontrado.",
        )
    if body.selected_option not in item_db["options"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La opción seleccionada no pertenece al ítem.",
        )
    if idempotency_key is not None and not 1 <= len(idempotency_key) <= 128:
        raise HTTPException(status_code=400, detail="Clave de idempotencia inválida.")
    # The item's topic stands where the client's elo_topic used to: old fingerprints of
    # clients that sent no elo_topic stay valid.
    fingerprint = hashlib.sha256(
        "\0".join((body.item_id, body.selected_option, item_db["topic"])).encode("utf-8")
    ).hexdigest()

    def persisted(saved: dict, cog_data: dict) -> AnswerResponse:
        if saved["request_fingerprint"] != fingerprint:
            raise HTTPException(
                status_code=409, detail="La clave de idempotencia pertenece a otra respuesta."
            )
        before = float(saved["elo_before"])
        after = float(saved["elo_after"])
        return AnswerResponse(
            is_correct=bool(saved["is_correct"]),
            elo_before=round(before, 2),
            elo_after=round(after, 2),
            rd_after=round(float(saved["rating_deviation"]), 2),
            delta_elo=round(after - before, 2),
            elo_valid=bool(saved["elo_valid"]),
            cog_data=cog_data,
        )

    if idempotency_key:
        saved = repo.get_answer_by_request_id(user["user_id"], idempotency_key)
        if saved:
            return persisted(saved, {"idempotent_replay": True})

    is_correct, result = service.process_answer(
        user_id=user["user_id"],
        item_data=item_db,
        selected_option=body.selected_option,
        reasoning=body.reasoning or "",
        time_taken=body.time_taken,
        request_id=idempotency_key,
        request_fingerprint=fingerprint if idempotency_key else None,
    )

    if idempotency_key:
        saved = repo.get_answer_by_request_id(user["user_id"], idempotency_key)
        replayed = result.get("idempotent_replay")
        return persisted(saved, {"idempotent_replay": True} if replayed else result)

    return AnswerResponse(
        is_correct=is_correct,
        elo_before=round(result["elo_before"], 2),
        elo_after=round(result["elo_after"], 2),
        rd_after=round(result["rd_after"], 2),
        delta_elo=round(result["elo_after"] - result["elo_before"], 2),
        elo_valid=result["elo_valid"],
        cog_data=result,
    )


# ── Stats ──────────────────────────────────────────────────────────────────────


@router.get("/stats", response_model=StudentStatsResponse)
def stats(user: CurrentUser, repo: RepoDep):
    """Overall rating, per-course ratings, study streak and attempts (spec 001, FR-028a–c).

    Everything comes from RatingReadService: `global_elo` is None and `overall_status` is
    "pending_diagnostic" while no current course has a rated topic.
    """
    view = _make_service(repo).ratings.ratings_view(user["user_id"])
    courses = [
        CourseRatingView(
            **{k: c[k] for k in ("course_id", "course_name", "rating", "display_rating",
                                 "rank_label", "current_context")},
            topics=[TopicELO(topic=t["topic"], rating=t["elo"], rd=t["rd"]) for t in c["topics"]],
        )
        for c in view["courses"]
    ]
    return StudentStatsResponse(
        user_id=user["user_id"],
        global_elo=view["overall"],
        display_rating=view["display_rating"],
        overall_status=view["overall_status"],
        rank_label=view["rank_label"],
        course_ratings=courses,
        topic_elos=[t for c in courses if c.current_context for t in c.topics],
        total_attempts=repo.get_total_attempts_count(user["user_id"]),
        study_streak=repo.get_study_streak(user["user_id"]),
    )


# ── Cursos y matrículas ────────────────────────────────────────────────────────


@router.get("/courses", response_model=list[CourseResponse])
def courses(user: CurrentUser, repo: RepoDep):
    """Catálogo de cursos disponibles para el nivel educativo del estudiante."""
    service = _make_service(repo)
    available = service.get_available_courses(user["user_id"])
    enrolled_ids = {e["id"] for e in repo.get_user_enrollments(user["user_id"])}
    diag_done = set(repo.get_completed_diagnostic_course_ids(user["user_id"]))

    return [
        CourseResponse(
            id=c["id"],
            name=c["name"],
            block=c.get("block", ""),
            enrolled=c["id"] in enrolled_ids,
            group_id=c.get("group_id"),
            diagnostic_done=c["id"] in diag_done,
        )
        for c in available
    ]


@router.get("/blocks/{course_id}")
def course_blocks(course_id: str, user: CurrentUser, repo: RepoDep):
    """Bloques temáticos de un curso (concursos) con conteo de ítems."""
    return repo.get_course_blocks(course_id)


@router.get("/pvp/history")
def pvp_history(user: CurrentUser, repo: RepoDep):
    """Historial de partidas PvP del estudiante autenticado."""
    return repo.get_pvp_history(user["user_id"])


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
    """The student's group ranking on one basis (FR-028d): the requested course (400 unknown,
    403 not enrolled), else the group's course, else the overall rating. Competition ranks;
    pending students last with no rank (FR-028h)."""
    user_data = repo.get_user_by_id(user["user_id"])
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    group_id = user_data.get("group_id") if isinstance(user_data, dict) else None
    if not group_id:
        return {"basis": None, "ranking": [], "my_rank": None}
    try:
        view = _make_service(repo).ratings.ranking_view(
            "group", group_id=group_id, course_id=course_id, requester=user
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return ranking_response(repo, view, user["user_id"])


def ranking_response(repo, view: dict, user_id: int) -> dict:
    """Ranking payload (contracts/api.md): `global_elo`/`rank_pos` stay as aliases."""
    basis = dict(view["basis"])
    names = {c["id"]: c["name"] for c in repo.get_courses()}
    basis["course_name"] = names.get(basis["course_id"]) if basis["course_id"] else None
    ranking = [{**e, "global_elo": e["rating"], "rank_pos": e["rank"]} for e in view["entries"]]
    my_rank = next((e["rank"] for e in ranking if e["user_id"] == user_id), None)
    return {"basis": basis, "ranking": ranking, "my_rank": my_rank}


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
    analysis_token: str | None = Form(default=None),
):
    """Recibe y persiste un procedimiento manuscrito del estudiante.

    Si vienen ai_proposed_score/ai_feedback (del endpoint /procedure/analyze),
    se guardan en la submission para que el docente los vea como sugerencia.
    El score de IA (ai_proposed_score) NO afecta el ELO — solo teacher_score lo hace.
    """
    image_data, mime = await read_validated_upload(file)
    file_hash = hashlib.sha256(image_data).hexdigest()
    if repo.check_file_hash_duplicate(item_id, user["user_id"], file_hash):
        raise HTTPException(status_code=409, detail="Este archivo ya fue enviado por otro estudiante.")

    ai_proposed_score = None
    ai_feedback = None
    if analysis_token:
        review = decode_token(analysis_token)
        if (
            review.get("type") != "procedure_review"
            or int(review.get("sub", -1)) != user["user_id"]
            or review.get("item_id") != item_id
            or review.get("file_hash") != file_hash
        ):
            raise HTTPException(status_code=400, detail="El análisis IA no corresponde al archivo.")
        ai_proposed_score = review.get("score")
        ai_feedback = review.get("feedback") or ""

    submission_id = repo.save_procedure_submission(
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
        submission_id=submission_id,
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
@limiter.limit(settings.rate_limit_review)
async def analyze_procedure(
    request: Request,
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

    original_data, mime = await read_validated_upload(file)
    image_data = original_data
    file_hash = hashlib.sha256(original_data).hexdigest()

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

        return {
            "item_id": item_id, "provider": "groq", "review": review,
            "analysis_token": create_procedure_review_token(
                user["user_id"], item_id, file_hash, review.get("score_procedimiento"),
                review.get("evaluacion_global") or "",
            ),
        }

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

        review = {
            "score_procedimiento": None,
            "evaluacion_global": result,
            "transcripcion": None,
            "pasos": [],
            "errores_detectados": [],
            "saltos_logicos": [],
            "resultado_correcto": None,
            "corresponde_a_pregunta": None,
        }
        return {
            "item_id": item_id,
            "provider": provider or "unknown",
            "review": review,
            "analysis_token": create_procedure_review_token(
                user["user_id"], item_id, file_hash, None, result or "",
            ),
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
        visible = repo.list_active_templates_for_student(
            user_id=user["user_id"], course_id=body.course_id
        )
        template = next((t for t in visible if t["id"] == body.template_id), None)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plantilla no disponible para el estudiante en este momento.",
            )
        if len(template["item_ids"]) != len(set(template["item_ids"])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La plantilla contiene preguntas duplicadas.",
            )
        selected = _items_from_template(repo, template)
        if len(selected) != len(template["item_ids"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La plantilla contiene preguntas que ya no están disponibles.",
            )
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

    session_id = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=time_limit_seconds)
    repo.create_active_exam_session(
        session_id=session_id,
        user_id=user["user_id"],
        course_id=body.course_id,
        template_id=body.template_id,
        item_ids=[it["id"] for it in selected],
        expires_at=expires_at.isoformat(),
    )

    return ExamStartResponse(
        session_id=session_id,
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
    run = repo.get_active_exam_session(body.session_id, user["user_id"])
    if not run:
        raise HTTPException(status_code=404, detail="Sesión de examen no encontrada.")
    if run.get("result") is not None:
        return ExamSubmitResponse(**run["result"])
    if body.course_id and body.course_id != run["course_id"]:
        raise HTTPException(status_code=400, detail="El curso no corresponde a la sesión.")
    if body.template_id is not None and body.template_id != run["template_id"]:
        raise HTTPException(status_code=400, detail="La plantilla no corresponde a la sesión.")

    expected_ids = run["item_ids"]
    submitted_ids = [answer.item_id for answer in body.answers]
    if len(submitted_ids) != len(set(submitted_ids)):
        raise HTTPException(status_code=400, detail="Hay preguntas duplicadas en el envío.")
    if submitted_ids != expected_ids:
        raise HTTPException(
            status_code=400,
            detail="Las respuestas no corresponden exactamente a la sesión iniciada.",
        )

    results = []
    correct_count = 0
    responses = []  # por pregunta, para análisis del docente

    for ans in body.answers:
        item_db = repo.get_item_by_id(ans.item_id)
        if not item_db:
            raise HTTPException(status_code=409, detail="Una pregunta ya no está disponible.")
        if ans.selected_option and ans.selected_option not in item_db["options"]:
            raise HTTPException(status_code=400, detail="Una opción seleccionada no es válida.")

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
        responses.append(
            {
                "item_id": ans.item_id,
                "topic": item_db.get("topic"),
                "is_correct": is_correct,
            }
        )

    # Rating global actual (sin modificación): None mientras el diagnóstico está pendiente.
    score_pct = round(correct_count / len(expected_ids) * 100, 1)
    global_elo = _make_service(repo).ratings.ratings_view(user["user_id"])["overall"]
    result = {
        "results": results,
        "correct_count": correct_count,
        "total_questions": len(expected_ids),
        "score_pct": score_pct,
        "global_elo_after": global_elo,
    }
    saved = repo.complete_active_exam_session(
        body.session_id, user["user_id"], body.course_name, result, responses
    )
    if not saved:
        current = repo.get_active_exam_session(body.session_id, user["user_id"])
        if current and current.get("result") is not None:
            return ExamSubmitResponse(**current["result"])
        raise HTTPException(status_code=409, detail="La sesión de examen expiró.")
    return ExamSubmitResponse(**result)


@router.get("/exam/history")
def exam_history(user: CurrentUser, repo: RepoDep):
    """Historial de intentos de examen del estudiante (últimos 20)."""
    return repo.get_exam_history(user["user_id"], limit=20)


# ── Examen diagnóstico (inicio de materia) ────────────────────────────────────

_DIAG_N = 10  # longitud estándar del diagnóstico


_DIAG_LEAGUES = [
    {"name": "Diamante", "min": 1320, "color": "#7dd3fc", "rank": "Avanzado"},
    {"name": "Oro", "min": 1180, "color": "#ffd700", "rank": "Intermedio-alto"},
    {"name": "Plata", "min": 1040, "color": "#cbd5e1", "rank": "Intermedio"},
    {"name": "Bronce", "min": 0, "color": "#d8975a", "rank": "Inicial"},
]


def _diag_league(elo: float) -> dict:
    for lg in _DIAG_LEAGUES:
        if elo >= lg["min"]:
            return lg
    return _DIAG_LEAGUES[-1]


@router.get("/diagnostic/{course_id}", response_model=DiagnosticStatusResponse)
def diagnostic_status(course_id: str, user: CurrentUser, repo: RepoDep, redo: bool = False):
    """Estado del diagnóstico de una materia.

    Si ya está hecho → devuelve el resultado guardado. Si no (o `redo=true`) →
    devuelve ~10 preguntas (sin la opción correcta) para presentarlo."""
    existing = repo.get_diagnostic(user["user_id"], course_id)
    if existing and not redo:
        return DiagnosticStatusResponse(
            completed=True,
            course_id=course_id,
            result={**existing["result"], "initial_elo": existing["initial_elo"],
                    "score_pct": existing["score_pct"]},
        )

    items = _build_standard_exam(repo, course_id, _DIAG_N)
    questions = [
        DiagnosticQuestion(
            id=it["id"],
            content=it["content"],
            topic=it.get("topic"),
            difficulty=int(it.get("difficulty", 1000)),
            options=it.get("options", []),
        )
        for it in items
    ]
    return DiagnosticStatusResponse(completed=False, course_id=course_id, questions=questions)


@router.post("/diagnostic/{course_id}/submit", response_model=DiagnosticResultResponse)
def diagnostic_submit(
    course_id: str, body: DiagnosticSubmitRequest, user: CurrentUser, repo: RepoDep
):
    """Califica el diagnóstico, fija el ELO inicial por tópico y lo marca hecho.

    Evaluativo: no genera intentos. 'No lo sé'/saltar = opción vacía → no
    cambia ELO pero cuenta como vacío del tema."""
    BASE = 1000.0
    by_topic: dict[str, dict] = {}
    correct_total = 0
    answered = 0
    seen_item_ids: set[str] = set()

    for ans in body.answers:
        if ans.item_id in seen_item_ids:
            raise HTTPException(status_code=400, detail="El diagnóstico contiene ítems repetidos.")
        seen_item_ids.add(ans.item_id)
        item_db = repo.get_item_by_id(ans.item_id)
        if not item_db or item_db.get("course_id") != course_id:
            raise HTTPException(status_code=400, detail="Ítem ajeno al curso diagnosticado.")
        if ans.selected_option and ans.selected_option not in item_db.get("options", []):
            raise HTTPException(status_code=400, detail="Opción inválida en el diagnóstico.")
        topic = item_db.get("topic") or course_id
        t = by_topic.setdefault(topic, {"answers": [], "correct": 0, "total": 0})
        t["total"] += 1
        difficulty = float(item_db.get("difficulty", 1000))
        if not ans.selected_option:  # no contestada / no lo sé
            t["answers"].append((difficulty, None))
            continue
        answered += 1
        is_correct = ans.selected_option == item_db["correct_option"]
        t["answers"].append((difficulty, is_correct))
        if is_correct:
            t["correct"] += 1
            correct_total += 1

    # fijar ELO inicial por tópico (clamp) y construir desglose
    themes = []
    elos = []
    for topic, t in by_topic.items():
        elo = diagnostic_baseline(t["answers"])
        elos.append(elo)
        # Un nuevo diagnóstico puede medir progreso, pero nunca reinicia una
        # línea ELO que ya contiene práctica real del alumno.
        if not repo.has_practice_attempts(user["user_id"], course_id, topic):
            repo.set_topic_rating_baseline(user["user_id"], course_id, topic, elo)
        ratio = t["correct"] / t["total"] if t["total"] else 0.0
        status = "strong" if ratio >= 0.67 else "mid" if ratio >= 0.34 else "gap"
        themes.append(
            {
                "topic": topic,
                "correct": t["correct"],
                "total": t["total"],
                "ratio": round(ratio, 2),
                "status": status,
                "elo": elo,
            }
        )

    total_q = sum(t["total"] for t in by_topic.values())
    initial_elo = round(sum(elos) / len(elos), 2) if elos else BASE
    score_pct = round(correct_total / total_q * 100, 1) if total_q else 0.0
    league = _diag_league(initial_elo)

    import json as _json

    result_payload = {
        "themes": themes,
        "league": league,
        "correct_total": correct_total,
        "answered": answered,
    }
    repo.save_diagnostic(
        user["user_id"], course_id, initial_elo, score_pct, _json.dumps(result_payload)
    )

    return DiagnosticResultResponse(
        initial_elo=initial_elo,
        score_pct=score_pct,
        league=league,
        themes=themes,
        correct_total=correct_total,
        answered=answered,
    )


# ── Mapa de contenido ─────────────────────────────────────────────────────────

_MASTERY_ELO = 1250.0  # umbral para considerar un tópico "dominado"
_LESSON_EVENTS = {
    "node_viewed",
    "objectives_viewed",
    "math_convention_viewed",
    "node_completed",
}


def _ensure_n2_hub_completed_if_cards_opened(repo, user_id: int, course_id: str) -> None:
    """Repara estados previos: 6 carteles abiertos => hub N2 completado."""
    progress = repo.get_lesson_progress(user_id, course_id, N2_HUB_NODE_ID)
    if progress["state"] == "completed":
        return

    hub = get_lesson(N2_HUB_NODE_ID)
    if not hub:
        return
    required = {interaction["interaction_id"] for interaction in hub.get("interactions", [])}
    responses = repo.get_lesson_interactions(user_id, course_id, N2_HUB_NODE_ID)
    if required and required.issubset(responses):
        repo.record_lesson_event(user_id, course_id, N2_HUB_NODE_ID, "node_completed")


def _ensure_n3_hub_completed_if_machines_introduced(repo, user_id: int, course_id: str) -> None:
    """Repara estados previos: 5 máquinas introducidas => hub N3 completado."""
    progress = repo.get_lesson_progress(user_id, course_id, N3_HUB_NODE_ID)
    if progress["state"] == "completed":
        return

    hub = get_lesson(N3_HUB_NODE_ID)
    if not hub:
        return
    required = {interaction["interaction_id"] for interaction in hub.get("interactions", [])}
    responses = repo.get_lesson_interactions(user_id, course_id, N3_HUB_NODE_ID)
    if required and required.issubset(responses):
        repo.record_lesson_event(user_id, course_id, N3_HUB_NODE_ID, "node_completed")


def _all_nodes_completed(repo, user_id: int, course_id: str, node_ids: list[str]) -> bool:
    return all(
        repo.get_lesson_progress(user_id, course_id, node_id)["state"] == "completed"
        for node_id in node_ids
    )


def _lesson_with_progress(repo, user_id: int, course_id: str, lesson: dict) -> dict:
    """Combina el catálogo con progreso, respetando el desbloqueo secuencial."""
    if lesson["node_id"] == N2_HUB_NODE_ID or lesson.get("unlock_after") == N2_HUB_NODE_ID:
        _ensure_n2_hub_completed_if_cards_opened(repo, user_id, course_id)
    if lesson["node_id"] == N3_HUB_NODE_ID or lesson.get("unlock_after") == N3_HUB_NODE_ID:
        _ensure_n3_hub_completed_if_machines_introduced(repo, user_id, course_id)
    if lesson["node_id"] in {N3_HUB_NODE_ID, *N3_MACHINE_NODE_IDS}:
        if not _all_nodes_completed(repo, user_id, course_id, N2_OPERATION_NODE_IDS):
            raise HTTPException(status_code=403, detail="Completa el Nivel 2 primero")

    unlock_after = lesson.get("unlock_after")
    if unlock_after:
        prerequisite = repo.get_lesson_progress(user_id, course_id, unlock_after)
        if prerequisite["state"] != "completed":
            raise HTTPException(status_code=403, detail="Completa el nodo anterior primero")

    progress = repo.get_lesson_progress(user_id, course_id, lesson["node_id"])
    progress["responses"] = repo.get_lesson_interactions(
        user_id, course_id, lesson["node_id"]
    )
    diagnostic = repo.get_diagnostic(user_id, course_id)
    presentation = presentation_band(diagnostic.get("score_pct") if diagnostic else None)

    # Complejos (B09) es callejón opcional: solo banda intermedia/avanzada.
    if lesson["node_id"] == COMPLEX_NODE_ID and presentation == "basico":
        raise HTTPException(
            status_code=403,
            detail="Nodo opcional disponible solo para banda intermedia o avanzada",
        )

    # explored_complex_branch (derivado): el estudiante abrió/completó B09.
    # Gobierna el contenido complejo en cascada (B10–B13).
    complex_state = repo.get_lesson_progress(user_id, course_id, COMPLEX_NODE_ID)["state"]
    explored_complex_branch = complex_state in ("viewed", "completed")

    lesson_payload = {**lesson}
    if lesson["node_id"] == N3_HUB_NODE_ID and lesson.get("content"):
        content = {**lesson["content"]}
        machines = []
        previous_completed = True
        for machine in content.get("machines", []):
            machine_progress = repo.get_lesson_progress(user_id, course_id, machine["node_id"])
            state = (
                "completed"
                if machine_progress["state"] == "completed"
                else "current"
                if previous_completed
                else "blocked"
            )
            machines.append({**machine, "state": state})
            previous_completed = machine_progress["state"] == "completed"
        content["machines"] = machines
        lesson_payload["content"] = content

    return {
        **lesson_payload,
        "course_id": course_id,
        "state": progress["state"],
        "presentation": presentation,
        "explored_complex_branch": explored_complex_branch,
        "progress": progress,
    }


@router.get(
    "/lessons/{course_id}/{node_id}",
    response_model=LessonDetailResponse,
)
def lesson_detail(course_id: str, node_id: str, user: CurrentUser, repo: RepoDep):
    """Entrega metadatos curriculares sin exponer respuestas ni tocar ELO."""
    lesson = get_lesson(node_id)
    if course_id != PREALGEBRA_COURSE_ID or lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    return LessonDetailResponse(
        **_lesson_with_progress(repo, user["user_id"], course_id, lesson)
    )


@router.post(
    "/lessons/{course_id}/{node_id}/events",
    response_model=LessonDetailResponse,
)
def lesson_event(
    course_id: str,
    node_id: str,
    body: LessonEventRequest,
    user: CurrentUser,
    repo: RepoDep,
):
    """Registra progreso idempotente de contenido; nunca actualiza ELO."""
    lesson = get_lesson(node_id)
    if course_id != PREALGEBRA_COURSE_ID or lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    if body.event not in _LESSON_EVENTS:
        raise HTTPException(status_code=422, detail="Evento de lección inválido")

    _lesson_with_progress(repo, user["user_id"], course_id, lesson)
    required_by_node = {
        TRIGGER_NODE_ID: {"PREALG-N1-B02-Q01", "PREALG-N1-B02-Q02"},
        STAIRCASE_NODE_ID: {"PREALG-N1-B03-Q01"},
        # Los nodos reconstruidos a 11 bloques no se listan: sus interacciones
        # son data-driven y se derivan del propio nodo (igual que N2/N3/N4).
    }
    if body.event == "node_completed" and (lesson.get("content") or {}).get(
        "kind"
    ) == "eleven_block_node":
        required_by_node[node_id] = {
            interaction["interaction_id"] for interaction in lesson.get("interactions", [])
        }
    if body.event == "node_completed" and node_id in required_by_node:
        responses = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        required = required_by_node[node_id]
        if not required.issubset(responses):
            raise HTTPException(status_code=409, detail="Responde las dos preguntas primero")
    if body.event == "node_completed" and (
        node_id == N2_HUB_NODE_ID or node_id in N2_OPERATION_NODE_IDS
    ):
        responses = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        required = {interaction["interaction_id"] for interaction in lesson.get("interactions", [])}
        if not required.issubset(responses):
            raise HTTPException(status_code=409, detail="Completa las interacciones del nodo")
    if body.event == "node_completed" and (
        node_id == N3_HUB_NODE_ID or node_id in N3_MACHINE_NODE_IDS
    ):
        responses = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        required = {interaction["interaction_id"] for interaction in lesson.get("interactions", [])}
        if not required.issubset(responses):
            raise HTTPException(status_code=409, detail="Completa las interacciones del nodo")
    repo.record_lesson_event(user["user_id"], course_id, node_id, body.event)
    return LessonDetailResponse(
        **_lesson_with_progress(repo, user["user_id"], course_id, lesson)
    )


@router.post(
    "/lessons/{course_id}/{node_id}/interactions",
    response_model=LessonInteractionResponse,
)
def lesson_interaction(
    course_id: str,
    node_id: str,
    body: LessonInteractionRequest,
    user: CurrentUser,
    repo: RepoDep,
):
    """Evalúa y guarda solo una selección cerrada; no acepta texto libre."""
    lesson = get_lesson(node_id)
    if course_id != PREALGEBRA_COURSE_ID or lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    _lesson_with_progress(repo, user["user_id"], course_id, lesson)
    result = evaluate_interaction(node_id, body.interaction_id, body.selected_option)
    if result is None:
        raise HTTPException(status_code=422, detail="Interacción u opción inválida")

    repo.save_lesson_interaction(
        user["user_id"],
        course_id,
        node_id,
        result["interaction_id"],
        result["selected_option"],
        result["is_expected"],
        result["misconception_tag"],
    )
    if node_id == N2_HUB_NODE_ID:
        responses = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        required = {interaction["interaction_id"] for interaction in lesson.get("interactions", [])}
        if required and required.issubset(responses):
            repo.record_lesson_event(user["user_id"], course_id, node_id, "node_completed")
    if node_id == N3_HUB_NODE_ID:
        responses = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        required = {interaction["interaction_id"] for interaction in lesson.get("interactions", [])}
        if required and required.issubset(responses):
            repo.record_lesson_event(user["user_id"], course_id, node_id, "node_completed")
    return LessonInteractionResponse(**result)


_NODE_MAP_TITLE = {
    NATURALS_NODE_ID: "prealgebra.n1.b04.mapTitle",
    INTEGERS_NODE_ID: "prealgebra.n1.b05.mapTitle",
    RATIONALS_NODE_ID: "prealgebra.n1.b06.mapTitle",
    IRRATIONALS_NODE_ID: "prealgebra.n1.b07.mapTitle",
    REALS_NODE_ID: "prealgebra.n1.b08.mapTitle",
    COMPLEX_NODE_ID: "prealgebra.n1.b09.mapTitle",
    CLASSIFIER_BASIC_NODE_ID: "prealgebra.n1.b10.mapTitle",
    CLASSIFIER_RIGOROUS_NODE_ID: "prealgebra.n1.b11.mapTitle",
    DETECTIVE_NODE_ID: "prealgebra.n1.b12.mapTitle",
}


@router.get("/prealgebra-summary/{course_id}")
def prealgebra_summary(course_id: str, user: CurrentUser, repo: RepoDep):
    """Cierre diagnóstico (B13): agrega progreso y misconceptions del nivel.

    No afecta ELO. MVP: persiste/lee misconceptions de las interacciones y
    propone hasta 4 nodos de repaso. Sin panel docente todavía.
    """
    explored = repo.get_lesson_progress(
        user["user_id"], course_id, COMPLEX_NODE_ID
    )["state"] in ("viewed", "completed")

    applicable = [n for n in DIAGNOSTIC_NODE_IDS if n != COMPLEX_NODE_ID or explored]
    completed_nodes = 0
    misconceptions: list[str] = []
    for node_id in applicable:
        progress = repo.get_lesson_progress(user["user_id"], course_id, node_id)
        if progress["state"] == "completed":
            completed_nodes += 1
        responses = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        for resp in responses.values():
            tag = resp.get("misconception_tag")
            if tag and tag not in misconceptions:
                misconceptions.append(tag)

    # Ruta de repaso: nodos recomendados (máx 4), únicos, en orden de ruta.
    review_nodes: list[str] = []
    for tag in misconceptions:
        node = recommended_node_for_misconception(tag)
        if node and node in _NODE_MAP_TITLE and node not in review_nodes:
            review_nodes.append(node)
    # Por posición en la ruta, no por índice en la lista de un nivel: desde que
    # el enrutado cubre N2-N4 y Álgebra, `DIAGNOSTIC_NODE_IDS.index` reventaría.
    review_nodes.sort(key=route_position)
    review = [
        {"node_id": n, "label_key": _NODE_MAP_TITLE[n]}
        for n in review_nodes[:4]
    ]

    if not misconceptions and completed_nodes == len(applicable):
        overall_status = "strong"
    elif len(review) >= 3:
        overall_status = "attention"
    else:
        overall_status = "review"

    return {
        "course_id": course_id,
        "completed_nodes": completed_nodes,
        "total_nodes": len(applicable),
        "overall_status": overall_status,
        "review": review,
    }


@router.get("/map/{course_id}", response_model=CourseMapResponse)
def course_map(course_id: str, user: CurrentUser, repo: RepoDep):
    """Mapa de contenido de una materia: un nodo por tópico, ordenados por
    dificultad, con el ELO/estado del estudiante (leído de student_topic_elo,
    incluye el ELO inicial del diagnóstico)."""
    items = repo.get_items_from_db(course_id=course_id)
    # This course's topic ratings only (spec 001, FR-029); an unrated topic has no rating.
    elo_map = {
        r["topic"]: {"elo": r["elo"], "rd": r["rd"]}
        for r in repo.get_course_topic_ratings(user["user_id"], course_id=course_id)
    }
    diagnostic_done = repo.get_diagnostic(user["user_id"], course_id) is not None

    # agrupar ítems por tópico con sus dificultades
    by_topic: dict[str, list[float]] = {}
    for it in items:
        topic = it.get("topic") or course_id
        by_topic.setdefault(topic, []).append(float(it.get("difficulty", 1000)))

    topics_sorted = sorted(by_topic.items(), key=lambda kv: sum(kv[1]) / max(1, len(kv[1])))

    # Si hay pocos tópicos, subdividir cada uno en niveles por dificultad para
    # que el mapa tenga varios nodos visibles. Si hay muchos, usar tópicos.
    _LEVELS = ["Fundamentos", "Intermedio", "Avanzado"]
    raw: list[dict] = []
    subdivide = len(topics_sorted) < 5

    def _elo_for(topic: str) -> tuple[float | None, float | None]:
        te = elo_map.get(topic)
        return (float(te["elo"]), float(te["rd"])) if te else (None, None)

    def _mastered(elo: float | None) -> bool:
        return elo is not None and elo >= _MASTERY_ELO

    for topic, diffs in topics_sorted:
        elo, rd = _elo_for(topic)
        if subdivide and len(diffs) >= 3:
            diffs_sorted = sorted(diffs)
            third = max(1, len(diffs_sorted) // 3)
            bands = [diffs_sorted[:third], diffs_sorted[third : 2 * third], diffs_sorted[2 * third :]]
            for bi, band in enumerate(bands):
                if not band:
                    continue
                raw.append({
                    "topic": topic,
                    "label": f"{topic} · {_LEVELS[bi]}",
                    "elo": elo, "rd": rd, "item_count": len(band),
                })
        else:
            raw.append({"topic": topic, "label": topic, "elo": elo, "rd": rd, "item_count": len(diffs)})

    raw = raw[:30]  # tope de nodos para no saturar el mapa

    curriculum: list[MapNode] = []
    curriculum_completed = True
    if course_id == PREALGEBRA_COURSE_ID:
        # Una sola lectura por nodo; la ruta y los estados los deriva el dominio
        # de `unlock_after`. El endpoint ya no sabe de nodos concretos: añadir
        # uno no se toca aquí.
        _cache: dict[str, str] = {}

        def _state_of(node_id: str) -> str:
            if node_id not in _cache:
                _cache[node_id] = repo.get_lesson_progress(
                    user["user_id"], course_id, node_id
                )["state"]
            return _cache[node_id]

        # B09 (complejos) solo visible para banda intermedia/avanzada (callejón opcional).
        _diag = repo.get_diagnostic(user["user_id"], course_id)
        complex_visible = presentation_band(
            _diag.get("score_pct") if _diag else None
        ) in ("intermedio", "avanzado")
        curriculum = [
            MapNode(**row)
            for row in curriculum_map_rows(_state_of, complex_visible=complex_visible)
        ]
        curriculum_completed = _state_of(REALS_NODE_ID) == "completed"

    # estado: dominado (>=umbral) = completed; el PRIMER nodo no dominado =
    # current (dónde reforzar); el resto = available (no se bloquea: es refuerzo).
    current_idx = (
        next((i for i, n in enumerate(raw) if not _mastered(n["elo"])), None)
        if curriculum_completed
        else None
    )
    nodes = curriculum + [
        MapNode(
            topic=n["topic"],
            label=n["label"],
            elo=None if n["elo"] is None else round(n["elo"], 1),
            rd=None if n["rd"] is None else round(n["rd"], 1),
            item_count=n["item_count"],
            state=(
                "blocked"
                if not curriculum_completed
                else "completed"
                if _mastered(n["elo"])
                else "current"
                if i == current_idx
                else "available"
            ),
        )
        for i, n in enumerate(raw)
    ]

    course_name = next((c["name"] for c in repo.get_courses() if c["id"] == course_id), course_id)
    return CourseMapResponse(
        course_id=course_id,
        course_name=course_name,
        diagnostic_done=diagnostic_done,
        nodes=nodes,
    )

