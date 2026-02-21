# ======================================================
# elo/model.py
# ======================================================
import math
import statistics
from dataclasses import dataclass

# Constantes configurables para el motor ELO
INITIAL_K = 40.0
GROWTH_K = 32.0
STABLE_K = 16.0
DEFAULT_K = 24.0

INITIAL_ATTEMPTS_THRESHOLD = 30
GROWTH_RATING_THRESHOLD = 1400
STABILITY_ERROR_THRESHOLD = 0.15
STABILITY_SAMPLE_SIZE = 20

@dataclass
class Item:
    difficulty: float
    weight: float = 1.0


@dataclass
class StudentELO:
    rating: float = 1000.0


def expected_score(rating_a: float, rating_b: float) -> float:
    """
    Calcula la probabilidad esperada de que A gane contra B
    según el modelo ELO clásico.
    """
    exponent = (rating_b - rating_a) / 400
    return 1.0 / (1.0 + 10 ** exponent)


def _calculate_average_error(recent_results: list[tuple[float, float]]) -> float:
    """
    Calcula el error absoluto medio entre los resultados reales y los esperados.
    Internal function to support stability-based K calculation.
    """
    if not recent_results:
        return 1.0  # Error máximo asumido ante falta de datos
    
    errors = [abs(actual - expected) for actual, expected in recent_results]
    return statistics.mean(errors)


def calculate_dynamic_k(
    attempts: int,
    rating: float,
    recent_results: list[tuple[float, float]]
) -> float:
    """
    Calcula el Factor K dinámico basado en la experiencia, nivel y estabilidad del estudiante.
    Asume que el orden de evaluación es crítico para la convergencia del sistema.
    """
    # 1. Fase Inicial (Búsqueda rápida de nivel)
    if attempts < INITIAL_ATTEMPTS_THRESHOLD:
        return INITIAL_K
    
    # 2. Fase de Crecimiento (Niveles básicos)
    if rating < GROWTH_RATING_THRESHOLD:
        return GROWTH_K
    
    # 3. Fase de Estabilidad (Consistencia demostrada)
    if len(recent_results) >= STABILITY_SAMPLE_SIZE:
        avg_error = _calculate_average_error(recent_results)
        if avg_error < STABILITY_ERROR_THRESHOLD:
            return STABLE_K
            
    # 4. Caso base (Estándar de producción)
    return DEFAULT_K


def update_elo(student: StudentELO, item: Item, result: float, k: float, impact_modifier: float = 1.0) -> float:
    """
    Actualiza el rating del estudiante usando ELO.
    Retorna el nuevo rating. El impact_modifier escala el cambio final.
    """
    if not 0.0 <= result <= 1.0:
        raise ValueError("result must be between 0 and 1")

    expected = expected_score(student.rating, item.difficulty)
    delta = k * (result - expected) * impact_modifier
    student.rating += delta

    return student.rating
