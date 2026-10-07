"""
Spec 001: the course × topic rating store and its raw reads, on both engines.

[CHANGE] tests (tasks T030, T030a and later story tasks): written before the code they test.
Repositories return raw rows and participants; they never compute a rating (constitution III).
"""

from datetime import datetime, timedelta, timezone

import pytest

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
    repo.set_topic_elo_baseline(student, TOPIC, 1300.0)  # legacy store
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
