"""
Spec 001: the course × topic rating store and its raw reads, on both engines.

[CHANGE] tests (tasks T030, T030a and later story tasks): written before the code they test.
Repositories return raw rows and participants; they never compute a rating (constitution III).
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.domain.elo.model import rating_delta

from tests.integration.conftest import (
    answer,
    enroll,
    make_course,
    make_group,
    make_student,
    make_teacher,
    sql,
)

TOPIC = "Fracciones"


def _row(repo, user_id, course_id, topic, elo, rd=350.0, origin="practice", approximate=False):
    sql(
        repo,
        "INSERT INTO student_course_topic_elo"
        " (user_id, course_id, topic, current_elo, rd, origin, approximate)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, course_id, topic, elo, rd, origin, approximate),
    )


def _course(repo, block="Colegio", id_suffix=""):
    course_id, items = make_course(repo, [TOPIC], block=block, id_suffix=id_suffix)
    return course_id, items[TOPIC][0]


def _age_attempts(repo, user_id, days):
    old = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    sql(repo, "UPDATE attempts SET timestamp = ? WHERE user_id = ?", (old, user_id))


def _ids(participants):
    return {p["user_id"]: p["attempts_in_window"] for p in participants}


# ── T030: raw rating rows ───────────────────────────────────────────────────


def test_spec001_course_topic_ratings_are_new_table_rows_only(repo, student):
    """FR-028, FR-029: legacy rows never appear; origin and approximate come back."""
    c1, _ = _course(repo)
    c2, _ = _course(repo)
    sql(
        repo,
        "INSERT INTO student_topic_elo (user_id, topic, current_elo, rd)" " VALUES (?, ?, ?, ?)",
        (student, TOPIC, 1300.0, 350.0),
    )  # legacy store
    _row(repo, student, c1, TOPIC, 1100.25, rd=300.0)
    _row(repo, student, c2, TOPIC, 900.0, origin="legacy_topic_row", approximate=True)

    rows = sorted(repo.get_course_topic_ratings(student), key=lambda r: r["course_id"])
    only_c1 = repo.get_course_topic_ratings(student, course_id=c1)

    expected = sorted(
        [
            {
                "course_id": c1,
                "topic": TOPIC,
                "elo": 1100.25,
                "rd": 300.0,
                "origin": "practice",
                "approximate": False,
            },
            {
                "course_id": c2,
                "topic": TOPIC,
                "elo": 900.0,
                "rd": 350.0,
                "origin": "legacy_topic_row",
                "approximate": True,
            },
        ],
        key=lambda r: r["course_id"],
    )
    assert rows == expected
    assert only_c1 == [r for r in expected if r["course_id"] == c1]


def test_spec001_course_topic_ratings_bulk(repo):
    a, b = make_student(repo), make_student(repo)
    c1, _ = _course(repo)
    c2, _ = _course(repo)
    _row(repo, a, c1, TOPIC, 1010.0)
    _row(repo, b, c1, TOPIC, 990.0)
    _row(repo, b, c2, TOPIC, 1200.0)

    rows = repo.get_course_topic_ratings_bulk([a, b], course_id=c1)

    assert sorted((r["user_id"], r["course_id"], r["elo"]) for r in rows) == sorted(
        [(a, c1, 1010.0), (b, c1, 990.0)]
    )
    assert len(repo.get_course_topic_ratings_bulk([a, b])) == 3
    assert repo.get_course_topic_ratings_bulk([]) == []


# ── T030: current-context courses (FR-028a) ─────────────────────────────────


@pytest.mark.parametrize(
    "level,grade,current,other",
    [
        # Semillero courses all have block 'Semillero'; the grade is the id suffix.
        ("semillero", "6", ("Semillero", "_semillero_6"), ("Semillero", "_semillero_7")),
        ("colegio", None, ("Colegio", ""), ("Universidad", "")),
        ("universidad", None, ("Universidad", ""), ("Colegio", "")),
        ("concursos", None, ("Concursos", ""), ("Universidad", "")),
    ],
)
def test_spec001_current_context_is_enrollments_in_the_users_catalogue(
    repo, level, grade, current, other
):
    user = make_student(repo, education_level=level, grade=grade)
    not_enrolled, _ = _course(repo, *current)
    current, _ = _course(repo, *current)
    other, _ = _course(repo, *other)
    enroll(repo, user, current)
    enroll(repo, user, other)

    assert repo.get_current_context_course_ids(user) == [current]
    assert repo.get_current_context_course_ids_bulk([user]) == {user: [current]}
    assert not_enrolled not in repo.get_current_context_course_ids(user)


# ── T030: ranking participants (FR-028f) ────────────────────────────────────


def test_spec001_global_participants_are_active_this_week(repo):
    active = make_student(repo, education_level="semillero", grade="6")
    inactive = make_student(repo, education_level="semillero", grade="6")
    other_level = make_student(repo, education_level="colegio")
    _, item = _course(repo)
    for user in (active, inactive, other_level):
        answer(repo, user, item)
    _age_attempts(repo, inactive, days=10)

    everyone = _ids(repo.get_ranking_participants("global"))
    semillero_6 = _ids(
        repo.get_ranking_participants("global", education_level="semillero", grade="6")
    )

    assert everyone[active] == 1 and everyone[other_level] == 1
    assert inactive not in everyone
    assert active in semillero_6 and other_level not in semillero_6


def test_spec001_course_participants_count_only_that_course(repo):
    both, only_other = make_student(repo), make_student(repo)
    course, item = _course(repo)
    _, other_item = _course(repo)
    answer(repo, both, item)
    answer(repo, both, other_item)
    answer(repo, only_other, other_item)

    participants = _ids(repo.get_ranking_participants("course", course_id=course))

    assert participants.get(both) == 1
    assert only_other not in participants


def test_spec001_group_and_weekly_participants(repo):
    course, item = _course(repo)
    _, other_item = _course(repo)
    group = make_group(repo, make_teacher(repo), course)
    active, idle, outsider = make_student(repo), make_student(repo), make_student(repo)
    for user in (active, idle):
        enroll(repo, user, course, group)
    answer(repo, active, item)
    answer(repo, active, other_item)
    answer(repo, outsider, item)

    group_rows = repo.get_ranking_participants("group", group_id=group)
    weekly = _ids(repo.get_ranking_participants("weekly", group_id=group))
    weekly_course = _ids(repo.get_ranking_participants("weekly", group_id=group, course_id=course))

    assert _ids(group_rows) == {active: 0, idle: 0}
    assert all(set(r) == {"user_id", "username", "attempts_in_window"} for r in group_rows)
    assert weekly == {active: 2}
    assert weekly_course == {active: 1}


def test_spec001_group_course_id(repo):
    teacher = make_teacher(repo)
    course, _ = _course(repo)

    assert repo.get_group_course_id(make_group(repo, teacher, course)) == course
    assert repo.get_group_course_id(make_group(repo, teacher)) is None


# ── T030a: storage precision and display agree on both engines ─────────────


@pytest.mark.parametrize(
    "stored,shown,label", [(999.4999999, 999, "Plata II"), (999.6, 1000, "Plata I")]
)
def test_spec001_stored_precision_and_display_agree_on_both_engines(repo, stored, shown, label):
    """FR-028i, FR-028j, research R20: no engine turns 999.4999999 into 999.5 (→ 1000)."""
    from src.application.services.rating_read_service import RatingReadService

    student = make_student(repo, education_level="colegio")
    course, _ = _course(repo)
    enroll(repo, student, course)
    _row(repo, student, course, TOPIC, stored)

    assert [r["elo"] for r in repo.get_course_topic_ratings(student, course_id=course)] == [stored]
    view = RatingReadService(repo).ratings_view(student)
    entry = next(c for c in view["courses"] if c["course_id"] == course)
    assert (entry["display_rating"], entry["rank_label"]) == (shown, label)
    assert (view["display_rating"], view["rank_label"]) == (shown, label)


# ── T034: an answer writes only its item's course and topic (FR-029) ────────


@pytest.mark.parametrize("correct,expected", [(True, 1016.0), (False, 984.0)])
def test_spec001_answer_writes_only_the_items_course_topic(repo, student, correct, expected):
    """US1-AS1/AS2: (C, T) gets 1016/984 with origin 'practice'; the legacy store, the users
    column and the same topic label in another course C' stay untouched."""
    course, item = _course(repo)
    other, _ = _course(repo)
    _row(repo, student, other, TOPIC, 1200.0)
    current_before = sql(repo, "SELECT current_elo FROM users WHERE id = ?", (student,))[0][0]

    answer(repo, student, item, correct=correct)

    rows = sql(
        repo,
        "SELECT course_id, topic, current_elo, origin FROM student_course_topic_elo"
        " WHERE user_id = ? ORDER BY course_id",
        (student,),
    )
    assert sorted(tuple(r) for r in rows) == sorted(
        [(course, TOPIC, expected, "practice"), (other, TOPIC, 1200.0, "practice")]
    )
    assert sql(repo, "SELECT COUNT(*) FROM student_topic_elo WHERE user_id = ?", (student,)) == [
        (0,)
    ]
    current_after = sql(repo, "SELECT current_elo FROM users WHERE id = ?", (student,))[0][0]
    assert current_after == current_before


