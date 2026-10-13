"""
Spec 005 (block 6): where KatIA's request goes and how the model's reply comes back.

Provider routing (FR-027 … FR-029), the output limit (FR-031), truncation (FR-032) and failures
that never carry the key (FR-030). The SDK clients are replaced by fakes: nothing leaves the test.
"""

import logging
from types import SimpleNamespace

import pytest

from src.application.interfaces.tutor import TutorUnavailable
from src.infrastructure.external_api import katia_tutor
from src.infrastructure.external_api.katia_tutor import ProviderTutor, RouteError, resolve_route

SECRET = "gsk_SECRET_do_not_log_123"


# ── Routing with the system key (FR-027, FR-028) ─────────────────────────────


@pytest.mark.parametrize(
    "configured, key, provider",
    [
        ("", "gsk_system", "groq"),
        ("", "sk-ant-system", "anthropic"),
        ("anthropic", "sk-ant-system", "anthropic"),
        ("google", "AIzaSySystem", "gemini"),
        ("Groq", "gsk_system", "groq"),
    ],
)
def test_spec005_system_key_goes_where_the_server_says(configured, key, provider):
    route = resolve_route(
        key, own_key=False, configured_provider=configured, requested_provider="openai"
    )

    assert route.provider == provider
    assert route.model == katia_tutor.PROVIDERS[provider]["model_cog"]
    assert route.base_url == katia_tutor.PROVIDERS[provider]["base_url"]


@pytest.mark.parametrize(
    "configured, key, code",
    [
        ("openai", "gsk_system", "provider_mismatch"),
        ("lmstudio", "gsk_system", "local_provider"),
        ("ollama", "", "local_provider"),
        ("deepthought", "gsk_system", "unknown_provider"),
        ("", "no-prefix-key", "unknown_provider"),
    ],
)
def test_spec005_an_invalid_system_configuration_sends_the_key_nowhere(configured, key, code):
    with pytest.raises(RouteError) as error:
        resolve_route(key, own_key=False, configured_provider=configured, requested_provider="groq")

    assert error.value.code == code


# ── Routing with the student's own key (FR-029) ──────────────────────────────


@pytest.mark.parametrize(
    "key, requested, provider",
    [
        ("sk-ant-student", "groq", "anthropic"),
        ("gsk_student", "", "groq"),
        ("custom-student-key", "openai", "openai"),
        ("custom-student-key", "Gemini", "gemini"),
    ],
)
def test_spec005_a_students_key_goes_only_to_its_provider(key, requested, provider):
    route = resolve_route(
        key, own_key=True, configured_provider="anthropic", requested_provider=requested
    )

    assert route.provider == provider


@pytest.mark.parametrize("requested", ["", "ollama", "lmstudio", "skynet"])
def test_spec005_a_students_unrecognised_key_needs_a_cloud_provider(requested):
    with pytest.raises(RouteError) as error:
        resolve_route("custom-student-key", own_key=True, requested_provider=requested)

    assert error.value.code == "unknown_provider"


# ── The tutor client (FR-030 … FR-032) ───────────────────────────────────────


class _FakeOpenAI:
    created = []
    calls = []
    reply = None

    def __init__(self, **kwargs):
        _FakeOpenAI.created.append(kwargs)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        _FakeOpenAI.calls.append(kwargs)
        if isinstance(_FakeOpenAI.reply, Exception):
            raise _FakeOpenAI.reply
        return _FakeOpenAI.reply


def _openai_reply(text, finish_reason="stop"):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content=text), finish_reason=finish_reason)
        ],
        usage=SimpleNamespace(prompt_tokens=310, completion_tokens=42),
    )


@pytest.fixture
def fake_openai(monkeypatch):
    _FakeOpenAI.created, _FakeOpenAI.calls, _FakeOpenAI.reply = [], [], _openai_reply("¿Qué ves?")
    monkeypatch.setattr(katia_tutor, "OpenAI", _FakeOpenAI)
    return _FakeOpenAI


def _tutor(provider="groq", key=SECRET, max_tokens=120):
    return ProviderTutor(
        resolve_route(key, own_key=True, requested_provider=provider), key, max_tokens
    )


def test_spec005_the_model_is_asked_for_the_configured_output_limit(fake_openai):
    completion = _tutor().complete("instrucciones", [{"role": "user", "content": "hola"}])

    call = fake_openai.calls[0]
    assert call["max_tokens"] == 120
    assert call["model"] == katia_tutor.PROVIDERS["groq"]["model_cog"]
    assert call["messages"][0] == {"role": "system", "content": "instrucciones"}
    assert call["messages"][1:] == [{"role": "user", "content": "hola"}]
    assert fake_openai.created[0]["base_url"] == katia_tutor.PROVIDERS["groq"]["base_url"]
    assert completion.text == "¿Qué ves?" and completion.truncated is False
    assert (completion.input_tokens, completion.output_tokens) == (310, 42)


def test_spec005_a_reply_cut_by_the_limit_is_flagged(fake_openai):
    fake_openai.reply = _openai_reply(
        "<think>plan</think>¿Qué función está", finish_reason="length"
    )

    completion = _tutor().complete("s", [{"role": "user", "content": "m"}])

    assert completion.truncated is True and completion.text == "¿Qué función está"


def test_spec005_anthropic_replies_report_truncation(monkeypatch):
    calls = []

    class _Messages:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                content=[SimpleNamespace(text="¿Cuál es la función interna?")],
                stop_reason="max_tokens",
                usage=SimpleNamespace(input_tokens=200, output_tokens=120),
            )

    monkeypatch.setattr(
        katia_tutor.anthropic, "Anthropic", lambda **kwargs: SimpleNamespace(messages=_Messages())
    )

    completion = _tutor("anthropic", key="sk-ant-x", max_tokens=120).complete(
        "s", [{"role": "user", "content": "m"}]
    )

    assert calls[0]["max_tokens"] == 120 and calls[0]["system"] == "s"
    assert completion.truncated is True and completion.output_tokens == 120


class AuthenticationError(Exception):
    pass


class RateLimitError(Exception):
    pass


class APITimeoutError(Exception):
    pass


@pytest.mark.parametrize(
    "failure, code",
    [
        (AuthenticationError(f"Incorrect API key provided: {SECRET}"), "auth"),
        (RateLimitError(f"rate limited for key {SECRET}"), "rate_limited"),
        (APITimeoutError("timed out"), "timeout"),
        (RuntimeError(f"upstream 500 for {SECRET}"), "provider_error"),
    ],
)
def test_spec005_a_failure_carries_a_code_and_never_the_key(fake_openai, caplog, failure, code):
    fake_openai.reply = failure
    caplog.set_level(logging.DEBUG)

    with pytest.raises(TutorUnavailable) as raised:
        _tutor().complete("s", [{"role": "user", "content": "m"}])

    assert raised.value.code == code
    assert SECRET not in str(raised.value)
    assert raised.value.__cause__ is None and raised.value.__suppress_context__
    assert SECRET not in caplog.text
