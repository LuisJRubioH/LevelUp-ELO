"""
Spec 005 delivery K3 (US3; FR-030 … FR-033): KatIA's record.

A student's messages about one item, with KatIA's replies, are one conversation; its earlier
turns go to the provider as context. The next answer to the item closes it as «superado» or «no
superado»; asking for another item, ending the session or 24 hours without a message close it as
«abandonado». When it closes its text is deleted and a summary stays: topic, item, turns, outcome
and the kind of difficulty (N2) — what the teacher reads; the export gives counts. Both engines;
the provider is a double that records every call.
"""

import io

import openpyxl
import pytest

from tests.api.test_spec005_k1_providers import Provider
from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    sql,
)

KEY = "gsk_k3_test"


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


@pytest.fixture
def no_system_key(monkeypatch):
    from api.config import settings

    for name in ("system_ai_api_key", "ai_key_katia"):
        monkeypatch.setattr(settings, name, "")


def _class(repo):
    """A teacher's group in a two-topic course, with one enrolled student."""
    course, items = make_course(repo, ["k3_alpha", "k3_beta"])
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, course, group)
    return {
        "course": course,
        "item": items["k3_alpha"][0],
        "other": items["k3_beta"][0],
        "student": student,
        "headers": headers_for(repo, student),
        "teacher": headers_for(repo, teacher),
    }


def _katia(client, c, message, item=None):
    response = client.post(
        "/api/ai/socratic",
        headers=c["headers"],
        json={
            "item_id": item or c["item"],
            "student_message": message,
            "course_id": c["course"],
            "api_key": KEY,
        },
    )
    assert response.status_code == 200, response.text
    return response


def _answer(client, c, correct):
    response = client.post(
        "/api/student/answer",
        headers=c["headers"],
        json={"item_id": c["item"], "selected_option": "A" if correct else "B", "time_taken": 20},
    )
    assert response.status_code == 200, response.text


def _prompt(call) -> str:
    return "\n".join(str(m.get("content")) for m in call["messages"])


def _conversations(repo, student):
    return sql(
        repo,
        "SELECT id, item_id, status, outcome, turns, difficulty, closed_at"
        " FROM katia_conversations WHERE user_id = ? ORDER BY id",
        (student,),
    )


def _texts(repo, student):
    return sql(
        repo,
        "SELECT m.text FROM katia_messages m"
        " JOIN katia_conversations k ON k.id = m.conversation_id WHERE k.user_id = ?",
        (student,),
    )


# ── FR-030: one conversation, its turns as context ───────────────────────────


def test_a_conversation_keeps_its_turns_and_sends_them_as_context(
    repo, client, monkeypatch, no_system_key
):
    """FR-030: one open conversation per item; the last 6 earlier turns go to the provider."""
    c = _class(repo)
    provider = Provider(monkeypatch, reply="¿Qué observas en el primer término?")

    for n in range(1, 9):
        _katia(client, c, f"mensaje k3 número {n}")

    rows = _conversations(repo, c["student"])
    assert [(r[1], r[2], r[4]) for r in rows] == [(c["item"], "open", 8)]
    assert len(_texts(repo, c["student"])) == 16
    second = _prompt(provider.calls[1])
    assert "mensaje k3 número 1" in second and "¿Qué observas en el primer término?" in second
    last = _prompt(provider.calls[7])
    assert "mensaje k3 número 1" not in last
    assert all(f"mensaje k3 número {n}" in last for n in range(2, 9))


# ── FR-031: how it closes ────────────────────────────────────────────────────


@pytest.mark.parametrize("correct, outcome", [(True, "superado"), (False, "no_superado")])
def test_answering_right_or_wrong_closes_as_superado_or_no_superado(
    repo, client, monkeypatch, no_system_key, correct, outcome
):
    """US3-AS1, FR-031: the answer to the item closes its conversation, and the teacher sees it."""
    c = _class(repo)
    Provider(monkeypatch)
    _katia(client, c, "no sé cómo empezar")
    _katia(client, c, "¿y ahora?")

    _answer(client, c, correct)

    rows = _conversations(repo, c["student"])
    assert [(r[2], r[3], r[4], r[5]) for r in rows] == [("closed", outcome, 2, "sin_clasificar")]
    assert rows[0][6] is not None
    seen = client.get(f"/api/teacher/student/{c['student']}/katia-history", headers=c["teacher"])
    assert seen.status_code == 200, seen.text
    [summary] = seen.json()["conversations"]
    assert (summary["item_id"], summary["topic"], summary["turns"], summary["outcome"]) == (
        c["item"],
        "k3_alpha",
        2,
        outcome,
    )
    assert summary["difficulty"] == "sin_clasificar"


def _next_question(client, c):
    response = client.post(
        "/api/student/next-question", headers=c["headers"], json={"course_id": c["course"]}
    )
    assert response.status_code == 200, response.text


def _logout(client, c):
    response = client.post("/api/auth/logout", headers=c["headers"])
    assert response.status_code == 204, response.text


def _silence(client, c, repo):
    sql(
        repo,
        "UPDATE katia_conversations SET last_message_at = ? WHERE user_id = ?",
        ("2000-01-01 00:00:00", c["student"]),
    )
    # The sweep runs on every KatIA request: a message about another item triggers it.
    _katia(client, c, "otra pregunta", item=c["other"])


