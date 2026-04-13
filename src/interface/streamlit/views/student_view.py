"""
src/interface/streamlit/views/student_view.py
=============================================
Vista del panel del estudiante.
Código movido exactamente desde app.py líneas 1875-3701.
"""

import os
import time
import random
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import src.infrastructure.external_api.ai_client as ai_mod
import src.infrastructure.external_api.math_procedure_review as _math_review_mod
import src.infrastructure.external_api.model_router as _router_mod
import src.infrastructure.external_api.math_analysis_pipeline as _pipeline_mod

from src.domain.elo.vector_elo import VectorRating, aggregate_global_elo, aggregate_global_rd
from src.domain.elo.model import expected_score, calculate_dynamic_k, Item
from src.domain.entities import LEVEL_TO_BLOCK
from src.domain.katia.katia_messages import (
    get_random_message,
    get_streak_message,
    get_procedure_comment,
    MENSAJES_BIENVENIDA,
    MENSAJES_DESPEDIDA,
)
from src.utils import strip_thinking_tags
from src.infrastructure.logging_config import get_logger

from src.interface.streamlit.assets import (
    BASE_PATH as base_path,
    _get_logo,
    load_katia_avatar_bytes,
    load_katia_gif_html,
    _get_banner_b64,
)
from src.interface.streamlit.state import cached, invalidate_cache, get_rank, logout
from src.interface.streamlit.components.timers import _render_live_timer

# Funciones de IA extraídas de módulos
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

_app_logger = get_logger(__name__)


