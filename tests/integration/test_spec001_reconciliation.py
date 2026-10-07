"""
Spec 001: one-time, idempotent reconciliation of legacy ratings (task T060; FR-033–FR-036,
FR-034a/b, SC-008; research R10). Both engines.

Fixtures reproduce the real ambiguity: a legacy row is keyed by one name that may be a topic
label, a course id or a course name; a course name can equal a topic label; one topic label can
belong to two courses. Only evidence (attempts recorded under that key on the course's items, or
the course's diagnostic) attributes a legacy row to a course.
"""

from tests.integration.conftest import make_course, make_student, sql

TOPIC = "Fracciones"


def _legacy(repo, user_id, key, elo, rd=350.0, updated_at="2026-01-01 00:00:00"):
    sql(
        repo,
        "INSERT INTO student_topic_elo (user_id, topic, current_elo, rd, updated_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (user_id, key, elo, rd, updated_at),
    )


def _attempt_under(repo, user_id, item_id, key):
    """A historical attempt recorded under the legacy rating key `key`."""
    sql(
        repo,
        "INSERT INTO attempts (user_id, item_id, is_correct, difficulty, topic, elo_after,"
        " elo_before, prob_failure, expected_score, elo_valid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, item_id, True, 1000, key, 1000.0, 1000.0, 0.5, 0.5, 1),
    )


def _new_rows(repo, user_id):
    rows = sql(
        repo,
        "SELECT course_id, topic, current_elo, rd, origin, approximate, legacy_source_key,"
        " reconciled_at FROM student_course_topic_elo WHERE user_id = ? ORDER BY course_id, topic",
        (user_id,),
    )
    return [
        (r[0], r[1], float(r[2]), float(r[3]), r[4], bool(r[5]), r[6], r[7] is not None)
        for r in rows
    ]


def _legacy_rows(repo, user_id):
    rows = sql(
        repo,
        "SELECT topic, current_elo, rd FROM student_topic_elo WHERE user_id = ? ORDER BY topic",
        (user_id,),
    )
    return [tuple(r) for r in rows]


def test_spec001_topic_label_row_reaches_only_the_practised_course(repo, student):
    """FR-034 (a), FR-034a: the topic row seeds (C1, T) — not the same label in C2."""
    c1, items1 = make_course(repo, [TOPIC])
    c2, _ = make_course(repo, [TOPIC])  # the same topic label in another course
    _attempt_under(repo, student, items1[TOPIC][0], TOPIC)
    _legacy(repo, student, TOPIC, 1234.5, rd=200.0)

    repo._reconcile_legacy_ratings()

    assert _new_rows(repo, student) == [
        (c1, TOPIC, 1234.5, 200.0, "legacy_topic_row", True, TOPIC, True)
    ]


def test_spec001_course_name_equal_to_a_topic_label(repo, student):
    """The real ambiguity: course name == topic label; attempts under that key decide."""
    course, items = make_course(repo, ["Geometría"], name="Geometría")
    _attempt_under(repo, student, items["Geometría"][0], "Geometría")
    _legacy(repo, student, "Geometría", 1180.0)

    repo._reconcile_legacy_ratings()

    assert _new_rows(repo, student) == [
        (course, "Geometría", 1180.0, 350.0, "legacy_topic_row", True, "Geometría", True)
    ]


def test_spec001_diagnostic_makes_the_courses_topics_eligible(repo, student):
    """FR-034: the course's diagnostic makes its topics eligible for source (a)."""
    course, _ = make_course(repo, [TOPIC, "Decimales"])
    repo.save_diagnostic(student, course, 1100.0, 50.0, "{}")
    _legacy(repo, student, TOPIC, 1111.0)

    repo._reconcile_legacy_ratings()

    assert _new_rows(repo, student) == [
        (course, TOPIC, 1111.0, 350.0, "legacy_topic_row", True, TOPIC, True)
    ]


def test_spec001_course_row_most_recent_wins_and_is_never_summed(repo):
    """FR-034 (b), FR-035: course-id vs course-name row — most recent, course id on a tie."""
    recent, tie = make_student(repo), make_student(repo)
    for user, name_updated, expected in (
        (recent, "2026-02-01 00:00:00", "name"),
        (tie, "2026-01-01 00:00:00", "id"),
    ):
        course, items = make_course(repo, ["Decimales"], name=f"Curso {user}")
        name = f"Curso {user}"
        _attempt_under(repo, user, items["Decimales"][0], course)  # old flow: key = course id
        _legacy(repo, user, course, 1300.0, updated_at="2026-01-01 00:00:00")
        _legacy(repo, user, name, 1250.0, updated_at=name_updated)

        repo._reconcile_legacy_ratings()

        value, key = (1250.0, name) if expected == "name" else (1300.0, course)
        assert _new_rows(repo, user) == [
            (course, "Decimales", value, 350.0, "legacy_course_row", True, key, True)
        ]


def test_spec001_existing_rows_and_unassigned_legacy_rows_are_left_alone(repo, student):
    """FR-033, FR-034b, FR-036: a stored rating wins; no evidence → nothing created."""
    course, items = make_course(repo, [TOPIC])
    _attempt_under(repo, student, items[TOPIC][0], TOPIC)
    sql(
        repo,
        "INSERT INTO student_course_topic_elo (user_id, course_id, topic, current_elo, rd, origin)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (student, course, TOPIC, 1500.0, 300.0, "practice"),
    )
    _legacy(repo, student, TOPIC, 1100.0)
    _legacy(repo, student, "Sin evidencia", 1700.0)
    legacy_before = _legacy_rows(repo, student)

    repo._reconcile_legacy_ratings()

    assert _new_rows(repo, student) == [
        (course, TOPIC, 1500.0, 300.0, "practice", False, None, False)
    ]
    assert _legacy_rows(repo, student) == legacy_before


def test_spec001_reconciliation_is_idempotent(repo, student):
    """SC-008: a second run creates nothing and changes nothing."""
    course, items = make_course(repo, [TOPIC])
    _attempt_under(repo, student, items[TOPIC][0], TOPIC)
    _legacy(repo, student, TOPIC, 1234.5)

    first = repo._reconcile_legacy_ratings()
    after_first = _new_rows(repo, student)
    second = repo._reconcile_legacy_ratings()

    assert first >= 1
    assert second == 0
    assert _new_rows(repo, student) == after_first
