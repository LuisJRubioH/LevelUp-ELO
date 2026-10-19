"""
api/routers/ai.py
=================
Endpoints de IA:
  POST /ai/socratic          → respuesta socrática (SSE streaming)
  POST /ai/review-procedure  → revisión de procedimiento manuscrito (multipart)
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse

from api.ai_target import TIMED_OUT, UNAVAILABLE, ai_target
from api.dependencies import CurrentUser, RepoDep
from api.schemas.student import SocraticRequest
from api.config import settings
from api.rate_limit import limiter
from api.upload_validation import read_validated_upload

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger("api.ai")

# `_call_ai_api` reports a provider failure as text ("ERROR_401: …", "❌ Error …"), not as an
# exception. That text is not KatIA speaking: it is neither streamed as her reply nor saved.
_PROVIDER_ERROR_PREFIXES = ("ERROR_", "❌")
_KATIA_UNAVAILABLE = "KatIA no pudo responder ahora. Intenta de nuevo en un momento."


def _is_provider_error(text: str | None) -> bool:
    return not (text or "").strip() or text.lstrip().startswith(_PROVIDER_ERROR_PREFIXES)


# ── Chat socrático (SSE) ──────────────────────────────────────────────────────


@router.post("/socratic")
@limiter.limit(settings.rate_limit_socratic)
async def socratic(request: Request, body: SocraticRequest, user: CurrentUser, repo: RepoDep):
    """
    Respuesta socrática de KatIA como Server-Sent Events (streaming).

    El cliente recibe tokens en tiempo real via EventSource:
        data: {"token": "..."}
        data: {"done": true, "full_text": "..."}

    La API key viaja en el body (nunca se persiste).
    """
    from api.config import settings
    from src.application.services.rating_read_service import RatingReadService
    from src.infrastructure.external_api.ai_client import get_socratic_guidance

    effective_key = settings.get_ai_key("katia", body.api_key or "")

    if not effective_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay API key de IA configurada para KatIA.",
        )

    # Obtener datos del ítem desde DB (correct_option nunca viaja al frontend)
    # A worker thread, not the event loop: the repository is synchronous (spec 002 FR-024).
    item_db = await asyncio.to_thread(repo.get_item_by_id, body.item_id)
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem {body.item_id} no encontrado.",
        )

    correct_answer = item_db.get("correct_option", "")
    all_options = item_db.get("options", [])
    if isinstance(all_options, str):
        import json as _json

        try:
            all_options = _json.loads(all_options)
        except Exception:
            all_options = []
    topic = item_db.get("topic", body.course_id or "")

    # Rating global del estudiante (None mientras el diagnóstico está pendiente).
    student_rating = RatingReadService(repo).ratings_view(user["user_id"])["overall"]

    # Spec 005 FR-010 … FR-013: the key's prefix picks the provider, settings the model.
    target = ai_target("katia", effective_key)

    # The provider answers in one piece; it is called before the stream starts, so a failure is
    # a 502/503 with a fixed message, never a 200 (FR-016, US2-AS3).
    try:
        full_text = await asyncio.to_thread(
            get_socratic_guidance,
            student_rating,
            topic,
            body.item_content,
            body.student_message,
            correct_answer,
            all_options,
            target.base_url,
            target.model,
            target.api_key,
            target.provider,
            body.lang,
            timeout=target.timeout,
        )
    except TimeoutError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=TIMED_OUT)
    except ConnectionError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=UNAVAILABLE)
    except Exception:
        # The detail stays in the server log; the student gets a plain message.
        logger.exception("KatIA: socratic reply failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=_KATIA_UNAVAILABLE)
    if _is_provider_error(full_text):
        logger.warning("KatIA: provider %s failed", target.provider)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=_KATIA_UNAVAILABLE)

    await asyncio.to_thread(
        repo.save_katia_interaction,
        user["user_id"],
        body.course_id,
        body.item_id,
        topic,
        body.student_message,
        full_text,
    )

    async def _generate() -> AsyncGenerator[str, None]:
        # Streaming simulado token a token (palabras): el proveedor ya respondió completo.
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield f"data: {json.dumps({'done': True, 'full_text': full_text})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # deshabilita buffering en nginx
        },
    )


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
        logger.exception("Legacy procedure review failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=UNAVAILABLE
        ) from exc
