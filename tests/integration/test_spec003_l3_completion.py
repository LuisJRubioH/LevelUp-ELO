"""
Spec 003 L3 (US3; FR-030; N1, N2): an eleven-block node completes on right answers.

A node completes only when the latest answer of each required interaction is right; otherwise the
409 names the items still missing, in the order the student sees them. A wrong answer corrected
counts. B01 completes on view, B13 on answers right or wrong, and a node completed before L3 stays
completed. Both engines.
"""

from src.domain.learning import prealgebra
from tests.integration.conftest import enroll, headers_for, make_student, sql

COURSE = "algebra_basica"
ROUTE = list(prealgebra._LESSONS)
NODE = "PREALG-N1-B03-ESCALERA-NECESIDAD"
NEXT = prealgebra._LESSONS[NODE]["next_node_id"]
REQUIRED = [i["interaction_id"] for i in prealgebra._LESSONS[NODE]["interactions"]]


def _right(interaction_id):
    rule = prealgebra._INTERACTION_RULES[interaction_id]
    expected = rule["expected"]
    if isinstance(expected, (set, frozenset, list)):
        return ",".join(sorted(expected))
    return str(expected)


def _wrong(interaction_id):
    rule = prealgebra._INTERACTION_RULES[interaction_id]
    if "valid_options" in rule and rule.get("input_kind") != "multi_select":
        return next(o for o in sorted(rule["valid_options"]) if o != rule["expected"])
    return "999999" if str(rule["expected"]) != "999999" else "1"


def _student_before(repo, node_id):
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


def _answer(client, headers, interaction_id, option, node_id=NODE):
    response = client.post(
        f"/api/student/lessons/{COURSE}/{node_id}/interactions",
        headers=headers,
        json={"interaction_id": interaction_id, "selected_option": option},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _complete(client, headers, node_id=NODE):
    return client.post(
        f"/api/student/lessons/{COURSE}/{node_id}/events",
        headers=headers,
        json={"event": "node_completed"},
    )


def _state(repo, user, node_id=NODE):
    rows = sql(
        repo,
        "SELECT state FROM lesson_progress WHERE user_id = ? AND node_id = ?",
        (user, node_id),
    )
    return rows[0][0] if rows else None


def test_one_wrong_required_answer_refuses_naming_it(repo, client):
    """US3-AS1, FR-030: every item answered, the second practice wrong → 409 naming it."""
    user, headers = _student_before(repo, NODE)
    for interaction_id in REQUIRED:
        option = _wrong(interaction_id) if interaction_id == REQUIRED[1] else _right(interaction_id)
        _answer(client, headers, interaction_id, option)

    response = _complete(client, headers)

    assert response.status_code == 409
    assert response.json()["detail"] == "Te falta acertar: Práctica 2."
    assert _state(repo, user) != "completed"


def test_the_refusal_lists_every_missing_item_in_order(repo, client):
    """FR-030: unanswered and wrong items are both missing; the closing item reads «Cierre»."""
    user, headers = _student_before(repo, NODE)
    for interaction_id in REQUIRED[2:-1]:
        _answer(client, headers, interaction_id, _right(interaction_id))
    _answer(client, headers, REQUIRED[-1], _wrong(REQUIRED[-1]))

    response = _complete(client, headers)

    assert response.status_code == 409
    assert response.json()["detail"] == "Te falta acertar: Práctica 1, Práctica 2 y Cierre."


def test_all_latest_answers_right_completes_and_opens_the_next(repo, client):
    """US3-AS2: every required answer right → completed, and the next node opens."""
    user, headers = _student_before(repo, NODE)
    assert client.get(f"/api/student/lessons/{COURSE}/{NEXT}", headers=headers).status_code == 403
    for interaction_id in REQUIRED:
        _answer(client, headers, interaction_id, _right(interaction_id))

    response = _complete(client, headers)

    assert response.status_code == 200, response.text
    assert response.json()["state"] == "completed"
    assert client.get(f"/api/student/lessons/{COURSE}/{NEXT}", headers=headers).status_code == 200


def test_a_wrong_answer_corrected_lets_the_node_complete(repo, client):
    """US3-AS3: the latest answer counts — wrong, then right, completes."""
    user, headers = _student_before(repo, NODE)
    for interaction_id in REQUIRED:
        _answer(client, headers, interaction_id, _right(interaction_id))
    _answer(client, headers, REQUIRED[0], _wrong(REQUIRED[0]))
    assert _complete(client, headers).status_code == 409
    _answer(client, headers, REQUIRED[0], _right(REQUIRED[0]))

    response = _complete(client, headers)

    assert response.status_code == 200, response.text
    assert _state(repo, user) == "completed"


def test_welcome_completes_on_view_and_closing_on_answers_right_or_wrong(repo, client):
    """N1: B01 completes with no answer. N2: B13 never refuses for a wrong answer."""
    welcome, closing = prealgebra.WELCOME_NODE_ID, prealgebra.CLOSING_NODE_ID
    assert prealgebra._LESSONS[welcome]["completion"] == "view"
    assert prealgebra._LESSONS[closing]["completion"] == "answered"
    user, headers = _student_before(repo, welcome)
    assert _complete(client, headers, welcome).status_code == 200

    user, headers = _student_before(repo, closing)
    for interaction in prealgebra._LESSONS[closing]["interactions"]:
        _answer(
            client,
            headers,
            interaction["interaction_id"],
            _wrong(interaction["interaction_id"]),
            closing,
        )
    response = _complete(client, headers, closing)
    assert response.status_code == 200, response.text
    assert _state(repo, user, closing) == "completed"


def test_a_node_completed_before_l3_stays_completed(repo, client):
    """Edge case: a node completed on answers present stays completed, even with a wrong one."""
    user, headers = _student_before(repo, NODE)
    for interaction_id in REQUIRED:
        _answer(client, headers, interaction_id, _wrong(interaction_id))
    sql(
        repo,
        "INSERT INTO lesson_progress (user_id, course_id, node_id, state) "
        "VALUES (?, ?, ?, 'completed')",
        (user, COURSE, NODE),
    )

    response = _complete(client, headers)

    assert response.status_code == 200, response.text
    assert _state(repo, user) == "completed"
    assert client.get(f"/api/student/lessons/{COURSE}/{NEXT}", headers=headers).status_code == 200
