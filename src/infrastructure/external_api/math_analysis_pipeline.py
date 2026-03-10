"""Pipeline de análisis matemático automático.

Orquesta el flujo completo:
    imagen → OCR → extracción de pasos → verificación simbólica → feedback

Cada etapa tiene fallback independiente. Si todo el pipeline falla,
retorna None para que la capa de UI use el análisis por LLM existente.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.infrastructure.external_api.math_ocr import (
    OCRResult,
    extract_math_from_image,
    extract_math_from_text,
)
from src.infrastructure.external_api.math_step_extractor import (
    MathStep,
    extract_steps,
    extract_steps_from_llm_transcription,
)
from src.infrastructure.external_api.math_reasoning_analyzer import (
    ProcedureAnalysis,
    analyze_steps,
)
from src.infrastructure.external_api.pedagogical_feedback import (
    generate_feedback,
)


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
    """Ejecuta el pipeline de análisis matemático.

    Acepta imagen (para OCR), texto transcrito (del LLM), o pasos
    ya estructurados. Usa la fuente más rica disponible.

    Args:
        image_bytes: Bytes de la imagen del procedimiento (opcional).
        transcription: Texto transcrito del procedimiento (opcional).
                       Puede venir del campo 'transcripcion' de review_math_procedure().
        llm_pasos: Pasos estructurados del LLM (opcional).
                   Compatible con el formato de review_math_procedure().

    Returns:
        PipelineResult con el análisis completo, o None si no hay datos
        suficientes para analizar (señal para usar fallback LLM).
    """
    result = PipelineResult()

    # ── Etapa 1: OCR / obtener texto ─────────────────────────────────────
    if image_bytes:
        try:
            ocr_result = extract_math_from_image(image_bytes)
            if ocr_result:
                result.ocr = ocr_result
                result.pipeline_stage_reached = "ocr"
        except Exception as exc:
            result.errors.append(f"OCR falló: {exc}")

    # Si no hay OCR pero hay transcripción del LLM, usarla
    if result.ocr is None and transcription:
        result.ocr = extract_math_from_text(transcription)
        result.pipeline_stage_reached = "ocr_from_text"

    # Sin texto de ninguna fuente y sin pasos del LLM → no hay datos
    if result.ocr is None and not llm_pasos:
        return None

    # ── Etapa 2: Extracción de pasos ─────────────────────────────────────
    try:
        if llm_pasos:
            # Preferir pasos del LLM (ya estructurados)
            result.steps = extract_steps_from_llm_transcription(
                transcription or "",
                llm_pasos,
            )
            result.pipeline_stage_reached = "steps_from_llm"
        elif result.ocr:
            result.steps = extract_steps(result.ocr.raw_text)
            result.pipeline_stage_reached = "steps"
    except Exception as exc:
        result.errors.append(f"Extracción de pasos falló: {exc}")

    if not result.steps:
        # Sin pasos extraídos, el pipeline no puede continuar
        # pero retorna lo que tiene (OCR) para que sea útil
        result.feedback = "No se pudieron extraer pasos del procedimiento."
        return result

    # ── Etapa 3: Verificación simbólica ──────────────────────────────────
    try:
        result.analysis = analyze_steps(result.steps)
        result.pipeline_stage_reached = "analysis"
        result.score = result.analysis.score
    except Exception as exc:
        result.errors.append(f"Verificación simbólica falló: {exc}")
        # Continuar sin score — el feedback será parcial
        result.analysis = None

    # ── Etapa 4: Feedback pedagógico ─────────────────────────────────────
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
    """Ejecuta el pipeline usando datos de review_math_procedure().

    Toma el JSON retornado por el servicio de revisión Groq y aplica
    verificación simbólica adicional sobre los pasos transcritos.

    Args:
        llm_result: Dict con 'transcripcion', 'pasos', 'score_procedimiento', etc.

    Returns:
        PipelineResult con verificación simbólica adicional, o None si falla.
    """
    transcription = llm_result.get("transcripcion", "")
    pasos = llm_result.get("pasos", [])

    if not transcription and not pasos:
        return None

    return analyze(
        transcription=transcription,
        llm_pasos=pasos,
    )
