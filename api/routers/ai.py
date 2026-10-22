"""
api/routers/ai.py
=================
Endpoints de IA:
  POST /ai/socratic          → respuesta socrática (SSE streaming)

La revisión de procedimientos es POST /student/procedure/analyze (spec 005 K4 retiró el antiguo
/ai/review-procedure).
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from api.ai_target import TIMED_OUT, UNAVAILABLE, ai_target, require_enrolled_in_item
from api.dependencies import CurrentUser, RepoDep, require_role
from api.katia_record import classify_closed
from api.schemas.student import SocraticRequest
from api.config import settings
from api.rate_limit import limiter
from src.domain.katia.conversation import HISTORY_TURNS, STALE_AFTER_HOURS
from src.domain.katia.guardrail import GUIDING_QUESTION, check_reply

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger("api.ai")

# `_call_ai_api` reports a provider failure as text ("ERROR_401: …", "❌ Error …"), not as an
# exception. That text is not KatIA speaking: it is neither streamed as her reply nor saved.
_PROVIDER_ERROR_PREFIXES = ("ERROR_", "❌")
_KATIA_UNAVAILABLE = "KatIA no pudo responder ahora. Intenta de nuevo en un momento."


def _is_provider_error(text: str | None) -> bool:
    return not (text or "").strip() or text.lstrip().startswith(_PROVIDER_ERROR_PREFIXES)


# ── Chat socrático (SSE) ──────────────────────────────────────────────────────


@router.post("/socratic", dependencies=[require_role("student")])
@limiter.limit(settings.rate_limit_socratic)
async def socratic(
    request: Request,
    body: SocraticRequest,
    user: CurrentUser,
    repo: RepoDep,
    background_tasks: BackgroundTasks,
):
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

    # Spec 005 FR-021: only a student enrolled in the item's course (403 before any provider).
    await require_enrolled_in_item(repo, user["user_id"], item_db)

    correct_answer = item_db.get("correct_option", "")
    all_options = item_db.get("options", [])
    if isinstance(all_options, str):
        import json as _json

        try:
            all_options = _json.loads(all_options)
        except Exception:
            all_options = []
    topic = item_db.get("topic", body.course_id or "")
    # FR-020: the statement as stored, never the client's; the option the student chose, if it
    # is one of the item's.
    statement = item_db.get("content", "")
    selected = body.selected_option if body.selected_option in all_options else None

    # Rating global del estudiante (None mientras el diagnóstico está pendiente), off the loop.
    student_rating = (
        await asyncio.to_thread(RatingReadService(repo).ratings_view, user["user_id"])
    )["overall"]

    # Spec 005 FR-010 … FR-013: the key's prefix picks the provider, settings the model.
    target = ai_target("katia", effective_key)

    # K3 (FR-030 … FR-032): conversations silent for 24 hours close as «abandonado» and lose
    # their text; then this message joins the student's open conversation about the item, whose
    # last turns go to the provider as context.
    stale = await asyncio.to_thread(repo.expire_stale_katia_conversations, STALE_AFTER_HOURS)
    background_tasks.add_task(classify_closed, repo, stale)
    conversation = await asyncio.to_thread(
        repo.open_katia_conversation,
        user["user_id"],
        item_db.get("course_id") or body.course_id,
        body.item_id,
        topic,
        HISTORY_TURNS,
    )

    # The provider answers in one piece; it is called before the stream starts, so a failure is
    # a 502/503 with a fixed message, never a 200 (FR-016, US2-AS3).
    try:
        full_text = await asyncio.to_thread(
            get_socratic_guidance,
            student_rating,
            topic,
            statement,
            body.student_message,
            selected,
            all_options,
            target.base_url,
            target.model,
            target.api_key,
            target.provider,
            body.lang,
            timeout=target.timeout,
            history=conversation["history"],
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

    # FR-022: a reply that names the correct option, announces a solution or runs past three
    # sentences is replaced by a guiding question, and is not recorded as KatIA's: the turn keeps
    # only the student's message.
    if not check_reply(full_text, correct_answer):
        logger.info("KatIA: a reply was replaced by the guiding question")
        full_text = None
    await asyncio.to_thread(
        repo.record_katia_turn, conversation["id"], body.student_message, full_text
    )
    full_text = full_text or GUIDING_QUESTION

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
