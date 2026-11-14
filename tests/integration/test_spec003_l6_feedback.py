"""
Spec 003 L6 (US7-AS1, US7-AS2; FR-060, FR-061): through the API, a multiple-answer question
tells a partial answer from a wrong one — the key the server answers has its text in the
lesson the same student reads, so the screen needs nothing else. Both engines.
"""

from src.domain.learning import prealgebra
from tests.integration.conftest import enroll, headers_for, make_student, sql

COURSE = "algebra_basica"
ROUTE = list(prealgebra._LESSONS)
NODE = "PREALG-N1-B04-NATURALES-CONTAR"
ABSTRACTION = f"{NODE}-ABSTRACCION"  # right: below_zero, subtraction; wrong: big, zero
INCOMPLETE = "Vas bien: lo que marcaste es correcto, pero falta al menos una opción más."
HAS_WRONG = "Al menos una de las opciones que marcaste no es correcta. Revísalas una por una."


def _student_at(repo, node_id):
    user = make_student(repo)
    enroll(repo, user, COURSE)
    for done in ROUTE[: ROUTE.index(node_id)]:
        sql(
            repo,
            "INSERT INTO lesson_progress (user_id, course_id, node_id, state) "
            "VALUES (?, ?, ?, 'completed')",
            (user, COURSE, done),
        )
    return headers_for(repo, user)


def test_the_lesson_response_carries_the_text_of_the_key_the_server_answers(repo, client):
    """US7-AS1, US7-AS2: answer through `/interactions`, read the text from the lesson."""
    headers = _student_at(repo, NODE)
    lesson = client.get(f"/api/student/lessons/{COURSE}/{NODE}", headers=headers)
    assert lesson.status_code == 200, lesson.text
    feedback = lesson.json()["content"]["feedback"]

    said = {}
    for sent in ("below_zero", "below_zero,big", "below_zero,subtraction"):
        response = client.post(
            f"/api/student/lessons/{COURSE}/{NODE}/interactions",
            headers=headers,
            json={"interaction_id": ABSTRACTION, "selected_option": sent},
        )
        assert response.status_code == 200, response.text
        graded = response.json()
        assert graded["is_expected"] is (sent == "below_zero,subtraction")
        said[sent] = feedback[graded["feedback_key"]]

    assert said == {
        "below_zero": INCOMPLETE,
        "below_zero,big": HAS_WRONG,
        "below_zero,subtraction": feedback["correct"],
    }
    assert feedback["default"] not in said.values()
