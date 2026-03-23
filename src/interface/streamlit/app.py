import streamlit as st
import os
import sys

print("[APP VERSION] 2026-03-23-v2")

# Parche para resolver imports desde la raíz del proyecto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if base_path not in sys.path:
    sys.path.append(base_path)

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import requests
import json
import random
import importlib
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
importlib.reload(db_mod)
importlib.reload(pg_mod)
importlib.reload(ai_mod)
importlib.reload(_math_review_mod)
importlib.reload(_router_mod)
importlib.reload(_pipeline_mod)

from src.domain.elo.vector_elo import VectorRating, aggregate_global_elo, aggregate_global_rd
from src.domain.elo.model import expected_score, calculate_dynamic_k, Item
from src.utils import strip_thinking_tags
SQLiteRepository = db_mod.SQLiteRepository
PostgresRepository = pg_mod.PostgresRepository
analyze_performance_local = ai_mod.analyze_performance_local
get_active_models = ai_mod.get_active_models
get_socratic_guidance_stream = ai_mod.get_socratic_guidance_stream
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

# Configuración de página
st.set_page_config(page_title="LevelUp ELO — Evaluación Adaptativa", layout="wide", page_icon="🎓")

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
# Inicializar Servicios (Re-instanciar en cada recarga para capturar cambios en código)
import src.application.services.student_service as ss_mod
import src.application.services.teacher_service as ts_mod
importlib.reload(ss_mod)
importlib.reload(ts_mod)

