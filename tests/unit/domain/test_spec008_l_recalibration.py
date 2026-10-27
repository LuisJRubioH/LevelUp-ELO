"""
Spec 008 delivery L (FR-032, plan-l.md O-IL9): the recalibration arithmetic, pure domain code.

`dstar` is the difficulty D at which the expected successes of the students who answered an item,
Σ expected_score(rating_i, D), equal the successes observed — for one rating R and a success share
P* it is AGENTS' `R + 400·log10((1 − P*)/P*)`. `plan_recalibration` turns raw attempt rows into
the changes the script writes.
"""

import math

import pytest

from src.domain.bank.recalibration import plan_recalibration
from src.domain.elo.model import dstar, expected_score


@pytest.mark.parametrize("share, offset", [(0.25, 191), (0.10, 382), (0.5, 0), (0.75, -191)])
def test_spec008_l_dstar_inverts_the_expected_score(share, offset):
    """FR-032: for one rating the closed form, AGENTS' examples included; for mixed ratings the
    expected successes equal the observed ones."""
    ratings = [1000.0] * 20

    assert round(dstar(ratings, share * 20)) == 1000 + offset
    assert dstar(ratings, share * 20) == pytest.approx(
        1000 + 400 * math.log10((1 - share) / share), abs=0.01
    )

    mixed = [700.0, 900.0, 1100.0, 1300.0, 1500.0]
    d = dstar(mixed, 2.0)
    assert sum(expected_score(r, d) for r in mixed) == pytest.approx(2.0, abs=1e-6)


def _rows(item_id, n, successes, rating=1000.0, difficulty=1000.0, bank=1000, retired=None):
    return [
        {
            "item_id": item_id,
            "course_id": "curso_l",
            "difficulty": difficulty,
            "bank_difficulty": bank,
            "retired_at": retired,
            "elo_before": rating,
            "is_correct": k < successes,
        }
        for k in range(n)
    ]


def test_spec008_l_the_plan_skips_retired_few_attempts_and_small_changes():
    """FR-032, O-IL9: items with fewer than 10 valid attempts, retired items and changes under 25
    are skipped; 0 % and 100 % give a finite difficulty; the result is an integer in 400–2000;
    `bank` plans the bank value where it differs."""
    rows = (
        _rows("few", 9, 0)
        + _rows("retired", 20, 0, retired="2026-10-01 00:00:00")
        + _rows("small", 20, 10, difficulty=1010.0)  # D* = 1000: |Δ| = 10
        + _rows("hard", 20, 0, rating=1500.0)  # 0 %: smoothed, then clamped to 2000
        + _rows("easy", 20, 20, rating=700.0)  # 100 %: smoothed, then clamped to 400
        + _rows("quarter", 40, 10)  # 25 % (smoothed 10.5/41)
        + [{**_rows("unanswered", 1, 0)[0], "elo_before": None, "is_correct": None}]
    )

    plan = {c["item_id"]: c for c in plan_recalibration(rows, "dstar")}

    assert set(plan) == {"hard", "easy", "quarter"}
    assert plan["hard"]["new"] == 2000 and plan["easy"]["new"] == 400
    expected = 1000 + 400 * math.log10((1 - 10.5 / 41) / (10.5 / 41))
    assert plan["quarter"]["new"] == round(expected)
    assert all(isinstance(c["new"], int) for c in plan.values())
    assert plan["quarter"]["previous"] == 1000.0
    assert plan["quarter"]["detail"] == "40 attempts, 10 successes"

    banked = (
        _rows("edited", 1, 0, difficulty=719.0, bank=1000)
        + _rows("same", 1, 0, difficulty=900.0, bank=900)
        + _rows("never", 1, 0, difficulty=900.0, bank=None)
        + [{**_rows("unanswered", 1, 0, difficulty=600.0, bank=881)[0], "elo_before": None}]
    )
    plan = {c["item_id"]: c for c in plan_recalibration(banked, "bank")}

    assert {k: (c["previous"], c["new"]) for k, c in plan.items()} == {
        "edited": (719.0, 1000),
        "unanswered": (600.0, 881),
    }
