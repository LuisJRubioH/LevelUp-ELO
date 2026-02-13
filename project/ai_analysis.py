import requests
import json

def analyze_performance_local(history_data, current_elo, base_url="http://localhost:1234/v1"):
    """
    Analiza el rendimiento del estudiante utilizando un modelo local vía LM Studio.
    """
    
    if not history_data:
        return "No hay suficientes datos para realizar un análisis. ¡Responde más preguntas!"

    # Construir el contexto para la IA
    incorrect_topics = [h['topic'] for h in history_data if not h['is_correct']]
    recent_difficulty = [h['difficulty'] for h in history_data]
    avg_difficulty = sum(recent_difficulty) / len(recent_difficulty) if recent_difficulty else 0
    
    prompt = f"""
    Actúa como un tutor experto en matemáticas y educación personalizada. 
    Analiza el siguiente perfil de estudiante y dame 3 recomendaciones concretas y breves de estudio.
    
    Perfil del Estudiante:
    - ELO Actual: {current_elo:.2f}
    - Dificultad promedio enfrentada: {avg_difficulty:.0f}
    - Temas con errores recientes: {', '.join(set(incorrect_topics)) if incorrect_topics else 'Ninguno reciente'}
    - Últimos {len(history_data)} intentos: {sum(1 for h in history_data if h['is_correct'])} aciertos.
    
    Responde ÚNICAMENTE con un array JSON de strings, por ejemplo:
    ["Repasar integrales básicas", "Practicar regla de la cadena", "Hacer ejercicios de límites"]
    """

    payload = {
        "messages": [
            {"role": "system", "content": "Eres un tutor de matemáticas útil. Responde solo en JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": False
    }

    try:
        # Intentar conectar con el endpoint de Chat Completions de LM Studio (compatible con OpenAI)
        response = requests.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers={"Content-Type": "application/json"}, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            # Limpiar markdown si existe
            clean_content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_content)
        else:
            return [f"⚠️ Error IA ({response.status_code})", "Verifique conexión", "Intente más tarde"]
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # FALLBACK: Si no hay conexión, devolver recomendaciones simuladas para no romper la UI
        return [
            "⚠️ (Modo Offline) Repasa los conceptos básicos de derivadas.",
            "⚠️ (Modo Offline) Intenta resolver ejercicios de límites sin calculadora.",
            "⚠️ (Modo Offline) Conecta LM Studio para análisis real."
        ]
    except json.JSONDecodeError:
        return ["⚠️ Error de formato IA", "La respuesta no fue JSON válido", "Intente de nuevo"]
    except Exception as e:
        return [f"⚠️ Error inesperado", str(e)[:50], "Contacte soporte"]
