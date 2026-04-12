from src.domain.elo.model import expected_score
from src.domain.selector.item_selector import AdaptiveItemSelector
from src.domain.entities import VALID_LEVELS, LEVEL_UNIVERSIDAD, LEVEL_SEMILLERO
from src.infrastructure.external_api.ai_client import get_socratic_guidance
from src.application.interfaces.repositories import IStudentRepository

class StudentService:
    """
    Servicio de aplicación que orquesta los casos de uso del estudiante.
    """
    def __init__(self, repository: IStudentRepository, ai_client=None, enable_cognitive_modifier: bool = False):
        self.repository = repository
        self.ai_client = ai_client
        self.enable_cognitive_modifier = enable_cognitive_modifier
        if enable_cognitive_modifier:
            from src.domain.elo.cognitive import CognitiveAnalyzer
            self.cognitive_analyzer = CognitiveAnalyzer()
        else:
            self.cognitive_analyzer = None

    def get_next_question(self, student_id, topic, vector_rating,
                          session_correct_ids=None, session_wrong_timestamps=None,
                          session_questions_count=0, course_id=None):
        """Orquesta la selección de la siguiente pregunta.

        Si se proporciona course_id, el pool de ítems se restringe EXCLUSIVAMENTE
        al curso activo. El motor ZDP (AdaptiveItemSelector) solo evalúa ese subconjunto.
        """
        session_correct_ids = session_correct_ids or set()
        session_wrong_timestamps = session_wrong_timestamps or {}

        # Filtrado por curso (Tarea F) — prioritario sobre filtro por topic
        if course_id:
            pool = self.repository.get_items_from_db(course_id=course_id)
        else:
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

    def process_answer(self, user_id, item_data, selected_option, reasoning, time_taken, vector_rating, elo_topic=None):
        """Orquesta el procesamiento de una respuesta.

        elo_topic: clave del VectorRating para buscar/actualizar ELO.
            Si no se pasa, usa item_data['topic'] (retrocompatible).
            Para cursos con subtemas heterogéneos (e.g., DIAN) se debe pasar
            el nombre del curso para que el ELO se consolide en una sola clave.
        """
        is_correct = (selected_option == item_data['correct_option'])
        _topic_key = elo_topic or item_data['topic']
        current_elo = vector_rating.get(_topic_key)

        # 1. Análisis cognitivo — controlado por feature flag
        if self.enable_cognitive_modifier and self.cognitive_analyzer is not None:
            cog_data = self.cognitive_analyzer.analyze_cognition(reasoning, is_correct, time_taken)
            impact_modifier = cog_data.get("impact_modifier", 1.0)
        else:
            # Feature flag desactivado — neutro explícito
            impact_modifier = 1.0
            cog_data = {
                "confidence_score": None,
                "error_type": "none",
                "impact_modifier": 1.0,
                "reasoning": "Análisis cognitivo desactivado",
            }

        # 2. Actualizar ELO del estudiante
        result = 1.0 if is_correct else 0.0
        new_r, new_rd = vector_rating.update(
            _topic_key,
            item_data['difficulty'],
            result,
            impact_modifier=impact_modifier,
        )

        # 3. Calcular nueva dificultad del ítem (ELO simétrico)
        p_success = expected_score(current_elo, item_data['difficulty'])
        item_score = 1.0 - result
        p_item_wins = 1.0 - p_success
        k_item = 32.0
        new_item_difficulty = item_data['difficulty'] + k_item * (item_score - p_item_wins)
        item_rd_current = item_data.get('rating_deviation', 350.0)

        # 4. Persistir ítem + intento de forma atómica
        attempt_data = {
            'is_correct': is_correct,
            'difficulty': item_data['difficulty'],
            'topic': _topic_key,
            'elo_after': new_r,
            'prob_failure': 1.0 - p_success,
            'expected_score': p_success,
            'time_taken': time_taken,
            'confidence_score': cog_data['confidence_score'],
            'error_type': cog_data['error_type'],
            'rating_deviation': new_rd,
        }
        self.repository.save_answer_transaction(
            user_id=user_id,
            item_id=item_data['id'],
            item_difficulty_new=new_item_difficulty,
            item_rd_new=item_rd_current,
            attempt_data=attempt_data,
        )

        return is_correct, cog_data

    def get_groups_for_course(self, course_id: str) -> list:
        """Devuelve los grupos disponibles para inscribirse en un curso específico."""
        return self.repository.get_available_groups_for_course(course_id)

    def enroll_in_course(self, user_id: int, course_id: str, group_id: int = None) -> None:
        """Matricula al estudiante en un curso asociándolo al grupo elegido."""
        self.repository.enroll_user(user_id, course_id, group_id)

    def get_available_courses(self, user_id: int) -> list:
        """Devuelve los cursos disponibles para el nivel educativo del estudiante.

        El nivel se lee desde la base de datos (fuente de verdad), nunca
        desde la sesión, garantizando el filtro estricto de catálogo.
        Un estudiante de Colegio NUNCA recibe cursos de Universidad y viceversa.
        """
        level = self.repository.get_education_level(user_id) or LEVEL_UNIVERSIDAD
        if level.lower() not in VALID_LEVELS:
            level = LEVEL_UNIVERSIDAD
        grade = None
        if level == LEVEL_SEMILLERO:
            grade = self.repository.get_grade(user_id)
        return self.repository.get_available_courses_by_level(level, grade=grade)

    def get_socratic_help(self, student_rating, topic, content, last_answer, correct_answer, all_options, model_name, ai_url):
        """Orquesta la obtención de guía socrática adaptativa y contextualizada."""
        return get_socratic_guidance(
            student_rating, topic, content, last_answer, 
            correct_answer=correct_answer,
            all_options=all_options,
            base_url=ai_url, model_name=model_name
        )
