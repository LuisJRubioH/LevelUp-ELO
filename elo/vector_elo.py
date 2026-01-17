# ======================================================
# elo/vector_elo.py
# ======================================================
from typing import Dict
from elo.model import expected_score


class VectorELO:
    def __init__(self):
        self.ratings: Dict[str, float] = {}

    def get(self, concept: str) -> float:
        return self.ratings.get(concept, 1000.0)

    def update(self, concept: str, difficulty: float, result: float, k_factor: float):
        r = self.get(concept)
        p = expected_score(r, difficulty)
        self.ratings[concept] = r + k_factor * (result - p)


def aggregate_global_elo(vector: VectorELO) -> float:
    if not vector.ratings:
        return 1000.0
    return sum(vector.ratings.values()) / len(vector.ratings)