@pytest.mark.parametrize(
    "leave", [_next_question, _logout, _silence], ids=["other", "logout", "24h"]
)
def test_another_item_logout_or_24h_close_as_abandonado(
    repo, client, monkeypatch, no_system_key, leave
):
    """US3-AS2, FR-031, FR-032."""
    c = _class(repo)
    Provider(monkeypatch)
    _katia(client, c, "estoy perdido")

    leave(client, c, repo) if leave is _silence else leave(client, c)

    first = _conversations(repo, c["student"])[0]
    assert (first[1], first[2], first[3]) == (c["item"], "closed", "abandonado")
    texts = [t[0] for t in _texts(repo, c["student"])]
    assert "estoy perdido" not in texts


def test_an_answer_closes_only_that_items_conversation(repo, client, monkeypatch, no_system_key):
    """FR-031: a conversation about another item stays open after an answer."""
    c = _class(repo)
    Provider(monkeypatch)
    _katia(client, c, "sobre el otro", item=c["other"])

    _answer(client, c, True)

    assert [(r[1], r[2]) for r in _conversations(repo, c["student"])] == [(c["other"], "open")]


# ── FR-032: no text after closing ────────────────────────────────────────────


def test_no_text_remains_after_closing(repo, client, monkeypatch, no_system_key):
    """US3-AS3, FR-032, SC-004, N3: closed text is gone from every table and from the export."""
    c = _class(repo)
    Provider(monkeypatch, reply="¿Qué dice el enunciado?")
    _katia(client, c, "texto que no debe quedar k3")

    _answer(client, c, False)

    assert _texts(repo, c["student"]) == []
    assert sql(repo, "SELECT 1 FROM katia_interactions WHERE user_id = ?", (c["student"],)) == []
    # SC-004: the sweep leaves no text older than 24 hours, closed or open.
    repo.expire_stale_katia_conversations()
    assert sql(
        repo,
        "SELECT COUNT(*) FROM katia_messages m JOIN katia_conversations k"
        " ON k.id = m.conversation_id WHERE k.status = 'closed'",
    ) == [(0,)]
    for path in ("/api/teacher/export/xlsx", "/api/teacher/export/csv"):
        exported = client.get(path, headers=c["teacher"])
        assert exported.status_code == 200, exported.text
        assert b"texto que no debe quedar" not in exported.content
        assert "Qué dice el enunciado".encode() not in exported.content


# ── FR-031 (N2): the kind of difficulty ──────────────────────────────────────


@pytest.mark.parametrize(
    "classifier, expected",
    [
        ("procedimiento", "procedimiento"),
        ("Diría que es un problema de concepto y de cálculo.", "sin_clasificar"),
        (RuntimeError("provider down"), "sin_clasificar"),
    ],
    ids=["label", "free-text", "failure"],
)
def test_an_unclassifiable_difficulty_is_sin_clasificar(
    repo, client, monkeypatch, classifier, expected
):
    """FR-031, N2: one provider call with the conversation's text picks one label of the list."""
    from api.config import settings

    monkeypatch.setattr(settings, "ai_key_katia", "gsk_k3_system")
    c = _class(repo)
    provider = Provider(monkeypatch)
    _katia(client, c, "no entiendo qué me piden k3")
    provider.reply = classifier

    _answer(client, c, False)

    assert [r[5] for r in _conversations(repo, c["student"])] == [expected]
    classify = _prompt(provider.calls[-1])
    assert "no entiendo qué me piden k3" in classify and "procedimiento" in classify
    assert _texts(repo, c["student"]) == []


def test_without_a_system_key_the_difficulty_is_sin_clasificar(
    repo, client, monkeypatch, no_system_key
):
    """FR-031: the student's own key never outlives their request (R7)."""
    c = _class(repo)
    provider = Provider(monkeypatch)
    _katia(client, c, "hola")
    calls = len(provider.calls)

    _answer(client, c, True)

    assert len(provider.calls) == calls
    assert [r[5] for r in _conversations(repo, c["student"])] == ["sin_clasificar"]


# ── FR-033: what the teacher reads ───────────────────────────────────────────


def test_the_teacher_reads_summaries_and_exports_counts_only(
    repo, client, monkeypatch, no_system_key
):
    """FR-033: summaries without text; the export counts per course, topic and outcome."""
    c = _class(repo)
    Provider(monkeypatch)
    _katia(client, c, "primera k3")
    _answer(client, c, False)
    _katia(client, c, "segunda k3")
    _answer(client, c, True)
    _katia(client, c, "tercera k3")
    _next_question(client, c)

    history = client.get(
        f"/api/teacher/student/{c['student']}/katia-history", headers=c["teacher"]
    ).json()
    keys = {key for row in history["conversations"] for key in row}
    assert keys == {
        "id",
        "course_id",
        "course_name",
        "topic",
        "item_id",
        "turns",
        "outcome",
        "difficulty",
        "misconception_tag",
        "opened_at",
        "closed_at",
    }
    assert sorted(r["outcome"] for r in history["conversations"]) == [
        "abandonado",
        "no_superado",
        "superado",
    ]

    book = openpyxl.load_workbook(
        io.BytesIO(client.get("/api/teacher/export/xlsx", headers=c["teacher"]).content)
    )
    sheet = book["KatIA"]
    header = [cell.value for cell in sheet[1]]
    assert header == ["course_id", "course_name", "topic", "outcome", "conversations"]
    rows = {
        (row[2], row[3]): row[4]
        for row in sheet.iter_rows(min_row=2, values_only=True)
        if row[0] == c["course"]
    }
    assert rows == {
        ("k3_alpha", "abandonado"): 1,
        ("k3_alpha", "no_superado"): 1,
        ("k3_alpha", "superado"): 1,
    }
