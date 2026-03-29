import os
import requests
import json
import re
import base64

from src.utils import strip_thinking_tags, strip_thinking_tags_stream


def _normalize_latex(text: str) -> str:
    """Normaliza notación LaTeX de modelos que usan \\(...\\) y \\[...\\] a $...$ y $$...$$.

    Algunos modelos (Qwen, Mistral) emiten LaTeX con paréntesis/corchetes
    escapados que Streamlit no renderiza. Esta función los convierte al
    formato estándar $...$ / $$...$$ que sí se renderiza correctamente.
    """
    if not text:
        return text
    # \[...\] → $$...$$  (bloque)
    text = re.sub(r'\\\[', '$$', text)
    text = re.sub(r'\\\]', '$$', text)
    # \(...\) → $...$  (inline)
    text = re.sub(r'\\\(', '$', text)
    text = re.sub(r'\\\)', '$', text)
    return text


def _normalize_latex_stream(chunk_generator):
    """Wrapper para generadores de streaming que normaliza LaTeX chunk a chunk."""
    for chunk in chunk_generator:
        yield _normalize_latex(chunk)

# Cargar variables de entorno desde .env si python-dotenv está instalado
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv()
except ImportError:
    pass

# Variable de módulo que registra el último error 401 detectado
_AI_KEY_ERROR: str | None = None

# ── Provider registry ────────────────────────────────────────────────────────
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model_cog": "llama-3.1-8b-instant",
        "model_analysis": "llama-3.3-70b-versatile",
        "label": "☁️ Groq Cloud",
        "openai_compat": True,
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model_cog": "gpt-4o-mini",
        "model_analysis": "gpt-4o",
        "label": "☁️ OpenAI",
        "openai_compat": True,
    },
    "anthropic": {
        "base_url": None,
        "model_cog": "claude-haiku-4-5-20251001",
        "model_analysis": "claude-sonnet-4-6",
        "label": "☁️ Anthropic Claude",
        "openai_compat": False,
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model_cog": "gemini-2.0-flash",
        "model_analysis": "gemini-2.0-flash",
        "label": "☁️ Google Gemini",
        "openai_compat": True,
    },
    "huggingface": {
        "base_url": "https://api-inference.huggingface.co/v1",
        "model_cog": "meta-llama/Llama-3.1-8B-Instruct",
        "model_analysis": "meta-llama/Llama-3.3-70B-Instruct",
        "label": "☁️ HuggingFace",
        "openai_compat": True,
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "model_cog": None,
        "model_analysis": None,
        "label": "🖥️ LM Studio",
        "openai_compat": True,
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model_cog": None,
        "model_analysis": None,
        "label": "🖥️ Ollama",
        "openai_compat": True,
    },
}

_KEY_PREFIXES = [
    ("sk-ant-", "anthropic"),
    ("gsk_",    "groq"),
    ("AIzaSy",  "gemini"),
    ("hf_",     "huggingface"),
    ("sk-proj-","openai"),
    ("sk-",     "openai"),
]


def _proc_quality_label(avg_score: float) -> str:
    """Convierte un promedio de procedimiento (0-5) en etiqueta cualitativa."""
    if avg_score < 3.0:
        return f"Deficiente ({avg_score:.1f}/5.0) — Falta de rigor técnico en el desarrollo"
    elif avg_score <= 4.0:
        return f"Regular ({avg_score:.1f}/5.0) — Procedimiento incompleto o poco claro"
    else:
        return f"Excelente ({avg_score:.1f}/5.0) — Dominio total del desarrollo"


def detect_provider_from_key(api_key: str):
    """Infiere el proveedor a partir del prefijo de la API key."""
    if not api_key:
        return None
    for prefix, provider in _KEY_PREFIXES:
        if api_key.startswith(prefix):
            return provider
    return None