# ── T035a: an explicit 0 s is invalid, an absent time is 30 s (FR-008a) ─────


@pytest.mark.parametrize("seconds,moves", [(0, False), (0.0, False), (None, True)])
def test_spec001_explicit_zero_seconds_is_invalid(repo, student, seconds, moves):
    course, item = _course(repo)

    answer(repo, student, item, correct=True, seconds=seconds)

    stored = sql(
        repo,
        "SELECT current_elo FROM student_course_topic_elo WHERE user_id = ? AND course_id = ?",
        (student, course),
    )
    assert [r[0] for r in stored] == ([1016.0] if moves else [])
    assert float(repo.get_item_by_id(item)["difficulty"]) == (984.0 if moves else 1000.0)
    recorded = sql(repo, "SELECT elo_valid FROM attempts WHERE user_id = ?", (student,))
    assert [int(r[0]) for r in recorded] == [1 if moves else 0]


# ── T046: the diagnostic writes (user, C, T) rows (FR-029, FR-021) ──────────


def test_spec001_diagnostic_writes_course_topic_baselines(repo, student, client):
    """US3: baselines land on the diagnosed course's topics with origin 'diagnostic'; a topic
    already practised in C keeps its rating; the same label in another course is untouched."""
    from tests.integration.conftest import headers_for

    course, items = make_course(repo, [TOPIC, "Decimales"], difficulty=1200.0)
    other, _ = _course(repo)
    _row(repo, student, other, TOPIC, 1200.0)
    answer(repo, student, items["Decimales"][0])  # practised before the diagnostic

    response = client.post(
        f"/api/student/diagnostic/{course}/submit",
        headers=headers_for(repo, student),
        json={
            "answers": [
                {"item_id": items[TOPIC][0], "selected_option": "A"},
                {"item_id": items["Decimales"][0], "selected_option": "B"},
            ]
        },
    )

    assert response.status_code == 200
    rows = sql(
        repo,
        "SELECT course_id, topic, current_elo, origin FROM student_course_topic_elo"
        " WHERE user_id = ?",
        (student,),
    )
    assert sorted(tuple(r) for r in rows) == sorted(
        [
            (course, TOPIC, 1022.0, "diagnostic"),
            (course, "Decimales", 1000.0 + rating_delta(1000.0, 350.0, 1200.0, 1.0), "practice"),
            (other, TOPIC, 1200.0, "practice"),
        ]
    )


