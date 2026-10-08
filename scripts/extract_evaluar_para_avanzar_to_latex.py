"""Extract five Evaluar para Avanzar grade-8 math booklets to LaTeX.

The source PDFs contain usable text, but their tables, diagrams, and multi-column
answer choices still require visual references.  Each numbered question is
detected from its positioned PDF text, transcribed to editable LaTeX, and paired
with an exact crop of the source page.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import textwrap
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path(r"C:\Users\orian\OneDrive\Documentos\IE Los Andes\Libros\Evaluar para avanzar 8")
DEFAULT_OUTPUT = ROOT / "output" / "latex" / "evaluar_para_avanzar_matematicas_8"
DEFAULT_TEMP = ROOT / "tmp" / "pdfs" / "cuadernillos"
DEFAULT_PDFTOPPM = Path(
    r"C:\Users\orian\.cache\codex-runtimes\codex-primary-runtime\dependencies\native"
    r"\poppler\Library\bin\pdftoppm.exe"
)


@dataclass(frozen=True)
class Booklet:
    key: str
    title: str
    year: int
    number: int
    code: str
    source_path: Path


@dataclass
class Question:
    booklet: Booklet
    number: int
    pdf_page: int
    text: str
    bbox: tuple[float, float, float, float]
    fingerprint: str
    asset_name: str = ""
    duplicate_of: str = ""

    @property
    def identifier(self) -> str:
        return f"{self.booklet.key}-p{self.number:02d}"


BOOKLETS = (
    Booklet(
        "cuadernillo_1_2023",
        "Cuadernillo 1 - 2023",
        2023,
        1,
        "M081",
        SOURCE_ROOT / "Cuadernillo-Matematicas-8-1.pdf",
    ),
    Booklet(
        "cuadernillo_1_2022",
        "Cuadernillo 1 - 2022",
        2022,
        1,
        "M081",
        SOURCE_ROOT / "Cuadernillo-Matematicas-8-1-1.pdf",
    ),
    Booklet(
        "cuadernillo_1_2021",
        "Cuadernillo 1 - 2021",
        2021,
        1,
        "M081",
        SOURCE_ROOT / "Cuadernillo-Matematicas-8-1-2.pdf",
    ),
    Booklet(
        "cuadernillo_1_2020",
        "Cuadernillo 1 - 2020",
        2020,
        1,
        "M081",
        SOURCE_ROOT / "Cuadernillo-Matematicas-8-1-3.pdf",
    ),
    Booklet(
        "cuadernillo_2_2021",
        "Cuadernillo 2 - 2021",
        2021,
        2,
        "M082",
        SOURCE_ROOT / "Cuadernillo-Matematicas-8-2.pdf",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--temp", type=Path, default=DEFAULT_TEMP)
    parser.add_argument("--pdftoppm", type=Path, default=DEFAULT_PDFTOPPM)
    parser.add_argument("--dpi", type=int, default=170)
    return parser.parse_args()


def render_booklet(booklet: Booklet, render_dir: Path, pdftoppm: Path, dpi: int) -> None:
    render_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(render_dir.glob("page-*.jpg"))
    with pdfplumber.open(booklet.source_path) as pdf:
        expected = len(pdf.pages)
    if len(existing) == expected:
        return

    for stale in existing:
        stale.unlink()
    subprocess.run(
        [
            str(pdftoppm),
            "-jpeg",
            "-r",
            str(dpi),
            "-jpegopt",
            "quality=90",
            str(booklet.source_path),
            str(render_dir / "page"),
        ],
        check=True,
    )


def question_markers(page: pdfplumber.page.Page) -> list[dict[str, object]]:
    markers = []
    for word in page.extract_words(x_tolerance=2, y_tolerance=2):
        if word["x0"] >= 100:
            continue
        if re.fullmatch(r"(?:[1-9]|1\d|20)\.", str(word["text"])):
            markers.append(word)
    return sorted(markers, key=lambda item: float(item["top"]))


def clean_question_text(text: str, number: int) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\s*\n\s*(?=[a-záéíóúñ])", "", text)
    text = re.sub(r"^\s*" + str(number) + r"\.\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    return text


def question_fingerprint(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).casefold()
    normalized = "".join(char for char in normalized if char.isalnum())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_questions(booklet: Booklet) -> list[Question]:
    questions: list[Question] = []
    with pdfplumber.open(booklet.source_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            markers = question_markers(page)
            for marker_index, marker in enumerate(markers):
                number = int(str(marker["text"])[:-1])
                top = max(44.0, float(marker["top"]) - 6.0)
                if marker_index + 1 < len(markers):
                    bottom = float(markers[marker_index + 1]["top"]) - 7.0
                else:
                    bottom = page.height - 34.0
                bbox = (40.0, top, page.width - 28.0, bottom)
                crop = page.crop(bbox)
                raw_text = crop.extract_text(x_tolerance=2, y_tolerance=3) or ""
                cleaned = clean_question_text(raw_text, number)
                questions.append(
                    Question(
                        booklet=booklet,
                        number=number,
                        pdf_page=page_index,
                        text=cleaned,
                        bbox=bbox,
                        fingerprint=question_fingerprint(cleaned),
                    )
                )

    questions.sort(key=lambda question: question.number)
    actual_numbers = [question.number for question in questions]
    expected_numbers = list(range(1, 21))
    if actual_numbers != expected_numbers:
        raise ValueError(f"{booklet.title}: expected questions 1-20, found {actual_numbers}")
    return questions


def mark_duplicates(questions: list[Question]) -> None:
    first_seen: dict[str, str] = {}
    for question in questions:
        previous = first_seen.get(question.fingerprint)
        if previous is None:
            first_seen[question.fingerprint] = question.identifier
        else:
            question.duplicate_of = previous


def rendered_page_path(render_dir: Path, pdf_page: int) -> Path:
    candidates = sorted(render_dir.glob(f"page-*{pdf_page:02d}.jpg"))
    exact = [
        candidate for candidate in candidates if int(candidate.stem.rsplit("-", 1)[-1]) == pdf_page
    ]
    if len(exact) != 1:
        raise FileNotFoundError(
            f"Expected one rendered image for PDF page {pdf_page} in {render_dir}, found {exact}"
        )
    return exact[0]


def crop_question_asset(
    question: Question,
    render_dir: Path,
    assets_dir: Path,
    pdf_width: float = 612.0,
    pdf_height: float = 792.0,
) -> None:
    source_image = rendered_page_path(render_dir, question.pdf_page)
    with Image.open(source_image) as image:
        x_scale = image.width / pdf_width
        y_scale = image.height / pdf_height
        x0, top, x1, bottom = question.bbox
        padding = 8
        pixel_box = (
            max(0, round(x0 * x_scale) - padding),
            max(0, round(top * y_scale) - padding),
            min(image.width, round(x1 * x_scale) + padding),
            min(image.height, round(bottom * y_scale) + padding),
        )
        cropped = image.crop(pixel_box)
        question.asset_name = f"{question.booklet.key}_pregunta_{question.number:02d}.jpg"
        cropped.save(assets_dir / question.asset_name, quality=92, optimize=True)


def latex_escape(text: str) -> str:
    placeholders = {
        "π": "@@PI@@",
        "≤": "@@LE@@",
        "≥": "@@GE@@",
        "≠": "@@NE@@",
        "≈": "@@APPROX@@",
        "×": "@@TIMES@@",
        "÷": "@@DIV@@",
        "²": "@@SUP2@@",
        "³": "@@SUP3@@",
        "•": "@@BULLET@@",
    }
    for symbol, token in placeholders.items():
        text = text.replace(symbol, token)

    special = {
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
    escaped = "".join(special.get(char, char) for char in text)
    latex_symbols = {
        "@@PI@@": r"\ensuremath{\pi}",
        "@@LE@@": r"\ensuremath{\leq}",
        "@@GE@@": r"\ensuremath{\geq}",
        "@@NE@@": r"\ensuremath{\neq}",
        "@@APPROX@@": r"\ensuremath{\approx}",
        "@@TIMES@@": r"\ensuremath{\times}",
        "@@DIV@@": r"\ensuremath{\div}",
        "@@SUP2@@": r"\textsuperscript{2}",
        "@@SUP3@@": r"\textsuperscript{3}",
        "@@BULLET@@": r"\textbullet{}",
    }
    for token, replacement in latex_symbols.items():
        escaped = escaped.replace(token, replacement)
    return escaped


def format_question_text(text: str) -> str:
    escaped = latex_escape(text)
    escaped = re.sub(
        r"(?<![A-Za-z])([ABCD])\.\s+",
        lambda match: rf"\par\medskip\noindent\textbf{{{match.group(1)}.}} ",
        escaped,
    )
    escaped = re.sub(
        r"\b(cm|mm|km|m)\s*([23])\b",
        lambda match: (rf"\ensuremath{{\mathrm{{{match.group(1)}}}^{{{match.group(2)}}}}}"),
        escaped,
    )
    escaped = re.sub(r"\s+", " ", escaped).strip()
    return "\n".join(textwrap.wrap(escaped, width=105, break_long_words=False))


def document_header() -> str:
    return r"""\documentclass[11pt,openany]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-nodecimaldot,es-noquoting]{babel}
