"""
Spec 001, block 5 (FR-020a–c, FR-031a, US3-AS5–AS8): the diagnostic result shows one figure, the
student's current course rating read through RatingReadService, with its rank label; it keeps the
diagnostic's per-topic breakdown with no rating figure per topic, marks each topic as initialized
or kept, and summarises the outcome for the message. On both engines.

[CHANGE] tests: written before the code they test.
"""

import json

from src.domain.elo.ranks import rating_display

from tests.integration.conftest import (
    answer,
    enroll,
    headers_for,
    make_course,
    rating_of,
    set_rating,
)

TOPICS = ["Fracciones", "Decimales"]


def _submit(client, repo, student, course, answers):
    response = client.post(
        f"/api/student/diagnostic/{course}/submit",
        headers=headers_for(repo, student),
        json={"answers": [{"item_id": i, "selected_option": o} for i, o in answers]},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _status(client, repo, student, course):
    response = client.get(f"/api/student/diagnostic/{course}", headers=headers_for(repo, student))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["completed"] is True
    return body["result"]


def _themes(result):
    return {t["topic"]: t for t in result["themes"]}


def _current(repo, student, course):
    """The course rating as RatingReadService reads it, displayed (FR-028j)."""
    from src.application.services.rating_read_service import RatingReadService

    return {
        **rating_display(RatingReadService(repo).course_rating_of(student, course)),
        "status": "rated",
    }


def _assert_one_figure(result):
    """FR-020b: the breakdown carries no rating figure per topic."""
    for theme in result["themes"]:
        assert "current_rating" not in theme
        assert set(theme) >= {"topic", "correct", "total", "status", "outcome"}


def test_spec001_first_diagnostic_is_all_initialized(repo, student, client):
    """US3-AS5, FR-020a, FR-020b, FR-020c, FR-031a: no practice yet → every topic initialized;
    the one figure and its rank label are the current course rating."""
    course, items = make_course(repo, TOPICS, difficulty=1200.0)
    enroll(repo, student, course)

    result = _submit(
        client,
        repo,
        student,
        course,
        [(items["Fracciones"][0], "A"), (items["Decimales"][0], "B")],
    )

    assert result["course_rating"] == _current(repo, student, course)
    assert result["outcome_summary"] == "initialized"
    assert {t: v["outcome"] for t, v in _themes(result).items()} == {
        "Fracciones": "initialized",
        "Decimales": "initialized",
    }
    themes = _themes(result)
    assert (themes["Fracciones"]["correct"], themes["Fracciones"]["total"]) == (1, 1)
    assert (themes["Decimales"]["correct"], themes["Decimales"]["total"]) == (0, 1)
    _assert_one_figure(result)


def test_spec001_retaken_diagnostic_keeps_a_practised_topic_mixed(repo, student, client):
    """US3-AS6, FR-020a, FR-020c, FR-021: a practised topic (1058.16) failed in a retake is kept and
    its rating unchanged, the other is initialized, and the figure is the current course rating."""
    course, items = make_course(repo, TOPICS, difficulty=1200.0)
    enroll(repo, student, course)
    set_rating(repo, student, course, "Fracciones", 1058.16, origin="practice")
    answer(repo, student, items["Fracciones"][0])  # practice exists, so FR-021 protects it
    practised = rating_of(repo, student, course, "Fracciones")

    result = _submit(
        client,
        repo,
        student,
        course,
        [(items["Fracciones"][0], "B"), (items["Decimales"][0], "A")],
    )

    assert rating_of(repo, student, course, "Fracciones") == practised
    themes = _themes(result)
    assert themes["Fracciones"]["outcome"] == "kept"
    assert themes["Decimales"]["outcome"] == "initialized"
    assert result["outcome_summary"] == "mixed"
    assert result["course_rating"] == _current(repo, student, course)
    assert result["course_rating"]["display_rating"] != round(result["initial_elo"])
    _assert_one_figure(result)


def test_spec001_retaken_diagnostic_with_every_topic_practised_keeps_all(repo, student, client):
    """US3-AS8, FR-020c, FR-021: practice in every topic → all kept, no rating moves."""
    course, items = make_course(repo, TOPICS, difficulty=1200.0)
    enroll(repo, student, course)
    for topic in TOPICS:
        set_rating(repo, student, course, topic, 1100.0, origin="practice")
        answer(repo, student, items[topic][0])
    before = {topic: rating_of(repo, student, course, topic) for topic in TOPICS}

    result = _submit(
        client,
        repo,
        student,
        course,
        [(items["Fracciones"][0], "B"), (items["Decimales"][0], "B")],
    )

    assert {topic: rating_of(repo, student, course, topic) for topic in TOPICS} == before
    assert result["outcome_summary"] == "kept"
    assert {v["outcome"] for v in result["themes"]} == {"kept"}
    assert result["course_rating"] == _current(repo, student, course)


def test_spec001_returning_to_the_course_shows_the_current_rating(repo, student, client):
    """US3-AS7, FR-020a, FR-020b: after practice, the stored result is shown with today's course
    rating and with that diagnostic's breakdown, marks and outcome unchanged."""
    course, items = make_course(repo, TOPICS, difficulty=1200.0, items_per_topic=2)
    enroll(repo, student, course)
    submitted = _submit(
        client,
        repo,
        student,
        course,
        [(items["Fracciones"][0], "A"), (items["Decimales"][0], "A")],
    )
    answer(repo, student, items["Fracciones"][1], correct=False)

    shown = _status(client, repo, student, course)

    assert shown["course_rating"] == _current(repo, student, course)
    assert shown["course_rating"] != submitted["course_rating"]
    assert shown["outcome_summary"] == submitted["outcome_summary"] == "initialized"
    for topic in TOPICS:
        for key in ("correct", "total", "status", "outcome"):
            assert _themes(shown)[topic][key] == _themes(submitted)[topic][key]
    _assert_one_figure(shown)


def test_spec001_a_result_stored_before_block_5_has_no_mark(repo, student, client):
    """Edge case (FR-020c): a stored result without marks shows the current rating, no mark and
    no outcome."""
    course, items = make_course(repo, TOPICS, difficulty=1200.0)
    enroll(repo, student, course)
    set_rating(repo, student, course, "Fracciones", 1100.0)
    old = {
        "themes": [
            {
                "topic": "Fracciones",
                "correct": 1,
                "total": 1,
                "ratio": 1.0,
                "status": "strong",
                "elo": 1022.0,
            }
        ],
        "league": {"name": "Plata", "rank": "II", "color": "#c0c0c0"},
        "correct_total": 1,
        "answered": 1,
    }
    repo.save_diagnostic(student, course, 1022.0, 100.0, json.dumps(old))

    shown = _status(client, repo, student, course)

    assert _themes(shown)["Fracciones"]["outcome"] is None
    assert shown["outcome_summary"] is None
    assert shown["course_rating"]["display_rating"] == 1100
