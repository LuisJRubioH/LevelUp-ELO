"""
src/interface/streamlit/views/teacher_view.py
=============================================
Vista del panel del profesor.
Código movido exactamente desde app.py líneas 914-1871.
"""
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import src.infrastructure.external_api.ai_client as ai_mod

from src.interface.streamlit.assets import _get_logo
from src.interface.streamlit.state import cached, get_rank, logout
from src.utils import strip_thinking_tags


def render_teacher():
    """Punto de entrada del panel del profesor."""
    repo = st.session_state.db

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
