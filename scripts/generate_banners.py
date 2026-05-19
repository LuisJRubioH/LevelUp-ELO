"""
Generador de banners pixel-art para los cursos sin banner.

Estrategia híbrida:
  1. Dibujar canvas pequeño (256×112 px, ratio 16:7) con montañas, estrellas
     y título chunky → upscalear con NEAREST a 1536×672 para conservar el
     look pixelado del bloque.
  2. Renderizar la fórmula matemática con matplotlib mathtext (LaTeX) a la
     resolución final, con anti-aliasing limpio. Se compone encima del
     canvas pixelado para que las expresiones sean legibles.

Esto separa el estilo (pixel-art en montañas + título) del contenido
matemático (LaTeX nítido), evitando los caracteres Unicode rotos del
intento anterior (∫, ∂, →, ², θ con fuente Consolas).
"""

import io
import os
import random
from PIL import Image, ImageDraw, ImageFont

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import rcParams  # noqa: E402

# Tipografía matemática serif (similar a Computer Modern).
rcParams["mathtext.fontset"] = "stix"
rcParams["mathtext.default"] = "regular"

OUT_DIR = "frontend/public/banners"
CANVAS_W, CANVAS_H = 256, 112  # 16:7 (aprox) — quedará pixelado al upscalear
SCALE = 6
FINAL_W, FINAL_H = CANVAS_W * SCALE, CANVAS_H * SCALE


