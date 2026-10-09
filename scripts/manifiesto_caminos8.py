"""Construye el manifiesto de páginas con ejercicios de Los Caminos del Saber 8.

El PDF es un escaneo sin capa de texto, así que no hay forma de buscar "Afianzo
competencias" como cadena. Pero ese banner es un rectángulo azul oscuro sólido
en la mitad izquierda de la página, y eso sí se detecta escaneando fila por
fila: en la fila más azul de una página con banner, el azul llena ~0,58 del
ancho de la franja, y en una sin banner no pasa de ~0,12. El banner **no** está
siempre arriba — en la página 12 aparece a media altura —, así que hay que
recorrer toda la altura y no solo el encabezado.

Las secciones de cierre de unidad (ejercicios y problemas para repasar, "y esto
que aprendí", "trabaja con…") no llevan ese banner, así que salen de la tabla
de contenidos del propio libro, que sí es fiable.

    python scripts/manifiesto_caminos8.py            # reconstruye el manifiesto
    python scripts/manifiesto_caminos8.py --umbral 3 # ajusta el corte, en %

Escribe items/source/caminos8/_manifiesto.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PDF = Path(
    r"C:\Users\orian\OneDrive\Documentos\IE Los Andes\Libros\Libros santillana 8 y 9"
    r"\los-caminos-del-saber-matematicas-8-pdf1.pdf"
)
DESTINO = ROOT / "items" / "source" / "caminos8" / "_manifiesto.json"
PAGINAS = 336

# De la tabla de contenidos (páginas 6 y 7). El número es la página donde empieza
# la unidad; las secciones de cierre traen su propia página.
UNIDADES = [
    (
        1,
        "Conjuntos numéricos",
        8,
        {"ejercicios": 26, "problemas": 28, "aplicacion": 30, "software": 32},
    ),
    (
        2,
        "Expresiones algebraicas",
        34,
        {"ejercicios": 46, "problemas": 48, "aplicacion": 50, "software": 51},
    ),
    (
        3,
        "Operaciones entre polinomios",
        52,
        {"ejercicios": 74, "problemas": 76, "aplicacion": 78, "software": 79},
    ),
    (
        4,
        "Productos notables y cocientes notables",
        80,
        {"ejercicios": 100, "problemas": 102, "aplicacion": 104, "software": 105},
    ),
    (
        5,
        "Factorización",
        106,
        {"ejercicios": 138, "problemas": 140, "aplicacion": 142, "software": 143},
    ),
    (
        6,
        "Fracciones algebraicas",
        144,
        {"ejercicios": 176, "problemas": 178, "aplicacion": 180, "software": 181},
    ),
    (
        7,
        "Ecuaciones e inecuaciones",
        182,
        {"ejercicios": 214, "problemas": 216, "aplicacion": 218, "software": 219},
    ),
    (
        8,
        "Función lineal",
        220,
        {"ejercicios": 248, "problemas": 250, "aplicacion": 252, "software": 253},
    ),
    (
        9,
        "Geometría",
        254,
        {"ejercicios": 284, "problemas": 286, "aplicacion": 288, "software": 290},
    ),
    (
        10,
        "Estadística y probabilidad",
        292,
        {"ejercicios": 326, "problemas": 328, "aplicacion": 330, "software": 332},
    ),
]
FIN_CONTENIDO = 333  # 334 glosario, 336 bibliografía

# Falsos positivos confirmados visualmente. El detector reacciona a otros
# rectángulos azules de estas páginas, aunque no exista un banner de ejercicios.
SIN_EJERCICIOS = {
    18: "Página teórica sobre irracionales y construcción de √2; sin consigna impresa.",
    25: "Infografía sobre el número de oro y el número cordobés; sin consigna impresa.",
    28: "Problema modelo completamente resuelto paso a paso; no es una actividad para responder.",
    36: "Página teórica de lenguaje algebraico con ejemplos completamente resueltos; sin actividad para responder.",
    48: "Problema modelo completamente resuelto paso a paso; no es una actividad para responder.",
    54: "Página teórica de adición y sustracción de monomios con ejemplos completamente resueltos; sin actividad para responder.",
    58: "Página teórica de signos de agrupación con ejemplos completamente resueltos; sin actividad para responder.",
}

# Falsos negativos confirmados visualmente. No tienen el banner azul de
# "Afianzo competencias", pero sí una consigna lateral "Matemáticamente".
CON_EJERCICIOS_FORZADAS = {82, 294}


def _pdftoppm() -> str:
    ruta = Path(
        r"C:\Users\orian\.cache\codex-runtimes\codex-primary-runtime\dependencies\native"
        r"\poppler\Library\bin\pdftoppm.exe"
    )
    if ruta.exists():
        return str(ruta)
    encontrado = shutil.which("pdftoppm")
    if not encontrado:
        raise SystemExit("No se encontró pdftoppm.")
    return encontrado


def _es_azul_banner(pixel) -> bool:
    r, g, b = pixel
    return b > 90 and b - r > 40 and b - g > 30 and r < 130


def _fila_mas_azul(png: Path) -> float:
    """Fracción del ancho que ocupa el azul del banner en su fila más azul."""
    im = Image.open(png).convert("RGB")
    w, h = im.size
    caja = im.crop((int(0.08 * w), int(0.05 * h), int(0.45 * w), int(0.97 * h)))
    ancho, alto = caja.size
    datos = list(caja.get_flattened_data())
    mejor = 0.0
    for i in range(alto):
        fila = datos[i * ancho : (i + 1) * ancho]
        mejor = max(mejor, sum(1 for p in fila if _es_azul_banner(p)) / ancho)
    return mejor


def paginas_con_banner(dpi: int, umbral: float) -> list[int]:
    """Renderiza el libro entero de una sola pasada y busca el banner en cada página."""
    temporal_base = ROOT / "tmp" / "manifiesto_caminos8"
    temporal_base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temporal_base) as tmp:
        subprocess.run(
            [_pdftoppm(), "-r", str(dpi), "-png", str(PDF), str(Path(tmp) / "p")],
            check=True,
            capture_output=True,
        )
        return [
            int(png.stem.split("-")[-1])
            for png in sorted(Path(tmp).glob("p-*.png"))
            if _fila_mas_azul(png) >= umbral
        ]


def unidad_de(pagina: int) -> int:
    ultima = 0
    for numero, _, inicio, _ in UNIDADES:
        if pagina >= inicio:
            ultima = numero
    return ultima


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dpi", type=int, default=80)
    parser.add_argument(
        "--umbral",
        type=float,
        default=0.30,
        help="fracción mínima de ancho azul en la fila más azul (0.30)",
    )
    args = parser.parse_args()

    afianzo = sorted(set(paginas_con_banner(args.dpi, args.umbral)) | CON_EJERCICIOS_FORZADAS)

    # Las secciones de cierre mandan sobre el detector: el banner azul tambien
    # aparece en la portada, el indice y las paginas de software.
    secciones: dict[int, str] = {}
    for numero, _, inicio, cierres in UNIDADES:
        hitos = sorted(cierres.items(), key=lambda kv: kv[1])
        siguiente_unidad = next(
            (i for n, _, i, _ in UNIDADES if n == numero + 1), FIN_CONTENIDO + 1
        )
        for idx, (clase, pagina) in enumerate(hitos):
            fin = hitos[idx + 1][1] if idx + 1 < len(hitos) else siguiente_unidad
            for p in range(pagina, fin):
                secciones[p] = clase
        # La actividad diagnóstica "Lo que sabes" está en la primera página
        # de la apertura. La segunda página completa la doble página con una
        # infografía, pero no contiene consignas.
        secciones[inicio] = "lo_que_sabes"

    primera_unidad = UNIDADES[0][2]
    segundas_paginas_apertura = {inicio + 1 for _, _, inicio, _ in UNIDADES}
    for p in afianzo:
        if (
            primera_unidad <= p <= FIN_CONTENIDO
            and p not in segundas_paginas_apertura
            and p not in SIN_EJERCICIOS
        ):
            secciones.setdefault(p, "afianzo")

    manifiesto = {
        "libro": "Los Caminos del Saber Matemáticas 8 (Santillana)",
        "paginas_pdf": PAGINAS,
        "offset_pdf_a_libro": 0,
        "unidades": [{"unidad": n, "titulo": t, "pagina_inicio": i} for n, t, i, _ in UNIDADES],
        "paginas_sin_ejercicios": [
            {"pagina": pagina, "motivo": motivo}
            for pagina, motivo in sorted(SIN_EJERCICIOS.items())
        ],
        "paginas": [
            {"pagina": p, "unidad": unidad_de(p), "clase": secciones[p]}
            for p in sorted(secciones)
            if p <= FIN_CONTENIDO and p not in SIN_EJERCICIOS
        ],
    }
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    por_clase: dict[str, int] = {}
    for p in manifiesto["paginas"]:
        por_clase[p["clase"]] = por_clase.get(p["clase"], 0) + 1
    print(f"{len(manifiesto['paginas'])} páginas con ejercicios -> {DESTINO.name}")
    for clase, n in sorted(por_clase.items(), key=lambda kv: -kv[1]):
        print(f"  {clase:14} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
