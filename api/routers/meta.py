"""
api/routers/meta.py
===================
Public reference data. GET /api/meta/ranks — the single 16-level rank scale (spec 001, FR-031).
"""

from fastapi import APIRouter, Request

from api.config import settings
from api.rate_limit import limiter
from src.application.services.rating_read_service import rank_scale

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/ranks")
@limiter.limit(settings.rate_limit_default)
def ranks(request: Request):
    """The rank scale, ascending: [{label, min}]. No authentication."""
    return rank_scale()
