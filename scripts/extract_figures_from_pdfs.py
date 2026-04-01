#!/usr/bin/env python3
"""Extrae figuras geométricas de los PDFs de Olimpiadas UdeA 2020.

Cada figura se recorta de una región precisa de una página específica.
Las coordenadas están en puntos PDF (72 puntos = 1 pulgada).
La página se renderiza a 3x zoom para buena calidad.

Ejecutar desde la raíz del repo:
    python scripts/extract_figures_from_pdfs.py
"""

import fitz  # PyMuPDF
import os

OUTPUT_DIR = 'items/images'
PDF_DIR = 'Semillero/OLIMPIADAS-2020'

# Coordenadas derivadas de get_image_rects() — posiciones exactas de cada
# imagen embebida en el PDF, con 12 pts de margen por lado.
# Formato: (x0, y0, x1, y1) en puntos PDF (página A4 = 595×842 pts)

PAD = 12  # margen de recorte

EXTRACTIONS = {
    # =============================================
    # OCTAVO  (pdf page 1 = índice 1, page 2 = índice 2)
    # =============================================

    # Q13: Tres cuadrados sobre triángulo — xref=103 en p1
    ('2020-Taller-OctavoEstudiantes.pdf', 1, (367-PAD, 319-PAD, 537+PAD, 481+PAD)):
        'octavo_q13_cuadrados_triangulo.png',

    # Q14: Rectángulo 20×32 en 108×98 — xref=104 en p1
    ('2020-Taller-OctavoEstudiantes.pdf', 1, (367-PAD, 673-PAD, 537+PAD, 779+PAD)):
        'octavo_q14_rectangulos.png',

    # Q15: Rectángulo con centro O, triángulo OPQ — xref=105 en p2
    ('2020-Taller-OctavoEstudiantes.pdf', 2, (86-PAD, 202-PAD, 228+PAD, 349+PAD)):
        'octavo_q15_centro_O.png',

    # Q16: Cuadrado PQRS inscrito en círculo en ABCD — xref=158 en p2
    ('2020-Taller-OctavoEstudiantes.pdf', 2, (58-PAD, 503-PAD, 256+PAD, 660+PAD)):
        'octavo_q16_cuadrado_inscrito.png',

    # Q20: Triángulo ABC con DE‖BC, FE‖DC — xref=159 en p2
    ('2020-Taller-OctavoEstudiantes.pdf', 2, (381-PAD, 538-PAD, 523+PAD, 636+PAD)):
        'octavo_q20_triangulo_paralelas.png',

    # =============================================
    # SÉPTIMO
    # =============================================

    # Q13: Triángulo isósceles + cuadrado superpuestos — xref=103 en p1
    ('2020-Taller-Septimo-Estudiantes.pdf', 1, (367-PAD, 544-PAD, 537+PAD, 618+PAD)):
        'septimo_q13_superposicion.png',

    # Q14: Dos cuadrados (6cm y 4cm) superpuestos — xref=105 en p2
    ('2020-Taller-Septimo-Estudiantes.pdf', 2, (58-PAD, 45-PAD, 256+PAD, 167+PAD)):
        'septimo_q14_cuadrados.png',

    # Q15: Dos cuadrados cortados en 5 piezas — xref=156 en p2
    ('2020-Taller-Septimo-Estudiantes.pdf', 2, (72-PAD, 371-PAD, 242+PAD, 485+PAD)):
        'septimo_q15_corte_cuadrados.png',

    # =============================================
    # NOVENO
    # =============================================

    # Q14: Rombo AECF en rectángulo ABCD — xref=110 en p1
    ('2020-Taller-NovenoEstudiantes.pdf', 1, (367-PAD, 526-PAD, 537+PAD, 666+PAD)):
        'noveno_q14_rombo.png',

    # Q15: Triángulo ABC rectángulo con cuadrado APRS — xref=112 en p2
    ('2020-Taller-NovenoEstudiantes.pdf', 2, (86-PAD, 105-PAD, 228+PAD, 277+PAD)):
        'noveno_q15_triangulo_cuadrado.png',

    # Q16: Sucesión de triángulos rectángulos isósceles — xref=163 en p2
    ('2020-Taller-NovenoEstudiantes.pdf', 2, (86-PAD, 459-PAD, 228+PAD, 618+PAD)):
        'noveno_q16_sucesion_triangulos.png',

    # Q20: Triángulo isósceles con M y N puntos medios — xref=164 en p2
    ('2020-Taller-NovenoEstudiantes.pdf', 2, (381-PAD, 520-PAD, 523+PAD, 617+PAD)):
        'noveno_q20_isosceles_medianas.png',

    # =============================================
    # DÉCIMO
    # =============================================

    # Q12: Diagrama de barras (notas 1-5) — xref=101 en p1
    ('2020-Taller-DecimoEstudiantes.pdf', 1, (395-PAD, 206-PAD, 509+PAD, 311+PAD)):
        'decimo_q12_barras.png',

    # Q13: Triángulo rectángulo AX=AD, CY=CD — xref=102 en p1
    ('2020-Taller-DecimoEstudiantes.pdf', 1, (353-PAD, 557-PAD, 551+PAD, 633+PAD)):
        'decimo_q13_triangulo_XDY.png',

    # Q14: Rectángulo ABCD con PQRS — xref=104 en p2
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (100-PAD, 45-PAD, 214+PAD, 114+PAD)):
        'decimo_q14_paralelogramo.png',

    # Q15: Semicírculo diámetro 5, rectángulo altura 2 — xref=158 en p2
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (86-PAD, 307-PAD, 228+PAD, 405+PAD)):
        'decimo_q15_semicirculo.png',

    # Q16: Dos cuadrados cubriendo círculo radio 4 — xref=159 en p2
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (115-PAD, 585-PAD, 200+PAD, 667+PAD)):
        'decimo_q16_cuadrados_circulo.png',

    # Q20: Triángulo ABC con paralelogramo ADEF — xref=160 en p2
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (395-PAD, 526-PAD, 509+PAD, 667+PAD)):
        'decimo_q20_paralelogramo_ADEF.png',

    # =============================================
    # UNDÉCIMO
    # =============================================

    # Q4: Tablero/grid con puntos A, B, C — xref=52 en p0
    ('2020-Taller-OnceEstudiantes.pdf', 0, (395-PAD, 174-PAD, 509+PAD, 244+PAD)):
        'undecimo_q4_tablero.png',

    # Q13: Tres cuadrados (lados 9, ?, 4) — xref=109 en p1
    ('2020-Taller-OnceEstudiantes.pdf', 1, (367-PAD, 242-PAD, 537+PAD, 337+PAD)):
        'undecimo_q13_tres_cuadrados.png',

    # Q14: Paralelogramo ABCD con E y F puntos medios — xref=110 en p1
    ('2020-Taller-OnceEstudiantes.pdf', 1, (367-PAD, 547-PAD, 537+PAD, 621+PAD)):
        'undecimo_q14_paralelogramo.png',

    # Q15: Triángulo equilátero XYZ dividido — xref=111 en p2
    ('2020-Taller-OnceEstudiantes.pdf', 2, (100-PAD, 45-PAD, 214+PAD, 154+PAD)):
        'undecimo_q15_equilatero_XYZ.png',

    # Q16: Triángulo rectángulo ABC con punto P — xref=166 en p2
    ('2020-Taller-OnceEstudiantes.pdf', 2, (72-PAD, 364-PAD, 242+PAD, 517+PAD)):
        'undecimo_q16_triangulo_P.png',

    # Q20: Rectángulo con diagonal BD — xref=167 en p2
    ('2020-Taller-OnceEstudiantes.pdf', 2, (395-PAD, 484-PAD, 509+PAD, 577+PAD)):
        'undecimo_q20_rectangulo_diagonal.png',

    # =============================================
    # SEXTO
    # =============================================

    # Q1: Cuadrícula de rectángulos — xref=52 en p0
    ('2020-Taller-Sexto-Estudiantes.pdf', 0, (86-PAD, 221-PAD, 228+PAD, 332+PAD)):
        'sexto_q1_rectangulos.png',

    # Q14: Circuito para autos — xref=105 en p2
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (72-PAD, 45-PAD, 242+PAD, 145+PAD)):
        'sexto_q14_circuito.png',

    # Q15: Triángulo equilátero + cuadrado (casa) — xref=159 en p2
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (100-PAD, 338-PAD, 214+PAD, 525+PAD)):
        'sexto_q15_triangulo_cuadrado.png',

    # Q16: Rectángulo ABCD sombreado — xref=160 en p2 (y0+12 extra para excluir texto)
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (72-PAD, 665, 242+PAD, 776+PAD)):
        'sexto_q16_rectangulo_sombreado.png',

    # Q20: Cuadrado exterior con rombo interior — xref=161 en p2
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (381-PAD, 610-PAD, 523+PAD, 745+PAD)):
        'sexto_q20_cuadrado_rombo.png',

    # =============================================
    # PRIMARIA
    # =============================================

    # Q13: Figura tipo L con segmento CD — xref=109 en p1
    ('2020-TallerPrimariaEstudiantes.pdf', 1, (339-PAD, 391-PAD, 565+PAD, 529+PAD)):
        'primaria_q13_CD.png',

    # Q14: Tres cuadrados I, II, III — xref=110 en p1
    ('2020-TallerPrimariaEstudiantes.pdf', 1, (395-PAD, 690-PAD, 509+PAD, 761+PAD)):
        'primaria_q14_cuadrados.png',

    # Q16: Arreglo 3×3 de puntos — xref=164 en p2
    ('2020-TallerPrimariaEstudiantes.pdf', 2, (115-PAD, 317-PAD, 200+PAD, 395+PAD)):
        'primaria_q16_puntos.png',

    # Q20: Triángulo sombreado en rectángulo — xref=165 en p2
    ('2020-TallerPrimariaEstudiantes.pdf', 2, (381-PAD, 409-PAD, 523+PAD, 480+PAD)):
        'primaria_q20_triangulo_rect.png',
}


