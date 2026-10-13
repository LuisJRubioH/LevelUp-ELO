"""
Spec 001, block 5 (FR-020a–c, US3-AS5–AS7): the diagnostic result shows the student's current
ratings — the course's and each diagnosed topic's — and marks each topic as initialized by the
diagnostic or kept because it already had practice. On both engines.

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


def _course_display(repo, student, course):
    from src.application.services.rating_read_service import RatingReadService

    return rating_display(RatingReadService(repo).course_rating_of(student, course))


def test_spec001_first_diagnostic_shows_current_ratings_all_initialized(repo, student, client):
    """US3-AS5, FR-020a, FR-020b, FR-020c: no practice yet → every topic initialized; the course
    and each topic show the stored ratings as the backend displays them."""
    course, items = make_course(repo, TOPICS, difficulty=1200.0)
    enroll(repo, student, course)

    result = _submit(
        client,
        repo,
        student,
        course,
        [(items["Fracciones"][0], "A"), (items["Decimales"][0], "B")],
    )

    assert result["course_rating"] == {
        **_course_display(repo, student, course),
        "status": "rated",
    }
    themes = _themes(result)
    for topic in TOPICS:
        assert themes[topic]["outcome"] == "initialized"
        stored = rating_of(repo, student, course, topic)
        assert themes[topic]["current_rating"] == rating_display(stored)["display_rating"]
    # The diagnostic's own breakdown stays (FR-020b).
    assert (themes["Fracciones"]["correct"], themes["Fracciones"]["total"]) == (1, 1)
    assert (themes["Decimales"]["correct"], themes["Decimales"]["total"]) == (0, 1)


def test_spec001_retaken_diagnostic_keeps_a_practised_topic_and_shows_it(repo, student, client):
    """US3-AS6, FR-020a, FR-020c: a practised topic (1058.16) failed in a retake is shown as kept
    with 1058, and the course rating shown is the current one, not the diagnostic's values."""
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

    themes = _themes(result)
    assert rating_of(repo, student, course, "Fracciones") == practised
    assert themes["Fracciones"]["outcome"] == "kept"
    assert themes["Fracciones"]["current_rating"] == rating_display(practised)["display_rating"]
    assert themes["Decimales"]["outcome"] == "initialized"
    shown = _course_display(repo, student, course)
    assert result["course_rating"]["display_rating"] == shown["display_rating"]
    assert result["course_rating"]["rank_label"] == shown["rank_label"]


def test_spec001_returning_to_the_course_shows_current_ratings(repo, student, client):
    """US3-AS7, FR-020a, FR-020b: after practice, the stored result is shown with today's ratings
    and with that diagnostic's breakdown and marks unchanged."""
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

    now = rating_of(repo, student, course, "Fracciones")
    themes = _themes(shown)
    assert themes["Fracciones"]["current_rating"] == rating_display(now)["display_rating"]
    assert (
        themes["Fracciones"]["current_rating"] != _themes(submitted)["Fracciones"]["current_rating"]
    )
    assert shown["course_rating"]["display_rating"] == (
        _course_display(repo, student, course)["display_rating"]
    )
    for topic in TOPICS:
        for key in ("correct", "total", "status", "outcome"):
            assert themes[topic][key] == _themes(submitted)[topic][key]


def test_spec001_a_result_stored_before_block_5_has_no_mark(repo, student, client):
    """Edge case (FR-020c): a stored result without marks shows current ratings and no mark."""
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

    theme = _themes(shown)["Fracciones"]
    assert theme["outcome"] is None
    assert theme["current_rating"] == 1100
    assert shown["course_rating"]["display_rating"] == 1100
