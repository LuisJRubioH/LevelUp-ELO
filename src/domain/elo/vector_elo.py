# ======================================================
# elo/vector_elo.py
# ======================================================
from typing import Dict, Tuple
from .uncertainty import RatingModel


class VectorRating:
    """
    Gestiona múltiples calificaciones y sus desviaciones (incertidumbre) por tópico.
    """

    def __init__(self):
        # Mapeo de tópico -> (rating, rd)
        self.ratings: Dict[str, Tuple[float, float]] = {}

    def get(self, concept: str) -> float:
        """Retorna el rating del tópico (default 1000.0)."""
        return self.ratings.get(concept, (1000.0, 350.0))[0]

    def get_rd(self, concept: str) -> float:
        """Retorna la desviación del tópico (default 350.0)."""
        return self.ratings.get(concept, (1000.0, 350.0))[1]

    def update(
        self, concept: str, difficulty: float, result: float, impact_modifier: float = 1.0
    ) -> Tuple[float, float]:
        """
        Actualiza el rating y RD usando el modelo de incertidumbre.
        Impact_modifier escala el cambio final (mantenemos compatibilidad con IA cognitiva).
        """
        current_r, current_rd = self.ratings.get(concept, (1000.0, 350.0))

        model = RatingModel(current_r, current_rd)
        new_r, new_rd = model.update(result, difficulty)

        # Aplicar el modificador de impacto al DELTA del rating si es necesario
        delta = (new_r - current_r) * impact_modifier
        final_r = current_r + delta

        self.ratings[concept] = (final_r, new_rd)
        return final_r, new_rd


def aggregate_global_elo(vector: VectorRating) -> float:
    if not vector.ratings:
        return 1000.0
    return sum(r for r, rd in vector.ratings.values()) / len(vector.ratings)


def aggregate_global_rd(vector: VectorRating) -> float:
    if not vector.ratings:
        return 350.0
    return sum(rd for r, rd in vector.ratings.values()) / len(vector.ratings)
