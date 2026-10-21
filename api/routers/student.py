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
  POST /student/enroll-by-code → invitación de un solo uso de un grupo (spec 001 INV)
  DELETE /student/enroll/{course_id} → darse de baja
  GET  /student/history        → historial de intentos
  POST /student/exam/start     → inicia sesión de examen cronometrado
  POST /student/exam/submit    → envía respuestas del examen y obtiene resultados
"""

import asyncio
import functools
import hashlib
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)

from api.ai_target import (
    GROQ_ONLY,
    TIMED_OUT,
    UNAVAILABLE,
    ai_target,
    require_enrolled_in_item,
)
from api.dependencies import (
    CurrentUser, RepoDep, create_procedure_review_token, decode_token, require_role,
)
from api.katia_record import classify_closed
from api.rate_limit import limiter
from api.config import settings
from api.upload_validation import read_validated_upload
from api.schemas.auth import DisplayNameRequest
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
    PathSummaryResponse,
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
from src.application.services.rating_read_service import RatingReadService
from src.application.services.student_service import StudentService
from src.application.services.study_report_service import StudyReportService
from src.domain.elo.model import diagnostic_baseline
from src.domain.katia.conversation import STALE_AFTER_HOURS, close_outcome
from src.domain.procedures import COPY, REFUSE_OTHER_ITEM, REFUSE_SAME_ITEM
from src.domain.learning.public_content import public_content
from src.domain.learning.path import (
    completes_on_cards,
    completion_gaps,
    completion_refused,
    is_post_diagnostic,
    post_diagnostic_outcome,
    node_access,
)
from src.domain.learning.prealgebra import (
    PREALGEBRA_COURSE_ID,
    curriculum_map_rows,
    evaluate_interaction,
    explored_optional_branch,
    get_lesson,
    path_summary,
    presentation_band,
)

logger = logging.getLogger("api.student")

router = APIRouter(prefix="/student", tags=["student"])


@functools.lru_cache(maxsize=1)
def _calibrator():
    """One calibrator per process (survey 008 B15): its model is read from disk once, not on
    every request. Read-only after loading, so requests share it."""
    from src.infrastructure.ml.calibration import IsotonicCalibrator

    calibrator = IsotonicCalibrator()
    calibrator.load()  # False si no hay modelo entrenado — se usa p_raw
    return calibrator


def _make_service(repo) -> StudentService:
    """Composición: la capa de entrada es la que conoce infrastructure (R2)."""
    return StudentService(repository=repo, calibrator=_calibrator())


def _require_enrolment(service: StudentService, user_id: int, course_id: str) -> None:
    """403 before serving an item or touching any rating (spec 001 FR-037, FR-037a)."""
    try:
        service.ensure_enrolled(user_id, course_id)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No estás inscrito en este curso."
        )


_PREVIEW_REFUSED = "Vista previa: no se guarda progreso."


def _path_access(repo, user: dict, course_id: str) -> bool:
    """Who may use a course's learning path (spec 003 L1, FR-010, FR-011, N10).

    False — a student enrolled in the course (spec 001 FR-037's check): they walk it. True — a
    teacher with a group in the course, or an admin: they read it, and nothing they send is
    stored. Anyone else: 403, before any read or write.
    """
    if user["role"] == "student":
        _require_enrolment(_make_service(repo), user["user_id"], course_id)
        return False
    if user["role"] == "admin":
        return True
    if user["role"] == "teacher" and any(
        group.get("course_id") == course_id
        for group in repo.get_groups_by_teacher(user["user_id"])
    ):
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="No estás inscrito en este curso."
    )


def _refuse_preview(preview: bool) -> None:
    if preview:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_PREVIEW_REFUSED)


# ── Preguntas ──────────────────────────────────────────────────────────────────


@router.post("/next-question", response_model=NextQuestionResponse)
def next_question(
    body: NextQuestionRequest,
    user: CurrentUser,
    repo: RepoDep,
    background_tasks: BackgroundTasks,
):
    """Selecciona la siguiente pregunta adaptativa (ZDP) para el estudiante."""
    service = _make_service(repo)
    _require_enrolment(service, user["user_id"], body.course_id)
    # Spec 005 FR-031, FR-032: asking for another item abandons the open KatIA conversations
    # (their text goes in the same transaction); the 24-hour sweep runs here too.
    closed = repo.close_katia_conversations(user["user_id"], close_outcome("other_item"))
    closed += repo.expire_stale_katia_conversations(STALE_AFTER_HOURS)
    background_tasks.add_task(classify_closed, repo, closed)
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
    background_tasks: BackgroundTasks,
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
    # Before option validation and the retry replay: a refused answer changes nothing.
    _require_enrolment(service, user["user_id"], item_db["course_id"])
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

    # Spec 005 FR-031: the answer closes the item's KatIA conversation in its own transaction,
    # which deletes the text; it is read first so the difficulty can be classified afterwards.
    katia_closing = repo.open_katia_transcripts(user["user_id"], body.item_id)
    is_correct, result = service.process_answer(
        user_id=user["user_id"],
        item_data=item_db,
        selected_option=body.selected_option,
        reasoning=body.reasoning or "",
        time_taken=body.time_taken,
        request_id=idempotency_key,
        request_fingerprint=fingerprint if idempotency_key else None,
    )
    if not result.get("idempotent_replay"):
        background_tasks.add_task(classify_closed, repo, katia_closing)

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
            topics=[
                TopicELO(topic=t["topic"], rating=t["elo"], rd=t["rd"],
                         approximate=t["approximate"], origin=t["origin"])
                for t in c["topics"]
            ],
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
        subtopics=StudyReportService(repo).subtopic_report(user["user_id"]),
    )


# ── Cursos y matrículas ────────────────────────────────────────────────────────


@router.get("/courses", response_model=list[CourseResponse])
def courses(user: CurrentUser, repo: RepoDep):
    """The student's catalogue, then the courses they are enrolled in outside it.

    Spec 001 FR-028k, FR-028l: a course reached by invitation is listed as enrolled with
    `in_catalogue: false`; a semillero student without a grade has no catalogue, so only their
    enrolments are listed (FR-028o).
    """
    service = _make_service(repo)
    available = service.get_available_courses(user["user_id"])
    enrolments = {e["id"]: e for e in repo.get_user_enrollments(user["user_id"])}
    diag_done = set(repo.get_completed_diagnostic_course_ids(user["user_id"]))
    catalogue_ids = {c["id"] for c in available}
    listed = [(c, True) for c in available] + [
        (e, False) for course_id, e in enrolments.items() if course_id not in catalogue_ids
    ]

    return [
        CourseResponse(
            id=c["id"],
            name=c["name"],
            block=c.get("block", ""),
            enrolled=c["id"] in enrolments,
            group_id=(enrolments.get(c["id"]) or {}).get("group_id"),
            diagnostic_done=c["id"] in diag_done,
            in_catalogue=in_catalogue,
        )
        for c, in_catalogue in listed
    ]


@router.get("/blocks/{course_id}")
def course_blocks(course_id: str, user: CurrentUser, repo: RepoDep):
    """Bloques temáticos de un curso (concursos) con conteo de ítems."""
    return repo.get_course_blocks(course_id)


@router.get("/pvp/history")
def pvp_history(
    user: CurrentUser,
    repo: RepoDep,
    # A match id: PostgreSQL INTEGER, so anything outside 1 … 2³¹−1 is refused here (422).
    before: int | None = Query(None, ge=1, le=2_147_483_647),
):
    """Historial de partidas PvP del estudiante autenticado, de a 5 (spec 007 FR-060): terminadas
    y abandonadas, con su materia y su motivo; `before` pide las siguientes. El rival, por su
    nombre visible (spec 004 FR-021), y el delta a mostrar, redondeado en el servidor (V14)."""
    return RatingReadService(repo).pvp_history(user["user_id"], before)


@router.put("/display-name")
def change_display_name(body: DisplayNameRequest, user: CurrentUser, repo: RepoDep):
    """Spec 004 FR-025: the student changes their own display name, under the name filter
    (FR-020); the change is recorded. No display name is decided for teachers."""
    if user["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Solo los estudiantes tienen nombre visible."
        )
    ok, message = repo.set_display_name(user["user_id"], user["user_id"], body.display_name)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"display_name": message}


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
    try:
        service.enroll_from_catalogue(user["user_id"], body.course_id)
    except PermissionError:
        # Spec 001 FR-028m: other levels' courses are reached only through an invitation.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Ese curso no está en tu catálogo."
        )
    return {"message": f"Matriculado en {body.course_id} correctamente."}


# Spec 001 FR-028r, FR-028s: a refused invitation stays as it was.
_INVITATION_REFUSALS = {
    "invalid": (status.HTTP_404_NOT_FOUND, "Código de invitación inválido."),
    "used": (
        status.HTTP_409_CONFLICT,
        "Este código ya fue usado. Pide uno nuevo a tu docente.",
    ),
    "expired": (status.HTTP_410_GONE, "Este código venció. Pide uno nuevo a tu docente."),
    "already_member": (status.HTTP_409_CONFLICT, "Ya estás en este grupo."),
    "no_course": (status.HTTP_400_BAD_REQUEST, "El grupo no tiene un curso asignado."),
}


@router.post("/enroll-by-code", status_code=status.HTTP_201_CREATED)
def enroll_by_code(body: EnrollByCodeRequest, user: CurrentUser, repo: RepoDep):
    """Redeem a single-use invitation of a teacher's group (spec 001 FR-028l, FR-028q … FR-028u).

    The first student who redeems it consumes it. The group's reusable code of the old system
    (`groups.invite_code`) is not read: it is an unknown invitation.
    """
    if user["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden usar un código de invitación.",
        )
    try:
        result = _make_service(repo).enroll_by_invitation(user["user_id"], body.invite_code)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Necesitamos registrar tu grado para usar un código de invitación. "
                "Contacta a tu docente o al administrador."
            ),
        )
    if result["status"] in _INVITATION_REFUSALS:
        code, detail = _INVITATION_REFUSALS[result["status"]]
        raise HTTPException(status_code=code, detail=detail)
    return {"message": "Acceso especial activado correctamente.", "course_id": result["course_id"]}


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
    # Spec 004 FR-021: classmates by `name`; the username of a named student never leaves.
    ranking = [
        {
            **{k: v for k, v in e.items() if k != "username"},
            "global_elo": e["rating"],
            "rank_pos": e["rank"],
        }
        for e in view["entries"]
    ]
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

    # La base y el Storage son síncronos: van a un hilo para no frenar el event loop, que en un
    # solo proceso (R18) atiende a todos los demás (R17).
    result = await asyncio.to_thread(
        _make_service(repo).submit_procedure,
        user["user_id"],
        item_id,
        item_content,
        image_data,
        mime,
        file_hash,
    )
    if result["outcome"] == REFUSE_SAME_ITEM:  # spec 001 FR-024k
        raise HTTPException(status_code=409, detail="Ya subiste este archivo para este ejercicio.")
    if result["outcome"] == REFUSE_OTHER_ITEM:  # spec 001 FR-024j
        raise HTTPException(status_code=409, detail="Este archivo pertenece a otro ejercicio.")
    submission_id = result["submission_id"]
    if result["outcome"] == COPY:  # spec 001 FR-024i: graded 0, never sent to the AI or review
        return ProcedureSubmitResponse(
            submission_id=submission_id,
            ai_score=None,
            ai_feedback=None,
            status="graded",
            is_copy=True,
            teacher_score=result["grading"]["grade"],
            elo_delta=result["grading"]["applied"],
        )

    if ai_proposed_score is not None:
        try:
            await asyncio.to_thread(
                repo.save_ai_proposed_score,
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


def _ai_score_in_range(value) -> float | None:
    """The AI's procedure score kept within 0-100; None when it gave no number."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    if score != score:  # NaN
        return None
    return max(0.0, min(100.0, score))


@router.get("/ai-status")
def ai_status():
    """Indica al frontend si el servidor tiene IA configurada (sin revelar keys)."""
    from api.config import settings
    from src.infrastructure.external_api.ai_client import detect_provider_from_key

    procedure_key = settings.get_ai_key("procedure")
    if not procedure_key:
        return {"available": False, "provider": None}
    # Spec 005 FR-010: the key's prefix is the provider (the interface says when it is not Groq).
    return {"available": True, "provider": detect_provider_from_key(procedure_key) or "unknown"}


def _pdf_first_page_png(pdf_bytes: bytes) -> bytes:
    """La primera página de un PDF como PNG a 200 dpi (lo que ve el modelo de visión)."""
    import fitz  # PyMuPDF

    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        return pdf_doc[0].get_pixmap(dpi=200).tobytes("png")
    finally:
        pdf_doc.close()


@router.post("/procedure/analyze", dependencies=[require_role("student")])
@limiter.limit(settings.rate_limit_review)
async def analyze_procedure(
    request: Request,
    user: CurrentUser,
    repo: RepoDep,
    item_id: str = Form(...),
    item_content: str = Form(default=""),
    api_key: str = Form(default=""),
    file: UploadFile = File(...),
):
    """Analiza un procedimiento con IA SIN PERSISTIR.

    Prioridad de API key: la del estudiante (si la envía) > la del sistema
    (env SYSTEM_AI_API_KEY). Solo Groq (revisión rigurosa con el modelo de visión; spec 005
    FR-014).
    """
    from api.config import settings

    effective_key = settings.get_ai_key("procedure", api_key)
    if not effective_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay API key de IA configurada. Pide al administrador que configure SYSTEM_AI_API_KEY.",
        )

    # Spec 005 FR-021: only a student enrolled in the exercise's course (403 before any provider).
    item = await asyncio.to_thread(repo.get_item_by_id, item_id)
    await require_enrolled_in_item(repo, user["user_id"], item)

    # Spec 005 FR-010, FR-014: the key's prefix decides; the review runs on Groq only, refused
    # before the upload is read.
    target = ai_target("procedure", effective_key)
    if target.provider != "groq":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=GROQ_ONLY)

    original_data, mime = await read_validated_upload(file)
    image_data = original_data
    file_hash = hashlib.sha256(original_data).hexdigest()

    # La revisión espera segundos al proveedor de IA. Todo lo bloqueante va a un hilo: en un solo
    # proceso (R18), esperar en el event loop congelaba cualquier otra petición (R17).
    if mime == "application/pdf":
        try:
            image_data = await asyncio.to_thread(_pdf_first_page_png, image_data)
            mime = "image/png"
        except Exception:
            logger.exception("Procedure review: the PDF could not be read")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se pudo leer el PDF. Sube una imagen o un PDF válido.",
            )

    from src.infrastructure.external_api.math_procedure_review import review_math_procedure

    # FR-016: fixed messages; the cause stays in the server log.
    try:
        review = await asyncio.to_thread(
            review_math_procedure,
            image_data,
            mime,
            api_key=target.api_key,
            question_content=item_content or "",
            model=target.model,
            timeout=target.timeout,
        )
    except ValueError:
        logger.warning("Procedure review: the model's answer was not valid JSON")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La IA devolvió una revisión que no se pudo leer. Intenta de nuevo.",
        )
    except TimeoutError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=TIMED_OUT)
    except ConnectionError:
        logger.exception("Procedure review: Groq could not be reached")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=UNAVAILABLE)
    except Exception:
        logger.exception("Procedure review failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=UNAVAILABLE)

    # Advisory and on a 0-100 scale: a value outside it (or not a number) is not shown as is.
    review["score_procedimiento"] = _ai_score_in_range(review.get("score_procedimiento"))
    return {
        "item_id": item_id,
        "provider": "groq",
        "review": review,
        "analysis_token": create_procedure_review_token(
            user["user_id"],
            item_id,
            file_hash,
            review["score_procedimiento"],
            review.get("evaluacion_global") or "",
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


# Seconds a submission may arrive after the time limit shown to the student (network and a
# browser's slowed timers); after that the session is closed (409).
EXAM_SUBMIT_GRACE_SECONDS = 30


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


# Spec 006 FR-020: exams are for students enrolled in the course, as practice (spec 001 FR-037).
_EXAM_STUDENTS = [require_role("student")]
_TAKEN = "Ya presentaste este examen."


@router.get(
    "/exam/templates", response_model=list[ExamTemplateSummary], dependencies=_EXAM_STUDENTS
)
def list_exam_templates_for_student(
    repo: RepoDep,
    user: CurrentUser,
    course_id: str = Query(..., min_length=1),
):
    """Plantillas de examen visibles a este estudiante en el curso.

    Filtrado por:
    - Plantilla NO archivada del curso indicado
    - Y: no tiene asignaciones (legacy/abierta) → visible a todos los inscritos
    -    O: hay una asignación al grupo del estudiante con ventana activa
    """
    _require_enrolment(_make_service(repo), user["user_id"], course_id)
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


@router.get("/exam/pending", response_model=list[PendingExam], dependencies=_EXAM_STUDENTS)
def list_pending_exams(repo: RepoDep, user: CurrentUser):
    """Plantillas pendientes para el estudiante en TODOS sus cursos inscritos.

    Assigned, open and not yet submitted (spec 006 FR-022); the exam screen lists them.
    """
    rows = repo.list_pending_exams_for_student(user_id=user["user_id"])
    return [PendingExam(**r) for r in rows]


@router.post("/exam/start", response_model=ExamStartResponse, dependencies=_EXAM_STUDENTS)
@limiter.limit(settings.rate_limit_exam_start)
def exam_start(request: Request, body: ExamStartRequest, user: CurrentUser, repo: RepoDep):
    """
    Inicia una sesión de examen.

    Modos:
      - Con `template_id`: usa exactamente los items de la plantilla del docente
        en el orden definido. Ignora n_questions y time_limit_minutes (toma los
        del template).
      - Sin `template_id`: examen estándar con curva de dificultad 30/40/30.

    En ambos casos, NO afecta el ELO del estudiante.
    """
    _require_enrolment(_make_service(repo), user["user_id"], body.course_id)
    # Spec 006 FR-023: sessions a day past their deadline are no longer needed.
    repo.expire_stale_exam_sessions()
    if body.template_id is not None:
        # FR-021: a template is graded once; standard exams stay unlimited.
        if repo.has_submitted_template(user["user_id"], body.template_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_TAKEN)
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
    # The student sees `time_limit_seconds`; the server accepts the submission a little longer,
    # because the answers leave the browser when its clock reaches zero and still have to arrive.
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=time_limit_seconds + EXAM_SUBMIT_GRACE_SECONDS
    )
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


@router.post("/exam/submit", response_model=ExamSubmitResponse, dependencies=_EXAM_STUDENTS)
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
    _require_enrolment(_make_service(repo), user["user_id"], run["course_id"])
    if body.course_id and body.course_id != run["course_id"]:
        raise HTTPException(status_code=400, detail="El curso no corresponde a la sesión.")
    if body.template_id is not None and body.template_id != run["template_id"]:
        raise HTTPException(status_code=400, detail="La plantilla no corresponde a la sesión.")
    if run["template_id"] is not None and repo.has_submitted_template(
        user["user_id"], run["template_id"]
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_TAKEN)

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
            # FR-024: an item removed after the start is reported and not counted.
            results.append(
                {
                    "item_id": ans.item_id,
                    "graded": False,
                    "is_correct": False,
                    "selected_option": ans.selected_option,
                    "elo_delta": 0.0,
                }
            )
            continue
        if ans.selected_option and ans.selected_option not in item_db["options"]:
            raise HTTPException(status_code=400, detail="Una opción seleccionada no es válida.")

        is_correct = ans.selected_option == item_db["correct_option"]
        if is_correct:
            correct_count += 1

        results.append(
            {
                "item_id": ans.item_id,
                "graded": True,
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
                "selected_option": ans.selected_option or None,  # spec 006 FR-033
            }
        )

    # Rating global actual (sin modificación): None mientras el diagnóstico está pendiente.
    graded = len(responses)
    if graded == 0:
        raise HTTPException(status_code=409, detail="Ninguna pregunta del examen sigue disponible.")
    score_pct = round(correct_count / graded * 100, 1)
    global_elo = _make_service(repo).ratings.ratings_view(user["user_id"])["overall"]
    result = {
        "results": results,
        "correct_count": correct_count,
        "total_questions": graded,
        "score_pct": score_pct,
        "global_elo_after": global_elo,
    }
    # FR-023: the course's own name, not the request's.
    course_name = next(
        (
            e["name"]
            for e in repo.get_user_enrollments(user["user_id"])
            if e["id"] == run["course_id"]
        ),
        run["course_id"],
    )
    saved = repo.complete_active_exam_session(
        body.session_id, user["user_id"], course_name, result, responses
    )
    if not saved:
        current = repo.get_active_exam_session(body.session_id, user["user_id"])
        if current and current.get("result") is not None:
            return ExamSubmitResponse(**current["result"])
        raise HTTPException(status_code=409, detail="La sesión de examen expiró.")
    return ExamSubmitResponse(**result)


@router.get("/exam/history", dependencies=_EXAM_STUDENTS)
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
    _require_enrolment(StudentService(repository=repo), user["user_id"], course_id)
    existing = repo.get_diagnostic(user["user_id"], course_id)
    if existing and not redo:
        stored = {
            **existing["result"],
            "initial_elo": existing["initial_elo"],
            "score_pct": existing["score_pct"],
        }
        return DiagnosticStatusResponse(
            completed=True,
            course_id=course_id,
            result=_diagnostic_result_view(repo, user["user_id"], course_id, stored),
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
    _require_enrolment(StudentService(repository=repo), user["user_id"], course_id)
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
        initialized = not repo.has_practice_attempts(user["user_id"], course_id, topic)
        if initialized:
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
                "outcome": "initialized" if initialized else "kept",  # FR-020c
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

    view = _diagnostic_result_view(repo, user["user_id"], course_id, result_payload)
    return DiagnosticResultResponse(
        initial_elo=initial_elo,
        score_pct=score_pct,
        league=league,
        themes=view["themes"],
        correct_total=correct_total,
        answered=answered,
        course_rating=view["course_rating"],
        outcome_summary=view["outcome_summary"],
    )


def _diagnostic_result_view(repo, user_id: int, course_id: str, result: dict) -> dict:
    """A diagnostic result as the screen shows it (spec 001 FR-020a–c, FR-031a): the course's
    current rating as the one figure, and that diagnostic's per-topic breakdown with each topic's
    initialized/kept mark and the outcome of them all. A result stored before the mark existed
    has none (`outcome` and `outcome_summary` None)."""
    themes = [{**theme, "outcome": theme.get("outcome")} for theme in result.get("themes", [])]
    outcomes = {theme["outcome"] for theme in themes}
    if not themes or None in outcomes:
        summary = None
    elif len(outcomes) == 1:
        summary = outcomes.pop()  # "initialized" or "kept"
    else:
        summary = "mixed"
    return {
        **result,
        "themes": themes,
        "outcome_summary": summary,
        "course_rating": StudentService(repository=repo).ratings.course_rating_view(
            user_id, course_id
        ),
    }


# ── Mapa de contenido ─────────────────────────────────────────────────────────

_MASTERY_ELO = 1250.0  # umbral para considerar un tópico "dominado"
_LESSON_EVENTS = {
    "node_viewed",
    "objectives_viewed",
    "math_convention_viewed",
    "node_completed",
}


# El estado de un nodo sin fila de progreso: lo que devuelve `get_lesson_progress`.
_NO_PROGRESS = "available"


def _lesson_states(repo, user_id: int, course_id: str):
    """`node_id -> estado guardado` de toda la materia en una sola lectura.

    Cada lectura del repositorio cuesta viajes de red a la base; leer nodo por nodo hacía que el
    mapa y las lecciones de N3 tardaran segundos en PostgreSQL.
    """
    states = repo.get_lesson_states(user_id, course_id)
    return lambda node_id: states.get(node_id, _NO_PROGRESS)


def _complete_hub_if_cards_opened(repo, user_id: int, course_id: str, hub: dict) -> None:
    """Spec 003 N3: a hub (`completion: "cards"`) completes once every card is opened. Also
    repairs progress recorded before the rule ran on the server for every hub."""
    if repo.get_lesson_progress(user_id, course_id, hub["node_id"])["state"] == "completed":
        return
    answered = repo.get_lesson_interactions(user_id, course_id, hub["node_id"])
    if hub.get("interactions") and not completion_gaps(hub, answered):
        repo.record_lesson_event(user_id, course_id, hub["node_id"], "node_completed")


def _lesson_with_progress(
    repo, user_id: int, course_id: str, lesson: dict, preview: bool = False
) -> dict:
    """Combina el catálogo con progreso, respetando el desbloqueo secuencial.

    Whether the node is open is decided by `node_access` (spec 003 L5) over the node's own data,
    the same function the map uses. In preview (spec 003 L1) every node is available and nothing
    is read or repaired for the viewer: the hub repair below writes progress.
    """
    # Spec 003 L2 (FR-020): the browser receives the allow-listed content, never a grading key.
    lesson = {**lesson, "content": public_content(lesson.get("content"))}
    if preview:
        return {
            **lesson,
            "course_id": course_id,
            "state": _NO_PROGRESS,
            "presentation": presentation_band(None),
            "explored_complex_branch": False,
            "progress": {"state": _NO_PROGRESS, "responses": {}},
            "preview": True,
        }
    for node in (lesson, get_lesson(lesson["unlock_after"]) if lesson.get("unlock_after") else None):
        if node and completes_on_cards(node):
            _complete_hub_if_cards_opened(repo, user_id, course_id, node)
    state_of = _lesson_states(repo, user_id, course_id)
    diagnostic = repo.get_diagnostic(user_id, course_id)
    presentation = presentation_band(diagnostic.get("score_pct") if diagnostic else None)
    refused = node_access(lesson, state_of, presentation)
    if refused:
        raise HTTPException(status_code=403, detail=refused)

    progress = repo.get_lesson_progress(user_id, course_id, lesson["node_id"])
    progress["responses"] = repo.get_lesson_interactions(
        user_id, course_id, lesson["node_id"]
    )
    # Spec 003 L4: the post-diagnostic outcome as the server stored it, or None.
    progress["outcome"] = repo.get_lesson_outcomes(user_id, course_id).get(lesson["node_id"])

    lesson_payload = {**lesson}
    if (lesson.get("content") or {}).get("machines"):
        # A hub that shows its nodes in order: each machine completed, current or blocked.
        content = {**lesson["content"]}
        machines = []
        previous_completed = True
        for machine in content["machines"]:
            machine_state = state_of(machine["node_id"])
            state = (
                "completed"
                if machine_state == "completed"
                else "current"
                if previous_completed
                else "blocked"
            )
            machines.append({**machine, "state": state})
            previous_completed = machine_state == "completed"
        content["machines"] = machines
        lesson_payload["content"] = content

    return {
        **lesson_payload,
        "course_id": course_id,
        "state": progress["state"],
        "presentation": presentation,
        "explored_complex_branch": explored_optional_branch(state_of),
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
    preview = _path_access(repo, user, course_id)

    return LessonDetailResponse(
        **_lesson_with_progress(repo, user["user_id"], course_id, lesson, preview)
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
    _refuse_preview(_path_access(repo, user, course_id))

    current = _lesson_with_progress(repo, user["user_id"], course_id, lesson)
    if body.event == "node_completed" and current["state"] != "completed":
        # One rule for every node (spec 003 L3, FR-030): its `completion` data. A node already
        # completed stays completed (FR-004), so the check only gates a first completion.
        answers = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        gaps = completion_gaps(lesson, answers)
        if gaps:
            raise HTTPException(status_code=409, detail=completion_refused(lesson, gaps))
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
    _refuse_preview(_path_access(repo, user, course_id))
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
    if completes_on_cards(lesson):
        _complete_hub_if_cards_opened(repo, user["user_id"], course_id, lesson)
    # Spec 003 L4 (FR-041): the answer that finishes the post-diagnostic stores its outcome.
    outcome = None
    if is_post_diagnostic(lesson, result["interaction_id"]):
        answers = repo.get_lesson_interactions(user["user_id"], course_id, node_id)
        outcome = post_diagnostic_outcome(lesson, answers)
        if outcome:
            repo.save_lesson_outcome(user["user_id"], course_id, node_id, **outcome)
    return LessonInteractionResponse(**result, outcome=outcome["outcome"] if outcome else None)


@router.get("/prealgebra-summary/{course_id}", response_model=PathSummaryResponse)
def prealgebra_summary(course_id: str, user: CurrentUser, repo: RepoDep):
    """Cierre diagnóstico (B13): agrega progreso y misconceptions del nivel.

    No afecta ELO. MVP: persiste/lee misconceptions de las interacciones y
    propone hasta 4 nodos de repaso. Sin panel docente todavía.
    """
    if course_id != PREALGEBRA_COURSE_ID:
        raise HTTPException(status_code=404, detail="Este curso no tiene ruta de aprendizaje")
    # One student's progress: a preview has none to summarise (the teacher's view is L4).
    _refuse_preview(_path_access(repo, user, course_id))
    state_of = _lesson_states(repo, user["user_id"], course_id)
    history = repo.get_lesson_answers(user["user_id"], course_id)
    summary = path_summary(
        state_of, lambda node_id: [a for a in history if a["node_id"] == node_id]
    )
    return {"course_id": course_id, **summary}


@router.get("/map/{course_id}", response_model=CourseMapResponse)
def course_map(course_id: str, user: CurrentUser, repo: RepoDep):
    """Mapa de contenido de una materia: un nodo por tópico, ordenados por
    dificultad, con el ELO/estado del estudiante (leído de student_topic_elo,
    incluye el ELO inicial del diagnóstico)."""
    if _path_access(repo, user, course_id):
        # Spec 003 L1 preview: every path node available; no rating rows (they are a student's).
        nodes = (
            [
                MapNode(**{**row, "state": "available"})
                for row in curriculum_map_rows(lambda _node: _NO_PROGRESS)
            ]
            if course_id == PREALGEBRA_COURSE_ID
            else []
        )
        course_name = next(
            (c["name"] for c in repo.get_courses() if c["id"] == course_id), course_id
        )
        return CourseMapResponse(
            course_id=course_id,
            course_name=course_name,
            diagnostic_done=False,
            nodes=nodes,
            preview=True,
        )
    items = repo.get_items_from_db(course_id=course_id)
    # This course's topic ratings only (spec 001, FR-029); an unrated topic has no rating.
    elo_map = {
        r["topic"]: {"elo": r["elo"], "rd": r["rd"], "approximate": r["approximate"]}
        for r in repo.get_course_topic_ratings(user["user_id"], course_id=course_id)
    }
    diagnostic = repo.get_diagnostic(user["user_id"], course_id)
    diagnostic_done = diagnostic is not None

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
    if course_id == PREALGEBRA_COURSE_ID:
        # Una sola lectura del progreso (`_lesson_states`). La ruta, sus estados y qué nodos
        # se muestran los decide el dominio con `node_access` sobre los datos de cada nodo
        # (spec 003 L5): el endpoint no sabe de nodos concretos.
        _state_of = _lesson_states(repo, user["user_id"], course_id)
        band = presentation_band(diagnostic.get("score_pct") if diagnostic else None)
        curriculum = [MapNode(**row) for row in curriculum_map_rows(_state_of, band=band)]

    # estado: dominado (>=umbral) = completed; el PRIMER nodo no dominado =
    # current (dónde reforzar); el resto = available. La práctica no depende de la
    # ruta (spec 001; spec 003 N4), así que la ruta no bloquea estos temas.
    current_idx = next((i for i, n in enumerate(raw) if not _mastered(n["elo"])), None)
    nodes = curriculum + [
        MapNode(
            topic=n["topic"],
            label=n["label"],
            elo=None if n["elo"] is None else round(n["elo"], 1),
            rd=None if n["rd"] is None else round(n["rd"], 1),
            approximate=elo_map.get(n["topic"], {}).get("approximate", False),
            item_count=n["item_count"],
            state=(
                "completed"
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

