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

    def get_next_question(self, student_id, topic, vector_rating):
        """Orquesta la selección de la siguiente pregunta."""
        # 1. Obtener pool de preguntas
        pool = self.repository.get_items_from_db(topic)
        answered_ids = self.repository.get_answered_item_ids(student_id)
        
        filtered = [i for i in pool if i['id'] not in answered_ids]
        
        # 2. Si no hay preguntas, decidir si reiniciar o terminar
        current_elo = vector_rating.get(topic)
        if not filtered:
            if current_elo < 1800:
                filtered = pool # Reiniciar
            else:
                return None, "mastery"
        
        # 3. Seleccionar óptima
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
