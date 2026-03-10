"""Extracción estructurada de pasos matemáticos desde texto OCR o LaTeX.

Analiza texto matemático y lo descompone en pasos secuenciales,
identificando el tipo de cada paso (ecuación, simplificación, sustitución, etc.).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

StepType = Literal[
    "equation",
    "simplification",
    "substitution",
    "factoring",
    "derivative",
    "integral",
    "limit",
    "definition",
    "unknown",
]


@dataclass
class MathStep:
    """Un paso individual del procedimiento matemático."""
    step: int
    expression: str
    step_type: StepType = "unknown"
    raw_line: str = ""


# ── Separadores de pasos ─────────────────────────────────────────────────────

# Patrón para detectar separadores entre pasos
_STEP_SEPARATORS = re.compile(
    r'(?:'
    r'\n\s*\n'           # doble salto de línea
    r'|(?<=\S)\s*→\s*'   # flecha →
    r'|(?<=\S)\s*⇒\s*'   # flecha ⇒
    r'|(?<=\S)\s*\\to\s*' # \to (LaTeX)
    r'|(?<=\S)\s*\\Rightarrow\s*'  # \Rightarrow (LaTeX)
    r'|\n\s*(?=\d+[\.\)]\s)'  # numeración explícita (1. o 1))
    r'|\n\s*(?=(?i:paso)\s+\d+)'  # "Paso N" (case-insensitive)
    r')',
)

# Patrón para limpiar prefijos de numeración
_NUMBERING_PREFIX = re.compile(r'^\s*(?:paso\s+)?(\d+)[\.\):\-]\s*', re.IGNORECASE)


# ── Clasificadores de tipo de paso ───────────────────────────────────────────

_TYPE_PATTERNS: list[tuple[StepType, re.Pattern]] = [
    ("derivative", re.compile(r"(?:d/d[a-z]|f'|\\frac\{d\}|\\partial|derivad)", re.IGNORECASE)),
    ("integral", re.compile(r"(?:\\int|∫|integral)", re.IGNORECASE)),
    ("limit", re.compile(r"(?:\\lim|lim\s|límite)", re.IGNORECASE)),
    ("factoring", re.compile(r"(?:factor|factori)", re.IGNORECASE)),
    ("substitution", re.compile(r"(?:sustitu|sustituy|reemplaz|replac)", re.IGNORECASE)),
    ("simplification", re.compile(r"(?:simplific|reduc|combin|cancel)", re.IGNORECASE)),
    ("equation", re.compile(r"=")),
]


def _classify_step(expression: str, raw_line: str = "") -> StepType:
    """Clasifica el tipo de un paso matemático."""
    text = f"{raw_line} {expression}".lower()
    for step_type, pattern in _TYPE_PATTERNS:
        if pattern.search(text):
            return step_type
    return "unknown"


def _split_by_equals(text: str) -> list[str]:
    """Divide texto en líneas separadas por '=', preservando ecuaciones completas."""
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            result.append(stripped)
    return result


def extract_steps(text: str) -> list[MathStep]:
    """Extrae una lista estructurada de pasos matemáticos desde texto.

    Analiza el texto buscando separadores naturales (saltos de línea,
    flechas, numeración) y clasifica cada paso.

    Args:
        text: Texto con procedimiento matemático (puede contener LaTeX).

    Returns:
        Lista ordenada de MathStep. Lista vacía si no se detectan pasos.
    """
    if not text or not text.strip():
        return []

    # Intentar separar por patrones conocidos
    parts = _STEP_SEPARATORS.split(text)

    # Si solo hay una parte, intentar separar por líneas
    if len(parts) <= 1:
        parts = _split_by_equals(text)

    steps = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part or len(part) < 2:
            continue

        # Limpiar prefijo de numeración
        clean = _NUMBERING_PREFIX.sub('', part).strip()
        if not clean:
            clean = part

        step = MathStep(
            step=len(steps) + 1,
            expression=clean,
            step_type=_classify_step(clean, part),
            raw_line=part,
        )
        steps.append(step)

    return steps


def extract_steps_from_llm_transcription(transcription: str, pasos: list[dict]) -> list[MathStep]:
    """Extrae pasos desde la transcripción estructurada de un LLM.

    Compatible con el formato JSON de review_math_procedure():
    {"numero": 1, "contenido": "...", "evaluacion": "...", "comentario": "..."}

    Args:
        transcription: Transcripción completa del procedimiento.
        pasos: Lista de pasos del JSON del LLM.

    Returns:
        Lista de MathStep. Si pasos está vacío, intenta extraer de la transcripción.
    """
    if pasos:
        steps = []
        for p in pasos:
            contenido = p.get("contenido", "")
            steps.append(MathStep(
                step=p.get("numero", len(steps) + 1),
                expression=contenido,
                step_type=_classify_step(contenido),
                raw_line=contenido,
            ))
        return steps

    # Fallback: extraer de la transcripción directa
    return extract_steps(transcription)
