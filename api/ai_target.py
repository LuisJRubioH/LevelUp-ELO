"""
Spec 005 delivery K1 (FR-010 … FR-013, FR-016): which provider, model and timeout an AI feature
uses, and the fixed messages a failure shows.

The key's prefix picks the provider — the browser chooses neither provider nor model. A Groq key
(the production provider) uses the model the function's setting names; another provider's key
uses that provider's entry in `ai_client.PROVIDERS`. Composition layer: it reads settings and the
infrastructure's provider table.
"""

from typing import NamedTuple

from fastapi import HTTPException, status

from api.config import settings

UNKNOWN_KEY = (
    "Clave no reconocida: usa una de Groq (gsk_), Anthropic (sk-ant-), OpenAI (sk-), "
    "Gemini (AIzaSy) o HuggingFace (hf_)."
)
TIMED_OUT = "La IA no respondió a tiempo. Intenta de nuevo."
UNAVAILABLE = "La IA no está disponible ahora. Intenta de nuevo en un momento."
GROQ_ONLY = "La revisión con IA usa Groq"  # FR-014: the interface shows the same sentence

# FR-013: seconds a provider call may take, per function.
TIMEOUTS = {"katia": 30, "procedure": 90, "teacher_analysis": 90}
_CLOUD = ("groq", "anthropic", "openai", "gemini", "huggingface")


class AITarget(NamedTuple):
    provider: str
    base_url: str
    model: str
    api_key: str
    timeout: float


def ai_target(function: str, key: str) -> AITarget:
    """The provider, model and timeout for `function` with `key`; 422 for an unknown prefix."""
    from src.infrastructure.external_api.ai_client import PROVIDERS, detect_provider_from_key

    provider = detect_provider_from_key(key)
    if provider not in _CLOUD:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=UNKNOWN_KEY)
    config = PROVIDERS[provider]
    if provider == "groq":
        model = {
            "katia": settings.ai_model_katia,
            "procedure": settings.ai_model_vision,
            "teacher_analysis": settings.ai_model_analysis,
        }[function]
    else:
        model = config["model_analysis" if function == "teacher_analysis" else "model_cog"]
    return AITarget(provider, config["base_url"] or "", model, key, TIMEOUTS[function])
