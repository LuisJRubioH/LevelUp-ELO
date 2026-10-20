"""
Spec 003 L2 (US2; FR-020, SC-002; N9): grading keys stay on the server.

No lesson response — opening a node, or the node returned after an event — holds a grading key,
for every node of the catalogue. Grading is unchanged: a right and a wrong answer per item kind
give the same response the domain gives. The abstraction question (N9) is graded on the server
and never gates completion. Both engines.
"""

import pytest

from src.domain.learning import prealgebra
from tests.integration.conftest import enroll, headers_for, make_student, make_teacher, sql

COURSE = "algebra_basica"
ROUTE = list(prealgebra._LESSONS)
KEYS = {
    "expected",
    "answer",
    "accepted",
    "misconception_by_option",
    "feedback_by_option",
    "trap_options",
    "feedback_correct",
    "feedback_incorrect",
    "feedback_missing",
    "feedback_trap",
    "misconception_incorrect",
    "misconception_missing",
}
ELEVEN_BLOCK = [
    n
    for n, lesson in prealgebra._LESSONS.items()
    if (lesson.get("content") or {}).get("kind") == "eleven_block_node"
]
NODE = ELEVEN_BLOCK[0]


def _keys_found(value, path=""):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in KEYS or (key == "correct" and not path.endswith(".feedback")):
                found.append(f"{path}.{key}")
            found += _keys_found(child, f"{path}.{key}")
    elif isinstance(value, list):
        for child in value:
            found += _keys_found(child, f"{path}[]")
    return found


def _admin(repo):
    viewer = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1, role = 'admin' WHERE id = ?", (viewer,))
    return headers_for(repo, viewer)


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
    return user, headers_for(repo, user)


def test_no_lesson_response_holds_a_grading_key(repo, client):
    """US2-AS1, FR-020, SC-002: every node of the catalogue, and the node an event returns."""
    headers = _admin(repo)
    leaks = {}
    for node_id in ROUTE:
        response = client.get(f"/api/student/lessons/{COURSE}/{node_id}", headers=headers)
        assert response.status_code == 200, (node_id, response.text)
        found = _keys_found(response.json().get("content") or {})
        if found:
            leaks[node_id] = found[:3]
    assert leaks == {}

    _, student = _student_at(repo, NODE)
    event = client.post(
        f"/api/student/lessons/{COURSE}/{NODE}/events",
        headers=student,
        json={"event": "node_viewed"},
    )
    assert event.status_code == 200
    assert _keys_found(event.json()["content"]) == []


def _sample_answers():
    """One item per kind in the catalogue, with a right and a wrong answer."""
    samples = {}
    for node_id in ELEVEN_BLOCK:
        for interaction in prealgebra._LESSONS[node_id]["interactions"]:
            rule = prealgebra._INTERACTION_RULES[interaction["interaction_id"]]
            kind = rule.get("input_kind", "single_select")
            if kind in samples:
                continue
            expected = rule["expected"]
            if kind == "multi_select":
                right = ",".join(sorted(expected))
                wrong = sorted(rule["valid_options"])[0]
                if {wrong} == expected:
                    wrong = ",".join(sorted(rule["valid_options"]))
            elif kind == "single_select":
                right = expected
                wrong = next(o for o in sorted(rule["valid_options"]) if o != expected)
            elif kind == "text_exact":
                right, wrong = expected, "9999" if expected != "9999" else "1"
            else:
                right, wrong = str(expected), "999999" if str(expected) != "999999" else "1"
            samples[kind] = (node_id, interaction["interaction_id"], right, wrong)
    return samples


SAMPLES = _sample_answers()


@pytest.mark.parametrize("kind", sorted(SAMPLES))
def test_feedback_is_unchanged_after_the_keys_leave(repo, client, kind):
    """US2-AS2: the server's grade is the domain's, right and wrong, for every item kind."""
    node_id, interaction_id, right, wrong = SAMPLES[kind]
    _, headers = _student_at(repo, node_id)
    for option in (wrong, right):
        response = client.post(
            f"/api/student/lessons/{COURSE}/{node_id}/interactions",
            headers=headers,
            json={"interaction_id": interaction_id, "selected_option": option},
        )
        assert response.status_code == 200, response.text
        graded = {k: v for k, v in response.json().items() if k != "outcome"}  # L4's field
        assert graded == prealgebra.evaluate_interaction(node_id, interaction_id, option)
    assert response.json()["is_expected"] is True


def test_the_abstraction_question_is_graded_on_the_server_and_never_gates(repo, client):
    """N9: the abstraction question is an interaction graded by the server, `required=False`."""
    lesson = prealgebra._LESSONS[NODE]
    interaction_id = f"{NODE}-ABSTRACCION"
    right = ",".join(
        sorted(
            o["id"] for o in lesson["content"]["abstraction_question"]["options"] if o["correct"]
        )
    )
    assert interaction_id not in {i["interaction_id"] for i in lesson["interactions"]}
    _, headers = _student_at(repo, NODE)

    graded = client.post(
        f"/api/student/lessons/{COURSE}/{NODE}/interactions",
        headers=headers,
        json={"interaction_id": interaction_id, "selected_option": right},
    )

    assert graded.status_code == 200, graded.text
    assert graded.json()["is_expected"] is True
    assert graded.json()["feedback_key"] == "correct"
