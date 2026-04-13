"""
src/interface/streamlit/views/auth_view.py
==========================================
Vista de autenticación: login, registro wizard y logout.
Código movido exactamente desde app.py líneas 474-666.
"""

import streamlit as st
from src.interface.streamlit.assets import _get_logo
from src.interface.streamlit.state import login, logout


def render_auth(cookie_manager):
    """
    Renderiza la vista de login/registro.
    Recibe cookie_manager del app.py para manejar tokens de sesión.
    """
    repo = st.session_state.db

    # ── Estado del wizard de registro ────────────────────────────────────────
    if "reg_step" not in st.session_state:
        st.session_state.reg_step = 1
    if "reg_chosen_role" not in st.session_state:
        st.session_state.reg_chosen_role = None

    _logo_col1, _logo_col2, _logo_col3 = st.columns([1, 2, 1])
    with _logo_col2:
        st.image(_get_logo(), use_container_width=True)
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    col_info, col_login = st.columns([1.4, 1])

    with col_info:
        st.markdown(
            """
        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>📌 ¿Qué es LevelUp ELO?</h3>
            <p>LevelUp ELO es una plataforma académica de evaluación adaptativa que utiliza el <b>sistema de calificación ELO</b> —originalmente diseñado para el ajedrez— para medir con precisión el nivel de dominio de cada estudiante en distintas materias.</p>
            <p style="margin-top:10px;">A diferencia de los exámenes tradicionales, el sistema se adapta continuamente: <b>la dificultad de cada ejercicio se ajusta en tiempo real</b> según el rendimiento del estudiante, maximizando el aprendizaje efectivo.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("⚙️ ¿Cómo funciona?"):
            st.markdown(
                """
            <ul style="margin-top: 6px; line-height: 2; color:#e0e0e0;">
                <li><b>Puntuación ELO por materia:</b> Cada estudiante tiene un índice numérico por área temática que sube o baja según sus respuestas correctas e incorrectas.</li>
                <li><b>Selección adaptativa de ejercicios:</b> El sistema elige automáticamente preguntas en la <em>zona de desarrollo óptimo</em> del estudiante, ni demasiado fáciles ni inalcanzables.</li>
                <li><b>Seguimiento del progreso:</b> Los profesores consultan la evolución de cada estudiante por tema, con métricas de probabilidad de acierto por ejercicio.</li>
                <li><b>Recomendaciones con IA:</b> Un asistente inteligente analiza el historial y genera recomendaciones de estudio personalizadas.</li>
            </ul>
            """,
                unsafe_allow_html=True,
            )

        with st.expander("👥 Roles en la plataforma"):
            st.markdown(
                """
            <ul style="margin-top: 6px; line-height: 2; color:#e0e0e0;">
                <li><b>🎓 Estudiante:</b> Accede a ejercicios adaptativos y consulta sus estadísticas de progreso.</li>
                <li><b>🏫 Profesor:</b> Visualiza el rendimiento de sus estudiantes con métricas detalladas por tema.
                    <span style='color:#f0ad4e;'> Requiere aprobación del administrador.</span></li>
                <li><b>🛡️ Administrador:</b> Gestiona las cuentas de profesores y estudiantes en la plataforma.</li>
            </ul>
            """,
                unsafe_allow_html=True,
            )

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
                        if role == "teacher" and not approved:
                            st.warning(
                                "⏳ Tu cuenta de profesor está pendiente de aprobación por el administrador."
                            )
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
                            if st.button(
                                "Soy Estudiante",
                                use_container_width=True,
                                type="primary",
                                key="wizard_student",
                            ):
                                st.session_state.reg_chosen_role = "Estudiante"
                                st.session_state.reg_step = 2
                                st.rerun()
                    with _wiz_p:
                        with st.container(border=True):
                            st.markdown("**🏫 Profesor**")
                            st.caption("Gestiona grupos y monitorea alumnos.")
                            if st.button(
                                "Soy Profesor", use_container_width=True, key="wizard_teacher"
                            ):
                                st.session_state.reg_chosen_role = "Profesor"
                                st.session_state.reg_step = 2
                                st.rerun()

                # ── Wizard paso 2: datos de la cuenta ────────────────────────
                elif st.session_state.reg_step == 2:
                    _role_icon = "🎓" if st.session_state.reg_chosen_role == "Estudiante" else "🏫"
                    _role_lbl = st.session_state.reg_chosen_role
                    st.markdown(f"**{_role_icon} Registro como {_role_lbl}**")

                    if st.session_state.reg_chosen_role == "Profesor":
                        st.warning(
                            "⏳ Las cuentas de profesor requieren aprobación del administrador antes de poder acceder."
                        )

                    if st.button("← Cambiar tipo de cuenta", key="wizard_back"):
                        st.session_state.reg_step = 1
                        st.rerun()

                    new_user = st.text_input("Nombre de usuario", key="reg_user")
                    st.caption(
                        "Solo letras, números y guion bajo. Sin espacios ni tildes. Ej: juan_perez"
                    )

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
                            help="Determina qué catálogo de cursos verás.",
                        )
                        st.caption(
                            "* Campo obligatorio — debes seleccionar tu nivel educativo para continuar."
                        )
                        education_level = (
                            None
                            if level_label is None
                            else (
                                "semillero"
                                if level_label == "Semillero de Matemáticas"
                                else level_label.lower()
                            )
                        )
                        if education_level == "semillero":
                            grade_label = st.selectbox(
                                "Grado",
                                ["6°", "7°", "8°", "9°", "10°", "11°"],
                                key="reg_grade",
                                help="Grado escolar (6° a 11° bachillerato).",
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
                        elif chosen_role == "student" and not education_level:
                            st.error("Debes seleccionar tu nivel educativo.")
                        else:
                            success, message = st.session_state.db.register_user(
                                new_user,
                                new_pass,
                                chosen_role,
                                education_level=education_level,
                                grade=grade,
                            )
                            if success:
                                if chosen_role == "teacher":
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

    st.markdown(
        """
        <p style='text-align:center; color:#666; font-size:0.78rem; margin-top:18px;'>
            ¿Problemas para acceder? Contacta a tu administrador.
        </p>
    """,
        unsafe_allow_html=True,
    )
