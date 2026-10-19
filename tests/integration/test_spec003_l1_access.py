"""
Spec 003 delivery L1 (US1; FR-010, FR-011; N6, N10): who may walk, and who may only look at, a
course's learning path.

The five path endpoints — the lesson, its events, its answers, the path summary and the map —
answer an enrolled student as before, refuse a student who is not enrolled (403, nothing stored),
let a teacher with a group in the course (or an admin) read every node without storing anything,
and refuse any other teacher. Both engines.
"""

import pytest

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    sql,
)

COURSE = "algebra_basica"
WELCOME = "PREALG-N1-B01-BIENVENIDA"
TRIGGER = "PREALG-N1-B02-PREGUNTA-DETONADORA"
FIRST_N2 = "PREALG-N2-E01-SUMA-JUNTAR"  # deep in the path: locked for a new student
NOT_ENROLLED = "No estás inscrito en este curso."


def _approved_teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _rows(repo, user_id):
    progress = sql(repo, "SELECT COUNT(*) FROM lesson_progress WHERE user_id = ?", (user_id,))
    answers = sql(repo, "SELECT COUNT(*) FROM lesson_interactions WHERE user_id = ?", (user_id,))
    return progress[0][0] + answers[0][0]


def _calls(client, headers, node=WELCOME):
    base = f"/api/student/lessons/{COURSE}/{node}"
    return {
        "lesson": client.get(base, headers=headers),
        "event": client.post(f"{base}/events", headers=headers, json={"event": "node_viewed"}),
        "answer": client.post(
            f"/api/student/lessons/{COURSE}/{TRIGGER}/interactions",
            headers=headers,
            json={"interaction_id": "PREALG-N1-B02-Q01", "selected_option": "yes"},
        ),
        "summary": client.get(f"/api/student/prealgebra-summary/{COURSE}", headers=headers),
        "map": client.get(f"/api/student/map/{COURSE}", headers=headers),
    }


def test_a_student_not_enrolled_is_refused_everywhere(repo, client):
    """US1-AS1, FR-010, SC-001: every path endpoint answers 403 and nothing is stored."""
    student = make_student(repo)
    responses = _calls(client, headers_for(repo, student))

    for name, response in responses.items():
        assert response.status_code == 403, (name, response.text)
        assert response.json()["detail"] == NOT_ENROLLED, name
    assert _rows(repo, student) == 0


def test_an_enrolled_student_walks_the_path_as_today(repo, client):
    """US1-AS2: the same calls work for a student enrolled in the course."""
    student = make_student(repo)
    enroll(repo, student, COURSE)
    headers = headers_for(repo, student)

    welcome = client.get(f"/api/student/lessons/{COURSE}/{WELCOME}", headers=headers)
    assert welcome.status_code == 200
    assert welcome.json()["preview"] is False
    done = client.post(
        f"/api/student/lessons/{COURSE}/{WELCOME}/events",
        headers=headers,
        json={"event": "node_completed"},
    )
    assert done.status_code == 200 and done.json()["state"] == "completed"
    answered = client.post(
        f"/api/student/lessons/{COURSE}/{TRIGGER}/interactions",
        headers=headers,
        json={"interaction_id": "PREALG-N1-B02-Q01", "selected_option": "yes"},
    )
    assert answered.status_code == 200
    assert (
        client.get(f"/api/student/prealgebra-summary/{COURSE}", headers=headers).status_code == 200
    )
    course_map = client.get(f"/api/student/map/{COURSE}", headers=headers)
    assert course_map.status_code == 200 and course_map.json()["preview"] is False
    assert (
        client.get(f"/api/student/lessons/{COURSE}/{FIRST_N2}", headers=headers).status_code == 403
    )


@pytest.mark.parametrize("role", ["teacher", "admin"])
def test_a_teacher_of_the_course_previews_without_storing(repo, client, role):
    """US1-AS3, FR-011, N10: every node opens, read only; events and answers are refused and
    nothing is stored. An admin previews like a teacher of every course."""
    if role == "teacher":
        viewer = _approved_teacher(repo)
        make_group(repo, viewer, COURSE)
    else:
        viewer = sql(repo, "SELECT id FROM users WHERE role = 'admin' LIMIT 1")[0][0]
    headers = headers_for(repo, viewer)

    for node in (WELCOME, FIRST_N2):
        lesson = client.get(f"/api/student/lessons/{COURSE}/{node}", headers=headers)
        assert lesson.status_code == 200, (node, lesson.text)
        assert lesson.json()["preview"] is True
        assert lesson.json()["state"] == "available"

    course_map = client.get(f"/api/student/map/{COURSE}", headers=headers)
    assert course_map.status_code == 200
    body = course_map.json()
    assert body["preview"] is True
    assert body["nodes"] and all(n["state"] == "available" for n in body["nodes"])

    responses = _calls(client, headers)
    for name in ("event", "answer", "summary"):
        assert responses[name].status_code == 403, (name, responses[name].text)
    assert _rows(repo, viewer) == 0


def test_a_teacher_without_a_group_in_the_course_is_refused(repo, client):
    """US1-AS4, FR-011: a teacher whose groups are in other courses reads nothing."""
    teacher = _approved_teacher(repo)
    make_group(repo, teacher, "calculo_diferencial")
    responses = _calls(client, headers_for(repo, teacher))

    for name, response in responses.items():
        assert response.status_code == 403, (name, response.text)
    assert _rows(repo, teacher) == 0


def test_the_summary_has_a_response_model_and_checks_the_course(repo, client):
    """N6: the summary is declared in the API's schema, and a course without a path is 404."""
    from api.main import app

    student = make_student(repo)
    enroll(repo, student, COURSE)
    enroll(repo, student, "calculo_diferencial")
    headers = headers_for(repo, student)

    operation = app.openapi()["paths"]["/api/student/prealgebra-summary/{course_id}"]["get"]
    assert "$ref" in str(operation["responses"]["200"]), "no response model"
    no_path = client.get("/api/student/prealgebra-summary/calculo_diferencial", headers=headers)
    assert no_path.status_code == 404
