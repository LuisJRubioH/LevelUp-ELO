from src.domain.elo.model import expected_score
from src.domain.elo.cognitive import CognitiveAnalyzer
from src.domain.selector.item_selector import AdaptiveItemSelector
from src.infrastructure.external_api.ai_client import get_socratic_guidance

class StudentService:
    """
    Servicio de aplicación que orquesta los casos de uso del estudiante.
    """
    def __init__(self, repository, ai_client=None):
        self.repository = repository
        self.ai_client = ai_client
        self.cognitive_analyzer = CognitiveAnalyzer()

    def get_next_question(self, student_id, topic, vector_rating,
                          session_correct_ids=None, session_wrong_timestamps=None,
                          session_questions_count=0):
        """Orquesta la selección de la siguiente pregunta."""
        session_correct_ids = session_correct_ids or set()
        session_wrong_timestamps = session_wrong_timestamps or {}

        pool = self.repository.get_items_from_db(topic)
        answered_ids = set(self.repository.get_answered_item_ids(student_id))
        current_elo = vector_rating.get(topic)

        # Excluir siempre las respondidas correctamente en esta sesión
        eligible = [i for i in pool if i['id'] not in session_correct_ids]

        # Prioridad 1: no vistas (no en DB histórica ni en sesión fallida)
        unseen = [
            i for i in eligible
            if i['id'] not in answered_ids and i['id'] not in session_wrong_timestamps
        ]

        # Prioridad 2: falladas en sesión con intervalo ≥ 3 preguntas
        wrong_available = [
            i for i in eligible
            if i['id'] in session_wrong_timestamps
            and session_questions_count - session_wrong_timestamps[i['id']] >= 3
        ]

        # Prioridad 3: históricas no de esta sesión (ni en cooldown)
        historical = [
            i for i in eligible
            if i['id'] in answered_ids and i['id'] not in session_wrong_timestamps
        ]

        filtered = unseen or wrong_available or historical

        # Si no hay candidatos, reiniciar o declarar maestría
        if not filtered:
            if current_elo < 1800:
                filtered = eligible or pool
            else:
                return None, "mastery"

        # Seleccionar óptima
        from src.domain.elo.model import Item
        selector = AdaptiveItemSelector()
        items_objs = [Item(difficulty=i['difficulty']) for i in filtered]
        target_item_obj = selector.select_optimal_item(current_elo, items_objs)

        if target_item_obj:
            item_data = next(i for i in filtered if i['difficulty'] == target_item_obj.difficulty)
            return item_data, "ok"
        return None, "empty"

    def process_answer(self, user_id, item_data, selected_option, reasoning, time_taken, vector_rating):
        """Orquesta el procesamiento de una respuesta."""
        is_correct = (selected_option == item_data['correct_option'])
        current_elo = vector_rating.get(item_data['topic'])
        
        # 1. Análisis Cognitivo
        cog_data = self.cognitive_analyzer.analyze_cognition(reasoning, is_correct, time_taken)
        
        # 2. Actualizar ELO del estudiante
        result = 1.0 if is_correct else 0.0
        new_r, new_rd = vector_rating.update(
            item_data['topic'], 
            item_data['difficulty'], 
            result, 
            impact_modifier=cog_data['impact_modifier']
        )
        
        # 3. Actualizar ELO del ítem (Simetría)
        self.repository.update_item_rating(item_data['id'], current_elo, result)
        
        # 4. Guardar intento
        p_success = expected_score(current_elo, item_data['difficulty'])
        self.repository.save_attempt(
            user_id, item_data['id'], is_correct, item_data['difficulty'],
            item_data['topic'], new_r, 
            prob_failure=1.0 - p_success,
            expected_score=p_success,
            time_taken=time_taken,
            confidence_score=cog_data['confidence_score'],
            error_type=cog_data['error_type'],
            rating_deviation=new_rd
        )
        
        return is_correct, cog_data

    def get_socratic_help(self, student_rating, topic, content, last_answer, correct_answer, all_options, model_name, ai_url):
        """Orquesta la obtención de guía socrática adaptativa y contextualizada."""
        return get_socratic_guidance(
            student_rating, topic, content, last_answer, 
            correct_answer=correct_answer,
            all_options=all_options,
            base_url=ai_url, model_name=model_name
        )
