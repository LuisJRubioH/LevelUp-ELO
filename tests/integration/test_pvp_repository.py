"""
tests/integration/test_pvp_repository.py
=========================================
Pruebas de integración de los métodos PvP del SQLiteRepository contra una DB
temporal: create_pvp_match → save_pvp_answer → finish_pvp_match → get_pvp_history.
También cubre get_course_blocks.
"""

import pytest
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from tests.integration.conftest import rating_of, set_rating

COURSE, TOPIC = "calculo_diferencial", "Límites"


@pytest.fixture
def repo(tmp_path) -> SQLiteRepository:
    db_path = str(tmp_path / "test_pvp.db")
    return SQLiteRepository(db_name=db_path)


def _two_players(repo, rated=True):
    """Registra dos estudiantes y retorna (id1, id2).

    Spec 001 (FR-029b/c): a match moves every rated topic of its course, so each player gets
    one rated topic (COURSE, TOPIC) = 1000 unless `rated=False`.
    """
    repo.register_user("jugador_a", "password123", "student", education_level="universidad")
    repo.register_user("jugador_b", "password123", "student", education_level="universidad")
    a = repo.login_user("jugador_a", "password123")[0]
    b = repo.login_user("jugador_b", "password123")[0]
    if rated:
        set_rating(repo, a, COURSE, TOPIC, 1000.0)
        set_rating(repo, b, COURSE, TOPIC, 1000.0)
    return a, b


class TestPvpMatchLifecycle:
    def test_create_returns_match_id(self, repo):
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1", "i2", "i3"])
        assert isinstance(mid, int) and mid > 0

    def test_full_match_recorded_in_history(self, repo):
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1", "i2", "i3"])

        repo.save_pvp_answer(mid, a, "i1", True)
        repo.save_pvp_answer(mid, a, "i2", True)
        repo.save_pvp_answer(mid, b, "i1", False)

        # a gana 2-0
        repo.finish_pvp_match(
            match_id=mid,
            winner_id=a,
            score_p1=2,
            score_p2=0,
            elo_delta_p1=12.0,
            elo_delta_p2=-12.0,
            p1_id=a,
            p2_id=b,
        )

        hist_a = repo.get_pvp_history(a)
        assert len(hist_a) == 1
        m = hist_a[0]
        assert m["won"] is True
        assert m["draw"] is False
        assert m["my_score"] == 2
        assert m["opp_score"] == 0
        assert m["elo_delta"] == 12.0
        assert m["opponent"] == "jugador_b"

    def test_history_perspective_is_per_user(self, repo):
        """El historial del perdedor refleja SU perspectiva (su score, su delta)."""
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        repo.finish_pvp_match(
            match_id=mid,
            winner_id=a,
            score_p1=5,
            score_p2=1,
            elo_delta_p1=12.0,
            elo_delta_p2=-12.0,
            p1_id=a,
            p2_id=b,
        )
        hist_b = repo.get_pvp_history(b)
        assert len(hist_b) == 1
        m = hist_b[0]
        assert m["won"] is False
        assert m["my_score"] == 1  # b es player2 → su score es score_p2
        assert m["opp_score"] == 5
        assert m["elo_delta"] == -12.0
        assert m["opponent"] == "jugador_a"

    def test_finish_updates_current_elo(self, repo):
        """Spec 001: the course's topic rating moves, not users.current_elo (FR-028, FR-029b)."""
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        repo.finish_pvp_match(
            match_id=mid,
            winner_id=a,
            score_p1=3,
            score_p2=0,
            elo_delta_p1=12.0,
            elo_delta_p2=-12.0,
            p1_id=a,
            p2_id=b,
        )
        assert rating_of(repo, a, COURSE, TOPIC) == pytest.approx(1012.0)

    def test_elo_never_negative(self, repo):
        """El rating no baja de 0 aunque el delta sea muy negativo."""
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        repo.finish_pvp_match(
            match_id=mid,
            winner_id=b,
            score_p1=0,
            score_p2=9,
            elo_delta_p1=-99999.0,
            elo_delta_p2=12.0,
            p1_id=a,
            p2_id=b,
        )
        assert rating_of(repo, a, COURSE, TOPIC) == 0.0

    def test_only_finished_matches_in_history(self, repo):
        """Una partida creada pero no terminada NO aparece en el historial."""
        a, b = _two_players(repo)
        repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        assert repo.get_pvp_history(a) == []


class TestCourseBlocks:
    def test_blocks_empty_for_unknown_course(self, repo):
        assert repo.get_course_blocks("__no_existe__") == []


class TestPvpStateSurvivesTheProcess:
    """Regresión del hallazgo P1 #6: el estado de PvP no puede vivir solo en memoria."""

    def test_result_moves_the_canonical_rating_not_just_the_average(self, repo):
        """El delta va a student_topic_elo; si no, la siguiente respuesta lo borra.

        users.current_elo se recalcula como promedio de student_topic_elo, así que
        escribirlo directamente duraba hasta el próximo ejercicio del alumno.
        """
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        repo.finish_pvp_match(
            match_id=mid,
            winner_id=a,
            score_p1=3,
            score_p2=0,
            elo_delta_p1=12.0,
            elo_delta_p2=-12.0,
            p1_id=a,
            p2_id=b,
        )

        assert rating_of(repo, a, COURSE, TOPIC) == 1012.0
        assert rating_of(repo, b, COURSE, TOPIC) == 988.0

    def test_closing_a_match_twice_applies_the_delta_once(self, repo):
        """El cronómetro y el último jugador pueden disparar a la vez."""
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        for _ in range(2):
            repo.finish_pvp_match(
                match_id=mid,
                winner_id=a,
                score_p1=3,
                score_p2=0,
                elo_delta_p1=12.0,
                elo_delta_p2=-12.0,
                p1_id=a,
                p2_id=b,
            )
        assert rating_of(repo, a, COURSE, TOPIC) == 1012.0

    def test_matches_orphaned_by_a_restart_are_closed(self, repo):
        """El cronómetro vive en el proceso: un reinicio deja la fila 'active' para siempre."""
        a, b = _two_players(repo, rated=False)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])

        conn = repo.get_connection()
        conn.execute(
            "UPDATE pvp_matches SET started_at = datetime('now', '-2 hours') WHERE id = ?",
            (mid,),
        )
        conn.commit()
        conn.close()

        assert repo.expire_stale_pvp_matches() == 1

        conn = repo.get_connection()
        status = conn.execute("SELECT status FROM pvp_matches WHERE id = ?", (mid,)).fetchone()[0]
        conn.close()
        assert status == "abandoned"
        # Nadie ganó: el ELO no se toca.
        assert repo.get_course_topic_ratings(a) == []

    def test_a_live_match_is_left_alone(self, repo):
        a, b = _two_players(repo)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        assert repo.expire_stale_pvp_matches() == 0

        conn = repo.get_connection()
        status = conn.execute("SELECT status FROM pvp_matches WHERE id = ?", (mid,)).fetchone()[0]
        conn.close()
        assert status == "active"
