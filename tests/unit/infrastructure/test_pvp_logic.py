"""
tests/unit/infrastructure/test_pvp_logic.py
============================================
Pruebas de la lógica de la liga PvP (api/websocket/pvp.py) en aislamiento:
  - pvp_deltas (dominio, antes _elo_deltas): ELO por resultado (K=24, simétrico, suma cero).
  - _finish_match: determina ganador, calcula deltas, persiste y emite game_end.

Sin servidor ni WebSocket real: se usan fakes async.
"""

import asyncio
import pytest

from api.websocket import pvp
from api.websocket.pvp import (
    ActiveMatch,
    LobbySlot,
    _finish_match,
)
from src.domain.elo.model import K_PVP as K, pvp_deltas


def _elo_deltas(winner_elo, loser_elo, draw=False):
    """The old helper's call shape, kept so the assertions below stay unchanged (spec 001 T027)."""
    return pvp_deltas(winner_elo, loser_elo, 0.5 if draw else 1.0)


# ── Fakes ─────────────────────────────────────────────────────────────────────


class FakeWS:
    """WebSocket mínimo que captura los mensajes enviados."""

    def __init__(self):
        self.sent = []

    async def send_json(self, msg):
        self.sent.append(msg)


class FakeRepo:
    """Repo que captura la llamada a finish_pvp_match."""

    def __init__(self):
        self.finished_call = None

    def finish_pvp_match(self, **kwargs):
        self.finished_call = kwargs


def _make_match(score_p1, score_p2, elo_p1=1000.0, elo_p2=1000.0):
    p1 = LobbySlot(user_id=1, username="uno", elo=elo_p1, ws=FakeWS())
    p2 = LobbySlot(user_id=2, username="dos", elo=elo_p2, ws=FakeWS())
    return ActiveMatch(
        match_id=99,
        course_id="curso",
        p1=p1,
        p2=p2,
        items=[],
        correct={},
        score={1: score_p1, 2: score_p2},
    )


# ── _elo_deltas ───────────────────────────────────────────────────────────────


class TestEloDeltas:
    def test_win_vs_equal_is_plus_half_K(self):
        """Ganar a un rival de igual ELO → +K/2 para el ganador, −K/2 para el perdedor."""
        dw, dl = _elo_deltas(1000.0, 1000.0)
        assert dw == pytest.approx(K * 0.5)  # +12 con K=24
        assert dl == pytest.approx(-K * 0.5)  # −12

    def test_draw_vs_equal_is_zero(self):
        """Empate entre iguales → 0 para ambos."""
        dw, dl = _elo_deltas(1000.0, 1000.0, draw=True)
        assert dw == pytest.approx(0.0)
        assert dl == pytest.approx(0.0)

    def test_win_vs_stronger_gives_more(self):
        """Ganar a un rival MÁS fuerte da más puntos que ganar a uno igual."""
        dw_equal, _ = _elo_deltas(1000.0, 1000.0)
        dw_upset, _ = _elo_deltas(1000.0, 1400.0)  # gano siendo el más débil
        assert dw_upset > dw_equal

    def test_zero_sum_on_decisive(self):
        """En partida decisiva, lo que gana uno lo pierde el otro (suma cero)."""
        dw, dl = _elo_deltas(1200.0, 900.0)
        assert dw + dl == pytest.approx(0.0)


# ── _finish_match ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestFinishMatch:
    async def test_winner_gets_positive_loser_negative(self):
        match = _make_match(score_p1=6, score_p2=5)
        repo = FakeRepo()
        await _finish_match(match, repo)

        # p1 ganó
        assert repo.finished_call["winner_id"] == 1
        assert repo.finished_call["elo_delta_p1"] > 0
        assert repo.finished_call["elo_delta_p2"] < 0

    async def test_game_end_sent_to_both_players(self):
        match = _make_match(score_p1=3, score_p2=7)
        repo = FakeRepo()
        await _finish_match(match, repo)

        p1_msgs = [m for m in match.p1.ws.sent if m["type"] == "game_end"]
        p2_msgs = [m for m in match.p2.ws.sent if m["type"] == "game_end"]
        assert len(p1_msgs) == 1
        assert len(p2_msgs) == 1
        # p2 ganó (7 > 3) → won=True para p2, False para p1
        assert p1_msgs[0]["won"] is False
        assert p2_msgs[0]["won"] is True
        # Cada quien ve su propio score primero
        assert p1_msgs[0]["your_score"] == 3 and p1_msgs[0]["opp_score"] == 7
        assert p2_msgs[0]["your_score"] == 7 and p2_msgs[0]["opp_score"] == 3

    async def test_draw_marks_both_draw_true(self):
        match = _make_match(score_p1=5, score_p2=5)
        repo = FakeRepo()
        await _finish_match(match, repo)

        assert repo.finished_call["winner_id"] is None
        for ws in (match.p1.ws, match.p2.ws):
            end = [m for m in ws.sent if m["type"] == "game_end"][0]
            assert end["draw"] is True
            assert end["won"] is False

    async def test_double_finish_is_guarded(self):
        """Llamar _finish_match dos veces (ambos loops / timer) emite game_end UNA sola vez."""
        match = _make_match(score_p1=8, score_p2=2)
        repo = FakeRepo()
        await asyncio.gather(_finish_match(match, repo), _finish_match(match, repo))

        p1_ends = [m for m in match.p1.ws.sent if m["type"] == "game_end"]
        assert len(p1_ends) == 1
        assert match.finished is True


# ── Spec 001 (T052): game_end reports what was applied, with its reason ──────


class AppliedRepo:
    def __init__(self, applied=None, fail=False):
        self.applied = applied
        self.fail = fail

    def finish_pvp_match(self, **_kwargs):
        if self.fail:
            raise RuntimeError("db down")
        return self.applied


@pytest.mark.asyncio
async def test_spec001_game_end_sends_the_applied_delta_and_reason():
    match = _make_match(score_p1=6, score_p2=5)
    await _finish_match(match, AppliedRepo({"p1": (12.0, None), "p2": (0.0, "no_rated_topics")}))

    p1_end = [m for m in match.p1.ws.sent if m["type"] == "game_end"][0]
    p2_end = [m for m in match.p2.ws.sent if m["type"] == "game_end"][0]
    assert (p1_end["elo_delta"], p1_end["elo_reason"]) == (12.0, None)
    assert (p2_end["elo_delta"], p2_end["elo_reason"]) == (0.0, "no_rated_topics")


@pytest.mark.asyncio
async def test_spec001_game_end_reports_not_applied_when_persistence_fails():
    match = _make_match(score_p1=6, score_p2=5)
    await _finish_match(match, AppliedRepo(fail=True))

    for ws in (match.p1.ws, match.p2.ws):
        end = [m for m in ws.sent if m["type"] == "game_end"][0]
        assert (end["elo_delta"], end["elo_reason"]) == (0.0, "not_applied")
