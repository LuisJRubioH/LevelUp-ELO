"""
tests/integration/test_pvp_repository.py
=========================================
Pruebas de integración de los métodos PvP de los repositorios, en ambos motores (survey 007 V15;
el fixture `repo` de conftest corre cada prueba en SQLite y en PostgreSQL):
create_pvp_match → save_pvp_answer → finish_pvp_match → get_pvp_history.
También cubre get_course_blocks.

PostgreSQL persiste entre pruebas: los jugadores tienen nombres únicos y las pruebas de
abandono cierran primero las partidas huérfanas que dejaron corridas anteriores.
"""

import pytest

from tests.integration.conftest import is_postgres, make_student, rating_of, set_rating, sql

COURSE, TOPIC = "calculo_diferencial", "Límites"


def _two_players(repo, rated=True):
    """Registra dos estudiantes y retorna (id1, id2).

    Spec 001 (FR-029b/c): a match moves every rated topic of its course, so each player gets
    one rated topic (COURSE, TOPIC) = 1000 unless `rated=False`.
    """
    a, b = make_student(repo, "universidad"), make_student(repo, "universidad")
    if rated:
        set_rating(repo, a, COURSE, TOPIC, 1000.0)
        set_rating(repo, b, COURSE, TOPIC, 1000.0)
    return a, b


def _username(repo, user_id):
    return sql(repo, "SELECT username FROM users WHERE id = ?", (user_id,))[0][0]


def _status(repo, match_id):
    return sql(repo, "SELECT status FROM pvp_matches WHERE id = ?", (match_id,))[0][0]


def _started_ago(repo, match_id, seconds):
    """Moves the match's start `seconds` into the past, in each engine's clock."""
    if is_postgres(repo):
        statement = (
            "UPDATE pvp_matches SET started_at = NOW() - make_interval(secs => ?) WHERE id = ?"
        )
        sql(repo, statement, (seconds, match_id))
    else:
        sql(
            repo,
            "UPDATE pvp_matches SET started_at = datetime('now', ?) WHERE id = ?",
            ("-%d seconds" % seconds, match_id),
        )


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
        assert m["opponent"] == _username(repo, b)

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
        assert m["opponent"] == _username(repo, a)

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
        repo.expire_stale_pvp_matches()  # orphans left by earlier runs (PostgreSQL persists)
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        _started_ago(repo, mid, 2 * 3600)

        assert repo.expire_stale_pvp_matches() == 1

        assert _status(repo, mid) == "abandoned"
        # Nadie ganó: el ELO no se toca.
        assert repo.get_course_topic_ratings(a) == []

    def test_a_live_match_is_left_alone(self, repo):
        a, b = _two_players(repo)
        repo.expire_stale_pvp_matches()
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        assert repo.expire_stale_pvp_matches() == 0

        assert _status(repo, mid) == "active"

    @pytest.mark.parametrize("age_seconds,expired", [(590, 0), (610, 1)])
    def test_spec001_abandonment_starts_after_600_seconds(self, repo, age_seconds, expired):
        """FR-027 boundary (spec 001, T070): only matches active for more than 600 s close."""
        a, b = _two_players(repo, rated=False)
        repo.expire_stale_pvp_matches()
        mid = repo.create_pvp_match("calculo_diferencial", a, b, ["i1"])
        _started_ago(repo, mid, age_seconds)

        assert repo.expire_stale_pvp_matches() == expired
        assert _status(repo, mid) == ("abandoned" if expired else "active")


def test_spec007_finish_with_a_reason_keeps_no_rated_topics(repo):
    """Spec 007 F (FR-042, O-F3): a forfeit is an ordinary finished close whose reason is
    `forfeit` where the delta was applied; a player with no rated topic keeps `no_rated_topics`;
    closing twice changes nothing."""
    a, b = make_student(repo, "universidad"), make_student(repo, "universidad")
    set_rating(repo, a, COURSE, TOPIC, 1000.0)  # b has no rated topic in the course
    mid = repo.create_pvp_match(COURSE, a, b, ["i1"])
    close = dict(
        match_id=mid, winner_id=a, score_p1=1, score_p2=3,
        elo_delta_p1=12.0, elo_delta_p2=-12.0, p1_id=a, p2_id=b, reason="forfeit",
    )  # fmt: skip

    applied = repo.finish_pvp_match(**close)

    assert applied == {"p1": (12.0, "forfeit"), "p2": (0.0, "no_rated_topics")}
    row = sql(
        repo,
        "SELECT status, winner_id, elo_reason_p1, elo_reason_p2 FROM pvp_matches WHERE id = ?",
        (mid,),
    )[0]
    assert tuple(row) == ("finished", a, "forfeit", "no_rated_topics")
    assert rating_of(repo, a, COURSE, TOPIC) == 1012.0

    assert repo.finish_pvp_match(**close) is None
    assert rating_of(repo, a, COURSE, TOPIC) == 1012.0


# ── Spec 007 delivery M (FR-031, FR-032): raw reads and the unrated close ───


def _ago(repo, hours):
    """A moment `hours` before now in the form each engine stores CURRENT_TIMESTAMP (UTC)."""
    from datetime import datetime, timedelta, timezone

    moment = datetime.now(timezone.utc) - timedelta(hours=hours)
    return moment if is_postgres(repo) else moment.strftime("%Y-%m-%d %H:%M:%S")


def _since(hours):
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone.utc) - timedelta(hours=hours)


