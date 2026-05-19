"""
Generador de banners pixel-art para los cursos sin banner.

Estrategia: dibujar en un canvas pequeño (256×112 px, ratio 16:7), luego
upscalear con NEAREST a 1536×672 para preservar el look pixelado del bloque.

Cada banner tiene:
  - Fondo de color temático
  - Montañas pixeladas en la parte inferior
  - Estrellas/destellos esparcidos
  - Título del curso (chunky font)
  - Fórmula representativa abajo
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont

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
    """Dibuja texto centrado horizontalmente, anti-alias OFF."""
    # Renderizar texto en imagen aparte sin antialias, luego pegar
    font = find_font(font_size)
    tmp = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    dtmp = ImageDraw.Draw(tmp)
    bbox = dtmp.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (CANVAS_W - tw) // 2 - bbox[0]
    y = int(CANVAS_H * y_ratio) - th // 2 - bbox[1]
    dtmp.text((x, y), text, font=font, fill=color + (255,))
    # Quantizar a 2 niveles (sin gris medio) para look pixel-art
    img.alpha_composite(tmp)


def make_banner(
    course_id: str,
    title_line1: str,
    title_line2: str | None,
    formula: str,
    bg_hex: str,
    seed: int = 0,
):
    """Genera un banner pixel-art y lo guarda en frontend/public/banners/<course_id>.png."""
    bg = hex_to_rgb(bg_hex)
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), bg + (255,))
    draw = ImageDraw.Draw(img)

    # Estrellas en el cielo
    star_color = lighten(bg, 0.45)
    draw_stars(draw, star_color, seed=seed)

    # Montañas abajo
    draw_mountains(draw, base_color=bg, seed=seed + 1)

    # Título (1-2 líneas)
    if title_line2:
        draw_text_centered(img, title_line1, 0.20, font_size=22, color=(255, 255, 255))
        draw_text_centered(img, title_line2, 0.36, font_size=22, color=(255, 255, 255))
        draw_text_centered(img, formula, 0.54, font_size=12, color=(255, 255, 255))
    else:
        draw_text_centered(img, title_line1, 0.26, font_size=28, color=(255, 255, 255))
        draw_text_centered(img, formula, 0.52, font_size=12, color=(255, 255, 255))

    # Upscale con NEAREST para preservar look pixelado
    final = img.resize((FINAL_W, FINAL_H), Image.NEAREST)
    out_path = os.path.join(OUT_DIR, f"{course_id}.png")
    final.convert("RGB").save(out_path, optimize=True)
    print(f"  ✓ {out_path}  ({FINAL_W}×{FINAL_H})")


# ── Definición de banners faltantes ──────────────────────────────────────────

BANNERS = [
    # (course_id, title_line1, title_line2, formula, bg_hex, seed)
    ("calculo_diferencial", "Cálculo", "Diferencial", "f'(x)=lim (f(x+h)-f(x))/h", "#1E5F4E", 11),
    ("calculo_integral", "Cálculo", "Integral", "∫f(x)dx = F(b) - F(a)", "#0E5F7A", 22),
    ("calculo_varias_variables", "Varias", "Variables", "∂z/∂t = ∂z/∂x·∂x/∂t", "#5A2A8F", 33),
    (
        "ecuaciones_diferenciales",
        "Ecuaciones",
        "Diferenciales",
        "F(s) = ∫ f(t) e^(-st) dt",
        "#8F4500",
        44,
    ),
    ("algebra_lineal", "Álgebra", "Lineal", "|a b; c d| = ad - bc", "#2C3E8F", 55),
    ("trigonometria", "Trigonometría", None, "sin²θ + cos²θ = 1", "#10708F", 66),
    ("DIAN", "Concurso", "DIAN", "Aduanas · Tributaria", "#5C7A2E", 77),
    ("SENA", "Concurso", "SENA", "Profesional 10", "#7A2E2E", 88),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generando {len(BANNERS)} banners en {OUT_DIR}/ …")
    for spec in BANNERS:
        make_banner(*spec)


if __name__ == "__main__":
    main()
