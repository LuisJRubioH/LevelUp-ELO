"""
src/interface/streamlit/app.py
==============================
Punto de entrada de la aplicación — routing puro por rol.
Responsabilidad: configuración inicial, DB, servicios, IA, cookies y routing.
Las vistas viven en views/ y los helpers en state.py / assets.py.
"""

import os
import sys
import time

# Parche para resolver imports desde la raíz del proyecto
# DEBE ir antes de cualquier import de src.*
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.__version__ import __version__

print(f"[APP VERSION] LevelUp-ELO v{__version__}")

from src.infrastructure.logging_config import configure_logging, get_logger

configure_logging(level="INFO")
_app_logger = get_logger(__name__)

import streamlit as st
import extra_streamlit_components as stx

import src.infrastructure.persistence.sqlite_repository as db_mod
import src.infrastructure.persistence.postgres_repository as pg_mod
import src.infrastructure.external_api.ai_client as ai_mod

SQLiteRepository = db_mod.SQLiteRepository
PostgresRepository = pg_mod.PostgresRepository

# ── Configuración de página (debe ser la primera llamada a st) ─────────────────
st.set_page_config(
    page_title="LevelUp ELO — Evaluación Adaptativa",
    layout="wide",
    page_icon="🎓",
)

# ── CSS global ────────────────────────────────────────────────────────────────
from src.interface.streamlit.assets import apply_global_css

apply_global_css()

# ── Base de datos ─────────────────────────────────────────────────────────────
if "db" not in st.session_state:
    if os.environ.get("DATABASE_URL"):
        try:
            st.session_state.db = PostgresRepository()
        except RuntimeError as _db_err:
            st.error(f"Error al conectar con la base de datos: {_db_err}")
            st.stop()
    else:
        st.session_state.db = SQLiteRepository()

repo = st.session_state.db

# ── Cookie manager (almacenado en session_state para logout()) ─────────────────
cookie_manager = stx.CookieManager()
st.session_state["_cookie_manager"] = cookie_manager

# ── Servicios de aplicación ───────────────────────────────────────────────────
import src.application.services.student_service as ss_mod
import src.application.services.teacher_service as ts_mod

if "student_service" not in st.session_state:
    st.session_state.student_service = ss_mod.StudentService(
        st.session_state.db,
        enable_cognitive_modifier=False,
    )
if "teacher_service" not in st.session_state:
    st.session_state.teacher_service = ts_mod.TeacherService(st.session_state.db)

# ── Configuración de IA ───────────────────────────────────────────────────────
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "Rápido (Flash)"
if "model_cog" not in st.session_state:
    st.session_state.model_cog = "google/gemma-3-4b"
if "model_analysis" not in st.session_state:
    st.session_state.model_analysis = "mistralai/mistral-7b-instruct-v0.3"
if "ai_url" not in st.session_state:
    st.session_state.ai_url = ""
if "ai_provider_mode" not in st.session_state:
    st.session_state.ai_provider_mode = "auto"
if "lmstudio_models" not in st.session_state:
    st.session_state.lmstudio_models = []
if "cloud_api_key" not in st.session_state:
    st.session_state.cloud_api_key = None


@st.cache_resource
def _get_cached_ai_client(lmstudio_url: str):
    """Detecta el backend de IA UNA SOLA VEZ por URL para toda la instancia."""
    return ai_mod.get_ai_client(lmstudio_url)


if "ai_available" not in st.session_state:
    _client = _get_cached_ai_client(st.session_state.ai_url)
    st.session_state.ai_available = _client.is_available
    st.session_state.ai_provider = _client.provider
    st.session_state.cloud_api_key = _client.api_key
    if _client.provider == "lmstudio":
        st.session_state.lmstudio_models = _client.models
        _best = ai_mod.select_best_model(_client.models)
        if _best:
            st.session_state.model_cog = _best
            st.session_state.model_analysis = _best
    elif _client.provider:
        _pinfo = ai_mod.PROVIDERS.get(_client.provider, {})
        if _pinfo.get("model_cog"):
            st.session_state.model_cog = _pinfo["model_cog"]
        if _pinfo.get("model_analysis"):
            st.session_state.model_analysis = _pinfo["model_analysis"]

# ── Estado inicial de sesión ──────────────────────────────────────────────────
if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None

if "bank_synced_v12" not in st.session_state:
    st.session_state["bank_synced_v12"] = True

# ── Restauración de sesión por cookie ─────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    token = cookie_manager.get("elo_auth_token")
    if token:
        user = repo.validate_session(token)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user["id"]
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            if "session_start_time" not in st.session_state:
                st.session_state.session_start_time = time.time()
        else:
            cookie_manager.delete("elo_auth_token")

# ── Versión en sidebar (visible en todas las vistas autenticadas) ─────────────
with st.sidebar:
    st.caption(f"LevelUp-ELO v{__version__}")

# ── Routing por rol ───────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    from src.interface.streamlit.views.auth_view import render_auth

    render_auth(cookie_manager)
else:
    _role = st.session_state.get("role")
    if _role == "admin":
        from src.interface.streamlit.views.admin_view import render_admin

        render_admin()
    elif _role == "teacher":
        from src.interface.streamlit.views.teacher_view import render_teacher

        render_teacher()
    else:
        from src.interface.streamlit.views.student_view import render_student

        render_student()
