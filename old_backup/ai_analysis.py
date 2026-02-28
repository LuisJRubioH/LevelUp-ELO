import requests
import json
import re

def get_active_models(base_url="http://localhost:1234/v1"):
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
        system_instr += "Formato: Texto conversacional directo."

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

def get_socratic_guidance(student_rating, topic, content, student_answer, base_url="http://localhost:1234/v1", model_name="google/gemma-3-4b"):
    """Genera una guía socrática para el estudiante."""
    prompt = f"""
    Actúa como tutor socrático experto.
    
    CONTEXTO:
    - Nivel del estudiante (ELO): {student_rating:.0f}
    - Tema actual: {topic}
    - Pregunta planteada: {content}
    - Respuesta dada por el estudiante: {student_answer}

    REGLAS:
    1. NO proporciones la respuesta correcta bajo ninguna circunstancia.
    2. Haz preguntas abiertas que guíen al estudiante hacia el razonamiento correcto.
    3. Si detectas un error conceptual, formula una pregunta que lo haga evidente para el alumno.
    4. Divide el problema en pasos lógicos si es muy complejo.
    5. Usa un tono motivador pero desafiante.
    """
    return _call_ai_api(prompt, model_name, base_url)

def get_pedagogical_analysis(student_data, base_url="http://localhost:1234/v1", model_name="mistralai/mistral-7b-instruct-v0.3"):
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
    """
    return _call_ai_api(prompt, model_name, base_url)

def analyze_performance_local(history_data, current_elo, base_url="http://localhost:1234/v1", model_name="mistralai/mistral-7b-instruct-v0.3"):
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
    
    Genera 3 recomendaciones en JSON:
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
