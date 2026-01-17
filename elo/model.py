# ======================================================
# elo/model.py
# ======================================================
import math
from dataclasses import dataclass


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))


@dataclass
class Item:
    difficulty: float
    weight: float = 1.0


@dataclass
class StudentELO:
    rating: float = 1000.0


def update_elo(student: StudentELO, item: Item, result: float, K: float = 24.0):
    p = expected_score(student.rating, item.difficulty)
    student.rating += K * (result - p)











