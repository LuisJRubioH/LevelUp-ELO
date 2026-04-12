"""
src/interface/streamlit/state.py
=================================
Gestión centralizada del estado de sesión y utilidades compartidas.

Incluye:
- cached() / invalidate_cache()  — caché ligero en session_state
- get_rank()                      — conversión ELO → nivel
- login() / logout()              — gestión de sesión con cookies
"""
import time
import streamlit as st


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


# ── Tabla de rangos ELO ───────────────────────────────────────────────────────
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


# ── Gestión de sesión ─────────────────────────────────────────────────────────
def login():
    st.session_state.logged_in = True
    st.session_state.session_start_time = time.time()


def logout():
    """Limpia la sesión y redirige al login."""
    _cm = st.session_state.get('_cookie_manager')
    if _cm:
        try:
            token = _cm.get("elo_auth_token")
            if token:
                _repo = st.session_state.get('db')
                if _repo:
                    _repo.delete_session(token)
                _cm.delete("elo_auth_token")
        except Exception:
            pass
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()
