"""
Spec 006 delivery C1 (US4; FR-040 … FR-043): the console from the server.

One student set for a teacher — active, non-test students of the teacher's groups, by main group
or enrolment group — in the dashboard, the metrics, the group counts and every export sheet, each
student's data only for the courses that link them to the teacher. The group summary, ranking
(competition ranks, pending last, test students out) and «attention» list come from the server.
Teacher routes are for teachers. The dashboard and metrics count the last 7 days, the last 30 or
the whole history. Both engines.
"""

import io

import openpyxl
import pytest

from tests.integration.conftest import (
    answer,
    enroll,
    headers_for,
    is_postgres,
    make_course,
    make_group,
    make_student,
    make_teacher,
    set_rating,
    sql,
)


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher, headers_for(repo, teacher)


def _student(repo, main_group=None):
    student = make_student(repo)
    if main_group:
        sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (main_group, student))
    return student


def _days_ago(repo, user, days):
    """Move the user's attempts `days` back."""
    if is_postgres(repo):
        sql(
            repo,
            "UPDATE attempts SET timestamp = NOW() - (%s * INTERVAL '1 day') WHERE user_id = %s".replace(
                "%s", "?"
            ),
            (days, user),
        )
    else:
        sql(
            repo,
            "UPDATE attempts SET timestamp = datetime('now', ?) WHERE user_id = ?",
            ("-%d days" % days, user),
        )


def _procedure(repo, user, item):
    sql(
        repo,
        "INSERT INTO procedure_submissions (student_id, item_id, item_content, image_data)"
        " VALUES (?, ?, 'c1', ?)",
        (user, item, b"\x00"),
    )


def _world(repo):
    """Teacher T: group G in course C. Another teacher's group H in course D.
    a: main G, enrolled in C. b: main H, enrolled in C through G and in D through H.
    inactive and tester: main G, enrolled in C — never listed."""
    course_c, items_c = make_course(repo, ["c1_c"], items_per_topic=4)
    course_d, items_d = make_course(repo, ["c1_d"], items_per_topic=2)
    c_items, d_items = items_c["c1_c"], items_d["c1_d"]
    teacher, headers = _teacher(repo)
    other, _ = _teacher(repo)
    group_g = make_group(repo, teacher, course_c)
    group_h = make_group(repo, other, course_d)
    a = _student(repo, group_g)
    enroll(repo, a, course_c, group_g)
    b = _student(repo, group_h)
    enroll(repo, b, course_c, group_g)
    enroll(repo, b, course_d, group_h)
    inactive = _student(repo, group_g)
    enroll(repo, inactive, course_c, group_g)
    tester = _student(repo, group_g)
    enroll(repo, tester, course_c, group_g)
    for user in (a, b, inactive, tester):
        answer(repo, user, c_items[0])
        _procedure(repo, user, c_items[0])
    answer(repo, b, d_items[0])
    _procedure(repo, b, d_items[0])
    sql(repo, "UPDATE users SET active = 0 WHERE id = ?", (inactive,))
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (tester,))
    return {
        "headers": headers,
        "teacher": teacher,
        "course_c": course_c,
        "course_d": course_d,
        "group": group_g,
        "a": a,
        "b": b,
        "c_items": c_items,
    }


def _sheet(client, headers, name):
    book = openpyxl.load_workbook(
        io.BytesIO(client.get("/api/teacher/export/xlsx", headers=headers).content)
    )
    rows = list(book[name].iter_rows(values_only=True))
    if not rows:
        return []
    return [dict(zip(rows[0], r)) for r in rows[1:]]


# ── FR-040: one student set, linked courses only ─────────────────────────────


def test_every_place_lists_the_same_students(repo, client):
    """US4-AS2, FR-040: dashboard, metrics, group counts and every sheet list a and b only."""
    w = _world(repo)
    expected = {w["a"], w["b"]}

    dashboard = client.get("/api/teacher/dashboard?days=all", headers=w["headers"]).json()
    metrics = client.get("/api/teacher/metrics?days=all", headers=w["headers"]).json()
    groups = client.get("/api/teacher/groups", headers=w["headers"]).json()

    assert {s["user_id"] for s in dashboard["students"]} == expected
    assert metrics["total_attempts"] == 2  # one each in C; b's attempt in D is not the teacher's
    assert [g["student_count"] for g in groups if g["group_id"] == w["group"]] == [2]
    attempts = _sheet(client, w["headers"], "Intentos")
    enrolments = _sheet(client, w["headers"], "Matrículas")
    procedures = _sheet(client, w["headers"], "Procedimientos")
    assert {r["student_id"] for r in attempts} == expected and len(attempts) == 2
    assert {(r["student_id"], r["course_id"]) for r in enrolments} == {
        (w["a"], w["course_c"]),
        (w["b"], w["course_c"]),
    }
    assert {r["student_id"] for r in procedures} == expected and len(procedures) == 2


