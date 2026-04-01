"""Entidades de dominio del sistema LevelUp-ELO.

Complementa los dataclasses de model.py con entidades de negocio
que encapsulan invariantes del dominio (reglas que nunca cambian).
"""

from dataclasses import dataclass, field
from typing import Optional


# Valores canónicos del nivel educativo (fuente de verdad del dominio)
LEVEL_UNIVERSIDAD = 'universidad'
LEVEL_COLEGIO     = 'colegio'
LEVEL_CONCURSOS   = 'concursos'
LEVEL_SEMILLERO   = 'semillero'
VALID_LEVELS      = frozenset({LEVEL_UNIVERSIDAD, LEVEL_COLEGIO, LEVEL_CONCURSOS, LEVEL_SEMILLERO})

# ── Estados del flujo de validación de procedimientos ────────────────────────
# Invariante CRÍTICA: ai_proposed_score NUNCA afecta ELO ni estadísticas.
# Solo final_score (establecido por el docente) puede usarse en analytics.
PROC_STATUS_PENDING            = 'pending'                    # Enviado, sin revisión IA
PROC_STATUS_PENDING_VALIDATION = 'PENDING_TEACHER_VALIDATION' # IA propuso; espera docente
PROC_STATUS_VALIDATED          = 'VALIDATED_BY_TEACHER'       # Docente validó → oficial

# Bloque en la tabla `courses` correspondiente a cada nivel
LEVEL_TO_BLOCK = {
    LEVEL_UNIVERSIDAD: 'Universidad',
    LEVEL_COLEGIO:     'Colegio',
    LEVEL_CONCURSOS:   'Concursos',
    LEVEL_SEMILLERO:   'Semillero',
}


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
            LEVEL_COLEGIO:     "🏫 Colegio",
            LEVEL_CONCURSOS:   "🏆 Preparación para Concursos",
            LEVEL_SEMILLERO:   "🏅 Semillero de Matemáticas",
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
    teacher_score: Optional[float]     = field(default=None)
    final_score: Optional[float]       = field(default=None)
    teacher_feedback: Optional[str]    = field(default=None)

    def __post_init__(self):
        valid_statuses = {
            PROC_STATUS_PENDING,
            PROC_STATUS_PENDING_VALIDATION,
            PROC_STATUS_VALIDATED,
            'reviewed',  # valor heredado de versiones anteriores
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
