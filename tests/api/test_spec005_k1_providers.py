"""
Spec 005 delivery K1 (US2, US4; FR-010 … FR-016): one key reaches its provider.

The key's prefix picks the provider for every AI feature, whatever the browser sends; each
function's model comes from settings; every provider call has a timeout; the procedure review is
Groq only; the teacher analysis receives the student's procedure statistics; and no response
carries exception text. Provider SDKs are replaced by doubles that record what they were given.
"""

import io
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ITEM = "q47"  # calculo_integral, in the bank the API syncs at start
UNKNOWN = "Clave no reconocida"
GROQ_ONLY = "La revisión con IA usa Groq"


class Provider:
    """Records every SDK client built and every call made; replies with `reply` or raises it."""

    def __init__(self, monkeypatch, reply="¿Qué observas en el primer término?"):
        self.calls = []
        self.reply = reply
        rec = self

        class _Completions:
            def create(self, model, messages, **kwargs):
                rec.calls[-1].update(model=model, messages=messages, **kwargs)
                if isinstance(rec.reply, Exception):
                    raise rec.reply
                msg = SimpleNamespace(content=rec.reply)
                return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

        class FakeOpenAI:
            def __init__(self, api_key=None, base_url=None, timeout=None, **_):
                rec.calls.append({"sdk": "openai", "base_url": base_url, "timeout": timeout})
                self.chat = SimpleNamespace(completions=_Completions())

        class _Messages:
            def create(self, model, messages, **kwargs):
                rec.calls[-1].update(model=model, messages=messages, **kwargs)
                if isinstance(rec.reply, Exception):
                    raise rec.reply
                return SimpleNamespace(content=[SimpleNamespace(text=rec.reply)])

        class FakeAnthropic:
            def __init__(self, api_key=None, timeout=None, **_):
                rec.calls.append({"sdk": "anthropic", "base_url": None, "timeout": timeout})
                self.messages = _Messages()

        monkeypatch.setattr("openai.OpenAI", FakeOpenAI)
        monkeypatch.setattr("anthropic.Anthropic", FakeAnthropic)


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _katia(api_client, headers, key, **extra):
    return api_client.post(
        "/api/ai/socratic",
        headers=headers,
        json={
            "item_id": ITEM,
            "item_content": "Fórmula de integración por partes",
            "student_message": "spec005 k1 probe",
            "course_id": "calculo_integral",
            "api_key": key,
            **extra,
        },
    )


def _png() -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


def _review(api_client, headers, key):
    return api_client.post(
        "/api/student/procedure/analyze",
        headers=headers,
        data={"item_id": ITEM, "api_key": key},
        files={"file": ("p.png", _png(), "image/png")},
    )


# ── FR-010, FR-011, FR-012: the key decides the provider, settings the model ─


def _expected(provider):
    from api.config import settings
    from src.infrastructure.external_api.ai_client import PROVIDERS

    if provider == "groq":
        return "openai", PROVIDERS["groq"]["base_url"], settings.ai_model_katia
    if provider == "anthropic":
        return "anthropic", None, PROVIDERS["anthropic"]["model_cog"]
    return "openai", PROVIDERS[provider]["base_url"], PROVIDERS[provider]["model_cog"]


@pytest.mark.parametrize(
    "key, provider",
    [
        ("gsk_k1_test", "groq"),
        ("sk-ant-k1_test", "anthropic"),
        ("sk-proj-k1_test", "openai"),
        ("AIzaSyk1_test", "gemini"),
    ],
)
def test_the_key_prefix_picks_the_provider_for_every_feature(
    api_client, student_headers, monkeypatch, key, provider
):
    """US2-AS1, FR-010, FR-012: KatIA calls the key's provider with the function's model."""
    calls = Provider(monkeypatch).calls

    response = _katia(api_client, student_headers, key)

    assert response.status_code == 200, response.text
    sdk, base_url, model = _expected(provider)
    assert calls and (calls[0]["sdk"], calls[0]["base_url"], calls[0]["model"]) == (
        sdk,
        base_url,
        model,
    )


