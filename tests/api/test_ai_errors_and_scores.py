"""
When the AI provider fails, KatIA says she could not answer: the provider's error text is not
streamed as her reply nor saved as her answer in katia_interactions (the teacher reads that
history and exports it). An unexpected failure shows a generic message, not the exception text.
The procedure review's AI score is advisory and lives on a 0-100 scale: a value outside it is
brought into range before it is signed and shown.
"""

import io
import json
import os
import sqlite3

import pytest

ITEM = "q47"  # calculo_integral, in the bank the API syncs at start


def _events(response):
    return [
        json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")
    ]


def _saved_replies(student_message):
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        return [
            row[0]
            for row in conn.execute(
                "SELECT katia_response FROM katia_interactions WHERE student_message = ?",
                (student_message,),
            )
        ]


def _ask(api_client, headers, message):
    return api_client.post(
        "/api/ai/socratic",
        headers=headers,
        json={
            "item_id": ITEM,
            "item_content": "Fórmula de integración por partes",
            "student_message": message,
            "course_id": "calculo_integral",
            "api_key": "gsk_fake_test_key",
        },
    )


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _reply_with(monkeypatch, outcome):
    def fake_guidance(*_args, **_kwargs):
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(
        "src.infrastructure.external_api.ai_client.get_socratic_guidance", fake_guidance
    )


@pytest.mark.parametrize(
    "provider_says",
    [
        "ERROR_401: ❌ API Key inválida o expirada para groq. Verifica tu clave en el panel lateral.",
        "ERROR_429: ⏳ Límite de solicitudes alcanzado. Espera un momento antes de continuar.",
        "❌ Error inesperado: APIError. Contacta al administrador.",
        "",
    ],
    ids=["bad-key", "rate-limited", "unexpected", "empty"],
)
def test_a_provider_failure_is_not_katias_reply(
    api_client, student_headers, monkeypatch, provider_says
):
    message = f"failure probe {provider_says[:9]}"
    _reply_with(monkeypatch, provider_says)

    events = _events(_ask(api_client, student_headers, message))

    assert [e for e in events if "token" in e] == []
    assert [e for e in events if "error" in e] != []
    assert _saved_replies(message) == []


def test_an_unexpected_failure_shows_no_internal_detail(api_client, student_headers, monkeypatch):
    _reply_with(monkeypatch, RuntimeError("upstream said: internal-host-10.0.0.7 trace"))

    events = _events(_ask(api_client, student_headers, "exception probe"))

    errors = [e["error"] for e in events if "error" in e]
    assert errors and all("internal-host" not in error for error in errors)


def test_a_reply_is_streamed_and_saved(api_client, student_headers, monkeypatch):
    _reply_with(monkeypatch, "¿Qué parte del producto derivarías primero?")

    events = _events(_ask(api_client, student_headers, "reply probe"))

    assert "".join(e["token"] for e in events if "token" in e) == (
        "¿Qué parte del producto derivarías primero?"
    )
    assert _saved_replies("reply probe") == ["¿Qué parte del producto derivarías primero?"]


def _png() -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


@pytest.mark.parametrize("ai_score, shown", [(250, 100), (-5, 0), (73, 73), ("n/a", None)])
def test_the_ai_score_stays_on_its_0_to_100_scale(
    api_client, student_headers, monkeypatch, ai_score, shown
):
    from api.dependencies import decode_token

    monkeypatch.setattr(
        "src.infrastructure.external_api.math_procedure_review.review_math_procedure",
        lambda *_a, **_k: {"score_procedimiento": ai_score, "evaluacion_global": "bien"},
    )

    response = api_client.post(
        "/api/student/procedure/analyze",
        headers=student_headers,
        data={"item_id": ITEM, "api_key": "gsk_fake_test_key"},
        files={"file": ("work.png", _png(), "image/png")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["review"]["score_procedimiento"] == shown
    assert decode_token(body["analysis_token"]).get("score") == shown
