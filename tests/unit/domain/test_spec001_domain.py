"""
Spec 001 domain contract (task T023; specs/001-elo-engine/contracts/domain.md).

[CHANGE]: written before the functions existed. Pure functions, no I/O.
"""

import pytest

from src.domain.elo.aggregation import course_rating, overall_rating
from src.domain.elo.model import (
    diagnostic_baseline,
    diagnostic_tier,
    expected_score,
    is_valid_response_time,
    item_difficulty_delta,
    next_rd,
    pvp_deltas,
    rating_delta,
)
from src.domain.elo.ranks import (
    RANKS,
    RATING_DISPLAY_DECIMALS,
    rank_competition,
    rank_for,
    rating_display,
    round_for_display,
)

# ── Update formulas (FR-002, FR-003, FR-005) ─────────────────────────────────


def test_spec001_rating_delta():
    assert rating_delta(1000.0, 350.0, 1000.0, 1.0) == pytest.approx(16.0)
    assert rating_delta(1000.0, 350.0, 1000.0, 0.0) == pytest.approx(-16.0)
    expected = 32 * (175 / 350) * (1.0 - expected_score(1100.0, 1000.0))
    assert rating_delta(1100.0, 175.0, 1000.0, 1.0) == pytest.approx(expected)


def test_spec001_next_rd_has_a_floor_of_30():
    assert next_rd(350.0) == pytest.approx(332.5)
    assert next_rd(31.0) == 30.0
    assert next_rd(30.0) == 30.0


def test_spec001_item_difficulty_delta():
    assert item_difficulty_delta(1000.0, 1000.0, 1.0) == pytest.approx(-16.0)
    assert item_difficulty_delta(1000.0, 1000.0, 0.0) == pytest.approx(16.0)


# ── Validity (FR-008, FR-008a) ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "seconds,valid",
    [
        (None, True),
        (3, True),
        (3.0, True),
        (600, True),
        (30.0, True),
        (0, False),
        (0.0, False),
        (2.99, False),
        (600.01, False),
    ],
)
def test_spec001_is_valid_response_time(seconds, valid):
    """None is absent (30 s); an explicit 0 is a value and invalid (FR-008a)."""
    assert is_valid_response_time(seconds) is valid


# ── PvP (FR-025) ────────────────────────────────────────────────────────────


def test_spec001_pvp_deltas():
    assert pvp_deltas(1000.0, 1000.0, 1.0) == pytest.approx((12.0, -12.0))
    assert pvp_deltas(1000.0, 1000.0, 0.5) == pytest.approx((0.0, 0.0))
    assert pvp_deltas(1000.0, 1000.0, 0.0) == pytest.approx((-12.0, 12.0))
    e = expected_score(1200.0, 1000.0)
    assert pvp_deltas(1200.0, 1000.0, 1.0) == pytest.approx((24 * (1 - e), -24 * (1 - e)))


# ── Diagnostic (FR-020) ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "difficulty,tier",
    [(1099.9, (14, -20)), (1100, (22, -12)), (1449.9, (22, -12)), (1450, (34, -6))],
)
def test_spec001_diagnostic_tier(difficulty, tier):
    assert diagnostic_tier(difficulty) == tier


def test_spec001_diagnostic_baseline():
    """Answers are (difficulty, correct) with None for a skipped question; floor 760."""
    assert diagnostic_baseline([(1200.0, True), (1200.0, None)]) == 1022.0
    assert diagnostic_baseline([(1000.0, False)] * 13) == 760.0
    assert diagnostic_baseline([]) == 1000.0


# ── Aggregation (FR-028a, FR-028b, FR-028i, FR-029a) ────────────────────────


def test_spec001_course_rating():
    assert course_rating([]) is None
    assert course_rating([1200.0, 1000.0]) == 1100.0
    assert course_rating([1200.4, 1200.4, 1201.4]) == pytest.approx(1200.7333333333)


def test_spec001_overall_rating():
    assert overall_rating([]) is None
    assert overall_rating([None, None]) is None
    assert overall_rating([1200.0, None, 1000.0]) == 1100.0  # US6-AS1
    assert overall_rating([1200.7333333333]) == pytest.approx(1200.7333333333)


# ── Ranks and display (FR-031, FR-028h, FR-028i, FR-028j) ───────────────────


def test_spec001_one_rank_scale():
    assert [label for _, label in RANKS] == [
        "Aspirante",
        "Hierro",
        "Bronce II",
        "Bronce I",
        "Plata II",
        "Plata I",
        "Oro II",
        "Oro I",
        "Platino II",
        "Platino I",
        "Diamante II",
        "Diamante I",
        "Maestro",
        "Gran Maestro",
        "Leyenda",
        "Leyenda Suprema",
    ]
    assert [m for m, _ in RANKS] == sorted(m for m, _ in RANKS)
    assert rank_for(None) is None
    assert rank_for(0) == "Aspirante"
    assert rank_for(999.9) == "Plata II"
    assert rank_for(1000) == "Plata I"
    assert rank_for(2500) == "Leyenda Suprema"


@pytest.mark.parametrize(
    "rating,shown",
    [(1199.5, 1200), (1200.5, 1201), (1200.49, 1200), (1200.4999999, 1200), (0.5, 1), (2.5, 3)],
)
def test_spec001_round_for_display_is_half_up(rating, shown):
    """FR-028i: half up on the decimal value — never Python's half-to-even round()."""
    assert RATING_DISPLAY_DECIMALS == 0
    assert round_for_display(rating) == shown
    assert isinstance(round_for_display(rating), int)


@pytest.mark.parametrize(
    "rating,display",
    [
        (999.6, {"display_rating": 1000, "rank_label": "Plata I"}),
        (999.5, {"display_rating": 1000, "rank_label": "Plata I"}),
        (999.4, {"display_rating": 999, "rank_label": "Plata II"}),
        (999.4999999, {"display_rating": 999, "rank_label": "Plata II"}),
        (None, {"display_rating": None, "rank_label": None}),
    ],
)
def test_spec001_rating_display_number_and_label_agree(rating, display):
    """FR-028j, US6-AS9: the label comes from the displayed number, not the full value."""
    assert rating_display(rating) == display


def test_spec001_average_then_round_once():
    """FR-028i: topics 1200.4, 1200.4, 1201.4 → course 1200.733… → ranked as 1201, not 1200."""
    assert round_for_display(course_rating([1200.4, 1200.4, 1201.4])) == 1201


def test_spec001_rank_competition():
    """FR-028h, US6-AS8: 1, 2, 2, 4; ties by user id; attempts never break ties; pending last."""
    entries = [
        {"user_id": 5, "rating": 1150.2, "attempts_in_window": 9},
        {"user_id": 4, "rating": 1200.3, "attempts_in_window": 1},
        {"user_id": 3, "rating": 1199.6, "attempts_in_window": 50},  # ties 1200 below precision
        {"user_id": 9, "rating": None, "attempts_in_window": 2},
        {"user_id": 1, "rating": 1249.5, "attempts_in_window": 0},
    ]

    ranked = rank_competition(entries)

    assert [(e["user_id"], e["rating"], e["rank"]) for e in ranked] == [
        (1, 1250, 1),
        (3, 1200, 2),
        (4, 1200, 2),
        (5, 1150, 4),
        (9, None, None),
    ]
    assert [e["rank_label"] for e in ranked] == ["Oro I", "Oro I", "Oro I", "Oro II", None]
    assert [e["attempts_in_window"] for e in ranked] == [0, 50, 1, 9, 2]
    assert all(isinstance(e["rating"], int) for e in ranked[:4])
