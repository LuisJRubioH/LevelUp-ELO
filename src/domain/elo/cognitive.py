# ======================================================
# elo/cognitive.py
# ======================================================
import requests
import json
import time
import re

from src.utils import strip_thinking_tags

class CognitiveAnalyzer:
    def __init__(self, base_url="", model_name="google/gemma-3-4b"):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name

    def analyze_cognition(self, response_text: str, is_correct: bool, time_taken: float) -> dict:
        """
        Realiza un análisis completo del impacto cognitivo.
        Retorna un diccionario con modificadores y clasificaciones.
        """
        if not response_text or len(response_text.strip()) < 5:
            # Sin texto de razonamiento (flujo estándar de radio button):
            # usar impact_modifier=1.0 para que el ELO coincida exactamente
            # con el preview mostrado al estudiante antes de responder.
            # El time_modifier solo aplica cuando hay texto cognitivo que analizar.
            return {
                "confidence_score": 0.5,
                "error_type": "N/A",
                "impact_modifier": 1.0,
                "reasoning": "Sin razonamiento escrito — impacto estándar."
            }

        ai_data = self._call_ai_analyzer(response_text, is_correct)
        time_mod = self.compute_time_modifier(time_taken, is_correct)
        
        # Combinar modificadores
        # confidence_score (0.0 a 1.0) -> influye en el impacto
        # error_type (conceptual vs superficial) -> influye solo en fallos
        
        conf_mod = 0.8 + (ai_data['confidence'] * 0.4) # Rango [0.8, 1.2]
        
        error_mod = 1.0
        if not is_correct:
            if ai_data['error_type'] == "superficial":
                error_mod = 0.7  # Penalización reducida por descuido
            else:
                error_mod = 1.2  # Penalización mayor por falta de base

        final_mod = conf_mod * time_mod * error_mod
        # Limitar modificador entre 0.5 y 1.5 para evitar cambios extremos
        final_mod = max(0.5, min(1.5, final_mod))

        return {
            "confidence_score": ai_data['confidence'],
            "error_type": ai_data['error_type'],
            "impact_modifier": final_mod,
            "reasoning": ai_data['explanation']
        }

    def compute_time_modifier(self, time_taken: float, is_correct: bool) -> float:
        """
        Ajusta el impacto basado en la velocidad de respuesta.
        - Acierto muy rápido (< 5s): Maestría (+20%)
        - Acierto muy lento (> 30s): Duda (-20%)
        - Fallo muy rápido (< 3s): Descuido (-30% impacto -> menos penalización)
        """
        if is_correct:
            if time_taken < 5: return 1.2
            if time_taken > 30: return 0.8
        else:
            if time_taken < 3: return 0.7 # Penaliza menos si fue un click accidental/rápido
        return 1.0

    def _call_ai_analyzer(self, text: str, is_correct: bool) -> dict:
        """Llamada interna a IA local para clasificar la respuesta."""
        prompt = f"""
        Analiza el razonamiento de un estudiante para una pregunta {'correcta' if is_correct else 'incorrecta'}.
        Texto del alumno: "{text}"
        
        Determina:
        1. Confianza (0.0 a 1.0): ¿Qué tan seguro se ve el alumno de su proceso?
        2. Tipo de error (solo si es incorrecta): "conceptual" (no entiende el tema) o "superficial" (error de cálculo o descuido).
        
        Responde ÚNICAMENTE en JSON:
        {{"confidence": float, "error_type": "conceptual"|"superficial"|"none", "explanation": "breve texto"}}
        """
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 150
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Robust extraction for objects {...}
                # Eliminar tags de pensamiento (<think>, <thought>)
                content = strip_thinking_tags(content)
                
                # Extract the first valid JSON object
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
        except:
            pass

        # Fallback neutro
        return {
            "confidence": 0.5,
            "error_type": "conceptual" if not is_correct else "none",
            "explanation": "Análisis IA no disponible (Modo Offline)"
        }
