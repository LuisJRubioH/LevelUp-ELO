# ======================================================
# elo/uncertainty.py
# ======================================================
import math

from .model import RD_MAX, expected_score, next_rd, rating_delta


class RatingModel:
    """
    Versión simplificada de un sistema con incertidumbre (inspirado en Glicko).
    Gestiona el rating y el Rating Deviation (RD); las fórmulas viven en model.py.
    """

    def __init__(self, rating: float = 1000.0, rd: float = RD_MAX):
        self.rating = rating
        self.rd = rd

    def expected_score(self, opponent_difficulty: float) -> float:
        """Calcula la probabilidad esperada de éxito."""
        return expected_score(self.rating, opponent_difficulty)

    def update(self, actual_score: float, opponent_difficulty: float) -> tuple[float, float]:
        """
        Actualiza el rating y el RD basado en un resultado.
        actual_score: 1.0 (acierto) o 0.0 (fallo)
        Retorna: (nuevo_rating, nuevo_rd)
        """
        self.rating += rating_delta(self.rating, self.rd, opponent_difficulty, actual_score)
        self.rd = next_rd(self.rd)
        return self.rating, self.rd

    def get_confidence_interval(self) -> tuple[float, float]:
        """Retorna el rango de confianza (Rating ± RD)."""
        return self.rating - self.rd, self.rating + self.rd

    @staticmethod
    def calculate_g_rd(rd: float) -> float:
        """Factor de escala G basado en el RD (para versiones más avanzadas)."""
        q = math.log(10) / 400
        return 1.0 / math.sqrt(1 + 3 * (q * rd / math.pi) ** 2)
