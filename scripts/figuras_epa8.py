"""Reconstruye en Python las figuras de los ítems de Evaluar para Avanzar 8.

Cada pregunta que en el PDF depende de una imagen (gráfica, tabla ilustrada,
pictograma, cuerpo geométrico, árbol) tiene aquí una función que la vuelve a
dibujar. La salida es SVG con fondo blanco en `items/assets/epa8/`.

    python scripts/figuras_epa8.py            # todas
    python scripts/figuras_epa8.py P01 P16    # solo algunas (por sufijo del id)

Convenciones: coma decimal es-CO en los rótulos, sin dependencias fuera de
matplotlib, un builder por figura (nada de DSL genérico).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "items" / "assets" / "epa8"

AZUL = "#4BA3D3"
NARANJA = "#E8792B"
GRIS = "#4A4A4A"
CREMA = "#F7D9B8"

BUILDERS: dict[str, callable] = {}


def figura(nombre: str):
    def deco(fn):
        BUILDERS[nombre] = fn
        return fn

    return deco


def _guardar(fig, nombre: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    destino = OUT / f"{nombre}.svg"
    fig.savefig(destino, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


def _marco(ax):
    """Rejilla suave y ejes limpios, el estilo de las gráficas del cuadernillo."""
    ax.grid(True, color="#CCCCCC", linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def _coma(valores, decimales=2):
    return [f"{v:.{decimales}f}".replace(".", ",").rstrip("0").rstrip(",") for v in valores]


# ── Cuadernillo 1 - 2023 ──────────────────────────────────────────────────────

PERSONAS = [
    ("María", 1.60, 65),
    ("Marta", 1.65, 70),
    ("Juan", 1.75, 75),
    ("Pedro", 1.72, 80),
    ("Luis", 1.80, 79),
]


def _dispersion(ax, puntos):
    for nombre, x, y in puntos:
        ax.plot(x, y, "o", color="#D93A2B", markersize=7)
        ax.annotate(nombre, (x, y), textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.set_xticks([1.60, 1.65, 1.70, 1.75, 1.80])
    ax.set_xticklabels(["1,6", "1,65", "1,7", "1,75", "1,8"])
    ax.set_xlim(1.575, 1.825)
    ax.set_ylim(50, 85)
    ax.set_yticks(range(50, 90, 5))
    ax.set_xlabel("Estatura (m)", fontweight="bold")
    ax.set_ylabel("Peso (kg)", fontweight="bold")
    _marco(ax)


@figura("EPA8-C1-2023-P01_A")
def p2023_01_a():
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    _dispersion(ax, PERSONAS)
    return fig


@figura("EPA8-C1-2023-P01_B")
def p2023_01_b():
    """Distractor: barras con los PESOS rotuladas como estatura."""
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    nombres = ["María", "Marta", "Pedro", "Juan", "Luis"]
    ax.bar(nombres, [65, 70, 75, 80, 80], color=AZUL, width=0.45)
    ax.set_ylim(0, 90)
    ax.set_yticks([0] + list(range(50, 95, 5)))
    ax.set_xlabel("Trabajador", fontweight="bold")
    ax.set_ylabel("Estatura (m)", fontweight="bold")
    _marco(ax)
    return fig


@figura("EPA8-C1-2023-P01_C")
def p2023_01_c():
    """Distractor: solo la estatura, sin relacionar el peso."""
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    nombres = ["María", "Marta", "Juan", "Pedro", "Luis"]
    ax.bar(nombres, [1.60, 1.65, 1.75, 1.72, 1.80], color=AZUL, width=0.35)
    ax.set_ylim(1.5, 1.85)
    ticks = [1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85]
    ax.set_yticks(ticks)
    ax.set_yticklabels(_coma(ticks))
    ax.set_xlabel("Trabajador", fontweight="bold")
    ax.set_ylabel("Estatura (m)", fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    _marco(ax)
    return fig


@figura("EPA8-C1-2023-P01_D")
def p2023_01_d():
    """Distractor: Juan y Pedro intercambiados en el eje de estatura."""
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    _dispersion(
        ax,
        [
            ("María", 1.60, 65),
            ("Marta", 1.65, 70),
            ("Juan", 1.70, 75),
            ("Pedro", 1.75, 80),
            ("Luis", 1.80, 79),
        ],
    )
    return fig


def _arbol(ax, raiz, ramas, titulo=""):
    """Árbol de dos niveles: raíz → 2 nodos → 2 hojas cada uno."""

    def caja(x, y, texto):
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.42, y - 0.13),
                0.84,
                0.26,
                boxstyle="round,pad=0.02",
                facecolor="white",
                edgecolor=GRIS,
                linewidth=1.0,
            )
        )
        ax.text(x, y, texto, ha="center", va="center", fontsize=8.5)

    caja(0.5, 2.0, raiz)
    for i, (medio, hojas) in enumerate(ramas):
        y_medio = 3.1 if i == 0 else 0.9
        caja(2.0, y_medio, medio)
        ax.plot([0.95, 1.55], [2.0, y_medio], color=GRIS, linewidth=1.0)
        for j, hoja in enumerate(hojas):
            y_hoja = y_medio + (0.6 if j == 0 else -0.6)
            caja(3.5, y_hoja, hoja)
            ax.plot([2.45, 3.05], [y_medio, y_hoja], color=GRIS, linewidth=1.0)
    ax.set_xlim(0, 4.1)
    ax.set_ylim(0, 4.0)
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=10, fontweight="bold")


@figura("EPA8-C1-2023-P02")
def p2023_02_mapa():
    """Mapa esquemático del parque: zonas y senderos que las conectan."""
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    zonas = {
        "Piscinas": (1.1, 3.0),
        "Zoológico": (3.1, 3.3),
        "Deportes": (1.0, 1.0),
        "Lago": (2.9, 1.4),
        "Museo": (4.3, 1.1),
    }
    for nombre, (x, y) in zonas.items():
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.55, y - 0.22),
                1.1,
                0.44,
                boxstyle="round,pad=0.03",
                facecolor="white",
                edgecolor=GRIS,
                linewidth=1.2,
            )
        )
        ax.text(x, y, nombre, ha="center", va="center", fontsize=9)
    senderos = [
        ("Museo", "Zoológico"),
        ("Museo", "Lago"),
        ("Zoológico", "Piscinas"),
        ("Zoológico", "Deportes"),
        ("Lago", "Deportes"),
        ("Lago", "Piscinas"),
    ]
    for a, b in senderos:
        (x1, y1), (x2, y2) = zonas[a], zonas[b]
        ax.plot([x1, x2], [y1, y2], color="#9A9A9A", linewidth=1.0, zorder=0)
    ax.plot(5.1, 1.8, marker="*", color="#9A9A9A", markersize=16)
    ax.text(5.1, 2.1, "ENTRADA", ha="center", fontsize=8)
    ax.set_xlim(0.2, 5.6)
    ax.set_ylim(0.4, 3.9)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P02_A")
def p2023_02_a():
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    _arbol(ax, "Museo", [("Zoológico", ["Piscinas", "Lago"]), ("Lago", ["Piscinas", "Zoológico"])])
    return fig


@figura("EPA8-C1-2023-P02_B")
def p2023_02_b():
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    _arbol(ax, "Piscinas", [("Zoológico", ["Museo", "Lago"]), ("Deportes", ["Lago", "Museo"])])
    return fig


@figura("EPA8-C1-2023-P02_C")
def p2023_02_c():
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    _arbol(
        ax, "Museo", [("Zoológico", ["Piscinas", "Deportes"]), ("Lago", ["Piscinas", "Deportes"])]
    )
    return fig


@figura("EPA8-C1-2023-P02_D")
def p2023_02_d():
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    _arbol(ax, "Piscinas", [("Zoológico", ["Deportes", "Museo"]), ("Lago", ["Deportes", "Museo"])])
    return fig


def _prisma(ax, ancho, fondo, alto, color, sesgo=0.38):
    """Prisma rectangular en proyección oblicua; devuelve el desplazamiento usado."""
    dx, dy = fondo * sesgo, fondo * sesgo
    frente = [(0, 0), (ancho, 0), (ancho, alto), (0, alto)]
    ax.add_patch(Polygon(frente, facecolor=color, edgecolor=GRIS, linewidth=1.1))
    techo = [(0, alto), (ancho, alto), (ancho + dx, alto + dy), (dx, alto + dy)]
    ax.add_patch(Polygon(techo, facecolor=color, edgecolor=GRIS, linewidth=1.1, alpha=0.75))
    lado = [(ancho, 0), (ancho + dx, dy), (ancho + dx, alto + dy), (ancho, alto)]
    ax.add_patch(Polygon(lado, facecolor=color, edgecolor=GRIS, linewidth=1.1, alpha=0.55))
    return dx, dy


def _cota(ax, p1, p2, texto, desfase=(0, 0), vertical=False):
    (x1, y1), (x2, y2) = p1, p2
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="<->", color=GRIS, linewidth=0.9),
    )
    ax.text(
        (x1 + x2) / 2 + desfase[0],
        (y1 + y2) / 2 + desfase[1],
        texto,
        ha="center",
        va="center",
        fontsize=9,
        rotation=90 if vertical else 0,
    )


@figura("EPA8-C1-2023-P03")
def p2023_03():
    """Ladrillo 13 x 2 x 1 cm."""
    fig, ax = plt.subplots(figsize=(2.8, 4.2))
    dx, dy = _prisma(ax, 1.0, 2.0, 13.0, "#B5542F")
    _cota(ax, (1.0 + dx + 0.5, 0 + dy), (1.0 + dx + 0.5, 13 + dy), "13 cm", desfase=(0.45, 0))
    _cota(ax, (0, -0.9), (1.0, -0.9), "1 cm", desfase=(0, -0.7))
    _cota(ax, (1.05, -0.55), (1.0 + dx, dy - 0.55), "2 cm", desfase=(0.75, -0.55))
    ax.set_xlim(-0.8, 3.6)
    ax.set_ylim(-2.2, 14.6)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P04")
def p2023_04():
    fig, ax = plt.subplots(figsize=(5.4, 3.0))
    horas = ["3 p. m.", "4 p. m.", "5 p. m.", "6 p. m.", "7 p. m.", "8 p. m.", "9 p. m."]
    valores = [76, 85, 100, 105, 100, 85, 76]
    ax.plot(horas, valores, "--", color=NARANJA, linewidth=1.4)
    ax.plot(horas, valores, "*", color=NARANJA, markersize=11)
    for h, v in zip(horas, valores):
        ax.annotate(
            f"${v}", (h, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5
        )
    ax.set_ylim(0, 120)
    ax.set_yticks(range(0, 140, 20))
    ax.set_yticklabels([f"${v}" for v in range(0, 140, 20)])
    ax.set_xlabel("Hora del día", fontweight="bold")
    ax.set_ylabel("Valor de la unidad", fontweight="bold")
    _marco(ax)
    return fig


@figura("EPA8-C1-2023-P05")
def p2023_05():
    """Carteles de precios (sustituye la ilustración decorativa del original)."""
    fig, ax = plt.subplots(figsize=(6.4, 2.0))
    cines = [
        ("Cine 1", 7500, 3350),
        ("Cine 2", 6800, 3200),
        ("Cine 3", 5000, 4000),
        ("Cine 4", 6600, 4400),
    ]
    for i, (nombre, adulto, nino) in enumerate(cines):
        x = i * 1.6
        ax.add_patch(
            FancyBboxPatch(
                (x, 0),
                1.4,
                1.2,
                boxstyle="round,pad=0.03",
                facecolor="#FDF0C9",
                edgecolor=NARANJA,
                linewidth=1.6,
            )
        )
        ax.text(x + 0.7, 0.92, nombre, ha="center", fontsize=10, fontweight="bold")
        ax.text(x + 0.7, 0.58, f"Adultos: ${adulto:,}".replace(",", "."), ha="center", fontsize=9)
        ax.text(x + 0.7, 0.26, f"Niños: ${nino:,}".replace(",", "."), ha="center", fontsize=9)
    ax.set_xlim(-0.15, 6.35)
    ax.set_ylim(-0.15, 1.35)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P06")
def p2023_06():
    fig, ax = plt.subplots(figsize=(5.4, 2.4))
    animales = ["Elefante", "Babuino", "Guepardo"]
    ax.barh(animales, [70, 30, 10], color=AZUL, height=0.42)
    ax.set_xlim(0, 80)
    ax.set_xticks(range(0, 90, 10))
    ax.set_xlabel("Promedio de vida (años)", fontweight="bold")
    ax.set_ylabel("Animal", fontweight="bold")
    _marco(ax)
    return fig


@figura("EPA8-C1-2023-P07")
def p2023_07():
    """Árbol de tres lanzamientos: dos sub-árboles (raíz Cara y raíz Sello)."""
    fig, axes = plt.subplots(2, 1, figsize=(4.6, 5.4))
    for ax, raiz in zip(axes, ("Cara", "Sello")):
        _arbol(
            ax,
            raiz,
            [("Cara", ["Cara", "Sello"]), ("Sello", ["Cara", "Sello"])],
        )
    return fig


@figura("EPA8-C1-2023-P09")
def p2023_09():
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    for x0, lado, titulo in ((0, 6, "Ficha 1"), (8, 8, "Ficha 2")):
        ax.add_patch(Rectangle((x0, 0), lado, lado, facecolor="#E09A2B", edgecolor="none"))
        ax.text(x0 + lado / 2, lado + 0.7, titulo, ha="center", fontsize=10, fontweight="bold")
        _cota(ax, (x0, -0.9), (x0 + lado, -0.9), f"{lado} cm", desfase=(0, -0.75))
    ax.set_xlim(-1, 17)
    ax.set_ylim(-2.6, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P10")
def p2023_10():
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    pesos = [5, 6, 7, 8, 9, 10]
    costos = [5000, 5200, 5400, 5600, 5800, 6000]
    ax.plot(pesos, costos, "-o", color=NARANJA, linewidth=1.6, markersize=6)
    ax.set_ylim(4800, 6200)
    ax.set_yticks(range(4800, 6400, 200))
    ax.set_yticklabels([f"{v:,}".replace(",", ".") for v in range(4800, 6400, 200)])
    ax.set_xlabel("Peso (kg)", fontweight="bold")
    ax.set_ylabel("Costo ($)", fontweight="bold")
    ax.set_title("Costo de envío", fontweight="bold")
    _marco(ax)
    return fig


@figura("EPA8-C1-2023-P12")
def p2023_12():
    """Octágono regular con los ocho lados rotulados."""
    import math

    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    # Vértice inicial girado para que un lado quede horizontal arriba.
    puntos = [
        (math.cos(math.radians(67.5 + 45 * k)), math.sin(math.radians(67.5 + 45 * k)))
        for k in range(8)
    ]
    ax.add_patch(Polygon(puntos, facecolor=CREMA, edgecolor=NARANJA, linewidth=1.6))
    for x, y in puntos:
        ax.plot(x, y, "o", color=NARANJA, markersize=5)
    # Lados en sentido horario desde el superior: q, r, s, t, u, v, w, p
    etiquetas = ["q", "p", "w", "v", "u", "t", "s", "r"]
    for k, etiqueta in enumerate(etiquetas):
        x1, y1 = puntos[k]
        x2, y2 = puntos[(k + 1) % 8]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(
            mx * 1.22, my * 1.22, etiqueta, ha="center", va="center", fontsize=11, style="italic"
        )
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P13")
def p2023_13():
    fig, ax = plt.subplots(figsize=(6.4, 1.3))
    datos = [("Leticia", "5,1"), ("Viviana", "5,25"), ("Eduardo", "5"), ("Javier", "5,134")]
    for i, (nombre, distancia) in enumerate(datos):
        x = i * 1.6
        ax.add_patch(
            FancyBboxPatch(
                (x, 0),
                1.4,
                0.8,
                boxstyle="round,pad=0.03",
                facecolor="#FBE4CE",
                edgecolor=NARANJA,
                linewidth=1.4,
            )
        )
        ax.text(x + 0.7, 0.53, nombre, ha="center", fontsize=9.5)
        ax.text(x + 0.7, 0.24, f"{distancia} kilómetros", ha="center", fontsize=9)
    ax.set_xlim(-0.15, 6.35)
    ax.set_ylim(-0.1, 0.95)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P14")
def p2023_14():
    """Pictograma: botella grande = 10 L, botella pequeña = 5 L."""
    fig, ax = plt.subplots(figsize=(6.6, 2.8))

    def botella(x, y, grande=True):
        alto = 0.62 if grande else 0.31
        ax.add_patch(
            Rectangle((x, y), 0.34, alto, facecolor="#8FD0E8", edgecolor="#2C7FA6", linewidth=0.8)
        )
        ax.add_patch(
            Rectangle((x + 0.10, y + alto), 0.14, 0.08, facecolor="#1F4E68", edgecolor="none")
        )

    filas = [("Ducharse", 9, 1), ("Cocinar", 2, 0), ("Usar\ninodoro", 7, 1), ("Lavar\nropa", 11, 0)]
    for i, (nombre, grandes, pequenas) in enumerate(filas):
        y = (len(filas) - 1 - i) * 0.95
        ax.text(-0.2, y + 0.3, nombre, ha="right", va="center", fontsize=9)
        for k in range(grandes):
            botella(k * 0.45, y, grande=True)
        for k in range(pequenas):
            botella((grandes + k) * 0.45, y, grande=False)
    ax.add_patch(Rectangle((5.4, 0.35), 2.5, 1.6, facecolor="white", edgecolor=GRIS, linewidth=1.0))
    botella(5.6, 1.25, grande=True)
    ax.text(6.15, 1.5, "equivale a 10 litros", fontsize=8.5, va="center")
    botella(5.6, 0.55, grande=False)
    ax.text(6.15, 0.72, "equivale a 5 litros", fontsize=8.5, va="center")
    ax.set_xlim(-1.6, 8.1)
    ax.set_ylim(-0.15, 3.6)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P15")
def p2023_15():
    """Empaque tipo casa: prisma rectangular 6x4x5 + techo triangular de altura 3."""
    fig, ax = plt.subplots(figsize=(3.6, 3.6))
    dx, dy = _prisma(ax, 6.0, 4.0, 5.0, "#F2C4AE")
    techo_frente = [(0, 5), (6, 5), (3, 8)]
    ax.add_patch(Polygon(techo_frente, facecolor="#F2C4AE", edgecolor=GRIS, linewidth=1.1))
    techo_lado = [(6, 5), (6 + dx, 5 + dy), (3 + dx, 8 + dy), (3, 8)]
    ax.add_patch(Polygon(techo_lado, facecolor="#F2C4AE", edgecolor=GRIS, linewidth=1.1, alpha=0.6))
    ax.plot([3, 3 + dx], [8, 8 + dy], color=GRIS, linewidth=1.1)
    _cota(ax, (-0.7, 0), (-0.7, 8), "8 cm", desfase=(-0.55, 0))
    _cota(ax, (6 + dx + 0.5, dy), (6 + dx + 0.5, 5 + dy), "5 cm", desfase=(0.5, 0))
    _cota(ax, (0, -0.8), (6, -0.8), "6 cm", desfase=(0, -0.6))
    _cota(ax, (6.1, -0.5), (6 + dx, dy - 0.5), "4 cm", desfase=(0.9, -0.5))
    ax.set_xlim(-2.2, 9.4)
    ax.set_ylim(-2.2, 10.2)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def _barras_moda(valores, ymax):
    fig, ax = plt.subplots(figsize=(5.0, 2.2))
    anios = [1, 2, 3, 4, 5]
    ax.bar(anios, valores, color=NARANJA, width=0.35)
    for x, v in zip(anios, valores):
        ax.annotate(
            f"{v}".replace(".", ","),
            (x, v),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontsize=8.5,
        )
    ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, ymax + 1))
    ax.set_xticks(anios)
    ax.set_xlabel("Año", fontweight="bold")
    ax.set_ylabel("Centímetros", fontweight="bold")
    ax.set_title("Centímetros de aumento en la altura", fontweight="bold", fontsize=10)
    _marco(ax)
    return fig


@figura("EPA8-C1-2023-P16_A")
def p2023_16_a():
    return _barras_moda([6, 6.2, 6.5, 6.2, 6], 7)


@figura("EPA8-C1-2023-P16_B")
def p2023_16_b():
    return _barras_moda([6.3, 6.7, 6.3, 6.7, 6.3], 7)


@figura("EPA8-C1-2023-P16_C")
def p2023_16_c():
    return _barras_moda([5, 6.5, 6, 7, 6.5], 8)


@figura("EPA8-C1-2023-P16_D")
def p2023_16_d():
    return _barras_moda([5, 6.5, 7, 7, 6.5], 8)


def _estrella(cx, cy, radio, color, ax):
    import math

    puntos = []
    for k in range(10):
        r = radio if k % 2 == 0 else radio * 0.42
        ang = math.radians(90 + k * 36)
        puntos.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    ax.add_patch(Polygon(puntos, facecolor="none", edgecolor=color, linewidth=2.0))
    return puntos


@figura("EPA8-C1-2023-P18")
def p2023_18():
    """Linterna → estrella de cartón → sombra ampliada (homotecia)."""
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    ax.add_patch(
        Rectangle((3.4, 0.4), 3.0, 3.0, facecolor="#EFEFEF", edgecolor=GRIS, linewidth=0.8)
    )
    foco = (0.5, 0.6)
    ax.plot(*foco, marker="o", color="#2C7FA6", markersize=9)
    ax.text(foco[0], foco[1] - 0.32, "Linterna", ha="center", fontsize=8.5)
    pequena = _estrella(1.9, 1.5, 0.45, "#B5342B", ax)
    grande = _estrella(4.9, 2.1, 1.15, "#8A8A8A", ax)
    for p, g in zip(pequena[::2], grande[::2]):
        ax.plot([foco[0], g[0]], [foco[1], g[1]], ":", color="#D9A441", linewidth=0.9, zorder=0)
    ax.text(1.9, 0.75, "Estrella de cartón", ha="center", fontsize=8.5)
    ax.text(4.9, 3.55, "Sombra de la estrella", ha="center", fontsize=8.5)
    ax.set_xlim(0, 6.8)
    ax.set_ylim(0, 3.9)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2023-P19")
def p2023_19():
    """Círculo de centro (-2, 2) y radio 4 en el plano cartesiano."""
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    circulo = plt.Circle((-2, 2), 4, facecolor="#EDEDED", edgecolor=NARANJA, linewidth=1.8)
    ax.add_patch(circulo)
    ax.set_xlim(-8, 8)
    ax.set_ylim(-4, 6)
    ax.set_xticks(range(-8, 9))
    ax.set_yticks(range(-4, 7))
    ax.grid(True, color="#CCCCCC", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.axhline(0, color=GRIS, linewidth=1.1)
    ax.axvline(0, color=GRIS, linewidth=1.1)
    ax.set_aspect("equal")
    for lado in ("top", "right", "bottom", "left"):
        ax.spines[lado].set_visible(False)
    ax.set_xlabel("x", loc="right", style="italic")
    ax.set_ylabel("y", loc="top", rotation=0, style="italic")
    ax.tick_params(labelsize=7)
    return fig


@figura("EPA8-C1-2023-P20")
def p2023_20():
    """Proporciones de P (creciente) y Q (decreciente) que se cruzan. Sin escala numérica."""
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    t = [i / 100 for i in range(101)]
    p = [x**2 for x in t]
    q = [1 - x**2 for x in t]
    ax.plot(t, p, color=NARANJA, linewidth=2.0)
    ax.plot(t, q, color="#8E44AD", linewidth=2.0)
    ax.text(1.02, p[-1], "P", fontsize=11, style="italic", va="center")
    ax.text(1.02, q[-1], "Q", fontsize=11, style="italic", va="center")
    ax.set_xlim(0, 1.12)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("Tiempo", fontweight="bold")
    ax.set_ylabel("Proporción de líquido", fontweight="bold")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    return fig


# ── Cuadernillo 1 - 2022 ──────────────────────────────────────────────────────


@figura("EPA8-C1-2022-P05")
def p2022_05():
    """Cuadrícula 6x6 con las parejas de los dos dados."""
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    for i in range(6):
        for j in range(6):
            ax.add_patch(
                Rectangle((j, 5 - i), 1, 1, facecolor="white", edgecolor=GRIS, linewidth=0.9)
            )
            ax.text(j + 0.5, 5 - i + 0.5, f"{i+1},{j+1}", ha="center", va="center", fontsize=9)
    for k in range(6):
        ax.text(
            k + 0.5,
            6.35,
            f"{k+1}",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#2E8B7A",
        )
        ax.text(
            -0.4,
            5 - k + 0.5,
            f"{k+1}",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#C9A227",
        )
    ax.text(-0.4, 6.35, "", ha="center")
    ax.set_xlim(-0.9, 6.2)
    ax.set_ylim(-0.2, 6.8)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2022-P09")
def p2022_09():
    """Dos triángulos rectángulos sobre cuadrícula de 1 cm: catetos 1-1 y √2-1."""
    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    for k in range(4):
        ax.plot([k, k], [0, 3], color="#CFCFCF", linewidth=0.8, zorder=0)
        ax.plot([0, 3], [k, k], color="#CFCFCF", linewidth=0.8, zorder=0)
    inferior = [(0, 0), (1, 0), (1, 1)]
    superior = [(0, 0), (1, 1), (1, 2)]
    for poligono in (inferior, superior):
        ax.add_patch(Polygon(poligono, facecolor="#BFE3EC", edgecolor=GRIS, linewidth=1.3))
    ax.plot([0, 1], [0, 1], color=GRIS, linewidth=1.3)
    ax.text(0.5, -0.22, "1 cm", ha="center", fontsize=9)
    ax.text(1.12, 0.5, "1 cm", ha="left", va="center", fontsize=9)
    ax.text(1.12, 1.5, "1 cm", ha="left", va="center", fontsize=9)
    ax.text(0.30, 1.05, r"$\sqrt{3}$ cm", ha="center", va="center", fontsize=9, rotation=63)
    ax.text(0.72, 0.42, r"$\sqrt{2}$ cm", ha="center", va="center", fontsize=9, rotation=45)
    ax.set_xlim(-0.5, 2.6)
    ax.set_ylim(-0.5, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2022-P10")
def p2022_10():
    """Dos sombreros triangulares semejantes (razón 1:2)."""
    fig, ax = plt.subplots(figsize=(5.2, 2.8))

    def sombrero(x0, y0, escala, color, punta, titulo):
        cuerpo = [(x0, y0), (x0 + 3.0 * escala, y0), (x0, y0 + 3.4 * escala)]
        ax.add_patch(Polygon(cuerpo, facecolor=color, edgecolor="black", linewidth=2.0))
        pico = [
            (x0, y0 + 3.4 * escala),
            (x0, y0 + 2.35 * escala),
            (x0 + 0.85 * escala, y0 + 3.4 * escala),
        ]
        ax.add_patch(Polygon(pico, facecolor=punta, edgecolor="black", linewidth=2.0))
        ax.plot(
            x0 + 1.0 * escala, y0 + 1.35 * escala, marker="*", color="black", markersize=13 * escala
        )
        ax.text(x0 + 1.3 * escala, y0 - 0.35, titulo, ha="center", fontsize=9, fontweight="bold")

    sombrero(0.3, 0.4, 1.0, "#D8C22B", "#2FAE72", "Sombrero 1")
    sombrero(4.6, 0.4, 0.55, "#E09A2B", "#D93A5B", "Sombrero 2")
    ax.set_xlim(0, 7.2)
    ax.set_ylim(-0.1, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2022-P11")
def p2022_11():
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    anios = [1, 2, 3, 4]
    precios = [200, 600, 1000, 1400]
    ax.plot(anios, precios, "o", color="#8E44AD", markersize=7)
    ax.set_xlim(0, 4.8)
    ax.set_ylim(0, 1800)
    ax.set_xticks(anios)
    ax.set_yticks(range(0, 2000, 200))
    ax.set_yticklabels([f"${v:,}".replace(",", ".") for v in range(0, 2000, 200)])
    ax.set_xlabel("Año", fontweight="bold")
    ax.set_ylabel("Precio", fontweight="bold")
    _marco(ax)
    return fig


@figura("EPA8-C1-2022-P14")
def p2022_14():
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    ax.plot([1, 4, 8], [10, 25, 25], color=NARANJA, linewidth=2.0)
    ax.set_xlim(0, 8.4)
    ax.set_ylim(0, 30)
    ax.set_xticks(range(0, 9))
    ax.set_yticks(range(0, 35, 5))
    ax.set_yticklabels([f"{v} %" for v in range(0, 35, 5)])
    ax.set_xlabel("Cantidad de artículos comprados", fontweight="bold")
    ax.set_ylabel("Porcentaje de descuento", fontweight="bold")
    ax.set_title("Descuentos en la tienda de Esteban", fontweight="bold", fontsize=10)
    _marco(ax)
    return fig


@figura("EPA8-C1-2022-P16")
def p2022_16():
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    dias = list(range(1, 11))
    alturas = [10 * d + 20 for d in dias]
    ax.plot(dias, alturas, "-o", color="#4BC0E0", linewidth=1.6, markersize=5)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 130)
    ax.set_xticks(range(0, 12))
    ax.set_yticks(range(0, 140, 10))
    ax.set_xlabel("Día", fontweight="bold")
    ax.set_ylabel("Altura de la guadua (cm)", fontweight="bold")
    ax.tick_params(labelsize=8)
    _marco(ax)
    return fig


@figura("EPA8-C1-2022-P18")
def p2022_18():
    fig, ax = plt.subplots(figsize=(4.4, 2.4))
    ax.barh(["5", "10", "15"], [20, 15, 10], color="#3C74C4", height=0.5)
    ax.set_xlim(0, 24)
    ax.set_xticks([10, 15, 20])
    ax.set_xlabel("Cantidad de estudiantes", fontweight="bold")
    ax.set_ylabel("Tiempo en minutos", fontweight="bold")
    ax.grid(True, axis="x", color="#CCCCCC", linewidth=0.8, linestyle=":")
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    return fig


# ── Cuadernillo 1 - 2021 ──────────────────────────────────────────────────────


@figura("EPA8-C1-2021-P01")
def p2021_01():
    """Mapa a escala: cada casilla mide 20 m. Recorrido O(4) → N(3) → E(8) → N(2)."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for k in range(15):
        ax.plot([k, k], [0, 9], color="#CFCFCF", linewidth=0.7, linestyle="--", zorder=0)
    for k in range(10):
        ax.plot([0, 14], [k, k], color="#CFCFCF", linewidth=0.7, linestyle="--", zorder=0)
    manzanas = [(6, 7, 4, 2), (0, 2, 1, 6), (4, 4, 10, 1), (4, 1, 9, 1), (11, 5, 2, 1)]
    for x, y, ancho, alto in manzanas:
        ax.add_patch(
            Rectangle((x, y), ancho, alto, facecolor="#DDDDDD", edgecolor=GRIS, linewidth=1.2)
        )
    inicio = (7, 4)
    parque = (11, 8)
    tramos = [(3, 4), (3, 7), (11, 7), (11, 8)]
    puntos = [inicio] + tramos
    for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.6),
        )
    ax.plot(*inicio, "o", color="black", markersize=7)
    ax.text(inicio[0] + 0.2, inicio[1] - 0.45, "Punto de inicio", fontsize=8.5, fontweight="bold")
    ax.plot(*parque, "o", color="black", markersize=7)
    ax.text(parque[0] + 0.25, parque[1], "Parque", fontsize=8.5, fontweight="bold", va="center")
    _cota(ax, (12, -0.6), (13, -0.6), "20 metros", desfase=(0, -0.55))
    _cota(ax, (14.4, 1), (14.4, 2), "20 metros", desfase=(1.3, 0))
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-1.6, 9.5)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2021-P03")
def p2021_03():
    """Sala de cine: sillas ocupadas (azul) y disponibles M, N, P, Q (blancas)."""
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ocupadas = {
        6: [1, 2, 4, 5, 6, 7, 8, 9],
        5: [1, 2, 3, 5, 6, 7, 8, 9],
        4: [2, 3, 4, 5, 7, 8],
        3: [2, 3, 4, 5, 6, 8],
        2: [4, 5, 6],
        1: [4, 5, 6],
    }
    disponibles = {"M": (3, 6), "N": (4, 5), "P": (6, 4), "Q": (7, 3)}
    for fila, columnas in ocupadas.items():
        for col in columnas:
            ax.add_patch(
                Rectangle((col - 0.4, fila - 0.35), 0.8, 0.7, facecolor="#2A3B8F", edgecolor="none")
            )
    for etiqueta, (col, fila) in disponibles.items():
        ax.add_patch(
            Rectangle(
                (col - 0.4, fila - 0.35), 0.8, 0.7, facecolor="white", edgecolor=GRIS, linewidth=1.0
            )
        )
        ax.text(col, fila, etiqueta, ha="center", va="center", fontsize=8)
    ax.set_xlim(0, 9.8)
    ax.set_ylim(0, 6.9)
    ax.set_xticks(range(0, 10))
    ax.set_yticks(range(0, 7))
    ax.set_xlabel("Número de columna", fontweight="bold")
    ax.set_ylabel("Número de fila", fontweight="bold")
    ax.tick_params(labelsize=8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    return fig


@figura("EPA8-C1-2021-P04")
def p2021_04():
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    meses = [0, 2, 4, 6, 8]
    tasas = [0.012, 0.014, 0.016, 0.018, 0.020]
    ax.plot([0, 8.6], [0.012, 0.0163 + 0.0043], color="black", linewidth=1.4, zorder=1)
    ax.plot(
        meses,
        tasas,
        "o",
        markerfacecolor="white",
        markeredgecolor=GRIS,
        markersize=8,
        linestyle="none",
        zorder=2,
    )
    ax.set_xlim(0, 8.6)
    ax.set_ylim(0.010, 0.0212)
    ax.set_xticks(range(0, 9))
    ax.set_yticks([0.010, 0.012, 0.014, 0.016, 0.018, 0.020])
    ax.set_yticklabels(["0,010", "0,012", "0,014", "0,016", "0,018", "0,020"])
    ax.set_xlabel("Tiempo del préstamo\nMeses", fontweight="bold")
    ax.set_ylabel("Tasa de interés", fontweight="bold")
    ax.tick_params(labelsize=8)
    _marco(ax)
    return fig


@figura("EPA8-C1-2021-P05")
def p2021_05():
    """Estante esquemático: arriba cilindros (base circular), abajo prismas (6 caras)."""
    fig, ax = plt.subplots(figsize=(5.4, 3.0))
    for x in range(6):
        cx = 0.6 + x * 0.9
        ax.add_patch(
            Rectangle(
                (cx - 0.26, 2.1), 0.52, 0.85, facecolor="#E8A33D", edgecolor=GRIS, linewidth=1.0
            )
        )
        ax.add_patch(
            plt.matplotlib.patches.Ellipse(
                (cx, 2.95), 0.52, 0.18, facecolor="#F3C98B", edgecolor=GRIS, linewidth=1.0
            )
        )
        ax.add_patch(
            plt.matplotlib.patches.Ellipse(
                (cx, 2.1), 0.52, 0.18, facecolor="#E8A33D", edgecolor=GRIS, linewidth=1.0
            )
        )
    ax.plot([0, 6], [1.95, 1.95], color="black", linewidth=5)
    ax.text(6.25, 2.45, "Parte superior\ndel estante", fontsize=8.5, va="center")
    for x in range(5):
        cx = 0.7 + x * 1.0
        dx, dy = 0.22, 0.18
        frente = [(cx - 0.35, 0.5), (cx + 0.35, 0.5), (cx + 0.35, 1.35), (cx - 0.35, 1.35)]
        ax.add_patch(Polygon(frente, facecolor="#B5794A", edgecolor=GRIS, linewidth=1.0))
        techo = [
            (cx - 0.35, 1.35),
            (cx + 0.35, 1.35),
            (cx + 0.35 + dx, 1.35 + dy),
            (cx - 0.35 + dx, 1.35 + dy),
        ]
        ax.add_patch(Polygon(techo, facecolor="#CE9366", edgecolor=GRIS, linewidth=1.0))
        lado = [
            (cx + 0.35, 0.5),
            (cx + 0.35 + dx, 0.5 + dy),
            (cx + 0.35 + dx, 1.35 + dy),
            (cx + 0.35, 1.35),
        ]
        ax.add_patch(Polygon(lado, facecolor="#9C6339", edgecolor=GRIS, linewidth=1.0))
    ax.plot([0, 6], [0.4, 0.4], color="black", linewidth=5)
    ax.text(6.25, 0.95, "Parte inferior\ndel estante", fontsize=8.5, va="center")
    ax.set_xlim(-0.2, 8.4)
    ax.set_ylim(0.2, 3.3)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2021-P06")
def p2021_06():
    """Dos caminos de parqués: ficha 1 a tres casillas de LLEGADA, ficha 2 a una."""
    fig, ax = plt.subplots(figsize=(4.8, 3.4))
    for i, (x0, casilla_ficha, color) in enumerate([(0, 4, "#C0392B"), (2.6, 6, "#27AE60")]):
        for k in range(7):
            ax.add_patch(
                Rectangle(
                    (x0, 0.55 + k * 0.42),
                    1.8,
                    0.42,
                    facecolor="#F3DFB0",
                    edgecolor=GRIS,
                    linewidth=1.0,
                )
            )
        ax.add_patch(
            Rectangle((x0, 0.1), 1.8, 0.45, facecolor="#F3DFB0", edgecolor=GRIS, linewidth=1.4)
        )
        ax.text(x0 + 0.9, 0.32, "SEGURO", ha="center", va="center", fontsize=8.5, fontweight="bold")
        techo = [(x0, 3.49), (x0 + 1.8, 3.49), (x0 + 1.8, 3.85), (x0 + 0.9, 4.1), (x0, 3.85)]
        ax.add_patch(Polygon(techo, facecolor="#F3DFB0", edgecolor=GRIS, linewidth=1.4))
        ax.text(x0 + 0.9, 3.7, "LLEGADA", ha="center", va="center", fontsize=8.5, fontweight="bold")
        ax.plot(
            x0 + 0.9, 0.55 + casilla_ficha * 0.42 + 0.21, marker="o", color=color, markersize=11
        )
        ax.text(x0 + 0.9, -0.15, f"Ficha jugador {i+1}", ha="center", fontsize=8)
    ax.set_xlim(-0.4, 4.8)
    ax.set_ylim(-0.5, 4.4)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2021-P09")
def p2021_09():
    """Trapecio 20/12 de altura 12, descompuesto en triángulo (8) + cuadrado (12)."""
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.add_patch(
        Polygon(
            [(0, 0), (8, 0), (8, 12), (0, 0)], facecolor="#F7D7BE", edgecolor=GRIS, linewidth=1.2
        )
    )
    ax.add_patch(
        Polygon(
            [(8, 0), (20, 0), (20, 12), (8, 12)],
            facecolor="#E8792B",
            edgecolor=GRIS,
            linewidth=1.2,
            alpha=0.55,
        )
    )
    _cota(ax, (-1.6, 0), (-1.6, 12), "12 cm", desfase=(-1.5, 0))
    _cota(ax, (0, -1.4), (8, -1.4), "8 cm", desfase=(0, -1.0))
    _cota(ax, (8, -1.4), (20, -1.4), "12 cm", desfase=(0, -1.0))
    _cota(ax, (0, -3.6), (20, -3.6), "20 cm", desfase=(0, -1.0))
    ax.set_xlim(-4.5, 21)
    ax.set_ylim(-6, 13.5)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2021-P11")
def p2021_11():
    """Altura de la pelota: 5 m en t=0, máximo 9 m en t=2, suelo en t=5."""
    fig, ax = plt.subplots(figsize=(4.0, 3.2))
    # Parábola por los tres datos del enunciado: (0,5), (2,9), (5,0).
    t = [i / 100 for i in range(0, 501)]
    a, b, c = -0.6, 2.4, 5.0
    y = [max(0, a * x * x + b * x + c) for x in t]
    ax.plot(t, y, color="#5CB85C", linewidth=2.0)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 9.4)
    ax.set_xticks(range(0, 7))
    ax.set_yticks(range(0, 10))
    ax.set_xlabel("Tiempo (segundos)", fontweight="bold")
    ax.set_ylabel("Altura (metros)", fontweight="bold")
    ax.grid(True, color="#CCCCCC", linewidth=0.7)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    return fig


