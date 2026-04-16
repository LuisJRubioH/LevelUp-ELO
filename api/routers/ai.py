"""
api/routers/ai.py
=================
Endpoints de IA:
  POST /ai/socratic          → respuesta socrática (SSE streaming)
  POST /ai/review-procedure  → revisión de procedimiento manuscrito (multipart)
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from api.dependencies import CurrentUser, RepoDep
from api.schemas.student import SocraticRequest

router = APIRouter(prefix="/ai", tags=["ai"])


# ── Chat socrático (SSE) ──────────────────────────────────────────────────────


@router.post("/socratic")
async def socratic(body: SocraticRequest, user: CurrentUser, repo: RepoDep):
    """
    Respuesta socrática de KatIA como Server-Sent Events (streaming).

    El cliente recibe tokens en tiempo real via EventSource:
        data: {"token": "..."}
        data: {"done": true, "full_text": "..."}

    La API key viaja en el body (nunca se persiste).
    """
    from api.config import settings
    from api.dependencies import build_vector_rating
    from src.domain.elo.vector_elo import aggregate_global_elo
    from src.infrastructure.external_api.ai_client import (
        detect_provider_from_key,
        get_socratic_guidance,
        PROVIDERS,
    )

    effective_key = settings.get_ai_key("katia", body.api_key or "")

    if not effective_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay API key de IA configurada para KatIA.",
        )

    # Obtener datos del ítem desde DB (correct_option nunca viaja al frontend)
    item_db = repo.get_item_by_id(body.item_id)
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

    # ELO global del estudiante
    vector = build_vector_rating(user["user_id"], repo)
    student_rating = aggregate_global_elo(vector)

    # Resolver proveedor y modelo
    provider = body.provider or ""
    if not provider and effective_key:
        provider = detect_provider_from_key(effective_key) or "groq"
    prov_cfg = PROVIDERS.get(provider, PROVIDERS.get("groq", {}))
    base_url = prov_cfg.get("base_url", "") or ""
    model_name = prov_cfg.get("model_cog", "") or ""

    async def _generate() -> AsyncGenerator[str, None]:
        try:
            import asyncio
            from functools import partial

            loop = asyncio.get_event_loop()
            full_text = await loop.run_in_executor(
                None,
                partial(
                    get_socratic_guidance,
                    student_rating,
                    topic,
                    body.item_content,
                    body.student_message,
                    correct_answer,
                    all_options,
                    base_url,
                    model_name,
                    effective_key,
                    provider,
                ),
            )

            # Simular streaming token a token (dividir en palabras)
            words = (full_text or "").split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'token': chunk})}\n\n"

            # Guardar interacción en DB
            await loop.run_in_executor(
                None,
                partial(
                    repo.save_katia_interaction,
                    user["user_id"],
                    body.course_id,
                    body.item_id,
                    topic,
                    body.student_message,
                    full_text or "",
                ),
            )

            yield f"data: {json.dumps({'done': True, 'full_text': full_text})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

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
async def review_procedure(
    file: UploadFile,
    item_id: str,
    api_key: str = "",
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

    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "application/pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no soportado. Usa JPG, PNG, WebP o PDF.",
        )

    MAX_SIZE = 10 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Archivo demasiado grande (máx 10 MB).",
        )

    try:
        from src.infrastructure.external_api.math_procedure_review import review_math_procedure

        result = review_math_procedure(contents, file.content_type, effective_key)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en la revisión de IA: {exc}",
        ) from exc