def get_active_models(base_url="http://localhost:1234/v1"):
    """Consulta un servidor compatible con OpenAI /models para obtener IDs disponibles."""
    try:
        response = requests.get(f"{base_url.rstrip('/')}/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [m['id'] for m in data.get('data', [])]
    except Exception:
        pass
    return []


def detect_lmstudio(base_url="http://localhost:1234/v1"):
    """Detecta si LM Studio (u Ollama) está activo y retorna sus modelos disponibles."""
    models = get_active_models(base_url)
    return {'available': bool(models), 'models': models}


def select_best_model(models):
    """Selecciona el modelo más adecuado de la lista.
    Prioriza modelos de 7b-9b (balance rendimiento/velocidad).
    """
    if not models:
        return None
    if len(models) == 1:
        return models[0]
    preferred_sizes = ['8b', '7b', '9b', '4b', '3b', '12b', '13b', '14b', '72b', '70b']
    for size in preferred_sizes:
        for model in models:
            if size in model.lower():
                return model
    return models[0]


def _call_ai_api(prompt, model_name, base_url, json_mode=False, api_key=None, provider=None):
    """Llama a cualquier proveedor de IA.

    Routing:
    - provider='anthropic' → Anthropic SDK
    - api_key != None → OpenAI-compatible cloud (Groq, OpenAI, Gemini, HF, …)
    - api_key == None  → LM Studio / Ollama local
    """
    system_instr = "Responde EXCLUSIVAMENTE con el contenido solicitado. "
    if json_mode:
        system_instr += "Formato: JSON puro, sin explicaciones externas."
    else:
        system_instr += "Formato: Texto conversacional directo. REGLA CRÍTICA: Usa SIEMPRE notación LaTeX para matemáticas ($...$ para línea, $$...$$ para bloque)."

    full_prompt = f"SISTEMA: {system_instr}\n\nUSUARIO: {prompt}"
    messages = [{"role": "user", "content": full_prompt}]
    temperature = 0.3 if not json_mode else 0.1

    if provider is None and api_key:
        provider = detect_provider_from_key(api_key)

    if provider == "anthropic":
        # ── Anthropic Claude SDK ─────────────────────────────────────────────
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model=model_name,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_prompt}],
            )
            content = resp.content[0].text
            return strip_thinking_tags(content)
        except Exception as e:
            # T9c: mapeo estandarizado de errores Anthropic
            err_str = str(e)
            if "401" in err_str or "authentication" in err_str.lower():
                return "ERROR_401: ❌ API Key inválida o expirada para Anthropic. Verifica tu clave en el panel lateral."
            if "429" in err_str or "rate_limit" in err_str.lower():
                return "ERROR_429: ⏳ Límite de solicitudes alcanzado. Espera un momento antes de continuar."
            if "timeout" in err_str.lower() or "connection" in err_str.lower():
                raise ConnectionError("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.") from e
            return f"❌ Error inesperado: {type(e).__name__}. Contacta al administrador."

    elif api_key:
        # ── OpenAI-compatible cloud (Groq, OpenAI, Gemini, HuggingFace, …) ──
        _base = PROVIDERS.get(provider, {}).get("base_url") if provider else None
        if not _base:
            _base = base_url
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=_base)
            response = client.chat.completions.create(
                model=model_name, messages=messages,
                temperature=temperature, max_tokens=4096,
            )
            content = response.choices[0].message.content
            return strip_thinking_tags(content)
        except Exception as e:
            global _AI_KEY_ERROR
            err_str = str(e)
            # T9c: mapeo estandarizado de errores HTTP a mensajes en español
            if "401" in err_str or "invalid_api_key" in err_str.lower() or "authentication" in err_str.lower():
                _AI_KEY_ERROR = (
                    f"❌ API Key inválida o expirada para {provider or 'proveedor cloud'}. "
                    "Verifica tu clave en el panel lateral (⚙️ Configuración IA)."
                )
                return f"ERROR_401: {_AI_KEY_ERROR}"
            if "429" in err_str or "rate_limit" in err_str.lower() or "too many requests" in err_str.lower():
                return "ERROR_429: ⏳ Límite de solicitudes alcanzado. Espera un momento antes de continuar."
            if "timeout" in err_str.lower() or "timed out" in err_str.lower():
                raise TimeoutError("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.") from e
            if "connection" in err_str.lower():
                raise ConnectionError("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.") from e
            return f"❌ Error inesperado: {type(e).__name__}. Contacta al administrador."
    else:
        # ── LM Studio / Ollama local ─────────────────────────────────────────
        payload = {
            "model": model_name, "messages": messages,
            "temperature": temperature, "max_tokens": 4096, "stream": False,
        }
        try:
            response = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                json=payload, headers={"Content-Type": "application/json"}, timeout=180,
            )
            # Si el servidor rechaza max_tokens, reintentar sin ese campo
            if response.status_code == 400:
                payload.pop("max_tokens", None)
                response = requests.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    json=payload, headers={"Content-Type": "application/json"}, timeout=180,
                )
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return strip_thinking_tags(content)
            # T9c: mensajes estandarizados para errores del servidor local
            if response.status_code == 429:
                return "ERROR_429: ⏳ Límite de solicitudes alcanzado. Espera un momento antes de continuar."
            return f"❌ Error HTTP {response.status_code} del servidor local."
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.") from e
        except requests.exceptions.Timeout as e:
            raise TimeoutError("⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos.") from e
        except Exception as e:
            return f"❌ Error inesperado: {type(e).__name__}. Contacta al administrador."


