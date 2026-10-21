"""
Survey 007 V14 (`docs/sdd/pvp-survey.md` § 7): the League screen rounded the applied PvP delta in
the browser with `Math.round`, which rounds a negative tie toward +∞ (-2.5 → -2) where the
backend's display rule is half up on the value (-2.5 → -3, spec 001 FR-028j). The server now
sends the shown number with the delta — in `game_end` and in the history — and the screen
renders it as given (R15). The applied delta itself is unchanged.
"""

import pytest

from api.websocket import pvp
from src.application.services.rating_read_service import RatingReadService


@pytest.mark.parametrize(
    "applied,shown", [(-2.5, -3), (2.5, 3), (12.0, 12), (-11.4, -11), (0.0, 0)]
)
def test_game_end_carries_the_shown_delta(applied, shown):
    message = pvp._game_end(3, 1, won=True, draw=False, applied=(applied, None))

    assert message["elo_delta"] == applied
    assert message["elo_delta_display"] == shown
    assert (message["your_score"], message["opp_score"]) == (3, 1)


def test_pvp_history_carries_the_shown_delta():
    class Repo:
        def get_pvp_history(self, user_id, limit=20, before=None):
            return [{"elo_delta": d, "won": True} for d in (-2.5, 2.5, None)]

    rows = RatingReadService(Repo()).pvp_history(7)["matches"]

    assert [(r["elo_delta"], r["elo_delta_display"]) for r in rows] == [
        (-2.5, -3),
        (2.5, 3),
        (None, None),
    ]
