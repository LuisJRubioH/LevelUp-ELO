# ======================================================
# elo/model.py
# ======================================================
"""Rating formulas of the ELO engine (spec 001, contracts/domain.md). Pure functions, no I/O."""

from dataclasses import dataclass, field

K_PRACTICE = 32.0  # rating and item updates (FR-002, FR-005)
K_PVP = 24.0  # match result (FR-025)
RD_MAX = 350.0
RD_MIN = 30.0
RD_DECAY = 0.05
MISSING_RESPONSE_SECONDS = 30.0
MIN_RESPONSE_SECONDS = 3.0
MAX_RESPONSE_SECONDS = 600.0
DIAGNOSTIC_START = 1000.0
DIAGNOSTIC_FLOOR = 760.0


def procedure_elo_delta(score: float) -> float:
    """Ajuste oficial de una revisión docente, entre -10 y +10 puntos."""
    if not 0.0 <= score <= 100.0:
        raise ValueError("La nota del procedimiento debe estar entre 0 y 100.")
    return round((score - 50.0) * 0.2, 4)


@dataclass
class Item:
    difficulty: float
    weight: float = 1.0


@dataclass
class User:
    """Modelo de dominio para un usuario del sistema LMS."""

    id: int
    username: str
    role: str  # 'student' | 'teacher' | 'admin'
    education_level: str = "universidad"  # 'universidad' | 'colegio'
    enrolled_courses: list = field(default_factory=list)  # lista de course_id


@dataclass
class Course:
    """Representa un curso (unidad de contenido del LMS)."""

    id: str  # slug derivado del nombre de archivo, ej: 'algebra_lineal'
    name: str  # nombre legible, ej: 'Álgebra Lineal'
    block: str  # 'Universidad' | 'Colegio'
    description: str = ""


def expected_score(rating_a: float, rating_b: float) -> float:
    """Probability that A beats B: 1 / (1 + 10^((B − A) / 400)) (FR-001)."""
    exponent = (rating_b - rating_a) / 400
    return 1.0 / (1.0 + 10**exponent)


def rating_delta(rating: float, rd: float, difficulty: float, result: float) -> float:
    """Change of the student's rating: 32 × (RD / 350) × (result − P) (FR-002).

    The only formula used by both the answer update and the answer preview.
    """
    return K_PRACTICE * (rd / RD_MAX) * (result - expected_score(rating, difficulty))


def next_rd(rd: float) -> float:
    """Uncertainty after a valid answer: max(30, RD × 0.95) (FR-003)."""
    return max(RD_MIN, rd * (1 - RD_DECAY))


def item_difficulty_delta(rating: float, difficulty: float, result: float) -> float:
    """Change of the item's difficulty: 32 × ((1 − result) − (1 − P)) (FR-005)."""
    return K_PRACTICE * ((1.0 - result) - (1.0 - expected_score(rating, difficulty)))


def is_valid_response_time(seconds: float | None) -> bool:
    """Whether an answer may move ratings: 3 ≤ s ≤ 600 (FR-008).

    Only an absent time (None) counts as 30 s; an explicit 0 is a value, so invalid (FR-008a).
    """
    if seconds is None:
        seconds = MISSING_RESPONSE_SECONDS
    return MIN_RESPONSE_SECONDS <= seconds <= MAX_RESPONSE_SECONDS


def pvp_deltas(rating_a: float, rating_b: float, outcome_a: float) -> tuple[float, float]:
    """Match result for A and B: 24 × (outcome − expected); outcome 1 / 0.5 / 0 (FR-025)."""
    delta_a = K_PVP * (outcome_a - expected_score(rating_a, rating_b))
    return delta_a, -delta_a


def diagnostic_tier(difficulty: float) -> tuple[int, int]:
    """(win, loss) of one diagnostic answer by item difficulty (FR-020)."""
    if difficulty < 1100:
        return 14, -20
    if difficulty >= 1450:
        return 34, -6
    return 22, -12


def diagnostic_baseline(answers) -> float:
    """Starting topic rating from (difficulty, correct) pairs; None = skipped (FR-020)."""
    total = DIAGNOSTIC_START
    for difficulty, correct in answers:
        if correct is None:
            continue
        win, loss = diagnostic_tier(difficulty)
        total += win if correct else loss
    return max(DIAGNOSTIC_FLOOR, total)
