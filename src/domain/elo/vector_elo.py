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

    def update(self, concept: str, difficulty: float, result: float) -> Tuple[float, float]:
        """Actualiza el rating y RD del tópico con el modelo de incertidumbre (model.py)."""
        current_r, current_rd = self.ratings.get(concept, (1000.0, 350.0))
        new_r, new_rd = RatingModel(current_r, current_rd).update(result, difficulty)
        self.ratings[concept] = (new_r, new_rd)
        return new_r, new_rd
