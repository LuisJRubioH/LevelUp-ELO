"""Detección automática de capacidades de modelos desde servidores OpenAI-compatibles.

Consulta GET /v1/models y aplica heurísticas sobre el nombre del modelo
para inferir: visión, razonamiento y velocidad estimada.

Se usa como fallback cuando el modelo no está en el registro manual de model_router.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

# Reusar el dataclass del router para mantener consistencia
from src.infrastructure.external_api.model_router import ModelCapabilities


# ── Heurísticas de detección ─────────────────────────────────────────────────

# Keywords que indican soporte de visión (case-insensitive)
_VISION_KEYWORDS = [
    "vision",
    "vl",
    "gpt-4o",
    "gpt-4.1",
    "llava",
    "qwen-vl",
    "qwen2-vl",
    "qwen2.5-vl",
    "moondream",
    "fuyu",
    "minicpm-v",
    "pixtral",
    "gemma-3",
    "gemma3",
    "llama-4",
    "llama4",
    "mistral-3",
    "mistral3",
    "internvl",
    "cogvlm",
    "phi-3-vision",
    "phi-4-vision",
    "molmo",
    "ovis",
    "idefics",
    "deepseek-vl",
]

# Keywords que indican capacidad de razonamiento matemático
_REASONING_KEYWORDS = [
    "math",
    "instruct",
    "reason",
    "-r1",
    "-r2",
    "deepseek",
    "qwen",
    "gpt-4",
    "gpt-3.5",
    "llama-3",
    "llama-4",
    "mistral",
    "mixtral",
    "gemma",
    "phi-3",
    "phi-4",
    "claude",
]

# Keywords de exclusión para razonamiento (modelos demasiado simples)
_REASONING_EXCLUSIONS = [
    "embed",
    "embedding",
    "tts",
    "whisper",
    "dall-e",
    "text-to-speech",
    "moderation",
]

# Keywords de exclusión para visión (falsos positivos conocidos)
_VISION_EXCLUSIONS = [
    "qwen2.5-math",
    "qwen2.5-coder",
    "gemma-3-1b",
]

# Regex para extraer tamaño del modelo en billones de parámetros
_SIZE_PATTERN = re.compile(r"(\d+\.?\d*)[bB]")
# Patrón MoE: "8x7b" → interpreta como >14b efectivo
_MOE_PATTERN = re.compile(r"(\d+)x(\d+\.?\d*)[bB]", re.IGNORECASE)
# Nombres conocidos de modelos lentos (MoE o muy grandes)
_SLOW_KEYWORDS = ["mixtral", "110b", "70b", "72b", "65b"]


def _estimate_speed(model_name: str) -> Literal["fast", "medium", "slow"]:
    """Estima la velocidad del modelo según el tamaño en parámetros."""
    model_lower = model_name.lower()

    # Modelos conocidos como lentos
    if any(kw in model_lower for kw in _SLOW_KEYWORDS):
        return "slow"

    # Patrón MoE: NxMb (ej: 8x7b) → considerar lento
    if _MOE_PATTERN.search(model_name):
        return "slow"

    match = _SIZE_PATTERN.search(model_name)
    if not match:
        return "medium"

    size_b = float(match.group(1))
    if size_b <= 9:
        return "fast"
    elif size_b <= 14:
        return "medium"
    else:
        return "slow"


def _has_vision(model_name: str) -> bool:
    """Determina si el modelo tiene visión por heurística de nombre."""
    model_lower = model_name.lower()

    # Verificar exclusiones primero
    if any(ex in model_lower for ex in _VISION_EXCLUSIONS):
        return False

    return any(kw in model_lower for kw in _VISION_KEYWORDS)


def _has_reasoning(model_name: str) -> bool:
    """Determina si el modelo tiene razonamiento suficiente por heurística."""
    model_lower = model_name.lower()

    # Exclusiones: modelos que no son de texto generativo
    if any(ex in model_lower for ex in _REASONING_EXCLUSIONS):
        return False

    return any(kw in model_lower for kw in _REASONING_KEYWORDS)


def detect_capabilities_from_name(model_name: str) -> ModelCapabilities:
    """Infiere las capacidades de un modelo a partir de su nombre.

    Esta función aplica heurísticas y NO debe usarse como fuente primaria.
    El registro manual en model_router.py siempre tiene prioridad.

    Args:
        model_name: ID del modelo (ej: "qwen2.5-vl-7b-instruct").

    Returns:
        ModelCapabilities inferidas por heurística.
    """
    if not model_name:
        return ModelCapabilities()

    return ModelCapabilities(
        text=True,
        vision=_has_vision(model_name),
        reasoning=_has_reasoning(model_name),
        speed=_estimate_speed(model_name),
    )


def detect_all_capabilities(
    base_url: str = "http://localhost:1234/v1",
) -> dict[str, ModelCapabilities]:
    """Consulta GET /v1/models y retorna capacidades inferidas para cada modelo.

    Útil para poblar el detector automáticamente al conectar con
    LM Studio, Ollama, o cualquier servidor OpenAI-compatible.

    Args:
        base_url: URL base del servidor (sin /models al final).

    Returns:
        Dict {model_id: ModelCapabilities} con todos los modelos detectados.
        Dict vacío si el servidor no responde.
    """
    import requests

    try:
        response = requests.get(
            f"{base_url.rstrip('/')}/models",
            timeout=5,
        )
        if response.status_code != 200:
            return {}

        data = response.json()
        models = [m["id"] for m in data.get("data", [])]
    except Exception:
        return {}

    return {model_id: detect_capabilities_from_name(model_id) for model_id in models}