def test_a_moved_student_shows_only_the_shared_course(repo, client):
    """FR-040 (N7): b, moved to another teacher's group, shows only course C and T's group."""
    w = _world(repo)

    dashboard = client.get("/api/teacher/dashboard?days=all", headers=w["headers"]).json()
    [b] = [s for s in dashboard["students"] if s["user_id"] == w["b"]]

    assert b["total_attempts"] == 1
    assert b["group_id"] == w["group"]


# ── FR-041: figures from the server ──────────────────────────────────────────


def test_the_summary_comes_from_the_server(repo, client):
    """US4-AS1, FR-041: competition ranks, pending last, mean, buckets, attention."""
    course, items = make_course(repo, ["c1_rank"], items_per_topic=3)
    teacher, headers = _teacher(repo)
    group = make_group(repo, teacher, course)
    one, two, pending, low = (_student(repo, group) for _ in range(4))
    for user in (one, two, pending, low):
        enroll(repo, user, course, group)
    set_rating(repo, one, course, "c1_rank", 1200.2)
    set_rating(repo, two, course, "c1_rank", 1199.8)
    set_rating(repo, low, course, "c1_rank", 1000.0)
    tester = _student(repo, group)
    enroll(repo, tester, course, group)
    set_rating(repo, tester, course, "c1_rank", 1900.0)
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (tester,))

    summary = client.get("/api/teacher/dashboard", headers=headers).json()["summary"]

    places = {e["user_id"]: e["rank"] for e in summary["ranking"]}
    assert places == {one: 1, two: 1, low: 3, pending: None}
    assert [e["user_id"] for e in summary["ranking"]][-1] == pending
    assert summary["mean"] == round((1200 + 1200 + 1000) / 3)
    assert sum(b["count"] for b in summary["histogram"]) == 3
    assert low in summary["attention"] and one not in summary["attention"]
    groups = summary["groups"]
    assert groups[str(group)]["n"] == 4 and groups[str(group)]["mean"] == summary["mean"]


def test_the_group_ranking_leaves_out_test_students(repo, client):
    """US4-AS1, FR-041: a test student never takes a place."""
    course, _ = make_course(repo, ["c1_rk"])
    teacher, headers = _teacher(repo)
    group = make_group(repo, teacher, course)
    real, tester = _student(repo, group), _student(repo, group)
    for user in (real, tester):
        enroll(repo, user, course, group)
        set_rating(repo, user, course, "c1_rk", 1300.0)
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (tester,))

    ranking = client.get(f"/api/teacher/student/{real}/ranking", headers=headers).json()

    assert [e["user_id"] for e in ranking["ranking"]] == [real]


# ── FR-041a … c: each set ranked on its basis (delivery RV) ──────────────────


def _rated(repo, user, ratings):
    """Seed one topic per course: {course: rating}."""
    for course, (topic, value) in ratings.items():
        set_rating(repo, user, course, topic, value)


def test_a_group_ranks_on_its_course(repo, client):
    """US4-AS5, FR-041a: a course-X group is ranked on course X, not on the overall rating,
    and each place carries the number it was ranked on."""
    x, _ = make_course(repo, ["rv_x"])
    y, _ = make_course(repo, ["rv_y"])
    teacher, headers = _teacher(repo)
    group = make_group(repo, teacher, x)
    a, b = _student(repo, group), _student(repo, group)
    for user in (a, b):
        enroll(repo, user, x, group)
        enroll(repo, user, y)
    _rated(repo, a, {x: ("rv_x", 1300.0), y: ("rv_y", 900.0)})  # overall 1100
    _rated(repo, b, {x: ("rv_x", 1200.0), y: ("rv_y", 1800.0)})  # overall 1500

    figures = client.get("/api/teacher/dashboard", headers=headers).json()["summary"]["groups"][
        str(group)
    ]

    assert [(e["user_id"], e["rank"], e["display_rating"]) for e in figures["ranking"]] == [
        (a, 1, 1300),
        (b, 2, 1200),
    ]
    assert figures["mean"] == 1250
    assert figures["basis"]["kind"] == "course" and figures["basis"]["course_id"] == x


