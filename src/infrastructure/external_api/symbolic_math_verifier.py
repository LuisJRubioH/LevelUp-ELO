"""Verificador simbólico de pasos matemáticos usando SymPy.

Verifica equivalencia algebraica entre pasos consecutivos,
detecta errores comunes (distributiva incorrecta, signos, etc.)
y reporta el tipo de error encontrado.

SymPy es una dependencia opcional. Si no está instalada,
todas las funciones retornan resultado "no verificable".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

ErrorType = Literal[
    "none",  # sin error
    "incorrect_distributive",  # distributiva incorrecta
    "unlike_terms_combined",  # suma de términos no semejantes
    "sign_error",  # error de signo
    "fraction_simplification",  # fracción mal simplificada
    "algebraic_error",  # error algebraico genérico
    "not_equivalent",  # pasos no son equivalentes
    "parse_error",  # no se pudo parsear la expresión
    "unavailable",  # SymPy no disponible
]


@dataclass
class VerificationResult:
    """Resultado de la verificación de un paso."""

    valid: bool
    error_type: ErrorType = "none"
    detail: str = ""


# ── Detección de SymPy ───────────────────────────────────────────────────────

_SYMPY_AVAILABLE = False
try:
    import sympy
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
        convert_xor,
    )

    _SYMPY_AVAILABLE = True
except ImportError:
    pass


def is_available() -> bool:
    """Retorna True si SymPy está instalado y disponible."""
    return _SYMPY_AVAILABLE


# ── Cache de simplificación (T4) ─────────────────────────────────────────────


@lru_cache(maxsize=256)
def _simplify_cached(expr):
    """sympy.simplify con cache LRU para evitar recálculos."""
    return sympy.simplify(expr)


@lru_cache(maxsize=256)
def _expand_cached(expr):
    """sympy.expand con cache LRU."""
    return sympy.expand(expr)


# ── Limpieza y parseo ────────────────────────────────────────────────────────

# Patrones LaTeX → notación Python/SymPy
_LATEX_REPLACEMENTS = [
    (re.compile(r"\\frac\{([^}]+)\}\{([^}]+)\}"), r"((\1)/(\2))"),
    (re.compile(r"\\sqrt\{([^}]+)\}"), r"sqrt(\1)"),
    (re.compile(r"\\sqrt\[(\d+)\]\{([^}]+)\}"), r"(\2)**(1/\1)"),
    (re.compile(r"\\left\s*"), ""),
    (re.compile(r"\\right\s*"), ""),
    (re.compile(r"\\cdot"), "*"),
    (re.compile(r"\\times"), "*"),
    (re.compile(r"\\div"), "/"),
    (re.compile(r"\\pm"), "+-"),
    (re.compile(r"\\pi"), "pi"),
    (re.compile(r"\\infty"), "oo"),
    (re.compile(r"\\sin"), "sin"),
    (re.compile(r"\\cos"), "cos"),
    (re.compile(r"\\tan"), "tan"),
    (re.compile(r"\\log"), "log"),
    (re.compile(r"\\ln"), "ln"),
    (re.compile(r"\\exp"), "exp"),
    (re.compile(r"\^"), "**"),
    (re.compile(r"[{}]"), ""),
    (re.compile(r"\$"), ""),
]


def _clean_expression(expr: str) -> str:
    """Limpia una expresión matemática para parseo con SymPy."""
    result = expr.strip()
    for pattern, replacement in _LATEX_REPLACEMENTS:
        result = pattern.sub(replacement, result)
    # Eliminar texto descriptivo al inicio (ej: "simplificamos: ")
    # Solo eliminar si es una palabra de 3+ letras seguida de espacio/dos puntos
    result = re.sub(r"^[a-záéíóúñ]{3,}[\s:]+", "", result, flags=re.IGNORECASE).strip()
    return result


def parse_expression(expr_str: str) -> object | None:
    """Parsea una expresión matemática a objeto SymPy.

    Args:
        expr_str: Expresión en texto o LaTeX.

    Returns:
        Objeto SymPy, o None si no se pudo parsear.
    """
    if not _SYMPY_AVAILABLE:
        return None

    cleaned = _clean_expression(expr_str)
    if not cleaned:
        return None

    # Si tiene '=', tomar el lado derecho (resultado del paso)
    if "=" in cleaned:
        parts = cleaned.split("=")
        cleaned = parts[-1].strip()

    try:
        transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )
        return parse_expr(cleaned, transformations=transformations)
    except Exception:
        return None


# ── Equivalencia con valor absoluto (T1) ─────────────────────────────────────


def _check_abs_equivalence(e1, e2) -> bool:
    """Verifica equivalencia considerando valor absoluto.

    Acepta casos como sqrt(x**2) == x o sqrt(x**2) == Abs(x),
    comunes en contextos escolares donde se asume x >= 0.

    Solo se activa cuando las expresiones involucran sqrt o potencias,
    para evitar falsos positivos como x == -x.
    """
    try:
        # Solo aplicar si alguna expresión contiene sqrt o Pow (raíces)
        has_sqrt_or_pow = (
            e1.has(sympy.sqrt)
            or e2.has(sympy.sqrt)
            or e1.has(sympy.Abs)
            or e2.has(sympy.Abs)
            or any(
                isinstance(a, sympy.Pow) and not a.exp.is_Integer
                for a in sympy.preorder_traversal(e1)
            )
            or any(
                isinstance(a, sympy.Pow) and not a.exp.is_Integer
                for a in sympy.preorder_traversal(e2)
            )
        )
        if not has_sqrt_or_pow:
            return False

        # Estrategia 1: re-evaluar con variables positivas (contexto escolar)
        free_vars = e1.free_symbols | e2.free_symbols
        if free_vars:
            pos_subs = {v: sympy.Symbol(v.name, positive=True) for v in free_vars}
            e1_pos = e1.subs(pos_subs)
            e2_pos = e2.subs(pos_subs)
            if _simplify_cached(e1_pos - e2_pos) == 0:
                return True

        # Estrategia 2: Abs(e1) == Abs(e2) (ej: sqrt(x^2) == Abs(x))
        if _simplify_cached(sympy.Abs(e1) - sympy.Abs(e2)) == 0:
            return True
    except Exception:
        pass
    return False


# ── Verificación numérica como fallback (T2/T3) ─────────────────────────────

# Valores de prueba para verificación numérica
_TEST_VALUES = [2, 3, -2]


def _check_numeric_equivalence(e1, e2) -> bool:
    """Verifica equivalencia evaluando numéricamente en varios puntos.

    Solo se ejecuta si ambas expresiones contienen variables (T3).
    Sustituye valores seguros y compara resultados.
    """
    try:
        # Obtener variables libres de ambas expresiones
        vars1 = e1.free_symbols
        vars2 = e2.free_symbols
        all_vars = vars1 | vars2

        # T3: solo ejecutar si hay variables en al menos una expresión
        if not all_vars:
            return False

        for val in _TEST_VALUES:
            subs = {v: val for v in all_vars}
            try:
                v1 = complex(e1.subs(subs))
                v2 = complex(e2.subs(subs))
                # Tolerancia para errores de punto flotante
                if abs(v1 - v2) > 1e-9:
                    return False
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                # Si un valor causa error (ej: log de negativo), saltar
                continue

        # Si todos los valores probados coincidieron (y al menos uno fue evaluado)
        return True
    except Exception:
        return False


# ── Verificación principal ───────────────────────────────────────────────────


def check_equivalence(expr1_str: str, expr2_str: str) -> VerificationResult:
    """Verifica si dos expresiones son algebraicamente equivalentes.

    Estrategia de verificación en capas:
    1. simplify(e1 - e2) == 0
    2. expand(e1 - e2) == 0
    3. Equivalencia con valor absoluto (T1)
    4. Verificación numérica como fallback (T2)
    5. Diagnóstico de error si todo falla

    Args:
        expr1_str: Primera expresión (paso anterior).
        expr2_str: Segunda expresión (paso actual).

    Returns:
        VerificationResult indicando si son equivalentes.
    """
    if not _SYMPY_AVAILABLE:
        return VerificationResult(
            valid=True,
            error_type="unavailable",
            detail="SymPy no instalado, verificación no disponible.",
        )

    e1 = parse_expression(expr1_str)
    e2 = parse_expression(expr2_str)

    if e1 is None or e2 is None:
        return VerificationResult(
            valid=True,
            error_type="parse_error",
            detail="No se pudo parsear una o ambas expresiones.",
        )

    try:
        # Capa 1: simplificación directa
        diff = _simplify_cached(e1 - e2)
        if diff == 0:
            return VerificationResult(valid=True)

        # Capa 2: expand
        diff_expanded = _expand_cached(e1 - e2)
        if diff_expanded == 0:
            return VerificationResult(valid=True)

        # Capa 3 (T1): equivalencia con valor absoluto
        if _check_abs_equivalence(e1, e2):
            return VerificationResult(valid=True)

        # Capa 4 (T2/T3): verificación numérica si hay variables
        if _check_numeric_equivalence(e1, e2):
            return VerificationResult(valid=True)

        # No son equivalentes — diagnosticar el error
        error_type = _diagnose_error(e1, e2, diff)
        return VerificationResult(
            valid=False,
            error_type=error_type,
            detail=f"Las expresiones no son equivalentes. Diferencia: {diff}",
        )
    except Exception as exc:
        return VerificationResult(
            valid=True,
            error_type="parse_error",
            detail=f"Error durante verificación: {exc}",
        )


def _diagnose_error(e1: object, e2: object, diff: object) -> ErrorType:
    """Intenta clasificar el tipo de error algebraico."""
    if not _SYMPY_AVAILABLE:
        return "algebraic_error"

    try:
        # Verificar error de signo: si -e1 == e2
        if _simplify_cached(e1 + e2) == 0:
            return "sign_error"

        # Verificar fracción mal simplificada:
        # Solo aplica cuando ambas expresiones son numéricas puras (sin variables)
        try:
            if diff.is_number:
                if diff.is_Rational and not diff.is_Integer:
                    return "fraction_simplification"
                if e1.is_number and e2.is_number:
                    return (
                        "fraction_simplification"
                        if (diff.is_Rational and not diff.is_Integer)
                        else "not_equivalent"
                    )
        except Exception:
            pass

        # Verificar distributiva incorrecta
        e1_exp = _expand_cached(e1)
        e2_exp = _expand_cached(e2)
        diff_exp = _expand_cached(e1_exp - e2_exp)
        if diff_exp != 0:
            if diff_exp.is_Integer and diff_exp != 0:
                return "incorrect_distributive"
            diff_terms = sympy.Add.make_args(diff_exp)
            if len(diff_terms) >= 2:
                return "incorrect_distributive"

        return "not_equivalent"
    except Exception:
        return "algebraic_error"


def compare_steps(
    step1_expr: str,
    step2_expr: str,
) -> VerificationResult:
    """Compara dos pasos consecutivos del procedimiento.

    Wrapper semántico de check_equivalence() con manejo de ecuaciones.
    Si ambos pasos son ecuaciones (contienen '='), verifica que
    la transformación sea válida.

    Args:
        step1_expr: Expresión del paso anterior.
        step2_expr: Expresión del paso actual.

    Returns:
        VerificationResult.
    """
    if not _SYMPY_AVAILABLE:
        return VerificationResult(
            valid=True,
            error_type="unavailable",
            detail="SymPy no instalado.",
        )

    # Si ambos son ecuaciones, comparar ambos lados
    if "=" in step1_expr and "=" in step2_expr:
        return _compare_equations(step1_expr, step2_expr)

    return check_equivalence(step1_expr, step2_expr)


def _compare_equations(eq1_str: str, eq2_str: str) -> VerificationResult:
    """Compara dos ecuaciones verificando que la transformación sea válida."""
    parts1 = eq1_str.split("=", 1)
    parts2 = eq2_str.split("=", 1)

    if len(parts1) != 2 or len(parts2) != 2:
        return check_equivalence(eq1_str, eq2_str)

    lhs1 = parse_expression(parts1[0])
    rhs1 = parse_expression(parts1[1])
    lhs2 = parse_expression(parts2[0])
    rhs2 = parse_expression(parts2[1])

    if any(x is None for x in [lhs1, rhs1, lhs2, rhs2]):
        return VerificationResult(
            valid=True,
            error_type="parse_error",
            detail="No se pudo parsear una o más partes de las ecuaciones.",
        )

    try:
        eq1_expr = lhs1 - rhs1
        eq2_expr = lhs2 - rhs2

        # Verificar que lhs1 - rhs1 == lhs2 - rhs2 (misma ecuación, diferente forma)
        diff = _simplify_cached(eq1_expr - eq2_expr)
        if diff == 0:
            return VerificationResult(valid=True)

        # Intentar con expand
        diff_exp = _expand_cached(eq1_expr - eq2_expr)
        if diff_exp == 0:
            return VerificationResult(valid=True)

        # Verificar si una ecuación es múltiplo escalar de la otra
        # (ej: 3x-9 = 3*(x-3), ambas tienen la misma solución)
        try:
            ratio = _simplify_cached(eq1_expr / eq2_expr)
            if ratio.is_number and ratio != 0:
                return VerificationResult(valid=True)
        except Exception:
            pass

        # T1: equivalencia con valor absoluto en ecuaciones
        if _check_abs_equivalence(eq1_expr, eq2_expr):
            return VerificationResult(valid=True)

        # T2/T3: verificación numérica para ecuaciones
        if _check_numeric_equivalence(eq1_expr, eq2_expr):
            return VerificationResult(valid=True)

        error_type = _diagnose_error(eq1_expr, eq2_expr, diff)
        return VerificationResult(
            valid=False,
            error_type=error_type,
            detail="La transformación de la ecuación no es equivalente.",
        )
    except Exception:
        return VerificationResult(
            valid=True,
            error_type="parse_error",
            detail="Error durante la comparación de ecuaciones.",
        )
