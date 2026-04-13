"""
src/interface/streamlit/views/admin_view.py
==========================================
Vista del panel de administración.
Código movido exactamente desde app.py líneas 671-910.
"""

import streamlit as st

try:
    from psycopg2.extras import RealDictCursor
except ImportError:
    RealDictCursor = None

from src.interface.streamlit.assets import _get_logo
from src.interface.streamlit.state import logout


def render_admin():
    """Punto de entrada del panel de administración."""
    with st.sidebar:
        st.image(_get_logo(), width=180)
        st.write(f"### 🛡️ Admin: **{st.session_state.username}**")
        st.markdown("---")
        if st.button("Cerrar Sesión"):
            logout()

    st.title("🛡️ Panel de Administración")

    # ── Reportes de problemas técnicos ────────────────────────────────────
    _pending_reports = st.session_state.db.get_problem_reports(status="pending")
    if _pending_reports:
        st.subheader(
            f"🔔 Problemas Técnicos — {len(_pending_reports)} pendiente{'s' if len(_pending_reports) != 1 else ''}"
        )
        for _rpt in _pending_reports:
            with st.container(border=True):
                col_rpt_info, col_rpt_btn = st.columns([4, 1])
                with col_rpt_info:
                    st.write(f"**{_rpt['username']}** — {str(_rpt['created_at'])[:16]}")
                    st.caption(_rpt["description"])
                with col_rpt_btn:
                    if st.button("✅ Resuelto", key=f"resolve_report_{_rpt['id']}"):
                        st.session_state.db.mark_problem_resolved(_rpt["id"])
                        st.rerun()
        st.markdown("---")

    # ── Profesores pendientes ──────────────────────────────────────────────
    st.subheader("⏳ Solicitudes de Profesores Pendientes")
    if "cache_pending_teachers" not in st.session_state:
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
                    st.session_state.db.approve_teacher(teacher["id"])
                    st.session_state.pop("cache_pending_teachers", None)
                    st.session_state.pop("cache_approved_teachers", None)
                    st.rerun()
            with col_no:
                if st.button("❌ Rechazar", key=f"reject_{teacher['id']}"):
                    st.session_state.db.reject_teacher(teacher["id"])
                    st.session_state.pop("cache_pending_teachers", None)
                    st.session_state.pop("cache_approved_teachers", None)
                    st.rerun()

    st.markdown("---")

    # ── Profesores activos ─────────────────────────────────────────────────
    st.subheader("✅ Profesores Activos")
    if "cache_approved_teachers" not in st.session_state:
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
                    st.session_state.db.deactivate_user(t["id"])
                    st.session_state.pop("cache_approved_teachers", None)
                    st.session_state.pop("cache_all_students", None)
                    st.rerun()

    # Profesores dados de baja
    conn_t = st.session_state.db.get_connection()
    try:
        cur_t = conn_t.cursor(cursor_factory=RealDictCursor)
        cur_t.execute(
            "SELECT id, username, created_at FROM users WHERE role='teacher' AND active=0 ORDER BY username ASC"
        )
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
                        st.session_state.db.reactivate_user(t["id"])
                        st.session_state.pop("cache_approved_teachers", None)
                        st.session_state.pop("cache_all_students", None)
                        st.rerun()

    st.markdown("---")

    # ── Estudiantes registrados ────────────────────────────────────────────
    st.subheader("🎓 Estudiantes Registrados")
    if "cache_all_students" not in st.session_state:
        st.session_state.cache_all_students = st.session_state.db.get_all_students_admin()
    all_students = st.session_state.cache_all_students
    if not all_students:
        st.info("No hay estudiantes registrados aún.")
    else:
        activos = [s for s in all_students if s["active"]]
        inactivos = [s for s in all_students if not s["active"]]

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
                            st.session_state.db.deactivate_user(s["id"])
                            st.session_state.pop(confirm_key_s, None)
                            st.session_state.pop("cache_all_students", None)
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
                            st.session_state.db.reactivate_user(s["id"])
                            st.session_state.pop("cache_all_students", None)
                            st.rerun()

        st.markdown("---")

        # ── Reasignación de Grupo (Solo Admin) ──────────────────────────────
        st.subheader("📍 Reasignación de Grupo")
        with st.container(border=True):
            col_s, col_g = st.columns(2)

            # Cargar datos necesarios (cached)
            if "cache_all_groups" not in st.session_state:
                st.session_state.cache_all_groups = st.session_state.db.get_all_groups()
            all_groups = st.session_state.cache_all_groups
            # Filtrar solo estudiantes activos para reasignar (usando la lista ya cargada arriba)
            student_options = {s["username"]: s["id"] for s in activos}
            group_options = {f"{g['name']} ({g['teacher_name']})": g["id"] for g in all_groups}
            group_options["[ Ningún Grupo ]"] = None

            with col_s:
                sel_student_name = st.selectbox(
                    "Selecciona Estudiante", list(student_options.keys()), key="reassign_student"
                )
            with col_g:
                sel_group_label = st.selectbox(
                    "Selecciona Nuevo Grupo", list(group_options.keys()), key="reassign_group"
                )

            allow_null = st.checkbox(
                "Permitir dejar sin grupo",
                value=False,
                help="Si se marca, permite asignar '[ Ningún Grupo ]'.",
            )

            st.write("")
            if st.button("🚀 Aplicar Cambio de Grupo", type="primary", use_container_width=True):
                student_id = student_options[sel_student_name]
                new_group_id = group_options[sel_group_label]

                success, message = st.session_state.db.change_student_group(
                    student_id=student_id,
                    new_group_id=new_group_id,
                    admin_id=st.session_state.user_id,
                    allow_null=allow_null,
                )

                if success:
                    st.success(message)
                    st.session_state.pop("cache_all_students", None)
                    st.session_state.pop("cache_all_groups", None)
                    import time

                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("---")

        # ── Gestión de Grupos (Admin) ────────────────────────────────────
        st.subheader("📂 Gestión de Grupos")
        if "cache_all_groups" not in st.session_state:
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
                                    g["id"], st.session_state.user_id
                                )
                                st.session_state.pop(confirm_key, None)
                                if ok:
                                    st.success(msg)
                                    st.session_state.pop("cache_all_groups", None)
                                    st.session_state.pop("cache_all_students", None)
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
