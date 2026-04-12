import streamlit as st
import os
import sys

print("[APP VERSION] 2026-03-23-v3")

# Parche para resolver imports desde la raíz del proyecto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if base_path not in sys.path:
    sys.path.append(base_path)

from src.infrastructure.logging_config import configure_logging, get_logger
configure_logging(level="INFO")
_app_logger = get_logger(__name__)

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import requests
import json
import random
try:
    from psycopg2.extras import RealDictCursor
except ImportError:
    RealDictCursor = None
import src.infrastructure.persistence.sqlite_repository as db_mod
import src.infrastructure.persistence.postgres_repository as pg_mod
import src.infrastructure.external_api.ai_client as ai_mod
import src.infrastructure.external_api.math_procedure_review as _math_review_mod
import src.infrastructure.external_api.model_router as _router_mod
import src.infrastructure.external_api.math_analysis_pipeline as _pipeline_mod

from src.domain.elo.vector_elo import VectorRating, aggregate_global_elo, aggregate_global_rd
from src.domain.elo.model import expected_score, calculate_dynamic_k, Item
from src.domain.entities import LEVEL_TO_BLOCK
from src.domain.katia.katia_messages import (
    get_random_message, get_streak_message, get_procedure_comment,
    MENSAJES_BIENVENIDA, MENSAJES_DESPEDIDA,
)
from src.utils import strip_thinking_tags
SQLiteRepository = db_mod.SQLiteRepository
PostgresRepository = pg_mod.PostgresRepository
analyze_performance_local = ai_mod.analyze_performance_local
get_active_models = ai_mod.get_active_models
get_socratic_guidance_stream = ai_mod.get_socratic_guidance_stream
get_katia_chat_stream = ai_mod.get_katia_chat_stream
analyze_procedure_image = ai_mod.analyze_procedure_image
validate_procedure_relevance = ai_mod.validate_procedure_relevance
_model_supports_vision = ai_mod._model_supports_vision
review_math_procedure = _math_review_mod.review_math_procedure
apply_procedure_elo_adjustment = _math_review_mod.apply_procedure_elo_adjustment
select_model_for_task = _router_mod.select_model_for_task
validate_socratic_response = _router_mod.validate_socratic_response
math_pipeline_analyze = _pipeline_mod.analyze_with_llm_data
import time
import extra_streamlit_components as stx
from streamlit.components.v1 import html as st_html


_TIMER_ID_COUNTER = [0]  # mutable counter for unique timer IDs

def _render_live_timer(start_epoch: float, label: str = "",
                       font_size: str = "1.1rem", height: int = 40,
                       color: str = "#FFD700", bold: bool = True,
                       align: str = "right"):
    """Renderiza un temporizador en tiempo real usando JavaScript puro.

    El timer corre segundo a segundo sin necesidad de rerun de Streamlit.
    """
    _TIMER_ID_COUNTER[0] += 1
    _tid = f"tmr_{_TIMER_ID_COUNTER[0]}"
    _w = "font-weight:700;" if bold else ""
    _html = f"""
    <style>
      body {{ margin:0; padding:0; background:transparent; overflow:hidden; }}
    </style>
    <div style="text-align:{align};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <span style="color:{color};font-size:{font_size};{_w}letter-spacing:0.5px;">
        {label}<span id="{_tid}">0:00</span>
      </span>
    </div>
    <script>
    (function() {{
      var start = {start_epoch} * 1000;
      var el = document.getElementById('{_tid}');
      function tick() {{
        var diff = Math.floor((Date.now() - start) / 1000);
        if (diff < 0) diff = 0;
        var h = Math.floor(diff / 3600);
        var m = Math.floor((diff % 3600) / 60);
        var s = diff % 60;
        if (h > 0) {{
          el.textContent = h + 'h ' + String(m).padStart(2,'0') + 'm ' + String(s).padStart(2,'0') + 's';
        }} else if (m > 0) {{
          el.textContent = m + ':' + String(s).padStart(2,'0');
        }} else {{
          el.textContent = s + 's';
        }}
      }}
      tick();
      setInterval(tick, 1000);
    }})();
    </script>
    """
    st_html(_html, height=height)


# Configuración de página
st.set_page_config(page_title="LevelUp ELO — Evaluación Adaptativa", layout="wide", page_icon="🎓")

# ── CSS: radio button seleccionado en verde ──────────────────────────────────
st.markdown("""
<style>
/* Streamlit 1.55+ radio: the selected indicator circle */
div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
/* Fallback: target the SVG-based radio indicator */
div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"],
div[data-testid="stRadio"] [role="radiogroup"] label div:first-child div {
    border-color: inherit;
}
div[data-testid="stRadio"] [role="radiogroup"] label[aria-checked="true"] div:first-child div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
/* Streamlit emotion-cache based radio dot */
div[data-testid="stRadio"] [role="radiogroup"] label[aria-checked="true"] > div:first-child > div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
div[data-testid="stRadio"] [role="radiogroup"] label[aria-checked="true"] > div:first-child {
    border-color: #00CC66 !important;
}
/* Target the Streamlit primary color variable override */
div[data-testid="stRadio"] {
    --primary-color: #00CC66;
}
/* BaseWeb radio overrides */
[data-baseweb="radio"] input[type="radio"]:checked ~ div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
[data-baseweb="radio"] input[type="radio"]:checked ~ div::after {
    background-color: #00CC66 !important;
}
/* Generic: override Streamlit's red/blue active color for radios */
.stRadio > div[role="radiogroup"] > label > div:first-child > div {
    border-color: #555 !important;
}
.stRadio > div[role="radiogroup"] > label[aria-checked="true"] > div:first-child > div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Caché ligero en session_state ─────────────────────────────────────────────
def cached(key, fn):
    """Devuelve st.session_state[key]; solo llama a fn() si la clave no existe."""
    if key not in st.session_state:
        st.session_state[key] = fn()
    return st.session_state[key]


def invalidate_cache(*keys):
    """Elimina una o más claves de caché de session_state."""
    for k in keys:
        st.session_state.pop(k, None)


# ── Logos según tema claro/oscuro ─────────────────────────────────────────────
_LOGO_LIGHT = os.path.join(base_path, "logo-elo-light.png")
_LOGO_DARK  = os.path.join(base_path, "logo-elo2-dark.png")

def _get_theme():
    """Devuelve 'light' o 'dark' según el tema activo de Streamlit."""
    try:
        return st.get_option("theme.base") or "light"
    except Exception:
        return "light"

def _get_logo():
    """Devuelve la ruta del logo adecuada al tema actual."""
    return _LOGO_DARK if _get_theme() == "dark" else _LOGO_LIGHT

# ── Imagen de KatIA (cacheada para no releer en cada rerun) ──────────────────
_KATIA_IMG_PATH = os.path.join(base_path, "KatIA", "katIA.png")

@st.cache_resource
def _load_katia_image():
    try:
        with open(_KATIA_IMG_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None

_KATIA_IMG = _load_katia_image()

# ── GIFs animados de KatIA (revisión de procedimientos) ───────────────────
_KATIA_GIF_CORRECTO_PATH = os.path.join(base_path, "KatIA", "correcto_compressed.gif")
_KATIA_GIF_ERRORES_PATH = os.path.join(base_path, "KatIA", "errores_compressed.gif")

@st.cache_resource
def _load_katia_gif_b64(path: str):
    """Carga un GIF y retorna el tag HTML <img> con base64 para animación."""
    import base64
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<img src="data:image/gif;base64,{b64}" width="220" style="border-radius:12px;">'
    except FileNotFoundError:
        return None

_KATIA_GIF_CORRECTO_HTML = _load_katia_gif_b64(_KATIA_GIF_CORRECTO_PATH)
_KATIA_GIF_ERRORES_HTML = _load_katia_gif_b64(_KATIA_GIF_ERRORES_PATH)

# ── Banners pixel art para tarjetas de curso ────────────────────────────
_BANNERS_DIR = os.path.join(base_path, "Banners")

@st.cache_resource
def _load_course_banners():
    """Carga los banners como base64 y retorna dict {keyword: b64_str}."""
    import base64
    _files = {
        'geometr': 'geometria.png',
        'aritm':   'aritmetica.png',
        'logic':   'logica.png',
        'lógic':   'logica.png',
        'conteo':  'conteo_combinatoria.png',
        'combinat': 'conteo_combinatoria.png',
        'probab':  'probabilidad.png',
        'álgebra': 'algebra.png',
        'algebra': 'algebra.png',
        'trigon':  'algebra.png',
    }
    banners = {}
    for kw, fname in _files.items():
        if kw in banners:
            continue
        fpath = os.path.join(_BANNERS_DIR, fname)
        try:
            with open(fpath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            banners[kw] = b64
        except FileNotFoundError:
            banners[kw] = None
    return banners

_COURSE_BANNERS = _load_course_banners()

def _get_banner_b64(course_name: str):
    """Retorna el base64 del banner que corresponda al nombre del curso, o None."""
    name_lower = course_name.lower()
    for kw, b64 in _COURSE_BANNERS.items():
        if kw in name_lower:
            return b64
    return None

# Inicializar Base de Datos
# Si DATABASE_URL está definida → PostgreSQL; si no → SQLite local
if 'db' not in st.session_state:
    if os.environ.get('DATABASE_URL'):
        try:
            st.session_state.db = PostgresRepository()
        except RuntimeError as _db_err:
            st.error(f"Error al conectar con la base de datos: {_db_err}")
            st.stop()
    else:
        st.session_state.db = SQLiteRepository()
repo = st.session_state.db
cookie_manager = stx.CookieManager()
# Inicializar Servicios
import src.application.services.student_service as ss_mod
import src.application.services.teacher_service as ts_mod

st.session_state.student_service = ss_mod.StudentService(
    st.session_state.db,
    enable_cognitive_modifier=False,  # Explícito y buscable con grep
)
st.session_state.teacher_service = ts_mod.TeacherService(st.session_state.db)

# Inicializar Configuración de IA
if 'ai_mode' not in st.session_state:
    st.session_state.ai_mode = "Rápido (Flash)"

if 'model_cog' not in st.session_state:
    st.session_state.model_cog = "google/gemma-3-4b"

if 'model_analysis' not in st.session_state:
    st.session_state.model_analysis = "mistralai/mistral-7b-instruct-v0.3"

if 'ai_url' not in st.session_state:
    st.session_state.ai_url = ""

if 'ai_provider_mode' not in st.session_state:
    st.session_state.ai_provider_mode = 'auto'

if 'lmstudio_models' not in st.session_state:
    st.session_state.lmstudio_models = []

if 'cloud_api_key' not in st.session_state:
    st.session_state.cloud_api_key = None

@st.cache_resource
def _get_cached_ai_client(lmstudio_url: str):
    """Detecta el backend de IA UNA SOLA VEZ por URL para toda la instancia de la app.
    @st.cache_resource evita repetir la llamada de red en cada rerun o nueva sesión.
    """
    return ai_mod.get_ai_client(lmstudio_url)

if 'ai_available' not in st.session_state:
    _client = _get_cached_ai_client(st.session_state.ai_url)
    st.session_state.ai_available = _client.is_available
    st.session_state.ai_provider = _client.provider
    st.session_state.cloud_api_key = _client.api_key
    if _client.provider == 'lmstudio':
        st.session_state.lmstudio_models = _client.models
        _best = ai_mod.select_best_model(_client.models)
        if _best:
            st.session_state.model_cog = _best
            st.session_state.model_analysis = _best
    elif _client.provider:
        _pinfo = ai_mod.PROVIDERS.get(_client.provider, {})
        if _pinfo.get('model_cog'):
            st.session_state.model_cog = _pinfo['model_cog']
        if _pinfo.get('model_analysis'):
            st.session_state.model_analysis = _pinfo['model_analysis']

# Mapeo de modelos por modo (Valores predeterminados que el usuario puede sobreescribir)
AI_DEFAULTS = {
    "Rápido (Flash)": {
        "cognitive": "google/gemma-3-4b",
        "analysis": "mistralai/mistral-7b-instruct-v0.3"
    },
    "Profundo (Razonamiento)": {
        "cognitive": "deepseek-r1-0528-qwen3-8b",
        "analysis": "deepseek-r1-0528-qwen3-8b"
    }
}


if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None

# Sincronizar banco de ítems — la carga modular ocurre automáticamente
# en SQLiteRepository.__init__() → sync_items_from_bank_folder()
if 'bank_synced_v12' not in st.session_state:
    st.session_state['bank_synced_v12'] = True

# --- NIVELES DE DESEMPEÑO ACADÉMICO ---
def get_rank(elo):
    """Retorna (nombre_rango, color_hex) según la tabla de rangos ELO.
    16 niveles progresivos que aplican a cualquier materia.
    """
    if elo < 1000:  return "🌱 Punto de Partida",  "#9E9E9E"
    if elo < 1100:  return "🔰 Iniciado",          "#8D6E63"
    if elo < 1200:  return "🔍 Curioso",            "#78909C"
    if elo < 1300:  return "🧭 Explorador",         "#26A69A"
    if elo < 1400:  return "📖 Aprendiz",           "#66BB6A"
    if elo < 1500:  return "📝 Aprendiz Activo",    "#29B6F6"
    if elo < 1600:  return "💡 Intermedio Básico",  "#AB47BC"
    if elo < 1700:  return "🧩 Intermedio",         "#7E57C2"
    if elo < 1800:  return "⚙️ En Desarrollo",      "#42A5F5"
    if elo < 1900:  return "🏗️ Consolidado",        "#26C6DA"
    if elo < 2000:  return "✅ Competente",          "#D4E157"
    if elo < 2100:  return "🎯 Competente Plus",    "#FFCA28"
    if elo < 2200:  return "🚀 Avanzado",           "#FFA726"
    if elo < 2300:  return "🏅 Especialista",       "#FF7043"
    if elo < 2400:  return "🥈 Experto",            "#EF5350"
    if elo < 2500:  return "🥇 Sabio",              "#EC407A"
    return "🌟 Visionario", "#AB47BC"

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    h1, h2 {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 201, 255, 0.3);
    }
    h3 {
        color: #00C9FF;
        font-weight: 700 !important;
        margin-top: 15px;
        text-shadow: 0 0 5px rgba(0, 201, 255, 0.2);
        border-left: 4px solid #92FE9D;
        padding-left: 12px;
    }
    .elo-card {
        padding: 25px; border-radius: 20px;
        background: rgba(38, 39, 48, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center; transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s;
        margin-bottom: 20px; color: #ffffff;
    }
    .elo-card h3, .elo-card p, .elo-card li { color: #e0e0e0 !important; }
    .elo-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 201, 255, 0.15);
        border-color: rgba(0, 201, 255, 0.5);
    }
    ul { text-align: left; color: #e0e0e0; }
    .stButton>button {
        border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; font-weight: 700; border: none;
        letter-spacing: 1px; transition: all 0.3s ease;
        text-transform: uppercase; font-size: 0.9rem;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(118, 75, 162, 0.5); }
    .stTextInput>div>div>input {
        border-radius: 10px; background-color: #1E1E1E;
        color: white; border: 1px solid #333; padding: 10px;
    }
    .stTextInput>div>div>input:focus { border-color: #764ba2; box-shadow: 0 0 10px rgba(118, 75, 162, 0.2); }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px; padding: 10px 25px;
        background-color: #262730; color: #aaa; border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; font-weight: bold;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #00C9FF; }
    .sidebar-text { color: #aaa; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
def login():
    st.session_state.logged_in = True
    st.session_state.session_start_time = time.time()

def logout():
    token = cookie_manager.get("elo_auth_token")
    if token:
        repo.delete_session(token)
        cookie_manager.delete("elo_auth_token")
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    token = cookie_manager.get("elo_auth_token")
    if token:
        user = repo.validate_session(token)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['username']
            st.session_state.role = user['role']
            if 'session_start_time' not in st.session_state:
                st.session_state.session_start_time = time.time()
        else:
            cookie_manager.delete("elo_auth_token")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA DE LOGIN / REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    # ── Estado del wizard de registro ────────────────────────────────────────
    if 'reg_step' not in st.session_state:
        st.session_state.reg_step = 1
    if 'reg_chosen_role' not in st.session_state:
        st.session_state.reg_chosen_role = None

    _logo_col1, _logo_col2, _logo_col3 = st.columns([1, 2, 1])
    with _logo_col2:
        st.image(_get_logo(), width='stretch')
    st.markdown("""
        <div style='text-align:center; margin-bottom:24px;'>
            <p style='color:#aaa; font-size:1.1rem; margin-bottom:10px;'>
                Plataforma de evaluación y aprendizaje adaptativo basada en el sistema ELO
            </p>
            <span style='display:inline-block; background:#1E1E2E; border:1px solid #333;
                         border-radius:20px; padding:5px 14px; font-size:0.82rem; color:#aaa; margin:3px;'>
                📚 +5.000 preguntas adaptativas
            </span>
            <span style='display:inline-block; background:#1E1E2E; border:1px solid #333;
                         border-radius:20px; padding:5px 14px; font-size:0.82rem; color:#aaa; margin:3px;'>
                🎯 Sistema ELO por materia
            </span>
            <span style='display:inline-block; background:#1E1E2E; border:1px solid #333;
                         border-radius:20px; padding:5px 14px; font-size:0.82rem; color:#aaa; margin:3px;'>
                🤖 IA pedagógica integrada
            </span>
        </div>
    """, unsafe_allow_html=True)

    col_info, col_login = st.columns([1.4, 1])

    with col_info:
        st.markdown("""
        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>📌 ¿Qué es LevelUp ELO?</h3>
            <p>LevelUp ELO es una plataforma académica de evaluación adaptativa que utiliza el <b>sistema de calificación ELO</b> —originalmente diseñado para el ajedrez— para medir con precisión el nivel de dominio de cada estudiante en distintas materias.</p>
            <p style="margin-top:10px;">A diferencia de los exámenes tradicionales, el sistema se adapta continuamente: <b>la dificultad de cada ejercicio se ajusta en tiempo real</b> según el rendimiento del estudiante, maximizando el aprendizaje efectivo.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("⚙️ ¿Cómo funciona?"):
            st.markdown("""
            <ul style="margin-top: 6px; line-height: 2; color:#e0e0e0;">
                <li><b>Puntuación ELO por materia:</b> Cada estudiante tiene un índice numérico por área temática que sube o baja según sus respuestas correctas e incorrectas.</li>
                <li><b>Selección adaptativa de ejercicios:</b> El sistema elige automáticamente preguntas en la <em>zona de desarrollo óptimo</em> del estudiante, ni demasiado fáciles ni inalcanzables.</li>
                <li><b>Seguimiento del progreso:</b> Los profesores consultan la evolución de cada estudiante por tema, con métricas de probabilidad de acierto por ejercicio.</li>
                <li><b>Recomendaciones con IA:</b> Un asistente inteligente analiza el historial y genera recomendaciones de estudio personalizadas.</li>
            </ul>
            """, unsafe_allow_html=True)

        with st.expander("👥 Roles en la plataforma"):
            st.markdown("""
            <ul style="margin-top: 6px; line-height: 2; color:#e0e0e0;">
                <li><b>🎓 Estudiante:</b> Accede a ejercicios adaptativos y consulta sus estadísticas de progreso.</li>
                <li><b>🏫 Profesor:</b> Visualiza el rendimiento de sus estudiantes con métricas detalladas por tema.
                    <span style='color:#f0ad4e;'> Requiere aprobación del administrador.</span></li>
                <li><b>🛡️ Administrador:</b> Gestiona las cuentas de profesores y estudiantes en la plataforma.</li>
            </ul>
            """, unsafe_allow_html=True)

    with col_login:
        with st.container(border=True):
            st.markdown("### 🔐 Acceso a la Plataforma")
            tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "✨ Crear Cuenta"])

            with tab1:
                username = st.text_input("Usuario", key="login_user")
                password = st.text_input("Contraseña", type="password", key="login_pass")
                st.write("")
                if st.button("Iniciar Sesión", type="primary", use_container_width=True):
                    with st.spinner("Verificando..."):
                        user = st.session_state.db.login_user(username, password)
                    if user:
                        user_id, uname, role, approved = user
                        if role == 'teacher' and not approved:
                            st.warning("⏳ Tu cuenta de profesor está pendiente de aprobación por el administrador.")
                        else:
                            st.session_state.user_id = user_id
                            st.session_state.username = uname
                            st.session_state.role = role
                            token = repo.create_session(user_id)
                            cookie_manager.set("elo_auth_token", token)
                            login()
                            st.rerun()
                    else:
                        st.error("Credenciales inválidas. Verifique su usuario y contraseña.")

            with tab2:
                # ── Wizard paso 1: selección de rol ──────────────────────────
                if st.session_state.reg_step == 1:
                    st.markdown("#### ¿Cómo usarás LevelUp ELO?")
                    _wiz_s, _wiz_p = st.columns(2)
                    with _wiz_s:
                        with st.container(border=True):
                            st.markdown("**🎓 Estudiante**")
                            st.caption("Practica materias y sigue tu progreso ELO.")
                            if st.button("Soy Estudiante", use_container_width=True,
                                         type="primary", key="wizard_student"):
                                st.session_state.reg_chosen_role = "Estudiante"
                                st.session_state.reg_step = 2
                                st.rerun()
                    with _wiz_p:
                        with st.container(border=True):
                            st.markdown("**🏫 Profesor**")
                            st.caption("Gestiona grupos y monitorea alumnos.")
                            if st.button("Soy Profesor", use_container_width=True,
                                         key="wizard_teacher"):
                                st.session_state.reg_chosen_role = "Profesor"
                                st.session_state.reg_step = 2
                                st.rerun()

                # ── Wizard paso 2: datos de la cuenta ────────────────────────
                elif st.session_state.reg_step == 2:
                    _role_icon = "🎓" if st.session_state.reg_chosen_role == "Estudiante" else "🏫"
                    _role_lbl  = st.session_state.reg_chosen_role
                    st.markdown(f"**{_role_icon} Registro como {_role_lbl}**")

                    if st.session_state.reg_chosen_role == "Profesor":
                        st.warning("⏳ Las cuentas de profesor requieren aprobación del administrador antes de poder acceder.")

                    if st.button("← Cambiar tipo de cuenta", key="wizard_back"):
                        st.session_state.reg_step = 1
                        st.rerun()

                    new_user = st.text_input("Nombre de usuario", key="reg_user")
                    st.caption("Solo letras, números y guion bajo. Sin espacios ni tildes. Ej: juan_perez")

                    new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
                    st.caption("Mínimo 6 caracteres. Ej: Mate2024! · ProfeGrupo3#")

                    education_level = None
                    grade = None
                    if st.session_state.reg_chosen_role == "Estudiante":
                        level_label = st.selectbox(
                            "Nivel Educativo *",
                            ["Universidad", "Colegio", "Concursos", "Semillero de Matemáticas"],
                            index=None,
                            placeholder="— Selecciona tu nivel —",
                            key="reg_level",
                            help="Determina qué catálogo de cursos verás."
                        )
                        st.caption("* Campo obligatorio — debes seleccionar tu nivel educativo para continuar.")
                        education_level = None if level_label is None else ("semillero" if level_label == "Semillero de Matemáticas" else level_label.lower())
                        if education_level == "semillero":
                            grade_label = st.selectbox(
                                "Grado",
                                ["6°", "7°", "8°", "9°", "10°", "11°"],
                                key="reg_grade",
                                help="Grado escolar (6° a 11° bachillerato)."
                            )
                            grade = grade_label.replace("°", "")

                    st.write("")
                    if st.button("Crear Cuenta", type="primary", use_container_width=True):
                        role_map = {"Estudiante": "student", "Profesor": "teacher"}
                        chosen_role = role_map[st.session_state.reg_chosen_role]

                        _pass_stripped = (new_pass or "").strip()
                        if not (new_user or "").strip():
                            st.error("El nombre de usuario es obligatorio.")
                        elif not _pass_stripped:
                            st.error("La contraseña es obligatoria.")
                        elif len(_pass_stripped) < 6:
                            st.error("La contraseña debe tener al menos 6 caracteres.")
                        elif chosen_role == 'student' and not education_level:
                            st.error("Debes seleccionar tu nivel educativo.")
                        else:
                            success, message = st.session_state.db.register_user(
                                new_user, new_pass, chosen_role,
                                education_level=education_level,
                                grade=grade
                            )
                            if success:
                                if chosen_role == 'teacher':
                                    st.info(f"✅ {message} Espera la aprobación del administrador.")
                                else:
                                    st.success(
                                        f"✅ ¡Cuenta creada exitosamente! "
                                        f"Ve a **🔑 Iniciar Sesión** y entra con tu usuario **{new_user}**. "
                                        f"Luego comparte ese usuario con tu profesor para que te agregue a su grupo."
                                    )
                                st.session_state.reg_step = 1
                                st.session_state.reg_chosen_role = None
                            else:
                                st.error(message)

        st.markdown("""
            <p style='text-align:center; color:#666; font-size:0.78rem; margin-top:18px;'>
                ¿Problemas para acceder? Contacta a tu administrador.
            </p>
        """, unsafe_allow_html=True)

