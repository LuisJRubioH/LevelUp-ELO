# ======================================================
# elo/uncertainty.py
# ======================================================
import math


class RatingModel:
    """
    Versión simplificada de un sistema con incertidumbre (inspirado en Glicko).
    Gestiona el rating y el Rating Deviation (RD).
    """

    def __init__(self, rating: float = 1000.0, rd: float = 350.0):
        self.rating = rating
        self.rd = rd

        # Constantes del modelo
        self.RD_BASE = 350.0  # Incertidumbre máxima inicial
        self.RD_MIN = 30.0  # Incertidumbre mínima (estabilidad)
        self.K_BASE = 32.0  # Factor K base para el cambio de rating
        self.RD_DECAY = 0.05  # Tasa de reducción de RD por cada intento

    def expected_score(self, opponent_difficulty: float) -> float:
        """Calcula la probabilidad esperada de éxito."""
        return 1.0 / (1.0 + 10 ** ((opponent_difficulty - self.rating) / 400))

    def update(self, actual_score: float, opponent_difficulty: float) -> tuple[float, float]:
        """
        Actualiza el rating y el RD basado en un resultado.
        actual_score: 1.0 (acierto) o 0.0 (fallo)
        Retorna: (nuevo_rating, nuevo_rd)
        """
        expected = self.expected_score(opponent_difficulty)

        # 1. Escalar el impacto basado en la incertidumbre actual (RD)
        # A mayor RD, mayor es la corrección del rating.
        uncertainty_factor = self.rd / self.RD_BASE
        delta = self.K_BASE * uncertainty_factor * (actual_score - expected)

        self.rating += delta

        # 2. Reducir la incertidumbre (el sistema confía más en el rating con cada dato)
        # Usamos una reducción multiplicativa simple
        self.rd = max(self.RD_MIN, self.rd * (1 - self.RD_DECAY))

        return self.rating, self.rd

    def get_confidence_interval(self) -> tuple[float, float]:
        """Retorna el rango de confianza (Rating ± RD)."""
        return self.rating - self.rd, self.rating + self.rd

    @staticmethod
    def calculate_g_rd(rd: float) -> float:
        """Factor de escala G basado en el RD (para versiones más avanzadas)."""
        q = math.log(10) / 400
        return 1.0 / math.sqrt(1 + 3 * (q * rd / math.pi) ** 2)
