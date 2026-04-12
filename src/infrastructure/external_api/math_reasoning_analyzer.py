"""Analizador de razonamiento matemático — valida pasos secuenciales.

Recibe una lista de pasos extraídos y usa el verificador simbólico
para determinar si cada transición es matemáticamente válida.
Genera un reporte estructurado de validez por paso.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from src.infrastructure.external_api.math_step_extractor import MathStep
from src.infrastructure.external_api.symbolic_math_verifier import (
    compare_steps,
    is_available as sympy_available,
    ErrorType,
)


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
    score: int = 0  # 0-100
    sympy_used: bool = False
    summary: str = ""


# ── Mensajes de error por tipo ───────────────────────────────────────────────

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
    """Analiza una secuencia de pasos matemáticos.

    Compara cada par de pasos consecutivos usando el verificador
    simbólico para determinar si las transiciones son válidas.

    Args:
        steps: Lista ordenada de pasos del procedimiento.

    Returns:
        ProcedureAnalysis con el resultado detallado.
    """
    if not steps:
        return ProcedureAnalysis(summary="No se detectaron pasos en el procedimiento.")

    analysis = ProcedureAnalysis(
        total_steps=len(steps),
        sympy_used=sympy_available(),
    )

    # El primer paso siempre se marca como válido (es la expresión inicial)
    first = StepAnalysis(
        step=steps[0].step,
        expression=steps[0].expression,
        valid=True,
        feedback="Expresión inicial del procedimiento.",
    )
    analysis.steps.append(first)
    analysis.valid_steps = 1

    # Comparar cada par de pasos consecutivos
    for i in range(1, len(steps)):
        prev_step = steps[i - 1]
        curr_step = steps[i]

        result = compare_steps(prev_step.expression, curr_step.expression)

        step_analysis = StepAnalysis(
            step=curr_step.step,
            expression=curr_step.expression,
            valid=result.valid,
            error_type=result.error_type,
            feedback=_ERROR_MESSAGES.get(result.error_type, ""),
        )

        if result.valid:
            if result.error_type in ("parse_error", "unavailable"):
                step_analysis.feedback = "Paso no verificable automáticamente."
            else:
                step_analysis.feedback = "Transformación algebraica correcta."
            analysis.valid_steps += 1
        else:
            analysis.invalid_steps += 1

        analysis.steps.append(step_analysis)

    # Calcular score (0-100)
    if analysis.total_steps > 0:
        # Ponderar: pasos válidos / total * 100, penalizando errores graves
        base_score = (analysis.valid_steps / analysis.total_steps) * 100
        # Penalización extra por errores de signo y distributiva (errores conceptuales)
        conceptual_errors = sum(
            1
            for s in analysis.steps
            if s.error_type in ("sign_error", "incorrect_distributive", "unlike_terms_combined")
        )
        penalty = conceptual_errors * 10
        analysis.score = max(0, min(100, int(base_score - penalty)))
    else:
        analysis.score = 0

    # Generar resumen
    if analysis.invalid_steps == 0:
        analysis.summary = "Todos los pasos son algebraicamente correctos."
    else:
        errors = [s for s in analysis.steps if not s.valid]
        error_nums = ", ".join(str(s.step) for s in errors)
        analysis.summary = (
            f"Se detectaron {analysis.invalid_steps} error(es) " f"en los pasos: {error_nums}."
        )

    return analysis