else:
    # ══════════════════════════════════════════════════════════════════════════
    # VISTA: ADMINISTRADOR
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.role == 'admin':
        with st.sidebar:
            st.image(_get_logo(), width=180)
            st.write(f"### 🛡️ Admin: **{st.session_state.username}**")
            st.markdown("---")
            if st.button("Cerrar Sesión"):
                logout()

        st.title("🛡️ Panel de Administración")

        # ── Reportes de problemas técnicos ────────────────────────────────────
        _pending_reports = st.session_state.db.get_problem_reports(status='pending')
        if _pending_reports:
            st.subheader(f"🔔 Problemas Técnicos — {len(_pending_reports)} pendiente{'s' if len(_pending_reports) != 1 else ''}")
            for _rpt in _pending_reports:
                with st.container(border=True):
                    col_rpt_info, col_rpt_btn = st.columns([4, 1])
                    with col_rpt_info:
                        st.write(f"**{_rpt['username']}** — {str(_rpt['created_at'])[:16]}")
                        st.caption(_rpt['description'])
                    with col_rpt_btn:
                        if st.button("✅ Resuelto", key=f"resolve_report_{_rpt['id']}"):
                            st.session_state.db.mark_problem_resolved(_rpt['id'])
                            st.rerun()
            st.markdown("---")

        # ── Profesores pendientes ──────────────────────────────────────────────
        st.subheader("⏳ Solicitudes de Profesores Pendientes")
        if 'cache_pending_teachers' not in st.session_state:
            st.session_state.cache_pending_teachers = st.session_state.db.get_pending_teachers()
        pending = st.session_state.cache_pending_teachers

        if not pending:
            st.info("No hay solicitudes pendientes.")
        else:
            for teacher in pending:
                col_name, col_date, col_ok, col_no = st.columns([2, 2, 1, 1])
                with col_name:
                    st.write(f"👤 **{teacher['username']}**")
                with col_date:
                    st.caption(f"Registrado: {str(teacher['created_at'])[:10]}")
                with col_ok:
                    if st.button("✅ Aprobar", key=f"approve_{teacher['id']}"):
                        st.session_state.db.approve_teacher(teacher['id'])
                        st.session_state.pop('cache_pending_teachers', None)
                        st.session_state.pop('cache_approved_teachers', None)
                        st.rerun()
                with col_no:
                    if st.button("❌ Rechazar", key=f"reject_{teacher['id']}"):
                        st.session_state.db.reject_teacher(teacher['id'])
                        st.session_state.pop('cache_pending_teachers', None)
                        st.session_state.pop('cache_approved_teachers', None)
                        st.rerun()

        st.markdown("---")

        # ── Profesores activos ─────────────────────────────────────────────────
        st.subheader("✅ Profesores Activos")
        if 'cache_approved_teachers' not in st.session_state:
            st.session_state.cache_approved_teachers = st.session_state.db.get_approved_teachers()
        approved_teachers = st.session_state.cache_approved_teachers
        if not approved_teachers:
            st.info("No hay profesores activos aún.")
        else:
            for t in approved_teachers:
                col_name, col_date, col_baja = st.columns([2, 2, 1])
                with col_name:
                    st.write(f"🏫 **{t['username']}**")
                with col_date:
                    st.caption(f"Desde: {str(t['created_at'])[:10]}")
                with col_baja:
                    if st.button("🚫 Dar de baja", key=f"deact_t_{t['id']}"):
                        st.session_state.db.deactivate_user(t['id'])
                        st.session_state.pop('cache_approved_teachers', None)
                        st.session_state.pop('cache_all_students', None)
                        st.rerun()

        # Profesores dados de baja
        conn_t = st.session_state.db.get_connection()
        try:
            cur_t = conn_t.cursor(cursor_factory=RealDictCursor)
            cur_t.execute("SELECT id, username, created_at FROM users WHERE role='teacher' AND active=0 ORDER BY username ASC")
            inactive_teachers = [dict(r) for r in cur_t.fetchall()]
        finally:
            st.session_state.db.put_connection(conn_t)
        if inactive_teachers:
            with st.expander(f"Ver {len(inactive_teachers)} profesor(es) dado(s) de baja"):
                for t in inactive_teachers:
                    col_n, col_r = st.columns([3, 1])
                    with col_n:
                        st.write(f"~~{t['username']}~~ — dado de baja")
                    with col_r:
                        if st.button("✅ Reactivar", key=f"react_t_{t['id']}"):
                            st.session_state.db.reactivate_user(t['id'])
                            st.session_state.pop('cache_approved_teachers', None)
                            st.session_state.pop('cache_all_students', None)
                            st.rerun()

        st.markdown("---")

        # ── Estudiantes registrados ────────────────────────────────────────────
        st.subheader("🎓 Estudiantes Registrados")
        if 'cache_all_students' not in st.session_state:
            st.session_state.cache_all_students = st.session_state.db.get_all_students_admin()
        all_students = st.session_state.cache_all_students
        if not all_students:
            st.info("No hay estudiantes registrados aún.")
        else:
            activos = [s for s in all_students if s['active']]
            inactivos = [s for s in all_students if not s['active']]

            for s in activos:
                col_name, col_group, col_date, col_baja = st.columns([2, 1.5, 1.5, 1])
                with col_name:
                    st.write(f"🎓 **{s['username']}**")
                with col_group:
                    st.caption(f"Grupo: {s['group_name'] or 'N/A'}")
                with col_date:
                    st.caption(f"Desde: {str(s['created_at'])[:10]}")
                with col_baja:
                    confirm_key_s = f"confirm_deact_s_{s['id']}"
                    if st.session_state.get(confirm_key_s):
                        col_y, col_n = st.columns(2)
                        with col_y:
                            if st.button("✅ Sí", key=f"yes_deact_s_{s['id']}"):
                                st.session_state.db.deactivate_user(s['id'])
                                st.session_state.pop(confirm_key_s, None)
                                st.session_state.pop('cache_all_students', None)
                                st.rerun()
                        with col_n:
                            if st.button("❌ No", key=f"no_deact_s_{s['id']}"):
                                st.session_state.pop(confirm_key_s, None)
                                st.rerun()
                    else:
                        if st.button("🚫 Dar de baja", key=f"deact_s_{s['id']}"):
                            st.session_state[confirm_key_s] = True
                            st.rerun()

            if inactivos:
                with st.expander(f"Ver {len(inactivos)} estudiante(s) dado(s) de baja"):
                    for s in inactivos:
                        col_n, col_r = st.columns([3, 1])
                        with col_n:
                            st.write(f"~~{s['username']}~~ — dado de baja")
                        with col_r:
                            if st.button("✅ Reactivar", key=f"react_s_{s['id']}"):
                                st.session_state.db.reactivate_user(s['id'])
                                st.session_state.pop('cache_all_students', None)
                                st.rerun()

            st.markdown("---")

            # ── Reasignación de Grupo (Solo Admin) ──────────────────────────────
            st.subheader("📍 Reasignación de Grupo")
            with st.container(border=True):
                col_s, col_g = st.columns(2)
                
                # Cargar datos necesarios (cached)
                if 'cache_all_groups' not in st.session_state:
                    st.session_state.cache_all_groups = st.session_state.db.get_all_groups()
                all_groups = st.session_state.cache_all_groups
                # Filtrar solo estudiantes activos para reasignar (usando la lista ya cargada arriba)
                student_options = {s['username']: s['id'] for s in activos}
                group_options = {f"{g['name']} ({g['teacher_name']})": g['id'] for g in all_groups}
                group_options["[ Ningún Grupo ]"] = None
                
                with col_s:
                    sel_student_name = st.selectbox("Selecciona Estudiante", list(student_options.keys()), key="reassign_student")
                with col_g:
                    sel_group_label = st.selectbox("Selecciona Nuevo Grupo", list(group_options.keys()), key="reassign_group")
                
                allow_null = st.checkbox("Permitir dejar sin grupo", value=False, help="Si se marca, permite asignar '[ Ningún Grupo ]'.")
                
                st.write("")
                if st.button("🚀 Aplicar Cambio de Grupo", type="primary", width='stretch'):
                    student_id = student_options[sel_student_name]
                    new_group_id = group_options[sel_group_label]
                    
                    success, message = st.session_state.db.change_student_group(
                        student_id=student_id,
                        new_group_id=new_group_id,
                        admin_id=st.session_state.user_id,
                        allow_null=allow_null
                    )
                    
                    if success:
                        st.success(message)
                        st.session_state.pop('cache_all_students', None)
                        st.session_state.pop('cache_all_groups', None)
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown("---")

            # ── Gestión de Grupos (Admin) ────────────────────────────────────
            st.subheader("📂 Gestión de Grupos")
            if 'cache_all_groups' not in st.session_state:
                st.session_state.cache_all_groups = st.session_state.db.get_all_groups()
            all_groups_admin = st.session_state.cache_all_groups
            if not all_groups_admin:
                st.info("No hay grupos registrados aún.")
            else:
                for g in all_groups_admin:
                    col_name, col_teacher, col_del = st.columns([2.5, 2, 1.5])
                    with col_name:
                        st.write(f"📂 **{g['name']}**")
                    with col_teacher:
                        st.caption(f"Profesor: {g['teacher_name']}")
                    with col_del:
                        # Confirmación en dos pasos usando session_state
                        confirm_key = f"confirm_del_group_{g['id']}"
                        if st.session_state.get(confirm_key):
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Sí", key=f"yes_del_g_{g['id']}"):
                                    ok, msg = st.session_state.db.delete_group(
                                        g['id'], st.session_state.user_id
                                    )
                                    st.session_state.pop(confirm_key, None)
                                    if ok:
                                        st.success(msg)
                                        st.session_state.pop('cache_all_groups', None)
                                        st.session_state.pop('cache_all_students', None)
                                        import time
                                        time.sleep(1.5)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            with col_no:
                                if st.button("❌ No", key=f"no_del_g_{g['id']}"):
                                    st.session_state.pop(confirm_key, None)
                                    st.rerun()
                        else:
                            if st.button("🗑️ Eliminar", key=f"del_g_{g['id']}"):
                                st.session_state[confirm_key] = True
                                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # VISTA: PROFESOR
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.role == 'teacher':
        with st.sidebar:
            st.image(_get_logo(), width=180)
            st.write(f"### 🏫 Profesor: **{st.session_state.username}**")
            # T4a: badge de procedimientos pendientes en el sidebar
            _pend_n = st.session_state.db.get_pending_submissions_count(st.session_state.user_id)
            if _pend_n > 0:
                st.markdown(f"🔔 **Pendientes: {_pend_n}**")
            st.markdown("---")
            # ── Badge de estado de IA (siempre visible) ───────────────────────
            _badge_p = st.session_state.get('ai_provider')
            _badge_ok = st.session_state.get('ai_available', False)
            if not _badge_ok or not _badge_p:
                st.markdown("⚠️ **Sin backend de IA**")
            elif _badge_p == 'lmstudio':
                st.markdown("🟢 **Local Conectada**")
            else:
                _badge_label = ai_mod.PROVIDERS.get(_badge_p, {}).get('label', _badge_p)
                _badge_name = _badge_label.split(' ', 1)[-1] if _badge_label else _badge_p
                st.markdown(f"🔵 **{_badge_name} Activo**")
            with st.expander("⚙️ Configuración de IA"):
                st.caption("🔧 **Proveedor de IA**")
                _t_mode = st.radio(
                    "Modo IA",
                    ["🤖 Auto", "☁️ API Key", "🖥️ Local"],
                    index=["auto", "cloud", "local"].index(st.session_state.get('ai_provider_mode', 'auto')),
                    key="provider_radio_teacher",
                    label_visibility="collapsed",
                    horizontal=True,
                )
                _new_mode_t = {"🤖 Auto": "auto", "☁️ API Key": "cloud", "🖥️ Local": "local"}[_t_mode]
                # T9b: limpiar API key al cambiar de modo para evitar mezclas entre proveedores
                if st.session_state.ai_provider_mode != _new_mode_t:
                    st.session_state.cloud_api_key = None
                    st.session_state.ai_provider_mode = _new_mode_t

                if _t_mode == "🤖 Auto":
                    if st.button("🔄 Reconectar", key="btn_reconnect_teacher"):
                        for _k in ('ai_available', 'lmstudio_models'):
                            st.session_state.pop(_k, None)
                        st.rerun()
                elif _t_mode == "☁️ API Key":
                    _env_key = os.getenv("GROQ_API_KEY")
                    if _env_key:
                        # Remoto (Streamlit Cloud): key disponible en entorno, no mostrar input
                        if st.session_state.cloud_api_key != _env_key:
                            st.session_state.cloud_api_key = _env_key
                            _detected = ai_mod.detect_provider_from_key(_env_key)
                            st.session_state.ai_provider = _detected or 'groq'
                            _pinfo = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {})
                            st.session_state.model_cog = _pinfo.get('model_cog') or st.session_state.model_cog
                            st.session_state.model_analysis = _pinfo.get('model_analysis') or st.session_state.model_analysis
                            st.session_state.ai_available = True
                        _plabel = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {}).get('label', st.session_state.ai_provider)
                        st.caption(f"🔒 Modelo activo: **{_plabel}**")
                    else:
                        # Local: el usuario ingresa la key manualmente
                        _key_in = st.text_input(
                            "API Key", type="password",
                            value="",
                            placeholder="sk-ant-… / gsk_… / sk-… / AIzaSy…",
                            key="cloud_key_teacher",
                        )
                        st.caption("🔒 Tus credenciales son seguras y no se almacenan en ninguna base de datos.")
                        if _key_in:
                            _detected = ai_mod.detect_provider_from_key(_key_in)
                            st.session_state.cloud_api_key = _key_in
                            st.session_state.ai_provider = _detected or 'groq'
                            _pinfo = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {})
                            st.session_state.model_cog = _pinfo.get('model_cog') or st.session_state.model_cog
                            st.session_state.model_analysis = _pinfo.get('model_analysis') or st.session_state.model_analysis
                            st.session_state.ai_available = True
                            _plabel = _pinfo.get('label', st.session_state.ai_provider)
                            st.success(f"{_plabel} detectado")
                        else:
                            st.caption("Soporta: Groq, OpenAI, Anthropic, Gemini, HuggingFace")
                elif _t_mode == "🖥️ Local":
                    _local_url = st.text_input("URL servidor local", value=st.session_state.ai_url, key="lm_url_teacher")
                    st.session_state.ai_url = _local_url
                    if st.button("🔍 Detectar modelos", key="btn_detect_teacher"):
                        _det = ai_mod.detect_lmstudio(st.session_state.ai_url)
                        st.session_state.lmstudio_models = _det['models']
                        if _det['available']:
                            st.session_state.ai_available = True
                            st.session_state.ai_provider = 'lmstudio'
                            st.session_state.cloud_api_key = None
                            _best = ai_mod.select_best_model(_det['models'])
                            if _best:
                                st.session_state.model_cog = _best
                                st.session_state.model_analysis = _best
                            st.rerun()
                        else:
                            st.error("Servidor no detectado en esa URL")
                    _models = st.session_state.get('lmstudio_models', [])
                    if _models:
                        _sel_idx = _models.index(st.session_state.model_cog) if st.session_state.model_cog in _models else 0
                        _sel = st.selectbox("Modelo activo", _models, index=_sel_idx, key="lm_model_teacher")
                        if _sel != st.session_state.model_cog:
                            st.session_state.model_cog = _sel
                            st.session_state.model_analysis = _sel
                        st.session_state.ai_available = True
                        st.session_state.ai_provider = 'lmstudio'
                    else:
                        st.caption("Pulsa 'Detectar modelos' para listar los disponibles")

            st.markdown("---")

            # ── Mis grupos (selector directo) ──────────────────────────────────
            st.markdown("### 🔍 Mis grupos")

            _all_my_groups = st.session_state.teacher_service.get_teacher_groups(
                st.session_state.user_id
            )

            _sel_grp_sidebar_id = None
            _sel_grp_sidebar = '— Grupo —'

            if not _all_my_groups:
                st.caption("Sin grupos creados aún.")
            else:
                # Etiqueta de opción: "Nombre del grupo  ·  Curso"
                _grp_id_to_label = {}
                for _g in _all_my_groups:
                    _lbl = _g['name']
                    if _g.get('course_name') and _g['course_name'] != '—':
                        _lbl += f"  ·  {_g['course_name']}"
                    _grp_id_to_label[_g['id']] = _lbl

                _sidebar_grp_opts = ['— Selecciona un grupo —'] + [
                    _grp_id_to_label[_g['id']] for _g in _all_my_groups
                ]
                _sel_grp_lbl = st.selectbox(
                    "Grupo activo",
                    _sidebar_grp_opts,
                    key="tch_sidebar_group",
                    label_visibility="collapsed",
                )
                if _sel_grp_lbl != '— Selecciona un grupo —':
                    _found_grp = next(
                        (_g for _g in _all_my_groups
                         if _grp_id_to_label[_g['id']] == _sel_grp_lbl),
                        None,
                    )
                    if _found_grp:
                        _sel_grp_sidebar_id = _found_grp['id']
                        _sel_grp_sidebar = _found_grp['name']

            st.markdown("---")
            if st.button("Cerrar Sesión"):
                logout()

        st.title("🏫 Panel del Profesor")

        # ── Notificación de procedimientos pendientes (por grupo activo) ────────
        _pending_count = st.session_state.db.get_pending_submissions_count(
            st.session_state.user_id,
            group_id=_sel_grp_sidebar_id,
        )
        if _sel_grp_sidebar_id and _pending_count > 0:
            st.warning(
                f"📋 **{_pending_count} procedimiento(s) de {_sel_grp_sidebar} esperando revisión.** "
                "Revísalos en la sección de abajo."
            )

        # ── Revisión de Procedimientos ─────────────────────────────────────────
        _exp_badge = f"  🔴 {_pending_count} pendiente(s)" if _pending_count > 0 else ""
        _exp_grp_label = f" — {_sel_grp_sidebar}" if _sel_grp_sidebar_id else ""
        _exp_label = f"📋 Procedimientos para Revisar{_exp_grp_label}{_exp_badge}"
        with st.expander(_exp_label, expanded=(_sel_grp_sidebar_id is not None and _pending_count > 0)):
            if _sel_grp_sidebar_id is None:
                st.info("👈 Selecciona un grupo en el panel izquierdo para ver los procedimientos pendientes.")
            else:
                _pending_subs = st.session_state.db.get_pending_submissions_for_teacher(
                    st.session_state.user_id,
                    group_id=_sel_grp_sidebar_id,
                )
                if not _pending_subs:
                    st.info(f"No hay procedimientos pendientes en **{_sel_grp_sidebar}**.")
                else:
                    for _sub in _pending_subs:
                        _sub_status_t = _sub.get('status', 'pending')
                        _is_validated = (_sub_status_t == 'VALIDATED_BY_TEACHER')

                        with st.container(border=True):
                            st.markdown(
                                f"**👤 {_sub['student_name']}** — "
                                f"enviado el {str(_sub['submitted_at'])[:16]}"
                            )
                            st.caption(f"Pregunta: {_sub['item_content'][:120]}{'…' if len(_sub['item_content']) > 120 else ''}")

                            _c_img, _c_fb = st.columns([1, 1])
                            with _c_img:
                                _stor_url = _sub.get('storage_url')
                                _img_path = _sub.get('procedure_image_path')
                                _img_shown = False
                                if _stor_url:
                                    _img_bytes = repo.resolve_storage_image(_stor_url)
                                    if _img_bytes:
                                        st.image(_img_bytes, caption="Procedimiento del estudiante", width='stretch')
                                        _img_shown = True
                                if not _img_shown and _img_path and os.path.exists(_img_path):
                                    st.image(_img_path, caption="Procedimiento del estudiante", width='stretch')
                                    _img_shown = True
                                if not _img_shown and _sub.get('image_data'):
                                    st.image(bytes(_sub['image_data']), caption="Procedimiento del estudiante", width='stretch')
                                    _img_shown = True
                                if not _img_shown:
                                    print(f"[TEACHER VIEW] No se pudo mostrar imagen: "
                                          f"storage_url={_stor_url}, "
                                          f"img_path={_img_path}, "
                                          f"image_data={'tiene' if _sub.get('image_data') else 'None'}")
                                    st.warning("Imagen no disponible.")

                            with _c_fb:
                                # ── Flujo A: revisado por IA → validar calificación ──
                                if _sub_status_t == 'PENDING_TEACHER_VALIDATION':
                                    _ai_prop = _sub.get('ai_proposed_score')
                                    if _ai_prop is not None:
                                        st.info(
                                            f"🤖 **Nota propuesta por IA: {_ai_prop:.1f} / 100**\n\n"
                                            "Puedes aceptarla o ajustarla antes de confirmar."
                                        )
                                    _ai_fb_t = _sub.get('ai_feedback') or ''
                                    if _ai_fb_t:
                                        with st.expander("📋 Ver retroalimentación de la IA"):
                                            st.markdown(strip_thinking_tags(_ai_fb_t))
                                    _default_score = float(_ai_prop) if _ai_prop is not None else 50.0
                                    _teacher_score_val = st.number_input(
                                        "📊 Calificación oficial (0.0 – 100.0)",
                                        min_value=0.0, max_value=100.0,
                                        value=_default_score,
                                        step=0.5, format="%.1f",
                                        key=f"tscore_{_sub['id']}",
                                        disabled=_is_validated,
                                        help="La nota que ingreses se convierte en la calificación oficial (final_score).",
                                    )
                                    _fb_text_v = st.text_area(
                                        "📝 Retroalimentación (opcional):",
                                        key=f"fb_text_v_{_sub['id']}",
                                        placeholder="Observaciones para el estudiante…",
                                        height=100,
                                        disabled=_is_validated,
                                    )
                                    if st.button(
                                        "✅ Validar y Guardar Calificación",
                                        key=f"validate_btn_{_sub['id']}",
                                        width='stretch',
                                        disabled=_is_validated,
                                    ):
                                        try:
                                            st.session_state.teacher_service.validate_procedure(
                                                _sub['id'], _teacher_score_val, _fb_text_v
                                            )
                                            st.success(
                                                f"Calificación de {_sub['student_name']} "
                                                f"validada: **{_teacher_score_val:.1f}/100**."
                                            )
                                            st.rerun()
                                        except ValueError as _ve:
                                            st.error(str(_ve))

                                # ── Flujo B: enviado manualmente (legado 0-5) ────────
                                else:
                                    _proc_score = st.number_input(
                                        "📊 Calidad del procedimiento (0.0 – 5.0)",
                                        min_value=0.0, max_value=5.0, value=3.0, step=0.1,
                                        format="%.1f",
                                        key=f"score_{_sub['id']}",
                                        disabled=_is_validated,
                                        help="Evalúa la calidad del desarrollo matemático del estudiante.",
                                    )
                                    _fb_text = st.text_area(
                                        "📝 Retroalimentación escrita:",
                                        key=f"fb_text_{_sub['id']}",
                                        placeholder="Escribe tu retroalimentación aquí…",
                                        height=120,
                                        disabled=_is_validated,
                                    )
                                    _fb_img = st.file_uploader(
                                        "🖼️ Sube el procedimiento corregido (opcional):",
                                        type=["jpg", "jpeg", "png", "webp"],
                                        key=f"fb_img_{_sub['id']}",
                                        disabled=_is_validated,
                                    )
                                    _can_submit = (not _is_validated) and bool(_fb_text or _fb_img)
                                    if st.button(
                                        "✅ Enviar retroalimentación",
                                        key=f"fb_submit_{_sub['id']}",
                                        width='stretch',
                                        disabled=not _can_submit,
                                    ):
                                        _fb_img_data = _fb_img.getvalue() if _fb_img else None
                                        _fb_mime = None
                                        if _fb_img:
                                            _fext = _fb_img.name.rsplit('.', 1)[-1].lower()
                                            _fb_mime = {
                                                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                                                'png': 'image/png', 'webp': 'image/webp',
                                            }.get(_fext, 'image/jpeg')
                                        st.session_state.db.save_teacher_feedback(
                                            _sub['id'], _fb_text, _fb_img_data, _fb_mime,
                                            procedure_score=_proc_score,
                                        )
                                        st.success(f"Retroalimentación enviada a {_sub['student_name']} (nota: {_proc_score}/5.0).")
                                        st.rerun()

        # ── Gestión de Grupos ──────────────────────────────────────────────────
        with st.expander("🛠️ Gestión de Grupos"):
            st.markdown("**Crear nuevo grupo**")
            _all_courses_tch = st.session_state.db.get_courses()
            if not _all_courses_tch:
                st.warning("⚠️ No hay cursos en el catálogo. El administrador debe cargar el banco de ítems primero.")
            else:
                _course_opts_tch = {f"{c['name']} ({c['block']})": c['id'] for c in _all_courses_tch}
                _col_a, _col_b, _col_c = st.columns([2, 3, 1])
                with _col_a:
                    _sel_course_label = st.selectbox(
                        "Curso", list(_course_opts_tch.keys()), key="tch_new_group_course"
                    )
                    _sel_course_id = _course_opts_tch[_sel_course_label]
                with _col_b:
                    _new_group_name = st.text_input(
                        "Nombre del grupo",
                        placeholder="Ej: Cálculo Diferencial — 2026 Grupo A",
                        key="tch_new_group_name"
                    )
                with _col_c:
                    st.write(" ")
                    if st.button("➕ Crear", key="tch_btn_create_group"):
                        _ok, _msg = st.session_state.teacher_service.create_new_group(
                            st.session_state.user_id, _sel_course_id, _new_group_name
                        )
                        if _ok:
                            st.success(_msg)
                            st.session_state.pop('cache_all_groups', None)
                            st.rerun()
                        else:
                            st.error(_msg)

            st.markdown("---")
            st.markdown("**Mis grupos actuales**")
            _my_groups = st.session_state.teacher_service.get_teacher_groups(st.session_state.user_id)
            if _my_groups:
                for _mg in _my_groups:
                    with st.container(border=True):
                        _mg_c1, _mg_c2 = st.columns([3, 2])
                        with _mg_c1:
                            st.write(f"**{_mg['name']}** — {_mg['course_name']}")
                            st.caption(f"Creado: {str(_mg['created_at'])[:10]}")
                        with _mg_c2:
                            _active_code = st.session_state.get(f'gen_code_{_mg["id"]}') or _mg.get('invite_code')
                            if _active_code:
                                st.code(_active_code, language=None)
                                st.caption("Comparte este código con tus estudiantes")
                            if st.button("🔑 Generar código", key=f"gen_code_btn_{_mg['id']}"):
                                try:
                                    _new_code = repo.generate_group_invite_code(_mg['id'])
                                    st.session_state[f'gen_code_{_mg["id"]}'] = _new_code
                                    st.rerun()
                                except Exception as _ce:
                                    st.error(str(_ce))
            else:
                st.info("No tienes grupos creados aún.")

        st.markdown("---")

        # ── Ranking semanal ─────────────────────────────────────────
        with st.expander("🏆 Ranking Semanal"):
            _rank_mode = st.radio("Modo", ["Por nivel", "Por curso", "Por grupo"], horizontal=True, key="tch_rank_mode")
            _medal = {1: "🥇", 2: "🥈", 3: "🥉"}

            if _rank_mode == "Por nivel":
                _sel_level = st.selectbox(
                    "Nivel educativo",
                    ["universidad", "colegio", "concursos", "semillero"],
                    format_func=lambda x: {"semillero": "Semillero de Matemáticas"}.get(x, x.title()),
                    key="tch_rank_level",
                )
                _tch_rank_grade = None
                if _sel_level == "semillero":
                    _tch_grade_label = st.selectbox(
                        "Grado", ["6°", "7°", "8°", "9°", "10°", "11°"], key="tch_rank_grade"
                    )
                    _tch_rank_grade = _tch_grade_label.replace("°", "")
                _global_ranking = repo.get_global_ranking(limit=10, education_level=_sel_level, grade=_tch_rank_grade)
                if _global_ranking:
                    _tch_rank_html = "<table style='width:100%; border-collapse:collapse; font-size:0.9rem;'>"
                    _tch_rank_html += "<tr style='border-bottom:1px solid #444;'><th style='padding:6px;'>🏅</th><th style='padding:6px; text-align:left;'>Estudiante</th><th style='padding:6px;'>ELO</th><th style='padding:6px;'>Intentos</th></tr>"
                    for _r in _global_ranking:
                        _pos = _medal.get(_r['rank'], str(_r['rank']))
                        _tch_rank_html += f"<tr style='border-bottom:1px solid #333;'>"
                        _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_pos}</td>"
                        _tch_rank_html += f"<td style='padding:6px;'>{_r['username']}</td>"
                        _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_r['global_elo']:.0f}</td>"
                        _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_r['attempts_this_week']}</td>"
                        _tch_rank_html += "</tr>"
                    _tch_rank_html += "</table>"
                    st.markdown(_tch_rank_html, unsafe_allow_html=True)
                else:
                    st.caption("Sin actividad esta semana en este nivel.")
            elif _rank_mode == "Por curso":
                _all_courses = repo.get_courses()
                if _all_courses:
                    _course_opts = {c['name']: c['id'] for c in _all_courses}
                    _sel_course_rank = st.selectbox("Curso", list(_course_opts.keys()), key="tch_rank_course")
                    _sel_course_rank_id = _course_opts[_sel_course_rank]
                    _course_ranking = repo.get_course_ranking(_sel_course_rank_id, limit=10)
                    if _course_ranking:
                        _tch_rank_html = "<table style='width:100%; border-collapse:collapse; font-size:0.9rem;'>"
                        _tch_rank_html += "<tr style='border-bottom:1px solid #444;'><th style='padding:6px;'>🏅</th><th style='padding:6px; text-align:left;'>Estudiante</th><th style='padding:6px;'>ELO</th><th style='padding:6px;'>Intentos</th></tr>"
                        for _r in _course_ranking:
                            _pos = _medal.get(_r['rank'], str(_r['rank']))
                            _tch_rank_html += f"<tr style='border-bottom:1px solid #333;'>"
                            _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_pos}</td>"
                            _tch_rank_html += f"<td style='padding:6px;'>{_r['username']}</td>"
                            _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_r['course_elo']:.0f}</td>"
                            _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_r['attempts_this_week']}</td>"
                            _tch_rank_html += "</tr>"
                        _tch_rank_html += "</table>"
                        st.markdown(_tch_rank_html, unsafe_allow_html=True)
                    else:
                        st.caption("Sin actividad esta semana en este curso.")
                else:
                    st.caption("No hay cursos registrados.")
            else:
                _tch_groups = st.session_state.teacher_service.get_teacher_groups(st.session_state.user_id)
                if not _tch_groups:
                    st.info("Crea un grupo primero para ver el ranking.")
                else:
                    _grp_opts_rank = {g['name']: g['id'] for g in _tch_groups}
                    _sel_grp_rank = st.selectbox(
                        "Grupo", list(_grp_opts_rank.keys()), key="tch_ranking_group"
                    )
                    _sel_grp_rank_id = _grp_opts_rank[_sel_grp_rank]

                    _tch_ranking = repo.get_weekly_ranking(_sel_grp_rank_id)
                    if _tch_ranking:
                        _tch_rank_html = "<table style='width:100%; border-collapse:collapse; font-size:0.9rem;'>"
                        _tch_rank_html += "<tr style='border-bottom:1px solid #444;'><th style='padding:6px;'>🏅</th><th style='padding:6px; text-align:left;'>Estudiante</th><th style='padding:6px;'>ELO</th><th style='padding:6px;'>Intentos</th></tr>"
                        for _r in _tch_ranking:
                            _pos = _medal.get(_r['rank'], str(_r['rank']))
                            _tch_rank_html += f"<tr style='border-bottom:1px solid #333;'>"
                            _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_pos}</td>"
                            _tch_rank_html += f"<td style='padding:6px;'>{_r['username']}</td>"
                            _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_r['global_elo']:.0f}</td>"
                            _tch_rank_html += f"<td style='padding:6px; text-align:center;'>{_r['attempts_this_week']}</td>"
                            _tch_rank_html += "</tr>"
                        _tch_rank_html += "</table>"
                        st.markdown(_tch_rank_html, unsafe_allow_html=True)
                    else:
                        st.caption("Sin actividad esta semana en este grupo.")

                    _col_save, _col_hist = st.columns(2)
                    with _col_save:
                        if st.button("📸 Guardar ranking de esta semana", key="tch_save_ranking"):
                            repo.save_weekly_ranking(_sel_grp_rank_id)
                            st.success("Ranking guardado exitosamente.")
                    with _col_hist:
                        pass

                    # ── Historial de rankings ──────────────────────────────────
                    _history = repo.get_ranking_history(_sel_grp_rank_id)
                    if _history:
                        st.markdown("**📊 Historial de rankings (últimas 4 semanas)**")
                        from collections import defaultdict
                        _weeks_hist = defaultdict(list)
                        for _h in _history:
                            _weeks_hist[_h['week_start']].append(_h)
                        _prev_week_users = {}
                        _sorted_weeks = sorted(_weeks_hist.keys(), reverse=True)
                        for _w_idx, _wk in enumerate(_sorted_weeks):
                            _entries = _weeks_hist[_wk]
                            _wk_end = _entries[0]['week_end']
                            st.caption(f"Semana {_wk} → {_wk_end}")
                            _curr_week_users = {e['username']: e['rank'] for e in _entries}
                            for _e in _entries:
                                _pos_str = _medal.get(_e['rank'], str(_e['rank']))
                                _arrow = ""
                                if _prev_week_users:
                                    _old_rank = _prev_week_users.get(_e['username'])
                                    if _old_rank is None:
                                        _arrow = " 🆕"
                                    elif _old_rank > _e['rank']:
                                        _arrow = " ⬆️"
                                    elif _old_rank < _e['rank']:
                                        _arrow = " ⬇️"
                                st.markdown(f"  {_pos_str} **{_e['username']}** — {_e['global_elo']:.0f} ELO ({_e['attempts_count']} intentos){_arrow}")
                            _prev_week_users = _curr_week_users

        st.markdown("---")

        # ── Dashboard principal ────────────────────────────────────────────────
        if _sel_grp_sidebar_id is None:
            # Pantalla de bienvenida — aún no hay grupo seleccionado
            _all_students_q, _ = st.session_state.teacher_service.get_dashboard_data(st.session_state.user_id)
            if not _all_students_q:
                st.info("Aún no tienes estudiantes vinculados a tus grupos.")
            else:
                st.info("👈 Selecciona una categoría y un grupo en el panel izquierdo para ver el rendimiento de tus estudiantes.")
                _sc1, _sc2, _sc3 = st.columns(3)
                _sc1.metric("👥 Grupos activos", len({s['group_id'] for s in _all_students_q}))
                _sc2.metric("📚 Estudiantes únicos", len({s['id'] for s in _all_students_q}))
                _sc3.metric("📋 Procedimientos pendientes", _pending_count)
        else:
            # Cargar estudiantes del profesor y filtrar por el grupo seleccionado
            _all_students_raw, _ = st.session_state.teacher_service.get_dashboard_data(st.session_state.user_id)
            students = [s for s in _all_students_raw if s['group_id'] == _sel_grp_sidebar_id]

            if not students:
                st.info(f"No hay estudiantes en el grupo **{_sel_grp_sidebar}**.")
            else:
                # ── Filtro de materia (solo si hay varias en el grupo) ─────────
                _all_subjects = sorted(set(
                    s.get('course_name', '—') for s in students if s.get('course_name', '—') != '—'
                ))
                if len(_all_subjects) > 1:
                    _subj_opts = ["Todas"] + _all_subjects
                    _sel_subject = st.selectbox(
                        "📚 Filtrar por Materia", _subj_opts,
                        key="tch_subject_filter",
                    )
                    if _sel_subject != "Todas":
                        students = [s for s in students if s.get('course_name') == _sel_subject]

                if not students:
                    st.info("No hay estudiantes en esta combinación de filtros.")

                # Deduplicar por id
                _seen_ids = set()
                _unique_students = []
                for _st in students:
                    if _st['id'] not in _seen_ids:
                        _seen_ids.add(_st['id'])
                        _unique_students.append(_st)
                students = _unique_students

                # ── Selector de estudiante ─────────────────────────────────────
                _stu_opts = ["— Selecciona un estudiante —"] + [s['username'] for s in students]
                _sel_name = st.selectbox(
                    "👤 Ver detalle de estudiante", _stu_opts,
                    key="tch_student_selector",
                )

                # ── Tabla resumen ELO (siempre visible) ───────────────────────
                st.subheader(f"📈 Rendimiento ELO — {_sel_grp_sidebar}")
                _BASE_COLS = {"Estudiante", "Grupo", "ELO Global", "Rango"}
                _sum_rows = []
                for _s in students:
                    _elo_map = cached(f'cache_elo_topic_{_s["id"]}',
                                      lambda _sid=_s['id']: st.session_state.db.get_latest_elo_by_topic(_sid))

                    _enrolled_topics = cached(f'cache_enrolled_topics_{_s["id"]}',
                                              lambda _sid=_s['id']: st.session_state.db.get_enrolled_topics(_sid))
                    _active_map = (
                        {t: v for t, v in _elo_map.items() if t in _enrolled_topics}
                        if _enrolled_topics
                        else _elo_map
                    )

                    _gelo = (
                        sum(e for e, _ in _active_map.values()) / len(_active_map)
                        if _active_map else 1000.0
                    )
                    _rname, _ = get_rank(_gelo)
                    _row = {
                        "Estudiante": _s['username'],
                        "Grupo": _s.get('group_name', _sel_grp_sidebar),
                        "ELO Global": round(_gelo, 1),
                        "Rango": _rname,
                    }
                    _row.update({t: round(v[0], 1) for t, v in _active_map.items()})
                    _sum_rows.append(_row)

                _df_sum = (
                    pd.DataFrame(_sum_rows)
                    if _sum_rows
                    else pd.DataFrame(columns=["Estudiante", "Grupo", "ELO Global", "Rango"])
                )

                for _c in _df_sum.columns:
                    if _c not in _BASE_COLS:
                        _df_sum[_c] = pd.to_numeric(_df_sum[_c], errors='coerce')

                _topic_cols = [c for c in _df_sum.columns if c not in _BASE_COLS]
                _active_topic_cols = [c for c in _topic_cols if _df_sum[c].notna().any()]
                _ordered = [c for c in ["Estudiante", "Grupo", "ELO Global", "Rango"]
                            if c in _df_sum.columns] + _active_topic_cols
                _df_sum = _df_sum[_ordered]

                st.dataframe(_df_sum, width='stretch')

                st.markdown("---")

                # ── Panel de detalle (solo cuando hay estudiante seleccionado) ─
                if _sel_name == "— Selecciona un estudiante —":
                    st.info("☝️ Selecciona un estudiante en el filtro de arriba para ver su detalle completo.")
                else:
                    _sel_stu = next(s for s in students if s['username'] == _sel_name)
                    _dash = st.session_state.teacher_service.get_student_dashboard(_sel_stu['id'])
                    _elo_sum = _dash['elo_summary']
                    _proc_by_course = _dash['procedure_stats_by_course']
                    _att_list = _dash['attempts']
                    _global_elo = _elo_sum['global_elo']
                    _rank_n, _ = get_rank(_global_elo)

                    # ── Cabecera del estudiante ────────────────────────────────
                    st.subheader(f"🔍 Detalle: **{_sel_name}**")
                    _mc1, _mc2, _mc3, _mc4 = st.columns(4)
                    _mc1.metric("🏆 ELO Global", f"{_global_elo:.1f}", delta=_rank_n)
                    _mc2.metric("📊 Intentos Totales", _elo_sum['attempts_count'])
                    _mc3.metric("🎯 Precisión Reciente", f"{_elo_sum['recent_accuracy']:.1%}")
                    # Tiempo promedio por pregunta
                    _times_list = [a.get('time_taken') for a in _att_list if a.get('time_taken') and a['time_taken'] > 0]
                    _avg_time_s = sum(_times_list) / len(_times_list) if _times_list else 0
                    _mc4.metric("⏱️ Tiempo Prom.", f"{_avg_time_s:.0f}s" if _avg_time_s else "—")

                    st.markdown("---")

                    # ── Bloque 1: ELO por Tópico + Procedimientos ─────────────
                    _d1, _d2 = st.columns([1, 1])
                    with _d1:
                        st.markdown("**📊 ELO por Tópico**")
                        if _elo_sum['elo_by_topic']:
                            _elo_rows = [
                                {"Tópico": t, "ELO": round(e, 1), "RD ±": round(rd, 1)}
                                for t, (e, rd) in sorted(
                                    _elo_sum['elo_by_topic'].items(), key=lambda x: -x[1][0]
                                )
                            ]
                            st.dataframe(
                                pd.DataFrame(_elo_rows), width='stretch', hide_index=True
                            )
                        else:
                            st.caption("Sin datos de ELO por tópico.")

                    with _d2:
                        st.markdown("**📝 Calidad de Procedimientos por Curso**")
                        if _proc_by_course:
                            _proc_rows = [
                                {
                                    "Curso": v['course_name'],
                                    "Promedio": f"{v['avg_score']:.1f} / 100",
                                    "Envíos": v['count'],
                                }
                                for v in _proc_by_course.values()
                            ]
                            st.dataframe(
                                pd.DataFrame(_proc_rows), width='stretch', hide_index=True
                            )
                        else:
                            st.caption("Sin procedimientos evaluados.")

                    # ── Bloque 2: Gráfico evolución ELO por tema ──────────────
                    st.markdown("**📈 Evolución ELO por Tema**")
                    if _att_list:
                        _df_att = pd.DataFrame(_att_list)
                        _df_att['intento'] = range(1, len(_df_att) + 1)
                        _df_att['resultado'] = _df_att['is_correct'].map(
                            {1: '✅', 0: '❌', True: '✅', False: '❌'}
                        )
                        _fig_evo = go.Figure()
                        for _topic in _df_att['topic'].unique():
                            _td = _df_att[_df_att['topic'] == _topic]
                            _fig_evo.add_trace(go.Scatter(
                                x=_td['intento'], y=_td['elo_after'],
                                mode='lines+markers', name=_topic, line=dict(width=2)
                            ))
                        _fig_evo.update_layout(
                            template="plotly_dark",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis_title="Intento #", yaxis_title="ELO",
                            legend=dict(bgcolor='rgba(38,39,48,0.8)', bordercolor='gray'),
                            margin=dict(t=10),
                        )
                        st.plotly_chart(_fig_evo, width='stretch')

                        with st.expander("🎯 Probabilidad de Acierto por Intento"):
                            _df_prob = _df_att.dropna(subset=['prob_failure']).copy()
                            if _df_prob.empty:
                                st.info("Sin datos de probabilidad aún.")
                            else:
                                _df_prob['prob_success'] = 1.0 - _df_prob['prob_failure']
                                _bar_c = [
                                    '#28a745' if ps >= 0.5 else '#dc3545'
                                    for ps in _df_prob['prob_success']
                                ]
                                _fig_p = go.Figure()
                                _fig_p.add_trace(go.Bar(
                                    x=_df_prob['intento'], y=_df_prob['prob_success'],
                                    marker_color=_bar_c, opacity=0.85,
                                ))
                                _fig_p.add_hline(
                                    y=0.5, line_dash='dash', line_color='#ffc107',
                                    annotation_text='Umbral 50%', annotation_font_color='#ffc107',
                                )
                                _fig_p.update_layout(
                                    template="plotly_dark",
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    xaxis_title="Intento #", yaxis_title="Prob. de Acierto",
                                    yaxis=dict(range=[0, 1]),
                                )
                                st.plotly_chart(_fig_p, width='stretch')
                                _pm1, _pm2, _pm3 = st.columns(3)
                                _pm1.metric("Promedio", f"{_df_prob['prob_success'].mean():.1%}")
                                _pm2.metric("Máximo", f"{_df_prob['prob_success'].max():.1%}")
                                _pm3.metric("Preguntas difíciles (<50%)", int((_df_prob['prob_success'] < 0.5).sum()))

                        with st.expander("📄 Historial de Intentos"):
                            _hist_cols = ['intento', 'topic', 'difficulty', 'resultado',
                                          'elo_after', 'rating_deviation', 'prob_failure',
                                          'time_taken', 'timestamp']
                            _hist_cols = [c for c in _hist_cols if c in _df_att.columns]
                            _df_hist_v = _df_att[_hist_cols].copy()
                            if 'time_taken' in _df_hist_v.columns:
                                _df_hist_v['time_taken'] = _df_hist_v['time_taken'].apply(
                                    lambda x: f"{x:.1f}s" if pd.notna(x) and x > 0 else "—"
                                )
                            _rename_map = {
                                'intento': '#', 'topic': 'Tema', 'difficulty': 'Dificultad',
                                'resultado': 'Res.', 'elo_after': 'ELO',
                                'rating_deviation': 'RD ±', 'prob_failure': 'P.Fallo',
                                'time_taken': 'Tiempo', 'timestamp': 'Fecha',
                            }
                            _df_hist_v.rename(columns=_rename_map, inplace=True)
                            st.dataframe(_df_hist_v, width='stretch')
                    else:
                        st.info(f"{_sel_name} aún no ha respondido ninguna pregunta.")

                    # ── Interacciones con KatIA ────────────────────────────────
                    st.markdown("---")
                    with st.expander("🐾 Interacciones con KatIA (Tutor Socrático)"):
                        _katia_data = repo.get_katia_interactions(_sel_stu['id'])
                        if _katia_data:
                            # Resumen
                            _ki_total = len(_katia_data)
                            _ki_topics = {}
                            _ki_courses = {}
                            for _ki in _katia_data:
                                _t = _ki.get('item_topic') or 'Sin tema'
                                _ki_topics[_t] = _ki_topics.get(_t, 0) + 1
                                _cn = _ki.get('course_name') or _ki.get('course_id') or 'Sin curso'
                                _ki_courses[_cn] = _ki_courses.get(_cn, 0) + 1

                            _km1, _km2 = st.columns(2)
                            _km1.metric("Total de preguntas a KatIA", _ki_total)
                            _top_topic = max(_ki_topics, key=_ki_topics.get)
                            _km2.metric("Tema más consultado", _top_topic, delta=f"{_ki_topics[_top_topic]} preguntas")

                            # Tabla de temas consultados
                            st.markdown("**Temas consultados:**")
                            _topic_rows = sorted(_ki_topics.items(), key=lambda x: -x[1])
                            _topic_df = pd.DataFrame(_topic_rows, columns=["Tema", "Consultas"])
                            st.dataframe(_topic_df, width='stretch', hide_index=True)

                            # Por materia
                            if len(_ki_courses) > 1:
                                st.markdown("**Por materia:**")
                                _course_rows = sorted(_ki_courses.items(), key=lambda x: -x[1])
                                _course_df = pd.DataFrame(_course_rows, columns=["Materia", "Consultas"])
                                st.dataframe(_course_df, width='stretch', hide_index=True)

                            # Historial detallado
                            st.markdown("**Historial de conversaciones:**")
                            for _ki in _katia_data[:50]:
                                _ki_date = str(_ki.get('created_at', ''))[:16]
                                _ki_course = _ki.get('course_name') or _ki.get('course_id') or ''
                                _ki_topic = _ki.get('item_topic') or ''
                                _ki_label = f"{_ki_date} · {_ki_course} · {_ki_topic}" if _ki_course else _ki_date
                                with st.expander(_ki_label, expanded=False):
                                    st.markdown(f"**Estudiante:** {_ki.get('student_message', '')}")
                                    if _ki.get('katia_response'):
                                        st.markdown(f"**KatIA:** {_ki['katia_response']}")
                        else:
                            st.caption(f"{_sel_name} no ha interactuado con KatIA aún.")

                    # ── Análisis Pedagógico con IA ─────────────────────────────
                    st.markdown("---")
                    _ai_disabled = not st.session_state.ai_available
                    _ai_help_txt = "IA no disponible en este entorno" if _ai_disabled else None
                    if st.button(
                        "🧠 Generar Análisis Pedagógico con IA",
                        key=f"ai_anal_{_sel_stu['id']}",
                        width='stretch',
                        disabled=_ai_disabled,
                        help=_ai_help_txt,
                    ):
                        try:
                            with st.spinner("Analizando trayectoria del estudiante..."):
                                _ai_proc = st.session_state.db.get_student_procedure_scores(_sel_stu['id'])
                                _ai_proc_stats = {
                                    'count': len(_ai_proc),
                                    'avg_score': (sum(p['score'] for p in _ai_proc) / len(_ai_proc)) if _ai_proc else None,
                                    'scores': [p['score'] for p in _ai_proc],
                                }
                                _analysis = st.session_state.teacher_service.generate_ai_analysis(
                                    _sel_stu['id'], _global_elo,
                                    api_key=st.session_state.cloud_api_key,
                                    provider=st.session_state.get('ai_provider'),
                                    base_url=st.session_state.ai_url,
                                    model_name=st.session_state.model_analysis,
                                    procedure_stats=_ai_proc_stats,
                                    procedure_stats_by_course=_proc_by_course,
                                )
                            if isinstance(_analysis, str) and (_analysis.startswith("ERROR_401:") or _analysis.startswith("ERROR_429:")):
                                st.error(_analysis.split(": ", 1)[1])
                            else:
                                with st.container(border=True):
                                    st.markdown("#### 📋 Análisis Pedagógico con IA")
                                    st.markdown(_analysis)
                        except (ConnectionError, TimeoutError):
                            st.error("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.")

        # ── Exportar datos de estudiantes (CSV / Excel) ──────────────────────
        st.markdown("---")
        with st.expander("📥 Exportar datos de estudiantes"):
            st.caption(
                "Descarga todos los datos de tus estudiantes para análisis externo. "
                "Incluye intentos, tiempo por pregunta, RD, probabilidad de fallo, "
                "matrículas, procedimientos e interacciones con KatIA."
            )
            _export_scope = "del grupo seleccionado" if _sel_grp_sidebar_id else "de todos tus grupos"
            st.info(f"📊 Se exportarán datos **{_export_scope}**.")

            _exp_fmt = st.radio(
                "Formato", ["CSV", "Excel (.xlsx)"],
                horizontal=True, key="tch_export_fmt",
            )

            if st.button("📥 Generar archivo de exportación", key="tch_export_btn", type="primary"):
                with st.spinner("Recopilando datos..."):
                    _exp_attempts = repo.export_teacher_student_data(
                        st.session_state.user_id,
                        group_id=_sel_grp_sidebar_id,
                    )
                    _exp_enrollments = repo.export_teacher_enrollments(
                        st.session_state.user_id,
                        group_id=_sel_grp_sidebar_id,
                    )
                    _exp_procedures = repo.export_teacher_procedures(
                        st.session_state.user_id,
                        group_id=_sel_grp_sidebar_id,
                    )
                    _exp_katia = repo.export_teacher_katia_interactions(
                        st.session_state.user_id,
                        group_id=_sel_grp_sidebar_id,
                    )

                if not _exp_attempts and not _exp_enrollments:
                    st.warning("No hay datos para exportar.")
                else:
                    _df_att_exp = pd.DataFrame(_exp_attempts) if _exp_attempts else pd.DataFrame()
                    _df_enr_exp = pd.DataFrame(_exp_enrollments) if _exp_enrollments else pd.DataFrame()
                    _df_proc_exp = pd.DataFrame(_exp_procedures) if _exp_procedures else pd.DataFrame()
                    _df_katia_exp = pd.DataFrame(_exp_katia) if _exp_katia else pd.DataFrame()

                    # Renombrar columnas a español
                    _col_map_att = {
                        'student_id': 'ID Estudiante', 'username': 'Usuario',
                        'education_level': 'Nivel', 'grade': 'Grado',
                        'group_name': 'Grupo', 'course_name': 'Curso',
                        'course_block': 'Bloque', 'attempt_id': 'ID Intento',
                        'item_id': 'ID Pregunta', 'topic': 'Tema',
                        'item_area': 'Área', 'item_enfoque': 'Enfoque',
                        'item_componente': 'Componente Específica',
                        'item_content': 'Enunciado', 'item_difficulty': 'Dificultad Ítem',
                        'is_correct': 'Correcto', 'elo_after': 'ELO Después',
                        'attempt_rd': 'RD', 'prob_failure': 'P. Fallo',
                        'expected_score': 'P. Éxito Esperada',
                        'time_taken': 'Tiempo (s)', 'confidence_score': 'Confianza IA',
                        'error_type': 'Tipo Error', 'attempt_timestamp': 'Fecha',
                    }
                    _col_map_enr = {
                        'student_id': 'ID Estudiante', 'username': 'Usuario',
                        'education_level': 'Nivel', 'grade': 'Grado',
                        'group_name': 'Grupo', 'course_id': 'ID Curso',
                        'course_name': 'Curso', 'course_block': 'Bloque',
                        'enrolled_at': 'Fecha Matrícula',
                    }
                    _col_map_proc = {
                        'student_id': 'ID Estudiante', 'username': 'Usuario',
                        'group_name': 'Grupo', 'item_id': 'ID Pregunta',
                        'item_content': 'Enunciado',
                        'status': 'Estado', 'ai_proposed_score': 'Nota IA',
                        'teacher_score': 'Nota Docente', 'final_score': 'Nota Final',
                        'elo_delta': 'Delta ELO', 'submitted_at': 'Fecha Envío',
                        'reviewed_at': 'Fecha Revisión',
                    }
                    _col_map_katia = {
                        'student_id': 'ID Estudiante', 'username': 'Usuario',
                        'group_name': 'Grupo', 'course_name': 'Materia',
                        'course_id': 'ID Curso', 'item_topic': 'Tema Específico',
                        'student_message': 'Pregunta del Estudiante',
                        'katia_response': 'Respuesta de KatIA',
                        'created_at': 'Fecha',
                    }
                    if not _df_att_exp.empty:
                        _df_att_exp.rename(columns=_col_map_att, inplace=True)
                    if not _df_enr_exp.empty:
                        _df_enr_exp.rename(columns=_col_map_enr, inplace=True)
                    if not _df_proc_exp.empty:
                        _df_proc_exp.rename(columns=_col_map_proc, inplace=True)
                    if not _df_katia_exp.empty:
                        _df_katia_exp.rename(columns=_col_map_katia, inplace=True)

                    _grp_label = _sel_grp_sidebar.replace(' ', '_') if _sel_grp_sidebar_id else "todos"
                    _ts_label = pd.Timestamp.now().strftime('%Y%m%d')

                    if _exp_fmt == "CSV":
                        import io as _io
                        _csv_buf = _io.StringIO()
                        _csv_buf.write("# === INTENTOS ===\n")
                        if not _df_att_exp.empty:
                            _df_att_exp.to_csv(_csv_buf, index=False)
                        _csv_buf.write("\n# === MATRÍCULAS ===\n")
                        if not _df_enr_exp.empty:
                            _df_enr_exp.to_csv(_csv_buf, index=False)
                        _csv_buf.write("\n# === PROCEDIMIENTOS ===\n")
                        if not _df_proc_exp.empty:
                            _df_proc_exp.to_csv(_csv_buf, index=False)
                        _csv_buf.write("\n# === INTERACCIONES KATIA ===\n")
                        if not _df_katia_exp.empty:
                            _df_katia_exp.to_csv(_csv_buf, index=False)
                        st.download_button(
                            "⬇️ Descargar CSV",
                            data=_csv_buf.getvalue(),
                            file_name=f"LevelUp_datos_{_grp_label}_{_ts_label}.csv",
                            mime="text/csv",
                            key="tch_dl_csv",
                        )
                    else:
                        import io as _io
                        _xlsx_buf = _io.BytesIO()
                        with pd.ExcelWriter(_xlsx_buf, engine='openpyxl') as _writer:
                            if not _df_att_exp.empty:
                                _df_att_exp.to_excel(_writer, sheet_name='Intentos', index=False)
                            if not _df_enr_exp.empty:
                                _df_enr_exp.to_excel(_writer, sheet_name='Matrículas', index=False)
                            if not _df_proc_exp.empty:
                                _df_proc_exp.to_excel(_writer, sheet_name='Procedimientos', index=False)
                            if not _df_katia_exp.empty:
                                _df_katia_exp.to_excel(_writer, sheet_name='KatIA', index=False)
                        st.download_button(
                            "⬇️ Descargar Excel",
                            data=_xlsx_buf.getvalue(),
                            file_name=f"LevelUp_datos_{_grp_label}_{_ts_label}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="tch_dl_xlsx",
                        )

                    st.success(
                        f"✅ Datos listos: {len(_exp_attempts)} intentos, "
                        f"{len(_exp_enrollments)} matrículas, "
                        f"{len(_exp_procedures)} procedimientos, "
                        f"{len(_exp_katia)} interacciones KatIA."
                    )

    # ══════════════════════════════════════════════════════════════════════════
    # VISTA: ESTUDIANTE (sin cambios funcionales)
    # ══════════════════════════════════════════════════════════════════════════
    else:
        # 1. Recuperar Estado Inicial de DB para VectorELO
        if 'vector_initialized' not in st.session_state:
            latest_elos = cached('cache_elo_by_topic',
                                 lambda: st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id))
            st.session_state.vector = VectorRating()
            for topic, (elo, rd) in latest_elos.items():
                st.session_state.vector.ratings[topic] = (elo, rd)
            st.session_state.vector_initialized = True

        if 'session_correct_ids' not in st.session_state:
            st.session_state.session_correct_ids = set()
        if 'session_wrong_timestamps' not in st.session_state:
            st.session_state.session_wrong_timestamps = {}
        if 'session_questions_count' not in st.session_state:
            st.session_state.session_questions_count = 0
        if 'streak_correct' not in st.session_state:
            st.session_state.streak_correct = 0

        # ── Saludo de KatIA al iniciar sesión (una sola vez) ─────────────────
        if not st.session_state.get('katia_greeted') and _KATIA_IMG:
            st.session_state.katia_greeted = True
            st.toast(get_random_message(MENSAJES_BIENVENIDA), icon="🐱")

        # ── Onboarding: nivel educativo ──────────────────────────────────────
        if 'education_level' not in st.session_state:
            st.session_state.education_level = cached('cache_edu_level',
                                                       lambda: repo.get_education_level(st.session_state.user_id))

        if not st.session_state.education_level:
            st.title("🎓 Bienvenido a LevelUp ELO")
            st.markdown("### ¿En qué nivel educativo estás?")
            st.markdown("Esto nos permite mostrarte los cursos adecuados para ti.")
            st.write("")
            col_uni, col_col, col_con = st.columns(3)
            with col_uni:
                with st.container(border=True):
                    st.markdown("#### 🎓 Universidad")
                    st.write("Cálculo, Álgebra Lineal, EDO, Probabilidad, Estadística")
                    st.write("")
                    if st.button("Soy universitario", width='stretch', type="primary", key="onb_uni"):
                        repo.set_education_level(st.session_state.user_id, 'universidad')
                        st.session_state.education_level = 'universidad'
                        st.rerun()
            with col_col:
                with st.container(border=True):
                    st.markdown("#### 🏫 Colegio")
                    st.write("Álgebra Básica, Aritmética, Trigonometría, Geometría")
                    st.write("")
                    if st.button("Soy de colegio", width='stretch', key="onb_col"):
                        repo.set_education_level(st.session_state.user_id, 'colegio')
                        st.session_state.education_level = 'colegio'
                        st.rerun()
            with col_con:
                with st.container(border=True):
                    st.markdown("#### 🏆 Concursos")
                    st.write("Preparación para concursos públicos: DIAN, SENA y más")
                    st.write("")
                    if st.button("Preparo concursos", width='stretch', key="onb_con"):
                        repo.set_education_level(st.session_state.user_id, 'concursos')
                        st.session_state.education_level = 'concursos'
                        st.rerun()
            st.stop()

        # Cargar cursos matriculados filtrados por nivel educativo del estudiante.
        # Regla: se muestran cursos del bloque propio + cursos de otro bloque solo si
        # tienen group_id (matrícula con permiso especial vía código de profesor).
        # Las matrículas legacy sin grupo (group_id=None) de otro bloque se ocultan.
        _level = st.session_state.education_level or 'universidad'
        if _level == 'semillero':
            _sem_grade_blk = st.session_state.get('student_grade') or repo.get_grade(st.session_state.user_id)
            st.session_state['student_grade'] = _sem_grade_blk
            _student_block = f'Semillero {_sem_grade_blk}°' if _sem_grade_blk else 'Semillero'
        else:
            _student_block = LEVEL_TO_BLOCK.get(_level, 'Universidad')
        _enrolled = [
            c for c in cached('cache_enrollments',
                              lambda: repo.get_user_enrollments(st.session_state.user_id))
            if c.get('block') == _student_block                                          # nivel propio
            or (c.get('block') != _student_block and c.get('group_id') is not None)     # acceso especial vía código
        ]

        # ── Banner "sin grupo asignado" ──────────────────────────────────────
        # Se muestra si el estudiante no tiene ninguna matrícula con grupo asignado
        _all_enroll = cached('cache_all_enrollments',
                             lambda: repo.get_user_enrollments(st.session_state.user_id))
        _has_group = any(e.get('group_id') for e in _all_enroll)
        if not _has_group:
            st.info(
                f"👋 Aún no perteneces a ningún grupo. "
                f"Comparte tu nombre de usuario **{st.session_state.username}** "
                f"con tu profesor para que te agregue y puedas acceder a tus cursos."
            )

        # Defaults para variables usadas en las vistas
        selected_course_id = None
        selected_topic = None

        # T4b: inicializar set de entregas ya vistas por el estudiante en esta sesión.
        # Al abrir el Centro de Feedback se marcan como vistas.
        if 'fb_seen_ids' not in st.session_state:
            st.session_state.fb_seen_ids = set()

        # T4b: calcular cuántas retroalimentaciones nuevas hay (revisadas - vistas)
        _reviewed_ids = cached('cache_reviewed_ids',
                               lambda: repo.get_reviewed_submission_ids(st.session_state.user_id))
        _unseen_fb = _reviewed_ids - st.session_state.fb_seen_ids
        _fb_badge = f" 🆕 {len(_unseen_fb)}" if _unseen_fb else ""

        # Sidebar Estilizado
        with st.sidebar:
            st.image(_get_logo(), width=180)
            st.write(f"### Hola, **{st.session_state.username}**")
            # ── Temporizador de sesión (tiempo real) ──────────────────────────
            _sess_start = st.session_state.get('session_start_time')
            if _sess_start:
                _render_live_timer(
                    _sess_start, label="⏱️ Sesión: ",
                    font_size="0.85rem", height=30, color="#aaa", bold=False,
                )
            _mode_options = ["📝 Practicar", "📊 Estadísticas", "🎓 Mis Cursos", f"💬 Feedback{_fb_badge}"]
            _pending = st.session_state.pop("_pending_student_mode", None)
            _default_idx = 0
            if _pending and _pending in _mode_options:
                _default_idx = _mode_options.index(_pending)
            mode = st.radio(
                "Modo",
                _mode_options,
                index=_default_idx,
                label_visibility="collapsed",
                key="student_mode_radio",
            )
            st.caption("Navegación Principal")

            if mode == "📝 Practicar":
                if _enrolled and 'selected_course' in st.session_state:
                    _sc = st.session_state.selected_course
                    st.markdown(f"### 📚 {_sc['name']}")
                    if st.button("↩ Cambiar materia", key="sidebar_change_course"):
                        del st.session_state.selected_course
                        st.session_state.question_start_time = None
                        st.session_state.pop('katia_chat_history', None)
                        st.rerun()

            st.markdown("---")
            # ── Badge de estado de IA (siempre visible) ───────────────────────
            _badge_p = st.session_state.get('ai_provider')
            _badge_ok = st.session_state.get('ai_available', False)
            if not _badge_ok or not _badge_p:
                st.markdown("⚠️ **Sin backend de IA**")
            elif _badge_p == 'lmstudio':
                st.markdown("🟢 **Local Conectada**")
            else:
                _badge_label = ai_mod.PROVIDERS.get(_badge_p, {}).get('label', _badge_p)
                _badge_name = _badge_label.split(' ', 1)[-1] if _badge_label else _badge_p
                st.markdown(f"🔵 **{_badge_name} Activo**")
            with st.expander("⚙️ Configuración de IA"):
                st.caption("🔧 **Proveedor de IA**")
                _s_mode = st.radio(
                    "Modo IA",
                    ["🤖 Auto", "☁️ API Key", "🖥️ Local"],
                    index=["auto", "cloud", "local"].index(st.session_state.get('ai_provider_mode', 'auto')),
                    key="provider_radio_st",
                    label_visibility="collapsed",
                    horizontal=True,
                )
                _new_mode_s = {"🤖 Auto": "auto", "☁️ API Key": "cloud", "🖥️ Local": "local"}[_s_mode]
                # T9b: limpiar API key al cambiar de modo para evitar mezclas entre proveedores
                if st.session_state.ai_provider_mode != _new_mode_s:
                    st.session_state.cloud_api_key = None
                    st.session_state.ai_provider_mode = _new_mode_s

                if _s_mode == "🤖 Auto":
                    if st.button("🔄 Reconectar", key="btn_reconnect_ai"):
                        for _k in ('ai_available', 'lmstudio_models'):
                            st.session_state.pop(_k, None)
                        st.rerun()
                elif _s_mode == "☁️ API Key":
                    _env_key = os.getenv("GROQ_API_KEY")
                    if _env_key:
                        # Remoto (Streamlit Cloud): key disponible en entorno, no mostrar input
                        if st.session_state.cloud_api_key != _env_key:
                            st.session_state.cloud_api_key = _env_key
                            _detected_st = ai_mod.detect_provider_from_key(_env_key)
                            st.session_state.ai_provider = _detected_st or 'groq'
                            _pinfo_st = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {})
                            st.session_state.model_cog = _pinfo_st.get('model_cog') or st.session_state.model_cog
                            st.session_state.model_analysis = _pinfo_st.get('model_analysis') or st.session_state.model_analysis
                            st.session_state.student_service.cognitive_analyzer.model_name = st.session_state.model_cog
                            st.session_state.ai_available = True
                        _plabel_st = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {}).get('label', st.session_state.ai_provider)
                        st.caption(f"🔒 Modelo activo: **{_plabel_st}**")
                    else:
                        # Local: el usuario ingresa la key manualmente
                        _key_in_st = st.text_input(
                            "API Key", type="password",
                            value="",
                            placeholder="sk-ant-… / gsk_… / sk-… / AIzaSy…",
                            key="cloud_key_st",
                        )
                        st.caption("🔒 Tus credenciales son seguras y no se almacenan en ninguna base de datos.")
                        if _key_in_st:
                            _detected_st = ai_mod.detect_provider_from_key(_key_in_st)
                            st.session_state.cloud_api_key = _key_in_st
                            st.session_state.ai_provider = _detected_st or 'groq'
                            _pinfo_st = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {})
                            st.session_state.model_cog = _pinfo_st.get('model_cog') or st.session_state.model_cog
                            st.session_state.model_analysis = _pinfo_st.get('model_analysis') or st.session_state.model_analysis
                            st.session_state.student_service.cognitive_analyzer.model_name = st.session_state.model_cog
                            st.session_state.ai_available = True
                            _plabel_st = _pinfo_st.get('label', st.session_state.ai_provider)
                            st.success(f"{_plabel_st} detectado")
                        else:
                            st.caption("Soporta: Groq, OpenAI, Anthropic, Gemini, HuggingFace")
                elif _s_mode == "🖥️ Local":
                    _local_url_st = st.text_input("URL servidor local", value=st.session_state.ai_url, key="lm_url_st")
                    st.session_state.ai_url = _local_url_st
                    if st.button("🔍 Detectar modelos", key="btn_detect_lm"):
                        _det = ai_mod.detect_lmstudio(st.session_state.ai_url)
                        st.session_state.lmstudio_models = _det['models']
                        if _det['available']:
                            st.session_state.ai_available = True
                            st.session_state.ai_provider = 'lmstudio'
                            st.session_state.cloud_api_key = None
                            # T6c: si hay curso activo de matemáticas, priorizar modelo
                            # con mejor razonamiento matemático de la lista de preferencia
                            _math_best = ai_mod.select_best_math_model(
                                _det['models'], provider='ollama',
                            )
                            _best = _math_best or ai_mod.select_best_model(_det['models'])
                            if _best:
                                st.session_state.model_cog = _best
                                st.session_state.model_analysis = _best
                                st.session_state.student_service.cognitive_analyzer.model_name = _best
                            st.rerun()
                        else:
                            st.error("Servidor no detectado en esa URL")
                    _models = st.session_state.get('lmstudio_models', [])
                    if _models:
                        _sel_idx = _models.index(st.session_state.model_cog) if st.session_state.model_cog in _models else 0
                        _sel = st.selectbox("Modelo activo", _models, index=_sel_idx, key="lm_model_sel")
                        if _sel != st.session_state.model_cog:
                            st.session_state.model_cog = _sel
                            st.session_state.model_analysis = _sel
                            st.session_state.student_service.cognitive_analyzer.model_name = _sel
                        st.session_state.ai_available = True
                        st.session_state.ai_provider = 'lmstudio'
                    else:
                        st.caption("Pulsa 'Detectar modelos' para listar los disponibles")

            with st.expander("🔧 Reportar un problema"):
                _report_desc = st.text_area(
                    "Describe el problema",
                    placeholder="Ej: No puedo ver las imágenes de las preguntas...",
                    max_chars=500,
                    key="problem_report_desc",
                    label_visibility="collapsed",
                )
                if st.button("Enviar reporte", key="btn_send_report"):
                    if _report_desc and len(_report_desc.strip()) >= 10:
                        repo.save_problem_report(st.session_state.user_id, _report_desc.strip())
                        st.success("Reporte enviado. El administrador lo revisará pronto.")
                        st.session_state.pop('problem_report_desc', None)
                        st.rerun()
                    else:
                        st.warning("Describe el problema con al menos 10 caracteres.")

            if st.button("Cerrar Sesión"):
                if _KATIA_IMG:
                    st.toast(get_random_message(MENSAJES_DESPEDIDA), icon="🐱")
                    time.sleep(1.5)
                logout()

        # --- LÓGICA DE ACTUALIZACIÓN ---
        def handle_answer_topic(is_correct, item_data, reasoning=""):
            st.session_state['last_was_correct'] = is_correct

            # --- Cálculo de Modificadores Cognitivos ---
            time_taken = 0.0
            if st.session_state.question_start_time:
                time_taken = time.time() - st.session_state.question_start_time

            # Configurar el servicio con los parámetros de IA de la sesión
            st.session_state.student_service.cognitive_analyzer.base_url = st.session_state.ai_url
            st.session_state.student_service.cognitive_analyzer.model_name = st.session_state.model_cog

            # Delegar procesamiento al servicio.
            # elo_topic = nombre del curso (selected_topic), para que cursos con
            # subtemas heterogéneos (DIAN, SENA) consoliden ELO en una sola clave.
            _elo_topic = st.session_state.selected_course['name']
            is_correct, cog_data = st.session_state.student_service.process_answer(
                st.session_state.user_id, item_data,
                # La opción seleccionada se recupera del texto mapeado (soporte LaTeX)
                st.session_state.get(f"answer_text_{item_data['id']}"),
                reasoning, time_taken, st.session_state.vector,
                elo_topic=_elo_topic,
            )

            st.session_state.session_questions_count += 1
            if is_correct:
                st.session_state.session_correct_ids.add(item_data['id'])
            else:
                st.session_state.session_wrong_timestamps[item_data['id']] = float(st.session_state.session_questions_count)

            # Invalidar caches afectados por save_attempt
            invalidate_cache('cache_answered_ids', 'cache_elo_by_topic', 'cache_streak',
                             f'cache_streak_{selected_course_id}', 'cache_weekly_ranking',
                             'cache_course_ranking', 'cache_teachers_groups')

            st.session_state.question_start_time = None
            # Marcar que estamos mostrando el resultado (no avanzar automáticamente)
            st.session_state.show_result = True
            st.session_state.last_result_correct = is_correct
            st.session_state.last_result_item = item_data
            st.rerun()

        # --- VISTAS ---
        # ── Pantalla de bienvenida (primer acceso sin matrículas) ───────────
        if not _enrolled and not st.session_state.get('welcome_dismissed'):
            st.markdown("""
                <div style='text-align:center; padding:2rem 1rem;'>
                    <div style='font-size:4rem;'>🎓</div>
                    <h1 style='font-size:2rem; margin:0.5rem 0;'>¡Bienvenido a LevelUp-ELO!</h1>
                    <p style='color:#aaa; font-size:1rem; max-width:600px; margin:0.5rem auto;'>
                        La plataforma que adapta cada pregunta a tu nivel usando el sistema de rating ELO
                        — el mismo del ajedrez competitivo. Cuanto más practiques, más preciso se vuelve.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            _wc1, _wc2, _wc3 = st.columns(3)
            with _wc1:
                st.markdown("""
                    <div style='background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;'>
                        <div style='font-size:2rem;'>📚</div>
                        <b>1. Elige tu profesor</b>
                        <p style='color:#aaa; font-size:0.85rem; margin-top:0.5rem;'>
                            Ve a <b>Mis Cursos</b> y explora los profesores disponibles para tu nivel.
                            Elige el que prefieras para cada materia.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            with _wc2:
                st.markdown("""
                    <div style='background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;'>
                        <div style='font-size:2rem;'>⚡</div>
                        <b>2. Practica a tu ritmo</b>
                        <p style='color:#aaa; font-size:0.85rem; margin-top:0.5rem;'>
                            El sistema selecciona preguntas en tu zona de desarrollo óptimo:
                            ni muy fáciles ni imposibles.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            with _wc3:
                st.markdown("""
                    <div style='background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;'>
                        <div style='font-size:2rem;'>📈</div>
                        <b>3. Sube tu rating</b>
                        <p style='color:#aaa; font-size:0.85rem; margin-top:0.5rem;'>
                            Cada respuesta actualiza tu ELO en tiempo real.
                            Escala los 16 niveles desde Aspirante hasta Leyenda Suprema.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            st.write("")
            _wb1, _wb2, _wb3 = st.columns([2, 2, 1])
            with _wb1:
                if st.button("🎓 Ir a Mis Cursos", type="primary", use_container_width=True, key="welcome_goto_courses"):
                    st.session_state.welcome_dismissed = True
                    st.session_state._pending_student_mode = "🎓 Mis Cursos"
                    st.rerun()
            with _wb2:
                if st.button("🔑 Tengo un código de invitación", use_container_width=True, key="welcome_goto_code"):
                    st.session_state.welcome_dismissed = True
                    st.session_state._pending_student_mode = "🎓 Mis Cursos"
                    st.session_state.welcome_open_code_tab = True
                    st.rerun()
            with _wb3:
                if st.button("Explorar primero", use_container_width=True, key="welcome_dismiss"):
                    st.session_state.welcome_dismissed = True
                    st.rerun()

        elif mode == "📝 Practicar" and not _enrolled:
            st.title("🚀 Sala de Estudio")
            st.info("📚 Aún no tienes cursos inscritos. Ve a **🎓 Mis Cursos** en el menú lateral para matricularte.")
        elif mode == "📝 Practicar" and 'selected_course' not in st.session_state:
            # ── Pantalla de selección de curso ──────────────────────────────
            st.title("🚀 Sala de Estudio")
            if _level == 'semillero':
                _sem_grade = st.session_state.get('student_grade') or repo.get_grade(st.session_state.user_id)
                st.session_state['student_grade'] = _sem_grade
                _grade_label = f" — Grado {_sem_grade}°" if _sem_grade else ""
                st.markdown(f"### 🏅 Semillero de Matemáticas — Preparación Olimpiadas de Matemáticas{_grade_label}")
                st.markdown("---")
            st.markdown("#### Selecciona la materia que deseas practicar")
            st.markdown("")

            # Grid de cards: 2 columnas
            for row_start in range(0, len(_enrolled), 2):
                cols = st.columns(2)
                for col_idx, course in enumerate(_enrolled[row_start:row_start + 2]):
                    c_name = course['name']
                    c_elo = st.session_state.vector.get(c_name)
                    c_rank, c_color = get_rank(c_elo)
                    # Posición del estudiante en esta materia
                    _c_rank_info = repo.get_student_rank(st.session_state.user_id, course['id'])
                    _c_rank_text = (f"📊 Tu posición: #{_c_rank_info['rank']} de {_c_rank_info['total_students']} estudiantes"
                                    if _c_rank_info else "Sin posición aún")
                    _c_special = course.get('block') != _student_block
                    _c_special_html = '<p style="color:#FFD700; font-size:0.7rem; margin:4px 0 0;">📌 Acceso especial</p>' if _c_special else ''
                    with cols[col_idx]:
                        _banner_b64 = _get_banner_b64(c_name)
                        _banner_html = (
                            f'<img src="data:image/png;base64,{_banner_b64}" '
                            f'style="width:100%;border-radius:16px 16px 0 0;display:block;">'
                        ) if _banner_b64 else ''
                        _top_radius = '0' if _banner_b64 else '16px'
                        _card_html = (
                            f'<div style="border-radius:16px;'
                            f'background:rgba(38,39,48,0.95);'
                            f'border:1px solid {c_color}44;'
                            f'box-shadow:0 4px 20px {c_color}22;'
                            f'overflow:hidden;margin-bottom:12px;">'
                            + _banner_html +
                            f'<div style="padding:20px 24px;text-align:center;">'
                            f'<h3 style="color:#fff!important;margin:0 0 12px 0;'
                            f'border-left:none;padding-left:0;'
                            f'background:linear-gradient(90deg,#00C9FF,#92FE9D);'
                            f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
                            f'{c_name}</h3>'
                            + _c_special_html +
                            f'<p style="color:{c_color};font-size:0.9rem;margin:0;">{c_rank}</p>'
                            f'<p style="color:#fff;font-size:2.4rem;font-weight:700;margin:4px 0;">'
                            f'{c_elo:.0f}</p>'
                            f'<p style="color:#888;font-size:0.8rem;margin:0;">Puntos ELO</p>'
                            f'<p style="color:#aaa;font-size:0.8rem;margin:6px 0 0;">{_c_rank_text}</p>'
                            f'</div>'
                            f'</div>'
                        )
                        st.markdown(_card_html, unsafe_allow_html=True)
                        if st.button(f"Practicar", key=f"sel_course_{course['id']}",
                                     width='stretch'):
                            st.session_state.selected_course = course
                            st.session_state.question_start_time = None
                            st.session_state.pop('current_question', None)
                            st.rerun()

            # ── Ranking General por nivel educativo — Top 5 ──────────────
            st.markdown("---")
            _level_label = {'universidad': 'Universidad', 'colegio': 'Colegio', 'concursos': 'Concursos', 'semillero': 'Semillero'}.get(_level, _level.title())
            # Para semillero: sub-filtro por grado del propio estudiante
            _rank_grade = None
            if _level == 'semillero':
                _rank_grade = st.session_state.get('student_grade') or repo.get_grade(st.session_state.user_id)
                st.session_state['student_grade'] = _rank_grade
                _grade_suffix = f" — Grado {_rank_grade}°" if _rank_grade else ""
                st.markdown(f"#### 🏆 Ranking General — {_level_label}{_grade_suffix}")
            else:
                st.markdown(f"#### 🏆 Ranking General — {_level_label}")
            _global_top = repo.get_global_ranking(limit=5, education_level=_level, grade=_rank_grade)
            if _global_top:
                _medal_sel = {1: "🥇", 2: "🥈", 3: "🥉"}
                _my_user_sel = st.session_state.username
                _in_top_sel = False
                _grank_html = "<table style='width:100%; border-collapse:collapse; font-size:0.9rem;'>"
                _grank_html += "<tr style='border-bottom:1px solid #444;'><th style='padding:4px 6px;'>🏅</th><th style='padding:4px 6px; text-align:left;'>Estudiante</th><th style='padding:4px 6px;'>ELO</th><th style='padding:4px 6px;'>Intentos</th></tr>"
                for _r in _global_top:
                    _is_me_sel = (_r['username'] == _my_user_sel)
                    if _is_me_sel:
                        _in_top_sel = True
                    _bg_sel = "background:rgba(255,215,0,0.15); font-weight:700;" if _is_me_sel else ""
                    _pos_sel = _medal_sel.get(_r['rank'], str(_r['rank']))
                    _grank_html += f"<tr style='{_bg_sel} border-bottom:1px solid #333;'>"
                    _grank_html += f"<td style='padding:4px 6px; text-align:center;'>{_pos_sel}</td>"
                    _grank_html += f"<td style='padding:4px 6px;'>{_r['username']}</td>"
                    _grank_html += f"<td style='padding:4px 6px; text-align:center;'>{_r['global_elo']:.0f}</td>"
                    _grank_html += f"<td style='padding:4px 6px; text-align:center;'>{_r['attempts_this_week']}</td>"
                    _grank_html += "</tr>"
                _grank_html += "</table>"
                st.markdown(_grank_html, unsafe_allow_html=True)
                if not _in_top_sel:
                    _my_global_rank = repo.get_student_rank(st.session_state.user_id, education_level=_level, grade=_rank_grade)
                    if _my_global_rank:
                        st.caption(f"Tu posición: #{_my_global_rank['rank']} de {_my_global_rank['total_students']} 🎯")
                    else:
                        st.caption("Practica esta semana para aparecer en el ranking")
            else:
                st.caption(f"Sin actividad esta semana en {_level_label}.")

        elif mode == "📝 Practicar":
            selected_course_id = st.session_state.selected_course['id']
            selected_topic = st.session_state.selected_course['name']
            current_elo_display = st.session_state.vector.get(selected_topic)
            current_rd_display = st.session_state.vector.get_rd(selected_topic)
            topic_display_name = selected_topic

            rank_name, rank_color = get_rank(current_elo_display)

            st.title("🚀 Sala de Estudio")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"""
                    <div class="elo-card">
                        <p style="color: #aaa; margin-bottom: 5px; font-weight: 600;">NIVEL ACTUAL</p>
                        <h2 style="color: {rank_color}; margin: 0; text-shadow: 0 0 10px {rank_color};">{rank_name}</h2>
                        <h1 style="font-size: 3.5rem; margin: 10px 0; color: white;">{current_elo_display:.0f}</h1>
                        <p style="color: #aaa; font-size: 0.9rem;">Puntos ELO · {topic_display_name}</p>
                    </div>
                """, unsafe_allow_html=True)
                # T8c: racha de estudio (días consecutivos en este curso)
                _streak = cached(f'cache_streak_{selected_course_id}',
                                lambda: repo.get_study_streak(st.session_state.user_id, selected_course_id))
                if _streak == 0:
                    st.markdown("""
                        <div style="text-align:center; padding:12px 8px; background:linear-gradient(135deg,#1a1a2e,#16213e);
                                    border-radius:12px; margin-bottom:12px;">
                            <div style="font-size:2rem;">💤</div>
                            <p style="color:#aaa; margin:4px 0 0; font-size:0.9rem;">Empieza hoy tu racha de estudio</p>
                        </div>
                    """, unsafe_allow_html=True)
                elif _streak <= 2:
                    st.markdown(f"""
                        <div style="text-align:center; padding:12px 8px; background:linear-gradient(135deg,#1a1a2e,#2d1b00);
                                    border-radius:12px; margin-bottom:12px;">
                            <div style="font-size:2.5rem;">🔥</div>
                            <div style="font-size:2rem; font-weight:800; color:#FF9800;">{_streak} día{'s' if _streak != 1 else ''}</div>
                            <p style="color:#FFB74D; margin:2px 0 0; font-size:0.85rem;">¡Buen inicio!</p>
                        </div>
                    """, unsafe_allow_html=True)
                elif _streak <= 6:
                    st.markdown(f"""
                        <div style="text-align:center; padding:12px 8px; background:linear-gradient(135deg,#1a1a2e,#4a1500);
                                    border-radius:12px; margin-bottom:12px;">
                            <div style="font-size:2.5rem;">🔥🔥</div>
                            <div style="font-size:2rem; font-weight:800; color:#FF5722;">{_streak} días</div>
                            <p style="color:#FF8A65; margin:2px 0 0; font-size:0.85rem;">¡Vas en racha!</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="text-align:center; padding:14px 8px; background:linear-gradient(135deg,#4a0000,#ff4500,#ff8c00);
                                    border-radius:12px; margin-bottom:12px; box-shadow:0 0 15px rgba(255,69,0,0.3);">
                            <div style="font-size:3rem;">🔥🔥🔥</div>
                            <div style="font-size:2.2rem; font-weight:900; color:#fff;">{_streak} días</div>
                            <p style="color:#FFE0B2; margin:2px 0 0; font-size:0.9rem; font-weight:700;">¡IMPARABLE!</p>
                        </div>
                    """, unsafe_allow_html=True)
                st.info("💡 **Consejo:** La constancia es clave. Practica diariamente para consolidar tu aprendizaje.")

                # ── Ranking del curso actual Top 5 ──────────────────────────
                _ranking = cached('cache_course_ranking',
                                  lambda: repo.get_course_ranking(selected_course_id, limit=5))
                if _ranking:
                    st.markdown(f"#### 🏆 Ranking — {topic_display_name}")
                    _medal = {1: "🥇", 2: "🥈", 3: "🥉"}
                    _my_user = st.session_state.username
                    _in_top = False
                    _rank_html = "<table style='width:100%; border-collapse:collapse; font-size:0.9rem;'>"
                    _rank_html += "<tr style='border-bottom:1px solid #444;'><th style='padding:4px 6px;'>🏅</th><th style='padding:4px 6px; text-align:left;'>Estudiante</th><th style='padding:4px 6px;'>ELO</th><th style='padding:4px 6px;'>Intentos</th></tr>"
                    for _r in _ranking:
                        _is_me = (_r['username'] == _my_user)
                        if _is_me:
                            _in_top = True
                        _bg = "background:rgba(255,215,0,0.15); font-weight:700;" if _is_me else ""
                        _pos = _medal.get(_r['rank'], str(_r['rank']))
                        _rank_html += f"<tr style='{_bg} border-bottom:1px solid #333;'>"
                        _rank_html += f"<td style='padding:4px 6px; text-align:center;'>{_pos}</td>"
                        _rank_html += f"<td style='padding:4px 6px;'>{_r['username']}</td>"
                        _rank_html += f"<td style='padding:4px 6px; text-align:center;'>{_r['course_elo']:.0f}</td>"
                        _rank_html += f"<td style='padding:4px 6px; text-align:center;'>{_r['attempts_this_week']}</td>"
                        _rank_html += "</tr>"
                    _rank_html += "</table>"
                    st.markdown(_rank_html, unsafe_allow_html=True)
                    if _in_top:
                        st.caption("¡Estás en el Top 5! 🎯")
                    else:
                        _my_rank = repo.get_student_rank(st.session_state.user_id, course_id=selected_course_id)
                        if _my_rank:
                            st.caption(f"Tu posición: #{_my_rank['rank']} de {_my_rank['total_students']} 🎯")
                        else:
                            st.caption("Sigue practicando para entrar al ranking")
                else:
                    st.markdown(f"#### 🏆 Ranking — {topic_display_name}")
                    st.caption("Sin actividad esta semana en este curso.")

            with col2:
                st.subheader(f"📖 Ejercicio: {selected_topic}")
                item_data = None  # inicializar para scope exterior (procedimiento manuscrito)

                # ── Pantalla de celebración KatIA (bloquea vista de pregunta) ──
                if st.session_state.get('show_celebration'):
                    _cel_sc = st.session_state.get('celebration_streak', 5)
                    _cel_elo = st.session_state.get('celebration_elo', 1000)
                    _cel_msg = get_streak_message(_cel_sc)

                    # Animación diferenciada por tier
                    if _cel_sc >= 20 and _cel_sc % 20 == 0:
                        st.balloons()
                        st.snow()
                    elif _cel_sc >= 10 and _cel_sc % 10 == 0:
                        st.snow()
                    else:
                        st.balloons()

                    # Imagen de KatIA centrada
                    if _KATIA_IMG:
                        _kc1, _kc2, _kc3 = st.columns([1, 2, 1])
                        with _kc2:
                            st.image(_KATIA_IMG, width=180)

                    st.markdown(f"""
                        <div style="text-align:center; padding:48px 24px; margin:20px 0;
                                    background:linear-gradient(135deg,#6a0dad 0%,#ffd700 50%,#ff8c00 100%);
                                    border-radius:24px; box-shadow:0 0 40px rgba(255,215,0,0.6);">
                            <div style="font-size:2rem; font-weight:900; color:white; margin-bottom:8px;
                                        text-shadow:0 2px 8px rgba(0,0,0,0.3);">
                                {_cel_sc} RESPUESTAS CORRECTAS</div>
                            <div style="font-size:1.2rem; font-weight:600; color:rgba(255,255,255,0.95);
                                        margin-bottom:16px; font-style:italic;">
                                {_cel_msg}</div>
                            <div style="display:inline-block; background:rgba(0,0,0,0.25); border-radius:12px;
                                        padding:10px 24px;">
                                <span style="color:#ffd700; font-size:1.1rem; font-weight:700;">
                                    Tu ELO actual: {_cel_elo:.0f} puntos</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button("🐾 SEGUIR PRACTICANDO", width='stretch', type="primary", key="btn_continue_cel"):
                        st.session_state.show_celebration = False
                        st.session_state.pop('current_question', None)
                        st.session_state.pop('katia_chat_history', None)
                        st.rerun()

                # ── Pantalla de resultado (después de responder) ─────────
                elif st.session_state.get('show_result'):
                    _res_correct = st.session_state.get('last_result_correct', False)
                    _res_elo_before = st.session_state.get('last_result_elo_before', current_elo_display)
                    _res_elo_after = st.session_state.vector.get(selected_topic)
                    _res_delta = _res_elo_after - _res_elo_before
                    _delta_str = f"+{_res_delta:.0f}" if _res_delta >= 0 else f"{_res_delta:.0f}"

                    if _res_correct:
                        st.success(f"¡Respuesta correcta! 🎓   {_delta_str} pts  ·  Tu ELO: **{_res_elo_after:.0f}**")
                    else:
                        st.error(f"Respuesta incorrecta.   {_delta_str} pts  ·  Tu ELO: **{_res_elo_after:.0f}**")
                        st.info("💡 ¿Quieres entender el concepto? Pregúntale a KatIA abajo — te guiará sin revelar la respuesta.")

                    st.write("")
                    if st.button("▶️ SIGUIENTE PREGUNTA", width='stretch', type="primary", key="btn_next_question"):
                        st.session_state.show_result = False
                        st.session_state.pop('current_question', None)
                        st.session_state.pop('last_result_item', None)
                        st.session_state.pop('last_result_correct', None)
                        st.session_state.pop('last_result_elo_before', None)
                        st.session_state.pop('katia_chat_history', None)
                        st.rerun()

                else:
                    # ── Vista normal: pregunta activa ─────────────────────
                    # Delegar obtención de pregunta al servicio (una sola vez por recarga)
                    if 'current_question' not in st.session_state:
                        st.session_state.current_question = st.session_state.student_service.get_next_question(
                            st.session_state.user_id, selected_topic, st.session_state.vector,
                            session_correct_ids=st.session_state.session_correct_ids,
                            session_wrong_timestamps=st.session_state.session_wrong_timestamps,
                            session_questions_count=st.session_state.session_questions_count,
                            course_id=selected_course_id,
                        )
                    item_data, status = st.session_state.current_question

                    if status == "mastery":
                        st.success("🎉 ¡Excelente trabajo! Has alcanzado el nivel de excelencia en esta materia.")
                        st.balloons()
                        item_data = None
                    elif status == "empty":
                        st.warning("No hay preguntas disponibles para tu nivel actual.")
                        item_data = None

                    if item_data:
                        # Iniciar cronómetro si es una nueva pregunta
                        if st.session_state.question_start_time is None:
                            st.session_state.question_start_time = time.time()

                        # ── Temporizador en tiempo real por pregunta ───────────
                        _render_live_timer(
                            st.session_state.question_start_time,
                            label="⏱️ ",
                            font_size="1.3rem", height=45, color="#FFD700", bold=True,
                        )

                        with st.container(border=True):
                            diff = item_data.get('difficulty') or 1000

                            def get_difficulty_label(d):
                                if d < 750:  return 1, "Fácil"
                                if d < 950:  return 2, "Básico"
                                if d < 1150: return 3, "Intermedio"
                                if d < 1400: return 4, "Difícil"
                                return 5, "Experto"

                            _nstars, _dlabel = get_difficulty_label(diff)
                            _filled = "★" * _nstars
                            _empty  = "★" * (5 - _nstars)
                            _item_topic = item_data.get('topic') or selected_topic or ''
                            st.caption(f"Área: {selected_topic} | Tema: {_item_topic}")
                            # ── Tag badges (3 dimensiones de la taxonomía) ────────────────
                            _tags = item_data.get('tags') or []
                            if _tags:
                                def _tag_style(tag):
                                    if tag.startswith('[Enfoque:'):
                                        return '#1565C0', '#E3F2FD'   # azul — cognitivo
                                    if tag.startswith('[General:'):
                                        return '#2E7D32', '#E8F5E9'   # verde — transversal
                                    if tag.startswith('[Específica:'):
                                        return '#B45309', '#FFF8E1'   # ámbar — conocimiento
                                    return '#555555', '#EEEEEE'
                                _badges = ''.join(
                                    '<span style="'
                                    f'background:{_tag_style(t)[1]};'
                                    f'color:{_tag_style(t)[0]};'
                                    f'border:1px solid {_tag_style(t)[0]};'
                                    'border-radius:4px;padding:2px 8px;'
                                    'font-size:0.72rem;font-weight:600;'
                                    'margin-right:4px;margin-bottom:4px;'
                                    'display:inline-block;line-height:1.6;'
                                    f'">{t[1:-1]}</span>'
                                    for t in _tags
                                )
                                st.markdown(
                                    f'<div style="margin:4px 0 6px 0;">{_badges}</div>',
                                    unsafe_allow_html=True
                                )
                            st.markdown(
                                f"<span style='color:#FFD700; font-weight:700; font-size:1rem;'>{_filled}</span>"
                                f"<span style='color:#444; font-weight:700; font-size:1rem;'>{_empty}</span>"
                                f"<span style='font-weight:600; font-size:0.9rem;'> {_dlabel}</span>"
                                f"<span style='color:#888; font-size:0.8rem;'> · {diff:.0f}</span>",
                                unsafe_allow_html=True
                            )
                            st.markdown(f"### {item_data.get('content') or ''}")

                            _img_url = item_data.get('image_url') or item_data.get('image_path')
                            if _img_url:
                                try:
                                    # Si es ruta local relativa, resolverla desde la raíz del repo
                                    _img_source = _img_url
                                    if not _img_url.startswith('http'):
                                        _abs = os.path.join(base_path, _img_url)
                                        if os.path.isfile(_abs):
                                            with open(_abs, 'rb') as _f:
                                                _img_source = _f.read()
                                    _c1, _c2, _c3 = st.columns([1, 2, 1])
                                    with _c2:
                                        st.image(_img_source, width=420,
                                                 caption="Figura correspondiente a la pregunta")
                                except Exception:
                                    pass

                            st.write("")

                            # ── Stakes preview (puntos en juego) ─────────────
                            # K_BASE = 32.0 según RatingModel en uncertainty.py (fuente de verdad)
                            _p_win = expected_score(current_elo_display, item_data.get('difficulty') or 1000)
                            _k_est = 32.0 * (current_rd_display / 350.0)
                            _pts_up = max(1, round(_k_est * (1 - _p_win)))
                            _pts_dn = max(1, round(_k_est * _p_win))
                            st.markdown(f"""
                            <div style="display:flex; gap:10px; margin:0 0 14px 0;">
                                <span style="background:rgba(76,175,80,0.12); border:1px solid rgba(76,175,80,0.4);
                                             border-radius:8px; padding:4px 14px; color:#66BB6A;
                                             font-size:0.85rem; font-weight:600;">
                                    ✅ +{_pts_up} pts si aciertas
                                </span>
                                <span style="background:rgba(255,75,75,0.10); border:1px solid rgba(255,75,75,0.35);
                                             border-radius:8px; padding:4px 14px; color:#EF5350;
                                             font-size:0.85rem; font-weight:600;">
                                    ❌ −{_pts_dn} pts si fallas
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                            if item_data.get('options'):
                                shuffled_options = item_data['options'].copy()
                                random.Random(item_data['id']).shuffle(shuffled_options)
                                option_labels = [chr(65 + i) for i in range(len(shuffled_options))]
                                label_to_text = dict(zip(option_labels, shuffled_options))
                                _item_id = item_data['id']

                                for lbl, opt in zip(option_labels, shuffled_options):
                                    st.markdown(f"**{lbl}.** {opt}")

                                def _sync_answer(_id=_item_id, _map=label_to_text):
                                    lbl = st.session_state.get(f"radio_{_id}")
                                    st.session_state[f"answer_text_{_id}"] = _map.get(lbl)

                                st.radio(
                                    "Selecciona tu respuesta:",
                                    option_labels,
                                    index=None,
                                    format_func=lambda x: x,
                                    key=f"radio_{item_data['id']}",
                                    on_change=_sync_answer,
                                )
                                selected_option = st.session_state.get(f"answer_text_{item_data['id']}")
                                st.write("")
                                submit_button = st.button(
                                    label="📝 Enviar Respuesta",
                                    width='stretch',
                                    disabled=(selected_option is None),
                                )

                                if submit_button:
                                    st.session_state.last_result_elo_before = current_elo_display
                                    is_correct = (selected_option == item_data.get('correct_option'))
                                    if is_correct:
                                        st.session_state.streak_correct += 1
                                        _sc = st.session_state.streak_correct
                                        if _sc > 0 and _sc % 5 == 0:
                                            # Preparar pantalla de celebración
                                            st.session_state.show_celebration = True
                                            st.session_state.celebration_streak = _sc
                                            st.session_state.celebration_elo = st.session_state.vector.get(selected_topic)
                                    else:
                                        st.session_state.streak_correct = 0
                                    handle_answer_topic(is_correct, item_data)

                            # --- CHATBOT KatIA (conversacional multi-turno) ---
                            st.markdown("---")
                            _katia_avatar = _KATIA_IMG or "🐱"
                            st.markdown("#### 🐾 KatIA — Tu Tutora")
                            if _KATIA_IMG:
                                st.image(_KATIA_IMG, width=80)

                            if 'katia_chat_history' not in st.session_state:
                                st.session_state.katia_chat_history = []

                            _chat_container = st.container(height=350)
                            with _chat_container:
                                if not st.session_state.katia_chat_history:
                                    _katia_welcome = get_random_message(MENSAJES_BIENVENIDA)
                                    st.chat_message("assistant", avatar=_katia_avatar).markdown(_katia_welcome)
                                for _msg in st.session_state.katia_chat_history:
                                    if _msg["role"] == "user":
                                        st.chat_message("user").markdown(_msg["content"])
                                    else:
                                        st.chat_message("assistant", avatar=_katia_avatar).markdown(_msg["content"])

                            if st.session_state.ai_available:
                                _katia_input = st.chat_input("Escribe tu pregunta a KatIA...", key="katia_chat_input")
                            else:
                                _katia_input = None
                                st.caption("IA no disponible — configura un proveedor en la barra lateral.")

                            if _katia_input:
                                st.session_state.katia_chat_history.append({"role": "user", "content": _katia_input})
                                _soc_model = select_model_for_task(
                                    "tutor_socratic",
                                    st.session_state.get('lmstudio_models', []),
                                    st.session_state.model_cog,
                                    provider=st.session_state.get('ai_provider'),
                                )
                                _q_ctx = {
                                    'content': item_data.get('content') or '',
                                    'topic': item_data.get('topic') or '',
                                    'options': item_data.get('options') or [],
                                    'selected_option': st.session_state.get(f"answer_text_{item_data['id']}", ''),
                                    'correct_option': item_data.get('correct_option') or '',
                                }
                                try:
                                    # Recolectar respuesta sin mostrarla para validar primero
                                    with st.spinner("KatIA está pensando..."):
                                        _katia_resp = "".join(
                                            get_katia_chat_stream(
                                                messages=st.session_state.katia_chat_history,
                                                question_context=_q_ctx,
                                                base_url=st.session_state.ai_url,
                                                model_name=_soc_model,
                                                api_key=st.session_state.cloud_api_key,
                                                provider=st.session_state.get('ai_provider'),
                                            )
                                        )
                                    # Validar antes de mostrar — si revela la respuesta, sustituir
                                    if isinstance(_katia_resp, str) and not validate_socratic_response(_katia_resp):
                                        _katia_resp = "¿Qué pasos has intentado hasta ahora? ¿Qué parte del problema te genera más dudas?"
                                    with _chat_container:
                                        st.chat_message("user").markdown(_katia_input)
                                        with st.chat_message("assistant", avatar=_katia_avatar):
                                            st.markdown(_katia_resp)
                                    if isinstance(_katia_resp, str):
                                        st.session_state.katia_chat_history.append({"role": "assistant", "content": _katia_resp})
                                        # Registrar interacción con KatIA
                                        try:
                                            repo.save_katia_interaction(
                                                user_id=st.session_state.user_id,
                                                course_id=selected_course_id,
                                                item_id=item_data.get('id', ''),
                                                item_topic=item_data.get('topic', ''),
                                                student_message=_katia_input,
                                                katia_response=_katia_resp,
                                            )
                                        except Exception:
                                            pass  # No bloquear la UX si falla el registro
                                except ConnectionError:
                                    st.warning(
                                        "⚠️ No se pudo conectar con el servidor de IA. "
                                        "Verifica que esté activo o revisa tu conexión."
                                    )
                                except TimeoutError:
                                    st.warning(
                                        "⏱️ La IA tardó demasiado en responder. "
                                        "Puedes intentar de nuevo o continuar sin asistencia."
                                    )
                                except Exception as _katia_err:
                                    st.error("❌ Error inesperado al contactar la IA.")
                                    _app_logger.error(
                                        "Error en chat socrático KatIA (usuario=%s): %s",
                                        st.session_state.get("username", "desconocido"),
                                        _katia_err, exc_info=True,
                                    )
                                st.rerun()

                            if not item_data.get('options'):
                                st.warning("Pregunta sin opciones configuradas.")

            # --- Procedimiento Manuscrito (columna izquierda, debajo del ELO) ---
            if item_data:
                with col1:
                    st.markdown("---")
                    st.markdown("""
                        <div style="
                            border: 2px dashed #00CC66;
                            border-radius: 16px;
                            padding: 20px 16px;
                            text-align: center;
                            background: rgba(0, 204, 102, 0.05);
                            margin-bottom: 12px;
                        ">
                            <div style="font-size: 2.5rem; margin-bottom: 6px;">📸</div>
                            <p style="color: #fff; font-size: 1rem; font-weight: 600; margin: 0 0 4px;">
                                ¡Sube tu procedimiento y recibe retroalimentación!</p>
                            <p style="color: #aaa; font-size: 0.8rem; margin: 0;">
                                Toma una foto de tu desarrollo paso a paso. Tu profesor y la IA lo revisarán.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    uploaded_file = st.file_uploader(
                        "Foto, escaneo o PDF de tu desarrollo:",
                        type=["jpg", "jpeg", "png", "webp", "pdf"],
                        key=f"proc_upload_{item_data['id']}",
                        label_visibility="collapsed",
                    )
                    if uploaded_file is not None:
                        if True:
                            _iid = item_data['id']
                            _uid = st.session_state.user_id
                            _ext = uploaded_file.name.rsplit('.', 1)[-1].lower()

                            # T13: procesamiento diferenciado según formato
                            import hashlib
                            _raw_bytes = uploaded_file.getvalue()
                            _file_hash = hashlib.sha256(_raw_bytes).hexdigest()
                            print(f"[UPLOAD] archivo recibido: {uploaded_file.name}, size={len(_raw_bytes)} bytes, type={uploaded_file.type}")

                            if _ext == 'pdf':
                                # PDF: renderizar primera página como imagen para visión
                                try:
                                    import fitz  # PyMuPDF
                                    _pdf_doc = fitz.open(stream=_raw_bytes, filetype="pdf")
                                    _page = _pdf_doc[0]
                                    _pix = _page.get_pixmap(dpi=200)
                                    _file_bytes = _pix.tobytes("png")
                                    _mime = 'image/png'
                                    _pdf_doc.close()
                                except Exception as _pdf_err:
                                    st.error(f"No se pudo procesar el PDF: {_pdf_err}")
                                    _file_bytes = None
                            else:
                                _file_bytes = _raw_bytes
                                _mime = {'jpg':'image/jpeg','jpeg':'image/jpeg',
                                         'png':'image/png','webp':'image/webp'}.get(_ext,'image/jpeg')

                            if _file_bytes is None:
                                st.stop()  # Error procesando PDF, no continuar

                            # T7: verificar si otro estudiante ya subió el mismo archivo para esta pregunta
                            _plagiarism_detected = repo.check_file_hash_duplicate(_iid, _uid, _file_hash)
                            if _plagiarism_detected:
                                st.error(
                                    "⚠️ Este archivo ya ha sido registrado por otro usuario "
                                    "para esta pregunta."
                                )

                            st.image(_file_bytes, width='stretch')

                            # Groq activo → revisión matemática rigurosa con Llama 4 Scout
                            _is_groq = (
                                st.session_state.get('ai_provider') == 'groq'
                                and bool(st.session_state.get('cloud_api_key'))
                            )
                            # Model Router: seleccionar modelo con visión+razonamiento
                            _proc_model = select_model_for_task(
                                "image_procedure_analysis",
                                st.session_state.get('lmstudio_models', []),
                                st.session_state.model_analysis,
                                provider=st.session_state.get('ai_provider'),
                            )
                            _vision_ok = _is_groq or (_proc_model is not None)

                            # ── T5b: contador de intentos fallidos por pregunta ────
                            _fail_key = f'proc_fail_count_{_iid}'
                            if _fail_key not in st.session_state:
                                st.session_state[_fail_key] = 0
                            _fail_count = st.session_state[_fail_key]

                            # T5b: si ya alcanzó 3 fallos, mostrar opciones finales
                            if _fail_count >= 3 and not _plagiarism_detected:
                                st.error(
                                    "⚠️ Has fallado 3 veces seguidas. Se registrará una "
                                    "calificación de 0.0 por inconsistencia persistente."
                                )
                                _b1, _b2, _b3 = st.columns(3)
                                with _b1:
                                    if st.button("📤 Enviar como está", key=f"proc_send0_{_iid}"):
                                        # Registrar 0.0 y enviar al profesor
                                        print(f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes")
                                        st.session_state.db.save_procedure_submission(
                                            _uid, _iid, item_data.get('content') or '',
                                            _file_bytes, _mime,
                                            file_hash=_file_hash,
                                        )
                                        st.session_state.db.save_ai_proposed_score(
                                            _uid, _iid, 0.0,
                                            ai_feedback="Procedimiento irrelevante para la pregunta (3 intentos fallidos).",
                                        )
                                        st.session_state[f'proc_ai_saved_{_iid}'] = True
                                        st.session_state[_fail_key] = 0
                                        st.rerun()
                                with _b2:
                                    if st.button("🚫 No enviar nada", key=f"proc_cancel_{_iid}"):
                                        # Cancelar sin registrar
                                        st.session_state[_fail_key] = 0
                                        st.rerun()
                                with _b3:
                                    if st.button("📁 Subir el correcto", key=f"proc_retry_{_iid}"):
                                        # Resetear para un último intento
                                        st.session_state[_fail_key] = 0
                                        st.rerun()

                            # ── Análisis con IA ───────────────────────────────
                            elif _vision_ok:
                                _btn_label = "🔬 Analizar procedimiento" if _is_groq else "🔍 Analizar procedimiento"
                                # T7: bloquear análisis si se detectó plagio
                                if st.button(
                                    _btn_label,
                                    key=f"analyze_proc_{_iid}",
                                    width='stretch',
                                    disabled=not st.session_state.ai_available or _plagiarism_detected,
                                ):
                                    # T10: validar que el contenido de la pregunta no sea nulo/vacío
                                    _q_content = item_data.get('content') or ''
                                    if not _q_content.strip():
                                        st.error("No se pudo cargar el contenido de la pregunta. Intenta recargar.")
                                        st.stop()

                                    # ── GIF de KatIA revisando mientras la IA analiza ──
                                    _katia_review_placeholder = st.empty()
                                    _gif_start_time = time.time()
                                    _GIF_LOOP_DURATION = 13.44  # 48 frames × 280ms
                                    if _KATIA_GIF_CORRECTO_HTML:
                                        _review_html = (
                                            '<div style="text-align:center;">'
                                            f'{_KATIA_GIF_CORRECTO_HTML}'
                                            '<p style="color:#888;font-size:0.85rem;">KatIA está revisando tu procedimiento... 🔍</p>'
                                            '</div>'
                                        )
                                        _katia_review_placeholder.markdown(_review_html, unsafe_allow_html=True)
                                    _spinner_msg = (
                                        "Analizando con rigor matemático (Llama 4 Scout)..."
                                        if _is_groq else "Analizando procedimiento..."
                                    )
                                    with st.spinner(_spinner_msg):
                                        # T5a: validación de relevancia antes de calificar.
                                        # Para Groq la validación está integrada en review_math_procedure
                                        # (campo corresponde_a_pregunta). Para otros proveedores se hace
                                        # una llamada ligera previa.
                                        _is_relevant = True
                                        if not _is_groq:
                                            _is_relevant = validate_procedure_relevance(
                                                _file_bytes, _mime,
                                                _q_content,
                                                api_key=st.session_state.cloud_api_key,
                                                provider=st.session_state.get('ai_provider'),
                                                base_url=st.session_state.ai_url,
                                                model_name=_proc_model or st.session_state.model_analysis,
                                            )

                                        if not _is_relevant:
                                            # T5a+5b: procedimiento irrelevante → nota 0.0 + incrementar fallo
                                            st.session_state[_fail_key] = _fail_count + 1
                                            print(f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes")
                                            st.session_state.db.save_procedure_submission(
                                                _uid, _iid, _q_content,
                                                _file_bytes, _mime,
                                                file_hash=_file_hash,
                                            )
                                            st.session_state.db.save_ai_proposed_score(
                                                _uid, _iid, 0.0,
                                                ai_feedback="Procedimiento irrelevante para la pregunta.",
                                            )
                                            st.session_state[f'proc_ai_saved_{_iid}'] = True
                                            _new_fails = _fail_count + 1
                                            if _new_fails < 3:
                                                st.warning(
                                                    f"⚠️ El procedimiento no corresponde a la pregunta asignada "
                                                    f"(intento {_new_fails}/3). Sube el procedimiento correcto."
                                                )
                                            else:
                                                st.rerun()  # mostrará la lógica de 3 fallos arriba
                                        elif _is_groq:
                                            try:
                                                _rev = review_math_procedure(
                                                    _file_bytes, _mime,
                                                    api_key=st.session_state.cloud_api_key,
                                                    question_content=_q_content,
                                                )
                                                # Groq: la validación de relevancia viene dentro del JSON
                                                if not _rev.get('corresponde_a_pregunta', True):
                                                    st.session_state[_fail_key] = _fail_count + 1
                                                    _new_fails = _fail_count + 1
                                                    if _new_fails < 3:
                                                        st.warning(
                                                            f"⚠️ El procedimiento no corresponde a la pregunta asignada "
                                                            f"(intento {_new_fails}/3). Sube el procedimiento correcto."
                                                        )
                                                    # Guardar 0.0 en DB
                                                    if not st.session_state.get(f'proc_ai_saved_{_iid}', False):
                                                        print(f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes")
                                                        st.session_state.db.save_procedure_submission(
                                                            _uid, _iid, _q_content,
                                                            _file_bytes, _mime,
                                                            file_hash=_file_hash,
                                                        )
                                                        st.session_state.db.save_ai_proposed_score(
                                                            _uid, _iid, 0.0,
                                                            ai_feedback="Procedimiento irrelevante para la pregunta.",
                                                        )
                                                        st.session_state[f'proc_ai_saved_{_iid}'] = True
                                                    if _new_fails >= 3:
                                                        st.rerun()
                                                else:
                                                    # Procedimiento relevante: flujo normal
                                                    st.session_state[_fail_key] = 0
                                                    st.session_state[f'proc_review_{_iid}'] = _rev
                                                    if not st.session_state.get(f'proc_ai_saved_{_iid}', False):
                                                        print(f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes")
                                                        st.session_state.db.save_procedure_submission(
                                                            _uid, _iid, _q_content,
                                                            _file_bytes, _mime,
                                                            file_hash=_file_hash,
                                                        )
                                                        _ai_score = _rev.get('score_procedimiento')
                                                        _ai_eval = _rev.get('evaluacion_global') or ''
                                                        if _ai_score is not None:
                                                            st.session_state.db.save_ai_proposed_score(
                                                                _uid, _iid, float(_ai_score),
                                                                ai_feedback=_ai_eval,
                                                            )
                                                        st.session_state[f'proc_ai_saved_{_iid}'] = True
                                            except (ValueError, ConnectionError) as _exc:
                                                st.error(f"Error en la revisión matemática: {_exc}")
                                                # Guardar para revisión del profesor aunque la IA falle
                                                if not st.session_state.get(f'proc_ai_saved_{_iid}', False):
                                                    try:
                                                        repo.save_procedure_submission(
                                                            _uid, _iid, _q_content,
                                                            _file_bytes, _mime,
                                                            file_hash=_file_hash,
                                                        )
                                                        st.session_state[f'proc_ai_saved_{_iid}'] = True
                                                    except Exception:
                                                        pass
                                                st.session_state[f'proc_no_vision_{_iid}'] = True
                                        else:
                                            # Proveedor no-Groq, procedimiento relevante
                                            st.session_state[_fail_key] = 0
                                            try:
                                                result = analyze_procedure_image(
                                                    _file_bytes, _mime,
                                                    _q_content,
                                                    model_name=_proc_model or st.session_state.model_analysis,
                                                    base_url=st.session_state.ai_url,
                                                    api_key=st.session_state.cloud_api_key,
                                                    provider=st.session_state.get('ai_provider'),
                                                )
                                                if result == "VISION_NOT_SUPPORTED":
                                                    st.session_state[f'proc_no_vision_{_iid}'] = True
                                                else:
                                                    st.session_state[f'proc_fb_{_iid}'] = result
                                            except ConnectionError:
                                                st.warning("⚠️ No se pudo conectar con la IA para revisar el procedimiento.")
                                                st.session_state[f'proc_no_vision_{_iid}'] = True
                                            except TimeoutError:
                                                st.warning("⏱️ La IA tardó demasiado. El procedimiento se enviará al profesor.")
                                                st.session_state[f'proc_no_vision_{_iid}'] = True
                                            except Exception as _proc_err:
                                                _app_logger.error(
                                                    "Error en análisis de procedimiento (usuario=%s, ítem=%s): %s",
                                                    st.session_state.get("username", "desconocido"),
                                                    _iid, _proc_err, exc_info=True,
                                                )
                                                st.session_state[f'proc_no_vision_{_iid}'] = True

                                    # Esperar a que el GIF complete al menos un loop
                                    _elapsed = time.time() - _gif_start_time
                                    _remaining = _GIF_LOOP_DURATION - _elapsed
                                    if _remaining > 0:
                                        time.sleep(_remaining)
                                    # Limpiar GIF de "revisando" al terminar el análisis
                                    _katia_review_placeholder.empty()

                                if st.session_state.get(f'proc_no_vision_{_iid}'):
                                    st.info("El profesor revisará el archivo y proporcionará la retroalimentación.")

                                # ── Resultado: revisión matemática rigurosa (Groq) ──
                                _math_review = st.session_state.get(f'proc_review_{_iid}')
                                if _math_review:
                                    # ── GIF de KatIA según resultado ──
                                    _pscore_v = _math_review.get('score_procedimiento', 0)
                                    _katia_result_html = (
                                        _KATIA_GIF_CORRECTO_HTML if _pscore_v >= 91
                                        else _KATIA_GIF_ERRORES_HTML
                                    )
                                    if _katia_result_html:
                                        _result_div = (
                                            '<div style="text-align:center;">'
                                            f'{_katia_result_html}'
                                            '</div>'
                                        )
                                        st.markdown(_result_div, unsafe_allow_html=True)

                                    # ── Comentario de KatIA sobre el procedimiento ──
                                    _katia_proc_msg = get_procedure_comment(_pscore_v)
                                    _katia_proc_avatar = _KATIA_IMG or "🐱"
                                    with st.chat_message("assistant", avatar=_katia_proc_avatar):
                                        st.markdown(f"**KatIA dice:** {_katia_proc_msg}")
                                        if _pscore_v < 91:
                                            _eval_global = _math_review.get('evaluacion_global') or ''
                                            if _eval_global:
                                                st.caption(strip_thinking_tags(_eval_global))

                                    with st.container(border=True):
                                        st.markdown("##### 🔬 Revisión Matemática Rigurosa")
                                        _pscore_color = (
                                            "#FF4B4B" if _pscore_v < 40
                                            else "#FFD700" if _pscore_v < 70
                                            else "#92FE9D"
                                        )
                                        st.markdown(
                                            f"<span style='color:{_pscore_color};"
                                            f"font-size:1.4rem;font-weight:700;'>"
                                            f"Puntuación: {_pscore_v}/100</span>",
                                            unsafe_allow_html=True,
                                        )
                                        st.caption(
                                            "⏳ Nota propuesta por IA — pendiente de validación docente. "
                                            "El ELO solo se ajustará cuando el profesor confirme la calificación."
                                        )
                                        if _math_review.get('transcripcion'):
                                            with st.expander("📝 Transcripción del procedimiento"):
                                                st.markdown(strip_thinking_tags(_math_review['transcripcion']))
                                        _pasos = _math_review.get('pasos', [])
                                        if _pasos:
                                            with st.expander(f"🔢 Pasos analizados ({len(_pasos)})"):
                                                for _paso in _pasos:
                                                    _ev = _paso.get('evaluacion', '')
                                                    _paso_color = (
                                                        "#92FE9D" if _ev == "Valido"
                                                        else "#FF4B4B" if "incorrecto" in _ev.lower()
                                                        else "#FFD700"
                                                    )
                                                    st.markdown(
                                                        f"**Paso {_paso.get('numero', '?')}:** "
                                                        f"{strip_thinking_tags(_paso.get('contenido', ''))}  \n"
                                                        f"<span style='color:{_paso_color};'>"
                                                        f"▶ {strip_thinking_tags(_ev)}</span>  \n"
                                                        f"{strip_thinking_tags(_paso.get('comentario', ''))}",
                                                        unsafe_allow_html=True,
                                                    )
                                                    st.markdown("---")
                                        _errores = _math_review.get('errores_detectados', [])
                                        if _errores:
                                            with st.expander(f"⚠️ Errores detectados ({len(_errores)})"):
                                                for _err in _errores:
                                                    st.markdown(f"- {strip_thinking_tags(_err)}")
                                        _saltos = _math_review.get('saltos_logicos', [])
                                        if _saltos:
                                            with st.expander(f"🔗 Saltos lógicos ({len(_saltos)})"):
                                                for _salto in _saltos:
                                                    st.markdown(f"- {strip_thinking_tags(_salto)}")
                                        _res_ok = _math_review.get('resultado_correcto', False)
                                        st.markdown(
                                            f"**Resultado final:** "
                                            f"{'✅ Correcto' if _res_ok else '❌ Incorrecto'}"
                                        )
                                        if _math_review.get('evaluacion_global'):
                                            st.markdown(
                                                f"**Evaluación global:** {strip_thinking_tags(_math_review['evaluacion_global'])}"
                                            )

                                        # ── Pipeline de verificación simbólica (complementario) ──
                                        try:
                                            _sym_result = math_pipeline_analyze(_math_review)
                                            if _sym_result and _sym_result.analysis and _sym_result.analysis.sympy_used:
                                                _sym_invalid = _sym_result.analysis.invalid_steps
                                                if _sym_invalid > 0:
                                                    with st.expander(f"🧮 Verificación simbólica ({_sym_invalid} error(es))"):
                                                        st.markdown(_sym_result.feedback)
                                                elif _sym_result.analysis.valid_steps > 1:
                                                    with st.expander("🧮 Verificación simbólica"):
                                                        st.markdown("Todos los pasos verificados son algebraicamente correctos.")
                                        except Exception as _sym_err:
                                            _app_logger.warning(
                                                "Verificación simbólica falló: %s. "
                                                "Se omite la sección de verificación algebraica.",
                                                _sym_err,
                                            )

                                # ── Resultado: revisión genérica (otros proveedores) ──
                                _ai_fb = st.session_state.get(f'proc_fb_{_iid}')
                                if _ai_fb:
                                    with st.container(border=True):
                                        st.markdown("##### 🔍 Retroalimentación del procedimiento")
                                        st.markdown(strip_thinking_tags(_ai_fb))

                            # T6b: si el modelo no soporta visión, indicar al usuario que
                            # el procedimiento se enviará directamente al profesor.
                            if not _vision_ok and _fail_count < 3:
                                st.info(
                                    "📤 Tu modelo actual no soporta visión. El procedimiento "
                                    "será enviado al profesor para revisión manual."
                                )

                            # ── Sección de envío al docente: SIEMPRE visible ──────────
                            st.markdown("---")
                            _sub = st.session_state.db.get_student_submission(_uid, _iid)
                            _sub_status = _sub['status'] if _sub else None

                            if _sub_status == 'PENDING_TEACHER_VALIDATION':
                                # IA ya analizó; esperando validación del docente
                                _ai_prop = _sub.get('ai_proposed_score')
                                if _ai_prop is not None:
                                    st.info(
                                        f"⏳ **Nota propuesta por IA: {_ai_prop:.1f}/100** — "
                                        "Tu profesor revisará y confirmará (o ajustará) la calificación."
                                    )
                                else:
                                    st.info("⏳ Procedimiento enviado al profesor para validación.")

                            elif _sub_status == 'VALIDATED_BY_TEACHER':
                                # Docente validó → mostrar nota oficial
                                with st.container(border=True):
                                    st.markdown("##### ✅ Calificación validada por el Profesor")
                                    _final = _sub.get('final_score')
                                    _teacher_sc = _sub.get('teacher_score')
                                    if _final is not None:
                                        st.metric("📊 Nota final (oficial)", f"{_final:.1f} / 100")
                                    elif _teacher_sc is not None:
                                        st.metric("📊 Nota del profesor", f"{_teacher_sc:.1f} / 100")
                                    if _sub.get('teacher_feedback'):
                                        st.markdown(_sub['teacher_feedback'])
                                    _fb_path = _sub.get('feedback_image_path')
                                    if _fb_path and os.path.exists(_fb_path):
                                        st.image(_fb_path, caption="Procedimiento calificado", width='stretch')
                                    elif _sub.get('feedback_image'):
                                        st.image(bytes(_sub['feedback_image']), caption="Procedimiento calificado", width='stretch')

                            elif _sub_status in ('pending', 'reviewed'):
                                # Flujo legado: enviado manualmente o revisado sin IA
                                if _sub_status == 'pending':
                                    st.info("⏳ Procedimiento enviado. Tu profesor lo revisará pronto.")
                                else:
                                    with st.container(border=True):
                                        st.markdown("##### ✅ Retroalimentación del Profesor")
                                        if _sub.get('procedure_score') is not None:
                                            st.metric("📊 Nota del procedimiento", f"{_sub['procedure_score']:.1f} / 5.0")
                                        if _sub.get('teacher_feedback'):
                                            st.markdown(_sub['teacher_feedback'])
                                        _fb_path = _sub.get('feedback_image_path')
                                        if _fb_path and os.path.exists(_fb_path):
                                            st.image(_fb_path, caption="Procedimiento calificado", width='stretch')
                                        elif _sub.get('feedback_image'):
                                            st.image(bytes(_sub['feedback_image']), caption="Procedimiento calificado", width='stretch')

                            else:
                                # Sin envío previo: mostrar botón para enviar al docente
                                _show_send_btn = (
                                    not _vision_ok
                                    or st.session_state.get(f'proc_no_vision_{_iid}', False)
                                    or not st.session_state.get(f'proc_ai_saved_{_iid}', False)
                                )
                                if _show_send_btn and not _plagiarism_detected:
                                    st.info("El profesor revisará el archivo y proporcionará retroalimentación.")
                                    if st.button(
                                        "📤 Enviar al profesor para revisión",
                                        key=f"send_teacher_{_iid}",
                                        width='stretch',
                                    ):
                                        # T7: guardar hash junto con la entrega
                                        print(f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes")
                                        st.session_state.db.save_procedure_submission(
                                            _uid, _iid, item_data.get('content') or '',
                                            _file_bytes, _mime,
                                            file_hash=_file_hash,
                                        )
                                        st.rerun()

        elif mode == "📊 Estadísticas":
            st.title("📊 Estadísticas de Aprendizaje")
            # T8c: racha de estudio en la cabecera de estadísticas
            _stat_streak = cached('cache_streak',
                                  lambda: repo.get_study_streak(st.session_state.user_id))
            if _stat_streak == 0:
                _streak_msg = "💤 Sin racha activa — ¡empieza hoy!"
                _streak_color = "#aaa"
            elif _stat_streak <= 2:
                _streak_msg = f"🔥 Racha: {_stat_streak} día{'s' if _stat_streak != 1 else ''} — ¡Buen inicio!"
                _streak_color = "#FF9800"
            elif _stat_streak <= 6:
                _streak_msg = f"🔥🔥 Racha: {_stat_streak} días — ¡Vas en racha!"
                _streak_color = "#FF5722"
            else:
                _streak_msg = f"🔥🔥🔥 Racha: {_stat_streak} días — ¡IMPARABLE!"
                _streak_color = "#FF4500"
            st.markdown(f"<p style='font-size:1.1rem; font-weight:700; color:{_streak_color};'>{_streak_msg}</p>",
                        unsafe_allow_html=True)

            history_full = st.session_state.db.get_user_history_full(st.session_state.user_id)
            attempts_data = st.session_state.db.get_attempts_for_ai(st.session_state.user_id, limit=1000)
            # Cargar scores de procedimientos una sola vez para toda la sección
            _proc_scores = st.session_state.db.get_student_procedure_scores(st.session_state.user_id)

            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Ejercicios Resueltos", len(history_full), delta=f"+{len(attempts_data)} recientes")
            with m2:
                if attempts_data:
                    accuracy = sum(1 for a in attempts_data if a['is_correct']) / len(attempts_data)
                    st.metric("Precisión Promedio", f"{accuracy:.1%}")
                else:
                    st.metric("Precisión Promedio", "0%")
            with m3:
                global_elo = aggregate_global_elo(st.session_state.vector)
                rank_n, rank_c = get_rank(global_elo)
                st.metric("Nivel Global", f"{global_elo:.0f}", delta=rank_n)
            with m4:
                # Tiempo promedio por pregunta
                _st_times = [a.get('time_taken') for a in history_full if a.get('time_taken') and a['time_taken'] > 0]
                _st_avg_t = sum(_st_times) / len(_st_times) if _st_times else 0
                st.metric("⏱️ Tiempo Prom.", f"{_st_avg_t:.0f}s" if _st_avg_t else "—")
            with m5:
                if _proc_scores:
                    avg_proc = sum(s['score'] for s in _proc_scores) / len(_proc_scores)
                    st.metric("📝 Procedimientos", f"{avg_proc:.1f}/100",
                              delta=f"{len(_proc_scores)} evaluado(s)")
                else:
                    st.metric("📝 Procedimientos", "Sin datos")

            if not _proc_scores:
                st.info(
                    "No has subido procedimientos manuales. Te recomendamos subir fotos de tu "
                    "desarrollo paso a paso para que el profesor pueda evaluarte y la IA pueda "
                    "darte mejores recomendaciones."
                )
            else:
                # Desglose de calidad por curso
                _proc_by_course = st.session_state.db.get_procedure_stats_by_course(st.session_state.user_id)
                if _proc_by_course:
                    st.markdown("**📝 Calidad de procedimientos por curso:**")
                    for _cid, _cdata in _proc_by_course.items():
                        _avg = _cdata['avg_score']
                        if _avg < 60:
                            _icon, _lbl = "🔴", "Deficiente"
                        elif _avg <= 80:
                            _icon, _lbl = "🟡", "Regular"
                        else:
                            _icon, _lbl = "🟢", "Excelente"
                        st.markdown(
                            f"- **{_cdata['course_name']}**: {_icon} {_lbl} — "
                            f"{_avg:.1f}/100 ({_cdata['count']} envío(s))"
                        )

            st.markdown("---")

            st.subheader("🏆 Dominio por Materia")
            current_elos = cached('cache_elo_by_topic',
                                  lambda: st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id))

            if current_elos:
                try:
                    # Extraer nombres de tópicos y sus valores (elo, rd)
                    topics_list = list(current_elos.keys())
                    elos_list = [val[0] for val in current_elos.values()]
                    rds_list = [val[1] for val in current_elos.values()]
                    
                    # Crear DataFrame para ordenar
                    df_elo = pd.DataFrame({
                        'Tema': topics_list, 
                        'ELO': elos_list,
                        'RD': rds_list
                    }).sort_values('ELO', ascending=False)

                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=df_elo['Tema'], y=df_elo['ELO'],
                        marker_color='#00C9FF', opacity=0.8,
                        error_y=dict(type='data', array=df_elo['RD'].tolist(),
                                     color='#FFC107', thickness=1.5, width=5)
                    ))
                    fig_bar.update_layout(
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Materia", yaxis_title="ELO",
                        yaxis=dict(range=[max(0, min(elos_list) - 50), None])
                    )
                    st.plotly_chart(fig_bar, width='stretch')
                except Exception as e:
                    st.error(f"Error visualizando gráfica: {str(e)}")
            else:
                st.info("Completa ejercicios para visualizar tu perfil de fortalezas.")

            st.subheader("📈 Progreso Académico")
            if history_full:
                df_hist = pd.DataFrame(history_full)
                df_hist['intento'] = range(1, len(df_hist) + 1)
                fig = go.Figure()
                for topic in df_hist['topic'].unique():
                    topic_data = df_hist[df_hist['topic'] == topic]
                    fig.add_trace(go.Scatter(
                        x=topic_data['intento'], y=topic_data['elo'],
                        mode='lines+markers', name=topic, line=dict(width=2)
                    ))
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Secuencia de Ejercicios", yaxis_title="Nivel ELO",
                    legend=dict(bgcolor='rgba(38,39,48,0.8)', bordercolor='gray')
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.write("Sin datos históricos.")

            st.markdown("---")
            st.subheader("🧠 Asistente Virtual Inteligente")
            st.write("Genera un diagnóstico personalizado con tus fortalezas, áreas a mejorar y puntos críticos.")

            _REC_META = [
                ("💪", "Fortalezas",    "Qué estás haciendo bien — sigue así"),
                ("⚡", "Por mejorar",   "Áreas aceptables con potencial de crecimiento"),
                ("🎯", "Áreas críticas","Debilidades que necesitan atención urgente"),
            ]

            _rec_help = None if st.session_state.ai_available else "IA no disponible en este entorno demo"
            if st.button("✨ Generar Recomendaciones de Estudio", disabled=not st.session_state.ai_available, help=_rec_help):
                try:
                    with st.spinner("Analizando patrones de aprendizaje..."):
                        recent_attempts = st.session_state.db.get_attempts_for_ai(st.session_state.user_id)
                        current_elo_val = aggregate_global_elo(st.session_state.vector)
                        _proc_stats = {
                            'count': len(_proc_scores),
                            'avg_score': (sum(s['score'] for s in _proc_scores) / len(_proc_scores)) if _proc_scores else None,
                            'scores': [s['score'] for s in _proc_scores],
                        }
                        _proc_by_course_student = st.session_state.db.get_procedure_stats_by_course(st.session_state.user_id)
                        recs = analyze_performance_local(
                            recent_attempts,
                            current_elo_val,
                            base_url=st.session_state.ai_url,
                            model_name=st.session_state.model_analysis,
                            api_key=st.session_state.cloud_api_key,
                            provider=st.session_state.get('ai_provider'),
                            procedure_stats=_proc_stats,
                            procedure_stats_by_course=_proc_by_course_student,
                        )
                    # Detectar error de autenticación antes de guardar
                    # T9c: detectar errores estandarizados de la capa IA
                    if isinstance(recs, str) and (recs.startswith("ERROR_401:") or recs.startswith("ERROR_429:")):
                        st.error(recs.split(": ", 1)[1])
                    else:
                        # Guardar en session_state y renderizar FUERA del spinner
                        st.session_state['study_recs'] = recs if isinstance(recs, list) else []
                except (ConnectionError, TimeoutError):
                    st.info("IA no disponible en este momento. Inténtalo más tarde.")
                except Exception as e:
                    st.error(f"Error crítico: {str(e)}")

            # Renderizado persistente (sobrevive reruns)
            if st.session_state.get('study_recs') is not None:
                recs = st.session_state['study_recs']
                if len(recs) == 0:
                    st.warning("No hay suficientes datos para generar recomendaciones aún.")
                else:
                    _CALLOUT = [st.success, st.info, st.warning]
                    for idx, (icon, label, subtitle) in enumerate(_REC_META):
                        rec = recs[idx] if idx < len(recs) else {}
                        with st.container(border=True):
                            st.markdown(f"### {icon} Recomendación #{idx + 1}: {label}")
                            st.caption(subtitle)
                            st.markdown(f"**🔍 Diagnóstico:** {strip_thinking_tags(rec.get('diagnostico', 'N/A'))}")
                            _CALLOUT[idx](f"**📝 Acción:** {strip_thinking_tags(rec.get('accion', 'N/A'))}")
                            st.markdown(f"**💡 Justificación:** {strip_thinking_tags(rec.get('justificacion', 'N/A'))}")
                            ejercicios = rec.get('ejercicios', 0)
                            if ejercicios:
                                st.markdown(f"**🔢 Meta sugerida:** {ejercicios} ejercicios")

        elif mode == "🎓 Mis Cursos":
            st.title("🎓 Mis Cursos")

            _level = st.session_state.education_level or 'universidad'
            _level_labels = {'universidad': "🎓 Universidad", 'colegio': "🏫 Colegio",
                             'concursos': "🏆 Concursos", 'semillero': "🏅 Semillero de Matemáticas"}
            _level_label = _level_labels.get(_level, "🎓 Universidad")
            st.markdown(f"**Nivel académico:** {_level_label}")
            st.caption("Tu nivel se fijó al registrarte y determina qué cursos puedes ver.")

            _enrolled_ids = {c['id'] for c in _enrolled}

            # Noticia si el usuario llegó desde "Tengo un código" en la bienvenida
            _came_from_code_btn = st.session_state.pop('welcome_open_code_tab', False)
            if _came_from_code_btn:
                st.info("👇 Haz clic en la pestaña **🔑 Código de invitación** para ingresar el código de tu profesor.")

            _tab_explore, _tab_enrolled, _tab_code = st.tabs([
                "🔍 Explorar profesores",
                f"📋 Mis matrículas ({len(_enrolled)})",
                "🔑 Código de invitación",
            ])

            # ── Tab 1: Explorar por profesor ──────────────────────────────────
            with _tab_explore:
                _sem_grade_exp = st.session_state.get('student_grade') if _level == 'semillero' else None
                _teachers_data = cached('cache_teachers_groups',
                    lambda: repo.get_teachers_with_groups_and_courses(_level, grade=_sem_grade_exp))

                if not _teachers_data:
                    st.info("No hay profesores con grupos disponibles para tu nivel aún. "
                            "Si tu profesor ya creó un grupo, pídele el código de invitación (Tab 🔑).")
                else:
                    st.caption("Elige el profesor de tu preferencia para cada materia y haz clic en **Matricular**.")
                    for _tch in _teachers_data:
                        st.markdown(f"### 👤 Prof. {_tch['teacher_name']}")
                        for _grp in _tch['groups']:
                            with st.container(border=True):
                                _tc1, _tc2 = st.columns([5, 1])
                                with _tc1:
                                    st.markdown(f"**{_grp['course_name']}**")
                                    st.caption(f"Grupo: {_grp['group_name']} · {_grp['student_count']} estudiante(s) matriculado(s)")
                                with _tc2:
                                    if _grp['course_id'] in _enrolled_ids:
                                        st.markdown("✅ Matriculado")
                                    else:
                                        if st.button("Matricular", key=f"enroll_tch_{_grp['group_id']}", type="primary"):
                                            repo.enroll_user(st.session_state.user_id, _grp['course_id'], _grp['group_id'])
                                            invalidate_cache('cache_enrollments', 'cache_teachers_groups')
                                            st.session_state.welcome_dismissed = True
                                            st.rerun()

            # ── Tab 2: Mis matrículas ──────────────────────────────────────────
            with _tab_enrolled:
                if not _enrolled:
                    st.info("Aún no estás matriculado en ningún curso. Ve a **Explorar profesores** para comenzar.")
                else:
                    st.caption("Puedes desmatricularte y volver a matricularte con otro profesor cuando quieras.")
                    for _ec in _enrolled:
                        with st.container(border=True):
                            _ec1, _ec2 = st.columns([5, 1])
                            with _ec1:
                                st.markdown(f"**{_ec['name']}**")
                                _grp_label = _ec.get('group_name', '')
                                _is_cross = _ec.get('block') != _student_block
                                _cap = f"Grupo: {_grp_label}" if _grp_label else f"Bloque: {_ec['block']}"
                                if _is_cross:
                                    _cap += " · 📌 Acceso especial"
                                st.caption(_cap)
                            with _ec2:
                                if st.button("Desmatricular", key=f"unenroll_tab_{_ec['id']}"):
                                    repo.unenroll_user(st.session_state.user_id, _ec['id'])
                                    invalidate_cache('cache_enrollments', 'cache_teachers_groups')
                                    st.session_state.pop('current_question', None)
                                    st.session_state.pop('selected_course', None)
                                    st.rerun()

            # ── Tab 3: Código de invitación ────────────────────────────────────
            with _tab_code:
                st.markdown("Si tu profesor te compartió un código, ingrésalo aquí para unirte directamente a su grupo.")
                _code_raw = st.text_input(
                    "Código de invitación",
                    placeholder="Ej: ALG3B7",
                    max_chars=6,
                    key="invite_code_input",
                )
                _code_upper = (_code_raw or "").upper().strip()
                if st.button("🔍 Buscar grupo", key="btn_lookup_code"):
                    if len(_code_upper) >= 4:
                        _found = repo.get_group_by_invite_code(_code_upper)
                        if _found:
                            st.session_state['code_group_found'] = _found
                        else:
                            st.session_state.pop('code_group_found', None)
                            st.error("Código no encontrado. Verifica que esté escrito correctamente.")
                    else:
                        st.warning("El código debe tener al menos 4 caracteres.")

                _cg = st.session_state.get('code_group_found')
                if _cg:
                    if _cg['course_id'] in _enrolled_ids:
                        st.warning(f"Ya estás matriculado en **{_cg['course_name']}**. Si quieres cambiar de profesor, desmatricúlate primero desde la pestaña 📋.")
                    else:
                        st.success(
                            f"✅ Grupo encontrado\n\n"
                            f"**Curso:** {_cg['course_name']}  \n"
                            f"**Grupo:** {_cg['group_name']}  \n"
                            f"**Profesor:** {_cg['teacher_name']}"
                        )
                        if _cg.get('block') and _cg['block'] != _student_block:
                            st.info("📌 Este curso es de un nivel diferente al tuyo. Tu profesor te ha dado acceso especial — podrás practicarlo junto a tus cursos normales.")
                        if st.button("Confirmar matrícula", key="btn_confirm_code_enroll", type="primary"):
                            repo.enroll_user(st.session_state.user_id, _cg['course_id'], _cg['group_id'])
                            invalidate_cache('cache_enrollments', 'cache_teachers_groups')
                            st.session_state.pop('code_group_found', None)
                            st.session_state.welcome_dismissed = True
                            st.rerun()

        # ── MODO: Centro de Feedback (solo lectura) ───────────────────────────
        elif mode.startswith("💬 Feedback"):
            # T4b: al entrar al centro de feedback, marcar todas las revisadas como vistas
            st.session_state.fb_seen_ids |= _reviewed_ids

            st.title("💬 Centro de Feedback")
            st.caption("Historial de tus entregas de procedimiento y retroalimentación recibida. Solo lectura.")

            # Consulta todas las entregas del estudiante ordenadas por fecha DESC
            _fb_rows = repo.get_student_feedback_history(st.session_state.user_id)

            if not _fb_rows:
                st.info("Aún no tienes entregas de procedimiento. Envía tu primer procedimiento desde el modo Practicar.")
            else:
                for _fb in _fb_rows:
                    # Encabezado: pregunta resumida + fecha
                    _item_label = _fb.get('item_short') or _fb.get('item_id', '—')
                    _date_label = str(_fb.get('submitted_at') or '—')[:16]
                    _status = _fb.get('status', 'pending')

                    # Indicador visual del estado de revisión
                    _status_map = {
                        'pending': "🟡 Pendiente",
                        'PENDING_TEACHER_VALIDATION': "🟠 Esperando validación docente",
                        'VALIDATED_BY_TEACHER': "🟢 Validado por docente",
                        'reviewed': "🟢 Revisado",
                    }
                    _status_label = _status_map.get(_status, f"⚪ {_status}")

                    with st.expander(f"📄 {_item_label}… — {_date_label} — {_status_label}"):
                        # Nota IA: ai_proposed_score (0-100). Si no existe, sin dato.
                        _ai_score = _fb.get('ai_proposed_score')

                        # Nota docente: flujo formal (final_score/teacher_score, 0-100)
                        # o flujo legacy (procedure_score, 0-5 escalado a 0-100).
                        _final = _fb.get('final_score')
                        if _final is None:
                            _final = _fb.get('teacher_score')
                        if _final is None:
                            _legacy = _fb.get('procedure_score')
                            if _legacy is not None:
                                _final = _legacy * 20.0

                        # Mostrar notas siempre visibles con métricas grandes
                        _m1, _m2, _m3 = st.columns(3)
                        _m1.metric(
                            "🤖 Nota IA",
                            f"{_ai_score:.1f}" if _ai_score is not None else "—",
                        )
                        _m2.metric(
                            "👨‍🏫 Nota Docente",
                            f"{_final:.1f}" if _final is not None else "—",
                        )
                        _m3.metric("📅 Enviado", _date_label)

                        # Justificación IA (ai_feedback)
                        _ai_fb = _fb.get('ai_feedback')
                        if _ai_fb:
                            st.markdown("**Retroalimentación IA:**")
                            st.info(_ai_fb)

                        # Comentario manual del docente (teacher_feedback)
                        _tch_fb = _fb.get('teacher_feedback')
                        if _tch_fb:
                            st.markdown("**Comentario del docente:**")
                            st.success(_tch_fb)

                        # Si no hay ningún comentario todavía
                        if not _ai_fb and not _tch_fb:
                            st.caption("Sin comentarios aún.")

                        # Enlace para ver el archivo enviado
                        _stor_url = _fb.get('storage_url')
                        _img_path = _fb.get('procedure_image_path')
                        _fb_img_shown = False
                        if _stor_url:
                            _fb_img_bytes = repo.resolve_storage_image(_stor_url)
                            if _fb_img_bytes:
                                st.markdown("**Archivo enviado:**")
                                st.image(_fb_img_bytes, caption="Procedimiento enviado", width='stretch')
                                _fb_img_shown = True
                        if not _fb_img_shown and _img_path and os.path.isfile(_img_path):
                            st.markdown("**Archivo enviado:**")
                            st.image(_img_path, caption="Procedimiento enviado", width='stretch')

                        # Enlace para ver corrección del docente (feedback_image_path)
                        _fb_img_path = _fb.get('feedback_image_path')
                        if _fb_img_path and os.path.isfile(_fb_img_path):
                            st.markdown("**Corrección del docente:**")
                            st.image(_fb_img_path, caption="Archivo corregido", width='stretch')
