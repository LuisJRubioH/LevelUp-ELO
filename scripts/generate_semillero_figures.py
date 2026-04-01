"""
Genera las 14 figuras PNG del banco Semillero de Matemáticas (Olimpiadas UdeA).
Ejecutar desde la raíz del repositorio:
    python scripts/generate_semillero_figures.py

Salida: items/images/  (se crea si no existe)
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = 'items/images'
os.makedirs(OUTPUT_DIR, exist_ok=True)

GRAY  = '#CCCCCC'
BLACK = 'black'
LW    = 2
FS    = 12


def save_fig(filename):
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight', dpi=100)
    plt.close()
    print(f'  OK: {filename}')


# ── 1. septimo_q14_cuadrados.png ─────────────────────────────────────────────
# gs_7_01: Dos cuadrados (6 cm y 4 cm) parcialmente superpuestos
def fig_septimo_cuadrados():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    # Cuadrado grande 6×6; cuadrado pequeño 4×4 superpuesto en esquina inferior-der
    overlap = patches.Rectangle((4, 0), 2, 4, lw=0, facecolor=GRAY)
    big     = patches.Rectangle((0, 0), 6, 6, lw=LW, edgecolor=BLACK, facecolor='none')
    small   = patches.Rectangle((4, 0), 4, 4, lw=LW, edgecolor=BLACK, facecolor='none')

    ax.add_patch(overlap)
    ax.add_patch(big)
    ax.add_patch(small)

    # Dimensiones
    ax.annotate('', xy=(0, -0.5), xytext=(6, -0.5),
                arrowprops=dict(arrowstyle='<->', color=BLACK, lw=1))
    ax.text(3, -0.8, '6 cm', ha='center', va='top', fontsize=FS)
    ax.annotate('', xy=(4, -1.3), xytext=(8, -1.3),
                arrowprops=dict(arrowstyle='<->', color=BLACK, lw=1))
    ax.text(6, -1.6, '4 cm', ha='center', va='top', fontsize=FS)

    ax.text(5, 2, 'zona\nsombreada', ha='center', va='center', fontsize=10, color='#555')

    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-2, 7)
    save_fig('septimo_q14_cuadrados.png')


# ── 2. octavo_q14_rectangulos.png ────────────────────────────────────────────
# gs_8_01: Rectángulo 20×32 en vértice del rectángulo 108×98, marcar centros
def fig_octavo_rectangulos():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    # Escala ÷10 para visualización
    W, H = 10.8, 9.8
    w, h = 3.2, 2.0   # 32×20

    big   = patches.Rectangle((0, 0), W, H, lw=LW, edgecolor=BLACK, facecolor='white')
    small = patches.Rectangle((0, 0), w, h, lw=LW, edgecolor=BLACK, facecolor=GRAY)

    ax.add_patch(big)
    ax.add_patch(small)

    cx_big, cy_big = W / 2, H / 2
    cx_sm,  cy_sm  = w / 2, h / 2

    ax.plot(cx_big, cy_big, 'ko', markersize=7, zorder=5)
    ax.plot(cx_sm,  cy_sm,  'ko', markersize=7, zorder=5)
    ax.plot([cx_sm, cx_big], [cy_sm, cy_big], 'k--', lw=1.5)

    ax.text(cx_big + 0.2, cy_big + 0.25, 'Centro', fontsize=9)
    ax.text(cx_sm  + 0.15, cy_sm  + 0.2,  'Centro', fontsize=9)

    ax.text(W / 2, -0.6,  '108 cm', ha='center', va='top',    fontsize=10)
    ax.text(-0.6,  H / 2, '98 cm',  ha='right',  va='center', fontsize=10, rotation=90)
    ax.text(w / 2, h + 0.2, '32 cm', ha='center', va='bottom', fontsize=9)
    ax.text(w + 0.15, h / 2, '20 cm', ha='left',   va='center', fontsize=9)

    ax.set_xlim(-1.5, W + 1.5)
    ax.set_ylim(-1.2, H + 1)
    save_fig('octavo_q14_rectangulos.png')


# ── 3. octavo_q15_centro_O.png ───────────────────────────────────────────────
# gs_8_02: Rectángulo con centro O, triángulo OPQ sombreado
def fig_octavo_centro_O():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    W, H = 8, 5
    O = (W / 2, H / 2)
    P = (1.5, 0)
    Q = (W, 1.0)

    # Rectángulo con todas las regiones sombreadas (dos triángulos opuestos desde O)
    # Triángulo OPQ y su opuesto simetricamente
    O2 = (W - O[0], H - O[1])   # = O (centro del rectángulo)
    P2 = (W - P[0], H - P[1])
    Q2 = (W - Q[0], H - Q[1])

    tri1 = plt.Polygon([O, P, Q],   closed=True, facecolor=GRAY, edgecolor=BLACK, lw=LW)
    tri2 = plt.Polygon([O, P2, Q2], closed=True, facecolor=GRAY, edgecolor=BLACK, lw=LW)
    ax.add_patch(tri1)
    ax.add_patch(tri2)

    rect = patches.Rectangle((0, 0), W, H, lw=LW, edgecolor=BLACK, facecolor='none')
    ax.add_patch(rect)

    # Diagonales (tenues)
    ax.plot([0, W], [0, H], 'k-', lw=1, alpha=0.3)
    ax.plot([W, 0], [0, H], 'k-', lw=1, alpha=0.3)

    ax.text(O[0] + 0.2, O[1] + 0.25, 'O', fontsize=FS + 2, fontweight='bold')
    ax.text(P[0],       P[1] - 0.35, 'P', ha='center', va='top',   fontsize=FS)
    ax.text(Q[0] + 0.2, Q[1],        'Q', ha='left',   va='center', fontsize=FS)

    ax.set_xlim(-0.5, W + 0.8)
    ax.set_ylim(-0.8, H + 0.5)
    save_fig('octavo_q15_centro_O.png')


# ── 4. noveno_q14_rombo.png ──────────────────────────────────────────────────
# gs_9_01: Rectángulo ABCD (AD=16, AB=12) con rombo AECF inscrito
def fig_noveno_rombo():
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.set_aspect('equal')
    ax.axis('off')

    # A=BL, B=BR, C=TR, D=TL  (AB=12 ancho, AD=16 alto)
    A = (0,  0); B = (12,  0)
    C = (12, 16); D = (0, 16)

    # E en BC, F en AD (rombo AECF)
    # AE = sqrt(144 + y²) = 16 - y  →  y = 3.5
    y = 3.5
    E = (12, y)
    F = (0, 16 - y)   # F = (0, 12.5)

    rhombus = plt.Polygon([A, E, C, F], closed=True, facecolor=GRAY,  edgecolor=BLACK, lw=LW)
    rect    = plt.Polygon([A, B, C, D], closed=True, facecolor='none', edgecolor=BLACK, lw=LW)

    ax.add_patch(rhombus)
    ax.add_patch(rect)

    # Diagonal EF del rombo
    ax.plot([E[0], F[0]], [E[1], F[1]], 'k-', lw=1.5)
    # Diagonal AC
    ax.plot([A[0], C[0]], [A[1], C[1]], 'k-', lw=1.5)

    off = 0.6
    for pt, lbl, ha, va in [
        (A, 'A', 'right', 'top'),  (B, 'B', 'left', 'top'),
        (C, 'C', 'left', 'bottom'),(D, 'D', 'right', 'bottom'),
        (E, 'E', 'left', 'center'),(F, 'F', 'right', 'center'),
    ]:
        dx = off if ha == 'left' else (-off if ha == 'right' else 0)
        dy = off if va == 'bottom' else (-off if va == 'top' else 0)
        ax.text(pt[0] + dx, pt[1] + dy, lbl, ha=ha, va=va, fontsize=FS)

    ax.text(6, -1,   'AB = 12', ha='center', va='top',    fontsize=10)
    ax.text(-1.5, 8, 'AD = 16', ha='right',  va='center', fontsize=10, rotation=90)

    ax.set_xlim(-3, 15)
    ax.set_ylim(-2.5, 18)
    save_fig('noveno_q14_rombo.png')


# ── 5. decimo_q14_paralelogramo.png ──────────────────────────────────────────
# gs_10_01: Rectángulo ABCD, P/Q/R/S dividen lados en razón 1:2 → paralelogramo PQRS
def fig_decimo_paralelogramo():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    W, H = 6, 4
    A = (0, 0); B = (W, 0); C = (W, H); D = (0, H)

    P = (W / 3,       0)
    Q = (W,           H / 3)
    R = (W - W / 3,   H)
    S = (0,           H - H / 3)

    pqrs = plt.Polygon([P, Q, R, S], closed=True, facecolor=GRAY,  edgecolor=BLACK, lw=LW)
    rect = plt.Polygon([A, B, C, D], closed=True, facecolor='none', edgecolor=BLACK, lw=LW)

    ax.add_patch(pqrs)
    ax.add_patch(rect)

    off = 0.28
    for pt, lbl, ha, va in [
        (A, 'A', 'right', 'top'),  (B, 'B', 'left', 'top'),
        (C, 'C', 'left', 'bottom'),(D, 'D', 'right', 'bottom'),
        (P, 'P', 'center', 'top'), (Q, 'Q', 'left', 'center'),
        (R, 'R', 'center', 'bottom'),(S, 'S', 'right', 'center'),
    ]:
        dx = off if ha == 'left' else (-off if ha == 'right' else 0)
        dy = off if va == 'bottom' else (-off if va == 'top' else 0)
        ax.text(pt[0] + dx, pt[1] + dy, lbl, ha=ha, va=va, fontsize=FS)

    # Marcas de los tercios en los lados
    for t in [1/3, 2/3]:
        ax.plot(W * t,   0,   'k|', ms=6, lw=1.5)
        ax.plot(W,       H*t, 'k_', ms=6, lw=1.5)
        ax.plot(W*(1-t), H,   'k|', ms=6, lw=1.5)
        ax.plot(0,       H*(1-t), 'k_', ms=6, lw=1.5)

    ax.set_xlim(-0.8, W + 0.8)
    ax.set_ylim(-0.8, H + 0.8)
    save_fig('decimo_q14_paralelogramo.png')


# ── 6. decimo_q15_semicirculo.png ────────────────────────────────────────────
# gs_10_02: Semicírculo diámetro 5, rectángulo inscrito de altura 2
def fig_decimo_semicirculo():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect('equal')
    ax.axis('off')

    r = 2.5   # radio = 5/2
    h = 2.0   # altura rectángulo
    x_rect = math.sqrt(r**2 - h**2)  # 1.5

    theta = np.linspace(0, np.pi, 200)
    x_arc = r * np.cos(theta)
    y_arc = r * np.sin(theta)

    # Fondo semicírculo
    ax.fill(np.append(x_arc, [-r, r]), np.append(y_arc, [0, 0]), color='#EEEEEE')
    ax.plot(x_arc, y_arc, 'k-', lw=LW)
    ax.plot([-r, r], [0, 0], 'k-', lw=LW)

    # Rectángulo inscrito
    rect = patches.Rectangle((-x_rect, 0), 2 * x_rect, h,
                              lw=LW, edgecolor=BLACK, facecolor=GRAY)
    ax.add_patch(rect)

    # Dimensiones
    ax.annotate('', xy=(-r, -0.4), xytext=(r, -0.4),
                arrowprops=dict(arrowstyle='<->', color=BLACK, lw=1))
    ax.text(0, -0.65, 'diámetro = 5', ha='center', va='top', fontsize=FS)
    ax.text(x_rect + 0.15, h / 2, '2', ha='left', va='center', fontsize=FS)

    # Ángulo recto
    s = 0.12
    ax.plot([-x_rect, -x_rect + s, -x_rect + s], [0, 0, s], 'k-', lw=1.2)

    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-1, 3)
    save_fig('decimo_q15_semicirculo.png')


# ── 7. decimo_q16_cuadrados_circulo.png ──────────────────────────────────────
# gs_10_03: Círculo radio 4, dos cuadrados iguales cubriéndolo
def fig_decimo_cuadrados_circulo():
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.axis('off')

    r = 4
    side = r * math.sqrt(2)  # lado del cuadrado; diagonal = 2r = diámetro
    half = side / 2

    theta = np.linspace(0, 2 * np.pi, 300)
    x_c = r * np.cos(theta)
    y_c = r * np.sin(theta)

    # Círculo gris
    ax.fill(x_c, y_c, color=GRAY)
    ax.plot(x_c, y_c, 'k-', lw=LW)

    # Cuadrado 1: cubre mitad superior; Cuadrado 2: cubre mitad inferior
    # Colocados de modo que su unión cubre el círculo
    sq1 = patches.Rectangle((-half, 0),   side, side, lw=LW, edgecolor=BLACK,
                             facecolor='white', alpha=0.6)
    sq2 = patches.Rectangle((-half, -side), side, side, lw=LW, edgecolor=BLACK,
                             facecolor='white', alpha=0.6)

    ax.add_patch(sq1)
    ax.add_patch(sq2)

    # Contorno del círculo encima
    ax.plot(x_c, y_c, 'k-', lw=LW)

    # Radio
    ax.plot([0, r], [0, 0], 'k-', lw=1.2)
    ax.text(r / 2, 0.25, f'r = {r}', ha='center', fontsize=FS)

    ax.set_xlim(-r - 1.5, r + 1.5)
    ax.set_ylim(-r - 1.5, r + 1.5)
    save_fig('decimo_q16_cuadrados_circulo.png')


# ── 8. decimo_q20_paralelogramo_ADEF.png ─────────────────────────────────────
# gs_10_04: Triángulo isósceles ABC (AB=AC=28, BC=20), paralelogramo ADEF
def fig_decimo_paralelogramo_ADEF():
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.set_aspect('equal')
    ax.axis('off')

    h = math.sqrt(28**2 - 10**2)   # ≈ 26.15
    B = (-10, 0); C = (10, 0); A = (0, h)

    # t tal que perimetro ADEF = 56
    # Perimetro = 2*(AB*t + BC*t) = 2*t*(28+20) = 96t = 56  →  t = 7/12
    t = 7 / 12
    D = (B[0] + t * (A[0] - B[0]), B[1] + t * (A[1] - B[1]))
    E = (B[0] + t * (C[0] - B[0]), B[1] + t * (C[1] - B[1]))
    F = (C[0] + t * (A[0] - C[0]), C[1] + t * (A[1] - C[1]))

    para = plt.Polygon([A, D, E, F], closed=True, facecolor=GRAY,  edgecolor=BLACK, lw=LW)
    tri  = plt.Polygon([A, B, C],   closed=True, facecolor='none', edgecolor=BLACK, lw=LW)

    ax.add_patch(para)
    ax.add_patch(tri)

    off = 0.9
    for pt, lbl, ha, va in [
        (A, 'A', 'center', 'bottom'), (B, 'B', 'right', 'top'),
        (C, 'C', 'left',  'top'),     (D, 'D', 'right', 'center'),
        (E, 'E', 'center','top'),     (F, 'F', 'left',  'center'),
    ]:
        dx = off if ha == 'left' else (-off if ha == 'right' else 0)
        dy = off if va == 'bottom' else (-off if va == 'top' else 0)
        ax.text(pt[0] + dx, pt[1] + dy, lbl, ha=ha, va=va, fontsize=FS)

    ax.text(-7, h / 2 + 2, 'AB=28', ha='right', va='center', fontsize=10, rotation=70)
    ax.text(7,  h / 2 + 2, 'AC=28', ha='left',  va='center', fontsize=10, rotation=-70)
    ax.text(0, -1.2, 'BC = 20', ha='center', va='top', fontsize=10)

    ax.set_xlim(-14, 14)
    ax.set_ylim(-3, h + 2.5)
    save_fig('decimo_q20_paralelogramo_ADEF.png')


# ── 9. undecimo_q14_paralelogramo.png ────────────────────────────────────────
# gs_11_01: Paralelogramo ABCD, E y F puntos medios, región sombreada
def fig_undecimo_paralelogramo():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    A = (0, 0); B = (6, 0); C = (8, 4); D = (2, 4)

    # E = punto medio de AB, F = punto medio de CD
    E = ((A[0] + B[0]) / 2, 0)
    F = ((C[0] + D[0]) / 2, 4)
    O = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)  # centro (intersección diagonales)

    # Sombrear región entre EF y diagonal AC (dos triángulos)
    tri1 = plt.Polygon([E, O, B], closed=True, facecolor=GRAY, edgecolor='none')
    tri2 = plt.Polygon([F, O, D], closed=True, facecolor=GRAY, edgecolor='none')
    ax.add_patch(tri1)
    ax.add_patch(tri2)

    # Paralelogramo
    para = plt.Polygon([A, B, C, D], closed=True, facecolor='none', edgecolor=BLACK, lw=LW)
    ax.add_patch(para)

    # Diagonales y segmento EF
    ax.plot([A[0], C[0]], [A[1], C[1]], 'k-', lw=1.5)
    ax.plot([B[0], D[0]], [B[1], D[1]], 'k-', lw=1.5)
    ax.plot([E[0], F[0]], [E[1], F[1]], 'k-', lw=1.5)

    off = 0.3
    for pt, lbl, ha, va in [
        (A, 'A', 'right', 'top'),  (B, 'B', 'left', 'top'),
        (C, 'C', 'left', 'bottom'),(D, 'D', 'right', 'bottom'),
        (E, 'E', 'center', 'top'), (F, 'F', 'center', 'bottom'),
    ]:
        dx = off if ha == 'left' else (-off if ha == 'right' else 0)
        dy = off if va == 'bottom' else (-off if va == 'top' else 0)
        ax.text(pt[0] + dx, pt[1] + dy, lbl, ha=ha, va=va, fontsize=FS)

    ax.set_xlim(-0.8, 9.5)
    ax.set_ylim(-0.8, 5)
    save_fig('undecimo_q14_paralelogramo.png')


# ── 10. undecimo_q15_equilatero_XYZ.png ──────────────────────────────────────
# gs_11_02: Triángulo equilátero XYZ, lados divididos en tercios, hexágono sombreado
def fig_undecimo_equilatero():
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    s = 6
    X = (0, 0)
    Y = (s, 0)
    Z = (s / 2, s * math.sqrt(3) / 2)

    def third(P, Q, k):
        """Punto a k/3 del segmento PQ."""
        return (P[0] + k * (Q[0] - P[0]) / 3,
                P[1] + k * (Q[1] - P[1]) / 3)

    # Puntos a 1/3 y 2/3 de cada lado
    A = third(X, Y, 1);  B = third(X, Y, 2)
    C = third(Y, Z, 1);  D = third(Y, Z, 2)
    E = third(Z, X, 1);  F = third(Z, X, 2)

    # Hexágono convexo interior: A, C, E alternados con B, D, F
    # Ordenado por ángulo alrededor del centroide
    cx = (X[0] + Y[0] + Z[0]) / 3
    cy = (X[1] + Y[1] + Z[1]) / 3
    pts = [A, C, E, B, D, F]
    pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    hex_poly = plt.Polygon(pts, closed=True, facecolor=GRAY, edgecolor=BLACK, lw=LW)
    ax.add_patch(hex_poly)

    tri = plt.Polygon([X, Y, Z], closed=True, facecolor='none', edgecolor=BLACK, lw=LW)
    ax.add_patch(tri)

    # Líneas trisectoras
    ax.plot([A[0], D[0]], [A[1], D[1]], 'k-', lw=1)
    ax.plot([B[0], E[0]], [B[1], E[1]], 'k-', lw=1)
    ax.plot([C[0], F[0]], [C[1], F[1]], 'k-', lw=1)

    off = 0.35
    ax.text(X[0] - off, X[1] - off, 'X', ha='right', va='top',    fontsize=FS + 2)
    ax.text(Y[0] + off, Y[1] - off, 'Y', ha='left',  va='top',    fontsize=FS + 2)
    ax.text(Z[0],       Z[1] + off, 'Z', ha='center', va='bottom', fontsize=FS + 2)

    for pt in [A, B, C, D, E, F]:
        ax.plot(pt[0], pt[1], 'ko', ms=3)

    ax.set_xlim(-0.8, s + 0.8)
    ax.set_ylim(-0.8, s * math.sqrt(3) / 2 + 0.8)
    save_fig('undecimo_q15_equilatero_XYZ.png')


# ── 11. undecimo_q16_triangulo_P.png ─────────────────────────────────────────
# gs_11_03: Triángulo rectángulo ABC, punto P interior, tres triángulos con áreas 2, 8, 18
def fig_undecimo_triangulo_P():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    # Área total = (sqrt2 + sqrt8 + sqrt18)² = (sqrt2 + 2sqrt2 + 3sqrt2)² = 72
    # Triángulo rectángulo con catetos a y b: ab/2 = 72  → elegir a=12, b=12
    C = (0, 0); B = (12, 0); A = (0, 12)

    # P interior
    P = (3, 3)

    shades = ['#AAAAAA', GRAY, '#888888']
    tris   = [[P, A, B], [P, B, C], [P, C, A]]
    areas  = ['2', '8', '18']
    labels_pos = [(4.5, 8), (7, 1.2), (1.2, 5.5)]

    for verts, shade in zip(tris, shades):
        ax.add_patch(plt.Polygon(verts, closed=True, facecolor=shade,
                                 edgecolor=BLACK, lw=LW, alpha=0.7))

    for (lx, ly), area in zip(labels_pos, areas):
        ax.text(lx, ly, area, ha='center', va='center', fontsize=12, fontweight='bold')

    for V in [A, B, C]:
        ax.plot([P[0], V[0]], [P[1], V[1]], 'k-', lw=1.2)

    # Ángulo recto en C
    s = 0.6
    ax.plot([s, s, 0], [0, s, s], 'k-', lw=1.5)

    # Etiquetas
    off = 0.5
    ax.text(A[0] - off, A[1],       'A', ha='right',  va='center', fontsize=FS)
    ax.text(B[0] + off, B[1] - off, 'B', ha='left',   va='top',    fontsize=FS)
    ax.text(C[0] - off, C[1] - off, 'C', ha='right',  va='top',    fontsize=FS)
    ax.text(P[0] + 0.3, P[1] + 0.3, 'P', ha='left',   va='bottom', fontsize=FS)

    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(-1.2, 13.5)
    save_fig('undecimo_q16_triangulo_P.png')


# ── 12. undecimo_q13_tres_cuadrados.png ──────────────────────────────────────
# gs_11_04: Tres cuadrados (lados 9, ?, 4) vértices A,B,C colineales
def fig_undecimo_tres_cuadrados():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    # x² = 36  →  x = 6
    s1, s2, s3 = 9, 6, 4

    # Cuadrado 1 (9): x[0..9], y[0..9]
    # Cuadrado 2 (6): x[9..15], y[0..6]
    # Cuadrado 3 (4): x[15..19], y[0..4]
    # A = esquina sup-der del cuadrado 1 = (9, 9)
    # B = esquina sup-der del cuadrado 2 = (15, 6)
    # C = esquina sup-der del cuadrado 3 = (19, 4)
    # Colinealidad: pendiente AB = (6-9)/(15-9) = -3/6 = -0.5
    #               pendiente AC = (4-9)/(19-9) = -5/10 = -0.5  ✓

    sq1 = patches.Rectangle((0,  0), s1, s1, lw=LW, edgecolor=BLACK, facecolor='white')
    sq2 = patches.Rectangle((s1, 0), s2, s2, lw=LW, edgecolor=BLACK, facecolor=GRAY)
    sq3 = patches.Rectangle((s1 + s2, 0), s3, s3, lw=LW, edgecolor=BLACK, facecolor='white')

    ax.add_patch(sq1)
    ax.add_patch(sq2)
    ax.add_patch(sq3)

    # Línea colineal A-B-C
    A = (s1,          s1)
    B = (s1 + s2,     s2)
    C = (s1 + s2 + s3, s3)

    ax.plot([A[0], C[0]], [A[1], C[1]], 'k-', lw=2)
    for pt in [A, B, C]:
        ax.plot(pt[0], pt[1], 'ko', ms=6, zorder=5)

    off = 0.45
    ax.text(A[0] + off, A[1] + off, 'A', ha='left', va='bottom', fontsize=FS)
    ax.text(B[0] + off, B[1] + off, 'B', ha='left', va='bottom', fontsize=FS)
    ax.text(C[0] + off, C[1] + off, 'C', ha='left', va='bottom', fontsize=FS)

    ax.text(s1 / 2,             -0.7, '9', ha='center', va='top', fontsize=11)
    ax.text(s1 + s2 / 2,        -0.7, '?', ha='center', va='top', fontsize=11)
    ax.text(s1 + s2 + s3 / 2,   -0.7, '4', ha='center', va='top', fontsize=11)

    ax.set_xlim(-0.5, s1 + s2 + s3 + 1.5)
    ax.set_ylim(-1.5, s1 + 1.5)
    save_fig('undecimo_q13_tres_cuadrados.png')


# ── 13. primaria_q14_cuadrados.png ───────────────────────────────────────────
# gs_p_01: Tres cuadrados I, II, III conectados (perímetros 12, 24, ?)
def fig_primaria_cuadrados():
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_aspect('equal')
    ax.axis('off')

    # Lados: perímetro 12 → lado 3; perímetro 24 → lado 6; perímetro 36 → lado 9
    s1, s2, s3 = 3, 6, 9

    sq1 = patches.Rectangle((0,        0), s1, s1, lw=LW, edgecolor=BLACK, facecolor='#EEEEEE')
    sq2 = patches.Rectangle((s1,       0), s2, s2, lw=LW, edgecolor=BLACK, facecolor=GRAY)
    sq3 = patches.Rectangle((s1 + s2,  0), s3, s3, lw=LW, edgecolor=BLACK, facecolor='#DDDDDD')

    ax.add_patch(sq1)
    ax.add_patch(sq2)
    ax.add_patch(sq3)

    ax.text(s1 / 2,              s1 / 2,  'I',   ha='center', va='center', fontsize=FS + 2, fontweight='bold')
    ax.text(s1 + s2 / 2,         s2 / 2,  'II',  ha='center', va='center', fontsize=FS + 2, fontweight='bold')
    ax.text(s1 + s2 + s3 / 2,    s3 / 2,  'III', ha='center', va='center', fontsize=FS + 2, fontweight='bold')

    ax.text(s1 / 2,              -0.6,  'P = 12', ha='center', va='top', fontsize=10)
    ax.text(s1 + s2 / 2,         -0.6,  'P = 24', ha='center', va='top', fontsize=10)
    ax.text(s1 + s2 + s3 / 2,    -0.6,  'P = ?',  ha='center', va='top', fontsize=10)

    ax.set_xlim(-0.5, s1 + s2 + s3 + 0.5)
    ax.set_ylim(-1.5, s3 + 0.8)
    save_fig('primaria_q14_cuadrados.png')


# ── 14. decimo_q12_barras.png ─────────────────────────────────────────────────
# ps_10_01: Diagrama de barras — notas 1→2, 2→4, 3→7, 4→5, 5→2
def fig_decimo_barras():
    fig, ax = plt.subplots(figsize=(6, 4))

    notas = [1, 2, 3, 4, 5]
    freqs = [2, 4, 7, 5, 2]

    bars = ax.bar(notas, freqs, color=GRAY, edgecolor=BLACK, linewidth=LW, width=0.6)

    ax.set_xlabel('Nota',       fontsize=FS)
    ax.set_ylabel('Frecuencia', fontsize=FS)
    ax.set_title('Resultados del examen', fontsize=FS)
    ax.set_xticks(notas)
    ax.set_yticks(range(0, 9))
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0, 8.5)

    for bar, f in zip(bars, freqs):
        ax.text(bar.get_x() + bar.get_width() / 2, f + 0.15,
                str(f), ha='center', va='bottom', fontsize=11)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    save_fig('decimo_q12_barras.png')


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f'Generando 14 figuras en {OUTPUT_DIR}/ ...\n')
    fig_septimo_cuadrados()
    fig_octavo_rectangulos()
    fig_octavo_centro_O()
    fig_noveno_rombo()
    fig_decimo_paralelogramo()
    fig_decimo_semicirculo()
    fig_decimo_cuadrados_circulo()
    fig_decimo_paralelogramo_ADEF()
    fig_undecimo_paralelogramo()
    fig_undecimo_equilatero()
    fig_undecimo_triangulo_P()
    fig_undecimo_tres_cuadrados()
    fig_primaria_cuadrados()
    fig_decimo_barras()
    print('\nListo. 14 figuras generadas.')
