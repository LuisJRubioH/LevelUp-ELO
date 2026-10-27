"""Spec 008 delivery C: the course catalogue — block and name of every course, in one place
(FR-020, FR-021; D5; plan-c.md O-C1 … O-C9).

Read by both repositories (the bank sync and its fingerprint), by `scripts/validate_bank.py` and by
`src.domain.entities.in_catalogue`. Pure data and functions over a course id and a path relative
to `items/bank/`; standard library only (the CI job that runs the validator installs nothing).

- A top-level bank file `items/bank/<course>.json` is a course with an explicit entry in `COURSES`
  (block, name). Its name is never its first item's topic (survey B14).
- A file `items/bank/semillero/<subject>_semillero_<g>.json` needs no entry: block «Semillero»,
  grade g (6–11), name «<label> Semillero <g>°» from `SEMILLERO_SUBJECTS` (O-C3, O-C4).
- A course the catalogue does not know is not synced (O-C5) and fails validation; so does an entry
  with no bank file (O-C6).

New course: add its entry to `COURSES` (a semillero file of a known subject needs none), then run
`python scripts/validate_bank.py`.
"""

from __future__ import annotations

import re
from typing import Iterable, NamedTuple

from src.domain.entities import COURSE_BLOCKS, SEMILLERO_GRADES

CATALOGUE_PATH = "src/domain/bank/catalogue.py"
SEMILLERO_DIR = "semillero"
SEMILLERO_BLOCK = "Semillero"

# course id (bank file name without extension) → (block, name). One entry per course outside
# `semillero/`. The ten courses once named by their first item's topic keep that name (O-C2).
COURSES: dict[str, tuple[str, str]] = {
    # ── Universidad ───────────────────────────────────────────────────────────
    "algebra_lineal": ("Universidad", "Álgebra Lineal"),
    "calculo_diferencial": ("Universidad", "Cálculo Diferencial"),
    "calculo_integral": ("Universidad", "Cálculo Integral"),
    "calculo_varias_variables": ("Universidad", "Cálculo de Varias Variables"),
    "ecuaciones_diferenciales": ("Universidad", "Ecuaciones Diferenciales Ordinarias"),
    "probabilidad": ("Universidad", "Probabilidad"),
    # ── Colegio ───────────────────────────────────────────────────────────────
    "algebra_basica": ("Colegio", "Álgebra Básica"),
    "aritmetica_basica": ("Colegio", "Aritmética Básica"),
    "geometria": ("Colegio", "Geometría"),
    "trigonometria": ("Colegio", "Trigonometría"),
    "evaluar_para_avanzar_8": ("Colegio", "Evaluar para Avanzar — Matemáticas 8.°"),
    # ── Concursos (preparación para concursos públicos) ───────────────────────
    "DIAN": ("Concursos", "Concurso DIAN — Gestor I"),
    "SENA": ("Concursos", "Concurso SENA — Profesional 10"),
}

# Semillero (Olimpiadas Matemáticas UdeA, grades 6–11): subject → the label its courses carry.
SEMILLERO_SUBJECTS: dict[str, str] = {
    "algebra": "Álgebra",
    "aritmetica": "Aritmética",
    "conteo_combinatoria": "Conteo y Combinatoria",
    "geometria": "Geometría",
    "logica": "Lógica",
    "probabilidad": "Probabilidad",
}

_SEMILLERO_ID = re.compile(r"^(?P<subject>.+)_semillero_(?P<grade>\d+)$")


class CourseEntry(NamedTuple):
    block: str
    name: str
    grade: str | None  # a semillero course's grade; None elsewhere


def semillero_grade(course_id: str) -> str | None:
    """The grade ('6' … '11') a semillero course id ends with (`<…>_semillero_<g>`), else None.
    The one owner of the rule (O-C8): `in_catalogue` asks it. Whether the subject is known is the
    bank file's rule (`course_entry`), not the grade's."""
    match = _SEMILLERO_ID.match(course_id)
    if match and match["grade"] in SEMILLERO_GRADES:
        return match["grade"]
    return None


def _folder(relative_path: str) -> str:
    parts = relative_path.replace("\\", "/").split("/")
    return "/".join(parts[:-1])