def find_font(size: int) -> ImageFont.ImageFont:
    """Busca una fuente bitmap-friendly del sistema."""
    candidates = [
        "C:/Windows/Fonts/consolab.ttf",  # Consolas Bold
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",  # Courier New
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def lighten(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    r, g, b = rgb
    return (
        min(255, int(r + (255 - r) * factor)),
        min(255, int(g + (255 - g) * factor)),
        min(255, int(b + (255 - b) * factor)),
    )


def darken(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    r, g, b = rgb
    return (
        max(0, int(r * (1 - factor))),
        max(0, int(g * (1 - factor))),
        max(0, int(b * (1 - factor))),
    )


def draw_stars(draw: ImageDraw.ImageDraw, color: tuple[int, int, int], seed: int):
    """Esparce estrellas/destellos pixelados aleatorios en el cielo."""
    rnd = random.Random(seed)
    for _ in range(40):
        x = rnd.randint(2, CANVAS_W - 3)
        y = rnd.randint(2, int(CANVAS_H * 0.55))
        # Estrella pequeña: 1×1, ocasionalmente 2×2 con +
        size = rnd.choice([1, 1, 1, 2])
        if size == 1:
            draw.point((x, y), fill=color)
        else:
            draw.point((x, y), fill=color)
            draw.point((x + 1, y), fill=color)
            draw.point((x, y + 1), fill=color)
            draw.point((x - 1, y), fill=color)
            draw.point((x, y - 1), fill=color)


def draw_mountains(
    draw: ImageDraw.ImageDraw,
    base_color: tuple[int, int, int],
    seed: int,
):
    """Dibuja siluetas de montañas chunky pixeladas en la parte inferior.

    Steps grandes (cada 4-6 px) para que al upscalear con NEAREST los picos
    queden visibles como bloques claros (no líneas suaves).
    """
    rnd = random.Random(seed)
    light = lighten(base_color, 0.22)
    mid = base_color
    dark = darken(base_color, 0.30)

    # Banda inferior comienza a 60% de altura
    horizon = int(CANVAS_H * 0.62)
    step_w = 4  # ancho de cada "columna" de la silueta

    def make_silhouette(top_y: int, amp: int, freq: float) -> list[tuple[int, int]]:
        pts = []
        y = top_y
        for x in range(0, CANVAS_W + step_w, step_w):
            if rnd.random() < freq:
                delta = rnd.choice([-amp, -amp, -1, 1, amp, amp])
                y = max(top_y - amp * 2, min(CANVAS_H - 1, y + delta))
            pts.append((x, y))
        return pts

    # Capa 1 (más atrás, más alta y oscura)
    layer1 = make_silhouette(top_y=horizon + 4, amp=4, freq=0.35)
    draw.polygon([(0, CANVAS_H)] + layer1 + [(CANVAS_W, CANVAS_H)], fill=dark)

    # Capa 2 (medio)
    layer2 = make_silhouette(top_y=horizon + 12, amp=3, freq=0.30)
    draw.polygon([(0, CANVAS_H)] + layer2 + [(CANVAS_W, CANVAS_H)], fill=mid)

    # Capa 3 (frente, más clara y plana)
    layer3 = make_silhouette(top_y=horizon + 22, amp=2, freq=0.25)
    draw.polygon([(0, CANVAS_H)] + layer3 + [(CANVAS_W, CANVAS_H)], fill=light)

    # Algunas chispas (sparkles) en las montañas
    for _ in range(8):
        x = rnd.randint(4, CANVAS_W - 5)
        y = rnd.randint(horizon + 4, CANVAS_H - 3)
        sparkle = lighten(base_color, 0.50)
        # cruz de 5 pixeles
        draw.point((x, y), fill=sparkle)
        draw.point((x + 1, y), fill=sparkle)
        draw.point((x - 1, y), fill=sparkle)
        draw.point((x, y + 1), fill=sparkle)
        draw.point((x, y - 1), fill=sparkle)


def draw_text_centered(
    img: Image.Image,
    text: str,
    y_ratio: float,
    font_size: int,
    color: tuple[int, int, int],
):
    """Dibuja texto centrado horizontalmente, anti-alias OFF (canvas pequeño)."""
    font = find_font(font_size)
    tmp = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    dtmp = ImageDraw.Draw(tmp)
    bbox = dtmp.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (CANVAS_W - tw) // 2 - bbox[0]
    y = int(CANVAS_H * y_ratio) - th // 2 - bbox[1]
    dtmp.text((x, y), text, font=font, fill=color + (255,))
    img.alpha_composite(tmp)


def render_latex_overlay(
    formula: str,
    target_width: int,
    target_height: int,
    fontsize: int = 38,
    color: str = "#FFFFFF",
) -> Image.Image:
    """
    Renderiza una fórmula matemática con matplotlib mathtext a un PNG RGBA
    transparente con el tamaño exacto solicitado. Útil para componer sobre
    el banner pixelado ya upscalado.
    """
    # Figure DPI 100 → figsize en pulgadas = pixels/100
    fig = plt.figure(figsize=(target_width / 100, target_height / 100), dpi=100)
    fig.patch.set_alpha(0.0)

    # Backdrop semi-transparente para legibilidad sobre cualquier fondo.
    bbox = dict(
        boxstyle="round,pad=0.55",
        facecolor=(0, 0, 0, 0.45),
        edgecolor=(1, 1, 1, 0.15),
        linewidth=0.8,
    )
    fig.text(
        0.5,
        0.5,
        f"${formula}$",
        ha="center",
        va="center",
        color=color,
        fontsize=fontsize,
        bbox=bbox,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=100, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA").resize((target_width, target_height), Image.LANCZOS)


def make_banner(
    course_id: str,
    title_line1: str | None = None,
    title_line2: str | None = None,
    formula_text: str | None = None,
    bg_hex: str | None = None,
    seed: int = 0,
    *,
    latex: str | None = None,
    latex_fontsize: int = 38,
    base_image: str | None = None,
    overlay_y_ratio: float = 0.50,
    overlay_h_ratio: float = 0.45,
):
    """
    Genera un banner y lo guarda en frontend/public/banners/<course_id>.png.

    Dos modos:
      (a) Generativo: dibuja canvas pixel-art (mountains + stars + título) y
          opcionalmente compone LaTeX encima. Requiere bg_hex y title_*.
      (b) Overlay: carga un banner base existente (`base_image`) y le
          superpone una fórmula LaTeX. Preserva el tamaño y arte originales.
          Útil para banners user-supplied a los que solo queremos agregar la
          ecuación.
    """
    if base_image is not None:
        # Modo (b): cargar imagen base, normalizar a 16:7 (1536x672) y luego
        # añadir overlay LaTeX. La normalización es importante porque el
        # componente React renderiza con aspect-[16/7] + object-cover, así
        # que cualquier imagen con otro ratio se recorta arriba/abajo y la
        # fórmula se pierde.
        with Image.open(base_image) as src:
            raw = src.convert("RGBA").copy()
        # Crop centrado al ratio target, luego resize a (FINAL_W, FINAL_H).
        target_ratio = FINAL_W / FINAL_H
        src_w, src_h = raw.size
        src_ratio = src_w / src_h
        if src_ratio > target_ratio:
            # Más ancha que target — recortar a los lados
            new_w = int(src_h * target_ratio)
            offset = (src_w - new_w) // 2
            raw = raw.crop((offset, 0, offset + new_w, src_h))
        elif src_ratio < target_ratio:
            # Más alta que target — recortar arriba/abajo. Como los títulos
            # suelen estar centrados verticalmente, esto es no destructivo.
            new_h = int(src_w / target_ratio)
            offset = (src_h - new_h) // 2
            raw = raw.crop((0, offset, src_w, offset + new_h))
        final = raw.resize((FINAL_W, FINAL_H), Image.LANCZOS)
        canvas_w, canvas_h = FINAL_W, FINAL_H
    else:
        # Modo (a): generar canvas pixel-art.
        assert (
            bg_hex is not None and title_line1 is not None
        ), "Modo generativo requiere bg_hex y title_line1"
        bg = hex_to_rgb(bg_hex)
        img = Image.new("RGBA", (CANVAS_W, CANVAS_H), bg + (255,))
        draw = ImageDraw.Draw(img)

        star_color = lighten(bg, 0.45)
        draw_stars(draw, star_color, seed=seed)
        draw_mountains(draw, base_color=bg, seed=seed + 1)

        if title_line2:
            draw_text_centered(img, title_line1, 0.18, font_size=22, color=(255, 255, 255))
            draw_text_centered(img, title_line2, 0.34, font_size=22, color=(255, 255, 255))
            title_height_ratio = 0.50
        else:
            draw_text_centered(img, title_line1, 0.24, font_size=28, color=(255, 255, 255))
            title_height_ratio = 0.48

        if latex is None and formula_text:
            draw_text_centered(
                img,
                formula_text,
                (title_height_ratio + 0.95) / 2,
                font_size=12,
                color=(255, 255, 255),
            )

        final = img.resize((FINAL_W, FINAL_H), Image.NEAREST).convert("RGBA")
        canvas_w, canvas_h = FINAL_W, FINAL_H

    # Componer LaTeX (si aplica) sobre el banner upscalado / base.
    if latex is not None:
        overlay_w = int(canvas_w * 0.84)
        overlay_h = int(canvas_h * overlay_h_ratio)
        overlay_x = (canvas_w - overlay_w) // 2
        overlay_y = int(canvas_h * overlay_y_ratio)

        latex_img = render_latex_overlay(latex, overlay_w, overlay_h, fontsize=latex_fontsize)
        final.alpha_composite(latex_img, dest=(overlay_x, overlay_y))

    out_path = os.path.join(OUT_DIR, f"{course_id}.png")
    final.convert("RGB").save(out_path, optimize=True)
    print(f"  + {out_path}  ({canvas_w}x{canvas_h})")


# ── Definición de banners ────────────────────────────────────────────────────

# Cada entrada es un dict con las opciones que recibe make_banner.
# Los cursos matemáticos usan `latex` (mathtext); DIAN/SENA usan `formula_text`.
BANNERS: list[dict] = [
    # Cálculo Diferencial — definición clásica de derivada
    {
        "course_id": "calculo_diferencial",
        "title_line1": "Cálculo",
        "title_line2": "Diferencial",
        "formula_text": None,
        "bg_hex": "#1E5F4E",
        "seed": 11,
        "latex": r"f'(x) = \lim_{h \to 0} \dfrac{f(x+h) - f(x)}{h}",
        "latex_fontsize": 34,
    },
    # Cálculo Integral — teorema fundamental del cálculo
    {
        "course_id": "calculo_integral",
        "title_line1": "Cálculo",
        "title_line2": "Integral",
        "formula_text": None,
        "bg_hex": "#0E5F7A",
        "seed": 22,
        "latex": r"\int_{a}^{b} f(x)\, dx = F(b) - F(a)",
        "latex_fontsize": 42,
    },
    # Varias variables — regla de la cadena multivariable
    {
        "course_id": "calculo_varias_variables",
        "title_line1": "Varias",
        "title_line2": "Variables",
        "formula_text": None,
        "bg_hex": "#5A2A8F",
        "seed": 33,
        "latex": (
            r"\dfrac{\partial z}{\partial t} = "
            r"\dfrac{\partial z}{\partial x}\dfrac{\partial x}{\partial t} + "
            r"\dfrac{\partial z}{\partial y}\dfrac{\partial y}{\partial t}"
        ),
        "latex_fontsize": 28,
    },
    # Ecuaciones diferenciales — transformada de Laplace
    {
        "course_id": "ecuaciones_diferenciales",
        "title_line1": "Ecuaciones",
        "title_line2": "Diferenciales",
        "formula_text": None,
        "bg_hex": "#8F4500",
        "seed": 44,
        "latex": r"\mathcal{L}\{f(t)\} = \int_{0}^{\infty} f(t)\, e^{-st}\, dt",
        "latex_fontsize": 36,
    },
    # Álgebra Lineal — ecuación de autovalores (más limpia que la 2x2)
    {
        "course_id": "algebra_lineal",
        "title_line1": "Álgebra",
        "title_line2": "Lineal",
        "formula_text": None,
        "bg_hex": "#2C3E8F",
        "seed": 55,
        "latex": r"A\,\mathbf{v} = \lambda\, \mathbf{v}",
        "latex_fontsize": 56,
    },
    # Trigonometría — identidad pitagórica
    {
        "course_id": "trigonometria",
        "title_line1": "Trigonometría",
        "title_line2": None,
        "formula_text": None,
        "bg_hex": "#10708F",
        "seed": 66,
        "latex": r"\sin^{2}\theta + \cos^{2}\theta = 1",
        "latex_fontsize": 48,
    },
    # Concursos: sin fórmula matemática, texto plano descriptivo
    {
        "course_id": "DIAN",
        "title_line1": "Concurso",
        "title_line2": "DIAN",
        "formula_text": "Aduanas · Tributaria",
        "bg_hex": "#5C7A2E",
        "seed": 77,
        "latex": None,
    },
    {
        "course_id": "SENA",
        "title_line1": "Concurso",
        "title_line2": "SENA",
        "formula_text": "Profesional 10",
        "bg_hex": "#7A2E2E",
        "seed": 88,
        "latex": None,
    },
    # ── Overlays sobre banners user-supplied (preservando arte original) ────
    # Aritmética básica: regla de exponentes (producto de potencias).
    {
        "course_id": "aritmetica",
        "base_image": "frontend/public/banners/_originals/aritmetica.png",
        "latex": r"a^{m} \cdot a^{n} = a^{m+n}",
        "latex_fontsize": 56,
        "overlay_y_ratio": 0.55,
        "overlay_h_ratio": 0.40,
    },
    # Álgebra básica: fórmula general (cuadrática) — la fórmula icónica.
    {
        "course_id": "algebra",
        "base_image": "frontend/public/banners/_originals/algebra.png",
        "latex": r"x = \dfrac{-b \pm \sqrt{b^{2} - 4ac}}{2a}",
        "latex_fontsize": 38,
        "overlay_y_ratio": 0.55,
        "overlay_h_ratio": 0.40,
    },
    # Geometría: teorema de Pitágoras.
    {
        "course_id": "geometria",
        "base_image": "frontend/public/banners/_originals/geometria.png",
        "latex": r"a^{2} + b^{2} = c^{2}",
        "latex_fontsize": 60,
        "overlay_y_ratio": 0.55,
        "overlay_h_ratio": 0.40,
    },
    # Lógica y conjuntos: ley de De Morgan.
    {
        "course_id": "logica",
        "base_image": "frontend/public/banners/_originals/logica.png",
        "latex": r"\overline{A \cup B} = \overline{A} \cap \overline{B}",
        "latex_fontsize": 48,
        "overlay_y_ratio": 0.55,
        "overlay_h_ratio": 0.40,
    },
    # Conteo y combinatoria: número de combinaciones C(n,k).
    # Título original de 3 líneas (Conteo / y / Combinatoria) — overlay
    # más bajo para no solaparse con el bloque de título.
    {
        "course_id": "conteo_combinatoria",
        "base_image": "frontend/public/banners/_originals/conteo_combinatoria.png",
        "latex": r"\binom{n}{k} = \dfrac{n!}{k!\,(n-k)!}",
        "latex_fontsize": 38,
        "overlay_y_ratio": 0.72,
        "overlay_h_ratio": 0.26,
    },
    # Probabilidad: teorema de Bayes (mismo caso: título de 3 líneas).
    {
        "course_id": "probabilidad",
        "base_image": "frontend/public/banners/_originals/probabilidad.png",
        "latex": r"P(A \mid B) = \dfrac{P(B \mid A)\, P(A)}{P(B)}",
        "latex_fontsize": 36,
        "overlay_y_ratio": 0.72,
        "overlay_h_ratio": 0.26,
    },
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generando {len(BANNERS)} banners en {OUT_DIR}/ ...")
    for spec in BANNERS:
        make_banner(**spec)


if __name__ == "__main__":
    main()
