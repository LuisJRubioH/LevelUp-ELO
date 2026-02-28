"""Servicio de revisión matemática rigurosa de procedimientos escritos a mano.

Usa el modelo meta-llama/llama-4-scout-17b-16e-instruct en Groq con soporte
de visión multimodal. Devuelve un JSON estructurado con transcripción, análisis
paso a paso, errores detectados y un score 0-100.
"""

import base64
import json
import re

REVIEW_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Factor de ajuste ELO: max ±10 pts cuando score = 0 ó 100
# Fórmula: ELO_final = ELO_base + (score_procedimiento - 50) * FACTOR_AJUSTE
PROCEDURE_FACTOR_AJUSTE = 0.2

_SYSTEM_PROMPT = (
    "Eres un corrector matemático universitario experto. "
    "Evalúas procedimientos matemáticos escritos a mano con rigor formal. "
    "No inventes pasos. "
    "No completes lo que no esté explícitamente visible. "
    "Si algo es ilegible, indícalo explícitamente. "
    "Evalúa únicamente lo que aparece en la imagen."
)

_USER_PROMPT = """Analiza la imagen del procedimiento y realiza lo siguiente:

1) Transcribe exactamente el contenido matemático visible.
2) Enumera cada paso explícito.
3) Verifica formalmente cada implicación matemática.
4) Clasifica cada paso como:
   - Valido
   - Algebraicamente incorrecto
   - Conceptualmente incorrecto
   - Incompleto
5) Detecta saltos logicos o pasos omitidos.
6) Determina si el procedimiento conduce correctamente al resultado final.
7) Asigna un puntaje de 0 a 100 basado exclusivamente en la correccion matematica.

Devuelve exclusivamente un JSON valido con esta estructura:

{
  "transcripcion": "...",
  "pasos": [
    {
      "numero": 1,
      "contenido": "...",
      "evaluacion": "Valido | Algebraicamente incorrecto | Conceptualmente incorrecto | Incompleto",
      "comentario": "..."
    }
  ],
  "errores_detectados": [],
  "saltos_logicos": [],
  "resultado_correcto": true,
  "evaluacion_global": "...",
  "score_procedimiento": 0
}

No incluyas texto fuera del JSON."""


def _parse_json_response(content: str) -> dict:
    """Extrae y parsea el JSON de la respuesta del modelo."""
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    content = content.strip()

    start = content.find('{')
    end = content.rfind('}')
    if start == -1 or end == -1 or end <= start:
        raise ValueError("La respuesta no contiene un objeto JSON válido.")

    return json.loads(content[start:end + 1])


def review_math_procedure(
    image_bytes: bytes,
    mime_type: str,
    api_key: str,
) -> dict:
    """Envía la imagen a Groq y retorna la revisión estructurada del procedimiento.

    Parámetros:
        image_bytes: bytes de la imagen del procedimiento manuscrito.
        mime_type:   'image/jpeg' | 'image/png' | 'image/webp'
        api_key:     API key de Groq (prefijo 'gsk_').

    Retorna:
        dict con claves: transcripcion, pasos, errores_detectados,
        saltos_logicos, resultado_correcto, evaluacion_global, score_procedimiento.

    Lanza:
        ValueError:       si la respuesta no es JSON válido tras un reintento.
        ConnectionError:  si hay error de red al conectar con Groq.
    """
    from openai import OpenAI

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                },
                {"type": "text", "text": _USER_PROMPT},
            ],
        },
    ]

    last_error = None
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=REVIEW_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
            )
            content = response.choices[0].message.content or ""
        except Exception as exc:
            raise ConnectionError(f"Error al conectar con Groq: {exc}") from exc

        try:
            return _parse_json_response(content)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt == 0:
                continue  # un reintento con el mismo prompt

    raise ValueError(
        f"La respuesta del modelo no es JSON válido tras dos intentos. "
        f"Error: {last_error}"
    )


def apply_procedure_elo_adjustment(elo_base: float, score_procedimiento: int) -> float:
    """Aplica el ajuste ELO secundario basado en el score del procedimiento.

    Fórmula: ELO_final = ELO_base + (score_procedimiento - 50) * PROCEDURE_FACTOR_AJUSTE

    Ejemplos de ajuste (factor = 0.2):
        score=100  → +10.0 ELO
        score= 75  → +5.0  ELO
        score= 50  →  0.0  ELO  (neutro)
        score= 25  → -5.0  ELO
        score=  0  → -10.0 ELO

    Parámetros:
        elo_base:             ELO actual del estudiante en el tópico.
        score_procedimiento:  Puntaje 0-100 devuelto por el modelo.

    Retorna:
        Nuevo ELO con el ajuste aplicado.
    """
    score = max(0, min(100, int(score_procedimiento)))
    return elo_base + (score - 50) * PROCEDURE_FACTOR_AJUSTE