# ── T048: a teacher's grade adds to the item's (course, topic) once (FR-029, US4-AS1) ──


def _pending_submission(repo, student, item_id):
    return sql(
        repo,
        "INSERT INTO procedure_submissions (student_id, item_id, item_content, image_data, status)"
        " VALUES (?, ?, ?, ?, 'pending') RETURNING id",
        (student, item_id, "spec001 procedure", b"spec001 image"),
    )[0][0]


def _store(repo, user_id):
    rows = sql(
        repo,
        "SELECT course_id, topic, current_elo, origin FROM student_course_topic_elo"
        " WHERE user_id = ?",
        (user_id,),
    )
    return sorted(tuple(r) for r in rows)


def test_spec001_procedure_grade_bumps_the_items_course_topic_once(repo, student):
    course, item = _course(repo)
    other, _ = _course(repo)
    _row(repo, student, course, TOPIC, 1100.0)
    _row(repo, student, other, TOPIC, 1200.0)
    submission = _pending_submission(repo, student, item)

    assert repo.validate_procedure_submission(submission, teacher_score=80.0)
    assert not repo.validate_procedure_submission(submission, teacher_score=80.0)

    assert _store(repo, student) == sorted(
        [(course, TOPIC, 1106.0, "practice"), (other, TOPIC, 1200.0, "practice")]
    )
    assert sql(repo, "SELECT COUNT(*) FROM student_topic_elo WHERE user_id = ?", (student,)) == [
        (0,)
    ]


