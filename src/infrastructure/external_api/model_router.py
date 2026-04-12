"""Model Router — selección automática del modelo óptimo según la tarea.

Mantiene un registro de capacidades por modelo y selecciona el más adecuado
según los requisitos de cada tipo de tarea (tutor socrático, análisis de
procedimiento con imagen, chat general).

El registro es extensible: se pueden agregar modelos con `register_model()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# ── Tipos ────────────────────────────────────────────────────────────────────

TaskType = Literal["tutor_socratic", "image_procedure_analysis", "general_chat"]
SpeedTier = Literal["fast", "medium", "slow"]


@dataclass(frozen=True)
class ModelCapabilities:
    """Capacidades conocidas de un modelo de IA."""

    text: bool = True
    vision: bool = False
    reasoning: bool = False
    speed: SpeedTier = "medium"


# ── Registro configurable de modelos ─────────────────────────────────────────
# Clave: substring que identifica al modelo (case-insensitive).
# Se busca como subcadena dentro del model_id completo.

_MODEL_REGISTRY: dict[str, ModelCapabilities] = {
    # ── Modelos matemáticos sin visión ──
    "qwen2.5-math": ModelCapabilities(vision=False, reasoning=True, speed="fast"),
    "deepseek-r1": ModelCapabilities(vision=False, reasoning=True, speed="medium"),
    # ── Modelos con visión + razonamiento ──
    "qwen2.5-vl": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "qwen-2-vl": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "gpt-4o": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "gpt-4.1": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "gpt-4-turbo": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "claude-sonnet": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "claude-opus": ModelCapabilities(vision=True, reasoning=True, speed="slow"),
    "claude-haiku": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "gemini-2": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "gemini-1.5": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "llama-4": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "llama4": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "mistral-3": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "mistral3": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "ministral-3": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    "pixtral": ModelCapabilities(vision=True, reasoning=True, speed="medium"),
    # ── Modelos con visión pero razonamiento limitado ──
    "gemma-3": ModelCapabilities(vision=True, reasoning=False, speed="fast"),
    "gemma3": ModelCapabilities(vision=True, reasoning=False, speed="fast"),
    "moondream": ModelCapabilities(vision=True, reasoning=False, speed="fast"),
    "minicpm-v": ModelCapabilities(vision=True, reasoning=False, speed="fast"),
    "llava": ModelCapabilities(vision=True, reasoning=False, speed="fast"),
    # ── Modelos de texto rápidos (sin visión) ──
    "llama-3.1-8b": ModelCapabilities(vision=False, reasoning=True, speed="fast"),
    "llama-3.3-70b": ModelCapabilities(vision=False, reasoning=True, speed="medium"),
    "qwen2.5-7b": ModelCapabilities(vision=False, reasoning=True, speed="fast"),
    "qwen2.5-9b": ModelCapabilities(vision=False, reasoning=True, speed="fast"),
    "qwen2.5-14b": ModelCapabilities(vision=False, reasoning=True, speed="medium"),
    "qwen2.5-72b": ModelCapabilities(vision=False, reasoning=True, speed="slow"),
    "gpt-4o-mini": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "gemini-2.0-flash": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "mistral-small": ModelCapabilities(vision=False, reasoning=False, speed="fast"),
}

# ── Capacidades por defecto según proveedor cloud ────────────────────────────
# Se usan cuando el modelo no aparece en el registro explícito.
_PROVIDER_DEFAULTS: dict[str, ModelCapabilities] = {
    "anthropic": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "gemini": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "openai": ModelCapabilities(vision=True, reasoning=True, speed="fast"),
    "groq": ModelCapabilities(vision=False, reasoning=True, speed="fast"),
}


def register_model(keyword: str, capabilities: ModelCapabilities) -> None:
    """Registra o actualiza las capacidades de un modelo en el registry."""
    _MODEL_REGISTRY[keyword.lower()] = capabilities


def detect_model_capabilities(
    model_name: str,
    provider: str | None = None,
) -> ModelCapabilities:
    """Detecta las capacidades de un modelo buscando en el registro.

    Busca coincidencia por subcadena (case-insensitive) en el nombre del modelo.
    Si no hay match, usa los defaults del proveedor. Si tampoco hay proveedor,
    retorna capacidades conservadoras (solo texto).
    """
    if not model_name:
        return _PROVIDER_DEFAULTS.get(provider, ModelCapabilities())

    model_lower = model_name.lower()

    # Buscar el match más largo (más específico) en el registro
    best_match = ""
    best_caps = None
    for keyword, caps in _MODEL_REGISTRY.items():
        if keyword in model_lower and len(keyword) > len(best_match):
            best_match = keyword
            best_caps = caps

    if best_caps is not None:
        return best_caps

    # Sin match explícito → usar defaults del proveedor
    if provider and provider in _PROVIDER_DEFAULTS:
        return _PROVIDER_DEFAULTS[provider]

    # Fallback: detección automática por heurística del nombre
    try:
        from src.infrastructure.external_api.model_capability_detector import (
            detect_capabilities_from_name,
        )

        return detect_capabilities_from_name(model_name)
    except ImportError:
        pass

    # Fallback conservador
    return ModelCapabilities(text=True, vision=False, reasoning=False, speed="medium")


def select_model_for_task(
    task_type: TaskType,
    available_models: list[str],
    current_model: str,
    provider: str | None = None,
) -> str | None:
    """Selecciona el modelo más adecuado para una tarea.

    Args:
        task_type: Tipo de tarea a realizar.
        available_models: Lista de modelos disponibles (puede estar vacía para cloud).
        current_model: Modelo actualmente seleccionado por el usuario.
        provider: Proveedor activo (groq, openai, anthropic, etc.).

    Returns:
        Nombre del modelo seleccionado, o None si no hay candidato válido
        (solo para image_procedure_analysis cuando se requiere visión+razonamiento).
    """
    if task_type == "general_chat":
        return current_model

    # Para proveedores cloud sin lista de modelos, evaluar el modelo actual
    candidates = available_models if available_models else [current_model]

    if task_type == "tutor_socratic":
        return _select_for_socratic(candidates, current_model, provider)

    if task_type == "image_procedure_analysis":
        return _select_for_image_procedure(candidates, current_model, provider)

    return current_model


def _select_for_socratic(
    candidates: list[str],
    current_model: str,
    provider: str | None,
) -> str:
    """Tutor socrático: priorizar modelos rápidos con razonamiento, excluir lentos."""
    # Clasificar candidatos
    fast_reasoning = []
    any_reasoning = []

    for model in candidates:
        caps = detect_model_capabilities(model, provider)
        if caps.reasoning and caps.speed == "fast":
            fast_reasoning.append(model)
        elif caps.reasoning and caps.speed != "slow":
            any_reasoning.append(model)

    # Mejor opción: rápido + razonamiento
    if fast_reasoning:
        # Si el modelo actual ya es fast+reasoning, mantenerlo
        if current_model in fast_reasoning:
            return current_model
        return fast_reasoning[0]

    # Segunda opción: cualquiera con razonamiento
    if any_reasoning:
        if current_model in any_reasoning:
            return current_model
        return any_reasoning[0]

    # Fallback: usar el modelo actual
    return current_model


def _select_for_image_procedure(
    candidates: list[str],
    current_model: str,
    provider: str | None,
) -> str | None:
    """Análisis de procedimiento con imagen: requiere visión + razonamiento."""
    valid = []

    for model in candidates:
        caps = detect_model_capabilities(model, provider)
        if caps.vision and caps.reasoning:
            valid.append(model)

    if not valid:
        # No hay modelo con visión+razonamiento → retorna None
        # para que la capa de UI envíe a revisión manual del profesor
        return None

    # Si el modelo actual ya cumple, mantenerlo
    if current_model in valid:
        return current_model

    return valid[0]


# ── Validación socrática ─────────────────────────────────────────────────────

# Indicadores de que la respuesta viola las reglas del tutor socrático
_SOCRATIC_VIOLATION_PATTERNS = [
    "la respuesta correcta es",
    "la respuesta es",
    "la solución es",
    "el resultado es",
    "la opción correcta es",
    "debes elegir",
    "la respuesta correcta sería",
    "primero derivamos",
    "primero calculamos",
    "resolvemos paso a paso",
    "paso 1:",
    "paso 2:",
    "paso 3:",
]

# Máximo de oraciones permitidas en la respuesta socrática
_SOCRATIC_MAX_SENTENCES = 5


def validate_socratic_response(response: str) -> bool:
    """Valida que la respuesta del tutor socrático no viole las reglas.

    Retorna True si la respuesta es válida (socrática), False si viola las reglas.
    """
    if not response:
        return True

    response_lower = response.lower().strip()

    # Verificar patrones de violación (revela solución o procedimiento)
    for pattern in _SOCRATIC_VIOLATION_PATTERNS:
        if pattern in response_lower:
            return False

    # Contar oraciones (separadas por . ! ?)
    import re

    sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]
    if len(sentences) > _SOCRATIC_MAX_SENTENCES:
        return False

    return True


# Prompt correctivo para regenerar respuestas que violan las reglas
SOCRATIC_CORRECTION_PROMPT = (
    "Tu respuesta anterior violó las reglas del tutor socrático. "
    "No reveles la solución. Solo formula preguntas breves que guíen al estudiante. "
    "Máximo 3-5 oraciones, todas deben ser preguntas o pistas breves."
)

# Límite de tokens para respuestas del tutor socrático (optimización de latencia)
SOCRATIC_MAX_TOKENS = 120
