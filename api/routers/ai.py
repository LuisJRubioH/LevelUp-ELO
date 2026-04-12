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
    from src.infrastructure.external_api.ai_client import get_socratic_guidance

    # Construcción del contexto del ítem
    item_context = {
        "content": body.item_content,
        "id": body.item_id,
    }

    async def _generate() -> AsyncGenerator[str, None]:
        try:
            # get_socratic_guidance es síncrono → ejecutar en threadpool
            import asyncio
            from functools import partial

            loop = asyncio.get_event_loop()
            full_text = await loop.run_in_executor(
                None,
                partial(
                    get_socratic_guidance,
                    body.student_message,
                    item_context,
                    body.api_key,
                    body.provider,
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
                    None,  # item_topic
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
    api_key: str,
    user: CurrentUser,
    repo: RepoDep,
):
    """
    Revisa un procedimiento manuscrito con IA (Groq + Llama 4 Scout).

    Retorna:
    - transcripcion: texto extraído
    - pasos: lista de pasos evaluados
    - score_procedimiento: 0–100
    - errores_detectados: lista de errores
    - evaluacion_global: texto de evaluación
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "application/pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no soportado. Usa JPG, PNG, WebP o PDF.",
        )

    MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Archivo demasiado grande (máx 10 MB).",
        )

    try:
        from src.infrastructure.external_api.math_procedure_review import review_math_procedure

        result = review_math_procedure(contents, file.content_type, api_key)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en la revisión de IA: {exc}",
        ) from exc
