# ======================================================
# selector/item_selector.py
# ======================================================
from typing import List
from elo.model import Item, expected_score
from elo.zdp import zdp_interval


class AdaptiveItemSelector:
    def __init__(self, delta: float = 100.0):
        self.delta = delta

    def information(self, p: float) -> float:
        return p * (1 - p)

    def select(self, student_rating: float, items: List[Item]) -> Item:
        low, high = zdp_interval(student_rating, self.delta)
        candidates = [i for i in items if low <= i.difficulty <= high]
        pool = candidates if candidates else items
        return max(
            pool,
            key=lambda i: self.information(expected_score(student_rating, i.difficulty)) * i.weight
        )