def extract_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ok = 0
    fail = 0

    for (pdf_name, page_num, rect), out_name in EXTRACTIONS.items():
        pdf_path = os.path.join(PDF_DIR, pdf_name)

        if not os.path.exists(pdf_path):
            print(f'  SKIP: {pdf_name} no encontrado en {PDF_DIR}')
            fail += 1
            continue

        try:
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                print(f'  SKIP: pagina {page_num} no existe en {pdf_name} ({len(doc)} paginas)')
                doc.close()
                fail += 1
                continue

            page = doc[page_num]
            clip = fitz.Rect(*rect)

            # Renderizar a 3x zoom para buena calidad
            mat = fitz.Matrix(3, 3)
            pix = page.get_pixmap(matrix=mat, clip=clip)

            out_path = os.path.join(OUTPUT_DIR, out_name)
            pix.save(out_path)

            size_kb = os.path.getsize(out_path) // 1024
            print(f'  OK: {out_name} ({size_kb}KB)')
            ok += 1
            doc.close()

        except Exception as e:
            print(f'  ERROR: {out_name} -> {e}')
            fail += 1

    print(f'\nResultado: {ok} OK, {fail} fallos')
    print(f'Figuras en: {OUTPUT_DIR}/')


def verify_image_paths():
    """Verifica que cada image_path en los JSON apunte a un archivo existente."""
    import json
    import glob as _glob

    bank_dir = 'items/bank'
    errors = []
    total = 0

    all_files = sorted(
        _glob.glob(os.path.join(bank_dir, '*.json')) +
        _glob.glob(os.path.join(bank_dir, 'semillero', '*.json'))
    )

    for f in all_files:
        items = json.load(open(f, encoding='utf-8'))
        for item in items:
            img = item.get('image_path', '') or item.get('image_url', '')
            if img:
                total += 1
                if not os.path.exists(img):
                    errors.append(f'  {item["id"]} -> {img} NO EXISTE')

    if errors:
        print(f'\n{len(errors)} image_path rotos (de {total} con imagen):')
        for e in errors:
            print(e)
    else:
        print(f'\nTodos los image_path apuntan a archivos existentes ({total} con imagen)')


if __name__ == '__main__':
    print('=== Extrayendo figuras de PDFs ===\n')
    extract_all()
    print('\n=== Verificando image_path en JSONs ===')
    verify_image_paths()
