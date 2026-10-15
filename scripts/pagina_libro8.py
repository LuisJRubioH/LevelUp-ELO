"""Renderiza una página (o una banda de ella) de un libro de 8.° a PNG.

Los dos libros de Santillana son escaneos sin capa de texto usable, así que
transcribir exige mirar la página. A 200 dpi y recortando la banda de interés,
las expresiones con signos de agrupación se leen sin ambigüedad — que es donde
el OCR falla.

    python scripts/pagina_libro8.py hipertexto 14                 # página completa
    python scripts/pagina_libro8.py caminos 110 --y 0.62 0.83     # banda vertical
    python scripts/pagina_libro8.py caminos 110 --y 0.6 0.9 --x 0.5 1.0 --dpi 260

Escribe en tmp/<libro>/ (ignorado por git).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LIBROS_DIR = Path(r"C:\Users\orian\OneDrive\Documentos\IE Los Andes\Libros\Libros santillana 8 y 9")

# nombre corto -> (archivo PDF, carpeta de salida, páginas)
LIBROS = {
    "hipertexto": ("hipertexto-matematicas-8.pdf", "hipertexto8", 304),
    "caminos": ("los-caminos-del-saber-matematicas-8-pdf1.pdf", "caminos8", 336),
}

POPPLER = Path(
    r"C:\Users\orian\.cache\codex-runtimes\codex-primary-runtime\dependencies\native"
    r"\poppler\Library\bin\pdftoppm.exe"
)


def _pdftoppm() -> str:
    if POPPLER.exists():
        return str(POPPLER)
    encontrado = shutil.which("pdftoppm")
    if not encontrado:
        raise SystemExit("No se encontró pdftoppm (poppler ni MiKTeX).")
    return encontrado


def renderizar(libro: str, pagina: int, dpi: int) -> Path:
    archivo, carpeta, _ = LIBROS[libro]
    salida = ROOT / "tmp" / carpeta
    salida.mkdir(parents=True, exist_ok=True)
    prefijo = salida / f"p{pagina:03d}_{dpi}"
    destino = prefijo.with_suffix(".png")
    if not destino.exists():
        subprocess.run(
            [
                _pdftoppm(),
                "-f",
                str(pagina),
                "-l",
                str(pagina),
                "-r",
                str(dpi),
                "-png",
                "-singlefile",
                str(LIBROS_DIR / archivo),
                str(prefijo),
            ],
            check=True,
            capture_output=True,
        )
    return destino


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("libro", choices=sorted(LIBROS), help="hipertexto o caminos")
    parser.add_argument("pagina", type=int, help="número de página del PDF")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument(
        "--y",
        type=float,
        nargs=2,
        metavar=("Y0", "Y1"),
        help="banda vertical en fracción de la altura, p. ej. 0.6 0.9",
    )
    parser.add_argument(
        "--x",
        type=float,
        nargs=2,
        metavar=("X0", "X1"),
        help="banda horizontal en fracción del ancho",
    )
    parser.add_argument("--max-lado", type=int, default=2200, help="lado máximo del PNG resultante")
    args = parser.parse_args()

    total = LIBROS[args.libro][2]
    if not 1 <= args.pagina <= total:
        raise SystemExit(f"{args.libro} tiene {total} páginas; pediste la {args.pagina}.")

    completa = renderizar(args.libro, args.pagina, args.dpi)
    im = Image.open(completa)
    if not (args.y or args.x):
        print(completa, im.size)
        return 0

    w, h = im.size
    x0, x1 = args.x or (0.0, 1.0)
    y0, y1 = args.y or (0.0, 1.0)
    rec = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    if max(rec.size) > args.max_lado:
        escala = args.max_lado / max(rec.size)
        rec = rec.resize((int(rec.width * escala), int(rec.height * escala)), Image.LANCZOS)
    carpeta = LIBROS[args.libro][1]
    destino = (
        ROOT
        / "tmp"
        / carpeta
        / f"p{args.pagina:03d}_{int(y0*100)}{int(y1*100)}_{int(x0*100)}{int(x1*100)}.png"
    )
    rec.save(destino)
    print(destino, rec.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