def test_the_browser_cannot_choose_provider_or_model(api_client, student_headers, monkeypatch):
    """FR-011: a provider and a model sent by the browser are ignored."""
    from api.config import settings

    calls = Provider(monkeypatch).calls

    response = _katia(api_client, student_headers, "gsk_k1_test", provider="anthropic", model="x")

    assert response.status_code == 200, response.text
    assert calls[0]["sdk"] == "openai" and calls[0]["model"] == settings.ai_model_katia


def test_models_come_from_settings(api_client, student_headers, monkeypatch):
    """FR-012: AI_MODEL_KATIA names KatIA's model; the defaults are today's Groq models."""
    from api.config import Settings, settings

    defaults = Settings()
    assert (defaults.ai_model_katia, defaults.ai_model_vision, defaults.ai_model_analysis) == (
        "llama-3.1-8b-instant",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
    )
    monkeypatch.setattr(settings, "ai_model_katia", "spec005-katia-model")
    calls = Provider(monkeypatch).calls

    _katia(api_client, student_headers, "gsk_k1_test")

    assert calls[0]["model"] == "spec005-katia-model"


@pytest.mark.parametrize("feature", ["katia", "review", "analysis"])
def test_a_key_with_no_known_prefix_is_refused_naming_the_providers(
    api_client, student_headers, teacher_headers, monkeypatch, feature
):
    """FR-010: a key no prefix names is refused before any provider is called."""

    calls = Provider(monkeypatch).calls
    if feature == "katia":
        response = _katia(api_client, student_headers, "local-key-123")
    elif feature == "review":
        response = _review(api_client, student_headers, "local-key-123")
    else:
        from api.config import settings

        monkeypatch.setattr(settings, "system_ai_api_key", "local-key-123")
        dashboard = api_client.get("/api/teacher/dashboard", headers=teacher_headers).json()
        student_id = dashboard["students"][0]["user_id"]
        response = api_client.post(
            f"/api/teacher/student/{student_id}/ai-analysis", headers=teacher_headers
        )

    assert response.status_code == 422, response.text
    assert UNKNOWN in response.json()["detail"]
    assert calls == []


# ── FR-013: timeouts ─────────────────────────────────────────────────────────


def test_every_provider_call_has_a_timeout(api_client, student_headers, monkeypatch):
    """FR-013: 30 s for KatIA, 90 s for the review."""
    provider = Provider(monkeypatch)
    _katia(api_client, student_headers, "gsk_k1_test")
    provider.reply = json.dumps({"score_procedimiento": 70, "evaluacion_global": "Bien."})
    _review(api_client, student_headers, "gsk_k1_test")

    assert [c["timeout"] for c in provider.calls] == [30, 90]


def test_the_analysis_has_a_timeout_and_the_analysis_model():
    """FR-013, FR-015: the analysis call gets 90 s and the model it is given."""
    from src.infrastructure.external_api import ai_client

    seen = {}

    def fake_call(prompt, model_name, base_url, **kwargs):
        seen.update(prompt=prompt, model=model_name, **kwargs)
        return "Análisis."

    original = ai_client._call_ai_api
    ai_client._call_ai_api = fake_call
    try:
        ai_client.get_pedagogical_analysis(
            {
                "elo_global": 1000.0,
                "attempts_count": 5,
                "topics": ["t"],
                "recent_accuracy": 0.5,
            },
            model_name="llama-3.3-70b-versatile",
            api_key="gsk_x",
            provider="groq",
            timeout=90,
            procedure_stats={"count": 2, "avg_score": 85.0, "scores": [80.0, 90.0]},
        )
    finally:
        ai_client._call_ai_api = original

    assert seen["model"] == "llama-3.3-70b-versatile" and seen["timeout"] == 90
    assert "No ha subido ningun procedimiento" not in seen["prompt"]
    assert "Excelente (85.0/100)" in seen["prompt"]  # scores are 0-100


@pytest.mark.parametrize("raised", [TimeoutError("timed out"), Exception("Request timed out.")])
def test_a_provider_that_does_not_answer_in_time_is_503(
    api_client, student_headers, monkeypatch, raised
):
    """US2-AS3, FR-013: a timeout is a 503 with a fixed message, never a 200."""
    Provider(monkeypatch, reply=raised)

    response = _katia(api_client, student_headers, "gsk_k1_test")

    assert response.status_code == 503
    assert response.json()["detail"] == "La IA no respondió a tiempo. Intenta de nuevo."