def render_student():
    """Punto de entrada del panel del estudiante."""
    repo = st.session_state.db

    # Assets cargados una sola vez (cache_resource)
    _KATIA_IMG = load_katia_avatar_bytes()
    _KATIA_GIF_CORRECTO_HTML = load_katia_gif_html("correcto")
    _KATIA_GIF_ERRORES_HTML = load_katia_gif_html("errores")

    # 1. Recuperar Estado Inicial de DB para VectorELO
    if "vector_initialized" not in st.session_state:
        latest_elos = cached(
            "cache_elo_by_topic",
            lambda: st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id),
        )
        st.session_state.vector = VectorRating()
        for topic, (elo, rd) in latest_elos.items():
            st.session_state.vector.ratings[topic] = (elo, rd)
        st.session_state.vector_initialized = True

    if "session_correct_ids" not in st.session_state:
        st.session_state.session_correct_ids = set()
    if "session_wrong_timestamps" not in st.session_state:
        st.session_state.session_wrong_timestamps = {}
    if "session_questions_count" not in st.session_state:
        st.session_state.session_questions_count = 0
    if "streak_correct" not in st.session_state:
        st.session_state.streak_correct = 0

    # ── Saludo de KatIA al iniciar sesión (una sola vez) ─────────────────
    if not st.session_state.get("katia_greeted") and _KATIA_IMG:
        st.session_state.katia_greeted = True
        st.toast(get_random_message(MENSAJES_BIENVENIDA), icon="🐱")

    # ── Onboarding: nivel educativo ──────────────────────────────────────
    if "education_level" not in st.session_state:
        st.session_state.education_level = cached(
            "cache_edu_level", lambda: repo.get_education_level(st.session_state.user_id)
        )

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
                if st.button("Soy universitario", width="stretch", type="primary", key="onb_uni"):
                    repo.set_education_level(st.session_state.user_id, "universidad")
                    st.session_state.education_level = "universidad"
                    st.rerun()
        with col_col:
            with st.container(border=True):
                st.markdown("#### 🏫 Colegio")
                st.write("Álgebra Básica, Aritmética, Trigonometría, Geometría")
                st.write("")
                if st.button("Soy de colegio", width="stretch", key="onb_col"):
                    repo.set_education_level(st.session_state.user_id, "colegio")
                    st.session_state.education_level = "colegio"
                    st.rerun()
        with col_con:
            with st.container(border=True):
                st.markdown("#### 🏆 Concursos")
                st.write("Preparación para concursos públicos: DIAN, SENA y más")
                st.write("")
                if st.button("Preparo concursos", width="stretch", key="onb_con"):
                    repo.set_education_level(st.session_state.user_id, "concursos")
                    st.session_state.education_level = "concursos"
                    st.rerun()
        st.stop()

    # Cargar cursos matriculados filtrados por nivel educativo del estudiante.
    _level = st.session_state.education_level or "universidad"
    if _level == "semillero":
        _sem_grade_blk = st.session_state.get("student_grade") or repo.get_grade(
            st.session_state.user_id
        )
        st.session_state["student_grade"] = _sem_grade_blk
        _student_block = f"Semillero {_sem_grade_blk}°" if _sem_grade_blk else "Semillero"
    else:
        _student_block = LEVEL_TO_BLOCK.get(_level, "Universidad")
    _enrolled = [
        c
        for c in cached(
            "cache_enrollments", lambda: repo.get_user_enrollments(st.session_state.user_id)
        )
        if c.get("block") == _student_block  # nivel propio
        or (
            c.get("block") != _student_block and c.get("group_id") is not None
        )  # acceso especial vía código
    ]

    # ── Banner "sin grupo asignado" ──────────────────────────────────────
    _all_enroll = cached(
        "cache_all_enrollments", lambda: repo.get_user_enrollments(st.session_state.user_id)
    )
    _has_group = any(e.get("group_id") for e in _all_enroll)
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
    if "fb_seen_ids" not in st.session_state:
        st.session_state.fb_seen_ids = set()

    # T4b: calcular cuántas retroalimentaciones nuevas hay (revisadas - vistas)
    _reviewed_ids = cached(
        "cache_reviewed_ids", lambda: repo.get_reviewed_submission_ids(st.session_state.user_id)
    )
    _unseen_fb = _reviewed_ids - st.session_state.fb_seen_ids
    _fb_badge = f" 🆕 {len(_unseen_fb)}" if _unseen_fb else ""

    # Sidebar Estilizado
    with st.sidebar:
        st.image(_get_logo(), width=180)
        st.write(f"### Hola, **{st.session_state.username}**")
        # ── Temporizador de sesión (tiempo real) ──────────────────────────
        _sess_start = st.session_state.get("session_start_time")
        if _sess_start:
            _render_live_timer(
                _sess_start,
                label="⏱️ Sesión: ",
                font_size="0.85rem",
                height=30,
                color="#aaa",
                bold=False,
            )
        _mode_options = [
            "📝 Practicar",
            "📊 Estadísticas",
            "🎓 Mis Cursos",
            f"💬 Feedback{_fb_badge}",
        ]
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
            if _enrolled and "selected_course" in st.session_state:
                _sc = st.session_state.selected_course
                st.markdown(f"### 📚 {_sc['name']}")
                if st.button("↩ Cambiar materia", key="sidebar_change_course"):
                    del st.session_state.selected_course
                    st.session_state.question_start_time = None
                    st.session_state.pop("katia_chat_history", None)
                    st.rerun()

        st.markdown("---")
        # ── Badge de estado de IA (siempre visible) ───────────────────────
        _badge_p = st.session_state.get("ai_provider")
        _badge_ok = st.session_state.get("ai_available", False)
        if not _badge_ok or not _badge_p:
            st.markdown("⚠️ **Sin backend de IA**")
        elif _badge_p == "lmstudio":
            st.markdown("🟢 **Local Conectada**")
        else:
            _badge_label = ai_mod.PROVIDERS.get(_badge_p, {}).get("label", _badge_p)
            _badge_name = _badge_label.split(" ", 1)[-1] if _badge_label else _badge_p
            st.markdown(f"🔵 **{_badge_name} Activo**")
        with st.expander("⚙️ Configuración de IA"):
            st.caption("🔧 **Proveedor de IA**")
            _s_mode = st.radio(
                "Modo IA",
                ["🤖 Auto", "☁️ API Key", "🖥️ Local"],
                index=["auto", "cloud", "local"].index(
                    st.session_state.get("ai_provider_mode", "auto")
                ),
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
                    for _k in ("ai_available", "lmstudio_models"):
                        st.session_state.pop(_k, None)
                    st.rerun()
            elif _s_mode == "☁️ API Key":
                _env_key = os.getenv("GROQ_API_KEY")
                if _env_key:
                    # Remoto (Streamlit Cloud): key disponible en entorno, no mostrar input
                    if st.session_state.cloud_api_key != _env_key:
                        st.session_state.cloud_api_key = _env_key
                        _detected_st = ai_mod.detect_provider_from_key(_env_key)
                        st.session_state.ai_provider = _detected_st or "groq"
                        _pinfo_st = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {})
                        st.session_state.model_cog = (
                            _pinfo_st.get("model_cog") or st.session_state.model_cog
                        )
                        st.session_state.model_analysis = (
                            _pinfo_st.get("model_analysis") or st.session_state.model_analysis
                        )
                        st.session_state.student_service.cognitive_analyzer.model_name = (
                            st.session_state.model_cog
                        )
                        st.session_state.ai_available = True
                    _plabel_st = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {}).get(
                        "label", st.session_state.ai_provider
                    )
                    st.caption(f"🔒 Modelo activo: **{_plabel_st}**")
                else:
                    # Local: el usuario ingresa la key manualmente
                    _key_in_st = st.text_input(
                        "API Key",
                        type="password",
                        value="",
                        placeholder="sk-ant-… / gsk_… / sk-… / AIzaSy…",
                        key="cloud_key_st",
                    )
                    st.caption(
                        "🔒 Tus credenciales son seguras y no se almacenan en ninguna base de datos."
                    )
                    if _key_in_st:
                        _detected_st = ai_mod.detect_provider_from_key(_key_in_st)
                        st.session_state.cloud_api_key = _key_in_st
                        st.session_state.ai_provider = _detected_st or "groq"
                        _pinfo_st = ai_mod.PROVIDERS.get(st.session_state.ai_provider, {})
                        st.session_state.model_cog = (
                            _pinfo_st.get("model_cog") or st.session_state.model_cog
                        )
                        st.session_state.model_analysis = (
                            _pinfo_st.get("model_analysis") or st.session_state.model_analysis
                        )
                        st.session_state.student_service.cognitive_analyzer.model_name = (
                            st.session_state.model_cog
                        )
                        st.session_state.ai_available = True
                        _plabel_st = _pinfo_st.get("label", st.session_state.ai_provider)
                        st.success(f"{_plabel_st} detectado")
                    else:
                        st.caption("Soporta: Groq, OpenAI, Anthropic, Gemini, HuggingFace")
            elif _s_mode == "🖥️ Local":
                _local_url_st = st.text_input(
                    "URL servidor local", value=st.session_state.ai_url, key="lm_url_st"
                )
                st.session_state.ai_url = _local_url_st
                if st.button("🔍 Detectar modelos", key="btn_detect_lm"):
                    _det = ai_mod.detect_lmstudio(st.session_state.ai_url)
                    st.session_state.lmstudio_models = _det["models"]
                    if _det["available"]:
                        st.session_state.ai_available = True
                        st.session_state.ai_provider = "lmstudio"
                        st.session_state.cloud_api_key = None
                        _math_best = ai_mod.select_best_math_model(
                            _det["models"],
                            provider="ollama",
                        )
                        _best = _math_best or ai_mod.select_best_model(_det["models"])
                        if _best:
                            st.session_state.model_cog = _best
                            st.session_state.model_analysis = _best
                            st.session_state.student_service.cognitive_analyzer.model_name = _best
                        st.rerun()
                    else:
                        st.error("Servidor no detectado en esa URL")
                _models = st.session_state.get("lmstudio_models", [])
                if _models:
                    _sel_idx = (
                        _models.index(st.session_state.model_cog)
                        if st.session_state.model_cog in _models
                        else 0
                    )
                    _sel = st.selectbox(
                        "Modelo activo", _models, index=_sel_idx, key="lm_model_sel"
                    )
                    if _sel != st.session_state.model_cog:
                        st.session_state.model_cog = _sel
                        st.session_state.model_analysis = _sel
                        st.session_state.student_service.cognitive_analyzer.model_name = _sel
                    st.session_state.ai_available = True
                    st.session_state.ai_provider = "lmstudio"
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
                    st.session_state.pop("problem_report_desc", None)
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
        st.session_state["last_was_correct"] = is_correct

        # --- Cálculo de Modificadores Cognitivos ---
        time_taken = 0.0
        if st.session_state.question_start_time:
            time_taken = time.time() - st.session_state.question_start_time

        # Configurar el servicio con los parámetros de IA de la sesión
        if st.session_state.student_service.cognitive_analyzer is not None:
            st.session_state.student_service.cognitive_analyzer.base_url = st.session_state.ai_url
            st.session_state.student_service.cognitive_analyzer.model_name = (
                st.session_state.model_cog
            )

        # Delegar procesamiento al servicio.
        _elo_topic = st.session_state.selected_course["name"]
        is_correct, cog_data = st.session_state.student_service.process_answer(
            st.session_state.user_id,
            item_data,
            st.session_state.get(f"answer_text_{item_data['id']}"),
            reasoning,
            time_taken,
            st.session_state.vector,
            elo_topic=_elo_topic,
        )

        st.session_state.session_questions_count += 1
        if is_correct:
            st.session_state.session_correct_ids.add(item_data["id"])
        else:
            st.session_state.session_wrong_timestamps[item_data["id"]] = float(
                st.session_state.session_questions_count
            )

        # Invalidar caches afectados por save_attempt
        invalidate_cache(
            "cache_answered_ids",
            "cache_elo_by_topic",
            "cache_streak",
            f"cache_streak_{selected_course_id}",
            "cache_weekly_ranking",
            "cache_course_ranking",
            "cache_teachers_groups",
        )

        st.session_state.question_start_time = None
        st.session_state.show_result = True
        st.session_state.last_result_correct = is_correct
        st.session_state.last_result_item = item_data
        st.rerun()

    # --- VISTAS ---
    # ── Pantalla de bienvenida (primer acceso sin matrículas) ───────────
    if not _enrolled and not st.session_state.get("welcome_dismissed"):
        st.markdown(
            """
            <div style='text-align:center; padding:2rem 1rem;'>
                <div style='font-size:4rem;'>🎓</div>
                <h1 style='font-size:2rem; margin:0.5rem 0;'>¡Bienvenido a LevelUp-ELO!</h1>
                <p style='color:#aaa; font-size:1rem; max-width:600px; margin:0.5rem auto;'>
                    La plataforma que adapta cada pregunta a tu nivel usando el sistema de rating ELO
                    — el mismo del ajedrez competitivo. Cuanto más practiques, más preciso se vuelve.
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        _wc1, _wc2, _wc3 = st.columns(3)
        with _wc1:
            st.markdown(
                """
                <div style='background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;'>
                    <div style='font-size:2rem;'>📚</div>
                    <b>1. Elige tu profesor</b>
                    <p style='color:#aaa; font-size:0.85rem; margin-top:0.5rem;'>
                        Ve a <b>Mis Cursos</b> y explora los profesores disponibles para tu nivel.
                        Elige el que prefieras para cada materia.
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with _wc2:
            st.markdown(
                """
                <div style='background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;'>
                    <div style='font-size:2rem;'>⚡</div>
                    <b>2. Practica a tu ritmo</b>
                    <p style='color:#aaa; font-size:0.85rem; margin-top:0.5rem;'>
                        El sistema selecciona preguntas en tu zona de desarrollo óptimo:
                        ni muy fáciles ni imposibles.
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with _wc3:
            st.markdown(
                """
                <div style='background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;'>
                    <div style='font-size:2rem;'>📈</div>
                    <b>3. Sube tu rating</b>
                    <p style='color:#aaa; font-size:0.85rem; margin-top:0.5rem;'>
                        Cada respuesta actualiza tu ELO en tiempo real.
                        Escala los 16 niveles desde Aspirante hasta Leyenda Suprema.
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.write("")
        _wb1, _wb2, _wb3 = st.columns([2, 2, 1])
        with _wb1:
            if st.button(
                "🎓 Ir a Mis Cursos",
                type="primary",
                use_container_width=True,
                key="welcome_goto_courses",
            ):
                st.session_state.welcome_dismissed = True
                st.session_state._pending_student_mode = "🎓 Mis Cursos"
                st.rerun()
        with _wb2:
            if st.button(
                "🔑 Tengo un código de invitación",
                use_container_width=True,
                key="welcome_goto_code",
            ):
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
        st.info(
            "📚 Aún no tienes cursos inscritos. Ve a **🎓 Mis Cursos** en el menú lateral para matricularte."
        )
    elif mode == "📝 Practicar" and "selected_course" not in st.session_state:
        # ── Pantalla de selección de curso ──────────────────────────────
        st.title("🚀 Sala de Estudio")
        if _level == "semillero":
            _sem_grade = st.session_state.get("student_grade") or repo.get_grade(
                st.session_state.user_id
            )
            st.session_state["student_grade"] = _sem_grade
            _grade_label = f" — Grado {_sem_grade}°" if _sem_grade else ""
            st.markdown(
                f"### 🏅 Semillero de Matemáticas — Preparación Olimpiadas de Matemáticas{_grade_label}"
            )
            st.markdown("---")
        st.markdown("#### Selecciona la materia que deseas practicar")
        st.markdown("")

        # Grid de cards: 2 columnas
        for row_start in range(0, len(_enrolled), 2):
            cols = st.columns(2)
            for col_idx, course in enumerate(_enrolled[row_start : row_start + 2]):
                c_name = course["name"]
                c_elo = st.session_state.vector.get(c_name)
                c_rank, c_color = get_rank(c_elo)
                # Posición del estudiante en esta materia
                _c_rank_info = repo.get_student_rank(st.session_state.user_id, course["id"])
                _c_rank_text = (
                    f"📊 Tu posición: #{_c_rank_info['rank']} de {_c_rank_info['total_students']} estudiantes"
                    if _c_rank_info
                    else "Sin posición aún"
                )
                _c_special = course.get("block") != _student_block
                _c_special_html = (
                    '<p style="color:#FFD700; font-size:0.7rem; margin:4px 0 0;">📌 Acceso especial</p>'
                    if _c_special
                    else ""
                )
                with cols[col_idx]:
                    _banner_b64 = _get_banner_b64(c_name)
                    _banner_html = (
                        (
                            f'<img src="data:image/png;base64,{_banner_b64}" '
                            f'style="width:100%;border-radius:16px 16px 0 0;display:block;">'
                        )
                        if _banner_b64
                        else ""
                    )
                    _top_radius = "0" if _banner_b64 else "16px"
                    _card_html = (
                        f'<div style="border-radius:16px;'
                        f"background:rgba(38,39,48,0.95);"
                        f"border:1px solid {c_color}44;"
                        f"box-shadow:0 4px 20px {c_color}22;"
                        f'overflow:hidden;margin-bottom:12px;">'
                        + _banner_html
                        + f'<div style="padding:20px 24px;text-align:center;">'
                        f'<h3 style="color:#fff!important;margin:0 0 12px 0;'
                        f"border-left:none;padding-left:0;"
                        f"background:linear-gradient(90deg,#00C9FF,#92FE9D);"
                        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
                        f"{c_name}</h3>"
                        + _c_special_html
                        + f'<p style="color:{c_color};font-size:0.9rem;margin:0;">{c_rank}</p>'
                        f'<p style="color:#fff;font-size:2.4rem;font-weight:700;margin:4px 0;">'
                        f"{c_elo:.0f}</p>"
                        f'<p style="color:#888;font-size:0.8rem;margin:0;">Puntos ELO</p>'
                        f'<p style="color:#aaa;font-size:0.8rem;margin:6px 0 0;">{_c_rank_text}</p>'
                        f"</div>"
                        f"</div>"
                    )
                    st.markdown(_card_html, unsafe_allow_html=True)
                    if st.button(f"Practicar", key=f"sel_course_{course['id']}", width="stretch"):
                        st.session_state.selected_course = course
                        st.session_state.question_start_time = None
                        st.session_state.pop("current_question", None)
                        st.rerun()

        # ── Ranking General por nivel educativo — Top 5 ──────────────
        st.markdown("---")
        _level_label = {
            "universidad": "Universidad",
            "colegio": "Colegio",
            "concursos": "Concursos",
            "semillero": "Semillero",
        }.get(_level, _level.title())
        _rank_grade = None
        if _level == "semillero":
            _rank_grade = st.session_state.get("student_grade") or repo.get_grade(
                st.session_state.user_id
            )
            st.session_state["student_grade"] = _rank_grade
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
                _is_me_sel = _r["username"] == _my_user_sel
                if _is_me_sel:
                    _in_top_sel = True
                _bg_sel = "background:rgba(255,215,0,0.15); font-weight:700;" if _is_me_sel else ""
                _pos_sel = _medal_sel.get(_r["rank"], str(_r["rank"]))
                _grank_html += f"<tr style='{_bg_sel} border-bottom:1px solid #333;'>"
                _grank_html += f"<td style='padding:4px 6px; text-align:center;'>{_pos_sel}</td>"
                _grank_html += f"<td style='padding:4px 6px;'>{_r['username']}</td>"
                _grank_html += (
                    f"<td style='padding:4px 6px; text-align:center;'>{_r['global_elo']:.0f}</td>"
                )
                _grank_html += f"<td style='padding:4px 6px; text-align:center;'>{_r['attempts_this_week']}</td>"
                _grank_html += "</tr>"
            _grank_html += "</table>"
            st.markdown(_grank_html, unsafe_allow_html=True)
            if not _in_top_sel:
                _my_global_rank = repo.get_student_rank(
                    st.session_state.user_id, education_level=_level, grade=_rank_grade
                )
                if _my_global_rank:
                    st.caption(
                        f"Tu posición: #{_my_global_rank['rank']} de {_my_global_rank['total_students']} 🎯"
                    )
                else:
                    st.caption("Practica esta semana para aparecer en el ranking")
        else:
            st.caption(f"Sin actividad esta semana en {_level_label}.")

    elif mode == "📝 Practicar":
        selected_course_id = st.session_state.selected_course["id"]
        selected_topic = st.session_state.selected_course["name"]
        current_elo_display = st.session_state.vector.get(selected_topic)
        current_rd_display = st.session_state.vector.get_rd(selected_topic)
        topic_display_name = selected_topic

        rank_name, rank_color = get_rank(current_elo_display)

        st.title("🚀 Sala de Estudio")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(
                f"""
                <div class="elo-card">
                    <p style="color: #aaa; margin-bottom: 5px; font-weight: 600;">NIVEL ACTUAL</p>
                    <h2 style="color: {rank_color}; margin: 0; text-shadow: 0 0 10px {rank_color};">{rank_name}</h2>
                    <h1 style="font-size: 3.5rem; margin: 10px 0; color: white;">{current_elo_display:.0f}</h1>
                    <p style="color: #aaa; font-size: 0.9rem;">Puntos ELO · {topic_display_name}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )
            # T8c: racha de estudio (días consecutivos en este curso)
            _streak = cached(
                f"cache_streak_{selected_course_id}",
                lambda: repo.get_study_streak(st.session_state.user_id, selected_course_id),
            )
            if _streak == 0:
                st.markdown(
                    """
                    <div style="text-align:center; padding:12px 8px; background:linear-gradient(135deg,#1a1a2e,#16213e);
                                border-radius:12px; margin-bottom:12px;">
                        <div style="font-size:2rem;">💤</div>
                        <p style="color:#aaa; margin:4px 0 0; font-size:0.9rem;">Empieza hoy tu racha de estudio</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            elif _streak <= 2:
                st.markdown(
                    f"""
                    <div style="text-align:center; padding:12px 8px; background:linear-gradient(135deg,#1a1a2e,#2d1b00);
                                border-radius:12px; margin-bottom:12px;">
                        <div style="font-size:2.5rem;">🔥</div>
                        <div style="font-size:2rem; font-weight:800; color:#FF9800;">{_streak} día{'s' if _streak != 1 else ''}</div>
                        <p style="color:#FFB74D; margin:2px 0 0; font-size:0.85rem;">¡Buen inicio!</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            elif _streak <= 6:
                st.markdown(
                    f"""
                    <div style="text-align:center; padding:12px 8px; background:linear-gradient(135deg,#1a1a2e,#4a1500);
                                border-radius:12px; margin-bottom:12px;">
                        <div style="font-size:2.5rem;">🔥🔥</div>
                        <div style="font-size:2rem; font-weight:800; color:#FF5722;">{_streak} días</div>
                        <p style="color:#FF8A65; margin:2px 0 0; font-size:0.85rem;">¡Vas en racha!</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align:center; padding:14px 8px; background:linear-gradient(135deg,#4a0000,#ff4500,#ff8c00);
                                border-radius:12px; margin-bottom:12px; box-shadow:0 0 15px rgba(255,69,0,0.3);">
                        <div style="font-size:3rem;">🔥🔥🔥</div>
                        <div style="font-size:2.2rem; font-weight:900; color:#fff;">{_streak} días</div>
                        <p style="color:#FFE0B2; margin:2px 0 0; font-size:0.9rem; font-weight:700;">¡IMPARABLE!</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            st.info(
                "💡 **Consejo:** La constancia es clave. Practica diariamente para consolidar tu aprendizaje."
            )

            # ── Ranking del curso actual Top 5 ──────────────────────────
            _ranking = cached(
                "cache_course_ranking", lambda: repo.get_course_ranking(selected_course_id, limit=5)
            )
            if _ranking:
                st.markdown(f"#### 🏆 Ranking — {topic_display_name}")
                _medal = {1: "🥇", 2: "🥈", 3: "🥉"}
                _my_user = st.session_state.username
                _in_top = False
                _rank_html = (
                    "<table style='width:100%; border-collapse:collapse; font-size:0.9rem;'>"
                )
                _rank_html += "<tr style='border-bottom:1px solid #444;'><th style='padding:4px 6px;'>🏅</th><th style='padding:4px 6px; text-align:left;'>Estudiante</th><th style='padding:4px 6px;'>ELO</th><th style='padding:4px 6px;'>Intentos</th></tr>"
                for _r in _ranking:
                    _is_me = _r["username"] == _my_user
                    if _is_me:
                        _in_top = True
                    _bg = "background:rgba(255,215,0,0.15); font-weight:700;" if _is_me else ""
                    _pos = _medal.get(_r["rank"], str(_r["rank"]))
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
                    _my_rank = repo.get_student_rank(
                        st.session_state.user_id, course_id=selected_course_id
                    )
                    if _my_rank:
                        st.caption(
                            f"Tu posición: #{_my_rank['rank']} de {_my_rank['total_students']} 🎯"
                        )
                    else:
                        st.caption("Sigue practicando para entrar al ranking")
            else:
                st.markdown(f"#### 🏆 Ranking — {topic_display_name}")
                st.caption("Sin actividad esta semana en este curso.")

        with col2:
            st.subheader(f"📖 Ejercicio: {selected_topic}")
            item_data = None  # inicializar para scope exterior (procedimiento manuscrito)

            # ── Pantalla de celebración KatIA (bloquea vista de pregunta) ──
            if st.session_state.get("show_celebration"):
                _cel_sc = st.session_state.get("celebration_streak", 5)
                _cel_elo = st.session_state.get("celebration_elo", 1000)
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

                st.markdown(
                    f"""
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
                """,
                    unsafe_allow_html=True,
                )
                st.write("")
                if st.button(
                    "🐾 SEGUIR PRACTICANDO", width="stretch", type="primary", key="btn_continue_cel"
                ):
                    st.session_state.show_celebration = False
                    st.session_state.pop("current_question", None)
                    st.session_state.pop("katia_chat_history", None)
                    st.rerun()

            # ── Pantalla de resultado (después de responder) ─────────
            elif st.session_state.get("show_result"):
                _res_correct = st.session_state.get("last_result_correct", False)
                _res_elo_before = st.session_state.get(
                    "last_result_elo_before", current_elo_display
                )
                _res_elo_after = st.session_state.vector.get(selected_topic)
                _res_delta = _res_elo_after - _res_elo_before
                _delta_str = f"+{_res_delta:.0f}" if _res_delta >= 0 else f"{_res_delta:.0f}"

                if _res_correct:
                    st.success(
                        f"¡Respuesta correcta! 🎓   {_delta_str} pts  ·  Tu ELO: **{_res_elo_after:.0f}**"
                    )
                else:
                    st.error(
                        f"Respuesta incorrecta.   {_delta_str} pts  ·  Tu ELO: **{_res_elo_after:.0f}**"
                    )
                    st.info(
                        "💡 ¿Quieres entender el concepto? Pregúntale a KatIA abajo — te guiará sin revelar la respuesta."
                    )

                st.write("")
                if st.button(
                    "▶️ SIGUIENTE PREGUNTA", width="stretch", type="primary", key="btn_next_question"
                ):
                    st.session_state.show_result = False
                    st.session_state.pop("current_question", None)
                    st.session_state.pop("last_result_item", None)
                    st.session_state.pop("last_result_correct", None)
                    st.session_state.pop("last_result_elo_before", None)
                    st.session_state.pop("katia_chat_history", None)
                    st.rerun()

            else:
                # ── Vista normal: pregunta activa ─────────────────────
                if "current_question" not in st.session_state:
                    st.session_state.current_question = (
                        st.session_state.student_service.get_next_question(
                            st.session_state.user_id,
                            selected_topic,
                            st.session_state.vector,
                            session_correct_ids=st.session_state.session_correct_ids,
                            session_wrong_timestamps=st.session_state.session_wrong_timestamps,
                            session_questions_count=st.session_state.session_questions_count,
                            course_id=selected_course_id,
                        )
                    )
                item_data, status = st.session_state.current_question

                if status == "mastery":
                    st.success(
                        "🎉 ¡Excelente trabajo! Has alcanzado el nivel de excelencia en esta materia."
                    )
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
                        font_size="1.3rem",
                        height=45,
                        color="#FFD700",
                        bold=True,
                    )

                    with st.container(border=True):
                        diff = item_data.get("difficulty") or 1000

                        def get_difficulty_label(d):
                            if d < 750:
                                return 1, "Fácil"
                            if d < 950:
                                return 2, "Básico"
                            if d < 1150:
                                return 3, "Intermedio"
                            if d < 1400:
                                return 4, "Difícil"
                            return 5, "Experto"

                        _nstars, _dlabel = get_difficulty_label(diff)
                        _filled = "★" * _nstars
                        _empty = "★" * (5 - _nstars)
                        _item_topic = item_data.get("topic") or selected_topic or ""
                        st.caption(f"Área: {selected_topic} | Tema: {_item_topic}")
                        # ── Tag badges (3 dimensiones de la taxonomía) ────────────────
                        _tags = item_data.get("tags") or []
                        if _tags:

                            def _tag_style(tag):
                                if tag.startswith("[Enfoque:"):
                                    return "#1565C0", "#E3F2FD"  # azul — cognitivo
                                if tag.startswith("[General:"):
                                    return "#2E7D32", "#E8F5E9"  # verde — transversal
                                if tag.startswith("[Específica:"):
                                    return "#B45309", "#FFF8E1"  # ámbar — conocimiento
                                return "#555555", "#EEEEEE"

                            _badges = "".join(
                                '<span style="'
                                f"background:{_tag_style(t)[1]};"
                                f"color:{_tag_style(t)[0]};"
                                f"border:1px solid {_tag_style(t)[0]};"
                                "border-radius:4px;padding:2px 8px;"
                                "font-size:0.72rem;font-weight:600;"
                                "margin-right:4px;margin-bottom:4px;"
                                "display:inline-block;line-height:1.6;"
                                f'">{t[1:-1]}</span>'
                                for t in _tags
                            )
                            st.markdown(
                                f'<div style="margin:4px 0 6px 0;">{_badges}</div>',
                                unsafe_allow_html=True,
                            )
                        st.markdown(
                            f"<span style='color:#FFD700; font-weight:700; font-size:1rem;'>{_filled}</span>"
                            f"<span style='color:#444; font-weight:700; font-size:1rem;'>{_empty}</span>"
                            f"<span style='font-weight:600; font-size:0.9rem;'> {_dlabel}</span>"
                            f"<span style='color:#888; font-size:0.8rem;'> · {diff:.0f}</span>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"### {item_data.get('content') or ''}")

                        _img_url = item_data.get("image_url") or item_data.get("image_path")
                        if _img_url:
                            try:
                                _img_source = _img_url
                                if not _img_url.startswith("http"):
                                    _abs = os.path.join(base_path, _img_url)
                                    if os.path.isfile(_abs):
                                        with open(_abs, "rb") as _f:
                                            _img_source = _f.read()
                                _c1, _c2, _c3 = st.columns([1, 2, 1])
                                with _c2:
                                    st.image(
                                        _img_source,
                                        width=420,
                                        caption="Figura correspondiente a la pregunta",
                                    )
                            except Exception:
                                pass

                        st.write("")

                        # ── Stakes preview (puntos en juego) ─────────────
                        _p_win = expected_score(
                            current_elo_display, item_data.get("difficulty") or 1000
                        )
                        _k_est = 32.0 * (current_rd_display / 350.0)
                        _pts_up = max(1, round(_k_est * (1 - _p_win)))
                        _pts_dn = max(1, round(_k_est * _p_win))
                        st.markdown(
                            f"""
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
                        """,
                            unsafe_allow_html=True,
                        )

                        if item_data.get("options"):
                            shuffled_options = item_data["options"].copy()
                            random.Random(item_data["id"]).shuffle(shuffled_options)
                            option_labels = [chr(65 + i) for i in range(len(shuffled_options))]
                            label_to_text = dict(zip(option_labels, shuffled_options))
                            _item_id = item_data["id"]

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
                                width="stretch",
                                disabled=(selected_option is None),
                            )

                            if submit_button:
                                st.session_state.last_result_elo_before = current_elo_display
                                is_correct = selected_option == item_data.get("correct_option")
                                if is_correct:
                                    st.session_state.streak_correct += 1
                                    _sc = st.session_state.streak_correct
                                    if _sc > 0 and _sc % 5 == 0:
                                        st.session_state.show_celebration = True
                                        st.session_state.celebration_streak = _sc
                                        st.session_state.celebration_elo = (
                                            st.session_state.vector.get(selected_topic)
                                        )
                                else:
                                    st.session_state.streak_correct = 0
                                handle_answer_topic(is_correct, item_data)

                        # --- CHATBOT KatIA (conversacional multi-turno) ---
                        st.markdown("---")
                        _katia_avatar = _KATIA_IMG or "🐱"
                        st.markdown("#### 🐾 KatIA — Tu Tutora")
                        if _KATIA_IMG:
                            st.image(_KATIA_IMG, width=80)

                        if "katia_chat_history" not in st.session_state:
                            st.session_state.katia_chat_history = []

                        _chat_container = st.container(height=350)
                        with _chat_container:
                            if not st.session_state.katia_chat_history:
                                _katia_welcome = get_random_message(MENSAJES_BIENVENIDA)
                                st.chat_message("assistant", avatar=_katia_avatar).markdown(
                                    _katia_welcome
                                )
                            for _msg in st.session_state.katia_chat_history:
                                if _msg["role"] == "user":
                                    st.chat_message("user").markdown(_msg["content"])
                                else:
                                    st.chat_message("assistant", avatar=_katia_avatar).markdown(
                                        _msg["content"]
                                    )

                        if st.session_state.ai_available:
                            _katia_input = st.chat_input(
                                "Escribe tu pregunta a KatIA...", key="katia_chat_input"
                            )
                        else:
                            _katia_input = None
                            st.caption(
                                "IA no disponible — configura un proveedor en la barra lateral."
                            )

                        if _katia_input:
                            st.session_state.katia_chat_history.append(
                                {"role": "user", "content": _katia_input}
                            )
                            _soc_model = select_model_for_task(
                                "tutor_socratic",
                                st.session_state.get("lmstudio_models", []),
                                st.session_state.model_cog,
                                provider=st.session_state.get("ai_provider"),
                            )
                            _q_ctx = {
                                "content": item_data.get("content") or "",
                                "topic": item_data.get("topic") or "",
                                "options": item_data.get("options") or [],
                                "selected_option": st.session_state.get(
                                    f"answer_text_{item_data['id']}", ""
                                ),
                                "correct_option": item_data.get("correct_option") or "",
                            }
                            try:
                                with st.spinner("KatIA está pensando..."):
                                    _katia_resp = "".join(
                                        get_katia_chat_stream(
                                            messages=st.session_state.katia_chat_history,
                                            question_context=_q_ctx,
                                            base_url=st.session_state.ai_url,
                                            model_name=_soc_model,
                                            api_key=st.session_state.cloud_api_key,
                                            provider=st.session_state.get("ai_provider"),
                                        )
                                    )
                                if isinstance(_katia_resp, str) and not validate_socratic_response(
                                    _katia_resp
                                ):
                                    _katia_resp = "¿Qué pasos has intentado hasta ahora? ¿Qué parte del problema te genera más dudas?"
                                with _chat_container:
                                    st.chat_message("user").markdown(_katia_input)
                                    with st.chat_message("assistant", avatar=_katia_avatar):
                                        st.markdown(_katia_resp)
                                if isinstance(_katia_resp, str):
                                    st.session_state.katia_chat_history.append(
                                        {"role": "assistant", "content": _katia_resp}
                                    )
                                    try:
                                        repo.save_katia_interaction(
                                            user_id=st.session_state.user_id,
                                            course_id=selected_course_id,
                                            item_id=item_data.get("id", ""),
                                            item_topic=item_data.get("topic", ""),
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
                                    _katia_err,
                                    exc_info=True,
                                )
                            st.rerun()

                        if not item_data.get("options"):
                            st.warning("Pregunta sin opciones configuradas.")

        # --- Procedimiento Manuscrito (columna izquierda, debajo del ELO) ---
        if item_data:
            with col1:
                st.markdown("---")
                st.markdown(
                    """
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
                """,
                    unsafe_allow_html=True,
                )
                uploaded_file = st.file_uploader(
                    "Foto, escaneo o PDF de tu desarrollo:",
                    type=["jpg", "jpeg", "png", "webp", "pdf"],
                    key=f"proc_upload_{item_data['id']}",
                    label_visibility="collapsed",
                )
                if uploaded_file is not None:
                    if True:
                        _iid = item_data["id"]
                        _uid = st.session_state.user_id
                        _ext = uploaded_file.name.rsplit(".", 1)[-1].lower()

                        import hashlib

                        _raw_bytes = uploaded_file.getvalue()
                        _file_hash = hashlib.sha256(_raw_bytes).hexdigest()
                        print(
                            f"[UPLOAD] archivo recibido: {uploaded_file.name}, size={len(_raw_bytes)} bytes, type={uploaded_file.type}"
                        )

                        if _ext == "pdf":
                            try:
                                import fitz  # PyMuPDF

                                _pdf_doc = fitz.open(stream=_raw_bytes, filetype="pdf")
                                _page = _pdf_doc[0]
                                _pix = _page.get_pixmap(dpi=200)
                                _file_bytes = _pix.tobytes("png")
                                _mime = "image/png"
                                _pdf_doc.close()
                            except Exception as _pdf_err:
                                st.error(f"No se pudo procesar el PDF: {_pdf_err}")
                                _file_bytes = None
                        else:
                            _file_bytes = _raw_bytes
                            _mime = {
                                "jpg": "image/jpeg",
                                "jpeg": "image/jpeg",
                                "png": "image/png",
                                "webp": "image/webp",
                            }.get(_ext, "image/jpeg")

                        if _file_bytes is None:
                            st.stop()

                        # T7: verificar si otro estudiante ya subió el mismo archivo para esta pregunta
                        _plagiarism_detected = repo.check_file_hash_duplicate(
                            _iid, _uid, _file_hash
                        )
                        if _plagiarism_detected:
                            st.error(
                                "⚠️ Este archivo ya ha sido registrado por otro usuario "
                                "para esta pregunta."
                            )

                        st.image(_file_bytes, width="stretch")

                        # Groq activo → revisión matemática rigurosa con Llama 4 Scout
                        _is_groq = st.session_state.get("ai_provider") == "groq" and bool(
                            st.session_state.get("cloud_api_key")
                        )
                        # Model Router: seleccionar modelo con visión+razonamiento
                        _proc_model = select_model_for_task(
                            "image_procedure_analysis",
                            st.session_state.get("lmstudio_models", []),
                            st.session_state.model_analysis,
                            provider=st.session_state.get("ai_provider"),
                        )
                        _vision_ok = _is_groq or (_proc_model is not None)

                        # ── T5b: contador de intentos fallidos por pregunta ────
                        _fail_key = f"proc_fail_count_{_iid}"
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
                                    print(
                                        f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes"
                                    )
                                    st.session_state.db.save_procedure_submission(
                                        _uid,
                                        _iid,
                                        item_data.get("content") or "",
                                        _file_bytes,
                                        _mime,
                                        file_hash=_file_hash,
                                    )
                                    st.session_state.db.save_ai_proposed_score(
                                        _uid,
                                        _iid,
                                        0.0,
                                        ai_feedback="Procedimiento irrelevante para la pregunta (3 intentos fallidos).",
                                    )
                                    st.session_state[f"proc_ai_saved_{_iid}"] = True
                                    st.session_state[_fail_key] = 0
                                    st.rerun()
                            with _b2:
                                if st.button("🚫 No enviar nada", key=f"proc_cancel_{_iid}"):
                                    st.session_state[_fail_key] = 0
                                    st.rerun()
                            with _b3:
                                if st.button("📁 Subir el correcto", key=f"proc_retry_{_iid}"):
                                    st.session_state[_fail_key] = 0
                                    st.rerun()

                        # ── Análisis con IA ───────────────────────────────
                        elif _vision_ok:
                            _btn_label = (
                                "🔬 Analizar procedimiento"
                                if _is_groq
                                else "🔍 Analizar procedimiento"
                            )
                            if st.button(
                                _btn_label,
                                key=f"analyze_proc_{_iid}",
                                width="stretch",
                                disabled=not st.session_state.ai_available or _plagiarism_detected,
                            ):
                                _q_content = item_data.get("content") or ""
                                if not _q_content.strip():
                                    st.error(
                                        "No se pudo cargar el contenido de la pregunta. Intenta recargar."
                                    )
                                    st.stop()

                                # ── GIF de KatIA revisando mientras la IA analiza ──
                                _katia_review_placeholder = st.empty()
                                _gif_start_time = time.time()
                                _GIF_LOOP_DURATION = 13.44  # 48 frames × 280ms
                                if _KATIA_GIF_CORRECTO_HTML:
                                    _review_html = (
                                        '<div style="text-align:center;">'
                                        f"{_KATIA_GIF_CORRECTO_HTML}"
                                        '<p style="color:#888;font-size:0.85rem;">KatIA está revisando tu procedimiento... 🔍</p>'
                                        "</div>"
                                    )
                                    _katia_review_placeholder.markdown(
                                        _review_html, unsafe_allow_html=True
                                    )
                                _spinner_msg = (
                                    "Analizando con rigor matemático (Llama 4 Scout)..."
                                    if _is_groq
                                    else "Analizando procedimiento..."
                                )
                                with st.spinner(_spinner_msg):
                                    _is_relevant = True
                                    if not _is_groq:
                                        _is_relevant = validate_procedure_relevance(
                                            _file_bytes,
                                            _mime,
                                            _q_content,
                                            api_key=st.session_state.cloud_api_key,
                                            provider=st.session_state.get("ai_provider"),
                                            base_url=st.session_state.ai_url,
                                            model_name=_proc_model
                                            or st.session_state.model_analysis,
                                        )

                                    if not _is_relevant:
                                        st.session_state[_fail_key] = _fail_count + 1
                                        print(
                                            f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes"
                                        )
                                        st.session_state.db.save_procedure_submission(
                                            _uid,
                                            _iid,
                                            _q_content,
                                            _file_bytes,
                                            _mime,
                                            file_hash=_file_hash,
                                        )
                                        st.session_state.db.save_ai_proposed_score(
                                            _uid,
                                            _iid,
                                            0.0,
                                            ai_feedback="Procedimiento irrelevante para la pregunta.",
                                        )
                                        st.session_state[f"proc_ai_saved_{_iid}"] = True
                                        _new_fails = _fail_count + 1
                                        if _new_fails < 3:
                                            st.warning(
                                                f"⚠️ El procedimiento no corresponde a la pregunta asignada "
                                                f"(intento {_new_fails}/3). Sube el procedimiento correcto."
                                            )
                                        else:
                                            st.rerun()
                                    elif _is_groq:
                                        try:
                                            _rev = review_math_procedure(
                                                _file_bytes,
                                                _mime,
                                                api_key=st.session_state.cloud_api_key,
                                                question_content=_q_content,
                                            )
                                            if not _rev.get("corresponde_a_pregunta", True):
                                                st.session_state[_fail_key] = _fail_count + 1
                                                _new_fails = _fail_count + 1
                                                if _new_fails < 3:
                                                    st.warning(
                                                        f"⚠️ El procedimiento no corresponde a la pregunta asignada "
                                                        f"(intento {_new_fails}/3). Sube el procedimiento correcto."
                                                    )
                                                if not st.session_state.get(
                                                    f"proc_ai_saved_{_iid}", False
                                                ):
                                                    print(
                                                        f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes"
                                                    )
                                                    st.session_state.db.save_procedure_submission(
                                                        _uid,
                                                        _iid,
                                                        _q_content,
                                                        _file_bytes,
                                                        _mime,
                                                        file_hash=_file_hash,
                                                    )
                                                    st.session_state.db.save_ai_proposed_score(
                                                        _uid,
                                                        _iid,
                                                        0.0,
                                                        ai_feedback="Procedimiento irrelevante para la pregunta.",
                                                    )
                                                    st.session_state[f"proc_ai_saved_{_iid}"] = True
                                                if _new_fails >= 3:
                                                    st.rerun()
                                            else:
                                                st.session_state[_fail_key] = 0
                                                st.session_state[f"proc_review_{_iid}"] = _rev
                                                if not st.session_state.get(
                                                    f"proc_ai_saved_{_iid}", False
                                                ):
                                                    print(
                                                        f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes"
                                                    )
                                                    st.session_state.db.save_procedure_submission(
                                                        _uid,
                                                        _iid,
                                                        _q_content,
                                                        _file_bytes,
                                                        _mime,
                                                        file_hash=_file_hash,
                                                    )
                                                    _ai_score = _rev.get("score_procedimiento")
                                                    _ai_eval = _rev.get("evaluacion_global") or ""
                                                    if _ai_score is not None:
                                                        st.session_state.db.save_ai_proposed_score(
                                                            _uid,
                                                            _iid,
                                                            float(_ai_score),
                                                            ai_feedback=_ai_eval,
                                                        )
                                                    st.session_state[f"proc_ai_saved_{_iid}"] = True
                                        except (ValueError, ConnectionError) as _exc:
                                            st.error(f"Error en la revisión matemática: {_exc}")
                                            if not st.session_state.get(
                                                f"proc_ai_saved_{_iid}", False
                                            ):
                                                try:
                                                    repo.save_procedure_submission(
                                                        _uid,
                                                        _iid,
                                                        _q_content,
                                                        _file_bytes,
                                                        _mime,
                                                        file_hash=_file_hash,
                                                    )
                                                    st.session_state[f"proc_ai_saved_{_iid}"] = True
                                                except Exception:
                                                    pass
                                            st.session_state[f"proc_no_vision_{_iid}"] = True
                                    else:
                                        st.session_state[_fail_key] = 0
                                        try:
                                            result = analyze_procedure_image(
                                                _file_bytes,
                                                _mime,
                                                _q_content,
                                                model_name=_proc_model
                                                or st.session_state.model_analysis,
                                                base_url=st.session_state.ai_url,
                                                api_key=st.session_state.cloud_api_key,
                                                provider=st.session_state.get("ai_provider"),
                                            )
                                            if result == "VISION_NOT_SUPPORTED":
                                                st.session_state[f"proc_no_vision_{_iid}"] = True
                                            else:
                                                st.session_state[f"proc_fb_{_iid}"] = result
                                        except ConnectionError:
                                            st.warning(
                                                "⚠️ No se pudo conectar con la IA para revisar el procedimiento."
                                            )
                                            st.session_state[f"proc_no_vision_{_iid}"] = True
                                        except TimeoutError:
                                            st.warning(
                                                "⏱️ La IA tardó demasiado. El procedimiento se enviará al profesor."
                                            )
                                            st.session_state[f"proc_no_vision_{_iid}"] = True
                                        except Exception as _proc_err:
                                            _app_logger.error(
                                                "Error en análisis de procedimiento (usuario=%s, ítem=%s): %s",
                                                st.session_state.get("username", "desconocido"),
                                                _iid,
                                                _proc_err,
                                                exc_info=True,
                                            )
                                            st.session_state[f"proc_no_vision_{_iid}"] = True

                                # Esperar a que el GIF complete al menos un loop
                                _elapsed = time.time() - _gif_start_time
                                _remaining = _GIF_LOOP_DURATION - _elapsed
                                if _remaining > 0:
                                    time.sleep(_remaining)
                                # Limpiar GIF de "revisando" al terminar el análisis
                                _katia_review_placeholder.empty()

                            if st.session_state.get(f"proc_no_vision_{_iid}"):
                                st.info(
                                    "El profesor revisará el archivo y proporcionará la retroalimentación."
                                )

                            # ── Resultado: revisión matemática rigurosa (Groq) ──
                            _math_review = st.session_state.get(f"proc_review_{_iid}")
                            if _math_review:
                                _pscore_v = _math_review.get("score_procedimiento", 0)
                                _katia_result_html = (
                                    _KATIA_GIF_CORRECTO_HTML
                                    if _pscore_v >= 91
                                    else _KATIA_GIF_ERRORES_HTML
                                )
                                if _katia_result_html:
                                    _result_div = (
                                        '<div style="text-align:center;">'
                                        f"{_katia_result_html}"
                                        "</div>"
                                    )
                                    st.markdown(_result_div, unsafe_allow_html=True)

                                _katia_proc_msg = get_procedure_comment(_pscore_v)
                                _katia_proc_avatar = _KATIA_IMG or "🐱"
                                with st.chat_message("assistant", avatar=_katia_proc_avatar):
                                    st.markdown(f"**KatIA dice:** {_katia_proc_msg}")
                                    if _pscore_v < 91:
                                        _eval_global = _math_review.get("evaluacion_global") or ""
                                        if _eval_global:
                                            st.caption(strip_thinking_tags(_eval_global))

                                with st.container(border=True):
                                    st.markdown("##### 🔬 Revisión Matemática Rigurosa")
                                    _pscore_color = (
                                        "#FF4B4B"
                                        if _pscore_v < 40
                                        else "#FFD700" if _pscore_v < 70 else "#92FE9D"
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
                                    if _math_review.get("transcripcion"):
                                        with st.expander("📝 Transcripción del procedimiento"):
                                            st.markdown(
                                                strip_thinking_tags(_math_review["transcripcion"])
                                            )
                                    _pasos = _math_review.get("pasos", [])
                                    if _pasos:
                                        with st.expander(f"🔢 Pasos analizados ({len(_pasos)})"):
                                            for _paso in _pasos:
                                                _ev = _paso.get("evaluacion", "")
                                                _paso_color = (
                                                    "#92FE9D"
                                                    if _ev == "Valido"
                                                    else (
                                                        "#FF4B4B"
                                                        if "incorrecto" in _ev.lower()
                                                        else "#FFD700"
                                                    )
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
                                    _errores = _math_review.get("errores_detectados", [])
                                    if _errores:
                                        with st.expander(f"⚠️ Errores detectados ({len(_errores)})"):
                                            for _err in _errores:
                                                st.markdown(f"- {strip_thinking_tags(_err)}")
                                    _saltos = _math_review.get("saltos_logicos", [])
                                    if _saltos:
                                        with st.expander(f"🔗 Saltos lógicos ({len(_saltos)})"):
                                            for _salto in _saltos:
                                                st.markdown(f"- {strip_thinking_tags(_salto)}")
                                    _res_ok = _math_review.get("resultado_correcto", False)
                                    st.markdown(
                                        f"**Resultado final:** "
                                        f"{'✅ Correcto' if _res_ok else '❌ Incorrecto'}"
                                    )
                                    if _math_review.get("evaluacion_global"):
                                        st.markdown(
                                            f"**Evaluación global:** {strip_thinking_tags(_math_review['evaluacion_global'])}"
                                        )

                                    # ── Pipeline de verificación simbólica (complementario) ──
                                    try:
                                        _sym_result = math_pipeline_analyze(_math_review)
                                        if (
                                            _sym_result
                                            and _sym_result.analysis
                                            and _sym_result.analysis.sympy_used
                                        ):
                                            _sym_invalid = _sym_result.analysis.invalid_steps
                                            if _sym_invalid > 0:
                                                with st.expander(
                                                    f"🧮 Verificación simbólica ({_sym_invalid} error(es))"
                                                ):
                                                    st.markdown(_sym_result.feedback)
                                            elif _sym_result.analysis.valid_steps > 1:
                                                with st.expander("🧮 Verificación simbólica"):
                                                    st.markdown(
                                                        "Todos los pasos verificados son algebraicamente correctos."
                                                    )
                                    except Exception as _sym_err:
                                        _app_logger.warning(
                                            "Verificación simbólica falló: %s. "
                                            "Se omite la sección de verificación algebraica.",
                                            _sym_err,
                                        )

                            # ── Resultado: revisión genérica (otros proveedores) ──
                            _ai_fb = st.session_state.get(f"proc_fb_{_iid}")
                            if _ai_fb:
                                with st.container(border=True):
                                    st.markdown("##### 🔍 Retroalimentación del procedimiento")
                                    st.markdown(strip_thinking_tags(_ai_fb))

                        # T6b: si el modelo no soporta visión
                        if not _vision_ok and _fail_count < 3:
                            st.info(
                                "📤 Tu modelo actual no soporta visión. El procedimiento "
                                "será enviado al profesor para revisión manual."
                            )

                        # ── Sección de envío al docente: SIEMPRE visible ──────────
                        st.markdown("---")
                        _sub = st.session_state.db.get_student_submission(_uid, _iid)
                        _sub_status = _sub["status"] if _sub else None

                        if _sub_status == "PENDING_TEACHER_VALIDATION":
                            _ai_prop = _sub.get("ai_proposed_score")
                            if _ai_prop is not None:
                                st.info(
                                    f"⏳ **Nota propuesta por IA: {_ai_prop:.1f}/100** — "
                                    "Tu profesor revisará y confirmará (o ajustará) la calificación."
                                )
                            else:
                                st.info("⏳ Procedimiento enviado al profesor para validación.")

                        elif _sub_status == "VALIDATED_BY_TEACHER":
                            with st.container(border=True):
                                st.markdown("##### ✅ Calificación validada por el Profesor")
                                _final = _sub.get("final_score")
                                _teacher_sc = _sub.get("teacher_score")
                                if _final is not None:
                                    st.metric("📊 Nota final (oficial)", f"{_final:.1f} / 100")
                                elif _teacher_sc is not None:
                                    st.metric("📊 Nota del profesor", f"{_teacher_sc:.1f} / 100")
                                if _sub.get("teacher_feedback"):
                                    st.markdown(_sub["teacher_feedback"])
                                _fb_path = _sub.get("feedback_image_path")
                                if _fb_path and os.path.exists(_fb_path):
                                    st.image(
                                        _fb_path,
                                        caption="Procedimiento calificado",
                                        width="stretch",
                                    )
                                elif _sub.get("feedback_image"):
                                    st.image(
                                        bytes(_sub["feedback_image"]),
                                        caption="Procedimiento calificado",
                                        width="stretch",
                                    )

                        elif _sub_status in ("pending", "reviewed"):
                            if _sub_status == "pending":
                                st.info("⏳ Procedimiento enviado. Tu profesor lo revisará pronto.")
                            else:
                                with st.container(border=True):
                                    st.markdown("##### ✅ Retroalimentación del Profesor")
                                    if _sub.get("procedure_score") is not None:
                                        st.metric(
                                            "📊 Nota del procedimiento",
                                            f"{_sub['procedure_score']:.1f} / 5.0",
                                        )
                                    if _sub.get("teacher_feedback"):
                                        st.markdown(_sub["teacher_feedback"])
                                    _fb_path = _sub.get("feedback_image_path")
                                    if _fb_path and os.path.exists(_fb_path):
                                        st.image(
                                            _fb_path,
                                            caption="Procedimiento calificado",
                                            width="stretch",
                                        )
                                    elif _sub.get("feedback_image"):
                                        st.image(
                                            bytes(_sub["feedback_image"]),
                                            caption="Procedimiento calificado",
                                            width="stretch",
                                        )

                        else:
                            _show_send_btn = (
                                not _vision_ok
                                or st.session_state.get(f"proc_no_vision_{_iid}", False)
                                or not st.session_state.get(f"proc_ai_saved_{_iid}", False)
                            )
                            if _show_send_btn and not _plagiarism_detected:
                                st.info(
                                    "El profesor revisará el archivo y proporcionará retroalimentación."
                                )
                                if st.button(
                                    "📤 Enviar al profesor para revisión",
                                    key=f"send_teacher_{_iid}",
                                    width="stretch",
                                ):
                                    print(
                                        f"[UPLOAD] Llamando save_procedure_submission con image_data={len(_file_bytes) if _file_bytes else 'None'} bytes"
                                    )
                                    st.session_state.db.save_procedure_submission(
                                        _uid,
                                        _iid,
                                        item_data.get("content") or "",
                                        _file_bytes,
                                        _mime,
                                        file_hash=_file_hash,
                                    )
                                    st.rerun()

    elif mode == "📊 Estadísticas":
        st.title("📊 Estadísticas de Aprendizaje")
        # T8c: racha de estudio en la cabecera de estadísticas
        _stat_streak = cached(
            "cache_streak", lambda: repo.get_study_streak(st.session_state.user_id)
        )
        if _stat_streak == 0:
            _streak_msg = "💤 Sin racha activa — ¡empieza hoy!"
            _streak_color = "#aaa"
        elif _stat_streak <= 2:
            _streak_msg = (
                f"🔥 Racha: {_stat_streak} día{'s' if _stat_streak != 1 else ''} — ¡Buen inicio!"
            )
            _streak_color = "#FF9800"
        elif _stat_streak <= 6:
            _streak_msg = f"🔥🔥 Racha: {_stat_streak} días — ¡Vas en racha!"
            _streak_color = "#FF5722"
        else:
            _streak_msg = f"🔥🔥🔥 Racha: {_stat_streak} días — ¡IMPARABLE!"
            _streak_color = "#FF4500"
        st.markdown(
            f"<p style='font-size:1.1rem; font-weight:700; color:{_streak_color};'>{_streak_msg}</p>",
            unsafe_allow_html=True,
        )

        history_full = st.session_state.db.get_user_history_full(st.session_state.user_id)
        attempts_data = st.session_state.db.get_attempts_for_ai(
            st.session_state.user_id, limit=1000
        )
        _proc_scores = st.session_state.db.get_student_procedure_scores(st.session_state.user_id)

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric(
                "Ejercicios Resueltos", len(history_full), delta=f"+{len(attempts_data)} recientes"
            )
        with m2:
            if attempts_data:
                accuracy = sum(1 for a in attempts_data if a["is_correct"]) / len(attempts_data)
                st.metric("Precisión Promedio", f"{accuracy:.1%}")
            else:
                st.metric("Precisión Promedio", "0%")
        with m3:
            global_elo = aggregate_global_elo(st.session_state.vector)
            rank_n, rank_c = get_rank(global_elo)
            st.metric("Nivel Global", f"{global_elo:.0f}", delta=rank_n)
        with m4:
            _st_times = [
                a.get("time_taken")
                for a in history_full
                if a.get("time_taken") and a["time_taken"] > 0
            ]
            _st_avg_t = sum(_st_times) / len(_st_times) if _st_times else 0
            st.metric("⏱️ Tiempo Prom.", f"{_st_avg_t:.0f}s" if _st_avg_t else "—")
        with m5:
            if _proc_scores:
                avg_proc = sum(s["score"] for s in _proc_scores) / len(_proc_scores)
                st.metric(
                    "📝 Procedimientos",
                    f"{avg_proc:.1f}/100",
                    delta=f"{len(_proc_scores)} evaluado(s)",
                )
            else:
                st.metric("📝 Procedimientos", "Sin datos")

        if not _proc_scores:
            st.info(
                "No has subido procedimientos manuales. Te recomendamos subir fotos de tu "
                "desarrollo paso a paso para que el profesor pueda evaluarte y la IA pueda "
                "darte mejores recomendaciones."
            )
        else:
            _proc_by_course = st.session_state.db.get_procedure_stats_by_course(
                st.session_state.user_id
            )
            if _proc_by_course:
                st.markdown("**📝 Calidad de procedimientos por curso:**")
                for _cid, _cdata in _proc_by_course.items():
                    _avg = _cdata["avg_score"]
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
        current_elos = cached(
            "cache_elo_by_topic",
            lambda: st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id),
        )

        if current_elos:
            try:
                topics_list = list(current_elos.keys())
                elos_list = [val[0] for val in current_elos.values()]
                rds_list = [val[1] for val in current_elos.values()]

                df_elo = pd.DataFrame(
                    {"Tema": topics_list, "ELO": elos_list, "RD": rds_list}
                ).sort_values("ELO", ascending=False)

                fig_bar = go.Figure()
                fig_bar.add_trace(
                    go.Bar(
                        x=df_elo["Tema"],
                        y=df_elo["ELO"],
                        marker_color="#00C9FF",
                        opacity=0.8,
                        error_y=dict(
                            type="data",
                            array=df_elo["RD"].tolist(),
                            color="#FFC107",
                            thickness=1.5,
                            width=5,
                        ),
                    )
                )
                fig_bar.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Materia",
                    yaxis_title="ELO",
                    yaxis=dict(range=[max(0, min(elos_list) - 50), None]),
                )
                st.plotly_chart(fig_bar, width="stretch")
            except Exception as e:
                st.error(f"Error visualizando gráfica: {str(e)}")
        else:
            st.info("Completa ejercicios para visualizar tu perfil de fortalezas.")

        st.subheader("📈 Progreso Académico")
        if history_full:
            df_hist = pd.DataFrame(history_full)
            df_hist["intento"] = range(1, len(df_hist) + 1)
            fig = go.Figure()
            for topic in df_hist["topic"].unique():
                topic_data = df_hist[df_hist["topic"] == topic]
                fig.add_trace(
                    go.Scatter(
                        x=topic_data["intento"],
                        y=topic_data["elo"],
                        mode="lines+markers",
                        name=topic,
                        line=dict(width=2),
                    )
                )
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Secuencia de Ejercicios",
                yaxis_title="Nivel ELO",
                legend=dict(bgcolor="rgba(38,39,48,0.8)", bordercolor="gray"),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.write("Sin datos históricos.")

        st.markdown("---")
        st.subheader("🧠 Asistente Virtual Inteligente")
        st.write(
            "Genera un diagnóstico personalizado con tus fortalezas, áreas a mejorar y puntos críticos."
        )

        _REC_META = [
            ("💪", "Fortalezas", "Qué estás haciendo bien — sigue así"),
            ("⚡", "Por mejorar", "Áreas aceptables con potencial de crecimiento"),
            ("🎯", "Áreas críticas", "Debilidades que necesitan atención urgente"),
        ]

        _rec_help = (
            None if st.session_state.ai_available else "IA no disponible en este entorno demo"
        )
        if st.button(
            "✨ Generar Recomendaciones de Estudio",
            disabled=not st.session_state.ai_available,
            help=_rec_help,
        ):
            try:
                with st.spinner("Analizando patrones de aprendizaje..."):
                    recent_attempts = st.session_state.db.get_attempts_for_ai(
                        st.session_state.user_id
                    )
                    current_elo_val = aggregate_global_elo(st.session_state.vector)
                    _proc_stats = {
                        "count": len(_proc_scores),
                        "avg_score": (
                            (sum(s["score"] for s in _proc_scores) / len(_proc_scores))
                            if _proc_scores
                            else None
                        ),
                        "scores": [s["score"] for s in _proc_scores],
                    }
                    _proc_by_course_student = st.session_state.db.get_procedure_stats_by_course(
                        st.session_state.user_id
                    )
                    recs = analyze_performance_local(
                        recent_attempts,
                        current_elo_val,
                        base_url=st.session_state.ai_url,
                        model_name=st.session_state.model_analysis,
                        api_key=st.session_state.cloud_api_key,
                        provider=st.session_state.get("ai_provider"),
                        procedure_stats=_proc_stats,
                        procedure_stats_by_course=_proc_by_course_student,
                    )
                if isinstance(recs, str) and (
                    recs.startswith("ERROR_401:") or recs.startswith("ERROR_429:")
                ):
                    st.error(recs.split(": ", 1)[1])
                else:
                    st.session_state["study_recs"] = recs if isinstance(recs, list) else []
            except (ConnectionError, TimeoutError):
                st.info("IA no disponible en este momento. Inténtalo más tarde.")
            except Exception as e:
                st.error(f"Error crítico: {str(e)}")

        if st.session_state.get("study_recs") is not None:
            recs = st.session_state["study_recs"]
            if len(recs) == 0:
                st.warning("No hay suficientes datos para generar recomendaciones aún.")
            else:
                _CALLOUT = [st.success, st.info, st.warning]
                for idx, (icon, label, subtitle) in enumerate(_REC_META):
                    rec = recs[idx] if idx < len(recs) else {}
                    with st.container(border=True):
                        st.markdown(f"### {icon} Recomendación #{idx + 1}: {label}")
                        st.caption(subtitle)
                        st.markdown(
                            f"**🔍 Diagnóstico:** {strip_thinking_tags(rec.get('diagnostico', 'N/A'))}"
                        )
                        _CALLOUT[idx](
                            f"**📝 Acción:** {strip_thinking_tags(rec.get('accion', 'N/A'))}"
                        )
                        st.markdown(
                            f"**💡 Justificación:** {strip_thinking_tags(rec.get('justificacion', 'N/A'))}"
                        )
                        ejercicios = rec.get("ejercicios", 0)
                        if ejercicios:
                            st.markdown(f"**🔢 Meta sugerida:** {ejercicios} ejercicios")

    elif mode == "🎓 Mis Cursos":
        st.title("🎓 Mis Cursos")

        _level = st.session_state.education_level or "universidad"
        _level_labels = {
            "universidad": "🎓 Universidad",
            "colegio": "🏫 Colegio",
            "concursos": "🏆 Concursos",
            "semillero": "🏅 Semillero de Matemáticas",
        }
        _level_label = _level_labels.get(_level, "🎓 Universidad")
        st.markdown(f"**Nivel académico:** {_level_label}")
        st.caption("Tu nivel se fijó al registrarte y determina qué cursos puedes ver.")

        _enrolled_ids = {c["id"] for c in _enrolled}

        _came_from_code_btn = st.session_state.pop("welcome_open_code_tab", False)
        if _came_from_code_btn:
            st.info(
                "👇 Haz clic en la pestaña **🔑 Código de invitación** para ingresar el código de tu profesor."
            )

        _tab_explore, _tab_enrolled, _tab_code = st.tabs(
            [
                "🔍 Explorar profesores",
                f"📋 Mis matrículas ({len(_enrolled)})",
                "🔑 Código de invitación",
            ]
        )

        # ── Tab 1: Explorar por profesor ──────────────────────────────────
        with _tab_explore:
            _sem_grade_exp = (
                st.session_state.get("student_grade") if _level == "semillero" else None
            )
            _teachers_data = cached(
                "cache_teachers_groups",
                lambda: repo.get_teachers_with_groups_and_courses(_level, grade=_sem_grade_exp),
            )

            if not _teachers_data:
                st.info(
                    "No hay profesores con grupos disponibles para tu nivel aún. "
                    "Si tu profesor ya creó un grupo, pídele el código de invitación (Tab 🔑)."
                )
            else:
                st.caption(
                    "Elige el profesor de tu preferencia para cada materia y haz clic en **Matricular**."
                )
                for _tch in _teachers_data:
                    st.markdown(f"### 👤 Prof. {_tch['teacher_name']}")
                    for _grp in _tch["groups"]:
                        with st.container(border=True):
                            _tc1, _tc2 = st.columns([5, 1])
                            with _tc1:
                                st.markdown(f"**{_grp['course_name']}**")
                                st.caption(
                                    f"Grupo: {_grp['group_name']} · {_grp['student_count']} estudiante(s) matriculado(s)"
                                )
                            with _tc2:
                                if _grp["course_id"] in _enrolled_ids:
                                    st.markdown("✅ Matriculado")
                                else:
                                    if st.button(
                                        "Matricular",
                                        key=f"enroll_tch_{_grp['group_id']}",
                                        type="primary",
                                    ):
                                        repo.enroll_user(
                                            st.session_state.user_id,
                                            _grp["course_id"],
                                            _grp["group_id"],
                                        )
                                        invalidate_cache(
                                            "cache_enrollments", "cache_teachers_groups"
                                        )
                                        st.session_state.welcome_dismissed = True
                                        st.rerun()

        # ── Tab 2: Mis matrículas ──────────────────────────────────────────
        with _tab_enrolled:
            if not _enrolled:
                st.info(
                    "Aún no estás matriculado en ningún curso. Ve a **Explorar profesores** para comenzar."
                )
            else:
                st.caption(
                    "Puedes desmatricularte y volver a matricularte con otro profesor cuando quieras."
                )
                for _ec in _enrolled:
                    with st.container(border=True):
                        _ec1, _ec2 = st.columns([5, 1])
                        with _ec1:
                            st.markdown(f"**{_ec['name']}**")
                            _grp_label = _ec.get("group_name", "")
                            _is_cross = _ec.get("block") != _student_block
                            _cap = (
                                f"Grupo: {_grp_label}" if _grp_label else f"Bloque: {_ec['block']}"
                            )
                            if _is_cross:
                                _cap += " · 📌 Acceso especial"
                            st.caption(_cap)
                        with _ec2:
                            if st.button("Desmatricular", key=f"unenroll_tab_{_ec['id']}"):
                                repo.unenroll_user(st.session_state.user_id, _ec["id"])
                                invalidate_cache("cache_enrollments", "cache_teachers_groups")
                                st.session_state.pop("current_question", None)
                                st.session_state.pop("selected_course", None)
                                st.rerun()

        # ── Tab 3: Código de invitación ────────────────────────────────────
        with _tab_code:
            st.markdown(
                "Si tu profesor te compartió un código, ingrésalo aquí para unirte directamente a su grupo."
            )
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
                        st.session_state["code_group_found"] = _found
                    else:
                        st.session_state.pop("code_group_found", None)
                        st.error("Código no encontrado. Verifica que esté escrito correctamente.")
                else:
                    st.warning("El código debe tener al menos 4 caracteres.")

            _cg = st.session_state.get("code_group_found")
            if _cg:
                if _cg["course_id"] in _enrolled_ids:
                    st.warning(
                        f"Ya estás matriculado en **{_cg['course_name']}**. Si quieres cambiar de profesor, desmatricúlate primero desde la pestaña 📋."
                    )
                else:
                    st.success(
                        f"✅ Grupo encontrado\n\n"
                        f"**Curso:** {_cg['course_name']}  \n"
                        f"**Grupo:** {_cg['group_name']}  \n"
                        f"**Profesor:** {_cg['teacher_name']}"
                    )
                    if _cg.get("block") and _cg["block"] != _student_block:
                        st.info(
                            "📌 Este curso es de un nivel diferente al tuyo. Tu profesor te ha dado acceso especial — podrás practicarlo junto a tus cursos normales."
                        )
                    if st.button(
                        "Confirmar matrícula", key="btn_confirm_code_enroll", type="primary"
                    ):
                        repo.enroll_user(
                            st.session_state.user_id, _cg["course_id"], _cg["group_id"]
                        )
                        invalidate_cache("cache_enrollments", "cache_teachers_groups")
                        st.session_state.pop("code_group_found", None)
                        st.session_state.welcome_dismissed = True
                        st.rerun()

    # ── MODO: Centro de Feedback (solo lectura) ───────────────────────────
    elif mode.startswith("💬 Feedback"):
        # T4b: al entrar al centro de feedback, marcar todas las revisadas como vistas
        st.session_state.fb_seen_ids |= _reviewed_ids

        st.title("💬 Centro de Feedback")
        st.caption(
            "Historial de tus entregas de procedimiento y retroalimentación recibida. Solo lectura."
        )

        _fb_rows = repo.get_student_feedback_history(st.session_state.user_id)

        if not _fb_rows:
            st.info(
                "Aún no tienes entregas de procedimiento. Envía tu primer procedimiento desde el modo Practicar."
            )
        else:
            for _fb in _fb_rows:
                _item_label = _fb.get("item_short") or _fb.get("item_id", "—")
                _date_label = str(_fb.get("submitted_at") or "—")[:16]
                _status = _fb.get("status", "pending")

                _status_map = {
                    "pending": "🟡 Pendiente",
                    "PENDING_TEACHER_VALIDATION": "🟠 Esperando validación docente",
                    "VALIDATED_BY_TEACHER": "🟢 Validado por docente",
                    "reviewed": "🟢 Revisado",
                }
                _status_label = _status_map.get(_status, f"⚪ {_status}")

                with st.expander(f"📄 {_item_label}… — {_date_label} — {_status_label}"):
                    _ai_score = _fb.get("ai_proposed_score")

                    _final = _fb.get("final_score")
                    if _final is None:
                        _final = _fb.get("teacher_score")
                    if _final is None:
                        _legacy = _fb.get("procedure_score")
                        if _legacy is not None:
                            _final = _legacy * 20.0

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

                    _ai_fb = _fb.get("ai_feedback")
                    if _ai_fb:
                        st.markdown("**Retroalimentación IA:**")
                        st.info(_ai_fb)

                    _tch_fb = _fb.get("teacher_feedback")
                    if _tch_fb:
                        st.markdown("**Comentario del docente:**")
                        st.success(_tch_fb)

                    if not _ai_fb and not _tch_fb:
                        st.caption("Sin comentarios aún.")

                    _stor_url = _fb.get("storage_url")
                    _img_path = _fb.get("procedure_image_path")
                    _fb_img_shown = False
                    if _stor_url:
                        _fb_img_bytes = repo.resolve_storage_image(_stor_url)
                        if _fb_img_bytes:
                            st.markdown("**Archivo enviado:**")
                            st.image(
                                _fb_img_bytes, caption="Procedimiento enviado", width="stretch"
                            )
                            _fb_img_shown = True
                    if not _fb_img_shown and _img_path and os.path.isfile(_img_path):
                        st.markdown("**Archivo enviado:**")
                        st.image(_img_path, caption="Procedimiento enviado", width="stretch")

                    _fb_img_path = _fb.get("feedback_image_path")
                    if _fb_img_path and os.path.isfile(_fb_img_path):
                        st.markdown("**Corrección del docente:**")
                        st.image(_fb_img_path, caption="Archivo corregido", width="stretch")
