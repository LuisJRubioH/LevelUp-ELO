"""Pipeline de análisis matemático automático.

Orquesta el flujo completo:
    imagen → OCR → extracción de pasos → verificación simbólica → feedback

Cada etapa tiene fallback independiente. Si todo el pipeline falla,
retorna None para que la capa de UI use el análisis por LLM existente.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from src.infrastructure.external_api.math_ocr import (
    OCRResult,
    extract_math_from_image,
    extract_math_from_text,
)
from src.infrastructure.external_api.symbolic_math_verifier import (
    compare_steps,
    is_available as sympy_available,
    ErrorType,
)


# ── Step extraction ───────────────────────────────────────────────────────────

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


_STEP_SEPARATORS = re.compile(
    r"(?:"
    r"\n\s*\n"
    r"|(?<=\S)\s*→\s*"
    r"|(?<=\S)\s*⇒\s*"
    r"|(?<=\S)\s*\\to\s*"
    r"|(?<=\S)\s*\\Rightarrow\s*"
    r"|\n\s*(?=\d+[\.\)]\s)"
    r"|\n\s*(?=(?i:paso)\s+\d+)"
    r")",
)

_NUMBERING_PREFIX = re.compile(r"^\s*(?:paso\s+)?(\d+)[\.\):\-]\s*", re.IGNORECASE)

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
    text = f"{raw_line} {expression}".lower()
    for step_type, pattern in _TYPE_PATTERNS:
        if pattern.search(text):
            return step_type
    return "unknown"


def _split_by_equals(text: str) -> list[str]:
    return [line.strip() for line in text.split("\n") if line.strip()]


def extract_steps(text: str) -> list[MathStep]:
    """Extrae pasos matemáticos estructurados desde texto."""
    if not text or not text.strip():
        return []

    parts = _STEP_SEPARATORS.split(text)
    if len(parts) <= 1:
        parts = _split_by_equals(text)

    steps = []
    for part in parts:
        part = part.strip()
        if not part or len(part) < 2:
            continue
        clean = _NUMBERING_PREFIX.sub("", part).strip() or part
        steps.append(
            MathStep(
                step=len(steps) + 1,
                expression=clean,
                step_type=_classify_step(clean, part),
                raw_line=part,
            )
        )
    return steps


def extract_steps_from_llm_transcription(transcription: str, pasos: list[dict]) -> list[MathStep]:
    """Extrae pasos desde la transcripción estructurada de un LLM."""
    if pasos:
        steps = []
        for p in pasos:
            contenido = p.get("contenido", "")
            steps.append(
                MathStep(
                    step=p.get("numero", len(steps) + 1),
                    expression=contenido,
                    step_type=_classify_step(contenido),
                    raw_line=contenido,
                )
            )
        return steps
    return extract_steps(transcription)


# ── Step analysis ─────────────────────────────────────────────────────────────


@dataclass
class StepAnalysis:
    """Resultado del análisis de un paso individual."""

    step: int
    expression: str
    valid: bool
    error_type: ErrorType = "none"
    feedback: str = ""


@dataclass
class ProcedureAnalysis:
    """Resultado completo del análisis de un procedimiento."""

    steps: list[StepAnalysis] = field(default_factory=list)
    total_steps: int = 0
    valid_steps: int = 0
    invalid_steps: int = 0
    score: int = 0
    sympy_used: bool = False
    summary: str = ""


_ERROR_MESSAGES: dict[ErrorType, str] = {
    "none": "",
    "incorrect_distributive": "Error en la propiedad distributiva. Verifica cómo distribuyes los factores.",
    "unlike_terms_combined": "Se combinaron términos que no son semejantes. Solo puedes sumar/restar términos con la misma variable y exponente.",
    "sign_error": "Error de signo. Revisa los signos al transponer términos o al multiplicar/dividir por negativos.",
    "fraction_simplification": "La fracción no se simplificó correctamente. Verifica el MCD del numerador y denominador.",
    "algebraic_error": "Error algebraico. La transformación no preserva la igualdad.",
    "not_equivalent": "El resultado de este paso no es equivalente al anterior.",
    "parse_error": "No se pudo verificar automáticamente esta expresión.",
    "unavailable": "Verificación simbólica no disponible.",
}


def analyze_steps(steps: list[MathStep]) -> ProcedureAnalysis:
    """Analiza una secuencia de pasos matemáticos."""
    if not steps:
        return ProcedureAnalysis(summary="No se detectaron pasos en el procedimiento.")

    analysis = ProcedureAnalysis(total_steps=len(steps), sympy_used=sympy_available())

    analysis.steps.append(
        StepAnalysis(
            step=steps[0].step,
            expression=steps[0].expression,
            valid=True,
            feedback="Expresión inicial del procedimiento.",
        )
    )
    analysis.valid_steps = 1

    for i in range(1, len(steps)):
        result = compare_steps(steps[i - 1].expression, steps[i].expression)
        sa = StepAnalysis(
            step=steps[i].step,
            expression=steps[i].expression,
            valid=result.valid,
            error_type=result.error_type,
            feedback=_ERROR_MESSAGES.get(result.error_type, ""),
        )
        if result.valid:
            sa.feedback = (
                "Paso no verificable automáticamente."
                if result.error_type in ("parse_error", "unavailable")
                else "Transformación algebraica correcta."
            )
            analysis.valid_steps += 1
        else:
            analysis.invalid_steps += 1
        analysis.steps.append(sa)

    base_score = (analysis.valid_steps / analysis.total_steps) * 100
    conceptual_errors = sum(
        1
        for s in analysis.steps
        if s.error_type in ("sign_error", "incorrect_distributive", "unlike_terms_combined")
    )
    analysis.score = max(0, min(100, int(base_score - conceptual_errors * 10)))

    if analysis.invalid_steps == 0:
        analysis.summary = "Todos los pasos son algebraicamente correctos."
    else:
        error_nums = ", ".join(str(s.step) for s in analysis.steps if not s.valid)
        analysis.summary = (
            f"Se detectaron {analysis.invalid_steps} error(es) en los pasos: {error_nums}."
        )

    return analysis


# ── Pedagogical feedback ──────────────────────────────────────────────────────

_SOCRATIC_HINTS: dict[ErrorType, list[str]] = {
    "incorrect_distributive": [
        "Revisa el paso {step}. ¿Qué ocurre cuando multiplicas cada término dentro del paréntesis?",
        "En el paso {step}, ¿aplicaste la distributiva a TODOS los términos?",
    ],
    "unlike_terms_combined": [
        "Revisa el paso {step}. ¿Qué condiciones deben cumplir dos términos para poder sumarlos?",
        "En el paso {step}, ¿los términos que combinaste tienen la misma variable y exponente?",
    ],
    "sign_error": [
        "Revisa el paso {step}. ¿Qué pasa con el signo cuando mueves un término al otro lado de la ecuación?",
        "En el paso {step}, ¿verificaste los signos después de la operación?",
    ],
    "fraction_simplification": [
        "Revisa el paso {step}. ¿Cuál es el máximo común divisor del numerador y denominador?",
        "En el paso {step}, ¿simplificaste correctamente la fracción?",
    ],
    "algebraic_error": [
        "Revisa el paso {step}. ¿La operación que aplicaste preserva la igualdad?",
        "En el paso {step}, verifica que la transformación sea algebraicamente válida.",
    ],
    "not_equivalent": [
        "El paso {step} no parece seguir del anterior. ¿Puedes verificar la operación aplicada?",
        "Revisa el paso {step}. ¿Qué operación realizaste para llegar a esta expresión?",
    ],
}

_DEFAULT_HINT = "Revisa cuidadosamente el paso {step}. ¿Cada operación que realizaste es correcta?"


def _get_hint(error_type: ErrorType, step_num: int) -> str:
    hints = _SOCRATIC_HINTS.get(error_type, [_DEFAULT_HINT])
    return hints[step_num % len(hints)].format(step=step_num)


def generate_feedback(analysis: ProcedureAnalysis) -> str:
    """Genera feedback pedagógico completo. No revela la respuesta final."""
    if not analysis.steps:
        return (
            "No se detectaron pasos en tu procedimiento. Intenta mostrar tu desarrollo paso a paso."
        )

    lines: list[str] = []
    if analysis.invalid_steps == 0:
        lines.append("**Excelente trabajo.** Tu procedimiento es algebraicamente correcto.")
        lines.append("")
        lines.append(f"Se verificaron {analysis.total_steps} pasos correctamente.")
    else:
        lines.append(
            f"Tu procedimiento tiene {analysis.invalid_steps} paso(s) que necesitan revisión "
            f"de un total de {analysis.total_steps}."
        )
        lines.append("")

    for sa in (s for s in analysis.steps if not s.valid):
        lines.append(f"**Paso {sa.step}:** `{sa.expression}`")
        lines.append(f"- {sa.feedback}")
        lines.append(f"- **Pista:** {_get_hint(sa.error_type, sa.step)}")
        lines.append("")

    if analysis.sympy_used:
        lines.append(f"**Puntuación automática:** {analysis.score}/100")

    return "\n".join(lines)


def generate_step_feedback(step_analysis: StepAnalysis) -> str:
    """Genera feedback para un paso individual."""
    if step_analysis.valid:
        return (
            "Paso no verificable automáticamente."
            if step_analysis.error_type in ("parse_error", "unavailable")
            else "Correcto."
        )
    return f"{step_analysis.feedback} {_get_hint(step_analysis.error_type, step_analysis.step)}"


# ── Pipeline ──────────────────────────────────────────────────────────────────


@dataclass
class PipelineResult:
    """Resultado completo del pipeline de análisis."""

    ocr: OCRResult | None = None
    steps: list[MathStep] = field(default_factory=list)
    analysis: ProcedureAnalysis | None = None
    feedback: str = ""
    score: int | None = None
    pipeline_stage_reached: str = "none"
    errors: list[str] = field(default_factory=list)


def analyze(
    image_bytes: bytes | None = None,
    transcription: str | None = None,
    llm_pasos: list[dict] | None = None,
) -> PipelineResult | None:
    """Ejecuta el pipeline de análisis matemático."""
    result = PipelineResult()

    if image_bytes:
        try:
            ocr_result = extract_math_from_image(image_bytes)
            if ocr_result:
                result.ocr = ocr_result
                result.pipeline_stage_reached = "ocr"
        except Exception as exc:
            result.errors.append(f"OCR falló: {exc}")

    if result.ocr is None and transcription:
        result.ocr = extract_math_from_text(transcription)
        result.pipeline_stage_reached = "ocr_from_text"

    if result.ocr is None and not llm_pasos:
        return None

    try:
        if llm_pasos:
            result.steps = extract_steps_from_llm_transcription(transcription or "", llm_pasos)
            result.pipeline_stage_reached = "steps_from_llm"
        elif result.ocr:
            result.steps = extract_steps(result.ocr.raw_text)
            result.pipeline_stage_reached = "steps"
    except Exception as exc:
        result.errors.append(f"Extracción de pasos falló: {exc}")

    if not result.steps:
        result.feedback = "No se pudieron extraer pasos del procedimiento."
        return result

    try:
        result.analysis = analyze_steps(result.steps)
        result.pipeline_stage_reached = "analysis"
        result.score = result.analysis.score
    except Exception as exc:
        result.errors.append(f"Verificación simbólica falló: {exc}")

    try:
        if result.analysis:
            result.feedback = generate_feedback(result.analysis)
            result.pipeline_stage_reached = "feedback"
        else:
            result.feedback = (
                "Se extrajeron los pasos pero la verificación automática no estuvo disponible. "
                "El profesor revisará tu procedimiento."
            )
    except Exception as exc:
        result.errors.append(f"Generación de feedback falló: {exc}")
        result.feedback = "Análisis parcial completado. El profesor revisará tu procedimiento."

    return result


def analyze_with_llm_data(llm_result: dict) -> PipelineResult | None:
    """Ejecuta el pipeline usando datos de review_math_procedure()."""
    transcription = llm_result.get("transcripcion", "")
    pasos = llm_result.get("pasos", [])
    if not transcription and not pasos:
        return None
    return analyze(transcription=transcription, llm_pasos=pasos)
