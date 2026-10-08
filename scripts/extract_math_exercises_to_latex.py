"""Build a page-auditable LaTeX exercise anthology from two scanned textbooks.

The source PDFs do not contain a usable text layer.  This script consumes the
Windows OCR output created in ``tmp/pdfs`` and keeps a source-page image for
every exercise block whose statement depends on a diagram, graph, table, or
other spatial layout.

Run from the repository root after ``tmp/pdfs/book1_ocr.txt`` and
``tmp/pdfs/book2_ocr.txt`` have been generated.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "latex" / "listas_ejercicios_matematicas_8"


@dataclass(frozen=True)
class Unit:
    number: int
    title: str
    start: int
    end: int
    review_start: int | None = None
    topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class Book:
    key: str
    title: str
    ocr_path: Path
    image_dir: Path
    units: tuple[Unit, ...]
    style: str


@dataclass(frozen=True)
class ExercisePage:
    book_key: str
    unit_number: int
    unit_title: str
    page: int
    section: str
    category: str
    text: str
    needs_visual: bool


BOOK1_UNITS = (
    Unit(
        1,
        "Conjuntos numéricos",
        8,
        33,
        26,
        (
            "Números naturales",
            "Números enteros",
            "Números racionales",
            "Números irracionales",
            "Números reales",
            "Orden en el conjunto de números reales",
        ),
    ),
    Unit(
        2,
        "Expresiones algebraicas",
        34,
        51,
        46,
        (
            "Lenguaje algebraico",
            "Términos algebraicos",
            "Monomios",
            "Características de un monomio",
            "Polinomios",
            "Características de un polinomio",
            "Valor numérico de un polinomio",
        ),
    ),
    Unit(
        3,
        "Operaciones entre polinomios",
        52,
        79,
        74,
        (
            "Adición y sustracción de polinomios",
            "Multiplicación de polinomios",
            "División de polinomios",
            "División sintética",
            "Teorema del residuo",
            "Operaciones combinadas entre polinomios",
        ),
    ),
    Unit(
        4,
        "Productos notables y cocientes notables",
        80,
        105,
        100,
        (
            "Productos notables",
            "Cuadrado de un binomio",
            "Producto de la suma por la diferencia",
            "Cubo de un binomio",
            "Triángulo de Pascal",
            "Cocientes notables",
        ),
    ),
    Unit(
        5,
        "Factorización",
        106,
        143,
        138,
        (
            "Noción de factorización",
            "Factor común",
            "Factor común por agrupación",
            "Factorización de binomios",
            "Factorización de trinomios",
            "Factorización de un cubo perfecto",
            "Factorización completa",
            "Factorización de un polinomio con división sintética",
        ),
    ),
    Unit(
        6,
        "Fracciones algebraicas",
        144,
        181,
        176,
        (
            "Máximo común divisor",
            "Mínimo común múltiplo",
            "Expresiones algebraicas racionales",
            "Simplificación de fracciones algebraicas",
            "Adición y sustracción",
            "Multiplicación de fracciones algebraicas",
            "División de fracciones algebraicas",
            "Operaciones combinadas",
            "Fracciones complejas",
        ),
    ),
    Unit(
        7,
        "Ecuaciones e inecuaciones",
        182,
        219,
        214,
        (
            "Ecuaciones",
            "Solución de una ecuación",
            "Ecuaciones con signos de agrupación",
            "Ecuaciones con coeficientes literales",
            "Desigualdades",
            "Inecuaciones",
            "Solución de problemas con inecuaciones",
        ),
    ),
    Unit(
        8,
        "Función lineal",
        220,
        253,
        248,
        (
            "Función",
            "Función lineal",
            "Función afín",
            "Pendiente de una recta",
            "Ecuación de la recta",
            "Rectas paralelas",
            "Rectas perpendiculares",
            "Sistemas de ecuaciones lineales",
        ),
    ),
    Unit(
        9,
        "Geometría",
        254,
        291,
        284,
        (
            "Ángulos",
            "Triángulos",
            "Métodos de demostración",
            "Congruencia",
            "Líneas notables",
            "Longitud y área",
            "Unidades de longitud",
            "Unidades de área",
        ),
    ),
    Unit(
        10,
        "Estadística y probabilidad",
        292,
        336,
        326,
        (
            "Estadística",
            "Variables cuantitativas",
            "Medidas de posición",
            "Medidas de variabilidad",
            "Probabilidad",
            "Propiedades de la probabilidad",
        ),
    ),
)


BOOK2_UNITS = (
    Unit(1, "Conjuntos numéricos", 8, 27, 24, BOOK1_UNITS[0].topics),
    Unit(2, "Expresiones algebraicas", 28, 43, 40, BOOK1_UNITS[1].topics),
    Unit(3, "Operaciones entre expresiones algebraicas", 44, 69, 66, BOOK1_UNITS[2].topics),
    Unit(4, "Productos y cocientes notables", 70, 97, 90, BOOK1_UNITS[3].topics),
    Unit(5, "Factorización", 98, 133, 130, BOOK1_UNITS[4].topics),
    Unit(6, "Fracciones algebraicas", 134, 169, 166, BOOK1_UNITS[5].topics),
    Unit(7, "Ecuaciones e inecuaciones", 170, 205, 202, BOOK1_UNITS[6].topics),
    Unit(8, "Función lineal", 206, 237, 234, BOOK1_UNITS[7].topics),
    Unit(9, "Geometría", 238, 273, 270, BOOK1_UNITS[8].topics),
    Unit(10, "Estadística y probabilidad", 274, 304, 298, BOOK1_UNITS[9].topics),
)


VISUAL_PATTERN = re.compile(
    r"\b(?:figura|tabla|gráfic\w*|recta numérica|diagrama|plano|mapa|laberinto|cuadro|"
    r"triángulo|cuadrado|rectángulo|circunferencia|polígono|cuerpo|sólido|imagen|"
    r"dibuja|representa|construye|observa|completa la tabla|une los puntos)\b",
    re.IGNORECASE,
)

BOOK2_EXERCISE_PATTERN = re.compile(
    r"Actividades|TALLER\s+\d+|PREP[ÁA]RATE|"
    r"Soluciona?\s+(?:p|r)?oblemas|Ejercito:|Razona:|Modela:|"
    r"Recupera\s+(?:la\s+)?informaci|Recu.{0,8}informaci|"
    r"Reflexiona\s+(?:y\s+)?valora|Plantea\s+(?:y\s+)?actúa",
    re.IGNORECASE,
)


def parse_ocr(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    pages = re.split(r"^===== .*? =====\s*$", raw, flags=re.MULTILINE)[1:]
    return [clean_ocr_whitespace(page) for page in pages]


def clean_ocr_whitespace(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def unit_for_page(units: tuple[Unit, ...], page: int) -> Unit:
    for unit in units:
        if unit.start <= page <= unit.end:
            return unit
    raise ValueError(f"Page {page} is outside the configured unit ranges")


def is_summary_page(text: str) -> bool:
    return bool(re.search(r"EN\s+S[ÍI]NTESIS", text, re.IGNORECASE))


def choose_book1_pages(pages: list[str], units: tuple[Unit, ...]) -> set[int]:
    selected: set[int] = set()
    for unit in units:
        for page in range(unit.start, unit.end + 1):
            text = pages[page - 1]
            if re.search(r"Afianzo\s+COMPETENCIAS|Lo\s*que\s+sabes", text, re.IGNORECASE):
                selected.add(page)
        if unit.review_start is not None:
            selected.update(range(unit.review_start, unit.end + 1))
    selected.difference_update({334, 335, 336})
    return selected


def choose_book2_pages(pages: list[str], units: tuple[Unit, ...]) -> set[int]:
    selected: set[int] = set()
    for unit in units:
        for page in range(unit.start, unit.end + 1):
            if BOOK2_EXERCISE_PATTERN.search(pages[page - 1]):
                selected.add(page)
        if unit.review_start is not None:
            for page in range(unit.review_start, unit.end + 1):
                if not is_summary_page(pages[page - 1]):
                    selected.add(page)
            if unit.review_start + 1 <= unit.end:
                selected.add(unit.review_start + 1)
    selected.difference_update({302, 303, 304})
    return selected


def clip_exercise_text(text: str, style: str, is_closing: bool) -> str:
    if is_closing:
        return text

    patterns = (
        (r"Afianzo\s+COMPETENCIAS", "Afianzo competencias"),
        (r"Lo\s*que\s+sabes", "Lo que sabes"),
        (r"PREP[ÁA]RATE\s+PARA", "Prepárate para"),
        (r"Actividades", "Actividades"),
    )
    for pattern, label in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{label}. {text[match.end():].strip()}"

    if style == "book2":
        starts = [
            re.search(pattern, text, re.IGNORECASE)
            for pattern in (
                r"Soluciona?\s+(?:p|r)?oblemas",
                r"Ejercito:",
                r"Razona:",
                r"Modela:",
            )
        ]
        starts = [match for match in starts if match is not None]
        if starts:
            first = min(starts, key=lambda item: item.start())
            return text[first.start() :]

    return text


def infer_topic(unit: Unit, pages: list[str], page: int) -> str:
    window_start = max(unit.start, page - 2)
    best: tuple[int, str] | None = None
    for source_page in range(window_start, page + 1):
        source = pages[source_page - 1]
        for topic in unit.topics:
            for match in re.finditer(re.escape(topic), source, re.IGNORECASE):
                score = source_page * 100_000 + match.start()
                if best is None or score > best[0]:
                    best = (score, topic)
    return best[1] if best is not None else unit.title


def categorize(text: str, unit: Unit, page: int, style: str) -> str:
    if re.search(r"PROBLEMAS\s+PARA\s+REPASAR", text, re.IGNORECASE):
        return "Problemas para repasar"
    if re.search(r"TALLER\s+\d+", text, re.IGNORECASE):
        return f"Taller {unit.number}"
    if re.search(r"Y\s+esto\s+que\s+aprend", text, re.IGNORECASE):
        return "Aplicación: ¿para qué me sirve?"
    if re.search(r"Trabaja\s+con|LABORATORIO|MATEMÁTICAS\s*\+\s*TECNOLOGÍA", text, re.IGNORECASE):
        return "Actividad con tecnología"
    if re.search(r"PREP[ÁA]RATE", text, re.IGNORECASE):
        return "Prepárate para analizar"
    if re.search(r"Lo\s*que\s+sabes", text, re.IGNORECASE):
        return "Diagnóstico: lo que sabes"
    if unit.review_start is not None and page >= unit.review_start:
        if style == "book1" and not re.search(
            r"Y\s+esto|Trabaja\s+con|PROBLEMAS\s+PARA\s+REPASAR", text, re.IGNORECASE
        ):
            return "Ejercicios para repasar"
        if style == "book2" and not re.search(
            r"Y\s+esto|MATEMÁTICAS\s*\+\s*TECNOLOGÍA|LABORATORIO", text, re.IGNORECASE
        ):
            return f"Taller {unit.number} - continuación"
    if re.search(r"Afianzo\s+COMPETENCIAS", text, re.IGNORECASE):
        return "Afianzo competencias"
    return "Actividades"


def build_records(book: Book, pages: list[str]) -> list[ExercisePage]:
    if book.style == "book1":
        selected = choose_book1_pages(pages, book.units)
    else:
        selected = choose_book2_pages(pages, book.units)

    records: list[ExercisePage] = []
    for page in sorted(selected):
        unit = unit_for_page(book.units, page)
        original = pages[page - 1]
        is_closing = unit.review_start is not None and page >= unit.review_start
        category = categorize(original, unit, page, book.style)
        section = infer_topic(unit, pages, page)
        clipped = clip_exercise_text(original, book.style, is_closing)
        records.append(
            ExercisePage(
                book_key=book.key,
                unit_number=unit.number,
                unit_title=unit.title,
                page=page,
                section=section,
                category=category,
                text=clipped,
                needs_visual=bool(VISUAL_PATTERN.search(clipped)),
            )
        )
    return records


def normalize_ocr_text(text: str) -> str:
    replacements = {
        "EI ": "El ",
        " EI ": " El ",
        "IOS ": "los ",
        " IOS ": " los ",
        "nÚmerOS": "números",
        "nÚmeroS": "números",
        "nÚmero": "número",
        "tiÚmero": "número",
        " tiÚmet•OS": " números",
        "Soluciona roblemas": "Soluciona problemas",
        "Soluciono roblemas": "Soluciono problemas",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("—", "-").replace("–", "-").replace("‑", "-")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def latex_escape(text: str) -> str:
    placeholders = {
        "≤": "@@LE@@",
        "≥": "@@GE@@",
        "≠": "@@NE@@",
        "∈": "@@IN@@",
        "∉": "@@NOTIN@@",
        "⊂": "@@SUBSET@@",
        "∪": "@@UNION@@",
        "∩": "@@INTER@@",
        "×": "@@TIMES@@",
        "÷": "@@DIV@@",
        "√": "@@SQRT@@",
        "π": "@@PI@@",
        "∞": "@@INF@@",
        "•": "@@BULLET@@",
    }
    for symbol, token in placeholders.items():
        text = text.replace(symbol, token)

    escaped: list[str] = []
    latex_chars = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "<": r"\ensuremath{<}",
        ">": r"\ensuremath{>}",
        "|": r"\textbar{}",
        '"': r"\textquotedbl{}",
    }
    for char in text:
        escaped.append(latex_chars.get(char, char))
    result = "".join(escaped)

    latex_symbols = {
        "@@LE@@": r"\ensuremath{\leq}",
        "@@GE@@": r"\ensuremath{\geq}",
        "@@NE@@": r"\ensuremath{\neq}",
        "@@IN@@": r"\ensuremath{\in}",
        "@@NOTIN@@": r"\ensuremath{\notin}",
        "@@SUBSET@@": r"\ensuremath{\subset}",
        "@@UNION@@": r"\ensuremath{\cup}",
        "@@INTER@@": r"\ensuremath{\cap}",
        "@@TIMES@@": r"\ensuremath{\times}",
        "@@DIV@@": r"\ensuremath{\div}",
        "@@SQRT@@": r"\ensuremath{\sqrt{\phantom{x}}}",
        "@@PI@@": r"\ensuremath{\pi}",
        "@@INF@@": r"\ensuremath{\infty}",
        "@@BULLET@@": r"\textbullet{}",
    }
    for token, replacement in latex_symbols.items():
        result = result.replace(token, replacement)
    return result


def format_exercise_text(text: str) -> str:
    normalized = normalize_ocr_text(text)
    escaped = latex_escape(normalized)
    escaped = re.sub(
        r"(?<![\d,])\b(\d{1,3})\.(?!\d)",
        lambda match: rf"\par\medskip\noindent\textbf{{{match.group(1)}.}}",
        escaped,
    )
    instruction_words = (
        "Responde",
        "Resuelve",
        "Determina",
        "Escribe",
        "Completa",
        "Representa",
        "Observa",
        "Relaciona",
        "Calcula",
        "Halla",
        "Justifica",
        "Explica",
    )
    for word in instruction_words:
        escaped = re.sub(
            rf"(?<![A-Za-zÁÉÍÓÚÑáéíóúñ]){word}\b",
            lambda _match, label=word: rf"\par\medskip\noindent\textbf{{{label}}}",
            escaped,
        )
    escaped = re.sub(r"\s+", " ", escaped).strip()
    return "\n".join(textwrap.wrap(escaped, width=105, break_long_words=False))


def latex_document_header(book_titles: list[str]) -> str:
    sources = " y ".join(book_titles)
    return rf"""\documentclass[11pt,openany]{{book}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[spanish,es-nodecimaldot,es-noquoting]{{babel}}
\usepackage[a4paper,margin=2.2cm]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}