st.session_state.student_service = ss_mod.StudentService(st.session_state.db)
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
        else:
            cookie_manager.delete("elo_auth_token")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA DE LOGIN / REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    _logo_col1, _logo_col2, _logo_col3 = st.columns([1, 2, 1])
    with _logo_col2:
        st.image(_get_logo(), width='stretch')
    st.markdown("<p style='text-align: center; color: #aaa; font-size: 1.2rem; margin-bottom: 40px;'>Plataforma de evaluación y aprendizaje adaptativo basada en el sistema ELO</p>", unsafe_allow_html=True)

    col_info, col_login = st.columns([1.4, 1])

    with col_info:
        st.markdown("""
        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>📌 ¿Qué es LevelUp ELO?</h3>
            <p>LevelUp ELO es una plataforma académica de evaluación adaptativa que utiliza el <b>sistema de calificación ELO</b> —originalmente diseñado para el ajedrez— para medir con precisión el nivel de dominio de cada estudiante en distintas materias.</p>
            <p style="margin-top:10px;">A diferencia de los exámenes tradicionales, el sistema se adapta continuamente: <b>la dificultad de cada ejercicio se ajusta en tiempo real</b> según el rendimiento del estudiante, maximizando el aprendizaje efectivo.</p>
        </div>

        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>⚙️ ¿Cómo funciona?</h3>
            <ul style="margin-top: 10px; line-height: 2;">
                <li><b>Puntuación ELO por materia:</b> Cada estudiante tiene un índice numérico por área temática que sube o baja según sus respuestas correctas e incorrectas.</li>
                <li><b>Selección adaptativa de ejercicios:</b> El sistema elige automáticamente preguntas que se encuentran en la <em>zona de desarrollo óptimo</em> del estudiante, ni demasiado fáciles ni inalcanzables.</li>
                <li><b>Seguimiento del progreso:</b> Los profesores pueden consultar la evolución de cada estudiante por tema, junto con métricas de probabilidad de acierto por ejercicio.</li>
                <li><b>Recomendaciones con IA:</b> Un asistente inteligente analiza el historial del estudiante y genera recomendaciones de estudio personalizadas.</li>
            </ul>
        </div>

        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>👥 Roles en la plataforma</h3>
            <ul style="margin-top: 10px; line-height: 2;">
                <li><b>🎓 Estudiante:</b> Accede a ejercicios adaptativos y consulta sus estadísticas de progreso.</li>
                <li><b>🏫 Profesor:</b> Visualiza el rendimiento de todos los estudiantes y sus métricas detalladas por tema. Requiere aprobación del administrador.</li>
                <li><b>🛡️ Administrador:</b> Gestiona las cuentas de profesores y estudiantes en la plataforma.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_login:
        with st.container(border=True):
            st.markdown("### 🔐 Acceso a la Plataforma")
            tab1, tab2 = st.tabs(["INICIAR SESIÓN", "REGISTRARSE"])

            with tab1:
                username = st.text_input("Usuario", key="login_user")
                password = st.text_input("Contraseña", type="password", key="login_pass")
                st.write("")
                if st.button("Iniciar Sesión", type="primary"):
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
                new_user = st.text_input("Nombre de usuario", key="reg_user")
                new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
                new_role = st.selectbox("Tipo de cuenta", ["Estudiante", "Profesor"], key="reg_role")

                education_level = None
                if new_role == "Estudiante":
                    level_label = st.selectbox(
                        "Nivel Educativo *",
                        ["Universidad", "Colegio", "Concursos"],
                        key="reg_level",
                        help="Determina qué catálogo de cursos podrás ver."
                    )
                    education_level = level_label.lower()

                st.write("")
                if st.button("Crear Cuenta"):
                    role_map = {"Estudiante": "student", "Profesor": "teacher"}
                    chosen_role = role_map[new_role]

                    # Validaciones de contraseña en UI
                    _pass_stripped = (new_pass or "").strip()
                    if not _pass_stripped:
                        st.error("La contraseña es obligatoria.")
                    elif len(_pass_stripped) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres.")
                    elif chosen_role == 'student' and not education_level:
                        st.error("Debes seleccionar tu nivel educativo.")
                    else:
                        success, message = st.session_state.db.register_user(
                            new_user, new_pass, chosen_role,
                            education_level=education_level
                        )
                        if success:
                            if chosen_role == 'teacher':
                                st.info(f"✅ {message} Espera la aprobación del administrador.")
                            else:
                                st.success(f"✅ {message} Ya puede iniciar sesión.")
                        else:
                            st.error(message)

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

            if st.button("Cerrar Sesión"):
                logout()

        st.title("🏫 Panel del Profesor")

        # ── Notificación de procedimientos pendientes ──────────────────────────
        _pending_count = st.session_state.db.get_pending_submissions_count(st.session_state.user_id)
        if _pending_count > 0:
            st.warning(
                f"📋 **{_pending_count} procedimiento(s) de estudiantes esperando revisión.** "
                "Revísalos en la sección de abajo."
            )

        # ── Revisión de Procedimientos ─────────────────────────────────────────
        _exp_label = (
            f"📋 Procedimientos para Revisar  🔴 {_pending_count} pendiente(s)"
            if _pending_count > 0 else "📋 Procedimientos para Revisar"
        )
        with st.expander(_exp_label, expanded=_pending_count > 0):
            _pending_subs = st.session_state.db.get_pending_submissions_for_teacher(
                st.session_state.user_id
            )
            if not _pending_subs:
                st.info("No hay procedimientos pendientes de revisión.")
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
                _tbl_groups = [
                    {
                        "Grupo": g['name'],
                        "Curso": g['course_name'],
                        "Creado": str(g['created_at'])[:10],
                    }
                    for g in _my_groups
                ]
                st.dataframe(pd.DataFrame(_tbl_groups), width='stretch', hide_index=True)
            else:
                st.info("No tienes grupos creados aún.")

        st.markdown("---")

        # ── Dashboard principal ────────────────────────────────────────────────
        students, groups = st.session_state.teacher_service.get_dashboard_data(st.session_state.user_id)

        if not students:
            st.info("Aún no tienes estudiantes vinculados a tus grupos.")
        else:
            # ── Fila de filtros: Grupo + Nivel + Materia ─────────────────────
            _f_col1, _f_col2, _f_col3 = st.columns([1, 1, 1])
            with _f_col1:
                _grp_opts = {"Todos mis grupos": None}
                _grp_opts.update({g['name']: g['id'] for g in groups})
                selected_group_name = st.selectbox(
                    "🎯 Filtrar por Grupo", list(_grp_opts.keys()),
                    key="tch_group_filter",
                )
                selected_group_id = _grp_opts[selected_group_name]
                if selected_group_id:
                    students = [s for s in students if s['group_id'] == selected_group_id]

            with _f_col2:
                # Nivel educativo: filtra por el bloque del curso vinculado al grupo
                _level_opts = ["Todos", "Colegio", "Universidad", "Concursos"]
                _sel_level = st.selectbox(
                    "🎓 Filtrar por Nivel", _level_opts,
                    key="tch_level_filter",
                )
                if _sel_level != "Todos":
                    students = [s for s in students if s.get('course_block') == _sel_level]

            with _f_col3:
                # Materia: lista dinámica construida a partir de los cursos reales
                # de los estudiantes ya filtrados por grupo y nivel.
                # Se usa "Todas" como opción por defecto para evitar conflictos
                # de Streamlit cuando las opciones cambian entre reruns.
                _all_subjects = sorted(set(
                    s.get('course_name', '—') for s in students if s.get('course_name', '—') != '—'
                ))
                _subj_opts = ["Todas"] + _all_subjects
                _sel_subject = st.selectbox(
                    "📚 Filtrar por Materia", _subj_opts,
                    key="tch_subject_filter",
                )
                if _sel_subject != "Todas":
                    students = [s for s in students if s.get('course_name') == _sel_subject]

            # ── Verificación de filtros vacíos ────────────────────────────────
            if not students:
                st.info("No hay estudiantes en esta combinación de filtros.")

            # Deduplicar estudiantes por id tras aplicar filtros (un estudiante
            # puede aparecer en varias filas si está matriculado en múltiples
            # grupos del profesor; los filtros ya redujeron al contexto correcto).
            _seen_ids = set()
            _unique_students = []
            for _st in students:
                if _st['id'] not in _seen_ids:
                    _seen_ids.add(_st['id'])
                    _unique_students.append(_st)
            students = _unique_students

            # ── Selector de estudiante (sobre el subconjunto filtrado) ────────
            _stu_opts = ["— Selecciona un estudiante —"] + [s['username'] for s in students]
            _sel_name = st.selectbox(
                "👤 Ver detalle de estudiante", _stu_opts,
                key="tch_student_selector",
            )

            # ── Tabla resumen ELO (siempre visible) ───────────────────────────
            st.subheader(f"📈 Rendimiento ELO — {selected_group_name}")
            _BASE_COLS = {"Estudiante", "Grupo", "ELO Global", "Rango"}
            _sum_rows = []
            for _s in students:
                _elo_map = cached(f'cache_elo_topic_{_s["id"]}',
                                  lambda _sid=_s['id']: st.session_state.db.get_latest_elo_by_topic(_sid))

                # Filtrado estricto: solo tópicos de cursos inscritos o procedimientos.
                # Si el conjunto de tópicos inscritos está vacío (estudiante antiguo sin
                # matrículas o sin ítems con course_id), usamos el elo_map completo como
                # fallback para no ocultar actividad real.
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
                    "Grupo": _s.get('group_name', selected_group_name),
                    "ELO Global": round(_gelo, 1),
                    "Rango": _rname,
                }
                _row.update({t: round(v[0], 1) for t, v in _active_map.items()})
                _sum_rows.append(_row)

            # Construir DataFrame (tolerante a lista vacía)
            _df_sum = (
                pd.DataFrame(_sum_rows)
                if _sum_rows
                else pd.DataFrame(columns=["Estudiante", "Grupo", "ELO Global", "Rango"])
            )

            # Convertir columnas de tópico a numérico — NO rellenar NaN.
            # Celda vacía = estudiante sin actividad en ese tópico (honesto).
            for _c in _df_sum.columns:
                if _c not in _BASE_COLS:
                    _df_sum[_c] = pd.to_numeric(_df_sum[_c], errors='coerce')

            # Eliminar columnas de tópico donde NINGÚN estudiante tiene datos reales.
            # Esto descarta ruido de cursos no matriculados que colaron vía actividad
            # de otros alumnos en el mismo DataFrame.
            _topic_cols = [c for c in _df_sum.columns if c not in _BASE_COLS]
            _active_topic_cols = [c for c in _topic_cols if _df_sum[c].notna().any()]

            # Reordenar: columnas base primero, luego tópicos activos
            _ordered = [c for c in ["Estudiante", "Grupo", "ELO Global", "Rango"]
                        if c in _df_sum.columns] + _active_topic_cols
            _df_sum = _df_sum[_ordered]

            st.dataframe(_df_sum, width='stretch')

            st.markdown("---")

            # ── Panel de detalle (solo cuando hay estudiante seleccionado) ────
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

                # ── Cabecera del estudiante ────────────────────────────────────
                st.subheader(f"🔍 Detalle: **{_sel_name}**")
                _mc1, _mc2, _mc3 = st.columns(3)
                _mc1.metric("🏆 ELO Global", f"{_global_elo:.1f}", delta=_rank_n)
                _mc2.metric("📊 Intentos Totales", _elo_sum['attempts_count'])
                _mc3.metric("🎯 Precisión Reciente", f"{_elo_sum['recent_accuracy']:.1%}")

                st.markdown("---")

                # ── Bloque 1: ELO por Tópico + Procedimientos (simultáneos) ──
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

                # ── Bloque 2: Gráfico evolución ELO por tema (ancho completo) ─
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

                    # ── Secciones expandibles ──────────────────────────────────
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
                        st.dataframe(
                            _df_att[['intento', 'topic', 'difficulty', 'resultado', 'elo_after', 'prob_failure', 'timestamp']]
                            .rename(columns={
                                'intento': '#', 'topic': 'Tema', 'difficulty': 'Dificultad',
                                'resultado': 'Res.', 'elo_after': 'ELO', 'prob_failure': 'P.Fallo',
                                'timestamp': 'Fecha',
                            }),
                            width='stretch',
                        )
                else:
                    st.info(f"{_sel_name} aún no ha respondido ninguna pregunta.")

                # ── Análisis Pedagógico con IA ─────────────────────────────────
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
                        # T9c: detectar errores estandarizados de la capa IA
                        if isinstance(_analysis, str) and (_analysis.startswith("ERROR_401:") or _analysis.startswith("ERROR_429:")):
                            st.error(_analysis.split(": ", 1)[1])
                        else:
                            with st.container(border=True):
                                st.markdown("#### 📋 Análisis Pedagógico con IA")
                                st.markdown(_analysis)
                    except (ConnectionError, TimeoutError):
                        st.error("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.")

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

        # Cargar cursos matriculados (disponible para todo el flujo del estudiante)
        _enrolled = cached('cache_enrollments',
                           lambda: repo.get_user_enrollments(st.session_state.user_id))

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
            mode = st.radio(
                "Modo",
                ["📝 Practicar", "📊 Estadísticas", "🎓 Mis Cursos", f"💬 Feedback{_fb_badge}"],
                label_visibility="collapsed",
            )
            st.caption("Navegación Principal")

            if mode == "📝 Practicar":
                if _enrolled and 'selected_course' in st.session_state:
                    _sc = st.session_state.selected_course
                    st.markdown(f"### 📚 {_sc['name']}")
                    if st.button("↩ Cambiar materia", key="sidebar_change_course"):
                        del st.session_state.selected_course
                        st.session_state.question_start_time = None
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

            if st.button("Cerrar Sesión"):
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
            invalidate_cache('cache_answered_ids', 'cache_elo_by_topic', 'cache_streak')
            # Forzar que get_next_question se llame de nuevo en la próxima recarga
            st.session_state.pop('current_question', None)

            st.session_state.question_start_time = None
            st.rerun()

        # --- VISTAS ---
        if mode == "📝 Practicar" and not _enrolled:
            st.title("🚀 Sala de Estudio")
            st.info(
                "📚 Aún no tienes cursos inscritos. "
                "Ve a **🎓 Mis Cursos** en el menú lateral para matricularte."
            )
        elif mode == "📝 Practicar" and 'selected_course' not in st.session_state:
            # ── Pantalla de selección de curso ──────────────────────────────
            st.title("🚀 Sala de Estudio")
            st.markdown("#### Selecciona la materia que deseas practicar")
            st.markdown("")

            # Grid de cards: 2 columnas
            for row_start in range(0, len(_enrolled), 2):
                cols = st.columns(2)
                for col_idx, course in enumerate(_enrolled[row_start:row_start + 2]):
                    c_name = course['name']
                    c_elo = st.session_state.vector.get(c_name)
                    c_rank, c_color = get_rank(c_elo)
                    with cols[col_idx]:
                        st.markdown(f"""
                        <div style="
                            padding: 24px; border-radius: 16px;
                            background: rgba(38, 39, 48, 0.95);
                            border: 1px solid {c_color}44;
                            box-shadow: 0 4px 20px {c_color}22;
                            text-align: center; margin-bottom: 12px;
                        ">
                            <h3 style="color: #fff !important; margin: 0 0 12px 0;
                                border-left: none; padding-left: 0;
                                background: linear-gradient(90deg, #00C9FF, #92FE9D);
                                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                                {c_name}
                            </h3>
                            <p style="color: {c_color}; font-size: 0.9rem; margin: 0;">{c_rank}</p>
                            <p style="color: #fff; font-size: 2.4rem; font-weight: 700; margin: 4px 0;">
                                {c_elo:.0f}
                            </p>
                            <p style="color: #888; font-size: 0.8rem; margin: 0;">Puntos ELO</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Practicar", key=f"sel_course_{course['id']}",
                                     width='stretch'):
                            st.session_state.selected_course = course
                            st.session_state.question_start_time = None
                            st.session_state.pop('current_question', None)
                            st.rerun()

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
                        <h1 style="font-size: 3.5rem; margin: 10px 0; color: white;">{current_elo_display:.0f} <span style="font-size: 1.2rem; color: #888;">± {current_rd_display:.0f}</span></h1>
                        <p style="color: #aaa; font-size: 0.9rem;">Puntos ELO en {topic_display_name} (± RD)</p>
                    </div>
                """, unsafe_allow_html=True)
                # T8c: racha de estudio (días consecutivos con actividad)
                _streak = cached('cache_streak',
                                lambda: repo.get_study_streak(st.session_state.user_id))
                if _streak > 0:
                    st.markdown(f"🔥 **Racha: {_streak} día{'s' if _streak != 1 else ''}**")
                st.info("💡 **Consejo:** La constancia es clave. Practica diariamente para consolidar tu aprendizaje.")

            with col2:
                st.subheader(f"📖 Ejercicio: {selected_topic}")

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

                    with st.container(border=True):
                        # Color dinámico por dificultad
                        # T9a: null safety — proteger accesos a campos del ítem
                        diff = item_data.get('difficulty') or 1000
                        if diff < 800:
                            diff_color = "#92FE9D"  # Verde neón (Fácil)
                        elif diff < 1100:
                            diff_color = "#FFD700"  # Dorado (Medio)
                        elif diff < 1400:
                            diff_color = "#FF8C00"  # Naranja (Difícil)
                        else:
                            diff_color = "#FF4B4B"  # Rojo (Experto)

                        # T8a: metadatos de área y tópico sobre el enunciado
                        _item_topic = item_data.get('topic') or selected_topic or ''
                        st.caption(f"Área: {selected_topic} | Tema: {_item_topic}")
                        st.markdown(f"<span style='color: {diff_color}; font-weight: 700; font-size: 0.9rem;'>⚡ Dificultad {diff:.0f}</span>", unsafe_allow_html=True)
                        st.markdown(f"### {item_data.get('content') or ''}")

                        # T14: soporte visual en preguntas — renderizar imagen si existe
                        _img_url = item_data.get('image_url') or item_data.get('image_path')
                        if _img_url:
                            try:
                                st.image(_img_url, width='stretch',
                                         caption="Figura correspondiente a la pregunta")
                            except Exception:
                                pass  # imagen no disponible — no romper la UI

                        st.write("")

                        if item_data.get('options'):
                            # Bug 3: Aleatorizar opciones
                            shuffled_options = item_data['options'].copy()
                            random.Random(item_data['id']).shuffle(shuffled_options)
                            option_labels = [chr(65 + i) for i in range(len(shuffled_options))]
                            label_to_text = dict(zip(option_labels, shuffled_options))
                            _item_id = item_data['id']

                            # Renderizar opciones con LaTeX via markdown
                            for lbl, opt in zip(option_labels, shuffled_options):
                                st.markdown(f"**{lbl}.** {opt}")

                            def _sync_answer(_id=_item_id, _map=label_to_text):
                                lbl = st.session_state.get(f"radio_{_id}")
                                st.session_state[f"answer_text_{_id}"] = _map.get(lbl)

                            st.radio(
                                "Selecciona tu respuesta:",
                                option_labels,
                                format_func=lambda x: x,
                                key=f"radio_{item_data['id']}",
                                on_change=_sync_answer,
                            )
                            selected_option = st.session_state.get(f"answer_text_{item_data['id']}")
                            st.write("")
                            submit_button = st.button(label="📝 Enviar Respuesta", width='stretch')

                            if submit_button:
                                is_correct = (selected_option == item_data.get('correct_option'))
                                if is_correct:
                                    st.success("¡Respuesta correcta! Excelente análisis. 🎓")
                                else:
                                    st.error(f"Respuesta incorrecta. La opción correcta era: **{item_data.get('correct_option') or '—'}**")
                                
                                time.sleep(1.5)
                                handle_answer_topic(is_correct, item_data)

                        # --- Ayuda del Tutor Socrático (Siempre disponible) ---
                        st.markdown("---")
                        st.info("💡 Si te sientes bloqueado, puedes pedir orientación. El tutor socrático no te dará la respuesta, pero te ayudará a razonar.")
                        _soc_help = None if st.session_state.ai_available else "IA no disponible en este entorno demo"
                        if st.button("🙋 Preguntar al Tutor Socrático", key=f"socratic_{item_data['id']}", width='stretch', disabled=not st.session_state.ai_available, help=_soc_help):
                            try:
                                current_ans = st.session_state.get(f"answer_text_{item_data['id']}", "Aún no ha seleccionado una opción")
                                # Model Router: seleccionar modelo óptimo para tutoría socrática
                                _soc_model = select_model_for_task(
                                    "tutor_socratic",
                                    st.session_state.get('lmstudio_models', []),
                                    st.session_state.model_cog,
                                    provider=st.session_state.get('ai_provider'),
                                )
                                with st.chat_message("assistant", avatar="🎓"):
                                    _soc_full = st.write_stream(get_socratic_guidance_stream(
                                        current_elo_display,
                                        item_data.get('topic') or '',
                                        item_data.get('content') or '',
                                        current_ans,
                                        correct_answer=item_data.get('correct_option') or '',
                                        all_options=item_data.get('options') or [],
                                        base_url=st.session_state.ai_url,
                                        model_name=_soc_model,
                                        api_key=st.session_state.cloud_api_key,
                                        provider=st.session_state.get('ai_provider'),
                                    ))
                                    # Validación post-generación: verificar que no viole reglas socrátivas
                                    if isinstance(_soc_full, str) and not validate_socratic_response(_soc_full):
                                        st.warning("⚠️ La respuesta fue filtrada por revelar demasiada información. Intenta de nuevo.")
                            except (ConnectionError, TimeoutError):
                                st.error("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.")
                            except Exception:
                                st.error("⚠️ El modelo no pudo procesar la solicitud. Verifica que esté cargado correctamente.")
                        elif not item_data.get('options'):
                            st.warning("Pregunta sin opciones configuradas.")

            # --- Procedimiento Manuscrito (columna izquierda, debajo del ELO) ---
            if item_data:
                with col1:
                    st.markdown("---")
                    show_upload = st.checkbox(
                        "📎 ¿Subir procedimiento para retroalimentación?",
                        key=f"show_upload_{item_data['id']}",
                    )
                    if show_upload:
                        uploaded_file = st.file_uploader(
                            "Foto, escaneo o PDF de tu desarrollo:",
                            type=["jpg", "jpeg", "png", "webp", "pdf"],
                            key=f"proc_upload_{item_data['id']}",
                            label_visibility="collapsed",
                        )
                        if uploaded_file is not None:
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
                                            except Exception:
                                                st.session_state[f'proc_no_vision_{_iid}'] = True

                                if st.session_state.get(f'proc_no_vision_{_iid}'):
                                    st.info("El profesor revisará el archivo y proporcionará la retroalimentación.")

                                # ── Resultado: revisión matemática rigurosa (Groq) ──
                                _math_review = st.session_state.get(f'proc_review_{_iid}')
                                if _math_review:
                                    with st.container(border=True):
                                        st.markdown("##### 🔬 Revisión Matemática Rigurosa")
                                        _pscore_v = _math_review.get('score_procedimiento', 0)
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
                                        except Exception:
                                            pass  # T10: fallback silencioso, no interrumpir flujo

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
            if _stat_streak > 0:
                st.markdown(f"🔥 **Racha de estudio: {_stat_streak} día{'s' if _stat_streak != 1 else ''} consecutivo{'s' if _stat_streak != 1 else ''}**")

            history_full = st.session_state.db.get_user_history_full(st.session_state.user_id)
            attempts_data = st.session_state.db.get_attempts_for_ai(st.session_state.user_id, limit=1000)
            # Cargar scores de procedimientos una sola vez para toda la sección
            _proc_scores = st.session_state.db.get_student_procedure_scores(st.session_state.user_id)

            m1, m2, m3, m4 = st.columns(4)
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
                if _proc_scores:
                    avg_proc = sum(s['score'] for s in _proc_scores) / len(_proc_scores)
                    st.metric("📝 Calidad de Procedimientos", f"{avg_proc:.1f} / 100",
                              delta=f"{len(_proc_scores)} evaluado(s)")
                else:
                    st.metric("📝 Calidad de Procedimientos", "Sin datos")

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
            st.title("🎓 Catálogo de Cursos")

            # ── Badge de nivel educativo (SOLO LECTURA — inmutable desde la UI) ─
            # El nivel se asigna en el registro y es la fuente de verdad para el
            # catálogo. get_available_courses() lo lee desde DB, nunca desde sesión.
            # No existe ningún mecanismo en la UI para cambiarlo.
            _level = st.session_state.education_level or 'universidad'
            _level_labels = {'universidad': "🎓 Universidad", 'colegio': "🏫 Colegio", 'concursos': "🏆 Concursos"}
            _level_label = _level_labels.get(_level, "🎓 Universidad")
            st.markdown(f"**Nivel académico:** {_level_label}")
            st.caption("Tu nivel se fijó al registrarte y determina qué cursos puedes ver.")

            st.markdown("---")

            # ── Catálogo filtrado estrictamente por nivel (vía servicio) ─────
            # get_available_courses lee el nivel desde DB, nunca desde sesión.
            _all_courses  = st.session_state.student_service.get_available_courses(
                st.session_state.user_id
            )
            _enrolled_ids = {c['id'] for c in _enrolled}

            if not _all_courses:
                st.info(f"No hay cursos disponibles para el nivel {_level_label} aún.")
            else:
                st.subheader(f"📚 Cursos disponibles — {_level_label}")
                for _course in _all_courses:
                    with st.container(border=True):
                        if _course['id'] in _enrolled_ids:
                            # ── Curso ya inscrito ────────────────────────────
                            _cc1, _cc2 = st.columns([4, 1])
                            with _cc1:
                                st.markdown(f"**{_course['name']} ✅ Inscrito**")
                                st.caption(_course['description'])
                            with _cc2:
                                if st.button("Desmatricular", key=f"unenroll_{_course['id']}"):
                                    repo.unenroll_user(st.session_state.user_id, _course['id'])
                                    invalidate_cache('cache_enrollments')
                                    st.session_state.pop('current_question', None)
                                    st.session_state.pop('selected_course', None)
                                    st.rerun()
                        else:
                            # ── Curso disponible: verificar grupos ──────────
                            _avail_groups = st.session_state.student_service.get_groups_for_course(
                                _course['id']
                            )
                            _cc1, _cc2 = st.columns([4, 1])
                            with _cc1:
                                st.markdown(f"**{_course['name']}**")
                                st.caption(_course['description'])
                                if not _avail_groups:
                                    st.caption("⚠️ Sin grupos disponibles actualmente.")
                                else:
                                    _grp_opts = {
                                        f"{g['name']} (Prof. {g['teacher_name']})": g['id']
                                        for g in _avail_groups
                                    }
                                    _sel_grp_label = st.selectbox(
                                        "Grupo",
                                        list(_grp_opts.keys()),
                                        key=f"grp_sel_{_course['id']}",
                                        label_visibility="collapsed",
                                    )
                                    _sel_grp_id = _grp_opts[_sel_grp_label]
                            with _cc2:
                                if _avail_groups:
                                    if st.button(
                                        "Matricularse",
                                        key=f"enroll_{_course['id']}",
                                        type="primary",
                                    ):
                                        st.session_state.student_service.enroll_in_course(
                                            st.session_state.user_id,
                                            _course['id'],
                                            _sel_grp_id,
                                        )
                                        invalidate_cache('cache_enrollments')
                                        st.rerun()

            # ── Resumen de matrículas activas ─────────────────────────────────
            if _enrolled:
                st.markdown("---")
                st.subheader("📋 Mis Cursos Inscritos")
                for _ec in _enrolled:
                    _grp_label = _ec.get('group_name', '')
                    _suffix = f"— {_grp_label}" if _grp_label else f"— {_ec['block']}"
                    st.markdown(f"- **{_ec['name']}** {_suffix}")

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