def stream_ai_response(prompt, model_name, base_url="http://localhost:1234/v1", api_key=None, provider=None, max_tokens=4096):
    """Genera respuesta de IA en streaming. Soporta todos los proveedores."""
    system_instr = (
        "Responde EXCLUSIVAMENTE con el contenido solicitado. "
        "Formato: Texto conversacional directo. "
        "REGLA CRÍTICA: Usa SIEMPRE notación LaTeX para matemáticas ($...$ para línea, $$...$$ para bloque)."
    )
    full_prompt = f"SISTEMA: {system_instr}\n\nUSUARIO: {prompt}"
    messages = [{"role": "user", "content": full_prompt}]

    if provider is None and api_key:
        provider = detect_provider_from_key(api_key)

    if provider == "anthropic":
        # ── Anthropic SDK streaming ──────────────────────────────────────────
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            with client.messages.stream(
                model=model_name,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": full_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise ConnectionError(f"Error Anthropic streaming: {e}") from e

    elif api_key:
        # ── OpenAI-compatible cloud streaming ────────────────────────────────
        _base = PROVIDERS.get(provider, {}).get("base_url") if provider else None
        if not _base:
            _base = base_url
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=_base)
            stream = client.chat.completions.create(
                model=model_name, messages=messages,
                temperature=0.3, max_tokens=max_tokens, stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            raise ConnectionError(f"Error {provider or 'cloud'} streaming: {e}") from e
    else:
        # ── LM Studio / Ollama local streaming (SSE) ─────────────────────────
        payload = {
            "model": model_name, "messages": messages,
            "temperature": 0.3, "max_tokens": max_tokens, "stream": True,
        }
        try:
            response = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                json=payload, headers={"Content-Type": "application/json"},
                timeout=180, stream=True,
            )
            # Si el servidor rechaza max_tokens, reintentar sin ese campo
            if response.status_code == 400:
                payload.pop("max_tokens", None)
                response = requests.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    json=payload, headers={"Content-Type": "application/json"},
                    timeout=180, stream=True,
                )
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8") if isinstance(line, bytes) else line
                if not decoded.startswith("data: "):
                    continue
                data = decoded[6:]
                if data == "[DONE]":
                    return
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, KeyError):
                    continue
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Servidor local no disponible: {e}") from e
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Tiempo de espera agotado: {e}") from e
        except requests.exceptions.HTTPError as e:
            raise ConnectionError(f"Error del servidor local ({e.response.status_code}): {e}") from e


def get_socratic_guidance(student_rating, topic, content, student_answer, correct_answer, all_options, base_url="http://localhost:1234/v1", model_name="google/gemma-3-4b", api_key=None, provider=None):
    """Genera una guía socrática adaptativa y altamente alineada para el estudiante."""
    options_str = "\n".join([f"- {opt}" for opt in all_options])
    prompt = f"""Eres KatIA, una tutora socrática mitad gata, mitad cyborg. Tu personalidad:
- Usas metáforas felinas y tecnológicas ("mis sensores detectan", "desenredemos este ovillo")
- Haces referencias a filósofos griegos (Sócrates, Platón, Diógenes, Aristóteles)
- Eres amigable, motivadora, pero NUNCA revelas la respuesta directa
- Guías con preguntas socráticas que lleven al estudiante a descubrir por sí mismo
- Tus respuestas son concisas (máx. 3-4 oraciones)
- Puedes usar onomatopeyas felinas ocasionalmente (miau, purrr, bip)
- JAMÁS uses emojis. Tu personalidad se expresa solo con palabras.

CONTEXTO DE LA PREGUNTA:
- Tema: {topic}
- Enunciado: {content}
- Opciones disponibles:
{options_str}

ESTADO DEL ESTUDIANTE:
- Nivel ELO (Capacidad): {student_rating:.0f}
- Opción que el estudiante TIENE SELECCIONADA actualmente: "{student_answer}"
- Respuesta CORRECTA real: "{correct_answer}"

INSTRUCCIONES CRÍTICAS DE ALINEACIÓN:
1. Tu respuesta DEBE reconocer explícitamente la opción "{student_answer}" que el alumno ha marcado.
2. Si "{student_answer}" es la correcta, felicita sutilmente su intuición y haz una pregunta para profundizar en el "por qué" o qué pasaría si cambiamos un parámetro.
3. Si "{student_answer}" es INCORRECTA, analiza por qué esa opción específica es un distractor común o qué error de lógica implica, y haz una pregunta que lo haga notar sin dar la respuesta correcta.
4. Prohibido mencionar opciones que el alumno NO ha seleccionado a menos que sea para contrastar.
5. NUNCA reveles que la respuesta correcta es "{correct_answer}".
6. Sé breve, motivadora y puramente socrática (guía mediante preguntas).
7. REGLA ESTRICTA DE FORMATO: Escribe TODA expresión matemática exclusivamente en LaTeX usando $...$ o $$...$$.
"""
    return _call_ai_api(prompt, model_name, base_url, api_key=api_key, provider=provider)


