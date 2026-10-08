"""
api/routers/meta.py
===================
Public reference data. GET /api/meta/ranks — the single 16-level rank scale (spec 001, FR-031).
"""

from fastapi import APIRouter, Request, Response

from api.config import settings
from api.rate_limit import limiter
from src.application.services.rating_read_service import rank_scale

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/ranks")
@limiter.limit(settings.rate_limit_default)
def ranks(request: Request, response: Response):
    """The rank scale, ascending: [{label, min}]. No authentication; static, so cacheable."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    return rank_scale()
