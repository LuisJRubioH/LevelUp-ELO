"""
Spec 006 deliveries AB1 and AB2 (US8; FR-060 … FR-064): the two kinds of open question.

A template's teacher writes short-answer questions (accepted answers) and procedure questions
(reference solution). A student gets the statements and kinds, never the answers; a short answer
is graded on submission against the accepted ones, equivalent forms counted, with no AI; a
procedure is a photo uploaded while the session is open, kept under a code, replaced by a new one,
refused when it should be; with no photo it is blank. After the submission a vision model is asked
for four levels per procedure photo, with the code and never a name. Both engines.
"""

import io
import json

import pytest
from PIL import Image

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    sql,
)

SHORT = {"kind": "short", "statement": "¿Cuánto es 10 ÷ 4?", "accepted_answers": ["5/2"]}
PROCEDURE = {
    "kind": "procedure",
    "statement": "Demuestra que la suma de dos pares es par.",
    "reference_solution": "2a+2b=2(a+b)",
}
OPEN = [SHORT, PROCEDURE]
LEVELS = {"comprension": 3, "estrategia": 2, "ejecucion": 2, "justificacion": 1}


def _png(color=(200, 30, 30)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (12, 12), color).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


@pytest.fixture
def ai(monkeypatch):
    """A vision stub: records every prompt and image and answers with `ai.reply`."""
    from api.config import settings

    monkeypatch.setattr(settings, "system_ai_api_key", "gsk_test_only")
    monkeypatch.setattr(settings, "ai_key_procedure", "")

    class Stub:
        reply = json.dumps({**LEVELS, "comentario": "Buen planteamiento."})
        calls: list = []

    def fake_vision(image_bytes, mime_type, api_key, prompt, model=None, timeout=None):
        Stub.calls.append({"image": image_bytes, "mime": mime_type, "prompt": prompt})
        return Stub.reply

    monkeypatch.setattr(
        "src.infrastructure.external_api.math_procedure_review.rubric_from_image", fake_vision
    )
    Stub.calls = []
    return Stub


@pytest.fixture
def no_ai_key(monkeypatch):
    from api.config import settings

    for name in ("system_ai_api_key", "ai_key_procedure"):
        monkeypatch.setattr(settings, name, "")


def _class(repo, client, open_questions=OPEN):
    course, items = make_course(repo, ["ab_a", "ab_b"])
    item_ids = [ids[0] for ids in items.values()]
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, course)
    students = []
    for _ in range(2):
        student = make_student(repo)
        sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
        enroll(repo, student, course, group)
        students.append(student)
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
        "student": students[0],
        "headers": headers_for(repo, students[0]),
        "other_headers": headers_for(repo, students[1]),
        "teacher_headers": teacher_headers,
    }


def _start(client, c, headers=None):
    response = client.post(
        "/api/student/exam/start",
        headers=headers or c["headers"],
        json={"course_id": c["course"], "template_id": c["template"]["id"]},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _question(exam, kind):
    return next(q for q in exam["open_questions"] if q["kind"] == kind)


def _photo(client, headers, exam, question_id, data=None, mime="image/png", name="hoja.png"):
    return client.post(
        "/api/student/exam/open-photo",
        headers=headers,
        data={"session_id": exam["session_id"], "question_id": str(question_id)},
        files={"file": (name, data if data is not None else _png(), mime)},
    )


def _submit(client, c, exam, short_text="5/2"):
    return client.post(
        "/api/student/exam/submit",
        headers=c["headers"],
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
            "open_answers": [{"question_id": _question(exam, "short")["id"], "text": short_text}],
        },
    )


def _answers(repo, user_id):
    rows = sql(
        repo,
        "SELECT a.id, q.kind, a.answer_text, a.auto_correct, a.ai_status, a.ai_levels,"
        " a.ai_feedback, a.file_hash FROM exam_open_answers a"
        " JOIN exam_open_questions q ON q.id = a.question_id"
        " WHERE a.user_id = ? ORDER BY q.position",
        (user_id,),
    )
    return {r[1]: r for r in rows}


def _ratings(repo, user_id):
    return sql(
        repo,
        "SELECT course_id, topic, current_elo FROM student_course_topic_elo WHERE user_id = ?"
        " ORDER BY course_id, topic",
        (user_id,),
    )


# ── AB1: the teacher's questions (FR-060) ───────────────────────────────────


