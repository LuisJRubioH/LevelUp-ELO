import requests
import json
import re

def get_active_models(base_url="http://192.168.40.66:1234/v1"):
    """Consulta LM Studio para obtener la lista de IDs de modelos disponibles."""
    try:
        response = requests.get(f"{base_url.rstrip('/')}/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [m['id'] for m in data.get('data', [])]
    except:
        pass
    return []

def _call_ai_api(prompt, model_name, base_url, json_mode=False):
    """Función de utilidad para llamar a la API de LM Studio."""
    system_instr = "Responde EXCLUSIVAMENTE con el contenido solicitado. "
    if json_mode:
        system_instr += "Formato: JSON puro, sin explicaciones externas."
    else:
        system_instr += "Formato: Texto conversacional directo. REGLA CRÍTICA: Usa SIEMPRE notación LaTeX para matemáticas ($...$ para línea, $$...$$ para bloque)."

    full_prompt = f"SISTEMA: {system_instr}\n\nUSUARIO: {prompt}"
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": 0.3 if not json_mode else 0.1,
        "max_tokens": 4096,
        "stream": False
    }

    try:
        response = requests.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers={"Content-Type": "application/json"}, timeout=180)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # Limpiar razonamientos internos de DeepSeek u otros modelos
            content = re.sub(r'<thought>.*?</thought>', '', content, flags=re.DOTALL)
            return content.strip()
        return f"Error HTTP {response.status_code}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def get_socratic_guidance(student_rating, topic, content, student_answer, correct_answer, all_options, base_url="http://192.168.40.66:1234/v1", model_name="google/gemma-3-4b"):
    """Genera una guía socrática adaptativa y altamente alineada para el estudiante."""
    
    options_str = "\n".join([f"- {opt}" for opt in all_options])
    
    prompt = f"""
    Actúa como un Tutor Socrático altamente preciso y adaptativo.
    
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
    6. Sé breve, motivador y puramente socrático (guía mediante preguntas).
    7. REGLA ESTRICTA DE FORMATO: Escribe TODA expresión matemática (integrales, raíces, potencias, etc.) exclusivamente en LaTeX usando $...$ o $$...$$.
    """
    return _call_ai_api(prompt, model_name, base_url)

def get_pedagogical_analysis(student_data, base_url="http://192.168.40.66:1234/v1", model_name="mistralai/mistral-7b-instruct-v0.3"):
    """Genera un análisis pedagógico detallado para el profesor."""
    prompt = f"""
    Actúa como analista pedagógico experto. 
    Analiza los siguientes datos de rendimiento de un estudiante:

    DATOS:
    - ELO Global: {student_data['elo_global']:.1f}
    - Intentos totales: {student_data['attempts_count']}
    - Temas recorridos: {', '.join(student_data['topics'])}
    - Tasa de acierto reciente: {student_data['recent_accuracy']:.1%}
    
    OBJETIVOS DEL ANÁLISIS:
    1. Identificar debilidades conceptuales específicas basadas en los temas con menor rendimiento.
    2. Recomendar tipos de ejercicios o áreas de refuerzo concretas.
    3. Sugerir ajustes en la estrategia de enseñanza o dificultad.
    4. Proponer una estrategia pedagógica personalizada y accionable.

    IMPORTANTE: No expliques teoría básica. Sé directo y profesional. Usa bullet points.
    REGLA ESTRICTA DE FORMATO: Escribe TODA expresión matemática en LaTeX usando $...$ o $$...$$.
    """
    return _call_ai_api(prompt, model_name, base_url)

def analyze_performance_local(history_data, current_elo, base_url="http://192.168.40.66:1234/v1", model_name="mistralai/mistral-7b-instruct-v0.3"):
    """
    Analiza el rendimiento del estudiante (versión JSON para el dashboard de estadísticas).
    """
    if not history_data:
        return []

    incorrect_topics = [h['topic'] for h in history_data if not h['is_correct']]
    recent_difficulty = [h['difficulty'] for h in history_data]
    avg_difficulty = sum(recent_difficulty) / len(recent_difficulty) if recent_difficulty else 0
    
    prompt = f"""
    Actúa como tutor experto. Analiza:
    - ELO: {current_elo:.2f}, Dificultad media: {avg_difficulty:.0f}
    - Fallos en: {', '.join(set(incorrect_topics)) if incorrect_topics else 'Ninguno'}
    
    Genera 3 recomendaciones en JSON. REGLA DE FORMATO: Usa LaTeX ($...$) para cualquier símbolo matemático dentro del texto.
    [
      {{"diagnostico": "...", "recomendación": "...", "justificación": "...", "ejercicios": 10}}
    ]
    """
    
    content = _call_ai_api(prompt, model_name, base_url, json_mode=True)
    
    # Intento de extracción de JSON
    try:
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1:
            return json.loads(content[start:end+1])
        return json.loads(content)
    except:
        return [{"diagnostico": "Análisis no disponible", "recomendación": "Continuar practicando", "justificación": "La IA no pudo formatear el JSON correctamente.", "ejercicios": 0}]
