"""Generador de feedback pedagógico para procedimientos matemáticos.

Toma el análisis de pasos y genera retroalimentación constructiva
sin revelar la respuesta final, siguiendo principios socráticos.
"""

from __future__ import annotations

from src.infrastructure.external_api.math_reasoning_analyzer import (
    ProcedureAnalysis,
    StepAnalysis,
)
from src.infrastructure.external_api.symbolic_math_verifier import ErrorType


# ── Pistas socráticas por tipo de error ──────────────────────────────────────

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

# Hint genérico para errores no clasificados
_DEFAULT_HINT = "Revisa cuidadosamente el paso {step}. ¿Cada operación que realizaste es correcta?"


def _get_hint(error_type: ErrorType, step_num: int) -> str:
    """Selecciona una pista socrática para un tipo de error y paso."""
    hints = _SOCRATIC_HINTS.get(error_type, [_DEFAULT_HINT])
    # Rotar hints según el número de paso para variedad
    hint = hints[step_num % len(hints)]
    return hint.format(step=step_num)


def generate_feedback(analysis: ProcedureAnalysis) -> str:
    """Genera feedback pedagógico completo para un procedimiento analizado.

    Reglas:
    1. NO revela la respuesta final.
    2. Identifica el paso incorrecto.
    3. Explica el tipo de error sin resolverlo.
    4. Da pistas socráticas.

    Args:
        analysis: Resultado del análisis de pasos.

    Returns:
        Texto markdown con la retroalimentación pedagógica.
    """
    if not analysis.steps:
        return (
            "No se detectaron pasos en tu procedimiento. Intenta mostrar tu desarrollo paso a paso."
        )

    lines: list[str] = []

    # Encabezado con resumen
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

    # Detalle por paso con errores
    error_steps = [s for s in analysis.steps if not s.valid]
    for step_analysis in error_steps:
        lines.append(f"**Paso {step_analysis.step}:** `{step_analysis.expression}`")
        lines.append(f"- {step_analysis.feedback}")
        hint = _get_hint(step_analysis.error_type, step_analysis.step)
        lines.append(f"- **Pista:** {hint}")
        lines.append("")

    # Score si hay verificación simbólica
    if analysis.sympy_used:
        lines.append(f"**Puntuación automática:** {analysis.score}/100")

    return "\n".join(lines)


def generate_step_feedback(step_analysis: StepAnalysis) -> str:
    """Genera feedback para un paso individual.

    Útil para mostrar feedback inline junto a cada paso.

    Args:
        step_analysis: Análisis de un paso individual.

    Returns:
        Texto breve con la retroalimentación.
    """
    if step_analysis.valid:
        if step_analysis.error_type in ("parse_error", "unavailable"):
            return "Paso no verificable automáticamente."
        return "Correcto."

    hint = _get_hint(step_analysis.error_type, step_analysis.step)
    return f"{step_analysis.feedback} {hint}"
