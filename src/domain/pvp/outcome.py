"""
src/domain/pvp/outcome.py
=========================
Spec 007 FR-041 (owner decisions O3, O-F7, O-F9): who won a League match. Pure — no clock, no I/O.

The higher score wins. On equal scores the player with the lower total answer time wins — the sum,
over their correct answers, of the seconds from `game_start` to the answer — compared in whole
seconds; equal whole seconds is a draw. A win by time is a full win.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class MatchOutcome:
    result_p1: float  # 1.0 player 1 won, 0.0 player 2 won, 0.5 a draw (`pvp_deltas`' outcome)
    tiebreak: bool  # True when the time, not the score, decided it


def match_outcome(
    score_p1: int, score_p2: int, elapsed_p1: float, elapsed_p2: float
) -> MatchOutcome:
    if score_p1 != score_p2:
        return MatchOutcome(1.0 if score_p1 > score_p2 else 0.0, False)
    seconds_p1, seconds_p2 = math.floor(elapsed_p1), math.floor(elapsed_p2)
    if seconds_p1 == seconds_p2:
        return MatchOutcome(0.5, False)
    return MatchOutcome(1.0 if seconds_p1 < seconds_p2 else 0.0, True)