# ── FR-014: Groq-only review ─────────────────────────────────────────────────


@pytest.mark.parametrize("key", ["sk-ant-k1_test", "sk-k1_test", "AIzaSyk1_test", "hf_k1"])
def test_review_with_a_non_groq_key_is_refused_before_processing(
    api_client, student_headers, monkeypatch, key
):
    """US2-AS2, FR-014."""
    calls = Provider(monkeypatch).calls

    response = _review(api_client, student_headers, key)

    assert response.status_code == 422
    assert response.json()["detail"] == GROQ_ONLY
    assert calls == []


# ── FR-015: the teacher analysis's inputs ────────────────────────────────────


def test_teacher_analysis_receives_procedure_stats_and_the_analysis_model(
    api_client, teacher_headers, monkeypatch
):
    """US4-AS1, FR-015: the router passes the student's procedure statistics and the model."""
    from api.config import settings
    from src.application.services.teacher_service import TeacherService

    monkeypatch.setattr(settings, "system_ai_api_key", "gsk_k1_test")
    spy = Mock(return_value="Análisis.")
    monkeypatch.setattr(TeacherService, "generate_ai_analysis", spy)
    student_id = api_client.get("/api/teacher/dashboard", headers=teacher_headers).json()[
        "students"
    ][0]["user_id"]

    response = api_client.post(
        f"/api/teacher/student/{student_id}/ai-analysis",
        headers=teacher_headers,
        json={"provider": "anthropic"},
    )

    assert response.status_code == 200, response.text
    kwargs = spy.call_args.kwargs
    assert kwargs["provider"] == "groq"
    assert kwargs["model_name"] == settings.ai_model_analysis
    assert kwargs["timeout"] == 90
    assert "procedure_stats" in kwargs and "procedure_stats_by_course" in kwargs


# ── FR-016: no exception text ────────────────────────────────────────────────

SECRET = "internal-host-10.0.0.7 key=gsk_leak"


def test_no_response_carries_exception_text(api_client, student_headers, monkeypatch):
    """US2-AS3, FR-016, SC-003: KatIA, the review (network failure, invalid JSON) and a bad
    PDF answer fixed messages."""
    provider = Provider(monkeypatch, reply=RuntimeError(SECRET))
    katia = _katia(api_client, student_headers, "gsk_k1_test")
    review = _review(api_client, student_headers, "gsk_k1_test")
    provider.reply = f"not json {SECRET}"
    invalid = _review(api_client, student_headers, "gsk_k1_test")
    pdf = api_client.post(
        "/api/student/procedure/analyze",
        headers=student_headers,
        data={"item_id": ITEM, "api_key": "gsk_k1_test"},
        files={"file": ("p.pdf", b"%PDF-1.4 broken " + SECRET.encode(), "application/pdf")},
    )

    for response, status in ((katia, 502), (review, 503), (invalid, 502)):
        assert response.status_code == status, response.text
        assert SECRET not in response.text and "gsk_" not in response.text
    assert SECRET not in pdf.text


def test_a_provider_error_string_from_the_analysis_is_not_a_200(
    api_client, teacher_headers, monkeypatch
):
    """FR-016: the analysis's provider error text («ERROR_401: …») becomes a 502."""
    from api.config import settings
    from src.application.services.teacher_service import TeacherService

    monkeypatch.setattr(settings, "system_ai_api_key", "gsk_k1_test")
    monkeypatch.setattr(
        TeacherService,
        "generate_ai_analysis",
        Mock(return_value="ERROR_401: ❌ API Key inválida o expirada para groq."),
    )
    student_id = api_client.get("/api/teacher/dashboard", headers=teacher_headers).json()[
        "students"
    ][0]["user_id"]

    response = api_client.post(
        f"/api/teacher/student/{student_id}/ai-analysis", headers=teacher_headers
    )

    assert response.status_code == 502
    assert "ERROR_401" not in response.text