def test_the_teacher_writes_both_kinds(repo, client):
    """FR-060: a short answer keeps its accepted answers, a procedure its reference solution."""
    c = _class(repo, client)
    got = client.get("/api/teacher/exam-templates", headers=c["teacher_headers"]).json()
    questions = next(t for t in got if t["id"] == c["template"]["id"])["open_questions"]

    assert [q["kind"] for q in questions] == ["short", "procedure"]
    assert questions[0]["accepted_answers"] == ["5/2"]
    assert questions[1]["reference_solution"] == "2a+2b=2(a+b)"


def test_a_short_question_needs_an_accepted_answer(repo, client):
    """FR-060: a short answer without accepted answers is refused."""
    c = _class(repo, client)

    response = client.patch(
        f"/api/teacher/exam-templates/{c['template']['id']}",
        headers=c["teacher_headers"],
        json={"open_questions": [{"kind": "short", "statement": "¿?", "accepted_answers": []}]},
    )

    assert response.status_code == 422


def test_an_unstarted_templates_open_questions_can_change(repo, client):
    """FR-060: before any start the teacher may replace them; at most six."""
    c = _class(repo, client)
    template_id = c["template"]["id"]

    edited = client.patch(
        f"/api/teacher/exam-templates/{template_id}",
        headers=c["teacher_headers"],
        json={"open_questions": [PROCEDURE]},
    )
    too_many = client.patch(
        f"/api/teacher/exam-templates/{template_id}",
        headers=c["teacher_headers"],
        json={"open_questions": [SHORT] * 7},
    )

    assert edited.status_code == 200, edited.text
    assert [q["kind"] for q in edited.json()["open_questions"]] == ["procedure"]
    assert too_many.status_code == 422


def test_a_started_templates_open_questions_are_locked(repo, client, no_ai_key):
    """US8-AS4, FR-060: 409 once a student started it; a duplicate carries the questions."""
    c = _class(repo, client)
    _start(client, c)
    template_id = c["template"]["id"]

    edited = client.patch(
        f"/api/teacher/exam-templates/{template_id}",
        headers=c["teacher_headers"],
        json={"open_questions": [PROCEDURE]},
    )
    copy = client.post(
        f"/api/teacher/exam-templates/{template_id}/duplicate", headers=c["teacher_headers"]
    )

    assert edited.status_code == 409, edited.text
    assert copy.status_code == 201, copy.text
    assert [q["kind"] for q in copy.json()["open_questions"]] == ["short", "procedure"]
    assert copy.json()["open_questions"][0]["accepted_answers"] == ["5/2"]


# ── AB1: what the student sees and sends (FR-061 … FR-063) ──────────────────


def test_a_student_gets_statements_and_kinds_never_the_answers(repo, client, no_ai_key):
    """US8-AS1, FR-061: statements and kinds in order, no accepted answer, no reference; a resume
    says which procedure already has its photo."""
    c = _class(repo, client)
    exam = _start(client, c)
    assert _photo(client, c["headers"], exam, _question(exam, "procedure")["id"]).status_code == 200
    again = _start(client, c)

    for got in (exam, again):
        assert [(q["kind"], q["statement"]) for q in got["open_questions"]] == [
            (q["kind"], q["statement"]) for q in OPEN
        ]
        text = json.dumps(got)
        assert "5/2" not in text and "2(a+b)" not in text
    assert [q["has_photo"] for q in exam["open_questions"]] == [False, False]
    assert [q["has_photo"] for q in again["open_questions"]] == [False, True]


@pytest.mark.parametrize(
    "typed, right", [("5/2", True), ("2,5", True), ("2.5", True), (" 5 / 2 ", True), ("3", False)]
)
def test_short_answers_are_graded_with_equivalents(repo, client, ai, typed, right):
    """US8-AS2, FR-062: right when equal in value; no AI call; no rating moves; the student sees
    which short answers were right."""
    c = _class(repo, client, open_questions=[SHORT])
    before = _ratings(repo, c["student"])
    exam = _start(client, c)

    submitted = _submit(client, c, exam, typed)

    assert submitted.status_code == 200, submitted.text
    body = submitted.json()
    assert body["open_results"] == [
        {"question_id": _question(exam, "short")["id"], "correct": right}
    ]
    assert body["open_pending"] == 0
    row = _answers(repo, c["student"])["short"]
    assert row[2] == typed and row[3] == (1 if right else 0) and row[4] == "auto"
    assert ai.calls == []
    assert _ratings(repo, c["student"]) == before


def test_a_typed_answer_to_a_procedure_is_refused(repo, client, no_ai_key):
    """FR-062: a procedure is answered with a photo; a typed answer to it is 400, nothing kept."""
    c = _class(repo, client)
    exam = _start(client, c)

    response = client.post(
        "/api/student/exam/submit",
        headers=c["headers"],
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
            "open_answers": [{"question_id": _question(exam, "procedure")["id"], "text": "x"}],
        },
    )

    assert response.status_code == 400, response.text
    assert _answers(repo, c["student"]) == {}