def test_spec007_pair_matches_since_returns_raw_rows(repo):
    """FR-031 (O-M5): the pair's matches finished since `since`, in either seat order, as raw
    rows — the abandoned and the unrated ones too (the domain decides what counts); not the
    still active, the earlier ones, nor a match with someone else."""
    a, b = _two_players(repo)
    other = make_student(repo, "universidad")
    close = dict(winner_id=None, score_p1=1, score_p2=1, elo_delta_p1=0.0, elo_delta_p2=0.0)

    rated = repo.create_pvp_match(COURSE, a, b, ["i1"])
    repo.finish_pvp_match(match_id=rated, p1_id=a, p2_id=b, **close)
    reversed_seats = repo.create_pvp_match(COURSE, b, a, ["i1"])
    repo.finish_pvp_match(match_id=reversed_seats, p1_id=b, p2_id=a, reason="forfeit", **close)
    abandoned = repo.create_pvp_match(COURSE, a, b, ["i1"])
    repo.abandon_pvp_match(abandoned, "not_saved")
    old = repo.create_pvp_match(COURSE, a, b, ["i1"])
    repo.finish_pvp_match(match_id=old, p1_id=a, p2_id=b, **close)
    sql(repo, "UPDATE pvp_matches SET finished_at = ? WHERE id = ?", (_ago(repo, 30), old))
    repo.create_pvp_match(COURSE, a, b, ["i1"])  # active
    with_other = repo.create_pvp_match(COURSE, a, other, ["i1"])
    repo.finish_pvp_match(match_id=with_other, p1_id=a, p2_id=other, **close)

    rows = repo.get_pvp_pair_matches_since(b, a, _since(24))

    by_id = {row["id"]: row for row in rows}
    assert set(by_id) == {rated, reversed_seats, abandoned}
    assert (by_id[rated]["status"], by_id[rated]["elo_reason_p1"]) == ("finished", None)
    assert by_id[reversed_seats]["elo_reason_p2"] == "forfeit"
    assert (by_id[abandoned]["status"], by_id[abandoned]["elo_reason_p1"]) == (
        "abandoned", "not_saved",
    )  # fmt: skip
    assert all(row["finished_at"] is not None for row in rows)


def test_spec007_items_seen_since_reads_practice_exams_and_league(repo):
    """FR-032 (O-M9): an item is seen when, since `since`, either player answered it in practice
    or in an exam, or was served it in a League match of the course; older reads, other courses'
    items and other students' reads do not count."""
    from tests.integration.conftest import make_course

    course_id, items = make_course(repo, [TOPIC], items_per_topic=7)
    other_course, other_items = make_course(repo, [TOPIC], items_per_topic=1)
    practised, examined, served, old, by_stranger, unseen, _ = items[TOPIC]
    a, b = _two_players(repo, rated=False)
    stranger = make_student(repo, "universidad")

    def attempt(user, item, hours=1):
        sql(
            repo,
            "INSERT INTO attempts (user_id, item_id, is_correct, timestamp) VALUES (?, ?, ?, ?)",
            (user, item, True if is_postgres(repo) else 1, _ago(repo, hours)),
        )

    attempt(a, practised)
    attempt(a, old, hours=8 * 24)
    attempt(stranger, by_stranger)
    attempt(a, other_items[TOPIC][0])
    sql(
        repo,
        "INSERT INTO exam_responses (session_id, user_id, item_id, topic, is_correct)"
        " VALUES (?, ?, ?, ?, ?)",
        (0, b, examined, TOPIC, 1),
    )
    repo.create_pvp_match(course_id, stranger, b, [served])
    repo.create_pvp_match(other_course, a, b, [unseen])  # another course's match

    seen = set(repo.get_item_ids_seen_since([a, b], course_id, _since(7 * 24)))

    assert seen == {practised, examined, served}


def test_spec007_finish_unrated_moves_no_rating(repo):
    """FR-031 (O-M5): an over-cap close is finished — winner and scores kept — with both deltas
    0 and both reasons `daily_cap`, and touches no rating; closing twice changes nothing."""
    a, b = _two_players(repo)
    mid = repo.create_pvp_match(COURSE, a, b, ["i1"])
    close = dict(
        match_id=mid, winner_id=a, score_p1=4, score_p2=2,
        elo_delta_p1=12.0, elo_delta_p2=-12.0, p1_id=a, p2_id=b,
        reason="daily_cap", rated=False,
    )  # fmt: skip

    assert repo.finish_pvp_match(**close) == {"p1": (0.0, "daily_cap"), "p2": (0.0, "daily_cap")}

    row = sql(
        repo,
        "SELECT status, winner_id, score_p1, score_p2, elo_delta_p1, elo_delta_p2,"
        " elo_reason_p1, elo_reason_p2 FROM pvp_matches WHERE id = ?",
        (mid,),
    )[0]
    assert tuple(row) == ("finished", a, 4, 2, 0.0, 0.0, "daily_cap", "daily_cap")
    assert rating_of(repo, a, COURSE, TOPIC) == 1000.0
    assert rating_of(repo, b, COURSE, TOPIC) == 1000.0
    assert repo.finish_pvp_match(**close) is None
    assert rating_of(repo, a, COURSE, TOPIC) == 1000.0


def test_spec007_league_entry_profile_returns_raw_fields(repo):
    """Spec 007 G1 (FR-021): the League's entry read returns the account's `is_test_user` as
    stored; the institution is None until delivery G2 reads the main group's (FR-022). An
    unknown account is None."""
    real, tester = make_student(repo, "universidad"), make_student(repo, "universidad")
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (tester,))

    assert repo.get_league_entry_profile(real) == {"is_test_user": 0, "institution": None}
    assert repo.get_league_entry_profile(tester) == {"is_test_user": 1, "institution": None}
    assert repo.get_league_entry_profile(-1) is None
