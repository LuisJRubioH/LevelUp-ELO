"""
Spec 007 delivery F (FR-041, US4-AS2; owner decisions O3, O-F7, O-F9): the winner rule.

Higher score wins; on equal scores the lower total answer time, compared in whole seconds, wins;
equal whole seconds is a draw. A pure function in the domain: no clock, no I/O.
"""

import pytest

from src.domain.pvp.outcome import match_outcome


@pytest.mark.parametrize(
    "scores, elapsed, expected",
    [
        # a higher score wins whatever the time
        ((6, 5), (500.0, 10.0), (1.0, False)),
        ((3, 7), (1.0, 900.0), (0.0, False)),
        # equal scores: the lower total time wins, by speed
        ((5, 5), (40.2, 52.9), (1.0, True)),
        ((5, 5), (61.0, 60.9), (0.0, True)),
        # equal whole seconds is a draw (O3: "a draw remains only on equal time to the second")
        ((5, 5), (40.1, 40.9), (0.5, False)),
        # 0–0 with no counted answer: both 0 s, a draw as before F
        ((0, 0), (0.0, 0.0), (0.5, False)),
    ],
)
def test_spec007_equal_scores_the_faster_player_wins(scores, elapsed, expected):
    outcome = match_outcome(*scores, *elapsed)

    assert (outcome.result_p1, outcome.tiebreak) == expected