@figura("EPA8-C1-2021-P12")
def p2021_12():
    """Árbol de dos niveles con 3 hojas por rama (no cabe en el _arbol binario)."""
    fig, ax = plt.subplots(figsize=(5.4, 3.0))
    raiz = (3.0, 2.6)
    ax.plot(*raiz, "o", color="black", markersize=6)
    ax.text(raiz[0], raiz[1] + 0.22, "Género", ha="center", fontsize=9.5, fontweight="bold")
    ramas = [
        (1.3, 1.7, "Mujer", ["Azul", "Café", "Verde"], -1),
        (4.7, 1.7, "Hombre", ["Azul", "Café", "Negro"], 1),
    ]
    for x, y, etiqueta, hojas, signo in ramas:
        ax.plot([raiz[0], x], [raiz[1], y], color="black", linewidth=1.0)
        ax.plot(x, y, "o", color="black", markersize=6)
        ax.text(x + signo * 0.75, y + 0.32, etiqueta, ha="center", fontsize=9)
        ax.text(x, y + 0.22, "Color de ojos", ha="center", fontsize=9, fontweight="bold")
        for k, hoja in enumerate(hojas):
            hx = x + (k - 1) * 0.85
            hy = 0.7
            ax.plot([x, hx], [y, hy], color="black", linewidth=1.0)
            ax.plot(hx, hy, "o", color="black", markersize=5)
            ax.text(hx, hy - 0.22, hoja, ha="center", fontsize=8.5)
    ax.text(3.0, 3.15, "Salón de clases", ha="center", fontsize=10.5, fontweight="bold")
    ax.set_xlim(-0.3, 6.3)
    ax.set_ylim(0.2, 3.5)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2021-P14")