\definecolor{{Ink}}{{HTML}}{{172033}}
\definecolor{{Accent}}{{HTML}}{{315E8A}}
\definecolor{{Soft}}{{HTML}}{{EEF3F8}}
\pagestyle{{headings}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.55em}}

\newenvironment{{exerciseblock}}
  {{\begin{{sloppypar}}\small\color{{Ink}}}}
  {{\end{{sloppypar}}}}

\newcommand{{\sourcepage}}[2]{{%
  \par\medskip
  \begin{{center}}
    \centering
    \fcolorbox{{Accent}}{{white}}{{\includegraphics[width=0.92\textwidth]{{#1}}}}
    \\[0.4em]{{\small\itshape Referencia visual del enunciado - página PDF #2.}}
  \end{{center}}
  \clearpage%
}}

\title{{\Huge\bfseries Listas de ejercicios\\[0.35em]\Large Matemáticas 8}}
\author{{\parbox{{0.82\textwidth}}{{\centering Compilación ordenada a partir de\\{latex_escape(sources)}}}}}
\date{{}}

\begin{{document}}
\frontmatter
\maketitle

\chapter*{{Criterio de edición}}
Esta compilación reúne, en orden de aparición, los diagnósticos, actividades de sección,
repasos, problemas, talleres y aplicaciones de los dos libros fuente. Cada bloque indica la
página física del PDF para que la transcripción sea auditable.

Los documentos fuente son escaneos sin capa de texto utilizable. El texto fue recuperado por
OCR local en español y convertido a una fuente \LaTeX{{}} editable. Las expresiones apiladas,
fracciones, tablas y diagramas pueden perder relaciones espaciales durante el OCR; por eso los
bloques que dependen de una figura o de la disposición gráfica incluyen una captura de la
página fuente inmediatamente después de la transcripción.

\tableofcontents
\mainmatter
"""


def write_book_tex(
    book: Book,
    records: list[ExercisePage],
    pages: list[str],
    output_dir: Path,
    assets_dir: Path,
) -> Path:
    del pages
    output_path = output_dir / f"{book.key}.tex"
    lines = [
        rf"\part{{{latex_escape(book.title)}}}",
        r"\setcounter{chapter}{0}",
        "",
    ]
    current_unit: int | None = None
    current_section: str | None = None

    for record in records:
        if record.unit_number != current_unit:
            current_unit = record.unit_number
            current_section = None
            lines.extend(
                [
                    rf"\chapter{{Unidad {record.unit_number}. {latex_escape(record.unit_title)}}}",
                    "",
                ]
            )
        if record.section != current_section:
            current_section = record.section
            lines.extend([rf"\section{{{latex_escape(record.section)}}}", ""])

        lines.extend(
            [
                rf"\subsection{{{latex_escape(record.category)} - página PDF {record.page}}}",
                r"\begin{exerciseblock}",
                format_exercise_text(record.text),
                r"\end{exerciseblock}",
                "",
            ]
        )

        if record.needs_visual:
            source_image = book.image_dir / f"page-{record.page:03d}.jpg"
            asset_name = f"{book.key}_page_{record.page:03d}.jpg"
            target_image = assets_dir / asset_name
            if not source_image.exists():
                raise FileNotFoundError(f"Missing rendered source page: {source_image}")
            shutil.copy2(source_image, target_image)
            lines.extend(
                [
                    rf"\sourcepage{{assets/{asset_name}}}{{{record.page}}}",
                    "",
                ]
            )

    output_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return output_path


def write_manifest(records: list[ExercisePage], output_dir: Path) -> None:
    with (output_dir / "manifest.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "libro",
                "unidad",
                "titulo_unidad",
                "pagina_pdf",
                "seccion_inferida",
                "categoria",
                "referencia_visual",
                "caracteres_ocr",
            ]
        )
        for record in records:
            writer.writerow(
                [
                    record.book_key,
                    record.unit_number,
                    record.unit_title,
                    record.page,
                    record.section,
                    record.category,
                    "si" if record.needs_visual else "no",
                    len(record.text),
                ]
            )


def write_readme(books: list[Book], records: list[ExercisePage], output_dir: Path) -> None:
    counts = {book.key: sum(item.book_key == book.key for item in records) for book in books}
    visuals = {
        book.key: sum(item.book_key == book.key and item.needs_visual for item in records)
        for book in books
    }
    content = f"""# Listas de ejercicios - Matemáticas 8

La carpeta contiene una compilación LaTeX editable y organizada por libro, unidad, sección y
página fuente.

- `{books[0].key}.tex`: {counts[books[0].key]} bloques; {visuals[books[0].key]} referencias visuales.
- `{books[1].key}.tex`: {counts[books[1].key]} bloques; {visuals[books[1].key]} referencias visuales.
- `manifest.csv`: inventario auditable de los bloques extraídos.
- `assets/`: capturas de las páginas que contienen figuras, tablas, gráficas o disposición espacial.

Compilación desde esta carpeta:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Nota de fidelidad

Los PDF fuente son escaneos. La transcripción textual se obtuvo mediante OCR local y se dejó
editable en LaTeX. Cuando la lectura depende de una fracción apilada, una tabla, un gráfico o una
figura, la captura incluida es la fuente de verdad visual. `manifest.csv` conserva la página PDF
exacta para revisión o corrección posterior.
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--book1-ocr", type=Path, default=ROOT / "tmp/pdfs/book1_ocr.txt")
    parser.add_argument("--book2-ocr", type=Path, default=ROOT / "tmp/pdfs/book2_ocr.txt")
    parser.add_argument("--book1-images", type=Path, default=ROOT / "tmp/pdfs/book1_low")
    parser.add_argument("--book2-images", type=Path, default=ROOT / "tmp/pdfs/book2_low")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output.resolve()
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for stale_asset in assets_dir.glob("*.jpg"):
        if stale_asset.name.startswith(("los_caminos_del_saber_", "hipertexto_matematicas_8_")):
            stale_asset.unlink()

    books = [
        Book(
            "los_caminos_del_saber",
            "Los Caminos del Saber - Matemáticas 8",
            args.book1_ocr.resolve(),
            args.book1_images.resolve(),
            BOOK1_UNITS,
            "book1",
        ),
        Book(
            "hipertexto_matematicas_8",
            "Hipertexto Matemáticas 8",
            args.book2_ocr.resolve(),
            args.book2_images.resolve(),
            BOOK2_UNITS,
            "book2",
        ),
    ]

    all_records: list[ExercisePage] = []
    book_tex_paths: list[Path] = []
    for book in books:
        pages = parse_ocr(book.ocr_path)
        expected_pages = book.units[-1].end
        if len(pages) < expected_pages:
            raise ValueError(
                f"{book.title}: expected at least {expected_pages} OCR pages, found {len(pages)}"
            )
        records = build_records(book, pages)
        all_records.extend(records)
        book_tex_paths.append(write_book_tex(book, records, pages, output_dir, assets_dir))

    main_tex = latex_document_header([book.title for book in books])
    for path in book_tex_paths:
        main_tex += rf"\input{{{path.stem}.tex}}" + "\n"
    main_tex += "\\backmatter\n\\end{document}\n"
    (output_dir / "main.tex").write_text(main_tex, encoding="utf-8", newline="\n")
    write_manifest(all_records, output_dir)
    write_readme(books, all_records, output_dir)

    print(f"Output: {output_dir}")
    print(f"Exercise blocks: {len(all_records)}")
    print(f"Visual references: {sum(record.needs_visual for record in all_records)}")


if __name__ == "__main__":
    main()
