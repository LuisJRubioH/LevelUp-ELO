"""OCR matemático — extrae texto y expresiones LaTeX de imágenes.

Soporta múltiples backends con detección automática:
1. pix2tex (LatexOCR) — mejor para expresiones matemáticas
2. pytesseract — fallback general para texto mixto
3. regex — extracción mínima desde texto plano (siempre disponible)

Todas las dependencias de OCR son opcionales. Si ninguna está instalada,
el módulo retorna None para señalizar al pipeline que use el LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class OCRResult:
    """Resultado del OCR matemático."""

    raw_text: str
    latex_expressions: list[str] = field(default_factory=list)
    backend_used: str = "none"
    confidence: float = 0.0


# ── Regex para extraer expresiones matemáticas de texto ──────────────────────

# Patrones que identifican expresiones matemáticas en texto plano
_MATH_PATTERNS = [
    # LaTeX delimitado: $...$, $$...$$, \(...\), \[...\]
    re.compile(r"\$\$(.+?)\$\$", re.DOTALL),
    re.compile(r"\$(.+?)\$"),
    re.compile(r"\\\((.+?)\\\)"),
    re.compile(r"\\\[(.+?)\\\]", re.DOTALL),
    # Ecuaciones con = (ej: "2x + 3 = 7")
    re.compile(r"[0-9a-zA-Z\s\+\-\*/\^\(\)]+\s*=\s*[0-9a-zA-Z\s\+\-\*/\^\(\)]+"),
    # Expresiones con operadores matemáticos comunes
    re.compile(r"(?:sin|cos|tan|log|ln|lim|int|sum|sqrt)\s*[\(\[{].+?[\)\]}]"),
]


def _extract_latex_from_text(text: str) -> list[str]:
    """Extrae expresiones matemáticas de texto plano usando regex."""
    expressions = []
    for pattern in _MATH_PATTERNS:
        for match in pattern.finditer(text):
            expr = match.group().strip()
            if len(expr) >= 3:  # filtrar matches triviales
                expressions.append(expr)
    # Deduplicar manteniendo orden
    seen = set()
    unique = []
    for expr in expressions:
        if expr not in seen:
            seen.add(expr)
            unique.append(expr)
    return unique


def _try_pix2tex(image_bytes: bytes) -> OCRResult | None:
    """Intenta usar pix2tex (LatexOCR) para reconocimiento de LaTeX."""
    try:
        from pix2tex.cli import LatexOCR
        from PIL import Image
        import io

        model = LatexOCR()
        img = Image.open(io.BytesIO(image_bytes))
        latex = model(img)
        if latex:
            return OCRResult(
                raw_text=latex,
                latex_expressions=[latex],
                backend_used="pix2tex",
                confidence=0.8,
            )
    except ImportError:
        pass
    except Exception:
        pass
    return None


def _try_tesseract(image_bytes: bytes) -> OCRResult | None:
    """Intenta usar pytesseract para OCR general."""
    try:
        import pytesseract
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang="eng")
        if text and text.strip():
            return OCRResult(
                raw_text=text.strip(),
                latex_expressions=_extract_latex_from_text(text),
                backend_used="tesseract",
                confidence=0.5,
            )
    except ImportError:
        pass
    except Exception:
        pass
    return None


def extract_math_from_image(image_bytes: bytes) -> OCRResult | None:
    """Extrae texto y expresiones matemáticas de una imagen.

    Intenta cada backend en orden de prioridad. Retorna None si ninguno
    está disponible, lo cual señaliza al pipeline que debe usar el LLM.

    Args:
        image_bytes: Bytes de la imagen (PNG, JPEG, etc.).

    Returns:
        OCRResult con el texto extraído, o None si no hay backend disponible.
    """
    # 1. pix2tex: mejor para expresiones matemáticas puras
    result = _try_pix2tex(image_bytes)
    if result:
        return result

    # 2. tesseract: fallback para texto mixto
    result = _try_tesseract(image_bytes)
    if result:
        return result

    # Sin backend de OCR disponible
    return None


def extract_math_from_text(text: str) -> OCRResult:
    """Extrae expresiones matemáticas de texto ya transcrito (ej: del LLM).

    Siempre disponible — no requiere dependencias externas.

    Args:
        text: Texto con posibles expresiones matemáticas.

    Returns:
        OCRResult con las expresiones extraídas.
    """
    return OCRResult(
        raw_text=text,
        latex_expressions=_extract_latex_from_text(text),
        backend_used="regex",
        confidence=0.3,
    )
