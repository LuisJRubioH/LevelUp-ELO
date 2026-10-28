"""
Spec 008 delivery C (FR-020, FR-021; US3-AS1, US3-AS2; plan-c.md O-C1, O-C3, O-C4): the course
catalogue module, `src/domain/bank/catalogue.py`. Block and name of every course live here, once;
a semillero course takes its block, grade and name from its file name. Runs in the «Banco de
preguntas» CI job, which installs nothing but pytest.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
BANK = ROOT / "items" / "bank"
GRADES = ["6", "7", "8", "9", "10", "11"]
# The six semillero subjects and the label each course name carries (O-C3): literal here, so the
# test does not read the table it checks.
SUBJECT_LABELS = {
    "algebra": "Álgebra",
    "aritmetica": "Aritmética",
    "conteo_combinatoria": "Conteo y Combinatoria",
    "geometria": "Geometría",
    "logica": "Lógica",
    "probabilidad": "Probabilidad",
}


def _bank_paths():
    return sorted(p.relative_to(BANK).as_posix() for p in BANK.rglob("*.json"))


def test_spec008_c_every_bank_course_has_a_block_and_a_name():
    """FR-020, US3-AS1: every file of the real bank resolves, through the catalogue, to one of the
    four blocks and a non-empty name; the catalogue has nothing to say against the bank."""
    from src.domain.bank.catalogue import catalogue_problems, course_entry
    from src.domain.entities import COURSE_BLOCKS

    paths = _bank_paths()
    assert len(paths) == 49
    for path in paths:
        entry = course_entry(Path(path).stem, path)
        assert entry is not None, path
        assert entry.block in COURSE_BLOCKS, path
        assert isinstance(entry.name, str) and entry.name.strip(), path
    assert catalogue_problems(paths) == []


@pytest.mark.parametrize("grade", GRADES)
@pytest.mark.parametrize("subject", sorted(SUBJECT_LABELS))
def test_spec008_c_a_semillero_file_gives_block_grade_and_name(subject, grade):
    """FR-021, US3-AS2 (O-C3): `semillero/<subject>_semillero_<g>.json` is block «Semillero»,
    grade g, name «<label> Semillero <g>°» — with no entry of its own in the catalogue."""
    from src.domain.bank.catalogue import COURSES, course_entry, semillero_grade

    course_id = f"{subject}_semillero_{grade}"
    entry = course_entry(course_id, f"semillero/{course_id}.json")

    assert course_id not in COURSES
    assert (entry.block, entry.grade, entry.name) == (
        "Semillero",
        grade,
        f"{SUBJECT_LABELS[subject]} Semillero {grade}°",
    )
    assert semillero_grade(course_id) == grade


@pytest.mark.parametrize(
    "path",
    [
        "semillero/logica_semillero_5.json",  # grade below 6
        "semillero/logica_semillero_12.json",  # grade above 11
        "semillero/astronomia_semillero_7.json",  # unknown subject
        "semillero/logica.json",  # no grade at all
        "logica_semillero_6.json",  # top-level, named like a semillero course (O-C4)
    ],
)
def test_spec008_c_a_semillero_name_outside_the_rule_is_refused(path):
    """FR-021 (O-C4): a semillero course is its folder AND its name; anything else has no entry,
    and the validator's check names the file."""
    from src.domain.bank.catalogue import catalogue_problems, course_entry

    assert course_entry(Path(path).stem, path) is None
    problems = catalogue_problems(_bank_paths() + [path])
    assert any(path in p for p in problems), problems


def test_spec008_c_the_catalogue_imports_only_the_standard_library():
    """FR-020 (O-C1): the catalogue is pure domain data; importing it loads nothing outside the
    standard library and `src` itself, so the bank job (pytest only) can import it."""
    probe = (
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "before = set(sys.modules)\n"
        "import src.domain.bank.catalogue\n"
        "loaded = {m.split('.')[0] for m in set(sys.modules) - before}\n"
        "print(sorted(loaded - set(sys.stdlib_module_names) - {'src'}))\n"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", probe], capture_output=True, text=True, timeout=60
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"