def p2021_14():
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    xs, ys = [2, 4, 6, 8], [24, 28, 32, 36]
    ax.plot(xs, ys, "o", color="#5CB85C", markersize=7)
    for x, y in zip(xs, ys):
        ax.annotate(f"({x}, {y})", (x, y), textcoords="offset points", xytext=(8, 2), fontsize=8.5)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 40)
    ax.set_xticks(range(2, 13, 2))
    ax.set_yticks(range(0, 40, 5))
    ax.set_xlabel("Edad biológica del humano en años", fontweight="bold", fontsize=9)
    ax.set_ylabel("Edad biológica del perro en años", fontweight="bold", fontsize=9)
    ax.tick_params(labelsize=8)
    _marco(ax)
    return fig


@figura("EPA8-C1-2021-P16")
def p2021_16():
    """Cara triangular de la pirámide: 410, 410 y 440 cm."""
    import math

    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    base = 4.40
    lado = 4.10
    altura = math.sqrt(lado**2 - (base / 2) ** 2)
    vertices = [(0, 0), (base, 0), (base / 2, altura)]
    ax.add_patch(Polygon(vertices, facecolor="#F0E0C8", edgecolor="black", linewidth=1.8))
    ax.text(base / 2, -0.35, "440 cm", ha="center", fontsize=9)
    ax.text(0.85, altura / 2 + 0.15, "410 cm", ha="center", fontsize=9, rotation=58)
    ax.text(base - 0.85, altura / 2 + 0.15, "410 cm", ha="center", fontsize=9, rotation=-58)
    ax.set_xlim(-0.6, base + 0.6)
    ax.set_ylim(-0.9, altura + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2021-P17")
def p2021_17():
    """Ficha de 2x2 cm y la figura de 9 fichas (4 arriba, 1 en medio, 4 abajo)."""
    fig, ax = plt.subplots(figsize=(4.6, 3.0))

    def ficha(x, y):
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor="white", edgecolor="#7A3FA0", linewidth=2.0))

    ficha(0, 3.6)
    _cota(ax, (0, 4.85), (1, 4.85), "2 cm", desfase=(0, 0.35))
    _cota(ax, (-0.35, 3.6), (-0.35, 4.6), "2 cm", desfase=(-0.75, 0))
    for k in range(4):
        ficha(3 + k, 2)
    ficha(4, 1)
    for k in range(4):
        ficha(3 + k, 0)
    ax.set_xlim(-1.6, 7.6)
    ax.set_ylim(-0.4, 5.4)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


