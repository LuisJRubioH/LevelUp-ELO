"""
Spec 001 characterization pins for the rating engine (tasks T004, T012, T016, T019).

[AS-IS]: every assertion here holds on the code before the spec 001 refactor and must keep
holding after it. A failure means behaviour changed; it is never fixed by editing a number.
"""

import random

import pytest

from src.domain.elo.model import Item, expected_score
from src.domain.elo.uncertainty import RatingModel
from src.domain.elo.vector_elo import VectorRating
from src.domain.selector.item_selector import AdaptiveItemSelector


def _formula(rating, difficulty):
    return 1 / (1 + 10 ** ((difficulty - rating) / 400))


@pytest.mark.parametrize("rating,difficulty", [(1000, 950), (1000, 1100), (1500, 1000)])
def test_spec001_fr001_both_engine_paths_use_the_same_expected_success(rating, difficulty):
    """FR-001: the rating update (RatingModel) and the item update (expected_score) agree."""
    assert expected_score(rating, difficulty) == pytest.approx(_formula(rating, difficulty))
    assert RatingModel(rating).expected_score(difficulty) == pytest.approx(
        _formula(rating, difficulty)
    )


# ── T012: FR-002, FR-003, FR-004, US1-AS1, US1-AS2, edge "RD floor 30" ────────


@pytest.mark.parametrize("result,expected_rating", [(1.0, 1016.0), (0.0, 984.0)])
def test_spec001_new_topic_answer_from_defaults(result, expected_rating):
    """US1-AS1/AS2: no rating yet → starts at 1000/350; D=1000 → ±16 and RD 332.5."""
    vector = VectorRating()

    rating, rd = vector.update("Fracciones", 1000.0, result)

    assert rating == pytest.approx(expected_rating, abs=1e-9)
    assert rd == pytest.approx(332.5, abs=1e-9)


def test_spec001_rd_floor_30_holds_and_scales_the_change():
    """FR-002/FR-003 edge: at RD 30 the RD stays 30 and the change is 32·30/350·0.5."""
    vector = VectorRating()
    vector.ratings["Fracciones"] = (1000.0, 30.0)

    rating, rd = vector.update("Fracciones", 1000.0, 1.0)

    assert rd == 30.0
    assert rating == pytest.approx(1000.0 + 32 * 30 / 350 * 0.5, abs=1e-9)


# ── T016: FR-017, US2-AS1 ────────────────────────────────────────────────────


def test_spec001_selection_keeps_the_zdp_window_and_the_probability_band():
    """US2-AS1: rating 1000, items 600/950/1100/1600 → 950 every time.

    600 and 1600 fall outside ±250; 1100 has P = 0.36 < 0.40; only 950 (P = 0.57) qualifies.
    """
    selector = AdaptiveItemSelector(rng=random.Random(1))
    items = [Item(difficulty=d) for d in (600.0, 950.0, 1100.0, 1600.0)]

    picks = {selector.select_optimal_item(1000.0, items).difficulty for _ in range(50)}

    assert picks == {950.0}


# ── T019: FR-025 (formula), US5-AS1 ──────────────────────────────────────────


def test_spec001_pvp_equal_ratings_win_and_draw():
    """US5-AS1: 24 × (outcome − expected) at 1000 vs 1000 → ±12; a draw moves nobody."""
    from src.domain.elo.model import pvp_deltas

    assert pvp_deltas(1000, 1000, 1.0) == (12.0, -12.0)
    assert pvp_deltas(1000, 1000, 0.5) == (0.0, 0.0)