def test_spec001_procedure_grade_creates_an_absent_row_and_floors_at_zero(repo, student):
    course, item = _course(repo)
    low, low_item = _course(repo)
    _row(repo, student, low, TOPIC, 3.0)

    assert repo.validate_procedure_submission(
        _pending_submission(repo, student, item), teacher_score=80.0
    )
    assert repo.validate_procedure_submission(
        _pending_submission(repo, student, low_item), teacher_score=0.0
    )

    assert _store(repo, student) == sorted(
        [(course, TOPIC, 1006.0, "procedure"), (low, TOPIC, 0.0, "practice")]
    )


# ── T050: a PvP result reaches every rated topic of the course, once (FR-029b/c) ──


def _finish(repo, match, p1, p2, d1, d2, winner):
    return repo.finish_pvp_match(
        match_id=match,
        winner_id=winner,
        score_p1=3,
        score_p2=0,
        elo_delta_p1=d1,
        elo_delta_p2=d2,
        p1_id=p1,
        p2_id=p2,
    )


def test_spec001_pvp_delta_reaches_every_rated_topic_once(repo):
    """US5-AS5: +12 to each rated topic, so the course rating moves by exactly 12."""
    from src.application.services.rating_read_service import RatingReadService

    a, b = make_student(repo), make_student(repo)
    course, items = make_course(repo, [TOPIC, "Decimales", "Porcentajes"])
    _row(repo, a, course, TOPIC, 1100.0)
    _row(repo, a, course, "Decimales", 1300.0)
    _row(repo, b, course, TOPIC, 1000.0)
    match = repo.create_pvp_match(course, a, b, [items[TOPIC][0]])

    applied = _finish(repo, match, a, b, 12.0, -12.0, a)
    again = _finish(repo, match, a, b, 12.0, -12.0, a)

    assert applied == {"p1": (12.0, None), "p2": (-12.0, None)}
    assert again is None
    assert _store(repo, a) == sorted(
        [(course, TOPIC, 1112.0, "practice"), (course, "Decimales", 1312.0, "practice")]
    )
    assert _store(repo, b) == [(course, TOPIC, 988.0, "practice")]
    assert RatingReadService(repo).course_rating_of(a, course) == 1212.0


def test_spec001_pvp_player_without_rated_topics_gets_zero(repo):
    """FR-029c: no rated topic → applied 0, reason no_rated_topics; the opponent applies."""
    a, b = make_student(repo), make_student(repo)
    course, items = make_course(repo, [TOPIC])
    other, _ = _course(repo)
    _row(repo, a, course, TOPIC, 1100.0)
    _row(repo, b, other, TOPIC, 1500.0)
    match = repo.create_pvp_match(course, a, b, [items[TOPIC][0]])

    applied = _finish(repo, match, a, b, -12.0, 12.0, b)

    assert applied == {"p1": (-12.0, None), "p2": (0.0, "no_rated_topics")}
    assert _store(repo, a) == [(course, TOPIC, 1088.0, "practice")]
    assert _store(repo, b) == [(other, TOPIC, 1500.0, "practice")]
    stored = sql(
        repo,
        "SELECT elo_delta_p1, elo_reason_p1, elo_delta_p2, elo_reason_p2 FROM pvp_matches"
        " WHERE id = ?",
        (match,),
    )[0]
    assert (float(stored[0]), stored[1], float(stored[2]), stored[3]) == (
        -12.0,
        None,
        0.0,
        "no_rated_topics",
    )