def test_all_groups_rank_on_the_courses_linked_to_the_teacher(repo, client):
    """US4-AS5, FR-041a … c: «Todos» ranks each student on the courses that link them to the
    teacher — the overall rating when a link names no course; a group without a course ranks a
    student it holds only by an enrolment on that course. The rows carry those ratings and no
    other."""
    x, _ = make_course(repo, ["rv_x"])
    y, _ = make_course(repo, ["rv_y"])
    teacher, headers = _teacher(repo)
    other, _ = _teacher(repo)
    group_x = make_group(repo, teacher, x)
    open_group = make_group(repo, teacher)  # no course: the teacher reviews every course
    elsewhere = make_group(repo, other, y)
    # a: enrolled in X through the teacher's group, then joined another teacher's group for Y.
    a = _student(repo)
    enroll(repo, a, x, group_x)
    enroll(repo, a, y, elsewhere)
    _rated(repo, a, {x: ("rv_x", 1200.0), y: ("rv_y", 1800.0)})  # overall 1500
    # c: main group is the teacher's group without a course.
    c = _student(repo, open_group)
    enroll(repo, c, x)
    enroll(repo, c, y)
    _rated(repo, c, {x: ("rv_x", 1000.0), y: ("rv_y", 1600.0)})  # overall 1300
    # d: enrolled in X through the group without a course, main group elsewhere.
    d = _student(repo)
    enroll(repo, d, x, open_group)
    enroll(repo, d, y, elsewhere)
    _rated(repo, d, {x: ("rv_x", 1100.0), y: ("rv_y", 1900.0)})  # overall 1500

    dashboard = client.get("/api/teacher/dashboard", headers=headers).json()
    summary = dashboard["summary"]

    def places(figures):
        return [(e["user_id"], e["rank"], e["display_rating"]) for e in figures["ranking"]]

    assert places(summary) == [(c, 1, 1300), (a, 2, 1200), (d, 3, 1100)]
    assert summary["basis"] == {"kind": "linked_courses"}
    assert places(summary["groups"][str(open_group)]) == [(c, 1, 1300), (d, 2, 1100)]
    assert summary["groups"][str(open_group)]["basis"] == {"kind": "linked_courses"}
    assert places(summary["groups"][str(group_x)]) == [(a, 1, 1200)]
    rows = {s["user_id"]: s for s in dashboard["students"]}
    assert {u: rows[u]["display_rating"] for u in (a, c, d)} == {a: 1200, c: 1300, d: 1100}
    assert (
        rows[a]["rank_label"]
        == next(e for e in summary["ranking"] if e["user_id"] == a)["rank_label"]
    )
    assert not {"global_elo", "overall_status"} & set(rows[a])


# ── FR-042: teacher routes for teachers ──────────────────────────────────────


def test_an_admin_gets_403_on_teacher_routes(repo, client):
    """US4-AS3, FR-042."""
    admin = make_student(repo)
    sql(repo, "UPDATE users SET role = 'admin' WHERE id = ?", (admin,))
    headers = headers_for(repo, admin)
    for path in ("/api/teacher/dashboard", "/api/teacher/groups", "/api/teacher/exam-templates"):
        assert client.get(path, headers=headers).status_code == 403, path


# ── FR-043: the chosen window ────────────────────────────────────────────────


def test_the_dashboard_counts_the_chosen_window(repo, client):
    """US4-AS4, FR-043: attempts 3, 20 and 90 days old; ratings stay current."""
    course, items = make_course(repo, ["c1_w"], items_per_topic=3)
    teacher, headers = _teacher(repo)
    group = make_group(repo, teacher, course)
    students = []
    for days, item in zip((3, 20, 90), items["c1_w"]):
        user = _student(repo, group)
        enroll(repo, user, course, group)
        answer(repo, user, item)
        _days_ago(repo, user, days)
        students.append(user)

    def attempts(days):
        dashboard = client.get(f"/api/teacher/dashboard?days={days}", headers=headers).json()
        metrics = client.get(f"/api/teacher/metrics?days={days}", headers=headers).json()
        per_student = sum(s["total_attempts"] for s in dashboard["students"])
        return per_student, metrics["total_attempts"], len(dashboard["students"])

    assert attempts(7) == (1, 1, 3)
    assert attempts(30) == (2, 2, 3)
    assert attempts("all") == (3, 3, 3)
    default = client.get("/api/teacher/dashboard", headers=headers).json()
    assert sum(s["total_attempts"] for s in default["students"]) == 2  # 30 days by default
    assert client.get("/api/teacher/dashboard?days=12", headers=headers).status_code == 422