def get_socratic_guidance_stream(student_rating, topic, content, student_answer, correct_answer, all_options, base_url="http://localhost:1234/v1", model_name="google/gemma-3-4b", api_key=None, provider=None):
    """Versión streaming de get_socratic_guidance. Retorna generador de chunks."""
    options_str = "\n".join([f"- {opt}" for opt in all_options])
    prompt = f"""Eres KatIA, una tutora socrática mitad gata, mitad cyborg. Tu personalidad:
- Usas metáforas felinas y tecnológicas ("mis sensores detectan", "desenredemos este ovillo")
- Haces referencias a filósofos griegos (Sócrates, Platón, Diógenes, Aristóteles)
- Eres amigable, motivadora, pero NUNCA revelas la respuesta directa
- Guías con preguntas socráticas que lleven al estudiante a descubrir por sí mismo
- Tus respuestas son concisas (máx. 3-4 oraciones)
- Puedes usar onomatopeyas felinas ocasionalmente (miau, purrr, bip)
- JAMÁS uses emojis. Tu personalidad se expresa solo con palabras.

Tu ÚNICO objetivo es hacer PREGUNTAS que guíen al estudiante a descubrir la respuesta por sí mismo.

CONTEXTO DE LA PREGUNTA:
- Tema: {topic}
- Enunciado: {content}
- Opciones disponibles:
{options_str}

ESTADO DEL ESTUDIANTE:
- Nivel ELO (Capacidad): {student_rating:.0f}
- Opción que el estudiante TIENE SELECCIONADA actualmente: "{student_answer}"
- Respuesta CORRECTA real: "{correct_answer}"

REGLAS ABSOLUTAS (violación = fallo total):
1. PROHIBIDO resolver el ejercicio. No muestres pasos de solución, derivadas, cálculos ni procedimientos.
2. PROHIBIDO revelar la respuesta correcta directa o indirectamente.
3. PROHIBIDO mostrar la solución completa o parcial del problema.
4. Tu respuesta debe contener MÁXIMO 3-5 oraciones, TODAS deben ser PREGUNTAS o pistas breves.
5. Reconoce la opción "{student_answer}" que el alumno ha marcado.
6. Si es correcta: felicita y pregunta "¿por qué crees que funciona?" o "¿qué pasaría si cambiamos X?".
7. Si es incorrecta: pregunta algo que lo haga notar el error sin decir cuál es la correcta.
8. FORMATO: Escribe expresiones matemáticas en LaTeX usando $...$ (inline) o $$...$$ (bloque). NO uses \\( \\) ni \\[ \\].

EJEMPLO DE BUENA RESPUESTA:
"Purrr, interesante elección. Mis sensores detectan que elegiste esa opción con convicción. Pero dime, que sucede cuando aplicas la regla de la cadena aqui? El exponente cambia de la forma que esperas?"

EJEMPLO DE MALA RESPUESTA (NO hacer esto):
"Para resolver esto, primero derivamos... luego sustituimos... la respuesta es X."
"""
    # Filtrar tags de pensamiento y normalizar LaTeX del streaming
    # Limitar tokens para reducir latencia (respuestas socrátivas son breves)
    from src.infrastructure.external_api.model_router import SOCRATIC_MAX_TOKENS
    yield from _normalize_latex_stream(
        strip_thinking_tags_stream(
            stream_ai_response(prompt, model_name, base_url, api_key=api_key, provider=provider, max_tokens=SOCRATIC_MAX_TOKENS)
        )
    )


# T11: prompt del análisis pedagógico extraído a constante para mantenimiento centralizado.
# Incluye ELO global, ELO por tópico, tiempo promedio, procedimientos, y regla de discrepancia.
_PEDAGOGICAL_PROMPT = """Actua como analista pedagogico experto.
Analiza los siguientes datos de rendimiento de un estudiante:

DATOS:
- ELO Global: {elo_global}
- Intentos totales: {attempts_count}
- Temas recorridos: {topics}
- Tasa de acierto reciente: {recent_accuracy}{elo_topic_section}{time_section}
- Habito de procedimientos escritos: {proc_line}{course_proc_section}

OBJETIVOS DEL ANALISIS:
1. Identificar debilidades conceptuales especificas basadas en los temas con menor rendimiento.
   Usar el ELO por topico para detectar areas debiles vs fuertes.
2. Recomendar tipos de ejercicios o areas de refuerzo concretas.
3. Sugerir ajustes en la estrategia de ensenanza o dificultad.
4. Proponer una estrategia pedagogica personalizada y accionable.
5. SECCION OBLIGATORIA — Calidad del procedimiento y desarrollo manual: {proc_instruction}
6. Si hay datos por curso, detecta si existe discrepancia entre ELO alto y procedimiento bajo
   (posible patron de adivinanza) o ELO bajo con procedimiento alto (comprende el proceso
   pero falla en la seleccion final). Reporta cualquier patron anomalo encontrado.
7. ALERTA PEDAGOGICA: Si el ELO global es alto pero la calidad reciente de procedimientos es
   baja, señalarlo explicitamente como una alerta critica — el estudiante podria estar
   adivinando respuestas sin comprender el proceso.

IMPORTANTE: No expliques teoria basica. Se directo y profesional. Usa bullet points.
Incluye siempre la seccion "Calidad del procedimiento" como ultimo punto del analisis.
REGLA ESTRICTA DE FORMATO: Escribe TODA expresion matematica en LaTeX usando $...$ o $$...$$.
"""


