"""
api/routers/ai.py
=================
Endpoints de IA:
  POST /ai/socratic          → KatIA's reply as SSE (spec 005)
  POST /ai/review-procedure  → revisión de procedimiento manuscrito (multipart)
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse

from api.dependencies import CurrentUser, RepoDep
from api.schemas.student import SocraticRequest
from api.config import settings
from api.rate_limit import limiter
from api.upload_validation import read_validated_upload
from src.application.interfaces.tutor import TutorUnavailable
from src.application.services.katia_service import KatiaRefused, KatiaService
from src.application.services.rating_read_service import RatingReadService
from src.infrastructure.external_api.katia_tutor import ProviderTutor, RouteError, resolve_route

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger("api.ai")

_KATIA_UNAVAILABLE = "KatIA no pudo responder ahora. Intenta de nuevo en un momento."

# Every refusal is decided before the stream starts (research R9). The chat translates by code.
_REFUSALS = {
    "item_not_found": (status.HTTP_404_NOT_FOUND, "Ese ejercicio no existe."),
    "not_enrolled": (status.HTTP_403_FORBIDDEN, "No estás inscrito en el curso de este ejercicio."),
    "exam_active": (
        status.HTTP_403_FORBIDDEN,
        "KatIA no está disponible para las preguntas de un examen en curso.",
    ),
    "not_served": (
        status.HTTP_409_CONFLICT,
        "KatIA ayuda con la pregunta que estás practicando. Pide la siguiente pregunta.",
    ),
    "message_too_long": (422, "Tu mensaje es demasiado largo. Escribe una pregunta más corta."),
    "katia_not_configured": (422, "KatIA no tiene una API key de IA configurada."),
    "unknown_provider": (422, "No reconocemos el proveedor de tu API key."),
    "katia_unavailable": (status.HTTP_503_SERVICE_UNAVAILABLE, _KATIA_UNAVAILABLE),
}


def _refusal(code: str) -> HTTPException:
    status_code, message = _REFUSALS[code]
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def make_tutor(route, api_key: str, max_tokens: int) -> ProviderTutor:
    """The model client for one request (tests replace it with a fake)."""
    return ProviderTutor(route, api_key, max_tokens)


def _events(events: list[dict]) -> StreamingResponse:
    async def stream():
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Chat socrático (SSE) ──────────────────────────────────────────────────────


@router.post("/socratic")
@limiter.limit(settings.rate_limit_socratic)
async def socratic(request: Request, body: SocraticRequest, user: CurrentUser, repo: RepoDep):
    """KatIA's reply to one message, as Server-Sent Events (spec 005, contracts/api.md).

        data: {"token": "..."}            the reply, word by word
        data: {"done": true, "full_text": "..."}
        data: {"error": "..."}            the model failed; nothing was stored

    The key the request carries is the student's own and is never stored.
    """
    own_key = (body.api_key or "").strip()
    api_key = settings.get_ai_key("katia", own_key)
    if not api_key:
        raise _refusal("katia_not_configured")
    try:
        route = resolve_route(
            api_key,
            own_key=bool(own_key),
            configured_provider=settings.system_ai_provider,
            requested_provider=body.provider,
        )
    except RouteError as error:
        if own_key:
            raise _refusal("unknown_provider")
        # The reason only: never the key (FR-028, FR-030).
        logger.error("KatIA: the system provider configuration is not usable (%s)", error.code)
        raise _refusal("katia_unavailable")

    limits = settings.katia_limits()
    service = KatiaService(repo, make_tutor(route, api_key, limits.max_output_tokens), limits)

    def reply():
        level = RatingReadService(repo).ratings_view(user["user_id"])["overall"]
        return service.reply(user["user_id"], body.item_id, body.student_message, body.lang, level)

    try:
        katia = await asyncio.to_thread(reply)
    except KatiaRefused as refused:
        raise _refusal(refused.code)
    except TutorUnavailable as failure:
        logger.warning("KatIA: no reply from %s (%s)", route.provider, failure.code)
        return _events([{"error": _KATIA_UNAVAILABLE}])
    except Exception:
        # The detail stays in the server log; the student gets a plain message.
        logger.exception("KatIA: socratic reply failed")
        return _events([{"error": _KATIA_UNAVAILABLE}])

    words = katia.text.split(" ")
    tokens = [{"token": w + (" " if i < len(words) - 1 else "")} for i, w in enumerate(words)]
    return _events(tokens + [{"done": True, "full_text": katia.text}])


# ── Revisión de procedimientos ────────────────────────────────────────────────


@router.post("/review-procedure")
@limiter.limit(settings.rate_limit_review)
async def review_procedure(
    request: Request,
    file: UploadFile,
    item_id: str = Form(...),
    api_key: str = Form(default=""),
    user: CurrentUser = None,
    repo: RepoDep = None,
):
    """
    Revisa un procedimiento manuscrito con IA (Groq + Llama 4 Scout).

    La API key se resuelve por prioridad: usuario > AI_KEY_PROCEDURE > SYSTEM_AI_API_KEY.
    """
    from api.config import settings

    effective_key = settings.get_ai_key("procedure", api_key)
    if not effective_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay API key de IA configurada.",
        )

    contents, mime = await read_validated_upload(file)

    try:
        from src.infrastructure.external_api.math_procedure_review import review_math_procedure

        result = review_math_procedure(contents, mime, effective_key)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en la revisión de IA: {exc}",
        ) from exc