# ── Cuadernillo 1 - 2020 ──────────────────────────────────────────────────────


@figura("EPA8-C1-2020-P01")
def p2020_01():
    """Cartel del clima laboral: tres categorías con su porcentaje."""
    fig, ax = plt.subplots(figsize=(5.6, 2.0))
    ax.add_patch(Rectangle((0, 0), 6.6, 1.9, facecolor="white", edgecolor="black", linewidth=1.6))
    datos = [("Felices", "30 %"), ("Tristes", "50 %"), ("No saben, no\nresponden", "20 %")]
    for i, (etiqueta, porcentaje) in enumerate(datos):
        x = 1.1 + i * 2.2
        ax.text(x, 1.55, etiqueta, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.add_patch(plt.Circle((x, 0.9), 0.34, facecolor="white", edgecolor=GRIS, linewidth=1.4))
        ax.text(x, 0.25, porcentaje, ha="center", va="center", fontsize=12, fontweight="bold")
    ax.set_xlim(-0.2, 6.8)
    ax.set_ylim(-0.15, 2.05)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2020-P03")
def p2020_03():
    """Prisma hexagonal y sus dos tapas: hexágonos regulares de 5 cm y 120°."""
    import math

    fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.6))
    puntos = [
        (math.cos(math.radians(30 + 60 * k)), math.sin(math.radians(30 + 60 * k))) for k in range(6)
    ]
    # Figura 1: prisma hexagonal (dos hexágonos desplazados + aristas verticales).
    ax = axes[0]
    # Hexágono achatado (vista en perspectiva) arriba y abajo, unidos por aristas verticales.
    tapa = [(x, y * 0.34) for x, y in puntos]
    altura = 2.0
    superior = [(x, y + altura) for x, y in tapa]
    cuerpo = [
        superior[3],
        superior[4],
        superior[5],
        superior[0],
        tapa[0],
        tapa[5],
        tapa[4],
        tapa[3],
    ]
    ax.add_patch(Polygon(cuerpo, facecolor="white", edgecolor=GRIS, linewidth=1.3))
    ax.add_patch(Polygon(superior, facecolor="white", edgecolor=GRIS, linewidth=1.3))
    for k in (0, 3, 4, 5):
        ax.plot(
            [tapa[k][0], superior[k][0]], [tapa[k][1], superior[k][1]], color=GRIS, linewidth=1.3
        )
    for k in (1, 2):
        ax.plot(
            [tapa[k][0], superior[k][0]],
            [tapa[k][1], superior[k][1]],
            color=GRIS,
            linewidth=0.9,
            linestyle="--",
        )
    ax.add_patch(Polygon(tapa, facecolor="none", edgecolor=GRIS, linewidth=0.9, linestyle="--"))
    ax.set_title("Cartuchera\n(Figura 1)", fontsize=9, fontweight="bold")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.9, 3.1)
    # Figuras 2 y 3: las tapas.
    for ax, titulo in zip(axes[1:], ("Tapa superior\n(Figura 2)", "Tapa inferior\n(Figura 3)")):
        ax.add_patch(Polygon(puntos, facecolor=CREMA, edgecolor=NARANJA, linewidth=1.6))
        for k in range(6):
            x1, y1 = puntos[k]
            x2, y2 = puntos[(k + 1) % 6]
            ax.text(
                (x1 + x2) / 2 * 1.32,
                (y1 + y2) / 2 * 1.32,
                "5 cm",
                ha="center",
                va="center",
                fontsize=7,
            )
            ax.text(x1 * 0.74, y1 * 0.74, "120°", ha="center", va="center", fontsize=6.5)
        ax.set_title(titulo, fontsize=9, fontweight="bold")
        ax.set_xlim(-1.7, 1.7)
        ax.set_ylim(-1.7, 1.7)
    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    return fig


