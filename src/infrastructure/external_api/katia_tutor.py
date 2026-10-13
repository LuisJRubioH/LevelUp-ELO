"""
KatIA's model access (spec 005, research R6, R7).

- ``resolve_route`` decides where a key may go. The system key goes where the server's
  configuration says — ``SYSTEM_AI_PROVIDER`` or, when empty, the key's prefix — and never where
  the browser asks (FR-027, FR-028). A student's own key goes to the provider its prefix names,
  or, for an unrecognised prefix, to the cloud provider the student chose (FR-029). Local
  providers (LM Studio, Ollama) are never a destination: the API's localhost is not the
  student's machine.
- ``ProviderTutor`` asks the model for at most the configured output tokens (FR-031), reports a
  reply the limit cut (FR-032), and turns any SDK failure into ``TutorUnavailable`` with a code —
  never the SDK's text, which can quote the key (FR-030).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import anthropic
from openai import OpenAI

from src.application.interfaces.tutor import TutorCompletion, TutorUnavailable
from src.infrastructure.external_api.ai_client import PROVIDERS, detect_provider_from_key
from src.utils import strip_thinking_tags

logger = logging.getLogger("katia.tutor")

LOCAL_PROVIDERS = frozenset({"lmstudio", "ollama"})
_ALIASES = {"google": "gemini", "claude": "anthropic"}
TIMEOUT_SECONDS = 30.0
TEMPERATURE = 0.3


@dataclass(frozen=True)
class Route:
    provider: str
    model: str
    base_url: str | None


class RouteError(Exception):
    """No valid destination for the key. `code` is safe to log and to map to a response."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _name(provider: str) -> str:
    name = (provider or "").strip().lower()
    return _ALIASES.get(name, name)


def resolve_route(
    api_key: str,
    *,
    own_key: bool,
    configured_provider: str = "",
    requested_provider: str = "",
) -> Route:
    detected = detect_provider_from_key((api_key or "").strip())
    if own_key:
        requested = _name(requested_provider)
        provider = detected or (
            requested if requested in PROVIDERS and requested not in LOCAL_PROVIDERS else None
        )
        if not provider:
            raise RouteError("unknown_provider")
    else:
        configured = _name(configured_provider)
        if configured in LOCAL_PROVIDERS:
            raise RouteError("local_provider")
        if configured:
            if configured not in PROVIDERS:
                raise RouteError("unknown_provider")
            if detected and detected != configured:
                raise RouteError("provider_mismatch")
            provider = configured
        else:
            provider = detected
            if not provider:
                raise RouteError("unknown_provider")
    config = PROVIDERS[provider]
    if not config.get("model_cog"):
        raise RouteError("no_model")
    return Route(provider=provider, model=config["model_cog"], base_url=config.get("base_url"))


def _failure_code(exc: Exception) -> str:
    name = type(exc).__name__
    status = getattr(exc, "status_code", None)
    if name in ("AuthenticationError", "PermissionDeniedError") or status in (401, 403):
        return "auth"
    if name == "RateLimitError" or status == 429:
        return "rate_limited"
    if "Timeout" in name:
        return "timeout"
    return "provider_error"


class ProviderTutor:
    """`ITutor` over the provider SDKs (OpenAI-compatible APIs and Anthropic)."""

    def __init__(
        self, route: Route, api_key: str, max_tokens: int, timeout: float = TIMEOUT_SECONDS
    ):
        self.route = route
        self._api_key = api_key
        self.max_tokens = max_tokens
        self.timeout = timeout

    def complete(self, system: str, messages: list) -> TutorCompletion:
        try:
            if self.route.provider == "anthropic":
                return self._anthropic(system, messages)
            return self._openai_compatible(system, messages)
        except Exception as exc:
            code = _failure_code(exc)
            # The provider and the exception's class only: its message can quote the key.
            logger.warning(
                "KatIA: provider %s failed (%s, %s)", self.route.provider, code, type(exc).__name__
            )
            raise TutorUnavailable(code) from None

    def _openai_compatible(self, system: str, messages: list) -> TutorCompletion:
        client = OpenAI(
            api_key=self._api_key,
            base_url=self.route.base_url,
            timeout=self.timeout,
            max_retries=1,
        )
        response = client.chat.completions.create(
            model=self.route.model,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=TEMPERATURE,
            max_tokens=self.max_tokens,
        )
        choice = response.choices[0]
        usage = getattr(response, "usage", None)
        return TutorCompletion(
            text=strip_thinking_tags(choice.message.content or ""),
            truncated=choice.finish_reason == "length",
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )

    def _anthropic(self, system: str, messages: list) -> TutorCompletion:
        client = anthropic.Anthropic(api_key=self._api_key, timeout=self.timeout, max_retries=1)
        response = client.messages.create(
            model=self.route.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            temperature=TEMPERATURE,
        )
        usage = getattr(response, "usage", None)
        return TutorCompletion(
            text=strip_thinking_tags("".join(getattr(b, "text", "") for b in response.content)),
            truncated=response.stop_reason == "max_tokens",
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
        )
