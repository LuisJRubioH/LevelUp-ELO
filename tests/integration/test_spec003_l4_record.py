"""
Spec 003 L4 (US4; FR-040 … FR-042, FR-006; N11): what the teacher sees.

Every answer to an interaction is kept in order (`lesson_answers`); the post-diagnostic outcome is
stored when the last post-diagnostic item is answered (`lesson_outcomes`); a teacher of one of
the student's groups reads both — right or wrong and the tag, never the value chosen (N11). The
migration that creates the history copies each answer known before L4 once. Both engines.
"""

from src.domain.learning import prealgebra
from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    sql,
)
from tests.integration.test_spec003_l3_completion import _right, _wrong

COURSE = "algebra_basica"
ROUTE = list(prealgebra._LESSONS)
NODE = "PREALG-N1-B03-ESCALERA-NECESIDAD"
CONTENT = prealgebra._LESSONS[NODE]["content"]
PRACTICE_1 = f"{NODE}-{CONTENT['practice'][0]['id']}"
DIAGNOSTIC = [f"{NODE}-{item['id']}" for item in CONTENT["diagnostic"]["items"]]
POST = [f"{NODE}-{item['id']}" for item in CONTENT["post_diagnostic"]["items"]]


def _class(repo):
    """A teacher with a group in the course and one enrolled student at NODE."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, COURSE)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, COURSE, group)
    for done in ROUTE[: ROUTE.index(NODE)]:
        sql(
            repo,
            "INSERT INTO lesson_progress (user_id, course_id, node_id, state) "
            "VALUES (?, ?, ?, 'completed')",
            (student, COURSE, done),
        )
    return headers_for(repo, teacher), student, headers_for(repo, student)


def _answer(client, headers, interaction_id, option):
    response = client.post(
        f"/api/student/lessons/{COURSE}/{NODE}/interactions",
        headers=headers,
        json={"interaction_id": interaction_id, "selected_option": option},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _node_record(client, teacher, student):
    response = client.get(f"/api/teacher/student/{student}/path/{COURSE}", headers=teacher)
    assert response.status_code == 200, response.text
    return next(n for n in response.json()["nodes"] if n["node_id"] == NODE)


def test_wrong_then_right_are_both_kept_in_order(repo, client):
    """US4-AS1, FR-040, FR-042: both answers, in order, right or wrong with the tag."""
    teacher, student, headers = _class(repo)
    wrong = _answer(client, headers, PRACTICE_1, _wrong(PRACTICE_1))
    _answer(client, headers, PRACTICE_1, _right(PRACTICE_1))

    answers = _node_record(client, teacher, student)["answers"]

    assert [(a["label"], a["is_expected"], a["misconception_tag"]) for a in answers] == [
        ("Práctica 1", False, wrong["misconception_tag"]),
        ("Práctica 1", True, None),
    ]
    assert all(a["answered_at"] for a in answers)


def test_post_diagnostic_outcome_is_stored_and_shown_to_the_teacher(repo, client):
    """US4-AS2, FR-041, FR-042: the last post-diagnostic answer stores the outcome."""
    teacher, student, headers = _class(repo)
    for interaction_id in DIAGNOSTIC:
        _answer(client, headers, interaction_id, _wrong(interaction_id))
    for interaction_id in POST[:-1]:
        assert _answer(client, headers, interaction_id, _right(interaction_id))["outcome"] is None
    last = _answer(client, headers, POST[-1], _right(POST[-1]))

    assert last["outcome"] == "gain"
    record = _node_record(client, teacher, student)
    assert record["outcome"] == {
        "diagnostic_correct": 0,
        "post_correct": len(POST),
        "items": len(POST),
        "outcome": "gain",
    }
    lesson = client.get(f"/api/student/lessons/{COURSE}/{NODE}", headers=headers).json()
    assert lesson["progress"]["outcome"]["outcome"] == "gain"


def test_an_outcome_never_reads_worse(repo, client):
    """FR-041: post below the diagnostic is «flat», never «worse» (the browser's rule)."""
    teacher, student, headers = _class(repo)
    for interaction_id in DIAGNOSTIC:
        _answer(client, headers, interaction_id, _right(interaction_id))
    for interaction_id in POST:
        last = _answer(client, headers, interaction_id, _wrong(interaction_id))
    assert last["outcome"] == "flat"
    assert _node_record(client, teacher, student)["outcome"]["outcome"] == "flat"


def test_no_answer_row_holds_free_text(repo, client):
    """US4-AS3, FR-006: every stored value is one the server's grader produced and accepts."""
    _, student, headers = _class(repo)
    for interaction_id in [PRACTICE_1, *DIAGNOSTIC, *POST]:
        _answer(client, headers, interaction_id, _wrong(interaction_id))
        _answer(client, headers, interaction_id, _right(interaction_id))

    rows = sql(
        repo,
        "SELECT node_id, interaction_id, selected_option FROM lesson_answers WHERE user_id = ?",
        (student,),
    )
    assert len(rows) == 2 * (1 + len(DIAGNOSTIC) + len(POST))
    for node_id, interaction_id, stored in rows:
        graded = prealgebra.evaluate_interaction(node_id, interaction_id, stored)
        assert graded is not None and graded["selected_option"] == stored


def test_only_the_students_teacher_reads_the_path(repo, client):
    """FR-042, N11: another teacher and a student are refused; no chosen value is returned."""
    teacher, student, headers = _class(repo)
    _answer(client, headers, PRACTICE_1, _wrong(PRACTICE_1))
    other = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (other,))
    make_group(repo, other, COURSE)
    url = f"/api/teacher/student/{student}/path/{COURSE}"

    assert client.get(url, headers=headers_for(repo, other)).status_code == 404
    assert client.get(url, headers=headers).status_code == 403
    body = client.get(url, headers=teacher)
    assert body.status_code == 200
    assert "selected_option" not in body.text
    no_path = client.get(
        f"/api/teacher/student/{student}/path/calculo_diferencial", headers=teacher
    )
    assert no_path.status_code == 404


def test_the_migration_copies_each_last_answer_once(repo, client):
    """History before L4 starts with the last answer known: copied once, never twice."""
    _, student, headers = _class(repo)
    _answer(client, headers, PRACTICE_1, _wrong(PRACTICE_1))
    _answer(client, headers, DIAGNOSTIC[0], _right(DIAGNOSTIC[0]))
    # A database from before L4: answers in lesson_interactions, no history, older version.
    sql(repo, "DELETE FROM lesson_answers WHERE user_id = ?", (student,))
    for _ in range(2):
        sql(repo, "DELETE FROM schema_versions WHERE version >= 3")
        assert repo._migrate_db()

    rows = sql(
        repo,
        "SELECT interaction_id, is_expected FROM lesson_answers WHERE user_id = ? ORDER BY id",
        (student,),
    )
    assert sorted((r[0], bool(r[1])) for r in rows) == sorted(
        [(PRACTICE_1, False), (DIAGNOSTIC[0], True)]
    )
