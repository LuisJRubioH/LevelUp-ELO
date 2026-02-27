import streamlit as st
import os
import sys

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
import src.infrastructure.persistence.sqlite_repository as db_mod
import src.infrastructure.external_api.ai_client as ai_mod
importlib.reload(db_mod)
importlib.reload(ai_mod)

from src.domain.elo.vector_elo import VectorRating, aggregate_global_elo, aggregate_global_rd
from src.domain.elo.model import expected_score, calculate_dynamic_k, Item
SQLiteRepository = db_mod.SQLiteRepository
analyze_performance_local = ai_mod.analyze_performance_local
get_active_models = ai_mod.get_active_models
get_socratic_guidance_stream = ai_mod.get_socratic_guidance_stream
analyze_procedure_image = ai_mod.analyze_procedure_image
_model_supports_vision = ai_mod._model_supports_vision
import time
import extra_streamlit_components as stx

# Configuración de página
st.set_page_config(page_title="ELO Learning — Evaluación Adaptativa", layout="wide", page_icon="🎓")

# Inicializar Base de Datos
if 'db' not in st.session_state:
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
    st.session_state.ai_url = "http://192.168.40.66:1234/v1"

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
    if elo < 800: return "🌱 Inicial", "#28a745"
    if elo < 1000: return "📖 Básico", "#17a2b8"
    if elo < 1200: return "✏️ Intermedio", "#007bff"
    if elo < 1400: return "📐 Avanzado", "#6610f2"
    if elo < 1600: return "🔬 Experto", "#fd7e14"
    if elo < 1800: return "🎓 Sobresaliente", "#dc3545"
    return "⭐ Excelencia", "#e83e8c"

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
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            st.session_state.role = user[3]
        else:
            cookie_manager.delete("elo_auth_token")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA DE LOGIN / REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 8px;'>🎓 ELO Learning</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa; font-size: 1.2rem; margin-bottom: 40px;'>Plataforma de evaluación y aprendizaje adaptativo basada en el sistema ELO</p>", unsafe_allow_html=True)

    col_info, col_login = st.columns([1.4, 1])

    with col_info:
        st.markdown("""
        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>📌 ¿Qué es ELO Learning?</h3>
            <p>ELO Learning es una plataforma académica de evaluación adaptativa que utiliza el <b>sistema de calificación ELO</b> —originalmente diseñado para el ajedrez— para medir con precisión el nivel de dominio de cada estudiante en distintas materias.</p>
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
                
                group_id = None
                if new_role == "Estudiante":
                    all_groups = st.session_state.db.get_all_groups()
                    if not all_groups:
                        st.warning("⚠️ No hay grupos disponibles. Un profesor debe crear un grupo antes de que puedas registrarte.")
                    else:
                        group_options = {f"{g['name']} ({g['teacher_name']})": g['id'] for g in all_groups}
                        selected_group_label = st.selectbox("Selecciona tu grupo", list(group_options.keys()))
                        group_id = group_options[selected_group_label]

                st.write("")
                if st.button("Crear Cuenta"):
                    role_map = {"Estudiante": "student", "Profesor": "teacher"}
                    chosen_role = role_map[new_role]
                    
                    if chosen_role == 'student' and group_id is None:
                        st.error("Debes seleccionar un grupo para registrarte como estudiante.")
                    else:
                        success, message = st.session_state.db.register_user(new_user, new_pass, chosen_role, group_id)
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
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
            st.write(f"### 🛡️ Admin: **{st.session_state.username}**")
            st.markdown("---")
            if st.button("Cerrar Sesión"):
                logout()

        st.title("🛡️ Panel de Administración")

        # ── Profesores pendientes ──────────────────────────────────────────────
        st.subheader("⏳ Solicitudes de Profesores Pendientes")
        pending = st.session_state.db.get_pending_teachers()

        if not pending:
            st.info("No hay solicitudes pendientes.")
        else:
            for teacher in pending:
                col_name, col_date, col_ok, col_no = st.columns([2, 2, 1, 1])
                with col_name:
                    st.write(f"👤 **{teacher['username']}**")
                with col_date:
                    st.caption(f"Registrado: {teacher['created_at'][:10]}")
                with col_ok:
                    if st.button("✅ Aprobar", key=f"approve_{teacher['id']}"):
                        st.session_state.db.approve_teacher(teacher['id'])
                        st.rerun()
                with col_no:
                    if st.button("❌ Rechazar", key=f"reject_{teacher['id']}"):
                        st.session_state.db.reject_teacher(teacher['id'])
                        st.rerun()

        st.markdown("---")

        # ── Profesores activos ─────────────────────────────────────────────────
        st.subheader("✅ Profesores Activos")
        approved_teachers = st.session_state.db.get_approved_teachers()
        if not approved_teachers:
            st.info("No hay profesores activos aún.")
        else:
            for t in approved_teachers:
                col_name, col_date, col_baja = st.columns([2, 2, 1])
                with col_name:
                    st.write(f"🏫 **{t['username']}**")
                with col_date:
                    st.caption(f"Desde: {t['created_at'][:10]}")
                with col_baja:
                    if st.button("🚫 Dar de baja", key=f"deact_t_{t['id']}"):
                        st.session_state.db.deactivate_user(t['id'])
                        st.rerun()

        # Profesores dados de baja
        conn_t = st.session_state.db.get_connection()
        cur_t = conn_t.cursor()
        cur_t.execute("SELECT id, username, created_at FROM users WHERE role='teacher' AND active=0 ORDER BY username ASC")
        inactive_teachers = [{'id': r[0], 'username': r[1], 'created_at': r[2]} for r in cur_t.fetchall()]
        conn_t.close()
        if inactive_teachers:
            with st.expander(f"Ver {len(inactive_teachers)} profesor(es) dado(s) de baja"):
                for t in inactive_teachers:
                    col_n, col_r = st.columns([3, 1])
                    with col_n:
                        st.write(f"~~{t['username']}~~ — dado de baja")
                    with col_r:
                        if st.button("✅ Reactivar", key=f"react_t_{t['id']}"):
                            st.session_state.db.reactivate_user(t['id'])
                            st.rerun()

        st.markdown("---")

        # ── Estudiantes registrados ────────────────────────────────────────────
        st.subheader("🎓 Estudiantes Registrados")
        all_students = st.session_state.db.get_all_students_admin()
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
                    st.caption(f"Desde: {s['created_at'][:10]}")
                with col_baja:
                    if st.button("🚫 Dar de baja", key=f"deact_s_{s['id']}"):
                        st.session_state.db.deactivate_user(s['id'])
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
                                st.rerun()

            st.markdown("---")

            # ── Reasignación de Grupo (Solo Admin) ──────────────────────────────
            st.subheader("📍 Reasignación de Grupo")
            with st.container(border=True):
                col_s, col_g = st.columns(2)
                
                # Cargar datos necesarios
                all_groups = st.session_state.db.get_all_groups()
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
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(message)

    # ══════════════════════════════════════════════════════════════════════════
    # VISTA: PROFESOR
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.role == 'teacher':
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
            st.write(f"### 🏫 Profesor: **{st.session_state.username}**")
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
                st.session_state.ai_provider_mode = {"🤖 Auto": "auto", "☁️ API Key": "cloud", "🖥️ Local": "local"}[_t_mode]

                if _t_mode == "🤖 Auto":
                    if st.button("🔄 Reconectar", key="btn_reconnect_teacher"):
                        for _k in ('ai_available', 'lmstudio_models'):
                            st.session_state.pop(_k, None)
                        st.rerun()
                elif _t_mode == "☁️ API Key":
                    _key_in = st.text_input(
                        "API Key", type="password",
                        value=st.session_state.cloud_api_key or "",
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
                    with st.container(border=True):
                        st.markdown(
                            f"**👤 {_sub['student_name']}** — "
                            f"enviado el {_sub['submitted_at'][:16]}"
                        )
                        st.caption(f"Pregunta: {_sub['item_content'][:120]}{'…' if len(_sub['item_content']) > 120 else ''}")
                        _c_img, _c_fb = st.columns([1, 1])
                        with _c_img:
                            # Mostrar imagen desde archivo si existe, si no desde BLOB
                            _img_path = _sub.get('procedure_image_path')
                            if _img_path and os.path.exists(_img_path):
                                st.image(_img_path, caption="Procedimiento del estudiante", use_container_width=True)
                            elif _sub.get('image_data'):
                                st.image(bytes(_sub['image_data']), caption="Procedimiento del estudiante", use_container_width=True)
                            else:
                                st.warning("Imagen no disponible.")
                        with _c_fb:
                            _proc_score = st.number_input(
                                "📊 Calidad del procedimiento (0.0 – 5.0)",
                                min_value=0.0, max_value=5.0, value=3.0, step=0.1,
                                format="%.1f",
                                key=f"score_{_sub['id']}",
                                help="Evalúa la calidad del desarrollo matemático del estudiante.",
                            )
                            _fb_text = st.text_area(
                                "📝 Retroalimentación escrita:",
                                key=f"fb_text_{_sub['id']}",
                                placeholder="Escribe tu retroalimentación aquí…",
                                height=120,
                            )
                            _fb_img = st.file_uploader(
                                "🖼️ Sube el procedimiento corregido (opcional):",
                                type=["jpg", "jpeg", "png", "webp"],
                                key=f"fb_img_{_sub['id']}",
                            )
                            _can_submit = bool(_fb_text or _fb_img)
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
            col_a, col_b = st.columns([3, 1])
            with col_a:
                new_group_name = st.text_input("Nombre del nuevo grupo", placeholder="Ej: Cálculo I - 2024")
            with col_b:
                st.write(" ") # Espaciado
                if st.button("➕ Crear Grupo", width='stretch'):
                    if new_group_name:
                        st.session_state.db.create_group(new_group_name, st.session_state.user_id)
                        st.success(f"Grupo '{new_group_name}' creado.")
                        st.rerun()
                    else:
                        st.error("Ingresa un nombre.")
            
            my_groups = st.session_state.db.get_groups_by_teacher(st.session_state.user_id)
            if my_groups:
                st.write("**Mis Grupos:**")
                for g in my_groups:
                    st.caption(f"• {g['name']} (Creado: {g['created_at'][:10]})")
            else:
                st.info("No tienes grupos creados aún.")

        st.markdown("---")

        # ── Filtro por Grupo ───────────────────────────────────────────────────
        # Usar TeacherService para el dashboard
        students, groups = st.session_state.teacher_service.get_dashboard_data(st.session_state.user_id)
        
        if not students:
            st.info("Aún no tienes estudiantes vinculados a tus grupos.")
        else:
            group_filter_options = {"Todos mis grupos": None}
            group_filter_options.update({g['name']: g['id'] for g in groups})
            
            selected_group_name = st.selectbox("🎯 Filtrar por Grupo", list(group_filter_options.keys()))
            selected_group_id = group_filter_options[selected_group_name]

            if selected_group_id:
                students = [s for s in students if s['group_id'] == selected_group_id]
            # else: students already contains all students for the teacher

            # ── Sección 1: Rendimiento ELO (Aciertos) ─────────────────────────
            st.subheader(f"📈 Rendimiento ELO (Aciertos) — {selected_group_name}")

            summary_rows = []
            for s in students:
                elo_by_topic = st.session_state.db.get_latest_elo_by_topic(s['id'])
                if elo_by_topic:
                    global_elo = sum(e for e, r in elo_by_topic.values()) / len(elo_by_topic)
                else:
                    global_elo = 1000.0
                rank_name, _ = get_rank(global_elo)
                row = {
                    "Estudiante": s['username'],
                    "Grupo": s.get('group_name', selected_group_name),
                    "ELO Global": round(global_elo, 1),
                    "Rango": rank_name,
                }
                row.update({topic: round(val[0], 1) for topic, val in elo_by_topic.items()})
                summary_rows.append(row)

            df_summary = pd.DataFrame(summary_rows)
            _str_cols_elo = {"Estudiante", "Grupo", "Rango"}
            for col in df_summary.columns:
                if col not in _str_cols_elo:
                    df_summary[col] = pd.to_numeric(df_summary[col], errors='coerce').fillna(1000.0)
            st.dataframe(df_summary, width='stretch')

            st.markdown("---")

            # ── Sección 2: Calidad de Procedimientos (Desarrollo) ─────────────
            st.subheader("📝 Calidad de Procedimientos (Desarrollo)")
            st.caption(
                "Promedio de notas de desarrollos manuales enviados y calificados, agrupado por "
                "estudiante y curso.  🔴 < 3.0 Deficiente · 🟡 3.0–4.0 Regular · 🟢 > 4.0 Excelente"
            )
            _proc_table_rows = st.session_state.db.get_students_procedure_summary_table(
                st.session_state.user_id
            )
            if _proc_table_rows:
                df_proc_teacher = pd.DataFrame(_proc_table_rows)[
                    ['student', 'course_name', 'avg_score', 'count']
                ].rename(columns={
                    'student':     'Estudiante',
                    'course_name': 'Curso',
                    'avg_score':   'Promedio (0-5)',
                    'count':       'Envíos',
                })

                def _score_color(val):
                    if not isinstance(val, (int, float)):
                        return ''
                    if val < 3.0:
                        return 'color: #ef5350'
                    elif val <= 4.0:
                        return 'color: #FFC107'
                    return 'color: #66BB6A'

                st.dataframe(
                    df_proc_teacher.style.map(_score_color, subset=['Promedio (0-5)']),
                    width='stretch',
                )
            else:
                st.info("Ningún estudiante ha enviado procedimientos evaluados aún.")

            st.markdown("---")

            # ── Detalle por estudiante ─────────────────────────────────────────
            st.subheader("🔍 Detalle de Estudiante")
            student_names = [s['username'] for s in students]
            selected_name = st.selectbox("Selecciona un estudiante", student_names)
            selected_student = next(s for s in students if s['username'] == selected_name)

            tab_elo, tab_prob, tab_history = st.tabs(["📈 Progreso ELO", "🎯 Prob. de Fallo", "📄 Tabla de Intentos"])

            with tab_history:
                # Usar TeacherService para el reporte
                attempts = st.session_state.teacher_service.get_student_report(selected_student['id'])
                
                if not attempts:
                    st.info(f"{selected_name} aún no ha respondido ninguna pregunta.")
                else:
                    df = pd.DataFrame(attempts)
                    df['intento'] = range(1, len(df) + 1)
                    df['resultado'] = df['is_correct'].map({1: '✅ Correcto', 0: '❌ Incorrecto', True: '✅ Correcto', False: '❌ Incorrecto'})

                    with tab_elo:
                        st.markdown(f"**Evolución del ELO de {selected_name} por tema**")
                        fig_elo = go.Figure()
                        for topic in df['topic'].unique():
                            td = df[df['topic'] == topic]
                            fig_elo.add_trace(go.Scatter(
                                x=td['intento'], y=td['elo_after'],
                                mode='lines+markers', name=topic, line=dict(width=2)
                            ))
                        fig_elo.update_layout(
                            template="plotly_dark",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis_title="Intento #", yaxis_title="ELO",
                            legend=dict(bgcolor='rgba(38,39,48,0.8)', bordercolor='gray')
                        )
                        st.plotly_chart(fig_elo, width='stretch')

                        # --- Botón de Análisis Comparativo ELO + Procedimientos ---
                        st.markdown("---")
                        _ai_help = None if st.session_state.ai_available else "IA no disponible en este entorno demo"
                        if st.button("🧠 Generar Análisis Pedagógico con IA", key=f"ai_anal_{selected_student['id']}", width='stretch', disabled=not st.session_state.ai_available, help=_ai_help):
                            try:
                                with st.spinner("Analizando trayectoria del estudiante..."):
                                    _sel_proc = st.session_state.db.get_student_procedure_scores(selected_student['id'])
                                    _sel_proc_stats = {
                                        'count': len(_sel_proc),
                                        'avg_score': (sum(p['score'] for p in _sel_proc) / len(_sel_proc)) if _sel_proc else None,
                                        'scores': [p['score'] for p in _sel_proc],
                                    }
                                    _sel_proc_by_course = st.session_state.db.get_procedure_stats_by_course(selected_student['id'])
                                    analysis = st.session_state.teacher_service.generate_ai_analysis(
                                        selected_student['id'], global_elo,
                                        api_key=st.session_state.cloud_api_key,
                                        provider=st.session_state.get('ai_provider'),
                                        procedure_stats=_sel_proc_stats,
                                        procedure_stats_by_course=_sel_proc_by_course,
                                    )
                                if analysis and analysis.startswith("ERROR_401:"):
                                    st.error(analysis.replace("ERROR_401: ", ""))
                                else:
                                    with st.container(border=True):
                                        st.markdown("#### 📋 Análisis Pedagógico con IA")
                                        st.markdown(analysis)
                            except (ConnectionError, TimeoutError):
                                st.info("IA no disponible en este momento. Inténtalo más tarde.")

                    with tab_prob:
                        st.markdown(f"**Probabilidad de acierto de {selected_name} en cada pregunta**")
                        st.caption("Calculada con el ELO del estudiante **antes** del intento. Barras verdes = el sistema esperaba que acertara. Barras rojas = la pregunta era demasiado difícil para su nivel.")

                        df_prob = df.dropna(subset=['prob_failure']).copy()

                        if df_prob.empty:
                            st.info("Cargando datos... (recarga la página si persiste el mensaje)")
                        else:
                            df_prob['prob_success'] = 1.0 - df_prob['prob_failure']

                            bar_colors = ['#28a745' if ps >= 0.5 else '#dc3545' for ps in df_prob['prob_success']]
                            fig_prob = go.Figure()
                            fig_prob.add_trace(go.Bar(
                                x=df_prob['intento'], y=df_prob['prob_success'],
                                marker_color=bar_colors, opacity=0.85, name='Prob. Acierto'
                            ))
                            fig_prob.add_hline(y=0.5, line_dash='dash', line_color='#ffc107',
                                               annotation_text='Umbral 50%', annotation_font_color='#ffc107')
                            fig_prob.update_layout(
                                template="plotly_dark",
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                xaxis_title="Intento #", yaxis_title="Prob. de Acierto",
                                yaxis=dict(range=[0, 1])
                            )
                            st.plotly_chart(fig_prob, width='stretch')

                            # Métricas rápidas
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Prob. Acierto Promedio", f"{df_prob['prob_success'].mean():.1%}")
                            m2.metric("Acierto más alto", f"{df_prob['prob_success'].max():.1%}")
                            m3.metric("Preguntas retadoras (<50%)", int((df_prob['prob_success'] < 0.5).sum()))

                    with tab_history:
                        st.dataframe(
                            df[['intento', 'topic', 'difficulty', 'resultado', 'elo_after', 'prob_failure', 'timestamp']]
                            .rename(columns={
                                'intento': '#', 'topic': 'Tema', 'difficulty': 'Dificultad',
                                'resultado': 'Resultado', 'elo_after': 'ELO después',
                                'prob_failure': 'Prob. Fallo', 'timestamp': 'Fecha'
                            }),
                            width='stretch'
                        )

    # ══════════════════════════════════════════════════════════════════════════
    # VISTA: ESTUDIANTE (sin cambios funcionales)
    # ══════════════════════════════════════════════════════════════════════════
    else:
        # 1. Recuperar Estado Inicial de DB para VectorELO
        if 'vector_initialized' not in st.session_state:
            latest_elos = st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id)
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
            st.session_state.education_level = repo.get_education_level(st.session_state.user_id)

        if not st.session_state.education_level:
            st.title("🎓 Bienvenido a ELO Learning")
            st.markdown("### ¿En qué nivel educativo estás?")
            st.markdown("Esto nos permite mostrarte los cursos adecuados para ti.")
            st.write("")
            col_uni, col_col = st.columns(2)
            with col_uni:
                with st.container(border=True):
                    st.markdown("#### 🎓 Universidad")
                    st.write("Cálculo, Álgebra Lineal, EDO, Probabilidad, Estadística")
                    st.write("")
                    if st.button("Soy universitario", use_container_width=True, type="primary", key="onb_uni"):
                        repo.set_education_level(st.session_state.user_id, 'universidad')
                        st.session_state.education_level = 'universidad'
                        st.rerun()
            with col_col:
                with st.container(border=True):
                    st.markdown("#### 🏫 Colegio")
                    st.write("Álgebra Básica, Aritmética, Trigonometría, Geometría")
                    st.write("")
                    if st.button("Soy de colegio", use_container_width=True, key="onb_col"):
                        repo.set_education_level(st.session_state.user_id, 'colegio')
                        st.session_state.education_level = 'colegio'
                        st.rerun()
            st.stop()

        # Cargar cursos matriculados (disponible para todo el flujo del estudiante)
        _enrolled = repo.get_user_enrollments(st.session_state.user_id)

        # Defaults para variables usadas en las vistas
        selected_course_id = None
        selected_topic = None

        # Sidebar Estilizado
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
            st.write(f"### Hola, **{st.session_state.username}**")
            mode = st.radio(
                "Modo",
                ["📝 Practicar", "📊 Estadísticas", "🎓 Mis Cursos"],
                label_visibility="collapsed",
            )
            st.caption("Navegación Principal")

            if mode == "📝 Practicar":
                st.markdown("### Curso Activo")
                if _enrolled:
                    _course_names = [c['name'] for c in _enrolled]
                    _sel_name = st.selectbox("¿Qué quieres estudiar hoy?", _course_names)
                    _sel_course = next(c for c in _enrolled if c['name'] == _sel_name)
                    selected_course_id = _sel_course['id']
                    selected_topic = _sel_course['name']
                else:
                    st.warning("Sin cursos inscritos. Ve a '🎓 Mis Cursos'.")

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
                st.session_state.ai_provider_mode = {"🤖 Auto": "auto", "☁️ API Key": "cloud", "🖥️ Local": "local"}[_s_mode]

                if _s_mode == "🤖 Auto":
                    if st.button("🔄 Reconectar", key="btn_reconnect_ai"):
                        for _k in ('ai_available', 'lmstudio_models'):
                            st.session_state.pop(_k, None)
                        st.rerun()
                elif _s_mode == "☁️ API Key":
                    _key_in_st = st.text_input(
                        "API Key", type="password",
                        value=st.session_state.cloud_api_key or "",
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
                            _best = ai_mod.select_best_model(_det['models'])
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
            
            # Delegar procesamiento al servicio
            is_correct, cog_data = st.session_state.student_service.process_answer(
                st.session_state.user_id, item_data,
                # La opción seleccionada se recupera del texto mapeado (soporte LaTeX)
                st.session_state.get(f"answer_text_{item_data['id']}"),
                reasoning, time_taken, st.session_state.vector
            )

            st.session_state.session_questions_count += 1
            if is_correct:
                st.session_state.session_correct_ids.add(item_data['id'])
            else:
                st.session_state.session_wrong_timestamps[item_data['id']] = float(st.session_state.session_questions_count)

            st.session_state.question_start_time = None
            st.rerun()

        # --- VISTAS ---
        if mode == "📝 Practicar" and (not _enrolled or not selected_course_id):
            st.title("🚀 Sala de Estudio")
            st.info(
                "📚 Aún no tienes cursos inscritos. "
                "Ve a **🎓 Mis Cursos** en el menú lateral para matricularte."
            )
        elif mode == "📝 Practicar":
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
                st.info("💡 **Consejo:** La constancia es clave. Practica diariamente para consolidar tu aprendizaje.")

            with col2:
                st.subheader(f"📖 Ejercicio: {selected_topic}")

                # Delegar obtención de pregunta al servicio (filtrado exclusivo por curso activo)
                item_data, status = st.session_state.student_service.get_next_question(
                    st.session_state.user_id, selected_topic, st.session_state.vector,
                    session_correct_ids=st.session_state.session_correct_ids,
                    session_wrong_timestamps=st.session_state.session_wrong_timestamps,
                    session_questions_count=st.session_state.session_questions_count,
                    course_id=selected_course_id,
                )

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
                        diff = item_data['difficulty']
                        if diff < 800:
                            diff_color = "#92FE9D"  # Verde neón (Fácil)
                        elif diff < 1100:
                            diff_color = "#FFD700"  # Dorado (Medio)
                        elif diff < 1400:
                            diff_color = "#FF8C00"  # Naranja (Difícil)
                        else:
                            diff_color = "#FF4B4B"  # Rojo (Experto)

                        st.markdown(f"<span style='color: {diff_color}; font-weight: 700; font-size: 0.9rem;'>⚡ Dificultad {diff:.0f}</span>", unsafe_allow_html=True)
                        st.markdown(f"### {item_data['content']}")
                        st.write("")

                        if 'options' in item_data:
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
                                is_correct = (selected_option == item_data['correct_option'])
                                if is_correct:
                                    st.success("¡Respuesta correcta! Excelente análisis. 🎓")
                                else:
                                    st.error(f"Respuesta incorrecta. La opción correcta era: **{item_data['correct_option']}**")
                                
                                time.sleep(1.5)
                                handle_answer_topic(is_correct, item_data)

                        # --- Ayuda del Tutor Socrático (Siempre disponible) ---
                        st.markdown("---")
                        st.info("💡 Si te sientes bloqueado, puedes pedir orientación. El tutor socrático no te dará la respuesta, pero te ayudará a razonar.")
                        _soc_help = None if st.session_state.ai_available else "IA no disponible en este entorno demo"
                        if st.button("🙋 Preguntar al Tutor Socrático", key=f"socratic_{item_data['id']}", width='stretch', disabled=not st.session_state.ai_available, help=_soc_help):
                            try:
                                current_ans = st.session_state.get(f"answer_text_{item_data['id']}", "Aún no ha seleccionado una opción")
                                with st.chat_message("assistant", avatar="🎓"):
                                    st.write_stream(get_socratic_guidance_stream(
                                        current_elo_display,
                                        item_data['topic'],
                                        item_data['content'],
                                        current_ans,
                                        correct_answer=item_data['correct_option'],
                                        all_options=item_data['options'],
                                        base_url=st.session_state.ai_url,
                                        model_name=st.session_state.model_cog,
                                        api_key=st.session_state.cloud_api_key,
                                        provider=st.session_state.get('ai_provider'),
                                    ))
                            except (ConnectionError, TimeoutError):
                                st.info("IA no disponible en este momento. Inténtalo más tarde.")
                        elif 'options' not in item_data:
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
                            "Foto o escaneo de tu desarrollo:",
                            type=["jpg", "jpeg", "png", "webp"],
                            key=f"proc_upload_{item_data['id']}",
                            label_visibility="collapsed",
                        )
                        if uploaded_file is not None:
                            _iid = item_data['id']
                            _uid = st.session_state.user_id
                            _ext = uploaded_file.name.rsplit('.', 1)[-1].lower()
                            _mime = {'jpg':'image/jpeg','jpeg':'image/jpeg',
                                     'png':'image/png','webp':'image/webp'}.get(_ext,'image/jpeg')

                            st.image(uploaded_file, use_container_width=True)

                            _vision_ok = _model_supports_vision(
                                st.session_state.model_analysis,
                                st.session_state.get('ai_provider'),
                            )

                            # ── Análisis con IA ───────────────────────────────
                            if _vision_ok:
                                if st.button(
                                    "🔍 Analizar procedimiento",
                                    key=f"analyze_proc_{_iid}",
                                    width='stretch',
                                    disabled=not st.session_state.ai_available,
                                ):
                                    with st.spinner("Analizando procedimiento..."):
                                        try:
                                            result = analyze_procedure_image(
                                                uploaded_file.getvalue(), _mime,
                                                item_data['content'],
                                                model_name=st.session_state.model_analysis,
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

                                _ai_fb = st.session_state.get(f'proc_fb_{_iid}')
                                if _ai_fb:
                                    with st.container(border=True):
                                        st.markdown("##### 🔍 Retroalimentación del procedimiento")
                                        st.markdown(_ai_fb)

                            # ── Envío al docente (sin visión o fallback) ──────
                            _no_vision = (not _vision_ok or
                                          st.session_state.get(f'proc_no_vision_{_iid}', False))
                            if _no_vision:
                                _sub = st.session_state.db.get_student_submission(_uid, _iid)
                                if _sub is None:
                                    st.info("El profesor revisará el archivo y proporcionará la retroalimentación.")
                                    if st.button(
                                        "📤 Enviar al profesor para revisión",
                                        key=f"send_teacher_{_iid}",
                                        width='stretch',
                                    ):
                                        st.session_state.db.save_procedure_submission(
                                            _uid, _iid, item_data['content'],
                                            uploaded_file.getvalue(), _mime,
                                        )
                                        st.rerun()
                                elif _sub['status'] == 'pending':
                                    st.info("⏳ Procedimiento enviado. Tu profesor lo revisará pronto.")
                                elif _sub['status'] == 'reviewed':
                                    with st.container(border=True):
                                        st.markdown("##### ✅ Retroalimentación del Profesor")
                                        if _sub.get('procedure_score') is not None:
                                            st.metric("📊 Nota del procedimiento", f"{_sub['procedure_score']:.1f} / 5.0")
                                        if _sub.get('teacher_feedback'):
                                            st.markdown(_sub['teacher_feedback'])
                                        # Mostrar imagen desde archivo si existe, si no desde BLOB
                                        _fb_path = _sub.get('feedback_image_path')
                                        if _fb_path and os.path.exists(_fb_path):
                                            st.image(_fb_path, caption="Procedimiento calificado", use_container_width=True)
                                        elif _sub.get('feedback_image'):
                                            st.image(bytes(_sub['feedback_image']), caption="Procedimiento calificado", use_container_width=True)

        elif mode == "📊 Estadísticas":
            st.title("📊 Estadísticas de Aprendizaje")

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
                    st.metric("📝 Calidad de Procedimientos", f"{avg_proc:.1f} / 5.0",
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
                        if _avg < 3.0:
                            _icon, _lbl = "🔴", "Deficiente"
                        elif _avg <= 4.0:
                            _icon, _lbl = "🟡", "Regular"
                        else:
                            _icon, _lbl = "🟢", "Excelente"
                        st.markdown(
                            f"- **{_cdata['course_name']}**: {_icon} {_lbl} — "
                            f"{_avg:.1f}/5.0 ({_cdata['count']} envío(s))"
                        )

            st.markdown("---")

            st.subheader("🏆 Dominio por Materia")
            current_elos = st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id)

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
                    if isinstance(recs, str) and recs.startswith("ERROR_401:"):
                        st.error(recs.replace("ERROR_401: ", ""))
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
                            st.markdown(f"**🔍 Diagnóstico:** {rec.get('diagnostico', 'N/A')}")
                            _CALLOUT[idx](f"**📝 Acción:** {rec.get('accion', 'N/A')}")
                            st.markdown(f"**💡 Justificación:** {rec.get('justificacion', 'N/A')}")
                            ejercicios = rec.get('ejercicios', 0)
                            if ejercicios:
                                st.markdown(f"**🔢 Meta sugerida:** {ejercicios} ejercicios")

        elif mode == "🎓 Mis Cursos":
            st.title("🎓 Catálogo de Cursos")

            # ── Badge de nivel educativo ──────────────────────────────────────
            _level = st.session_state.education_level or 'universidad'
            _level_label = "🎓 Universidad" if _level == 'universidad' else "🏫 Colegio"
            _level_block = "Universidad" if _level == 'universidad' else "Colegio"

            col_lv, col_btn = st.columns([3, 1])
            with col_lv:
                st.markdown(f"**Nivel actual:** {_level_label}")
                st.caption("Tus cursos disponibles se filtran según este nivel.")
            with col_btn:
                _alt_level  = 'colegio'      if _level == 'universidad' else 'universidad'
                _alt_label  = "Cambiar a Colegio" if _level == 'universidad' else "Cambiar a Universidad"
                if st.button(_alt_label, key="btn_change_level"):
                    repo.set_education_level(st.session_state.user_id, _alt_level)
                    st.session_state.education_level = _alt_level
                    st.rerun()

            st.markdown("---")

            # ── Catálogo filtrado por bloque ──────────────────────────────────
            _all_courses   = repo.get_courses(block=_level_block)
            _enrolled_ids  = {c['id'] for c in _enrolled}

            if not _all_courses:
                st.info(f"No hay cursos disponibles para el nivel {_level_label} aún.")
            else:
                st.subheader(f"📚 Cursos disponibles — {_level_label}")
                for _course in _all_courses:
                    with st.container(border=True):
                        _cc1, _cc2 = st.columns([4, 1])
                        with _cc1:
                            _badge = " ✅ Inscrito" if _course['id'] in _enrolled_ids else ""
                            st.markdown(f"**{_course['name']}{_badge}**")
                            st.caption(_course['description'])
                        with _cc2:
                            if _course['id'] in _enrolled_ids:
                                if st.button(
                                    "Desmatricular",
                                    key=f"unenroll_{_course['id']}",
                                ):
                                    repo.unenroll_user(st.session_state.user_id, _course['id'])
                                    st.rerun()
                            else:
                                if st.button(
                                    "Inscribirse",
                                    key=f"enroll_{_course['id']}",
                                    type="primary",
                                ):
                                    repo.enroll_user(st.session_state.user_id, _course['id'])
                                    st.rerun()

            # ── Resumen de matrículas activas ─────────────────────────────────
            if _enrolled:
                st.markdown("---")
                st.subheader("📋 Mis Cursos Inscritos")
                for _ec in _enrolled:
                    st.markdown(f"- **{_ec['name']}** — {_ec['block']}")
