"""
Genera instrucciones_estudiantes.png — handout para impartir el primer día
con las instrucciones de registro de estudiantes en LevelUp-ELO.

Estilo: paleta V2 (fondo oscuro, acento morado).
Formato: 1200x1800 portrait, ideal para proyector + impresión carta.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Paleta V2
BG = (10, 10, 15)  # #0A0A0F fondo
SURFACE = (24, 24, 35)  # #181823 superficie cards (un tono más claro que #12121A)
SURFACE2 = (35, 35, 50)  # #232332 superficie nested
ACCENT = (108, 99, 255)  # #6C63FF acento (morado LevelUp)
ACCENT2 = (155, 144, 255)  # acento claro
SUCCESS = (34, 197, 94)  # #22C55E verde
WARNING = (245, 158, 11)  # #F59E0B ámbar
TEXT = (241, 245, 249)  # #F1F5F9 texto principal
TEXT2 = (148, 163, 184)  # #94A3B8 texto secundario
TEXT3 = (100, 116, 139)  # texto terciario
BORDER = (40, 44, 60)

W, H = 1200, 1580
MARGIN = 60

FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


F_TITLE = font("segoeuib.ttf", 64)
F_SUBT = font("segoeui.ttf", 28)
F_H1 = font("segoeuib.ttf", 36)
F_H2 = font("segoeuib.ttf", 26)
F_BODY = font("segoeui.ttf", 22)
F_BODY_B = font("segoeuib.ttf", 22)
F_SMALL = font("segoeui.ttf", 18)
F_URL = font("segoeuib.ttf", 38)
F_MONO = font("consola.ttf", 22)  # Consolas monoespaciada
F_NUM = font("segoeuib.ttf", 32)


def rounded(draw: ImageDraw.ImageDraw, xy, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_centered(draw, xy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((xy[0] - tw // 2, xy[1]), text, font=font, fill=fill)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ── HEADER: banda morada con gradiente sutil ──────────────────────────
    header_h = 220
    for y in range(header_h):
        t = y / header_h
        r = int(108 * (1 - t * 0.3))
        g = int(99 * (1 - t * 0.3))
        b = int(255 * (1 - t * 0.4))
        d.line([(0, y), (W, y)], fill=(r, g, b))

    # Logo placeholder + título
    text_centered(d, (W // 2, 40), "LevelUp-ELO", F_TITLE, (255, 255, 255))
    text_centered(d, (W // 2, 130), "Plataforma de práctica adaptativa", F_SUBT, (220, 220, 255))
    text_centered(
        d, (W // 2, 168), "Instrucciones de registro · Estudiantes", F_SUBT, (200, 200, 230)
    )

    y = header_h + 50

    # ── URL destacada ─────────────────────────────────────────────────────
    url_box_h = 130
    rounded(d, (MARGIN, y, W - MARGIN, y + url_box_h), 16, fill=SURFACE, outline=ACCENT, width=3)
    text_centered(d, (W // 2, y + 18), "Entra aquí desde tu celular o computador", F_SMALL, TEXT2)
    text_centered(d, (W // 2, y + 50), "luislevelupelo.vercel.app", F_URL, ACCENT2)
    text_centered(
        d, (W // 2, y + 102), "Funciona en Chrome, Safari, Firefox y Edge", F_SMALL, TEXT3
    )
    y += url_box_h + 40

    # ── PASOS DE REGISTRO ─────────────────────────────────────────────────
    d.text((MARGIN, y), "Pasos para registrarte", font=F_H1, fill=TEXT)
    y += 60

    steps = [
        ("Abre la URL en tu navegador", "Verás la pantalla de inicio de sesión."),
        ("Toca o haz clic en  «Regístrate»", "Está debajo del botón azul de «Iniciar sesión»."),
        ("Elige tu rol: Estudiante", "Luego toca «Siguiente»."),
        (
            "Completa el formulario",
            "Usuario, contraseña, nivel educativo (y grado si eres semillero).",
        ),
        ("Toca «Registrarse»", "No requiere aprobación — entras directo a practicar."),
        ("Inicia sesión con tu usuario y contraseña", "Bienvenido a la sala de práctica."),
    ]

    for i, (title, sub) in enumerate(steps, 1):
        step_h = 70
        # círculo morado con número
        cx, cy = MARGIN + 30, y + 18
        d.ellipse((cx - 25, cy - 5, cx + 25, cy + 45), fill=ACCENT)
        text_centered(d, (cx, cy + 1), str(i), F_NUM, (255, 255, 255))
        # textos
        d.text((MARGIN + 80, y + 6), title, font=F_BODY_B, fill=TEXT)
        d.text((MARGIN + 80, y + 38), sub, font=F_SMALL, fill=TEXT2)
        y += step_h

    y += 30

    # ── REGLAS USUARIO + CONTRASEÑA ─────────────────────────────────────
    d.text((MARGIN, y), "Reglas para tu cuenta", font=F_H1, fill=TEXT)
    y += 60

    card_w = (W - 2 * MARGIN - 30) // 2
    card_h = 290

    # CARD USUARIO
    rounded(d, (MARGIN, y, MARGIN + card_w, y + card_h), 14, fill=SURFACE, outline=BORDER, width=2)
    d.text((MARGIN + 25, y + 20), "Usuario", font=F_H2, fill=ACCENT2)

    user_lines = [
        ("• 3 a 50 caracteres", TEXT, F_BODY),
        ("• Sin espacios", TEXT, F_BODY),
        ("• Único en la plataforma", TEXT, F_BODY),
        ("", TEXT, F_BODY),
        ("Ejemplos:", TEXT2, F_SMALL),
        ("  juan_perez_9", SUCCESS, F_MONO),
        ("  maria_g_11a", SUCCESS, F_MONO),
    ]
    ly = y + 65
    for line, color, f in user_lines:
        d.text((MARGIN + 25, ly), line, font=f, fill=color)
        ly += 30

    # CARD CONTRASEÑA
    cx2 = MARGIN + card_w + 30
    rounded(d, (cx2, y, cx2 + card_w, y + card_h), 14, fill=SURFACE, outline=BORDER, width=2)
    d.text((cx2 + 25, y + 20), "Contraseña", font=F_H2, fill=ACCENT2)

    pass_lines = [
        ("• Mínimo 6 caracteres", TEXT, F_BODY),
        ("• Cualquier combinación válida", TEXT, F_BODY),
        ("• Recuérdala — no se recupera", WARNING, F_BODY),
        ("", TEXT, F_BODY),
        ("Sugerencia:", TEXT2, F_SMALL),
        ("  levelup2026", SUCCESS, F_MONO),
        ("  (cámbiala luego si quieres)", TEXT3, F_SMALL),
    ]
    ly = y + 65
    for line, color, f in pass_lines:
        d.text((cx2 + 25, ly), line, font=f, fill=color)
        ly += 30

    y += card_h + 30

    # ── TIPS / NOTAS ────────────────────────────────────────────────────
    tips_box_h = 175
    rounded(d, (MARGIN, y, W - MARGIN, y + tips_box_h), 14, fill=SURFACE2, outline=ACCENT, width=2)
    d.text((MARGIN + 25, y + 18), "Importante", font=F_H2, fill=ACCENT2)

    tips = [
        "Anota tu usuario y contraseña en un lugar seguro.",
        "El correo es opcional, pero ayuda si olvidas tu cuenta.",
        "No compartas tu contraseña con nadie.",
    ]
    ly = y + 65
    for tip in tips:
        # bullet morado
        d.ellipse((MARGIN + 25, ly + 10, MARGIN + 33, ly + 18), fill=ACCENT)
        d.text((MARGIN + 45, ly), tip, font=F_BODY, fill=TEXT)
        ly += 32

    y += tips_box_h + 25

    # ── FOOTER ──────────────────────────────────────────────────────────
    footer_y = H - 40
    text_centered(
        d,
        (W // 2, footer_y),
        "LevelUp-ELO · Plataforma desarrollada por Luis J. Rubio",
        F_SMALL,
        TEXT3,
    )

    out = Path("instrucciones_estudiantes.png")
    img.save(out, "PNG", optimize=True)
    print(f"OK -> {out.resolve()}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
