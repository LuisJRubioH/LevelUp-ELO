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

if 'ai_available' not in st.session_state:
    st.session_state.ai_available = bool(get_active_models(st.session_state.ai_url))

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

# Sincronizar banco de ítems con la DB al inicio
try:
    if 'bank_synced_v11' not in st.session_state:
        with open("items/bank.json", "r", encoding="utf-8") as f:
            bank_data = json.load(f)
        st.session_state.db.sync_items_from_json(bank_data)
        st.session_state['bank_synced_v11'] = True
except Exception as e:
    st.error(f"Error sincronizando banco de ítems: {e}")

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
            if st.button("Cerrar Sesión"):
                logout()

        st.title("🏫 Panel del Profesor")

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

            # ── Tabla resumen de ELO por estudiante ───────────────────────────
            st.subheader(f"📋 Resumen de Estudiantes - {selected_group_name}")

            summary_rows = []
            for s in students:
                elo_by_topic = st.session_state.db.get_latest_elo_by_topic(s['id'])
                # elo_by_topic es {topic: (elo, rd)}
                if elo_by_topic:
                    global_elo = sum(e for e, r in elo_by_topic.values()) / len(elo_by_topic)
                else:
                    global_elo = 1000.0
                
                rank_name, _ = get_rank(global_elo)
                row = {
                    "Estudiante": s['username'], 
                    "Grupo": s.get('group_name', selected_group_name), 
                    "ELO Global": round(global_elo, 1), 
                    "Rango": rank_name
                }
                # Añadir cada tópico a la fila (solo el valor de elo para la tabla resumen)
                row.update({topic: round(val[0], 1) for topic, val in elo_by_topic.items()})
                summary_rows.append(row)


            df_summary = pd.DataFrame(summary_rows)
            # Asegurar que las columnas de tópicos sean numéricas para evitar error de Arrow
            # Llenar con 1000.0 (ELO base) en lugar de un string "—"
            for col in df_summary.columns:
                if col not in ["Estudiante", "Grupo", "Rango"]:
                    df_summary[col] = pd.to_numeric(df_summary[col], errors='coerce').fillna(1000.0)
            
            st.dataframe(df_summary, width='stretch')

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

                        # --- Botón de Análisis Pedagógico para el Profesor ---
                        st.markdown("---")
                        _ai_help = None if st.session_state.ai_available else "IA no disponible en este entorno demo"
                        if st.button("🧠 Generar Análisis Pedagógico con IA", key=f"ai_anal_{selected_student['id']}", width='stretch', disabled=not st.session_state.ai_available, help=_ai_help):
                            try:
                                with st.spinner("Analizando trayectoria del estudiante..."):
                                    analysis = st.session_state.teacher_service.generate_ai_analysis(
                                        selected_student['id'], global_elo
                                    )
                                    st.markdown(f"""
                                    <div class="elo-card" style="text-align: left; background: rgba(0, 201, 255, 0.05); border-color: rgba(0, 201, 255, 0.3);">
                                        <h4>📋 Análisis de la IA para el Docente</h4>
                                        <div style="font-size: 0.95rem; color: #e0e0e0;">
                                        {analysis}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
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

        # Cargar temas antes del sidebar para el selectbox
        bank_data = st.session_state.db.get_items_from_db()
        topics = list(set([i['topic'] for i in bank_data]))

        # Sidebar Estilizado
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
            st.write(f"### Hola, **{st.session_state.username}**")
            mode = st.radio("Modo", ["📝 Practicar", "📊 Estadísticas"], label_visibility="collapsed")
            st.caption("Navegación Principal")

            if mode == "📝 Practicar":
                st.markdown("### Configuración de Estudio")
                selected_topic = st.selectbox("¿Qué quieres estudiar hoy?", ["Todos"] + topics)

            st.markdown("---")
            st.caption("Configuración de IA")
            ai_mode = st.selectbox(
                "Modo de IA",
                ["Rápido (Flash)", "Profundo (Razonamiento)"],
                index=0 if st.session_state.ai_mode == "Rápido (Flash)" else 1,
                help="El modo rápido usa modelos ligeros para feedback instantáneo. El modo profundo usa razonamiento complejo pero es más lento."
            )

            # Si cambia el modo, actualizamos los inputs de texto con los defaults
            if ai_mode != st.session_state.ai_mode:
                st.session_state.ai_mode = ai_mode
                defaults = AI_DEFAULTS[ai_mode]
                st.session_state.model_cog = defaults['cognitive']
                st.session_state.model_analysis = defaults['analysis']
                st.session_state.student_service.cognitive_analyzer.model_name = defaults['cognitive']
                st.rerun()

            if st.session_state.role == 'admin':
                with st.expander("⚙️ ID de Modelos (LM Studio)"):
                    st.session_state.ai_url = st.text_input("URL de LM Studio", value=st.session_state.ai_url)
                    if st.button("🔄 Sincronizar con LM Studio"):
                        active_models = get_active_models(st.session_state.ai_url)
                        if active_models:
                            selected_model = active_models[0]
                            st.session_state.model_cog = selected_model
                            st.session_state.model_analysis = selected_model
                            st.session_state.student_service.cognitive_analyzer.model_name = selected_model
                            st.success(f"Detectado: {selected_model}")
                        else:
                            st.error("No se detectaron modelos activos. Verifica la URL e IP.")

                    new_cog = st.text_input("ID Análisis Cognitivo", value=st.session_state.model_cog, key="cog_model_input")
                    new_analysis = st.text_input("ID Recomendaciones", value=st.session_state.model_analysis, key="analysis_model_input")

                    if new_cog != st.session_state.model_cog or new_analysis != st.session_state.model_analysis:
                        st.session_state.model_cog = new_cog
                        st.session_state.model_analysis = new_analysis
                        st.session_state.student_service.cognitive_analyzer.model_name = new_cog
                        st.info("Configuración de modelos actualizada.")

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
        if mode == "📝 Practicar":
            if selected_topic == "Todos":
                current_elo_display = aggregate_global_elo(st.session_state.vector)
                current_rd_display = aggregate_global_rd(st.session_state.vector)
                topic_display_name = "Global"
            else:
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

                # Delegar obtención de pregunta al servicio
                item_data, status = st.session_state.student_service.get_next_question(
                    st.session_state.user_id, selected_topic, st.session_state.vector,
                    session_correct_ids=st.session_state.session_correct_ids,
                    session_wrong_timestamps=st.session_state.session_wrong_timestamps,
                    session_questions_count=st.session_state.session_questions_count,
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
                            reasoning = st.text_area("🧠 Justifica tu razonamiento (opcional para análisis IA):", 
                                                    placeholder="Explica brevemente por qué crees que esta es la respuesta...",
                                                    help="Tu explicación ayuda a la IA a entender si tu acierto fue seguro o si tu error fue conceptual.")
                            st.write("")
                            submit_button = st.button(label="📝 Enviar Respuesta", width='stretch')

                            if submit_button:
                                is_correct = (selected_option == item_data['correct_option'])
                                if is_correct:
                                    st.success("¡Respuesta correcta! Excelente análisis. 🎓")
                                else:
                                    st.error(f"Respuesta incorrecta. La opción correcta era: **{item_data['correct_option']}**")
                                
                                time.sleep(1.5)
                                handle_answer_topic(is_correct, item_data, reasoning=reasoning)

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
                                    ))
                            except (ConnectionError, TimeoutError):
                                st.info("IA no disponible en este momento. Inténtalo más tarde.")
                        elif 'options' not in item_data:
                            st.warning("Pregunta sin opciones configuradas.")

        elif mode == "📊 Estadísticas":
            st.title("📊 Estadísticas de Aprendizaje")

            history_full = st.session_state.db.get_user_history_full(st.session_state.user_id)
            attempts_data = st.session_state.db.get_attempts_for_ai(st.session_state.user_id, limit=1000)

            m1, m2, m3 = st.columns(3)
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
            st.write("Generando recomendaciones personalizadas basadas en tu desempeño reciente.")

            lm_studio_url_dash = st.text_input("Servidor de IA (URL)", value="http://192.168.40.66:1234/v1", key="lm_dash")

            _rec_help = None if st.session_state.ai_available else "IA no disponible en este entorno demo"
            if st.button("✨ Generar Recomendaciones de Estudio", disabled=not st.session_state.ai_available, help=_rec_help):
                try:
                    with st.spinner("Analizando patrones de aprendizaje..."):
                        recent_attempts = st.session_state.db.get_attempts_for_ai(st.session_state.user_id)
                        current_elo_val = aggregate_global_elo(st.session_state.vector)
                        
                        # Usar el modelo de análisis configurado
                        recommendations = analyze_performance_local(
                            recent_attempts, 
                            current_elo_val, 
                            base_url=lm_studio_url_dash,
                            model_name=st.session_state.model_analysis
                        )

                        if isinstance(recommendations, list) and len(recommendations) > 0:
                            for idx, rec in enumerate(recommendations):
                                with st.container(border=True):
                                    st.markdown(f"### 🎯 Recomendación #{idx+1}")
                                    if isinstance(rec, dict):
                                        st.markdown(f"**🔍 Diagnóstico:** {rec.get('diagnostico', 'N/A')}")
                                        st.success(f"**📝 Acción:** {rec.get('recomendación', 'N/A')}")
                                        st.info(f"**💡 Justificación:** {rec.get('justificación', 'N/A')}")
                                        st.markdown(f"**🔢 Meta Sugerida:** {rec.get('ejercicios', 0)} ejercicios")
                                    else:
                                        # Manejo de mensajes de error o formatos antiguos
                                        st.info(str(rec))
                        elif isinstance(recommendations, list) and len(recommendations) == 0:
                            st.warning("No hay suficientes datos para generar recomendaciones aún.")
                        else:
                            st.error(f"Respuesta inesperada de IA: {recommendations}")
                except (ConnectionError, TimeoutError):
                    st.info("IA no disponible en este momento. Inténtalo más tarde.")
                except Exception as e:
                    st.error(f"Error crítico en interfaz: {str(e)}")