def get_pedagogical_analysis(student_data, base_url="http://localhost:1234/v1", model_name="llama-3.1-8b-instant", api_key=None, provider=None, procedure_stats=None, procedure_stats_by_course=None):
    """Genera un análisis pedagógico detallado para el profesor.
    procedure_stats (opcional): dict con 'count', 'avg_score', 'scores'.
    procedure_stats_by_course (opcional): dict {course_id: {course_name, avg_score, count}}.
    """
    # Construir línea e instrucción de procedimientos con etiquetas cualitativas
    if procedure_stats and procedure_stats.get('count', 0) > 0:
        _pc = procedure_stats['count']
        _pavg = procedure_stats['avg_score']
        _pscores = procedure_stats.get('scores', [])
        _quality = _proc_quality_label(_pavg)
        _proc_line = (
            f"{_pc} procedimiento(s) evaluado(s). Calidad global: {_quality}. "
            f"Notas individuales: {', '.join(f'{s:.1f}' for s in _pscores[:5])}"
        )
        if _pavg < 3.0:
            _proc_instruction = (
                "Calidad DEFICIENTE. El estudiante carece de rigor tecnico en el desarrollo escrito. "
                "Exigir que rehaga los ejercicios mostrando todos los pasos intermedios."
            )
        elif _pavg <= 4.0:
            _proc_instruction = (
                "Calidad REGULAR. El procedimiento esta incompleto o poco claro. "
                "Indicar al estudiante que justifique cada paso y use notacion correcta."
            )
        else:
            _proc_instruction = (
                "Calidad EXCELENTE. El estudiante domina el desarrollo matematico escrito. "
                "Felicitar este habito y proponer ejercicios de mayor complejidad procedimental."
            )
    else:
        _proc_line = "No ha subido ningun procedimiento escrito."
        _proc_instruction = (
            "ADVERTENCIA CRITICA: el estudiante NO documenta su desarrollo matematico paso a paso. "
            "Esto es un habito esencial que el docente debe exigir corregir de inmediato, "
            "ya que impide detectar errores de proceso aunque la respuesta final sea correcta."
        )

    # Bloque de análisis comparativo por curso (detecta adivinanza si ELO alto + procedimiento bajo)
    _course_proc_section = ""
    if procedure_stats_by_course:
        lines = []
        for cid, cdata in procedure_stats_by_course.items():
            lines.append(
                f"  - {cdata['course_name']}: {_proc_quality_label(cdata['avg_score'])} "
                f"({cdata['count']} envío(s))"
            )
        _course_proc_section = (
            "\n- Calidad de procedimientos por curso:\n" + "\n".join(lines) +
            "\n  ANALISIS COMPARATIVO: Si el ELO es alto en un curso pero el procedimiento es "
            "Deficiente o Regular, podria indicar que el alumno adivina respuestas en lugar de "
            "razonar. Señalarlo explicitamente si es el caso."
        )

    # T11: ELO desglosado por tópico (si viene en student_data)
    _elo_by_topic = student_data.get('elo_by_topic', {})
    _elo_topic_section = ""
    if _elo_by_topic:
        _elo_lines = [f"    - {t}: {e}" for t, e in sorted(_elo_by_topic.items(), key=lambda x: -x[1])]
        _elo_topic_section = "\n  ELO por tópico:\n" + "\n".join(_elo_lines)

    # T11: tiempo promedio de respuesta (si viene en student_data)
    _avg_time = student_data.get('avg_response_time')
    _time_section = f"\n- Tiempo promedio de respuesta: {_avg_time:.1f} segundos" if _avg_time else ""

    prompt = _PEDAGOGICAL_PROMPT.format(
        elo_global=f"{student_data['elo_global']:.1f}",
        attempts_count=student_data['attempts_count'],
        topics=', '.join(student_data['topics']),
        recent_accuracy=f"{student_data['recent_accuracy']:.1%}",
        proc_line=_proc_line,
        course_proc_section=_course_proc_section,
        elo_topic_section=_elo_topic_section,
        time_section=_time_section,
        proc_instruction=_proc_instruction,
    )
    return _call_ai_api(prompt, model_name, base_url, api_key=api_key, provider=provider)


_FALLBACK_RECOMMENDATIONS = [
    {
        "diagnostico": "Sin datos suficientes para evaluar fortalezas.",
        "accion": "Continúa practicando con constancia para que el sistema identifique tus puntos fuertes.",
        "justificacion": "Con más intentos el análisis será más preciso y personalizado.",
        "ejercicios": 10,
    },
    {
        "diagnostico": "Sin datos suficientes para evaluar áreas regulares.",
        "accion": "Revisa los temas con mayor variación en tus resultados y practica con preguntas de dificultad media.",
        "justificacion": "Consolidar el nivel intermedio es la base para avanzar hacia temas más complejos.",
        "ejercicios": 15,
    },
    {
        "diagnostico": "Sin datos suficientes para evaluar áreas críticas.",
        "accion": "Dedica tiempo extra a los conceptos fundamentales de los temas donde hayas fallado más.",
        "justificacion": "Reforzar la base conceptual evita errores recurrentes en preguntas más avanzadas.",
        "ejercicios": 20,
    },
]


