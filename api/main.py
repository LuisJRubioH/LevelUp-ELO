"""
api/main.py
===========
Punto de entrada de la API FastAPI — LevelUp-ELO V2.0.

Ejecutar con:
    uvicorn api.main:app --reload --port 8000

La app Streamlit V1 puede seguir corriendo en paralelo (mismo PostgreSQL).
La migración es gradual: React → /api/*, Streamlit → legacy.

Endpoints base:
    GET /            → health check
    GET /api/docs    → Swagger UI
    GET /api/redoc   → ReDoc
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Path setup (ejecutar desde raíz del repo) ─────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.config import settings
from api.routers import admin, ai, auth, student, teacher
from api.websocket.notifications import ws_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la DB al arrancar y libera recursos al parar."""
    logger.info("=== LevelUp-ELO API v%s iniciando ===", settings.app_version)
    try:
        from api.dependencies import get_repository

        repo = get_repository()
        repo.init_db()
        logger.info("Base de datos inicializada.")
    except Exception as exc:
        logger.error("Error inicializando DB: %s", exc)

    yield

    logger.info("=== LevelUp-ELO API detenida ===")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="LevelUp-ELO API",
    description=(
        "API REST + WebSocket para la plataforma educativa adaptativa LevelUp-ELO. "
        "Motor ELO vectorial, tutoría socrática KatIA, revisión de procedimientos con IA."
    ),
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(student.router, prefix="/api")
app.include_router(teacher.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(ws_router, prefix="/api")


# ── Health check ──────────────────────────────────────────────────────────────


@app.get("/", tags=["health"])
def root():
    return {
        "service": "LevelUp-ELO API",
        "version": settings.app_version,
        "status": "ok",
        "docs": "/api/docs",
    }


@app.get("/api/health", tags=["health"])
def health():
    """Health check detallado: verifica conectividad con la DB."""
    try:
        from api.dependencies import get_repository

        repo = get_repository()
        conn = repo.get_connection()
        if hasattr(repo, "put_connection"):
            repo.put_connection(conn)
        else:
            conn.close()
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "version": settings.app_version,
    }