\usepackage[a4paper,margin=2.2cm]{geometry}
\usepackage{graphicx}
\usepackage{xcolor}

\definecolor{Ink}{HTML}{172033}
\definecolor{Accent}{HTML}{D97706}
\pagestyle{headings}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}

\newenvironment{questiontext}
  {\begin{sloppypar}\small\color{Ink}}
  {\end{sloppypar}}

\newcommand{\questionimage}[2]{%
  \par\medskip
  \begin{center}
    \fcolorbox{Accent}{white}{%
      \includegraphics[width=0.94\textwidth,height=0.80\textheight,keepaspectratio]{#1}%
    }
    \\[0.4em]{\small\itshape Captura del enunciado original - página PDF #2.}
  \end{center}
  \clearpage%
}

\title{\Huge\bfseries Listas de ejercicios\\[0.35em]\Large Evaluar para Avanzar - Matemáticas 8}
\author{Cinco cuadernillos, ediciones 2020-2023}
\date{}

\begin{document}
\frontmatter
\maketitle

\chapter*{Criterio de edición}
Las preguntas se presentan en el orden original de cada cuadernillo. La transcripción procede de
la capa de texto de los PDF y se conserva como fuente \LaTeX{} editable. Cada pregunta incluye
además una captura exacta de su región en la página original, necesaria para preservar gráficas,
tablas, diagramas, fracciones apiladas y opciones distribuidas en columnas.

Las preguntas repetidas entre ediciones no se eliminaron: permanecen dentro del cuadernillo al que
pertenecen y se identifican mediante una nota y en el manifiesto CSV.

\tableofcontents
\mainmatter
"""


def write_booklet_tex(
    booklet: Booklet,
    questions: list[Question],
    output_dir: Path,
) -> Path:
    output_path = output_dir / f"{booklet.key}.tex"
    lines = [
        rf"\part{{{latex_escape(booklet.title)} ({booklet.code})}}",
        r"\setcounter{chapter}{0}",
        rf"\chapter{{Preguntas 1 a 20 - {latex_escape(booklet.title)}}}",
        "",
    ]
    for question in questions:
        lines.extend(
            [
                rf"\section{{Pregunta {question.number} - página PDF {question.pdf_page}}}",
            ]
        )
        if question.duplicate_of:
            lines.extend(
                [
                    rf"\textit{{Pregunta repetida; coincide con {latex_escape(question.duplicate_of)}.}}",
                    "",
                ]
            )
        lines.extend(
            [
                r"\begin{questiontext}",
                format_question_text(question.text),
                r"\end{questiontext}",
                "",
                rf"\questionimage{{assets/{question.asset_name}}}{{{question.pdf_page}}}",
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return output_path


def write_manifest(questions: list[Question], output_dir: Path) -> None:
    path = output_dir / "manifest.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "id",
                "cuadernillo",
                "anio",
                "numero_cuadernillo",
                "codigo",
                "pregunta",
                "pagina_pdf",
                "captura",
                "duplicada_de",
                "huella_sha256",
                "caracteres_texto",
            ]
        )
        for question in questions:
            writer.writerow(
                [
                    question.identifier,
                    question.booklet.title,
                    question.booklet.year,
                    question.booklet.number,
                    question.booklet.code,
                    question.number,
                    question.pdf_page,
                    question.asset_name,
                    question.duplicate_of,
                    question.fingerprint,
                    len(question.text),
                ]
            )


def write_readme(questions: list[Question], output_dir: Path) -> None:
    duplicate_count = sum(bool(question.duplicate_of) for question in questions)
    content = f"""# Evaluar para Avanzar - Matemáticas 8

Compilación LaTeX de cinco cuadernillos, organizada por edición y pregunta.

- 5 cuadernillos.
- {len(questions)} preguntas transcritas.
- {len(questions)} capturas recortadas de los enunciados originales.
- {duplicate_count} apariciones marcadas como repetidas respecto de una edición anterior.
- `manifest.csv` conserva página fuente, huella de contenido y relación de duplicados.

Compilación desde esta carpeta:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Las capturas son la fuente visual de verdad cuando una tabla, gráfica, fracción o distribución en
columnas no puede representarse de forma inequívoca mediante extracción lineal de texto.
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    args = parse_args()
    output_dir = args.output.resolve()
    assets_dir = output_dir / "assets"
    temp_dir = args.temp.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    for stale in assets_dir.glob("*.jpg"):
        if stale.name.startswith("cuadernillo_"):
            stale.unlink()

    all_questions: list[Question] = []
    questions_by_booklet: dict[str, list[Question]] = {}
    for booklet in BOOKLETS:
        if not booklet.source_path.exists():
            raise FileNotFoundError(booklet.source_path)
        render_dir = temp_dir / booklet.key
        render_booklet(booklet, render_dir, args.pdftoppm.resolve(), args.dpi)
        questions = extract_questions(booklet)
        questions_by_booklet[booklet.key] = questions
        all_questions.extend(questions)

    mark_duplicates(all_questions)

    input_files: list[Path] = []
    for booklet in BOOKLETS:
        render_dir = temp_dir / booklet.key
        questions = questions_by_booklet[booklet.key]
        for question in questions:
            crop_question_asset(question, render_dir, assets_dir)
        input_files.append(write_booklet_tex(booklet, questions, output_dir))

    main_tex = document_header()
    for input_file in input_files:
        main_tex += rf"\input{{{input_file.stem}.tex}}" + "\n"
    main_tex += "\\backmatter\n\\end{document}\n"
    (output_dir / "main.tex").write_text(main_tex, encoding="utf-8", newline="\n")
    write_manifest(all_questions, output_dir)
    write_readme(all_questions, output_dir)

    print(f"Output: {output_dir}")
    print(f"Questions: {len(all_questions)}")
    print(f"Duplicate appearances: {sum(bool(q.duplicate_of) for q in all_questions)}")
    print(f"Assets: {len(list(assets_dir.glob('*.jpg')))}")


if __name__ == "__main__":
    main()
