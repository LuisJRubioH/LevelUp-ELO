"""Entidades de dominio del sistema LevelUp-ELO.

Complementa los dataclasses de model.py con entidades de negocio
que encapsulan invariantes del dominio (reglas que nunca cambian).
"""

from dataclasses import dataclass, field
from typing import Optional


# Valores canónicos del nivel educativo (fuente de verdad del dominio)
LEVEL_UNIVERSIDAD = "universidad"
LEVEL_COLEGIO = "colegio"
LEVEL_CONCURSOS = "concursos"
LEVEL_SEMILLERO = "semillero"
VALID_LEVELS = frozenset({LEVEL_UNIVERSIDAD, LEVEL_COLEGIO, LEVEL_CONCURSOS, LEVEL_SEMILLERO})

# ── Estados del flujo de validación de procedimientos ────────────────────────
# Invariante CRÍTICA: ai_proposed_score NUNCA afecta ELO ni estadísticas.
# Solo final_score (establecido por el docente) puede usarse en analytics.
PROC_STATUS_PENDING = "pending"  # Enviado, sin revisión IA
PROC_STATUS_PENDING_VALIDATION = "PENDING_TEACHER_VALIDATION"  # IA propuso; espera docente
PROC_STATUS_VALIDATED = "VALIDATED_BY_TEACHER"  # Docente validó → oficial

# Bloque en la tabla `courses` correspondiente a cada nivel
LEVEL_TO_BLOCK = {
    LEVEL_UNIVERSIDAD: "Universidad",
    LEVEL_COLEGIO: "Colegio",
    LEVEL_CONCURSOS: "Concursos",
    LEVEL_SEMILLERO: "Semillero",
}


# The four values of courses.block the code writes (spec 001 FR-028n).
COURSE_BLOCKS = tuple(LEVEL_TO_BLOCK.values())

# Grades a semillero student may have (spec 001 FR-028k, FR-028m).
SEMILLERO_GRADES = frozenset({"6", "7", "8", "9", "10", "11"})


def valid_semillero_grade(grade) -> bool:
    """A semillero grade from 6 to 11, as stored ('6' … '11') or as a number."""
    return grade is not None and str(grade) in SEMILLERO_GRADES


def in_catalogue(level: Optional[str], grade, course_id: str, block: str) -> bool:
    """Whether a course belongs to the catalogue of a student's level (and grade, for semillero).

    Spec 001 FR-028k. Every semillero course has block 'Semillero'; its grade is the id suffix
    (`algebra_semillero_6`), read by the course catalogue's `semillero_grade` (spec 008 O-C8). A
    semillero student without a valid grade has no catalogue: no grade is ever inferred. An
    unknown or missing level falls back to universidad.
    """
    from src.domain.bank.catalogue import semillero_grade  # the catalogue imports this module

    level = (level or LEVEL_UNIVERSIDAD).lower()
    if level not in VALID_LEVELS:
        level = LEVEL_UNIVERSIDAD
    if block != LEVEL_TO_BLOCK[level]:
        return False
    if level == LEVEL_SEMILLERO:
        return valid_semillero_grade(grade) and semillero_grade(course_id) == str(grade)
    return True


def catalogue_enrolment_group(group: Optional[dict], course_id: str) -> Optional[int]:
    """The group a catalogue enrolment in `course_id` is recorded with, or None to refuse it.

    Spec 001 FR-028v (delivery TCH): no enrolment without a teacher. `group` is the student's own
    group as `{"group_id", "course_id", "teacher_ok"}`, or None when they have none. Its teacher
    reviews the course when that teacher is approved and active (`teacher_ok`) and the group has
    no course or has this one (spec 006 FR-050).
    """
    if not group or not group["teacher_ok"]:
        return None
    if group["course_id"] not in (None, course_id):
        return None
    return group["group_id"]


@dataclass
class Student:
    """Representa a un estudiante con su nivel académico.

    Invariante de dominio: `level` debe estar en VALID_LEVELS.
    El nivel determina qué catálogo de cursos puede ver el estudiante.
    """

    id: int
    username: str
    level: str  # 'universidad' | 'colegio'

    def __post_init__(self):
        _normalized = self.level.lower() if self.level else LEVEL_UNIVERSIDAD
        if _normalized not in VALID_LEVELS:
            raise ValueError(
                f"Nivel educativo inválido: '{self.level}'. "
                f"Valores permitidos: {sorted(VALID_LEVELS)}"
            )
        self.level = _normalized

    @property
    def block(self) -> str:
        """Bloque del catálogo correspondiente a este nivel ('Universidad' | 'Colegio')."""
        return LEVEL_TO_BLOCK[self.level]

    @property
    def level_label(self) -> str:
        """Etiqueta legible para la UI."""
        _labels = {
            LEVEL_UNIVERSIDAD: "🎓 Universidad",
            LEVEL_COLEGIO: "🏫 Colegio",
            LEVEL_CONCURSOS: "🏆 Preparación para Concursos",
            LEVEL_SEMILLERO: "🏅 Semillero de Matemáticas",
        }
        return _labels.get(self.level, "🎓 Universidad")


@dataclass
class ProcedureSubmission:
    """Entrega de procedimiento matemático por el estudiante.

    Invariante de dominio:
      - `ai_proposed_score` NUNCA afecta ELO ni estadísticas.
      - Solo `final_score` (validado por el docente) puede usarse en analytics.

    Ciclo de vida del status:
      pending → PENDING_TEACHER_VALIDATION → VALIDATED_BY_TEACHER
    """

    id: int
    student_id: int
    item_id: str
    status: str
    ai_proposed_score: Optional[float] = field(default=None)
    teacher_score: Optional[float] = field(default=None)
    final_score: Optional[float] = field(default=None)
    teacher_feedback: Optional[str] = field(default=None)

    def __post_init__(self):
        valid_statuses = {
            PROC_STATUS_PENDING,
            PROC_STATUS_PENDING_VALIDATION,
            PROC_STATUS_VALIDATED,
            "reviewed",  # valor heredado de versiones anteriores
        }
        if self.status not in valid_statuses:
            raise ValueError(
                f"Estado de procedimiento inválido: '{self.status}'. "
                f"Valores permitidos: {sorted(valid_statuses)}"
            )

    @property
    def is_pending_validation(self) -> bool:
        return self.status == PROC_STATUS_PENDING_VALIDATION

    @property
    def is_validated(self) -> bool:
        return self.status == PROC_STATUS_VALIDATED
