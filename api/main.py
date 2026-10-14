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

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# ── Path setup (ejecutar desde raíz del repo) ─────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.config import settings
from api.rate_limit import LimitsUnavailable, limiter, limits_state
from api.routers import admin, ai, auth, meta, student, teacher
from api.websocket.notifications import ws_router
from api.websocket.pvp import pvp_router

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
        settings.validate_runtime()
        from api.dependencies import get_repository

        from api.websocket.notifications import bind_event_loop

        bind_event_loop(asyncio.get_running_loop())
        repo = get_repository()
        # El esquema NO se aplica aquí: en despliegue lo hace scripts/migrate.py
        # antes de arrancar uvicorn, con RUN_MIGRATIONS=0 en este proceso.
        # Ver _bootstrap_schema() y el startCommand de render.yaml.
        logger.info("Repositorio listo (%s).", type(repo).__name__)
    except Exception as exc:
        logger.exception("No se pudo preparar el arranque: %s", exc)
        raise

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
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


_LIMITS_UNAVAILABLE = "El servicio no puede aplicar sus límites ahora. Inténtalo en un minuto."


async def _limits_unavailable_handler(request, exc):
    """Spec 004 FR-095: with no way to count a limit, the limited request is refused."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": _LIMITS_UNAVAILABLE},
        headers={"Retry-After": "60"},
    )


app.add_exception_handler(LimitsUnavailable, _limits_unavailable_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Estáticos: imágenes de items del banco ────────────────────────────────────
# An item's `image_url` is a path under items/ (items/images/… or items/assets/…); the screens
# request it from the API as written.
_IMAGES_DIR = os.path.join(_ROOT, "items", "images")
if os.path.isdir(_IMAGES_DIR):
    app.mount("/items/images", StaticFiles(directory=_IMAGES_DIR), name="item-images")
_ASSETS_DIR = os.path.join(_ROOT, "items", "assets")
if os.path.isdir(_ASSETS_DIR):
    app.mount("/items/assets", StaticFiles(directory=_ASSETS_DIR), name="item-assets")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(student.router, prefix="/api")
app.include_router(teacher.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(meta.router, prefix="/api")
app.include_router(ws_router, prefix="/api")
app.include_router(pvp_router, prefix="/api")


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
    """Readiness: la base y los límites (constitución 1.1.0; spec 004 FR-094).

    503 si la base falla o si los límites no se pueden aplicar; 200 si no, con `limits` en
    "normal" o "degraded" (contando en memoria porque el almacén compartido no responde). Los
    monitores deben leer el cuerpo, no solo el código. Sin direcciones internas ni credenciales.
    """
    try:
        from api.dependencies import get_repository

        repo = get_repository()
        conn = repo.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            if cursor.fetchone() is None:
                raise RuntimeError("La consulta de readiness no devolvió resultado")
        finally:
            if hasattr(repo, "put_connection"):
                repo.put_connection(conn)
            else:
                conn.close()
    except Exception as exc:
        logger.error("Readiness de base de datos falló: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible.",
        ) from exc

    try:
        limits = limits_state()
    except Exception as exc:
        logger.error("Readiness de los límites falló: %s", type(exc).__name__)
        limits = "unavailable"
    if limits == "unavailable":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Límites no disponibles.",
        )

    return {
        "status": "ok" if limits == "normal" else "degraded",
        "db": "ok",
        "limits": limits,
        "version": settings.app_version,
    }
