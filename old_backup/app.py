import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import random
from elo.vector_elo import VectorRating, aggregate_global_elo, aggregate_global_rd
from elo.model import expected_score, calculate_dynamic_k
from selector.item_selector import AdaptiveItemSelector
from elo.model import Item
from database import DatabaseManager
from ai_analysis import analyze_performance_local, get_active_models, get_socratic_guidance, get_pedagogical_analysis
from elo.cognitive import CognitiveAnalyzer
import time

# Configuración de página
st.set_page_config(page_title="ELO Learning — Evaluación Adaptativa", layout="wide", page_icon="🎓")

# Inicializar Base de Datos
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Inicializar Configuración de IA
if 'ai_mode' not in st.session_state:
    st.session_state.ai_mode = "Rápido (Flash)"

if 'model_cog' not in st.session_state:
    st.session_state.model_cog = "google/gemma-3-4b"

if 'model_analysis' not in st.session_state:
    st.session_state.model_analysis = "mistralai/mistral-7b-instruct-v0.3"

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

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = CognitiveAnalyzer(model_name=st.session_state.model_cog)

if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None

# Sincronizar banco de ítems con la DB al inicio
try:
    with open('items/bank.json', 'r', encoding='utf-8') as f:
        initial_bank = json.load(f)
        st.session_state.db.sync_items_from_json(initial_bank)
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
    h1, h2, h3 {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 201, 255, 0.3);
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
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
        all_my_students = st.session_state.db.get_students_by_teacher(st.session_state.user_id)
        
        if not all_my_students:
            st.info("Aún no tienes estudiantes vinculados a tus grupos.")
        else:
            my_groups = st.session_state.db.get_groups_by_teacher(st.session_state.user_id)
            group_filter_options = {"Todos mis grupos": None}
            group_filter_options.update({g['name']: g['id'] for g in my_groups})
            
            selected_group_name = st.selectbox("🎯 Filtrar por Grupo", list(group_filter_options.keys()))
            selected_group_id = group_filter_options[selected_group_name]

            if selected_group_id:
                students = st.session_state.db.get_students_by_group(selected_group_id, st.session_state.user_id)
            else:
                students = all_my_students

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

            attempts = st.session_state.db.get_student_attempts_detail(selected_student['id'])

            if not attempts:
                st.info(f"{selected_name} aún no ha respondido ninguna pregunta.")
            else:
                df = pd.DataFrame(attempts)
                df['intento'] = range(1, len(df) + 1)
                df['resultado'] = df['is_correct'].map({1: '✅ Correcto', 0: '❌ Incorrecto', True: '✅ Correcto', False: '❌ Incorrecto'})

                tab_elo, tab_prob, tab_tabla = st.tabs(["📈 Progreso ELO", "🎯 Prob. de Fallo", "📄 Tabla de Intentos"])

                with tab_elo:
                    st.markdown(f"**Evolución del ELO de {selected_name} por tema**")
                    fig_elo, ax_elo = plt.subplots(figsize=(10, 5))
                    fig_elo.patch.set_alpha(0)
                    ax_elo.set_facecolor('#1E1E1E')
                    for topic in df['topic'].unique():
                        td = df[df['topic'] == topic]
                        ax_elo.plot(td['intento'], td['elo_after'], marker='o', label=topic, linewidth=2)
                    ax_elo.set_ylabel("ELO", color="white")
                    ax_elo.set_xlabel("Intento #", color="white")
                    ax_elo.tick_params(colors='white')
                    ax_elo.grid(True, linestyle=':', alpha=0.3, color='gray')
                    for spine in ax_elo.spines.values():
                        spine.set_color('#444')
                    legend = ax_elo.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
                    legend.get_frame().set_facecolor('#262730')
                    legend.get_frame().set_edgecolor('gray')
                    for text in legend.get_texts():
                        text.set_color("white")
                    plt.tight_layout()
                    st.pyplot(fig_elo)

                    # --- Botón de Análisis Pedagógico para el Profesor ---
                    st.markdown("---")
                    if st.button("🧠 Generar Análisis Pedagógico con IA", key=f"ai_anal_{selected_student['id']}", width='stretch'):
                        with st.spinner("Analizando trayectoria del estudiante..."):
                            # Preparar datos para el análisis
                            incorrect_topics = [a['topic'] for a in attempts if not a['is_correct']]
                            topics_unique = list(set([a['topic'] for a in attempts]))
                            recent_attempts = attempts[-10:]
                            recent_acc = sum(1 for a in recent_attempts if a['is_correct']) / len(recent_attempts) if recent_attempts else 0
                            
                            student_data = {
                                "elo_global": global_elo,
                                "attempts_count": len(attempts),
                                "topics": topics_unique,
                                "recent_accuracy": recent_acc
                            }
                            
                            analysis = get_pedagogical_analysis(
                                student_data, 
                                model_name=st.session_state.model_analysis
                            )
                            st.markdown(f"""
                            <div class="elo-card" style="text-align: left; background: rgba(0, 201, 255, 0.05); border-color: rgba(0, 201, 255, 0.3);">
                                <h4>📋 Análisis de la IA para el Docente</h4>
                                <div style="font-size: 0.95rem; color: #e0e0e0;">
                                {analysis}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                with tab_prob:
                    st.markdown(f"**Probabilidad de acierto de {selected_name} en cada pregunta**")
                    st.caption("Calculada con el ELO del estudiante **antes** del intento. Barras verdes = el sistema esperaba que acertara. Barras rojas = la pregunta era demasiado difícil para su nivel.")

                    df_prob = df.dropna(subset=['prob_failure']).copy()

                    if df_prob.empty:
                        st.info("Cargando datos... (recarga la página si persiste el mensaje)")
                    else:
                        df_prob['prob_success'] = 1.0 - df_prob['prob_failure']

                        fig_prob, ax_prob = plt.subplots(figsize=(10, 5))
                        fig_prob.patch.set_alpha(0)
                        ax_prob.set_facecolor('#1E1E1E')

                        colors = ['#28a745' if ps >= 0.5 else '#dc3545' for ps in df_prob['prob_success']]
                        ax_prob.bar(df_prob['intento'], df_prob['prob_success'], color=colors, alpha=0.85)
                        ax_prob.axhline(0.5, color='#ffc107', linestyle='--', linewidth=1.5, label='Umbral 50%')

                        ax_prob.set_ylabel("Prob. de Acierto", color="white")
                        ax_prob.set_xlabel("Intento #", color="white")
                        ax_prob.set_ylim(0, 1)
                        ax_prob.tick_params(colors='white')
                        ax_prob.grid(True, axis='y', linestyle=':', alpha=0.3, color='gray')
                        for spine in ax_prob.spines.values():
                            spine.set_color('#444')
                        legend_p = ax_prob.legend(frameon=True)
                        legend_p.get_frame().set_facecolor('#262730')
                        legend_p.get_frame().set_edgecolor('gray')
                        for text in legend_p.get_texts():
                            text.set_color("white")
                        plt.tight_layout()
                        st.pyplot(fig_prob)

                        # Métricas rápidas
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Prob. Acierto Promedio", f"{df_prob['prob_success'].mean():.1%}")
                        m2.metric("Acierto más alto", f"{df_prob['prob_success'].max():.1%}")
                        m3.metric("Preguntas retadoras (<50%)", int((df_prob['prob_success'] < 0.5).sum()))

                with tab_tabla:
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

        # Sidebar Estilizado
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
            st.write(f"### Hola, **{st.session_state.username}**")
            mode = st.radio("Modo", ["📝 Practicar", "📊 Estadísticas"], label_visibility="collapsed")
            st.caption("Navegación Principal")
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
                st.session_state.analyzer = CognitiveAnalyzer(model_name=st.session_state.model_cog)
                st.rerun()

            with st.expander("⚙️ ID de Modelos (LM Studio)"):
                if st.button("🔄 Sincronizar con LM Studio"):
                    active_models = get_active_models(st.session_state.get('lm_url', "http://localhost:1234/v1"))
                    if active_models:
                        selected_model = active_models[0]
                        st.session_state.model_cog = selected_model
                        st.session_state.model_analysis = selected_model
                        st.session_state.analyzer = CognitiveAnalyzer(model_name=selected_model)
                        st.success(f"Detectado: {selected_model}")
                    else:
                        st.error("No se detectaron modelos activos. Verifica la URL e IP.")

                new_cog = st.text_input("ID Análisis Cognitivo", value=st.session_state.model_cog, key="cog_model_input")
                new_analysis = st.text_input("ID Recomendaciones", value=st.session_state.model_analysis, key="analysis_model_input")
                
                if new_cog != st.session_state.model_cog or new_analysis != st.session_state.model_analysis:
                    st.session_state.model_cog = new_cog
                    st.session_state.model_analysis = new_analysis
                    st.session_state.analyzer = CognitiveAnalyzer(model_name=new_cog)
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
            
            cognition = st.session_state.analyzer.analyze_cognition(reasoning, is_correct, time_taken)
            impact_mod = cognition['impact_modifier']

            # Calcular métricas ANTES de actualizar el ELO
            current_elo = st.session_state.vector.get(item_data['topic'])
            p_success = expected_score(current_elo, item_data['difficulty'])
            prob_failure = 1.0 - p_success

            # --- Cálculo de Factor K Dinámico ---
            attempts_count = st.session_state.db.get_total_attempts_count(st.session_state.user_id)
            latest_history = st.session_state.db.get_latest_attempts(st.session_state.user_id, limit=20)
            recent_results = [(h['actual'], h['expected']) for h in latest_history]
            
            k_val = calculate_dynamic_k(attempts_count, current_elo, recent_results)

            # Actualizar Rating con Modificador Cognitivo (Incertidumbre gestionada internamente)
            new_r, new_rd = st.session_state.vector.update(
                item_data['topic'], 
                item_data['difficulty'], 
                1.0 if is_correct else 0.0, 
                impact_modifier=impact_mod
            )

            # --- Actualización Simétrica del Ítem (Dificultad Dinámica) ---
            st.session_state.db.update_item_rating(
                item_data['id'],
                current_elo,
                1.0 if is_correct else 0.0
            )

            # Guardar en BD con todas las métricas nuevas incluyendo RD
            st.session_state.db.save_attempt(
                st.session_state.user_id,
                item_data['id'],
                is_correct,
                item_data['difficulty'],
                item_data['topic'],
                new_r,
                prob_failure,
                p_success,
                time_taken=time_taken,
                confidence_score=cognition['confidence_score'],
                error_type=cognition['error_type'],
                rating_deviation=new_rd
            )
            # Resetear timer para la próxima pregunta
            st.session_state.question_start_time = None
            st.rerun()

        # --- VISTAS ---
        if mode == "📝 Practicar":
            # Cargar ítems desde la base de datos para usar dificultad dinámica
            bank_data = st.session_state.db.get_items_from_db()
            topics = list(set([i['topic'] for i in bank_data]))

            st.sidebar.markdown("### Configuración de Estudio")
            selected_topic = st.sidebar.selectbox("¿Qué quieres estudiar hoy?", ["Todos"] + topics)

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

                if selected_topic != "Todos":
                    topic_pool = [i for i in bank_data if i['topic'] == selected_topic]
                else:
                    topic_pool = bank_data

                answered_ids = st.session_state.db.get_answered_item_ids(st.session_state.user_id)
                filtered_items = [i for i in topic_pool if i['id'] not in answered_ids]

                if not filtered_items:
                    # Bug 2: Reiniciar pool si el ELO no es el máximo (1800)
                    if current_elo_display < 1800:
                        st.info("🔄 Se ha completado el banco de preguntas. Reiniciando para continuar con tu proceso de aprendizaje.")
                        filtered_items = topic_pool
                    else:
                        st.success("🎉 ¡Excelente trabajo! Has alcanzado el nivel de excelencia en esta materia.")
                        st.balloons()
                        filtered_items = [] # Mantener vacío para que no cargue más

                if filtered_items:
                    selector = AdaptiveItemSelector()
                    items_objs = [Item(difficulty=i['difficulty']) for i in filtered_items]
                    
                    # El nuevo selector probabilístico no necesita que bajemos el ELO manualmente
                    # ya que busca el rango de probabilidad óptimo (0.4 a 0.75).
                    target_item_obj = selector.select_optimal_item(current_elo_display, items_objs)
                    
                    if target_item_obj:
                        item_data = next(i for i in filtered_items if i['difficulty'] == target_item_obj.difficulty)
                    else:
                        item_data = random.choice(filtered_items) if filtered_items else None

                    # Iniciar cronómetro si es una nueva pregunta
                    if st.session_state.question_start_time is None:
                        st.session_state.question_start_time = time.time()

                    with st.container(border=True):
                        diff_color = "#28a745" if item_data['difficulty'] < 1000 else "#ffc107" if item_data['difficulty'] < 1400 else "#dc3545"
                        st.markdown(f"**Tema:** {item_data['topic']} <span style='background-color: {diff_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; margin-left: 10px;'>⚡ Dificultad {item_data['difficulty']}</span>", unsafe_allow_html=True)
                        st.markdown(f"### {item_data['content']}")
                        st.write("")

                        if 'options' in item_data:
                            # Bug 3: Aleatorizar opciones
                            shuffled_options = item_data['options'].copy()
                            random.Random(item_data['id']).shuffle(shuffled_options)
                            
                            with st.form(key=f"form_{item_data['id']}"):
                                selected_option = st.radio("Selecciona tu respuesta:", shuffled_options, key=f"radio_{item_data['id']}")
                                reasoning = st.text_area("🧠 Justifica tu razonamiento (opcional para análisis IA):", 
                                                        placeholder="Explica brevemente por qué crees que esta es la respuesta...",
                                                        help="Tu explicación ayuda a la IA a entender si tu acierto fue seguro o si tu error fue conceptual.")
                                st.write("")
                                submit_button = st.form_submit_button(label="📝 Enviar Respuesta")

                            if submit_button:
                                is_correct = (selected_option == item_data['correct_option'])
                                if is_correct:
                                    st.success("¡Respuesta correcta! Excelente análisis. 🎓")
                                else:
                                    st.error(f"Respuesta incorrecta. La opción correcta era: **{item_data['correct_option']}**")
                                
                                time.sleep(1.5)
                                handle_answer_topic(is_correct, item_data, reasoning=reasoning)

                        # --- Ayuda Socrática si falló la última vez ---
                        if not st.session_state.get('last_was_correct', True):
                            st.info("💡 ¿Te gustaría una pista para la próxima? No te daré la respuesta, pero te ayudaré a pensar.")
                            if st.button("🙋 Pedir Ayuda Socrática", key=f"socratic_{item_data['id']}"):
                                with st.spinner("El tutor socrático está pensando una pregunta para ti..."):
                                    # Obtener la última respuesta del usuario (si está en session_state o aproximar)
                                    last_ans = st.session_state.get(f"radio_{item_data['id']}", "Respuesta previa")
                                    guidance = get_socratic_guidance(
                                        current_elo_display, 
                                        item_data['topic'], 
                                        item_data['content'], 
                                        last_ans,
                                        model_name=st.session_state.model_cog
                                    )
                                    st.markdown(f"""
                                    <div style="padding: 15px; border-radius: 10px; background: #262730; border-left: 5px solid #FFC107; margin-top: 10px;">
                                        <strong>🎓 Tutor Socrático:</strong><br>{guidance}
                                    </div>
                                    """, unsafe_allow_html=True)
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

                    fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
                    fig_bar.patch.set_alpha(0)
                    ax_bar.set_facecolor('#1E1E1E')
                    
                    # Graficar barras
                    bars = ax_bar.bar(df_elo['Tema'], df_elo['ELO'], color='#00C9FF', alpha=0.8)
                    
                    # Añadir error bars (RD) si se desea, o solo el texto
                    ax_bar.errorbar(df_elo['Tema'], df_elo['ELO'], yerr=df_elo['RD'], fmt='none', ecolor='#FFC107', capsize=5, alpha=0.6)
                    ax_bar.set_ylabel("ELO", color="white")
                    ax_bar.set_xlabel("Materia", color="white")
                    ax_bar.tick_params(axis='x', colors='white', rotation=45)
                    ax_bar.tick_params(axis='y', colors='white')
                    ax_bar.set_ylim(bottom=max(0, min(elos_list) - 50))
                    ax_bar.grid(True, axis='y', linestyle=':', alpha=0.3, color='gray')
                    for spine in ax_bar.spines.values():
                        spine.set_color('#444')
                    st.pyplot(fig_bar)
                except Exception as e:
                    st.error(f"Error visualizando gráfica: {str(e)}")
            else:
                st.info("Completa ejercicios para visualizar tu perfil de fortalezas.")

            st.subheader("📈 Progreso Académico")
            if history_full:
                df_hist = pd.DataFrame(history_full)
                df_hist['intento'] = range(1, len(df_hist) + 1)
                fig, ax = plt.subplots(figsize=(10, 5))
                fig.patch.set_alpha(0)
                ax.set_facecolor('#1E1E1E')
                for topic in df_hist['topic'].unique():
                    topic_data = df_hist[df_hist['topic'] == topic]
                    ax.plot(topic_data['intento'], topic_data['elo'], marker='o', label=topic, linewidth=2)
                ax.set_ylabel("Nivel ELO", color="white")
                ax.set_xlabel("Secuencia de Ejercicios", color="white")
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                legend = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
                legend.get_frame().set_facecolor('#262730')
                legend.get_frame().set_edgecolor('gray')
                for text in legend.get_texts():
                    text.set_color("white")
                ax.grid(True, linestyle=':', alpha=0.3, color='gray')
                for spine in ax.spines.values():
                    spine.set_color('#444')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.write("Sin datos históricos.")

            st.markdown("---")
            st.subheader("🧠 Asistente Virtual Inteligente")
            st.write("Generando recomendaciones personalizadas basadas en tu desempeño reciente.")

            lm_studio_url_dash = st.text_input("Servidor de IA (URL)", value="http://localhost:1234/v1", key="lm_dash")

            if st.button("✨ Generar Recomendaciones de Estudio"):
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
                except Exception as e:
                    st.error(f"Error crítico en interfaz: {str(e)}")