def analyze_performance_local(history_data, current_elo, base_url="http://localhost:1234/v1", model_name="llama-3.1-8b-instant", api_key=None, provider=None, procedure_stats=None, procedure_stats_by_course=None):
    """
    Analiza el rendimiento del estudiante y devuelve EXACTAMENTE 3 recomendaciones
    con estructura fija: [fortalezas, áreas regulares, áreas críticas].
    Umbral mínimo: 3 intentos. Con menos datos devuelve recomendaciones genéricas.
    procedure_stats (opcional): dict con 'count', 'avg_score', 'scores'.
    procedure_stats_by_course (opcional): dict {course_id: {course_name, avg_score, count}}.
    """
    if not history_data:
        return _FALLBACK_RECOMMENDATIONS

    total = len(history_data)
    correct_count = sum(1 for h in history_data if h['is_correct'])
    accuracy = correct_count / total if total > 0 else 0
    correct_topics = sorted({h['topic'] for h in history_data if h['is_correct']})
    incorrect_topics = sorted({h['topic'] for h in history_data if not h['is_correct']})
    avg_difficulty = sum(h['difficulty'] for h in history_data) / total

    # Construir línea de hábito de procedimientos con etiquetas cualitativas
    if procedure_stats and procedure_stats.get('count', 0) > 0:
        _pc = procedure_stats['count']
        _pavg = procedure_stats['avg_score']
        _pscores = procedure_stats.get('scores', [])
        _quality = _proc_quality_label(_pavg)
        _pline = (
            f"{_pc} procedimiento(s) evaluado(s). Calidad: {_quality}. "
            f"Notas: {', '.join(f'{s:.1f}' for s in _pscores[:5])}"
        )
    else:
        _pline = "No ha subido ningun procedimiento escrito. No documenta su desarrollo matematico paso a paso."

    # Bloque por curso (para detectar discrepancias ELO vs procedimiento)
    _course_breakdown = ""
    if procedure_stats_by_course:
        lines = [
            f"  - {d['course_name']}: {_proc_quality_label(d['avg_score'])} ({d['count']} envío(s))"
            for d in procedure_stats_by_course.values()
        ]
        _course_breakdown = "\n- Por curso:\n" + "\n".join(lines)

    prompt = f"""Eres un tutor académico experto. Analiza el rendimiento de un estudiante y genera exactamente 3 recomendaciones estructuradas.

DATOS DEL ESTUDIANTE:
- ELO global: {current_elo:.0f} (escala 600-1800, promedio=1000)
- Intentos analizados: {total}
- Tasa de acierto: {accuracy:.0%}
- Temas donde acierta: {', '.join(correct_topics) if correct_topics else 'Ninguno registrado aun'}
- Temas donde falla: {', '.join(incorrect_topics) if incorrect_topics else 'Ninguno'}
- Dificultad media de las preguntas: {avg_difficulty:.0f}
- Habito de procedimientos escritos: {_pline}{_course_breakdown}

INSTRUCCION CRITICA: Responde UNICAMENTE con el siguiente JSON, sin ningun texto antes ni despues, sin bloques de codigo markdown:
[
  {{
    "diagnostico": "Describe especificamente lo que el estudiante HACE BIEN segun los datos. Tono muy positivo y motivador.",
    "accion": "Como puede potenciar y mantener estas fortalezas. Una sola accion clara.",
    "justificacion": "Por que es importante seguir cultivando estas fortalezas.",
    "ejercicios": 10
  }},
  {{
    "diagnostico": "Describe especificamente lo que el estudiante hace de forma REGULAR o ACEPTABLE pero puede mejorar.",
    "accion": "2 acciones concretas y ordenadas para pasar de nivel regular a bueno en esos temas.",
    "justificacion": "Por que mejorar este nivel intermedio marcara la diferencia en su ELO.",
    "ejercicios": 15
  }},
  {{
    "diagnostico": "Describe especificamente lo que el estudiante hace MAL o tiene como debilidad critica segun los datos.",
    "accion": "Pasos especificos y ordenados para superar esta debilidad. Se directo.",
    "justificacion": "Por que es urgente atender esto y que consecuencias tiene no hacerlo.",
    "ejercicios": 20
  }}
]"""

    content = _call_ai_api(prompt, model_name, base_url, json_mode=True, api_key=api_key, provider=provider)

    try:
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        # Buscar el array JSON usando [{ para no confundir con corchetes en texto
        match = re.search(r'\[[\s\n]*\{', content)
        start = match.start() if match else content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1 and end > start:
            parsed = json.loads(content[start:end + 1])
            if isinstance(parsed, list):
                # Descartar cualquier elemento que no sea dict (strings de intro, nulls, etc.)
                dict_items = [_normalize_rec(item) for item in parsed if isinstance(item, dict)]
                while len(dict_items) < 3:
                    dict_items.append(_FALLBACK_RECOMMENDATIONS[len(dict_items)])
                return dict_items[:3]
    except Exception:
        pass

    return _FALLBACK_RECOMMENDATIONS


def _normalize_rec(rec: dict) -> dict:
    """Normaliza claves alternativas que distintos modelos pueden devolver."""
    diagnostico = (rec.get('diagnostico') or rec.get('descripcion') or
                   rec.get('description') or rec.get('diagnosis') or 'N/A')
    accion = (rec.get('accion') or rec.get('acción') or rec.get('recomendacion') or
              rec.get('recomendación') or rec.get('recommendation') or
              rec.get('action') or rec.get('consejo') or 'N/A')
    justificacion = (rec.get('justificacion') or rec.get('justificación') or
                     rec.get('justification') or rec.get('razon') or
                     rec.get('razón') or rec.get('why') or 'N/A')
    ejercicios = rec.get('ejercicios') or rec.get('exercises') or rec.get('meta') or 0
    return {
        'diagnostico': diagnostico,
        'accion': accion,
        'justificacion': justificacion,
        'ejercicios': ejercicios,
    }