@figura("EPA8-C1-2020-P08")
def p2020_08():
    """Cubo (8 vértices), pirámide cuadrangular (5), prisma triangular (6), bipirámide (6)."""
    fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.2))

    def dibujar(ax, caras, ocultas=()):
        for cara in caras:
            ax.add_patch(
                Polygon(cara, facecolor="#F7D7BE", edgecolor=GRIS, linewidth=1.2, alpha=0.85)
            )
        for x1, y1, x2, y2 in ocultas:
            ax.plot([x1, x2], [y1, y2], color=GRIS, linewidth=0.9, linestyle="--")

    d = 0.35
    dibujar(
        axes[0],
        [
            [(0, 0), (1, 0), (1, 1), (0, 1)],
            [(0, 1), (1, 1), (1 + d, 1 + d), (d, 1 + d)],
            [(1, 0), (1 + d, d), (1 + d, 1 + d), (1, 1)],
        ],
        ocultas=[(0, 0, d, d), (d, d, 1 + d, d), (d, d, d, 1 + d)],
    )
    axes[0].set_title("Marca $P$", fontsize=9)
    dibujar(
        axes[1],
        [[(0, 0), (1, 0), (0.75, 1.3)], [(1, 0), (1.4, 0.3), (0.75, 1.3)]],
        ocultas=[(0, 0, 0.4, 0.3), (0.4, 0.3, 1.4, 0.3), (0.4, 0.3, 0.75, 1.3)],
    )
    axes[1].set_title("Marca $Q$", fontsize=9)
    dibujar(
        axes[2],
        [[(0, 0.25), (1.1, 0), (0.55, 1.0)], [(1.1, 0), (1.5, 0.55), (0.55, 1.0)]],
        ocultas=[(0, 0.25, 0.45, 0.75), (0.45, 0.75, 1.5, 0.55), (0.45, 0.75, 0.55, 1.0)],
    )
    axes[2].set_title("Marca $R$", fontsize=9)
    dibujar(
        axes[3],
        [
            [(0.15, 0.65), (0.75, 0.42), (0.75, 1.4)],
            [(0.75, 0.42), (1.35, 0.65), (0.75, 1.4)],
            [(0.15, 0.65), (0.75, 0.42), (0.75, 0)],
            [(0.75, 0.42), (1.35, 0.65), (0.75, 0)],
        ],
        ocultas=[
            (0.15, 0.65, 0.75, 0.9),
            (0.75, 0.9, 1.35, 0.65),
            (0.75, 0.9, 0.75, 1.4),
            (0.75, 0.9, 0.75, 0),
        ],
    )
    axes[3].set_title("Marca $S$", fontsize=9)
    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
        ax.margins(0.15)
    return fig


