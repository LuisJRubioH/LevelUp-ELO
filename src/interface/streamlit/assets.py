"""
src/interface/streamlit/assets.py
===================================
Carga y cache de assets estáticos (logos, GIFs, banners) y estilos CSS globales.
Todos los assets se cargan una sola vez con @st.cache_resource.
"""
import base64
import os
import streamlit as st

# Ruta raíz del proyecto (4 niveles arriba de este archivo:
# assets.py → streamlit/ → interface/ → src/ → LevelUp-ELO/)
BASE_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
_BASE = BASE_PATH  # alias de compatibilidad interna

_LOGO_LIGHT = os.path.join(_BASE, "logo-elo-light.png")
_LOGO_DARK  = os.path.join(_BASE, "logo-elo2-dark.png")


# ── Logos ────────────────────────────────────────────────────────────────────
def _get_theme():
    """Devuelve 'light' o 'dark' según el tema activo de Streamlit."""
    try:
        return st.get_option("theme.base") or "light"
    except Exception:
        return "light"


def get_logo_path() -> str:
    """Devuelve la ruta del logo adecuada al tema actual."""
    return _LOGO_DARK if _get_theme() == "dark" else _LOGO_LIGHT


# Alias para compatibilidad con código que llama _get_logo()
def _get_logo() -> str:
    return get_logo_path()


# ── KatIA image ───────────────────────────────────────────────────────────────
_KATIA_IMG_PATH = os.path.join(_BASE, "KatIA", "katIA.png")


@st.cache_resource
def load_katia_avatar_bytes():
    try:
        with open(_KATIA_IMG_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None


# ── GIFs animados de KatIA ────────────────────────────────────────────────────
_KATIA_GIF_CORRECTO_PATH = os.path.join(_BASE, "KatIA", "correcto_compressed.gif")
_KATIA_GIF_ERRORES_PATH = os.path.join(_BASE, "KatIA", "errores_compressed.gif")


@st.cache_resource
def _load_katia_gif_b64(path: str):
    """Carga un GIF y retorna el tag HTML <img> con base64 para animación."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<img src="data:image/gif;base64,{b64}" width="220" style="border-radius:12px;">'
    except FileNotFoundError:
        return None


def load_katia_gif_html(gif_type: str = "correcto"):
    """
    Retorna el HTML del GIF comprimido de KatIA.
    gif_type: 'correcto' (score >= 91) | 'errores' (score < 91)
    """
    path = _KATIA_GIF_CORRECTO_PATH if gif_type == "correcto" else _KATIA_GIF_ERRORES_PATH
    return _load_katia_gif_b64(path)


# ── Banners pixel art de cursos ───────────────────────────────────────────────
_BANNERS_DIR = os.path.join(_BASE, "Banners")


@st.cache_resource
def _load_course_banners():
    """Carga los banners como base64 y retorna dict {keyword: b64_str}."""
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


def get_banner_for_course(course_name: str):
    """Retorna el base64 del banner que corresponda al nombre del curso, o None."""
    banners = _load_course_banners()
    name_lower = course_name.lower()
    for kw, b64 in banners.items():
        if kw in name_lower:
            return b64
    return None


# Alias de compatibilidad con código de app.py que llama _get_banner_b64()
def _get_banner_b64(course_name: str):
    return get_banner_for_course(course_name)


# ── CSS global ────────────────────────────────────────────────────────────────
def apply_global_css():
    """Aplica los estilos CSS globales de la aplicación. Llamar una vez en app.py."""

    # CSS: radio button seleccionado en verde
    st.markdown("""
<style>
div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"],
div[data-testid="stRadio"] [role="radiogroup"] label div:first-child div {
    border-color: inherit;
}
div[data-testid="stRadio"] [role="radiogroup"] label[aria-checked="true"] div:first-child div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
div[data-testid="stRadio"] [role="radiogroup"] label[aria-checked="true"] > div:first-child > div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
div[data-testid="stRadio"] [role="radiogroup"] label[aria-checked="true"] > div:first-child {
    border-color: #00CC66 !important;
}
div[data-testid="stRadio"] {
    --primary-color: #00CC66;
}
[data-baseweb="radio"] input[type="radio"]:checked ~ div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
[data-baseweb="radio"] input[type="radio"]:checked ~ div::after {
    background-color: #00CC66 !important;
}
.stRadio > div[role="radiogroup"] > label > div:first-child > div {
    border-color: #555 !important;
}
.stRadio > div[role="radiogroup"] > label[aria-checked="true"] > div:first-child > div {
    background-color: #00CC66 !important;
    border-color: #00CC66 !important;
}
</style>
""", unsafe_allow_html=True)

    # CSS principal: tipografía, cards, botones, inputs, tabs
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
