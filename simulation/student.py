# ======================================================
# simulation/student.py
# ======================================================
import random
from elo.model import expected_score, Item


class SimulatedStudent:
    def __init__(self, true_skill: float, noise: float = 0.05):
        self.true_skill = true_skill
        self.noise = noise

    def attempt(self, item: Item) -> float:
        p = expected_score(self.true_skill, item.difficulty)
        p = min(max(p + random.uniform(-self.noise, self.noise), 0), 1)
        if p > 0.75:
            return 1.0
        elif p > 0.45:
            return 0.5
        return 0.0
