"""
Spec 006 deliveries AB1 and AB2 (US8; FR-060 … FR-063): the open question.

A template's teacher writes open questions with a reference solution; a student starts the
template and gets the statements, never the reference; the typed answers are kept with the session
under a code, a blank one too, and move no rating; a started template's open questions cannot
change and a duplicate carries them. After the submission the AI is asked for four levels per
non-empty answer, with the code and never a name; a blank answer is 0 without a call; with no key
or an unreadable reply the answer waits for the teacher. Both engines.
"""

import json

import pytest

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    sql,
)

OPEN = [
    {
        "statement": "Demuestra que la suma de dos pares es par.",
        "reference_solution": "2a+2b=2(a+b)",
    },
    {"statement": "¿Cuántos divisores tiene 36? Justifica.", "reference_solution": "9: 2^2·3^2"},
]
LEVELS = {"comprension": 3, "estrategia": 2, "ejecucion": 2, "justificacion": 1}


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


@pytest.fixture
def no_ai_key(monkeypatch):
    from api.config import settings

    for name in ("system_ai_api_key", "ai_key_teacher_analysis"):
        monkeypatch.setattr(settings, name, "")


@pytest.fixture
def ai(monkeypatch):
    """A provider stub: records every prompt and answers with `ai.reply`."""
    from api.config import settings

    monkeypatch.setattr(settings, "system_ai_api_key", "gsk_test_only")
    monkeypatch.setattr(settings, "ai_key_teacher_analysis", "")

    class Stub:
        reply = json.dumps({**LEVELS, "comentario": "Buen planteamiento."})
        prompts: list = []

    def fake_call(prompt, *args, **kwargs):
        Stub.prompts.append(prompt)
        return Stub.reply

    monkeypatch.setattr("src.infrastructure.external_api.ai_client._call_ai_api", fake_call)
    Stub.prompts = []
    return Stub


def _class(repo, client, open_questions=OPEN):
    course, items = make_course(repo, ["ab_a", "ab_b"])
    item_ids = [ids[0] for ids in items.values()]
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, course, group)
    teacher_headers = headers_for(repo, teacher)
    created = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={
            "course_id": course,
            "title": "AB",
            "time_limit_min": 30,
            "item_ids": item_ids,
            "open_questions": open_questions,
        },
    )
    assert created.status_code == 201, created.text
    template = created.json()
    assigned = client.post(
        f"/api/teacher/exam-templates/{template['id']}/assignments",
        headers=teacher_headers,
        json={"group_ids": [group], "starts_at": None, "ends_at": None},
    )
    assert assigned.status_code in (200, 201), assigned.text
    return {
        "course": course,
        "template": template,
        "student": student,
        "headers": headers_for(repo, student),
        "teacher_headers": teacher_headers,
    }


def _start(client, c):
    response = client.post(
        "/api/student/exam/start",
        headers=c["headers"],
        json={"course_id": c["course"], "template_id": c["template"]["id"]},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _submit(client, c, exam, texts):
    return client.post(
        "/api/student/exam/submit",
        headers=c["headers"],
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
            "open_answers": [
                {"question_id": q["id"], "text": t} for q, t in zip(exam["open_questions"], texts)
            ],
        },
    )


def _answers(repo, user_id):
    return sql(
        repo,
        "SELECT id, question_id, answer_text, ai_status, ai_levels, ai_feedback"
        " FROM exam_open_answers WHERE user_id = ? ORDER BY id",
        (user_id,),
    )


def _ratings(repo, user_id):
    return sql(
        repo,
        "SELECT course_id, topic, current_elo FROM student_course_topic_elo WHERE user_id = ?"
        " ORDER BY course_id, topic",
        (user_id,),
    )


# ── AB1 ──────────────────────────────────────────────────────────────────────


def test_the_teacher_writes_open_questions(repo, client):
    """FR-060: the template keeps its open questions, in order, with the reference solution."""
    c = _class(repo, client)
    got = client.get("/api/teacher/exam-templates", headers=c["teacher_headers"]).json()
    template = next(t for t in got if t["id"] == c["template"]["id"])

    assert [q["statement"] for q in template["open_questions"]] == [q["statement"] for q in OPEN]
    assert [q["reference_solution"] for q in template["open_questions"]] == [
        q["reference_solution"] for q in OPEN
    ]


def test_a_student_gets_the_statements_never_the_reference(repo, client, no_ai_key):
    """US8-AS1, FR-061: start and resume carry the statements in order, no reference solution."""
    c = _class(repo, client)
    exam = _start(client, c)
    again = _start(client, c)

    for got in (exam, again):
        assert [q["statement"] for q in got["open_questions"]] == [q["statement"] for q in OPEN]
        assert "2(a+b)" not in json.dumps(got) and "reference" not in json.dumps(got)
    assert again["resumed"] is True
    assert [q["id"] for q in again["open_questions"]] == [q["id"] for q in exam["open_questions"]]