@figura("EPA8-C1-2020-P09")
def p2020_09():
    """Edificio con cotas 18 m de alto y base de 12 m por 8 m."""
    fig, ax = plt.subplots(figsize=(3.0, 3.8))
    dx, dy = _prisma(ax, 12.0, 8.0, 18.0, "#9FC4DE")
    ax.add_patch(
        Polygon(
            [(-0.8, -1.2), (12.8, -1.2), (12.8 + dx, -1.2 + dy), (-0.8 + dx, -1.2 + dy)],
            facecolor="#D6D6D6",
            edgecolor=GRIS,
            linewidth=1.0,
        )
    )
    ax.add_patch(
        Polygon(
            [(3, 18 + dy * 0.4), (9, 18 + dy * 0.4), (9 + dx * 0.5, 20), (3 + dx * 0.5, 20)],
            facecolor="#E4D7A8",
            edgecolor=GRIS,
            linewidth=1.0,
        )
    )
    _cota(ax, (12 + dx + 1.4, dy), (12 + dx + 1.4, 18 + dy), "18 m", desfase=(1.4, 0))
    _cota(ax, (0, -2.6), (12, -2.6), "12 m", desfase=(0, -1.4))
    _cota(ax, (12.2, -2.2), (12 + dx, dy - 2.2), "8 m", desfase=(2.0, -1.2))
    ax.set_xlim(-3, 20)
    ax.set_ylim(-6, 22)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2020-P10")