# ── Visión ────────────────────────────────────────────────────────────────────

# Palabras clave en el nombre del modelo que indican soporte de visión.
# Se buscan como subcadenas (case-insensitive) dentro del model ID completo.
# Incluye modelos cloud y locales populares con capacidad multimodal.
_VISION_KEYWORDS = [
    # OpenAI
    'gpt-4o', 'gpt-4-vision', 'gpt-4-turbo', 'gpt-4.1',
    # Google / Anthropic
    'gemini', 'claude',
    # Meta Llama 4+ (visión nativa)
    'llama-4', 'llama4',
    # Mistral con visión (Mistral 3+, Pixtral)
    'mistral-3', 'mistral3', 'pixtral',
    # Qwen con visión (múltiples convenciones de nombre)
    'qwen-vl', 'qwen2-vl', 'qwen2.5-vl', 'qwen-2-vl', 'qwen2.5-v',
    # Google Gemma 3+ (visión nativa desde Gemma 3)
    'gemma-3', 'gemma3',
    # GML (variante de Gemma con visión)
    'gml-',
    # Keyword genérico: cualquier modelo con "vision" o "vl" en el nombre
    'vision', 'llava', '-vl-', '-vl:',
    # Otros modelos locales populares con visión
    'minicpm-v', 'internvl', 'cogvlm', 'moondream',
    'deepseek-vl', 'phi-3-vision', 'phi-3.5-vision', 'phi-4-vision',
    'molmo', 'ovis', 'mantis', 'idefics',
]

_VISION_PROMPT = """Eres un profesor de matemáticas revisando el procedimiento manuscrito de un estudiante.

PREGUNTA DEL EJERCICIO:
{question}

INSTRUCCIONES DE REVISIÓN:
1. Indica si el desarrollo general es correcto o incorrecto.
2. Señala específicamente dónde hay errores (si existen), explicando si son conceptuales o de cálculo.
3. Indica qué pasos o conceptos importantes faltan o están incompletos.
4. Da una retroalimentación constructiva y motivadora.
5. Usa notación LaTeX para expresiones matemáticas ($...$ inline, $$...$$ para bloque).

Sé específico, directo y pedagógico."""


# Modelos que matchean keywords de visión pero son solo texto.
# Se excluyen explícitamente para evitar falsos positivos.
_VISION_EXCLUSIONS = [
    'qwen2.5-math',      # modelo matemático sin visión
    'qwen2.5-coder',     # modelo de código sin visión
    'gemma-3-1b',        # Gemma 3 1B no tiene visión (solo 4B+)
]


def _model_supports_vision(model_name: str, provider: str) -> bool:
    """Heurística para detectar si el modelo/proveedor activo soporta visión.

    Usa una lista de keywords conocidos de modelos con visión y
    una lista de exclusión para falsos positivos.
    """
    if provider in ('anthropic', 'gemini'):
        return True
    if model_name:
        model_lower = model_name.lower()
        # Verificar exclusiones primero (modelos de texto que matchean keywords)
        if any(ex in model_lower for ex in _VISION_EXCLUSIONS):
            return False
        return any(kw in model_lower for kw in _VISION_KEYWORDS)
    return False

# T6a: alias público para detección de capacidad de visión (fail-safe: False por defecto)
check_vision_support = _model_supports_vision

# T6c: lista de preferencia de modelos locales con buen razonamiento matemático.
# Se usa para priorizar automáticamente en Ollama cuando el área es matemáticas.
_MATH_REASONING_PREFERENCE = [
    "deepseek-r1",
    "qwen2.5-math",
    "qwen2.5",
    "llama3",
    "mistral",
]


def select_best_math_model(available_models: list, provider: str = None) -> str | None:
    """Selecciona el mejor modelo local para razonamiento matemático.

    Recorre la lista de preferencia y retorna el primer modelo disponible que
    coincida (por substring). Retorna None si ningún modelo preferido está disponible.
    Solo aplica para proveedores locales (Ollama, LM Studio).
    """
    if provider not in ('ollama', 'lmstudio', None):
        return None
    for preferred in _MATH_REASONING_PREFERENCE:
        for model in available_models:
            if preferred in model.lower():
                return model
    return None