def test_typed_answers_are_kept_under_a_code_and_move_no_rating(repo, client, no_ai_key):
    """US8-AS2, FR-062: one answer per question, a blank one too; no rating moves; the response
    counts the answers awaiting review."""
    c = _class(repo, client)
    before = _ratings(repo, c["student"])
    exam = _start(client, c)

    submitted = _submit(client, c, exam, ["2a + 2b = 2(a + b), que es par.", "   "])

    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["open_pending"] == 2
    rows = _answers(repo, c["student"])
    assert [r[1] for r in rows] == [q["id"] for q in exam["open_questions"]]
    assert rows[0][2] == "2a + 2b = 2(a + b), que es par."
    assert rows[1][2].strip() == ""
    assert _ratings(repo, c["student"]) == before


def test_an_answer_to_a_question_not_in_the_template_is_refused(repo, client, no_ai_key):
    """FR-062: 400, nothing kept."""
    c = _class(repo, client)
    exam = _start(client, c)

    response = client.post(
        "/api/student/exam/submit",
        headers=c["headers"],
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
            "open_answers": [{"question_id": 999999, "text": "x"}],
        },
    )

    assert response.status_code == 400, response.text
    assert _answers(repo, c["student"]) == []


def test_an_answer_longer_than_the_limit_is_refused(repo, client, no_ai_key):
    """FR-062: up to 4,000 characters."""
    c = _class(repo, client)
    exam = _start(client, c)

    response = _submit(client, c, exam, ["x" * 4001, ""])

    assert response.status_code == 422


def test_a_started_templates_open_questions_are_locked(repo, client, no_ai_key):
    """US8-AS3, FR-060: 409 once a student started it; a duplicate carries the questions."""
    c = _class(repo, client)
    _start(client, c)
    template_id = c["template"]["id"]

    edited = client.patch(
        f"/api/teacher/exam-templates/{template_id}",
        headers=c["teacher_headers"],
        json={"open_questions": [{"statement": "Otra", "reference_solution": ""}]},
    )
    copy = client.post(
        f"/api/teacher/exam-templates/{template_id}/duplicate", headers=c["teacher_headers"]
    )

    assert edited.status_code == 409, edited.text
    assert copy.status_code == 201, copy.text
    assert [q["statement"] for q in copy.json()["open_questions"]] == [q["statement"] for q in OPEN]


def test_an_unstarted_templates_open_questions_can_change(repo, client):
    """FR-060: before any start, the teacher may replace them; at most six."""
    c = _class(repo, client)
    template_id = c["template"]["id"]

    edited = client.patch(
        f"/api/teacher/exam-templates/{template_id}",
        headers=c["teacher_headers"],
        json={"open_questions": [{"statement": "Una sola", "reference_solution": "r"}]},
    )
    too_many = client.patch(
        f"/api/teacher/exam-templates/{template_id}",
        headers=c["teacher_headers"],
        json={
            "open_questions": [{"statement": f"P{n}", "reference_solution": ""} for n in range(7)]
        },
    )

    assert edited.status_code == 200, edited.text
    assert [q["statement"] for q in edited.json()["open_questions"]] == ["Una sola"]
    assert too_many.status_code == 422


# ── AB2 ──────────────────────────────────────────────────────────────────────


def test_the_ai_proposes_four_levels_with_the_code_and_no_name(repo, client, ai):
    """US8-AS4, FR-063: one call per non-empty answer; the prompt carries the statement, the
    reference, the answer and the code, never the student's name or username; the levels are
    recorded as a proposal; a blank answer is 0 without a call."""
    c = _class(repo, client)
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (c["student"],))[0][0]
    sql(repo, "UPDATE users SET display_name = ? WHERE id = ?", ("Ana Pérez", c["student"]))
    exam = _start(client, c)

    assert _submit(client, c, exam, ["2(a+b) es par", ""]).status_code == 200

    rows = _answers(repo, c["student"])
    assert len(ai.prompts) == 1
    prompt = ai.prompts[0]
    assert f"R-{rows[0][0]:06d}" in prompt
    assert OPEN[0]["statement"] in prompt and OPEN[0]["reference_solution"] in prompt
    assert "2(a+b) es par" in prompt
    assert username not in prompt and "Ana Pérez" not in prompt
    assert rows[0][3] == "proposed" and json.loads(rows[0][4]) == LEVELS
    assert rows[0][5] == "Buen planteamiento."
    assert rows[1][3] == "blank"
    assert json.loads(rows[1][4]) == {k: 0 for k in LEVELS}


def test_an_unreadable_reply_leaves_the_answer_to_the_teacher(repo, client, ai):
    """FR-063: a reply that is not four levels 0–3 records no proposal; the state says why."""
    ai.reply = "No puedo calificar esto."
    c = _class(repo, client)
    exam = _start(client, c)

    assert _submit(client, c, exam, ["algo", "otra cosa"]).status_code == 200

    rows = _answers(repo, c["student"])
    assert [r[3] for r in rows] == ["failed", "failed"]
    assert [r[4] for r in rows] == [None, None]


def test_without_a_key_the_answer_waits_for_the_teacher(repo, client, no_ai_key):
    """FR-063: no key, no call; the state says so."""
    c = _class(repo, client)
    exam = _start(client, c)

    assert _submit(client, c, exam, ["algo", ""]).status_code == 200

    assert [r[3] for r in _answers(repo, c["student"])] == ["no_key", "blank"]
