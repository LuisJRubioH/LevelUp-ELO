"""
Spec 005 delivery A: as-is pins FR-005 (no API key stored or returned) and FR-006 (key
precedence). Both pass on the unchanged code.
"""

import json
import os
import re
import sqlite3

import pytest

USER_KEY = "gsk_spec005_user_key_never_stored"
SYSTEM_KEY = "gsk_spec005_system_key_never_returned"


def _settings(**values):
    from api.config import Settings

    return Settings(**values)


def test_spec005_user_key_then_function_key_then_general_key():
    """FR-006: the user's key, else the function's, else the general one."""
    s = _settings(
        system_ai_api_key="general",
        ai_key_katia="katia",
        ai_key_procedure="procedure",
        ai_key_teacher_analysis="teacher",
    )
    assert s.get_ai_key("katia", " mine ") == "mine"
    assert s.get_ai_key("katia", "   ") == "katia"
    assert s.get_ai_key("procedure") == "procedure"
    assert s.get_ai_key("teacher_analysis") == "teacher"
    assert s.get_ai_key("student_analysis") == "general"  # no key of its own
    assert s.get_ai_key("unknown") == "general"
    assert _settings().get_ai_key("katia") == ""


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _database_text() -> str:
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        return "\n".join(conn.iterdump())


def test_spec005_no_table_has_a_key_column(api_client):
    """FR-005: no column of the schema is meant to hold an API key."""
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        columns = [(t, c[1]) for t in tables for c in conn.execute(f"PRAGMA table_info({t})")]
    assert [c for c in columns if re.search(r"api_?key|secret|token_key", c[1], re.I)] == []


def test_spec005_a_users_key_is_neither_stored_nor_returned(
    api_client, student_headers, monkeypatch
):
    """FR-005: the key a student sends reaches the provider call and nothing else — not the
    stream, not the stored conversation, not any row of the database."""
    seen = []

    def fake_guidance(*args, **_kwargs):
        seen.append(args)
        return "¿Qué observas en el primer término?"

    monkeypatch.setattr(
        "src.infrastructure.external_api.ai_client.get_socratic_guidance", fake_guidance
    )
    response = api_client.post(
        "/api/ai/socratic",
        headers=student_headers,
        json={
            "item_id": "q21",
            "item_content": "Fórmula de integración por partes",
            "student_message": "spec005 key probe",
            "course_id": "calculo_diferencial",
            "api_key": USER_KEY,
        },
    )

    assert response.status_code == 200
    assert seen and USER_KEY in seen[0]  # it did reach the provider call
    assert USER_KEY not in response.text
    assert USER_KEY not in _database_text()


def test_spec005_the_system_key_is_never_returned(api_client, monkeypatch):
    """FR-005: `/ai-status` says whether AI is available, never the key."""
    from api.config import settings

    monkeypatch.setattr(settings, "system_ai_api_key", SYSTEM_KEY)
    body = api_client.get("/api/student/ai-status")
    assert body.status_code == 200
    assert json.loads(body.text)["available"] is True
    assert SYSTEM_KEY not in body.text