def _semillero_entry(course_id: str) -> CourseEntry | None:
    match = _SEMILLERO_ID.match(course_id)
    grade = semillero_grade(course_id)
    if not match or grade is None or match["subject"] not in SEMILLERO_SUBJECTS:
        return None
    label = SEMILLERO_SUBJECTS[match["subject"]]
    return CourseEntry(SEMILLERO_BLOCK, f"{label} Semillero {grade}°", grade)


def _named(entry) -> bool:
    return (
        isinstance(entry, tuple)
        and len(entry) == 2
        and isinstance(entry[1], str)
        and bool(entry[1].strip())
    )


def course_entry(course_id: str, relative_path: str) -> CourseEntry | None:
    """Block, name and grade of the course of a bank file (`relative_path` under `items/bank/`);
    None when the catalogue does not know it or its entry has no name. A block outside
    `COURSE_BLOCKS` is the validator's error and the `courses` CHECK's refusal, not filtered
    here."""
    folder = _folder(relative_path)
    if folder == SEMILLERO_DIR:
        return _semillero_entry(course_id)
    if folder or _SEMILLERO_ID.match(course_id):
        return None  # outside the folders the sync reads, or a semillero name at the top (O-C4)
    entry = COURSES.get(course_id)
    if not _named(entry):
        return None
    return CourseEntry(entry[0], entry[1], None)


def catalogue_problems(bank_paths: Iterable[str]) -> list[str]:
    """What the validator reports against the catalogue, for every bank file (paths relative to
    `items/bank/`): a course with no entry or no explicit name, a semillero file whose name gives
    no known subject or grade, a top-level file named like a semillero course, a file outside the
    folders the sync reads, and an entry with no bank file (O-C6)."""
    problems = []
    top_level = set()
    subjects = ", ".join(sorted(SEMILLERO_SUBJECTS))
    for path in bank_paths:
        path = path.replace("\\", "/")
        course_id = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        folder = _folder(path)
        if folder == SEMILLERO_DIR:
            if _semillero_entry(course_id) is None:
                problems.append(
                    f"[{path}]: un archivo de semillero se llama <materia>_semillero_<g>, con "
                    f"materia en {{{subjects}}} y g de 6 a 11 ({CATALOGUE_PATH})"
                )
        elif folder:
            problems.append(
                f"[{path}]: la sincronización lee solo items/bank/*.json e "
                f"items/bank/{SEMILLERO_DIR}/*.json; este archivo no sería un curso"
            )
        elif _SEMILLERO_ID.match(course_id):
            problems.append(
                f"[{path}]: un curso de semillero va en items/bank/{SEMILLERO_DIR}/, no en la "
                f"raíz del banco ({CATALOGUE_PATH})"
            )
        else:
            top_level.add(course_id)
            entry = COURSES.get(course_id)
            if entry is None:
                problems.append(
                    f"[{path}]: el curso '{course_id}' no está en el catálogo de cursos "
                    f"({CATALOGUE_PATH}); sin entrada no se sincroniza"
                )
            elif not (isinstance(entry, tuple) and len(entry) == 2):
                problems.append(
                    f"[{path}]: la entrada del curso '{course_id}' en {CATALOGUE_PATH} debe ser "
                    "(bloque, nombre)"
                )
            elif entry[0] not in COURSE_BLOCKS:
                problems.append(
                    f"[{path}]: el curso '{course_id}' tiene el bloque {entry[0]!r} en "
                    f"{CATALOGUE_PATH}; los bloques son {', '.join(COURSE_BLOCKS)}"
                )
            elif not (isinstance(entry[1], str) and entry[1].strip()):
                problems.append(
                    f"[{path}]: el curso '{course_id}' no tiene un nombre explícito en "
                    f"{CATALOGUE_PATH} (spec 008 FR-021)"
                )
    for course_id in sorted(set(COURSES) - top_level):
        problems.append(
            f"el curso '{course_id}' está en {CATALOGUE_PATH} y no tiene archivo en items/bank/ "
            "(spec 008 O-C6): quita la entrada o añade el archivo"
        )
    return problems


def fingerprint_view(bank_paths: Iterable[str]) -> dict:
    """`{course_id: [block, name]}` of the bank's courses (paths relative to `items/bank/`), what
    the bank fingerprint hashes with the files (O-C7): a change to a bank course's block or name
    resyncs the bank; a catalogue edit that changes none does not. An unknown course is `None`."""
    view = {}
    for path in bank_paths:
        course_id = path.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
        entry = course_entry(course_id, path)
        view[course_id] = [entry.block, entry.name] if entry else None
    return view