def p2020_10():
    """Tres cartas (personaje, poder) con flechas rotulando cada componente."""
    fig, ax = plt.subplots(figsize=(5.8, 2.6))
    for i, (personaje, poder) in enumerate([(1, 5), (4, 6), (2, 7)]):
        x = i * 2.0
        ax.add_patch(
            Rectangle((x, 0), 1.75, 2.3, facecolor="white", edgecolor="black", linewidth=1.6)
        )
        ax.text(x + 0.875, 2.02, "Personaje", ha="center", fontsize=9)
        ax.annotate(
            "",
            xy=(x + 0.875, 1.48),
            xytext=(x + 0.875, 1.85),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.2),
        )
        ax.text(
            x + 0.875,
            1.15,
            f"({personaje},{poder})",
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
        )
        ax.annotate(
            "",
            xy=(x + 0.875, 0.72),
            xytext=(x + 0.875, 0.38),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.2),
        )
        ax.text(x + 0.875, 0.18, "Poder", ha="center", fontsize=9)
    ax.set_xlim(-0.2, 5.95)
    ax.set_ylim(-0.15, 2.45)
    ax.axis("off")
    return fig


@figura("EPA8-C1-2020-P13")
def p2020_13():
    """Plano a escala de la fachada: 50 cm de ancho por 15 cm de alto."""
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    ax.add_patch(Rectangle((0, 0), 50, 15, facecolor="white", edgecolor=GRIS, linewidth=1.4))
    ax.add_patch(
        Polygon([(-2, 15), (52, 15), (25, 26)], facecolor="white", edgecolor=GRIS, linewidth=1.4)
    )
    for x in (7, 34):
        ax.add_patch(Rectangle((x, 5), 9, 6, facecolor="white", edgecolor=GRIS, linewidth=1.1))
    ax.add_patch(Rectangle((22, 0), 6, 11, facecolor="white", edgecolor=GRIS, linewidth=1.1))
    ax.add_patch(Rectangle((23, 18), 3, 3, facecolor="white", edgecolor=GRIS, linewidth=1.1))
    _cota(ax, (54, 0), (54, 15), "15 cm", desfase=(4.5, 0))
    _cota(ax, (0, -3), (50, -3), "50 cm", desfase=(0, -2.6))
    ax.set_xlim(-6, 64)
    ax.set_ylim(-9, 28)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@figura("EPA8-C1-2020-P17")
