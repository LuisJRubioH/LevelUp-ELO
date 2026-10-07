"""
Spec 001 behaviour changes through the HTTP API (SQLite, tests/api).

[CHANGE] tests: each was written before its implementation task and failed first.
"""

from tests.api.test_spec001_answer_pins import _answer, _item, _student
from tests.integration.conftest import sql

# ── T035: FR-009, FR-008 — an invalid attempt reports no change ─────────────


def test_spec001_invalid_time_reports_and_records_no_change(api_client):
    repo, user_id, headers = _student(api_client)
    _, (item,) = _item(repo)

    response = api_client.post(
        "/api/student/answer",
        headers=headers,
        json={"item_id": item["id"], "selected_option": "A", "time_taken": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["elo_valid"] is False
    assert body["delta_elo"] == 0
    assert body["elo_after"] == body["elo_before"]
    stored = sql(repo, "SELECT elo_before, elo_after FROM attempts WHERE user_id = ?", (user_id,))
    assert [(float(b), float(a)) for b, a in stored] == [(body["elo_before"], body["elo_before"])]


def test_spec001_valid_answer_reports_elo_valid(api_client):
    repo, _, headers = _student(api_client)
    _, (item,) = _item(repo)

    body = _answer(api_client, headers, item).json()

    assert body["elo_valid"] is True
    assert body["elo_after"] == 1016.0


# ── US6 fixtures: real students, teacher and group on the API's SQLite ──────

import pytest  # noqa: E402

from tests.integration.conftest import (  # noqa: E402
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    set_rating,
)


def _repo(api_client):
    from api.dependencies import get_repository

    return get_repository()


def _teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _classroom(repo, ratings):
    """A teacher's group on course C; `ratings` = {name: {topic: elo}} for students in it."""
    teacher = _teacher(repo)
    course, items = make_course(repo, ["a", "b"])
    group = make_group(repo, teacher, course)
    students = {}
    for name, topics in ratings.items():
        students[name] = make_student(repo)
        enroll(repo, students[name], course, group)
        for topic, elo in topics.items():
            set_rating(repo, students[name], course, topic, elo)
    return teacher, course, items, group, students


def _get(api_client, repo, user_id, path):
    response = api_client.get(path, headers=headers_for(repo, user_id))
    assert response.status_code == 200, response.text
    return response.json()


# ── T054: FR-028a/b/c, US6-AS1, US6-AS5, US6-AS6 ────────────────────────────


def test_spec001_stats_overall_is_the_mean_of_current_courses(api_client):
    repo = _repo(api_client)
    student = make_student(repo)
    x, _ = make_course(repo, ["a", "b"])
    y, _ = make_course(repo, ["a"])
    for course in (x, y):
        enroll(repo, student, course)
    set_rating(repo, student, x, "a", 1100.0)
    set_rating(repo, student, x, "b", 1300.0)
    set_rating(repo, student, y, "a", 1000.0)

    body = _get(api_client, repo, student, "/api/student/stats")

    assert (body["global_elo"], body["display_rating"], body["rank_label"]) == (
        1100.0,
        1100,
        "Oro II",
    )
    assert body["overall_status"] == "rated"
    by_id = {c["course_id"]: c for c in body["course_ratings"]}
    assert (by_id[x]["rating"], by_id[x]["display_rating"], by_id[x]["rank_label"]) == (
        1200.0,
        1200,
        "Oro I",
    )
    assert by_id[x]["current_context"] is True


def test_spec001_promoted_student_is_pending_and_keeps_history(api_client):
    repo = _repo(api_client)
    student = make_student(repo, education_level="semillero", grade="7")
    g6, _ = make_course(repo, ["a"], block="Semillero", id_suffix="_semillero_6")
    g7, _ = make_course(repo, ["a"], block="Semillero", id_suffix="_semillero_7")
    for course in (g6, g7):
        enroll(repo, student, course)
    set_rating(repo, student, g6, "a", 1300.0)

    body = _get(api_client, repo, student, "/api/student/stats")

    assert (body["global_elo"], body["display_rating"], body["rank_label"]) == (None, None, None)
    assert body["overall_status"] == "pending_diagnostic"
    by_id = {c["course_id"]: c for c in body["course_ratings"]}
    assert (by_id[g6]["rating"], by_id[g6]["current_context"]) == (1300.0, False)
    assert (by_id[g7]["rating"], by_id[g7]["display_rating"], by_id[g7]["current_context"]) == (
        None,
        None,
        True,
    )
    assert not [k for k in body if "delta" in k or "change" in k]  # FR-028c


# ── T058: FR-031, FR-028j, US6-AS3, US6-AS9 ─────────────────────────────────


def test_spec001_meta_ranks_is_public_and_ascending(api_client):
    response = api_client.get("/api/meta/ranks")

    assert response.status_code == 200
    ranks = response.json()
    assert len(ranks) == 16
    assert [r["min"] for r in ranks] == sorted(r["min"] for r in ranks)
    assert (ranks[0]["label"], ranks[-1]["label"]) == ("Aspirante", "Leyenda Suprema")


@pytest.mark.parametrize("stored,shown,label", [(999.6, 1000, "Plata I"), (999.4, 999, "Plata II")])
def test_spec001_number_and_label_agree_on_every_surface(api_client, stored, shown, label):
    repo = _repo(api_client)
    teacher, course, _, _, students = _classroom(repo, {"s": {"a": stored}})
    student = students["s"]

    stats = _get(api_client, repo, student, "/api/student/stats")
    dashboard = _get(api_client, repo, teacher, "/api/teacher/dashboard")
    report = _get(api_client, repo, teacher, f"/api/teacher/student/{student}")
    ranking = _get(api_client, repo, student, "/api/student/group-ranking")

    entry = next(s for s in dashboard["students"] if s["user_id"] == student)
    mine = next(r for r in ranking["ranking"] if r["user_id"] == student)
    assert (stats["display_rating"], stats["rank_label"]) == (shown, label)
    assert (entry["display_rating"], entry["rank_label"]) == (shown, label)
    assert (report["display_rating"], report["rank_label"]) == (shown, label)
    assert (mine["rating"], mine["rank_label"]) == (shown, label)
    assert rating_of(repo, student, course, "a") == stored


# ── T059: FR-030, US6-AS2 — the preview is the change the engine applies ────


@pytest.mark.parametrize("correct", [True, False])
def test_spec001_preview_equals_the_applied_change(api_client, correct):
    repo = _repo(api_client)
    student = make_student(repo)
    course, items = make_course(repo, ["a"], difficulty=1100.0)
    enroll(repo, student, course)
    set_rating(repo, student, course, "a", 1050.0, rd=200.0)
    headers = headers_for(repo, student)

    question = api_client.post(
        "/api/student/next-question", headers=headers, json={"course_id": course}
    ).json()
    response = api_client.post(
        "/api/student/answer",
        headers=headers,
        json={
            "item_id": question["item"]["id"],
            "selected_option": "A" if correct else "B",
            "time_taken": 20,
        },
    ).json()

    expected = question["preview"]["on_correct" if correct else "on_wrong"]
    assert response["delta_elo"] == pytest.approx(expected, abs=0.1)


# ── T056 (API half): FR-028d, US6-AS7 — basis, errors, pending ──────────────


def test_spec001_group_ranking_basis_errors_and_pending(api_client):
    repo = _repo(api_client)
    teacher, course, _, group, s = _classroom(
        repo, {"A": {"a": 1200.0}, "B": {"a": 1100.0}, "D": {}}
    )
    other, _ = make_course(repo, ["a"])
    for name in ("B", "D"):
        enroll(repo, s[name], other)
    set_rating(repo, s["B"], other, "a", 1900.0)
    set_rating(repo, s["D"], other, "a", 1000.0)
    a_id = s["A"]

    by_group = _get(api_client, repo, s["D"], "/api/student/group-ranking")
    requested = _get(api_client, repo, s["B"], f"/api/student/group-ranking?course_id={other}")
    teacher_view = _get(api_client, repo, teacher, f"/api/teacher/student/{a_id}/ranking")

    assert (by_group["basis"]["course_id"], by_group["basis"]["source"]) == (course, "group")
    assert [(r["user_id"], r["rank"], r["status"]) for r in by_group["ranking"]] == [
        (s["A"], 1, "rated"),
        (s["B"], 2, "rated"),
        (s["D"], None, "pending_diagnostic"),
    ]
    assert by_group["my_rank"] is None
    assert (requested["basis"]["course_id"], requested["basis"]["source"]) == (other, "requested")
    assert [(r["user_id"], r["rating"], r["rank"]) for r in requested["ranking"]] == [
        (s["B"], 1900, 1),
        (s["D"], 1000, 2),
        (s["A"], None, None),
    ]
    assert teacher_view["basis"]["source"] == "group"
    assert [r["user_id"] for r in teacher_view["ranking"]] == [s["A"], s["B"], s["D"]]
    headers = headers_for(repo, a_id)
    unknown = api_client.get("/api/student/group-ranking?course_id=no_such_course", headers=headers)
    not_enrolled = api_client.get(f"/api/student/group-ranking?course_id={other}", headers=headers)
    assert (unknown.status_code, not_enrolled.status_code) == (400, 403)


# ── T055 (API half): FR-028, FR-036, SC-005 — every surface reads one rating ──


def test_spec001_every_surface_reads_the_canonical_rating(api_client, monkeypatch):
    from src.application.services.rating_read_service import RatingReadService
    import src.infrastructure.external_api.ai_client as ai_client

    repo = _repo(api_client)
    teacher, course, items, _, s = _classroom(repo, {"s": {"a": 1234.4, "b": 1100.0}})
    student = s["s"]
    # Legacy state edited by hand must not change any read (FR-036, research R4).
    sql(
        repo,
        "INSERT INTO student_topic_elo (user_id, topic, current_elo, rd) VALUES (?, ?, ?, ?)",
        (student, "a", 1900.0, 350.0),
    )
    sql(repo, "UPDATE users SET current_elo = 1900 WHERE id = ?", (student,))
    view = RatingReadService(repo).ratings_view(student)
    shown = view["display_rating"]

    stats = _get(api_client, repo, student, "/api/student/stats")
    dashboard = _get(api_client, repo, teacher, "/api/teacher/dashboard")
    report = _get(api_client, repo, teacher, f"/api/teacher/student/{student}")
    ranking = _get(api_client, repo, student, "/api/student/group-ranking")
    captured = {}

    def fake_guidance(rating, *args, **kwargs):
        captured["rating"] = rating
        return "ok"

    monkeypatch.setattr(ai_client, "get_socratic_guidance", fake_guidance)
    api_client.post(
        "/api/ai/socratic",
        headers=headers_for(repo, student),
        json={
            "item_id": items["a"][0],
            "item_content": "x",
            "student_message": "ayuda",
            "course_id": course,
            "api_key": "sk-test",
        },
    )
    start = api_client.post(
        "/api/student/exam/start",
        headers=headers_for(repo, student),
        json={"course_id": course, "n_questions": 2},
    ).json()
    exam = api_client.post(
        "/api/student/exam/submit",
        headers=headers_for(repo, student),
        json={
            "session_id": start["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in start["items"]],
        },
    ).json()

    assert view["overall"] == pytest.approx(1167.2)
    assert stats["display_rating"] == shown
    entry = next(x for x in dashboard["students"] if x["user_id"] == student)
    assert entry["display_rating"] == shown
    assert report["display_rating"] == shown
    assert next(r for r in ranking["ranking"] if r["user_id"] == student)["rating"] == shown
    assert captured["rating"] == pytest.approx(view["overall"])
    assert exam["global_elo_after"] == pytest.approx(view["overall"], abs=0.01)


def test_spec001_course_map_shows_unrated_topics_as_pending(api_client):
    """FR-029a (T064, T070): a topic without a rating comes back null — never the 1000 start —
    and is not counted as mastered; a rated topic keeps its value."""
    repo = _repo(api_client)
    student = make_student(repo)
    course, _ = make_course(repo, ["a", "b", "c", "d", "e"])
    enroll(repo, student, course)
    set_rating(repo, student, course, "a", 1234.5)

    body = _get(api_client, repo, student, f"/api/student/map/{course}")

    by_topic = {n["topic"]: n for n in body["nodes"]}
    assert by_topic["a"]["elo"] == 1234.5
    assert (by_topic["b"]["elo"], by_topic["b"]["rd"]) == (None, None)
    assert by_topic["b"]["state"] != "completed"