def validate_procedure_relevance(
    image_bytes: bytes,
    mime_type: str,
    question_content: str,
    api_key: str = None,
    provider: str = None,
    base_url: str = "http://localhost:1234/v1",
    model_name: str = None,
) -> bool:
    """Valida si el procedimiento de la imagen corresponde a la pregunta activa.

    Llamada ligera al LLM con visión: solo pide SÍ o NO.
    Retorna True si corresponde, False si no.
    En caso de error o modelo sin visión, retorna True (beneficio de la duda).
    """
    if provider is None and api_key:
        provider = detect_provider_from_key(api_key)
    if not _model_supports_vision(model_name, provider):
        return True  # sin visión no se puede validar, asumimos que es válido

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    _val_prompt = (
        f"PREGUNTA ASIGNADA AL ESTUDIANTE:\n{question_content}\n\n"
        "¿El procedimiento visible en la imagen corresponde a la pregunta anterior? "
        "Responde ÚNICAMENTE 'SÍ' o 'NO'."
    )

    try:
        from openai import OpenAI
        _url = base_url or "http://localhost:1234/v1"
        _key = api_key or "not-needed"
        if provider in PROVIDERS:
            _url = PROVIDERS[provider].get('base_url', _url)
        client = OpenAI(api_key=_key, base_url=_url)
        resp = client.chat.completions.create(
            model=model_name or "default",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                    {"type": "text", "text": _val_prompt},
                ],
            }],
            max_tokens=10,
            temperature=0.0,
        )
        answer = (resp.choices[0].message.content or "").strip().upper()
        # Considerar variantes: SÍ, SI, YES → True; NO → False
        return "NO" not in answer
    except Exception:
        return True  # en caso de error, beneficio de la duda


def analyze_procedure_image(
    image_bytes: bytes,
    mime_type: str,
    question_content: str,
    model_name: str,
    base_url: str = "http://localhost:1234/v1",
    api_key: str = None,
    provider: str = None,
) -> str:
    """
    Analiza una imagen del procedimiento manuscrito del estudiante usando visión de IA.
    Devuelve la retroalimentación como texto Markdown, o la cadena
    'VISION_NOT_SUPPORTED' si el modelo no tiene capacidad de visión.
    """
    if provider is None and api_key:
        provider = detect_provider_from_key(api_key)

    if not _model_supports_vision(model_name, provider):
        return "VISION_NOT_SUPPORTED"

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    prompt = _VISION_PROMPT.format(question=question_content)

    if provider == 'anthropic':
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model=model_name,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
            return resp.content[0].text.strip()
        except Exception as e:
            return f"Error al analizar la imagen: {str(e)}"

    else:
        # OpenAI-compatible: OpenAI (gpt-4o), Gemini, LM Studio/Ollama con modelo de visión
        _base = PROVIDERS.get(provider, {}).get("base_url") if provider else None
        if not _base:
            _base = base_url
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key or "no-key", base_url=_base)
            response = client.chat.completions.create(
                model=model_name,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            err = str(e).lower()
            if any(kw in err for kw in ('vision', 'image', 'multimodal', 'unsupported', 'does not support')):
                return "VISION_NOT_SUPPORTED"
            return f"Error al analizar la imagen: {str(e)}"


# ── AIClient Strategy Pattern ─────────────────────────────────────────────────

class AIClient:
    """Cliente de IA con auto-detección y fallback entre proveedores.

    Orden de prioridad:
    1. LM Studio local (si detectado)
    2. Groq Cloud (si GROQ_API_KEY disponible)
    3. Otros proveedores cloud via variables de entorno
    4. Sin backend (degradación graciosa)
    """

    _ENV_PROVIDERS = [
        ('GROQ_API_KEY',      'groq'),
        ('OPENAI_API_KEY',    'openai'),
        ('ANTHROPIC_API_KEY', 'anthropic'),
        ('GOOGLE_API_KEY',    'gemini'),
        ('HF_TOKEN',          'huggingface'),
    ]

    def __init__(self, lmstudio_url: str = ""):
        self._provider = None
        self._api_key = None
        self._base_url = lmstudio_url
        self._models = []

        # 1. Intentar LM Studio local
        detection = detect_lmstudio(lmstudio_url)
        if detection['available']:
            self._provider = 'lmstudio'
            self._base_url = lmstudio_url
            self._models = detection['models']
            return

        # 2. Buscar API key en variables de entorno (load_dotenv ya fue llamado al importar)
        _secrets = {}
        try:
            import streamlit as _st
            _secrets = _st.secrets
        except Exception:
            pass

        for env_name, provider in self._ENV_PROVIDERS:
            key = os.environ.get(env_name)
            if not key:
                try:
                    key = _secrets.get(env_name)
                except Exception:
                    pass
            if key:
                self._provider = provider
                self._api_key = key
                pinfo = PROVIDERS.get(provider, {})
                self._base_url = pinfo.get('base_url') or lmstudio_url
                return

        # 3. Sin backend
        self._provider = None

    @property
    def active_backend_name(self) -> str:
        if self._provider == 'lmstudio':
            return "🖥️ LM Studio Local"
        if self._provider:
            return PROVIDERS.get(self._provider, {}).get('label', self._provider)
        return "Ninguno"

    @property
    def provider(self):
        return self._provider

    @property
    def api_key(self):
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def models(self) -> list:
        return self._models

    @property
    def is_available(self) -> bool:
        return self._provider is not None

    @property
    def key_error(self) -> str | None:
        """Retorna el mensaje del último error 401 detectado, o None si no hubo error."""
        return _AI_KEY_ERROR


def get_ai_client(lmstudio_url: str = "") -> AIClient:
    """Factory que crea y retorna un AIClient con auto-detección de backend."""
    return AIClient(lmstudio_url)