def test_a_procedure_photo_is_kept_and_replaced(repo, client, no_ai_key):
    """US8-AS3, FR-063: one photo per procedure, the last one kept with its fingerprint."""
    import hashlib

    c = _class(repo, client)
    exam = _start(client, c)
    question = _question(exam, "procedure")["id"]
    first, second = _png((10, 10, 10)), _png((240, 240, 240))

    assert _photo(client, c["headers"], exam, question, first).status_code == 200
    assert _photo(client, c["headers"], exam, question, second).status_code == 200
    assert _submit(client, c, exam).status_code == 200

    row = _answers(repo, c["student"])["procedure"]
    assert row[7] == hashlib.sha256(second).hexdigest()
    assert row[4] == "no_key"


def test_a_photo_upload_is_refused_when_it_should_be(repo, client, no_ai_key):
    """US8-AS3, FR-063: another student's session, a short question, a file that is not a
    picture, and an upload after the submission are refused."""
    c = _class(repo, client)
    exam = _start(client, c)
    procedure = _question(exam, "procedure")["id"]
    short = _question(exam, "short")["id"]

    other = _photo(client, c["other_headers"], exam, procedure)
    wrong_question = _photo(client, c["headers"], exam, short)
    not_a_picture = _photo(
        client, c["headers"], exam, procedure, b"%PDF-1.4 nada", "application/pdf", "hoja.pdf"
    )
    assert _submit(client, c, exam).status_code == 200
    late = _photo(client, c["headers"], exam, procedure)

    assert other.status_code == 404
    assert wrong_question.status_code == 400
    assert not_a_picture.status_code in (415, 422)
    assert late.status_code == 409


def test_a_procedure_without_a_photo_is_blank(repo, client, ai):
    """FR-063: no photo at submission is 0 on every criterion, with no call to the AI."""
    c = _class(repo, client)
    exam = _start(client, c)

    submitted = _submit(client, c, exam)

    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["open_pending"] == 1
    row = _answers(repo, c["student"])["procedure"]
    assert row[4] == "blank" and json.loads(row[5]) == {k: 0 for k in LEVELS}
    assert ai.calls == []


# ── AB2: the AI's proposal for a photo (FR-064) ─────────────────────────────


def test_the_ai_proposes_levels_for_a_photo_with_the_code_and_no_name(repo, client, ai):
    """US8-AS5, FR-064: the photo, the statement, the reference and the code go to the vision
    model, never the student's name or username; the levels are recorded as a proposal."""
    c = _class(repo, client)
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (c["student"],))[0][0]
    sql(repo, "UPDATE users SET display_name = ? WHERE id = ?", ("Ana Pérez", c["student"]))
    exam = _start(client, c)
    photo = _png()
    _photo(client, c["headers"], exam, _question(exam, "procedure")["id"], photo)

    assert _submit(client, c, exam).status_code == 200

    row = _answers(repo, c["student"])["procedure"]
    assert len(ai.calls) == 1
    call = ai.calls[0]
    assert call["image"] == photo and call["mime"] == "image/png"
    assert f"R-{row[0]:06d}" in call["prompt"]
    assert PROCEDURE["statement"] in call["prompt"]
    assert PROCEDURE["reference_solution"] in call["prompt"]
    assert username not in call["prompt"] and "Ana Pérez" not in call["prompt"]
    assert row[4] == "proposed" and json.loads(row[5]) == LEVELS
    assert row[6] == "Buen planteamiento."


def test_an_unreadable_reply_leaves_the_photo_to_the_teacher(repo, client, ai):
    """FR-064: a reply that is not four levels 0–3 records no proposal; the state says why."""
    ai.reply = "No puedo calificar esto."
    c = _class(repo, client)
    exam = _start(client, c)
    _photo(client, c["headers"], exam, _question(exam, "procedure")["id"])

    assert _submit(client, c, exam).status_code == 200

    row = _answers(repo, c["student"])["procedure"]
    assert row[4] == "failed" and row[5] is None


def test_without_a_key_the_photo_waits_for_the_teacher(repo, client, no_ai_key):
    """FR-064: no key, no call; the state says so."""
    c = _class(repo, client)
    exam = _start(client, c)
    _photo(client, c["headers"], exam, _question(exam, "procedure")["id"])

    assert _submit(client, c, exam).status_code == 200

    assert _answers(repo, c["student"])["procedure"][4] == "no_key"
