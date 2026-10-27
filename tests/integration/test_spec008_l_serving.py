"""
Spec 008 delivery L (US4; FR-030, plan-l.md O-IL1 … O-IL3): what the serving paths do with a
retired item.

New practice, new exams, the diagnostic and PvP never serve it; a template that holds it cannot
start and cannot be written; what was served before the retirement is honoured (a started exam is
graded, an answer in flight counts). Both engines, through the app's real endpoints.
"""

import json
import socket as _socket
import threading
import time

import pytest

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    sql,
)
from tests.integration.test_spec008_l_item_life import LifeBank


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _student(repo, bank):
    student = make_student(repo)
    enroll(repo, student, bank.course)
    return student, headers_for(repo, student)


def _start(client, headers, course, n=3, template=None):
    body = {"course_id": course, "n_questions": n, "time_limit_minutes": 10}
    if template is not None:
        body["template_id"] = template
    return client.post("/api/student/exam/start", headers=headers, json=body)


def _retire(repo, bank, item_id):
    bank.item(item_id)["retired"] = True
    bank.sync(repo)


# ── Phase 1: pins that hold on the unchanged code ───────────────────────────


def test_spec008_l_a_started_exam_grades_an_item_retired_since(repo, client, tmp_path, monkeypatch):
    """Spec § Edge Cases: an exam started before the retirement grades the item as served."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.sync(repo)
    _, headers = _student(repo, bank)
    exam = _start(client, headers, bank.course).json()
    retired = exam["items"][0]["id"]
    _retire(repo, bank, retired)

    response = client.post(
        "/api/student/exam/submit",
        headers=headers,
        json={
            "session_id": exam["session_id"],
            "answers": [{"item_id": i["id"], "selected_option": "A"} for i in exam["items"]],
        },
    )

    assert response.status_code == 200, response.text
    by_id = {r["item_id"]: r for r in response.json()["results"]}
    assert by_id[retired]["graded"] is True
    assert response.json()["total_questions"] == 3


def test_spec008_l_an_answer_to_an_item_retired_after_serving_is_accepted(
    repo, client, tmp_path, monkeypatch
):
    """O-IL2: an item served before its retirement is answered as any other — 200, and the
    rating moves."""
    bank = LifeBank(tmp_path, monkeypatch, n=1)
    bank.sync(repo)
    student, headers = _student(repo, bank)
    served = client.post(
        "/api/student/next-question", headers=headers, json={"course_id": bank.course}
    )
    assert served.status_code == 200, served.text
    item_id = served.json()["item"]["id"]
    _retire(repo, bank, item_id)

    response = client.post(
        "/api/student/answer",
        headers=headers,
        json={"item_id": item_id, "selected_option": "A", "time_taken": 20},
    )

    assert response.status_code == 200, response.text
    assert rating_of(repo, student, bank.course, "Vida") is not None
    assert sql(
        repo, "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND elo_valid = 1", (student,)
    ) == [(1,)]