def p2020_17():
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo"]
    turistas = [1, 1.5, 2, 2.5, 3]
    ax.plot(meses, turistas, "o", color="#7A3FA0", markersize=8)
    ax.set_ylim(1, 3)
    ticks = [1 + 0.1 * k for k in range(21)]
    ax.set_yticks(ticks)
    ax.set_yticklabels(_coma(ticks, 1))
    ax.set_xlabel("Mes", fontweight="bold")
    ax.set_ylabel("N.° turistas (millones)", fontweight="bold")
    ax.tick_params(labelsize=7)
    _marco(ax)
    return fig


@figura("EPA8-C1-2020-P20")
def p2020_20():
    """Rectángulo original de 4 cm por 8 cm."""
    fig, ax = plt.subplots(figsize=(2.2, 2.8))
    ax.add_patch(Rectangle((0, 0), 4, 8, facecolor="#2C7FA6", edgecolor=GRIS, linewidth=1.2))
    _cota(ax, (4.7, 0), (4.7, 8), "8 cm", desfase=(1.3, 0))
    _cota(ax, (0, -0.9), (4, -0.9), "4 cm", desfase=(0, -0.8))
    ax.set_xlim(-1.5, 8.5)
    ax.set_ylim(-2.6, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


# ── CLI ───────────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    filtros = argv[1:]
    seleccion = {
        nombre: fn
        for nombre, fn in BUILDERS.items()
        if not filtros or any(f in nombre for f in filtros)
    }
    if not seleccion:
        print(f"Sin figuras que coincidan con {filtros}. Disponibles: {sorted(BUILDERS)}")
        return 1
    for nombre, fn in sorted(seleccion.items()):
        destino = _guardar(fn(), nombre)
        print(f"OK  {destino.relative_to(ROOT)}")
    print(f"\n{len(seleccion)} figura(s) generada(s) en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
